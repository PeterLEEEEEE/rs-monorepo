import { useMutation, useQueryClient } from '@tanstack/react-query'
import { updateChatRoom } from '@/api/chat'

interface UpdateChatRoomParams {
  chatId: string
  title: string
}

export function useUpdateChatRoom() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ chatId, title }: UpdateChatRoomParams) => updateChatRoom(chatId, title),
    onSuccess: (_, { chatId }) => {
      queryClient.invalidateQueries({ queryKey: ['chatRooms'] })
      queryClient.invalidateQueries({ queryKey: ['chatRoom', chatId] })
    },
  })
}
