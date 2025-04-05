// مشاعر | Mashaaer PWA Service Worker
const CACHE_NAME = 'mashaaer-cache-v1';

// المصادر التي سيتم تخزينها محلياً
const urlsToCache = [
  '/',
  '/static/sounds/click.mp3',
  '/static/sounds/hover.mp3',
  '/static/sounds/listen_start.mp3',
  "/static/offline.html",
  '/static/sounds/listen_stop.mp3',
  '/static/sounds/welcome.mp3',
  '/static/sounds/greeting.mp3',
  '/static/sounds/cosmic.mp3',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  '/static/manifest.json',
  '/health',
  '/cosmic-onboarding',
  '/cosmic-theme'
];

// تثبيت Service Worker وتخزين الموارد
self.addEventListener('install', event => {
  console.log('[ServiceWorker] Install');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[ServiceWorker] Caching app shell');
        return cache.addAll(urlsToCache);
      })
  );
});

// تنشيط Service Worker وحذف التخزين المؤقت القديم
self.addEventListener('activate', event => {
  console.log('[ServiceWorker] Activate');
  event.waitUntil(
    caches.keys().then(keyList => {
      return Promise.all(keyList.map(key => {
        if (key !== CACHE_NAME) {
          console.log('[ServiceWorker] Removing old cache', key);
          return caches.delete(key);
        }
      }));
    })
  );
  // تأكد من أن Service Worker يبدأ في التحكم في الصفحات فوراً
  return self.clients.claim();
});

// استراتيجية "الشبكة أولاً ثم التخزين المؤقت" للأنماط الديناميكية مثل API
const networkThenCache = async (event) => {
  try {
    // محاولة جلب من الشبكة
    const networkResponse = await fetch(event.request);
    
    // إذا كان الرد ناجحًا، احفظه في التخزين المؤقت ثم أعده
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(event.request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    // إذا فشل الاتصال بالشبكة، استخدم التخزين المؤقت
    const cachedResponse = await caches.match(event.request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
};

// استراتيجية "التخزين المؤقت أولاً ثم الشبكة" للمصادر الثابتة
const cacheFirstThenNetwork = async (event) => {
  const cachedResponse = await caches.match(event.request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  // إذا لم يكن في التخزين المؤقت، حاول من الشبكة
  try {
    const networkResponse = await fetch(event.request);
    
    // خزن الاستجابة الجديدة
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(event.request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    // فشل الاتصال تماماً
    console.error('[ServiceWorker] Fetch failed; returning offline page instead.', error);
    throw error;
  }
};

// معالجة طلبات الشبكة
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  
  // إذا كان الطلب يبدأ بـ /api/ استخدم استراتيجية الشبكة أولاً
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkThenCache(event));
  } 
  // للمصادر الثابتة مثل الصور والأصوات استخدم التخزين المؤقت أولاً
  else if (
    url.pathname.includes('/static/') || 
    url.pathname.includes('/icons/') || 
    url.pathname.includes('/sounds/')
  ) {
    event.respondWith(cacheFirstThenNetwork(event));
  }
  // لجميع الطلبات الأخرى، حاول الشبكة أولاً ثم التخزين المؤقت
  else {
    event.respondWith(networkThenCache(event));
  }
});
