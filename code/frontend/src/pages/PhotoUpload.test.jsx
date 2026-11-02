import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'

// Mock the API client
vi.mock('../api/client', () => ({
  uploadPhoto: vi.fn(),
  analyzePhoto: vi.fn(() => Promise.resolve({ message: 'Analysis complete' })),
}))

import PhotoUpload from './PhotoUpload'
import { uploadPhoto, analyzePhoto } from '../api/client'

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

    expect(screen.getByText('Przód')).toBeInTheDocument()
    expect(screen.getByText('Bok')).toBeInTheDocument()
    expect(screen.getByText('Tył')).toBeInTheDocument()
    // D1: skin and hairline come from the front photo
    expect(screen.getByText(/Analiza: twarz, skóra, brwi, zarost, linia włosów/)).toBeInTheDocument()
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
      expect(screen.getByText(/Nie udało się wysłać zdjęcia: Network error/)).toBeInTheDocument()
    })
  })

  it('shows the backend reason when the photo is rejected', async () => {
    const err = new Error('Request failed with status code 400')
    err.response = { data: { detail: 'Zdjęcie jest za duże (limit 15 MB).' } }
    uploadPhoto.mockRejectedValue(err)
    const user = userEvent.setup()
    render(
      <BrowserRouter>
        <PhotoUpload />
      </BrowserRouter>
    )
    await user.upload(screen.getAllByLabelText('Choose File')[0], new File(['x'], 'a.jpg', { type: 'image/jpeg' }))
    expect(await screen.findByText(/limit 15 MB/)).toBeInTheDocument()
  })

  it('starts the analysis after upload (the UI never did before)', async () => {
    uploadPhoto.mockResolvedValue({ id: 7, url: 'a.jpg', quality: { ok: true, problems: [] } })
    analyzePhoto.mockResolvedValue({ message: 'Analysis complete' })
    const user = userEvent.setup()
    render(
      <BrowserRouter>
        <PhotoUpload />
      </BrowserRouter>
    )
    await user.upload(screen.getAllByLabelText('Choose File')[0], new File(['x'], 'a.jpg', { type: 'image/jpeg' }))
    expect(await screen.findByText('Analiza gotowa')).toBeInTheDocument()
    expect(analyzePhoto).toHaveBeenCalledWith(7, false)
    expect(screen.getByText('Zobacz wyniki analizy')).toBeInTheDocument()
  })

  it('poor quality: shows problems, analyses only on request', async () => {
    uploadPhoto.mockResolvedValue({
      id: 8, url: 'b.jpg', quality: { ok: false, problems: ['Zdjęcie jest nieostre — oprzyj telefon albo użyj samowyzwalacza.'] },
    })
    analyzePhoto.mockResolvedValue({ message: 'Analysis complete' })
    const user = userEvent.setup()
    render(
      <BrowserRouter>
        <PhotoUpload />
      </BrowserRouter>
    )
    await user.upload(screen.getAllByLabelText('Choose File')[1], new File(['x'], 'b.jpg', { type: 'image/jpeg' }))
    expect(await screen.findByText(/nieostre/)).toBeInTheDocument()
    expect(analyzePhoto).not.toHaveBeenCalled()
    await user.click(screen.getByText('Analizuj mimo to'))
    expect(analyzePhoto).toHaveBeenCalledWith(8, true)
  })

  it('AI unavailable is shown, not hidden', async () => {
    uploadPhoto.mockResolvedValue({ id: 9, url: 'c.jpg', quality: { ok: true, problems: [] } })
    const err = new Error('503')
    err.response = { status: 503, data: { detail: 'Usługa AI jest teraz niedostępna — spróbuj ponownie później.' } }
    analyzePhoto.mockRejectedValue(err)
    const user = userEvent.setup()
    render(
      <BrowserRouter>
        <PhotoUpload />
      </BrowserRouter>
    )
    await user.upload(screen.getAllByLabelText('Choose File')[2], new File(['x'], 'c.jpg', { type: 'image/jpeg' }))
    expect(await screen.findByText(/AI jest teraz niedostępna/)).toBeInTheDocument()
  })
})
