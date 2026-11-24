// Bnews PWA Service Worker (v4.0)
const CACHE_NAME = 'bnews-v4-shell-1';
const SHELL_ASSETS = [
  '/fintech-intelligence/',
  '/fintech-intelligence/index.html',
  '/fintech-intelligence/magspread.css',
  '/fintech-intelligence/magspread.js',
  '/fintech-intelligence/bnews-logo-light.svg',
  '/fintech-intelligence/fintech-favicon.svg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_ASSETS)).catch(() => {})
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;
  // Network-first for HTML/JSON/JS so new daily editions always load fresh
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
