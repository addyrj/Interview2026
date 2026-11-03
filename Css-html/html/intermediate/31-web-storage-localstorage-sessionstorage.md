# 31. Web Storage (localStorage, sessionStorage)
# हिंदी में: Web Storage — Browser में Data सहेजना

---

## 🔵 Simple Definition (English)
Web Storage lets a website save **key-value string pairs inside the browser**. `localStorage` persists until you clear it (survives closing the browser). `sessionStorage` lasts only for that **tab session** and is wiped when the tab closes. Both are per-origin, synchronous, and about 5 MB.

## 🔵 सरल परिभाषा (Hindi)
Web Storage से website browser के अंदर **key-value string जोड़ियाँ** सहेज सकती है। `localStorage` तब तक रहता है जब तक आप clear न करें (browser बंद करने पर भी)। `sessionStorage` सिर्फ उस **tab के session** तक रहता है और tab बंद होते ही मिट जाता है। दोनों per-origin, synchronous और लगभग 5 MB के होते हैं।

---

## 🔴 Problem it Solves
```
BEFORE Web Storage, the only client-side storage was COOKIES:
  - Only ~4 KB per cookie.
  - Sent to the server with EVERY request (wastes bandwidth).
  - Clumsy API: document.cookie = "a=1; path=/; expires=..." (string parsing).

WITH Web Storage:
  - ~5 MB per origin, NEVER sent automatically to the server.
  - Clean API: setItem / getItem / removeItem.
  - Perfect for UI preferences (theme, language), draft text, cart for guests.
```

## 🔴 यह क्यों बना? (Hindi)
```
Web Storage से पहले client-side storage सिर्फ COOKIES थीं:
  - हर cookie सिर्फ ~4 KB।
  - हर request के साथ server को अपने-आप जाती थीं (bandwidth बर्बाद)।
  - अजीब API: document.cookie = "a=1; path=/; expires=..." (string parsing)।

Web Storage के साथ:
  - ~5 MB प्रति origin, server को अपने-आप कभी नहीं जाता।
  - साफ API: setItem / getItem / removeItem।
  - UI preferences (theme, language), draft text, guest cart के लिए बिल्कुल सही।
```

---

## 🟢 How it Works — Step by Step

```
API (same for both):
  localStorage.setItem('theme', 'dark');     // save
  localStorage.getItem('theme');             // 'dark'  (or null if missing)
  localStorage.removeItem('theme');          // delete one
  localStorage.clear();                      // delete ALL for this origin
  localStorage.length;  localStorage.key(0); // iterate

VALUES ARE ALWAYS STRINGS:
  localStorage.setItem('n', 5);  ->  stored "5"
  localStorage.setItem('user', {a:1}) -> "[object Object]"  (BUG!)
  Correct: JSON.stringify(obj) to save, JSON.parse(str) to read.

DIFFERENCES:
                    localStorage              sessionStorage
  lifetime          until cleared             until TAB closes
  scope             all tabs, same origin     ONE tab only (even same URL in new tab = separate)
  survives reload   yes                       yes
  survives restart  yes                       no

SCOPE = ORIGIN (protocol + host + port): https://a.com cannot read https://b.com
        and http://a.com is different from https://a.com.

'storage' EVENT: when another tab changes localStorage, this tab gets a 'storage' event
  (not fired in the tab that made the change). Use it to sync login/logout across tabs.

LIMITS / GOTCHAS:
  - ~5 MB; setItem throws QuotaExceededError when full -> wrap in try/catch.
  - SYNCHRONOUS: heavy use blocks the main thread. For big data use IndexedDB.
  - Not available on the server (SSR): `window` / `localStorage` is undefined in Node.
  - Private/incognito and blocked-cookie modes may throw or be cleared on close.
  - NOT secure: any JavaScript on the page (including an XSS attacker) can read it.
    Do NOT store passwords or long-lived auth tokens here.
```

## 🟢 कैसे काम करता है? (Hindi)

```
API (दोनों में एक जैसी):
  setItem(key, value) | getItem(key) | removeItem(key) | clear() | length | key(i)

Values हमेशा STRING होती हैं:
  object सहेजना हो तो JSON.stringify(), पढ़ते समय JSON.parse()।

फर्क:
  localStorage: जब तक clear न हो; सभी tabs में share (same origin)।
  sessionStorage: सिर्फ उसी tab तक; tab बंद = data खत्म; हर tab का अलग।

Scope = origin (protocol + host + port)। https://a.com का data https://b.com नहीं पढ़ सकता।

'storage' event: दूसरे tab में localStorage बदले तो इस tab को event मिलता है
(login/logout को tabs में sync करने के लिए)।

सावधानी: ~5 MB limit, synchronous (भारी use से UI अटकती है), server (SSR) पर नहीं मिलता,
और सुरक्षित नहीं: page का कोई भी JS (XSS attacker भी) इसे पढ़ सकता है।
Password या लंबे समय वाले auth token यहाँ न रखें।
```

---

## 🟡 Real World Example
**Swiggy / Zomato:** your selected delivery location and language, and the guest cart before login, are saved in `localStorage`, so they are still there when you reopen the site tomorrow. **YouTube / Instagram web** remember dark mode and muted preference. **Amazon-style multi-step checkout:** a form wizard may use `sessionStorage` so the half-filled step data survives a refresh but disappears once the tab is closed (and does not leak to another tab). **Gmail** keeps unsent compose drafts locally as an extra safety net.

## 🟡 Real Example Hindi mein
**Swiggy / Zomato:** आपकी चुनी हुई delivery location, language और login से पहले का guest cart `localStorage` में रहता है, इसलिए कल दोबारा खोलने पर भी मिलता है। **YouTube / Instagram web** dark mode और mute preference याद रखते हैं। **Amazon जैसा multi-step checkout:** form wizard `sessionStorage` use कर सकता है ताकि refresh पर आधा भरा data बचे पर tab बंद होते ही मिट जाए (और दूसरे tab में leak न हो)। **Gmail** unsent drafts को अतिरिक्त सुरक्षा के लिए locally भी रखता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Web Storage Demo</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main class="page" id="app">
    <h1>Web Storage</h1>

    <!-- 1. Theme saved in localStorage (persists across restarts) -->
    <section>
      <h2>1. Theme (localStorage)</h2>
      <button id="themeBtn">Toggle dark mode</button>
    </section>

    <!-- 2. Visit counters: local = all time, session = this tab -->
    <section>
      <h2>2. Counters</h2>
      <p>Total page opens (localStorage): <strong id="total">0</strong></p>
      <p>Opens in this tab (sessionStorage): <strong id="tab">0</strong></p>
    </section>

    <!-- 3. Draft note autosave with JSON -->
    <section>
      <h2>3. Draft autosave (JSON)</h2>
      <textarea id="note" rows="3" placeholder="Type, then refresh the page..."></textarea>
      <button id="clearBtn">Clear saved data</button>
    </section>

    <!-- 4. Cross-tab sync using the storage event -->
    <p id="sync" class="sync">Open this page in 2 tabs and change the theme.</p>
  </main>

  <script>
    // Safe wrapper: storage can throw (private mode, quota, blocked)
    const store = {
      get(key, fallback) {
        try {
          const raw = localStorage.getItem(key);
          return raw === null ? fallback : JSON.parse(raw);   // parse string -> value
        } catch (e) { return fallback; }
      },
      set(key, value) {
        try { localStorage.setItem(key, JSON.stringify(value)); }  // value -> string
        catch (e) { console.warn('Storage failed', e); }
      }
    };

    // 1. THEME
    const body = document.body;
    function applyTheme(t) { body.dataset.theme = t; }
    applyTheme(store.get('theme', 'light'));
    document.getElementById('themeBtn').addEventListener('click', () => {
      const next = body.dataset.theme === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      store.set('theme', next);
    });

    // 2. COUNTERS (stored as strings, so convert with Number())
    const total = Number(localStorage.getItem('opens') || 0) + 1;
    localStorage.setItem('opens', total);
    const tab = Number(sessionStorage.getItem('tabOpens') || 0) + 1;
    sessionStorage.setItem('tabOpens', tab);
    document.getElementById('total').textContent = total;
    document.getElementById('tab').textContent = tab;

    // 3. DRAFT
    const note = document.getElementById('note');
    note.value = store.get('draft', { text: '' }).text;
    note.addEventListener('input', () => store.set('draft', { text: note.value, savedAt: Date.now() }));
    document.getElementById('clearBtn').addEventListener('click', () => {
      localStorage.clear(); sessionStorage.clear(); note.value = '';
    });

    // 4. CROSS-TAB SYNC: fires in OTHER tabs only
    window.addEventListener('storage', (e) => {
      if (e.key === 'theme') {
        applyTheme(JSON.parse(e.newValue));
        document.getElementById('sync').textContent = 'Theme synced from another tab!';
      }
    });
  </script>
</body>
</html>
```

```css
/* style.css */
*, *::before, *::after { box-sizing: border-box; }

/* Theme through CSS variables, switched by data-theme on body */
body { --bg: #f6f7f9; --fg: #222; --card: #fff;
       margin: 0; font-family: system-ui, sans-serif; background: var(--bg); color: var(--fg);
       transition: background .2s, color .2s; }
body[data-theme="dark"] { --bg: #121212; --fg: #eee; --card: #1e1e1e; }

.page { max-width: 560px; margin: 0 auto; padding: 24px 16px; }
section { background: var(--card); padding: 16px; border-radius: 12px; margin-bottom: 16px; }
textarea { width: 100%; padding: 8px; border-radius: 6px; border: 1px solid #888;
           background: var(--bg); color: var(--fg); margin-bottom: 8px; }
button { padding: 8px 14px; border: 0; border-radius: 6px; background: #e23744; color: #fff; cursor: pointer; }
.sync { font-size: 14px; opacity: .8; }
```

---

## 🟠 React/Next.js Connection

```jsx
"use client";
import { useState, useEffect } from "react";

// Reusable hook. IMPORTANT for Next.js: localStorage does not exist during SSR.
export function useLocalStorage(key, initial) {
  const [value, setValue] = useState(initial);      // same value on server AND first client render
  const [ready, setReady] = useState(false);

  // read AFTER mount (avoids hydration mismatch)
  useEffect(() => {
    try {
      const raw = localStorage.getItem(key);
      if (raw !== null) setValue(JSON.parse(raw));
    } catch {}
    setReady(true);
  }, [key]);

  // write on change
  useEffect(() => {
    if (ready) localStorage.setItem(key, JSON.stringify(value));
  }, [key, value, ready]);

  return [value, setValue];
}

// Usage
export default function ThemeToggle() {
  const [theme, setTheme] = useLocalStorage("theme", "light");
  return <button onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>Theme: {theme}</button>;
}
```
- Reading `localStorage` in the `useState` initializer in Next.js causes **hydration mismatch** or a `ReferenceError` on the server.
- Libraries: `zustand/middleware` `persist`, `redux-persist`, and `next-themes` (stores theme in localStorage and injects a script to avoid flash).
- Tailwind dark mode: toggle a `dark` class on `<html>` from the stored value.

---

## ⚫ Interview Questions + Answers

Q1: localStorage vs sessionStorage?
A1: Both store ~5 MB of strings per origin. localStorage persists until cleared and is shared across all tabs; sessionStorage lasts for one tab's session and is isolated per tab.

Q2: Can you store objects? Any other types?
A2: Only strings. Serialize with `JSON.stringify` and parse with `JSON.parse`. Functions, Dates (become strings), Maps/Sets do not round-trip without custom handling.

Q3: Is localStorage safe for JWT / auth tokens?
A3: Risky. Any JS on the page, including XSS-injected code, can read it. Prefer `HttpOnly; Secure; SameSite` cookies for session tokens. Use localStorage for non-sensitive preferences.

Q4: Is Web Storage synchronous? What are the consequences?
A4: Yes. Reads/writes block the main thread, so avoid large or frequent writes. For large/structured/async data use IndexedDB. It also is not available in Web Workers or on the server.

Q5: How do you sync state between tabs?
A5: Listen to the `storage` window event, which fires in other same-origin tabs when localStorage changes (not in the originating tab). `BroadcastChannel` is an alternative.

---

## 🔷 Common Mistakes to Avoid
❌ Mistake 1: `localStorage.setItem('user', user)` with an object, saving "[object Object]".
✅ Correct way: `JSON.stringify(user)` and `JSON.parse` on read.

❌ Mistake 2: Storing JWTs/passwords/PII in localStorage.
✅ Correct way: HttpOnly secure cookies for auth; only non-sensitive data in storage.

❌ Mistake 3: Using `localStorage` during SSR (Next.js) at module or render level.
✅ Correct way: Access it in `useEffect` or guard with `typeof window !== 'undefined'`.

❌ Mistake 4: Not handling exceptions and `null`.
✅ Correct way: Wrap in try/catch, use fallback values (`getItem` returns `null`, not `undefined`).

❌ Mistake 5: Assuming booleans/numbers keep their type (`"false"` is truthy!).
✅ Correct way: Convert after reading, or store via JSON.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| localStorage | Persistent key-value store | स्थायी browser storage |
| sessionStorage | Per-tab, session-only store | सिर्फ tab session का storage |
| Origin | Protocol + host + port | Website की पहचान |
| Serialize | Convert object to string | Object को string बनाना |
| `storage` event | Notifies other tabs of changes | दूसरे tabs को बदलाव की सूचना |
| Quota | Max allowed storage size | Storage की सीमा |
| IndexedDB | Async large-data browser DB | बड़े data का async DB |
| Hydration mismatch | Server/client HTML differ | Server और client HTML में फर्क |

---

## ⚡ 3-Line Summary
English: Web Storage keeps string key-value data in the browser: `localStorage` persists, `sessionStorage` dies with the tab.
It is synchronous, ~5 MB, per-origin, and readable by any page script, so never put secrets in it.
Use JSON for objects, `try/catch` for errors, and `useEffect` (not render) in Next.js.

Hindi: Web Storage browser में string key-value data रखता है: `localStorage` स्थायी, `sessionStorage` tab के साथ खत्म।
ये synchronous, ~5 MB, per-origin है और page का कोई भी script इसे पढ़ सकता है, इसलिए secrets न रखें।
Objects के लिए JSON, errors के लिए `try/catch`, और Next.js में render नहीं `useEffect` में use करें।

---

## ➡️ Next Topic
**32. Cookies vs localStorage vs sessionStorage** — तीनों की सीधी तुलना: कब कौन सा, security और server से रिश्ता।

---
