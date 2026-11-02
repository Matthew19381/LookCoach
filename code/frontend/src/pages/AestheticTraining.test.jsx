import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

vi.mock('../api/client', () => ({
  getEcosystemNeeds: vi.fn(),
  sendEcosystemNeeds: vi.fn(),
}))

import AestheticTraining from './AestheticTraining'
import { getEcosystemNeeds, sendEcosystemNeeds } from '../api/client'

const needs = (current, last_sent = null) => ({
  aesthetic_priority: { target_module: 'forge-body', current, last_sent },
  nutrition_needs: { target_module: 'dieta', current: null, last_sent: null },
})

describe('AestheticTraining (LC-4: priorytet dla ForgeBody, bez planów)', () => {
  beforeEach(() => vi.clearAllMocks())

  it('shows muscle priorities in Polish and no plan generator', async () => {
    getEcosystemNeeds.mockResolvedValue(needs({ muscle_groups: ['side_delts', 'rear_delts'], duration_weeks: 4, reason: 'Analiza zdjęcia' }))
    render(<AestheticTraining />)
    expect(await screen.findByText('boczne aktony barków')).toBeInTheDocument()
    expect(screen.getByText('tylne aktony barków')).toBeInTheDocument()
    expect(document.body.textContent).not.toMatch(/reps|sets|Weekly Schedule/i)
  })

  it('sends to ForgeBody', async () => {
    getEcosystemNeeds.mockResolvedValue(needs({ muscle_groups: ['glutes'], duration_weeks: 4 }))
    sendEcosystemNeeds.mockResolvedValue({ queued: ['aesthetic_priority'] })
    const user = userEvent.setup()
    render(<AestheticTraining />)
    await user.click(await screen.findByRole('button', { name: 'Wyślij do ForgeBody' }))
    expect(sendEcosystemNeeds).toHaveBeenCalledWith(false)
    expect(await screen.findByText('Priorytet przekazany do ForgeBody.')).toBeInTheDocument()
  })

  it('resend forces when already sent', async () => {
    getEcosystemNeeds.mockResolvedValue(needs({ muscle_groups: ['glutes'], duration_weeks: 4 },
      { payload: {}, status: 'sent', timestamp: '2026-11-01T10:00:00Z' }))
    sendEcosystemNeeds.mockResolvedValue({ queued: ['aesthetic_priority'] })
    const user = userEvent.setup()
    render(<AestheticTraining />)
    expect(await screen.findByText(/wysłane/)).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Wyślij ponownie do ForgeBody' }))
    expect(sendEcosystemNeeds).toHaveBeenCalledWith(true)
  })

  it('says when there is nothing to pass on', async () => {
    getEcosystemNeeds.mockResolvedValue(needs(null))
    render(<AestheticTraining />)
    expect(await screen.findByText(/nie wskazuje teraz niczego/)).toBeInTheDocument()
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })
})
