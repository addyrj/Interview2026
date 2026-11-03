# 59. Typography (font-family, size, weight, line-height)
# हिंदी में: Typography — Text को पढ़ने लायक और सुंदर बनाना

---

## 🔵 Simple Definition (English)
Typography in CSS controls how text looks: **`font-family`** (which typeface), **`font-size`** (how big), **`font-weight`** (how bold), and **`line-height`** (space between lines). Good typography makes content easy to read.

## 🔵 सरल परिभाषा (Hindi)
CSS Typography तय करती है कि text कैसा दिखे: **`font-family`** (कौन सा font), **`font-size`** (कितना बड़ा), **`font-weight`** (कितना मोटा), और **`line-height`** (lines के बीच जगह)। अच्छी typography से content पढ़ना आसान होता है।

---

## 🔴 Problem it Solves
```
PROBLEM:
  - Default browser font is Times-like serif: looks dated and different on each OS.
  - Font not installed on user's device -> random fallback, layout shifts.
  - Lines too tight (line-height: 1) -> text feels cramped and hard to read.
  - Headings and body look the same -> no visual hierarchy.

SOLUTION:
  body { font-family: "Inter", system-ui, sans-serif;  /* fallback stack */
         font-size: 1rem; line-height: 1.6; }
  h1   { font-size: 2rem; font-weight: 700; }
```

## 🔴 यह क्यों बना? (Hindi)
```
समस्या:
  - Browser का default font पुराना serif दिखता है और हर OS पर अलग।
  - अगर font user के device पर नहीं है तो random font आ जाता है।
  - line-height कम हो तो text भींचा हुआ लगता है।
  - Heading और body एक जैसे दिखें तो hierarchy समझ नहीं आती।

हल: font stack (fallback fonts), सही size, weight और line-height 1.5-1.7।
```

---

## 🟢 How it Works — Step by Step

```
1. font-family  (a list = FONT STACK; browser uses the first one available)
     font-family: "Inter", "Segoe UI", Arial, sans-serif;
     - Names with spaces need quotes.  Last item = GENERIC family:
       serif | sans-serif | monospace | cursive | system-ui | ui-monospace
     - Web fonts: @font-face (own file) or Google Fonts <link>; add font-display: swap

2. font-size
     16px is the browser default (= 1rem). Use rem. Keywords: small, medium, large (rare).
     Scale example:  0.875rem small, 1rem body, 1.25rem h3, 1.5rem h2, 2rem h1.
     Fluid: clamp(1.5rem, 1rem + 2vw, 3rem)

3. font-weight
     100 thin | 300 light | 400 normal (default) | 500 medium | 600 semibold | 700 bold | 900 black
     keywords: normal = 400, bold = 700.  Only weights the font FILE contains will look different
     (else browser fakes/rounds it). Variable fonts allow any number 1-1000.

4. line-height   (vertical space of one line)
     UNITLESS is best:  line-height: 1.6   -> 1.6 x the element's OWN font size (inherited as the ratio)
     With units (1.6rem / 150%) the COMPUTED px value is inherited -> children with bigger text overlap!
     Body text 1.5-1.7, headings 1.1-1.3.   WCAG: at least 1.5 for body.

5. SHORTHAND  font: [style] [weight] size/line-height family
     font: italic 600 1rem/1.6 "Inter", sans-serif;     (size and family are REQUIRED; missing parts reset)

6. Related: font-style (italic), font-variant, letter-spacing (topic 60),
   font-display (swap = show fallback instantly then swap), font-optical-sizing.

READABILITY RULES:  45-75 characters per line (max-width: 65ch), contrast >= 4.5:1,
                    left aligned for long text, avoid ALL CAPS paragraphs.
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. font-family: list होती है (font stack); browser पहला उपलब्ध font use करता है।
   आखिर में generic family ज़रूर रखो (sans-serif, serif, monospace)।
   Web fonts @font-face या Google Fonts से, और font-display: swap लगाओ।

2. font-size: default 16px = 1rem। rem में लिखो। Hierarchy बनाओ: h1 > h2 > p।

3. font-weight: 400 normal, 500 medium, 600 semibold, 700 bold।
   वही weights दिखेंगे जो font file में हों।

4. line-height: बिना unit के लिखो (1.6)। unit के साथ (1.6rem) लिखा तो children को वही
   पक्की px value मिलती है और बड़े text वाले children की lines overlap हो सकती हैं।
   Body के लिए 1.5-1.7, headings के लिए 1.1-1.3।

5. Shorthand: font: 600 1rem/1.6 "Inter", sans-serif;  (size + family ज़रूरी)

पढ़ने के नियम: एक line में 45-75 अक्षर (max-width: 65ch), अच्छा contrast।
```

---

## 🟡 Real World Example
**Gmail / Amazon / Medium:** Gmail uses Google Sans/Roboto with a `system-ui` fallback so the UI loads instantly. Amazon product titles are 16-18px with `line-height: 1.3`, prices bold (`700`), and secondary info 13px regular grey, creating clear hierarchy. Medium articles use `max-width ~ 680px`, `font-size: 21px`, `line-height: 1.58` for long reading comfort. All of them define a fallback stack so nothing breaks if the web font is blocked.

## 🟡 Real Example Hindi mein
**Gmail / Amazon / Medium:** Gmail Google Sans/Roboto use करता है और fallback में `system-ui` रखता है ताकि UI तुरंत load हो। Amazon के product titles 16-18px, `line-height: 1.3`, price bold (`700`), और दूसरी info 13px grey — साफ hierarchy। Medium के articles में `max-width ~680px`, `font-size: 21px`, `line-height: 1.58` है ताकि लंबा लेख आराम से पढ़ा जाए। सब fallback stack रखते हैं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Typography Demo</title>

  <!-- Google Font (needs internet). If blocked, the fallback stack still looks fine -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">

  <style>
    * { box-sizing: border-box; }

    body {
      /* FONT STACK: Inter -> system UI -> any sans-serif */
      font-family: "Inter", system-ui, -apple-system, "Segoe UI", Arial, sans-serif;
      font-size: 1rem;          /* 16px base, respects user setting */
      line-height: 1.6;         /* unitless: inherited as ratio */
      color: #1f2937;
      background: #fff;
      margin: 0; padding: 24px;
      max-width: 720px;
    }

    /* HIERARCHY: size + weight + tighter line-height for headings */
    h1 { font-size: 2rem;    font-weight: 700; line-height: 1.2; margin: 0 0 .5rem; }
    h2 { font-size: 1.5rem;  font-weight: 600; line-height: 1.3; margin: 2rem 0 .5rem; }
    h3 { font-size: 1.125rem;font-weight: 600; line-height: 1.4; margin: 1.5rem 0 .25rem; }

    p  { margin: 0 0 1rem; max-width: 65ch; }   /* readable line length */

    .muted { font-size: .875rem; color: #6b7280; }      /* secondary text */
    .price { font-weight: 700; font-size: 1.25rem; }    /* emphasised number */
    .mono  { font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace; background:#f3f4f6; padding:2px 6px; border-radius:4px; }
    .serif { font-family: Georgia, "Times New Roman", serif; font-style: italic; }

    /* WEIGHT SCALE demo */
    .w300 { font-weight: 300; } .w400 { font-weight: 400; } .w600 { font-weight: 600; } .w700 { font-weight: 700; }

    /* LINE-HEIGHT demo */
    .lh-tight { line-height: 1;   background: #fee2e2; }   /* cramped */
    .lh-good  { line-height: 1.6; background: #dcfce7; }   /* comfortable */

    /* Bug demo: line-height WITH unit is inherited as fixed px */
    .lh-unit { line-height: 1.6rem; background: #fef3c7; }
    .lh-unit .big { font-size: 2rem; }           /* line box stays 25.6px -> lines crowd */
    .lh-ratio { line-height: 1.6; background: #dbeafe; }
    .lh-ratio .big { font-size: 2rem; }          /* line box = 2rem x 1.6 -> correct */

    /* SHORTHAND */
    .short { font: italic 600 1.125rem/1.5 Georgia, serif; }

    /* FLUID heading */
    .fluid { font-size: clamp(1.5rem, 1rem + 2vw, 2.5rem); }
  </style>
</head>
<body>
  <h1>Biryani Blues</h1>
  <p class="muted">Posted on 2 Nov · 5 min read</p>

  <p>Good typography is invisible: readers just feel it is easy. This paragraph uses a 1.6 line-height and a 65ch maximum width, the sweet spot for long text.</p>

  <h2>Weights</h2>
  <p><span class="w300">300 Light</span> · <span class="w400">400 Regular</span> · <span class="w600">600 Semibold</span> · <span class="w700">700 Bold</span></p>

  <h2>Families</h2>
  <p>Sans body, <span class="serif">serif accent</span>, and <span class="mono">monospace code()</span>.</p>

  <h2>Line height</h2>
  <p class="lh-tight">line-height: 1 — lines of text touch each other and feel cramped when the paragraph wraps onto the second line.</p>
  <p class="lh-good">line-height: 1.6 — comfortable spacing between lines, much easier on the eyes for the same paragraph that wraps across lines.</p>

  <h3>Unit vs unitless</h3>
  <div class="lh-unit">Small text <span class="big">BIG text</span> and more small text after it that wraps again and again.</div>
  <br>
  <div class="lh-ratio">Small text <span class="big">BIG text</span> and more small text after it that wraps again and again.</div>

  <h3>Shorthand and fluid</h3>
  <p class="short">font: italic 600 1.125rem/1.5 Georgia, serif</p>
  <p class="fluid">Fluid size using clamp()</p>

  <p class="price">Rs. 499 <span class="muted">Free delivery</span></p>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Next.js font optimisation: self-hosted, no layout shift, no external request
// app/layout.tsx
import { Inter, Roboto_Mono } from "next/font/google";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });
const mono  = Roboto_Mono({ subsets: ["latin"], variable: "--font-mono" });

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${inter.variable} ${mono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
// globals.css:  body { font-family: var(--font-inter), system-ui, sans-serif; line-height: 1.6; }

// 2. Tailwind typography utilities
<h1 className="text-3xl font-bold leading-tight">Title</h1>
<p className="text-base leading-relaxed text-gray-700 max-w-prose">Body</p>
<code className="font-mono text-sm">code</code>
// tailwind.config.js -> theme.extend.fontFamily: { sans: ["var(--font-inter)", "system-ui"] }

// 3. Do NOT put <link> to Google Fonts inside components repeatedly; use next/font.
// 4. Inline style in React: fontSize: 16 (px), fontWeight: 600, lineHeight: 1.6 (unitless)
<p style={{ fontWeight: 600, lineHeight: 1.6 }}>Hello</p>
```

---

## ⚫ Interview Questions + Answers

**Q1: What is a font stack and why does the last value matter?**
A1: `font-family` accepts a comma-separated list; the browser uses the first font that is available. The last should be a generic family (`sans-serif`, `serif`, `monospace`, `system-ui`) so some reasonable font is always used. Font names with spaces must be quoted.

**Q2: Should `line-height` have a unit?**
A2: Prefer unitless (`1.6`). A unitless number is inherited as a ratio and recalculated per element from its own font size. With units (`1.6rem`, `150%`) the computed pixel value is inherited, so child elements with larger font sizes get the same fixed line height and lines can overlap or look cramped.

**Q3: How do you load a custom font and avoid layout shift or invisible text?**
A3: Use `@font-face` (or Google Fonts / `next/font`) with `font-display: swap` so fallback text shows immediately. Preload critical fonts (`<link rel="preload" as="font" crossorigin>`), use WOFF2, subset the font, and choose a fallback with similar metrics (`size-adjust`) to reduce CLS.

**Q4: What do font-weight numbers mean? Why does `700` sometimes look the same as `600`?**
A4: 100-900 scale (400 normal, 700 bold). A weight only changes visually if the font family provides it (a file for that weight, or a variable font). Otherwise the browser picks the nearest available weight or fakes bold. Import only weights you need.

**Q5: What are good typography practices for readability?**
A5: Body 16px+ (1rem), line-height 1.5-1.7, line length 45-75 characters (`max-width: 65ch`), clear hierarchy through size/weight, good contrast (4.5:1), fewer than 2-3 font families, use `rem` so users can scale text.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** No fallback fonts
```css
/* WRONG: if Inter fails, you get default serif */
body { font-family: "Inter"; }

/* CORRECT */
body { font-family: "Inter", system-ui, sans-serif; }
```

❌ **Mistake 2:** Line-height with units on a parent
```css
/* WRONG: children inherit 24px */
body { line-height: 24px; }

/* CORRECT */
body { line-height: 1.5; }
```

❌ **Mistake 3:** Using pixel font sizes everywhere
```css
/* WRONG: ignores browser font size preference */
p { font-size: 14px; }

/* CORRECT */
p { font-size: 0.875rem; }
```

❌ **Mistake 4:** Using the `font` shorthand and wiping other values accidentally
```css
/* WRONG: resets weight, line-height to defaults, and is invalid without a family */
h1 { font-weight: 700; }
h1 { font: 2rem; }          /* invalid: family missing, whole line ignored */

/* CORRECT */
h1 { font: 700 2rem/1.2 "Inter", sans-serif; }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| font-family | Typeface list (stack) | Font की list |
| Generic family | serif, sans-serif, monospace | आखिरी fallback type |
| font-size | Size of text | Text का आकार |
| font-weight | Boldness 100-900 | मोटाई |
| line-height | Height of each line | Lines की ऊँचाई |
| @font-face | Define custom font file | अपना font जोड़ना |
| font-display: swap | Show fallback until font loads | Font आने तक fallback |
| Variable font | One file, many weights | एक file में कई weights |

---

## ⚡ 3-Line Summary
**English:**
1. `font-family` takes a stack ending in a generic family; `font-size` in `rem`; `font-weight` 400-700; `line-height` unitless 1.5-1.7.
2. Build hierarchy with size and weight, keep lines 45-75 characters long.
3. In Next.js use `next/font`; in Tailwind use `text-*`, `font-*`, `leading-*`.

**Hindi:**
1. `font-family` में stack और आखिर में generic family; `font-size` `rem` में; `font-weight` 400-700; `line-height` बिना unit 1.5-1.7।
2. Size और weight से hierarchy बनाओ, एक line में 45-75 अक्षर रखो।
3. Next.js में `next/font`, Tailwind में `text-*`, `font-*`, `leading-*` use करो।

---

## ➡️ Next Topic
**60. Text Properties** — text-align, text-transform, text-decoration, letter-spacing, ताकि text की alignment और सजावट पर पूरा control मिले।
