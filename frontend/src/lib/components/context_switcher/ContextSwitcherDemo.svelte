<script lang="ts">
  import { ContextSwitcher } from "./index";
  import type { SubApp } from "./types";

  let currentSubApp = "nurture";
  let hasNewAccess = true; // Simulate new access to Support mode

  function handleSubAppChange(event: CustomEvent) {
    const subApp = event.detail;
    currentSubApp = subApp.id;

    // If user clicked on Support (the new access), stop the sparkler
    if (subApp.id === "support" && hasNewAccess) {
      hasNewAccess = false;
    }

    console.log(`Switched to: ${subApp.label}`);
    // Here you would implement your actual navigation logic
    // For example: goto(`/${subApp.id}`) or dispatch a custom event
  }
</script>

<div class="demo-container">
  <h2>Context Switcher Demo</h2>

  <!-- Context Switcher Component -->
  <ContextSwitcher
    activeSubApp={currentSubApp}
    {hasNewAccess}
    sparkleIntensity="medium"
    on:subAppChange={handleSubAppChange}
  />

  <div class="demo-content">
    <h3>Current Sub-App: <span class="current-app">{currentSubApp}</span></h3>
    <p>
      The context switcher is now collapsible! Hover over the active icon to
      expand and see all options.
    </p>

    {#if hasNewAccess}
      <div class="new-access-notice">
        <h4>🎉 New Access Available!</h4>
        <p>
          You now have access to the <strong>Support</strong> mode. Notice the sparkler
          effect on the Nurture button!
        </p>
        <p>
          The sparkler will stop when you hover over the menu or after 10
          seconds.
        </p>
      </div>
    {/if}

    <div class="sub-app-descriptions">
      <h4>Sub-App Colors & Descriptions:</h4>
      <ul>
        <li>
          <span class="color-demo" style="background: #3b82f6;"></span><strong
            >Discover:</strong
          > Find new opportunities and leads
        </li>
        <li>
          <span class="color-demo" style="background: #10b981;"></span><strong
            >Qualify:</strong
          > Assess and validate prospects
        </li>
        <li>
          <span class="color-demo" style="background: #f59e0b;"></span><strong
            >Nurture:</strong
          > Build relationships with clients
        </li>
        <li>
          <span class="color-demo" style="background: #ef4444;"></span><strong
            >Commit:</strong
          > Finalize agreements and contracts
        </li>
        <li>
          <span class="color-demo" style="background: #8b5cf6;"></span><strong
            >Onboard:</strong
          > Welcome and setup new clients
        </li>
        <li>
          <span class="color-demo" style="background: #06b6d4;"></span><strong
            >Support:</strong
          > Provide ongoing assistance
        </li>
        <li>
          <span class="color-demo" style="background: #84cc16;"></span><strong
            >Expand:</strong
          > Grow existing relationships
        </li>
        <li>
          <span class="color-demo" style="background: #f97316;"></span><strong
            >Renew:</strong
          > Extend and refresh contracts
        </li>
        <li>
          <span class="color-demo" style="background: #ec4899;"></span><strong
            >Advocate:</strong
          > Promote and represent clients
        </li>
      </ul>

      <div class="interaction-guide">
        <h5>🎨 Collapsible Design Features:</h5>
        <p>
          <strong>Collapsed State:</strong> Shows only the active sub-app icon for
          space efficiency
        </p>
        <p>
          <strong>Hover Expansion:</strong> Smoothly expands to reveal all sub-app
          options
        </p>
        <p>
          <strong>Compact Size:</strong> 50% smaller buttons (2rem instead of 4rem)
          for better space usage
        </p>
        <p>
          <strong>Enhanced Icons:</strong> Larger icons with better fill and visibility
        </p>

        <h5>🎨 Color Interactions:</h5>
        <p><strong>Default:</strong> Icons appear grayscale and muted</p>
        <p>
          <strong>Hover:</strong> Icons transition to vibrant colors with glow effects
        </p>
        <p>
          <strong>Active:</strong> Current sub-app stays colored with enhanced brightness
        </p>
        <p>
          <strong>Click:</strong> Loveable bounce animation with icon pulse, ripple
          effect, and enhanced glow
        </p>
        <p>
          <strong>New Active:</strong> Celebration animation when switching to a
          new sub-app
        </p>
      </div>
    </div>
  </div>
</div>

<style>
  .demo-container {
    min-height: 100vh;
    background: var(--color-bg-primary, #0d1117);
    color: var(--color-text-primary, #f0f6fc);
    padding: 2rem;
  }

  .demo-content {
    max-width: 800px;
    margin: 2rem auto;
    padding: 2rem;
    background: var(--color-bg-secondary, #161b22);
    border: 1px solid var(--color-border-default, #30363d);
    border-radius: 0.5rem;
  }

  .current-app {
    color: var(--bs-primary, #0d6efd);
    text-transform: capitalize;
    font-weight: 600;
  }

  .sub-app-descriptions {
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--color-border-muted, #21262d);
  }

  .sub-app-descriptions ul {
    list-style: none;
    padding: 0;
  }

  .sub-app-descriptions li {
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--color-border-muted, #21262d);
  }

  .sub-app-descriptions li:last-child {
    border-bottom: none;
  }

  .color-demo {
    display: inline-block;
    width: 1rem;
    height: 1rem;
    border-radius: 0.25rem;
    margin-right: 0.5rem;
    vertical-align: middle;
    border: 1px solid rgba(255, 255, 255, 0.2);
  }

  .new-access-notice {
    margin: 1.5rem 0;
    padding: 1rem;
    background: linear-gradient(135deg, #06b6d4, #0891b2);
    border-radius: 0.5rem;
    border: 1px solid #0e7490;
    animation: glow-pulse 2s ease-in-out infinite;
  }

  .new-access-notice h4 {
    margin: 0 0 0.5rem 0;
    color: #ffffff;
    font-size: 1.1rem;
  }

  .new-access-notice p {
    margin: 0.25rem 0;
    color: #f0f9ff;
    font-size: 0.9rem;
  }

  .new-access-notice strong {
    color: #ffffff;
    font-weight: 600;
  }

  @keyframes glow-pulse {
    0%,
    100% {
      box-shadow: 0 0 5px rgba(6, 182, 212, 0.5);
    }
    50% {
      box-shadow:
        0 0 20px rgba(6, 182, 212, 0.8),
        0 0 30px rgba(6, 182, 212, 0.4);
    }
  }

  .interaction-guide {
    margin-top: 1.5rem;
    padding: 1rem;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 0.5rem;
    border-left: 4px solid var(--bs-primary, #0d6efd);
  }

  .interaction-guide h5 {
    margin-bottom: 0.75rem;
    color: var(--color-text-primary, #f0f6fc);
  }

  .interaction-guide p {
    margin-bottom: 0.5rem;
    color: var(--color-text-secondary, #9198a1);
    font-size: 0.9rem;
  }

  .interaction-guide p:last-child {
    margin-bottom: 0;
  }

  h2 {
    text-align: center;
    margin-bottom: 2rem;
    color: var(--color-text-primary, #f0f6fc);
  }

  h3,
  h4 {
    color: var(--color-text-primary, #f0f6fc);
  }
</style>
