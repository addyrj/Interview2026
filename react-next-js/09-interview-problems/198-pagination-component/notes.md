# 198. Build Pagination Component
# हिंदी में: Pagination Component बनाना

Code: [`App.jsx`](./App.jsx) in this folder (pure `getPageRange` helper with ellipsis, reusable `Pagination` component, client-side paging demo).

---

## 🔵 Simple Definition (English)
Pagination splits a long list into pages and shows controls to move between them: Prev, Next and page numbers (with `...` for skipped ranges). The core logic is a small pure function that computes which page numbers to display.

## 🔵 सरल परिभाषा (Hindi)
Pagination लंबी list को pages में बाँटता है और उनके बीच जाने के controls देता है: Prev, Next और page numbers (छूटी हुई range के लिए `...`)। मुख्य logic एक छोटा pure function है जो तय करता है कि कौन से page numbers दिखाने हैं।

---

## 🔴 Problem it Solves

Rendering thousands of rows is slow, and one huge page is hard to navigate. But showing 500 page buttons is also bad. A good pagination component shows only a window around the current page, always shows the first and last page, and uses an ellipsis for gaps ("1 ... 4 5 6 ... 20"). Interviewers test the range algorithm, off-by-one errors and edge cases (few pages, first or last page).

```jsx
// PROBLEM: one button per page for 500 pages
{Array.from({ length: 500 }, (_, i) => <button key={i}>{i + 1}</button>)}  // unusable and slow ❌
```

## 🔴 यह क्यों बना? (Hindi)
हज़ारों rows render करना धीमा है और एक विशाल page में चलना कठिन है। लेकिन 500 page buttons दिखाना भी बुरा है। अच्छा pagination component मौजूदा page के आसपास की एक window दिखाता है, पहला और आख़िरी page हमेशा दिखाता है और बीच के gaps के लिए ellipsis ("1 ... 4 5 6 ... 20") इस्तेमाल करता है। Interviewer range algorithm, off-by-one गलतियों और edge cases (कम pages, पहला या आख़िरी page) को जाँचते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → State: page (1-based). Derived: totalPages = ceil(totalItems / pageSize)
Step 2 → Data for the page: items.slice((page - 1) * pageSize, page * pageSize)
Step 3 → getPageRange(current, total, siblings=1):
           always [1] first, always [total] last
           window = [current - siblings .. current + siblings], clamped to 2..total-1
           add '...' where there is a gap (window start > 2, or window end < total - 1)
Step 4 → Render: Prev (disabled on page 1), numbers (current is disabled + aria-current),
         Next (disabled on the last page)
Step 5 → onChange(p) updates page; the list re-slices

Examples (total = 10, siblings = 1):
current 1  → 1 2 ... 10
current 5  → 1 ... 4 5 6 ... 10
current 10 → 1 ... 9 10
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → State: page (1 से शुरू)। Derived: totalPages = ceil(totalItems / pageSize)
Step 2 → Page का data: items.slice((page - 1) * pageSize, page * pageSize)
Step 3 → getPageRange(current, total, siblings=1):
           पहला [1] हमेशा, आख़िरी [total] हमेशा
           window = [current - siblings .. current + siblings], 2..total-1 में सीमित
           जहाँ gap हो वहाँ '...' (window की शुरुआत > 2, या अंत < total - 1)
Step 4 → Render: Prev (page 1 पर disabled), numbers (current disabled + aria-current),
         Next (आख़िरी page पर disabled)
Step 5 → onChange(p) page बदलता है; list दोबारा slice होती है

उदाहरण (total = 10, siblings = 1):
current 1  → 1 2 ... 10
current 5  → 1 ... 4 5 6 ... 10
current 10 → 1 ... 9 10
```

---

## 🟡 Real World Example
**Google search results (1 2 3 ... Next), Amazon search results, Flipkart listing, admin tables in dashboards:** each shows a window of numbers with Prev/Next. Amazon uses `?page=3` in the URL so the page is shareable and crawlable; Swiggy/Zomato mostly use infinite scroll instead, which is a different trade-off (topic 194).

## 🟡 Real Example Hindi mein
**Google search results (1 2 3 ... Next), Amazon search results, Flipkart listing, dashboards की admin tables:** सब में numbers की एक window और Prev/Next होता है। Amazon URL में `?page=3` रखता है ताकि page share और crawl हो सके; Swiggy/Zomato ज़्यादातर infinite scroll इस्तेमाल करते हैं, जो अलग trade-off है (topic 194)।

---

## 💻 Code Example — Basic

```jsx
// Simple Prev / Next paging of an in-memory array
import { useState } from 'react';

const ITEMS = Array.from({ length: 25 }, (_, i) => `Item ${i + 1}`);   // fake data
const PAGE_SIZE = 10;

export default function SimplePaging() {
  const [page, setPage] = useState(1);                                // current page (1-based)
  const totalPages = Math.ceil(ITEMS.length / PAGE_SIZE);             // 3 pages
  const start = (page - 1) * PAGE_SIZE;                               // first index of this page
  const visible = ITEMS.slice(start, start + PAGE_SIZE);              // items of this page
  return (
    <div>
      <ul>{visible.map((x) => <li key={x}>{x}</li>)}</ul>
      <button onClick={() => setPage((p) => p - 1)} disabled={page === 1}>Prev</button>
      <span> {page} / {totalPages} </span>
      <button onClick={() => setPage((p) => p + 1)} disabled={page === totalPages}>Next</button>
    </div>
  );
}
```

## 💻 Code Example — Advanced

Full code: [`App.jsx`](./App.jsx). The algorithm and the component:

```jsx
// Pure helper: easy to unit test without React
export function getPageRange(current, total, siblings = 1) {
  const first = 1;
  const last = total;
  const start = Math.max(first + 1, current - siblings);      // window start (never overlaps first)
  const end = Math.min(last - 1, current + siblings);         // window end (never overlaps last)
  const pages = [first];
  if (start > first + 1) pages.push('...');                   // gap after the first page
  for (let p = start; p <= end; p++) pages.push(p);           // middle window
  if (end < last - 1) pages.push('...');                      // gap before the last page
  if (last > first) pages.push(last);
  return pages;
}

export function Pagination({ page, totalPages, onChange }) {
  if (totalPages <= 1) return null;                           // nothing to paginate
  const range = getPageRange(page, totalPages);
  return (
    <nav aria-label="Pagination">
      <button onClick={() => onChange(page - 1)} disabled={page === 1}>Prev</button>
      {range.map((p, i) => p === '...'
        ? <span key={`gap-${i}`}> ... </span>
        : <button key={p} onClick={() => onChange(p)}
                  aria-current={p === page ? 'page' : undefined} disabled={p === page}>{p}</button>)}
      <button onClick={() => onChange(page + 1)} disabled={page === totalPages}>Next</button>
    </nav>
  );
}
```

Verified by running the helper and the component under jsdom:
`getPageRange(1,10)` = `[1,2,'...',10]`, `(5,10)` = `[1,'...',4,5,6,'...',10]`, `(10,10)` = `[1,'...',9,10]`, `(1,2)` = `[1,2]`, `(2,3)` = `[1,2,3]`. Clicking Next shows "Order #11", and clicking 10 shows the last page with 5 items.

Known limitation of this helper: with a small `total` and a large `current` it is still correct, but the number of buttons changes as you move (the width jumps). Libraries keep a fixed count of slots to avoid layout jump.

---

## 🟠 Next.js Connection

Prefer **server-side pagination with the page in the URL**: the server fetches only one page from the database, the URL is shareable (`/orders?page=3`), the back button works, and crawlers can follow `<Link>` page links.

```jsx
// app/orders/page.jsx (Server Component)
import Link from 'next/link';
import { getOrders } from '@/lib/orders';                     // hypothetical: returns { rows, total }
import { getPageRange } from '@/lib/pagination';              // the helper from App.jsx

const PAGE_SIZE = 10;

export default async function OrdersPage({ searchParams }) {
  const sp = await searchParams;                              // Next.js 15: Promise (14: plain object)
  const page = Math.max(1, Number(sp.page) || 1);             // sanitise: never trust the URL
  const { rows, total } = await getOrders({ skip: (page - 1) * PAGE_SIZE, take: PAGE_SIZE }); // DB does OFFSET/LIMIT
  const totalPages = Math.ceil(total / PAGE_SIZE);
  return (
    <>
      <ul>{rows.map((o) => <li key={o.id}>{o.name}</li>)}</ul>
      <nav aria-label="Pagination">
        {getPageRange(page, totalPages).map((p, i) =>
          p === '...' ? <span key={`g${i}`}>...</span> : (
            <Link key={p} href={`/orders?page=${p}`} aria-current={p === page ? 'page' : undefined}>{p}</Link>
          )
        )}
      </nav>
    </>
  );
}
```
For very large tables, offset pagination gets slow (`OFFSET 100000`); production systems use cursor (keyset) pagination instead.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Off-by-one errors with 0-based vs 1-based pages
✅ **Correct:** Pick one convention (1-based for UI) and convert in exactly one place: `slice((page - 1) * size, page * size)`.

```jsx
// Wrong: page 1 skips the first 10 items
items.slice(page * size, (page + 1) * size);                           // ❌ for 1-based page
// Right
items.slice((page - 1) * size, page * size);                           // ✅
```

❌ **Mistake 2:** Not clamping the page when the data changes (filter, delete) or when the URL is invalid
✅ **Correct:** Clamp to `[1, totalPages]`, or reset to page 1 when filters change.

```jsx
// Wrong: page 7 stays selected after a filter leaves only 2 pages → empty list
const [page, setPage] = useState(7);                                   // ❌
// Right: derive a safe page
const safePage = Math.min(Math.max(1, page), totalPages || 1);         // ✅
// and call setPage(1) inside the filter change handler
```

❌ **Mistake 3:** Using the index as `key` for the ellipsis, or computing totals with floats (`total / size` without `ceil`)
✅ **Correct:** `Math.ceil`, unique keys for gaps (`gap-${i}`), and numeric page values as keys for page buttons.

```jsx
// Wrong: 95 / 10 = 9.5 pages; two '...' share the same key
const totalPages = 95 / 10;                                            // ❌
{range.map((p) => <span key={p}>{p}</span>)}                           // ❌ duplicate '...' keys
// Right
const totalPages = Math.ceil(95 / 10);                                 // ✅ 10
{range.map((p, i) => <span key={p === '...' ? `gap-${i}` : p}>{p}</span>)} // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
console.log(getPageRange(3, 5));
console.log(getPageRange(4, 5));
// Using the getPageRange from App.jsx (siblings = 1). What is printed?
```
**Answer:** The first call prints `[1, 2, 3, 4, 5]` and the second prints `[1, '...', 3, 4, 5]`. For `(3, 5)`: `start = max(2, 2) = 2` and `end = min(4, 4) = 4`. There is no left gap (`start > 2` is false) and no right gap (`end < 4` is false), so every page appears. For `(4, 5)`: `start = max(2, 3) = 3` and `end = min(4, 5) = 4`. Now `start > 2` is true, so `'...'` is inserted, but it hides only page 2. A better implementation shows page 2 instead of an ellipsis when the gap is exactly one page. Trace the algorithm by hand like this; this off-by-one detail is exactly what interviewers probe.

---

## ⚫ Interview Questions + Answers

Q1: How do you compute the items for a page and the total number of pages?
A1: `totalPages = Math.ceil(totalItems / pageSize)` and `items.slice((page - 1) * pageSize, page * pageSize)` for 1-based pages. On a server use `OFFSET`/`LIMIT` or `skip`/`take`.

Q2: How does the ellipsis algorithm work?
A2: Always include the first and last page. Compute a window of `current ± siblings` clamped between 2 and `total - 1`. If the window starts after page 2, add `...` before it; if it ends before `total - 1`, add `...` after it. The function is pure, so it is easy to unit test.

Q3: Client-side vs server-side pagination?
A3: Client-side loads all data and slices in the browser: simple, instant page changes, but heavy for large data. Server-side asks the backend for one page at a time: scalable and cheap per request, requires loading states and a total count. Use server-side for anything beyond a few hundred rows.

Q4: Offset vs cursor pagination?
A4: Offset (`page=3`) is simple and supports jumping to a page, but gets slower for large offsets and can duplicate or skip rows if data changes between requests. Cursor/keyset (`after=<id>`) is fast and stable for feeds, but cannot jump to arbitrary pages.

Q5: How do you make pagination accessible and SEO-friendly?
A5: Wrap it in `<nav aria-label="Pagination">`, mark the current page with `aria-current="page"`, use real links (`<a href="?page=2">`/`next/link`) so crawlers and middle-click work, disable Prev/Next at the ends, and keep the page in the URL.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Users need to find, compare or return to a specific position (search results, tables)
- You need shareable URLs and predictable footer content
- Data is large and you want bounded page weight

❌ **Avoid when:**
- The experience is an endless discovery feed (use infinite scroll)
- The list is small enough to show fully (a few dozen items)
- You need stable results over rapidly changing data without a cursor (offset can skip/duplicate)

---

## 📊 Visual Diagram

```
  total = 20, current = 10, siblings = 1

  1  ...  9  [10]  11  ...  20
  │   │   └──window──┘   │    │
  │   gap                gap  last (always)
  first (always)

  data flow:
  items[200] ──slice((page-1)*10, page*10)──▶ 10 rows on screen
  page (state / URL) ──▶ getPageRange(page, 20) ──▶ buttons

  Re-render: changing page re-renders the list and the pager only; memoise rows if heavy.
  Server-side: URL ?page=N → server fetches rows N → HTML (no big client data).
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pagination | Splitting data into pages | Data को pages में बाँटना |
| Page size | Items per page | प्रति page items |
| Siblings | Page numbers shown around current | मौजूदा page के आसपास के numbers |
| Ellipsis | `...` for hidden page numbers | छिपे numbers का `...` चिह्न |
| Offset pagination | Skip N rows then take M | N rows छोड़कर M लेना |
| Cursor pagination | Continue after a given item | किसी item के बाद से आगे बढ़ना |
| aria-current | Marks the current page | मौजूदा page को दर्शाता है |
| Pure function | Same input → same output, no side effects | समान input पर समान output, कोई side effect नहीं |

---

## ⚡ 3-Line Summary
**English:**
1. Compute `totalPages` with `Math.ceil`, slice data with `(page - 1) * size`, and show a window of page numbers with ellipses using a pure helper.
2. Disable Prev/Next at the ends, mark the current page with `aria-current`, clamp invalid pages, and trace edge cases by hand.
3. In Next.js store the page in the URL and paginate on the server; use cursor pagination for huge or fast-changing data.

**Hindi:**
1. `totalPages` `Math.ceil` से निकालो, data को `(page - 1) * size` से slice करो और एक pure helper से ellipsis वाली page numbers की window दिखाओ।
2. किनारों पर Prev/Next disable करो, मौजूदा page पर `aria-current` लगाओ, गलत pages को clamp करो और edge cases हाथ से trace करो।
3. Next.js में page को URL में रखो और server पर paginate करो; बहुत बड़े या तेज़ी से बदलते data के लिए cursor pagination लो।

---

## ➡️ Next Topic
**199. Build Form with Validation** — controlled inputs, error messages, touched state और submit handling, साथ में React Hook Form और Zod का परिचय।
