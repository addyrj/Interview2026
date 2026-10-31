# 93. Context API for State Management
# हिंदी में: Context API — State Management के लिए Context का इस्तेमाल

---

## 🔵 Simple Definition (English)
Context API lets you share a value with any component below a **Provider** without passing props through every level. A component reads it with `useContext(MyContext)`. It is built into React, so you can share theme, user or cart without installing a library.

## 🔵 सरल परिभाषा (Hindi)
Context API आपको एक value को **Provider** के नीचे के किसी भी component तक बिना हर level पर props भेजे पहुँचाने देता है। Component उसे `useContext(MyContext)` से पढ़ता है। यह React में पहले से है, इसलिए theme, user या cart share करने के लिए कोई library install करने की जरूरत नहीं।

---

## 🔴 Problem it Solves
Prop drilling (topic 91) forces every middle component to accept and forward props it does not use. Theme, logged-in user and language change rarely but are needed deep in the tree. Context removes the middle layers: the value is provided once at the top and read directly where it is needed. The limit is that Context is a broadcast. Every consumer re-renders when the value changes, so it suits data that changes rarely.

## 🔴 यह क्यों बना? (Hindi)
Prop drilling (topic 91) में हर बीच वाला component ऐसे props लेता और आगे भेजता है जो वह खुद इस्तेमाल नहीं करता। Theme, logged-in user और language बहुत कम बदलते हैं, पर tree में गहराई पर चाहिए होते हैं। Context बीच की layers हटा देता है: value ऊपर एक बार दी जाती है, और जहाँ चाहिए वहीं पढ़ी जाती है। सीमा यह है कि Context एक broadcast है। Value बदलने पर हर consumer re-render होता है, इसलिए यह कम बदलने वाले data के लिए अच्छा है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create the context with a default value:
         const ThemeContext = createContext('light');

Step 2 → Wrap the subtree in a Provider with a value:
         <ThemeContext.Provider value="dark"> ... </ThemeContext.Provider>

Step 3 → Any component inside calls useContext(ThemeContext) → "dark"

Step 4 → Provider value changes → React re-renders ALL consumers below it

Step 5 → No Provider above a consumer → useContext returns the default ('light')

KEY: The NEAREST Provider wins. Provider value of undefined is NOT the default.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Context बनाओ, default value के साथ: createContext('light')
Step 2 → Subtree को Provider में लपेटो: <ThemeContext.Provider value="dark">
Step 3 → अंदर का कोई भी component useContext(ThemeContext) से "dark" पढ़ता है
Step 4 → Provider की value बदलने पर नीचे के सभी consumers re-render होते हैं
Step 5 → ऊपर कोई Provider न हो तो useContext default ('light') लौटाता है
KEY: सबसे नज़दीकी Provider जीतता है। Provider की value undefined, default नहीं है।
```

---

## 🟡 Real World Example
**Zomato app language and theme:** The app is in English or Hindi, and users can switch to dark mode. A `LocaleProvider` wraps the whole app once. The search bar, the restaurant card and the footer all call `useLocale()` and show the right text, without any of them receiving a `locale` prop. When a user switches to Hindi, the value changes once and every screen updates together.

## 🟡 Real Example Hindi mein
**Zomato app की language और theme:** App English या Hindi में हो सकती है, और user dark mode चुन सकता है। एक `LocaleProvider` पूरी app को एक बार wrap करता है। Search bar, restaurant card और footer सभी `useLocale()` call करके सही text दिखाते हैं, बिना किसी को `locale` prop भेजे। User Hindi चुने तो value एक बार बदलती है और हर screen एक साथ update हो जाती है।

---

## 💻 Code Example — Basic

```jsx
import { createContext, useContext, useState } from 'react';

// Step 1: create the context. 'light' is the default used with NO Provider above
const ThemeContext = createContext('light');

// Step 2: a Provider component that owns the theme state and shares it
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');   // the value to share
  const toggle = () => setTheme((t) => (t === 'light' ? 'dark' : 'light'));

  return (
    // Provider value = what consumers receive; it is an object here so they can toggle too
    <ThemeContext.Provider value={{ theme, toggle }}>
      {children}  {/* everything inside is a potential consumer */}
    </ThemeContext.Provider>
  );
}

// Step 3: a deep consumer. No props needed.
function ThemeButton() {
  const { theme, toggle } = useContext(ThemeContext); // read from nearest Provider
  return <button onClick={toggle}>Current: {theme}</button>;
}

// Another consumer far down the tree
function Footer() {
  const { theme } = useContext(ThemeContext); // same value, different component
  return <footer>Theme: {theme}</footer>;
}

export default function App() {
  return (
    <ThemeProvider>
      <ThemeButton />  {/* both read the same shared value */}
      <Footer />
    </ThemeProvider>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { createContext, useContext, useReducer, useMemo } from 'react';

// Two SEPARATE contexts: state changes often, dispatch never changes.
// Splitting them means components that only dispatch do not re-render on state changes.
const CartStateContext = createContext(undefined);      // undefined = "no provider"
const CartDispatchContext = createContext(undefined);

// Pure reducer: returns the next state, never mutates the old one
function cartReducer(state, action) {
  switch (action.type) {
    case 'ADD': {
      // Check whether this product is already in the cart
      const existing = state.items.find((i) => i.id === action.product.id);
      if (existing) {
        // Immutable update: map to a new array with the changed item
        return {
          ...state,
          items: state.items.map((i) =>
            i.id === action.product.id ? { ...i, qty: i.qty + 1 } : i
          ),
        };
      }
      // New product: add it with quantity 1
      return { ...state, items: [...state.items, { ...action.product, qty: 1 }] };
    }
    case 'REMOVE':
      // Keep every item except the one with this id
      return { ...state, items: state.items.filter((i) => i.id !== action.id) };
    default:
      // Unknown action: return the same state (React bails out of re-render)
      return state;
  }
}

// Provider: holds state with useReducer and shares both state and dispatch
export function CartProvider({ children }) {
  const [state, dispatch] = useReducer(cartReducer, { items: [] }); // initial state

  return (
    <CartStateContext.Provider value={state}>
      {/* dispatch from useReducer is stable across renders, safe to share directly */}
      <CartDispatchContext.Provider value={dispatch}>
        {children}
      </CartDispatchContext.Provider>
    </CartStateContext.Provider>
  );
}

// Custom hooks: check the Provider exists and give a clear error message if not
export function useCartState() {
  const state = useContext(CartStateContext);     // read the state context
  if (state === undefined) {                      // no Provider above this component
    throw new Error('useCartState must be used inside <CartProvider>');
  }
  return state;
}

export function useCartDispatch() {
  const dispatch = useContext(CartDispatchContext); // read the dispatch context
  if (dispatch === undefined) {                    // same guard for dispatch
    throw new Error('useCartDispatch must be used inside <CartProvider>');
  }
  return dispatch;
}

// A component that only adds items: it does NOT re-render when the cart changes
export function AddButton({ product }) {
  const dispatch = useCartDispatch();              // subscribes to dispatch only
  return <button onClick={() => dispatch({ type: 'ADD', product })}>Add</button>;
}
```

---

## 🟠 Real App Integration (React + Next.js)

In Next.js App Router, a Context Provider uses state and hooks, so it must be a **Client Component**. Put the Provider in a small `providers.jsx` file and wrap `children` in the root layout, which stays a Server Component.

```jsx
// app/providers.jsx — Client Component that owns the shared context
'use client';                                    // Context needs state, so this runs in the browser
import { ThemeProvider } from '../lib/theme';   // the ThemeProvider from the Basic example

export function Providers({ children }) {
  return <ThemeProvider>{children}</ThemeProvider>; // wrap the whole app once
}
```

```jsx
// app/layout.jsx — Server Component; passes server-rendered children into the client Provider
import { Providers } from './providers';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers> {/* every page is a consumer-capable child */}
      </body>
    </html>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting the Provider and getting the default silently
✅ **Correct:** Default values hide missing Providers. Use `undefined` as the default and throw in a custom hook, as the advanced example does.

```jsx
// Wrong: silently uses the default, bugs appear far from the cause
const ctx = createContext({ user: null });
const { user } = useContext(ctx);               // ❌ no error without a Provider

// Right: fail loudly where the mistake is made
const ctx = createContext(undefined);
function useUser() {
  const value = useContext(ctx);
  if (value === undefined) throw new Error('useUser needs <UserProvider>'); // ✅
  return value;
}
```

❌ **Mistake 2:** Putting everything into one giant context
✅ **Correct:** Split contexts by how often they change. A "theme" context should not re-render components that only read the cart.

```jsx
// Wrong: one context for everything — any change re-renders all consumers
<AppContext.Provider value={{ theme, user, cart, toggleTheme, addItem }}>

// Right: separate providers for separate concerns
<ThemeContext.Provider value={themeValue}>
  <CartContext.Provider value={cartValue}>
```

---

## 🧠 Tricky Interview Question

```jsx
import { createContext, useContext } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';

const ThemeContext = createContext('light');   // default value

function ThemeLabel() {
  const theme = useContext(ThemeContext);      // nearest Provider or the default
  return <span>{theme}</span>;
}

const html = renderToStaticMarkup(
  <div>
    {/* case 1: nearest Provider wins */}
    <ThemeContext.Provider value="dark">
      <ThemeLabel />
    </ThemeContext.Provider>
    {/* case 2: no Provider above, so the default is used */}
    <ThemeLabel />
    {/* case 3: Provider exists with undefined, so no default */}
    <ThemeContext.Provider value={undefined}>
      <ThemeLabel />
    </ThemeContext.Provider>
  </div>
);
console.log(html);
```

**Answer:** The output is `<div><span>dark</span><span>light</span><span></span></div>`. Case 1 reads the nearest Provider, `dark`. Case 2 has no Provider above it, so `useContext` returns the default `light`. Case 3 is the trap: a Provider **exists** with `value={undefined}`, so `useContext` returns `undefined`, and React renders nothing inside the span. A Provider's value always overrides the default, even when it is `undefined`. That is exactly why the advanced example checks for `undefined` and throws a clear error.

---

## ⚫ Interview Questions + Answers

**Q1: What problem does Context solve?**
A1: It removes prop drilling. A value is provided once above a subtree and read by any component below it, without passing props through the middle layers.

**Q2: How does a consumer read a context value?**
A2: Call `useContext(MyContext)` inside a function component or a custom hook. React returns the value of the nearest Provider above the component, or the default if there is none.

**Q3: Does Context replace Redux?**
A3: For small amounts of rarely changing data, yes. For frequent updates, complex transitions and large shared state, Context re-renders every consumer on each change, so a store with selectors (topics 94–98) is better.

**Q4: How do you avoid unnecessary re-renders with Context?**
A4: Split contexts by change frequency, memoize the Provider value with `useMemo`, and keep dispatch functions in their own context since they never change.

**Q5: Can a Provider be a Client Component in Next.js?**
A5: Yes, and it usually must be. Context Providers use state and hooks, so they need `'use client'`. Wrap `children` in the Provider from a Server Component layout.

---

## 🔷 When to Use + When Not to Use
✅ **Use Context when:**
- Value is needed by many components at different depths (theme, locale, current user)
- Value changes rarely (login state, language, feature flags)
- You want shared state without adding a library

❌ **Avoid Context when:**
- Value changes many times per second (typing, mouse position, animations)
- Only a few sibling components need it (lift state up instead)
- You need selectors so each component updates only for the part it reads

---

## 📊 Visual Diagram

```
createContext('light')
        │
        ▼
<ThemeContext.Provider value="dark">          ← nearest provider wins
   ├── <ThemeButton />   useContext → "dark"
   └── <div>
          └── <Footer /> useContext → "dark"

<div>                                          ← no provider above
   └── <ThemeLabel />    useContext → "light" (default)

When value changes:
   Provider value "dark" → "light"
        │
        ▼
   React re-renders ALL consumers below, even if they show only part of the value
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| createContext | Creates a context object with a default value | Default value के साथ context object बनाना |
| Provider | Component that supplies the value to its subtree | Subtree को value देने वाला component |
| useContext | Hook that reads the nearest provider value | Nearest provider की value पढ़ने वाला hook |
| Consumer | Any component that calls useContext | `useContext` call करने वाला component |
| Default value | Value used when no Provider exists above | Provider न होने पर इस्तेमाल होने वाली value |
| Broadcast | Context sends changes to all consumers | Context का सभी consumers को change भेजना |

---

## ⚡ 3-Line Summary
**English:**
1. Context shares one value with any component below a Provider, without props at each level.
2. Read it with `useContext`; the nearest Provider wins and the default applies only without a Provider.
3. Every consumer re-renders on change, so keep values stable, split contexts, and use a store for frequent updates.

**Hindi:**
1. Context एक value को Provider के नीचे के किसी भी component तक बिना हर level पर props के पहुँचाता है।
2. `useContext` से पढ़ो; नज़दीकी Provider जीतता है, और default सिर्फ Provider न होने पर लगता है।
3. बदलने पर हर consumer re-render होता है, इसलिए values stable रखो, contexts बाँटो, और बार-बार बदलने वाले data के लिए store इस्तेमाल करो।

---

## ➡️ Next Topic
**94. Redux — Core Concepts** — Redux का store, action और reducer मॉडल, जो बड़ी apps में predictable state update देता है। Context की broadcast सीमा के बाद अगला कदम selectors वाला centralized store है।
