import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'

// Mock the API client
vi.mock('../api/client', () => ({
  getSkincareRoutine: vi.fn(),
}))

import SkincareRoutine from './SkincareRoutine'
import { getSkincareRoutine } from '../api/client'

const mockRoutine = {
  skin_type: 'Combination',
  notes: 'Focus on hydration and oil control',
  morning: ['Cleanse with gentle cleanser', 'Apply Vitamin C serum', 'Moisturize with SPF 30'],
  evening: ['Remove makeup', 'Cleanse', 'Apply Retinol 0.5%', 'Night moisturizer'],
}

describe('SkincareRoutine', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    getSkincareRoutine.mockReturnValue(new Promise(() => {}))

    render(
      <BrowserRouter>
        <SkincareRoutine />
      </BrowserRouter>
    )

    expect(screen.getByText('Loading skincare routine...')).toBeInTheDocument()
  })

  it('renders routine after data loaded', async () => {
    getSkincareRoutine.mockResolvedValue(mockRoutine)

    render(
      <BrowserRouter>
        <SkincareRoutine />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Skincare Routine')).toBeInTheDocument()
    })
  })

  it('displays skin type and notes', async () => {
    getSkincareRoutine.mockResolvedValue(mockRoutine)

    render(
      <BrowserRouter>
        <SkincareRoutine />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Skin Type: Combination')).toBeInTheDocument()
    })
    expect(screen.getByText('Focus on hydration and oil control')).toBeInTheDocument()
  })

  it('displays morning routine steps', async () => {
    getSkincareRoutine.mockResolvedValue(mockRoutine)

    render(
      <BrowserRouter>
        <SkincareRoutine />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Morning Routine')).toBeInTheDocument()
    })

    expect(screen.getByText('Cleanse with gentle cleanser')).toBeInTheDocument()
    expect(screen.getByText('Apply Vitamin C serum')).toBeInTheDocument()
    expect(screen.getByText('Moisturize with SPF 30')).toBeInTheDocument()
  })

  it('displays evening routine steps', async () => {
    getSkincareRoutine.mockResolvedValue(mockRoutine)

    render(
      <BrowserRouter>
        <SkincareRoutine />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Evening Routine')).toBeInTheDocument()
    })

    expect(screen.getByText('Remove makeup')).toBeInTheDocument()
    expect(screen.getByText('Apply Retinol 0.5%')).toBeInTheDocument()
    expect(screen.getByText('Night moisturizer')).toBeInTheDocument()
  })

  it('handles no routine available', async () => {
    getSkincareRoutine.mockResolvedValue(null)

    render(
      <BrowserRouter>
        <SkincareRoutine />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('No routine available')).toBeInTheDocument()
    })
  })

  it('handles error gracefully', async () => {
    getSkincareRoutine.mockRejectedValue(new Error('API error'))

    render(
      <BrowserRouter>
        <SkincareRoutine />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('No routine available')).toBeInTheDocument()
    })
  })
})
