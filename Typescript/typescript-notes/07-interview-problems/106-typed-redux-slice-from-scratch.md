# 106. Typed Redux Slice from Scratch
# हिंदी में: Typed Redux Slice शुरू से बनाना

> Verified with **TypeScript 5.9.3** (`--strict`) and **@reduxjs/toolkit 2.x**. `NoInfer<S>` needs **TS 5.4+** (marked below); the rest works on TS 4.x.

---

## 🔵 Simple Definition (English)
A **Redux slice** bundles a piece of state, its reducers and the auto-generated **action creators**. RTK's `createSlice` is famous for its inference: write `added(state, action: PayloadAction<CartItem>)` and you automatically get `slice.actions.added(item)` returning `{ type: "cart/added", payload: item }`. "Implement a typed `createSlice`" is a favourite senior interview problem because it needs **generics, mapped types, `infer`, conditional types and template literal types** in one small function.

## 🔵 सरल परिभाषा (Hindi)
**Redux slice** state का एक हिस्सा, उसके reducers और auto-generated **action creators** को एक साथ बाँधता है। RTK का `createSlice` अपनी inference के लिए मशहूर है: `added(state, action: PayloadAction<CartItem>)` लिखो और अपने-आप `slice.actions.added(item)` मिलता है जो `{ type: "cart/added", payload: item }` लौटाता है। "Typed `createSlice` implement करो" senior interviews का पसंदीदा सवाल है क्योंकि एक छोटे function में **generics, mapped types, `infer`, conditional types और template literal types** सब चाहिए।

---

## 🔴 Problem it Solves
Classic Redux needed three hand-written things per feature: action type constants (`"cart/added"`), action creators and a `switch` reducer. Typos in type strings, creators whose payload drifts from what the reducer reads, and a missing `default` branch were everyday bugs. The slice pattern derives **creators and type strings from the reducer map**, so one definition stays consistent. Building it yourself shows you exactly how the inference works and why `PayloadAction<void>` creates a zero-argument creator.

## 🔴 यह क्यों बना? (Hindi)
Classic Redux में हर feature के लिए तीन चीज़ें हाथ से लिखनी पड़ती थीं: action type constants (`"cart/added"`), action creators और `switch` reducer। Type strings में typo, creator का payload reducer से अलग हो जाना, और `default` branch भूलना रोज़ के bugs थे। Slice pattern **creators और type strings को reducer map से derive** करता है, इसलिए एक ही definition consistent रहती है। खुद बनाने से दिखता है कि inference कैसे काम करता है और `PayloadAction<void>` zero-argument creator क्यों बनाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Define `PayloadAction<P, T>` = `{ type: T; payload: P }`.
Step 2 → `createSlice<N, S, R>(name, initialState, reducers)`: generic over **name literal `N`**, **state `S`** (from `initialState`) and the **reducer map `R`**.
Step 3 → Constrain `R extends Record<string, (state: S, action: PayloadAction<any>) => S | void>`. This also gives each reducer its **contextual `state` type**. Wrap `S` in `NoInfer<S>` (TS 5.4+) so `S` comes from `initialState` only, not from reducers.
Step 4 → Map each reducer key to an action creator type: look at the 2nd parameter with `infer A`, then `A extends PayloadAction<infer P>`. If `P` is `void` or there is no action parameter, the creator takes **no arguments**.
Step 5 → Type string: `` `${N}/${K}` `` (template literal) so `actions.added(...).type` is the literal `"cart/added"`, enabling discriminated-union reducers elsewhere.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `PayloadAction<P, T>` = `{ type: T; payload: P }` define करो।
Step 2 → `createSlice<N, S, R>(name, initialState, reducers)`: **name literal `N`**, **state `S`** (`initialState` से) और **reducer map `R`** पर generic।
Step 3 → `R extends Record<string, (state: S, action: PayloadAction<any>) => S | void>` constrain करो। यह हर reducer को उसका **contextual `state` type** भी देता है। `S` को `NoInfer<S>` (TS 5.4+) में लपेटो ताकि `S` सिर्फ `initialState` से आए, reducers से नहीं।
Step 4 → हर reducer key को action creator type में map करो: दूसरे parameter को `infer A` से देखो, फिर `A extends PayloadAction<infer P>`। अगर `P` `void` है या action parameter नहीं है तो creator **बिना arguments** का होगा।
Step 5 → Type string: `` `${N}/${K}` `` (template literal) ताकि `actions.added(...).type` literal `"cart/added"` हो।

---

## 🟡 Real World Example
**Swiggy cart** slice: `added(item)`, `removed(sku)`, `couponApplied(code)`, `cleared()`. The UI dispatches `dispatch(cartActions.added({ sku: "dosa", qty: 1 }))`. Analytics middleware listens for `action.type === "cart/added"` and reads `payload.sku`. With a typed slice, renaming `sku` to `itemId` in `CartItem` breaks the reducer, every dispatch site and the analytics middleware at **compile time**, not in a production funnel report.

## 🟡 Real Example Hindi mein
**Swiggy cart** slice: `added(item)`, `removed(sku)`, `couponApplied(code)`, `cleared()`। UI `dispatch(cartActions.added({ sku: "dosa", qty: 1 }))` करता है। Analytics middleware `action.type === "cart/added"` सुनकर `payload.sku` पढ़ता है। Typed slice में `CartItem` का `sku` बदलकर `itemId` करते ही reducer, हर dispatch site और analytics middleware **compile time** पर टूटते हैं, production funnel report में नहीं।

---

## 💻 Code Example — Basic

```typescript
// mini-slice.ts — a tiny createSlice with full inference (NoInfer needs TS 5.4+)
interface PayloadAction<P = void, T extends string = string> { type: T; payload: P } // action shape

type CaseReducers<S> = Record<string, (state: S, action: PayloadAction<any>) => S | void>; // reducer map shape

type ActionCreator<R, T extends string> = // derive creator type from ONE reducer function type R
  R extends (state: any, action: infer A) => any // look at the 2nd parameter
    ? A extends PayloadAction<infer P> // does it declare a payload?
      ? [P] extends [void] ? () => PayloadAction<void, T> // PayloadAction<void> -> no argument
        : (payload: P) => PayloadAction<P, T> // otherwise payload is required
      : () => PayloadAction<void, T> // 2nd param exists but is not a PayloadAction
    : () => PayloadAction<void, T>; // fallback

type Actions<N extends string, R> = { [K in keyof R & string]: ActionCreator<R[K], `${N}/${K}`> }; // one creator per key

function createMiniSlice<N extends string, S, R extends CaseReducers<NoInfer<S>>>( // N: name literal, S: state, R: reducers
  name: N, initialState: S, reducers: R,
) {
  const actions = {} as Actions<N, R>; // filled below (cast is the only unavoidable one)
  for (const key of Object.keys(reducers)) { // build a creator for every reducer
    (actions as Record<string, unknown>)[key] = (payload?: unknown) => ({ type: `${name}/${key}`, payload }); // runtime creator
  }
  const reducer = (state: S = initialState, action: { type: string; payload?: unknown }): S => {
    const fn = (reducers as Record<string, (s: S, a: unknown) => S | void>)[action.type.slice(name.length + 1)]; // find reducer
    if (!action.type.startsWith(`${name}/`) || !fn) return state; // not ours: ignore
    const draft = structuredClone(state); // poor-man's Immer: clone, then let the reducer "mutate"
    const result = fn(draft, action); // run it
    return result === undefined ? draft : result; // reducers may mutate OR return a new state
  };
  return { name, actions, reducer }; // the slice
}

interface CartItem { sku: string; qty: number } // domain
interface CartState { items: CartItem[]; coupon: string | null } // state

const cart = createMiniSlice("cart", { items: [], coupon: null } as CartState, { // name literal "cart"
  added(state, action: PayloadAction<CartItem>) { state.items.push(action.payload); }, // state is CartState (contextual)
  couponApplied(state, action: PayloadAction<string>) { state.coupon = action.payload; }, // payload string
  cleared() { return { items: [], coupon: null }; }, // no action param, returns new state
});

const a1 = cart.actions.added({ sku: "dosa", qty: 2 }); // a1: PayloadAction<CartItem, "cart/added">
let s = cart.reducer(undefined, { type: "@@init" }); // initial state
s = cart.reducer(s, a1); // add item
s = cart.reducer(s, cart.actions.couponApplied("SAVE20")); // apply coupon
console.log(a1.type, JSON.stringify(s)); // prints cart/added {"items":[{"sku":"dosa","qty":2}],"coupon":"SAVE20"}

// ❌ 1. wrong payload type
cart.actions.added("x");
// error TS2345: Argument of type 'string' is not assignable to parameter of type 'CartItem'.

// ❌ 2. creator for a payload-less reducer takes zero arguments
cart.actions.cleared(1);
// error TS2554: Expected 0 arguments, but got 1.

// ❌ 3. creator needing a payload called without one
cart.actions.couponApplied();
// error TS2554: Expected 1 arguments, but got 0.
```

## 💻 Code Example — Advanced

```typescript
// rtk-advanced.ts — the REAL createSlice: prepare callbacks, extraReducers, store types
import { configureStore, createSlice, type PayloadAction } from "@reduxjs/toolkit"; // RTK 2.x

interface CartItem { sku: string; qty: number; price: number } // domain
interface CartState { items: CartItem[]; coupon: string | null } // state
const initialState: CartState = { items: [], coupon: null }; // typed initial state

const cartSlice = createSlice({
  name: "cart", // becomes the action type prefix
  initialState, // S inferred from here
  reducers: {
    added(state, action: PayloadAction<CartItem>) { state.items.push(action.payload); }, // Immer lets us "mutate"
    removed(state, action: PayloadAction<string>) { // payload = sku
      state.items = state.items.filter((i) => i.sku !== action.payload); // or return a new array
    },
    cleared: () => initialState, // returning a new state is also fine
    couponApplied: { // "prepare" form: creator args differ from the payload
      reducer(state, action: PayloadAction<{ code: string; at: number }>) { state.coupon = action.payload.code; }, // payload shape
      prepare(code: string) { return { payload: { code: code.toUpperCase(), at: 0 } }; }, // creator takes ONE string
    },
  },
});

export const { added, removed, cleared, couponApplied } = cartSlice.actions; // generated creators

const store = configureStore({ reducer: { cart: cartSlice.reducer } }); // store with one slice
export type RootState = ReturnType<typeof store.getState>; // state type derived, never hand-written
export type AppDispatch = typeof store.dispatch; // dispatch type

store.dispatch(added({ sku: "dosa", qty: 2, price: 80 })); // typed dispatch
store.dispatch(couponApplied("save20")); // prepare uppercases it
const total = (s: RootState) => s.cart.items.reduce((sum, i) => sum + i.qty * i.price, 0); // typed selector
console.log(total(store.getState()), store.getState().cart.coupon, added.type); // prints 160 SAVE20 cart/added

// Discriminated-union narrowing using the generated action matcher
function isAdded(a: { type: string }): a is ReturnType<typeof added> { return added.match(a); } // type predicate via RTK matcher
console.log(isAdded({ type: "cart/added" })); // prints true
```

---

## 🟠 Node/Express + React Integration

```typescript
// server-prefetch.ts — Node/Express: seed the same slice on the server (SSR / session restore)
import express from "express"; // express + types
import { configureStore, createSlice, type PayloadAction } from "@reduxjs/toolkit"; // RTK

const cart = createSlice({
  name: "cart", initialState: { items: [] as string[] }, // state
  reducers: { added(state, a: PayloadAction<string>) { state.items.push(a.payload); } }, // one reducer
});

const app = express(); // app
app.get("/cart/preview", (_req, res) => {
  const store = configureStore({ reducer: cart.reducer }); // fresh store per request, never share between users
  store.dispatch(cart.actions.added("dosa")); // reuse the SAME reducer logic on the server
  res.json(store.getState()); // { items: ["dosa"] }
});
```

```tsx
// CartButton.tsx — React: typed hooks pattern so components never import RootState/AppDispatch ad hoc
import { configureStore, createSlice, type PayloadAction } from "@reduxjs/toolkit"; // RTK
import { useDispatch, useSelector, type TypedUseSelectorHook } from "react-redux"; // react-redux

const slice = createSlice({
  name: "cart", initialState: { count: 0 }, // tiny state
  reducers: { added(state, a: PayloadAction<number>) { state.count += a.payload; } }, // payload number
});
const store = configureStore({ reducer: { cart: slice.reducer } }); // store
type RootState = ReturnType<typeof store.getState>; // derived
type AppDispatch = typeof store.dispatch; // derived
const useAppDispatch: () => AppDispatch = useDispatch; // pre-typed dispatch hook
const useAppSelector: TypedUseSelectorHook<RootState> = useSelector; // pre-typed selector hook

export function CartButton() { // component
  const count = useAppSelector((s) => s.cart.count); // count: number, no annotation needed
  const dispatch = useAppDispatch(); // typed dispatch
  return <button onClick={() => dispatch(slice.actions.added(1))}>Cart ({count})</button>; // payload must be number
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `PayloadAction<...>` on the action parameter
```typescript
// wrong-action.ts — NO compile error, which is exactly the danger
import { createSlice } from "@reduxjs/toolkit"; // RTK

const slice = createSlice({
  name: "cart", initialState: { n: 0 }, // state
  reducers: {
    bump(state, action) { state.n += action.payload; }, // wrong: action is contextually typed, payload is any
  },
});
slice.actions.bump("not a number"); // compiles! creator accepts any payload
console.log(slice.reducer({ n: 0 }, slice.actions.bump("not a number"))); // prints { n: '0not a number' }
```
✅ Correct: `bump(state, action: PayloadAction<number>)`. Then `bump("x")` fails with `TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.` Under `strict` you do **not** get `TS7006` here, because the reducer map gives `action` a contextual type whose payload is `any`.

❌ Mistake 2: Mutating AND returning in the same reducer
```typescript
// wrong-both.ts
import { createSlice } from "@reduxjs/toolkit"; // RTK
const s = createSlice({
  name: "x", initialState: { n: 0 }, // state
  reducers: {
    // runtime error from Immer: "An immer producer returned a new value *and* modified its draft"
    bad(state) { state.n++; return { n: 5 }; }, // wrong: pick ONE style
    good(state) { state.n++; }, // right: mutate only (or return only)
  },
});
console.log(typeof s.actions.good); // prints function
```
(The compiler allows `bad`. Calling it throws at runtime: `[Immer] An immer producer returned a new value *and* modified its draft. Either return a new value *or* modify the draft.` A rule the types cannot enforce.)

❌ Mistake 3: Putting non-serializable values (Date, class instances, Map) in the slice state or payload
✅ Correct: store ISO strings / plain objects. RTK's `serializableCheck` middleware warns in development.

---

## 🧠 Tricky Interview Question

```typescript
// tricky.ts — why does cleared() take NO argument but added(item) takes one?
import { createSlice, type PayloadAction } from "@reduxjs/toolkit"; // RTK

const s = createSlice({
  name: "cart", initialState: { items: [] as string[] }, // state
  reducers: {
    cleared(state) { state.items = []; }, // no action param
    ping(state, _a: PayloadAction<void>) { state.items.length; }, // PayloadAction<void>
    maybe(state, a: PayloadAction<string | undefined>) { state.items.push(a.payload ?? ""); }, // optional payload
  },
});

s.actions.cleared(); // no args
s.actions.ping(); // no args
s.actions.maybe(); // payload may be omitted
s.actions.maybe("x"); // or given
console.log(s.actions.maybe.type); // prints cart/maybe
```
**Answer:** RTK computes each creator's signature from the reducer's **second parameter type**: no parameter or `PayloadAction<void>` -> `() => ...`; `PayloadAction<string | undefined>` -> **optional** parameter `(payload?: string)`; `PayloadAction<string>` -> required. The mechanism is the same conditional-type logic you wrote in the Basic example: `[P] extends [void]`, then `undefined extends P`. The brackets `[P] extends [void]` stop the conditional from **distributing** over a union payload.

---

## ⚫ Interview Questions + Answers

Q1: How does `createSlice` know the type of `state` inside reducers?
A1: The `reducers` option is contextually typed by `ValidateSliceCaseReducers<State, CR>`, where `State` is inferred from `initialState`. Declare `initialState` with an explicit type (`const initialState: CartState = ...`) so unions and `null` are not narrowed away.

Q2: Why wrap a conditional type in `[P] extends [void]`?
A2: Without brackets the conditional is **distributive** over naked type parameters, so a union payload splits into branches. Wrapping both sides in tuples switches distribution off.

Q3: What does `NoInfer<S>` (TS 5.4) do here?
A3: It blocks `S` from being inferred through the `reducers` argument. Without it, a reducer annotated `(state: Wrong, ...)` could change `S`; with it, `S` comes only from `initialState` and mismatches become errors.

Q4: Why does Redux Toolkit let you "mutate" state?
A4: Immer wraps the state in a draft proxy, records the mutations and produces a new immutable object. The types still show `state: CartState` (mutable), so the compiler cannot warn you about mutating **outside** a reducer.

Q5: How do `RootState` and `AppDispatch` stay in sync with the store?
A5: Derive them: `ReturnType<typeof store.getState>` and `typeof store.dispatch`. Never hand-write them, and export typed `useAppSelector`/`useAppDispatch` hooks so components never pass generics.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Global client state with many writers (cart, auth, filters) in a React app
- You want actions and reducers to share one source of truth with strict payload types

❌ Avoid when:
- State is just server data (use RTK Query / React Query)
- Purely local component state (`useState`/`useReducer` is lighter)

---

## 📊 Visual Diagram
```
 createSlice("cart", initialState, reducers)
        │             │              │
        │             │              └─ { added(state, a: PayloadAction<CartItem>) {...},
        │             │                   cleared() {...} }
        │             └─ S = CartState  (NoInfer: only from here)
        └─ N = "cart"  (literal)

 for each key K of reducers:
     2nd param  ──infer A──► PayloadAction<P> ?
             yes, P = void ──► actions.K(): { type: "cart/K" }
             yes, P = X    ──► actions.K(payload: X): { type: "cart/K"; payload: X }
             no param      ──► actions.K()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Slice | State + reducers + actions bundle | State, reducers और actions का bundle |
| `PayloadAction<P>` | Action carrying payload `P` | `P` payload वाला action |
| Action creator | Function returning an action object | Action object लौटाने वाला function |
| `infer` | Capture a type inside a conditional | Conditional में type पकड़ना |
| `NoInfer<T>` | Block inference from a position (TS 5.4) | उस जगह से inference रोकना |
| Immer draft | Proxy letting you "mutate" safely | Safe "mutation" देने वाला proxy |

---

## ⚡ 3-Line Summary
English:
1. A typed slice maps each reducer key to an action creator using `infer` on the reducer's 2nd parameter and a `` `${name}/${key}` `` template type.
2. `PayloadAction<void>` or no parameter gives a zero-argument creator; `[P] extends [void]` avoids distribution.
3. Derive `RootState`/`AppDispatch` from the store and use pre-typed hooks everywhere.

Hindi:
1. Typed slice हर reducer key को action creator में map करता है: reducer के 2nd parameter पर `infer` और `` `${name}/${key}` `` template type से।
2. `PayloadAction<void>` या parameter न होने पर zero-argument creator बनता है; `[P] extends [void]` distribution रोकता है।
3. `RootState`/`AppDispatch` को store से derive करो और हर जगह pre-typed hooks इस्तेमाल करो।

---

## ➡️ Next Topic
**107. Discriminated Union State Machine** — modelling a payment/order lifecycle so illegal states cannot be represented.
