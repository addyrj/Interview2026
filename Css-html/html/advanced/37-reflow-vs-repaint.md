# 37. Reflow vs Repaint
# हिंदी में: Reflow बनाम Repaint — Browser Layout दोबारा कब बनाता है

---

## 🔵 Simple Definition (English)
**Reflow (layout)** is when the browser recalculates the size and position of elements. **Repaint** is when the browser redraws pixels (colors, shadows) without changing geometry. Reflow is more expensive and always leads to a repaint; a repaint alone is cheaper. Some changes (`transform`, `opacity`) skip both and only need **compositing**.

## 🔵 सरल परिभाषा (Hindi)
**Reflow (layout)** तब होता है जब browser elements का size और position दोबारा calculate करता है। **Repaint** तब होता है जब browser सिर्फ pixels (color, shadow) दोबारा draw करता है, geometry नहीं बदलती। Reflow महँगा है और उसके बाद repaint भी होता है। `transform` और `opacity` दोनों को skip करके सिर्फ **compositing** करते हैं।

---

## 🔴 Problem it Solves
```
PROBLEM: Page feels janky / laggy (below 60fps)
  - Developer animates `width`, `top`, `left` in a loop
  - Every frame: browser recalculates layout of the whole page
  - Reads like el.offsetWidth right after writing el.style.width
    forces a SYNCHRONOUS reflow ("layout thrashing")
  - Result: scroll stutter, slow dropdowns, laggy Instagram-like feeds

WHY NEEDED TO UNDERSTAND:
  - 16.6ms is the budget per frame at 60fps
  - Knowing which CSS property triggers which stage lets you pick the cheap one
```

## 🔴 यह क्यों बना? (Hindi)
```
समस्या: Page अटकता है (60fps से कम)
  - Developer `width`, `top`, `left` को animate करता है
  - हर frame में browser पूरे page का layout दोबारा निकालता है
  - el.style.width लिखने के तुरंत बाद el.offsetWidth पढ़ने से
    browser को ज़बरदस्ती reflow करना पड़ता है ("layout thrashing")
  - नतीजा: scroll में झटके, slow dropdown

ज़रूरत: हर frame का budget सिर्फ 16.6ms होता है।
कौन सी property किस stage को trigger करती है यह पता हो तो सस्ती property चुन सकते हैं।
```

---

## 🟢 How it Works — Step by Step

```
PIPELINE (after first load):

  JS / CSS change
        │
        ▼
  1. Style      → recalculate computed styles
        │
        ▼
  2. Layout     → REFLOW: geometry (width, height, x, y) of affected boxes
        │
        ▼
  3. Paint      → REPAINT: fill pixels (color, background, border, shadow, text)
        │
        ▼
  4. Composite  → GPU combines layers (transform, opacity live here only)

COST:  Layout + Paint + Composite  >  Paint + Composite  >  Composite only

TRIGGERS REFLOW (geometry):
  width, height, margin, padding, border, top/left, display, position,
  font-size, float, flex/grid props, adding/removing DOM nodes, window resize

TRIGGERS REPAINT ONLY (no geometry change):
  color, background-color, visibility, box-shadow, outline, border-color

COMPOSITE ONLY (cheapest, GPU):
  transform, opacity  (and usually filter, with will-change)

READING properties that FORCE a reflow:
  offsetWidth/Height, clientWidth, scrollTop, getBoundingClientRect(),
  getComputedStyle(el).width ...

LAYOUT THRASHING:
  for each item: read height -> write height   (reflow every iteration!)
FIX: batch all reads first, then all writes. Or use requestAnimationFrame.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Pipeline: Style -> Layout (Reflow) -> Paint (Repaint) -> Composite

1. Style     : computed styles दोबारा बनते हैं
2. Layout    : हर element की जगह और size फिर से निकलती है (महँगा)
3. Paint     : pixels भरे जाते हैं (color, shadow, text)
4. Composite : GPU layers जोड़ता है (transform, opacity सिर्फ यहाँ)

Reflow trigger: width, height, margin, padding, top/left, font-size,
                DOM में node add/remove, window resize
Repaint trigger: color, background-color, box-shadow, visibility
सबसे सस्ता: transform, opacity

Layout thrashing: loop में पहले पढ़ना फिर लिखना, बार-बार reflow।
हल: पहले सारे reads, फिर सारे writes। या requestAnimationFrame।
```

---

## 🟡 Real World Example
**Instagram feed:** When you scroll, the feed must stay at 60fps. If a "like" heart animated using `top` and `width`, every like would reflow neighbouring posts. Instead the heart burst uses `transform: scale()` and `opacity`, which the GPU composites without touching layout. Similarly, **Zomato's** sticky "View Cart" bar slides up with `transform: translateY()` rather than animating `bottom`.

## 🟡 Real Example Hindi mein
**Instagram feed:** Scroll करते समय feed 60fps पर चलना चाहिए। अगर "like" का heart `top` और `width` से animate होता तो हर like पर आसपास की posts का reflow होता। इसलिए heart `transform: scale()` और `opacity` से animate होता है, जो GPU पर चलता है और layout को छूता नहीं। **Zomato** का "View Cart" bar भी `bottom` की जगह `transform: translateY()` से ऊपर आता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reflow vs Repaint Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: sans-serif; padding: 20px; background: #f5f5f5; }

    .stage { background: #fff; border: 1px solid #ddd; padding: 12px; margin-bottom: 16px; height: 90px; overflow: hidden; }

    .box { width: 60px; height: 60px; background: #1976d2; border-radius: 6px; }

    /* ❌ BAD: animating `margin-left` triggers LAYOUT every frame */
    .bad { animation: moveBad 2s ease-in-out infinite alternate; }
    @keyframes moveBad { from { margin-left: 0; } to { margin-left: 300px; } }

    /* ✅ GOOD: animating `transform` is composite-only (GPU) */
    .good { background: #2e7d32; animation: moveGood 2s ease-in-out infinite alternate; }
    @keyframes moveGood { from { transform: translateX(0); } to { transform: translateX(300px); } }

    /* Repaint only: color change, geometry unchanged */
    .paint { transition: background-color .3s; }
    .paint:hover { background: #c62828; }

    button { padding: 8px 14px; cursor: pointer; margin-right: 8px; }
    #log { font-family: monospace; background: #222; color: #0f0; padding: 10px; white-space: pre-wrap; }
  </style>
</head>
<body>
  <h1>Reflow vs Repaint</h1>

  <p>❌ Layout animation (margin-left)</p>
  <div class="stage"><div class="box bad"></div></div>

  <p>✅ Composite animation (transform)</p>
  <div class="stage"><div class="box good"></div></div>

  <p>🎨 Repaint only (hover me)</p>
  <div class="stage"><div class="box paint"></div></div>

  <!-- Layout thrashing vs batching demo -->
  <button id="thrash">Thrash (read+write in loop)</button>
  <button id="batch">Batch (reads then writes)</button>
  <ul id="list"></ul>
  <div id="log">Click a button to measure...</div>

  <script>
    // Build 2000 list items
    const list = document.getElementById('list');
    for (let i = 0; i < 2000; i++) {
      const li = document.createElement('li');
      li.textContent = 'Item ' + i;
      list.appendChild(li);
    }
    const items = Array.from(list.children);
    const log = document.getElementById('log');

    // BAD: read offsetHeight then write style, forces reflow on every iteration
    document.getElementById('thrash').onclick = () => {
      const t = performance.now();
      items.forEach(li => {
        const h = li.offsetHeight;          // READ  -> forces layout
        li.style.paddingLeft = (h % 10) + 'px'; // WRITE -> invalidates layout
      });
      log.textContent = 'Thrash: ' + (performance.now() - t).toFixed(1) + ' ms';
    };

    // GOOD: do all reads first, then all writes -> one reflow
    document.getElementById('batch').onclick = () => {
      const t = performance.now();
      const heights = items.map(li => li.offsetHeight); // all READS
      items.forEach((li, i) => {
        li.style.paddingLeft = (heights[i] % 10) + 'px'; // all WRITES
      });
      log.textContent = 'Batch: ' + (performance.now() - t).toFixed(1) + ' ms';
    };
  </script>
</body>
</html>
```

```css
/* Cheat rule for animations:
   Only animate transform and opacity. */
.toast {
  transform: translateY(100%);   /* hidden below screen */
  opacity: 0;
  transition: transform .3s ease, opacity .3s ease;
}
.toast.show { transform: translateY(0); opacity: 1; }
```

---

## 🟠 React/Next.js Connection

```jsx
import { useLayoutEffect, useRef, useState } from 'react';

// 1. Read layout in useLayoutEffect (runs before paint), write once.
function Tooltip({ children }) {
  const ref = useRef(null);
  const [pos, setPos] = useState({ top: 0, left: 0 });

  useLayoutEffect(() => {
    const rect = ref.current.getBoundingClientRect(); // one READ
    setPos({ top: rect.bottom + 8, left: rect.left });  // one WRITE (state)
  }, []);

  return <span ref={ref} data-top={pos.top}>{children}</span>;
}

// 2. Animate with transform, not top/left:
<div className="transition-transform duration-300 translate-y-0 hover:-translate-y-1" />
// Tailwind: transform utilities (translate-*, scale-*) = composite-only

// 3. Avoid inline style changes in a loop; change a className instead.
// 4. Long lists: use virtualization (react-window) to keep DOM small,
//    since reflow cost grows with DOM size.
// 5. React batches state updates, but DOM reads inside effects still
//    force layout - read once, store in a ref.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between reflow and repaint?**
A1: Reflow (layout) recalculates geometry: size and position of elements. Repaint redraws pixels when look changes but geometry does not (color, shadow). Reflow always causes a repaint of the affected area; a repaint does not need a reflow.

**Q2: Which CSS properties trigger reflow, repaint, or neither?**
A2: Reflow: `width`, `height`, `margin`, `padding`, `top/left`, `font-size`, `display`. Repaint only: `color`, `background-color`, `box-shadow`, `visibility`. Neither (composite only): `transform`, `opacity`. Always check csstriggers-style tables or DevTools Performance panel for the exact result.

**Q3: What is layout thrashing and how do you avoid it?**
A3: Alternating DOM reads (`offsetHeight`, `getBoundingClientRect`) and writes (`style.x = ...`) in a loop forces the browser to run layout synchronously every iteration. Avoid it by batching all reads, then all writes, or by using `requestAnimationFrame`, or libraries like fastdom.

**Q4: Why is `transform` better than `left/top` for animation?**
A4: `transform` does not affect layout, so the browser skips Layout and Paint; the element is promoted to its own compositor layer and the GPU moves it. `left/top` changes geometry, forcing layout of the element and possibly its neighbours every frame.

**Q5: Does `display: none` vs `visibility: hidden` differ for reflow?**
A5: `display: none` removes the element from layout, so toggling it causes reflow. `visibility: hidden` keeps its space, so toggling it only causes a repaint. `opacity: 0` keeps space and is composite-only.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Animating layout properties
```css
/* WRONG: reflow every frame */
.drawer { transition: left .3s; left: -300px; }
/* CORRECT: composite only */
.drawer { transition: transform .3s; transform: translateX(-300px); }
```

❌ **Mistake 2:** Read-write interleaving
```js
// WRONG
els.forEach(e => { e.style.width = e.offsetWidth + 10 + 'px'; });
// CORRECT
const w = els.map(e => e.offsetWidth);
els.forEach((e, i) => { e.style.width = w[i] + 10 + 'px'; });
```

❌ **Mistake 3:** Appending nodes one by one to the live DOM
```js
// WRONG: 1000 reflows potential
for (...) list.appendChild(li);
// CORRECT: build in a DocumentFragment, append once
const frag = document.createDocumentFragment();
for (...) frag.appendChild(li);
list.appendChild(frag);
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Reflow / Layout | Recalculate size and position | Size/position दोबारा निकालना |
| Repaint | Redraw pixels without geometry change | Pixels दोबारा बनाना |
| Compositing | GPU merges layers | GPU से layers जोड़ना |
| Layout thrashing | Repeated forced reflows | बार-बार ज़बरदस्ती reflow |
| requestAnimationFrame | Run code before next frame | अगले frame से पहले code चलाना |
| DocumentFragment | Off-DOM container for batching | Batch में DOM जोड़ने का container |
| 60fps | 16.6ms per frame | हर frame 16.6ms |

---

## ⚡ 3-Line Summary
**English:**
1. Reflow recalculates geometry, repaint redraws pixels; reflow is costlier and always implies repaint.
2. `transform` and `opacity` skip layout and paint, so use them for animations.
3. Avoid layout thrashing: batch DOM reads then writes, use fragments and `requestAnimationFrame`.

**Hindi:**
1. Reflow geometry निकालता है, repaint pixels बनाता है; reflow महँगा है।
2. `transform` और `opacity` layout/paint skip करते हैं, animation में यही use करो।
3. Layout thrashing से बचो: पहले reads फिर writes, fragment और `requestAnimationFrame` use करो।

---

## ➡️ Next Topic
**38. HTML Performance Optimization** — reflow समझने के बाद अब पूरे page को तेज़ कैसे बनाएँ: images, scripts, preload, lazy loading।
