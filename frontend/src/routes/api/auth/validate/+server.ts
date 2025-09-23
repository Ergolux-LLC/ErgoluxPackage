import { json, type RequestHandler } from '@sveltejs/kit';

const WEB_BFF_URL = 'http://web_bff:8000';

export const GET: RequestHandler = async ({ request, cookies }) => {
    const startTime = Date.now();
    const requestId = crypto.randomUUID().substring(0, 8);
    
    console.log(`[AUTH-VALIDATE-${requestId}] Starting token validation at ${new Date().toISOString()}`);
    
    try {
        // Get authorization header (access token) and refresh token from cookies
        const authHeader = request.headers.get('authorization');
        const refreshToken = cookies.get('refresh_token');
        
        console.log(`[AUTH-VALIDATE-${requestId}] Auth header present: ${!!authHeader}`);
        console.log(`[AUTH-VALIDATE-${requestId}] Refresh token cookie present: ${!!refreshToken}`);
        
        if (!authHeader) {
            console.error(`[AUTH-VALIDATE-${requestId}] No Authorization header provided`);
            return json(
                { error: 'Authorization header required. Use Bearer <access_token> format.' },
                { status: 401 }
            );
        }

        if (!authHeader.startsWith('Bearer ')) {
            console.error(`[AUTH-VALIDATE-${requestId}] Invalid Authorization header format`);
            return json(
                { error: 'Invalid Authorization header format. Use Bearer <access_token>.' },
                { status: 401 }
            );
        }

        const accessToken = authHeader.substring(7); // Remove 'Bearer ' prefix
        console.log(`[AUTH-VALIDATE-${requestId}] Access token extracted from Authorization header`);
        console.log(`[AUTH-VALIDATE-${requestId}] Token length: ${accessToken.length}`);

        // Prepare headers for web-bff validation request
        const webBffHeaders: Record<string, string> = {
            'Authorization': `Bearer ${accessToken}`,
            'Accept': 'application/json',
            'User-Agent': `SvelteKit-Frontend-${requestId}`
        };

        console.log(`[AUTH-VALIDATE-${requestId}] Sending validation request to web-bff`);
        console.log(`[AUTH-VALIDATE-${requestId}] Target URL: ${WEB_BFF_URL}/auth/validate`);

        // Make validation request to web-bff
        const webBffResponse = await fetch(`${WEB_BFF_URL}/auth/validate`, {
            method: 'GET',
            headers: webBffHeaders
        });

        const duration = Date.now() - startTime;
        console.log(`[AUTH-VALIDATE-${requestId}] Web-bff response received in ${duration}ms`);
        console.log(`[AUTH-VALIDATE-${requestId}] Status: ${webBffResponse.status} ${webBffResponse.statusText}`);
        console.log(`[AUTH-VALIDATE-${requestId}] Headers:`, Object.fromEntries(webBffResponse.headers.entries()));

        if (!webBffResponse.ok) {
            let errorDetail = 'Token validation failed';
            try {
                const errorData = await webBffResponse.json();
                errorDetail = errorData.detail || errorData.message || errorDetail;
                console.error(`[AUTH-VALIDATE-${requestId}] Web-bff validation error:`, errorData);
            } catch (parseError) {
                const errorText = await webBffResponse.text();
                console.error(`[AUTH-VALIDATE-${requestId}] Failed to parse error response:`, parseError);
                console.error(`[AUTH-VALIDATE-${requestId}] Raw error response:`, errorText);
            }
            
            if (webBffResponse.status === 401) {
                console.log(`[AUTH-VALIDATE-${requestId}] Access token expired or invalid`);
                if (refreshToken) {
                    console.log(`[AUTH-VALIDATE-${requestId}] Refresh token available for potential refresh`);
                    return json(
                        { 
                            error: errorDetail,
                            can_refresh: true,
                            message: 'Access token expired. Frontend should attempt token refresh.'
                        },
                        { status: 401 }
                    );
                }
            }
            
            return json(
                { error: errorDetail },
                { status: webBffResponse.status }
            );
        }

        // Parse successful validation response
        const validationData = await webBffResponse.json();
        console.log(`[AUTH-VALIDATE-${requestId}] Validation successful`);
        console.log(`[AUTH-VALIDATE-${requestId}] User ID: ${validationData.user?.id || 'missing'}`);
        console.log(`[AUTH-VALIDATE-${requestId}] User email: ${validationData.user?.email || 'missing'}`);

        console.log(`[AUTH-VALIDATE-${requestId}] Token validation completed successfully in ${Date.now() - startTime}ms`);

        return json({
            valid: true,
            user: validationData.user,
            message: 'Token is valid'
        });

    } catch (error) {
        const duration = Date.now() - startTime;
        console.error(`[AUTH-VALIDATE-${requestId}] Validation failed after ${duration}ms`);
        console.error(`[AUTH-VALIDATE-${requestId}] Error:`, error);
        
        if (error instanceof TypeError && error.message.includes('fetch')) {
            console.error(`[AUTH-VALIDATE-${requestId}] Network error - web-bff may be unavailable`);
            return json(
                { error: 'Authentication service unavailable' },
                { status: 502 }
            );
        }

        return json(
            { error: 'Internal server error during validation' },
            { status: 500 }
        );
    }
};