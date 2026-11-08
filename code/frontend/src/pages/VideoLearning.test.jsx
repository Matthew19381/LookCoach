import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'

// Mock the API client
vi.mock('../api/client', () => ({
  getRecommendedVideos: vi.fn(),
  searchVideos: vi.fn(),
}))

import VideoLearning from './VideoLearning'
import { getRecommendedVideos, searchVideos } from '../api/client'

const mockVideos = [
  {
    id: 'vid1',
    title: 'Gua Sha Tutorial',
    description: 'Learn gua sha basics',
    evidence_note: '[HIPOTEZA] brak badań',
    url: 'https://www.youtube.com/results?search_query=gua+sha',
  },
  {
    id: 'vid2',
    title: 'Skincare Routine',
    description: 'Morning and evening routine',
    evidence_note: '[HIPOTEZA] mała próba',
    study_url: 'https://pubmed.ncbi.nlm.nih.gov/26904154/',
    url: 'https://www.youtube.com/results?search_query=skincare',
  },
]

describe('VideoLearning', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    getRecommendedVideos.mockReturnValue(new Promise(() => {}))

    render(
      <BrowserRouter>
        <VideoLearning />
      </BrowserRouter>
    )

    expect(screen.getByText('Ładowanie...')).toBeInTheDocument()
  })

  it('renders videos after data loaded', async () => {
    getRecommendedVideos.mockResolvedValue(mockVideos)

    render(
      <BrowserRouter>
        <VideoLearning />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Wideo')).toBeInTheDocument()
    })

    expect(screen.getByText('Gua Sha Tutorial')).toBeInTheDocument()
    expect(screen.getByText('Skincare Routine')).toBeInTheDocument()
  })

  it('displays video details', async () => {
    getRecommendedVideos.mockResolvedValue(mockVideos)

    render(
      <BrowserRouter>
        <VideoLearning />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Gua Sha Tutorial')).toBeInTheDocument()
    })

    expect(screen.getByText('Learn gua sha basics')).toBeInTheDocument()
    expect(screen.getByText('[HIPOTEZA] brak badań')).toBeInTheDocument()
    expect(screen.getByText('Badanie')).toHaveAttribute('href', 'https://pubmed.ncbi.nlm.nih.gov/26904154/')
    expect(screen.queryByText(/•/)).not.toBeInTheDocument()
  })

  it('has search form', async () => {
    getRecommendedVideos.mockResolvedValue([])

    render(
      <BrowserRouter>
        <VideoLearning />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Szukaj techniki/)).toBeInTheDocument()
    })

    expect(screen.getByRole('button', { name: /Szukaj/ })).toBeInTheDocument()
  })

  it('performs search when form submitted', async () => {
    getRecommendedVideos.mockResolvedValue([])
    searchVideos.mockResolvedValue([mockVideos[0]])

    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <VideoLearning />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Szukaj techniki/)).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText(/Szukaj techniki/)
    await user.type(searchInput, 'gua sha')

    const searchButton = screen.getByRole('button', { name: /Szukaj/ })
    await user.click(searchButton)

    expect(searchVideos).toHaveBeenCalledWith('gua sha')
  })

  it('displays search results', async () => {
    getRecommendedVideos.mockResolvedValue([])
    searchVideos.mockResolvedValue([mockVideos[0]])

    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <VideoLearning />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Szukaj techniki/)).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText(/Szukaj techniki/)
    await user.type(searchInput, 'gua sha')

    const searchButton = screen.getByRole('button', { name: /Szukaj/ })
    await user.click(searchButton)

    await waitFor(() => {
      expect(screen.getByText(/Wyniki dla „gua sha”: 1/)).toBeInTheDocument()
    })

    expect(screen.getByText('Gua Sha Tutorial')).toBeInTheDocument()
  })

  it('clears search results', async () => {
    getRecommendedVideos.mockResolvedValue(mockVideos)
    searchVideos.mockResolvedValue([mockVideos[0]])

    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <VideoLearning />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Gua Sha Tutorial')).toBeInTheDocument()
    })

    // Perform search
    const searchInput = screen.getByPlaceholderText(/Szukaj techniki/)
    await user.type(searchInput, 'gua sha')
    await user.click(screen.getByRole('button', { name: /Szukaj/ }))

    await waitFor(() => {
      expect(screen.getByText(/Wyniki dla/)).toBeInTheDocument()
    })

    // Clear search
    const clearButton = screen.getByText('Wyczyść')
    await user.click(clearButton)

    await waitFor(() => {
      expect(screen.queryByText(/Wyniki dla/)).not.toBeInTheDocument()
    })

    // Should show recommended videos again
    expect(screen.getByText('Gua Sha Tutorial')).toBeInTheDocument()
  })

  it('shows no videos message when empty', async () => {
    getRecommendedVideos.mockResolvedValue([])

    render(
      <BrowserRouter>
        <VideoLearning />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText(/Nie znaleziono techniki/)).toBeInTheDocument()
    })
  })

  it('links to YouTube search, not to unverified videos', async () => {
    getRecommendedVideos.mockResolvedValue(mockVideos)

    render(
      <BrowserRouter>
        <VideoLearning />
      </BrowserRouter>
    )

    await waitFor(() => {
      const links = screen.getAllByText('Szukaj na YouTube')
      expect(links).toHaveLength(2)
      expect(links[0]).toHaveAttribute('href', 'https://www.youtube.com/results?search_query=gua+sha')
      expect(links[1]).toHaveAttribute('href', 'https://www.youtube.com/results?search_query=skincare')
    })
  })
})
