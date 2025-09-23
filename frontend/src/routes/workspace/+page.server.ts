import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, fetch, url }) => {
    const requestId = crypto.randomUUID().substring(0, 8);
    console.log(`[WORKSPACE-${requestId}] Loading protected workspace page`);
    
    // Check for refresh token (server-side protection)
    const refreshToken = cookies.get('refresh_token');
    
    if (!refreshToken) {
        console.log(`[WORKSPACE-${requestId}] No refresh token found - showing access denied screen`);
        
        // Instead of redirect, return access denied state
        return {
            accessDenied: true,
            message: 'Authentication Required',
            requestId
        };
    }
    
    console.log(`[WORKSPACE-${requestId}] Refresh token found, allowing workspace access`);
    
    // Return data for the protected page
    return {
        accessDenied: false,
        workspace: {
            // This would typically come from validating the refresh token
            // For now, just indicate that server-side validation passed
            serverValidated: true,
            validatedAt: new Date().toISOString(),
            requestId
        }
    };
};