# 120. Responsive Table
# हिंदी में: Responsive Table बनाना

Files: [index.html](index.html) · [style.css](style.css) (open index.html directly, narrow below 600px)

---

## 🔵 Simple Definition (English)
A responsive table stays readable on small screens. There are two main patterns: wrap the table in a horizontally scrollable container, or turn each row into a stacked "card" using `display: block` and `data-label` attributes.

## 🔵 सरल परिभाषा (Hindi)
Responsive table छोटी screens पर भी पढ़ने लायक रहता है। दो मुख्य तरीके हैं: table को horizontally scroll होने वाले container में रखना, या `display: block` और `data-label` से हर row को "card" की तरह stack करना।

---

## 🔴 Problem it Solves
```
PROBLEM: tables are inherently wide. On a 375px phone:
  - columns squash and text breaks into 1 word per line, or
  - the whole PAGE scrolls sideways (very bad UX)

SOLUTION: contain the overflow (scroll wrapper) or reshape the data (cards).
```

## 🔴 यह क्यों बना? (Hindi)
```
समस्या: tables स्वभाव से चौड़ी होती हैं। 375px के phone पर:
  - columns दब जाते हैं और text एक-एक शब्द में टूटता है, या
  - पूरा PAGE side में scroll होता है (बहुत खराब UX)

हल: overflow को container में रखो (scroll wrapper) या data का रूप बदलो (cards)।
```

---

## 🟢 How it Works — Step by Step
```
PATTERN 1 - scroll wrapper
  1. <div class="scroll"> around <table>
  2. .scroll { overflow-x: auto }  -> only the wrapper scrolls
  3. table { min-width: 560px }    -> keeps columns readable, triggers scroll
  4. tabindex="0" + role="region" + aria-label so keyboard users can scroll

PATTERN 2 - stacked cards (max-width: 600px)
  1. table, tbody, tr, td { display: block }   -> table layout turned off
  2. hide <thead> visually (clip, not display:none, keeps semantics)
  3. tr = card (background, radius, shadow)
  4. td { display:flex; justify-content: space-between }
  5. td::before { content: attr(data-label) }  -> shows column name per value
```

## 🟢 कैसे काम करता है? (Hindi)
```
तरीका 1 - scroll wrapper
  1. <table> के चारों ओर <div class="scroll">
  2. .scroll { overflow-x: auto } -> सिर्फ wrapper scroll होता है
  3. table { min-width: 560px }   -> columns पढ़ने लायक रहते हैं
  4. tabindex="0" + role="region" + aria-label ताकि keyboard user भी scroll कर सके

तरीका 2 - stacked cards (max-width: 600px)
  1. table, tbody, tr, td { display: block } -> table layout बंद
  2. <thead> को visually छिपाओ (display:none नहीं, ताकि semantics बने रहें)
  3. tr = card (background, radius, shadow)
  4. td { display:flex; justify-content: space-between }
  5. td::before { content: attr(data-label) } -> हर value के साथ column का नाम दिखता है
```

---

## 🟡 Real World Example
**Zomato / Swiggy order history** and **Amazon "Your Orders"** show data as cards on mobile. **Gmail** (list rows) and **bank/finance dashboards** use scrollable wide tables with a sticky first column. **Admin panels** (Razorpay, Stripe) typically use the scroll-wrapper pattern.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy की order history** और **Amazon "Your Orders"** mobile पर cards की तरह दिखते हैं। **Bank/finance dashboards** में wide table scroll wrapper के साथ और पहला column sticky होता है। **Admin panels** (Razorpay, Stripe) आम तौर पर scroll-wrapper वाला तरीका use करते हैं।

---

## 💻 Live Code Example
Complete page: [index.html](index.html) + [style.css](style.css).

```html
<!-- Pattern 2 cell: data-label is displayed on mobile -->
<tr><td data-label="Order">#4821</td><td data-label="Total">Rs 540</td></tr>
```

```css
/* Pattern 1 */
.scroll { overflow-x: auto; }
.scroll .table { min-width: 560px; }

/* Pattern 2 */
@media (max-width: 600px) {
  .stack, .stack tbody, .stack tr, .stack td { display: block; }
  .stack td { display: flex; justify-content: space-between; }
  .stack td::before { content: attr(data-label); font-weight: 600; }
}
```

---

## 🟠 React/Next.js Connection
```jsx
// Reusable scroll wrapper (Tailwind)
export function TableWrap({ children }) {
  return <div className="overflow-x-auto rounded-lg shadow" tabIndex={0} role="region" aria-label="Table">{children}</div>;
}

// Cards pattern: render data-label from your column config
const cols = [{ key: 'id', label: 'Order' }, { key: 'total', label: 'Total' }];

<table className="w-full">
  <tbody>
    {rows.map((r) => (
      <tr key={r.id} className="block border-b md:table-row">
        {cols.map((c) => (
          // Tailwind: before:content-[attr(data-label)] shows the label on mobile only
          <td key={c.key} data-label={c.label}
              className="flex justify-between p-3 before:font-semibold before:content-[attr(data-label)] md:table-cell md:before:content-none">
            {r[c.key]}
          </td>
        ))}
      </tr>
    ))}
  </tbody>
</table>
// For big data sets use TanStack Table (headless) + virtualization.
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you make a table responsive?**
A1: Wrap it in `overflow-x: auto` so it scrolls horizontally, or at a breakpoint switch rows to blocks and show header labels with `td::before { content: attr(data-label) }`.

**Q2: Why not put `overflow-x: auto` directly on `<table>`?**
A2: A table has `display: table`, and overflow does not apply the way it does on a block box. Put the overflow on a wrapper div.

**Q3: How do you keep accessibility when using `display:block` on table parts?**
A3: Changing `display` on table elements can drop table semantics in some browsers/screen readers. Add `role="table"`, `role="row"`, `role="cell"` or hide thead with clip (not `display:none`). Prefer the scroll wrapper when semantics matter.

**Q4: How do you keep the first column visible while scrolling?**
A4: `position: sticky; left: 0; background: #fff; z-index: 1` on the first `th`/`td`, inside the scroll container.

**Q5: When use scroll vs cards?**
A5: Scroll when users compare many columns (finance, analytics). Cards when each row is an independent entity with few important fields (orders, contacts).

---

## 🔷 Common Mistakes to Avoid
❌ **Mistake 1:** Table wider than viewport with no wrapper, so the whole page scrolls sideways.
✅ **Correct way:** Wrap in `overflow-x: auto`.

❌ **Mistake 2:** Using tables for page layout.
✅ **Correct way:** Use Grid/Flexbox; tables only for tabular data.

❌ **Mistake 3:** `display:none` on `thead` in card mode.
✅ **Correct way:** Visually hide it with the clip technique.

❌ **Mistake 4:** Forgetting `scope="col"` and `<caption>`.
✅ **Correct way:** Add them for screen readers.

❌ **Mistake 5:** Missing `data-label` values.
✅ **Correct way:** Generate them from the column config.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `overflow-x: auto` | Scrollbar only when needed | ज़रूरत पर side scroll |
| `border-collapse` | Merge cell borders | Borders जोड़ना |
| `data-label` | Custom attribute holding column name | Column नाम वाला attribute |
| `attr()` | Reads an attribute into CSS content | Attribute को CSS में पढ़ना |
| Sticky column | Column that stays while scrolling | चिपका हुआ column |
| `scope` | Marks header as column/row header | Header का प्रकार |

---

## ⚡ 3-Line Summary
**English:**
1. Wide tables need containment: wrap in `overflow-x: auto` (simple, keeps semantics).
2. Or at a breakpoint turn rows into cards using `display:block` and `td::before { content: attr(data-label) }`.
3. Keep accessibility (scope, caption, focusable scroller); in React drive labels from column config.

**Hindi:**
1. चौड़ी tables को रोकना ज़रूरी है: `overflow-x: auto` wrapper (आसान, semantics बने रहते हैं)।
2. या breakpoint पर `display:block` और `td::before { content: attr(data-label) }` से rows को cards बनाओ।
3. Accessibility रखो (scope, caption, focusable scroller); React में labels column config से बनाओ।

---

## ➡️ Next Topic
**121. Image Gallery with Grid** — अलग-अलग size की images की grid, hover effect और object-fit।
