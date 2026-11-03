# 11. React Project Structure
# हिंदी में: React Project Structure — Folders और Files को सही तरीके से सजाना

---

## 🔵 Simple Definition (English)
**React project structure** is the way you organize folders and files (components, hooks, services, assets, tests) so a team can find, change and scale code easily. React itself does not force any structure, so the choice is yours. A good structure groups code by feature, not only by file type.

## 🔵 सरल परिभाषा (Hindi)
**React project structure** वह तरीका है जिससे आप folders और files (components, hooks, services, assets, tests) को सजाते हैं ताकि team code को आसानी से ढूँढ, बदल और बड़ा कर सके। React खुद कोई structure थोपता नहीं है, इसलिए चुनाव आपका है। अच्छा structure code को सिर्फ file type से नहीं, बल्कि feature से group करता है।

---

## 🔴 Problem it Solves

React is a library, not a framework, so it gives no rules about where files go. In a small app everything sits in `src/` and works. When the app grows to 300 components, a flat `components/` folder with 300 files becomes impossible to navigate, and unrelated features start importing each other's internals. A clear structure solves three problems: finding code fast, limiting what a change can break, and letting many developers work without merge conflicts.

```
// PROBLEM: flat structure, everything in one folder
src/
  components/
    Button.jsx  Cart.jsx  CartItem.jsx  Login.jsx  LoginForm.jsx
    Menu.jsx  MenuItem.jsx  Navbar.jsx  OrderList.jsx  ... (300 more)

// SOLUTION: group by feature, share only what is truly common
src/
  features/cart/   features/auth/   features/menu/
  components/ui/   (Button, Modal: used everywhere)
```

## 🔴 यह क्यों बना? (Hindi)
React एक library है, framework नहीं, इसलिए files कहाँ रखें इस पर कोई नियम नहीं देता। छोटे app में सब कुछ `src/` में चल जाता है। जब app में 300 components हो जाते हैं, तो एक ही `components/` folder में 300 files को navigate करना नामुमकिन हो जाता है, और अलग-अलग features एक-दूसरे के internals import करने लगते हैं। साफ structure तीन समस्याएँ हल करता है: code जल्दी मिलना, किसी बदलाव से कम चीज़ें टूटना, और कई developers का बिना merge conflict के काम करना।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Start with the tool's default (Vite: index.html, src/main.jsx, src/App.jsx)
Step 2 → Keep entry files at the root of src/ (main.jsx mounts <App />)
Step 3 → Put truly shared UI in components/ (Button, Modal, Spinner)
Step 4 → Put each business area in features/<name>/ with its own components, hooks, api
Step 5 → Put cross-feature helpers in hooks/, lib/ (utils), and services/ (API client)
Step 6 → Expose a feature only through its index.js (public API), so others never reach inside
Step 7 → Place tests next to the code (Cart.test.jsx beside Cart.jsx)

RULE OF THUMB: things that change together should live together
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Tool के default से शुरू करो (Vite: index.html, src/main.jsx, src/App.jsx)
Step 2 → Entry files को src/ की root में रखो (main.jsx में <App /> mount होता है)
Step 3 → सच में shared UI को components/ में रखो (Button, Modal, Spinner)
Step 4 → हर business area को features/<name>/ में रखो, उसके अपने components, hooks, api के साथ
Step 5 → Feature के बीच के helpers को hooks/, lib/ (utils) और services/ (API client) में रखो
Step 6 → Feature को सिर्फ उसकी index.js (public API) से expose करो, ताकि दूसरे अंदर तक न पहुँचें
Step 7 → Tests को code के पास रखो (Cart.test.jsx, Cart.jsx के बगल में)

नियम: जो चीज़ें साथ बदलती हैं, वे साथ रहनी चाहिए
```

---

## 🟡 Real World Example
**Swiggy-like food ordering app:** The team has features such as `restaurants`, `cart`, `checkout`, `auth` and `tracking`. The cart team works only inside `features/cart/` (CartPage, CartItem, `useCart` hook, `cartSlice`, `cartApi`). The `Button`, `Modal` and `Rating` components live in `components/ui/` because every feature uses them. When the checkout team needs the cart total, they import from `features/cart` (its index file), not from `features/cart/components/CartItem.jsx`. A change in cart internals therefore cannot break checkout.

## 🟡 Real Example Hindi mein
**Swiggy जैसा food ordering app:** Team के features हैं `restaurants`, `cart`, `checkout`, `auth` और `tracking`। Cart team सिर्फ `features/cart/` में काम करती है (CartPage, CartItem, `useCart` hook, `cartSlice`, `cartApi`)। `Button`, `Modal` और `Rating` components `components/ui/` में हैं क्योंकि हर feature इन्हें इस्तेमाल करता है। Checkout team को cart total चाहिए तो वे `features/cart` (उसकी index file) से import करती है, `features/cart/components/CartItem.jsx` से नहीं। इसलिए cart के internals बदलने से checkout नहीं टूटता।

---

## 💻 Code Example — Basic

```jsx
// src/main.jsx — the entry file Vite loads from index.html
import { StrictMode } from 'react';               // dev-only checks wrapper
import { createRoot } from 'react-dom/client';    // React 18/19 root API
import App from './App.jsx';                      // the root component
import './index.css';                             // global styles, imported once here

createRoot(document.getElementById('root')).render( // mount into <div id="root"> in index.html
  <StrictMode>                                      {/* highlights unsafe patterns in development */}
    <App />                                         {/* whole app starts here */}
  </StrictMode>
);
```

```jsx
// src/App.jsx — the top-level component that wires pages together
import Navbar from './components/layout/Navbar.jsx';   // shared layout piece
import RestaurantList from './features/restaurants';   // feature imported via its index.js

export default function App() {                        // root component, no props needed
  return (
    <>
      <Navbar />                                       {/* always visible header */}
      <main>
        <RestaurantList />                             {/* the feature renders its own UI */}
      </main>
    </>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// Feature-based structure with a public API (barrel file). Folder tree shown as comments:
//
// src/
//   main.jsx
//   App.jsx
//   components/ui/Button.jsx          <- generic, no business logic
//   lib/formatPrice.js                <- pure helper
//   services/apiClient.js             <- one fetch wrapper for the whole app
//   features/cart/
//     index.js                        <- PUBLIC API of the feature
//     CartPage.jsx
//     CartItem.jsx
//     useCart.js
//     cartApi.js
//     CartPage.test.jsx

// ---- src/services/apiClient.js ----
const BASE_URL = import.meta.env.VITE_API_URL;          // Vite env var (must start with VITE_)

export async function apiClient(path, options = {}) {   // single place for fetch settings
  const res = await fetch(`${BASE_URL}${path}`, {       // build the full URL
    headers: { 'Content-Type': 'application/json' },    // default header
    ...options,                                         // allow caller overrides
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`); // fetch does not throw on 404/500
  return res.json();                                    // parse the JSON body
}
```

```jsx
// ---- src/features/cart/useCart.js ----
import { useState, useCallback } from 'react';           // state + stable function identity
import { formatPrice } from '../../lib/formatPrice.js';  // shared pure helper

export function useCart() {                              // feature logic lives in a hook
  const [items, setItems] = useState([]);                // [{ id, name, price, qty }]

  const add = useCallback((item) => {                    // add or increase quantity
    setItems((prev) => {                                 // updater form avoids stale state
      const found = prev.find((i) => i.id === item.id);  // is it already in the cart?
      if (found) return prev.map((i) => (i.id === item.id ? { ...i, qty: i.qty + 1 } : i));
      return [...prev, { ...item, qty: 1 }];             // otherwise add a new row
    });
  }, []);

  const total = items.reduce((sum, i) => sum + i.price * i.qty, 0); // derived, not stored
  return { items, add, total, totalLabel: formatPrice(total) };     // what the UI needs
}
```

```jsx
// ---- src/features/cart/index.js ---- (the only file other features may import)
export { default as CartPage } from './CartPage.jsx';   // re-export the page component
export { useCart } from './useCart.js';                 // re-export the hook
// CartItem.jsx and cartApi.js are intentionally NOT exported: they are private internals
```

---

## 🟠 Real App Integration

Next.js (App Router) adds a convention on top: the `app/` folder is the router, and special files (`page.jsx`, `layout.jsx`, `loading.jsx`, `error.jsx`) are routes. The usual advice is to keep `app/` thin and put real code in `src/features` or `components`. You can also colocate private folders using an underscore prefix, which opts them out of routing.

```jsx
// Next.js 14/15 App Router layout (a typical structure):
//
// src/
//   app/
//     layout.jsx                 <- root layout (html, body)
//     page.jsx                   <- route "/"
//     cart/page.jsx              <- route "/cart"
//     _components/               <- private folder, NOT a route
//   features/cart/               <- same feature folders as in plain React
//   components/ui/
//   lib/

// src/app/cart/page.jsx — a thin route that delegates to the feature
import { CartPage } from '@/features/cart';   // "@/" alias to src/ is set in jsconfig.json

export default function Page() {              // Server Component by default
  return <CartPage />;                        // CartPage itself adds 'use client' if it needs state
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Grouping only by file type forever (`components/`, `hooks/`, `utils/` with hundreds of files)
✅ **Correct:** Group by feature, and keep only shared code in the global folders

```jsx
// Wrong: to change "cart" you edit files in 5 distant folders
// src/components/CartItem.jsx
// src/hooks/useCart.js
// src/api/cartApi.js
// src/store/cartSlice.js
// src/tests/cart.test.jsx

// Right: one folder holds everything that changes together
// src/features/cart/CartItem.jsx
// src/features/cart/useCart.js
// src/features/cart/cartApi.js
// src/features/cart/cartSlice.js
// src/features/cart/cart.test.jsx
```

❌ **Mistake 2:** Deep relative imports like `../../../../components/Button`
✅ **Correct:** Configure a path alias so imports stay short and survive file moves

```jsx
// Wrong: breaks when you move the file one level
import ButtonOld from '../../../../components/ui/Button.jsx';

// Right: alias set in vite.config.js (resolve.alias) or jsconfig.json (paths)
import Button from '@/components/ui/Button.jsx';
```

❌ **Mistake 3:** Importing another feature's internal files directly (creates hidden coupling)
✅ **Correct:** Import only from the feature's `index.js`

```jsx
// Wrong: checkout reaches inside cart
import CartItem from '../cart/CartItem.jsx';

// Right: use the public API
import { useCart } from '@/features/cart';
```

---

## 🧠 Tricky Interview Question

```jsx
// src/features/cart/index.js
export { useCart } from './useCart.js';

// src/features/cart/useCart.js
import { useCheckoutSummary } from '../checkout';   // cart imports checkout...

// src/features/checkout/index.js
export { useCheckoutSummary } from './useCheckoutSummary.js';

// src/features/checkout/useCheckoutSummary.js
import { useCart } from '../cart';                  // ...and checkout imports cart
```
Question: What goes wrong here?

**Answer:** This is a **circular dependency**. When the bundler loads `cart/index.js`, it needs `useCart.js`, which needs `checkout/index.js`, which needs `useCheckoutSummary.js`, which needs `cart/index.js` again, which is still loading. One of the imports can be `undefined` at the moment it is evaluated, which causes hard-to-debug errors such as "useCart is not a function" (it often works in one entry order and fails in another). Fix it by moving the shared piece (for example, cart totals) into a third module that both features import, or by making one direction of the dependency go through props or a callback. A lint rule such as `import/no-cycle` catches this early.

---

## ⚫ Interview Questions + Answers

Q1: Does React enforce a folder structure?
A1: No. React is only a UI library, so any structure works. Tools such as Next.js enforce specific files (`app/page.jsx`), but inside those rules the organization is still your choice.

Q2: What is the difference between grouping by type and grouping by feature?
A2: By type means folders like `components/`, `hooks/`, `services/`, which is simple for small apps. By feature means folders like `cart/`, `auth/`, each containing its own components, hooks and API code. Feature grouping scales better because a change touches one folder, and teams can own features.

Q3: What is a barrel file (`index.js`) and why use it?
A3: A file that re-exports selected items from a folder. It defines the public API of a feature, so other code imports from `features/cart` and cannot depend on private files. Downside: in large apps barrel files can hurt tree shaking and build speed, so keep them small.

Q4: Where should shared components go versus feature components?
A4: A component used by only one feature stays inside that feature. A component used by two or more features, and containing no business logic (Button, Modal), moves to `components/ui`. Do not move code to shared too early.

Q5: What are the main files in a Vite React project?
A5: `index.html` (has `<div id="root">` and loads `/src/main.jsx`), `src/main.jsx` (calls `createRoot`), `src/App.jsx` (root component), `vite.config.js` (build config) and `package.json` (scripts and dependencies). Note that `index.html` sits at the project root, not in `public/`.

---

## 🔷 When to Use + When Not to Use
✅ **Use feature-based structure when:**
- The app has several business areas and more than a few developers
- You expect the app to grow beyond about 50 components
- Different teams need ownership of different areas

❌ **Avoid over-structuring when:**
- It is a small demo or a learning project (a flat `src/` is fine)
- You create folders "for later" that stay empty
- You split every component into its own folder with five files for no reason

---

## 📊 Visual Diagram

```
  my-app/
  ├── index.html              ← Vite entry, loads /src/main.jsx
  ├── package.json            ← scripts + dependencies
  ├── vite.config.js          ← build config + path aliases
  ├── public/                 ← static files served as-is (favicon, robots.txt)
  └── src/
      ├── main.jsx            ← createRoot(...).render(<App />)
      ├── App.jsx             ← top-level component / routes
      ├── components/ui/      ← shared dumb UI   (Button, Modal)
      ├── lib/                ← pure helpers     (formatPrice)
      ├── services/           ← apiClient
      └── features/
          ├── cart/    ── index.js ── (public API)
          ├── auth/    ── index.js
          └── menu/    ── index.js

  features may import: components/ui, lib, services   ✅
  features import each other only via index.js        ⚠️
  components/ui must NOT import features              ❌
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Entry file | File where the app starts (`main.jsx`) | वह file जहाँ से app शुरू होता है |
| Feature folder | All code of one business area together | एक business area का पूरा code एक जगह |
| Barrel file | `index.js` that re-exports items | `index.js` जो items को re-export करती है |
| Public API | The only exports others may use | केवल वे exports जो दूसरे इस्तेमाल कर सकें |
| Path alias | Short import prefix like `@/` | छोटा import prefix जैसे `@/` |
| Colocation | Keeping related files side by side | जुड़ी files को पास-पास रखना |
| Circular dependency | A imports B and B imports A | A, B को और B, A को import करे |
| `public/` folder | Static files copied without processing | बिना process हुए copy होने वाली static files |

---

## ⚡ 3-Line Summary
**English:**
1. React has no required structure; Vite gives `index.html`, `main.jsx` and `App.jsx` and you organize the rest.
2. Group code by feature, keep only truly shared code global, and expose each feature through an `index.js`.
3. Use path aliases, colocate tests, and avoid circular imports and premature folder splitting.

**Hindi:**
1. React में कोई तय structure नहीं है; Vite `index.html`, `main.jsx` और `App.jsx` देता है, बाकी आप सजाते हैं।
2. Code को feature से group करो, सिर्फ सच में shared code को global रखो, और हर feature को `index.js` से expose करो।
3. Path aliases इस्तेमाल करो, tests पास में रखो, और circular imports व ज़रूरत से पहले folders बाँटने से बचो।

---

## ➡️ Next Topic
**12. Components — Basics** — Files की जगह तय हो गई, अब देखो कि component असल में क्या है और उसे कैसे लिखते हैं। इसके बाद functional और class components का फर्क (13) आएगा.
