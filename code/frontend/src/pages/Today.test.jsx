import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'

vi.mock('../api/client', () => ({ getToday: vi.fn() }))

import Today from './Today'
import { getToday } from '../api/client'

const renderPage = () => render(<BrowserRouter><Today /></BrowserRouter>)

describe('Today', () => {
  it('shows today actions, observed state and next photo session', async () => {
    getToday.mockResolvedValue({
      date: '2026-11-02', has_photos: true,
      actions: [{ title: 'Pielęgnacja rano', intention_cue: 'rano po umyciu twarzy', estimated_minutes: 5 }],
      directives: { survival_mode: false, priority: null },
      state: { 'Obrzęk twarzy': 'niski' }, next_photos_in_days: 6,
      wellbeing: { level: 'ok', message: null }, ecosystem: null,
    })
    renderPage()
    expect(await screen.findByText('Pielęgnacja rano')).toBeInTheDocument()
    expect(screen.getByText('niski')).toBeInTheDocument()
    expect(screen.getByText('Następne zdjęcia kontrolne za 6 dni.')).toBeInTheDocument()
  })

  it('first run points to photos; survival mode is acknowledged', async () => {
    getToday.mockResolvedValue({
      date: '2026-11-02', has_photos: false, actions: [],
      directives: { survival_mode: true, priority: null },
      state: {}, next_photos_in_days: null, wellbeing: { level: 'ok' }, ecosystem: null,
    })
    renderPage()
    expect(await screen.findByText(/Zacznij od zdjęć/)).toBeInTheDocument()
    expect(screen.getByText(/Tryb przetrwania/)).toBeInTheDocument()
  })
})
