# 209. Implement Virtual List
# हिंदी में: Virtual List बनाओ (Windowing)

Code: [App.jsx](./App.jsx) (complete working implementation: `getVisibleRange`, `VirtualList`, demo `App` with 10,000 rows)

---

## 🔵 Simple Definition (English)
A **virtual list** (windowing) renders only the rows that are visible in the scroll area, plus a few extra, instead of all rows. A tall empty spacer keeps the scrollbar correct, and rows are placed at the right position with absolute positioning.

## 🔵 सरल परिभाषा (Hindi)
**Virtual list** (windowing) scroll area में दिखने वाली rows और कुछ अतिरिक्त rows ही render करती है, सभी rows नहीं। एक लंबा खाली spacer scrollbar को सही रखता है, और rows absolute positioning से सही जगह पर रखी जाती हैं।

---

## 🔴 Problem it Solves

Rendering 10,000 rows creates 10,000 (or more) DOM nodes. The first render is slow, scrolling is janky, memory grows, and every state change re-renders a huge tree. The user only sees about 10 rows at a time, so 99.9 percent of the work is wasted. Virtualization keeps the DOM size constant (about 13 nodes here) regardless of the list length.

## 🔴 यह क्यों बना? (Hindi)
10,000 rows render करने पर 10,000 (या ज़्यादा) DOM nodes बनते हैं। पहला render धीमा होता है, scroll अटकता है, memory बढ़ती है, और हर state change पर पूरा बड़ा tree दोबारा render होता है। User को एक समय में सिर्फ़ 10 rows दिखती हैं, तो 99.9 प्रतिशत काम बेकार है। Virtualization list कितनी भी लंबी हो, DOM का size स्थिर (यहाँ लगभग 13 nodes) रखती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Fixed row height (itemHeight = 40) and viewport height (400)
Step 2 → Outer div: height 400, overflow-y auto, position relative (the scroll container)
Step 3 → Inner spacer div: height = items.length * itemHeight (scrollbar reflects ALL rows)
Step 4 → onScroll saves scrollTop in state
Step 5 → first = floor(scrollTop / itemHeight); count = ceil(viewport / itemHeight)
Step 6 → start = max(0, first - overscan); end = min(total, first + count + overscan)
Step 7 → Render only items[start..end) at top = index * itemHeight (position: absolute)
Step 8 → Scrolling changes scrollTop → new range → React updates a few rows
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Row की height fixed (itemHeight = 40) और viewport height (400)
Step 2 → बाहरी div: height 400, overflow-y auto, position relative (scroll container)
Step 3 → अंदर का spacer div: height = items.length * itemHeight (scrollbar सारी rows दिखाता है)
Step 4 → onScroll scrollTop को state में रखता है
Step 5 → first = floor(scrollTop / itemHeight); count = ceil(viewport / itemHeight)
Step 6 → start = max(0, first - overscan); end = min(total, first + count + overscan)
Step 7 → सिर्फ items[start..end) render करो, top = index * itemHeight (position: absolute)
Step 8 → Scroll से scrollTop बदलता है → नई range → React कुछ ही rows update करता है
```

---

## 🟡 Real World Example
**Swiggy order history / Amazon "Your Orders":** A power user has 8,000 past orders. The page does not create 8,000 cards. It renders the 10 you can see plus a few above and below. As you scroll, the same few DOM nodes are reused for new orders. Chat apps such as WhatsApp Web and spreadsheet tools such as Google Sheets use the same idea.

## 🟡 Real Example Hindi mein
**Swiggy order history / Amazon "Your Orders":** किसी power user के 8,000 पुराने orders हैं। Page 8,000 cards नहीं बनाता। वह जो 10 दिखते हैं और ऊपर-नीचे कुछ अतिरिक्त render करता है। Scroll करने पर वही कुछ DOM nodes नए orders के लिए दोबारा इस्तेमाल होते हैं। WhatsApp Web जैसे chat apps और Google Sheets जैसे spreadsheet tools भी यही idea इस्तेमाल करते हैं।

---

## 💻 Code Example — Basic

```jsx
// Basic: the math only. Which rows are visible at a given scroll position?
function visibleRange(scrollTop, viewportHeight, itemHeight, total) {
  const start = Math.floor(scrollTop / itemHeight);                 // first row at the top edge
  const end = Math.min(total, start + Math.ceil(viewportHeight / itemHeight) + 1); // +1: partial row
  return { start, end };                                            // render rows start..end-1
}

console.log(visibleRange(0, 400, 40, 10000));     // { start: 0, end: 11 }
console.log(visibleRange(4000, 400, 40, 10000));  // { start: 100, end: 111 }
```

## 💻 Code Example — Advanced

The full file is [App.jsx](./App.jsx). Its structure:

```jsx
// Virtual list (windowing): render only the visible rows of a fixed-height list
import { useState, useMemo } from 'react';
import { createRoot } from 'react-dom/client';

// Pure math: easy to unit test
export function getVisibleRange({ scrollTop, viewportHeight, itemHeight, total, overscan = 3 }) {
  const first = Math.floor(scrollTop / itemHeight);          // first row touching the top
  const count = Math.ceil(viewportHeight / itemHeight);      // rows that fit in the view
  const start = Math.max(0, first - overscan);               // extra rows above (smooth fast scroll)
  const end = Math.min(total, first + count + overscan);     // extra rows below (exclusive end)
  return { start, end };
}

export function VirtualList({ items, itemHeight = 40, height = 400, overscan = 3, renderItem }) {
  const [scrollTop, setScrollTop] = useState(0);             // scroll position drives everything

  const { start, end } = useMemo(
    () => getVisibleRange({ scrollTop, viewportHeight: height, itemHeight, total: items.length, overscan }),
    [scrollTop, height, itemHeight, items.length, overscan]
  );

  const visible = [];                                        // only these rows exist in the DOM
  for (let i = start; i < end; i++) {
    visible.push(
      <div key={i} style={{ position: 'absolute', top: i * itemHeight, height: itemHeight, left: 0, right: 0 }}>
        {renderItem(items[i], i)}
      </div>
    );
  }

  return (
    <div onScroll={(e) => setScrollTop(e.currentTarget.scrollTop)}
         style={{ height, overflowY: 'auto', position: 'relative' }} data-testid="viewport">
      {/* spacer: full height so the scrollbar looks like the whole list */}
      <div style={{ height: items.length * itemHeight, position: 'relative' }}>{visible}</div>
    </div>
  );
}

const orders = Array.from({ length: 10000 }, (_, i) => `Order #${i + 1}`);
export default function App() {
  return <VirtualList items={orders} renderItem={(text) => <span>{text}</span>} />;
}
```

Verified by script in jsdom: `getVisibleRange` gives `{0, 13}` at scrollTop 0 and `{97, 113}` at scrollTop 4000 (viewport 400, row 40, overscan 3), and the rendered demo has exactly 13 row elements for 10,000 items.

---

## 🟠 Next.js Connection

A virtual list needs scroll events and DOM measurement, so it is a Client Component. The Server Component can fetch data and pass it down. For production, use a library (TanStack Virtual, react-window) because they handle variable heights, dynamic measuring and horizontal lists.

```jsx
// app/orders/page.jsx (Server Component): fetch on the server
import OrdersList from './OrdersList';                     // Client Component below
import { getOrders } from '@/lib/orders';                  // hypothetical data helper

export default async function Page() {
  const orders = await getOrders();                        // array of { id, title }
  return <OrdersList orders={orders} />;                   // serializable props only
}
```

```jsx
// app/orders/OrdersList.jsx
'use client';                                              // scroll state needs the client
import { VirtualList } from '@/components/VirtualList';    // the component from App.jsx

export default function OrdersList({ orders }) {
  return <VirtualList items={orders} height={500} itemHeight={56}
                      renderItem={(o) => <strong>{o.title}</strong>} />;
}
```

Note: the server HTML contains only the first rows, so a virtual list helps runtime performance but gives crawlers only the initial rows. For SEO-critical content, paginate instead. TanStack Virtual API names are version-dependent, check its docs.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Rendering the whole list and hoping `overflow: auto` makes it fast
✅ **Correct:** Render only the window of rows

```jsx
// Wrong: 10,000 DOM nodes, slow first paint and slow updates
{items.map((x) => <Row key={x.id} {...x} />)}

// Right: slice by the computed range
{items.slice(start, end).map((x, i) => <Row key={x.id} {...x} style={{ top: (start + i) * H }} />)}
```

❌ **Mistake 2:** Forgetting the spacer, so the scrollbar is tiny or missing
✅ **Correct:** Add a container with `height = total * itemHeight`

```jsx
// Wrong: absolutely positioned rows have no height, parent height is 0, nothing to scroll
<div style={{ overflowY: 'auto', height: 400 }}>{visible}</div>

// Right
<div style={{ overflowY: 'auto', height: 400 }}>
  <div style={{ height: items.length * 40, position: 'relative' }}>{visible}</div>
</div>
```

❌ **Mistake 3:** No overscan, causing white flashes on fast scroll
✅ **Correct:** Render a few extra rows above and below

```jsx
// Wrong: end = first + count  → blank area appears before React catches up
// Right: end = first + count + overscan (3 to 5 rows is typical)
```

---

## 🧠 Tricky Interview Question

```jsx
// scrollTop = 85, itemHeight = 40, viewportHeight = 400, total = 100, overscan = 0
const first = Math.floor(85 / 40);          // ?
const count = Math.ceil(400 / 40);          // ?
const end = Math.min(100, first + count);   // ?
```
Which rows are shown, and is that enough?

**Answer:** `first = 2`, `count = 10`, `end = 12`, so rows 2 to 11 render. But the viewport starts 5px inside row 2 (85 - 80) and so shows part of row 12 at the bottom: the visible window covers pixels 85 to 485, and row 12 spans 480 to 520. With `overscan = 0` the bottom 5px would be blank. That is why `count` is computed with `ceil` and an overscan (or +1) is added. The general rule: when scrollTop is not a multiple of itemHeight, you need `ceil` plus a spare row.

---

## ⚫ Interview Questions + Answers

Q1: What is list virtualization and why use it?
A1: Rendering only the items inside (and just around) the viewport. It keeps DOM size and render cost constant, so a list of 100,000 rows scrolls as smoothly as one of 100.

Q2: Why is the spacer div needed?
A2: Rows are absolutely positioned and do not give the container any height. The spacer has the height of the full list, so the browser draws a correct scrollbar and allows scrolling to any position.

Q3: What is overscan?
A3: Extra rows rendered beyond the visible edges. Scroll events and React updates are asynchronous, so without overscan fast scrolling shows blank gaps. Typical values are 3 to 10 rows.

Q4: How do you handle variable row heights?
A4: Fixed heights give O(1) math. For variable heights you either measure rows (ResizeObserver) and keep a cache of offsets, searching it with binary search, or use an estimated height that is corrected after measuring. Libraries like TanStack Virtual do this.

Q5: What are the downsides of virtualization?
A5: Browser find (Ctrl+F) and screen readers cannot see unrendered rows, SEO sees only initial rows, focus can be lost when a focused row scrolls out, and the implementation is more complex. Use it only for really large lists; pagination or "load more" is often simpler.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- The list has thousands of rows (orders, logs, chat history, tables)
- Each row is heavy (images, many nodes)
- Scroll jank is measured in the Performance panel

❌ **Avoid when:**
- The list has fewer than about 100 simple rows (plain `map` is fine)
- Content must be searchable by the browser or indexed by crawlers
- Rows have wildly different, unknown heights and you have no library

---

## 📊 Visual Diagram

```
  data: 10,000 items          DOM (what actually exists)

  ┌───────────────┐           ┌──────────────── viewport (400px, scrolls) ─┐
  │ item 0        │           │ spacer height = 10,000 * 40 = 400,000 px   │
  │ item 1        │           │   ... empty space above (top: 0..)         │
  │ ...           │  scroll   │   row 97  top: 3880                        │
  │ item 97       │ ────────► │   row 98  top: 3920                        │
  │ item 98 ◄──── visible     │   row 99  top: 3960   ← visible area       │
  │ ...           │           │   ...                                      │
  │ item 109      │           │   row 112 top: 4480                        │
  │ ...           │           │   ... empty space below                    │
  │ item 9,999    │           └────────────────────────────────────────────┘
  └───────────────┘            only rows 97..112 exist (about 13 to 16 nodes)

  scrollTop=4000 → first=100 → start=97 (overscan 3), end=113
  Re-renders: every scroll event re-renders ~13 rows, not 10,000.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Virtualization / Windowing | Render only visible items | सिर्फ़ दिखने वाले items render करना |
| Viewport | The visible scroll area | दिखने वाला scroll क्षेत्र |
| Overscan | Extra rows rendered outside the view | View के बाहर अतिरिक्त rows |
| Spacer | Empty element giving full scroll height | पूरी scroll height देने वाला खाली element |
| scrollTop | How far the container is scrolled (px) | Container कितना scroll हुआ (px) |
| Absolute positioning | Place an element by top/left offsets | top/left से जगह तय करना |
| DOM node | One element in the page tree | Page tree का एक element |
| Layout thrashing | Repeated forced layout reads/writes | बार-बार forced layout पढ़ना/लिखना |

---

## ⚡ 3-Line Summary
**English:**
1. A virtual list renders only visible rows (plus overscan) and uses a full-height spacer for the scrollbar.
2. `scrollTop` and `itemHeight` give the start and end index with simple math, and rows are placed with `top = index * itemHeight`.
3. It makes huge lists fast, but costs searchability and SEO; use libraries like TanStack Virtual for variable heights.

**Hindi:**
1. Virtual list सिर्फ़ दिखने वाली rows (और overscan) render करती है और scrollbar के लिए पूरी height का spacer इस्तेमाल करती है।
2. `scrollTop` और `itemHeight` से सरल math द्वारा start व end index मिलते हैं, और rows `top = index * itemHeight` पर रखी जाती हैं।
3. इससे बड़ी lists तेज़ होती हैं, पर searchability और SEO घटते हैं; variable heights के लिए TanStack Virtual जैसी libraries लो।

---

## ➡️ Next Topic
**210. Build Simple Redux from Scratch** — `createStore`, `combineReducers`, middleware और thunk खुद बनाकर समझो कि Redux अंदर से कैसे काम करता है।
