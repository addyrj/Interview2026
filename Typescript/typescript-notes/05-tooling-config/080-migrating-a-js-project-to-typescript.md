# 80. Migrating a JS Project to TypeScript
# हिंदी में: JavaScript Project को TypeScript में Migrate करना

> Verified with **TypeScript 5.9.x**. `satisfies` needs 4.9+; `@ts-expect-error` needs 3.9+; `moduleResolution: "bundler"` needs 5.0+.

---

## 🔵 Simple Definition (English)
Migrating to TypeScript means **gradually** adding types to an existing JavaScript codebase without stopping feature work. You do it in layers: let `tsc` accept JS (`allowJs`), then type-check JS files via JSDoc (`checkJs`), then rename files to `.ts` one by one, and finally turn on `strict` flags one at a time until the whole project is strict.

## 🔵 सरल परिभाषा (Hindi)
TypeScript में migrate करने का मतलब है मौजूदा JavaScript codebase में **धीरे-धीरे** types जोड़ना, feature काम रोके बिना। आप layers में करते हैं: पहले `tsc` को JS लेने दो (`allowJs`), फिर JSDoc से JS files को type-check करो (`checkJs`), फिर files को एक-एक करके `.ts` rename करो, और आख़िर में `strict` flags एक-एक करके चालू करो जब तक पूरा project strict न हो जाए।

---

## 🔴 Problem it Solves
A big-bang rewrite of a 200-file Express + React app is risky: months without releases, merge conflicts, hidden regressions. Teams still want types because JS bugs like `order.totl` (typo) or `undefined is not a function` hit production. Incremental migration gives value **from day one** (autocomplete, typo detection) and lets the codebase stay shippable.

## 🔴 यह क्यों बना? (Hindi)
200-file के Express + React app का big-bang rewrite risky है: महीनों तक release नहीं, merge conflicts, छिपे regressions। फिर भी types चाहिए क्योंकि `order.totl` (typo) या `undefined is not a function` जैसे bugs production में आते हैं। Incremental migration पहले दिन से फ़ायदा देता है (autocomplete, typo detection) और codebase ship-able रहता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `npm i -D typescript @types/node @types/express` and add a `tsconfig.json` with `allowJs: true`, `checkJs: false`, `noEmit: true`. Nothing breaks.
Step 2 → Run tests + build; existing JS keeps working. Add `tsc --noEmit` to CI (non-blocking at first).
Step 3 → Turn on `checkJs: true` (or per-file `// @ts-check`) and fix errors; use JSDoc `@param`/`@type` for quick wins.
Step 4 → Convert **leaf files first** (utils, constants, DTOs) to `.ts`, then work inward to routes/services. New code is TS only.
Step 5 → Replace `any` hotspots: `unknown` + narrowing, shared interfaces in `types/`, `@types/*` for libs.
Step 6 → Enable strict flags one by one: `noImplicitAny` → `strictNullChecks` → rest of `strict`. Use `// @ts-expect-error` (not `@ts-ignore`) with a ticket reference for known gaps.
Step 7 → Switch `allowJs` off, make CI blocking, delete leftover `any`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `npm i -D typescript @types/node @types/express` और `tsconfig.json` में `allowJs: true`, `checkJs: false`, `noEmit: true`। कुछ नहीं टूटता।
Step 2 → Tests + build चलाओ; मौजूदा JS चलता रहता है। CI में `tsc --noEmit` जोड़ो (शुरू में non-blocking)।
Step 3 → `checkJs: true` (या file-level `// @ts-check`) चालू करो और errors ठीक करो; जल्दी फ़ायदे के लिए JSDoc `@param`/`@type` इस्तेमाल करो।
Step 4 → **Leaf files पहले** (utils, constants, DTOs) `.ts` बनाओ, फिर अंदर की ओर routes/services तक। नया code सिर्फ TS में।
Step 5 → `any` की जगहें हटाओ: `unknown` + narrowing, `types/` में shared interfaces, libs के लिए `@types/*`।
Step 6 → Strict flags एक-एक करके: `noImplicitAny` → `strictNullChecks` → बाकी `strict`। Known gaps के लिए `@ts-ignore` नहीं, `// @ts-expect-error` (ticket के साथ)।
Step 7 → `allowJs` बंद करो, CI blocking करो, बचे हुए `any` हटाओ।

---

## 🟡 Real World Example
A **Paytm-style wallet backend** has 180 JS files. Week 1: add tsconfig + `allowJs` (zero code change). Week 2: `// @ts-check` on `src/money/*.js`, which immediately catches `amount + "50"` string concatenation bugs. Weeks 3-6: `utils/`, `models/`, then `services/` renamed to `.ts`. New features are written in TS only. By quarter end `strict: true` is on and CI blocks on `tsc`.

## 🟡 Real Example Hindi mein
**Paytm जैसे wallet backend** में 180 JS files हैं। Week 1: tsconfig + `allowJs` (code में कोई बदलाव नहीं)। Week 2: `src/money/*.js` पर `// @ts-check`, जो तुरंत `amount + "50"` जैसे string concatenation bugs पकड़ लेता है। Weeks 3-6: `utils/`, `models/`, फिर `services/` को `.ts` rename किया। नए features सिर्फ TS में। Quarter के अंत तक `strict: true` और CI `tsc` पर block करता है।

---

## 💻 Code Example — Basic

```json
// tsconfig.json — STEP 1: the "do nothing harmful" starting config
{
  "compilerOptions": {
    "allowJs": true,          // tsc accepts .js files in the program
    "checkJs": false,         // but does NOT report errors in them yet
    "noEmit": true,           // type-check only; your existing build keeps emitting
    "target": "ES2022",       // modern output
    "module": "NodeNext",     // Node-aware modules
    "strict": false,          // start loose, tighten later
    "esModuleInterop": true,  // lets `import express from "express"` work with CJS typings
    "skipLibCheck": true      // ignore errors inside node_modules typings
  },
  "include": ["src"]          // only your source
}
```

```typescript
// Original JS (calcTotal.js) — no types, bug-prone:
//   function calcTotal(items, coupon) {
//     return items.reduce((s, i) => s + i.price * i.qty, 0) - (coupon ? coupon.off : 0);
//   }
//
// Migrated TS — same logic, now a typo or wrong shape is a compile error
interface CartItem { price: number; qty: number }       // shape of one cart line
interface Coupon { code: string; off: number }          // shape of a coupon

// coupon is optional (`?`), return type is explicit
export function calcTotal(items: CartItem[], coupon?: Coupon): number {
  const sub = items.reduce((s, i) => s + i.price * i.qty, 0); // subtotal
  return sub - (coupon ? coupon.off : 0);                      // subtract discount if present
}

console.log(calcTotal([{ price: 220, qty: 2 }], { code: "NEW50", off: 50 })); // 390
```

```typescript
// ❌ What strict mode says about un-typed JS-style parameters (noImplicitAny)
function applyCoupon(order, code) {
  return order.total - code.length;
}
// error TS7006: Parameter 'order' implicitly has an 'any' type.
// error TS7006: Parameter 'code' implicitly has an 'any' type.
```

## 💻 Code Example — Advanced

```javascript
// src/money/wallet.js — STEP 3: type a JS file WITHOUT renaming it, using JSDoc + @ts-check
// @ts-check

/**
 * @typedef {Object} Wallet
 * @property {string} userId   - owner id
 * @property {number} balance  - rupees, integer
 */

/**
 * Debit money from a wallet.
 * @param {Wallet} wallet
 * @param {number} amount
 * @returns {Wallet}
 */
export function debit(wallet, amount) {
  if (amount > wallet.balance) throw new Error("Insufficient balance"); // runtime guard
  return { ...wallet, balance: wallet.balance - amount };              // new object, types checked
}

// debit(wallet, "50")  -> with @ts-check: Argument of type 'string' is not assignable to parameter of type 'number'.
```

```typescript
// migration-helpers.ts — patterns used DURING migration

// 1) Temporary escape hatch with a paper trail (prefer over @ts-ignore: it errors if the bug is later fixed)
function legacyChargeCard(order: unknown): number { return order ? 1 : 0; } // typed wrapper over the old JS
// @ts-expect-error TODO(PAY-412): legacyChargeCard takes (order, retries) in the JS version
const charged: number = legacyChargeCard({ id: "o1" }, 3);

// 2) Replace `any` by `unknown` + a runtime guard, so callers must prove the shape
interface PaymentEvent { id: string; amount: number }                  // the shape we expect
function isPaymentEvent(x: unknown): x is PaymentEvent {               // type guard (topic 27)
  return typeof x === "object" && x !== null
    && typeof (x as Record<string, unknown>).id === "string"           // check id
    && typeof (x as Record<string, unknown>).amount === "number";      // check amount
}

// 3) Legacy JSON from an old Mongo/SQL query: validate at the boundary, then trust inside
export function parseEvent(raw: unknown): PaymentEvent {
  if (!isPaymentEvent(raw)) throw new Error("Bad payment event");      // fail loudly at the edge
  return raw;                                                          // narrowed to PaymentEvent
}

// 4) Gradual strictness: `satisfies` (TS 4.9+) types a config object without widening it
const flags = { allowJs: true, checkJs: false } satisfies Record<string, boolean>; // keeps literal keys
console.log(flags.allowJs, charged);
```

```bash
# Handy commands during migration (terminal, not TS)
npx tsc --noEmit                      # how many errors total?
npx tsc --noEmit | grep -c "error TS" # a number to chart in CI as it goes down
npx tsc --init                        # generate a starter tsconfig
```

---

## 🟠 Node/Express + React Integration

```typescript
// routes/orders.ts — an Express route migrated from orders.js (leaf-to-root order)
import express, { type Request, type Response } from "express"; // types are erased at runtime

const router = express.Router(); // router instance

// Params/body shapes were implicit in JS; now they are explicit
interface CreateOrderBody { userId: string; items: { sku: string; qty: number }[] }

// Request<Params, ResBody, ReqBody> generics (see topic 82)
router.post("/", (req: Request<{}, unknown, CreateOrderBody>, res: Response) => {
  const { userId, items } = req.body;            // typed, no `any`
  res.status(201).json({ userId, count: items.length }); // typo like items.lenght = compile error
});

export default router; // server.js can still `require`/import this during the migration
```

```typescript
// React side: rename Cart.jsx -> Cart.tsx and type the props first (topic 90)
interface CartProps { items: { name: string; price: number }[]; onCheckout: () => void }

export function Cart({ items, onCheckout }: CartProps) {
  const total = items.reduce((s, i) => s + i.price, 0); // number, inferred
  return <button onClick={onCheckout}>Pay Rs {total}</button>; // wrong prop type = compile error
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Big-bang rename of every file to `.ts` and turning on `strict` in one PR (3,000 errors, everyone sprays `any`).
✅ `allowJs` + `checkJs` per file, convert leaf modules first, tighten flags one at a time.

❌ Mistake 2: Using `@ts-ignore` everywhere; it silently stays even after the code is fixed.
✅ `// @ts-expect-error <ticket>` — the compiler complains when the suppression is no longer needed.

❌ Mistake 3: Typing everything as `any` to get green quickly.
```typescript
// ❌ any hides the bug forever
function total(order: any) { return order.totl; }   // typo compiles fine, returns undefined at runtime
// ✅ unknown/interface — typo now fails:
interface Order { total: number }
function totalOk(order: Order) { return order.total; } // 'totl' would be: Property 'totl' does not exist on type 'Order'
```

❌ Mistake 4: Forgetting `@types/*` for libraries (`@types/express`, `@types/node`); every import becomes implicit `any` (error TS7016 under strict).
✅ Install them as devDependencies, or write a small `declare module` shim (topic 74).

---

## 🧠 Tricky Interview Question
**Q:** "You turned on `strictNullChecks` and got 900 errors. You cannot fix them this sprint. How do you ship without disabling it?"

**A:** Don't disable it globally. Options: (1) keep it off in the main tsconfig and add a second `tsconfig.strict.json` whose `include` lists only already-clean folders — CI runs both, and you grow the include list each sprint (a "ratchet"); (2) use a per-file strict plugin; (3) fix by layers — boundary code (`req.body`, DB rows) gets zod/guards first because that is where `undefined` actually enters. Record the error count in CI and fail the build if it **increases**.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `allowJs` and `checkJs`?
A1: `allowJs` lets TS include `.js` files in the program (imports resolve, JS can be emitted). `checkJs` additionally reports type errors in them, using inference and JSDoc.

Q2: Why migrate leaf modules first?
A2: Leaves (utils, constants, pure functions) depend on nothing, so typing them gives accurate types to everything that imports them. Converting a route first would force you to type all its dependencies as `any`.

Q3: `@ts-ignore` vs `@ts-expect-error`?
A3: Both silence the next line. `@ts-expect-error` produces an **error** if the next line has no error any more, so stale suppressions are found. Prefer it, with a ticket id in the comment.

Q4: How do you type a legacy library that has no `@types`?
A4: First check DefinitelyTyped (`npm i -D @types/x`). Otherwise add `declare module "x";` (everything `any`) as a stopgap, then refine into a proper `.d.ts` with only the functions you use.

Q5: How do you stop the codebase regressing mid-migration?
A5: Make new/changed files TS-only via lint rule, run `tsc --noEmit` in CI with a ratchet (error count must not grow), and enable `noImplicitAny` before `strictNullChecks`, because implicit `any` is the biggest leak.

---

## 🔷 When to Use + When Not to Use
✅ Use incremental migration when:
- A large, live JS codebase with active releases
- Team is new to TS and needs a learning ramp

❌ Reconsider when:
- Tiny script/prototype (rewrite in TS is faster than migrating)
- Code is dying/being replaced soon — not worth typing

---

## 📊 Visual Diagram
```
 JS app ──► allowJs ──► checkJs/@ts-check ──► rename leaf .ts ──► inward ──► strict
  (0%)       (0 risk)      (JSDoc types)       (utils, DTOs)      (routes)   (100%)
                                  │
   CI ratchet:  errors:  900 → 640 → 300 → 80 → 0   (must never go UP)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `allowJs` | Include JS files in compilation | Compilation में JS files शामिल करना |
| `checkJs` | Type-check JS files | JS files को type-check करना |
| JSDoc | Comment-based types for JS | JS के लिए comment वाले types |
| `@ts-expect-error` | Suppress an expected error | अपेक्षित error दबाना |
| Ratchet | Error count may only go down | Error count सिर्फ घट सकता है |
| Leaf module | File with no local imports | बिना local imports वाली file |
| `noImplicitAny` | Disallow untyped params | बिना type के params मना |

---

## ⚡ 3-Line Summary
English:
1. Migrate gradually: `allowJs` → `checkJs` → rename leaf files → tighten `strict` flags.
2. Use `@ts-expect-error` with tickets, `unknown` + guards instead of `any`, and a CI error-count ratchet.
3. Type the boundaries (request bodies, DB rows, props) first — that is where bugs enter.

Hindi:
1. धीरे-धीरे migrate करो: `allowJs` → `checkJs` → leaf files rename → `strict` flags कसो।
2. `any` की जगह `unknown` + guards, tickets के साथ `@ts-expect-error`, और CI में error-count ratchet रखो।
3. Boundaries (request bodies, DB rows, props) पहले type करो — bugs वहीं से आते हैं।

---

## ➡️ Next Topic
**81. TypeScript with Node.js + Express Setup** — a clean, production-style TS Express project from scratch.
