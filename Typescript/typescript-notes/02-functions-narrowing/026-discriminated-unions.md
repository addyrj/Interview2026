# 26. Discriminated Unions
# हिंदी में: Discriminated Unions (tag वाले unions)

> Verified with TypeScript 5.x (5.9) under `tsc --strict`.

---

## 🔵 Simple Definition (English)
A **discriminated union** (tagged union) is a union of object types that all share one property with a **unique literal type** (the *discriminant*, e.g. `status: "paid"`). Checking that one property lets TypeScript narrow to exactly one member, and you then access only the fields that exist for that case.

## 🔵 सरल परिभाषा (Hindi)
**Discriminated union** (tagged union) object types का union है जिनमें एक common property होती है जिसका **unique literal type** होता है (*discriminant*, जैसे `status: "paid"`)। सिर्फ़ उस एक property को check करने से TypeScript ठीक एक member तक narrow कर देता है, और फिर आप सिर्फ़ वही fields access करते हैं जो उस case में मौजूद हैं।

---

## 🔴 Problem it Solves
Modeling state with one wide object (`{ status: string; data?: X; error?: string; txnId?: string }`) allows impossible states, such as `status: "failed"` with a `txnId`, or `"success"` with no data. Every consumer then needs `!`/`?.` and guesses. A discriminated union makes illegal states **unrepresentable** and the compiler checks each case.

## 🔴 यह क्यों बना? (Hindi)
State को एक चौड़े object (`{ status: string; data?: X; error?: string; txnId?: string }`) में रखने से असंभव states बन सकती हैं, जैसे `status: "failed"` के साथ `txnId`, या `"success"` बिना data के। फिर हर consumer को `!`/`?.` लगाना पड़ता है और अंदाज़ा लगाना पड़ता है। Discriminated union गलत states को **represent ही नहीं होने देता** और compiler हर case जाँचता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Give each member a common property with a distinct **literal** type (`kind`, `type`, `status`).
Step 2 → Combine them: `type Result = Ok | Err`.
Step 3 → Check the discriminant with `if (r.status === "ok")` or `switch (r.status)`.
Step 4 → Inside each branch TypeScript narrows to that single member, so its unique fields are available.
Step 5 → Add a `default` branch assigning to `never` to get **exhaustiveness checking** (next notes: 29).
Step 6 → The discriminant must be a literal (string, number, boolean, null/undefined), not plain `string`.
Step 7 → Redux actions (`{ type: "cart/add"; ... }`) and reducers are the most common real-world use.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → हर member में एक common property दो जिसका type अलग **literal** हो (`kind`, `type`, `status`)।
Step 2 → उन्हें जोड़ो: `type Result = Ok | Err`।
Step 3 → Discriminant को `if (r.status === "ok")` या `switch (r.status)` से check करो।
Step 4 → हर branch में TypeScript उसी एक member तक narrow करता है, इसलिए उसके unique fields मिलते हैं।
Step 5 → `default` branch में `never` को assign करके **exhaustiveness checking** पाओ (note 29)।
Step 6 → Discriminant literal होना चाहिए (string, number, boolean, null/undefined), सादा `string` नहीं।
Step 7 → Redux actions (`{ type: "cart/add"; ... }`) और reducers इसका सबसे आम real-world उपयोग हैं।

---

## 🟡 Real World Example
**Razorpay payment result**: `{ status: "success"; paymentId: string }`, `{ status: "failed"; reason: string }`, `{ status: "pending"; retryAfterSec: number }`. UI shows a tick on success, the reason on failure, and a countdown on pending, and cannot read `reason` on a success object by mistake.

## 🟡 Real Example Hindi mein
**Razorpay payment result**: `{ status: "success"; paymentId: string }`, `{ status: "failed"; reason: string }`, `{ status: "pending"; retryAfterSec: number }`। UI success पर tick, failure पर कारण और pending पर countdown दिखाती है, और success object पर गलती से `reason` नहीं पढ़ सकती।

---

## 💻 Code Example — Basic

```typescript
// Three payment outcomes, each with its own fields and a literal 'status' tag
type PaymentResult =
  | { status: "success"; paymentId: string } // paid
  | { status: "failed"; reason: string } // declined
  | { status: "pending"; retryAfterSec: number }; // waiting for bank

// switch on the discriminant: each case narrows to ONE member
function message(r: PaymentResult): string {
  switch (r.status) {
    case "success":
      return `Paid: ${r.paymentId}`; // r: { status: "success"; paymentId }
    case "failed":
      return `Failed: ${r.reason}`; // r: { status: "failed"; reason }
    case "pending":
      return `Retry in ${r.retryAfterSec}s`; // r: { status: "pending"; retryAfterSec }
  }
}

console.log(message({ status: "success", paymentId: "pay_9" })); // success branch
console.log(message({ status: "failed", reason: "insufficient funds" })); // failed branch
console.log(message({ status: "pending", retryAfterSec: 30 })); // pending branch
```

Run with `npx tsx`:

```
Paid: pay_9
Failed: insufficient funds
Retry in 30s
```

## 💻 Code Example — Advanced

```typescript
// Advanced: generic Result<T,E>, async state machine, narrowing with if, and extracting members

// Generic discriminated union for success/failure (like Rust's Result)
type Result<T, E = string> =
  | { ok: true; value: T } // boolean discriminant: true
  | { ok: false; error: E }; // boolean discriminant: false

// Helper constructors keep literal types
const ok = <T,>(value: T): Result<T> => ({ ok: true, value }); // success builder
const err = <E,>(error: E): Result<never, E> => ({ ok: false, error }); // failure builder

// Function that returns a Result instead of throwing
function parseQty(input: string): Result<number> {
  const n = Number(input); // convert
  if (!Number.isInteger(n) || n <= 0) return err("qty must be a positive integer"); // failure
  return ok(n); // success
}

// Consumer narrows by 'ok'
const r = parseQty("3"); // Result<number>
if (r.ok) {
  console.log(r.value * 2); // r: { ok: true; value: number }
} else {
  console.log(r.error); // r: { ok: false; error: string }
}

// Async request state, the classic UI/Redux shape
type Req<T> =
  | { state: "idle" } // not started
  | { state: "loading" } // in flight
  | { state: "done"; data: T } // finished
  | { state: "error"; message: string }; // failed

// Extract one member by its tag using Extract<>
type Done = Extract<Req<number[]>, { state: "done" }>; // { state: "done"; data: number[] }
const d: Done = { state: "done", data: [1, 2] }; // valid Done
console.log(d.data.length); // 2

// Narrowing works on destructured discriminants too (TS 4.6+ for destructured unions)
function show({ state, ...rest }: { state: "a"; x: number } | { state: "b"; y: string }): string {
  return state === "a" ? "A" : "B"; // simple tag use
}
console.log(show({ state: "b", y: "q" }), parseQty("-1")); // B and the failure object
```

Run with `npx tsx`:

```
6
2
B { ok: false, error: 'qty must be a positive integer' }
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express + Redux-style reducer: actions are a discriminated union on 'type'
import express from "express"; // express
import type { Request, Response } from "express"; // types

// Redux-style cart actions (same shape as Redux Toolkit's action.type)
type CartAction =
  | { type: "cart/add"; sku: string; qty: number } // add item
  | { type: "cart/remove"; sku: string } // remove item
  | { type: "cart/clear" }; // empty cart

type CartState = Record<string, number>; // sku -> qty

// Reducer: switch on action.type narrows the payload fields
function cartReducer(state: CartState, action: CartAction): CartState {
  switch (action.type) {
    case "cart/add":
      return { ...state, [action.sku]: (state[action.sku] ?? 0) + action.qty }; // has sku + qty
    case "cart/remove": {
      const { [action.sku]: _gone, ...rest } = state; // has sku only
      return rest; // without the sku
    }
    case "cart/clear":
      return {}; // no payload fields exist here
  }
}

// API response union: server returns different shapes by 'status'
type ApiResponse = { status: "ok"; cart: CartState } | { status: "error"; code: number; message: string };

const app = express(); // app
app.post("/cart", (_req: Request, res: Response<ApiResponse>) => {
  const cart = cartReducer({}, { type: "cart/add", sku: "BIRYANI", qty: 2 }); // compute
  res.json({ status: "ok", cart }); // matches the ok member
});
```

```tsx
// React: render by discriminant, no optional chaining needed
import type { ReactNode } from "react"; // type

type View<T> =
  | { state: "loading" } // spinner
  | { state: "error"; message: string } // message
  | { state: "ready"; items: T[] }; // data

export function OrderList({ view }: { view: View<string> }): ReactNode {
  if (view.state === "loading") return <p>Loading...</p>; // no items here
  if (view.state === "error") return <p role="alert">{view.message}</p>; // message exists
  return <ul>{view.items.map((o) => <li key={o}>{o}</li>)}</ul>; // items exist
}
```

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: Discriminant typed as plain `string` (no narrowing).**

```typescript
// ❌ WRONG: 'status: string' is not a literal, so the compiler cannot tell members apart
type Bad = { status: string; reason: string } | { status: string; id: string };
function f(b: Bad): string {
  if (b.status === "failed") return b.reason; // ❌ reason is not on every member
  return "";
}
```

Real compiler output:

```
error TS2339: Property 'reason' does not exist on type 'Bad'.
  Property 'reason' does not exist on type '{ status: string; id: string; }'.
```

```typescript
// ✅ RIGHT: literal types
type Good = { status: "failed"; reason: string } | { status: "paid"; id: string }; // literal tags
function g(b: Good): string {
  if (b.status === "failed") return b.reason; // narrowed
  return b.id; // narrowed to paid
}
console.log(g({ status: "paid", id: "p1" }));
```

**Mistake 2: Reading a field that exists on only one member.**

```typescript
// ❌ WRONG: accessing .paymentId without checking status
type R = { status: "success"; paymentId: string } | { status: "failed"; reason: string };
function id(r: R): string {
  return r.paymentId; // ❌ error
}
```

Real compiler output:

```
error TS2339: Property 'paymentId' does not exist on type 'R'.
  Property 'paymentId' does not exist on type '{ status: "failed"; reason: string; }'.
```

**Mistake 3: Using optional fields instead of a union (impossible states).**

```typescript
// ❌ BAD DESIGN: compiles, but allows { status: "success", reason: "x" } and { status: "failed" } without reason
type Loose = { status: "success" | "failed"; paymentId?: string; reason?: string };
const impossible: Loose = { status: "success", reason: "declined" }; // accepted silently!
console.log(impossible);
// ✅ Use the discriminated union instead, so this value would be a compile error.
```

---

## 🧠 Tricky Interview Question

**Q: Why does this fail to narrow, and why does it compile after `as const` or a literal annotation?**

```typescript
type Shape = { kind: "circle"; r: number } | { kind: "square"; side: number }; // union
function area(s: Shape): number { return s.kind === "circle" ? s.r ** 2 * 3 : s.side ** 2; } // uses tag

let kind = "circle"; // widened to string
const bad = { kind, r: 2 }; // kind: string
// ❌ area(bad);
const good = { kind: "circle", r: 2 } as const; // kind: "circle"
console.log(area(good)); // works
```

Real compiler output for the commented-out `area(bad)` call (uncommented):

```
error TS2345: Argument of type '{ kind: string; r: number; }' is not assignable to parameter of type 'Shape'.
  Type '{ kind: string; r: number; }' is not assignable to type '{ kind: "circle"; r: number; }'.
    Types of property 'kind' are incompatible.
      Type 'string' is not assignable to type '"circle"'.
```

Output of the `good` call with `npx tsx`:

```
12
```

**Answer:** A `let`/mutable object property widens a string literal to `string`, so the literal discriminant is lost. `as const` (or typing the variable as `Shape`) keeps the literal. This is exactly why Redux action creators use `as const` or typed action creators.

---

## ⚫ Interview Questions + Answers

Q1: What three ingredients make a discriminated union?
A1: A union of object types, a common property in all members, and a unique literal type for that property in each member.

Q2: Which discriminant types are allowed?
A2: Any unit/literal type: string, number, boolean literals, `null`, `undefined`, enums members. Plain `string` does not discriminate.

Q3: Discriminated union vs optional fields?
A3: Unions encode which fields co-exist, eliminating impossible states and removing `!`/`?.`. Optional fields compile but allow invalid combinations.

Q4: How do you get exhaustiveness checking?
A4: In the `default` branch assign the value to `never` (or call `assertNever`). Adding a new member then produces a compile error in every `switch` that forgot it.

Q5: How do you pull one member out of the union?
A5: `Extract<Union, { status: "success" }>`, or `Union & { status: "success" }`; the reverse is `Exclude`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Modeling request state, payment/order status, Redux actions, API responses, parser tokens
- Different cases carry different data
- You want compile-time exhaustiveness

❌ Avoid when:
- All variants have the same shape (use a plain literal union for the status field)
- You get data from outside without validating: validate with Zod first (a discriminated union is only as true as the data)
- A class hierarchy with polymorphism is truly better

---

## 📊 Visual Diagram
```
type PaymentResult = A | B | C
 A = { status: "success"; paymentId }
 B = { status: "failed";  reason }
 C = { status: "pending"; retryAfterSec }

 switch (r.status)
   "success" ──► r is A  (paymentId ✅, reason ❌)
   "failed"  ──► r is B  (reason ✅)
   "pending" ──► r is C  (retryAfterSec ✅)
   default   ──► r is never  → exhaustiveness proof
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Discriminant | Shared literal-typed tag property | साझा literal tag property |
| Tagged union | Another name for it | इसका दूसरा नाम |
| Literal type | Exact value as type (`"paid"`) | Exact value वाला type |
| Exhaustiveness | Compiler proves all cases handled | सब cases handled होने का प्रमाण |
| Illegal state | Combination that should not exist | ऐसी state जो नहीं होनी चाहिए |

---

## ⚡ 3-Line Summary
English:
1. Give every union member a shared literal tag so checking it narrows to one member.
2. This replaces optional-field soup and makes impossible states unrepresentable.
3. Keep tags literal (`as const`), and end `switch` with a `never` check.

Hindi:
1. हर union member को साझा literal tag दो ताकि check करने पर एक member तक narrow हो।
2. यह optional-field की गड़बड़ी हटाता है और असंभव states को बनने नहीं देता।
3. Tags literal रखो (`as const`) और `switch` के अंत में `never` check लगाओ।

---

## ➡️ Next Topic
**27. User-defined Type Guards (x is T)** — your own functions that teach the compiler a narrowing it cannot see itself.
