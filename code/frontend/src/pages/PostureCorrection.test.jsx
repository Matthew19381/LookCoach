import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import PostureCorrection from './PostureCorrection';

// Mock the API client
vi.mock('../api/client', () => ({
  getPostureIssues: vi.fn(),
  getCorrectionPlan: vi.fn(),
  getPostureAssessment: vi.fn(),
}));

import { getPostureIssues, getCorrectionPlan, getPostureAssessment } from '../api/client';

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

  it('assesses posture from the latest real analysis, not a mock', async () => {
    getPostureIssues.mockResolvedValue([]);
    getPostureAssessment.mockResolvedValue({
      has_analysis: true,
      issues_detected: 1,
      issues: [{ name: 'Forward Head', description: 'Head too forward' }],
      daily_habits: ['Chin tucks'],
    });
    render(<PostureCorrection />);
    fireEvent.click(await screen.findByText(/Oceń postawę/i));
    expect(getPostureAssessment).toHaveBeenCalledWith();
    expect(await screen.findByText('Forward Head')).toBeInTheDocument();
  });

  it('asks for a side photo when there is no analysis', async () => {
    getPostureIssues.mockResolvedValue([]);
    getPostureAssessment.mockResolvedValue({ has_analysis: false, message: 'Brak analizy zdjęcia z boku' });
    render(<PostureCorrection />);
    fireEvent.click(await screen.findByText(/Oceń postawę/i));
    expect(await screen.findByText('Brak analizy zdjęcia z boku')).toBeInTheDocument();
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
