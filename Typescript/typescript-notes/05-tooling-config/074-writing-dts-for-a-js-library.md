# 74. Writing .d.ts for a JS Library
# हिंदी में: JS Library के लिए .d.ts लिखना

> Verified with TypeScript 5.9 (`tsc --strict`) on a real sample CommonJS library `cart-kit`. `export =` + `esModuleInterop` rules apply to all TS 5.x.

---

## 🔵 Simple Definition (English)
Writing a `.d.ts` for a JS library means **describing its public API with types only** - functions (with overloads), classes, constants, callback shapes and the way the module is exported (`export =` for `module.exports = ...`, named `export` for `exports.x = ...`, `export default` for ESM). The JavaScript stays untouched; the `.d.ts` is the **contract** TypeScript checks your usage against.

## 🔵 सरल परिभाषा (Hindi)
JS library के लिए `.d.ts` लिखने का मतलब है **उसके public API को सिर्फ types से बयान करना** - functions (overloads समेत), classes, constants, callback की shape और module export करने का तरीका (`module.exports = ...` के लिए `export =`, `exports.x = ...` के लिए named `export`, ESM के लिए `export default`)। JavaScript नहीं बदलता; `.d.ts` वह **contract** है जिसके against TypeScript तुम्हारा उपयोग जाँचता है।

---

## 🔴 Problem it Solves
Many internal or old npm packages are plain CommonJS JS and will never be rewritten. Without a hand-written `.d.ts`, they are `any` (TS7016 / implicit any), so mistakes like `format("5")` reach production. Writing declarations is the fastest way to **bring such a library into a strict codebase**, and the skill is also tested in interviews ("how would you type a library that exports a function with properties?").

## 🔴 यह क्यों बना? (Hindi)
कई internal या पुराने npm packages साधारण CommonJS JS हैं और कभी दोबारा नहीं लिखे जाएँगे। हाथ से लिखे `.d.ts` के बिना वे `any` हैं (TS7016 / implicit any), इसलिए `format("5")` जैसी गलतियाँ production तक पहुँचती हैं। Declarations लिखना ऐसी library को **strict codebase में लाने का सबसे तेज़ तरीका** है, और यह skill interviews में भी पूछी जाती है ("जो library एक function export करती है जिस पर properties भी हैं, उसे कैसे type करोगे?")।

---

## 🟢 How it Works — Step by Step

Step 1 → Read how the JS exports: `module.exports = fn` (single export), `exports.a = ...` (named exports), or ESM `export`.
Step 2 → Pick the matching declaration style: `export = x` (CommonJS single export), named `export function/const`, or `export default`.
Step 3 → When the exported function **also has properties** (like `cartKit.format`), merge a function and a `namespace` of the **same name**: `declare function cartKit(...)` + `declare namespace cartKit { ... }` (declaration merging).
Step 4 → Describe each function: parameter types, optional params (`?`), return type; for multi-shape functions write **overloads** (most specific first).
Step 5 → Describe callbacks as a named function type (`type ChangeCallback = (err: Error | null, state?: State) => void`).
Step 6 → Put the file next to the JS as `index.d.ts` (or set `"types"` in `package.json`); for a package without access to the source, use `declare module "name" { ... }` in a local `.d.ts`.
Step 7 → Test it: write a small `.ts` that calls every function **correctly**, and one that calls them **wrongly** and expect errors.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → देखो JS export कैसे करती है: `module.exports = fn` (एक export), `exports.a = ...` (named exports), या ESM `export`।
Step 2 → मेल खाता declaration style चुनो: `export = x` (CommonJS का एक export), named `export function/const`, या `export default`।
Step 3 → जब exported function पर **properties भी हों** (जैसे `cartKit.format`), तो एक ही नाम का function और `namespace` merge करो: `declare function cartKit(...)` + `declare namespace cartKit { ... }` (declaration merging)।
Step 4 → हर function describe करो: parameter types, optional params (`?`), return type; कई shapes वाले function के लिए **overloads** लिखो (सबसे specific पहले)।
Step 5 → Callbacks को named function type में लिखो (`type ChangeCallback = (err: Error | null, state?: State) => void`)।
Step 6 → File को JS के पास `index.d.ts` नाम से रखो (या `package.json` में `"types"` दो); जिस package का source हाथ में नहीं, उसके लिए local `.d.ts` में `declare module "name" { ... }` लिखो।
Step 7 → Test करो: एक `.ts` जो हर function को **सही** call करे, और एक जो **गलत** call करे और errors की उम्मीद रखे।

---

## 🟡 Real World Example
**Swiggy's older cart module** `cart-kit` is a 2017 CommonJS file: `module.exports = function cartKit(items)` with extra properties `format`, `discount`, `onChange`, `VERSION` and a `Cart` class. The platform team writes a single `index.d.ts` (50 lines). From that day all 40 services that import it get autocomplete, and the compiler rejects `cartKit.format("5")`.

## 🟡 Real Example Hindi mein
**Swiggy का पुराना cart module** `cart-kit` 2017 की CommonJS file है: `module.exports = function cartKit(items)` और अतिरिक्त properties `format`, `discount`, `onChange`, `VERSION` व एक `Cart` class। Platform team एक `index.d.ts` (50 lines) लिखती है। उसी दिन से इसे import करने वाली सभी 40 services को autocomplete मिलता है और compiler `cartKit.format("5")` को reject कर देता है।

---

## 💻 Code Example — Basic

The JavaScript library (CommonJS), exactly as it exists - we will not edit it:

```text
// node_modules/cart-kit/index.js
function cartKit(items) { return items.reduce((s, i) => s + i.price * (i.qty || 1), 0); }
cartKit.VERSION = "1.2.0";
cartKit.format = function (n, opts) { opts = opts || {}; return (opts.symbol || "Rs.") + n.toFixed(opts.decimals === undefined ? 2 : opts.decimals); };
cartKit.discount = function (a, b) {
  if (typeof a === "number" && typeof b === "number") return a - a * b / 100;
  if (typeof a === "string") return a.length;
  return a;
};
cartKit.onChange = function (cb) { setTimeout(() => cb(null, { total: 99 }), 1); };
cartKit.Cart = class Cart { constructor(owner) { this.owner = owner; this.items = []; }
  add(i) { this.items.push(i); return this; } total() { return cartKit(this.items); } };
module.exports = cartKit;
```

The declaration file we write for it:

```typescript
// script
// flags: --module commonjs --moduleResolution node10 --ignoreDeprecations 5.0
// node_modules/cart-kit/index.d.ts   (module.exports = function WITH properties)
declare function cartKit(items: cartKit.Item[]): number; // the function itself

declare namespace cartKit { // merged with the function above: adds the properties
  interface Item { name?: string; price: number; qty?: number } // cart line
  interface FormatOptions { symbol?: string; decimals?: number } // options bag
  const VERSION: string; // constant (read-only from outside)
  function format(n: number, opts?: FormatOptions): string; // optional 2nd arg

  function discount(price: number, percent: number): number; // overload 1
  function discount(label: string): number; // overload 2

  type ChangeCallback = (err: Error | null, state?: { total: number }) => void; // callback shape
  function onChange(cb: ChangeCallback): void;

  class Cart { // class exposed as a property
    constructor(owner: string);
    readonly owner: string; // set once in the constructor
    items: Item[];
    add(item: Item): this; // `this` return keeps chaining typed (note 70)
    total(): number;
  }
}

export = cartKit; // matches `module.exports = cartKit`
```

## 💻 Code Example — Advanced

Using the library (this real file compiled and ran: `Rs.250.00 1.2.0`, `15 180 3`, `99`):

```typescript
// flags: --module commonjs --moduleResolution node10 --ignoreDeprecations 5.0
import cartKit = require("cart-kit"); // the correct import for `export =` (module: commonjs/nodenext)

const total = cartKit([{ price: 100, qty: 2 }, { price: 50 }]); // function call -> number
console.log(cartKit.format(total), cartKit.VERSION); // Rs.250.00 1.2.0

const cart = new cartKit.Cart("Asha").add({ price: 10 }).add({ price: 5 }); // chained, still Cart
console.log(cart.total()); // 15
console.log(cartKit.discount(200, 10), cartKit.discount("abc")); // 180 3  (both overloads)

cartKit.onChange((err, state) => { // err and state are contextually typed
  if (err) throw err; // Error | null narrowed
  console.log(state?.total); // 99
});
```

The `export =` rule for default imports (real compiler output):

```typescript
// flags: --module commonjs --moduleResolution node10 --ignoreDeprecations 5.0
import cartKit from "cart-kit"; // ❌ without esModuleInterop (module commonjs): error TS1259: Module '".../cart-kit/index"' can only be default-imported using the 'esModuleInterop' flag
console.log(cartKit.format(1)); // with esModuleInterop or module nodenext/bundler this line compiles fine
```

Wrong usage is rejected (real output from `tsc --strict` on a file with these lines):

```typescript
import cartKit from "cart-kit"; // OK under module: esnext + moduleResolution: bundler
cartKit.format("5"); // ❌ error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.
cartKit.discount(1, 2, 3); // ❌ error TS2554: Expected 1-2 arguments, but got 3.
new cartKit.Cart(5); // ❌ error TS2345: Argument of type 'number' is not assignable to parameter of type 'string'.
cartKit.VERSION = "2"; // ❌ error TS2540: Cannot assign to 'VERSION' because it is a read-only property.
cartKit.nope(); // ❌ error TS2339: Property 'nope' does not exist on type 'typeof cartKit'.
```

Other export shapes cheat-sheet:

```text
JS:  exports.toRupees = fn;            .d.ts:  export function toRupees(paise: number): string;
JS:  module.exports = class Foo {}     .d.ts:  declare class Foo {...}   export = Foo;
JS:  export default function () {}     .d.ts:  declare function f(): void;  export default f;
JS:  global via <script> (UMD)         .d.ts:  export as namespace MyLib;   (plus the exports)
```
For the UMD form the compiler says `error TS2686: 'RupeeFmt' refers to a UMD global, but the current file is a module. Consider adding an import instead.` when the global is used inside a module file (real output).

---

## 🟠 Node/Express + React Integration

```typescript
// script
// src/types/express-extras.d.ts - typing a tiny untyped Express middleware package "rate-gate"
declare module "rate-gate" {
  import type { RequestHandler } from "express"; // types from @types/express
  interface RateGateOptions { windowMs: number; max: number } // config
  function rateGate(opts: RateGateOptions): RequestHandler; // returns an Express middleware
  export = rateGate; // module.exports = rateGate
}
```

```typescript
// flags: --module commonjs --moduleResolution node10 --ignoreDeprecations 5.0 --esModuleInterop
import express from "express";
import cartKit = require("cart-kit"); // our typed CommonJS lib (module: commonjs / nodenext in a CJS package)

const app = express();
app.use(express.json());

app.post("/cart/total", (req, res) => {
  const items = req.body as cartKit.Item[]; // reuse the library's exported interface
  const total = cartKit(items); // number
  res.json({ total, label: cartKit.format(total) }); // typed helpers
});
```

```tsx
// Frontend: do NOT import the CJS library in React; share only its types
interface Item { name?: string; price: number; qty?: number } // local copy of the library's Item type

export function CartLine({ item }: { item: Item }) {
  return <li>{item.name ?? "item"} x {item.qty ?? 1} = Rs.{item.price * (item.qty ?? 1)}</li>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using named exports when JS uses `module.exports = fn`
```typescript
// script
declare module "bad-lib" {
  export function run(): void; // lie: the JS exports a function itself, not an object with `run`
}
```
Consumers compile fine and crash at runtime (`run is not a function`). Use `export =`.

❌ Mistake 2: Writing a `.d.ts` that does not match the JS (declaration drift)
The compiler trusts the `.d.ts` blindly. Keep it in a test (`tsc --noEmit` on usage files) and review it when the library changes.

❌ Mistake 3: Wrong overload order (generic one first)
```typescript
declare function parse(x: unknown): unknown; // too general - always chosen first
declare function parse(x: string): string; // can never be selected
```
✅ List the most specific overload first.

❌ Mistake 4: Putting the type `any` everywhere "to finish quickly"
Prefer `unknown` for inputs you do not know and real interfaces for outputs; otherwise the declaration gives a false sense of safety.

❌ Mistake 5: `import cartKit from "cart-kit"` with `export =` and no interop
Shown above with the real message `TS1259`. Fix: `esModuleInterop` (default in `module: nodenext`/`bundler` setups) or `import x = require()`.

---

## 🧠 Tricky Interview Question

Q: In the `.d.ts` above, why is `cartKit` declared **twice** (`declare function cartKit` and `declare namespace cartKit`) and why does it not error?

Answer: Declaration merging. A function and a namespace with the same name merge into one entity that is **callable and has properties** - the exact shape of `module.exports = fn; fn.format = ...`. The namespace must come **after** the function in the same file. Interfaces/types inside the namespace are exposed as `cartKit.Item`. This is the standard trick for typing jQuery-style/Express-style libraries.

---

## ⚫ Interview Questions + Answers

Q1: `export =` vs `export default`?
A1: `export =` models `module.exports = x` (CommonJS). `export default` models ES `export default`. They interoperate only via `esModuleInterop`/`allowSyntheticDefaultImports`.

Q2: How do you type a callback with an error-first signature?
A2: `type Cb = (err: Error | null, result?: T) => void`. Modern alternative: add a Promise overload returning `Promise<T>`.

Q3: How do you type a function that returns different types for different inputs?
A3: Overloads (specific first) or a generic with conditional type; overloads are simplest in `.d.ts`.

Q4: Do you need `declare` in a `.d.ts`?
A4: Top-level declarations in a `.d.ts` need `declare` (or `export`) unless inside `declare module`/`declare namespace`; interfaces and type aliases do not need it.

Q5: How would you verify a `.d.ts` is correct?
A5: Usage tests with `// @ts-expect-error` lines, `tsc --noEmit` in CI, and tools such as `dtslint`/`tsd`/Are the Types Wrong for published packages.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A JS dependency has no types and no `@types` package
- Typing internal legacy modules gradually while migrating to TS

❌ Avoid when:
- The library already ships types or a maintained `@types` exists
- It is your own code - convert it to TS (or `// @ts-check` + JSDoc) and let `tsc --declaration` generate the `.d.ts`

---

## 📊 Visual Diagram
```
  index.js                               index.d.ts
  ─────────────────────────              ──────────────────────────────
  function cartKit(items){..}     ───►   declare function cartKit(items: Item[]): number;
  cartKit.format = ...            ───►   declare namespace cartKit {
  cartKit.Cart  = class {..}                  function format(...): string;
  module.exports = cartKit        ───►        class Cart {...}   }
                                         export = cartKit;
        ▲                                         │
        └──── TS trusts this contract ◄───────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `export =` | Declare `module.exports = x` | `module.exports = x` का declaration |
| Namespace merging | Function + namespace of same name | एक नाम का function + namespace जुड़ना |
| Overload | Several call signatures | एक function के कई call signatures |
| UMD global | Library usable as global and module | Global और module दोनों रूप में library |
| `esModuleInterop` | Lets `import x from` work for CJS | CJS के लिए default import चलाता है |
| Declaration drift | `.d.ts` out of sync with JS | `.d.ts` का JS से अलग हो जाना |

---

## ⚡ 3-Line Summary
English:
1. A `.d.ts` is a types-only contract for existing JS; match it to how the JS exports (`export =`, named, default).
2. Function + same-named `namespace` models "function with properties"; overloads go specific-first.
3. Test the declaration with correct and incorrect usage; never let it drift from the JS.

Hindi:
1. `.d.ts` मौजूदा JS का types-only contract है; JS जैसे export करती है वैसा ही लिखो (`export =`, named, default)।
2. Function + उसी नाम का `namespace` "properties वाला function" बनाता है; overloads में specific पहले।
3. सही और गलत usage से declaration को test करो; उसे JS से अलग मत होने दो।

---

## ➡️ Next Topic
**75. Project References and Incremental Builds** - Splitting a monorepo into `tsc --build` projects for faster, correct builds.
