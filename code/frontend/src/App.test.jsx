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
    expect(screen.getByText('LookCoach')).toBeInTheDocument()
  })

  it('has the correct routes', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )
    // Check navigation is present (from Layout)
    expect(screen.getByText('Upload')).toBeInTheDocument()
    expect(screen.getByText('Analysis')).toBeInTheDocument()
  })
})
