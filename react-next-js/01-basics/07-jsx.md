# 07. JSX — JavaScript XML
# हिंदी में: JSX — JavaScript में HTML जैसा Syntax

---

## 🔵 Simple Definition (English)
**JSX** (JavaScript XML) is a syntax extension for JavaScript that lets you write HTML-like code inside JavaScript. It gets **compiled by Babel** into `React.createElement()` calls. JSX is NOT HTML — it's syntactic sugar for creating React elements.

## 🔵 सरल परिभाषा (Hindi)
**JSX** (JavaScript XML) JavaScript का syntax extension है जो आपको JavaScript के अंदर HTML जैसा code लिखने देता है। **Babel** इसे `React.createElement()` calls में compile करता है। JSX HTML नहीं है — यह React elements बनाने का syntactic sugar है।

---

## 🔴 Problem it Solves
Without JSX, React code would look like this:
```javascript
React.createElement('div', { className: 'card' },
  React.createElement('h2', null, 'Pizza'),
  React.createElement('p', null, '₹299'),
  React.createElement('button', { onClick: handleClick }, 'Add to Cart')
);
```
**JSX makes this readable** and close to the HTML developers already know.

## 🔴 यह क्यों बना? (Hindi)
JSX के बिना React code ऐसा दिखता:
```javascript
React.createElement('div', null, React.createElement('h2', null, 'Pizza'))
// नेस्टेड React.createElement calls — unreadable!
```
**JSX इसे readable** बनाता है और HTML जैसा जो developers पहले से जानते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write JSX in your .jsx/.tsx file
Step 2 → Babel (transpiler) converts JSX to React.createElement()
Step 3 → React.createElement() creates Virtual DOM objects
Step 4 → React renders these objects to real DOM
Step 5 → Browser paints the UI

JSX       →  Babel  →  React.createElement()  →  Virtual DOM  →  Real DOM
<h1>Hi</h1>    →     React.createElement('h1', null, 'Hi')
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप .jsx/.tsx file में JSX लिखते हो
Step 2 → Babel JSX को React.createElement() में convert करता है
Step 3 → React.createElement() Virtual DOM objects बनाता है
Step 4 → React इन्हें real DOM में render करता है
Step 5 → Browser UI paint करता है
```

---

## 🟡 Real World Example
**Zomato Restaurant Card** — The entire card with image, name, rating, price is JSX. You write it like HTML but it's actually JavaScript that creates React elements. The `{}` curly braces inject dynamic data from props/state into the UI.

## 🟡 Real Example Hindi mein
**Zomato Restaurant Card** — Image, name, rating, price वाला पूरा card JSX है। आप HTML जैसा लिखते हो but actually यह JavaScript है जो React elements बनाता है। `{}` curly braces props/state से dynamic data inject करते हैं।

---

## 💻 Code Example — Basic

```jsx
// JSX RULES — सबसे ज़रूरी rules
import { useState } from 'react';

function JSXRules() {
  const userName = "Aditya";
  const userAge = 25;
  const isLoggedIn = true;
  const products = ["Pizza", "Burger", "Coke"];

  return (
    // RULE 1: Single root element (or use Fragment <>)
    <div className="container">

      {/* RULE 2: className not class */}
      <div className="header">Header</div>

      {/* RULE 3: {} for JavaScript expressions */}
      <p>Hello, {userName}!</p>
      <p>Age: {userAge * 2}</p>                 {/* math inside {} */}
      <p>Greeting: {isLoggedIn ? "Hi!" : "Please login"}</p>

      {/* RULE 4: camelCase for HTML attributes */}
      <input
        type="text"
        onChange={() => {}}          {/* not onchange */}
        tabIndex={1}                  {/* not tabindex */}
        autoFocus                     {/* not autofocus */}
      />

      {/* RULE 5: Self-closing tags must be closed */}
      <img src="/photo.jpg" alt="Photo" />   {/* <img/> not just <img> */}
      <br />
      <input type="text" />

      {/* RULE 6: JSX comments use {/* */} */}
      {/* This is a JSX comment */}

      {/* RULE 7: Return EXPRESSION not statement in {} */}
      {/* WRONG: {if (x) { return ... }} */}
      {/* CORRECT: ternary or && */}
      {isLoggedIn && <span>Logged in!</span>}

      {/* RULE 8: Numbers and booleans don't render (except 0!) */}
      {true}    {/* renders nothing */}
      {false}   {/* renders nothing */}
      {42}      {/* renders "42" */}
      {0}       {/* renders "0" — GOTCHA! */}

      {/* RULE 9: Arrays render (each item side by side) */}
      {products.map(p => <li key={p}>{p}</li>)}

      {/* RULE 10: style takes OBJECT not string */}
      <div style={{ color: 'red', fontSize: '16px' }}>Styled</div>
      {/* NOT style="color:red" — that's HTML, not JSX */}

    </div>
  );
}

export default JSXRules;
```

## 💻 Code Example — Advanced

```jsx
// Advanced JSX patterns — production code
import { Fragment } from 'react';

// ── FRAGMENTS ─────────────────────────────
// Return multiple elements without wrapper div
function MultipleItems() {
  return (
    <>                            {/* Fragment shorthand */}
      <h1>Title</h1>
      <p>Paragraph</p>
      <span>Span</span>
    </>
    // OR: <Fragment> if you need key prop on each item
  );
}

// Fragment with key (needed in lists):
function TableRows({ items }) {
  return items.map(item => (
    <Fragment key={item.id}>      {/* can't use <> here, need key */}
      <tr><td>{item.name}</td></tr>
      <tr><td>{item.detail}</td></tr>
    </Fragment>
  ));
}

// ── DYNAMIC JSX ───────────────────────────
function DynamicComponent({ type, children }) {
  // Variable as component name — must be capitalized!
  const Tag = type === 'primary' ? 'h1' : 'h2'; // string works for HTML elements
  // const Component = type === 'a' ? ButtonA : ButtonB; // for React components

  return <Tag className="dynamic">{children}</Tag>;
}

// ── SPREADING PROPS ───────────────────────
function InputField({ label, error, ...inputProps }) {
  // inputProps = { type, placeholder, value, onChange, ... }
  return (
    <div>
      <label>{label}</label>
      <input {...inputProps} />    {/* spread remaining props to native input */}
      {error && <span className="error">{error}</span>}
    </div>
  );
}
// Usage: <InputField label="Email" type="email" placeholder="Enter email" error={emailError} />

// ── CONDITIONAL RENDERING PATTERNS ───────
function OrderStatus({ status, count }) {
  // Pattern 1: ternary
  const badge = status === 'active' ? '🟢' : '🔴';

  // Pattern 2: && (short-circuit) — BE CAREFUL WITH 0!
  const showCount = count && <span>{count}</span>; // WRONG if count=0 → renders "0"
  const showCountSafe = count > 0 && <span>{count}</span>; // ✅ safe

  // Pattern 3: IIFE in JSX
  const statusText = (() => {
    if (status === 'pending')   return 'Waiting...';
    if (status === 'preparing') return 'Kitchen is working!';
    if (status === 'delivered') return 'Enjoy your meal!';
    return 'Unknown status';
  })();

  // Pattern 4: object map (cleaner than if/else chains)
  const STATUS_LABELS = {
    pending:   <span className="yellow">Pending</span>,
    preparing: <span className="orange">Preparing</span>,
    delivered: <span className="green">Delivered</span>,
  };

  return (
    <div>
      {badge} {statusText}
      {STATUS_LABELS[status] || <span>Unknown</span>}
      {showCountSafe}
    </div>
  );
}

// ── RENDERING PATTERNS ────────────────────
function SmartList({ items, renderItem, emptyMessage = "No items found" }) {
  // Empty state
  if (items.length === 0) {
    return <p className="empty">{emptyMessage}</p>;
  }

  return (
    <ul className="list">
      {items.map((item, index) => (
        // renderItem is a "render prop" — caller controls item rendering
        <li key={item.id || index}>
          {renderItem(item, index)}
        </li>
      ))}
    </ul>
  );
}

// Usage:
// <SmartList
//   items={products}
//   renderItem={(p) => <ProductCard product={p} />}
//   emptyMessage="No products available"
// />
```

---

## 🟠 Next.js Connection

```jsx
// JSX works identically in Next.js
// But Next.js adds file-based routing via JSX files

// app/page.jsx → "/" route
export default function HomePage() {
  return <h1>Home Page</h1>;
}

// app/about/page.jsx → "/about" route
export default function AboutPage() {
  return <h1>About Page</h1>;
}

// Next.js Server Components: JSX on server (no hooks, no state)
async function ServerCard() {
  const data = await fetchData();
  // This JSX runs on server — HTML sent to browser
  return <div>{data.name}</div>;
}

// Next.js Client Components: must add 'use client' for hooks/interactivity
'use client';
function ClientCounter() {
  const [n, setN] = useState(0);
  return <button onClick={() => setN(c => c+1)}>{n}</button>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `class` instead of `className`
```jsx
// WRONG:
<div class="container">Hello</div>    // ❌ 'class' is reserved in JS

// CORRECT:
<div className="container">Hello</div> // ✅
```

❌ **Mistake 2:** `&&` with 0 (renders "0" on screen!)
```jsx
// WRONG: if cart is empty (0 items), renders "0" on screen!
{cart.length && <CartBadge count={cart.length} />}
// When cart.length = 0: renders "0" because 0 is falsy but JSX renders it!

// CORRECT: convert to boolean
{cart.length > 0 && <CartBadge count={cart.length} />}
// OR:
{!!cart.length && <CartBadge count={cart.length} />}
```

❌ **Mistake 3:** Statements inside `{}` (not allowed — only expressions)
```jsx
// WRONG: if statement inside JSX
return (
  <div>
    {if (isLoggedIn) { <p>Hello!</p> }}  // ❌ SyntaxError!
  </div>
);

// CORRECT: ternary (expression)
return <div>{isLoggedIn ? <p>Hello!</p> : null}</div>;
// OR: && operator
return <div>{isLoggedIn && <p>Hello!</p>}</div>;
```

---

## 🧠 Tricky Interview Question

```jsx
function App() {
  const items = [];

  return (
    <div>
      {items.length && <p>Items: {items.length}</p>}
    </div>
  );
}
// What does this render?
```
**Answer:** Renders `<div>0</div>` — showing the number "0" on screen! `items.length` is `0` (falsy), so `0 && <p>...</p>` evaluates to `0` (not `false`). JSX renders `0` as text! Fix: `{items.length > 0 && <p>Items: {items.length}</p>}`.

---

## ⚫ Interview Questions + Answers

**Q1: What is JSX and how does it work under the hood?**
A1: JSX is a syntax extension for JavaScript that looks like HTML but compiles to `React.createElement()` calls via Babel. `<div className="box">Hello</div>` becomes `React.createElement('div', {className: 'box'}, 'Hello')`. This creates a plain JS object (Virtual DOM node). You need Babel/a bundler to use JSX — browsers can't understand it directly.

**Q2: What are the main differences between JSX and HTML?**
A2: (1) `className` not `class`. (2) `htmlFor` not `for`. (3) Self-closing tags: `<img />` `<br />`. (4) `{}` for JS expressions. (5) camelCase events: `onClick`, `onChange`, `onMouseEnter`. (6) `style` takes object: `style={{ color: 'red' }}`. (7) JSX comments: `{/* comment */}`. (8) `tabIndex`, `autoFocus`, `autoComplete` (camelCase).

**Q3: Can we use JSX without React?**
A3: Yes (with React 17+ and the new JSX transform). Before React 17, you needed `import React from 'react'` at the top of every JSX file because JSX compiled to `React.createElement()`. With the new transform, the compiler automatically imports the JSX runtime — no manual React import needed. Other libraries (like Preact) also support JSX with their own pragma.

**Q4: What is a React Fragment and why use it?**
A4: Fragment (`<>...</>` or `<React.Fragment>`) lets you return multiple elements without adding an extra DOM node. Every JSX return must have one root — without fragments, you'd add unnecessary `<div>` wrappers that pollute the DOM. Use `<Fragment key={...}>` (not `<>`) when you need to add a `key` prop (for list items that return multiple elements).

**Q5: Can you use JavaScript statements (if/for) inside JSX?**
A5: No — JSX `{}` only accepts **expressions** (things that return a value), not **statements** (if/for/switch). Use ternary `? :` for if/else, `&&` for conditional rendering, and `.map()` for loops. For complex logic, compute values before JSX return and use those variables inside JSX.

---

## 🔷 When to Use + When Not to Use
✅ **JSX is used when:**
- Writing any React component (it's the standard)
- Need to mix JavaScript logic with UI structure
- Want readable, maintainable UI code

❌ **JSX alternatives (rare):**
- Pure `React.createElement()` calls (no Babel needed, but ugly)
- Template strings for emails/server rendering
- Svelte/Vue use different templating (not JSX)

---

## 📊 Visual Diagram

```
JSX COMPILATION PIPELINE:
────────────────────────────────────────────────
Your Code (.jsx):
  <div className="card">
    <h2>{name}</h2>
  </div>
       │
       ▼ Babel transforms
  React.createElement('div', {className:'card'},
    React.createElement('h2', null, name)
  )
       │
       ▼ Creates Virtual DOM object
  {
    type: 'div',
    props: {
      className: 'card',
      children: {
        type: 'h2',
        props: { children: 'Pizza' }
      }
    }
  }
       │
       ▼ React renders to
  Real DOM: <div class="card"><h2>Pizza</h2></div>

JSX EXPRESSION RULES:
────────────────────────────────────────────────
  ✅ {name}              → variable value
  ✅ {2 + 2}             → math: 4
  ✅ {isOn ? 'Yes' : 'No'} → ternary
  ✅ {items.map(...)}    → array (renders each)
  ✅ {fn()}              → function call
  ❌ {if (x) {...}}      → statement — NOT allowed
  ❌ {for (...) {...}}   → statement — NOT allowed
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JSX | HTML-like syntax in JavaScript | JavaScript में HTML जैसा syntax |
| Babel | Transpiler that compiles JSX | JSX compile करने वाला tool |
| className | JSX attribute for CSS class | CSS class के लिए JSX attribute |
| Expression | Code that returns value | Value return करने वाला code |
| Fragment | Wrapper without DOM node | DOM node के बिना wrapper |
| Self-closing | `<img />` — tag with no children | कोई child नहीं वाला tag |
| Spread props | `{...props}` — pass all props | सभी props pass करना |

---

## ⚡ 3-Line Summary
**English:**
1. JSX = HTML-like syntax in JS, compiled by Babel to `React.createElement()` — it's not HTML, it's JS.
2. Key rules: `className`, camelCase events, `{}` for expressions only (no if/for), self-close all tags.
3. `&&` with 0 renders "0" on screen — always use `count > 0 &&` or ternary for safe conditional rendering.

**Hindi:**
1. JSX = JS में HTML जैसा syntax, Babel `React.createElement()` में compile करता है — HTML नहीं, JS है।
2. Key rules: `className`, camelCase events, `{}` में सिर्फ expressions, सब tags self-close करो।
3. `0 &&` screen पर "0" render करता है — safe conditional rendering के लिए `count > 0 &&` या ternary use करो।

---

## ➡️ Next Topic
**08. JSX Rules + Best Practices** — JSX के advanced rules और production-ready best practices।
