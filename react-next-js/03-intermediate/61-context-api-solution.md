# 61. Context API Solution
# हिंदी में: Context API — Props Drilling का हल

---

## 🔵 Simple Definition (English)
The **Context API** lets a value be provided once at the top of a tree (`<Context.Provider value={...}>`) and read by any descendant component with `useContext(Context)`. The middle components no longer need to pass the value along, so props drilling disappears for that data.

## 🔵 सरल परिभाषा (Hindi)
**Context API** एक value को tree के ऊपर एक बार (`<Context.Provider value={...}>`) देने देता है, और उसके नीचे का कोई भी component `useContext(Context)` से उसे पढ़ सकता है। बीच के components को value आगे भेजनी नहीं पड़ती, इसलिए उस data के लिए props drilling खत्म हो जाती है।

---

## 🔴 Problem it Solves

Props drilling (topic 60) forces every intermediate component to accept and forward values it does not use. Shared values such as the logged-in user, theme, language or cart count are needed in many places at different depths. Passing them manually is repetitive and fragile. Context gives a direct channel from a provider to any consumer below it, so the tree in between stays clean.

```jsx
// PROBLEM: theme must reach Profile, but Layout and Sidebar only forward it
<Layout theme={theme}>          {/* Layout ignores theme */}
  <Sidebar theme={theme} />     {/* Sidebar ignores theme */}
</Layout>

// SOLUTION: provide once, read anywhere below
<ThemeContext.Provider value={theme}>
  <Layout />                    {/* no theme prop at all */}
</ThemeContext.Provider>
// deep inside: const theme = useContext(ThemeContext);
```

## 🔴 यह क्यों बना? (Hindi)
Props drilling (topic 60) में हर बीच के component को ऐसी values लेनी और आगे भेजनी पड़ती हैं जिनकी उसे ज़रूरत नहीं। Logged-in user, theme, language या cart count कई जगह और अलग-अलग गहराई पर चाहिए। इन्हें हाथ से भेजना दोहराव और नाज़ुकपन लाता है। Context ऊपर के provider से नीचे के किसी भी consumer तक सीधा रास्ता देता है, इसलिए बीच का tree साफ़ रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → createContext(defaultValue)       → creates a Context object with a fallback value
Step 2 → <Context.Provider value={v}>      → wraps part of the tree and supplies v
Step 3 → Any descendant calls useContext(Context) → gets the NEAREST provider's v
Step 4 → If no Provider is above, useContext returns defaultValue
Step 5 → When the provider's value changes (Object.is), ALL consumers below re-render
Step 6 → Middle components between provider and consumer are NOT forced to re-render
          just because a context exists; only consumers re-render on value change

Tip: memoize the value object (useMemo) so the provider does not change on every render
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → createContext(defaultValue)       → Context object बनता है, जिसकी fallback value होती है
Step 2 → <Context.Provider value={v}>      → tree के हिस्से को wrap करता है और v देता है
Step 3 → नीचे का कोई भी component useContext(Context) लिखता है → सबसे नज़दीकी provider की v मिलती है
Step 4 → ऊपर कोई Provider न हो तो useContext defaultValue लौटाता है
Step 5 → Provider की value बदले (Object.is से), तो नीचे के सभी consumers re-render होते हैं
Step 6 → Provider और consumer के बीच के components खुद re-render नहीं होते, सिर्फ consumers होते हैं

Tip: value object को useMemo में रखो, ताकि हर render पर provider की value नई न बने
```

---

## 🟡 Real World Example
**Razorpay checkout:** The checkout flow has a `PaymentProvider` at the top that holds the merchant key, selected method and amount. The `Header` shows the amount, the `PaymentForm` reads the selected method, and the `SubmitButton` reads the merchant key. None of the layout components between them touch these values. Context gives each one direct access, so adding a new field (for example a currency code) does not change the layout components at all.

## 🟡 Real Example Hindi mein
**Razorpay checkout:** Checkout flow के ऊपर एक `PaymentProvider` है, जिसमें merchant key, चुना गया method और amount रहता है। `Header` amount दिखाता है, `PaymentForm` चुना हुआ method पढ़ता है, और `SubmitButton` merchant key पढ़ता है। इनके बीच के layout components इन values को छूते तक नहीं। Context हर component को सीधा access देता है, इसलिए नया field (जैसे currency code) जोड़ने पर layout components में कोई बदलाव नहीं होता।

---

## 💻 Code Example — Basic

```jsx
// Theme toggle: one Provider at the top, consumers read it at any depth
import { createContext, useContext, useState } from 'react';  // Context tools + state
import { createRoot } from 'react-dom/client';                 // React 18/19 root API

// Default value: used ONLY when a component has no Provider above it
const ThemeContext = createContext({ theme: 'light', toggle: () => {} });

function ThemeToggleButton() {                  // deep consumer: no props received
  const { theme, toggle } = useContext(ThemeContext); // read the nearest provider's value
  return <button onClick={toggle}>Theme: {theme}</button>; // label shows current theme
}

function Layout({ children }) {                 // middle component: knows nothing about theme
  return <div className="layout">{children}</div>; // just a wrapper
}

function App() {
  const [theme, setTheme] = useState('light');  // real state lives here
  const value = {                               // value object given to the provider
    theme,                                      // current theme string
    toggle: () => setTheme(t => (t === 'light' ? 'dark' : 'light')), // flip the theme
  };
  return (
    <ThemeContext.Provider value={value}>       {/* everything below can read value */}
      <Layout>
        <ThemeToggleButton />                   {/* reads context directly, no props */}
      </Layout>
    </ThemeContext.Provider>
  );
}

const root = createRoot(document.getElementById('root'));
root.render(<App />);
setTimeout(() => document.querySelector('button').click(), 50); // demo: click after 50 ms (light → dark)
setTimeout(() => console.log(document.getElementById('root').innerHTML), 100); // React re-rendered by now: shows "Theme: dark"
```

## 💻 Code Example — Advanced

```jsx
// Production pattern: split state and dispatch contexts, guard hook, memoized values
import { createContext, useContext, useReducer, useEffect } from 'react'; // hooks used below
import { createRoot } from 'react-dom/client';                             // React 18/19 root

// Two contexts: state changes often, dispatch never changes → split them
const AuthStateContext = createContext(undefined);    // undefined = "no provider" marker
const AuthDispatchContext = createContext(undefined); // dispatch from useReducer is stable

// Pure reducer: all state changes go through here, easy to test
function authReducer(state, action) {
  switch (action.type) {                              // decide by action type
    case 'login':
      return { user: action.user };                  // store the logged-in user object
    case 'logout':
      return { user: null };                         // clear the user
    default:
      throw new Error(`Unknown auth action: ${action.type}`); // fail loudly on a typo
  }
}

// Provider component: owns the state and exposes it through two contexts
export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, { user: null }); // initial state: logged out
  return (
    <AuthDispatchContext.Provider value={dispatch}>   {/* stable: never re-renders dispatch readers */}
      <AuthStateContext.Provider value={state}>       {/* changes only when state changes */}
        {children}
      </AuthStateContext.Provider>
    </AuthDispatchContext.Provider>
  );
}

// Custom hooks with a guard: a clear error if someone forgets the Provider
export function useAuthState() {
  const ctx = useContext(AuthStateContext);          // read state context
  if (ctx === undefined) {                           // no provider above this component
    throw new Error('useAuthState must be used inside <AuthProvider>'); // clear message
  }
  return ctx;                                        // { user }
}

export function useAuthDispatch() {
  const dispatch = useContext(AuthDispatchContext);  // read dispatch context
  if (dispatch === undefined) {                      // same guard for the dispatch context
    throw new Error('useAuthDispatch must be used inside <AuthProvider>');
  }
  return dispatch;                                   // function used to send actions
}

// Consumers: Header re-renders on login; LoginButton does NOT (it only dispatches)
function Header() {
  const { user } = useAuthState();                   // subscribes to state context
  console.log('Header render:', user ? user.name : 'guest'); // logs each state change
  return <p>Hello {user ? user.name : 'guest'}</p>;  // greeting text
}

function LoginButton() {
  const dispatch = useAuthDispatch();                // subscribes to dispatch context only
  console.log('LoginButton render');                 // should log once, never on login
  return (
    <button onClick={() => dispatch({ type: 'login', user: { name: 'Priya' } })}>
      Login
    </button>
  );
}

// Demo helper: logs in once after mount using the dispatch context
function AutoLogin() {
  const dispatch = useAuthDispatch();                // get the dispatch function
  useEffect(() => {                                  // runs once after the first paint
    dispatch({ type: 'login', user: { name: 'Priya' } }); // simulate a successful login
  }, [dispatch]);                                    // dispatch is stable, so this runs once
  return null;                                       // renders nothing
}

createRoot(document.getElementById('root')).render(
  <AuthProvider>
    <Header />
    <LoginButton />
    <AutoLogin />
  </AuthProvider>
);
```

---

## 🟠 Real App Integration

Context needs client-side state, so in Next.js App Router the provider is a Client Component. The root layout (a Server Component) imports it and wraps `children`. Server Components cannot call `createContext` or `useState`.

```jsx
// app/providers.jsx
'use client';                                           // providers hold state → Client Component
import { AuthProvider } from '@/lib/auth';              // the AuthProvider from the advanced example

export default function Providers({ children }) {
  return <AuthProvider>{children}</AuthProvider>;       // every page below can use useAuthState()
}
```

```jsx
// app/layout.jsx (Server Component)
import Providers from './providers';                    // client provider imported into a server file

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>               {/* children stay Server Components */}
      </body>
    </html>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Putting everything in one giant context, so any change re-renders all consumers
✅ **Correct:** Split unrelated or frequently changing values into separate contexts (topic 61 advanced shows state vs dispatch)

```jsx
// Wrong: one context for user, theme, cart and notifications
const AppContext = createContext(null);
// Typing in the cart re-renders every component that reads only the theme
<AppContext.Provider value={{ user, theme, cart, notifications }}>

// Right: separate contexts, so each consumer subscribes only to what it reads
<ThemeContext.Provider value={theme}>
  <CartContext.Provider value={cart}>
    <App />
  </CartContext.Provider>
</ThemeContext.Provider>
```

❌ **Mistake 2:** Creating a new value object on every render without memoization
✅ **Correct:** Wrap the object in `useMemo` so the reference stays the same while the data is unchanged

```jsx
// Wrong: a new object every render → every consumer re-renders, even when nothing changed
function Provider({ children }) {
  const [user, setUser] = useState(null);
  return <UserContext.Provider value={{ user, setUser }}>{children}</UserContext.Provider>; // ❌
}

// Right: memoize the value object
function Provider({ children }) {
  const [user, setUser] = useState(null);
  const value = useMemo(() => ({ user, setUser }), [user]); // ✅ same object while user is same
  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
}
```

❌ **Mistake 3:** Forgetting that `useContext` silently uses the default value when there is no Provider
✅ **Correct:** Use `undefined` as the default and throw a clear error in a custom hook (see the advanced example)

---

## 🧠 Tricky Interview Question

```jsx
import { createContext, useContext, useEffect, useReducer, memo } from 'react';
import { createRoot } from 'react-dom/client';

const CountCtx = createContext({ n: 0 });        // default value, not used below (there is a Provider)

function Reader() {                               // consumes the context
  const { n } = useContext(CountCtx);
  console.log('Reader render, n =', n);
  return null;
}

const MemoWrapper = memo(function MemoWrapper() { // memo: skips re-render when props are equal
  console.log('MemoWrapper render');
  return <Reader />;                              // Reader is created inside MemoWrapper
});

function App() {
  const [, force] = useReducer(x => x + 1, 0);   // used to force App to re-render once
  useEffect(() => { force(); }, []);             // runs once after mount
  return (
    <CountCtx.Provider value={{ n: 1 }}>        {/* NEW object on every App render */}
      <MemoWrapper />                            {/* no props → memo compares {} with {} → equal */}
    </CountCtx.Provider>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```
**Answer:** The output is:
```
MemoWrapper render
Reader render, n = 1
Reader render, n = 1
```
On the second App render, `MemoWrapper` is skipped by `memo`, so its function does not run and `MemoWrapper render` is not printed again. However, the Provider's `value` is a new object (`{ n: 1 }` is recreated), so `Object.is` detects a change and React re-renders every consumer of the context, even one that sits inside a memoized component. `memo` controls props, not context subscriptions. The fix is to hoist the value to a stable reference (for example with `useMemo`), after which `Reader` logs only once.

---

## ⚫ Interview Questions + Answers

Q1: What does `createContext` return, and what is the default value for?
A1: It returns a Context object with `Provider` and `Consumer` properties. The default value is used only when a component reads the context with no Provider above it. It is not the value used when a Provider exists without a value prop (that gives `undefined`).

Q2: How do you read a context value in a function component?
A2: With `const value = useContext(MyContext)`. The component re-renders whenever the nearest provider's value changes.

Q3: Does Context replace Redux?
A3: Context is a delivery mechanism, not a state manager. It passes values, but there is no built-in selector, middleware or devtools. For frequently changing, large or complex state, a store library (Redux Toolkit, Zustand, Jotai) with selectors is usually better. Context is ideal for stable values such as theme, locale or the current user.

Q4: Why does a context value change re-render many components?
A4: React compares the provider's `value` with `Object.is`. When it changes, every component that called `useContext` for that context is re-rendered, even if it reads only one field. Memoizing the value and splitting contexts reduce this cost.

Q5: How do you use Context in Next.js App Router?
A5: `createContext` and `useState` need client-side JavaScript, so the provider must be a Client Component (`'use client'`). Create a providers file with `'use client'`, and import it into the Server Component `app/layout.jsx`. Server Components can render Client Components, so the provider wraps `children` as usual.

---

## 🔷 When to Use + When Not to Use
✅ **Use Context when:**
- A value is needed by many components at different depths (theme, locale, current user, auth)
- The value changes rarely
- You want to avoid props drilling through pass-through components

❌ **Avoid Context when:**
- The value changes many times per second (use a store with selectors)
- Only a child or two need the value (pass props, it is clearer)
- You use it to avoid good design, putting everything in one provider

---

## 📊 Visual Diagram

```
  <ThemeContext.Provider value={theme}>        ← provider (source of truth)
     │
     ├── <Layout>                              ← does NOT read theme, not re-rendered by value change
     │     │
     │     └── <Sidebar>                       ← does NOT read theme
     │           │
     │           └── <ThemeToggleButton />     ← useContext(ThemeContext) → gets "dark"
     │
     └── <Footer />                            ← useContext(ThemeContext) → also gets "dark"

  Value changes → only consumers (ThemeToggleButton, Footer) re-render
  Default value → used only when NO Provider is above the consumer
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context | Shared channel for values | Values share करने का channel |
| Provider | Component that supplies the value | Value देने वाला component |
| Consumer | Component that reads the value | Value पढ़ने वाला component |
| useContext | Hook to read the nearest provider value | नज़दीकी provider की value पढ़ने का hook |
| Default value | Fallback when no provider exists | Provider न होने पर fallback value |
| Splitting contexts | Separate contexts by update frequency | Update की आवृत्ति के हिसाब से contexts अलग करना |
| Value memoization | Keeping the provider value stable | Provider value को स्थिर रखना |
| Object.is | Equality check that decides re-render | Re-render तय करने वाली equality check |

---

## ⚡ 3-Line Summary
**English:**
1. Context lets one Provider supply a value to any descendant with `useContext`, with no props drilling.
2. Every consumer re-renders when the provider value changes, so memoize the value and split frequently changing data.
3. Context delivers values, it does not manage complex state; in Next.js the provider must be a Client Component.

**Hindi:**
1. Context एक Provider से किसी भी descendant को `useContext` से value देता है, बिना props drilling के।
2. Provider की value बदलने पर सभी consumers re-render होते हैं, इसलिए value को memoize करो और बार-बार बदलने वाला data अलग करो।
3. Context values पहुँचाता है, complex state नहीं संभालता; Next.js में provider Client Component होना चाहिए।

---

## ➡️ Next Topic
**62. Component Composition** — Components को एक-दूसरे में जोड़कर flexible UI कैसे बनाएँ (children, slots और compound components)। Context से data नीचे जाता है, composition से UI की structure को साफ़ तरीके से खड़ा किया जाता है।
