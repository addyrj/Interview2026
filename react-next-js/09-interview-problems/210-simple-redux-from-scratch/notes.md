# 210. Build Simple Redux from Scratch
# हिंदी में: Redux को शुरू से बनाओ

Code: [redux.js](./redux.js) (complete working implementation: `createStore`, `combineReducers`, `applyMiddleware`, `thunk`, `createHooks`)

---

## 🔵 Simple Definition (English)
**Redux** is a small state container: one state object, changed only by dispatching actions to a pure reducer function, with subscribers notified after each change. The core is about 25 lines, and middleware and React bindings are small additions.

## 🔵 सरल परिभाषा (Hindi)
**Redux** एक छोटा state container है: एक state object, जो सिर्फ़ actions को pure reducer function में dispatch करके बदलता है, और हर बदलाव के बाद subscribers को खबर मिलती है। Core लगभग 25 lines का है, और middleware व React bindings छोटे जोड़ हैं।

---

## 🔴 Problem it Solves

Interviewers ask "implement Redux" to check that you understand what the library really does, not just how to call it. Using `useDispatch` without knowing the internals leads to mistakes: mutating state, impure reducers, not knowing why middleware exists, or why `useSelector` returning a new object re-renders forever. Building it removes the magic.

## 🔴 यह क्यों बना? (Hindi)
Interviewer "Redux implement करो" इसलिए पूछते हैं कि आप समझें library असल में क्या करती है, सिर्फ़ उसे call करना नहीं। अंदर की बनावट जाने बिना `useDispatch` इस्तेमाल करने पर गलतियाँ होती हैं: state mutate करना, impure reducers, middleware क्यों है यह न जानना, या `useSelector` का नया object लौटाने पर अंतहीन re-render। खुद बनाने से जादू खत्म हो जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → createStore(reducer) keeps `state` and a `listeners` array in a closure
Step 2 → getState() returns the current state
Step 3 → dispatch(action): state = reducer(state, action); then call every listener
Step 4 → subscribe(fn) adds a listener and returns an unsubscribe function
Step 5 → dispatch({ type: '@@INIT' }) once, so reducers fill their default state
Step 6 → combineReducers({ a, b }) → one reducer: state.a = a(state.a, action), same for b
Step 7 → applyMiddleware wraps dispatch: action → mw1 → mw2 → real dispatch
Step 8 → thunk: if the action is a function, call it with (dispatch, getState)
Step 9 → useSelector = useSyncExternalStore(subscribe, () => selector(getState()))
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → createStore(reducer) closure में `state` और `listeners` array रखता है
Step 2 → getState() मौजूदा state लौटाता है
Step 3 → dispatch(action): state = reducer(state, action); फिर हर listener को call करो
Step 4 → subscribe(fn) listener जोड़ता है और unsubscribe function लौटाता है
Step 5 → एक बार dispatch({ type: '@@INIT' }) ताकि reducers अपनी default state भर दें
Step 6 → combineReducers({ a, b }) → एक reducer: state.a = a(state.a, action), b भी वैसे ही
Step 7 → applyMiddleware dispatch को wrap करता है: action → mw1 → mw2 → असली dispatch
Step 8 → thunk: action अगर function है तो उसे (dispatch, getState) के साथ call करो
Step 9 → useSelector = useSyncExternalStore(subscribe, () => selector(getState()))
```

---

## 🟡 Real World Example
**Zomato cart:** One store holds `{ cart, user }`. Tapping "Add" dispatches `{ type: 'cart/add', item }`. The `cart` reducer returns a new cart, listeners fire, and the cart badge in the header re-renders. "Place order" is a thunk: `dispatch(orderStarted())`, await the API, then `dispatch(orderSucceeded())` or `orderFailed()`. A logger middleware prints every action while debugging.

## 🟡 Real Example Hindi mein
**Zomato cart:** एक store में `{ cart, user }` है। "Add" दबाने पर `{ type: 'cart/add', item }` dispatch होता है। `cart` reducer नया cart लौटाता है, listeners चलते हैं, और header का cart badge दोबारा render होता है। "Place order" एक thunk है: `dispatch(orderStarted())`, API का इंतज़ार, फिर `dispatch(orderSucceeded())` या `orderFailed()`। Debug के समय logger middleware हर action print करता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: the 15-line heart of Redux
function createStore(reducer) {
  let state;                                         // single state tree
  const listeners = [];                              // functions to call after each change

  const getState = () => state;                      // read state

  const dispatch = (action) => {
    state = reducer(state, action);                  // the ONLY way state changes
    listeners.forEach((l) => l());                   // tell subscribers
    return action;
  };

  const subscribe = (l) => {
    listeners.push(l);                               // add subscriber
    return () => listeners.splice(listeners.indexOf(l), 1); // unsubscribe
  };

  dispatch({ type: '@@INIT' });                      // initialise default state
  return { getState, dispatch, subscribe };
}

// A pure reducer: (state, action) => newState, never mutate
function counter(state = 0, action) {
  switch (action.type) {
    case 'inc': return state + 1;                    // return NEW value
    case 'dec': return state - 1;
    default: return state;                           // unknown action: same state
  }
}

const store = createStore(counter);
store.subscribe(() => console.log('state =', store.getState()));
store.dispatch({ type: 'inc' });                     // state = 1
store.dispatch({ type: 'inc' });                     // state = 2
store.dispatch({ type: 'dec' });                     // state = 1
```

## 💻 Code Example — Advanced

The full file is [redux.js](./redux.js). Key parts and usage with React:

```jsx
// redux.js (extract): combineReducers + applyMiddleware + thunk + hooks
import { useSyncExternalStore } from 'react';

export function combineReducers(reducers) {
  const keys = Object.keys(reducers);
  return (state = {}, action) => {
    let changed = false;
    const next = {};
    for (const key of keys) {
      next[key] = reducers[key](state[key], action);   // each slice handles its own part
      if (next[key] !== state[key]) changed = true;
    }
    return changed ? next : state;                     // same reference if nothing changed
  };
}

export function applyMiddleware(...middlewares) {
  return (createStoreFn) => (reducer, preloadedState) => {
    const store = createStoreFn(reducer, preloadedState);
    let dispatch = () => { throw new Error('Dispatching while constructing middleware'); };
    const api = { getState: store.getState, dispatch: (a) => dispatch(a) };
    const chain = middlewares.map((m) => m(api));
    dispatch = chain.reduceRight((next, mw) => mw(next), store.dispatch); // compose
    return { ...store, dispatch };
  };
}

export const thunk = ({ dispatch, getState }) => (next) => (action) =>
  typeof action === 'function' ? action(dispatch, getState) : next(action);

export function createHooks(store) {
  return {
    useSelector: (selector) => useSyncExternalStore(store.subscribe, () => selector(store.getState())),
    useDispatch: () => store.dispatch,
  };
}
```

```jsx
// App.jsx (usage)
import { createStore, combineReducers, applyMiddleware, thunk, createHooks } from './redux';

const cart = (state = [], a) => (a.type === 'cart/add' ? [...state, a.item] : state);
const user = (state = { name: 'Guest' }, a) => (a.type === 'user/set' ? { name: a.name } : state);

const store = createStore(combineReducers({ cart, user }), applyMiddleware(thunk));
const { useSelector, useDispatch } = createHooks(store);

const placeOrder = () => async (dispatch, getState) => {       // a thunk
  dispatch({ type: 'order/start' });
  await new Promise((r) => setTimeout(r, 300));                // fake API
  dispatch({ type: 'cart/add', item: 'Biryani' });
};

export default function App() {
  const count = useSelector((s) => s.cart.length);             // primitive: safe selector
  const dispatch = useDispatch();
  return <button onClick={() => dispatch(placeOrder())}>Cart ({count})</button>;
}
```

Verified by script: reducers combine, `subscribe`/unsubscribe counts are right, thunk dispatches work with both `applyMiddleware(thunk)(createStore)(...)` and `createStore(reducer, applyMiddleware(thunk))`, and `useSelector` re-renders a React component from 2 to 3 after a dispatch.

---

## 🟠 Next.js Connection

In the App Router, create the store **per request** (a module-level store on the server would be shared between users). Redux Toolkit's recommended pattern is a `makeStore()` function and a client Provider that creates the store once per browser session.

```jsx
// lib/store.js
import { configureStore } from '@reduxjs/toolkit';          // real Redux Toolkit
import cartReducer from './cartSlice';

export const makeStore = () => configureStore({ reducer: { cart: cartReducer } }); // new store per call
```

```jsx
// app/StoreProvider.jsx
'use client';                                               // Provider uses context and refs
import { useRef } from 'react';
import { Provider } from 'react-redux';
import { makeStore } from '@/lib/store';

export default function StoreProvider({ children }) {
  const storeRef = useRef(null);
  if (!storeRef.current) storeRef.current = makeStore();    // create once per client tree
  return <Provider store={storeRef.current}>{children}</Provider>;
}
// Use it in app/layout.jsx around {children}
```

Our mini version teaches the internals; in real projects use Redux Toolkit (`configureStore` includes thunk and DevTools). Server Components cannot use hooks or the store directly, so only Client Components read from it.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Mutating state inside a reducer
✅ **Correct:** Return a new object or array

```jsx
// Wrong: same array reference, listeners fire but selectors see no change
const cart = (state = [], a) => { if (a.type === 'add') state.push(a.item); return state; };

// Right
const cart = (state = [], a) => (a.type === 'add' ? [...state, a.item] : state);
```

❌ **Mistake 2:** A selector that returns a new object every time
✅ **Correct:** Select primitives or stable references

```jsx
// Wrong: new object each call, useSyncExternalStore sees a changed snapshot → infinite loop warning
const data = useSelector((s) => ({ n: s.cart.length }));

// Right
const n = useSelector((s) => s.cart.length);
```

❌ **Mistake 3:** Side effects (fetch, random, Date.now) inside a reducer
✅ **Correct:** Do side effects in thunks or middleware, keep reducers pure

```jsx
// Wrong
const r = (s = {}, a) => { fetch('/api/log'); return { ...s, t: Date.now() }; };

// Right: thunk does the fetch, reducer only applies the result
const load = () => async (dispatch) => { const d = await (await fetch('/api')).json(); dispatch({ type: 'loaded', d }); };
```

---

## 🧠 Tricky Interview Question

```jsx
const log = (tag) => () => (next) => (action) => { console.log(tag); return next(action); };
const store = createStore(
  (s = 0) => s,
  applyMiddleware(log('A'), log('B'), log('C'))
);
store.dispatch({ type: 'x' });
```
What is printed, and why is `reduceRight` used?

**Answer:** It prints `A`, `B`, `C` in that order. `reduceRight` starts from the real `store.dispatch` and wraps it with C, then B, then A, so the final `dispatch` is A's function: A runs first, calls `next` which is B, which calls C, which calls the real dispatch. If you used `reduce` the order would be reversed (C, B, A). Note also that `createStore` itself dispatches `@@INIT` before middleware is applied, so the `log` middleware does not print for the init action.

---

## ⚫ Interview Questions + Answers

Q1: What are the three principles of Redux?
A1: Single source of truth (one store), state is read-only (only changed by dispatching actions), and changes are made with pure functions (reducers).

Q2: Why must reducers be pure?
A2: Redux compares references to detect changes. A mutation keeps the same reference, so subscribers miss it. Purity also makes time-travel debugging, testing and replaying actions possible.

Q3: How does middleware work?
A3: Middleware has the signature `store => next => action`. It sits between `dispatch` and the reducer and can log, delay, transform or stop actions. `applyMiddleware` composes them so each `next` calls the following one, and the last calls the real `dispatch`.

Q4: What does redux-thunk do?
A4: It lets you dispatch a function instead of an object. The middleware calls that function with `dispatch` and `getState`, so you can run async code and dispatch several actions over time.

Q5: Why use `useSyncExternalStore` for `useSelector`?
A5: It is React 18's official API for subscribing to external stores. It avoids tearing in concurrent rendering (different components seeing different values in one render) and re-renders only when the selected snapshot changes. React-Redux v8+ uses it too.

---

## 🔷 When to Use + When Not to Use
✅ **Use Redux (Toolkit) when:**
- Many parts of a large app share complex state with clear update rules
- You need DevTools, time travel, middleware and predictable debugging
- Several teams need a strict, common pattern

❌ **Avoid when:**
- State is local to one component (`useState`) or a small subtree (`useReducer` plus context)
- The state is server data (use TanStack Query or SWR)
- You plan to ship this hand-made version (use Redux Toolkit or Zustand instead)

---

## 📊 Visual Diagram

```
   UI event
      │ dispatch(action)
      ▼
 ┌─────────────┐  action   ┌─────────┐  action   ┌─────────┐   action   ┌─────────┐
 │ dispatch(A) │ ────────► │ thunk   │ ────────► │ logger  │ ─────────► │ real    │
 └─────────────┘ (function │ (runs   │ (plain    │         │            │ dispatch│
                  is run)  │  fn)    │  object)  └─────────┘            └────┬────┘
                                                                              ▼
                               state = reducer(state, action)   (pure, new object)
                                                                              │
                                                                              ▼
                              listeners.forEach(l => l())  ──► useSelector re-runs selector
                                                                 re-render only if value changed
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Store | Holds the state tree | State tree रखने वाला container |
| Action | Plain object describing what happened | क्या हुआ, यह बताने वाला object |
| Reducer | Pure function (state, action) => new state | Pure function जो नई state लौटाता है |
| Dispatch | Send an action to the store | Action को store में भेजना |
| Subscribe | Register a listener for changes | बदलाव सुनने के लिए listener जोड़ना |
| Middleware | Code between dispatch and reducer | Dispatch और reducer के बीच का code |
| Thunk | Function dispatched for async logic | Async logic के लिए dispatch किया गया function |
| Selector | Function reading a piece of state | State का हिस्सा पढ़ने वाला function |

---

## ⚡ 3-Line Summary
**English:**
1. Redux is a closure holding `state` and `listeners`; `dispatch` runs a pure reducer and notifies subscribers.
2. `combineReducers` splits state into slices, `applyMiddleware` wraps `dispatch`, and `thunk` allows async actions.
3. `useSyncExternalStore` connects the store to React; in real apps use Redux Toolkit, with one store per request in Next.js.

**Hindi:**
1. Redux एक closure है जो `state` और `listeners` रखता है; `dispatch` pure reducer चलाता है और subscribers को बताता है।
2. `combineReducers` state को slices में बाँटता है, `applyMiddleware` `dispatch` को wrap करता है, और `thunk` async actions देता है।
3. `useSyncExternalStore` store को React से जोड़ता है; असली apps में Redux Toolkit इस्तेमाल करो, और Next.js में हर request के लिए एक store।

---

## ➡️ Next Topic
**यह Interview Problems section (191-210) का आखिरी topic है।** अब पूरे section को दोहराओ: जिन problems में तुम अटके थे (जैसे 199 Form, 209 Virtual List) उन्हें बिना देखे दोबारा बनाओ, और Redux Toolkit (97) से इस mini Redux की तुलना करो।
