# 35. useState — Deep Dive
# हिंदी में: useState की गहराई — Batching, Updater, Lazy Init और Stale Closure

---

## 🔵 Simple Definition (English)
`useState` stores a value that React remembers between renders. It returns `[value, setValue]`. Calling `setValue` does not change the variable right away; it **schedules a re-render** in which `value` has the new content. Each render sees its own fixed snapshot of state.

## 🔵 सरल परिभाषा (Hindi)
`useState` ऐसी value रखता है जिसे React renders के बीच याद रखता है। यह `[value, setValue]` return करता है। `setValue` call करने से variable तुरंत नहीं बदलता; यह **re-render schedule** करता है जिसमें `value` की नई content होती है। हर render को state का अपना fixed snapshot दिखता है।

---

## 🔴 Problem it Solves

Normal local variables are re-created on every render and changing them does not update the UI. Before Hooks, state needed classes. The basics of `useState` are simple, but several details cause real bugs and interview questions: updates that look sequential but are batched, stale values inside timers and handlers, state objects that must be copied, expensive initial values computed on every render, and updates that React ignores because the value did not change.

```jsx
// PROBLEM 1: normal variable → UI never updates
function Bad() {
  let count = 0;
  return <button onClick={() => { count++; }}>{count}</button>;   // ❌ count resets, no re-render
}

// PROBLEM 2: three calls, but only +1 (snapshot + batching)
function Counter() {
  const [n, setN] = useState(0);
  const add3 = () => { setN(n + 1); setN(n + 1); setN(n + 1); };  // ❌ ends at 1, not 3
  return <button onClick={add3}>{n}</button>;
}
```

## 🔴 यह क्यों बना? (Hindi)
सामान्य local variables हर render पर दोबारा बनते हैं और उन्हें बदलने से UI update नहीं होता। Hooks से पहले state के लिए classes चाहिए थीं। `useState` की basics आसान हैं, पर कुछ details असली bugs और interview सवाल बनाती हैं: जो updates क्रम से चलते लगते हैं पर batch होते हैं, timers और handlers में पुरानी (stale) values, state objects जिन्हें copy करना पड़ता है, भारी initial value जो हर render पर गिनी जाती है, और ऐसे updates जिन्हें React ignore करता है क्योंकि value नहीं बदली।

---

## 🟢 How it Works — Step by Step

```
Step 1 → First render: React creates a slot for this useState, stores initial value
         (initializer function runs ONLY on the first render)
Step 2 → Function returns [state, setState]; `state` is a constant for THIS render
Step 3 → Event happens → setState(next) or setState(prev => next)
Step 4 → React queues the update (does NOT change `state` in the running code)
Step 5 → Batching: all updates in the same event/tick are grouped (React 18+: everywhere,
         including timeouts, promises and native handlers)
Step 6 → React processes the queue: applies updater functions in order, producing new state
Step 7 → Bail out: if new state is identical (Object.is) to current → skip render of children
Step 8 → Re-render: the function runs again; useState now returns the new value
Step 9 → Commit changes to DOM; effects with changed deps run

RULES
  Replace, don't mutate:  setUser({ ...user, city })     (objects/arrays are replaced, not merged)
  Based on previous?      setCount(c => c + 1)           (updater form)
  Expensive initial?      useState(() => compute())      (lazy initializer)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → पहला render: React इस useState के लिए slot बनाता है, initial value रखता है
         (initializer function सिर्फ पहले render पर चलता है)
Step 2 → Function [state, setState] return करता है; `state` इस render के लिए constant है
Step 3 → Event होता है → setState(next) या setState(prev => next)
Step 4 → React update को queue करता है (चल रहे code में `state` नहीं बदलता)
Step 5 → Batching: एक ही event/tick के सारे updates एक group में आते हैं (React 18+: हर जगह,
         timeouts, promises और native handlers में भी)
Step 6 → React queue process करता है: updater functions क्रम से लगती हैं, नई state बनती है
Step 7 → Bail out: अगर नई state (Object.is से) वही है → children का render skip
Step 8 → Re-render: function फिर चलता है; useState अब नई value देता है
Step 9 → DOM में commit; बदले deps वाले effects चलते हैं

नियम
  Mutate नहीं, replace करो:  setUser({ ...user, city })     (objects/arrays replace होते हैं, merge नहीं)
  पिछली value पर निर्भर?     setCount(c => c + 1)           (updater form)
  भारी initial value?        useState(() => compute())      (lazy initializer)
```

---

## 🟡 Real World Example
**Amazon cart quantity stepper:** The "+" button increments quantity, and a double-click should add 2. With `setQty(qty + 1)` rapid clicks inside the same event sometimes add 1, so the team uses `setQty(q => Math.min(q + 1, 10))`. The cart panel also reads saved items from `localStorage` once: `useState(() => JSON.parse(localStorage.getItem('cart') ?? '[]'))`, so parsing does not run on every keystroke elsewhere in the page. The address form stores an object and updates one field at a time with `{ ...address, pincode }`.

## 🟡 Real Example Hindi mein
**Amazon cart quantity stepper:** "+" बटन quantity बढ़ाता है और double-click से 2 बढ़ना चाहिए। `setQty(qty + 1)` से एक ही event में तेज़ clicks कभी-कभी सिर्फ 1 जोड़ते हैं, इसलिए team `setQty(q => Math.min(q + 1, 10))` इस्तेमाल करती है। Cart panel `localStorage` से saved items सिर्फ एक बार पढ़ता है: `useState(() => JSON.parse(localStorage.getItem('cart') ?? '[]'))`, ताकि page पर कहीं और typing के समय parsing बार-बार न चले। Address form एक object रखता है और `{ ...address, pincode }` से एक-एक field बदलता है।

---

## 💻 Code Example — Basic

```jsx
// The five core behaviors of useState in one file
import { useState } from 'react';
import { createRoot } from 'react-dom/client';

function Demo() {
  // 1) Basic value
  const [count, setCount] = useState(0);                        // initial value 0

  // 2) Updater form: safe when the next value depends on the previous one
  const addThree = () => {
    setCount((c) => c + 1);                                     // queue: 0 → 1
    setCount((c) => c + 1);                                     // queue: 1 → 2
    setCount((c) => c + 1);                                     // queue: 2 → 3  → one re-render, count = 3
  };

  // 3) Object state: replace, never mutate
  const [user, setUser] = useState({ name: 'Asha', city: 'Pune' });
  const moveToDelhi = () => setUser({ ...user, city: 'Delhi' }); // copy + override one key

  // 4) Array state: create a new array
  const [tags, setTags] = useState(['veg']);
  const addTag = () => setTags([...tags, 'spicy']);              // not tags.push(...)

  // 5) Lazy initializer: runs only on the first render
  const [saved] = useState(() => {
    console.log('expensive init runs once');                     // appears once, not on every render
    return JSON.parse(localStorage.getItem('saved') ?? '[]');
  });

  console.log('render', count);                                  // shows each render
  return (
    <div>
      <button onClick={() => setCount(count + 1)}>+1 ({count})</button>
      <button onClick={addThree}>+3</button>
      <button onClick={moveToDelhi}>{user.name} lives in {user.city}</button>
      <button onClick={addTag}>Tags: {tags.join(', ')}</button>
      <p>Saved items: {saved.length}</p>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Demo />);
```

## 💻 Code Example — Advanced

```jsx
// Real world: checkout form with grouped state, derived values, stale-closure fix and reset by key
import { useState, useEffect, useRef } from 'react';

const initialAddress = { name: '', pincode: '', city: '' };   // outside: stable reference

export function AddressForm({ onSave }) {
  const [address, setAddress] = useState(initialAddress);     // one object for related fields
  const [saving, setSaving] = useState(false);                // separate state for unrelated UI flag

  // Generic field updater: functional form avoids stale state when typing fast
  const update = (field) => (e) =>
    setAddress((prev) => ({ ...prev, [field]: e.target.value }));

  // Derived value: compute during render, do NOT put it in state
  const isValid = address.name.trim() !== '' && /^\d{6}$/.test(address.pincode);

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);                                          // update 1 (batched)
    try {
      await onSave(address);                                  // async work
      setAddress(initialAddress);                             // update 2 after await: still batched in React 18+
    } finally {
      setSaving(false);                                       // update 3
    }
  };

  return (
    <form onSubmit={submit}>
      <input placeholder="Name" value={address.name} onChange={update('name')} />
      <input placeholder="Pincode" value={address.pincode} onChange={update('pincode')} />
      <input placeholder="City" value={address.city} onChange={update('city')} />
      <button disabled={!isValid || saving}>{saving ? 'Saving...' : 'Save address'}</button>
    </form>
  );
}

// Stale closure example: interval that reads state
export function AutoCounter() {
  const [count, setCount] = useState(0);
  const countRef = useRef(count);
  countRef.current = count;                                   // always holds the latest value

  useEffect(() => {
    const id = setInterval(() => {
      // BAD: setCount(count + 1) here would use the count from the FIRST render forever
      setCount((c) => c + 1);                                 // GOOD: updater reads the latest
      console.log('latest via ref:', countRef.current);       // GOOD: ref for read-only access
    }, 1000);
    return () => clearInterval(id);                           // cleanup
  }, []);                                                     // empty deps are now safe

  return <p>Seconds: {count}</p>;
}

// Reset all state of a component by changing its key (instead of many setState calls)
export function CheckoutPage({ userId, onSave }) {
  return <AddressForm key={userId} onSave={onSave} />;        // new userId → fresh form state
}
```

---

## 🟠 Real App Integration

In Next.js, `useState` works only in **Client Components** (`'use client'`). A Server Component cannot hold state, so the usual pattern is: fetch on the server, pass data as props, and keep only the interactive part in a small client component. Initial state from props is read **once**; later prop changes do not reset state unless you use a `key`. Never read `localStorage` or `window` in the initial value without a guard, because the component also renders on the server (hydration mismatch).

```jsx
// app/cart/CartCounter.jsx
'use client';                                              // required to use hooks

import { useState } from 'react';

export default function CartCounter({ initialQty }) {      // value comes from a Server Component
  const [qty, setQty] = useState(initialQty);              // used only for the first render
  return (
    <div>
      <button onClick={() => setQty((q) => Math.max(0, q - 1))}>-</button>
      <span>{qty}</span>
      <button onClick={() => setQty((q) => Math.min(10, q + 1))}>+</button>
    </div>
  );
}
```

```jsx
// app/cart/page.jsx — Server Component
import CartCounter from './CartCounter';

export default async function Page() {
  const cart = await fetch('https://api.example.com/cart', { cache: 'no-store' }).then((r) => r.json());
  // key={cart.version} resets the client state when the server sends a new cart version
  return <CartCounter key={cart.version} initialQty={cart.qty} />;
}
```

```jsx
// SAFE localStorage default in Next.js (avoid hydration mismatch)
'use client';
import { useState, useEffect } from 'react';

export function useSavedTheme() {
  const [theme, setTheme] = useState('light');             // same value on server and first client render
  useEffect(() => {
    setTheme(localStorage.getItem('theme') ?? 'light');    // read only after mount, in the browser
  }, []);
  return [theme, setTheme];
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Mutating state directly
✅ **Correct:** Create a new object or array

```jsx
// Wrong: same reference → React bails out, UI does not update
const [cart, setCart] = useState([]);
cart.push('biryani');             // ❌ mutation
setCart(cart);                    // ❌ same array, no re-render

// Right
setCart([...cart, 'biryani']);    // ✅ new array
```

❌ **Mistake 2:** Reading state right after setting it
✅ **Correct:** Use the next value you computed, or an effect, or the updater form

```jsx
// Wrong: `count` is the old snapshot within this render
setCount(count + 1);
console.log(count);               // ❌ prints the OLD value

// Right
const next = count + 1;
setCount(next);
console.log(next);                // ✅ the value you actually set
```

❌ **Mistake 3:** Storing derived data in state (two sources of truth)
✅ **Correct:** Compute it during render

```jsx
// Wrong: total can go out of sync with items
const [items, setItems] = useState([]);
const [total, setTotal] = useState(0);        // ❌ must be updated everywhere items change

// Right
const [items2, setItems2] = useState([]);
const total2 = items2.reduce((s, i) => s + i.price, 0);   // ✅ always correct
```

❌ **Mistake 4:** Passing a function to `useState` by accident, or calling an expensive function on every render
✅ **Correct:** Pass a function reference (lazy init), not the call

```jsx
// Wrong: loadCart() runs on EVERY render (the result is ignored after the first)
const [cart, setCart] = useState(loadCart());          // ❌

// Right: React calls it once
const [cart2, setCart2] = useState(loadCart);          // ✅ or useState(() => loadCart())
```

---

## 🧠 Tricky Interview Question

```jsx
function App() {
  const [count, setCount] = useState(0);

  function handleClick() {
    setCount(count + 1);
    setCount(count + 1);
    setCount((c) => c + 1);
    setCount(count + 5);
    setCount((c) => c + 1);
  }

  console.log('render', count);
  return <button onClick={handleClick}>{count}</button>;
}
```
Question: What is `count` after one click, and how many renders happen for that click?

**Answer:** `count` becomes **6**, with **one** extra render. React processes the queue in order: start `0`. `setCount(1)` → 1. `setCount(1)` → 1. `c => c + 1` → 2. `setCount(5)` replaces the value with 5. `c => c + 1` → 6. Plain values replace the state; updater functions receive the result of the queue so far. All five calls are batched, so React renders once and logs `render 6`.

---

## ⚫ Interview Questions + Answers

Q1: Why is state update asynchronous (or "not immediate")?
A1: React batches updates and applies them at the next render. `setState` only schedules work, and the `state` variable in the current render is a constant snapshot. To use the new value, read it in the next render, an effect, or compute it before setting.

Q2: When should you use the updater form `setState(prev => ...)`?
A2: Whenever the new value depends on the previous one, especially for repeated updates in one event, timers, async callbacks, and effects with empty dependencies. It always receives the latest queued value, so it avoids stale closures.

Q3: What is lazy initialization?
A3: `useState(() => expensive())` makes React call the function only on the first render. `useState(expensive())` calls it on every render (the result is ignored after the first), which wastes time for work like parsing localStorage or building a big array.

Q4: Does `setState` merge objects like class `setState`?
A4: No. `useState` replaces the value. For objects, spread the old one: `setUser(prev => ({ ...prev, city }))`. Alternatively split unrelated fields into separate `useState` calls, or use `useReducer` for complex shapes.

Q5: When does React skip a re-render after `setState`?
A5: When the new value is identical to the current one by `Object.is`. React may still call the component once more before bailing out, but it will not render children or run effects. Mutating and re-setting the same object always hits this bail-out, which is why mutation fails.

---

## 🔷 When to Use + When Not to Use
✅ **Use `useState` when:**
- A value changes over time and the UI must reflect it (inputs, toggles, counters, selected tab)
- The state is local to one component or a small subtree
- State is simple (primitive or a small object)

❌ **Avoid / choose something else when:**
- The value can be computed from props or other state (derive it during render)
- A value changes without needing a re-render (use `useRef`)
- State logic is complex with many related transitions (use `useReducer`), or state is shared widely (Context, Zustand, Redux Toolkit)
- The data comes from a server (use TanStack Query, SWR, or Server Components)

---

## 📊 Visual Diagram

```
 RENDER 1  (count = 0)                                 RENDER 2  (count = 1)
 ┌────────────────────────────────┐                    ┌────────────────────────────────┐
 │ const [count,setCount]=useState│                    │ const [count,setCount]=useState│
 │          count = 0  (constant) │                    │          count = 1  (constant) │
 │ onClick → setCount(count + 1)  │ ── queue ────────▶ │                                │
 └────────────────────────────────┘    update(+1)      └────────────────────────────────┘
                                          │ batched
                                          ▼
   React state slot:  [ 0 ]  ──queue: [c=>c+1, c=>c+1]──▶  process in order ──▶  [ 2 ]
                                                              │
                                      same value (Object.is)? ─ yes → skip render
                                                              └ no  → re-render + commit

 Re-render behavior:
  • setState with a NEW value → this component AND its children re-render (unless memo)
  • setState with the SAME value → bail out (no children render)
  • Several setState in one event → ONE render
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| State | Data React remembers between renders | Renders के बीच React द्वारा याद रखा डेटा |
| Snapshot | State value fixed for one render | एक render की fixed state value |
| Batching | Grouping several updates into one render | कई updates को एक render में जोड़ना |
| Updater function | `setX(prev => next)` | `setX(prev => next)` वाला function |
| Lazy initializer | Function that computes initial state once | Initial state एक बार गिनने वाला function |
| Stale closure | Function using an old state value | पुरानी state value इस्तेमाल करने वाला function |
| Bail out | React skips render when state is unchanged | State न बदलने पर render skip करना |
| Derived state | Value computed from other state/props | दूसरी state/props से निकाली गई value |

---

## ⚡ 3-Line Summary
**English:**
1. `useState` returns a snapshot value and a setter that schedules a re-render; updates are batched and never mutate the current variable.
2. Use the updater form for updates based on previous state, lazy initializers for expensive initial values, and copies for objects and arrays.
3. Derive values instead of storing them, and remember that the same value (`Object.is`) causes no re-render.

**Hindi:**
1. `useState` एक snapshot value और setter देता है जो re-render schedule करता है; updates batch होते हैं और मौजूदा variable को कभी नहीं बदलते।
2. पिछली state पर निर्भर updates के लिए updater form, भारी initial value के लिए lazy initializer, और objects व arrays के लिए copy इस्तेमाल करो।
3. Values को state में रखने की जगह derive करो, और याद रखो कि वही value (`Object.is`) होने पर re-render नहीं होता।

---

## ➡️ Next Topic
**36. useEffect — Complete Guide** — State बदलने के बाद side effects (fetch, subscription, timer) कैसे चलाएँ, यह `useEffect` सिखाता है.
