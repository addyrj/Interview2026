# 57. Rules of Hooks — Why These Rules
# हिंदी में: Hooks के नियम — ये नियम क्यों हैं

---

## 🔵 Simple Definition (English)
The Rules of Hooks say: (1) call hooks only at the top level of a component or custom hook, never inside `if`, loops, nested functions or after an early `return`, and (2) call hooks only from React function components or custom hooks. React identifies each hook by its **call order**, so that order must be the same on every render.

## 🔵 सरल परिभाषा (Hindi)
Hooks के नियम: (1) hooks सिर्फ component या custom hook के top level पर बुलाओ, `if`, loop, nested function या early `return` के बाद कभी नहीं, और (2) hooks सिर्फ React function components या custom hooks से बुलाओ। React हर hook को उसके **call order** से पहचानता है, इसलिए हर render में order वही रहना चाहिए।

---

## 🔴 Problem it Solves

Function components have no instance, so React needs somewhere to keep `useState` values between renders. It does not use names (you never write `useState('count')`). It uses a list per component and matches hooks by position: first call, second call, third call. If a hook is skipped in one render, every later hook reads the wrong slot, and state gets mixed up. The rules guarantee a stable order.

```jsx
// PROBLEM: hook inside a condition → order changes between renders
function Cart({ loggedIn }) {
  if (loggedIn) {
    const [name, setName] = useState('Aditya');  // ❌ slot 1 exists only sometimes
  }
  const [items, setItems] = useState([]);         // slot 1 on some renders, slot 2 on others
}

// SOLUTION: always call hooks, put the condition INSIDE or AFTER them
function Cart2({ loggedIn }) {
  const [name, setName] = useState('Aditya');     // ✅ always slot 1
  const [items, setItems] = useState([]);         // ✅ always slot 2
  if (!loggedIn) return <p>Please log in</p>;     // early return AFTER all hooks
  return <p>{name}: {items.length}</p>;
}
```

## 🔴 यह क्यों बना? (Hindi)
Function components का कोई instance नहीं होता, इसलिए React को `useState` की values renders के बीच कहीं रखनी होती हैं। React नामों का इस्तेमाल नहीं करता (आप `useState('count')` नहीं लिखते)। वह हर component के लिए एक list रखता है और position से hooks match करता है: पहली call, दूसरी call, तीसरी call। अगर किसी render में कोई hook छूट गया तो बाद वाले सारे hooks गलत slot पढ़ते हैं और state आपस में मिल जाती है। नियम stable order की गारंटी देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → On first render React creates a "hooks list" for this component instance (a linked list on the fiber)
Step 2 → Each hook call appends one node: [useState #1] → [useEffect #2] → [useState #3]
Step 3 → On re-render React walks the SAME list from the start, one node per hook call
Step 4 → Call number N reads node number N (this is why order must not change)
Step 5 → If a hook is skipped, later calls shift by one and read the wrong node
Step 6 → React detects the mismatch in development: "Rendered more/fewer hooks than expected" or
         "React has detected a change in the order of Hooks"
Step 7 → The eslint-plugin-react-hooks rule (rules-of-hooks) catches this before you run the code
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले render में React इस component instance के लिए "hooks list" बनाता है (fiber पर linked list)
Step 2 → हर hook call एक node जोड़ती है: [useState #1] → [useEffect #2] → [useState #3]
Step 3 → Re-render में React वही list शुरू से चलता है, हर hook call पर एक node
Step 4 → N-वीं call N-वाँ node पढ़ती है (इसीलिए order नहीं बदलना चाहिए)
Step 5 → अगर कोई hook छूटा तो बाद वाली calls एक जगह खिसक जाती हैं और गलत node पढ़ती हैं
Step 6 → Development में React mismatch पकड़ता है: "Rendered more/fewer hooks than expected" या
         "React has detected a change in the order of Hooks"
Step 7 → eslint-plugin-react-hooks का rules-of-hooks rule code चलाने से पहले ही यह पकड़ लेता है
```

---

## 🟡 Real World Example
**Zomato order screen:** A developer writes `if (!order) return <Spinner />;` at the top of `OrderTracker`, and below it adds `useEffect(...)` to poll delivery status. On the first render `order` is `null`, so the effect hook is never called. When data arrives, the component calls one more hook than before and React throws "Rendered more hooks than during the previous render" and the screen crashes. The fix is simple: move all hooks above the early return.

## 🟡 Real Example Hindi mein
**Zomato order screen:** एक developer `OrderTracker` में सबसे ऊपर `if (!order) return <Spinner />;` लिखता है और उसके नीचे delivery status poll करने के लिए `useEffect(...)` डालता है। पहले render में `order` `null` है, इसलिए effect hook कभी बुलाया ही नहीं जाता। Data आने पर component पहले से एक hook ज़्यादा बुलाता है और React "Rendered more hooks than during the previous render" error देता है और screen crash हो जाती है। Fix आसान है: सारे hooks early return के ऊपर ले जाओ।

---

## 💻 Code Example — Basic

```jsx
// Basic: the same component, broken and fixed (run the broken one to see React's error)
import { useState, useEffect } from 'react';             // hooks used below
import { createRoot } from 'react-dom/client';           // React 18/19 root API

// ❌ BROKEN: useEffect sits after an early return, so hook count changes between renders
function BrokenTracker({ order }) {
  const [tick, setTick] = useState(0);                   // hook 1: always called
  if (!order) return <p>Loading...</p>;                  // early return BEFORE the next hook
  useEffect(() => {                                      // hook 2: only called when order exists
    const id = setInterval(() => setTick(t => t + 1), 1000); // poll every second
    return () => clearInterval(id);                      // cleanup
  }, []);
  return <p>{order.status} {tick}</p>;
}

// ✅ FIXED: all hooks first, conditions after
function Tracker({ order }) {
  const [tick, setTick] = useState(0);                   // hook 1: always called
  useEffect(() => {                                      // hook 2: always called
    if (!order) return;                                  // condition goes INSIDE the hook
    const id = setInterval(() => setTick(t => t + 1), 1000);
    return () => clearInterval(id);                      // cleanup
  }, [order]);                                           // re-run when order changes
  if (!order) return <p>Loading...</p>;                  // early return is safe now
  return <p>{order.status} {tick}</p>;
}

createRoot(document.getElementById('root')).render(<Tracker order={{ status: 'On the way' }} />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: how React tracks hooks, a tiny simulation, plus the right way to do conditional logic
import { useState } from 'react';
import { createRoot } from 'react-dom/client';

// --- Mini simulation of React's hook storage (educational, not real React code) ---
let hooks = [];            // slot array for ONE component
let cursor = 0;            // which slot the current hook call will use

function useMyState(initial) {
  const slot = cursor;                                   // remember my position (call order!)
  if (hooks[slot] === undefined) hooks[slot] = initial;  // first render: initialize the slot
  const setState = v => { hooks[slot] = v; render(); };  // setter writes to MY slot only
  cursor++;                                              // next hook call uses the next slot
  return [hooks[slot], setState];
}

function render() {
  cursor = 0;                                            // every render starts from slot 0
  const out = MyComponent();                             // run the component
  console.log(out);
}

function MyComponent() {
  const [a, setA] = useMyState('first');                 // slot 0
  const [b, setB] = useMyState('second');                // slot 1
  MyComponent.setA = setA;                               // expose setters for the demo
  return `${a} / ${b}`;
}
render();                                                // "first / second"
MyComponent.setA('changed');                             // "changed / second"
// If useMyState('first') were skipped once, 'second' would read slot 0 → wrong value

// --- Real component: conditional data without breaking the rules ---
import { useEffect } from 'react';
function Profile({ userId }) {
  const [user, setUser] = useState(null);                // always called
  const [error, setError] = useState(null);              // always called
  // ❌ Do NOT write:  if (userId) { useEffect(...) }
  // ✅ Put the condition inside:
  useEffect(() => {
    if (!userId) return;                                 // skip work, not the hook
    const ctrl = new AbortController();                  // allows cancel on cleanup
    fetch(`/api/users/${userId}`, { signal: ctrl.signal })
      .then(r => r.json()).then(setUser)
      .catch(e => { if (e.name !== 'AbortError') setError(e); });
    return () => ctrl.abort();                           // cancel stale request
  }, [userId]);
  if (error) return <p>Error</p>;
  return <p>{user ? user.name : 'Loading...'}</p>;
}
```

---

## 🟠 Next.js Connection

The same rules apply in Next.js, with one extra rule: hooks only work in **Client Components**. A Server Component (the default in the App Router) cannot use `useState`, `useEffect` and similar hooks, and Next.js shows an error telling you to add `'use client'`. Server Components can use `async/await` directly, and the hook `use()` (React 19) is an exception: it may be called inside conditions and loops, unlike other hooks. Also enable `eslint-config-next`, which already includes the `react-hooks` plugin.

```jsx
// app/orders/OrderTracker.jsx
'use client';                                        // hooks require a Client Component
import { useState, useEffect } from 'react';

export default function OrderTracker({ orderId }) {
  const [status, setStatus] = useState('loading');   // hooks at the top level, always
  useEffect(() => {
    let ignore = false;                              // avoids setting state after unmount
    fetch(`/api/orders/${orderId}`)
      .then(r => r.json())
      .then(d => { if (!ignore) setStatus(d.status); });
    return () => { ignore = true; };
  }, [orderId]);
  if (status === 'loading') return <p>Loading...</p>; // returns come AFTER hooks
  return <p>Order status: {status}</p>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Calling a hook inside a condition or after an early return
✅ **Correct:** Call all hooks first, then branch

```jsx
// Wrong
function A({ show }) {
  if (!show) return null;
  const [n, setN] = useState(0);        // ❌ skipped when show is false
  return <p>{n}</p>;
}
// Right
function B({ show }) {
  const [n, setN] = useState(0);        // ✅ always called
  if (!show) return null;
  return <p>{n}</p>;
}
```

❌ **Mistake 2:** Calling a hook inside a loop, callback or event handler
✅ **Correct:** Create one component per item and let each call its own hook

```jsx
// Wrong: number of hooks depends on items.length
function List({ items }) {
  return items.map(i => { const [v] = useState(i); return <li key={i}>{v}</li>; }); // ❌
}
// Right: each Row has exactly one useState
function Row({ item }) { const [v] = useState(item); return <li>{v}</li>; }          // ✅
function List2({ items }) { return items.map(i => <Row key={i} item={i} />); }
```

❌ **Mistake 3:** Calling hooks from regular functions or class components
✅ **Correct:** Call them from components or functions named `useXxx`

```jsx
// Wrong: regular function, lint error and runtime error
function getUser() { const [u] = useState(null); return u; }   // ❌
// Right: rename to a custom hook and call it only from components/hooks
function useUser() { const [u] = useState(null); return u; }   // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState } from 'react';

function App() {
  const [on, setOn] = useState(false);
  if (on) {
    const [x] = useState('hello');
  }
  return <button onClick={() => setOn(true)}>Click</button>;
}
```
**Answer:** The first render works (`on` is `false`, one hook called). After the click, `on` becomes `true` and the component calls `useState` twice, but React stored only one hook for it. In development React throws an error: "Rendered more hooks than during the previous render" (the exact wording is version-dependent). The component call order changed, so React cannot match hooks to slots. The ESLint rule `react-hooks/rules-of-hooks` flags this line before running. Fix: call `useState('hello')` unconditionally, or move it into a child component rendered conditionally.

---

## ⚫ Interview Questions + Answers

Q1: What are the Rules of Hooks?
A1: Call hooks only at the top level (not in conditions, loops, nested functions or after an early return), and only from React function components or custom hooks.

Q2: Why does React need the same call order?
A2: React stores hook state in an ordered list per component and has no names to identify hooks. The N-th hook call on every render reads the N-th slot. Changing the order makes calls read wrong slots.

Q3: How do you run an effect conditionally?
A3: Call `useEffect` always, and put the `if` inside the callback (or use the dependency array). Never put the hook call itself inside the `if`.

Q4: Can a custom hook call another custom hook? Can a normal function call a hook?
A4: A custom hook can call other hooks. A normal function (not named `use...`, not a component) must not call hooks. The `use` prefix helps the linter apply the rules.

Q5: Is there any hook that can be called conditionally?
A5: In React 19, `use(promiseOrContext)` can be called inside conditions and loops (but still only inside components or hooks). All other hooks must follow the order rule.

---

## 🔷 When to Use + When Not to Use
✅ **Follow these rules when:**
- Writing any component or custom hook (always, no exceptions)
- You have conditional logic: put conditions inside hooks or in child components
- You see "Rendered more hooks" errors: look for early returns above hooks

❌ **Do not try to work around them when:**
- You want a variable number of states (use one array/object state, or child components)
- You want a conditional hook (extract a child component and render it conditionally)

---

## 📊 Visual Diagram

```
  Render 1 (loggedIn = false)         Render 2 (loggedIn = true)   ← hook skipped before
  ─────────────────────────           ─────────────────────────
  call 1: useState(items)  → slot 0   call 1: useState(name)   → slot 0  ✗ reads items' slot!
  call 2: useEffect        → slot 1   call 2: useState(items)  → slot 1  ✗ reads effect's slot!
                                      call 3: useEffect        → slot 2  ✗ no slot exists

  Fiber hooks list:  [ slot 0 ] → [ slot 1 ] → [ slot 2 ] → null
                       ▲ matched by POSITION, never by name

  Correct: same calls in the same order on every render → slots always line up
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Top level | Not inside condition, loop or nested function | Condition, loop या nested function के बाहर |
| Call order | Sequence in which hooks are called | Hooks बुलाने का क्रम |
| Hooks list | Per-component ordered storage for hook state | हर component की hooks की क्रम वाली list |
| Fiber | React's internal unit of work per component | हर component के लिए React की internal unit |
| Early return | Returning before the end of the function | Function खत्म होने से पहले return |
| rules-of-hooks | ESLint rule that enforces the rules | नियम लागू करने वाला ESLint rule |
| Custom hook | `use...` function that calls other hooks | `use...` function जो दूसरे hooks बुलाता है |
| use() | React 19 API that may be called conditionally | React 19 का API जो condition में बुला सकते हैं |

---

## ⚡ 3-Line Summary
**English:**
1. Call hooks at the top level, in the same order on every render, only from components or custom hooks.
2. React matches hooks by call position in a list, so skipping one shifts all later hooks to wrong slots.
3. Put conditions inside hooks or in child components, and keep the `react-hooks` ESLint rule on.

**Hindi:**
1. Hooks को top level पर, हर render में उसी क्रम में, सिर्फ components या custom hooks से बुलाओ।
2. React hooks को list में call position से match करता है, इसलिए एक भी छूटा तो बाद वाले गलत slot पढ़ते हैं।
3. Conditions को hook के अंदर या child components में रखो, और `react-hooks` ESLint rule चालू रखो।

---

## ➡️ Next Topic
**58. Component Lifecycle (Class)** — Hooks section पूरा हुआ। अब Intermediate section शुरू करते हैं: class components के lifecycle methods (`componentDidMount`, `componentDidUpdate`, `componentWillUnmount`) और वे hooks से कैसे map होते हैं। पुराने codebases और interviews में यह अब भी पूछा जाता है।
