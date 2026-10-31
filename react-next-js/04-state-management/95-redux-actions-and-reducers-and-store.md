# 95. Redux — Actions + Reducers + Store
# हिंदी में: Redux — Actions, Reducers और Store कैसे जुड़े हैं

---

## 🔵 Simple Definition (English)
An **action** is a plain object that says what happened. A **reducer** decides how the state changes for an action. A **store** holds the state and connects the two: it passes each dispatched action to the reducer and saves the result. **`combineReducers`** joins several reducers, one per slice of state, into one root reducer.

## 🔵 सरल परिभाषा (Hindi)
**Action** एक plain object है जो बताता है क्या हुआ। **Reducer** तय करता है कि action से state कैसे बदलेगा। **Store** state रखता है और दोनों को जोड़ता है: हर dispatch किया action reducer को देता है और नतीजा सेव करता है। **`combineReducers`** कई reducers (हर state slice के लिए एक) को एक root reducer में जोड़ता है।

---

## 🔴 Problem it Solves
In a real app the state has many parts: todos, filters, user, cart. One huge reducer with a 300-line `switch` becomes unreadable and two developers edit the same lines. Redux splits the work: each slice has its own reducer that handles only its actions, and `combineReducers` assembles them. Action creators stop typos from spreading, because every dispatch goes through one function with one spelling.

## 🔴 यह क्यों बना? (Hindi)
असली app में state के कई हिस्से होते हैं: todos, filters, user, cart। एक बड़ा reducer जिसमें 300 लाइन का `switch` हो, पढ़ने में मुश्किल होता है और दो developers एक ही लाइनें बदलते हैं। Redux काम बाँटता है: हर slice का अपना reducer होता है जो सिर्फ उसके actions सँभालता है, और `combineReducers` उन्हें जोड़ता है। Action creators typos को फैलने से रोकते हैं, क्योंकि हर dispatch एक function से और एक spelling से होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Action creator builds the action:
         addTodo('Buy milk') → { type: 'todos/added', payload: 'Buy milk' }

Step 2 → store.dispatch(action) sends it to the ROOT reducer

Step 3 → combineReducers calls EACH slice reducer with its own slice:
         todos(state.todos, action)
         filter(state.filter, action)

Step 4 → Each slice reducer returns its new slice (or the same one if not interested)

Step 5 → combineReducers builds the new root object { todos, filter }, store saves it

KEY: Action = what happened. Reducer = how the slice changes. Store = where the result lives.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Action creator action बनाता है: addTodo('Buy milk') → { type, payload }
Step 2 → store.dispatch(action) उसे ROOT reducer को भेजता है
Step 3 → combineReducers हर slice reducer को उसका अपना slice देता है
Step 4 → हर slice reducer अपना नया slice लौटाता है (या वही, अगर action उसका नहीं)
Step 5 → combineReducers नया root object { todos, filter } बनाता है, store उसे सेव करता है
KEY: Action = क्या हुआ। Reducer = slice कैसे बदलता है। Store = नतीजा कहाँ रहता है।
```

---

## 🟡 Real World Example
**Flipkart cart and filters:** The app has a `cart` slice (items, coupon), a `filters` slice (price range, brand), and a `user` slice. Tapping "Add to cart" dispatches `cart/itemAdded`. Only the `cart` reducer changes anything. Changing a price filter dispatches `filters/priceSet`, and only the `filters` reducer runs its logic. Both slices live in one store, so the header badge and the product grid stay in sync.

## 🟡 Real Example Hindi mein
**Flipkart cart और filters:** App में `cart` slice (items, coupon), `filters` slice (price range, brand) और `user` slice है। "Add to cart" दबाने पर `cart/itemAdded` dispatch होता है। सिर्फ `cart` reducer कुछ बदलता है। Price filter बदलने पर `filters/priceSet` dispatch होता है, और सिर्फ `filters` reducer अपनी logic चलाता है। दोनों slices एक store में रहते हैं, इसलिए header का badge और product grid एक साथ sync में रहते हैं।

---

## 💻 Code Example — Basic

```javascript
// Run: npm i redux && node file.js
import { createStore } from 'redux';

// Action creator: returns the action object, so the shape is defined in one place
function addTodo(text) {
  return { type: 'todos/added', payload: text }; // type = what happened, payload = data
}

// Reducer for the todos slice: starts with an empty list
function todos(state = [], action) {
  switch (action.type) {                        // check which action arrived
    case 'todos/added':
      // Return a new array with the new todo at the end
      return [...state, action.payload];
    default:
      return state;                            // not our action: keep the same slice
  }
}

// Create the store with that reducer
const store = createStore(todos);

// Subscribe prints the state after each dispatch (like a React component would re-render)
store.subscribe(() => console.log('State now:', store.getState()));

// Dispatch two actions created with the action creator
store.dispatch(addTodo('Buy milk'));    // prints: State now: [ 'Buy milk' ]
store.dispatch(addTodo('Call mom'));    // prints: State now: [ 'Buy milk', 'Call mom' ]
```

## 💻 Code Example — Advanced

```javascript
// Run: npm i redux && node file.js
import { createStore, combineReducers } from 'redux';

// ── Action creators for two different slices ──
const todoAdded = (text) => ({ type: 'todos/added', payload: { text } });
const filterSet = (filter) => ({ type: 'filter/set', payload: filter });

// ── Slice 1: todos. Owns the list only ──
function todos(state = [], action) {
  switch (action.type) {
    case 'todos/added':
      // Append a new todo object, never mutate the array in place
      return [...state, { id: state.length + 1, text: action.payload.text }];
    default:
      return state;
  }
}

// ── Slice 2: filter. Owns one string value ──
const VALID_FILTERS = ['all', 'active', 'done']; // allowed values

function filter(state = 'all', action) {
  switch (action.type) {
    case 'filter/set':
      // Reject unknown values: keep the old state instead of storing garbage
      return VALID_FILTERS.includes(action.payload) ? action.payload : state;
    default:
      return state;
  }
}

// combineReducers builds the ROOT reducer: { todos: [...], filter: '...' }
const rootReducer = combineReducers({ todos, filter });

// Preloaded state: useful for server rendering or restoring from localStorage
const store = createStore(rootReducer, { todos: [], filter: 'active' });

store.dispatch(todoAdded('Buy milk'));    // only todos changes
store.dispatch(filterSet('done'));        // only filter changes
store.dispatch(filterSet('banana'));      // invalid: filter stays 'done'

console.log(store.getState());
// { todos: [ { id: 1, text: 'Buy milk' } ], filter: 'done' }
```

---

## 🟠 Real App Integration (React + Next.js)

A typical Redux setup keeps the reducers in one file and creates the store with a factory function. The factory can run on the server for each request and on the client for each tab, which matches the Next.js rule from topic 94.

```jsx
// lib/store.js — factory: creates a fresh store every time it is called
import { createStore, combineReducers } from 'redux';
import todos from './todosSlice';    // slice reducer
import filter from './filterSlice';  // slice reducer

const rootReducer = combineReducers({ todos, filter }); // one root reducer

export function makeStore(preloadedState) {
  // preloadedState comes from the server render, so the client starts with the same data
  return createStore(rootReducer, preloadedState);
}
```

```jsx
// app/todos/page.jsx — Client Component reads the store with react-redux hooks
'use client';
import { useSelector, useDispatch } from 'react-redux';

export default function TodoList() {
  const todos = useSelector((state) => state.todos);       // subscribe to one slice
  const dispatch = useDispatch();                          // get the dispatch function

  return (
    <ul>
      {todos.map((t) => <li key={t.id}>{t.text}</li>)}
      {/* a click would call dispatch({ type: 'todos/added', payload: { text: 'New' } }) */}
    </ul>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Typos in action type strings
✅ **Correct:** Use action creators or constants, so a typo is caught by a missing function or an undefined import. A typo in a plain string is silently ignored.

```javascript
// Wrong: typo in the type string, nothing errors, state never changes
store.dispatch({ type: 'todos/ad', payload: 'Buy milk' }); // ❌ 'todos/ad'

// Right: the action creator guarantees the spelling
store.dispatch(todoAdded('Buy milk'));                     // ✅
```

❌ **Mistake 2:** Putting an action's shape in many places
✅ **Correct:** Keep the action object's shape in a single action creator. Components then only call `dispatch(todoAdded(text))`.

```javascript
// Wrong: each component builds its own action object
dispatch({ type: 'todos/added', payload: text });      // ❌ shape repeated everywhere
dispatch({ type: 'todos/added', payload: { text } });  // ❌ and it does not match!

// Right: one action creator, one shape
dispatch(todoAdded(text));                             // ✅
```

---

## 🧠 Tricky Interview Question

```javascript
// Run: npm i redux && node file.js
import { createStore } from 'redux';

function todos(state = [], action) {
  switch (action.type) {
    case 'todos/added':
      return [...state, action.payload];
    default:
      return state;
  }
}

const store = createStore(todos);

// Notice the typo: 'todos/ad' instead of 'todos/added'
store.dispatch({ type: 'todos/ad', payload: 'Buy milk' });

console.log(store.getState());
```

**Answer:** The output is `[]`. There is no error. Redux does not validate action types, so `'todos/ad'` goes to the reducer, matches no `case`, and falls into `default`, which returns the same empty array. The store is correct, but the requested change never happened. This silent failure is why action creators and typed constants are used in real projects: a mistake there becomes an immediate error instead of a missing todo.

---

## ⚫ Interview Questions + Answers

**Q1: What is the role of `combineReducers`?**
A1: It takes an object of reducers, one per state key, and returns one root reducer. On each action it calls every slice reducer with its own slice and assembles the result into a new object.

**Q2: Why does a reducer return the same state for an unknown action?**
A2: The reducer should only change its own slice. Returning the same reference tells Redux and React-Redux that nothing changed, which prevents extra re-renders.

**Q3: What is the purpose of an action creator?**
A3: It builds the action object in one place, so the `type` and `payload` shape stays consistent. Components call the creator, not a hand-written object.

**Q4: What can you pass as the second argument to `createStore`?**
A4: The preloaded (initial) state. It is useful for hydrating state from the server or from saved data.

**Q5: Can two slices respond to the same action?**
A5: Yes. Each slice reducer checks the action type independently. One action can update the cart and the notification count together.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- State has several independent slices (todos, filters, cart, user)
- Many components read different slices from one place
- You want action history for debugging

❌ **Avoid when:**
- You only have one or two small pieces of state
- The data is a cache of server responses (use a server-state library)
- You would write a reducer for every `useState` in the app

---

## 📊 Visual Diagram

```
  addTodo('Buy milk')            filterSet('done')
  { type: 'todos/added' }        { type: 'filter/set' }
          │                              │
          └──────────────┬───────────────┘
                         ▼
                 store.dispatch(action)
                         │
                         ▼
              ┌────────────────────────┐
              │ rootReducer            │  combineReducers({ todos, filter })
              │  ├─ todos(slice, act)  │ ──► [ { id:1, text:'Buy milk' } ]
              │  └─ filter(slice, act) │ ──► 'done'
              └────────────────────────┘
                         │
                         ▼
          store.getState() = { todos: [...], filter: 'done' }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Action | Plain object with a `type` and optional `payload` | `type` और `payload` वाला plain object |
| Action creator | Function that returns an action object | Action object लौटाने वाला function |
| Reducer | Pure function that returns the next slice | अगला slice लौटाने वाला pure function |
| Slice | One part of the state, with its own reducer | State का एक हिस्सा, जिसका अपना reducer है |
| combineReducers | Joins slice reducers into one root reducer | Slice reducers को एक root reducer में जोड़ना |
| Preloaded state | Initial state passed to createStore | `createStore` को दिया गया शुरुआती state |

---

## ⚡ 3-Line Summary
**English:**
1. An action describes what happened, a reducer decides how a slice changes, and the store holds the result.
2. `combineReducers` assembles slice reducers, so each one handles only its own part of the state.
3. Use action creators, because a typo in a plain type string fails silently and produces no change.

**Hindi:**
1. Action बताता है क्या हुआ, reducer तय करता है slice कैसे बदले, और store नतीजा रखता है।
2. `combineReducers` slice reducers को जोड़ता है, ताकि हर reducer सिर्फ अपना हिस्सा सँभाले।
3. Action creators इस्तेमाल करो, क्योंकि plain type string की गलती बिना error के कोई बदलाव नहीं करती।

---

## ➡️ Next Topic
**96. Redux — dispatch + getState** — dispatch का पूरा रास्ता, middleware कैसे बीच में चलते हैं, और `getState` को async logic में कैसे इस्तेमाल करते हैं। Store कैसे बनता है, यह समझने के बाद अब data के बहाव (flow) को देखेंगे।
