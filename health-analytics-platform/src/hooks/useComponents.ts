import { useQuery } from '@tanstack/react-query'
import { getComponents, getComponent } from '../services/api'

export function useComponents(source?: string) {
  return useQuery({
    queryKey: ['components', source],
    queryFn: async () => {
      console.log('[useComponents] Fetching with source:', source)
      const result = await getComponents(source)
      console.log('[useComponents] Result:', result)
      return result
    },
    refetchInterval: 120000,
  })
}

export function useComponent(id: string) {
  return useQuery({
    queryKey: ['component', id],
    queryFn: () => getComponent(id),
    enabled: !!id,
  })
}