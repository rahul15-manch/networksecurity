import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AnalysisPanel } from '../components/AnalysisPanel';
import { PRESETS } from '../types';

describe('AnalysisPanel Component', () => {
  const mockSetFeatures = vi.fn();
  const mockOnAnalyze = vi.fn();
  const mockOnSelectPreset = vi.fn();

  it('renders all 30 feature controls and presets', () => {
    render(
      <AnalysisPanel
        features={PRESETS.phishing.features}
        setFeatures={mockSetFeatures}
        onAnalyze={mockOnAnalyze}
        isLoading={false}
        onSelectPreset={mockOnSelectPreset}
      />
    );

    expect(screen.getByText(/Benchmark Vector Presets/i)).toBeInTheDocument();
    expect(screen.getByText(/Credential Harvester/i)).toBeInTheDocument();
    expect(screen.getByText(/Enterprise Banking Portal/i)).toBeInTheDocument();
    expect(screen.getByText(/IP Address in URL/i)).toBeInTheDocument();
    expect(screen.getByText(/SSL \/ TLS Certificate State/i)).toBeInTheDocument();
  });

  it('triggers preset selection when clicking preset card', () => {
    render(
      <AnalysisPanel
        features={PRESETS.phishing.features}
        setFeatures={mockSetFeatures}
        onAnalyze={mockOnAnalyze}
        isLoading={false}
        onSelectPreset={mockOnSelectPreset}
      />
    );

    const legitBtn = screen.getByText(/Enterprise Banking Portal/i).closest('button');
    expect(legitBtn).not.toBeNull();
    fireEvent.click(legitBtn!);
    expect(mockOnSelectPreset).toHaveBeenCalledWith(PRESETS.legitimate.features);
  });

  it('prevents duplicate submissions when loading is in progress', () => {
    render(
      <AnalysisPanel
        features={PRESETS.phishing.features}
        setFeatures={mockSetFeatures}
        onAnalyze={mockOnAnalyze}
        isLoading={true}
        onSelectPreset={mockOnSelectPreset}
      />
    );

    const analyzeBtns = screen.getAllByRole('button', { name: /Analyzing/i });
    expect(analyzeBtns.length).toBeGreaterThan(0);
    for (const btn of analyzeBtns) {
      expect(btn).toBeDisabled();
    }
  });

  it('allows category filtering of features', () => {
    render(
      <AnalysisPanel
        features={PRESETS.phishing.features}
        setFeatures={mockSetFeatures}
        onAnalyze={mockOnAnalyze}
        isLoading={false}
        onSelectPreset={mockOnSelectPreset}
      />
    );

    const sslFilterBtn = screen.getByRole('button', { name: 'Security & SSL' });
    fireEvent.click(sslFilterBtn);

    // SSL feature should be present
    expect(screen.getByText(/SSL \/ TLS Certificate State/i)).toBeInTheDocument();
    // Non-SSL feature like IP Address in URL should be filtered out
    expect(screen.queryByText(/IP Address in URL/i)).not.toBeInTheDocument();
  });
});
