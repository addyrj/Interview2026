# 40. Cross-Browser Compatibility
# हिंदी में: Cross-Browser Compatibility — हर Browser में एक जैसा चलना

---

## 🔵 Simple Definition (English)
Cross-browser compatibility means your site looks and works acceptably in all target browsers (Chrome, Safari, Firefox, Edge) and devices. Browsers implement standards at different speeds and have quirks, so you check support (caniuse, MDN), use fallbacks, prefixes via tooling, polyfills, and test on real browsers.

## 🔵 सरल परिभाषा (Hindi)
Cross-browser compatibility का मतलब है कि आपकी site सभी target browsers (Chrome, Safari, Firefox, Edge) और devices पर ठीक दिखे और चले। Browsers standards अलग-अलग गति से लागू करते हैं और उनके अपने quirks होते हैं, इसलिए support check करना (caniuse, MDN), fallback, tooling से prefixes, polyfills और असली browsers पर testing ज़रूरी है।

---

## 🔴 Problem it Solves
```
PROBLEM:
  - Feature works in Chrome, breaks in Safari (e.g. 100vh on iOS, date input UI)
  - Form controls look different in every browser
  - New CSS (subgrid, :has(), container queries) not in older versions
  - Vendor prefixes: -webkit-, -moz- needed for some properties

HISTORY:
  - Internet Explorer era: separate code for IE6/7/8
  - Today: evergreen browsers (auto-update) but Safari iOS lags and
    older Android WebViews/corporate browsers still exist

COST OF IGNORING: lost customers (iOS Safari is ~ a quarter of mobile traffic)
```

## 🔴 यह क्यों बना? (Hindi)
```
समस्या:
  - Feature Chrome में चलता है, Safari में टूटता है (जैसे iOS पर 100vh)
  - Form controls हर browser में अलग दिखते हैं
  - नया CSS (subgrid, :has(), container queries) पुराने versions में नहीं
  - कुछ properties के लिए -webkit-, -moz- prefix चाहिए

इतिहास: IE के समय हर version के लिए अलग code।
आज: browsers auto-update होते हैं, पर iOS Safari और पुराने WebView पीछे रहते हैं।

न देखने का नुकसान: iOS users खो सकते हैं।
```

---

## 🟢 How it Works — Step by Step

```
WORKFLOW:

1. DEFINE TARGETS
   - Check analytics: which browsers do YOUR users use?
   - Write a browserslist: "> 0.5%, last 2 versions, not dead"

2. CHECK SUPPORT
   - caniuse.com, MDN "Browser compatibility" table, web.dev Baseline
   - "Baseline" = feature works in all latest major browsers

3. WRITE STANDARD CODE FIRST
   - Use HTML5 semantic elements and standard CSS/JS

4. HANDLE GAPS
   a) Fallback in CSS (old value first, new value after)
   b) @supports feature queries
   c) Autoprefixer (PostCSS): adds -webkit- etc. from browserslist
   d) Polyfills / transpile: Babel + core-js for older JS syntax/APIs
   e) CSS reset / normalize.css to unify defaults

5. TEST
   - Real devices + BrowserStack/LambdaTest, Safari (iOS) is a must
   - Playwright can run Chromium, Firefox, WebKit
   - Test: keyboard, zoom, different viewport sizes

COMMON QUIRKS:
  - iOS Safari: 100vh includes address bar -> use 100dvh / svh
  - Input zoom on iOS if font-size < 16px
  - Date/time inputs render differently
  - Flex `gap` / `aspect-ratio` older Safari versions
  - -webkit-appearance, -webkit-tap-highlight-color, -webkit-line-clamp
```

## 🟢 कैसे काम करता है? (Hindi)

```
Workflow:
1. Target तय करो: analytics देखो, browserslist लिखो
   ("> 0.5%, last 2 versions, not dead")
2. Support जाँचो: caniuse.com, MDN compatibility table, Baseline
3. पहले standard code लिखो (semantic HTML, standard CSS)
4. Gaps भरो:
   a) CSS में पहले पुरानी value, बाद में नई
   b) @supports
   c) Autoprefixer: -webkit- अपने आप जुड़ते हैं
   d) Babel + core-js, polyfills
   e) normalize.css / reset
5. Test: असली devices, BrowserStack, Playwright (Chromium, Firefox, WebKit)

आम quirks: iOS पर 100vh में address bar जुड़ती है (100dvh use करो),
iOS पर input का font-size 16px से कम हो तो zoom होता है।
```

---

## 🟡 Real World Example
**Zomato/Swiggy web on iPhone:** A full-height bottom sheet with `height: 100vh` gets its buttons hidden behind Safari's bottom bar. They use `100dvh` with a `100vh` fallback. The phone number input also uses `font-size: 16px` to stop iOS from auto-zooming. **Amazon** keeps a very old-browser friendly layout alongside the new one, using feature checks for what it enhances.

## 🟡 Real Example Hindi mein
**iPhone पर Zomato/Swiggy web:** `height: 100vh` वाली bottom sheet के buttons Safari की नीचे वाली bar के पीछे छिप जाते थे। हल: `100vh` fallback के साथ `100dvh`। Phone number input में `font-size: 16px` रखा जाता है ताकि iOS अपने आप zoom न करे। **Amazon** पुराने browsers के लिए भी चलने वाला layout रखता है और नई चीज़ें feature checks से जोड़ता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cross-Browser Techniques</title>
  <style>
    /* 1. Unify defaults (mini reset) */
    *, *::before, *::after { box-sizing: border-box; }
    body { margin: 0; font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }

    /* 2. Fallback then modern viewport unit (unsupported line is ignored) */
    .sheet {
      min-height: 100vh;     /* fallback: older browsers */
      min-height: 100dvh;    /* modern: accounts for mobile browser bars */
      background: #e3f2fd;
      padding: 16px;
    }

    /* 3. Prefixed + standard property: put the standard LAST */
    .clamp {
      display: -webkit-box;              /* older WebKit/Blink/Firefox need this form */
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;             /* max 2 lines */
      line-clamp: 2;                     /* standard (newer) */
      overflow: hidden;
      max-width: 320px;
    }

    /* 4. Feature query: use grid only where supported */
    .gallery { display: flex; flex-wrap: wrap; gap: 8px; }
    .gallery div { flex: 1 1 120px; background: #ffe0b2; padding: 24px; text-align: center; }
    @supports (display: grid) {
      .gallery { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); }
    }

    /* 5. Form controls: normalize look */
    input, button, select, textarea { font: inherit; }          /* inherit font instead of browser default */
    input[type="text"], input[type="tel"] {
      font-size: 16px;                    /* prevents iOS auto-zoom on focus */
      padding: 10px; border: 1px solid #999; border-radius: 6px;
      -webkit-appearance: none; appearance: none;  /* remove native styling */
    }

    /* 6. Remove iOS tap flash */
    a, button { -webkit-tap-highlight-color: transparent; }

    /* 7. Use :focus-visible only where supported, fall back to :focus */
    button:focus { outline: 2px solid #1976d2; }
    button:focus:not(:focus-visible) { outline: none; }
    button:focus-visible { outline: 2px solid #1976d2; outline-offset: 2px; }

    /* 8. Respect user's motion setting */
    @media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
  </style>
</head>
<body>
  <main class="sheet">
    <h1>Cross-browser demo</h1>
    <p class="clamp">This long text is limited to two lines using the line-clamp technique which still needs the -webkit- prefix in several browsers, so we add both versions for safety. Resize the window and see it stay at two lines.</p>

    <input type="tel" placeholder="Phone number">
    <button>Continue</button>

    <section class="gallery">
      <div>1</div><div>2</div><div>3</div><div>4</div>
    </section>
  </main>

  <script>
    // JS feature detection + simple fallback (no browser sniffing)
    if (!('IntersectionObserver' in window)) {
      console.log('Fallback: load all images immediately');
    }
    // CSS.supports lets JS ask the same question as @supports
    console.log('Grid supported:', CSS.supports('display', 'grid'));
  </script>
</body>
</html>
```

```js
// postcss.config.js - Autoprefixer reads browserslist and adds prefixes
module.exports = { plugins: { autoprefixer: {} } };
// package.json: "browserslist": ["> 0.5%", "last 2 versions", "not dead"]
```

---

## 🟠 React/Next.js Connection

```jsx
// Next.js already ships with PostCSS + Autoprefixer and SWC (transpiles
// modern JS using your browserslist). Tailwind uses PostCSS too.

// 1. Set targets in package.json:
// "browserslist": ["chrome >= 100", "safari >= 15", "firefox >= 100"]

// 2. Feature check inside effect (never on server, window does not exist):
import { useEffect, useState } from 'react';

function LazyImg({ src, alt }) {
  const [ready, setReady] = useState(false);
  useEffect(() => {
    if (!('IntersectionObserver' in window)) setReady(true); // fallback
  }, []);
  return <img src={ready ? src : undefined} loading="lazy" alt={alt} />;
}

// 3. Tailwind arbitrary support: dvh fallback
<div className="min-h-screen min-h-[100dvh]" />

// 4. Test across engines with Playwright (playwright.config.ts):
// projects: [{ name: 'chromium' }, { name: 'firefox' }, { name: 'webkit' }]
```

---

## ⚫ Interview Questions + Answers

**Q1: What is cross-browser compatibility and how do you ensure it?**
A1: The site works well across target browsers. Ensure it by defining a browser support matrix, using standards, checking caniuse/MDN, adding fallbacks, `@supports`, Autoprefixer, Babel/polyfills, a CSS reset, and testing on real browsers/devices, especially Safari on iOS.

**Q2: What are vendor prefixes and do we still need them?**
A2: Prefixes (`-webkit-`, `-moz-`, `-ms-`) were used for experimental features. Today few are needed (e.g. `-webkit-line-clamp`, `-webkit-appearance`, `-webkit-backdrop-filter` on older Safari). Do not write them by hand; Autoprefixer adds what your browserslist needs.

**Q3: Polyfill vs transpiler?**
A3: A transpiler (Babel) rewrites new syntax (arrow functions, optional chaining) into older syntax. A polyfill adds missing runtime APIs (e.g. `Promise`, `Array.prototype.at`) using JS. Syntax cannot be polyfilled; APIs cannot be transpiled.

**Q4: How do you handle a CSS feature not supported in some browsers?**
A4: Provide a fallback declaration before the new one, wrap enhancements in `@supports`, or use progressive enhancement so the base layout works without it. Check Baseline status before depending on it.

**Q5: Why does `100vh` break on mobile and what is the fix?**
A5: On mobile, `100vh` is computed with the browser toolbars hidden, so the element is taller than the visible area. Use `100dvh` (dynamic viewport height), or `100svh` for the small viewport, with `100vh` as a fallback.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Testing only in Chrome
✅ **Correct way:** Test Chrome, Safari (iOS), Firefox and Edge; use BrowserStack or Playwright (WebKit).

❌ **Mistake 2:** Prefix after the standard property
```css
/* WRONG: prefixed overrides standard */
.a { border-radius: 8px; -webkit-border-radius: 2px; }
/* CORRECT: standard last */
.a { -webkit-appearance: none; appearance: none; }
```

❌ **Mistake 3:** Using new features without checking support
✅ **Correct way:** Open MDN's compatibility table / caniuse and decide with `@supports` or a fallback.

❌ **Mistake 4:** Browser sniffing via userAgent
✅ **Correct way:** Feature detection (`'x' in window`, `CSS.supports`).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Vendor prefix | Browser-specific property prefix | Browser-विशेष prefix |
| Autoprefixer | Tool that adds prefixes | Prefix अपने आप जोड़ने वाला tool |
| browserslist | List of target browsers | Target browsers की सूची |
| Polyfill | JS that adds missing API | Missing API जोड़ने वाला JS |
| Transpile | Convert new syntax to old | नया syntax -> पुराना |
| caniuse | Browser support database | Support देखने की site |
| Baseline | Works in all major browsers | सब major browsers में चलने वाला |
| Evergreen browser | Auto-updating browser | खुद update होने वाला browser |
| @supports | CSS feature query | CSS feature जाँच |

---

## ⚡ 3-Line Summary
**English:**
1. Define target browsers, write standard code, and check support on MDN/caniuse before using a feature.
2. Close gaps with fallbacks, `@supports`, Autoprefixer, Babel and polyfills; never use browser sniffing.
3. Test on real browsers, especially iOS Safari; Next.js and Tailwind already include PostCSS and Autoprefixer.

**Hindi:**
1. Target browsers तय करो, standard code लिखो, feature use करने से पहले MDN/caniuse देखो।
2. Gaps के लिए fallback, `@supports`, Autoprefixer, Babel और polyfills; browser sniffing नहीं।
3. असली browsers पर test करो, खासकर iOS Safari; Next.js और Tailwind में PostCSS और Autoprefixer पहले से हैं।

---

## ➡️ Next Topic
**41. Web Accessibility (WCAG Guidelines)** — अब सीखें कि site हर इंसान के लिए usable कैसे बने: contrast, keyboard, screen readers।
