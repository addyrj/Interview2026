# 87. CSS Calc() Function
# हिंदी में: CSS calc() — CSS में ही Maths करना

---

## 🔵 Simple Definition (English)
`calc()` lets you do arithmetic (`+ - * /`) inside CSS values and, most importantly, mix different units, for example `width: calc(100% - 250px)`. The browser works out the final value at render time, so it adapts when the window or parent size changes.

## 🔵 सरल परिभाषा (Hindi)
`calc()` से आप CSS values के अंदर गणित (`+ - * /`) कर सकते हो, और सबसे बड़ी बात, अलग-अलग units मिला सकते हो, जैसे `width: calc(100% - 250px)`। Browser final value render के समय निकालता है, इसलिए window या parent की size बदलने पर वो अपने आप adjust होती है।

---

## 🔴 Problem it Solves
```
BEFORE:
  Sidebar is a fixed 250px, content should fill the REST of the screen.
  - width: 100% would overflow (100% + 250px)
  - width: 75% breaks when screen size changes (sidebar stays 250px, content becomes 75% of something else)
  - JS: window.onresize = () => content.style.width = window.innerWidth - 250 + 'px'  (slow, flickers)

AFTER:
  .content { width: calc(100% - 250px); }
  /* Pure CSS, always correct, no JS, no resize listener */
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  Sidebar 250px fixed है, content को बाकी पूरी जगह भरनी है।
  - width: 100% से overflow (100% + 250px)
  - width: 75% screen बदलने पर गलत हो जाता है
  - JS से resize listener (धीमा, flicker)

अब:
  width: calc(100% - 250px) और बस। कोई JS नहीं, हमेशा सही।
```

---

## 🟢 How it Works — Step by Step

```
SYNTAX:
  property: calc(expression);

  width:      calc(100% - 250px);
  height:     calc(100vh - 64px);               /* full screen minus the header height */
  font-size:  calc(14px + 0.5vw);               /* fluid font */
  margin-left: calc(var(--gap) * 2);            /* with variables (topic 77) */
  padding:    calc(1rem + 2px);

RULES:
  1. + and - MUST have spaces around them:  calc(100% - 20px)  OK,  calc(100%-20px)  INVALID
     (because -20px could be read as a negative number). * and / don't strictly need spaces, but add them.
  2. For * : at least one side must be a plain NUMBER (unitless): calc(10px * 3), calc(2 * 1rem)
  3. For / : the right side must be a plain NUMBER and not zero: calc(100% / 3)
  4. Nesting is allowed: calc(100% - calc(2 * 1rem)) -> or just use plain parentheses: calc(100% - (2 * 1rem))
  5. You can mix: px, %, em, rem, vw, vh, ch, etc. The browser resolves them at layout time.
  6. Works wherever a length, percentage, number, angle, time, or integer is allowed
     (modern browsers: width, margin, font-size, rotate(), transition-duration, etc.)

COMMON USES:
  - Full-height section under a fixed header: calc(100vh - var(--header-h))
  - Grid-like columns with gaps (pre-Grid): width: calc(33.333% - 20px)
  - Fluid typography: calc(1rem + 1vw) (modern: clamp(), topic 88)
  - Sticky offset below header: top: calc(var(--header-h) + 16px)
  - Centering with offsets: left: calc(50% - 150px)  (150 = half of 300px width)
  - Dividing a value: calc(var(--space) / 2)

ADVANCED / NEWER:
  - Keywords: calc(infinity * 1px), calc(pi * 10px)  (math constants, newer browsers)
  - Typed arithmetic with attr()/unit division is still emerging; don't rely on it.
  - Related math functions (topic 88): min(), max(), clamp(). Newer ones (round(), mod(), abs(), sign(),
    sin()/cos()) have uneven browser support: check caniuse before using.

PERCENT RESOLUTION: % inside calc() refers to the same thing as the % would on that property
  (width: % of parent's width; height: % of parent's height, if defined; font-size: % of parent's font-size).

WHAT CAN'T IT DO:
  - Can't multiply two lengths (px * px invalid).
  - Can't divide by a length: calc(100px / 2px) was invalid in older browsers (newer ones support typed division).
  - var() cannot be used inside media query conditions.

SUPPORT: all modern browsers (Chrome 26+, Firefox 16+, Safari 7+, IE9+).
```

## 🟢 कैसे काम करता है? (Hindi)

```
SYNTAX:  property: calc(expression);

  width:  calc(100% - 250px);
  height: calc(100vh - 64px);          /* header छोड़कर पूरी screen */
  font-size: calc(14px + 0.5vw);       /* fluid font */

नियम:
  1. + और - के दोनों तरफ space ज़रूरी है: calc(100% - 20px) सही, calc(100%-20px) गलत।
  2. गुणा (*) में कम से कम एक तरफ बिना unit की संख्या होनी चाहिए: calc(10px * 3)
  3. भाग (/) में दाईं तरफ बिना unit की संख्या (शून्य नहीं): calc(100% / 3)
  4. Nesting और brackets चलते हैं: calc(100% - (2 * 1rem))
  5. px, %, em, rem, vw, vh सब मिला सकते हो; browser layout के समय हल करता है।
  6. Variables के साथ भी: calc(var(--gap) * 2)

आम उपयोग:
  - Fixed header के नीचे पूरी screen: calc(100vh - var(--header-h))
  - Gap के साथ columns: calc(33.333% - 20px)
  - Sticky offset: top: calc(var(--header-h) + 16px)

जो नहीं कर सकता:
  - दो lengths का गुणा (px * px) नहीं होता।
  - Media query में var() नहीं चलता।
```

---

## 🟡 Real World Example
**Gmail and Amazon layouts:** Gmail's inbox list fills the screen height minus the top bar (about 64px) using `height: calc(100vh - 64px)`, so only the email list scrolls, not the whole page. Amazon's product page has a fixed-width filter sidebar on the left and the results area takes the remaining width: `calc(100% - 260px)`. Swiggy's sticky category tabs sit `calc(header height + 8px)` below the top. Many feed UIs (Instagram-style) also use calc for padding-aware widths such as `calc(100% - 24px)`.

## 🟡 Real Example Hindi mein
**Gmail और Amazon के layouts:** Gmail की inbox list screen की height में से top bar (लगभग 64px) घटाकर बनती है: `height: calc(100vh - 64px)`, ताकि सिर्फ email list scroll हो, पूरा page नहीं। Amazon के product page में बाईं तरफ fixed-width filter sidebar है और results area बाकी चौड़ाई लेता है: `calc(100% - 260px)`। Swiggy की sticky category tabs header की height + 8px नीचे चिपकी रहती हैं: `calc(header height + 8px)`।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CSS calc() Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }

    :root {
      --header-h: 56px;     /* one source of truth for header height */
      --sidebar-w: 220px;   /* fixed sidebar width */
      --gap: 16px;
    }

    body { margin: 0; font-family: system-ui, sans-serif; background: #f0f2f5; }

    /* 1. FIXED HEADER */
    .header {
      position: fixed; top: 0; left: 0; right: 0;
      height: var(--header-h);
      background: #ff5a5f; color: #fff;
      display: flex; align-items: center; padding: 0 var(--gap);
      font-weight: bold; z-index: 10;
    }

    /* 2. APP SHELL: sidebar + content using calc */
    .shell { padding-top: var(--header-h); display: flex; }   /* room for the fixed header */

    .sidebar {
      width: var(--sidebar-w); flex: none;
      height: calc(100vh - var(--header-h));          /* full height minus header */
      background: #fff; border-right: 1px solid #ddd;
      padding: var(--gap); overflow-y: auto;
      position: sticky; top: var(--header-h);          /* stays below the header */
    }

    .content {
      width: calc(100% - var(--sidebar-w));            /* takes the REST of the width */
      padding: calc(var(--gap) * 1.5);                 /* 24px, derived from the gap token */
    }

    /* 3. THREE CARDS PER ROW WITH A GAP (legacy but a classic calc exercise) */
    .cards { display: flex; flex-wrap: wrap; gap: var(--gap); }
    .card {
      /* 3 cards + 2 gaps = 100%, so each card is (100% - 2 gaps) / 3 */
      width: calc((100% - 2 * var(--gap)) / 3);
      background: #fff; border-radius: 12px; padding: var(--gap);
      box-shadow: 0 2px 6px rgba(0,0,0,.1);
    }

    /* 4. FLUID FONT SIZE: 16px base that grows with viewport */
    h1 { font-size: calc(1.25rem + 1.2vw); margin-top: 0; }

    /* 5. CENTERING WITH calc (fixed width element) */
    .abs-wrap { position: relative; height: 90px; background: #fff; border: 2px dashed #bbb; margin: var(--gap) 0; }
    .abs-box {
      position: absolute; top: 20px;
      width: 160px; height: 50px;
      left: calc(50% - 80px);                          /* 50% minus half of own width */
      background: #1a73e8; color: #fff; display: grid; place-items: center; border-radius: 8px;
    }

    /* 6. SCROLLABLE LIST that fills the remaining height of a panel */
    .panel { height: 220px; background: #fff; border-radius: 12px; overflow: hidden; }
    .panel-title { height: 40px; padding: 10px 14px; background: #e8f0fe; font-weight: bold; }
    .panel-list { height: calc(100% - 40px); overflow-y: auto; padding: 0 14px; }

    /* 7. STICKY SUBHEADER offset */
    .tabs { position: sticky; top: calc(var(--header-h) + 8px); background: #fff; padding: 8px 12px; border-radius: 8px; margin-bottom: var(--gap); }

    /* 8. Small screens: sidebar goes away, content uses full width */
    @media (max-width: 700px) {
      .sidebar { display: none; }
      .content { width: 100%; }
      .card { width: 100%; }
    }
  </style>
</head>
<body>
  <div class="header">calc() layout - header is --header-h tall</div>

  <div class="shell">
    <aside class="sidebar">
      <strong>Sidebar</strong>
      <p>width: var(--sidebar-w)<br>height: calc(100vh - header)</p>
    </aside>

    <main class="content">
      <h1>Fluid heading</h1>
      <div class="tabs">Sticky tabs: top = calc(header + 8px)</div>

      <div class="cards">
        <div class="card">Card 1<br><small>(100% - 2 gaps) / 3</small></div>
        <div class="card">Card 2</div>
        <div class="card">Card 3</div>
      </div>

      <h3>Offset centering</h3>
      <div class="abs-wrap"><div class="abs-box">left: calc(50% - 80px)</div></div>

      <h3>Panel with remaining height</h3>
      <div class="panel">
        <div class="panel-title">Inbox</div>
        <div class="panel-list">
          <p>Mail 1</p><p>Mail 2</p><p>Mail 3</p><p>Mail 4</p><p>Mail 5</p>
          <p>Mail 6</p><p>Mail 7</p><p>Mail 8</p><p>Mail 9</p><p>Mail 10</p>
        </div>
      </div>
      <div style="height:600px"></div>   <!-- extra height to test the sticky parts -->
    </main>
  </div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Tailwind arbitrary values: underscores replace spaces, and + - need spaces so use _
<div className="h-[calc(100vh-64px)] w-[calc(100%-250px)] overflow-y-auto">Content</div>
// In Tailwind arbitrary values Tailwind normalizes spaces around + - * / inside calc(),
// but in plain CSS and inline styles always write the spaces yourself.

// 2. Combine with CSS variables (topic 77)
<main style={{ height: 'calc(100vh - var(--header-h))' }}>...</main>

// 3. Inline style in React: calc is just a string
<div style={{ width: `calc(100% - ${sidebarWidth}px)` }}>   {/* dynamic JS value inside calc */}
  ...
</div>

// 4. Next.js layout.js: full-height app shell
export default function Layout({ children }) {
  return (
    <div className="min-h-[calc(100vh-4rem)] pt-16">{children}</div>   // 4rem header
  );
}

// 5. Mobile browser quirk: 100vh includes the URL bar area on mobile.
//    Prefer the dynamic viewport unit: h-[calc(100dvh-4rem)]  (dvh: Chrome 108+, Safari 15.4+, Firefox 101+)

// 6. Modern alternatives that need no calc: flex-1 (take remaining width), grid-template-columns: 250px 1fr
```

---

## ⚫ Interview Questions + Answers

**Q1: What is `calc()` and why is it useful?**
A1: `calc()` evaluates simple math (`+ - * /`) inside CSS values and can mix different units, such as `%` with `px`. It is useful for values that depend on both relative and fixed sizes, such as `width: calc(100% - 250px)` or `height: calc(100vh - 64px)`. The browser resolves it at layout time, so it stays correct on resize without JavaScript.

**Q2: What are the syntax rules for `calc()`?**
A2: `+` and `-` must have whitespace on both sides (`calc(100% - 20px)`; `calc(100%-20px)` is invalid). For `*`, at least one operand must be a unitless number. For `/`, the right operand must be a unitless number (non-zero). You cannot multiply two lengths. Parentheses and nested `calc()` are allowed, and CSS variables can be used inside.

**Q3: How would you make a section fill the screen height under a fixed header?**
A3: `height: calc(100vh - var(--header-h))`, with the header height stored in a CSS variable (or `100dvh` on mobile browsers where the URL bar changes the viewport). Alternatives without calc: make the page a flex column with `min-height: 100vh` and let the main area use `flex: 1`, or use Grid with `grid-template-rows: auto 1fr`. These are often more robust.

**Q4: Can you use calc() with CSS variables and percentages? What does the percentage refer to?**
A4: Yes: `calc(var(--gap) * 2)` and `calc(100% - var(--sidebar-w))` are common. A percentage inside `calc()` resolves exactly like it would on that property alone (for `width`, the parent's width; for `font-size`, the parent's font size; for `top`, the containing block height). A `var()` that holds a unitless number can be multiplied by a unit: `calc(var(--n) * 1px)`.

**Q5: What are alternatives to `calc()` and its limitations?**
A5: Flexbox (`flex: 1`) or Grid (`1fr`, `minmax()`) can take "the remaining space" without any math, so they are preferred for layout. `min()`, `max()`, `clamp()` (topic 88) handle responsive bounds. Limitations of `calc()`: no multiplying two lengths, no dividing by a length in older browsers, errors invalidate the whole declaration, and `var()` is not allowed in media query conditions. Browser support is universal for basics.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Missing spaces around `+` or `-`
```css
/* WRONG: invalid, the declaration is ignored */
.box { width: calc(100%-20px); }

/* CORRECT */
.box { width: calc(100% - 20px); }
```

❌ **Mistake 2:** Multiplying two lengths
```css
/* WRONG */
.box { width: calc(10px * 5px); }

/* CORRECT: one side must be a number */
.box { width: calc(10px * 5); }
```

❌ **Mistake 3:** Using `100vh` on mobile and getting content hidden behind the URL bar
```css
/* WRONG on mobile Safari/Chrome */
.screen { height: calc(100vh - 56px); }

/* CORRECT: dynamic viewport unit with a fallback */
.screen { height: calc(100vh - 56px); height: calc(100dvh - 56px); }
```

❌ **Mistake 4:** Using calc for a layout that Flexbox/Grid solves better
```css
/* WRONG: magic numbers that break when the sidebar changes */
.content { width: calc(100% - 250px); }

/* CORRECT */
.layout { display: grid; grid-template-columns: 250px 1fr; }
```

❌ **Mistake 5:** Forgetting `box-sizing: border-box` and padding on a calc width
```css
/* CORRECT: add the reset so padding/border don't push calc(...) widths over 100% */
*, *::before, *::after { box-sizing: border-box; }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| calc() | CSS function for math with mixed units | CSS में गणित करने वाला function |
| mixed units | Using %, px, rem together | अलग-अलग units एक साथ |
| viewport units | vh/vw/dvh relative to the screen | Screen के अनुपात वाली units |
| unitless number | Plain number without px, % | बिना unit की संख्या |
| fluid | Size that scales with viewport | Screen के साथ बढ़ने-घटने वाली size |
| `dvh` | Dynamic viewport height (mobile-friendly) | Mobile के लिए सही viewport height |
| magic number | Hard-coded value with no explanation | बिना कारण वाली fixed value |
| invalid at parse | Wrong syntax: whole declaration dropped | गलत syntax से property ignore |

---

## ⚡ 3-Line Summary
**English:**
1. `calc()` performs `+ - * /` inside CSS values and mixes units like `100% - 250px` at render time.
2. Spaces around `+` and `-` are mandatory; for `*` and `/` one side must be a unitless number.
3. Great with CSS variables and viewport units, but prefer Flexbox/Grid when you just need "remaining space".

**Hindi:**
1. `calc()` CSS values में `+ - * /` करता है और `100% - 250px` जैसी अलग units को render के समय मिलाता है।
2. `+` और `-` के दोनों तरफ space ज़रूरी है; `*` और `/` में एक तरफ बिना unit की संख्या होनी चाहिए।
3. CSS variables और viewport units के साथ बढ़िया है, पर "बची हुई जगह" के लिए Flexbox/Grid बेहतर है।

---

## ➡️ Next Topic
**88. CSS Functions (min, max, clamp)** — `calc()` के बाद सबसे useful responsive functions: fluid typography और container widths बिना media queries के।
