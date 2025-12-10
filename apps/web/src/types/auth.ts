export interface User {
  id: number;
  email: string;
  username: string;
  role: string;
}

export interface LoginRequest {
  email: string;
  password: string;
  device_id?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface RefreshResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}
