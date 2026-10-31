# 91. State Management — Why Needed
# हिंदी में: State Management — ज़रूरत क्यों पड़ती है

---

## 🔵 Simple Definition (English)
State management is the practice of deciding **where** data lives in a React app and **how** components read and change it. When many components need the same data, you need a clear plan, otherwise screens show different values for the same thing.

## 🔵 सरल परिभाषा (Hindi)
State management का मतलब है कि React app में data **कहाँ** रहेगा और components उसे **कैसे** पढ़ेंगे और बदलेंगे। जब कई components को एक ही data चाहिए, तब साफ़ plan जरूरी है, वरना screens पर एक ही चीज़ की अलग-अलग values दिखेंगी।

---

## 🔴 Problem it Solves
Each `useState` lives inside one component. Real apps need the same data in many places: the logged-in user is needed by the header, the profile page and the checkout. Passing it by hand through every level (prop drilling) makes code fragile, and two copies of the same data drift apart. Without a plan, developers copy values into local state, forget to update one copy, and users see the cart count as 3 in the header and 2 on the cart page.

## 🔴 यह क्यों बना? (Hindi)
हर `useState` एक component के अंदर रहता है। असली apps में वही data कई जगह चाहिए: logged-in user header, profile page और checkout तीनों को चाहिए। हर level से हाथ से prop पास करना (prop drilling) code को नाज़ुक बनाता है, और एक ही data की दो copies अलग हो जाती हैं। बिना plan के, एक copy update होती है और दूसरी छूट जाती है — header में cart count 3 दिखता है और cart page पर 2।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Identify the data: "the logged-in user" is needed in 3 places
Step 2 → Find the lowest common parent that owns the data
Step 3 → Put useState there (this is "lifting state up")
Step 4 → Pass data DOWN as props, and change functions DOWN as props
Step 5 → If the tree gets deep, move the data to Context or a store (topics 92–98)

KEY: One owner per piece of data. Everyone else reads or calls a function.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Data पहचानो: "logged-in user" तीन जगह चाहिए
Step 2 → सबसे नज़दीकी common parent ढूँढो जो data का owner बने
Step 3 → वहीं useState रखो ("state को ऊपर उठाना" / lifting state up)
Step 4 → Data को props से नीचे भेजो, और update function भी props से भेजो
Step 5 → Tree बहुत गहरा हो तो data को Context या store में ले जाओ (topic 92–98)
KEY: हर data का एक owner। बाकी सब उसे पढ़ें या उसका function call करें।
```

---

## 🟡 Real World Example
**Swiggy cart:** The cart count is shown in the top bar, on the restaurant menu page (add button changes it), and on the checkout page. One cart owner holds the items. Every other component reads the same list and calls the same `addItem` function. When you add a biryani on the menu page, the top bar badge updates the same instant, because all three read one source of truth.

## 🟡 Real Example Hindi mein
**Swiggy cart:** Cart count ऊपर की top bar में, restaurant menu page पर (add बटन से बदलता है) और checkout page पर दिखता है। Cart items का एक owner होता है। बाकी सब उसी list को पढ़ते हैं और एक ही `addItem` function call करते हैं। Menu page पर biryani add करते ही top bar का badge उसी पल बदलता है, क्योंकि तीनों एक ही source of truth से पढ़ते हैं।

---

## 💻 Code Example — Basic

```jsx
import { useState } from 'react';

// Bottom of the tree: only this component actually USES the user's name
function UserMenu({ user }) {
  // Reads the prop and shows it
  return <p>Hi, {user.name}</p>;
}

// Middle layer: does NOT use the user at all, only passes it along
function Header({ user }) {
  // Forwards the prop to UserMenu (this is "prop drilling")
  return <header><UserMenu user={user} /></header>;
}

// Top layer: owns the data, because it created it with useState
function App() {
  // The user lives here; any change to it would re-render the whole tree below
  const [user] = useState({ name: 'Aditya' });

  // Pass the data down through every layer
  return (
    <div>
      <Header user={user} />
    </div>
  );
}

// renderToStaticMarkup turns the tree into HTML; used here to show the output
import { renderToStaticMarkup } from 'react-dom/server';
console.log(renderToStaticMarkup(<App />));
// Output: <div><header><p>Hi, Aditya</p></header></div>
```

## 💻 Code Example — Advanced

```jsx
import { useState, useMemo, useCallback } from 'react';

// Two SIBLINGS need the same cart: ProductList adds, CartSummary reads.
// Neither can own the cart alone, so the parent (ShopPage) owns it.
function ProductList({ products, onAdd }) {
  return (
    <ul>
      {products.map((p) => (
        // onAdd is a function prop: the child calls it, the parent updates state
        <li key={p.id}>
          {p.name} — ₹{p.price}
          <button onClick={() => onAdd(p)}>Add</button>
        </li>
      ))}
    </ul>
  );
}

// Reads the cart and shows totals. Does not own the data.
function CartSummary({ items, total }) {
  return <p>{items.length} items · Total ₹{total}</p>;
}

// Owner of the shared data. Everything the children need comes from here.
export function ShopPage() {
  const products = [                                  // static catalogue for the demo
    { id: 1, name: 'Biryani', price: 220 },
    { id: 2, name: 'Paneer Tikka', price: 180 },
  ];
  const [items, setItems] = useState([]);             // the cart lives here

  // useCallback keeps the same function identity between renders
  const addToCart = useCallback((product) => {
    // Functional update: uses the latest state, safe even with fast clicks
    setItems((prev) => [...prev, product]);
  }, []);                                             // setItems never changes, so no deps

  // Derived value: computed from state, NOT stored as separate state
  // useMemo caches the sum until items changes
  const total = useMemo(
    () => items.reduce((sum, item) => sum + item.price, 0),
    [items]
  );

  return (
    <section>
      <ProductList products={products} onAdd={addToCart} />
      <CartSummary items={items} total={total} />
    </section>
  );
}
```

---

## 🟠 Real App Integration (React + Next.js)

In a Next.js App Router app, the "owner" for data is often the **server**. Fetch once in a Server Component, then pass the result down to a small Client Component that owns only the UI state it needs. Shared client data (like the cart) still goes into a store or Context.

```jsx
// app/shop/page.jsx — Server Component: fetches data, owns no client state
import ShopClient from './ShopClient';                 // Client Component below

export default async function ShopPage() {
  // Runs on the server; the result is passed as a plain prop to the client
  const products = await fetch('https://api.example.com/products').then((r) => r.json());
  return <ShopClient initialProducts={products} />;    // hand data down once
}
```

```jsx
// app/shop/ShopClient.jsx — Client Component: owns the cart UI state
'use client';                                          // needed for useState
import { useState } from 'react';

export default function ShopClient({ initialProducts }) {
  // Cart is local to this subtree; it moves to a store if other pages need it
  const [cart, setCart] = useState([]);
  return (
    <button onClick={() => setCart((c) => [...c, initialProducts[0]])}>
      Cart: {cart.length}                              {/* shows the current count */}
    </button>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Copying props into state
✅ **Correct:** `useState(prop)` only uses the prop on the first render. Later prop changes are ignored. Derive the value instead.

```jsx
// Wrong: total is frozen at the first items.length
function Total({ items }) {
  const [total] = useState(items.length); // ❌ copies the prop once
  return <p>{total}</p>;
}

// Right: compute from the prop on every render
function Total({ items }) {
  const total = items.length;             // ✅ always in sync with the prop
  return <p>{total}</p>;
}
```

❌ **Mistake 2:** Keeping the same data in two states
✅ **Correct:** Store the data once. Compute everything else from it.

```jsx
// Wrong: two copies that can drift apart
const [items, setItems] = useState([]);
const [count, setCount] = useState(0);   // ❌ a second copy of items.length

// Right: one source of truth
const [items, setItems] = useState([]);
const count = items.length;              // ✅ derived, can never be wrong
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState } from 'react';
import { createRoot } from 'react-dom/client';
import { act } from 'react-dom/test-utils';

// Shows a count that was copied from a prop once
function Total({ items }) {
  const [total] = useState(items.length); // initial value only
  return <p>{total}</p>;
}

// Render with 2 items, then re-render the SAME component with 4 items
const container = document.createElement('div');
const root = createRoot(container);
act(() => root.render(<Total items={[1, 2]} />));
act(() => root.render(<Total items={[1, 2, 3, 4]} />));
console.log(container.textContent);
```

**Answer:** The output is `2`, not `4`. `useState(items.length)` reads the initial value only on the first mount. On the second render, React keeps the existing state (`2`) and ignores the new initial argument. The prop changed, but the copy did not. The fix is to derive the value directly: `const total = items.length;`, which prints `4`.

---

## ⚫ Interview Questions + Answers

**Q1: What is prop drilling?**
A1: Passing data through several components that do not use it, just so a deep child can reach it. It makes refactors hard, and it is the main reason developers reach for Context or a store.

**Q2: What does "lifting state up" mean?**
A2: Moving `useState` to the nearest common parent of the components that need the same data. The parent passes the value and update functions down as props.

**Q3: What is a "single source of truth"?**
A3: One place where a piece of data is owned and updated. Other components read from it or call its update function, so they never hold separate copies.

**Q4: Why is storing derived data in state a bug risk?**
A4: Derived data (like a count or total) can be recomputed from the source. If you store it separately, you must update both copies everywhere, and a missed update shows stale values.

**Q5: When does prop drilling become a problem worth solving with a store or Context?**
A5: When many layers pass props they never use, when unrelated screens need the same data, or when a small change in a parent forces many files to change.

---

## 🔷 When to Use + When Not to Use
✅ **Use this thinking when:**
- Two or more components need the same data
- A value can be derived from other state
- You are deciding where a new piece of state should live

❌ **Avoid when:**
- Data is used by one component only (keep it local with `useState`)
- You jump to a global store before the tree proves it is needed
- You copy a prop into state without a reason to decouple them

---

## 📊 Visual Diagram

```
PROP DRILLING (data passes through layers that ignore it)

  App  ── owns user ──┐
   │                  │ props
   ▼                  ▼
  Layout        (does not use user)
   │
   ▼
  Header        (does not use user)
   │
   ▼
  UserMenu      ── uses user.name ✅

LIFTING STATE (single owner, functions go back up)

  ShopPage  ── owns items ─────────────┐
   │  props: products, onAdd           │  props: items, total
   ▼                                   ▼
  ProductList ── calls onAdd(p) ──► CartSummary ── reads items
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| State | Data that changes and causes re-renders | ऐसा data जो बदलता है और re-render करवाता है |
| Prop drilling | Passing props through layers that ignore them | ऐसी layers से props भेजना जो उन्हें इस्तेमाल नहीं करतीं |
| Lifting state up | Moving state to a common parent | State को common parent तक ले जाना |
| Single source of truth | One owner for each piece of data | हर data का एक ही owner |
| Derived value | Value computed from other state | दूसरे state से निकाली गई value |
| Source of truth | The authoritative copy of the data | Data की असली और भरोसेमंद copy |

---

## ⚡ 3-Line Summary
**English:**
1. State management decides where shared data lives so every component shows the same value.
2. Lift state to the nearest common parent, pass data down as props, and pass update functions down too.
3. Store each value once, derive the rest, and move to Context or a store only when prop drilling hurts.

**Hindi:**
1. State management तय करता है कि shared data कहाँ रहेगा, ताकि हर component एक ही value दिखाए।
2. State को सबसे नज़दीकी common parent तक उठाओ, data props से नीचे भेजो और update functions भी।
3. हर value एक बार store करो, बाकी derive करो, और Context या store में तभी जाओ जब prop drilling तकलीफ़ दे।

---

## ➡️ Next Topic
**92. Local vs Global State** — कौन सा state किसी एक component का है और कौन सा पूरी app का। यह समझने के बाद ही Context या Redux चुनने का सही फ़ैसला होता है।
