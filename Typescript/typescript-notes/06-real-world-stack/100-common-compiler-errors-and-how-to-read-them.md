# 100. Common Compiler Errors and How to Read Them
# हिंदी में: आम Compiler Errors और उन्हें पढ़ना कैसे सीखें

> Verified with **TypeScript 5.9.3** (`tsc --strict --target ES2022 --module esnext --moduleResolution bundler`). Sab error messages niche real `tsc` output se paste kiye gaye hain.

---

## 🔵 Simple Definition (English)
A TypeScript **compiler error** is a message of the form `file(line,col): error TSxxxx: message`. The `TSxxxx` number is a stable error code, the message says **what type was found vs what was expected**, and the indented lines below it (the "elaboration chain") explain **why** the check failed. Reading errors **bottom-up** (the last, most indented line is usually the real root cause) is the single most valuable debugging skill in TypeScript.

## 🔵 सरल परिभाषा (Hindi)
TypeScript का **compiler error** एक message होता है: `file(line,col): error TSxxxx: message`। `TSxxxx` एक fixed error code है, message बताता है कि **कौन सा type मिला और कौन सा expected था**, और नीचे की indented lines (elaboration chain) बताती हैं कि check **क्यों** fail हुआ। Errors को **नीचे से ऊपर** पढ़ना (सबसे आखिरी, सबसे ज़्यादा indented line अक्सर असली कारण होती है) TypeScript की सबसे कीमती debugging skill है।

---

## 🔴 Problem it Solves
Juniors see a wall of red text and either paste `as any` or `// @ts-ignore` to silence it. That throws away the whole safety net. Senior engineers instead recognise the 15-20 most common error codes (TS2322, TS2339, TS2345, TS2532/TS18048, TS7006, TS7053, TS2307, TS2554, TS2741, TS2353...) and know in 5 seconds whether the bug is in **their code** (wrong data), **the type** (too narrow), or **the config** (missing types). In interviews, "here is an error, explain it and fix it without `any`" is a very common live question.

## 🔴 यह क्यों बना? (Hindi)
Juniors लाल text की दीवार देखकर `as any` या `// @ts-ignore` चिपका देते हैं। इससे पूरा safety net बेकार हो जाता है। Senior engineers 15-20 सबसे आम error codes (TS2322, TS2339, TS2345, TS2532/TS18048, TS7006, TS7053, TS2307, TS2554, TS2741, TS2353...) पहचानते हैं और 5 seconds में जान लेते हैं कि bug **आपके code** (गलत data), **type** (बहुत narrow), या **config** (types missing) में है। Interview में "यह error दिया है, इसे बिना `any` के समझाओ और fix करो" बहुत आम live सवाल है।

---

## 🟢 How it Works — Step by Step

Step 1 → Read the **location**: `file(line,col)` points to the exact token, not the whole line.
Step 2 → Read the **code**: `TS2322` = "not assignable", `TS2339` = "property does not exist", `TS2345` = "bad argument". Google/search the code, it is stable across versions.
Step 3 → Read the **first line**: "Type A is not assignable to type B" means **A = what you gave, B = what was expected**.
Step 4 → Read the **indented chain bottom-up**. The last line is the exact mismatching leaf (e.g. one property of one nested object).
Step 5 → Decide the fix: change the **value**, widen the **type**, add a **narrowing check**, or fix **config/@types**. Never reach for `any` first.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Location** पढ़ो: `file(line,col)` exact token दिखाता है, पूरी line नहीं।
Step 2 → **Code** पढ़ो: `TS2322` = "assign नहीं हो सकता", `TS2339` = "property मौजूद नहीं", `TS2345` = "argument गलत"। Code search करो, यह versions में stable रहता है।
Step 3 → **पहली line** पढ़ो: "Type A is not assignable to type B" यानी **A = जो आपने दिया, B = जो expected था**।
Step 4 → **Indented chain नीचे से ऊपर** पढ़ो। आखिरी line exact mismatching leaf बताती है (जैसे एक nested object की एक property)।
Step 5 → Fix चुनो: **value** बदलो, **type** widen करो, **narrowing check** जोड़ो, या **config/@types** ठीक करो। सबसे पहले `any` मत लगाओ।

---

## 🟡 Real World Example
A Razorpay-style checkout screen crashes in production with `Cannot read properties of undefined (reading 'toUpperCase')` because `order.coupon` is optional and the API did not send it. With `strict` on, the compiler would have flagged the exact line at build time as `TS18048: 'order.coupon' is possibly 'undefined'`. The team that **reads** that error adds one `if` and the production crash never happens; the team that silences it with `!` ships the crash.

## 🟡 Real Example Hindi mein
Razorpay-style checkout screen production में `Cannot read properties of undefined (reading 'toUpperCase')` से crash होती है क्योंकि `order.coupon` optional है और API ने भेजा नहीं। `strict` on होने पर compiler build time पर ही exact line को `TS18048: 'order.coupon' is possibly 'undefined'` बताकर flag कर देता। जो team यह error **पढ़ती** है वह एक `if` जोड़ देती है और production crash कभी नहीं होता; जो `!` से चुप करा देती है वह crash ship करती है।

---

## 💻 Code Example — Basic

Each block below is an **intentional error** (marked `// ❌`) with the real compiler output.

```typescript
// error-1.ts — TS2322: "Type X is not assignable to type Y"
interface Order { id: number; amount: number; status: "paid" | "failed" } // Order shape

// ❌ amount must be number but we passed a string (typical when reading from an HTML input)
const o: Order = { id: 1, amount: "499", status: "paid" };
// error TS2322: Type 'string' is not assignable to type 'number'.
```

```typescript
// error-2.ts — TS2322 with a literal union: the classic "pending" typo
type Status = "paid" | "failed"; // only two allowed values

// ❌ "pending" is not part of the union
const s: Status = "pending";
// error TS2322: Type '"pending"' is not assignable to type 'Status'.
```

```typescript
// error-3.ts — TS2339: property does not exist
const p = { a: 1 }; // inferred as { a: number }

// ❌ "b" was never declared on p
console.log(p.b);
// error TS2339: Property 'b' does not exist on type '{ a: number; }'.
```

```typescript
// error-4.ts — TS2554: wrong number of arguments
function applyCoupon(total: number, code: string): number { // two required params
  return code ? total - 50 : total; // toy discount
}

// ❌ forgot the second argument
applyCoupon(500);
// error TS2554: Expected 2 arguments, but got 1.
```

```typescript
// error-5.ts — TS2353: excess property check on a fresh object literal
function sumPrices(items: { price: number }[]): number { // items only know "price"
  return items.reduce((acc, i) => acc + i.price, 0); // add up all prices
}

// ❌ "qty" is not declared in the parameter type
sumPrices([{ price: 10, qty: 2 }]);
// error TS2353: Object literal may only specify known properties, and 'qty' does not exist in type '{ price: number; }'.
```

## 💻 Code Example — Advanced

The errors that senior interviews actually ask about: nullability, implicit any, index access, and nested chains.

```typescript
// adv-1.ts — TS18048: possibly undefined (strictNullChecks)
interface Cart { coupon?: string } // coupon is optional
const cart: Cart = {}; // no coupon given

// ❌ calling a method on string | undefined
console.log(cart.coupon.toUpperCase());
// error TS18048: 'cart.coupon' is possibly 'undefined'.
```

```typescript
// adv-2.ts — fixing TS18048 properly with narrowing (compiles clean)
interface Cart { coupon?: string } // same shape
function couponLabel(cart: Cart): string {
  if (cart.coupon === undefined) return "NO COUPON"; // narrow: handle the undefined path
  return cart.coupon.toUpperCase(); // here TS knows coupon is string
}
console.log(couponLabel({ coupon: "save20" })); // prints SAVE20
console.log(couponLabel({})); // prints NO COUPON
```

```typescript
// adv-3.ts — TS7006: implicit any (noImplicitAny is part of strict)
// ❌ parameter has no type and no contextual type to infer from
function double(x) { return x * 2; }
// error TS7006: Parameter 'x' implicitly has an 'any' type.
```

```typescript
// adv-4.ts — TS7053: indexing an object with a plain string
const prices = { dosa: 80, idli: 40 }; // inferred { dosa: number; idli: number }
const key: string = "dosa"; // widened to string, not the literal

// ❌ string cannot be proven to be a key of prices
console.log(prices[key]);
// error TS7053: Element implicitly has an 'any' type because expression of type 'string' can't be used to index type '{ dosa: number; idli: number; }'.
//   No index signature with a parameter of type 'string' was found on type '{ dosa: number; idli: number; }'.
```

```typescript
// adv-5.ts — fixing TS7053 with keyof (compiles clean)
const prices = { dosa: 80, idli: 40 }; // same object
function priceOf(k: keyof typeof prices): number { // only real keys accepted
  return prices[k]; // safe indexing
}
console.log(priceOf("dosa")); // prints 80
```

```typescript
// adv-6.ts — reading a multi-line chain: the REAL cause is the LAST line
type Handler = (id: string) => void; // handler receives a string id

// ❌ our function takes a number instead
const h: Handler = (id: number) => {};
// error TS2322: Type '(id: number) => void' is not assignable to type 'Handler'.
//   Types of parameters 'id' and 'id' are incompatible.
//     Type 'string' is not assignable to type 'number'.
```

```typescript
// adv-7.ts — TS2366: not all code paths return a value
// ❌ if x is 0 the function falls off the end and returns undefined
function label(x: number): string {
  if (x) return "non-zero";
}
// error TS2366: Function lacks ending return statement and return type does not include 'undefined'.
```

```typescript
// adv-8.ts — TS2307: module not found (config / @types problem, not a type problem)
// ❌ file path typo OR missing "@types/xyz" package
import { nothing } from "./nope";
// error TS2307: Cannot find module './nope' or its corresponding type declarations.
```

---

## 🟠 Node/Express + React Integration

```typescript
// express-errors.ts — typical Express mistakes and their codes
import express, { Request, Response } from "express"; // types ship in @types/express

const app = express(); // create app

app.get("/orders/:id", (req: Request<{ id: string }>, res: Response) => {
  const id: number = req.params.id; // ❌ params are ALWAYS strings
  // error TS2322: Type 'string' is not assignable to type 'number'.
  res.json({ id }); // never reached at build time
});
```

```typescript
// express-fixed.ts — the same route fixed with an explicit conversion
import express, { Request, Response } from "express"; // express types

const app = express(); // create app

app.get("/orders/:id", (req: Request<{ id: string }>, res: Response) => {
  const id = Number(req.params.id); // convert the string explicitly
  if (Number.isNaN(id)) { // reject garbage like /orders/abc
    res.status(400).json({ error: "id must be numeric" }); // 400 Bad Request
    return; // stop here
  }
  res.json({ id }); // id is a real number now
});
```

```tsx
// Badge.tsx — React props mismatch is TS2322 or TS2741 too
type BadgeProps = { label: string; count: number }; // required props

function Badge({ label, count }: BadgeProps) { // simple component
  return <span>{label}: {count}</span>; // render
}

// ❌ "count" is missing
export const bad = <Badge label="Cart" />;
// error TS2741: Property 'count' is missing in type '{ label: string; }' but required in type 'BadgeProps'.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Silencing with `any`, `!`, or `@ts-ignore` instead of reading the error
```typescript
// wrong-silence.ts
interface User { nick?: string } // nick optional
const u: User = {}; // no nick
const bad = u.nick!.length; // wrong: "!" hides TS18048 and crashes at runtime with TypeError
const good = u.nick?.length ?? 0; // right: optional chaining + default, no crash, no error
console.log(good); // prints 0
```

❌ Mistake 2: Fixing the top line instead of the bottom line of a chain
```typescript
// wrong-chain.ts
type Item = { name: string; price: number }; // item shape
type Cart = { items: Item[] }; // cart holds items

// ❌ the error is deep inside items[0].price, not "cart"
const c: Cart = { items: [{ name: "Dosa", price: "80" }] };
// error TS2322: Type 'string' is not assignable to type 'number'.
```
✅ Correct: the location already points at `price: "80"`. Change that single value to `80`; do not touch `Cart`.

❌ Mistake 3: Adding `as Type` to force an assignment
✅ Correct: `as` does not convert anything at runtime, it only lies to the compiler. Use `Number(x)`, a type guard, or `zod.parse` to **really** change or validate the value.

---

## 🧠 Tricky Interview Question

```typescript
// tricky.ts — why does the first line compile but the second does not?
const a: { id: number } = { id: 1, extra: true }; // ❌ fresh literal
// error TS2353: Object literal may only specify known properties, and 'extra' does not exist in type '{ id: number; }'.

const tmp = { id: 1, extra: true }; // not a fresh literal any more (stored in a variable)
const b: { id: number } = tmp; // compiles clean
console.log(b.id); // prints 1
```
**Answer:** **Excess property checks** only run on *fresh object literals* assigned directly to a typed target. Once the object is stored in a variable, normal **structural typing** applies: `{ id: number; extra: boolean }` has everything `{ id: number }` needs, so it is assignable. This is a deliberate trade-off, the check catches typos (`amout` vs `amount`) without banning subtypes.

---

## ⚫ Interview Questions + Answers

Q1: What does `TS2322` mean and how do you read it?
A1: "Type A is not assignable to type B". A is what you supplied, B is what the target expects. If there is an indented chain below, the **last line** is the exact leaf mismatch. Fix the value, widen B, or narrow A, in that order of preference.

Q2: Difference between `TS2339` and `TS7053`?
A2: `TS2339` = property name does not exist on that type at all (typo or wrong type). `TS7053` = you indexed with a *dynamic* key (like a `string` variable) that TypeScript cannot prove is a valid key, fix with `keyof typeof obj`, a union of literals, or an index signature / `Record<string, T>`.

Q3: Why does `TS18048` (or `TS2532` in older versions) appear and how do you fix it without `!`?
A3: With `strictNullChecks`, optional values are `T | undefined`. Narrow first: `if (x)`, `x?.y`, `x ?? default`, or an early `return`. The `!` operator only suppresses the compiler, the runtime crash stays.

Q4: What does `TS7006` tell you about your tsconfig?
A4: `noImplicitAny` (part of `strict`) is on and a parameter has no annotation and no contextual type. Add a type, or let it be inferred from context (callback passed to a typed API).

Q5: `TS2307 Cannot find module` appears for a package that is installed. Why?
A5: The package ships no types. Install `@types/<pkg>`, or declare it in a `.d.ts` (`declare module "pkg";`). Also check `moduleResolution` and `paths` in tsconfig, because `bundler` vs `node16` resolve extensions differently.

---

## 🔷 When to Use + When Not to Use
✅ Use this reading discipline when:
- Any red squiggle appears, always read the bottom of the chain first
- Reviewing a PR where someone added `any`, `!` or `@ts-ignore`
- Triaging a build-break after upgrading `@types/*` or TypeScript itself

❌ Avoid:
- Pasting `// @ts-ignore` (use `// @ts-expect-error` with a comment if you truly must, it fails loudly when the error disappears)
- Bulk `as any` migrations that hide hundreds of real bugs

---

## 📊 Visual Diagram
```
src/order.ts(2,27): error TS2322: Type 'string' is not assignable to type 'number'.
 │        │   │          │                 │                          │
 │        │   │          │                 │                          └─ EXPECTED (target)
 │        │   │          │                 └─ GIVEN (source)
 │        │   │          └─ stable error code, search this
 │        │   └─ column
 │        └─ line
 └─ file

Chain error (read BOTTOM -> TOP):
  Type '(id: number) => void' is not assignable to type 'Handler'.   <- 3. symptom
    Types of parameters 'id' and 'id' are incompatible.              <- 2. where
      Type 'string' is not assignable to type 'number'.              <- 1. ROOT CAUSE
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Error code (TSxxxx) | Stable numeric id of a diagnostic | Diagnostic का stable number |
| Elaboration chain | Indented lines explaining the failure | Failure समझाने वाली indented lines |
| Excess property check | Extra keys on fresh literal rejected | Fresh literal में extra keys reject |
| noImplicitAny | Forbid untyped params | बिना type के params मना |
| strictNullChecks | `null`/`undefined` are separate types | null/undefined अलग types |
| `@ts-expect-error` | Suppress one error, fail if no error | एक error दबाओ, error न हो तो fail |

---

## ⚡ 3-Line Summary
English:
1. Error = location + `TSxxxx` code + (given vs expected) + an indented chain whose **last line is the root cause**.
2. Fix by changing the value, widening the type, narrowing with a check, or fixing config/`@types`, never by `any`/`!`.
3. Memorise TS2322, TS2339, TS2345, TS2554, TS2353, TS18048, TS7006, TS7053, TS2307.

Hindi:
1. Error = location + `TSxxxx` code + (given vs expected) + indented chain जिसकी **आखिरी line असली कारण** है।
2. Value बदलकर, type widen करके, check से narrow करके, या config/`@types` ठीक करके fix करो, `any`/`!` से कभी नहीं।
3. TS2322, TS2339, TS2345, TS2554, TS2353, TS18048, TS7006, TS7053, TS2307 याद कर लो।

---

## ➡️ Next Topic
**101. Implement DeepPartial and DeepReadonly** — recursive mapped types, the first classic interview problem.
