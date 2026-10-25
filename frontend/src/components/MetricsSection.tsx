import React from 'react';
import { Award, BarChart2, CheckCircle, Info, Layers } from 'lucide-react';

export const MetricsSection: React.FC = () => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-xs font-mono text-[#DC2626] uppercase font-bold tracking-wider mb-1">
          <BarChart2 className="w-4 h-4" />
          <span>Model Benchmark & Evaluation Report</span>
        </div>
        <h2 className="text-3xl font-bold tracking-tight text-[#F5F5F5]">
          Evaluated Classifier Performance
        </h2>
        <p className="text-sm text-[#A3A3A3] mt-2 max-w-3xl leading-relaxed">
          The following evaluation scores represent population-level benchmark statistics from the completed model-selection phase (Phase 4), evaluated on deduplicated data partitions using stratified cross-validation and a reserved held-out test partition.
        </p>
      </div>

      {/* 4 Core Metric Highlight Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl bg-[#171717] border border-[#303030] hover:border-[#DC2626]/50 transition-all">
          <div className="flex items-center justify-between text-xs text-[#A3A3A3] font-mono mb-2">
            <span>5-Fold Stratified CV</span>
            <Layers className="w-4 h-4 text-[#DC2626]" />
          </div>
          <div className="text-3xl font-extrabold text-[#F5F5F5] font-mono">95.52%</div>
          <span className="text-xs text-[#DC2626] font-medium block mt-1">Cross-Validation F1 Score</span>
          <p className="text-[11px] text-[#737373] mt-2 border-t border-[#303030] pt-2">
            Average macro F1 across 5 distinct training folds without test-set leakage.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-[#171717] border border-[#303030] hover:border-[#DC2626]/50 transition-all">
          <div className="flex items-center justify-between text-xs text-[#A3A3A3] font-mono mb-2">
            <span>Held-Out Partition</span>
            <CheckCircle className="w-4 h-4 text-[#10B981]" />
          </div>
          <div className="text-3xl font-extrabold text-[#F5F5F5] font-mono">96.28%</div>
          <span className="text-xs text-[#10B981] font-medium block mt-1">Held-Out Test Accuracy</span>
          <p className="text-[11px] text-[#737373] mt-2 border-t border-[#303030] pt-2">
            Evaluated exactly once on untouched test partition of 1,069 deduplicated samples.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-[#171717] border border-[#303030] hover:border-[#DC2626]/50 transition-all">
          <div className="flex items-center justify-between text-xs text-[#A3A3A3] font-mono mb-2">
            <span>Held-Out Partition</span>
            <Award className="w-4 h-4 text-[#DC2626]" />
          </div>
          <div className="text-3xl font-extrabold text-[#F5F5F5] font-mono">96.19%</div>
          <span className="text-xs text-[#DC2626] font-medium block mt-1">Held-Out Test F1 Score</span>
          <p className="text-[11px] text-[#737373] mt-2 border-t border-[#303030] pt-2">
            Harmonic mean of precision (96.53%) and recall (95.85%) on held-out test data.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-[#171717] border border-[#303030] hover:border-[#DC2626]/50 transition-all">
          <div className="flex items-center justify-between text-xs text-[#A3A3A3] font-mono mb-2">
            <span>Discriminative Ability</span>
            <BarChart2 className="w-4 h-4 text-[#10B981]" />
          </div>
          <div className="text-3xl font-extrabold text-[#F5F5F5] font-mono">99.41%</div>
          <span className="text-xs text-[#10B981] font-medium block mt-1">Held-Out ROC-AUC</span>
          <p className="text-[11px] text-[#737373] mt-2 border-t border-[#303030] pt-2">
            Area under ROC curve demonstrating high separation between classes.
          </p>
        </div>
      </div>

      {/* Model Benchmark Comparison Table */}
      <div className="p-6 rounded-xl bg-[#171717] border border-[#303030]">
        <h3 className="text-lg font-bold text-[#F5F5F5] mb-1">
          Model Candidate Evaluation Matrix
        </h3>
        <p className="text-xs text-[#A3A3A3] mb-4">
          Trained on 4,272 deduplicated training samples and evaluated via 5-fold cross validation.
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-[#303030] text-[#A3A3A3] uppercase text-[11px]">
                <th className="py-3 px-3">Classifier Model</th>
                <th className="py-3 px-3">Hyperparameters</th>
                <th className="py-3 px-3">5-Fold CV F1</th>
                <th className="py-3 px-3">Test Accuracy</th>
                <th className="py-3 px-3">Test F1</th>
                <th className="py-3 px-3">Selection Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#303030]/60 text-[#F5F5F5]">
              <tr className="bg-[#DC2626]/10 font-bold border-l-2 border-[#DC2626]">
                <td className="py-3 px-3 flex items-center space-x-2">
                  <span className="text-[#DC2626]">&#9733;</span>
                  <span>Random Forest</span>
                </td>
                <td className="py-3 px-3 text-[#A3A3A3]">n_estimators=128</td>
                <td className="py-3 px-3 text-[#DC2626]">95.52%</td>
                <td className="py-3 px-3">96.28%</td>
                <td className="py-3 px-3 text-[#10B981]">96.19%</td>
                <td className="py-3 px-3">
                  <span className="px-2 py-0.5 rounded bg-[#DC2626]/20 text-[#DC2626] border border-[#DC2626]/40 text-[10px]">
                    PRODUCTION WINNER
                  </span>
                </td>
              </tr>
              <tr>
                <td className="py-3 px-3">Gradient Boosting</td>
                <td className="py-3 px-3 text-[#A3A3A3]">n_estimators=128</td>
                <td className="py-3 px-3">94.34%</td>
                <td className="py-3 px-3">94.85%</td>
                <td className="py-3 px-3">94.67%</td>
                <td className="py-3 px-3 text-[#737373]">Candidate</td>
              </tr>
              <tr>
                <td className="py-3 px-3">Decision Tree</td>
                <td className="py-3 px-3 text-[#A3A3A3]">criterion=gini</td>
                <td className="py-3 px-3">93.97%</td>
                <td className="py-3 px-3">93.55%</td>
                <td className="py-3 px-3">93.41%</td>
                <td className="py-3 px-3 text-[#737373]">Candidate</td>
              </tr>
              <tr>
                <td className="py-3 px-3">Logistic Regression</td>
                <td className="py-3 px-3 text-[#A3A3A3]">C=1.0, max_iter=500</td>
                <td className="py-3 px-3">92.48%</td>
                <td className="py-3 px-3">92.70%</td>
                <td className="py-3 px-3">92.42%</td>
                <td className="py-3 px-3 text-[#737373]">Baseline</td>
              </tr>
              <tr>
                <td className="py-3 px-3">AdaBoost</td>
                <td className="py-3 px-3 text-[#A3A3A3]">n_estimators=50</td>
                <td className="py-3 px-3">92.41%</td>
                <td className="py-3 px-3">92.70%</td>
                <td className="py-3 px-3">92.38%</td>
                <td className="py-3 px-3 text-[#737373]">Candidate</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Required Evaluation Disclaimer */}
      <div className="p-4 rounded-xl bg-[#111111] border border-[#303030] flex items-start space-x-3 text-xs text-[#A3A3A3]">
        <Info className="w-5 h-5 text-[#DC2626] flex-shrink-0 mt-0.5" />
        <div>
          <h4 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-wide">
            Statistical Interpretation & Evaluation Notice
          </h4>
          <p className="mt-1 leading-relaxed">
            These reported metrics reflect population-level benchmark validation conducted on the curated dataset during Phase 4. They must <strong>not</strong> be interpreted as the probability that an individual domain or URL is malicious, nor does this presentation claim independent third-party verification of external threats.
          </p>
        </div>
      </div>
    </div>
  );
};
