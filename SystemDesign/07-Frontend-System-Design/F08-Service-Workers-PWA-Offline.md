# F08. Service Workers + PWA + Offline
# हिंदी में: Service Worker — ब्राउज़र में पेज से अलग चलने वाली एक script जो बीच में बैठकर network requests पकड़ सकती है, cache से जवाब दे सकती है और offline काम चला सकती है; PWA — ऐसी website जो app जैसी install हो, offline चले और notifications भेजे

---

## 🔵 Simple Definition (English)
A **Service Worker (SW)** is a JavaScript file that the browser runs **in the background, separate from the page**, acting as a **programmable network proxy** between your web app and the network. It can:
- intercept `fetch` requests and respond from **Cache Storage**, the network, or both (caching strategies)
- make the app work **offline** or on flaky networks
- receive **push notifications** (Web Push) and do **background sync**
A **Progressive Web App (PWA)** is a web app that uses a service worker, a **Web App Manifest** (name, icons, theme, `display: standalone`) and HTTPS, so it is **installable** on the home screen, launches like an app, and works offline.

## 🔵 सरल परिभाषा (Hindi)
Service Worker एक JavaScript file है जो पेज से अलग, पीछे चलती है और ऐप व network के बीच "proxy" की तरह बैठती है — requests पकड़कर cache से जवाब दे सकती है, offline चला सकती है, push notification और background sync कर सकती है।
PWA = service worker + manifest (नाम, icon) + HTTPS वाली website, जो फ़ोन की home screen पर install हो, app जैसी खुले और बिना internet भी चले।

---

## 🔴 Problem it Solves
- **Flaky/slow networks** (trains, metros, rural 2G/3G in India): pages fail with the "dinosaur" offline screen.
- HTTP cache isn't **programmable**: you can't say "show cached feed instantly, then update", or "queue this message and send later".
- Native apps require **store installs** (big downloads, friction). Many users won't install a 50 MB app for occasional use.
- Repeat visits still need network for the HTML shell.

Service workers give **offline support, instant repeat loads (app shell), background sync and push**, and PWAs give an **installable, lightweight app experience** without app stores.

## 🔴 यह क्यों बना? (Hindi)
धीमे/टूटते नेटवर्क (मेट्रो, ट्रेन, गाँव में 2G/3G) में पेज fail हो जाते हैं; HTTP cache को हम code से नियंत्रित नहीं कर सकते ("पहले पुराना feed दिखाओ, फिर ताज़ा करो", "message बाद में भेजो")।
50 MB का native app हर कोई install नहीं करता। Service worker offline, तुरंत खुलना, background sync और push देता है; PWA बिना app store के हल्का, installable ऐप देता है।

---

## 🟢 How it Works — Step by Step

### Lifecycle

```
Page: navigator.serviceWorker.register('/sw.js')   (HTTPS or localhost only; scope = folder of sw.js)
   │
   ▼
INSTALL event   → pre-cache app shell (HTML shell, main JS/CSS, logo, offline.html)
   │               (event.waitUntil(cache.addAll([...])))
   ▼
WAITING         → new SW waits while old SW still controls open tabs
   │               (skipWaiting() to activate immediately — careful with version mismatch)
   ▼
ACTIVATE event  → delete old caches (versioned cache names), clients.claim()
   │
   ▼
FETCH events    → intercept every request in scope → apply caching strategy
PUSH / SYNC / message events → notifications, background sync, page communication
Browser may terminate the SW when idle → no global state; persist in Cache Storage / IndexedDB
```

### Caching strategies (Workbox names)

```
Cache First (cache falling back to network)
   → hashed static assets, fonts, images: instant, works offline
Network First (network falling back to cache)
   → HTML pages, API data that should be fresh (news feed, order status) but usable offline
Stale-While-Revalidate
   → return cache immediately, update cache from network in background
   → avatars, menus, catalog, non-critical API data
Network Only
   → payments, auth, POST requests (or queue with background sync)
Cache Only
   → pre-cached app shell assets

App shell model: cache the UI skeleton (header, nav, layout JS/CSS) → instant load; fetch content separately
```

### Offline writes: background sync / outbox

```
User sends message/order offline
   → save to IndexedDB "outbox" + show as "pending" in UI (optimistic)
   → register sync: registration.sync.register('send-outbox')       (Chromium; fallback: retry on 'online')
   → when connectivity returns, SW 'sync' event → replay requests with Idempotency-Key → mark sent
   → conflicts resolved by server (Topic M07)
```

### PWA requirements

```
✓ HTTPS
✓ manifest.json: name, short_name, icons (192, 512, maskable), start_url, display: standalone, theme_color
✓ Service worker with fetch handler (offline experience)
→ Chrome/Android shows install prompt (beforeinstallprompt); iOS: Share → Add to Home Screen
   (iOS supports Web Push for installed PWAs since iOS 16.4)
Storage: Cache Storage + IndexedDB, quota-based (browser may evict; request navigator.storage.persist())
```

### Update strategy (the tricky part)

```
New deploy → new sw.js bytes → browser installs new SW → WAITING
Options:
  a) Wait until all tabs close (safest, default)
  b) Show "New version available — Refresh" toast → postMessage SKIP_WAITING → reload   ⭐ common
  c) skipWaiting() immediately (risk: old page + new cached assets mismatch)
Serve sw.js itself with Cache-Control: no-cache so updates are detected
Always version caches (shell-v42) and clean old ones in activate
```

## 🟢 कैसे काम करता है? (Hindi)
1. पेज `register('/sw.js')` करता है (सिर्फ़ HTTPS); install में app shell (HTML ढाँचा, JS, CSS, offline पेज) पहले से cache होता है; activate में पुराने cache साफ़।
2. हर request SW के `fetch` से गुज़रती है — static files: Cache First; HTML/ताज़ा डेटा: Network First; menu/avatars: Stale-While-Revalidate; payment: Network Only।
3. Offline में भेजा message/order IndexedDB के outbox में रखो, UI में "pending" दिखाओ; internet लौटते ही sync event से Idempotency-Key के साथ भेजो।
4. PWA = HTTPS + manifest (नाम, icon, standalone) + service worker → home screen पर install; iOS 16.4+ पर installed PWA में push भी।
5. नया deploy → नया SW waiting में; "नया version आया — Refresh" दिखाओ; sw.js को no-cache रखो और cache नामों में version रखो।

---

## 🟡 Real World Example

**Flipkart Lite (2015)** — one of the first big PWAs, built for India's slow networks. It used an app-shell model, service worker caching and offline handling, and reported large gains: about 3× more time spent on the site and a 40% higher re-engagement rate in the published case study.

**Twitter Lite** — a PWA under ~1 MB versus a much larger native app. Service worker caching, offline support and data-saver mode made it work in markets with costly data.

**Starbucks PWA** — the ordering app works offline for browsing the menu and customizing orders, which sync when online. Starbucks reported the PWA as far smaller than its iOS app.

**Google Docs offline / Gmail offline** — use service workers and IndexedDB to let users read and edit offline and sync later.

## 🟡 Real Example Hindi में
Flipkart Lite (2015) भारत के धीमे नेटवर्क के लिए बनी पहली बड़ी PWAs में से थी — app shell, service worker cache, offline; case study में ~3 गुना ज़्यादा समय और 40% ज़्यादा re-engagement बताया गया।
Twitter Lite ~1 MB से कम की PWA थी; Starbucks PWA में offline menu देखकर order बनाओ, internet आते ही sync।

---

## 🟠 My Stack Example

### Workbox service worker (Vite + vite-plugin-pwa or plain)
```ts
// sw.ts
import { precacheAndRoute, cleanupOutdatedCaches } from 'workbox-precaching';
import { registerRoute, NavigationRoute } from 'workbox-routing';
import { CacheFirst, NetworkFirst, NetworkOnly, StaleWhileRevalidate } from 'workbox-strategies';
import { ExpirationPlugin } from 'workbox-expiration';
import { BackgroundSyncPlugin } from 'workbox-background-sync';

declare const self: ServiceWorkerGlobalScope;
precacheAndRoute(self.__WB_MANIFEST);           // build-injected list of hashed app-shell assets
cleanupOutdatedCaches();

// HTML navigations: network first (3s timeout), fallback to cached shell/offline page
registerRoute(new NavigationRoute(new NetworkFirst({ cacheName: 'pages', networkTimeoutSeconds: 3 })));

// Images from CDN: cache first, max 200 entries / 30 days
registerRoute(({ request }) => request.destination === 'image',
  new CacheFirst({ cacheName: 'images', plugins: [new ExpirationPlugin({ maxEntries: 200, maxAgeSeconds: 30 * 86400 })] }));

// Menu / catalog API: stale-while-revalidate
registerRoute(({ url }) => url.pathname.startsWith('/api/menu'), new StaleWhileRevalidate({ cacheName: 'api-menu' }));

// Order status API: network first so it's fresh, cached fallback offline
registerRoute(({ url }) => url.pathname.startsWith('/api/orders'), new NetworkFirst({ cacheName: 'api-orders' }));

// Queue failed POSTs (e.g., feedback/review) and retry when online
registerRoute(({ url, request }) => url.pathname === '/api/reviews' && request.method === 'POST',
  new NetworkOnly({ plugins: [new BackgroundSyncPlugin('reviews-queue', { maxRetentionTime: 24 * 60 })] }), 'POST');

self.addEventListener('message', (e) => { if (e.data === 'SKIP_WAITING') self.skipWaiting(); });

// Web Push
self.addEventListener('push', (event) => {
  const data = event.data?.json() ?? {};
  event.waitUntil(self.registration.showNotification(data.title ?? 'Order update', {
    body: data.body, icon: '/icons/192.png', data: { url: data.url },
  }));
});
self.addEventListener('notificationclick', (e) => { e.notification.close(); e.waitUntil(self.clients.openWindow(e.notification.data.url)); });
```

### Register + "update available" prompt (React)
```tsx
import { registerSW } from 'virtual:pwa-register';      // vite-plugin-pwa helper
const updateSW = registerSW({
  onNeedRefresh() { showToast('New version available', { action: 'Refresh', onClick: () => updateSW(true) }); },
  onOfflineReady() { showToast('App ready to work offline'); },
});
```

### manifest.webmanifest
```json
{
  "name": "QuickBite — Food Delivery", "short_name": "QuickBite",
  "start_url": "/?source=pwa", "display": "standalone", "background_color": "#ffffff", "theme_color": "#fc8019",
  "icons": [
    { "src": "/icons/192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

### Offline indicator + IndexedDB outbox (idb-keyval)
```tsx
import { set, get, del, keys } from 'idb-keyval';
export async function sendMessage(msg: { id: string; chatId: string; text: string }) {
  await set(`outbox:${msg.id}`, msg);                            // persist first
  try { await api.post('/messages', msg, { headers: { 'Idempotency-Key': msg.id } }); await del(`outbox:${msg.id}`); }
  catch { /* stays in outbox, UI shows ⏱ pending */ }
}
window.addEventListener('online', async () => {
  for (const k of await keys()) if (String(k).startsWith('outbox:')) await sendMessage((await get(k))!);
});
```

### Node backend: Web Push (VAPID)
```js
import webpush from 'web-push';
webpush.setVapidDetails('mailto:ops@quickbite.in', process.env.VAPID_PUBLIC, process.env.VAPID_PRIVATE);
await webpush.sendNotification(subscriptionFromDb, JSON.stringify({ title: 'Order picked up 🛵', body: 'Arriving in 12 min', url: '/orders/123' }));
```

### Next.js
```
Use @serwist/next (successor of next-pwa) or a custom SW in /public; ensure sw.js has Cache-Control: no-cache.
```

### React Native note
```
Native apps don't need service workers: offline = local DB (SQLite/WatermelonDB/MMKV) + sync queue (M06/M07),
push via FCM/APNs (M10). PWA is the web alternative when a native app is too heavy.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is a service worker and what can it do?**
A1: It's a background script, separate from the page, that acts as a programmable network proxy for its scope. It intercepts fetch requests and can respond from Cache Storage, the network or a combination, which enables offline support, instant app-shell loads and custom caching strategies. It also handles push notifications, background sync and messages from pages. It has no DOM access, can be terminated when idle (so state goes in IndexedDB or caches), and requires HTTPS.

**Q2: Which caching strategy would you use for different resources?**
A2: Hashed static assets and fonts: cache-first or precache. HTML navigations and fresh data such as order status: network-first with a timeout and an offline fallback. Semi-static API data (menus, catalog, avatars): stale-while-revalidate. Payments, auth and other sensitive or non-idempotent requests: network-only, with failed POSTs optionally queued via background sync and idempotency keys. Add expiration limits to runtime caches.

**Q3: How do you handle service worker updates safely?**
A3: Serve `sw.js` with no-cache so the browser detects new versions. Version cache names and clean up old caches in `activate`. Let the new worker wait, notify the user that a new version is available, and on confirmation send SKIP_WAITING and reload, which avoids mixing old pages with new assets. Avoid calling `skipWaiting` blindly. Have a kill-switch plan (deploy a no-op SW that unregisters) for bad releases.

**Q4: How would you make a chat or ordering web app work offline?**
A4: Precache the app shell. Cache recent conversations or menus in IndexedDB and render them instantly. Treat writes optimistically: put them in an IndexedDB outbox with client-generated IDs and show a pending state. Retry via background sync or the online event, using idempotency keys so retries don't duplicate. Reconcile with server responses (ordering, conflicts). Show clear offline and online indicators, and make sure payment flows need connectivity.

**Q5: PWA vs native app — when would you choose each?**
A5: A PWA fits broad reach without installs, small size, instant updates, SEO and shareable URLs, and users on low-storage devices or occasional use (e.g., a lite version for emerging markets). Native fits deep device integration (background location, Bluetooth, advanced camera), best performance and smooth animations, reliable background processing and push on all platforms, app-store presence, and payments or wallet integrations. Many companies run both: a native app for power users and a PWA or lite web app for the long tail.

---

## 🔷 Trade-offs
✅ Offline, instant repeat loads, push, installable without stores, tiny download.
❌ Update/versioning complexity, stale-content bugs, debugging difficulty.
❌ iOS limitations (storage eviction, fewer APIs, background sync unsupported).
❌ Storage quotas & eviction; must design for SW being killed anytime.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Service Worker | Background script / network proxy | पीछे चलने वाली proxy script |
| Cache Storage | SW-controlled response cache | SW का cache |
| App shell | Cached UI skeleton | ऐप का ढाँचा |
| Precache | Cache assets at install | पहले से cache |
| Cache First / Network First | Strategy order | पहले cache / पहले network |
| Stale-While-Revalidate | Serve cache, refresh in background | पुराना दो, पीछे ताज़ा |
| Background Sync | Retry when online | internet आने पर भेजना |
| Web App Manifest | PWA metadata | ऐप की जानकारी file |
| PWA | Installable offline web app | install होने वाली website |
| skipWaiting | Activate new SW immediately | नया SW तुरंत चालू |

---

## ⚡ 3-Line Summary
**English:**
1. A service worker is a background, programmable network proxy: install (precache) → activate (cleanup) → fetch (strategies) + push/sync.
2. Strategies: cache-first for static, network-first for fresh pages/data, SWR for semi-static, network-only for sensitive; outbox + background sync for offline writes.
3. PWA = HTTPS + manifest + SW → installable, offline-capable; handle updates carefully with versioned caches and a refresh prompt.

**Hindi:**
1. Service worker पीछे चलने वाली proxy: install (pre-cache) → activate (सफ़ाई) → fetch (strategies) + push/sync।
2. Static: cache-first; ताज़ा डेटा: network-first; menu: SWR; payment: network-only; offline लिखाई के लिए outbox + sync।
3. PWA = HTTPS + manifest + SW; update सावधानी से — cache version और "Refresh" prompt।

---

## ➡️ Next Topic Suggestion
**F09. State Management (Local vs Global vs Server State)** — Where should data live inside the app? Next: the types of state, when to use useState, Context, Zustand or Redux versus a server-state cache, and how to avoid unnecessary re-renders.
