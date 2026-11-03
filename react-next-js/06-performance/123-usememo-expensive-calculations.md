# 123. useMemo — Expensive Calculations
# हिंदी में: useMemo — भारी Calculations को Cache करना

---

## 🔵 Simple Definition (English)
**`useMemo(fn, deps)`** caches the **result** of a calculation between renders. React re-runs `fn` only when a value in `deps` changes; otherwise it returns the previously calculated value. It is for expensive work and for keeping object/array references stable.

## 🔵 सरल परिभाषा (Hindi)
**`useMemo(fn, deps)`** renders के बीच किसी calculation का **result** cache करता है। React `fn` को तभी दोबारा चलाता है जब `deps` की कोई value बदले; वरना पिछला result दे देता है। यह भारी काम और object/array की reference stable रखने के लिए है।

---

## 🔴 Problem it Solves

Every render runs the whole component function again, including heavy calculations (filtering and sorting 10,000 rows, building chart data). If an unrelated state changes (a modal opens), the heavy work repeats for no reason and the UI feels slow. Also, objects created in render (`{}` or `[]`) get a new identity each time, which breaks `memo` and effect dependencies.

```jsx
// PROBLEM: sorting 10,000 items on EVERY render, even when only `open` changed
function Orders({ orders }) {
  const [open, setOpen] = useState(false);
  const sorted = [...orders].sort((a, b) => b.total - a.total);   // runs on each render
  return /* ... */ null;
}
// SOLUTION: const sorted = useMemo(() => [...orders].sort(...), [orders]);
```

## 🔴 यह क्यों बना? (Hindi)
हर render पर पूरा component function दोबारा चलता है, उसकी भारी calculations समेत (10,000 rows filter और sort करना, chart data बनाना)। कोई अलग state बदले (modal खुले) तब भी भारी काम बेवजह दोहराया जाता है और UI धीमा लगता है। साथ ही render में बने objects (`{}` या `[]`) की identity हर बार नई होती है, जिससे `memo` और effect dependencies टूटते हैं। `useMemo` दोनों समस्याएँ हल करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → const value = useMemo(() => compute(a, b), [a, b])
Step 2 → First render: React calls the function and stores { value, deps }
Step 3 → Next render: React compares new deps with stored deps using Object.is
Step 4 → All equal → return the stored value (function NOT called)
Step 5 → Any different → call the function again, store the new value and deps
Step 6 → Component unmount → cache discarded (it is not shared between components)

Rules:
  - function must be PURE (no side effects, no setState)
  - include every reactive value you read inside the function in deps
  - React may drop the cache in rare cases (e.g. offscreen); treat useMemo as an optimization, not a guarantee
  - Strict Mode (dev) calls your function twice to find impurity
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → const value = useMemo(() => compute(a, b), [a, b])
Step 2 → पहला render: React function चलाता है और { value, deps } store करता है
Step 3 → अगला render: React नए deps की stored deps से Object.is द्वारा तुलना करता है
Step 4 → सब बराबर → stored value लौटाओ (function NOT called)
Step 5 → कोई भी अलग → function दोबारा चलाओ, नई value और deps store करो
Step 6 → Component unmount → cache खत्म (यह components के बीच share नहीं होता)

Rules:
  - function PURE होना चाहिए (कोई side effect या setState नहीं)
  - function के अंदर पढ़ी गई हर reactive value deps में डालो
  - React कभी-कभी cache हटा सकता है (जैसे offscreen); useMemo को optimization समझो, guarantee नहीं
  - Strict Mode (dev) में impurity पकड़ने के लिए function दो बार चलता है
```

---

## 🟡 Real World Example
**Zomato restaurant list:** A page has 2,000 restaurants, a sort dropdown (rating, delivery time, cost) and a "filters" side panel that opens and closes. Opening the panel changes unrelated state. With `useMemo`, sorting and filtering are recomputed only when the restaurants, the sort option or the filters change, so opening the panel is instant.

## 🟡 Real Example Hindi mein
**Zomato restaurant list:** Page पर 2,000 restaurants, एक sort dropdown (rating, delivery time, cost) और "filters" side panel है जो खुलता-बंद होता है। Panel खोलने से unrelated state बदलती है। `useMemo` के साथ sort और filter सिर्फ तब दोबारा होते हैं जब restaurants, sort option या filters बदलें, इसलिए panel तुरंत खुलता है।

---

## 💻 Code Example — Basic

```jsx
// Basic useMemo: skip a slow calculation when unrelated state changes
import { useState, useMemo } from 'react';
import { createRoot } from 'react-dom/client';

function slowSum(n) {                                   // intentionally slow function
  console.log('slowSum running');                       // proves when it runs
  let total = 0;
  for (let i = 0; i < n * 1_000_000; i++) total += i;   // heavy loop
  return total;
}

function App() {
  const [n, setN] = useState(5);                        // input of the calculation
  const [dark, setDark] = useState(false);              // unrelated state

  const result = useMemo(() => slowSum(n), [n]);        // recomputed only when n changes

  return (
    <div style={{ background: dark ? '#222' : '#fff', color: dark ? '#fff' : '#000' }}>
      <button onClick={() => setN(n + 1)}>n = {n}</button>         {/* triggers slowSum */}
      <button onClick={() => setDark(!dark)}>Toggle theme</button>  {/* does NOT trigger slowSum */}
      <p>Result: {result}</p>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: derived data pipeline (filter → sort → group) + stable object for a memoized child
import { useState, useMemo, memo } from 'react';
import { createRoot } from 'react-dom/client';

const RESTAURANTS = Array.from({ length: 3000 }, (_, i) => ({
  id: i,
  name: `Restaurant ${i}`,
  rating: 3 + ((i * 7) % 20) / 10,                       // 3.0 .. 4.9
  cuisine: ['North Indian', 'Chinese', 'South Indian', 'Pizza'][i % 4],
  deliveryMin: 20 + (i % 40),
}));

// memo child: re-renders only when `stats` reference changes
const StatsBar = memo(function StatsBar({ stats }) {
  console.log('StatsBar render');
  return <p>{stats.count} results, avg rating {stats.avg.toFixed(2)}</p>;
});

function RestaurantList() {
  const [cuisine, setCuisine] = useState('All');          // filter state
  const [sortBy, setSortBy] = useState('rating');         // sort state
  const [panelOpen, setPanelOpen] = useState(false);      // unrelated UI state

  // Step 1: filter (depends on cuisine only)
  const filtered = useMemo(
    () => RESTAURANTS.filter((r) => cuisine === 'All' || r.cuisine === cuisine),
    [cuisine]
  );

  // Step 2: sort a COPY (never mutate memoized arrays); depends on filtered + sortBy
  const sorted = useMemo(() => {
    const copy = [...filtered];                           // .sort mutates, so copy first
    copy.sort((a, b) => sortBy === 'rating' ? b.rating - a.rating : a.deliveryMin - b.deliveryMin);
    return copy;
  }, [filtered, sortBy]);

  // Step 3: stable object for the memoized child
  const stats = useMemo(() => ({
    count: sorted.length,
    avg: sorted.reduce((s, r) => s + r.rating, 0) / (sorted.length || 1),
  }), [sorted]);

  return (
    <div>
      <select value={cuisine} onChange={(e) => setCuisine(e.target.value)}>
        {['All', 'North Indian', 'Chinese', 'South Indian', 'Pizza'].map((c) => <option key={c}>{c}</option>)}
      </select>
      <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
        <option value="rating">Rating</option>
        <option value="time">Delivery time</option>
      </select>
      <button onClick={() => setPanelOpen(!panelOpen)}>Filters</button>   {/* no recomputation */}
      {panelOpen && <aside>Filter panel</aside>}
      <StatsBar stats={stats} />                                            {/* skipped when panel toggles */}
      <ul>{sorted.slice(0, 50).map((r) => <li key={r.id}>{r.name} ★{r.rating}</li>)}</ul>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<RestaurantList />);
```

Re-render behavior: toggling the panel re-renders `RestaurantList`, but `filtered`, `sorted` and `stats` return the cached values, and `StatsBar` is skipped because `stats` kept the same reference. Performance impact: you save the O(n log n) sort on every unrelated render; the cost of `useMemo` itself is a deps comparison and some memory.

---

## 🟠 Next.js Connection

In Server Components do the heavy filtering/sorting on the server (once per request or cached), and send only the needed rows to the browser. `useMemo` is a client hook, so use it only for work that depends on client state (typed filters, selected sort).

```jsx
// app/restaurants/page.jsx (Server Component): heavy work happens here, no useMemo needed
import RestaurantsClient from './RestaurantsClient';
import { getRestaurants } from '@/lib/restaurants';          // hypothetical data helper

export default async function Page() {
  const all = await getRestaurants();                         // server-side fetch
  const top = all.sort((a, b) => b.rating - a.rating).slice(0, 200); // done once on the server
  return <RestaurantsClient restaurants={top} />;             // ship fewer rows to the browser
}
```

```jsx
// app/restaurants/RestaurantsClient.jsx
'use client';                                                 // interactive sorting stays on the client
import { useMemo, useState } from 'react';

export default function RestaurantsClient({ restaurants }) {
  const [q, setQ] = useState('');
  const visible = useMemo(                                    // cheap client filter keyed on q + props
    () => restaurants.filter((r) => r.name.toLowerCase().includes(q.toLowerCase())),
    [restaurants, q]
  );
  return (
    <>
      <input value={q} onChange={(e) => setQ(e.target.value)} />
      <ul>{visible.map((r) => <li key={r.id}>{r.name}</li>)}</ul>
    </>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Wrong or missing dependencies (stale results)
✅ **Correct:** List every reactive value used inside; use the `react-hooks/exhaustive-deps` lint rule

```jsx
// Wrong: `sortBy` is used but not listed → sorting never updates
const sorted = useMemo(() => sortList(items, sortBy), [items]);          // ❌ stale on sortBy change

// Right
const sorted2 = useMemo(() => sortList(items, sortBy), [items, sortBy]); // ✅
```

❌ **Mistake 2:** Mutating the input array inside `useMemo`
✅ **Correct:** Copy first; `sort`, `reverse` and `splice` mutate

```jsx
// Wrong: mutates the `items` prop and silently breaks other components
const sorted = useMemo(() => items.sort((a, b) => a.p - b.p), [items]);  // ❌ in-place sort

// Right
const sorted3 = useMemo(() => [...items].sort((a, b) => a.p - b.p), [items]); // ✅ copy
// (ES2023 alternative in modern runtimes: items.toSorted(...) returns a copy)
```

❌ **Mistake 3:** Using `useMemo` for side effects or for trivial work
✅ **Correct:** Side effects go in `useEffect`; do not memoize cheap math

```jsx
// Wrong: fetch inside useMemo (impure, may run twice or be dropped)
const data = useMemo(() => fetch('/api').then((r) => r.json()), []);     // ❌ side effect

// Wrong: memoizing a + b
const total = useMemo(() => a + b, [a, b]);                              // ❌ overhead > benefit

// Right
const total2 = a + b;                                                    // ✅ just compute
```

---

## 🧠 Tricky Interview Question

```jsx
function App() {
  const [n, setN] = useState(0);
  const obj = useMemo(() => ({ value: 1 }), []);
  useEffect(() => { console.log('effect'); }, [obj]);
  return <button onClick={() => setN(n + 1)}>{n}</button>;
}
```
**Answer:** `effect` is logged **once** on mount (twice in dev because Strict Mode double-invokes effects), and not on button clicks. `useMemo` with `[]` returns the same object reference every render, so `Object.is(prev, next)` is true and the effect does not re-run. Without `useMemo`, `obj` would be a new object each render and the effect would run after every click. Note: React may in rare cases discard memoized values, so never put logic correctness (only performance) on `useMemo`.

---

## ⚫ Interview Questions + Answers

Q1: What is `useMemo` and when do you use it?
A1: It caches a calculated value between renders and recomputes only when dependencies change. Use it for expensive derived data and for stable object/array references passed to `memo` components or hooks' dependency arrays.

Q2: `useMemo` vs `useCallback`?
A2: `useMemo` caches the **return value** of a function; `useCallback(fn, deps)` caches the **function itself**. `useCallback(fn, deps)` equals `useMemo(() => fn, deps)`.

Q3: Does `useMemo` guarantee the function will not re-run?
A3: No. It is a performance hint. React can discard the cache (for memory or offscreen reasons). Your code must work correctly even if the function runs again.

Q4: How do you decide something is "expensive"?
A4: Measure. React docs suggest checking if a single calculation takes ~1 ms or more (use `console.time` or the Profiler with CPU throttling). Also consider the size of the data and how often the component renders.

Q5: Can `useMemo` return JSX?
A5: Yes, memoized elements can skip re-rendering that subtree because the element reference is the same. This is a pattern similar to `memo`, but usually `memo` or moving state down is cleaner.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Filtering, sorting or grouping large lists
- A computed object/array is passed to a `memo` child or used in a dependency array
- The Profiler shows the calculation is a real bottleneck

❌ **Avoid when:**
- The calculation is cheap (simple math, string concat)
- Dependencies change on nearly every render (cache never hits)
- You can fix the problem by moving state down or changing component structure

---

## 📊 Visual Diagram

```
 render 1: deps [items, "rating"]  ──► compute() ──► store {value A, deps}
 render 2: deps [items, "rating"]  ──► Object.is all equal ──► return A  (compute skipped)
 render 3: deps [items, "time"]    ──► "time" !== "rating"   ──► compute() ──► store {value B, deps}

 Parent state `panelOpen` toggles ──► component re-renders ──► useMemo deps same ──► cached value
                                                                (no heavy work)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| useMemo | Cache a computed value | Calculated value को cache करना |
| Dependency array | Values that trigger recomputation | Recompute करने वाली values की list |
| Memoization | Remembering results of earlier work | पुराने result को याद रखना |
| Derived data | Data calculated from state/props | State/props से निकला data |
| Pure function | Same input, same output, no side effects | बिना side effect वाला function |
| Referential stability | Same reference across renders | Renders में वही reference |
| Strict Mode | Dev checks that double-run code | Dev में code दो बार चलाने वाला check |
| Bottleneck | The slowest part of a system | सबसे धीमा हिस्सा |

---

## ⚡ 3-Line Summary
**English:**
1. `useMemo` caches a computed value until its dependencies change.
2. Use it for heavy derived data and stable references; keep the function pure and deps complete.
3. Measure first; it is an optimization hint, not a guarantee, and cheap work needs no memo.

**Hindi:**
1. `useMemo` computed value को तब तक cache रखता है जब तक dependencies न बदलें।
2. भारी derived data और stable references के लिए इस्तेमाल करो; function pure और deps पूरे रखो।
3. पहले measure करो; यह optimization hint है, guarantee नहीं, और सस्ते काम को memo नहीं चाहिए।

---

## ➡️ Next Topic
**124. useCallback — Stable References** — `useMemo` values को cache करता है, `useCallback` functions को। `memo` वाले children को बचाने के लिए दोनों साथ चलते हैं।
