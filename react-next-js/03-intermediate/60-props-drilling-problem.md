# 60. Props Drilling Problem
# हिंदी में: Props Drilling Problem — Data को कई Levels नीचे भेजने की समस्या

---

## 🔵 Simple Definition (English)
**Props drilling** means passing data from a top component down to a deeply nested child through several middle components, even though those middle components never use the data themselves. The data travels down through props, level by level, like a parcel passed hand to hand.

## 🔵 सरल परिभाषा (Hindi)
**Props drilling** का मतलब है data को ऊपर वाले component से गहराई में बैठे child तक कई बीच के components से होकर props के ज़रिए भेजना, जबकि बीच के components उस data को खुद कभी इस्तेमाल नहीं करते। Data एक-एक level करके नीचे जाता है, जैसे कोई parcel हाथ-हाथ से आगे बढ़ता है।

---

## 🔴 Problem it Solves

React data flows one way: from parent to child, through props. This is simple and predictable, but it has a cost. When a value such as the logged-in user or the theme is needed by a component five levels down, every component in between must accept it and pass it on. These middle components become coupled to data they do not care about. Renaming a prop means editing every level, and adding a new value means touching a long chain of files.

```jsx
// PROBLEM: App → Layout → Sidebar → Profile
// Layout and Sidebar never read "user" or "theme", they only forward them
function App()     { return <Layout user={user} theme={theme} />; }
function Layout({ user, theme }) { return <Sidebar user={user} theme={theme} />; } // ❌ just forwarding
function Sidebar({ user, theme }) { return <Profile user={user} theme={theme} />; } // ❌ just forwarding
function Profile({ user, theme }) { return <p className={theme}>{user.name}</p>; } // ✅ the only real user
```

## 🔴 यह क्यों बना? (Hindi)
React में data एक ही दिशा में बहता है: parent से child की तरफ, props के ज़रिए। यह simple और predictable है, पर इसकी कीमत है। जब logged-in user या theme किसी component को पाँच levels नीचे चाहिए, तो बीच के हर component को वह prop लेना और आगे भेजना पड़ता है। ये बीच के components ऐसे data से जुड़ जाते हैं जिसकी उन्हें परवाह नहीं। Prop का नाम बदलो तो हर level एडिट करना पड़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Top component (App) owns the data: user, theme
Step 2 → It passes them to its child as props: <Layout user theme />
Step 3 → Layout does not use them, but must accept and forward: <Sidebar user theme />
Step 4 → Sidebar does the same: <Profile user theme />
Step 5 → Only the deepest component (Profile) finally reads the values
Step 6 → Every extra level adds one more place to change when the data shape changes

KEY: the middle components are "pass-through" — they add noise, not behavior
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → ऊपर वाला component (App) data रखता है: user, theme
Step 2 → वह child को props में देता है: <Layout user theme />
Step 3 → Layout इन्हें इस्तेमाल नहीं करता, पर लेकर आगे भेजना पड़ता है: <Sidebar user theme />
Step 4 → Sidebar भी यही करता है: <Profile user theme />
Step 5 → आखिर में सिर्फ सबसे गहरा component (Profile) values पढ़ता है
Step 6 → हर अतिरिक्त level एक और जगह है जहाँ data का shape बदलने पर एडिट करना होगा

KEY: बीच के components "pass-through" होते हैं — वे behavior नहीं, सिर्फ noise जोड़ते हैं
```

---

## 🟡 Real World Example
**Flipkart product page:** The `currentUser` object is loaded at the top of the app. The `ProductPage` renders `ProductInfo`, which renders `PriceBox`, which renders `AddToCartButton`. Only `AddToCartButton` needs the user ID. Without a better approach, `ProductPage`, `ProductInfo` and `PriceBox` all receive and forward `currentUser`. Adding a "logged-in region" field means editing four files, and two of them do nothing with it.

## 🟡 Real Example Hindi mein
**Flipkart product page:** `currentUser` object app के ऊपर load होता है। `ProductPage`, `ProductInfo` को रेंडर करता है, जो `PriceBox` को, जो `AddToCartButton` को रेंडर करता है। सिर्फ `AddToCartButton` को user ID चाहिए। बेहतर तरीके के बिना `ProductPage`, `ProductInfo` और `PriceBox` तीनों `currentUser` लेते और आगे भेजते हैं। Naya "region" field जोड़ने पर चार files बदलनी पड़ती हैं, जिनमें से दो उसका कुछ नहीं करतीं।

---

## 💻 Code Example — Basic

```jsx
// Props drilling: the user and theme travel through two middle components that ignore them
import { createRoot } from 'react-dom/client';   // React 18/19 root API

function App() {                                 // top of the tree: owns the data
  const user = { name: 'Aditya', city: 'Delhi' }; // data that the deepest child needs
  const theme = 'dark';                          // second value that is drilled down
  return <Layout user={user} theme={theme} />;   // pass both down to Layout
}

function Layout({ user, theme }) {               // middle level 1: does NOT use user or theme itself
  return <Sidebar user={user} theme={theme} />;  // just forwards them to Sidebar
}

function Sidebar({ user, theme }) {              // middle level 2: also just forwards
  return <Profile user={user} theme={theme} />;  // forwards to Profile
}

function Profile({ user, theme }) {              // the only component that really uses the data
  return <p className={theme}>{user.name} from {user.city}</p>; // rendered output
}

createRoot(document.getElementById('root')).render(<App />); // start the app
// Output in the DOM: <p class="dark">Aditya from Delhi</p>
```

## 💻 Code Example — Advanced

```jsx
// Drilling a callback through memo'd components: an inline function silently breaks React.memo
import { useState, useEffect, memo } from 'react';  // hooks + memo
import { createRoot } from 'react-dom/client';      // React 18/19 root API

// Module-level constant: created ONCE, so its reference never changes
const PRODUCTS = [
  { id: 1, name: 'Biryani' },                       // product 1
  { id: 2, name: 'Dosa' },                          // product 2
];

// Leaf component: wrapped in memo, should skip work when its props are equal
const ProductCard = memo(function ProductCard({ product, theme, onAddToCart }) {
  console.log('ProductCard render:', product.name); // logs ONLY when this card really re-renders
  return (
    <div className={theme}>                         {/* theme is a string → compares equal */}
      {product.name}{' '}
      <button onClick={() => onAddToCart(product.id)}>Add</button> {/* calls the drilled callback */}
    </div>
  );
});

// Middle level: forwards the callback down to every card
function ProductList({ products, theme, onAddToCart }) {
  return products.map(p => (                        // one card per product
    <ProductCard
      key={p.id}                                    // stable key for list identity
      product={p}                                   // same object reference from PRODUCTS
      theme={theme}                                 // string → always equal
      onAddToCart={onAddToCart}                     // callback identity decides memo behavior!
    />
  ));
}

// BAD version: a NEW arrow function is created on every render
function BadShop() {
  const [, setCart] = useState([]);                 // cart state (unused for display here)
  const [, setTick] = useState(0);                  // an unrelated state that changes once
  useEffect(() => { setTick(1); }, []);             // forces ONE extra render of BadShop
  // ❌ new function object each render → memo sees "changed" props → cards re-render
  return <ProductList products={PRODUCTS} theme="dark" onAddToCart={id => setCart(c => [...c, id])} />;
}

// GOOD version: setCart is stable and useCallback keeps the same function identity
import { useCallback } from 'react';               // needed for the stable callback
function GoodShop() {
  const [, setCart] = useState([]);                 // setState functions are stable by React rules
  const [, setTick] = useState(0);                  // same unrelated state
  useEffect(() => { setTick(1); }, []);             // same extra render
  // ✅ useCallback returns the SAME function when deps are unchanged (deps = [] here)
  const handleAdd = useCallback(id => setCart(c => [...c, id]), []);
  return <ProductList products={PRODUCTS} theme="dark" onAddToCart={handleAdd} />;
}

// Two separate roots so both versions run on the same page
const bad = createRoot(document.getElementById('root'));    // root 1
bad.render(<BadShop />);                                    // logs 4 lines: 2 cards × 2 renders
const good = createRoot(document.createElement('div'));    // root 2 (detached div is fine for the demo)
good.render(<GoodShop />);                                  // logs 2 lines: cards skip the second render
// The extra render happens because of setTick(1). In BadShop the new callback
// breaks memo; in GoodShop memo skips the cards on that second render.
```

---

## 🟠 Real App Integration

In a Next.js App Router app, the Server Component layout can read the session and pass only what the client header needs. One prop level is fine. If many client components need the user, move the value into a provider (topic 61) instead of passing it through every layout.

```jsx
// app/layout.jsx (Server Component: runs on the server, no hooks)
import Header from './Header';                          // Client Component ('use client' inside it)
import { getCurrentUser } from '@/lib/session';         // your server-side session helper

export default async function RootLayout({ children }) {
  const user = await getCurrentUser();                  // read the session on the server
  return (
    <html lang="en">
      <body>
        <Header userName={user?.name ?? 'Guest'} />     {/* pass ONLY the string Header uses */}
        <main>{children}</main>                         {/* pages render here */}
      </body>
    </html>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Passing a whole big object down when a child needs only one field
✅ **Correct:** Pass only what the child needs, so middle components stay independent

```jsx
// Wrong: the whole store goes through every level just to read userName
<Layout store={store} />          // ❌ every component now depends on the entire store shape

// Right: pass the one value that is actually used
<Layout userName={store.user.name} />   // ✅ middle levels only carry a plain string
```

❌ **Mistake 2:** Adding a prop to every level "just in case"
✅ **Correct:** If more than 2-3 levels only forward a value, move it to Context (topic 61) or use composition (topic 62)

```jsx
// Wrong: each level grows a new pass-through prop
function Layout({ user, theme, locale, cartCount, onLogout }) { /* ... forwarded ... */ } // ❌

// Right: provide the shared values through Context once, and read them where needed
// <UserProvider><Layout /></UserProvider>  → inside Profile: const user = useContext(UserContext);
```

---

## 🧠 Tricky Interview Question

```jsx
import { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';

function Leaf({ theme }) {                       // Leaf only needs "theme"
  console.log('Leaf render', theme);
  return <p>{theme}</p>;
}

function Middle(props) {                         // Middle does NOT use any prop, it just spreads them
  console.log('Middle render');
  return <Leaf {...props} />;                    // forwards everything
}

function App() {
  const [, setCount] = useState(0);              // state that Middle and Leaf never read
  useEffect(() => { setCount(1); }, []);         // parent re-renders once, after mount
  return <Middle theme="dark" />;                // same props every time
}

createRoot(document.getElementById('root')).render(<App />);
```
**Answer:** The output is:
```
Middle render
Leaf render dark
Middle render
Leaf render dark
```
`Leaf` receives the same `theme="dark"` both times, yet it still re-renders. Only `App` changed state, but `Middle` is not memoized, so React re-renders it and creates a new `<Leaf>` element. The new element is a new object, so `Leaf` renders again. Props drilling makes unrelated components re-run; wrapping `Middle` in `React.memo` (or moving the state lower) would stop the second render.

---

## ⚫ Interview Questions + Answers

Q1: What is props drilling?
A1: Passing data from a top component to a deeply nested child through intermediate components that do not use the data. Each middle component must accept the prop and forward it.

Q2: Why is props drilling a problem?
A2: It couples middle components to data they do not need, makes refactoring harder (renaming a prop changes many files), adds visual noise, and can cause unnecessary re-renders when pass-through components are not memoized.

Q3: Is props drilling always bad?
A3: No. For two or three levels, explicit props are the clearest and most testable way to share data. React's one-way data flow is a feature. It becomes a problem only when many levels just forward the same value.

Q4: What are the common solutions?
A4: Component composition (passing components or `children` directly, topic 62), React Context (topic 61), state libraries such as Redux Toolkit, Zustand or Jotai for app-wide state, and moving state closer to where it is used.

Q5: How does props drilling interact with React.memo?
A5: A memoized child skips re-rendering only when its props are equal. If a middle component passes an inline object or arrow function, the reference changes on every parent render and memo stops working. Use `useCallback` and `useMemo` to keep those references stable.

---

## 🔷 When to Use + When Not to Use
✅ **Accept props drilling when:**
- The data is needed by a child one or two levels down
- You want explicit, easy-to-test data flow
- The intermediate components are reusable and should stay generic

❌ **Avoid props drilling when:**
- Three or more levels only forward the same value
- The same value (user, theme, locale, cart) is needed in many unrelated places
- Each change to shared data requires editing a long chain of files

---

## 📊 Visual Diagram

```
  PROPS DRILLING (data passes through every level)

  ┌─────────────┐  user, theme   ┌─────────────┐  user, theme   ┌─────────────┐  user, theme   ┌─────────────┐
  │    App      │ ─────────────▶ │   Layout    │ ─────────────▶ │   Sidebar   │ ─────────────▶ │   Profile   │
  │ owns data   │                │ (forwards)  │                │ (forwards)  │                │ (uses data) │
  └─────────────┘                └─────────────┘                └─────────────┘                └─────────────┘

  Layout and Sidebar: receive props they never read → extra coupling and noise
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Props drilling | Passing props through many levels | कई levels से props ले जाना |
| Pass-through component | Component that only forwards props | सिर्फ props आगे भेजने वाला component |
| One-way data flow | Data moves from parent to child | Data parent से child की तरफ बहता है |
| Coupling | Dependence between components | Components के बीच निर्भरता |
| Context | React feature to share values without drilling | Bina drilling values share करने का React feature |
| Reference equality | Same object in memory | Memory में एक ही object |
| Memoization | Skipping work when inputs are equal | Inputs same हों तो काम छोड़ना |

---

## ⚡ 3-Line Summary
**English:**
1. Props drilling passes data through middle components that never use it.
2. It couples components, adds noise, and can break memoization when callbacks are recreated.
3. Fix it with composition for layout, Context for shared values, or a state library for app-wide state.

**Hindi:**
1. Props drilling में data उन बीच के components से गुज़रता है जो उसे कभी इस्तेमाल नहीं करते।
2. यह components को जोड़ता है, noise बढ़ाता है, और callbacks दोबारा बनने पर memoization तोड़ सकता है।
3. Layout के लिए composition, shared values के लिए Context, और app-wide state के लिए state library से हल करो।

---

## ➡️ Next Topic
**61. Context API Solution** — `createContext`, `Provider` और `useContext` से data को बिना drilling के किसी भी गहराई तक कैसे पहुँचाया जाए। यह इसी problem का सीधा solution है।
