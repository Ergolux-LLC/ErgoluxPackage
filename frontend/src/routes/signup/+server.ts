import type { RequestHandler } from '@sveltejs/kit';
import { API_BASE_URL, DEFAULT_HEADERS } from '$lib/api/config';

export const POST: RequestHandler = async ({ request }) => {
  try {
    const body = await request.text();
    const res = await fetch(`${API_BASE_URL}/account-setup/signup`, {
      method: 'POST',
      headers: DEFAULT_HEADERS,
      body,
    });
    const data = await res.text();
    return new Response(data, {
      status: res.status,
      headers: { 'Content-Type': res.headers.get('Content-Type') || 'application/json' },
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Proxy error', details: error }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
