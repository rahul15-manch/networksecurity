import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Hero } from './components/Hero';
import { AnalysisPanel } from './components/AnalysisPanel';
import { ResultCard } from './components/ResultCard';
import { MetricsSection } from './components/MetricsSection';
import { ArchitectureSection } from './components/ArchitectureSection';
import { Footer } from './components/Footer';
import { checkHealth, predictPhishing, predictURL } from './services/api';
import type { HealthResponse, PhishingFeatures, UnifiedResult } from './types';
import { PRESETS } from './types';

export const App: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'analyze' | 'metrics' | 'architecture'>('analyze');
  const [features, setFeatures] = useState<PhishingFeatures>(PRESETS.phishing.features);
  const [urlInput, setUrlInput] = useState<string>('https://secure-login.apple-account-verification.com/auth');
  const [allowHeuristics, setAllowHeuristics] = useState<boolean>(true);
  const [result, setResult] = useState<UnifiedResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Poll or check health on initial load
  useEffect(() => {
    let isMounted = true;
    checkHealth()
      .then(data => {
        if (isMounted) setHealth(data);
      })
      .catch(() => {
        if (isMounted) {
          setHealth({
            status: 'degraded',
            model_loaded: false,
            version: '1.1.0',
            supported_features_count: 30,
          });
        }
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const handleSelectPreset = (newFeatures: PhishingFeatures) => {
    setFeatures(newFeatures);
    setResult(null);
    setError(null);
  };

  const handleAnalyzeVector = async () => {
    if (isLoading) return;
    setIsLoading(true);
    setError(null);

    try {
      const prediction = await predictPhishing(features);
      setResult(prediction);
      const resultElem = document.getElementById('results-view');
      if (resultElem) {
        resultElem.scrollIntoView({ behavior: 'smooth' });
      }
    } catch (err: any) {
      setError(err.message || 'An unexpected inference error occurred.');
      setResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyzeUrl = async (targetUrl: string, heuristics: boolean) => {
    if (isLoading) return;
    setIsLoading(true);
    setError(null);

    try {
      const urlResponse = await predictURL({
        url: targetUrl,
        allow_heuristics: heuristics,
        fetch_network: true,
      });

      setResult(urlResponse);

      // If features were extracted, sync with 30-feature vector controls
      if (urlResponse.features && Object.keys(urlResponse.features).length > 0) {
        setFeatures(prev => ({
          ...prev,
          ...urlResponse.features,
        }));
      }

      const resultElem = document.getElementById('results-view');
      if (resultElem) {
        resultElem.scrollIntoView({ behavior: 'smooth' });
      }
    } catch (err: any) {
      setError(err.message || 'URL feature extraction or inference failed.');
      setResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEnableHeuristicsAndReanalyze = () => {
    setAllowHeuristics(true);
    if (urlInput) {
      handleAnalyzeUrl(urlInput, true);
    }
  };

  const scrollToAnalyzer = () => {
    const el = document.getElementById('analyzer');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-[#090909] text-[#F5F5F5] flex flex-col font-sans selection:bg-[#DC2626] selection:text-white">
      {/* Navigation Header */}
      <Navbar health={health} activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="flex-1">
        {activeTab === 'analyze' && (
          <div>
            {/* Cybersecurity Hero Banner */}
            <Hero onSelectPreset={handleSelectPreset} onScrollToAnalyzer={scrollToAnalyzer} />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* 2-Columns for URL & Feature Controls */}
                <div className="lg:col-span-2 space-y-6">
                  <AnalysisPanel
                    features={features}
                    setFeatures={setFeatures}
                    onAnalyzeVector={handleAnalyzeVector}
                    onAnalyzeUrl={handleAnalyzeUrl}
                    isLoading={isLoading}
                    onSelectPreset={handleSelectPreset}
                    urlInput={urlInput}
                    setUrlInput={setUrlInput}
                    allowHeuristics={allowHeuristics}
                    setAllowHeuristics={setAllowHeuristics}
                  />
                </div>

                {/* 1-Column Sticky Output Card */}
                <div className="lg:col-span-1" id="results-view">
                  <div className="sticky top-24 space-y-6">
                    <div>
                      <span className="text-xs font-mono uppercase tracking-wider text-[#A3A3A3] block mb-2 font-bold">
                        Inference Output
                      </span>
                      <ResultCard
                        result={result}
                        isLoading={isLoading}
                        error={error}
                        onEnableHeuristics={handleEnableHeuristicsAndReanalyze}
                      />
                    </div>

                    {/* Quick Model Summary Card */}
                    <div className="p-5 rounded-xl bg-[#111111] border border-[#303030] text-xs font-mono space-y-2">
                      <div className="flex justify-between items-center text-[#A3A3A3]">
                        <span>Classifier:</span>
                        <span className="text-[#F5F5F5]">Random Forest (128 trees)</span>
                      </div>
                      <div className="flex justify-between items-center text-[#A3A3A3]">
                        <span>Preprocessing:</span>
                        <span className="text-[#F5F5F5]">SimpleImputer</span>
                      </div>
                      <div className="flex justify-between items-center text-[#A3A3A3]">
                        <span>Dimensions:</span>
                        <span className="text-[#F5F5F5]">30 Features Enforced</span>
                      </div>
                      <div className="flex justify-between items-center text-[#A3A3A3]">
                        <span>Target:</span>
                        <span className="text-[#F5F5F5]">Result (0=Phish, 1=Legit)</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'metrics' && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <MetricsSection />
          </div>
        )}

        {activeTab === 'architecture' && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <ArchitectureSection />
          </div>
        )}
      </main>

      {/* Global Footer */}
      <Footer />
    </div>
  );
};

export default App;
