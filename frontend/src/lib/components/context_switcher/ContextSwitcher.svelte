<script lang="ts">
  import type { SubApp } from "./types";
  import { browser } from "$app/environment";

  // Define the sub-apps with their icons, labels, and unique colors
  const subApps: SubApp[] = [
    { id: "discover", label: "Discover", icon: "compass", color: "#3b82f6" }, // Blue
    {
      id: "qualify",
      label: "Qualify",
      icon: "clipboard-check",
      color: "#10b981",
    }, // Emerald
    { id: "nurture", label: "Nurture", icon: "chat-heart", color: "#f59e0b" }, // Amber
    {
      id: "commit",
      label: "Commit",
      icon: "file-earmark-check",
      color: "#ef4444",
    }, // Red
    {
      id: "onboard",
      label: "Onboard",
      icon: "rocket-takeoff",
      color: "#8b5cf6",
    }, // Violet
    {
      id: "support",
      label: "Support",
      icon: "life-preserver",
      color: "#06b6d4",
    }, // Cyan
    {
      id: "expand",
      label: "Expand",
      icon: "arrows-fullscreen",
      color: "#84cc16",
    }, // Lime
    { id: "renew", label: "Renew", icon: "arrow-repeat", color: "#f97316" }, // Orange
    { id: "advocate", label: "Advocate", icon: "megaphone", color: "#ec4899" }, // Pink
  ];

  // Currently active sub-app (for styling)
  export let activeSubApp: string = "discover";

  // Props for sparkler effect
  export let hasNewAccess: boolean = false; // Whether user has access to new context modes
  export let sparkleIntensity: "low" | "medium" | "high" = "medium";
  export let enableSparkler: boolean = false; // Toggle to enable/disable sparkler effect

  // State for collapsible behavior
  let isExpanded = false;
  let isRepositioning = false;
  let isDelayedClosing = false;
  let sparklerActive = false;

  // Get the currently active sub-app object
  $: activeSubAppObj =
    subApps.find((app) => app.id === activeSubApp) || subApps[0];
  $: activeIndex = subApps.findIndex((app) => app.id === activeSubApp);

  // Sparkler effect management - only run in browser environment when enabled
  $: if (
    browser &&
    typeof window !== "undefined" &&
    enableSparkler &&
    hasNewAccess &&
    !isExpanded
  ) {
    startSparkler();
  }

  function startSparkler() {
    if (!browser) return; // Prevent SSR issues

    sparklerActive = true;

    // Create continuous sparkler effect that runs until manually stopped
    const sparklerInterval = setInterval(() => {
      if (!sparklerActive || isExpanded || !browser) {
        clearInterval(sparklerInterval);
        return;
      }
      createSparklerBurst();
    }, 300); // More frequent bursts for dramatic effect

    // Store interval ID for cleanup
    (window as any).sparklerInterval = sparklerInterval;
  }

  function createSparklerBurst() {
    if (!browser) return; // Prevent SSR issues

    const container = document.querySelector(".context-switcher-button.active");
    if (!container) return;

    const rect = container.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    // Create enhanced particle burst for dramatic effect
    const particleCount =
      sparkleIntensity === "low" ? 15 : sparkleIntensity === "medium" ? 25 : 35;

    for (let i = 0; i < particleCount; i++) {
      createSparkleParticle(centerX, centerY, i, particleCount);
    }
  }

  function createSparkleParticle(
    centerX: number,
    centerY: number,
    index: number,
    total: number,
  ) {
    // Staggered particle creation for realistic sparkler effect
    setTimeout(() => {
      if (!browser) return;

      const particle = document.createElement("div");
      particle.className = "sparkle-particle";

      // Golden sparkler colors array
      const goldenColors = [
        "#FFD700",
        "#FFA500",
        "#FF8C00",
        "#FFB347",
        "#FFDF00",
        "#FFCC00",
        "#FFF700",
        "#F4C430",
      ];

      // Extreme sparkler physics - particles that reach page bottom
      const baseAngle = 90; // Straight down (90 degrees)
      const spreadAngle = 70; // ±35° spread for wide coverage
      const angle = baseAngle + (Math.random() - 0.5) * spreadAngle;

      // Massive velocity to reach page bottom (1200-1500px typical viewport height)
      const initialVelocity = 1200 + Math.random() * 800; // 1200-2000px velocity
      const gravity = 1500; // Extreme gravity for dramatic downward acceleration
      const lifetime = 4000 + Math.random() * 2000; // 4-6 seconds for full travel

      // Set initial position with slight randomness
      const startX = centerX + (Math.random() - 0.5) * 20;
      const startY = centerY + (Math.random() - 0.5) * 10;

      particle.style.left = startX + "px";
      particle.style.top = startY + "px";

      // Random golden color
      const color =
        goldenColors[Math.floor(Math.random() * goldenColors.length)];
      particle.style.background = color;
      particle.style.boxShadow = `0 0 4px ${color}, 0 0 8px ${color}40`;

      // Calculate trajectory with gravity
      const radians = (angle * Math.PI) / 180;
      const velocityX = Math.sin(radians) * initialVelocity;
      const velocityY = Math.cos(radians) * initialVelocity;

      // Set CSS variables for realistic sparkler animation
      particle.style.setProperty("--velocity-x", velocityX + "px");
      particle.style.setProperty("--velocity-y", velocityY + "px");
      particle.style.setProperty("--gravity", gravity + "px");
      particle.style.setProperty("--lifetime", lifetime + "ms");

      // Add to body for global positioning
      document.body.appendChild(particle);

      // Remove particle after lifetime or if it goes too far off screen
      setTimeout(() => {
        if (particle.parentNode) {
          particle.remove();
        }
      }, lifetime);

      // Additional cleanup: remove particles that go way off screen early
      setTimeout(() => {
        if (particle.parentNode) {
          const rect = particle.getBoundingClientRect();
          const viewportHeight = window.innerHeight;
          const viewportWidth = window.innerWidth;

          // Remove if particle is way off screen (beyond viewport bounds + buffer)
          if (
            rect.top > viewportHeight + 200 ||
            rect.left < -200 ||
            rect.left > viewportWidth + 200
          ) {
            particle.remove();
          }
        }
      }, lifetime / 2); // Check halfway through lifetime
    }, index * 20); // Faster stagger for more continuous effect
  }

  // Stop sparkler when expanded or disabled - only run in browser environment
  $: if (
    browser &&
    typeof window !== "undefined" &&
    (isExpanded || !enableSparkler)
  ) {
    sparklerActive = false;
    // Clean up interval
    if ((window as any).sparklerInterval) {
      clearInterval((window as any).sparklerInterval);
      (window as any).sparklerInterval = null;
    }
  }

  // Handle mouse enter/leave for expansion
  function handleContainerMouseEnter() {
    if (!isExpanded && !isDelayedClosing) {
      // Start repositioning phase first
      isRepositioning = true;

      // After repositioning animation, start full expansion
      setTimeout(() => {
        isRepositioning = false;
        isExpanded = true;
      }, 200); // Duration of repositioning animation
    }
  }

  function handleContainerMouseLeave() {
    // Only close if we're not in a delayed closing state (from a click)
    if (!isDelayedClosing) {
      isExpanded = false;
      isRepositioning = false;
    }
  }

  // Handle sub-app selection with loveable click animation
  function handleSubAppClick(subApp: SubApp, event: MouseEvent) {
    const button = event.currentTarget as HTMLButtonElement;
    const wasActive = activeSubApp === subApp.id;

    // Add click animation class
    button.classList.add("clicked");

    // Remove the class after animation completes
    setTimeout(() => {
      button.classList.remove("clicked");

      // If this button just became active, add celebration animation
      if (!wasActive && activeSubApp === subApp.id) {
        button.classList.add("newly-active");
        setTimeout(() => {
          button.classList.remove("newly-active");
        }, 800);
      }
    }, 600);

    activeSubApp = subApp.id;

    // Keep the menu open for half a second after selection, then close directly
    isDelayedClosing = true;
    setTimeout(() => {
      isExpanded = false;
      isRepositioning = false;
      isDelayedClosing = false;
    }, 1000);

    // TODO: Implement navigation logic here
    console.log(`Switching to ${subApp.label} (${subApp.id})`);
  }
</script>

<div class="context-switcher">
  <div
    class="context-switcher-container"
    class:expanded={isExpanded}
    class:repositioning={isRepositioning}
    class:delayed-closing={isDelayedClosing}
    on:mouseenter={handleContainerMouseEnter}
    on:mouseleave={handleContainerMouseLeave}
    role="tablist"
    tabindex="0"
    aria-label="Sub-application navigator"
  >
    {#if isExpanded || isDelayedClosing}
      <!-- Show all buttons when fully expanded or in delayed closing -->
      {#each subApps as subApp, index}
        <button
          class="context-switcher-button"
          class:active={activeSubApp === subApp.id}
          class:delayed-appear={index !== activeIndex && !isDelayedClosing}
          data-color={subApp.color}
          style="--button-color: {subApp.color}; --appear-delay: {(index <
          activeIndex
            ? index
            : index - 1) * 50}ms;"
          on:click={(event) => handleSubAppClick(subApp, event)}
          title={subApp.label}
          aria-label={`Switch to ${subApp.label}`}
          role="tab"
          aria-selected={activeSubApp === subApp.id}
        >
          <i class="bi bi-{subApp.icon}" aria-hidden="true"></i>
          <span class="context-switcher-label">{subApp.label}</span>
        </button>
      {/each}
    {:else if isRepositioning}
      <!-- Show repositioning state: active button sliding to its position -->
      {#each subApps as subApp, index}
        {#if activeSubApp === subApp.id}
          <button
            class="context-switcher-button active repositioning-active"
            data-color={subApp.color}
            style="--button-color: {subApp.color}; --target-position: {index *
              3}rem;"
            title={subApp.label}
            aria-label={`Current: ${subApp.label}`}
            role="tab"
            aria-selected="true"
          >
            <i class="bi bi-{subApp.icon}" aria-hidden="true"></i>
            <span class="context-switcher-label">{subApp.label}</span>
          </button>
        {:else}
          <!-- Placeholder buttons to maintain spacing during repositioning -->
          <div
            class="context-switcher-placeholder"
            style="--placeholder-delay: {Math.abs(index - activeIndex) * 20}ms;"
          ></div>
        {/if}
      {/each}
    {:else}
      <!-- Show only active button when collapsed -->
      <button
        class="context-switcher-button active"
        class:sparkler-active={sparklerActive}
        data-color={activeSubAppObj.color}
        style="--button-color: {activeSubAppObj.color};"
        title={`${activeSubAppObj.label} - Hover to expand`}
        aria-label={`Current: ${activeSubAppObj.label}. Hover to expand menu`}
        role="tab"
        aria-selected="true"
      >
        <i class="bi bi-{activeSubAppObj.icon}" aria-hidden="true"></i>
        <span class="context-switcher-label">{activeSubAppObj.label}</span>
      </button>
    {/if}
  </div>
</div>

<style>
  .context-switcher {
    background: var(--color-bg-secondary, #161b22);
    border-bottom: 1px solid var(--color-border-default, #30363d);
    padding: 0.75rem 1rem;
    position: sticky;
    top: 0;
    z-index: 1000;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
  }

  .context-switcher-container {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 0.25rem;
    max-width: 1200px;
    margin: 0;
    flex-wrap: nowrap;
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    overflow: visible;
    position: relative;
    width: fit-content;
  }

  /* Expanded state */
  .context-switcher-container.expanded {
    gap: 0.5rem;
    width: auto;
  }

  /* Repositioning state */
  .context-switcher-container.repositioning {
    gap: 0.5rem;
    width: auto;
    overflow: visible;
  }

  /* Delayed closing state */
  .context-switcher-container.delayed-closing {
    gap: 0.5rem;
    width: auto;
    overflow: visible;
  }

  /* Placeholder elements during repositioning */
  .context-switcher-placeholder {
    width: 3rem;
    height: 3rem;
    opacity: 0;
    transition: opacity 0.1s ease;
    animation: placeholderAppear 0.15s ease forwards;
    animation-delay: var(--placeholder-delay, 0ms);
  }

  @keyframes placeholderAppear {
    to {
      opacity: 0.1;
    }
  }

  /* Repositioning animation for active button */
  .context-switcher-button.repositioning-active {
    position: relative;
    animation: slideToPosition 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94)
      forwards;
  }

  @keyframes slideToPosition {
    from {
      transform: translateX(0);
    }
    to {
      transform: translateX(var(--target-position, 0));
    }
  }

  /* Smooth transitions for buttons appearing/disappearing */
  .context-switcher-button {
    opacity: 1;
    transform: scale(1);
    transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  }

  /* Animation for non-active buttons when expanding - delayed appearance */
  .context-switcher-container.expanded .context-switcher-button.delayed-appear {
    animation: delayedExpandIn 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94)
      forwards;
    animation-delay: var(--appear-delay, 0ms);
    opacity: 0;
    transform: scale(0.8) translateX(-10px);
  }

  @keyframes delayedExpandIn {
    0% {
      opacity: 0;
      transform: scale(0.8) translateX(-10px);
    }
    100% {
      opacity: 1;
      transform: scale(1) translateX(0);
    }
  }

  .context-switcher-button {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 3rem; /* Increased from 2rem to give more space for text */
    height: 3rem; /* Increased from 2rem to give more space for text */
    background: var(--color-bg-tertiary, #21262d);
    border: 1px solid var(--color-border-muted, #21262d);
    border-radius: 0.5rem;
    cursor: pointer;
    padding: 0.375rem;
    text-decoration: none;
    position: relative;
    overflow: visible; /* Changed from hidden to visible to prevent text cutoff */

    /* Default state: grayscale and muted */
    color: var(--color-text-secondary, #7d8590);
    filter: grayscale(1) brightness(0.7);
  }

  /* Hover state: vibrant colors with smooth transition */
  .context-switcher-button:hover {
    background: rgba(0, 0, 0, 0.3);
    border-color: var(--button-color);
    color: var(--button-color);
    filter: grayscale(0) brightness(1.1);
    transform: translateY(-2px);
    box-shadow:
      0 8px 25px rgba(0, 0, 0, 0.4),
      0 0 20px var(--button-color);
  }

  /* Support for color-mix() where available */
  @supports (background: color-mix(in srgb, red, blue)) {
    .context-switcher-button:hover {
      box-shadow:
        0 8px 25px rgba(0, 0, 0, 0.4),
        0 0 20px color-mix(in srgb, var(--button-color) 30%, transparent);
    }
  }

  /* Active state: bright with enhanced glow */
  .context-switcher-button.active {
    /* Fallback for browsers without color-mix */
    background: var(--color-bg-tertiary, #21262d);
    border-color: var(--button-color);
    color: var(--button-color);
    filter: grayscale(0) brightness(1.2);
    box-shadow:
      0 0 0 2px var(--button-color),
      0 4px 15px rgba(0, 0, 0, 0.3);
  }

  /* Enhanced active state with color-mix support */
  @supports (background: color-mix(in srgb, red, blue)) {
    .context-switcher-button.active {
      background: color-mix(
        in srgb,
        var(--button-color) 15%,
        var(--color-bg-tertiary, #21262d)
      );
      box-shadow:
        0 0 0 2px color-mix(in srgb, var(--button-color) 30%, transparent),
        0 4px 15px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 color-mix(in srgb, var(--button-color) 20%, transparent);
    }
  }

  /* Active button hover: even more enhanced */
  .context-switcher-button.active:hover {
    /* Fallback */
    background: var(--color-bg-tertiary, #21262d);
    border-color: var(--button-color);
    color: var(--button-color);
    filter: grayscale(0) brightness(1.3);
    transform: translateY(-3px);
    box-shadow:
      0 0 0 2px var(--button-color),
      0 12px 30px rgba(0, 0, 0, 0.5),
      0 0 25px var(--button-color);
  }

  /* Enhanced with color-mix support */
  @supports (background: color-mix(in srgb, red, blue)) {
    .context-switcher-button.active:hover {
      background: color-mix(
        in srgb,
        var(--button-color) 20%,
        var(--color-bg-tertiary, #21262d)
      );
      box-shadow:
        0 0 0 2px color-mix(in srgb, var(--button-color) 40%, transparent),
        0 12px 30px rgba(0, 0, 0, 0.5),
        0 0 25px color-mix(in srgb, var(--button-color) 40%, transparent),
        inset 0 1px 0 color-mix(in srgb, var(--button-color) 30%, transparent);
    }
  }

  /* Click animation */
  .context-switcher-button:active {
    transform: translateY(-1px);
    transition: all 0.1s ease;
  }

  /* Loveable click animation with bounce effect */
  .context-switcher-button.clicked {
    animation: loveableBounce 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  }

  :global(.context-switcher-button.clicked i) {
    animation: iconPulse 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  }

  /* Add a ripple effect on click */
  .context-switcher-button.clicked::before {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: radial-gradient(
      circle,
      var(--button-color) 0%,
      transparent 70%
    );
    transform: translate(-50%, -50%);
    animation: rippleEffect 0.6s ease-out;
    z-index: -1;
  }

  /* Enhanced glow during click */
  .context-switcher-button.clicked {
    box-shadow:
      0 0 0 3px color-mix(in srgb, var(--button-color) 50%, transparent),
      0 0 30px color-mix(in srgb, var(--button-color) 60%, transparent),
      0 12px 25px rgba(0, 0, 0, 0.4);
  }

  /* Fallback for browsers without color-mix */
  .context-switcher-button.clicked {
    box-shadow:
      0 0 0 3px var(--button-color),
      0 0 30px var(--button-color),
      0 12px 25px rgba(0, 0, 0, 0.4);
  }

  @supports (background: color-mix(in srgb, red, blue)) {
    .context-switcher-button.clicked {
      box-shadow:
        0 0 0 3px color-mix(in srgb, var(--button-color) 50%, transparent),
        0 0 30px color-mix(in srgb, var(--button-color) 60%, transparent),
        0 12px 25px rgba(0, 0, 0, 0.4);
    }
  }

  /* Keyframe animations */
  @keyframes loveableBounce {
    0% {
      transform: translateY(-2px) scale(1);
    }
    25% {
      transform: translateY(-8px) scale(1.1);
      filter: grayscale(0) brightness(1.4);
    }
    50% {
      transform: translateY(-4px) scale(1.05);
      filter: grayscale(0) brightness(1.3);
    }
    75% {
      transform: translateY(-6px) scale(1.08);
      filter: grayscale(0) brightness(1.35);
    }
    100% {
      transform: translateY(-2px) scale(1);
      filter: grayscale(0) brightness(1.2);
    }
  }

  @keyframes iconPulse {
    0% {
      transform: scale(1);
    }
    25% {
      transform: scale(1.3) rotate(5deg);
    }
    50% {
      transform: scale(1.15) rotate(-2deg);
    }
    75% {
      transform: scale(1.25) rotate(3deg);
    }
    100% {
      transform: scale(1);
    }
  }

  @keyframes rippleEffect {
    0% {
      width: 0;
      height: 0;
      opacity: 0.8;
    }
    50% {
      width: 60px;
      height: 60px;
      opacity: 0.4;
    }
    100% {
      width: 90px;
      height: 90px;
      opacity: 0;
    }
  }

  /* Celebration animation for newly active buttons */
  .context-switcher-button.newly-active {
    animation: celebration 0.8s ease-out;
  }

  :global(.context-switcher-button.newly-active i) {
    animation: celebrationIcon 0.8s ease-out;
  }

  @keyframes celebration {
    0%,
    100% {
      transform: translateY(-2px) scale(1);
    }
    20% {
      transform: translateY(-8px) scale(1.15);
    }
    40% {
      transform: translateY(-3px) scale(1.05);
    }
    60% {
      transform: translateY(-6px) scale(1.1);
    }
    80% {
      transform: translateY(-1px) scale(1.02);
    }
  }

  @keyframes celebrationIcon {
    0%,
    100% {
      transform: scale(1) rotate(0deg);
    }
    25% {
      transform: scale(1.4) rotate(10deg);
    }
    50% {
      transform: scale(1.2) rotate(-5deg);
    }
    75% {
      transform: scale(1.3) rotate(8deg);
    }
  }

  .context-switcher-button i {
    font-size: 1.25rem;
    margin-bottom: 0.25rem;
    line-height: 1;
    transition: inherit;
  }

  .context-switcher-label {
    font-size: 0.65rem;
    font-weight: 500;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    overflow: visible; /* Changed to prevent cutoff */
    text-overflow: clip;
    max-width: none; /* Removed max-width constraint */
    transition: inherit;
  }

  /* Sparkler active state - enhanced glow and pulse */
  .context-switcher-button.sparkler-active {
    animation: sparkler-pulse 1.5s ease-in-out infinite;
    box-shadow:
      0 0 0 2px var(--button-color),
      0 0 20px var(--button-color),
      0 0 40px var(--button-color);
  }

  @keyframes sparkler-pulse {
    0%,
    100% {
      transform: scale(1);
      filter: brightness(1.2);
    }
    50% {
      transform: scale(1.05);
      filter: brightness(1.4);
    }
  }

  /* Dark mode specific styles */
  @media (prefers-color-scheme: dark) {
    .context-switcher {
      background: #0d1117;
      border-bottom-color: #30363d;
    }

    .context-switcher-button {
      background: #21262d;
      border-color: #30363d;
      color: #7d8590;
    }

    .context-switcher-button:hover {
      background: rgba(0, 0, 0, 0.4);
    }

    .context-switcher-button.active {
      /* Fallback for dark mode */
      background: #21262d;
    }

    .context-switcher-button.active:hover {
      /* Fallback for dark mode */
      background: #21262d;
    }

    /* Enhanced dark mode with color-mix support */
    @supports (background: color-mix(in srgb, red, blue)) {
      .context-switcher-button.active {
        background: color-mix(in srgb, var(--button-color) 20%, #21262d);
      }

      .context-switcher-button.active:hover {
        background: color-mix(in srgb, var(--button-color) 25%, #21262d);
      }
    }
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .context-switcher {
      padding: 0.375rem;
    }

    .context-switcher-container {
      gap: 0.25rem;
    }

    .context-switcher-container.expanded {
      gap: 0.375rem;
    }

    .context-switcher-button {
      width: 2.5rem;
      height: 2.5rem;
      padding: 0.25rem;
    }

    .context-switcher-button i {
      font-size: 1rem;
      margin-bottom: 0.1875rem;
    }

    .context-switcher-label {
      font-size: 0.55rem;
    }
  }

  @media (max-width: 576px) {
    .context-switcher-container {
      gap: 0.125rem;
    }

    .context-switcher-container.expanded {
      gap: 0.25rem;
    }

    .context-switcher-button {
      width: 2.25rem;
      height: 2.25rem;
      padding: 0.1875rem;
    }

    .context-switcher-button.collapsed-active {
      width: 2.75rem;
      height: 2.75rem;
    }

    .context-switcher-button i {
      font-size: 0.875rem;
      margin-bottom: 0.125rem;
    }

    .context-switcher-label {
      font-size: 0.5rem;
    }
  }

  /* Global sparkle particle effects - positioned absolutely on body */
  :global(.sparkle-particle) {
    position: fixed;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    pointer-events: none;
    z-index: 10000;
    transform-origin: center;
    animation: sparkle-fly var(--lifetime, 1000ms) linear forwards;
  }

  @keyframes sparkle-fly {
    0% {
      opacity: 1;
      transform: scale(1) translate(0, 0);
    }
    20% {
      opacity: 1;
      transform: scale(1.3)
        translate(
          calc(var(--velocity-x, 0px) * 0.2),
          calc(var(--velocity-y, 0px) * 0.2 + var(--gravity, 0px) * 0.04)
        );
    }
    40% {
      opacity: 0.9;
      transform: scale(1.1)
        translate(
          calc(var(--velocity-x, 0px) * 0.4),
          calc(var(--velocity-y, 0px) * 0.4 + var(--gravity, 0px) * 0.16)
        );
    }
    60% {
      opacity: 0.7;
      transform: scale(0.9)
        translate(
          calc(var(--velocity-x, 0px) * 0.6),
          calc(var(--velocity-y, 0px) * 0.6 + var(--gravity, 0px) * 0.36)
        );
    }
    80% {
      opacity: 0.4;
      transform: scale(0.6)
        translate(
          calc(var(--velocity-x, 0px) * 0.8),
          calc(var(--velocity-y, 0px) * 0.8 + var(--gravity, 0px) * 0.64)
        );
    }
    100% {
      opacity: 0;
      transform: scale(0.2)
        translate(
          calc(var(--velocity-x, 0px) * 1),
          calc(var(--velocity-y, 0px) * 1 + var(--gravity, 0px) * 1)
        );
    }
  }

  /* Enhanced sparkler glow when active */
  :global(.sparkle-particle::before) {
    content: "";
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    background: inherit;
    border-radius: 50%;
    opacity: 0.3;
    filter: blur(2px);
  }

  /* Sparkler trail effect */
  :global(.sparkle-particle::after) {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    width: 2px;
    height: 8px;
    background: linear-gradient(to bottom, currentColor, transparent);
    transform: translate(-50%, -100%);
    opacity: 0.4;
  }
</style>
