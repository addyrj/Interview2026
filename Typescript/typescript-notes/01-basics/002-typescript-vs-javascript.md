# 2. TypeScript vs JavaScript
# हिंदी में: TypeScript बनाम JavaScript

> Version note: सारे code **TypeScript 5.x** (5.9.3 पर verify) और `--strict` में compile होते हैं।

---

## 🔵 Simple Definition (English)
**JavaScript (JS)** is the dynamically typed language that runs natively in browsers and Node.js; types are checked **while running**. **TypeScript (TS)** is JavaScript **plus** a static type system and a few extra constructs (`enum`, `interface`, generics, decorators); types are checked **before running** by `tsc`, then erased. TS never runs by itself — it always becomes JS first. So the real comparison is *"JS with a safety net at build time"* versus *"JS without it"*.

## 🔵 सरल परिभाषा (Hindi)
**JavaScript (JS)** dynamically typed language है जो browsers और Node.js में सीधे चलती है; types की जाँच **चलते समय** होती है। **TypeScript (TS)** JavaScript **के ऊपर** static type system और कुछ extra constructs (`enum`, `interface`, generics, decorators) जोड़ता है; types की जाँच `tsc` **चलाने से पहले** करता है और फिर types हटा देता है। TS खुद कभी नहीं चलता — पहले हमेशा JS में बदलता है। इसलिए असली तुलना है: *"build time पर safety net वाला JS"* बनाम *"बिना safety net का JS"*।

---

## 🔴 Problem it Solves
Teams often ask "why add a build step and learn types when JS works?" The honest answer is **scale and change**. In a 5-file script, JS is faster to write. In a codebase with 400 React components, 120 Express routes and a SQL Server schema, the cost is not *writing* code but *changing* it safely. JS gives no signal when a function signature changes; TS lists every broken call site. TS also solves the "what does this function accept?" problem without reading its body or running it.

## 🔴 यह क्यों बना? (Hindi)
Teams पूछती हैं "JS चल तो रहा है, फिर build step और types क्यों?" सच्चा जवाब है **scale और बदलाव**। 5 files की script में JS लिखना तेज़ है। लेकिन 400 React components, 120 Express routes और SQL Server schema वाले codebase में खर्च *लिखने* का नहीं, उसे *सुरक्षित बदलने* का है। Function का signature बदलने पर JS कोई संकेत नहीं देता; TS हर टूटा हुआ call site गिना देता है। TS "यह function क्या लेता है?" का जवाब बिना body पढ़े या चलाए दे देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Rename `app.js` to `app.ts` — it still works because JS is valid TS (with `allowJs`/`checkJs` you can migrate gradually).
Step 2 → Add annotations: `function pay(amount: number): boolean`.
Step 3 → `tsc` type-checks. In JS the same bug would surface only at runtime.
Step 4 → TS-only syntax (`interface`, `type`, `: number`, `as`, generics `<T>`) is erased. A few TS features DO emit code: `enum`, `namespace`, parameter properties, decorators.
Step 5 → Run the emitted JS. Runtime semantics (event loop, `==`, `this`, prototypes) are **identical** — TS changes nothing at runtime.

Comparison table:
- Typing: JS dynamic / TS static (structural)
- Errors found: JS at runtime / TS at compile time + runtime
- Run directly: JS yes / TS no (needs tsc, tsx, esbuild, swc or Node type stripping)
- Tooling: JS basic / TS rich IntelliSense, refactor
- Learning curve: JS low / TS medium (generics, utility types)
- Runtime cost: both same — types are erased

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `app.js` का नाम `app.ts` करो — फिर भी चलेगा क्योंकि JS valid TS है (`allowJs`/`checkJs` से धीरे-धीरे migrate कर सकते हैं)।
Step 2 → Annotations जोड़ो: `function pay(amount: number): boolean`।
Step 3 → `tsc` type-check करता है। वही bug JS में सिर्फ runtime पर दिखता।
Step 4 → TS-only syntax (`interface`, `type`, `: number`, `as`, generics `<T>`) हट जाता है। कुछ TS features code **emit** करते हैं: `enum`, `namespace`, parameter properties, decorators।
Step 5 → Emit हुआ JS चलाओ। Runtime semantics (event loop, `==`, `this`, prototypes) **बिल्कुल वही** हैं — TS runtime में कुछ नहीं बदलता।

---

## 🟡 Real World Example
**Paytm's merchant dashboard** (React + Node) started as JavaScript. A backend engineer changed the settlement API from `amount` (rupees, string) to `amountPaise` (number). In JS nobody noticed; the "Today's Settlement" card showed `undefined` for a few hours. After migrating the shared API contract to TypeScript, the same rename produced 14 red errors in the frontend repo during the pull request, before merge. The runtime code is the same JS — only the **feedback loop** moved earlier.

## 🟡 Real Example Hindi mein
**Paytm के merchant dashboard** (React + Node) की शुरुआत JavaScript में हुई। Backend engineer ने settlement API का field `amount` (rupees, string) से बदलकर `amountPaise` (number) कर दिया। JS में किसी को पता नहीं चला; "Today's Settlement" card कुछ घंटे `undefined` दिखाता रहा। Shared API contract TypeScript में आने के बाद वही rename merge से पहले, pull request में ही frontend repo में 14 लाल errors दे देता है। Runtime code वही JS है — बस **feedback loop** पहले आ गया।

---

## 💻 Code Example — Basic

```typescript
// js-vs-ts-basic.ts — JS-style bugs that TypeScript refuses to compile
// (each line below would run in plain JS and fail or misbehave at runtime)

// 1) Variable keeps its type
let cartCount = 3;                 // inferred as number
console.log(cartCount + 1);        // 4

// 2) Safe version of the classic string-concat bug
const priceFromInput = "499";                 // value arrives as string (form input)
const priceNum = Number(priceFromInput);      // convert explicitly
console.log(priceNum + 50);                   // 549 (a JS "499" + 50 would give "49950")

// 3) Optional chaining + nullish coalescing work the same as in modern JS
const user: { name: string; address?: { city: string } } = { name: "Aditya" };
console.log(user.address?.city ?? "unknown"); // unknown
```

```typescript
// ❌ intentional errors — all of these are legal JavaScript! Real tsc 5.9 output below
let cartCount = 3;
cartCount = "three";
// error TS2322: Type 'string' is not assignable to type 'number'.

const total = "499" * 2;
// error TS2362: The left-hand side of an arithmetic operation must be of type 'any', 'number', 'bigint' or an enum type.

const user = { name: "Aditya" };
user.age = 30;
// error TS2339: Property 'age' does not exist on type '{ name: string; }'.

function pay(amount: number, upiId: string): string {
  return `${upiId} paid ${amount}`;
}
pay(499);
// error TS2554: Expected 2 arguments, but got 1.
```

## 💻 Code Example — Advanced

```typescript
// js-vs-ts-advanced.ts — what TS emits vs what it erases
// TS-only constructs (ERASED, zero runtime cost):
interface CartItem { sku: string; qty: number } // erased completely
type Cart = CartItem[];                         // erased completely

// Constructs that DO produce JavaScript output:
enum OrderStatus { Placed, Shipped, Delivered }  // becomes an IIFE-built object in JS

class PaymentService {
  // "parameter property": TS generates `this.gateway = gateway` for you
  constructor(private gateway: string) {}
  describe(): string { return `via ${this.gateway}`; }
}

const cart: Cart = [{ sku: "PIZZA-1", qty: 2 }];
console.log(cart.length);                    // 1
console.log(OrderStatus.Shipped);            // 1  (numeric enum -> real runtime object)
console.log(OrderStatus[1]);                 // Shipped (reverse mapping exists at runtime)
console.log(new PaymentService("razorpay").describe()); // via razorpay

// Runtime check that JS semantics are unchanged: == still coerces!
// TS only warns when types can't overlap; here both are number-compatible with `any`
const a: unknown = "5";
console.log(a == 5);                         // true  (JS coercion, TS does not alter it)
console.log(a === 5);                        // false

// Output:
// 1
// 1
// Shipped
// via razorpay
// true
// false
```

Emitted JS for the `enum` (shape only, `tsc --target ES2022`):
```javascript
var OrderStatus;
(function (OrderStatus) {
    OrderStatus[OrderStatus["Placed"] = 0] = "Placed";
    OrderStatus[OrderStatus["Shipped"] = 1] = "Shipped";
    OrderStatus[OrderStatus["Delivered"] = 2] = "Delivered";
})(OrderStatus || (OrderStatus = {}));
```
Note: with `erasableSyntaxOnly` (TS 5.8+) or Node's native type-stripping, `enum`, `namespace` and parameter properties are **not allowed** — one more reason many teams now prefer union types over enums.

---

## 🟠 Node/Express + React Integration

**Same Express app, JS vs TS:**

```typescript
// orders-route.ts — what a TS version buys you over orders-route.js
import express, { Request, Response } from "express";

const app = express();
app.use(express.json());

// JS: app.post("/orders", (req, res) => { const { qty } = req.body; ... })  -> qty could be anything
// TS: describe the body you EXPECT, so misuse is flagged in the handler
interface CreateOrderBody { sku: string; qty: number }

app.post("/orders", (req: Request<unknown, unknown, CreateOrderBody>, res: Response) => {
  const { sku, qty } = req.body;                  // typed: sku string, qty number
  const totalPaise = qty * 19900;                 // arithmetic is checked
  res.status(201).json({ sku, totalPaise });      // response built from typed values
});

export default app;                               // export for supertest, no listen here
```

**React: JS PropTypes vs TS props**

```tsx
// CartBadge.tsx — compile-time props instead of runtime PropTypes warnings
type CartBadgeProps = { count: number; label?: string }; // label optional

export function CartBadge({ count, label = "items" }: CartBadgeProps) {
  // count is number: count.toFixed would be fine, count.length would be an error
  return <span>{count} {label}</span>;
}
// <CartBadge count="3" /> -> error TS2322: Type 'string' is not assignable to type 'number'.
```
Note: remember the caveat from topic 001 — `req.body` types are a *promise*, not a check. Validate with Zod (topic 086).

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Believing TS changes runtime behaviour or adds runtime safety
```typescript
// ⚠️ Wrong assumption: "my types will reject a string here at runtime"
function addGst(paise: number): number { return paise * 1.05; }
const fromApi: any = "499";            // any sneaks past the checker
console.log(addGst(fromApi));          // 523.95 (JS coerces "499" * 1.05) - no TS protection
```
✅ Correct: types protect only code the compiler sees. Validate external data at the boundary.

❌ Mistake 2: Using `allowJs` and thinking JS files are now checked
✅ Correct: `allowJs` only lets `.js` files be part of the build. Add `checkJs: true` (or `// @ts-check` at file top) to actually type-check them.

❌ Mistake 3: Renaming everything to `.ts` and adding `any` to silence 2000 errors
✅ Correct: migrate in slices (see topic 080) — enable `strict` per folder, keep `any` count tracked in lint.

---

## 🧠 Tricky Interview Question

```typescript
// Is this a TS error? What does it print?
const prices: number[] = [10, 20, 30];
const idx = 5;
const p = prices[idx];
console.log(p.toFixed(2));
```
**Answer:** With default `--strict` it **compiles** (a "number" is assumed for `prices[5]`), but at runtime `p` is `undefined`, so it throws `TypeError: Cannot read properties of undefined (reading 'toFixed')`. TS is unsound here by design; enable **`noUncheckedIndexedAccess`** (not part of `strict`) to make `p` type `number | undefined`, which then forces a check. Lesson: TS reduces — does not eliminate — runtime errors.

---

## ⚫ Interview Questions + Answers

Q1: Is TypeScript faster or slower than JavaScript at runtime?
A1: Identical — the browser/Node runs the emitted JS and types are erased. The only cost is build/compile time. (Some TS-only features like `enum` generate a little extra code.)

Q2: Which JS features does TypeScript NOT add?
A2: TS never changes semantics: same event loop, same `this` rules, same number type. Features it adds are type-level (`interface`, generics, `as`, `satisfies`) plus a few emit-time extras (`enum`, `namespace`, decorators, parameter properties).

Q3: Can you gradually adopt TypeScript in a JS repo?
A3: Yes. Set `allowJs: true` (+ `checkJs` per file with `// @ts-check`), convert files one by one, start with leaf modules/shared types, and tighten `strict` flags progressively. Tools: `ts-migrate`, `typescript-eslint` `no-explicit-any` as warning.

Q4: What is structural typing and how is it different from JS's duck typing?
A4: Duck typing is a runtime habit ("if it has `.quack()`, call it"). TS structural typing formalises it at compile time: type compatibility depends on the **shape**, not the declared name, so any object with `{ id: string }` satisfies a type needing `{ id: string }`.

Q5: Why do many teams still choose JS + JSDoc for small libraries?
A5: No build step, direct debugging, and editors still give type hints from JSDoc with `checkJs`. Tradeoff: JSDoc syntax is clumsier for complex generics. Svelte and others moved this way; it is a valid choice, not a failure.

---

## 🔷 When to Use + When Not to Use
✅ Choose TS when:
- Multiple devs, long life, shared API contracts, frequent refactors
- Library or SDK consumed by others (ship `.d.ts`)
- Money/payments/inventory logic where a typo is expensive

❌ Choose plain JS when:
- Throwaway scripts, quick experiments, tiny CLI helpers
- Build tooling is impossible (e.g. a snippet pasted into a browser console)
- Team cannot invest in learning; consider JSDoc + `@ts-check` as the middle path

---

## 📊 Visual Diagram
```
        JavaScript                               TypeScript
 ┌────────────────────┐                  ┌──────────────────────────┐
 │ write code         │                  │ write code + types       │
 │        │           │                  │        │                 │
 │        ▼           │                  │        ▼                 │
 │ run  ──► 💥 bug    │                  │ tsc --noEmit ──► ❌ bug  │
 │ (customer sees it) │                  │ (developer sees it)      │
 └────────────────────┘                  │        │ fixed           │
                                         │        ▼                 │
                                         │ emit .js ──► run (same   │
                                         │ runtime as plain JS)     │
                                         └──────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dynamic typing | Types checked at runtime | Runtime पर types की जाँच |
| Static typing | Types checked before running | चलाने से पहले types की जाँच |
| Gradual typing | Mix typed and untyped code (`any`) | Typed और untyped code का मेल |
| allowJs / checkJs | Include / type-check JS files | JS files शामिल / check करना |
| Structural typing | Compatible if shapes match | Shape मिले तो compatible |
| Unsound | Type system can be fooled in some cases | कुछ जगह type system को धोखा दिया जा सकता है |
| noUncheckedIndexedAccess | Makes `arr[i]` possibly undefined | `arr[i]` को undefined संभव मानना |

---

## ⚡ 3-Line Summary
English:
1. TS = JS + static types; runtime behaviour and speed are identical because types are erased.
2. The win is an earlier feedback loop and safe refactoring, which matters most at scale.
3. TS is not runtime validation and is deliberately a bit unsound (`any`, `as`, array index) — know the gaps.

Hindi:
1. TS = JS + static types; runtime behaviour और speed बिल्कुल वही हैं क्योंकि types हट जाते हैं।
2. फायदा जल्दी मिलने वाला feedback और safe refactoring है, जो बड़े codebase में सबसे ज़्यादा काम आता है।
3. TS runtime validation नहीं है और जानबूझकर थोड़ा unsound है (`any`, `as`, array index) — इन gaps को जानो।

---

## ➡️ Next Topic
**003. Installing TypeScript + tsc + First Program** — install, run `tsc`, compile your first `.ts` file and read the output.
