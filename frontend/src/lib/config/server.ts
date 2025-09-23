// Server-side configuration for Docker networking
// This should only be used in +server.ts files and other server-side code

const {
  SERVER_API_BASE_URL,
  SERVER_HUMAN_SERVICE_URL,
  PUBLIC_API_BASE_URL,
  PUBLIC_HUMAN_SERVICE_URL
} = process.env;

export const serverConfig = {
  api: {
    // Use Docker service names for server-to-server communication
    baseUrl: SERVER_API_BASE_URL || PUBLIC_API_BASE_URL || 'http://localhost:8050',
    humanServiceUrl: SERVER_HUMAN_SERVICE_URL || PUBLIC_HUMAN_SERVICE_URL || 'http://localhost:8004'
  }
};