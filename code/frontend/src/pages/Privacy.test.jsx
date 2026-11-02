import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

vi.mock('../api/client', () => ({
  dataExportUrl: vi.fn(() => '/api/v1/data/export?user_id=1'),
  deleteAllData: vi.fn(),
}))

import Privacy from './Privacy'
import { deleteAllData } from '../api/client'

describe('Privacy', () => {
  beforeEach(() => vi.clearAllMocks())

  it('links to the data export', () => {
    render(<Privacy />)
    expect(screen.getByText('Pobierz archiwum').closest('a')).toHaveAttribute('href', '/api/v1/data/export?user_id=1')
  })

  it('delete is disabled until the exact phrase is typed', async () => {
    const user = userEvent.setup()
    render(<Privacy />)
    const button = screen.getByRole('button', { name: /Usuń trwale/ })
    expect(button).toBeDisabled()
    await user.type(screen.getByLabelText('Fraza potwierdzenia'), 'usun')
    expect(button).toBeDisabled()
    await user.clear(screen.getByLabelText('Fraza potwierdzenia'))
    await user.type(screen.getByLabelText('Fraza potwierdzenia'), 'USUN-WSZYSTKO')
    expect(button).toBeEnabled()
  })

  it('deletes and confirms', async () => {
    deleteAllData.mockResolvedValue({ status: 'deleted' })
    const user = userEvent.setup()
    render(<Privacy />)
    await user.type(screen.getByLabelText('Fraza potwierdzenia'), 'USUN-WSZYSTKO')
    await user.click(screen.getByRole('button', { name: /Usuń trwale/ }))
    expect(deleteAllData).toHaveBeenCalledWith('USUN-WSZYSTKO')
    expect(await screen.findByText(/trwale usunięte/)).toBeInTheDocument()
  })
})
