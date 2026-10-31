# 96. Redux — dispatch + getState
# हिंदी में: Redux — dispatch और getState कैसे काम करते हैं

---

## 🔵 Simple Definition (English)
`dispatch(action)` sends an action into the store, and the store runs it through any **middleware** before the reducer. `getState()` returns the current state snapshot. Middleware can read the state with `getState` and send more actions with `dispatch`, which is how Redux handles logging, async calls and side effects.

## 🔵 सरल परिभाषा (Hindi)
`dispatch(action)` एक action को store में भेजता है, और store उसे reducer से पहले किसी भी **middleware** से गुज़ारता है। `getState()` मौजूदा state की snapshot लौटाता है। Middleware `getState` से state पढ़ सकता है और `dispatch` से और actions भेज सकता है, यही तरीका Redux में logging, async calls और side effects सँभालता है।

---

## 🔴 Problem it Solves
Reducers must be pure, so they cannot call APIs, read timers or log to the console. But real apps need all of those. Without a place for side effects, developers call `fetch` inside components, and the same request runs twice, or the state updates after the component unmounts. Middleware gives a controlled point between `dispatch` and the reducer. It can log, delay, cancel or replace actions, and it can read the current state through `getState` before deciding what to do.

## 🔴 यह क्यों बना? (Hindi)
Reducers pure होने चाहिए, इसलिए वे API call, timer या console log नहीं कर सकते। पर असली apps को यह सब चाहिए। Side effects के लिए जगह न हो तो developers components में `fetch` लिखते हैं, और वही request दो बार चलती है या component unmount होने के बाद state बदलता है। Middleware `dispatch` और reducer के बीच एक नियंत्रित जगह देता है। वह log कर सकता है, रोक सकता है, delay कर सकता है, और `getState` से पहले state पढ़कर फ़ैसला ले सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Component calls dispatch(action)
Step 2 → The action goes through middleware in order (first → last)
         Each middleware can: log, change, delay, or stop the action
Step 3 → A middleware can call getState() to read the current state
Step 4 → A middleware can call dispatch(newAction) to send more actions
Step 5 → The final action reaches the reducer → new state is saved
Step 6 → Middleware return path runs in reverse (last → first)

KEY: getState reads, dispatch sends. Reducers never call them; only middleware and components do.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Component dispatch(action) call करता है
Step 2 → Action middleware से क्रम में गुज़रता है (पहले → आखिरी)
         हर middleware: log, बदल, delay, या रोक सकता है
Step 3 → Middleware getState() से मौजूदा state पढ़ सकता है
Step 4 → Middleware dispatch(newAction) से और actions भेज सकता है
Step 5 → आखिरी action reducer तक पहुँचता है → नया state सेव होता है
Step 6 → Middleware का return path उल्टे क्रम (आखिरी → पहले) में चलता है
KEY: getState पढ़ता है, dispatch भेजता है। Reducers इन्हें कभी call नहीं करते।
```

---

## 🟡 Real World Example
**Swiggy order placement:** Tapping "Place order" dispatches `order/placeRequested`. A middleware sees this, reads `getState()` to check that the cart is not empty and the address is set, then calls the API. When the server replies, it dispatches `order/placed` with the order id, and the reducer stores it. If the cart is empty, the middleware stops the request before it leaves the device, so no bad order reaches the server.

## 🟡 Real Example Hindi mein
**Swiggy order placement:** "Place order" दबाने पर `order/placeRequested` dispatch होता है। एक middleware इसे देखता है, `getState()` से जाँचता है कि cart खाली न हो और address set हो, फिर API call करता है। Server जवाब देने पर `order/placed` dispatch करता है जिसमें order id होता है, और reducer उसे रखता है। Cart खाली हो तो middleware request को device से बाहर जाने से पहले ही रोक देता है।

---

## 💻 Code Example — Basic

```javascript
// Run: npm i redux && node file.js
import { createStore, applyMiddleware } from 'redux';

// A simple reducer for a counter
function counter(state = 0, action) {
  switch (action.type) {
    case 'inc':
      return state + 1;      // new value for this slice
    default:
      return state;
  }
}

// Middleware: a function that receives the store, returns a function that receives "next"
// "next" = the next middleware, or the reducer if this is the last one
const logger = (store) => (next) => (action) => {
  console.log('Before:', store.getState());  // read the state BEFORE the action
  const result = next(action);              // pass the action down the chain
  console.log('After: ', store.getState());  // read the state AFTER the action
  return result;                            // return what next() returned
};

// applyMiddleware wires the middleware into the store
const store = createStore(counter, applyMiddleware(logger));

store.dispatch({ type: 'inc' });
// Before: 0
// After:  1
```

## 💻 Code Example — Advanced

```javascript
// Run: npm i redux && node file.js
import { createStore, applyMiddleware } from 'redux';

// Reducer for a product list and its loading state
function products(state = { items: [], loading: false }, action) {
  switch (action.type) {
    case 'products/requested':
      return { ...state, loading: true };           // show spinner
    case 'products/succeeded':
      return { items: action.payload, loading: false }; // store results
    default:
      return state;
  }
}

// Thunk middleware: lets an action be a FUNCTION that receives (dispatch, getState)
// This is the same idea as the redux-thunk package, written out so you can see it.
const thunk = ({ dispatch, getState }) => (next) => (action) => {
  if (typeof action === 'function') {        // a function is not a plain action
    return action(dispatch, getState);       // run it with the store's tools
  }
  return next(action);                       // plain object: pass it along
};

// Thunk: an async action. It reads state, skips work if already loaded, then dispatches results.
const loadProducts = () => async (dispatch, getState) => {
  // getState() lets us check the current state before doing any network work
  const { loading, items } = getState();
  if (loading || items.length > 0) {
    return;                                  // already loading or loaded: skip the request
  }
  dispatch({ type: 'products/requested' });  // tell the store we started loading

  // Fake API call: resolves after the simulated network delay
  const fakeApi = () => new Promise((resolve) =>
    setTimeout(() => resolve([{ id: 1, name: 'Biryani' }]), 10)
  );

  const data = await fakeApi();              // wait for the result
  dispatch({ type: 'products/succeeded', payload: data }); // store it
};

const store = createStore(products, applyMiddleware(thunk));

store.dispatch(loadProducts());              // first call: fetches
store.dispatch(loadProducts());              // second call: getState says loaded, skip

// Wait a little so the fake API finishes, then read the final state
setTimeout(() => {
  console.log(store.getState());
  // { items: [ { id: 1, name: 'Biryani' } ], loading: false }
}, 50);
```

---

## 🟠 Real App Integration (React + Next.js)

In a React app, components call `dispatch` through the `useDispatch` hook from react-redux, and read state through `useSelector`. The middleware in the Redux Toolkit store (topic 97) handles thunks by default, so the thunk pattern above is what production code uses.

```jsx
// components/AddToCartButton.jsx — Client Component
'use client';
import { useDispatch } from 'react-redux';

export default function AddToCartButton({ product }) {
  const dispatch = useDispatch();                // dispatch from the store Provider
  return (
    <button onClick={() => dispatch({ type: 'cart/itemAdded', payload: product })}>
      Add to cart
    </button>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Calling `dispatch` inside a reducer
✅ **Correct:** Reducers must only return state. Redux throws an error if a reducer dispatches, because it would create an endless loop.

```javascript
// Wrong: reducer dispatches, Redux throws "Reducers may not dispatch actions."
function badReducer(state, action) {
  if (action.type === 'load') store.dispatch({ type: 'loaded' }); // ❌
  return state;
}

// Right: put the extra action in middleware or in a thunk, after the reducer finishes
const goodThunk = () => (dispatch) => {
  dispatch({ type: 'load' });                // ✅ dispatch from outside the reducer
  dispatch({ type: 'loaded' });
};
```

❌ **Mistake 2:** Reading state from a stale variable instead of `getState()`
✅ **Correct:** In async code, call `getState()` at the moment you need it. A variable captured before an `await` can be out of date.

```javascript
// Wrong: captured before the await, so the check uses an old state
const thunk = () => async (dispatch, getState) => {
  const items = getState().items;            // ❌ snapshot taken early
  await fetchMore();
  if (items.length > 0) { /* uses stale data */ }
};

// Right: read fresh state after the await
const thunk = () => async (dispatch, getState) => {
  await fetchMore();
  if (getState().items.length > 0) { /* ✅ current state */ }
};
```

---

## 🧠 Tricky Interview Question

```javascript
// Run: npm i redux && node file.js
import { createStore, applyMiddleware } from 'redux';

function reducer(state = 0, action) {
  return action.type === 'PING' ? state + 1 : state;
}

// Two middlewares that print when they are entered and left
const first = (store) => (next) => (action) => {
  console.log('first in');
  const result = next(action);
  console.log('first out');
  return result;
};

const second = (store) => (next) => (action) => {
  console.log('second in');
  const result = next(action);
  console.log('second out');
  return result;
};

const store = createStore(reducer, applyMiddleware(first, second));
store.dispatch({ type: 'PING' });
console.log(store.getState());
```

**Answer:** The output is:
```
first in
second in
second out
first out
1
```
`applyMiddleware(first, second)` builds a chain: `dispatch` calls `first`, which calls `next`, which is `second`, which calls the reducer. The "in" lines appear in forward order. When the reducer returns, control unwinds back up the chain, so `second out` prints before `first out`. The state is `1` because the reducer ran once and handled `PING`. The middleware order is the one you pass to `applyMiddleware`, which is why logging middleware usually comes first.

---

## ⚫ Interview Questions + Answers

**Q1: What does `dispatch` do?**
A1: It sends an action into the store. The action passes through the middleware chain, then reaches the reducer, which returns the new state.

**Q2: What does `getState` return?**
A2: The current state object. It is a snapshot at the moment of the call, so read it again after any `await`.

**Q3: What is a middleware in Redux?**
A3: A function with the shape `store => next => action => ...`. It can read state, change or stop actions, call `next` to continue, and dispatch new actions.

**Q4: Why does a thunk receive `dispatch` and `getState`?**
A4: So async logic can dispatch several actions over time and read the current state before deciding what to do, for example to skip a request that is already done.

**Q5: Can a reducer call `getState`?**
A5: It can read the state it was given, but it should not call `store.getState()` or `dispatch`. Reducers must be pure and only compute the next state from their inputs.

---

## 🔷 When to Use + When Not to Use
✅ **Use middleware and thunks when:**
- An action needs an API call before the state changes
- You need logging, analytics or crash reporting on every action
- An async flow depends on the current state (skip if loaded, cancel if stale)

❌ **Avoid when:**
- The logic is simple and can live in an event handler
- The data is a server cache that a query library handles (topic 100)
- You add middleware only to avoid thinking about where side effects belong

---

## 📊 Visual Diagram

```
   component: dispatch(action)
            │
            ▼
   ┌───────────────────┐
   │ first middleware  │ ── log "in"
   │  ┌─────────────┐  │
   │  │ second mw   │  │ ── getState() can read here
   │  │  ┌───────┐  │  │
   │  │  │reducer│  │  │ ── returns NEW state
   │  │  └───────┘  │  │
   │  └─────────────┘  │
   └───────────────────┘
            │
            ▼
   store saves state; getState() returns it
   (return path unwinds: second out → first out)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| dispatch | Sends an action into the store | Store में action भेजना |
| getState | Returns the current state snapshot | मौजूदा state की snapshot लौटाना |
| Middleware | Function that runs between dispatch and reducer | Dispatch और reducer के बीच चलने वाला function |
| applyMiddleware | Connects middleware into the store | Middleware को store से जोड़ना |
| Thunk | Function action that does async work | Async काम करने वाला function action |
| Side effect | Work outside the state update, like an API call | State update के बाहर का काम, जैसे API call |

---

## ⚡ 3-Line Summary
**English:**
1. `dispatch` sends an action through middleware to the reducer; `getState` returns the current state.
2. Middleware and thunks use both to handle logging, async calls and conditional logic.
3. Reducers stay pure and never dispatch; read fresh state with `getState` after each `await`.

**Hindi:**
1. `dispatch` action को middleware से होकर reducer तक भेजता है; `getState` मौजूदा state लौटाता है।
2. Middleware और thunks दोनों का उपयोग करके logging, async calls और शर्तों वाला logic सँभालते हैं।
3. Reducers pure रहते हैं और कभी dispatch नहीं करते; हर `await` के बाद `getState` से ताज़ा state पढ़ो।

---

## ➡️ Next Topic
**97. Redux Toolkit (RTK) — Complete Guide** — Redux का यही boilerplate कम करने वाला official toolkit: `createSlice`, `configureStore` और `createAsyncThunk` एक जगह। Middleware और thunk समझने के बाद RTK सबसे सीधा अगला कदम है।
