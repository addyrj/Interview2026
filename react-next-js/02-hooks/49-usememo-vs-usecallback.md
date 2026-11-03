# 49. useMemo vs useCallback
# हिंदी में: useMemo बनाम useCallback — Value cache करें या Function?

---

## 🔵 Simple Definition (English)
Both hooks **cache something between renders** and recompute it only when dependencies change. `useMemo(() => compute(), deps)` caches the **result** (a value, object or array). `useCallback(fn, deps)` caches the **function itself**. In fact `useCallback(fn, deps)` is the same as `useMemo(() => fn, deps)`.

## 🔵 सरल परिभाषा (Hindi)
दोनों hooks **renders के बीच कोई चीज़ cache** करते हैं और dependencies बदलने पर ही दोबारा बनाते हैं। `useMemo(() => compute(), deps)` **result** (value, object या array) cache करता है। `useCallback(fn, deps)` **function को ही** cache करता है। असल में `useCallback(fn, deps)` और `useMemo(() => fn, deps)` एक ही चीज़ हैं।

---

## 🔴 Problem it Solves

On every render, a component function runs again, so it creates new objects, arrays and functions, even if they look the same. This causes two problems:

1. **Expensive calculations** (filtering and sorting 10,000 products) run on every keystroke, even when their inputs did not change.
2. **Unstable references:** a new `{}` or `() => {}` is `!==` the previous one. A `memo` child, a `useEffect` dependency array, or a context value sees a "change" and re-renders or re-runs for no reason.

```jsx
// PROBLEM 1: heavy work on every render, even when only `theme` changed
function Products({ products, query, theme }) {
  const filtered = products.filter((p) => p.name.includes(query)).sort(byPrice); // runs every render
  return <List items={filtered} />;
}

// PROBLEM 2: new function each render → memo(Child) can never skip
function Parent() {
  const [n, setN] = useState(0);
  const onSelect = (id) => console.log(id);          // new function identity on every render
  return <MemoChild onSelect={onSelect} />;          // MemoChild re-renders on every n change
}
```

## 🔴 यह क्यों बना? (Hindi)
हर render पर component function फिर से चलता है, इसलिए नई objects, arrays और functions बनती हैं, चाहे वे एक जैसी दिखें। इससे दो समस्याएँ आती हैं:

1. **भारी calculations** (10,000 products को filter और sort करना) हर keystroke पर चलते हैं, भले ही उनके inputs नहीं बदले।
2. **अस्थिर references:** नया `{}` या `() => {}` पिछले वाले से `!==` होता है। `memo` वाला child, `useEffect` की dependency array या context value को "बदलाव" दिखता है और वे बेवजह re-render या re-run होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → First render: React runs your function (useMemo) or stores your function (useCallback)
Step 2 → React remembers the result/function AND the dependency array
Step 3 → Next render: React compares each dependency with the old one using Object.is
Step 4 → ALL equal → return the cached value/function (no computation, same reference)
Step 5 → ANY changed → run again (useMemo) / store the new function (useCallback)
Step 6 → The stable reference lets memo(Child), useEffect and Context skip unnecessary work

                useMemo                          useCallback
caches          the RETURN VALUE of fn           the FUNCTION fn itself
you write       useMemo(() => calc(a), [a])      useCallback((x) => doIt(x, a), [a])
returns         a value/object/array             a function
typical use     expensive calc, stable object    stable handler passed to memo child / effect dep

WARNING: both are performance hints. React may discard the cache (e.g., low memory), so the code must still be correct without them.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → पहला render: React आपका function चलाता है (useMemo) या function सहेजता है (useCallback)
Step 2 → React result/function और dependency array दोनों याद रखता है
Step 3 → अगला render: React हर dependency की पुरानी से Object.is से तुलना करता है
Step 4 → सब बराबर → cached value/function लौटाता है (कोई गणना नहीं, वही reference)
Step 5 → कोई भी बदला → फिर चलाता है (useMemo) / नया function सहेजता है (useCallback)
Step 6 → Stable reference से memo(Child), useEffect और Context बेवजह का काम छोड़ देते हैं

                useMemo                          useCallback
cache करता है    fn का RETURN VALUE               खुद FUNCTION fn
लिखते हैं         useMemo(() => calc(a), [a])      useCallback((x) => doIt(x, a), [a])
लौटाता है         value/object/array               function
आम उपयोग        भारी गणना, stable object          memo child / effect dep को दिया stable handler

चेतावनी: दोनों performance hints हैं। React cache हटा भी सकता है, इसलिए code इनके बिना भी सही होना चाहिए।
```

---

## 🟡 Real World Example
**Flipkart search results:** The page has 5,000 products in memory, a search box, and a theme toggle. Typing in the search box filters and sorts the list, which is heavy, so the filtered list is wrapped in `useMemo([products, query, sort])`. Toggling the theme re-renders the page, but the list is not recomputed. Each `ProductCard` is wrapped in `memo`, and the "Add to cart" handler passed to cards is wrapped in `useCallback`, so toggling the theme or typing does not re-render the 5,000 cards that did not change.

## 🟡 Real Example Hindi mein
**Flipkart search results:** Page में 5,000 products memory में हैं, एक search box और एक theme toggle है। Search box में typing list को filter और sort करती है, जो भारी है, इसलिए filtered list `useMemo([products, query, sort])` में है। Theme toggle से page re-render होता है, पर list दोबारा नहीं गिनी जाती। हर `ProductCard` `memo` में है, और cards को दिया "Add to cart" handler `useCallback` में है, इसलिए theme बदलने या typing से उन 5,000 cards का re-render नहीं होता जो बदले नहीं।

---

## 💻 Code Example — Basic

```jsx
// Side by side: useMemo caches a value, useCallback caches a function
import { useState, useMemo, useCallback, memo } from 'react';
import { createRoot } from 'react-dom/client';

// memo: skip rendering when props are shallow-equal
const Row = memo(function Row({ item, onAdd }) {
  console.log('Row render', item.name);               // watch which rows render
  return <li>{item.name} <button onClick={() => onAdd(item.id)}>Add</button></li>;
});

function App() {
  const [query, setQuery] = useState('');             // changes while typing
  const [dark, setDark] = useState(false);            // unrelated state
  const [cart, setCart] = useState([]);

  const products = useMemo(() => [                    // stable data for the demo
    { id: 1, name: 'Mouse' }, { id: 2, name: 'Keyboard' }, { id: 3, name: 'Monitor' },
  ], []);

  // useMemo: result cached; recomputed only when products or query change
  const visible = useMemo(() => {
    console.log('filtering...');                      // runs only when query/products change
    return products.filter((p) => p.name.toLowerCase().includes(query.toLowerCase()));
  }, [products, query]);

  // useCallback: same function identity until deps change ([] → never changes)
  const handleAdd = useCallback((id) => {
    setCart((prev) => [...prev, id]);                 // updater form, so no dependency on `cart`
  }, []);

  return (
    <div style={{ background: dark ? '#222' : '#fff' }}>
      <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search" />
      <button onClick={() => setDark(!dark)}>Toggle theme</button>   {/* Rows do NOT re-render here */}
      <ul>{visible.map((p) => <Row key={p.id} item={p} onAdd={handleAdd} />)}</ul>
      <p>Cart: {cart.length}</p>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

## 💻 Code Example — Advanced

```jsx
// Real world: stable objects for context and effects, expensive computations, and measuring first
import { createContext, useContext, useState, useMemo, useCallback, useEffect } from 'react';

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const [items, setItems] = useState([]);

  const add = useCallback((product) => {               // stable function identities
    setItems((prev) => {
      const found = prev.find((i) => i.id === product.id);
      return found
        ? prev.map((i) => (i.id === product.id ? { ...i, qty: i.qty + 1 } : i))
        : [...prev, { ...product, qty: 1 }];
    });
  }, []);

  const remove = useCallback((id) => setItems((p) => p.filter((i) => i.id !== id)), []);

  const total = useMemo(                               // derived value, recomputed on items change only
    () => items.reduce((s, i) => s + i.price * i.qty, 0),
    [items]
  );

  // Context value is an OBJECT: without useMemo it is new every render → ALL consumers re-render
  const value = useMemo(() => ({ items, total, add, remove }), [items, total, add, remove]);

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export const useCart = () => useContext(CartContext);

// Effect dependency: a stable function avoids re-subscribing on every render
export function useProductSearch(query) {
  const [results, setResults] = useState([]);

  const search = useCallback(async (q, signal) => {    // stable function (no outside deps)
    const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`, { signal });
    return res.json();
  }, []);

  useEffect(() => {
    if (!query) return;                                // nothing to search
    const ctrl = new AbortController();                // cancel stale requests
    search(query, ctrl.signal).then(setResults).catch(() => {});
    return () => ctrl.abort();
  }, [query, search]);                                 // `search` is stable → effect runs only on query change

  return results;
}

// Measure before memoizing: use the Profiler, or console.time around the calculation
export function ExpensiveList({ items, filter }) {
  const filtered = useMemo(() => {
    console.time('filter');                            // log duration in dev
    const out = items.filter((i) => i.tags.includes(filter));
    console.timeEnd('filter');
    return out;
  }, [items, filter]);
  return <p>{filtered.length} matches</p>;
}
```

---

## 🟠 Real App Integration

In Next.js, these hooks work only in **Client Components**. Server Components render once on the server, so they never need memoization. Before reaching for `useMemo`, ask: can this calculation move to the server (a Server Component, a database query, or `unstable_cache`/`cache`)? Also note that **React Compiler** (React 19 ecosystem, opt-in in Next.js 15 via `experimental.reactCompiler`, version-dependent) can add this memoization automatically at build time, so many new codebases write fewer manual `useMemo` and `useCallback` calls.

```jsx
// app/products/ProductFilter.jsx — heavy filtering belongs on the server when possible
// Server Component: no useMemo needed, runs once per request
export default async function ProductsPage({ searchParams }) {
  const { q = '' } = await searchParams;               // Next.js 15: searchParams is a Promise
  const products = await fetch(`https://api.example.com/products?q=${encodeURIComponent(q)}`, {
    next: { revalidate: 60 },                          // cache the response
  }).then((r) => r.json());
  return <ProductList products={products} />;          // client part only handles interaction
}
```

```jsx
// app/products/ProductList.jsx — Client Component with memoized interaction
'use client';
import { useMemo, useState } from 'react';

export default function ProductList({ products }) {
  const [sort, setSort] = useState('price');
  const sorted = useMemo(
    () => [...products].sort((a, b) => a[sort] - b[sort]),   // copy before sort, never mutate props
    [products, sort]
  );
  return (
    <>
      <select value={sort} onChange={(e) => setSort(e.target.value)}>
        <option value="price">Price</option><option value="rating">Rating</option>
      </select>
      <ul>{sorted.map((p) => <li key={p.id}>{p.name}</li>)}</ul>
    </>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** `useCallback` on a child that is NOT wrapped in `memo`
✅ **Correct:** Stable props help only if the receiver skips re-rendering on equal props

```jsx
// Wrong: useless. Child re-renders anyway whenever Parent renders
function Child({ onClick }) { return <button onClick={onClick}>Go</button>; }
function Parent() {
  const onClick = useCallback(() => {}, []);          // ❌ no benefit, extra work
  return <Child onClick={onClick} />;
}

// Right: pair with memo
const Child2 = memo(function Child2({ onClick }) { return <button onClick={onClick}>Go</button>; });
```

❌ **Mistake 2:** Wrong or missing dependencies (stale values)
✅ **Correct:** List every reactive value used inside (use the ESLint rule `react-hooks/exhaustive-deps`)

```jsx
// Wrong: `taxRate` is used but not listed → total never updates
const total = useMemo(() => price * (1 + taxRate), [price]);       // ❌ stale when taxRate changes

// Right
const total2 = useMemo(() => price * (1 + taxRate), [price, taxRate]);   // ✅
```

❌ **Mistake 3:** Memoizing everything "for performance"
✅ **Correct:** Memoize when you measured a slow calculation (>1 ms) or need reference stability

```jsx
// Wrong: the memo costs more than the work it saves
const doubled = useMemo(() => count * 2, [count]);                 // ❌ trivial calculation
const label = useCallback(() => 'Hi', []);                         // ❌ pointless

// Right
const doubled2 = count * 2;                                        // ✅ just compute it
```

❌ **Mistake 4:** Using `useMemo` to make a function (or `useCallback` for a value)
✅ **Correct:** `useMemo` must RETURN the value; `useCallback` takes the function directly

```jsx
// Wrong: onSave is the result of calling nothing; a function that returns undefined
const onSave = useMemo(() => { save(draft); }, [draft]);           // ❌ runs save() during render!

// Right
const onSave2 = useCallback(() => { save(draft); }, [draft]);      // ✅ function stored, run on click
```

---

## 🧠 Tricky Interview Question

```jsx
const Child = React.memo(function Child({ style, onClick }) {
  console.log('Child render');
  return <button style={style} onClick={onClick}>Child</button>;
});

function Parent() {
  const [n, setN] = React.useState(0);

  const style = React.useMemo(() => ({ color: 'red' }), []);
  const onClick = React.useCallback(() => console.log('clicked'), []);

  return (
    <>
      <button onClick={() => setN(n + 1)}>{n}</button>
      <Child style={style} onClick={onClick} />
      <Child style={{ color: 'red' }} onClick={() => console.log('clicked')} />
    </>
  );
}
```
Question: When `n` changes, which `Child` re-renders?

**Answer:** Only the **second** `Child` re-renders. The first gets the same `style` and `onClick` references from `useMemo` and `useCallback`, so `memo`'s shallow comparison passes and React skips it. The second gets a new object and a new function each render, so its props "changed" even though they look the same. Console on a click: `Child render` once (second child). On the initial mount it logs twice (both children).

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `useMemo` and `useCallback`?
A1: `useMemo` caches the return value of a function; `useCallback` caches the function itself. `useCallback(fn, deps)` equals `useMemo(() => fn, deps)`. Use `useMemo` for expensive values or stable objects/arrays, and `useCallback` for stable function props and effect dependencies.

Q2: When should you NOT use them?
A2: For cheap calculations, for props passed to non-memoized children, or when you have not measured a problem. Every memo has a cost (comparing dependencies, storing results, extra code to read). React docs call them performance optimizations, not a semantic guarantee.

Q3: What does the dependency array do?
A3: React compares each item with the previous render using `Object.is`. If all are equal it reuses the cached result; if any differ it recomputes. Missing deps create stale values; an empty array computes once per component instance.

Q4: Why does `React.memo` plus `useCallback` often appear together?
A4: `memo` skips re-rendering when props are shallow-equal. Functions are recreated on every render, so they always look "changed" unless wrapped in `useCallback`. Together they let a child skip rendering when nothing relevant changed.

Q5: Will React Compiler make `useMemo` and `useCallback` obsolete?
A5: Mostly for new code. The compiler memoizes components and values automatically at build time, so manual hooks are rarely needed, but they remain useful as escape hatches (for example, a value used as an effect dependency that must be stable). Version-dependent: the compiler is opt-in and works best on code that follows the Rules of React.

---

## 🔷 When to Use + When Not to Use
✅ **Use `useMemo` when:**
- A calculation is measurably slow (large filter/sort/aggregate)
- You pass an object/array to a `memo` child, effect dependency or context value and need a stable reference

✅ **Use `useCallback` when:**
- A function is passed to a `memo` child, or is a `useEffect`/`useMemo` dependency
- A custom hook returns functions that consumers may put in their dependency arrays

❌ **Avoid when:**
- The work is trivial, or the receiver is not memoized
- You can move the logic out of the component (module-level function/constant) or to the server
- You are using them to "fix" an infinite loop that really needs a dependency or design fix

---

## 📊 Visual Diagram

```
  RENDER 1                      RENDER 2 (deps same)             RENDER 3 (deps changed)
  ────────                      ────────────────────             ───────────────────────
  useMemo(fn,[a])               useMemo(fn,[a])                  useMemo(fn,[b])
   ├─ run fn() → R1             ├─ [a]==[a] ✔ → return R1        ├─ [b]≠[a] ✘ → run fn() → R2
   └─ cache R1, [a]             └─ (fn NOT called)               └─ cache R2, [b]

  useCallback(f,[a])            useCallback(f,[a])               useCallback(f,[b])
   └─ cache f1                  └─ return f1  (same reference)   └─ cache f2 (new reference)

  Parent re-renders ─▶ <MemoChild onClick={f1}> → props equal → SKIP render ✔
                       <MemoChild onClick={()=>…}> → new function → RENDER ✘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `useMemo` | Caches a computed value | गणना किए गए value को cache करता है |
| `useCallback` | Caches a function | Function को cache करता है |
| Dependency array | Values whose change invalidates the cache | जिनके बदलने पर cache हटता है |
| Referential equality | Same object in memory (`===`) | Memory में वही object |
| `React.memo` | Skips re-render if props are equal | Props बराबर होने पर re-render छोड़ता है |
| Memoization | Remembering a result for the same inputs | Same inputs पर result याद रखना |
| Stale value | Old value captured by a closure | Closure में फँसी पुरानी value |
| React Compiler | Auto-memoizing build tool | अपने आप memoize करने वाला build tool |

---

## ⚡ 3-Line Summary
**English:**
1. `useMemo` caches a computed value and `useCallback` caches a function; both recompute only when dependencies change.
2. They help for expensive calculations and for stable references passed to `memo` children, effects, and context.
3. Measure first, list all dependencies, and skip them for trivial work; the React Compiler can automate most of it.

**Hindi:**
1. `useMemo` गणना की value cache करता है और `useCallback` function; दोनों सिर्फ dependencies बदलने पर दोबारा बनते हैं।
2. ये भारी गणनाओं और `memo` children, effects व context को दिए stable references के लिए काम आते हैं।
3. पहले measure करो, सारी dependencies लिखो, और हल्के काम के लिए इन्हें छोड़ो; React Compiler इसे ज़्यादातर अपने आप कर सकता है।

---

## ➡️ Next Topic
**50. useLayoutEffect vs useEffect** — Values cache करना सीख लिया, अब देखो कि effects browser के paint से पहले या बाद में कब चलें, और flicker जैसी layout समस्याओं में कौन-सा चुनें।
