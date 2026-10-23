# 157. memo, useMemo, useCallback — Performance
# हिंदी में: React Performance Optimization
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
Three tools that prevent unnecessary re-renders and expensive recomputations:
- **`React.memo`**: wraps a component — skips re-render if props didn't change
- **`useMemo`**: memoizes an expensive computed value — recomputes only when deps change
- **`useCallback`**: memoizes a function reference — new function only when deps change

All three are optimizations — only use them when there's a measurable performance problem, not by default.

## 🔵 सरल परिभाषा (Hindi)
तीन tools जो unnecessary re-renders और expensive computations रोकते हैं:
- **`React.memo`**: component wrap करता है — props नहीं बदले तो re-render skip
- **`useMemo`**: expensive computed value memoize — deps change होने पर ही recompute
- **`useCallback`**: function reference memoize — deps change होने पर ही new function

तीनों optimizations हैं — measurable performance problem हो तभी use करो, by default नहीं।

---

## 🔴 Problem they Solve
```
DEFAULT REACT BEHAVIOR:
  Parent re-renders → ALL child components re-render
  Even if child's props didn't change!

  FlatList parent re-renders (new state update):
    → CartBadge re-renders (props unchanged)
    → HeaderTitle re-renders (props unchanged)
    → 100 list items re-render (props unchanged!)
    Total: 103 unnecessary re-renders

WITH OPTIMIZATION:
    → CartBadge: props same → memo skips ✅
    → HeaderTitle: props same → memo skips ✅
    → 100 list items: memo skips ✅
    Total: 1 re-render (only the changed component)

WHEN IS THIS CRITICAL IN REACT NATIVE?
  FlatList with 100+ items
  Animations that update state rapidly
  Real-time data (WebSocket, polling)
  Complex forms with many fields
```

---

## 💻 Code Example

```tsx
import React, { memo, useMemo, useCallback, useState } from 'react';
import { View, Text, FlatList, Pressable, StyleSheet } from 'react-native';

// ─── React.memo: SKIP RE-RENDER IF PROPS UNCHANGED ────────────────────────────
// WITHOUT memo: re-renders whenever parent re-renders (even if item unchanged)
// WITH memo: re-renders only when item.id, item.price, or onPress changes

const ProductCard = memo(function ProductCard({
  item,
  onAddToCart,
}: {
  item: { id: string; name: string; price: number };
  onAddToCart: (id: string) => void;
}) {
  console.log(`ProductCard ${item.id} rendering`);  // should NOT fire on every parent render
  return (
    <View style={styles.card}>
      <Text style={styles.name}>{item.name}</Text>
      <Text style={styles.price}>₹{item.price}</Text>
      <Pressable onPress={() => onAddToCart(item.id)}>
        <Text>Add to Cart</Text>
      </Pressable>
    </View>
  );
});

// CUSTOM COMPARISON (optional second arg to memo):
// Only re-render when price changes (ignore name change)
const StrictProductCard = memo(
  function StrictProductCard({ item, onAddToCart }) {
    return <View />;
  },
  (prevProps, nextProps) => {
    // Return TRUE if props are equal (skip re-render)
    // Return FALSE if props changed (do re-render)
    return prevProps.item.price === nextProps.item.price &&
           prevProps.item.id === nextProps.item.id;
    // Note: if we return true even when onAddToCart changed,
    // the old function is called — can cause stale closure bugs!
  }
);

// ─── PARENT COMPONENT ────────────────────────────────────────────────────────
type Product = { id: string; name: string; price: number };

export default function ProductList() {
  const [products] = useState<Product[]>([
    { id: '1', name: 'Phone', price: 15000 },
    { id: '2', name: 'Laptop', price: 55000 },
    { id: '3', name: 'Tablet', price: 25000 },
  ]);
  const [cartCount, setCartCount] = useState(0);
  const [filter, setFilter] = useState<'all' | 'under20k'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // ─── useMemo: EXPENSIVE COMPUTATION ────────────────────────────────────────
  // WITHOUT useMemo: recomputes on EVERY render (even cartCount changes!)
  // WITH useMemo: recomputes only when products or filter changes
  const filteredProducts = useMemo(() => {
    console.log('Computing filtered products...');  // should NOT fire on cartCount change
    let result = products;

    if (filter === 'under20k') {
      result = result.filter(p => p.price < 20000);
    }

    if (searchQuery) {
      result = result.filter(p =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Simulate expensive operation (sorting by multiple criteria):
    return result.sort((a, b) => a.price - b.price);
  }, [products, filter, searchQuery]);  // ← deps: recompute only when these change

  // ─── useMemo: DERIVED STATS ──────────────────────────────────────────────────
  const stats = useMemo(() => ({
    totalProducts: filteredProducts.length,
    averagePrice: filteredProducts.reduce((sum, p) => sum + p.price, 0) / filteredProducts.length,
    maxPrice: Math.max(...filteredProducts.map(p => p.price)),
  }), [filteredProducts]);

  // ─── useCallback: STABLE FUNCTION REFERENCE ─────────────────────────────────
  // WITHOUT useCallback: new function reference every render
  //   → ProductCard's memo sees new onAddToCart prop → re-renders!
  //   → memo becomes USELESS without useCallback on passed functions
  // WITH useCallback: same function reference until deps change
  //   → ProductCard's memo comparison: onAddToCart same → skip ✅
  const handleAddToCart = useCallback((productId: string) => {
    console.log('Adding to cart:', productId);
    setCartCount(prev => prev + 1);
    // ⚠️ Use setCartCount(prev => prev + 1) not setCartCount(cartCount + 1)!
    // Reason: the callback is captured at creation time (when cartCount might be stale)
    // Functional update pattern ensures correct current value
  }, []);  // ← empty deps: function never changes (uses only setCartCount, which is stable)

  // ─── useCallback for FlatList handlers ──────────────────────────────────────
  const renderItem = useCallback(
    ({ item }: { item: Product }) => (
      <ProductCard item={item} onAddToCart={handleAddToCart} />
    ),
    [handleAddToCart]  // handleAddToCart is stable → renderItem is stable → memo works
  );

  const keyExtractor = useCallback((item: Product) => item.id, []);

  return (
    <View style={{ flex: 1 }}>
      {/* This state update (cartCount) should NOT re-render ProductCards */}
      <Text style={styles.badge}>Cart: {cartCount}</Text>

      <Text style={styles.stats}>
        {stats.totalProducts} products | Avg: ₹{stats.averagePrice.toFixed(0)}
      </Text>

      <FlatList
        data={filteredProducts}
        renderItem={renderItem}
        keyExtractor={keyExtractor}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  card: { padding: 16, backgroundColor: 'white', margin: 8, borderRadius: 8 },
  name: { fontSize: 16, fontWeight: '600' },
  price: { fontSize: 14, color: '#888', marginTop: 4 },
  badge: { fontSize: 16, padding: 12, fontWeight: '700' },
  stats: { padding: 8, fontSize: 13, color: '#666' },
});
```

---

## 📱 Android vs iOS Difference
No difference — these are React optimizations, not platform-specific.

However: performance sensitivity differs:
- **Android (budget phones)**: slower JS engine (Hermes helps but still), slower native rendering → optimizations matter MORE on Android
- **iOS**: generally faster hardware → issues less noticeable, but optimizations still important for smooth 120fps ProMotion displays

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using memo but not useCallback (kills memo's effect)
```tsx
// ProductCard has memo... but:
const handleAdd = (id) => setCart([...cart, id]);  // NEW function every render!

<ProductCard item={item} onAddToCart={handleAdd} />
// memo comparison: onAddToCart prop changed (new reference)! → re-renders anyway

// FIX: useCallback to stabilize function reference
const handleAdd = useCallback((id) => setCart(prev => [...prev, id]), []);
```

❌ **Mistake 2:** Empty deps on useMemo/useCallback that use changing values
```tsx
// WRONG: stale closure — shows outdated cart value
const handleAdd = useCallback((id) => {
  console.log('Current cart:', cart.length);  // cart is stale! captured at creation
  setCart([...cart, id]);                      // might miss items
}, []);  // ← cart not in deps!

// CORRECT: include all used values in deps, OR use functional update
const handleAdd = useCallback((id) => {
  setCart(prev => [...prev, id]);  // no need for cart in deps
}, []);
// OR:
const handleAdd = useCallback((id) => {
  console.log('cart length:', cart.length);
  setCart([...cart, id]);
}, [cart]);  // ← cart in deps: new function when cart changes
```

❌ **Mistake 3:** memo on everything (premature optimization)
```tsx
// DON'T: wrap every component in memo "just in case"
const SimpleText = memo(({ text }) => <Text>{text}</Text>);
// Overhead of memo comparison > cost of simple re-render
// Memo is SLOWER for very cheap components!

// DO: profile first, then memo only components that:
//   1. Render many times (list items!)
//   2. Have expensive render logic
//   3. Have stable props most of the time
```

---

## 🧠 Tricky Interview Question

**Q: You have `React.memo` on a component but it keeps re-rendering. Why?**

**Answer:** The most common cause: **the parent passes an object, array, or function created inline**. `memo` does shallow comparison — `{}` and `{}` are different references even with same content. Solutions: (1) `useCallback` for functions passed as props; (2) `useMemo` for objects/arrays passed as props; (3) lift the object/array outside the component if it's static; (4) move the value into state/ref. Other causes: `useContext` with a frequently-changing context value (component subscribes to whole context), or a custom comparison function returning false unnecessarily.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between `memo`, `useMemo`, and `useCallback`?**
A1: `React.memo(Component)` — HOC that memoizes a component, skips re-render if props are shallowly equal. For components. `useMemo(() => expensiveCalc(), [deps])` — memoizes a computed value, recomputes only when deps change. For values. `useCallback(() => fn(), [deps])` — memoizes a function reference, new reference only when deps change. For functions (especially passed as props to memoized children or used as FlatList handlers).

**Q2: When should you NOT use memo/useMemo/useCallback?**
A2: Don't use them by default — they add overhead (comparison cost). Skip them for: (1) Components that always re-render anyway (their props always change), (2) Simple components where re-render cost < comparison cost, (3) Components that are rarely rendered. Use them only when profiling shows unnecessary re-renders are causing measurable jank. React DevTools (Flipper) and the React Profiler can identify which components are re-rendering unnecessarily.

**Q3: Why must `useCallback` be used with `React.memo` for it to work?**
A3: `memo` does shallow prop comparison. If parent passes a function `onPress={() => handlePress(id)}`, a new function object is created every render — even if the logic is identical. `memo` sees a new object reference = props changed = re-render. With `useCallback`, the same function reference is returned between renders (unless deps change) — `memo` comparison finds same reference = no re-render. They must be used together; `memo` alone doesn't help if props include unstable function references.

**Q4: What is the stale closure problem with `useCallback`?**
A4: When `useCallback` has empty deps `[]`, the callback captures the values of all external variables at creation time and never updates. If the callback uses `count` and `count` changes, the callback still sees the old `count`. Fix: (1) Add `count` to deps array (new callback when count changes), or (2) Use functional update pattern `setState(prev => prev + 1)` which doesn't need the current state value.

---

## 📊 Quick Decision Guide

```
RE-RENDERING PROBLEM?
  → Profile first with React DevTools / Flipper
  
  Is it a component re-rendering unnecessarily?
  → React.memo + useCallback on passed functions

  Is it an expensive computation running on every render?
  → useMemo for the computed value

  Is a function reference causing child re-renders?
  → useCallback on the function

MEMO DECISION TREE:
  Is it a FlatList item? → YES: memo (definitely)
  Does it render 50+ instances? → YES: memo (probably)
  Does it have heavy render logic? → YES: memo (probably)
  Is it a simple display component? → Maybe not needed
  Does parent re-render very frequently? → Consider memo
```

---

## ⚡ 3-Line Summary
**English:**
1. `React.memo` skips component re-render if props didn't change (shallow comparison) — use on FlatList items and frequently-rendered components; requires `useCallback` on function props to actually work.
2. `useMemo(() => expensiveCalc(), [deps])` caches computed values — use for filtering/sorting large arrays that don't need to recompute on every render.
3. `useCallback(() => fn(), [deps])` caches function references — primary use is stabilizing functions passed to memoized children; use functional updates (`setState(prev => ...)`) to avoid stale closures.

**Hindi:**
1. `React.memo` props same हों तो re-render skip — FlatList items पर use करो; function props पर `useCallback` भी जरूरी नहीं तो memo काम नहीं करेगा।
2. `useMemo` expensive computation cache करता है — large array filter/sort जो हर render पर recompute न हो।
3. `useCallback` function reference cache करता है — memoized children को pass करने के लिए; stale closure से बचो functional updates `setState(prev => ...)` से।

---

## ➡️ Next Topic
**158. InteractionManager** — Deferring heavy work after animations complete।
