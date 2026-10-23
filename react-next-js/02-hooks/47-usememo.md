# 47. useMemo — Complete Guide
# हिंदी में: useMemo — Expensive Calculations याद रखना

---

## 🔵 Simple Definition (English)
`useMemo` **memoizes (caches) the result of an expensive calculation**. It only recomputes the value when its dependencies change. Between renders, if deps haven't changed, it returns the cached result without running the function again.

## 🔵 सरल परिभाषा (Hindi)
`useMemo` **expensive calculation का result memoize (cache) करता है**। Value को सिर्फ तब recompute करता है जब dependencies बदलें। Re-renders के बीच, अगर deps नहीं बदले, cached result return करता है बिना function दोबारा run किए।

---

## 🔴 Problem it Solves

```jsx
// PROBLEM: Expensive calculation runs on EVERY render
function ProductList({ products, searchTerm, sortBy }) {
  // This runs even when only sortBy changes!
  // filteredProducts recalculated even if products/searchTerm same
  const filteredProducts = products
    .filter(p => p.name.includes(searchTerm))  // O(n) search
    .sort((a, b) => a[sortBy] - b[sortBy]);    // O(n log n) sort

  return <ul>{filteredProducts.map(p => <li key={p.id}>{p.name}</li>)}</ul>;
}
// With 10,000 products: recalculating every render (including unrelated state changes) = slow!
```

## 🔴 यह क्यों बना? (Hindi)
```jsx
// PROBLEM: Expensive calculation हर render पर run होती है
// Even जब unrelated state बदले (e.g., button hover)
// useMemo: सिर्फ तब recalculate करो जब products या searchTerm बदले
// बाकी renders पर cached result return करो
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → First render: useMemo runs the function, stores result
         memo = useMemo(() => expensiveCalc(a, b), [a, b])
         runs expensiveCalc(a, b) → stores result

Step 2 → Re-render: React checks dependencies
         Old deps: [a=5, b=10]
         New deps: [a=5, b=10] → SAME → return cached result ✅
                   [a=6, b=10] → DIFFERENT → rerun function

Step 3 → If deps changed: rerun function, store new result
         Next render: use new cached result

KEY: useMemo skips recomputation when deps are same
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → First render: useMemo function run करता है, result store करता है

Step 2 → Re-render: React dependencies check करता है
         Old deps same → cached result return करता है ✅
         Deps changed → function rerun करता है

Step 3 → Deps बदले: function rerun, नया result store
         अगला render: नया cached result use

KEY: useMemo recomputation skip करता है जब deps same हों
```

---

## 🟡 Real World Example
**Amazon Search + Filter:** You have 50,000 products. User types in search box (state changes on every keystroke). Without `useMemo`, the filter+sort runs on EVERY keystroke — laggy. With `useMemo([products, searchTerm, sortBy])`, the filter only reruns when those values change — smooth UX even while typing.

## 🟡 Real Example Hindi mein
**Amazon Search + Filter:** 50,000 products हैं। User search box में type करता है (हर keystroke पर state change)। `useMemo` के बिना, filter+sort हर keystroke पर run होती है — laggy। `useMemo([products, searchTerm, sortBy])` से filter सिर्फ तब rerun होता है जब वो values बदलें — smooth UX।

---

## 💻 Code Example — Basic

```jsx
import { useState, useMemo } from 'react';

// ── BASIC useMemo ─────────────────────────
function ProductCatalog({ products }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('price');
  const [cartCount, setCartCount] = useState(0); // unrelated state

  // WITHOUT useMemo: recalculates on EVERY render
  // (even when cartCount changes — irrelevant to filtering!)

  // WITH useMemo: only recalculates when products/searchTerm/sortBy change
  const filteredProducts = useMemo(() => {
    console.log('Filtering...'); // only logs when deps change
    return products
      .filter(p =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase())
      )
      .sort((a, b) => {
        if (sortBy === 'price') return a.price - b.price;
        if (sortBy === 'rating') return b.rating - a.rating;
        return a.name.localeCompare(b.name);
      });
  }, [products, searchTerm, sortBy]); // only these 3 trigger recompute

  return (
    <div>
      <input
        value={searchTerm}
        onChange={e => setSearchTerm(e.target.value)}
        placeholder="Search..."
      />

      <select value={sortBy} onChange={e => setSortBy(e.target.value)}>
        <option value="price">Sort by Price</option>
        <option value="rating">Sort by Rating</option>
        <option value="name">Sort by Name</option>
      </select>

      {/* Clicking cart doesn't retrigger the filter! */}
      <button onClick={() => setCartCount(c => c + 1)}>
        Cart ({cartCount})
      </button>

      <ul>
        {filteredProducts.map(p => (
          <li key={p.id}>{p.name} — ₹{p.price}</li>
        ))}
      </ul>
    </div>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { useState, useMemo, useCallback, memo } from 'react';

// ── MEMOIZING EXPENSIVE COMPUTATION ──────
function DataAnalytics({ transactions }) {
  const [year, setYear] = useState(2024);
  const [metric, setMetric] = useState('revenue');

  // Expensive: process thousands of transactions
  const analytics = useMemo(() => {
    console.log('Computing analytics...');

    const filtered = transactions.filter(t => t.year === year);

    return {
      total: filtered.reduce((sum, t) => sum + t.amount, 0),
      average: filtered.length > 0
        ? filtered.reduce((sum, t) => sum + t.amount, 0) / filtered.length
        : 0,
      max: Math.max(...filtered.map(t => t.amount)),
      min: Math.min(...filtered.map(t => t.amount)),
      count: filtered.length,
      byMonth: filtered.reduce((acc, t) => {
        acc[t.month] = (acc[t.month] || 0) + t.amount;
        return acc;
      }, {}),
    };
  }, [transactions, year]); // 'metric' not in deps — doesn't affect computation

  // The displayed metric changes without recomputing analytics
  const displayValue = analytics[metric] || 0;

  return (
    <div>
      <select value={year} onChange={e => setYear(Number(e.target.value))}>
        <option value={2024}>2024</option>
        <option value={2023}>2023</option>
      </select>

      <select value={metric} onChange={e => setMetric(e.target.value)}>
        <option value="total">Total</option>
        <option value="average">Average</option>
        <option value="max">Max</option>
        <option value="count">Count</option>
      </select>

      <h2>₹{displayValue.toFixed(2)}</h2>
    </div>
  );
}

// ── useMemo FOR STABLE OBJECT REFERENCE ──
// This is actually the most common use case in real apps!

// Problem: object created inline is a new reference every render
// This causes React.memo'd child to always re-render

const UserCard = memo(function UserCard({ user }) {
  console.log('UserCard rendered:', user.name);
  return <div>{user.name} — {user.role}</div>;
});

function Dashboard({ userId, userRole }) {
  const [count, setCount] = useState(0); // unrelated state

  // WRONG: new object every render → UserCard always re-renders!
  // const user = { id: userId, name: 'Aditya', role: userRole };

  // CORRECT: stable reference — only changes when userId/userRole change
  const user = useMemo(
    () => ({ id: userId, name: 'Aditya', role: userRole }),
    [userId, userRole]
  );

  return (
    <div>
      <UserCard user={user} />          {/* won't re-render on count change! */}
      <button onClick={() => setCount(c => c + 1)}>Count: {count}</button>
    </div>
  );
}

// ── WHEN NOT TO useMemo ───────────────────
// DON'T useMemo for simple calculations — overhead of memoization > benefit
function BadUseMemo({ a, b }) {
  // OVER-OPTIMIZATION: useMemo overhead for trivial add!
  const sum = useMemo(() => a + b, [a, b]); // ❌ overkill

  // Just compute it:
  const sum2 = a + b; // ✅ simple, no overhead

  return <div>{sum2}</div>;
}
```

---

## 🟠 Next.js Connection

```jsx
// useMemo works in Next.js Client Components
// Server Components: no useMemo needed — computation runs once on server

// Server Component (no useMemo — runs once):
async function ProductsPage({ searchParams }) {
  const allProducts = await fetchProducts();
  // This filter runs ONCE on server — no re-render optimization needed
  const filtered = allProducts.filter(p =>
    p.name.includes(searchParams.search || '')
  );
  return <ProductList products={filtered} />;
}

// Client Component (useMemo useful for interactive filtering):
'use client';
function InteractiveFilter({ initialProducts }) {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');

  // useMemo: client-side filtering without hitting server
  const filtered = useMemo(() => {
    return initialProducts.filter(p => {
      const matchesSearch = p.name.toLowerCase().includes(search.toLowerCase());
      const matchesCategory = category === 'all' || p.category === category;
      return matchesSearch && matchesCategory;
    });
  }, [initialProducts, search, category]);

  return (
    <div>
      <input value={search} onChange={e => setSearch(e.target.value)} />
      {filtered.map(p => <ProductCard key={p.id} product={p} />)}
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using useMemo for everything (premature optimization)
```jsx
// WRONG: memoizing a trivial computation
const doubled = useMemo(() => count * 2, [count]); // ❌ unnecessary overhead

// CORRECT: just compute it
const doubled = count * 2; // ✅ no overhead, same performance for simple ops
```

❌ **Mistake 2:** Missing dependencies
```jsx
// WRONG: stale value because of missing dep
function Component({ multiplier }) {
  const [count, setCount] = useState(0);

  const result = useMemo(
    () => count * multiplier,
    [count] // ❌ missing multiplier! result stale when multiplier changes
  );

  return <div>{result}</div>;
}

// CORRECT:
const result = useMemo(
  () => count * multiplier,
  [count, multiplier] // ✅ all values used in function
);
```

❌ **Mistake 3:** Confusing useMemo (value) with useCallback (function)
```jsx
// useMemo → memoizes a VALUE
const memoizedValue = useMemo(() => computeExpensiveThing(), [dep]);

// useCallback → memoizes a FUNCTION
const memoizedFunction = useCallback(() => doSomething(), [dep]);

// They're equivalent:
// useCallback(fn, deps) === useMemo(() => fn, deps)
```

---

## 🧠 Tricky Interview Question

```jsx
function App() {
  const [count, setCount] = useState(0);

  const value = useMemo(() => {
    return { number: count };
  }, [count]);

  const sameValue = useMemo(() => {
    return { number: count };
  }, [count]);

  console.log(value === sameValue); // What logs?

  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}
```
**Answer:** `false`. Even though both `useMemo` calls have the same deps and computation, they create **different object instances** — `value` and `sameValue` are separate objects with the same contents. `===` compares references, not values. `useMemo` guarantees the SAME reference between renders when deps don't change — but two separate `useMemo` calls always produce different references.

---

## ⚫ Interview Questions + Answers

**Q1: What is useMemo and when should you use it?**
A1: `useMemo(fn, deps)` caches the return value of `fn`, recomputing only when `deps` change. Use it when: (1) The computation is genuinely expensive (filtering/sorting large arrays, complex math). (2) The result is passed as prop to a `memo()`-wrapped component and needs stable reference. (3) The value is used as a dependency in other hooks (useEffect, useCallback). Don't use it for simple calculations.

**Q2: What is the difference between useMemo and useCallback?**
A2: `useMemo(() => computeValue(), [deps])` memoizes a **value** (any type — array, object, number, string). `useCallback(() => doSomething(), [deps])` memoizes a **function** — equivalent to `useMemo(() => () => doSomething(), [deps])`. Use useMemo for computed values, useCallback for event handlers/callbacks passed to children.

**Q3: Does useMemo guarantee the cached value is always returned?**
A3: No. React may discard cached values in certain situations (low memory, future features like Offscreen). `useMemo` is a performance optimization hint, not a semantic guarantee. Don't rely on it to prevent a side effect from running — if the computation has side effects, put them in `useEffect` instead.

**Q4: What is referential equality and why does it matter for useMemo?**
A4: Referential equality (`===`) for objects/arrays compares memory addresses, not content. `{a:1} === {a:1}` is `false` (different objects). React uses referential equality to check if props changed (for `React.memo`) and if deps changed (for hooks). `useMemo` returns the same object reference when deps don't change — this allows `React.memo` and other hooks to correctly detect "no change."

**Q5: How do you profile whether useMemo is actually helping?**
A5: React DevTools Profiler shows render times. Record interactions without `useMemo`, then with — compare times. Also: check if the computation is actually slow (> 1ms) using `console.time`/`console.timeEnd` or `performance.now()`. If the computation takes < 0.05ms, `useMemo` overhead (tracking deps, checking equality) probably costs more than it saves.

---

## 🔷 When to Use + When Not to Use
✅ **Use useMemo when:**
- Filtering/sorting large arrays (> 1000 items)
- Complex mathematical computation on every render
- Stable object reference needed for `React.memo` child
- Value used as dependency in `useEffect` or `useCallback`

❌ **Skip useMemo when:**
- Simple computations (arithmetic, string concat, small arrays)
- Computation is fast (< 0.1ms)
- You're just guessing it might be slow (profile first!)
- Every single value in the component (over-optimization)

---

## 📊 Visual Diagram

```
useMemo FLOW:
───────────────────────────────────────────────
  Render 1: useMemo runs fn(), stores result
            deps: [products=A, search="pi"]
            result: [Pizza, Pineapple]  ← cached

  Render 2: deps: [products=A, search="pi"] ← SAME
            → return cached [Pizza, Pineapple] ✅ (fn not called!)

  Render 3: deps: [products=A, search="bu"] ← CHANGED
            → fn() reruns
            → result: [Burger]  ← new cache

  Render 4: unrelated state change (cartCount++)
            deps: [products=A, search="bu"] ← SAME
            → return cached [Burger] ✅ (fn not called!)

WHEN TO useMemo:
───────────────────────────────────────────────
  Computation Cost:     Low ──────────────► High
  useMemo benefit:       ❌ Not worth it    ✅ Use it!

  Examples:
  count * 2              → ❌ skip
  items.length            → ❌ skip
  array.filter (< 100)    → ❌ probably skip
  array.filter (> 1000)   → ✅ useMemo
  matrix multiplication   → ✅ useMemo
  deep tree parsing       → ✅ useMemo
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Memoization | Cache result, skip recomputation | Result cache करना, recompute skip करना |
| Referential equality | Same memory address (`===`) | Same memory address |
| Stale value | Old cached value, not updated | पुरानी cached value, update नहीं हुई |
| Recompute | Run the calculation again | Calculation दोबारा run करना |
| Dependency | Value that triggers recomputation | Recomputation trigger करने वाली value |
| Over-optimization | Adding optimization where not needed | जहाँ ज़रूरत न हो वहाँ optimization |

---

## ⚡ 3-Line Summary
**English:**
1. `useMemo(fn, deps)` caches fn's return value — recomputes only when deps change, returns cache otherwise.
2. Two real use cases: (1) expensive computations (filtering 10k+ items), (2) stable object reference for `React.memo` children.
3. Don't overuse — `useMemo` has overhead; simple calculations are faster without it. Profile before optimizing.

**Hindi:**
1. `useMemo(fn, deps)` fn का return value cache करता है — deps बदलने पर recompute, वरना cache return।
2. दो real use cases: (1) expensive computations (10k+ items filter), (2) `React.memo` children के लिए stable object reference।
3. Overuse मत करो — `useMemo` का overhead है; simple calculations इसके बिना faster। Optimize करने से पहले profile करो।

---

## ➡️ Next Topic
**48. useCallback — Complete Guide** — Functions को memoize करना — child components को unnecessary re-renders से बचाना।
