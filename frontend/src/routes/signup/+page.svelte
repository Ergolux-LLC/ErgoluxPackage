<script lang="ts">
  import { page } from "$app/stores";
  import { onMount } from "svelte";
  import { beforeNavigate } from "$app/navigation";
  import { config, isDevMode, shouldLog } from "$lib/config/environment";
  import { apiClient } from "$lib/api/client";
  // Log all environment and config values at module load
  console.log("[SIGNUP PAGE] config:", config);
  console.log("[SIGNUP PAGE] config.api.baseUrl:", config.api.baseUrl);
  console.log(
    "[SIGNUP PAGE] window.location:",
    typeof window !== "undefined" ? window.location.href : "server"
  );
  if (typeof import.meta !== "undefined") {
    console.log("[SIGNUP PAGE] import.meta.env:", import.meta.env);
  }

  // Helper function to log client-side events
  function logClient(event: string, data: any) {
    if (!shouldLog()) return;
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [CLIENT] [${event}]`, data);
  }

  // Define the form data type based on the API spec
  type FormData = {
    success?: boolean;
    email_confirmation_status?: string;
    code?: string | null;
    reason?: string | null;
    error?: string | Record<string, string>;
    debug?: {
      status: number;
      statusText: string;
      contentType?: string;
      rawResponse?: string;
    };
  };

  export let form: FormData | null = null;

  // Log when form data changes
  $: if (form) {
    logClient("FormData", {
      success: form.success,
      hasError: !!form.error,
      hasCode: !!form.code,
      errorType: form.error ? typeof form.error : null,
    });
    console.log("[SIGNUP PAGE] FormData:", form);
  }

  let email = "";
  // No workspaceId for this flow
  let isDev = isDevMode();
  console.log("[SIGNUP PAGE] Initial email:", email);
  console.log("[SIGNUP PAGE] isDev:", isDev);

  // Track form submission
  let isSubmitting = false;

  // Dev mode code retrieval
  let isGettingCode = false;
  let devCode = "";
  let codeRetryCount = 0;
  const maxRetries = 10;

  // Log navigation events
  beforeNavigate((navigation) => {
    logClient("Navigation", {
      from: navigation.from?.url.pathname,
      to: navigation.to?.url.pathname,
      type: navigation.type,
    });
  });

  // Check if we're in development mode
  onMount(() => {
    // Log page initialization
    logClient("PageInit", {
      url: window.location.href,
      params: Object.fromEntries(
        new URLSearchParams(window.location.search).entries()
      ),
      isDev,
      config: config.app,
    });
    console.log(
      "[SIGNUP PAGE] onMount: url",
      window.location.href,
      "isDev",
      isDev,
      "config",
      config
    );

    // For easy testing in development mode
    if (isDev) {
      email = `dev+${Date.now()}@starwars.com`; // Use unique email to avoid "already signed up" error
      logClient("DevMode", { email, environment: config.app.env });
      console.log("[SIGNUP PAGE] DevMode: email", email, "env", config.app.env);
    }
  });

  // Handle form submission using API client
  async function handleSubmit(event: SubmitEvent) {
    event.preventDefault();
    logClient("FormSubmit", {
      email,
      isDev,
    });
    console.log("[SIGNUP PAGE] handleSubmit called");
    console.log(
      "[SIGNUP PAGE] handleSubmit: email",
      email,
      "isDev",
      isDev,
      "config",
      config
    );
    isSubmitting = true;
    console.log("[SIGNUP PAGE] isSubmitting set to true");

    try {
      const signupArgs = { email };
      console.log("[SIGNUP PAGE] Calling apiClient.signup with:", signupArgs);
      const result = await apiClient.signup(email);
      console.log("[SIGNUP PAGE] apiClient.signup result:", result);

      if (result.success === false) {
        // API call was successful but signup failed (business logic error)
        logClient("APIBusinessError", result);
        form = {
          error: result.reason || result.error || "Signup failed",
          debug: result.debug,
        };
        console.log("[SIGNUP PAGE] Business error:", form);
      } else {
        // Signup was successful
        logClient("APIResponse", result);
        form = result;
        console.log("[SIGNUP PAGE] Signup success:", form);

        // In dev mode, automatically get the confirmation code
        if (isDev && result.success) {
          await getDevCode(email);
        }
      }
    } catch (error) {
      logClient("APIError", error);
      form = { error: "Network or server error. Please try again." };
      console.error("[SIGNUP PAGE] API error:", error);
    } finally {
      isSubmitting = false;
      console.log("[SIGNUP PAGE] isSubmitting set to false");
    }
  }

  // Get dev code with retry logic
  async function getDevCode(userEmail: string) {
    if (!isDev) return;

    isGettingCode = true;
    codeRetryCount = 0;
    devCode = "";

    console.log("[SIGNUP PAGE] Getting dev code for:", userEmail);

    const encodedEmail = encodeURIComponent(userEmail);
    const codeUrl = `http://localhost:8050/account-setup/dev/get-code/${encodedEmail}`;

    const tryGetCode = async (): Promise<boolean> => {
      try {
        codeRetryCount++;
        console.log(
          `[SIGNUP PAGE] Code attempt ${codeRetryCount}/${maxRetries}`
        );

        const response = await fetch(codeUrl, {
          headers: {
            Accept: "application/json",
          },
        });

        if (response.ok) {
          const data = await response.json();
          console.log("[SIGNUP PAGE] Code response:", data);

          if (data.code) {
            devCode = data.code;
            console.log("[SIGNUP PAGE] Got dev code:", devCode);
            return true;
          }
        } else {
          console.log(
            `[SIGNUP PAGE] Code request failed: ${response.status} ${response.statusText}`
          );
        }
      } catch (error) {
        console.error("[SIGNUP PAGE] Error getting code:", error);
      }
      return false;
    };

    // Retry logic
    while (codeRetryCount < maxRetries && !devCode) {
      const success = await tryGetCode();
      if (success) break;

      // Wait 1 second before retry
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }

    isGettingCode = false;

    if (!devCode) {
      console.error(
        "[SIGNUP PAGE] Failed to get dev code after",
        maxRetries,
        "attempts"
      );
    }
  }
</script>

{#if form?.success && isDev}
  <div class="signup-form dev-success">
    <h1>Dev Signup Successful</h1>
    <p>Signup for <b>{email}</b> was successful (dev mode).</p>

    {#if isGettingCode}
      <div class="getting-code">
        <p>
          Getting confirmation code... (attempt {codeRetryCount}/{maxRetries})
        </p>
      </div>
    {:else if devCode}
      <div class="code-display">
        <p><strong>Confirmation Code:</strong> <code>{devCode}</code></p>
        <a class="activation-link" href={`/setup?code=${devCode}`}>
          Continue to Setup →
        </a>
      </div>
    {:else if form.code}
      <a class="activation-link" href={`/setup?code=${form.code}`}>
        Go to activation link (Code: {form.code})
      </a>
    {:else}
      <p class="warning-message">
        Failed to get confirmation code automatically. Check your email or
        contact support.
      </p>
    {/if}

    {#if form.reason}
      <p class="info-message">Note: {form.reason}</p>
    {/if}
  </div>
{:else if form?.success}
  <div class="signup-form success">
    <h1>Check your email</h1>
    <p>
      We've sent a signup link to <b>{email}</b>. Please check your inbox to
      continue.
    </p>
    {#if isDev && form.code}
      <a class="activation-link" href={`/setup?code=${form.code}`}>
        Go to activation link (Dev Code: {form.code})
      </a>
    {/if}
    {#if form.reason}
      <p class="info-message">Note: {form.reason}</p>
    {/if}
  </div>
{:else}
  <form class="signup-form" on:submit={handleSubmit} autocomplete="off">
    <h1>Sign Up</h1>
    <label>
      Email
      <input
        type="email"
        name="email"
        bind:value={email}
        required
        autocomplete="username"
        on:change={() => logClient("EmailChange", { email })}
      />
    </label>

    <button type="submit" disabled={isSubmitting}>
      {isSubmitting ? "Processing..." : "Sign Up"}
    </button>
    {#if form?.error}
      <div class="error">
        <!-- Display the main error message -->
        <div class="error-main">
          {#if typeof form.error === "object"}
            {#each Object.entries(form.error) as [key, value]}
              <div>{key}: {value}</div>
            {/each}
          {:else}
            {form.error}
          {/if}
        </div>

        <!-- Show debug info if available -->
        {#if form.debug}
          <details class="debug-info">
            <summary>Show technical details</summary>
            <div class="debug-content">
              <div>
                <strong>Status:</strong>
                {form.debug.status}
                {form.debug.statusText}
              </div>
              <div>
                <strong>Content-Type:</strong>
                {form.debug.contentType || "unknown"}
              </div>
              {#if form.debug.rawResponse}
                <div>
                  <strong>Raw Response:</strong>
                  <pre>{form.debug.rawResponse}</pre>
                </div>
              {/if}
              // Debug panel state let showDebug = false; console.log('[API CONFIG]
              PUBLIC_API_BASE_URL:', PUBLIC_API_BASE_URL); console.log('[API CONFIG]
              API_BASE_URL:', API_BASE_URL);
            </div>
          </details>
        {/if}
      </div>
    {/if}
  </form>
{/if}

<style>
  :global(body) {
    background: #181a1b;
    color: #f3f3f3;
    font-family: system-ui, sans-serif;
    margin: 0;
    padding: 0;
  }
  .signup-form {
    max-width: 320px;
    margin: 4em auto;
    padding: 2em;
    background: #23272b;
    border-radius: 10px;
    box-shadow: 0 4px 24px #0008;
    display: flex;
    flex-direction: column;
    gap: 1em;
    color: #f3f3f3;
  }
  .signup-form.success,
  .signup-form.dev-success {
    align-items: center;
    text-align: center;
    gap: 1.5em;
  }
  .signup-form.dev-success {
    border: 2px solid #4caf50;
    color: #4caf50;
    background: #232b23;
  }
  .activation-link {
    margin-top: 1em;
    color: #ffe082;
    background: #23272b;
    padding: 0.5em 1em;
    border-radius: 6px;
    text-decoration: none;
    font-weight: bold;
    display: inline-block;
    transition:
      background 0.2s,
      color 0.2s;
  }
  .activation-link:hover {
    background: #4f8cff;
    color: #fff;
  }
  .code-display {
    text-align: center;
    margin: 1em 0;
  }
  .code-display code {
    background: #333;
    padding: 0.5em 1em;
    border-radius: 4px;
    font-family: monospace;
    font-size: 1.1em;
    color: #4caf50;
    display: inline-block;
    margin: 0.5em 0;
  }
  .info-message {
    font-size: 0.9em;
    color: #b3e5fc;
    margin-top: 0.5em;
    padding: 0.5em;
    background: rgba(179, 229, 252, 0.1);
    border-radius: 5px;
    text-align: center;
  }
  .warning-message {
    font-size: 0.9em;
    color: #ffb74d;
    margin-top: 0.5em;
    padding: 0.5em;
    background: rgba(255, 183, 77, 0.1);
    border-radius: 5px;
    text-align: center;
  }
  .getting-code {
    color: #81c784;
    font-style: italic;
    margin: 0.5em 0;
  }
  .getting-code p {
    margin: 0;
    animation: pulse 1.5s ease-in-out infinite;
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
  label {
    display: flex;
    flex-direction: column;
    gap: 0.3em;
    font-size: 1em;
    margin-bottom: 0.8em;
  }
  input[type="email"] {
    padding: 0.6em;
    border-radius: 5px;
    border: 1px solid #444;
    background: #181a1b;
    color: #f3f3f3;
    font-size: 1em;
  }
  button {
    padding: 0.7em;
    border: none;
    border-radius: 5px;
    background: #4f8cff;
    color: #fff;
    font-size: 1em;
    cursor: pointer;
    margin-top: 1em;
    transition: background 0.2s;
  }
  button:disabled {
    background: #888;
    cursor: not-allowed;
  }
  .error {
    color: #ff6b6b;
    margin-top: 0.5em;
    font-size: 0.95em;
    text-align: center;
    background: rgba(255, 107, 107, 0.1);
    padding: 0.7em;
    border-radius: 5px;
    word-break: break-word;
  }

  .error-main {
    margin-bottom: 0.7em;
  }

  .debug-info {
    margin-top: 0.8em;
    padding: 0.5em;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 4px;
    font-size: 0.85em;
    text-align: left;
  }

  .debug-info summary {
    cursor: pointer;
    user-select: none;
    color: #b8b8b8;
  }

  .debug-content {
    margin-top: 0.5em;
    padding: 0.5em;
    display: flex;
    flex-direction: column;
    gap: 0.5em;
  }

  .debug-content pre {
    max-height: 200px;
    overflow: auto;
    background: rgba(0, 0, 0, 0.3);
    padding: 0.5em;
    border-radius: 3px;
    margin: 0.5em 0;
    text-align: left;
    white-space: pre-wrap;
  }
</style>
