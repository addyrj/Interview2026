# 71. CSS Grid — Complete Guide
# हिंदी में: CSS Grid — 2D Layout का Master

---

## 🔵 Simple Definition (English)
**CSS Grid** is a 2-dimensional layout system that lets you control both rows AND columns simultaneously. Set `display: grid` on the parent, define column/row sizes with `grid-template-columns` and `grid-template-rows`, and place items anywhere on the grid. Grid is perfect for page layouts, image galleries, and any design that needs precise 2D control.

## 🔵 सरल परिभाषा (Hindi)
**CSS Grid** एक 2-dimensional layout system है जो rows AND columns दोनों simultaneously control करता है। Parent पर `display: grid` set करो, `grid-template-columns` से columns define करो, items कहीं भी place कर सकते हो। Page layouts, image galleries और 2D control के लिए perfect।

---

## 🔴 Problem it Solves
```
BEFORE CSS GRID:
  /* Making a 3-column layout: */
  .col { float: left; width: 33.33%; }  /* float hell! */
  .clearfix::after { content: ''; display: table; clear: both; }
  
  /* Items can't span multiple columns/rows easily */
  /* Can't place items in specific grid areas */
  /* Complex layouts needed JavaScript */
  /* Responsive layouts: very painful */

WITH CSS GRID:
  .grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);  /* 3 equal columns */
    gap: 20px;
  }
  /* Done! Responsive, equal columns, no floats */
  
  /* Item spanning 2 columns: */
  .featured { grid-column: span 2; }
  
  /* Named template areas (like a magazine layout): */
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
```

---

## 🟢 How it Works

```
CSS GRID MODEL:
──────────────────────────────────────────────────────────

  GRID CONTAINER (parent with display: grid)
  ┌──────────────────────────────────────────────────────┐
  │     col 1      col 2      col 3                      │
  │  ┌──────────┬──────────┬──────────┐  ← row 1        │
  │  │  Item 1  │  Item 2  │  Item 3  │                  │
  │  ├──────────┼──────────┼──────────┤  ← row 2        │
  │  │  Item 4  │  Item 5  │  Item 6  │                  │
  │  └──────────┴──────────┴──────────┘                  │
  │                                                       │
  │  Grid lines: 1, 2, 3, 4 (columns: n+1 lines)        │
  └──────────────────────────────────────────────────────┘

CONTAINER PROPERTIES:
  display: grid
  grid-template-columns: 200px 1fr 1fr   → 3 columns
  grid-template-rows: 100px auto 60px    → 3 rows
  grid-template-areas: "h h" "s m" "f f" → named areas
  gap: 20px                              → space between
  grid-auto-flow: row | column           → auto placement

THE 'fr' UNIT:
  fr = fractional unit (remaining space fraction)
  grid-template-columns: 1fr 2fr 1fr
  → Column 2 gets TWICE the space of col 1 and col 3
  
  grid-template-columns: repeat(3, 1fr)
  → Same as: 1fr 1fr 1fr (3 equal columns)
  
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr))
  → As many 250px columns as fit, expand to fill

ITEM PROPERTIES:
  grid-column: 1 / 3       → span from line 1 to 3 (2 cols)
  grid-column: span 2      → span 2 columns
  grid-row: 1 / 3          → span 2 rows
  grid-area: header        → use named area
  justify-self             → align item horizontally in cell
  align-self               → align item vertically in cell
```

---

## 🟡 Real World Example
**Amazon India product page layout:** Header (full width), sidebar (filter panel, fixed width), main product grid (responsive, fills remaining), footer (full width). CSS Grid `grid-template-areas` handles this perfectly — one declaration, named areas, no float hacks. The product grid inside uses `repeat(auto-fill, minmax(220px, 1fr))` — automatically shows as many cards as fit, responsive without media queries.

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CSS Grid Complete Guide</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: sans-serif; padding: 20px; background: #f5f5f5; }
    h2 { margin: 24px 0 10px; color: #333; }

    /* ─── 1. BASIC GRID ──────────────────────────────────────────── */
    .basic-grid {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;  /* 3 equal columns */
      gap: 10px;                            /* gap between all */
      background: #e3f2fd;
      padding: 10px;
    }
    .basic-grid .item {
      background: #1565c0;
      color: white;
      padding: 20px;
      text-align: center;
      border-radius: 4px;
    }

    /* ─── 2. repeat() + fr unit ──────────────────────────────────── */
    .fr-grid {
      display: grid;
      grid-template-columns: 1fr 2fr 1fr;  /* middle is twice as wide */
      gap: 10px;
      background: #e8f5e9;
      padding: 10px;
    }
    .fr-grid .item {
      background: #2e7d32;
      color: white;
      padding: 15px;
      text-align: center;
      border-radius: 4px;
    }

    /* ─── 3. SPANNING COLUMNS/ROWS ───────────────────────────────── */
    .span-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      background: #fce4ec;
      padding: 10px;
    }
    .span-grid .item {
      background: #c62828;
      color: white;
      padding: 15px;
      text-align: center;
      border-radius: 4px;
    }
    .span-grid .featured {
      grid-column: span 2;   /* takes 2 columns */
      background: #b71c1c;
    }
    .span-grid .tall {
      grid-row: span 2;      /* takes 2 rows */
    }

    /* ─── 4. NAMED AREAS (Page Layout) ──────────────────────────── */
    .page-layout {
      display: grid;
      grid-template-columns: 220px 1fr;
      grid-template-rows: 56px 1fr 48px;
      grid-template-areas:
        "header  header"     /* header spans both columns */
        "sidebar main"       /* sidebar left, main right */
        "footer  footer";    /* footer spans both columns */
      gap: 0;
      height: 300px;
      border: 2px solid #ddd;
      border-radius: 8px;
      overflow: hidden;
    }
    .page-layout .header  { grid-area: header;  background: #ff5722; color: white; display: flex; align-items: center; padding: 0 20px; font-weight: bold; }
    .page-layout .sidebar { grid-area: sidebar; background: #37474f; color: white; padding: 15px; }
    .page-layout .main    { grid-area: main;    background: white;   padding: 20px; }
    .page-layout .footer  { grid-area: footer;  background: #212121; color: #aaa;   display: flex; align-items: center; padding: 0 20px; font-size: 13px; }

    /* ─── 5. AUTO-FILL + MINMAX (Responsive!) ───────────────────── */
    .responsive-grid {
      display: grid;
      /* Create as many 200px columns as fit, stretch to fill */
      grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
      gap: 12px;
      background: #f3e5f5;
      padding: 10px;
    }
    .responsive-grid .card {
      background: #6a1b9a;
      color: white;
      padding: 20px;
      text-align: center;
      border-radius: 8px;
      aspect-ratio: 1;  /* square cards */
      display: flex;
      align-items: center;
      justify-content: center;
    }

    /* ─── 6. IMAGE GALLERY ───────────────────────────────────────── */
    .gallery {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      grid-auto-rows: 120px;
      gap: 8px;
    }
    .gallery .photo {
      background: #455a64;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 12px;
    }
    .gallery .photo:nth-child(1) { grid-column: span 2; grid-row: span 2; background: #1a237e; }
    .gallery .photo:nth-child(4) { grid-column: span 2; background: #1b5e20; }
  </style>
</head>
<body>

  <h2>1. Basic Grid — 3 Equal Columns</h2>
  <div class="basic-grid">
    <div class="item">1</div>
    <div class="item">2</div>
    <div class="item">3</div>
    <div class="item">4</div>
    <div class="item">5</div>
    <div class="item">6</div>
  </div>

  <h2>2. fr Unit — 1fr 2fr 1fr</h2>
  <div class="fr-grid">
    <div class="item">1fr</div>
    <div class="item">2fr (double width)</div>
    <div class="item">1fr</div>
  </div>

  <h2>3. Spanning Columns + Rows</h2>
  <div class="span-grid">
    <div class="item featured">Featured (spans 2 cols)</div>
    <div class="item tall">Tall (spans 2 rows)</div>
    <div class="item">Item 3</div>
    <div class="item">Item 4</div>
    <div class="item">Item 5</div>
  </div>

  <h2>4. Named Grid Areas — Page Layout ⭐</h2>
  <div class="page-layout">
    <header class="header">🍕 FoodApp Header</header>
    <aside class="sidebar">📌 Sidebar<br><br>• Filters<br>• Categories</aside>
    <main class="main">📄 Main Content — Products / Articles</main>
    <footer class="footer">© 2024 FoodApp. All rights reserved.</footer>
  </div>

  <h2>5. Auto-fill + minmax (Responsive Without Media Query!)</h2>
  <div class="responsive-grid">
    <div class="card">Card 1</div>
    <div class="card">Card 2</div>
    <div class="card">Card 3</div>
    <div class="card">Card 4</div>
    <div class="card">Card 5</div>
    <div class="card">Card 6</div>
  </div>

  <h2>6. Image Gallery with Spanning</h2>
  <div class="gallery">
    <div class="photo">Big (2×2)</div>
    <div class="photo">Photo 2</div>
    <div class="photo">Photo 3</div>
    <div class="photo">Wide (2×1)</div>
    <div class="photo">Photo 5</div>
    <div class="photo">Photo 6</div>
    <div class="photo">Photo 7</div>
  </div>

</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// CSS Grid in React with Tailwind:

// Page layout with named areas:
<div className="grid grid-cols-[220px_1fr] grid-rows-[56px_1fr_48px] h-screen">
  <header className="col-span-2 bg-orange-600 flex items-center px-5 text-white">
    Header
  </header>
  <aside className="bg-gray-700 text-white p-4">Sidebar</aside>
  <main className="p-5">Main content</main>
  <footer className="col-span-2 bg-gray-900 text-gray-400 px-5 flex items-center">
    Footer
  </footer>
</div>

// Responsive product grid:
<div className="grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-4 p-4">
  {products.map(product => (
    <div key={product.id} className="bg-white rounded-lg shadow p-4">
      <img src={product.image} className="w-full h-40 object-cover rounded" />
      <h3>{product.name}</h3>
      <p className="text-green-600 font-bold">₹{product.price}</p>
    </div>
  ))}
</div>

// Standard responsive breakpoints with grid:
<div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>

// Inline CSS for grid areas (Next.js):
const layoutStyle = {
  display: 'grid',
  gridTemplateColumns: '240px 1fr',
  gridTemplateAreas: `"sidebar main"`,
  minHeight: '100vh',
};
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between CSS Grid and Flexbox?**
A1: **Flexbox is 1-dimensional** — it lays items in one direction (row OR column). Best for: navbars, centering, lists of items. **Grid is 2-dimensional** — it controls rows AND columns simultaneously. Best for: page layouts, image galleries, complex 2D designs. They can be used together: Grid for the page layout, Flexbox inside grid cells for component layouts.

**Q2: What is the `fr` unit in CSS Grid?**
A2: `fr` (fractional unit) represents a fraction of the available space in the grid container. `grid-template-columns: 1fr 2fr 1fr` — total 4 parts; column 1 gets 1/4, column 2 gets 2/4 (double), column 3 gets 1/4. Unlike percentages, `fr` accounts for gap spacing automatically. `repeat(3, 1fr)` is shorthand for `1fr 1fr 1fr`.

**Q3: What does `repeat(auto-fill, minmax(200px, 1fr))` do?**
A3: Creates as many columns as fit in the container where each column is at least 200px wide. If the container is 800px: 4 columns of 200px. If 650px: 3 columns (each ~217px due to `1fr` stretching). This creates a responsive grid WITHOUT any media queries — as the viewport shrinks, columns automatically reduce. `auto-fill` creates empty columns if items don't fill; `auto-fit` collapses empty columns.

**Q4: How do you place a grid item in a specific position?**
A4: Use `grid-column` and `grid-row` with line numbers or `span`: `grid-column: 1 / 3` = starts at line 1, ends at line 3 (spans 2 columns). `grid-column: span 2` = spans 2 columns from current position. `grid-area: header` = places in named area (defined in `grid-template-areas` on container). Negative line numbers (-1) count from the end.

**Q5: What is `grid-template-areas` and how do you use it?**
A5: Named areas define a visual map of your layout using strings. Each row is a string, areas with the same name merge into one. A `.` means empty cell. Example:
```css
grid-template-areas:
  "header header header"  /* 3 columns wide */
  "sidebar main main"     /* sidebar = 1 col, main = 2 cols */
  "footer footer footer";
```
Items reference areas with `grid-area: header`. Makes layouts readable and easy to redesign by changing the template strings.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Using Grid when Flexbox would be simpler
```css
/* WRONG: Grid for a simple horizontal list */
.nav { display: grid; grid-template-columns: repeat(5, auto); }

/* CORRECT: Flexbox for 1D layouts */
.nav { display: flex; gap: 20px; }
```

❌ **Mistake 2:** Forgetting `box-sizing: border-box` with grid
```css
/* WRONG: padding causes items to overflow grid */
.item { width: 100%; padding: 20px; }  /* total = 100% + 40px → overflow */

/* CORRECT: Always use border-box */
*, *::before, *::after { box-sizing: border-box; }
```

❌ **Mistake 3:** Using pixel values for responsive grids instead of `minmax`
```css
/* WRONG: breaks on small screens */
.grid { grid-template-columns: 250px 250px 250px 250px; }

/* CORRECT: responsive without media queries */
.grid { grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Grid Container | Parent with `display: grid` | Grid का parent |
| Grid Item | Direct child of container | Container का direct child |
| Grid Line | Dividing lines of grid | Grid को divide करने वाली lines |
| fr unit | Fraction of available space | Available space का fraction |
| grid-template-areas | Named layout areas | Named layout areas |
| grid-column: span 2 | Item spans 2 columns | Item 2 columns लेता है |
| auto-fill | Fill row with as many as fit | जितने fit हों उतने columns |
| minmax(200px, 1fr) | Min 200px, max fill | Min 200px, max भरो |
| gap | Space between grid items | Grid items के बीच space |

---

## ⚡ 3-Line Summary
**English:**
1. CSS Grid = `display: grid` on parent → 2D layout with `grid-template-columns` (column sizes) and `grid-template-rows` — use `fr` unit for flexible sizing.
2. `grid-template-areas` creates named regions (header/sidebar/main/footer) that you reference with `grid-area: header` — makes layouts readable.
3. `repeat(auto-fill, minmax(200px, 1fr))` creates a responsive grid without media queries — most powerful responsive layout technique.

**Hindi:**
1. CSS Grid = parent पर `display: grid` → 2D layout, `fr` unit से flexible sizing।
2. `grid-template-areas` named regions बनाता है — visual layout map, readable code।
3. `repeat(auto-fill, minmax(200px, 1fr))` = responsive grid बिना media queries के।

---

## ➡️ Next Topic
**72. Grid Properties Deep Dive** — grid-auto-flow, dense packing, subgrid, alignment।
