import React from 'react';
import { ShieldAlert, GitBranch, Terminal } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="mt-20 bg-[#090909] border-t border-[#303030] py-10 text-xs text-[#737373]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Brand & Attribution */}
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-[#171717] border border-[#DC2626]/40 flex items-center justify-center text-[#DC2626]">
              <ShieldAlert className="w-4 h-4" />
            </div>
            <div>
              <span className="text-sm font-bold text-[#F5F5F5]">
                Phish<span className="text-[#DC2626]">Guard</span>
              </span>
              <p className="text-[11px] text-[#A3A3A3]">
                Machine Learning Phishing Website Classification Dashboard
              </p>
            </div>
          </div>

          {/* Links & Technical Meta */}
          <div className="flex flex-wrap items-center gap-6 text-[#A3A3A3]">
            <a
              href="https://github.com/rahul15-manch/networksecurity"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-1.5 hover:text-[#DC2626] transition-colors"
            >
              <GitBranch className="w-4 h-4 text-[#DC2626]" />
              <span>GitHub Repository</span>
            </a>
            <span className="text-[#303030]">•</span>
            <div className="flex items-center space-x-1.5">
              <Terminal className="w-4 h-4 text-[#DC2626]" />
              <span className="font-mono">FastAPI :8000</span>
            </div>
            <span className="text-[#303030]">•</span>
            <span>Audited Random Forest Pipeline</span>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-8 pt-6 border-t border-[#303030]/60 text-center sm:text-left text-[11px] text-[#737373] space-y-2">
          <p>
            Disclaimer: PhishGuard is built for threat detection research and classification evaluation. Model inferences are probabilistic estimates based on engineered features and must not be used as the sole determinant for enterprise security policies without defense-in-depth verification.
          </p>
          <div className="flex items-center justify-between flex-col sm:flex-row gap-2 pt-2 text-[#A3A3A3]">
            <span>&copy; {new Date().getFullYear()} Rahul Manchanda. Network Security Project.</span>
            <span className="font-mono text-[10px]">Branch: fix/phase1-security-runTime</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
