import { useQuery } from '@tanstack/react-query'
import { fetchChatRooms } from '@/api/chat'

export function useChatRooms(page: number = 1, limit: number = 10) {
  return useQuery({
    queryKey: ['chatRooms', page, limit],
    queryFn: () => fetchChatRooms(page, limit),
  })
}
