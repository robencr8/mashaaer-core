// Mashaaer Service Worker v1.0

const CACHE_NAME = 'mashaaer-cache-v1';
const OFFLINE_URL = '/offline';

// Assets to cache on install
const CORE_ASSETS = [
  '/',
  '/static/sounds/welcome.mp3',
  '/static/sounds/click.mp3',
  '/static/sounds/hover.mp3',
  '/static/sounds/cosmic.mp3',
  '/static/sounds/greeting.mp3',
  '/static/sounds/listen_start.mp3',
  '/static/sounds/listen_stop.mp3',
  '/tts_cache/fallback.mp3',
  '/offline',
  '/static/manifest.json'
];

// Install event - cache core assets
self.addEventListener('install', (event) => {
  console.log('Service Worker installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Caching core app shell and content');
        return cache.addAll(CORE_ASSETS);
      })
      .then(() => {
        console.log('Service Worker installed successfully');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker installation failed:', error);
      })
  );
});

// Activate event - cleanup old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.filter((cacheName) => {
            return cacheName !== CACHE_NAME;
          }).map((cacheName) => {
            console.log('Service Worker: Deleting old cache', cacheName);
            return caches.delete(cacheName);
          })
        );
      })
      .then(() => {
        console.log('Service Worker activated successfully, claiming clients');
        return self.clients.claim();
      })
  );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }
  
  // Handle API requests differently (network-first)
  if (event.request.url.includes('/api/')) {
    event.respondWith(
      fetch(event.request)
        .catch((error) => {
          console.log('Service Worker: API request failed, serving offline content', error);
          return caches.match('/offline');
        })
    );
    return;
  }
  
  // For other requests, try cache first, then network
  event.respondWith(
    caches.match(event.request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          console.log('Service Worker: Serving from cache:', event.request.url);
          return cachedResponse;
        }
        
        // Not in cache, get from network
        return fetch(event.request)
          .then((networkResponse) => {
            // Cache valid responses for future use
            if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
              const clonedResponse = networkResponse.clone();
              caches.open(CACHE_NAME)
                .then((cache) => {
                  console.log('Service Worker: Caching new resource:', event.request.url);
                  cache.put(event.request, clonedResponse);
                });
            }
            return networkResponse;
          })
          .catch((error) => {
            console.log('Service Worker: Network request failed, serving offline page', error);
            
            // If the request is for a page, show the offline page
            if (event.request.mode === 'navigate') {
              return caches.match('/offline');
            }
            
            // For other resources, return a simple error response
            return new Response('Network error happened', {
              status: 408,
              headers: { 'Content-Type': 'text/plain' }
            });
          });
      })
  );
});

// Listen for messages from the client
self.addEventListener('message', (event) => {
  if (event.data && event.data.action === 'skipWaiting') {
    self.skipWaiting();
  }
});
