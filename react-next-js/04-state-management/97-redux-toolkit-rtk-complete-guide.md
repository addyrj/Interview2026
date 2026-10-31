# 97. Redux Toolkit (RTK) — Complete Guide
# हिंदी में: Redux Toolkit (RTK) — पूरी गाइड

---

## 🔵 Simple Definition (English)
Redux Toolkit is the official, recommended way to write Redux. It removes the boilerplate: `createSlice` writes reducers and action creators together, `configureStore` sets up the store with good defaults, and `createAsyncThunk` handles async requests with pending, fulfilled and rejected states. Immer lets you write "mutating" code that is still immutable underneath.

## 🔵 सरल परिभाषा (Hindi)
Redux Toolkit Redux लिखने का official और recommended तरीका है। यह boilerplate हटाता है: `createSlice` reducers और action creators एक साथ लिखता है, `configureStore` अच्छे defaults के साथ store बनाता है, और `createAsyncThunk` async requests को pending, fulfilled और rejected states के साथ सँभालता है। Immer की वजह से "mutate" जैसा दिखने वाला code अंदर से immutable रहता है।

---

## 🔴 Problem it Solves
Plain Redux needs a lot of repeated code: an action type constant, an action creator, a switch case, and immutable spreads for every change. A small feature like "add to cart" needs four to five pieces in four files. Mistakes are common: a forgotten spread mutates the state, a typo in a type string does nothing, and async flows need hand-written loading flags. RTK puts the type, action creator and reducer in one place and does the immutable update for you.

## 🔴 यह क्यों बना? (Hindi)
Plain Redux में बहुत सारा दोहराया हुआ code लगता है: action type constant, action creator, switch case, और हर बदलाव के लिए immutable spread। "Add to cart" जैसे छोटे feature के लिए चार फ़ाइलों में चार-पाँच टुकड़े लगते हैं। गलतियाँ आम हैं: spread छूटा तो state mutate हो जाता है, type string की typo से कुछ नहीं होता, और async flows में loading flags हाथ से लिखने पड़ते हैं। RTK type, action creator और reducer को एक जगह रखता है और immutable update अपने आप करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → createSlice({ name, initialState, reducers })
         → gives you: slice.reducer (the reducer) and slice.actions (action creators)

Step 2 → configureStore({ reducer: { cart: slice.reducer } })
         → builds the store with thunk middleware and Redux DevTools already added

Step 3 → Component: useSelector(state => state.cart.items) reads data
Step 4 → Component: dispatch(slice.actions.itemAdded(product)) changes data
Step 5 → Inside the reducer, state.items.push(...) is safe: Immer turns it into a new object

Step 6 → Async work: createAsyncThunk creates pending / fulfilled / rejected actions
         extraReducers handles those actions in the slice

KEY: Write "mutating" code inside reducers. RTK (Immer) keeps the update immutable.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → createSlice({ name, initialState, reducers }) से मिलते हैं: reducer और actions
Step 2 → configureStore({ reducer: { cart: slice.reducer } }) store बनाता है, thunk और DevTools के साथ
Step 3 → Component में useSelector(state => state.cart.items) से data पढ़ो
Step 4 → dispatch(slice.actions.itemAdded(product)) से data बदलो
Step 5 → Reducer के अंदर state.items.push(...) सुरक्षित है: Immer इसे नया object बना देता है
Step 6 → Async काम के लिए createAsyncThunk pending/fulfilled/rejected actions बनाता है
KEY: Reducers के अंदर "mutate" जैसा code लिखो। RTK (Immer) update को immutable रखता है।
```

---

## 🟡 Real World Example
**Zomato cart with live totals:** The cart slice has an `items` list and a `couponCode`. "Add" pushes an item with `state.items.push(item)`, which reads like a mutation but is safe. "Apply coupon" starts an async thunk that calls the coupon API. While it loads, the slice shows a spinner (`status: 'loading'`). On success the discount is stored, and on failure the user sees "Invalid coupon". All these states are handled inside one slice file, so the cart screen only reads `status` and `items`.

## 🟡 Real Example Hindi mein
**Zomato cart with live totals:** Cart slice में `items` की list और `couponCode` है। "Add" करने पर `state.items.push(item)` होता है, जो mutation जैसा लगता है पर सुरक्षित है। "Apply coupon" एक async thunk शुरू करता है जो coupon API call करता है। लोड होते समय spinner दिखता है (`status: 'loading'`)। सफल होने पर discount सेव होता है, और असफल होने पर user को "Invalid coupon" दिखता है। ये सारे states एक ही slice file में सँभलते हैं।

---

## 💻 Code Example — Basic

```jsx
// Imports: RTK helpers, plus the React bindings for the store
import { configureStore, createSlice } from '@reduxjs/toolkit';
import { Provider, useSelector, useDispatch } from 'react-redux';

// createSlice: reducer and action creators from ONE definition
const cartSlice = createSlice({
  name: 'cart',                          // prefix for action types: 'cart/itemAdded'
  initialState: { items: [] },           // starting state for this slice
  reducers: {
    // Each function here is a case reducer. The first argument is a DRAFT copy.
    itemAdded(state, action) {
      state.items.push(action.payload);  // "mutation" is safe: Immer makes a new object
    },
    itemRemoved(state, action) {
      // Remove by id: filter the draft array and assign it back
      state.items = state.items.filter((item) => item.id !== action.payload);
    },
  },
});

// Export the action creators for components to call
export const { itemAdded, itemRemoved } = cartSlice.actions;

// configureStore: builds the store with thunk middleware and DevTools by default
const store = configureStore({
  reducer: { cart: cartSlice.reducer }, // the state key "cart" maps to this reducer
});

// A component that shows the cart and a button to add an item
function Cart() {
  const items = useSelector((state) => state.cart.items); // read the slice
  const dispatch = useDispatch();                         // get dispatch

  return (
    <div>
      <p>Items in cart: {items.length}</p>
      <button onClick={() => dispatch(itemAdded({ id: Date.now(), name: 'Biryani' }))}>
        Add biryani
      </button>
    </div>
  );
}

// Provider makes the store available to every component below it
export default function App() {
  return (
    <Provider store={store}>
      <Cart />
    </Provider>
  );
}
```

## 💻 Code Example — Advanced

```javascript
// Run: npm i @reduxjs/toolkit && node file.js
import { configureStore, createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// createAsyncThunk: makes three actions: '<name>/pending', '<name>/fulfilled', '<name>/rejected'
// The payload creator is an async function. rejectWithValue sends a custom error payload.
export const fetchProducts = createAsyncThunk(
  'products/fetch',                                  // action type prefix
  async (category, { rejectWithValue }) => {        // category = the thunk argument
    try {
      // Fake API: fails for an unknown category, succeeds otherwise
      if (category === 'unknown') throw new Error('No such category');
      await new Promise((r) => setTimeout(r, 10));  // simulate network delay
      return [{ id: 1, name: 'Biryani', category }]; // returned value becomes the fulfilled payload
    } catch (err) {
      return rejectWithValue(err.message);          // becomes action.payload in rejected
    }
  }
);

const productsSlice = createSlice({
  name: 'products',
  // status tracks the request: 'idle' | 'loading' | 'succeeded' | 'failed'
  initialState: { items: [], status: 'idle', error: null },
  reducers: {},                                     // no sync reducers needed here
  // extraReducers reacts to actions created OUTSIDE this slice (the thunk actions)
  extraReducers: (builder) => {
    builder
      .addCase(fetchProducts.pending, (state) => {
        state.status = 'loading';                   // show spinner
        state.error = null;                         // clear the old error
      })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.items = action.payload;               // data from the thunk's return value
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;               // the value passed to rejectWithValue
      });
  },
});

const store = configureStore({ reducer: { products: productsSlice.reducer } });

// dispatch(thunk) returns a promise that resolves with the final action
async function main() {
  const result = await store.dispatch(fetchProducts('biryani')); // success path
  console.log(result.type);                         // 'products/fetch/fulfilled'
  console.log(store.getState().products.status);    // 'succeeded'

  const failed = await store.dispatch(fetchProducts('unknown')); // error path
  console.log(failed.type);                         // 'products/fetch/rejected'
  console.log(store.getState().products.error);     // 'No such category'
}

main();
```

---

## 🟠 Real App Integration (React + Next.js)

In a Next.js App Router project, the store lives in a Client Component wrapper (same rule as topic 94). The `useSelector` hook reads only the slice it needs, so the cart can update without re-rendering the product grid.

```jsx
// app/products/ProductGrid.jsx — Client Component reading the RTK slice
'use client';
import { useSelector, useDispatch } from 'react-redux';
import { fetchProducts } from '../../lib/productsSlice';

export default function ProductGrid() {
  const { items, status, error } = useSelector((s) => s.products); // read the slice
  const dispatch = useDispatch();

  if (status === 'loading') return <p>Loading…</p>;               // pending state
  if (status === 'failed') return <p>Error: {error}</p>;          // rejected state

  return (
    <div>
      <button onClick={() => dispatch(fetchProducts('biryani'))}>Load biryani</button>
      <ul>{items.map((p) => <li key={p.id}>{p.name}</li>)}</ul>
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Returning a new value AND mutating the draft in the same reducer
✅ **Correct:** Do one or the other. Immer throws an error when both happen.

```javascript
// Wrong: mutates the draft and also returns a new object
itemAdded(state, action) {
  state.items.push(action.payload);     // mutation
  return { items: [...state.items] };   // ❌ returning too: Immer throws
}

// Right: mutate the draft, return nothing
itemAdded(state, action) {
  state.items.push(action.payload);     // ✅ Immer makes the new object for you
}
```

❌ **Mistake 2:** Writing `reducers` for async results instead of `extraReducers`
✅ **Correct:** Async results come from `createAsyncThunk` actions, so handle them in `extraReducers` (or with `builder.addCase`), not in the `reducers` object.

```javascript
// Wrong: the 'fulfilled' action type is never matched here
reducers: {
  'products/fetch/fulfilled': (state, action) => { state.items = action.payload; } // ❌
}

// Right: handle the thunk actions in extraReducers
extraReducers: (builder) => {
  builder.addCase(fetchProducts.fulfilled, (state, action) => {
    state.items = action.payload;       // ✅
  });
}
```

---

## 🧠 Tricky Interview Question

```javascript
// Run: npm i @reduxjs/toolkit && node file.js
import { configureStore, createSlice } from '@reduxjs/toolkit';

const counter = createSlice({
  name: 'counter',
  initialState: { value: 0 },
  reducers: {
    increment(state) {
      state.value += 1;               // looks like a mutation
    },
  },
});

const store = configureStore({ reducer: { counter: counter.reducer } });

const before = store.getState().counter;        // snapshot before the action
store.dispatch(counter.actions.increment());
const after = store.getState().counter;         // snapshot after the action

console.log(before.value, after.value, before === after);
```

**Answer:** The output is `0 1 false`. The reducer writes `state.value += 1`, which looks like it mutates the store's object. Immer works on a draft, so the original `before` object is left alone and `before.value` stays `0`. Immer creates a new state object for the change, so `after` is a different reference and `before === after` is `false`. Unchanged parts of the tree are shared, which is why Immer is fast. If you wrote the same code in plain Redux, you would get `1 1 true`.

---

## ⚫ Interview Questions + Answers

**Q1: What does `createSlice` return?**
A1: An object with `name`, `reducer` (the slice reducer, to pass to `configureStore`) and `actions` (action creators keyed by the reducer names).

**Q2: What does `configureStore` add that `createStore` does not?**
A2: It adds thunk middleware, Redux DevTools support and development checks (immutability and serializability) by default. It also accepts a `reducer` object and combines the reducers for you.

**Q3: What are the three action types that `createAsyncThunk` dispatches?**
A3: `pending` when the request starts, `fulfilled` with the return value on success, and `rejected` with an error when the payload creator throws or `rejectWithValue` is used.

**Q4: How does Immer make "mutating" code safe?**
A4: Each reducer receives a draft proxy. Changes are recorded on the draft, and Immer produces a new immutable object with structural sharing for the unchanged parts.

**Q5: When should you use `extraReducers` instead of `reducers`?**
A5: When the slice must respond to actions defined elsewhere, such as the actions generated by `createAsyncThunk` or actions from other slices. `reducers` is only for actions the slice creates itself.

---

## 🔷 When to Use + When Not to Use
✅ **Use RTK when:**
- You use Redux at all (it is the recommended default)
- You have async requests that need loading and error states
- You want DevTools and sensible defaults without manual setup

❌ **Avoid when:**
- The state is only server data that RTK Query (topic 100) or another library handles better
- The app has one small piece of shared state that Context handles well (topic 93)
- You are maintaining an old codebase where a rewrite to RTK is not planned

---

## 📊 Visual Diagram

```
          createSlice({ name:'cart', reducers:{ itemAdded } })
                 │                         │
           slice.reducer              slice.actions.itemAdded
                 │                         │
                 ▼                         │
   configureStore({ reducer:{ cart } })    │  dispatch(itemAdded(product))
   (thunk + devtools included)  ◄──────────┘
                 │
                 ▼
   state.cart.items  ──► useSelector ──► component re-renders

ASYNC:
   dispatch(fetchProducts('x'))
        ├── fetchProducts/pending    → status = 'loading'
        ├── (await API)
        └── fetchProducts/fulfilled  → status = 'succeeded', items = payload
                 or fetchProducts/rejected → status = 'failed', error = payload
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| createSlice | Makes a reducer and action creators together | Reducer और action creators एक साथ बनाना |
| configureStore | Creates the store with good defaults | अच्छे defaults के साथ store बनाना |
| createAsyncThunk | Creates pending, fulfilled, rejected actions for async work | Async काम के लिए तीन actions बनाना |
| extraReducers | Handles actions defined outside the slice | Slice के बाहर के actions सँभालना |
| Immer | Lets you write mutations that stay immutable | Mutation जैसा code लिखने देना जो immutable रहे |
| Draft | The mutable proxy that reducers receive | Reducer को मिलने वाला mutable proxy |

---

## ⚡ 3-Line Summary
**English:**
1. RTK's `createSlice`, `configureStore` and `createAsyncThunk` replace most manual Redux boilerplate.
2. Reducers may mutate the draft safely because Immer produces the new immutable state.
3. Handle async results in `extraReducers` with pending, fulfilled and rejected cases.

**Hindi:**
1. RTK के `createSlice`, `configureStore` और `createAsyncThunk` ज़्यादातर manual Redux boilerplate की जगह लेते हैं।
2. Reducers draft को सुरक्षित रूप से mutate कर सकते हैं, क्योंकि Immer नया immutable state बनाता है।
3. Async नतीजे `extraReducers` में pending, fulfilled और rejected cases से सँभालो।

---

## ➡️ Next Topic
**98. createSlice + configureStore** — इन दो APIs को गहराई से देखना: slice की structure, `prepare` callback, middleware और store की setup। RTK का overview समझने के बाद अब सबसे ज़्यादा इस्तेमाल होने वाले दो tools को बारीकी से सीखेंगे।
