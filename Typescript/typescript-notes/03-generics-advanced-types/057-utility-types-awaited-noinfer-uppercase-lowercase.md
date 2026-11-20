# 57. Utility Types — Awaited, NoInfer, Uppercase/Lowercase
# हिंदी में: Utility Types — Awaited, NoInfer, Uppercase/Lowercase

> TypeScript 5.x (`tsc --strict`, TS 5.9) पर verify किया गया। `Uppercase/Lowercase/Capitalize/Uncapitalize` TS 4.1 से; `Awaited<T>` TS 4.5 से; **`NoInfer<T>` TS 5.4+** (पुराने version पर "Cannot find name 'NoInfer'")।

---

## 🔵 Simple Definition (English)
Three families of built-in helpers:
- **`Awaited<T>`** unwraps a Promise recursively: `Awaited<Promise<Promise<number>>>` = `number`.
- **`NoInfer<T>`** (TS 5.4) tells inference "do **not** use this position to infer `T`" - other arguments decide.
- **`Uppercase<S>`, `Lowercase<S>`, `Capitalize<S>`, `Uncapitalize<S>`** transform **string literal types** (they are compiler intrinsics, not written in TS).

## 🔵 सरल परिभाषा (Hindi)
तीन तरह के built-in helpers:
- **`Awaited<T>`** Promise को recursively खोलता है: `Awaited<Promise<Promise<number>>>` = `number`।
- **`NoInfer<T>`** (TS 5.4) inference को बताता है "इस जगह से `T` infer **मत** करो" - बाकी arguments तय करेंगे।
- **`Uppercase<S>`, `Lowercase<S>`, `Capitalize<S>`, `Uncapitalize<S>`** **string literal types** को बदलते हैं (ये compiler intrinsics हैं, TS में लिखे नहीं गए)।

---

## 🔴 Problem it Solves
1. `ReturnType<typeof fetchOrders>` gives `Promise<Order[]>`, but your component wants the **resolved** `Order[]`. Hand-unwrapping with `infer` breaks for nested promises and `PromiseLike`. `Awaited` handles all of it, and it is what `Promise.all` uses internally.
2. Generic functions often have two arguments with the same `T`: `createStore(initial, defaultValue)`. If the second is just a fallback, TypeScript may **widen `T`** to include it and hide a bug. `NoInfer` pins `T` to the main argument.
3. Building keys like `"ORDER_PLACED"` from `"orderPlaced"` or `"onClick"` from `"click"` used to need manual duplication. The string intrinsics transform literal types.

## 🔴 यह क्यों बना? (Hindi)
1. `ReturnType<typeof fetchOrders>` से `Promise<Order[]>` मिलता है, पर component को **resolved** `Order[]` चाहिए। `infer` से हाथ से unwrap करना nested promises और `PromiseLike` पर टूट जाता है। `Awaited` सब संभालता है, और `Promise.all` भी अंदर यही इस्तेमाल करता है।
2. Generic functions में अक्सर दो arguments एक ही `T` वाले होते हैं: `createStore(initial, defaultValue)`। अगर दूसरा सिर्फ fallback है, तो TypeScript `T` को **widen** करके उसे भी शामिल कर सकता है और bug छुप जाता है। `NoInfer` `T` को मुख्य argument पर pin करता है।
3. `"orderPlaced"` से `"ORDER_PLACED"` या `"click"` से `"onClick"` जैसी keys पहले हाथ से duplicate करनी पड़ती थीं। String intrinsics literal types को transform करते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `Awaited<T>`: if `T` is `PromiseLike<U>` (has a `then` whose callback takes `U`), it recurses into `U`; otherwise returns `T`. Non-promises pass through: `Awaited<number>` = `number`.
Step 2 → Combine: `Awaited<ReturnType<typeof fn>>` = resolved value of an async function. This is **the** idiom for deriving data types from API functions.
Step 3 → `NoInfer<T>` is an intrinsic marker. In `f<T>(a: T, b: NoInfer<T>)`, candidates for `T` are collected only from `a`; `b` is then **checked** against that `T`.
Step 4 → Use `NoInfer` for defaults, "current value" in reducers, and `Record` keys that must come from one source. **Needs TS 5.4+**.
Step 5 → `Uppercase<"upi">` = `"UPI"`; `Capitalize<"paid">` = `"Paid"`. They distribute over unions: `Uppercase<"a" | "b">` = `"A" | "B"`.
Step 6 → With **template literal types**: `` `on${Capitalize<E>}` `` turns `"click"` into `"onClick"`; `` `${Uppercase<S>}_EVENT` `` builds constants.
Step 7 → On a non-literal `string` they give `Uppercase<string>` (still a branded-ish template-like type), not plain `string`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `Awaited<T>`: अगर `T` `PromiseLike<U>` है तो `U` में recurse करता है; वरना `T` ही लौटाता है। Non-promise वैसे ही निकलता है: `Awaited<number>` = `number`।
Step 2 → मिलाकर: `Awaited<ReturnType<typeof fn>>` = async function की resolved value। API functions से data types derive करने का **यही** idiom है।
Step 3 → `NoInfer<T>` एक intrinsic marker है। `f<T>(a: T, b: NoInfer<T>)` में `T` के candidates सिर्फ `a` से लिए जाते हैं; `b` को उसी `T` के against **check** किया जाता है।
Step 4 → Defaults, reducers की "current value" और ऐसी `Record` keys के लिए `NoInfer` लगाओ जो एक ही source से आनी हैं। **TS 5.4+ चाहिए**।
Step 5 → `Uppercase<"upi">` = `"UPI"`; `Capitalize<"paid">` = `"Paid"`। ये unions पर distribute होते हैं: `Uppercase<"a" | "b">` = `"A" | "B"`।
Step 6 → **Template literal types** के साथ: `` `on${Capitalize<E>}` `` से `"click"` → `"onClick"`; `` `${Uppercase<S>}_EVENT` `` से constants बनते हैं।
Step 7 → Plain `string` पर ये `Uppercase<string>` देते हैं (plain `string` नहीं)।

---

## 🟡 Real World Example
**Swiggy's** `getOrders()` is `async` and returns `Order[]`. The Redux thunk, the React Query hook and the test mock all need `Awaited<ReturnType<typeof getOrders>>` so they stay correct if the API function changes. In **Paytm's** event tracker, event names like `"payment_success"` are turned into handler names `"onPaymentSuccess"` using `Capitalize` and template literals, and `NoInfer` makes sure `track("payment_success", defaultPayload)` cannot silently widen the event type.

## 🟡 Real Example Hindi mein
**Swiggy** का `getOrders()` `async` है और `Order[]` देता है। Redux thunk, React Query hook और test mock, सबको `Awaited<ReturnType<typeof getOrders>>` चाहिए ताकि API function बदलने पर भी types सही रहें। **Paytm** के event tracker में `"payment_success"` जैसे event names से `Capitalize` और template literals द्वारा handler names `"onPaymentSuccess"` बनते हैं, और `NoInfer` पक्का करता है कि `track("payment_success", defaultPayload)` event type को चुपचाप widen न कर सके।

---

## 💻 Code Example — Basic

```typescript
// An async API function
interface Order { id: string; amount: number } // order shape
async function getOrders(): Promise<Order[]> { // returns a promise
  return [{ id: "o1", amount: 499 }]; // one fake order
}

// ReturnType alone still has the Promise wrapper
type Raw = ReturnType<typeof getOrders>; // Promise<Order[]>

// Awaited removes the wrapper: the value you get after `await`
type Resolved = Awaited<ReturnType<typeof getOrders>>; // Order[]

// Recursion: nested promises are fully unwrapped
type Deep = Awaited<Promise<Promise<number>>>; // number
type Plain = Awaited<string>; // string (non-promises pass through)
type Mixed = Awaited<string | Promise<number>>; // string | number

// Use the derived type for a variable
async function main(): Promise<void> {
  const orders: Resolved = await getOrders(); // typed as Order[]
  console.log(orders.length); // 1
}
void main(); // run it

// String intrinsics on literal types
type Up = Uppercase<"upi">; // "UPI"
type Low = Lowercase<"NETBANKING">; // "netbanking"
type Cap = Capitalize<"paid">; // "Paid"
type Unc = Uncapitalize<"Paid">; // "paid"
const m: Up = "UPI"; // OK
console.log(m, "" as Low, "" as Cap, "" as Unc); // UPI (plus three empty strings)

// ❌ Wrong case for the transformed literal
const bad: Up = "upi";
// error TS2322: Type '"upi"' is not assignable to type '"UPI"'.
```

## 💻 Code Example — Advanced

```typescript
// ===== 1) NoInfer (TS 5.4+): default must NOT widen T =====
type Method = "UPI" | "CARD" | "COD"; // allowed values

// Without NoInfer: T is inferred from BOTH arguments
function pickLoose<T extends string>(options: T[], fallback: T): T {
  return options[0] ?? fallback; // returns one of them
}
// "WALLET" is not in the list, but T widens to "UPI" | "CARD" | "WALLET" (bug hidden)
const loose = pickLoose(["UPI", "CARD"], "WALLET"); // compiles, T = "UPI" | "CARD" | "WALLET"

// With NoInfer: T comes ONLY from `options`, fallback is just checked
function pickStrict<T extends string>(options: T[], fallback: NoInfer<T>): T {
  return options[0] ?? fallback; // same body
}
const strict = pickStrict(["UPI", "CARD"], "UPI"); // OK, T = "UPI" | "CARD"
console.log(loose, strict); // UPI UPI

// ❌ Now the bad fallback is caught
const bad = pickStrict(["UPI", "CARD"], "WALLET");
// error TS2345: Argument of type '"WALLET"' is not assignable to parameter of type '"UPI" | "CARD"'.

// ===== 2) Awaited with Promise.all-like helper =====
async function fetchUser(): Promise<{ name: string }> { return { name: "Riya" }; } // user API
async function fetchCart(): Promise<{ items: number }> { return { items: 3 }; } // cart API
type Loaders = { user: typeof fetchUser; cart: typeof fetchCart }; // map of loaders
type Loaded = { [K in keyof Loaders]: Awaited<ReturnType<Loaders[K]>> }; // resolved values
const page: Loaded = { user: { name: "Riya" }, cart: { items: 3 } }; // fully typed page data
console.log(page.user.name, page.cart.items); // Riya 3

// ===== 3) String intrinsics + template literals =====
type DomainEvent = "payment_success" | "payment_failed" | "order_placed"; // snake_case events

// snake_case -> PascalCase using recursion + Capitalize
type Pascal<S extends string> = S extends `${infer H}_${infer T}`
  ? `${Capitalize<H>}${Pascal<T>}` // capitalise the head and recurse
  : Capitalize<S>; // last segment

type HandlerName<E extends string> = `on${Pascal<E>}`; // "onPaymentSuccess"
type Handlers = { [E in DomainEvent as HandlerName<E>]: () => void }; // keys renamed via `as`

const handlers: Handlers = {
  onPaymentSuccess: () => console.log("ok"), // key generated from the event union
  onPaymentFailed: () => console.log("failed"), // second key
  onOrderPlaced: () => console.log("placed"), // third key
};
handlers.onPaymentSuccess(); // ok

// Constants: "orderPlaced" -> "ORDER_PLACED" style prefix
type Const<S extends string> = `EVT_${Uppercase<S>}`; // EVT_ + uppercase
const key: Const<"paid"> = "EVT_PAID"; // compiles
console.log(key); // EVT_PAID
```

---

## 🟠 Node/Express + React Integration

```typescript
import express from "express";

// Service layer: async functions are the single source of truth
interface Payment { id: string; status: "CAPTURED" | "FAILED" } // payment row
async function findPayment(id: string): Promise<Payment | undefined> { // SQL Server lookup (mocked)
  return id === "p1" ? { id, status: "CAPTURED" } : undefined; // fake data
}

// Derive the resolved type once, reuse everywhere (controller, tests, mappers)
type FoundPayment = Awaited<ReturnType<typeof findPayment>>; // Payment | undefined

const app = express(); // create app
app.get("/payments/:id", async (req, res) => {
  const payment: FoundPayment = await findPayment(String(req.params.id)); // typed result
  if (!payment) { // handle undefined
    res.status(404).json({ error: "not found" }); // not found
    return; // stop
  }
  res.json(payment); // payment is Payment here
});
```

```tsx
import { useEffect, useState, type ReactElement } from "react";

// API function and its resolved type
async function getOrders(): Promise<{ id: string; total: number }[]> { return []; } // mock API
type OrdersData = Awaited<ReturnType<typeof getOrders>>; // { id: string; total: number }[]

// Generic hook: state type comes from the async function, not hand-written
function useAsync<F extends () => Promise<unknown>>(fn: F, initial: NoInfer<Awaited<ReturnType<F>>>) {
  const [data, setData] = useState<Awaited<ReturnType<F>>>(initial); // state = resolved type
  useEffect(() => { void fn().then((d) => setData(d as Awaited<ReturnType<F>>)); }, [fn]); // load once
  return data; // typed result
}

export function OrderCount(): ReactElement {
  const orders: OrdersData = useAsync(getOrders, []); // initial [] is checked against OrdersData
  return <span>{orders.length} orders</span>; // render count
}
```

```typescript
// Redux Toolkit: reducer state typed from the thunk's resolved value
import { createAsyncThunk } from "@reduxjs/toolkit";

const fetchMenu = async (restaurantId: string) => [{ sku: "B1", name: "Biryani", restaurantId }]; // payload creator
const loadMenu = createAsyncThunk("menu/load", fetchMenu); // thunk built from it
type MenuItems = Awaited<ReturnType<typeof fetchMenu>>; // { sku; name; restaurantId }[]
type Fulfilled = ReturnType<typeof loadMenu.fulfilled>; // the fulfilled action type
const count = (items: MenuItems): number => items.length; // reducer-style helper
void fetchMenu("r1").then((items) => {
  const action: Fulfilled = loadMenu.fulfilled(items, "req1", "r1"); // build the action
  console.log(count(action.payload), action.type); // 1 menu/load/fulfilled
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `ReturnType` of an async function and expecting the value
```typescript
async function getTotal(): Promise<number> { return 100; } // async function

// Wrong: this is Promise<number>, not number
type Wrong = ReturnType<typeof getTotal>; // Promise<number>
const t: Wrong = 100;
// ❌ error TS2322: Type 'number' is not assignable to type 'Promise<number>'.

// Right: unwrap with Awaited
type Right = Awaited<ReturnType<typeof getTotal>>; // number
const ok: Right = 100; // compiles
```

❌ Mistake 2: Using `NoInfer` on the argument that SHOULD drive inference
```typescript
// Wrong: both positions blocked, T has no candidate -> falls back to the constraint
function wrong<T extends string>(a: NoInfer<T>, b: NoInfer<T>): T { return a; } // nothing infers T
const w = wrong("UPI", "CARD"); // T = string (lost the literals)
type W = typeof w; // string

// Right: leave exactly ONE position free to infer, wrap the others
function right<T extends string>(a: T, b: NoInfer<T>): T { return a; } // a drives inference
const r = right("UPI", "UPI"); // T = "UPI"
```

❌ Mistake 3: Assuming `Uppercase<string>` is just `string`
```typescript
const raw: string = "abc"; // a plain string
// ❌ plain string is not assignable to Uppercase<string>
const x: Uppercase<string> = raw;
// error TS2322: Type 'string' is not assignable to type 'Uppercase<string>'.
const y: Uppercase<string> = "ABC"; // OK: an already-uppercase literal
```
✅ Correct: use the helpers on literal types; if you need an uppercase runtime string, call `.toUpperCase()` (it returns plain `string`) and cast only if you must.

---

## 🧠 Tricky Interview Question

```typescript
type A = Awaited<Promise<string> | number>;
type B = Awaited<{ then(cb: (v: boolean) => void): void }>;
type C = Awaited<Promise<number>[]>;
```
**Answer:** `A = string | number` (distributes over the union). `B = boolean` - `Awaited` works on any **thenable** (`PromiseLike`), not just real `Promise`. `C = Promise<number>[]` - an **array** of promises is not a thenable, so nothing is unwrapped (to await the elements use `Promise.all` or `Awaited<Promise<number>>[]`). Interviewers like this because many people believe `Awaited` "goes deep into arrays"; it does not - `Promise.all`'s own return type does the mapping with a mapped tuple.

---

## ⚫ Interview Questions + Answers

Q1: Why was `Awaited<T>` added in TS 4.5, and how does it relate to `Promise.all`?
A1: Before 4.5 `await` and `Promise.all` used ad-hoc rules to unwrap promises, and `await` on a generic `T` could not be typed correctly. `Awaited<T>` is the single recursive definition of "what you get after `await`". `Promise.all` is typed as `Promise<{ -readonly [P in keyof T]: Awaited<T[P]> }>`, so tuples keep per-element resolved types.

Q2: What problem does `NoInfer<T>` (TS 5.4) solve? Give an example.
A2: It prevents a parameter from contributing inference candidates for `T`. In `createFSM<S extends string>(states: S[], initial: NoInfer<S>)`, `S` is inferred only from `states`, so passing an `initial` that is not in the list is an error instead of silently widening `S`. Before 5.4 people used tricks like `T & {}` or `[T][T extends any ? 0 : never]`.

Q3: How do you get the type a thunk or API function **resolves to**?
A3: `Awaited<ReturnType<typeof fn>>`. For an RTK thunk, `Awaited<ReturnType<typeof thunk>>` is the fulfilled/rejected action; for the plain payload use `Awaited<ReturnType<typeof payloadCreator>>`.

Q4: What do `Capitalize`, `Uppercase`, `Lowercase`, `Uncapitalize` do, and are they distributive?
A4: They are intrinsic string-literal transformers implemented inside the compiler (you cannot write them in plain TS). They distribute over unions: `Capitalize<"a" | "b">` = `"A" | "B"`. They are most useful inside template literal types and key remapping (`as`) to generate names like `onClick` or `SET_AMOUNT`.

Q5: How do you convert `"payment_success"` to `"paymentSuccess"` at type level?
A5: Use a recursive conditional type with `infer` and template literals: split at `_`, `Uncapitalize` the first part, `Capitalize` the rest, and concatenate. The intrinsics do the case change, template literal types do the splitting (topic 50 and 49).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Deriving the data type from an `async` function (`Awaited<ReturnType<typeof fn>>`) for thunks, hooks, mocks
- A generic has a "main" argument and a "default/fallback" argument (`NoInfer`)
- Generating key/handler/constant names from a union of literals (`Capitalize`, `Uppercase`)

❌ Avoid when:
- You can simply name the type: if `Order[]` is used 20 times, declare `type Orders = Order[]` rather than recompute it
- Targeting TS < 5.4 (`NoInfer` unavailable) - use a local helper `type NoInfer<T> = [T][T extends any ? 0 : never]`
- Applying case helpers to wide `string` - they do not produce plain `string`

---

## 📊 Visual Diagram
```
Awaited<T>                        NoInfer<T>  (TS 5.4)
──────────────────────            ───────────────────────────────
Promise<Promise<X>>  ─► X         f<T>(a: T, b: NoInfer<T>)
PromiseLike<X>       ─► X              │         │
X (not a promise)    ─► X              │         └─ only CHECKED against T
Promise<A> | B       ─► A | B          └─ infers T

String intrinsics (on literals)
──────────────────────────────────────────
Uppercase<"upi">       ─► "UPI"
Lowercase<"UPI">       ─► "upi"
Capitalize<"paid">     ─► "Paid"
Uncapitalize<"Paid">   ─► "paid"
`on${Capitalize<"click">}` ─► "onClick"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Awaited | Recursive "type after await" | `await` के बाद वाला type |
| Thenable / PromiseLike | Object with a `then` method | `then` method वाला object |
| NoInfer | Blocks inference from one position | एक जगह से inference रोकता है |
| Inference candidate | A type TS considers for a type parameter | type parameter के लिए संभावित type |
| Intrinsic type | Built into the compiler, not written in TS | compiler में built-in type |
| Key remapping (`as`) | Rename keys in a mapped type | mapped type में key का नाम बदलना |

---

## ⚡ 3-Line Summary
English:
1. `Awaited<ReturnType<typeof fn>>` is the standard way to get the resolved value type of any async function.
2. `NoInfer<T>` (TS 5.4+) stops defaults and fallbacks from widening a generic.
3. `Uppercase/Lowercase/Capitalize/Uncapitalize` transform literal types and power generated key names like `onPaymentSuccess`.

Hindi:
1. `Awaited<ReturnType<typeof fn>>` किसी भी async function की resolved value का type पाने का standard तरीका है।
2. `NoInfer<T>` (TS 5.4+) defaults और fallbacks को generic widen करने से रोकता है।
3. `Uppercase/Lowercase/Capitalize/Uncapitalize` literal types को बदलते हैं और `onPaymentSuccess` जैसे generated key names बनाते हैं।

---

## ➡️ Next Topic
**58. Branded / Nominal Types** — make `UserId` and `OrderId` incompatible even though both are `string`.
