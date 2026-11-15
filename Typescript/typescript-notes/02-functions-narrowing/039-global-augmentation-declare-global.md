# 39. Global Augmentation (declare global)
# हिंदी में: Global Augmentation (`declare global`)

> Verified with **TypeScript 5.x** (compiled with 5.9, `--strict`). Behaviour of `declare global` is the same across 5.x.

---

## 🔵 Simple Definition (English)
**Global augmentation** means adding or extending **global** types and variables (`Window`, `globalThis`, `Array`, `NodeJS.ProcessEnv`, `Express.Request`) from **inside a module file**. Because a file with an `import`/`export` has its own scope, ordinary top-level declarations stay local. The block `declare global { ... }` is the door that lets a module file write into the global scope. It uses declaration merging (topic 35) under the hood.

## 🔵 सरल परिभाषा (Hindi)
**Global augmentation** का मतलब है **global** types और variables (`Window`, `globalThis`, `Array`, `NodeJS.ProcessEnv`, `Express.Request`) को **module file के अंदर से** बढ़ाना। जिस file में `import`/`export` है उसका अपना scope होता है, इसलिए सामान्य top-level declarations local रहती हैं। `declare global { ... }` वह दरवाज़ा है जिससे module file global scope में लिख सकती है। यह अंदर से declaration merging (topic 35) का इस्तेमाल करता है।

---

## 🔴 Problem it Solves
Browser/Node globals that your app adds at runtime — `window.Razorpay` (loaded from a CDN), `globalThis.__prisma` (dev-server singleton), a polyfill like `Array.prototype.last`, or `process.env.DB_URL` — are unknown to the standard lib types. Writing `(window as any).Razorpay` everywhere loses safety and autocomplete. `declare global` adds the property **once**, and the whole project sees it with the correct type.

## 🔴 यह क्यों बना? (Hindi)
Browser/Node के globals जो आपका app runtime पर जोड़ता है — `window.Razorpay` (CDN से load), `globalThis.__prisma` (dev-server singleton), `Array.prototype.last` जैसा polyfill, या `process.env.DB_URL` — standard lib types को पता नहीं होते। हर जगह `(window as any).Razorpay` लिखने से safety और autocomplete खो जाते हैं। `declare global` property को **एक बार** जोड़ देता है और पूरा project उसे सही type के साथ देखता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Make sure the file is a **module** (has an `import` or `export`; add `export {}` if nothing else).
Step 2 → Write `declare global { ... }` at the top level of that file.
Step 3 → Inside, re-open built-in interfaces (`interface Window { ... }`) — they **merge**.
Step 4 → For global variables use **`var`** (`var __db: Pool | undefined`). `let`/`const` create global bindings that are **not** properties of `globalThis`.
Step 5 → For library namespaces use `namespace NodeJS { interface ProcessEnv {...} }` or `namespace Express { interface Request {...} }`.
Step 6 → Make sure the file is included by `tsconfig` (`include`, `files` or imported somewhere). Runtime must really provide the value — `declare global` is only a type promise.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → पक्का करो file **module** है (`import` या `export` हो; और कुछ न हो तो `export {}` जोड़ो)।
Step 2 → उस file के top level पर `declare global { ... }` लिखो।
Step 3 → अंदर built-in interfaces (`interface Window { ... }`) दोबारा खोलो — वे **merge** हो जाती हैं।
Step 4 → Global variables के लिए **`var`** इस्तेमाल करो (`var __db: Pool | undefined`)। `let`/`const` global bindings बनाते हैं जो `globalThis` की properties **नहीं** होते।
Step 5 → Library namespaces के लिए `namespace NodeJS { interface ProcessEnv {...} }` या `namespace Express { interface Request {...} }` लिखो।
Step 6 → File `tsconfig` में included होनी चाहिए (`include`, `files` या कहीं import हो)। Runtime को असल में value देनी होगी — `declare global` सिर्फ type का वादा है।

---

## 🟡 Real World Example
**Razorpay checkout in a React app**: the Razorpay SDK is loaded by `<script src="https://checkout.razorpay.com/v1/checkout.js">` and defines `window.Razorpay`. The team writes one file `globals.ts` with `declare global { interface Window { Razorpay?: RazorpayConstructor } }`. Now `new window.Razorpay({...})` is typed, and the optional `?` forces the `if (!window.Razorpay)` check for the case when the script was blocked.

## 🟡 Real Example Hindi mein
**React app में Razorpay checkout**: Razorpay SDK `<script src="https://checkout.razorpay.com/v1/checkout.js">` से load होता है और `window.Razorpay` बनाता है। टीम एक file `globals.ts` लिखती है: `declare global { interface Window { Razorpay?: RazorpayConstructor } }`। अब `new window.Razorpay({...})` typed है, और optional `?` की वजह से `if (!window.Razorpay)` check ज़रूरी हो जाता है (जब script block हो गई हो)।

---

## 💻 Code Example — Basic

```typescript
// This file is a module (has `export {}` at the end), so declare global is allowed
declare global {
  // `var` (not let/const) makes it a property of globalThis
  var appName: string;                      // global variable
  interface Array<T> {                      // merges into the built-in Array<T>
    last(): T | undefined;                  // new method signature
  }
}

// Runtime implementation: declare global only TYPES it, we must provide it
globalThis.appName = "FoodApp";             // typed assignment
Array.prototype.last = function <T>(this: T[]): T | undefined {
  return this[this.length - 1];             // last element or undefined
};

console.log(globalThis.appName, [10, 20, 30].last(), ([] as number[]).last());
// Output:
// FoodApp 30 undefined
export {};
```

```typescript
// file: web/checkout.ts
// Window augmentation for a script-tag SDK (Razorpay-style)
interface RazorpayOptions { key: string; amount: number; currency: "INR" } // checkout options
interface RazorpayInstance { open(): void }                                   // what we call
type RazorpayConstructor = new (opts: RazorpayOptions) => RazorpayInstance;   // constructor type

declare global {
  interface Window { Razorpay?: RazorpayConstructor } // optional: script may be missing
}

export function openCheckout(amountPaise: number): boolean {
  if (!window.Razorpay) return false;                 // narrowing from optional property
  const rzp = new window.Razorpay({ key: "rzp_test_x", amount: amountPaise, currency: "INR" });
  rzp.open();                                          // typed call
  return true;
}
```

## 💻 Code Example — Advanced

```typescript
// Singleton across dev hot-reloads (Next.js/ts-node-dev): cache the DB pool on globalThis
interface FakePool { query(sql: string): Promise<string[]> } // stand-in for mssql ConnectionPool

declare global {
  var __pool: FakePool | undefined; // `var` so globalThis.__pool is typed
}

function createPool(): FakePool {
  console.log("creating pool");                          // shows how often it runs
  return { query: async (sql) => [`ran: ${sql}`] };      // fake implementation
}

// Reuse if already created, otherwise create once
export const pool: FakePool = globalThis.__pool ?? (globalThis.__pool = createPool());

pool.query("SELECT 1").then((rows) => console.log(rows)); // uses the shared pool
const again = globalThis.__pool ?? createPool();          // second access: no new creation
console.log(again === pool);
// Output:
// creating pool
// true
// [ 'ran: SELECT 1' ]
```

```typescript
// Typed process.env via the NodeJS namespace (merges with @types/node)
declare global {
  namespace NodeJS {
    interface ProcessEnv {
      DB_URL: string;                         // required at runtime (validate with Zod!)
      PORT?: string;                          // optional
      NODE_ENV: "development" | "production" | "test";
    }
  }
}

const port = Number(process.env.PORT ?? 3000);   // PORT is string | undefined
const url: string = process.env.DB_URL;           // string (not undefined) now
console.log(port, typeof url);
export {};
```

---

## 🟠 Node/Express + React Integration

```typescript
// file: server/types/global.ts  (Express Request extension via declare global)
import type { JwtPayload } from "./jwt"; // import makes this file a module

declare global {
  namespace Express {
    interface Request {
      user?: JwtPayload;  // set by auth middleware
      id: string;         // request id set by logger middleware
    }
  }
}
```

```typescript
// file: server/types/jwt.ts
export interface JwtPayload { sub: string; role: "admin" | "customer" } // token shape
```

```typescript
// file: server/auth.ts
import type { Request, Response, NextFunction } from "express";
import "./types/global";                          // ensure augmentation is loaded

export function auth(req: Request, _res: Response, next: NextFunction): void {
  req.user = { sub: "u-1", role: "customer" };    // typed assignment, no cast
  req.id = "req-123";                              // typed
  next();
}
```

```tsx
// file: web/Pay.tsx  (React component using the Window augmentation)
import { openCheckout } from "./checkout"; // function from the Window example

export function PayButton({ amount }: { amount: number }) {
  return (
    <button onClick={() => { if (!openCheckout(amount * 100)) alert("Payment SDK blocked"); }}>
      Pay ₹{amount}
    </button>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: Using `declare global` in a file that is NOT a module.**

```typescript
// file: bad-global.ts (script file)
// ❌ No import/export in this file => it is a global script, not a module
declare global {
  interface Window { Razorpay?: unknown }
}
// error TS2669: Augmentations for the global scope can only be directly nested in external modules or ambient module declarations.
```

```typescript
// file: good-global.ts
declare global {
  interface Window { Razorpay2?: unknown } // fine: file is a module because of export {}
}
export {}; // the one-line fix: make the file a module
```

**Mistake 2: Using `const`/`let` and expecting `globalThis.x`.**

```typescript
// ❌ const in declare global creates a global BINDING, not a globalThis property
declare global {
  const region: string;
}
console.log(globalThis.region); // wrong
// error TS2339: Property 'region' does not exist on type 'typeof globalThis'.
```

```typescript
// ✅ Use var so it is a property of globalThis
declare global {
  var region2: string;
}
globalThis.region2 = "ap-south-1"; // typed property of globalThis
console.log(globalThis.region2);
// Output:
// ap-south-1
```

**Mistake 3: Declaring the type but never providing the runtime value** (script not loaded, polyfill file not imported). The compiler is happy, production throws `TypeError: window.Razorpay is not a constructor`. Make the property optional (`?`) when it may be missing, and guard it.

**Mistake 4: Polluting globals when a module export would do.** Use `declare global` only for things that really are global at runtime.

---

## 🧠 Tricky Interview Question

```typescript
declare global { var counter: number } // global var
let counter = 0;                        // module-local let, same name
console.log(counter, globalThis.counter);
// Output:
// 0 undefined
export {};
```
**Q:** Does line 2 error, and what is printed?
**Answer:** It compiles with **no error** (verified with tsc 5.9) and prints `0 undefined`. Inside a module the local `let counter` *shadows* the global `var counter`; they are two different variables. `globalThis.counter` still reaches the global one (never assigned, so `undefined`). Takeaway: `declare global` variables are reached through `globalThis.x`, and a module-local with the same name silently shadows them, which is legal but confusing. (In a script file, both would be in the same scope and you would get a redeclaration error.)

---

## ⚫ Interview Questions + Answers

**Q1: Why does `declare global` require the file to be a module?**
A1: In a script file everything is already global, so you augment by plain `interface Window {...}`. In a module, top-level declarations are local; `declare global` is the explicit escape to the global scope. The compiler enforces this with TS2669.

**Q2: How do you add a property to `Window` for a CDN script?**
A2: `declare global { interface Window { Razorpay?: RazorpayConstructor } }` in a module (or a plain `interface Window` in a script `.d.ts`). Mark it optional if the script may fail to load.

**Q3: Why `var` and not `let` for global variables?**
A3: Only `var`-declared globals (and function declarations) become properties on `globalThis`. `let`/`const` are global bindings but unreachable via `globalThis.name`, giving TS2339 on `globalThis.name`.

**Q4: How do you type `process.env`?**
A4: Augment `NodeJS.ProcessEnv` in a `declare global { namespace NodeJS { interface ProcessEnv {...} } }` block. It only changes types — validate real values at startup with Zod (topic 87).

**Q5: Can you extend built-ins like `Array`/`String`? Should you?**
A5: Yes via `declare global { interface Array<T> { last(): T | undefined } }` plus a runtime prototype patch. But prototype pollution can break libraries and tree-shaking; prefer utility functions (`last(arr)`) in app code.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Typing script-tag SDKs on `Window` (Razorpay, Google Analytics, feature-flag clients)
- Adding to library namespaces (`Express.Request`, `NodeJS.ProcessEnv`)
- Dev-time singletons on `globalThis` (DB pool, Prisma client)

❌ Avoid when:
- A plain exported function/constant will do
- You would patch built-in prototypes in library code
- You expect the declaration to guarantee the value exists at runtime

---

## 📊 Visual Diagram
```
 module file (has import/export)
 ┌────────────────────────────────────────────┐
 │ const local = 1          ← stays PRIVATE   │
 │                                            │
 │ declare global {         ← door to global  │
 │    interface Window { Razorpay?: ... }  ───┼──► merges into lib.dom Window
 │    var __pool: Pool | undefined         ───┼──► globalThis.__pool
 │    namespace NodeJS { interface ProcessEnv }┼──► merges with @types/node
 │ }                                          │
 └────────────────────────────────────────────┘
 script file (no import/export): write `interface Window {...}` directly — everything is global.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| declare global | Write into global scope from a module | Module से global scope में लिखना |
| globalThis | The global object (window/global) | Global object |
| Window | Browser global interface | Browser का global interface |
| ProcessEnv | Type of `process.env` | `process.env` का type |
| External module | File with import/export | Import/export वाली file |
| Augmentation | Extending existing types | मौजूदा types को बढ़ाना |

---

## ⚡ 3-Line Summary
English:
1. `declare global { ... }` inside a module adds to global types like `Window`, `globalThis` and `NodeJS.ProcessEnv`.
2. The file must be a module (`export {}`), globals you want on `globalThis` must be `var`, and runtime must really provide them.
3. It is declaration merging plus a trust-me promise — validate at runtime and keep augmentations minimal.

Hindi:
1. Module के अंदर `declare global { ... }` से `Window`, `globalThis` और `NodeJS.ProcessEnv` जैसे global types में जोड़ सकते हैं।
2. File module होनी चाहिए (`export {}`), `globalThis` पर चाहिए तो `var` लिखो, और runtime को असल में value देनी होगी।
3. यह declaration merging + भरोसे का वादा है — runtime पर validate करो और augmentations कम रखो।

---

## ➡️ Next Topic
**40. Excess Property Checks and Structural Typing** — why object literals get stricter checks than variables, and how TypeScript decides two types are compatible.
