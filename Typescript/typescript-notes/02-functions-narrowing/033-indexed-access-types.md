# 33. Indexed Access Types
# हिंदी में: Indexed Access Types (`T["key"]` से type निकालना)

> TypeScript 5.x (`tsc --strict`, TS 5.9) पर verify किया गया। `T[K]` TS 2.1 से है; `as const` arrays के साथ `(typeof arr)[number]` pattern TS 3.4+ से आम है।

---

## 🔵 Simple Definition (English)
An **indexed access type** `T[K]` looks up the type of property `K` inside type `T`, exactly like `obj["key"]` looks up a value - but at the **type level**. `K` can be a string literal, a union of keys (`T["a" | "b"]`), `keyof T`, or `number` for arrays (`T[number]` gives the element type).

## 🔵 सरल परिभाषा (Hindi)
**Indexed access type** `T[K]`, type `T` के अंदर property `K` का type निकालता है, बिल्कुल वैसे जैसे `obj["key"]` value निकालता है - पर **type level** पर। `K` एक string literal, keys का union (`T["a" | "b"]`), `keyof T`, या arrays के लिए `number` (`T[number]` से element type मिलता है) हो सकता है।

---

## 🔴 Problem it Solves
An API returns an `Order` with a nested `payment.method` field. A React component needs a prop typed as "whatever payment method is". Re-declaring `"UPI" | "CARD"` in three places means a change to the model silently leaves the others stale. Likewise, if you have `const STATUSES = ["PLACED", "PAID"] as const`, you want the union type `"PLACED" | "PAID"` **without** writing it twice. Indexed access lets you **derive** types from the single source of truth.

## 🔴 यह क्यों बना? (Hindi)
एक API `Order` return करती है जिसमें nested `payment.method` field है। React component को ऐसा prop चाहिए जिसका type "payment method जो भी है" वही हो। `"UPI" | "CARD"` को तीन जगह लिखने पर model बदलते ही बाकी जगह पुराना type रह जाता है। इसी तरह `const STATUSES = ["PLACED", "PAID"] as const` से union type `"PLACED" | "PAID"` चाहिए, **दोबारा लिखे बिना**। Indexed access से आप single source of truth से types **derive** करते हो।

---

## 🟢 How it Works — Step by Step

Step 1 → `T["name"]` returns the declared type of property `name` of `T`. The key must exist, else error.
Step 2 → A **union of keys** gives a union of types: `T["a" | "b"]` = `T["a"] | T["b"]`.
Step 3 → `T[keyof T]` gives the union of **all value types** of `T`.
Step 4 → **Chain** lookups for nested data: `Order["payment"]["method"]`.
Step 5 → For arrays and tuples use `number`: `string[][number]` = `string`; for a tuple use a literal index `Tup[0]`.
Step 6 → With `typeof` on a `const` array: `(typeof STATUSES)[number]` converts a runtime list to a union type (needs `as const`).
Step 7 → For an **optional** property the result includes `undefined`; use `NonNullable<...>` or `Required<T>[K]` to drop it.
Step 8 → The index must be a **type**, not a value: `T[someVariable]` is an error, you need `T[typeof someVariable]`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `T["name"]`, `T` की property `name` का declared type देता है। Key मौजूद होनी चाहिए, वरना error।
Step 2 → **Keys का union** देने पर types का union मिलता है: `T["a" | "b"]` = `T["a"] | T["b"]`।
Step 3 → `T[keyof T]` से `T` की **सारी values के types** का union मिलता है।
Step 4 → Nested data के लिए lookups **chain** करो: `Order["payment"]["method"]`।
Step 5 → Arrays/tuples के लिए `number` इस्तेमाल करो: `string[][number]` = `string`; tuple में literal index `Tup[0]`।
Step 6 → `const` array पर `typeof` के साथ: `(typeof STATUSES)[number]` runtime list को union type में बदलता है (`as const` ज़रूरी)।
Step 7 → **Optional** property के result में `undefined` भी आता है; हटाने के लिए `NonNullable<...>` या `Required<T>[K]`।
Step 8 → Index एक **type** होना चाहिए, value नहीं: `T[someVariable]` error है, `T[typeof someVariable]` लिखो।

---

## 🟡 Real World Example
**Razorpay's** `Payment` type has `method: "upi" | "card" | "netbanking" | "wallet"`. The checkout form's `<select>` options, the analytics event and the backend validator all use `Payment["method"]` - when Razorpay adds `"emi"`, every place updates automatically. In **Zomato**, the API response `Restaurant["menu"][number]` is the type of a single menu item, reused in the `MenuRow` component without a separate `MenuItem` interface.

## 🟡 Real Example Hindi mein
**Razorpay** के `Payment` type में `method: "upi" | "card" | "netbanking" | "wallet"` है। Checkout form का `<select>`, analytics event और backend validator, सब `Payment["method"]` इस्तेमाल करते हैं - जब Razorpay `"emi"` जोड़ता है, हर जगह अपने आप update हो जाता है। **Zomato** में API response का `Restaurant["menu"][number]` एक menu item का type है, जो `MenuRow` component में बिना अलग `MenuItem` interface के reuse होता है।

---

## 💻 Code Example — Basic

```typescript
// The single source of truth: an order from the API
interface Order {
  id: string; // order id
  amount: number; // in rupees
  payment: { method: "UPI" | "CARD" | "COD"; txnId?: string }; // nested object
  items: { sku: string; qty: number }[]; // array of line items
}

// 1) Look up one property type
type OrderId = Order["id"]; // string
type Amount = Order["amount"]; // number

// 2) Chain into nested objects
type Method = Order["payment"]["method"]; // "UPI" | "CARD" | "COD"

// 3) Optional property includes undefined
type Txn = Order["payment"]["txnId"]; // string | undefined

// 4) Array element type with [number]
type Line = Order["items"][number]; // { sku: string; qty: number }

// 5) Union of keys gives union of value types
type IdOrAmount = Order["id" | "amount"]; // string | number

// 6) keyof gives union of ALL property value types
type AnyOrderValue = Order[keyof Order]; // string | number | {...} | {...}[]

// Use the derived types in real code
const method: Method = "UPI"; // OK, kept in sync with Order
const line: Line = { sku: "BIRYANI-1", qty: 2 }; // OK
console.log(method, line.qty); // UPI 2

// ❌ A key that does not exist in the type
type Bad = Order["discount"];
// error TS2339: Property 'discount' does not exist on type 'Order'.
```

## 💻 Code Example — Advanced

```typescript
// 1) Runtime list -> union type (as const + typeof + [number])
const ORDER_STATUSES = ["PLACED", "PAID", "SHIPPED", "DELIVERED"] as const; // readonly tuple
type OrderStatus = (typeof ORDER_STATUSES)[number]; // "PLACED" | "PAID" | "SHIPPED" | "DELIVERED"

// A runtime guard that uses the same list (no duplication)
function isOrderStatus(s: string): s is OrderStatus {
  return (ORDER_STATUSES as readonly string[]).includes(s); // check against the real array
}
console.log(isOrderStatus("PAID"), isOrderStatus("LOST")); // true false

// 2) Tuple positions use literal indices
type Row = [id: string, qty: number, price: number]; // SQL row as tuple
type Qty = Row[1]; // number
type Len = Row["length"]; // 3 (yes, "length" is indexable too)

// 3) Generic getter: K must be a key of T, return type is T[K]
function pluck<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key]; // return type tracks the exact key
}
const o = { id: "o1", amount: 499, paid: true }; // inferred object
const a = pluck(o, "amount"); // number (not string | number | boolean)
const p = pluck(o, "paid"); // boolean
console.log(a, p); // 499 true

// 4) Discriminated union: pick the type of the tag and of a variant
type Event =
  | { type: "PAID"; amount: number } // payment succeeded
  | { type: "FAILED"; reason: string }; // payment failed
type EventType = Event["type"]; // "PAID" | "FAILED"
type Reason = Extract<Event, { type: "FAILED" }>["reason"]; // string

// 5) Indexed access in a mapped type: build handlers keyed by tag
type Handlers = { [E in Event as E["type"]]: (e: E) => string }; // one handler per event
const handlers: Handlers = {
  PAID: (e) => `paid ${e.amount}`, // e is narrowed to the PAID member
  FAILED: (e) => `failed: ${e.reason}`, // e is narrowed to the FAILED member
};
console.log(handlers.PAID({ type: "PAID", amount: 10 })); // paid 10

// 6) Strip optionality of a nested field
type Required_Txn = NonNullable<Order2["payment"]["txnId"]>; // string
interface Order2 { payment: { txnId?: string } } // helper type

// 7) Awaited return of a function via indexed access on a mapped result
type Api = { getOrder: () => Promise<{ id: string }>; getUser: () => Promise<{ name: string }> };
type ApiResult = { [K in keyof Api]: Awaited<ReturnType<Api[K]>> }; // each method's resolved value
const r: ApiResult["getUser"] = { name: "Riya" }; // { name: string }
console.log(r.name); // Riya
```

---

## 🟠 Node/Express + React Integration

```typescript
import express from "express";

// Shared model (could live in a /shared package used by frontend and backend)
interface Payment {
  orderId: string; // which order
  method: "UPI" | "CARD" | "NETBANKING"; // allowed methods
  amount: number; // rupees
}

// Validator uses the SAME union via indexed access
const METHODS: readonly Payment["method"][] = ["UPI", "CARD", "NETBANKING"]; // typed list

const app = express(); // create app
app.use(express.json()); // parse JSON

// Body type is derived from Payment, only the fields we accept
type CreatePaymentBody = Pick<Payment, "orderId" | "amount"> & { method: string }; // method unchecked yet

app.post("/payments", (req, res) => {
  const body = req.body as CreatePaymentBody; // trust-but-verify cast
  const method = body.method as Payment["method"]; // narrow the string to the union
  if (!METHODS.includes(method)) { // runtime check backs the cast
    res.status(400).json({ error: "bad method" }); // reject invalid
    return; // stop
  }
  res.json({ ok: true, method }); // method is Payment["method"]
});
```

```tsx
import { useState, type ReactElement } from "react";

// Same model on the frontend
interface Payment { method: "UPI" | "CARD" | "NETBANKING"; amount: number }

// Option list typed from the model; adding a method forces this Record to be updated
const LABELS: Record<Payment["method"], string> = {
  UPI: "UPI / GPay", // label for UPI
  CARD: "Credit / Debit Card", // label for CARD
  NETBANKING: "Net Banking", // label for NETBANKING
};

export function MethodPicker(): ReactElement {
  const [method, setMethod] = useState<Payment["method"]>("UPI"); // state type from the model
  return (
    <select value={method} onChange={(e) => setMethod(e.target.value as Payment["method"])}>
      {(Object.keys(LABELS) as Payment["method"][]).map((m) => (
        <option key={m} value={m}>{LABELS[m]}</option>
      ))}
    </select>
  );
}
```

```typescript
// Redux Toolkit: derive action payload types from the state slice
interface CartState { items: { sku: string; qty: number }[]; coupon: string | null }
type CartItem = CartState["items"][number]; // one cart line
type Coupon = NonNullable<CartState["coupon"]>; // string (only when a coupon exists)
const add = (items: CartState["items"], item: CartItem): CartState["items"] => [...items, item]; // typed reducer helper
console.log(add([], { sku: "A1", qty: 1 }).length as number, "" as Coupon); // 1 (empty coupon string)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Indexing with a value instead of a type
```typescript
const KEY = "amount"; // a value (const string "amount")
interface Order { amount: number }

// ❌ Wrong: KEY is a value, T[...] needs a type
type Wrong = Order[KEY];
// error TS2538: Type 'KEY' cannot be used as an index type.
// error TS2749: 'KEY' refers to a value, but is being used as a type here. Did you mean 'typeof KEY'?

// Right: take the type of the value
type Right = Order[typeof KEY]; // number
```

❌ Mistake 2: `(typeof LIST)[number]` without `as const`
```typescript
const METHODS = ["UPI", "CARD"]; // inferred as string[]
type Wide = (typeof METHODS)[number]; // string (too wide, you lost the literals)

const METHODS2 = ["UPI", "CARD"] as const; // readonly ["UPI", "CARD"]
type Narrow = (typeof METHODS2)[number]; // "UPI" | "CARD"
const x: Narrow = "NETBANKING"; // ❌
// error TS2322: Type '"NETBANKING"' is not assignable to type '"UPI" | "CARD"'.
```

❌ Mistake 3: Forgetting that optional props add `undefined`
✅ Correct: `Order["payment"]["txnId"]` is `string | undefined`; if you need the plain `string` after a check use `NonNullable<Order["payment"]["txnId"]>`.

---

## 🧠 Tricky Interview Question

```typescript
type T1 = { a: string; b: number };
type R1 = T1[keyof T1]; // ?
type R2 = string[][number]; // ?
type R3 = [string, number][number]; // ?
type R4 = T1["a" | "c"]; // ❌ ?
```
**Answer:** `R1 = string | number` (union of all value types). `R2 = string` (array element). `R3 = string | number` (for a tuple, `[number]` is the **union of all element types**). `R4` is an **error**: `"c"` is not a key of `T1`:
```typescript
type T1b = { a: string; b: number };
type R4b = T1b["a" | "c"]; // ❌
// error TS2339: Property 'c' does not exist on type 'T1b'.
```
Key idea: with a union index, **every** member must be a valid key, otherwise the whole lookup fails.

---

## ⚫ Interview Questions + Answers

Q1: What is an indexed access type and how is it different from `keyof`?
A1: `T[K]` returns the **type of the value** at key `K`. `keyof T` returns the **union of key names**. They combine: `T[keyof T]` is the union of all value types. `keyof` answers "what are the keys", indexed access answers "what is stored under them".

Q2: How do you get the element type of an array type?
A2: `T[number]`, e.g. `Order["items"][number]`. For a `readonly` tuple created with `as const` use `(typeof LIST)[number]` to get the union of literals - the standard way to avoid declaring a union and an array separately.

Q3: Why do we write `function get<T, K extends keyof T>(o: T, k: K): T[K]`?
A3: `K extends keyof T` guarantees the key exists, and the return type `T[K]` is **exact** for the passed key (`number` for `"amount"`), not the loose union of all properties. Without the generic `K` you could only return `T[keyof T]`, losing precision.

Q4: How do you extract a nested type from an API response without declaring a new interface?
A4: Chain lookups: `Response["data"]["orders"][number]["payment"]`. For async function results combine with utilities: `Awaited<ReturnType<typeof fetchOrders>>[number]`. This keeps types in sync with the producer.

Q5: What happens with indexed access on a union type, e.g. `(A | B)["id"]`?
A5: The property must exist in **every** member; the result is the union of the member property types (`A["id"] | B["id"]`). If one member lacks the property, it is an error, so you narrow first or use `Extract`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want a field type to stay in sync with a model (`Payment["method"]`, `State["items"][number]`)
- Converting a runtime constant list to a union (`(typeof LIST)[number]`)
- Writing generic getters/setters (`T[K]`) that keep exact key-value types
- Deriving props/payload types for React and Redux from one interface

❌ Avoid when:
- The nested type is used everywhere and deserves a **name** (`type OrderItem = Order["items"][number]`) - name it once for readability
- Chains get very long (4+ levels) and hurt readability: export the intermediate type
- You need a value, not a type: indexed access exists only at the type level, it emits no JavaScript

---

## 📊 Visual Diagram
```
INDEXED ACCESS  T[K]

interface Order {
  id: string
  payment: { method: "UPI"|"CARD" ; txnId?: string }
  items: { sku: string }[]
}

Order["id"]                       ──►  string
Order["payment"]["method"]        ──►  "UPI" | "CARD"
Order["payment"]["txnId"]         ──►  string | undefined
Order["items"][number]            ──►  { sku: string }
Order["id" | "payment"]           ──►  string | {...}
Order[keyof Order]                ──►  union of ALL value types

const L = ["A","B"] as const
(typeof L)[number]                ──►  "A" | "B"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Indexed access type | `T[K]`, type of property K in T | T में K property का type |
| keyof | Union of the key names of a type | type की keys का union |
| `[number]` index | Element type of an array/tuple | array/tuple का element type |
| Lookup chain | `A["b"]["c"]` nested lookup | nested property का type निकालना |
| as const | Freeze literals so they stay narrow | literals को narrow रखना |
| Single source of truth | One declaration other types derive from | एक जगह declare, बाकी वहीं से derive |

---

## ⚡ 3-Line Summary
English:
1. `T[K]` reads the type stored under key `K`; chain it for nested data and use `[number]` for array elements.
2. `(typeof LIST)[number]` with `as const` turns a runtime list into a union with zero duplication.
3. Pair it with `K extends keyof T` to write generic getters whose return type is exact.

Hindi:
1. `T[K]` key `K` के नीचे रखा type पढ़ता है; nested data के लिए chain करो और array element के लिए `[number]` लगाओ।
2. `as const` के साथ `(typeof LIST)[number]` runtime list को बिना duplication के union बना देता है।
3. `K extends keyof T` के साथ मिलाकर ऐसे generic getters लिखो जिनका return type exact हो।

---

## ➡️ Next Topic
**34. satisfies Operator** — validate a value against a type without widening it (TS 4.9+).
