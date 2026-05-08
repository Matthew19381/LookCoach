import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import StressManagement from './StressManagement'
import { getStressEffects, getRelaxationTechniques, analyzeStress } from '../api/client'

vi.mock('../api/client', () => ({
  getStressEffects: vi.fn(),
  getRelaxationTechniques: vi.fn(),
  analyzeStress: vi.fn(),
}))

const mockEffects = {
  cortisol_spike: { name: 'Cortisol Spike', looks_impact: 'Acne, skin thinning', signs: ['acne', 'oily skin'] },
}

const mockTechniques = [
  { name: 'Box Breathing', duration: '5 min', looks_benefit: 'Reduces cortisol' },
]

describe('StressManagement', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getStressEffects.mockResolvedValue(mockEffects)
    getRelaxationTechniques.mockResolvedValue(mockTechniques)
  })

  it('renders stress management page', async () => {
    render(
      <BrowserRouter>
        <StressManagement />
      </BrowserRouter>
    )
    await waitFor(() => {
      expect(screen.getByText('Stress Management')).toBeInTheDocument()
    })
  })

  it('loads and displays effects', async () => {
    render(
      <BrowserRouter>
        <StressManagement />
      </BrowserRouter>
    )
    await waitFor(() => {
      expect(screen.getByText('Cortisol Spike')).toBeInTheDocument()
    })
  })

  it('displays relaxation techniques', async () => {
    render(
      <BrowserRouter>
        <StressManagement />
      </BrowserRouter>
    )
    await waitFor(() => {
      expect(screen.getByText('Box Breathing')).toBeInTheDocument()
      expect(screen.getByText('Reduces cortisol')).toBeInTheDocument()
    })
  })

  it('analyzes stress data', async () => {
    analyzeStress.mockResolvedValue({ score: 70, effects: [], recommendations: ['Meditate'] })
    const user = userEvent.setup()
    render(
      <BrowserRouter>
        <StressManagement />
      </BrowserRouter>
    )
    await waitFor(() => {
      expect(screen.getByText('Stress Management')).toBeInTheDocument()
    })
    const analyzeBtn = screen.getByText('Analyze Stress')
    await user.click(analyzeBtn)
    await waitFor(() => {
      expect(analyzeStress).toHaveBeenCalled()
    })
  })
})
