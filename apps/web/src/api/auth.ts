import { API_URL } from "@/lib/constants";
import { getDeviceId } from "@/lib/fingerprint";
import type { LoginResponse, RefreshResponse, User } from "@/types/auth";

export async function login(
  email: string,
  password: string
): Promise<LoginResponse> {
  const deviceId = await getDeviceId();

  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({
      email,
      password,
      device_id: deviceId,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "로그인에 실패했습니다.");
  }

  return response.json();
}

export async function refreshToken(): Promise<RefreshResponse> {
  const response = await fetch(`${API_URL}/auth/refresh`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("토큰 갱신에 실패했습니다.");
  }

  return response.json();
}

export async function logout(accessToken: string): Promise<void> {
  await fetch(`${API_URL}/auth/logout`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    credentials: "include",
  });
}

export async function getMe(accessToken: string): Promise<User> {
  const response = await fetch(`${API_URL}/auth/me`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error("사용자 정보를 가져오는데 실패했습니다.");
  }

  return response.json();
}
