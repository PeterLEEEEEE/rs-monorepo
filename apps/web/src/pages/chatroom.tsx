import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  ChatSidebar,
  ChatMessageBubble,
  ChatInput,
  EditRoomDialog,
  DeleteRoomDialog,
} from '@/components/chat'
import { useChatRooms } from '@/hooks/queries/use-chat-rooms'
import { useCreateChatRoom } from '@/hooks/mutations/use-create-chat-room'
import { useDeleteChatRoom } from '@/hooks/mutations/use-delete-chat-room'
import { useUpdateChatRoom } from '@/hooks/mutations/use-update-chat-room'
import { useChatMessages } from '@/hooks/use-chat-messages'
import type { ChatRoom as ChatRoomType } from '@/types/chat'

export default function ChatRoom() {
  const [searchParams, setSearchParams] = useSearchParams()
  const chatId = searchParams.get('id')

  // 다이얼로그 상태
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [editingRoom, setEditingRoom] = useState<ChatRoomType | null>(null)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [deletingRoomId, setDeletingRoomId] = useState<string | null>(null)

  // Queries & Mutations
  const { data: chatRoomsData, isLoading: isLoadingRooms } = useChatRooms()
  const createChatRoom = useCreateChatRoom()
  const deleteChatRoom = useDeleteChatRoom()
  const updateChatRoom = useUpdateChatRoom()

  // 메시지 관련 (새 훅 사용)
  const {
    messages,
    isLoading: isLoadingMessages,
    isStreaming,
    streamingContent,
    sendMessage,
    messagesEndRef,
    room,
  } = useChatMessages({ chatId })

  // 핸들러 함수들
  const handleNewChat = async () => {
    const newRoom = await createChatRoom.mutateAsync(undefined)
    setSearchParams({ id: newRoom.id })
  }

  const handleSelectRoom = (roomId: string) => {
    setSearchParams({ id: roomId })
  }

  const handleEditRoom = (targetRoom: ChatRoomType) => {
    setEditingRoom(targetRoom)
    setEditDialogOpen(true)
  }

  const handleSaveRoom = async (roomId: string, title: string) => {
    await updateChatRoom.mutateAsync({ chatId: roomId, title })
  }

  const handleOpenDeleteDialog = (roomId: string) => {
    setDeletingRoomId(roomId)
    setDeleteDialogOpen(true)
  }

  const handleDeleteRoom = async (roomId: string) => {
    await deleteChatRoom.mutateAsync(roomId)
    if (chatId === roomId) {
      setSearchParams({})
    }
  }

  return (
    <div className="flex h-screen bg-background text-foreground">
      {/* 사이드바 */}
      <ChatSidebar
        rooms={chatRoomsData?.items || []}
        selectedRoomId={chatId}
        isLoading={isLoadingRooms}
        isCreating={createChatRoom.isPending}
        onNewChat={handleNewChat}
        onSelectRoom={handleSelectRoom}
        onEditRoom={handleEditRoom}
        onDeleteRoom={handleOpenDeleteDialog}
      />

      {/* 메인 채팅 영역 */}
      <main className="flex-1 flex flex-col">
        {chatId ? (
          <>
            {/* 헤더 */}
            <header className="h-14 border-b flex items-center px-4">
              <h1 className="font-semibold">{room?.title || '새 채팅'}</h1>
            </header>

            {/* 메시지 영역 */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {isLoadingMessages ? (
                <div className="text-center text-gray-500">메시지 로딩 중...</div>
              ) : (
                <>
                  {messages.map((msg) => (
                    <ChatMessageBubble key={msg.id} message={msg} />
                  ))}
                  {/* 스트리밍 중인 메시지 */}
                  {isStreaming && streamingContent && (
                    <div className="flex justify-start">
                      <div className="max-w-[70%] rounded-lg px-4 py-2 bg-muted">
                        <p className="whitespace-pre-wrap">{streamingContent}</p>
                      </div>
                    </div>
                  )}
                </>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* 입력 영역 */}
            <ChatInput onSend={sendMessage} isStreaming={isStreaming} />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            채팅방을 선택하거나 새 채팅을 시작하세요
          </div>
        )}
      </main>

      {/* 다이얼로그 */}
      <EditRoomDialog
        room={editingRoom}
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
        onSave={handleSaveRoom}
        isPending={updateChatRoom.isPending}
      />

      <DeleteRoomDialog
        roomId={deletingRoomId}
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        onConfirm={handleDeleteRoom}
        isPending={deleteChatRoom.isPending}
      />
    </div>
  )
}
