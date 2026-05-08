import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'

// Mock react-chartjs-2 to avoid canvas issues in jsdom
vi.mock('react-chartjs-2', () => ({
  Line: (props) => <div data-testid="chart-line" />,
}))

// Mock chart.js - ChartJS.register is called on module load, we just need to not error
vi.mock('chart.js', () => ({
  Chart: {
    register: vi.fn(),
  },
  LineElement: {},
  PointElement: {},
  LinearScale: {},
  CategoryScale: {},
  Legend: {},
  Tooltip: {},
}))

// Mock the API client
vi.mock('../api/client', () => ({
  getTimeline: vi.fn(),
  comparePhotos: vi.fn(),
}))

import ProgressTracker from './ProgressTracker'
import { getTimeline, comparePhotos } from '../api/client'

const mockPhotos = [
  {
    id: 1,
    photo_type: 'front',
    url: '/uploads/photo1.jpg',
    uploaded_at: '2026-05-01T10:00:00Z',
    status: 'done',
  },
  {
    id: 2,
    photo_type: 'side',
    url: '/uploads/photo2.jpg',
    uploaded_at: '2026-05-03T10:00:00Z',
    status: 'done',
  },
  {
    id: 3,
    photo_type: 'back',
    url: '/uploads/photo3.jpg',
    uploaded_at: '2026-05-05T10:00:00Z',
    status: 'done',
  },
]

describe('ProgressTracker', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    getTimeline.mockReturnValue(new Promise(() => {}))

    render(
      <BrowserRouter>
        <ProgressTracker />
      </BrowserRouter>
    )

    expect(screen.getByText('Loading progress...')).toBeInTheDocument()
  })

  it('renders photo timeline after data loaded', async () => {
    getTimeline.mockResolvedValue(mockPhotos)

    render(
      <BrowserRouter>
        <ProgressTracker />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Photo Timeline')).toBeInTheDocument()
    })

    // Check that photos are rendered
    expect(screen.getByAltText('front')).toBeInTheDocument()
    expect(screen.getByAltText('side')).toBeInTheDocument()
    expect(screen.getByAltText('back')).toBeInTheDocument()
  })

  it('renders compare section', async () => {
    getTimeline.mockResolvedValue(mockPhotos)

    render(
      <BrowserRouter>
        <ProgressTracker />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Compare Photos')).toBeInTheDocument()
    })

    expect(screen.getByText('Select before photo...')).toBeInTheDocument()
    expect(screen.getByText('Select after photo...')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Compare' })).toBeInTheDocument()
  })

  it('calls comparePhotos when compare button clicked', async () => {
    getTimeline.mockResolvedValue(mockPhotos)
    comparePhotos.mockResolvedValue({
      before: { url: '/uploads/photo1.jpg' },
      after: { url: '/uploads/photo2.jpg' },
      delta_score: 5,
    })

    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <ProgressTracker />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Compare Photos')).toBeInTheDocument()
    })

    // Select before and after photos
    const selectBefore = screen.getAllByRole('combobox')[0]
    const selectAfter = screen.getAllByRole('combobox')[1]

    await user.selectOptions(selectBefore, '1')
    await user.selectOptions(selectAfter, '2')

    // Click compare
    const compareButton = screen.getByRole('button', { name: 'Compare' })
    await user.click(compareButton)

    expect(comparePhotos).toHaveBeenCalledWith(1, 2)
  })

  it('displays compare result after successful comparison', async () => {
    getTimeline.mockResolvedValue(mockPhotos)
    comparePhotos.mockResolvedValue({
      before: { url: '/uploads/photo1.jpg' },
      after: { url: '/uploads/photo2.jpg' },
      delta_score: 5,
    })

    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <ProgressTracker />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Compare Photos')).toBeInTheDocument()
    })

    const selectBefore = screen.getAllByRole('combobox')[0]
    const selectAfter = screen.getAllByRole('combobox')[1]

    await user.selectOptions(selectBefore, '1')
    await user.selectOptions(selectAfter, '2')

    const compareButton = screen.getByRole('button', { name: 'Compare' })
    await user.click(compareButton)

    await waitFor(() => {
      expect(screen.getByAltText('Before')).toBeInTheDocument()
      expect(screen.getByAltText('After')).toBeInTheDocument()
    })

    expect(screen.getByText(/Score Change:/)).toBeInTheDocument()
  })

  it('renders chart when photos loaded', async () => {
    getTimeline.mockResolvedValue(mockPhotos)

    render(
      <BrowserRouter>
        <ProgressTracker />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Look Score Over Time')).toBeInTheDocument()
    })

    // Chart component should be rendered (mocked as div with data-testid)
    expect(screen.getByTestId('chart-line')).toBeInTheDocument()
  })
})
