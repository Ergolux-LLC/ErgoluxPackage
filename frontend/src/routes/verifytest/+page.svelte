<script lang="ts">
  import { onMount } from "svelte";
  import { browser } from "$app/environment";
  import { page } from "$app/stores";
  import type { PageData } from "./$types";

  export let data: PageData;

  // Test state
  let logs: string[] = [];
  let isLoading = false;
  let validationResult: any = null;
  let error: string | null = null;

  // Auth state from localStorage
  let accessToken: string | null = null;
  let isAuthenticated = false;

  // Add log entry with timestamp
  function addLog(
    message: string,
    type: "info" | "error" | "success" = "info",
  ) {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = `[${timestamp}] [${type.toUpperCase()}] ${message}`;
    logs = [...logs, logEntry];
    console.log(logEntry);
  }

  // Load access token from localStorage
  function loadAccessToken() {
    if (browser) {
      const stored = localStorage.getItem("access_token");
      if (stored) {
        accessToken = stored;
        isAuthenticated = true;
        addLog("Access token loaded from localStorage", "success");
        addLog(`Token length: ${stored.length} characters`);
      } else {
        addLog("No access token found in localStorage", "error");
      }
    }
  }

  // Test token validation
  async function testValidation() {
    if (!accessToken) {
      error = "No access token available. Please login first.";
      addLog("Validation failed: No access token", "error");
      return;
    }

    isLoading = true;
    error = null;
    validationResult = null;

    const requestId = crypto.randomUUID().substring(0, 8);
    addLog(`Starting token validation (ID: ${requestId})`);

    const startTime = Date.now();

    try {
      addLog("Sending GET request to /api/auth/validate");
      addLog(`Using Authorization: Bearer ${accessToken.substring(0, 20)}...`);

      const response = await fetch("/api/auth/validate", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        credentials: "include", // Include cookies for refresh token
      });

      const duration = Date.now() - startTime;
      addLog(`Response received in ${duration}ms`);
      addLog(`Status: ${response.status} ${response.statusText}`);

      // Log response headers
      const headers = Object.fromEntries(response.headers.entries());
      addLog(`Response headers: ${JSON.stringify(headers, null, 2)}`);

      const responseData = await response.json();

      if (response.ok) {
        validationResult = responseData;
        addLog("Token validation successful!", "success");
        addLog(`Valid: ${responseData.valid}`);
        addLog(`User ID: ${responseData.user?.id || "missing"}`);
        addLog(`User Email: ${responseData.user?.email || "missing"}`);
        addLog(`Message: ${responseData.message || "none"}`);
      } else {
        error =
          responseData.error ||
          `Validation failed with status ${response.status}`;
        addLog(`Validation failed: ${error}`, "error");

        if (response.status === 401) {
          if (responseData.can_refresh) {
            addLog("Token expired but refresh token available", "info");
            addLog(
              "In a real app, this would trigger automatic token refresh",
              "info",
            );
          } else {
            addLog("Token invalid and no refresh available", "error");
          }
        }

        addLog(
          `Error details: ${JSON.stringify(responseData, null, 2)}`,
          "error",
        );
      }
    } catch (fetchError) {
      const duration = Date.now() - startTime;
      error =
        fetchError instanceof Error
          ? fetchError.message
          : "Unknown error occurred";
      addLog(`Validation failed after ${duration}ms: ${error}`, "error");

      if (
        fetchError instanceof TypeError &&
        fetchError.message.includes("fetch")
      ) {
        addLog("Network error - check if services are running", "error");
      }
    } finally {
      isLoading = false;
      addLog(`Validation attempt completed (ID: ${requestId})`);
    }
  }

  // Test invalid token
  function testInvalidToken() {
    const originalToken = accessToken;
    accessToken = "invalid_token_for_testing";
    addLog("Using invalid token for testing");

    testValidation().then(() => {
      // Restore original token after test
      accessToken = originalToken;
      addLog("Restored original token");
    });
  }

  // Clear logs
  function clearLogs() {
    logs = [];
    validationResult = null;
    error = null;
    addLog("Logs and results cleared");
  }

  // Navigate to login
  function goToLogin() {
    window.location.href = "/logintest";
  }

  onMount(() => {
    addLog("Token Verification Test Page loaded");
    addLog(`Server validation: ${JSON.stringify(data.serverValidation)}`);
    addLog(`Auth state: ${JSON.stringify(data.auth)}`);
    loadAccessToken();

    if (!accessToken) {
      addLog("No access token found - user needs to login first", "error");
    }
  });
</script>

<svelte:head>
  <title>Token Verification Test - Ergolux Portal</title>
</svelte:head>

<div class="container mt-4">
  <div class="row">
    <div class="col-lg-10 mx-auto">
      <div class="card">
        <div class="card-header bg-success text-white">
          <h3 class="card-title mb-0">
            <i class="bi bi-shield-check me-2"></i>
            Token Verification Test Portal
            {#if isAuthenticated}
              <span class="badge bg-light text-success ms-2"
                >Token Available</span
              >
            {:else}
              <span class="badge bg-warning text-dark ms-2">No Token</span>
            {/if}
          </h3>
        </div>

        <div class="card-body">
          <!-- Server-side Validation Status -->
          <div class="row mb-4">
            <div class="col-md-6">
              <div class="alert alert-info">
                <h6><i class="bi bi-server me-2"></i>Server-side Validation</h6>
                <ul class="mb-0 small">
                  <li>
                    <strong>Refresh Token:</strong>
                    {data.auth?.hasRefreshToken ? "✅ Present" : "❌ Missing"}
                  </li>
                  <li>
                    <strong>Page Access:</strong> ✅ Allowed (you're seeing this
                    page)
                  </li>
                  <li>
                    <strong>Validated At:</strong>
                    {data.serverValidation?.validatedAt}
                  </li>
                  <li>
                    <strong>Request ID:</strong>
                    {data.serverValidation?.requestId}
                  </li>
                </ul>
              </div>
            </div>

            <div class="col-md-6">
              <div
                class="alert {isAuthenticated
                  ? 'alert-success'
                  : 'alert-warning'}"
              >
                <h6><i class="bi bi-key me-2"></i>Client-side Token Status</h6>
                <ul class="mb-0 small">
                  <li>
                    <strong>Access Token:</strong>
                    {isAuthenticated ? "✅ Available" : "❌ Missing"}
                  </li>
                  <li>
                    <strong>Storage:</strong>
                    {isAuthenticated ? "localStorage" : "none"}
                  </li>
                  <li>
                    <strong>Can Validate:</strong>
                    {isAuthenticated ? "✅ Yes" : "❌ No"}
                  </li>
                  {#if isAuthenticated}
                    <li>
                      <strong>Length:</strong>
                      {accessToken?.length || 0} chars
                    </li>
                  {/if}
                </ul>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="row mb-4">
            <div class="col-md-8">
              <h5>Validation Tests</h5>
              <div class="btn-group w-100" role="group">
                <button
                  type="button"
                  class="btn btn-primary"
                  on:click={testValidation}
                  disabled={isLoading || !isAuthenticated}
                >
                  {#if isLoading}
                    <span class="spinner-border spinner-border-sm me-2"></span>
                    Validating...
                  {:else}
                    <i class="bi bi-shield-check me-2"></i>
                    Test Valid Token
                  {/if}
                </button>
                <button
                  type="button"
                  class="btn btn-warning"
                  on:click={testInvalidToken}
                  disabled={isLoading || !isAuthenticated}
                >
                  <i class="bi bi-shield-x me-2"></i>
                  Test Invalid Token
                </button>
                <button
                  type="button"
                  class="btn btn-outline-secondary"
                  on:click={clearLogs}
                  disabled={isLoading}
                >
                  <i class="bi bi-arrow-clockwise me-2"></i>
                  Clear Results
                </button>
              </div>
            </div>

            <div class="col-md-4">
              <h5>Navigation</h5>
              <button
                type="button"
                class="btn btn-outline-primary w-100"
                on:click={goToLogin}
              >
                <i class="bi bi-box-arrow-in-right me-2"></i>
                Go to Login Test
              </button>
            </div>
          </div>

          {#if !isAuthenticated}
            <div class="alert alert-warning">
              <h6>
                <i class="bi bi-exclamation-triangle me-2"></i>No Access Token
                Available
              </h6>
              <p class="mb-2">
                You need to login first to test token validation. The
                server-side validation passed (allowing you to see this page),
                but client-side validation requires an access token.
              </p>
              <button class="btn btn-primary btn-sm" on:click={goToLogin}>
                <i class="bi bi-box-arrow-in-right me-1"></i>
                Login Now
              </button>
            </div>
          {/if}
        </div>
      </div>

      <!-- Validation Results -->
      {#if error || validationResult}
        <div class="card mt-4">
          <div class="card-header">
            <h5 class="mb-0">
              {#if error}
                <i class="bi bi-exclamation-triangle text-danger me-2"></i>
                Validation Failed
              {:else}
                <i class="bi bi-check-circle text-success me-2"></i>
                Validation Successful
              {/if}
            </h5>
          </div>
          <div class="card-body">
            {#if error}
              <div class="alert alert-danger">
                <strong>Validation Error:</strong>
                {error}
              </div>
            {/if}

            {#if validationResult}
              <div class="alert alert-success">
                <strong>Token is Valid!</strong>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <h6>Validation Result</h6>
                  <ul class="list-group list-group-flush">
                    <li class="list-group-item d-flex justify-content-between">
                      <span>Valid:</span>
                      <span class="badge bg-success"
                        >{validationResult.valid ? "True" : "False"}</span
                      >
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                      <span>Message:</span>
                      <span>{validationResult.message || "none"}</span>
                    </li>
                  </ul>
                </div>

                <div class="col-md-6">
                  <h6>User Information</h6>
                  <ul class="list-group list-group-flush">
                    <li class="list-group-item d-flex justify-content-between">
                      <span>User ID:</span>
                      <code>{validationResult.user?.id || "N/A"}</code>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                      <span>Email:</span>
                      <span>{validationResult.user?.email || "N/A"}</span>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                      <span>First Name:</span>
                      <span>{validationResult.user?.first_name || "N/A"}</span>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                      <span>Last Name:</span>
                      <span>{validationResult.user?.last_name || "N/A"}</span>
                    </li>
                  </ul>
                </div>
              </div>

              <div class="mt-3">
                <details>
                  <summary class="btn btn-outline-secondary btn-sm"
                    >View Raw Response</summary
                  >
                  <pre class="mt-2"><code
                      >{JSON.stringify(validationResult, null, 2)}</code
                    ></pre>
                </details>
              </div>
            {/if}
          </div>
        </div>
      {/if}

      <!-- Logs Section -->
      {#if logs.length > 0}
        <div class="card mt-4">
          <div
            class="card-header d-flex justify-content-between align-items-center"
          >
            <h5 class="mb-0">
              <i class="bi bi-terminal me-2"></i>
              Validation Logs ({logs.length})
            </h5>
            <button
              type="button"
              class="btn btn-outline-secondary btn-sm"
              on:click={() => (logs = [])}
            >
              Clear Logs
            </button>
          </div>
          <div class="card-body">
            <div
              class="bg-dark text-light p-3 rounded font-monospace"
              style="max-height: 400px; overflow-y: auto;"
            >
              {#each logs as log}
                <div class="small mb-1">{log}</div>
              {/each}
            </div>
          </div>
        </div>
      {/if}

      <!-- Documentation -->
      <div class="card mt-4">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="bi bi-book me-2"></i>
            Validation Flow Documentation
          </h5>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <h6>Server-side Protection</h6>
              <ul class="list-unstyled">
                <li>
                  <i class="bi bi-check text-success me-2"></i><code
                    >+layout.server.ts</code
                  > - Checks refresh token
                </li>
                <li>
                  <i class="bi bi-check text-success me-2"></i><code
                    >+page.server.ts</code
                  > - Validates access to page
                </li>
                <li>
                  <i class="bi bi-check text-success me-2"></i>Redirects to
                  login if no refresh token
                </li>
                <li>
                  <i class="bi bi-check text-success me-2"></i>Runs before page
                  loads
                </li>
              </ul>
            </div>
            <div class="col-md-6">
              <h6>Client-side Validation</h6>
              <ul class="list-unstyled">
                <li>
                  <i class="bi bi-check text-success me-2"></i><code
                    >/api/auth/validate</code
                  > - Validates access token
                </li>
                <li>
                  <i class="bi bi-check text-success me-2"></i>Proxies to
                  web-bff for validation
                </li>
                <li>
                  <i class="bi bi-check text-success me-2"></i>Returns user
                  information if valid
                </li>
                <li>
                  <i class="bi bi-check text-success me-2"></i>Handles token
                  expiration gracefully
                </li>
              </ul>
            </div>
          </div>

          <div class="mt-3">
            <h6>Testing Scenarios</h6>
            <div class="row">
              <div class="col-md-4">
                <div class="alert alert-info">
                  <strong>Valid Token:</strong> Tests normal authentication flow
                  with stored access token
                </div>
              </div>
              <div class="col-md-4">
                <div class="alert alert-warning">
                  <strong>Invalid Token:</strong> Tests error handling with malformed
                  token
                </div>
              </div>
              <div class="col-md-4">
                <div class="alert alert-danger">
                  <strong>No Token:</strong> Tests behavior when no access token
                  is available
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .font-monospace {
    font-family: "Courier New", monospace;
  }

  .card {
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    border: 1px solid rgba(0, 0, 0, 0.125);
  }

  pre {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 0.375rem;
    padding: 1rem;
    font-size: 0.875rem;
    max-height: 300px;
    overflow-y: auto;
  }

  details summary {
    cursor: pointer;
  }
</style>
