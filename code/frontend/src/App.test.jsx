import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import App from './App'

describe('App', () => {
  it('renders without crashing', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )
    // Check that the Layout is rendered (it has "LookCoach" brand)
    expect(screen.getAllByText('LookCoach').length).toBeGreaterThan(0)
  })

  it('has the correct routes', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )
    // Check navigation is present (from Layout)
    expect(screen.getByText('Zdjęcia')).toBeInTheDocument()
    expect(screen.getByText('Wyniki analizy')).toBeInTheDocument()
  })
})
