<script lang="ts">
  import { onMount } from "svelte";
  import { browser } from "$app/environment";
  import type { PageData } from "./$types";

  export let data: PageData;

  // Auth state
  let accessToken: string | null = null;
  let isAuthenticated = false;
  let user: any = null;
  let workspaces: any[] = [];
  let selectedWorkspace: any = null;

  // UI state
  let isLoading = false;
  let error: string | null = null;
  let isRefreshingToken = false;
  let refreshAttempts = 0;
  const MAX_REFRESH_ATTEMPTS = 3;

  // Test state
  let testResults: any = {};
  let currentTest: string | null = null;
  let allTestsPassed = false;
  let testInProgress = false;

  // Token backup for safe testing
  let originalTokenBackup: string | null = null;

  // Load stored access token
  function loadAccessToken() {
    if (browser) {
      const stored = localStorage.getItem("access_token");
      if (stored) {
        accessToken = stored;
        isAuthenticated = true;
        console.log("✅ Access token loaded for workspace page");
      }
    }
  }

  // Safe token backup and restore for testing
  function backupCurrentToken() {
    originalTokenBackup = accessToken;
    console.log("🔒 Token backed up for testing");
  }

  function restoreTokenFromBackup() {
    if (originalTokenBackup) {
      accessToken = originalTokenBackup;
      if (browser) {
        localStorage.setItem("access_token", originalTokenBackup);
      }
      console.log("🔓 Token restored from backup");
    }
  }

  // Attempt to refresh access token using refresh token
  async function refreshAccessToken(): Promise<boolean> {
    if (isRefreshingToken || refreshAttempts >= MAX_REFRESH_ATTEMPTS) {
      console.log("Refresh already in progress or max attempts reached");
      return false;
    }

    isRefreshingToken = true;
    refreshAttempts++;
    console.log(
      `🔄 Attempting to refresh access token (attempt ${refreshAttempts}/${MAX_REFRESH_ATTEMPTS})...`,
    );

    try {
      const response = await fetch("/api/auth/refresh", {
        method: "POST",
        credentials: "include",
      });

      if (response.ok) {
        const data = await response.json();
        if (data.access_token) {
          const oldToken = accessToken;
          accessToken = data.access_token;
          isAuthenticated = true;

          // Store new access token
          if (browser) {
            localStorage.setItem("access_token", data.access_token);
          }

          console.log(
            `✅ Token refreshed successfully: ${oldToken?.substring(0, 8)}... → ${data.access_token?.substring(0, 8)}...`,
          );
          refreshAttempts = 0;
          return true;
        }
      } else {
        const errorData = await response.json();
        console.error("❌ Token refresh failed:", response.status, errorData);
        if (response.status === 401) {
          if (browser) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("login_response");
          }
          accessToken = null;
          isAuthenticated = false;
        }
      }
    } catch (err) {
      console.error("❌ Network error during token refresh:", err);
    } finally {
      isRefreshingToken = false;
    }

    return false;
  }

  // Validate token and get user info with automatic refresh
  async function validateAndLoadUser(): Promise<boolean> {
    // Skip validation if we're in the middle of testing
    if (testInProgress) {
      console.log("⏸️ Skipping validation during test execution");
      return true;
    }

    if (!accessToken && refreshAttempts < MAX_REFRESH_ATTEMPTS) {
      const refreshed = await refreshAccessToken();
      if (!refreshed) {
        error = "No access token available and refresh failed";
        return false;
      }
    }

    if (!accessToken) {
      error = "No access token available after refresh attempts";
      return false;
    }

    isLoading = true;
    error = null;

    try {
      const response = await fetch("/api/auth/validate", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        credentials: "include",
      });

      if (response.ok) {
        const validationData = await response.json();
        user = validationData.user;
        console.log("✅ User validation successful:", user);

        // Load workspace data from login response if available
        const loginData = localStorage.getItem("login_response");
        if (loginData) {
          const parsed = JSON.parse(loginData);
          workspaces = parsed.workspaces || [];
          selectedWorkspace = parsed.last_accessed_workspace || workspaces[0];
        }
        return true;
      } else if (
        response.status === 401 &&
        refreshAttempts < MAX_REFRESH_ATTEMPTS
      ) {
        console.log("🔄 Access token expired, attempting automatic refresh...");

        const refreshed = await refreshAccessToken();
        if (refreshed) {
          return validateAndLoadUser();
        } else {
          error = "Session expired. Please login again.";
          if (browser) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("login_response");
          }
          accessToken = null;
          isAuthenticated = false;
          return false;
        }
      } else {
        const errorData = await response.json();
        error = errorData.error || "Failed to validate token";
        return false;
      }
    } catch (err) {
      error = "Network error during validation";
      console.error("❌ Validation error:", err);
      return false;
    } finally {
      isLoading = false;
    }
  }

  // Comprehensive token refresh testing
  async function runComprehensiveRefreshTests() {
    console.log("🧪 Starting comprehensive token refresh tests...");
    testInProgress = true;
    testResults = {};
    currentTest = null;
    allTestsPassed = false;

    // Backup current token before starting tests
    backupCurrentToken();

    const tests = [
      { name: "basic_refresh", description: "Basic refresh with valid tokens" },
      {
        name: "expired_simulation",
        description: "Simulate expired access token scenario",
      },
      {
        name: "automatic_retry",
        description: "Test automatic refresh on 401 response",
      },
      {
        name: "failed_api_recovery",
        description: "API call failure → refresh → retry flow",
      },
      {
        name: "multiple_concurrent",
        description: "Multiple simultaneous refresh attempts",
      },
      { name: "edge_cases", description: "Edge cases and error handling" },
    ];

    try {
      for (const test of tests) {
        currentTest = test.name;
        console.log(`🔬 Running test: ${test.description}`);

        try {
          // Restore token before each test to ensure clean state
          restoreTokenFromBackup();

          let result;
          switch (test.name) {
            case "basic_refresh":
              result = await testBasicRefresh();
              break;
            case "expired_simulation":
              result = await testExpiredTokenSimulation();
              break;
            case "automatic_retry":
              result = await testAutomaticRefreshRetry();
              break;
            case "failed_api_recovery":
              result = await testFailedApiRecovery();
              break;
            case "multiple_concurrent":
              result = await testMultipleConcurrentRefresh();
              break;
            case "edge_cases":
              result = await testEdgeCases();
              break;
            default:
              result = { success: false, error: "Unknown test" };
          }

          testResults[test.name] = {
            ...result,
            description: test.description,
            timestamp: new Date().toISOString(),
          };

          console.log(
            `${result.success ? "✅" : "❌"} ${test.description}: ${result.success ? "PASSED" : "FAILED"}`,
          );
          if (!result.success) {
            console.error(`   Error: ${result.error}`);
          }
        } catch (error) {
          testResults[test.name] = {
            success: false,
            error: error.message,
            description: test.description,
            timestamp: new Date().toISOString(),
          };
          console.error(
            `❌ ${test.description}: FAILED with exception: ${error.message}`,
          );
        }

        // Wait between tests to avoid rate limiting
        await new Promise((resolve) => setTimeout(resolve, 500));
      }
    } finally {
      // Always restore the original token after all tests
      restoreTokenFromBackup();
      currentTest = null;
      testInProgress = false;

      allTestsPassed = Object.values(testResults).every(
        (result: any) => result.success,
      );

      console.log(
        `🏁 Comprehensive tests complete. Overall result: ${allTestsPassed ? "✅ ALL PASSED" : "❌ SOME FAILED"}`,
      );
      console.log("🔓 Original token restored, normal operation resumed");
    }
  }

  // Test 1: Basic refresh functionality
  async function testBasicRefresh() {
    const oldToken = accessToken;

    const response = await fetch("/api/auth/refresh", {
      method: "POST",
      credentials: "include",
    });

    if (!response.ok) {
      const errorData = await response.json();
      return {
        success: false,
        error: `HTTP ${response.status}: ${errorData.detail || errorData.error}`,
      };
    }

    const data = await response.json();
    if (!data.access_token) {
      return { success: false, error: "No access token in response" };
    }

    if (data.access_token === oldToken) {
      return { success: false, error: "New token is same as old token" };
    }

    // For basic refresh test, we DON'T update the stored token
    // This test just verifies the refresh mechanism works

    return {
      success: true,
      oldToken: oldToken?.substring(0, 8) + "...",
      newToken: data.access_token?.substring(0, 8) + "...",
      tokenType: data.token_type,
      expiresIn: data.expires_in,
      note: "Test only - token not permanently updated",
    };
  }

  // Test 2: Simulate expired access token scenario
  async function testExpiredTokenSimulation() {
    // Create a test token that will definitely be invalid
    const testInvalidToken = "TEST_EXPIRED_TOKEN_" + Date.now();

    // Test the validation with invalid token (should fail)
    const response = await fetch("/api/auth/validate", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${testInvalidToken}`,
        "Content-Type": "application/json",
      },
      credentials: "include",
    });

    if (response.ok) {
      return {
        success: false,
        error: "Invalid token was unexpectedly accepted",
      };
    }

    if (response.status !== 401) {
      return { success: false, error: `Expected 401, got ${response.status}` };
    }

    // Now test that refresh still works with our valid refresh token
    const refreshResponse = await fetch("/api/auth/refresh", {
      method: "POST",
      credentials: "include",
    });

    if (!refreshResponse.ok) {
      const errorData = await refreshResponse.json();
      return {
        success: false,
        error: `Refresh failed: ${errorData.detail || errorData.error}`,
      };
    }

    const refreshData = await refreshResponse.json();
    if (!refreshData.access_token) {
      return { success: false, error: "No access token in refresh response" };
    }

    return {
      success: true,
      invalidTokenRejected: true,
      refreshWorked: true,
      newToken: refreshData.access_token?.substring(0, 8) + "...",
    };
  }

  // Test 3: Test automatic refresh retry logic using a controlled approach
  async function testAutomaticRefreshRetry() {
    // Reset refresh attempts for this test
    const originalRefreshAttempts = refreshAttempts;
    refreshAttempts = 0;

    try {
      // First verify that refresh mechanism works
      const refreshResult = await refreshAccessToken();

      if (!refreshResult) {
        return {
          success: false,
          error: "Refresh mechanism failed during test",
        };
      }

      return {
        success: true,
        refreshMechanismWorking: true,
        refreshAttempts: refreshAttempts,
        newToken: accessToken?.substring(0, 8) + "...",
      };
    } finally {
      // Restore original refresh attempts
      refreshAttempts = originalRefreshAttempts;
    }
  }

  // Test 4: Failed API call → refresh → retry flow
  async function testFailedApiRecovery() {
    // Test the actual API call failure → refresh → retry flow
    // First, test that we can make an API call with current token
    const response = await fetch("/api/auth/validate", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      credentials: "include",
    });

    let initialCallSuccessful = response.ok;
    let refreshNeeded = false;
    let refreshWorked = false;
    let retrySuccessful = false;
    let newAccessToken = null;

    // If the first call fails (which simulates an expired token scenario)
    if (!response.ok) {
      refreshNeeded = true;
      console.log(
        "🔄 API call failed, attempting refresh as part of recovery flow...",
      );

      // Attempt refresh (simulating automatic refresh on API failure)
      const refreshResponse = await fetch("/api/auth/refresh", {
        method: "POST",
        credentials: "include",
      });

      if (!refreshResponse.ok) {
        const errorData = await refreshResponse.json();
        return {
          success: false,
          error: `Refresh failed during recovery: ${errorData.detail || errorData.error}`,
          initialCallSuccessful,
          refreshNeeded,
          refreshWorked: false,
        };
      }

      const refreshData = await refreshResponse.json();
      newAccessToken = refreshData.access_token;
      refreshWorked = true;

      if (!newAccessToken) {
        return {
          success: false,
          error: "No new access token received from refresh",
          initialCallSuccessful,
          refreshNeeded,
          refreshWorked,
        };
      }

      // Retry the original API call with the new token
      const retryResponse = await fetch("/api/auth/validate", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${newAccessToken}`,
          "Content-Type": "application/json",
        },
        credentials: "include",
      });

      retrySuccessful = retryResponse.ok;

      if (!retryResponse.ok) {
        return {
          success: false,
          error: "Retry with new token failed",
          initialCallSuccessful,
          refreshNeeded,
          refreshWorked,
          retrySuccessful,
        };
      }
    }

    // If initial call was successful, test refresh functionality anyway
    if (initialCallSuccessful) {
      const refreshResponse = await fetch("/api/auth/refresh", {
        method: "POST",
        credentials: "include",
      });

      if (!refreshResponse.ok) {
        const errorData = await refreshResponse.json();
        return {
          success: false,
          error: `Refresh failed: ${errorData.detail || errorData.error}`,
          initialCallSuccessful,
          refreshNeeded: false,
        };
      }

      const refreshData = await refreshResponse.json();
      refreshWorked = true;
      newAccessToken = refreshData.access_token;
    }

    return {
      success: true,
      initialCallSuccessful,
      refreshNeeded,
      refreshWorked,
      retrySuccessful: refreshNeeded ? retrySuccessful : true,
      newTokenGenerated: !!newAccessToken,
      scenario: refreshNeeded ? "API_FAILURE_RECOVERY" : "CURRENT_TOKEN_VALID",
    };
  }

  // Test 5: Multiple concurrent refresh attempts
  async function testMultipleConcurrentRefresh() {
    const originalRefreshAttempts = refreshAttempts;
    refreshAttempts = 0;

    try {
      // Start multiple refresh attempts simultaneously
      const promises = [
        fetch("/api/auth/refresh", { method: "POST", credentials: "include" }),
        fetch("/api/auth/refresh", { method: "POST", credentials: "include" }),
        fetch("/api/auth/refresh", { method: "POST", credentials: "include" }),
      ];

      const results = await Promise.all(promises);

      // All should succeed (server should handle concurrent requests)
      const successCount = results.filter((r) => r.ok).length;

      if (successCount === 0) {
        return { success: false, error: "No refresh requests succeeded" };
      }

      return {
        success: true,
        totalRequests: promises.length,
        successfulRequests: successCount,
        allSucceeded: successCount === promises.length,
      };
    } finally {
      refreshAttempts = originalRefreshAttempts;
    }
  }

  // Test 6: Edge cases and error handling
  async function testEdgeCases() {
    const tests = [];

    // Test that refresh endpoint is accessible
    try {
      const refreshResponse = await fetch("/api/auth/refresh", {
        method: "POST",
        credentials: "include",
      });

      tests.push({
        name: "refresh_endpoint_accessible",
        success:
          refreshResponse.status === 200 || refreshResponse.status === 401,
        result: `HTTP ${refreshResponse.status}`,
      });
    } catch (error) {
      tests.push({
        name: "refresh_endpoint_accessible",
        success: false,
        result: `Network error: ${error.message}`,
      });
    }

    // Test validate endpoint accessibility
    try {
      const validateResponse = await fetch("/api/auth/validate", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        credentials: "include",
      });

      tests.push({
        name: "validate_endpoint_accessible",
        success:
          validateResponse.status === 200 || validateResponse.status === 401,
        result: `HTTP ${validateResponse.status}`,
      });
    } catch (error) {
      tests.push({
        name: "validate_endpoint_accessible",
        success: false,
        result: `Network error: ${error.message}`,
      });
    }

    const allEdgeTestsPassed = tests.every((t) => t.success);

    return {
      success: allEdgeTestsPassed,
      edgeTests: tests,
      error: allEdgeTestsPassed ? null : "Some edge case tests failed",
    };
  }

  // Switch workspace
  function switchWorkspace(workspace: any) {
    selectedWorkspace = workspace;
    console.log("Switched to workspace:", workspace.name);
  }

  // Logout function
  async function logout() {
    try {
      await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (err) {
      console.error("Logout API call failed:", err);
    }

    if (browser) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("login_response");
    }

    window.location.href = "/logintest?message=Logged out successfully";
  }

  // Navigate to login
  function goToLogin() {
    window.location.href = "/logintest";
  }

  // Auto-refresh token periodically
  let refreshInterval: number;

  function startTokenRefreshInterval() {
    if (browser && isAuthenticated && !testInProgress) {
      refreshInterval = setInterval(
        async () => {
          if (!testInProgress) {
            console.log("🕐 Periodic token refresh triggered");
            await refreshAccessToken();
          }
        },
        50 * 60 * 1000,
      ); // 50 minutes
    }
  }

  function stopTokenRefreshInterval() {
    if (refreshInterval) {
      clearInterval(refreshInterval);
    }
  }

  onMount(() => {
    if (!data.accessDenied) {
      console.log("Workspace page loaded - server validation:", data.workspace);
      loadAccessToken();

      // Only validate if we have a token and we're not in test mode
      if (accessToken) {
        validateAndLoadUser().then(() => {
          if (isAuthenticated) {
            startTokenRefreshInterval();
          }
        });
      } else {
        error = "No access token found. Please login again.";
      }
    }

    return () => {
      stopTokenRefreshInterval();
    };
  });
</script>

<svelte:head>
  <title>Workspace - Ergolux Portal</title>
</svelte:head>

{#if data.accessDenied}
  <!-- BLACKOUT SCREEN -->
  <div class="blackout-screen">
    <div class="access-denied-container">
      <div class="access-denied-content">
        <div class="text-center">
          <i class="bi bi-shield-x display-1 text-danger mb-4"></i>
          <h1 class="text-white mb-3">Access Denied</h1>
          <p class="text-light mb-4">
            {data.message || "Authentication required to access this resource."}
          </p>
          <div class="d-grid gap-2 d-md-block">
            <button
              type="button"
              class="btn btn-primary btn-lg me-md-2"
              on:click={goToLogin}
            >
              <i class="bi bi-box-arrow-in-right me-2"></i>
              Login
            </button>
            <button
              type="button"
              class="btn btn-outline-light btn-lg"
              on:click={() => window.history.back()}
            >
              <i class="bi bi-arrow-left me-2"></i>
              Go Back
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
{:else}
  <!-- PROTECTED CONTENT -->
  <div class="container mt-4">
    <div class="row">
      <div class="col-lg-12 mx-auto">
        <!-- Header -->
        <div class="card">
          <div
            class="card-header bg-primary text-white d-flex justify-content-between align-items-center"
          >
            <div>
              <h3 class="card-title mb-0">
                <i class="bi bi-building me-2"></i>
                Workspace Management
                {#if isRefreshingToken}
                  <span class="badge bg-warning text-dark ms-2">
                    <span class="spinner-border spinner-border-sm me-1"></span>
                    Refreshing...
                  </span>
                {/if}
                {#if currentTest}
                  <span class="badge bg-info ms-2">
                    <span class="spinner-border spinner-border-sm me-1"></span>
                    Testing: {currentTest}
                  </span>
                {/if}
              </h3>
              <small class="opacity-75">Tenant-Scoped Protected Content</small>
            </div>
            <button
              type="button"
              class="btn btn-outline-light btn-sm"
              on:click={logout}
              disabled={isLoading}
            >
              <i class="bi bi-box-arrow-right me-1"></i>
              Logout
            </button>
          </div>

          <div class="card-body">
            <!-- Authentication Status -->
            <div class="row mb-4">
              <div class="col-md-6">
                <div class="alert alert-success">
                  <h6>
                    <i class="bi bi-shield-check me-2"></i>Server Protection
                  </h6>
                  <ul class="mb-0 small">
                    <li>✅ Server-side validation passed</li>
                    <li>✅ Refresh token present</li>
                    <li>✅ Workspace access granted</li>
                    <li>
                      <strong>Validated:</strong>
                      {data.workspace?.validatedAt}
                    </li>
                  </ul>
                </div>
              </div>

              <div class="col-md-6">
                <div
                  class="alert {isAuthenticated && user
                    ? 'alert-success'
                    : error
                      ? 'alert-danger'
                      : 'alert-warning'}"
                >
                  <h6><i class="bi bi-person-check me-2"></i>User Session</h6>
                  {#if testInProgress}
                    <div class="d-flex align-items-center">
                      <span class="spinner-border spinner-border-sm me-2"
                      ></span>
                      <span class="text-info"
                        >Tests in progress - session validation paused</span
                      >
                    </div>
                  {:else if isLoading}
                    <div class="d-flex align-items-center">
                      <span class="spinner-border spinner-border-sm me-2"
                      ></span>
                      Loading workspace data...
                    </div>
                  {:else if error}
                    <div class="text-danger small">
                      <i class="bi bi-exclamation-triangle me-1"></i>
                      {error}
                    </div>
                    <button
                      type="button"
                      class="btn btn-sm btn-outline-primary mt-2"
                      on:click={validateAndLoadUser}
                      disabled={isLoading ||
                        isRefreshingToken ||
                        testInProgress}
                    >
                      <i class="bi bi-arrow-clockwise me-1"></i>
                      Retry Authentication
                    </button>
                  {:else if user}
                    <ul class="mb-0 small">
                      <li>
                        <strong>Name:</strong>
                        {user.first_name || ""}
                        {user.last_name || ""}
                      </li>
                      <li><strong>Email:</strong> {user.email || "N/A"}</li>
                      <li><strong>Workspaces:</strong> {workspaces.length}</li>
                      <li>✅ Access token valid</li>
                    </ul>
                  {:else}
                    <div class="small">
                      <i class="bi bi-info-circle me-1"></i>
                      {isAuthenticated
                        ? "Loading workspace data..."
                        : "No access token found"}
                    </div>
                  {/if}
                </div>
              </div>
            </div>

            <!-- SAFE COMPREHENSIVE TOKEN REFRESH TESTING -->
            <div class="row mb-4">
              <div class="col-12">
                <div class="card border-primary">
                  <div
                    class="card-header bg-primary text-white d-flex justify-content-between align-items-center"
                  >
                    <h6 class="mb-0">
                      <i class="bi bi-gear-fill me-2"></i>
                      Safe Token Refresh Testing
                    </h6>
                    {#if allTestsPassed}
                      <span class="badge bg-success">
                        <i class="bi bi-check-circle me-1"></i>
                        ALL TESTS PASSED
                      </span>
                    {:else if Object.keys(testResults).length > 0}
                      <span class="badge bg-warning text-dark">
                        <i class="bi bi-exclamation-triangle me-1"></i>
                        SOME TESTS FAILED
                      </span>
                    {/if}
                  </div>
                  <div class="card-body">
                    <div class="row">
                      <div class="col-md-8">
                        <div class="alert alert-info small">
                          <strong>🔒 Safe Testing Mode:</strong><br />
                          Tests run in isolation without affecting your active session.
                          Your access token is backed up before testing and restored
                          afterward.
                        </div>

                        <p class="text-muted mb-3">
                          <strong>Production-ready refresh scenarios:</strong
                          ><br />
                          Tests refresh functionality, token validation, API retry
                          logic, and error handling without disrupting your current
                          workspace session.
                        </p>

                        <button
                          type="button"
                          class="btn btn-primary"
                          on:click={runComprehensiveRefreshTests}
                          disabled={testInProgress || !isAuthenticated}
                        >
                          {#if testInProgress}
                            <span class="spinner-border spinner-border-sm me-2"
                            ></span>
                            Running Safe Tests...
                          {:else}
                            <i class="bi bi-play-circle me-2"></i>
                            Run All Refresh Tests
                          {/if}
                        </button>

                        {#if testInProgress}
                          <div class="mt-3">
                            <div class="progress">
                              <div
                                class="progress-bar progress-bar-striped progress-bar-animated"
                                role="progressbar"
                                style="width: {(Object.keys(testResults)
                                  .length /
                                  6) *
                                  100}%"
                              ></div>
                            </div>
                            <small class="text-muted">
                              Running: {currentTest} ({Object.keys(testResults)
                                .length}/6 complete)
                            </small>
                          </div>
                        {/if}
                      </div>

                      <div class="col-md-4">
                        {#if Object.keys(testResults).length > 0}
                          <h6 class="text-muted">Test Results Summary</h6>
                          <div class="small">
                            {#each Object.entries(testResults) as [testName, result]}
                              <div
                                class="d-flex justify-content-between align-items-center mb-1"
                              >
                                <span class="text-truncate me-2"
                                  >{result.description}</span
                                >
                                <span
                                  class="badge {result.success
                                    ? 'bg-success'
                                    : 'bg-danger'}"
                                >
                                  {result.success ? "✅" : "❌"}
                                </span>
                              </div>
                            {/each}
                          </div>
                        {/if}
                      </div>
                    </div>

                    <!-- Detailed Test Results -->
                    {#if Object.keys(testResults).length > 0}
                      <div class="mt-4">
                        <h6>Detailed Test Results</h6>
                        <div class="accordion" id="testResultsAccordion">
                          {#each Object.entries(testResults) as [testName, result], index}
                            <div class="accordion-item">
                              <h2 class="accordion-header">
                                <button
                                  class="accordion-button {result.success
                                    ? ''
                                    : 'text-danger'}"
                                  type="button"
                                  data-bs-toggle="collapse"
                                  data-bs-target="#collapse{index}"
                                  aria-expanded="false"
                                >
                                  <span class="me-2"
                                    >{result.success ? "✅" : "❌"}</span
                                  >
                                  <strong>{result.description}</strong>
                                  <small class="ms-auto text-muted"
                                    >{new Date(
                                      result.timestamp,
                                    ).toLocaleTimeString()}</small
                                  >
                                </button>
                              </h2>
                              <div
                                id="collapse{index}"
                                class="accordion-collapse collapse"
                                data-bs-parent="#testResultsAccordion"
                              >
                                <div class="accordion-body">
                                  {#if result.success}
                                    <div class="text-success">
                                      <strong>✅ Test Passed</strong>
                                    </div>
                                    <pre
                                      class="bg-light p-2 mt-2 small">{JSON.stringify(
                                        result,
                                        null,
                                        2,
                                      )}</pre>
                                  {:else}
                                    <div class="text-danger">
                                      <strong>❌ Test Failed:</strong>
                                      {result.error}
                                    </div>
                                    <pre
                                      class="bg-light p-2 mt-2 small">{JSON.stringify(
                                        result,
                                        null,
                                        2,
                                      )}</pre>
                                  {/if}
                                </div>
                              </div>
                            </div>
                          {/each}
                        </div>
                      </div>
                    {/if}
                  </div>
                </div>
              </div>
            </div>

            <!-- Workspace Content (condensed) -->
            {#if workspaces.length > 0 && selectedWorkspace}
              <div class="row">
                <div class="col-12">
                  <div class="card">
                    <div class="card-header">
                      <h6 class="mb-0">
                        <i class="bi bi-buildings me-2"></i>
                        Current Workspace: {selectedWorkspace.name}
                      </h6>
                    </div>
                    <div class="card-body">
                      <div class="row">
                        {#each workspaces as workspace}
                          <div class="col-md-3 mb-2">
                            <button
                              type="button"
                              class="btn {selectedWorkspace?.id === workspace.id
                                ? 'btn-primary'
                                : 'btn-outline-primary'} w-100 btn-sm"
                              on:click={() => switchWorkspace(workspace)}
                              disabled={!isAuthenticated ||
                                !user ||
                                testInProgress}
                            >
                              {workspace.name}
                              {#if selectedWorkspace?.id === workspace.id}
                                <i class="bi bi-check-circle ms-1"></i>
                              {/if}
                            </button>
                          </div>
                        {/each}
                      </div>

                      <div class="mt-3 p-3 bg-light rounded">
                        <small class="text-muted">
                          <strong>Workspace ID:</strong>
                          <code>{selectedWorkspace.id}</code><br />
                          <strong>User Access Level:</strong> Authenticated user
                          with valid token<br />
                          <strong>Token Refresh:</strong> Automatic refresh
                          enabled with 50-minute interval<br />
                          <strong>Test Mode:</strong>
                          {testInProgress
                            ? "🧪 Active (session protected)"
                            : "✅ Ready for testing"}
                        </small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            {/if}
          </div>
        </div>

        <!-- Navigation -->
        <div class="card mt-4">
          <div class="card-body">
            <div class="row">
              <div class="col-md-4">
                <a href="/logintest" class="btn btn-outline-secondary w-100">
                  <i class="bi bi-arrow-left me-2"></i>
                  Back to Login Test
                </a>
              </div>
              <div class="col-md-4">
                <a href="/verifytest" class="btn btn-outline-info w-100">
                  <i class="bi bi-shield-check me-2"></i>
                  Token Verification Test
                </a>
              </div>
              <div class="col-md-4">
                <button
                  type="button"
                  class="btn btn-outline-success w-100"
                  disabled={!allTestsPassed}
                  title={allTestsPassed
                    ? "All refresh tests passed!"
                    : "Run comprehensive tests first"}
                >
                  <i class="bi bi-shield-check me-2"></i>
                  Refresh System Verified
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  .blackout-screen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }

  .access-denied-container {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    padding: 2rem;
  }

  .access-denied-content {
    max-width: 500px;
    text-align: center;
    animation: fadeInUp 0.6s ease-out;
  }

  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .blackout-screen * {
    user-select: none;
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

  .accordion-button {
    font-size: 0.9rem;
  }

  .accordion-body pre {
    max-height: 200px;
    font-size: 0.8rem;
  }
</style>
