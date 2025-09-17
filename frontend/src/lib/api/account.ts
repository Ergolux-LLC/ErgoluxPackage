/**
 * Account API Client
 * 
 * This module provides functions for interacting with the Account API endpoints
 * through the BFF (Backend For Frontend) service.
 */

// Import shared API configuration
import { API_BASE_URL, DEFAULT_HEADERS, generateRequestId } from './config';

const EMAIL_FOR_CODE_ENDPOINT = '/account-setup/email-for-code';

/**
 * Interface for email code verification response
 */
export interface EmailForCodeResponse {
  email: string;
  valid: boolean;
  message?: string;
}

/**
 * Verify an activation code to get associated email
 * 
 * @param code - The activation code to verify
 * @returns Promise resolving to the verification result
 */
export async function verifyActivationCode(code: string): Promise<{ isValid: boolean, email: string | null, error?: string }> {
  // Special case for test code
  if (code === 'BUTTS') {
    console.log('Using special test activation code');
    return {
      isValid: true,
      email: 'special@example.com'
    };
  }

  try {
    // Prepare the API request
    const apiUrl = `${API_BASE_URL}${EMAIL_FOR_CODE_ENDPOINT}`;
    
    console.log(`Verifying activation code at: ${apiUrl}`);
    
    // Make the API call
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        ...DEFAULT_HEADERS,
        'X-Request-ID': generateRequestId()
      },
      body: JSON.stringify({ code })
    });
    
    // Parse the response
    const responseText = await response.text();
    
    // Try to parse as JSON
    let data: EmailForCodeResponse;
    try {
      data = JSON.parse(responseText) as EmailForCodeResponse;
    } catch (error) {
      console.error('Failed to parse API response:', error);
      return {
        isValid: false,
        email: null,
        error: 'Failed to parse API response'
      };
    }
    
    // Check if the response was successful
    if (!response.ok || !data.valid) {
      return {
        isValid: false,
        email: null,
        error: data.message || 'Invalid or expired activation code'
      };
    }
    
    // Code is valid
    return {
      isValid: true,
      email: data.email
    };
    
  } catch (error) {
    // Handle any unexpected errors
    console.error('Unexpected error during activation code verification:', error);
    
    return {
      isValid: false,
      email: null,
      error: `Unexpected error: ${error instanceof Error ? error.message : String(error)}`
    };
  }
}
