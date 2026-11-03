# 107. CSS Houdini Basics
# हिंदी में: CSS Houdini — Browser की CSS Engine तक Developers की पहुँच

---

## 🔵 Simple Definition (English)
**CSS Houdini** is a set of low-level browser APIs that let developers hook into the CSS engine: define **typed custom properties** (`@property` / `CSS.registerProperty`), draw custom backgrounds with the **Paint API** (`CSS.paintWorklet`), and more. It lets you extend CSS itself instead of waiting for browsers to ship new features.

## 🔵 सरल परिभाषा (Hindi)
**CSS Houdini** low-level browser APIs का समूह है जिनसे developers CSS engine में घुस सकते हैं: **typed custom properties** (`@property` / `CSS.registerProperty`) बनाना, **Paint API** (`CSS.paintWorklet`) से custom backgrounds बनाना, और भी बहुत कुछ। इससे हम नए browser features का इंतज़ार किए बिना CSS को खुद बढ़ा सकते हैं।

---

## 🔴 Problem it Solves
```
BEFORE:
  - New CSS features took years: devs used JS polyfills which run AFTER layout,
    are slow, and cause flicker.
  - Custom properties (--x) are just strings: browser cannot animate them.
        --angle: 0deg  ->  --angle: 360deg   (jumps, no smooth transition!)
  - Cool effects (squircle, noise, ripple) needed images, canvas or extra DOM.

AFTER (Houdini):
  - @property gives a variable a TYPE, so transitions/animations work.
  - Paint API paints a background with code, running in the browser pipeline.
  - Worklets run off the main thread (Animation/Layout worklets are proposals).
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  - नए CSS features आने में सालों लगते थे; JS polyfills layout के बाद चलते थे,
    धीमे थे और flicker करते थे।
  - Custom properties (--x) सिर्फ strings थीं; browser इन्हें animate नहीं कर पाता था।
        --angle: 0deg  ->  --angle: 360deg   (सीधा कूदता है, smooth नहीं!)
  - अच्छे effects (squircle, noise, ripple) के लिए images, canvas या extra DOM चाहिए था।

अब (Houdini):
  - @property से variable को TYPE मिलता है, इसलिए transition/animation चलते हैं।
  - Paint API से background को code से paint करते हैं, browser pipeline के अंदर।
  - Worklets main thread से बाहर चलते हैं (Animation/Layout worklets अभी proposal हैं)।
```

---

## 🟢 How it Works — Step by Step

```
HOUDINI FAMILY (know what is shipped vs. experimental):

  1. Properties & Values API  (@property)            -> SHIPPED in all modern browsers
        Chrome 85+, Safari 16.4+, Firefox 128+
  2. Typed OM (element.attributeStyleMap)            -> Chrome/Safari (not Firefox)
        faster, typed CSS values in JS instead of strings
  3. Paint API (CSS.paintWorklet, paint(name))       -> Chrome/Edge only (Safari, Firefox: no)
  4. Layout API, Animation Worklet                   -> experimental (Chrome flag)
  5. Parser API, Font Metrics API                    -> proposals

MOST USEFUL AND SAFE: @property

   @property --angle {
     syntax: "<angle>";        /* type of the value */
     inherits: false;          /* inherit from parent? */
     initial-value: 0deg;      /* required when syntax is not "*" */
   }
   Now the browser knows --angle is an angle, so it can INTERPOLATE it:
      transition: --angle 1s;      -> smooth rotation
   Used in: animated gradients, conic-gradient spinners, counters.

PAINT API FLOW:
   a) JS file registers a painter:  registerPaint('dots', class { paint(ctx, size, props) { ... } })
   b) Load it:        CSS.paintWorklet.addModule('dots.js')
   c) Use in CSS:     background: paint(dots);
   d) Browser calls paint() whenever size/props change (re-paints, not re-layouts).
   Needs HTTPS or localhost (secure context) and a separate JS file.

PROGRESSIVE ENHANCEMENT:  always give a fallback value and test with
   @supports (background: paint(id))  or  if ('paintWorklet' in CSS)
```

## 🟢 कैसे काम करता है? (Hindi)

```
HOUDINI परिवार (क्या ship हो चुका है और क्या experimental):

  1. Properties & Values API  (@property)         -> सभी modern browsers में
        Chrome 85+, Safari 16.4+, Firefox 128+
  2. Typed OM (element.attributeStyleMap)         -> Chrome/Safari (Firefox में नहीं)
  3. Paint API (CSS.paintWorklet, paint(name))    -> सिर्फ Chrome/Edge (Safari, Firefox में नहीं)
  4. Layout API, Animation Worklet                -> experimental
  5. Parser API, Font Metrics API                 -> proposals

सबसे उपयोगी और सुरक्षित: @property

   @property --angle {
     syntax: "<angle>";        /* value का type */
     inherits: false;          /* parent से inherit करे? */
     initial-value: 0deg;      /* ज़रूरी */
   }
   अब browser जानता है कि --angle एक angle है, तो उसे INTERPOLATE कर सकता है:
      transition: --angle 1s;      -> smooth rotation
   इस्तेमाल: animated gradients, conic-gradient spinners, counters।

PAINT API का flow:
   a) JS file में painter register करो: registerPaint('dots', class { paint(ctx, size) { ... } })
   b) Load करो:        CSS.paintWorklet.addModule('dots.js')
   c) CSS में use:     background: paint(dots);
   d) Size/props बदलने पर browser paint() दोबारा चलाता है (layout नहीं)।
   HTTPS या localhost ज़रूरी, और अलग JS file।

Progressive enhancement: हमेशा fallback दो और @supports या 'paintWorklet' in CSS से check करो।
```

---

## 🟡 Real World Example
**Instagram-style story ring / Swiggy "offer" banners:** The colorful rotating gradient border around a story avatar is a `conic-gradient` whose angle is animated. Before `@property`, you could not animate the gradient angle in CSS; developers used JS or image sprites. Now `--angle` is registered as `<angle>` and a plain CSS animation rotates it smoothly on the compositor-friendly pipeline with no JS.

## 🟡 Real Example Hindi mein
**Instagram जैसी story ring / Swiggy के "offer" banners:** Story avatar के चारों ओर घूमता रंगीन gradient border एक `conic-gradient` है जिसका angle animate होता है। `@property` से पहले gradient का angle CSS में animate नहीं हो सकता था; JS या image sprites लगते थे। अब `--angle` को `<angle>` type में register करके सिर्फ CSS animation से बिना JS के smooth घुमाया जा सकता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CSS Houdini @property Demo</title>
  <style>
    /* ─── 1. REGISTER typed custom properties (Houdini Properties & Values API) ─── */
    @property --angle {
      syntax: "<angle>";      /* browser now knows this is an angle */
      inherits: false;
      initial-value: 0deg;
    }

    @property --num {
      syntax: "<integer>";    /* integers can be animated -> counter trick */
      inherits: false;
      initial-value: 0;
    }

    @property --hue {
      syntax: "<number>";
      inherits: true;
      initial-value: 200;
    }

    * { box-sizing: border-box; }
    body {
      font-family: system-ui, sans-serif;
      background: #111827;
      color: #fff;
      display: grid;
      gap: 32px;
      place-items: center;
      padding: 32px;
    }

    /* ─── 2. STORY RING: rotating conic-gradient border ─── */
    .story {
      width: 120px;
      height: 120px;
      border-radius: 50%;
      padding: 5px;                                   /* ring thickness */
      /* The angle changes, so the gradient rotates */
      background: conic-gradient(from var(--angle), #f09433, #e6683c, #dc2743, #cc2366, #bc1888, #f09433);
      animation: spin 3s linear infinite;
    }
    .story span {
      display: grid; place-items: center;
      width: 100%; height: 100%;
      border-radius: 50%;
      background: #111827;
      font-size: 2rem;
    }
    @keyframes spin { to { --angle: 360deg; } }       /* works ONLY because of @property */

    /* ─── 3. COUNTER: animate an integer, show with CSS counter ─── */
    .counter {
      font-size: 3rem;
      font-weight: 700;
      animation: count 2s ease-out forwards;
      counter-reset: n var(--num);                    /* feed the number into a counter */
    }
    .counter::after { content: counter(n) "%"; }
    @keyframes count { from { --num: 0; } to { --num: 87; } }

    /* ─── 4. SMOOTH HOVER on a gradient using a transition ─── */
    .btn {
      --hue: 200;
      padding: 14px 28px;
      border: 0;
      border-radius: 10px;
      color: #fff;
      font-size: 1rem;
      cursor: pointer;
      background: linear-gradient(135deg, hsl(var(--hue) 80% 50%), hsl(calc(var(--hue) + 60) 80% 50%));
      transition: --hue .6s;                           /* smooth color shift thanks to <number> type */
    }
    .btn:hover { --hue: 330; }

    /* ─── 5. FALLBACK for browsers without @property: no animation, still a static ring ─── */
    @media (prefers-reduced-motion: reduce) {
      .story, .counter { animation: none; }
    }
  </style>
</head>
<body>
  <div class="story"><span>A</span></div>   <!-- rotating ring -->
  <div class="counter"></div>               <!-- 0% to 87% -->
  <button class="btn">Hover me (hue transition)</button>

  <script>
    // Same registration is possible from JS (older way, shows Houdini JS API)
    if (window.CSS && CSS.registerProperty) {
      try {
        CSS.registerProperty({
          name: '--demo',            // must start with --
          syntax: '<length>',
          inherits: false,
          initialValue: '0px'
        });
      } catch (e) { /* already registered via @property */ }
    }
    // Feature detect Paint API (Chrome/Edge only)
    console.log('Paint API supported:', 'paintWorklet' in CSS);
  </script>
</body>
</html>
```

```js
// dots.js: Paint API worklet (needs HTTPS/localhost; Chrome/Edge only)
registerPaint('dots', class {
  static get inputProperties() { return ['--dot-color']; }  // read CSS vars
  paint(ctx, size, props) {
    ctx.fillStyle = props.get('--dot-color').toString() || '#999';
    for (let y = 10; y < size.height; y += 20)
      for (let x = 10; x < size.width; x += 20) {
        ctx.beginPath(); ctx.arc(x, y, 3, 0, 2 * Math.PI); ctx.fill();
      }
  }
});
// In JS:  CSS.paintWorklet.addModule('/dots.js');   In CSS:  background: paint(dots);
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. @property goes into global CSS (Next.js globals.css): no JS needed.
/* globals.css */
@property --angle { syntax: "<angle>"; inherits: false; initial-value: 0deg; }

// 2. Tailwind v4 itself uses @property for its gradient and shadow variables
//    (e.g. --tw-gradient-from) to allow transitions of gradient colors.

// 3. Register a paint worklet in a client component (Chrome only, guard it)
'use client';
import { useEffect } from 'react';
export default function DotsBackground({ children }) {
  useEffect(() => {
    if ('paintWorklet' in CSS) CSS.paintWorklet.addModule('/dots.js'); // file in /public
  }, []);
  return <div style={{ background: 'paint(dots), #eee' }}>{children}</div>; // fallback color
}

// 4. Framer Motion / GSAP can animate registered custom properties too.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is CSS Houdini?**
A1: A collection of APIs exposing parts of the browser's CSS engine to developers: Properties & Values API (`@property`), Typed OM, Paint API, Layout/Animation Worklets, Parser API. The goal is to let developers create CSS features themselves with performance close to native.

**Q2: What does `@property` do and why is it useful?**
A2: It registers a custom property with a `syntax` (type), `inherits`, and `initial-value`. A typed variable can be interpolated, so you can transition/animate things like gradient angles, colors and numbers that plain `--vars` could not animate (they are strings and swap instantly).

**Q3: What is a worklet?**
A3: A lightweight script (like a Web Worker) that runs inside the browser's rendering pipeline, outside the main thread's normal JS, and has a limited API. `paintWorklet` registers a `registerPaint()` class called when the browser needs to paint an element.

**Q4: Which Houdini APIs can you use in production today?**
A4: `@property` (all modern browsers: Chrome 85, Safari 16.4, Firefox 128). Typed OM is partial (not Firefox). The Paint API is Chromium-only, so use it only as progressive enhancement with a normal CSS fallback. Layout/Animation worklets are not production-ready.

**Q5: How do you handle browsers that don't support a Houdini feature?**
A5: Provide a fallback first (`background: #eee; background: paint(dots);`), feature-detect (`CSS.registerProperty`, `'paintWorklet' in CSS`, `@supports`), and make sure the page still works without the effect.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Expecting plain custom properties to animate
```css
/* WRONG: --angle is just a string, so the animation jumps */
@keyframes spin { to { --angle: 360deg; } }

/* CORRECT: register type first */
@property --angle { syntax: "<angle>"; inherits: false; initial-value: 0deg; }
```

❌ **Mistake 2:** Missing `initial-value` (or wrong `syntax`)
```css
/* WRONG: rule is ignored when syntax is not "*" and initial-value missing */
@property --size { syntax: "<length>"; inherits: false; }
/* CORRECT: add initial-value: 0px; */
```

❌ **Mistake 3:** Using the Paint API without a fallback
```css
/* WRONG: blank background in Safari/Firefox */
.box { background: paint(dots); }
/* CORRECT */
.box { background: #eee; background: paint(dots); }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Houdini | APIs to extend the CSS engine | CSS engine बढ़ाने वाली APIs |
| @property | Registers a typed custom property | Typed variable register करना |
| Worklet | Light script in the render pipeline | Render pipeline की छोटी script |
| Paint API | Draw backgrounds with JS | JS से background बनाना |
| Typed OM | Typed CSS values in JS | JS में typed CSS values |
| syntax | Type descriptor like `<angle>` | Value का type |
| Interpolation | Smooth in-between values | बीच की values का smooth बदलाव |

---

## ⚡ 3-Line Summary
**English:**
1. Houdini exposes the CSS engine to developers through APIs like `@property`, Typed OM and the Paint API.
2. `@property` makes custom properties typed so they can be animated (gradient angles, counters); it works in all modern browsers.
3. Paint API and worklets are Chromium-only; use them as progressive enhancement with fallbacks.

**Hindi:**
1. Houdini `@property`, Typed OM और Paint API जैसी APIs से developers को CSS engine तक पहुँच देता है।
2. `@property` custom properties को typed बनाता है ताकि वे animate हो सकें (gradient angle, counters); सभी modern browsers में चलता है।
3. Paint API और worklets सिर्फ Chromium में हैं; इन्हें fallback के साथ progressive enhancement की तरह use करो।

---

## ➡️ Next Topic
**108. Tailwind CSS Basics** — Houdini के बाद practical tools: utility-first CSS, जो आज की React/Next.js projects में सबसे ज़्यादा use होता है।
