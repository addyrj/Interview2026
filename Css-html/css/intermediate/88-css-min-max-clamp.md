# 88. CSS Functions (min, max, clamp)
# हिंदी में: min(), max(), clamp() — बिना Media Query के Responsive Sizes

---

## 🔵 Simple Definition (English)
`min()` picks the smallest of its values, `max()` picks the largest, and `clamp(MIN, PREFERRED, MAX)` keeps a value between a lower and upper limit while letting it scale in between. They are evaluated live in the browser, so they make responsive widths, spacing and fluid typography possible without media queries.

## 🔵 सरल परिभाषा (Hindi)
`min()` दी गई values में से सबसे छोटी चुनता है, `max()` सबसे बड़ी, और `clamp(MIN, PREFERRED, MAX)` value को निचली और ऊपरी सीमा के बीच रखता है और बीच में scale होने देता है। ये browser में live evaluate होते हैं, इसलिए media queries के बिना responsive width, spacing और fluid typography बनती है।

---

## 🔴 Problem it Solves
```
BEFORE:
  /* Container: 90% wide but never above 1200px */
  .container { width: 90%; }
  @media (min-width: 1334px) { .container { width: 1200px; } }

  /* Font grows with screen but stays between 16px and 24px */
  p { font-size: 16px; }
  @media (min-width: 600px)  { p { font-size: 18px; } }
  @media (min-width: 900px)  { p { font-size: 20px; } }
  @media (min-width: 1200px) { p { font-size: 24px; } }
  /* Stepped, many breakpoints, tedious */

AFTER:
  .container { width: min(90%, 1200px); }
  p { font-size: clamp(1rem, 0.9rem + 0.5vw, 1.5rem); }
  /* Smooth scaling, one line, no breakpoints */
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  Container 90% चौड़ा पर 1200px से ज़्यादा नहीं: media query लिखनी पड़ती थी।
  Font screen के साथ बढ़े पर 16px से 24px के बीच रहे: 4-5 breakpoints, और size सीढ़ी की तरह कूदती थी।

अब:
  width: min(90%, 1200px);
  font-size: clamp(1rem, 0.9rem + 0.5vw, 1.5rem);
  एक line, smooth scaling, कोई breakpoint नहीं।
```

---

## 🟢 How it Works — Step by Step

```
min(a, b, c ...)     returns the SMALLEST value.   -> acts as a MAXIMUM limit
max(a, b, c ...)     returns the LARGEST value.    -> acts as a MINIMUM limit
clamp(MIN, VAL, MAX) = max(MIN, min(VAL, MAX))     -> value limited on both sides

THE "REVERSED" NAMING TRICK (common interview trap):
  width: min(90%, 1200px)   -> "width is 90%, but at most 1200px"   (min() caps the upper bound)
  width: max(300px, 50%)    -> "width is 50%, but at least 300px"   (max() sets the lower bound)

STEP BY STEP for clamp(1rem, 2.5vw, 2rem)  on a 1000px-wide viewport:
  1. MIN       = 1rem   = 16px
  2. PREFERRED = 2.5vw  = 25px
  3. MAX       = 2rem   = 32px
  4. 25px is between 16 and 32 -> result 25px.
  On a 400px viewport: preferred = 10px < MIN -> result 16px.
  On a 1600px viewport: preferred = 40px > MAX -> result 32px.

FEATURES:
  - Mix units freely: clamp(320px, 50%, 40rem)
  - Math inside without calc(): min(100%, 600px - 2rem) , clamp(1rem, 0.5rem + 2vw, 3rem)
    (inside these functions, +, -, *, / work like calc, and need spaces for + and -)
  - Nest them: max(16px, min(5vw, 32px))
  - Works with CSS variables: clamp(var(--min), 4vw, var(--max))

FLUID TYPOGRAPHY FORMULA:
  font-size: clamp(minSize, intercept + slope*vw, maxSize)
  Example: clamp(1rem, 0.8rem + 1vw, 2rem)
  Using only vw (e.g. 5vw) ignores the user's browser font-size setting and breaks zoom;
  adding a rem term keeps it zoomable (WCAG 1.4.4).

WHERE IT WORKS: any property accepting length, percentage, angle, time, number, e.g.
  width, max-width, padding, margin, gap, font-size, border-radius, grid-template-columns, line-height (numbers)

SUPPORT: Chrome 79+, Firefox 75+, Safari 13.1+. Not in IE11.
  Fallback: declare a plain value first, then the clamp() line (older browsers drop the invalid one):
     font-size: 1.25rem;
     font-size: clamp(1rem, 2vw, 2rem);

RELATED: `min()` and `max()` with `%` in `grid-template-columns: repeat(auto-fit, minmax(min(100%, 250px), 1fr))`
  -> prevents overflow on screens narrower than 250px.
```

## 🟢 कैसे काम करता है? (Hindi)

```
min(a, b, c)         सबसे छोटी value देता है  -> ऊपरी सीमा (maximum) की तरह काम करता है
max(a, b, c)         सबसे बड़ी value देता है  -> निचली सीमा (minimum) की तरह काम करता है
clamp(MIN, VAL, MAX) = max(MIN, min(VAL, MAX))  -> दोनों तरफ सीमा

नाम उल्टा लगता है (interview का trap):
  width: min(90%, 1200px)  = "90% चौड़ा, पर 1200px से ज़्यादा नहीं"
  width: max(300px, 50%)   = "50% चौड़ा, पर 300px से कम नहीं"

clamp(1rem, 2.5vw, 2rem) का step by step (1000px viewport):
  1. MIN = 16px, PREFERRED = 25px, MAX = 32px
  2. 25px बीच में है -> result 25px
  400px viewport पर preferred = 10px < MIN -> result 16px
  1600px viewport पर preferred = 40px > MAX -> result 32px

Fluid typography: clamp(1rem, 0.8rem + 1vw, 2rem)
सिर्फ vw use करोगे तो user की browser font setting और zoom टूटते हैं, इसलिए rem का हिस्सा जोड़ो।

Fallback: पहले साधारण value लिखो, फिर clamp() वाली line।
```

---

## 🟡 Real World Example
**Apple, Stripe, Swiggy, Zomato:** Marketing pages like Apple's or Stripe's have headlines that grow smoothly from phone to wide desktop without jumping, which is the pattern `font-size: clamp(2rem, 5vw, 4.5rem)`. Zomato's and Amazon's page wrappers use `width: min(100% - 2rem, 1200px)` so there is 1rem padding on small screens and a max width on big ones. Swiggy's restaurant grid uses `repeat(auto-fill, minmax(min(100%, 260px), 1fr))` to show as many cards per row as fit, and one card on tiny phones without overflow. Section padding such as `padding-block: clamp(2rem, 6vw, 6rem)` is also common.

## 🟡 Real Example Hindi mein
**Apple, Stripe, Swiggy, Zomato:** Apple या Stripe जैसे marketing pages की headlines phone से बड़े desktop तक बिना कूदे धीरे-धीरे बढ़ती हैं: `font-size: clamp(2rem, 5vw, 4.5rem)`। Zomato/Amazon के page wrappers `width: min(100% - 2rem, 1200px)` use करते हैं: छोटी screen पर 1rem किनारा और बड़ी screen पर max width। Swiggy की restaurant grid `repeat(auto-fill, minmax(min(100%, 260px), 1fr))` से जितने cards समाएँ उतने एक row में दिखाती है और छोटे phone पर बिना overflow एक card। Section padding भी `padding-block: clamp(2rem, 6vw, 6rem)` से बनती है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CSS min() max() clamp() Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }

    body {
      margin: 0; font-family: system-ui, sans-serif; background: #f6f7f9; color: #222;
      /* 1. FLUID BASE TEXT: never below 16px, never above 20px */
      font-size: 1rem;                                       /* fallback for old browsers */
      font-size: clamp(1rem, 0.95rem + 0.25vw, 1.25rem);
      line-height: 1.6;
    }

    /* 2. min(): responsive container with side padding and a max width.
          Reads as "100% minus 2rem, but no more than 1100px". */
    .wrapper {
      width: min(100% - 2rem, 1100px);
      margin-inline: auto;                                  /* centre horizontally */
    }

    /* 3. clamp() headline: smooth growth between 2rem and 4rem */
    h1 {
      font-size: clamp(2rem, 1rem + 5vw, 4rem);             /* rem term keeps zoom friendly */
      line-height: 1.1;
      margin: 0 0 0.5em;
    }

    /* 4. clamp() for spacing */
    header.hero {
      background: linear-gradient(135deg, #ff5a5f, #f5a623);
      color: #fff;
      padding-block: clamp(2rem, 8vw, 6rem);                /* tight on phones, roomy on desktop */
    }

    /* 5. max(): a minimum size. Button text never smaller than 14px, width at least 120px */
    .btn {
      display: inline-block;
      min-width: max(120px, 20%);                           /* at least 120px OR 20%, whichever is larger */
      font-size: max(14px, 1rem);                           /* guard against tiny text */
      padding: 0.75em 1.25em;
      background: #fff; color: #ff5a5f; border-radius: 999px; text-align: center; font-weight: 700;
      text-decoration: none;
    }

    /* 6. RESPONSIVE GRID with no media query: min(100%, 260px) avoids overflow on tiny screens */
    .grid {
      display: grid;
      gap: clamp(0.75rem, 2vw, 1.5rem);                     /* fluid gap */
      grid-template-columns: repeat(auto-fill, minmax(min(100%, 260px), 1fr));
      padding-block: 2rem;
    }
    .card { background: #fff; border-radius: 12px; padding: clamp(1rem, 2vw, 1.5rem); box-shadow: 0 2px 8px rgba(0,0,0,.1); }
    .card h3 { margin: 0 0 .25rem; font-size: clamp(1.05rem, 0.95rem + 0.5vw, 1.35rem); }

    /* 7. Readable line length: about 65 characters wide, never wider than the container */
    .article { max-width: min(65ch, 100%); }

    /* 8. Live readout so you can see the values change when you resize */
    .readout { font: 13px/1.5 ui-monospace, monospace; background: #222; color: #9ef; padding: 12px; border-radius: 8px; }
  </style>
</head>
<body>
  <header class="hero">
    <div class="wrapper">
      <h1>Hungry? Order in minutes</h1>
      <p>Resize the browser window: the heading, padding and grid adapt smoothly with no media queries.</p>
      <a class="btn" href="#grid">Browse</a>
    </div>
  </header>

  <main class="wrapper" id="grid">
    <div class="grid">
      <div class="card"><h3>Biryani House</h3><p>4.4 stars - 25 min</p></div>
      <div class="card"><h3>Pizza Corner</h3><p>4.1 stars - 30 min</p></div>
      <div class="card"><h3>South Tiffin</h3><p>4.6 stars - 20 min</p></div>
      <div class="card"><h3>Chai Point</h3><p>4.2 stars - 15 min</p></div>
    </div>

    <p class="article">
      This paragraph is limited with <code>max-width: min(65ch, 100%)</code> so lines stay readable on wide
      screens and never overflow on narrow ones.
    </p>

    <div class="readout" id="readout">Calculating...</div>
  </main>

  <script>
    // Show the computed font-size of the h1 so the clamp() behaviour is visible while resizing
    const h1 = document.querySelector('h1');
    const out = document.getElementById('readout');
    function update() {
      const fs = getComputedStyle(h1).fontSize;             // resolved clamp() value in px
      out.textContent = 'viewport: ' + window.innerWidth + 'px | h1 font-size: ' + fs;
    }
    window.addEventListener('resize', update);
    update();
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Tailwind arbitrary values (underscores for spaces):
<h1 className="text-[clamp(2rem,1rem+5vw,4rem)] font-bold leading-tight">Hungry?</h1>
<div className="mx-auto w-[min(100%-2rem,1100px)]">Content</div>
<section className="py-[clamp(2rem,8vw,6rem)]">Hero</section>

// 2. Extend the Tailwind theme with fluid font sizes (tailwind.config.js)
// theme: { extend: { fontSize: {
//   'fluid-h1': 'clamp(2rem, 1rem + 5vw, 4rem)',
//   'fluid-body': 'clamp(1rem, 0.95rem + 0.25vw, 1.25rem)',
// } } }
<h1 className="text-fluid-h1">Title</h1>

// 3. Design tokens as CSS variables (topic 77) in globals.css for Next.js
/*
:root {
  --step-0: clamp(1rem, 0.95rem + 0.25vw, 1.25rem);
  --step-3: clamp(2rem, 1rem + 5vw, 4rem);
  --container: min(100% - 2rem, 1100px);
}
h1 { font-size: var(--step-3); }
.container { width: var(--container); margin-inline: auto; }
*/

// 4. Responsive grid with no JS media-query hook (avoid useMediaQuery just for sizing)
<div style={{ display: 'grid', gap: 'clamp(0.75rem, 2vw, 1.5rem)',
              gridTemplateColumns: 'repeat(auto-fill, minmax(min(100%, 260px), 1fr))' }}>
  {restaurants.map(r => <Card key={r.id} {...r} />)}
</div>

// 5. Benefit in Next.js SSR: pure CSS sizing means no hydration flicker from
//    window.innerWidth checks in JS.
```

---

## ⚫ Interview Questions + Answers

**Q1: What do `min()`, `max()` and `clamp()` do?**
A1: `min(a, b)` returns the smaller value; `max(a, b)` returns the larger; `clamp(MIN, PREFERRED, MAX)` returns the preferred value limited between MIN and MAX; it is shorthand for `max(MIN, min(PREFERRED, MAX))`. All accept mixed units and math expressions and are computed at runtime from the viewport/parent.

**Q2: Why does `min()` act as a maximum and `max()` act as a minimum?**
A2: Because they pick the smaller or larger result, the effect on the value is the opposite of the name. `width: min(90%, 1200px)` can never exceed 1200px (a cap, like `max-width`), while `width: max(300px, 50%)` can never go below 300px (a floor, like `min-width`). A simple way to remember: "min() = at most", "max() = at least".

**Q3: How do you build fluid typography with `clamp()`?**
A3: Choose a lower and upper size and a preferred value that scales with the viewport: `font-size: clamp(1rem, 0.8rem + 1vw, 2rem)`. Below a certain width it stays at 1rem, above another it stays at 2rem, and smoothly scales between. Include a `rem` part in the preferred value; using only `vw` ignores the user's font-size preference and prevents text from enlarging on zoom, which is an accessibility failure (WCAG 1.4.4 Resize Text).

**Q4: Do you still need media queries if you use `clamp()`?**
A4: Fewer, but yes. `clamp()` handles continuous scaling of single properties (font size, spacing, widths). Media queries (or container queries) are still needed for structural changes: switching from 1 to 3 columns, hiding a sidebar, changing the nav layout. A common modern approach is `repeat(auto-fill, minmax(min(100%, 260px), 1fr))` for grids so that many layouts need no breakpoints at all.

**Q5: Are `min`/`max`/`clamp` the same as `calc()`? What are the browser support and fallbacks?**
A5: They are related math functions: inside them you can use `calc`-style arithmetic without writing `calc()` (spaces around `+`/`-` still required). Unlike `calc()`, they choose between candidates. Support: Chrome 79+, Firefox 75+, Safari 13.1+. For older browsers declare a static fallback line before the `clamp()` line, since browsers ignore declarations they cannot parse.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Swapping the order of arguments in `clamp()`
```css
/* WRONG: min and max reversed, result is stuck at the upper value */
h1 { font-size: clamp(4rem, 5vw, 2rem); }

/* CORRECT: MIN, PREFERRED, MAX */
h1 { font-size: clamp(2rem, 5vw, 4rem); }
```

❌ **Mistake 2:** Fluid font size made only from `vw`
```css
/* WRONG: ignores user's font-size setting; zooming the page doesn't enlarge the text */
p { font-size: 2vw; }

/* CORRECT: mix rem and vw */
p { font-size: clamp(1rem, 0.9rem + 0.5vw, 1.5rem); }
```

❌ **Mistake 3:** Forgetting spaces around `+` and `-` inside the functions
```css
/* WRONG: invalid, declaration dropped */
.box { width: min(100%-2rem, 1100px); }

/* CORRECT */
.box { width: min(100% - 2rem, 1100px); }
```

❌ **Mistake 4:** Confusing `min()`/`max()` meaning
```css
/* WRONG intent: "I want at least 300px" but this CAPS the width at 300px */
.card { width: min(300px, 100%); }

/* CORRECT for a floor */
.card { width: max(300px, 50%); }
```

❌ **Mistake 5:** Using a grid min size that overflows on tiny screens
```css
/* WRONG: horizontal scroll on screens narrower than 260px */
.grid { grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }

/* CORRECT */
.grid { grid-template-columns: repeat(auto-fill, minmax(min(100%, 260px), 1fr)); }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| min() | Smallest of values (acts as a cap) | सबसे छोटी value (ऊपरी सीमा) |
| max() | Largest of values (acts as a floor) | सबसे बड़ी value (निचली सीमा) |
| clamp() | Value bounded by MIN and MAX | MIN और MAX के बीच बंधी value |
| fluid typography | Font size scales smoothly with viewport | Screen के साथ smooth बढ़ता font |
| preferred value | Middle argument of clamp() | clamp() की बीच वाली value |
| vw | 1% of viewport width | Viewport चौड़ाई का 1% |
| `ch` | Width of the "0" glyph, used for line length | Text की line length की unit |
| fallback declaration | Plain value placed before newer syntax | पुराने browsers के लिए backup line |

---

## ⚡ 3-Line Summary
**English:**
1. `min()` picks the smallest value (acts as a maximum), `max()` the largest (acts as a minimum), and `clamp(MIN, PREFERRED, MAX)` keeps a value within bounds.
2. They create fluid fonts, spacing and container widths without breakpoints, e.g. `width: min(100% - 2rem, 1100px)`.
3. Add a `rem` term to fluid font sizes for accessibility, and use media/container queries only for structural layout changes.

**Hindi:**
1. `min()` सबसे छोटी value चुनता है (cap), `max()` सबसे बड़ी (floor), और `clamp(MIN, PREFERRED, MAX)` value को सीमा में रखता है।
2. बिना breakpoints के fluid font, spacing और container width बनती है, जैसे `width: min(100% - 2rem, 1100px)`।
3. Accessibility के लिए fluid font में `rem` का हिस्सा जोड़ो, और media/container queries सिर्फ structural layout बदलने के लिए रखो।

---

## ➡️ Next Topic
**89. CSS Pseudo-class :not()** — Sizing की functions के बाद selectors की बारी: "इसे छोड़कर बाकी सब" चुनना (जैसे `.card:not(:last-child)`)।
