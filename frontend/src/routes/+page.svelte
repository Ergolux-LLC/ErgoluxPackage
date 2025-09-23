<script lang="ts">
  let email = "dev@example.com";
  let password = "devpassword123";
  let error: string | null = null;
  let loading = false;

  import { apiClient } from "$lib/api/client";

  async function handleSubmit(event: Event) {
    event.preventDefault();
    error = null;
    loading = true;
    console.log("[LOGIN] Attempt started", { email });

    let data;
    try {
      data = await apiClient.login(email, password);
      console.log("[LOGIN] API response:", data);
    } catch (fetchErr) {
      console.error("[LOGIN] Network or unexpected error:", fetchErr);
      error = `Network error during login: ${fetchErr instanceof Error ? fetchErr.message : fetchErr}`;
      loading = false;
      return;
    }
    loading = false;

    if (data && (data.success || data.access_token)) {
      console.log(
        "[LOGIN] Success, redirecting to /dashboard (no cookie wait)",
      );
      window.location.href = "/dashboard";
    } else if (data && data.error) {
      // Handle validation errors (422)
      if (
        data.debug &&
        data.debug.status === 422 &&
        data.detail &&
        Array.isArray(data.detail)
      ) {
        // Show the first missing field or a summary
        const missingFields = data.detail
          .filter((d: any) => d.msg && d.msg.toLowerCase().includes("required"))
          .map((d: any) => (d.loc && d.loc.length > 1 ? d.loc[1] : null))
          .filter(Boolean);
        if (missingFields.length > 0) {
          error = `Please enter your ${missingFields.join(" and ")}.`;
        } else {
          error =
            "Some required fields are missing. Please check your input and try again.";
        }
        console.warn("[LOGIN] Validation error:", data.detail);
      } else if (data.error === "Login failed") {
        error =
          "Incorrect email or password. Please check your credentials and try again.";
        console.warn("[LOGIN] Login failed: Incorrect credentials.");
      } else if (data.debug && data.debug.status) {
        error = `Login failed: Server error: ${data.debug.status} ${data.debug.statusText || ""}`;
        console.warn("[LOGIN] Login failed:", data.error, data.debug);
      } else {
        error = `Login failed: ${data.error}`;
        console.warn("[LOGIN] Login failed:", data.error);
      }
    } else {
      error =
        "Login failed due to an unknown error. Please try again or contact support.";
      console.warn("[LOGIN] Login failed: Unknown error.", data);
    }
  }
</script>

<main>
  <video
    autoplay
    loop
    muted
    playsinline
    class="background-video"
    poster="/images/backgrounds/falling_stars_red.mp4"
  >
    <source src="/images/backgrounds/falling_stars_red.mp4" type="video/mp4" />
    Your browser does not support the video tag.
  </video>

  <div
    class="min-vh-100 d-flex align-items-center justify-content-center position-relative"
  >
    <div class="container position-relative">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5 col-xl-4">
          <!-- Main login card -->
          <div class="card luxury-card border-0 shadow-lg">
            <div
              class="card-header bg-transparent border-0 text-center pt-4 pb-2"
            >
              <div class="luxury-icon mb-3">
                <i class="bi bi-gem text-danger fs-1"></i>
              </div>
              <h1 class="card-title text-white mb-0 fw-light">
                <span class="text-danger">Ergolux</span> CRM
              </h1>
              <p class="text-light small mb-0 opacity-75">
                Premium Business Management
              </p>
            </div>

            <div class="card-body px-4 pb-4">
              <form on:submit|preventDefault={handleSubmit}>
                <!-- Email Input Group -->
                <div class="mb-3">
                  <label for="email" class="form-label text-white fw-medium">
                    <i class="bi bi-envelope me-2 text-danger"></i>Email Address
                  </label>
                  <div class="input-group">
                    <span class="input-group-text luxury-input-addon">
                      <i class="bi bi-person-circle"></i>
                    </span>
                    <input
                      id="email"
                      type="email"
                      class="form-control luxury-input"
                      bind:value={email}
                      required
                      autocomplete="username"
                      placeholder="Enter your email address"
                    />
                  </div>
                </div>

                <!-- Password Input Group -->
                <div class="mb-4">
                  <label for="password" class="form-label text-white fw-medium">
                    <i class="bi bi-shield-lock me-2 text-danger"></i>Password
                  </label>
                  <div class="input-group">
                    <span class="input-group-text luxury-input-addon">
                      <i class="bi bi-key"></i>
                    </span>
                    <input
                      id="password"
                      type="password"
                      class="form-control luxury-input"
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
              <div class="text-light small opacity-75">
                <i class="bi bi-person-plus me-1 text-danger"></i>
                Don't have an account?
                <a
                  href="/signup"
                  class="text-danger text-decoration-none fw-medium"
                >
                  Create Account
                </a>
              </div>
              <hr class="my-3 opacity-25" />
              <div class="text-light opacity-50" style="font-size: 0.75rem;">
                <i class="bi bi-shield-check me-1 text-danger"></i>
                Secured with enterprise-grade encryption
              </div>
            </div>
          </div>

          <!-- Additional luxury elements -->
          <div class="text-center mt-4">
            <div class="luxury-footer-links">
              <a
                href="/bootstrap_check"
                class="text-light opacity-75 text-decoration-none me-3 small"
              >
                <i class="bi bi-gear text-danger"></i> System Status
              </a>
              <a
                href="#"
                class="text-light opacity-75 text-decoration-none me-3 small"
              >
                <i class="bi bi-question-circle text-danger"></i> Help
              </a>
              <a
                href="#"
                class="text-light opacity-75 text-decoration-none small"
              >
                <i class="bi bi-shield-lock text-danger"></i> Privacy
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Cat image section with luxury styling -->
    <div
      class="luxury-cat-section position-absolute bottom-0 end-0 m-4 d-none d-lg-block"
    >
      <div class="card luxury-mini-card border-0 shadow">
        <div class="card-body p-3 text-center">
          <div class="img-container mb-2">
            <img
              src="https://placecats.com/120/80"
              alt="Cute kitten"
              class="rounded"
            />
          </div>
          <p class="text-white small mb-0">
            <i class="bi bi-heart-fill text-danger"></i> Cat!
          </p>
        </div>
      </div>
    </div>
  </div>
</main>

<style>
  /* Preserve video background with luxury overlay */
  :global(body) {
    margin: 0;
    padding: 0;
    overflow: hidden;
    font-family: "Inter", "Segoe UI", system-ui, sans-serif;
  }

  main {
    min-height: 100vh;
    min-width: 100vw;
    position: relative;
    overflow: hidden;
  }

  .background-video {
    position: fixed;
    top: 0;
    left: 0;
    min-width: 100vw;
    min-height: 100vh;
    width: auto;
    height: auto;
    object-fit: cover;
    z-index: 0;
    opacity: 1;
    pointer-events: none;
  }

  /* Luxury card styling */
  .luxury-card {
    background: linear-gradient(
      145deg,
      rgba(25, 25, 45, 0.95) 0%,
      rgba(15, 15, 30, 0.98) 100%
    );
    backdrop-filter: blur(30px);
    border-radius: 20px !important;
    box-shadow:
      0 25px 50px rgba(0, 0, 0, 0.6),
      0 0 0 1px rgba(255, 255, 255, 0.08),
      inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
    position: relative;
    z-index: 2;
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
      rgba(220, 53, 69, 0.5),
      transparent
    );
  }

  .luxury-card:hover {
    transform: translateY(-2px);
    box-shadow:
      0 35px 70px rgba(0, 0, 0, 0.6),
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
      rgba(220, 53, 69, 0.2) 0%,
      transparent 70%
    );
    border-radius: 50%;
    animation: luxuryPulse 3s ease-in-out infinite;
  }

  /* Premium input styling */
  .luxury-input {
    background: rgba(15, 15, 30, 0.85) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #ffffff !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    transition: all 0.3s ease !important;
    font-size: 0.95rem !important;
  }

  .luxury-input:focus {
    background: rgba(20, 20, 40, 0.9) !important;
    border-color: rgba(220, 53, 69, 0.6) !important;
    box-shadow:
      0 0 0 3px rgba(220, 53, 69, 0.1),
      0 8px 25px rgba(220, 53, 69, 0.1) !important;
    color: #ffffff !important;
  }

  .luxury-input::placeholder {
    color: rgba(255, 255, 255, 0.4) !important;
  }

  .luxury-input-addon {
    background: rgba(20, 20, 40, 0.85) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px 0 0 12px !important;
    color: rgba(220, 53, 69, 0.8) !important;
  }

  /* Luxury button styling */
  .luxury-btn {
    background: linear-gradient(
      135deg,
      #dc3545 0%,
      #c82333 50%,
      #b21e2f 100%
    ) !important;
    border: none !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative;
    overflow: hidden;
    box-shadow:
      0 8px 25px rgba(220, 53, 69, 0.3),
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
      0 12px 35px rgba(220, 53, 69, 0.4),
      inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
    background: linear-gradient(
      135deg,
      #e74c3c 0%,
      #dc3545 50%,
      #c82333 100%
    ) !important;
  }

  .luxury-btn:active {
    transform: translateY(0);
  }

  .luxury-btn:disabled {
    background: linear-gradient(
      135deg,
      rgba(220, 53, 69, 0.5) 0%,
      rgba(200, 35, 51, 0.5) 100%
    ) !important;
    cursor: not-allowed;
    transform: none !important;
  }

  /* Form labels */
  .form-label {
    color: #ffffff !important;
    font-weight: 500 !important;
    margin-bottom: 8px !important;
  }

  /* Alert styling */
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
    color: rgba(220, 53, 69, 0.8) !important;
    transform: translateY(-1px);
  }

  /* Card title */
  .card-title {
    font-size: 1.75rem;
    font-weight: 300;
    letter-spacing: -0.5px;
  }

  /* Cat section styling */
  .luxury-cat-section {
    z-index: 3;
    margin-right: 1.5rem !important;
    margin-bottom: 1.5rem !important;
  }

  .luxury-mini-card {
    background: linear-gradient(
      145deg,
      rgba(25, 25, 45, 0.95) 0%,
      rgba(15, 15, 30, 0.98) 100%
    );
    backdrop-filter: blur(20px);
    border-radius: 12px !important;
    box-shadow:
      0 8px 25px rgba(0, 0, 0, 0.4),
      0 0 0 1px rgba(255, 255, 255, 0.08) !important;
    transition: all 0.3s ease;
  }

  .luxury-mini-card:hover {
    transform: translateY(-2px);
    box-shadow:
      0 12px 35px rgba(0, 0, 0, 0.4),
      0 0 0 1px rgba(255, 255, 255, 0.1) !important;
  }

  .img-container img {
    width: 100%;
    height: auto;
    transition: transform 0.3s ease;
  }

  .luxury-mini-card:hover .img-container img {
    transform: scale(1.05);
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

    .luxury-cat-section {
      display: none !important;
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
    background: rgba(220, 53, 69, 0.3);
    border-radius: 4px;
  }

  :global(::-webkit-scrollbar-thumb:hover) {
    background: rgba(220, 53, 69, 0.5);
  }
</style>
