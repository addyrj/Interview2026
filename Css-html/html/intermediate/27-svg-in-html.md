# 27. SVG in HTML
# हिंदी में: SVG — Vector Graphics जो हर Size पर Sharp रहें

---

## 🔵 Simple Definition (English)
SVG (Scalable Vector Graphics) is an XML-based image format describing shapes with math (lines, curves, paths) instead of pixels. You can write it **inline** inside HTML as `<svg>...</svg>`, so every shape becomes a DOM element you can style with CSS and control with JavaScript. It stays sharp at any size.

## 🔵 सरल परिभाषा (Hindi)
SVG (Scalable Vector Graphics) एक XML-based format है जो shapes को pixels की जगह math (lines, curves, paths) से describe करता है। इसे HTML के अंदर **inline** `<svg>...</svg>` लिख सकते हैं, तब हर shape एक DOM element बन जाती है जिसे CSS से style और JavaScript से control कर सकते हैं। ये हर size पर sharp रहता है।

---

## 🔴 Problem it Solves
```
BEFORE SVG (PNG/JPG icons):
  - Logo/icon looks blurry when scaled up or on Retina screens.
  - Need icon@1x.png, icon@2x.png, icon@3x.png (3 files + 3 HTTP requests).
  - Cannot change colour with CSS (need a new image for hover/dark mode).
  - Cannot animate parts of the image.

WITH SVG:
  - ONE tiny file (or inline code) that is crisp at any size.
  - fill/stroke change via CSS (currentColor, dark mode, hover).
  - Parts can be animated (stroke draw effect, spinner).
  - Text inside SVG is real text: searchable and accessible.
```

## 🔴 यह क्यों बना? (Hindi)
```
SVG से पहले (PNG/JPG icons):
  - Icon बड़ा करने पर या Retina screen पर blurry दिखता था।
  - icon@1x, @2x, @3x अलग files = 3 HTTP requests।
  - CSS से colour नहीं बदल सकते (hover/dark mode के लिए नई image चाहिए)।
  - Image के हिस्सों को animate नहीं कर सकते।

SVG के साथ:
  - एक छोटी file (या inline code), हर size पर साफ।
  - CSS से fill/stroke बदलना (currentColor, dark mode, hover)।
  - Parts animate हो सकते हैं (spinner, stroke-draw effect)।
  - SVG का text असली text है: searchable और accessible।
```

---

## 🟢 How it Works — Step by Step

```
FOUR WAYS TO USE SVG:
  1. <img src="logo.svg" alt="Logo">     -> cached, simple. CSS/JS CANNOT reach inside.
  2. CSS background-image: url(bg.svg)   -> decorative only.
  3. Inline <svg>...</svg> in HTML       -> full CSS + JS control, no extra request.
  4. <svg><use href="#icon-id"/></svg>   -> reuse one symbol many times (sprite).

KEY ELEMENTS:
  <svg width height viewBox="minX minY width height">
  <rect>  <circle>  <ellipse>  <line>  <polyline>  <polygon>
  <path d="M10 10 L90 90 Z">   M=move L=line C=curve Z=close (most powerful)
  <text>  <g> (group)  <defs>  <symbol>  <use>  <linearGradient>

viewBox (the interview favourite):
  viewBox="0 0 24 24" = the internal coordinate system (a 24x24 grid).
  width/height (or CSS) = how large it is DISPLAYED.
  Browser scales the grid to the display size -> that is why SVG is "scalable".

STYLING PROPERTIES (not background/color like HTML):
  fill (inside colour)   stroke (outline colour)   stroke-width
  fill="currentColor"    -> takes the CSS `color` of the parent (themeable icons!)

ACCESSIBILITY:
  Meaningful svg: role="img" + <title> (or aria-label).
  Decorative svg: aria-hidden="true".
```

## 🟢 कैसे काम करता है? (Hindi)

```
SVG use करने के 4 तरीके:
  1. <img src="logo.svg">         -> simple, cache होता है, पर अंदर CSS/JS नहीं पहुँचता
  2. CSS background-image         -> सिर्फ decoration
  3. Inline <svg> HTML में        -> पूरा CSS + JS control, extra request नहीं
  4. <use href="#id"/>            -> एक symbol बार-बार reuse (sprite)

viewBox="0 0 24 24" = अंदर का coordinate grid (24x24)।
width/height या CSS = screen पर कितना बड़ा दिखे।
Browser grid को display size में scale कर देता है, इसीलिए ये "scalable" है।

Styling: fill (अंदर का रंग), stroke (outline), stroke-width।
fill="currentColor" लगाओ तो icon parent के CSS `color` का रंग ले लेता है।

Accessibility: meaningful svg में role="img" + <title>; सिर्फ सजावट वाले में aria-hidden="true"।
```

---

## 🟡 Real World Example
**Instagram, Gmail and Zomato icons** (heart, search, cart, home) are SVGs: the heart turns red on like via CSS `fill`, and the same icon is crisp on a 4K desktop and a small phone. **Swiggy / Amazon logos** are SVG so one file serves every screen density. **Spinners and animated checkmarks** on payment-success screens are SVG with CSS `stroke-dashoffset` animation. **Charts** (D3, Recharts) render as SVG so tooltips and hover work on each bar.

## 🟡 Real Example Hindi mein
**Instagram, Gmail और Zomato के icons** (heart, search, cart, home) SVG हैं: like करने पर heart का CSS `fill` लाल हो जाता है, और वही icon 4K desktop और छोटे phone दोनों पर साफ दिखता है। **Swiggy / Amazon logo** SVG हैं, एक file हर screen density के लिए। Payment-success का **animated checkmark और spinners** SVG + CSS `stroke-dashoffset` animation हैं। **Charts** (D3, Recharts) SVG में बनते हैं ताकि हर bar पर tooltip/hover चले।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SVG in HTML</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <!-- Hidden sprite: define icons ONCE, reuse with <use> -->
  <svg width="0" height="0" style="position:absolute" aria-hidden="true">
    <symbol id="i-heart" viewBox="0 0 24 24">
      <!-- heart path from a 24x24 grid -->
      <path d="M12 21s-7-4.6-9.5-9A5.5 5.5 0 0 1 12 6a5.5 5.5 0 0 1 9.5 6c-2.5 4.4-9.5 9-9.5 9z"/>
    </symbol>
    <symbol id="i-check" viewBox="0 0 24 24">
      <path d="M4 12l5 5L20 6" fill="none" stroke="currentColor" stroke-width="3"
            stroke-linecap="round" stroke-linejoin="round"/>
    </symbol>
  </svg>

  <main class="page">
    <h1>SVG Basics</h1>

    <!-- 1. Basic shapes. viewBox makes the drawing scale to width/height -->
    <h2>1. Shapes</h2>
    <svg class="shapes" viewBox="0 0 300 100" role="img" aria-labelledby="t1">
      <title id="t1">A rectangle, a circle and a triangle</title>
      <rect x="10" y="10" width="80" height="80" rx="10" fill="#e53935"/>
      <circle cx="150" cy="50" r="40" fill="#1e88e5"/>
      <polygon points="210,90 250,10 290,90" fill="#43a047"/>
    </svg>

    <!-- 2. Reusable like button: icon colour controlled by CSS -->
    <h2>2. Like button (CSS controls fill)</h2>
    <button class="like" id="likeBtn" aria-pressed="false" aria-label="Like">
      <svg class="icon" aria-hidden="true"><use href="#i-heart"/></svg>
    </button>

    <!-- 3. Stroke-draw animated checkmark (payment success) -->
    <h2>3. Animated check</h2>
    <svg class="success" viewBox="0 0 52 52" role="img" aria-label="Success">
      <circle class="ring" cx="26" cy="26" r="24"/>
      <path class="tick" d="M14 27l8 8 16-17"/>
    </svg>
  </main>

  <script>
    // toggle liked state; CSS reacts to the class
    const btn = document.getElementById('likeBtn');
    btn.addEventListener('click', () => {
      const on = btn.classList.toggle('liked');
      btn.setAttribute('aria-pressed', on);   // keep accessibility state in sync
    });
  </script>
</body>
</html>
```

```css
/* style.css */
*, *::before, *::after { box-sizing: border-box; }
body { font-family: system-ui, sans-serif; background: #f6f7f9; margin: 0; }
.page { max-width: 600px; margin: 0 auto; padding: 24px 16px; }

/* Responsive svg: height follows viewBox ratio automatically */
.shapes { width: 100%; max-width: 360px; background: #fff; border-radius: 8px; }

/* Like button: icon uses CSS, not an image */
.like { background: none; border: 0; cursor: pointer; padding: 8px; color: #777; }
.icon { width: 40px; height: 40px; fill: currentColor; transition: transform .2s, color .2s; }
.like:hover .icon { transform: scale(1.15); }
.like.liked { color: #e91e63; }        /* fill follows currentColor */

/* Animated checkmark using the stroke-dash trick */
.success { width: 96px; height: 96px; }
.ring, .tick { fill: none; stroke: #2e7d32; stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; }
.ring { stroke-dasharray: 151; stroke-dashoffset: 151; animation: draw .6s ease forwards; }  /* 2*PI*24 ~ 151 */
.tick { stroke-dasharray: 40;  stroke-dashoffset: 40;  animation: draw .4s .5s ease forwards; }
@keyframes draw { to { stroke-dashoffset: 0; } }  /* line "draws" itself */

/* Respect users who want less motion */
@media (prefers-reduced-motion: reduce) {
  .ring, .tick { animation: none; stroke-dashoffset: 0; }
}
```

---

## 🟠 React/Next.js Connection

```jsx
// Inline SVG as a component. JSX uses camelCase: strokeWidth, strokeLinecap, viewBox
export function HeartIcon({ className = "h-6 w-6" }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden="true">
      <path d="M12 21s-7-4.6-9.5-9A5.5 5.5 0 0 1 12 6a5.5 5.5 0 0 1 9.5 6c-2.5 4.4-9.5 9-9.5 9z" />
    </svg>
  );
}

// Tailwind: colour via text-* because of currentColor; fill/stroke utilities also exist
<button className="text-gray-500 hover:text-pink-500">
  <HeartIcon className="h-8 w-8" />
</button>
```
- **SVGR** (`@svgr/webpack`) turns `.svg` files into React components; Next.js supports it via config.
- With `next/image`, an `.svg` is served as-is (set `dangerouslyAllowSVG` only for trusted files; SVG can contain scripts).
- Icon libraries (lucide-react, heroicons, react-icons) are all inline SVG components.

---

## ⚫ Interview Questions + Answers

Q1: SVG vs PNG: when use which?
A1: SVG for logos, icons, illustrations and charts (scales infinitely, tiny, stylable). PNG/JPG/WebP for photos and complex raster images, where SVG would be huge.

Q2: What does `viewBox` do?
A2: It defines the SVG's internal coordinate system (`minX minY width height`). The browser scales it to fit the element's displayed size, keeping the aspect ratio via `preserveAspectRatio`. Without it, the SVG will not scale.

Q3: How can you change an SVG icon's colour with CSS?
A3: The SVG must be inline (or sprite via `<use>`; an `<img>` cannot be styled from outside). Use `fill="currentColor"` and set CSS `color`, or set `fill`/`stroke` directly. Inside `<use>`, CSS custom properties and `currentColor` can pass through.

Q4: Inline SVG vs `<img src>` SVG?
A4: `<img>`: cacheable, simple, but no CSS/JS access to internals and no external CSS. Inline: full control and no request, but increases HTML size and is not cached separately.

Q5: SVG vs canvas?
A5: SVG is retained-mode vector with DOM nodes, events and CSS animation, best for fewer objects. Canvas is immediate-mode raster, best for thousands of fast-changing objects.

---

## 🔷 Common Mistakes to Avoid
❌ Mistake 1: No `viewBox`, so the SVG will not resize.
✅ Correct way: Always set `viewBox` and control size by CSS width/height.

❌ Mistake 2: Hard-coded `fill="#000"` inside every icon.
✅ Correct way: Use `fill="currentColor"` so icons follow text colour and dark mode.

❌ Mistake 3: Using `<img src=icon.svg>` and then trying to style `path` with CSS.
✅ Correct way: Inline it (or use `<use>` / a component).

❌ Mistake 4: Forgetting accessibility.
✅ Correct way: `aria-hidden="true"` on decorative icons; `role="img"` + `<title>` for meaningful ones.

❌ Mistake 5: Accepting untrusted SVG uploads and inlining them (XSS through `<script>`/`onload`).
✅ Correct way: Sanitize (DOMPurify) or serve as `<img>`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SVG | XML vector graphics | Vector image format |
| viewBox | Internal coordinate window | अंदर का coordinate grid |
| path / d | Shape defined by commands | Commands से बनी रेखा/shape |
| fill / stroke | Inside colour / outline | अंदर का रंग / outline |
| currentColor | Inherits CSS color | Parent text का रंग |
| `<symbol>` + `<use>` | Define once, reuse | एक बार बनाओ, बार-बार use |
| stroke-dasharray | Dash pattern of outline | Outline का dash pattern |
| SVGR | SVG to React component tool | SVG को React component बनाने वाला tool |

---

## ⚡ 3-Line Summary
English: SVG describes shapes as vectors, so it is crisp at any size and tiny in file size.
Inline SVG lets CSS and JS style and animate parts; use `viewBox` and `currentColor`.
Add `<title>`/`aria-label` for meaningful graphics and `aria-hidden` for decorative ones.

Hindi: SVG shapes को vectors की तरह describe करता है, इसलिए हर size पर साफ और file में छोटा।
Inline SVG में CSS और JS से parts को style/animate कर सकते हैं; `viewBox` और `currentColor` use करें।
Meaningful graphics में `<title>`/`aria-label` और सजावटी में `aria-hidden` लगाएँ।

---

## ➡️ Next Topic
**28. Link Tag (stylesheet, favicon, preload)** — अब `<head>` की `<link>` tag देखेंगे जिससे CSS, favicon और fonts/images को पहले load करवाया जाता है।

---
