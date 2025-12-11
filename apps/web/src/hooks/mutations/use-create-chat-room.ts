import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createChatRoom } from '@/api/chat'

export function useCreateChatRoom() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (title?: string) => createChatRoom(title),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chatRooms'] })
    },
  })
}
