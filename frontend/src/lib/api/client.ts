import { config, getApiUrl, devLog, devError } from '$lib/config/environment';

// Enhanced API client with environment-aware configuration
class ApiClient {
  private baseUrl: string;
  private humanServiceUrl: string;
  private timeout: number;

  constructor() {
    this.baseUrl = config.api.baseUrl;
    this.humanServiceUrl = config.api.humanServiceUrl;
    this.timeout = config.api.timeout;
    devLog('API Client initialized', { 
      baseUrl: this.baseUrl, 
      humanServiceUrl: this.humanServiceUrl,
      timeout: this.timeout 
    });
  }

  private async request(endpoint: string, options: RequestInit = {}, useHumanService = false): Promise<any> {
    const baseUrl = useHumanService ? this.humanServiceUrl : this.baseUrl;
    const url = `${baseUrl}${endpoint}`;
    const requestOptions: RequestInit = {
      ...options,
      credentials: 'include', // Always include cookies
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    // Add Authorization header if we have an access token
    const accessToken = this.getAccessToken();
    if (accessToken) {
      requestOptions.headers = {
        ...requestOptions.headers,
        'Authorization': `Bearer ${accessToken}`,
      };
      console.log('[API CLIENT] Adding Authorization header with token:', accessToken.substring(0, 12) + '...');
    } else {
      console.log('[API CLIENT] No access token available - making unauthenticated request');
    }

    // Add development headers if in dev mode
    if (config.isDevelopment) {
      requestOptions.headers = {
        ...requestOptions.headers,
        'X-Dev-Mode': 'true',
        'X-App-Version': config.app.version,
      };
    }

    devLog('API Request', { url, method: options.method || 'GET', options: requestOptions });
    console.log('[API CLIENT] request:', { url, endpoint, options: requestOptions });
    console.log('[API CLIENT] credentials:', requestOptions.credentials);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      const response = await fetch(url, {
        ...requestOptions,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const contentType = response.headers.get('content-type');
      let text = '';
      let data: any = null;

      try {
        text = await response.text();
        data = text ? JSON.parse(text) : {};
      } catch (e) {
        devError('JSON parse error', e);
        console.error('[API CLIENT] JSON parse error:', e, 'Raw response:', text);
        return {
          success: false,
          error: 'Invalid server response',
          debug: {
            status: response.status,
            statusText: response.statusText,
            contentType: contentType ?? undefined,
            rawResponse: text,
          },
        };
      }

      if (!response.ok) {
        devError('HTTP error response', { status: response.status, data });
        console.error('[API CLIENT] HTTP error response:', response.status, data);
        return {
          success: false,
          error: data?.error || data?.message || `Server error: ${response.status} ${response.statusText}`,
          debug: {
            status: response.status,
            statusText: response.statusText,
            contentType: contentType ?? undefined,
            rawResponse: text,
          },
        };
      }

      devLog('API Response', { url, status: response.status, data });
      console.log('[API CLIENT] API Response:', { url, status: response.status, data });
      // For successful HTTP responses, return the data as-is
      // The data may still contain success: false for business logic errors
      return data;
    } catch (error) {
      devError('API Error', { url, error });
      console.error('[API CLIENT] API Error:', error, 'URL:', url);
      if (error instanceof Error && error.name === 'AbortError') {
        return {
          success: false,
          error: 'Request timeout. Please try again.',
        };
      }
      return {
        success: false,
        error: 'Network or server error. Please try again.',
      };
    }
  }

  // Authentication endpoints
  async login(email: string, password: string) {
    // Web-bff expects form data for login
    const formData = new FormData();
    formData.append('email', email);
    formData.append('password', password);
    
    const result = await this.request('/auth/login', {
      method: 'POST',
      headers: {}, // Remove Content-Type to let browser set it for FormData
      body: formData,
    });

    // Handle new authentication format
    if (result && result.access_token) {
      // Store access token in memory/localStorage for this session
      if (typeof window !== 'undefined') {
        // Store in sessionStorage (cleared when browser closes)
        sessionStorage.setItem('access_token', result.access_token);
        sessionStorage.setItem('token_type', result.token_type || 'bearer');
        sessionStorage.setItem('expires_in', (result.expires_in || 3600).toString());
        
        devLog('Access token stored in session', {
          token_type: result.token_type,
          expires_in: result.expires_in
        });
      }
    }

    return result;
  }

  async logout() {
    const result = await this.request('/auth/logout', {
      method: 'POST',
    });

    // Clear stored access token
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('token_type');
      sessionStorage.removeItem('expires_in');
      devLog('Access token cleared from session');
    }

    return result;
  }

  // Get current access token from memory
  getAccessToken(): string | null {
    if (typeof window !== 'undefined') {
      return sessionStorage.getItem('access_token');
    }
    return null;
  }

  // Check if user has valid authentication
  // Debugging method to verify token storage
  debugTokenStorage() {
    if (typeof window === 'undefined') {
      console.log('❌ No window object - running in SSR');
      return null;
    }

    const accessToken = sessionStorage.getItem('access_token');
    const tokenType = sessionStorage.getItem('token_type');
    const expiresIn = sessionStorage.getItem('expires_in');
    
    const debug = {
      hasAccessToken: !!accessToken,
      accessTokenPreview: accessToken ? accessToken.substring(0, 12) + '...' : null,
      tokenType: tokenType,
      expiresIn: expiresIn,
      isAuthenticated: this.isAuthenticated(),
      getAccessTokenWorks: !!this.getAccessToken(),
      sessionStorageKeys: Object.keys(sessionStorage),
      currentTime: new Date().toISOString()
    };

    console.log('🔍 TOKEN STORAGE DEBUG:', debug);
    return debug;
  }

  isAuthenticated(): boolean {
    const token = this.getAccessToken();
    return !!token;
  }

  async validateAuth() {
    return this.request('/auth/validate', {
      method: 'GET',
    });
  }

  // Account Setup endpoints
  async signup(email: string, workspace_id?: number | null) {
    const body: any = { email };
    if (workspace_id) {
      body.workspace_id = workspace_id;
    }
    
    return this.request('/account-setup/signup', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async confirmCode(code: string) {
    return this.request('/account-setup/confirm', {
      method: 'POST',
      body: JSON.stringify({ code }),
    });
  }

  async getEmailStatus(email: string) {
    return this.request(`/account-setup/status/${encodeURIComponent(email)}`);
  }

  async getEmailForCode(code: string) {
    return this.request(`/account-setup/email-for-code/${encodeURIComponent(code)}`);
  }

  async getAllEmails() {
    return this.request('/account-setup/emails');
  }

  // User Setup endpoints
  async completeUserSetup(userData: {
    first_name: string;
    last_name: string;
    email: string;
    password: string;
    workspace_id?: string | null;
    new_workspace_name?: string | null;
  }) {
    const result = await this.request('/user-setup/complete', {
      method: 'POST',
      body: JSON.stringify(userData),
    });

    // Handle new authentication format - if setup includes login
    if (result && result.access_token) {
      console.log('🔑 SETUP RESPONSE CONTAINS ACCESS TOKEN - Starting storage process');
      console.log('Access token preview:', result.access_token.substring(0, 12) + '...');
      console.log('Token type:', result.token_type);
      console.log('Expires in:', result.expires_in);

      // Store access token in memory/localStorage for this session
      if (typeof window !== 'undefined') {
        console.log('📱 Browser environment confirmed - storing tokens in sessionStorage');
        
        // Check before storage
        const beforeStorage = !!sessionStorage.getItem('access_token');
        console.log('SessionStorage before:', { has_token: beforeStorage });

        sessionStorage.setItem('access_token', result.access_token);
        sessionStorage.setItem('token_type', result.token_type || 'bearer');
        sessionStorage.setItem('expires_in', (result.expires_in || 3600).toString());
        
        // Verify storage worked
        const afterStorage = !!sessionStorage.getItem('access_token');
        const storedToken = sessionStorage.getItem('access_token');
        console.log('SessionStorage after:', { 
          has_token: afterStorage,
          stored_token_preview: storedToken ? storedToken.substring(0, 12) + '...' : 'NONE',
          api_authenticated: this.isAuthenticated()
        });
        
        devLog('✅ Access token stored after setup completion - CONFIRMED', {
          token_type: result.token_type,
          expires_in: result.expires_in,
          storage_successful: afterStorage,
          client_authenticated: this.isAuthenticated()
        });

        console.log('🎉 TOKEN STORAGE COMPLETE - User should now be automatically logged in');
      } else {
        console.log('❌ No window object - cannot store token (likely SSR)');
      }
    } else {
      console.log('❌ No access_token in setup response - no automatic login available');
      console.log('Setup response keys:', result ? Object.keys(result) : 'No result');
    }

    return result;
  }

  async validateWorkspace(workspace_id: string) {
    return this.request(`/user-setup/workspaces/${encodeURIComponent(workspace_id)}/validate`);
  }

  // Workspace endpoints
  async getWorkspaces(name?: string, limit = 20, offset = 0) {
    const params = new URLSearchParams();
    if (name) params.append('name', name);
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());
    
    return this.request(`/workspaces?${params.toString()}`);
  }

  async createWorkspace(name: string) {
    return this.request('/workspaces', {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
  }

  async validateWorkspaceForSignup(workspace_id: number) {
    return this.request(`/user-setup/workspaces/${workspace_id}/validate`);
  }

  // Human Directory endpoints (uses human service)
  async getHumans(workspace_id: string, params?: {
    created_by?: string;
    limit?: number;
    offset?: number;
    q?: string;
    sortBy?: string;
    sortDirection?: 'asc' | 'desc';
    fields?: string;
  }) {
    const searchParams = new URLSearchParams();
    searchParams.append('workspace_id', workspace_id);
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    return this.request(`/views/directory?${searchParams.toString()}`, {}, true);
  }

  async createHuman(data: {
    workspace_id: string;
    created_by: string;
    first_name: string;
    last_name: string;
    middle_name?: string;
    email?: string;
    phone_number?: string;
    linkedin_url?: string;
  }) {
    return this.request('/views/directory', {
      method: 'POST',
      body: JSON.stringify(data),
    }, true);
  }

  async getHuman(human_id: string) {
    return this.request(`/views/directory/${encodeURIComponent(human_id)}`, {}, true);
  }

  async updateHuman(id: string, data: any) {
    return this.request(`/views/directory/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }, true);
  }

  async deleteHuman(id: string, workspace_id: string, created_by: string) {
    return this.request(`/views/directory/${encodeURIComponent(id)}`, {
      method: 'DELETE',
      body: JSON.stringify({ workspace_id, created_by }),
    }, true);
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }

  // Development endpoints
  async checkCookies() {
    return this.request('/dev/cookie-check');
  }
}

// Create singleton instance
const apiClient = new ApiClient();

// Export singleton instance

export { apiClient };

// Create global debug functions for testing (browser only)
if (typeof window !== 'undefined') {
  (window as any).debugApiClient = () => {
    return apiClient.debugTokenStorage();
  };
  
  (window as any).testTokenStorage = () => {
    console.log('=== TOKEN STORAGE TEST ===');
    const debug = apiClient.debugTokenStorage();
    
    if (debug?.hasAccessToken) {
      console.log('✅ Access token is present and stored correctly');
      console.log('✅ API client reports authenticated:', debug.isAuthenticated);
      console.log('✅ getAccessToken() works:', debug.getAccessTokenWorks);
    } else {
      console.log('❌ No access token found in storage');
      console.log('Available sessionStorage keys:', debug?.sessionStorageKeys);
    }
    
    return debug;
  };
}

// Export individual functions for convenience
export const {
  login,
  logout,
  validateAuth,
  getAccessToken,
  isAuthenticated,
  signup,
  confirmCode,
  getEmailStatus,
  getEmailForCode,
  getAllEmails,
  completeUserSetup,
  validateWorkspace,
  getWorkspaces,
  createWorkspace,
  validateWorkspaceForSignup,
  getHumans,
  createHuman,
  getHuman,
  updateHuman,
  deleteHuman,
  healthCheck,
  checkCookies,
} = apiClient;
