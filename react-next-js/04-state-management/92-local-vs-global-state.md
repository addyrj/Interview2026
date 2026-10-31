# 92. Local vs Global State
# हिंदी में: Local vs Global State — कौन सा state कहाँ रखें

---

## 🔵 Simple Definition (English)
**Local state** belongs to one component (for example, whether a dropdown is open). **Global state** is shared by many parts of the app (for example, the logged-in user or the cart). Keep state as local as possible, and make it global only when more than one distant part of the app needs it.

## 🔵 सरल परिभाषा (Hindi)
**Local state** एक ही component का होता है (जैसे dropdown खुला है या बंद)। **Global state** पूरी app के कई हिस्से share करते हैं (जैसे logged-in user या cart)। State को जितना हो सके local रखो, और global तभी बनाओ जब app के दूर के कई हिस्सों को उसकी जरूरत हो।

---

## 🔴 Problem it Solves
Beginners often put everything in a global store: modal open or closed, input text, tab selected. Every change then goes through the store, more components re-render than needed, and the code becomes hard to follow. The opposite mistake also happens: the cart is kept as local state in one page, so it resets when the user navigates. Knowing the scope of each value prevents both problems.

## 🔴 यह क्यों बना? (Hindi)
Beginners अक्सर हर चीज़ global store में डाल देते हैं: modal खुला है या नहीं, input का text, selected tab। फिर हर बदलाव store से गुज़रता है, ज़रूरत से ज़्यादा components re-render होते हैं और code समझना मुश्किल हो जाता है। उल्टी गलती भी होती है: cart को एक page के local state में रखा जाता है, तो user navigate करते ही cart खाली हो जाता है। हर value का scope जानने से दोनों समस्याएँ रुकती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Ask: "Who needs this value?"
Step 2 → Only one component?          → useState (LOCAL)
Step 3 → Siblings or a parent/child?  → lift state to common parent (topic 91)
Step 4 → Many distant parts, or must survive navigation/refresh?
                                      → Context, store, or URL (GLOBAL)
Step 5 → Data from the server?        → server-state library or fetch in a server component

KEY: Scope = the smallest place that still has every reader in its subtree.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पूछो: "यह value किसे चाहिए?"
Step 2 → सिर्फ एक component को?              → useState (LOCAL)
Step 3 → Siblings या parent/child को?          → common parent तक उठाओ (topic 91)
Step 4 → दूर के कई हिस्सों को, या navigation/refresh के बाद भी बचे?
                                              → Context, store या URL (GLOBAL)
Step 5 → Data server से आता है?               → server-state library या server component में fetch
KEY: Scope = सबसे छोटी जगह जहाँ सभी readers उसके subtree में हों।
```

---

## 🟡 Real World Example
**Flipkart product page:** The image carousel index, the "Show more" toggle and the size dropdown are **local** — only that component cares about them. The logged-in user, the cart count and the currency preference are **global** — the header, the product page and the checkout all need them. The selected filters on the listing page are kept in the **URL**, so pressing back or sharing the link restores the same result.

## 🟡 Real Example Hindi mein
**Flipkart product page:** Image carousel का index, "Show more" toggle और size dropdown **local** हैं, क्योंकि उन्हें सिर्फ एक component देखता है। Logged-in user, cart count और currency preference **global** हैं, क्योंकि header, product page और checkout तीनों को चाहिए। Listing page के चुने हुए filters **URL** में रहते हैं, ताकि back दबाने या link share करने पर वही result वापस आए।

---

## 💻 Code Example — Basic

```jsx
import { createContext, useContext, useState } from 'react';

// GLOBAL: a context shared by every component inside the Provider
const UserContext = createContext(null); // default value used only without a Provider

// Provider: owns the global user state and makes it available below
function UserProvider({ children }) {
  const [user] = useState({ name: 'Aditya', city: 'Patna' }); // global data
  return <UserContext.Provider value={user}>{children}</UserContext.Provider>;
}

// Deep child: reads the GLOBAL user without any props
function Greeting() {
  const user = useContext(UserContext); // subscribe to the nearest provider
  return <p>Welcome, {user.name}</p>;
}

// LOCAL: a dropdown that only this component cares about
function SizePicker() {
  const [open, setOpen] = useState(false); // local: no one else needs to know
  return (
    <div>
      <button onClick={() => setOpen(!open)}>Size</button>
      {open && <ul><li>M</li><li>L</li></ul>} {/* list shows only when open */}
    </div>
  );
}

export default function App() {
  return (
    <UserProvider>
      <Greeting />   {/* global consumer */}
      <SizePicker /> {/* local state, unaffected by the provider */}
    </UserProvider>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { useSearchParams } from 'react-router-dom'; // v6 hook for query strings
import { useState, useMemo } from 'react';

// Filter state lives in the URL: shareable, survives refresh and back button.
// Reading and writing query params is the "global" store for this page.
function useListingFilters() {
  const [searchParams, setSearchParams] = useSearchParams(); // URL-backed state

  // Read a value; default to 'all' when the param is missing
  const category = searchParams.get('category') ?? 'all';
  // Read a number; Number() converts the string, NaN means "not a number"
  const maxPrice = Number(searchParams.get('max')) || Infinity;

  // Update one filter but keep the others (copy the current params first)
  const setCategory = (value) => {
    const next = new URLSearchParams(searchParams); // copy, do not mutate
    next.set('category', value);                    // change one key
    setSearchParams(next);                          // navigate with new query
  };

  return { category, maxPrice, setCategory };
}

// Products list is derived from the filters every render, not stored separately
export default function Listing({ products }) {
  const { category, maxPrice, setCategory } = useListingFilters();

  // useMemo: recompute the filtered list only when the inputs change
  const visible = useMemo(
    () => products.filter(
      (p) => (category === 'all' || p.category === category) && p.price <= maxPrice
    ),
    [products, category, maxPrice]
  );

  // Local state: whether the mobile filter drawer is open (no one else needs it)
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <section>
      <button onClick={() => setDrawerOpen(!drawerOpen)}>Filters</button>
      {drawerOpen && (
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="all">All</option>
          <option value="shoes">Shoes</option>
        </select>
      )}
      <p>{visible.length} results</p> {/* count comes from derived data */}
    </section>
  );
}
```

---

## 🟠 Real App Integration (React + Next.js)

In a Next.js App Router app, URL state is the natural "global" store for filters: `searchParams` is passed to the page as a prop, so the server can fetch the right data. Local UI state stays in a small Client Component.

```jsx
// app/products/page.jsx — Server Component reads the URL directly
export default async function ProductsPage({ searchParams }) {
  // Next.js 15+: searchParams is a Promise
  const { category = 'all' } = await searchParams;       // URL state, read on the server
  const res = await fetch(`https://api.example.com/products?category=${category}`);
  const products = await res.json();                     // data for this filter only
  return <ProductGrid products={products} />;            // ProductGrid is a Client Component
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Putting a modal's open flag in global state
✅ **Correct:** Keep UI-only flags local. Global state for them forces unrelated re-renders.

```jsx
// Wrong: every store change re-renders the whole app for a modal flag
const isModalOpen = useAppStore((s) => s.isModalOpen); // ❌ global for one component

// Right: local state, scoped to the component that uses it
const [isModalOpen, setModalOpen] = useState(false);    // ✅ local
```

❌ **Mistake 2:** Using a context value that is a new object on every render
✅ **Correct:** Memoize the value. A new object each render makes every consumer re-render, even when nothing it reads has changed.

```jsx
// Wrong: new object every time the Provider renders
<CartContext.Provider value={{ items, addItem }}>  {/* ❌ new reference */}

// Right: stable reference, consumers update only when items or addItem change
const value = useMemo(() => ({ items, addItem }), [items, addItem]);
<CartContext.Provider value={value}>               {/* ✅ */}
```

---

## 🧠 Tricky Interview Question

```jsx
import { createContext, useContext, useState, memo } from 'react';
import { createRoot } from 'react-dom/client';
import { act } from 'react-dom/test-utils';

const CountContext = createContext(null);
let headerRenders = 0;                        // counts renders of the consumer

// memo: Header skips re-render when its PARENT re-renders with the same props
const Header = memo(function Header() {
  useContext(CountContext);                   // subscribes to the context
  headerRenders++;
  return <h1>Title</h1>;
});

// Page re-renders on every root.render; the Provider value is a NEW object each time
function Page() {
  const [count] = useState(0);
  return (
    <CountContext.Provider value={{ count }}>  {/* new object on every Page render */}
      <Header />
    </CountContext.Provider>
  );
}

const container = document.createElement('div');
const root = createRoot(container);
act(() => root.render(<Page />));             // first render: Header runs once
act(() => root.render(<Page />));             // Page re-renders with a new value object
console.log(headerRenders);
```

**Answer:** The output is `2`. `memo` stops Header from re-rendering because its props did not change, but it does not block context updates. The Provider builds a new `{ count }` object on every render, React compares context values with `Object.is`, sees a new reference, and re-renders every consumer, including the memoized `Header`. Wrapping the value in `useMemo(() => ({ count }), [count])` keeps the reference stable, and the output becomes `1`.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between local and global state?**
A1: Local state is owned by one component with `useState` or `useReducer`. Global state is owned higher up and read by many components through Context, a store, or the URL.

**Q2: Why is URL state a good choice for filters?**
A2: The URL survives refresh, can be shared, and works with the back button. Users can bookmark a filtered view and get the same result back.

**Q3: Is all state that is used in two places global?**
A3: Not necessarily. Two siblings can share state through their parent (lifting state up). Global is needed only when the readers are far apart or the state must outlive a component.

**Q4: Why do context consumers re-render even if they don't use the changed field?**
A4: Context has no field-level subscriptions. When the value reference changes, every consumer re-renders. Split large contexts or keep the value stable with `useMemo`.

**Q5: Where should server data (API results) live?**
A5: Ideally in a server-state library (TanStack Query, RTK Query) or in Server Components for Next.js. Copying API results into a general store makes caching and freshness your problem.

---

## 🔷 When to Use + When Not to Use
✅ **Use global state when:**
- Many distant components read the same value (user, theme, cart)
- The state must survive navigation within the app
- Filters or selections should be shareable through the URL

❌ **Avoid global state when:**
- Only one component uses the value (modal, dropdown, input text)
- A value changes many times per second (typing, drag position)
- The data is only needed on one page

---

## 📊 Visual Diagram

```
SCOPE LADDER (choose the smallest one that works)

 ┌─────────────────────────────────────────────────────────┐
 │ GLOBAL: user, cart, theme         → Context / store      │
 │  ┌───────────────────────────────────────────────────┐   │
 │  │ PAGE: filters                 → URL (searchParams)│   │
 │  │  ┌─────────────────────────────────────────────┐  │   │
 │  │  │ COMPONENT: dropdown open   → useState (local)│  │   │
 │  │  └─────────────────────────────────────────────┘  │   │
 │  └───────────────────────────────────────────────────┘   │
 └─────────────────────────────────────────────────────────┘

Rule: outer rings re-render more; keep changing values in the inner rings.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Local state | State owned by one component | एक component का अपना state |
| Global state | State shared across the app | पूरी app में share होने वाला state |
| Scope | The part of the tree that can read a value | Tree का वह हिस्सा जो value पढ़ सकता है |
| URL state | State stored in query params or path | Query params या path में रखा state |
| Context value | The object a Provider passes to consumers | Provider जो object consumers को देता है |
| Server state | Data that lives on the server (API results) | Server पर रहने वाला data (API results) |

---

## ⚡ 3-Line Summary
**English:**
1. Local state belongs to one component; global state is shared by distant parts of the app.
2. Keep state as local as possible and put filters in the URL when they should be shareable.
3. Memoize context values and do not put fast-changing UI flags in global state.

**Hindi:**
1. Local state एक component का होता है; global state app के दूर के हिस्सों में share होता है।
2. State को जितना हो सके local रखो, और filters को URL में तब रखो जब उन्हें share करना हो।
3. Context values को memoize करो और तेज़ी से बदलने वाले UI flags को global state में मत डालो।

---

## ➡️ Next Topic
**93. Context API for State Management** — Context कैसे बनता है, Provider और `useContext` कैसे काम करते हैं, और global state के लिए उसकी सीमाएँ क्या हैं। Local और global का फ़र्क समझने के बाद Context सबसे पहला tool है।
