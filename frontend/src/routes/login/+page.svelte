<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import { apiClient } from "$lib/api/client";

  let email = "";
  let password = "";
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
    console.log("Login attempt started with email:", email);

    try {
      const result = await apiClient.login(email, password);
      console.log("Login result:", result);

      if (result.success || result.access_token) {
        console.log("Login successful!");
        successMessage = "Login successful! Redirecting...";

        // Check for access token (new format)
        if (result.access_token) {
          console.log("New authentication format detected");

          // Short delay before redirect for better user experience
          setTimeout(() => {
            if (result.workspace) {
              window.location.href = `${window.location.protocol}//${result.workspace}.app.ergolux.io.localhost:5173/directory`;
            } else {
              goto("/directory");
            }
          }, 1000);
        } else {
          // Fallback for old format
          setTimeout(() => {
            if (result.workspace) {
              window.location.href = `${window.location.protocol}//${result.workspace}.app.ergolux.io.localhost:5173/directory`;
            } else {
              goto("/directory");
            }
          }, 1000);
        }
      } else {
        // Handle login failure
        if (result.error) {
          if (
            result.error === "Login failed" ||
            result.error.includes("credentials")
          ) {
            error = "Incorrect email or password.";
          } else if (
            result.error.includes("not active") ||
            result.error.includes("activation")
          ) {
            error =
              "This account has not been activated. Please check your email for an activation link.";
          } else {
            error = result.error;
          }
        } else {
          error = "Login failed. Please check your credentials and try again.";
        }
        console.warn("Login failed:", result.error || "Unknown error");
      }
    } catch (err) {
      console.error("Login error:", err);
      error = "Network error. Please try again.";
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
                      'password'
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

<style>
  /* Luxury background with gradient and subtle patterns */
  :global(body) {
    background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 50%, #16213e 100%);
    min-height: 100vh;
    margin: 0;
    font-family: "Inter", "Segoe UI", system-ui, sans-serif;
  }

  .luxury-bg {
    background: radial-gradient(
        circle at 20% 80%,
        rgba(120, 119, 198, 0.1) 0%,
        transparent 50%
      ),
      radial-gradient(
        circle at 80% 20%,
        rgba(255, 193, 7, 0.05) 0%,
        transparent 50%
      ),
      radial-gradient(
        circle at 40% 40%,
        rgba(79, 140, 255, 0.05) 0%,
        transparent 50%
      );
    backdrop-filter: blur(40px);
  }

  /* Luxury card styling */
  .luxury-card {
    background: linear-gradient(
      145deg,
      rgba(30, 30, 50, 0.95) 0%,
      rgba(20, 20, 35, 0.98) 100%
    );
    backdrop-filter: blur(20px);
    border-radius: 20px !important;
    box-shadow:
      0 25px 50px rgba(0, 0, 0, 0.4),
      0 0 0 1px rgba(255, 255, 255, 0.05),
      inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
    position: relative;
  }

  .luxury-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 193, 7, 0.5),
      transparent
    );
  }

  .luxury-card:hover {
    transform: translateY(-2px);
    box-shadow:
      0 35px 70px rgba(0, 0, 0, 0.5),
      0 0 0 1px rgba(255, 255, 255, 0.08),
      inset 0 1px 0 rgba(255, 255, 255, 0.15);
  }

  /* Luxury icon styling */
  .luxury-icon {
    position: relative;
    display: inline-block;
  }

  .luxury-icon::before {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 60px;
    height: 60px;
    background: radial-gradient(
      circle,
      rgba(255, 193, 7, 0.2) 0%,
      transparent 70%
    );
    border-radius: 50%;
    animation: luxuryPulse 3s ease-in-out infinite;
  }

  /* Premium input styling */
  .luxury-input {
    background: rgba(15, 15, 30, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #ffffff !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    transition: all 0.3s ease !important;
    font-size: 0.95rem !important;
  }

  .luxury-input:focus {
    background: rgba(20, 20, 40, 0.9) !important;
    border-color: rgba(255, 193, 7, 0.6) !important;
    box-shadow:
      0 0 0 3px rgba(255, 193, 7, 0.1),
      0 8px 25px rgba(255, 193, 7, 0.1) !important;
    color: #ffffff !important;
  }

  .luxury-input::placeholder {
    color: rgba(255, 255, 255, 0.4) !important;
  }

  .luxury-input-addon {
    background: rgba(20, 20, 40, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px 0 0 12px !important;
    color: rgba(255, 193, 7, 0.8) !important;
  }

  /* Luxury button styling */
  .luxury-btn {
    background: linear-gradient(
      135deg,
      #ffc107 0%,
      #ff8f00 50%,
      #f57c00 100%
    ) !important;
    border: none !important;
    border-radius: 12px !important;
    color: #000000 !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative;
    overflow: hidden;
    box-shadow:
      0 8px 25px rgba(255, 193, 7, 0.3),
      inset 0 1px 0 rgba(255, 255, 255, 0.2);
  }

  .luxury-btn::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.2),
      transparent
    );
    transition: left 0.5s ease;
  }

  .luxury-btn:hover::before {
    left: 100%;
  }

  .luxury-btn:hover {
    transform: translateY(-1px);
    box-shadow:
      0 12px 35px rgba(255, 193, 7, 0.4),
      inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
    background: linear-gradient(
      135deg,
      #ffcd38 0%,
      #ffa000 50%,
      #f57c00 100%
    ) !important;
  }

  .luxury-btn:active {
    transform: translateY(0);
  }

  .luxury-btn:disabled {
    background: linear-gradient(
      135deg,
      rgba(255, 193, 7, 0.5) 0%,
      rgba(255, 143, 0, 0.5) 100%
    ) !important;
    cursor: not-allowed;
    transform: none !important;
  }

  /* Form labels */
  .form-label {
    color: rgba(255, 255, 255, 0.9) !important;
    font-weight: 500 !important;
    margin-bottom: 8px !important;
  }

  /* Alert styling */
  .alert-success {
    background: linear-gradient(
      135deg,
      rgba(40, 167, 69, 0.1) 0%,
      rgba(40, 167, 69, 0.05) 100%
    ) !important;
    border: 1px solid rgba(40, 167, 69, 0.2) !important;
    color: #66bb6a !important;
    border-radius: 12px !important;
  }

  .alert-danger {
    background: linear-gradient(
      135deg,
      rgba(220, 53, 69, 0.1) 0%,
      rgba(220, 53, 69, 0.05) 100%
    ) !important;
    border: 1px solid rgba(220, 53, 69, 0.2) !important;
    color: #ef5350 !important;
    border-radius: 12px !important;
  }

  /* Footer links */
  .luxury-footer-links a {
    transition: all 0.3s ease;
    font-size: 0.85rem;
  }

  .luxury-footer-links a:hover {
    color: rgba(255, 193, 7, 0.8) !important;
    transform: translateY(-1px);
  }

  /* Card title */
  .card-title {
    font-size: 1.75rem;
    font-weight: 300;
    letter-spacing: -0.5px;
  }

  /* Animations */
  @keyframes luxuryPulse {
    0%,
    100% {
      transform: translate(-50%, -50%) scale(1);
      opacity: 0.3;
    }
    50% {
      transform: translate(-50%, -50%) scale(1.2);
      opacity: 0.1;
    }
  }

  /* Responsive adjustments */
  @media (max-width: 576px) {
    .luxury-card {
      margin: 1rem;
      border-radius: 16px !important;
    }

    .card-title {
      font-size: 1.5rem;
    }
  }

  /* Custom scrollbar for luxury feel */
  :global(::-webkit-scrollbar) {
    width: 8px;
  }

  :global(::-webkit-scrollbar-track) {
    background: rgba(20, 20, 35, 0.3);
  }

  :global(::-webkit-scrollbar-thumb) {
    background: rgba(255, 193, 7, 0.3);
    border-radius: 4px;
  }

  :global(::-webkit-scrollbar-thumb:hover) {
    background: rgba(255, 193, 7, 0.5);
  }
</style>
