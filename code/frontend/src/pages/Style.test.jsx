import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('../api/client', () => ({ getStyleAdvice: vi.fn() }))

import Style from './Style'
import { getStyleAdvice } from '../api/client'

describe('Style', () => {
  it('shows hairstyles with barber text and labelled advice', async () => {
    getStyleAdvice.mockResolvedValue({
      has_front_photo: true, has_side_photo: false,
      hair: {
        proposals: [{ name: 'Quiff', tell_barber: 'boki krótko, góra 7-9 cm', styling_minutes: 8, level: 'porada stylistyczna' }],
        notes: [{ text: 'Konwencja fryzjerska', level: 'hipoteza' }],
      },
      brows: [{ text: 'Usuń włoski między brwiami', level: 'porada stylistyczna' }],
      beard: [{ text: 'Minoksydyl przeciwwskazany', level: 'blokada' }],
      eyes: [{ text: 'Sen 7-9 h', level: 'rct', evidence_id: 'sleep_001' }],
      glasses: [], clothing: [], colors: [{ text: 'Chłodne barwy', level: 'hipoteza' }],
    })
    render(<Style />)
    expect(await screen.findByText('Quiff')).toBeInTheDocument()
    expect(screen.getByText('boki krótko, góra 7-9 cm')).toBeInTheDocument()
    expect(screen.getByText('przeciwwskazanie')).toBeInTheDocument()
    expect(screen.getByText('badania (RCT) · sleep_001')).toBeInTheDocument()
    expect(screen.getByText('Kolorystyka (HIPOTEZA)')).toBeInTheDocument()
    expect(document.body.textContent).not.toMatch(/score|\/10|\/100/i)
  })

  it('asks for a front photo when there is none', async () => {
    getStyleAdvice.mockResolvedValue({
      has_front_photo: false, has_side_photo: false, hair: null,
      brows: [], beard: [], eyes: [], glasses: [], clothing: [], colors: [],
    })
    render(<Style />)
    expect(await screen.findByText(/zdjęcie z przodu/)).toBeInTheDocument()
  })
})
