import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import SleepOptimizer from './SleepOptimizer'
import { getSleepFactors, analyzeSleep, getPreEventSleepTips } from '../api/client'

vi.mock('../api/client', () => ({
  getSleepFactors: vi.fn(),
  analyzeSleep: vi.fn(),
  getPreEventSleepTips: vi.fn(),
}))

const mockFactors = {
  duration: { name: 'Sleep Duration', looks_impact: 'Skin repair', optimal: '7-9 hours', poor: '<6' },
  quality: { name: 'Sleep Quality', looks_impact: 'Skin glow', optimal: 'Głęboki', poor: 'Fragmented' },
}

describe('SleepOptimizer', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getSleepFactors.mockResolvedValue(mockFactors)
  })

  it('renders sleep optimizer page', async () => {
    render(
      <BrowserRouter>
        <SleepOptimizer />
      </BrowserRouter>
    )
    await waitFor(() => {
      expect(screen.getByText('Sleep Optimizer')).toBeInTheDocument()
    })
  })

  it('loads and displays factors', async () => {
    render(
      <BrowserRouter>
        <SleepOptimizer />
      </BrowserRouter>
    )
    await waitFor(() => {
      expect(screen.getByText('Sleep Duration')).toBeInTheDocument()
      expect(screen.getByText('Sleep Quality')).toBeInTheDocument()
    })
  })

  it('analyzes sleep data', async () => {
    analyzeSleep.mockResolvedValue({ status: 'needs_improvement', status_label: 'do poprawy', issues: [], recommendations: ['Sleep more'] })
    const user = userEvent.setup()
    render(
      <BrowserRouter>
        <SleepOptimizer />
      </BrowserRouter>
    )
    await waitFor(() => {
      expect(screen.getByText('Sleep Optimizer')).toBeInTheDocument()
    })
    const analyzeBtn = screen.getByText('Oceń sen')
    await user.click(analyzeBtn)
    await waitFor(() => {
      expect(analyzeSleep).toHaveBeenCalled()
    })
    expect(await screen.findByText('Stan: do poprawy')).toBeInTheDocument()
    expect(document.body.textContent).not.toMatch(/\/100/)
  })

  it('loads pre-event tips', async () => {
    getPreEventSleepTips.mockResolvedValue(['Sleep 8+ hours', 'Cool room'])
    const user = userEvent.setup()
    render(
      <BrowserRouter>
        <SleepOptimizer />
      </BrowserRouter>
    )
    await waitFor(() => {
      expect(screen.getByText('Sleep Optimizer')).toBeInTheDocument()
    })
    const getTipsBtn = screen.getByText('Pokaż wskazówki')
    await user.click(getTipsBtn)
    await waitFor(() => {
      expect(getPreEventSleepTips).toHaveBeenCalled()
    })
  })
})
