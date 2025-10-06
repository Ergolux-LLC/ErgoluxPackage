<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { config } from "$lib/config/environment";

  let slowCanvasEl: HTMLCanvasElement | null = null;
  let fastCanvasEl: HTMLCanvasElement | null = null;
  let raf = 0;
  let running = true;

  // Visual tuning — smaller cell -> more stars. Smaller cell -> denser sky.
  const CELL_SIZE = 12; // pixels; jittered grid cell size (smaller -> more stars)
  // chance a cell contains a star (slow layer). Reduced by ~25% for fewer stars.
  const FILL_PROB = 0.3;
  // uniform speed for slow layer (px/sec)
  const GLOBAL_SPEED = 36;
  // fast layer tuning — fewer stars, much faster
  const FAST_CELL_SIZE = 28;
  const FAST_FILL_PROB = 0.12;
  const GLOBAL_SPEED_FAST = 220;
  const MAX_IMAGE_ENTRIES = 60;

  type Star = {
    x: number;
    y: number;
    size: number; // integer CSS pixels
    alphaSeed: number; // used for subtle alpha variation
  };

  let slowStars: Star[] = [];
  let fastStars: Star[] = [];
  // ship state
  let shipImgEl: HTMLImageElement | null = null;
  let shipWidth = 0;
  let shipHeight = 0;
  let shipX = 0; // left in px
  let shipBottom = 0; // base bottom offset in px
  let shipYOffset = 0; // (deprecated) kept for compatibility
  let shipTop = 0; // top in px
  const SHIP_SPEED = 560; // px/sec (doubled)
  const SHIP_VERT_RANGE = 60; // px up from base
  const LASER_SPEED = 900; // px/sec
  const LASER_WIDTH = 3; // px
  let keysPressed: { [k: string]: boolean } = {};
  let lastShot = 0;
  const SHOT_COOLDOWN = 80; // ms — reduced for higher fire rate
  let firing = false; // true while space is held
  type Laser = {
    el: HTMLDivElement;
    top: number;
    left: number;
    height: number;
  };
  let lasers: Laser[] = [];

  function seededRandom(seed: number) {
    let s = seed >>> 0;
    return function () {
      // xorshift32-ish
      s ^= s << 13;
      s ^= s >>> 17;
      s ^= s << 5;
      return (s >>> 0) / 4294967295;
    };
  }

  // we draw square pixel stars directly — no sprite cache needed for small rects

  function generateStars(
    width: number,
    height: number,
    dpr: number,
    cellSize: number,
    fillProb: number,
  ) {
    const list: Star[] = [];
    const cols = Math.ceil(width / cellSize);
    const rows = Math.ceil(height / cellSize);
    const seed = Math.floor(width * 31 + height * 17 + cellSize * 7);
    const rand = seededRandom(seed);
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        if (rand() > fillProb) continue;
        // jitter within cell
        const jitterX = (rand() - 0.5) * cellSize * 0.8;
        const jitterY = (rand() - 0.5) * cellSize * 0.8;
        const x = Math.min(
          width - 1,
          Math.max(0, c * cellSize + cellSize / 2 + jitterX),
        );
        const y = Math.min(
          height - 1,
          Math.max(0, r * cellSize + cellSize / 2 + jitterY),
        );
        // square pixel sizes in CSS pixels (1..3)
        const sizePx = 1 + Math.floor(rand() * 3);
        const alphaSeed = Math.floor(rand() * 100);
        list.push({ x, y, size: sizePx, alphaSeed });
      }
    }
    return list;
  }

  function drawLayer(
    now: number,
    lastTime: number,
    ctx: CanvasRenderingContext2D,
    width: number,
    height: number,
    dpr: number,
    list: Star[],
    speed: number,
  ) {
    const dt = Math.min(0.05, (now - lastTime) / 1000);
    // clear (in CSS pixels)
    ctx.clearRect(0, 0, width, height);
    // ensure crisp pixel rendering
    ctx.imageSmoothingEnabled = false;
    // draw stars; update y — uniform speed for whole layer
    for (let i = 0; i < list.length; i++) {
      const s = list[i];
      s.y += speed * dt;
      if (s.y > height) s.y -= height; // wrap to top preserving x
      const size = Math.max(1, Math.round(s.size));
      // compute integer-aligned coords for crisp squares
      const drawX = Math.round(s.x - size / 2);
      const drawY = Math.round(s.y - size / 2);
      // derive subtle alpha from seed
      const alpha = ((s.alphaSeed % 100) / 100) * 0.4 + 0.6; // 0.6..1.0
      ctx.fillStyle = `rgba(255,255,255,${alpha.toFixed(3)})`;
      ctx.fillRect(drawX, drawY, size, size);
    }
  }

  let lastTime = performance.now();

  function startAnimation() {
    const slow = slowCanvasEl;
    const fast = fastCanvasEl;
    if (!slow && !fast) return;
    const ctxSlow = slow?.getContext("2d");
    const ctxFast = fast?.getContext("2d");
    if (!ctxSlow && !ctxFast) return;
    running = true;
    lastTime = performance.now();
    const dpr = Math.max(1, window.devicePixelRatio || 1);
    const slowC = slow as HTMLCanvasElement | null;
    const fastC = fast as HTMLCanvasElement | null;

    function frame(now: number) {
      if (!running) return;
      const dt = Math.min(0.05, (now - lastTime) / 1000);
      // update ship movement
      if (document.hasFocus()) {
        const vw = Math.max(
          document.documentElement.clientWidth,
          window.innerWidth || 0,
        );
        const vh = Math.max(
          document.documentElement.clientHeight,
          window.innerHeight || 0,
        );
        let dx = 0;
        let dy = 0;
        if (keysPressed["ArrowLeft"] || keysPressed["Left"]) dx -= 1;
        if (keysPressed["ArrowRight"] || keysPressed["Right"]) dx += 1;
        // conventional mapping: up decreases top, down increases top
        if (keysPressed["ArrowUp"] || keysPressed["Up"]) dy -= 1;
        if (keysPressed["ArrowDown"] || keysPressed["Down"]) dy += 1;
        shipX = shipX + dx * SHIP_SPEED * dt;
        shipTop = shipTop + dy * SHIP_SPEED * dt;
        // keep ship within viewport bounds (allow full-travel across viewport)
        shipX = Math.max(0, Math.min(vw - shipWidth, shipX));
        shipTop = Math.max(0, Math.min(vh - shipHeight, shipTop));
        // apply position to wrapper (disable the CSS centering transform and use absolute px)
        if (shipUseAbsolutePosition && shipWrapEl) {
          shipWrapEl.style.transform = "none";
          shipWrapEl.style.left = `${Math.round(shipX)}px`;
          shipWrapEl.style.top = `${Math.round(shipTop)}px`;
          // override stylesheet bottom so top takes precedence
          shipWrapEl.style.bottom = "auto";
        }
      }

      if (ctxSlow && slowC)
        drawLayer(
          now,
          lastTime,
          ctxSlow,
          slowC.width / dpr,
          slowC.height / dpr,
          dpr,
          slowStars,
          GLOBAL_SPEED,
        );
      if (ctxFast && fastC)
        drawLayer(
          now,
          lastTime,
          ctxFast,
          fastC.width / dpr,
          fastC.height / dpr,
          dpr,
          fastStars,
          GLOBAL_SPEED_FAST,
        );

      // update lasers
      for (let i = lasers.length - 1; i >= 0; i--) {
        const L = lasers[i];
        L.top -= LASER_SPEED * dt;
        // remove when fully off-screen (top + height < 0)
        if (L.top + (L.height || 0) < 0) {
          L.el.remove();
          lasers.splice(i, 1);
        } else {
          L.el.style.top = `${L.top}px`;
          // pixel-perfect collision with badguy (fast path: bounding box, then sample alpha)
          try {
            // fast AABB check against the enemy's bounding box, then use Enemy.isPointOpaque for pixel test
            if (enemyComp && typeof enemyComp.isPointOpaque === "function") {
              // approximate enemy rect by querying its DOM node via the component
              // We'll sample a grid inside the overlap and call isPointOpaque
              const laserLeft = L.left;
              const laserRight = L.left + (L.el.offsetWidth || LASER_WIDTH);
              const laserTop = L.top;
              const laserBottom = L.top + (L.height || 0);
              // sample step and bounding area — use a modest step to balance cost
              const step = 6;
              let found = false;
              let foundX = 0;
              let foundY = 0;
              for (let sx = laserLeft; sx <= laserRight && !found; sx += step) {
                for (
                  let sy = laserTop;
                  sy <= laserBottom && !found;
                  sy += step
                ) {
                  try {
                    if (
                      enemyComp.isPointOpaque(Math.round(sx), Math.round(sy))
                    ) {
                      found = true;
                      foundX = sx;
                      foundY = sy;
                      break;
                    }
                  } catch (e) {
                    // ignore per-point errors
                  }
                }
              }
              if (found) {
                const m = document.createElement("div");
                m.className = "hit-marker";
                m.style.position = "fixed";
                m.style.left = `${Math.round(foundX - 8)}px`;
                m.style.top = `${Math.round(foundY - 8)}px`;
                m.style.width = "18px";
                m.style.height = "18px";
                m.style.borderRadius = "50%";
                m.style.pointerEvents = "none";
                m.style.zIndex = "6";
                m.style.background =
                  "radial-gradient(circle, rgba(255,255,255,1) 0%, rgba(255,200,50,0.9) 30%, rgba(255,40,40,0.8) 60%, rgba(255,0,0,0.0) 100%)";
                m.style.transform = "scale(0.6)";
                m.style.transition =
                  "transform 220ms ease-out, opacity 220ms ease-out";
                document.body.appendChild(m);
                requestAnimationFrame(() => {
                  m.style.transform = "scale(1.4)";
                  m.style.opacity = "0";
                });
                setTimeout(() => m.remove(), 320);
                // apply damage via store
                try {
                  enemyHPStore.damage(HIT_DAMAGE);
                } catch (e) {}
                // damage was applied to the store. Do not hide the enemy here —
                // the behavior module will run the full death sequence (explosions + final big explosion)
                // and will hide/consume the enemy when that completes.
                // consume laser
                L.el.remove();
                lasers.splice(i, 1);
              }
            }
          } catch (e) {
            // guard against any unexpected runtime errors in collision detection
          }
        }
      }

      // process firing at fixed intervals to keep timing consistent
      if (firing) {
        // allow multiple shots if the frame was delayed, but cap to avoid giant bursts
        const nowMs = performance.now();
        let shots = 0;
        while (nowMs - lastShot >= SHOT_COOLDOWN && shots < 6) {
          shoot();
          lastShot += SHOT_COOLDOWN;
          shots++;
        }
      }

      lastTime = now;
      raf = requestAnimationFrame(frame);
    }
    raf = requestAnimationFrame(frame);
  }

  function stopAnimation() {
    running = false;
    if (raf) cancelAnimationFrame(raf);
  }

  import Enemy from "$lib/game/enemy/Enemy.svelte";
  import enemyHPStore, {
    ENEMY_MAX_HP,
    HIT_DAMAGE,
  } from "$lib/game/enemy/stats";
  import * as behavior from "$lib/game/enemy/behavior";
  import shipBuffer from "$lib/game/ship/shipBuffer";
  import { playerHP, PLAYER_MAX_HP } from "$lib/game/player/player";
  let shipWrapEl: HTMLDivElement | null = null;
  let shipUseAbsolutePosition = false;
  let playerHPWrapEl: HTMLDivElement | null = null;
  let _lowHealthAudio: HTMLAudioElement | null = null;
  function ensureLowHealthAudio() {
    if (_lowHealthAudio) return _lowHealthAudio;
    try {
      const a = new Audio("/sounds/low-health.mp3");
      a.preload = "auto";
      a.loop = true;
      _lowHealthAudio = a;
    } catch (e) {
      _lowHealthAudio = null;
    }
    return _lowHealthAudio;
  }

  // watch player HP and toggle low-health flashing/sound when <=20%
  $: {
    // reactive statement depends on $playerHP
    const pct = ($playerHP / PLAYER_MAX_HP) * 100;
    if (playerHPWrapEl) {
      if (pct <= 20) {
        playerHPWrapEl.classList.add("player-hp-low");
        try {
          const a = ensureLowHealthAudio();
          if (a) a.play().catch(() => {});
        } catch (e) {}
      } else {
        playerHPWrapEl.classList.remove("player-hp-low");
        try {
          const a = ensureLowHealthAudio();
          if (a) {
            a.pause();
            try {
              a.currentTime = 0;
            } catch (e) {}
          }
        } catch (e) {}
      }
    }
  }
  let enemyComp: any = null; // component ref for collision queries

  function handleKeyDown(e: KeyboardEvent) {
    keysPressed[e.key] = true;
    // spacebar: enable firing state; set lastShot so we fire immediately on next frame
    if (e.code === "Space") {
      if (!firing) {
        firing = true;
        lastShot = performance.now() - SHOT_COOLDOWN; // allow immediate shot in RAF
      }
      e.preventDefault();
    }
  }

  function handleKeyUp(e: KeyboardEvent) {
    keysPressed[e.key] = false;
    if (e.code === "Space") firing = false;
  }

  function shoot() {
    if (!shipImgEl || !shipWrapEl) return;
    const rect = shipImgEl.getBoundingClientRect();
    const laser = document.createElement("div");
    laser.style.position = "fixed";
    laser.style.width = `${LASER_WIDTH}px`;
    // make lasers shorter and prominent red
    const laserH = Math.max(28, Math.round(window.innerHeight * 0.06));
    laser.style.height = `${laserH}px`;
    const leftPx = Math.round(rect.left + rect.width / 2 - LASER_WIDTH / 2);
    laser.style.left = `${leftPx}px`;
    // start laser at ship top (rect.top is distance from viewport top)
    const initialTop = Math.round(rect.top - laserH);
    laser.style.top = `${initialTop}px`;
    laser.style.background = "linear-gradient(180deg,#ff6b6b,#ff1a1a)";
    laser.style.boxShadow = "0 0 6px rgba(255,30,30,0.9)";
    laser.style.pointerEvents = "none";
    laser.style.zIndex = "4";
    laser.style.borderRadius = "1px";
    laser.style.opacity = "0.98";
    document.body.appendChild(laser);
    const L: Laser = {
      el: laser as HTMLDivElement,
      top: initialTop,
      left: leftPx,
      height: laserH,
    };
    lasers.push(L);
    // play laser sound (non-blocking)
    try {
      playLaserSound();
    } catch (err) {
      // ignore audio errors
      // console.warn('laser sound failed', err);
    }
  }

  // Lightweight WebAudio synth for a short laser zap — no external asset required.
  let _audioCtx: AudioContext | null = null;
  let _laserArrayBuffer: ArrayBuffer | null = null;
  let _laserAudioBuffer: AudioBuffer | null = null;
  let _laserFetchInProgress = false;
  function ensureAudioContext() {
    if (_audioCtx) return _audioCtx;
    try {
      const Ctor =
        (window as any).AudioContext || (window as any).webkitAudioContext;
      if (!Ctor) return null;
      _audioCtx = new Ctor();
      return _audioCtx;
    } catch (e) {
      return null;
    }
  }

  function playLaserSound() {
    const ctx = ensureAudioContext();
    // If we have an external decoded buffer, play it
    if (ctx && _laserAudioBuffer) {
      const src = ctx.createBufferSource();
      src.buffer = _laserAudioBuffer;
      const g = ctx.createGain();
      g.gain.setValueAtTime(0.9, ctx.currentTime);
      src.connect(g);
      g.connect(ctx.destination);
      src.start();
      return;
    }

    // If we have fetched raw data but not decoded, try to decode it now and play once ready
    if (ctx && _laserArrayBuffer && !_laserAudioBuffer) {
      try {
        ctx.decodeAudioData(
          _laserArrayBuffer.slice(0),
          (buf) => {
            _laserAudioBuffer = buf;
            try {
              const src = ctx.createBufferSource();
              src.buffer = _laserAudioBuffer as AudioBuffer;
              src.connect(ctx.destination);
              src.start();
            } catch (e) {
              // ignore
            }
          },
          () => {
            // decode failed — fall through to synth
          },
        );
        return; // we'll decode/play asynchronously
      } catch (e) {
        // if decodeAudioData isn't available as promise, fall through to synth
      }
    }

    // no external buffer ready; fall back to the lightweight synth
    if (!ctx) return;
    const now = ctx.currentTime;
    // short noise + descending pitch tone
    const noiseBuf = ctx.createBuffer(1, ctx.sampleRate * 0.03, ctx.sampleRate);
    const data = noiseBuf.getChannelData(0);
    for (let i = 0; i < data.length; i++)
      data[i] = (Math.random() * 2 - 1) * (1 - i / data.length);
    const noise = ctx.createBufferSource();
    noise.buffer = noiseBuf;
    const noiseFilter = ctx.createBiquadFilter();
    noiseFilter.type = "highpass";
    noiseFilter.frequency.value = 800;
    const noiseGain = ctx.createGain();
    noiseGain.gain.setValueAtTime(0.6, now);
    noiseGain.gain.exponentialRampToValueAtTime(0.001, now + 0.06);
    noise.connect(noiseFilter);
    noiseFilter.connect(noiseGain);

    // descending tone
    const osc = ctx.createOscillator();
    osc.type = "sawtooth";
    osc.frequency.setValueAtTime(1200, now);
    osc.frequency.exponentialRampToValueAtTime(300, now + 0.12);
    const toneGain = ctx.createGain();
    toneGain.gain.setValueAtTime(0.001, now);
    toneGain.gain.exponentialRampToValueAtTime(0.5, now + 0.005);
    toneGain.gain.exponentialRampToValueAtTime(0.001, now + 0.14);

    // master
    const master = ctx.createGain();
    master.gain.setValueAtTime(0.8, now);
    master.gain.exponentialRampToValueAtTime(0.001, now + 0.18);

    noiseGain.connect(master);
    toneGain.connect(master);
    master.connect(ctx.destination);

    noise.start(now);
    noise.stop(now + 0.06);

    osc.connect(toneGain);
    osc.start(now);
    osc.stop(now + 0.14);
  }

  onMount(() => {
    // keyboard
    window.addEventListener("keydown", handleKeyDown, { passive: false });
    window.addEventListener("keyup", handleKeyUp);
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (mq.matches) {
      // do not animate if user prefers reduced motion; still render static stars
    }

    let resizeObserver: ResizeObserver | null = null;
    let visibilityHandler: () => void;

    function setup() {
      if (!slowCanvasEl && !fastCanvasEl) return;
      const dpr = Math.max(1, window.devicePixelRatio || 1);
      // compute viewport size
      const vw = Math.max(
        document.documentElement.clientWidth,
        window.innerWidth || 0,
      );
      const vh = Math.max(
        document.documentElement.clientHeight,
        window.innerHeight || 0,
      );

      // backing store size must be viewport * dpr for both canvases
      const slow = slowCanvasEl;
      const fast = fastCanvasEl;
      if (slow) {
        slow.width = Math.round(vw * dpr);
        slow.height = Math.round(vh * dpr);
        slow.style.position = "absolute";
        slow.style.left = "0";
        slow.style.top = "0";
        slow.style.width = "100%";
        slow.style.height = "100%";
        const ctxSlow = slow.getContext("2d");
        if (ctxSlow) {
          ctxSlow.setTransform(1, 0, 0, 1, 0, 0);
          ctxSlow.scale(dpr, dpr);
          ctxSlow.imageSmoothingEnabled = false;
        }
        slowStars = generateStars(vw, vh, dpr, CELL_SIZE, FILL_PROB);
      }
      if (fast) {
        fast.width = Math.round(vw * dpr);
        fast.height = Math.round(vh * dpr);
        fast.style.position = "absolute";
        fast.style.left = "0";
        fast.style.top = "0";
        fast.style.width = "100%";
        fast.style.height = "100%";
        const ctxFast = fast.getContext("2d");
        if (ctxFast) {
          ctxFast.setTransform(1, 0, 0, 1, 0, 0);
          ctxFast.scale(dpr, dpr);
          ctxFast.imageSmoothingEnabled = false;
        }
        fastStars = generateStars(vw, vh, dpr, FAST_CELL_SIZE, FAST_FILL_PROB);
      }
      // compute ship size and initial position
      if (shipImgEl && shipWrapEl) {
        shipWidth = shipImgEl.naturalWidth || shipImgEl.width || 0;
        shipHeight = shipImgEl.naturalHeight || shipImgEl.height || 0;
        // place ship centered horizontally, but keep it below the viewport initially
        shipX = Math.round((vw - shipWidth) / 2);
        // position shipTop off-screen (below viewport) so it starts hidden
        shipTop = Math.round(vh + Math.max(24, shipHeight / 2));
        // apply to wrapper but preserve the translate-based offscreen transform so it remains hidden
        shipWrapEl.style.position = "fixed";
        shipWrapEl.style.left = "50%";
        shipWrapEl.style.transform = "translate(-50%,100vh)";
        shipWrapEl.style.bottom = "auto";
        // do not enable absolute positioning here — wait for the intro sequence to enable movement
        shipUseAbsolutePosition = false;
      }
      // prepare badguy pixel buffer for pixel-perfect collision
      // (Enemy offscreen buffer handled by Enemy component)
      if (!mq.matches) startAnimation();
    }

    setup();

    // wire behavior: defer to next frame so Svelte has bound the Enemy component
    requestAnimationFrame(() => {
      try {
        if (enemyComp) behavior.attach(enemyComp);
        if (shipImgEl) shipBuffer.setShipImage(shipImgEl);
        // start behavior later after timed intro sequence; hide enemy initially
        try {
          if (enemyComp && typeof enemyComp.hide === "function")
            enemyComp.hide();
        } catch (e) {}
        // startBehavior will be called after the intro timeline completes
        // schedule the intro timeline and audio so battle begins at t=16s
        scheduleIntroTimeline();
        // prepare audio element muted so autoplay doesn't get blocked; unmute after user gesture
        try {
          const musicEl = document.getElementById(
            "boss-music",
          ) as HTMLAudioElement | null;
          if (musicEl) {
            musicEl.muted = true;
            musicEl.play().catch(() => {});
          }
        } catch (e) {}
        // wire unmute button click handler (safe to call multiple times)
        try {
          const btn = document.getElementById("unmute-btn");
          if (btn) {
            const handler = () => {
              try {
                const musicEl = document.getElementById(
                  "boss-music",
                ) as HTMLAudioElement | null;
                if (musicEl) {
                  musicEl.muted = false;
                  musicEl.play().catch(() => {});
                }
                if (_audioCtx && _audioCtx.state === "suspended")
                  try {
                    _audioCtx.resume();
                  } catch (e) {}
                const container = document.getElementById("unmute-container");
                if (container) container.style.display = "none";
              } catch (e) {}
            };
            // attach once (store on element so we can remove later)
            (btn as any).__unmute_handler = handler;
            btn.addEventListener("click", handler);
          }
        } catch (e) {}
        // wire player hit callback to decrement player HP
        try {
          behavior.onPlayerHit((x: number, y: number, damage: number) => {
            try {
              playerHP.damage(damage);
            } catch (e) {}
          });
        } catch (e) {}
      } catch (e) {}
    });

    // lazy-fetch the external laser sound so we can decode it for low-latency playback
    if (!_laserFetchInProgress) {
      _laserFetchInProgress = true;
      fetch("/sounds/laser-gun.mp3", { cache: "force-cache" })
        .then((res) => res.arrayBuffer())
        .then((buf) => {
          _laserArrayBuffer = buf;
          const ctx = _audioCtx || ensureAudioContext();
          if (ctx) {
            try {
              ctx.decodeAudioData(
                buf.slice(0),
                (decoded) => {
                  _laserAudioBuffer = decoded;
                },
                () => {
                  // ignore decode error
                },
              );
            } catch (e) {
              // ignore
            }
          }
        })
        .catch(() => {
          // ignore fetch errors
        });
    }

    // Resize observer for responsive canvas
    const RO: any = (window as any).ResizeObserver;
    if (RO) {
      resizeObserver = new RO(() => {
        setup();
      });
      if (resizeObserver) resizeObserver.observe(document.documentElement);
    } else {
      // typed addEventListener fallback
      (window as any).addEventListener("resize", setup);
    }

    visibilityHandler = () => {
      if (document.hidden) stopAnimation();
      else if (!mq.matches) startAnimation();
    };
    document.addEventListener("visibilitychange", visibilityHandler);

    const mqListener = (e: MediaQueryListEvent) => {
      if (e.matches) stopAnimation();
      else startAnimation();
    };
    mq.addEventListener?.("change", mqListener);

    onDestroy(() => {
      stopAnimation();
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("keyup", handleKeyUp);
      if (resizeObserver) resizeObserver.disconnect();
      else window.removeEventListener("resize", setup);
      document.removeEventListener("visibilitychange", visibilityHandler);
      mq.removeEventListener?.("change", mqListener);
      try {
        behavior.stopBehavior();
      } catch (e) {}
      // clear any scheduled intro timers
      clearIntroTimeline();
      // remove unmute handler if attached
      try {
        const btn = document.getElementById("unmute-btn") as any;
        if (btn && btn.__unmute_handler) {
          try {
            btn.removeEventListener("click", btn.__unmute_handler);
          } catch (e) {}
          btn.__unmute_handler = null;
        }
      } catch (e) {}
    });
  });

  // --- Intro timeline orchestration ---
  let _introTimers: number[] = [];
  function clearIntroTimeline() {
    for (const id of _introTimers) {
      try {
        clearTimeout(id);
      } catch (e) {}
    }
    _introTimers.length = 0;
  }

  function scheduleIntroTimeline() {
    clearIntroTimeline();
    const musicEl = document.getElementById(
      "boss-music",
    ) as HTMLAudioElement | null;
    const main404 = document.getElementById("main-404");
    const main404sub = document.getElementById("main-404-sub");
    const middle = document.getElementById("middle-msg");
    const controls = document.getElementById("controls-msg");
    const warn = document.getElementById("warning-flash");

    const t0 = performance.now();
    // Start music immediately (user gesture may be required on some browsers; attempt play)
    try {
      musicEl?.play().catch(() => {});
    } catch (e) {}

    // Timeline according to spec:
    // 0s: music starts, enemy hidden (done earlier)
    // 0-5s: show main 404 prominently
    // 5s: over 1s, slide + shrink main 404 to bottom-right
    // 6s: show center message for 2s (6-8)
    // 8-9s: 1s gap
    // 9-14s: show controls overlay for 5s
    // 14s: flash red [ X WARNING X ] briefly (400ms)
    // 14.4s: start enemy entrance animation so battle mode begins at 16s (allow entranceDuration ~1600ms and preBattleIdle such that entered=true at 16s)

    // ensure enemy hidden
    try {
      if (enemyComp && typeof enemyComp.hide === "function") enemyComp.hide();
    } catch (e) {}

    // schedule main 404 shrink at 5s -> 6s transition
    _introTimers.push(
      window.setTimeout(() => {
        if (main404) {
          // switch to fixed positioning anchored to bottom-right so the element doesn't cause scrollbars
          main404.style.transition =
            "transform 1000ms ease, font-size 1000ms ease, opacity 1000ms ease, right 1000ms ease, bottom 1000ms ease";
          main404.style.transformOrigin = "right bottom";
          main404.style.position = "fixed";
          main404.style.right = "18px";
          main404.style.bottom = "18px";
          main404.style.margin = "0";
          main404.style.transform = "scale(0.45)";
          main404.style.opacity = "0.92";
          main404.style.pointerEvents = "auto";
          main404.style.zIndex = "9";
        }
        if (main404sub) {
          // subtitle should just fade out when the 404 moves rather than being relocated
          main404sub.style.transition = "opacity 600ms ease";
          main404sub.style.opacity = "0";
          // keep it out of layout flow and ensure no transforms cause scroll
          main404sub.style.position = "fixed";
          main404sub.style.right = "18px";
          main404sub.style.bottom = "64px";
          main404sub.style.margin = "0";
          main404sub.style.transform = "none";
          main404sub.style.zIndex = "9";
        }

        // move the go home button to the side of the shrunk 404 title, keeping it inside the viewport
        const btn = document.getElementById(
          "go-home-btn",
        ) as HTMLElement | null;
        if (btn && main404) {
          btn.style.transition =
            "left 1000ms ease, right 1000ms ease, bottom 1000ms ease, opacity 300ms ease";
          btn.style.position = "fixed";
          // compute a position to the left of the main404 title
          requestAnimationFrame(() => {
            try {
              const mrect = main404.getBoundingClientRect();
              const brect = btn.getBoundingClientRect();
              // place button to the left of the title with a 12px gap, clamp to viewport
              let left = Math.round(mrect.left - brect.width - 12);
              if (left < 12) left = 12;
              btn.style.left = `${left}px`;
              btn.style.bottom = "18px";
              btn.style.right = "auto";
              btn.style.zIndex = "9";
            } catch (e) {}
          });
        }
      }, 5000),
    );

    // show middle message at 6s for 2s
    _introTimers.push(
      window.setTimeout(() => {
        if (middle) {
          middle.style.display = "block";
          middle.style.opacity = "0";
          middle.style.transition = "opacity 260ms ease";
          requestAnimationFrame(() => (middle.style.opacity = "1"));
        }
        // show unmute control and start blinking for 3s
        const unmuteContainer = document.getElementById("unmute-container");
        const unmuteBtn = document.getElementById("unmute-btn");
        const unmuteArrow = document.getElementById("unmute-arrow");
        if (unmuteContainer) unmuteContainer.style.display = "flex";
        if (unmuteBtn) {
          // blinking animation via class toggling
          unmuteBtn.classList.add("blink-3s");
          // stop blinking after 3s
          _introTimers.push(
            window.setTimeout(() => {
              try {
                unmuteBtn.classList.remove("blink-3s");
              } catch (e) {}
            }, 3000),
          );
        }
        if (unmuteArrow) {
          unmuteArrow.style.opacity = "1";
          unmuteArrow.style.transition = "opacity 200ms ease";
        }
      }, 6000),
    );
    _introTimers.push(
      window.setTimeout(() => {
        if (middle) {
          middle.style.opacity = "0";
          setTimeout(() => (middle.style.display = "none"), 280);
        }
      }, 8000),
    );

    // 1s gap -> show controls overlay at 9s for 5s
    _introTimers.push(
      window.setTimeout(() => {
        if (controls) {
          controls.style.display = "block";
          controls.style.opacity = "0";
          controls.style.transition = "opacity 240ms ease";
          requestAnimationFrame(() => (controls.style.opacity = "1"));
        }
        // slide player ship and HP into view when controls appear
        try {
          // delay slightly so the controls overlay is visible first
          _introTimers.push(
            window.setTimeout(() => {
              try {
                if (shipWrapEl) {
                  // ensure the wrapper is anchored to the bottom center before removing the offscreen translate
                  shipWrapEl.style.left = "50%";
                  shipWrapEl.style.bottom = "8vh";
                  shipWrapEl.style.top = "";
                  shipWrapEl.style.transform = "translate(-50%,0)";
                }
              } catch (e) {}
              try {
                if (typeof playerHPWrapEl !== "undefined" && playerHPWrapEl) {
                  playerHPWrapEl.style.left = "12px";
                }
              } catch (e) {}
            }, 220),
          );
          // after the visual slide completes, enable absolute positioning so RAF updates will control the ship
          _introTimers.push(
            window.setTimeout(
              () => {
                try {
                  if (shipWrapEl) {
                    // compute the current rect and set shipX/shipTop so RAF doesn't snap
                    const r = shipWrapEl.getBoundingClientRect();
                    shipX = r.left;
                    shipTop = r.top;
                    shipUseAbsolutePosition = true;
                  }
                } catch (e) {}
              },
              220 + 1200 + 40,
            ),
          );
        } catch (e) {}
      }, 9000),
    );
    _introTimers.push(
      window.setTimeout(() => {
        if (controls) {
          controls.style.opacity = "0";
          setTimeout(() => (controls.style.display = "none"), 260);
        }
      }, 14000),
    );

    // flash warning at 14s for ~400ms
    _introTimers.push(
      window.setTimeout(() => {
        if (warn) {
          warn.style.display = "block";
          warn.style.opacity = "0";
          warn.style.transition = "opacity 120ms ease";
          requestAnimationFrame(() => (warn.style.opacity = "1"));
        }
      }, 14000),
    );
    _introTimers.push(
      window.setTimeout(() => {
        if (warn) {
          warn.style.opacity = "0";
          setTimeout(() => (warn.style.display = "none"), 150);
        }
      }, 14400),
    );

    // start enemy entrance at ~14.4s so that entranceDuration + preBattleIdle align to reach battle entered=true at 16s
    // we will use entranceDuration=1200ms and preBattleIdle=400ms -> arrival at ~15.6 and preBattleIdle to 16.0 when entered true
    _introTimers.push(
      window.setTimeout(() => {
        // show enemy and start behavior with tuned timing
        try {
          if (enemyComp && typeof enemyComp.show === "function")
            enemyComp.show();
        } catch (e) {}
        try {
          behavior.startBehavior({
            entranceDuration: 1200,
            preBattleIdle: 400,
          });
        } catch (e) {}
        // fade in enemy health bar
        try {
          const eh = document.querySelector(
            ".enemy-health-wrap",
          ) as HTMLElement | null;
          if (eh) {
            eh.style.opacity = "1";
          }
        } catch (e) {}
        // fade out arrow once battle begins
        try {
          const unmuteArrow = document.getElementById("unmute-arrow");
          if (unmuteArrow) {
            unmuteArrow.style.opacity = "0";
          }
        } catch (e) {}
      }, 14400),
    );
  }
</script>

<svelte:head>
  <title>{config.app.name} - Not Found</title>
  <style>
    .star-canvas-wrap {
      position: fixed;
      inset: 0;
      z-index: 0;
      pointer-events: none;
      background: radial-gradient(
        ellipse at center,
        rgba(10, 12, 20, 1) 0%,
        rgba(2, 4, 10, 1) 100%
      );
      overflow: hidden;
    }
    .star-layer {
      position: absolute;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      display: block;
      background: transparent; /* only white pixels are drawn */
    }
    .slow-layer {
      z-index: 0;
    }
    .fast-layer {
      z-index: 1;
    }
    .app-404-content {
      position: relative;
      z-index: 2;
      min-height: 100vh;
      display: flex;
      align-items: center;
    }
    /* ship placement */
    .ship-wrap {
      position: fixed;
      left: 50%;
      bottom: 8vh; /* near the bottom */
      transform: translateX(-50%);
      z-index: 3; /* above canvases, below any dev overlays */
      pointer-events: none;
      display: flex;
      justify-content: center;
      align-items: flex-end;
    }
    .ship-img {
      display: block;
      width: auto; /* keep intrinsic image size */
      height: auto;
      max-width: none;
      max-height: none;
      image-rendering: pixelated; /* keep crisp pixels */
    }
    /* badguy visuals are provided by the Enemy component */
  </style>
</svelte:head>

<div class="star-canvas-wrap">
  <canvas
    bind:this={slowCanvasEl}
    aria-hidden="true"
    class="star-layer slow-layer"
  ></canvas>
  <canvas
    bind:this={fastCanvasEl}
    aria-hidden="true"
    class="star-layer fast-layer"
  ></canvas>
</div>

<!-- Enemy component + health bar -->
<Enemy bind:this={enemyComp} />
{#if $enemyHPStore > 0}
  <div
    class="enemy-health-wrap"
    aria-hidden="true"
    style="opacity:0;transition:opacity 420ms ease"
  >
    <div class="enemy-health-bar">
      <div
        class="enemy-health-fill"
        style="width: {Math.max(0, ($enemyHPStore / ENEMY_MAX_HP) * 100)}%"
      ></div>
      <div class="enemy-health-text">{$enemyHPStore} / {ENEMY_MAX_HP}</div>
    </div>
  </div>
{/if}

<!-- ship image sits above the star layers but underneath interactive UI -->
<!-- ship starts offscreen (translateY) and will slide up when controls show -->
<div
  class="ship-wrap"
  aria-hidden="true"
  bind:this={shipWrapEl}
  style="transform:translate(-50%,100vh);transition:transform 1200ms cubic-bezier(.22,.9,.27,1)"
>
  <img
    src="/images/ship.png"
    alt="ship"
    class="ship-img"
    bind:this={shipImgEl}
  />
</div>

<!-- (Enemy visual served by Enemy component above) -->

<div class="container py-5 app-404-content">
  <div class="row justify-content-center w-100">
    <div class="col-md-8 text-center">
      <h1 id="main-404" class="display-4 text-white">404 — Page Not Found</h1>
      <p id="main-404-sub" class="lead text-light">
        We couldn't find the page you're looking for.
      </p>
      <a id="go-home-btn" class="btn btn-primary" href="/">Go home</a>
    </div>
  </div>
</div>

<!-- Player HP (bottom-left) -->
<!-- player HP starts offscreen left and will slide in when controls show -->
<div
  class="player-hp-wrap"
  aria-hidden="true"
  bind:this={playerHPWrapEl}
  style="left:-260px;transition:left 520ms cubic-bezier(.22,.9,.27,1)"
>
  <div class="player-hp-bar">
    <div
      class="player-hp-fill"
      style="width: {Math.max(0, ($playerHP / PLAYER_MAX_HP) * 100)}%"
    ></div>
    <div
      style="position:absolute;left:8px;top:2px;color:#e8fff0;font-weight:700;font-size:12px;pointer-events:none"
    >
      Pilot
    </div>
  </div>
  <div class="player-hp-text">HP: {$playerHP} / {PLAYER_MAX_HP}</div>
</div>

<!-- Intro overlays -->
<div
  id="middle-msg"
  style="position:fixed;left:50%;top:48%;transform:translate(-50%,-50%);z-index:9;color:white;font-size:26px;display:none;pointer-events:none"
>
  But maybe you can find it... in the stars!
</div>

<div
  id="controls-msg"
  style="position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);z-index:9;color:white;font-size:20px;display:none;pointer-events:none"
>
  <div style="display:flex;gap:12px;align-items:center;justify-content:center;">
    <div style="text-align:center;">↑<br />Up</div>
    <div style="text-align:center;">↓<br />Down</div>
    <div style="text-align:center;">←<br />Left</div>
    <div style="text-align:center;">→<br />Right</div>
    <div style="text-align:center;">Space<br />Fire</div>
  </div>
</div>

<div
  id="warning-flash"
  style="position:fixed;left:50%;top:45%;transform:translate(-50%,-50%);z-index:9;color:red;font-weight:900;font-size:28px;display:none;pointer-events:none"
>
  [ X WARNING X]
</div>

<audio id="boss-music" src="/sounds/boss-fight.mp3" preload="auto"></audio>

<!-- Unmute control (top-right). Hidden until the middle message shows. -->
<div
  id="unmute-container"
  style="position:fixed;top:12px;right:12px;z-index:12;display:none;align-items:center;gap:8px"
>
  <button
    id="unmute-btn"
    style="padding:8px 12px;border-radius:6px;border:none;background:#ffd54f;color:#111;font-weight:700;cursor:pointer"
    >🔊 Enable sound</button
  >
  <div
    id="unmute-arrow"
    style="position:fixed;top:56px;right:18px;z-index:12;color:#ffd54f;font-size:22px;opacity:1;transition:opacity 400ms ease"
  >
    ⬇
  </div>
</div>

<style>
  .enemy-health-wrap {
    position: fixed;
    left: 50%;
    top: 8px;
    transform: translateX(-50%);
    z-index: 7;
    width: 60%;
    max-width: 720px;
    pointer-events: none;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .enemy-health-bar {
    width: 100%;
    height: 14px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.6);
    overflow: hidden;
  }
  .enemy-health-fill {
    height: 100%;
    background: linear-gradient(90deg, #ff4d4d, #ffcc33);
    width: 100%;
    transform-origin: left center;
    transition: width 180ms ease-out;
  }
  .enemy-health-text {
    position: absolute;
    color: white;
    font-weight: 600;
    font-size: 12px;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6);
    pointer-events: none;
  }
  /* player HP bar (bottom-left) */
  .player-hp-wrap {
    position: fixed;
    left: 12px;
    bottom: 12px;
    z-index: 9;
    width: 220px;
    pointer-events: none;
  }
  .player-hp-bar {
    width: 100%;
    height: 18px;
    background: rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
  }
  .player-hp-fill {
    height: 100%;
    background: linear-gradient(90deg, #4de680, #2ebd4a);
    width: 100%;
    transition: width 180ms linear;
  }
  .player-hp-text {
    margin-top: 6px;
    color: #fff;
    font-size: 13px;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6);
    pointer-events: none;
  }
  /* blink helper (used dynamically via JS) */
  :global(.blink-3s) {
    animation: blinkPulse 0.45s ease-in-out infinite;
  }
  @keyframes blinkPulse {
    0% {
      transform: scale(1);
      box-shadow: 0 0 0 rgba(255, 213, 79, 0);
    }
    50% {
      transform: scale(1.06);
      box-shadow: 0 0 10px rgba(255, 213, 79, 0.6);
    }
    100% {
      transform: scale(1);
      box-shadow: 0 0 0 rgba(255, 213, 79, 0);
    }
  }
  /* low health flashing */
  @keyframes hpFlash {
    0% {
      box-shadow:
        0 2px 6px rgba(0, 0, 0, 0.5),
        0 0 6px rgba(255, 0, 0, 0);
    }
    50% {
      box-shadow:
        0 2px 6px rgba(0, 0, 0, 0.5),
        0 0 14px rgba(255, 0, 0, 0.85);
    }
    100% {
      box-shadow:
        0 2px 6px rgba(0, 0, 0, 0.5),
        0 0 6px rgba(255, 0, 0, 0);
    }
  }
  :global(.player-hp-low) .player-hp-bar {
    animation: hpFlash 800ms linear infinite;
  }
  :global(.player-hp-low) .player-hp-fill {
    background: linear-gradient(90deg, #ff6b6b, #ff3b3b) !important;
  }
</style>
