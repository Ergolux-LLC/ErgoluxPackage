<script lang="ts">
  import { fade } from "svelte/transition";
  import { onMount, onDestroy, createEventDispatcher, tick } from "svelte";

  // Props
  export let initialDelay = 0; // Delay before showing content (ms)
  export let fadeInDuration = 1000; // Duration of fade in (ms)
  export let fadeOutDuration = 1000; // Duration of fade out (ms)
  export let showNotification = false; // Whether to show completion notification

  // Internal state
  let ready = false;
  let fadeOutComplete = false;
  let fadeOutRequested = false;
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  // Event dispatcher
  const dispatch = createEventDispatcher<{
    ready: void; // Fired when component is ready to be shown
    complete: void; // Fired when fade out is complete
  }>();

  // Initialize with optional delay
  onMount(() => {
    console.log("FadeTransition mounted with initialDelay:", initialDelay);
    if (initialDelay > 0) {
      timeoutId = setTimeout(() => {
        console.log("Initial delay completed, setting ready=true");
        ready = true;
        dispatch("ready");
      }, initialDelay);
    } else {
      ready = true;
      dispatch("ready");
    }
  });

  // Clean up timeouts on destroy
  onDestroy(() => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
  });

  // Handle fade out
  export async function fadeOut() {
    console.log("FadeTransition fadeOut called");
    fadeOutRequested = true;
    fadeOutComplete = false;

    // Ensure DOM updates before changing state
    await tick();

    // Set ready to false to trigger the fade-out animation
    ready = false;
  }

  // Handle outroend event
  function handleOutroEnd() {
    console.log("FadeTransition outroend event triggered");
    fadeOutComplete = true;
    fadeOutRequested = false;
    dispatch("complete");
  }
</script>

<div class="fade-transition-wrapper">
  {#if showNotification && fadeOutComplete}
    <div class="fade-out-notification">
      <slot name="notification">Transition complete</slot>
    </div>
  {/if}

  {#if ready}
    <div
      in:fade={{ duration: fadeInDuration }}
      out:fade={{ duration: fadeOutDuration }}
      on:outroend={handleOutroEnd}
      class="fade-transition-content"
    >
      <slot />
    </div>
  {/if}
</div>

<style>
  .fade-transition-wrapper {
    position: relative;
    width: 100%;
    height: 100%;
  }

  .fade-transition-content {
    width: 100%;
    height: 100%;
  }

  .fade-out-notification {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background-color: rgba(79, 140, 255, 0.9);
    color: white;
    padding: 20px;
    border-radius: 10px;
    font-size: 1.2em;
    font-weight: bold;
    text-align: center;
    z-index: 100;
    max-width: 300px;
  }
</style>
