<script lang="ts">
  import { message } from "$lib/components/testcomponent/test.js";
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
        draggable: { handle: ".grid-stack-item-content" },
        resizable: { handles: "se, sw" },
      };

      if (!mounted) return;
      grid = GridStack.init(options, gridEl!);

      try {
        if (typeof (grid as any).setStatic === "function")
          (grid as any).setStatic(!editMode);
        if (typeof (grid as any).enableMove === "function")
          (grid as any).enableMove(editMode);
        if (typeof (grid as any).enableResize === "function")
          (grid as any).enableResize(editMode);
      } catch (e) {
        /* ignore */
      }

      (grid as any).renderCB = (el: HTMLElement, w: any) => {
        while (el.firstChild) el.removeChild(el.firstChild);

        const payload = w && (w.content ?? w.contentText ?? "");

        const content = document.createElement("div");
        content.className = "grid-stack-item-content";

        if (payload instanceof Node) {
          content.appendChild(payload.cloneNode(true));
        } else if (typeof payload === "string") {
          if (/<[a-z][\s\S]*>/i.test(payload)) {
            content.innerHTML = payload;
          } else {
            content.textContent = payload;
          }
        } else {
          content.textContent = payload == null ? "" : String(payload);
        }

        el.appendChild(content);
      };

      // --- load saved layout if present, otherwise add defaults ---
      const raw = localStorage.getItem("grid-layout");
      if (raw) {
        try {
          const layout = JSON.parse(raw);
          // prefer load API
          if (typeof (grid as any).load === "function") {
            if (typeof (grid as any).removeAll === "function")
              (grid as any).removeAll();
            (grid as any).load(layout);
          } else {
            // fallback: iterate widgets (v11 expects widget objects)
            (layout as any[]).forEach((w: any) => {
              if (typeof (grid as any).addWidget === "function")
                (grid as any).addWidget(w);
            });
          }
          // layout restored — skip adding defaults
          return;
        } catch (e) {
          console.error("failed to load saved grid layout", e);
          // fall through to add defaults
        }
      }

      // no saved layout -> add defaults
      const widget1 = { w: 3, h: 1, content: message };
      const widget2 = { w: 3, h: 1, content: "another longer widget!" };

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
      // use modern API
      const layout = (grid as any).save();
      const json = JSON.stringify(layout);
      localStorage.setItem("grid-layout", json);

      // verification: read back and compare string forms
      const readRaw = localStorage.getItem("grid-layout");
      if (readRaw == null) {
        saveStatus = "error";
        verified = false;
        savedPreview = null;
        return;
      }

      // basic verification by comparing JSON normalized strings
      const parsedRead = JSON.parse(readRaw);
      const parsedOriginal = JSON.parse(json);
      const same =
        JSON.stringify(parsedRead) === JSON.stringify(parsedOriginal);

      if (same) {
        saveStatus = "saved";
        verified = true;
        lastSaved = new Date().toLocaleString();
        // small preview to display in UI (truncate to avoid huge content)
        savedPreview =
          JSON.stringify(parsedOriginal, null, 2).slice(0, 200) +
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
      // reset status indicator after a short delay so UI doesn't stay in "saved" forever
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
      (grid as any).removeAll();
      (grid as any).load(layout);
      // show quick confirmation
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
