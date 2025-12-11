import { memo } from 'react'
import type { ChatMessage } from '@/types/chat'

interface ChatMessageBubbleProps {
  message: ChatMessage
}

export const ChatMessageBubble = memo(function ChatMessageBubble({
  message,
}: ChatMessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[70%] rounded-lg px-4 py-2 ${
          isUser ? 'bg-primary text-primary-foreground' : 'bg-muted'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
      </div>
    </div>
  )
})
