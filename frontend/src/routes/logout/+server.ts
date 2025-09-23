import type { RequestHandler } from "@sveltejs/kit";
import { serverConfig } from '$lib/config/server';

export const GET: RequestHandler = async ({ cookies, request }) => {
    // Call web-bff logout endpoint to clear session on server
    try {
        const logoutUrl = `${serverConfig.api.baseUrl}/auth/logout`;
        await fetch(logoutUrl, {
            method: 'POST',
            headers: {
                'Cookie': request.headers.get('cookie') || ''
            }
        });
    } catch (error) {
        console.error('[LOGOUT] Error calling web-bff logout:', error);
        // Continue with local cleanup even if server call fails
    }

    // Clear local cookies
    cookies.delete("sessionid", { path: "/" });
    cookies.delete("refresh_token", { path: "/" });
    
    return new Response(null, {
        status: 302,
        headers: { Location: "/login" }
    });
};