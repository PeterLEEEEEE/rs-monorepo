import { useMutation, useQueryClient } from '@tanstack/react-query'
import { deleteChatRoom } from '@/api/chat'

export function useDeleteChatRoom() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (chatId: string) => deleteChatRoom(chatId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chatRooms'] })
    },
  })
}
