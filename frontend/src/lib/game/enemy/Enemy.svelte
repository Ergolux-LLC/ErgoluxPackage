<script lang="ts">
  import { onMount, createEventDispatcher } from "svelte";
  import { enemyHP, ENEMY_MAX_HP, HIT_DAMAGE } from "./stats";

  const dispatch = createEventDispatcher();

  let wrapEl: HTMLDivElement | null = null;
  let imgEl: HTMLImageElement | null = null;

  // offscreen buffer
  let _canvas: HTMLCanvasElement | null = null;
  let _imageData: Uint8ClampedArray | null = null;
  let _naturalW = 0;
  let _naturalH = 0;

  // Expose helper methods via component instance
  export function isPointOpaque(viewportX: number, viewportY: number) {
    if (!imgEl || !_imageData || _naturalW <= 0 || _naturalH <= 0) return false;
    try {
      const rect = imgEl.getBoundingClientRect();
      if (viewportX < rect.left || viewportX >= rect.right) return false;
      if (viewportY < rect.top || viewportY >= rect.bottom) return false;
      const localX = viewportX - rect.left;
      const localY = viewportY - rect.top;
      const dispW = rect.width;
      const dispH = rect.height;
      let px = Math.floor((localX * _naturalW) / dispW);
      let py = Math.floor((localY * _naturalH) / dispH);
      // account for 180deg rotation (same as in page)
      px = _naturalW - 1 - px;
      py = _naturalH - 1 - py;
      if (px < 0 || py < 0 || px >= _naturalW || py >= _naturalH) return false;
      const idx = (py * _naturalW + px) * 4 + 3;
      return (_imageData[idx] || 0) > 16;
    } catch (e) {
      return false;
    }
  }

  // Expose a method to hide/show
  export function hide() {
    try {
      if (!wrapEl) return;
      // if a preventHide flag is set, honor it and ignore hide requests
      if (wrapEl.dataset && wrapEl.dataset.preventHide === "1") return;
      wrapEl.style.display = "none";
    } catch (e) {}
  }

  // Allow external controllers to temporarily prevent the component from being hidden
  export function preventHide(flag: boolean) {
    try {
      if (!wrapEl) return;
      if (flag) wrapEl.dataset.preventHide = "1";
      else delete wrapEl.dataset.preventHide;
    } catch (e) {}
  }

  export function show() {
    if (wrapEl) wrapEl.style.display = "";
  }

  // Expose geometry and transform helpers for external behavior
  export function getRect(): DOMRect | null {
    try {
      if (!imgEl) return null;
      return imgEl.getBoundingClientRect();
    } catch (e) {
      return null;
    }
  }

  export function setTransform(xOffset: number, yOffset: number) {
    try {
      if (wrapEl) {
        // keep legacy transform API (offset from centered 50%) for compatibility
        wrapEl.style.transform = `translateX(calc(-50% + ${xOffset}px)) translateY(${yOffset}px)`;
      }
    } catch (e) {}
  }

  // New API: set absolute center X in pixels and Y position in pixels.
  // This allows behavior to place the enemy so it won't clip off the viewport edges.
  export function setPosition(centerX: number, yOffset: number) {
    try {
      if (wrapEl) {
        // position the element so its center aligns to centerX using translateX(-50%)
        wrapEl.style.left = `${Math.round(centerX)}px`;
        wrapEl.style.top = `${Math.round(yOffset)}px`;
        wrapEl.style.transform = `translateX(-50%)`;
      }
    } catch (e) {}
  }

  // Prepare offscreen buffer once image is loaded
  function prepareBuffer() {
    if (!imgEl) return;
    try {
      _naturalW = imgEl.naturalWidth || imgEl.width || 0;
      _naturalH = imgEl.naturalHeight || imgEl.height || 0;
      if (_naturalW > 0 && _naturalH > 0) {
        _canvas = document.createElement("canvas");
        _canvas.width = _naturalW;
        _canvas.height = _naturalH;
        const ctx = _canvas.getContext("2d");
        if (ctx) {
          ctx.clearRect(0, 0, _naturalW, _naturalH);
          ctx.drawImage(imgEl, 0, 0, _naturalW, _naturalH);
          const id = ctx.getImageData(0, 0, _naturalW, _naturalH);
          _imageData = id.data;
        }
      }
    } catch (e) {
      // ignore buffer errors
    }
  }

  onMount(() => {
    if (imgEl) {
      if (imgEl.complete) prepareBuffer();
      else imgEl.addEventListener("load", prepareBuffer, { once: true });
    }
  });

  // expose refs for behavior module
  export { wrapEl, imgEl };
</script>

<div class="badguy-wrap" bind:this={wrapEl} aria-hidden="true">
  <img
    src="/images/badguy.png"
    alt="badguy"
    class="badguy-img"
    bind:this={imgEl}
  />
</div>

<style>
  .badguy-wrap {
    position: fixed;
    left: 50%;
    top: 2vh;
    transform: translateX(-50%);
    z-index: 3;
    pointer-events: none;
    display: flex;
    justify-content: center;
    align-items: flex-start;
  }
  .badguy-img {
    display: block;
    width: 300px !important;
    height: auto !important;
    max-width: none !important;
    max-height: none !important;
    image-rendering: pixelated;
    transform: rotate(180deg);
  }
</style>
