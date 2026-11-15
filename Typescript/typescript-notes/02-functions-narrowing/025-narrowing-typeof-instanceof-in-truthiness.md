# 25. Narrowing — typeof, instanceof, in, truthiness
# हिंदी में: Narrowing — typeof, instanceof, in और truthiness

> Verified with TypeScript 5.x (5.9) under `tsc --strict`. Inferred type predicates (`x => x !== null` auto-guard) need TS 5.5+.

---

## 🔵 Simple Definition (English)
**Narrowing** is how TypeScript refines a wide type (like `string | number | null`) into a more specific one inside a branch, using runtime checks it understands: `typeof`, `instanceof`, `in`, truthiness, equality, and `Array.isArray`. This is called **control-flow analysis**.

## 🔵 सरल परिभाषा (Hindi)
**Narrowing** वह तरीका है जिससे TypeScript किसी चौड़े type (जैसे `string | number | null`) को एक branch के अंदर ज़्यादा specific type में बदल देता है, उन runtime checks से जिन्हें वह समझता है: `typeof`, `instanceof`, `in`, truthiness, equality और `Array.isArray`। इसे **control-flow analysis** कहते हैं।

---

## 🔴 Problem it Solves
A value from `req.body`, `JSON.parse`, a DB column that can be NULL, or a union prop is not one clear type. You cannot call `.toUpperCase()` on `string | number`. Casting with `as` hides bugs. Narrowing lets plain `if` checks both protect the runtime AND prove the type to the compiler, with no casts.

## 🔴 यह क्यों बना? (Hindi)
`req.body`, `JSON.parse`, NULL हो सकने वाला DB column, या union prop एक साफ़ type नहीं होता। `string | number` पर आप `.toUpperCase()` नहीं बुला सकते। `as` से cast करने पर bugs छिप जाते हैं। Narrowing में साधारण `if` checks runtime को भी बचाते हैं और compiler को type भी साबित करते हैं, बिना cast के।

---

## 🟢 How it Works — Step by Step

Step 1 → Start with a union type: `string | number | null`.
Step 2 → Write a check TypeScript recognizes, e.g. `typeof x === "string"`.
Step 3 → Inside the true branch the type is narrowed to `string`; in the else branch the remaining members are `number | null`.
Step 4 → `typeof` narrows primitives (`"string" "number" "boolean" "bigint" "symbol" "undefined" "function" "object"`). Beware `typeof null === "object"`.
Step 5 → `instanceof` narrows class instances (`err instanceof AppError`). It checks the prototype chain.
Step 6 → `in` narrows object unions by property presence (`"card" in payment`).
Step 7 → Truthiness removes `null | undefined | 0 | "" | false | NaN`; careful, it also removes valid `0` and `""`. Prefer `!= null` or `=== undefined`.
Step 8 → Equality (`=== "paid"`), `Array.isArray`, and assignments also narrow. Narrowing is reset inside callbacks for `let` variables that are reassigned.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Union type से शुरू करो: `string | number | null`।
Step 2 → ऐसा check लिखो जिसे TypeScript पहचानता है, जैसे `typeof x === "string"`।
Step 3 → True branch में type `string` हो जाता है; else में बाकी `number | null` बचता है।
Step 4 → `typeof` primitives narrow करता है। ध्यान रहे `typeof null === "object"` होता है।
Step 5 → `instanceof` class instances narrow करता है (`err instanceof AppError`); यह prototype chain देखता है।
Step 6 → `in` property की मौजूदगी से object unions narrow करता है (`"card" in payment`)।
Step 7 → Truthiness `null | undefined | 0 | "" | false | NaN` हटाता है; सावधान, यह valid `0` और `""` भी हटा देता है। `!= null` या `=== undefined` बेहतर है।
Step 8 → Equality (`=== "paid"`), `Array.isArray` और assignments भी narrow करते हैं। जो `let` variable बाद में reassign होता है, उसकी narrowing callbacks के अंदर रीसेट हो जाती है।

---

## 🟡 Real World Example
**Paytm checkout** receives `amount` that may arrive as `"499"` (string from a form), `499` (number from JSON), or `null` (missing). The server narrows with `typeof` to normalise it into a number before charging. A wrong guess means charging Rs 0 or crashing.

## 🟡 Real Example Hindi mein
**Paytm checkout** को `amount` कभी `"499"` (form से string), कभी `499` (JSON से number), या `null` (missing) मिलता है। Server charge करने से पहले `typeof` से narrow करके उसे number में बदलता है। गलत अंदाज़ा मतलब Rs 0 charge या crash।

---

## 💻 Code Example — Basic

```typescript
// typeof narrowing: normalise a value that may be string | number | null
function toRupees(amount: string | number | null): number {
  // null check first (typeof null is "object", so use ===)
  if (amount === null) return 0; // here amount: string | number
  // typeof narrows to string
  if (typeof amount === "string") {
    return parseInt(amount, 10); // amount: string
  }
  // only number remains
  return amount; // amount: number
}

// truthiness narrowing: removes undefined (and "" / 0 too!)
function greet(name?: string): string {
  if (name) return `Hi ${name.toUpperCase()}`; // name: string (non-empty)
  return "Hi guest"; // name: string | undefined ("" lands here too)
}

console.log(toRupees("499"), toRupees(250), toRupees(null)); // numbers
console.log(greet("asha"), greet(), greet("")); // empty string falls to guest
```

Run with `npx tsx`:

```
499 250 0
Hi ASHA Hi guest Hi guest
```

## 💻 Code Example — Advanced

```typescript
// instanceof + in + Array.isArray + equality narrowing on realistic data

class AppError extends Error { // base custom error
  constructor(message: string, public readonly status: number) { super(message); } // keeps http status
}
class PaymentError extends AppError { // subclass
  constructor(message: string, public readonly gateway: string) { super(message, 402); } // 402 Payment Required
}

// instanceof narrows to a class (and its subclasses)
function describe(err: unknown): string {
  if (err instanceof PaymentError) return `pay:${err.gateway}:${err.status}`; // err: PaymentError
  if (err instanceof AppError) return `app:${err.status}`; // err: AppError
  if (err instanceof Error) return `error:${err.message}`; // err: Error
  return "unknown"; // err: unknown
}

// 'in' narrows a union of object shapes by property presence
type Card = { card: { last4: string } }; // card payment
type Upi = { upi: { vpa: string } }; // upi payment
type Payment = Card | Upi; // union

function label(p: Payment): string {
  if ("card" in p) return `card ****${p.card.last4}`; // p: Card
  return `upi ${p.upi.vpa}`; // p: Upi
}

// Array.isArray narrows string | string[]
function toList(tags: string | string[]): string[] {
  return Array.isArray(tags) ? tags : [tags]; // string[] in both branches
}

// Inferred type predicate (TS 5.5+): filter(x => x !== null) now gives number[]
const raw: (number | null)[] = [1, null, 3]; // mixed array
const clean = raw.filter((x) => x !== null); // TS 5.5+: number[]  (before 5.5: (number|null)[])
const total: number = clean.reduce((a, b) => a + b, 0); // compiles on 5.5+

console.log(describe(new PaymentError("declined", "razorpay"))); // pay:razorpay:402
console.log(describe(new AppError("bad", 400)), describe(new Error("x")), describe("s")); // others
console.log(label({ upi: { vpa: "a@okaxis" } }), toList("a"), total); // upi..., [ 'a' ], 4
```

Run with `npx tsx`:

```
pay:razorpay:402
app:400 error:x unknown
upi a@okaxis [ 'a' ] 4
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: narrow unknown input (req.query values are string | string[] | ParsedQs | ... )
import express from "express"; // express
import type { Request, Response } from "express"; // types

const app = express(); // app

app.get("/search", (req: Request, res: Response) => {
  const q = req.query.q; // type: string | ParsedQs | (string | ParsedQs)[] | undefined
  // typeof narrows away everything except plain string
  if (typeof q !== "string") { res.status(400).json({ error: "q must be a string" }); return; } // guard
  res.json({ results: [q.trim().toLowerCase()] }); // q: string here
});

// Narrowing caught errors: 'catch (e)' is unknown under strict (useUnknownInCatchVariables)
app.post("/pay", (_req: Request, res: Response) => {
  try {
    throw new Error("gateway timeout"); // simulate failure
  } catch (e) {
    const msg = e instanceof Error ? e.message : "unknown error"; // narrow unknown -> Error
    res.status(502).json({ error: msg }); // safe to read .message
  }
});
```

```tsx
// React: narrowing union props and loading/error/data state
import type { ReactNode } from "react"; // node type

type Props = { value: string | number | null }; // may be missing

export function Price({ value }: Props): ReactNode {
  if (value === null) return <span>N/A</span>; // value: string | number
  if (typeof value === "string") return <span>{value}</span>; // value: string
  return <span>Rs {value.toFixed(2)}</span>; // value: number
}
```

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: Using truthiness when 0 or "" is valid.**

```typescript
// ❌ WRONG: a Rs 0 discount is falsy, so it is treated as "no discount"
function discountLabel(d?: number): string {
  if (d) return `${d}% off`; // 0 is skipped
  return "no discount"; // prints for 0 as well
}
// ✅ RIGHT: compare explicitly
function discountLabel2(d?: number): string {
  if (d !== undefined) return `${d}% off`; // 0 is kept
  return "no discount";
}
console.log(discountLabel(0), "|", discountLabel2(0)); // behaviour differs
```

Real output with `npx tsx`:

```
no discount | 0% off
```

**Mistake 2: Calling a method before narrowing.**

```typescript
// ❌ WRONG: toUpperCase does not exist on number
function shout(x: string | number): string {
  return x.toUpperCase(); // ❌ error
}
```

Real compiler output:

```
error TS2339: Property 'toUpperCase' does not exist on type 'string | number'.
  Property 'toUpperCase' does not exist on type 'number'.
```

**Mistake 3: Forgetting `typeof null === "object"`.**

```typescript
// ❌ WRONG: object check does not remove null, then property access fails
function size(x: { n: number } | null): number {
  if (typeof x === "object") return x.n; // ❌ x may still be null
  return 0;
}
```

Real compiler output:

```
error TS18047: 'x' is possibly 'null'.
```

---

## 🧠 Tricky Interview Question

**Q: Why does narrowing not survive inside the callback here, and what prints?**

```typescript
// 'let' variable is reassigned later, so TS cannot trust narrowing inside the closure
function run(initial: string | undefined): void {
  let name = initial; // let, may be reassigned
  if (name !== undefined) {
    // narrowed to string here
    const len = name.length; // fine: narrowed
    setTimeout(() => {
      console.log(name?.length ?? -1); // optional chaining needed? (see answer)
    }, 0);
    console.log(len); // sync use
  }
  name = undefined; // reassigned after the check
}
run("Zomato");
```

Real output with `npx tsx`:

```
6
-1
```

**Answer:** Inside the closure TypeScript widens `name` back to `string | undefined` because it is a `let` that is reassigned later (`name = undefined`), so the callback may run after the reassignment. At runtime the timer fires after `name = undefined`, so the timer prints `-1` (the sync line prints `6`). Fix: copy to a `const` (`const safe = name;`) before the callback. (If a `let` is never reassigned after the check, newer TS versions keep narrowing in closures: TS 5.4+.)

---

## ⚫ Interview Questions + Answers

Q1: What are the main narrowing constructs?
A1: `typeof`, `instanceof`, `in`, truthiness, equality (`===`), `Array.isArray`, discriminant property checks, user-defined type guards, and assertion functions.

Q2: Why is `typeof x === "object"` not enough to exclude null?
A2: Because `typeof null` is `"object"` (a historic JS quirk). Check `x !== null` too, or use `x != null` to drop both null and undefined.

Q3: `instanceof` vs `in`: when to use which?
A3: `instanceof` works for class instances (checks prototype chain), so it fails on plain objects and across realms/duplicate package copies. `in` works for plain-object unions by checking a property name. For API data (JSON) prefer `in` or a discriminant field.

Q4: What changed in TS 5.4 and 5.5 for narrowing?
A4: TS 5.4 preserves narrowing in closures after last assignment. TS 5.5 infers type predicates for simple functions, so `arr.filter(x => x !== null)` yields `T[]` without a manual guard.

Q5: How does `catch (e)` get typed and how do you narrow it?
A5: Under `strict` (`useUnknownInCatchVariables`, TS 4.4+) `e` is `unknown`. Narrow with `e instanceof Error` (or a custom guard) before reading `.message`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Handling unions, optional values, `unknown` from `JSON.parse`, `catch`, and `req.body`
- Writing the first line of defence in Express controllers and React components
- You want zero-cost safety instead of `as` casts

❌ Avoid when:
- Checking external data deeply: use a validator like Zod, since `typeof` on a nested shape gets long
- Truthiness where `0`, `""` or `false` are legitimate values
- Relying on `instanceof` across package boundaries or serialized (JSON) data

---

## 📊 Visual Diagram
```
CONTROL-FLOW NARROWING
────────────────────────────────────────────
 x: string | number | null
        │ if (x === null)        ──► null  (return)
        ▼
 x: string | number
        │ if (typeof x === "string")
        ├── true  ──► x: string
        └── false ──► x: number

 Tools: typeof │ instanceof │ in │ truthiness │ === │ Array.isArray
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Narrowing | Refining a union to a subtype | Union को छोटे type में बदलना |
| Control-flow analysis | Compiler tracks types along branches | Branches के साथ type track करना |
| typeof guard | Check on primitive type string | Primitive type का check |
| instanceof guard | Prototype-chain class check | Class instance का check |
| in operator | Property-existence narrowing | Property की मौजूदगी से narrowing |
| Truthiness | Falsy values removed | Falsy values हटाना |

---

## ⚡ 3-Line Summary
English:
1. Narrowing uses `typeof`, `instanceof`, `in`, truthiness and equality to shrink unions safely.
2. Beware `typeof null`, falsy `0` / `""`, and closures over reassigned `let` variables.
3. For untrusted input prefer explicit checks or Zod; TS 5.5 infers filter predicates.

Hindi:
1. Narrowing `typeof`, `instanceof`, `in`, truthiness और equality से unions को सुरक्षित रूप से छोटा करता है।
2. `typeof null`, falsy `0` / `""` और reassigned `let` वाले closures से सावधान रहो।
3. Untrusted input के लिए explicit checks या Zod लो; TS 5.5 filter predicates infer करता है।

---

## ➡️ Next Topic
**26. Discriminated Unions** — a shared literal field (`status`, `type`) that lets the compiler narrow whole object shapes with a simple `switch`.
