import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ResultCard } from '../components/ResultCard';
import type { UnifiedResult } from '../types';

describe('ResultCard Component', () => {
  it('renders loading state when inference is in progress', () => {
    render(<ResultCard result={null} isLoading={true} error={null} />);
    expect(screen.getByText(/Executing Feature Pipeline & Inference/i)).toBeInTheDocument();
  });

  it('renders error message when API call fails', () => {
    const errorMsg = 'Model artifact not available on server';
    render(<ResultCard result={null} isLoading={false} error={errorMsg} />);
    expect(screen.getByText(/Analysis Request Failed/i)).toBeInTheDocument();
    expect(screen.getByText(errorMsg)).toBeInTheDocument();
  });

  it('renders idle placeholder when no prediction is available yet', () => {
    render(<ResultCard result={null} isLoading={false} error={null} />);
    expect(screen.getByText(/No Prediction Generated Yet/i)).toBeInTheDocument();
  });

  it('renders incomplete feature vector warning and enable button in strict mode', () => {
    const mockIncompleteResult: UnifiedResult = {
      status: 'unsupported_features',
      url: 'https://example.com',
      prediction: null,
      class_id: null,
      model_score: null,
      feature_coverage: 'incomplete',
      extracted_count: 23,
      total_expected: 30,
      features: {},
      stages: {},
      unsupported_features: ['web_traffic', 'Page_Rank', 'Google_Index'],
      warnings: [],
    };
    const mockEnableHeuristics = vi.fn();

    render(
      <ResultCard
        result={mockIncompleteResult}
        isLoading={false}
        error={null}
        onEnableHeuristics={mockEnableHeuristics}
      />
    );

    expect(screen.getByText(/Strict Mode Halted: 7 Features Require External Baseline/i)).toBeInTheDocument();
    expect(screen.getByText('web_traffic')).toBeInTheDocument();
    expect(screen.getByText('Page_Rank')).toBeInTheDocument();

    const enableBtn = screen.getByRole('button', { name: /Enable Baseline Heuristics/i });
    fireEvent.click(enableBtn);
    expect(mockEnableHeuristics).toHaveBeenCalled();
  });

  it('renders phishing detection outcome with red accents, high risk, and class_id 0', () => {
    const mockPhishingResult: UnifiedResult = {
      status: 'success',
      url: 'http://apple-verify.evil.com',
      prediction: 'phishing',
      class_id: 0,
      model_score: 0.035, // 3.5% legitimate => 96.5% phishing risk
      feature_coverage: 'heuristic',
      extracted_count: 30,
      total_expected: 30,
      features: {},
      stages: {
        url_lexical: { status: 'success', count: 10, details: '10 lexical features extracted' },
      },
      unsupported_features: [],
      warnings: [],
    };

    render(<ResultCard result={mockPhishingResult} isLoading={false} error={null} />);

    expect(screen.getByText(/Phishing Malicious Signature/i)).toBeInTheDocument();
    expect(screen.getByText(/Class ID: 0/i)).toBeInTheDocument();
    expect(screen.getByText(/HIGH RISK/i)).toBeInTheDocument();
    expect(screen.getByText(/Phishing Risk: 96.5%/i)).toBeInTheDocument();
    expect(screen.getByText(/Target:/i)).toBeInTheDocument();
    expect(screen.getByText('http://apple-verify.evil.com')).toBeInTheDocument();
    expect(screen.getByText(/Heuristic Baseline/i)).toBeInTheDocument();
  });

  it('renders legitimate website outcome with green accents, low risk, and class_id 1', () => {
    const mockLegitResult: UnifiedResult = {
      status: 'success',
      url: 'https://www.google.com',
      prediction: 'legitimate',
      class_id: 1,
      model_score: 0.942, // 94.2% legitimate
      feature_coverage: 'complete',
      extracted_count: 30,
      total_expected: 30,
      features: {},
      stages: {},
      unsupported_features: [],
      warnings: [],
    };

    render(<ResultCard result={mockLegitResult} isLoading={false} error={null} />);

    expect(screen.getByText(/Legitimate Safe Signature/i)).toBeInTheDocument();
    expect(screen.getByText(/Class ID: 1/i)).toBeInTheDocument();
    expect(screen.getByText(/LOW RISK/i)).toBeInTheDocument();
    expect(screen.getByText(/Legitimate: 94.2%/i)).toBeInTheDocument();
    expect(screen.getByText(/100% Complete/i)).toBeInTheDocument();
  });

  it('renders uncertain suspicious risk badge and notice for suspicious sites in heuristic mode', () => {
    const mockUncertainResult: UnifiedResult = {
      status: 'uncertain',
      url: 'https://testsafebrowsing.appspot.com/s/phishing.html',
      prediction: 'uncertain',
      class_id: 1,
      model_score: 0.78,
      risk_tier: 'SUSPICIOUS / UNVERIFIED',
      feature_coverage: 'heuristic',
      is_heuristic: true,
      observed_count: 19,
      estimated_count: 11,
      missing_count: 0,
      extracted_count: 30,
      total_expected: 30,
      features: {},
      stages: {},
      unsupported_features: [],
      warnings: ['Missing, empty, or external form action (SFH) with credential inputs detected.'],
      message: 'Suspicious indicator(s) detected while external reputation features were imputed with neutral defaults.',
    };

    render(<ResultCard result={mockUncertainResult} isLoading={false} error={null} />);

    expect(screen.getByText(/Uncertain \/ Suspicious Risk Detected/i)).toBeInTheDocument();
    expect(screen.getByText(/SUSPICIOUS \/ UNVERIFIED/i)).toBeInTheDocument();
    expect(screen.getByText(/19/i)).toBeInTheDocument();
    expect(screen.getByText(/11/i)).toBeInTheDocument();
    expect(screen.queryByText(/Legitimate Safe Signature/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/LOW RISK/i)).not.toBeInTheDocument();
  });

  it('renders estimated legitimate without green safe signature when heuristic mode is used', () => {
    const mockHeuristicLegit: UnifiedResult = {
      status: 'success',
      url: 'https://example.com',
      prediction: 'legitimate',
      class_id: 1,
      model_score: 0.92,
      risk_tier: 'ESTIMATED (UNVERIFIED REPUTATION)',
      feature_coverage: 'heuristic',
      is_heuristic: true,
      observed_count: 23,
      estimated_count: 7,
      missing_count: 0,
      extracted_count: 30,
      total_expected: 30,
      features: {},
      stages: {},
      unsupported_features: [],
      warnings: [],
      message: 'Classified as legitimate based on URL and page characteristics, but external reputation metrics use estimated neutral baselines.',
    };

    render(<ResultCard result={mockHeuristicLegit} isLoading={false} error={null} />);

    expect(screen.getByText(/Estimated Legitimate \(Heuristic Baseline\)/i)).toBeInTheDocument();
    expect(screen.getByText(/ESTIMATED \(UNVERIFIED REPUTATION\)/i)).toBeInTheDocument();
    expect(screen.queryByText(/Legitimate Safe Signature/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/^LOW RISK$/i)).not.toBeInTheDocument();
  });
});
