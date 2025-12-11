import { API_URL } from '@/lib/constants'
import { refreshToken } from './auth'

let isRefreshing = false
let refreshPromise: Promise<string> | null = null

function getAccessToken(): string | null {
  return localStorage.getItem('access_token')
}

function setAccessToken(token: string): void {
  localStorage.setItem('access_token', token)
}

function clearAccessToken(): void {
  localStorage.removeItem('access_token')
}

async function refreshAccessToken(): Promise<string> {
  // 이미 갱신 중이면 기존 Promise 재사용 (중복 요청 방지)
  if (isRefreshing && refreshPromise) {
    return refreshPromise
  }

  isRefreshing = true
  refreshPromise = (async () => {
    try {
      const response = await refreshToken()
      setAccessToken(response.access_token)
      return response.access_token
    } catch (error) {
      clearAccessToken()
      // 로그인 페이지로 리다이렉트
      window.location.href = '/sign-in'
      throw error
    } finally {
      isRefreshing = false
      refreshPromise = null
    }
  })()

  return refreshPromise
}

interface FetchOptions extends RequestInit {
  skipAuth?: boolean
}

export async function fetchWithAuth(
  endpoint: string,
  options: FetchOptions = {}
): Promise<Response> {
  const { skipAuth = false, headers: customHeaders, ...restOptions } = options

  const makeRequest = async (token: string | null): Promise<Response> => {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...customHeaders,
    }

    if (!skipAuth && token) {
      ;(headers as Record<string, string>)['Authorization'] = `Bearer ${token}`
    }

    return fetch(`${API_URL}${endpoint}`, {
      ...restOptions,
      headers,
      credentials: 'include',
    })
  }

  let token = getAccessToken()
  let response = await makeRequest(token)

  // 401 에러 시 토큰 갱신 후 재시도
  if (response.status === 401 && !skipAuth) {
    try {
      token = await refreshAccessToken()
      response = await makeRequest(token)
    } catch {
      // refreshToken 실패 시 이미 로그인 페이지로 리다이렉트됨
      throw new Error('인증이 만료되었습니다. 다시 로그인해주세요.')
    }
  }

  return response
}

// 편의 메서드들
export const apiClient = {
  get: (endpoint: string, options?: FetchOptions) =>
    fetchWithAuth(endpoint, { ...options, method: 'GET' }),

  post: (endpoint: string, body?: unknown, options?: FetchOptions) =>
    fetchWithAuth(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),

  patch: (endpoint: string, body?: unknown, options?: FetchOptions) =>
    fetchWithAuth(endpoint, {
      ...options,
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    }),

  delete: (endpoint: string, options?: FetchOptions) =>
    fetchWithAuth(endpoint, { ...options, method: 'DELETE' }),
}
