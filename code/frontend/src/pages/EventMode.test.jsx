import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'

// Mock the API client
vi.mock('../api/client', () => ({
  generateEventPlan: vi.fn(),
  getEventTips: vi.fn(),
}))

import EventMode from './EventMode'
import { generateEventPlan, getEventTips } from '../api/client'

const mockPlan = {
  event_type: 'party',
  days_until_event: 5,
  timeline: [
    {
      days_before: 5,
      actions: ['Start drinking more water', 'Get 8 hours sleep'],
    },
    {
      days_before: 2,
      actions: ['Exfoliate skin', 'Use face mask'],
    },
    {
      days_before: 0,
      actions: ['Cold water splash', 'Light makeup'],
    },
  ],
  day_of_event: ['Smile confidently', 'Stand tall'],
}

const mockTips = [
  'Drink water 2h before',
  'Avoid salty foods day before',
  'Get good sleep 2 nights before',
]

describe('EventMode', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders title and form', () => {
    render(
      <BrowserRouter>
        <EventMode />
      </BrowserRouter>
    )

    expect(screen.getByText('Event Mode')).toBeInTheDocument()
    expect(screen.getByLabelText('Event Date')).toBeInTheDocument()
    expect(screen.getByLabelText('Event Type')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Generate Plan/ })).toBeInTheDocument()
  })

  it('generates plan on submit', async () => {
    generateEventPlan.mockResolvedValue(mockPlan)

    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <EventMode />
      </BrowserRouter>
    )

    // Set event date
    const dateInput = screen.getByLabelText('Event Date')
    await user.type(dateInput, '2026-05-20')

    // Select event type
    const typeSelect = screen.getByLabelText('Event Type')
    await user.selectOptions(typeSelect, 'party')

    // Click generate
    const generateButton = screen.getByRole('button', { name: /Generate Plan/ })
    await user.click(generateButton)

    expect(generateEventPlan).toHaveBeenCalledWith('2026-05-20', 'party')
  })

  it('displays plan after generation', async () => {
    generateEventPlan.mockResolvedValue(mockPlan)

    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <EventMode />
      </BrowserRouter>
    )

    const dateInput = screen.getByLabelText('Event Date')
    await user.type(dateInput, '2026-05-20')

    const generateButton = screen.getByRole('button', { name: /Generate Plan/ })
    await user.click(generateButton)

    await waitFor(() => {
      expect(screen.getByText(/5 days until event/)).toBeInTheDocument()
    })

    // Check event type is displayed (the text is split, so check for parts)
    expect(screen.getByText(/Event Type:/)).toBeInTheDocument()
    expect(screen.getByText('party')).toBeInTheDocument()
  })

  it('shows timeline actions', async () => {
    generateEventPlan.mockResolvedValue(mockPlan)

    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <EventMode />
      </BrowserRouter>
    )

    const dateInput = screen.getByLabelText('Event Date')
    await user.type(dateInput, '2026-05-20')

    const generateButton = screen.getByRole('button', { name: /Generate Plan/ })
    await user.click(generateButton)

    await waitFor(() => {
      expect(screen.getByText('Daily Action Plan')).toBeInTheDocument()
    })

    expect(screen.getByText('5 days before')).toBeInTheDocument()
    expect(screen.getByText('2 days before')).toBeInTheDocument()
    expect(screen.getByText('Day of Event')).toBeInTheDocument()

    expect(screen.getByText('Start drinking more water')).toBeInTheDocument()
    expect(screen.getByText('Exfoliate skin')).toBeInTheDocument()
    expect(screen.getByText('Cold water splash')).toBeInTheDocument()
  })

  it('shows day of event quick actions', async () => {
    generateEventPlan.mockResolvedValue(mockPlan)

    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <EventMode />
      </BrowserRouter>
    )

    const dateInput = screen.getByLabelText('Event Date')
    await user.type(dateInput, '2026-05-20')

    const generateButton = screen.getByRole('button', { name: /Generate Plan/ })
    await user.click(generateButton)

    await waitFor(() => {
      expect(screen.getByText('Day of Event - Quick Actions')).toBeInTheDocument()
    })

    expect(screen.getByText('Smile confidently')).toBeInTheDocument()
    expect(screen.getByText('Stand tall')).toBeInTheDocument()
  })

  it('gets tips for event type', async () => {
    getEventTips.mockResolvedValue({ tips: mockTips })

    render(
      <BrowserRouter>
        <EventMode />
      </BrowserRouter>
    )

    // Click on Party button (among quick tips buttons)
    const partyButton = screen.getByRole('button', { name: 'Party' })
    await userEvent.setup().click(partyButton)

    expect(getEventTips).toHaveBeenCalledWith('party')
  })

  it('displays tips after fetching', async () => {
    getEventTips.mockResolvedValue({ tips: mockTips })

    render(
      <BrowserRouter>
        <EventMode />
      </BrowserRouter>
    )

    const partyButton = screen.getByRole('button', { name: 'Party' })
    await userEvent.setup().click(partyButton)

    await waitFor(() => {
      expect(screen.getByText('Drink water 2h before')).toBeInTheDocument()
    })

    expect(screen.getByText('Avoid salty foods day before')).toBeInTheDocument()
    expect(screen.getByText('Get good sleep 2 nights before')).toBeInTheDocument()
  })

  it('shows loading state during plan generation', async () => {
    // Mock a slow response
    let resolvePromise
    const promise = new Promise((resolve) => { resolvePromise = resolve })
    generateEventPlan.mockReturnValue(promise)

    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <EventMode />
      </BrowserRouter>
    )

    const dateInput = screen.getByLabelText('Event Date')
    await user.type(dateInput, '2026-05-20')

    const generateButton = screen.getByRole('button', { name: /Generate Plan/ })
    await user.click(generateButton)

    expect(screen.getByText('Generating...')).toBeInTheDocument()

    // Resolve the promise
    resolvePromise(mockPlan)

    await waitFor(() => {
      expect(screen.queryByText('Generating...')).not.toBeInTheDocument()
    })
  })
})
