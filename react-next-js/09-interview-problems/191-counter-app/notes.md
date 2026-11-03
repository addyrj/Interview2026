# 191. Build Counter App (useState)
# हिंदी में: Counter App बनाना (useState के साथ)

Code: [`App.jsx`](./App.jsx) in this folder (complete, runs as-is in Vite / CRA / a Next.js Client Component with `'use client'` on top).

---

## 🔵 Simple Definition (English)
The Counter App is the classic first interview problem: show a number, and let the user increase, decrease and reset it using `useState`. Good answers also add limits (min/max), a custom step, and use functional updates.

## 🔵 सरल परिभाषा (Hindi)
Counter App interview का सबसे पहला classic problem है: एक number दिखाओ और user को `useState` से उसे बढ़ाने, घटाने और reset करने दो। अच्छे जवाब में limits (min/max), custom step और functional updates भी होते हैं।

---

## 🔴 Problem it Solves

Interviewers use this tiny problem to check the basics: Do you know that a normal variable does not trigger a re-render? Do you use the functional form `setCount(c => c + 1)` when the next value depends on the previous one? Do you handle edge cases (limits, invalid input)? Mistakes here show weak fundamentals.

```jsx
// PROBLEM: a plain variable never updates the screen
function Counter() {
  let count = 0;                                 // reset to 0 on every render
  return <button onClick={() => { count++; console.log(count); }}>{count}</button>;
  // The console shows 1, 2, 3 but the screen always shows 0
}
```

## 🔴 यह क्यों बना? (Hindi)
Interviewer इस छोटे problem से basics जाँचते हैं: क्या आपको पता है कि सामान्य variable re-render नहीं करता? क्या आप अगला value पिछले पर निर्भर हो तो `setCount(c => c + 1)` वाला functional form इस्तेमाल करते हैं? क्या आप edge cases (limits, गलत input) संभालते हैं? यहाँ की गलतियाँ कमज़ोर fundamentals दिखाती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → State: const [count, setCount] = useState(0) stores the number
Step 2 → Render: the component returns JSX showing {count}
Step 3 → Click: handler calls setCount(updaterFn)
Step 4 → React queues the update, re-runs Counter() with the new count
Step 5 → Limits: Math.min / Math.max keep count inside [MIN, MAX]; buttons disable at edges
Step 6 → Step input: a second state (controlled input) changes how much one click adds
Step 7 → Reset: setCount(0)

Approach to say in the interview: "State for count and step, functional updates,
clamp values, disable buttons at the limits, controlled number input."
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → State: const [count, setCount] = useState(0) number को रखता है
Step 2 → Render: component JSX return करता है जिसमें {count} दिखता है
Step 3 → Click: handler setCount(updaterFn) call करता है
Step 4 → React update को queue करता है और नए count के साथ Counter() दोबारा चलाता है
Step 5 → Limits: Math.min / Math.max count को [MIN, MAX] में रखते हैं; किनारों पर buttons disable
Step 6 → Step input: दूसरी state (controlled input) बदलती है कि एक click कितना जोड़े
Step 7 → Reset: setCount(0)

Interview में कहने का approach: "count और step की state, functional updates,
values clamp करना, limits पर buttons disable, controlled number input।"
```

---

## 🟡 Real World Example
**Amazon / Swiggy cart quantity selector:** the "- 1 +" control next to an item is exactly a counter. The minimum is 1 (or 0 to remove), the maximum is the available stock or a per-order limit (for example 10), and the "+" button is disabled at the limit. Same logic, same `useState`.

## 🟡 Real Example Hindi mein
**Amazon / Swiggy cart का quantity selector:** item के पास का "- 1 +" control बिल्कुल एक counter है। Minimum 1 (या हटाने के लिए 0) होता है, maximum उपलब्ध stock या प्रति order limit (जैसे 10), और limit पर "+" button disable हो जाता है। वही logic, वही `useState`।

---

## 💻 Code Example — Basic

```jsx
// Smallest correct counter (works in React 18/19)
import { useState } from 'react';                    // hook for local state

export default function Counter() {
  const [count, setCount] = useState(0);             // count starts at 0
  return (
    <div>
      <h1>{count}</h1>                                {/* shows the current value */}
      <button onClick={() => setCount((c) => c - 1)}>-</button>  {/* functional update */}
      <button onClick={() => setCount(0)}>Reset</button>         {/* back to 0 */}
      <button onClick={() => setCount((c) => c + 1)}>+</button>  {/* functional update */}
    </div>
  );
}
```

## 💻 Code Example — Advanced

The full solution is in [`App.jsx`](./App.jsx). The important part:

```jsx
// Excerpt from App.jsx: limits, custom step, disabled buttons
const MIN = -10;                                         // lower limit
const MAX = 10;                                          // upper limit
const [count, setCount] = useState(0);                   // current value
const [step, setStep] = useState(1);                     // click size

// Functional updates are safe even if several updates are batched together
const increment = () => setCount((c) => Math.min(MAX, c + step)); // clamp at MAX
const decrement = () => setCount((c) => Math.max(MIN, c - step)); // clamp at MIN

<button onClick={decrement} disabled={count <= MIN}>-</button>    // UI also blocks the edge
<input
  type="number" min="1" value={step}                              // controlled input
  onChange={(e) => setStep(Math.max(1, Number(e.target.value) || 1))} // never below 1, never NaN
/>
```

Verified: with a jsdom + react-dom test, two "+" clicks show 2, 15 clicks stop at 10 with "+" disabled, and Reset returns to 0.

---

## 🟠 Next.js Connection

In the App Router, a component with `useState` or `onClick` must be a **Client Component**. The page itself can stay a Server Component and import the counter.

```jsx
// app/counter/Counter.jsx
'use client';                                            // required: uses state and events
import App from '@/components/CounterApp';               // the App.jsx code, moved to components/
export default App;
```

```jsx
// app/counter/page.jsx (Server Component by default)
import Counter from './Counter';

export const metadata = { title: 'Counter' };            // SEO handled on the server

export default function Page() {
  return <Counter />;                                    // only the counter ships JS to the browser
}
```
Tip: if the initial count came from the server (for example a saved cart quantity), pass it as a prop: `useState(initialCount)`.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Calling the setter several times with the same stale value
✅ **Correct:** Use the functional form so each update sees the latest value.

```jsx
// Wrong: all three calls read the SAME count, final result is +1
const addThree = () => { setCount(count + 1); setCount(count + 1); setCount(count + 1); }; // ❌

// Right: result is +3
const addThree = () => { setCount((c) => c + 1); setCount((c) => c + 1); setCount((c) => c + 1); }; // ✅
```

❌ **Mistake 2:** Mutating state or using a plain variable
✅ **Correct:** Always call the setter; never `count++` on the state value.

```jsx
// Wrong: no re-render, and breaks the rules of React
count++;                                                 // ❌ count is const → TypeError, or no update
// Right
setCount((c) => c + 1);                                  // ✅
```

❌ **Mistake 3:** Forgetting input edge cases (`''`, `NaN`, negative step)
✅ **Correct:** Convert and validate: `Number(value) || 1`, `Math.max(1, ...)`.

```jsx
// Wrong: typing an empty box makes step = 0 or NaN, so the counter freezes or shows NaN
onChange={(e) => setStep(e.target.value)}                // ❌ also stores a string, "1" + 1 = "11"

// Right
onChange={(e) => setStep(Math.max(1, Number(e.target.value) || 1))} // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
function App() {
  const [count, setCount] = useState(0);
  const handle = () => {
    setCount(count + 1);          // A
    setCount(count + 1);          // B
    setCount((c) => c + 1);       // C
    console.log(count);           // D
  };
  return <button onClick={handle}>{count}</button>;
}
// After ONE click: what does the console show, what does the button show,
// and how many renders happen?
```
**Answer:** The console prints `0` (D), the button shows `2`, and there is **one** re-render. `count` inside `handle` is the value from this render (0), so A queues "set to 1" and B queues "set to 1" again. C queues an updater: `c => c + 1`. React processes the queue in order: 0 → 1 → 1 → 2. React 18 batches all three updates into a single render, and state does not change inside the running handler, which is why `console.log(count)` still prints 0.

---

## ⚫ Interview Questions + Answers

Q1: Why use `setCount(c => c + 1)` instead of `setCount(count + 1)`?
A1: The functional form receives the latest queued state, so it is correct when several updates are batched, when called in async callbacks, intervals or effects where `count` may be stale. It also lets you omit `count` from dependency arrays.

Q2: What re-renders when you click "+"?
A2: The `App` component and all children that are not memoised. State lives in `App`, so React re-runs the function, compares the new JSX with the old one and updates only the changed DOM text node (the `<h1>`). If the counter is small and isolated, this is cheap.

Q3: How do you prevent the count from going below zero?
A3: Clamp in the update (`Math.max(0, c - step)`) and disable the button (`disabled={count <= 0}`). The first protects logic (also from keyboard/other callers), the second helps the user.

Q4: Where should `step` live: its own state, or derived?
A4: It is user input, so it needs its own state (controlled input). `count` after clicks is state too. Things you can compute (for example `isMax = count >= MAX`) should be derived during render and not stored.

Q5: How would you make the counter persist after refresh?
A5: Initialise from `localStorage` with lazy init (`useState(() => Number(localStorage.getItem('count')) || 0)`) and save in a `useEffect([count])`. In Next.js guard against SSR (`localStorage` does not exist on the server) by reading in an effect or using a custom hook (topic 205).

---

## 🔷 When to Use + When Not to Use
✅ **Use `useState` for a counter when:**
- The value is local to one component (quantity picker, like button count)
- Updates are simple and synchronous

❌ **Avoid when:**
- Many fields change together with complex rules (use `useReducer`)
- The value must be shared by distant components or persisted (Context, Zustand, Redux, URL state)

---

## 📊 Visual Diagram

```
   click "+"
      │
      ▼
  setCount(c => min(MAX, c + step))
      │  (queued; batched with other updates)
      ▼
  React re-runs App()  ──▶  new JSX  ──▶  diff  ──▶  DOM: <h1> text updated only
      │
      └─ count = 10 → "+" gets disabled=true on this render

  State: count, step         Derived: disabled flags
  Re-renders: 1 per click (batched)     Cost: negligible
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| State | Data that triggers re-render when changed | वह data जो बदलने पर re-render कराता है |
| Functional update | `setX(prev => next)` form | पिछले value पर आधारित update |
| Batching | Grouping several updates into one render | कई updates को एक render में जोड़ना |
| Controlled input | Input whose value comes from state | State से value लेने वाला input |
| Clamp | Keep a number within min and max | Number को min-max में रखना |
| Derived state | Value computed from other state | दूसरी state से निकाला गया value |
| Re-render | Running the component function again | Component function का दोबारा चलना |
| Stale closure | Old value captured by a callback | Callback में फँसा पुराना value |

---

## ⚡ 3-Line Summary
**English:**
1. A counter stores a number in `useState`, and buttons update it with functional updates.
2. Clamp values to min/max, disable buttons at the edges, and validate the step input.
3. In Next.js it must be a Client Component (`'use client'`), while the page can stay on the server.

**Hindi:**
1. Counter `useState` में number रखता है और buttons functional updates से उसे बदलते हैं।
2. Values को min/max में clamp करो, किनारों पर buttons disable करो और step input validate करो।
3. Next.js में यह Client Component (`'use client'`) होना चाहिए, जबकि page server पर रह सकता है।

---

## ➡️ Next Topic
**192. Build Todo App (CRUD)** — अब एक से ज़्यादा items की list: add, edit, delete, toggle और filter, जिसमें arrays की immutable state updates सीखने को मिलती हैं।
