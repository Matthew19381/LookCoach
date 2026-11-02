import { describe, it, expect } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import Layout, { NAV_GROUPS } from './Layout'

const renderLayout = () => render(<BrowserRouter><Layout /></BrowserRouter>)

describe('Layout', () => {
  it('shows grouped Polish navigation in the sidebar', () => {
    renderLayout()
    const nav = screen.getByRole('navigation', { name: 'Nawigacja' })
    for (const title of ['Analiza', 'Plan', 'Styl życia', 'Więcej']) {
      expect(within(nav).getByText(title)).toBeInTheDocument()
    }
    expect(within(nav).getByText('Dziś').closest('a')).toHaveAttribute('href', '/')
    expect(within(nav).getByText('Zdjęcia').closest('a')).toHaveAttribute('href', '/photos')
    expect(within(nav).getByText('Rekomendacje').closest('a')).toHaveAttribute('href', '/recommendations')
    expect(nav.textContent).not.toMatch(/Upload|Recommendations|Experiments/)
  })

  it('every page is reachable exactly once', () => {
    const paths = NAV_GROUPS.flatMap((g) => g.items.map((i) => i.to))
    expect(new Set(paths).size).toBe(paths.length)
    expect(paths.length).toBe(20)
  })

  it('mobile menu toggles', async () => {
    const user = userEvent.setup()
    renderLayout()
    await user.click(screen.getByRole('button', { name: 'Otwórz menu' }))
    expect(screen.getAllByRole('navigation', { name: 'Nawigacja' })).toHaveLength(2)
    await user.click(screen.getByRole('button', { name: 'Zamknij menu' }))
    expect(screen.getAllByRole('navigation', { name: 'Nawigacja' })).toHaveLength(1)
  })
})
