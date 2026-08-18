import { useQuery } from '@tanstack/react-query'
import { getCorrelationGroups } from '../services/api'

export function useCorrelationGroups() {
  return useQuery({
    queryKey: ['correlations'],
    queryFn: getCorrelationGroups,
    refetchInterval: 120000,
  })
}