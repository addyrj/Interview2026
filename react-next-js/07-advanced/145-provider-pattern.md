# 145. Provider Pattern
# हिंदी में: Provider Pattern — पूरे Tree को Data देना

---

## 🔵 Simple Definition (English)
The **Provider pattern** wraps part of the component tree in a Provider component that holds some state or service and shares it with any descendant through context, accessed with a custom hook. It removes props drilling for global-ish data like theme, auth, cart or locale.

## 🔵 सरल परिभाषा (Hindi)
**Provider pattern** में component tree के एक हिस्से को Provider component में लपेटते हैं, जो state या service रखता है और context से किसी भी descendant को देता है, जिसे custom hook से पढ़ते हैं। यह theme, auth, cart या locale जैसे global-जैसे data के लिए props drilling खत्म करता है।

---

## 🔴 Problem it Solves

Passing `user` or `cart` through ten layers of components that don't use it (props drilling) makes code fragile: every intermediate component gets extra props and every change touches many files.

```jsx
// PROBLEM: props drilling
<App user={user}>
  <Layout user={user}>
    <Header user={user}>
      <Avatar user={user} />           // only Avatar needs it
    </Header>
  </Layout>
</App>

// SOLUTION: Provider at the top, hook at the leaf
<AuthProvider>                          {/* holds the user once */}
  <Layout><Header><Avatar /></Header></Layout>   {/* Avatar calls useAuth() */}
</AuthProvider>
```

## 🔴 यह क्यों बना? (Hindi)
`user` या `cart` को दस layers से गुज़ारना जिनको उसकी ज़रूरत नहीं (props drilling) code को नाज़ुक बना देता है: हर बीच वाले component को अतिरिक्त props मिलते हैं और हर बदलाव कई files छूता है। Provider में data एक बार ऊपर रहता है और leaf पर hook से मिलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → createContext(defaultValue) makes a context object
Step 2 → Write a Provider component: it holds state (useState/useReducer) and renders <Context.Provider value={...}>{children}</Context.Provider>
Step 3 → Put the Provider high in the tree (root, or around the feature that needs it)
Step 4 → Write a custom hook useX() = useContext(Context) that throws if the Provider is missing
Step 5 → Any descendant calls useX() and gets the value, with no props passing
Step 6 → When the Provider's value changes (by Object.is), every consumer re-renders

Rules: memoize the value, split contexts by update frequency (state vs actions, or theme vs cart), keep Providers close to where they are needed
Re-render: `children` passed from above keeps the same identity, so non-consumer children do NOT re-render when Provider state changes
Performance: context has no selectors; for frequently changing big state use Zustand/Redux or split contexts
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → createContext(defaultValue) एक context object बनाता है
Step 2 → Provider component लिखो: वह state (useState/useReducer) रखता है और <Context.Provider value={...}>{children}</Context.Provider> render करता है
Step 3 → Provider को tree में ऊपर रखो (root पर, या उस feature के आसपास जिसे ज़रूरत हो)
Step 4 → Custom hook useX() = useContext(Context) लिखो जो Provider न मिलने पर error फेंके
Step 5 → कोई भी descendant useX() बुलाकर value पाता है, props passing के बिना
Step 6 → Provider की value बदलने पर (Object.is से) सारे consumers re-render होते हैं

नियम: value को memoize करो, context को update frequency के हिसाब से बाँटो (state बनाम actions, या theme बनाम cart), Provider को ज़रूरत के पास रखो
Re-render: ऊपर से आया `children` वही identity रखता है, इसलिए जो consumers नहीं हैं वे Provider की state बदलने पर re-render नहीं होते
Performance: context में selectors नहीं होते; बार-बार बदलने वाली बड़ी state के लिए Zustand/Redux या contexts बाँटो
```

---

## 🟡 Real World Example
**Swiggy app:** The logged-in user, the delivery address, the cart and the theme are needed on many screens (header, restaurant list, checkout). A `CartProvider` holds items and exposes `addItem`, `removeItem` and `total`. The header badge, the restaurant page's "Add" button and the checkout page all call `useCart()`. Nobody passes `cart` through props.

## 🟡 Real Example Hindi mein
**Swiggy app:** Logged-in user, delivery address, cart और theme कई screens (header, restaurant list, checkout) पर चाहिए। `CartProvider` items रखता है और `addItem`, `removeItem`, `total` देता है। Header का badge, restaurant page का "Add" बटन और checkout page सब `useCart()` बुलाते हैं। कोई भी `cart` को props से नहीं भेजता।

---

## 💻 Code Example — Basic

```jsx
// Basic: ThemeProvider + useTheme hook
import { createContext, useContext, useState } from 'react';   // context + state
import { createRoot } from 'react-dom/client';                  // root API

const ThemeContext = createContext(null);                       // null default lets us detect a missing Provider

function ThemeProvider({ children }) {                          // Provider component
  const [theme, setTheme] = useState('light');                  // state lives here
  const toggle = () => setTheme((t) => (t === 'light' ? 'dark' : 'light')); // action
  return (
    <ThemeContext.Provider value={{ theme, toggle }}>           {/* share state + action */}
      {children}
    </ThemeContext.Provider>
  );
}

function useTheme() {                                            // custom consumer hook
  const ctx = useContext(ThemeContext);                          // read nearest Provider
  if (!ctx) throw new Error('useTheme must be used inside ThemeProvider'); // helpful error
  return ctx;
}

function Header() {                                              // deep consumer, no props
  const { theme, toggle } = useTheme();                          // get value directly
  return <button onClick={toggle}>Theme: {theme}</button>;
}

createRoot(document.getElementById('root')).render(
  <ThemeProvider>                                                {/* wrap the app once */}
    <Header />
  </ThemeProvider>
);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: CartProvider with useReducer, split state/dispatch contexts, memoized value, and localStorage persistence
import { createContext, useContext, useReducer, useMemo, useEffect } from 'react';
import { createRoot } from 'react-dom/client';

const CartStateContext = createContext(null);                   // read-only data (changes often)
const CartActionsContext = createContext(null);                 // actions (stable, rarely re-render consumers)

function cartReducer(state, action) {                            // pure reducer: all updates in one place
  switch (action.type) {
    case 'add': {
      const found = state.items.find((i) => i.id === action.item.id);
      const items = found
        ? state.items.map((i) => (i.id === found.id ? { ...i, qty: i.qty + 1 } : i)) // increase qty
        : [...state.items, { ...action.item, qty: 1 }];                              // new line item
      return { ...state, items };
    }
    case 'remove':
      return { ...state, items: state.items.filter((i) => i.id !== action.id) };     // drop item
    case 'hydrate':
      return { ...state, items: action.items };                                      // load saved cart
    default:
      throw new Error(`Unknown action ${action.type}`);          // fail loudly in dev
  }
}

function CartProvider({ children }) {
  const [state, dispatch] = useReducer(cartReducer, { items: [] }); // cart state

  useEffect(() => {                                              // restore cart on mount (client only)
    const saved = localStorage.getItem('cart');
    if (saved) dispatch({ type: 'hydrate', items: JSON.parse(saved) });
  }, []);
  useEffect(() => {                                              // persist on every change
    localStorage.setItem('cart', JSON.stringify(state.items));
  }, [state.items]);

  const total = useMemo(                                          // derived value, cached
    () => state.items.reduce((s, i) => s + i.price * i.qty, 0),
    [state.items]
  );
  const stateValue = useMemo(() => ({ items: state.items, total }), [state.items, total]);
  const actions = useMemo(() => ({                                // stable object: dispatch never changes
    add: (item) => dispatch({ type: 'add', item }),
    remove: (id) => dispatch({ type: 'remove', id }),
  }), []);

  return (
    <CartActionsContext.Provider value={actions}>               {/* components that only add don't re-render on change */}
      <CartStateContext.Provider value={stateValue}>
        {children}
      </CartStateContext.Provider>
    </CartActionsContext.Provider>
  );
}

function useCartState() {
  const ctx = useContext(CartStateContext);
  if (!ctx) throw new Error('useCartState must be used inside CartProvider');
  return ctx;
}
function useCartActions() {
  const ctx = useContext(CartActionsContext);
  if (!ctx) throw new Error('useCartActions must be used inside CartProvider');
  return ctx;
}

function AddButton({ item }) {                                   // uses only actions → no re-render on cart change
  const { add } = useCartActions();
  return <button onClick={() => add(item)}>Add {item.name}</button>;
}
function CartBadge() {                                           // uses state → re-renders when cart changes
  const { items, total } = useCartState();
  return <span>{items.length} items, Rs {total}</span>;
}

createRoot(document.getElementById('root')).render(
  <CartProvider>
    <CartBadge />
    <AddButton item={{ id: 1, name: 'Paneer Tikka', price: 220 }} />
  </CartProvider>
);
```

---

## 🟠 Next.js Connection

In the App Router, the Provider must be a Client Component (it uses state and context). Create a `providers.jsx` with `'use client'` and render it in the root `layout.jsx`. Since the Provider receives `children`, the pages inside remain Server Components (children passed as props are not turned into client code). Do not read `localStorage` during render (server has none); initialize in an effect, or use cookies for SSR-safe values like theme. Libraries (TanStack Query's `QueryClientProvider`, Redux `Provider`, next-themes) follow the same approach.

```jsx
// app/providers.jsx
'use client';                                              // context + hooks → client
import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'; // TanStack Query v5

export default function Providers({ children }) {
  const [client] = useState(() => new QueryClient());      // one client per browser session (not module-level on the server)
  return (
    <QueryClientProvider client={client}>
      <CartProvider>{children}</CartProvider>              {/* your own provider, nested */}
    </QueryClientProvider>
  );
}

// app/layout.jsx (Server Component)
import Providers from './providers';
export default function RootLayout({ children }) {
  return <html lang="en"><body><Providers>{children}</Providers></body></html>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Passing a fresh object literal as the Provider value
✅ **Correct:** Memoize it (`useMemo`) so consumers re-render only on real changes

```jsx
// Wrong: new object each render → all consumers re-render whenever Provider re-renders
<Ctx.Provider value={{ user, login }}>          // ❌
// Right
const value = useMemo(() => ({ user, login }), [user, login]);   // ✅ (login should be useCallback)
<Ctx.Provider value={value}>
```

❌ **Mistake 2:** One giant context for everything
✅ **Correct:** Split by domain and update frequency

```jsx
// Wrong: typing in a search field (global state) re-renders the whole app's consumers
<AppContext.Provider value={{ user, cart, theme, search }}>   // ❌
// Right: AuthContext, CartContext, ThemeContext, and keep fast-changing state local
```

❌ **Mistake 3:** Using the context without a Provider (silent `undefined`)
✅ **Correct:** Use a hook that throws when the Provider is missing

```jsx
// Wrong
const { items } = useContext(CartContext);       // ❌ crashes with "cannot destructure of undefined/null"
// Right
function useCart() { const c = useContext(CartContext); if (!c) throw new Error('Wrap in <CartProvider>'); return c; }
```

---

## 🧠 Tricky Interview Question

```jsx
const Ctx = createContext(0);
const Child = memo(function Child() {
  console.log('Child render');
  return <p>static</p>;
});
const Consumer = () => <p>{useContext(Ctx)}</p>;

function App() {
  const [n, setN] = useState(0);
  return (
    <Ctx.Provider value={n}>
      <button onClick={() => setN(n + 1)}>+</button>
      <Child />
      <Consumer />
    </Ctx.Provider>
  );
}
```
**Answer:** On each click, `Consumer` re-renders (it reads the changed context value), while `Child` does NOT print again: it is wrapped in `memo`, has no props and does not use the context. Without `memo`, `Child` would re-render because `App` re-rendered and created a new `<Child />` element. Key point: context updates bypass `memo` for consumers, while non-consumers are protected by `memo` (or by being passed through `children`).

---

## ⚫ Interview Questions + Answers

Q1: What is the Provider pattern?
A1: A Provider component owns state/services and exposes them to the subtree through context. Consumers use a custom hook to read it, so no props drilling is needed.

Q2: When do consumers re-render?
A2: When the Provider's `value` changes by `Object.is`. A new object/array/function each render counts as changed, so memoize the value.

Q3: Why wrap `useContext` in a custom hook?
A3: To hide the context object, give a better API, throw a clear error when the Provider is missing, and allow changing the internals later without touching consumers.

Q4: When is Context not enough?
A4: For frequently updating or large state, because all consumers re-render and there are no selectors. Use Zustand, Redux Toolkit or Jotai, or split contexts, or use TanStack Query for server state.

Q5: How do Providers work with Next.js Server Components?
A5: Providers are Client Components. Put `'use client'` in a `providers.jsx`, render it in the root layout, and pass `children` through so server pages inside stay server-rendered.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Sharing slow-changing global data: theme, auth user, locale, feature flags
- Dependency injection (API client, QueryClient, router)
- Compound components need shared internal state

❌ **Avoid when:**
- Data changes many times per second (mouse position, input text)
- Only two levels are involved (just pass props or use composition)
- You need fine-grained subscriptions (use a store library)

---

## 📊 Visual Diagram

```
 <Providers>                      ← AuthProvider, ThemeProvider, CartProvider
   └─ <Layout>
        ├─ <Header>
        │     └─ <CartBadge/>   ── useCartState() ◀─┐
        ├─ <Menu>                                     │  context lookup
        │     └─ <AddButton/>   ── useCartActions() ◀─┤  (no props passed
        └─ <Checkout/>          ── useCartState() ◀──┘   through Layout/Header/Menu)

 value changes → only components that CALL the hook re-render (plus their children)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Provider | Component that supplies a context value | Context value देने वाला component |
| Consumer | Component reading a context | Context पढ़ने वाला component |
| Context | Mechanism to share data across the tree | Tree भर में data share करने की व्यवस्था |
| Props drilling | Passing props through unrelated layers | बेकार layers से props गुज़ारना |
| Custom hook | `useX()` wrapper around `useContext` | `useContext` को लपेटने वाला hook |
| Memoized value | Value kept stable with `useMemo` | `useMemo` से स्थिर रखी value |
| Split contexts | Separate contexts for state and actions | State और actions के अलग contexts |
| Dependency injection | Providing services via context | Context से services देना |

---

## ⚡ 3-Line Summary
**English:**
1. A Provider holds state and shares it to any descendant through context and a custom hook.
2. Memoize the value, split contexts by update frequency, and throw when the Provider is missing.
3. In Next.js, make Providers Client Components in `providers.jsx` and keep pages as server children.

**Hindi:**
1. Provider state रखता है और context व custom hook से किसी भी descendant को देता है।
2. Value को memoize करो, update frequency के हिसाब से contexts बाँटो, और Provider न होने पर error फेंको।
3. Next.js में Providers को `providers.jsx` में Client Components बनाओ और pages को server children रखो।

---

## ➡️ Next Topic
**146. Container + Presentational Pattern** — Data/logic वाले components और सिर्फ UI दिखाने वाले components को अलग करना, जो आज hooks और Server Components के रूप में दिखता है।
