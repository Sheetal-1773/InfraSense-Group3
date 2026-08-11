import { useQuery } from '@tanstack/react-query'
import { getComponents, getComponent } from '../services/api'

export function useComponents() {
  return useQuery({
    queryKey: ['components'],
    queryFn: getComponents,
  })
}

export function useComponent(id: string) {
  return useQuery({
    queryKey: ['component', id],
    queryFn: () => getComponent(id),
    enabled: !!id,
  })
}