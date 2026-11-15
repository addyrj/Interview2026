# 1. What is TypeScript + Why Use It
# हिंदी में: TypeScript क्या है और इसे क्यों इस्तेमाल करें

> Version note: इस पूरे note के सारे code **TypeScript 5.x** (5.9.3 पर verify किया गया) और `--strict` mode में compile होते हैं।

---

## 🔵 Simple Definition (English)
**TypeScript** is a **typed superset of JavaScript** built by Microsoft. Every valid JavaScript file is already valid TypeScript, but TypeScript adds an optional **static type system** on top. You write types, the **compiler (`tsc`)** checks them *before* the code runs, and then it **erases** the types and emits plain JavaScript that runs in the browser or Node.js. Types exist only at compile time; at runtime there is nothing of them left.

## 🔵 सरल परिभाषा (Hindi)
**TypeScript** Microsoft का बनाया हुआ JavaScript का **typed superset** है। हर valid JavaScript file पहले से valid TypeScript है, लेकिन TypeScript उसके ऊपर एक optional **static type system** जोड़ देता है। आप types लिखते हैं, **compiler (`tsc`)** code चलने से *पहले* ही उन्हें check कर लेता है, और फिर types को **हटाकर (erase)** सादा JavaScript बना देता है जो browser या Node.js में चलता है। Types सिर्फ compile time पर होते हैं; runtime पर उनका कोई निशान नहीं बचता।

---

## 🔴 Problem it Solves
JavaScript is dynamically typed. A typo like `order.totl` or passing `"499"` where a number is expected is not caught until that exact line runs in production — often as `undefined is not a function` or a silently wrong total (`"499" + 50 = "49950"`). In a 8-10 year career you have seen this: a refactor renames a field in an Express response and three React screens break only when a user opens them. TypeScript moves these bugs from **runtime (customer sees it)** to **compile time (your editor shows red underline)**. It also gives IDE autocomplete, safe refactoring (rename symbol across 500 files) and self-documenting function signatures.

## 🔴 यह क्यों बना? (Hindi)
JavaScript dynamically typed है। `order.totl` जैसा typo या number की जगह `"499"` pass कर देना तब तक पकड़ में नहीं आता जब तक वही line production में चल न जाए — तब `undefined is not a function` या चुपचाप गलत total (`"499" + 50 = "49950"`) मिलता है। Express response का एक field rename करने पर तीन React screens तभी टूटती हैं जब user उन्हें खोलता है। TypeScript इन bugs को **runtime (customer को दिखता है)** से हटाकर **compile time (editor में लाल लकीर)** पर ले आता है। साथ में IDE autocomplete, safe refactoring (500 files में symbol rename) और self-documenting function signatures भी मिलते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → You write `.ts` / `.tsx` files with type annotations (`price: number`).
Step 2 → The TypeScript compiler **parses** the code into an AST (syntax tree).
Step 3 → The **type checker** walks the tree, infers/validates types, and reports errors (`TS2322`, `TS2339`...).
Step 4 → The **emitter** removes all type syntax and writes `.js` (optionally `.d.ts` and source maps), downleveling syntax to the `target` you chose.
Step 5 → The `.js` runs on Node.js / browser. **Types do not exist anymore** — so untrusted input (HTTP body, DB row) still needs runtime validation (Zod).

Important: type errors do **not** stop emit by default (unless `noEmitOnError`). Tools like Vite/esbuild/tsx only strip types and never type-check; `tsc --noEmit` in CI is the real gate.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → आप `.ts` / `.tsx` files लिखते हैं type annotations के साथ (`price: number`)।
Step 2 → TypeScript compiler code को **parse** करके AST (syntax tree) बनाता है।
Step 3 → **Type checker** tree पर चलता है, types infer/validate करता है और errors (`TS2322`, `TS2339`...) बताता है।
Step 4 → **Emitter** सारा type syntax हटाकर `.js` लिखता है (चाहें तो `.d.ts` और source maps भी), और syntax को आपके चुने `target` के हिसाब से downlevel करता है।
Step 5 → `.js` Node.js / browser में चलता है। **अब types मौजूद नहीं हैं** — इसलिए बाहर से आने वाले data (HTTP body, DB row) की runtime validation (Zod) अभी भी ज़रूरी है।

ज़रूरी बात: default में type error होने पर भी JS emit हो जाता है (जब तक `noEmitOnError` न हो)। Vite/esbuild/tsx सिर्फ types हटाते हैं, check नहीं करते; असली gate CI में `tsc --noEmit` है।

---

## 🟡 Real World Example
**Razorpay's checkout SDK** is used by thousands of merchants. If `amount` is expected in **paise** (integer) but a merchant passes `"499.50"` (string rupees), the payment either fails or charges the wrong amount. With TypeScript typings (`amount: number`), the merchant's editor flags it the moment they type it. Same story inside a company: a Swiggy order service returns `{ orderId, totalPaise, status }`; when the backend team renames `totalPaise` to `grandTotalPaise`, every consumer fails to compile until fixed — instead of showing "NaN" to users on Friday night.

## 🟡 Real Example Hindi mein
**Razorpay का checkout SDK** हज़ारों merchants इस्तेमाल करते हैं। अगर `amount` **paise** (integer) में चाहिए और merchant `"499.50"` (string rupees) भेज दे, तो payment fail होगा या गलत amount कटेगा। TypeScript typings (`amount: number`) हों तो merchant का editor उसी पल गलती दिखा देता है। Company के अंदर भी यही होता है: Swiggy का order service `{ orderId, totalPaise, status }` लौटाता है; backend team `totalPaise` को `grandTotalPaise` बनाए तो हर consumer तब तक compile नहीं होगा जब तक fix न हो — Friday रात users को "NaN" दिखने की जगह।

---

## 💻 Code Example — Basic

```typescript
// basic-order.ts — typed data + typed function
// Compiles under: tsc --noEmit --strict (TypeScript 5.x)

// Describe the SHAPE of an order (exists only at compile time)
interface Order {
  orderId: string;      // unique id like "SW-1001"
  items: string[];      // list of dish names
  totalPaise: number;   // money in paise (integer) to avoid float bugs
  status: "PLACED" | "DELIVERED"; // only these two strings are allowed
}

// Function takes an Order and returns a string; both are type-checked
function summary(order: Order): string {
  // Template literal: types of every part are known to the compiler
  return `${order.orderId}: ${order.items.length} items, Rs ${order.totalPaise / 100}`;
}

// An object literal that matches the Order shape
const order: Order = {
  orderId: "SW-1001",                      // string OK
  items: ["Paneer Tikka", "Butter Naan"],  // string[] OK
  totalPaise: 49950,                       // number OK
  status: "PLACED",                        // one of allowed literals OK
};

// Prints: SW-1001: 2 items, Rs 499.5
console.log(summary(order));
```

Now the same idea when you make a mistake. These are **intentional errors** with the **real compiler output**:

```typescript
// ❌ intentional errors — real tsc 5.9 output is in the comments
interface Order {
  orderId: string;
  totalPaise: number;
}

const order: Order = { orderId: "SW-1002", totalPaise: 49950 };

// ❌ Typo in property name
console.log(order.totl);
// error TS2339: Property 'totl' does not exist on type 'Order'.

// ❌ Wrong argument type
function addGst(paise: number): number {
  return Math.round(paise * 1.05); // 5% GST
}
addGst("499");
// error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.
```

## 💻 Code Example — Advanced

```typescript
// advanced-why-ts.ts — types erase at runtime, so check the boundary
// This file shows WHY "TypeScript is not enough": the compiler trusts what you tell it.

// 1) A type for what we EXPECT from the API
interface PaymentResponse {
  paymentId: string;                    // Razorpay-like id
  status: "captured" | "failed";        // allowed statuses
  amountPaise: number;                  // amount in paise
}

// 2) A lie: JSON.parse returns any, so assigning it to PaymentResponse is NOT checked
const raw = '{"paymentId":"pay_9","status":"refunded","amountPaise":"oops"}';
const unsafe: PaymentResponse = JSON.parse(raw); // compiles! but data is wrong
console.log(unsafe.status === "captured");       // false -- but TS thinks status is only captured|failed

// 3) An honest approach: take unknown and narrow it at runtime
function isPaymentResponse(v: unknown): v is PaymentResponse {
  if (typeof v !== "object" || v === null) return false;   // must be an object
  const o = v as Record<string, unknown>;                  // view as a bag of unknowns
  return (
    typeof o.paymentId === "string" &&                     // paymentId must be string
    (o.status === "captured" || o.status === "failed") &&  // status must be allowed literal
    typeof o.amountPaise === "number"                      // amount must be a number
  );
}

const parsed: unknown = JSON.parse(raw);                   // unknown forces us to check first
if (isPaymentResponse(parsed)) {
  console.log("valid", parsed.paymentId);                  // safe here
} else {
  console.log("invalid payment payload");                  // our raw data lands here
}
// Output: false
//         invalid payment payload
```

---

## 🟠 Node/Express + React Integration

**Backend (Express) — typed handler:**

```typescript
// server.ts — Express with types (npm i express; npm i -D @types/express)
import express, { Request, Response } from "express";

// Shared contract: same interface can be imported by the React app
export interface OrderDto {
  orderId: string;
  totalPaise: number;
}

const app = express();           // create the app
app.use(express.json());         // parse JSON bodies

// Response<OrderDto> makes res.json() check the shape we send
app.get("/api/orders/:id", (req: Request<{ id: string }>, res: Response<OrderDto>) => {
  const dto: OrderDto = { orderId: req.params.id, totalPaise: 49950 }; // req.params.id is string
  res.json(dto);                 // wrong shape here would be a compile error
});

export default app;              // export so tests can import without listening
```

**Frontend (React + Redux Toolkit) — same contract:**

```tsx
// OrderCard.tsx — props are typed, so wrong usage fails at compile time
import type { OrderDto } from "./server";   // type-only import: erased at runtime

// Props type: what the parent must pass
type Props = { order: OrderDto };

// Function component returning JSX
export function OrderCard({ order }: Props) {
  // order.totalPaise is number -> division is safe
  return <p>{order.orderId}: Rs {order.totalPaise / 100}</p>;
}
// <OrderCard order={{ orderId: "A" }} /> would fail: Property 'totalPaise' is missing
```

Takeaway: one `OrderDto` shared between Express and React means a backend rename breaks the frontend **build**, not the user's screen. (Types are still erased — validate the network response with Zod, see topic 086.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Thinking types exist at runtime
```typescript
// ❌ Wrong — Order is an interface, it is erased and cannot be used as a value
interface Order { orderId: string }
const x: unknown = { orderId: "A" };
if (x instanceof Order) { /* ... */ }
// error TS2693: 'Order' only refers to a type, but is being used as a value here.
```
```typescript
// ✅ Right — check the shape at runtime with a type guard (or Zod)
interface Order { orderId: string }
function isOrder(x: unknown): x is Order {
  return typeof x === "object" && x !== null && typeof (x as Order).orderId === "string";
}
console.log(isOrder({ orderId: "A" })); // true
```

❌ Mistake 2: Using `any` everywhere "just to make it compile"
```typescript
// ⚠️ Wrong (compiles, but unsafe) — any switches the checker OFF, so typos pass silently
const order: any = { orderId: "A", totalPaise: 100 };
console.log(order.totl); // compiles fine, prints undefined at runtime
```
✅ Correct: describe the shape (`interface Order`) or use `unknown` and narrow. `any` should be a rare, deliberate escape hatch.

❌ Mistake 3: Assuming a green editor means a green build — Vite/esbuild/tsx **do not type-check**. Run `tsc --noEmit` in CI.

---

## 🧠 Tricky Interview Question

```typescript
interface User { name: string }
const data = JSON.parse('{"name": 42}') as User;
console.log(typeof data.name);
```
**Question:** Does this compile? What does it print?

**Answer:** It compiles cleanly and prints `number`. `JSON.parse` returns `any`; the `as User` assertion only tells the compiler "trust me" — it generates **no runtime check** (types are erased). So the declared type `string` is a lie. This is exactly why API boundaries need runtime validation (Zod/io-ts) and why `as` is dangerous. TypeScript is **unsound by design** in some places for pragmatism.

---

## ⚫ Interview Questions + Answers

Q1: What is TypeScript and does the browser run it?
A1: TypeScript is a typed superset of JavaScript. Browsers and Node cannot run it directly (Node 22+ can strip types experimentally, and Deno/Bun run it natively, but standard practice is compile first). `tsc` (or esbuild/swc) converts it to JavaScript; types are erased.

Q2: Name the main benefits of TypeScript in a large codebase.
A2: (1) Catches bugs at compile time, (2) rich IDE autocomplete and navigation, (3) safe large-scale refactors, (4) types act as living documentation, (5) shared contracts between frontend and backend (monorepo), (6) enables newer JS syntax downleveled to old targets.

Q3: If TypeScript has types, why do we still need Zod/validation?
A3: Types are erased at runtime. Data from outside your program (HTTP body, localStorage, DB rows, third-party API) is untrusted and the compiler cannot verify it. Zod validates at runtime and `z.infer` gives the static type from the same schema, so both stay in sync.

Q4: Is TypeScript statically or dynamically typed? Strongly or weakly?
A4: Statically typed (checked before running) with **structural** typing (shape matters, not names). It is gradually typed — `any` lets you opt out — and intentionally not 100% sound (e.g. type assertions, array index access without `noUncheckedIndexedAccess`).

Q5: Does a TypeScript error stop the JavaScript from being generated?
A5: Not by default. `tsc` still emits JS unless `noEmitOnError: true`. Bundlers like Vite/esbuild/swc never type-check at all; they only strip types. So enforce correctness with `tsc --noEmit` in CI and editor.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Team project, long-lived code, many contributors (React + Node + shared DTOs)
- Public libraries/SDKs where consumers need good autocomplete (Razorpay-style)
- Refactor-heavy domains: payments, orders, inventory

❌ Avoid / go light when:
- Tiny throwaway script or a 20-line prototype (JSDoc `// @ts-check` may be enough)
- Team has no time to learn it AND the project is short-lived
- Never rely on it as security/validation — it is erased at runtime

---

## 📊 Visual Diagram
```
 order.ts (TypeScript)              compile time                   runtime
┌──────────────────────┐   ┌─────────────────────────────┐   ┌───────────────┐
│ price: number        │──▶│ Parse -> Type check -> Emit │──▶│ order.js      │
│ order.totl  (typo)   │   │   ❌ TS2339 shown here      │   │ (no types!)   │
└──────────────────────┘   └─────────────────────────────┘   └───────────────┘
                                   types live HERE only         Node / Browser
                                                             Zod validates data HERE
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Superset | Includes all of JS plus extra features | JS के सब features + कुछ extra |
| Static typing | Types checked before the program runs | Program चलने से पहले types की जाँच |
| Type erasure | Types removed from emitted JS | Emit हुए JS से types हट जाना |
| tsc | The TypeScript compiler CLI | TypeScript compiler command |
| Structural typing | Compatibility by shape, not name | नाम नहीं, shape से compatibility |
| Type checker | Part of compiler that finds type errors | Compiler का हिस्सा जो type errors ढूँढता है |
| Runtime validation | Checking real data while running (Zod) | चलते समय असली data की जाँच |

---

## ⚡ 3-Line Summary
English:
1. TypeScript = JavaScript + a static type system; `tsc` checks types, then erases them and emits plain JS.
2. It moves bugs from production runtime to compile time and gives autocomplete + safe refactors.
3. Types vanish at runtime, so validate untrusted input (Zod) and run `tsc --noEmit` in CI.

Hindi:
1. TypeScript = JavaScript + static type system; `tsc` types check करता है, फिर उन्हें हटाकर सादा JS बनाता है।
2. यह bugs को production runtime से compile time पर ले आता है और autocomplete + safe refactor देता है।
3. Runtime पर types नहीं रहते, इसलिए बाहरी input को Zod से validate करो और CI में `tsc --noEmit` चलाओ।

---

## ➡️ Next Topic
**002. TypeScript vs JavaScript** — side-by-side comparison: what changes in syntax, tooling, runtime behaviour and team workflow.
