<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import { browser } from "$app/environment";
  import { login, redirectToWorkspace, type AuthError } from "$lib/api";
  import "./login.css";

  let email = "dev@example.com";
  let password = "devpassword123";
  let error: string | null = null;
  let loading = false;
  let setupComplete = false;
  let successMessage: string | null = null;

  onMount(() => {
    // Check if user just completed setup
    const setupParam = $page.url.searchParams.get("setup");
    if (setupParam === "complete") {
      setupComplete = true;
      successMessage =
        "Your account has been set up successfully. Please log in.";
      // Can set a timeout to clear the success message after a few seconds
      setTimeout(() => {
        successMessage = null;
      }, 6000);
    }
  });

  async function handleSubmit(event: Event) {
    event.preventDefault();
    error = null;
    loading = true;

    try {
      const result = await login({ email, password });

      if (result.success) {
        successMessage = "Login successful! Redirecting...";
        redirectToWorkspace();
      } else if (result.error) {
        error = result.error.message;
      }
    } catch (loginError) {
      console.error("Unexpected login error:", loginError);
      error = "An unexpected error occurred. Please try again.";
    }

    loading = false;
  }
</script>

<div
  class="min-vh-100 d-flex align-items-center justify-content-center position-relative"
>
  <!-- Luxurious background overlay -->
  <div class="luxury-bg position-absolute w-100 h-100"></div>

  <div class="container position-relative">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-5 col-xl-4">
        <!-- Main login card -->
        <div class="card luxury-card border-0 shadow-lg">
          <div
            class="card-header bg-transparent border-0 text-center pt-4 pb-2"
          >
            <div class="luxury-icon mb-3">
              <i class="bi bi-gem text-warning fs-1"></i>
            </div>
            <h1 class="card-title text-light mb-0 fw-light">
              <span class="text-warning">Ergolux</span> CRM
            </h1>
            <p class="text-muted small mb-0">Premium Business Management</p>
          </div>

          <div class="card-body px-4 pb-4">
            {#if successMessage}
              <div
                class="alert alert-success d-flex align-items-center fade show"
                role="alert"
              >
                <i class="bi bi-check-circle-fill me-2"></i>
                {successMessage}
              </div>
            {/if}

            <form on:submit|preventDefault={handleSubmit}>
              <!-- Email Input Group -->
              <div class="mb-3">
                <label for="email" class="form-label text-light fw-medium">
                  <i class="bi bi-envelope me-2"></i>Email Address
                </label>
                <div class="input-group">
                  <span class="input-group-text luxury-input-addon">
                    <i class="bi bi-person-circle"></i>
                  </span>
                  <input
                    id="email"
                    type="email"
                    class="form-control luxury-input {error?.includes('email')
                      ? 'is-invalid'
                      : ''}"
                    bind:value={email}
                    required
                    autocomplete="username"
                    placeholder="Enter your email address"
                  />
                </div>
              </div>

              <!-- Password Input Group -->
              <div class="mb-4">
                <label for="password" class="form-label text-light fw-medium">
                  <i class="bi bi-shield-lock me-2"></i>Password
                </label>
                <div class="input-group">
                  <span class="input-group-text luxury-input-addon">
                    <i class="bi bi-key"></i>
                  </span>
                  <input
                    id="password"
                    type="password"
                    class="form-control luxury-input {error?.includes(
                      'password',
                    )
                      ? 'is-invalid'
                      : ''}"
                    bind:value={password}
                    required
                    autocomplete="current-password"
                    placeholder="Enter your password"
                  />
                </div>
              </div>

              <!-- Login Button -->
              <div class="d-grid mb-3">
                <button
                  type="submit"
                  class="btn luxury-btn btn-lg fw-semibold"
                  disabled={loading}
                >
                  {#if loading}
                    <span
                      class="spinner-border spinner-border-sm me-2"
                      role="status"
                      aria-hidden="true"
                    ></span>
                    Signing you in...
                  {:else}
                    <i class="bi bi-box-arrow-in-right me-2"></i>
                    Sign In
                  {/if}
                </button>
              </div>

              {#if error}
                <div
                  class="alert alert-danger d-flex align-items-center fade show"
                  role="alert"
                >
                  <i class="bi bi-exclamation-triangle-fill me-2"></i>
                  {error}
                </div>
              {/if}
            </form>
          </div>

          <!-- Card Footer -->
          <div class="card-footer bg-transparent border-0 text-center pb-4">
            <div class="text-muted small">
              <i class="bi bi-person-plus me-1"></i>
              Don't have an account?
              <a
                href="/signup"
                class="text-warning text-decoration-none fw-medium"
              >
                Create Account
              </a>
            </div>
            <hr class="my-3 opacity-25" />
            <div class="text-muted" style="font-size: 0.75rem;">
              <i class="bi bi-shield-check me-1"></i>
              Secured with enterprise-grade encryption
            </div>
          </div>
        </div>

        <!-- Additional luxury elements -->
        <div class="text-center mt-4">
          <div class="luxury-footer-links">
            <a
              href="/bootstrap_check"
              class="text-muted text-decoration-none me-3 small"
            >
              <i class="bi bi-gear"></i> System Status
            </a>
            <a href="#" class="text-muted text-decoration-none me-3 small">
              <i class="bi bi-question-circle"></i> Help
            </a>
            <a href="#" class="text-muted text-decoration-none small">
              <i class="bi bi-shield-lock"></i> Privacy
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
