# 41. useRef vs useState
# हिंदी में: useRef बनाम useState — कब कौन सा इस्तेमाल करें

---

## 🔵 Simple Definition (English)
Both hooks remember a value between renders. **`useState`** stores data that shows on screen: changing it triggers a re-render. **`useRef`** stores a mutable value in `ref.current`: changing it does **not** re-render, so it is for things React does not need to display (timer ids, DOM nodes, previous values).

## 🔵 सरल परिभाषा (Hindi)
दोनों hooks renders के बीच value याद रखते हैं। **`useState`** वह data रखता है जो screen पर दिखता है: उसे बदलने पर re-render होता है। **`useRef`** `ref.current` में बदली जा सकने वाली value रखता है: उसे बदलने पर re-render **नहीं** होता, इसलिए यह उन चीज़ों के लिए है जो React को दिखानी नहीं हैं (timer id, DOM nodes, पिछली values)।

---

## 🔴 Problem it Solves

Developers needed a place to store values that survive re-renders. A plain `let` variable inside the component resets every render. Putting everything in `useState` causes extra re-renders for values that never affect the UI (like a `setInterval` id), which wastes performance. The reverse mistake, storing visible data in a ref, makes the UI stale because nothing re-renders.

```jsx
// PROBLEM 1: plain variable resets on every render
function Timer() {
  let id = null;                       // ❌ becomes null again after each render, cannot clear the timer
}

// PROBLEM 2: state for a hidden value → pointless re-render
const [timerId, setTimerId] = useState(null);   // ❌ setting it re-renders for nothing

// SOLUTION: ref for hidden values, state for visible values
const timerId = useRef(null);                   // ✅ persists, no re-render
const [seconds, setSeconds] = useState(0);      // ✅ shown on screen
```

## 🔴 यह क्यों बना? (Hindi)
Developers को ऐसी जगह चाहिए थी जहाँ value re-renders के बाद भी बची रहे। Component के अंदर साधारण `let` variable हर render में reset हो जाता है। सब कुछ `useState` में रखने से उन values के लिए भी extra re-render होते हैं जो UI को प्रभावित नहीं करतीं (जैसे `setInterval` की id), जिससे performance बर्बाद होती है। उल्टी गलती, दिखने वाला data ref में रखना, UI को पुराना छोड़ देती है क्योंकि कुछ re-render नहीं होता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → useState returns [value, setter]. Calling setter schedules a re-render with the new value
Step 2 → useRef returns { current: initial }, the SAME object on every render
Step 3 → Changing ref.current mutates that object directly: React is not notified, no re-render
Step 4 → State is a snapshot per render (immutable inside one render); ref.current is always the latest
Step 5 → Rule: if the value is used in JSX/return output → state. If not → ref
Step 6 → Never read or write ref.current during render (except lazy init); do it in handlers/effects

                 useState              useRef
  triggers re-render?   YES                  NO
  value readable        in render           in handlers/effects
  update is             async (batched)     immediate (sync)
  holds                 UI data             DOM nodes, ids, previous values
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → useState [value, setter] देता है। setter बुलाने पर नई value के साथ re-render schedule होता है
Step 2 → useRef { current: initial } देता है, हर render में वही SAME object
Step 3 → ref.current बदलना उस object को सीधे mutate करता है: React को खबर नहीं, re-render नहीं
Step 4 → State हर render का snapshot है (एक render के अंदर बदलता नहीं); ref.current हमेशा latest रहता है
Step 5 → नियम: value JSX/return में दिखती है → state। नहीं दिखती → ref
Step 6 → Render के दौरान ref.current कभी पढ़ो/लिखो मत (lazy init को छोड़कर); handlers/effects में करो

                 useState              useRef
  re-render?            हाँ                  नहीं
  value पढ़ना           render में           handlers/effects में
  update                async (batched)     तुरंत (sync)
  क्या रखता है          UI data             DOM nodes, ids, पिछली values
```

---

## 🟡 Real World Example
**Zomato order screen:** The "delivery ETA" countdown shown on screen is **state**, because the UI must update every second. The `setInterval` id used to stop that timer is a **ref**, since nobody sees it. The "Add instructions" textarea that must be focused when the user taps a button uses a ref to the DOM node. The number of times the user pressed "Retry payment", used only for analytics at the end, can be a ref as well, to avoid needless re-renders.

## 🟡 Real Example Hindi mein
**Zomato order screen:** Screen पर दिखने वाला "delivery ETA" countdown **state** है, क्योंकि UI हर सेकंड update होना चाहिए। उस timer को रोकने वाली `setInterval` की id **ref** है, क्योंकि उसे कोई नहीं देखता। "Add instructions" textarea जिसे बटन दबाने पर focus करना है, DOM node के ref से होता है। "Retry payment" कितनी बार दबा, जो सिर्फ़ आखिर में analytics के लिए चाहिए, उसे भी ref में रख सकते हैं ताकि बेवजह re-render न हों।

---

## 💻 Code Example — Basic

```jsx
// Same click counter with state vs ref: observe which one updates the screen
import { useState, useRef } from 'react';             // both hooks
import { createRoot } from 'react-dom/client';        // React 18/19 root API

function Compare() {
  const [stateCount, setStateCount] = useState(0);    // visible value → state
  const refCount = useRef(0);                         // hidden value → ref
  const renders = useRef(0);                          // counts renders, no re-render of itself
  renders.current += 1;                               // OK for demos (see rules: avoid in real code)

  return (
    <div>
      <p>Rendered {renders.current} times</p>
      <button onClick={() => setStateCount(c => c + 1)}>
        State: {stateCount}                           {/* updates screen: re-render happens */}
      </button>
      <button onClick={() => {
        refCount.current += 1;                        // mutate the ref
        console.log('ref is', refCount.current);      // value changes, but...
      }}>
        Ref (check console)                           {/* ...screen does NOT update */}
      </button>
      <p>Ref value on screen (stale until next re-render): {refCount.current}</p>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Compare />);
```

## 💻 Code Example — Advanced

```jsx
// Stopwatch: state for what is displayed, refs for timer id, start time and the input DOM node
import { useState, useRef, useEffect } from 'react';
import { createRoot } from 'react-dom/client';

function DeliveryTimer() {
  const [elapsed, setElapsed] = useState(0);          // shown on screen → STATE
  const [running, setRunning] = useState(false);      // controls button label → STATE
  const intervalId = useRef(null);                    // setInterval id → REF (never displayed)
  const startedAt = useRef(0);                        // timestamp base → REF
  const noteInput = useRef(null);                     // DOM node → REF
  const prevElapsed = useRef(0);                      // previous value → REF

  useEffect(() => {
    prevElapsed.current = elapsed;                    // runs AFTER render: safe place to write refs
  });                                                 // so during render it still holds the older value

  useEffect(() => () => clearInterval(intervalId.current), []); // clear on unmount to avoid a leak

  function start() {
    if (intervalId.current) return;                   // already running: ignore double click
    startedAt.current = Date.now() - elapsed * 1000;  // continue from the paused time
    intervalId.current = setInterval(() => {          // store the id in the ref
      setElapsed(Math.floor((Date.now() - startedAt.current) / 1000)); // state → re-render per second
    }, 1000);
    setRunning(true);                                 // state: button text changes
  }

  function stop() {
    clearInterval(intervalId.current);                // ref gives the latest id, no stale closure
    intervalId.current = null;                        // mark as stopped
    setRunning(false);
  }

  function reset() {
    stop();
    setElapsed(0);
    noteInput.current?.focus();                       // imperative DOM call: focus the input
  }

  return (
    <div>
      <h2>{elapsed}s</h2>
      <p>Previous render showed: {prevElapsed.current}s</p>
      <button onClick={running ? stop : start}>{running ? 'Pause' : 'Start'}</button>
      <button onClick={reset}>Reset</button>
      <input ref={noteInput} placeholder="Delivery note" />
    </div>
  );
}

createRoot(document.getElementById('root')).render(<DeliveryTimer />);
```

---

## 🟠 Next.js Connection

Both hooks only work in **Client Components** (`'use client'`). A Server Component cannot hold state or refs. A common Next.js pattern is: keep shareable UI state in the URL (`useSearchParams`) so it survives refresh and can be rendered by the server, and keep only transient things (focus, scroll position, timers) in refs. For hydration, never read `ref.current` during render to decide markup: the server has no refs, so it would mismatch.

```jsx
// app/checkout/NoteBox.jsx (Client Component)
'use client';
import { useRef, useState } from 'react';

export default function NoteBox() {
  const [note, setNote] = useState('');                 // visible text → state
  const textareaRef = useRef(null);                     // DOM access → ref

  function clear() {
    setNote('');                                        // update UI
    textareaRef.current?.focus();                       // refocus without re-render cost
  }

  return (
    <>
      <textarea ref={textareaRef} value={note} onChange={e => setNote(e.target.value)} />
      <button onClick={clear}>Clear</button>
    </>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using a ref for data that must appear on screen
✅ **Correct:** Use state, so React re-renders

```jsx
// Wrong: UI never updates
const count = useRef(0);
<button onClick={() => { count.current++; }}>{count.current}</button>   // ❌ stays 0 on screen

// Right
const [count, setCount] = useState(0);
<button onClick={() => setCount(c => c + 1)}>{count}</button>           // ✅
```

❌ **Mistake 2:** Using state for a timer id or other hidden value
✅ **Correct:** Use a ref (no re-render, and always the latest value)

```jsx
// Wrong: extra renders, and clearInterval in a stale closure may use null
const [id, setId] = useState(null);
// Right
const id2 = useRef(null);
id2.current = setInterval(tick, 1000);                // ✅ clearInterval(id2.current) later
```

❌ **Mistake 3:** Writing `ref.current` during render
✅ **Correct:** Write it in event handlers or effects

```jsx
// Wrong: render must be pure; in StrictMode/concurrent rendering this runs more than once
function Comp({ value }) {
  const last = useRef();
  last.current = value;                               // ❌ side effect during render
  return <p>{value}</p>;
}

// Right
function Comp2({ value }) {
  const last = useRef();
  useEffect(() => { last.current = value; });         // ✅ after render
  return <p>{value}</p>;
}
```

---

## 🧠 Tricky Interview Question

```jsx
function App() {
  const [count, setCount] = useState(0);
  const ref = useRef(0);

  function handle() {
    setCount(count + 1);
    ref.current = ref.current + 1;
    console.log('state:', count, 'ref:', ref.current);
  }

  return <button onClick={handle}>{count} / {ref.current}</button>;
}
```
**Answer:** First click logs `state: 0 ref: 1`. The screen then shows `1 / 1`. The state inside the handler is a snapshot from that render (`0`), while the ref is already updated (`1`). The re-render caused by `setCount` also shows the new ref value, so it looks in sync, but only because the state change forced a render. If you click and only the ref changed, the screen would not update. Second click logs `state: 1 ref: 2`.

---

## ⚫ Interview Questions + Answers

Q1: What is the main difference between `useRef` and `useState`?
A1: Updating state triggers a re-render and its value is a per-render snapshot. Updating `ref.current` does not trigger a re-render and is always the latest value. State is for data the UI shows; refs are an escape hatch for values React does not render.

Q2: When would you use a ref instead of state?
A2: For DOM nodes (focus, scroll, measure), timer or subscription ids, previous values, instance-like variables such as an `AbortController` or a "is mounted" flag, and any value that changes often but is not displayed.

Q3: Why shouldn't you read or write `ref.current` in render?
A3: Render must be pure. Refs are mutable and not tracked by React, so using them in render can make output depend on hidden state and break concurrent rendering and StrictMode. Use them in handlers and effects.

Q4: Does changing a ref cause an effect with `[ref.current]` to run?
A4: No, effects only run after a render. Changing a ref does not trigger a render, and `ref.current` in deps is only compared on a render caused by something else. Avoid it as a dependency.

Q5: Can a ref hold previous state?
A5: Yes. Update the ref in an effect after render. During the next render, reading it gives the previous value. This is the `usePrevious` custom hook pattern.

---

## 🔷 When to Use + When Not to Use
✅ **Use `useState` when:**
- The value appears in the rendered output
- A change must update the UI

✅ **Use `useRef` when:**
- You need a DOM node, timer id, previous value or any non-visual mutable value
- You want to avoid re-renders while still persisting the value

❌ **Avoid refs when:**
- You are using them to dodge proper state management for visible data
- You would read/write them during render

---

## 📊 Visual Diagram

```
 setState(x)                              ref.current = x
     │                                         │
     ▼                                         ▼
 schedule re-render ──► component runs    value changed silently
     │                      │                  │
     ▼                      ▼                  ▼
 new snapshot shown     JSX updated        screen unchanged
                                           (until something else re-renders)

 Re-render behavior : state → 1 re-render per change (batched); ref → 0 re-renders
 Performance        : many fast updates (mouse move, scroll, timers) → keep in a ref, flush to state rarely
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| State | Value that triggers re-render | Re-render कराने वाली value |
| Ref | Mutable box `{ current }` | बदली जा सकने वाली box `{ current }` |
| Snapshot | Value fixed for one render | एक render के लिए तय value |
| Mutation | Changing a value directly | Value को सीधे बदलना |
| Escape hatch | Way out of React's data flow | React के data flow से बाहर का रास्ता |
| DOM node | Real HTML element | असली HTML element |
| Pure render | Same input gives same output | वही input, वही output |

---

## ⚡ 3-Line Summary
**English:**
1. `useState` is for values shown on screen and re-renders on change; `useRef` is a mutable box that does not.
2. Use refs for DOM nodes, timer ids and previous values; use state for UI data.
3. Do not read or write refs during render, and do not hide visible data in refs.

**Hindi:**
1. `useState` screen पर दिखने वाली values के लिए है और बदलने पर re-render करता है; `useRef` बदली जा सकने वाली box है जो re-render नहीं करती।
2. DOM nodes, timer ids और पिछली values के लिए ref, UI data के लिए state।
3. Render के दौरान ref पढ़ो/लिखो मत, और दिखने वाला data ref में मत छिपाओ।

---

## 📚 Go Deeper — External Resources
| Type | Link | Why |
|------|------|-----|
| 📝 Article | [react.dev — Referencing Values with Refs](https://react.dev/learn/referencing-values-with-refs) | Official guide, ref vs state |
| 📝 Article | [react.dev — useRef](https://react.dev/reference/react/useRef) | API reference |

---

## ➡️ Next Topic
**42. useContext** (already covered) और फिर **43. Context API — Complete Guide** — state को पूरे component tree में बिना props के कैसे बाँटें, `createContext` और Provider के साथ।
