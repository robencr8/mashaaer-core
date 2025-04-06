/**
 * Service Worker for Mashaaer Feelings Application
 * Provides offline support and caching for the Progressive Web App
 */

const CACHE_NAME = 'mashaaer-cosmic-v1';

// Resources to pre-cache
const PRECACHE_URLS = [
  '/',
  '/start',
  '/static/mobile/css/mobile_style.css',
  '/static/mobile/css/app.css',
  '/static/mobile/js/emotion_audio_integration.js',
  '/static/mobile/js/app.js',
  '/static/mobile/js/api-service.js',
  '/static/mobile/audio/happy_cosmic.mp3',
  '/static/mobile/audio/sad_cosmic.mp3',
  '/static/mobile/audio/angry_cosmic.mp3',
  '/static/mobile/audio/calm_cosmic.mp3',
  '/static/mobile/images/robin-icon-192.png',
  '/static/mobile/images/robin-icon-512.png'
];

// Install event - pre-cache critical resources
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching app shell and content');
        return cache.addAll(PRECACHE_URLS);
      })
      .then(() => {
        console.log('Service Worker: Installation complete');
        return self.skipWaiting();
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  
  const currentCaches = [CACHE_NAME];
  
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return cacheNames.filter(cacheName => !currentCaches.includes(cacheName));
      })
      .then(cachesToDelete => {
        return Promise.all(cachesToDelete.map(cacheToDelete => {
          console.log('Service Worker: Clearing old cache:', cacheToDelete);
          return caches.delete(cacheToDelete);
        }));
      })
      .then(() => {
        console.log('Service Worker: Activation complete');
        return self.clients.claim();
      })
  );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', event => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }
  
  // Skip requests to API endpoints
  if (event.request.url.includes('/api/')) {
    return;
  }
  
  // For GET requests, try cache first, then network
  if (event.request.method === 'GET') {
    event.respondWith(
      caches.match(event.request)
        .then(cachedResponse => {
          if (cachedResponse) {
            console.log('Service Worker: Serving from cache:', event.request.url);
            return cachedResponse;
          }
          
          return fetch(event.request)
            .then(response => {
              // Don't cache non-success responses
              if (!response || response.status !== 200 || response.type !== 'basic') {
                return response;
              }
              
              // Clone the response to cache it and return it
              const responseToCache = response.clone();
              
              caches.open(CACHE_NAME)
                .then(cache => {
                  console.log('Service Worker: Caching new resource:', event.request.url);
                  cache.put(event.request, responseToCache);
                });
              
              return response;
            });
        })
        .catch(error => {
          console.error('Service Worker: Fetch failed:', error);
          // You could return a custom offline page here
          return caches.match('/static/mobile/offline.html');
        })
    );
  }
});

// Handle messages from clients
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
