// Mashaaer PWA Service Worker
const CACHE_NAME = 'mashaaer-cache-v1';
const urlsToCache = [
  '/',
  '/start',
  '/static/mobile/css/app.css',
  '/static/mobile/js/emotion_audio_integration.js',
  '/static/mobile/audio/happy_cosmic.mp3',
  '/static/mobile/audio/sad_cosmic.mp3',
  '/static/mobile/audio/angry_cosmic.mp3',
  '/static/mobile/audio/calm_cosmic.mp3',
  '/static/mobile/audio/cosmicmusic.mp3',
  '/static/mobile/manifest.json'
];

// Install stage sets up the cache-array to configure pre-cache content
self.addEventListener('install', event => {
  console.log('Service Worker: Installing');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching Files');
        return cache.addAll(urlsToCache);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate the service worker and clear old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating');
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            console.log('Service Worker: Cleaning Old Cache');
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Serve cached content when offline
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }
        return fetch(event.request).then(
          fetchResponse => {
            // Check if we received a valid response
            if(!fetchResponse || fetchResponse.status !== 200 || fetchResponse.type !== 'basic') {
              return fetchResponse;
            }

            // If it's a valid navigation response, cache it
            if (event.request.mode === 'navigate' || 
                (event.request.method === 'GET' && 
                 event.request.headers.get('accept').includes('text/html'))) {
              
              // Clone the response as it can only be used once
              var responseToCache = fetchResponse.clone();
              caches.open(CACHE_NAME)
                .then(cache => {
                  cache.put(event.request, responseToCache);
                });
            }
            
            return fetchResponse;
          }
        );
      }).catch(() => {
        // If fetch fails, deliver the offline page for navigation requests
        if (event.request.mode === 'navigate') {
          return caches.match('/');
        }
      })
  );
});
