<script lang="ts">
  import favicon from "$lib/assets/favicon.svg";
  import "$lib/assets/global.css";
  // Import Bootstrap CSS and Icons
  import "bootstrap/dist/css/bootstrap.min.css";
  import "bootstrap-icons/font/bootstrap-icons.css";
  // Import Bootstrap JS
  import { onMount } from "svelte";
  // Import environment tools
  import DevTools from "$lib/components/DevTools.svelte";
  import EnvironmentBadge from "$lib/components/EnvironmentBadge.svelte";
  import { config, devLog } from "$lib/config/environment";
  // Import memory manager for initialization
  import { memoryManager } from "$lib/memorymanager";

  let { children, data } = $props();

  onMount(async () => {
    // Initialize memory manager
    memoryManager.initialize();

    // Bootstrap should be available from CDN
    if (typeof window !== "undefined" && (window as any).bootstrap) {
      devLog("Bootstrap loaded successfully from CDN");
    }

    // Log environment info
    devLog("Application started", {
      environment: config.app.env,
      version: config.app.version,
      features: config.features,
    });
  });
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
  <title>{config.app.name} - {config.app.env}</title>
</svelte:head>

{@render children?.()}

<!-- Development Tools (only shown in dev mode) -->
<DevTools />
<EnvironmentBadge />
