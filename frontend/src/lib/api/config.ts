// API Base URL (should use environment variable in production)
/**
 * API Configuration
 * 
 * Central configuration for all API clients
 */

// API Base URL (should use environment variable in production)
import { PUBLIC_API_BASE_URL } from '$env/static/public';
console.log('[API CONFIG] PUBLIC_API_BASE_URL:', PUBLIC_API_BASE_URL);
export const API_BASE_URL = PUBLIC_API_BASE_URL || 'http://localhost:8050';
console.log('[API CONFIG] API_BASE_URL:', API_BASE_URL);

// Common request headers
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'X-Request-Source': 'web-client'
};

// Generate a unique request ID
export function generateRequestId(): string {
  return `req_${Date.now()}_${Math.random().toString(36).substring(2, 10)}`;
}
