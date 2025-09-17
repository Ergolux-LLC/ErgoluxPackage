<script lang="ts">
  import { config } from "$lib/config/environment";
</script>

{#if config.ui.showEnvironmentBadge}
  <div class="environment-badge">
    <span
      class="badge {config.isDevelopment
        ? 'bg-warning text-dark'
        : 'bg-success'}"
    >
      <i class="bi {config.isDevelopment ? 'bi-code-slash' : 'bi-shield-check'}"
      ></i>
      {config.app.env.toUpperCase()}
      {#if config.isDevelopment}
        <small>v{config.app.version}</small>
      {/if}
    </span>
  </div>
{/if}

<style>
  .environment-badge {
    position: fixed;
    bottom: 1rem;
    left: 1rem;
    z-index: 9998;
  }

  .badge {
    backdrop-filter: blur(10px);
    font-size: 0.7rem;
    padding: 0.4rem 0.6rem;
    border-radius: 0.5rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
  }

  .badge:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
  }

  .bg-warning {
    background: linear-gradient(135deg, #ffc107, #ff8f00) !important;
  }

  .bg-success {
    background: linear-gradient(135deg, #28a745, #20c997) !important;
  }
</style>
