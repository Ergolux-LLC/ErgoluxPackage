<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  function portal(node: HTMLElement) {
    document.body.appendChild(node);
    return {
      destroy() {
        if (node.parentNode) node.parentNode.removeChild(node);
      },
    };
  }
  // anchor is the in-flow placeholder element; we measure it and mirror its box on the trigger inside the portal
  let anchorEl: HTMLElement | null = null;
  let portalStyle = "";
  let triggerStyle = "";
  // currently selected icon class (changes the trigger icon)
  let selected = "bi-list";
  // trigger visuals (color + bg) mirror the selected icon
  let triggerColor = "var(--icon-trigger)";
  let triggerBg = "var(--cs-bg)";

  let expanded = false;
  let portalEl: HTMLDivElement | null = null;
  let ro: ResizeObserver | null = null;

  // clicked icon state + collapse timer
  let clickedIcon: string | null = null;
  let collapseTimer: number | null = null;

  // animation + hold timings (ms)
  const CLICK_ANIM_MS = 1000; // matches cs-click keyframes duration
  const HOLD_AFTER_ANIM_MS = 500; // extra time to keep the item bar visible after animation

  // mapping from icon class -> color + trigger-background vars (use darker trigger variants so trigger stays dark)
  const ICON_MAP: Record<string, { color: string; bg?: string }> = {
    "bi-list": { color: "var(--icon-trigger)", bg: "var(--cs-bg)" },
    "bi-house": {
      color: "var(--icon-home)",
      bg: "var(--icon-home-trigger-bg)",
    },
    "bi-search": {
      color: "var(--icon-search)",
      bg: "var(--icon-search-trigger-bg)",
    },
    "bi-bell": { color: "var(--icon-bell)", bg: "var(--icon-bell-trigger-bg)" },
    "bi-person": {
      color: "var(--icon-person)",
      bg: "var(--icon-person-trigger-bg)",
    },
    "bi-gear": { color: "var(--icon-gear)", bg: "var(--icon-gear-trigger-bg)" },
    "bi-calendar": {
      color: "var(--icon-calendar)",
      bg: "var(--icon-calendar-trigger-bg)",
    },
    "bi-envelope": {
      color: "var(--icon-envelope)",
      bg: "var(--icon-envelope-trigger-bg)",
    },
    "bi-camera": {
      color: "var(--icon-camera)",
      bg: "var(--icon-camera-trigger-bg)",
    },
    "bi-chat": { color: "var(--icon-chat)", bg: "var(--icon-chat-trigger-bg)" },
    "bi-cloud": {
      color: "var(--icon-cloud)",
      bg: "var(--icon-cloud-trigger-bg)",
    },
  };

  function applyTriggerVisuals(iconClass: string) {
    const mapping = ICON_MAP[iconClass] || ICON_MAP["bi-list"];
    triggerColor = mapping.color;
    // Keep the trigger background constant (dark mode) regardless of icon selection.
    // Only the icon color should change — prevent per-icon translucent backgrounds
    // from making the trigger appear transparent or black during animations.
    triggerBg = "var(--cs-bg)";
  }

  // helper to start/clear a collapse timer. default 1000ms for mouse-leave collapse.
  function startCollapseTimer(ms = 1000) {
    if (collapseTimer) {
      clearTimeout(collapseTimer);
      collapseTimer = null;
    }
    collapseTimer = window.setTimeout(() => {
      expanded = false;
      // keep clickedIcon until animation+hold finishes (select() manages that)
      if (!clickedIcon) updatePortalPosition();
      collapseTimer = null;
    }, ms);
  }

  function clearCollapseTimer() {
    if (collapseTimer) {
      clearTimeout(collapseTimer);
      collapseTimer = null;
    }
  }

  // keep items visible if a selection was clicked until the animation + hold time completes
  function handleItemsMouseLeave() {
    // if a click animation is in progress, do nothing; select() sets its own timer
    if (clickedIcon) return;
    // start a 1s collapse after the user leaves (this is the requested behaviour)
    if (!collapseTimer) startCollapseTimer(1000);
  }

  function updatePortalPosition() {
    if (anchorEl) {
      const rect = anchorEl.getBoundingClientRect();
      const cs = getComputedStyle(anchorEl);

      // Extract margin/padding/border-radius so the trigger inside the portal matches the anchor
      const margin =
        cs.margin ||
        `${cs.marginTop} ${cs.marginRight} ${cs.marginBottom} ${cs.marginLeft}`;
      const padding =
        cs.padding ||
        `${cs.paddingTop} ${cs.paddingRight} ${cs.paddingBottom} ${cs.paddingLeft}`;
      const borderRadius = cs.borderRadius || "6px";

      // getBoundingClientRect does not include margins, so offset the portal by negative margins
      const marginTop = parseFloat(cs.marginTop || "0") || 0;
      const marginLeft = parseFloat(cs.marginLeft || "0") || 0;

      // Position portal so the trigger (first child) overlays the anchor including margins
      const top = rect.top - marginTop;
      const left = rect.left - marginLeft;

      // ensure portal box is exactly the same height as the trigger (anchor)
      portalStyle = `top: ${top}px; left: ${left}px; height: ${rect.height}px; z-index:2147483647;`;

      // Trigger style mirrors anchor box (width/height/margin/padding/border-radius)
      triggerStyle = [
        `width: ${rect.width}px`,
        `height: ${rect.height}px`,
        `margin: ${margin}`,
        `padding: ${padding}`,
        `border-radius: ${borderRadius}`,
        `border: none`,
      ].join("; ");
    } else {
      portalStyle = "top:20px;left:60px;z-index:2147483647;";
      triggerStyle =
        "width:40px;height:40px;padding:0;margin:0;border-radius:6px;border:none;";
    }
  }

  // toggle portal items; trigger always visible
  function togglePortal() {
    expanded = !expanded;
    // when opening, ensure we clear any pending collapse timer
    if (expanded) {
      clearCollapseTimer();
      updatePortalPosition();
    } else {
      // if closed immediately by toggle, clear click state/timers
      if (!clickedIcon) clearCollapseTimer();
    }
  }

  // ensure portal/trigger are positioned initially and on changes
  onMount(() => {
    updatePortalPosition();
    window.addEventListener("resize", updatePortalPosition);
    window.addEventListener("scroll", updatePortalPosition, true);

    if ("ResizeObserver" in window && anchorEl) {
      ro = new ResizeObserver(() => updatePortalPosition());
      ro.observe(anchorEl);
    }

    return () => {
      window.removeEventListener("resize", updatePortalPosition);
      window.removeEventListener("scroll", updatePortalPosition, true);
      ro?.disconnect();
    };
  });

  onDestroy(() => {
    if (collapseTimer) {
      clearTimeout(collapseTimer);
      collapseTimer = null;
    }
  });

  function showPortal() {
    expanded = true;
    updatePortalPosition();
  }

  function hidePortal() {
    // only collapse the items — keep portalStyle/triggerStyle so the trigger stays visible
    expanded = false;
  }

  // select mode: set trigger icon immediately, animate clicked item and collapse after 1s
  function select(iconClass: string) {
    selected = iconClass;
    // immediately update trigger visuals to match selection
    applyTriggerVisuals(iconClass);
    // mark which item was clicked to run the animation
    clickedIcon = iconClass;

    // reset any existing timer
    if (collapseTimer) {
      clearTimeout(collapseTimer);
      collapseTimer = null;
    }

    // wait animation duration + extra hold time before collapsing so the click animation can play
    collapseTimer = window.setTimeout(() => {
      expanded = false;
      clickedIcon = null;
      updatePortalPosition();
      collapseTimer = null;
    }, CLICK_ANIM_MS + HOLD_AFTER_ANIM_MS);
  }

  // set initial trigger visuals based on default selection
  applyTriggerVisuals(selected);
</script>

<!-- Invisible anchor placeholder for context switcher -->
<!-- Anchor remains in the document flow and is measured to size/position the trigger inside the portal -->
<a
  href="#context-switcher-anchor"
  id="context-switcher-anchor"
  bind:this={anchorEl}
  style="display: block; height: 40px; width: 40px; margin: 0; padding: 0; border: none;"
  aria-hidden="true"
  tabindex="-1"
></a>

<!-- Trigger button in normal flow -->
<div class="d-flex align-items-center p-2">
  <!-- The portal is always rendered so the trigger button (inside the portal) is always visible.
       The other switcher items live in a separate container and are only shown when "expanded" -->
  <div
    use:portal
    class="context-switcher__portal d-flex align-items-center shadow rounded flex-nowrap"
    bind:this={portalEl}
    role="dialog"
    aria-label="Context switcher menu"
    tabindex="-1"
    style={portalStyle}
    on:mouseenter={clearCollapseTimer}
    on:mouseleave={handleItemsMouseLeave}
  >
    <!-- Wrap so portal bounding box stays the trigger only; items are absolutely positioned -->
    <div class="context-switcher__inner">
      <!-- Trigger button (always visible). Clicking toggles the items. -->
      <button
        aria-label="Open context switcher"
        class="context-switcher__trigger btn d-flex align-items-center justify-content-center"
        style={triggerStyle +
          `; background: ${triggerBg}; color: ${triggerColor};`}
        tabindex="0"
        on:click={togglePortal}
      >
        <i class={"bi " + selected + " fs-3"}></i>
      </button>

      <!-- Items are positioned to the right of the trigger and animated via scaleX.
           They are always present in DOM so we can animate expansion from the trigger. -->
      <div
        class="context-switcher__items d-flex align-items-center"
        class:is-expanded={expanded}
        class:is-collapsed={!expanded}
        role="menu"
        tabindex="-1"
        aria-hidden={!expanded}
        on:mouseenter={clearCollapseTimer}
        on:mouseleave={handleItemsMouseLeave}
      >
        <div class="context-switcher__items-inner d-flex align-items-center">
          <button
            class="btn btn-link p-2"
            class:is-clicked={clickedIcon === "bi-house"}
            aria-label="Home"
            on:click={() => select("bi-house")}
            ><i class="bi bi-house"></i></button
          >
          <button
            class="btn btn-link p-2"
            class:is-clicked={clickedIcon === "bi-search"}
            aria-label="Search"
            on:click={() => select("bi-search")}
            ><i class="bi bi-search"></i></button
          >
          <button
            class="btn btn-link p-2"
            class:is-clicked={clickedIcon === "bi-bell"}
            aria-label="Bell"
            on:click={() => select("bi-bell")}
            ><i class="bi bi-bell"></i></button
          >
          <button
            class="btn btn-link p-2"
            class:is-clicked={clickedIcon === "bi-person"}
            aria-label="Person"
            on:click={() => select("bi-person")}
            ><i class="bi bi-person"></i></button
          >
          <button
            class="btn btn-link p-2"
            class:is-clicked={clickedIcon === "bi-gear"}
            aria-label="Gear"
            on:click={() => select("bi-gear")}
            ><i class="bi bi-gear"></i></button
          >
          <button
            class="btn btn-link p-2"
            class:is-clicked={clickedIcon === "bi-calendar"}
            aria-label="Calendar"
            on:click={() => select("bi-calendar")}
            ><i class="bi bi-calendar"></i></button
          >
          <button
            class="btn btn-link p-2"
            class:is-clicked={clickedIcon === "bi-envelope"}
            aria-label="Envelope"
            on:click={() => select("bi-envelope")}
            ><i class="bi bi-envelope"></i></button
          >
          <button
            class="btn btn-link p-2"
            class:is-clicked={clickedIcon === "bi-camera"}
            aria-label="Camera"
            on:click={() => select("bi-camera")}
            ><i class="bi bi-camera"></i></button
          >
          <button
            class="btn btn-link p-2"
            class:is-clicked={clickedIcon === "bi-chat"}
            aria-label="Chat"
            on:click={() => select("bi-chat")}
            ><i class="bi bi-chat"></i></button
          >
          <button
            class="btn btn-link p-2"
            class:is-clicked={clickedIcon === "bi-cloud"}
            aria-label="Cloud"
            on:click={() => select("bi-cloud")}
            ><i class="bi bi-cloud"></i></button
          >
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  /* dark-mode palette (not pure black) */
  :root {
    --cs-bg: #263038; /* trigger background (keep fully opaque) */
    --cs-panel: rgba(31, 38, 43, 0.88); /* was #1f262b */
    --icon-muted: rgba(255, 255, 255, 0.65);
    --icon-muted-items: rgba(255, 255, 255, 0.45);
    --icon-vibrant: #63d3ff; /* fallback vibrant accent (cyan) */
    --transition-fast: 120ms;
    --transition-medium: 180ms;

    /* per-icon vibrant colours (dark-mode friendly) */
    --icon-trigger: #63d3ff;
    --icon-home: #7bd389; /* green */
    --icon-search: #ffd66b; /* yellow */
    --icon-bell: #ffb86b; /* orange */
    --icon-person: #a78bfa; /* purple */
    --icon-gear: #63d3ff; /* cyan */
    --icon-calendar: #ff6b9a; /* pink */
    --icon-envelope: #6be0ff; /* light-cyan */
    --icon-camera: #f0b6ff; /* lavendar */
    --icon-chat: #9be6a8; /* mint */
    --icon-cloud: #74e0ff; /* sky */

    /* per-icon translucent bg colours used on hover / trigger background options */
    --icon-home-bg: rgba(123, 211, 137, 0.12);
    --icon-home-trigger-bg: rgba(123, 211, 137, 0.18);
    --icon-search-bg: rgba(255, 214, 107, 0.12);
    --icon-search-trigger-bg: rgba(255, 214, 107, 0.18);
    --icon-bell-bg: rgba(255, 184, 107, 0.12);
    --icon-bell-trigger-bg: rgba(255, 184, 107, 0.18);
    --icon-person-bg: rgba(167, 139, 250, 0.12);
    --icon-person-trigger-bg: rgba(167, 139, 250, 0.18);
    --icon-gear-bg: rgba(99, 211, 255, 0.08);
    --icon-gear-trigger-bg: rgba(99, 211, 255, 0.12);
    --icon-calendar-bg: rgba(255, 107, 154, 0.12);
    --icon-calendar-trigger-bg: rgba(255, 107, 154, 0.18);
    --icon-envelope-bg: rgba(107, 224, 255, 0.12);
    --icon-envelope-trigger-bg: rgba(107, 224, 255, 0.18);
    --icon-camera-bg: rgba(240, 182, 255, 0.12);
    --icon-camera-trigger-bg: rgba(240, 182, 255, 0.18);
    --icon-chat-bg: rgba(155, 230, 168, 0.12);
    --icon-chat-trigger-bg: rgba(155, 230, 168, 0.18);
    --icon-cloud-bg: rgba(116, 224, 255, 0.12);
    --icon-cloud-trigger-bg: rgba(116, 224, 255, 0.18);
  }

  /* remove default blue focus outline (we keep visible focus styles on the icon via color/scale) */
  .context-switcher__trigger:focus {
    outline: none;
    box-shadow: none;
  }

  /* Make trigger visible always and darkmode; inline styles may exist, use CSS defaults but allow inline override */
  .context-switcher__trigger {
    /* rounded box appearance for the trigger */
    background: var(--cs-bg);
    color: var(--icon-muted);
    border: none !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.35);
    margin: 0 !important;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition:
      transform var(--transition-fast) ease,
      color var(--transition-fast) ease,
      filter var(--transition-fast) ease,
      background var(--transition-fast) ease;
    will-change: transform, filter, background;
    /* enforce rounded box even when triggerStyle inlines border-radius */
    border-radius: 10px !important;
    overflow: hidden;
    /* ensure visible box shape even if anchor size is small */
    min-width: 40px;
    min-height: 40px;
    padding: 6px 8px !important;
  }

  /* Ensure the trigger background is always the dark CS background and cannot
     be overridden by inline styles or animation keyframes (keeps UI consistent). */
  .context-switcher__trigger {
    background: var(--cs-bg) !important;
  }

  /* trigger icon should inherit the button color so it exactly matches the chosen mapping */
  .context-switcher__trigger i {
    color: inherit !important;
    display: inline-block;
    transition:
      transform var(--transition-fast) ease,
      color var(--transition-fast) ease,
      filter var(--transition-fast) ease,
      background var(--transition-fast) ease,
      padding var(--transition-fast) ease;
    transform-origin: center;
    will-change: transform, color, filter, background, padding;
    font-size: 1.25rem;
    background: transparent;
    padding: 0;
    border-radius: 8px;
  }

  /* keep item icons separate and muted by default */
  .context-switcher__items button i {
    color: var(--icon-muted-items);
    display: inline-block;
    transition:
      transform var(--transition-fast) ease,
      color var(--transition-fast) ease,
      filter var(--transition-fast) ease,
      background var(--transition-fast) ease,
      padding var(--transition-fast) ease;
    transform-origin: center;
    will-change: transform, color, filter, background, padding;
    font-size: 1.25rem;
    background: transparent;
    padding: 0;
    border-radius: 8px;
  }

  /* Trigger hover/focus: scale only (color comes from selection/inheritance) */
  .context-switcher__trigger:hover i,
  .context-switcher__trigger:focus i {
    transform: scale(1.18);
    filter: saturate(1.6) drop-shadow(0 6px 14px rgba(99, 211, 255, 0.08));
  }

  /* Portal trimmed to trigger size; items are absolutely positioned so portal box stays tight */
  .context-switcher__portal {
    position: fixed;
    pointer-events: auto;
    z-index: 2147483647;
    padding: 0;
    display: inline-block;
    background: transparent;
    /* ensure the portal box matches the trigger height and stays tight around it */
    overflow: visible;
  }

  .context-switcher__inner {
    position: relative; /* parent for absolutely positioned items */
    display: inline-block;
    height: 100%;
    /* remove any padding/margins here so portal height is strictly the trigger height */
    padding: 0;
    margin: 0;
  }

  /* Items panel positioned to the right of the trigger, visually a floating panel.
     Important: fix height to match trigger so the panel doesn't grow vertically.
     Animate via scaleX from the trigger's left edge. */
  .context-switcher__items {
    position: absolute;
    left: 100%;
    top: 0; /* align to trigger top so height:100% lines up exactly */
    height: 100%; /* match trigger height exactly */
    transform: scaleX(0); /* collapsed state */
    transform-origin: left center;
    transition:
      transform var(--transition-medium) cubic-bezier(0.2, 0.9, 0.2, 1),
      opacity var(--transition-fast);
    opacity: 0;
    pointer-events: none;
    white-space: nowrap;
    /* visual styling for the items container (darkmode) */
    background: var(--cs-panel);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.4);
    border-radius: 8px;
    overflow: hidden;
    display: flex;
    align-items: center; /* vertically center icons within the fixed height */
  }

  /* inner wrapper provides horizontal padding and gap for buttons, no vertical padding */
  .context-switcher__items-inner {
    display: flex;
    gap: 6px;
    padding: 0 8px; /* horizontal padding only */
    align-items: center;
    height: 100%;
  }

  /* Buttons inside items - keep compact so items panel height == trigger height */
  .context-switcher__items button {
    /* make item backgrounds very subtle/translucent so panel feels lighter */
    background: rgba(255, 255, 255, 0.01);
    border: none;
    padding: 6px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    transition:
      background var(--transition-fast),
      transform var(--transition-fast);
    height: calc(
      100% - 12px
    ); /* slightly reduce so gap remains; centers icons nicely */
    align-self: center;
  }

  /* Muted by default; keep icons muted until hover/focus */
  .context-switcher__items button i {
    color: var(--icon-muted-items);
    transform: scale(1);
  }

  /* General hover transform/filter for icons (scale + subtle glow). Specific colors are applied per-icon below. */
  .context-switcher__items button:hover i,
  .context-switcher__items button:focus i {
    transform: scale(1.18);
    filter: saturate(1.6) drop-shadow(0 6px 14px rgba(0, 0, 0, 0.06));
  }

  /* Light-up backgrounds for icons on hover/focus — per-icon translucent backgrounds */
  .context-switcher__items button:hover .bi-house,
  .context-switcher__items button:focus .bi-house,
  .context-switcher__items button.is-clicked .bi-house {
    background: var(--icon-home-bg);
    color: var(--icon-home);
    padding: 6px;
  }

  .context-switcher__items button:hover .bi-search,
  .context-switcher__items button:focus .bi-search,
  .context-switcher__items button.is-clicked .bi-search {
    background: var(--icon-search-bg);
    color: var(--icon-search);
    padding: 6px;
  }

  .context-switcher__items button:hover .bi-bell,
  .context-switcher__items button:focus .bi-bell,
  .context-switcher__items button.is-clicked .bi-bell {
    background: var(--icon-bell-bg);
    color: var(--icon-bell);
    padding: 6px;
  }

  .context-switcher__items button:hover .bi-person,
  .context-switcher__items button:focus .bi-person,
  .context-switcher__items button.is-clicked .bi-person {
    background: var(--icon-person-bg);
    color: var(--icon-person);
    padding: 6px;
  }

  .context-switcher__items button:hover .bi-gear,
  .context-switcher__items button:focus .bi-gear,
  .context-switcher__items button.is-clicked .bi-gear {
    background: var(--icon-gear-bg);
    color: var(--icon-gear);
    padding: 6px;
  }

  .context-switcher__items button:hover .bi-calendar,
  .context-switcher__items button:focus .bi-calendar,
  .context-switcher__items button.is-clicked .bi-calendar {
    background: var(--icon-calendar-bg);
    color: var(--icon-calendar);
    padding: 6px;
  }

  .context-switcher__items button:hover .bi-envelope,
  .context-switcher__items button:focus .bi-envelope,
  .context-switcher__items button.is-clicked .bi-envelope {
    background: var(--icon-envelope-bg);
    color: var(--icon-envelope);
    padding: 6px;
  }

  .context-switcher__items button:hover .bi-camera,
  .context-switcher__items button:focus .bi-camera,
  .context-switcher__items button.is-clicked .bi-camera {
    background: var(--icon-camera-bg);
    color: var(--icon-camera);
    padding: 6px;
  }

  .context-switcher__items button:hover .bi-chat,
  .context-switcher__items button:focus .bi-chat,
  .context-switcher__items button.is-clicked .bi-chat {
    background: var(--icon-chat-bg);
    color: var(--icon-chat);
    padding: 6px;
  }

  .context-switcher__items button:hover .bi-cloud,
  .context-switcher__items button:focus .bi-cloud,
  .context-switcher__items button.is-clicked .bi-cloud {
    background: var(--icon-cloud-bg);
    color: var(--icon-cloud);
    padding: 6px;
  }

  /* Click animation for the selected item (now more pronounced / attention-grabbing) */
  .context-switcher__items button.is-clicked i {
    animation: cs-click 1s cubic-bezier(0.2, 0.9, 0.3, 1) forwards;
  }

  /* subtle pulse/glow on the button itself during the animation */
  .context-switcher__items button.is-clicked {
    animation: cs-pulse 1s cubic-bezier(0.2, 0.9, 0.3, 1) forwards;
  }

  @keyframes cs-click {
    0% {
      transform: scale(1) rotate(0);
      filter: saturate(1) drop-shadow(0 0 0 rgba(0, 0, 0, 0));
      opacity: 1;
    }
    25% {
      transform: scale(1.6) rotate(-10deg);
      filter: saturate(2) drop-shadow(0 18px 40px rgba(99, 211, 255, 0.2));
      opacity: 1;
    }
    55% {
      transform: scale(0.86) rotate(6deg);
      filter: saturate(1.5) drop-shadow(0 10px 26px rgba(99, 211, 255, 0.14));
    }
    85% {
      transform: scale(1.12) rotate(-2deg);
      filter: saturate(1.3) drop-shadow(0 8px 20px rgba(99, 211, 255, 0.1));
    }
    100% {
      transform: scale(1.02) rotate(0);
      filter: saturate(1.15) drop-shadow(0 6px 14px rgba(99, 211, 255, 0.06));
    }
  }

  @keyframes cs-pulse {
    0% {
      box-shadow: 0 0 0 rgba(99, 211, 255, 0);
      transform: scale(1);
      background: rgba(255, 255, 255, 0.01);
    }
    30% {
      box-shadow: 0 22px 54px rgba(99, 211, 255, 0.2);
      transform: scale(1.06);
      background: rgba(99, 211, 255, 0.035);
    }
    60% {
      box-shadow: 0 12px 32px rgba(99, 211, 255, 0.12);
      transform: scale(1.03);
      background: rgba(99, 211, 255, 0.02);
    }
    100% {
      box-shadow: 0 6px 18px rgba(99, 211, 255, 0.06);
      transform: scale(1);
      background: rgba(255, 255, 255, 0.01);
    }
  }

  /* When expanded, scaleX to full width and enable interactions */
  .context-switcher__items.is-expanded {
    transform: scaleX(1);
    opacity: 1;
    pointer-events: auto;
  }

  /* ensure the trigger remains on top of the items panel edge */
  .context-switcher__inner > .context-switcher__trigger {
    position: relative;
    z-index: 2;
  }
</style>
