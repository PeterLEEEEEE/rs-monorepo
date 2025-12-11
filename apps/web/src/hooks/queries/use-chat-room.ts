import { useQuery } from '@tanstack/react-query'
import { fetchChatRoom } from '@/api/chat'

export function useChatRoom(chatId: string | undefined, page: number = 1, limit: number = 50) {
  return useQuery({
    queryKey: ['chatRoom', chatId, page, limit],
    queryFn: () => fetchChatRoom(chatId!, page, limit),
    enabled: !!chatId,
  })
}
