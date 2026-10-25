# 03. Node.js vs Browser JavaScript
# हिंदी में: Node.js vs Browser JavaScript

---

## 🔵 Simple Definition (English)
Node.js and browser JavaScript both run the **same JavaScript language** (ES2023+ syntax), but in completely different environments. The browser gives you `window`, `document`, DOM APIs, and sandboxed security; Node.js gives you `process`, `fs`, `http`, OS-level access, and no DOM at all.

## 🔵 सरल परिभाषा (Hindi)
Node.js और browser JavaScript दोनों **same JavaScript language** चलाते हैं, लेकिन environment बिल्कुल अलग है। Browser में `window`, `document`, DOM APIs, sandboxed security मिलती है; Node.js में `process`, `fs`, `http`, OS-level access मिलता है और DOM बिलकुल नहीं।

---

## 🔴 Problem it Solves
Before Node.js, if a team wanted to use JavaScript on the server, there was no runtime — JS only existed embedded in browsers to manipulate pages. Ryan Dahl took V8 (the browser's JS engine) OUT of the browser, stripped away DOM/window, and bolted on system-level APIs (file, network, process) — creating a new, separate runtime. Understanding this split is critical because many bugs and interview mistakes come from treating Node and browser code as interchangeable.

## 🔴 यह क्यों बना? (Hindi)
Node.js से पहले JavaScript सिर्फ browser के अंदर pages manipulate करने के लिए था — server पर चलाने का कोई runtime नहीं था। Ryan Dahl ने V8 (browser का JS engine) को browser से बाहर निकाला, DOM/window हटाया, और system-level APIs (file, network, process) जोड़े — एक नया runtime बनाया। यह अंतर समझना ज़रूरी है क्योंकि कई bugs तब होती हैं जब लोग Node और browser code को एक जैसा मान लेते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Both environments embed the **V8 engine** (or similar) to parse/execute JavaScript syntax — the language rules (closures, prototypes, async/await) are identical.
Step 2 → The **global object** differs: browser's is `window`; Node's is `global` (and `globalThis` works in both since ES2020).
Step 3 → Browser exposes **Web APIs** (DOM, `fetch`, `localStorage`, `document.querySelector`) — these don't exist in Node.
Step 4 → Node exposes **system APIs** (`fs`, `path`, `os`, `process`, `net`) — these don't exist in browsers (for security — a website can't read your hard disk).
Step 5 → Module systems differ historically: Node defaults to **CommonJS** (`require`/`module.exports`), browsers natively support **ES Modules** (`import`/`export` with `<script type="module">`); modern Node supports both.
Step 6 → Security model differs: browser JS runs in a sandbox (can't access files, limited network via CORS); Node JS runs with the permissions of the OS user executing it (full file/network access unless restricted).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → दोनों environments **V8 engine** embed करते हैं — language rules (closures, prototypes, async/await) बिल्कुल same हैं।
Step 2 → **Global object** अलग है: browser में `window`; Node में `global` (और ES2020 से दोनों में `globalThis` काम करता है)।
Step 3 → Browser **Web APIs** देता है (DOM, `fetch`, `localStorage`) — ये Node में नहीं हैं।
Step 4 → Node **system APIs** देता है (`fs`, `path`, `os`, `process`, `net`) — security कारणों से browser में नहीं हैं।
Step 5 → Module systems अलग: Node default `CommonJS` (`require`/`module.exports`); browser native `ES Modules` (`import`/`export`); modern Node दोनों support करता है।
Step 6 → Security model अलग: browser JS sandbox में चलता है (files access नहीं कर सकता, CORS से network limited); Node JS OS user की permission से चलता है (full file/network access जब तक restrict न करें)।

---

## 🟡 Real World Example
**Paytm wallet app:** The React frontend (browser JS) reads `localStorage` for a cached user session and calls `fetch('/api/balance')`. The Node.js backend (same language!) handling `/api/balance` uses `fs` to read a config file, `crypto` to verify a signed JWT, and `pg` to query PostgreSQL directly — none of which the frontend could ever do, because a browser sandbox deliberately blocks direct file/DB access for security.

## 🟡 Real Example Hindi mein
**Paytm wallet app:** React frontend (browser JS) `localStorage` से cached session पढ़ता है और `fetch('/api/balance')` call करता है। Node.js backend (same language!) `/api/balance` handle करते समय `fs` से config file पढ़ता है, `crypto` से JWT verify करता है, और `pg` से directly PostgreSQL query करता है — यह सब frontend कभी नहीं कर सकता, क्योंकि browser sandbox security के लिए direct file/DB access block करता है।

---

## 💻 Code Example — Basic
```javascript
// nodejs-only-demo.js
// Run with: node nodejs-only-demo.js
// These APIs exist ONLY in Node.js, never in a browser

const fs = require('fs');       // file system — no browser equivalent
const os = require('os');       // OS info — no browser equivalent

console.log(typeof window);      // "undefined" — Node has no `window`
console.log(typeof document);    // "undefined" — Node has no `document`
console.log(typeof process);     // "object" — Node-only global
console.log(typeof global);      // "object" — Node's global object (vs browser's `window`)

// Reading the filesystem — impossible in browser JS for security reasons
fs.readdir('.', (err, files) => {
  if (err) return console.error(err);
  console.log('Files in current directory:', files.slice(0, 5));
});

console.log('Hostname:', os.hostname());  // machine name — browser can never know this
```

## 💻 Code Example — Advanced
```javascript
// isomorphic-code-demo.js
// Shows CODE THAT WORKS IN BOTH environments (pure JS, no env-specific API)
// then shows how to detect which environment you're in — needed for isomorphic libraries

// ─── 1. Pure JS logic — identical behavior in Node and browser ───────────────
function calculateDiscount(price, percent) {
  if (percent < 0 || percent > 100) throw new Error('Invalid percent');
  return Math.round(price - (price * percent) / 100);
}
console.log(calculateDiscount(1000, 20)); // 800 — works everywhere

// ─── 2. Environment detection pattern (used by libraries like axios, lodash) ──
const isNode = typeof process !== 'undefined' &&
               process.versions != null &&
               process.versions.node != null;

const isBrowser = typeof window !== 'undefined' &&
                   typeof window.document !== 'undefined';

console.log('Running in Node?', isNode);
console.log('Running in browser?', isBrowser);

// ─── 3. Conditional API usage based on environment (isomorphic storage) ──────
function getStorageAdapter() {
  if (isBrowser) {
    return {
      get: (key) => window.localStorage.getItem(key),
      set: (key, val) => window.localStorage.setItem(key, val),
    };
  }
  if (isNode) {
    const fs = require('fs');
    const STORE_FILE = './.node-storage.json';
    return {
      get: (key) => {
        try {
          const data = JSON.parse(fs.readFileSync(STORE_FILE, 'utf8'));
          return data[key];
        } catch { return null; }
      },
      set: (key, val) => {
        let data = {};
        try { data = JSON.parse(fs.readFileSync(STORE_FILE, 'utf8')); } catch {}
        data[key] = val;
        fs.writeFileSync(STORE_FILE, JSON.stringify(data));
      },
    };
  }
  throw new Error('Unknown environment');
}

const storage = getStorageAdapter();
storage.set('lastUser', 'rahul@paytm.com');
console.log('Stored value:', storage.get('lastUser'));
```

---

## 🟠 Express.js Integration
```javascript
// Express (Node) server serving a static HTML page that runs browser JS
const express = require('express');
const path = require('path');
const app = express();

// Server-side (Node) code — has fs/path access, no window/document
app.get('/api/user/:id', (req, res) => {
  // Direct DB-style logic — a browser could NEVER do this safely
  res.json({ id: req.params.id, name: 'Rahul Sharma', wallet: 450 });
});

// Serve static files — the browser JS inside these files has NO fs/process access
app.use(express.static(path.join(__dirname, 'public')));
// public/app.js (browser-side) can only do:
//   fetch('/api/user/1').then(r => r.json()).then(data => {
//     document.getElementById('name').textContent = data.name; // DOM — Node can't do this
//   });

app.listen(3000, () => console.log('Server (Node.js side) running on :3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `window` or `document` in Node.js code (common when copy-pasting frontend utility code to backend)
```javascript
// Wrong — crashes with "window is not defined"
function getQueryParam(name) {
  return new URLSearchParams(window.location.search).get(name);
}

// Correct — Node has no window; parse from req.url or process.argv instead
function getQueryParam(req, name) {
  const url = new URL(req.url, `http://${req.headers.host}`);
  return url.searchParams.get(name);
}
```

❌ Mistake 2: Trying to use `require()` directly in browser `<script>` tags
```javascript
// Wrong — browsers don't understand CommonJS natively
const _ = require('lodash'); // ReferenceError: require is not defined

// Correct — use a bundler (Webpack/Vite) to convert require/import for browser,
// or use native ES modules with <script type="module">
import _ from 'lodash';
```

---

## 🧠 Tricky Interview Question

```javascript
// File: test.js, run with: node test.js
console.log(this);
```
Answer: In Node.js, at the top level of a CommonJS module, `this` refers to `module.exports` (an empty object `{}` initially) — NOT the global object, unlike a browser's top-level script where `this` refers to `window`. This is because Node wraps every module file in a function: `(function(exports, require, module, __filename, __dirname) { ... })`, and `this` inside that wrapper is bound to `module.exports`.

---

## ⚫ Interview Questions + Answers

Q1: Can you use `fetch()` in Node.js?
A1: Yes, since Node.js 18, `fetch` is available globally (built on `undici`) without any import — before that, you needed packages like `node-fetch` or `axios`. It behaves similarly to browser `fetch` but without CORS restrictions.

Q2: Why doesn't Node.js have a DOM?
A2: Because Node.js runs on the server with no rendering surface — there's no "page" to represent as a DOM tree. DOM is a browser-specific concept for representing and manipulating HTML visually.

Q3: What is `globalThis` and why was it introduced?
A3: `globalThis` is a standardized way (ES2020) to access the global object regardless of environment — `window` in browsers, `global` in Node, `self` in Web Workers. It lets library authors write environment-agnostic code without `typeof window !== 'undefined'` checks everywhere.

Q4: Is CommonJS (`require`) available in the browser?
A4: Not natively. Browsers only understand ES Modules (`import`/`export`) or plain scripts. Tools like Webpack, Browserify, or esbuild transform `require()` calls into browser-compatible bundles.

Q5: Why can Node.js access the file system but browser JS cannot?
A5: Security. If arbitrary websites could read your local files, every webpage could steal your documents, passwords, photos, etc. Browsers deliberately sandbox JS away from the OS. Node.js, by contrast, is meant to run trusted server-side code, so it's given full OS-level access by design.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Writing shared/isomorphic business logic (validation, calculations) that must run identically on client and server
- Building libraries meant to work in both environments (detect with `typeof window`/`typeof process`)

❌ Avoid when:
- Assuming any browser Web API (DOM, `localStorage`, `window`) is available in a Node.js backend, or vice-versa with Node-only APIs (`fs`, `process`) in frontend bundles

---

## 📊 Visual Diagram
```
SAME LANGUAGE, DIFFERENT WORLDS
─────────────────────────────────────────────────────
        JavaScript (ES2023+ syntax, same everywhere)
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
   BROWSER JS                   NODE.JS
  ┌──────────────┐           ┌──────────────┐
  │ window        │           │ global       │
  │ document      │           │ process       │
  │ DOM APIs      │           │ fs, path, os  │
  │ fetch, CORS   │           │ http, net     │
  │ localStorage  │           │ require/CJS   │
  │ Sandboxed     │           │ Full OS access│
  └──────────────┘           └──────────────┘
      Engine: V8                Engine: V8 + libuv
      (Chrome)                  (standalone runtime)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| DOM | Document Object Model, browser's page representation | Browser का page representation |
| window | Browser's global object | Browser का global object |
| global | Node's global object | Node का global object |
| CommonJS | Node's default module system (`require`) | Node का default module system |
| ES Modules | Native JS module system (`import`/`export`) | Native JS module system |
| Sandbox | Restricted execution environment (security) | Security के लिए restricted environment |
| Isomorphic code | Code that runs in both Node and browser | Node और browser दोनों में चलने वाला code |

---

## ⚡ 3-Line Summary
English:
1. Node.js and browsers both run JavaScript via V8, but give you completely different global objects and APIs — Node has no DOM, browsers have no file system access.
2. Node adds `process`, `fs`, `os`, `http` and defaults to CommonJS modules; browsers add `window`, `document`, DOM APIs, and natively use ES Modules.
3. Writing isomorphic code requires feature-detecting the environment (`typeof window`/`typeof process`) rather than assuming any specific API exists.

Hindi:
1. Node.js और browser दोनों V8 से JavaScript चलाते हैं, पर global objects और APIs पूरी तरह अलग हैं — Node में DOM नहीं, browser में file system access नहीं।
2. Node `process`, `fs`, `os`, `http` देता है और default CommonJS modules use करता है; browser `window`, `document`, DOM APIs देता है और native ES Modules use करता है।
3. Isomorphic code लिखने के लिए environment detect करना ज़रूरी है (`typeof window`/`typeof process`), किसी specific API के होने की उम्मीद मत रखो।

---

## ➡️ Next Topic
**04. V8 Engine — How it Works** — Dive deeper into the engine both environments share, and how it compiles/executes JavaScript so fast.
