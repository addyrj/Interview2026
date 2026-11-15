# 38. Ambient Declarations and declare
# हिंदी में: Ambient Declarations और `declare`

> Verified with **TypeScript 5.x** (compiled with 5.9, `--strict`). Ambient syntax is stable across all 5.x versions.

---

## 🔵 Simple Definition (English)
An **ambient declaration** tells the compiler "this thing **exists at runtime**, here is its type — but do not emit any code for it". You write it with the `declare` keyword (`declare const`, `declare function`, `declare class`, `declare module "x"`, `declare namespace`). `.d.ts` files contain *only* ambient declarations. Ambient declarations **never produce JavaScript**; they describe code that comes from somewhere else (a `<script>` tag, a bundler define, an untyped npm package).

## 🔵 सरल परिभाषा (Hindi)
**Ambient declaration** compiler से कहता है: "यह चीज़ **runtime पर मौजूद है**, उसका type यह है — लेकिन इसके लिए कोई code emit मत करो"। इसे `declare` keyword से लिखते हैं (`declare const`, `declare function`, `declare class`, `declare module "x"`, `declare namespace`)। `.d.ts` files में *सिर्फ* ambient declarations होती हैं। Ambient declarations **कभी JavaScript पैदा नहीं करतीं**; वे उस code को describe करती हैं जो कहीं और से आता है (`<script>` tag, bundler define, बिना types वाला npm package)।

---

## 🔴 Problem it Solves
Real apps use things TypeScript cannot see: a Google Analytics `gtag()` injected by a `<script>` tag, `__APP_VERSION__` replaced by Vite's `define`, a legacy JS payment SDK with no types, or `import logo from "./logo.svg"` handled by a bundler loader. Without declarations you get `TS2304: Cannot find name` / `TS2307: Cannot find module` or you sprinkle `any` everywhere. `declare` gives these a **proper type** without lying in your source with fake implementations.

## 🔴 यह क्यों बना? (Hindi)
Real apps में ऐसी चीज़ें होती हैं जिन्हें TypeScript देख नहीं पाता: `<script>` tag से आया Google Analytics `gtag()`, Vite के `define` से बदला हुआ `__APP_VERSION__`, बिना types वाला पुराना JS payment SDK, या `import logo from "./logo.svg"` जिसे bundler loader संभालता है। Declarations के बिना `TS2304: Cannot find name` / `TS2307: Cannot find module` आता है या आप हर जगह `any` डाल देते हो। `declare` इन्हें **सही type** देता है — बिना source में नकली implementation लिखे।

---

## 🟢 How it Works — Step by Step

Step 1 → Decide where the declaration lives: top of a file, or (better) a `*.d.ts` file included by `tsconfig`.
Step 2 → Write `declare` + normal signature, **no body, no initializer**: `declare function gtag(e: string): void;`
Step 3 → For a whole untyped package: `declare module "legacy-pay" { export function charge(n: number): Promise<string>; }`
Step 4 → For file-type imports: wildcard `declare module "*.svg" { const url: string; export default url; }`
Step 5 → Globals: a `.d.ts` **without** top-level import/export is a *global script* so its `declare const` becomes global everywhere.
Step 6 → The compiler trusts you. If runtime does not match, you get `ReferenceError` — ambient declarations are **promises, not checks**.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → तय करो declaration कहाँ रहेगी: file के top पर, या (बेहतर) `tsconfig` में included `*.d.ts` file में।
Step 2 → `declare` + normal signature लिखो, **कोई body या initializer नहीं**: `declare function gtag(e: string): void;`
Step 3 → पूरे untyped package के लिए: `declare module "legacy-pay" { export function charge(n: number): Promise<string>; }`
Step 4 → File-type imports के लिए wildcard: `declare module "*.svg" { const url: string; export default url; }`
Step 5 → Globals: जिस `.d.ts` में top-level import/export **नहीं** है वह *global script* है, इसलिए उसका `declare const` हर जगह global बन जाता है।
Step 6 → Compiler आप पर भरोसा करता है। Runtime में चीज़ न हो तो `ReferenceError` आएगा — ambient declarations **वादे हैं, checks नहीं**।

---

## 🟡 Real World Example
**Swiggy web app**: the HTML shell loads Google Analytics via `<script>`, creating a global `gtag`. Vite replaces `__APP_VERSION__` at build. The team also integrates `legacy-pay`, an in-house JS SDK nobody typed. One file `src/types/ambient.d.ts` declares all three: `gtag`, `__APP_VERSION__`, and the `legacy-pay` module. Every component can now call `gtag("event", ...)` with autocomplete and the compiler catches `gtag(42)`.

## 🟡 Real Example Hindi mein
**Swiggy web app**: HTML shell `<script>` से Google Analytics load करता है, जिससे global `gtag` बनता है। Vite build पर `__APP_VERSION__` replace करता है। टीम `legacy-pay` भी इस्तेमाल करती है — एक in-house JS SDK जिसके types किसी ने नहीं लिखे। एक file `src/types/ambient.d.ts` तीनों declare करती है: `gtag`, `__APP_VERSION__` और `legacy-pay` module। अब हर component `gtag("event", ...)` autocomplete के साथ call कर सकता है और `gtag(42)` पर compiler पकड़ लेता है।

---

## 💻 Code Example — Basic

```typescript
// declare = "exists at runtime, emit nothing" (no body, no initializer)
declare function gtag(event: string, params?: Record<string, unknown>): void; // GA global
declare const __APP_VERSION__: string;                                         // build-time define

// Because the compiler trusts us, we guard against the global not existing at runtime
function track(name: string): string {
  if (typeof gtag === "function") { // typeof on an undeclared runtime name is safe
    gtag(name, { v: __APP_VERSION__ }); // typed call
    return "sent";
  }
  return "skipped (gtag not loaded)"; // e.g. ad-blocker removed the script
}

console.log(track("add_to_cart")); // here gtag was never defined at runtime
// Output:
// skipped (gtag not loaded)
```

```typescript
// declare class: describe a runtime class you do not own (e.g. loaded via CDN)
declare class RazorpayCheckout {
  constructor(options: { key: string; amount: number }); // constructor signature
  open(): void;                                           // instance method
  static readonly version: string;                        // static member
}

declare function makeCheckout(): RazorpayCheckout; // pretend a factory exists
const rz = makeCheckout();  // type is RazorpayCheckout
rz.open();                   // typed method call (no runtime here: type check only)
export {};
```

## 💻 Code Example — Advanced

```typescript
// file: types/ambient.d.ts (script file)
// No top-level import/export => this file is GLOBAL, everything here is visible everywhere.
declare const __DEV__: boolean; // replaced by bundler define

// Wildcard modules: bundler handles these imports, TS only needs a type
declare module "*.svg" {
  const url: string; // import logo from "./logo.svg" gives a URL string
  export default url;
}
declare module "*.module.css" {
  const classes: Readonly<Record<string, string>>; // CSS-modules class map
  export default classes;
}

// A whole untyped package, described by us
declare module "legacy-pay" {
  export interface ChargeResult { id: string; status: "ok" | "declined" } // exported type
  export function charge(amountPaise: number, upiId: string): Promise<ChargeResult>; // async API
}
```

```typescript
// file: pay/use-legacy.ts
import { charge, type ChargeResult } from "legacy-pay"; // resolved by our ambient module
import logo from "../assets/logo.svg";                   // resolved by the wildcard

export async function payAndLog(upi: string): Promise<ChargeResult> {
  if (__DEV__) console.log("logo", logo.length);   // __DEV__ is a declared global
  const result = await charge(49900, upi);          // typed: Promise<ChargeResult>
  return result;                                     // result.status is "ok" | "declined"
}
```

```typescript
// Ambient enums and `declare global` for module files (see topic 39)
declare enum Currency { INR = "INR", USD = "USD" } // exists at runtime elsewhere
declare const enum Gateway { Razorpay, Paytm }     // const enum: inlined at compile time
const c: Currency = Currency.INR;                   // compiles; runtime value is YOUR responsibility
const g = Gateway.Paytm;                            // inlined as 1 under normal tsc settings
export { c, g };
```

---

## 🟠 Node/Express + React Integration

```typescript
// file: server/env.d.ts (script file)
// Node: describe process.env keys (NodeJS namespace merge - see topic 35)
declare namespace NodeJS {
  interface ProcessEnv {
    DB_URL: string;                       // required connection string
    JWT_SECRET: string;                   // required secret
    NODE_ENV: "development" | "production"; // narrowed env
  }
}
```

```typescript
// file: server/db.ts
// Now process.env.DB_URL is `string`, not `string | undefined`.
const dbUrl: string = process.env.DB_URL; // typed by the ambient declaration (still validate at startup!)
export const connectionInfo = { url: dbUrl, prod: process.env.NODE_ENV === "production" };
```

```tsx
// file: web/Header.tsx   (React + Vite: SVG import via wildcard module, global __APP_VERSION__)
import logo from "../assets/logo.svg"; // typed as string by the ambient wildcard

export function Header() {
  return (
    <header>
      <img src={logo} alt="logo" />
      <small>v{__APP_VERSION__}</small>
    </header>
  );
}
```

```typescript
// file: web/vite-globals.d.ts (script file)
declare const __APP_VERSION__: string; // Vite define: JSON.stringify(pkg.version)
```

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: Using a runtime global without declaring it.**

```typescript
// ❌ No declaration => compiler has no idea APP_VERSION exists
const v = APP_VERSION; // wrong
// error TS2304: Cannot find name 'APP_VERSION'.
```

```typescript
// ✅ Declare it (ideally in a .d.ts), then use it
declare const APP_VERSION: string;
const v = APP_VERSION; // ok: typed string
console.log(typeof v);
export {};
```

**Mistake 2: Putting an initializer in a `declare`.**

```typescript
// ❌ declare means "exists elsewhere"; you cannot give it a value here
declare const X: number = 5; // wrong
// error TS1039: Initializers are not allowed in ambient contexts.
```

```typescript
// ✅ No initializer. If you need a real value, write a normal const instead
declare const X: number; // ambient: trusts runtime to provide X
const Y = 5;             // real value emitted to JS
export { Y };
```

**Mistake 3: Importing an untyped module and not describing it.** `import { charge } from "legacy-pay"` gives `error TS2307: Cannot find module 'legacy-pay' or its corresponding type declarations.` (I ran this exact import in a clean project.) For a local JS file without `allowJs` the message is `TS7016: Could not find a declaration file for module './legacy.js'`. Fix: add `declare module "legacy-pay" {...}`, install `@types/...`, or enable `allowJs`.

**Mistake 4: Putting `declare module "x"` in a file that has an `import`.** It then becomes a **module augmentation** and errors if `x` cannot be resolved. Keep ambient module declarations in a **script** `.d.ts` (no imports).

---

## 🧠 Tricky Interview Question

```typescript
declare const flag: boolean;
if (flag) console.log("on"); else console.log("off");
```
**Q:** What does this print, and can it be compiled by `tsc`?
**Answer:** It **compiles** fine (the ambient declaration satisfies the checker), but at runtime it throws `ReferenceError: flag is not defined` because `declare` emits nothing and no real `flag` exists. This is the key point: ambient declarations are a promise to the compiler, not a runtime guarantee. The safe pattern when a global may be missing is `typeof flag !== "undefined"`.

---

## ⚫ Interview Questions + Answers

**Q1: What does `declare` do and what does it never do?**
A1: It declares a type for something that exists at runtime without emitting JS. It never creates a value, never allows initializers (TS1039) and never checks the runtime.

**Q2: Difference between `.ts` and `.d.ts`?**
A2: `.d.ts` contains only declarations (types and ambient declarations), is never emitted, and is for describing JS. `.ts` can hold implementation and always produces `.js` (unless `noEmit`).

**Q3: How do you type `import img from "./x.png"` in Vite/Webpack?**
A3: With a wildcard ambient module: `declare module "*.png" { const src: string; export default src; }`, or reference `vite/client` types (`/// <reference types="vite/client" />`) which already declare common assets.

**Q4: `declare module "x"` vs `declare global` vs `declare namespace`?**
A4: `declare module "x"` types a specific module specifier (or augments it when inside a module file); `declare global` adds to the global scope from inside a module (topic 39); `declare namespace Foo` describes a global object with members, e.g. the `NodeJS` namespace.

**Q5: When do you prefer `@types/xyz` over writing your own declaration?**
A5: When DefinitelyTyped already has it (`npm i -D @types/express`). Write your own `declare module` for internal packages or when types are missing or wrong, and consider `declare module "x";` (shorthand) to type everything as `any` as a temporary escape hatch.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Typing `<script>`-injected globals, bundler defines, asset imports
- Wrapping an untyped JS dependency while you migrate
- Describing global namespaces like `NodeJS.ProcessEnv`

❌ Avoid when:
- A real `@types` package exists (use it)
- You can instead write the module in TypeScript (declarations drift from reality)
- You need runtime safety: validate with Zod instead of trusting a declaration

---

## 📊 Visual Diagram
```
 compile time (tsc)                         runtime (JS)
 ──────────────────                         ────────────
 declare const __APP_VERSION__: string  ─►  (nothing emitted)
 declare module "legacy-pay" {...}      ─►  (nothing emitted)
        │ trusts you                             │
        ▼                                        ▼
 gtag("x") type-checks                  must REALLY exist (script tag / bundler / npm)
                                        else: ReferenceError / Cannot find module
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Ambient declaration | Type for code that exists elsewhere | कहीं और मौजूद code का type |
| declare | Keyword that emits no JS | बिना JS emit करने वाला keyword |
| .d.ts | Declaration-only file | सिर्फ declarations वाली file |
| Wildcard module | `declare module "*.svg"` | Pattern वाला module declaration |
| Script file | File with no import/export (global) | Global file (बिना import/export) |
| DefinitelyTyped | Community `@types/*` packages | Community द्वारा लिखे types |

---

## ⚡ 3-Line Summary
English:
1. `declare` describes runtime things (globals, untyped packages, asset imports) to the compiler and emits no JavaScript.
2. Keep ambient code in script-style `.d.ts` files: globals, `declare module "x"`, and wildcard modules like `"*.svg"`.
3. It is a promise, not a check — a wrong declaration compiles but fails at runtime.

Hindi:
1. `declare` runtime की चीज़ों (globals, untyped packages, asset imports) को compiler को बताता है और JavaScript emit नहीं करता।
2. Ambient code को script-style `.d.ts` files में रखो: globals, `declare module "x"`, और `"*.svg"` जैसे wildcard modules।
3. यह वादा है, check नहीं — गलत declaration compile हो जाता है पर runtime पर fail होता है।

---

## ➡️ Next Topic
**39. Global Augmentation (declare global)** — adding to global types (`Window`, `globalThis`, `process.env`) from inside a module.
