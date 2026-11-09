/* Offline support: keeps the whole guide (about 3.5 MB) on the device.
   Bump VERSION with every change (same number as the ?v= in index.html):
   a changed sw.js is what makes devices fetch the new files. */
var VERSION = "6";
var CACHE = "hf-guide-v" + VERSION;
var FILES = [
  "./", "index.html", "manifest.webmanifest",
  "css/guide.css", "js/content.js", "js/app.js", "js/install.js",
  "icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-512.png",
  "icons/apple-touch-icon.png", "icons/favicon-32.png", "icons/logo.png"
];
for (var i = 1; i <= 28; i++) FILES.push("img/image" + i + ".webp");

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(FILES); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k.indexOf("hf-guide-") === 0 && k !== CACHE; })
      .map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  if (req.mode === "navigate") {
    // the page: the network when there is one (so updates show), else the saved copy
    e.respondWith(fetch(req).catch(function () { return caches.match("index.html"); }));
    return;
  }
  // everything else: the saved copy (ignoring ?v=), else the network
  e.respondWith(caches.match(req, { ignoreSearch: true }).then(function (hit) { return hit || fetch(req); }));
});
