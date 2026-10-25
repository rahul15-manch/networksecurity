import React from 'react';
import { ShieldCheck, AlertOctagon, Terminal, ArrowDown } from 'lucide-react';
import { PRESETS } from '../types';
import type { PhishingFeatures } from '../types';

interface HeroProps {
  onSelectPreset: (features: PhishingFeatures) => void;
  onScrollToAnalyzer: () => void;
}

export const Hero: React.FC<HeroProps> = ({ onSelectPreset, onScrollToAnalyzer }) => {
  return (
    <section className="relative overflow-hidden pt-12 pb-10 border-b border-[#303030] radar-sweep cyber-grid">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
        {/* Threat Level Badge */}
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-[#171717] border border-[#DC2626]/40 shadow-glow-red mb-6">
          <span className="flex h-2 w-2 rounded-full bg-[#DC2626] animate-ping" />
          <span className="text-xs font-mono font-medium text-[#F5F5F5]">
            Phishing Detection Layer Active
          </span>
          <span className="text-[10px] text-[#A3A3A3] font-mono">v1.0.0</span>
        </div>

        {/* Main Headline */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-[#F5F5F5] max-w-4xl mx-auto leading-tight">
          Enterprise Domain & Phishing <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#DC2626] via-[#EF4444] to-[#991B1B]">
            Threat Classification
          </span>
        </h1>

        <p className="mt-4 text-base sm:text-lg text-[#A3A3A3] max-w-2xl mx-auto leading-relaxed">
          Evaluate 30 high-fidelity lexical, DNS, SSL, and behavioral website attributes using 
          an audited <strong className="text-[#F5F5F5]">Random Forest (n=128)</strong> ensemble model trained on vetted cybersecurity benchmarks.
        </p>

        {/* Action Buttons & Presets */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3 sm:gap-4">
          <button
            onClick={() => onSelectPreset(PRESETS.phishing.features)}
            className="flex items-center space-x-2 px-5 py-3 rounded-lg bg-[#DC2626] hover:bg-[#EF4444] text-white font-medium text-sm transition-all shadow-glow-red hover:shadow-glow-red-lg active:scale-95"
          >
            <AlertOctagon className="w-4 h-4" />
            <span>Load Phishing Sample</span>
          </button>

          <button
            onClick={() => onSelectPreset(PRESETS.legitimate.features)}
            className="flex items-center space-x-2 px-5 py-3 rounded-lg bg-[#171717] hover:bg-[#202020] text-[#F5F5F5] border border-[#303030] hover:border-[#DC2626]/60 font-medium text-sm transition-all active:scale-95"
          >
            <ShieldCheck className="w-4 h-4 text-[#10B981]" />
            <span>Load Legitimate Sample</span>
          </button>

          <button
            onClick={onScrollToAnalyzer}
            className="flex items-center space-x-2 px-4 py-3 rounded-lg bg-[#111111] hover:bg-[#171717] text-[#A3A3A3] hover:text-[#F5F5F5] border border-[#303030] text-sm font-medium transition-all"
          >
            <span>Custom Vectors</span>
            <ArrowDown className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Transparent Architecture Disclaimer Callout */}
        <div className="mt-8 max-w-2xl mx-auto p-3 rounded-lg bg-[#111111]/90 border border-[#303030] flex items-center justify-center space-x-2 text-xs text-[#A3A3A3]">
          <Terminal className="w-4 h-4 text-[#DC2626] flex-shrink-0" />
          <span>
            <strong className="text-[#F5F5F5]">Model Input Contract:</strong> The inference service evaluates 30 discrete engineered features. Raw URLs are not scraped or visited over the network.
          </span>
        </div>
      </div>
    </section>
  );
};
