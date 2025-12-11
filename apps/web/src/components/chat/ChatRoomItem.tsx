import { memo } from 'react'
import { MoreVertical, Pencil, Trash2 } from 'lucide-react'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import type { ChatRoom } from '@/types/chat'

interface ChatRoomItemProps {
  room: ChatRoom
  isSelected: boolean
  onSelect: (roomId: string) => void
  onEdit: (room: ChatRoom) => void
  onDelete: (roomId: string) => void
}

export const ChatRoomItem = memo(function ChatRoomItem({
  room,
  isSelected,
  onSelect,
  onEdit,
  onDelete,
}: ChatRoomItemProps) {
  return (
    <div
      className={`group relative border-b hover:bg-accent transition-colors ${
        isSelected ? 'bg-accent' : ''
      }`}
    >
      <button
        onClick={() => onSelect(room.id)}
        className="w-full p-3 pr-10 text-left text-foreground"
      >
        <div className="font-medium truncate">{room.title || '새 채팅'}</div>
        {room.last_message && (
          <div className="text-sm text-gray-500 truncate">
            {room.last_message.content}
          </div>
        )}
      </button>

      {/* 옵션 메뉴 */}
      <Popover>
        <PopoverTrigger asChild>
          <button className="absolute right-1 top-1/2 -translate-y-1/2 p-2 opacity-0 group-hover:opacity-100 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-opacity">
            <MoreVertical className="w-4 h-4" />
          </button>
        </PopoverTrigger>
        <PopoverContent className="w-36 p-1" align="end">
          <button
            onClick={() => onEdit(room)}
            className="flex items-center gap-2 w-full px-3 py-2 text-sm hover:bg-accent rounded"
          >
            <Pencil className="w-4 h-4" />
            이름 변경
          </button>
          <button
            onClick={() => onDelete(room.id)}
            className="flex items-center gap-2 w-full px-3 py-2 text-sm hover:bg-accent text-red-500 rounded"
          >
            <Trash2 className="w-4 h-4" />
            삭제
          </button>
        </PopoverContent>
      </Popover>
    </div>
  )
})
