import { useRef, useEffect, useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useChatRoom } from './queries/use-chat-room'
import { useStreamMessage } from './use-stream-message'
import type { ChatMessage, ChatRoomDetailResponse } from '@/types/chat'

interface UseChatMessagesOptions {
  chatId: string | null
}

export function useChatMessages({ chatId }: UseChatMessagesOptions) {
  const queryClient = useQueryClient()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // 채팅방 데이터 조회
  const { data: chatRoomData, isLoading } = useChatRoom(chatId || undefined)

  // 캐시에 메시지 추가하는 함수
  const addMessageToCache = useCallback(
    (message: ChatMessage) => {
      if (!chatId) return

      queryClient.setQueryData<ChatRoomDetailResponse>(
        ['chatRoom', chatId, 1, 50],
        (old) => {
          if (!old) return old
          return {
            ...old,
            messages: [...old.messages, message],
          }
        }
      )
    },
    [chatId, queryClient]
  )

  // 스트리밍 hook
  const { send, isStreaming, streamingContent, error } = useStreamMessage({
    chatId: chatId || '',
    onUserMessage: addMessageToCache,
    onAssistantMessage: (msg) => {
      addMessageToCache(msg)
      // 채팅방 목록도 갱신 (last_message 업데이트)
      queryClient.invalidateQueries({ queryKey: ['chatRooms'] })
    },
  })

  // 메시지는 서버 데이터 직접 사용
  const messages = chatRoomData?.messages || []

  // 새 메시지 시 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingContent])

  // 메시지 전송
  const sendMessage = useCallback(
    (message: string) => {
      if (!chatId || !message.trim()) return
      send(message)
    },
    [chatId, send]
  )

  return {
    messages,
    isLoading,
    isStreaming,
    streamingContent,
    error,
    sendMessage,
    messagesEndRef,
    room: chatRoomData?.room,
  }
}
