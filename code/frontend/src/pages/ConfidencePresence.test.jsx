import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'

// Mock the API client
vi.mock('../api/client', () => ({
  getConfidenceAnalysis: vi.fn(),
  getActionPlan: vi.fn(),
}))

import ConfidencePresence from './ConfidencePresence'
import { getConfidenceAnalysis, getActionPlan } from '../api/client'

const mockAnalysis = {
  has_analysis: true,
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

describe('ConfidencePresence', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    getConfidenceAnalysis.mockReturnValue(new Promise(() => {}))
    getActionPlan.mockReturnValue(new Promise(() => {}))

    render(
      <BrowserRouter>
        <ConfidencePresence />
      </BrowserRouter>
    )

    expect(screen.getByText('Ładowanie analizy...')).toBeInTheDocument()
  })

  it('renders confidence analysis after data loaded', async () => {
    getConfidenceAnalysis.mockResolvedValue(mockAnalysis)
    getActionPlan.mockResolvedValue({ plan: mockPlan })

    render(
      <BrowserRouter>
        <ConfidencePresence />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Pewność siebie')).toBeInTheDocument()
    })
  })

  it('displays qualitative posture status instead of numeric score', async () => {
    getConfidenceAnalysis.mockResolvedValue(mockAnalysis)
    getActionPlan.mockResolvedValue({ plan: mockPlan })

    render(
      <BrowserRouter>
        <ConfidencePresence />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Postawa')).toBeInTheDocument()
    })

    expect(screen.getByText('Do pracy')).toBeInTheDocument()
    expect(screen.getByText('• Slouching')).toBeInTheDocument()
    expect(screen.getByText('• Forward head posture')).toBeInTheDocument()
    // No numeric rating rendered
    expect(screen.queryByText(/Overall Score/i)).not.toBeInTheDocument()
  })

  it('displays facial status badge and micro-habits', async () => {
    getConfidenceAnalysis.mockResolvedValue(mockAnalysis)
    getActionPlan.mockResolvedValue({ plan: mockPlan })

    render(
      <BrowserRouter>
        <ConfidencePresence />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Mimika')).toBeInTheDocument()
    })

    expect(screen.getByText('Dobrze')).toBeInTheDocument()
    expect(screen.getByText('• Smile at strangers')).toBeInTheDocument()
    expect(screen.getByText('• Practice power poses')).toBeInTheDocument()
  })

  it('has no attractiveness percentage or "#1 most attractive" claim (LC-1/LC-9)', async () => {
    getConfidenceAnalysis.mockResolvedValue(mockAnalysis)
    getActionPlan.mockResolvedValue({ plan: mockPlan })

    render(
      <BrowserRouter>
        <ConfidencePresence />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Postawa')).toBeInTheDocument()
    })
    expect(document.body.textContent).not.toMatch(/most attractive|boost|%/i)
  })

  it('tells the user to take photos when there is no analysis', async () => {
    getConfidenceAnalysis.mockResolvedValue({
      has_analysis: false, message: 'Brak analizy zdjęć — zrób zdjęcia.', posture: null, facial: null,
    })
    getActionPlan.mockResolvedValue({ plan: mockPlan })

    render(
      <BrowserRouter>
        <ConfidencePresence />
      </BrowserRouter>
    )

    expect(await screen.findByText('Brak analizy zdjęć — zrób zdjęcia.')).toBeInTheDocument()
    expect(screen.queryByText('Postawa')).not.toBeInTheDocument()
  })

  it('displays action plan', async () => {
    getConfidenceAnalysis.mockResolvedValue(mockAnalysis)
    getActionPlan.mockResolvedValue({ plan: mockPlan })

    render(
      <BrowserRouter>
        <ConfidencePresence />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('7-dniowy plan')).toBeInTheDocument()
    })

    expect(screen.getByText('Dzień 1:')).toBeInTheDocument()
    expect(screen.getByText('Posture')).toBeInTheDocument()
    expect(screen.getByText(/Shoulder rolls/)).toBeInTheDocument()
    expect(screen.getByText('Dzień 2:')).toBeInTheDocument()
    expect(screen.getByText('Eye contact')).toBeInTheDocument()
  })

  it('handles error gracefully', async () => {
    getConfidenceAnalysis.mockRejectedValue(new Error('API error'))
    getActionPlan.mockRejectedValue(new Error('API error'))

    render(
      <BrowserRouter>
        <ConfidencePresence />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.queryByText('Ładowanie analizy...')).not.toBeInTheDocument()
    })
  })
})
