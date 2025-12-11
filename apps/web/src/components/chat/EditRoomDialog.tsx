import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogClose,
} from '@/components/ui/dialog'
import type { ChatRoom } from '@/types/chat'

interface EditRoomDialogProps {
  room: ChatRoom | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onSave: (roomId: string, title: string) => Promise<void>
  isPending: boolean
}

export function EditRoomDialog({
  room,
  open,
  onOpenChange,
  onSave,
  isPending,
}: EditRoomDialogProps) {
  const [title, setTitle] = useState('')

  useEffect(() => {
    if (room) {
      setTitle(room.title || '')
    }
  }, [room])

  const handleSave = async () => {
    if (!room || !title.trim()) return
    await onSave(room.id, title)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="text-gray-900 dark:text-gray-100">
        <DialogHeader>
          <DialogTitle className="text-gray-900 dark:text-gray-100">
            채팅방 이름 변경
          </DialogTitle>
        </DialogHeader>
        <Input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="새 이름을 입력하세요"
          className="text-gray-900 dark:text-gray-100"
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              handleSave()
            }
          }}
        />
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">취소</Button>
          </DialogClose>
          <Button onClick={handleSave} disabled={isPending || !title.trim()}>
            {isPending ? '저장 중...' : '저장'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
