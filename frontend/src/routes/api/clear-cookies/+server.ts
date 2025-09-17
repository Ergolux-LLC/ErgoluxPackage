import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ cookies }) => {
  try {
    console.log('[CLEAR-COOKIES] Starting cookie clearing process');
    
    // List of common cookie names to clear
    const cookiesToClear = [
      'access_token',
      'refresh_token', 
      'test_cookie',
      'access_token_manual',
      'refresh_token_manual',
      'test1',
      'test2',
      'manual1',
      'manual2'
    ];
    
    let clearedCount = 0;
    
    // Clear each cookie by setting it to expire
    for (const cookieName of cookiesToClear) {
      try {
        // Clear for multiple path/domain combinations
        cookies.delete(cookieName, { path: '/' });
        cookies.delete(cookieName, { path: '/', domain: 'localhost' });
        cookies.delete(cookieName, { path: '/', domain: '.localhost' });
        clearedCount++;
        console.log(`[CLEAR-COOKIES] Cleared cookie: ${cookieName}`);
      } catch (error) {
        console.log(`[CLEAR-COOKIES] Failed to clear cookie ${cookieName}:`, error);
      }
    }
    
    console.log(`[CLEAR-COOKIES] Clearing process complete. Attempted to clear ${clearedCount} cookies`);
    
    return json({ 
      success: true, 
      message: `Cleared ${clearedCount} cookies server-side`,
      clearedCookies: cookiesToClear
    });
  } catch (error) {
    console.error('[CLEAR-COOKIES] Failed to clear cookies:', error);
    return json({ 
      success: false, 
      error: 'Failed to clear cookies server-side' 
    }, { status: 500 });
  }
};
