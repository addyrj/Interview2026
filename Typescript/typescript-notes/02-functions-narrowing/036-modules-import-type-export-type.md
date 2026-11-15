# 36. Modules, import type and export type
# हिंदी में: Modules, import type और export type

> Verified with **TypeScript 5.x** (compiled with 5.9, `--strict`). Feature versions: `import type` / `export type` = **TS 3.8**, inline `import { type X }` = **TS 4.5**, `verbatimModuleSyntax` = **TS 5.0**, `export type * from` = **TS 5.0**.

---

## 🔵 Simple Definition (English)
In TypeScript, **any file with a top-level `import` or `export` is a module** (its declarations are private to the file). Types and values live in separate "worlds": `interface`/`type` exist only at compile time, `class`/`enum`/`const` exist at runtime too. **`import type`** and **`export type`** explicitly say "this is types only — erase it from the JavaScript output".

## 🔵 सरल परिभाषा (Hindi)
TypeScript में **जिस file में top-level `import` या `export` हो वह एक module है** (उसकी declarations file तक private रहती हैं)। Types और values अलग "दुनिया" में रहते हैं: `interface`/`type` सिर्फ compile time पर होते हैं, `class`/`enum`/`const` runtime पर भी होते हैं। **`import type`** और **`export type`** साफ बताते हैं: "यह सिर्फ types है — JavaScript output से हटा दो"।

---

## 🔴 Problem it Solves
1. **Runtime cost / circular imports:** `import { Order } from "./order"` where `Order` is only an interface used to be silently erased, but bundlers/transpilers that compile one file at a time (esbuild, swc, Babel, `tsx`, Vite) **cannot know** whether `Order` is a type or a value. They either keep a useless import (and crash with "does not provide an export named Order") or break circular dependencies.
2. **Side effects:** a stray import can run a module's top-level code (DB connect, polyfills) just to get a type.
3. **Clarity:** reader sees at a glance which imports are real dependencies.

## 🔴 यह क्यों बना? (Hindi)
1. **Runtime cost / circular imports:** `import { Order } from "./order"` में `Order` सिर्फ interface हो तो पहले चुपचाप हट जाता था, लेकिन एक-एक file compile करने वाले tools (esbuild, swc, Babel, `tsx`, Vite) को **पता नहीं चलता** कि `Order` type है या value। वे बेकार import रख लेते हैं (और "does not provide an export named Order" से crash) या circular dependency बिगाड़ देते हैं।
2. **Side effects:** सिर्फ type के लिए import करने पर module का top-level code (DB connect, polyfill) चल सकता है।
3. **Clarity:** पढ़ने वाले को तुरंत दिखता है कि कौन से imports असली dependency हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → A file with `import`/`export` is a module; otherwise it is a global script.
Step 2 → `export` marks what is public. Types: `export interface/type`; values: `export const/function/class`.
Step 3 → `import type { Order } from "./types"` — can be used **only in type positions**; the whole statement is deleted from emitted JS.
Step 4 → Inline form: `import { PaymentError, type Order } from "./types"` — keeps the value import, erases the type specifier (TS 4.5).
Step 5 → `export type { Order } from "./types"` re-exports a type safely (needed under `isolatedModules`).
Step 6 → Turn on `"verbatimModuleSyntax": true` (TS 5.0): imports without `type` are **kept exactly**, type-only imports **must** say `type`. This replaces `importsNotUsedAsValues` / `preserveValueImports`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → जिस file में `import`/`export` हो वह module है; वरना global script।
Step 2 → `export` से तय होता है क्या public है। Types: `export interface/type`; values: `export const/function/class`।
Step 3 → `import type { Order } from "./types"` — सिर्फ **type positions** में इस्तेमाल हो सकता है; पूरा statement emitted JS से हट जाता है।
Step 4 → Inline form: `import { PaymentError, type Order } from "./types"` — value import रहता है, type वाला हिस्सा हट जाता है (TS 4.5)।
Step 5 → `export type { Order } from "./types"` से type को सुरक्षित re-export करो (`isolatedModules` में ज़रूरी)।
Step 6 → `"verbatimModuleSyntax": true` ऑन करो (TS 5.0): बिना `type` वाले imports **जैसे-के-तैसे रहते** हैं, type-only imports पर `type` लिखना **ज़रूरी** है। यह `importsNotUsedAsValues` / `preserveValueImports` की जगह लेता है।

---

## 🟡 Real World Example
**Paytm-style payments repo**: `payments/types.ts` has `PaymentRequest` (interface) and `PaymentError` (class). The React checkout app imports `PaymentRequest` only for props typing — with `import type` the bundle never pulls in the Node-only server code that lives next to it. The API's `index.ts` re-exports a public surface with `export type { PaymentRequest }` and `export { PaymentError }`, so consumers get a clean, tree-shakeable entry point.

## 🟡 Real Example Hindi mein
**Paytm जैसा payments repo**: `payments/types.ts` में `PaymentRequest` (interface) और `PaymentError` (class) है। React checkout app `PaymentRequest` सिर्फ props typing के लिए import करता है — `import type` से bundle में उसके पास रखा Node-only server code नहीं आता। API का `index.ts` `export type { PaymentRequest }` और `export { PaymentError }` से public surface re-export करता है, जिससे consumers को साफ, tree-shakeable entry point मिलता है।

---

## 💻 Code Example — Basic

```typescript
// Type-only import: Server is only used as a type annotation
import type { Server } from "node:http"; // erased from JS output
// Value import: createServer is real runtime code
import { createServer } from "node:http"; // kept in JS output

function describe(s: Server): string { // Server used only in a type position
  return s.listening ? "listening" : "idle"; // runtime property check
}

const server = createServer(); // value usage
console.log(describe(server)); // never started, so idle
// Output:
// idle
```

```typescript
// file: order/types.ts
export interface Order { id: string; total: number } // type only (erased)
export type OrderId = Order["id"];                    // type alias (erased)
export class PaymentError extends Error {             // real class (kept)
  constructor(public readonly code: string, message: string) { super(message); }
}
```

```typescript
// file: order/service.ts
import { PaymentError, type Order } from "./types"; // inline type modifier (TS 4.5)
import type { OrderId } from "./types";             // whole statement is type-only

export function charge(order: Order): OrderId {
  if (order.total <= 0) throw new PaymentError("E_AMOUNT", "Amount must be positive"); // value use
  return order.id; // returns the OrderId type
}

export type { Order } from "./types"; // re-export a type safely
export { PaymentError };               // re-export a value
```

## 💻 Code Example — Advanced

```typescript
// file: order/index.ts  (a "barrel" file)
export type { Order, OrderId } from "./types"; // types: erased fully
export { PaymentError } from "./types";          // class = value, so a normal re-export
// NOTE: `export type * from "./types"` (TS 5.0) would ALSO make PaymentError type-only (TS1362)
export { charge } from "./service";      // real function re-export
export * as pricing from "./pricing";    // namespace re-export (value)
```

```typescript
// file: order/pricing.ts
export const GST_RATE = 0.18; // constant exported as a value
export const withGst = (amount: number): number => Math.round(amount * (1 + GST_RATE)); // helper
```

```typescript
// file: order/usage.ts
import { charge, pricing, type Order, PaymentError } from "./index"; // mix of values + types

const order: Order = { id: "o-7", total: pricing.withGst(100) }; // 118
try {
  console.log(charge(order)); // prints the id
} catch (e) {
  // narrow unknown errors with instanceof (class exists at runtime)
  if (e instanceof PaymentError) console.error(e.code);
}
```

```typescript
// Dynamic import is typed too: the result is a Promise of the module namespace
async function loadPricing() {
  const mod = await import("./order/pricing"); // type: typeof import("./order/pricing")
  return mod.withGst(200); // 236
}
loadPricing().then((v) => console.log(v));
// Output:
// 236
```

---

## 🟠 Node/Express + React Integration

```typescript
// file: api/routes.ts  (Express server: types come from express, runtime from our code)
import type { Request, Response } from "express"; // types only => no extra runtime import
import { Router } from "express";                  // value: we call Router()
import { charge, type Order } from "../order";      // value + inline type

export const router = Router(); // real Express router

router.post("/pay", (req: Request<unknown, unknown, Order>, res: Response) => {
  const id = charge(req.body); // body typed as Order
  res.json({ paid: id });
});
```

```tsx
// file: web/PayButton.tsx  (React: only types are imported from the server package)
import type { Order } from "../order"; // erased: no server code lands in the browser bundle

export function PayButton({ order }: { order: Order }) {
  // We only need the shape for props; fetch does the real work
  return <button onClick={() => fetch("/pay", { method: "POST", body: JSON.stringify(order) })}>Pay</button>;
}
```

**Redux note:** keep `RootState`/`AppDispatch` as `export type` in `store.ts` and import them with `import type` in components, so the store file is not pulled into leaf components (avoids circular imports store -> slice -> component -> store).

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: Using a `import type` binding as a value.**

```typescript
// file: bad-use.ts
// ❌ PaymentError is a class (a value) but was imported as type-only
import type { PaymentError } from "./order/types";
const e = new PaymentError("E1", "fail"); // wrong: used with `new` (value position)
// error TS1361: 'PaymentError' cannot be used as a value because it was imported using 'import type'.
```

```typescript
// file: good-use.ts
import { PaymentError } from "./order/types"; // normal import: class is a value
const e = new PaymentError("E1", "fail");       // ok
console.log(e.code);
```

**Mistake 2: Re-exporting a type without `export type` under `isolatedModules` / `verbatimModuleSyntax`.**

```typescript
// file: reexport-bad.ts
// ❌ With "isolatedModules": true (Vite/esbuild/swc projects)
export { Order } from "./order/types"; // wrong: transpiler cannot tell Order is a type
// error TS1205: Re-exporting a type when 'isolatedModules' is enabled requires using 'export type'.
```

```typescript
// file: reexport-good.ts
export type { Order } from "./order/types"; // ok: explicitly a type, erased
```

**Mistake 3 (verbatimModuleSyntax):** `import { Order } from "./types"` where `Order` is an interface gives `error TS1484: 'Order' is a type and must be imported using a type-only import when 'verbatimModuleSyntax' is enabled.` Fix: `import type { Order }` or `import { type Order }`.

*(Messages for mistakes 2 and 3 were produced by running `tsc --isolatedModules` and `tsc --verbatimModuleSyntax` on those exact lines; the default `--strict` run does not enable those flags.)*

---

## 🧠 Tricky Interview Question

```typescript
import { type Order } from "./order/types";
// Does this line leave an import in the emitted JavaScript?
```
**Answer:** It depends on the flag. With the default settings, all specifiers are `type`, so the import is elided. With **`verbatimModuleSyntax: true`** the statement is **kept as a side-effect import** (`import {} from "./order/types"`), because that flag preserves every import that is not a *top-level* `import type`. To drop it fully write `import type { Order } from "./order/types"`. This is why `import type {..}` (statement-level) and `import { type ..}` (specifier-level) are not always identical.

---

## ⚫ Interview Questions + Answers

**Q1: What makes a file a module in TypeScript?**
A1: A top-level `import` or `export`. Without it, the file is a global script and its declarations leak into the global scope (the reason `export {}` is used to force module-ness).

**Q2: Difference between `import type` and a normal import?**
A2: `import type` is erased and can only be used in type positions; a normal import may be kept in JS and can be used as a value. For classes/enums, a type-only import can still be used as a *type annotation* but not with `new`/`instanceof`.

**Q3: Why do esbuild/Vite/swc projects need `isolatedModules`?**
A3: They transpile each file alone without type information, so they cannot know if an imported name is a type. `isolatedModules` makes TS flag constructs that need cross-file knowledge (e.g. re-exporting a type without `export type`, TS1205).

**Q4: What does `verbatimModuleSyntax` do (TS 5.0)?**
A4: Imports/exports are emitted exactly as written unless marked `type`. It forces explicit `import type` and also errors on `import x = require()` in ESM output. It replaces `importsNotUsedAsValues` and `preserveValueImports`.

**Q5: What is `export type * from "./x"`?**
A5: TS 5.0 syntax to re-export all types from a module in a barrel file and guarantee nothing is emitted at runtime. Plain `export *` can drag in runtime code.

---

## 🔷 When to Use + When Not to Use
✅ Use `import type` when:
- The import is only used for annotations (props, DTOs, Redux `RootState`)
- Avoiding circular dependencies or pulling server code into the browser bundle
- Your toolchain is `isolatedModules` based (Vite, esbuild, swc, tsx)

❌ Don't bother when:
- The imported name is a class/enum you also use at runtime (use a normal import)
- Old TS (< 3.8) — use plain imports and rely on elision

---

## 📊 Visual Diagram
```
 source                                   emitted JS
 ─────────────────────────────────       ─────────────────────────
 import type { Order } from "./t"   ──►   (nothing)
 import { PaymentError, type Order }──►   import { PaymentError } from "./t"
 import { Order } from "./t"        ──►   elided by tsc, but UNKNOWN to esbuild
                                           (so use `type`, or verbatimModuleSyntax errors)
 export type { Order } from "./t"   ──►   (nothing)
 export { PaymentError } from "./t" ──►   export { PaymentError } from "./t"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Module | File with top-level import/export | Import/export वाली file |
| import type | Type-only import, erased | सिर्फ type import, हटा दिया जाता है |
| export type | Type-only (re)export | सिर्फ type export |
| isolatedModules | Each file must be transpilable alone | हर file अकेले compile हो सके |
| verbatimModuleSyntax | Emit imports exactly as written (TS 5.0) | Imports जैसे लिखे वैसे emit |
| Barrel file | index.ts that re-exports others | Re-export करने वाली index file |

---

## ⚡ 3-Line Summary
English:
1. A file with top-level import/export is a module; types vanish at runtime, values do not.
2. Use `import type` / `export type` (and `import { type X }`) for type-only usage to avoid runtime imports and cycles.
3. Enable `verbatimModuleSyntax` (TS 5.0) or `isolatedModules` for esbuild/Vite/swc-based builds.

Hindi:
1. Top-level import/export वाली file module होती है; types runtime पर गायब होते हैं, values नहीं।
2. सिर्फ type के लिए `import type` / `export type` (और `import { type X }`) इस्तेमाल करो — runtime import और cycles से बचाव।
3. esbuild/Vite/swc builds के लिए `verbatimModuleSyntax` (TS 5.0) या `isolatedModules` ऑन करो।

---

## ➡️ Next Topic
**37. Namespaces vs ES Modules** — the legacy `namespace` keyword, when it still matters, and why ES modules replaced it.
