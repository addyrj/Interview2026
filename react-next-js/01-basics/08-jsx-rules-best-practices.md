# 8. JSX Rules + Best Practices
# हिंदी में: JSX के नियम और अच्छी आदतें

---

## 🔵 Simple Definition (English)
**JSX** is a syntax extension that lets you write HTML-like markup inside JavaScript. It is not HTML: a compiler (Babel, SWC, esbuild) turns each tag into a function call that returns a React element. JSX has strict rules, such as one root element, `className`, and closing every tag.

## 🔵 सरल परिभाषा (Hindi)
**JSX** एक syntax extension है जिससे आप JavaScript के अंदर HTML जैसा markup लिख सकते हैं। यह HTML नहीं है: एक compiler (Babel, SWC, esbuild) हर tag को ऐसे function call में बदलता है जो React element लौटाता है। JSX के सख़्त नियम हैं, जैसे एक root element, `className`, और हर tag को बंद करना।

---

## 🔴 Problem it Solves

Writing UI with `React.createElement` calls is hard to read. Splitting markup into separate template files separates things that change together (logic and UI). JSX keeps them in one place. But because JSX is JavaScript underneath, it has rules that differ from HTML. Developers who ignore them get confusing errors or bugs (for example `class` instead of `className`, or `0` printed on screen).

```jsx
// Without JSX: hard to read
createElement('div', { className: 'card' }, createElement('h2', null, 'Biryani'), createElement('p', null, '₹250'));

// With JSX: looks like the UI
<div className="card"><h2>Biryani</h2><p>₹250</p></div>
```

## 🔴 यह क्यों बना? (Hindi)
`React.createElement` calls से UI लिखना पढ़ने में कठिन है। Markup को अलग template files में रखने से वे चीज़ें अलग हो जाती हैं जो साथ बदलती हैं (logic और UI)। JSX दोनों को एक जगह रखता है। लेकिन JSX अंदर से JavaScript है, इसलिए इसके नियम HTML से अलग हैं। नियम न मानने पर confusing errors या bugs आते हैं (जैसे `class` की जगह `className`, या screen पर `0` छप जाना)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write JSX: <button className="btn" onClick={add}>Add</button>
Step 2 → Compiler (Babel/SWC/esbuild) transforms it at build time
Step 3 → New JSX transform (React 17+) → jsx('button', { className:'btn', onClick: add, children:'Add' })
         (no need to `import React` anymore)
Step 4 → The call returns a plain object (React element), not a DOM node
Step 5 → React reads the object and updates the DOM

THE CORE RULES:
  1. Return ONE root (use <> </> Fragment if you need no wrapper)
  2. Close every tag:   <img />   <input />   <br />
  3. camelCase attributes: className, htmlFor, onClick, tabIndex
  4. {} holds a JS EXPRESSION (not statements like if/for)
  5. Style is an object: style={{ color: 'red' }}
  6. Components start with a Capital letter; lowercase = HTML tag
  7. Lists need a stable `key`
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप JSX लिखते हैं: <button className="btn" onClick={add}>Add</button>
Step 2 → Compiler (Babel/SWC/esbuild) build time पर इसे transform करता है
Step 3 → नया JSX transform (React 17+) → jsx('button', { className:'btn', onClick: add, children:'Add' })
         (अब `import React` ज़रूरी नहीं)
Step 4 → यह call plain object (React element) लौटाता है, DOM node नहीं
Step 5 → React उस object को पढ़कर DOM update करता है

मुख्य नियम:
  1. एक ही ROOT लौटाओ (wrapper न चाहिए तो <> </> Fragment)
  2. हर tag बंद करो:   <img />   <input />   <br />
  3. camelCase attributes: className, htmlFor, onClick, tabIndex
  4. {} में JS EXPRESSION आता है (if/for जैसे statements नहीं)
  5. Style एक object है: style={{ color: 'red' }}
  6. Components बड़े अक्षर से शुरू होते हैं; छोटे अक्षर = HTML tag
  7. Lists के लिए stable `key` चाहिए
```

---

## 🟡 Real World Example
**Swiggy menu item row:** Each dish shows a veg/non-veg icon, name, price, and an "ADD" button, and shows "Out of stock" if unavailable. In JSX you use `className` for styles, `{price}` for the number, a ternary for stock, `.map` with `key={dish.id}` for the list, and a Fragment to return the icon and text without an extra `div`. A wrong rule (for example `class=`) gives a warning, and `{count && <Badge />}` with `count = 0` prints a stray `0` on screen.

## 🟡 Real Example Hindi mein
**Swiggy menu item row:** हर dish में veg/non-veg icon, नाम, price और "ADD" बटन होता है, और अनुपलब्ध होने पर "Out of stock" दिखता है। JSX में styles के लिए `className`, number के लिए `{price}`, stock के लिए ternary, list के लिए `key={dish.id}` वाला `.map`, और अतिरिक्त `div` के बिना icon व text लौटाने के लिए Fragment इस्तेमाल होता है। कोई नियम गलत हो (जैसे `class=`) तो warning आती है, और `count = 0` के साथ `{count && <Badge />}` screen पर अनचाहा `0` छाप देता है।

---

## 💻 Code Example — Basic

```jsx
// JSX rules in one small component
import { createRoot } from 'react-dom/client';           // React 18/19 root API

function DishRow() {
  const dish = { id: 1, name: 'Paneer Tikka', price: 249, veg: true, stock: 5 }; // sample data
  const styleBox = { padding: 12, border: '1px solid #ddd' };  // RULE 5: style is an object

  return (
    // RULE 1: one root. A Fragment adds no extra DOM node
    <>
      <div className="dish" style={styleBox}>            {/* RULE 3: className, not class */}
        <span>{dish.veg ? '🟢' : '🔴'}</span>            {/* RULE 4: expression (ternary) inside {} */}
        <h3>{dish.name}</h3>                             {/* a variable inside {} */}
        <p>₹{dish.price}</p>                             {/* text and expression mixed */}
        <img src="/paneer.jpg" alt={dish.name} />        {/* RULE 2: self-closing tag with alt */}
        <label htmlFor="qty">Qty</label>                 {/* htmlFor, not for */}
        <input id="qty" type="number" defaultValue={1} />{/* self-closed input */}
        {dish.stock > 0 ? <button>ADD</button> : <span>Out of stock</span>} {/* conditional UI */}
      </div>
    </>
  );
}

createRoot(document.getElementById('root')).render(<DishRow />); // RULE 6: Capital = component
```

## 💻 Code Example — Advanced

A production-style menu list that applies the best practices: stable keys, safe conditional rendering (no stray `0`), small components, no inline object churn, spreading props carefully, and accessibility.

```jsx
// Advanced: best-practice JSX for a Swiggy-like menu
import { useState, memo } from 'react';                    // state + memo for pure rows
import { createRoot } from 'react-dom/client';             // React 18/19 root API

const MENU = [                                              // sample data with stable ids
  { id: 'd1', name: 'Masala Dosa', price: 120, veg: true, stock: 10 },
  { id: 'd2', name: 'Chicken Roll', price: 180, veg: false, stock: 0 },
  { id: 'd3', name: 'Idli Sambar', price: 80, veg: true, stock: 3 },
];

const rowStyle = { display: 'flex', gap: 12, padding: 8 }; // BEST: style object defined once, outside render

// Small, focused, memoized component: re-renders only when its props change
const DishRow = memo(function DishRow({ dish, onAdd }) {
  const { id, name, price, veg, stock } = dish;             // destructure for readable JSX
  return (
    <li style={rowStyle}>
      <span aria-label={veg ? 'Vegetarian' : 'Non-vegetarian'}>{veg ? '🟢' : '🔴'}</span> {/* a11y label */}
      <span>{name}</span>
      <span>₹{price}</span>
      {stock > 0 && stock <= 3 && <em>Only {stock} left</em>}  {/* BEST: compare to a boolean, never `stock && ...` */}
      <button
        type="button"                                       // avoid accidental form submit
        disabled={stock === 0}                              // boolean attribute
        onClick={() => onAdd(id)}                           // pass id; arrow is fine for simple cases
      >
        {stock === 0 ? 'Sold out' : 'ADD'}
      </button>
    </li>
  );
});

function Menu() {
  const [cart, setCart] = useState({});                     // { dishId: quantity }

  function handleAdd(id) {
    setCart((c) => ({ ...c, [id]: (c[id] ?? 0) + 1 }));     // immutable update with functional form
  }

  const total = Object.entries(cart).reduce((sum, [id, qty]) => {
    const dish = MENU.find((d) => d.id === id);             // look up price for each cart line
    return sum + dish.price * qty;                          // running total
  }, 0);

  return (
    <section>
      <h2>Menu</h2>
      <ul>
        {MENU.map((dish) => (                               // BEST: stable id as key, never index for dynamic lists
          <DishRow key={dish.id} dish={dish} onAdd={handleAdd} />
        ))}
      </ul>
      <p>Cart total: ₹{total}</p>
    </section>
  );
}

createRoot(document.getElementById('root')).render(<Menu />);
```

**Re-render behavior:** clicking ADD updates `cart`, so `Menu` re-renders. `handleAdd` is a new function on every render, so `memo` cannot skip the rows as written; wrap it in `useCallback` (it only uses the functional `setCart`, so an empty dependency array works) to make `memo` effective. **Performance impact:** inline arrow functions in JSX are fine for small lists, but for hundreds of memoized rows use `useCallback` so props stay stable.

---

## 🟠 Next.js Connection
Next.js compiles JSX with **SWC** by default (fast, Rust-based), so you do not configure Babel. In the App Router, JSX in a file without `'use client'` is a Server Component, so you cannot attach `onClick` there. Interactive parts move to small Client Components. `next/image` and `next/link` replace raw `<img>` and `<a>` for optimization.

```jsx
// app/menu/page.jsx (Server Component: JSX without event handlers)
import Image from 'next/image';                              // optimized image component
import Link from 'next/link';                                // client-side navigation
import AddButton from './AddButton';                         // Client Component for onClick

export default function MenuPage() {
  return (
    <main>
      <h1>Menu</h1>                                          {/* plain JSX on the server */}
      <Image src="/dosa.jpg" alt="Masala Dosa" width={200} height={150} /> {/* auto-optimized */}
      <Link href="/cart">Go to cart</Link>                   {/* prefetches the route */}
      <AddButton dishId="d1" />                              {/* interactive island */}
    </main>
  );
}
```

```jsx
// app/menu/AddButton.jsx
'use client';                                                // enables onClick and state
export default function AddButton({ dishId }) {
  return <button onClick={() => alert(`Added ${dishId}`)}>ADD</button>; // handler only works on the client
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `&&` with a number that can be `0`
✅ **Correct:** Convert to a boolean or use a ternary

```jsx
// Wrong: when items.length is 0, React renders the number 0 on screen
{items.length && <List items={items} />}

// Right
{items.length > 0 && <List items={items} />}
{items.length ? <List items={items} /> : null}
```

❌ **Mistake 2:** Returning multiple roots, or using HTML attribute names
✅ **Correct:** Wrap in a Fragment and use camelCase names

```jsx
// Wrong: Adjacent JSX elements must be wrapped; class and for are reserved words in JS
function Bad() {
  return (
    <label for="a" class="x">Name</label>
    <input id="a" />
  );
}

// Right
function Good() {
  return (
    <>
      <label htmlFor="a" className="x">Name</label>
      <input id="a" />
    </>
  );
}
```

❌ **Mistake 3:** Putting statements (`if`, `for`) or objects directly inside `{}`
✅ **Correct:** Use expressions: ternary, `&&`, `.map`; convert objects to strings or render their fields

```jsx
// Wrong
<p>{if (ok) 'Yes'}</p>            // ❌ syntax error: if is a statement
<p>{{ name: 'Asha' }}</p>         // ❌ runtime error: Objects are not valid as a React child

// Right
<p>{ok ? 'Yes' : 'No'}</p>        // ✅ expression
<p>{user.name}</p>                // ✅ render a primitive field
```

---

## 🧠 Tricky Interview Question

```jsx
import { createRoot } from 'react-dom/client';

function App() {
  const a = null;
  const b = undefined;
  const c = false;
  const d = 0;
  const e = '';
  return (
    <div>
      [{a}] [{b}] [{c}] [{d}] [{e}] [{true}] [{NaN}]
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```
What text does the `div` show?

**Answer:** `[] [] [] [0] [] [] [NaN]`. React does not render `null`, `undefined`, `false` or `true` (they are valid "empty" children), so the brackets are empty for those. The empty string renders nothing visible either. Numbers render, including `0` and `NaN`. This is why `{count && <X />}` shows `0` when `count` is `0`, and why `{flag && <X />}` is safe only when `flag` is a real boolean.

---

## ⚫ Interview Questions + Answers

Q1: What is JSX and is it required to use React?
A1: JSX is syntax sugar that a compiler turns into function calls (`jsx()` or `createElement`) returning React elements. It is not required: you can call `createElement` directly, but nearly everyone uses JSX because it is far more readable.

Q2: Why do we use `className` and `htmlFor` instead of `class` and `for`?
A2: JSX is JavaScript, and `class` and `for` are reserved words in JS. DOM properties are also named `className` and `htmlFor`, and JSX uses camelCase names that match the DOM API. `className` is the standard.

Q3: Why must a component return a single root element?
A3: A function can return only one value, and JSX tags compile to a single function call. To return siblings without an extra DOM node, wrap them in a Fragment: `<>...</>`.

Q4: What can go inside `{}` in JSX?
A4: Any JavaScript expression: variables, function calls, ternaries, `&&`, template literals, `.map()` results. Statements such as `if`, `for`, `switch` cannot. Plain objects cannot be rendered as children (arrays of elements can).

Q5: Do I still need `import React from 'react'` in every file?
A5: Not since the new JSX transform (React 17+, enabled by default in Vite, Next.js and modern tooling). The compiler imports `jsx` from `react/jsx-runtime` for you. You import only the hooks or APIs you use.

---

## 🔷 When to Use + When Not to Use
✅ **Use JSX when:**
- Building components in any React project (it is the standard)
- You want logic and markup next to each other and compile-time syntax checks
- You use TypeScript (TSX gives type-checked props and elements)

❌ **Avoid / be careful when:**
- Putting heavy logic directly inside JSX (move it to variables or helper functions above `return`)
- Creating deeply nested ternaries (split into small components or early returns)
- Building HTML strings and using `dangerouslySetInnerHTML` (XSS risk; sanitize first)

---

## 📊 Visual Diagram

```
   JSX (what you write)                    What the compiler outputs
 ┌────────────────────────────┐        ┌────────────────────────────────────┐
 │ <button className="btn"    │  ───►  │ jsx('button', {                    │
 │   onClick={add}>Add</button>│        │   className: 'btn',                │
 └────────────────────────────┘        │   onClick: add, children: 'Add' }) │
                                        └──────────────────┬─────────────────┘
                                                           ▼
                                        { type:'button', props:{...} }   ← React element (plain object)
                                                           ▼
                                               React diffs → updates DOM

  Allowed inside { }:  expressions ✅    |   Not allowed:  statements ❌ (if/for)
  Falsy render:  null undefined false true → nothing    |  0 NaN → printed
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JSX | HTML-like syntax in JavaScript | JavaScript में HTML जैसा syntax |
| React element | Plain object describing UI | UI बताने वाला plain object |
| Fragment | Wrapper that adds no DOM node | बिना DOM node वाला wrapper |
| Expression | Code that produces a value | वह code जो value देता है |
| className | JSX name for the class attribute | class attribute का JSX नाम |
| Self-closing tag | Tag ending with `/>` | `/>` पर खत्म होने वाला tag |
| JSX transform | Compiler step turning JSX to calls | JSX को calls में बदलने वाला compiler चरण |
| key | Identity for list items | List items की पहचान |

---

## ⚡ 3-Line Summary
**English:**
1. JSX is JavaScript in disguise: one root, closed tags, camelCase attributes, expressions in `{}`.
2. Compilers turn it into element-creating function calls; no `import React` needed in modern setups.
3. Best practices: stable keys, boolean-safe `&&`, small components, accessible markup.

**Hindi:**
1. JSX भेस बदला हुआ JavaScript है: एक root, बंद tags, camelCase attributes, और `{}` में expressions।
2. Compilers इसे elements बनाने वाले function calls में बदलते हैं; आधुनिक setup में `import React` ज़रूरी नहीं।
3. अच्छी आदतें: stable keys, boolean-safe `&&`, छोटे components, accessible markup।

---

## ➡️ Next Topic
**9. Babel + Webpack in React** — JSX और modern JavaScript browser तक पहुँचने से पहले compile और bundle कैसे होते हैं, यह समझने के लिए Babel और Webpack की भूमिका पढ़ें।
