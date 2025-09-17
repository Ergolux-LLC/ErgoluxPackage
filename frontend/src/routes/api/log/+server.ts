import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request }) => {
  try {
    const { level, message, data, timestamp } = await request.json();
    
    // Log to server console (terminal)
    const logPrefix = `[${timestamp}]`;
    const logMessage = data ? `${message} | ${JSON.stringify(data)}` : message;
    
    switch (level) {
      case 'error':
        console.error(`${logPrefix} ${logMessage}`);
        break;
      case 'warn':
        console.warn(`${logPrefix} ${logMessage}`);
        break;
      case 'info':
      default:
        console.log(`${logPrefix} ${logMessage}`);
        break;
    }
    
    return json({ success: true });
  } catch (error) {
    console.error('[LOG-API] Failed to process log:', error);
    return json({ success: false, error: 'Failed to process log' }, { status: 500 });
  }
};
