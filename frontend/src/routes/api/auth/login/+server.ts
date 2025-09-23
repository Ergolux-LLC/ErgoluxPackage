import { json, type RequestHandler } from '@sveltejs/kit';
import { dev } from '$app/environment';

const WEB_BFF_URL = 'http://web_bff:8000'

export const POST: RequestHandler = async ({ request, cookies }) => {
    const startTime = Date.now();
    const requestId = crypto.randomUUID().substring(0, 8);
    
    console.log(`[AUTH-LOGIN-${requestId}] Starting login request at ${new Date().toISOString()}`);
    
    try {
        // Parse request body
        const body = await request.json();
        const { email, password } = body;
        
        console.log(`[AUTH-LOGIN-${requestId}] Request body parsed successfully`);
        console.log(`[AUTH-LOGIN-${requestId}] Email: ${email ? email : 'missing'}`);
        console.log(`[AUTH-LOGIN-${requestId}] Password: ${password ? '[REDACTED]' : 'missing'}`);
        
        if (!email || !password) {
            console.error(`[AUTH-LOGIN-${requestId}] Missing required fields - email: ${!!email}, password: ${!!password}`);
            return json(
                { error: 'Email and password are required' },
                { status: 400 }
            );
        }

        // Prepare form data for web-bff
        const formData = new FormData();
        formData.append('email', email);
        formData.append('password', password);
        
        console.log(`[AUTH-LOGIN-${requestId}] Form data prepared for web-bff`);
        console.log(`[AUTH-LOGIN-${requestId}] Target URL: ${WEB_BFF_URL}/auth/login`);

        // Make request to web-bff
        const webBffResponse = await fetch(`${WEB_BFF_URL}/auth/login`, {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json',
                'User-Agent': `SvelteKit-Frontend-${requestId}`
            }
        });

        console.log(`[AUTH-LOGIN-${requestId}] Web-bff response received`);
        console.log(`[AUTH-LOGIN-${requestId}] Status: ${webBffResponse.status} ${webBffResponse.statusText}`);
        console.log(`[AUTH-LOGIN-${requestId}] Headers:`, Object.fromEntries(webBffResponse.headers.entries()));

        // Handle non-200 responses
        if (!webBffResponse.ok) {
            let errorDetail = 'Login failed';
            try {
                const errorData = await webBffResponse.json();
                errorDetail = errorData.detail || errorData.message || errorDetail;
                console.error(`[AUTH-LOGIN-${requestId}] Web-bff error response:`, errorData);
            } catch (parseError) {
                const errorText = await webBffResponse.text();
                console.error(`[AUTH-LOGIN-${requestId}] Failed to parse error response as JSON:`, parseError);
                console.error(`[AUTH-LOGIN-${requestId}] Raw error response:`, errorText);
            }
            
            return json(
                { error: errorDetail },
                { status: webBffResponse.status }
            );
        }

        // Parse successful response
        const responseData = await webBffResponse.json();
        console.log(`[AUTH-LOGIN-${requestId}] Success response parsed`);
        console.log(`[AUTH-LOGIN-${requestId}] User ID: ${responseData.user?.id || 'missing'}`);
        console.log(`[AUTH-LOGIN-${requestId}] User name: ${responseData.user?.first_name || 'missing'} ${responseData.user?.last_name || 'missing'}`);
        console.log(`[AUTH-LOGIN-${requestId}] Access token present: ${!!responseData.access_token}`);
        console.log(`[AUTH-LOGIN-${requestId}] Workspaces count: ${responseData.workspaces?.length || 0}`);

        // Handle refresh token from Set-Cookie header
        const setCookieHeader = webBffResponse.headers.get('set-cookie');
        if (setCookieHeader) {
            console.log(`[AUTH-LOGIN-${requestId}] Set-Cookie header present:`, setCookieHeader);
            
            // Extract refresh token from Set-Cookie header
            const refreshTokenMatch = setCookieHeader.match(/refresh_token=([^;]+)/);
            if (refreshTokenMatch) {
                const refreshToken = refreshTokenMatch[1];
                console.log(`[AUTH-LOGIN-${requestId}] Refresh token extracted, setting SvelteKit cookie`);
                
                // Set refresh token as HttpOnly cookie in SvelteKit
                cookies.set('refresh_token', refreshToken, {
                    httpOnly: true,
                    secure: !dev, // Use secure in production
                    sameSite: dev ? 'lax' : 'none', // Cross-site for production
                    path: '/',
                    maxAge: 7 * 24 * 60 * 60, // 7 days
                    ...(dev ? {} : { domain: '.app.ergolux.io' }) // Domain for production
                });
                
                console.log(`[AUTH-LOGIN-${requestId}] Refresh token cookie set with secure=${!dev}, sameSite=${dev ? 'lax' : 'none'}`);
            } else {
                console.warn(`[AUTH-LOGIN-${requestId}] Set-Cookie header present but no refresh_token found`);
            }
        } else {
            console.warn(`[AUTH-LOGIN-${requestId}] No Set-Cookie header in web-bff response`);
        }

        // Return response without refresh token (it's now in HttpOnly cookie)
        const clientResponse = {
            user: responseData.user,
            access_token: responseData.access_token,
            token_type: responseData.token_type || 'bearer',
            expires_in: responseData.expires_in || 3600,
            workspaces: responseData.workspaces || [],
            last_accessed_workspace: responseData.last_accessed_workspace
        };

        const duration = Date.now() - startTime;
        console.log(`[AUTH-LOGIN-${requestId}] Login completed successfully in ${duration}ms`);
        console.log(`[AUTH-LOGIN-${requestId}] Response payload keys:`, Object.keys(clientResponse));

        return json(clientResponse);

    } catch (error) {
        const duration = Date.now() - startTime;
        console.error(`[AUTH-LOGIN-${requestId}] Login failed after ${duration}ms`);
        console.error(`[AUTH-LOGIN-${requestId}] Error:`, error);
        
        if (error instanceof TypeError && error.message.includes('fetch')) {
            console.error(`[AUTH-LOGIN-${requestId}] Network error - web-bff may be unavailable`);
            return json(
                { error: 'Authentication service unavailable' },
                { status: 502 }
            );
        }

        return json(
            { error: 'Internal server error during login' },
            { status: 500 }
        );
    }
};