import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ResultCard } from '../components/ResultCard';
import type { PredictionResponse } from '../types';

describe('ResultCard Component', () => {
  it('renders loading state when inference is in progress', () => {
    render(<ResultCard result={null} isLoading={true} error={null} />);
    expect(screen.getByText(/Executing Random Forest Inference/i)).toBeInTheDocument();
  });

  it('renders error message when API call fails', () => {
    const errorMsg = 'Model artifact not available on server';
    render(<ResultCard result={null} isLoading={false} error={errorMsg} />);
    expect(screen.getByText(/Inference Request Failed/i)).toBeInTheDocument();
    expect(screen.getByText(errorMsg)).toBeInTheDocument();
  });

  it('renders idle placeholder when no prediction is available yet', () => {
    render(<ResultCard result={null} isLoading={false} error={null} />);
    expect(screen.getByText(/No Prediction Generated Yet/i)).toBeInTheDocument();
  });

  it('renders phishing detection outcome with red accents, high risk, and class_id 0', () => {
    const mockPhishingResult: PredictionResponse = {
      prediction: 'phishing',
      class_id: 0,
      model_score: 0.035, // 3.5% legitimate => 96.5% phishing risk
    };

    render(<ResultCard result={mockPhishingResult} isLoading={false} error={null} />);

    expect(screen.getByText(/Phishing Malicious Signature/i)).toBeInTheDocument();
    expect(screen.getByText(/Class ID: 0/i)).toBeInTheDocument();
    expect(screen.getByText(/HIGH RISK/i)).toBeInTheDocument();
    expect(screen.getByText(/Phishing Risk: 96.5%/i)).toBeInTheDocument();
    expect(screen.getByText(/Security Notice:/i)).toBeInTheDocument();
  });

  it('renders legitimate website outcome with green accents, low risk, and class_id 1', () => {
    const mockLegitResult: PredictionResponse = {
      prediction: 'legitimate',
      class_id: 1,
      model_score: 0.942, // 94.2% legitimate
    };

    render(<ResultCard result={mockLegitResult} isLoading={false} error={null} />);

    expect(screen.getByText(/Legitimate Safe Signature/i)).toBeInTheDocument();
    expect(screen.getByText(/Class ID: 1/i)).toBeInTheDocument();
    expect(screen.getByText(/LOW RISK/i)).toBeInTheDocument();
    expect(screen.getByText(/Legitimate: 94.2%/i)).toBeInTheDocument();
    expect(screen.getByText(/Security Notice:/i)).toBeInTheDocument();
  });
});
