<script lang="ts">
  import { config, devLog } from "$lib/config/environment";
  import { onMount } from "svelte";

  let showPanel = false;
  let envInfo = {
    environment: config.app.env,
    version: config.app.version,
    isDev: config.isDevelopment,
    debugMode: config.features.debugMode,
    apiUrl: config.api.baseUrl,
    timestamp: new Date().toLocaleString(),
  };

  onMount(() => {
    devLog("Development tools loaded", envInfo);
  });

  function togglePanel() {
    showPanel = !showPanel;
    devLog("Dev panel toggled", { visible: showPanel });
  }

  function clearStorage() {
    localStorage.clear();
    sessionStorage.clear();
    devLog("Storage cleared");
    alert("Local storage cleared!");
  }

  function reloadPage() {
    devLog("Page reload triggered");
    window.location.reload();
  }
</script>

{#if config.ui.enableDevMenu}
  <!-- Development Tools Floating Button -->
  <div class="dev-tools-container">
    <button
      class="dev-toggle-btn btn btn-sm btn-outline-warning"
      on:click={togglePanel}
      title="Development Tools"
    >
      <i class="bi bi-gear-fill"></i>
      DEV
    </button>

    {#if showPanel}
      <!-- Development Panel -->
      <div class="dev-panel card border-warning">
        <div
          class="card-header bg-warning text-dark d-flex justify-content-between align-items-center"
        >
          <strong>🛠️ Development Tools</strong>
          <button class="btn btn-sm btn-outline-dark" on:click={togglePanel}>
            <i class="bi bi-x"></i>
          </button>
        </div>

        <div class="card-body">
          <!-- Environment Info -->
          <div class="mb-3">
            <h6 class="text-warning">Environment Info</h6>
            <div class="small text-light">
              <div><strong>Environment:</strong> {envInfo.environment}</div>
              <div><strong>Version:</strong> {envInfo.version}</div>
              <div><strong>API URL:</strong> {envInfo.apiUrl}</div>
              <div>
                <strong>Debug Mode:</strong>
                {envInfo.debugMode ? "ON" : "OFF"}
              </div>
              <div><strong>Loaded:</strong> {envInfo.timestamp}</div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="mb-3">
            <h6 class="text-warning">Quick Actions</h6>
            <div class="d-grid gap-2">
              <button class="btn btn-sm btn-outline-info" on:click={reloadPage}>
                <i class="bi bi-arrow-clockwise"></i> Reload Page
              </button>
              <button
                class="btn btn-sm btn-outline-danger"
                on:click={clearStorage}
              >
                <i class="bi bi-trash"></i> Clear Storage
              </button>
            </div>
          </div>

          <!-- Quick Links -->
          <div class="mb-3">
            <h6 class="text-warning">Quick Links</h6>
            <div class="d-grid gap-1">
              <a href="/bootstrap_check" class="btn btn-sm btn-outline-success">
                <i class="bi bi-check-circle"></i> Bootstrap Check
              </a>
              <a href="/login" class="btn btn-sm btn-outline-primary">
                <i class="bi bi-box-arrow-in-right"></i> Login Page
              </a>
              <a href="/setup" class="btn btn-sm btn-outline-secondary">
                <i class="bi bi-gear"></i> Setup Page
              </a>
            </div>
          </div>

          <!-- Status -->
          <div class="text-center">
            <span class="badge bg-success">
              <i class="bi bi-check-circle-fill"></i>
              Development Mode Active
            </span>
          </div>
        </div>
      </div>
    {/if}
  </div>
{/if}

<style>
  .dev-tools-container {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 9999;
  }

  .dev-toggle-btn {
    backdrop-filter: blur(10px);
    background: rgba(255, 193, 7, 0.1) !important;
    border-color: rgba(255, 193, 7, 0.5) !important;
    color: #ffc107 !important;
    font-size: 0.75rem;
    font-weight: bold;
    padding: 0.25rem 0.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 4px 15px rgba(255, 193, 7, 0.2);
    transition: all 0.3s ease;
  }

  .dev-toggle-btn:hover {
    background: rgba(255, 193, 7, 0.2) !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(255, 193, 7, 0.3);
  }

  .dev-panel {
    position: absolute;
    top: 3rem;
    right: 0;
    width: 300px;
    max-height: 80vh;
    overflow-y: auto;
    background: rgba(20, 20, 35, 0.95) !important;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 193, 7, 0.3) !important;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    animation: slideIn 0.3s ease;
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .dev-panel .card-header {
    background: rgba(255, 193, 7, 0.9) !important;
    border-bottom: 1px solid rgba(255, 193, 7, 0.3);
  }

  .dev-panel .card-body {
    background: rgba(20, 20, 35, 0.98);
    color: #ffffff;
  }

  .dev-panel h6 {
    color: #ffc107 !important;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .dev-panel .text-light {
    opacity: 0.9;
  }

  /* Responsive adjustments */
  @media (max-width: 576px) {
    .dev-panel {
      width: calc(100vw - 2rem);
      right: -1rem;
    }
  }
</style>
