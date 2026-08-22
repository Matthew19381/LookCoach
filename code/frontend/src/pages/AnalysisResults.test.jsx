import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import AnalysisResults from './AnalysisResults';

// Mock the API client
vi.mock('../api/client', () => ({
  getAnalysis: vi.fn(),
}));

import { getAnalysis } from '../api/client';

describe('AnalysisResults', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders qualitative observations instead of numeric scores', async () => {
    getAnalysis.mockResolvedValue({
      lever: { primary_lever: 'skin_texture', reason: 'Skin needs work' },
      face: {
        observations: ['mild puffiness in cheeks'],
        swelling: { level: 'medium', areas: ['cheeks'] },
        focus_areas: [{ area: 'skincare', priority: 'medium', reason: 'hydration' }],
      },
      body: { observations: [], posture_notes: [] },
      skin: { skin_type: 'combination', problems: [] },
      hair: { density_status: 'normal' },
      photos_analyzed: 3,
    });
    render(<AnalysisResults />);
    expect(
      await screen.findByRole('heading', { name: /Observations/i })
    ).toBeInTheDocument();
    expect(screen.getAllByText(/mild puffiness in cheeks/i).length).toBeGreaterThan(0);
    // No numeric person rating may be rendered
    expect(screen.queryByText(/Look Score/i)).not.toBeInTheDocument();
  });

  it('renders upload prompt when no photos analyzed', async () => {
    getAnalysis.mockResolvedValue({
      photos_analyzed: 0,
    });
    render(<AnalysisResults />);
    expect(await screen.findByText(/upload all 3 photos/i)).toBeInTheDocument();
  });
});
