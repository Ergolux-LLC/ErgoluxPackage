import { browser, dev } from '$app/environment';
import { 
  PUBLIC_APP_ENV,
  PUBLIC_APP_NAME,
  PUBLIC_APP_VERSION,
  PUBLIC_API_BASE_URL,
  PUBLIC_HUMAN_SERVICE_URL,
  PUBLIC_DEBUG_MODE,
  PUBLIC_SHOW_DEV_TOOLS
} from '$env/static/public';

// Log all environment variables at module load
console.log('[ENVIRONMENT] PUBLIC_APP_ENV:', PUBLIC_APP_ENV);
console.log('[ENVIRONMENT] PUBLIC_APP_NAME:', PUBLIC_APP_NAME);
console.log('[ENVIRONMENT] PUBLIC_APP_VERSION:', PUBLIC_APP_VERSION);
console.log('[ENVIRONMENT] PUBLIC_API_BASE_URL:', PUBLIC_API_BASE_URL);
console.log('[ENVIRONMENT] PUBLIC_HUMAN_SERVICE_URL:', PUBLIC_HUMAN_SERVICE_URL);
console.log('[ENVIRONMENT] PUBLIC_DEBUG_MODE:', PUBLIC_DEBUG_MODE);
console.log('[ENVIRONMENT] PUBLIC_SHOW_DEV_TOOLS:', PUBLIC_SHOW_DEV_TOOLS);
if (typeof import.meta !== 'undefined') {
  console.log('[ENVIRONMENT] import.meta.env:', import.meta.env);
}

// Environment configuration
export const config = {
  // Environment info
  isDevelopment: dev,
  isProduction: !dev,
  isBrowser: browser,
  
  // App configuration
  app: {
    name: PUBLIC_APP_NAME || 'Ergolux CRM',
    version: PUBLIC_APP_VERSION || '1.0.0',
    env: PUBLIC_APP_ENV || 'development'
  },
  
  // API configuration
  api: {
    baseUrl: PUBLIC_API_BASE_URL || 'http://web_bff:8000',
    humanServiceUrl: PUBLIC_HUMAN_SERVICE_URL || 'http://human_service:8000',
    timeout: dev ? 10000 : 30000 // 10s for dev, 30s for prod
  },
  
  // Feature flags
  features: {
    debugMode: PUBLIC_DEBUG_MODE === 'true',
    showDevTools: PUBLIC_SHOW_DEV_TOOLS === 'true',
    enableLogging: dev || PUBLIC_DEBUG_MODE === 'true'
  },
  
  // UI configuration
  ui: {
    showEnvironmentBadge: dev,
    enableDevMenu: dev && PUBLIC_SHOW_DEV_TOOLS === 'true',
    defaultTimeout: dev ? 5000 : 3000
  }
};

// Helper functions
export const isDevMode = () => config.isDevelopment;
export const isProdMode = () => config.isProduction;
export const getApiUrl = (endpoint: string = '') => `${config.api.baseUrl}${endpoint}`;
export const shouldLog = () => config.features.enableLogging;

// Development utilities
export const devLog = (message: string, ...args: any[]) => {
  if (shouldLog()) {
    console.log(`[${config.app.env.toUpperCase()}] ${message}`, ...args);
  }
};

export const devWarn = (message: string, ...args: any[]) => {
  if (shouldLog()) {
    console.warn(`[${config.app.env.toUpperCase()}] ${message}`, ...args);
  }
};

export const devError = (message: string, ...args: any[]) => {
  if (shouldLog()) {
    console.error(`[${config.app.env.toUpperCase()}] ${message}`, ...args);
  }
};

// Export default config
export default config;
