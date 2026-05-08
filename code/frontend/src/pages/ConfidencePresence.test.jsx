import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
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
    overall_score: 75,
    issues: ['Slouching', 'Forward head posture'],
    recommendations: ['Keep shoulders back', 'Chin tuck exercise'],
  },
  facial: {
    overall_score: 80,
    issues: ['Tense jaw', 'Limited eye contact'],
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
  confidence_score: 76,  // unique, not 75
  presence_score: 81,   // unique, not 80
  attractiveness_boost_pct: 15,
  tip: 'Confidence is key to attractiveness',
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

  it('displays posture indicators', async () => {
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

    // Posture score 75 is unique (others are 76, 80, 81)
    expect(screen.getByText('75')).toBeInTheDocument()
    expect(screen.getByText('• Slouching')).toBeInTheDocument()
    expect(screen.getByText('• Forward head posture')).toBeInTheDocument()
  })

  it('displays posture recommendations', async () => {
    getConfidenceAnalysis.mockResolvedValue(mockAnalysis)
    getActionPlan.mockResolvedValue({ plan: mockPlan })
    getAttractivenessImpact.mockResolvedValue(mockImpact)

    render(
      <BrowserRouter>
        <ConfidencePresence />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Recommendations:')).toBeInTheDocument()
    })

    expect(screen.getByText('• Keep shoulders back')).toBeInTheDocument()
    expect(screen.getByText('• Chin tuck exercise')).toBeInTheDocument()
  })

  it('displays facial expressions', async () => {
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

    // Facial score 80 is unique (others: 75, 76, 81)
    expect(screen.getByText('80')).toBeInTheDocument()
    expect(screen.getByText('• Tense jaw')).toBeInTheDocument()
    expect(screen.getByText('• Limited eye contact')).toBeInTheDocument()
  })

  it('displays micro-habits', async () => {
    getConfidenceAnalysis.mockResolvedValue(mockAnalysis)
    getActionPlan.mockResolvedValue({ plan: mockPlan })
    getAttractivenessImpact.mockResolvedValue(mockImpact)

    render(
      <BrowserRouter>
        <ConfidencePresence />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Micro-Habits:')).toBeInTheDocument()
    })

    expect(screen.getByText('• Smile at strangers')).toBeInTheDocument()
    expect(screen.getByText('• Practice power poses')).toBeInTheDocument()
  })

  it('displays attractiveness impact', async () => {
    getConfidenceAnalysis.mockResolvedValue(mockAnalysis)
    getActionPlan.mockResolvedValue({ plan: mockPlan })
    getAttractivenessImpact.mockResolvedValue(mockImpact)

    render(
      <BrowserRouter>
        <ConfidencePresence />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Attractiveness Impact of Confidence')).toBeInTheDocument()
    })

    // Confidence score 76 unique
    expect(screen.getByText('76')).toBeInTheDocument()
    // Presence score 81 unique
    expect(screen.getByText('81')).toBeInTheDocument()
    expect(screen.getByText('+15%')).toBeInTheDocument()
    expect(screen.getByText('Confidence is key to attractiveness')).toBeInTheDocument()
  })

  it('displays 7-day action plan', async () => {
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
