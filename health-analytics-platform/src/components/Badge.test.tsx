import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Badge } from './Badge'

describe('Badge', () => {
  it('renders children text', () => {
    render(<Badge>healthy</Badge>)
    expect(screen.getByText('healthy')).toBeInTheDocument()
  })

  it('applies the success variant styles', () => {
    render(<Badge variant="success">ok</Badge>)
    const badge = screen.getByText('ok')
    expect(badge.className).toContain('bg-green-100')
    expect(badge.className).toContain('text-green-800')
  })

  it('applies the danger variant styles', () => {
    render(<Badge variant="danger">down</Badge>)
    const badge = screen.getByText('down')
    expect(badge.className).toContain('bg-red-100')
  })

  it('defaults to the default variant', () => {
    render(<Badge>info</Badge>)
    const badge = screen.getByText('info')
    expect(badge.className).toContain('bg-gray-100')
  })

  it('merges custom className', () => {
    render(<Badge className="custom-class">x</Badge>)
    expect(screen.getByText('x').className).toContain('custom-class')
  })
})