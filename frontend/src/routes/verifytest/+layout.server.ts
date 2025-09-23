import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ cookies, fetch, url }) => {
    const requestId = crypto.randomUUID().substring(0, 8);
    console.log(`[VERIFY-LAYOUT-${requestId}] Loading protected layout for ${url.pathname}`);
    
    // Check if refresh token exists
    const refreshToken = cookies.get('refresh_token');
    console.log(`[VERIFY-LAYOUT-${requestId}] Refresh token present: ${!!refreshToken}`);
    
    // Try to get access token from various sources
    // In a real app, this might come from a session store or be passed from the client
    const accessToken = null; // We'll handle this in the page components
    
    return {
        auth: {
            hasRefreshToken: !!refreshToken,
            hasAccessToken: !!accessToken,
            isAuthenticated: !!refreshToken // Basic check
        },
        requestId
    };
};