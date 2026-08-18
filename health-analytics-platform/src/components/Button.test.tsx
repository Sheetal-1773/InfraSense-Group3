import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from './Button'

describe('Button', () => {
  it('renders children text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument()
  })

  it('calls onClick when clicked', async () => {
    const user = userEvent.setup()
    const onClick = vi.fn()
    render(<Button onClick={onClick}>Go</Button>)
    await user.click(screen.getByRole('button', { name: 'Go' }))
    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('is disabled when disabled prop is set', () => {
    render(<Button disabled>No</Button>)
    expect(screen.getByRole('button', { name: 'No' })).toBeDisabled()
  })

  it('is disabled while loading', () => {
    render(<Button loading>Saving</Button>)
    expect(screen.getByRole('button', { name: 'Saving' })).toBeDisabled()
  })

  it('does not fire onClick when disabled', async () => {
    const user = userEvent.setup()
    const onClick = vi.fn()
    render(<Button disabled onClick={onClick}>No</Button>)
    await user.click(screen.getByRole('button', { name: 'No' }))
    expect(onClick).not.toHaveBeenCalled()
  })

  it('applies size styles', () => {
    render(<Button size="sm">small</Button>)
    expect(screen.getByRole('button', { name: 'small' }).className).toContain('px-3 py-1.5')
  })
})