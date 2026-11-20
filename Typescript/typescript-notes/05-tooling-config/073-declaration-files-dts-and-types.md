# 73. Declaration Files (.d.ts) and @types
# हिंदी में: Declaration Files (.d.ts) और @types (JavaScript code के लिए types)

> Verified with TypeScript 5.9 (`tsc --strict`). `declaration`/`.d.ts` emit is stable since TS 1.x; `typesVersions` since 3.1; `@types` since TS 2.0.

---

## 🔵 Simple Definition (English)
A **declaration file** (`.d.ts`) contains **only type information** - no runnable code. It describes the shape of JavaScript that already exists (a library, a global, an asset import) so TypeScript can type-check your usage of it. **`@types/*`** packages (from the DefinitelyTyped project) are community-written `.d.ts` files published to npm for libraries that do not ship their own types, e.g. `@types/express`, `@types/node`, `@types/react`.

## 🔵 सरल परिभाषा (Hindi)
**Declaration file** (`.d.ts`) में **सिर्फ type की जानकारी** होती है - चलने लायक code नहीं। यह पहले से मौजूद JavaScript (library, global, asset import) की shape बताती है ताकि TypeScript तुम्हारे उपयोग को type-check कर सके। **`@types/*`** packages (DefinitelyTyped project से) community के लिखे `.d.ts` files हैं जो npm पर उन libraries के लिए छपते हैं जो अपने types खुद नहीं देतीं, जैसे `@types/express`, `@types/node`, `@types/react`।

---

## 🔴 Problem it Solves
TypeScript can only check what it can see. A plain JS library is a black box: every function would be `any`, so you would lose autocomplete and safety exactly where bugs like to hide (payment SDKs, legacy internal packages). Declaration files let you **add types without touching the JavaScript**, and let library authors **ship types alongside compiled JS** so consumers get IntelliSense for free.

## 🔴 यह क्यों बना? (Hindi)
TypeScript सिर्फ वही check कर सकता है जो उसे दिखे। साधारण JS library एक काला डिब्बा है: हर function `any` होगा, यानी autocomplete और safety वहीं चली जाती है जहाँ bugs छिपते हैं (payment SDKs, पुराने internal packages)। Declaration files से **JavaScript को छुए बिना types जोड़े जा सकते हैं**, और library authors compiled JS के साथ **types भी भेज सकते हैं** ताकि users को IntelliSense मुफ्त मिले।

---

## 🟢 How it Works — Step by Step

Step 1 → You `import { charge } from "legacy-pay"`. TS resolves the module (see note 72) and looks for types.
Step 2 → It checks, in order: the package's `types`/`typings` field (or `exports.types`), `index.d.ts` next to `main`, then `node_modules/@types/legacy-pay`.
Step 3 → If only JS is found, under `noImplicitAny` you get **TS7016: Could not find a declaration file**.
Step 4 → Fix A: `npm i -D @types/<pkg>` if DefinitelyTyped has it. Fix B: write your own `.d.ts` (`declare module "legacy-pay" { ... }`). Fix C (quick and unsafe): `declare module "legacy-pay";` makes everything `any`.
Step 5 → When **you** publish a library: set `"declaration": true` in tsconfig, `tsc` emits `.d.ts` next to JS, and `package.json` gets `"types": "dist/index.d.ts"`.
Step 6 → `skipLibCheck: true` makes TS skip type-checking inside all `.d.ts` files (faster, avoids clashes between dependencies) but does not stop them from being used.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → तुम `import { charge } from "legacy-pay"` लिखते हो। TS module resolve करता है (note 72 देखो) और types खोजता है।
Step 2 → वह क्रम से देखता है: package की `types`/`typings` field (या `exports.types`), `main` के पास `index.d.ts`, फिर `node_modules/@types/legacy-pay`।
Step 3 → सिर्फ JS मिले तो `noImplicitAny` में **TS7016: Could not find a declaration file** आता है।
Step 4 → उपाय A: `npm i -D @types/<pkg>` (अगर DefinitelyTyped पर है)। उपाय B: अपना `.d.ts` लिखो (`declare module "legacy-pay" { ... }`)। उपाय C (जल्दी पर असुरक्षित): `declare module "legacy-pay";` सब कुछ `any` बना देता है।
Step 5 → जब **तुम** library publish करो: tsconfig में `"declaration": true`, `tsc` JS के साथ `.d.ts` emit करता है, और `package.json` में `"types": "dist/index.d.ts"` जोड़ो।
Step 6 → `skipLibCheck: true` सभी `.d.ts` files के अंदर type-check छोड़ देता है (तेज़, dependencies के टकराव से बचाव) पर उनका इस्तेमाल नहीं रोकता।

---

## 🟡 Real World Example
**A Paytm-style codebase** still depends on an internal, untyped JS package `legacy-pay` written in 2018. Instead of rewriting it, the team adds `src/types/legacy-pay.d.ts` describing `charge()` and the `ChargeResult` shape. Immediately every call site gets autocomplete, and passing `"100"` instead of `100` becomes a compile error. Meanwhile `express`, `node`, `react` come typed through `@types/express`, `@types/node`, `@types/react` installed as devDependencies.

## 🟡 Real Example Hindi mein
**Paytm-जैसे codebase** में 2018 का एक internal, बिना types का JS package `legacy-pay` है। उसे दोबारा लिखने की जगह team `src/types/legacy-pay.d.ts` जोड़ती है जो `charge()` और `ChargeResult` की shape बताती है। तुरंत हर call site को autocomplete मिलता है, और `100` की जगह `"100"` देना compile error बन जाता है। उधर `express`, `node`, `react` के types devDependencies में रखे `@types/express`, `@types/node`, `@types/react` से आते हैं।

---

## 💻 Code Example — Basic

The problem: importing an untyped JS package (real compiler output):

```typescript
import { charge } from "legacy-pay"; // ❌ error TS7016: Could not find a declaration file for module 'legacy-pay'. '.../node_modules/legacy-pay/index.js' implicitly has an 'any' type.
//   Try `npm i --save-dev @types/legacy-pay` if it exists or add a new declaration (.d.ts) file containing `declare module 'legacy-pay';`
console.log(charge(100, "INR"));
```

The fix - our own declaration file (a "script" file: no top-level import/export, so `declare module` creates a new module declaration):

```typescript
// script
// src/types/legacy-pay.d.ts
declare module "legacy-pay" {
  export interface ChargeResult { ok: boolean; amount: number; currency: string } // result shape
  export function charge(amount: number, currency: string): ChargeResult; // signature only, no body
}

// wildcard module: lets bundlers import images as URL strings
declare module "*.svg" {
  const url: string; // Vite/webpack turns the import into a URL
  export default url;
}
```

Using it (compiled together with the declaration file above):

```text
// src/payment.ts - uses the declarations above
import { charge } from "legacy-pay";
const r = charge(100, "INR");                 // r: ChargeResult  (autocomplete works)
console.log(r.ok);                            // true  (real output of running the JS)
const bad = charge("100", "INR");
// real compiler output:
// error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.
```

## 💻 Code Example — Advanced

What `tsc --declaration` generates from real code - the `.d.ts` is just the public shape. Source:

```typescript
// src/order.ts - the implementation
export interface Order { id: string; total: number }
export function totalOf(o: Order): number { return o.total; } // body stays in the .js
export const TAX = 0.18; // literal constant
```

Real emitted `dist/order.d.ts` (`tsc --declaration --emitDeclarationOnly`):

```text
export interface Order {
    id: string;
    total: number;
}
export declare function totalOf(o: Order): number;
export declare const TAX = 0.18;
```

Publishing types in `package.json`, and how `@types` is controlled in tsconfig:

```json
{
  "name": "@acme/orders",
  "version": "1.0.0",
  "main": "./dist/order.js",
  "types": "./dist/order.d.ts",
  "exports": {
    ".": { "types": "./dist/order.d.ts", "default": "./dist/order.js" }
  },
  "files": ["dist"]
}
```

```json
{
  "compilerOptions": {
    "types": ["node"],
    "typeRoots": ["./node_modules/@types", "./src/types"],
    "skipLibCheck": true,
    "declaration": true
  }
}
```

`"types": ["node"]` means **only** `@types/node` is auto-included as a global package (important: without it, every `@types/*` in node_modules - for example `@types/jest` and `@types/mocha` together - is loaded globally and can clash).

---

## 🟠 Node/Express + React Integration

```typescript
// script
// src/types/assets.d.ts - tell TS what non-code imports look like (React + Vite)
declare module "*.png" {
  const src: string; // image import becomes a URL string
  export default src;
}

declare module "*.module.css" {
  const classes: { readonly [className: string]: string }; // CSS Modules map
  export default classes;
}
```

```typescript
import express from "express"; // express ships no types -> TS uses @types/express
import type { Request, Response } from "express"; // types come from @types/express

const app = express();

app.get("/ping", (_req: Request, res: Response): void => {
  res.json({ pong: true }); // res.json is typed by @types/express
});

console.log(typeof app.listen); // function
```

```tsx
// React ships/needs types too: @types/react (and @types/react-dom) as devDependencies
import React from "react";

export function PriceTag({ paise }: { paise: number }) {
  return <b>Rs.{(paise / 100).toFixed(2)}</b>; // JSX is checked via @types/react
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Putting `@types/*` in `dependencies` for an app, or forgetting them entirely
Install as dev dependency: `npm i -D @types/express @types/node`. They are not needed at runtime. For a published library whose public `.d.ts` mentions those types, list them in `dependencies` instead.

❌ Mistake 2: `declare module "x";` (no body) as the permanent fix
It silences TS7016 but types the whole package as `any`. Write at least the functions you really use.

❌ Mistake 3: Writing code (implementation) in a `.d.ts`
```typescript
// script
declare function charge(a: number): number { return a; } // ❌ error TS1183: An implementation cannot be declared in ambient contexts.
```

❌ Mistake 4: Making the `.d.ts` a module by accident
A top-level `import`/`export` in a `.d.ts` turns it from a global script into a module; then `declare module "*.svg"` no longer adds a new module, it becomes an augmentation. Keep asset declarations free of top-level imports, or use `import("...")` types inside.

❌ Mistake 5: Not shipping `types` when publishing
Consumers get TS7016 on your package. Set `"declaration": true` and `"types"` / `exports.types`.

---

## 🧠 Tricky Interview Question

Q: You installed `@types/express` but also have `"types": ["node"]` in tsconfig. Does `import express from "express"` still get typed? What about a global like `describe` from `@types/jest`?

Answer: Yes for `express` - the `types` option only restricts **automatic global inclusion** of `@types` packages. A package you explicitly **import** is always resolved normally (including its `@types/...`). But `describe`/`it` globals from `@types/jest` would be missing, because it is not in the `types` list and nothing imports it - you would add `"types": ["node", "jest"]` or a `/// <reference types="jest" />`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `.ts` and `.d.ts`?
A1: `.ts` has implementation and is compiled to JS. `.d.ts` has declarations only and emits nothing; it exists to describe JS or to ship types.

Q2: What is DefinitelyTyped / `@types`?
A2: A community repo that publishes `.d.ts` for libraries lacking built-in types (`@types/express`). Modern libs (zod, RTK, Axios) ship their own types; check for a `types` field before installing `@types`.

Q3: What does `skipLibCheck` do and is it safe?
A3: Skips checking **all** `.d.ts` files (including yours). It speeds builds and hides conflicts between dependency types. Reasonable for apps; for libraries keep checking your own `.d.ts` output in CI.

Q4: `declare module "x"` vs `declare global`?
A4: `declare module "x"` describes a module specifier; `declare global { }` (inside a module file) adds to the global scope (see note 39).

Q5: How do you generate types for a JS-with-JSDoc project?
A5: `allowJs` + `checkJs` + `declaration` + `emitDeclarationOnly`: TS reads JSDoc annotations and emits `.d.ts` without converting source.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A dependency has no types (write a local `.d.ts` or install `@types/*`)
- Importing assets (`*.svg`, `*.css`) in bundler projects
- Publishing a library (always emit declarations)

❌ Avoid when:
- A package already ships types (installing `@types` too can create conflicts or stale types)
- You can convert the JS file to TS directly - a real implementation beats a hand-written declaration

---

## 📊 Visual Diagram
```
 import { charge } from "legacy-pay"
              │
              ▼
   node_modules/legacy-pay/package.json
        ├─ "types": "x.d.ts"?   ── yes ──► use it
        ├─ index.d.ts beside main? yes ──► use it
        ├─ node_modules/@types/legacy-pay? yes ─► use it
        ├─ your own  declare module "legacy-pay" (in an included .d.ts)? ─► use it
        └─ none ──► JS only ──► TS7016 (noImplicitAny) / implicit any
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `.d.ts` | Types-only declaration file | सिर्फ types वाली file |
| `@types/*` | DefinitelyTyped packages | Community के लिखे types packages |
| Ambient declaration | `declare` something that exists at runtime | जो runtime पर पहले से है उसका declaration |
| `typeRoots` / `types` | Which global @types to include | कौन से global @types शामिल हों |
| `declaration` | Emit `.d.ts` on build | Build पर `.d.ts` बनाना |
| `skipLibCheck` | Skip checking `.d.ts` files | `.d.ts` की जाँच छोड़ना |

---

## ⚡ 3-Line Summary
English:
1. `.d.ts` files carry types only; `@types/*` are community `.d.ts` for libraries without built-in types.
2. TS7016 means "JS found, no types": install `@types/x`, or write `declare module "x" { ... }`.
3. When publishing, emit declarations (`declaration: true`) and point `types` at them.

Hindi:
1. `.d.ts` में सिर्फ types होते हैं; `@types/*` उन libraries के community `.d.ts` हैं जिनमें अपने types नहीं हैं।
2. TS7016 का मतलब "JS मिला, types नहीं": `@types/x` install करो या `declare module "x" { ... }` लिखो।
3. Publish करते समय declarations emit करो (`declaration: true`) और `types` से उनकी ओर इशारा करो।

---

## ➡️ Next Topic
**74. Writing .d.ts for a JS Library** - Hand-writing declarations for CommonJS/UMD modules, overloads, callbacks and classes.
