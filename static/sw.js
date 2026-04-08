const CACHE_NAME = 'store-v3';
const ASSETS = ['/', '/static/style.css', '/static/icon.png'];

self.addEventListener('install', e => {
    e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(ASSETS)));
});

self.addEventListener('fetch', e => {
    // Never cache the add_to_cart API call
    if (e.request.url.includes('/add_to_cart/')) return;
    e.respondWith(caches.match(e.request).then(res => res || fetch(e.request)));
});

self.addEventListener('install', (event) => {
    console.log('Service Worker installed');
});

// Browsers REQUIRE a fetch handler for PWA installation
self.addEventListener('fetch', (event) => {
    // We can leave this empty for now, but it must exist
});