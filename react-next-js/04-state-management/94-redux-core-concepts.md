# 94. Redux — Core Concepts
# हिंदी में: Redux — Core Concepts (Store, Action, Reducer, Dispatch)

---

## 🔵 Simple Definition (English)
Redux keeps all shared app state in **one store** object. The only way to change it is to **dispatch an action** (a plain object describing what happened). A **reducer** is a pure function that takes the old state and the action, and returns the new state.

## 🔵 सरल परिभाषा (Hindi)
Redux सभी shared app state को **एक store** object में रखता है। State बदलने का एक ही तरीका है: **action dispatch करना** (एक plain object जो बताता है क्या हुआ)। **Reducer** एक pure function है जो पुराना state और action लेता है और नया state लौटाता है।

---

## 🔴 Problem it Solves
With Context and `useState` alone, a large app has many small state holders, and no single place shows what changed or why. A bug like "cart total is wrong after refresh" is hard to trace. Redux forces every change through one path: action in, reducer computes, store saves. Because each change is a plain object, you can log it, replay it, test it without rendering, and show developers exactly which action caused which state.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ Context और `useState` से बड़ी app में कई छोटे state holders बन जाते हैं, और कोई एक जगह नहीं बताती कि क्या बदला और क्यों। "Refresh के बाद cart total गलत है" जैसा bug ढूँढना मुश्किल होता है। Redux हर बदलाव को एक रास्ते से भेजता है: action आता है, reducer नया state निकालता है, store उसे रखता है। हर बदलाव एक plain object होने से उसे log कर सकते हैं, replay कर सकते हैं, और rendering के बिना test भी कर सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Store holds the whole state:        { count: 0 }
Step 2 → Something happens (user clicks):    dispatch({ type: 'counter/increment' })
Step 3 → Store calls the root reducer:       reducer(currentState, action)
Step 4 → Reducer returns a NEW state object: { count: 1 }   (never edits the old one)
Step 5 → Store replaces its state and notifies subscribers (UI re-reads with getState)

KEY: state changes ONLY through dispatch → reducer. Reducers are pure: same input, same output, no side effects.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Store पूरा state रखता है:            { count: 0 }
Step 2 → कुछ होता है (click):                  dispatch({ type: 'counter/increment' })
Step 3 → Store root reducer call करता है:      reducer(पुराना state, action)
Step 4 → Reducer नया state object लौटाता है:   { count: 1 }  (पुराना कभी edit नहीं होता)
Step 5 → Store state बदलता है और subscribers को बताता है (UI getState से पढ़ता है)
KEY: State सिर्फ dispatch → reducer से बदलता है। Reducer pure होते हैं: वही input, वही output, कोई side effect नहीं।
```

---

## 🟡 Real World Example
**Razorpay dashboard — payment status:** A payment moves from `created` to `captured` to `refunded`. Each step is an action such as `payment/captured` with the payment id. The reducer updates only that payment's status, and every screen that reads that payment (the list, the detail drawer, the notification badge) updates from the same store. The action log tells the support team exactly when and why the status changed.

## 🟡 Real Example Hindi mein
**Razorpay dashboard — payment status:** Payment `created` से `captured` और फिर `refunded` होता है। हर step एक action है, जैसे `payment/captured` payment id के साथ। Reducer सिर्फ उसी payment का status बदलता है, और उसे पढ़ने वाली हर screen (list, detail drawer, notification badge) एक ही store से update होती है। Action log बताता है कि status कब और क्यों बदला।

---

## 💻 Code Example — Basic

```javascript
// Run: npm i redux && node file.js
// createStore builds a store from one reducer (classic Redux API)
import { createStore } from 'redux';

// Initial state: a plain object describing the whole counter
const initialState = { count: 0 };

// Reducer: (state, action) => newState. Default state used on first call.
function counterReducer(state = initialState, action) {
  switch (action.type) {                 // decide what to do from the action type
    case 'counter/increment':
      return { ...state, count: state.count + 1 }; // NEW object, old state untouched
    case 'counter/decrement':
      return { ...state, count: state.count - 1 };
    default:
      return state;                      // unknown action: return the same state
  }
}

// Build the store with the reducer
const store = createStore(counterReducer);

// Read the current state
console.log(store.getState());           // { count: 0 }

// Send an action: the ONLY way to change state
store.dispatch({ type: 'counter/increment' });
console.log(store.getState());           // { count: 1 }

store.dispatch({ type: 'counter/increment' });
store.dispatch({ type: 'counter/decrement' });
console.log(store.getState());           // { count: 1 }
```

## 💻 Code Example — Advanced

```javascript
// Run: npm i redux && node file.js
import { createStore } from 'redux';

// Action creators: small functions that build action objects.
// They keep the shape of actions in one place and make typos less likely.
const addTodo = (text) => ({ type: 'todos/added', payload: { id: Date.now(), text } });
const toggleTodo = (id) => ({ type: 'todos/toggled', payload: id });

// Pure reducer for the todos slice
function todosReducer(state = [], action) {
  switch (action.type) {
    case 'todos/added':
      // Add a new todo; spread creates a new array, state is never mutated
      return [...state, { ...action.payload, done: false }];
    case 'todos/toggled':
      // Flip the done flag only for the matching id
      return state.map((t) =>
        t.id === action.payload ? { ...t, done: !t.done } : t
      );
    default:
      return state;
  }
}

// Keep a history of every state, so we can show how it evolved (useful for debugging)
const history = [];

const store = createStore(todosReducer);

// subscribe runs after EVERY dispatch; we record the latest state
const unsubscribe = store.subscribe(() => {
  history.push(store.getState());        // store the state after this action
});

// Dispatch two actions through the action creators
store.dispatch(addTodo('Buy milk'));
const firstId = store.getState()[0].id;  // read the id generated by the action
store.dispatch(toggleTodo(firstId));

unsubscribe();                           // stop listening when we are done

// Print the number of recorded states and the final todo
console.log(history.length);             // 2 (one entry per dispatch)
console.log(store.getState()[0].done);   // true
```

---

## 🟠 Real App Integration (React + Next.js)

In Next.js App Router, create the store inside a Client Component so each browser tab gets its own store. On the server, create a new store per request, never a module-level singleton, otherwise one user's state could leak into another's request.

```jsx
// app/StoreProvider.jsx — Client Component that owns the store for this browser tab
'use client';                                   // Redux Provider needs client-side React
import { useRef } from 'react';
import { Provider } from 'react-redux';         // React binding for Redux
import { createStore } from 'redux';
import { counterReducer } from '../lib/counter';

export default function StoreProvider({ children }) {
  const storeRef = useRef(null);                // keeps one store across re-renders
  if (!storeRef.current) {                      // create it only on the first render
    storeRef.current = createStore(counterReducer);
  }
  return <Provider store={storeRef.current}>{children}</Provider>; // share with all children
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Mutating state inside a reducer
✅ **Correct:** Return a new object. Redux and React-Redux compare references, so a mutated object looks unchanged.

```javascript
// Wrong: mutates state and returns the SAME reference
function badReducer(state, action) {
  state.count += 1;   // ❌ edits the old object
  return state;       // ❌ same reference → no UI update
}

// Right: return a new object
function goodReducer(state, action) {
  return { ...state, count: state.count + 1 }; // ✅ new reference
}
```

❌ **Mistake 2:** Putting side effects (API calls, random numbers, `Date.now()`) inside reducers
✅ **Correct:** Reducers must be pure. Do API calls in middleware or thunks (topic 96, 99), and generate ids in action creators.

```javascript
// Wrong: reducer does an API call; running it twice sends two requests
function badReducer(state, action) {
  if (action.type === 'load') fetch('/api/items'); // ❌ side effect
  return state;
}

// Right: the reducer only describes the change; middleware does the request
function goodReducer(state, action) {
  if (action.type === 'items/loaded') return { ...state, items: action.payload }; // ✅ pure
  return state;
}
```

---

## 🧠 Tricky Interview Question

```javascript
// Run: npm i redux && node file.js
import { createStore } from 'redux';

// A BAD reducer: it changes the old object and returns the same reference
function badReducer(state = { count: 0 }, action) {
  if (action.type === 'inc') {
    state.count += 1;     // mutation
    return state;         // same object as before
  }
  return state;
}

const store = createStore(badReducer);
const before = store.getState();          // reference before the action
store.dispatch({ type: 'inc' });
const after = store.getState();           // reference after the action

console.log(before === after, after.count);
```

**Answer:** The output is `true 1`. The state's `count` changed from 0 to 1, so `after.count` is `1`. However, `before` and `after` are the same object, so `before === after` is `true`. Any `useSelector` or `connect` in React-Redux compares references with `===`. It sees "no change" and skips the re-render, so the screen shows the old count even though the store is correct. This is why reducers must return new objects.

---

## ⚫ Interview Questions + Answers

**Q1: What are the three core principles of Redux?**
A1: A single source of truth (one store), state is read-only (changed only by dispatching actions), and changes are made with pure reducers.

**Q2: What is an action?**
A2: A plain JavaScript object with a `type` string, and optionally a `payload`. It describes what happened, not how state should change.

**Q3: What is a reducer?**
A3: A pure function `(state, action) => newState`. It returns the same input for the same arguments and never mutates or performs side effects.

**Q4: What does `store.subscribe` do?**
A4: It registers a listener that runs after every dispatch. It returns an unsubscribe function. React-Redux uses subscriptions internally to re-render components.

**Q5: Why must a Next.js Redux store not be a module-level singleton on the server?**
A5: On the server one module instance serves many users, so a shared store would leak one user's data into another user's request. Create a new store per request, and per browser tab on the client.

---

## 🔷 When to Use + When Not to Use
✅ **Use Redux when:**
- Many distant components read and write the same state
- You need to know exactly which action caused a change (debugging, audit)
- The team benefits from a strict, predictable update pattern

❌ **Avoid Redux when:**
- The app is small and Context or `useState` is enough
- The state is server data that a server-state library handles better (topic 100)
- You would only use it for one form or one modal

---

## 📊 Visual Diagram

```
  UI event (click)
       │
       ▼
  dispatch({ type: 'counter/increment' })
       │
       ▼
  ┌──────────────────────────────┐
  │ Reducer: (state, action)      │  pure: no API calls, no mutation
  │   returns NEW state           │
  └──────────────────────────────┘
       │
       ▼
  ┌──────────────────────────────┐
  │ Store: { count: 1 }           │ ── subscribers notified
  └──────────────────────────────┘
       │
       ▼
  UI re-reads with getState / useSelector ──► screen shows count: 1
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Store | Object that holds the whole state | पूरा state रखने वाला object |
| Action | Plain object describing an event | घटना बताने वाला plain object |
| Reducer | Pure function that computes the next state | अगला state निकालने वाला pure function |
| Dispatch | Sends an action to the store | Store को action भेजना |
| Subscribe | Registers a listener called after each dispatch | हर dispatch के बाद चलने वाला listener |
| Pure function | Same input gives same output, no side effects | वही input, वही output, कोई side effect नहीं |

---

## ⚡ 3-Line Summary
**English:**
1. Redux keeps shared state in one store and changes it only by dispatching plain action objects.
2. Reducers are pure: they take the old state and an action, and return a new state object.
3. Never mutate state in a reducer, because equal references hide the change from React.

**Hindi:**
1. Redux shared state को एक store में रखता है और सिर्फ plain action objects dispatch करके बदलता है।
2. Reducers pure होते हैं: पुराना state और action लेते हैं, और नया state object लौटाते हैं।
3. Reducer में state कभी mutate मत करो, क्योंकि एक जैसे reference में React को बदलाव दिखता ही नहीं।

---

## ➡️ Next Topic
**95. Redux — Actions + Reducers + Store** — action creators, reducer की structure और `combineReducers` से कई slices को एक store में जोड़ना। Core concepts समझने के बाद यही सबसे पहला practical कदम है।
