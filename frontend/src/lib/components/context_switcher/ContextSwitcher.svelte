<script lang="ts">
  import { onMount, tick } from "svelte";
  import { goto } from "$app/navigation";
  import { ContextSwitcherTile } from "../context_switcher_tile";
  import APPS from "./apps";

  // Portal action: attach node to document.body so it's rendered above all content
  function portal(node: HTMLElement) {
    document.body.appendChild(node);
    return {
      destroy() {
        if (node.parentNode) node.parentNode.removeChild(node);
      },
    };
  }

  // Minimal portal state: style positioning + element refs
  let anchorEl: HTMLElement | null = null; // invisible placeholder in document flow
  let portalEl: HTMLDivElement | null = null; // actual portal node
  let portalContainerEl: HTMLElement | null = null; // container inside portal that holds trigger+menu
  let triggerVisibleEl: HTMLElement | null = null;
  let menuWrapperEl: HTMLElement | null = null;
  let portalStyle = "";
  let selectedId: string | null = null;
  // show/hide the visible trigger inside the portal after a selection
  let showTrigger = true;
  // menu open/closed state (start open on page load, can still be toggled/closed)
  let menuOpen = true;

  // logging flag
  const LOG = true;
  function log(...args: any[]) {
    if (LOG) console.debug("[ContextSwitcher]", ...args);
  }

  // minimal active app state so template references exist
  const ACTIVE_ID = "create";
  // make activeApp mutable so we can swap it with a clicked menu item
  let activeApp: NormalizedApp = {
    id: ACTIVE_ID,
    name: "Create",
    icon: "bi-plus-circle",
    color: "#7bd389",
    triggerBg: "#4FA763",
    path: "/create",
  };
  $: activeIcon = activeApp.icon;
  $: activeColor = activeApp.color ?? "#7bd389";

  // measure anchor once (after first client render) and bind portal to that fixed position
  const PORTAL_OFFSET_Y = 0; // move portal down 12px from anchor
  function setPortalPositionOnce() {
    if (!anchorEl) {
      log("anchorEl missing; skipping one-time portal positioning");
      return;
    }
    const rect = anchorEl.getBoundingClientRect();
    log("one-time measured anchor rect:", rect);
    const top = Math.round(rect.top + window.scrollY + PORTAL_OFFSET_Y);
    const left = Math.round(rect.left + window.scrollX);
    portalStyle = `top: ${top}px; left: ${left}px; z-index:2147483647;`;
    log("one-time portalStyle ->", portalStyle);
  }

  // On mount: set portal position once after the first paint. Do not add listeners.
  onMount(async () => {
    log("mounted (one-time bind)");
    await tick(); // ensure DOM/layout has settled
    setPortalPositionOnce();
  });

  type NormalizedApp = {
    id: string;
    name: string;
    icon?: string;
    color?: string;
    path?: string;
    triggerBg?: string;
  };
  let appsList: NormalizedApp[] = [];

  function normalizeApps(raw: any): NormalizedApp[] {
    if (Array.isArray(raw)) {
      return raw.map((a: any) => ({
        id: a.id ?? String(a.name ?? a),
        name: a.name ?? a.title ?? String(a.id ?? a),
        icon: a.icon ?? a.iconClass,
        color: a.color ?? a.colorVar,
        triggerBg: a.triggerBg,
        path: a.path ?? a.route,
      }));
    }
    if (raw && typeof raw === "object") {
      // keyed object: { create: { name: 'Create', icon: 'bi-plus', ... }, ... }
      return Object.entries(raw).map(([key, val]: any) => {
        if (typeof val === "string") {
          return { id: key, name: val };
        }
        return {
          id: val?.id ?? key,
          name: val?.name ?? val?.title ?? key,
          icon: val?.icon ?? val?.iconClass,
          color: val?.color ?? val?.colorVar,
          triggerBg: val?.triggerBg,
          path: val?.path ?? val?.route,
        };
      });
    }
    return [];
  }

  // normalize at module init so markup can iterate reliably
  appsList = normalizeApps(APPS);

  function findAppById(id: string): NormalizedApp | undefined {
    return appsList.find((a) => a.id === id);
  }

  function swapWithTrigger(selectedId: string) {
    const selected = findAppById(selectedId);
    if (!selected) return;
    // We will copy the selected app data into activeApp and also replace the app in appsList with the previous activeApp
    const prevActive = { ...activeApp } as NormalizedApp;
    // find index of selected in appsList
    const idx = appsList.findIndex((a) => a.id === selectedId);
    if (idx >= 0) {
      // put previous active in the list at the selected index
      appsList[idx] = {
        id: prevActive.id,
        name: prevActive.name,
        icon: prevActive.icon,
        color: prevActive.color,
        triggerBg: prevActive.triggerBg,
        path: prevActive.path,
      };
      // reassign to trigger Svelte reactivity
      appsList = [...appsList];
    }
    // set activeApp to the selected app
    activeApp = {
      id: selected.id,
      name: selected.name,
      icon: selected.icon,
      color: selected.color,
      triggerBg: selected.triggerBg,
      path: selected.path,
    };
    // ensure the portal's trigger reflects the new activeApp
    activeIcon = activeApp.icon;
    activeColor = activeApp.color ?? activeColor;
  }

  // wait for a transition or animation to finish on an element (with timeout)
  function waitForTransition(
    el: HTMLElement | null,
    props: string[] = [],
    timeout = 1200,
  ) {
    return new Promise<void>((resolve) => {
      if (!el) return resolve();
      let done = false;
      const onEnd = (e: Event & { propertyName?: string }) => {
        // Accept animationend or matching transition property
        if ((e as AnimationEvent).animationName) return cleanup();
        if (
          !props.length ||
          (e && "propertyName" in e && props.includes((e as any).propertyName))
        )
          cleanup();
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

  // handler for actual app tile selection (menu items)
  async function handleSelect(event: CustomEvent) {
    const { id } = event.detail || {};
    if (!id) return;
    // swap the selected menu item with the trigger so the trigger shows the selected app
    swapWithTrigger(id);
    selectedId = id;
    // start closing animation (menu stays in DOM so we can animate)
    menuOpen = false;
    log("selection received -> animate menu closing for", id);
    // allow DOM to update so the closing class/transitions apply
    await tick();
    // wait for the menu-panel to finish its collapse animation
    const panel = menuWrapperEl?.querySelector(
      ".menu-panel",
    ) as HTMLElement | null;
    if (panel) {
      await waitForTransition(
        panel,
        ["max-height", "opacity", "transform"],
        1400,
      );
      log("menu close animation finished");
    } else {
      // fallback small delay if panel not found
      await new Promise((r) => setTimeout(r, 300));
    }

    // extra visual pause before navigating (one second)
    await new Promise((r) => setTimeout(r, 1000));

    // now navigate
    try {
      const app = appsList.find((a) => a.id === id);
      const target =
        app?.path ??
        (typeof id === "string" && id.startsWith("/") ? id : `/${id}`);
      await goto(target);
    } catch (err) {
      console.debug("[ContextSwitcher] navigation error", err);
    }
  }

  // handler for clicking the trigger tile: toggle the menu
  async function handleTriggerSelect() {
    if (!showTrigger) return;
    menuOpen = !menuOpen;
    log("toggled menuOpen ->", menuOpen);
    await tick(); // keep DOM stable, but do NOT re-measure or move portal
  }
</script>

hi
<!-- container wraps the anchor placeholder (left) and the menu bar placeholder (right) -->
<div class="switcher-container" aria-hidden="false">
  <!-- invisible placeholder anchor in document flow: occupies exact space of trigger -->
  <div
    class="anchor-placeholder"
    bind:this={anchorEl}
    aria-hidden="true"
    style="display:inline-block; width:424px; height:80px;"
  >
    <!-- anchor now purely an empty placeholder; sizing is controlled via inline style -->
  </div>

  <!-- placeholder for menu bar layout (keeps layout flow) -->
  <div class="menu-flow-placeholder" aria-hidden="true">
    <!-- optional static spacing or preview in document flow if needed -->
  </div>
</div>

<!-- portal renders the visible trigger and the menu bar to its right -->
{#if anchorEl}
  <div
    use:portal
    bind:this={portalEl}
    class="context-switcher__portal"
    style={portalStyle}
  >
    <div class="portal-inner" role="presentation">
      <!-- container around trigger + menubar so alignment/positioning stays correct as content changes -->
      <div class="portal-container" bind:this={portalContainerEl}>
        <div class="portal-row">
          <!-- visible trigger (inside portal) - hidden after selection -->
          {#if showTrigger}
            <div
              class="trigger-visible"
              role="button"
              aria-label="Context switcher trigger"
              bind:this={triggerVisibleEl}
            >
              <!-- trigger toggles menuOpen instead of being treated as a menu selection -->
              <ContextSwitcherTile
                name={activeApp.name}
                id="switcher-trigger"
                icon={activeIcon}
                color={activeColor}
                triggerBg={activeApp.triggerBg}
                alwaysShowBg={true}
                disableClickAnimation={true}
                on:select={handleTriggerSelect}
              />
            </div>
          {/if}

          <!-- menu bar (to the right of trigger) - rendered but animated open/closed via class -->
          <div
            class="menu-wrapper"
            aria-label="context-switcher-tiles"
            bind:this={menuWrapperEl}
            aria-hidden={!menuOpen}
          >
            <div class="menu-panel {menuOpen ? 'open' : 'closed'}">
              <div
                style="padding:12px; background: rgba(28,30,33,0.88); border-radius: 10px;"
              >
                <div class="tiles-row" role="list">
                  {#each appsList as app}
                    <ContextSwitcherTile
                      name={app.name}
                      id={app.id}
                      icon={app.icon}
                      color={app.color ?? "#7bd389"}
                      triggerBg={app.triggerBg}
                      on:select={handleSelect}
                    />
                  {/each}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  :global(.context-switcher__portal) {
    position: fixed;
    display: block;
    z-index: 2147483647;
    pointer-events: auto;
  }
  /* panel open/close animation (collapse) */
  .menu-panel {
    max-height: 0;
    opacity: 0;
    transform: translateY(-6px);
    overflow: hidden;
    transition:
      max-height 420ms cubic-bezier(0.2, 0.9, 0.26, 1),
      opacity 220ms ease,
      transform 320ms ease;
  }
  .menu-panel.open {
    /* large enough to contain the tiles row; if row grows, bump this value */
    max-height: 520px;
    opacity: 1;
    transform: translateY(0);
  }
  /* container that holds the anchor placeholder and flow placeholder */
  .switcher-container {
    display: inline-flex;
    /* allow children (anchor) to set the container height so the anchor can grow past 64px */
    align-items: stretch;
    gap: 12px;
  }

  /* anchor placeholder matches the trigger size by containing an invisible mirror */
  .anchor-placeholder {
    display: inline-block;
    line-height: 0;
    /* background-color: #d647a4; */
  }

  /* trigger-mirror removed — anchor is sized via inline style / constants */

  /* small container for portal content */
  .portal-inner {
    display: inline-block;
  }

  /* layout inside portal: trigger then menu to the right */
  .portal-row {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    padding: 0; /* removed 4px padding */
  }

  .trigger-visible {
    display: inline-block;
    line-height: 0;
    margin-top: 12px;
    margin-bottom: 12px;
  }

  .menu-wrapper {
    display: inline-flex; /* ensure wrapper sizes to its content */
    align-items: center;
  }

  /* make the immediate inner panel tight around the tile plates */
  .menu-wrapper > div {
    padding: 4px; /* minimal padding around the plates */
    background: rgba(28, 30, 33, 0.88);
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
  }

  .tiles-row {
    display: flex;
    gap: 4px; /* smaller gap so the plates sit closer together */
    align-items: center;
    flex-wrap: nowrap; /* keep a single row so width is tight */
    justify-content: flex-start;
  }
</style>
