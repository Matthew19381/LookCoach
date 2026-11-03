import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'

vi.mock('../api/client', () => ({
  assistantChat: vi.fn(),
  getAssistantHistory: vi.fn(() => Promise.resolve([])),
  clearAssistantHistory: vi.fn(() => Promise.resolve({ deleted: 2 })),
  sendEcosystemNeeds: vi.fn(() => Promise.resolve({ queued: [] })),
  startExperiment: vi.fn(),
}))

import Assistant from './Assistant'
import { assistantChat, sendEcosystemNeeds } from '../api/client'

const renderPage = () => render(<BrowserRouter><Assistant /></BrowserRouter>)

describe('Assistant', () => {
  beforeEach(() => vi.clearAllMocks())

  it('sends a message and shows the reply', async () => {
    assistantChat.mockResolvedValue({ reply: 'Zacznij od SPF (RCT).', actions: [], flags: [] })
    const user = userEvent.setup()
    renderPage()
    await user.type(screen.getByLabelText('Wiadomość'), 'Od czego zacząć?')
    await user.click(screen.getByRole('button', { name: 'Wyślij' }))
    expect(assistantChat).toHaveBeenCalledWith('Od czego zacząć?')
    expect(await screen.findByText('Zacznij od SPF (RCT).')).toBeInTheDocument()
  })

  it('actions run only after confirmation', async () => {
    assistantChat.mockResolvedValue({
      reply: 'Przekaż priorytety.', actions: [{ type: 'send_needs', label: 'Wyślij potrzeby do ForgeBody/Diety' }], flags: [],
    })
    const user = userEvent.setup()
    renderPage()
    await user.click(screen.getByText('Od czego zacząć przy moich wynikach?'))
    const action = await screen.findByText('Wyślij potrzeby do ForgeBody/Diety')

    vi.spyOn(window, 'confirm').mockReturnValueOnce(false)
    await user.click(action)
    expect(sendEcosystemNeeds).not.toHaveBeenCalled()

    vi.spyOn(window, 'confirm').mockReturnValueOnce(true)
    await user.click(action)
    expect(sendEcosystemNeeds).toHaveBeenCalled()
    expect(await screen.findByText('Zrobione.')).toBeInTheDocument()
  })

  it('shows when the assistant is unavailable', async () => {
    const err = new Error('503')
    err.response = { data: { detail: 'Asystent jest niedostępny' } }
    assistantChat.mockRejectedValue(err)
    const user = userEvent.setup()
    renderPage()
    await user.type(screen.getByLabelText('Wiadomość'), 'Hej')
    await user.click(screen.getByRole('button', { name: 'Wyślij' }))
    expect(await screen.findByText('Asystent jest niedostępny')).toBeInTheDocument()
  })
})
