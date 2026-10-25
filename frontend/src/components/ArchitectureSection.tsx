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
          <h3 className="text-sm font-bold text-[#F5F5F5]">URL Extraction & SSRF Defense</h3>
          <p className="text-xs text-[#A3A3A3] mt-1.5 leading-relaxed">
            FastAPI endpoint receives submitted URLs. The feature extractor enforces SSRF defenses (blocking private/loopback/link-local/cloud metadata), extracts 10 lexical attributes, probes DNS/TLS, and parses HTML DOM elements safely without script execution.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-[#171717] border border-[#303030]">
          <div className="w-8 h-8 rounded-lg bg-[#DC2626]/20 border border-[#DC2626]/40 text-[#DC2626] flex items-center justify-center font-mono font-bold text-sm mb-3">
            02
          </div>
          <h3 className="text-sm font-bold text-[#F5F5F5]">Heuristics & Alignment</h3>
          <p className="text-xs text-[#A3A3A3] mt-1.5 leading-relaxed">
            Retired third-party services (Alexa Rank, Google PageRank) use documented UCI baseline defaults. The fitted preprocessor ensures exact column ordering and validates discrete value bounds.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-[#171717] border border-[#303030]">
          <div className="w-8 h-8 rounded-lg bg-[#DC2626]/20 border border-[#DC2626]/40 text-[#DC2626] flex items-center justify-center font-mono font-bold text-sm mb-3">
            03
          </div>
          <h3 className="text-sm font-bold text-[#F5F5F5]">Ensemble Inference</h3>
          <p className="text-xs text-[#A3A3A3] mt-1.5 leading-relaxed">
            RandomForestClassifier (128 decision trees) aggregates binary votes across all 30 dimensions to compute discrete class predictions (0: phishing, 1: legitimate) and probability estimates.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-[#171717] border border-[#303030]">
          <div className="w-8 h-8 rounded-lg bg-[#DC2626]/20 border border-[#DC2626]/40 text-[#DC2626] flex items-center justify-center font-mono font-bold text-sm mb-3">
            04
          </div>
          <h3 className="text-sm font-bold text-[#F5F5F5]">Audited Delivery</h3>
          <p className="text-xs text-[#A3A3A3] mt-1.5 leading-relaxed">
            Returns validated JSON response with explicit prediction label, binary class_id, feature coverage level, and 4-stage pipeline diagnostics without leaking internal paths or stack traces.
          </p>
        </div>
      </div>

      {/* Honest Limitations & Scope Boundaries */}
      <div className="p-6 rounded-xl bg-[#171717] border border-[#DC2626]/40 shadow-glow-red">
        <div className="flex items-center space-x-2 text-xs font-mono text-[#DC2626] uppercase font-bold tracking-wider mb-2">
          <AlertTriangle className="w-4 h-4" />
          <span>Operational Boundaries & Security Controls</span>
        </div>
        <h3 className="text-lg font-bold text-[#F5F5F5] mb-2">
          Architectural Boundaries & Safety Commitments
        </h3>
        <p className="text-xs text-[#A3A3A3] mb-4 leading-relaxed">
          In compliance with security requirements, the following boundaries represent the actual capabilities and safety rules of the pipeline:
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="p-3 rounded-lg bg-[#111111] border border-[#303030] flex items-start space-x-2">
            <span className="text-[#10B981] font-bold text-base leading-none">&#10003;</span>
            <span className="text-[#A3A3A3]">
              <strong className="text-[#F5F5F5]">Strict SSRF Blocking:</strong> Resolves DNS before connection and rejects private networks (RFC 1918), loopback (127.0.0.1/::1), and cloud metadata (169.254.169.254).
            </span>
          </div>

          <div className="p-3 rounded-lg bg-[#111111] border border-[#303030] flex items-start space-x-2">
            <span className="text-[#10B981] font-bold text-base leading-none">&#10003;</span>
            <span className="text-[#A3A3A3]">
              <strong className="text-[#F5F5F5]">No Script Execution:</strong> HTML parsing uses a streaming standard library parser with a 512KB limit and 3-second timeout; JavaScript is never executed.
            </span>
          </div>

          <div className="p-3 rounded-lg bg-[#111111] border border-[#303030] flex items-start space-x-2">
            <span className="text-[#F59E0B] font-bold text-base leading-none">&#33;</span>
            <span className="text-[#A3A3A3]">
              <strong className="text-[#F5F5F5]">Deprecated Service Baseline:</strong> Alexa Rank and Google PageRank are permanently sunset; baseline defaults from the UCI paper are used when heuristics are enabled.
            </span>
          </div>

          <div className="p-3 rounded-lg bg-[#111111] border border-[#303030] flex items-start space-x-2">
            <span className="text-[#F59E0B] font-bold text-base leading-none">&#33;</span>
            <span className="text-[#A3A3A3]">
              <strong className="text-[#F5F5F5]">Probabilistic Model:</strong> Outputs reflect machine learning classification on 30 features, not absolute cryptographic guarantees of safety.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
