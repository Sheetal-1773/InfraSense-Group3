import { useQuery } from '@tanstack/react-query'
import { getPredictions } from '../services/api'

export function usePredictions() {
  return useQuery({
    queryKey: ['predictions'],
    queryFn: getPredictions,
  })
}