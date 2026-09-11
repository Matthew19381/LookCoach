import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'


vi.mock('../api/client', () => ({
  getRecommendations: vi.fn(),
}))

import PriorityBoard from './PriorityBoard'
import { getRecommendations } from '../api/client'

const mockRecs = [
  {
    id: 1,
    name: 'Gentle Cleansing',
    description: 'A low-effort starting point',
    category: 'skincare',
    evidence_level: 'expert',
    confidence: 'low',
    time_to_effect: 2,
    roi_score: 0.14,
  },
  {
    id: 2,
    name: 'Sleep Deprivation Avoided',
    description: 'Protect the nightly recovery window',
    category: 'sleep',
    evidence_level: 'RCT',
    confidence: 'high',
    time_to_effect: 1,
    roi_score: 0.8,
  },
  {
    id: 3,
    name: 'Consistent Schedule',
    description: 'Keep sleep timing stable',
    category: 'sleep',
    evidence_level: 'observational',
    confidence: 'moderate',
    time_to_effect: 7,
    roi_score: 0.32,
  },
]

describe('PriorityBoard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading and then the ROI priority view', async () => {
    getRecommendations.mockResolvedValue(mockRecs)

    render(<PriorityBoard />)

    expect(screen.getByText('Loading ROI priorities...')).toBeInTheDocument()
    await waitFor(() => expect(screen.getByText('ROI priorities')).toBeInTheDocument())
    expect(screen.getAllByText('3')).toHaveLength(2)
    // "High potential" appears in stat card, tab, and article - check it's present
    expect(screen.getAllByText('High potential').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Moderate potential').length).toBeGreaterThan(0)
  })

  it('orders interventions by ROI and does not expose raw scores', async () => {
    getRecommendations.mockResolvedValue([...mockRecs].reverse())

    render(<PriorityBoard />)

    await waitFor(() => expect(screen.getByText('Sleep Deprivation Avoided')).toBeInTheDocument())
    const articles = screen.getAllByRole('article')
    expect(articles[0]).toHaveTextContent('Sleep Deprivation Avoided')
    expect(articles[1]).toHaveTextContent('Consistent Schedule')
    expect(articles[2]).toHaveTextContent('Gentle Cleansing')
    expect(screen.queryByText('0.8')).not.toBeInTheDocument()
    expect(screen.queryByText('ROI score')).not.toBeInTheDocument()
  })

  it('filters the board by evidence-adjusted potential', async () => {
    getRecommendations.mockResolvedValue(mockRecs)
    const user = userEvent.setup()

    render(<PriorityBoard />)
    await waitFor(() => expect(screen.getByText('Gentle Cleansing')).toBeInTheDocument())

    await user.click(screen.getByRole('tab', { name: 'High potential' }))
    const highBand = screen.getByRole('tabpanel')
    expect(highBand).toHaveTextContent('Sleep Deprivation Avoided')
    expect(highBand).not.toHaveTextContent('Gentle Cleansing')

    await user.click(screen.getByRole('tab', { name: 'Exploratory' }))
    expect(screen.getByRole('tabpanel')).toHaveTextContent('Gentle Cleansing')
  })

  it('handles an API error without crashing', async () => {
    getRecommendations.mockRejectedValue(new Error('API error'))

    render(<PriorityBoard />)

    await waitFor(() => expect(screen.getByText('Priority data could not be loaded. Please try again.')).toBeInTheDocument())
    expect(screen.queryByText('Loading ROI priorities...')).not.toBeInTheDocument()
  })
})