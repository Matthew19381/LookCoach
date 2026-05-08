import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'

// Mock the API client
vi.mock('../api/client', () => ({
  uploadPhoto: vi.fn(),
  getPhotos: vi.fn()
}))

import PhotoUpload from './PhotoUpload'
import { uploadPhoto } from '../api/client'

describe('PhotoUpload', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders upload page with title', () => {
    render(
      <BrowserRouter>
        <PhotoUpload />
      </BrowserRouter>
    )

    expect(screen.getByText('Upload Your Photos')).toBeInTheDocument()
    expect(screen.getByText(/Upload front, side, and back photos/)).toBeInTheDocument()
  })

  it('shows 3 upload zones (front, side, back)', () => {
    render(
      <BrowserRouter>
        <PhotoUpload />
      </BrowserRouter>
    )

    expect(screen.getByText('front View')).toBeInTheDocument()
    expect(screen.getByText('side View')).toBeInTheDocument()
    expect(screen.getByText('back View')).toBeInTheDocument()
  })

  it('shows "Uploaded!" after successful upload', async () => {
    uploadPhoto.mockResolvedValue({ id: 1, url: 'test.jpg' })
    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <PhotoUpload />
      </BrowserRouter>
    )

    // Find the file input and upload a file
    const fileInputs = screen.getAllByLabelText('Choose File')
    const file = new File([''], 'test.jpg', { type: 'image/jpeg' })

    await user.upload(fileInputs[0], file)

    await waitFor(() => {
      expect(screen.getByText('Uploaded!')).toBeInTheDocument()
    })
  })

  it('calls uploadPhoto with correct arguments', async () => {
    uploadPhoto.mockResolvedValue({ id: 1 })
    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <PhotoUpload />
      </BrowserRouter>
    )

    const fileInputs = screen.getAllByLabelText('Choose File')
    const file = new File([''], 'front.jpg', { type: 'image/jpeg' })

    await user.upload(fileInputs[0], file)

    await waitFor(() => {
      expect(uploadPhoto).toHaveBeenCalledWith(expect.any(File), 'front')
    })
  })

  it('shows error message on upload failure', async () => {
    uploadPhoto.mockRejectedValue(new Error('Network error'))
    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <PhotoUpload />
      </BrowserRouter>
    )

    const fileInputs = screen.getAllByLabelText('Choose File')
    const file = new File([''], 'test.jpg', { type: 'image/jpeg' })

    await user.upload(fileInputs[0], file)

    await waitFor(() => {
      expect(screen.getByText(/Upload failed/)).toBeInTheDocument()
    })
  })
})
