import { describe, it, expect, vi, beforeEach } from 'vitest'

// Use vi.hoisted to define mocks before module load
const mockGet = vi.hoisted(() => vi.fn())
const mockPost = vi.hoisted(() => vi.fn())
const mockAxiosInstance = vi.hoisted(() => ({
  get: mockGet,
  post: mockPost,
  interceptors: {
    response: {
      use: vi.fn((fn) => fn)
    }
  }
}))

vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => mockAxiosInstance)
  }
}))

import { getUserId, getRecommendations } from './client'

describe('getUserId', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('generates and stores a new user ID if none exists', () => {
    const id = getUserId()
    expect(id).toBeTruthy()
    expect(localStorage.getItem('lookcoach_user_id')).toBe(String(id))
  })

  it('returns existing user ID from localStorage', () => {
    localStorage.setItem('lookcoach_user_id', '12345')
    const id = getUserId()
    expect(id).toBe(12345)
  })
})

describe('getRecommendations', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('calls correct endpoint with default limit', async () => {
    mockGet.mockResolvedValue([{ id: 1, name: 'Test' }])

    await getRecommendations()

    expect(mockGet).toHaveBeenCalledWith('/api/v1/recommendations/?limit=10')
  })

  it('calls correct endpoint with custom limit', async () => {
    mockGet.mockResolvedValue([{ id: 1 }])

    await getRecommendations(5)

    expect(mockGet).toHaveBeenCalledWith('/api/v1/recommendations/?limit=5')
  })
})
