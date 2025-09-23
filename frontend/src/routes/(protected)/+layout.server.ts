
import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async (event) => {
  try {
    const { cookies, url, request } = event;
    const requestId = crypto.randomUUID().substring(0, 8);
    const logPrefix = `[PROTECTED-${requestId}]`;
    
    console.log(`${logPrefix} Loading protected route: ${url.pathname}`);
    console.log(`${logPrefix} Host: ${request.headers.get('host')}`);
    
    // Check for refresh token (server-side protection) - same pattern as workspace
    const refreshToken = cookies.get('refresh_token');
    console.log(`${logPrefix} Refresh token present: ${!!refreshToken}`);
    
    if (!refreshToken) {
      console.log(`${logPrefix} No refresh token found - blocking access to protected route`);
      
      // Use same pattern as workspace: return access denied state instead of redirect
      return {
        accessDenied: true,
        message: 'Authentication Required',
        requestId,
        redirectUrl: `/login?error=auth_required&redirected_from=${url.pathname}`
      };
    }
    
    console.log(`${logPrefix} Refresh token found, allowing access to protected route`);
    
    // Return data for the protected pages
    return {
      accessDenied: false,
      protectedData: {
        serverValidated: true,
        validatedAt: new Date().toISOString(),
        requestId,
        path: url.pathname
      }
    };
  } catch (error) {
    console.error('[PROTECTED LAYOUT ERROR]', error);
    
    // Return access denied on any error to be safe
    return {
      accessDenied: true,
      message: 'Server Error - Authentication Required',
      error: error instanceof Error ? error.message : String(error)
    };
  }
};
