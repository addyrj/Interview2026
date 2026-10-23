# 58. React.memo — Component Memoization
# हिंदी में: React.memo — Component को Unnecessary Re-renders से बचाना

---

## 🔵 Simple Definition (English)
`React.memo` is a **Higher Order Component (HOC)** that memoizes a component — it skips re-rendering if its props haven't changed. When a parent re-renders, wrapped child components only re-render if their props actually changed (compared with `Object.is`).

## 🔵 सरल परिभाषा (Hindi)
`React.memo` एक **Higher Order Component (HOC)** है जो component को memoize करता है — props नहीं बदले तो re-render skip करता है। Parent re-render होने पर, wrapped child components सिर्फ तब re-render होते हैं जब उनके props actually बदलें (`Object.is` से compare)।

---

## 🔴 Problem it Solves

```jsx
// PROBLEM: Child re-renders even when ITS props didn't change!
function Parent() {
  const [count, setCount] = useState(0);
  const [search, setSearch] = useState('');

  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>Count: {count}</button>
      <input value={search} onChange={e => setSearch(e.target.value)} />
      <ExpensiveList items={STATIC_ITEMS} />  {/* Items never change! */}
    </div>
  );
}

function ExpensiveList({ items }) {
  console.log('ExpensiveList rendered!'); // logs on every keystroke!
  // Even though items is the same STATIC_ITEMS every render!
  return items.map(item => <ComplexItem key={item.id} item={item} />);
}
```

## 🔴 यह क्यों बना? (Hindi)
```jsx
// PROBLEM: Parent re-render पर सब children re-render होते हैं
// Even जब child के props नहीं बदले!
// React.memo: "props same हैं? Skip करो re-render!"
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Wrap component in React.memo
         const MemoizedList = React.memo(ExpensiveList);
         // OR: define and wrap at once
         const ExpensiveList = memo(function ExpensiveList({ items }) { ... });

Step 2 → When parent re-renders, React checks memoized child:
         "Did props change?"

Step 3 → Props comparison (Object.is — shallow):
         Old props: { items: [same array] }
         New props: { items: [same array] } → SAME → SKIP re-render ✅

Step 4 → If props changed (by reference or value):
         → Re-render the component

KEY: Works only with STABLE props — objects/arrays must be same reference!
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → React.memo से component wrap करो
Step 2 → Parent re-render पर, React memoized child check करता है
Step 3 → Props compare करता है (Object.is — shallow):
         Same props → Re-render SKIP ✅
         Props changed → Re-render होता है
KEY: Stable props चाहिए — objects/arrays same reference होनी चाहिए!
```

---

## 🟡 Real World Example
**Instagram Post Feed:** 50 posts rendered. User updates their profile picture (header state changes). Without `memo`, all 50 PostCards re-render. With `React.memo`, only the header updates — all PostCards see unchanged props and skip re-rendering. 50× fewer DOM operations.

## 🟡 Real Example Hindi मे
**Instagram Post Feed:** 50 posts render हैं। User profile picture update करता है (header state change)। `memo` के बिना, सभी 50 PostCards re-render। `React.memo` से, सिर्फ header update — सभी PostCards unchanged props देखते हैं और re-render skip करते हैं।

---

## 💻 Code Example — Basic

```jsx
import { useState, memo } from 'react';

// ── BASIC React.memo ──────────────────────

// WITHOUT memo: re-renders on every parent render
function PostCard_Old({ post }) {
  console.log('PostCard rendered:', post.id); // too many!
  return (
    <div>
      <h3>{post.title}</h3>
      <p>{post.content}</p>
    </div>
  );
}

// WITH memo: only re-renders when post prop changes
const PostCard = memo(function PostCard({ post }) {
  console.log('PostCard rendered:', post.id); // only when post changes
  return (
    <div>
      <h3>{post.title}</h3>
      <p>{post.content}</p>
    </div>
  );
});

function Feed() {
  const [headerText, setHeaderText] = useState('Instagram');
  const [posts] = useState([
    { id: 1, title: 'Post 1', content: 'Content 1' },
    { id: 2, title: 'Post 2', content: 'Content 2' },
    { id: 3, title: 'Post 3', content: 'Content 3' },
  ]);

  return (
    <div>
      <h1>{headerText}</h1>
      <button onClick={() => setHeaderText(h => h + '!')}>
        Update Header
      </button>

      {posts.map(post => (
        // PostCard won't re-render when headerText changes!
        // post prop is same object reference → memo skips ✅
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { useState, memo, useCallback, useMemo } from 'react';

// ── MEMO + useCallback + useMemo = Full optimization ──

// Memoized child needs:
// 1. Object props → useMemo (stable reference)
// 2. Function props → useCallback (stable reference)
const ProductCard = memo(function ProductCard({
  product,       // object — needs useMemo
  style,         // object — needs useMemo
  onAddToCart,   // function — needs useCallback
  onWishlist,    // function — needs useCallback
}) {
  console.log('ProductCard rendered:', product.id);
  return (
    <div style={style}>
      <h3>{product.name}</h3>
      <button onClick={() => onAddToCart(product.id)}>Add to Cart</button>
      <button onClick={() => onWishlist(product.id)}>Wishlist</button>
    </div>
  );
});

function ProductList({ products, userId }) {
  const [cartItems, setCartItems] = useState(new Set());
  const [filter, setFilter] = useState('all');

  // useCallback: stable function references for memo'd child
  const handleAddToCart = useCallback((id) => {
    setCartItems(prev => new Set([...prev, id]));
  }, []); // setCartItems is stable → no deps

  const handleWishlist = useCallback((id) => {
    console.log('Wishlisted:', id, 'by user:', userId);
  }, [userId]); // depends on userId

  // useMemo: stable object reference for style prop
  const cardStyle = useMemo(
    () => ({ border: '1px solid #ddd', padding: 16, borderRadius: 8 }),
    [] // never changes
  );

  // filter doesn't need useMemo — it changes the list, not a prop
  const displayed = filter === 'all'
    ? products
    : products.filter(p => p.category === filter);

  return (
    <div>
      <select value={filter} onChange={e => setFilter(e.target.value)}>
        <option value="all">All</option>
        <option value="food">Food</option>
        <option value="drink">Drink</option>
      </select>

      {displayed.map(product => (
        <ProductCard
          key={product.id}
          product={product}          // from array — same reference ✅
          style={cardStyle}          // useMemo — stable ✅
          onAddToCart={handleAddToCart} // useCallback — stable ✅
          onWishlist={handleWishlist}   // useCallback — stable ✅
        />
        // ProductCard won't re-render when filter changes!
        // (unless a product's data changed — which it hasn't)
      ))}
    </div>
  );
}

// ── CUSTOM COMPARISON FUNCTION ────────────
// memo accepts optional second argument: custom areEqual function
const DeepCard = memo(
  function DeepCard({ user }) {
    return <div>{user.name} — {user.address.city}</div>;
  },
  // Custom comparator: return true to SKIP re-render, false to re-render
  (prevProps, nextProps) => {
    // Only re-render if name or city changed (not other user fields)
    return prevProps.user.name === nextProps.user.name &&
           prevProps.user.address.city === nextProps.user.address.city;
  }
);
// Use sparingly — custom comparators are hard to maintain
```

---

## 🟠 Next.js Connection

```jsx
// React.memo is useful in Client Components
// Server Components don't re-render — no memo needed!

'use client';
// In Next.js, memo is most useful for lists in Client Components

import { memo, useState, useCallback } from 'react';

const ReviewCard = memo(function ReviewCard({ review, onHelpful }) {
  return (
    <div>
      <p>{review.text}</p>
      <span>⭐ {review.rating}</span>
      <button onClick={() => onHelpful(review.id)}>Helpful</button>
    </div>
  );
});

function ReviewSection({ productId }) {
  const [reviews, setReviews] = useState([...]);
  const [sortBy, setSortBy] = useState('recent');

  const markHelpful = useCallback((id) => {
    setReviews(prev => prev.map(r =>
      r.id === id ? { ...r, helpful: r.helpful + 1 } : r
    ));
  }, []);

  const sorted = [...reviews].sort((a, b) =>
    sortBy === 'recent' ? b.date - a.date : b.helpful - a.helpful
  );

  return (
    <div>
      <select value={sortBy} onChange={e => setSortBy(e.target.value)}>
        <option value="recent">Most Recent</option>
        <option value="helpful">Most Helpful</option>
      </select>

      {sorted.map(review => (
        <ReviewCard
          key={review.id}
          review={review}           // same reference (unaffected reviews) ✅
          onHelpful={markHelpful}   // useCallback — stable ✅
        />
      ))}
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** memo without stable props (object/function props)
```jsx
const Child = memo(function Child({ config, onClick }) { ... });

function Parent() {
  return (
    <Child
      config={{ color: 'red' }}   // ❌ new object every render!
      onClick={() => doSomething()} // ❌ new function every render!
    />
  );
}
// memo is useless here — new references every render → always re-renders!
// Fix: useMemo for config, useCallback for onClick
```

❌ **Mistake 2:** Wrapping everything in memo
```jsx
// WRONG: memo on tiny, cheap components adds overhead without benefit
const Label = memo(({ text }) => <span>{text}</span>); // ❌ overkill!
// memo check + comparison costs more than just re-rendering a span

// CORRECT: use memo for components that:
// - Are computationally expensive to render
// - Render frequently (large lists)
// - Receive stable props (primitive or memoized objects)
```

---

## 🧠 Tricky Interview Question

```jsx
const Child = memo(function Child({ items }) {
  console.log('Child rendered');
  return <ul>{items.map(i => <li key={i}>{i}</li>)}</ul>;
});

function Parent() {
  const [count, setCount] = useState(0);
  const items = ['a', 'b', 'c']; // defined inside Parent!

  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>{count}</button>
      <Child items={items} />
    </div>
  );
}
// Does "Child rendered" log every time you click the button?
```
**Answer:** Yes, every click. `items` is a new array on every render (new reference). `React.memo` does a shallow comparison — `oldItems !== newItems` (different objects) → re-renders. Fix: move `items` outside Parent, or use `useMemo(() => ['a', 'b', 'c'], [])`.

---

## ⚫ Interview Questions + Answers

**Q1: What is React.memo and how does it work?**
A1: `React.memo(Component)` wraps a component in memoization. When the parent re-renders, React checks if the memoized component's props changed using `Object.is` (shallow comparison). If props are the same, the previous render output is reused — the component function is not called. If any prop changed, it re-renders normally. It's a performance optimization — not a semantic change.

**Q2: What is the difference between React.memo and useMemo?**
A2: `React.memo` memoizes a **component** — skips re-rendering if props unchanged. `useMemo` memoizes a **value** (result of a function) — skips recomputation if deps unchanged. They work together: use `useMemo` to create stable object props and `useCallback` to create stable function props, then pass them to `memo()`'d children.

**Q3: Why does React.memo fail when passing inline functions/objects?**
A3: `React.memo` uses `Object.is` for prop comparison. `Object.is({a:1}, {a:1})` → `false` (different object references). An inline function or object literal creates a NEW reference on every render, so memo always sees "new props" and re-renders. Fix: use `useMemo` for objects, `useCallback` for functions, or move the value outside the component.

**Q4: What is the custom comparator function in React.memo?**
A4: `React.memo(Component, areEqual)` accepts an optional second argument — a function `(prevProps, nextProps) => boolean`. Return `true` to skip re-render (props considered equal), `false` to re-render. Unlike `shouldComponentUpdate` in class components (return false to update, true to skip), here `true` = skip, `false` = update. Use sparingly — complex comparators are hard to maintain and easy to get wrong.

**Q5: Does React.memo prevent re-renders triggered by state or context changes?**
A5: No — `React.memo` only prevents re-renders from PROP changes. If the component calls `useState` internally and state changes, it re-renders. If it subscribes to a `useContext`, it re-renders when context changes. `memo` only stops parent-triggered re-renders when props are the same.

---

## 🔷 When to Use + When Not to Use
✅ **Use React.memo when:**
- Component renders frequently (in a large list)
- Component is expensive to render (complex JSX, deep trees)
- Props are mostly stable (primitives or memoized objects/functions)
- You've profiled and confirmed unnecessary re-renders

❌ **Skip React.memo when:**
- Component is simple (renders in < 0.1ms)
- Props change almost every render anyway
- Component renders rarely
- You haven't profiled — premature optimization

---

## 📊 Visual Diagram

```
WITHOUT React.memo:
────────────────────────────────────────────────
  Parent state changes
       │
       ├── Header   → re-renders
       ├── Sidebar  → re-renders (even if props same!)
       └── PostList → re-renders
           ├── PostCard key=1 → re-renders ❌
           ├── PostCard key=2 → re-renders ❌
           └── PostCard key=3 → re-renders ❌

WITH React.memo:
────────────────────────────────────────────────
  Parent state changes
       │
       ├── Header   → re-renders (connected state)
       ├── Sidebar  → memo: props same? → SKIP ✅
       └── PostList → re-renders (receives new posts prop)
           ├── PostCard key=1 → memo: post same? → SKIP ✅
           ├── PostCard key=2 → memo: post changed → re-render ✅
           └── PostCard key=3 → memo: post same? → SKIP ✅

MEMO TRIO:
────────────────────────────────────────────────
  memo(Component)     → memoize COMPONENT
  useMemo(fn, deps)   → memoize VALUE
  useCallback(fn,deps)→ memoize FUNCTION

  All three together = full optimization for expensive trees
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| React.memo | HOC that memoizes a component | Component memoize करने वाला HOC |
| Shallow comparison | Compare top-level references only | सिर्फ top-level references compare |
| Object.is | React's equality check for props | React का equality check |
| Re-render | Component function called again | Component function दोबारा call |
| Stable reference | Same memory address across renders | Renders में same memory address |
| HOC | Higher Order Component | Higher Order Component |

---

## ⚡ 3-Line Summary
**English:**
1. `React.memo(Component)` skips re-rendering if props haven't changed — compares with shallow `Object.is`.
2. Ineffective with inline objects/functions (new reference every render) — pair with `useMemo`/`useCallback` for stable props.
3. Only prevents parent-triggered re-renders, not state or context changes inside the component.

**Hindi:**
1. `React.memo(Component)` props न बदलें तो re-render skip करता है — shallow `Object.is` से compare।
2. Inline objects/functions के साथ ineffective (हर render पर new reference) — `useMemo`/`useCallback` से stable props बनाओ।
3. सिर्फ parent-triggered re-renders रोकता है, component के अंदर state या context changes नहीं।

---

## ➡️ Next Topic
**59. React Performance — Profiling + Optimization** — React DevTools Profiler से performance measure करना।
