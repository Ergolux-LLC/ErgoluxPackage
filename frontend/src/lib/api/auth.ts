/**
 * Authentication API endpoints
 * Handles login, logout, and auth-related operations
 */

import { apiClient, type ApiResponse } from './client';
import { browser } from '$app/environment';
import { memoryManager } from '$lib/memorymanager';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user?: any;
}

export interface AuthError {
  message: string;
  type: 'invalid_credentials' | 'not_activated' | 'system_unavailable' | 'network_error' | 'unknown';
}

/**
 * Parse and categorize authentication errors
 */
function parseAuthError(apiResponse: ApiResponse): AuthError {
  const error = apiResponse.error || apiResponse.detail || 'Login failed';
  
  // Invalid credentials
  if (
    error === "Login failed" ||
    error.includes("credentials") ||
    error.includes("Invalid")
  ) {
    return {
      message: "Incorrect email or password.",
      type: 'invalid_credentials'
    };
  }
  
  // Account not activated
  if (
    error.includes("not active") ||
    error.includes("activation")
  ) {
    return {
      message: "This account has not been activated. Please check your email for an activation link.",
      type: 'not_activated'
    };
  }
  
  // System unavailable
  if (
    error.includes("Database unavailable") ||
    error.includes("Service temporarily unavailable") ||
    apiResponse.status === 503
  ) {
    return {
      message: "The system is temporarily unavailable. Please try again in a moment.",
      type: 'system_unavailable'
    };
  }
  
  // Internal server error
  if (error === "Internal server error") {
    return {
      message: "Something went wrong on our end. Please try again or contact support if the issue persists.",
      type: 'unknown'
    };
  }
  
  // Network error
  if (apiResponse.status === 0) {
    return {
      message: "Network error. Please try again.",
      type: 'network_error'
    };
  }
  
  // Default fallback
  return {
    message: error,
    type: 'unknown'
  };
}

/**
 * Login user with email and password
 */
export async function login(credentials: LoginRequest): Promise<{
  success: boolean;
  data?: LoginResponse;
  error?: AuthError;
}> {
  console.log("Login attempt started with email:", credentials.email);
  
  const response = await apiClient.post<LoginResponse>('/auth/login', credentials);
  
  if (response.success && response.data) {
    console.log("Login successful!");
    
    // Store the access token
    if (response.data.access_token && browser) {
      localStorage.setItem("access_token", response.data.access_token);
      console.log("Access token stored in localStorage");
    }
    
    // Initialize memory manager with user data
    if (browser) {
      memoryManager.onLoginSuccess(response.data);
      console.log("Memory manager initialized with user data");
    }
    
    return {
      success: true,
      data: response.data
    };
  } else {
    const authError = parseAuthError(response);
    console.warn("Login failed:", authError.message);
    
    return {
      success: false,
      error: authError
    };
  }
}

/**
 * Logout user and clear stored tokens
 */
export async function logout(): Promise<void> {
  // Clear memory manager data
  if (browser) {
    memoryManager.onLogout();
    console.log("Memory manager cleared user data");
  }
  
  // Clear local storage
  if (browser) {
    localStorage.removeItem('access_token');
    console.log("Access token removed from localStorage");
  }
  
  // Optionally call logout endpoint to invalidate server-side session
  try {
    await apiClient.post('/auth/logout');
  } catch (error) {
    console.warn("Logout endpoint failed, but local tokens cleared:", error);
  }
}

/**
 * Check if user is currently authenticated
 */
export function isAuthenticated(): boolean {
  if (!browser) return false;
  
  // Use memory manager for instant check (sub-millisecond)
  const memoryAuth = memoryManager.isAuthenticated();
  if (memoryAuth) {
    return true;
  }
  
  // Fallback to localStorage if memory manager doesn't have data
  return !!localStorage.getItem('access_token');
}

/**
 * Get stored access token
 */
export function getAccessToken(): string | null {
  if (!browser) return null;
  return localStorage.getItem('access_token');
}

/**
 * Get current user profile data (instant from memory)
 */
export function getCurrentUser() {
  if (!browser) return null;
  return memoryManager.getCurrentUser();
}

/**
 * Redirect to dashboard after successful login
 */
export function redirectToWorkspace(): void {
  if (browser) {
    setTimeout(() => {
      window.location.href = `${window.location.protocol}//${window.location.host}/dashboard`;
    }, 1000);
  }
}