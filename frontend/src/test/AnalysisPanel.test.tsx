import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AnalysisPanel } from '../components/AnalysisPanel';
import { PRESETS } from '../types';

describe('AnalysisPanel Component', () => {
  const mockSetFeatures = vi.fn();
  const mockOnAnalyzeVector = vi.fn();
  const mockOnAnalyzeUrl = vi.fn();
  const mockOnSelectPreset = vi.fn();
  const mockSetUrlInput = vi.fn();
  const mockSetAllowHeuristics = vi.fn();

  it('renders URL input bar and 30 feature controls', () => {
    render(
      <AnalysisPanel
        features={PRESETS.phishing.features}
        setFeatures={mockSetFeatures}
        onAnalyzeVector={mockOnAnalyzeVector}
        onAnalyzeUrl={mockOnAnalyzeUrl}
        isLoading={false}
        onSelectPreset={mockOnSelectPreset}
        urlInput="https://example.com"
        setUrlInput={mockSetUrlInput}
        allowHeuristics={true}
        setAllowHeuristics={mockSetAllowHeuristics}
      />
    );

    expect(screen.getByText(/End-to-End URL Phishing Classifier/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Analyze Live URL/i })).toBeInTheDocument();
    expect(screen.getByText(/IP Address in URL/i)).toBeInTheDocument();
    expect(screen.getByText(/Apply Documented Baseline Defaults/i)).toBeInTheDocument();
  });

  it('triggers onAnalyzeUrl when clicking Analyze Live URL', () => {
    render(
      <AnalysisPanel
        features={PRESETS.phishing.features}
        setFeatures={mockSetFeatures}
        onAnalyzeVector={mockOnAnalyzeVector}
        onAnalyzeUrl={mockOnAnalyzeUrl}
        isLoading={false}
        onSelectPreset={mockOnSelectPreset}
        urlInput="https://paypal-update.com/login"
        setUrlInput={mockSetUrlInput}
        allowHeuristics={true}
        setAllowHeuristics={mockSetAllowHeuristics}
      />
    );

    const analyzeBtn = screen.getByRole('button', { name: /Analyze Live URL/i });
    fireEvent.click(analyzeBtn);
    expect(mockOnAnalyzeUrl).toHaveBeenCalledWith('https://paypal-update.com/login', true);
  });

  it('triggers onAnalyzeVector when clicking Evaluate Vector', () => {
    render(
      <AnalysisPanel
        features={PRESETS.phishing.features}
        setFeatures={mockSetFeatures}
        onAnalyzeVector={mockOnAnalyzeVector}
        onAnalyzeUrl={mockOnAnalyzeUrl}
        isLoading={false}
        onSelectPreset={mockOnSelectPreset}
        urlInput="https://example.com"
        setUrlInput={mockSetUrlInput}
        allowHeuristics={true}
        setAllowHeuristics={mockSetAllowHeuristics}
      />
    );

    const vectorBtn = screen.getByRole('button', { name: /Evaluate Vector/i });
    fireEvent.click(vectorBtn);
    expect(mockOnAnalyzeVector).toHaveBeenCalled();
  });

  it('disables analyze button when loading is true', () => {
    render(
      <AnalysisPanel
        features={PRESETS.phishing.features}
        setFeatures={mockSetFeatures}
        onAnalyzeVector={mockOnAnalyzeVector}
        onAnalyzeUrl={mockOnAnalyzeUrl}
        isLoading={true}
        onSelectPreset={mockOnSelectPreset}
        urlInput="https://example.com"
        setUrlInput={mockSetUrlInput}
        allowHeuristics={true}
        setAllowHeuristics={mockSetAllowHeuristics}
      />
    );

    const loadingBtn = screen.getByRole('button', { name: /Extracting Features/i });
    expect(loadingBtn).toBeDisabled();
  });

  it('allows category filtering of features', () => {
    render(
      <AnalysisPanel
        features={PRESETS.phishing.features}
        setFeatures={mockSetFeatures}
        onAnalyzeVector={mockOnAnalyzeVector}
        onAnalyzeUrl={mockOnAnalyzeUrl}
        isLoading={false}
        onSelectPreset={mockOnSelectPreset}
        urlInput="https://example.com"
        setUrlInput={mockSetUrlInput}
        allowHeuristics={true}
        setAllowHeuristics={mockSetAllowHeuristics}
      />
    );

    const sslFilterBtn = screen.getByRole('button', { name: 'Security & SSL' });
    fireEvent.click(sslFilterBtn);

    expect(screen.getByText(/SSL \/ TLS Certificate State/i)).toBeInTheDocument();
    expect(screen.queryByText(/IP Address in URL/i)).not.toBeInTheDocument();
  });
});
