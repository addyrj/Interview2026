# 103. CSS Subgrid
# हिंदी में: CSS Subgrid — Nested Grid जो Parent की Tracks इस्तेमाल करे

---

## 🔵 Simple Definition (English)
`subgrid` lets a **nested grid reuse the rows and/or columns of its parent grid** instead of creating its own tracks. Written as `grid-template-rows: subgrid` or `grid-template-columns: subgrid`. This aligns inner parts of different cards (title, text, button) across the whole row.

## 🔵 सरल परिभाषा (Hindi)
`subgrid` से **nested grid अपने parent grid की rows और/या columns ही use करता है**, अपनी नई tracks नहीं बनाता। `grid-template-rows: subgrid` या `grid-template-columns: subgrid` लिखते हैं। इससे अलग-अलग cards के अंदर के हिस्से (title, text, button) पूरी row में एक सीध में आते हैं।

---

## 🔴 Problem it Solves
```
BEFORE (nested grid/flex):
  Card 1: short title, 2-line text, button
  Card 2: LONG title (3 lines), 1-line text, button
  -> Each card calculates its own heights. Buttons end up at
     different heights. Titles don't line up.
  Hacks: fixed min-height, JavaScript to equalize heights, margin-top:auto
         (fixes only the button, not title/text alignment).

AFTER (subgrid):
  Cards span 3 rows of the parent grid and "inherit" those 3 row tracks.
  The tallest title decides the title row for ALL cards in that row.
  Everything lines up automatically. No JS.
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले (nested grid/flex):
  Card 1: छोटा title, 2 line text, button
  Card 2: लंबा title (3 lines), 1 line text, button
  -> हर card अपनी heights खुद निकालता है। Buttons अलग ऊँचाई पर आते हैं,
     titles सीध में नहीं आते।
  Hacks: fixed min-height, JavaScript, margin-top:auto (सिर्फ button ठीक होता है)।

अब (subgrid):
  Cards parent grid की 3 rows span करते हैं और वही 3 row tracks "inherit" करते हैं।
  सबसे लंबा title पूरी row के लिए title की ऊँचाई तय करता है।
  सब अपने-आप align। JS की ज़रूरत नहीं।
```

---

## 🟢 How it Works — Step by Step

```
1. Make a parent grid:        .grid { display: grid; grid-template-columns: repeat(3, 1fr); }
2. Each card is a grid item AND spans extra rows in the parent:
                              .card { grid-row: span 3; }
3. Make the card itself a grid and borrow parent's rows:
                              .card { display: grid; grid-template-rows: subgrid; }
4. Children (h3, p, button) now sit on the parent's 3 row tracks.
5. Gaps: subgrid inherits the parent's gap by default.
   You can override with `row-gap` / `column-gap` on the subgrid.
6. Line names: parent's named lines are available in the subgrid.

RULES / CATCHES:
  - The element must itself be a grid item of a grid parent.
  - `span 3` must match the number of children (rows) you want to align.
  - Subgrid works per axis: rows, columns, or both:
        grid-template-columns: subgrid;
        grid-template-rows: subgrid;
  - Browser support: Firefox 71+, Safari 16+, Chrome/Edge 117+ (all modern browsers since late 2023).
  - Fallback: write a normal grid-template-rows first, then
    @supports (grid-template-rows: subgrid) { ... }
```

## 🟢 कैसे काम करता है? (Hindi)

```
1. Parent grid बनाओ:   .grid { display: grid; grid-template-columns: repeat(3, 1fr); }
2. हर card parent की extra rows span करता है:
                       .card { grid-row: span 3; }
3. Card को grid बनाओ और parent की rows उधार लो:
                       .card { display: grid; grid-template-rows: subgrid; }
4. Children (h3, p, button) अब parent की 3 row tracks पर बैठते हैं।
5. Gap: subgrid default में parent की gap inherit करता है; चाहो तो override कर सकते हो।
6. Parent की named lines subgrid में भी मिलती हैं।

ध्यान रखें:
  - Element खुद किसी grid parent का grid item होना चाहिए।
  - `span 3` की गिनती children की गिनती से मिलनी चाहिए।
  - Subgrid हर axis के लिए अलग काम करता है (rows, columns या दोनों)।
  - Support: Firefox 71+, Safari 16+, Chrome/Edge 117+ (अब सभी modern browsers में)।
  - Fallback: पहले normal grid-template-rows लिखो, फिर @supports में subgrid।
```

---

## 🟡 Real World Example
**Amazon / Flipkart product grids and pricing tables (like Zomato Gold plans):** Cards have different title lengths and different number of feature lines, but the "Buy now" buttons and price rows must sit on the same horizontal line across the row. Subgrid does this so each card keeps its own semantic HTML while sharing row heights with its neighbours.

## 🟡 Real Example Hindi mein
**Amazon / Flipkart product grids और pricing tables (जैसे Zomato Gold plans):** Cards में title की लंबाई और features की गिनती अलग होती है, पर "Buy now" button और price row पूरी row में एक ही horizontal line पर चाहिए। Subgrid यह करता है, और हर card की अपनी semantic HTML बनी रहती है जबकि row heights पड़ोसियों के साथ share होती हैं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CSS Subgrid Demo</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; background: #f3f4f6; margin: 0; padding: 24px; }

    /* PARENT GRID: 3 columns, auto rows */
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); /* responsive columns */
      gap: 16px;                 /* gap between cards (also inherited by subgrid rows) */
      max-width: 960px;
      margin: 0 auto;
    }

    /* Each CARD = grid item that spans 3 rows of the parent */
    .card {
      grid-row: span 3;                 /* takes 3 row tracks: title / text / button */
      display: grid;                    /* card is also a grid ... */
      grid-template-rows: subgrid;      /* ... that REUSES the parent's 3 rows */
      row-gap: 0;                       /* override inherited gap inside the card */

      background: #fff;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 16px;
    }

    .card h3 { margin: 0 0 8px; }               /* row 1: title (tallest title wins) */
    .card p  { margin: 0 0 12px; color: #555; } /* row 2: description */
    .card a {                                   /* row 3: button aligned at same height */
      align-self: end;
      text-align: center;
      background: #e47911;
      color: #fff;
      text-decoration: none;
      padding: 10px;
      border-radius: 8px;
    }

    /* FALLBACK for old browsers: card uses flex column and button goes to bottom */
    @supports not (grid-template-rows: subgrid) {
      .card { display: flex; flex-direction: column; }
      .card a { margin-top: auto; }
    }
  </style>
</head>
<body>
  <div class="grid">
    <!-- Card 1: short content -->
    <article class="card">
      <h3>Basic</h3>
      <p>One user.</p>
      <a href="#">Choose</a>
    </article>

    <!-- Card 2: long title + long text -->
    <article class="card">
      <h3>Professional Plan for Growing Teams and Agencies</h3>
      <p>Up to 10 users, priority support, analytics dashboard, custom domains and more.</p>
      <a href="#">Choose</a>
    </article>

    <!-- Card 3: medium -->
    <article class="card">
      <h3>Business</h3>
      <p>Unlimited users and SSO.</p>
      <a href="#">Choose</a>
    </article>
  </div>
</body>
</html>
```

```css
/* Column subgrid example: form labels and inputs aligned across fieldsets */
.form   { display: grid; grid-template-columns: max-content 1fr; gap: 8px 16px; }
.field  { grid-column: 1 / -1; display: grid; grid-template-columns: subgrid; }
/* Every .field uses the SAME label column width, set by the widest label */
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Component maps data to cards. The alignment is pure CSS, no JS measuring needed.
export default function Plans({ plans }) {
  return (
    <div className="plans">
      {plans.map(p => (
        <article key={p.id} className="plan">
          <h3>{p.name}</h3>
          <p>{p.desc}</p>
          <a href={p.href}>Choose</a>
        </article>
      ))}
    </div>
  );
}

/* plans.module.css */
.plans { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }
.plan  { display: grid; grid-row: span 3; grid-template-rows: subgrid; }

// 2. Tailwind v3.4+ supports subgrid utilities:
<div className="grid grid-cols-3 gap-4">
  <article className="row-span-3 grid grid-rows-subgrid">
    <h3>Title</h3><p>Text</p><a>Buy</a>
  </article>
</div>
// grid-rows-subgrid and grid-cols-subgrid are available in Tailwind 3.4+
```

---

## ⚫ Interview Questions + Answers

**Q1: What is CSS subgrid and what problem does it solve?**
A1: Subgrid lets a nested grid use its parent grid's row and/or column tracks. It solves aligning inner parts of sibling components (card titles, descriptions, buttons) across a row without fixed heights or JavaScript.

**Q2: How is subgrid different from a normal nested grid?**
A2: A normal nested grid creates independent tracks sized only by its own content, so siblings cannot influence each other. A subgrid shares tracks with the parent; the tallest/widest content in any sibling sizes the shared track for all.

**Q3: What are the requirements to use subgrid?**
A3: The element must be a grid item of a grid container AND be a grid container itself (`display: grid`), and it must span the tracks it wants to share (e.g. `grid-row: span 3`). Then set `grid-template-rows: subgrid` and/or `grid-template-columns: subgrid`.

**Q4: How does gap work in a subgrid?**
A4: By default it inherits the parent's `gap`. You can override it with `row-gap`/`column-gap` on the subgrid. Padding on the subgrid is also taken into account when sizing the shared tracks.

**Q5: Is it safe to use in production? What about fallback?**
A5: Yes. It has been available in all major browsers since late 2023 (Firefox 71, Safari 16, Chrome 117). For safety, provide a fallback inside `@supports not (grid-template-rows: subgrid)` using flex column with `margin-top: auto`.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting to span rows in the parent
```css
/* WRONG: card occupies one row; subgrid has nothing to share */
.card { display: grid; grid-template-rows: subgrid; }
/* CORRECT */
.card { grid-row: span 3; display: grid; grid-template-rows: subgrid; }
```

❌ **Mistake 2:** Using subgrid on an element that is not a grid item
```css
/* WRONG: parent is display:flex or block, subgrid is ignored */
/* CORRECT: parent must be display: grid */
```

❌ **Mistake 3:** Span count mismatch
```css
/* WRONG: span 2 but card has 3 children, extra child creates an implicit row */
/* CORRECT: span count = number of children rows */
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| subgrid | Nested grid using parent's tracks | Parent की tracks use करने वाला grid |
| track | A row or column in a grid | Grid की row या column |
| grid item | Direct child of a grid container | Grid का सीधा child |
| span | Occupy multiple tracks | कई tracks घेरना |
| implicit grid | Tracks created automatically | अपने-आप बनी tracks |
| @supports | Feature query for fallbacks | Feature check करके fallback |

---

## ⚡ 3-Line Summary
**English:**
1. `subgrid` makes a nested grid borrow the parent's rows or columns so siblings align.
2. Pattern: parent grid + `grid-row: span N` + `display: grid` + `grid-template-rows: subgrid`.
3. Supported in all modern browsers since 2023; use `@supports` for a flex fallback.

**Hindi:**
1. `subgrid` से nested grid parent की rows या columns उधार लेता है, इसलिए siblings align रहते हैं।
2. Pattern: parent grid + `grid-row: span N` + `display: grid` + `grid-template-rows: subgrid`।
3. 2023 से सभी modern browsers में support; पुराने के लिए `@supports` से flex fallback।

---

## ➡️ Next Topic
**104. Container Queries** — Grid cards अपने parent की चौड़ाई के हिसाब से बदलें, viewport के हिसाब से नहीं; यही component-level responsiveness है।
