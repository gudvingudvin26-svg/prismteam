import { create } from 'zustand'

interface AppState {
  user: null | { id: string; name: string; role: string }
  isLoading: boolean
  setUser: (user: null | { id: string; name: string; role: string }) => void
  setLoading: (loading: boolean) => void
}

export const useAppStore = create<AppState>((set) => ({
  user: null,
  isLoading: false,
  setUser: (user) => set({ user }),
  setLoading: (loading) => set({ isLoading: loading })
}))
