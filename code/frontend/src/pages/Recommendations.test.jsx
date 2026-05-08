import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'

// Mock the API client
vi.mock('../api/client', () => ({
  getRecommendations: vi.fn(),
}))

import Recommendations from './Recommendations'
import { getRecommendations } from '../api/client'

const mockRecs = [
  {
    name: 'Vitamin C Serum',
    description: 'Improves skin brightness',
    evidence_level: 'RCT',
    effect_size: 0.8,
    time_to_effect: 4,
    roi_score: 2.5,
    priority: 1,
  },
  {
    name: 'Retinol',
    description: 'Reduces wrinkles',
    evidence_level: 'meta',
    effect_size: 0.9,
    time_to_effect: 8,
    roi_score: 1.8,
    priority: 2,
  },
]

describe('Recommendations', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    getRecommendations.mockReturnValue(new Promise(() => {})) // never resolves

    render(
      <BrowserRouter>
        <Recommendations />
      </BrowserRouter>
    )

    expect(screen.getByText('Loading recommendations...')).toBeInTheDocument()
  })

  it('calls getRecommendations with limit 10', async () => {
    getRecommendations.mockResolvedValue(mockRecs)

    render(
      <BrowserRouter>
        <Recommendations />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(getRecommendations).toHaveBeenCalledWith(10)
    })
  })

  it('renders recommendations after data loaded', async () => {
    getRecommendations.mockResolvedValue(mockRecs)

    render(
      <BrowserRouter>
        <Recommendations />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Vitamin C Serum')).toBeInTheDocument()
    })
    expect(screen.getByText('Retinol')).toBeInTheDocument()
    expect(screen.getByText('Improves skin brightness')).toBeInTheDocument()
    expect(screen.getByText('Reduces wrinkles')).toBeInTheDocument()
  })

  it('displays evidence level badges', async () => {
    getRecommendations.mockResolvedValue(mockRecs)

    render(
      <BrowserRouter>
        <Recommendations />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('RCT')).toBeInTheDocument()
    })
    expect(screen.getByText('meta')).toBeInTheDocument()
  })

  it('displays effect size, time to effect, and ROI', async () => {
    getRecommendations.mockResolvedValue(mockRecs)

    render(
      <BrowserRouter>
        <Recommendations />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('80% effect')).toBeInTheDocument()
    })
    expect(screen.getByText('90% effect')).toBeInTheDocument()
    expect(screen.getByText('4 weeks')).toBeInTheDocument()
    expect(screen.getByText('8 weeks')).toBeInTheDocument()

    // ROI appears twice (once per recommendation)
    const roiElements = screen.getAllByText(/ROI:/)
    expect(roiElements).toHaveLength(2)
  })

  it('displays priority badges', async () => {
    getRecommendations.mockResolvedValue(mockRecs)

    render(
      <BrowserRouter>
        <Recommendations />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('#1')).toBeInTheDocument()
    })
    expect(screen.getByText('#2')).toBeInTheDocument()
  })

  it('handles error gracefully', async () => {
    getRecommendations.mockRejectedValue(new Error('API error'))

    render(
      <BrowserRouter>
        <Recommendations />
      </BrowserRouter>
    )

    await waitFor(() => {
      // After error, loading should stop and no recommendations rendered
      expect(screen.queryByText('Loading recommendations...')).not.toBeInTheDocument()
    })
    // No recommendation items rendered
    expect(screen.queryByText('Vitamin C Serum')).not.toBeInTheDocument()
  })
})
