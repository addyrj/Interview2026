# 02. How Browser Executes JavaScript
# हिंदी में: Browser JavaScript को कैसे Execute करता है?

---

## 🔵 Simple Definition (English)
When a browser loads a web page, it parses HTML top-to-bottom. When it finds a `<script>` tag, it **stops parsing HTML**, downloads and executes the JS, then continues. This is called **render-blocking** behavior.

## 🔵 सरल परिभाषा (Hindi)
Browser HTML को ऊपर से नीचे पढ़ता है। जब `<script>` tag मिलता है तो HTML पढ़ना रोककर पहले JS download और execute करता है। इसे render-blocking कहते हैं।

---

## 🔴 Problem it Solves
Without understanding this:
- Your JS runs **before the DOM is ready** → `document.getElementById("btn")` returns `null`
- Large JS files **block page rendering** → white screen for seconds
- Wrong script order → functions not defined yet

## 🔴 यह क्यों बना? (Hindi)
अगर यह समझ न हो तो: JS DOM तैयार होने से पहले चल जाता है और null मिलता है, बड़ी JS file पूरा page रोक देती है, और wrong order में scripts तो functions undefined होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Browser receives HTML from server
Step 2 → HTML Parser starts reading top to bottom
Step 3 → Encounters <script src="app.js">
Step 4 → Parser STOPS (render-blocking)
Step 5 → Browser downloads app.js
Step 6 → JS Engine executes app.js completely
Step 7 → HTML Parser RESUMES from where it stopped
Step 8 → Page finishes rendering
```

### The 3 ways to load scripts

```
1. Normal (render-blocking)
<script src="app.js"></script>
HTML: ──────⬛⬛⬛⬛──────────────────
JS:         ──download──execute──

2. defer (download in parallel, execute after HTML parsed)
<script defer src="app.js"></script>
HTML: ────────────────────────────────
JS:         ──download──────────execute (after HTML done)

3. async (download in parallel, execute immediately when ready)
<script async src="app.js"></script>
HTML: ──────────────⬛⬛──────────────
JS:         ──download──execute (blocks HTML when ready)
```

### Critical Rendering Path
```
HTML → DOM Tree ─┐
                  ├→ Render Tree → Layout → Paint → Display
CSS  → CSSOM    ─┘
JS can modify both DOM and CSSOM → why it can block rendering
```

## 🟢 कैसे काम करता है? (Hindi)
1. Browser server से HTML file पाता है
2. HTML Parser ऊपर से नीचे पढ़ना शुरू करता है
3. `<script>` tag मिलने पर रुक जाता है
4. JS file download होती है, फिर execute होती है
5. JS execute होने के बाद HTML parsing फिर शुरू
6. `defer` लगाने पर JS download parallel होती है पर execute बाद में
7. `async` लगाने पर download parallel, पर execute होते ही HTML रोक देती है

---

## 🟡 Real World Example
**Flipkart/Amazon page load** — अगर आपने `<script>` को `<head>` में रखा बिना `defer` के, तो user को blank page दिखेगा जब तक JS load न हो जाए। इसीलिए बड़े e-commerce sites हमेशा `defer` या scripts को `</body>` से पहले रखते हैं।

**Google Analytics** — `async` use करता है क्योंकि analytics script page render को block नहीं करनी चाहिए। Data थोड़ा बाद में आए तो चलेगा।

## 🟡 Real Example Hindi mein
Flipkart अगर JS को `<head>` में defer के बिना रखे, तो user को सेकंडों तक blank page दिखे। इसलिए scripts body के अंत में या defer के साथ रखते हैं। Google Analytics async है — analytics बाद में load हो तो चलेगा, page पहले दिखे।

---

## 💻 Code Example — Basic
```html
<!DOCTYPE html>
<html>
<head>
  <!-- ❌ WRONG: यह render-block करेगा, DOM ready नहीं -->
  <script>
    // यह line error देगी! #btn अभी exist नहीं करता
    document.getElementById("btn").style.color = "red"; // null error!
  </script>
</head>
<body>
  <button id="btn">Click Me</button>

  <!-- ✅ CORRECT: body के अंत में — DOM ready हो गया -->
  <script>
    // अब #btn exist करता है
    document.getElementById("btn").style.color = "red"; // works!
    console.log("DOM is ready, button found!");
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
```html
<!DOCTYPE html>
<html>
<head>
  <!-- ✅ Best Practice: defer use करो head में -->
  <script defer src="main.js"></script>

  <!-- Analytics: async (non-critical) -->
  <script async src="analytics.js"></script>
</head>
<body>
  <div id="app">Loading...</div>
</body>
</html>
```

```javascript
// main.js — defer के साथ load होगा
// DOM fully parsed होने के बाद run होगा

// DOMContentLoaded: HTML parsed, defer scripts run हो गए
document.addEventListener("DOMContentLoaded", () => {
  console.log("HTML parsed, deferred scripts done"); // सबसे पहले
});

// load: सब कुछ load — images, stylesheets भी
window.addEventListener("load", () => {
  console.log("Everything loaded including images"); // बाद में
});

// Practical example: button safely access करो
const btn = document.getElementById("app");
if (btn) {
  btn.textContent = "App Loaded!";
  btn.style.color = "green";
}

// Script loading order check करना
console.log("main.js executed");
```

```javascript
// analytics.js — async के साथ
// जब download हो जाए तब run होगा, order guaranteed नहीं
console.log("Analytics loaded (async - could run anytime)");

// Page view track करना
function trackPageView() {
  const data = {
    url: window.location.href,  // current URL
    time: new Date().toISOString(), // timestamp
    userAgent: navigator.userAgent  // browser info
  };
  console.log("Tracking:", data);
  // Real में यह server को send होता
}

trackPageView();
```

---

## 🟠 React/Next.js Connection
```jsx
// Next.js में Script component — async/defer automatically handle होता है
import Script from "next/script";

export default function Layout({ children }) {
  return (
    <html>
      <head>
        {/* strategy="afterInteractive" = defer जैसा */}
        <Script
          src="https://analytics.example.com/script.js"
          strategy="afterInteractive"
        />

        {/* strategy="lazyOnload" = page idle होने पर load */}
        <Script
          src="https://chat-widget.example.com/widget.js"
          strategy="lazyOnload"
        />

        {/* strategy="beforeInteractive" = render से पहले (rare) */}
        <Script
          src="https://critical-polyfill.js"
          strategy="beforeInteractive"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}

// React में DOMContentLoaded का equivalent = useEffect
import { useEffect } from "react";

function App() {
  useEffect(() => {
    // Component mount होने पर = DOM ready
    console.log("Component mounted, DOM ready");
    
    // Third-party library initialize करो
    // window.SomeLibrary.init();
  }, []); // [] = only on mount

  return <div>My App</div>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Script को `<head>` में defer/async के बिना रखना
```html
<!-- WRONG: page render block होगा -->
<head>
  <script src="large-library.js"></script>
</head>

<!-- CORRECT: defer use करो -->
<head>
  <script defer src="large-library.js"></script>
</head>
```

❌ **Mistake 2:** DOM element को script execute होने से पहले access करना
```javascript
// WRONG: <head> में script, <body> में element
const btn = document.getElementById("myBtn"); // null!
btn.addEventListener("click", handler); // TypeError: Cannot read properties of null

// CORRECT option 1: DOMContentLoaded wait करो
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("myBtn"); // exists now!
  btn.addEventListener("click", handler);
});

// CORRECT option 2: script defer करो
// <script defer src="app.js"></script>
```

❌ **Mistake 3:** async scripts का order assume करना
```html
<!-- WRONG assumption: order में execute होंगे -->
<script async src="jquery.js"></script>
<script async src="jquery-plugin.js"></script>
<!-- jquery-plugin.js पहले run हो सकता है! jquery load नहीं हुआ होगा तब -->

<!-- CORRECT: dependent scripts के लिए defer use करो -->
<script defer src="jquery.js"></script>
<script defer src="jquery-plugin.js"></script>
<!-- defer: order guaranteed है -->
```

---

## 🧠 Tricky Interview Output Question
```html
<script>console.log("Script 1");</script>
<script defer>console.log("Deferred");</script>
<script>console.log("Script 2");</script>
```
```javascript
// What is the output order?
```
**Answer:**
```
Script 1    ← normal, runs immediately
Script 2    ← normal, runs immediately
Deferred    ← defer: runs after HTML fully parsed
```
**Why:** `defer` scripts always wait for HTML to finish parsing, even if placed before other normal scripts.

---

## ⚫ Interview Questions + Answers

**Q1: What is render-blocking JavaScript?**
A1: When the browser encounters a `<script>` tag without `defer` or `async`, it stops parsing HTML, downloads the JS file, executes it completely, then resumes HTML parsing. During this time the page is blank — this is render-blocking. It's a performance problem for large JS files.

**Q2: What is the difference between defer and async?**
A2: Both download the script in parallel without blocking HTML parsing. The difference is execution timing: `defer` executes after HTML is fully parsed, in order of script appearance, making it safe for DOM access. `async` executes as soon as download finishes, possibly before HTML is done, in no guaranteed order — use for independent scripts like analytics.

**Q3: What is DOMContentLoaded vs load event?**
A3: `DOMContentLoaded` fires when the HTML is fully parsed and deferred scripts have run — the DOM is ready but images/stylesheets may still be loading. `load` fires when everything is fully loaded including images, fonts, and subresources. For DOM manipulation, use `DOMContentLoaded` — it fires much earlier.

**Q4: Why should scripts be placed at the bottom of `<body>`?**
A4: Placing scripts before `</body>` ensures HTML is parsed first, so the DOM is available when JS runs. It also lets the browser render visible content quickly — users see the page before JS loads. Today `defer` is preferred because it achieves the same benefit while keeping scripts in `<head>` (cleaner organization).

**Q5: What is the Critical Rendering Path?**
A5: The sequence of steps browsers take to convert HTML, CSS, and JS into pixels: Parse HTML → DOM, Parse CSS → CSSOM, Combine → Render Tree, Calculate positions → Layout, Draw pixels → Paint. JS can block and modify this path. Minimizing render-blocking JS, deferring non-critical scripts, and inlining critical CSS are key optimizations.

---

## 🔷 Trade-offs / When to Use
✅ Use `defer` when:
- Script needs DOM access
- Script order matters (A depends on B)
- Most scripts in a typical web app

✅ Use `async` when:
- Script is independent (analytics, ads, chat widgets)
- Order doesn't matter
- You want the fastest possible load of non-critical scripts

❌ Avoid normal `<script>` in `<head>` when:
- Script is large
- Script accesses DOM
- Performance matters

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Render-blocking | JS stops page from rendering | JS page render रोक देती है |
| defer | Download parallel, execute after HTML | HTML के बाद execute |
| async | Download parallel, execute when ready | तैयार होते ही execute |
| DOMContentLoaded | HTML parsed event | HTML parse होने का event |
| load | Everything loaded event | सब load होने का event |
| Critical Rendering Path | Steps to show pixels | Pixels दिखाने के steps |
| HTML Parser | Reads HTML, builds DOM | HTML पढ़कर DOM बनाता है |

---

## ⚡ 3-Line Summary
**English:**
1. Browser parses HTML top-to-bottom; a `<script>` tag without `defer/async` blocks parsing until JS finishes.
2. `defer` = download in parallel, execute after HTML parsed (DOM-safe, order guaranteed).
3. `async` = download in parallel, execute immediately when ready (no order guarantee — use for analytics/ads).

**Hindi:**
1. Browser HTML ऊपर से नीचे पढ़ता है; `<script>` बिना defer/async के HTML रोक देता है।
2. `defer` = parallel download, HTML parse के बाद execute — DOM safe, order सही।
3. `async` = parallel download, तैयार होते ही execute — order नहीं, analytics के लिए सही।

---

## ➡️ Next Topic
**03. Variables (var, let, const)** — JavaScript में data store करने के तीन तरीके, इनके scope और behavior अलग क्यों हैं।
