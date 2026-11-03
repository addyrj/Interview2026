# 97. CSS Scroll Behavior + Snap
# हिंदी में: CSS Scroll Behavior और Scroll Snap — बिना JS के Smooth Scroll और Carousel

---

## 🔵 Simple Definition (English)
`scroll-behavior: smooth` makes in-page jumps (anchor links, `scrollTo`) **animate** instead of jumping. **Scroll Snap** (`scroll-snap-type`, `scroll-snap-align`) makes a scroll container **stop at defined points**, like slides in a carousel, using only CSS.

## 🔵 सरल परिभाषा (Hindi)
`scroll-behavior: smooth` से anchor links और `scrollTo` झटके से कूदने की जगह **smooth animate** होते हैं। **Scroll Snap** (`scroll-snap-type`, `scroll-snap-align`) से scroll container तय बिंदुओं पर **रुकता** है, जैसे carousel के slides — सिर्फ CSS से।

---

## 🔴 Problem it Solves
```
BEFORE:
  <a href="#pricing">Pricing</a>   → page JUMPS instantly, user loses context.
  Fix needed JavaScript:  window.scrollTo({ top, behavior: 'smooth' }) or jQuery animate().

  Carousel / slider needed a JS library (Swiper, Slick, 30-60 KB):
    touch events, momentum math, snapping logic, resize handling...

NOW (pure CSS):
  html { scroll-behavior: smooth; }                       → smooth anchor jumps
  .slider { overflow-x: auto; scroll-snap-type: x mandatory; }
  .slide  { scroll-snap-align: start; }                   → native swipe + snapping, GPU-fast, accessible
```

## 🔴 यह क्यों बना? (Hindi)
पहले anchor link पर page झटके से कूदता था और smooth करने के लिए JS लिखनी पड़ती थी। Carousel के लिए Swiper/Slick जैसी भारी library चाहिए थी (touch events, snapping math)। अब सिर्फ कुछ CSS lines से native, तेज़ और accessible slider बन जाता है।

---

## 🟢 How it Works — Step by Step

```
PART 1: scroll-behavior
──────────────────────────────────────────────────────────
  html { scroll-behavior: smooth; }       /* applies to page-level scrolling */
  .box { scroll-behavior: smooth; }       /* or to any scroll container */
  Affects: anchor link jumps (#id), element.scrollIntoView(), window.scrollTo() (without explicit behavior),
           find-in-page does NOT animate.
  Values: auto (default, instant) | smooth
  ACCESSIBILITY (important):
    @media (prefers-reduced-motion: no-preference) { html { scroll-behavior: smooth; } }
  Fixed header covers the target? Use  scroll-margin-top  on the target (or scroll-padding-top on html).

PART 2: SCROLL SNAP
──────────────────────────────────────────────────────────
  Needs TWO sides:
  A) CONTAINER (the scroller):
       scroll-snap-type: <axis> <strictness>;
         axis:       x | y | both | block | inline
         strictness: mandatory  → always rests on a snap point
                     proximity  → snaps only if close (friendlier for long content)
       scroll-padding: 16px;          /* offset for snapping area (like for sticky header) */
       overflow-x: auto;              /* container must actually scroll */

  B) CHILDREN (snap points):
       scroll-snap-align: start | center | end;
       scroll-snap-stop: normal | always;    /* always = cannot skip a slide on a fast swipe */
       scroll-margin: 8px;                    /* offset for this child's snap position */

  EXAMPLE FLOW (horizontal slider):
    .slider { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; gap: 16px; }
    .slide  { flex: 0 0 80%; scroll-snap-align: center; }
    → user swipes; browser animates to nearest center point.

  FULL-PAGE SECTIONS (like Apple-style landing pages):
    html { scroll-snap-type: y proximity; }       /* proximity is kinder than mandatory */
    section { min-height: 100vh; scroll-snap-align: start; }

  HIDE the scrollbar (optional, cosmetic):
    .slider { scrollbar-width: none; }                      /* Firefox + modern Chrome */
    .slider::-webkit-scrollbar { display: none; }           /* older Chrome/Safari */
    Caution: keep keyboard/mouse users able to scroll (add prev/next buttons).

  OTHER RELATED:
    overscroll-behavior: contain;   /* stop scroll chaining to the page behind a modal/scroller */
    scrollbar-gutter: stable;       /* reserve space for scrollbar, avoids layout shift */
    scroll-snap-type + JS: el.scrollTo({ left: x, behavior: 'smooth' }) for prev/next buttons.
    Newer: scroll-driven animations (animation-timeline: scroll()) - different topic, Chrome/Edge 115+.
    scroll-snap-type events: scrollsnapchange (new, Chrome 129+). Do not rely on it widely yet.

SUPPORT: scroll-behavior: Chrome 61+, Firefox 36+, Safari 15.4+. Scroll snap: all modern browsers (Chrome 69+, Firefox 68+, Safari 11+).
         scrollbar-width: Firefox 64+, Chrome 121+, Safari 18.2+.
```

## 🟢 कैसे काम करता है? (Hindi)
1. `html { scroll-behavior: smooth }` — anchor jumps और `scrollIntoView()` animate होते हैं। `prefers-reduced-motion` का सम्मान करो।
2. Fixed header target को ढक दे तो target पर `scroll-margin-top` या `html` पर `scroll-padding-top` दो।
3. **Snap के दो हिस्से:** container पर `scroll-snap-type: x mandatory` (और `overflow-x: auto`), बच्चों पर `scroll-snap-align: start/center/end`।
4. `mandatory` = हमेशा snap point पर रुकेगा; `proximity` = पास हो तभी snap (लंबे content के लिए बेहतर)।
5. `scroll-snap-stop: always` से तेज़ swipe में भी slide skip नहीं होती।
6. Prev/Next buttons के लिए `el.scrollBy({ left: 300, behavior: 'smooth' })`।
7. `overscroll-behavior: contain` से modal के scroll का असर पीछे के page पर नहीं पड़ता।

---

## 🟡 Real World Example
**Instagram Stories / Netflix rows / Amazon "Customers also viewed":** Horizontal row jisme swipe karte hi card apni jagah par "snap" ho jata hai — CSS scroll snap se.
**Swiggy / Zomato home page:** Top "What's on your mind?" category strip aur offer banners horizontal scroll + snap.
**Apple product pages, landing pages:** Full-screen sections me `scroll-snap-type: y proximity`.
**Documentation sites (MDN, Docusaurus):** Sidebar link click par smooth scroll with `scroll-margin-top` so heading is not hidden under the sticky navbar.
**Image galleries on mobile:** Photo carousel with `scroll-snap-align: center`.

## 🟡 Real Example Hindi mein
**Instagram Stories / Netflix rows / Amazon:** Horizontal row में swipe करते ही card अपनी जगह पर "snap" हो जाता है — CSS scroll snap से।
**Swiggy/Zomato home:** ऊपर की category strip और offer banners horizontal scroll + snap होते हैं।
**Apple landing pages:** Full-screen sections में `scroll-snap-type: y proximity`।
**Docs sites:** Sidebar link पर smooth scroll और `scroll-margin-top` ताकि heading sticky navbar के नीचे न छुपे।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Scroll Behavior + Snap</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }

    /* ─── 1. SMOOTH SCROLL (only for users who allow motion) ──────── */
    @media (prefers-reduced-motion: no-preference) {
      html { scroll-behavior: smooth; }
    }
    /* leave space for the sticky header when jumping to #anchors */
    html { scroll-padding-top: 70px; }

    body { font-family: system-ui, sans-serif; margin: 0; background: #f5f5f5; color: #222; }

    /* sticky navbar with anchor links */
    .nav {
      position: sticky; top: 0; z-index: 10;
      display: flex; gap: 16px; padding: 14px 20px; background: #232f3e;
    }
    .nav a { color: #fff; text-decoration: none; }

    section.block { padding: 40px 20px; min-height: 60vh; }
    section.block:nth-of-type(even) { background: #fff; }
    h2 { margin-top: 0; }

    /* ─── 2. HORIZONTAL SNAP CAROUSEL ─────────────────────────────── */
    .slider {
      display: flex; gap: 16px;
      overflow-x: auto;                       /* container must be scrollable */
      scroll-snap-type: x mandatory;          /* snap on the x axis, always rest on a slide */
      scroll-padding: 0 20px;                 /* snap offset so the slide does not touch the edge */
      padding: 4px 20px 16px;
      overscroll-behavior-x: contain;         /* do not trigger browser back-swipe at the edge */
      scrollbar-width: thin;
    }
    .slide {
      flex: 0 0 80%;                          /* each slide is 80% wide so the next one peeks */
      max-width: 360px; height: 180px;
      border-radius: 14px; color: #fff; font-size: 24px;
      display: grid; place-items: center;
      scroll-snap-align: center;              /* this child's center aligns with container center */
      scroll-snap-stop: always;               /* cannot skip slides with a fast flick */
    }
    .slide:nth-child(1) { background: #e23744; }
    .slide:nth-child(2) { background: #ff9800; }
    .slide:nth-child(3) { background: #2e7d32; }
    .slide:nth-child(4) { background: #1976d2; }
    .slide:nth-child(5) { background: #8e24aa; }

    .controls { padding: 0 20px 20px; display: flex; gap: 8px; }
    .controls button { padding: 8px 14px; border: 0; border-radius: 6px; background: #232f3e; color: #fff; cursor: pointer; }

    /* ─── 3. VERTICAL snap (pager) ────────────────────────────────── */
    .pager {
      height: 220px; overflow-y: auto; width: 260px;
      scroll-snap-type: y proximity;          /* proximity: gentle snapping */
      background: #fff; border-radius: 12px; border: 1px solid #ddd;
    }
    .pager > div { height: 220px; display: grid; place-items: center; font-size: 20px; scroll-snap-align: start; }
    .pager > div:nth-child(odd)  { background: #e3f2fd; }
    .pager > div:nth-child(even) { background: #fce4ec; }
  </style>
</head>
<body>

  <nav class="nav">
    <a href="#carousel">Carousel</a>
    <a href="#pager-sec">Pager</a>
    <a href="#footer-sec">Footer</a>
  </nav>

  <section class="block" id="carousel">
    <h2>Snap carousel (swipe or use buttons)</h2>
  </section>
  <div class="slider" id="slider">
    <div class="slide">Biryani</div>
    <div class="slide">Pizza</div>
    <div class="slide">Burger</div>
    <div class="slide">Dosa</div>
    <div class="slide">Momos</div>
  </div>
  <div class="controls">
    <button id="prev">Prev</button>
    <button id="next">Next</button>
  </div>

  <section class="block" id="pager-sec">
    <h2>Vertical snap (proximity)</h2>
    <div class="pager">
      <div>Page 1</div><div>Page 2</div><div>Page 3</div>
    </div>
  </section>

  <section class="block" id="footer-sec">
    <h2>Footer section</h2>
    <p>Navbar link jumped here smoothly and the heading is NOT hidden under the sticky bar (scroll-padding-top).</p>
  </section>

  <script>
    // Prev/Next buttons: smooth scrolling still works, snapping finishes the move
    const slider = document.getElementById('slider');
    const step = () => slider.querySelector('.slide').offsetWidth + 16;   // slide width + gap
    document.getElementById('next').onclick = () => slider.scrollBy({ left:  step(), behavior: 'smooth' });
    document.getElementById('prev').onclick = () => slider.scrollBy({ left: -step(), behavior: 'smooth' });
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Global smooth scroll in Next.js: globals.css
/* globals.css */
@media (prefers-reduced-motion: no-preference) {
  html { scroll-behavior: smooth; }
}
/* Next.js note: on route change, the App Router may skip smooth scrolling for
   "scroll to top" navigation. Add data-scroll-behavior="smooth" on <html>
   (supported in newer Next.js versions) — check docs for your version. */

// 2. Tailwind utilities:
//    scroll-smooth                      → scroll-behavior: smooth
//    snap-x snap-mandatory              → scroll-snap-type: x mandatory
//    snap-center / snap-start           → scroll-snap-align
//    snap-always                        → scroll-snap-stop: always
//    scroll-mt-20 / scroll-pt-20        → scroll-margin-top / scroll-padding-top
export default function Carousel({ items }) {
  return (
    <div className="flex gap-4 overflow-x-auto snap-x snap-mandatory px-5 pb-4">
      {items.map((it) => (
        <div key={it.id} className="snap-center snap-always shrink-0 basis-4/5 h-44 rounded-2xl bg-orange-500">
          {it.title}
        </div>
      ))}
    </div>
  );
}

// 3. Prev/Next buttons with a ref:
import { useRef } from 'react';
function Slider() {
  const ref = useRef(null);
  const go = (dir) => ref.current.scrollBy({ left: dir * 300, behavior: 'smooth' });
  return (
    <>
      <div ref={ref} className="flex overflow-x-auto snap-x snap-mandatory">...</div>
      <button onClick={() => go(-1)}>Prev</button>
      <button onClick={() => go(1)}>Next</button>
    </>
  );
}

// 4. next/link with hash links + sticky header:
//    <Link href="#pricing">Pricing</Link>  with  <section id="pricing" className="scroll-mt-20">

// 5. Need dots/indicators or autoplay? Use IntersectionObserver or a library
//    (Embla Carousel is a small one) — CSS snap alone does not give "current slide" state.
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you make anchor-link scrolling smooth in CSS?**
A1: `html { scroll-behavior: smooth; }`. It also affects `scrollIntoView()` and `scrollTo()` calls without an explicit behavior. Wrap it in `@media (prefers-reduced-motion: no-preference)` for accessibility. If a sticky header hides the heading, add `scroll-padding-top` on `html` or `scroll-margin-top` on the target.

**Q2: How does CSS scroll snap work?**
A2: Two parts: the scroll container sets `scroll-snap-type: x|y|both mandatory|proximity` and must be scrollable (`overflow: auto`); each child sets `scroll-snap-align: start|center|end`. After scrolling, the browser settles at a snap point. `mandatory` always snaps; `proximity` only when close. `scroll-snap-stop: always` stops fast swipes from skipping items.

**Q3: `mandatory` vs `proximity`: which to choose?**
A3: `mandatory` suits carousels where every position must be a slide. `proximity` suits long page sections or content taller than the viewport, since `mandatory` can make parts of tall content unreachable or feel like a scroll trap. Always test on touch devices and with keyboard.

**Q4: What is the difference between `scroll-padding` and `scroll-margin`?**
A4: `scroll-padding` is set on the **scroll container** and shrinks the "snapport" (like an inset), useful for a sticky header or edge gutters. `scroll-margin` is set on the **child/target** and offsets its own snap area or anchor target. Common use: `html { scroll-padding-top: 70px }` or `h2 { scroll-margin-top: 70px }`.

**Q5: Can CSS scroll snap replace carousel libraries? What does it lack?**
A5: For simple swipe carousels, yes: native momentum, accessible, no JS, performant. It lacks: built-in prev/next buttons, pagination dots / active slide state, autoplay, infinite loop, and cross-browser consistency of the newest APIs. You add small JS (`scrollBy`, `IntersectionObserver`) or use a light library such as Embla.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Smooth scroll ignoring reduced-motion users
```css
/* WRONG */
html { scroll-behavior: smooth; }

/* CORRECT */
@media (prefers-reduced-motion: no-preference) {
  html { scroll-behavior: smooth; }
}
```

❌ **Mistake 2:** Forgetting `overflow` on the container
```css
/* WRONG: nothing scrolls, so nothing snaps */
.slider { display: flex; scroll-snap-type: x mandatory; }

/* CORRECT */
.slider { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; }
```

❌ **Mistake 3:** Snap type on the container without `scroll-snap-align` on children
```css
/* WRONG: no snap points exist */
.slide { flex: 0 0 80%; }

/* CORRECT */
.slide { flex: 0 0 80%; scroll-snap-align: center; }
```

❌ **Mistake 4:** `y mandatory` on the whole page with tall sections
```css
/* WRONG: sections taller than the viewport cannot be fully read */
html { scroll-snap-type: y mandatory; }

/* CORRECT */
html { scroll-snap-type: y proximity; }
```

❌ **Mistake 5:** Sticky header hides the anchor target
```css
/* WRONG: heading sits behind the header after a jump */

/* CORRECT */
html { scroll-padding-top: 70px; }   /* or  h2 { scroll-margin-top: 70px; } */
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| scroll-behavior | Smooth or instant programmatic scroll | Scroll का तरीका |
| scroll-snap-type | Container snapping rule | Container का snap नियम |
| scroll-snap-align | Where a child snaps | Child कहाँ रुके |
| mandatory | Always snaps | हमेशा snap |
| proximity | Snaps if close | पास हो तो snap |
| scroll-snap-stop | Force stopping at each item | हर item पर रुकना |
| scroll-padding | Container-side snap offset | Container की तरफ offset |
| scroll-margin | Item-side snap offset | Item की तरफ offset |
| overscroll-behavior | Control scroll chaining | Scroll आगे जाने का नियंत्रण |

---

## ⚡ 3-Line Summary
**English:**
1. `scroll-behavior: smooth` animates anchor and programmatic scrolling; guard it with `prefers-reduced-motion`.
2. Scroll snap = container `scroll-snap-type` + child `scroll-snap-align`; `mandatory` for carousels, `proximity` for long sections.
3. Use `scroll-padding` / `scroll-margin` for sticky headers; add small JS for buttons or indicators.

**Hindi:**
1. `scroll-behavior: smooth` anchor और programmatic scroll को animate करता है; `prefers-reduced-motion` का ध्यान रखो।
2. Scroll snap = container पर `scroll-snap-type` + child पर `scroll-snap-align`; carousel में `mandatory`, लंबे sections में `proximity`।
3. Sticky header के लिए `scroll-padding`/`scroll-margin`; buttons या indicators के लिए थोड़ी JS।

---

## ➡️ Next Topic
**98. CSS Aspect-ratio** — images, videos और cards को बिना padding hack के fixed ratio में रखना।
