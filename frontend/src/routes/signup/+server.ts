import type { RequestHandler } from '@sveltejs/kit';
import { serverConfig } from '$lib/config/server';

export const POST: RequestHandler = async ({ request }) => {
  try {
    const body = await request.text();
    const res = await fetch(`${serverConfig.api.baseUrl}/account-setup/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
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
