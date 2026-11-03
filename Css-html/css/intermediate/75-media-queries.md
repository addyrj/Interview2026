# 75. Media Queries
# हिंदी में: Media Queries — Screen के हिसाब से CSS बदलना

---

## 🔵 Simple Definition (English)
A media query applies CSS only when a condition is true, such as screen width, orientation, resolution, or user preferences (dark mode, reduced motion). Syntax: `@media (condition) { rules }`. It is the main tool for changing layout at breakpoints.

## 🔵 सरल परिभाषा (Hindi)
Media query CSS को तभी लागू करती है जब कोई शर्त सही हो, जैसे screen की width, orientation, resolution या user की पसंद (dark mode, reduced motion)। Syntax: `@media (शर्त) { rules }`। Breakpoints पर layout बदलने का यही मुख्य तरीका है।

---

## 🔴 Problem it Solves
```
PROBLEM:
  Ek hi CSS sabhi screens pe: desktop pe 4 columns theek,
  par phone pe 4 columns = ghisi-piti chhoti cards.

  Print karte time navbar + ads kyun chhapein?
  Dark mode wale user ko white background kyun dikhaye?

Media query = "agar yeh condition sach hai tabhi yeh CSS lagao."
```

## 🔴 यह क्यों बना? (Hindi)
सारे devices पर एक जैसा CSS नहीं चल सकता। हमें शर्त के साथ CSS चाहिए: "अगर width 768px से कम है तो columns 1 कर दो", "अगर user dark mode में है तो काला background", "print करते समय navbar छुपा दो"। Media query यही देती है।

---

## 🟢 How it Works — Step by Step

```
SYNTAX
  @media <media-type> and (<feature>: <value>) { ...rules... }

  media types : all (default), screen, print     (tv/handheld are obsolete)

COMMON FEATURES
  width / min-width / max-width           viewport width
  height / min-height / max-height        viewport height
  orientation: portrait | landscape
  resolution / min-resolution: 2dppx      (retina) 
  hover: hover | none                     (can the primary input hover?)
  pointer: fine | coarse                  (mouse vs touch)
  prefers-color-scheme: dark | light
  prefers-reduced-motion: reduce
  prefers-contrast: more
  display-mode: standalone                (installed PWA)

LOGIC
  and           @media (min-width: 600px) and (max-width: 900px)
  , (or)        @media (max-width: 500px), (orientation: portrait)
  not           @media not print
  only          @media only screen  (legacy hack for very old browsers)

RANGE SYNTAX (modern, supported in current Chrome 104+, Firefox 63+, Safari 16.4+):
  @media (width >= 768px)
  @media (600px <= width <= 900px)
  Cleaner than min-/max-width. For older browsers keep min-width.

EMBEDDING / ORDERING
  - Media queries add NO specificity. Later rule wins at equal specificity,
    so order matters: put min-width queries from small to large.
  - <link rel="stylesheet" media="print" href="print.css"> loads only for print
  - You can also nest media queries inside rules with CSS nesting (modern browsers).

UNITS INSIDE QUERIES
  px is common. em in queries (e.g. 48em) respects user's default font size
  (zoom/accessibility) and does not depend on html font-size set by you.

JS ACCESS
  window.matchMedia('(max-width: 768px)').matches
  mq.addEventListener('change', handler)

MOBILE FIRST vs DESKTOP FIRST (next topic):
  min-width queries = mobile first, max-width = desktop first.

AVOID: too many breakpoints, device-specific widths (iPhone 14 = 390px), 
  mixing min and max randomly (gaps like 768px / 767.98px edge cases).
```

## 🟢 कैसे काम करता है? (Hindi)
1. `@media (min-width: 768px) { ... }` = जब screen 768px या ज़्यादा हो तभी अंदर का CSS लगेगा।
2. `and` = दोनों शर्तें, कॉमा = कोई एक, `not` = उल्टा। जैसे `(min-width: 600px) and (max-width: 900px)`।
3. Media types: `screen` (monitor/phone) और `print` (छपाई)। बाकी पुराने हैं।
4. सिर्फ width नहीं: `orientation`, `hover`, `pointer: coarse` (touch), `prefers-color-scheme: dark`, `prefers-reduced-motion` भी जाँच सकते हैं।
5. Media query की specificity नहीं बढ़ती। इसलिए order मायने रखता है: बाद में लिखी rule जीतती है। Base CSS पहले, media queries बाद में।
6. नया range syntax `(width >= 768px)` साफ़ पढ़ने में आता है और अब सभी आधुनिक browsers में चलता है।
7. JS में `window.matchMedia(...)` से वही शर्त जाँच सकते हैं।
8. Print के लिए `@media print` में navbar, ads छुपाओ और background हटाओ।

---

## 🟡 Real World Example
**Amazon / Flipkart:** below ~768px the mega-menu collapses to a hamburger and the grid switches from 4 to 2 columns, all with `@media (max-width/min-width)`. **Instagram / YouTube:** `prefers-color-scheme: dark` auto-switches to the dark theme by system setting. **Gmail print:** `@media print` hides the sidebar so only the email prints. **Zomato / Swiggy:** `@media (hover: hover)` adds hover effects on desktop only, while touch devices get larger tap areas using `(pointer: coarse)`.

## 🟡 Real Example Hindi mein
**Amazon / Flipkart** में लगभग 768px से नीचे mega-menu hamburger बन जाता है और grid 4 से 2 columns हो जाता है, सब media queries से। **Instagram / YouTube** system के dark mode setting को `prefers-color-scheme: dark` से पहचानकर dark theme लगाते हैं। **Gmail** की print में `@media print` sidebar छुपा देता है, सिर्फ email छपता है। **Zomato / Swiggy** में hover effects सिर्फ `(hover: hover)` यानी desktop पर, और touch devices पर `(pointer: coarse)` से बड़े tap areas।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Media Queries Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }

    /* THEME VARIABLES: light by default */
    :root { --bg: #f5f5f5; --fg: #222; --card: #fff; }

    body { margin: 0; padding: 16px; font-family: system-ui, sans-serif; background: var(--bg); color: var(--fg); }

    /* A live indicator showing which breakpoint is active */
    .indicator { position: sticky; top: 0; padding: 8px 12px; color: #fff; font-weight: bold; background: #c62828; }
    .indicator::after { content: "Mobile (< 600px)"; }

    /* BASE (mobile) layout: one column */
    .grid { display: grid; gap: 12px; grid-template-columns: 1fr; margin-top: 12px; }
    .card { background: var(--card); border: 1px solid #ccc; padding: 16px; border-radius: 8px; }

    /* 1. WIDTH: min-width = mobile first, small to large */
    @media (min-width: 600px) {
      .indicator { background: #ef6c00; }
      .indicator::after { content: "Tablet (600px - 899px)"; }
      .grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (min-width: 900px) {
      .indicator { background: #2e7d32; }
      .indicator::after { content: "Desktop (900px+)"; }
      .grid { grid-template-columns: repeat(4, 1fr); }
    }

    /* 2. RANGE only (width between): both conditions joined with and */
    @media (min-width: 600px) and (max-width: 899px) {
      .card:first-child { border-color: #ef6c00; border-width: 3px; }  /* only on tablet */
    }

    /* 3. ORIENTATION */
    @media (orientation: landscape) and (max-height: 500px) {
      .indicator { font-size: 12px; padding: 4px 12px; }     /* compact in short landscape */
    }

    /* 4. HOVER + POINTER: hover effects only where hover exists */
    @media (hover: hover) {
      .card:hover { transform: translateY(-4px); box-shadow: 0 6px 14px rgba(0,0,0,.2); }
    }
    @media (pointer: coarse) {
      .btn { min-height: 48px; }            /* bigger tap targets on touch screens */
    }
    .btn { padding: 0 16px; min-height: 36px; border: 0; background: #ffd814; border-radius: 6px; }

    /* 5. DARK MODE from OS setting */
    @media (prefers-color-scheme: dark) {
      :root { --bg: #121212; --fg: #eee; --card: #1e1e1e; }
      .card { border-color: #444; }
    }

    /* 6. REDUCED MOTION: respect users who get dizzy from animation */
    .card { transition: transform .25s, box-shadow .25s; }
    @media (prefers-reduced-motion: reduce) {
      .card { transition: none; }
    }

    /* 7. PRINT: hide chrome, plain colours */
    @media print {
      .indicator, .btn { display: none; }
      body { background: #fff; color: #000; }
      .card { border: 1px solid #000; break-inside: avoid; }
    }
  </style>
</head>
<body>
  <div class="indicator"></div>   <!-- text comes from ::after + media queries -->
  <div class="grid">
    <div class="card"><h3>Card 1</h3><button class="btn">Buy</button></div>
    <div class="card"><h3>Card 2</h3><button class="btn">Buy</button></div>
    <div class="card"><h3>Card 3</h3><button class="btn">Buy</button></div>
    <div class="card"><h3>Card 4</h3><button class="btn">Buy</button></div>
  </div>

  <script>
    // JS equivalent of a media query: logs when crossing 900px
    const mq = window.matchMedia('(min-width: 900px)');
    mq.addEventListener('change', e => console.log('Desktop?', e.matches));
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Tailwind generates media queries from prefixes
//    sm:640px  md:768px  lg:1024px  xl:1280px  2xl:1536px   (all min-width)
<div className="flex-col md:flex-row dark:bg-black print:hidden hover:opacity-80" />
// Tailwind v4 also supports: @media (hover: hover) variant behaviour by default for hover:
// and arbitrary variants: [@media(min-width:900px)]:grid-cols-4

// 2. CSS Modules: write the media query normally
/* Card.module.css */
.card { padding: 12px; }
@media (min-width: 768px) { .card { padding: 24px; } }

// 3. useMediaQuery hook (client components only)
'use client';
import { useEffect, useState } from 'react';
export function useMediaQuery(query) {
  const [matches, setMatches] = useState(false);   // false on server = no mismatch
  useEffect(() => {
    const mql = window.matchMedia(query);
    const update = () => setMatches(mql.matches);
    update();
    mql.addEventListener('change', update);
    return () => mql.removeEventListener('change', update);
  }, [query]);
  return matches;
}
// Use CSS for visuals; use the hook only for logic (e.g. render a different component).

// 4. styled-components / emotion: const Box = styled.div` @media (min-width: 768px) { ... } `;

// 5. Dark mode with Tailwind: darkMode: 'media' follows OS; 'class' lets users toggle.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is a media query and what is its syntax?**
A1: A CSS conditional rule: `@media (min-width: 768px) { ... }`. The rules inside apply only when the condition is true. Conditions can test width, height, orientation, resolution, hover/pointer capability and user preferences.

**Q2: `min-width` vs `max-width` in media queries?**
A2: `min-width: 768px` applies at 768px and above (used mobile-first). `max-width: 767px` applies at 767px and below (desktop-first). Mixing both defines a range: `(min-width: 600px) and (max-width: 899px)`.

**Q3: How do you combine multiple conditions?**
A3: `and` for all conditions, comma for any (OR), `not` to negate: `@media (min-width: 600px) and (orientation: landscape)`, `@media (max-width: 500px), print`. Modern range syntax: `(600px <= width <= 900px)`.

**Q4: How do you support dark mode and reduced motion?**
A4: `@media (prefers-color-scheme: dark) { :root { --bg: #111; } }` and `@media (prefers-reduced-motion: reduce) { * { animation: none; transition: none; } }`. These respect OS-level user settings.

**Q5: Media query vs container query?**
A5: A media query responds to the viewport or device; a container query (`@container`) responds to the size of a parent container, so a reusable component adapts wherever it is placed (sidebar vs main). Container queries are supported in all current evergreen browsers (Chrome 105+, Safari 16+, Firefox 110+).

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Wrong order of min-width queries
```css
@media (min-width: 1024px) { .grid { grid-template-columns: repeat(4, 1fr); } }
@media (min-width: 768px)  { .grid { grid-template-columns: repeat(2, 1fr); } }
/* WRONG: at 1100px both match, the LATER rule (2 columns) wins */
```
✅ **Correct way:** write queries from smallest to largest for `min-width` (largest to smallest for `max-width`).

❌ **Mistake 2:** Missing the viewport meta tag, so queries never match on phones
✅ **Correct way:** `<meta name="viewport" content="width=device-width, initial-scale=1">`

❌ **Mistake 3:** Hard-coding device widths and many breakpoints
```css
@media (width: 390px) { }    /* iPhone only: unmaintainable */
```
✅ **Correct way:** use a few content-based breakpoints (e.g. 640 / 768 / 1024) and fluid CSS in between.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| @media | Conditional CSS rule | शर्त वाला CSS |
| Breakpoint | Width where styles change | जहाँ styles बदलते हैं |
| min-width | At this width and above | इस width या उससे ऊपर |
| max-width | At this width and below | इस width या उससे नीचे |
| prefers-color-scheme | OS dark/light setting | OS का dark/light mode |
| prefers-reduced-motion | User wants less animation | कम animation की पसंद |
| matchMedia | JS API for media queries | JS में media query |
| Container query | Query on parent size | Parent के size पर शर्त |

---

## ⚡ 3-Line Summary
**English:**
1. `@media (condition) { ... }` applies CSS only when the condition is true: width, orientation, hover, dark mode, print.
2. Order matters (no extra specificity): write `min-width` queries small to large.
3. Use few, content-based breakpoints; use container queries for component-level responsiveness.

**Hindi:**
1. `@media (शर्त) { ... }` सिर्फ शर्त सही होने पर CSS लगाती है: width, orientation, hover, dark mode, print।
2. Order मायने रखता है (specificity नहीं बढ़ती): `min-width` queries छोटे से बड़े लिखो।
3. कम और content-आधारित breakpoints रखो; component-level responsiveness के लिए container queries।

---

## ➡️ Next Topic
**76. Mobile First vs Desktop First** — media queries को किस दिशा से लिखें (`min-width` या `max-width`) और क्यों mobile-first बेहतर है।
