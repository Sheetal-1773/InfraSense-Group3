import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { HealthScoreCard } from './HealthScoreCard'
import type { Component } from '../types'

const component: Component = {
  id: 'comp-1',
  name: 'Payment API',
  type: 'api',
  status: 'healthy',
  health_score: 85,
  healthScore: 85,
  cpu: 42,
  memory: 63,
  disk: 71,
  lastUpdated: '2024-01-01T12:00:00Z',
}

describe('HealthScoreCard', () => {
  it('renders the component name and type', () => {
    render(<HealthScoreCard component={component} />)
    expect(screen.getByText('Payment API')).toBeInTheDocument()
    expect(screen.getByText('api')).toBeInTheDocument()
  })

  it('renders the status badge', () => {
    render(<HealthScoreCard component={component} />)
    expect(screen.getByText('healthy')).toBeInTheDocument()
  })

  it('renders the health score', () => {
    render(<HealthScoreCard component={component} />)
    expect(screen.getByText('85')).toBeInTheDocument()
  })

  it('renders CPU, memory and disk values', () => {
    render(<HealthScoreCard component={component} />)
    expect(screen.getByText('42%')).toBeInTheDocument()
    expect(screen.getByText('63%')).toBeInTheDocument()
    expect(screen.getByText('71%')).toBeInTheDocument()
  })

  it('calls onClick when clicked', async () => {
    const user = userEvent.setup()
    const onClick = vi.fn()
    render(<HealthScoreCard component={component} onClick={onClick} />)
    await user.click(screen.getByText('Payment API'))
    expect(onClick).toHaveBeenCalledTimes(1)
  })
})