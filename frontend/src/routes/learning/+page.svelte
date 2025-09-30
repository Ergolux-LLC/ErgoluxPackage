<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { browser } from "$app/environment";

  // state
  let showPortal = false;
  // explicitly type the anchor ref so TS doesn't infer `any`
  let anchor: HTMLElement | null = null;
  let portalStyle = "";

  // action that moves the element into document.body (a simple "portal")
  function portal(node: HTMLElement) {
    if (typeof document === "undefined") return;
    const mount = document.createElement("div");
    mount.className = "svelte-portal-root";
    document.body.appendChild(mount);
    mount.appendChild(node);

    return {
      destroy() {
        // restore cleanup
        if (mount.parentNode) mount.parentNode.removeChild(mount);
      },
    };
  }

  function togglePortal() {
    showPortal = !showPortal;
    if (showPortal) updatePortalPosition();
  }

  function updatePortalPosition() {
    if (!browser || !anchor) return;
    const rect = anchor.getBoundingClientRect();
    // place portal to the right of anchor, fixed relative to viewport
    // small offset so it visually sits outside the left panel
    portalStyle = `position: fixed; left: ${rect.right + 8}px; top: ${rect.top}px; z-index: 9999;`;
  }

  // update portal position on scroll/resize while open
  function onWindowChange() {
    if (showPortal) updatePortalPosition();
  }

  onMount(() => {
    if (browser) {
      window.addEventListener("resize", onWindowChange);
      // capture scroll on document (including nested scrollables)
      window.addEventListener("scroll", onWindowChange, true);
    }
  });

  onDestroy(() => {
    if (browser) {
      window.removeEventListener("resize", onWindowChange);
      window.removeEventListener("scroll", onWindowChange, true);
    }
  });
</script>

<div class="page-wrapper">
  <div class="left-panel">
    <div class="panel-label">Left panel</div>

    <!-- visible anchor inside the left panel to compute portal coords -->
    <div bind:this={anchor} class="anchor">anchor</div>

    <!-- portal overlay: this div is moved to document.body by the `portal` action -->
    {#if showPortal}
      <div use:portal class="portal-overlay" style={portalStyle}>
        Portal overlay (to body)
      </div>
    {/if}

    <div class="controls">
      <button on:click={togglePortal}>
        {showPortal ? "Hide" : "Show"} portal overlay
      </button>
    </div>
  </div>

  <div class="right-panel">
    <div class="panel-label">Right panel</div>

    <!-- this element sits later in the DOM and will normally paint above un-z-indexed earlier elements -->
    <div class="inside-right-panel">inside rightbox</div>
  </div>
</div>

<style>
  :global(html, body) {
    height: 100%;
    margin: 0;
    font-family:
      system-ui,
      -apple-system,
      "Segoe UI",
      Roboto,
      "Helvetica Neue",
      Arial;
  }

  .page-wrapper {
    display: flex;
    height: 100vh;
    width: 100vw;
    position: relative;
    z-index: 0;
  }

  .left-panel,
  .right-panel {
    width: 50%;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 12px;
  }

  .left-panel {
    background: #000;
    color: #fff;
    position: relative;
  }

  .right-panel {
    background: #333;
    color: #fff;
    position: relative;
  }

  .panel-label {
    font-weight: 600;
    margin-bottom: 8px;
  }

  .controls button {
    margin: 4px;
    padding: 8px 12px;
  }

  .anchor {
    width: 120px;
    height: 28px;
    background: rgba(255, 255, 255, 0.06);
    color: #ddd;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
  }

  /* Portal overlay: will be moved to document.body by the portal action,
     style (position/top/left/z-index) is set inline from portalStyle */
  .portal-overlay {
    width: 800px;
    height: 60px;
    background: orange;
    color: black;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    border-radius: 6px;
  }

  .inside-right-panel {
    position: relative;
    background: #777;
    width: 240px;
    height: 120px;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 0;
    border-radius: 6px;
  }

  /* portal mount root (appended to body) can be used for global styling if needed */
  :global(.svelte-portal-root) {
    position: relative;
    pointer-events: auto;
  }
</style>
