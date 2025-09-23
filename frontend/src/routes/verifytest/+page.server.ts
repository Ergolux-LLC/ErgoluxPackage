import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, fetch, url }) => {
    const requestId = crypto.randomUUID().substring(0, 8);
    console.log(`[VERIFY-PAGE-${requestId}] Loading verify test page`);
    
    // Get refresh token from cookies
    const refreshToken = cookies.get('refresh_token');
    
    if (!refreshToken) {
        console.log(`[VERIFY-PAGE-${requestId}] No refresh token found, redirecting to login`);
        throw redirect(302, '/logintest?message=Please login first');
    }
    
    console.log(`[VERIFY-PAGE-${requestId}] Refresh token found, allowing access to verify test`);
    
    // Return data for the page
    return {
        serverValidation: {
            refreshTokenPresent: true,
            validatedAt: new Date().toISOString(),
            requestId
        }
    };
};