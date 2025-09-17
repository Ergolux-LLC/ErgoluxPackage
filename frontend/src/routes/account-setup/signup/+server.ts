import type { RequestHandler } from '@sveltejs/kit';
import { API_BASE_URL, DEFAULT_HEADERS } from '$lib/api/config';

export const POST: RequestHandler = async ({ request }) => {
  try {
    // Parse the incoming request as JSON
    const json = await request.json();
    // Forward the request to the backend as JSON
    const res = await fetch(`${API_BASE_URL}/account-setup/signup`, {
      method: 'POST',
      headers: {
        ...DEFAULT_HEADERS,
      },
      body: JSON.stringify(json),
    });
    const data = await res.text();
    return new Response(data, {
      status: res.status,
      headers: { 'Content-Type': res.headers.get('Content-Type') || 'application/json' },
    });
  } catch (error: any) {
    // Log the error for debugging
    console.error('[Proxy Error]', error);
    return new Response(JSON.stringify({ error: 'Proxy error', details: error?.message || error }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
