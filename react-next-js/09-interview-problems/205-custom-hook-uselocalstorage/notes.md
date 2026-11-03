# 205. Build Custom Hook — useLocalStorage
# हिंदी में: Custom Hook — useLocalStorage बनाना

> Code: [useLocalStorage.js](./useLocalStorage.js) (complete, tested with jsdom: updater function, persistence, cross-tab storage event)

---

## 🔵 Simple Definition (English)
**useLocalStorage** is a custom hook that works like `useState` but also saves the value in the browser's `localStorage`. The value survives refresh and can sync between tabs.

## 🔵 सरल परिभाषा (Hindi)
**useLocalStorage** एक custom hook है जो `useState` जैसा चलता है पर value को browser के `localStorage` में भी save करता है। Value refresh के बाद भी बचती है और tabs के बीच sync हो सकती है।

---

## 🔴 Problem it Solves
Plain `useState` forgets everything on refresh. Writing `localStorage.getItem/setItem` by hand in every component leads to repeated code, JSON parsing bugs, crashes on the server (`window is not defined`) and errors when storage is full or blocked (private mode). One hook handles all of it.

## 🔴 यह क्यों बना? (Hindi)
साधारण `useState` refresh पर सब भूल जाता है। हर component में हाथ से `localStorage.getItem/setItem` लिखने से code दोहराता है, JSON parsing के bugs आते हैं, server पर crash होता है (`window is not defined`), और storage भरा या blocked (private mode) होने पर errors आते हैं। एक hook यह सब संभाल लेता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → read(key, fallback): returns fallback on the server, on missing key or on bad JSON
Step 2 → useState(() => read(...)) lazy init: reads storage once, on first render only
Step 3 → set(next) accepts a value or an updater function (prev => next), like useState
Step 4 → set writes JSON.stringify(next) to localStorage inside try/catch
Step 5 → useEffect adds a window "storage" listener; it fires in OTHER tabs when the key changes
Step 6 → The listener updates state; cleanup removes the listener

Re-render: set → state change → component re-renders once. A change in another tab → storage
event → setValue → re-render. Same-tab components do NOT get the storage event.
Performance: localStorage is synchronous and blocks the main thread, so keep values small
(a few KB), and never write on every keystroke without debouncing.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → read(key, fallback): server पर, key न होने पर या खराब JSON पर fallback लौटाता है
Step 2 → useState(() => read(...)) lazy init: storage सिर्फ पहले render में एक बार पढ़ता है
Step 3 → set(next) value या updater function (prev => next) लेता है, useState की तरह
Step 4 → set try/catch के अंदर JSON.stringify(next) को localStorage में लिखता है
Step 5 → useEffect window का "storage" listener जोड़ता है; key बदलने पर यह DUSRE tabs में fire होता है
Step 6 → Listener state अपडेट करता है; cleanup listener हटाता है

Re-render: set → state बदली → component एक बार re-render। दूसरे tab में बदलाव → storage
event → setValue → re-render। उसी tab के components को storage event नहीं मिलता।
Performance: localStorage synchronous है और main thread रोकता है, इसलिए values छोटी रखो
(कुछ KB), और debounce किए बिना हर keystroke पर मत लिखो।
```

---

## 🟡 Real World Example
**Flipkart language / recently viewed:** you pick Hindi and the choice is remembered on your next visit. "Recently viewed items" also persists. If you open Flipkart in two tabs and change the language in one, the other tab updates too, thanks to the `storage` event.

## 🟡 Real Example Hindi mein
**Flipkart की language / recently viewed:** आप Hindi चुनते हो और अगली visit पर भी वही याद रहती है। "Recently viewed items" भी बचे रहते हैं। दो tabs में Flipkart खोलकर एक में language बदलो तो दूसरा tab भी बदल जाता है, `storage` event की वजह से।

---

## 💻 Code Example — Basic

```jsx
// Basic: persist a string, no SSR handling
import { useState, useEffect } from 'react';               // hooks

function useLocalStorage(key, initial) {
  const [value, setValue] = useState(() => {               // lazy init: runs once
    const saved = localStorage.getItem(key);               // read the saved string
    return saved ? JSON.parse(saved) : initial;            // parse or use default
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));      // save after every change
  }, [key, value]);

  return [value, setValue];                                // same shape as useState
}

// const [lang, setLang] = useLocalStorage('lang', 'en');
```

## 💻 Code Example — Advanced

```jsx
// Production version (useLocalStorage.js): SSR safe, try/catch, updater fn, cross-tab sync
import { useState, useEffect, useCallback } from 'react';

function read(key, initialValue) {
  if (typeof window === 'undefined') return initialValue;   // server render
  try {
    const raw = window.localStorage.getItem(key);
    return raw === null ? initialValue : JSON.parse(raw);
  } catch { return initialValue; }                          // corrupt JSON or blocked storage
}

export function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => read(key, initialValue));

  const set = useCallback((next) => {
    setValue((prev) => {
      const resolved = typeof next === 'function' ? next(prev) : next; // updater support
      try { window.localStorage.setItem(key, JSON.stringify(resolved)); }
      catch { /* quota exceeded / private mode: keep it in memory */ }
      return resolved;
    });
  }, [key]);

  useEffect(() => {
    const onStorage = (e) => {                              // other tabs only
      if (e.key !== key) return;
      setValue(e.newValue === null ? initialValue : JSON.parse(e.newValue));
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  return [value, set];
}
```

Note: this simple version has a hydration issue in SSR (see the Next.js section). A side effect
(`setItem`) inside the state updater is tolerated here, but strictly updaters should be pure:
for stricter code, write storage in `useEffect([value])` instead.

---

## 🟠 Next.js Connection
`localStorage` does not exist on the server. If the hook reads storage in the initial render, the server HTML (default value) and the first client render (stored value) differ, causing a **hydration mismatch**. Safe pattern: render the default first, then read storage in `useEffect` (accept one extra render), or use `useSyncExternalStore` with a server snapshot. For things the server needs (theme, language), use **cookies**, which the server can read.

```jsx
// Hydration-safe variant for Next.js (Client Component)
'use client';
import { useState, useEffect } from 'react';

export function useLocalStorageSSR(key, initial) {
  const [value, setValue] = useState(initial);               // same on server and first client render
  useEffect(() => {
    const saved = window.localStorage.getItem(key);          // read only after hydration
    if (saved !== null) setValue(JSON.parse(saved));         // then update to the stored value
  }, [key]);
  return [value, setValue];                                  // add a write effect as in the basic hook
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `JSON.stringify` / `JSON.parse`
✅ **Correct:** Storage holds strings only

```jsx
// Wrong: saves "[object Object]"
localStorage.setItem('user', { name: 'Asha' });
// Right
localStorage.setItem('user', JSON.stringify({ name: 'Asha' }));
```

❌ **Mistake 2:** Reading storage on every render
✅ **Correct:** Use lazy initial state

```jsx
// Wrong: parses JSON on every render (slow, synchronous)
const [v, setV] = useState(JSON.parse(localStorage.getItem('k')));
// Right: function runs only once
const [v, setV] = useState(() => read('k', null));
```

❌ **Mistake 3:** No try/catch around storage and parse
✅ **Correct:** Wrap both

```jsx
// Wrong: crashes the app if JSON is corrupted or storage is blocked
const v = JSON.parse(localStorage.getItem('k'));
// Right: try { ... } catch { return fallback; }
```

---

## 🧠 Tricky Interview Question

```jsx
// Two components in the SAME tab
function A() { const [n, setN] = useLocalStorage('count', 0); return <button onClick={() => setN(n + 1)}>{n}</button>; }
function B() { const [n] = useLocalStorage('count', 0); return <p>{n}</p>; }
```
**Answer:** Clicking the button in `A` updates `localStorage`, but `B` does **not** update. The browser's `storage` event fires only in *other* documents (other tabs), never in the tab that made the change. Each hook call also has its own state. To sync within a tab, dispatch a custom event after `setItem` and listen for it, or lift the state to context, or use `useSyncExternalStore` with a shared subscription.

---

## ⚫ Interview Questions + Answers

Q1: Why use a function in `useState(() => read(...))`?
A1: Lazy initialisation runs the function only on the first render. Without it, `localStorage` would be read and parsed on every render.

Q2: When does the `storage` event fire?
A2: When storage is changed from a different document with the same origin (another tab or window). It does not fire in the tab that made the change.

Q3: localStorage vs sessionStorage vs cookies?
A3: `localStorage` persists until cleared and is per-origin; `sessionStorage` lasts for the tab session; cookies are sent to the server with each request and can be read in SSR. Never store secrets or tokens in `localStorage` (readable by any script, so XSS can steal them).

Q4: What is the storage limit and what happens when it is exceeded?
A4: About 5 MB per origin in most browsers (browser-dependent). `setItem` throws a `QuotaExceededError`, so wrap it in try/catch.

Q5: How do you avoid hydration errors in Next.js?
A5: Make the first client render match the server (render the default), then read storage in `useEffect`, or use `useSyncExternalStore` with a `getServerSnapshot`, or read from cookies on the server.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Saving small preferences (theme, language, filters, drafts)
- Data that only the browser needs

❌ **Avoid when:**
- Storing sensitive data like tokens or personal information
- The server needs the value on first render (use cookies)
- Large or structured data (use IndexedDB)

---

## 📊 Visual Diagram

```
   first render ─► read(key) ─► useState(value)
                                  │
   setValue(x) ───────────────────┼──► localStorage.setItem(key, JSON)
                                  │
   Tab A writes ──► [storage event, Tab B only] ──► Tab B setValue ──► re-render

   Server render:  window undefined ─► initialValue   (must match first client render!)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| localStorage | Persistent key-value browser storage | Browser का स्थायी key-value storage |
| Lazy initial state | `useState(fn)` runs fn once | useState में function, एक बार चलता है |
| storage event | Fired in other tabs on change | दूसरे tabs में बदलाव पर fire होने वाला event |
| Serialisation | Converting objects to strings (JSON) | Objects को strings में बदलना |
| Hydration | React attaching to server HTML | Server HTML से React का जुड़ना |
| QuotaExceededError | Storage full error | Storage भरने की error |
| XSS | Injected script attack | Injected script वाला attack |

---

## ⚡ 3-Line Summary
**English:**
1. `useLocalStorage` is `useState` plus JSON persistence, with lazy init and try/catch safety.
2. The `storage` event syncs other tabs, but not the same tab.
3. In Next.js render the default first and read storage after mount, or use cookies for server-needed values.

**Hindi:**
1. `useLocalStorage` मतलब `useState` के साथ JSON persistence, lazy init और try/catch सुरक्षा।
2. `storage` event दूसरे tabs को sync करता है, उसी tab को नहीं।
3. Next.js में पहले default render करो और mount के बाद storage पढ़ो, या server की ज़रूरत वाली values के लिए cookies इस्तेमाल करो।

---

## ➡️ Next Topic
**206. Build Custom Hook — useDebounce** — अब timing की practice: search box में हर keystroke पर API न बुलाकर रुकने के बाद एक बार बुलाना।
