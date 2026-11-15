# 27. User-defined Type Guards (x is T)
# हिंदी में: User-defined Type Guards (अपने खुद के narrowing functions)

> Verified with TypeScript 5.x (5.9) under `tsc --strict`. `x is T` has existed since TS 1.x; `in`-based inference and inferred predicates (TS 5.5) reduce the need for it.

---

## 🔵 Simple Definition (English)
A **type guard** is a function whose return type is a **type predicate** `param is Type`. When it returns `true`, TypeScript narrows the argument to `Type` in the calling `if`; when `false`, it narrows to the remaining members. It lets you teach the compiler a check it cannot understand by itself.

## 🔵 सरल परिभाषा (Hindi)
**Type guard** ऐसा function है जिसका return type एक **type predicate** `param is Type` होता है। जब वह `true` लौटाता है तो calling `if` में argument `Type` तक narrow हो जाता है; `false` पर बचे हुए members तक। इससे आप compiler को वह check सिखा सकते हैं जो वह खुद नहीं समझ पाता।

---

## 🔴 Problem it Solves
`JSON.parse`, `req.body`, webhooks and `unknown` values are not narrowed by `typeof` alone when the check is "does this object have the right shape?". Writing `as Order` is a lie. A guard centralises the check, gives the compiler the proof, and gets reused everywhere.

## 🔴 यह क्यों बना? (Hindi)
`JSON.parse`, `req.body`, webhooks और `unknown` values का सवाल "क्या इस object की shape सही है?" होता है, जिसे अकेला `typeof` narrow नहीं कर पाता। `as Order` लिखना झूठ है। Guard check को एक जगह रखता है, compiler को proof देता है और हर जगह reuse होता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Write a function returning `boolean`, e.g. `function isOrder(x: unknown): boolean`.
Step 2 → Change the return type to a predicate: `x is Order`.
Step 3 → Inside, perform real runtime checks (`typeof`, `in`, `Array.isArray`). TypeScript does NOT verify them.
Step 4 → At the call site `if (isOrder(v)) { v }` narrows `v` to `Order`; the else branch excludes `Order`.
Step 5 → Works with `.filter(isOrder)` to turn `(Order | null)[]` into `Order[]`.
Step 6 → For methods use `this is T`. For asserting variants use `asserts x is T` (next note).
Step 7 → A wrong guard is a lie the compiler trusts: if the runtime check is weak, you get unsound code.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → `boolean` लौटाने वाला function लिखो, जैसे `function isOrder(x: unknown): boolean`।
Step 2 → Return type को predicate बना दो: `x is Order`।
Step 3 → अंदर असली runtime checks लिखो (`typeof`, `in`, `Array.isArray`)। TypeScript इन्हें verify नहीं करता।
Step 4 → Call site पर `if (isOrder(v)) { v }` में `v` `Order` बन जाता है; else में `Order` हट जाता है।
Step 5 → `.filter(isOrder)` के साथ `(Order | null)[]` को `Order[]` बनाया जा सकता है।
Step 6 → Methods के लिए `this is T`। Asserting version के लिए `asserts x is T` (अगला note)।
Step 7 → गलत guard compiler के भरोसे वाला झूठ है: runtime check कमज़ोर हो तो code unsound हो जाता है।

---

## 🟡 Real World Example
**Razorpay webhook** arrives as raw JSON. A guard `isPaymentCaptured(body)` checks `event === "payment.captured"` and `payload.payment.entity.id` is a string. After the guard, the handler reads `body.payload...` with full types and no casts.

## 🟡 Real Example Hindi mein
**Razorpay webhook** raw JSON में आता है। Guard `isPaymentCaptured(body)` देखता है कि `event === "payment.captured"` है और `payload.payment.entity.id` string है। Guard के बाद handler `body.payload...` को पूरे types के साथ पढ़ता है, बिना cast के।

---

## 💻 Code Example — Basic

```typescript
// Target shape
interface Order {
  id: string; // order id
  total: number; // amount in rupees
}

// Type predicate: 'x is Order' promises the compiler the check proves Order
function isOrder(x: unknown): x is Order {
  // must be a non-null object first
  if (typeof x !== "object" || x === null) return false; // not an object
  // look at fields through a loose record type
  const o = x as Record<string, unknown>; // safe: we only READ and check each field
  return typeof o.id === "string" && typeof o.total === "number"; // field checks
}

const input: unknown = JSON.parse('{"id":"o1","total":499}'); // unknown from outside
if (isOrder(input)) {
  console.log(input.id, input.total + 1); // narrowed: input is Order
} else {
  console.log("invalid"); // input stays unknown here
}
```

Run with `npx tsx`:

```
o1 500
```

## 💻 Code Example — Advanced

```typescript
// Advanced: guards with generics, filter, class hierarchies, and this-guards

type Maybe<T> = T | null | undefined; // optional value alias

// Generic guard: removes null and undefined for any T
function isPresent<T>(x: Maybe<T>): x is T {
  return x !== null && x !== undefined; // keeps 0 and "" (unlike truthiness)
}

const raw: Maybe<number>[] = [10, null, 0, undefined, 5]; // mixed array
const nums: number[] = raw.filter(isPresent); // typed number[], 0 is kept
console.log(nums); // [10, 0, 5]

// Guard for a discriminated payload (webhook event)
type Captured = { event: "payment.captured"; id: string; amount: number }; // success event
type Failed = { event: "payment.failed"; id: string; reason: string }; // failure event
type Webhook = Captured | Failed; // union

const isCaptured = (w: Webhook): w is Captured => w.event === "payment.captured"; // arrow guard

const events: Webhook[] = [
  { event: "payment.captured", id: "p1", amount: 500 }, // ok
  { event: "payment.failed", id: "p2", reason: "bank" }, // not ok
];
const total = events.filter(isCaptured).reduce((s, e) => s + e.amount, 0); // e: Captured
console.log(total); // 500

// Guard on a class: instanceof wrapped in a predicate (reusable across modules)
class HttpError extends Error { constructor(public status: number, msg: string) { super(msg); } } // error with status
function isHttpError(e: unknown): e is HttpError { return e instanceof HttpError; } // wrapper

// 'this is T' guard method on a class hierarchy
class Shape { isCircle(): this is Circle { return this instanceof Circle; } } // base with this-guard
class Circle extends Shape { constructor(public r: number) { super(); } } // subclass
const s: Shape = new Circle(3); // static type Shape
if (s.isCircle()) console.log(s.r); // narrowed to Circle -> 3

try { throw new HttpError(404, "missing"); } catch (e) { console.log(isHttpError(e) ? e.status : 0); } // 404
```

Run with `npx tsx`:

```
[ 10, 0, 5 ]
500
3
404
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: validate webhook body with a guard instead of 'as'
import express from "express"; // express
import type { Request, Response } from "express"; // types

interface PaymentWebhook { event: string; payload: { id: string; amount: number } } // expected body

// Guard with real checks on nested data
function isPaymentWebhook(b: unknown): b is PaymentWebhook {
  if (typeof b !== "object" || b === null) return false; // object check
  const r = b as { event?: unknown; payload?: unknown }; // read-only peek
  if (typeof r.event !== "string") return false; // event must be a string
  if (typeof r.payload !== "object" || r.payload === null) return false; // payload object
  const p = r.payload as { id?: unknown; amount?: unknown }; // peek payload
  return typeof p.id === "string" && typeof p.amount === "number"; // leaf checks
}

const app = express(); // app
app.use(express.json()); // body parser, req.body is 'any'

app.post("/webhook", (req: Request, res: Response) => {
  const body: unknown = req.body; // treat as unknown on purpose
  if (!isPaymentWebhook(body)) { res.status(400).json({ error: "bad webhook" }); return; } // reject
  res.json({ ok: true, id: body.payload.id }); // body: PaymentWebhook
});
```

```tsx
// React: guard used on API data before rendering
import type { ReactNode } from "react"; // type

type Item = { sku: string; price: number }; // expected item

function isItem(x: unknown): x is Item {
  return typeof x === "object" && x !== null && "sku" in x && "price" in x; // 'in' narrows to object & {sku, price}
}

export function Row({ data }: { data: unknown }): ReactNode {
  if (!isItem(data)) return <span>Invalid row</span>; // data: unknown
  return <span>{data.sku}: Rs {data.price}</span>; // data: Item
}
```

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: A guard that lies (the compiler trusts you).**

```typescript
// ❌ WRONG: only checks it is an object, but claims it is an Order
interface Order { id: string; total: number } // target
function isOrderBad(x: unknown): x is Order { return typeof x === "object"; } // weak check

const v: unknown = {}; // actually no fields
if (isOrderBad(v)) console.log(v.total.toFixed(2)); // compiles, crashes at runtime
```

Real output of `npx tsx` on this block:

```
TypeError: Cannot read properties of undefined (reading 'toFixed')
```

**Mistake 2: Forgetting the predicate (returns plain boolean, no narrowing).**

```typescript
// ❌ WRONG: return type 'boolean' gives no narrowing
function isString(x: unknown): boolean { return typeof x === "string"; } // no predicate
function use(x: unknown): number {
  if (isString(x)) return x.length; // ❌ x is still unknown
  return 0;
}
```

Real compiler output:

```
error TS18046: 'x' is of type 'unknown'.
```

**Mistake 3: Predicate type not assignable to the parameter type.**

```typescript
// ❌ WRONG: predicate type must be assignable to the parameter's type
function isNum(x: string): x is number { return typeof x === "number"; } // ❌ error
```

Real compiler output:

```
error TS2677: A type predicate's type must be assignable to its parameter's type.
  Type 'number' is not assignable to type 'string'.
```

---

## 🧠 Tricky Interview Question

**Q: A guard returns `false`. What does TypeScript assume about the "else" branch, and how can this bite you?**

```typescript
// Guard that is only "one-directional": false does NOT mean "not a string"
function isLongString(x: string | number): x is string { return typeof x === "string" && x.length > 3; } // too narrow

function demo(x: string | number): string {
  if (isLongString(x)) return "long:" + x.length; // x: string
  // TS believes x is number here, but "ab" is a short string!
  const n: number = x; // compiles because of the lie
  return typeof n; // runtime value is really a string
}
console.log(demo("ab")); // runtime reveals the lie: typeof "ab"
```

Real output with `npx tsx`:

```
string
```

**Answer:** A predicate `x is string` tells TypeScript that `false` means "x is NOT string". So in the else branch TS narrows `x` to `number` even though `"ab"` is a string. A guard must be **exact in both directions** (true iff the type matches). Use a normal boolean for extra conditions like length.

---

## ⚫ Interview Questions + Answers

Q1: What is a type predicate and where is it written?
A1: `param is Type` as the return type of a function taking that param. A `true` return narrows the argument to `Type` at the call site.

Q2: Does TypeScript verify that the guard body is correct?
A2: No. It only checks the predicate type is assignable to the parameter type. The body is your responsibility, so a wrong guard makes unsound code.

Q3: How do guards relate to `.filter()`?
A3: `filter` has an overload accepting a predicate `(x): x is S`, returning `S[]`. TS 5.5 also infers predicates for simple arrows like `x => x !== null`.

Q4: Type guard vs `as` cast?
A4: A cast silences the compiler with no runtime check. A guard performs a runtime check AND informs the compiler, so it is both safe and reusable.

Q5: Guard vs Zod schema?
A5: For deep or large shapes use Zod `safeParse` (it returns a typed result and validates every field). Handwritten guards are fine for small shapes, and Zod can generate guards too.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Narrowing `unknown` from JSON, webhooks or `catch`
- Filtering arrays of nullable values or variant members
- A check is used in many places and needs one name

❌ Avoid when:
- A discriminant `switch` already narrows (simpler, compiler-proven)
- The shape is large or nested: use Zod
- You cannot guarantee the guard is exact in both directions

---

## 📊 Visual Diagram
```
function isOrder(x: unknown): x is Order { ...runtime checks... }
                                 ▲
                                 └── promise to the compiler

 unknown v
    │ if (isOrder(v))
    ├── true  ──► v: Order
    └── false ──► v: unknown (minus Order)

 ⚠ compiler trusts the predicate; it never checks the body
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Type predicate | `x is T` return annotation | `x is T` वाला return type |
| Type guard | Function using a predicate | Predicate वाला function |
| Unsound guard | Check weaker than its claim | दावे से कमज़ोर check |
| this-guard | `this is T` on methods | Methods पर `this is T` |
| Inferred predicate | Auto guard (TS 5.5+) | अपने आप बना guard (TS 5.5+) |

---

## ⚡ 3-Line Summary
English:
1. `x is T` turns a boolean function into a narrowing guard.
2. The compiler trusts it blindly, so the guard must be exact both ways.
3. Use for `unknown`, filters and webhooks; use Zod for big shapes.

Hindi:
1. `x is T` boolean function को narrowing guard बना देता है।
2. Compiler इस पर आँख बंद करके भरोसा करता है, इसलिए guard दोनों दिशाओं में exact होना चाहिए।
3. `unknown`, filters और webhooks के लिए इस्तेमाल करो; बड़ी shapes के लिए Zod।

---

## ➡️ Next Topic
**28. Assertion Functions (asserts x)** — guards that throw instead of returning false, narrowing the code that follows.
