<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { closeAllPopups } from "./popup.store";

  export let title: string = "";
  export let width: string = "400px";
  export let maxHeight: string = "80vh";

  const dispatch = createEventDispatcher();

  function handleClose() {
    closeAllPopups();
    dispatch("close");
  }

  function handleBackdropClick(event: MouseEvent) {
    if (event.target === event.currentTarget) {
      handleClose();
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === "Escape") {
      handleClose();
    }
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<!-- Backdrop -->
<div
  class="popup-backdrop"
  on:click={handleBackdropClick}
  role="dialog"
  aria-modal="true"
  aria-labelledby="popup-title"
>
  <!-- Popup Container -->
  <div
    class="popup-container shadow-lg"
    style="width: {width}; max-height: {maxHeight}"
  >
    <!-- Header -->
    <div class="popup-header">
      <h5 id="popup-title" class="popup-title mb-0">
        {title}
      </h5>
      <button
        type="button"
        class="btn-close btn-close-white"
        aria-label="Close"
        on:click={handleClose}
      ></button>
    </div>

    <!-- Content -->
    <div class="popup-content">
      <slot />
    </div>
  </div>
</div>

<style>
  .popup-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding-top: 80px;
    z-index: 1050;
    animation: fadeIn 0.2s ease-out;
  }

  .popup-container {
    background: linear-gradient(145deg, #2c3e50, #34495e);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    overflow: hidden;
    animation: slideIn 0.3s ease-out;
    max-width: 90vw;
  }

  .popup-header {
    background: linear-gradient(145deg, #1a252f, #2c3e50);
    padding: 1rem 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .popup-title {
    color: #fff;
    font-weight: 600;
  }

  .popup-content {
    padding: 1.5rem;
    max-height: calc(80vh - 70px);
    overflow-y: auto;
  }

  .popup-content::-webkit-scrollbar {
    width: 8px;
  }

  .popup-content::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
  }

  .popup-content::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 4px;
  }

  .popup-content::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.5);
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-20px) scale(0.95);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }
</style>
