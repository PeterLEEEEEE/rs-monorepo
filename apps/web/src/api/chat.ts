import { apiClient } from './client'
import type {
  ChatRoom,
  ChatRoomListResponse,
  ChatRoomDetailResponse,
  SendMessageResponse,
} from '@/types/chat'
import { API_URL } from '@/lib/constants'

// 채팅방 목록 조회
export async function fetchChatRooms(
  page: number = 1,
  limit: number = 10
): Promise<ChatRoomListResponse> {
  const response = await apiClient.get(`/chat?page=${page}&limit=${limit}`)

  if (!response.ok) {
    throw new Error('채팅방 목록을 불러오는데 실패했습니다.')
  }

  return response.json()
}

// 채팅방 생성
export async function createChatRoom(title?: string): Promise<ChatRoom> {
  const response = await apiClient.post('/chat', { title })

  if (!response.ok) {
    throw new Error('채팅방 생성에 실패했습니다.')
  }

  return response.json()
}

// 채팅방 상세 조회 (메시지 포함)
export async function fetchChatRoom(
  chatId: string,
  page: number = 1,
  limit: number = 50
): Promise<ChatRoomDetailResponse> {
  const response = await apiClient.get(`/chat/${chatId}?page=${page}&limit=${limit}`)

  if (!response.ok) {
    throw new Error('채팅방을 불러오는데 실패했습니다.')
  }

  return response.json()
}

// 채팅방 삭제
export async function deleteChatRoom(chatId: string): Promise<void> {
  const response = await apiClient.delete(`/chat/${chatId}`)

  if (!response.ok) {
    throw new Error('채팅방 삭제에 실패했습니다.')
  }
}

// 채팅방 수정 (제목 변경)
export async function updateChatRoom(chatId: string, title: string): Promise<ChatRoom> {
  const response = await apiClient.patch(`/chat/${chatId}`, { title })

  if (!response.ok) {
    throw new Error('채팅방 수정에 실패했습니다.')
  }

  return response.json()
}

// 메시지 전송 (동기)
export async function sendMessage(
  chatId: string,
  message: string
): Promise<SendMessageResponse> {
  const response = await apiClient.post(`/chat/${chatId}/message`, { message })

  if (!response.ok) {
    throw new Error('메시지 전송에 실패했습니다.')
  }

  return response.json()
}

// 메시지 전송 (SSE 스트리밍)
export function streamMessage(
  chatId: string,
  message: string,
  callbacks: {
    onUserMessage?: (data: { id: number; turn_id: number; role: string; content: string; created_at: string }) => void
    onToken?: (token: string) => void
    onAssistantMessage?: (data: { id: number; turn_id: number; role: string; content: string; created_at: string }) => void
    onError?: (error: string) => void
    onComplete?: () => void
  }
): AbortController {
  const controller = new AbortController()
  const token = localStorage.getItem('access_token')

  const makeRequest = async (accessToken: string | null) => {
    const response = await fetch(`${API_URL}/chat/${chatId}/message/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(accessToken && { Authorization: `Bearer ${accessToken}` }),
      },
      credentials: 'include',
      body: JSON.stringify({ message }),
      signal: controller.signal,
    })

    // 401이면 토큰 갱신 후 재시도
    if (response.status === 401) {
      const { refreshToken } = await import('./auth')
      try {
        const refreshResponse = await refreshToken()
        localStorage.setItem('access_token', refreshResponse.access_token)
        // 재시도
        return fetch(`${API_URL}/chat/${chatId}/message/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${refreshResponse.access_token}`,
          },
          credentials: 'include',
          body: JSON.stringify({ message }),
          signal: controller.signal,
        })
      } catch {
        window.location.href = '/sign-in'
        throw new Error('인증이 만료되었습니다.')
      }
    }

    return response
  }

  makeRequest(token)
    .then(async (response) => {
      if (!response.ok) {
        throw new Error('스트리밍 연결에 실패했습니다.')
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('스트림을 읽을 수 없습니다.')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        let currentEvent = ''
        for (const line of lines) {
          if (line.startsWith('event: ')) {
            currentEvent = line.slice(7).trim()
          } else if (line.startsWith('data: ')) {
            const data = line.slice(6)
            try {
              const parsed = JSON.parse(data)
              switch (currentEvent) {
                case 'user_message':
                  callbacks.onUserMessage?.(parsed)
                  break
                case 'token':
                  callbacks.onToken?.(parsed.token)
                  break
                case 'assistant_message':
                  callbacks.onAssistantMessage?.(parsed)
                  break
                case 'error':
                  callbacks.onError?.(parsed.message)
                  break
              }
            } catch {
              // JSON 파싱 실패 무시
            }
          }
        }
      }

      callbacks.onComplete?.()
    })
    .catch((error) => {
      if (error.name !== 'AbortError') {
        callbacks.onError?.(error.message)
      }
    })

  return controller
}
