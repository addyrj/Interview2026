# 29. Script Tag (defer vs async)
# हिंदी में: Script Tag — defer और async में फर्क

---

## 🔵 Simple Definition (English)
`<script>` loads and runs JavaScript. A plain script **blocks HTML parsing** while it downloads and executes. `async` downloads in parallel and runs **as soon as ready** (any order). `defer` downloads in parallel and runs **after the HTML is parsed**, in order.

## 🔵 सरल परिभाषा (Hindi)
`<script>` JavaScript load और run करता है। साधारण script download और execute होते समय **HTML parsing रोक देता है**। `async` parallel download करता है और **तैयार होते ही** चल जाता है (कोई भी order)। `defer` parallel download करता है और **HTML parse होने के बाद**, order में चलता है।

---

## 🔴 Problem it Solves
```
PROBLEM with a normal <script src="app.js"> in <head>:
  1. Parser STOPS at the script.
  2. Downloads app.js (network wait).
  3. Executes it.
  4. Only then continues parsing the rest of HTML.
  -> User stares at a blank page. Slow First Contentful Paint.

OLD WORKAROUND: put every script at the end of <body>.
  - Works, but the download starts late (parser must reach the bottom first).

MODERN FIX: defer / async in <head> -> download starts EARLY without blocking.
```

## 🔴 यह क्यों बना? (Hindi)
```
<head> में साधारण <script src="app.js"> की समस्या:
  1. Parser script पर रुक जाता है।
  2. app.js download होने तक इंतज़ार (network)।
  3. फिर execute।
  4. उसके बाद ही बाकी HTML parse होता है।
  -> User को खाली page दिखता है। First Contentful Paint slow।

पुराना जुगाड़: सारे scripts <body> के अंत में रखना।
  - चलता है, पर download देर से शुरू होता है।

आधुनिक हल: <head> में defer / async -> download जल्दी शुरू और parsing भी नहीं रुकती।
```

---

## 🟢 How it Works — Step by Step

```
TIMELINES (P = HTML parsing, D = download, E = execute):

 NORMAL     P───┤ D═══ E ├───P───────
                 (parser paused for download AND execution)

 ASYNC      P───────────────┤ E ├────P──
              D═══════╝       (download parallel; execution PAUSES parser when ready)

 DEFER      P─────────────────────────┤ E ├
              D═══════╝                 (download parallel; run after parsing, before
                                         DOMContentLoaded)

RULES:
  defer
    - Only for external scripts (src). Ignored on inline scripts.
    - Executes in DOCUMENT ORDER (a.js before b.js, always).
    - Runs before DOMContentLoaded. DOM is fully available.
  async
    - Runs whenever ready: ORDER NOT GUARANTEED. Can run before DOM is complete.
    - Good for independent scripts: analytics, ads.
  type="module"
    - Deferred by default! (can also add async)
    - Strict mode, import/export, own scope.
  nomodule  -> fallback for browsers without ES modules (legacy).
  Dynamic: document.createElement('script') is async by default.

WHICH TO USE:
  Your app code that needs the DOM or depends on other scripts  -> defer
  Independent third-party (Google Analytics, ads)               -> async
  Tiny inline critical script that must run immediately         -> plain inline
```

## 🟢 कैसे काम करता है? (Hindi)

```
Timeline (P = HTML parsing, D = download, E = execute):

 NORMAL : parse रुकता है download के लिए भी और execute के लिए भी।
 ASYNC  : download parallel; तैयार होते ही execute (उस समय parsing रुकती है)।
 DEFER  : download parallel; parsing पूरी होने के बाद execute।

नियम:
  defer: सिर्फ external scripts पर। Document के order में चलता है।
         DOMContentLoaded से पहले चलता है, DOM पूरा मिलता है।
  async: जब तैयार तब चलता है, order की guarantee नहीं। Analytics/ads जैसे
         independent scripts के लिए।
  type="module": by default deferred होता है।

कौन सा कब:
  आपका app code (DOM चाहिए / एक-दूसरे पर निर्भर) -> defer
  Independent third-party (Analytics, ads)         -> async
```

---

## 🟡 Real World Example
**Amazon / Flipkart product page:** the main app bundle uses `defer` (needs the DOM and runs in order), while the Google Analytics / Tag Manager snippet and ad scripts use `async` because they are independent and should never delay the page. **Swiggy** loads its heavy React bundle with `defer`/module so the restaurant list HTML can be painted first. A script that wrongly blocks in `<head>` is a classic reason Lighthouse reports "Eliminate render-blocking resources".

## 🟡 Real Example Hindi mein
**Amazon / Flipkart product page:** main app bundle `defer` से चलता है (DOM चाहिए, order ज़रूरी), जबकि Google Analytics / Tag Manager और ad scripts `async` होते हैं क्योंकि वो independent हैं और page को कभी रोकने नहीं चाहिए। **Swiggy** अपना भारी React bundle `defer`/module से लोड करता है ताकि restaurant list का HTML पहले दिख जाए। `<head>` में गलती से blocking script होना Lighthouse के "Eliminate render-blocking resources" warning का आम कारण है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>defer vs async</title>
  <link rel="stylesheet" href="style.css">

  <!-- ❌ BAD in head: blocks parsing. (kept commented for comparison)
  <script src="blocking.js"></script> -->

  <!-- ✅ defer: runs after HTML is parsed, in order. 'inline' module below simulates files -->
  <script defer>
    /* NOTE: defer is ignored on inline scripts (no src), so this runs IMMEDIATELY.
       This is the classic trap. Look at the console order. */
    console.log('1. inline script with defer attr (runs immediately, defer ignored)');
  </script>

  <!-- ✅ module scripts are deferred automatically (inline modules too) -->
  <script type="module">
    console.log('2. module script (deferred: DOM is ready)');
    document.getElementById('status').textContent = 'Module ran after parsing: DOM available';
  </script>

  <!-- ✅ external defer/async examples (real CDN files, harmless) -->
  <script defer src="https://cdn.jsdelivr.net/npm/dayjs@1/dayjs.min.js"></script>
  <script async src="https://cdn.jsdelivr.net/npm/lodash@4/lodash.min.js"></script>
</head>
<body>
  <h1>Script loading demo</h1>
  <p id="status">Waiting...</p>
  <p id="log"></p>

  <script>
    // Plain inline script at end of body: DOM above is available
    console.log('3. inline script at end of body');
    document.addEventListener('DOMContentLoaded', function () {
      console.log('4. DOMContentLoaded (deferred + module scripts have already run)');
      // dayjs was deferred, so it exists now. Show it.
      document.getElementById('log').textContent =
        typeof dayjs === 'function' ? 'dayjs loaded: ' + dayjs().format('YYYY-MM-DD') : 'dayjs not loaded (offline?)';
    });
  </script>
</body>
</html>
```

```css
/* style.css */
*, *::before, *::after { box-sizing: border-box; }
body { font-family: system-ui, sans-serif; padding: 24px; background: #f6f7f9; color: #222; }
#status { padding: 12px; background: #e3f2fd; border-radius: 8px; }
#log { padding: 12px; background: #e8f5e9; border-radius: 8px; }
```

Open DevTools console and Network tab. The cheat table:

```
attribute        download   execute when             order kept   blocks parser
-------------    --------   ----------------------   ----------   -------------
(none)           sync       immediately              yes          YES
async            parallel   as soon as downloaded    NO           only while running
defer            parallel   after parsing done       YES          no
type="module"    parallel   after parsing (deferred)  yes          no
```

---

## 🟠 React/Next.js Connection

```jsx
// Next.js: use next/script instead of raw <script>; 'strategy' maps to the same ideas
import Script from "next/script";

export default function Layout({ children }) {
  return (
    <>
      {children}
      {/* afterInteractive (default): load after page becomes interactive. Good for analytics */}
      <Script src="https://www.googletagmanager.com/gtag/js?id=G-XXXX" strategy="afterInteractive" />
      {/* lazyOnload: load during idle time. Chat widgets, low priority */}
      <Script src="https://widget.example.com/chat.js" strategy="lazyOnload" />
      {/* beforeInteractive: critical (e.g. consent/bot detection); only valid in root layout */}
      {/* worker: experimental (Partytown), offloads to web worker */}
    </>
  );
}
```
- Next.js and Vite bundlers output your app bundle as `<script type="module">` or `defer`, so you normally do not hand-write these.
- In plain React (Create React App era), the script was at the end of body; in Vite, `<script type="module" src="/src/main.jsx">` is deferred automatically.
- Hydration cost is why shipping less JS (code-splitting, Server Components) matters beyond just defer/async.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `async` and `defer`?
A1: Both download in parallel. `async` executes immediately when downloaded, order not guaranteed, may run before the DOM is ready. `defer` executes after HTML parsing is done, in document order, before `DOMContentLoaded`.

Q2: Where should script tags go?
A2: Today: in `<head>` with `defer` (download starts early, no blocking). Old approach: end of `<body>`. Use `async` for independent third-party scripts.

Q3: Do module scripts need `defer`?
A3: No. `type="module"` is deferred by default. Adding `async` to a module makes it run as soon as its dependencies are ready.

Q4: What happens if two `async` scripts depend on each other?
A4: Race condition: whichever downloads first runs first, so a dependent script can fail with "X is not defined". Use `defer` (ordered) or modules with imports.

Q5: What does `defer` do on an inline script?
A5: Nothing. `defer` and `async` only apply to scripts with `src` (and module scripts for async). Inline classic scripts execute immediately.

---

## 🔷 Common Mistakes to Avoid
❌ Mistake 1: `<script src="app.js">` (no attribute) in `<head>`, which blocks rendering.
✅ Correct way: Add `defer` (or use `type="module"`).

❌ Mistake 2: Using `async` for scripts that depend on each other (jQuery + plugin).
✅ Correct way: Use `defer` so order is preserved.

❌ Mistake 3: Using `defer` on inline scripts.
✅ Correct way: Move code to an external file, or use `DOMContentLoaded` listener / `type="module"`.

❌ Mistake 4: Using both `async` and `defer`, assuming order is kept.
✅ Correct way: `async` wins in modern browsers; `defer` is only a fallback for very old ones. Choose one.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Parser-blocking | Script stops HTML parsing | Parsing रोकने वाला script |
| async | Run when ready, any order | तैयार होते ही चलाओ |
| defer | Run after parsing, in order | Parsing के बाद, order में |
| DOMContentLoaded | HTML parsed and deferred scripts ran | DOM तैयार होने का event |
| type="module" | ES module, deferred by default | ES module |
| Render-blocking | Delays first paint | First paint रोकना |
| next/script strategy | Next.js loading policy | Next.js में loading तरीका |
| Hydration | React attaches JS to server HTML | Server HTML में JS जोड़ना |

---

## ⚡ 3-Line Summary
English: Plain scripts block HTML parsing; `async` and `defer` download in parallel to avoid that.
`defer` runs after parsing in order (use for app code); `async` runs ASAP in any order (use for analytics).
Module scripts are deferred by default; `defer` is ignored on inline scripts.

Hindi: साधारण scripts HTML parsing रोकते हैं; `async` और `defer` parallel download करके इसे रोकते हैं।
`defer` parsing के बाद order में चलता है (app code के लिए); `async` जल्दी, किसी भी order में (analytics के लिए)।
Module scripts by default deferred होते हैं; inline scripts पर `defer` बेअसर है।

---

## ➡️ Next Topic
**30. HTML Template Tag** — JavaScript से बार-बार HTML बनाने का सही तरीका: `<template>` जो page में दिखता नहीं पर clone हो सकता है।

---
