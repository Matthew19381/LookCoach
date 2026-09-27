import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import ConsistencyTracker from './ConsistencyTracker'

// Mock the API client
vi.mock('../api/client', () => ({
  logAdherence: vi.fn(),
  getAdherenceHistory: vi.fn(),
  getAdherenceRate: vi.fn(),
  getRecommendedDifficulty: vi.fn(),
  getAllProtocolsStatus: vi.fn(),
  getConsistencySummary: vi.fn(),
  getMinimumEffectiveProtocol: vi.fn(),
  recalculateMetrics: vi.fn(),
  getPatternAlert: vi.fn(),
}))

import * as api from '../api/client'

const mockLogAdherence = api.logAdherence
const mockGetAdherenceHistory = api.getAdherenceHistory
const mockGetAdherenceRate = api.getAdherenceRate
const mockGetRecommendedDifficulty = api.getRecommendedDifficulty
const mockGetAllProtocolsStatus = api.getAllProtocolsStatus
const mockGetConsistencySummary = api.getConsistencySummary
const mockGetMinimumEffectiveProtocol = api.getMinimumEffectiveProtocol
const mockRecalculateMetrics = api.recalculateMetrics
const mockGetPatternAlert = api.getPatternAlert

describe('ConsistencyTracker', () => {
  const mockProtocols = [
    {
      protocol_type: 'skincare',
      adherence_rate: 0.8,
      adherence_level: 'GOOD',
      current_difficulty: 'full',
      recommended_difficulty: 'full'
    },
    {
      protocol_type: 'exercise',
      adherence_rate: 0.6,
      adherence_level: 'MODERATE',
      current_difficulty: 'full',
      recommended_difficulty: 'reduced'
    }
  ]

  const mockSummary = {
    average_adherence: 0.75,  // real API field (was overall_consistency_score, never returned)
    system_status: 'stable',
    total_protocols: 2,
    protocols_needing_reduction: 1,
  }

  const mockAlerts = [
    {
      protocol_type: 'exercise',
      message: 'Consistency has dropped below recommended threshold',
      severity: 'warning'
    }
  ]

  beforeEach(() => {
    mockGetAllProtocolsStatus.mockResolvedValue({ protocols: mockProtocols })
    mockGetConsistencySummary.mockResolvedValue(mockSummary)
    mockGetPatternAlert.mockResolvedValue({ alerts: mockAlerts, has_alerts: true })
    mockLogAdherence.mockResolvedValue({ ok: true })
    mockRecalculateMetrics.mockResolvedValue({ ok: true })
    mockGetAdherenceHistory.mockResolvedValue({ logs: [] })
    mockGetAdherenceRate.mockResolvedValue({ adherence_rate: 0.8, adherence_level: 'GOOD' })
    mockGetRecommendedDifficulty.mockResolvedValue({ recommended_difficulty: 'full', needs_reduction: false })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    render(<ConsistencyTracker />)
    expect(screen.getByText('Loading consistency tracker...')).toBeInTheDocument()
  })

  it('renders consistency summary after loading', async () => {
    render(<ConsistencyTracker />)
    
    await waitFor(() => {
      expect(screen.getByText('Consistency Summary')).toBeInTheDocument()
    })
    
    expect(screen.getByText('75%')).toBeInTheDocument() // Overall Score
    expect(screen.getByText('stable')).toBeInTheDocument() // System Status
    expect(screen.getByText('2')).toBeInTheDocument() // Protocols
    expect(screen.getByText('1')).toBeInTheDocument() // Need Adjustment
  })

  it('renders pattern alerts when present', async () => {
    render(<ConsistencyTracker />)
    
    await waitFor(() => {
      expect(screen.getByText('Pattern Alerts')).toBeInTheDocument()
    })
    
    // 'exercise' appears in the alert and in the protocol status card
    expect(screen.getAllByText('exercise').length).toBeGreaterThanOrEqual(2)
    expect(screen.getByText('Consistency has dropped below recommended threshold')).toBeInTheDocument()
  })

  it('allows logging adherence', async () => {
    render(<ConsistencyTracker />)
    
    await waitFor(() => {
      expect(screen.getByText('Consistency Summary')).toBeInTheDocument()
    })
    
    fireEvent.change(screen.getByLabelText('Protocol Type'), { target: { value: 'skincare' } })
    
    fireEvent.change(screen.getByLabelText('Date'), { target: { value: '2026-09-18' } })
    
    fireEvent.change(screen.getByLabelText('Completed'), { target: { value: 'true' } })
    fireEvent.change(screen.getByLabelText('Difficulty Level'), { target: { value: 'full' } })
    
    fireEvent.change(screen.getByLabelText('Notes'), { target: { value: 'Test notes' } })
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: 'Log Adherence' }))
    
    await waitFor(() => {
      expect(mockLogAdherence).toHaveBeenCalledWith({
        protocol_type: 'skincare',
        completed: true,
        date: '2026-09-18',
        difficulty_level: 'full',
        notes: 'Test notes'
      })
    })
  })

  it('shows protocol status overview', async () => {
    render(<ConsistencyTracker />)
    
    await waitFor(() => {
      expect(screen.getByText('Protocol Status')).toBeInTheDocument()
    })
    
    const statusCard = screen.getByText('Protocol Status').parentElement
    expect(within(statusCard).getByText('skincare')).toBeInTheDocument()
    expect(within(statusCard).getByText('exercise')).toBeInTheDocument()
    
    // Check that adherence rates are displayed
    expect(screen.getByText('80%')).toBeInTheDocument() // skincare rate
    expect(screen.getByText('60%')).toBeInTheDocument() // exercise rate
  })

  it('loads history and analysis for selected protocol', async () => {
    render(<ConsistencyTracker />)
    
    await waitFor(() => {
      expect(screen.getByText('Consistency Summary')).toBeInTheDocument()
    })
    
    fireEvent.change(screen.getByLabelText('Protocol Type'), { target: { value: 'skincare' } })
    
    // Click to load history
    fireEvent.click(screen.getByText('Load History & Analysis'))
    
    await waitFor(() => {
      expect(mockGetAdherenceHistory).toHaveBeenCalledWith('skincare')
      expect(mockGetAdherenceRate).toHaveBeenCalledWith('skincare')
      expect(mockGetRecommendedDifficulty).toHaveBeenCalledWith('skincare')
    })
  })

  it('recalculates metrics when requested', async () => {
    render(<ConsistencyTracker />)
    
    await waitFor(() => {
      expect(screen.getByText('Consistency Summary')).toBeInTheDocument()
    })
    
    fireEvent.change(screen.getByLabelText('Protocol Type'), { target: { value: 'skincare' } })
    
    // Click to recalculate
    fireEvent.click(screen.getByText('Recalculate Metrics'))
    
    await waitFor(() => {
      expect(mockRecalculateMetrics).toHaveBeenCalled()
    })
  })
})