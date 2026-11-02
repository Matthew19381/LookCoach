import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('../api/client', () => ({
  getEcosystemOverview: vi.fn(),
  getConnectionStatus: vi.fn(),
}))

import Connections from './Connections'
import { getEcosystemOverview, getConnectionStatus } from '../api/client'

const status = {
  outbox: {
    pending: 1, failed: 0,
    recent: [{ event_type: 'module_directive', status: 'pending', data: { target_module: 'forge-body' } }],
  },
  directives: { survival_mode: true, priority: 'skincare', quiet_hours: { from: '22:00', to: '07:00' } },
}

describe('Connections', () => {
  beforeEach(() => vi.clearAllMocks())

  it('shows data from other modules and the hub link', async () => {
    getEcosystemOverview.mockResolvedValue({
      source: 'hub', fetched_at: '2026-11-02T10:00:00',
      forge_body: { measurements: { values: { waist_cm: { label: 'Talia (cm)', latest: 84, trend: 'spada' } } }, workouts_last_7_days: 3 },
      dieta: { weight: { latest_kg: 80.8, trend: 'stabilnie' } },
      affect_last_7_days: { samples: 2, stress: 'wysoki' },
    })
    getConnectionStatus.mockResolvedValue(status)
    render(<Connections />)
    expect(await screen.findByText(/Talia \(cm\): 84/)).toBeInTheDocument()
    expect(screen.getByText(/80.8 kg/)).toBeInTheDocument()
    expect(screen.getByText(/stres: wysoki/)).toBeInTheDocument()
    expect(screen.getByText(/dyrektywa dla modułu → forge-body/)).toBeInTheDocument()
    expect(screen.getByText('Tryb przetrwania: włączony')).toBeInTheDocument()
  })

  it('says when the hub is down and nothing is cached', async () => {
    getEcosystemOverview.mockResolvedValue({ source: 'unavailable' })
    getConnectionStatus.mockResolvedValue(status)
    render(<Connections />)
    expect(await screen.findByText(/brak zapisanych danych/)).toBeInTheDocument()
  })
})
