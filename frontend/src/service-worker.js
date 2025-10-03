/// <reference lib="webworker" />

/* Improved service worker
   - versioned caches
   - precache core app shell on install
   - stale-while-revalidate for CSS/JS/assets
   - cache-first for images (with max entries)
   - network-first for navigation (with offline fallback)
   - skipWaiting + clients.claim for immediate activation
   - message handler to trigger skipWaiting from the page
*/

const VERSION = "v2";
const PRECACHE = `ergolux-precache-${VERSION}`;
const RUNTIME = `ergolux-runtime-${VERSION}`;
const IMAGE_CACHE = `ergolux-images-${VERSION}`;

/** @type {ServiceWorkerGlobalScope} */
const sw = /** @type {any} */ (self);
const APP_SHELL = ["/", "/index.html", "/build/bundle.css", "/build/bundle.js"];

const MAX_IMAGE_ENTRIES = 60;

/**
 * Trim a cache to at most `maxItems` entries.
 * @param {string} cacheName
 * @param {number} maxItems
 * @returns {Promise<void>}
 */
function trimCache(cacheName, maxItems) {
  return caches.open(cacheName).then((cache) =>
    cache.keys().then((keys) => {
      if (keys.length > maxItems) {
        const deletions = keys
          .slice(0, keys.length - maxItems)
          .map((k) => cache.delete(k));
        return Promise.all(deletions).then(() => {});
      }
    })
  );
}

sw.addEventListener("install", (event) => {
  console.log("[SW] Install", VERSION);
  sw.skipWaiting();
  /** @type {ExtendableEvent} */
  (event).waitUntil(
    caches
      .open(PRECACHE)
      .then((cache) => cache.addAll(APP_SHELL))
      .catch((err) => console.error("Failed to precache", err))
  );
});

sw.addEventListener("activate", (event) => {
  console.log("[SW] Activate", VERSION);
  /** @type {ExtendableEvent} */
  (event).waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter((k) => ![PRECACHE, RUNTIME, IMAGE_CACHE].includes(k))
            .map((k) => caches.delete(k))
        )
      )
  );
  return sw.clients.claim();
});

// Utility: is navigation request
/**
 * @param {Request} request
 * @returns {boolean}
 */
function isNavigationRequest(request) {
  return (
    request.mode === "navigate" ||
    (request.headers.get("accept") || "").includes("text/html")
  );
}

sw.addEventListener("fetch", (event) => {
  /** @type {FetchEvent} */
  const fe = event;
  const request = fe.request;

  // Navigation: network-first, fallback to cache then offline fallback page
  if (isNavigationRequest(request)) {
    fe.respondWith(
      fetch(request)
        .then((response) => {
          // Put a copy in runtime cache for future navigations
          const copy = response.clone();
          caches.open(RUNTIME).then((cache) => cache.put(request, copy));
          return response;
        })
        .catch(() =>
          caches
            .match(request)
            .then(
              (r) =>
                r ||
                caches
                  .match("/")
                  .then(
                    (rr) =>
                      rr ||
                      new Response("Offline", {
                        status: 503,
                        headers: { "Content-Type": "text/html" },
                      })
                  )
            )
        )
    );
    return;
  }

  // Images: cache-first with LRU trimming
  if (
    request.destination === "image" ||
    /\.(png|jpg|jpeg|gif|webp|svg)$/.test(request.url)
  ) {
    fe.respondWith(
      caches.match(request).then((cached) => {
        if (cached) return cached;
        return fetch(request)
          .then((res) => {
            const copy = res.clone();
            caches
              .open(IMAGE_CACHE)
              .then((cache) =>
                cache
                  .put(request, copy)
                  .then(() => trimCache(IMAGE_CACHE, MAX_IMAGE_ENTRIES))
              );
            return res;
          })
          .catch(() =>
            caches
              .match("/")
              .then((r) => r || new Response("", { status: 504 }))
          );
      })
    );
    return;
  }

  // Static assets (CSS/JS/fonts): stale-while-revalidate
  if (
    /\.(?:js|css|woff2?|ttf|eot|otf)$/.test(request.url) ||
    request.destination === "script" ||
    request.destination === "style" ||
    request.destination === "font"
  ) {
    fe.respondWith(
      caches.open(RUNTIME).then((cache) =>
        cache.match(request).then((cached) => {
          const networkFetch = fetch(request)
            .then((response) => {
              if (response && response.status === 200)
                cache.put(request, response.clone());
              return response;
            })
            .catch(() =>
              caches
                .match(request)
                .then((r) => r || new Response("Offline", { status: 503 }))
            );

          return cached || networkFetch;
        })
      )
    );
    return;
  }

  // Default: try network then cache
  fe.respondWith(
    fetch(request)
      .then((res) => {
        // cache runtime responses for future offline
        const copy = res.clone();
        caches.open(RUNTIME).then((cache) => cache.put(request, copy));
        return res;
      })
      .catch(() =>
        caches
          .match(request)
          .then((r) => r || new Response("Offline", { status: 503 }))
      )
  );
});

// Allow the page to trigger skipWaiting/update flow
sw.addEventListener("message", (event) => {
  if (!event.data) return;
  switch (event.data.type) {
    case "SKIP_WAITING":
      sw.skipWaiting();
      break;
    default:
      console.log("Unknown message to SW:", event.data);
  }
});
