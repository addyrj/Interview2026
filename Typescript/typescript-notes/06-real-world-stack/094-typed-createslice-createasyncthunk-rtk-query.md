# 94. Typed createSlice, createAsyncThunk and RTK Query
# हिंदी में: Typed createSlice, createAsyncThunk और RTK Query

> Verified with **TypeScript 5.9 (5.x)**, `@reduxjs/toolkit` 2.x, `react-redux` 9. `builder` callback form of `extraReducers` is required in RTK 2 (object form was removed).

---

## 🔵 Simple Definition (English)
- **`createSlice`** - types come from `initialState` and from `PayloadAction<T>` on each reducer.
- **`createAsyncThunk<Returned, ThunkArg, ThunkApiConfig>`** - three generics: what the thunk resolves to, what you pass in, and config (`state`, `rejectValue`, `extra`). The resulting `fulfilled/pending/rejected` actions are fully typed.
- **RTK Query** (`createApi`) - you declare endpoints with `builder.query<ResultType, ArgType>` and RTK generates **typed hooks** (`useGetOrdersQuery`) plus cache invalidation tags.

## 🔵 सरल परिभाषा (Hindi)
- **`createSlice`** - types `initialState` और हर reducer पर `PayloadAction<T>` से आते हैं।
- **`createAsyncThunk<Returned, ThunkArg, ThunkApiConfig>`** - तीन generics: thunk क्या return करता है, क्या argument लेता है, और config (`state`, `rejectValue`, `extra`)। इससे बने `fulfilled/pending/rejected` actions पूरी तरह typed होते हैं।
- **RTK Query** (`createApi`) - आप `builder.query<ResultType, ArgType>` से endpoints बताते हो और RTK **typed hooks** (`useGetOrdersQuery`) व cache invalidation tags बना देता है।

---

## 🔴 Problem it Solves
Hand-written fetch thunks mean three hand-typed actions (`pending/fulfilled/rejected`), `any` payloads and untyped error shapes; each screen re-implements loading/error/cache logic. Typed thunks guarantee `action.payload` is `Order[]` in `fulfilled` and your error shape in `rejected`. RTK Query removes the boilerplate entirely: caching, dedupe, refetch and typed hooks from one endpoint definition.

## 🔴 यह क्यों बना? (Hindi)
हाथ से लिखे fetch thunks में तीन actions (`pending/fulfilled/rejected`) हाथ से type करने पड़ते हैं, payload `any` रहता है और error का shape untyped। हर screen loading/error/cache logic दोबारा लिखती है। Typed thunks गारंटी देते हैं कि `fulfilled` में `action.payload` `Order[]` है और `rejected` में आपका error shape। RTK Query boilerplate पूरा हटा देता है: caching, dedupe, refetch और typed hooks एक endpoint definition से।

---

## 🟢 How it Works — Step by Step
Step 1 → `createSlice({ name, initialState, reducers })`; annotate payloads with `PayloadAction<T>`.
Step 2 → `createAsyncThunk<Order[], number, { rejectValue: ApiError }>("orders/fetch", async (userId, { rejectWithValue }) => ...)`.
Step 3 → Handle the thunk in `extraReducers: (builder) => builder.addCase(fetchOrders.fulfilled, (state, action) => ...)`; `action.payload` is `Order[]`.
Step 4 → For errors: `rejectWithValue(apiError)` makes `action.payload` the `ApiError`; a thrown error goes to `action.error` (serialized).
Step 5 → RTK Query: `createApi({ baseQuery: fetchBaseQuery(...), tagTypes, endpoints: (b) => ({ getOrders: b.query<Order[], void>(...) }) })`.
Step 6 → Export generated hooks, add `api.reducer` and `api.middleware` to the store.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `createSlice({ name, initialState, reducers })`; payloads पर `PayloadAction<T>` लगाओ।
Step 2 → `createAsyncThunk<Order[], number, { rejectValue: ApiError }>("orders/fetch", async (userId, { rejectWithValue }) => ...)`।
Step 3 → `extraReducers: (builder) => builder.addCase(fetchOrders.fulfilled, (state, action) => ...)` में thunk handle करो; `action.payload` `Order[]` होता है।
Step 4 → Errors: `rejectWithValue(apiError)` से `action.payload` `ApiError` बनता है; throw किया error `action.error` में (serialized) जाता है।
Step 5 → RTK Query: `createApi({ baseQuery: fetchBaseQuery(...), tagTypes, endpoints: (b) => ({ getOrders: b.query<Order[], void>(...) }) })`।
Step 6 → Generated hooks export करो, store में `api.reducer` और `api.middleware` जोड़ो।

---

## 🟡 Real World Example
**Razorpay payment list**: `useGetPaymentsQuery({ status: "captured" })` returns `data: Payment[] | undefined`, `isLoading`, `error`. Creating a refund calls a **mutation** that invalidates the `"Payment"` tag, so the list refetches automatically. A legacy checkout flow still uses `createAsyncThunk` with `rejectWithValue({ code: "CARD_DECLINED" })`.

## 🟡 Real Example Hindi mein
**Razorpay payment list**: `useGetPaymentsQuery({ status: "captured" })` से `data: Payment[] | undefined`, `isLoading`, `error` मिलते हैं। Refund बनाना एक **mutation** है जो `"Payment"` tag invalidate करता है, इसलिए list अपने आप refetch होती है। पुराना checkout flow अभी भी `createAsyncThunk` और `rejectWithValue({ code: "CARD_DECLINED" })` use करता है।

---

## 💻 Code Example — Basic

```typescript
// slice-basic.ts — typed slice + typed thunk
import { createAsyncThunk, createSlice, type PayloadAction } from "@reduxjs/toolkit";

interface Order { id: number; amount: number; status: "PLACED" | "PAID" } // domain type
interface ApiError { code: string; message: string }                       // rejection shape

interface OrdersState {
  list: Order[];                                   // loaded orders
  status: "idle" | "loading" | "succeeded" | "failed"; // finite states
  error: ApiError | null;                          // typed error
}
const initialState: OrdersState = { list: [], status: "idle", error: null }; // annotate -> no never[]

// Generics: <Returned, ThunkArg, ThunkApiConfig>
export const fetchOrders = createAsyncThunk<Order[], number, { rejectValue: ApiError }>(
  "orders/fetch",                                               // action type prefix
  async (userId, { rejectWithValue }) => {                      // userId: number (ThunkArg)
    if (userId <= 0) return rejectWithValue({ code: "BAD_USER", message: "invalid user" }); // typed reject
    return [{ id: 1, amount: 250, status: "PLACED" }];          // must be Order[]
  },
);

const ordersSlice = createSlice({
  name: "orders",
  initialState,
  reducers: {
    markPaid(state, action: PayloadAction<number>) {            // payload: order id
      const o = state.list.find((x) => x.id === action.payload); // o: Order | undefined
      if (o) o.status = "PAID";                                  // Immer mutation
    },
  },
  extraReducers: (builder) => {                                  // builder callback = fully typed
    builder
      .addCase(fetchOrders.pending, (s) => { s.status = "loading"; })            // no payload
      .addCase(fetchOrders.fulfilled, (s, a) => { s.status = "succeeded"; s.list = a.payload; }) // a.payload: Order[]
      .addCase(fetchOrders.rejected, (s, a) => {
        s.status = "failed";
        s.error = a.payload ?? { code: "UNKNOWN", message: a.error.message ?? "failed" }; // payload: ApiError | undefined
      });
  },
});

export const { markPaid } = ordersSlice.actions;
export default ordersSlice.reducer;
```

## 💻 Code Example — Advanced

```tsx
// rtk-query.tsx — typed API slice with tags, mutation, transformResponse
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { configureStore } from "@reduxjs/toolkit";

interface Payment { id: string; amount: number; status: "created" | "captured" | "refunded" }
interface PaymentFilter { status?: Payment["status"]; page: number }          // query argument type
interface RefundBody { paymentId: string; reason: string }                    // mutation argument

export const paymentsApi = createApi({
  reducerPath: "paymentsApi",                                                  // key in the store
  baseQuery: fetchBaseQuery({ baseUrl: "/api" }),                              // calls Express
  tagTypes: ["Payment"],                                                       // cache tag names
  endpoints: (b) => ({
    // builder.query<ResultType, ArgType>
    getPayments: b.query<Payment[], PaymentFilter>({
      query: ({ status, page }) => ({ url: "payments", params: { status, page } }), // typed arg
      providesTags: (result) =>                                                // result: Payment[] | undefined
        result ? [...result.map((p) => ({ type: "Payment" as const, id: p.id })), "Payment"] : ["Payment"],
    }),
    // builder.mutation<ResultType, ArgType>
    refund: b.mutation<Payment, RefundBody>({
      query: (body) => ({ url: "refunds", method: "POST", body }),             // body: RefundBody
      invalidatesTags: (_r, _e, arg) => [{ type: "Payment", id: arg.paymentId }], // refetch that payment
    }),
    // transformResponse changes the stored type: server sends {data}, we store Payment
    getPayment: b.query<Payment, string>({
      query: (id) => `payments/${id}`,
      transformResponse: (raw: { data: Payment }) => raw.data,                 // raw typed, result Payment
    }),
  }),
});

// Generated hooks - names derive from endpoint names
export const { useGetPaymentsQuery, useRefundMutation, useGetPaymentQuery } = paymentsApi;

export const store = configureStore({
  reducer: { [paymentsApi.reducerPath]: paymentsApi.reducer },                // computed key stays typed
  middleware: (gdm) => gdm().concat(paymentsApi.middleware),                  // required for caching
});

export function PaymentList() {
  const { data, isLoading, error } = useGetPaymentsQuery({ status: "captured", page: 1 }); // data: Payment[] | undefined
  const [refund, { isLoading: refunding }] = useRefundMutation();               // typed trigger
  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error</p>;                                               // FetchBaseQueryError | SerializedError
  return (
    <ul>
      {data?.map((p) => (
        <li key={p.id}>
          {p.amount}
          <button disabled={refunding} onClick={() => refund({ paymentId: p.id, reason: "dup" })}>Refund</button>
        </li>
      ))}
    </ul>
  );
}
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express endpoint the RTK Query definition above talks to.
import express from "express";
interface Payment { id: string; amount: number; status: "created" | "captured" | "refunded" }

const app = express();
app.use(express.json());                                     // parse JSON bodies
const db: Payment[] = [{ id: "pay_1", amount: 49900, status: "captured" }]; // pretend SQL Server

app.get("/api/payments", (req, res) => {
  const status = typeof req.query.status === "string" ? req.query.status : undefined; // query is string | ParsedQs...
  res.json(status ? db.filter((p) => p.status === status) : db); // returns Payment[]
});
app.post("/api/refunds", (req, res) => {
  const { paymentId } = req.body as { paymentId: string; reason: string }; // body is any: assert, validate with zod in prod
  const p = db.find((x) => x.id === paymentId);
  if (!p) { res.status(404).json({ message: "not found" }); return; }
  p.status = "refunded";                                       // mutate
  res.json(p);                                                 // matches Payment
});
```

```typescript
// Handling errors from RTK Query in a typed way
import type { FetchBaseQueryError } from "@reduxjs/toolkit/query";
import type { SerializedError } from "@reduxjs/toolkit";

export function errorMessage(e: FetchBaseQueryError | SerializedError | undefined): string {
  if (!e) return "";                                                   // no error
  if ("status" in e) {                                                 // narrowed: FetchBaseQueryError
    return typeof e.status === "number" ? `HTTP ${e.status}` : e.error; // status can be a string like "FETCH_ERROR"
  }
  return e.message ?? "unknown";                                        // SerializedError
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Wrong argument to an action creator
```typescript
// ❌ WRONG
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
const s = createSlice({ name: "c", initialState: { n: 0 }, reducers: { set(st, a: PayloadAction<number>) { st.n = a.payload } } });
s.actions.set("x");
// error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.
s.actions.set();
// error TS2554: Expected 1 arguments, but got 0.
```

❌ Mistake 2: `rejectWithValue` payload not matching `rejectValue`
```typescript
// ❌ WRONG
import { createAsyncThunk } from "@reduxjs/toolkit";
const t = createAsyncThunk<string, number, { rejectValue: { msg: string } }>(
  "t", async (id, { rejectWithValue }) => rejectWithValue("bad"));
// error TS2345: Argument of type 'string' is not assignable to parameter of type '{ msg: string; }'.
```
✅ Correct: `rejectWithValue({ msg: "bad" })`.

❌ Mistake 3: Forgetting to type `initialState` (state becomes `never[]`)
✅ Correct: `const initialState: OrdersState = { list: [], ... }`. Without it, `s.list = a.payload` fails because `list` is `never[]`.

❌ Mistake 4: Using the removed object notation for `extraReducers`
In RTK 2, `extraReducers: { [fetchOrders.fulfilled]: ... }` is gone. ✅ Correct: use the `builder` callback shown above; it is also the only form that types `action` correctly.

---

## 🧠 Tricky Interview Question

```typescript
// What is the type of `a.payload` inside the `rejected` case, and why do we need `?? fallback`?
import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
const t = createAsyncThunk<number, void, { rejectValue: { code: string } }>("t", async (_, api) => {
  if (Math.random() > 2) return api.rejectWithValue({ code: "E" }); // typed rejection
  throw new Error("boom");                                          // untyped rejection
});
createSlice({ name: "x", initialState: 0, reducers: {}, extraReducers: (b) => {
  b.addCase(t.rejected, (_s, a) => { const z: number = a.payload; }); // ❌ deliberate probe
  // error TS2322: Type '{ code: string; } | undefined' is not assignable to type 'number'.
  //   Type 'undefined' is not assignable to type 'number'.
} });
```
**Answer:** The error message above (real compiler output) reveals the type: `{ code: string } | undefined`. A `rejected` action has a payload **only** if the thunk used `rejectWithValue`. If the thunk *throws* (network failure, bug), RTK serializes it into `action.error` (`{ message, name, stack }`) and `payload` is `undefined`. So the reducer must handle both: `a.payload ?? { code: "UNKNOWN", message: a.error.message }`.

---

## ⚫ Interview Questions + Answers

Q1: What are the three generics of `createAsyncThunk`?
A1: `<Returned, ThunkArg, ThunkApiConfig>`. `Returned` is the fulfilled payload, `ThunkArg` is the single argument (`void` if none, a tuple/object for several), `ThunkApiConfig` can set `state`, `dispatch`, `extra`, `rejectValue`, `serializedErrorType`.

Q2: Why does a thunk accept only ONE argument?
A2: Redux action creators serialize into `meta.arg`; RTK keeps one arg for simplicity. Pass an object (`{ userId, page }`) when you need several.

Q3: RTK Query vs `createAsyncThunk` for server data?
A3: RTK Query gives caching, dedupe, polling, invalidation and typed hooks for free; use it for server state. Thunks are for imperative flows (multi-step checkout, side-effects) or when you manage the cache yourself.

Q4: How are endpoint types inferred?
A4: From `builder.query<Result, Arg>` generics. Hooks (`useGetXQuery(arg)`) take `Arg` and return `data: Result | undefined`; `void` arg means `useGetXQuery()` with no argument.

Q5: What does `providesTags` / `invalidatesTags` give you?
A5: Declarative cache coherence: queries declare tags they provide; mutations declare tags they invalidate, and RTK refetches affected queries. With `as const` on `type`, TS checks tags against `tagTypes`.

---

## 🔷 When to Use + When Not to Use
✅ Use:
- `createSlice` + `PayloadAction` for client state
- RTK Query for REST/GraphQL server state (lists, details, mutations)
- `createAsyncThunk` + `rejectValue` for non-trivial, imperative async flows

❌ Avoid:
- Putting fetched server data in a slice by hand when RTK Query would cache it
- Multi-argument thunks (wrap in an object)
- `any` for `rejectValue`; define an `ApiError` type

---

## 📊 Visual Diagram
```
createAsyncThunk<Returned, Arg, Config>
   ├─ pending    (no payload)
   ├─ fulfilled  payload: Returned
   └─ rejected   payload: Config.rejectValue | undefined
                 error:   SerializedError

createApi
  endpoints: b.query<Result, Arg>   ─► useXQuery(arg) → { data?: Result, isLoading, error }
             b.mutation<Result,Arg> ─► [trigger(arg), { isLoading }]
  tags: providesTags ◄── cache ──► invalidatesTags
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| PayloadAction<T> | Action with typed payload | typed payload वाला action |
| rejectWithValue | Thunk helper for typed errors | typed error के लिए thunk helper |
| extraReducers | Handle actions from other creators | दूसरे creators के actions handle करना |
| RTK Query | Data fetching + cache layer | data fetching + cache layer |
| Tag | Label linking queries & mutations | queries व mutations को जोड़ने वाला label |
| transformResponse | Reshape server data before caching | cache से पहले data का shape बदलना |

---

## ⚡ 3-Line Summary
English:
1. Type slices with an annotated `initialState` and `PayloadAction<T>`; use the `builder` form for `extraReducers`.
2. `createAsyncThunk<Returned, Arg, { rejectValue }>` types `fulfilled.payload` and `rejected.payload`; thrown errors land in `action.error`.
3. For server data prefer RTK Query: `builder.query<Result, Arg>` generates typed hooks and tag-based caching.

Hindi:
1. Slices को annotated `initialState` और `PayloadAction<T>` से type करो; `extraReducers` के लिए `builder` form use करो।
2. `createAsyncThunk<Returned, Arg, { rejectValue }>` से `fulfilled.payload` और `rejected.payload` typed होते हैं; throw हुए errors `action.error` में जाते हैं।
3. Server data के लिए RTK Query चुनो: `builder.query<Result, Arg>` typed hooks और tag-based caching देता है।

---

## ➡️ Next Topic
**95. TypeScript with Next.js (App Router)** — typing pages, layouts, route handlers and server actions.
