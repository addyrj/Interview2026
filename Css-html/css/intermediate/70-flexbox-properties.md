# 70. Flexbox Properties (justify-content, align-items, flex-wrap)
# हिंदी में: Flexbox Properties — Container और Items के सारे Controls

---

## 🔵 Simple Definition (English)
Flexbox properties split in two groups. **Container** properties (`display:flex`, `flex-direction`, `flex-wrap`, `justify-content`, `align-items`, `align-content`, `gap`) control the layout. **Item** properties (`flex-grow`, `flex-shrink`, `flex-basis`, `flex`, `align-self`, `order`) control each child. `justify-content` works on the main axis, `align-items` on the cross axis.

## 🔵 सरल परिभाषा (Hindi)
Flexbox की properties दो हिस्सों में बँटी हैं। **Container** की properties (`display:flex`, `flex-direction`, `flex-wrap`, `justify-content`, `align-items`, `align-content`, `gap`) layout तय करती हैं। **Item** की properties (`flex-grow`, `flex-shrink`, `flex-basis`, `flex`, `align-self`, `order`) हर बच्चे को control करती हैं। `justify-content` main axis पर और `align-items` cross axis पर काम करता है।

---

## 🔴 Problem it Solves
```
PROBLEM (before flexbox): 
  - Vertical centering = hack (table-cell, position + negative margin)
  - Equal-height columns = faux columns / JS
  - Navbar: logo left, links right = float + clear + guesswork
  - Items wrap to next row with equal gaps = margin math

Flexbox properties give a single declarative knob for each need:
  justify-content: space-between   -> logo left, links right
  align-items: center              -> vertical centre
  flex-wrap: wrap + gap            -> responsive rows
  flex: 1                          -> equal columns
```

## 🔴 यह क्यों बना? (Hindi)
Flexbox से पहले alignment के लिए float, table और position के hacks चलते थे। अब हर काम की एक property है: बराबर जगह (`justify-content`), vertical centre (`align-items`), अगली line में जाना (`flex-wrap`), बाकी जगह भरना (`flex-grow`)। Interview में यही properties बार-बार पूछी जाती हैं।

---

## 🟢 How it Works — Step by Step

```
AXES (depend on flex-direction):
  row (default):    main axis = horizontal ->   cross axis = vertical  |
  column:           main axis = vertical   |   cross axis = horizontal ->

CONTAINER PROPERTIES
┌────────────────┬───────────────────────────────────────────────────────┐
│ flex-direction │ row | row-reverse | column | column-reverse           │
│ flex-wrap      │ nowrap (default) | wrap | wrap-reverse                │
│ flex-flow      │ shorthand: <direction> <wrap>  e.g. row wrap          │
│ justify-content│ MAIN axis: flex-start | center | flex-end |           │
│                │ space-between | space-around | space-evenly           │
│ align-items    │ CROSS axis (one line): stretch(default) | flex-start |│
│                │ center | flex-end | baseline                          │
│ align-content  │ CROSS axis spacing of MULTIPLE lines (needs wrap and  │
│                │ extra height): same values as justify-content + stretch│
│ gap            │ row-gap / column-gap between items (no margin hacks)  │
└────────────────┴───────────────────────────────────────────────────────┘

justify-content visual (3 items, row):
  flex-start    |[A][B][C]            |
  center        |      [A][B][C]      |
  flex-end      |            [A][B][C]|
  space-between |[A]      [B]      [C]|   (no outer space)
  space-around  | [A]    [B]    [C]   |   (half space at edges)
  space-evenly  |  [A]   [B]   [C]    |   (equal everywhere)

ITEM PROPERTIES
  flex-grow   : share of leftover space (default 0)
  flex-shrink : how much it shrinks when too tight (default 1)
  flex-basis  : starting size before grow/shrink (default auto)
  flex        : shorthand grow shrink basis
        flex: 1      = 1 1 0%      (equal share)
        flex: auto   = 1 1 auto
        flex: none   = 0 0 auto    (rigid)
        flex: 0 0 200px            (fixed 200px, never shrinks)
  align-self  : override align-items for one item
  order       : visual order (default 0); does NOT change tab/reading order
  margin: auto on an item absorbs free space (margin-left:auto pushes right)

HOW SPACE IS DISTRIBUTED:
  1. Browser computes each item's flex-basis (or width).
  2. Sum > container -> shrink by flex-shrink; Sum < container -> grow by flex-grow.
  3. Then justify-content positions any remaining free space.
  4. align-items places items across the cross axis.

KNOWN TRAPS:
  - Items won't shrink below their content: add min-width: 0 for text/ellipsis.
  - Default nowrap: items shrink instead of wrapping. Add flex-wrap: wrap.
  - align-content does nothing on a single line.
```

## 🟢 कैसे काम करता है? (Hindi)
1. पहले axes समझो: `row` में main axis आड़ी (horizontal) और cross axis खड़ी (vertical)। `column` में उल्टा।
2. `justify-content` = main axis पर बची जगह बाँटता है: `space-between` (किनारों पर चिपके, बीच में जगह), `center`, `space-evenly` (हर जगह बराबर)।
3. `align-items` = cross axis पर रखना: `center` से vertical centre (row में)।
4. `flex-wrap: wrap` से जगह कम पड़ने पर items अगली line में जाते हैं। `gap` से बीच में जगह बिना margin के।
5. `align-content` तभी काम करता है जब कई lines हों और container की extra height हो।
6. Item पर `flex: 1` = बाकी जगह बराबर बाँटो। `flex: 0 0 200px` = ठीक 200px, न बढ़े न घटे। `margin-left: auto` item को दाएँ धकेल देता है।
7. `order` सिर्फ दिखने का क्रम बदलता है, keyboard/screen reader क्रम नहीं।

---

## 🟡 Real World Example
**Swiggy / Zomato navbar:** logo on the left, search in the middle (`flex: 1`), cart/login on the right: `display:flex; align-items:center; justify-content:space-between`. **Amazon category tiles / Instagram highlights:** `flex-wrap: wrap; gap: 16px`. **Gmail compose footer:** Send button on the left, icons in the middle, trash on the right using `margin-left: auto`. **Product card:** `flex-direction: column` with the price row pinned to the bottom using `margin-top: auto`, so all cards in a row look aligned.

## 🟡 Real Example Hindi mein
**Swiggy / Zomato** के navbar में logo बाएँ, search बीच में (`flex: 1`), cart/login दाएँ: `display:flex; align-items:center; justify-content:space-between`। **Amazon** के category tiles `flex-wrap: wrap; gap: 16px` से लगते हैं। **Gmail** compose के नीचे Send बाएँ और trash दाएँ `margin-left: auto` से। Product card में `flex-direction: column` और price वाली row `margin-top: auto` से सबसे नीचे चिपकती है, इसलिए सारे cards बराबर दिखते हैं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Flexbox Properties Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; padding: 20px; background: #f5f5f5; margin: 0; }
    h2 { font-size: 15px; margin: 22px 0 6px; }

    /* Reusable demo container */
    .demo {
      display: flex;                 /* turns children into flex items */
      background: #e3f2fd;
      border: 2px dashed #1976d2;
      min-height: 90px;
      gap: 8px;
    }
    .demo > div { background: #1976d2; color: #fff; padding: 10px 16px; }

    /* justify-content (main axis) */
    .j-between { justify-content: space-between; }
    .j-center  { justify-content: center; }
    .j-evenly  { justify-content: space-evenly; }

    /* align-items (cross axis): container is 90px tall */
    .a-center { align-items: center; }
    .a-end    { align-items: flex-end; }

    /* flex-wrap with gap: items go to next row when out of space */
    .wrap { flex-wrap: wrap; }
    .wrap > div { width: 140px; }

    /* flex: 1 equal columns, item with flex-basis */
    .cols > div { flex: 1; }                 /* equal share */
    .cols > .fixed { flex: 0 0 120px; }      /* rigid 120px */

    /* align-self + order + margin-left:auto */
    .special > .self  { align-self: flex-end; }
    .special > .first { order: -1; }          /* visually first */
    .special > .push  { margin-left: auto; }  /* pushes to the far right */

    /* REAL NAVBAR */
    .navbar {
      display: flex;
      align-items: center;                 /* vertical centre */
      gap: 16px;
      padding: 10px 16px;
      background: #232f3e;
      color: #fff;
    }
    .navbar .logo { font-weight: bold; font-size: 20px; }
    .navbar input { flex: 1; padding: 8px; border: 0; border-radius: 4px; min-width: 0; }
    .navbar a { color: #fff; text-decoration: none; }

    /* CARD ROW: equal height cards with footer pinned to bottom */
    .cards { display: flex; gap: 12px; align-items: stretch; flex-wrap: wrap; }
    .card {
      flex: 1 1 180px;                     /* grow, shrink, base 180px */
      display: flex;
      flex-direction: column;              /* inner layout is a column */
      background: #fff; border: 1px solid #ddd; padding: 12px; border-radius: 8px;
    }
    .card .price { margin-top: auto; font-weight: bold; color: #b12704; } /* pinned bottom */
  </style>
</head>
<body>
  <h2>justify-content: space-between</h2>
  <div class="demo j-between"><div>A</div><div>B</div><div>C</div></div>

  <h2>justify-content: center</h2>
  <div class="demo j-center"><div>A</div><div>B</div><div>C</div></div>

  <h2>justify-content: space-evenly</h2>
  <div class="demo j-evenly"><div>A</div><div>B</div><div>C</div></div>

  <h2>align-items: center / flex-end</h2>
  <div class="demo a-center"><div>A</div><div>B</div></div>
  <div class="demo a-end"><div>A</div><div>B</div></div>

  <h2>flex-wrap: wrap + gap</h2>
  <div class="demo wrap">
    <div>1</div><div>2</div><div>3</div><div>4</div><div>5</div><div>6</div><div>7</div><div>8</div>
  </div>

  <h2>flex: 1 columns with one fixed 120px</h2>
  <div class="demo cols"><div>flex:1</div><div class="fixed">fixed</div><div>flex:1</div></div>

  <h2>align-self, order, margin-left:auto</h2>
  <div class="demo special">
    <div>One</div><div class="self">align-self:end</div><div class="first">order:-1</div><div class="push">auto margin</div>
  </div>

  <h2>Real navbar</h2>
  <nav class="navbar">
    <span class="logo">Swiggy</span>
    <input type="search" placeholder="Search for restaurants">
    <a href="#">Cart</a><a href="#">Login</a>
  </nav>

  <h2>Cards with bottom-pinned price</h2>
  <div class="cards">
    <div class="card"><h3>Burger</h3><p>Short text.</p><span class="price">Rs. 149</span></div>
    <div class="card"><h3>Pizza</h3><p>A much longer description that makes this card taller than the others in the row.</p><span class="price">Rs. 299</span></div>
    <div class="card"><h3>Momos</h3><p>Medium text here.</p><span class="price">Rs. 99</span></div>
  </div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Tailwind maps directly to flex properties
<nav className="flex items-center justify-between gap-4 px-4 py-2">
  <span className="font-bold">Logo</span>
  <input className="min-w-0 flex-1 rounded border px-2" />
  <div className="flex gap-3"><a>Cart</a><a>Login</a></div>
</nav>

// 2. Responsive direction: column on mobile, row from md up
<div className="flex flex-col gap-4 md:flex-row">
  <aside className="md:w-64 md:shrink-0">Sidebar</aside>
  <main className="flex-1">Content</main>
</div>

// 3. Wrap + gap for tags / chips
<div className="flex flex-wrap gap-2">
  {tags.map(t => <span key={t} className="rounded-full border px-3 py-1">{t}</span>)}
</div>

// 4. Card with pinned footer
<div className="flex h-full flex-col">
  <p>Description</p>
  <button className="mt-auto">Add to cart</button>
</div>

// 5. Inline style object (camelCase)
<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }} />

// Tailwind cheat: justify-start|center|end|between|around|evenly,
// items-start|center|end|stretch|baseline, flex-wrap, flex-1, grow, shrink-0, basis-1/3, self-end, order-first
```

---

## ⚫ Interview Questions + Answers

**Q1: Difference between `justify-content` and `align-items`?**
A1: `justify-content` distributes items along the main axis (horizontal in a row, vertical in a column). `align-items` aligns items along the cross axis, within each line. When `flex-direction` changes, their visual roles swap.

**Q2: What does `flex: 1` mean?**
A2: It is shorthand for `flex-grow: 1; flex-shrink: 1; flex-basis: 0%`. All items with `flex: 1` share the free space equally, regardless of content width. Items with `flex: 1` and a different one with `flex: 2` get a 1:2 split.

**Q3: `align-items` vs `align-content`?**
A3: `align-items` aligns items inside each flex line. `align-content` distributes the lines themselves along the cross axis, and only has effect when there are multiple lines (`flex-wrap: wrap`) and spare cross-axis space.

**Q4: Why do my flex items not wrap?**
A4: The default is `flex-wrap: nowrap`, so items shrink to fit. Set `flex-wrap: wrap` (and give items a `flex-basis` or width) to let them flow onto new lines. Add `gap` for spacing.

**Q5: Why does long text overflow its flex child instead of truncating?**
A5: A flex item has `min-width: auto`, so it cannot shrink below its content size. Set `min-width: 0` (or `overflow: hidden`) on the item to allow shrinking, then add `text-overflow: ellipsis`.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Putting item properties on the container (or vice versa)
```css
/* WRONG: flex-grow on the container does nothing */
.container { display: flex; flex-grow: 1; }
```
✅ **Correct way:**
```css
.container { display: flex; }
.item { flex-grow: 1; }      /* item property goes on the child */
```

❌ **Mistake 2:** Using margins for spacing between flex items
```css
.item { margin-right: 16px; }   /* last item has extra space */
```
✅ **Correct way:** `.container { display: flex; gap: 16px; }`

❌ **Mistake 3:** Expecting `align-items: center` to centre vertically in a short container
```css
/* WRONG: container height is just the content height, so nothing visibly moves */
.container { display: flex; align-items: center; }
```
✅ **Correct way:** give the container a height (`min-height: 100vh` or a fixed height) so there is free cross-axis space.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Main axis | Direction items flow | Items चलने की दिशा |
| Cross axis | Perpendicular to main axis | Main के लंबवत दिशा |
| justify-content | Main-axis distribution | Main axis पर बँटवारा |
| align-items | Cross-axis alignment | Cross axis पर alignment |
| align-content | Spacing of multiple lines | कई lines का बँटवारा |
| flex-wrap | Allow items to wrap | अगली line में जाने देना |
| flex-basis | Starting size of an item | Item का शुरुआती size |
| gap | Space between items | Items के बीच जगह |

---

## ⚡ 3-Line Summary
**English:**
1. `justify-content` works on the main axis, `align-items` on the cross axis; `flex-direction` swaps them.
2. Use `flex-wrap` + `gap` for rows that wrap, `flex: 1` for equal columns, `margin: auto` to push items apart.
3. Items need `min-width: 0` to shrink below their content and `align-content` only matters with multiple lines.

**Hindi:**
1. `justify-content` main axis पर, `align-items` cross axis पर; `flex-direction` से दोनों की भूमिका बदल जाती है।
2. Wrap होने वाली rows के लिए `flex-wrap` + `gap`, बराबर columns के लिए `flex: 1`, items अलग करने के लिए `margin: auto`।
3. Content से छोटा होने के लिए `min-width: 0` चाहिए और `align-content` सिर्फ कई lines में काम करता है।

---

## ➡️ Next Topic
**71. CSS Grid — Complete Guide**, फिर **72. Grid Properties**। Flexbox एक दिशा में layout देता है, Grid दो दिशाओं (rows + columns) में।
