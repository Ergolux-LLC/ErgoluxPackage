<script lang="ts">
  import FadeTransition from "./FadeTransition.svelte";
  import PasswordEntry from "./passwordEntry.svelte";
  import { onMount, tick } from "svelte";
  import { apiClient } from "$lib/api/client";
  import { config, shouldLog } from "$lib/config/environment";
  import { goto } from "$app/navigation";

  // Helper function to log client-side events
  function logClient(event: string, data: any) {
    if (!shouldLog()) return;
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [CLIENT] [SETUP] [${event}]`, data);
  }

  // Step 4: Success - redirect to app or login
  async function handleFinish() {
    logClient("SetupComplete", {
      email,
      authenticated: apiClient.isAuthenticated(),
    });

    if (apiClient.isAuthenticated()) {
      // User is logged in, go to dashboard
      goto("/directory");
    } else {
      // User needs to log in manually
      goto("/login");
    }
  }

  export let code = "";
  export let apiCheckCode: (code: string) => Promise<{
    valid?: boolean;
    email?: string;
    workspace_id?: number | null;
    error?: string;
  }>;

  let step = 0;
  let error = "";
  let loading = false;
  let email = "";
  let workspace_id: number | null = null;
  let workspace_name = "";
  let firstName = "";
  let lastName = "";
  let workspaceName = "";

  let joiningCompany: boolean | null = null;
  let password = "";
  let firstNameInput: HTMLInputElement;

  // Authentication verification state
  let authVerificationLoading = false;
  let authStatus: any = null;
  let authError: string | null = null;

  // Function to verify authentication with web-bff
  async function verifyAuthentication() {
    authVerificationLoading = true;
    authError = null;
    authStatus = null;

    logClient("VerifyingAuthentication", {
      hasAccessToken: !!apiClient.getAccessToken(),
      tokenPreview: apiClient.getAccessToken()?.substring(0, 12) + "...",
    });

    try {
      const result = await apiClient.validateAuth();
      logClient("AuthVerificationResult", result);

      authStatus = result;

      // Check if authentication was successful
      // For 200 responses, API client returns the data directly: { user: {...} }
      // For errors, it returns { success: false, error: "..." }
      if (result && result.user && result.user.id) {
        logClient("AuthVerificationSuccess", {
          hasUser: true,
          userId: result.user.id,
          userEmail: result.user.email,
          workspace: result.workspace,
        });

        // User is already authenticated! Redirect to protected area
        logClient("AutoRedirectingAuthenticatedUser", {
          userId: result.user.id,
          redirecting: true,
        });

        // Add a small delay to show the success state, then redirect
        setTimeout(() => {
          window.location.href = "/dashboard";
        }, 2000);
      } else if (result && result.success === false) {
        authError = result.error || "Authentication verification failed";
        logClient("AuthVerificationFailed", {
          error: authError,
          result: result,
        });
      } else {
        authError =
          "Authentication verification failed - no user data returned";
        logClient("AuthVerificationFailed", {
          error: authError,
          result: result,
          hasUser: !!result?.user,
          resultKeys: result ? Object.keys(result) : [],
        });
      }
    } catch (err) {
      authError = `Verification failed: ${err instanceof Error ? err.message : "Unknown error"}`;
      logClient("AuthVerificationError", { error: err });
    } finally {
      authVerificationLoading = false;
    }
  }

  // Generate random names for development mode
  function generateRandomName() {
    const firstNames = [
      "Aria",
      "Thane",
      "Luna",
      "Kael",
      "Seraphina",
      "Orion",
      "Lyra",
      "Zephyr",
      "Cassia",
      "Darius",
      "Ember",
      "Fenris",
      "Gwendolyn",
      "Jasper",
      "Iris",
      "Leander",
      "Nyx",
      "Rowan",
      "Sage",
      "Talon",
      "Vera",
      "Wren",
      "Xara",
      "Ysabel",
      "Zara",
      "Alaric",
      "Celeste",
      "Dorian",
      "Evelyn",
      "Gareth",
    ];

    const lastNames = [
      "Stormwind",
      "Nightshade",
      "Goldleaf",
      "Ironforge",
      "Silverbrook",
      "Moonwhisper",
      "Starweaver",
      "Shadowmere",
      "Brightblade",
      "Darkwood",
      "Frostborn",
      "Flameheart",
      "Stormcaller",
      "Windwalker",
      "Earthshaker",
      "Skyforge",
      "Thornfield",
      "Ravencrest",
      "Lightbringer",
      "Duskfall",
    ];

    const randomFirst =
      firstNames[Math.floor(Math.random() * firstNames.length)];
    const randomLast = lastNames[Math.floor(Math.random() * lastNames.length)];

    return { firstName: randomFirst, lastName: randomLast };
  }

  // Generate random fantasy workspace name for development mode
  function generateRandomWorkspaceName() {
    const adjectives = [
      "Mystic",
      "Ancient",
      "Golden",
      "Silver",
      "Crystal",
      "Shadow",
      "Twilight",
      "Starlight",
      "Ethereal",
      "Arcane",
      "Divine",
      "Celestial",
      "Enchanted",
      "Legendary",
      "Sacred",
      "Noble",
      "Forgotten",
      "Hidden",
      "Emerald",
      "Crimson",
      "Azure",
      "Violet",
      "Radiant",
      "Shimmering",
      "Whispering",
      "Dancing",
      "Soaring",
      "Blazing",
      "Frozen",
      "Thunder",
    ];

    const nouns = [
      "Dragons",
      "Phoenix",
      "Griffins",
      "Unicorns",
      "Sages",
      "Knights",
      "Wizards",
      "Guardians",
      "Spirits",
      "Realms",
      "Kingdoms",
      "Temples",
      "Towers",
      "Sanctuaries",
      "Citadels",
      "Bastions",
      "Archives",
      "Chronicles",
      "Legends",
      "Mysteries",
      "Prophecies",
      "Artifacts",
      "Relics",
      "Gems",
      "Stars",
      "Moons",
      "Suns",
      "Winds",
      "Flames",
      "Waters",
      "Mountains",
      "Forests",
      "Ventures",
      "Enterprises",
      "Guild",
      "Order",
      "Alliance",
      "Brotherhood",
      "Fellowship",
      "Circle",
    ];

    const randomAdjective =
      adjectives[Math.floor(Math.random() * adjectives.length)];
    const randomNoun = nouns[Math.floor(Math.random() * nouns.length)];

    return `${randomAdjective} ${randomNoun}`;
  }

  // Initialize random names in development mode
  if (config.isDevelopment) {
    const randomNames = generateRandomName();
    firstName = randomNames.firstName;
    lastName = randomNames.lastName;
    workspaceName = generateRandomWorkspaceName();
    console.log("[SETUP DIALOG] Dev mode: Generated random names:", {
      firstName,
      lastName,
      workspaceName,
    });
  }

  // Step 0: Code entry and validation (auto-submit)
  async function handleCodeSubmit() {
    loading = true;
    error = "";
    try {
      logClient("ValidateCode", { code: code ? "[PRESENT]" : "[MISSING]" });
      const result = await apiCheckCode(code);

      console.log("[SETUP DIALOG] apiCheckCode result:", result);
      console.log("[SETUP DIALOG] result.valid:", result.valid);
      console.log("[SETUP DIALOG] !result.valid:", !result.valid);

      if (!result.valid) {
        console.log(
          "[SETUP DIALOG] Code validation failed, error:",
          result.error
        );
        error =
          result.error || "Invalid or expired code. Please go back to signup.";
        loading = false;
        await goToStep(-1);
        return;
      }

      console.log(
        "[SETUP DIALOG] Code validation passed, proceeding with setup"
      );
      email = result.email || "";
      workspace_id = result.workspace_id || null;

      // Check if this is a workspace invitation
      if (workspace_id) {
        logClient("WorkspaceInvitation", { workspace_id });
        // Validate the workspace and get its name
        try {
          const workspaceResult =
            await apiClient.validateWorkspaceForSignup(workspace_id);
          if (workspaceResult.valid) {
            workspace_name =
              workspaceResult.workspace_name || "Unknown Workspace";
            joiningCompany = true;
          } else {
            error = "The workspace invitation is no longer valid.";
            loading = false;
            await goToStep(-1);
            return;
          }
        } catch (e) {
          logClient("WorkspaceValidationError", e);
          error = "Error validating workspace invitation.";
          loading = false;
          await goToStep(-1);
          return;
        }
      } else {
        joiningCompany = false;
      }

      logClient("CodeValidated", { email, workspace_id, joiningCompany });
      await goToStep(1);
    } catch (e) {
      logClient("CodeValidationError", e);
      error = "Error validating code.";
      await goToStep(-1);
    }
    loading = false;
  }

  // Helper to transition to next step with fade-out/fade-in
  let visibleStep: number | null = 0; // Only this step is mounted
  let transitioning = false;
  let fadeRef: any;
  let fadeOutResolver: ((value?: unknown) => void) | null = null;
  function handleFadeComplete() {
    if (fadeOutResolver) {
      fadeOutResolver();
      fadeOutResolver = null;
    }
  }
  async function goToStep(nextStep: number) {
    transitioning = true;
    if (fadeRef && fadeRef.fadeOut) {
      await new Promise((resolve) => {
        fadeOutResolver = resolve;
        fadeRef.fadeOut();
      });
    }
    visibleStep = null; // Unmount dialog after fade out
    await tick();
    step = nextStep;
    visibleStep = nextStep;
    transitioning = false;

    // Focus management after transition
    if (nextStep === 1) {
      await tick(); // Wait for DOM update
      setTimeout(() => {
        if (firstNameInput) {
          firstNameInput.focus();
        }
      }, 100); // Small delay to ensure element is fully rendered
    }
  }
  onMount(() => {
    // If code is missing, show error and block setup
    if (!code) {
      error = "No setup code found. Please use a valid invite link.";
      loading = false;
      step = -1;
      visibleStep = -1;
      return;
    }
    // If code is present, auto-submit
    if (step === 0) {
      handleCodeSubmit();
    }
  });

  // Step 1: Name entry
  async function handleNameSubmit() {
    error = "";
    if (!firstName.trim()) {
      error = "Please enter your first name.";
      return;
    }
    if (!lastName.trim()) {
      error = "Please enter your last name.";
      return;
    }
    logClient("NameSubmit", { firstName, lastName });
    await goToStep(2);
  }

  // Step 2: Workspace selection/confirmation
  function handleWorkspaceSubmit() {
    error = "";
    if (!joiningCompany && !workspaceName.trim()) {
      error = "Please enter a workspace name.";
      return;
    }
    goToStep(3); // Go to password entry step
  }

  // Step 3: Password entry and final submission
  async function handlePasswordSubmit(e: Event) {
    if (!password || password.length < 8) {
      error = "Password must be at least 8 characters long.";
      return;
    }

    loading = true;
    error = "";

    try {
      logClient("CompleteUserSetup", {
        email,
        firstName,
        lastName,
        workspace_id,
        workspaceName: joiningCompany ? undefined : workspaceName,
      });

      const userData = {
        first_name: firstName,
        last_name: lastName,
        email,
        password,
        workspace_id: workspace_id ? workspace_id.toString() : null,
        new_workspace_name: joiningCompany ? null : workspaceName,
      };

      const result = await apiClient.completeUserSetup(userData);

      logClient("UserSetupRawResult", {
        success: result.success,
        has_access_token: !!result.access_token,
        access_token_preview: result.access_token
          ? `${result.access_token.substring(0, 12)}...`
          : null,
        token_type: result.token_type,
        expires_in: result.expires_in,
        user_id: result.user_id,
        workspace_id: result.workspace_id,
      });

      if (result.success) {
        logClient("UserSetupComplete", {
          user_id: result.user_id,
          workspace_id: result.workspace_id,
          authenticated: !!result.access_token,
        });

        // Check if user was automatically logged in
        if (result.access_token) {
          logClient("AutoLogin", {
            token_present: true,
            token_type: result.token_type,
            expires_in: result.expires_in,
            token_stored_in_session: !!sessionStorage.getItem("access_token"),
            token_from_api_client: !!apiClient.getAccessToken(),
          });

          // Go to success step and verify authentication
          await goToStep(4);

          // Verify authentication in the background
          setTimeout(() => {
            verifyAuthentication();
          }, 500);
        } else {
          logClient("NoAutoLogin", {
            reason: "No access_token in response",
            response_keys: Object.keys(result),
          });
          // No auto-login, show success and manual login option
          await goToStep(4);
        }
      } else {
        error =
          result.error_details || "Failed to complete setup. Please try again.";
        logClient("UserSetupError", { error: result.error_details });
      }
    } catch (e) {
      logClient("UserSetupError", e);
      error = "Network error. Please try again.";
    }

    loading = false;
  }
</script>

{#key visibleStep}
  {#if visibleStep !== null}
    <FadeTransition
      fadeInDuration={1800}
      fadeOutDuration={1800}
      bind:this={fadeRef}
      on:complete={handleFadeComplete}
    >
      <div class="dialog-container">
        {#if visibleStep === -1}
          <h2>Setup Error</h2>
          <div class="error">{error}</div>
        {:else if visibleStep === 1}
          <form on:submit|preventDefault={handleNameSubmit}>
            <h2>Welcome!</h2>
            <p>
              Your account will be ready after a few quick questions.<br
              />First, what should we call you?
            </p>
            <div class="name-fields">
              <input
                type="text"
                bind:value={firstName}
                placeholder="First Name"
                bind:this={firstNameInput}
              />
              <input
                type="text"
                bind:value={lastName}
                placeholder="Last Name"
              />
            </div>
            <button type="submit">Continue</button>
            {#if error}<div class="error">{error}</div>{/if}
            {#if loading}<div>Loading...</div>{/if}
          </form>
        {:else if visibleStep === 2}
          <form on:submit|preventDefault={handleWorkspaceSubmit}>
            {#if joiningCompany === true}
              <h2>Join Workspace</h2>
              <p>You were invited to join <b>{workspace_name}</b>.</p>
              <button
                type="button"
                on:click={() => {
                  joiningCompany = false;
                  workspaceName = "";
                }}>Start my own workspace instead</button
              >
              <button type="submit">Continue</button>
            {:else}
              <h2>Create Your Workspace</h2>
              <input
                type="text"
                bind:value={workspaceName}
                placeholder="Workspace Name"
              />
              <p>
                If you were trying to join a company's workspace, ask them for
                an invite link.
              </p>
              <button type="submit">Continue</button>
            {/if}
            {#if error}<div class="error">{error}</div>{/if}
          </form>
        {:else if visibleStep === 3}
          <form on:submit|preventDefault={handlePasswordSubmit}>
            <h2>Set Your Password</h2>
            <PasswordEntry bind:value={password} />
            <button type="submit" disabled={loading}>
              {loading ? "Creating Account..." : "Continue"}
            </button>
            {#if error}<div class="error">{error}</div>{/if}
            {#if loading}<div>
                Please wait while we set up your account...
              </div>{/if}
          </form>
        {:else if visibleStep === 4}
          <h2>Welcome to Ergolux CRM!</h2>
          <p>Your account has been successfully created.</p>
          <p><strong>Name:</strong> {firstName} {lastName}</p>
          <p><strong>Email:</strong> {email}</p>
          <p>
            <strong>Workspace:</strong>
            {joiningCompany === true ? workspace_name : workspaceName}
          </p>

          <!-- Authentication Verification Section -->
          <div class="auth-verification-section">
            <h3>Authentication Status</h3>

            {#if authVerificationLoading}
              <div class="loading-section">
                <p>🔍 Verifying authentication...</p>
                <div class="verification-steps">
                  <div class="step">✓ Checking for access token</div>
                  <div class="step">🔄 Calling /auth/validate endpoint</div>
                  <div class="step">⏳ Waiting for server response</div>
                </div>
              </div>
            {:else if authError}
              <div class="error-section">
                <h4>❌ Authentication Verification Failed</h4>
                <p>{authError}</p>

                <!-- Debug Information -->
                <details class="debug-info">
                  <summary>🔧 Debug Information</summary>
                  <div class="debug-content">
                    <div class="debug-item">
                      <strong>Has Access Token:</strong>
                      <code>{!!apiClient.getAccessToken()}</code>
                    </div>
                    {#if authStatus}
                      <div class="debug-item">
                        <strong>Raw Response:</strong>
                        <pre><code>{JSON.stringify(authStatus, null, 2)}</code
                          ></pre>
                      </div>
                    {/if}
                  </div>
                </details>

                <button on:click={verifyAuthentication} class="retry-btn"
                  >Retry Verification</button
                >
                <button on:click={handleFinish}>Continue to Login</button>
              </div>
            {:else if authStatus}
              <div class="auth-status-section">
                <div class="status-summary">
                  <div class="status-item">
                    <strong>Authenticated:</strong>
                    <span
                      class="status {authStatus.user?.id ? 'success' : 'error'}"
                    >
                      {authStatus.user?.id ? "✅ Yes" : "❌ No"}
                    </span>
                  </div>

                  {#if authStatus?.user}
                    <div class="status-item">
                      <strong>User ID:</strong>
                      <code
                        >{authStatus.user.id ||
                          authStatus.user.user_id ||
                          "N/A"}</code
                      >
                    </div>
                    <div class="status-item">
                      <strong>User Email:</strong>
                      <code>{authStatus.user.email || "N/A"}</code>
                    </div>
                  {/if}

                  {#if authStatus?.workspace}
                    <div class="status-item">
                      <strong>Workspace:</strong>
                      <code
                        >{authStatus.workspace.name ||
                          authStatus.workspace.id ||
                          "N/A"}</code
                      >
                    </div>
                  {/if}

                  <div class="status-item">
                    <strong>Access Token:</strong>
                    <span
                      class="status {apiClient.getAccessToken()
                        ? 'success'
                        : 'error'}"
                    >
                      {apiClient.getAccessToken() ? "✅ Present" : "❌ Missing"}
                    </span>
                    {#if apiClient.getAccessToken()}
                      <code class="token-preview">
                        {apiClient.getAccessToken()?.substring(0, 12)}...
                      </code>
                    {/if}
                  </div>

                  <div class="status-item">
                    <strong>API Client Authenticated:</strong>
                    <span
                      class="status {apiClient.isAuthenticated()
                        ? 'success'
                        : 'error'}"
                    >
                      {apiClient.isAuthenticated() ? "✅ Yes" : "❌ No"}
                    </span>
                  </div>
                </div>

                <!-- Verification Logs -->
                <details class="verification-logs">
                  <summary>📋 Verification Logs & Debug Info</summary>
                  <div class="log-content">
                    <div class="log-section">
                      <h5>🔧 API Client Status</h5>
                      <div class="log-item">
                        <strong>Has Access Token:</strong>
                        {!!apiClient.getAccessToken()}
                      </div>
                      <div class="log-item">
                        <strong>Token Preview:</strong>
                        {apiClient.getAccessToken()?.substring(0, 12) ||
                          "None"}...
                      </div>
                      <div class="log-item">
                        <strong>Is Authenticated:</strong>
                        {apiClient.isAuthenticated()}
                      </div>
                    </div>

                    <div class="log-section">
                      <h5>🌐 API Response Details</h5>
                      <div class="log-item">
                        <strong>Response Type:</strong>
                        {typeof authStatus}
                      </div>
                      <div class="log-item">
                        <strong>Has User Data:</strong>
                        {!!authStatus?.user}
                      </div>
                      <div class="log-item">
                        <strong>User ID Present:</strong>
                        {!!authStatus?.user?.id}
                      </div>
                      {#if authStatus?.user?.id}
                        <div class="log-item">
                          <strong>User ID:</strong>
                          {authStatus.user.id}
                        </div>
                      {/if}
                    </div>
                  </div>
                </details>

                <div class="json-display">
                  <strong>Full Response:</strong>
                  <pre><code>{JSON.stringify(authStatus, null, 2)}</code></pre>
                </div>

                {#if authStatus?.user?.id}
                  <div class="success-actions">
                    <p class="success-text">
                      🎉 Authentication verified! You're already logged in.
                    </p>
                    <p class="auto-redirect-text">
                      Redirecting to your dashboard in 2 seconds...
                    </p>
                    <button
                      on:click={() => (window.location.href = "/dashboard")}
                      class="primary-btn">Go to Dashboard Now</button
                    >
                  </div>
                {:else}
                  <div class="manual-login">
                    <p>
                      Authentication verification completed, but login is
                      required.
                    </p>
                    <button on:click={handleFinish}>Go to Login</button>
                  </div>
                {/if}
              </div>
            {:else}
              <!-- Initial state - show verification button -->
              <div class="verification-pending">
                <button on:click={verifyAuthentication} class="verify-btn">
                  🔍 Verify Authentication
                </button>
                <p>
                  Click to verify your authentication status with the server.
                </p>
              </div>
            {/if}
          </div>
        {/if}
      </div>
    </FadeTransition>
  {/if}
{/key}

<style>
  :global(body) {
    background: #181a1b !important;
    color: #f3f3f3 !important;
    font-family: system-ui, sans-serif;
    margin: 0;
    padding: 0;
  }

  :global(html) {
    background: #181a1b !important;
  }

  .dialog-container {
    max-width: 400px;
    margin: 2rem auto;
    padding: 2rem;
    background: #23272b;
    border-radius: 12px;
    box-shadow: 0 2px 16px rgba(0, 0, 0, 0.2);
    color: #f3f3f3;
  }

  .dialog-container h2 {
    color: #f3f3f3;
    margin-bottom: 1rem;
  }

  .dialog-container p {
    color: #f3f3f3;
    margin-bottom: 1rem;
  }

  input {
    display: block;
    width: 100%;
    margin-bottom: 1rem;
    padding: 0.7rem;
    border-radius: 7px;
    border: 1px solid #444;
    background: #181a1b;
    color: #f3f3f3;
    box-sizing: border-box;
  }

  input:focus {
    outline: none;
    border-color: #4f8cff;
    box-shadow: 0 0 0 2px rgba(79, 140, 255, 0.2);
  }

  button {
    width: 100%;
    padding: 0.7rem;
    border-radius: 7px;
    background: #4f8cff;
    color: #fff;
    font-weight: bold;
    border: none;
    margin-bottom: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  button:hover {
    background: #3a7ae4;
  }

  button:disabled {
    background: #666;
    cursor: not-allowed;
  }

  .error {
    color: #ff6b6b;
    margin-top: 0.5rem;
    background: rgba(255, 107, 107, 0.1);
    padding: 0.5rem;
    border-radius: 4px;
  }

  .name-fields {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .name-fields input {
    flex: 1;
    margin-bottom: 0;
  }

  .success-message {
    background: rgba(76, 175, 80, 0.1);
    border: 1px solid #4caf50;
    border-radius: 6px;
    padding: 1rem;
    margin: 1rem 0;
    text-align: center;
  }

  .success-message p {
    color: #4caf50;
    margin: 0.5rem 0;
    font-weight: bold;
  }

  .auth-verification-section {
    background: rgba(79, 140, 255, 0.1);
    border: 1px solid #4f8cff;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
  }

  .auth-verification-section h3 {
    color: #4f8cff;
    margin: 0 0 1rem 0;
    font-size: 1.1rem;
  }

  .loading-section {
    text-align: center;
    padding: 1rem;
    color: #b3e5fc;
  }

  .error-section {
    background: rgba(255, 107, 107, 0.1);
    border: 1px solid #ff6b6b;
    border-radius: 6px;
    padding: 1rem;
    margin: 0.5rem 0;
  }

  .error-section h4 {
    color: #ff6b6b;
    margin: 0 0 0.5rem 0;
  }

  .retry-btn,
  .verify-btn {
    background: #ffc107;
    color: #000;
    margin-right: 0.5rem;
  }

  .primary-btn {
    background: #4caf50;
    font-weight: bold;
    padding: 0.8rem 1.5rem;
  }

  .auth-status-section {
    margin: 0.5rem 0;
  }

  .status-summary {
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

  .json-display {
    background: #1a1a1a;
    border-radius: 4px;
    padding: 1rem;
    overflow-x: auto;
    margin: 1rem 0;
  }

  .json-display pre {
    margin: 0;
    color: #e0e0e0;
    font-family: "Courier New", monospace;
    font-size: 0.8rem;
    line-height: 1.4;
  }

  .success-actions {
    text-align: center;
    margin: 1rem 0;
  }

  .success-text {
    color: #4caf50;
    font-weight: bold;
    margin-bottom: 1rem;
  }

  .auto-redirect-text {
    color: #b3e5fc;
    font-style: italic;
    margin: 0.5rem 0;
    font-size: 0.9rem;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%,
    100% {
      opacity: 1;
    }
    50% {
      opacity: 0.6;
    }
  }

  .manual-login {
    text-align: center;
    margin: 1rem 0;
  }

  .verification-pending {
    text-align: center;
    margin: 1rem 0;
  }

  .verification-pending p {
    color: #b3e5fc;
    margin-top: 0.5rem;
    font-size: 0.9rem;
  }

  /* Debug and verification logging styles */
  .verification-steps {
    margin: 1rem 0;
    padding: 0.5rem;
    background: rgba(79, 140, 255, 0.1);
    border-radius: 6px;
  }

  .verification-steps .step {
    padding: 0.25rem 0;
    font-size: 0.9rem;
    color: #b3e5fc;
  }

  .debug-info,
  .verification-logs {
    margin: 1rem 0;
    border: 1px solid #444;
    border-radius: 6px;
    background: #1a1d21;
  }

  .debug-info summary,
  .verification-logs summary {
    padding: 0.75rem;
    cursor: pointer;
    font-weight: bold;
    border-bottom: 1px solid #444;
    background: #23272b;
    border-radius: 6px 6px 0 0;
  }

  .debug-info[open] summary,
  .verification-logs[open] summary {
    border-radius: 6px 6px 0 0;
  }

  .debug-content,
  .log-content {
    padding: 1rem;
  }

  .debug-item,
  .log-item {
    margin: 0.5rem 0;
    font-size: 0.9rem;
  }

  .log-section {
    margin: 1rem 0;
    padding: 0.75rem;
    background: rgba(79, 140, 255, 0.05);
    border-radius: 4px;
    border-left: 3px solid #4f8cff;
  }

  .log-section h5 {
    margin: 0 0 0.5rem 0;
    color: #4f8cff;
    font-size: 0.9rem;
  }

  .token-preview {
    margin-left: 0.5rem;
    font-size: 0.8rem;
    opacity: 0.7;
  }

  .json-display pre {
    background: #1a1d21;
    padding: 1rem;
    border-radius: 4px;
    border: 1px solid #444;
    overflow-x: auto;
    font-size: 0.8rem;
  }

  .json-display code {
    color: #f3f3f3;
  }
</style>
