# 43. Context API — Complete Guide
# हिंदी में: Context API — Data को पूरे Tree में बाँटना, पूरी Guide

---

## 🔵 Simple Definition (English)
The **Context API** lets a parent component make a value available to **any component below it**, no matter how deep, without passing props through every level. You create it with `createContext`, supply it with `<Context.Provider>` (or `<Context>` in React 19), and read it with `useContext`.

## 🔵 सरल परिभाषा (Hindi)
**Context API** से कोई parent component अपने नीचे के **किसी भी component** को value उपलब्ध करा सकता है, चाहे वह कितना भी गहरा हो, बिना हर स्तर से props गुज़ारे। आप `createContext` से इसे बनाते हैं, `<Context.Provider>` (React 19 में `<Context>`) से value देते हैं, और `useContext` से पढ़ते हैं।

---

## 🔴 Problem it Solves

Some data is needed all over the app: logged-in user, theme, language, cart. Passing it as props through every level (**props drilling**) makes middle components carry props they never use, and any change touches many files. Global variables do not trigger re-renders. Context gives React a way to broadcast a value and update every consumer when it changes.

```jsx
// PROBLEM: user passed through Page → Header → Nav → Avatar (only Avatar uses it)
<Page user={user}>  <Header user={user}>  <Nav user={user}>  <Avatar user={user} />

// SOLUTION: provide once, read where needed
<UserContext.Provider value={user}>
  <Page />                      {/* Page, Header, Nav need no user prop */}
</UserContext.Provider>
// inside Avatar: const user = useContext(UserContext);
```

## 🔴 यह क्यों बना? (Hindi)
कुछ data पूरे app में चाहिए होता है: logged-in user, theme, भाषा, cart। इसे हर स्तर से props में भेजना (**props drilling**) बीच के components पर वे props लाद देता है जिन्हें वे इस्तेमाल नहीं करते, और बदलाव कई files छूता है। Global variables re-render नहीं कराते। Context React को value broadcast करने का तरीका देता है और value बदलने पर हर consumer को update करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → const ThemeContext = createContext(defaultValue)      // create (module level)
Step 2 → Wrap a subtree: <ThemeContext.Provider value={x}>    // provide
Step 3 → Any descendant calls useContext(ThemeContext)         // consume
Step 4 → React finds the NEAREST Provider above the consumer and returns its value
Step 5 → No Provider above? You get the default value from createContext
Step 6 → When Provider's value changes (Object.is), EVERY consumer re-renders, even if wrapped in React.memo

BEST PRACTICE: wrap Provider + state in one component, expose a custom hook
  function useTheme() { const c = useContext(ThemeContext); if (!c) throw ...; return c; }
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → const ThemeContext = createContext(defaultValue)      // बनाओ (module level पर)
Step 2 → Subtree को wrap करो: <ThemeContext.Provider value={x}>  // value दो
Step 3 → कोई भी descendant useContext(ThemeContext) बुलाता है     // पढ़ो
Step 4 → React consumer के ऊपर का सबसे NEAREST Provider ढूँढकर उसकी value देता है
Step 5 → ऊपर कोई Provider नहीं? createContext की default value मिलती है
Step 6 → Provider की value बदले (Object.is) तो HAR consumer re-render होता है, React.memo में हो तब भी

Best practice: Provider + state को एक component में रखो, और custom hook expose करो
  function useTheme() { const c = useContext(ThemeContext); if (!c) throw ...; return c; }
```

---

## 🟡 Real World Example
**Amazon:** The header shows "Hello, Aditya", the product page shows "Deliver to Delhi 110001", and checkout needs the same user and address. A `UserContext` (user + address) and a `CartContext` (items + count) are provided once at the top. The cart badge in the header reads `CartContext`; the "Add to Cart" button on a deep product card calls `addItem` from the same context. No props are passed through the layout components.

## 🟡 Real Example Hindi mein
**Amazon:** Header में "Hello, Aditya" दिखता है, product page पर "Deliver to Delhi 110001", और checkout को वही user व address चाहिए। एक `UserContext` (user + address) और एक `CartContext` (items + count) ऊपर एक बार provide होते हैं। Header का cart badge `CartContext` पढ़ता है; गहरे product card का "Add to Cart" बटन उसी context से `addItem` बुलाता है। Layout components से कोई props नहीं गुज़रते।

---

## 💻 Code Example — Basic

```jsx
// Theme context: create → provide → consume
import { createContext, useContext, useState } from 'react'; // context API + state
import { createRoot } from 'react-dom/client';               // React 18/19 root API

const ThemeContext = createContext('light');         // default 'light' if no Provider is found

function ThemeButton() {
  const theme = useContext(ThemeContext);            // read nearest Provider value
  return <button style={{ background: theme === 'dark' ? '#222' : '#eee',
                          color: theme === 'dark' ? '#fff' : '#000' }}>
    Theme: {theme}
  </button>;
}

function Toolbar() {
  return <div><ThemeButton /></div>;                 // no theme prop passed here
}

function App() {
  const [theme, setTheme] = useState('dark');        // state that lives in the provider owner
  return (
    <ThemeContext.Provider value={theme}>            {/* every descendant can read it */}
      <Toolbar />
      <button onClick={() => setTheme(t => (t === 'dark' ? 'light' : 'dark'))}>
        Toggle                                       {/* changing state updates all consumers */}
      </button>
    </ThemeContext.Provider>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

## 💻 Code Example — Advanced

```jsx
// Production cart context: reducer, split contexts (state vs actions), memoized value, safe hook
import { createContext, useContext, useReducer, useMemo } from 'react';
import { createRoot } from 'react-dom/client';

const CartStateContext = createContext(null);        // holds data (changes often)
const CartActionsContext = createContext(null);      // holds functions (stable identity)

function cartReducer(state, action) {                // pure reducer: easy to test
  switch (action.type) {
    case 'add': {
      const found = state.items.find(i => i.id === action.item.id);
      const items = found
        ? state.items.map(i => i.id === action.item.id ? { ...i, qty: i.qty + 1 } : i) // bump qty
        : [...state.items, { ...action.item, qty: 1 }];                                // add new
      return { ...state, items };
    }
    case 'remove':
      return { ...state, items: state.items.filter(i => i.id !== action.id) };
    case 'clear':
      return { ...state, items: [] };
    default:
      throw new Error(`Unknown action: ${action.type}`);
  }
}

export function CartProvider({ children }) {
  const [state, dispatch] = useReducer(cartReducer, { items: [] }); // one source of truth

  const actions = useMemo(() => ({                   // dispatch is stable → actions never change
    add: item => dispatch({ type: 'add', item }),
    remove: id => dispatch({ type: 'remove', id }),
    clear: () => dispatch({ type: 'clear' }),
  }), []);

  return (
    <CartActionsContext.Provider value={actions}>    {/* components that only click buttons */}
      <CartStateContext.Provider value={state}>      {/* components that display data */}
        {children}
      </CartStateContext.Provider>
    </CartActionsContext.Provider>
  );
}

export function useCart() {                          // custom hook hides context plumbing
  const state = useContext(CartStateContext);
  if (!state) throw new Error('useCart must be used inside <CartProvider>'); // clear error
  return state;
}

export function useCartActions() {
  const actions = useContext(CartActionsContext);
  if (!actions) throw new Error('useCartActions must be used inside <CartProvider>');
  return actions;
}

function AddButton({ item }) {                       // reads only actions → does not re-render on cart changes
  const { add } = useCartActions();
  return <button onClick={() => add(item)}>Add {item.name}</button>;
}

function CartBadge() {                               // reads state → re-renders when cart changes
  const { items } = useCart();
  const count = items.reduce((n, i) => n + i.qty, 0);
  return <span>Cart ({count})</span>;
}

function App() {
  return (
    <CartProvider>
      <CartBadge />
      <AddButton item={{ id: 1, name: 'Headphones' }} />
      <AddButton item={{ id: 2, name: 'Mouse' }} />
    </CartProvider>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

---

## 🟠 Next.js Connection

Context only works in **Client Components**. In the App Router, put providers in a `'use client'` file and wrap `{children}` in `app/layout.jsx` (a Server Component). The children passed through stay Server Components, because they are passed as props, not imported by the provider. Create providers as deep as possible in the tree so more of the app stays on the server. Never put per-user data in a module-level variable on the server (shared between requests); use context or request-scoped APIs.

```jsx
// app/providers.jsx (Client Component)
'use client';
import { CartProvider } from '@/components/cart-context';   // the provider from the advanced example

export default function Providers({ children }) {
  return <CartProvider>{children}</CartProvider>;           // children can still be Server Components
}
```

```jsx
// app/layout.jsx (Server Component)
import Providers from './providers';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>                   {/* pages below can use useCart() in client parts */}
      </body>
    </html>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Passing a new object literal as `value` on each render
✅ **Correct:** Memoize it (or keep it in state), so consumers do not re-render needlessly

```jsx
// Wrong: new object each render → ALL consumers re-render whenever Provider's parent renders
<ThemeContext.Provider value={{ theme, setTheme }}>{children}</ThemeContext.Provider>   // ❌

// Right
const value = useMemo(() => ({ theme, setTheme }), [theme]);   // setTheme from useState is stable
<ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>               // ✅
```

❌ **Mistake 2:** Putting fast-changing values (mouse position, form input) in a global context
✅ **Correct:** Keep fast state local; use context for slow-changing app-wide data

```jsx
// Wrong: every keystroke re-renders every consumer of FormContext
// Right: local state for the input, push to context only on submit
```

❌ **Mistake 3:** Using a consumer without a Provider and getting `undefined` errors
✅ **Correct:** Create the context with `null`, and throw a helpful error inside the custom hook

```jsx
// Wrong
const { items } = useContext(CartContext);              // ❌ TypeError if no Provider (default null)

// Right
function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error('Wrap your app in <CartProvider>');   // ✅ clear message
  return ctx;
}
```

---

## 🧠 Tricky Interview Question

```jsx
const Ctx = createContext('default');

function Child() {
  console.log('Child render', useContext(Ctx));
  return null;
}
const Memo = React.memo(Child);

function App() {
  const [v, setV] = useState('a');
  return (
    <Ctx.Provider value={v}>
      <Memo />
      <button onClick={() => setV('b')}>change</button>
    </Ctx.Provider>
  );
}
```
**Answer:** `Memo` has no props, so `React.memo` skips re-renders caused by the parent. But `Child` calls `useContext(Ctx)`, so it subscribes to the context. When `v` changes from `'a'` to `'b'`, React re-renders `Child` anyway and logs `Child render b`. `React.memo` cannot block context updates. Mount logs `Child render a`; the click logs `Child render b`.

---

## ⚫ Interview Questions + Answers

Q1: What is Context and what problem does it solve?
A1: It is React's built-in way to share data across the component tree without passing props at every level. It solves props drilling for app-wide values such as theme, user, locale.

Q2: What happens when a context value changes?
A2: Every component that calls `useContext` for that context re-renders, regardless of `React.memo` or `shouldComponentUpdate` on parents. Components between the Provider and consumers that do not consume it are not forced to re-render by the context change itself.

Q3: Is Context a state management library?
A3: No. It is only a transport. State comes from `useState` or `useReducer`. For frequently updating or complex global state, Redux Toolkit, Zustand or TanStack Query (for server data) are often better because they allow selective subscriptions.

Q4: How do you avoid unnecessary re-renders with Context?
A4: Memoize the `value`, split contexts (state vs actions, or by domain), keep Provider close to its users, and move rarely-changing and fast-changing data into separate contexts.

Q5: What is the default value used for?
A5: It is returned only when no matching Provider exists above the consumer. It is useful for tests and standalone components. For required providers, use `null` plus a throwing custom hook.

---

## 🔷 When to Use + When Not to Use
✅ **Use Context when:**
- Many components at different depths need the same slow-changing value (theme, auth user, locale)
- You want to avoid props drilling across more than 2 to 3 levels
- You are building compound components that share internal state

❌ **Avoid Context when:**
- The value changes very often (typing, animations, mouse move)
- Only one or two levels are involved (just pass props or use composition with `children`)
- You need selectors or devtools-level control (use Redux Toolkit or Zustand)

---

## 📊 Visual Diagram

```
 createContext()
      │
      ▼
 <Provider value={v}>  ◄── state lives in the component that renders Provider
      │
      ├── <Layout>             (does NOT need to know about v)
      │      ├── <Header>
      │      │      └── <CartBadge />  ── useContext() ──► gets v
      │      └── <Main>
      │             └── <ProductCard>
      │                    └── <AddButton /> ── useContext() ──► gets v
      │
 v changes ──► Provider re-renders ──► ONLY consumers re-render (Layout etc. are skipped if memoized or passed as children)

 Performance: new object as value every render = every consumer re-renders every time → memoize
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| createContext | Creates a context object | Context object बनाता है |
| Provider | Supplies the value to its subtree | अपने subtree को value देने वाला |
| Consumer / useContext | Reads the nearest value | नज़दीकी value पढ़ने वाला |
| Default value | Used when no Provider exists | Provider न होने पर इस्तेमाल होने वाली value |
| Props drilling | Passing props through many levels | कई स्तरों से props गुज़ारना |
| Memoized value | Value kept stable between renders | Renders के बीच स्थिर रखी value |
| Split context | Separate contexts for state and actions | State और actions के अलग contexts |

---

## ⚡ 3-Line Summary
**English:**
1. Context broadcasts a value from a Provider to every consumer below it, via `useContext`.
2. A changing value re-renders all consumers, so memoize the value and split contexts.
3. It is for slow-changing app-wide data; in Next.js it needs Client Components.

**Hindi:**
1. Context Provider से उसके नीचे के हर consumer को `useContext` के ज़रिए value broadcast करता है।
2. Value बदलने पर सारे consumers re-render होते हैं, इसलिए value को memoize करो और contexts बाँटो।
3. यह धीरे बदलने वाले app-wide data के लिए है; Next.js में इसके लिए Client Components चाहिए।

---

## 📚 Go Deeper — External Resources
| Type | Link | Why |
|------|------|-----|
| 📝 Article | [react.dev — Passing Data Deeply with Context](https://react.dev/learn/passing-data-deeply-with-context) | Official tutorial |
| 📝 Article | [react.dev — createContext](https://react.dev/reference/react/createContext) | API reference (React 19: `<Context>` as a provider) |

---

## ➡️ Next Topic
**44. Context API vs Props Drilling** — कब Context सही है और कब सिर्फ़ props या composition काफ़ी है। इससे आप over-engineering से बचेंगे।
