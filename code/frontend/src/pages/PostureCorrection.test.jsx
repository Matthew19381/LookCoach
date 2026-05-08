import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import PostureCorrection from './PostureCorrection';

// Mock the API client
vi.mock('../api/client', () => ({
  getPostureIssues: vi.fn(),
  detectPostureIssues: vi.fn(),
  getCorrectionPlan: vi.fn(),
  fullPostureAssessment: vi.fn(),
}));

import { getPostureIssues, detectPostureIssues, getCorrectionPlan } from '../api/client';

describe('PostureCorrection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders posture correction title', async () => {
    getPostureIssues.mockResolvedValue([
      { id: 'forward_head', name: 'Forward Head', description: 'Head too forward', looks_impact: 'Medium' },
    ]);
    render(<PostureCorrection />);
    expect(await screen.findByText(/Posture Correction/i)).toBeInTheDocument();
  });

  it('loads and displays posture issues', async () => {
    getPostureIssues.mockResolvedValue([
      { id: 'forward_head', name: 'Forward Head', description: 'Head too forward', looks_impact: 'Medium' },
      { id: 'rounded_shoulders', name: 'Rounded Shoulders', description: 'Shoulders rounded', looks_impact: 'High' },
    ]);
    render(<PostureCorrection />);
    expect(await screen.findByText(/Forward Head/i)).toBeInTheDocument();
    expect(screen.getByText(/Rounded Shoulders/i)).toBeInTheDocument();
  });

  it('detects issues on button click', async () => {
    getPostureIssues.mockResolvedValue([]);
    detectPostureIssues.mockResolvedValue({
      issues_detected: 2,
      issues: [
        { name: 'Forward Head', description: 'Head too forward' },
        { name: 'Rounded Shoulders', description: 'Shoulders rounded' },
      ],
      daily_habits: ['Chin tucks', 'Wall angels'],
    });
    render(<PostureCorrection />);
    const detectBtn = await screen.findByText(/Detect Issues/i);
    fireEvent.click(detectBtn);
    expect(detectPostureIssues).toHaveBeenCalled();
  });

  it('gets correction plan for an issue', async () => {
    getPostureIssues.mockResolvedValue([
      { id: 'forward_head', name: 'Forward Head', description: 'Head too forward' },
    ]);
    getCorrectionPlan.mockResolvedValue({
      issue: 'Forward Head',
      corrections: [
        { exercise: 'Chin tucks', sets: '3x10', focus: 'neck' },
      ],
    });
    render(<PostureCorrection />);
    const getPlanBtn = await screen.findByText(/Get Correction Plan/i);
    fireEvent.click(getPlanBtn);
    expect(getCorrectionPlan).toHaveBeenCalled();
  });
});
