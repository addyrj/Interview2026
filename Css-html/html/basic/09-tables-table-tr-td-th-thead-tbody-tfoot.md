# 9. Tables (table, tr, td, th, thead, tbody, tfoot)
# हिंदी में: Tables — Rows और Columns में Data दिखाना

---

## 🔵 Simple Definition (English)
An HTML `<table>` displays **tabular data** (data with rows and columns, like a spreadsheet). `<tr>` is a row, `<th>` a header cell, `<td>` a data cell; `<thead>`, `<tbody>` and `<tfoot>` group the header, body and footer rows.

## 🔵 सरल परिभाषा (Hindi)
HTML `<table>` **tabular data** (rows और columns वाला data, जैसे spreadsheet) दिखाता है। `<tr>` एक row, `<th>` header cell, `<td>` data cell है; `<thead>`, `<tbody>`, `<tfoot>` header, body और footer rows को group करते हैं।

---

## 🔴 Problem it Solves
```
PROBLEM:
  Data like an order list, price comparison or timetable has TWO dimensions.
  Using divs/spaces to line up columns breaks on different screens and tells
  screen readers nothing about which value belongs to which column.

TABLE GIVES:
  - Automatic column alignment
  - Relationship between header cell and data cell (screen reader reads
    "Price: Rs 500" for a cell, using <th>)
  - Row/column spanning (colspan, rowspan)
  - Built-in structure to sort/filter with JS

HISTORY WARNING:
  In the 1990s tables were abused for PAGE LAYOUT. That is obsolete: use CSS Flexbox/Grid
  for layout and tables ONLY for real tabular data.
```

## 🔴 यह क्यों बना? (Hindi)
```
समस्या:
  Order list, price comparison या timetable जैसे data के दो dimensions होते हैं।
  Div/spaces से columns align करना अलग screens पर टूट जाता है और screen reader को
  नहीं पता चलता कि कौन सी value किस column की है।

Table से:
  - Columns अपने आप align होते हैं
  - Header cell और data cell का रिश्ता बनता है (screen reader बोलता है "Price: Rs 500")
  - colspan, rowspan से cells merge कर सकते हैं
  - JS से sort/filter करने के लिए तैयार structure

चेतावनी:
  1990s में tables page layout के लिए इस्तेमाल होते थे। अब layout के लिए Flexbox/Grid,
  और table सिर्फ असली tabular data के लिए।
```

---

## 🟢 How it Works — Step by Step

```
TABLE ANATOMY:
──────────────────────────────────────────────────────────
<table>
  <caption>Monthly Orders</caption>        title of the table (best for a11y)
  <colgroup><col><col span="2"></colgroup> style whole columns (optional)
  <thead>                                   header section
    <tr>                                    row
      <th scope="col">Item</th>             header cell for a COLUMN
      <th scope="col">Qty</th>
    </tr>
  </thead>
  <tbody>                                   main data rows
    <tr>
      <th scope="row">Pizza</th>            header cell for a ROW
      <td>2</td>                            data cell
    </tr>
  </tbody>
  <tfoot>                                   summary/footer row (totals)
    <tr><td colspan="2">Total: 5</td></tr>
  </tfoot>
</table>

KEY ATTRIBUTES:
  colspan="2"    cell spans 2 columns
  rowspan="2"    cell spans 2 rows
  scope="col|row" tells assistive tech what the <th> labels
  headers="id1 id2" complex tables (multi-level headers)

CSS FOR TABLES:
  border-collapse: collapse;   merge double borders into one (default is separate)
  border-spacing               gap between cells (only when separate)
  table-layout: fixed          column widths from the first row (faster, predictable)
  tr:nth-child(even)           zebra striping
  overflow-x: auto on a wrapper div -> horizontal scroll on mobile
  position: sticky on thead th -> sticky header row

RULES:
  1. Tables are for DATA, never for layout
  2. Always use <th> for headers (not styled <td>) and add <caption>
  3. Browser auto-inserts <tbody> if you omit it (can surprise your CSS selectors)
  4. Keep direct children correct: table > thead/tbody/tfoot > tr > th/td
  5. Responsive: wrap in a scrollable div or restyle to stacked cards on mobile
```

## 🟢 कैसे काम करता है? (Hindi)
```
STRUCTURE:
  <table> -> <thead>/<tbody>/<tfoot> -> <tr> (row) -> <th> (header cell) या <td> (data cell)
  <caption> table का title है

IMPORTANT:
  - colspan / rowspan से cells merge होते हैं
  - scope="col" या "row" से screen reader को पता चलता है header किसका है
  - CSS: border-collapse: collapse; से double borders एक हो जाते हैं
  - Mobile पर table चौड़ी हो तो wrapper div में overflow-x: auto लगाओ
  - Table सिर्फ data के लिए, layout के लिए नहीं
```

---

## 🟡 Real World Example
**Amazon price comparison / order history:** The "Your Orders" page and the product "Compare with similar items" section are tables: columns are attributes (price, rating, brand), rows are products. In Gmail's inbox each email is effectively a table row (sender, subject, date) with column alignment. Stock websites such as Zerodha use tables for watchlists with a sticky header and zebra rows. Each `<th scope="col">` lets a screen reader announce "Price" before every price value.

## 🟡 Real Example Hindi mein
**Amazon price comparison / order history:** "Your Orders" और "Compare with similar items" असल में tables हैं: columns attributes हैं (price, rating, brand), rows products हैं। Gmail के inbox में हर email एक table row जैसा है (sender, subject, date)। Zerodha जैसी stock sites watchlist के लिए sticky header और zebra rows वाली tables इस्तेमाल करती हैं। हर `<th scope="col">` से screen reader हर price से पहले "Price" बोलता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HTML Table Demo</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; padding: 20px; background: #f7f7f7; }

    /* Wrapper makes the table scroll sideways on small screens */
    .table-wrap { overflow-x: auto; max-height: 340px; background: #fff;
                  border: 1px solid #ddd; border-radius: 8px; }

    table { border-collapse: collapse; width: 100%; min-width: 560px; }  /* single borders */
    caption { text-align: left; font-weight: bold; font-size: 18px; padding: 12px; }

    th, td { padding: 10px 14px; text-align: left; border-bottom: 1px solid #eee; }

    /* Sticky header stays visible when scrolling the wrapper */
    thead th { position: sticky; top: 0; background: #232f3e; color: #fff; }  /* Amazon navy */

    tbody tr:nth-child(even) { background: #fafafa; }       /* zebra striping */
    tbody tr:hover { background: #fff3cd; }                 /* row highlight */

    td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; } /* align digits */
    tfoot td, tfoot th { font-weight: bold; background: #f0f0f0; border-top: 2px solid #232f3e; }

    .in  { color: #2e7d32; font-weight: 600; }               /* in stock */
    .out { color: #c62828; font-weight: 600; }               /* out of stock */

    /* Second demo: colspan / rowspan */
    .span-demo { margin-top: 28px; width: auto; min-width: 0; background: #fff; }
    .span-demo th, .span-demo td { border: 1px solid #ccc; text-align: center; }
  </style>
</head>
<body>
  <h1>Product Comparison Table</h1>

  <div class="table-wrap" tabindex="0" role="region" aria-labelledby="cap">
    <table>
      <!-- caption names the table for assistive tech -->
      <caption id="cap">Headphones comparison (prices in Rs)</caption>
      <thead>
        <tr>
          <!-- scope="col": header for the column below -->
          <th scope="col">Product</th>
          <th scope="col">Brand</th>
          <th scope="col" class="num">Rating</th>
          <th scope="col" class="num">Price</th>
          <th scope="col">Stock</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <!-- scope="row": header for this row -->
          <th scope="row">Rockerz 450</th><td>boAt</td><td class="num">4.2</td><td class="num">1,499</td><td class="in">In stock</td>
        </tr>
        <tr>
          <th scope="row">WH-CH520</th><td>Sony</td><td class="num">4.4</td><td class="num">3,990</td><td class="in">In stock</td>
        </tr>
        <tr>
          <th scope="row">Buds Z2</th><td>OnePlus</td><td class="num">4.1</td><td class="num">2,299</td><td class="out">Out of stock</td>
        </tr>
        <tr>
          <th scope="row">Tune 510BT</th><td>JBL</td><td class="num">4.3</td><td class="num">2,999</td><td class="in">In stock</td>
        </tr>
        <tr>
          <th scope="row">Major IV</th><td>Marshall</td><td class="num">4.5</td><td class="num">9,999</td><td class="in">In stock</td>
        </tr>
      </tbody>
      <tfoot>
        <tr>
          <!-- colspan: label spans 3 columns -->
          <th scope="row" colspan="3">Average price</th>
          <td class="num">4,157</td><td></td>
        </tr>
      </tfoot>
    </table>
  </div>

  <h2>colspan and rowspan</h2>
  <table class="span-demo">
    <caption>Class timetable</caption>
    <thead>
      <tr><th scope="col">Time</th><th scope="col">Mon</th><th scope="col">Tue</th></tr>
    </thead>
    <tbody>
      <tr><th scope="row">9:00</th><td rowspan="2">Math (2 hrs)</td><td>Physics</td></tr>
      <tr><th scope="row">10:00</th><td>Chemistry</td></tr>          <!-- Mon cell is covered by rowspan -->
      <tr><th scope="row">11:00</th><td colspan="2">Assembly (both days)</td></tr>
    </tbody>
  </table>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Render rows with map() and stable keys; keep the full table structure.
function ProductTable({ products }) {
  return (
    <div className="overflow-x-auto rounded-lg border">
      <table className="w-full text-left border-collapse">
        <caption className="p-3 font-bold text-left">Headphones</caption>
        <thead className="bg-slate-800 text-white">
          <tr>
            <th scope="col" className="p-3">Product</th>
            <th scope="col" className="p-3 text-right">Price</th>
          </tr>
        </thead>
        <tbody>
          {products.map(p => (
            <tr key={p.id} className="even:bg-gray-50 hover:bg-yellow-50">
              <th scope="row" className="p-3 font-medium">{p.name}</th>
              <td className="p-3 text-right">Rs {p.price.toLocaleString("en-IN")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// 2. Hydration warnings: React warns on invalid nesting such as <tr> directly in <table>
//    (without tbody in some cases) or <div> inside <tr>. Keep correct structure.

// 3. Complex data grids (sorting, filtering, pagination, virtualisation):
//    use TanStack Table (headless) or AG Grid instead of hand-rolling.

// 4. Tailwind: even:bg-*, hover:bg-*, sticky top-0 on <th>, overflow-x-auto on a wrapper.
```

---

## ⚫ Interview Questions + Answers

**Q1: When should you use a table, and when not?**
A1: Use a table for **tabular data** (information with relationships across rows and columns: schedules, comparisons, reports). Do **not** use tables for page layout: that is rigid, not responsive, and confuses assistive tech. Use Flexbox/Grid for layout.

**Q2: Why use `<thead>`, `<tbody>` and `<tfoot>`?**
A2: They group rows semantically so browsers/AT understand header, body and summary; the header can repeat on each printed page, tbody can scroll independently, and CSS/JS selectors become simpler. Browsers insert an implicit `<tbody>` if missing, so selectors like `table > tr` do not match.

**Q3: Difference between `<th>` and `<td>`? What is `scope`?**
A3: `<th>` is a **header cell** (bold and centered by default, announced as a label by screen readers); `<td>` is a **data cell**. `scope="col"` or `scope="row"` states whether the header applies to the column or row below/next to it. For complex tables use `headers` + `id`.

**Q4: How do you make a table responsive?**
A4: (1) Wrap in `overflow-x: auto` container so it scrolls sideways. (2) Hide less important columns on small screens. (3) Convert rows to stacked cards using media queries (`display: block` on `tr`/`td` and `td::before { content: attr(data-label) }`). (4) Use `table-layout: fixed` and `word-break` for long text.

**Q5: What do `colspan` and `rowspan` do, and what does `border-collapse` do?**
A5: `colspan` merges a cell across columns and `rowspan` across rows; the covered cells must be omitted from the markup. `border-collapse: collapse` merges adjacent cell borders into one line; the default `separate` leaves gaps controlled by `border-spacing`.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Table for page layout
```html
<!-- WRONG --> <table><tr><td>Sidebar</td><td>Content</td></tr></table>
<!-- ✅ Correct way --> <div class="layout">  /* display: grid; grid-template-columns: 240px 1fr */
```

❌ **Mistake 2:** Using `<td>` styled bold instead of `<th>`; no caption
```html
<!-- WRONG --> <tr><td><b>Name</b></td></tr>
<!-- ✅ Correct way --> <tr><th scope="col">Name</th></tr>
```

❌ **Mistake 3:** Wrong cell counts after colspan/rowspan (misaligned columns)
```html
<!-- ✅ Count: every row must total the same number of columns, including spanned cells -->
```

❌ **Mistake 4:** Using `border="1"`, `cellpadding`, `align` attributes (obsolete)
```css
/* ✅ Correct way */
table { border-collapse: collapse; }
td { padding: 8px; border: 1px solid #ccc; }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `<table>` | Container for tabular data | Table का container |
| `<tr>` | Table row | Row |
| `<th>` | Header cell | Header cell |
| `<td>` | Data cell | Data cell |
| `<thead>/<tbody>/<tfoot>` | Header/body/footer groups | Header/body/footer के group |
| `<caption>` | Title of table | Table का शीर्षक |
| colspan / rowspan | Merge cells across columns/rows | Columns/rows में cells जोड़ना |
| scope | Header applies to col or row | Header किसके लिए है |
| border-collapse | Merge adjacent borders | Borders को जोड़ना |

---

## ⚡ 3-Line Summary
**English:**
1. Tables are for real rows-and-columns data: `table > thead/tbody/tfoot > tr > th/td`, with `caption` and `scope`.
2. Use `colspan`/`rowspan` to merge cells and CSS (`border-collapse`, zebra rows, sticky `th`) to style.
3. Never use tables for layout; make wide tables scroll with an `overflow-x: auto` wrapper.

**Hindi:**
1. Tables असली rows-columns data के लिए हैं: `table > thead/tbody/tfoot > tr > th/td`, साथ में `caption` और `scope`।
2. Cells merge करने के लिए `colspan`/`rowspan`; style के लिए CSS (`border-collapse`, zebra rows, sticky `th`)।
3. Layout के लिए table कभी नहीं; चौड़ी table को `overflow-x: auto` wrapper में scroll कराओ।

---

## ➡️ Next Topic
**10. Forms (form, input, label, button, select, textarea)** — ab user se data lene ka tareeka: forms, jinke bina login, search aur checkout nahi ban sakte।
