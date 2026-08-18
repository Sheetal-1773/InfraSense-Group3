import { useQuery } from '@tanstack/react-query'
import { getHealthScore } from '../services/api'

export function useHealthScore() {
  return useQuery({
    queryKey: ['healthScore'],
    queryFn: getHealthScore,
    refetchInterval: 120000,
  })
}