import React, { useState } from 'react';
import { 
  Play, 
  RotateCcw, 
  Sliders, 
  Globe, 
  AlertCircle 
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
  onAnalyze: () => void;
  isLoading: boolean;
  onSelectPreset: (features: PhishingFeatures) => void;
}

type CategoryFilter = 'All' | 'Lexical & URL' | 'Security & SSL' | 'Domain & DNS' | 'Page Content & Scripting';

export const AnalysisPanel: React.FC<AnalysisPanelProps> = ({
  features,
  setFeatures,
  onAnalyze,
  isLoading,
  onSelectPreset,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<CategoryFilter>('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [demoUrl, setDemoUrl] = useState('https://secure-login.apple-account-verification.com/auth');

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

  const handleReset = () => {
    onSelectPreset(PRESETS.phishing.features);
  };

  // Helper to sync demo URL string to prompt appropriate presets
  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setDemoUrl(val);
    if (val.toLowerCase().includes('phish') || val.toLowerCase().includes('verify') || val.toLowerCase().includes('update-account')) {
      onSelectPreset(PRESETS.phishing.features);
    } else if (val.toLowerCase().includes('google') || val.toLowerCase().includes('github') || val.toLowerCase().includes('apple.com')) {
      onSelectPreset(PRESETS.legitimate.features);
    }
  };

  return (
    <div id="analyzer" className="space-y-6">
      {/* URL Input & Contract Explanation Banner */}
      <div className="p-5 rounded-xl bg-[#171717] border border-[#303030]">
        <div className="flex items-center space-x-2 text-xs font-mono text-[#DC2626] uppercase font-bold tracking-wider mb-2">
          <Globe className="w-4 h-4" />
          <span>Domain URL Context & Architecture Notice</span>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <input
              type="text"
              value={demoUrl}
              onChange={handleUrlChange}
              placeholder="e.g. https://example-verification.com/login"
              className="w-full px-4 py-2.5 rounded-lg bg-[#090909] border border-[#303030] text-[#F5F5F5] placeholder-[#737373] text-sm font-mono focus:outline-none focus:ring-2 focus:ring-[#DC2626] focus:border-transparent transition-all"
            />
          </div>
          <button
            type="button"
            onClick={onAnalyze}
            disabled={isLoading}
            className="flex items-center justify-center space-x-2 px-6 py-2.5 rounded-lg bg-[#DC2626] hover:bg-[#EF4444] disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm transition-all shadow-glow-red hover:shadow-glow-red-lg active:scale-95"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Analyze Vector</span>
              </>
            )}
          </button>
        </div>

        <div className="mt-3 flex items-start space-x-2 text-xs text-[#A3A3A3] bg-[#111111] p-3 rounded-lg border border-[#303030]/60">
          <AlertCircle className="w-4 h-4 text-[#F59E0B] flex-shrink-0 mt-0.5" />
          <p>
            <strong className="text-[#F5F5F5]">Feature Contract:</strong> The backend model evaluates the 30 structured attributes below. Modifying the URL above demonstrates context; inspect or adjust individual features to observe how each dimension impacts the Random Forest classifier.
          </p>
        </div>
      </div>

      {/* Preset Selectors */}
      <div className="p-5 rounded-xl bg-[#171717] border border-[#303030]">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Sliders className="w-4 h-4 text-[#DC2626]" />
            <span className="text-sm font-bold text-[#F5F5F5]">Benchmark Vector Presets</span>
          </div>
          <span className="text-xs text-[#A3A3A3] font-mono">Quick Template Loader</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {Object.values(PRESETS).map(preset => {
            const isPhish = preset.id === 'phishing';
            const isLegit = preset.id === 'legitimate';
            return (
              <button
                key={preset.id}
                onClick={() => onSelectPreset(preset.features)}
                className={`p-3 rounded-lg border text-left transition-all hover:border-[#DC2626]/80 ${
                  isPhish
                    ? 'bg-[#111111] border-[#DC2626]/40 hover:bg-[#202020]'
                    : isLegit
                    ? 'bg-[#111111] border-[#10B981]/40 hover:bg-[#202020]'
                    : 'bg-[#111111] border-[#303030] hover:bg-[#202020]'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-[#F5F5F5]">{preset.name}</span>
                  <span
                    className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                      isPhish
                        ? 'bg-[#DC2626]/20 text-[#EF4444]'
                        : isLegit
                        ? 'bg-[#10B981]/20 text-[#10B981]'
                        : 'bg-[#303030] text-[#A3A3A3]'
                    }`}
                  >
                    {preset.tag}
                  </span>
                </div>
                <p className="text-[11px] text-[#A3A3A3] line-clamp-2">{preset.description}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Feature Filter Categories */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
        <div className="flex flex-wrap items-center gap-1.5">
          {(['All', 'Lexical & URL', 'Security & SSL', 'Domain & DNS', 'Page Content & Scripting'] as CategoryFilter[]).map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                selectedCategory === cat
                  ? 'bg-[#DC2626] text-white shadow-glow-red'
                  : 'bg-[#171717] text-[#A3A3A3] hover:text-[#F5F5F5] border border-[#303030]'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            placeholder="Search 30 features..."
            className="px-3 py-1.5 rounded-lg bg-[#111111] border border-[#303030] text-xs text-[#F5F5F5] placeholder-[#737373] focus:outline-none focus:ring-1 focus:ring-[#DC2626]"
          />
          <button
            onClick={handleReset}
            title="Reset to default phishing vector"
            className="p-1.5 rounded-lg bg-[#171717] border border-[#303030] text-[#A3A3A3] hover:text-[#F5F5F5]"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 30 Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredFeatures.map(item => {
          const currentValue = features[item.key] ?? item.allowedValues[0];
          return (
            <div
              key={item.key}
              className="p-4 rounded-xl bg-[#171717] border border-[#303030] hover:border-[#404040] transition-colors"
            >
              <div className="flex items-start justify-between mb-1.5">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-semibold text-[#F5F5F5]">{item.label}</span>
                    <span className="text-[10px] font-mono text-[#A3A3A3] bg-[#111111] px-1.5 py-0.5 rounded border border-[#303030]">
                      {item.category}
                    </span>
                  </div>
                  <span className="text-[11px] font-mono text-[#737373] block mt-0.5">{item.key}</span>
                </div>
              </div>

              <p className="text-xs text-[#A3A3A3] mb-3 leading-relaxed">{item.description}</p>

              {/* Discrete Value Buttons */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5">
                {item.options.map(opt => {
                  const isSelected = currentValue === opt.value;
                  const isOptSuspicious = opt.meaning === 'suspicious';
                  const isOptLegit = opt.meaning === 'legitimate';

                  let selectedClasses = 'bg-[#DC2626] text-white border-[#DC2626] shadow-glow-red';
                  if (isOptLegit) selectedClasses = 'bg-[#10B981] text-white border-[#10B981]';
                  if (isOptSuspicious) selectedClasses = 'bg-[#F59E0B] text-black border-[#F59E0B]';

                  return (
                    <button
                      key={opt.value}
                      type="button"
                      onClick={() => handleFeatureChange(item.key, opt.value)}
                      className={`px-2 py-1.5 rounded text-[11px] font-mono border transition-all text-center truncate ${
                        isSelected
                          ? selectedClasses
                          : 'bg-[#111111] text-[#A3A3A3] border-[#303030] hover:bg-[#202020] hover:text-[#F5F5F5]'
                      }`}
                      title={opt.label}
                    >
                      {opt.label.split(':')[0].trim()}
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Floating Bottom Action Bar */}
      <div className="p-4 rounded-xl bg-[#171717] border border-[#DC2626]/40 shadow-glow-red flex items-center justify-between">
        <div>
          <span className="text-sm font-bold text-[#F5F5F5] block">Ready to evaluate 30 features</span>
          <span className="text-xs text-[#A3A3A3] font-mono">Ensemble classifier: RandomForest(n_estimators=128)</span>
        </div>
        <button
          type="button"
          onClick={onAnalyze}
          disabled={isLoading}
          className="flex items-center space-x-2 px-6 py-2.5 rounded-lg bg-[#DC2626] hover:bg-[#EF4444] disabled:opacity-50 text-white font-semibold text-sm transition-all shadow-glow-red active:scale-95"
        >
          {isLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>Execute Inference</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
