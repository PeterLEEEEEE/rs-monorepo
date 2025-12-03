import { create } from 'zustand'

interface ChatStore {
  // 현재 선택된 채팅방
  selectedRoomId: string | null
  setSelectedRoom: (id: string | null) => void

  // 사이드바 상태
  isSidebarOpen: boolean
  toggleSidebar: () => void

  // 입력 중인 메시지 (draft)
  draftMessage: string
  setDraftMessage: (message: string) => void
  clearDraft: () => void
}

export const useChatStore = create<ChatStore>((set) => ({
  // 채팅방 선택
  selectedRoomId: null,
  setSelectedRoom: (id) => set({ selectedRoomId: id }),

  // 사이드바
  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),

  // 메시지 입력
  draftMessage: '',
  setDraftMessage: (message) => set({ draftMessage: message }),
  clearDraft: () => set({ draftMessage: '' }),
}))
