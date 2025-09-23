<script lang="ts">
  import type { LayoutData } from "./$types";
  import { ContextSwitcher } from "$lib/components/context_switcher";
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";

  export let data: LayoutData;

  // Type-safe access to our custom properties
  const layoutData = data as any; // Cast to any to access our custom properties

  // Context switcher logic
  $: currentSubApp = determineActiveSubApp($page.url.pathname);

  // Sparkler effect disabled by default - can be enabled via enableSparkler prop
  let hasNewAccess = false; // Set to true to show sparkler effect (when enabled)

  function determineActiveSubApp(pathname: string): string {
    // Extract sub-app from URL path
    // Examples: /dashboard -> 'discover', /dashboard/qualify -> 'qualify'
    const pathSegments = pathname.split("/").filter(Boolean);

    if (pathSegments.length > 1) {
      // Check if the second segment matches a known sub-app
      const subApp = pathSegments[1];
      const validSubApps = [
        "discover",
        "qualify",
        "nurture",
        "commit",
        "onboard",
        "support",
        "expand",
        "renew",
        "advocate",
      ];
      return validSubApps.includes(subApp) ? subApp : "discover";
    }

    // Default to 'nurture' to demonstrate sparkler effect
    return "nurture";
  }

  function handleSubAppChange(event: CustomEvent) {
    const subApp = event.detail;

    // If user accessed the new mode, stop the sparkler
    if (hasNewAccess) {
      hasNewAccess = false;
    }

    // Navigate to the sub-app route
    // For now, we'll append the sub-app to the dashboard path
    goto(`/dashboard/${subApp.id}`);
  }

  function goToLogin() {
    if (layoutData.redirectUrl) {
      window.location.href = layoutData.redirectUrl;
    } else {
      window.location.href = "/login";
    }
  }
</script>

<svelte:head>
  <title>Dashboard - Ergolux Portal</title>
</svelte:head>

{#if layoutData.accessDenied}
  <!-- ACCESS DENIED SCREEN (same pattern as workspace) -->
  <div class="blackout-screen">
    <div class="access-denied-container">
      <div class="access-denied-content">
        <div class="text-center">
          <i class="bi bi-shield-x display-1 text-danger mb-4"></i>
          <h1 class="text-white mb-3">Access Denied</h1>
          <p class="text-light mb-4">
            {layoutData.message ||
              "Authentication required to access this resource."}
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
  <!-- PROTECTED CONTENT - Context Switcher and child pages -->
  <ContextSwitcher
    activeSubApp={currentSubApp}
    {hasNewAccess}
    sparkleIntensity="medium"
    enableSparkler={false}
    on:subAppChange={handleSubAppChange}
  />
  <slot />
{/if}

<style>
  /* Blackout screen styling (same as workspace) */
  .blackout-screen {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 50%, #16213e 100%);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
  }

  /* Ensure content doesn't hide behind sticky context switcher */
  :global(main) {
    position: relative;
    z-index: 1;
  }

  .access-denied-container {
    width: 100%;
    max-width: 500px;
    padding: 2rem;
  }

  .access-denied-content {
    background: linear-gradient(
      145deg,
      rgba(30, 30, 50, 0.95) 0%,
      rgba(20, 20, 35, 0.98) 100%
    );
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 3rem 2rem;
    box-shadow:
      0 25px 50px rgba(0, 0, 0, 0.4),
      0 0 0 1px rgba(255, 255, 255, 0.05),
      inset 0 1px 0 rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  /* Button styling to match the luxury theme */
  :global(.blackout-screen .btn-primary) {
    background: linear-gradient(
      135deg,
      #ffc107 0%,
      #ff8f00 50%,
      #f57c00 100%
    ) !important;
    border: none !important;
    color: #000000 !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    transition: all 0.3s ease !important;
  }

  :global(.blackout-screen .btn-primary:hover) {
    background: linear-gradient(
      135deg,
      #ffcd38 0%,
      #ffa000 50%,
      #f57c00 100%
    ) !important;
    transform: translateY(-1px);
    box-shadow: 0 12px 35px rgba(255, 193, 7, 0.4) !important;
  }

  :global(.blackout-screen .btn-outline-light) {
    border: 2px solid rgba(255, 255, 255, 0.3) !important;
    color: rgba(255, 255, 255, 0.9) !important;
    border-radius: 12px !important;
    padding: 10px 24px !important;
    transition: all 0.3s ease !important;
  }

  :global(.blackout-screen .btn-outline-light:hover) {
    background: rgba(255, 255, 255, 0.1) !important;
    border-color: rgba(255, 255, 255, 0.5) !important;
    color: #ffffff !important;
    transform: translateY(-1px);
  }

  /* Responsive adjustments */
  @media (max-width: 576px) {
    .access-denied-container {
      padding: 1rem;
    }

    .access-denied-content {
      padding: 2rem 1.5rem;
      border-radius: 16px;
    }
  }
</style>
