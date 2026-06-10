// Service worker minimal — coquille applicative hors-ligne (PWA, Sprint 10).
const CACHE = "btp-shell-v1";
const SHELL = ["/", "/dashboard", "/chat", "/manifest.json"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  // Ne jamais mettre en cache les appels API (toujours frais).
  if (request.method !== "GET" || new URL(request.url).pathname.startsWith("/api")) {
    return;
  }
  // Network-first avec repli cache (navigation hors-ligne).
  event.respondWith(
    fetch(request)
      .then((response) => {
        const copy = response.clone();
        caches.open(CACHE).then((c) => c.put(request, copy));
        return response;
      })
      .catch(() => caches.match(request).then((r) => r || caches.match("/")))
  );
});
