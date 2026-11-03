# 201. Build Shopping Cart
# हिंदी में: Shopping Cart बनाना

> Code: [App.jsx](./App.jsx) (complete, tested with jsdom: add, quantity merge, remove, total, reducer edge case)

---

## 🔵 Simple Definition (English)
A **shopping cart** lets users add products, change quantities, remove items and see a live total. The standard React solution is a pure `useReducer` function plus context, with totals calculated from the items instead of stored.

## 🔵 सरल परिभाषा (Hindi)
**Shopping cart** में user products जोड़ता है, quantity बदलता है, items हटाता है और live total देखता है। React में standard हल है एक pure `useReducer` function और context, जिसमें total को store करने की जगह items से calculate किया जाता है।

---

## 🔴 Problem it Solves
Cart logic has many rules: adding the same product twice must increase quantity, quantity 0 must remove the line, totals must never go stale. Scattered `setState` calls break these rules. A reducer puts every rule in one pure function that is easy to read and test. Cart state is also needed in many places (header badge, cart page, checkout), so it must be shared.

## 🔴 यह क्यों बना? (Hindi)
Cart के कई rules होते हैं: एक product दो बार जोड़ने पर quantity बढ़नी चाहिए, quantity 0 होने पर line हट जानी चाहिए, total कभी पुराना नहीं होना चाहिए। बिखरे हुए `setState` calls ये rules तोड़ देते हैं। Reducer सारे rules एक pure function में रखता है जिसे पढ़ना और test करना आसान है। Cart state कई जगह चाहिए (header badge, cart page, checkout), इसलिए इसे share करना ज़रूरी है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → State shape: { items: [{ id, name, price, qty }] }  (no total stored)
Step 2 → cartReducer(state, action) handles ADD, REMOVE, SET_QTY, CLEAR immutably
Step 3 → CartProvider = useReducer + useMemo that DERIVES count and total
Step 4 → useEffect([items]) saves items to localStorage; lazy init loads them
Step 5 → Components call dispatch({ type, ... }) and read items/total from useCart()
Step 6 → Each dispatch returns a NEW state object, so React sees the change

Re-render: dispatch → reducer → new items array → Provider re-renders → all consumers.
Performance: fine for small carts; for big apps split state/dispatch contexts or use
Redux Toolkit / Zustand selectors so the header badge does not re-render with every field.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → State shape: { items: [{ id, name, price, qty }] }  (total store नहीं करते)
Step 2 → cartReducer(state, action) ADD, REMOVE, SET_QTY, CLEAR को immutably handle करता है
Step 3 → CartProvider = useReducer + useMemo जो count और total DERIVE करता है
Step 4 → useEffect([items]) items को localStorage में save करता है; lazy init उन्हें load करता है
Step 5 → Components dispatch({ type, ... }) करते हैं और useCart() से items/total पढ़ते हैं
Step 6 → हर dispatch NEW state object लौटाता है, इसलिए React को बदलाव दिखता है

Re-render: dispatch → reducer → नया items array → Provider re-render → सारे consumers।
Performance: छोटे cart के लिए ठीक; बड़े app में state/dispatch contexts अलग करो या
Redux Toolkit / Zustand selectors इस्तेमाल करो ताकि header badge हर बदलाव पर re-render न हो।
```

---

## 🟡 Real World Example
**Amazon / Flipkart cart:** Tapping "Add to cart" twice on the same mouse shows quantity 2 and not two rows. The header badge shows the total count, the cart page shows each line, and the price in the footer updates as you change quantity. Close the tab and come back, and the cart is still there.

## 🟡 Real Example Hindi mein
**Amazon / Flipkart cart:** एक ही mouse पर दो बार "Add to cart" दबाने से दो rows नहीं, quantity 2 दिखती है। Header badge कुल count दिखाता है, cart page हर line दिखाता है, और quantity बदलते ही footer की price बदलती है। Tab बंद करके लौटो तो भी cart वहीं मिलता है।

---

## 💻 Code Example — Basic

```jsx
// Basic cart with useState: add and count only
import { useState } from 'react';                    // state hook
import { createRoot } from 'react-dom/client';       // root API

function App() {
  const [items, setItems] = useState([]);            // cart lines

  const add = (name) => {
    setItems((prev) => {                             // always use the latest state
      const found = prev.find((i) => i.name === name);        // already in the cart?
      return found
        ? prev.map((i) => (i.name === name ? { ...i, qty: i.qty + 1 } : i)) // bump qty (new object)
        : [...prev, { name, qty: 1 }];               // first time: new line
    });
  };

  return (
    <div>
      <button onClick={() => add('Mouse')}>Add Mouse</button>
      <ul>{items.map((i) => <li key={i.name}>{i.name} x {i.qty}</li>)}</ul>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

## 💻 Code Example — Advanced

```jsx
// Reducer from App.jsx: every rule in one pure, testable function
export function cartReducer(state, action) {
  switch (action.type) {
    case 'ADD': {
      const found = state.items.find((i) => i.id === action.item.id);
      const items = found
        ? state.items.map((i) => (i.id === found.id ? { ...i, qty: i.qty + 1 } : i))
        : [...state.items, { ...action.item, qty: 1 }];
      return { ...state, items };
    }
    case 'REMOVE':
      return { ...state, items: state.items.filter((i) => i.id !== action.id) };
    case 'SET_QTY': {
      const qty = Math.max(0, Math.floor(action.qty));        // no negative or decimal quantity
      const items = state.items
        .map((i) => (i.id === action.id ? { ...i, qty } : i))
        .filter((i) => i.qty > 0);                            // quantity 0 removes the line
      return { ...state, items };
    }
    case 'CLEAR':
      return { ...state, items: [] };
    default:
      return state;
  }
}

// Provider: derived values are computed, never stored (they cannot go out of sync)
const value = useMemo(() => ({
  items: state.items,
  count: state.items.reduce((n, i) => n + i.qty, 0),          // badge number
  total: state.items.reduce((n, i) => n + i.qty * i.price, 0),// payable amount
  dispatch,
}), [state.items]);

// Pure reducer = trivially unit testable (no React needed)
// cartReducer({ items: [] }, { type: 'ADD', item: { id: 'p1', price: 10 } }).items[0].qty === 1
```

---

## 🟠 Next.js Connection
In a real shop the server is the source of truth: prices, stock and the cart live in a database. In the App Router, show the cart with a Server Component, and use **Server Actions** to mutate it. A small Client Component can still use `useOptimistic` (React 19) so the badge updates instantly while the action runs. Never trust prices sent from the browser; recalculate totals on the server.

```jsx
// app/cart/actions.js
'use server';                                          // Server Actions file
import { revalidatePath } from 'next/cache';           // refresh cached UI after a change
import { addItemToCart } from '@/lib/cart';            // hypothetical DB helper

export async function addToCart(productId) {
  await addItemToCart(productId);                      // server validates stock and price
  revalidatePath('/cart');                             // cart page shows fresh data
}

// app/products/AddButton.jsx
'use client';
import { addToCart } from '../cart/actions';
export default function AddButton({ id }) {
  return <button onClick={() => addToCart(id)}>Add to cart</button>; // calls the server function
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Mutating state (`item.qty++`) inside the reducer
✅ **Correct:** Return new objects and arrays

```jsx
// Wrong: same array reference, React may skip the re-render
state.items.find((i) => i.id === id).qty++;
return state;
// Right: copy what changed
return { ...state, items: state.items.map((i) => (i.id === id ? { ...i, qty: i.qty + 1 } : i)) };
```

❌ **Mistake 2:** Storing `total` in state next to `items`
✅ **Correct:** Derive it during render

```jsx
// Wrong: two sources of truth, can go stale
const [items, setItems] = useState([]); const [total, setTotal] = useState(0);
// Right
const total = items.reduce((n, i) => n + i.qty * i.price, 0);
```

❌ **Mistake 3:** Using the array index as `key` for cart lines
✅ **Correct:** Use the product `id`

```jsx
// Wrong: removing line 0 makes inputs show the wrong quantities
items.map((i, index) => <Row key={index} />)
// Right
items.map((i) => <Row key={i.id} />)
```

---

## 🧠 Tricky Interview Question

```jsx
function reducer(state, action) {
  if (action.type === 'inc') {
    state.count++;               // mutation
    return state;                // same reference
  }
  return state;
}
const [state, dispatch] = useReducer(reducer, { count: 0 });
<button onClick={() => dispatch({ type: 'inc' })}>{state.count}</button>
```
**Answer:** The button text does **not** update. The reducer returns the same object, so React compares with `Object.is`, sees no change and bails out of re-rendering. The count was mutated in memory, so it may suddenly appear after some unrelated re-render, which makes the bug confusing. In dev StrictMode the reducer also runs twice, so the mutation would add 2. Always return a new object.

---

## ⚫ Interview Questions + Answers

Q1: Why `useReducer` instead of `useState` for a cart?
A1: The cart has several related actions with rules (merge duplicates, remove at 0). A reducer centralises them in one pure function, which is easy to test and reason about. `useState` spreads that logic across handlers.

Q2: Why not store the total in state?
A2: It is derived data. Storing it creates two sources of truth that can disagree. Compute it during render, and use `useMemo` if the calculation is expensive.

Q3: How do you persist the cart?
A3: Lazy-initialise the reducer from `localStorage` (`useReducer(reducer, undefined, loadInitial)`) and save in `useEffect([items])`. Wrap `JSON.parse` in try/catch for corrupted data. For logged-in users, persist on the server instead.

Q4: How do you stop the whole page re-rendering when the cart changes?
A4: Split context into state and dispatch contexts, memoise heavy children with `React.memo`, or use a selector-based store (Redux Toolkit, Zustand) so a component subscribes only to the slice it needs.

Q5: Is client-side price calculation safe?
A5: It is fine for display, but the server must recompute prices and stock at checkout, because the browser can be tampered with.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- State has multiple actions and business rules
- Several distant components need the same data
- You want logic that is testable without rendering

❌ **Avoid when:**
- The state is one boolean or counter (`useState` is enough)
- The cart already lives on the server (use TanStack Query or Server Components)
- You need fine-grained subscriptions across a huge app (use a store with selectors)

---

## 📊 Visual Diagram

```
  UI event ──► dispatch({type:'ADD', item}) ──► cartReducer(state, action)
                                                      │ returns NEW state
                                                      ▼
                                    state.items ──► useMemo ──► { count, total }
                                         │                          │
                         useEffect ──► localStorage          Context value
                                                                    │
                           ┌─────────────────┬──────────────────────┤
                           ▼                 ▼                      ▼
                     Header badge        Cart page             Checkout total
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Reducer | Pure function (state, action) → new state | (state, action) से नई state देने वाला pure function |
| Action | Object describing what happened | क्या हुआ, यह बताने वाला object |
| Immutable update | Create a copy instead of changing | बदलने की जगह copy बनाना |
| Derived state | Value computed from other state | दूसरी state से निकाली गई value |
| Lazy init | Compute the initial state once | शुरुआती state एक बार बनाना |
| Optimistic update | Show result before the server confirms | Server की पुष्टि से पहले नतीजा दिखाना |
| Server Action | Server function callable from the UI | UI से बुलाया जाने वाला server function |

---

## ⚡ 3-Line Summary
**English:**
1. Model the cart with a pure reducer for ADD, REMOVE, SET_QTY and CLEAR, always returning new objects.
2. Derive count and total from `items`, share them through context, and persist items to storage.
3. In Next.js the server owns prices and stock, so use Server Actions and recompute totals on the server.

**Hindi:**
1. Cart को ADD, REMOVE, SET_QTY और CLEAR वाले pure reducer से बनाओ, और हमेशा नए objects लौटाओ।
2. Count और total को `items` से derive करो, context से share करो, और items को storage में save करो।
3. Next.js में prices और stock server के पास होते हैं, इसलिए Server Actions इस्तेमाल करो और total server पर दोबारा calculate करो।

---

## ➡️ Next Topic
**202. Build Star Rating Component** — अब एक छोटा पर reusable UI component: hover preview, controlled value और accessibility।
