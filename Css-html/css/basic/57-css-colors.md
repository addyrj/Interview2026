# 57. CSS Colors (hex, rgb, rgba, hsl, variables)
# हिंदी में: CSS Colors — रंग लिखने के सारे तरीके और Theme Variables

---

## 🔵 Simple Definition (English)
CSS lets you write a colour in several formats: **named** (`tomato`), **hex** (`#ff6347`), **rgb/rgba** (`rgb(255 99 71 / 0.5)`), **hsl/hsla** (`hsl(9 100% 64%)`). **CSS variables** (`--brand`) store a colour once so you can reuse and theme it.

## 🔵 सरल परिभाषा (Hindi)
CSS में रंग कई तरह से लिख सकते हैं: **नाम** (`tomato`), **hex** (`#ff6347`), **rgb/rgba** (`rgb(255 99 71 / 0.5)`), **hsl/hsla** (`hsl(9 100% 64%)`)। **CSS variables** (`--brand`) रंग को एक बार store करते हैं ताकि बार-बार use और theme बदलना आसान हो।

---

## 🔴 Problem it Solves
```
PROBLEM:
  Brand colour #e23744 typed in 200 places. Rebrand = find & replace nightmare.
  Need a transparent overlay -> hex can't do alpha (older syntax).
  Need a "slightly darker" shade -> hard to guess hex digits.

SOLUTION:
  :root { --brand: #e23744; }          /* one source of truth */
  .btn  { background: var(--brand); }
  .overlay { background: rgb(0 0 0 / 0.5); }                /* transparency */
  .btn:hover { background: hsl(355 75% 45%); }               /* tweak lightness only */
```

## 🔴 यह क्यों बना? (Hindi)
```
समस्या:
  Brand colour 200 जगह लिखा था; बदलना हो तो सब जगह replace करो।
  Transparent overlay चाहिए तो hex में आसान नहीं था।
  "थोड़ा गहरा" shade चाहिए तो hex अंदाज़े से बदलना पड़ता था।

हल:
  :root { --brand: #e23744; } एक जगह रखो, हर जगह var(--brand) use करो।
  rgb(0 0 0 / 0.5) से transparency।
  hsl में सिर्फ lightness बदलो तो shade मिल जाता है।
```

---

## 🟢 How it Works — Step by Step

```
FORMATS (same colour: Zomato red)
  Named      red, tomato, rebeccapurple, transparent, currentColor   (~148 names)
  HEX        #e23744   (RR GG BB, each 00-ff)    short: #f00 = #ff0000
             #e2374480 (8-digit: last pair = alpha, 80 = ~50%)
  RGB        rgb(226, 55, 68)    modern: rgb(226 55 68)   alpha: rgb(226 55 68 / 0.5)
  RGBA       rgba(226, 55, 68, 0.5)   (legacy alias; rgb() now accepts alpha too)
  HSL        hsl(355, 75%, 54%)  = Hue(0-360 wheel) Saturation(%) Lightness(%)
             alpha: hsl(355 75% 54% / 0.5)
  Modern     oklch(), lab(), color-mix(), color() -> wider gamut; check support
             (oklch/color-mix: Chrome 111+, Safari 16.4/16.2+, Firefox 113/120+)

WHICH TO USE?
  hex  -> design handoff (Figma gives hex)
  rgb  -> when you need alpha, or computing values in JS
  hsl  -> when building shades/themes (change L for light/dark variants)

HSL WHEEL:  0 red, 60 yellow, 120 green, 180 cyan, 240 blue, 300 magenta
  hsl(220 90% 50%)  vivid blue ;  lower S -> greyer ;  L 0% black, 100% white

SPECIAL KEYWORDS
  currentColor   uses the element's own `color` (icons/SVG/borders follow text colour)
  transparent    = rgba(0,0,0,0)

CSS VARIABLES (custom properties)
  Declare:   :root { --brand: #e23744; --bg: #fff; }
  Use:       background: var(--brand);
  Fallback:  color: var(--accent, #333);       (used if --accent isn't defined)
  Scope:     defined on :root = global; on .card = only .card and descendants
  They cascade and inherit, and can change at runtime (JS / media query / class) — unlike Sass variables.
  Dark mode:  [data-theme="dark"] { --bg: #111; --text: #eee; }

CONTRAST (accessibility): WCAG AA needs 4.5:1 for normal text, 3:1 for large text.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Formats (एक ही रंग):
  नाम      tomato, red, transparent, currentColor
  HEX      #e23744 (RR GG BB); 8 अंक वाला: आखिरी दो अंक = alpha
  RGB      rgb(226 55 68), alpha के साथ rgb(226 55 68 / 0.5)
  HSL      hsl(355 75% 54%) = Hue (रंग का कोण 0-360), Saturation, Lightness

कब क्या:
  hex -> Figma से मिला रंग
  rgb -> transparency चाहिए तब
  hsl -> shades बनाने हों (सिर्फ L बदलो)

currentColor: element के अपने text colour को border/icon में दोबारा use करता है।

CSS Variables:
  :root { --brand: #e23744; }   (global)
  color: var(--brand);          (use)
  var(--x, fallback)            (न मिले तो fallback)
  JS या media query से runtime में बदल सकते हैं -> dark mode आसान।

Contrast: normal text के लिए कम से कम 4.5:1 (WCAG AA)।
```

---

## 🟡 Real World Example
**Zomato / Instagram theming:** Zomato's red button is defined once as `--brand`. A "dark mode" switch only swaps `--bg` and `--text` variables on `<html>`, so every component recolours instantly. Image overlays on restaurant photos use `rgb(0 0 0 / 0.45)` so text stays readable. Hover shades are produced by lowering HSL lightness. The Instagram heart icon uses `currentColor` so it turns red when the parent `color` changes.

## 🟡 Real Example Hindi mein
**Zomato / Instagram theming:** Zomato का red button एक बार `--brand` में defined है। Dark mode switch सिर्फ `<html>` पर `--bg` और `--text` बदलता है, और सारे components तुरंत recolor हो जाते हैं। Restaurant photos पर text पढ़ने लायक रहे इसलिए overlay `rgb(0 0 0 / 0.45)` है। Hover shade के लिए HSL की lightness घटाते हैं। Instagram का heart icon `currentColor` use करता है, इसलिए parent का `color` बदलते ही icon लाल हो जाता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CSS Colors Demo</title>
  <style>
    /* ── CSS VARIABLES: single source of truth ── */
    :root {
      --brand: #e23744;                 /* Zomato-like red (hex) */
      --brand-dark: hsl(355 75% 40%);   /* darker shade via lightness */
      --bg: #ffffff;
      --text: #1f2937;
      --card: #f3f4f6;
    }
    /* Dark theme: same names, new values */
    [data-theme="dark"] {
      --bg: #111827;
      --text: #f9fafb;
      --card: #1f2937;
    }

    * { box-sizing: border-box; }
    body {
      font-family: system-ui, sans-serif;
      background: var(--bg);           /* uses variable */
      color: var(--text);
      padding: 20px;
      transition: background .3s, color .3s;
    }
    h2 { font-size: 15px; margin: 22px 0 8px; }

    /* ── Swatches: same colour, different formats ── */
    .swatches { display: flex; gap: 8px; flex-wrap: wrap; }
    .sw { width: 110px; height: 60px; border-radius: 8px; color: #fff; font-size: 11px; padding: 6px; }
    .named { background: tomato; }
    .hex   { background: #e23744; }
    .rgb   { background: rgb(226 55 68); }
    .hsl   { background: hsl(355 75% 54%); }

    /* ── Alpha: transparency ── */
    .photo { height: 120px; border-radius: 8px; position: relative;
             background: linear-gradient(135deg, #f59e0b, #ef4444); }
    .photo .overlay { position: absolute; inset: 0; border-radius: 8px;
                      background: rgb(0 0 0 / 0.45);    /* 45% black overlay */
                      color: #fff; display: grid; place-items: center; font-weight: 700; }

    /* ── Button using variables + hover shade ── */
    .btn { background: var(--brand); color: #fff; border: 0; padding: 10px 18px;
           border-radius: 6px; cursor: pointer; font: inherit; }
    .btn:hover { background: var(--brand-dark); }

    /* ── currentColor: icon and border follow text colour ── */
    .tag { color: #2563eb; border: 2px solid currentColor; padding: 4px 10px;
           border-radius: 999px; display: inline-flex; gap: 6px; align-items: center; }
    .tag svg { fill: currentColor; width: 14px; height: 14px; }

    /* ── Card using theme variables + fallback ── */
    .card { background: var(--card); padding: 12px; border-radius: 8px;
            border-left: 4px solid var(--accent, var(--brand)); /* fallback if --accent missing */ }
    .card.blue { --accent: #2563eb; }  /* scoped override */
  </style>
</head>
<body>
  <button class="btn" onclick="
    var h = document.documentElement;
    h.dataset.theme = h.dataset.theme === 'dark' ? 'light' : 'dark';  /* swap theme */
  ">Toggle dark mode</button>

  <h2>1. Formats</h2>
  <div class="swatches">
    <div class="sw named">tomato</div>
    <div class="sw hex">#e23744</div>
    <div class="sw rgb">rgb(226 55 68)</div>
    <div class="sw hsl">hsl(355 75% 54%)</div>
  </div>

  <h2>2. Alpha overlay</h2>
  <div class="photo"><div class="overlay">Biryani House</div></div>

  <h2>3. currentColor</h2>
  <span class="tag">
    <svg viewBox="0 0 10 10"><circle cx="5" cy="5" r="5"/></svg> Open now
  </span>

  <h2>4. Variables with fallback + scope</h2>
  <div class="card">Uses --brand (fallback)</div>
  <br>
  <div class="card blue">Uses scoped --accent</div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Theme with CSS variables + data attribute (no re-render of every component)
"use client";
import { useEffect, useState } from "react";

export default function ThemeToggle() {
  const [theme, setTheme] = useState("light");
  useEffect(() => {
    document.documentElement.dataset.theme = theme;   // swaps variable values
  }, [theme]);
  return <button onClick={() => setTheme(theme === "light" ? "dark" : "light")}>Toggle</button>;
}

// 2. Pass dynamic colour to CSS via variable (React inline style custom property)
<div style={{ "--accent": product.color }} className="card" />
/* card.css: .card { border-left: 4px solid var(--accent); } */

// 3. Tailwind: colours are utilities; extend with your variables
// tailwind.config.js
// theme: { extend: { colors: { brand: "var(--brand)" } } }
<button className="bg-brand text-white hover:bg-red-700">Order</button>
<div className="bg-black/50">{/* alpha shorthand = rgb(0 0 0 / 0.5) */}</div>
<span className="text-blue-600 border-2 border-current">tag</span>   {/* currentColor */}

// 4. Don't hard-code hex in every component; keep tokens in one file (design tokens).
```

---

## ⚫ Interview Questions + Answers

**Q1: Difference between hex, rgb and hsl? Which would you use?**
A1: All describe sRGB colours. Hex `#e23744` is compact (RR GG BB); `rgb()` uses decimal channels and supports alpha; `hsl()` uses hue/saturation/lightness, which is intuitive for making shades (change only L). Use hex from design handoff, rgb for alpha, hsl for theme scales. Modern CSS also has `oklch()` for perceptually even colours.

**Q2: How do you make a colour semi-transparent? Difference between `opacity` and `rgba`?**
A2: `rgb(0 0 0 / 0.5)` or `rgba(0,0,0,.5)` or 8-digit hex `#00000080` makes only that colour transparent. `opacity: 0.5` makes the whole element and all its children transparent, including text. Use alpha colours for backgrounds so text stays solid (topic 68).

**Q3: What are CSS variables and how are they different from Sass variables?**
A3: CSS custom properties (`--x`) are runtime values: they follow the cascade and inheritance, can be scoped to elements, changed via JS/media queries, and are readable with `getComputedStyle`. Sass variables are compile-time and replaced by static values, so they can't change at runtime (no live theming).

**Q4: What is `currentColor`?**
A4: A keyword equal to the element's computed `color`. Used for borders, SVG fills, box-shadows, so icons and borders automatically match the text colour on hover/themes. Example: `svg { fill: currentColor }`.

**Q5: How do you implement dark mode with variables?**
A5: Define colours as variables on `:root`, then override them under `[data-theme="dark"]` or `@media (prefers-color-scheme: dark)`. Components only use `var(--bg)` etc, so no component code changes. Persist the user's choice in localStorage and set the attribute early to avoid a flash.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Using `opacity` to fade a background
```css
/* WRONG: text becomes faded too */
.hero { background: black; opacity: 0.5; }

/* CORRECT */
.hero { background: rgb(0 0 0 / 0.5); }
```

❌ **Mistake 2:** Hard-coding the same hex everywhere
```css
/* WRONG */
.a { color: #e23744; } .b { border-color: #e23744; }

/* CORRECT */
:root { --brand: #e23744; }
.a { color: var(--brand); } .b { border-color: var(--brand); }
```

❌ **Mistake 3:** Low contrast text
```css
/* WRONG: light grey on white, ratio ~1.6:1 */
p { color: #ccc; background: #fff; }

/* CORRECT: at least 4.5:1 */
p { color: #595959; background: #fff; }
```

❌ **Mistake 4:** Using a variable that is not in scope / typo
```css
/* WRONG: --brnd undefined -> declaration becomes invalid at computed time (inherits/initial) */
.btn { background: var(--brnd); }

/* CORRECT: give a fallback and check the name */
.btn { background: var(--brand, #e23744); }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hex | `#RRGGBB` colour code | 16-आधार रंग कोड |
| RGB / RGBA | Red-Green-Blue (+ alpha) | लाल-हरा-नीला (+ पारदर्शिता) |
| HSL | Hue-Saturation-Lightness | रंग-गाढ़ापन-हल्कापन |
| Alpha | Transparency 0-1 | पारदर्शिता |
| currentColor | Element's own text colour | Text वाला रंग |
| CSS variable | `--name` custom property | Reusable मान |
| :root | Top element (`html`) for globals | Global scope |
| Contrast ratio | Text vs background readability | पढ़ने लायक अंतर |

---

## ⚡ 3-Line Summary
**English:**
1. Colours can be named, hex, `rgb()`, `hsl()` (alpha via `/ 0.5`); use hsl to build shades and rgb for transparency.
2. `currentColor` reuses the text colour; alpha colours differ from `opacity` because they don't fade children.
3. Store colours in CSS variables on `:root` and swap them for themes and dark mode.

**Hindi:**
1. रंग named, hex, `rgb()`, `hsl()` में लिखे जाते हैं (alpha `/ 0.5` से); shades के लिए hsl, transparency के लिए rgb।
2. `currentColor` text का रंग दोबारा use करता है; alpha रंग `opacity` से अलग हैं क्योंकि children fade नहीं होते।
3. रंगों को `:root` के CSS variables में रखो और theme/dark mode के लिए बदलो।

---

## ➡️ Next Topic
**58. CSS Units** — px, em, rem, %, vh, vw — कब कौन सी unit use करें ताकि layout और font responsive रहें।
