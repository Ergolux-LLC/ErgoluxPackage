# Environment Configuration

This project uses SvelteKit's built-in environment handling for managing different environments.

## Environment Files

- `.env` - Default environment (currently development)
- `.env.development` - Development environment settings
- `.env.production` - Production environment settings
- `.env.example` - Example configuration file

## Available Environments

### Development Mode (Current)

- **Debug logging enabled**
- **Development tools visible**
- **Hot reload enabled**
- **Local API endpoints**
- **Extended timeouts**

### Production Mode

- **Optimized build**
- **Debug logging disabled**
- **Development tools hidden**
- **Production API endpoints**
- **Standard timeouts**

## Scripts

```bash
# Development mode (default)
npm run dev

# Development mode with production config
npm run dev:prod

# Build for production
npm run build

# Build for development
npm run build:dev
```

## Environment Variables

All public environment variables must be prefixed with `PUBLIC_`:

- `PUBLIC_APP_ENV` - Environment name (development/production)
- `PUBLIC_APP_NAME` - Application name
- `PUBLIC_APP_VERSION` - Application version
- `PUBLIC_API_BASE_URL` - API base URL
- `PUBLIC_DEBUG_MODE` - Enable debug mode
- `PUBLIC_SHOW_DEV_TOOLS` - Show development tools

## Development Tools

When in development mode, you'll see:

1. **Development Tools Panel** (top-right corner)

   - Environment information
   - Quick actions (reload, clear storage)
   - Navigation shortcuts

2. **Environment Badge** (bottom-left corner)
   - Shows current environment
   - Version information

## Usage in Code

```typescript
import { config, devLog, getApiUrl } from "$lib/config/environment";

// Check environment
if (config.isDevelopment) {
  // Development-only code
}

// Logging (only shows in dev mode)
devLog("Debug message", { data: someData });

// API URLs
const apiUrl = getApiUrl("/api/users");

// Feature flags
if (config.features.debugMode) {
  // Debug features
}
```

## API Client

The API client automatically configures itself based on the environment:

```typescript
import { apiClient } from "$lib/api/client";

// Automatically uses correct base URL and timeout
const user = await apiClient.getUser("123");
```

## Switching Environments

To switch from development to production:

1. Update `.env` file or set `NODE_ENV=production`
2. Restart the development server
3. Development tools will automatically hide
4. API endpoints will switch to production URLs

## Security Notes

- Never commit actual `.env` files to version control
- Use `.env.example` as a template
- Keep sensitive data in server-side environment variables only
- All `PUBLIC_` variables are exposed to the client
