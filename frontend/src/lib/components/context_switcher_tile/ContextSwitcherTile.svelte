<script lang="ts">
  import { createEventDispatcher, onDestroy } from "svelte";

  export let name: string = "Untitled";
  export let id: string = "untitled";
  export let icon: string = "bi-question-circle";
  export let color: string | undefined;
  export let triggerBg: string | undefined;

  // when true, the tile will always render its plate background (used for the trigger button)
  export let alwaysShowBg: boolean = false;

  // when true, the tile will NOT run the dramatic click animation; it will dispatch immediately
  export let disableClickAnimation: boolean = false;

  const dispatch = createEventDispatcher();

  let plateEl: HTMLElement | null = null;
  let isHovered = false;
  let isActive = false;
  let isAnimating = false;
  $: tooltipId = `${id}-tooltip`;
  let tooltipEl: HTMLDivElement | null = null;

  // Use explicit colors provided by props - no calculations
  $: effectiveColor = (color && color.trim()) || "#0d6efd";
  $: hoverColor = (triggerBg && triggerBg.trim()) || "#333333";

  // wait for either a transitionend or animationend on an element (filter by propertyNames if provided)
  function waitForAnimationOrTransition(
    el: HTMLElement | null,
    props: string[] = [],
    timeout = 1200,
  ) {
    return new Promise<void>((resolve) => {
      if (!el) return resolve();
      let done = false;
      const onEnd = (e: Event & { propertyName?: string }) => {
        // if props provided, only accept matching transition property names
        if (
          props.length === 0 ||
          (e && "propertyName" in e && props.includes((e as any).propertyName))
        )
          cleanup();
        // if this is animationend (no propertyName), accept it
        if ((e as AnimationEvent).animationName) cleanup();
      };
      const cleanup = () => {
        if (done) return;
        done = true;
        el.removeEventListener("transitionend", onEnd as any);
        el.removeEventListener("animationend", onEnd as any);
        clearTimeout(timer);
        resolve();
      };
      const timer = setTimeout(cleanup, timeout);
      el.addEventListener("transitionend", onEnd as any);
      el.addEventListener("animationend", onEnd as any);
    });
  }

  // click handler: run tap animation and dispatch only after animation completes
  async function onClick() {
    if (isAnimating) return;

    // If animations are disabled for this instance (the trigger), send immediately.
    if (disableClickAnimation) {
      dispatch("select", { id });
      return;
    }

    isAnimating = true;
    isActive = true;
    // apply dramatic animation via CSS 'active' class; wait for animationend/transitionend
    const iconEl = plateEl?.querySelector(".icon") as HTMLElement | null;
    // give the browser one frame to apply class changes
    await Promise.resolve();
    await Promise.all([
      waitForAnimationOrTransition(plateEl, [], 1400),
      waitForAnimationOrTransition(iconEl, [], 1400),
    ]);

    // dispatch only after dramatic animation completes
    dispatch("select", { id });

    // reset states
    isActive = false;
    isAnimating = false;
  }

  function createTooltip() {
    if (tooltipEl) return;
    tooltipEl = document.createElement("div");
    tooltipEl.id = tooltipId;
    tooltipEl.setAttribute("role", "tooltip");
    tooltipEl.textContent = name;
    Object.assign(tooltipEl.style, {
      position: "fixed",
      background: "rgba(0,0,0,0.86)",
      color: "#fff",
      padding: "6px 8px",
      borderRadius: "6px",
      fontSize: "12px",
      whiteSpace: "nowrap",
      pointerEvents: "none",
      zIndex: "2147483647",
      opacity: "1" /* show immediately, no transition */,
      transform: "none" /* no slide animation */,
    });
    document.body.appendChild(tooltipEl);
    // position immediately (no animation)
    positionTooltip();
    window.addEventListener("scroll", positionTooltip, true);
    window.addEventListener("resize", positionTooltip);
  }

  function positionTooltip() {
    if (!tooltipEl || !plateEl) return;
    const rect = plateEl.getBoundingClientRect();
    const top = Math.round(rect.bottom + 8); // below the icon
    const left = Math.round(rect.left + rect.width / 2);
    tooltipEl.style.top = `${top}px`;
    tooltipEl.style.left = `${left}px`;
    tooltipEl.style.transform = "translateX(-50%)";
  }

  function removeTooltip() {
    if (!tooltipEl) return;
    // remove immediately (no fade-out)
    if (tooltipEl.parentNode) tooltipEl.parentNode.removeChild(tooltipEl);
    tooltipEl = null;
    window.removeEventListener("scroll", positionTooltip, true);
    window.removeEventListener("resize", positionTooltip);
  }

  onDestroy(() => {
    removeTooltip();
  });
</script>

<button
  class="tile-button"
  aria-describedby={isHovered ? tooltipId : undefined}
  aria-label={name}
  on:mouseenter={() => {
    isHovered = true;
    createTooltip();
  }}
  on:mouseleave={() => {
    isHovered = false;
    removeTooltip();
  }}
  on:mousemove={() => positionTooltip()}
  on:click={onClick}
  type="button"
  bind:this={plateEl}
  style="background: transparent; border: 0; padding: 0;"
>
  <div
    class="tile-plate {isActive ? 'active' : ''}"
    aria-hidden="true"
    style="background-color: {alwaysShowBg || isHovered || isActive
      ? hoverColor
      : 'transparent'};"
  >
    <i
      class="icon bi {icon}"
      aria-hidden="true"
      style="color: {isHovered || isActive
        ? effectiveColor
        : 'rgba(255,255,255,0.9)'};"
    ></i>
  </div>
</button>

<style>
  /* plate animation: background-color + transform; icon animates color + transform */
  .tile-button {
    cursor: pointer;
    outline: none;
    background: transparent;
    border: 0;
    padding: 0;
  }
  .tile-plate {
    width: 56px;
    height: 56px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    background-color: #222;
    transition: background-color 160ms linear;
    will-change: transform, background-color, box-shadow;
  }
  /* dramatic keyframes for a clear, satisfying tap with overshoot/bounce and shadow */
  @keyframes dramatic-plate {
    0% {
      transform: translateY(0) scale(1);
      box-shadow: none;
    }
    18% {
      transform: translateY(-10px) scale(1.18);
      box-shadow: 0 20px 36px rgba(0, 0, 0, 0.45);
    }
    45% {
      transform: translateY(6px) scale(0.88);
      box-shadow: 0 6px 18px rgba(0, 0, 0, 0.28);
    }
    70% {
      transform: translateY(-4px) scale(1.06);
      box-shadow: 0 12px 26px rgba(0, 0, 0, 0.36);
    }
    100% {
      transform: translateY(0) scale(1);
      box-shadow: none;
    }
  }

  @keyframes dramatic-icon {
    0% {
      transform: scale(1) rotate(0deg);
      opacity: 1;
    }
    20% {
      transform: scale(1.2) rotate(-8deg);
      opacity: 1;
    }
    50% {
      transform: scale(0.86) rotate(8deg);
      opacity: 0.95;
    }
    80% {
      transform: scale(1.06) rotate(-3deg);
      opacity: 1;
    }
    100% {
      transform: scale(1) rotate(0deg);
      opacity: 1;
    }
  }

  /* background-color for .tile-plate.hovered is set inline by Svelte */

  /* apply dramatic animation on active state */
  .tile-plate.active {
    animation: dramatic-plate 900ms cubic-bezier(0.2, 0.9, 0.26, 1) both;
  }

  .icon {
    font-size: 22px;
    transition: color 120ms linear;
    will-change: color, transform;
  }
  .tile-plate.active .icon {
    animation: dramatic-icon 900ms cubic-bezier(0.2, 0.9, 0.26, 1) both;
  }
</style>
