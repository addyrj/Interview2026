# 24. List Rendering + key Prop
# हिंदी में: List Rendering + key Prop — Arrays को JSX में Render करना

---

## 🔵 Simple Definition (English)
**List rendering** in React means using JavaScript's `.map()` to turn an array of data into an array of JSX elements. The `key` prop is a special React attribute that helps React's diffing algorithm efficiently identify which items changed, were added, or removed.

## 🔵 सरल परिभाषा (Hindi)
**List rendering** में React JavaScript के `.map()` से data array को JSX elements के array में convert करता है। `key` prop एक special React attribute है जो React के diffing algorithm को efficiently identify करने में help करता है कि कौन से items changed, added, या removed हुए।

---

## 🔴 Problem it Solves
```jsx
// WITHOUT list rendering: hard-coded, not scalable
function RestaurantList() {
  return (
    <ul>
      <li>Pizza Palace</li>   {/* manually written */}
      <li>Burger Barn</li>    {/* manually written */}
      <li>Taco Town</li>      {/* manually written */}
    </ul>
  );
}
// Doesn't scale — what if you have 1000 restaurants from an API?

// WITH list rendering:
function RestaurantList({ restaurants }) {
  return (
    <ul>
      {restaurants.map(r => <li key={r.id}>{r.name}</li>)}
    </ul>
  );
}
// Works for 1 or 10,000 restaurants!
```

## 🔴 यह क्यों बना? (Hindi)
```jsx
// Without: manually हर item लिखो — not scalable, API data से work नहीं
// With: `.map()` से dynamic data को JSX में convert करो
// key prop: React को efficient diff करने में help करता है
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → You have an array of data
         const products = [{ id: 1, name: 'Pizza' }, ...]

Step 2 → .map() transforms each item to JSX
         products.map(p => <ProductCard key={p.id} product={p} />)

Step 3 → React renders array of elements
         Each element needs a UNIQUE, STABLE key

Step 4 → On updates, React uses key to match old → new:
         key="1" → key="1": UPDATE props only ✅
         key="2" → not found: REMOVE this element ✅
         key="3" → didn't exist: ADD new element ✅
         Without key: React can't match → re-renders ALL items ❌
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आपके पास data array है
Step 2 → .map() हर item को JSX में transform करता है
         हर item को UNIQUE, STABLE key चाहिए
Step 3 → React key से old → new match करता है:
         Same key → props update करो
         Key gone → element remove करो
         New key → element add करो
         Key के बिना → सब re-render होता है ❌
```

---

## 🟡 Real World Example
**Swiggy/Zomato Food Menu:** You have 50 food items. User filters by "veg only" — 30 items remain. Without keys, React doesn't know which 20 items were removed — it remounts all 30. With keys (`key={item.id}`), React precisely removes only the 20 non-veg items — 6× less DOM work.

## 🟡 Real Example Hindi मे
**Swiggy Food Menu:** 50 food items हैं। User "veg only" filter करता है — 30 items रहते हैं। Keys के बिना, React नहीं जानता कौन से 20 remove हुए — सब 30 remount करता है। Keys से (`key={item.id}`), React precisely सिर्फ 20 non-veg remove करता है।

---

## 💻 Code Example — Basic

```jsx
import { useState } from 'react';

// ── BASIC LIST RENDERING ──────────────────
function MenuList({ items }) {
  return (
    <ul>
      {items.map(item => (
        // key MUST be on the outermost element returned by .map()
        // key must be UNIQUE among siblings
        // key must be STABLE (same item → same key across renders)
        <li key={item.id}>
          <span>{item.emoji}</span>
          <span>{item.name}</span>
          <span>₹{item.price}</span>
        </li>
      ))}
    </ul>
  );
}

// ── RENDERING COMPONENTS IN LIST ──────────
function ProductGrid({ products }) {
  return (
    <div className="grid">
      {products.map(product => (
        // key goes on the component, not inside it
        <ProductCard
          key={product.id}    // key here — NOT inside ProductCard
          product={product}
        />
      ))}
    </div>
  );
}

// ProductCard does NOT receive key as a prop — it's React-internal
function ProductCard({ product }) {
  // props.key is NOT accessible here — it's not passed as prop
  return (
    <div>
      <h3>{product.name}</h3>
      <p>₹{product.price}</p>
    </div>
  );
}

// ── FILTERING + MAPPING ───────────────────
function FilterableList() {
  const [filter, setFilter] = useState('all');

  const allProducts = [
    { id: 1, name: 'Pizza',  category: 'food',  price: 299 },
    { id: 2, name: 'Coke',   category: 'drink', price: 60  },
    { id: 3, name: 'Burger', category: 'food',  price: 149 },
    { id: 4, name: 'Juice',  category: 'drink', price: 80  },
  ];

  // Filter first, then map — clear and readable
  const displayed = filter === 'all'
    ? allProducts
    : allProducts.filter(p => p.category === filter);

  return (
    <div>
      <div>
        <button onClick={() => setFilter('all')}>All</button>
        <button onClick={() => setFilter('food')}>Food</button>
        <button onClick={() => setFilter('drink')}>Drink</button>
      </div>

      <ul>
        {displayed.map(p => (
          // key is stable (product.id) even after filtering!
          // Product id=1 always has key="1" regardless of position
          <li key={p.id}>{p.name} — ₹{p.price}</li>
        ))}
      </ul>
    </div>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { useState, useCallback } from 'react';

// ── WHY INDEX AS KEY IS WRONG ─────────────
function TodoListBad({ todos }) {
  return todos.map((todo, index) => (
    <TodoItem key={index} todo={todo} /> // ❌ index as key
  ));
}
// Problem: remove item at index 0
// Old:  [key=0: "Buy milk", key=1: "Walk dog", key=2: "Read"]
// New:  [key=0: "Walk dog", key=1: "Read"]        after remove
// React: key=0 "changed" (Buy milk → Walk dog) → update
//        key=1 "changed" (Walk dog → Read) → update
//        key=2 removed
// Result: 2 unnecessary updates + wrong state if TodoItem has local state!

function TodoListGood({ todos }) {
  return todos.map(todo => (
    <TodoItem key={todo.id} todo={todo} /> // ✅ stable unique id
  ));
}
// Remove item id=1:
// React: key="1" not in new list → remove it
//        key="2", key="3" unchanged → no update!
// Result: 1 remove, 0 unnecessary updates ✅

// ── REAL REORDERABLE LIST ─────────────────
function SortableProductList() {
  const [products, setProducts] = useState([
    { id: 'p1', name: 'Pizza',  price: 299, liked: false },
    { id: 'p2', name: 'Burger', price: 149, liked: false },
    { id: 'p3', name: 'Pasta',  price: 199, liked: true  },
  ]);

  const toggleLike = useCallback((id) => {
    setProducts(prev =>
      prev.map(p => p.id === id ? { ...p, liked: !p.liked } : p)
    );
  }, []);

  const sortByPrice = () => {
    setProducts(prev => [...prev].sort((a, b) => a.price - b.price));
  };

  const removeItem = (id) => {
    setProducts(prev => prev.filter(p => p.id !== id));
  };

  const addItem = () => {
    setProducts(prev => [
      ...prev,
      { id: `p${Date.now()}`, name: 'New Item', price: 99, liked: false }
    ]);
  };

  return (
    <div>
      <button onClick={sortByPrice}>Sort by Price</button>
      <button onClick={addItem}>Add Item</button>

      <ul>
        {products.map(product => (
          // key=product.id: stable even after sort/filter!
          // When sorted: same key, just different position → no remount
          <li key={product.id}>
            {product.name} — ₹{product.price}
            <button onClick={() => toggleLike(product.id)}>
              {product.liked ? '❤️' : '🤍'}
            </button>
            <button onClick={() => removeItem(product.id)}>×</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

// ── FRAGMENT WITH KEY ─────────────────────
// When list item renders multiple elements
import { Fragment } from 'react';

function TableWithDetails({ rows }) {
  return (
    <tbody>
      {rows.map(row => (
        // Can't use <> shorthand — need key on Fragment!
        <Fragment key={row.id}>
          <tr>
            <td>{row.name}</td>
            <td>{row.value}</td>
          </tr>
          <tr className="detail-row">
            <td colSpan={2}>{row.description}</td>
          </tr>
        </Fragment>
      ))}
    </tbody>
  );
}
```

---

## 🟠 Next.js Connection

```jsx
// List rendering works identically in both React and Next.js

// ── SERVER COMPONENT: list rendered on server ─
async function ProductCatalog({ searchParams }) {
  const products = await fetchProducts({
    category: searchParams.category,
    sort: searchParams.sort,
  });

  return (
    <ul>
      {products.map(product => (
        <li key={product.id}>
          <ProductCard product={product} />
        </li>
      ))}
    </ul>
  );
}

// ── CLIENT COMPONENT: interactive list ────
'use client';
function ClientFilterList({ initialProducts }) {
  const [products, setProducts] = useState(initialProducts);
  const [filter, setFilter] = useState('');

  const filtered = products.filter(p =>
    p.name.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div>
      <input value={filter} onChange={e => setFilter(e.target.value)} />
      <ul>
        {filtered.map(p => (
          <li key={p.id}>{p.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using array index as key
```jsx
// WRONG: causes state bugs on reorder/remove
items.map((item, index) => <Item key={index} item={item} />)

// CORRECT: use stable unique ID from data
items.map(item => <Item key={item.id} item={item} />)
```

❌ **Mistake 2:** Using non-unique keys
```jsx
// WRONG: duplicate keys → React warning + wrong behavior
items.map(item => <Item key={item.category} item={item} />)
// If multiple items have same category: duplicate keys!

// CORRECT: keys must be unique AMONG SIBLINGS
items.map(item => <Item key={item.id} item={item} />)
// id is unique per item ✅
```

❌ **Mistake 3:** Putting key inside the component
```jsx
// WRONG: key goes on element returned by .map(), not inside
items.map(item => (
  <Item item={item}>
    {/* key here is wrong — ignored by React! */}
  </Item>
))

// CORRECT: key on the outermost element in .map()
items.map(item => <Item key={item.id} item={item} />) // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
function App() {
  const [items, setItems] = useState(['A', 'B', 'C']);

  return (
    <ul>
      {items.map((item, index) => (
        <li key={index}>
          <input defaultValue={item} />
        </li>
      ))}
      <button onClick={() => setItems(['X', 'A', 'B', 'C'])}>
        Prepend X
      </button>
    </ul>
  );
}
// User types "ADITYA" in the first input (initially "A").
// They click "Prepend X". What do the inputs show?
```
**Answer:** Inputs show: `["X", "ADITYA", "B", "C"]` — which is wrong! The user's edit "ADITYA" stays at position 0 (key=0), but now key=0 corresponds to "X". React sees key=0 didn't change, reuses its DOM node (including the typed text "ADITYA") but updates the `defaultValue` prop. The uncontrolled input keeps "ADITYA" because React doesn't control it. Fix: use `item` as key when items are unique strings, or give items unique IDs.

---

## ⚫ Interview Questions + Answers

**Q1: Why do we need the `key` prop in lists?**
A1: React uses keys to identify which items in a list changed between renders. Without keys, React can only compare by position — if you remove item at position 0, it thinks ALL items shifted. With keys, React tracks by identity — it knows exactly which element was removed, added, or moved. This enables efficient DOM updates: only changed elements get updated, not the whole list.

**Q2: Why is using array index as key a bad practice?**
A2: When list items change order (sort), are added/removed from the middle, or are filtered, the index-to-item mapping changes. An item that was at index 0 might now be at index 2 — but React thinks key=0 is still the "same" item and tries to update it, causing bugs especially with local state. Use stable IDs from your data. Only use index if: the list never reorders, never filters, and items don't have local state.

**Q3: Where exactly should the `key` prop go?**
A3: The `key` goes on the **outermost element returned by the `.map()` callback** — the element directly inside the array. If you're returning a component, key goes on the component: `<Product key={p.id} />`. If returning a Fragment with multiple elements: `<Fragment key={id}>`. If returning plain HTML: `<li key={id}>`. It does NOT go deeper inside — React only looks at the top-level element returned from `.map()`.

**Q4: Can keys be the same in different lists?**
A4: Yes. Keys only need to be unique among SIBLINGS in the same list. A `key="1"` in one list and a `key="1"` in another list are fine — React tracks them per-parent. They don't need to be globally unique. What matters is uniqueness within `items.map(...)` of the same array.

**Q5: What happens when you use a non-stable key (like `Math.random()` or `Date.now()`)?**
A5: Every render generates new random keys — React sees all keys as "new" every render, unmounts all items and remounts them fresh. This causes: flickering UI, lost input state, slow rendering (creating DOM from scratch). It completely defeats the purpose of keys. Never use random values as keys. Keys should be stable across renders for the same logical item.

---

## 🔷 When to Use + When Not to Use
✅ **Use stable unique ID as key when:**
- Items come from database (use `id` field)
- Items are created by user (assign UUID or timestamp ID on creation)
- List can be sorted, filtered, or reordered

✅ **Index as key is acceptable ONLY when:**
- Static list that never changes order
- Items have no local state or animations
- No insert/remove from middle

❌ **Never use:**
- `Math.random()` or `Date.now()` as key
- Non-unique values (category, type) as key
- Omitting key entirely (React warning, poor performance)

---

## 📊 Visual Diagram

```
LIST RENDERING WITH .map():
────────────────────────────────────────────────
  Data Array:                JSX Array:
  [                          [
    { id: 1, name: 'Pizza' }   <li key="1">Pizza</li>
    { id: 2, name: 'Burger'}   <li key="2">Burger</li>
    { id: 3, name: 'Pasta' }   <li key="3">Pasta</li>
  ]                          ]

KEY MATCHING ON UPDATE (remove id=2):
────────────────────────────────────────────────
  Old Virtual DOM:    New Virtual DOM:
  key="1" Pizza  ───► key="1" Pizza   (unchanged ✅)
  key="2" Burger  ──► (removed ✅)
  key="3" Pasta  ───► key="3" Pasta   (unchanged ✅)
  Real DOM: remove exactly <li>Burger</li>

WITHOUT KEY (index-based):
────────────────────────────────────────────────
  Old:            After removing index 1:
  [0] Pizza  ──►  [0] Pizza    (same ✅)
  [1] Burger ──►  [1] Pasta    (UPDATE: Burger→Pasta ⚠️)
  [2] Pasta  ──►  [2] removed  (REMOVE last ⚠️)
  React does 2 operations instead of 1!
  Worse: any local state (input values) shifts with wrong item
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| List rendering | .map() array to JSX elements | Array को JSX elements में convert करना |
| key prop | Unique identifier for list items | List items के लिए unique identifier |
| Stable key | Same item → same key across renders | Same item का हर render पर same key |
| Sibling uniqueness | Keys unique within same list | एक ही list में unique keys |
| Reconciliation | React's update algorithm | React का update algorithm |
| Remount | Destroy + recreate DOM element | DOM element destroy + recreate करना |

---

## ⚡ 3-Line Summary
**English:**
1. Use `.map()` to render arrays of data as JSX — always provide a `key` prop on each returned element.
2. Keys must be unique among siblings and stable (same item = same key) — use database IDs, never array index for dynamic lists.
3. Wrong keys cause bugs: duplicate renders, lost state, performance problems — React uses keys to match old → new elements precisely.

**Hindi:**
1. Arrays को JSX render करने के लिए `.map()` use करो — हर returned element पर `key` prop ज़रूर दो।
2. Keys siblings में unique और stable होनी चाहिए (same item = same key) — database IDs use करो, dynamic lists में index नहीं।
3. Wrong keys bugs बनाते हैं: duplicate renders, lost state, performance problems — React keys से old → new elements precisely match करता है।

---

## ➡️ Next Topic
**25. Why key Prop is Important** — key prop की importance deep dive — state preservation और React's reconciliation से connection।
