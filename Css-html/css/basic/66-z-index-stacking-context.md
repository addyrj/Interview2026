# 66. Z-index + Stacking Context
# हिंदी में: Z-index और Stacking Context — कौन सा element ऊपर दिखेगा

---

## 🔵 Simple Definition (English)
`z-index` controls which overlapping element appears in front. Higher value is on top. But it only competes with elements inside the same **stacking context**, a self-contained "layer group". A parent that creates a stacking context traps all its children's z-index values inside it.

## 🔵 सरल परिभाषा (Hindi)
`z-index` तय करता है कि overlap होने पर कौन सा element आगे दिखेगा। बड़ी value = ऊपर। लेकिन यह सिर्फ उसी **stacking context** के अंदर के elements से मुकाबला करता है, जो एक बंद "layer group" है। जो parent stacking context बनाता है, वह अपने सारे बच्चों की z-index को अंदर ही कैद कर लेता है।

---

## 🔴 Problem it Solves
```
PROBLEM:
  Dropdown menu navbar ke neeche chhup jata hai.
  Modal ke upar tooltip dikhta hai.
  Developer likhta hai z-index: 99999 -- phir bhi kuch nahi hota!

Why? Kyunki z-index "global number race" nahi hai.
Har stacking context ek alag room hai. Room ke andar 99999
bhi bahar ke room ke 1 se haar sakta hai.
```

## 🔴 यह क्यों बना? (Hindi)
Overlap होने पर browser को order तय करना पड़ता है। Z-index से हम यह order control करते हैं। Stacking context इसलिए है कि एक component (जैसे modal) के अंदर की z-index values बाहर के बाकी page को खराब न करें, यानी हर component अपनी layers खुद संभाले।

---

## 🟢 How it Works — Step by Step

```
DEFAULT PAINT ORDER (inside one stacking context, back to front):
  1. Background/border of the context root
  2. Negative z-index children
  3. In-flow non-positioned blocks
  4. Floats
  5. Inline content
  6. z-index: auto / 0 positioned elements (in DOM order)
  7. Positive z-index children (low to high)

z-index works on:
  - positioned elements (relative, absolute, fixed, sticky)
  - flex and grid ITEMS (even with position: static)
  It does NOT work on a plain static block.

WHAT CREATES A NEW STACKING CONTEXT:
  - root <html>
  - position: fixed or sticky (always)
  - position: relative/absolute WITH z-index other than auto
  - opacity less than 1
  - transform, filter, perspective, clip-path, mask (any value except none)
  - will-change: transform / opacity
  - isolation: isolate        <- the clean, intentional way
  - flex/grid item with z-index other than auto
  - contain: layout / paint

EXAMPLE OF THE TRAP:
  <div class="header" style="position:relative; z-index:1">   <- context A (z=1)
     <div class="dropdown" style="position:absolute; z-index:9999">
  </div>
  <div class="hero" style="position:relative; z-index:2">     <- context B (z=2)
  Dropdown (9999) lives INSIDE A. A (1) < B (2). Dropdown shows BEHIND hero!
  Fix: raise header's z-index above hero (e.g. 3).

DEBUGGING STEPS:
  1. Find the two overlapping elements.
  2. Walk up from each to find its nearest stacking-context ancestor.
  3. Compare the z-index of those ANCESTORS at the first shared level.
  4. Chrome DevTools: "Layers" panel or the 3D view helps visualize.

GOOD PRACTICE: keep z-index scale in CSS variables
  :root { --z-dropdown: 100; --z-sticky: 200; --z-modal: 1000; --z-toast: 1100; }
```

## 🟢 कैसे काम करता है? (Hindi)
1. Browser पहले background paint करता है, फिर negative z-index, फिर normal flow, फिर positioned elements, और आखिर में positive z-index (छोटे से बड़े)।
2. बराबर z-index हो तो जो HTML में बाद में लिखा है वह ऊपर।
3. `z-index` सिर्फ positioned elements (और flex/grid items) पर चलता है।
4. नया stacking context बनता है जब: `position: fixed/sticky`, `z-index` वाला relative/absolute, `opacity < 1`, `transform`, `filter`, `isolation: isolate`, `will-change` आदि लगें।
5. बच्चे की z-index सिर्फ अपने context के अंदर गिनी जाती है। बाहर का मुकाबला parent contexts की z-index से होता है।
6. Debug: दोनों elements से ऊपर चढ़ो, पहला साझा context ढूँढो और उन ancestors की z-index compare करो।

---

## 🟡 Real World Example
**Amazon / Flipkart:** the mega-menu dropdown must sit above the page banners; the sticky header gets `z-index` higher than carousels. **Instagram:** a story viewer modal covers the whole feed; a toast ("Link copied") must be above the modal, so toasts get the highest layer. **Zomato:** the bottom "View cart" bar (fixed) must appear above restaurant cards but below the login modal. Teams define a z-index scale (dropdown < sticky < modal < toast) to avoid number wars.

## 🟡 Real Example Hindi mein
**Amazon / Flipkart** का mega-menu banners के ऊपर दिखना चाहिए और sticky header carousel से ऊपर। **Instagram** में story viewer पूरे feed को ढकता है, और "Link copied" toast उसके भी ऊपर चाहिए, इसलिए toast की layer सबसे ऊँची होती है। **Zomato** का नीचे का cart bar cards के ऊपर पर login modal के नीचे रहता है। बड़ी teams z-index का एक scale बना लेती हैं ताकि 99999 की दौड़ न हो।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Z-index and Stacking Context</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; padding: 20px; background: #f5f5f5; }
    h2 { font-size: 16px; margin: 24px 0 8px; }

    /* Z-INDEX SCALE as variables: one source of truth */
    :root {
      --z-dropdown: 100;
      --z-sticky: 200;
      --z-modal: 1000;
    }

    /* ---- DEMO 1: basic overlap ---- */
    .stack { position: relative; height: 110px; }
    .stack div {
      position: absolute;           /* z-index needs positioned elements */
      width: 120px; height: 80px;
      padding: 6px; color: #fff; font-size: 13px;
    }
    .a { background: #e53935; left: 0;    top: 0;    z-index: 1; }
    .b { background: #1e88e5; left: 60px; top: 20px; z-index: 3; } /* on top */
    .c { background: #43a047; left: 120px; top: 40px; z-index: 2; }

    /* ---- DEMO 2: THE TRAP ---- */
    .trap { display: flex; gap: 0; }
    .ctx-a {
      position: relative;
      z-index: 1;                   /* creates context A with value 1 */
      width: 200px; height: 80px;
      background: #ffe082; padding: 8px;
    }
    .ctx-a .dropdown {
      position: absolute;
      top: 50px; left: 20px;
      z-index: 9999;                /* huge, but trapped inside context A */
      width: 180px; padding: 10px;
      background: #8e24aa; color: #fff;
    }
    .ctx-b {
      position: relative;
      z-index: 2;                   /* context B (2) beats context A (1) */
      width: 200px; height: 120px;
      margin-left: -40px;
      background: #80cbc4; padding: 8px;
    }
    /* FIX: uncomment to make dropdown show above B */
    /* .ctx-a { z-index: 3; } */

    /* ---- DEMO 3: isolation: isolate (clean way to make a context) ---- */
    .card {
      isolation: isolate;           /* children z-index cannot leak out */
      position: relative;
      background: #fff; padding: 12px; border: 1px solid #ccc;
    }
    .card .glow {
      position: absolute; inset: 0;
      background: linear-gradient(90deg, #ffcdd2, transparent);
      z-index: -1;                  /* behind card content but NOT behind page */
    }
  </style>
</head>
<body>
  <h2>1. Basic z-index (blue 3 > green 2 > red 1)</h2>
  <div class="stack">
    <div class="a">z: 1</div>
    <div class="b">z: 3</div>
    <div class="c">z: 2</div>
  </div>

  <h2>2. The trap: purple dropdown (9999) is hidden behind teal box</h2>
  <div class="trap">
    <div class="ctx-a">Context A (z:1)
      <div class="dropdown">Dropdown z:9999</div>
    </div>
    <div class="ctx-b">Context B (z:2)</div>
  </div>

  <h2>3. isolation: isolate keeps z-index:-1 inside the card</h2>
  <div class="card">
    <div class="glow"></div>
    Card text stays above its own glow.
  </div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Tailwind z-index utilities: z-0 z-10 z-20 z-30 z-40 z-50, arbitrary z-[999]
<header className="sticky top-0 z-40">Navbar</header>
<div className="fixed inset-0 z-50 bg-black/50">Modal overlay</div>

// 2. Modals via Portal: render at the end of <body> so no ancestor's
//    transform/opacity/overflow traps the modal in a lower stacking context.
import { createPortal } from 'react-dom';
function Modal({ children }) {
  return createPortal(
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/50">{children}</div>,
    document.body
  );
}

// 3. Next.js: put a <div id="modal-root" /> in layout.tsx and portal into it.

// 4. Z-index scale in a design system (Tailwind config / CSS variables)
// :root { --z-dropdown: 100; --z-modal: 1000; --z-toast: 1100; }

// 5. Library note: Radix/Headless UI/MUI already portal their popovers.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is a stacking context?**
A1: An isolated 3D layering group created by an element. Inside it, children are stacked by their own z-index; the whole group is then treated as one unit against its siblings. Creators include the root, `position` + `z-index`, fixed/sticky, `opacity < 1`, `transform`, `filter`, `isolation: isolate`.

**Q2: Why does `z-index: 9999` not work?**
A2: Usually because the element is inside a lower stacking context, so it can never beat elements in a higher parent context. Or the element is `position: static` (z-index ignored, except flex/grid items). Find the ancestor that creates the context and fix its z-index.

**Q3: Which elements does z-index apply to?**
A3: Positioned elements (relative, absolute, fixed, sticky) and flex/grid items. Not plain static blocks.

**Q4: If two elements have the same z-index, who wins?**
A4: The one later in the DOM order is painted on top.

**Q5: How do you manage z-index in a large project?**
A5: Define a scale with CSS variables or Tailwind tokens (dropdown, sticky, modal, toast), use portals for overlays, use `isolation: isolate` on components to contain their internal z-indexes, and avoid arbitrary huge numbers.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Escalating numbers (9999, 99999, 999999)
```css
.dropdown { z-index: 999999; }  /* still loses to a parent context */
```
✅ **Correct way:** find the stacking context, then use a small scale with named variables.

❌ **Mistake 2:** Adding `transform` or `opacity` to a parent and accidentally trapping children
```css
.wrapper { transform: translateZ(0); }  /* new context! fixed children now relative to wrapper */
```
✅ **Correct way:** know what creates contexts; use `isolation: isolate` deliberately, and render modals via portal.

❌ **Mistake 3:** Setting `z-index` on a static element
```css
.box { z-index: 10; }          /* ignored: position is static */
```
✅ **Correct way:** `.box { position: relative; z-index: 10; }`

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| z-index | Stack order on the z-axis | Layers का क्रम |
| Stacking context | Isolated layer group | बंद layer group |
| isolation: isolate | Create a context without side effects | साफ़ तरीके से नया context |
| Paint order | Back to front drawing order | पीछे से आगे रंगने का क्रम |
| Portal | Render outside parent DOM | DOM में बाहर render करना |
| Negative z-index | Behind parent content | Parent के पीछे |
| Overlay | Layer above page content | ऊपर की परत |
| Z-index scale | Named levels for layers | Layers की तय सूची |

---

## ⚡ 3-Line Summary
**English:**
1. Higher z-index is in front, but only within the same stacking context.
2. Parents with position+z-index, transform, opacity<1, fixed/sticky or isolation create new contexts and trap children.
3. Use a small z-index scale, portals for modals, and `isolation: isolate` for components.

**Hindi:**
1. बड़ी z-index आगे दिखती है, पर सिर्फ उसी stacking context के अंदर।
2. position+z-index, transform, opacity<1, fixed/sticky या isolation वाले parent नया context बनाकर बच्चों को कैद कर लेते हैं।
3. छोटा z-index scale, modals के लिए portal और components के लिए `isolation: isolate` use करो।

---

## ➡️ Next Topic
**67. CSS Overflow** — content box से बड़ा हो जाए तो क्या होता है: hidden, scroll, auto, और scroll containers।
