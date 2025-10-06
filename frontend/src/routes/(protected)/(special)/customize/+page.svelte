<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { GridStack } from "gridstack";
  import type { GridStackOptions } from "gridstack";
  import "gridstack/dist/gridstack.min.css";

  let gsContainer: HTMLElement | null = null;
  let grid: GridStack | null = null;

  type Part = { type: string; label: string; cls: string };
  const parts: Part[] = [
    { type: "hero", label: "Hero Container", cls: "bg-light p-4" },
    { type: "card", label: "Card", cls: "bg-white p-3 border" },
    { type: "full", label: "Full-width", cls: "bg-primary text-white p-4" },
  ];

  function handleDragStart(e: DragEvent, p: Part) {
    e.dataTransfer?.setData("application/json", JSON.stringify(p));
    e.dataTransfer!.effectAllowed = "copy";
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault();
    e.dataTransfer!.dropEffect = "copy";
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    const raw = e.dataTransfer?.getData("application/json");
    if (!raw) return;
    const p: Part = JSON.parse(raw);
    const el = document.createElement("div");
    el.className = "grid-stack-item";
    el.innerHTML = `<div class="grid-stack-item-content ${p.cls}">${p.label}</div>`;
    // add default size; GridStack will place at drop position
    grid?.addWidget(el, { w: 4, h: 1 });
  }

  function exportLayout() {
    if (!grid) return;
    const layout = grid.save(); // GridStackWidget[] with x,y,w,h
    // Attach per-widget content/classes
    const widgets = Array.from(
      document.querySelectorAll(".grid-stack-item"),
    ).map((n) => {
      const content = n.querySelector(
        ".grid-stack-item-content",
      ) as HTMLElement | null;
      return {
        x: parseInt(n.getAttribute("gs-x") ?? "0"),
        y: parseInt(n.getAttribute("gs-y") ?? "0"),
        w: parseInt(n.getAttribute("gs-w") ?? "0"),
        h: parseInt(n.getAttribute("gs-h") ?? "0"),
        html: content?.outerHTML ?? "",
        classes: content?.className ?? "",
      };
    });
    const payload = { layout, widgets };
    // TODO: POST payload to your SvelteKit endpoint
    console.log("export", payload);
  }

  onMount(() => {
    const opts: GridStackOptions = {
      float: false,
      cellHeight: "auto",
      disableOneColumnMode: true,
      acceptWidgets: true,
      resizable: { handles: "se, sw, ne, nw" },
      removable: true,
    };
    grid = GridStack.init(opts, gsContainer!);
  });

  onDestroy(() => {
    if (grid) {
      grid.destroy(false);
      grid = null;
    }
  });
</script>

```svelte
<div class="editor">
  <aside class="palette">
    <h4>Palette</h4>
    {#each parts as p}
      <div
        class="palette-item"
        draggable="true"
        role="button"
        tabindex="0"
        on:dragstart={(e) => handleDragStart(e as DragEvent, p)}
      >
        {p.label}
      </div>
    {/each}
    <button on:click={exportLayout}>Save Template (console)</button>
  </aside>

  <main>
    <div
      bind:this={gsContainer}
      class="grid-stack"
      style="min-height:400px"
      role="region"
      on:drop={handleDrop}
      on:dragover={handleDragOver}
    >
      <!-- Dummy element to ensure Svelte sees .grid-stack-item-content as used -->
      <div class="grid-stack-item-content" style="display:none"></div>
    </div>
  </main>
</div>
```

<style>
  .editor {
    display: grid;
    grid-template-columns: 240px 1fr;
    gap: 1rem;
    height: calc(100vh - 120px);
    padding: 1rem;
  }
  .palette {
    border-right: 1px solid #eaeaea;
    padding-right: 1rem;
  }
  .palette-item {
    cursor: grab;
    user-select: none;
    margin-bottom: 0.5rem;
    padding: 0.5rem;
    border: 1px dashed #bbb;
    background: #fff;
  }
  .grid-stack-item-content {
    height: 100%;
    box-sizing: border-box;
  }
</style>
