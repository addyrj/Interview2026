# 122. React.memo — Prevent Re-renders
# हिंदी में: React.memo — अनावश्यक Re-renders रोकना

---

## 🔵 Simple Definition (English)
**`React.memo`** wraps a component and makes React skip re-rendering it when its **props are the same** as last time (compared with `Object.is` per prop, shallowly). It only helps when a parent re-renders but the child's props did not change.

## 🔵 सरल परिभाषा (Hindi)
**`React.memo`** किसी component को wrap करता है और अगर उसके **props पिछली बार जैसे ही हैं** (हर prop की `Object.is` से shallow comparison) तो React उसे दोबारा render करना छोड़ देता है। यह तभी मदद करता है जब parent re-render हो पर child के props न बदले हों।

---

## 🔴 Problem it Solves

By default, when a parent re-renders, **all its children re-render**, even if their props are identical. In a page with a typing input and a heavy 500-card list, each keystroke re-renders every card. The work is wasted because the output would be the same.

```jsx
// PROBLEM: typing in the input re-renders every ProductCard
function Page({ products }) {
  const [q, setQ] = useState('');
  return (
    <>
      <input value={q} onChange={(e) => setQ(e.target.value)} />
      {products.map((p) => <ProductCard key={p.id} product={p} />)}  {/* all re-render per key */}
    </>
  );
}
// SOLUTION: const ProductCard = memo(function ProductCard({ product }) { ... });
```

## 🔴 यह क्यों बना? (Hindi)
Default रूप से parent re-render होने पर **उसके सभी children भी re-render होते हैं**, चाहे props बिलकुल वही हों। जिस page पर typing वाला input और 500 cards की भारी list हो, वहाँ हर keystroke पर हर card re-render होता है। यह काम बेकार है क्योंकि output वही रहेगा। `memo` ऐसे children को छोड़ देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → const Card = memo(function Card(props) { ... })
Step 2 → Parent re-renders and "calls" <Card ... /> with props
Step 3 → React compares each new prop with the old prop using Object.is (shallow)
Step 4 → ALL equal → skip rendering Card (reuse the previous result)
Step 5 → ANY different → render Card normally
Step 6 → Card's own state or context changes ALWAYS re-render it (memo only guards against parent renders)

Gotchas:
  objects/arrays/functions created inline are NEW each render  → memo is defeated
  fix: stabilize with useMemo / useCallback, or move constants outside the component
  optional 2nd argument memo(Component, areEqual) for custom comparison (use rarely)
  React Compiler (React 19 era, opt-in) can auto-memoize; version-dependent
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → const Card = memo(function Card(props) { ... })
Step 2 → Parent re-render होता है और <Card ... /> को props के साथ "call" करता है
Step 3 → React हर नए prop को पुराने से Object.is (shallow) से compare करता है
Step 4 → सब बराबर → Card को render करना छोड़ो (पिछला result reuse)
Step 5 → कोई भी अलग → Card सामान्य रूप से render होता है
Step 6 → Card की अपनी state या context बदले तो वह हमेशा re-render होता है (memo सिर्फ parent के renders से बचाता है)

Gotchas:
  Inline बने object/array/function हर render में NEW होते हैं → memo बेकार हो जाता है
  Fix: useMemo / useCallback से stable करो, या constants को component के बाहर रखो
  वैकल्पिक दूसरा argument memo(Component, areEqual) custom comparison के लिए (कम इस्तेमाल करो)
  React Compiler (React 19 दौर, opt-in) अपने आप memoize कर सकता है; version-dependent
```

---

## 🟡 Real World Example
**Amazon search results page:** The left filter panel updates state (price slider) at 60 events per second while dragging. The right side has 48 `ProductCard` components. Without `memo`, every slider move re-renders all 48 cards. With `memo`, cards whose `product` prop is unchanged are skipped, and the slider stays smooth.

## 🟡 Real Example Hindi mein
**Amazon search results page:** बाएँ filter panel की state (price slider) drag करते समय प्रति सेकंड 60 बार बदलती है। दाईं तरफ 48 `ProductCard` components हैं। `memo` के बिना slider की हर हरकत पर सभी 48 cards re-render होते हैं। `memo` से जिन cards का `product` prop नहीं बदला वे skip हो जाते हैं और slider smooth रहता है।

---

## 💻 Code Example — Basic

```jsx
// Basic React.memo: count renders to prove the child is skipped
import { useState, memo } from 'react';                       // memo is a named export
import { createRoot } from 'react-dom/client';

let renders = 0;                                               // simple render counter (demo only)

const Greeting = memo(function Greeting({ name }) {            // memoized child
  renders += 1;                                                // increments only when it really renders
  console.log('Greeting rendered', renders);
  return <p>Hello, {name}</p>;
});

function App() {
  const [count, setCount] = useState(0);                       // unrelated parent state
  return (
    <div>
      <button onClick={() => setCount(count + 1)}>Clicked {count}</button> {/* re-renders App */}
      <Greeting name="Aditya" />                               {/* same string prop → skipped */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
// Click the button 5 times: App renders 6 times, Greeting renders once.
```

## 💻 Code Example — Advanced

```jsx
// Advanced: memo + useCallback + useMemo + custom comparator, on a product grid
import { useState, useCallback, useMemo, memo } from 'react';
import { createRoot } from 'react-dom/client';

const PRODUCTS = Array.from({ length: 200 }, (_, i) => ({ id: i, name: `Item ${i}`, price: 100 + i }));

// Child: memoized. Receives a stable `onAdd` and a stable `product` reference.
const ProductCard = memo(function ProductCard({ product, onAdd }) {
  console.log('render card', product.id);                       // watch the console while typing
  return (
    <li>
      {product.name} — ₹{product.price}
      <button onClick={() => onAdd(product.id)}>Add</button>    {/* calls the stable handler */}
    </li>
  );
});

// Custom comparator example: ignore `onAdd` identity, compare only product.id and price
const PriceTag = memo(
  function PriceTag({ product, onClick }) {
    return <span onClick={onClick}>₹{product.price}</span>;
  },
  (prev, next) => prev.product.id === next.product.id && prev.product.price === next.product.price
  // WARNING: ignoring onClick is only safe if the handler never closes over changing values
);

function Catalog() {
  const [query, setQuery] = useState('');                        // frequent state (typing)
  const [cart, setCart] = useState([]);                          // cart ids

  // Stable function identity: functional update avoids depending on `cart`
  const handleAdd = useCallback((id) => setCart((c) => [...c, id]), []);

  // Stable list identity unless `query` changes
  const visible = useMemo(
    () => PRODUCTS.filter((p) => p.name.toLowerCase().includes(query.toLowerCase())),
    [query]
  );

  return (
    <div>
      <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Filter" />
      <p>Cart items: {cart.length}</p>                           {/* changes on Add → cards still skip */}
      <ul>
        {visible.map((p) => (
          <ProductCard key={p.id} product={p} onAdd={handleAdd} /> // same props → skipped on cart change
        ))}
      </ul>
      <PriceTag product={PRODUCTS[0]} onClick={() => {}} />
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Catalog />);
```

Re-render behavior: adding to the cart re-renders `Catalog` (cart length changed) but all 200 `ProductCard` elements are skipped because `product` (same object from `PRODUCTS`) and `onAdd` (stable) did not change. Typing a letter changes `visible`, so only the cards that remain in the list but have the same props are skipped, and new ones mount. Performance impact: each skipped card saves its render and diff; the price is one shallow comparison per prop per parent render, which is cheap for small prop lists.

---

## 🟠 Next.js Connection

Server Components never re-render on the client, so `memo` is irrelevant for them. Use `memo` inside Client Components (files with `'use client'`) where state changes frequently. A good Next.js pattern is to fetch data in a Server Component and pass plain props to a memoized client list.

```jsx
// app/products/ProductList.jsx
'use client';                                                   // client-only: has state
import { useState, useCallback, memo } from 'react';

const Row = memo(function Row({ item, onSelect }) {              // skipped when item/onSelect unchanged
  return <li onClick={() => onSelect(item.id)}>{item.name}</li>;
});

export default function ProductList({ items }) {                 // items come from a Server Component
  const [selected, setSelected] = useState(null);                // changing this must not re-render all rows
  const onSelect = useCallback((id) => setSelected(id), []);     // stable handler
  return (
    <>
      <p>Selected: {selected ?? 'none'}</p>
      <ul>{items.map((i) => <Row key={i.id} item={i} onSelect={onSelect} />)}</ul>
    </>
  );
}
```

Note: props passed from a Server Component to a Client Component are serialized; on a client re-render of the page after navigation, they are new objects, so `memo` compares them by reference and will re-render the rows once on a fresh payload. That is expected.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Passing a new object, array or function inline to a memoized child
✅ **Correct:** Stabilize with `useMemo` / `useCallback` or hoist constants

```jsx
// Wrong: style and onClick are new on every render → memo never skips
<Card style={{ color: 'red' }} onClick={() => open(id)} />               // ❌

// Right
const style = useMemo(() => ({ color: 'red' }), []);                      // ✅ stable object
const onClick = useCallback(() => open(id), [id]);                        // ✅ stable function
<Card style={style} onClick={onClick} />
```

❌ **Mistake 2:** Memoizing everything "just in case"
✅ **Correct:** Measure first (Profiler); memoize components that are expensive or render in large lists

```jsx
// Wrong: memo on a trivial component adds comparison cost + code noise
const Label = memo(({ text }) => <span>{text}</span>);                    // ❌ almost free to render

// Right: memo where rendering is costly
const HeavyChart = memo(function HeavyChart({ data }) { /* thousands of SVG nodes */ return null; }); // ✅
```

❌ **Mistake 3:** Passing `children` JSX to a memoized component
✅ **Correct:** `children` is a new element every parent render, so memo is defeated; pass stable elements (memoize them) or avoid memo there

```jsx
// Wrong: <b>x</b> creates a new element object each render → props.children differs
<MemoBox><b>x</b></MemoBox>                                               // ❌ memo skipped

// Right: hoist or memoize the child element
const label = useMemo(() => <b>x</b>, []);                                // ✅ stable element
<MemoBox>{label}</MemoBox>
```

---

## 🧠 Tricky Interview Question

```jsx
const Child = memo(function Child({ user }) {
  console.log('Child render');
  return <p>{user.name}</p>;
});

function Parent() {
  const [n, setN] = useState(0);
  const user = { name: 'Asha' };                      // object created in render
  return (
    <>
      <button onClick={() => setN(n + 1)}>{n}</button>
      <Child user={user} />
    </>
  );
}
```
**Answer:** `Child render` is logged on **every** click. `memo` compares props with `Object.is`, and `user` is a new object on each `Parent` render, so `prev.user !== next.user` even though the content is identical. Fix: move `user` outside the component, or `const user = useMemo(() => ({ name: 'Asha' }), [])`. Another subtle point: if `Child` also used a context, a context change would re-render it regardless of `memo`.

---

## ⚫ Interview Questions + Answers

Q1: What does `React.memo` do?
A1: It memoizes a component's rendered output and skips re-rendering when its props are shallowly equal to the previous props. It does not stop re-renders caused by the component's own state or context.

Q2: Why can `memo` fail to work?
A2: Unstable props: inline objects, arrays, functions or JSX children are new each render. Use `useMemo`, `useCallback` or hoist values so references stay the same.

Q3: `memo` vs `useMemo` vs `useCallback`?
A3: `memo` wraps a **component** and skips its render. `useMemo` caches a **computed value**. `useCallback` caches a **function** reference. They often work together: `useCallback` / `useMemo` produce stable props so `memo` can compare equal.

Q4: When should you use a custom comparison function?
A4: Rarely: when the default shallow equality is wrong or too strict (for example, deep data where only an `id` matters). A wrong comparator causes stale UI bugs, so prefer restructuring props.

Q5: Does `memo` help with context?
A5: No. If a component reads a context value that changes, it re-renders regardless. Split contexts or use selectors (Zustand, Redux `useSelector`) to limit re-renders.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- A component renders often with the same props (list items, table rows, chart cells)
- The component is expensive to render (big subtree, heavy calculations)
- You confirmed with the Profiler that it re-renders needlessly

❌ **Avoid when:**
- The component is tiny or its props change on almost every render anyway
- You cannot keep the props stable (it will only add comparison cost)
- You are optimizing without measuring

---

## 📊 Visual Diagram

```
 Parent re-renders (typing in input)
        │
        ├─► <Header />            (not memoized)  ─► re-renders
        │
        └─► <ProductCard product={p} onAdd={stable} />
                 │
                 ▼
          memo: compare props (Object.is)
                 │
        ┌────────┴─────────┐
   all equal            some differ
        │                   │
   SKIP render         render again
   (reuse output)

 Own state/context change inside ProductCard → always re-renders (memo cannot block)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| React.memo | Skip render if props are equal | Props बराबर हों तो render छोड़ना |
| Shallow comparison | Compare top-level props by reference | ऊपरी स्तर के props की reference से तुलना |
| Object.is | Equality used by React for props/state | React की equality जाँच |
| Referential equality | Same object in memory | Memory में वही object |
| Custom comparator | Second argument of memo | memo का दूसरा argument |
| Unstable prop | Prop recreated every render | हर render में दोबारा बनने वाला prop |
| Re-render | Calling the component function again | Component function को फिर चलाना |
| React Compiler | Tool that auto-memoizes (opt-in) | अपने आप memoize करने वाला tool |

---

## ⚡ 3-Line Summary
**English:**
1. `memo` skips a child's render when its props are shallowly equal to the previous props.
2. Stable props (via `useMemo`, `useCallback`, hoisting) are required, or memo does nothing.
3. Use it on expensive or list-item components after measuring, not everywhere.

**Hindi:**
1. `memo` child का render छोड़ देता है जब उसके props पिछले props से shallow बराबर हों।
2. Stable props (`useMemo`, `useCallback`, hoisting से) ज़रूरी हैं, वरना memo कुछ नहीं करता।
3. इसे measure करने के बाद महँगे या list-item components पर इस्तेमाल करो, हर जगह नहीं।

---

## ➡️ Next Topic
**123. useMemo — Expensive Calculations** — `memo` components को बचाता है, `useMemo` भारी values की गणना को। साथ ही stable references बनाने में भी यही काम आता है।
