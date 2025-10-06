<script lang="ts">
  import { message } from "$lib/components/testcomponent/test.js";
  import { message as message2 } from "$lib/components/testcomponent2/test.js";
  import { onMount, onDestroy } from "svelte";
  import "gridstack/dist/gridstack.min.css";
  import type { GridStack as GridStackType } from "gridstack";

  type GridStackOptions = {
    column?: number;
    float?: boolean;
    cellHeight?: number | string;
    margin?: number;
    animate?: boolean;
    draggable?: any;
    resizable?: any;
    [key: string]: unknown;
  };

  let gridEl: HTMLElement | null = null;
  let grid: GridStackType | null = null;
  let editMode = false;

  // status/verification state for saving
  let saveStatus: "idle" | "saving" | "saved" | "error" = "idle";
  let lastSaved: string | null = null;
  let verified: boolean | null = null;
  let savedPreview: string | null = null;

  function toggleEdit() {
    editMode = !editMode;
    if (!grid) return;
    try {
      if (typeof (grid as any).enableMove === "function")
        (grid as any).enableMove(editMode);
      if (typeof (grid as any).enableResize === "function")
        (grid as any).enableResize(editMode);
      if (typeof (grid as any).setStatic === "function")
        (grid as any).setStatic(!editMode);
    } catch (e) {
      console.error("toggleEdit error:", e);
    }
  }

  let lastGreet = "";
  function handleGreet(event: CustomEvent<{ name: string }>) {
    const n = event.detail.name;
    lastGreet = `Greeted ${n} at ${new Date().toLocaleTimeString()}`;
  }

  onMount(() => {
    let mounted = true;
    (async () => {
      const gs = await import("gridstack");
      const GridStack = (gs as any).GridStack ?? (gs as any).default ?? gs;

      const options: GridStackOptions = {
        column: 12,
        float: false,
        cellHeight: 80,
        margin: 8,
        animate: true,
      };

      if (!mounted) return;
      grid = GridStack.init(options, gridEl!);

      // V11+ renderCB: use componentKey to inject live component output (do NOT rely on saved content)
      // Must set on the GridStack class so v11 calls it when creating widget divs
      (GridStack as any).renderCB = (el: HTMLElement, w: any) => {
        while (el.firstChild) el.removeChild(el.firstChild);

        const content = document.createElement("div");
        content.className = "grid-stack-item-content";

        // Prefer dynamic component rendering by componentKey
        if (w && w.componentKey === "testcomponent") {
          content.innerHTML = message;
        } else if (w && w.componentKey === "testcomponent2") {
          content.innerHTML = message2;
        } else {
          // fallback: use contentText or content if present (but we do NOT persist content)
          const payload = w && (w.contentText ?? w.content ?? "");
          if (typeof payload === "string" && /<[a-z][\s\S]*>/i.test(payload)) {
            content.innerHTML = payload;
          } else {
            content.textContent = payload ?? "";
          }
        }

        el.appendChild(content);
      };

      // --- load saved layout if present, otherwise add defaults ---
      const raw = localStorage.getItem("grid-layout");
      if (raw) {
        try {
          const layout = JSON.parse(raw);
          if (typeof (grid as any).removeAll === "function")
            (grid as any).removeAll();
          // load expects widget objects; our saved layout contains only layout metadata + componentKey
          if (typeof (grid as any).load === "function") {
            (grid as any).load(layout);
            return;
          } else {
            // fallback: add each widget object via addWidget (v11 expects widget objects)
            (layout as any[]).forEach((w: any) => {
              if (typeof (grid as any).addWidget === "function")
                (grid as any).addWidget(w);
            });
            return;
          }
        } catch (e) {
          console.error("failed to load saved grid layout", e);
          // fall through to add defaults
        }
      }

      // no saved layout -> add defaults (use componentKey, do NOT include actual content)
      const widget1 = {
        w: 3,
        h: 1,
        componentKey: "testcomponent",
        id: "item-1",
      };
      const widget2 = {
        w: 3,
        h: 1,
        componentKey: "testcomponent2",
        id: "item-2",
      };

      (grid as any).addWidget(widget1);
      (grid as any).addWidget(widget2);
      // --- end load/add defaults ---
    })();

    return () => {
      mounted = false;
    };
  });

  onDestroy(() => {
    if (grid) {
      try {
        grid.destroy(true);
      } catch (e) {
        /* ignore */
      }
      grid = null;
    }
  });

  // ---- Save / Load with verification ----
  async function saveLayout() {
    if (!grid) return;
    saveStatus = "saving";
    verified = null;
    try {
      // get full layout from GridStack
      const fullLayout = (grid as any).save();

      // strip any runtime content before persisting — keep only positional metadata + componentKey + id
      const stripped = (fullLayout as any[]).map((w: any) => ({
        id: w.id ?? (w.el && w.el.dataset && w.el.dataset.id) ?? undefined,
        x: w.x,
        y: w.y,
        w: w.w,
        h: w.h,
        componentKey: w.componentKey ?? w.contentKey ?? undefined,
      }));

      const json = JSON.stringify(stripped);
      localStorage.setItem("grid-layout", json);

      // verification: read back and compare normalized JSON
      const readRaw = localStorage.getItem("grid-layout");
      if (readRaw == null) {
        saveStatus = "error";
        verified = false;
        savedPreview = null;
        return;
      }

      const parsedRead = JSON.parse(readRaw);
      const same =
        JSON.stringify(parsedRead) === JSON.stringify(JSON.parse(json));

      if (same) {
        saveStatus = "saved";
        verified = true;
        lastSaved = new Date().toLocaleString();
        savedPreview =
          JSON.stringify(parsedRead, null, 2).slice(0, 200) +
          (json.length > 200 ? "…" : "");
      } else {
        saveStatus = "error";
        verified = false;
        savedPreview = JSON.stringify(parsedRead, null, 2).slice(0, 200);
      }
    } catch (e) {
      console.error("saveLayout error:", e);
      saveStatus = "error";
      verified = false;
      savedPreview = null;
    } finally {
      setTimeout(() => {
        if (saveStatus === "saved" || saveStatus === "error")
          saveStatus = "idle";
      }, 3000);
    }
  }

  function loadLayout() {
    if (!grid) return;
    const raw = localStorage.getItem("grid-layout");
    if (!raw) return;
    try {
      const layout = JSON.parse(raw);
      if (typeof (grid as any).removeAll === "function")
        (grid as any).removeAll();
      // load the metadata-only layout; renderCB will inject live testcomponent output
      if (typeof (grid as any).load === "function") {
        (grid as any).load(layout);
      } else {
        (layout as any[]).forEach((w: any) => {
          if (typeof (grid as any).addWidget === "function")
            (grid as any).addWidget(w);
        });
      }
      lastSaved = new Date().toLocaleTimeString();
    } catch (e) {
      console.error("loadLayout error:", e);
    }
  }
  // ---- end save/load ----
</script>

<!-- control -->
<div style="margin-bottom:8px;">
  <button on:click={toggleEdit}>
    {#if editMode}
      Switch to View
    {:else}
      Switch to Edit
    {/if}
  </button>

  <button on:click={saveLayout} disabled={saveStatus === "saving"}>
    {#if saveStatus === "saving"}Saving...{:else}Save Layout{/if}
  </button>

  <button on:click={loadLayout}>Load Layout</button>

  <!-- verification / confirmation UI -->
  <div style="display:inline-block; margin-left:12px; vertical-align:middle;">
    {#if saveStatus === "saved" && verified}
      <span style="color:green; font-weight:600;"
        >✓ Layout saved & verified</span
      >
      <div style="font-size:0.9em; color:#444;">Last saved: {lastSaved}</div>
    {:else if saveStatus === "error"}
      <span style="color:red; font-weight:600;"
        >✖ Save failed or verification mismatch</span
      >
    {:else if saveStatus === "saving"}
      <span style="color:#666;">Saving…</span>
    {:else if savedPreview}
      <div style="font-size:0.9em; color:#666;">
        Last saved preview: <pre
          style="display:inline-block; max-width:420px; white-space:pre-wrap;">{savedPreview}</pre>
      </div>
    {/if}
  </div>
</div>

<div class="grid-stack" bind:this={gridEl}></div>

<style>
  .grid-stack {
    background: #fafad2;
    min-height: 200px;
  }
  :global(.grid-stack-item-content) {
    background-color: #18bc9c;
    color: white;
    padding: 8px;
    border-radius: 4px;
  }
  :global(.grid-stack-item) {
    overflow: hidden;
  }
  :global(.grid-stack-item-content) {
    height: 100%;
    box-sizing: border-box;
  }
</style>
