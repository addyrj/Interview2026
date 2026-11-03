# 72. Grid Properties (template-columns, rows, gap, areas)
# हिंदी में: Grid Properties — Rows, Columns, Gap और Areas

---

## 🔵 Simple Definition (English)
CSS Grid properties define a two-dimensional layout. On the container you set `grid-template-columns`, `grid-template-rows`, `gap` and `grid-template-areas`. On items you place them with `grid-column`, `grid-row` or `grid-area`. The `fr` unit shares free space, and `repeat()`, `minmax()`, `auto-fit` make layouts responsive.

## 🔵 सरल परिभाषा (Hindi)
CSS Grid की properties दो-dimension (rows + columns) layout बनाती हैं। Container पर `grid-template-columns`, `grid-template-rows`, `gap` और `grid-template-areas` लिखते हैं। Items को `grid-column`, `grid-row` या `grid-area` से रखते हैं। `fr` unit बची जगह बाँटता है और `repeat()`, `minmax()`, `auto-fit` से layout responsive बनता है।

---

## 🔴 Problem it Solves
```
PROBLEM:
  - Product grid: 4 columns on desktop, 2 on tablet, 1 on mobile
    -> Flexbox me last row ke items stretch ho jate hain / widths ka math.
  - Page layout: header, sidebar, main, footer -> nested divs + floats.
  - Items ko row AUR column dono me align karna (flexbox sirf ek axis).

GRID:
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  -> Ek line me responsive grid, bina media query ke.
```

## 🔴 यह क्यों बना? (Hindi)
Flexbox एक समय में सिर्फ एक दिशा सँभालता है। पूरे page का layout या rows और columns दोनों में बँधा product grid बनाने के लिए एक असली 2D system चाहिए था। Grid में आप layout को नाम (areas) देकर ASCII-art की तरह लिख सकते हैं।

---

## 🟢 How it Works — Step by Step

```
CONTAINER PROPERTIES
  display: grid | inline-grid
  grid-template-columns: 200px 1fr 1fr;        /* 3 columns */
  grid-template-rows: auto 1fr auto;           /* header, content, footer */
  gap: 16px;   (row-gap column-gap: gap: 16px 24px)
  grid-template-areas:
       "header header"
       "sidebar main"
       "footer footer";
  grid-auto-flow: row | column | dense          (how auto-placement fills)
  grid-auto-rows: minmax(100px, auto);          (size of implicit rows)
  grid-auto-columns
  justify-items / align-items : align items INSIDE their cell (start|center|end|stretch)
  place-items: center                            (shorthand: align + justify)
  justify-content / align-content : align the WHOLE grid in the container
  place-content

ITEM PROPERTIES
  grid-column: 1 / 3;        start line / end line  (span 2 columns)
  grid-column: span 2;
  grid-row: 1 / 3;
  grid-area: header;         (name from grid-template-areas)
  justify-self / align-self / place-self

LINES, NOT TRACKS: a 3-column grid has 4 column lines numbered 1..4
  (negative numbers count from the end: -1 is the last line)
  grid-column: 1 / -1  -> spans ALL columns.

SIZING TOOLS
  fr          : fraction of free space.  1fr 2fr = 1:2 split of leftover.
  repeat(3, 1fr)                  : 3 equal columns
  minmax(200px, 1fr)              : at least 200px, grows up to 1fr
  auto-fill vs auto-fit:
     repeat(auto-fill, minmax(200px, 1fr))  keeps EMPTY tracks (items don't stretch)
     repeat(auto-fit,  minmax(200px, 1fr))  collapses empty tracks (items stretch)
  min-content / max-content / fit-content(300px)
  1fr is minmax(auto, 1fr): long content can blow it out -> use minmax(0, 1fr).

TEMPLATE AREAS LAYOUT (visual):
   ┌─────────────────────────────┐
   │ header                       │
   ├──────────┬──────────────────┤
   │ sidebar  │ main             │
   ├──────────┴──────────────────┤
   │ footer                       │
   └─────────────────────────────┘

RESPONSIVE: change grid-template-areas / columns inside a media query:
   @media (max-width: 700px) { areas: "header" "main" "sidebar" "footer"; columns: 1fr }

EXPLICIT vs IMPLICIT grid: tracks you define are explicit. Extra items create
implicit rows sized by grid-auto-rows.
```

## 🟢 कैसे काम करता है? (Hindi)
1. `display: grid` लगाओ, फिर `grid-template-columns` से columns और `grid-template-rows` से rows बताओ।
2. `fr` = बची हुई जगह का हिस्सा। `1fr 2fr` में दूसरा column दुगना चौड़ा।
3. `repeat(3, 1fr)` = तीन बराबर columns। `minmax(200px, 1fr)` = कम से कम 200px, ज़्यादा से ज़्यादा 1fr।
4. `repeat(auto-fit, minmax(220px, 1fr))` = जितने 220px के columns समाएँ उतने बनाओ, यानी बिना media query का responsive grid। `auto-fit` खाली columns को हटाकर items को खींच देता है, `auto-fill` खाली columns रखता है।
5. `gap` से rows/columns के बीच जगह (margin की ज़रूरत नहीं)।
6. `grid-template-areas` में layout को नाम देकर चित्र की तरह लिखो और item पर `grid-area: header` लगाओ।
7. Grid lines गिनी जाती हैं, tracks नहीं: 3 columns = 4 lines। `grid-column: 1 / -1` = सारे columns में फैलना।
8. `place-items: center` हर cell के अंदर item को बीच में रखता है।

---

## 🟡 Real World Example
**Amazon / Flipkart product listing:** `repeat(auto-fit, minmax(220px, 1fr))` makes a card grid that adapts from 1 to 6 columns. **Instagram profile:** a perfect 3-column photo grid with `gap: 4px` and square cells (`aspect-ratio: 1`). **Gmail / admin dashboards:** `grid-template-areas` for header, sidebar, main and footer. **Zomato home:** "Eat what makes you happy" tiles in a 2-row grid; a featured tile spans two columns with `grid-column: span 2`.

## 🟡 Real Example Hindi mein
**Amazon / Flipkart** की product listing `repeat(auto-fit, minmax(220px, 1fr))` से 1 से 6 columns तक अपने आप बदलती है। **Instagram profile** में 3-column photo grid `gap: 4px` और square cells (`aspect-ratio: 1`) से बनी है। **Gmail / dashboards** में header, sidebar, main और footer `grid-template-areas` से बनते हैं। **Zomato** home में एक featured tile `grid-column: span 2` से दो columns में फैलता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Grid Properties Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
    h2 { font-size: 15px; margin: 24px 0 8px; }
    .cell { background: #1976d2; color: #fff; padding: 14px; text-align: center; border-radius: 4px; }

    /* 1. Fixed + flexible columns, gap */
    .g1 {
      display: grid;
      grid-template-columns: 120px 1fr 2fr;   /* fixed, 1 part, 2 parts */
      gap: 12px;                              /* row and column gap */
      background: #e3f2fd; padding: 12px;
    }

    /* 2. Responsive cards with NO media query */
    .g2 {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
    }
    .g2 .cell { background: #43a047; }

    /* 3. Spanning items and explicit placement */
    .g3 {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      grid-auto-rows: 70px;                   /* implicit row height */
      gap: 8px;
    }
    .wide { grid-column: span 2; background: #e53935; }     /* 2 columns wide */
    .tall { grid-row: span 2;   background: #8e24aa; }      /* 2 rows tall */
    .full { grid-column: 1 / -1; background: #fb8c00; }     /* line 1 to last line */

    /* 4. Named areas: full page layout */
    .layout {
      display: grid;
      grid-template-columns: 180px 1fr;
      grid-template-rows: 56px 220px 48px;
      grid-template-areas:
        "header  header"
        "sidebar main"
        "footer  footer";
      gap: 8px;
      min-height: 330px;
    }
    .layout > header { grid-area: header; background: #232f3e; color: #fff; padding: 14px; }
    .layout > aside  { grid-area: sidebar; background: #ffe082; padding: 14px; }
    .layout > main   { grid-area: main; background: #fff; padding: 14px; border: 1px solid #ddd; }
    .layout > footer { grid-area: footer; background: #546e7a; color: #fff; padding: 12px; }

    /* Mobile: stack everything by redefining the areas */
    @media (max-width: 600px) {
      .layout {
        grid-template-columns: 1fr;
        grid-template-rows: auto;
        grid-template-areas: "header" "main" "sidebar" "footer";
      }
    }

    /* 5. Centering with place-items */
    .g5 { display: grid; place-items: center; height: 100px; background: #e0f2f1; }
  </style>
</head>
<body>
  <h2>1. Columns: 120px 1fr 2fr with gap</h2>
  <div class="g1"><div class="cell">120px</div><div class="cell">1fr</div><div class="cell">2fr</div></div>

  <h2>2. auto-fit + minmax (resize the window)</h2>
  <div class="g2">
    <div class="cell">1</div><div class="cell">2</div><div class="cell">3</div>
    <div class="cell">4</div><div class="cell">5</div>
  </div>

  <h2>3. span 2 columns / span 2 rows / full width</h2>
  <div class="g3">
    <div class="cell wide">span 2 cols</div>
    <div class="cell tall">span 2 rows</div>
    <div class="cell">3</div>
    <div class="cell">4</div>
    <div class="cell">5</div>
    <div class="cell full">1 / -1 (full width)</div>
  </div>

  <h2>4. grid-template-areas (shrinks to 1 column under 600px)</h2>
  <div class="layout">
    <header>Header</header>
    <aside>Sidebar</aside>
    <main>Main content</main>
    <footer>Footer</footer>
  </div>

  <h2>5. place-items: center</h2>
  <div class="g5"><div class="cell">Centered</div></div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Responsive product grid in Tailwind
<div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
  {products.map(p => <ProductCard key={p.id} {...p} />)}
</div>

// 2. Auto-fit grid with arbitrary value (no breakpoints)
<div className="grid gap-4 [grid-template-columns:repeat(auto-fit,minmax(220px,1fr))]">...</div>

// 3. Spanning
<div className="col-span-2 row-span-2">Featured tile</div>

// 4. Page layout with areas in a CSS Module (Next.js app router)
/* layout.module.css */
.shell {
  display: grid;
  grid-template-columns: 240px 1fr;
  grid-template-areas: "header header" "sidebar main";
  min-height: 100vh;
}
.header { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main { grid-area: main; min-width: 0; }   /* avoid overflow blowout */

// 5. Centering: <div className="grid min-h-screen place-items-center">Login</div>

// 6. Tailwind: grid-cols-3, col-span-2, gap-4, gap-x-2, place-items-center,
//    grid-rows-3, auto-rows-fr, [grid-template-areas] needs arbitrary values.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the `fr` unit?**
A1: A fraction of the available free space in the grid container. `grid-template-columns: 1fr 2fr` gives the second column twice the width of the first after any fixed tracks and gaps are subtracted.

**Q2: Explain `repeat(auto-fit, minmax(200px, 1fr))`.**
A2: Create as many columns as fit, each at least 200px and growing equally to fill the row. `auto-fit` collapses empty tracks so items stretch; `auto-fill` keeps empty tracks so items stay at their size. It gives a responsive card grid without media queries.

**Q3: `auto-fill` vs `auto-fit`?**
A3: They differ only when there are fewer items than could fill the row. `auto-fill` keeps the empty columns (items don't grow into them). `auto-fit` collapses them to 0, so the existing items grow to fill the row.

**Q4: What are `grid-template-areas` and how do you use them?**
A4: A way to name regions of the grid in a string-based diagram. Each string is a row, each word a column, and a repeated name spans cells (must form a rectangle). Items opt in with `grid-area: name`. Use `.` for an empty cell. You can redefine the areas in a media query to rearrange a page.

**Q5: `justify-items` vs `justify-content` in grid?**
A5: `justify-items` aligns each item inside its own cell (horizontal axis). `justify-content` aligns the whole set of tracks within the container when the grid is narrower than the container. Same pattern for `align-*` on the vertical axis.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Writing grid line numbers as track numbers
```css
/* WRONG: 3 columns has lines 1-4. "grid-column: 1 / 3" spans only 2 columns */
.item { grid-column: 1 / 3; }
```
✅ **Correct way:** `grid-column: 1 / 4` (or `1 / -1`, or `span 3`) to span all three.

❌ **Mistake 2:** `1fr` columns stretching because of long content
```css
.grid { grid-template-columns: 1fr 1fr; }  /* a long URL/pre pushes it wider */
```
✅ **Correct way:** `grid-template-columns: repeat(2, minmax(0, 1fr));` and `min-width: 0` on items.

❌ **Mistake 3:** Mismatched area names or non-rectangular areas
```css
grid-template-areas: "a b" "a a";  /* "a" is L-shaped: invalid, whole property ignored */
```
✅ **Correct way:** each name must form a solid rectangle, and every row needs the same number of cells.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| fr | Fraction of free space | बची जगह का हिस्सा |
| repeat() | Repeat a track pattern | Track pattern दोहराना |
| minmax() | Min and max track size | न्यूनतम और अधिकतम size |
| auto-fit | Collapse empty tracks | खाली tracks हटाओ |
| auto-fill | Keep empty tracks | खाली tracks रखो |
| grid-template-areas | Named layout regions | नाम वाले layout हिस्से |
| Grid line | Boundary between tracks | Tracks की सीमा रेखा |
| Implicit grid | Auto-created extra rows/cols | अपने आप बने extra tracks |

---

## ⚡ 3-Line Summary
**English:**
1. Define the grid on the container with `grid-template-columns/rows`, `gap` and `grid-template-areas`; place items with `grid-column`, `grid-row`, `grid-area`.
2. `fr`, `repeat()`, `minmax()` and `auto-fit` create flexible, responsive layouts without media queries.
3. Grid lines are numbered (n tracks = n+1 lines); use `minmax(0, 1fr)` to stop content blowing out tracks.

**Hindi:**
1. Container पर `grid-template-columns/rows`, `gap`, `grid-template-areas` लिखो और items को `grid-column`, `grid-row`, `grid-area` से रखो।
2. `fr`, `repeat()`, `minmax()` और `auto-fit` से बिना media query के responsive layout बनता है।
3. Grid lines गिनी जाती हैं (n tracks = n+1 lines); content से tracks न फैलें इसलिए `minmax(0, 1fr)` use करो।

---

## ➡️ Next Topic
**73. Flexbox vs Grid — When to Use** — दोनों में से कब कौन सा चुनें, और interview में यह तुलना कैसे समझाएँ।
