# 96. CSS Will-change Property
# हिंदी में: CSS will-change — Browser को पहले से हिंट देना

---

## 🔵 Simple Definition (English)
`will-change` is a **performance hint**. It tells the browser which property of an element is **about to change** (for example `transform` or `opacity`), so the browser can prepare (often by promoting the element to its own GPU layer) before the animation starts.

## 🔵 सरल परिभाषा (Hindi)
`will-change` एक **performance hint** है। ये browser को बताता है कि element की कौन सी property **जल्द बदलने वाली** है (जैसे `transform` या `opacity`), ताकि browser animation शुरू होने से पहले तैयारी कर ले (अक्सर element को अलग GPU layer में डालकर)।

---

## 🔴 Problem it Solves
```
WITHOUT will-change:
  User hovers a card → browser must NOW create a layer, upload the texture to the GPU,
  and then start animating → first frames stutter ("jank at the start of animation").

WITH will-change (used correctly):
  .card:hover-zone { will-change: transform; }   /* "heads up, transform will change" */
  Browser prepares the layer BEFORE the animation, so the first frame is already smooth.

BUT misuse (will-change on everything):
  → every element gets its own layer → big GPU memory use, slower page on phones.
  will-change is an EMERGENCY / fine-tuning tool, not a default.
```

## 🔴 यह क्यों बना? (Hindi)
Animation शुरू होते ही browser को layer बनानी पड़ती है और GPU पर texture भेजनी पड़ती है — इससे शुरुआती frames अटकते हैं। `will-change` से browser पहले से तैयार हो जाता है। लेकिन हर जगह लगाने पर memory ज़्यादा खर्च होती है, इसलिए इसे सोच-समझकर और थोड़े समय के लिए लगाओ।

---

## 🟢 How it Works — Step by Step

```
SYNTAX:
  will-change: auto;                       /* default, no hint */
  will-change: transform;                  /* one property */
  will-change: transform, opacity;         /* several */
  will-change: scroll-position;            /* scroller will be scrolled */
  will-change: contents;                   /* content will change a lot */

WHAT THE BROWSER DOES (implementation detail, not guaranteed):
  1. Sees will-change: transform (or opacity, filter...)
  2. Promotes the element to its own COMPOSITING LAYER (GPU texture)
  3. Animation then only moves/blends that layer; no re-layout, no re-paint of neighbors
  4. Side effect: will-change: transform / opacity (and others) creates a NEW STACKING CONTEXT
     and a containing block for position: fixed descendants (same as transform does)

RULES (from MDN / Google):
  1. DO NOT apply to many elements ("* { will-change: transform }" is harmful).
  2. DO NOT leave it on forever — remove it when the animation ends.
  3. Use it as a LAST RESORT after you see an actual problem in DevTools.
  4. Apply it just BEFORE the change, e.g. on :hover of the PARENT, or add the
     class with JS on mouseenter / animation start and remove on animationend.
  5. Do not use it for premature optimization.
  6. Do not use will-change on properties that are not going to change.

BEST PATTERNS:
  A. Hover on parent prepares the child:
       .card-wrap:hover .card { will-change: transform; }
       .card { transition: transform .25s; }
       .card:hover { transform: scale(1.05); }
  B. JS toggles it only while needed:
       el.style.willChange = 'transform';    // before animation
       el.addEventListener('transitionend', () => el.style.willChange = 'auto', { once: true });
  C. Permanent only for few special elements: fixed headers, full-screen sliders,
     map canvases, sticky video panels that always animate.

OLD HACK vs NEW:
  transform: translateZ(0);   /* old "force GPU layer" hack */
  backface-visibility: hidden;
  → replaced by will-change: transform (clearer intent).

WHAT TO ANIMATE (reminder):
  Only properties the compositor can handle benefit: transform, opacity, filter (and
  backdrop-filter in many browsers). will-change: width does not make width cheap.

SUPPORT: Chrome 36+, Firefox 36+, Safari 9.1+, Edge 79+. Unsupported browsers ignore it.
```

## 🟢 कैसे काम करता है? (Hindi)
1. `will-change: transform` लिखते ही browser element को अपनी **compositing layer** (GPU texture) में डाल देता है।
2. Animation के समय सिर्फ वो layer हिलती है; बाकी page का layout/paint दोबारा नहीं चलता।
3. **साइड इफेक्ट:** नया **stacking context** बनता है और `position: fixed` बच्चों के लिए containing block बन जाता है (जैसे `transform` में होता है)।
4. **नियम:** बहुत सारे elements पर मत लगाओ; animation खत्म होते ही हटाओ; पहले असली problem देखो (DevTools), फिर लगाओ।
5. **सही तरीका:** parent पर hover होते ही child को hint दो, या JS से animation से ठीक पहले लगाओ और `transitionend` पर `auto` कर दो।
6. पुराना hack `translateZ(0)` अब `will-change: transform` से बदला जा चुका है।

---

## 🟡 Real World Example
**Google Maps / Figma web:** Canvas ya map layer jo hamesha pan/zoom hoti rehti hai, uspar `will-change: transform` permanent hota hai, kyunki wo continuously animate hoti hai.
**Instagram Stories / Tinder-style swipe cards:** Card par touch shuru hote hi JS `will-change: transform` lagata hai, drag ke dauran smooth movement milta hai, aur release ke baad hata diya jata hai.
**Zomato / Swiggy bottom sheet / side drawer:** Menu button click se pehle drawer par hint dena, taaki slide-in ke pehle frame me stutter na ho.
**Amazon product hover zoom:** Image container par hover hone se pehle `will-change: transform`.

## 🟡 Real Example Hindi mein
**Google Maps / Figma:** Map या canvas हमेशा pan/zoom होता रहता है, इसलिए उस पर `will-change: transform` स्थायी रहता है।
**Instagram Stories / Tinder जैसे swipe cards:** Touch शुरू होते ही JS `will-change` लगाता है, drag smooth चलता है, छोड़ने पर हटा देता है।
**Zomato/Swiggy side drawer:** Menu button click से पहले drawer पर hint देने से slide-in का पहला frame अटकता नहीं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CSS will-change Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; background: #f5f5f5; padding: 20px; margin: 0; }
    h2 { margin: 24px 0 8px; font-size: 16px; border-bottom: 2px solid #333; padding-bottom: 4px; }

    /* ─── 1. PARENT HOVER PREPARES THE CHILD (best pattern) ───────── */
    .card-wrap { display: inline-block; padding: 16px; }     /* bigger hover zone than the card */
    .card {
      width: 180px; padding: 20px; background: #fff; border-radius: 12px;
      box-shadow: 0 2px 6px rgba(0,0,0,.15);
      transition: transform .25s ease;                       /* the actual animation */
    }
    /* Hint arrives when the mouse enters the PARENT zone, just before the card is hovered */
    .card-wrap:hover .card { will-change: transform; }
    .card:hover { transform: translateY(-6px) scale(1.04); }

    /* ─── 2. SLIDE-IN DRAWER (JS adds hint only during animation) ─── */
    .drawer {
      position: fixed; top: 0; right: 0; height: 100%; width: 260px;
      background: #232f3e; color: #fff; padding: 20px;
      transform: translateX(100%);                           /* hidden off-screen */
      transition: transform .3s ease;
    }
    .drawer.open { transform: translateX(0); }

    /* ─── 3. PERMANENT will-change: only for a special always-moving layer ── */
    .marquee { overflow: hidden; background: #fff; border-radius: 8px; white-space: nowrap; }
    .marquee-track {
      display: inline-block; padding: 12px 0;
      will-change: transform;                                /* continuous animation → justified */
      animation: scroll-left 12s linear infinite;
    }
    @keyframes scroll-left { from { transform: translateX(100%); } to { transform: translateX(-100%); } }

    /* ─── 4. SIDE EFFECT DEMO: stacking context + fixed containing block ── */
    .parent-hint { will-change: transform; background: #ffe0b2; padding: 10px; height: 80px; position: relative; }
    .parent-hint .fixed-child {
      position: fixed; top: 0; left: 0;                      /* now fixed relative to .parent-hint, not viewport! */
      background: #ef5350; color: #fff; padding: 4px 8px; font-size: 12px;
    }

    @media (prefers-reduced-motion: reduce) {
      .marquee-track { animation: none; }
      .card, .drawer { transition: none; }
    }
  </style>
</head>
<body>
  <h1>will-change</h1>

  <h2>1. Hint on parent hover</h2>
  <div class="card-wrap"><div class="card">Hover the area around me</div></div>

  <h2>2. Drawer: hint only while animating</h2>
  <button id="toggle">Open drawer</button>
  <aside class="drawer" id="drawer">Side drawer content</aside>

  <h2>3. Permanent hint on a continuously animated track</h2>
  <div class="marquee"><div class="marquee-track">Free delivery on orders above Rs 199 • Flat 50% off • New user offer •</div></div>

  <h2>4. Side effect: fixed child is trapped inside</h2>
  <div class="parent-hint">Parent has will-change: transform
    <div class="fixed-child">position: fixed, but stuck to parent</div>
  </div>

  <script>
    const drawer = document.getElementById('drawer');
    document.getElementById('toggle').addEventListener('click', () => {
      // 1) add the hint BEFORE the change
      drawer.style.willChange = 'transform';
      // 2) force the browser to register the hint first, then start the animation next frame
      requestAnimationFrame(() => drawer.classList.toggle('open'));
      // 3) remove the hint when the transition finishes (frees GPU memory)
      drawer.addEventListener('transitionend', () => {
        drawer.style.willChange = 'auto';
      }, { once: true });
    });
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Add the hint on interaction with a state or ref, remove it on end:
import { useRef } from 'react';

export default function SwipeCard({ children }) {
  const ref = useRef(null);
  return (
    <div
      ref={ref}
      className="card"
      onPointerDown={() => { ref.current.style.willChange = 'transform'; }}   // before dragging
      onPointerUp={() => { ref.current.style.willChange = 'auto'; }}          // after dragging
    >
      {children}
    </div>
  );
}

// 2. Tailwind utilities:  will-change-transform, will-change-auto, will-change-scroll
//    (Tailwind v3: will-change-transform / v4 has the same names)
<div className="will-change-transform transition-transform hover:-translate-y-1" />
// Avoid putting it on every list item. Apply only to the 1-2 elements that animate.

// 3. Framer Motion / React Spring already apply will-change when needed while animating,
//    so do NOT add it manually to motion components.

// 4. CSS Modules: same CSS as above.
/* Drawer.module.css */
.drawer { transform: translateX(100%); transition: transform .3s; }
.open   { transform: translateX(0); }

// 5. Next.js: nothing special; it is just CSS. Check results with
//    React DevTools Profiler + Chrome Performance panel (Layers panel shows promoted layers).
```

---

## ⚫ Interview Questions + Answers

**Q1: What does `will-change` do?**
A1: It is a hint that tells the browser which properties of an element will change, so it can optimize ahead of time, usually by creating a separate compositing layer. It removes the start-up stutter of animations. It does not make any property cheaper by itself; it only prepares.

**Q2: Why is it dangerous to overuse `will-change`?**
A2: Each promoted element consumes GPU memory for its texture and adds compositing work. Putting it on many elements (or `*`) can slow the page and crash low-memory devices. It can also create unexpected stacking contexts and containing blocks. MDN says to use it as a last resort for existing problems, not for premature optimization.

**Q3: How and when should you apply and remove it?**
A3: Apply shortly before the change (parent `:hover`, `pointerdown`, `mouseenter`, or JS right before adding a class) and remove it afterwards (`transitionend` / `animationend`, set `auto`). Permanent usage is acceptable only for elements that animate constantly (a map canvas, marquee, always-moving slider).

**Q4: What side effects does `will-change: transform` have?**
A4: Like `transform`, it creates a new stacking context (affects `z-index` behavior) and becomes the containing block for `position: fixed` and `absolute` descendants. A fixed header inside such a parent will no longer be fixed to the viewport. Also, text may render differently (grayscale anti-aliasing) on some browsers.

**Q5: `will-change: transform` vs `transform: translateZ(0)` hack?**
A5: Both historically promote the element to a GPU layer. `translateZ(0)` / `backface-visibility: hidden` were hacks with side effects (it applies a real transform). `will-change` is the standard, intention-revealing way, can be removed without altering visuals, and can target specific properties (`opacity`, `scroll-position`).

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Applying to everything
```css
/* WRONG: hundreds of GPU layers, memory blowup */
* { will-change: transform; }
.card { will-change: transform, opacity; }   /* on 500 cards */

/* CORRECT: only where animating, only when needed */
.card-wrap:hover .card { will-change: transform; }
```

❌ **Mistake 2:** Leaving it on after the animation
```js
// WRONG: set once and forget
el.style.willChange = 'transform';

// CORRECT: remove when done
el.addEventListener('transitionend', () => { el.style.willChange = 'auto'; }, { once: true });
```

❌ **Mistake 3:** Setting it on the same element in the same frame as the change
```css
/* WRONG: hint and change arrive together, no time to prepare */
.card:hover { will-change: transform; transform: scale(1.1); }

/* CORRECT: hint on the parent (earlier trigger), change on the child */
.card-wrap:hover .card { will-change: transform; }
```

❌ **Mistake 4:** Hinting properties that cannot be composited
```css
/* WRONG: width still triggers layout on each frame */
.panel { will-change: width; transition: width .3s; }

/* CORRECT: animate transform instead */
.panel { will-change: transform; transition: transform .3s; }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| will-change | Hint about upcoming property change | आने वाले बदलाव का संकेत |
| Compositing layer | Separate GPU texture for an element | अलग GPU layer |
| Compositor | Thread combining layers | Layers जोड़ने वाला thread |
| Jank | Visible stutter in animation | Animation में अटकना |
| Stacking context | Isolated z-index scope | z-index का अलग scope |
| Containing block | Reference box for positioned descendants | Positioned बच्चों का reference box |
| Premature optimization | Optimizing without a measured problem | बिना ज़रूरत optimization |
| translateZ(0) hack | Old way to force a GPU layer | GPU layer का पुराना hack |

---

## ⚡ 3-Line Summary
**English:**
1. `will-change` hints which property will change so the browser can prepare a GPU layer before the animation.
2. Use sparingly: apply just before animation (parent hover, pointerdown), remove after (`auto`); constant use only for always-animating layers.
3. It creates a stacking context and fixed-position containing block, and misuse wastes GPU memory.

**Hindi:**
1. `will-change` browser को बताता है कि कौन सी property बदलेगी ताकि animation से पहले GPU layer तैयार हो जाए।
2. कम इस्तेमाल करो: animation से ठीक पहले लगाओ, बाद में `auto` करो; हमेशा चलने वाली layers पर ही स्थायी रखो।
3. ये stacking context और fixed-containing block बनाता है, और गलत use से GPU memory बर्बाद होती है।

---

## ➡️ Next Topic
**97. CSS Scroll Behavior + Snap** — smooth scrolling और carousel जैसा snapping बिना JavaScript के।
