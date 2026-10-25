import type { HealthResponse, PhishingFeatures, PredictionResponse } from '../types';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/+$/, '');

export class ApiError extends Error {
  public statusCode?: number;
  public details?: any;

  constructor(message: string, statusCode?: number, details?: any) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.details = details;
  }
}

/**
 * Validates and formats the 30 engineered features payload before sending.
 */
function cleanFeaturePayload(features: PhishingFeatures): Record<string, number> {
  const payload: Record<string, number> = {};
  for (const [key, val] of Object.entries(features)) {
    // Strip accidental 'Result' or auxiliary keys
    if (key === 'Result' || key.startsWith('_')) continue;
    payload[key] = Number(val);
  }
  return payload;
}

/**
 * Checks system health and model availability.
 */
export async function checkHealth(): Promise<HealthResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new ApiError(
        errorData?.detail || `Health check failed with status ${response.status}`,
        response.status,
        errorData
      );
    }

    const data: HealthResponse = await response.json();
    return data;
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(
      'Unable to connect to PhishGuard prediction service. Ensure backend is running.',
      0,
      err.message
    );
  }
}

/**
 * Submits the 30-feature vector for real-time phishing classification.
 */
export async function predictPhishing(features: PhishingFeatures): Promise<PredictionResponse> {
  const cleanedPayload = cleanFeaturePayload(features);

  try {
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(cleanedPayload),
    });

    if (!response.ok) {
      let errorMessage = `Prediction request failed (HTTP ${response.status})`;
      let errorDetail: any = null;
      try {
        errorDetail = await response.json();
        if (typeof errorDetail?.detail === 'string') {
          errorMessage = errorDetail.detail;
        } else if (Array.isArray(errorDetail?.detail)) {
          // Pydantic validation error list
          const firstErr = errorDetail.detail[0];
          errorMessage = `Validation error on ${firstErr.loc?.join('.') || 'field'}: ${firstErr.msg}`;
        }
      } catch {
        // Response was not JSON
      }

      if (response.status === 503) {
        errorMessage = 'Model artifact is currently unavailable on the server. Ensure training has completed.';
      } else if (response.status === 422) {
        errorMessage = `Invalid feature input values: ${errorMessage}`;
      }

      throw new ApiError(errorMessage, response.status, errorDetail);
    }

    const data: PredictionResponse = await response.json();
    if (!data || typeof data.prediction !== 'string' || (data.class_id !== 0 && data.class_id !== 1)) {
      throw new ApiError('Received malformed response schema from inference backend.', 500, data);
    }

    return data;
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(
      'Network communication failure: unable to reach the prediction endpoint.',
      0,
      err.message
    );
  }
}
