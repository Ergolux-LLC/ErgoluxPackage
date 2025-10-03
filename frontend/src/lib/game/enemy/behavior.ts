// Placeholder for enemy behavior logic. Export functions to be implemented later.
import Enemy from './Enemy.svelte';
import { enemyHP } from './stats';
import shipBuffer from '$lib/game/ship/shipBuffer';

// Behavior implementation with multiple firing patterns and an RAF-driven beam loop
let _enemyComp: any = null;
let _running = false;
let _t0 = 0;
let _entered = false; // has the enemy finished its entrance
let _baseY = 40; // baseline Y used after entrance so movement doesn't jump
// movement target state (randomized movement)
let _moveStartTime = 0; // ms
let _moveStartX = 0;
let _moveTargetX = 0;
let _moveDuration = 1600; // ms
// pre-super movement snapshot so we can resume exactly where we left off
let _preSuper_moveStartX: number | null = null;
let _preSuper_moveTargetX: number | null = null;
let _preSuper_moveStartTime: number | null = null;
let _preSuper_moveDuration: number | null = null;
let _preSuper_elapsed: number | null = null;
let _hadMovementBeforeSuper = false;

// beams tracked in an array for a single RAF updater
type Beam = {
  el: HTMLDivElement;
  x: number;
  y: number;
  vx: number;
  vy: number;
  lifetime: number;
  width: number;
  height: number;
  // new fields for attachment and accurate movement
  baseX?: number;
  baseY?: number;
  age?: number; // seconds since fired
  initialEnemyX?: number;
  initialEnemyY?: number;
  attached?: boolean;
  lockX?: boolean; // when true, beam's X is fixed to baseX regardless of vx
};

const beams: Beam[] = [];
let _rafId: any = null;

// firing pattern state
let _pattern = 0; // 0=rapid,1=burst,2=spread
let _lastPatternSwitch = 0;
let _patternDur = 3500 + Math.random() * 2000; // ms
// super-move state
let _superActive = false;
let _nextSuperAt: number | null = null; // will be set to 20s after battle start
// when a super-move is active we freeze the enemy's screen position to avoid jumps
let _frozenCenterX: number | null = null;
let _frozenY: number | null = null;

// Audio elements for super-charge and zap
let _chargeAudio: HTMLAudioElement | null = null;
let _zapAudio: HTMLAudioElement | null = null;
let _enemyLaserBaseAudio: HTMLAudioElement | null = null;
let _boomBaseAudio: HTMLAudioElement | null = null;
let _playerHitBaseAudio: HTMLAudioElement | null = null;
let _audioCtx: AudioContext | null = null;
let _chargeSourceNode: MediaElementAudioSourceNode | null = null;
let _chargeGainNode: GainNode | null = null;

function ensureChargeAudio() {
  if (_chargeAudio) return _chargeAudio;
  try {
    const a = new Audio('/sounds/power-charge.mp3');
    a.preload = 'auto';
    a.loop = true;
    // attempt to route through WebAudio so we can amplify the charge sound beyond element.volume
    try {
      const Ctor = (window as any).AudioContext || (window as any).webkitAudioContext;
      if (Ctor) {
        _audioCtx = _audioCtx || new Ctor();
        // create source and gain only once
        if (!_chargeSourceNode) {
          try {
            const ctx = _audioCtx as AudioContext;
            _chargeSourceNode = ctx.createMediaElementSource(a);
            _chargeGainNode = ctx.createGain();
            // set gain higher than 1 for louder sound (clipping may occur if too high)
            _chargeGainNode.gain.value = 6.0; // increased gain for louder charge sound
            _chargeSourceNode.connect(_chargeGainNode);
            _chargeGainNode.connect(ctx.destination);
          } catch (e) {
            // if createMediaElementSource fails, fall back to element volume
            try { a.volume = 1.0; } catch (ee) {}
          }
        }
      } else {
        try { a.volume = 1.0; } catch (e) {}
      }
    } catch (e) {
      try { a.volume = 1.0; } catch (ee) {}
    }
    // keep muted until play is user-allowed by page audio context; play() will reject if blocked
    _chargeAudio = a;
  } catch (e) {
    _chargeAudio = null;
  }
  return _chargeAudio;
}

function ensureZapAudio() {
  if (_zapAudio) return _zapAudio;
  try {
    const a = new Audio('/sounds/big-zap.mp3');
    a.preload = 'auto';
    a.loop = false;
    _zapAudio = a;
  } catch (e) {
    _zapAudio = null;
  }
  return _zapAudio;
}

function ensureEnemyLaserBase() {
  if (_enemyLaserBaseAudio) return _enemyLaserBaseAudio;
  try {
    const a = new Audio('/sounds/enemy-laser-regular.mp3');
    a.preload = 'auto';
    // keep base element for cloning to allow overlapping playback
    _enemyLaserBaseAudio = a;
  } catch (e) {
    _enemyLaserBaseAudio = null;
  }
  return _enemyLaserBaseAudio;
}

function ensureBoomAudio() {
  if (_boomBaseAudio) return _boomBaseAudio;
  try {
    const a = new Audio('/sounds/boss-boom.mp3');
    a.preload = 'auto';
    _boomBaseAudio = a;
  } catch (e) {
    _boomBaseAudio = null;
  }
  return _boomBaseAudio;
}

function playBoomSound() {
  try {
    const base = ensureBoomAudio();
    if (!base) return;
    const a = base.cloneNode(true) as HTMLAudioElement;
    a.play().catch(() => {});
  } catch (e) {}
}

function ensurePlayerHitAudio() {
  if (_playerHitBaseAudio) return _playerHitBaseAudio;
  try {
    const a = new Audio('/sounds/player-ship-hit.mp3');
    a.preload = 'auto';
    _playerHitBaseAudio = a;
  } catch (e) {
    _playerHitBaseAudio = null;
  }
  return _playerHitBaseAudio;
}

function playPlayerHitSound() {
  try {
    const base = ensurePlayerHitAudio();
    if (!base) return;
    const a = base.cloneNode(true) as HTMLAudioElement;
    a.play().catch(() => {});
  } catch (e) {}
}

function playEnemyLaserSound() {
  try {
    const base = ensureEnemyLaserBase();
    if (!base) return;
    // clone so multiple rapid beams can overlap
    const a = base.cloneNode(true) as HTMLAudioElement;
    a.play().catch(() => {});
  } catch (e) {}
}

function playChargeSound() {
  try {
    const a = ensureChargeAudio();
    if (a) a.play().catch(() => {});
  } catch (e) {}
}

function stopChargeSound() {
  try {
    if (_chargeAudio) {
      _chargeAudio.pause();
      try { _chargeAudio.currentTime = 0; } catch (e) {}
    }
  } catch (e) {}
}

function playZapSound() {
  try {
    const z = ensureZapAudio();
    if (z) {
      try { z.currentTime = 0; } catch (e) {}
      z.play().catch(() => {});
    }
  } catch (e) {}
}

// player-hit callback (page can set to update player HP or UI)
// callback receives x,y and damage amount
let _onPlayerHit: ((x: number, y: number, damage: number) => void) | null = null;

export function onPlayerHit(cb: (x: number, y: number, damage: number) => void) {
  _onPlayerHit = cb;
}

export function attach(enemyComp: any) {
  _enemyComp = enemyComp;
}

// helper: animate enemy from above viewport straight down to target Y
function entranceSequence(targetY = 40, duration = 900) {
  return new Promise<void>((resolve) => {
    if (!_enemyComp || typeof _enemyComp.setTransform !== 'function') {
      resolve();
      return;
    }
    // start far above viewport
    let startY = - (window.innerHeight * 0.6 + 200);
    const start = performance.now();
    function frame(now: number) {
      const t = Math.min(1, (now - start) / duration);
      // ease out cubic
      const ease = 1 - Math.pow(1 - t, 3);
      const y = startY + (targetY - startY) * ease;
      try { _enemyComp.setTransform(0, y); } catch (e) {}
      if (t < 1) requestAnimationFrame(frame);
      else resolve();
    }
    requestAnimationFrame(frame);
  });
}

function createBeam(x: number, y: number, vx: number, vy: number, width = 6, height = 18, lockX = false) {
  const el = document.createElement('div');
  el.className = 'enemy-beam';
  el.style.position = 'fixed';
  el.style.left = `${Math.round(x - width / 2)}px`;
  el.style.top = `${Math.round(y)}px`;
  el.style.width = `${width}px`;
  el.style.height = `${height}px`;
  el.style.background = 'linear-gradient(180deg,#d9b3ff,#7a3bff)';
  el.style.boxShadow = '0 0 12px rgba(140,70,220,0.9)';
  el.style.zIndex = '6';
  el.style.pointerEvents = 'none';
  el.style.borderRadius = '2px';
  // disable transitions and hint to browser for stable left/top updates
  el.style.transition = 'none';
  el.style.willChange = 'left, top';
  el.style.transform = 'none';
  document.body.appendChild(el);
  // capture initial enemy rect so small beams visually follow the ship as it wiggles
  // store base position and start age; beams should travel relative to viewport after being fired
  beams.push({
    el,
    x,
    y,
    vx,
    vy,
    lifetime: 6000,
    width,
    height,
    baseX: x,
    baseY: y,
    age: 0,
    lockX: !!lockX,
  });
  // play small beam sound (non-blocking)
  try { playEnemyLaserSound(); } catch (e) {}
}

// pick a new target X for randomized movement within viewport bounds with an inset so it doesn't hug edges
function pickNewTarget(startX?: number) {
  if (!_enemyComp || typeof _enemyComp.getRect !== 'function') return;
  try {
    const rect = _enemyComp.getRect();
    const halfW = rect ? rect.width / 2 : 150;
    const inset = Math.max(40, halfW + 30); // keep some margin from edges
    const minX = inset;
    const maxX = Math.max(inset + 10, window.innerWidth - inset);
    // startX, if provided, is where movement will begin (important after a frozen super)
    if (typeof startX === 'number') {
      _moveStartX = Math.round(startX);
    } else {
      _moveStartX = _moveTargetX || Math.round(window.innerWidth / 2);
    }
    _moveTargetX = Math.round(minX + Math.random() * (maxX - minX));
    _moveStartTime = performance.now();
    _moveDuration = 1000 + Math.random() * 2200; // between 1s and 3.2s
  } catch (e) {}
}

function easeInOutCubic(p: number) {
  return p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
}

function clearAllBeams() {
  for (const b of beams) b.el.remove();
  beams.length = 0;
}

function updateBeams(dt: number) {
  // dt in seconds
  for (let i = beams.length - 1; i >= 0; --i) {
    const b = beams[i];
  // advance age and compute base motion due to velocity
  b.age = (typeof b.age === 'number' ? b.age : 0) + dt;
  const age = b.age;
  const baseX = typeof b.baseX === 'number' ? b.baseX : b.x;
  const baseY = typeof b.baseY === 'number' ? b.baseY : b.y;
  // compute final position from initial base + velocity*time
  const posFromVelY = baseY + b.vy * age;
  // X can either be locked to the firing origin (lockX) or computed from vx*age for true spread angles
  const finalX = (b.lockX ? baseX : baseX + b.vx * age);
  const finalY = posFromVelY;
  b.lifetime -= dt * 1000;
  // update internal position to match the rendered final position so collision checks are accurate
  b.x = finalX;
  b.y = finalY;
  b.el.style.left = `${Math.round(finalX - b.width / 2)}px`;
  b.el.style.top = `${Math.round(finalY)}px`;

    // sample a few points along the beam for collision with ship
    const sampleStep = Math.max(4, Math.floor(b.height / 3));
    let hit = false;
    for (let sy = Math.round(b.y); sy < Math.round(b.y + b.height); sy += sampleStep) {
      const sx = Math.round(b.x);
      try {
        if (shipBuffer.isShipOpaque(sx, sy)) {
          hit = true;
          // visual hit
          const m = document.createElement('div');
          m.style.position = 'fixed';
          m.style.left = `${sx - 10}px`;
          m.style.top = `${sy - 10}px`;
          m.style.width = '20px';
          m.style.height = '20px';
          m.style.borderRadius = '50%';
          m.style.background = 'radial-gradient(circle,#fff,#d9b3ff)';
          m.style.zIndex = '9';
          m.style.pointerEvents = 'none';
          document.body.appendChild(m);
          setTimeout(() => m.remove(), 220);
          // notify page
          try { if (_onPlayerHit) _onPlayerHit(sx, sy, 1); } catch (e) {}
          try { playPlayerHitSound(); } catch (e) {}
          break;
        }
      } catch (e) {}
    }

    if (hit || b.y > window.innerHeight + 120 || b.lifetime <= 0) {
      b.el.remove();
      beams.splice(i, 1);
    }
  }
}

function movementFrame(now: number) {
  if (!_running) return;
  if (!_t0) _t0 = now;
  const t = (now - _t0) / 1000; // seconds
  if (_enemyComp && typeof _enemyComp.setTransform === 'function') {
    if (_entered && _superActive) {
      // while a super is active, force the enemy to remain at the frozen start position
      try {
        if (typeof _enemyComp.setPosition === 'function' && _frozenCenterX !== null && _frozenY !== null) {
          _enemyComp.setPosition(_frozenCenterX, _frozenY);
        } else if (_frozenY !== null) {
          // fallback: keep vertical position and avoid horizontal wiggle
          _enemyComp.setTransform(0, _frozenY);
        }
      } catch (e) {}
    } else if (_entered && !_superActive) {
      // randomized target movement: interpolate center X between start and target
      try {
        // ensure we have a valid movement target
        if (!_moveTargetX || performance.now() - _moveStartTime > _moveDuration) pickNewTarget();
        const now = performance.now();
        const pRaw = Math.min(1, Math.max(0, (now - _moveStartTime) / _moveDuration));
        const p = easeInOutCubic(pRaw);
        const centerX = Math.round(_moveStartX + ( _moveTargetX - _moveStartX ) * p);
        const yOffset = _baseY + (Math.sin(t * 2.4) * 10 + Math.sin(t * 3.1) * 3);
        if (typeof _enemyComp.setPosition === 'function' && typeof _enemyComp.getRect === 'function') {
          const rect = _enemyComp.getRect();
          const halfW = rect ? rect.width / 2 : 150;
          const clampedCenterX = Math.max(halfW, Math.min(window.innerWidth - halfW, centerX));
          _enemyComp.setPosition(clampedCenterX, yOffset);
        } else {
          // fallback to legacy transform using offset from center
          const offsetX = centerX - window.innerWidth / 2;
          _enemyComp.setTransform(offsetX, yOffset);
        }
      } catch (e) {}
    }
    // if not entered, entranceSequence already controls transform
  }
  // update beams
  // compute dt from last frame stored on _t0
  const dt = 1 / 60; // approximate; use RAF frequency for simplicity
  updateBeams(dt);

  // pattern switching
  const nowMs = performance.now();
  if (nowMs - _lastPatternSwitch > _patternDur) {
    _pattern = (_pattern + 1) % 3;
    _lastPatternSwitch = nowMs;
    _patternDur = 2500 + Math.random() * 3000;
  }

  // maybe trigger super-move if time
  if (_entered && !_superActive && _nextSuperAt !== null && nowMs >= _nextSuperAt) {
    startSuperMove().catch(() => {});
  }

  // firing controller (disabled during super)
  if (_entered && !_superActive) maybeFire(nowMs);

  _rafId = requestAnimationFrame(movementFrame);
}

// firing timing state
let _lastFire = 0;
let _burstCount = 0;

function maybeFire(nowMs: number) {
  if (!_enemyComp || typeof _enemyComp.getRect !== 'function') return;
  const rect = _enemyComp.getRect();
  if (!rect) return;

  // base rates (ms)
  const baseRapid = 100; // very fast single-shot
  const baseBurstInterval = 600; // between bursts
  const burstShotGap = 90; // ms between shots inside a burst
  const spreadInterval = 220; // slower but multi-shot spread

  if (_pattern === 0) {
    // rapid single shots aimed at ship center x
    if (nowMs - _lastFire > baseRapid) {
      _lastFire = nowMs;
      // aim at player's current ship center x (estimate from shipBuffer bounds)
  // shipBuffer currently exposes only setShipImage/isShipOpaque; try optional helper or fall back
  const sbAny: any = shipBuffer as any;
  const shipCenterX = typeof sbAny.getShipCenterX === 'function' ? sbAny.getShipCenterX() : Math.round(window.innerWidth / 2);
      // compute beam origin from enemy rect bottom center (visual)
      const originX = Math.round(rect.left + rect.width / 2);
      const originY = Math.round(rect.bottom);
      // fire straight down from the enemy's bottom-center so beams originate visually from the ship
      createBeam(originX, originY, 0, 320, 6, 22);
    }
  } else if (_pattern === 1) {
    // burst mode: fire 3-5 shots quickly, then wait
    if (_burstCount > 0) {
      // we are in a burst, fire next shot if gap passed
      if (nowMs - _lastFire > burstShotGap) {
        _lastFire = nowMs;
        _burstCount--;
        createBeam(Math.round(rect.left + rect.width / 2), Math.round(rect.bottom), 0, 360, 6, 24);
      }
    } else if (nowMs - _lastFire > baseBurstInterval) {
      // start a new burst
      _burstCount = 3 + Math.floor(Math.random() * 3); // 3-5 shots
      _lastFire = nowMs;
    }
  } else {
    // spread mode: fire a true angled fan of 3 beams
    if (nowMs - _lastFire > spreadInterval) {
      _lastFire = nowMs;
      const cx = Math.round(rect.left + rect.width / 2);
      const sp = 320; // downward speed
      // angled horizontal speeds (px/s) for left, center, right
      const vxs = [-80, 0, 80];
      for (let i = 0; i < 3; i++) {
        // all beams originate visually at the enemy bottom-center
        createBeam(cx, Math.round(rect.bottom), vxs[i], sp, 6, 20, /*lockX=*/ false);
      }
    }
  }
}

export function startBehavior(opts?: { entranceDuration?: number; preBattleIdle?: number }) {
  if (_running) return;
  _running = true;
  _t0 = 0;
  _lastPatternSwitch = performance.now();
  _lastFire = 0;
  _burstCount = 0;
  // start with entrance; only after arrival + 5s do we let _entered=true and fire/move
  (async () => {
    try {
      // move onto screen
      await entranceSequence(40, opts?.entranceDuration ?? 900);
    } catch (e) {}
    // set baseY to the arrival Y so subsequent movement is relative and doesn't jump
    _baseY = 40;
    // keep ship idle for 5 seconds before active behavior
    _entered = false;
    await new Promise((r) => setTimeout(r, opts?.preBattleIdle ?? 5000));
  // reset timing so movement offsets start at zero (no jump)
    _t0 = performance.now();
    _lastPatternSwitch = performance.now();
    _lastFire = performance.now();
    _burstCount = 0;
    // explicitly set the transform to the arrival position before enabling movement
    try {
      if (_enemyComp && typeof _enemyComp.setTransform === 'function') {
        _enemyComp.setTransform(0, _baseY);
      }
    } catch (e) {}
    _entered = true;
    // schedule first super 20s after battle mode begins
    _nextSuperAt = performance.now() + 20000;
    // initialize movement target starting at current rect center so we don't jump
    try {
      if (_enemyComp && typeof _enemyComp.getRect === 'function') {
        const r = _enemyComp.getRect();
        if (r) pickNewTarget(r.left + r.width / 2);
      }
    } catch (e) {}
  })();
  _rafId = requestAnimationFrame(movementFrame);
}

export function stopBehavior() {
  _running = false;
  if (_rafId) cancelAnimationFrame(_rafId);
  _rafId = null;
  clearAllBeams();
}

export const api = {
  attach,
  startBehavior,
  stopBehavior,
  onPlayerHit,
};

// Explosions: when enemyHP reaches 0, show staged small explosions then a final big one
let _dying = false;
function smallExplosionAt(x: number, y: number) {
  const el = document.createElement('div');
  el.style.position = 'fixed';
  el.style.left = `${Math.round(x) - 6}px`;
  el.style.top = `${Math.round(y) - 6}px`;
  el.style.width = '12px';
  el.style.height = '12px';
  el.style.borderRadius = '50%';
  el.style.background = `radial-gradient(circle, #fff, #ffb3b3, #ff6b6b)`;
  el.style.boxShadow = '0 0 12px rgba(255,120,80,0.95)';
  el.style.zIndex = '40';
  el.style.pointerEvents = 'none';
  el.style.transition = 'transform 180ms ease-out, opacity 180ms linear';
  document.body.appendChild(el);
  try { playBoomSound(); } catch (e) {}
  // animate a quick pop+fade
  requestAnimationFrame(() => {
    el.style.transform = 'scale(1.4)';
    el.style.opacity = '0.95';
  });
  // short life so many can appear in 5s
  const lifetime = 160 + Math.random() * 180; // 160-340ms
  setTimeout(() => {
    try {
      el.style.opacity = '0';
      el.style.transform = 'scale(0.6)';
      setTimeout(() => el.remove(), 180);
    } catch (e) { try { el.remove(); } catch (er) {} }
  }, lifetime);
}

/**
 * Animated big explosion that grows from a small dot at (x,y) to target size (tw,th).
 * Returns a Promise that resolves when the final animation completes.
 */
function bigExplosionAt(x: number, y: number, tw?: number, th?: number, duration = 900) {
  return new Promise<void>((resolve) => {
    // sanitize center coordinates
    let cx = Number(x);
    let cy = Number(y);
    if (!Number.isFinite(cx)) cx = Math.round(window.innerWidth / 2);
    if (!Number.isFinite(cy)) cy = Math.round(window.innerHeight / 2);
    cx = Math.max(0, Math.min(window.innerWidth - 1, Math.round(cx)));
    cy = Math.max(0, Math.min(window.innerHeight - 1, Math.round(cy)));

    // target size defaults
    const finalW = Math.max(64, Math.round(tw ?? 120));
    const finalH = Math.max(64, Math.round(th ?? finalW));

    // create element starting very small at center
    const el = document.createElement('div');
    el.style.position = 'fixed';
    // start as a 12x12 centered at cx,cy
    const startSz = 12;
    el.style.left = `${cx - startSz / 2}px`;
    el.style.top = `${cy - startSz / 2}px`;
    el.style.width = `${startSz}px`;
    el.style.height = `${startSz}px`;
    el.style.borderRadius = '50%';
    el.style.background = 'radial-gradient(circle,#fff,#ffb3b3,#ff3b3b)';
    el.style.boxShadow = '0 0 60px rgba(255,80,40,0.95)';
    el.style.zIndex = '60';
    el.style.pointerEvents = 'none';
    el.style.transformOrigin = 'center center';
    el.style.transition = `left ${duration}ms ease-out, top ${duration}ms ease-out, width ${duration}ms ease-out, height ${duration}ms ease-out, opacity ${Math.max(200, duration / 6)}ms linear`;
    document.body.appendChild(el);

    // force layout then animate to final size/position
    requestAnimationFrame(() => {
      el.style.left = `${Math.round(cx - finalW / 2)}px`;
      el.style.top = `${Math.round(cy - finalH / 2)}px`;
      el.style.width = `${finalW}px`;
      el.style.height = `${finalH}px`;
      // slightly fade in then out by end
      el.style.opacity = '1';
    });

    // after animation completes, remove element and resolve
    setTimeout(() => {
      // play boom SFX for the final big explosion
      try { playBoomSound(); } catch (e) {}
      // fade out explosion and remove shortly after
      try { el.style.opacity = '0'; } catch (e) {}
      setTimeout(() => {
        try { el.remove(); } catch (e) {}
        resolve();
      }, 180);
    }, duration);
  });
}

// --- Super-move implementation ---
function makeCircleElement(cx: number, cy: number, r = 8) {
  const el = document.createElement('div');
  el.style.position = 'fixed';
  el.style.left = `${cx - r}px`;
  el.style.top = `${cy - r}px`;
  el.style.width = `${r * 2}px`;
  el.style.height = `${r * 2}px`;
  el.style.borderRadius = '50%';
  el.style.border = '2px solid rgba(200,120,255,0.95)';
  el.style.background = 'radial-gradient(circle, rgba(160,120,255,0.22), rgba(120,60,200,0.06))';
  el.style.boxShadow = '0 0 24px rgba(150,80,220,0.6)';
  el.style.zIndex = '11';
  el.style.pointerEvents = 'none';
  document.body.appendChild(el);
  return el;
}

async function startSuperMove() {
  if (_superActive || !_enemyComp || typeof _enemyComp.getRect !== 'function') return;
  _superActive = true;
  // snapshot movement state so we can resume exactly where we left off
  try {
    _preSuper_moveStartX = _moveStartX;
    _preSuper_moveTargetX = _moveTargetX;
    _preSuper_moveStartTime = _moveStartTime;
    _preSuper_moveDuration = _moveDuration;
    _preSuper_elapsed = _moveStartTime ? (performance.now() - _moveStartTime) : 0;
    _hadMovementBeforeSuper = !!_moveTargetX;
  } catch (e) {}

  // capture current center position to freeze enemy during super
  try {
    const rect = _enemyComp.getRect();
    if (rect) {
      _frozenCenterX = rect.left + rect.width / 2;
      _frozenY = rect.top;
    }
  } catch (e) {}
  // pause regular firing by keeping _superActive true; movement is also skipped in RAF
  const rect = _enemyComp.getRect();
  if (!rect) { _superActive = false; return; }
  const originX = Math.round(rect.left + rect.width / 2);
  const originY = Math.round(rect.bottom);

  // growth circle: grow from small to match the ship's max dimension (radius = half the max side)
  const finalRadius = Math.max(rect.width, rect.height) * 0.5;
  const duration = 4000;
  // solid purple charge circle
  const circle = makeCircleElement(originX, originY, 6);
  circle.style.background = 'rgba(140,40,220,0.95)';
  circle.style.border = '2px solid rgba(180,120,255,0.95)';
  // start charge sound loop
  try { playChargeSound(); } catch (e) {}
  const start = performance.now();
  await new Promise<void>((resolve) => {
    function frame(now: number) {
      const p = Math.min(1, (now - start) / duration);
      const r = 6 + (finalRadius - 6) * p;
      circle.style.left = `${Math.round(originX - r)}px`;
      circle.style.top = `${Math.round(originY - r)}px`;
      circle.style.width = `${Math.round(r * 2)}px`;
      circle.style.height = `${Math.round(r * 2)}px`;
      if (p < 1) requestAnimationFrame(frame);
      else resolve();
    }
    requestAnimationFrame(frame);
  });

  // fire big beam from origin downward (long straight beam) with width matching the charge circle diameter
  try {
    // stop the charge sound right before beam fires, and play the zap effect
    try { stopChargeSound(); } catch (e) {}
    try { playZapSound(); } catch (e) {}
    // wait until the beam finishes; keep circle visible while beam is active
    await shootBigBeam(originX, originY, Math.round(finalRadius * 2));
    // keep the charge circle visible for an extra 500ms after the beam ends
    await new Promise((r) => setTimeout(r, 500));
  } catch (e) {
    // if beam fails, stop charge sound and still remove circle after a short delay
    try { stopChargeSound(); } catch (err) {}
    await new Promise((r) => setTimeout(r, 200));
  }
  // remove the visual charge circle
  try { circle.remove(); } catch (e) {}

  // small cooldown after big shot
  await new Promise((r) => setTimeout(r, 500));
  // schedule next super between 10 and 20 seconds from now
  _nextSuperAt = performance.now() + 10000 + Math.random() * 10000;
  _superActive = false;
  // release frozen pos
  // restore pre-super movement snapshot if we had one so movement resumes smoothly
  try {
    if (_hadMovementBeforeSuper && _preSuper_moveStartX !== null && _preSuper_moveTargetX !== null && _preSuper_moveStartTime !== null && _preSuper_moveDuration !== null && _preSuper_elapsed !== null) {
      // compute new start values so interpolation resumes where it left off
      _moveStartX = _preSuper_moveStartX;
      _moveTargetX = _preSuper_moveTargetX;
      // shift the start time so that elapsed time continues from where it paused
      _moveStartTime = performance.now() - _preSuper_elapsed;
      _moveDuration = _preSuper_moveDuration;
    } else if (typeof _frozenCenterX === 'number') {
      // fallback: start from frozen center
      pickNewTarget(_frozenCenterX);
    }
  } catch (e) {}
  _frozenCenterX = null;
  _frozenY = null;
  // clear pre-super snapshot
  _preSuper_moveStartX = null;
  _preSuper_moveTargetX = null;
  _preSuper_moveStartTime = null;
  _preSuper_moveDuration = null;
  _preSuper_elapsed = null;
  _hadMovementBeforeSuper = false;
}

function shootBigBeam(x: number, y: number, width = 300) {
  // wide beam that travels downward fast
  const el = document.createElement('div');
  el.style.position = 'fixed';
  el.style.left = `${Math.round(x - width / 2)}px`;
  el.style.top = `${Math.round(y)}px`;
  el.style.width = `${width}px`;
  el.style.height = `${Math.max(window.innerHeight, 800)}px`;
  el.style.background = 'linear-gradient(180deg, rgba(180,120,255,0.95), rgba(120,40,220,0.95))';
  el.style.boxShadow = '0 0 60px rgba(120,40,220,0.9)';
  el.style.zIndex = '7';
  el.style.pointerEvents = 'none';
  document.body.appendChild(el);

  // check collision along beam every 60ms for a short time while it is active
  const speed = 900; // px/s (visual travel not necessary since element spans full height)
  const duration = 900; // ms
  const start = performance.now();
  return new Promise<void>((resolve) => {
    const interval = setInterval(() => {
      const now = performance.now();
      // sample a few points across width near player's ship area
      try {
        for (let sx = x - Math.floor(width / 2); sx <= x + Math.floor(width / 2); sx += Math.max(10, Math.floor(width / 8))) {
          for (let sy = Math.round(y); sy < window.innerHeight; sy += 40) {
            try {
              if (shipBuffer.isShipOpaque(sx, sy)) {
                // small hit effect
                const m = document.createElement('div');
                m.style.position = 'fixed';
                m.style.left = `${sx - 12}px`;
                m.style.top = `${sy - 12}px`;
                m.style.width = '24px';
                m.style.height = '24px';
                m.style.borderRadius = '50%';
                m.style.background = 'radial-gradient(circle,#fff,#ffd3ff)';
                m.style.zIndex = '10';
                m.style.pointerEvents = 'none';
                document.body.appendChild(m);
                setTimeout(() => m.remove(), 260);
                try { if (_onPlayerHit) _onPlayerHit(sx, sy, 10); } catch (e) {}
                try { playPlayerHitSound(); } catch (e) {}
              }
            } catch (e) {}
          }
        }
      } catch (e) {}
      if (now - start > duration) {
        clearInterval(interval);
        try { el.remove(); } catch (e) {}
        resolve();
      }
    }, 60);
  });
}

async function runDeathSequence() {
  if (_dying) return;
  _dying = true;
  // stop firing/movement control but keep ship visible for explosions
  _entered = false;
  // ensure enemy is visible (page-level code may have hidden it when HP reached 0)
  try {
    if (_enemyComp && typeof _enemyComp.show === 'function') _enemyComp.show();
  } catch (e) {}
  // capture a stable rect/center BEFORE explosions start so we have absolute coordinates
  let stableRect: DOMRect | null = null;
  try {
    if (_enemyComp && typeof _enemyComp.getRect === 'function') {
      stableRect = _enemyComp.getRect();
      if (!stableRect) {
        try { if (typeof _enemyComp.show === 'function') _enemyComp.show(); } catch (e) {}
        stableRect = _enemyComp.getRect();
      }
    }
  } catch (e) { stableRect = null; }
  // prevent any external caller from hiding the enemy until death sequence finishes
  try { if (_enemyComp && typeof _enemyComp.preventHide === 'function') _enemyComp.preventHide(true); } catch (e) {}
  // compute absolute center coordinates now (use viewport center fallback)
  const shipCenterX = stableRect ? (stableRect.left + stableRect.width / 2) : Math.round(window.innerWidth / 2);
  const shipCenterY = stableRect ? (stableRect.top + stableRect.height / 2) : Math.round(window.innerHeight / 2);
  logDebug('[death] stableRect captured', stableRect, 'center=', shipCenterX, shipCenterY);
  // perform many small explosions across visible enemy for ~5s
  const duration = 5000;
  const end = performance.now() + duration;
  // lightweight debug helper that stores logs on window for page-side inspection
  function logDebug(...args: any[]) {
    try {
      // normal console output
      // eslint-disable-next-line no-console
      console.log(...args);
      // mirror into a page-global array for easier inspection (stringify safe)
      const w = window as any;
      w.__GAME_DEBUG_LOG = w.__GAME_DEBUG_LOG || [];
      try {
        const s = args.map(a => (typeof a === 'object' ? JSON.stringify(a) : String(a))).join(' ');
        w.__GAME_DEBUG_LOG.push(s);
      } catch (e) {
        w.__GAME_DEBUG_LOG.push(String(args));
      }
    } catch (e) {}
  }
  while (performance.now() < end) {
    if (!_enemyComp || typeof _enemyComp.isPointOpaque !== 'function') break;
    // use stableRect for sampling bounds; fallback to live rect if stable missing
    let rect = stableRect;
    if (!rect && typeof _enemyComp.getRect === 'function') {
      rect = _enemyComp.getRect();
    }
    logDebug('[death] runDeathSequence iteration, using rect=', rect);
    if (!rect) break;
    // aggressively pick random opaque pixels on the visible PNG portion of enemy (relative to rect)
    let found = false;
    let pickX = NaN;
    let pickY = NaN;
    // try a larger number of attempts but bail quickly if found
    for (let attempt = 0; attempt < 12; attempt++) {
      const rx = rect.left + Math.random() * rect.width;
      const ry = rect.top + Math.random() * rect.height;
      try {
        if (_enemyComp.isPointOpaque(rx, ry)) {
          pickX = rx; pickY = ry; found = true; break;
        }
      } catch (e) {}
    }
    if (!found) {
      // fallback to center-ish jitter to ensure explosions are near the ship
      pickX = rect.left + rect.width * (0.3 + Math.random() * 0.4);
      pickY = rect.top + rect.height * (0.25 + Math.random() * 0.6);
    }
    // clamp to viewport
    pickX = Math.max(0, Math.min(window.innerWidth - 1, Math.round(pickX)));
    pickY = Math.max(0, Math.min(window.innerHeight - 1, Math.round(pickY)));
    smallExplosionAt(pickX, pickY);
    logDebug('[death] small explosion at', pickX, pickY, 'foundOpaque=', found);
    // very short delay so many explosions appear over 5s
    await new Promise((r) => setTimeout(r, 50 + Math.random() * 80));
  }
  // final big explosion at center
  if (_enemyComp && typeof _enemyComp.getRect === 'function') {
    let rect = _enemyComp.getRect();
    if (!rect) {
      try { if (typeof _enemyComp.show === 'function') _enemyComp.show(); } catch (e) {}
      rect = _enemyComp.getRect();
    }
    if (rect) {
      // use stableRect center if available to guarantee we know the center beforehand
      const cx = stableRect ? (stableRect.left + stableRect.width / 2) : (rect.left + rect.width / 2);
      const cy = stableRect ? (stableRect.top + stableRect.height / 2) : (rect.top + rect.height / 2);
      const tw = stableRect ? stableRect.width : rect.width;
      const th = stableRect ? stableRect.height : rect.height;
      logDebug('[death] big explosion center computed as', cx, cy, 'targetSize=', tw, th, 'rect=', rect);
      // animate final explosion to the ship's exact size
      await bigExplosionAt(cx, cy, tw, th, 900).catch(() => {});
    }
  }
  // Immediately release the preventHide lock and hide the enemy once the final
  // big explosion animation Promise has resolved (so the ship disappears exactly
  // when the explosion finishes).
  try {
    if (_enemyComp && typeof _enemyComp.preventHide === 'function') _enemyComp.preventHide(false);
    if (_enemyComp && typeof _enemyComp.hide === 'function') _enemyComp.hide();
  } catch (e) {}
  // final cleanup: clear beams and stop RAF
  clearAllBeams();
  stopBehavior();
}

// watch enemyHP for death
enemyHP.subscribe((v) => {
  if (v <= 0) {
    runDeathSequence().catch(() => {});
  }
});
