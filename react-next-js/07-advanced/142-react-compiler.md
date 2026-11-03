# 142. React Compiler (new)
# हिंदी में: React Compiler — अपने आप Memoization करने वाला Compiler

---

## 🔵 Simple Definition (English)
The **React Compiler** is a build-time tool that analyzes your components and automatically adds memoization, so values, functions and JSX are reused when their inputs do not change. You write plain React, and it does what `useMemo`, `useCallback` and `React.memo` did by hand.

## 🔵 सरल परिभाषा (Hindi)
**React Compiler** एक build-time tool है जो आपके components को analyze करके अपने आप memoization जोड़ देता है, ताकि inputs न बदलने पर values, functions और JSX दोबारा इस्तेमाल हों। आप सादा React लिखते हो, और `useMemo`, `useCallback`, `React.memo` का काम वह खुद कर देता है।

---

## 🔴 Problem it Solves

Re-rendering a parent re-renders all children by default. To stop wasted work, developers wrap things in `useMemo`, `useCallback` and `memo`, but this is verbose, easy to forget, easy to get wrong (wrong dependency arrays, unstable props) and clutters the code.

```jsx
// PROBLEM: manual memoization everywhere
const ProductList = memo(function ProductList({ items, onAdd }) {   // memo to skip re-render
  const sorted = useMemo(() => [...items].sort(byPrice), [items]);   // memo to avoid re-sorting
  return sorted.map((p) => <Row key={p.id} p={p} onAdd={onAdd} />);
});
function Page({ items }) {
  const onAdd = useCallback((id) => addToCart(id), []);              // stable function for memo child
  return <ProductList items={items} onAdd={onAdd} />;
}

// SOLUTION: write plain code; the compiler memoizes automatically
function ProductList({ items, onAdd }) {
  const sorted = [...items].sort(byPrice);        // compiler caches this by items
  return sorted.map((p) => <Row key={p.id} p={p} onAdd={onAdd} />);
}
function Page({ items }) {
  const onAdd = (id) => addToCart(id);            // compiler keeps it stable
  return <ProductList items={items} onAdd={onAdd} />;
}
```

## 🔴 यह क्यों बना? (Hindi)
Parent re-render होने पर डिफ़ॉल्ट रूप से सारे children re-render होते हैं। फालतू काम रोकने के लिए developers `useMemo`, `useCallback` और `memo` लगाते हैं, लेकिन यह लंबा है, भूलना आसान है, गलत होना आसान है (गलत dependency arrays, unstable props) और code गंदा करता है। Compiler से आप सादा code लिखते हो और memoization अपने आप होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You install babel-plugin-react-compiler (React Compiler 1.0 is stable; older docs call it a "release candidate", so check your version)
Step 2 → At build time it parses each component/hook into a control-flow graph
Step 3 → It tracks which values depend on which props/state ("data flow analysis")
Step 4 → It inserts cache slots (internally a hook-like `_c(n)` cache) around each computation and JSX element
Step 5 → At runtime, if the inputs are identical (Object.is) to the previous render, the cached output is reused
Step 6 → Rules of React must hold (pure render, no mutation of props/state); components that break them are skipped
Step 7 → You can opt out of a component with the "use no memo" directive

Re-render: components still "render", but unchanged parts return cached JSX, so children skip real work (like automatic memo)
Performance: fine-grained, even memoizes after conditionals (which useMemo cannot); needs React 19, or React 17/18 with the react-compiler-runtime package
Existing useMemo/useCallback: keep working, and are still useful as an escape hatch (e.g., stable effect dependencies)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → babel-plugin-react-compiler install करो (React Compiler 1.0 stable है; पुराने docs "release candidate" कहते हैं, अपना version देखो)
Step 2 → Build time पर यह हर component/hook को control-flow graph में बदलता है
Step 3 → यह देखता है कि कौन सी value किस props/state पर निर्भर है ("data flow analysis")
Step 4 → हर computation और JSX के चारों ओर cache slots जोड़ता है (अंदर hook जैसा `_c(n)` cache)
Step 5 → Runtime पर अगर inputs पिछली बार जैसे ही हैं (Object.is), तो cached output दोबारा इस्तेमाल होता है
Step 6 → React के नियम मानने ज़रूरी हैं (pure render, props/state mutate नहीं); जो components नियम तोड़ें उन्हें यह छोड़ देता है
Step 7 → किसी component को "use no memo" directive से बाहर रख सकते हैं

Re-render: components "render" तो होते हैं, पर unchanged हिस्से cached JSX लौटाते हैं, यानी automatic memo जैसा
Performance: बहुत बारीक, conditionals के बाद भी memoize करता है (जो useMemo नहीं कर सकता); React 19 चाहिए, या React 17/18 के लिए react-compiler-runtime package
पुराने useMemo/useCallback: चलते रहते हैं और escape hatch के रूप में काम के हैं
```

---

## 🟡 Real World Example
**Zomato restaurant listing with filters:** A list of 200 restaurant cards re-renders each time the user types in the search box, because the parent state changes. Teams used to wrap every card in `memo` and every handler in `useCallback`. With the compiler enabled, the typing input still re-renders, but each card whose data did not change returns its cached JSX, so typing stays smooth without manual memo code.

## 🟡 Real Example Hindi mein
**Zomato restaurant listing with filters:** 200 restaurant cards की list हर बार re-render होती है जब user search box में type करता है, क्योंकि parent की state बदलती है। पहले टीमें हर card को `memo` और हर handler को `useCallback` में लपेटती थीं। Compiler चालू होने पर input तो re-render होता है, पर जिस card का data नहीं बदला उसका cached JSX लौट आता है, इसलिए बिना manual memo के typing smooth रहती है।

---

## 💻 Code Example — Basic

```jsx
// Basic: what you write vs what the compiler conceptually does (the compiler output is generated, never written by hand)
import { useState } from 'react';                           // state hook
import { createRoot } from 'react-dom/client';              // root API

// What YOU write: plain React, no memo at all
function Cart({ items }) {
  const [coupon, setCoupon] = useState('');                  // typing a coupon re-renders Cart
  const total = items.reduce((s, i) => s + i.price * i.qty, 0); // compiler caches this by `items`
  return (
    <div>
      <input value={coupon} onChange={(e) => setCoupon(e.target.value)} placeholder="Coupon" />
      <p>Total: Rs {total}</p>                               {/* reused JSX while total is unchanged */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(
  <Cart items={[{ price: 199, qty: 2 }, { price: 99, qty: 1 }]} />
);

/* Conceptual compiled shape (simplified, real output differs):
   const $ = useMemoCache(3);
   let total;
   if ($[0] !== items) { total = items.reduce(...); $[0] = items; $[1] = total; }
   else { total = $[1]; }
   // JSX elements are cached the same way, keyed by their inputs
*/
```

## 💻 Code Example — Advanced

```jsx
// Advanced: enabling the compiler in a Vite project, opting out, and eslint support
// ---------- vite.config.js ----------
import { defineConfig } from 'vite';                          // Vite config helper
import react from '@vitejs/plugin-react';                     // React plugin with Babel support

export default defineConfig({
  plugins: [
    react({
      babel: {
        plugins: [
          ['babel-plugin-react-compiler', {                   // run the compiler on your source
            compilationMode: 'infer',                         // 'infer' (default) | 'annotation' (opt-in per function)
            // target: '18',                                  // set when using React 17/18 + react-compiler-runtime
          }],
        ],
      },
    }),
  ],
});

// ---------- src/ProductCard.jsx ----------
import { useState } from 'react';

export default function ProductCard({ product, onAdd }) {
  const [liked, setLiked] = useState(false);                  // local state
  const discount = Math.round(100 - (product.price / product.mrp) * 100); // cached by price/mrp
  return (
    <article>
      <h3>{product.name}</h3>
      <p>Rs {product.price} ({discount}% off)</p>
      <button onClick={() => onAdd(product.id)}>Add</button> {/* handler kept stable by the compiler */}
      <button onClick={() => setLiked((l) => !l)}>{liked ? 'Liked' : 'Like'}</button>
    </article>
  );
}

// ---------- src/LegacyWidget.jsx: opt a single component out ----------
export function LegacyWidget({ el }) {
  'use no memo';                                              // directive: compiler skips this function
  el.count = (el.count || 0) + 1;                             // mutates props: breaks Rules of React, so skip it
  return <p>{el.count}</p>;
}

// ---------- eslint.config.js (eslint-plugin-react-hooks recommended config includes compiler rules) ----------
// import reactHooks from 'eslint-plugin-react-hooks';
// export default [reactHooks.configs['recommended-latest']];   // flags code the compiler cannot optimize
```

---

## 🟠 Next.js Connection

Next.js 15 has experimental support through `experimental.reactCompiler` (uses SWC, plus the Babel plugin for full coverage). In later versions (Next.js 16) it is a stable top-level `reactCompiler` option; this is version-dependent, so check the docs for your exact version. It works for both Server and Client Components, but mainly benefits Client Components, because Server Components render once per request and do not re-render in the browser.

```js
// next.config.js (Next.js 15, experimental; install babel-plugin-react-compiler first)
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    reactCompiler: true,                  // enable compiler for the whole app
    // reactCompiler: { compilationMode: 'annotation' }, // opt-in per component with "use memo"
  },
};
module.exports = nextConfig;              // Next.js loads this at build time
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Mutating props, state or values during render and expecting the compiler to "just work"
✅ **Correct:** Follow the Rules of React: render must be pure; copy before changing

```jsx
// Wrong: mutation during render → compiler skips it, or stale UI
function List({ items }) {
  items.sort();                              // ❌ mutates the prop array
  return items.map((i) => <li key={i}>{i}</li>);
}
// Right
function List({ items }) {
  const sorted = [...items].sort();          // ✅ new array
  return sorted.map((i) => <li key={i}>{i}</li>);
}
```

❌ **Mistake 2:** Removing all `useMemo`/`useCallback` from an existing app on day one
✅ **Correct:** Enable the compiler, keep existing memos (they are safe), and clean up gradually after profiling

```jsx
// Risky: deleting a useCallback that is an effect dependency can change when the effect fires
useEffect(() => { subscribe(onMessage); }, [onMessage]);   // onMessage was stable via useCallback
// Keep it unless you verified the behavior after enabling the compiler
```

❌ **Mistake 3:** Thinking the compiler fixes slow algorithms or huge lists
✅ **Correct:** It only removes redundant re-computation; use virtualization, pagination and better algorithms for real cost

```jsx
// Wrong assumption: "compiler will make 50,000 DOM rows fast"
// Right: virtualize (react-window / TanStack Virtual) and keep the compiler for memoization
```

---

## 🧠 Tricky Interview Question

```jsx
let renders = 0;
function Child({ value }) {
  renders++;                                  // side effect during render
  return <p>{value}</p>;
}
function Parent() {
  const [n, setN] = useState(0);
  return (
    <>
      <button onClick={() => setN(n + 1)}>+</button>
      <Child value="fixed" />
    </>
  );
}
```
**Answer:** Without the compiler, clicking `+` re-renders `Parent` and `Child` each time, so `renders` increases on every click (in Strict Mode dev it doubles). With the compiler, `<Child value="fixed" />` is cached because its inputs never change, so `Child` is not called again and `renders` stays the same. This also shows why side effects during render are dangerous: the compiler (and Strict Mode) may call or skip render at any time, so the counter is not reliable. Do side effects in effects or handlers.

---

## ⚫ Interview Questions + Answers

Q1: What does the React Compiler do?
A1: It is a build-time Babel/SWC plugin that automatically memoizes components and hooks, so you do not need to write `useMemo`, `useCallback` or `React.memo` in most cases.

Q2: Does it replace `useMemo` and `useCallback` completely?
A2: Mostly for performance. They stay valid as escape hatches, for example when you need a stable value for an effect dependency or an expensive calculation you want to control precisely. New code usually does not need them.

Q3: What are the requirements for code to be compiled?
A3: It must follow the Rules of React: pure components and hooks, no mutation of props/state or values during render, hooks called unconditionally at the top level. Code that cannot be proven safe is skipped without breaking the app. `eslint-plugin-react-hooks` reports issues.

Q4: How is compiler memoization different from `useMemo`?
A4: It is automatic, fine-grained (per expression and JSX), and can memoize after early returns or conditionals, which hooks cannot do because of the rules of hooks.

Q5: Which React versions work, and what about Server Components?
A5: React 19 is the target; React 17 and 18 work with `react-compiler-runtime` and a `target` option. It benefits Client Components mainly, because Server Components do not re-render in the browser. Details change between releases, so check current docs.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Starting a new React 19 project (enable it from day one)
- Your codebase follows Rules of React and uses lots of manual memo
- You want less boilerplate and fewer dependency array bugs

❌ **Avoid when:**
- Code mutates props/state or relies on side effects in render (fix or use `"use no memo"`)
- You rely on render counts for logic
- Your toolchain does not support Babel/SWC plugins yet

---

## 📊 Visual Diagram

```
 Source (you write)            Build step                    Runtime
 ┌───────────────────┐      ┌──────────────────────┐      ┌────────────────────────┐
 │ function Cart() { │      │ babel-plugin-        │      │ render #1: compute all │
 │  const total = .. │ ───▶ │ react-compiler       │ ───▶ │ render #2: inputs same?│
 │  return <p>..</p> │      │ + cache slots $[0..n]│      │   yes → reuse cached   │
 └───────────────────┘      └──────────────────────┘      │   no  → recompute      │
                                                          └────────────────────────┘
 Before: memo() + useMemo() + useCallback() by hand
 After : plain code, same effect, less noise
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| React Compiler | Build tool that auto-memoizes | अपने आप memoize करने वाला build tool |
| Memoization | Reusing a result when inputs are unchanged | Inputs न बदलने पर पुराना नतीजा दोबारा इस्तेमाल |
| Rules of React | Purity and hook rules the compiler assumes | Compiler जिन नियमों को मानता है |
| `"use no memo"` | Directive to skip a function | किसी function को छोड़ने का directive |
| `compilationMode` | infer or annotation mode | Compiler कैसे चुने कि क्या compile करना है |
| Cache slot | Stored previous input/output pair | पिछला input/output रखने की जगह |
| `Object.is` | Equality used to compare inputs | Inputs की तुलना का तरीका |
| Escape hatch | Manual override like `useMemo` | Manual विकल्प |

---

## ⚡ 3-Line Summary
**English:**
1. The React Compiler automatically memoizes components at build time, replacing most manual `useMemo`, `useCallback` and `memo`.
2. It requires pure, rules-following code; unsafe components are skipped, and `"use no memo"` opts out.
3. Enable it gradually, keep existing memos, and still fix real bottlenecks with virtualization and better algorithms.

**Hindi:**
1. React Compiler build time पर components को अपने आप memoize करता है और ज़्यादातर manual `useMemo`, `useCallback`, `memo` की जगह लेता है।
2. इसे pure, नियम मानने वाला code चाहिए; असुरक्षित components छोड़ दिए जाते हैं, और `"use no memo"` से बाहर रख सकते हो।
3. धीरे-धीरे चालू करो, पुराने memos रखो, और असली bottlenecks virtualization और बेहतर algorithms से ठीक करो।

---

## ➡️ Next Topic
**143. Compound Components Pattern** — अब React की design patterns शुरू होती हैं: ऐसे components जो आपस में state share करके साफ, declarative API देते हैं।
