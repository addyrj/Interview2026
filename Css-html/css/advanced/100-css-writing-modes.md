# 100. CSS Writing Modes
# हिंदी में: CSS Writing Modes — Text की दिशा: Horizontal और Vertical

---

## 🔵 Simple Definition (English)
`writing-mode` controls whether text lines run **horizontally or vertically** and the direction in which new lines (blocks) stack. Values: `horizontal-tb` (default), `vertical-rl`, `vertical-lr`. Together with `direction` and `text-orientation`, it supports Japanese, Chinese, Mongolian vertical text and creative vertical labels.

## 🔵 सरल परिभाषा (Hindi)
`writing-mode` तय करता है कि text की lines **आड़ी (horizontal) चलेंगी या खड़ी (vertical)** और नई lines किस तरफ जमेंगी। Values: `horizontal-tb` (default), `vertical-rl`, `vertical-lr`। `direction` और `text-orientation` के साथ ये Japanese, Chinese, Mongolian की vertical writing और creative vertical labels को सपोर्ट करता है।

---

## 🔴 Problem it Solves
```
BEFORE:
  Vertical text (sidebar labels, table headers, East Asian typography) needed hacks:
    transform: rotate(-90deg);  transform-origin: ...;  width/height swapped;
  → the layout box STILL occupies the unrotated space, overlapping/awkward, text selection weird,
    and sizing math (width <-> height) confusing.

NOW:
  .label { writing-mode: vertical-rl; }
  → the text really flows top-to-bottom; the box, margins, scrolling and wrapping all follow.
  Japanese, Chinese, Korean, Mongolian typography works natively.
  Logical properties (inline-size / block-size) adapt automatically.
```

## 🔴 यह क्यों बना? (Hindi)
पहले vertical text के लिए `rotate(-90deg)` जैसे hacks चलते थे — box की जगह वैसी ही रहती थी, text selection अजीब, और width/height की गणना उलझी हुई। `writing-mode` से text सच में खड़ा चलता है और box, wrapping और scroll सब उसी के हिसाब से बदलते हैं। जापानी, चीनी जैसी भाषाओं की typography भी natively सही चलती है।

---

## 🟢 How it Works — Step by Step

```
THREE MAIN VALUES:
──────────────────────────────────────────────────────────
  horizontal-tb   (default)  lines run LEFT↔RIGHT, blocks stack TOP→BOTTOM (English, Hindi)
  vertical-rl                lines run TOP→BOTTOM, blocks stack RIGHT→LEFT (Japanese, Chinese traditional)
  vertical-lr                lines run TOP→BOTTOM, blocks stack LEFT→RIGHT (Mongolian)
  (sideways-rl / sideways-lr: newer values with limited browser support; avoid in production)

  tb = top-to-bottom   rl = right-to-left   lr = left-to-right

WHAT CHANGES:
  - Inline axis becomes VERTICAL, block axis becomes HORIZONTAL
  - inline-size = height now;  block-size = width now   ← this is why logical props matter
  - margin-inline-start = top;  margin-block-start = right (in vertical-rl)
  - Physical width/height/top/left do NOT change meaning, but logical ones do.
  - Flexbox/Grid follow the writing mode: flex-direction: row runs along the inline axis (vertical!)

RELATED PROPERTIES:
  text-orientation: mixed | upright | sideways
      mixed    (default) Latin glyphs are rotated 90deg, CJK glyphs stay upright
      upright  every character upright, stacked (Latin letters read top-to-bottom as letters)
      sideways all glyphs rotated 90deg
  text-combine-upright: all | digits 2   /* tate-chu-yoko: numbers like "12" kept horizontal inside vertical text */
  direction: ltr | rtl     /* for inline direction; combine with unicode-bidi; prefer the HTML dir attribute */
  unicode-bidi: normal | isolate | plaintext   /* mixed-direction text handling */

COMMON "MODERN WEB" USES:
  1. Vertical side labels ("Scroll", "Follow us") on landing pages
  2. Rotated table headers, chart axis labels, tab labels on a vertical tab bar
  3. Book-style layouts, Japanese/Chinese sites, Mongolian sites
  4. Vertical text in tight spaces (spine of a book card)
  5. Page-level: html { writing-mode: vertical-rl }  → whole page scrolls horizontally

INTERACTION WITH LAYOUT:
  - In vertical-rl, block-size is the width and inline-size is the height. Auto inline-size
    fills the available HEIGHT of the container, so you often need to set a height yourself.
  - Scrolling: vertical-rl documents scroll horizontally (to the left); the content starts at the right side.
  - Text selection and screen readers follow the logical order, which is why this beats rotate().

SUPPORT: writing-mode: Chrome 48+, Firefox 41+, Safari 10.1+, Edge 79+ (full for horizontal-tb, vertical-rl, vertical-lr).
         text-orientation: Chrome 48+, Firefox 41+, Safari 14+.
         text-combine-upright: Chrome 48+, Firefox 48+, Safari 15.4+.
```

## 🟢 कैसे काम करता है? (Hindi)
1. `horizontal-tb` (default): lines बाएँ-दाएँ चलती हैं, blocks ऊपर से नीचे जमते हैं — English/Hindi में।
2. `vertical-rl`: lines ऊपर से नीचे चलती हैं, नए blocks दाएँ से बाएँ जमते हैं — Japanese/Chinese।
3. `vertical-lr`: lines ऊपर से नीचे, blocks बाएँ से दाएँ — Mongolian।
4. **Axes बदल जाते हैं:** inline axis vertical और block axis horizontal; `inline-size` = height, `block-size` = width — इसीलिए Logical Properties (topic 99) ज़रूरी हैं।
5. `text-orientation: mixed` में Latin अक्षर 90° घूमते हैं और CJK सीधे रहते हैं; `upright` में सब सीधे।
6. `text-combine-upright: digits 2` से "12" जैसे अंक vertical text में आड़े (horizontal) रहते हैं।
7. `rotate()` hack के मुक़ाबले ये बेहतर है: box, selection और screen reader सब सही चलते हैं।

---

## 🟡 Real World Example
**Japanese sites (Yahoo! Japan articles, Aozora Bunko, manga/novel readers, Kindle Japan):** Poora article vertical-rl me, right se left padha jata hai.
**Landing pages (Apple, Stripe-style marketing pages, portfolio sites):** Page ke side me chhota vertical text "SCROLL" ya "Follow us" `writing-mode: vertical-rl`.
**Dashboards / Excel-like tables:** Narrow columns ke header text ko vertical karna (e.g., "Mon Tue Wed" headers in a heatmap) taaki column patla rahe.
**Gmail / Slack-like vertical tab rails:** Vertical tab labels.
**Instagram/Zomato:** Rare, mostly decorative vertical badges ("NEW", "50% OFF") on card edges.

## 🟡 Real Example Hindi mein
**जापानी sites (Yahoo! Japan articles, manga/novel readers):** पूरा article vertical-rl में, दाएँ से बाएँ पढ़ा जाता है।
**Landing pages / portfolio sites:** Page के किनारे छोटा vertical text "SCROLL" या "Follow us" `writing-mode: vertical-rl` से।
**Dashboards / tables:** Narrow columns के header को vertical करना ताकि column पतला रहे।
**Zomato/Swiggy:** Cards के किनारे vertical "50% OFF" जैसे decorative badges।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CSS Writing Modes Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; color: #222; }
    h2 { margin: 24px 0 8px; font-size: 16px; border-bottom: 2px solid #333; padding-bottom: 4px; }
    .row { display: flex; gap: 20px; flex-wrap: wrap; align-items: flex-start; }
    .demo { background: #fff; border: 2px solid #1976d2; padding: 10px; border-radius: 8px; }

    /* ─── 1. THE THREE VALUES ─────────────────────────────────────── */
    .h  { writing-mode: horizontal-tb; }                  /* default */
    .rl { writing-mode: vertical-rl;  height: 180px; }    /* columns stack right → left */
    .lr { writing-mode: vertical-lr;  height: 180px; }    /* columns stack left → right */
    /* height needed: in vertical modes the inline axis (line length) is the height */

    /* ─── 2. TEXT-ORIENTATION ─────────────────────────────────────── */
    .mixed   { writing-mode: vertical-rl; text-orientation: mixed;   height: 140px; }   /* Latin rotated */
    .upright { writing-mode: vertical-rl; text-orientation: upright; height: 140px; }   /* all upright */

    /* ─── 3. VERTICAL SIDE LABEL (very common in landing pages) ───── */
    .hero { position: relative; background: #232f3e; color: #fff; height: 180px; border-radius: 12px; padding: 20px; }
    .scroll-label {
      position: absolute; inset-block: 0; inset-inline-end: 12px;   /* logical positioning */
      writing-mode: vertical-rl;
      letter-spacing: .3em; font-size: 12px; text-transform: uppercase;
      display: grid; place-items: center;                           /* center along the vertical line */
    }

    /* ─── 4. ROTATE 180° so the text reads bottom → top (like a book spine in many languages) ── */
    .spine { writing-mode: vertical-rl; transform: rotate(180deg); background: #ff9800; color: #fff;
             padding: 12px 6px; border-radius: 6px; }

    /* ─── 5. TABLE HEADER: narrow columns with vertical labels ────── */
    table { border-collapse: collapse; background: #fff; }
    th, td { border: 1px solid #ddd; padding: 6px; text-align: center; min-width: 34px; }
    th.v { writing-mode: vertical-rl; transform: rotate(180deg); height: 90px; white-space: nowrap; }

    /* ─── 6. JAPANESE TATEGAKI (vertical article) + digits kept upright ── */
    .tategaki { writing-mode: vertical-rl; height: 220px; font-size: 18px; line-height: 1.8; background: #fff8e1; padding: 12px; overflow-x: auto; }
    .tcy { text-combine-upright: all; }     /* "12" stays horizontal in one character cell */

    /* ─── 7. LOGICAL PROPERTIES FOLLOW THE MODE ───────────────────── */
    .box { background: #c8e6c9; inline-size: 120px; block-size: 40px; padding-inline: 10px; margin-block-start: 8px; }
    .vbox { writing-mode: vertical-rl; }  /* inline-size now means HEIGHT, block-size means WIDTH */
  </style>
</head>
<body>
  <h1>CSS Writing Modes</h1>

  <h2>1. horizontal-tb, vertical-rl, vertical-lr</h2>
  <div class="row">
    <div class="demo h">Line one<br>Line two<br>Line three</div>
    <div class="demo rl">Line one<br>Line two<br>Line three</div>
    <div class="demo lr">Line one<br>Line two<br>Line three</div>
  </div>

  <h2>2. text-orientation: mixed vs upright</h2>
  <div class="row">
    <div class="demo mixed">Mixed ABC 123</div>
    <div class="demo upright">Upright ABC 123</div>
  </div>

  <h2>3. Vertical "scroll" label in a hero</h2>
  <div class="hero">
    <h3 style="margin:0">Big sale is live</h3>
    <span class="scroll-label">Scroll down</span>
  </div>

  <h2>4. Rotated 180° (reads bottom to top)</h2>
  <span class="spine">Book spine</span>

  <h2>5. Table with vertical headers</h2>
  <table>
    <tr><th></th><th class="v">Monday</th><th class="v">Tuesday</th><th class="v">Wednesday</th></tr>
    <tr><td>Orders</td><td>12</td><td>18</td><td>25</td></tr>
  </table>

  <h2>6. Japanese vertical text (tategaki)</h2>
  <div class="tategaki" lang="ja">
    吾輩は猫である。名前はまだ無い。どこで生れたかとんと見当がつかぬ。<span class="tcy">12</span>月の寒い日であった。
  </div>

  <h2>7. Logical sizes flip with the mode</h2>
  <div class="row">
    <div class="box">inline-size 120</div>
    <div class="box vbox">inline-size 120 (now height)</div>
  </div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Tailwind: v3 has no default writing-mode utilities (newer versions may add some;
//    check your version's docs). Arbitrary properties work in Tailwind v3.1+:
<span className="[writing-mode:vertical-rl] rotate-180 tracking-widest text-xs uppercase">
  Scroll
</span>

// 2. CSS Modules:
/* Label.module.css */
.vertical { writing-mode: vertical-rl; text-orientation: mixed; }

// 3. Inline style in React (camelCase):
<div style={{ writingMode: 'vertical-rl', textOrientation: 'upright' }}>縦書き</div>

// 4. Internationalized Next.js app: language decides both dir and writing-mode:
const LANG_CONFIG = {
  en: { dir: 'ltr' },
  ar: { dir: 'rtl' },
  ja: { dir: 'ltr', vertical: false },   // Japanese sites are mostly horizontal; vertical for literature
};
// Use logical properties everywhere (topic 99) so a vertical article component
// just toggles writing-mode on one wrapper and spacing adapts.

// 5. Charts (Recharts / Chart.js): rotating axis labels often uses SVG transform or
//    CSS writing-mode on HTML labels for crisp, selectable text.

// 6. Accessibility: vertical text is still read in logical order by screen readers;
//    do not use text-orientation: upright on long Latin text (hard to read).
```

---

## ⚫ Interview Questions + Answers

**Q1: What does `writing-mode` do?**
A1: It sets the direction lines of text run (horizontal or vertical) and the direction in which blocks stack. `horizontal-tb` is default; `vertical-rl` runs lines top-to-bottom with new lines to the left; `vertical-lr` runs top-to-bottom with new lines to the right. It enables native support for Japanese, Chinese, Mongolian vertical typography and clean vertical labels.

**Q2: Why use `writing-mode` instead of `transform: rotate(-90deg)` for a vertical label?**
A2: `rotate` is visual only: the element still occupies its original (horizontal) layout box, so it overlaps neighbors and you need to fix widths and `transform-origin`. `writing-mode` changes the actual flow, so the box, wrapping, margins, scrolling, selection and accessibility all follow. For a text that reads bottom-to-top you can combine `writing-mode: vertical-rl` with `rotate(180deg)`.

**Q3: What happens to width/height and flexbox in vertical writing modes?**
A3: Physical `width`/`height` keep their meaning, but logical `inline-size` becomes the height and `block-size` the width, and `margin-inline-*` maps to top/bottom. Flexbox and Grid are axis-based on the logical flow: `flex-direction: row` runs along the inline axis, which is now vertical. This is why logical properties are recommended.

**Q4: What is `text-orientation` and `text-combine-upright`?**
A4: `text-orientation` controls glyph orientation in vertical modes: `mixed` (default; Latin rotated sideways, CJK upright), `upright` (every character upright), `sideways` (all rotated). `text-combine-upright: all | digits 2` (tate-chu-yoko) squeezes a short run, such as "12", into one upright cell inside vertical text.

**Q5: How does this relate to `direction: rtl`?**
A5: `direction` (or better, the HTML `dir` attribute) sets the inline direction (left-to-right vs right-to-left) in horizontal text, used for Arabic/Hebrew. `writing-mode` sets the orientation of lines and blocks. Together they define the inline-start/inline-end and block-start/block-end mapping that logical properties use. Arabic = `horizontal-tb` + `rtl`; traditional Japanese = `vertical-rl` + `ltr`.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Using `rotate(-90deg)` for vertical text and then fixing the box with magic numbers
```css
/* WRONG */
.label { transform: rotate(-90deg); transform-origin: left top; width: 100px; margin-top: 100px; }

/* CORRECT */
.label { writing-mode: vertical-rl; transform: rotate(180deg); }
```

❌ **Mistake 2:** Forgetting that vertical text needs a height (block fills width by default)
```css
/* WRONG: the line length (inline-size = height) is auto → one very tall line */
.vertical { writing-mode: vertical-rl; }

/* CORRECT */
.vertical { writing-mode: vertical-rl; height: 200px; }   /* or max-block/inline-size on a wrapper */
```

❌ **Mistake 3:** Using physical properties with writing modes
```css
/* WRONG: width is not the inline size anymore, spacing ends up on the wrong sides */
.v { writing-mode: vertical-rl; margin-left: 10px; width: 120px; }

/* CORRECT */
.v { writing-mode: vertical-rl; margin-inline-start: 10px; inline-size: 120px; }
```

❌ **Mistake 4:** Long Latin text with `text-orientation: upright`
```css
/* WRONG: unreadable letter-by-letter stack */
.article { writing-mode: vertical-rl; text-orientation: upright; }

/* CORRECT: keep mixed (default) for Latin; use upright for short labels only */
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| writing-mode | Direction of lines and blocks | Lines और blocks की दिशा |
| horizontal-tb | Left-right lines, top-bottom blocks | आड़ी lines (default) |
| vertical-rl | Vertical lines, blocks right to left | खड़ी lines, दाएँ से बाएँ |
| vertical-lr | Vertical lines, blocks left to right | खड़ी lines, बाएँ से दाएँ |
| text-orientation | Glyph rotation in vertical text | Vertical में अक्षरों की दिशा |
| text-combine-upright | Keep short digit runs upright | अंक सीधे रखना |
| Tategaki | Japanese vertical writing | जापानी खड़ी लिखावट |
| Inline axis | Direction of text lines | Text line की दिशा |
| Block axis | Direction blocks stack | Blocks जमने की दिशा |

---

## ⚡ 3-Line Summary
**English:**
1. `writing-mode` (`horizontal-tb`, `vertical-rl`, `vertical-lr`) sets how text lines run and blocks stack; it replaces rotate hacks for vertical text.
2. In vertical modes inline-size becomes height and block-size becomes width, so use logical properties; `text-orientation` and `text-combine-upright` fine-tune glyphs.
3. Used for East Asian typography and vertical labels; add a height for vertical text and pair with `direction`/`dir` for RTL languages.

**Hindi:**
1. `writing-mode` (`horizontal-tb`, `vertical-rl`, `vertical-lr`) तय करता है कि text lines और blocks कैसे चलें; vertical text के लिए rotate hack की जगह यही सही है।
2. Vertical mode में inline-size = height और block-size = width बन जाता है, इसलिए logical properties use करो; `text-orientation` और `text-combine-upright` अक्षरों को ठीक करते हैं।
3. East Asian typography और vertical labels में काम आता है; vertical text को height दो और RTL भाषाओं के लिए `dir` इस्तेमाल करो।

---

## ➡️ Next Topic
**101. Dark Mode (prefers-color-scheme)** — user की system theme के हिसाब से अपने आप dark/light UI, CSS variables के साथ।
