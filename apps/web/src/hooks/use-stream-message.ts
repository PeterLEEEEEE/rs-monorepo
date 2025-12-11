import { useState, useCallback, useRef } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { streamMessage } from '@/api/chat'
import type { ChatMessage } from '@/types/chat'

interface UseStreamMessageOptions {
  chatId: string
  onUserMessage?: (message: ChatMessage) => void
  onAssistantMessage?: (message: ChatMessage) => void
}

export function useStreamMessage({ chatId, onUserMessage, onAssistantMessage }: UseStreamMessageOptions) {
  const queryClient = useQueryClient()
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingContent, setStreamingContent] = useState('')
  const [error, setError] = useState<string | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  const send = useCallback(
    (message: string) => {
      setIsStreaming(true)
      setStreamingContent('')
      setError(null)

      abortControllerRef.current = streamMessage(chatId, message, {
        onUserMessage: (data) => {
          const userMessage: ChatMessage = {
            id: data.id,
            turn_id: data.turn_id,
            role: 'user',
            content: data.content,
            created_at: data.created_at,
          }
          onUserMessage?.(userMessage)
        },
        onToken: (token) => {
          setStreamingContent((prev) => prev + token)
        },
        onAssistantMessage: (data) => {
          const assistantMessage: ChatMessage = {
            id: data.id,
            turn_id: data.turn_id,
            role: 'assistant',
            content: data.content,
            created_at: data.created_at,
          }
          onAssistantMessage?.(assistantMessage)
          setStreamingContent('')
          // 채팅방 캐시 무효화
          queryClient.invalidateQueries({ queryKey: ['chatRoom', chatId] })
          queryClient.invalidateQueries({ queryKey: ['chatRooms'] })
        },
        onError: (errorMessage) => {
          setError(errorMessage)
        },
        onComplete: () => {
          setIsStreaming(false)
        },
      })
    },
    [chatId, queryClient, onUserMessage, onAssistantMessage]
  )

  const cancel = useCallback(() => {
    abortControllerRef.current?.abort()
    setIsStreaming(false)
  }, [])

  return {
    send,
    cancel,
    isStreaming,
    streamingContent,
    error,
  }
}
