<script lang="ts">
  import { onMount } from "svelte";
  import { browser } from "$app/environment";

  // Form state
  let email = "test@example.com";
  let password = "password123";
  let isLoading = false;

  // Response state
  let response: any = null;
  let error: string | null = null;
  let logs: string[] = [];

  // Auth state
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

  // Clear all state
  function clearState() {
    response = null;
    error = null;
    logs = [];
    accessToken = null;
    isAuthenticated = false;
    // Clear from localStorage
    if (browser) {
      localStorage.removeItem("access_token");
    }
    addLog("State cleared");
  }

  // Store access token securely
  function storeAccessToken(token: string) {
    accessToken = token;
    isAuthenticated = true;
    if (browser) {
      // Store in localStorage for demo purposes
      // In production, consider memory-only storage or secure alternatives
      localStorage.setItem("access_token", token);
    }
    addLog("Access token stored for future requests", "success");
  }

  // Load access token from storage
  function loadAccessToken() {
    if (browser) {
      const stored = localStorage.getItem("access_token");
      if (stored) {
        accessToken = stored;
        isAuthenticated = true;
        addLog("Access token loaded from storage", "success");
      }
    }
  }

  // Test API call using stored access token
  async function testAuthenticatedRequest() {
    if (!accessToken) {
      addLog("No access token available for authenticated request", "error");
      return;
    }

    addLog("Testing authenticated API call to /api/auth/validate");

    try {
      const validateResponse = await fetch("/api/auth/validate", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        credentials: "include", // Important: include cookies for refresh token
      });

      addLog(
        `Validate response: ${validateResponse.status} ${validateResponse.statusText}`,
      );

      if (validateResponse.ok) {
        const validateData = await validateResponse.json();
        addLog("Token validation successful!", "success");
        addLog(
          `Validated user: ${JSON.stringify(validateData.user)}`,
          "success",
        );
      } else {
        const errorData = await validateResponse.json();
        addLog(
          `Token validation failed: ${errorData.detail || "Unknown error"}`,
          "error",
        );

        if (validateResponse.status === 401) {
          addLog(
            "Access token may be expired. Refresh token should handle this automatically.",
            "error",
          );
          // Clear invalid token
          accessToken = null;
          isAuthenticated = false;
          if (browser) {
            localStorage.removeItem("access_token");
          }
        }
      }
    } catch (err) {
      addLog(`Error during authenticated request: ${err}`, "error");
    }
  }

  // Handle login form submission
  async function handleLogin() {
    if (!email || !password) {
      error = "Please fill in all fields";
      addLog("Validation failed: Missing email or password", "error");
      return;
    }

    isLoading = true;
    error = null;
    response = null;

    const requestId = crypto.randomUUID().substring(0, 8);
    addLog(`Starting login request (ID: ${requestId})`);
    addLog(`Email: ${email}`);
    addLog(`Password: ${"*".repeat(password.length)}`);

    const startTime = Date.now();

    try {
      addLog("Sending POST request to /api/auth/login");

      const loginResponse = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
        credentials: "include", // Important: include cookies for refresh token
      });

      const duration = Date.now() - startTime;
      addLog(`Response received in ${duration}ms`);
      addLog(`Status: ${loginResponse.status} ${loginResponse.statusText}`);

      // Log response headers
      const headers = Object.fromEntries(loginResponse.headers.entries());
      addLog(`Response headers: ${JSON.stringify(headers, null, 2)}`);

      const responseData = await loginResponse.json();

      if (loginResponse.ok) {
        response = responseData;
        addLog("Login successful!", "success");
        addLog(`User ID: ${responseData.user?.id || "missing"}`);
        addLog(
          `User Name: ${responseData.user?.first_name || ""} ${responseData.user?.last_name || ""}`,
        );
        addLog(`Access Token Present: ${!!responseData.access_token}`);
        addLog(`Token Type: ${responseData.token_type || "missing"}`);
        addLog(`Expires In: ${responseData.expires_in || "missing"} seconds`);
        addLog(`Workspaces: ${responseData.workspaces?.length || 0}`);

        // Store the access token
        if (responseData.access_token) {
          storeAccessToken(responseData.access_token);
        }

        if (responseData.workspaces?.length > 0) {
          addLog(
            `First Workspace: ${responseData.workspaces[0].name} (${responseData.workspaces[0].id})`,
          );
        }

        if (responseData.last_accessed_workspace) {
          addLog(
            `Last Accessed: ${responseData.last_accessed_workspace.name} (${responseData.last_accessed_workspace.id})`,
          );
        }

        // Check if refresh token cookie was set (we can't access HttpOnly cookies from JS)
        addLog(
          "Note: Refresh token should be set as HttpOnly cookie (not visible to JavaScript)",
        );
        addLog(
          "Note: Access token stored in memory/localStorage for API requests",
        );
      } else {
        error =
          responseData.error ||
          `Login failed with status ${loginResponse.status}`;
        addLog(`Login failed: ${error}`, "error");
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
      addLog(`Login failed after ${duration}ms: ${error}`, "error");
      addLog(`Full error: ${JSON.stringify(fetchError, null, 2)}`, "error");

      if (
        fetchError instanceof TypeError &&
        fetchError.message.includes("fetch")
      ) {
        addLog("Network error - check if web-bff service is running", "error");
        addLog("Try: cd services/web_bff && docker-compose up -d", "error");
      }
    } finally {
      isLoading = false;
      addLog(`Login attempt completed (ID: ${requestId})`);
    }
  }

  // Test logout
  async function testLogout() {
    addLog("Testing logout functionality");

    try {
      const logoutResponse = await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "include", // Include cookies
      });

      if (logoutResponse.ok) {
        addLog("Logout successful!", "success");
        clearState();
      } else {
        const errorData = await logoutResponse.json();
        addLog(
          `Logout failed: ${errorData.detail || "Unknown error"}`,
          "error",
        );
      }
    } catch (err) {
      addLog(`Error during logout: ${err}`, "error");
    }
  }

  // Test with preset credentials
  function useTestCredentials() {
    email = "dev@example.com";
    password = "devpassword123";
    addLog("Using test credentials: dev@example.com / admin123");
  }

  // Test with invalid credentials
  function useInvalidCredentials() {
    email = "invalid@example.com";
    password = "wrongpassword";
    addLog("Using invalid credentials for error testing");
  }

  onMount(() => {
    addLog("Login Test Page loaded");
    addLog("Ready to test authentication flow");
    loadAccessToken(); // Load any existing token
  });
</script>

<svelte:head>
  <title>Login Test - Ergolux Portal</title>
</svelte:head>

<div class="container mt-4">
  <div class="row">
    <div class="col-lg-8 mx-auto">
      <div class="card">
        <div class="card-header bg-primary text-white">
          <h3 class="card-title mb-0">
            <i class="bi bi-shield-lock me-2"></i>
            Authentication Test Portal
            {#if isAuthenticated}
              <span class="badge bg-success ms-2">Authenticated</span>
            {/if}
          </h3>
        </div>

        <div class="card-body">
          <!-- Authentication Status -->
          <div class="row mb-4">
            <div class="col-12">
              <div
                class="alert {isAuthenticated
                  ? 'alert-success'
                  : 'alert-warning'}"
              >
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <i
                      class="bi {isAuthenticated
                        ? 'bi-check-circle'
                        : 'bi-exclamation-triangle'} me-2"
                    ></i>
                    <strong>Auth Status:</strong>
                    {isAuthenticated
                      ? "Authenticated with stored access token"
                      : "Not authenticated"}
                  </div>
                  {#if isAuthenticated}
                    <div class="btn-group">
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-primary"
                        on:click={testAuthenticatedRequest}
                      >
                        <i class="bi bi-shield-check me-1"></i>
                        Test Token
                      </button>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-danger"
                        on:click={testLogout}
                      >
                        <i class="bi bi-box-arrow-right me-1"></i>
                        Logout
                      </button>
                    </div>
                  {/if}
                </div>
              </div>
            </div>
          </div>

          <!-- Test Controls -->
          <div class="row mb-4">
            <div class="col-md-6">
              <h5>Quick Actions</h5>
              <div class="btn-group-vertical w-100">
                <button
                  type="button"
                  class="btn btn-outline-success btn-sm"
                  on:click={useTestCredentials}
                  disabled={isLoading}
                >
                  <i class="bi bi-person-check me-1"></i>
                  Use Test Credentials
                </button>
                <button
                  type="button"
                  class="btn btn-outline-warning btn-sm"
                  on:click={useInvalidCredentials}
                  disabled={isLoading}
                >
                  <i class="bi bi-person-x me-1"></i>
                  Test Invalid Credentials
                </button>
                <button
                  type="button"
                  class="btn btn-outline-secondary btn-sm"
                  on:click={clearState}
                  disabled={isLoading}
                >
                  <i class="bi bi-arrow-clockwise me-1"></i>
                  Clear Results
                </button>
              </div>
            </div>

            <div class="col-md-6">
              <h5>Service Status</h5>
              <div class="alert alert-info">
                <small>
                  <strong>Web BFF:</strong> http://localhost:8050<br />
                  <strong>Frontend API:</strong> /api/auth/login<br />
                  <strong>Auth Service:</strong> Proxied via Web BFF<br />
                  <strong>Cookie Flow:</strong> Refresh token in HttpOnly cookie
                </small>
              </div>
            </div>
          </div>

          <!-- Login Form -->
          <form on:submit|preventDefault={handleLogin}>
            <div class="row">
              <div class="col-md-6">
                <div class="mb-3">
                  <label for="email" class="form-label">Email Address</label>
                  <input
                    type="email"
                    class="form-control"
                    id="email"
                    bind:value={email}
                    disabled={isLoading}
                    placeholder="Enter email address"
                    required
                  />
                </div>
              </div>
              <div class="col-md-6">
                <div class="mb-3">
                  <label for="password" class="form-label">Password</label>
                  <input
                    type="password"
                    class="form-control"
                    id="password"
                    bind:value={password}
                    disabled={isLoading}
                    placeholder="Enter password"
                    required
                  />
                </div>
              </div>
            </div>

            <div class="d-grid">
              <button
                type="submit"
                class="btn btn-primary"
                disabled={isLoading}
              >
                {#if isLoading}
                  <span
                    class="spinner-border spinner-border-sm me-2"
                    role="status"
                  ></span>
                  Authenticating...
                {:else}
                  <i class="bi bi-box-arrow-in-right me-2"></i>
                  Test Login
                {/if}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Results Section -->
      {#if error || response}
        <div class="card mt-4">
          <div class="card-header">
            <h5 class="mb-0">
              {#if error}
                <i class="bi bi-exclamation-triangle text-danger me-2"></i>
                Error Response
              {:else}
                <i class="bi bi-check-circle text-success me-2"></i>
                Success Response
              {/if}
            </h5>
          </div>
          <div class="card-body">
            {#if error}
              <div class="alert alert-danger">
                <strong>Authentication Failed:</strong>
                {error}
              </div>
            {/if}

            {#if response}
              <div class="alert alert-success">
                <strong>Authentication Successful!</strong>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <h6>User Information</h6>
                  <ul class="list-group list-group-flush">
                    <li class="list-group-item d-flex justify-content-between">
                      <span>ID:</span>
                      <code>{response.user?.id || "N/A"}</code>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                      <span>Name:</span>
                      <span
                        >{response.user?.first_name || ""}
                        {response.user?.last_name || ""}</span
                      >
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                      <span>Email:</span>
                      <span>{response.user?.email || "N/A"}</span>
                    </li>
                  </ul>
                </div>

                <div class="col-md-6">
                  <h6>Token Information</h6>
                  <ul class="list-group list-group-flush">
                    <li class="list-group-item d-flex justify-content-between">
                      <span>Access Token:</span>
                      <span class="badge bg-success">Stored</span>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                      <span>Token Type:</span>
                      <code>{response.token_type}</code>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                      <span>Expires In:</span>
                      <span>{response.expires_in}s</span>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                      <span>Refresh Token:</span>
                      <span class="badge bg-info">HttpOnly Cookie</span>
                    </li>
                  </ul>
                </div>
              </div>

              {#if response.workspaces?.length > 0}
                <div class="mt-3">
                  <h6>Workspaces ({response.workspaces.length})</h6>
                  <div class="row">
                    {#each response.workspaces as workspace}
                      <div class="col-md-6 mb-2">
                        <div class="card">
                          <div class="card-body py-2">
                            <h6 class="card-title mb-1">{workspace.name}</h6>
                            <small class="text-muted">ID: {workspace.id}</small>
                          </div>
                        </div>
                      </div>
                    {/each}
                  </div>
                </div>
              {/if}

              <div class="mt-3">
                <details>
                  <summary class="btn btn-outline-secondary btn-sm"
                    >View Raw Response</summary
                  >
                  <pre class="mt-2"><code
                      >{JSON.stringify(response, null, 2)}</code
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
              Request Logs ({logs.length})
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
              class="bg-dark text-light p-3 rounded"
              style="max-height: 400px; overflow-y: auto;"
            >
              {#each logs as log}
                <div class="font-monospace small mb-1">
                  {log}
                </div>
              {/each}
            </div>
          </div>
        </div>
      {/if}

      <!-- Development Notes -->
      <div class="card mt-4">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="bi bi-info-circle me-2"></i>
            Development Notes
          </h5>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <h6>Test Scenarios</h6>
              <ul class="list-unstyled">
                <li>
                  <i class="bi bi-check text-success me-2"></i>Valid credentials
                </li>
                <li>
                  <i class="bi bi-x text-danger me-2"></i>Invalid credentials
                </li>
                <li>
                  <i class="bi bi-wifi-off text-warning me-2"></i>Service
                  unavailable
                </li>
                <li>
                  <i class="bi bi-hourglass text-info me-2"></i>Network timeout
                </li>
              </ul>
            </div>
            <div class="col-md-6">
              <h6>Service Dependencies</h6>
              <ul class="list-unstyled">
                <li><i class="bi bi-server me-2"></i>Web BFF (port 8050)</li>
                <li><i class="bi bi-shield-check me-2"></i>Auth Service</li>
                <li><i class="bi bi-people me-2"></i>Human Service</li>
                <li><i class="bi bi-database me-2"></i>PostgreSQL</li>
              </ul>
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
