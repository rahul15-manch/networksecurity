import React, { useState } from 'react';
import {
  Play,
  RotateCcw,
  Sliders,
  Globe,
  AlertCircle,
  Search,
  Cpu
} from 'lucide-react';
import {
  FEATURE_METADATA,
  PRESETS
} from '../types';
import type {
  PhishingFeatures,
  FeatureMeta
} from '../types';

interface AnalysisPanelProps {
  features: PhishingFeatures;
  setFeatures: React.Dispatch<React.SetStateAction<PhishingFeatures>>;
  onAnalyzeVector: () => void;
  onAnalyzeUrl: (url: string, allowHeuristics: boolean) => void;
  isLoading: boolean;
  onSelectPreset: (features: PhishingFeatures) => void;
  urlInput: string;
  setUrlInput: (url: string) => void;
  allowHeuristics: boolean;
  setAllowHeuristics: (allow: boolean) => void;
}

type CategoryFilter = 'All' | 'Lexical & URL' | 'Security & SSL' | 'Domain & DNS' | 'Page Content & Scripting';

const QUICK_URL_SAMPLES = [
  { label: 'Legitimate (Google)', url: 'https://www.google.com', meaning: 'legit' },
  { label: 'Phishing Credential Harvester', url: 'http://apple-id-verify.secure-update-login.com/auth', meaning: 'phish' },
  { label: 'Shortener (bit.ly)', url: 'http://bit.ly/security-test-sample', meaning: 'phish' },
];

export const AnalysisPanel: React.FC<AnalysisPanelProps> = ({
  features,
  setFeatures,
  onAnalyzeVector,
  onAnalyzeUrl,
  isLoading,
  onSelectPreset,
  urlInput,
  setUrlInput,
  allowHeuristics,
  setAllowHeuristics,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<CategoryFilter>('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [urlValidationError, setUrlValidationError] = useState<string | null>(null);

  const filteredFeatures = FEATURE_METADATA.filter((item: FeatureMeta) => {
    const matchesCategory = selectedCategory === 'All' || item.category === selectedCategory;
    const matchesQuery =
      item.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
      String(item.key).toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesQuery;
  });

  const handleFeatureChange = (key: keyof PhishingFeatures, value: number) => {
    setFeatures(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleUrlInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setUrlInput(val);

    // Client-side quick syntax guidance
    if (val && !val.startsWith('http://') && !val.startsWith('https://')) {
      setUrlValidationError('URL must start with http:// or https://');
    } else if (val.includes('localhost') || val.includes('127.0.0.1')) {
      setUrlValidationError('Localhost and private IP addresses are blocked by SSRF protections.');
    } else {
      setUrlValidationError(null);
    }
  };

  const handleTriggerUrlAnalysis = () => {
    if (!urlInput.trim()) {
      setUrlValidationError('Please enter a target URL to analyze.');
      return;
    }
    setUrlValidationError(null);
    onAnalyzeUrl(urlInput.trim(), allowHeuristics);
  };

  const handleReset = () => {
    onSelectPreset(PRESETS.phishing.features);
  };

  return (
    <div id="analyzer" className="space-y-6">
      {/* Live URL Prediction Section */}
      <div className="p-5 rounded-xl bg-[#171717] border border-[#303030] shadow-card-dark">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2 text-xs font-mono text-[#DC2626] uppercase font-bold tracking-wider">
            <Globe className="w-4 h-4" />
            <span>End-to-End URL Phishing Classifier</span>
          </div>
          <span className="text-[11px] font-mono text-[#A3A3A3] bg-[#111111] px-2 py-0.5 rounded border border-[#303030]">
            SSRF Defended &bull; Live DOM Probing
          </span>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <input
              type="text"
              value={urlInput}
              onChange={handleUrlInputChange}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleTriggerUrlAnalysis();
              }}
              placeholder="e.g. https://secure-login.bank-account.com/auth"
              className={`w-full px-4 py-2.5 rounded-lg bg-[#090909] border text-[#F5F5F5] placeholder-[#737373] text-sm font-mono focus:outline-none focus:ring-2 focus:ring-[#DC2626] focus:border-transparent transition-all ${
                urlValidationError ? 'border-[#DC2626]' : 'border-[#303030]'
              }`}
            />
          </div>
          <button
            type="button"
            onClick={handleTriggerUrlAnalysis}
            disabled={isLoading}
            className="flex items-center justify-center space-x-2 px-6 py-2.5 rounded-lg bg-[#DC2626] hover:bg-[#EF4444] disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm transition-all shadow-glow-red hover:shadow-glow-red-lg active:scale-95 flex-shrink-0"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Extracting Features...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Analyze Live URL</span>
              </>
            )}
          </button>
        </div>

        {/* Validation Error Message */}
        {urlValidationError && (
          <p className="mt-2 text-xs text-[#EF4444] font-mono flex items-center space-x-1">
            <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
            <span>{urlValidationError}</span>
          </p>
        )}

        {/* Heuristic Toggle & Sample Presets Bar */}
        <div className="mt-4 pt-3 border-t border-[#303030]/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <label className="flex items-center space-x-2 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={allowHeuristics}
              onChange={(e) => setAllowHeuristics(e.target.checked)}
              className="w-4 h-4 rounded bg-[#090909] border-[#303030] text-[#DC2626] focus:ring-[#DC2626] focus:ring-offset-0 focus:ring-1"
            />
            <span className="text-[#A3A3A3] font-mono">
              Apply Documented Baseline Defaults for Retired Services <span className="text-[#737373]">(Alexa, PageRank)</span>
            </span>
          </label>

          {/* Quick URL samples */}
          <div className="flex flex-wrap items-center gap-1.5 font-mono text-[11px]">
            <span className="text-[#737373]">Samples:</span>
            {QUICK_URL_SAMPLES.map((sample) => (
              <button
                key={sample.label}
                type="button"
                onClick={() => {
                  setUrlInput(sample.url);
                  setUrlValidationError(null);
                }}
                className={`px-2 py-1 rounded border transition-colors ${
                  sample.meaning === 'legit'
                    ? 'bg-[#111111] hover:bg-[#171717] text-[#10B981] border-[#10B981]/30'
                    : 'bg-[#111111] hover:bg-[#171717] text-[#EF4444] border-[#DC2626]/30'
                }`}
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Manual 30-Feature Inspection & Fine-Tuning Panel */}
      <div className="p-5 rounded-xl bg-[#171717] border border-[#303030] shadow-card-dark space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center space-x-2 text-xs font-mono text-[#A3A3A3] uppercase font-bold tracking-wider">
              <Sliders className="w-4 h-4 text-[#DC2626]" />
              <span>Engineered 30-Feature Inspection Vector</span>
            </div>
            <p className="text-xs text-[#737373] mt-0.5">
              Features extracted from URLs or loaded via presets populate the inputs below for auditing.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              type="button"
              onClick={handleReset}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#111111] hover:bg-[#202020] text-[#A3A3A3] hover:text-[#F5F5F5] border border-[#303030] text-xs font-mono transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Defaults</span>
            </button>

            <button
              type="button"
              onClick={onAnalyzeVector}
              disabled={isLoading}
              className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-[#202020] hover:bg-[#303030] text-[#F5F5F5] border border-[#303030] hover:border-[#DC2626]/60 text-xs font-mono transition-colors active:scale-95"
            >
              <Cpu className="w-3.5 h-3.5 text-[#DC2626]" />
              <span>Evaluate Vector</span>
            </button>
          </div>
        </div>

        {/* Filter Tabs & Search */}
        <div className="flex flex-col sm:flex-row gap-3 pt-2">
          <div className="flex-1 flex flex-wrap gap-1.5">
            {(['All', 'Lexical & URL', 'Security & SSL', 'Domain & DNS', 'Page Content & Scripting'] as CategoryFilter[]).map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1 rounded-md text-xs font-mono transition-all ${
                  selectedCategory === cat
                    ? 'bg-[#DC2626] text-white font-semibold shadow-glow-red'
                    : 'bg-[#111111] text-[#A3A3A3] hover:text-[#F5F5F5] border border-[#303030]'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          <div className="relative w-full sm:w-56">
            <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-[#737373]" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search features..."
              className="w-full pl-8 pr-3 py-1.5 rounded-md bg-[#090909] border border-[#303030] text-xs text-[#F5F5F5] placeholder-[#737373] font-mono focus:outline-none focus:ring-1 focus:ring-[#DC2626]"
            />
          </div>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 max-h-[500px] overflow-y-auto pr-1">
          {filteredFeatures.map((item) => {
            const currentValue = features[item.key] ?? 1;
            return (
              <div
                key={String(item.key)}
                className="p-3 rounded-lg bg-[#111111] border border-[#303030] hover:border-[#404040] transition-colors"
              >
                <div className="flex justify-between items-start gap-2">
                  <div>
                    <span className="text-xs font-semibold text-[#F5F5F5] block font-mono">
                      {item.label}
                    </span>
                    <span className="text-[11px] text-[#737373] font-mono block mt-0.5">
                      {String(item.key)}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#202020] text-[#A3A3A3] border border-[#303030]">
                    Val: {currentValue}
                  </span>
                </div>

                <p className="text-[11px] text-[#A3A3A3] mt-1.5 leading-snug">
                  {item.description}
                </p>

                {/* Value Buttons */}
                <div className="mt-2.5 flex items-center gap-1.5">
                  {item.options.map((opt) => (
                    <button
                      key={opt.value}
                      type="button"
                      onClick={() => handleFeatureChange(item.key, opt.value)}
                      className={`flex-1 py-1 px-1.5 rounded text-[11px] font-mono transition-all text-center ${
                        currentValue === opt.value
                          ? opt.meaning === 'phishing'
                            ? 'bg-[#DC2626] text-white font-bold shadow-glow-red'
                            : opt.meaning === 'suspicious'
                            ? 'bg-[#F59E0B] text-black font-bold'
                            : 'bg-[#10B981] text-white font-bold'
                          : 'bg-[#202020] text-[#A3A3A3] hover:text-[#F5F5F5] hover:bg-[#282828]'
                      }`}
                    >
                      {opt.value > 0 ? `+${opt.value}` : opt.value}
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
