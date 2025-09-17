<script lang="ts">
  import { onMount } from "svelte";
  import { config } from "$lib/config/environment";

  let loading = false;
  let cookieTestResponse: any = null;
  let cookieCheckResponse: any = null;
  let cookieHeadersResponse: any = null;
  let error: string | null = null;
  let currentBrowserCookies: string = "";

  // Update browser cookies display
  function updateBrowserCookiesDisplay() {
    currentBrowserCookies = document.cookie || "No cookies";
  }

  // Server-side logging function
  function serverLog(message: string, data?: any) {
    const timestamp = new Date().toISOString();
    const logData = data ? ` | Data: ${JSON.stringify(data)}` : "";
    console.log(`[${timestamp}] [COOKIE-UI] ${message}${logData}`);

    // Also try to send to server for terminal logging
    fetch("/api/log", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        level: "info",
        message: `[COOKIE-UI] ${message}`,
        data: data || null,
        timestamp,
      }),
    }).catch(() => {}); // Ignore errors for logging
  }

  async function clearAllCookies() {
    serverLog("Clearing all cookies for clean test");

    // Client-side cookie clearing (for non-HttpOnly cookies)
    const cookies = document.cookie.split(";");

    for (let cookie of cookies) {
      const eqPos = cookie.indexOf("=");
      const name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim();

      if (name) {
        // Clear cookie for current domain
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
        // Clear cookie for localhost specifically
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=localhost`;
        // Clear cookie for .localhost
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=.localhost`;
      }
    }

    serverLog(`Client-side: Attempted to clear ${cookies.length} cookies`);

    // Server-side cookie clearing (for HttpOnly cookies)
    try {
      const response = await fetch("/api/clear-cookies", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
      });

      if (response.ok) {
        const result = await response.json();
        serverLog("Server-side cookie clearing successful", result);
      } else {
        serverLog("Server-side cookie clearing failed", {
          status: response.status,
        });
      }
    } catch (err) {
      serverLog("Server-side cookie clearing request failed", { error: err });
    }

    // Reset all response data
    cookieTestResponse = null;
    cookieCheckResponse = null;
    cookieHeadersResponse = null;
    error = null;

    // Update display
    updateBrowserCookiesDisplay();
  }

  async function setCookies() {
    loading = true;
    error = null;
    cookieTestResponse = null;

    serverLog("Starting cookie test - calling POST /dev/cookie-test");

    try {
      const response = await fetch(`${config.api.baseUrl}/dev/cookie-test`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
      });

      serverLog(`Cookie test response status: ${response.status}`, {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
      });

      if (response.ok) {
        const data = await response.json();
        cookieTestResponse = data;
        serverLog("Cookie test successful", data);
      } else {
        const errorText = await response.text();
        error = `Failed to set cookies: ${response.status} ${response.statusText}`;
        serverLog("Cookie test failed", {
          error: errorText,
          status: response.status,
        });
      }
    } catch (err) {
      error = `Request failed: ${err instanceof Error ? err.message : "Unknown error"}`;
      serverLog("Cookie test request failed", { error: err });
    } finally {
      loading = false;
    }
  }

  async function checkCookies() {
    loading = true;
    error = null;
    cookieCheckResponse = null;

    serverLog("Checking cookies - calling GET /dev/cookie-check");

    try {
      const response = await fetch(`${config.api.baseUrl}/dev/cookie-check`, {
        method: "GET",
        credentials: "include",
        headers: {
          Accept: "application/json",
        },
      });

      serverLog(`Cookie check response status: ${response.status}`, {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
      });

      if (response.ok) {
        const data = await response.json();
        cookieCheckResponse = data;
        serverLog("Cookie check successful", data);
      } else {
        const errorText = await response.text();
        error = `Failed to check cookies: ${response.status} ${response.statusText}`;
        serverLog("Cookie check failed", {
          error: errorText,
          status: response.status,
        });
      }
    } catch (err) {
      error = `Request failed: ${err instanceof Error ? err.message : "Unknown error"}`;
      serverLog("Cookie check request failed", { error: err });
    } finally {
      loading = false;
    }
  }

  async function checkHeaders() {
    loading = true;
    error = null;
    cookieHeadersResponse = null;

    serverLog("Checking headers - calling GET /dev/cookie-headers");

    try {
      const response = await fetch(`${config.api.baseUrl}/dev/cookie-headers`, {
        method: "GET",
        credentials: "include",
        headers: {
          Accept: "application/json",
        },
      });

      serverLog(`Cookie headers response status: ${response.status}`, {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
      });

      if (response.ok) {
        const data = await response.json();
        cookieHeadersResponse = data;
        serverLog("Cookie headers check successful", data);
      } else {
        const errorText = await response.text();
        error = `Failed to check headers: ${response.status} ${response.statusText}`;
        serverLog("Cookie headers check failed", {
          error: errorText,
          status: response.status,
        });
      }
    } catch (err) {
      error = `Request failed: ${err instanceof Error ? err.message : "Unknown error"}`;
      serverLog("Cookie headers check request failed", { error: err });
    } finally {
      loading = false;
    }
  }

  async function runFullTest() {
    serverLog("Starting full cookie test sequence");

    // Clear all cookies first for clean test
    await clearAllCookies();
    await new Promise((resolve) => setTimeout(resolve, 500)); // Brief delay after clearing

    await setCookies();
    if (!error) {
      await new Promise((resolve) => setTimeout(resolve, 500)); // Brief delay
      await checkCookies();
    }
    if (!error) {
      await new Promise((resolve) => setTimeout(resolve, 500)); // Brief delay
      await checkHeaders();
    }
    serverLog("Full cookie test sequence complete");
  }

  onMount(() => {
    serverLog("Cookie test page loaded");
    updateBrowserCookiesDisplay();
  });
</script>

<div class="cookie-test-container">
  <h1>Cookie Test Interface</h1>
  <p>Test authentication cookie setting and retrieval with the web-bff</p>

  <div class="controls">
    <button on:click={clearAllCookies} disabled={loading} class="warning">
      Clear All Cookies
    </button>
    <button on:click={runFullTest} disabled={loading} class="primary">
      {loading ? "Running Test..." : "Run Full Test"}
    </button>
    <button on:click={setCookies} disabled={loading}> Set Tokens </button>
    <button on:click={checkCookies} disabled={loading}> Check Cookies </button>
    <button on:click={checkHeaders} disabled={loading}> Check Headers </button>
    <button on:click={updateBrowserCookiesDisplay} disabled={loading}>
      Refresh Cookie Display
    </button>
  </div>

  <div class="browser-cookies-section">
    <h3>Current Browser Cookies</h3>
    <div class="cookie-display">
      <code>{currentBrowserCookies}</code>
    </div>
  </div>

  {#if error}
    <div class="error-section">
      <h2>Error</h2>
      <p class="error-message">{error}</p>
    </div>
  {/if}

  {#if cookieTestResponse}
    <div class="response-section success">
      <h2>Cookie Test Response (POST /dev/cookie-test)</h2>
      <div class="response-summary">
        <div class="status-item">
          <strong>Success:</strong>
          <span
            class="status {cookieTestResponse.success ? 'success' : 'error'}"
            >{cookieTestResponse.success}</span
          >
        </div>
        <div class="status-item">
          <strong>Message:</strong>
          {cookieTestResponse.message || "N/A"}
        </div>
        <div class="status-item">
          <strong>Access Token (Response Body):</strong>
          {#if cookieTestResponse.access_token}
            <code class="token-preview"
              >{cookieTestResponse.access_token.substring(
                0,
                12
              )}...{cookieTestResponse.access_token.substring(
                cookieTestResponse.access_token.length - 8
              )}</code
            >
            <span class="status success">✓ In Response</span>
          {:else}
            <span class="status error">✗ Missing</span>
          {/if}
        </div>
        <div class="status-item">
          <strong>Refresh Token (Cookie):</strong>
          {#if cookieTestResponse.cookies_set?.includes("refresh_token")}
            <span class="status success">✓ Set as HttpOnly Cookie</span>
          {:else}
            <span class="status error">✗ Not Set</span>
          {/if}
        </div>
        <div class="status-item">
          <strong>Token Type:</strong>
          {cookieTestResponse.token_type || "N/A"}
        </div>
        <div class="status-item">
          <strong>Expires In:</strong>
          {cookieTestResponse.expires_in
            ? `${cookieTestResponse.expires_in}s`
            : "N/A"}
        </div>
      </div>
      <div class="json-display">
        <pre>{JSON.stringify(cookieTestResponse, null, 2)}</pre>
      </div>
    </div>
  {/if}

  {#if cookieCheckResponse}
    <div class="response-section info">
      <h2>Cookie Check Response (GET /dev/cookie-check)</h2>
      <div class="response-summary">
        <div class="status-item">
          <strong>Authentication Status:</strong>
          <span
            class="status {cookieCheckResponse.authenticated
              ? 'success'
              : 'warning'}"
            >{cookieCheckResponse.authenticated
              ? "Authenticated"
              : "Partial Auth"}</span
          >
        </div>
        <div class="status-item">
          <strong>Refresh Token (Cookie):</strong>
          <span
            class="status {cookieCheckResponse.refresh_token_present
              ? 'success'
              : 'error'}"
            >{cookieCheckResponse.refresh_token_present
              ? "Present"
              : "Missing"}</span
          >
          {#if cookieCheckResponse.refresh_token_preview}
            <code>{cookieCheckResponse.refresh_token_preview}</code>
          {/if}
        </div>
        <div class="status-item">
          <strong>Access Token (Cookie - Not Expected):</strong>
          <span
            class="status {cookieCheckResponse.access_token_present
              ? 'warning'
              : 'success'}"
            >{cookieCheckResponse.access_token_present
              ? "Present (Unexpected)"
              : "Absent (Correct)"}</span
          >
          {#if cookieCheckResponse.access_token_preview}
            <code>{cookieCheckResponse.access_token_preview}</code>
          {/if}
        </div>
        <div class="status-item">
          <strong>Total Cookies Received:</strong>
          {Object.keys(cookieCheckResponse.all_cookies || {}).length}
        </div>
        <div class="status-item">
          <strong>Raw Cookie Header:</strong>
          <code class="cookie-header"
            >{cookieCheckResponse.request_cookie_header || "None"}</code
          >
        </div>
      </div>
      <div class="json-display">
        <pre>{JSON.stringify(cookieCheckResponse, null, 2)}</pre>
      </div>
    </div>
  {/if}

  {#if cookieHeadersResponse}
    <div class="response-section warning">
      <h2>Cookie Headers Response (GET /dev/cookie-headers)</h2>
      <div class="response-summary">
        <div class="status-item">
          <strong>Message:</strong>
          {cookieHeadersResponse.message || "N/A"}
        </div>
        <div class="status-item">
          <strong>Set-Cookie Headers:</strong>
          {cookieHeadersResponse.set_cookie_headers?.length || 0} headers
        </div>
      </div>
      <div class="json-display">
        <pre>{JSON.stringify(cookieHeadersResponse, null, 2)}</pre>
      </div>
    </div>
  {/if}

  <div class="info-section">
    <h3>Test Flow - New Cookie Format</h3>
    <ol>
      <li>
        <strong>Set Tokens:</strong> POST /dev/cookie-test - Sets refresh_token as
        HttpOnly cookie, returns access_token in response body
      </li>
      <li>
        <strong>Check Cookies:</strong> GET /dev/cookie-check - Verifies refresh_token
        cookie is being sent
      </li>
      <li>
        <strong>Check Headers:</strong> GET /dev/cookie-headers - Inspects HTTP headers
      </li>
    </ol>
    <div class="auth-pattern">
      <h4>Authentication Pattern:</h4>
      <ul>
        <li>
          <strong>Access Token:</strong> Returned in JSON response body (short-lived,
          stored in memory)
        </li>
        <li>
          <strong>Refresh Token:</strong> Set as HttpOnly cookie (long-lived, 7 days)
        </li>
        <li>
          <strong>Security:</strong> Access token can't be stolen via XSS, refresh
          token can't be accessed by JavaScript
        </li>
      </ul>
    </div>
    <p><strong>Base URL:</strong> <code>{config.api.baseUrl}</code></p>
    <p>
      <strong>Credentials:</strong> Always included (credentials: 'include')
    </p>
    <p>
      <strong>Logging:</strong> Check both browser console and server terminal for
      detailed logs
    </p>
  </div>
</div>

<style>
  :global(body) {
    background: #181a1b !important;
    color: #f3f3f3 !important;
    font-family: system-ui, sans-serif;
    margin: 0;
    padding: 0;
  }

  .cookie-test-container {
    max-width: 1000px;
    margin: 2rem auto;
    padding: 2rem;
    background: #23272b;
    border-radius: 12px;
    color: #f3f3f3;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
  }

  h1 {
    color: #4f8cff;
    margin-bottom: 1rem;
  }

  h2,
  h3 {
    color: #f3f3f3;
    margin-top: 2rem;
    margin-bottom: 1rem;
  }

  .controls {
    display: flex;
    gap: 1rem;
    margin: 1.5rem 0;
    flex-wrap: wrap;
  }

  button {
    background: #4f8cff;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1rem;
    transition: background-color 0.2s;
  }

  button.primary {
    background: #4caf50;
    font-weight: bold;
  }

  button.warning {
    background: #ff6b6b;
    font-weight: bold;
  }

  button:hover:not(:disabled) {
    filter: brightness(1.1);
  }

  button:disabled {
    background: #666;
    cursor: not-allowed;
  }

  .error-section {
    background: rgba(255, 107, 107, 0.1);
    border: 1px solid #ff6b6b;
    border-radius: 6px;
    padding: 1rem;
    margin: 1rem 0;
  }

  .error-message {
    color: #ff6b6b;
    margin: 0;
  }

  .response-section {
    border-radius: 6px;
    padding: 1rem;
    margin: 1rem 0;
  }

  .response-section.success {
    background: rgba(76, 175, 80, 0.1);
    border: 1px solid #4caf50;
  }

  .response-section.info {
    background: rgba(79, 140, 255, 0.1);
    border: 1px solid #4f8cff;
  }

  .response-section.warning {
    background: rgba(255, 193, 7, 0.1);
    border: 1px solid #ffc107;
  }

  .response-summary {
    display: grid;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .status.success {
    color: #4caf50;
    font-weight: bold;
  }

  .status.error {
    color: #ff6b6b;
    font-weight: bold;
  }

  .status.warning {
    color: #ffc107;
    font-weight: bold;
  }

  .json-display {
    background: #1a1a1a;
    border-radius: 4px;
    padding: 1rem;
    overflow-x: auto;
    margin-top: 0.5rem;
  }

  .json-display pre {
    margin: 0;
    color: #e0e0e0;
    font-family: "Courier New", monospace;
    font-size: 0.85rem;
    line-height: 1.4;
  }

  .info-section {
    background: rgba(79, 140, 255, 0.1);
    border: 1px solid #4f8cff;
    border-radius: 6px;
    padding: 1rem;
    margin: 2rem 0;
  }

  code {
    background: #333;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: "Courier New", monospace;
    color: #4caf50;
    font-size: 0.9em;
  }

  .token-preview {
    color: #4f8cff !important;
    font-weight: bold;
  }

  .cookie-header {
    color: #ffc107 !important;
    font-size: 0.8em;
    word-break: break-all;
  }

  .auth-pattern {
    background: rgba(79, 140, 255, 0.05);
    border-left: 3px solid #4f8cff;
    padding: 1rem;
    margin: 1rem 0;
  }

  .auth-pattern h4 {
    margin: 0 0 0.5rem 0;
    color: #4f8cff;
  }

  .auth-pattern ul {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
  }

  .auth-pattern li {
    margin: 0.3rem 0;
    font-size: 0.9rem;
  }

  .browser-cookies-section {
    background: rgba(255, 193, 7, 0.1);
    border: 1px solid #ffc107;
    border-radius: 6px;
    padding: 1rem;
    margin: 1rem 0;
  }

  .browser-cookies-section h3 {
    margin: 0 0 0.5rem 0;
    color: #ffc107;
  }

  .cookie-display {
    background: #1a1a1a;
    border-radius: 4px;
    padding: 0.75rem;
    overflow-x: auto;
  }

  .cookie-display code {
    color: #ffc107;
    font-size: 0.85rem;
    background: transparent;
    padding: 0;
    word-break: break-all;
  }

  ol {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
  }

  li {
    margin: 0.5rem 0;
    line-height: 1.4;
  }

  p {
    margin-bottom: 1rem;
    line-height: 1.5;
  }
</style>
