import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { checkHealth, predictPhishing, ApiError } from '../services/api';
import { PRESETS } from '../types';

describe('API Client Service', () => {
  const originalFetch = globalThis.fetch;

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it('checkHealth returns health data on successful response', async () => {
    const mockHealthResponse = {
      status: 'healthy',
      model_loaded: true,
      version: '1.0.0',
      supported_features_count: 30,
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockHealthResponse,
    } as any);

    const data = await checkHealth();
    expect(data.status).toBe('healthy');
    expect(data.model_loaded).toBe(true);
    expect(data.supported_features_count).toBe(30);
  });

  it('checkHealth throws ApiError on non-200 response', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => ({ detail: 'Server error' }),
    } as any);

    await expect(checkHealth()).rejects.toThrow(ApiError);
  });

  it('predictPhishing sends cleaned features and parses valid prediction', async () => {
    const mockPrediction = {
      prediction: 'phishing',
      class_id: 0,
      model_score: 0.04,
    };

    globalThis.fetch = vi.fn().mockImplementation((_url, options) => {
      const body = JSON.parse(options.body);
      // Verify target Result is not in the request payload
      expect(body).not.toHaveProperty('Result');
      expect(Object.keys(body).length).toBe(30);

      return Promise.resolve({
        ok: true,
        json: async () => mockPrediction,
      });
    });

    // Provide features containing accidental Result key
    const featuresWithResult = {
      ...PRESETS.phishing.features,
      Result: 1,
    };

    const res = await predictPhishing(featuresWithResult);
    expect(res.prediction).toBe('phishing');
    expect(res.class_id).toBe(0);
    expect(res.model_score).toBe(0.04);
  });

  it('predictPhishing handles HTTP 503 model unavailable error gracefully', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
      json: async () => ({ detail: 'Model artifact not available' }),
    } as any);

    await expect(predictPhishing(PRESETS.phishing.features)).rejects.toThrow(
      /Model artifact is currently unavailable/i
    );
  });

  it('predictPhishing handles HTTP 422 input validation error', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 422,
      json: async () => ({
        detail: [{ loc: ['body', 'having_IP_Address'], msg: 'Input should be -1, 0, or 1' }],
      }),
    } as any);

    await expect(predictPhishing(PRESETS.phishing.features)).rejects.toThrow(
      /Invalid feature input values/i
    );
  });

  it('predictPhishing handles network failure without throwing unhandled exceptions', async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'));

    await expect(predictPhishing(PRESETS.phishing.features)).rejects.toThrow(
      /Network communication failure/i
    );
  });
});
