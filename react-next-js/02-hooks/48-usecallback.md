# 48. useCallback — Complete Guide
# हिंदी में: useCallback — Functions को Memoize करना

---

## 🔵 Simple Definition (English)
`useCallback` **memoizes a function** — it returns the same function reference between renders unless its dependencies change. This prevents child components (wrapped in `React.memo`) from re-rendering when the parent re-renders, because the function prop reference stays stable.

## 🔵 सरल परिभाषा (Hindi)
`useCallback` **एक function को memoize करता है** — यह renders के बीच same function reference return करता है जब तक dependencies नहीं बदलतीं। यह child components (`React.memo` wrapped) को unnecessary re-renders से बचाता है, क्योंकि function prop reference stable रहती है।

---

## 🔴 Problem it Solves

```jsx
// PROBLEM: Functions are re-created on every render!
// New function = new reference = React.memo thinks props changed → re-render!

function Parent() {
  const [count, setCount] = useState(0);

  const handleClick = () => {      // NEW function on every render!
    console.log('clicked');
  };

  return (
    <div>
      <ExpensiveChild onClick={handleClick} />  {/* re-renders on every Parent render! */}
      <button onClick={() => setCount(c => c + 1)}>Count: {count}</button>
    </div>
  );
}

const ExpensiveChild = React.memo(({ onClick }) => {
  console.log('ExpensiveChild rendered'); // logs on every count increment!
  return <button onClick={onClick}>Click me</button>;
});
// React.memo checks props by reference — handleClick is always new → always re-renders
```

## 🔴 यह क्यों बना? (Hindi)
```jsx
// PROBLEM: Functions हर render पर re-create होती हैं!
// नई function = नई reference = React.memo props changed समझे → re-render!

// useCallback: function को memoize करो
// Same deps → same function reference → React.memo no re-render ✅
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → First render: useCallback stores the function
         const fn = useCallback(() => doSomething(dep), [dep])
         Stores function in cache, returns it

Step 2 → Re-render: React checks deps
         Old deps: [dep=5]
         New deps: [dep=5] → SAME → return SAME function reference ✅
                   [dep=6] → DIFFERENT → create new function, store it

Step 3 → React.memo child receives same function reference
         → props haven't changed → child skips re-render ✅

KEY: useCallback keeps function reference stable when deps don't change
     so React.memo children can skip re-renders
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → First render: useCallback function store करता है
         cache में रखता है, return करता है

Step 2 → Re-render: React deps check करता है
         Same deps → same function reference return ✅
         Different deps → नई function create और store

Step 3 → React.memo child को same function reference मिलती है
         → props नहीं बदले → child re-render skip ✅

KEY: useCallback function reference stable रखता है ताकि
     React.memo children re-render skip कर सकें
```

---

## 🟡 Real World Example
**Instagram Feed:** The Feed component renders 50+ PostCard items. Each PostCard has an `onLike` callback. Without `useCallback`, every time the Feed's state changes (new post loaded), ALL 50 PostCards re-render because `onLike` is a new function. With `useCallback`, `onLike` is stable — PostCards wrapped in `React.memo` only re-render when their own post data changes.

## 🟡 Real Example Hindi mein
**Instagram Feed:** Feed component में 50+ PostCard items हैं। हर PostCard में `onLike` callback है। `useCallback` के बिना, Feed का state बदलने पर सभी 50 PostCards re-render होते हैं। `useCallback` से `onLike` stable रहती है — `React.memo` वाले PostCards सिर्फ तब re-render होते हैं जब उनका post data बदले।

---

## 💻 Code Example — Basic

```jsx
import { useState, useCallback, memo } from 'react';

// ── THE PROBLEM ───────────────────────────
// Without useCallback:

function FeedBad() {
  const [posts, setPosts] = useState([...]);
  const [filter, setFilter] = useState('all');

  const handleLike = (postId) => { // new function every render!
    setPosts(prev => prev.map(p =>
      p.id === postId ? { ...p, liked: !p.liked } : p
    ));
  };

  return (
    <div>
      <FilterBar filter={filter} onChange={setFilter} />
      {posts.map(post => (
        <PostCard key={post.id} post={post} onLike={handleLike} />
        // ↑ re-renders whenever filter changes (handleLike is always new!)
      ))}
    </div>
  );
}

// ── THE SOLUTION ──────────────────────────
// With useCallback: stable function reference

function FeedGood() {
  const [posts, setPosts] = useState([...]);
  const [filter, setFilter] = useState('all');

  // Stable function — same reference unless deps change
  const handleLike = useCallback((postId) => {
    setPosts(prev => prev.map(p =>
      p.id === postId ? { ...p, liked: !p.liked } : p
    ));
  }, []); // empty deps — setPosts is stable (from useState)

  return (
    <div>
      <FilterBar filter={filter} onChange={setFilter} />
      {posts.map(post => (
        <PostCard key={post.id} post={post} onLike={handleLike} />
        // ↑ won't re-render when filter changes! ✅
      ))}
    </div>
  );
}

// PostCard wrapped in memo — only re-renders if props change
const PostCard = memo(function PostCard({ post, onLike }) {
  console.log('PostCard rendered:', post.id);
  return (
    <div>
      <p>{post.content}</p>
      <button onClick={() => onLike(post.id)}>
        {post.liked ? '❤️' : '🤍'} Like
      </button>
    </div>
  );
});
```

## 💻 Code Example — Advanced

```jsx
import { useState, useCallback, useEffect, memo } from 'react';

// ── useCallback WITH DEPENDENCIES ─────────
function SearchPage({ categoryId }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  // This callback depends on categoryId
  // When categoryId changes, new callback is created (correct behavior!)
  const fetchResults = useCallback(async (searchQuery) => {
    const data = await fetch(
      `/api/search?q=${searchQuery}&category=${categoryId}`
    ).then(r => r.json());
    setResults(data);
  }, [categoryId]); // rebuild when categoryId changes

  // useCallback makes fetchResults stable per categoryId
  // useEffect can safely depend on it
  useEffect(() => {
    if (query) fetchResults(query);
  }, [query, fetchResults]); // fetchResults is now a safe dep

  return (
    <div>
      <input value={query} onChange={e => setQuery(e.target.value)} />
      <SearchResults results={results} onSelect={fetchResults} />
    </div>
  );
}

// ── useCallback FOR EVENT HANDLERS LIST ───
function ProductList({ products, userId }) {
  const [wishlist, setWishlist] = useState(new Set());

  // Stable callback — same reference for all ProductCard children
  const toggleWishlist = useCallback((productId) => {
    setWishlist(prev => {
      const next = new Set(prev);
      if (next.has(productId)) {
        next.delete(productId);
      } else {
        next.add(productId);
      }
      return next;
    });
  }, []); // setWishlist is stable → no deps needed

  const addToCart = useCallback(async (productId, quantity) => {
    await api.addToCart({ userId, productId, quantity });
    // Note: userId in deps because it's used inside!
  }, [userId]); // rebuild when userId changes

  return (
    <ul>
      {products.map(product => (
        <ProductCard
          key={product.id}
          product={product}
          isWishlisted={wishlist.has(product.id)}
          onToggleWishlist={toggleWishlist} // stable ✅
          onAddToCart={addToCart}           // stable per userId ✅
        />
      ))}
    </ul>
  );
}

const ProductCard = memo(function ProductCard({
  product, isWishlisted, onToggleWishlist, onAddToCart
}) {
  console.log('ProductCard:', product.name);
  return (
    <div>
      <h3>{product.name}</h3>
      <button onClick={() => onToggleWishlist(product.id)}>
        {isWishlisted ? '❤️' : '🤍'}
      </button>
      <button onClick={() => onAddToCart(product.id, 1)}>
        Add to Cart
      </button>
    </div>
  );
});
// ProductCard only re-renders when its own props change ✅
// (isWishlisted changes when item toggled — correct behavior)
```

---

## 🟠 Next.js Connection

```jsx
// useCallback works in Next.js Client Components

'use client';
// app/components/InfiniteList.jsx
import { useState, useCallback, useEffect, useRef } from 'react';

function InfiniteProductList() {
  const [products, setProducts] = useState([]);
  const [page, setPage] = useState(1);
  const loaderRef = useRef(null);

  // Stable loadMore function — passed to IntersectionObserver callback
  // Without useCallback: observer callback recreated, observer resets on every render
  const loadMore = useCallback(async () => {
    const newProducts = await fetch(`/api/products?page=${page}`)
      .then(r => r.json());
    setProducts(prev => [...prev, ...newProducts]);
    setPage(p => p + 1);
  }, [page]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => { if (entries[0].isIntersecting) loadMore(); },
      { threshold: 1 }
    );
    if (loaderRef.current) observer.observe(loaderRef.current);
    return () => observer.disconnect();
  }, [loadMore]); // loadMore is a safe dep because of useCallback

  return (
    <div>
      {products.map(p => <ProductCard key={p.id} product={p} />)}
      <div ref={loaderRef}>Loading...</div>
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using useCallback without React.memo on child
```jsx
// useCallback alone doesn't prevent re-renders!
// The CHILD must also be wrapped in React.memo

const handleClick = useCallback(() => { ... }, []); // ✅ stable function

// Without memo — child still re-renders!
function Child({ onClick }) { ... }                  // ❌ no memo

// WITH memo — now it works!
const Child = memo(function Child({ onClick }) { ... }); // ✅
```

❌ **Mistake 2:** Stale closure (missing deps)
```jsx
// WRONG: userId not in deps — stale closure!
const fetchUser = useCallback(() => {
  fetch(`/api/users/${userId}`); // userId captured but not in deps
}, []); // ❌ if userId changes, fetchUser still uses OLD userId!

// CORRECT:
const fetchUser = useCallback(() => {
  fetch(`/api/users/${userId}`);
}, [userId]); // ✅ rebuild when userId changes
```

❌ **Mistake 3:** useCallback on every function (over-optimization)
```jsx
// WRONG: useCallback on inline handlers that aren't passed as props
function Counter() {
  const [count, setCount] = useState(0);

  const increment = useCallback(() => setCount(c => c + 1), []); // ❌ unnecessary
  // This button is never memo'd — useCallback adds overhead for zero benefit

  return <button onClick={increment}>{count}</button>;
}

// CORRECT: only use useCallback when passing to memo'd children
// or as deps to other hooks
```

---

## 🧠 Tricky Interview Question

```jsx
const Counter = memo(function Counter({ onIncrement }) {
  console.log('Counter rendered');
  return <button onClick={onIncrement}>Click</button>;
});

function App() {
  const [count, setCount] = useState(0);
  const [text, setText] = useState('');

  const handleIncrement = useCallback(() => {
    setCount(c => c + 1);
  }, []);

  return (
    <div>
      <input value={text} onChange={e => setText(e.target.value)} />
      <Counter onIncrement={handleIncrement} />
      <p>Count: {count}</p>
    </div>
  );
}
// Does "Counter rendered" log when you type in the input?
```
**Answer:** No. `handleIncrement` has empty deps `[]` — it's the same function reference on every render. `Counter` is wrapped in `memo()` — it compares props. `onIncrement` reference is stable → props didn't change → Counter skips re-render. Only types in input trigger App re-render, not Counter re-render.

---

## ⚫ Interview Questions + Answers

**Q1: What is useCallback and why is it useful?**
A1: `useCallback(fn, deps)` returns a memoized version of the function — same reference between renders unless deps change. It's useful when passing callbacks to `React.memo`-wrapped children. Without it, every parent render creates a new function reference, which `React.memo` sees as a prop change, causing unnecessary child re-renders. Combined with `React.memo`, it prevents cascading re-renders in deep component trees.

**Q2: What's the relationship between useCallback and React.memo?**
A2: They work together. `React.memo(Component)` skips re-rendering if props haven't changed (by reference). But if a parent passes an inline function as prop, `React.memo` sees a new reference every render and re-renders anyway. `useCallback` makes the function reference stable — now `React.memo` correctly detects "props haven't changed" and skips the re-render. Both are needed; one without the other doesn't help.

**Q3: How is useCallback different from useMemo?**
A3: `useMemo(() => value, deps)` memoizes a **return value** (the result of calling the function). `useCallback(fn, deps)` memoizes the **function itself** — equivalent to `useMemo(() => fn, deps)`. Use `useMemo` for expensive computed values. Use `useCallback` for callback functions passed to children. Conceptually: "what do you want to keep stable? — a value → useMemo, a function → useCallback."

**Q4: Can you use useCallback to prevent component re-renders by itself?**
A4: No. `useCallback` only memoizes the function reference. The component still re-renders when ITS OWN STATE changes or its PARENT re-renders. To prevent unnecessary re-renders from parent, the child must be wrapped in `React.memo`. `useCallback` + `React.memo` together enable the optimization. Neither alone is sufficient for preventing parent-triggered re-renders.

**Q5: When should you NOT use useCallback?**
A5: Don't use it for: (1) Event handlers that aren't passed as props to `memo()`'d children — the function just goes into a regular DOM event listener, which doesn't care about reference equality. (2) Every function in a component "just in case" — `useCallback` itself has overhead (storing old values, comparing deps). Only add it when you've profiled and confirmed the optimization is needed.

---

## 🔷 When to Use + When Not to Use
✅ **Use useCallback when:**
- Passing callback to `React.memo`-wrapped child component
- Function is a dependency of `useEffect` or another `useCallback`
- Function passed to `IntersectionObserver`, `addEventListener`, or other APIs that should stay stable

❌ **Skip useCallback when:**
- Handler only used on a regular DOM element (`<button onClick={fn}>`)
- Component is not wrapped in `React.memo`
- "Premature optimization" — profile first, optimize second

---

## 📊 Visual Diagram

```
WITHOUT useCallback:
──────────────────────────────────────────────
  Parent renders
     │
     ├── handleLike = () => {...}  ← NEW function every render
     │
     └── <PostCard onLike={handleLike} />
               │
           memo check: prev.onLike !== new.onLike  → TRUE (new reference!)
               │
           → PostCard RE-RENDERS ❌ (unnecessary!)

WITH useCallback:
──────────────────────────────────────────────
  Parent renders
     │
     ├── handleLike = useCallback(() => {...}, [])
     │   └── deps same → return SAME function reference ✅
     │
     └── <PostCard onLike={handleLike} />
               │
           memo check: prev.onLike === new.onLike  → TRUE (same reference!)
               │
           → PostCard SKIPS re-render ✅

RULE: useCallback + React.memo = optimization pair
──────────────────────────────────────────────
  useCallback alone  → function stable, but child still re-renders
  React.memo alone   → child skips re-render, but only if props stable
  BOTH together      → child skips unnecessary re-renders ✅
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Memoize function | Cache function reference | Function reference cache करना |
| Stable reference | Same memory address across renders | Renders में same memory address |
| React.memo | Skip re-render if props unchanged | Props न बदलें तो re-render skip |
| Stale closure | Old captured variable in function | Function में पुरानी captured variable |
| Cascading re-render | Parent re-render causes child re-render | Parent re-render से child re-render |

---

## ⚡ 3-Line Summary
**English:**
1. `useCallback(fn, deps)` returns the same function reference between renders — new function only when deps change.
2. Only useful combined with `React.memo` — `useCallback` stabilizes the reference, `memo` uses that stability to skip re-renders.
3. Don't overuse — profile first. `useCallback` has overhead and only helps for `memo`-wrapped children.

**Hindi:**
1. `useCallback(fn, deps)` renders के बीच same function reference return करता है — deps बदलने पर ही नई function।
2. सिर्फ `React.memo` के साथ useful — `useCallback` reference stable करता है, `memo` उस stability से re-render skip करता है।
3. Overuse मत करो — पहले profile करो। `useCallback` का overhead है और सिर्फ `memo`-wrapped children के लिए useful है।

---

## ➡️ Next Topic
**49. useMemo vs useCallback** — दोनों का detailed comparison — कब क्या use करना है।
