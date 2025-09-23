import { json, redirect, type RequestHandler } from '@sveltejs/kit';

const WEB_BFF_URL = 'http://web_bff:8000';

export const POST: RequestHandler = async ({ request, cookies }) => {
    const requestId = crypto.randomUUID().substring(0, 8);
    console.log(`[AUTH-LOGOUT-${requestId}] Starting logout at ${new Date().toISOString()}`);
    
    try {
        // Forward logout request to web-bff
        const webBffHeaders: Record<string, string> = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': request.headers.get('user-agent') || 'SvelteKit-Frontend'
        };
        
        // Build cookie string for forwarding
        const cookieString = Object.entries(cookies.getAll())
            .map(([name, value]) => `${name}=${value}`)
            .join('; ');
        
        if (cookieString) {
            webBffHeaders['Cookie'] = cookieString;
        }
        
        console.log(`[AUTH-LOGOUT-${requestId}] Sending logout request to web-bff`);
        
        const response = await fetch(`${WEB_BFF_URL}/auth/logout`, {
            method: 'POST',
            headers: webBffHeaders
        });
        
        console.log(`[AUTH-LOGOUT-${requestId}] Web-bff logout response: ${response.status}`);
        
    } catch (error) {
        console.error(`[AUTH-LOGOUT-${requestId}] Logout error (continuing anyway):`, error);
        // Continue with local cleanup even if remote logout fails
    }
    
    // Clear cookies locally regardless of web-bff response
    cookies.delete('refresh_token', { 
        path: '/', 
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax'
    });
    
    // Also clear access token cookie if it exists
    cookies.delete('access_token', { 
        path: '/',
        secure: process.env.NODE_ENV === 'production', 
        sameSite: 'lax'
    });
    
    console.log(`[AUTH-LOGOUT-${requestId}] Logout completed, cookies cleared`);
    
    return json({ 
        success: true, 
        message: 'Logged out successfully' 
    });
};

export const GET: RequestHandler = async ({ cookies }) => {
    // Handle GET requests by clearing cookies and redirecting to login
    console.log('GET logout request - clearing cookies and redirecting');
    
    cookies.delete('refresh_token', { 
        path: '/', 
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax'
    });
    
    cookies.delete('access_token', { 
        path: '/',
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax'
    });
    
    throw redirect(302, '/logintest?message=Logged out successfully');
};