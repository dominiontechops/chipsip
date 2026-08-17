/* Chip & Sip service worker — build 2026-08-17.02
   ----------------------------------------------------------------------------------------------
   This exists for one reason: to make the board open instantly and to keep working in a bar with
   no signal. It is deliberately narrow.

   WHAT IT CACHES: the app shell only — the page itself, the icons, the manifest. Nothing else.

   WHAT IT MUST NEVER CACHE: anything from Supabase. Every pool, price and bet is live data, and a
   stale pool served from a cache is a stake struck at the wrong odds. Every cross-origin request
   and every non-GET request is passed straight through to the network, untouched. The app already
   has its own honest offline mode — it shows the last read it took, stamps the age on it, and
   refuses to accept a bet until the signal is back. That belongs in the app, where it can say so,
   not hidden in a worker that quietly lies about how fresh the numbers are.

   THE PAGE ITSELF is network-first, not cache-first. A new build must reach twenty phones the
   moment it is pushed; a cache-first shell would leave men betting on last week's board until
   they happened to clear their browser. Cache is the fallback for when the network fails.
   ---------------------------------------------------------------------------------------------- */
const BUILD = "2026-08-17.02";
const CACHE = "chipsip-" + BUILD;

/* Relative, so it works whether this is served from a domain root or a GitHub Pages sub-path. */
const SHELL = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icon-192.png",
  "./icon-512.png",
  "./apple-touch-icon.png"
];

self.addEventListener("install", e => {
  /* addAll fails the whole install if any single file 404s, which would leave the app with no
     worker at all. Fetch them individually and shrug off the ones that are not there. */
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    await Promise.all(SHELL.map(u => c.add(u).catch(() => {})));
    self.skipWaiting();
  })());
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k.startsWith("chipsip-") && k !== CACHE).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;                              // never touch a POST — that is a bet
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;               // Supabase, fonts, anything else: hands off

  const isPage = req.mode === "navigate" ||
    (req.destination === "document") ||
    url.pathname.endsWith("/") || url.pathname.endsWith("index.html");

  if (isPage) {
    /* Network first. If the network answers, that answer is the truth and it replaces the cache.
       If it does not, fall back to whatever shell we have, so the app opens and can say offline
       in its own words rather than showing the browser's dinosaur. */
    e.respondWith((async () => {
      try {
        const fresh = await fetch(req);
        const c = await caches.open(CACHE);
        c.put("./index.html", fresh.clone());
        return fresh;
      } catch (err) {
        const c = await caches.open(CACHE);
        return (await c.match("./index.html")) || (await c.match("./")) || Response.error();
      }
    })());
    return;
  }

  /* Everything else same-origin — icons, faces, the manifest — is cache first with a quiet
     background refresh. These change rarely and are the difference between opening instantly
     and staring at a white screen. */
  e.respondWith((async () => {
    const c = await caches.open(CACHE);
    const hit = await c.match(req);
    const net = fetch(req).then(r => { if (r && r.ok) c.put(req, r.clone()); return r; }).catch(() => null);
    return hit || (await net) || Response.error();
  })());
});

/* Lets the page tell a waiting worker to take over immediately when the user presses Update. */
self.addEventListener("message", e => { if (e.data === "skipWaiting") self.skipWaiting(); });
