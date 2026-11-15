# 23. Function Overloads
# हिंदी में: Function Overloads (एक function के कई signatures)

> Verified with TypeScript 5.x (5.9) under `tsc --strict`.

---

## 🔵 Simple Definition (English)
A **function overload** lets you declare **several call signatures** for one function name, followed by **one implementation** that handles all of them. The caller sees only the overload signatures (never the implementation signature), so the return type can depend on the argument types or argument count.

## 🔵 सरल परिभाषा (Hindi)
**Function overload** में आप एक function के नाम पर **कई call signatures** declare करते हैं और उसके बाद **एक implementation** लिखते हैं जो सबको handle करता है। Caller को सिर्फ overload signatures दिखते हैं (implementation signature नहीं दिखता), इसलिए return type argument के type या count पर निर्भर हो सकता है।

---

## 🔴 Problem it Solves
In JavaScript one function often behaves differently by argument: `getOrder(id)` returns one order, `getOrder(ids[])` returns many. A union return type (`Order | Order[]`) forces every caller to narrow the result even though they KNOW what they passed. Overloads map "input shape → output shape" precisely, so callers get exact types with no casts.

## 🔴 यह क्यों बना? (Hindi)
JavaScript में एक function अक्सर argument के हिसाब से अलग behave करता है: `getOrder(id)` एक order देता है, `getOrder(ids[])` कई orders देता है। Union return type (`Order | Order[]`) से हर caller को result narrow करना पड़ता है, जबकि उसे पहले से पता है कि उसने क्या pass किया। Overloads "input shape → output shape" का सही mapping देते हैं, इसलिए caller को exact type मिलता है, बिना cast के।

---

## 🟢 How it Works — Step by Step

Step 1 → Write one or more **overload signatures** (no body) with the same function name.
Step 2 → Write exactly **one implementation signature** with a body. It must be compatible with ALL overloads.
Step 3 → The implementation signature is **invisible** to callers; only overload signatures are callable.
Step 4 → TypeScript checks a call against overloads **top to bottom** and picks the **first** match.
Step 5 → Therefore put the **most specific** overload first and the most general last.
Step 6 → Inside the body, you narrow the broad implementation parameter types (typeof, Array.isArray) and cast/return carefully; the compiler does NOT verify that the body matches each overload's return type individually.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → एक ही नाम से एक या अधिक **overload signatures** लिखो (बिना body के)।
Step 2 → ठीक **एक implementation signature** लिखो जिसमें body हो। यह सभी overloads के साथ compatible होना चाहिए।
Step 3 → Implementation signature caller को **दिखता नहीं**; सिर्फ overload signatures call हो सकते हैं।
Step 4 → TypeScript call को overloads से **ऊपर से नीचे** match करता है और **पहला** match चुनता है।
Step 5 → इसलिए **सबसे specific** overload ऊपर और सबसे general नीचे रखो।
Step 6 → Body के अंदर broad parameter types को narrow करो (typeof, Array.isArray); compiler हर overload के return type को body से अलग-अलग verify नहीं करता।

---

## 🟡 Real World Example
**Razorpay-style `getPayment`**: `getPayment("pay_123")` returns one `Payment`; `getPayment(["pay_1","pay_2"])` returns `Payment[]`; `getPayment({ orderId: "order_9" })` returns the payments of that order. One function name, three input shapes, three exact output types.

## 🟡 Real Example Hindi mein
**Razorpay जैसा `getPayment`**: `getPayment("pay_123")` एक `Payment` देता है; `getPayment(["pay_1","pay_2"])` `Payment[]` देता है; `getPayment({ orderId: "order_9" })` उस order के सारे payments देता है। एक function का नाम, तीन input shapes, तीन exact output types।

---

## 💻 Code Example — Basic

```typescript
// Domain type for a payment record
interface Payment {
  id: string; // payment id like "pay_1"
  amount: number; // amount in paise
}

// Fake in-memory store standing in for a database
const store: Payment[] = [
  { id: "pay_1", amount: 49900 }, // first payment
  { id: "pay_2", amount: 12000 }, // second payment
];

// Overload 1: one id in -> one Payment (or undefined) out
function getPayment(id: string): Payment | undefined;
// Overload 2: many ids in -> array out
function getPayment(ids: string[]): Payment[];
// Implementation signature: broad, NOT visible to callers
function getPayment(arg: string | string[]): Payment | Payment[] | undefined {
  // Array input path
  if (Array.isArray(arg)) {
    return store.filter((p) => arg.includes(p.id)); // many results
  }
  // Single id path
  return store.find((p) => p.id === arg); // one result
}

const one = getPayment("pay_1"); // type: Payment | undefined
const many = getPayment(["pay_1", "pay_2"]); // type: Payment[]
console.log(one?.amount, many.length); // exact types, no narrowing needed for 'many'
```

Run with `npx tsx`:

```
49900 2
```

## 💻 Code Example — Advanced

```typescript
// Advanced: overloads by argument COUNT + overloaded arrow via call-signature type + generic overload
interface Payment { id: string; orderId: string; amount: number } // payment shape

const db: Payment[] = [
  { id: "pay_1", orderId: "o1", amount: 100 }, // row 1
  { id: "pay_2", orderId: "o1", amount: 250 }, // row 2
  { id: "pay_3", orderId: "o2", amount: 75 }, // row 3
];

// Most specific overload FIRST: an object filter returns an array
function findPayments(filter: { orderId: string }): Payment[];
// Then the id lookup
function findPayments(id: string): Payment | undefined;
// Then the "all" form (no argument)
function findPayments(): Payment[];
// Implementation: optional param covers the zero-argument overload
function findPayments(arg?: string | { orderId: string }): Payment | Payment[] | undefined {
  if (arg === undefined) return db; // no argument -> everything
  if (typeof arg === "string") return db.find((p) => p.id === arg); // string -> one
  return db.filter((p) => p.orderId === arg.orderId); // object -> many
}

// Overloads can also be written as a call-signature type (useful for arrow functions / interfaces)
interface Formatter {
  (value: number): string; // number -> string
  (value: Date): string; // date -> string
}
// An arrow function must satisfy ALL call signatures of Formatter
const fmt: Formatter = (value: number | Date): string =>
  typeof value === "number" ? `Rs ${(value / 100).toFixed(2)}` : value.toISOString();

console.log(findPayments({ orderId: "o1" }).length); // 2
console.log(findPayments("pay_3")?.amount); // 75
console.log(findPayments().length); // 3
console.log(fmt(12345)); // Rs 123.45
```

Run with `npx tsx`:

```
2
75
3
Rs 123.45
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: a repository whose overloads give controllers exact types
import express from "express"; // express app
import type { Request, Response } from "express"; // request/response types

interface Order { id: number; total: number; userId: number } // order row
const orders: Order[] = [{ id: 1, total: 500, userId: 7 }]; // pretend SQL Server table

// Overloads: by id -> one row, by userId object -> many rows
function loadOrders(id: number): Order | undefined;
function loadOrders(by: { userId: number }): Order[];
function loadOrders(arg: number | { userId: number }): Order | Order[] | undefined {
  if (typeof arg === "number") return orders.find((o) => o.id === arg); // single
  return orders.filter((o) => o.userId === arg.userId); // list
}

const app = express(); // create the app

// GET /orders/:id -> controller knows it gets Order | undefined, so it handles 404
app.get("/orders/:id", (req: Request<{ id: string }>, res: Response) => {
  const order = loadOrders(Number(req.params.id)); // Order | undefined
  if (!order) { res.status(404).json({ error: "not found" }); return; } // 404 branch
  res.json(order); // order is Order here
});

// GET /users/:uid/orders -> controller knows it gets Order[] (no undefined to handle)
app.get("/users/:uid/orders", (req: Request<{ uid: string }>, res: Response) => {
  res.json(loadOrders({ userId: Number(req.params.uid) })); // Order[]
});
```

```tsx
// React: overloads on a small utility used inside a component
import { useState } from "react"; // hook

// Overloads for a "toggle" helper: with value sets it, without value flips it
function useToggle(): [boolean, () => void]; // no initial -> default false
function useToggle(initial: boolean): [boolean, () => void]; // with initial
function useToggle(initial?: boolean): [boolean, () => void] {
  const [on, setOn] = useState<boolean>(initial ?? false); // state with default
  return [on, () => setOn((v) => !v)]; // value + flipper
}

export function CartButton() {
  const [open, toggle] = useToggle(); // overload 1 used
  return <button onClick={toggle}>{open ? "Hide cart" : "Show cart"}</button>; // UI
}
```

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: Calling the implementation signature (it is hidden).**

```typescript
// ❌ WRONG: only overload signatures are visible
function pick(id: string): string;
function pick(id: number): number;
function pick(id: string | number): string | number { return id; } // implementation

pick(Math.random() > 0.5 ? "a" : 1); // ❌ union argument matches no single overload
```

Real compiler output:

```
error TS2769: No overload matches this call.
  Overload 1 of 2, '(id: string): string', gave the following error.
    Argument of type 'string | number' is not assignable to parameter of type 'string'.
      Type 'number' is not assignable to type 'string'.
  Overload 2 of 2, '(id: number): number', gave the following error.
    Argument of type 'string | number' is not assignable to parameter of type 'number'.
      Type 'string' is not assignable to type 'number'.
```

```typescript
// ✅ RIGHT: add an overload that accepts the union (or use a generic/conditional type)
function pick2(id: string): string;
function pick2(id: number): number;
function pick2(id: string | number): string | number; // extra overload for the union
function pick2(id: string | number): string | number { return id; } // implementation
const r = pick2(Math.random() > 0.5 ? "a" : 1); // string | number
console.log(typeof r);
```

**Mistake 2: General overload first (it swallows the specific one).**

```typescript
// ❌ WRONG ORDER: first match wins, so the specific overload is dead code
function parse(x: unknown): unknown; // matches everything
function parse(x: string): number; // never chosen
function parse(x: unknown): unknown { return x; } // implementation

const n = parse("5"); // type is 'unknown', not number
// ✅ FIX: put parse(x: string): number FIRST, parse(x: unknown): unknown LAST.
```

**Mistake 3: Implementation not compatible with an overload.**

```typescript
// ❌ WRONG: implementation returns only string, overload promises number
function f(x: number): number;
function f(x: string): string;
function f(x: string): string { return x; } // implementation misses 'number'
```

Real compiler output:

```
error TS2394: This overload signature is not compatible with its implementation signature.
```

---

## 🧠 Tricky Interview Question

**Q: Why does this body compile even though it lies?**

```typescript
function dbl(x: number): number;
function dbl(x: string): string;
function dbl(x: number | string): number | string {
  return typeof x === "number" ? String(x) : Number(x); // swapped on purpose!
}
const a: number = dbl(2); // static type: number, runtime value: "2"
console.log(typeof a);
```

Real output with `npx tsx`:

```
string
```

**Answer:** TypeScript only checks that the implementation signature is *compatible* with each overload (loosely, in both directions); it does NOT check each return statement against the matching overload. So the overloads are a **promise you make**, not something proven. That is why overloads are unsafe if the body is sloppy; a generic function with a conditional type has the same limitation. Test overloads well.

---

## ⚫ Interview Questions + Answers

Q1: Is the implementation signature callable from outside?
A1: No. Callers only see the overload signatures. If you want the broad form callable, add it as an explicit overload.

Q2: How does TypeScript choose between overloads?
A2: Top to bottom; the first overload whose parameters accept the arguments wins. So order specific to general.

Q3: Overloads vs union types vs generics: when to choose which?
A3: Union param + union return is simplest but pushes narrowing to callers. Generics with conditional types (`T extends string ? A : B`) scale to many cases but are harder to read. Overloads are the most readable for a small fixed set (2-4) of input shapes with different return types.

Q4: Can arrow functions be overloaded?
A4: Not directly. Declare an interface/type with multiple call signatures (`{ (a: string): X; (a: number): Y }`) and assign a function that handles all, or use a function declaration with overloads.

Q5: Does TypeScript verify the body matches each overload?
A5: No, only a loose compatibility check on signatures. Return statements are checked against the implementation return type (usually a union), so you can write a body that contradicts the overloads (see the tricky question).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Return type truly depends on argument type or count (`getPayment(id)` vs `getPayment(ids)`)
- Wrapping a JS API that already behaved that way (e.g., library typings in `.d.ts`)
- You want ergonomic, cast-free call sites for a few fixed shapes

❌ Avoid when:
- A union or optional parameter is enough (do not overload just for optional params)
- Many cases exist: use generics + conditional types or separate named functions (`getPaymentById`, `getPaymentsByIds`), which is often clearer
- You cannot test the body: overloads are unchecked promises

---

## 📊 Visual Diagram
```
OVERLOAD RESOLUTION
────────────────────────────────────────────
 call: getPayment(x)
        │
        ▼  check top → bottom, first match wins
 ┌──────────────────────────────────┐
 │ (id: string): Payment|undefined  │ ◄─ visible
 │ (ids: string[]): Payment[]       │ ◄─ visible
 ├──────────────────────────────────┤
 │ (arg: string|string[]): ...      │ ◄─ implementation (HIDDEN)
 │   { body handles every case }    │
 └──────────────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Overload signature | A call shape without a body | बिना body का call shape |
| Implementation signature | The one real function with body | असली function (body के साथ), caller को नहीं दिखता |
| Resolution order | Top-to-bottom first match | ऊपर से नीचे पहला match |
| Call signature type | Interface with `(…): T` members | Interface में function call का shape |
| Compatibility check | Loose check impl vs overloads | Implementation और overloads का हल्का मेल जाँचना |

---

## ⚡ 3-Line Summary
English:
1. Overloads declare several visible signatures plus one hidden implementation.
2. The first matching overload wins, so order specific before general.
3. They are unchecked promises: keep the body honest and consider generics or separate functions.

Hindi:
1. Overloads कई visible signatures और एक छिपा हुआ implementation declare करते हैं।
2. पहला matching overload जीतता है, इसलिए specific को पहले रखो।
3. ये unchecked promises हैं: body ईमानदार रखो और generics या अलग functions पर भी सोचो।

---

## ➡️ Next Topic
**24. this Parameter Types** — declaring what `this` must be inside a function so detached methods and callbacks are caught at compile time.
