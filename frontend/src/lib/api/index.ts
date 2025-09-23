/**
 * Main API exports
 * Single import point for all API functionality
 */

export { apiClient } from './client';
export type { ApiResponse } from './client';

export * from './auth';

// Future API modules will be exported here
// export * from './contacts';
// export * from './workspaces';
// export * from './transactions';