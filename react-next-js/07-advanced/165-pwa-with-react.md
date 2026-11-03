# 165. PWA with React
# हिंदी में: PWA with React — Web App को Installable और Offline बनाना

---

## 🔵 Simple Definition (English)
A **Progressive Web App (PWA)** is a website that behaves like an installed app: it can be added to the home screen, work offline and send push notifications. It needs HTTPS, a web app manifest and a service worker.

## 🔵 सरल परिभाषा (Hindi)
**Progressive Web App (PWA)** ऐसी website है जो installed app जैसा व्यवहार करती है: home screen पर add हो सकती है, offline चल सकती है और push notifications भेज सकती है। इसके लिए HTTPS, web app manifest और service worker चाहिए।

---

## 🔴 Problem it Solves

Users on slow or unstable networks (metro, villages, 3G) get a blank page when the connection drops. Building a full native app only for "installable plus offline" is expensive and users must go to the store and download 50 MB. A PWA keeps one web codebase, loads fast from cache, can be installed from the browser in one tap and still works when the network is gone. Flipkart Lite (2015) was an early well-known PWA in India, and reported better engagement and time spent than their earlier mobile web.

## 🔴 यह क्यों बना? (Hindi)
धीमे या अस्थिर network पर (metro, गाँव, 3G) connection टूटते ही user को blank page दिखता है। सिर्फ "install और offline" के लिए पूरा native app बनाना महंगा है और user को store जाकर 50 MB download करना पड़ता है। PWA में एक ही web codebase रहता है, cache से तेज़ load होता है, browser से एक tap में install हो जाता है और network न होने पर भी चलता है। Flipkart Lite (2015) भारत का शुरुआती जाना-माना PWA था, जिसने पहले की mobile web से बेहतर engagement बताई थी।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Serve the site over HTTPS (localhost is allowed for development)
Step 2 → Add manifest.json: name, icons, start_url, display: "standalone", theme_color
Step 3 → Link it in the HTML: <link rel="manifest" href="/manifest.json" />
Step 4 → Register a service worker (JS file that runs in a separate thread, between page and network)
Step 5 → In the worker's install event, pre-cache the app shell (HTML, JS, CSS, icons)
Step 6 → In the fetch event, answer requests from cache or network (a caching strategy)
Step 7 → Browser sees manifest + service worker and offers "Install app" / "Add to Home screen"
Step 8 → Updates: a new worker installs in the background and activates after old tabs close (or skipWaiting)

Common strategies: cache-first (static files), network-first (API data), stale-while-revalidate (balance)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Site को HTTPS पर serve करो (development में localhost चलता है)
Step 2 → manifest.json जोड़ो: name, icons, start_url, display: "standalone", theme_color
Step 3 → HTML में link करो: <link rel="manifest" href="/manifest.json" />
Step 4 → Service worker register करो (अलग thread में चलने वाली JS file, page और network के बीच)
Step 5 → Worker के install event में app shell (HTML, JS, CSS, icons) pre-cache करो
Step 6 → fetch event में requests का जवाब cache या network से दो (caching strategy)
Step 7 → Browser को manifest + service worker दिखते हैं तो "Install app" / "Add to Home screen" देता है
Step 8 → Updates: नया worker background में install होता है और पुराने tabs बंद होने पर (या skipWaiting से) active होता है

आम strategies: cache-first (static files), network-first (API data), stale-while-revalidate (संतुलित)
```

---

## 🟡 Real World Example
**Swiggy/Zomato lite web on a weak network:** The user opens the restaurant page in the metro. The app shell (header, bottom nav, skeletons) loads instantly from cache. The last viewed menu is shown from cache while fresh data loads. If the user places an order offline, the order is saved in IndexedDB and sent when the network returns (background sync, where supported). On Android Chrome the user can install it to the home screen and it opens full screen without the browser bar.

## 🟡 Real Example Hindi mein
**कमज़ोर network पर Swiggy/Zomato lite web:** User metro में restaurant page खोलता है। App shell (header, bottom nav, skeletons) cache से तुरंत load हो जाता है। आखिरी देखा हुआ menu cache से दिखता है जबकि नया data load होता है। Offline में order करने पर वह IndexedDB में save होता है और network आने पर भेज दिया जाता है (background sync, जहाँ supported हो)। Android Chrome में user इसे home screen पर install कर सकता है और यह browser bar के बिना full screen खुलता है।

---

## 💻 Code Example — Basic

```jsx
// Basic PWA setup in a Vite + React app (no libraries). Three files: manifest, worker, registration.

// File: public/manifest.json
// {
//   "name": "Food Order App",            // full name shown on install prompt
//   "short_name": "FoodApp",             // name under the home screen icon
//   "start_url": "/",                    // page that opens on launch
//   "display": "standalone",             // hides the browser UI
//   "background_color": "#ffffff",       // splash screen background
//   "theme_color": "#fc8019",            // browser toolbar colour
//   "icons": [
//     { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
//     { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
//   ]
// }

// File: public/sw.js (the service worker: plain JavaScript, no JSX)
const CACHE = 'shell-v1';                                    // cache name; bump the version to invalidate
const SHELL = ['/', '/index.html', '/icon-192.png'];         // files needed to show the app offline

self.addEventListener('install', event => {                  // runs once when the worker installs
  event.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL))); // pre-cache the app shell
});

self.addEventListener('activate', event => {                 // runs when the worker takes control
  event.waitUntil(
    caches.keys().then(keys =>                               // list all caches
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))) // delete old versions
    )
  );
});

self.addEventListener('fetch', event => {                    // runs for every network request
  if (event.request.method !== 'GET') return;                // only cache GET requests
  event.respondWith(
    caches.match(event.request).then(hit => hit || fetch(event.request)) // cache-first, else network
  );
});

// File: src/registerSW.js: call this from main.jsx
export function registerSW() {
  if ('serviceWorker' in navigator) {                        // feature detection (not all browsers)
    window.addEventListener('load', () => {                  // register after the page loads
      navigator.serviceWorker.register('/sw.js')             // path must be at the scope you want to control
        .then(reg => console.log('SW registered:', reg.scope)) // success log
        .catch(err => console.error('SW failed:', err));       // e.g. not on HTTPS
    });
  }
}
```

## 💻 Code Example — Advanced

```jsx
// Advanced: install prompt hook + online/offline status + update-ready banner in React
import { useState, useEffect, useCallback } from 'react';

// Hook 1: capture the browser's install prompt so you can show your own "Install" button
export function useInstallPrompt() {
  const [promptEvent, setPromptEvent] = useState(null);       // stores the deferred event
  useEffect(() => {
    const handler = e => {
      e.preventDefault();                                      // stop the mini-infobar, we show our own UI
      setPromptEvent(e);                                       // keep the event for later
    };
    window.addEventListener('beforeinstallprompt', handler);   // Chromium browsers only (not Safari)
    return () => window.removeEventListener('beforeinstallprompt', handler); // cleanup
  }, []);
  const install = useCallback(async () => {
    if (!promptEvent) return;                                  // nothing to show yet
    promptEvent.prompt();                                      // open the native install dialog
    await promptEvent.userChoice;                              // wait for accepted/dismissed
    setPromptEvent(null);                                      // the event can be used only once
  }, [promptEvent]);
  return { canInstall: !!promptEvent, install };               // UI uses these two values
}

// Hook 2: online/offline state with the built-in React 18 hook for external stores
import { useSyncExternalStore } from 'react';
function subscribe(cb) {                                       // tell React when the status changes
  window.addEventListener('online', cb);
  window.addEventListener('offline', cb);
  return () => {
    window.removeEventListener('online', cb);
    window.removeEventListener('offline', cb);
  };
}
export function useOnlineStatus() {
  return useSyncExternalStore(
    subscribe,                                                 // subscribe function
    () => navigator.onLine,                                    // client snapshot
    () => true                                                 // server snapshot (assume online during SSR)
  );
}

// Hook 3: detect that a new service worker is waiting, so the user can refresh
export function useSWUpdate() {
  const [waiting, setWaiting] = useState(null);                // the waiting worker, if any
  useEffect(() => {
    if (!('serviceWorker' in navigator)) return;               // unsupported browser
    navigator.serviceWorker.getRegistration().then(reg => {
      if (!reg) return;
      if (reg.waiting) setWaiting(reg.waiting);                // already waiting
      reg.addEventListener('updatefound', () => {              // a new worker started installing
        const w = reg.installing;
        w?.addEventListener('statechange', () => {
          if (w.state === 'installed' && navigator.serviceWorker.controller) setWaiting(w); // update ready
        });
      });
    });
  }, []);
  const update = () => {
    waiting?.postMessage({ type: 'SKIP_WAITING' });            // worker must listen and call skipWaiting()
    window.location.reload();                                  // load the new version
  };
  return { updateReady: !!waiting, update };
}

// UI that uses all three
export function PwaBar() {
  const online = useOnlineStatus();                            // re-renders only when status changes
  const { canInstall, install } = useInstallPrompt();
  const { updateReady, update } = useSWUpdate();
  return (
    <div>
      {!online && <p role="status">You are offline. Showing saved data.</p>}
      {canInstall && <button onClick={install}>Install app</button>}
      {updateReady && <button onClick={update}>New version available. Refresh</button>}
    </div>
  );
}
```

---

## 🟠 Next.js Connection

Next.js has built-in support for the manifest through the App Router file `app/manifest.js` (or `manifest.json`), and you can put `sw.js` in `public/`. For a full offline setup people use libraries like `@ducanh2912/next-pwa` or Serwist (Workbox-based) (version-dependent: libraries change, check current docs). Caution: server-rendered pages cached by a service worker can show stale data, so choose strategies per route. Push notifications are also documented in the Next.js PWA guide.

```jsx
// app/manifest.js (Next.js 14/15 App Router): generates /manifest.webmanifest
export default function manifest() {
  return {
    name: 'Food Order App',                       // full app name
    short_name: 'FoodApp',                        // home screen label
    start_url: '/',                               // launch URL
    display: 'standalone',                        // app-like window
    background_color: '#ffffff',
    theme_color: '#fc8019',
    icons: [
      { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
      { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
    ],
  };
}
```

```jsx
// app/components/RegisterSW.jsx: register the worker from a Client Component
'use client';                                      // useEffect needs the browser
import { useEffect } from 'react';
export default function RegisterSW() {
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js', { scope: '/' }); // file lives in public/sw.js
    }
  }, []);
  return null;                                     // renders nothing, only a side effect
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Caching HTML and API responses forever (users never see updates)
✅ **Correct:** Version your cache names, delete old caches in `activate`, and use network-first for data

```jsx
// Wrong: cache-first for everything, including /api/orders
caches.match(req).then(hit => hit || fetch(req));

// Right: network-first for API, fall back to cache when offline
fetch(req).then(res => {
  const copy = res.clone();                            // a response body can be read only once
  caches.open('api-v1').then(c => c.put(req, copy));   // update the cache
  return res;
}).catch(() => caches.match(req));                     // offline fallback
```

❌ **Mistake 2:** Caching POST/PUT requests or authenticated personal data in a shared cache
✅ **Correct:** Only cache safe GET requests, and never cache sensitive user data

```jsx
// Wrong
cache.put(postRequest, response);   // ❌ Cache API rejects POST, and personal data must not be stored

// Right
if (event.request.method !== 'GET') return;   // ✅ skip non-GET
```

❌ **Mistake 3:** Registering the service worker in development and getting stuck with a stale app
✅ **Correct:** Register only in production, and use DevTools "Update on reload" / "Unregister" while testing

```jsx
// Wrong: always registers
navigator.serviceWorker.register('/sw.js');

// Right: only in production builds
if (process.env.NODE_ENV === 'production' && 'serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
```

---

## 🧠 Tricky Interview Question

```jsx
// sw.js version 1 is live. You deploy version 2 (CACHE = 'shell-v2') and a user refreshes the page once.
// Which version does the page run?
self.addEventListener('install', e => { e.waitUntil(caches.open('shell-v2')); });
```
**Answer:** The user still sees **version 1**. The new worker installs but goes into the **waiting** state, because the old worker still controls the open tab. It activates only after all tabs of the site are closed, or when the new worker calls `self.skipWaiting()` (and the page may then call `clients.claim()` or reload). A simple refresh does not replace the worker, because the refreshed page is still controlled by the old worker during the navigation. This is why PWAs show an "update available" banner, as in our `useSWUpdate` hook.

---

## ⚫ Interview Questions + Answers

Q1: What makes a web app a PWA?
A1: HTTPS, a web app manifest (name, icons, start_url, display) and a service worker. With these, browsers can offer installation. Offline support and push notifications come from the service worker and extra APIs.

Q2: What is a service worker?
A2: A JavaScript file that runs in a background thread, separate from the page, with no DOM access. It sits between the page and the network, so it can intercept fetches, cache responses, handle push events and background sync.

Q3: Name common caching strategies.
A3: Cache-first (static assets), network-first (fresh data with offline fallback), stale-while-revalidate (show cache immediately, update in the background), network-only and cache-only. Choose per resource type.

Q4: What are PWA limits compared with native apps?
A4: Less access to device features (varies by browser and OS), weaker push support on iOS than Android (version-dependent: it improved in recent iOS versions), storage can be evicted by the browser, and there is less store discoverability.

Q5: How do you add PWA features to a Next.js app?
A5: Add `app/manifest.js`, icons, and a service worker in `public/` (hand-written or through Serwist/next-pwa), register it from a Client Component, and design cache strategies so server-rendered pages do not become stale.

---

## 🔷 When to Use + When Not to Use
✅ **Use a PWA when:**
- Users are on poor networks and need fast repeat loads and offline basics
- You want an installable experience without app store work
- One web team must cover web and light mobile needs

❌ **Avoid a PWA when:**
- You need deep native features (Bluetooth profiles, background location, heavy graphics)
- iOS push or storage limits would break your core feature
- Your content is fully dynamic and offline gives no value

---

## 📊 Visual Diagram

```
   Browser tab (React app)
        │  fetch('/menu')
        ▼
   ┌──────────────────┐
   │  Service Worker   │  ← runs in separate thread, intercepts requests
   └───┬──────────┬───┘
       │          │
  cache hit?     miss
       ▼          ▼
   ┌────────┐  ┌─────────┐
   │ Cache   │  │ Network │
   │ Storage │  │ (server)│
   └────────┘  └─────────┘

   Install flow:  manifest.json + SW + HTTPS → browser shows "Install" → icon on home screen

   Re-render behavior: React re-renders only when state changes (e.g. useOnlineStatus flips).
   Performance impact: cached shell gives near-instant repeat loads; large caches cost storage.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| PWA | Installable, offline-capable web app | Install होने वाला, offline चलने वाला web app |
| Manifest | JSON describing app name, icons, display | App का नाम, icons, display बताने वाली JSON |
| Service worker | Background script that intercepts requests | Requests रोकने वाली background script |
| App shell | Minimal UI cached for instant load | Instant load के लिए cached minimal UI |
| Cache Storage | Browser API to store responses | Responses store करने वाला browser API |
| Stale-while-revalidate | Serve cache, refresh in background | Cache दिखाओ, background में refresh करो |
| beforeinstallprompt | Event to trigger custom install UI | Custom install UI का event |
| Background sync | Retry requests when online again | Online आने पर requests दोबारा भेजना |

---

## ⚡ 3-Line Summary
**English:**
1. A PWA is a website with HTTPS, a manifest and a service worker, making it installable and offline-capable.
2. The service worker caches the app shell and chooses a strategy (cache-first, network-first, stale-while-revalidate).
3. In Next.js use `app/manifest.js` plus a registered worker, and plan updates so users do not get stale versions.

**Hindi:**
1. PWA ऐसी website है जिसमें HTTPS, manifest और service worker होता है, जिससे वह installable और offline-capable बनती है।
2. Service worker app shell cache करता है और strategy चुनता है (cache-first, network-first, stale-while-revalidate)।
3. Next.js में `app/manifest.js` और registered worker इस्तेमाल करो, और updates की योजना रखो ताकि users को पुराना version न दिखे।

---

## ➡️ Next Topic
**167. Next.js vs React** — अब हम Next.js सेक्शन शुरू करते हैं: plain React (CRA/Vite) और Next.js framework में exactly क्या फ़र्क है और क्यों कंपनियाँ Next.js चुनती हैं। (166 पहले से मौजूद है।)
