# 64. Render Props Pattern
# हिंदी में: Render Props Pattern — Function Prop से UI बनवाना

---

## 🔵 Simple Definition (English)
A **render prop** is a prop whose value is a **function** that returns React elements. The component that owns the data or behavior calls that function with its internal values, and the caller decides how to draw the UI. The function can be passed under any name, most often `render` or as `children`.

## 🔵 सरल परिभाषा (Hindi)
**Render prop** एक ऐसा prop है जिसकी value एक **function** होती है जो React elements लौटाता है। जो component data या behavior संभालता है, वह अपनी internal values के साथ यह function call करता है, और caller तय करता है कि UI कैसा दिखे। Function किसी भी नाम से दिया जा सकता है, ज़्यादातर `render` नाम से या `children` के रूप में।

---

## 🔴 Problem it Solves

Sometimes two components need the same logic (for example, tracking the mouse position or loading data), but each needs to draw something different. Copying the logic into every component duplicates code. Putting the logic in a shared component but hard-coding its UI makes it unusable elsewhere. Render props separate **what the data is** (the owner component) from **how it is shown** (the caller's function).

```jsx
// PROBLEM: the same loading logic is copied into two components
function UserCard()  { const [u, setU] = useState(null); /* fetch... */ return <p>{u?.name}</p>; }
function OrderCard() { const [o, setO] = useState(null); /* fetch... same code... */ return <p>{o?.id}</p>; }

// SOLUTION: one owner component, the caller draws the UI
<DataLoader url="/api/user" render={(data) => <p>{data.name}</p>} />
<DataLoader url="/api/order" render={(data) => <p>{data.id}</p>} />
```

## 🔴 यह क्यों बना? (Hindi)
कभी-कभी दो components को एक ही logic चाहिए (जैसे mouse position track करना या data load करना), पर दोनों को अलग UI बनाना है। Logic को हर component में copy करना duplication है। Logic को shared component में रखो पर UI hard-code करो, तो वह कहीं और काम नहीं आता। Render props दो चीज़ें अलग करते हैं: **data क्या है** (owner component) और **कैसे दिखाया जाए** (caller का function)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Owner component holds the data/state (for example, on/off, or loading status)
Step 2 → Owner receives a function prop:  render={fn}  (or children as a function)
Step 3 → Owner calls the function with its values:  render(value)  → returns JSX
Step 4 → React renders the returned JSX as part of the owner's output
Step 5 → Caller controls the UI by writing the function; the logic stays in the owner
Step 6 → When the owner's state changes, it calls the function again with new values

KEY: the function is called by the owner, not by the caller
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Owner component data/state रखता है (जैसे on/off, या loading status)
Step 2 → Owner एक function prop लेता है:  render={fn}  (या children के रूप में function)
Step 3 → Owner अपनी values के साथ function call करता है:  render(value)  → JSX लौटता है
Step 4 → React लौटाए JSX को owner के output का हिस्सा बनाकर render करता है
Step 5 → Caller function लिखकर UI नियंत्रित करता है; logic owner में ही रहता है
Step 6 → Owner का state बदले तो वह नई values के साथ function फिर से call करता है

KEY: function को owner call करता है, caller नहीं
```

---

## 🟡 Real World Example
**Razorpay payment status:** A `PaymentStatus` component polls the payment API and holds the status (`pending`, `success`, `failed`). A checkout page renders a green tick for success, a spinner for pending and a retry button for failed. An admin dashboard renders the same status as a table row. Both use the same polling logic from `PaymentStatus`, but each passes its own render function. The polling code is written once.

## 🟡 Real Example Hindi mein
**Razorpay payment status:** `PaymentStatus` component payment API को poll करता है और status (`pending`, `success`, `failed`) रखता है। Checkout page success पर हरा tick, pending पर spinner और failed पर retry बटन दिखाता है। Admin dashboard वही status table की row में दिखाता है। दोनों एक ही polling logic इस्तेमाल करते हैं, पर हर कोई अपना render function देता है। Polling का code एक ही बार लिखा गया है।

---

## 💻 Code Example — Basic

```jsx
// Render prop basics: the owner keeps the on/off state, the caller draws the UI
import { useState } from 'react';                // state hook used by the owner
import { createRoot } from 'react-dom/client';   // React 18/19 root API

function Toggle({ render }) {                    // owner: has the logic, not the UI
  const [on, setOn] = useState(false);           // internal state: is it on?
  const toggle = () => setOn(v => !v);           // function that flips the state
  return render({ on, toggle });                 // call the caller's function with the values
}

function App() {
  return (
    <div>
      <Toggle render={({ on, toggle }) => (     // caller decides how it looks
        <button onClick={toggle}>{on ? 'ON' : 'OFF'}</button> // button text depends on state
      )} />

      <Toggle render={({ on, toggle }) => (     // second usage: different UI, same logic
        <label>
          <input type="checkbox" checked={on} onChange={toggle} /> Notifications
        </label>
      )} />
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />); // render both toggles
```

## 💻 Code Example — Advanced

```jsx
// Production-style data loader: loading/error/data states, AbortController, children as a function
import { useState, useEffect } from 'react';     // hooks used by the owner
import { createRoot } from 'react-dom/client';   // React 18/19 root API

// Fake API like fetch(): resolves after a delay and respects an AbortSignal
function fakeApi(url, { signal }) {
  return new Promise((resolve, reject) => {
    const delay = url.length * 20;                // simulated network time
    const timer = setTimeout(() => {              // success after the delay
      if (url.includes('missing')) reject(new Error('404 not found')); // simulated failure
      else resolve({ id: url, name: `Data for ${url}` }); // simulated JSON
    }, delay);
    signal.addEventListener('abort', () => {      // called when the controller aborts
      clearTimeout(timer);                        // stop the pending response
      reject(new DOMException('Aborted', 'AbortError')); // reject like a real aborted fetch
    });
  });
}

// Owner: manages the request lifecycle and passes a status object to the caller's function
function DataLoader({ url, children }) {
  const [state, setState] = useState({ status: 'loading', data: null, error: null });

  useEffect(() => {                              // runs after mount and whenever url changes
    const controller = new AbortController();    // one controller per request
    setState({ status: 'loading', data: null, error: null }); // reset while loading

    fakeApi(url, { signal: controller.signal })  // start the request
      .then(data => setState({ status: 'success', data, error: null }))
      .catch(err => {                            // ignore aborts, store real errors
        if (err.name !== 'AbortError') {
          setState({ status: 'error', data: null, error: err.message });
        }
      });

    return () => controller.abort();             // cancel the stale request on change or unmount
  }, [url]);                                     // effect depends on url

  // "children" is a FUNCTION here: call it with the state, it returns the UI
  return typeof children === 'function'
    ? children(state)                            // render-prop style usage
    : null;                                      // safety: nothing to draw without a function
}

// Caller: draws three different UIs from the same owner
function Dashboard() {
  return (
    <div>
      {/* children is a function: DataLoader calls it with the state */}
      <DataLoader url="/api/users/aditya">
        {({ status, data, error }) => {          // destructure the state object
          if (status === 'loading') return <p>Loading user…</p>;   // spinner text
          if (status === 'error') return <p>Could not load: {error}</p>; // error text
          return <p>User: {data.name}</p>;       // success text
        }}
      </DataLoader>

      {/* this one will fail on purpose (404 in the fake API) */}
      <DataLoader url="/api/missing/order">
        {({ status, error }) =>
          status === 'error' ? <p>Retry later ({error})</p> : <p>Checking order…</p>
        }
      </DataLoader>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Dashboard />);
```

---

## 🟠 Real App Integration

A render prop is a **function**, and functions cannot cross the Server → Client boundary in Next.js. A Server Component cannot pass an inline `render` function to a Client Component. The fix is to define the function inside the Client Component file that owns the UI.

```jsx
// app/components/Toggle.jsx
'use client';                                           // owner of the state
import { useState } from 'react';

export default function Toggle({ render }) {            // render is a function: must be created on the client
  const [on, setOn] = useState(false);
  return render({ on, toggle: () => setOn(v => !v) });  // call the caller's function with the state
}
```

```jsx
// app/components/PowerButton.jsx
'use client';                                           // the render function lives on the client too
import Toggle from './Toggle';

export default function PowerButton() {
  return (
    <Toggle render={({ on, toggle }) => (                // function created here, on the client
      <button onClick={toggle}>{on ? 'ON' : 'OFF'}</button>
    )} />
  );
}
```

```jsx
// app/page.jsx (Server Component)
import PowerButton from './components/PowerButton';    // only the component reference crosses the boundary
export default function Page() {
  return <PowerButton />;                               // ✅ no function is passed from the server
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Calling the render function from the caller side instead of letting the owner call it
✅ **Correct:** The owner calls the function with its state; the caller only provides the function

```jsx
// Wrong: the caller tries to read state it does not own
const data = useLoader();                         // ❌ this is a different pattern (a hook)
<DataLoader render={() => <p>{data.name}</p>} />  // ❌ data is not available here

// Right: the owner passes the state into the function as an argument
<DataLoader render={(data) => <p>{data.name}</p>} />  // ✅ data arrives as an argument
```

❌ **Mistake 2:** Passing an inline render function to a `React.memo` component, which defeats the memo
✅ **Correct:** Define the function outside the JSX (or with `useCallback`) so its reference is stable

```jsx
// Wrong: a NEW arrow function is created on every parent render → memo never skips
const Chart = memo(function Chart({ render }) { /* ... */ });
<Chart render={(x) => <p>{x}</p>} />                // ❌ new function each render

// Right: a stable function reference lets memo skip re-renders
const renderValue = (x) => <p>{x}</p>;              // ✅ created once at module level
<Chart render={renderValue} />
```

---

## 🧠 Tricky Interview Question

```jsx
import { memo, useEffect, useReducer } from 'react';
import { createRoot } from 'react-dom/client';

const Clock = memo(function Clock({ render }) {  // memo: skip re-render when props are equal
  console.log('Clock render');                  // logs each time Clock actually runs
  return render(1);                             // call the render prop
});

function Parent() {
  const [, force] = useReducer(x => x + 1, 0); // used to force Parent to render again
  useEffect(() => { force(); }, []);           // Parent re-renders once after mount
  return <Clock render={(v) => <p>{v}</p>} />; // NEW arrow function on every Parent render
}

createRoot(document.getElementById('root')).render(<Parent />);
```
**Answer:** The output is:
```
Clock render
Clock render
```
`React.memo` compares props with a shallow `Object.is` check. On the second `Parent` render the `render` prop is a brand-new arrow function, so the reference differs, and `memo` lets `Clock` run again. The output is the same whether or not the render prop changes meaning, because only its identity matters to `memo`. If you move the function to module level (`const renderOne = v => <p>{v}</p>`), `Clock render` is printed only once, because the reference is stable and `memo` skips the second render.

---

## ⚫ Interview Questions + Answers

Q1: What is a render prop?
A1: A prop whose value is a function that returns React elements. The component that owns the logic calls the function with its internal data, so the caller controls the output.

Q2: What problem do render props solve?
A2: They share logic between components without duplicating code and without hard-coding the UI. The owner handles data and behavior, and each caller decides how to draw it.

Q3: Why are render props less common now?
A3: Custom hooks (`useState`, `useEffect`, your own `useXyz`) share the same logic more directly, without an extra layer in the component tree and without nested callback syntax. Render props are still valid and are used by some libraries (for example, Formik and React Router older APIs), but hooks are the modern default.

Q4: What is the difference between `render` and `children` as a function?
A4: Both are just props that receive a function. `render` is an explicit name, which makes the intent clear. `children` as a function is shorter and reads like JSX, but it can confuse readers if the component also accepts normal children.

Q5: How do render props interact with `React.memo`?
A5: `memo` compares props shallowly, so a new inline function on every render breaks memoization. Keep the function reference stable with a module-level definition or `useCallback`.

---

## 🔷 When to Use + When Not to Use
✅ **Use render props when:**
- You maintain a library or code base that already uses this pattern
- The owner must pass several values into the caller's UI in a type-safe way
- You need flexible rendering controlled by the caller, without hooks (very old React)

❌ **Avoid render props when:**
- A custom hook can return the same values (prefer `const x = useX()`)
- You nest several render props, which creates "callback hell" in JSX
- The function is created inline in a memoized parent path, causing unnecessary renders

---

## 📊 Visual Diagram

```
  <Toggle render={fn} />

  ┌──────────── Toggle (OWNER: logic + state) ───────────┐
  │   const [on, setOn] = useState(false);                │
  │   const toggle = () => setOn(v => !v);                │
  │                                                        │
  │   return render({ on, toggle });  ── calls fn ──┐     │
  └────────────────────────────────────────────────┼─────┘
                                                   ▼
  ┌──────────── CALLER (decides the UI) ─────────────────┐
  │   ({ on, toggle }) => <button onClick={toggle}>      │
  │                         {on ? 'ON' : 'OFF'}          │
  │                       </button>                       │
  └──────────────────────────────────────────────────────┘

  Data flows UP from owner to function (as an argument), UI flows DOWN from function to DOM.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Render prop | Function prop that returns UI | UI लौटाने वाला function prop |
| Owner component | Component holding logic and state | Logic और state रखने वाला component |
| Caller | Component using the owner | Owner का इस्तेमाल करने वाला |
| children as function | Passing a function as children | Children की जगह function देना |
| Shallow comparison | Comparing props by reference | Props को reference से compare करना |
| Custom hook | Reusable stateful logic as a function | Reusable stateful logic वाला function |
| Callback hell | Deeply nested callbacks in JSX | JSX में गहराई तक nested callbacks |
| Memoization | Skipping work when props are equal | Props same हों तो काम छोड़ना |

---

## ⚡ 3-Line Summary
**English:**
1. A render prop is a function prop; the owner calls it with its data and returns the UI it produces.
2. It separates logic (owner) from presentation (caller), so one data loader can draw many UIs.
3. Custom hooks have mostly replaced it, but keep function references stable to avoid breaking `React.memo`.

**Hindi:**
1. Render prop एक function prop है; owner उसे अपने data के साथ call करता है और बनने वाला UI लौटाता है।
2. यह logic (owner) और presentation (caller) अलग करता है, इसलिए एक data loader कई UIs बना सकता है।
3. Custom hooks ने इसकी जगह ज़्यादातर ले ली है, पर `React.memo` टूटे नहीं इसलिए function reference स्थिर रखो।

---

## ➡️ Next Topic
**65. Higher Order Components (HOC)** — ऐसा function जो component लेकर नया component लौटाए। Render props की तरह यह भी logic share करता है, पर अलग तरीके से।
