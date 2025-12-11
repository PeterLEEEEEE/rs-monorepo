export interface ChatRoom {
  id: string
  title: string | null
  user_id: string
  message_count?: number
  last_message?: LastMessage | null
  created_at: string
  updated_at: string
}

export interface LastMessage {
  content: string
  role: string
  created_at: string
}

export interface ChatMessage {
  id: number
  turn_id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface Pagination {
  page: number
  limit: number
  total: number
  has_next: boolean
  has_prev: boolean
}

export interface ChatRoomListResponse {
  items: ChatRoom[]
  pagination: Pagination
}

export interface ChatRoomDetailResponse {
  room: ChatRoom
  messages: ChatMessage[]
  pagination: Pagination
}

export interface SendMessageResponse {
  turn_id: number
  user_message: ChatMessage
  assistant_message: ChatMessage
}

// SSE 이벤트 타입
export interface SSEUserMessageEvent {
  id: number
  turn_id: number
  role: string
  content: string
  created_at: string
}

export interface SSETokenEvent {
  token: string
}

export interface SSEAssistantMessageEvent {
  id: number
  turn_id: number
  role: string
  content: string
  created_at: string
}

export interface SSEErrorEvent {
  message: string
}
