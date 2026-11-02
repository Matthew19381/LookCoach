import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import NutritionLooks from './NutritionLooks'
import { getNutritionFactors, getNutritionRecommendations, getEcosystemNeeds, sendEcosystemNeeds } from '../api/client'

vi.mock('../api/client', () => ({
  getNutritionFactors: vi.fn(),
  getNutritionRecommendations: vi.fn(),
  getEcosystemNeeds: vi.fn(),
  sendEcosystemNeeds: vi.fn(),
}))

const mockFactors = {
  water_intake: { name: 'Water Intake', looks_impact: 'Skin hydration', optimal: '8+ glasses', poor: '<4' },
  sugar: { name: 'Sugar', looks_impact: 'Acne, inflammation', optimal: 'None', poor: '>10 tsp/day' },
}

const mockRecommendations = ['Drink 8+ glasses of water daily', 'Avoid sugar for clear skin']
const mockNeeds = {
  aesthetic_priority: { target_module: 'forge-body', current: null, last_sent: null },
  nutrition_needs: {
    target_module: 'dieta',
    current: {
      sodium_limit_mg: 2300, low_glycemic_load: true, reason: 'Analiza zdjęcia: obrzęk',
      items: [{ need: 'low_glycemic_load', evidence_id: 'nutrition_005', evidence_level: 'rct' }],
    },
    last_sent: null,
  },
}

describe('NutritionLooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getNutritionFactors.mockResolvedValue(mockFactors)
    getNutritionRecommendations.mockResolvedValue(mockRecommendations)
    getEcosystemNeeds.mockResolvedValue(mockNeeds)
  })

  it('renders nutrition page', async () => {
    render(
      <BrowserRouter>
        <NutritionLooks />
      </BrowserRouter>
    )
    await waitFor(() => {
      expect(screen.getByText('Żywienie')).toBeInTheDocument()
    })
  })

  it('loads and displays factors', async () => {
    render(
      <BrowserRouter>
        <NutritionLooks />
      </BrowserRouter>
    )
    await waitFor(() => {
      expect(screen.getByText('Water Intake')).toBeInTheDocument()
      expect(screen.getByText('Sugar')).toBeInTheDocument()
    })
  })

  it('displays recommendations', async () => {
    render(
      <BrowserRouter>
        <NutritionLooks />
      </BrowserRouter>
    )
    await waitFor(() => {
      expect(screen.getByText('Drink 8+ glasses of water daily')).toBeInTheDocument()
    })
  })

  it('shows needs for Dieta with evidence and sends them (LC-4: no meal plan, no own diet log)', async () => {
    sendEcosystemNeeds.mockResolvedValue({ queued: ['nutrition_needs'] })
    const user = userEvent.setup()
    render(
      <BrowserRouter>
        <NutritionLooks />
      </BrowserRouter>
    )
    expect(await screen.findByText('Sód do 2300 mg dziennie')).toBeInTheDocument()
    expect(screen.getByText(/nutrition_005/)).toBeInTheDocument()
    expect(document.body.textContent).not.toMatch(/Meal Plan|Diet Analysis/)
    await user.click(screen.getByRole('button', { name: 'Wyślij do Diety' }))
    expect(sendEcosystemNeeds).toHaveBeenCalledWith(false)
    expect(await screen.findByText('Potrzeby przekazane do Diety.')).toBeInTheDocument()
  })
})
