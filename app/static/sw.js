const CACHE_NAME = 'daniapp-v1';

// Detecta o prefixo do app a partir da localização do SW
const SW_SCOPE = self.registration ? self.registration.scope : '/daniapp/';

const STATIC_ASSETS = [
  SW_SCOPE + 'm/',
  SW_SCOPE + 'static/css/style.css',
  SW_SCOPE + 'static/js/app.js',
  SW_SCOPE + 'static/manifest.json',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS).catch(() => {}))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  const isStatic = url.pathname.includes('/static/');

  if (isStatic) {
    event.respondWith(
      caches.match(event.request).then(cached => cached || fetch(event.request))
    );
  } else {
    event.respondWith(
      fetch(event.request).catch(() => caches.match(event.request))
    );
  }
});
