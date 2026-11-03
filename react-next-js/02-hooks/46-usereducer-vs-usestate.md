# 46. useReducer vs useState
# हिंदी में: useReducer बनाम useState — State कब कौन सा

---

## 🔵 Simple Definition (English)
**`useState`** stores a value and gives you a setter: best for simple, independent values. **`useReducer`** stores state and a `dispatch` function; you describe *what happened* (an action) and a pure **reducer** function decides the next state: best for state with several related fields or many update rules.

## 🔵 सरल परिभाषा (Hindi)
**`useState`** एक value रखता है और setter देता है: सरल, स्वतंत्र values के लिए सबसे अच्छा। **`useReducer`** state और `dispatch` function रखता है; आप बताते हैं कि *क्या हुआ* (action), और एक pure **reducer** function अगली state तय करता है: कई जुड़े fields या कई update नियमों वाली state के लिए सबसे अच्छा।

---

## 🔴 Problem it Solves

When a component has many `useState` calls that change together (`loading`, `error`, `data`), event handlers contain several `setX` calls, and it is easy to land in an impossible combination (`loading: true` and `error: 'x'` together). Update logic is also scattered inside handlers, hard to test and hard to reuse. A reducer puts all transitions in one pure function, so every change is described by an action and states stay consistent.

```jsx
// PROBLEM: three setters must stay in sync manually
setLoading(false); setError(null); setData(result);     // forget one → inconsistent UI

// SOLUTION: one action, one place that knows the rules
dispatch({ type: 'fetch_success', data: result });      // reducer sets loading:false, error:null, data
```

## 🔴 यह क्यों बना? (Hindi)
जब component में कई `useState` हों जो साथ बदलते हैं (`loading`, `error`, `data`), तो event handlers में कई `setX` calls होती हैं, और असंभव combination (`loading: true` और `error: 'x'` एक साथ) में पहुँचना आसान है। Update logic handlers के अंदर बिखरा रहता है, जिसे test और दोबारा इस्तेमाल करना मुश्किल है। Reducer सारे बदलाव एक pure function में रखता है, हर बदलाव action से बताया जाता है और states consistent रहती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a pure reducer: (state, action) => newState (no mutation, no side effects)
Step 2 → const [state, dispatch] = useReducer(reducer, initialState)
Step 3 → In handlers call dispatch({ type: 'something', payload }) instead of many setX
Step 4 → React calls reducer(currentState, action) and compares the result with Object.is
Step 5 → New object → re-render with new state. Same object returned → bail out, no re-render
Step 6 → dispatch has a stable identity, so it is safe to pass down or put in effect deps

CHOOSING:
  one value / toggle / input text ........ useState
  several fields changing together ....... useReducer
  next state depends on previous + rules . useReducer
  want easy unit tests of update logic ... useReducer (test reducer alone)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Pure reducer लिखो: (state, action) => newState (mutation नहीं, side effects नहीं)
Step 2 → const [state, dispatch] = useReducer(reducer, initialState)
Step 3 → Handlers में कई setX की जगह dispatch({ type: 'something', payload }) बुलाओ
Step 4 → React reducer(currentState, action) बुलाता है और नतीजे को Object.is से तुलना करता है
Step 5 → नया object → नई state के साथ re-render। वही object लौटा → bail out, re-render नहीं
Step 6 → dispatch की identity स्थिर रहती है, इसलिए इसे नीचे भेजना या effect deps में रखना सुरक्षित है

चुनाव:
  एक value / toggle / input text ......... useState
  कई fields जो साथ बदलते हैं ............. useReducer
  अगली state पिछली + नियमों पर निर्भर ...... useReducer
  update logic का आसान unit test चाहिए .... useReducer (reducer अकेले test करो)
```

---

## 🟡 Real World Example
**Zomato checkout:** The screen has address, payment method, coupon, tip, loading flag and error message. Events like "apply coupon", "change tip", "payment failed", "place order success" each change several fields. With `useState` you would call 3 to 4 setters in each handler. With `useReducer`, each event is one `dispatch`, and the reducer computes the total, resets errors and clears the loading state in one place. In contrast, the search text box on the home screen is a single string: `useState`.

## 🟡 Real Example Hindi mein
**Zomato checkout:** Screen में address, payment method, coupon, tip, loading flag और error message हैं। "apply coupon", "change tip", "payment failed", "place order success" जैसे events हर एक कई fields बदलते हैं। `useState` में हर handler में 3 से 4 setters बुलाने पड़ते। `useReducer` में हर event एक `dispatch` है, और reducer total निकालना, errors reset करना और loading साफ़ करना एक ही जगह करता है। इसके उलट home screen का search text box सिर्फ़ एक string है: `useState`।

---

## 💻 Code Example — Basic

```jsx
// Counter written with both hooks
import { useState, useReducer } from 'react';         // both hooks
import { createRoot } from 'react-dom/client';        // React 18/19 root API

function CounterState() {
  const [count, setCount] = useState(0);              // simple value: useState is enough
  return (
    <div>
      <button onClick={() => setCount(c => c - 1)}>-</button>
      <span> {count} </span>
      <button onClick={() => setCount(c => c + 1)}>+</button>
    </div>
  );
}

function reducer(state, action) {                     // pure function: no mutation, no side effects
  switch (action.type) {                              // decide by the action type
    case 'inc': return { count: state.count + 1 };    // return NEW state object
    case 'dec': return { count: state.count - 1 };
    case 'reset': return { count: 0 };
    default: throw new Error('Unknown action: ' + action.type); // catch typos early
  }
}

function CounterReducer() {
  const [state, dispatch] = useReducer(reducer, { count: 0 }); // reducer + initial state
  return (
    <div>
      <button onClick={() => dispatch({ type: 'dec' })}>-</button>   {/* describe what happened */}
      <span> {state.count} </span>
      <button onClick={() => dispatch({ type: 'inc' })}>+</button>
      <button onClick={() => dispatch({ type: 'reset' })}>Reset</button>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<><CounterState /><CounterReducer /></>);
```

## 💻 Code Example — Advanced

```jsx
// Checkout form: related fields, legal transitions only, reducer is exported for unit tests
import { useReducer } from 'react';
import { createRoot } from 'react-dom/client';

export const initialState = {
  status: 'idle',            // idle | submitting | success | error  (one status instead of 3 booleans)
  coupon: '',
  discount: 0,
  tip: 0,
  subtotal: 500,
  error: null,
};

export function checkoutReducer(state, action) {
  switch (action.type) {
    case 'coupon_changed':
      return { ...state, coupon: action.value, error: null };          // typing clears old error
    case 'coupon_applied':
      return { ...state, discount: action.discount };                  // payload comes from the server
    case 'tip_changed':
      return { ...state, tip: Math.max(0, action.value) };             // rule lives in one place
    case 'submit':
      if (state.status === 'submitting') return state;                 // ignore double-click: same object → no re-render
      return { ...state, status: 'submitting', error: null };
    case 'success':
      return { ...state, status: 'success' };
    case 'failure':
      return { ...state, status: 'error', error: action.message };
    default:
      throw new Error('Unknown action: ' + action.type);
  }
}

// helper: derived value, not stored in state
const total = s => s.subtotal - s.discount + s.tip;

function Checkout() {
  const [state, dispatch] = useReducer(checkoutReducer, initialState);

  async function placeOrder() {
    dispatch({ type: 'submit' });                                      // one dispatch, no setter juggling
    try {
      const res = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ coupon: state.coupon, tip: state.tip }),
      });
      if (!res.ok) throw new Error('Payment failed');                  // fetch only rejects on network errors
      dispatch({ type: 'success' });
    } catch (e) {
      dispatch({ type: 'failure', message: e.message });
    }
  }

  return (
    <div>
      <input value={state.coupon} placeholder="Coupon"
             onChange={e => dispatch({ type: 'coupon_changed', value: e.target.value })} />
      <input type="number" value={state.tip}
             onChange={e => dispatch({ type: 'tip_changed', value: Number(e.target.value) })} />
      <p>Total: ₹{total(state)}</p>
      {state.error && <p role="alert">{state.error}</p>}
      <button disabled={state.status === 'submitting'} onClick={placeOrder}>
        {state.status === 'submitting' ? 'Placing...' : 'Place order'}
      </button>
      {state.status === 'success' && <p>Order placed!</p>}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Checkout />);

// Unit test idea (no React needed):
// expect(checkoutReducer(initialState, { type: 'tip_changed', value: -5 }).tip).toBe(0);
```

---

## 🟠 Next.js Connection

Both hooks are for Client Components. In the App Router, a form's submit/pending/error flow is increasingly handled with **Server Actions** and **`useActionState`** (React 19), which is like `useReducer` where the "reducer" is a server action. You still use `useReducer` for complex local UI state, like a multi-step form wizard.

```jsx
// app/checkout/actions.js (Server Action)
'use server';
export async function placeOrder(prevState, formData) {
  const coupon = formData.get('coupon');                 // read form fields on the server
  if (coupon === 'BAD') return { status: 'error', message: 'Invalid coupon' }; // returned as new state
  return { status: 'success', message: 'Order placed' };
}
```

```jsx
// app/checkout/CheckoutForm.jsx (Client Component, React 19 useActionState)
'use client';
import { useActionState } from 'react';                  // React 19 (was useFormState in canary/Next 14)
import { placeOrder } from './actions';

export default function CheckoutForm() {
  const [state, formAction, pending] = useActionState(placeOrder, { status: 'idle' }); // reducer-like
  return (
    <form action={formAction}>
      <input name="coupon" />
      <button disabled={pending}>{pending ? 'Placing...' : 'Place order'}</button>
      {state.message && <p>{state.message}</p>}
    </form>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Mutating state inside the reducer
✅ **Correct:** Return a new object/array

```jsx
// Wrong: same object returned → React bails out, UI does not update (and StrictMode exposes the bug)
function bad(state, action) { state.items.push(action.item); return state; }       // ❌
// Right
function good(state, action) { return { ...state, items: [...state.items, action.item] }; } // ✅
```

❌ **Mistake 2:** Side effects in the reducer (fetch, random, Date.now, localStorage)
✅ **Correct:** Reducers must be pure; do side effects in handlers or effects, then dispatch the result

```jsx
// Wrong: React may call reducers twice in StrictMode → two requests
case 'save': fetch('/api', { method: 'POST' }); return state;       // ❌
// Right: call fetch in the handler, then dispatch({ type: 'saved' })
```

❌ **Mistake 3:** Using `useReducer` for a single boolean or string
✅ **Correct:** Keep it simple with `useState`

```jsx
// Wrong: overkill
const [open, dispatch] = useReducer((s, a) => !s, false);               // ❌
// Right
const [open, setOpen] = useState(false);                               // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
function reducer(state, action) {
  state.count += 1;          // mutation!
  return state;              // same reference
}

function App() {
  const [state, dispatch] = useReducer(reducer, { count: 0 });
  return <button onClick={() => dispatch({})}>{state.count}</button>;
}
```
**Answer:** The button stays at `0` on screen in production: the reducer returns the **same object reference**, so React's `Object.is` check says nothing changed and it bails out of re-rendering (the object is mutated, but nobody re-renders to show it). In development with StrictMode, React calls reducers twice to catch impurity, so the hidden count can jump by 2 per click. The fix is `return { ...state, count: state.count + 1 }`.

---

## ⚫ Interview Questions + Answers

Q1: When should you choose `useReducer` over `useState`?
A1: When the state has multiple related fields, the next state depends on complex rules or the previous state, many handlers update the same state, or you want testable update logic. For one independent value, `useState` is simpler.

Q2: What is the signature of a reducer?
A2: `(state, action) => newState`. It must be pure: same inputs give the same output, and it must not mutate `state` or run side effects.

Q3: Is `useReducer` the same as Redux?
A3: The idea is the same (action + reducer), but `useReducer` is local to a component (share it with Context if needed). Redux adds a global store, middleware, devtools and selectors. Redux Toolkit uses Immer so you can write "mutating" code safely; plain `useReducer` does not.

Q4: Does `dispatch` change between renders?
A4: No, its identity is stable, so you can skip it from `useEffect`/`useCallback` dependencies and pass it to memoized children safely.

Q5: How do `useReducer` and `useState` differ in re-render behavior?
A5: Both re-render when the new state is not `Object.is`-equal to the old. With `useReducer` you can return the same `state` from the reducer for ignored actions, so no re-render happens. Both batch multiple updates in one event.

---

## 🔷 When to Use + When Not to Use
✅ **Use `useReducer` when:**
- State is an object with related fields, or a state machine (`idle/loading/success/error`)
- The same state is updated from many places
- You want to unit test transitions or share `dispatch` via Context

❌ **Use `useState` when:**
- State is one primitive: toggle, input text, counter
- The update is a simple replacement with no rules
- The extra boilerplate (types, cases) would be bigger than the logic

---

## 📊 Visual Diagram

```
 useState                               useReducer
 ┌──────────────┐                       ┌──────────────────────────────────┐
 │ handler      │                       │ handler                          │
 │  setLoading  │                       │   dispatch({type:'fetch_ok',..}) │
 │  setError    │                       └───────────────┬──────────────────┘
 │  setData     │  3 updates                            ▼
 └──────────────┘                       reducer(state, action) → newState   (pure, testable)
                                                        │
                                        Object.is(old, new)?  same → no re-render
                                                        │ different
                                                        ▼
                                                   re-render once

 Performance: the same (batched). Gain is correctness and testability, not speed.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Reducer | Pure function (state, action) → state | Pure function जो अगली state देता है |
| Action | Object describing what happened | क्या हुआ यह बताने वाला object |
| dispatch | Function that sends an action | Action भेजने वाला function |
| Pure function | No side effects, same input same output | बिना side effects, वही input वही output |
| Initial state | Starting value | शुरुआती value |
| State machine | Fixed set of states and transitions | तय states और transitions |
| Bail out | React skips re-render | React का re-render छोड़ देना |
| Immutability | Never change existing objects | मौजूदा objects को न बदलना |

---

## ⚡ 3-Line Summary
**English:**
1. `useState` suits simple values; `useReducer` suits related state with rules, via `dispatch(action)` and a pure reducer.
2. Reducers must not mutate state or run side effects, and `dispatch` is stable.
3. Choosing is about clarity and testability, not speed; React 19 `useActionState` is a reducer for form actions.

**Hindi:**
1. `useState` सरल values के लिए है; `useReducer` नियमों वाली जुड़ी state के लिए, `dispatch(action)` और pure reducer के साथ।
2. Reducer state को mutate नहीं करता और side effects नहीं चलाता, और `dispatch` स्थिर रहता है।
3. चुनाव clarity और testability का है, speed का नहीं; React 19 का `useActionState` form actions के लिए reducer जैसा है।

---

## 📚 Go Deeper — External Resources
| Type | Link | Why |
|------|------|-----|
| 📝 Article | [react.dev — Extracting State Logic into a Reducer](https://react.dev/learn/extracting-state-logic-into-a-reducer) | Official guide with comparison |
| 📝 Article | [react.dev — useReducer](https://react.dev/reference/react/useReducer) | API reference |

---

## ➡️ Next Topic
**47. useMemo** और **48. useCallback** (already covered) और फिर **49. useMemo vs useCallback** — दोनों memoization hooks में फ़र्क़ क्या है और कब कौन सा।
