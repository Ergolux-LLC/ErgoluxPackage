<script>
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api/client';
  
  let authStatus = null;
  let userInfo = null;
  let tokenInfo = null;
  let loadingAuth = true;
  let authError = null;

  onMount(async () => {
    // Get current authentication status
    try {
      const authResult = await apiClient.validateAuth();
      authStatus = authResult;
      userInfo = authResult?.user;
      
      // Get token information
      tokenInfo = {
        hasToken: !!apiClient.getAccessToken(),
        tokenPreview: apiClient.getAccessToken()?.substring(0, 12) + '...',
        isAuthenticated: apiClient.isAuthenticated(),
        sessionStorage: {
          accessToken: !!sessionStorage.getItem('access_token'),
          tokenType: sessionStorage.getItem('token_type'),
          expiresIn: sessionStorage.getItem('expires_in')
        }
      };
      
      console.log('Dashboard - Auth Status:', authStatus);
      console.log('Dashboard - Token Info:', tokenInfo);
      
    } catch (error) {
      console.error('Dashboard - Auth verification failed:', error);
      authError = error.message;
    } finally {
      loadingAuth = false;
    }
  });

  function refreshAuthStatus() {
    loadingAuth = true;
    authError = null;
    // Re-run the onMount logic
    onMount();
  }

  function logout() {
    sessionStorage.clear();
    window.location.href = '/login';
  }
</script>

<svelte:head>
  <title>Dashboard - ErgolUX CRM</title>
</svelte:head>

<div class="dashboard-container">
  <header class="dashboard-header">
    <h1>🎉 Dashboard - Authentication Successful!</h1>
    <p class="welcome-message">
      Welcome to your protected dashboard. This page confirms that authentication is working correctly.
    </p>
  </header>

  <main class="dashboard-content">
    <!-- Authentication Status Section -->
    <section class="auth-section">
      <h2>🔐 Authentication Verification</h2>
      
      {#if loadingAuth}
        <div class="loading">
          <p>🔍 Verifying authentication status...</p>
        </div>
      {:else if authError}
        <div class="error-panel">
          <h3>❌ Authentication Error</h3>
          <p>{authError}</p>
          <button on:click={refreshAuthStatus} class="retry-btn">Retry</button>
          <button on:click={logout} class="logout-btn">Go to Login</button>
        </div>
      {:else}
        <div class="success-panel">
          <div class="verification-grid">
            <!-- User Information -->
            <div class="info-card">
              <h3>👤 User Information</h3>
              {#if userInfo}
                <div class="info-item">
                  <strong>User ID:</strong>
                  <code>{userInfo.id || userInfo.user_id || 'N/A'}</code>
                </div>
                <div class="info-item">
                  <strong>Email:</strong>
                  <code>{userInfo.email || 'N/A'}</code>
                </div>
                <div class="info-item">
                  <strong>Status:</strong>
                  <span class="status success">✅ Authenticated</span>
                </div>
              {:else}
                <p class="no-data">No user information available</p>
              {/if}
            </div>

            <!-- Token Information -->
            <div class="info-card">
              <h3>🎫 Token Status</h3>
              {#if tokenInfo}
                <div class="info-item">
                  <strong>Access Token:</strong>
                  <span class="status {tokenInfo.hasToken ? 'success' : 'error'}">
                    {tokenInfo.hasToken ? '✅ Present' : '❌ Missing'}
                  </span>
                  {#if tokenInfo.hasToken}
                    <code class="token-preview">{tokenInfo.tokenPreview}</code>
                  {/if}
                </div>
                <div class="info-item">
                  <strong>API Client Status:</strong>
                  <span class="status {tokenInfo.isAuthenticated ? 'success' : 'error'}">
                    {tokenInfo.isAuthenticated ? '✅ Authenticated' : '❌ Not Authenticated'}
                  </span>
                </div>
                <div class="info-item">
                  <strong>Token Type:</strong>
                  <code>{tokenInfo.sessionStorage.tokenType || 'N/A'}</code>
                </div>
                <div class="info-item">
                  <strong>Expires In:</strong>
                  <code>{tokenInfo.sessionStorage.expiresIn || 'N/A'} seconds</code>
                </div>
              {/if}
            </div>

            <!-- Session Storage Info -->
            <div class="info-card">
              <h3>💾 Session Storage</h3>
              <div class="info-item">
                <strong>Access Token Stored:</strong>
                <span class="status {tokenInfo?.sessionStorage.accessToken ? 'success' : 'error'}">
                  {tokenInfo?.sessionStorage.accessToken ? '✅ Yes' : '❌ No'}
                </span>
              </div>
              <div class="info-item">
                <strong>Storage Keys:</strong>
                <code>{Object.keys(sessionStorage).join(', ') || 'None'}</code>
              </div>
            </div>

            <!-- API Response -->
            <div class="info-card full-width">
              <h3>🌐 Raw API Response</h3>
              <div class="json-display">
                <pre><code>{JSON.stringify(authStatus, null, 2)}</code></pre>
              </div>
            </div>
          </div>
        </div>
      {/if}
    </section>

    <!-- Action Buttons -->
    <section class="actions-section">
      <h2>🚀 Available Actions</h2>
      <div class="action-buttons">
        <button on:click={refreshAuthStatus} class="primary-btn">
          🔄 Refresh Auth Status
        </button>
        <button on:click={() => window.location.href = '/directory'} class="secondary-btn">
          📁 Go to Directory
        </button>
        <button on:click={logout} class="danger-btn">
          🚪 Logout
        </button>
      </div>
    </section>

    <!-- Setup Journey Info -->
    <section class="journey-section">
      <h2>🛣️ Authentication Journey</h2>
      <div class="journey-steps">
        <div class="step completed">
          <span class="step-number">1</span>
          <div class="step-content">
            <h4>Account Setup Completed</h4>
            <p>User account and workspace created successfully</p>
          </div>
        </div>
        <div class="step completed">
          <span class="step-number">2</span>
          <div class="step-content">
            <h4>Access Token Received</h4>
            <p>Server issued access token and refresh token cookie</p>
          </div>
        </div>
        <div class="step completed">
          <span class="step-number">3</span>
          <div class="step-content">
            <h4>Token Stored in Session</h4>
            <p>Access token saved to sessionStorage for API calls</p>
          </div>
        </div>
        <div class="step completed">
          <span class="step-number">4</span>
          <div class="step-content">
            <h4>Authentication Verified</h4>
            <p>Server validated token and returned user information</p>
          </div>
        </div>
        <div class="step completed">
          <span class="step-number">5</span>
          <div class="step-content">
            <h4>Redirected to Dashboard</h4>
            <p>Successfully accessed protected route without manual login</p>
          </div>
        </div>
      </div>
    </section>
  </main>
</div>

<style>
  :global(body) {
    background: #181a1b !important;
    color: #f3f3f3 !important;
    font-family: system-ui, sans-serif;
    margin: 0;
    padding: 0;
  }

  .dashboard-container {
    min-height: 100vh;
    background: #181a1b;
    color: #f3f3f3;
  }

  .dashboard-header {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    padding: 2rem;
    text-align: center;
    color: white;
  }

  .dashboard-header h1 {
    margin: 0 0 1rem 0;
    font-size: 2.5rem;
    font-weight: bold;
  }

  .welcome-message {
    font-size: 1.1rem;
    opacity: 0.9;
    margin: 0;
  }

  .dashboard-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }

  .auth-section, .actions-section, .journey-section {
    margin-bottom: 3rem;
  }

  .auth-section h2, .actions-section h2, .journey-section h2 {
    color: #3b82f6;
    margin-bottom: 1.5rem;
    border-bottom: 2px solid #3b82f6;
    padding-bottom: 0.5rem;
  }

  .loading {
    text-align: center;
    padding: 2rem;
    color: #b3e5fc;
  }

  .error-panel {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid #ef4444;
    border-radius: 8px;
    padding: 1.5rem;
    text-align: center;
  }

  .success-panel {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid #22c55e;
    border-radius: 8px;
    padding: 1.5rem;
  }

  .verification-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  .info-card {
    background: #23272b;
    border-radius: 8px;
    padding: 1.5rem;
    border: 1px solid #374151;
  }

  .info-card.full-width {
    grid-column: 1 / -1;
  }

  .info-card h3 {
    margin: 0 0 1rem 0;
    color: #3b82f6;
    font-size: 1.1rem;
  }

  .info-item {
    margin: 0.75rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .info-item strong {
    min-width: 120px;
    color: #d1d5db;
  }

  .status {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.9rem;
    font-weight: bold;
  }

  .status.success {
    background: rgba(34, 197, 94, 0.2);
    color: #22c55e;
  }

  .status.error {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
  }

  .token-preview {
    font-size: 0.8rem;
    opacity: 0.7;
  }

  .json-display {
    background: #1a1d21;
    border-radius: 4px;
    padding: 1rem;
    border: 1px solid #374151;
  }

  .json-display pre {
    margin: 0;
    font-size: 0.8rem;
    overflow-x: auto;
  }

  .action-buttons {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .primary-btn, .secondary-btn, .danger-btn, .retry-btn, .logout-btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.2s;
  }

  .primary-btn {
    background: #3b82f6;
    color: white;
  }

  .primary-btn:hover {
    background: #2563eb;
  }

  .secondary-btn {
    background: #6b7280;
    color: white;
  }

  .secondary-btn:hover {
    background: #4b5563;
  }

  .danger-btn, .logout-btn {
    background: #ef4444;
    color: white;
  }

  .danger-btn:hover, .logout-btn:hover {
    background: #dc2626;
  }

  .retry-btn {
    background: #f59e0b;
    color: white;
  }

  .retry-btn:hover {
    background: #d97706;
  }

  .journey-steps {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .step {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: #23272b;
    border-radius: 8px;
    border: 1px solid #374151;
  }

  .step.completed {
    border-color: #22c55e;
    background: rgba(34, 197, 94, 0.1);
  }

  .step-number {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #22c55e;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    flex-shrink: 0;
  }

  .step-content h4 {
    margin: 0 0 0.5rem 0;
    color: #22c55e;
  }

  .step-content p {
    margin: 0;
    color: #d1d5db;
    font-size: 0.9rem;
  }

  .no-data {
    color: #9ca3af;
    text-align: center;
    font-style: italic;
  }

  @media (max-width: 768px) {
    .verification-grid {
      grid-template-columns: 1fr;
    }
    
    .action-buttons {
      flex-direction: column;
    }
  }
</style>
