<script lang="ts">
  import favicon from "$lib/assets/favicon.svg";
  import "$lib/assets/global.css";
  import "bootstrap/dist/css/bootstrap.min.css";
  import "bootstrap-icons/font/bootstrap-icons.css";
  import { onMount } from "svelte";
  import DevTools from "$lib/components/DevTools.svelte";
  import EnvironmentBadge from "$lib/components/EnvironmentBadge.svelte";
  import { config, devLog } from "$lib/config/environment";
  import { memoryManager } from "$lib/memorymanager";

  import { page } from "$app/stores";

  let { children, data } = $props();

  onMount(async () => {
    try {
      const maybePromise: any = memoryManager.initialize();
      if (maybePromise && typeof maybePromise.then === "function") {
        await maybePromise;
      }
    } catch (e) {
      // initialization error should not block showing UI; continue
    }

    // reveal body now that initialization is done to avoid FOUC
    try {
      document.body.style.visibility = "visible";
    } catch (e) {}

    if (typeof window !== "undefined" && (window as any).bootstrap) {
      devLog("Bootstrap loaded successfully from CDN");
    }

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

<div class="app-wrapper">
  {@render children?.()}

  {#if !$page.url.pathname.includes("/learning")}
    <DevTools />
    <EnvironmentBadge />
  {/if}
</div>
