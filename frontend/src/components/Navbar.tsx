import React, { useState } from 'react';
import { ShieldAlert, Activity, Menu, X, Cpu } from 'lucide-react';
import type { HealthResponse } from '../types';

interface NavbarProps {
  health: HealthResponse | null;
  activeTab: 'analyze' | 'metrics' | 'architecture';
  setActiveTab: (tab: 'analyze' | 'metrics' | 'architecture') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ health, activeTab, setActiveTab }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isModelReady = health?.model_loaded === true;

  return (
    <header className="sticky top-0 z-50 bg-[#090909]/95 backdrop-blur-md border-b border-[#303030]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Product Brand */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('analyze')}>
            <div className="relative flex items-center justify-center w-10 h-10 rounded-lg bg-[#171717] border border-[#DC2626]/40 shadow-glow-red">
              <ShieldAlert className="w-6 h-6 text-[#DC2626]" />
              <div className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-[#DC2626] animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight text-[#F5F5F5]">
                  Phish<span className="text-[#DC2626]">Guard</span>
                </span>
                <span className="text-[10px] uppercase font-mono font-semibold px-1.5 py-0.5 rounded bg-[#DC2626]/20 text-[#DC2626] border border-[#DC2626]/40">
                  ML-Core
                </span>
              </div>
              <p className="text-[11px] text-[#A3A3A3] font-mono tracking-tight hidden sm:block">
                Cybersecurity Threat Intelligence Engine
              </p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-1" aria-label="Main Navigation">
            <button
              onClick={() => setActiveTab('analyze')}
              className={`px-3.5 py-2 rounded-md text-sm font-medium transition-all ${
                activeTab === 'analyze'
                  ? 'bg-[#171717] text-[#F5F5F5] border border-[#DC2626] shadow-glow-red'
                  : 'text-[#A3A3A3] hover:text-[#F5F5F5] hover:bg-[#171717]/60'
              }`}
            >
              Analyze Vector
            </button>
            <button
              onClick={() => setActiveTab('metrics')}
              className={`px-3.5 py-2 rounded-md text-sm font-medium transition-all ${
                activeTab === 'metrics'
                  ? 'bg-[#171717] text-[#F5F5F5] border border-[#DC2626] shadow-glow-red'
                  : 'text-[#A3A3A3] hover:text-[#F5F5F5] hover:bg-[#171717]/60'
              }`}
            >
              Model Metrics
            </button>
            <button
              onClick={() => setActiveTab('architecture')}
              className={`px-3.5 py-2 rounded-md text-sm font-medium transition-all ${
                activeTab === 'architecture'
                  ? 'bg-[#171717] text-[#F5F5F5] border border-[#DC2626] shadow-glow-red'
                  : 'text-[#A3A3A3] hover:text-[#F5F5F5] hover:bg-[#171717]/60'
              }`}
            >
              Pipeline & Limits
            </button>
          </nav>

          {/* System Status Indicators */}
          <div className="hidden lg:flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-xs font-mono px-3 py-1.5 rounded-full bg-[#111111] border border-[#303030]">
              <Cpu className="w-3.5 h-3.5 text-[#A3A3A3]" />
              <span className="text-[#A3A3A3]">Model:</span>
              <span className="text-[#F5F5F5] font-semibold">RandomForest (128)</span>
            </div>

            <div
              className={`flex items-center space-x-2 text-xs font-mono px-3 py-1.5 rounded-full border transition-colors ${
                isModelReady
                  ? 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]/30'
                  : 'bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/30'
              }`}
            >
              <Activity className="w-3.5 h-3.5 animate-pulse" />
              <span>{isModelReady ? 'API: Operational' : 'API: Degraded'}</span>
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg bg-[#171717] border border-[#303030] text-[#A3A3A3] hover:text-[#F5F5F5] focus:outline-none focus:ring-2 focus:ring-[#DC2626]"
              aria-label="Toggle Navigation Menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-[#111111] border-b border-[#303030] px-4 pt-3 pb-4 space-y-2">
          <button
            onClick={() => {
              setActiveTab('analyze');
              setMobileMenuOpen(false);
            }}
            className={`w-full text-left px-4 py-2.5 rounded-lg text-sm font-medium ${
              activeTab === 'analyze'
                ? 'bg-[#171717] text-[#F5F5F5] border border-[#DC2626]'
                : 'text-[#A3A3A3] hover:bg-[#171717]'
            }`}
          >
            Analyze Vector
          </button>
          <button
            onClick={() => {
              setActiveTab('metrics');
              setMobileMenuOpen(false);
            }}
            className={`w-full text-left px-4 py-2.5 rounded-lg text-sm font-medium ${
              activeTab === 'metrics'
                ? 'bg-[#171717] text-[#F5F5F5] border border-[#DC2626]'
                : 'text-[#A3A3A3] hover:bg-[#171717]'
            }`}
          >
            Model Metrics
          </button>
          <button
            onClick={() => {
              setActiveTab('architecture');
              setMobileMenuOpen(false);
            }}
            className={`w-full text-left px-4 py-2.5 rounded-lg text-sm font-medium ${
              activeTab === 'architecture'
                ? 'bg-[#171717] text-[#F5F5F5] border border-[#DC2626]'
                : 'text-[#A3A3A3] hover:bg-[#171717]'
            }`}
          >
            Pipeline & Limits
          </button>
          <div className="pt-2 border-t border-[#303030] flex items-center justify-between text-xs text-[#A3A3A3]">
            <span>Model: RandomForest (128)</span>
            <span className={isModelReady ? 'text-[#10B981]' : 'text-[#F59E0B]'}>
              {isModelReady ? 'Operational' : 'Degraded'}
            </span>
          </div>
        </div>
      )}
    </header>
  );
};
