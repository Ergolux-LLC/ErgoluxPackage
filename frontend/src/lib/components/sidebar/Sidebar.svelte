<script lang="ts">
  import { ContextSwitcher } from "$lib/components/context_switcher";

  // Props for context switcher
  export let activeSubApp: string = "discover";
  export let hasNewAccess: boolean = false;
  export let enableSparkler: boolean = false;
  export let sparkleIntensity: "low" | "medium" | "high" = "medium";
</script>

<!-- Main sidebar container -->

<aside class="sidebar">
  <div class="sidebar-content">
    <!-- Context Switcher at the top -->
    <div class="sidebar-section">
      <ContextSwitcher
        {activeSubApp}
        {hasNewAccess}
        {enableSparkler}
        {sparkleIntensity}
      />
    </div>

    <!-- Future sidebar content can go here -->
    <!-- 
    <div class="sidebar-section">
      Future navigation or tools
    </div>
    -->
  </div>
</aside>

<style>
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: 280px; /* Fixed sidebar width */
    height: 100vh;
    background-color: #000000; /* Completely black background */
    border-right: 1px solid var(--color-border-default, #30363d);
    overflow-y: auto;
    overflow-x: hidden;
    z-index: 100000; /* High z-index to appear above main content */
    display: flex;
    flex-direction: column;
    /* Prevent flicker during hydration */
    opacity: 1;
    transition: opacity 0.15s ease-in-out;
  }

  .sidebar-content {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 0; /* No padding - let components manage their own spacing */
  }

  .sidebar-section {
    flex-shrink: 0; /* Prevent sections from shrinking */
  }

  .sidebar-section:not(:last-child) {
    border-bottom: 1px solid var(--color-border-muted, #21262d);
  }

  /* Responsive behavior for smaller screens */
  @media (max-width: 768px) {
    .sidebar {
      width: 100%;
      position: relative;
      height: auto;
      border-right: none;
      border-bottom: 1px solid var(--color-border-default, #30363d);
    }
  }
</style>
