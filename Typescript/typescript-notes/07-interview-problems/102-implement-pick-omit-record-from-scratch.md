# 102. Implement Pick, Omit, Record from Scratch
# हिंदी में: Pick, Omit, Record को शुरू से बनाना

> Verified with **TypeScript 5.9.3** (`--strict`). All of this works on **TS 4.x and 5.x**; the key-remapping variant (`as` clause) needs **TS 4.1+**.

---

## 🔵 Simple Definition (English)
`Pick<T, K>`, `Omit<T, K>` and `Record<K, V>` are built-in **utility types** you use daily. Interviewers ask "implement them yourself" because each one needs a different core idea: **`Pick`** = a **mapped type over a constrained key union**, **`Omit`** = `Pick` + **`Exclude`** (remove keys from the union), **`Record`** = a mapped type over **any key union** with one fixed value type.

## 🔵 सरल परिभाषा (Hindi)
`Pick<T, K>`, `Omit<T, K>` और `Record<K, V>` रोज़ इस्तेमाल होने वाले built-in **utility types** हैं। Interviewer "इन्हें खुद implement करो" इसलिए पूछते हैं क्योंकि हर एक में अलग core idea है: **`Pick`** = **constrained key union पर mapped type**, **`Omit`** = `Pick` + **`Exclude`** (union से keys हटाना), **`Record`** = **किसी भी key union पर mapped type** जिसमें value type fixed है।

---

## 🔴 Problem it Solves
Without these helpers you copy-paste near-identical interfaces: `Order`, `CreateOrderDto` (no `id`), `OrderSummary` (just 3 fields), `StatusCounts` (one number per status). When `Order` gains a field, the copies drift apart and bugs appear. Utility types **derive** one type from another so there is a single source of truth, and knowing how they work lets you write your own variants (`PickByValue`, `RequireKeys`) in an interview.

## 🔴 यह क्यों बना? (Hindi)
इन helpers के बिना आप लगभग एक जैसे interfaces copy-paste करते हो: `Order`, `CreateOrderDto` (बिना `id`), `OrderSummary` (सिर्फ 3 fields), `StatusCounts` (हर status का एक number)। `Order` में field जुड़ने पर copies अलग-अलग हो जाती हैं और bugs आते हैं। Utility types एक type से दूसरा **derive** करते हैं ताकि single source of truth रहे, और इनका internals जानने से आप interview में अपने variants (`PickByValue`, `RequireKeys`) लिख सकते हो।

---

## 🟢 How it Works — Step by Step

Step 1 → **Pick**: `type MyPick<T, K extends keyof T> = { [P in K]: T[P] }`. The constraint `K extends keyof T` makes unknown keys an error, and because `K` is constrained to `keyof T` the mapped type is **homomorphic**, so `?` and `readonly` are copied.
Step 2 → **Exclude**: `type MyExclude<T, U> = T extends U ? never : T` (a distributive conditional type, removes members from a union).
Step 3 → **Omit**: `type MyOmit<T, K extends keyof any> = MyPick<T, MyExclude<keyof T, K>>`. Note `keyof any` = `string | number | symbol`, so `Omit` is **lenient** about unknown keys (unlike `Pick`).
Step 4 → **Record**: `type MyRecord<K extends keyof any, V> = { [P in K]: V }`. `K` can be a union of literals (exact keys) or `string` (index signature).
Step 5 → Test with valid cases and with `// ❌` cases to see the real compiler errors.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Pick**: `type MyPick<T, K extends keyof T> = { [P in K]: T[P] }`। Constraint `K extends keyof T` unknown keys को error बनाता है, और `K` के `keyof T` तक constrained होने से mapped type **homomorphic** बनता है, इसलिए `?` और `readonly` copy होते हैं।
Step 2 → **Exclude**: `type MyExclude<T, U> = T extends U ? never : T` (distributive conditional type, union से members हटाता है)।
Step 3 → **Omit**: `type MyOmit<T, K extends keyof any> = MyPick<T, MyExclude<keyof T, K>>`। ध्यान दो `keyof any` = `string | number | symbol`, इसलिए `Omit` unknown keys पर **lenient** है (`Pick` के उलट)।
Step 4 → **Record**: `type MyRecord<K extends keyof any, V> = { [P in K]: V }`। `K` literals का union (exact keys) या `string` (index signature) हो सकता है।
Step 5 → Valid cases और `// ❌` cases से test करो ताकि असली compiler errors दिखें।

---

## 🟡 Real World Example
**Razorpay-style payments service**: the DB row type `PaymentRow` has 14 columns. The "list payments" API returns `Pick<PaymentRow, "id" | "amount" | "status">`. The "create payment" body is `Omit<PaymentRow, "id" | "createdAt">` because the server generates those. A dashboard counter is `Record<PaymentStatus, number>`, and the compiler forces you to list **every** status, so adding `"refunded"` to the union breaks the build until counters are updated.

## 🟡 Real Example Hindi mein
**Razorpay-style payments service**: DB row type `PaymentRow` में 14 columns हैं। "list payments" API `Pick<PaymentRow, "id" | "amount" | "status">` लौटाती है। "create payment" body `Omit<PaymentRow, "id" | "createdAt">` है क्योंकि ये server generate करता है। Dashboard counter `Record<PaymentStatus, number>` है, और compiler **हर** status लिखने को मजबूर करता है, इसलिए union में `"refunded"` जोड़ते ही counters update होने तक build टूटता है।

---

## 💻 Code Example — Basic

```typescript
// utility-from-scratch.ts — all three from scratch, checked against the built-ins
type MyPick<T, K extends keyof T> = { [P in K]: T[P] }; // loop only over the chosen keys
type MyExclude<T, U> = T extends U ? never : T; // remove union members assignable to U
type MyOmit<T, K extends keyof any> = MyPick<T, MyExclude<keyof T, K>>; // keep every key except K
type MyRecord<K extends keyof any, V> = { [P in K]: V }; // every key in K maps to V

interface Order { // sample domain type
  id: number; // server generated
  amount: number; // rupees
  status: "placed" | "paid" | "failed"; // lifecycle
  note?: string; // optional
}

type Summary = MyPick<Order, "id" | "amount">; // { id: number; amount: number }
type CreateDto = MyOmit<Order, "id">; // { amount: number; status: ...; note?: string }
type StatusCount = MyRecord<Order["status"], number>; // { placed: number; paid: number; failed: number }

const s: Summary = { id: 1, amount: 499 }; // ok
const d: CreateDto = { amount: 250, status: "placed" }; // note stays optional
const c: StatusCount = { placed: 3, paid: 10, failed: 1 }; // all three keys required
console.log(s, d, c); // prints { id: 1, amount: 499 } { amount: 250, status: 'placed' } { placed: 3, paid: 10, failed: 1 }

// Type-level equality check: our version must be identical to the built-in one
type Equal<A, B> = (<T>() => T extends A ? 1 : 2) extends (<T>() => T extends B ? 1 : 2) ? true : false; // strict equality
const ok1: Equal<MyPick<Order, "id">, Pick<Order, "id">> = true; // compiles only if identical
const ok2: Equal<MyOmit<Order, "id">, Omit<Order, "id">> = true; // compiles only if identical
console.log(ok1, ok2); // prints true true
```

```typescript
// pick-errors.ts — the constraint is the whole point
type MyPick<T, K extends keyof T> = { [P in K]: T[P] }; // Pick with constraint
interface Order { id: number; amount: number } // tiny domain type

// ❌ "foo" is not a key of Order, constraint K extends keyof T rejects it
type Bad = MyPick<Order, "foo">;
// error TS2344: Type '"foo"' does not satisfy the constraint 'keyof Order'.
```

## 💻 Code Example — Advanced

```typescript
// utility-advanced.ts — modifiers, key remapping, and your own variants
type MyPick<T, K extends keyof T> = { [P in K]: T[P] }; // standard Pick

interface Cart { readonly id: string; coupon?: string; total: number } // has readonly and optional

type P = MyPick<Cart, "id" | "coupon">; // { readonly id: string; coupon?: string } (modifiers preserved)
const p: P = { id: "c1" }; // coupon may be omitted, so homomorphism works
// p.id = "c2"; would be TS2540 because readonly was copied

// Omit via key remapping (TS 4.1+): single pass, no Exclude needed
type OmitAs<T, K extends PropertyKey> = { [P in keyof T as P extends K ? never : P]: T[P] }; // "as never" drops key
type NoId = OmitAs<Cart, "id">; // { coupon?: string; total: number }
const n: NoId = { total: 100 }; // fine

// PickByValue: pick keys whose VALUE type matches, a classic follow-up question
type PickByValue<T, V> = { [P in keyof T as T[P] extends V ? P : never]: T[P] }; // filter keys by value type
type NumericCart = PickByValue<{ id: string; total: number; tax: number }, number>; // { total: number; tax: number }
const nc: NumericCart = { total: 100, tax: 18 }; // ok

// RequireKeys: make some keys required again, the opposite of Partial for a subset
type RequireKeys<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>; // omit then re-add as required
type CouponCart = RequireKeys<Cart, "coupon">; // coupon is now mandatory
const cc: CouponCart = { id: "c1", coupon: "SAVE20", total: 80 }; // must include coupon
console.log(p, n, nc, cc); // prints { id: 'c1' } { total: 100 } { total: 100, tax: 18 } { id: 'c1', coupon: 'SAVE20', total: 80 }
```

```typescript
// record-exhaustive.ts — Record with a literal union forces exhaustiveness
type PaymentStatus = "created" | "captured" | "failed"; // all states
type MyRecord<K extends keyof any, V> = { [P in K]: V }; // from scratch

const labels: MyRecord<PaymentStatus, string> = { // every status must have a label
  created: "Pending", // label 1
  captured: "Paid", // label 2
  failed: "Failed", // label 3
};

// With plain string keys Record becomes an index signature
const prices: MyRecord<string, number> = { dosa: 80 }; // any string key allowed
prices.idli = 40; // adding keys is fine
console.log(labels.captured, Object.keys(prices)); // prints Paid [ 'dosa', 'idli' ]

// ❌ missing "failed"
const broken: MyRecord<PaymentStatus, string> = { created: "Pending", captured: "Paid" };
// error TS2741: Property 'failed' is missing in type '{ created: string; captured: string; }' but required in type 'MyRecord<PaymentStatus, string>'.
```

---

## 🟠 Node/Express + React Integration

```typescript
// payments-route.ts — Pick for responses, Omit for request bodies
import express from "express"; // express + types

interface PaymentRow { id: number; amount: number; currency: "INR"; status: "created" | "captured"; createdAt: Date } // DB row

type CreatePaymentBody = Omit<PaymentRow, "id" | "createdAt" | "status">; // client sends only amount + currency
type PaymentListItem = Pick<PaymentRow, "id" | "amount" | "status">; // list API returns a slim view

const app = express(); // app
app.use(express.json()); // JSON body parser
const rows: PaymentRow[] = []; // in-memory table for the demo

app.post("/payments", (req: express.Request<unknown, PaymentRow, CreatePaymentBody>, res: express.Response<PaymentRow>) => {
  const row: PaymentRow = { id: rows.length + 1, status: "created", createdAt: new Date(), ...req.body }; // server fills the rest
  rows.push(row); // store it
  res.status(201).json(row); // return full row
});

app.get("/payments", (_req, res: express.Response<PaymentListItem[]>) => {
  res.json(rows.map(({ id, amount, status }) => ({ id, amount, status }))); // only picked fields leave the server
});
```

```tsx
// StatusBadges.tsx — Record<Union, ...> gives an exhaustive UI map
type Status = "created" | "captured" | "failed"; // payment states

const color: Record<Status, string> = { // adding a new Status breaks the build here, which is the goal
  created: "gray", // pending
  captured: "green", // ok
  failed: "red", // problem
};

export function StatusBadge({ status }: { status: Status }) { // component
  return <span style={{ color: color[status] }}>{status}</span>; // lookup is always defined, no undefined check needed
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Writing `Pick` without the `K extends keyof T` constraint
```typescript
// ❌ wrong-pick.ts
type BadPick<T, K> = { [P in K]: T[P] };
// error TS2322: Type 'K' is not assignable to type 'string | number | symbol'.
// error TS2536: Type 'P' cannot be used to index type 'T'.
```
```typescript
// right-pick.ts
type GoodPick<T, K extends keyof T> = { [P in K]: T[P] }; // constraint makes T[P] legal
interface A { x: number } // sample
const v: GoodPick<A, "x"> = { x: 1 }; // works
console.log(v); // prints { x: 1 }
```

❌ Mistake 2: Expecting `Omit` to reject unknown keys
```typescript
// omit-lenient.ts
interface Order { id: number; amount: number } // sample
type Typo = Omit<Order, "idd">; // compiles! built-in Omit uses K extends keyof any
const t: Typo = { id: 1, amount: 5 }; // typo silently removes nothing
console.log(t); // prints { id: 1, amount: 5 }
```
✅ Correct: if you want a strict version, define `StrictOmit<T, K extends keyof T> = Omit<T, K>`.

❌ Mistake 3: Using `Omit` on a **union** type
✅ Correct: `Omit<A | B, "x">` is **not** distributive, it collapses the union to common keys. Write `type DistOmit<T, K extends PropertyKey> = T extends unknown ? Omit<T, K> : never;`.

---

## 🧠 Tricky Interview Question

```typescript
// tricky.ts — why does Omit lose the discriminant?
type Shape = { kind: "circle"; r: number } | { kind: "square"; side: number }; // union
type NoKind = Omit<Shape, "r">; // what is this?
const x: NoKind = { kind: "circle" }; // compiles
console.log(Object.keys(x)); // prints [ 'kind' ]
```
**Answer:** `keyof (A | B)` is only the **common** keys, here just `"kind"`. `Omit<Shape, "r">` therefore picks from `"kind"` only, giving `{ kind: "circle" | "square" }` and losing `r` and `side` completely. `Omit` and `Pick` are **not distributive**. Fix with a distributive wrapper: `type DistOmit<T, K extends PropertyKey> = T extends unknown ? Omit<T, K> : never`. This question separates people who memorised the utilities from people who understand them.

---

## ⚫ Interview Questions + Answers

Q1: Implement `Pick`.
A1: `type Pick<T, K extends keyof T> = { [P in K]: T[P] }`. The constraint is required for `T[P]` to be legal and it makes the mapped type homomorphic so `readonly`/`?` carry over.

Q2: Implement `Omit` and explain why `K extends keyof any`.
A2: `type Omit<T, K extends keyof any> = Pick<T, Exclude<keyof T, K>>`. `keyof any` is `string | number | symbol`, so you may pass keys that do not exist, which is useful for generic code but hides typos.

Q3: What is the difference between `Record<string, T>` and `{ [k: string]: T }`?
A3: Practically none, `Record<string, T>` expands to an index signature. The difference is readability and that `Record` also accepts literal unions (`Record<"a" | "b", T>`) giving exact required keys.

Q4: Why does `Record<Status, number>` help maintainability?
A4: Required keys equal the union members, so adding a member to the union produces a compile error everywhere an exhaustive map exists (labels, colors, counters).

Q5: How do you implement `Omit` without `Exclude`?
A5: With key remapping: `{ [P in keyof T as P extends K ? never : P]: T[P] }` (TS 4.1+). Mapping a key to `never` drops it, and `keyof T` as source keeps modifiers.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Deriving DTOs and view-models from one canonical entity type
- Exhaustive lookup tables keyed by a string-literal union (`Record<Status, ...>`)

❌ Avoid when:
- You apply `Pick`/`Omit` to unions without a distributive wrapper
- The derived type is so different that an explicit interface would be clearer to readers

---

## 📊 Visual Diagram
```
Order = { id, amount, status, note? }

Pick<Order, "id"|"amount">
   keys: [id, amount]  ──►  { id; amount }

Omit<Order, "id">
   keyof Order = id | amount | status | note
        Exclude "id" ──► amount | status | note
        Pick those   ──► { amount; status; note? }

Record<"a"|"b", V>
   "a" ─► V
   "b" ─► V     ──►  { a: V; b: V }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Mapped type | Loop over keys to build a type | Keys पर loop से type बनाना |
| `keyof` | Union of an object type's keys | Object type की keys का union |
| `Exclude<T,U>` | Remove union members assignable to U | U वाले members हटाना |
| Homomorphic | Preserves `?` and `readonly` | `?` और `readonly` बचाता है |
| Key remapping (`as`) | Rename/drop keys in a mapped type | Mapped type में keys बदलना/हटाना |
| Distributive | Conditional applied to each union member | हर union member पर अलग लगना |

---

## ⚡ 3-Line Summary
English:
1. `Pick` = mapped type over `K extends keyof T`; `Omit` = `Pick` + `Exclude`; `Record` = mapped type over any key union.
2. `Pick`/`Omit` are not distributive and `Omit` accepts unknown keys, know both gotchas.
3. Use `Record<Union, V>` for exhaustive maps so new union members force code updates.

Hindi:
1. `Pick` = `K extends keyof T` पर mapped type; `Omit` = `Pick` + `Exclude`; `Record` = किसी भी key union पर mapped type।
2. `Pick`/`Omit` distributive नहीं हैं और `Omit` unknown keys लेता है, दोनों gotchas याद रखो।
3. Exhaustive maps के लिए `Record<Union, V>` इस्तेमाल करो ताकि नया union member code update करवाए।

---

## ➡️ Next Topic
**103. Type-safe Event Emitter** — a generic `on`/`emit` where the event name decides the payload type.
