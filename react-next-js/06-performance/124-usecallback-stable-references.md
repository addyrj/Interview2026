# 124. useCallback — Stable References
# हिंदी में: useCallback — Functions की Reference को Stable रखना

---

## 🔵 Simple Definition (English)
**`useCallback(fn, deps)`** returns the **same function object** between renders until its dependencies change. This keeps the function's identity (reference) stable, so `memo` children and `useEffect` dependency arrays do not see a "new" function on every render.

## 🔵 सरल परिभाषा (Hindi)
**`useCallback(fn, deps)`** renders के बीच **वही function object** लौटाता है जब तक dependencies न बदलें। इससे function की identity (reference) stable रहती है, इसलिए `memo` वाले children और `useEffect` के dependency array को हर render पर "नया" function नहीं दिखता।

---

## 🔴 Problem it Solves

In JavaScript, functions are objects. Every render creates a **new** function object, even if the code is the same. When you pass it as a prop to a `memo` child, the child sees `prevProps.onAdd !== nextProps.onAdd` and re-renders, so `memo` is wasted. In `useEffect`, a function in the deps array makes the effect run after every render.

```jsx
// PROBLEM: handleAdd is a new function each render → memo(ProductCard) always re-renders
function Page() {
  const [cart, setCart] = useState([]);
  const handleAdd = (id) => setCart((c) => [...c, id]);    // new identity each render
  return <ProductCard onAdd={handleAdd} />;
}
// SOLUTION: const handleAdd = useCallback((id) => setCart((c) => [...c, id]), []);
```

## 🔴 यह क्यों बना? (Hindi)
JavaScript में functions objects हैं। हर render एक **नया** function object बनाता है, चाहे code वही हो। उसे `memo` child को prop में दो तो child को `prevProps.onAdd !== nextProps.onAdd` दिखता है और वह re-render होता है, यानी `memo` बेकार। `useEffect` के deps में function हो तो effect हर render के बाद चलता है। `useCallback` identity स्थिर रखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → const fn = useCallback((x) => doSomething(x, a), [a])
Step 2 → First render: React stores the function and the deps
Step 3 → Next render: compare deps with Object.is
Step 4 → Equal → return the STORED function (same reference)
Step 5 → Different → store and return the NEW function
Step 6 → A memo child (or effect) compares function props/deps by reference → sees "no change" → skips

Remember:
  useCallback does NOT make the function faster and does NOT stop the function from being created
  (the arrow function is still created each render; React just returns the old one)
  It only pays off when something compares the reference: memo, useEffect deps, useMemo deps
  Tip: functional updates setX(prev => ...) avoid putting state in deps
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → const fn = useCallback((x) => doSomething(x, a), [a])
Step 2 → पहला render: React function और deps store करता है
Step 3 → अगला render: deps की Object.is से तुलना
Step 4 → बराबर → STORED function लौटाओ (वही reference)
Step 5 → अलग → नया function store करके लौटाओ
Step 6 → memo child (या effect) function props/deps को reference से compare करता है → "बदलाव नहीं" → skip

याद रखो:
  useCallback function को तेज़ नहीं बनाता और function बनने से रोकता भी नहीं
  (arrow function हर render में बनता है; React बस पुराना लौटा देता है)
  फायदा तभी है जब कोई reference compare करे: memo, useEffect deps, useMemo deps
  Tip: functional updates setX(prev => ...) से state को deps में डालने की ज़रूरत नहीं पड़ती
```

---

## 🟡 Real World Example
**Swiggy menu page:** A restaurant menu has 80 `DishRow` components, each with an "ADD" button. When the user adds a dish, the cart total at the top updates. Each `DishRow` receives `onAdd`. If `onAdd` is recreated every render, all 80 rows re-render on every add, and the page stutters on low-end phones. With `useCallback` plus `memo`, only the cart total re-renders.

## 🟡 Real Example Hindi mein
**Swiggy menu page:** Restaurant menu में 80 `DishRow` components हैं और हर में "ADD" button है। User dish add करता है तो ऊपर cart total update होता है। हर `DishRow` को `onAdd` मिलता है। अगर `onAdd` हर render में नया बने तो हर add पर सभी 80 rows re-render होती हैं और low-end phones पर page अटकता है। `useCallback` और `memo` साथ में हों तो सिर्फ cart total re-render होता है।

---

## 💻 Code Example — Basic

```jsx
// Basic useCallback: prove that a memoized child skips when the handler is stable
import { useState, useCallback, memo } from 'react';
import { createRoot } from 'react-dom/client';

const AddButton = memo(function AddButton({ onAdd }) {         // memo compares onAdd by reference
  console.log('AddButton rendered');
  return <button onClick={onAdd}>Add dish</button>;
});

function App() {
  const [count, setCount] = useState(0);                        // cart count
  const [theme, setTheme] = useState('light');                  // unrelated state

  const handleAdd = useCallback(() => {
    setCount((c) => c + 1);                                      // functional update → no dependency on count
  }, []);                                                        // empty deps: same function forever

  return (
    <div className={theme}>
      <p>Items: {count}</p>
      <AddButton onAdd={handleAdd} />                            {/* stable → skipped on theme change */}
      <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>Toggle theme</button>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: stable handlers for a list, useEffect dependency, and the "latest ref" pattern
import { useState, useCallback, useEffect, useRef, memo } from 'react';
import { createRoot } from 'react-dom/client';

const DishRow = memo(function DishRow({ dish, qty, onChange }) {
  console.log('row', dish.id);                                   // only changed rows should log
  return (
    <li>
      {dish.name} ({qty})
      <button onClick={() => onChange(dish.id, +1)}>+</button>   {/* inline arrow is fine: the ROW is memoized */}
      <button onClick={() => onChange(dish.id, -1)}>-</button>
    </li>
  );
});

const DISHES = [
  { id: 1, name: 'Paneer Tikka' },
  { id: 2, name: 'Masala Dosa' },
  { id: 3, name: 'Veg Biryani' },
];

function Menu() {
  const [qtys, setQtys] = useState({});                          // { dishId: quantity }

  // ONE stable handler for all rows. Functional update → deps stay empty.
  const changeQty = useCallback((id, delta) => {
    setQtys((prev) => ({ ...prev, [id]: Math.max(0, (prev[id] ?? 0) + delta) }));
  }, []);

  // useEffect with a function dependency: only re-runs when the function changes (never here)
  const logCart = useCallback(() => {
    console.log('cart snapshot', qtys);                          // reads qtys → so it depends on [qtys]
  }, [qtys]);
  useEffect(() => { logCart(); }, [logCart]);                    // runs whenever qtys changes

  // "Latest ref" pattern: stable function that always sees the latest value without changing identity
  const qtysRef = useRef(qtys);
  qtysRef.current = qtys;                                        // update ref on each render (see note)
  const getTotal = useCallback(
    () => Object.values(qtysRef.current).reduce((s, n) => s + n, 0),
    []                                                           // stable forever
  );

  return (
    <div>
      <p>Total items: {getTotal()}</p>
      <ul>
        {DISHES.map((d) => (
          <DishRow key={d.id} dish={d} qty={qtys[d.id] ?? 0} onChange={changeQty} /> // only the changed row re-renders
        ))}
      </ul>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Menu />);
// Note: writing ref.current during render is tolerated for this "latest value" pattern but the
// React docs prefer updating refs in an effect/event handler; React 19 has `useEffectEvent` (stable in
// newer releases, version-dependent) for the same need.
```

Re-render behavior: clicking "+" on one dish updates `qtys`, so `Menu` re-renders. `changeQty` is stable, and the `qty` prop of other rows is the same number, so only the changed `DishRow` re-renders. Performance impact: with 80 rows this is the difference between one row render and 80 per click.

---

## 🟠 Next.js Connection

Server Components cannot pass functions to Client Components (functions are not serializable), except Server Actions. So `useCallback` matters only inside Client Components. In Next.js, a common use is stable event handlers for memoized list rows or a stable callback passed to a third-party client library.

```jsx
// app/menu/Menu.jsx
'use client';                                                    // callbacks live on the client
import { useCallback, useState, memo } from 'react';

const Row = memo(function Row({ id, name, onSelect }) {
  return <li onClick={() => onSelect(id)}>{name}</li>;
});

export default function Menu({ dishes }) {                        // `dishes` is serializable data from the server
  const [selected, setSelected] = useState(null);
  const onSelect = useCallback((id) => setSelected(id), []);      // stable function created on the client
  return (
    <>
      <p>Selected: {selected}</p>
      <ul>{dishes.map((d) => <Row key={d.id} id={d.id} name={d.name} onSelect={onSelect} />)}</ul>
    </>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `useCallback` without `memo` on the receiving component
✅ **Correct:** Wrap the child in `memo` (or use the function in a dependency array)

```jsx
// Wrong: Child is not memoized → it re-renders anyway; useCallback only adds overhead
const onClick = useCallback(() => doIt(), []);
return <Child onClick={onClick} />;                                       // ❌ Child = plain component

// Right
const Child2 = memo(function Child2({ onClick }) { return <button onClick={onClick}>Go</button>; }); // ✅
```

❌ **Mistake 2:** Missing dependencies (stale closure)
✅ **Correct:** Include every value the callback reads, or use functional updates

```jsx
// Wrong: count is captured as 0 forever → button only ever sets 1
const inc = useCallback(() => setCount(count + 1), []);                   // ❌ stale closure

// Right
const inc2 = useCallback(() => setCount((c) => c + 1), []);               // ✅ no dependency needed
```

❌ **Mistake 3:** Creating a new inline function for a memoized child anyway
✅ **Correct:** Pass the stable function, not a fresh wrapper

```jsx
// Wrong: wrapper arrow is new every render → memo defeated even though handleAdd is stable
<ProductCard onAdd={() => handleAdd(product.id)} />                       // ❌

// Right: let the child call handleAdd(product.id) itself
<ProductCard product={product} onAdd={handleAdd} />                       // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
function App() {
  const [count, setCount] = useState(0);
  const log = useCallback(() => console.log(count), []);   // empty deps
  return (
    <>
      <button onClick={() => setCount(count + 1)}>+</button>
      <button onClick={log}>Log</button>
    </>
  );
}
```
**Answer:** Clicking "+" three times and then "Log" prints `0`. The callback was created on the first render with `count = 0` captured in its closure, and with `[]` deps React keeps returning that first function. This is a **stale closure**. Fix: add `[count]` to the deps (the function changes whenever count changes), or read the latest value from a ref. This is the most common `useCallback` bug in interviews.

---

## ⚫ Interview Questions + Answers

Q1: What does `useCallback` do?
A1: It returns a memoized function that keeps the same reference between renders until its dependencies change. It prevents unnecessary re-renders of memoized children and unnecessary effect runs.

Q2: How are `useCallback` and `useMemo` related?
A2: `useCallback(fn, deps)` is the same as `useMemo(() => fn, deps)`. `useMemo` caches a value, `useCallback` caches the function itself.

Q3: Does `useCallback` prevent the function from being recreated?
A3: No. The inline function is still created each render; React just returns the previously stored one when deps are unchanged. The benefit comes from the stable reference, not from avoiding allocation.

Q4: When is `useCallback` pointless?
A4: When the child is not memoized, when it is not used in any dependency array, or when deps change on every render. Then you pay for the comparison with no gain.

Q5: How do you avoid stale closures?
A5: Put all used reactive values in the deps, use functional state updates (`setX(prev => ...)`), or keep the latest value in a ref. The `exhaustive-deps` ESLint rule catches missing dependencies.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Passing a handler to a `memo`-wrapped child (especially list items)
- A function is a dependency of `useEffect`, `useMemo` or another `useCallback`
- Building custom hooks that return functions consumers may put in dependency arrays

❌ **Avoid when:**
- The child is not memoized or the component rarely re-renders
- The handler is used only on a DOM element (`<button onClick>`): DOM elements do not care about identity
- You can restructure (move the function inside the effect, or move state down)

---

## 📊 Visual Diagram

```
 Without useCallback                          With useCallback(fn, [])
 ───────────────────                          ────────────────────────
 render 1: onAdd = fnA                        render 1: onAdd = fnA (stored)
 render 2: onAdd = fnB  (fnA !== fnB)         render 2: onAdd = fnA (same ref)
              │                                           │
   memo(Child) sees a change                   memo(Child) sees NO change
              │                                           │
        Child re-renders ❌                          Child skipped ✅

 Stale closure trap:  useCallback(() => log(count), [])  ──► always the count from render 1
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| useCallback | Cache a function reference | Function reference को cache करना |
| Referential equality | Same object in memory | Memory में वही object |
| Stale closure | Function remembers old values | Function पुरानी values याद रखे |
| Functional update | setState(prev => next) | पिछली state से नई state बनाना |
| Dependency array | Values that invalidate the cache | Cache अमान्य करने वाली values |
| memo | Skip render if props unchanged | Props वही हों तो render छोड़ना |
| exhaustive-deps | ESLint rule for hook deps | Hook deps की ESLint जाँच |
| Ref | Mutable box that survives renders | Renders के पार टिकने वाला box |

---

## ⚡ 3-Line Summary
**English:**
1. `useCallback` keeps a function's reference stable until its dependencies change.
2. It pays off only with `memo` children or dependency arrays; otherwise it is overhead.
3. Avoid stale closures with correct deps or functional updates.

**Hindi:**
1. `useCallback` function की reference को तब तक stable रखता है जब तक dependencies न बदलें।
2. फायदा सिर्फ `memo` children या dependency arrays के साथ है; वरना यह अतिरिक्त बोझ है।
3. सही deps या functional updates से stale closure से बचो।

---

## ➡️ Next Topic
**125. When NOT to Optimize** — `memo`, `useMemo`, `useCallback` सीखने के बाद सबसे ज़रूरी सबक: कब ये tools नहीं लगाने चाहिए और premature optimization से कैसे बचें।
