import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
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

  it('renders analysis results when data is loaded', async () => {
    getAnalysis.mockResolvedValue({
      overall_score: 75,
      lever: { primary_lever: 'skin_texture', reason: 'Skin needs work' },
      face: { overall_face_score: 80 },
      body: { v_taper_score: 70 },
      skin: { score: 75 },
      hair: { score: 80 },
      photos_analyzed: 3,
    });
    render(<AnalysisResults />);
    expect(await screen.findByText(/Look Score/i)).toBeInTheDocument();
  });

  it('renders upload prompt when no photos analyzed', async () => {
    getAnalysis.mockResolvedValue({
      photos_analyzed: 0,
    });
    render(<AnalysisResults />);
    expect(await screen.findByText(/upload all 3 photos/i)).toBeInTheDocument();
  });
});
