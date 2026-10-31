# 98. createSlice + configureStore
# हिंदी में: createSlice + configureStore — Slice बनाना और Store सेट करना

---

## 🔵 Simple Definition (English)
`createSlice` builds one piece of state with its reducer and action creators in a single call. `configureStore` takes one or more slices and creates the Redux store with thunk middleware, DevTools and development checks already enabled. Together they are the standard setup for every modern Redux app.

## 🔵 सरल परिभाषा (Hindi)
`createSlice` एक call में state का एक हिस्सा, उसका reducer और action creators बनाता है। `configureStore` एक या ज़्यादा slices लेकर Redux store बनाता है, जिसमें thunk middleware, DevTools और development checks पहले से चालू होते हैं। साथ मिलकर ये हर आधुनिक Redux app का standard setup हैं।

---

## 🔴 Problem it Solves
Before RTK, adding one slice meant writing its action type constants, action creators, reducer switch and then wiring middleware by hand with `applyMiddleware`, plus adding the Redux DevTools extension manually. Each developer did it slightly differently, so setups diverged. Bugs like mutating state or forgetting the thunk middleware were common. `createSlice` makes the pattern one object, and `configureStore` makes the store setup one call with safe defaults.

## 🔴 यह क्यों बना? (Hindi)
RTK से पहले एक slice जोड़ने के लिए action type constants, action creators और reducer switch लिखने पड़ते थे, फिर `applyMiddleware` से middleware हाथ से जोड़ना पड़ता था, और DevTools extension खुद जोड़ना होता था। हर developer थोड़ा अलग तरीके से करता था, इसलिए setups बिखर जाते थे। State mutate करना या thunk middleware भूल जाना आम गलतियाँ थीं। `createSlice` पूरे pattern को एक object में रखता है, और `configureStore` store setup को safe defaults के साथ एक call में।

---

## 🟢 How it Works — Step by Step

```
Step 1 → createSlice({ name, initialState, reducers })
         name           → prefix for action types ('counter')
         initialState   → starting value for this slice
         reducers       → functions that change the slice (Immer draft inside)

Step 2 → Generated for each reducer key:
         action creator:  counter.actions.increment(payload) → { type: 'counter/increment', payload }
         reducer:         counter.reducer(state, action)

Step 3 → configureStore({ reducer: { counter: counter.reducer } })
         → combines slice reducers, adds thunk middleware, enables DevTools

Step 4 → store.dispatch(counter.actions.increment(5)) → reducer updates state.value
Step 5 → store.getState().counter → { value: 5 }

KEY: The NAME + KEY of each reducer decides the action type string. Keep names unique.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → createSlice({ name, initialState, reducers }) लिखो
         name         → action types का prefix ('counter')
         initialState → इस slice की शुरुआती value
         reducers     → functions जो slice बदलते हैं (अंदर Immer draft)
Step 2 → हर reducer key के लिए बनता है:
         action creator: counter.actions.increment(payload)
         reducer:        counter.reducer(state, action)
Step 3 → configureStore({ reducer: { counter: counter.reducer } }) store बनाता है
Step 4 → dispatch(counter.actions.increment(5)) से state.value बदलता है
Step 5 → store.getState().counter → { value: 5 }
KEY: हर reducer का name + key action type तय करते हैं। नाम अलग-अलग रखो।
```

---

## 🟡 Real World Example
**Swiggy restaurant filter bar:** The `filters` slice holds `veg`, `rating` and `sortBy`. The `setRating` reducer receives a number, and the `reset` reducer takes no payload. `configureStore` combines the `filters` slice with the `cart` and `user` slices. Changing the rating dispatches `filters/setRating(4)` and only the restaurant list re-renders, because it is the only component that selects the `rating` field.

## 🟡 Real Example Hindi mein
**Swiggy restaurant filter bar:** `filters` slice में `veg`, `rating` और `sortBy` हैं। `setRating` reducer एक number लेता है, और `reset` reducer बिना payload के चलता है। `configureStore` `filters` slice को `cart` और `user` slices के साथ जोड़ता है। Rating बदलने पर `filters/setRating(4)` dispatch होता है, और सिर्फ restaurant list re-render होती है, क्योंकि वही `rating` field select करती है।

---

## 💻 Code Example — Basic

```javascript
// Run: npm i @reduxjs/toolkit && node file.js
import { createSlice, configureStore } from '@reduxjs/toolkit';

// Define the slice: name, starting state and reducers in one object
const counterSlice = createSlice({
  name: 'counter',                  // action types become 'counter/increment' etc.
  initialState: { value: 0 },       // the slice state on first load
  reducers: {
    increment(state) {
      state.value += 1;             // Immer: this edit produces a new object
    },
    decrement(state) {
      state.value -= 1;
    },
    incrementByAmount(state, action) {
      state.value += action.payload; // payload = the number passed to the creator
    },
  },
});

// The generated action creators, ready to use
const { increment, decrement, incrementByAmount } = counterSlice.actions;

// configureStore: pass an object of slice reducers, get a full store
const store = configureStore({
  reducer: {
    counter: counterSlice.reducer,  // key "counter" becomes state.counter
  },
});

console.log(store.getState());      // { counter: { value: 0 } }

store.dispatch(increment());        // no payload, so the creator takes no argument
store.dispatch(incrementByAmount(5));
store.dispatch(decrement());
console.log(store.getState().counter.value); // 5
```

## 💻 Code Example — Advanced

```javascript
// Run: npm i @reduxjs/toolkit && node file.js
import { createSlice, configureStore, nanoid } from '@reduxjs/toolkit';

// Slice for a shopping list, using a 'prepare' callback for the action creator
const listSlice = createSlice({
  name: 'list',
  initialState: { entries: [], lastAddedId: null },
  reducers: {
    // prepare: builds the action in the creator. Here it generates a unique id.
    // The reducer then receives a clean { id, text } payload and needs no randomness.
    itemAdded: {
      reducer(state, action) {
        state.entries.push(action.payload);          // payload already has the id
        state.lastAddedId = action.payload.id;       // remember the newest id
      },
      prepare(text) {
        // Called by listSlice.actions.itemAdded(text). Returns the full action.
        return { payload: { id: nanoid(), text: text.trim() } };
      },
    },
    itemToggled(state, action) {
      // Find the entry with this id, then flip its flag directly (Immer draft)
      const entry = state.entries.find((e) => e.id === action.payload);
      if (entry) entry.done = !entry.done;          // missing id: do nothing
    },
  },
});

export const { itemAdded, itemToggled } = listSlice.actions;

// Selectors: functions that read a value from the whole state (keep logic out of components)
export const selectEntries = (state) => state.list.entries;
export const selectOpenCount = (state) =>
  state.list.entries.filter((e) => !e.done).length;   // derived value, computed on read

// Store with custom middleware options. getDefaultMiddleware returns the defaults.
const store = configureStore({
  reducer: { list: listSlice.reducer },
  // preloadedState: starting data (for example from localStorage on the client)
  preloadedState: { list: { entries: [], lastAddedId: null } },
  middleware: (getDefaultMiddleware) =>
    // Keep the defaults (thunk, immutability and serializability checks) and add more
    getDefaultMiddleware({
      serializableCheck: { ignoredActions: [] }, // default check; list ignored actions here
    }),
  devTools: true,                                  // explicit: show the state in DevTools
});

// Use the actions and selectors
store.dispatch(itemAdded('  Buy milk  '));        // prepare trims the text and adds an id
store.dispatch(itemAdded('Call mom'));
const firstId = store.getState().list.entries[0].id;
store.dispatch(itemToggled(firstId));

console.log(selectEntries(store.getState()).map((e) => e.text)); // [ 'Buy milk', 'Call mom' ]
console.log(selectOpenCount(store.getState()));                   // 1
```

---

## 🟠 Real App Integration (React + Next.js)

In Next.js, create the store with `configureStore` inside a factory and pass it through a Client Component `Provider` (topic 94 rule). Selectors defined beside the slice keep components short and make the logic testable without rendering.

```jsx
// lib/store.js — factory used by the client-side Provider
import { configureStore } from '@reduxjs/toolkit';
import listReducer from './listSlice';         // default export: listSlice.reducer

export function makeStore(preloadedState) {
  return configureStore({
    reducer: { list: listReducer },           // one key per slice
    preloadedState,                           // state from the server, if any
  });
}
```

```jsx
// app/list/ListCount.jsx — Client Component uses the selector, not raw state paths
'use client';
import { useSelector } from 'react-redux';
import { selectOpenCount } from '../../lib/listSlice'; // selector defined next to the slice

export default function ListCount() {
  const open = useSelector(selectOpenCount);  // subscribes only to this derived number
  return <p>{open} items left</p>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Two slices with the same `name`
✅ **Correct:** The name is the prefix for action types. Duplicates make actions from one slice trigger the other's reducer.

```javascript
// Wrong: both slices produce 'items/add' actions, so one dispatch changes both
const cartSlice = createSlice({ name: 'items', /* ... */ });
const wishSlice = createSlice({ name: 'items', /* ... */ }); // ❌ same name

// Right: unique names per slice
const cartSlice = createSlice({ name: 'cart', /* ... */ });    // ✅ cart/...
const wishSlice = createSlice({ name: 'wishlist', /* ... */ }); // ✅ wishlist/...
```

❌ **Mistake 2:** Replacing the whole state in a reducer without returning it
✅ **Correct:** Either mutate the draft or return a new value, but do not assign to the `state` variable itself.

```javascript
// Wrong: assigning to the parameter does nothing to the store
reset(state) {
  state = { value: 0 };     // ❌ rebinds the local name only
}

// Right: return the new value (or mutate the draft's fields)
reset() {
  return { value: 0 };      // ✅ new state returned
}
```

---

## 🧠 Tricky Interview Question

```javascript
// Run: npm i @reduxjs/toolkit && node file.js
import { createSlice, configureStore } from '@reduxjs/toolkit';

const slice = createSlice({
  name: 'counter',
  initialState: { value: 0 },
  reducers: {
    broken(state) {
      state = { value: 99 };      // assignment to the parameter, not to state.value
    },
    working(state) {
      state.value = 99;           // mutate the draft's field
    },
  },
});

const store = configureStore({ reducer: { counter: slice.reducer } });

store.dispatch(slice.actions.broken());
console.log(store.getState().counter.value);

store.dispatch(slice.actions.working());
console.log(store.getState().counter.value);
```

**Answer:** The output is `0` then `99`. In `broken`, `state = { value: 99 }` only rebinds the local parameter `state` to a new object. Immer sees that nothing was mutated and nothing was returned, so the draft is unchanged and the store keeps `value: 0`. The reducer did not throw, so the bug is silent. In `working`, `state.value = 99` changes the draft's field, Immer creates the new state, and the store shows `99`. The rule: assign fields on the draft, or return a value, never reassign the parameter.

---

## ⚫ Interview Questions + Answers

**Q1: What does `createSlice` generate?**
A1: A `reducer` function and an `actions` object with one action creator per reducer key. Action types are built as `name/reducerKey`.

**Q2: What is the purpose of the `prepare` callback?**
A2: It lets the action creator build the payload (for example generate an id or trim input) before the reducer runs. The reducer then stays pure and receives a ready payload.

**Q3: What does `configureStore` add by default?**
A3: The thunk middleware, Redux DevTools integration, and development checks for mutations and non-serializable values. It also combines the reducers object into one root reducer.

**Q4: What is a selector and why use one?**
A4: A function that reads a value from the state, such as `state => state.list.entries`. It keeps state paths out of components, and derived selectors can compute values like counts on read.

**Q5: Why does `state = {...}` inside a reducer not update the store?**
A5: The reducer receives a draft by parameter. Reassigning the parameter only changes the local variable. To update, mutate fields on the draft or return a new value.

---

## 🔷 When to Use + When Not to Use
✅ **Use `createSlice` + `configureStore` when:**
- You start any new Redux project (the official default)
- Each feature has its own slice of state with its own actions
- You want DevTools and development checks without setup

❌ **Avoid when:**
- The app needs only one shared value; `useState` or Context is enough (topic 93)
- The data is server cache (RTK Query in topic 100 is simpler)
- You add many slices with overlapping names and no structure

---

## 📊 Visual Diagram

```
createSlice({ name:'list', initialState, reducers:{ itemAdded:{reducer, prepare} } })
   │
   ├── slice.reducer  ──────────────────────────┐
   └── slice.actions.itemAdded(text)            │
            │                                    │
            │ prepare(text) → { payload: {id, text} }
            ▼                                    ▼
         dispatch ───────────────►  configureStore({
                                      reducer: { list: slice.reducer },
                                      middleware: thunk + checks,
                                      devTools: true
                                    })
                                             │
                                             ▼
                                  store.getState().list.entries
                                             │
                                             ▼
                                  selectOpenCount(state) → number
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Slice | One feature's state, reducer and actions | एक feature का state, reducer और actions |
| Action creator | Generated function that returns an action | Generated function जो action लौटाता है |
| prepare callback | Builds the action payload before the reducer | Reducer से पहले payload बनाने वाला callback |
| configureStore | Creates the store with defaults | Defaults के साथ store बनाना |
| preloadedState | Initial state for the store | Store की शुरुआती state |
| Selector | Function that reads a value from state | State से value पढ़ने वाला function |

---

## ⚡ 3-Line Summary
**English:**
1. `createSlice` makes a reducer and action creators in one object; action types are `name/key`.
2. `configureStore` combines slice reducers and adds thunk, DevTools and development checks.
3. Use `prepare` for payload work and selectors for reads, and never reassign the `state` parameter.

**Hindi:**
1. `createSlice` एक object में reducer और action creators बनाता है; action types `name/key` होते हैं।
2. `configureStore` slice reducers को जोड़ता है और thunk, DevTools और development checks जोड़ता है।
3. Payload का काम `prepare` से और reads के लिए selectors इस्तेमाल करो, और `state` parameter को कभी reassign मत करो।

---

## ➡️ Next Topic
**99. Redux Thunk — Async Actions** — Async logic को thunk functions में लिखने का पूरा तरीका, जिसकी नींव आपने topic 96 में देखी। RTK के `createAsyncThunk` के साथ अब async flows कैसे सुरक्षित रहते हैं, यह देखेंगे।
