# 6. React Fiber Architecture
# हिंदी में: React Fiber Architecture — काम को टुकड़ों में बाँटने वाला engine

---

## 🔵 Simple Definition (English)
**Fiber** is the rewrite of React's reconciliation engine (shipped in React 16). It represents each component as a small unit of work (a "fiber" object), so React can pause, resume, prioritize or throw away rendering work. This is what makes concurrent features in React 18 possible.

## 🔵 सरल परिभाषा (Hindi)
**Fiber** React के reconciliation engine का rewrite है (React 16 में आया)। यह हर component को काम की छोटी इकाई ("fiber" object) की तरह दिखाता है, ताकि React rendering का काम रोक सके, दोबारा शुरू कर सके, priority दे सके या छोड़ सके। इसी वजह से React 18 के concurrent features संभव हुए।

---

## 🔴 Problem it Solves

Before React 16, the "Stack reconciler" rendered the whole tree in one synchronous recursive pass. A large update (for example filtering 10,000 products) blocked the main thread. The browser could not respond to typing or clicks until the work finished, so the page felt frozen and animations dropped frames.

```
Old (Stack reconciler):   [=========== one long render, cannot stop ===========]
                          typing, clicks, animation → all WAIT → UI feels frozen

New (Fiber):              [render a bit][check urgent input][render a bit][commit]
                          urgent work (typing) can go first, big work yields
```

## 🔴 यह क्यों बना? (Hindi)
React 16 से पहले "Stack reconciler" पूरे tree को एक ही synchronous recursive pass में render करता था। बड़े update (जैसे 10,000 products filter करना) से main thread block हो जाता था। जब तक काम खत्म न हो, browser typing या clicks का जवाब नहीं दे पाता था, इसलिए page अटका हुआ लगता था और animations के frames गिर जाते थे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Every element in the tree gets a FIBER: a JS object with
         type, props, state, and links: child, sibling, return (parent)
Step 2 → Two trees exist: "current" (on screen) and "work-in-progress" (being built)
Step 3 → RENDER phase (interruptible in concurrent mode, pure, no side effects):
         walk the fibers one by one (beginWork down, completeWork up), build the new tree
Step 4 → After each small unit, the scheduler asks: "is something more urgent waiting?"
         If yes → pause and yield to the browser; resume later (or restart)
Step 5 → COMMIT phase (synchronous, cannot be interrupted):
         apply DOM changes, run layout effects, swap work-in-progress → current
Step 6 → Passive effects (useEffect) run after paint; lanes (priorities) decide what goes first
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Tree के हर element को एक FIBER मिलता है: JS object जिसमें
         type, props, state, और links: child, sibling, return (parent)
Step 2 → दो trees होते हैं: "current" (screen पर) और "work-in-progress" (बन रहा)
Step 3 → RENDER phase (concurrent mode में interruptible, pure, side effects नहीं):
         fibers पर एक-एक करके चलो (नीचे beginWork, ऊपर completeWork), नया tree बनाओ
Step 4 → हर छोटी इकाई के बाद scheduler पूछता है: "क्या कुछ ज़्यादा urgent इंतज़ार में है?"
         हाँ तो → रुको और browser को मौका दो; बाद में resume (या restart)
Step 5 → COMMIT phase (synchronous, रोका नहीं जा सकता):
         DOM changes लगाओ, layout effects चलाओ, work-in-progress → current swap
Step 6 → Passive effects (useEffect) paint के बाद चलते हैं; lanes (priorities) तय करती हैं कि पहले क्या जाए
```

---

## 🟡 Real World Example
**Zomato search with 5,000 restaurants:** The user types "pizza". Updating the input box must feel instant, but filtering and re-rendering the 5,000 cards is heavy. With Fiber and `useTransition`, React treats the typing as urgent and the list update as a transition. While the user keeps typing, React can pause the heavy list render, show the latest text in the input, and restart the list work with the newest query. Result: the input never lags.

## 🟡 Real Example Hindi mein
**5,000 restaurants वाला Zomato search:** User "pizza" टाइप करता है। Input box का update तुरंत दिखना चाहिए, लेकिन 5,000 cards को filter और re-render करना भारी काम है। Fiber और `useTransition` के साथ React typing को urgent और list update को transition मानता है। User टाइप करता रहे तो React भारी list render को रोक सकता है, input में ताज़ा text दिखा सकता है, और नई query के साथ list का काम फिर शुरू करता है। नतीजा: input कभी lag नहीं करता।

---

## 💻 Code Example — Basic

A simplified model of a fiber node and the work loop. This is NOT React's real source, only a teaching sketch to show `child`, `sibling`, `return` and the pausable loop.

```jsx
// Teaching sketch: a fiber is a plain object linked like a tree + linked list
function createFiber(type, props) {
  return {
    type,                    // 'div', or a component function
    props,                   // props passed in
    child: null,             // first child fiber
    sibling: null,           // next sibling fiber
    return: null,            // parent fiber
  };
}

// Build a tiny tree:  App → [Header, List]
const app = createFiber('App', {});
const header = createFiber('Header', {});
const list = createFiber('List', {});
app.child = header;          // App's first child
header.sibling = list;       // Header's next sibling
header.return = app;         // parent link
list.return = app;           // parent link

// Process ONE unit of work and return the next unit (child → sibling → parent's sibling)
function performUnitOfWork(fiber, log) {
  log.push(`beginWork ${fiber.type}`);          // "render" this component
  if (fiber.child) return fiber.child;          // go down first
  let node = fiber;
  while (node) {
    log.push(`completeWork ${node.type}`);      // finish this node
    if (node.sibling) return node.sibling;      // then go sideways
    node = node.return;                         // else climb up
  }
  return null;                                  // reached the root: done
}

// The loop can STOP after any unit because the "next unit" is just a variable
function workLoop(root, shouldYield) {
  const log = [];
  let next = root;
  while (next && !shouldYield()) {              // check for urgent work after each unit
    next = performUnitOfWork(next, log);        // do one unit
  }
  return { log, next };                         // `next` is where we resume later
}

console.log(workLoop(app, () => false).log);    // full pass
// ['beginWork App','beginWork Header','completeWork Header','beginWork List','completeWork List','completeWork App']
```

## 💻 Code Example — Advanced

Using the Fiber-powered concurrent features in a real search UI: `useTransition` marks the list update as non-urgent, so typing stays smooth.

```jsx
// Concurrent rendering in action (React 18/19): urgent input vs deferred heavy list
import { useState, useTransition, memo } from 'react';        // concurrent APIs
import { createRoot } from 'react-dom/client';                // React 18/19 root

// Fake big dataset: 5000 restaurants
const ALL = Array.from({ length: 5000 }, (_, i) => ({ id: i, name: `Restaurant ${i}` }));

// A deliberately heavy row (memo so unchanged rows are skipped)
const Row = memo(function Row({ name }) {
  let x = 0;                                                  // simulate slow render work
  for (let i = 0; i < 2000; i++) x += i;                      // busy loop (demo only)
  return <li>{name} {x > 0 ? '' : '!'}</li>;                  // cheap output
});

function Search() {
  const [text, setText] = useState('');                       // urgent: what the input shows
  const [query, setQuery] = useState('');                     // deferred: what the list filters by
  const [isPending, startTransition] = useTransition();       // transition control + pending flag

  function handleChange(e) {
    setText(e.target.value);                                  // urgent update: input stays instant
    startTransition(() => {                                   // low priority lane
      setQuery(e.target.value);                               // React may pause/restart this render
    });
  }

  const results = ALL.filter((r) => r.name.includes(query)); // heavy derived list (demo)

  return (
    <div>
      <input value={text} onChange={handleChange} placeholder="Search" />
      {isPending && <p>Updating list...</p>}                  {/* feedback while transition pending */}
      <ul style={{ opacity: isPending ? 0.6 : 1 }}>
        {results.slice(0, 200).map((r) => <Row key={r.id} name={r.name} />)}
      </ul>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Search />);
```

**Re-render behavior:** typing triggers two renders: one urgent (input text) that commits immediately, and one transition (list) that Fiber can interrupt if another keystroke arrives. Interrupted transition renders are discarded and restarted with the latest value. **Performance impact:** total work may be the same or slightly more, but perceived responsiveness improves a lot because urgent updates are never blocked. Render-phase code must be pure, because it can run more than once.

---

## 🟠 Next.js Connection
Next.js App Router is built on React 18/19 concurrent features. `Suspense` boundaries and `loading.jsx` let the server stream HTML in chunks, and during client navigation Next.js wraps route changes in transitions, so the old page stays interactive while the new one renders. Selective hydration (a Fiber-era feature) lets React hydrate the part the user clicks first.

```jsx
// app/products/page.jsx (Server Component)
import { Suspense } from 'react';                           // boundary: show fallback while loading
import Reviews from './Reviews';                            // slow async Server Component

export default function ProductPage() {
  return (
    <main>
      <h1>Wireless Mouse</h1>                               {/* fast content streams first */}
      <Suspense fallback={<p>Loading reviews...</p>}>       {/* slow part streams in later */}
        <Reviews />
      </Suspense>
    </main>
  );
}
```

```jsx
// app/products/Reviews.jsx
export default async function Reviews() {
  await new Promise((r) => setTimeout(r, 2000));            // simulate slow database call
  return <ul><li>Great mouse, 5 stars</li></ul>;            // streamed when ready
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Putting side effects (API calls, mutations) in the render body
✅ **Correct:** Render must be pure; put side effects in event handlers or `useEffect`, because Fiber may run render multiple times or discard it

```jsx
// Wrong: runs on every render, and maybe twice or more in concurrent mode / StrictMode
function Cart() {
  fetch('/api/track-view', { method: 'POST' });       // ❌ side effect in render
  return <p>Cart</p>;
}

// Right: effect runs after commit
import { useEffect } from 'react';
function CartOk() {
  useEffect(() => { fetch('/api/track-view', { method: 'POST' }); }, []); // ✅
  return <p>Cart</p>;
}
```

❌ **Mistake 2:** Thinking Fiber makes every app faster automatically
✅ **Correct:** Fiber enables scheduling; you must still use transitions/Suspense and avoid wasteful renders

```jsx
// Wrong: heavy update done as urgent → still blocks typing feel
setQuery(value);

// Right: mark non-urgent work
startTransition(() => setQuery(value));
```

❌ **Mistake 3:** Mutating variables outside the component during render
✅ **Correct:** Keep render free of external mutation; derive from props and state

```jsx
// Wrong: module-level counter changes during render, breaks with double render
let renders = 0;
function Bad() { renders++; return <p>{renders}</p>; }   // ❌ unpredictable

// Right: local derived value
function Good({ n }) { return <p>{n}</p>; }              // ✅ same input, same output
```

---

## 🧠 Tricky Interview Question

```jsx
import { StrictMode, useState } from 'react';
import { createRoot } from 'react-dom/client';

let log = [];                                      // module-level array

function App() {
  const [n, setN] = useState(0);
  log.push('render ' + n);                         // side effect in render
  return <button onClick={() => setN(n + 1)}>{n}</button>;
}

createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>);
// What does log contain after the first mount in development?
```
**Answer:** In development, `StrictMode` intentionally renders each component twice to help find impure render code, so `log` is `['render 0', 'render 0']` (production renders once). This double invocation mirrors what Fiber's concurrent mode may do: React is allowed to start, throw away and restart renders. Therefore render logic must be pure and idempotent. How the second render's `console.log` output is shown (silenced, dimmed or normal) depends on the React version and DevTools settings, so treat that as version-dependent.

---

## ⚫ Interview Questions + Answers

Q1: What is React Fiber?
A1: Fiber is the reimplementation of React's core reconciliation algorithm in React 16. Each component instance has a fiber object holding its type, props, state and pointers to child, sibling and parent. It splits rendering into small units, so React can pause, resume, prioritize and abort work.

Q2: What are the two phases of rendering?
A2: The **render phase** computes what changed (it can be paused, restarted or aborted in concurrent mode, and must be pure). The **commit phase** applies DOM changes and runs layout effects synchronously, and cannot be interrupted. `useEffect` callbacks run after paint.

Q3: What is the difference between the "current" and "work-in-progress" trees?
A3: The current tree is what is on screen. React builds a work-in-progress tree by reusing and updating fibers (double buffering). When the commit finishes, the work-in-progress tree becomes the current one, so a half-finished render never shows on screen.

Q4: How does Fiber enable features like `useTransition` and Suspense?
A4: Because work is chunked and prioritized (lanes), React can render a low-priority update in the background, interrupt it for a high-priority one like typing, and show fallbacks while data loads. Without Fiber these features would block the main thread.

Q5: Does Fiber change how I write components?
A5: Mostly no; the API stays the same. The important rule is that render must be pure, with no side effects, because React may call it more than once or discard a render. Side effects belong in event handlers and effects.

---

## 🔷 When to Use + When Not to Use
✅ **Use Fiber-powered features (`useTransition`, `useDeferredValue`, Suspense) when:**
- A heavy list, chart or search result update makes typing or clicking laggy
- You want fallbacks and streaming while data loads
- You need smoother navigation where the old UI stays responsive

❌ **Avoid / not needed when:**
- The update is tiny; adding transitions only adds complexity
- The slowness is from network or an expensive calculation you can memoize or move to a worker
- You expect it to speed up synchronous code (it only schedules, it does not make functions faster)

---

## 📊 Visual Diagram

```
  FIBER TREE (linked list style)              TWO TREES

        App                                  current  ──►  on screen
         │ child                             work-in-progress ──► being built
         ▼                                          │ commit
       Header ──sibling──► List                     ▼
         ▲                  │ child             swap: WIP becomes current
         │ return           ▼
         └────────────────► Row ──sibling──► Row

  RENDER (pausable)                    COMMIT (not pausable)
  ┌─────┬─────┬─────┬─────┐           ┌──────────────────────┐
  │unit │unit │yield│unit │  ───────► │ DOM updates + layout │ ──► paint ──► useEffect
  └─────┴─────┴──▲──┴─────┘           └──────────────────────┘
                 │ urgent input (typing) goes first
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fiber | Unit of work / node in React's internal tree | काम की इकाई / React के internal tree का node |
| Reconciler | Part of React that decides what changed | React का वह हिस्सा जो बदलाव तय करता है |
| Render phase | Pure phase computing the new tree | नया tree निकालने वाला pure चरण |
| Commit phase | Synchronous phase applying DOM changes | DOM बदलाव लगाने वाला synchronous चरण |
| Work-in-progress | Tree being built off-screen | Screen के बाहर बन रहा tree |
| Lanes | Priority levels for updates | Updates की priority levels |
| Concurrent rendering | Interruptible rendering | रोका जा सकने वाला rendering |
| Time slicing | Splitting render work into small chunks | Render काम को छोटे टुकड़ों में बाँटना |

---

## ⚡ 3-Line Summary
**English:**
1. Fiber is React's engine that turns each component into a small, linkable unit of work.
2. Render phase can pause or restart; commit phase is synchronous and applies the DOM changes.
3. This enables `useTransition`, Suspense and streaming, but render must stay pure.

**Hindi:**
1. Fiber React का engine है जो हर component को काम की छोटी, जुड़ी हुई इकाई बनाता है।
2. Render phase रुक या restart हो सकता है; commit phase synchronous है और DOM बदलाव लगाता है।
3. इससे `useTransition`, Suspense और streaming संभव होते हैं, लेकिन render pure रहना चाहिए।

---

## ➡️ Next Topic
**8. JSX Rules + Best Practices** — JSX कैसे लिखा जाता है, कौन से rules तोड़ने पर errors आते हैं (एक root, closing tags, className), और production code में JSX साफ़ कैसे रखें।
