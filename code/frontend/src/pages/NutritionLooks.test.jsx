import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import NutritionLooks from './NutritionLooks'
import { getNutritionFactors, getNutritionRecommendations, getMealPlan, analyzeDiet } from '../api/client'

vi.mock('../api/client', () => ({
  getNutritionFactors: vi.fn(),
  getNutritionRecommendations: vi.fn(),
  getMealPlan: vi.fn(),
  analyzeDiet: vi.fn(),
}))

const mockFactors = {
  water_intake: { name: 'Water Intake', looks_impact: 'Skin hydration', optimal: '8+ glasses', poor: '<4' },
  sugar: { name: 'Sugar', looks_impact: 'Acne, inflammation', optimal: 'None', poor: '>10 tsp/day' },
}

const mockRecommendations = ['Drink 8+ glasses of water daily', 'Avoid sugar for clear skin']
const mockMealPlan = [
  { timing: 'Morning', foods: 'Water, protein', looks_benefit: 'Hydration' },
]

describe('NutritionLooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    getNutritionFactors.mockResolvedValue(mockFactors)
    getNutritionRecommendations.mockResolvedValue(mockRecommendations)
    getMealPlan.mockResolvedValue(mockMealPlan)
  })

  it('renders nutrition page', async () => {
    render(
      <BrowserRouter>
        <NutritionLooks />
      </BrowserRouter>
    )
    await waitFor(() => {
      expect(screen.getByText('Nutrition for Looks')).toBeInTheDocument()
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

  it('analyzes diet', async () => {
    analyzeDiet.mockResolvedValue({ score: 75, issues: ['Low water'], recommendations: ['Drink more'] })
    const user = userEvent.setup()
    render(
      <BrowserRouter>
        <NutritionLooks />
      </BrowserRouter>
    )
    await waitFor(() => {
      expect(screen.getByText('Nutrition for Looks')).toBeInTheDocument()
    })
    const analyzeBtn = screen.getByText('Analyze Diet')
    await user.click(analyzeBtn)
    await waitFor(() => {
      expect(analyzeDiet).toHaveBeenCalled()
    })
  })
})
