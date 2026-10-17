import { describe, it, expect, vi, beforeEach } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'

// Mock the API client
vi.mock('../api/client', () => ({
  getSkincareRoutine: vi.fn(),
  getProducts: vi.fn(() => Promise.resolve([])),
  getMyRotation: vi.fn(() => Promise.resolve({ actives: [], recommendations: [] })),
  deleteProduct: vi.fn(),
  logProductUsage: vi.fn(),
  logSkinReaction: vi.fn(),
  parseProductText: vi.fn(),
  saveProduct: vi.fn(),
  scanProductLabel: vi.fn(),
  getRoutineToday: vi.fn(() => new Promise(() => {})),
  getMyRoutine: vi.fn(() => new Promise(() => {})),
  createDefaultRoutine: vi.fn(),
  addRoutineStep: vi.fn(),
  updateRoutineStep: vi.fn(),
  deleteRoutineStep: vi.fn(),
  logAdherence: vi.fn(),
}))

import SkincareRoutine from './SkincareRoutine'
import {
  addRoutineStep, createDefaultRoutine, getMyRoutine, getRoutineToday, getSkincareRoutine, logAdherence,
} from '../api/client'

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

    expect(screen.getByText('Wczytuję rutynę…')).toBeInTheDocument()
  })

  it('renders routine after data loaded', async () => {
    getSkincareRoutine.mockResolvedValue(mockRoutine)

    render(
      <BrowserRouter>
        <SkincareRoutine />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Pielęgnacja')).toBeInTheDocument()
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
      expect(screen.getByText('Typ skóry: Combination')).toBeInTheDocument()
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
      expect(screen.getByText('Rano')).toBeInTheDocument()
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
      expect(screen.getByText('Wieczór')).toBeInTheDocument()
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
      expect(screen.getByText('Rutyna niedostępna — sprawdź, czy backend działa.')).toBeInTheDocument()
    })
  })

  it('shows the product scanner', async () => {
    getSkincareRoutine.mockResolvedValue(mockRoutine)
    render(<BrowserRouter><SkincareRoutine /></BrowserRouter>)
    await waitFor(() => expect(screen.getByText('Moje produkty')).toBeInTheDocument())
    expect(screen.getByText('Zrób zdjęcie składu (INCI)')).toBeInTheDocument()
  })

  it('handles error gracefully', async () => {
    getSkincareRoutine.mockRejectedValue(new Error('API error'))

    render(
      <BrowserRouter>
        <SkincareRoutine />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Rutyna niedostępna — sprawdź, czy backend działa.')).toBeInTheDocument()
    })
  })

  describe('my routine and today', () => {
    const evidence = { level: 'RCT', ref: 'Hughes 2013', url: 'https://pubmed.ncbi.nlm.nih.gov/23732711/' }
    const step = (id, slot, name, extra = {}) => ({ id, slot, name, position: 0, weekdays: '0123456', essential: false,
      active: true, note: null, evidence: null, evidence_key: null, ...extra })
    const proposal = { saved: false, steps: [step(null, 'morning', 'Krem z filtrem SPF 30+', { evidence, essential: true })] }
    const emptyToday = { date: '2026-10-17', has_routine: false, survival_mode: false,
      slots: [{ slot: 'morning', protocol_type: 'skincare_morning', done: false, steps: [] },
        { slot: 'evening', protocol_type: 'skincare_evening', done: false, steps: [] }] }
    const savedToday = { ...emptyToday, has_routine: true,
      slots: [{ slot: 'morning', protocol_type: 'skincare_morning', done: false, steps: [step(1, 'morning', 'Krem z filtrem SPF 30+')] },
        { slot: 'evening', protocol_type: 'skincare_evening', done: true, steps: [step(2, 'evening', 'Zmyj twarz')] }] }
    const saved = { saved: true, steps: [step(1, 'morning', 'Krem z filtrem SPF 30+'), step(2, 'evening', 'Zmyj twarz')] }

    beforeEach(() => getSkincareRoutine.mockResolvedValue(null))

    it('offers the research-based proposal with its source and saves it', async () => {
      getRoutineToday.mockResolvedValueOnce(emptyToday).mockResolvedValue(savedToday)
      getMyRoutine.mockResolvedValueOnce(proposal).mockResolvedValue(saved)
      createDefaultRoutine.mockResolvedValue({ created: true })
      render(<BrowserRouter><SkincareRoutine /></BrowserRouter>)

      await waitFor(() => expect(screen.getByText(/Nie masz jeszcze zapisanej rutyny/)).toBeInTheDocument())
      expect(screen.getByText(/Dowody: RCT\. Hughes 2013/)).toBeInTheDocument()
      expect(screen.getByRole('link', { name: 'źródło' })).toHaveAttribute('href', evidence.url)

      fireEvent.click(screen.getByText('Zapisz jako moją rutynę'))
      await waitFor(() => expect(createDefaultRoutine).toHaveBeenCalled())
      await waitFor(() => expect(screen.getByRole('button', { name: 'Zrobione' })).toBeInTheDocument())
      expect(screen.queryByText('Zapisz jako moją rutynę')).not.toBeInTheDocument()
    })

    it('shows today and marks a slot as done', async () => {
      getRoutineToday.mockResolvedValue(savedToday)
      getMyRoutine.mockResolvedValue(saved)
      logAdherence.mockResolvedValue({})
      render(<BrowserRouter><SkincareRoutine /></BrowserRouter>)

      await waitFor(() => expect(screen.getByText('Dziś')).toBeInTheDocument())
      // evening already done: one button only, for the morning
      const buttons = screen.getAllByRole('button', { name: 'Zrobione' })
      expect(buttons).toHaveLength(1)
      fireEvent.click(buttons[0])
      await waitFor(() => expect(logAdherence).toHaveBeenCalledWith({ protocol_type: 'skincare_morning', completed: true }))
      expect(getRoutineToday).toHaveBeenCalledTimes(2)
    })

    it('adds an own step on chosen days', async () => {
      getRoutineToday.mockResolvedValue(savedToday)
      getMyRoutine.mockResolvedValue(saved)
      addRoutineStep.mockResolvedValue({})
      render(<BrowserRouter><SkincareRoutine /></BrowserRouter>)

      await waitFor(() => expect(screen.getByText('Dodaj krok')).toBeInTheDocument())
      fireEvent.change(screen.getByLabelText('Pora'), { target: { value: 'evening' } })
      fireEvent.change(screen.getByPlaceholderText('np. Krem z filtrem SPF 50'), { target: { value: 'Retinol' } })
      for (const d of ['Wt', 'Cz', 'So', 'Nd']) fireEvent.click(screen.getByLabelText(d))
      fireEvent.click(screen.getByRole('button', { name: /Dodaj$/ }))
      await waitFor(() => expect(addRoutineStep).toHaveBeenCalledWith({ slot: 'evening', name: 'Retinol', weekdays: '024' }))
    })
  })
})
