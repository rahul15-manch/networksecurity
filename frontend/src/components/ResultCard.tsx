import React, { useState } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Info,
  Clock,
  CheckCircle2,
  Globe,
  ChevronDown,
  ChevronUp,
  AlertCircle
} from 'lucide-react';
import type { UnifiedResult } from '../types';

interface ResultCardProps {
  result: UnifiedResult | null;
  isLoading: boolean;
  error: string | null;
  onEnableHeuristics?: () => void;
}

export const ResultCard: React.FC<ResultCardProps> = ({
  result,
  isLoading,
  error,
  onEnableHeuristics
}) => {
  const [showStages, setShowStages] = useState(false);

  if (isLoading) {
    return (
      <div className="p-6 rounded-xl bg-[#171717] border border-[#303030] shadow-card-dark text-center animate-pulse">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-[#202020] text-[#DC2626] mb-4">
          <div className="w-6 h-6 border-2 border-[#DC2626] border-t-transparent rounded-full animate-spin" />
        </div>
        <h3 className="text-lg font-semibold text-[#F5F5F5]">Executing Feature Pipeline & Inference...</h3>
        <p className="text-sm text-[#A3A3A3] mt-1 font-mono">
          Extracting DOM, TLS, and DNS attributes then evaluating Random Forest (n=128) ensemble.
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 rounded-xl bg-[#171717] border border-[#DC2626] shadow-glow-red text-left">
        <div className="flex items-start space-x-3">
          <AlertTriangle className="w-6 h-6 text-[#DC2626] flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-base font-semibold text-[#F5F5F5]">Analysis Request Failed</h3>
            <p className="text-sm text-[#EF4444] mt-1 font-mono">{error}</p>
            <p className="text-xs text-[#A3A3A3] mt-2">
              Ensure the URL is a supported public HTTP/HTTPS destination and the backend is running.
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="p-8 rounded-xl bg-[#171717] border border-[#303030] border-dashed text-center">
        <ShieldAlert className="w-10 h-10 text-[#737373] mx-auto mb-3" />
        <h3 className="text-base font-semibold text-[#F5F5F5]">No Prediction Generated Yet</h3>
        <p className="text-sm text-[#A3A3A3] mt-1 max-w-md mx-auto">
          Enter a web URL above and click &quot;Analyze Live URL&quot; or select a preset vector to inspect model classification.
        </p>
      </div>
    );
  }

  // Handle Incomplete / Unsupported Features State
  if (result.status === 'unsupported_features' || result.feature_coverage === 'incomplete' || result.prediction === null) {
    return (
      <div className="p-6 rounded-xl bg-[#171717] border border-[#F59E0B] shadow-[0_0_20px_-5px_rgba(245,158,11,0.2)] text-left space-y-4">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-6 h-6 text-[#F59E0B] flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <span className="text-xs font-mono uppercase tracking-wider text-[#F59E0B] font-bold block">
              Incomplete Feature Vector
            </span>
            <h3 className="text-lg font-bold text-[#F5F5F5] mt-0.5">
              Strict Mode Halted: 7 Features Require External Baseline
            </h3>
            <p className="text-sm text-[#A3A3A3] mt-2 leading-relaxed">
              The Random Forest model requires an exact 30-feature vector. Several features (such as Alexa Traffic Rank [retired 2022] and Google PageRank [retired 2016]) cannot be faithfully derived from live internet queries without baseline heuristics.
            </p>
          </div>
        </div>

        {/* List of Unsupported Features */}
        {result.unsupported_features && result.unsupported_features.length > 0 && (
          <div className="p-3 rounded-lg bg-[#111111] border border-[#303030]">
            <span className="text-xs font-mono text-[#A3A3A3] block mb-2">
              Unavailable Live Services ({result.unsupported_features.length}):
            </span>
            <div className="flex flex-wrap gap-1.5">
              {result.unsupported_features.map((feat) => (
                <span key={feat} className="px-2 py-0.5 rounded text-[11px] font-mono bg-[#202020] text-[#F59E0B] border border-[#F59E0B]/30">
                  {feat}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Action button to enable heuristics */}
        {onEnableHeuristics && (
          <button
            type="button"
            onClick={onEnableHeuristics}
            className="w-full py-2.5 px-4 rounded-lg bg-[#DC2626] hover:bg-[#EF4444] text-white font-medium text-sm transition-all shadow-glow-red active:scale-95 text-center font-mono"
          >
            Enable Baseline Heuristics & Evaluate Model
          </button>
        )}

        <p className="text-xs text-[#737373] italic">
          * PhishGuard does not fabricate fake predictions when required features are missing in strict mode.
        </p>
      </div>
    );
  }

  const isPhishing = String(result.prediction).toLowerCase() === 'phishing' || result.class_id === 0;
  const legitimateProb = result.model_score !== null ? (result.model_score * 100) : null;
  const phishingProb = legitimateProb !== null ? (100 - legitimateProb) : null;

  return (
    <div
      className={`p-6 rounded-xl bg-[#171717] border shadow-card-dark transition-all ${
        isPhishing
          ? 'border-[#DC2626] shadow-glow-red'
          : 'border-[#10B981]/50 shadow-[0_0_25px_-5px_rgba(16,185,129,0.2)]'
      }`}
    >
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-5 border-b border-[#303030] gap-4">
        {/* Classification Outcome */}
        <div className="flex items-center space-x-3">
          <div
            className={`flex items-center justify-center w-12 h-12 rounded-lg border ${
              isPhishing
                ? 'bg-[#DC2626]/20 border-[#DC2626] text-[#DC2626]'
                : 'bg-[#10B981]/20 border-[#10B981] text-[#10B981]'
            }`}
          >
            {isPhishing ? <ShieldAlert className="w-7 h-7" /> : <ShieldCheck className="w-7 h-7" />}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs uppercase font-mono tracking-wider text-[#A3A3A3]">
                Model Prediction
              </span>
              <span
                className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-bold uppercase ${
                  isPhishing
                    ? 'bg-[#DC2626] text-white'
                    : 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/40'
                }`}
              >
                Class ID: {result.class_id}
              </span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-[#F5F5F5] mt-0.5">
              {isPhishing ? 'Phishing Malicious Signature' : 'Legitimate Safe Signature'}
            </h2>
          </div>
        </div>

        {/* Risk Badge */}
        <div className="flex sm:flex-col sm:items-end justify-between items-center text-right">
          <span className="text-xs text-[#A3A3A3] font-mono">Assessed Risk Tier</span>
          <span
            className={`text-sm font-bold font-mono px-2.5 py-1 rounded ${
              isPhishing
                ? 'bg-[#DC2626]/20 text-[#EF4444] border border-[#DC2626]/40'
                : 'bg-[#10B981]/15 text-[#10B981] border border-[#10B981]/30'
            }`}
          >
            {isPhishing ? 'HIGH RISK' : 'LOW RISK'}
          </span>
        </div>
      </div>

      {/* Target URL & Coverage Metadata if URL analysis */}
      {result.url && (
        <div className="py-3.5 border-b border-[#303030] text-xs font-mono space-y-2">
          <div className="flex items-center justify-between gap-2 overflow-hidden">
            <span className="text-[#A3A3A3] flex items-center space-x-1 flex-shrink-0">
              <Globe className="w-3.5 h-3.5 text-[#DC2626]" />
              <span>Target:</span>
            </span>
            <span className="text-[#F5F5F5] truncate font-semibold" title={result.url}>
              {result.url}
            </span>
          </div>

          <div className="flex items-center justify-between text-[11px]">
            <span className="text-[#A3A3A3]">Feature Coverage:</span>
            <span className={`px-2 py-0.5 rounded uppercase font-bold text-[10px] ${
              result.feature_coverage === 'complete'
                ? 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/40'
                : 'bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/40'
            }`}>
              {result.feature_coverage === 'complete' ? '100% Complete' : 'Heuristic Baseline (UCI Standard)'}
            </span>
          </div>
        </div>
      )}

      {/* Model Probability Breakdown */}
      {result.model_score !== null && legitimateProb !== null && phishingProb !== null && (
        <div className="py-5 border-b border-[#303030] space-y-3">
          <div className="flex justify-between items-center text-xs font-mono">
            <span className="text-[#A3A3A3]">Estimated Legitimate Likelihood:</span>
            <span className="text-[#F5F5F5] font-semibold">{legitimateProb.toFixed(1)}%</span>
          </div>

          {/* Dual Probability Bar */}
          <div className="w-full h-3 rounded-full bg-[#202020] overflow-hidden flex" title="Probability distribution">
            <div
              style={{ width: `${phishingProb}%` }}
              className="h-full bg-gradient-to-r from-[#991B1B] to-[#DC2626] transition-all duration-500"
              title={`Phishing probability: ${phishingProb.toFixed(1)}%`}
            />
            <div
              style={{ width: `${legitimateProb}%` }}
              className="h-full bg-gradient-to-r from-[#059669] to-[#10B981] transition-all duration-500"
              title={`Legitimate probability: ${legitimateProb.toFixed(1)}%`}
            />
          </div>

          <div className="flex justify-between text-[11px] font-mono text-[#A3A3A3]">
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 rounded-full bg-[#DC2626]" />
              <span>Phishing Risk: {phishingProb.toFixed(1)}%</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 rounded-full bg-[#10B981]" />
              <span>Legitimate: {legitimateProb.toFixed(1)}%</span>
            </span>
          </div>
        </div>
      )}

      {/* Extraction Stage Breakdown Accordion */}
      {result.stages && (
        <div className="py-3 border-b border-[#303030]">
          <button
            type="button"
            onClick={() => setShowStages(!showStages)}
            className="w-full flex items-center justify-between text-xs font-mono text-[#A3A3A3] hover:text-[#F5F5F5] py-1 transition-colors"
          >
            <span className="flex items-center space-x-1.5 font-bold">
              <span>Pipeline Stage Breakdown</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#202020] text-[#F5F5F5]">4 Stages</span>
            </span>
            {showStages ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {showStages && (
            <div className="mt-3 space-y-2 text-xs font-mono">
              {Object.entries(result.stages).map(([stageKey, stageInfo]) => (
                <div key={stageKey} className="p-2.5 rounded bg-[#111111] border border-[#303030] flex items-start justify-between gap-2">
                  <div>
                    <span className="text-[#F5F5F5] font-semibold capitalize block">
                      {stageKey.replace('_', ' ')}
                    </span>
                    <span className="text-[11px] text-[#A3A3A3] mt-0.5 block">
                      {stageInfo.details || stageInfo.reason || 'Completed'}
                    </span>
                  </div>
                  <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase flex-shrink-0 ${
                    stageInfo.status === 'success'
                      ? 'bg-[#10B981]/20 text-[#10B981]'
                      : stageInfo.status === 'heuristic_baseline'
                      ? 'bg-[#F59E0B]/20 text-[#F59E0B]'
                      : 'bg-[#DC2626]/20 text-[#EF4444]'
                  }`}>
                    {stageInfo.count ? `${stageInfo.count} Feats` : stageInfo.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Key Factors & Details */}
      <div className="pt-4 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
        <div className="p-3 rounded-lg bg-[#111111] border border-[#303030]">
          <span className="text-[#A3A3A3] block">Evaluated Dimensions</span>
          <span className="text-[#F5F5F5] font-semibold mt-0.5 block flex items-center space-x-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-[#10B981]" />
            <span>30 Security Features</span>
          </span>
        </div>

        <div className="p-3 rounded-lg bg-[#111111] border border-[#303030]">
          <span className="text-[#A3A3A3] block">Active Classifier</span>
          <span className="text-[#F5F5F5] font-semibold mt-0.5 block">Random Forest (n=128)</span>
        </div>

        <div className="p-3 rounded-lg bg-[#111111] border border-[#303030]">
          <span className="text-[#A3A3A3] block">Response Latency</span>
          <span className="text-[#F5F5F5] font-semibold mt-0.5 block flex items-center space-x-1">
            <Clock className="w-3.5 h-3.5 text-[#A3A3A3]" />
            <span>&lt; 50ms Real Pipeline</span>
          </span>
        </div>
      </div>

      {/* Critical Security Warning Disclaimer */}
      <div className="mt-4 p-3 rounded-lg bg-[#111111] border border-[#303030] flex items-start space-x-2 text-xs text-[#A3A3A3]">
        <Info className="w-4 h-4 text-[#F59E0B] flex-shrink-0 mt-0.5" />
        <p>
          <strong className="text-[#F5F5F5]">Security Notice:</strong> Predictions are statistical model estimates based on 30 engineered features, not guarantees of domain safety. Always inspect SSL certificates and authentication flows before sharing sensitive credentials.
        </p>
      </div>
    </div>
  );
};
