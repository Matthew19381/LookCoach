import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('../api/client', () => ({
  getStyleAdvice: vi.fn(),
  getStylePreviewOptions: vi.fn(() => Promise.resolve({ hair: [], beard: ['zarost 3-5 mm'] })),
  generateStylePreview: vi.fn(),
}))

import Style from './Style'
import userEvent from '@testing-library/user-event'
import { getStyleAdvice, generateStylePreview } from '../api/client'

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

  it('preview asks for confirmation of the paid call, then shows image and warning', async () => {
    getStyleAdvice.mockResolvedValue({
      has_front_photo: true, has_side_photo: false,
      hair: { proposals: [{ name: 'Quiff', tell_barber: 'x', styling_minutes: 8, level: 'porada stylistyczna' }], notes: [] },
      brows: [], beard: [], eyes: [], glasses: [], clothing: [], colors: [],
    })
    generateStylePreview.mockResolvedValue({ image: 'data:image/png;base64,AAA', warning: 'To wizualizacja', remaining_today: 4 })
    const user = userEvent.setup()
    render(<Style />)
    await user.click(await screen.findByText('Podgląd na moim zdjęciu'))
    expect(screen.getByRole('dialog')).toHaveTextContent('płatne wywołanie API')
    expect(generateStylePreview).not.toHaveBeenCalled()
    await user.click(screen.getByRole('button', { name: 'Generuj' }))
    expect(generateStylePreview).toHaveBeenCalledWith('hair', 'Quiff')
    expect(await screen.findByAltText('Podgląd')).toBeInTheDocument()
    expect(screen.getByText('To wizualizacja')).toBeInTheDocument()
    await user.click(screen.getByText('zarost 3-5 mm'))
    expect(screen.getByRole('dialog')).toHaveTextContent('zarost 3-5 mm')
  })
})
