# 10. Union Types
# हिंदी में: Union Types (`A | B` — "इनमें से कोई एक")

> Version note: **TypeScript 5.x** (5.9.3 पर verify)। Narrowing के नियम 4.x से काफ़ी बेहतर हुए हैं (5.5 inferred predicates, 5.3 `switch(true)` narrowing)।

---

## 🔵 Simple Definition (English)
A **union type** `A | B` means "a value that is **either** `A` **or** `B`". You can only use members that are **common to every** alternative, until you **narrow** the union with a check (`typeof`, `in`, `===`, a discriminant property). Unions are how TypeScript models "one of several possibilities": `string | number`, `"PLACED" | "DELIVERED"`, `User | null`, `Success | Failure`.

## 🔵 सरल परिभाषा (Hindi)
**Union type** `A | B` का मतलब है "ऐसी value जो `A` **या** `B` है"। जब तक आप `typeof`, `in`, `===` या किसी discriminant property से union को **narrow** न कर दें, तब तक सिर्फ़ वही members इस्तेमाल हो सकते हैं जो **हर विकल्प में common** हों। Union से TypeScript "कई संभावनाओं में से एक" को मॉडल करता है: `string | number`, `"PLACED" | "DELIVERED"`, `User | null`, `Success | Failure`।

---

## 🔴 Problem it Solves
Real data is rarely one thing. An API returns `{ data }` **or** `{ error }`; a cart ID is a `string` for guests and a `number` for logged-in users; a status is one of five strings; a DB column is `string | null`. In JS you handle this with comments and hope. With unions the compiler **forces you to handle every case**: you cannot read `.error` without checking, you cannot pass `"SHIPED"` (typo) as a status, and when someone adds a new variant, every `switch` that forgot it fails to compile.

## 🔴 यह क्यों बना? (Hindi)
असली data शायद ही कभी एक ही चीज़ होता है। API `{ data }` **या** `{ error }` देती है; cart ID guest के लिए `string` और logged-in user के लिए `number` हो सकती है; status पाँच strings में से एक होता है; DB column `string | null` होता है। JS में आप इसे comments और उम्मीद से संभालते हैं। Unions में compiler **हर case handle करवाता है**: बिना check किए `.error` नहीं पढ़ सकते, `"SHIPED"` (typo) status के रूप में नहीं दे सकते, और कोई नया variant जुड़ते ही जिस `switch` ने उसे नहीं संभाला वह compile नहीं होगा।

---

## 🟢 How it Works — Step by Step

Step 1 → Write alternatives separated by `|`: `type Id = string | number`. A leading `|` is allowed for multi-line unions.
Step 2 → **Assignability:** a value of type `A` is assignable to `A | B` (widening into the union is free). The reverse is not: `A | B` → `A` needs narrowing.
Step 3 → **Only common members are usable:** `(string | number).toString()` works (both have it); `.toUpperCase()` does not (only string has it).
Step 4 → **Narrowing** removes members: `typeof x === "string"`, `x instanceof Date`, `"error" in res`, `x === null`, `Array.isArray(x)`, truthiness, or comparing a **discriminant** property.
Step 5 → **Literal unions** model enums: `"PLACED" | "PACKED" | "DELIVERED"`. They are erased at runtime (no enum object) and work with `as const` arrays (topic 007).
Step 6 → **Discriminated unions:** every member has a shared literal property (`kind`/`type`/`status`) → `switch` on it narrows perfectly (topic 026) and pairs with `never` for exhaustiveness (topic 029).
Step 7 → **Distribution & simplification:** `string | "a"` collapses to `string`; `T | never` is `T`; `boolean` is really `true | false`; `keyof` of a union gives only the **common** keys.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → विकल्प `|` से अलग करके लिखो: `type Id = string | number`। कई lines के union में शुरुआत में भी `|` लगा सकते हैं।
Step 2 → **Assignability:** `A` type की value `A | B` में assign हो सकती है। उल्टा नहीं: `A | B` → `A` के लिए narrowing चाहिए।
Step 3 → **सिर्फ़ common members चलते हैं:** `(string | number).toString()` चलता है (दोनों में है); `.toUpperCase()` नहीं (सिर्फ़ string में है)।
Step 4 → **Narrowing** members हटाती है: `typeof x === "string"`, `x instanceof Date`, `"error" in res`, `x === null`, `Array.isArray(x)`, truthiness, या **discriminant** property की तुलना।
Step 5 → **Literal unions** enums की जगह: `"PLACED" | "PACKED" | "DELIVERED"`। Runtime पर ये हट जाते हैं (कोई enum object नहीं) और `as const` arrays के साथ चलते हैं (topic 007)।
Step 6 → **Discriminated unions:** हर member में एक साझा literal property (`kind`/`type`/`status`) → उस पर `switch` एकदम सही narrow करता है (topic 026) और `never` के साथ exhaustiveness (topic 029)।
Step 7 → **Simplification:** `string | "a"` सिकुड़कर `string`; `T | never` = `T`; `boolean` असल में `true | false` है; union का `keyof` सिर्फ़ **common** keys देता है।

---

## 🟡 Real World Example
**Razorpay payment result:** `type PaymentResult = { status: "captured"; paymentId: string; amountPaise: number } | { status: "failed"; code: string; description: string } | { status: "pending"; retryAfterSec: number }`. The React screen does `switch (result.status)`: `captured` shows the receipt, `failed` shows `result.description`, `pending` starts a timer using `result.retryAfterSec`. Accessing `result.paymentId` without first checking `status` is a compile error. A DB column `couponCode NVARCHAR(20) NULL` becomes `string | null` in the row type.

## 🟡 Real Example Hindi mein
**Razorpay payment result:** `type PaymentResult = { status: "captured"; paymentId: string; amountPaise: number } | { status: "failed"; code: string; description: string } | { status: "pending"; retryAfterSec: number }`। React screen `switch (result.status)` करती है: `captured` पर receipt, `failed` पर `result.description`, `pending` पर `result.retryAfterSec` से timer। बिना `status` check किए `result.paymentId` पढ़ना compile error है। DB column `couponCode NVARCHAR(20) NULL` row type में `string | null` बन जाता है।

---

## 💻 Code Example — Basic

```typescript
// union-basic.ts

// A value that can be a number (logged-in user id) or a string (guest session id)
type CartId = string | number;

function describe(id: CartId): string {
  // Only members common to both types are allowed before narrowing
  if (typeof id === "string") {
    return `guest:${id.toUpperCase()}`;      // narrowed to string here
  }
  return `user:${id.toFixed(0)}`;            // narrowed to number here
}
console.log(describe("abc"), describe(42));  // guest:ABC user:42

// Literal union: a mini-enum with no runtime cost
type Status = "PLACED" | "PACKED" | "DELIVERED";
function isFinal(s: Status): boolean {
  return s === "DELIVERED";                  // comparison against a literal also narrows
}
console.log(isFinal("PLACED"), isFinal("DELIVERED")); // false true

// Nullable: string | null (DB column that may be NULL)
function couponLabel(code: string | null): string {
  return code ?? "NO COUPON";                // ?? handles null/undefined
}
console.log(couponLabel(null), couponLabel("WELCOME")); // NO COUPON WELCOME

// Union of arrays vs array of union: different things
const a: string[] | number[] = [1, 2];       // either ALL strings or ALL numbers
const b: (string | number)[] = [1, "x"];     // each element may differ
console.log(a.length, b.length);             // 2 2

// Output:
// guest:ABC user:42
// false true
// NO COUPON WELCOME
// 2 2
```

```typescript
// ❌ intentional errors — real tsc 5.9 output
type CartId = string | number;
function bad(id: CartId) {
  return id.toUpperCase();
}
// error TS2339: Property 'toUpperCase' does not exist on type 'string | number'.
//   Property 'toUpperCase' does not exist on type 'number'.

type Status = "PLACED" | "PACKED" | "DELIVERED";
const s: Status = "SHIPED";
// error TS2322: Type '"SHIPED"' is not assignable to type 'Status'.

declare const maybe: string | null;
maybe.length;
// error TS18047: 'maybe' is possibly 'null'.
```

## 💻 Code Example — Advanced

```typescript
// union-advanced.ts — discriminated union, `in` narrowing, exhaustiveness, API result type

// 1) Discriminated union: `status` is the discriminant (literal type in every member)
type PaymentResult =
  | { status: "captured"; paymentId: string; amountPaise: number }
  | { status: "failed"; code: string; description: string }
  | { status: "pending"; retryAfterSec: number };

function assertNever(x: never): never {
  throw new Error(`unhandled: ${JSON.stringify(x)}`);        // compile-time + runtime guard
}

function render(r: PaymentResult): string {
  switch (r.status) {                                        // narrows r in each case
    case "captured": return `Paid Rs ${r.amountPaise / 100} (${r.paymentId})`;
    case "failed":   return `Failed: ${r.description}`;
    case "pending":  return `Retry in ${r.retryAfterSec}s`;
    default:         return assertNever(r);                  // add a 4th status -> compile error here
  }
}
console.log(render({ status: "captured", paymentId: "pay_1", amountPaise: 49950 }));
console.log(render({ status: "pending", retryAfterSec: 5 }));

// 2) `in` operator narrows unions of object types that have no discriminant
type Ok = { data: string[] };
type Err = { error: string };
function unwrap(res: Ok | Err): string {
  if ("error" in res) return `ERR ${res.error}`;             // res: Err
  return `OK ${res.data.join(",")}`;                         // res: Ok
}
console.log(unwrap({ data: ["a", "b"] }), unwrap({ error: "boom" }));

// 3) Generic Result<T,E> union — the Rust-style pattern for typed error handling
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };
function parseQty(s: string): Result<number, string> {
  const n = Number(s);
  return Number.isInteger(n) && n > 0 ? { ok: true, value: n } : { ok: false, error: `bad qty: ${s}` };
}
const r1 = parseQty("3");
if (r1.ok) console.log(r1.value * 2);                        // 6  (r1: ok variant)
else console.log(r1.error);

// 4) Union of function types and calling it: parameters are INTERSECTED
type Handler = ((id: string) => void) | ((id: number) => void);
declare const h: Handler;
// h("a") would be an error: parameter must satisfy string & number => never

// 5) Extract members of a union (preview of utility types, topic 055)
type CapturedOnly = Extract<PaymentResult, { status: "captured" }>;   // the captured member
const c: CapturedOnly = { status: "captured", paymentId: "p", amountPaise: 1 };
console.log(c.paymentId);                                    // p

// Output:
// Paid Rs 499.5 (pay_1)
// Retry in 5s
// OK a,b ERR boom
// 6
// p
```

---

## 🟠 Node/Express + React Integration

**Express — a union response type for one endpoint:**

```typescript
// union-express.ts
import express, { Response } from "express";

type OrderOk = { ok: true; orderId: string; totalPaise: number };
type OrderFail = { ok: false; error: string };
type OrderResponse = OrderOk | OrderFail;               // both shapes the client may receive

const app = express();
app.use(express.json());

app.post("/orders", (req, res: Response<OrderResponse>) => {
  const qty = Number(req.body?.qty);                    // body is any -> convert to number
  if (!Number.isInteger(qty) || qty < 1) {
    res.status(400).json({ ok: false, error: "qty must be a positive integer" });
    return;
  }
  res.status(201).json({ ok: true, orderId: "SW-1", totalPaise: qty * 19900 });
});
export type { OrderResponse };                           // share with the frontend
export default app;
```

**React — consume the union: the `ok` flag narrows safely:**

```tsx
// OrderResult.tsx
import type { OrderResponse } from "./union-express";

export function OrderResult({ res }: { res: OrderResponse }) {
  if (!res.ok) return <p role="alert">{res.error}</p>;            // res: OrderFail
  return <p>Order {res.orderId}: Rs {res.totalPaise / 100}</p>;   // res: OrderOk
}
```
**Redux Toolkit:** model async state as a union instead of booleans: `type LoadState<T> = { status: "idle" } | { status: "loading" } | { status: "ok"; data: T } | { status: "error"; message: string }` — impossible states like `loading && error` simply cannot be constructed. **SQL Server:** nullable columns map to `T | null`; `mssql` returns `null`, not `undefined`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Modelling state with optional fields instead of a union
```typescript
// ⚠️ Wrong — allows impossible states ({ loading: true, error: "x", data: [...] })
type State = { loading: boolean; data?: string[]; error?: string };

// ✅ Right — each state is a distinct member
type State2 =
  | { status: "loading" }
  | { status: "ok"; data: string[] }
  | { status: "error"; error: string };
const s: State2 = { status: "ok", data: ["a"] };
console.log(s.status);
```

❌ Mistake 2: Using `string` where a literal union is meant
```typescript
// ⚠️ Wrong — any typo is accepted
function setStatus(s: string) { return s; }
// ✅ Right — compiler lists valid values and catches typos
function setStatus2(s: "PLACED" | "PACKED") { return s; }
console.log(setStatus2("PLACED"));
```

❌ Mistake 3: Calling a method that exists on only one member (shown above, `TS2339`). Narrow first.

❌ Mistake 4: Believing `A | B` with objects means "has props of both". That is **intersection** (`A & B`, topic 011). A union value has only the props it's *guaranteed* to have.
```typescript
// ❌ real compiler output
type Cash = { method: "cash" };
type Card = { method: "card"; last4: string };
declare const p: Cash | Card;
console.log(p.last4);
// error TS2339: Property 'last4' does not exist on type 'Cash | Card'.
//   Property 'last4' does not exist on type 'Cash'.
```

---

## 🧠 Tricky Interview Question

```typescript
type A = { id: number } | { name: string };
const x: A = { id: 1, name: "Aditya" };   // compiles?
function f(v: A) { return v.id; }          // compiles?
```
**Question:** Does each line compile?

**Answer:** Line 1 **compiles**. A union of *non-discriminated* object types allows an object that satisfies *either* member, and for object **literals** TypeScript only runs the excess-property check against the **combined** known keys of the union, so `{ id, name }` is allowed. Line 2 **fails**: `id` exists only on one member so `v.id` is not accessible without narrowing (`"id" in v`). This shows two facts: unions are "at least one", not "exactly one" (use `never`-optional keys, or a discriminant, to make members exclusive), and property access needs narrowing.

```typescript
// verified
type A = { id: number } | { name: string };
const x: A = { id: 1, name: "Aditya" };   // compiles
function f(v: A) { return v.id; }          // ❌
// error TS2339: Property 'id' does not exist on type 'A'.
//   Property 'id' does not exist on type '{ name: string; }'.
```

---

## ⚫ Interview Questions + Answers

Q1: What can you do with a value of type `string | number` without narrowing?
A1: Only operations valid for both: `toString()`, `valueOf()`, `===` comparison, passing to `unknown`. To use `toUpperCase()` or arithmetic you must narrow with `typeof` (or a type guard).

Q2: What is a discriminated union and why is it preferred?
A2: A union whose members share a property with distinct literal types (`kind: "a" | "b"`). Checking that property narrows the whole object, enabling exhaustive `switch`es and eliminating impossible states. It is the idiomatic way to model results, state machines and Redux actions.

Q3: Union vs enum — when do you choose each?
A3: Literal unions have zero runtime footprint, work naturally with JSON, and need no import. Enums (topic 016) give a runtime object, reverse mapping (numeric) and iteration, but add emitted code and break with `erasableSyntaxOnly`. Most modern codebases use `as const` arrays + literal unions.

Q4: How do union and intersection types differ?
A4: `A | B` = either A or B (you know less); `A & B` = both at once (you know more). Unions *widen* the set of accepted values; intersections *narrow* it. A function accepting `A | B` can take either; one accepting `A & B` needs an object satisfying both.

Q5: Why does `Array<string | number>` differ from `string[] | number[]`?
A5: The first is one array whose elements may mix types; the second is *either* an all-string array *or* an all-number array. Methods like `map` on the second are awkward (callbacks are unioned before TS 5.2; improved since) — often prefer the first.

---

## 🔷 When to Use + When Not to Use
✅ Use unions for: API results (`Ok | Err`), statuses/roles/modes (literal unions), nullable values (`T | null`), Redux actions / state machines (discriminated), function params accepting alternatives.

❌ Avoid: huge unions of 50+ members (slow, noisy errors), unions of object types without a discriminant (hard to narrow), and optional-field "bags" where a union of states would forbid invalid combinations.

---

## 📊 Visual Diagram
```
 type PaymentResult =
   │
   ├── { status:"captured"; paymentId; amountPaise }
   ├── { status:"failed";   code; description }
   └── { status:"pending";  retryAfterSec }

 value r: PaymentResult
        │  r.paymentId   → ❌ (not on every member)
        ▼
  switch (r.status)  ──"captured"──► r.paymentId ✅
                     ──"failed"────► r.description ✅
                     ──"pending"───► r.retryAfterSec ✅
                     ──default─────► r : never   (exhaustive!)

  A | B   =  A ∪ B   ("one of")      A & B = A ∩ B ("all of")
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Union type | Value is one of several types | Value कई types में से एक |
| Narrowing | Refine union via checks | Checks से union को छोटा करना |
| Literal union | Union of exact values | Exact values का union |
| Discriminant | Shared literal prop that tells the member | Member पहचानने वाली साझा literal property |
| Discriminated union | Union with a discriminant | Discriminant वाला union |
| Nullable | `T | null` | `T | null` वाला type |
| Exhaustiveness | Every member handled | हर member संभाला गया |

---

## ⚡ 3-Line Summary
English:
1. `A | B` means one of several types; before narrowing you may only use what all members share.
2. Narrow with `typeof`, `in`, `===` or a discriminant property; use `never` for exhaustive `switch`.
3. Prefer unions of states/literals over optional-field bags or enums — impossible states stop compiling.

Hindi:
1. `A | B` का मतलब कई types में से एक; narrow करने से पहले सिर्फ़ वही इस्तेमाल करो जो सब members में साझा हो।
2. `typeof`, `in`, `===` या discriminant property से narrow करो; exhaustive `switch` के लिए `never` इस्तेमाल करो।
3. Optional-field bags या enums की जगह states/literals के unions चुनो — असंभव states compile ही नहीं होंगे।

---

## ➡️ Next Topic
**011. Intersection Types** — `A & B`, combining object types and the traps of conflicting properties.
