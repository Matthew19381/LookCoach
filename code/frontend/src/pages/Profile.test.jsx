import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

vi.mock('../api/client', () => ({ getProfile: vi.fn(), updateProfile: vi.fn() }))

import Profile from './Profile'
import { getProfile, updateProfile } from '../api/client'

const base = {
  goals: { focus: ['skin'], deadline: null, minutes_per_day: 10, styling_minutes: null, constraints: null },
  health: { pregnancy: false, heart_disease: false, kidney_disease: false, back_injury: false,
    shoulder_injury: false, knee_injury: false, sensitive_skin: false },
  lifestyle: {}, mode: 'free', discipline_score: 50,
}

describe('Profile', () => {
  beforeEach(() => vi.clearAllMocks())

  it('saves goals and health flags', async () => {
    getProfile.mockResolvedValue(base)
    updateProfile.mockImplementation(async (b) => ({ ...base, ...b }))
    const user = userEvent.setup()
    render(<Profile />)
    await user.click(await screen.findByLabelText('Włosy'))
    await user.click(screen.getByLabelText('Ciąża lub karmienie'))
    await user.click(screen.getByRole('button', { name: 'Zapisz' }))
    const sent = updateProfile.mock.calls[0][0]
    expect(sent.goals.focus).toEqual(['skin', 'hair'])
    expect(sent.health.pregnancy).toBe(true)
    expect(await screen.findByText('Zapisano.')).toBeInTheDocument()
  })

  it('explains a validation error', async () => {
    getProfile.mockResolvedValue(base)
    const err = new Error('422')
    err.response = { status: 422 }
    updateProfile.mockRejectedValue(err)
    const user = userEvent.setup()
    render(<Profile />)
    await user.click(await screen.findByRole('button', { name: 'Zapisz' }))
    expect(await screen.findByText(/poza zakresem/)).toBeInTheDocument()
  })
})
