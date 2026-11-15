# 5. Primitive Types (string, number, boolean, bigint, symbol)
# हिंदी में: Primitive Types (string, number, boolean, bigint, symbol)

> Version note: **TypeScript 5.x** (5.9.3 पर verify)। `bigint` के लिए `target` ES2020+ चाहिए। `unique symbol` TS 2.7 से है।

---

## 🔵 Simple Definition (English)
**Primitive types** are the basic, immutable value types of JavaScript, and TypeScript names them with **lowercase** keywords: `string`, `number`, `boolean`, `bigint`, `symbol` (plus `null`, `undefined`, and `void`/`never`/`unknown`/`any` which are special). They are copied **by value**, have no properties of their own (the wrapper objects `String`, `Number` are different things) and all other types are built out of them.

## 🔵 सरल परिभाषा (Hindi)
**Primitive types** JavaScript के बुनियादी, immutable value types हैं और TypeScript इन्हें **lowercase** keywords से नाम देता है: `string`, `number`, `boolean`, `bigint`, `symbol` (साथ में `null`, `undefined`, और खास types `void`/`never`/`unknown`/`any`)। ये **value से copy** होते हैं, इनकी अपनी properties नहीं होतीं (wrapper objects `String`, `Number` अलग चीज़ हैं) और बाकी सारे types इन्हीं से बनते हैं।

---

## 🔴 Problem it Solves
JS values are loosely typed: a form field gives you `"499"` (string), an API gives `499` (number), a DB driver gives `"499.00"` (decimal as string) and `499 + 1` vs `"499" + 1` silently differ. Money is worse: `0.1 + 0.2 !== 0.3`, and IDs above `2^53` (Twitter-style snowflake IDs, some DB bigints) lose precision in `number`. Naming the primitive precisely (`number` vs `bigint`, `string` vs `number`) lets the compiler stop mix-ups like `bigint + number` and string-for-number bugs.

## 🔴 यह क्यों बना? (Hindi)
JS values ढीले typed हैं: form field `"499"` (string) देता है, API `499` (number), DB driver `"499.00"` (decimal string), और `499 + 1` व `"499" + 1` चुपचाप अलग नतीजे देते हैं। Money में दिक्कत और ज़्यादा: `0.1 + 0.2 !== 0.3`, और `2^53` से बड़े IDs (snowflake IDs, कुछ DB bigints) `number` में precision खो देते हैं। Primitive को सही नाम देना (`number` बनाम `bigint`, `string` बनाम `number`) compiler को `bigint + number` और string-को-number समझने जैसी गलतियाँ रोकने देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `string` — text; `'single'`, `"double"` or `` `template ${x}` `` literals.
Step 2 → `number` — ALL numbers are 64-bit floats (integers, decimals, `NaN`, `Infinity`). Safe integer range: ±(2^53 − 1).
Step 3 → `boolean` — `true` / `false` only (not "truthy" values).
Step 4 → `bigint` — arbitrary-size integers, literal `123n`. Cannot be mixed with `number` in arithmetic. Needs `target >= ES2020`.
Step 5 → `symbol` — unique, immutable identifiers: `Symbol("id")`. `unique symbol` type is used for `const` symbols as object keys / branding.
Step 6 → Lowercase vs uppercase: always use `string`, never `String` (the wrapper object type). `const x = "a"` gets the **literal type** `"a"`, `let x = "a"` gets widened `string`.
Step 7 → `null` and `undefined` are their own types; with `strictNullChecks` they are NOT assignable to `string`/`number` (topic 019).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `string` — text; `'single'`, `"double"` या `` `template ${x}` `` literals।
Step 2 → `number` — **सारे** numbers 64-bit floats हैं (integers, decimals, `NaN`, `Infinity`)। Safe integer range: ±(2^53 − 1)।
Step 3 → `boolean` — सिर्फ `true` / `false` ("truthy" values नहीं)।
Step 4 → `bigint` — किसी भी size का integer, literal `123n`। `number` के साथ arithmetic में मिला नहीं सकते। `target >= ES2020` चाहिए।
Step 5 → `symbol` — unique, immutable identifiers: `Symbol("id")`। `unique symbol` type `const` symbols को object key / branding के लिए इस्तेमाल होता है।
Step 6 → Lowercase बनाम uppercase: हमेशा `string` लिखो, `String` नहीं (वह wrapper object type है)। `const x = "a"` को **literal type** `"a"` मिलता है, `let x = "a"` को widened `string`।
Step 7 → `null` और `undefined` अपने अलग types हैं; `strictNullChecks` में ये `string`/`number` को assign नहीं हो सकते (topic 019)।

---

## 🟡 Real World Example
**Razorpay / Paytm money handling:** amounts travel as integers in **paise** (`number`) so `₹499.50` is `49950`, never `499.5` floats. Order IDs like `order_Mx83k...` are `string`. `isCodEligible` is a `boolean`. A 64-bit **ledger entry ID** from SQL Server `BIGINT` is returned by the `mssql` driver as a **string or bigint** because it can exceed `Number.MAX_SAFE_INTEGER` — typed as `bigint`/`string` rather than `number`, avoiding silent rounding of IDs. A `symbol` is used by libraries (Redux Toolkit uses it internally; React uses `Symbol.for("react.element")`).

## 🟡 Real Example Hindi mein
**Razorpay / Paytm में पैसे का handling:** amounts **paise** में integer (`number`) के रूप में चलते हैं, यानी `₹499.50` = `49950`, कभी `499.5` float नहीं। Order IDs जैसे `order_Mx83k...` `string` हैं। `isCodEligible` एक `boolean` है। SQL Server `BIGINT` वाला 64-bit **ledger entry ID** `mssql` driver **string या bigint** में देता है क्योंकि वह `Number.MAX_SAFE_INTEGER` से बड़ा हो सकता है — इसलिए उसे `number` नहीं, `bigint`/`string` type करते हैं ताकि ID चुपचाप round न हो। `symbol` libraries इस्तेमाल करती हैं (React `Symbol.for("react.element")` वापरता है)।

---

## 💻 Code Example — Basic

```typescript
// primitives-basic.ts — the five primitives in an order model

// string: text values
const orderId: string = "SW-90421";              // explicit annotation
const customer = "Aditya";                       // inferred as the literal type "Aditya" (const)

// number: ints and floats share one type; keep money in paise
const priceInPaise: number = 49950;              // Rs 499.50 stored as an integer
const gstPaise: number = Math.round(priceInPaise * 0.05); // 2498 (5% GST, rounded)

// boolean: strictly true/false
const isPaid: boolean = priceInPaise > 0;        // result of a comparison is boolean

// bigint: big integers, literal ends with n
const ledgerId: bigint = 9007199254740993n;      // 2^53 + 1, impossible to store exactly in number
const nextLedgerId: bigint = ledgerId + 1n;      // both sides bigint -> OK

// symbol: unique key that never collides
const internalFlag: symbol = Symbol("internal"); // every Symbol() call is unique
const same = Symbol("internal") === internalFlag;// false even with same description

console.log(orderId, customer, priceInPaise, gstPaise, isPaid);
console.log(ledgerId, nextLedgerId, same, 0.1 + 0.2);
// Output:
// SW-90421 Aditya 49950 2498 true
// 9007199254740993n 9007199254740994n false 0.30000000000000004
```

```typescript
// ❌ intentional errors — real tsc 5.9 output in comments
let name: string = 42;
// error TS2322: Type 'number' is not assignable to type 'string'.

const big: bigint = 10n;
const mixed = big + 5;
// error TS2365: Operator '+' cannot be applied to types 'bigint' and '5'.

let flag: boolean = "true";
// error TS2322: Type 'string' is not assignable to type 'boolean'.

const n: number = 10n;
// error TS2322: Type 'bigint' is not assignable to type 'number'.
```

## 💻 Code Example — Advanced

```typescript
// primitives-advanced.ts — widening, unique symbol, wrapper-type trap, safe money

// 1) const vs let: literal type vs widened type
const status = "PLACED";        // type: "PLACED" (literal)
let status2 = "PLACED";         // type: string  (widened because let can change)
status2 = "DELIVERED";          // OK, any string
// status = "x" would be an error: const cannot be reassigned

// 2) unique symbol: a compile-time unique key (only on const declarations)
const INTERNAL: unique symbol = Symbol("internal");
interface Order {
  id: string;
  [INTERNAL]: boolean;          // key is the symbol, not the string "INTERNAL"
}
const o: Order = { id: "A1", [INTERNAL]: true };
console.log(Object.keys(o));    // [ 'id' ]  (symbol keys are skipped by Object.keys)
console.log(o[INTERNAL]);       // true

// 3) Wrapper object types: use lowercase primitives, not String/Number
function lengthOf(s: string): number { return s.length; } // right
// function bad(s: String) {}  // "String" works but is the wrapper type, banned by eslint ban-types

// 4) Number helpers: guard against NaN and unsafe integers
function toPaise(rupees: string): number {
  const n = Number(rupees);                       // "499.50" -> 499.5, "abc" -> NaN
  if (Number.isNaN(n)) throw new Error("not a number");     // NaN is typeof "number"!
  const paise = Math.round(n * 100);              // avoid float drift by rounding once
  if (!Number.isSafeInteger(paise)) throw new Error("unsafe amount");
  return paise;
}
console.log(toPaise("499.50"));                   // 49950
console.log(typeof NaN, Number.isSafeInteger(2 ** 53)); // number false

// 5) bigint <-> number conversions are explicit
const id = BigInt("9007199254740993");            // from a DB string safely
console.log(id.toString(), Number(id));           // 9007199254740993 9007199254740992 (precision lost!)

// Output:
// [ 'id' ]
// true
// 49950
// number false
// 9007199254740993 9007199254740992
```

---

## 🟠 Node/Express + React Integration

**Express — query params are always `string` (or arrays/objects), never `number`:**

```typescript
// routes.ts — convert primitives at the HTTP boundary
import express from "express";

const app = express();

// GET /orders?page=2&paidOnly=true  -> req.query values are strings
app.get("/orders", (req, res) => {
  const page = Number(req.query.page ?? 1);            // string|ParsedQs|... -> number
  const paidOnly = req.query.paidOnly === "true";      // "true" string -> boolean
  if (!Number.isInteger(page) || page < 1) {           // guard NaN / decimals
    res.status(400).json({ error: "page must be a positive integer" });
    return;
  }
  res.json({ page, paidOnly });                        // typed values from here on
});

// BIGINT from SQL Server: JSON.stringify cannot serialize bigint, so send as string
app.get("/ledger/:id", (req, res) => {
  const id: bigint = BigInt(req.params.id);            // BigInt() throws on bad text
  res.json({ id: id.toString() });                     // bigint -> string for JSON
});
```

**React — controlled input gives `string`, state wants `number`:**

```tsx
// QtyInput.tsx — string in the DOM, number in state
import { useState } from "react";

export function QtyInput() {
  const [qty, setQty] = useState<number>(1);                    // number state
  return (
    <input
      type="number"
      value={qty}                                               // number is accepted by value
      onChange={(e) => setQty(e.target.valueAsNumber || 1)}     // valueAsNumber: number (NaN if empty)
    />
  );
}
```
Redux note: keep money as integer `number` paise in the store; format with `Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" })` only in the view. Redux state must be serializable — **do not store `bigint` or `symbol` in the store** (RTK's serializability check warns); store IDs as `string`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `String` / `Number` / `Boolean` (wrapper objects) as types
```typescript
// ⚠️ Wrong — wrapper object type, compiles but is almost never what you mean
function shout(s: String): String { return s.toUpperCase(); } // returns primitive, typed as wrapper
// Right
function shout2(s: string): string { return s.toUpperCase(); }
console.log(shout2("pizza"));
```
```typescript
// ❌ The difference shows up on assignment
const wrapper: String = "hi";
const prim: string = wrapper;
// error TS2322: Type 'String' is not assignable to type 'string'.
//   'string' is a primitive, but 'String' is a wrapper object. Prefer using 'string' when possible.
```

❌ Mistake 2: Storing money as floating rupees
```typescript
// ⚠️ Wrong — float drift
const total = 0.1 + 0.2;        // 0.30000000000000004
// Right — integer paise, convert only for display
const totalPaise = 10 + 20;     // 30
console.log(total, totalPaise);
```

❌ Mistake 3: Assuming `NaN` is not a `number`, or comparing `x === NaN`
✅ Correct: `typeof NaN === "number"`; use `Number.isNaN(x)`. `NaN === NaN` is always `false`.

❌ Mistake 4: `JSON.stringify` on an object containing `bigint` — throws `TypeError: Do not know how to serialize a BigInt`.
✅ Correct: convert to string first (`id.toString()`) or add a replacer.

---

## 🧠 Tricky Interview Question

```typescript
const a = "SW";
let b = "SW";
const c = [a];
const d = [b];
// What are the types of a, b, c, d?
```
**Answer:** `a: "SW"` (literal, `const`), `b: string` (widened, `let`), `c: string[]` (array element of a mutable array widens), `d: string[]`. Interviewers use this to test **literal widening**: `const` primitives keep the literal type, but when used in a mutable position (`let`, array/object property) TypeScript widens it to `string` unless you write `as const` or annotate. This is why `{ status: "PLACED" }` assigned to a variable is `{ status: string }` and fails to match a `"PLACED" | "DELIVERED"` parameter (topic 017).

---

## ⚫ Interview Questions + Answers

Q1: What are the primitive types in TypeScript?
A1: `string`, `number`, `boolean`, `bigint`, `symbol`, `null`, `undefined`. (`void`, `never`, `unknown`, `any` are special types; `object` is non-primitive.) Always use the lowercase names.

Q2: Why is there only one `number` type — what about int/float?
A2: JS numbers are IEEE-754 64-bit doubles, so TS has no `int`. Use `Number.isInteger()` at runtime or brand types (topic 058) for `Paise`. Beyond `Number.MAX_SAFE_INTEGER` (2^53−1) use `bigint`.

Q3: Why can't I add a `bigint` and a `number`?
A3: Mixing them would silently lose precision or change semantics, so both JS and TS throw/error (`TS2365`; JS throws `TypeError: Cannot mix BigInt and other types`). Convert explicitly: `BigInt(n)` or `Number(b)`.

Q4: What is `unique symbol` used for?
A4: A `const` symbol declared with type `unique symbol` has its own nominal-like type, so it can be a property key in an interface/class, a sentinel value, or a "brand" for nominal typing. Each `unique symbol` is only assignable to itself.

Q5: `string` vs `String` vs `"abc"` — explain.
A5: `string` is the primitive type. `String` is the interface of the wrapper object (and `new String()` type); primitives are assignable to it but not vice-versa — avoid it. `"abc"` is a literal type, a subtype of `string`, used for unions like `"PLACED" | "SHIPPED"`.

---

## 🔷 When to Use + When Not to Use
✅ Use:
- `number` for paise, counts, page numbers (integers within safe range)
- `string` for IDs, enums-as-strings, ISO date strings in JSON
- `bigint` for DB `BIGINT` IDs, crypto, huge counters; `symbol` for private keys/brands in libraries

❌ Avoid:
- `number` for money with decimals, or for IDs above 2^53
- `bigint` in Redux state / JSON responses without converting to string
- Wrapper types `String`, `Number`, `Boolean`, `Object`

---

## 📊 Visual Diagram
```
 PRIMITIVES                       ESCAPE / SPECIAL
 ───────────────────────          ─────────────────────
 string   "SW-1" `x${y}`          any     (checker off)
 number   49950  1.5  NaN         unknown (safe any)
 boolean  true | false            never   (no value)
 bigint   9007199254740993n       void    (no return value)
 symbol   Symbol("id")            null / undefined

  const s = "A"   ──► type "A"      (literal)
  let   s = "A"   ──► type string   (widened)

  number ──✕──► bigint   (never mixed in arithmetic)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Primitive | Immutable basic value type | Immutable बुनियादी value type |
| Literal type | Exact value as a type (`"A"`, `42`) | Exact value ही type |
| Widening | `let x = "a"` becomes `string` | Literal का general type बनना |
| bigint | Arbitrary-size integer type | बहुत बड़े integers का type |
| unique symbol | Symbol type unique to one const | एक const का अपना unique symbol type |
| Wrapper object | `String`/`Number` object types | `String`/`Number` object types |
| NaN | Not-a-Number, still typeof number | "Number नहीं" पर typeof number |

---

## ⚡ 3-Line Summary
English:
1. Use lowercase `string`, `number`, `boolean`, `bigint`, `symbol`; never `String`/`Number`.
2. Keep money as integer paise; use `bigint` (or string) for IDs beyond 2^53 and convert to string for JSON/Redux.
3. `const` keeps literal types, `let` widens — and `bigint` never mixes with `number`.

Hindi:
1. Lowercase `string`, `number`, `boolean`, `bigint`, `symbol` इस्तेमाल करो; `String`/`Number` कभी नहीं।
2. पैसा integer paise में रखो; 2^53 से बड़े IDs के लिए `bigint` (या string) लो और JSON/Redux के लिए string बनाओ।
3. `const` literal type रखता है, `let` उसे widen करता है — और `bigint` कभी `number` से नहीं मिलता।

---

## ➡️ Next Topic
**006. any vs unknown vs never vs void** — the special types that sit at the top and bottom of the type system.
