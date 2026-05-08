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
    channel: 'Beauty Channel',
    duration: '10:30',
    description: 'Learn gua sha basics',
    url: 'https://youtube.com/watch?v=123',
  },
  {
    id: 'vid2',
    title: 'Skincare Routine',
    channel: 'Skincare Pro',
    duration: '15:45',
    description: 'Morning and evening routine',
    url: 'https://youtube.com/watch?v=456',
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

    expect(screen.getByText('Loading videos...')).toBeInTheDocument()
  })

  it('renders videos after data loaded', async () => {
    getRecommendedVideos.mockResolvedValue(mockVideos)

    render(
      <BrowserRouter>
        <VideoLearning />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Video Learning')).toBeInTheDocument()
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

    expect(screen.getByText('Beauty Channel • 10:30')).toBeInTheDocument()
    expect(screen.getByText('Learn gua sha basics')).toBeInTheDocument()
    expect(screen.getByText('Skincare Pro • 15:45')).toBeInTheDocument()
  })

  it('has search form', async () => {
    getRecommendedVideos.mockResolvedValue([])

    render(
      <BrowserRouter>
        <VideoLearning />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Search videos/)).toBeInTheDocument()
    })

    expect(screen.getByRole('button', { name: /Search/ })).toBeInTheDocument()
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
      expect(screen.getByPlaceholderText(/Search videos/)).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText(/Search videos/)
    await user.type(searchInput, 'gua sha')

    const searchButton = screen.getByRole('button', { name: /Search/ })
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
      expect(screen.getByPlaceholderText(/Search videos/)).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText(/Search videos/)
    await user.type(searchInput, 'gua sha')

    const searchButton = screen.getByRole('button', { name: /Search/ })
    await user.click(searchButton)

    await waitFor(() => {
      expect(screen.getByText(/Found 1 results for "gua sha"/)).toBeInTheDocument()
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
    const searchInput = screen.getByPlaceholderText(/Search videos/)
    await user.type(searchInput, 'gua sha')
    await user.click(screen.getByRole('button', { name: /Search/ }))

    await waitFor(() => {
      expect(screen.getByText(/Found.*results/)).toBeInTheDocument()
    })

    // Clear search
    const clearButton = screen.getByText('Clear')
    await user.click(clearButton)

    await waitFor(() => {
      expect(screen.queryByText(/Found.*results/)).not.toBeInTheDocument()
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
      expect(screen.getByText(/No videos found/)).toBeInTheDocument()
    })
  })

  it('has YouTube links', async () => {
    getRecommendedVideos.mockResolvedValue(mockVideos)

    render(
      <BrowserRouter>
        <VideoLearning />
      </BrowserRouter>
    )

    await waitFor(() => {
      const links = screen.getAllByText('Watch on YouTube')
      expect(links).toHaveLength(2)
      expect(links[0]).toHaveAttribute('href', 'https://youtube.com/watch?v=123')
      expect(links[1]).toHaveAttribute('href', 'https://youtube.com/watch?v=456')
    })
  })
})
