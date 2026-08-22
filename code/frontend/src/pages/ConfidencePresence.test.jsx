import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'

// Mock the API client
vi.mock('../api/client', () => ({
  getConfidenceAnalysis: vi.fn(),
  getActionPlan: vi.fn(),
  getAttractivenessImpact: vi.fn(),
}))

import ConfidencePresence from './ConfidencePresence'
import { getConfidenceAnalysis, getActionPlan, getAttractivenessImpact } from '../api/client'

const mockAnalysis = {
  posture: {
    status: 'needs_work',
    issues: ['Slouching', 'Forward head posture'],
    recommendations: ['Keep shoulders back', 'Chin tuck exercise'],
  },
  facial: {
    status: 'good',
    issues: [],
    micro_habits: ['Smile at strangers', 'Practice power poses'],
  },
}

const mockPlan = [
  {
    day: 1,
    focus: 'Posture',
    actions: ['Shoulder rolls', 'Wall slides'],
  },
  {
    day: 2,
    focus: 'Eye contact',
    actions: ['Hold gaze 3 seconds', 'Look at triangle method'],
  },
]

const mockImpact = {
  perception_change: 'Moderate boost',
  tip: 'Confidence is key to presence',
}

describe('ConfidencePresence', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    getConfidenceAnalysis.mockReturnValue(new Promise(() => {}))
    getActionPlan.mockReturnValue(new Promise(() => {}))
    getAttractivenessImpact.mockReturnValue(new Promise(() => {}))

    render(
      <BrowserRouter>
        <ConfidencePresence />
      </BrowserRouter>
    )

    expect(screen.getByText('Loading confidence analysis...')).toBeInTheDocument()
  })

  it('renders confidence analysis after data loaded', async () => {
    getConfidenceAnalysis.mockResolvedValue(mockAnalysis)
    getActionPlan.mockResolvedValue({ plan: mockPlan })
    getAttractivenessImpact.mockResolvedValue(mockImpact)

    render(
      <BrowserRouter>
        <ConfidencePresence />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Confidence & Presence')).toBeInTheDocument()
    })
  })

  it('displays qualitative posture status instead of numeric score', async () => {
    getConfidenceAnalysis.mockResolvedValue(mockAnalysis)
    getActionPlan.mockResolvedValue({ plan: mockPlan })
    getAttractivenessImpact.mockResolvedValue(mockImpact)

    render(
      <BrowserRouter>
        <ConfidencePresence />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Posture Indicators')).toBeInTheDocument()
    })

    expect(screen.getByText('Needs work')).toBeInTheDocument()
    expect(screen.getByText('• Slouching')).toBeInTheDocument()
    expect(screen.getByText('• Forward head posture')).toBeInTheDocument()
    // No numeric rating rendered
    expect(screen.queryByText(/Overall Score/i)).not.toBeInTheDocument()
  })

  it('displays facial status badge and micro-habits', async () => {
    getConfidenceAnalysis.mockResolvedValue(mockAnalysis)
    getActionPlan.mockResolvedValue({ plan: mockPlan })
    getAttractivenessImpact.mockResolvedValue(mockImpact)

    render(
      <BrowserRouter>
        <ConfidencePresence />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Facial Expressions')).toBeInTheDocument()
    })

    expect(screen.getByText('Good')).toBeInTheDocument()
    expect(screen.getByText('• Smile at strangers')).toBeInTheDocument()
    expect(screen.getByText('• Practice power poses')).toBeInTheDocument()
  })

  it('displays impact without fabricated percentage boosts', async () => {
    getConfidenceAnalysis.mockResolvedValue(mockAnalysis)
    getActionPlan.mockResolvedValue({ plan: mockPlan })
    getAttractivenessImpact.mockResolvedValue(mockImpact)

    render(
      <BrowserRouter>
        <ConfidencePresence />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Moderate boost')).toBeInTheDocument()
    })

    expect(screen.getByText('Confidence is key to presence')).toBeInTheDocument()
    expect(screen.queryByText(/\+15%/)).not.toBeInTheDocument()
  })

  it('displays action plan', async () => {
    getConfidenceAnalysis.mockResolvedValue(mockAnalysis)
    getActionPlan.mockResolvedValue({ plan: mockPlan })
    getAttractivenessImpact.mockResolvedValue(mockImpact)

    render(
      <BrowserRouter>
        <ConfidencePresence />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('7-Day Confidence Building Plan')).toBeInTheDocument()
    })

    expect(screen.getByText('Day 1:')).toBeInTheDocument()
    expect(screen.getByText('Posture')).toBeInTheDocument()
    expect(screen.getByText(/Shoulder rolls/)).toBeInTheDocument()
    expect(screen.getByText('Day 2:')).toBeInTheDocument()
    expect(screen.getByText('Eye contact')).toBeInTheDocument()
  })

  it('handles error gracefully', async () => {
    getConfidenceAnalysis.mockRejectedValue(new Error('API error'))
    getActionPlan.mockRejectedValue(new Error('API error'))
    getAttractivenessImpact.mockRejectedValue(new Error('API error'))

    render(
      <BrowserRouter>
        <ConfidencePresence />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.queryByText('Loading confidence analysis...')).not.toBeInTheDocument()
    })
  })
})
