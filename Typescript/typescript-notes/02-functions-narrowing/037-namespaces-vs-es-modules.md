# 37. Namespaces vs ES Modules
# हिंदी में: Namespaces बनाम ES Modules

> Verified with **TypeScript 5.x** (compiled with 5.9, `--strict`). `erasableSyntaxOnly` flag = **TS 5.8**. Namespaces are TS-specific (not part of JavaScript).

---

## 🔵 Simple Definition (English)
A **namespace** (older name: "internal module") is a TypeScript-only construct that groups related code under one name inside a file or across files: `namespace Pay { export function charge() {} }`. It compiles to an **IIFE** that attaches members to an object. **ES modules** (`import`/`export`) are the JavaScript standard way to organise code, with one file = one module scope. In modern code, **use ES modules**; keep `namespace` only for a few special cases (declaration files, merging, legacy code).

## 🔵 सरल परिभाषा (Hindi)
**Namespace** (पुराना नाम: "internal module") TypeScript का अपना construct है जो related code को एक नाम के नीचे group करता है: `namespace Pay { export function charge() {} }`। यह compile होकर एक **IIFE** बनता है जो members को एक object पर जोड़ता है। **ES modules** (`import`/`export`) JavaScript का standard तरीका है, जहाँ एक file = एक module scope। Modern code में **ES modules** इस्तेमाल करो; `namespace` सिर्फ कुछ special cases (declaration files, merging, legacy code) के लिए रखो।

---

## 🔴 Problem it Solves
Before ES2015 modules existed, JavaScript had a single global scope. Teams used the "module pattern" (IIFE returning an object) to avoid name collisions; TypeScript added `namespace` to give that pattern real syntax and type checking. Today ES modules solve the same problem natively (with tooling support: tree-shaking, lazy loading), so the real question in an interview is **why not to use namespaces**.

## 🔴 यह क्यों बना? (Hindi)
ES2015 modules से पहले JavaScript में सिर्फ एक global scope था। Name collisions से बचने के लिए teams "module pattern" (IIFE जो object return करे) इस्तेमाल करती थीं; TypeScript ने इस pattern को proper syntax और type checking देने के लिए `namespace` जोड़ा। आज ES modules यही समस्या native तरीके से हल करते हैं (tree-shaking, lazy loading के साथ), इसलिए interview में असली सवाल होता है: **namespaces क्यों इस्तेमाल नहीं करने**।

---

## 🟢 How it Works — Step by Step

Step 1 → `namespace Pay { ... }` creates a container named `Pay`.
Step 2 → Only members marked `export` are visible outside; others stay private to the namespace body.
Step 3 → The compiler emits `var Pay; (function (Pay) { ... })(Pay || (Pay = {}));` — members are properties on the `Pay` object.
Step 4 → Two `namespace Pay` blocks **merge** (same object, even across files with `/// <reference>` or one compilation).
Step 5 → ES modules: each file is already its own scope; you `export`/`import` explicit names, the bundler can tree-shake unused exports.
Step 6 → With `erasableSyntaxOnly` (TS 5.8) or Node's type-stripping (`node --experimental-strip-types`), runtime namespaces are **not allowed** because they need code generation (like `enum` and parameter properties).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `namespace Pay { ... }` एक container बनाता है जिसका नाम `Pay` है।
Step 2 → सिर्फ `export` वाले members बाहर दिखते हैं; बाकी namespace body में private रहते हैं।
Step 3 → Compiler `var Pay; (function (Pay) { ... })(Pay || (Pay = {}));` emit करता है — members `Pay` object की properties बन जाते हैं।
Step 4 → दो `namespace Pay` blocks **merge** हो जाते हैं (एक ही object, कई files में भी, एक ही compilation में)।
Step 5 → ES modules: हर file पहले से अपना scope है; आप explicit names `export`/`import` करते हो, bundler unused exports को tree-shake कर सकता है।
Step 6 → `erasableSyntaxOnly` (TS 5.8) या Node की type-stripping (`node --experimental-strip-types`) में runtime namespaces **allowed नहीं** हैं क्योंकि उन्हें code generation चाहिए (जैसे `enum` और parameter properties)।

---

## 🟡 Real World Example
**An old Razorpay-integration codebase** has `namespace Payments { export namespace Gateway { ... } export namespace Refund { ... } }` spread over many files compiled with `outFile` into one `bundle.js`. A new microservice written today instead has `payments/gateway.ts` and `payments/refund.ts`, each with `export`, and a barrel `payments/index.ts`. Webpack/Vite tree-shake the unused refund code from the checkout page; with a namespace the whole object is one big IIFE and nothing can be dropped.

## 🟡 Real Example Hindi mein
**Razorpay integration का पुराना codebase**: `namespace Payments { export namespace Gateway { ... } export namespace Refund { ... } }` कई files में फैला है और `outFile` से एक `bundle.js` में compile होता है। आज लिखी नई microservice में `payments/gateway.ts` और `payments/refund.ts` हैं, दोनों में `export`, और एक barrel `payments/index.ts`। Webpack/Vite checkout page से unused refund code tree-shake कर देते हैं; namespace में पूरा object एक बड़ा IIFE होता है और कुछ हटाया नहीं जा सकता।

---

## 💻 Code Example — Basic

```typescript
// A namespace groups related code under one name
namespace Pay {
  const secret = "rzp_key_123";               // private: not exported
  export const fee = 2;                        // public constant
  export function charge(amount: number): number {
    return amount + (amount * fee) / 100;     // can use private + public members
  }
  export function keyHint(): string {
    return secret.slice(0, 7) + "***";        // exposes only a safe hint
  }
}

console.log(Pay.charge(1000)); // call exported function
console.log(Pay.keyHint());    // private secret never directly accessible
// Output:
// 1020
// rzp_key***
```

```typescript
// file: pay/index.ts
// The same idea as an ES module: file scope IS the container
const secret = "rzp_key_123";                  // private by default (not exported)
export const fee = 2;                           // public
export function charge(amount: number): number {
  return amount + (amount * fee) / 100;       // same logic
}
export function keyHint(): string {
  return secret.slice(0, 7) + "***";
}
```

```typescript
// file: pay/main.ts
import * as Pay from "./index";   // namespace-style import (tree-shakeable by bundlers)
import { charge } from "./index"; // or import only what you need

console.log(Pay.fee, charge(500)); // 2 510
```

## 💻 Code Example — Advanced

```typescript
// Nested namespaces + merging + import alias
namespace Payments {
  export namespace Gateway {
    export const name = "razorpay";            // Payments.Gateway.name
  }
}
namespace Payments {                            // second block MERGES into the first
  export namespace Refund {
    export function fee(amount: number): number {
      return Math.round(amount * 0.01);        // 1% refund fee
    }
  }
}

import Refund = Payments.Refund;               // alias for a long path (import = syntax)
console.log(Payments.Gateway.name, Refund.fee(2500));
// Output:
// razorpay 25
```

```typescript
// Legit modern use: a namespace in a .d.ts / global type to group TYPES only
// (types-only namespaces produce NO runtime code, so they are erasable)
declare namespace Checkout {
  interface Cart { items: string[]; total: number }   // Checkout.Cart
  type Status = "idle" | "paying" | "done";           // Checkout.Status
}

const cart: Checkout.Cart = { items: ["Pizza"], total: 399 }; // use grouped types
const status: Checkout.Status = "idle";
console.log(cart.total, status);
```

---

## 🟠 Node/Express + React Integration

```typescript
// file: server/express-augment.ts
// The ONE place namespaces are still everywhere: Express's own global `Express` namespace.
// Adding fields to it via declare global + namespace merging (see topic 35/39).
import "express";

declare global {
  namespace Express {            // eslint: no-namespace is OK here (merging with a library)
    interface Request {
      tenantId?: string;          // set by multi-tenant middleware
    }
  }
}
```

```tsx
// file: web/api.ts
// React/Vite apps: use ES modules for everything.
export const baseUrl = "/api"; // named export, tree-shakeable
export async function getOrders(): Promise<{ id: string }[]> {
  const res = await fetch(`${baseUrl}/orders`); // Fetch API
  return res.json();                              // any -> typed via return annotation
}
```

```tsx
// file: web/OrderList.tsx
import { useEffect, useState } from "react";
import { getOrders } from "./api"; // only getOrders is bundled

export function OrderList() {
  const [orders, setOrders] = useState<{ id: string }[]>([]); // typed state
  useEffect(() => { getOrders().then(setOrders); }, []);       // load on mount
  return <ul>{orders.map((o) => <li key={o.id}>{o.id}</li>)}</ul>;
}
```

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: Accessing a member that was not `export`ed.**

```typescript
// ❌ secret has no `export`, so it is private to the namespace
namespace Pay {
  const secret = "key";
  export function charge() { return secret; } // ok: inside the namespace
}
Pay.secret; // wrong: outside access
// error TS2339: Property 'secret' does not exist on type 'typeof Pay'.
```

```typescript
// ✅ Export what must be public, keep secrets private
namespace Pay {
  const secret = "key";
  export function charge() { return secret.length; }
}
console.log(Pay.charge());
// Output:
// 3
```

**Mistake 2: Using runtime namespaces in a type-stripping / `erasableSyntaxOnly` project.**

```typescript
// ❌ Runtime namespace (has `const`/functions) => needs code generation
namespace Pay { export const fee = 2; }
// With tsc --erasableSyntaxOnly (TS 5.8) or Node --experimental-strip-types:
// error TS1294: This syntax is not allowed when 'erasableSyntaxOnly' is enabled.
// (verified by running tsc 5.9 with that flag; default --strict run accepts it)
```

```typescript
// ✅ Use a module with exports instead
export const fee = 2; // plain export: erasable, no emitted wrapper
```

**Mistake 3:** Mixing `namespace` with ES `import`/`export` at the top level of the same file, then wondering why `/// <reference>` and `outFile` behave strangely. Pick one style per project: **modules**.

---

## 🧠 Tricky Interview Question

```typescript
namespace A { export let n = 1; }
const x = A.n;
A.n = 2;
console.log(x, A.n);
```
**Answer:** Prints `1 2`. `A.n` is a live property on the namespace object (the compiler emits `A.n = 1`), but `const x = A.n` copies the **value** at that moment. Exported `let` in a namespace compiles to a property assignment, while in an **ES module** an exported `let` is a *live binding* (importers see updates automatically). So namespaces and modules differ in subtle semantics even though both "export a variable".

---

## ⚫ Interview Questions + Answers

**Q1: Namespace vs ES module — which should you choose and why?**
A1: ES modules. They are the JS standard, work with bundlers (tree-shaking, code-splitting), Node ESM, and type-stripping tools. Namespaces are TS-only, emit IIFEs, block tree-shaking and cannot be run by Node's strip-types or `erasableSyntaxOnly`.

**Q2: What does a namespace compile to?**
A2: `var Pay; (function (Pay) { Pay.fee = 2; })(Pay || (Pay = {}));`. Verified from real `tsc` output: exported members become properties on the object; the `|| (Pay = {})` part enables merging.

**Q3: When are namespaces still acceptable?**
A3: (1) `declare namespace` in `.d.ts` files to group types (erased, no runtime), (2) augmenting libraries that use namespaces (Express `Request`, `JSX`), (3) function+namespace or enum+namespace merging, (4) legacy codebases using `outFile`.

**Q4: Difference between "internal modules" and "external modules"?**
A4: Old terminology: internal module = `namespace` (formerly `module Foo {}`), external module = file with import/export. Since TS 1.5, "module" means ES module and `namespace` was introduced to avoid confusion.

**Q5: How do `import * as X` and a namespace differ?**
A5: `import * as X from "./x"` creates a read-only module namespace object (exports cannot be reassigned by importers, bindings are live). A `namespace` is a mutable object created by the TS emit. Both give `X.member` syntax.

---

## 🔷 When to Use + When Not to Use
✅ Use namespaces when:
- Writing `declare namespace` in `.d.ts` to group types or describe a global JS library
- Augmenting existing namespaced types (Express, JSX)
- Merging helpers onto a function/enum

❌ Avoid when:
- Writing application code in any bundler/Node ESM project
- You enable `erasableSyntaxOnly`, `verbatimModuleSyntax` or run TS directly in Node
- You want tree-shaking and clear dependency graphs

---

## 📊 Visual Diagram
```
 NAMESPACE (TS-only)                    ES MODULE (JS standard)
 ───────────────────                    ───────────────────────
 namespace Pay { export ... }           pay.ts:  export const fee, export function charge
        │                                       │
        ▼ emits                                 ▼ stays as-is
 var Pay; (function(Pay){...})(Pay||(Pay={}))   import { charge } from "./pay"
 one object, merged, global-ish                 file scope, tree-shakeable, lazy-loadable
 ✖ erasableSyntaxOnly  ✖ tree-shaking           ✔ Node ESM  ✔ Vite  ✔ strip-types
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| namespace | TS grouping construct, emits IIFE | TS का grouping construct |
| ES module | File-scoped import/export unit | File-scope वाली module |
| IIFE | Immediately-invoked function expression | तुरंत चलने वाला function |
| Tree-shaking | Removing unused exports in bundling | Unused code हटाना |
| erasableSyntaxOnly | TS 5.8 flag: only syntax that can be erased | सिर्फ erasable syntax allowed |
| Live binding | Imported name reflects exporter's updates | Exporter के update दिखना |

---

## ⚡ 3-Line Summary
English:
1. `namespace` is a TS-only IIFE-based grouping; ES modules are the standard and should be your default.
2. Namespaces still make sense for `declare namespace` in `.d.ts` files and augmenting library namespaces.
3. Runtime namespaces fail under `erasableSyntaxOnly` (TS 5.8) and Node type-stripping (TS1294).

Hindi:
1. `namespace` TS का IIFE-आधारित grouping है; ES modules standard हैं और आपका default होने चाहिए।
2. `.d.ts` में `declare namespace` और library namespaces को augment करने के लिए namespaces अब भी ठीक हैं।
3. Runtime namespaces `erasableSyntaxOnly` (TS 5.8) और Node type-stripping में fail होते हैं (TS1294)।

---

## ➡️ Next Topic
**38. Ambient Declarations and declare** — telling the compiler about code that exists at runtime but is not written in TypeScript (`declare const`, `declare module`, `.d.ts`).
