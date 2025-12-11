import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogClose,
} from '@/components/ui/dialog'

interface DeleteRoomDialogProps {
  roomId: string | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirm: (roomId: string) => Promise<void>
  isPending: boolean
}

export function DeleteRoomDialog({
  roomId,
  open,
  onOpenChange,
  onConfirm,
  isPending,
}: DeleteRoomDialogProps) {
  const handleConfirm = async () => {
    if (!roomId) return
    await onConfirm(roomId)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="text-gray-900 dark:text-gray-100">
        <DialogHeader>
          <DialogTitle className="text-gray-900 dark:text-gray-100">
            채팅방 삭제
          </DialogTitle>
        </DialogHeader>
        <p className="text-gray-700 dark:text-gray-300">
          이 채팅방을 삭제하시겠습니까? 모든 대화 내용이 삭제됩니다.
        </p>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">취소</Button>
          </DialogClose>
          <Button
            variant="destructive"
            onClick={handleConfirm}
            disabled={isPending}
          >
            {isPending ? '삭제 중...' : '삭제'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
