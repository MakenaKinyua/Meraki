import { QueryClient } from '@tanstack/vue-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      networkMode: 'online',
      staleTime: 30_000,
      refetchOnReconnect: true,
      retry: (failureCount, error) => {
        if (error?.status && error.status < 500) return false
        return failureCount < 2
      },
    },
    mutations: {
      networkMode: 'online',
      retry: 0,
    },
  },
})
