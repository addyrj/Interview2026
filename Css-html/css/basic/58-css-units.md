# 58. CSS Units (px, em, rem, %, vh, vw)
# हिंदी में: CSS Units — Size नापने के पैमाने

---

## 🔵 Simple Definition (English)
CSS units say **how big** something is. **Absolute** units (`px`) are fixed. **Relative** units depend on something else: `em` (parent/own font size), `rem` (root font size), `%` (parent's size), `vw`/`vh` (browser window size).

## 🔵 सरल परिभाषा (Hindi)
CSS units बताती हैं कि कोई चीज़ **कितनी बड़ी** है। **Absolute** unit (`px`) fixed होती है। **Relative** units किसी और पर निर्भर होती हैं: `em` (parent/अपना font size), `rem` (root का font size), `%` (parent का size), `vw`/`vh` (browser window का size)।

---

## 🔴 Problem it Solves
```
PROBLEM with only px:
  font-size: 16px everywhere
  - User sets browser font to "Large" for poor eyesight -> your px text ignores it
  - Layout fixed at 1200px breaks on a 375px phone
  - Full-screen hero needs "exactly the screen height" -> impossible in px

SOLUTION - relative units:
  font-size: 1rem        -> respects user's browser setting
  width: 90%             -> adapts to the parent
  height: 100vh          -> exactly the viewport height
  padding: 1.5em         -> scales with the element's own text
```

## 🔴 यह क्यों बना? (Hindi)
```
सिर्फ px से समस्या:
  - कमज़ोर नज़र वाला user browser में बड़ा font चुने तो px वाला text नहीं बदलता
  - 1200px fixed layout 375px फोन पर टूट जाता है
  - "पूरी screen की height" px में लिखना असंभव

Relative units से:
  1rem   -> user की browser setting मानता है
  90%    -> parent के हिसाब से
  100vh  -> screen की पूरी height
  1.5em  -> अपने text size के साथ scale
```

---

## 🟢 How it Works — Step by Step

```
ABSOLUTE
  px   1 CSS pixel (not a physical pixel: on retina 1 css px = 2+ device px)
  (cm, mm, in, pt, pc exist but are for print; rarely used on screen)

RELATIVE TO FONT SIZE
  em   = font-size of the element itself (for font-size: the PARENT's font-size)
         compounds when nested: 1.2em inside 1.2em = 1.44x
  rem  = font-size of <html> (root). Default 16px -> 1rem = 16px.  No compounding.
  ch   = width of the "0" glyph (good for max-width: 60ch text lines)
  lh   = line-height (modern)

RELATIVE TO PARENT
  %    width: 50% -> 50% of the parent's content width
       height: 50% -> only works if parent has an explicit height
       font-size: 120% -> 120% of parent font size
       padding/margin % -> relative to parent's WIDTH (even top/bottom!)

RELATIVE TO VIEWPORT
  vw   1% of viewport width        vh   1% of viewport height
  vmin smaller of vw/vh            vmax larger
  dvh / svh / lvh  "dynamic/small/large" viewport height (mobile address bar fix)
       (dvh: Chrome 108+, Safari 15.4+, Firefox 101+)

QUICK RULE OF THUMB
  font-size      -> rem            (accessible, predictable)
  padding/margin -> rem or em      (em when it should scale with text, like buttons)
  width/layout   -> %, fr, vw, max-width in rem/ch
  borders, shadows, tiny details -> px
  media queries  -> em or px (em respects user font size)

PX TO REM:  16px = 1rem, 24px = 1.5rem, 12px = 0.75rem
TRICK: html { font-size: 62.5% } makes 1rem = 10px (but overrides the user's preference - use with care)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Absolute: px (screen पर 1 CSS pixel)।
em   -> अपने element का font-size (font-size property में parent का)। nested होने पर गुणा होता है।
rem  -> <html> का font-size (default 16px)। गुणा नहीं होता, इसलिए सबसे predictable।
%    -> parent के हिसाब से। height: 50% तभी चलेगा जब parent की height fixed हो।
        padding/margin का % हमेशा parent की WIDTH से निकलता है।
vw / vh -> window की चौड़ाई / ऊँचाई का 1%।
dvh  -> mobile की address bar को ध्यान में रखने वाली height।

Rule of thumb:
  font-size -> rem
  spacing   -> rem / em
  layout    -> %, vw, max-width
  border, shadow -> px

16px = 1rem, 24px = 1.5rem, 12px = 0.75rem
```

---

## 🟡 Real World Example
**Swiggy / Amazon mobile:** the hero banner uses `height: 60vh` so it's always 60% of the screen. Text uses `rem`, so when a visually-impaired user sets a larger system font, the whole app scales. Product grid cards are `width: 48%` on mobile, a button's padding is `0.75em 1.5em` so a bigger button font gets proportionally bigger padding. Borders stay `1px`. On mobile browsers `100vh` includes the hidden address bar, so full-screen sheets use `100dvh`.

## 🟡 Real Example Hindi mein
**Swiggy / Amazon mobile:** hero banner `height: 60vh` है, यानी हमेशा screen का 60%। Text `rem` में है, इसलिए कमज़ोर नज़र वाला user system font बड़ा करे तो पूरा app बड़ा हो जाता है। Cards mobile पर `width: 48%` हैं। Button की padding `0.75em 1.5em` है ताकि font बढ़ने पर padding भी बढ़े। Border `1px` ही रहता है। Mobile पर `100vh` में address bar भी गिनी जाती है, इसलिए full-screen sheet में `100dvh` use होता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CSS Units Demo</title>
  <style>
    * { box-sizing: border-box; }

    /* html font-size is the base for ALL rem values. Keep default 100% (=16px, user's choice) */
    html { font-size: 100%; }
    body { font-family: system-ui, sans-serif; margin: 0; padding: 1rem; background: #f8fafc; }

    h2 { font-size: 0.95rem; margin: 1.5rem 0 0.5rem; }

    /* ── 1. px vs rem ── */
    .px  { font-size: 16px;  background: #fecaca; padding: 4px; }  /* ignores user font setting */
    .rem { font-size: 1rem;  background: #bbf7d0; padding: 4px; }  /* respects user font setting */

    /* ── 2. em compounding ── */
    .em-parent { font-size: 1.25em; background: #e0e7ff; padding: 0.5em; }   /* 20px */
    .em-child  { font-size: 1.25em; background: #c7d2fe; padding: 0.5em; }   /* 25px (20 x 1.25) */
    .em-grand  { font-size: 1.25em; background: #a5b4fc; padding: 0.5em; }   /* 31.25px - grows! */
    /* with rem each would stay 1.25rem = 20px */

    /* ── 3. em for padding scales with the button's own font size ── */
    .btn { background: #2563eb; color: #fff; border: 0; border-radius: 0.4em;
           padding: 0.6em 1.2em;     /* proportional padding */
           cursor: pointer; font: inherit; }
    .btn.big { font-size: 1.5rem; }  /* padding grows automatically */

    /* ── 4. % widths ── */
    .parent { width: 100%; max-width: 500px; background: #e5e7eb; padding: 0.5rem; }
    .half   { width: 50%; background: #fde68a; padding: 0.5rem; }
    .quarter{ width: 25%; background: #fdba74; padding: 0.5rem; }

    /* ── 5. vw / vh ── */
    .hero { height: 30vh;               /* 30% of window height */
            min-height: 120px;
            background: linear-gradient(90deg, #f43f5e, #f59e0b); color: #fff;
            display: grid; place-items: center; }
    .hero h1 { margin: 0; font-size: clamp(1.25rem, 4vw, 2.5rem); }  /* fluid: scales with vw within limits */

    /* ── 6. ch for readable line length ── */
    .article { max-width: 60ch; line-height: 1.6; }   /* ~60 characters per line */

    /* ── 7. dvh for mobile full-screen sheet (falls back to vh) ── */
    .sheet { height: 40vh; height: 40dvh; background: #ddd6fe; display: grid; place-items: center; }

    /* ── 8. px for tiny details ── */
    .hairline { border: 1px solid #111; padding: 0.5rem; box-shadow: 0 2px 6px rgba(0,0,0,.2); }
  </style>
</head>
<body>
  <h2>1. px vs rem (change browser font size in settings to see difference)</h2>
  <div class="px">16px text</div>
  <div class="rem">1rem text</div>

  <h2>2. em compounding</h2>
  <div class="em-parent">parent 1.25em
    <div class="em-child">child 1.25em
      <div class="em-grand">grandchild 1.25em (keeps growing)</div>
    </div>
  </div>

  <h2>3. em padding on buttons</h2>
  <button class="btn">Normal</button> <button class="btn big">Big (padding scales)</button>

  <h2>4. Percent widths</h2>
  <div class="parent"><div class="half">50%</div><br><div class="quarter">25%</div></div>

  <h2>5. vh / vw / clamp</h2>
  <div class="hero"><h1>Fluid heading</h1></div>

  <h2>6. ch</h2>
  <p class="article">This paragraph never grows wider than about sixty characters per line, which keeps long text comfortable to read on wide screens, regardless of font size.</p>

  <h2>7. dvh</h2>
  <div class="sheet">40dvh sheet</div>

  <h2>8. px for hairlines</h2>
  <div class="hairline">1px border, px shadow</div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. React numbers become px automatically in inline styles (unitless number -> px)
<div style={{ width: 300, padding: 16 }} />            // 300px, 16px
<div style={{ width: "50%", fontSize: "1.25rem" }} />  // strings for other units
// Exception: unitless props stay unitless: lineHeight: 1.5, opacity, zIndex, flex

// 2. Tailwind scale is rem based (1 unit = 0.25rem = 4px at default)
<div className="p-4 text-lg w-1/2 h-screen min-h-dvh max-w-prose" />
//   p-4 = 1rem, w-1/2 = 50%, h-screen = 100vh, min-h-dvh = 100dvh, max-w-prose = 65ch
<div className="w-[37.5rem] h-[60vh]" />   // arbitrary values

// 3. Fluid typography in global CSS (Next.js globals.css)
/* h1 { font-size: clamp(1.5rem, 1rem + 2vw, 3rem); } */

// 4. SSR note: don't read window.innerHeight during render in Next.js (server has no window).
//    Prefer CSS vh/dvh units over JS measurements.
```

---

## ⚫ Interview Questions + Answers

**Q1: Difference between `em` and `rem`?**
A1: `rem` is relative to the root `<html>` font-size (usually 16px), so it never compounds. `em` is relative to the element's own font size (or the parent's when used on `font-size`), so nested elements compound: `1.2em` inside `1.2em` becomes 1.44x. Use `rem` for font sizes and global spacing; `em` for components whose padding should scale with their text, like buttons.

**Q2: Why is `rem` preferred over `px` for font sizes?**
A2: Accessibility. Users can change the default browser font size; `rem` respects it while `px` does not. WCAG recommends text can be resized to 200%. Also makes scaling the whole UI easy by changing the root size.

**Q3: What is the difference between `vh` and `%` for height? Why does `100vh` break on mobile?**
A3: `%` height needs the parent to have a defined height; `vh` is the viewport height, independent of parents. On mobile browsers `100vh` is the tall viewport (address bar hidden), so content gets cut when the bar is visible. Use `100dvh` (dynamic viewport) or `svh`/`lvh` as needed.

**Q4: Is `padding: 10%` relative to height or width?**
A4: Relative to the **width** of the containing block, for all four sides (including top/bottom). This is the basis of the old "padding-top: 56.25%" 16:9 trick; today use `aspect-ratio: 16 / 9`.

**Q5: When should I still use `px`?**
A5: For things that shouldn't scale with text: 1px borders, box shadows, outlines, thin dividers, and sometimes media query breakpoints. Everything about typography and spacing is better in `rem`/`em`.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Using `px` for all font sizes
```css
/* WRONG: ignores browser font setting */
body { font-size: 14px; }

/* CORRECT */
body { font-size: 1rem; }   /* or 100% */
```

❌ **Mistake 2:** Nested `em` surprises
```css
/* WRONG: each nested list gets bigger */
li { font-size: 1.2em; }

/* CORRECT */
li { font-size: 1.2rem; }
```

❌ **Mistake 3:** Percent height with no parent height
```css
/* WRONG: div collapses; height:50% does nothing */
.child { height: 50%; }

/* CORRECT */
.parent { height: 400px; }  .child { height: 50%; }
/* or: .child { height: 50vh; } */
```

❌ **Mistake 4:** `width: 100vw` causing horizontal scroll
```css
/* WRONG: 100vw includes the vertical scrollbar width -> horizontal scroll */
.banner { width: 100vw; }

/* CORRECT */
.banner { width: 100%; }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| px | CSS pixel, absolute | पक्की इकाई |
| em | Relative to element/parent font size | अपने font के हिसाब से |
| rem | Relative to root font size | Root font के हिसाब से |
| % | Relative to parent | Parent के हिसाब से |
| vw / vh | 1% of viewport width / height | Window का 1% |
| dvh | Dynamic viewport height | Mobile-safe height |
| ch | Width of "0" character | अक्षर की चौड़ाई |
| Viewport | Visible browser area | Browser का दिखने वाला हिस्सा |

---

## ⚡ 3-Line Summary
**English:**
1. `px` is fixed; `rem` follows root font size, `em` follows the element, `%` follows the parent, `vw/vh` follow the viewport.
2. Use `rem` for text and spacing (accessible), `%`/`max-width` for layout, `px` for borders and shadows.
3. Prefer `dvh` over `vh` on mobile and avoid `100vw` to prevent overflow.

**Hindi:**
1. `px` fixed है; `rem` root font, `em` अपना font, `%` parent, `vw/vh` window के हिसाब से चलते हैं।
2. Text और spacing के लिए `rem`, layout के लिए `%`/`max-width`, border-shadow के लिए `px`।
3. Mobile पर `vh` की जगह `dvh` और overflow से बचने के लिए `100vw` से परहेज़ करो।

---

## ➡️ Next Topic
**59. Typography** — font-family, font-size, font-weight, line-height से text को पढ़ने लायक और सुंदर बनाना।
