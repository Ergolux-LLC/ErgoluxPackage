import { json, type RequestHandler } from '@sveltejs/kit';

const WEB_BFF_URL = 'http://web_bff:8000';

export const POST: RequestHandler = async ({ request, cookies }) => {
    const requestId = crypto.randomUUID().substring(0, 8);
    console.log(`[AUTH-REFRESH-${requestId}] Starting token refresh at ${new Date().toISOString()}`);
    
    try {
        // Get refresh token from cookies
        const refreshToken = cookies.get('refresh_token');
        
        if (!refreshToken) {
            console.error(`[AUTH-REFRESH-${requestId}] No refresh token found in cookies`);
            return json(
                { error: 'No refresh token available' },
                { status: 401 }
            );
        }
        
        console.log(`[AUTH-REFRESH-${requestId}] Refresh token found, sending to web-bff`);
        
        // Forward request headers and properly format cookies
        const webBffHeaders: Record<string, string> = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': request.headers.get('user-agent') || 'SvelteKit-Frontend'
        };
        
        // FIXED: Properly build cookie string by just forwarding the Cookie header
        const originalCookieHeader = request.headers.get('cookie');
        if (originalCookieHeader) {
            webBffHeaders['Cookie'] = originalCookieHeader;
            console.log(`[AUTH-REFRESH-${requestId}] Forwarding cookies: ${originalCookieHeader}`);
        } else {
            // Fallback: manually build cookie string if no Cookie header
            webBffHeaders['Cookie'] = `refresh_token=${refreshToken}`;
            console.log(`[AUTH-REFRESH-${requestId}] Built cookie string: refresh_token=${refreshToken.substring(0, 20)}...`);
        }
        
        console.log(`[AUTH-REFRESH-${requestId}] Sending refresh request to web-bff`);
        
        // Send refresh request to web-bff
        const startTime = Date.now();
        const response = await fetch(`${WEB_BFF_URL}/auth/refresh`, {
            method: 'POST',
            headers: webBffHeaders
        });
        
        const duration = Date.now() - startTime;
        console.log(`[AUTH-REFRESH-${requestId}] Web-bff response: ${response.status} in ${duration}ms`);
        
        if (response.ok) {
            const data = await response.json();
            console.log(`[AUTH-REFRESH-${requestId}] Token refresh successful`);
            
            // Forward any Set-Cookie headers from web-bff response to update refresh token
            const responseInit: ResponseInit = {
                status: 200,
                headers: {}
            };
            
            const setCookieHeaders = response.headers.get('set-cookie');
            if (setCookieHeaders) {
                responseInit.headers = { 'Set-Cookie': setCookieHeaders };
                console.log(`[AUTH-REFRESH-${requestId}] Forwarding refresh token cookie update`);
            }
            
            return json({
                access_token: data.access_token,
                token_type: data.token_type || 'Bearer',
                expires_in: data.expires_in || 3600,
                user: data.user
            }, responseInit);
        } else {
            const errorData = await response.json();
            console.error(`[AUTH-REFRESH-${requestId}] Refresh failed:`, errorData);
            
            return json(
                { error: errorData.detail || 'Token refresh failed' },
                { status: response.status }
            );
        }
        
    } catch (error) {
        console.error(`[AUTH-REFRESH-${requestId}] Refresh error:`, error);
        
        if (error instanceof TypeError && error.message.includes('fetch')) {
            return json(
                { error: 'Authentication service unavailable' },
                { status: 502 }
            );
        }
        
        return json(
            { error: 'Internal server error during token refresh' },
            { status: 500 }
        );
    }
};