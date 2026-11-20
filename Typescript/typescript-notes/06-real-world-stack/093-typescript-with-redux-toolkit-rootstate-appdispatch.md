# 93. TypeScript with Redux Toolkit — RootState and AppDispatch
# हिंदी में: Redux Toolkit के साथ TypeScript — RootState और AppDispatch

> Verified with **TypeScript 5.9 (5.x)**, `@reduxjs/toolkit` 2.x, `react-redux` 9. `.withTypes()` helpers need RTK 2.1+ / react-redux 9.1+.

---

## 🔵 Simple Definition (English)
Redux Toolkit (RTK) infers almost everything from your store. The two types you export from the store file are `RootState = ReturnType<typeof store.getState>` and `AppDispatch = typeof store.dispatch`. Then you create **pre-typed hooks** (`useAppSelector`, `useAppDispatch`) once and use them everywhere, so selectors know the state shape and `dispatch` accepts thunks.

## 🔵 सरल परिभाषा (Hindi)
Redux Toolkit (RTK) store से लगभग सब कुछ infer कर लेता है। Store file से आप दो types export करते हो: `RootState = ReturnType<typeof store.getState>` और `AppDispatch = typeof store.dispatch`। फिर **pre-typed hooks** (`useAppSelector`, `useAppDispatch`) एक बार बनाकर हर जगह use करते हो, ताकि selectors को state का shape पता हो और `dispatch` thunks स्वीकार करे।

---

## 🔴 Problem it Solves
Plain `useSelector((state) => state.cart.items)` gives `state` as `unknown` in react-redux 9 (it cannot know your store). Plain `useDispatch()` returns `Dispatch<UnknownAction>`, which **rejects thunks**. Developers then sprinkle `(state: RootState)` and `as any` everywhere. Pre-typed hooks fix this in one place, and `RootState` is derived from reducers, so it can never drift from reality.

## 🔴 यह क्यों बना? (Hindi)
Plain `useSelector((state) => state.cart.items)` में react-redux 9 में `state` `unknown` मिलता है (उसे आपके store का पता नहीं)। Plain `useDispatch()` `Dispatch<UnknownAction>` देता है जो **thunks reject करता है**। फिर developers हर जगह `(state: RootState)` और `as any` छिड़कते हैं। Pre-typed hooks यह एक ही जगह ठीक कर देते हैं, और `RootState` reducers से derive होता है इसलिए असलियत से कभी अलग नहीं हो सकता।

---

## 🟢 How it Works — Step by Step
Step 1 → `configureStore({ reducer: { cart: cartReducer, user: userReducer } })` - the keys define the state shape.
Step 2 → `export type RootState = ReturnType<typeof store.getState>` - derived, never hand-written.
Step 3 → `export type AppDispatch = typeof store.dispatch` - includes thunk middleware typing.
Step 4 → `export const useAppDispatch = useDispatch.withTypes<AppDispatch>()` and `useAppSelector = useSelector.withTypes<RootState>()` (older style: `TypedUseSelectorHook<RootState>`).
Step 5 → Components import only the app hooks; never the raw `useSelector`/`useDispatch`.
Step 6 → Use `createAppAsyncThunk = createAsyncThunk.withTypes<{state: RootState; dispatch: AppDispatch}>()` so thunks know the state too.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `configureStore({ reducer: { cart: cartReducer, user: userReducer } })` - keys ही state का shape तय करती हैं।
Step 2 → `export type RootState = ReturnType<typeof store.getState>` - derived, हाथ से नहीं लिखते।
Step 3 → `export type AppDispatch = typeof store.dispatch` - इसमें thunk middleware की typing शामिल है।
Step 4 → `useAppDispatch = useDispatch.withTypes<AppDispatch>()` और `useAppSelector = useSelector.withTypes<RootState>()` (पुराना तरीका: `TypedUseSelectorHook<RootState>`)।
Step 5 → Components सिर्फ app hooks import करें; raw `useSelector`/`useDispatch` नहीं।
Step 6 → `createAppAsyncThunk = createAsyncThunk.withTypes<{state: RootState; dispatch: AppDispatch}>()` से thunks को भी state का type मिलता है।

---

## 🟡 Real World Example
**Razorpay dashboard**: store slices are `payments`, `settlements`, `auth`. `useAppSelector((s) => s.payments.list)` autocompletes the slice and its fields. When the team renames `payments.list` to `payments.rows`, the compiler flags every component that read the old name, which is a big refactoring win in a 200-component app.

## 🟡 Real Example Hindi mein
**Razorpay dashboard**: store slices हैं `payments`, `settlements`, `auth`। `useAppSelector((s) => s.payments.list)` में slice और fields autocomplete होते हैं। जब team `payments.list` का नाम `payments.rows` करती है तो compiler हर उस component को flag करता है जो पुराना नाम पढ़ रहा था - 200 components वाले app में refactoring की बड़ी जीत।

---

## 💻 Code Example — Basic

```tsx
// store.ts + hooks.ts + component, shown in one file for the demo
import { configureStore, createSlice, type PayloadAction } from "@reduxjs/toolkit";
import { useDispatch, useSelector } from "react-redux";

interface CartItem { id: number; name: string; qty: number } // one cart line
interface CartState { items: CartItem[] }                    // slice state shape

const initialState: CartState = { items: [] };               // annotate so state is not widened

const cartSlice = createSlice({
  name: "cart",                                              // action prefix: "cart/..."
  initialState,                                              // typed initial state
  reducers: {
    // PayloadAction<CartItem> types action.payload
    addItem(state, action: PayloadAction<CartItem>) {
      state.items.push(action.payload);                      // Immer allows "mutation"
    },
    clear(state) { state.items = []; },                      // no payload => no PayloadAction needed
  },
});
export const { addItem, clear } = cartSlice.actions;          // typed action creators

export const store = configureStore({
  reducer: { cart: cartSlice.reducer },                      // keys become RootState keys
});

// Derived types - the two exports every RTK+TS project has
export type RootState = ReturnType<typeof store.getState>;   // { cart: CartState }
export type AppDispatch = typeof store.dispatch;             // knows about thunks

// Pre-typed hooks (RTK 2 / react-redux 9.1+)
export const useAppDispatch = useDispatch.withTypes<AppDispatch>();
export const useAppSelector = useSelector.withTypes<RootState>();

export function CartCount() {
  const count = useAppSelector((s) => s.cart.items.length);  // s is RootState, count is number
  const dispatch = useAppDispatch();                         // typed dispatch
  return <button onClick={() => dispatch(addItem({ id: 1, name: "Dosa", qty: 1 }))}>{count}</button>;
}
```

## 💻 Code Example — Advanced

```tsx
// advanced: typed thunk with getState, createSelector, listener-free entity-like state
import {
  configureStore, createAsyncThunk, createSelector, createSlice, type PayloadAction,
} from "@reduxjs/toolkit";
import { useDispatch, useSelector } from "react-redux";

interface Product { id: number; name: string; price: number }              // catalog item
interface CatalogState { byId: Record<number, Product>; status: "idle" | "loading" | "failed" }

const catalog = createSlice({
  name: "catalog",
  initialState: { byId: {}, status: "idle" } as CatalogState,             // `as` here is fine: {} would widen
  reducers: {
    loaded(state, a: PayloadAction<Product[]>) {
      for (const p of a.payload) state.byId[p.id] = p;                    // normalize into a map
      state.status = "idle";
    },
  },
});

export const store = configureStore({ reducer: { catalog: catalog.reducer } });
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
export const useAppDispatch = useDispatch.withTypes<AppDispatch>();
export const useAppSelector = useSelector.withTypes<RootState>();

// A thunk factory that already knows state + dispatch types (RTK 2: .withTypes)
export const createAppAsyncThunk = createAsyncThunk.withTypes<{ state: RootState; dispatch: AppDispatch }>();

export const fetchProducts = createAppAsyncThunk("catalog/fetch", async (_: void, { getState, dispatch }) => {
  const already = Object.keys(getState().catalog.byId).length;           // getState() is RootState
  if (already > 0) return;                                                // skip refetch
  const products: Product[] = [{ id: 1, name: "Masala Dosa", price: 120 }]; // pretend fetch
  dispatch(catalog.actions.loaded(products));                             // dispatch is AppDispatch
});

// Memoized selector; input selectors are typed from RootState
export const selectCheap = createSelector(
  [(s: RootState) => s.catalog.byId, (_: RootState, max: number) => max],  // 2 inputs: state and an arg
  (byId, max) => Object.values(byId).filter((p) => p.price <= max),        // result: Product[]
);

export function Menu() {
  const dispatch = useAppDispatch();
  const cheap = useAppSelector((s) => selectCheap(s, 150));               // Product[]
  return <button onClick={() => dispatch(fetchProducts())}>{cheap.length}</button>; // thunk accepted
}
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express returns the same Product shape the Redux slice expects.
import express from "express";

interface Product { id: number; name: string; price: number } // would be shared via a common package
const products: Product[] = [{ id: 1, name: "Masala Dosa", price: 120 }]; // pretend SQL Server rows

const app = express();
app.get("/api/products", (_req, res) => { res.json(products); }); // React thunk fetches this
```

```tsx
// Store provider at the app root + thunk that calls Express
import { Provider } from "react-redux";
import { configureStore, createAsyncThunk, createSlice } from "@reduxjs/toolkit";

interface Product { id: number; name: string; price: number }
const load = createAsyncThunk("products/load", async (): Promise<Product[]> => {
  const r = await fetch("/api/products");                 // call Express
  if (!r.ok) throw new Error(`HTTP ${r.status}`);         // becomes rejected action
  return (await r.json()) as Product[];                    // fulfilled payload type: Product[]
});
const slice = createSlice({
  name: "products", initialState: [] as Product[], reducers: {},
  extraReducers: (b) => { b.addCase(load.fulfilled, (_s, a) => a.payload); }, // a.payload: Product[]
});
const store = configureStore({ reducer: { products: slice.reducer } });

export const Root = () => <Provider store={store}><div>app</div></Provider>; // typed Provider
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the raw `useDispatch` for thunks
```typescript
// ❌ WRONG
import { configureStore, createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { useDispatch } from "react-redux";
const s = createSlice({ name: "c", initialState: { n: 0 }, reducers: {} });
const store = configureStore({ reducer: { c: s.reducer } });
const t = createAsyncThunk("x", async (id: number) => id);
const d = useDispatch();
d(t(1));
// error TS2345: Argument of type 'AsyncThunkAction<number, number, AsyncThunkConfig>' is not assignable to parameter of type 'UnknownAction'.
```
✅ Correct: `const d = useAppDispatch();`

❌ Mistake 2: Using the raw `useSelector` (state is `unknown`)
```typescript
// ❌ WRONG
import { useSelector } from "react-redux";
const n = useSelector((st) => st.c.n);
// error TS18046: 'st' is of type 'unknown'.
```
✅ Correct: `const n = useAppSelector((st) => st.c.n);`

❌ Mistake 3: Wrong payload type on an action creator
```typescript
// ❌ WRONG
import { configureStore, createSlice } from "@reduxjs/toolkit";
const s = createSlice({ name: "c", initialState: { n: 0 }, reducers: { add(st, a: { payload: number }) { st.n += a.payload } } });
const store = configureStore({ reducer: { c: s.reducer } });
store.dispatch(s.actions.add("5"));
// error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.
```

❌ Mistake 4: Hand-writing `RootState`
Writing `interface RootState { cart: CartState }` by hand compiles but silently drifts when someone adds a slice. ✅ Correct: always `ReturnType<typeof store.getState>`.

---

## 🧠 Tricky Interview Question

```text
// store.ts  (imports the slice to build the store)
import { configureStore } from "@reduxjs/toolkit";
import cart from "./cart";
export const store = configureStore({ reducer: { cart } });
export type RootState = ReturnType<typeof store.getState>;

// cart.ts   (imports RootState back from store.ts  =>  circular import!)
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import type { RootState } from "./store";
export const selectItems = (s: RootState) => s.cart.items;
export const bad = createAsyncThunk("x", async (_: void, { getState }) =>
  (getState() as RootState).cart.items.length);
const slice = createSlice({ name: "cart", initialState: { items: [] as string[] }, reducers: {},
  extraReducers: (b) => { b.addCase(bad.fulfilled, (s) => { s.items.length; }); } });
export default slice.reducer;
```
Question: slice and store import each other. Does this compile, and is it safe at runtime?

**Answer:** I compiled exactly these two files with `tsc --strict` (5.9): **no error**. It is safe because `import type` is erased at build time, so there is no runtime cycle, and TypeScript resolves circular *type* references lazily. The breakage happens when the slice's own state type depends on `RootState`, e.g. `const initialState: { items: RootState["cart"]["items"] } = { items: [] };` - real compiler output: `error TS2502: 'items' is referenced directly or indirectly in its own type annotation.` Rule: always use `import type` for `RootState` inside slices, and never derive a slice's own types from `RootState`. (Without `type`, a normal `import` of a value across the cycle *would* be a runtime problem.)

---

## ⚫ Interview Questions + Answers

Q1: Why derive `RootState` instead of writing it?
A1: Single source of truth. `ReturnType<typeof store.getState>` always matches the reducers (even with `combineReducers`, RTK Query reducers and `injectSlice`). Hand-written types drift.

Q2: Why is `AppDispatch` needed?
A2: The default `Dispatch<UnknownAction>` does not accept thunks. `typeof store.dispatch` includes the thunk middleware overload, so `dispatch(fetchOrders())` type-checks, and it also includes any custom middleware extensions.

Q3: What does `useSelector.withTypes<RootState>()` replace?
A3: The older `const useAppSelector: TypedUseSelectorHook<RootState> = useSelector`. Same result; `.withTypes` is shorter and also exists for `useStore`, `createAsyncThunk`, `createSelector`.

Q4: How do you type `initialState` that starts empty?
A4: Declare a typed constant (`const initialState: CartState = { items: [] }`) or `as CartState`. Without it, `items: []` is inferred as `never[]`, and `push` fails.

Q5: Why not put non-serializable values (Map, class instances, Date) in state?
A5: RTK's serializability middleware warns; DevTools and persistence break. Store ISO strings / ids and derive objects in selectors. TS will not stop you, so this is a convention to enforce with lint/review.

---

## 🔷 When to Use + When Not to Use
✅ Use:
- App-wide state with many readers/writers (cart, auth, filters, entity caches)
- Pre-typed hooks in every RTK + TS project from day one

❌ Avoid:
- Putting form-field state or purely local UI state in Redux
- Hand-typing `RootState` or `as any` on `dispatch`
- Storing server cache manually when RTK Query / React Query fits (next note)

---

## 📊 Visual Diagram
```
configureStore({ reducer: { cart, user } })
        │
        ├─► RootState   = ReturnType<typeof store.getState>
        └─► AppDispatch = typeof store.dispatch
                │
   useAppSelector = useSelector.withTypes<RootState>()
   useAppDispatch = useDispatch.withTypes<AppDispatch>()
                │
   components: useAppSelector(s => s.cart.items)   (s fully typed)
               dispatch(fetchProducts())            (thunk OK)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RootState | Type of the whole store state | पूरे store state का type |
| AppDispatch | Dispatch type incl. thunks | thunks सहित dispatch का type |
| PayloadAction<T> | Action with typed payload | typed payload वाला action |
| withTypes | Pre-binds generic types to a hook | hook में types पहले से bind करना |
| Thunk | Function dispatched for async logic | async logic के लिए dispatch होने वाला function |
| Selector | Function reading state | state पढ़ने वाला function |

---

## ⚡ 3-Line Summary
English:
1. Derive `RootState` and `AppDispatch` from the store; never hand-write them.
2. Create `useAppSelector`/`useAppDispatch` (and `createAppAsyncThunk`) with `.withTypes` once; use only those.
3. Annotate `initialState` and action payloads with `PayloadAction<T>` so `never[]` and `unknown` problems vanish.

Hindi:
1. `RootState` और `AppDispatch` store से derive करो; हाथ से मत लिखो।
2. `useAppSelector`/`useAppDispatch` (और `createAppAsyncThunk`) `.withTypes` से एक बार बनाओ; सिर्फ वही use करो।
3. `initialState` annotate करो और payloads के लिए `PayloadAction<T>` लगाओ ताकि `never[]` और `unknown` की समस्या खत्म हो।

---

## ➡️ Next Topic
**94. Typed createSlice, createAsyncThunk and RTK Query** — deeper typing for async flows and API caching.
