# 127. Virtualization (react-window)
# हिंदी में: Virtualization — सिर्फ़ वही rows render करना जो screen पर दिख रही हैं

---

## 🔵 Simple Definition (English)
**Virtualization** (also called windowing) renders only the list items that are visible in the viewport, plus a few extra, instead of all of them. As the user scrolls, the same few DOM nodes are reused for new data. `react-window` is a small library that does this for lists and grids.

## 🔵 सरल परिभाषा (Hindi)
**Virtualization** (जिसे windowing भी कहते हैं) में list की सारी items की जगह सिर्फ़ वे items render होती हैं जो viewport में दिख रही हैं, और कुछ extra। Scroll करने पर वही कुछ DOM nodes नए data के लिए दोबारा इस्तेमाल होते हैं। `react-window` एक छोटी library है जो lists और grids के लिए यह करती है।

---

## 🔴 Problem it Solves

Rendering 10,000 rows creates 10,000 components and tens of thousands of DOM nodes. The first render is slow, memory grows, scrolling stutters, and every state change in the parent can re-render a huge tree. The user sees only about 15 rows at a time, so 99% of that work is wasted.

```jsx
// PROBLEM: 10,000 DOM rows exist even though only ~15 are visible
{orders.map(o => <OrderRow key={o.id} order={o} />)}   // slow mount, heavy memory

// SOLUTION: a virtual list renders only the visible window
<List rowCount={orders.length} rowHeight={56} rowComponent={Row} rowProps={{ orders }} />
```

## 🔴 यह क्यों बना? (Hindi)
10,000 rows render करने का मतलब है 10,000 components और हज़ारों DOM nodes। पहला render धीमा होता है, memory बढ़ती है, scroll अटकता है, और parent की हर state change पूरे बड़े tree को re-render कर सकती है। User को एक समय में सिर्फ़ 15 rows दिखती हैं, इसलिए 99% काम बेकार है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → The list has a fixed-size scroll container (height set, overflow auto)
Step 2 → An inner spacer is as tall as ALL rows (count x rowHeight), so the scrollbar looks real
Step 3 → On scroll, the library reads scrollTop and calculates the first and last visible index
Step 4 → It renders only those rows (plus a small "overscan" buffer), each absolutely positioned
Step 5 → Scrolling again changes the index range; rows are re-rendered with new data
Step 6 → DOM stays at ~20 nodes whether the list has 100 or 1,000,000 items

KEY: DOM size depends on the viewport, not on the data size
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → List का एक fixed-size scroll container होता है (height तय, overflow auto)
Step 2 → अंदर एक spacer सभी rows जितना ऊँचा होता है (count x rowHeight), इसलिए scrollbar असली जैसा दिखता है
Step 3 → Scroll पर library scrollTop पढ़कर पहला और आख़िरी visible index निकालती है
Step 4 → सिर्फ़ वही rows (और थोड़ा "overscan" buffer) absolutely positioned होकर render होती हैं
Step 5 → फिर scroll करने पर index range बदलती है; rows नए data के साथ दोबारा render होती हैं
Step 6 → DOM ~20 nodes पर रहता है, चाहे list में 100 items हों या 10 लाख

KEY: DOM का size viewport पर depend करता है, data के size पर नहीं
```

---

## 🟡 Real World Example
**Zomato order history / Flipkart product listing:** A user with 5,000 past orders (or a catalogue of 20,000 SKUs on an admin panel) scrolls through a long list. Without virtualization the page freezes on open. With virtualization only about 12 rows exist in the DOM at any time, so the screen opens instantly and scrolling stays at 60 fps. The same idea is used by chat apps (WhatsApp Web) and log viewers.

## 🟡 Real Example Hindi mein
**Zomato order history / Flipkart product listing:** जिस user के 5,000 पुराने orders हैं (या admin panel पर 20,000 SKUs की catalogue), वह लंबी list scroll करता है। Virtualization के बिना page खुलते ही freeze हो जाता है। Virtualization के साथ DOM में किसी भी समय सिर्फ़ ~12 rows होती हैं, इसलिए screen तुरंत खुलती है और scroll 60 fps पर चलता है। यही idea chat apps (WhatsApp Web) और log viewers में भी इस्तेमाल होता है।

---

## 💻 Code Example — Basic

Note: `react-window` v2 (2025) uses `List` with `rowComponent`, `rowCount`, `rowHeight`, `rowProps`. v1 used `FixedSizeList` with `itemCount`, `itemSize` and children as a render function. The API is **version-dependent**, so check the installed version. This example uses the v2 API.

```jsx
// Basic fixed-height virtual list (react-window v2 API)
import { List } from 'react-window';                  // virtualized list component
import { createRoot } from 'react-dom/client';        // React 18/19 root API

const orders = Array.from({ length: 10000 }, (_, i) => ({  // fake 10,000 orders
  id: i,                                              // unique id
  name: `Order #${i + 1}`,                            // label shown in the row
}));

// Row receives index + style from react-window, plus our own rowProps
function Row({ index, style, orders }) {              // style positions the row absolutely
  const order = orders[index];                        // pick the data for this index
  return (
    <div style={style}>                               {/* MUST apply style or layout breaks */}
      {order.name}                                    {/* row content */}
    </div>
  );
}

function App() {
  return (
    <List
      rowComponent={Row}                              // component used to render each row
      rowCount={orders.length}                        // total number of rows (10,000)
      rowHeight={40}                                  // each row is 40px tall
      rowProps={{ orders }}                           // extra props passed to every Row
      style={{ height: 400, width: 300 }}             // visible window size
    />
  );
}

createRoot(document.getElementById('root')).render(<App />); // mount the app
```

## 💻 Code Example — Advanced

```jsx
// Advanced: memoized row, search filter, and "infinite" load near the end
import { memo, useMemo, useState, useCallback } from 'react'; // React hooks
import { List } from 'react-window';                          // virtualized list
import { createRoot } from 'react-dom/client';                // root API

// memo: a row re-renders only if its own props change, not on every scroll tick
const OrderRow = memo(function OrderRow({ index, style, items, onSelect }) {
  const item = items[index];                                  // data for this row
  return (
    <div
      style={{ ...style, display: 'flex', justifyContent: 'space-between' }} // keep library style
      onClick={() => onSelect(item.id)}                       // row click handler
    >
      <span>{item.restaurant}</span>                          {/* left: restaurant */}
      <strong>Rs {item.total}</strong>                        {/* right: amount */}
    </div>
  );
});

// Fake API page loader (replace with fetch in a real app)
const makePage = (start, size) =>
  Array.from({ length: size }, (_, i) => ({
    id: start + i,                                            // stable unique id
    restaurant: ['Biryani Blues', 'Pizza Hub', 'Dosa Plaza'][(start + i) % 3],
    total: 150 + ((start + i) % 40) * 10,                     // fake amount
  }));

function OrderHistory() {
  const [items, setItems] = useState(() => makePage(0, 50));  // first 50 orders
  const [query, setQuery] = useState('');                     // search text
  const [selected, setSelected] = useState(null);             // clicked order id

  const filtered = useMemo(                                   // filter only when inputs change
    () => items.filter(o => o.restaurant.toLowerCase().includes(query.toLowerCase())),
    [items, query]
  );

  const onSelect = useCallback(id => setSelected(id), []);    // stable function for memo rows

  // rowsRendered fires when the visible range changes (v2 prop: onRowsRendered)
  const onRowsRendered = useCallback(({ stopIndex }) => {     // last visible index
    if (!query && stopIndex >= items.length - 5) {            // near the end of the data
      setItems(prev => prev.length >= 1000 ? prev : [...prev, ...makePage(prev.length, 50)]);
    }
  }, [items.length, query]);

  return (
    <div>
      <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search orders" />
      <p>Selected: {selected ?? 'none'} | Loaded: {items.length}</p>
      <List
        rowComponent={OrderRow}                               // memoized row
        rowCount={filtered.length}                            // count after filtering
        rowHeight={44}                                        // fixed height keeps math simple
        rowProps={{ items: filtered, onSelect }}              // shared props for every row
        onRowsRendered={onRowsRendered}                       // pagination trigger
        overscanCount={5}                                     // render 5 extra rows to avoid blank flashes
        style={{ height: 440 }}                               // window height
      />
    </div>
  );
}

createRoot(document.getElementById('root')).render(<OrderHistory />);
```

---

## 🟠 Real App Integration

In Next.js App Router, virtualization needs scroll position and DOM measurements, so the list must be a Client Component. Fetch the first page in a Server Component and pass it down as props, so the first HTML already has the top rows (they are rendered on the server too, using the initial window).

```jsx
// app/orders/page.jsx (Server Component: fetches data, no hooks)
import OrderList from './OrderList';                    // client component below
import { getOrders } from '@/lib/orders';               // your data layer (hypothetical helper)

export default async function Page() {
  const orders = await getOrders({ limit: 500 });       // fetched on the server
  return <OrderList initialOrders={orders} />;          // serializable props only
}
```

```jsx
// app/orders/OrderList.jsx
'use client';                                           // virtualization needs browser scroll events
import { List } from 'react-window';                    // virtualized list

function Row({ index, style, orders }) {                // row renderer
  return <div style={style}>{orders[index].name}</div>; // use the style from react-window
}

export default function OrderList({ initialOrders }) {
  return (
    <List
      rowComponent={Row}                                // row component
      rowCount={initialOrders.length}                   // number of rows
      rowHeight={48}                                    // fixed row height
      rowProps={{ orders: initialOrders }}              // data for rows
      style={{ height: '80vh' }}                        // fill most of the screen
    />
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting to apply the `style` prop to the row
✅ **Correct:** Always spread/apply the `style` that react-window gives you; it holds the absolute position

```jsx
// Wrong: rows all stack at the top, overlapping each other
function Row({ index, orders }) {
  return <div>{orders[index].name}</div>;               // ❌ no style → no positioning
}

// Right: style positions each row inside the scroll area
function Row({ index, style, orders }) {
  return <div style={style}>{orders[index].name}</div>; // ✅ position + height from the library
}
```

❌ **Mistake 2:** Defining the row component inline so it is a new type each render
✅ **Correct:** Define it at module level (and `memo` it), pass data through `rowProps`

```jsx
// Wrong: Row is re-created on each App render → every row remounts, scroll jank
function App({ orders }) {
  const Row = ({ index, style }) => <div style={style}>{orders[index].name}</div>; // ❌ inline
  return <List rowComponent={Row} rowCount={orders.length} rowHeight={40} rowProps={{}} />;
}

// Right: stable component, data via rowProps
const Row = ({ index, style, orders }) => <div style={style}>{orders[index].name}</div>; // ✅
function App2({ orders }) {
  return <List rowComponent={Row} rowCount={orders.length} rowHeight={40} rowProps={{ orders }} />;
}
```

❌ **Mistake 3:** Virtualizing a short list (under about 100 simple rows)
✅ **Correct:** Render normally; virtualization adds complexity (fixed heights, no Ctrl+F search, accessibility trade-offs)

```jsx
// Wrong: 20 items virtualized for no gain
<List rowCount={20} rowHeight={40} rowComponent={Row} rowProps={{}} />   // ❌ overkill

// Right: plain map is simpler and searchable by the browser
{items.map(i => <Row key={i.id} item={i} />)}                             // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
import { List } from 'react-window';

const items = Array.from({ length: 1000000 }, (_, i) => i);
const Row = ({ index, style }) => <div style={style}>{items[index]}</div>;

function App() {
  return <List rowComponent={Row} rowCount={items.length} rowHeight={30} rowProps={{}} style={{ height: 300 }} />;
}
// Question: how many Row components exist in memory at once, and why can Ctrl+F not find "999999"?
```
**Answer:** Only about 10 rows are visible (300 / 30) plus the overscan rows, so roughly 12 to 20 `Row` instances exist, not 1,000,000. The array of numbers itself still exists in memory, since virtualization limits DOM and components, not your data. Ctrl+F searches the DOM text, and "999999" is not in the DOM until you scroll near it, so the browser cannot find it. That is the trade-off: you need your own search UI that scrolls to an index (for example with the list's `scrollToRow` / `scrollToItem` imperative method, name depends on version).

---

## ⚫ Interview Questions + Answers

Q1: What is list virtualization and why use it?
A1: Rendering only the visible rows plus a small buffer. It keeps the DOM small, so the first render, memory usage and scrolling stay fast regardless of data size.

Q2: How does react-window know which rows to render?
A2: It uses fixed (or computed) row sizes and the scroll offset. With a fixed row height, `startIndex = floor(scrollTop / rowHeight)` and the end index follows from the container height. It then renders those rows with absolute positions inside a tall spacer.

Q3: What is overscan?
A3: Extra rows rendered just outside the visible area. They prevent blank flashes when the user scrolls fast, at a small rendering cost. Typical values are 3 to 10.

Q4: What are the drawbacks of virtualization?
A4: Browser find (Ctrl+F) cannot see off-screen rows, accessibility needs care (aria-rowcount, keyboard navigation), variable-height rows need measurement, and anchor links or print views may not work as expected.

Q5: react-window vs react-virtualized vs TanStack Virtual?
A5: `react-virtualized` is the older, larger, feature-heavy library. `react-window` is a lighter rewrite by the same author. TanStack Virtual is headless (hooks only, you control markup) and handles dynamic heights well. Pick by need: simple list, react-window; custom layout or dynamic sizes, TanStack Virtual.

---

## 🔷 When to Use + When Not to Use
✅ **Use virtualization when:**
- The list has hundreds or thousands of rows (order history, logs, tables, chat)
- Each row is complex and mounting all of them is measurably slow
- Profiling shows long scripting or layout time caused by list size

❌ **Avoid virtualization when:**
- The list is short (under about 100 simple items)
- You need native browser search, print or SEO for all rows
- Pagination or "load more" already limits the list size

---

## 📊 Visual Diagram

```
  Data: 10,000 items               DOM (what actually exists)
  ┌──────────────┐
  │ item 0       │
  │ ...          │                 ┌────────────────────┐  ← scroll container (300px)
  │ item 120     │  ── overscan ─▶ │ row 120 (buffer)   │
  │ item 121     │ ┐               │ row 121  ┐         │
  │ item 122     │ │ visible       │ row 122  │ visible │
  │ ...          │ │ window        │ ...      │ window  │
  │ item 130     │ ┘               │ row 130  ┘         │
  │ item 131     │  ── overscan ─▶ │ row 131 (buffer)   │
  │ ...          │                 └────────────────────┘
  │ item 9999    │                 Spacer height = 10,000 x rowHeight (fake scrollbar)
  └──────────────┘

  Scroll event → new start/end index → re-render ~12 rows → DOM nodes reused
```

Re-render behavior: each scroll tick changes the visible range, so the list re-renders its small set of rows. Wrapping rows in `memo` skips rows whose props did not change. Performance impact: render cost drops from O(n) to O(visible rows).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Virtualization / windowing | Render only visible items | सिर्फ़ दिखने वाली items render करना |
| Viewport | The visible scroll area | दिखने वाला scroll क्षेत्र |
| Overscan | Extra rows rendered off-screen | Screen के बाहर extra rendered rows |
| rowHeight | Height of each row (fixed or function) | हर row की ऊँचाई |
| Spacer | Tall inner element that makes the scrollbar | Scrollbar बनाने वाला ऊँचा inner element |
| Dynamic height | Rows with different heights, measured at runtime | अलग-अलग ऊँचाई वाली rows |
| DOM nodes | Elements in the page tree | Page tree के elements |
| TanStack Virtual | Headless virtualization hooks | Headless virtualization hooks |

---

## ⚡ 3-Line Summary
**English:**
1. Virtualization renders only the visible rows plus overscan, so DOM size stays small for huge lists.
2. `react-window` gives `List`/`Grid` components; always apply the row `style` and keep rows stable (module level, `memo`).
3. Skip it for short lists, and remember trade-offs: no native Ctrl+F and extra accessibility work.

**Hindi:**
1. Virtualization सिर्फ़ दिखने वाली rows और overscan render करता है, इसलिए बड़ी lists में भी DOM छोटा रहता है।
2. `react-window` `List`/`Grid` देता है; row का `style` हमेशा लगाओ और rows को stable रखो (module level, `memo`)।
3. छोटी lists में इसे मत लगाओ, और trade-offs याद रखो: native Ctrl+F नहीं चलता और accessibility पर extra काम लगता है।

---

## ➡️ Next Topic
**128. Image Optimization in React** — बड़ी images page को सबसे ज़्यादा धीमा करती हैं। lazy loading, responsive `srcset`, modern formats (WebP/AVIF) और Next.js `<Image>` से इसे कैसे ठीक करें।
