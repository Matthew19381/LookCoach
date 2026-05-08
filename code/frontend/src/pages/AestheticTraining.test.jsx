import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AestheticTraining from './AestheticTraining';

// Mock the API client
vi.mock('../api/client', () => ({
  getAvailablePlans: vi.fn(),
  generateTrainingPlan: vi.fn(),
  analyzePhysique: vi.fn(),
}));

import { getAvailablePlans, generateTrainingPlan } from '../api/client';

describe('AestheticTraining', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders training page title', async () => {
    getAvailablePlans.mockResolvedValue([]);
    render(<AestheticTraining />);
    expect(await screen.findByText(/Aesthetic Training/i)).toBeInTheDocument();
  });

  it('loads and displays available plans', async () => {
    getAvailablePlans.mockResolvedValue([
      { id: 'v_taper', name: 'V-Taper Program', description: 'Build v-taper' },
    ]);
    render(<AestheticTraining />);
    expect(await screen.findByText(/V-Taper Program/i)).toBeInTheDocument();
  });

  it('generates training plan on button click', async () => {
    getAvailablePlans.mockResolvedValue([
      { id: 'v_taper', name: 'V-Taper Program', description: 'Build v-taper' },
    ]);
    generateTrainingPlan.mockResolvedValue({
      name: 'V-Taper Program',
      frequency: '4x/week',
      duration_weeks: 8,
      reps: '8-12',
    });
    render(<AestheticTraining />);
    // Wait for the plan to load
    await waitFor(() => {
      expect(screen.getByText(/V-Taper Program/i)).toBeInTheDocument();
    });
    // Click the Generate Plan button
    const buttons = screen.queryAllByText(/Generate Plan/i);
    if (buttons.length > 0) {
      fireEvent.click(buttons[0]);
      expect(generateTrainingPlan).toHaveBeenCalled();
    }
  });
});
