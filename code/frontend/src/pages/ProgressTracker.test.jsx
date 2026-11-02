import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'

vi.mock('../api/client', () => ({
  getTimeline: vi.fn(),
  comparePhotos: vi.fn(),
  getStateTimeline: vi.fn(() => Promise.resolve({ sessions: [], areas: [] })),
  getCorrelations: vi.fn(() => Promise.resolve({ insights: [], caveat: null, front_sessions: 1, needed_per_group: 2 })),
}))

import ProgressTracker from './ProgressTracker'
import { getTimeline, comparePhotos, getStateTimeline, getCorrelations } from '../api/client'

const mockPhotos = [
  { id: 1, photo_type: 'front', url: '/uploads/photo1.jpg', uploaded_at: '2026-05-01T10:00:00Z', status: 'done' },
  { id: 2, photo_type: 'side', url: '/uploads/photo2.jpg', uploaded_at: '2026-05-03T10:00:00Z', status: 'done' },
  { id: 3, photo_type: 'back', url: '/uploads/photo3.jpg', uploaded_at: '2026-05-05T10:00:00Z', status: 'done' },
]

const compareResponse = {
  before: { id: 1, url: '/uploads/photo1.jpg', photo_type: 'front', uploaded_at: '2026-05-01T10:00:00Z' },
  after: { id: 2, url: '/uploads/photo2.jpg', photo_type: 'front', uploaded_at: '2026-05-03T10:00:00Z' },
  same_type: true,
  changes: [
    { area: 'Obrzęk twarzy', before: 'średni', after: 'niski', changed: true },
    { area: 'Stan skóry twarzy', before: 'dobry', after: 'dobry', changed: false },
  ],
}

const renderPage = () =>
  render(
    <BrowserRouter>
      <ProgressTracker />
    </BrowserRouter>
  )

const pickAndCompare = async () => {
  const user = userEvent.setup()
  await waitFor(() => expect(screen.getByText('Porównaj zdjęcia')).toBeInTheDocument())
  await user.selectOptions(screen.getByLabelText('Zdjęcie przed'), '1')
  await user.selectOptions(screen.getByLabelText('Zdjęcie po'), '2')
  await user.click(screen.getByRole('button', { name: 'Porównaj' }))
}

describe('ProgressTracker', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    getTimeline.mockReturnValue(new Promise(() => {}))
    renderPage()
    expect(screen.getByText('Ładowanie postępu...')).toBeInTheDocument()
  })

  it('renders photo timeline after data loaded', async () => {
    getTimeline.mockResolvedValue(mockPhotos)
    renderPage()
    await waitFor(() => expect(screen.getByText('Oś czasu zdjęć')).toBeInTheDocument())
    expect(screen.getByAltText('przód')).toBeInTheDocument()
    expect(screen.getByAltText('bok')).toBeInTheDocument()
    expect(screen.getByAltText('tył')).toBeInTheDocument()
  })

  it('calls comparePhotos with selected ids', async () => {
    getTimeline.mockResolvedValue(mockPhotos)
    comparePhotos.mockResolvedValue(compareResponse)
    renderPage()
    await pickAndCompare()
    expect(comparePhotos).toHaveBeenCalledWith(1, 2)
  })

  it('shows qualitative changes, never a score (LC-9)', async () => {
    getTimeline.mockResolvedValue(mockPhotos)
    comparePhotos.mockResolvedValue(compareResponse)
    renderPage()
    await pickAndCompare()

    await waitFor(() => expect(screen.getByAltText('Przed')).toBeInTheDocument())
    expect(screen.getByLabelText('Suwak przed/po')).toHaveValue('50') // plan 5.2
    expect(screen.getByText('Obrzęk twarzy')).toBeInTheDocument()
    expect(screen.getByText('średni')).toBeInTheDocument()
    expect(document.body.textContent).not.toMatch(/score/i)
  })

  it('warns when comparing different photo types', async () => {
    getTimeline.mockResolvedValue(mockPhotos)
    comparePhotos.mockResolvedValue({ ...compareResponse, same_type: false })
    renderPage()
    await pickAndCompare()
    await waitFor(() => expect(screen.getByText(/różnych ujęć/)).toBeInTheDocument())
  })

  it('has no "Look Score" chart', async () => {
    getTimeline.mockResolvedValue(mockPhotos)
    renderPage()
    await waitFor(() => expect(screen.getByText('Oś czasu zdjęć')).toBeInTheDocument())
    expect(document.body.textContent).not.toMatch(/score/i)
  })

  it('shows the state timeline in words (plan 5.1)', async () => {
    getTimeline.mockResolvedValue(mockPhotos)
    getStateTimeline.mockResolvedValue({
      areas: ['Obrzęk twarzy'],
      sessions: [
        { photo_id: 1, date: '2026-09-01T10:00:00', labels: { 'Obrzęk twarzy': 'średni' } },
        { photo_id: 2, date: '2026-10-01T10:00:00', labels: { 'Obrzęk twarzy': 'niski' } },
      ],
    })
    renderPage()
    expect(await screen.findByText('Jak zmieniał się stan')).toBeInTheDocument()
    expect(screen.getByText('średni')).toBeInTheDocument()
    expect(screen.getByText('niski')).toBeInTheDocument()
  })

  it('shows correlations with the caveat (plan 5.3)', async () => {
    getTimeline.mockResolvedValue(mockPhotos)
    getCorrelations.mockResolvedValue({
      insights: [{ area: 'Skóra a regularna pielęgnacja', text: 'skóra była „dobra” w 2 z 2 sesji', sessions: 4 }],
      caveat: 'To zbieżność w Twoich danych, nie dowód przyczyny', front_sessions: 4, needed_per_group: 2,
    })
    renderPage()
    expect(await screen.findByText(/w 2 z 2 sesji/)).toBeInTheDocument()
    expect(screen.getByText(/nie dowód przyczyny/)).toBeInTheDocument()
  })
})
