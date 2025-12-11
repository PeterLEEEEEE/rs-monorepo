import { Button } from '@/components/ui/button'
import { ChatRoomItem } from './ChatRoomItem'
import type { ChatRoom } from '@/types/chat'

interface ChatSidebarProps {
  rooms: ChatRoom[]
  selectedRoomId: string | null
  isLoading: boolean
  isCreating: boolean
  onNewChat: () => void
  onSelectRoom: (roomId: string) => void
  onEditRoom: (room: ChatRoom) => void
  onDeleteRoom: (roomId: string) => void
}

export function ChatSidebar({
  rooms,
  selectedRoomId,
  isLoading,
  isCreating,
  onNewChat,
  onSelectRoom,
  onEditRoom,
  onDeleteRoom,
}: ChatSidebarProps) {
  return (
    <aside className="w-64 border-r flex flex-col">
      <div className="p-4 border-b">
        <Button onClick={onNewChat} className="w-full" disabled={isCreating}>
          + 새 채팅
        </Button>
      </div>
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-4 text-center text-gray-500">로딩 중...</div>
        ) : (
          rooms.map((room) => (
            <ChatRoomItem
              key={room.id}
              room={room}
              isSelected={selectedRoomId === room.id}
              onSelect={onSelectRoom}
              onEdit={onEditRoom}
              onDelete={onDeleteRoom}
            />
          ))
        )}
      </div>
    </aside>
  )
}
