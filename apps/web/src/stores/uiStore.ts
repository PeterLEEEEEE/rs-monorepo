import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UIStore {
  // 테마
  theme: 'light' | 'dark' | 'system'
  setTheme: (theme: 'light' | 'dark' | 'system') => void

  // 모달
  isModalOpen: boolean
  modalContent: string | null
  openModal: (content: string) => void
  closeModal: () => void
}

export const useUIStore = create<UIStore>()(
  persist(
    (set) => ({
      // 테마 (localStorage에 저장)
      theme: 'system',
      setTheme: (theme) => set({ theme }),

      // 모달
      isModalOpen: false,
      modalContent: null,
      openModal: (content) => set({ isModalOpen: true, modalContent: content }),
      closeModal: () => set({ isModalOpen: false, modalContent: null }),
    }),
    {
      name: 'ui-storage',
      partialize: (state) => ({ theme: state.theme }), // theme만 persist
    }
  )
)
