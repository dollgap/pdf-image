/* 문서 변환기 · PDF↔이미지 · 오프라인 셸 캐시
   파일은 서버로 보내지 않는다. 변환은 브라우저 안에서만 이뤄지고,
   앱 셸과 PDF 엔진(pdf.js)·CMap·표준폰트를 모두 미리 받아 두어
   인터넷이 끊겨도 그대로 동작한다. */
const CACHE = 'pdf-image-shell-v1';
const SHELL = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  './icon-maskable-512.png',
  './sw.js',
  './vendor/pdf.min.mjs',
  './vendor/pdf.worker.min.mjs'
];

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    let list = SHELL;
    try {
      const res = await fetch('./sw-files.json', { cache: 'no-cache' });
      if (res.ok) {
        const json = await res.json();
        if (Array.isArray(json) && json.length) list = json;
      }
    } catch (e) { /* 목록을 못 받으면 기본 셸만 */ }

    // 한 파일이 실패해도 나머지는 계속 캐시한다.
    await Promise.all(list.map(async (url) => {
      try {
        const res = await fetch(url, { cache: 'no-cache' });
        if (res.ok) await cache.put(url, res);
      } catch (e) { /* 오프라인 설치 등은 무시 */ }
    }));
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // 문서 요청은 네트워크 우선, 끊겼을 때 캐시된 셸로 연다.
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((cache) => cache.put('./index.html', copy)).catch(() => {});
          return res;
        })
        .catch(async () => {
          const cache = await caches.open(CACHE);
          return (await cache.match('./index.html')) || (await cache.match('./')) || Response.error();
        })
    );
    return;
  }

  // 나머지 셸·엔진 파일은 캐시 우선.
  event.respondWith(
    caches.match(req).then((hit) => {
      if (hit) return hit;
      return fetch(req).then((res) => {
        if (res.ok && res.type === 'basic') {
          const copy = res.clone();
          caches.open(CACHE).then((cache) => cache.put(req, copy)).catch(() => {});
        }
        return res;
      });
    })
  );
});
