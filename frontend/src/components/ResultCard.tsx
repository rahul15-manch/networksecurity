import React from 'react';
import { ShieldAlert, ShieldCheck, AlertTriangle, Info, Clock, CheckCircle2 } from 'lucide-react';
import type { PredictionResponse } from '../types';

interface ResultCardProps {
  result: PredictionResponse | null;
  isLoading: boolean;
  error: string | null;
}

export const ResultCard: React.FC<ResultCardProps> = ({ result, isLoading, error }) => {
  if (isLoading) {
    return (
      <div className="p-6 rounded-xl bg-[#171717] border border-[#303030] shadow-card-dark text-center animate-pulse">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-[#202020] text-[#DC2626] mb-4">
          <div className="w-6 h-6 border-2 border-[#DC2626] border-t-transparent rounded-full animate-spin" />
        </div>
        <h3 className="text-lg font-semibold text-[#F5F5F5]">Executing Random Forest Inference...</h3>
        <p className="text-sm text-[#A3A3A3] mt-1 font-mono">
          Evaluating 30 preprocessed feature dimensions through fitted ensemble estimators.
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
            <h3 className="text-base font-semibold text-[#F5F5F5]">Inference Request Failed</h3>
            <p className="text-sm text-[#EF4444] mt-1 font-mono">{error}</p>
            <p className="text-xs text-[#A3A3A3] mt-2">
              Verify that the backend service is running on port 8000 and the model artifact exists at final_model/model.pkl.
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
          Select a template above or adjust the 30 feature toggles, then click &quot;Analyze Feature Vector&quot; to inspect model classification.
        </p>
      </div>
    );
  }

  const isPhishing = result.prediction.toLowerCase() === 'phishing' || result.class_id === 0;
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
            <span>&lt; 20ms Local Infer</span>
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
