# 86. Redux Toolkit in React Native
# हिंदी में: React Native में Redux Toolkit
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK version:** examples target **Expo SDK 52 (React Native 0.76, React 18.3)** with `@reduxjs/toolkit` 2.x + `react-redux` 9.x — check current docs — APIs change between SDKs/versions. (Redux Toolkit pure JS है — कोई native code नहीं, इसलिए Expo Go में भी चलता है।)

---

## 🔵 Simple Definition (English)
**Redux Toolkit (RTK)** is the official, opinionated way to use **Redux**: one global **store**, state split into **slices**, changes only via **actions** handled by **reducers**. RTK removes boilerplate (`configureStore`, `createSlice`, `createAsyncThunk`, RTK Query) and lets you write "mutating" code safely thanks to **Immer**.

## 🔵 सरल परिभाषा (Hindi)
**Redux Toolkit (RTK)** **Redux** use करने का official तरीका है: एक global **store**, state **slices** में बँटा हुआ, बदलाव सिर्फ़ **actions** से जो **reducers** handle करते हैं। RTK boilerplate हटाता है (`configureStore`, `createSlice`, `createAsyncThunk`, RTK Query) और **Immer** की वजह से "mutating" जैसा code सुरक्षित लिखने देता है।

---

## 🔴 Problem it Solves
```
❌ Context/useState se bada app: state bikhri hui, debug mushkil
❌ Plain Redux: bahut boilerplate (action types, creators, switch/case, spread copies)
❌ Async logic ka koi standard pattern nahi
✅ RTK: predictable single store + DevTools + kam code + async + caching (RTK Query)
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ Context/useState से बड़ा app: state बिखरी हुई, debug मुश्किल
❌ Plain Redux: बहुत boilerplate (action types, creators, switch/case, spread copies)
❌ Async logic का कोई standard pattern नहीं
✅ RTK: predictable single store + DevTools + कम code + async + caching (RTK Query)
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npm i @reduxjs/toolkit react-redux
Step 2 → createSlice({name, initialState, reducers}) -> reducer + actions
Step 3 → configureStore({reducer: {cart: cartReducer}}) -> store
Step 4 → <Provider store={store}> wraps the app (above NavigationContainer)
Step 5 → Read: const items = useSelector(s => s.cart.items)
Step 6 → Write: const dispatch = useDispatch(); dispatch(addItem(x))
Step 7 → Reducer (Immer) -> new immutable state -> only subscribed components re-render
Step 8 → Async: createAsyncThunk -> pending / fulfilled / rejected actions
Step 9 → Persist: redux-persist + AsyncStorage (or MMKV) saves slices
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → npm i @reduxjs/toolkit react-redux
Step 2 → createSlice({name, initialState, reducers}) -> reducer + actions
Step 3 → configureStore({reducer: {cart: cartReducer}}) -> store
Step 4 → <Provider store={store}> पूरे app को wrap करता है (NavigationContainer के ऊपर)
Step 5 → पढ़ो: const items = useSelector(s => s.cart.items)
Step 6 → लिखो: const dispatch = useDispatch(); dispatch(addItem(x))
Step 7 → Reducer (Immer) -> नया immutable state -> सिर्फ़ subscribed components re-render
Step 8 → Async: createAsyncThunk -> pending / fulfilled / rejected actions
Step 9 → Persist: redux-persist + AsyncStorage (या MMKV) से slices save
```

---

## 🟡 Real World Example
**Swiggy/Zomato cart**: `cartSlice` (items, coupon), `authSlice` (token, user), `ordersSlice` (history via `createAsyncThunk`). Header cart badge uses `useSelector(selectCartCount)` and re-renders only when count changes. **Paytm**: wallet balance slice + RTK Query for transaction history with caching.

## 🟡 Real Example Hindi mein
**Swiggy/Zomato cart**: `cartSlice` (items, coupon), `authSlice` (token, user), `ordersSlice` (history, `createAsyncThunk` से)। Header का cart badge `useSelector(selectCartCount)` use करता है और सिर्फ़ count बदलने पर re-render होता है। **Paytm**: wallet balance slice + transaction history के लिए RTK Query (caching के साथ)।

---

## 💻 Code Example — Basic
```jsx
// Basic: cart slice + store + Provider + component
// npm i @reduxjs/toolkit react-redux   (Expo: npx expo install not required; pure JS)
import React from 'react';                                          // React
import { View, Text, Button } from 'react-native';                  // UI
import { configureStore, createSlice } from '@reduxjs/toolkit';     // RTK
import { Provider, useSelector, useDispatch } from 'react-redux';   // bindings

// 1. Slice: state + reducers in one place
const cartSlice = createSlice({
  name: 'cart',                                                     // prefix for action types
  initialState: { items: {} },                                      // { [id]: qty }
  reducers: {
    addItem(state, action) {                                        // action.payload = id
      const id = action.payload;
      state.items[id] = (state.items[id] ?? 0) + 1;                 // "mutation" OK: Immer
    },
    removeItem(state, action) {
      const id = action.payload;
      if (!state.items[id]) return;                                 // nothing to remove
      state.items[id] -= 1;                                         // decrement
      if (state.items[id] === 0) delete state.items[id];            // delete at 0
    },
    clearCart(state) { state.items = {}; },                         // empty
  },
});
export const { addItem, removeItem, clearCart } = cartSlice.actions; // action creators

// 2. Store
export const store = configureStore({ reducer: { cart: cartSlice.reducer } });

// 3. Selector (reusable)
const selectCount = (s) => Object.values(s.cart.items).reduce((a, b) => a + b, 0);

function CartBar() {
  const count = useSelector(selectCount);                           // subscribe to count only
  const dispatch = useDispatch();                                   // get dispatch
  return (
    <View style={{ padding: 20 }}>
      <Text>Cart items: {count}</Text>
      <Button title="Add biryani" onPress={() => dispatch(addItem('b1'))} />
      <Button title="Remove biryani" onPress={() => dispatch(removeItem('b1'))} />
      <Button title="Clear" onPress={() => dispatch(clearCart())} />
    </View>
  );
}

export default function App() {
  return (
    <Provider store={store}>{/* make store available */}
      <CartBar />
    </Provider>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: createAsyncThunk (login/orders), typed-safe selectors with createSelector,
// redux-persist with AsyncStorage, and Provider + PersistGate order
// npm i redux-persist @react-native-async-storage/async-storage
import React from 'react';                                          // React
import { ActivityIndicator, Text, Button, View } from 'react-native'; // UI
import {
  configureStore, createSlice, createAsyncThunk, createSelector, combineReducers,
} from '@reduxjs/toolkit';                                          // RTK APIs
import { Provider, useSelector, useDispatch } from 'react-redux';   // bindings
import AsyncStorage from '@react-native-async-storage/async-storage'; // storage engine
import {
  persistStore, persistReducer, FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER,
} from 'redux-persist';                                             // persistence
import { PersistGate } from 'redux-persist/integration/react';      // delay UI until rehydrated

// ---------- async thunk ----------
export const fetchOrders = createAsyncThunk(
  'orders/fetch',                                                   // action type prefix
  async (userId, { rejectWithValue }) => {                          // payload creator
    try {
      const res = await fetch(`https://jsonplaceholder.typicode.com/posts?userId=${userId}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);           // HTTP errors
      return await res.json();                                      // becomes action.payload
    } catch (e) {
      return rejectWithValue(e.message);                            // becomes action.payload on reject
    }
  }
);

const ordersSlice = createSlice({
  name: 'orders',
  initialState: { list: [], status: 'idle', error: null },          // status machine
  reducers: {},
  extraReducers: (builder) => {                                     // handle thunk lifecycle
    builder
      .addCase(fetchOrders.pending, (s) => { s.status = 'loading'; s.error = null; })
      .addCase(fetchOrders.fulfilled, (s, a) => { s.status = 'succeeded'; s.list = a.payload; })
      .addCase(fetchOrders.rejected, (s, a) => { s.status = 'failed'; s.error = a.payload ?? a.error.message; });
  },
});

const authSlice = createSlice({
  name: 'auth',
  initialState: { token: null, user: null },
  reducers: {
    loggedIn: (s, a) => { s.token = a.payload.token; s.user = a.payload.user; },
    loggedOut: (s) => { s.token = null; s.user = null; },
  },
});
export const { loggedIn, loggedOut } = authSlice.actions;

// ---------- store with persistence ----------
const rootReducer = combineReducers({ auth: authSlice.reducer, orders: ordersSlice.reducer });
const persisted = persistReducer(
  { key: 'root', storage: AsyncStorage, whitelist: ['auth'] },      // persist ONLY auth
  rootReducer
);
export const store = configureStore({
  reducer: persisted,
  middleware: (getDefault) =>
    getDefault({
      serializableCheck: {                                          // redux-persist actions are non-serializable
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }),
});
export const persistor = persistStore(store);

// ---------- memoised selector ----------
const selectOrders = (s) => s.orders.list;
export const selectOrderCount = createSelector([selectOrders], (list) => list.length);

function Orders() {
  const dispatch = useDispatch();
  const { status, error } = useSelector((s) => s.orders);
  const count = useSelector(selectOrderCount);
  const user = useSelector((s) => s.auth.user);
  return (
    <View style={{ padding: 20 }}>
      <Text>{user ? `Hi ${user.name}` : 'Logged out'}</Text>
      <Button title="Login (fake)" onPress={() => dispatch(loggedIn({ token: 't', user: { name: 'Aditya' } }))} />
      <Button title="Load orders" onPress={() => dispatch(fetchOrders(1))} />
      {status === 'loading' && <ActivityIndicator />}
      {status === 'failed' && <Text style={{ color: 'red' }}>{error}</Text>}
      <Text>Orders: {count}</Text>
    </View>
  );
}

export default function App() {
  return (
    <Provider store={store}>
      <PersistGate loading={<ActivityIndicator />} persistor={persistor}>
        <Orders />
      </PersistGate>
    </Provider>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Redux logic | Same | Same |
| Persisted storage | AsyncStorage (SQLite-backed, 6MB default limit) | AsyncStorage (file-based) |
| Redux DevTools | Flipper plugin (older) / React Native DevTools / Reactotron | Same |
| App killed in background | More frequent -> rehydrate often | Less frequent |
| Large state serialisation | Slower on low-end devices | Faster, but still avoid huge blobs |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Pure JS: works in Expo Go. Persist storage via Expo-compatible package:
npx expo install @react-native-async-storage/async-storage
npm install @reduxjs/toolkit react-redux redux-persist
```
CLI way:
```bash
npm install @reduxjs/toolkit react-redux redux-persist @react-native-async-storage/async-storage
cd ios && pod install && cd ..     # AsyncStorage is native -> rebuild the app
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Mutating state outside a reducer
```jsx
const items = useSelector(s => s.cart.items); items.b1 = 5;   // ❌ mutates store state
```
✅ Correct: dispatch an action; mutate only inside `createSlice` reducers (Immer).

❌ Mistake 2: Selecting a new object every time
```jsx
useSelector(s => ({ a: s.a, b: s.b }));   // ❌ new object each call -> re-render every dispatch
```
✅ Correct: select primitives separately, or use `createSelector`/`shallowEqual`.

❌ Mistake 3: Putting non-serializable values (functions, Date, class instances, navigation objects) in state
✅ Correct: store ISO strings/ids; keep functions outside the store.

❌ Mistake 4: Persisting everything (including server cache and loading flags)
✅ Correct: `whitelist` only what's needed (auth, settings).

❌ Mistake 5: `Provider` placed below `NavigationContainer` that screens need
✅ Correct: Provider at the very top.

---

## 🧠 Tricky Interview Question
**Q: In `createSlice` you write `state.items.push(x)` — isn't that mutating state? Why is it allowed?**

**Answer:** Inside RTK reducers, `state` is an **Immer draft proxy**, not the real state. Immer records your "mutations" and produces a **new immutable object** with structural sharing. So you either mutate the draft **or** return a new value — **never both** in the same reducer (Immer throws). Outside reducers (components, thunks) state is plain frozen data in dev, so mutation there throws/behaves wrongly. Also, `useSelector` uses reference equality, so returning new objects from a selector causes unnecessary re-renders.

---

## ⚫ Interview Questions + Answers

**Q1: Redux vs Redux Toolkit?**
A1: RTK is the official toolset on top of Redux: less boilerplate, Immer, thunks, DevTools by default, good defaults.

**Q2: What is a slice?**
A2: A piece of state with its reducers and generated actions (`createSlice`).

**Q3: `createAsyncThunk` lifecycle?**
A3: Dispatches `pending`, then `fulfilled` (payload) or `rejected` (error); handled in `extraReducers`.

**Q4: RTK Query vs React Query?**
A4: RTK Query is built into RTK, integrates with the store (cache in Redux, generated hooks). React Query is standalone and store-agnostic. Both handle caching, refetching, invalidation.

**Q5: When Redux over Context/Zustand?**
A5: Large teams, complex cross-feature state, middleware, time-travel debugging, strict patterns. Zustand is lighter for small/medium apps.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Large app, many screens sharing state (auth, cart, orders)
- Need DevTools, middleware, strict predictable updates
- Team already knows Redux

❌ Avoid when:
- Small app (useState/Context is enough)
- Only server data (React Query/RTK Query alone)
- High-frequency UI state (animations, input text) — keep local

---

## 📊 Visual Diagram
```
 UI (component) ──dispatch(addItem('b1'))──► STORE
      ▲                                        │
      │                              reducer (Immer draft)
      │                                        ▼
      └────── useSelector(selectCount) ◄── new state

Async:  dispatch(fetchOrders)
          -> pending -> [API] -> fulfilled/rejected -> reducers
Persist: store ──redux-persist──► AsyncStorage ──REHYDRATE──► store
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Store | Single global state container | एक global state container |
| Slice | State + reducers + actions | State + reducers + actions का समूह |
| Action | Object describing a change | बदलाव बताने वाला object |
| Reducer | Pure function (state, action) -> state | Pure function जो नया state देता है |
| Thunk | Function for async logic | Async logic वाला function |
| Selector | Reads data from store | Store से data पढ़ने वाला function |
| Immer | Lets you write mutating-style code safely | Mutating-style code सुरक्षित बनाता है |

---

## ⚡ 3-Line Summary
**English:**
1. RTK = `configureStore` + `createSlice` + thunks; one store, predictable updates.
2. Wrap app in `Provider`; read with `useSelector`, write with `dispatch`.
3. Persist only needed slices; avoid non-serializable state and unstable selectors.

**Hindi:**
1. RTK = `configureStore` + `createSlice` + thunks; एक store, predictable updates।
2. App को `Provider` में wrap करो; `useSelector` से पढ़ो, `dispatch` से लिखो।
3. सिर्फ़ ज़रूरी slices persist करो; non-serializable state और unstable selectors से बचो।

---

## ➡️ Next Topic
**87. MMKV Storage (Fast Storage)** — AsyncStorage से कई गुना तेज़ synchronous storage, Redux persist के लिए भी।
