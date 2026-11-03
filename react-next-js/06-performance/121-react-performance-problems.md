# 121. React Performance Problems
# हिंदी में: React Performance की आम समस्याएँ — App धीमा क्यों होता है?

---

## 🔵 Simple Definition (English)
A **React performance problem** is when the UI feels slow or janky because React does too much work: too many re-renders, heavy calculations during render, huge lists in the DOM, or a large JavaScript bundle. Most problems come from **unnecessary work**, not from React being slow.

## 🔵 सरल परिभाषा (Hindi)
**React performance problem** तब होती है जब UI धीमा या अटकता हुआ लगता है क्योंकि React बहुत ज़्यादा काम करता है: बहुत सारे re-renders, render के दौरान भारी calculations, DOM में विशाल lists, या बड़ा JavaScript bundle। ज़्यादातर समस्याएँ **अनावश्यक काम** से आती हैं, React के धीमा होने से नहीं।

---

## 🔴 Problem it Solves

Developers often guess at performance ("add `memo` everywhere") and make things worse. To fix performance you must first know what the usual causes are, so you can measure and pick the right tool. This topic is the map: the 6 common causes and the matching fix.

```jsx
// PROBLEM 1: parent state change re-renders every child (even if their props did not change)
function Page() {
  const [text, setText] = useState('');                        // typing changes this on every keystroke
  return (<><input value={text} onChange={e => setText(e.target.value)} />
            <HugeTable rows={rows} /></>);                     // re-rendered on every key press
}

// PROBLEM 2: heavy work during render
const sorted = bigList.slice().sort(compare);                  // runs on EVERY render

// PROBLEM 3: new object/function props break memoization
<Child style={{ color: 'red' }} onClick={() => go()} />        // new references every render
```

## 🔴 यह क्यों बना? (Hindi)
Developers अक्सर अंदाज़े से optimization करते हैं ("हर जगह `memo` लगा दो") और हालत और बिगाड़ देते हैं। Performance सुधारने से पहले जानना ज़रूरी है कि आम कारण क्या हैं, ताकि पहले measure करो और फिर सही tool चुनो। यह topic एक नक्शा है: 6 आम कारण और उनके मिलते-जुलते हल।

---

## 🟢 How it Works — Step by Step

```
How React renders (why slowness happens):
Step 1 → Trigger: state change, props change from parent, or context change
Step 2 → Render phase: React CALLS your component function (and all children by default)
Step 3 → Diffing (reconciliation): compare new element tree with the old one
Step 4 → Commit phase: apply only the real changes to the DOM
Step 5 → Browser paints. The whole thing must finish within ~16 ms for 60 fps

The 6 common causes:
  1. Unnecessary re-renders (parent renders → all children render)
  2. Expensive calculations in render (sort, filter, big loops)
  3. Unstable props (new object/array/function each render) defeating memo
  4. Huge lists / big DOM (thousands of nodes)
  5. Large bundle / too much JS (slow first load)
  6. Wrong state placement (state too high; context value changes too often)

Fix order: MEASURE → move state down → split components → memoize → virtualize → code split
```

## 🟢 कैसे काम करता है? (Hindi)
```
React कैसे render करता है (धीमापन क्यों आता है):
Step 1 → Trigger: state बदली, parent से props बदले, या context बदला
Step 2 → Render phase: React आपका component function (और default रूप से सारे children) CALL करता है
Step 3 → Diffing (reconciliation): नए element tree की पुराने से तुलना
Step 4 → Commit phase: सिर्फ़ असली बदलाव DOM पर लागू होते हैं
Step 5 → Browser paint करता है। यह सब ~16 ms में पूरा होना चाहिए (60 fps के लिए)

6 आम कारण:
  1. अनावश्यक re-renders (parent render हुआ → सारे children भी)
  2. Render में भारी calculations (sort, filter, बड़े loops)
  3. Unstable props (हर render नया object/array/function) जो memo को बेकार कर देते हैं
  4. विशाल lists / बड़ा DOM (हज़ारों nodes)
  5. बड़ा bundle / ज़्यादा JS (पहला load धीमा)
  6. State की गलत जगह (state बहुत ऊपर; context value बार-बार बदलती है)

Fix का क्रम: पहले MEASURE → state नीचे ले जाओ → components बाँटो → memoize → virtualize → code split
```

---

## 🟡 Real World Example
**Flipkart product listing page:** It has a search box, filters, and a grid of 500 products. If the search text lives in the top-level component, every key press re-renders all 500 product cards, and typing lags. Fixes: keep the input state inside a small `SearchBox` component, memoize `ProductCard`, show only visible products with virtualization, and lazy-load the review widget. Amazon's slow-feeling pages often have the same causes: too much JS and too many components updating together.

## 🟡 Real Example Hindi mein
**Flipkart product listing page:** इसमें search box, filters और 500 products का grid है। अगर search text सबसे ऊपर के component में रखा है तो हर key press पर 500 product cards re-render होते हैं और typing अटकती है। हल: input की state छोटे `SearchBox` component के अंदर रखो, `ProductCard` को memoize करो, सिर्फ़ दिखने वाले products virtualization से दिखाओ, और review widget को lazy-load करो। Amazon के धीमे लगने वाले pages में भी अक्सर यही कारण होते हैं: बहुत ज़्यादा JS और एक साथ update होते बहुत सारे components।

---

## 💻 Code Example — Basic

```jsx
// Basic: see the problem and the simplest fix (move state down)
import { useState, memo } from 'react';                          // hooks + memo
import { createRoot } from 'react-dom/client';                   // React 18/19 root API

let renders = 0;                                                  // count how many times Slow renders

function Slow() {
  renders++;                                                      // runs on every render of Slow
  console.log('Slow rendered', renders);                          // visible proof in the console
  return <p>Imagine a heavy component here</p>;                   // stands for a big table or chart
}

// ❌ BEFORE: state lives in the parent, so Slow re-renders on every keystroke
function Before() {
  const [text, setText] = useState('');                           // changes on every key press
  return (
    <div>
      <input value={text} onChange={e => setText(e.target.value)} /> {/* controlled input */}
      <Slow />                                                    {/* re-renders although it has no props */}
    </div>
  );
}

// ✅ AFTER: move the changing state into its own small component
function SearchBox() {
  const [text, setText] = useState('');                           // state is now local to SearchBox
  return <input value={text} onChange={e => setText(e.target.value)} />;
}
function After() {
  return (
    <div>
      <SearchBox />                                               {/* only this re-renders while typing */}
      <Slow />                                                    {/* untouched: parent did not re-render */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<After />);   // try <Before /> to compare the logs
```

## 💻 Code Example — Advanced

```jsx
// Advanced: a "performance smell" demo with 4 problems and their fixes in one product list
import { memo, useCallback, useDeferredValue, useMemo, useState } from 'react';

const PRODUCTS = Array.from({ length: 2000 }, (_, i) => ({     // fake catalogue of 2000 items
  id: i, name: `Product ${i}`, price: (i * 37) % 999,
}));

// FIX for cause 1+3: memo + stable props, so a card re-renders only if ITS data changes
const ProductCard = memo(function ProductCard({ product, onAdd }) {
  return (
    <li>
      {product.name} — ₹{product.price}
      <button onClick={() => onAdd(product.id)}>Add</button>      {/* onAdd must be stable */}
    </li>
  );
});

export default function ProductList() {
  const [query, setQuery] = useState('');                         // search text
  const [cart, setCart] = useState([]);                           // cart ids
  const deferredQuery = useDeferredValue(query);                  // React 18+: lower-priority copy of query

  // FIX for cause 2: filter only when the query changes, not on every cart click
  const visible = useMemo(
    () => PRODUCTS.filter(p => p.name.toLowerCase().includes(deferredQuery.toLowerCase())),
    [deferredQuery]                                               // recompute only when this changes
  );

  // FIX for cause 3: stable function identity, so memo(ProductCard) can skip renders
  const handleAdd = useCallback(
    (id) => setCart(prev => [...prev, id]),                       // functional update: no `cart` dependency
    []
  );

  return (
    <div>
      <input
        value={query}
        onChange={e => setQuery(e.target.value)}                  // input stays responsive (urgent update)
        placeholder="Search 2000 products"
      />
      <p>Cart: {cart.length} items</p>                            {/* cart change: cards do NOT re-render */}
      <ul>
        {visible.slice(0, 100).map(p => (                         {/* FIX for cause 4: render only 100 rows */}
          <ProductCard key={p.id} product={p} onAdd={handleAdd} /> // key = stable id
        ))}
      </ul>
    </div>
  );
}
```

---

## 🟠 Next.js Connection

Next.js attacks several causes for you. **Server Components** send no JavaScript for non-interactive UI (smaller bundle, cause 5). **Automatic code splitting** per route, `next/dynamic` for heavy client widgets, `next/image` for optimized images, `next/font` for fonts and `next/script` for third-party scripts reduce load time. `loading.js` and `<Suspense>` stream the page in parts. Keep `'use client'` boundaries as low and small as possible.

```jsx
// app/products/page.jsx (Server Component: no JS shipped for this list markup)
import dynamic from 'next/dynamic';                                // lazy-load heavy client widgets
import { Suspense } from 'react';
import Image from 'next/image';                                    // automatic image optimization

const ReviewsWidget = dynamic(() => import('./ReviewsWidget'));    // loaded in its own JS chunk, when rendered
// (add { ssr: false } only inside a Client Component, if it needs browser-only APIs)

export default async function Page() {
  const products = await fetch('https://example.com/api/products').then(r => r.json()); // server fetch
  return (
    <main>
      <ul>
        {products.map(p => (
          <li key={p.id}>
            <Image src={p.image} alt={p.name} width={200} height={200} />  {/* lazy + resized */}
            {p.name}
          </li>
        ))}
      </ul>
      <Suspense fallback={<p>Loading reviews...</p>}>              {/* page streams without waiting */}
        <ReviewsWidget />
      </Suspense>
    </main>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Optimizing without measuring (adding `memo`/`useMemo` everywhere)
✅ **Correct:** Measure with React DevTools Profiler first, then fix the real bottleneck

```jsx
// Wrong: wrapping cheap things "just in case" adds comparison cost and complexity
const label = useMemo(() => 'Hello ' + name, [name]);              // ❌ string concat is already cheap
// Right: do nothing here; profile and optimize only slow components
const label = 'Hello ' + name;                                     // ✅
```

❌ **Mistake 2:** Defining objects/functions inline and passing them to memoized children
✅ **Correct:** Keep references stable (`useCallback`, `useMemo`) or move constants outside the component

```jsx
// Wrong: style is a new object every render, so memo(Child) never skips
<Child style={{ margin: 8 }} />
// Right: constant defined once at module level
const childStyle = { margin: 8 };
<Child style={childStyle} />
```

❌ **Mistake 3:** Putting everything in one global Context whose value changes often
✅ **Correct:** Split contexts (state vs actions), memoize the value, or use a selector-based store (Zustand, Redux)

```jsx
// Wrong: every consumer re-renders when ANY field changes
<AppContext.Provider value={{ user, cart, theme, setCart }}>{children}</AppContext.Provider>
// Right: separate providers by change frequency
<ThemeContext.Provider value={theme}><CartContext.Provider value={cart}>{children}</CartContext.Provider></ThemeContext.Provider>
```

---

## 🧠 Tricky Interview Question

```jsx
const Child = memo(function Child({ onClick }) {
  console.log('Child render');
  return <button onClick={onClick}>Go</button>;
});

function Parent() {
  const [n, setN] = useState(0);
  const handle = () => console.log('clicked');     // new function every render
  return (<><button onClick={() => setN(n + 1)}>{n}</button><Child onClick={handle} /></>);
}
// Click the counter button 3 times. How many times does "Child render" print?
```
**Answer:** Four times: once on mount and once for each of the 3 clicks. `memo` compares props shallowly with `Object.is`. `handle` is a new function object on every `Parent` render, so `onClick` always looks "changed" and `memo` never skips. Wrapping `handle` in `useCallback(() => ..., [])` would stop the re-renders (only the first mount render would print). This is why unstable props are one of the top performance causes, and why `memo` alone is not enough.

---

## ⚫ Interview Questions + Answers

Q1: What causes a React component to re-render?
A1: Its own state changes, its parent re-renders (by default all children re-render, even with the same props), or a context it consumes changes. Props changing is NOT required for a re-render, which is why `memo` exists.

Q2: What are the most common React performance problems?
A2: Unnecessary re-renders, expensive calculations inside render, unstable props, huge lists rendered at once, large bundles, bad state placement or over-broad context, and too many effects doing network calls. Always confirm with the Profiler.

Q3: How do you find the cause of a slow component?
A3: Use React DevTools Profiler to record an interaction, check which components rendered and why (enable "Record why each component rendered"), look at render durations, and use browser Performance tab and Lighthouse for loading issues. Then fix and measure again.

Q4: What is the cheapest optimization with the biggest effect?
A4: Moving state closer to where it is used (state colocation) and splitting a big component into smaller ones, so only a small part re-renders. It needs no hooks and has no extra cost. Next in order: `memo`, `useMemo`/`useCallback`, virtualization, code splitting.

Q5: Does the Virtual DOM make React fast automatically?
A5: The Virtual DOM reduces DOM writes by diffing, but rendering components and diffing still cost CPU time. React is fast enough by default for most apps, but a slow render function, thousands of nodes or too many re-renders can still cause lag. React Compiler (React 19, opt-in, version-dependent) can auto-memoize some of this.

---

## 🔷 When to Use + When Not to Use
✅ **Optimize when:**
- Users can feel lag (typing delay, slow scroll, long clicks)
- The Profiler shows a component taking many milliseconds or rendering too often
- Lighthouse/Web Vitals (LCP, INP) fail on real devices

❌ **Do not optimize when:**
- The app already feels fast on a mid-range phone
- You have no measurement showing a problem
- The change makes code harder to read for a tiny gain

---

## 📊 Visual Diagram

```
 Typing in the search box (state in PARENT):

   Parent (state: text) ─ re-renders
     ├─ <input>          ─ re-renders (needed)
     ├─ <Header/>        ─ re-renders (wasted)
     ├─ <Filters/>       ─ re-renders (wasted)
     └─ <Grid 500 cards> ─ 500 re-renders (VERY wasted)   → lag

 After moving state down + memo:

   Parent (no state)
     ├─ <SearchBox> (state: text) ─ re-renders (needed)
     ├─ <Header/>        ─ skipped
     ├─ <Filters/>       ─ skipped
     └─ <Grid memo>      ─ skipped                         → smooth

 Budget: 16 ms per frame for 60 fps (render + commit + paint)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Re-render | React calls the component again | React का component को दोबारा चलाना |
| Reconciliation | Diffing old and new element trees | पुराने और नए tree की तुलना |
| Unstable prop | Prop with a new reference each render | हर render नया reference वाला prop |
| State colocation | Keep state near where it is used | State को इस्तेमाल की जगह के पास रखना |
| Bundle size | Amount of JavaScript the user downloads | User द्वारा download किया गया JavaScript |
| Virtualization | Render only visible list items | सिर्फ़ दिखने वाले items render करना |
| Profiler | Tool that measures render time | Render का समय नापने वाला tool |
| INP / LCP | Web Vitals for responsiveness / loading | Responsiveness / loading के Web Vitals |

---

## ⚡ 3-Line Summary
**English:**
1. Most React slowness is unnecessary work: extra re-renders, heavy render logic, unstable props, huge lists and big bundles.
2. Fix in order: measure with Profiler, move state down, split components, then memoize, virtualize and code split.
3. Next.js helps with Server Components, dynamic imports, `next/image` and streaming with Suspense.

**Hindi:**
1. ज़्यादातर React धीमापन अनावश्यक काम से आता है: extra re-renders, भारी render logic, unstable props, विशाल lists और बड़े bundles।
2. क्रम से सुधारो: Profiler से measure, state नीचे ले जाओ, components बाँटो, फिर memoize, virtualize और code split करो।
3. Next.js Server Components, dynamic imports, `next/image` और Suspense streaming से मदद करता है।

---

## ➡️ Next Topic
**122. React.memo — Prevent Re-renders** — सबसे पहला optimization tool: `memo` से component तब तक दोबारा render नहीं होता जब तक उसके props सच में न बदलें।
