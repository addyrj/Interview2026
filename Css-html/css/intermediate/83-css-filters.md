# 83. CSS Filters
# हिंदी में: CSS Filters — Images और Elements पर Photoshop जैसे Effects

---

## 🔵 Simple Definition (English)
The `filter` property applies graphical effects like `blur()`, `brightness()`, `grayscale()`, `contrast()` and `drop-shadow()` to an element and everything inside it. A sister property, `backdrop-filter`, applies the effect to whatever is BEHIND the element, which gives the frosted-glass look.

## 🔵 सरल परिभाषा (Hindi)
`filter` property element और उसके अंदर की हर चीज़ पर `blur()`, `brightness()`, `grayscale()`, `contrast()`, `drop-shadow()` जैसे graphic effects लगाती है। इसकी जुड़वाँ `backdrop-filter` element के पीछे की चीज़ों पर effect लगाती है, जिससे frosted-glass जैसा look बनता है।

---

## 🔴 Problem it Solves
```
BEFORE:
  - Need a greyscale version of an image? Export a second file.
  - Blur a background? Pre-blur in Photoshop or use canvas/JS.
  - Disabled-state or dark-mode image tweaks = more assets
  - Frosted glass (iOS style) was impossible in CSS

AFTER:
  img { filter: grayscale(100%); }                       /* one line, reversible */
  .navbar { backdrop-filter: blur(10px); }               /* glass effect over page content */
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  - Grey version चाहिए तो दूसरी image export करो
  - Background blur करना हो तो Photoshop या canvas/JS
  - Disabled state या dark mode के लिए और assets
  - Frosted glass (iOS जैसा) CSS में बन ही नहीं सकता था

अब:
  filter: grayscale(100%) एक line, और hover पर वापस रंगीन।
  backdrop-filter: blur(10px) से पीछे का content धुंधला दिखता है।
```

---

## 🟢 How it Works — Step by Step

```
FILTER FUNCTIONS:
  blur(4px)             Gaussian blur (length, not %)
  brightness(1.2)       1 = normal, 0 = black, >1 brighter (also accepts 120%)
  contrast(1.3)         1 = normal, 0 = flat grey
  grayscale(1)          0..1 or 0%..100%
  sepia(0.8)            old-photo brown tone
  saturate(1.5)         0 = grey, >1 vivid
  hue-rotate(90deg)     rotates colours around the colour wheel
  invert(1)             negative (used for dark-mode icon tricks)
  opacity(0.5)          like opacity, but can be GPU-accelerated in a filter chain
  drop-shadow(x y blur colour)   shadow that follows the alpha shape (no spread, no inset)
  url(#svgFilter)       reference an SVG filter for advanced effects

CHAINING: space separated, applied left to right, order matters.
  filter: grayscale(1) brightness(1.2) blur(2px);

filter vs backdrop-filter:
  filter           affects the element ITSELF (and its children, text, borders)
  backdrop-filter  affects what's BEHIND the element; the element needs a semi-transparent background to show it
     .glass { background: rgba(255,255,255,.2); backdrop-filter: blur(12px) saturate(160%); }
     Support: Chrome 76+, Safari 9+ (with -webkit- prefix until 18), Firefox 103+.
     Include -webkit-backdrop-filter for older Safari.

SIDE EFFECTS:
  - A filter (other than none) creates a new stacking context
  - It becomes the containing block for position: fixed descendants
  - Applies to the whole element including children: you can't "un-blur" a child
    (to blur only a background, put it in a pseudo-element/separate layer)

PERFORMANCE:
  - blur() with big radius on large areas is GPU heavy; backdrop-filter is heavier still
  - Animating filter values can be smooth when the element is promoted to its own layer,
    but avoid many blurred elements at once, especially on low-end phones

ACCESSIBILITY:
  - Don't convey meaning by colour filter alone. grayscale hover is decoration.
  - Filters don't change contrast ratios the way you compute them in code; test the result.
```

## 🟢 कैसे काम करता है? (Hindi)

```
FUNCTIONS:
  blur(4px)           धुंधला (length में)
  brightness(1.2)     1 = normal, 0 = काला, >1 = ज़्यादा चमक
  contrast(1.3)       contrast कम/ज़्यादा
  grayscale(1)        पूरा काला-सफेद (0 से 1)
  sepia(0.8)          पुरानी photo जैसा
  saturate(1.5)       रंग गहरे/हल्के
  hue-rotate(90deg)   रंगों को colour wheel पर घुमाता है
  invert(1)           negative
  drop-shadow()       असली shape को follow करने वाली shadow

CHAINING: space से अलग करके लिखो; बाएँ से दाएँ apply होते हैं।
  filter: grayscale(1) brightness(1.2);

filter बनाम backdrop-filter:
  filter           element पर और उसके children पर
  backdrop-filter  element के पीछे जो है उस पर; element का background semi-transparent होना चाहिए
     .glass { background: rgba(255,255,255,.2); backdrop-filter: blur(12px); }

साइड इफेक्ट: filter लगते ही नई stacking context बनती है और position: fixed वाले children का containing block बदल जाता है।

Performance: बड़े area पर ज़्यादा blur महंगा है; एक साथ बहुत सारे blurred elements मत रखो।
```

---

## 🟡 Real World Example
**Amazon, Instagram, Apple:** Instagram's photo filters (Clarendon, Sepia) are the same idea: brightness, contrast, saturate, sepia combined. On Zomato or Swiggy a closed restaurant card shows its photo in `grayscale(1)` with reduced opacity. Apple's and macOS-style sticky navbars (and many iOS-like web headers) use `backdrop-filter: blur()` so page content blurs as it scrolls under the bar. Modal overlays blur the page behind them. Logo walls ("Trusted by") show logos in grey and bring colour back on hover.

## 🟡 Real Example Hindi mein
**Amazon, Instagram, Apple:** Instagram के photo filters (Clarendon, Sepia) यही idea हैं: brightness, contrast, saturate, sepia का मेल। Zomato/Swiggy पर बंद restaurant की photo `grayscale(1)` और कम opacity में दिखती है। Apple जैसे sticky navbars में `backdrop-filter: blur()` से scroll करते समय पीछे का content धुंधला दिखता है। Modal के पीछे की page blur होती है। "Trusted by" logo wall में logos grey होते हैं और hover पर रंग वापस आता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CSS Filters Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; padding: 24px; background: #fafafa; }
    h2 { margin: 28px 0 10px; }
    .row { display: flex; gap: 14px; flex-wrap: wrap; }

    /* A coloured "photo" made with gradients so the demo needs no image file */
    .photo {
      width: 140px; height: 100px; border-radius: 10px;
      background:
        radial-gradient(circle at 70% 30%, #ffeb3b 0 18%, transparent 19%),   /* sun */
        linear-gradient(#4fc3f7 0 60%, #66bb6a 60%);                           /* sky + grass */
      display: grid; place-items: end start; padding: 6px;
      font-size: 12px; font-weight: bold; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,.6);
    }

    /* 1. SINGLE FILTERS */
    .f-blur       { filter: blur(3px); }
    .f-bright     { filter: brightness(1.4); }
    .f-contrast   { filter: contrast(1.8); }
    .f-gray       { filter: grayscale(1); }
    .f-sepia      { filter: sepia(0.9); }
    .f-saturate   { filter: saturate(2.2); }
    .f-hue        { filter: hue-rotate(120deg); }
    .f-invert     { filter: invert(1); }

    /* 2. CHAIN: Instagram-like preset */
    .f-insta { filter: contrast(1.1) saturate(1.4) sepia(0.2) brightness(1.05); }

    /* 3. LOGO WALL: grey until hover */
    .logo {
      width: 90px; height: 50px; border-radius: 8px; background: #ff5a5f; color: #fff;
      display: grid; place-items: center; font-weight: bold;
      filter: grayscale(1); opacity: .6;
      transition: filter .3s, opacity .3s;
    }
    .logo:hover { filter: grayscale(0); opacity: 1; }

    /* 4. CLOSED RESTAURANT state */
    .closed { filter: grayscale(1) brightness(.9); }

    /* 5. GLASS NAVBAR with backdrop-filter over a colourful background */
    .stage {
      position: relative; height: 200px; border-radius: 12px; overflow: auto;
      background: linear-gradient(135deg, #ff5a5f, #f5a623 40%, #1a73e8 70%, #34a853);
    }
    .glass {
      position: sticky; top: 0;                                  /* sticks to the top of .stage */
      padding: 12px 16px; color: #fff; font-weight: bold;
      background: rgba(255,255,255,.25);                         /* must be semi-transparent */
      -webkit-backdrop-filter: blur(10px) saturate(160%);        /* older Safari */
      backdrop-filter: blur(10px) saturate(160%);
      border-bottom: 1px solid rgba(255,255,255,.4);
    }
    .stage .content { height: 400px; padding: 16px; color: #fff; }
    .stripe { height: 14px; margin: 14px 0; background: rgba(255,255,255,.8); border-radius: 7px; }

    /* 6. drop-shadow on a shape */
    .shape-wrap { filter: drop-shadow(0 6px 6px rgba(0,0,0,.45)); width: fit-content; }
    .heart {
      width: 70px; height: 70px; background: #e91e63;
      clip-path: polygon(50% 100%, 0 40%, 15% 10%, 50% 25%, 85% 10%, 100% 40%);
    }

    /* 7. Provide a fallback when backdrop-filter is not supported */
    @supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
      .glass { background: rgba(40,40,40,.85); }
    }
  </style>
</head>
<body>
  <h1>CSS Filters</h1>

  <h2>1. Individual filters</h2>
  <div class="row">
    <div class="photo">original</div>
    <div class="photo f-blur">blur(3px)</div>
    <div class="photo f-bright">brightness</div>
    <div class="photo f-contrast">contrast</div>
    <div class="photo f-gray">grayscale</div>
    <div class="photo f-sepia">sepia</div>
    <div class="photo f-saturate">saturate</div>
    <div class="photo f-hue">hue-rotate</div>
    <div class="photo f-invert">invert</div>
  </div>

  <h2>2. Chained (Instagram-like)</h2>
  <div class="row"><div class="photo f-insta">chained</div></div>

  <h2>3. Logo wall (hover)</h2>
  <div class="row"><div class="logo">ACME</div><div class="logo">Globex</div><div class="logo">Initech</div></div>

  <h2>4. Closed state</h2>
  <div class="row"><div class="photo closed">Closed now</div></div>

  <h2>5. Frosted glass header (scroll inside the box)</h2>
  <div class="stage">
    <div class="glass">Glass Navbar</div>
    <div class="content">
      <div class="stripe"></div><div class="stripe"></div><div class="stripe"></div>
      <div class="stripe"></div><div class="stripe"></div><div class="stripe"></div>
    </div>
  </div>

  <h2>6. drop-shadow follows the shape</h2>
  <div class="shape-wrap"><div class="heart"></div></div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Tailwind filter utilities: blur-sm|md|lg, brightness-110, contrast-125, grayscale, sepia,
//    saturate-150, hue-rotate-90, invert, drop-shadow-lg
//    Backdrop: backdrop-blur-md, backdrop-brightness-90, backdrop-saturate-150
<header className="sticky top-0 bg-white/30 backdrop-blur-md border-b border-white/40">
  Glass Navbar
</header>

// 2. Hover colour-return on logos
<img src="/logo.svg" alt="Acme"
     className="grayscale opacity-60 transition hover:grayscale-0 hover:opacity-100" />

// 3. Next.js <Image> placeholder="blur": different idea (built-in LQIP), but you can combine
//    with CSS: while loading, apply `blur-lg scale-105`, then remove on onLoad
import Image from 'next/image';
import { useState } from 'react';
function Photo({ src, alt }) {
  const [loaded, setLoaded] = useState(false);
  return (
    <Image src={src} alt={alt} width={400} height={300}
      onLoad={() => setLoaded(true)}
      className={`transition duration-700 ${loaded ? 'blur-0' : 'blur-lg'}`} />
  );
}

// 4. Modal overlay that blurs the page behind it
<div className="fixed inset-0 bg-black/40 backdrop-blur-sm" />

// 5. Dark mode for dark-on-transparent icons: dark:invert
<img src="/github.svg" alt="GitHub" className="dark:invert" />
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the CSS `filter` property? Name some functions.**
A1: It applies visual effects to an element and its contents. Functions: `blur`, `brightness`, `contrast`, `grayscale`, `sepia`, `saturate`, `hue-rotate`, `invert`, `opacity`, `drop-shadow`, and `url()` for SVG filters. Multiple functions can be chained with spaces and are applied in order.

**Q2: What is the difference between `filter` and `backdrop-filter`?**
A2: `filter` processes the element itself, including its children, so `filter: blur(5px)` blurs the text inside too. `backdrop-filter` processes the content painted behind the element, then draws the element on top unblurred. It needs a translucent background to be visible. It is how frosted-glass navbars and modals are made. Support: Chrome 76+, Safari 9+ (prefixed `-webkit-` in older versions), Firefox 103+.

**Q3: What is the difference between `box-shadow` and `filter: drop-shadow()`?**
A3: `box-shadow` follows the rectangular box (with `border-radius`). `drop-shadow()` follows the pixel alpha of the rendered content, so a transparent PNG, SVG, or clip-path shape gets a hugging shadow. `drop-shadow` has no spread/inset. Since `clip-path` also clips box-shadow, apply `drop-shadow` on a wrapper.

**Q4: Does applying a filter have side effects on layout or stacking?**
A4: It does not change layout size, but any filter other than `none` creates a new stacking context and becomes the containing block for fixed and absolute descendants, which can unexpectedly break `position: fixed` children (such as a fixed tooltip inside a blurred card). Also `blur` bleeds beyond the element's box visually.

**Q5: What are the performance concerns, and how do you blur only the background of a card but not its text?**
A5: Large blur radii and backdrop filters are costly (GPU memory and fill rate), especially on mobile or when animated; limit the area and number of elements. Because `filter` applies to all children, blur only a background by putting it in its own layer, such as a `::before` pseudo-element or a sibling absolutely positioned behind the content with `filter: blur()`, and keep the text in a separate unblurred element. Or just use `backdrop-filter` on the card.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Using `backdrop-filter` with an opaque background
```css
/* WRONG: nothing visible blurs because the background covers it */
.glass { background: #fff; backdrop-filter: blur(10px); }

/* CORRECT */
.glass { background: rgba(255,255,255,.3); backdrop-filter: blur(10px); }
```

❌ **Mistake 2:** Blurring a container and expecting the text to stay sharp
```css
/* WRONG: the heading blurs too */
.card { filter: blur(6px); }

/* CORRECT: blur a background layer only */
.card { position: relative; }
.card::before { content: ""; position: absolute; inset: 0; background: url(bg.jpg) center/cover; filter: blur(6px); z-index: -1; }
```

❌ **Mistake 3:** Fixed-position child suddenly stops sticking to the viewport
```css
/* WRONG: .parent has a filter, so .child { position: fixed } is positioned relative to .parent */
.parent { filter: grayscale(1); }

/* CORRECT: move the fixed element out of the filtered parent, or apply the filter to the img only */
```

❌ **Mistake 4:** Forgetting the `-webkit-` prefix / `@supports` fallback for `backdrop-filter`
```css
/* CORRECT: include both and a solid fallback */
.glass { background: rgba(255,255,255,.7); -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| filter | Visual effects on element + children | Element पर effects |
| backdrop-filter | Effect on content behind element | Element के पीछे की चीज़ों पर effect |
| blur() | Gaussian blur | धुंधला करना |
| grayscale() | Convert to black & white | काला-सफेद करना |
| hue-rotate() | Shift colours on the wheel | रंगों को घुमाना |
| drop-shadow() | Shadow following alpha shape | Shape वाली shadow |
| frosted glass | Translucent + blurred panel look | धुंधला काँच जैसा look |
| stacking context | New z-index layer created by filter | नई z-index layer |

---

## ⚡ 3-Line Summary
**English:**
1. `filter` applies effects (blur, brightness, grayscale, drop-shadow and more) to an element and its children; chain them with spaces.
2. `backdrop-filter` blurs what is behind an element (needs a translucent background) and powers frosted-glass UI.
3. Filters create a stacking context, can be GPU-costly, and `drop-shadow` follows the real shape unlike `box-shadow`.

**Hindi:**
1. `filter` element और उसके children पर effects (blur, brightness, grayscale, drop-shadow आदि) लगाता है; spaces से chain करो।
2. `backdrop-filter` element के पीछे की चीज़ें blur करता है (translucent background चाहिए) और frosted-glass UI बनाता है।
3. Filters नई stacking context बनाते हैं, GPU पर भारी हो सकते हैं, और `drop-shadow` असली shape को follow करती है, `box-shadow` की तरह नहीं।

---

## ➡️ Next Topic
**84. CSS Object-fit + Object-position** — Filters से images सुंदर बनीं; अब सीखो कि अलग-अलग aspect ratio की images को fixed box में बिना खिंचे कैसे fit करें।
