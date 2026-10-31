# 99. Redux Thunk — Async Actions
# हिंदी में: Redux Thunk — Async Actions (async काम को Redux में संभालना)

---

## 🔵 Simple Definition (English)
Redux reducers must be **pure and synchronous**, so they cannot call APIs. A **thunk** is a function that you dispatch instead of a plain action object. Redux middleware calls it with `dispatch` and `getState`, so it can do async work (API calls, timers) and then dispatch plain actions when results arrive. Redux Toolkit already includes thunk middleware in `configureStore`, and `createAsyncThunk` is the standard helper.

## 🔵 सरल परिभाषा (Hindi)
Redux के reducers **pure और synchronous** होने चाहिए, इसलिए वे API call नहीं कर सकते। **Thunk** एक ऐसा function है जिसे plain action object की जगह dispatch किया जाता है। Redux middleware उसे `dispatch` और `getState` के साथ call करता है, तो वह async काम (API call, timer) कर सकता है और नतीजा आने पर plain actions dispatch कर सकता है। Redux Toolkit के `configureStore` में thunk middleware पहले से जुड़ा होता है, और `createAsyncThunk` standard helper है।

---

## 🔴 Problem it Solves
Reducer में `fetch` लिखोगे तो reducer impure हो जाएगा: एक ही action पर अलग-अलग नतीजे, time-travel debugging टूट जाती है। Thunk के बिना हर component खुद fetch करता है, फिर खुद loading/error dispatch करता है, और यही logic हर जगह copy-paste होता है। Race conditions भी आते हैं (पुराना response नए को overwrite कर दे)।

**Zomato example:** Order tracking screen पर status server से आता है। Loading spinner, error message और data — ये तीनों state में रहने चाहिए, और कई components इन्हें read करते हैं। Thunk यह सब एक ही जगह centralize करता है।

## 🔴 यह क्यों बना? (Hindi)
Reducer side effects (API calls) नहीं कर सकता, क्योंकि उससे purity और predictability टूटती है। पहले हर component अपना loading/error लिखता था, जिससे code बिखरा और duplicate होता था। Thunk एक **middleware-based** जगह देता है जहाँ async flow लिखा जाए: पहले "शुरू हुआ", फिर "सफल" या "असफल"।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Store में thunk middleware होना चाहिए
         configureStore() इसे default में add करता है (Redux Toolkit)

Step 2 → Component एक thunk dispatch करता है
         dispatch(fetchOrder('ZMT-1001'))

Step 3 → Middleware thunk function को call करता है
         thunk(dispatch, getState, extraArgument)
         Plain object नहीं है, इसलिए reducer तक सीधे नहीं जाता

Step 4 → Thunk async काम करता है और plain actions dispatch करता है
         dispatch(fetchStarted())        → loading = true
         await API...
         dispatch(fetchSucceeded(data))  → data save

Step 5 → हर plain action reducer में synchronously जाता है
         Reducer pure रहता है, state predictably बदलती है
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Store में thunk middleware (configureStore default में देता है)
Step 2 → Component dispatch(fetchOrder(id)) करता है
Step 3 → Middleware function को dispatch और getState के साथ call करता है
Step 4 → Thunk API का इंतज़ार करता है, फिर "शुरू" और "सफल/असफल" actions dispatch करता है
Step 5 → हर plain action reducer में synchronously जाता है, reducer pure रहता है
```

---

## 🟡 Real World Example
**Zomato order tracking:** User "Track Order" दबाता है, तो `fetchOrderStatus(orderId)` dispatch होता है। Thunk सबसे पहले `pending` (loading spinner ON) dispatch करता है, फिर API call करता है। सफल होने पर `fulfilled` के साथ status आता है। Fail होने पर `rejected` के साथ error message। **Razorpay checkout** में भी ऐसे ही `createPayment` thunk होते हैं।

## 🟡 Real Example Hindi mein
**Zomato order tracking:** User "Track Order" दबाता है, तो `fetchOrderStatus(orderId)` dispatch होता है। Thunk पहले `pending` (spinner ON) dispatch करता है, फिर API call करता है। सफल हो तो `fulfilled` के साथ status आता है। Fail हो तो `rejected` के साथ error message। **Razorpay checkout** में भी ऐसे ही `createPayment` thunk होते हैं।

---

## 💻 Code Example — Basic

```javascript
// Basic: hand-written thunk with configureStore — ESM file (.mjs ya "type": "module")
import { configureStore, createSlice } from '@reduxjs/toolkit'; // store aur reducer helpers
const fakeOrderApi = (orderId) =>                                  // fake API (network ki zaroorat nahi)
  new Promise((resolve) =>                                         // Promise banaya
    setTimeout(() => resolve({ id: orderId, status: 'OUT_FOR_DELIVERY' }), 100)); // 100ms baad resolve
const orderSlice = createSlice({                                   // slice = name + initialState + reducers
  name: 'order',                                                   // action type ka prefix: "order/..."
  initialState: { status: 'idle', data: null, error: null },       // shuruaati state
  reducers: {                                                      // sync, pure reducers
    fetchStarted(state) { state.status = 'loading'; },             // loading ON
    fetchSucceeded(state, action) {                                // success: data save karo
      state.status = 'succeeded';                                  // status update
      state.data = action.payload;                                 // payload = order object
    },
    fetchFailed(state, action) {                                   // failure: error save karo
      state.status = 'failed';                                     // status update
      state.error = action.payload;                                // error message
    },
  },
});
const { fetchStarted, fetchSucceeded, fetchFailed } = orderSlice.actions; // action creators nikale
const fetchOrder = (orderId) => async (dispatch) => {              // THUNK: function jo function return kare
  dispatch(fetchStarted());                                        // 1. loading turant ON
  try {
    const order = await fakeOrderApi(orderId);                     // 2. async API call ka wait
    dispatch(fetchSucceeded(order));                               // 3. success action
  } catch (err) {                                                  // 4. error aaya to
    dispatch(fetchFailed(err.message));                            // failure action
  }
};
const store = configureStore({ reducer: { order: orderSlice.reducer } }); // store (thunk middleware default)
console.log('Before:', store.getState().order.status);              // Before: idle
store.dispatch(fetchOrder('ZMT-1001'));                            // thunk dispatch karo
console.log('Right after dispatch:', store.getState().order.status); // Right after dispatch: loading
setTimeout(() => {                                                 // 200ms baad state dekho
  console.log('After API:', JSON.stringify(store.getState().order)); // success state print
}, 200);
// Expected output:
// Before: idle
// Right after dispatch: loading
// After API: {"status":"succeeded","data":{"id":"ZMT-1001","status":"OUT_FOR_DELIVERY"},"error":null}
```

## 💻 Code Example — Advanced

```javascript
// Advanced: createAsyncThunk + AbortSignal + rejectWithValue + condition — ESM file (.mjs ya "type": "module")
import { configureStore, createSlice, createAsyncThunk } from '@reduxjs/toolkit'; // RTK helpers

// Fake API jo AbortSignal ka respect karti hai (real fetch(url, { signal }) bhi aisa hi karta hai)
const fetchRestaurant = (id, signal) =>
  new Promise((resolve, reject) => {                               // Promise banaya
    if (id === 'bad') return reject(new Error('Restaurant not found')); // server error simulate
    const timer = setTimeout(() => resolve({ id, name: 'Biryani House', rating: 4.6 }), 150); // 150ms
    signal.addEventListener('abort', () => {                       // cancel hone par
      clearTimeout(timer);                                         // timer band
      reject(new Error('Aborted'));                                // promise reject
    });
  });

// createAsyncThunk pending / fulfilled / rejected action types khud banata hai
export const loadRestaurant = createAsyncThunk(
  'restaurants/load',                                              // type prefix
  async (id, { signal, rejectWithValue }) => {                     // thunkAPI: signal aur helper
    try {
      return await fetchRestaurant(id, signal);                    // return value = fulfilled payload
    } catch (err) {
      return rejectWithValue(err.message);                         // rejected payload = custom message
    }
  },
  {
    // condition: false return kare to request dispatch hi nahi hoti (duplicate requests rokta hai)
    condition: (id, { getState }) => getState().restaurants.status !== 'loading',
  }
);

const restaurantSlice = createSlice({
  name: 'restaurants',                                             // slice ka naam
  initialState: { status: 'idle', item: null, error: null },       // shuruaati state
  reducers: {
    clearError(state) { state.error = null; },                     // normal sync reducer bhi chal sakta hai
  },
  extraReducers: (builder) => {                                    // generated actions handle karo
    builder
      .addCase(loadRestaurant.pending, (state) => {                // request shuru
        state.status = 'loading';                                  // spinner ON
        state.error = null;                                        // purana error saaf
      })
      .addCase(loadRestaurant.fulfilled, (state, action) => {      // success
        state.status = 'succeeded';                                // status update
        state.item = action.payload;                               // restaurant save
      })
      .addCase(loadRestaurant.rejected, (state, action) => {       // fail ya abort
        state.status = 'failed';                                   // status update
        state.error = action.payload ?? action.error.message;      // custom msg ya default msg
      });
  },
});

const store = configureStore({ reducer: { restaurants: restaurantSlice.reducer } }); // store banaya

const main = async () => {                                         // async main (node mein top-level await ki jagah)
  const first = store.dispatch(loadRestaurant('R-42'));            // request 1 shuru
  store.dispatch(loadRestaurant('R-42'));                          // condition false: request skip
  const result = await first;                                      // request 1 ka final action
  console.log(result.type);                                        // restaurants/load/fulfilled
  console.log(JSON.stringify(store.getState().restaurants));       // success state
  await store.dispatch(loadRestaurant('bad'));                     // error wala case
  console.log(JSON.stringify(store.getState().restaurants.error)); // "Restaurant not found"
  const pending = store.dispatch(loadRestaurant('R-99'));          // request shuru
  pending.abort('User left the page');                             // user ne page chhod diya: cancel
  const aborted = await pending;                                   // cancel ka final action
  console.log(aborted.type, aborted.meta.aborted);                 // restaurants/load/rejected true
};
main();
// Expected output:
// restaurants/load/fulfilled
// {"status":"succeeded","item":{"id":"R-42","name":"Biryani House","rating":4.6},"error":null}
// "Restaurant not found"
// restaurants/load/rejected true
```

---

## 🟠 Real app integration

Next.js App Router mein store ek Client Component wrapper ke andar dena hota hai. Component `useEffect` mein thunk dispatch karta hai, aur unmount par request cancel karta hai. (Yeh snippet syntax-level example hai, poora project nahi.)

```jsx
// app/providers.jsx — Redux store ko Client side tree mein dene ke liye
'use client';                                                      // Redux context browser mein chalta hai
import { Provider } from 'react-redux';                            // store React tree mein dene ke liye
import { store } from '@/lib/store';                               // configureStore wala store
export function Providers({ children }) {                          // children = app ke pages
  return <Provider store={store}>{children}</Provider>;            // sab components ko store milega
}

// components/RestaurantPage.jsx — thunk dispatch aur cleanup
'use client';
import { useEffect } from 'react';                                 // side effect hook
import { useDispatch, useSelector } from 'react-redux';            // Redux hooks
import { loadRestaurant } from '@/lib/restaurantSlice';            // thunk export
export default function RestaurantPage({ id }) {
  const dispatch = useDispatch();                                  // dispatch function
  const { status, item, error } = useSelector((s) => s.restaurants); // slice state read karo
  useEffect(() => {                                                // id badle ya mount par
    const request = dispatch(loadRestaurant(id));                  // thunk dispatch
    return () => request.abort();                                  // unmount par request cancel
  }, [dispatch, id]);
  if (status === 'loading') return <p>Loading...</p>;              // spinner
  if (status === 'failed') return <p>Error: {error}</p>;           // error message
  return <h1>{item?.name}</h1>;                                    // data dikhao
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Async API call reducer ke andar
✅ **Correct:** API call thunk mein karo, reducer sirf state update kare

```javascript
// Wrong
const slice = createSlice({
  name: 'order', initialState: { data: null },
  reducers: {
    fetched(state) {
      fetch('/api/order').then((r) => r.json()); // ❌ reducer impure, promise ignore
    },
  },
});

// Right
const fetchOrder = () => async (dispatch) => {   // ✅ thunk async kaam karta hai
  const res = await fetch('/api/order');         // API call thunk mein
  const data = await res.json();                 // parse
  dispatch(orderSlice.actions.fetched(data));    // reducer ko plain action
};
```

❌ **Mistake 2:** try/catch nahi, error aane par state hamesha `loading` par atak jaati hai
✅ **Correct:** Har failure path par `failed` action dispatch karo

```javascript
// Wrong
const fetchOrderWrong = (id) => async (dispatch) => {
  dispatch(fetchStarted());                      // loading ON
  const order = await api.get(id);               // ❌ error aaya to fetchFailed kabhi nahi chalega
  dispatch(fetchSucceeded(order));
};

// Right
const fetchOrder = (id) => async (dispatch) => {
  dispatch(fetchStarted());                      // loading ON
  try {
    const order = await api.get(id);             // API call
    dispatch(fetchSucceeded(order));             // success
  } catch (err) {
    dispatch(fetchFailed(err.message));          // ✅ error state set hua
  }
};
```

---

## 🧠 Tricky Interview Question

```javascript
import { configureStore, createSlice } from '@reduxjs/toolkit'; // store helpers

const slice = createSlice({                                      // slice banaya
  name: 'log',                                                   // prefix
  initialState: { steps: [] },                                   // steps ki list
  reducers: {
    add(state, action) { state.steps.push(action.payload); },    // step push karo
  },
});

const store = configureStore({ reducer: { log: slice.reducer } }); // store

const task = () => async (dispatch) => {                         // thunk
  dispatch(slice.actions.add('A'));                              // (1) sync
  await Promise.resolve();                                       // (2) microtask ka wait
  dispatch(slice.actions.add('C'));                              // (4) baad mein
};

store.dispatch(task());                                          // (0) thunk shuru
store.dispatch(slice.actions.add('B'));                          // (3) turant
console.log(JSON.stringify(store.getState().log.steps));         // kya print hoga?
setTimeout(() => console.log(JSON.stringify(store.getState().log.steps)), 0); // aur yahan?
```

**Answer:** Output is:
```
["A","B"]
["A","B","C"]
```
Reasoning: `store.dispatch(task())` thunk ko call karta hai, aur thunk ka pehla line (`add('A')`) turant synchronous chalta hai. `await Promise.resolve()` function ko pause karta hai aur control wapas bhejta hai, isliye `store.dispatch(add('B'))` ab bhi synchronous code mein chalta hai. Pehla `console.log` sirf `A` aur `B` dekhta hai. `'C'` tab aata hai jab microtask queue chalti hai, jo synchronous script khatam hone ke baad hoti hai. `B` ko `C` se pehle hona "code order" ke bawajood sach hai, kyunki `await` ne thunk ka dusra hissa piche dhakel diya.

---

## ⚫ Interview Questions + Answers

**Q1: Redux Thunk kya hai?**
A1: Thunk ek function hai jo `dispatch` aur `getState` lete hue async kaam kar sakta hai. Redux middleware thunk ko detect karke call karta hai, aur reducer ko sirf plain action milta hai, isliye reducer pure rehta hai.

**Q2: Thunk aur saga mein kya fark hai?**
A2: Thunk simple async flow ke liye hai: ek function, `await`, aur do-teen dispatches. Redux-Saga generator functions (`function*`) se complex flows (cancel, race, debounce, retry) handle karta hai. Aaj ke zyadatar apps ke liye `createAsyncThunk` ya RTK Query kaafi hote hain.

**Q3: createAsyncThunk kya automatically deta hai?**
A3: Ek action creator jo `pending`, `fulfilled`, `rejected` action types khud banata hai. `AbortSignal` (cancel), `rejectWithValue` (custom error payload), aur `condition` (duplicate requests skip) jaise options bhi deta hai.

**Q4: Thunk ko `dispatch` karne par kya return hota hai?**
A4: `createAsyncThunk` ke thunk ke liye `dispatch` ek promise-like object return karta hai, jo final action (fulfilled ya rejected) par resolve hota hai aur `.abort()` method deta hai. Plain thunk mein jo return hota hai, woh function ki return value hoti hai.

**Q5: Thunk ke andar `getState` kab use karna chahiye?**
A5: Sirf decision ke liye: jaise `condition` mein check karna ki data pehle se hai ya request already chal rahi hai. Business logic ko component ke bajaye thunk mein rakho, par state ko directly mutate mat karo.

---

## 🔷 When to Use + When Not to Use

✅ **Use when:**
- API call ke baad multiple state updates chahiye (loading, data, error)
- Ek hi async flow kai components se trigger hota hai
- Cancel, duplicate-request rokna, ya error payload customize karna hai
- Project mein Redux pehle se hai aur simple async flow chahiye

❌ **Avoid when:**
- Sirf server data cache/refetch karna hai: RTK Query better hai (next topic)
- State sirf ek component ka hai: `useState` ya `useReducer` kaafi hai
- Naya project hai jisme Redux ki zarurat nahi: Zustand ya Jotai halke hain
- Reducer ke andar side effects daalne ki koshish: yeh kabhi nahi

---

## 📊 Visual Diagram

```
Component                 Middleware (thunk)              Reducer
─────────                 ──────────────────              ───────
dispatch(fetchOrder(1)) ─▶ fn(dispatch, getState)
                              │
                              ├─▶ dispatch(fetchStarted) ──────▶ status = 'loading'
                              │
                              ├── await API ....... (async gap)
                              │
                              ├─▶ dispatch(fetchSucceeded) ───▶ data = order, status = 'succeeded'
                              │         OR
                              └─▶ dispatch(fetchFailed) ──────▶ error = msg,  status = 'failed'

useSelector(s => s.order) ◀──── component re-renders with new state
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Thunk | Function jo dispatch hota hai aur async kaam karta hai | Async काम करने वाला dispatch-able function |
| Middleware | Action aur reducer ke beech ka layer | Action और reducer के बीच की layer |
| createAsyncThunk | pending/fulfilled/rejected action types banane wala helper | Async actions के तीन चरण बनाने वाला helper |
| pending / fulfilled / rejected | Async request ke teen states | Async request की तीन अवस्थाएँ |
| AbortSignal | Request cancel karne ka signal | Request cancel करने का signal |
| rejectWithValue | Rejected action mein custom payload dalna | Error में custom data भेजना |
| condition | False return karne par request skip | False होने पर request skip होती है |
| Pure reducer | Same input, same output, no side effects | Side effects के बिना predictable reducer |

---

## ⚡ 3-Line Summary
**English:**
1. Thunk ek function hai jo async kaam karke plain actions dispatch karta hai, reducer ko pure rakhte hue.
2. `createAsyncThunk` pending/fulfilled/rejected actions khud banata hai, aur cancel (`signal`) plus duplicate-skip (`condition`) deta hai.
3. Hamesha failure path par state update karo, warna UI loading par atak jaayega.

**Hindi:**
1. Thunk एक function है जो async काम करके plain actions dispatch करता है, और reducer pure रहता है।
2. `createAsyncThunk` pending/fulfilled/rejected actions खुद बनाता है, और cancel (`signal`) व duplicate-skip (`condition`) देता है।
3. हमेशा failure path पर state update करो, वरना UI loading पर अटक जाएगा।

---

## ➡️ Next Topic
**100. RTK Query — Data Fetching** — Redux Toolkit का server-data layer: caching, refetching और auto-generated hooks, जिससे `createAsyncThunk` वाला boilerplate ज़्यादातर खत्म हो जाता है।
