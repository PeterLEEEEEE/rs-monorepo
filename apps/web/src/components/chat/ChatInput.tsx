import { useState, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

interface ChatInputProps {
  onSend: (message: string) => void
  isStreaming: boolean
  disabled?: boolean
}

export function ChatInput({ onSend, isStreaming, disabled }: ChatInputProps) {
  const [inputValue, setInputValue] = useState('')

  const handleSend = useCallback(() => {
    if (!inputValue.trim() || isStreaming || disabled) return
    onSend(inputValue)
    setInputValue('')
  }, [inputValue, isStreaming, disabled, onSend])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="border-t p-4">
      <div className="flex gap-2">
        <Input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="메시지를 입력하세요..."
          disabled={isStreaming || disabled}
          className="flex-1"
        />
        <Button
          onClick={handleSend}
          disabled={isStreaming || disabled || !inputValue.trim()}
        >
          {isStreaming ? '전송 중...' : '전송'}
        </Button>
      </div>
    </div>
  )
}
