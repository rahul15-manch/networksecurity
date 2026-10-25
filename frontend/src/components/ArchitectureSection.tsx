import React from 'react';
import { Layers, AlertTriangle } from 'lucide-react';

export const ArchitectureSection: React.FC = () => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-xs font-mono text-[#DC2626] uppercase font-bold tracking-wider mb-1">
          <Layers className="w-4 h-4" />
          <span>Pipeline Architecture & Security Boundaries</span>
        </div>
        <h2 className="text-3xl font-bold tracking-tight text-[#F5F5F5]">
          How PhishGuard Classifies Threats
        </h2>
        <p className="text-sm text-[#A3A3A3] mt-2 max-w-3xl leading-relaxed">
          An overview of the verified machine learning architecture, serialized artifact pipeline, and explicit operational limitations.
        </p>
      </div>

      {/* 4-Stage Architectural Flow */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl bg-[#171717] border border-[#303030]">
          <div className="w-8 h-8 rounded-lg bg-[#DC2626]/20 border border-[#DC2626]/40 text-[#DC2626] flex items-center justify-center font-mono font-bold text-sm mb-3">
            01
          </div>
          <h3 className="text-sm font-bold text-[#F5F5F5]">Feature Ingestion</h3>
          <p className="text-xs text-[#A3A3A3] mt-1.5 leading-relaxed">
            FastAPI endpoint receives 30 discrete security attributes. Input validator enforces schema constraints, rejects unexpected dimensions, and strips the target column.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-[#171717] border border-[#303030]">
          <div className="w-8 h-8 rounded-lg bg-[#DC2626]/20 border border-[#DC2626]/40 text-[#DC2626] flex items-center justify-center font-mono font-bold text-sm mb-3">
            02
          </div>
          <h3 className="text-sm font-bold text-[#F5F5F5]">Imputation & Alignment</h3>
          <p className="text-xs text-[#A3A3A3] mt-1.5 leading-relaxed">
            The serialized fitted preprocessor handles missing or null features and guarantees exact column ordering corresponding to training geometry.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-[#171717] border border-[#303030]">
          <div className="w-8 h-8 rounded-lg bg-[#DC2626]/20 border border-[#DC2626]/40 text-[#DC2626] flex items-center justify-center font-mono font-bold text-sm mb-3">
            03
          </div>
          <h3 className="text-sm font-bold text-[#F5F5F5]">Ensemble Inference</h3>
          <p className="text-xs text-[#A3A3A3] mt-1.5 leading-relaxed">
            RandomForestClassifier (128 decision trees) aggregates binary votes to compute discrete class predictions (0: phishing, 1: legitimate) and probability estimates.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-[#171717] border border-[#303030]">
          <div className="w-8 h-8 rounded-lg bg-[#DC2626]/20 border border-[#DC2626]/40 text-[#DC2626] flex items-center justify-center font-mono font-bold text-sm mb-3">
            04
          </div>
          <h3 className="text-sm font-bold text-[#F5F5F5]">Output Delivery</h3>
          <p className="text-xs text-[#A3A3A3] mt-1.5 leading-relaxed">
            Returns validated JSON response with explicit prediction label, binary class_id, and model score without leaking internal paths or stack traces.
          </p>
        </div>
      </div>

      {/* Honest Limitations & Scope Boundaries */}
      <div className="p-6 rounded-xl bg-[#171717] border border-[#DC2626]/40 shadow-glow-red">
        <div className="flex items-center space-x-2 text-xs font-mono text-[#DC2626] uppercase font-bold tracking-wider mb-2">
          <AlertTriangle className="w-4 h-4" />
          <span>Operational Boundaries & Limitations</span>
        </div>
        <h3 className="text-lg font-bold text-[#F5F5F5] mb-2">
          What the Current Engine Does NOT Do
        </h3>
        <p className="text-xs text-[#A3A3A3] mb-4 leading-relaxed">
          In compliance with project forensic requirements, the following boundaries represent the actual capabilities of the current implementation:
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="p-3 rounded-lg bg-[#111111] border border-[#303030] flex items-start space-x-2">
            <span className="text-[#DC2626] font-bold text-base leading-none">&#10005;</span>
            <span className="text-[#A3A3A3]">
              <strong className="text-[#F5F5F5]">No Raw URL Scraping:</strong> Does not extract lexical features from raw URL strings automatically. Pre-engineered features must be supplied.
            </span>
          </div>

          <div className="p-3 rounded-lg bg-[#111111] border border-[#303030] flex items-start space-x-2">
            <span className="text-[#DC2626] font-bold text-base leading-none">&#10005;</span>
            <span className="text-[#A3A3A3]">
              <strong className="text-[#F5F5F5]">No Active Network Requests:</strong> The server never navigates to, visits, or pings submitted web domains to avoid SSRF and malicious payload execution.
            </span>
          </div>

          <div className="p-3 rounded-lg bg-[#111111] border border-[#303030] flex items-start space-x-2">
            <span className="text-[#DC2626] font-bold text-base leading-none">&#10005;</span>
            <span className="text-[#A3A3A3]">
              <strong className="text-[#F5F5F5]">No Live Threat Feeds:</strong> Operates strictly via the local offline Random Forest model; does not query dynamic external blocklists.
            </span>
          </div>

          <div className="p-3 rounded-lg bg-[#111111] border border-[#303030] flex items-start space-x-2">
            <span className="text-[#DC2626] font-bold text-base leading-none">&#10005;</span>
            <span className="text-[#A3A3A3]">
              <strong className="text-[#F5F5F5]">Probabilistic Verdict:</strong> Outputs reflect statistical pattern recognition on tabular features, not cryptographic guarantees of site authenticity.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
