import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Layout from './Layout'

describe('Layout', () => {
  it('renders navigation with all links', () => {
    render(
      <BrowserRouter>
        <Layout />
      </BrowserRouter>
    )

    // Check brand name
    expect(screen.getByText('LookCoach')).toBeInTheDocument()

    // Check all nav links are present
    expect(screen.getByText('Upload')).toBeInTheDocument()
    expect(screen.getByText('Analysis')).toBeInTheDocument()
    expect(screen.getByText('Recommendations')).toBeInTheDocument()
    expect(screen.getByText('Progress')).toBeInTheDocument()
    expect(screen.getByText('Skincare')).toBeInTheDocument()
    expect(screen.getByText('Videos')).toBeInTheDocument()
    expect(screen.getByText('Event Mode')).toBeInTheDocument()
    expect(screen.getByText('Confidence')).toBeInTheDocument()
    expect(screen.getByText('Experiments')).toBeInTheDocument()
  })

  it('has correct links for all nav items', () => {
    render(
      <BrowserRouter>
        <Layout />
      </BrowserRouter>
    )

    expect(screen.getByText('Upload').closest('a')).toHaveAttribute('href', '/')
    expect(screen.getByText('Analysis').closest('a')).toHaveAttribute('href', '/analysis')
    expect(screen.getByText('Recommendations').closest('a')).toHaveAttribute('href', '/recommendations')
    expect(screen.getByText('Experiments').closest('a')).toHaveAttribute('href', '/experiments')
  })
})
