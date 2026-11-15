# 35. Declaration Merging
# हिंदी में: Declaration Merging (एक ही नाम की declarations का जुड़ जाना)

> Verified with **TypeScript 5.x** (compiled with 5.9, `--strict`). Merging rules are stable across 5.x.

---

## 🔵 Simple Definition (English)
**Declaration merging** means that when the compiler finds **two or more declarations with the same name**, it combines them into a **single definition**. It works for `interface` + `interface`, `namespace` + `namespace`, `class` + `interface`, `function` + `namespace`, `enum` + `namespace`. It does **not** work for `type` aliases (duplicate identifier) and not for `class` + `class`.

## 🔵 सरल परिभाषा (Hindi)
**Declaration merging** का मतलब: जब compiler को **एक ही नाम की दो या ज़्यादा declarations** मिलती हैं, वह उन्हें **एक single definition** में जोड़ देता है। यह `interface` + `interface`, `namespace` + `namespace`, `class` + `interface`, `function` + `namespace`, `enum` + `namespace` के लिए काम करता है। `type` alias में यह **नहीं** चलता (duplicate identifier error), और `class` + `class` में भी नहीं।

---

## 🔴 Problem it Solves
Libraries ship types you cannot edit: Express's `Request` has no `user` property, but your auth middleware adds `req.user`. Without merging you would cast `(req as any).user` everywhere (no safety). Likewise, a global `Window` has no `Razorpay`. Merging lets you **re-open** the interface and add fields from your own code — the whole type system then knows about them.

## 🔴 यह क्यों बना? (Hindi)
Libraries के types आप edit नहीं कर सकते: Express के `Request` में `user` नहीं है, पर आपका auth middleware `req.user` जोड़ता है। Merging के बिना हर जगह `(req as any).user` करना पड़ता (कोई safety नहीं)। इसी तरह global `Window` में `Razorpay` नहीं होता। Merging से आप interface को **दोबारा खोलकर** अपने code से fields जोड़ सकते हो — पूरा type system उन्हें जान लेता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Declare `interface Order { id: string }` in one place.
Step 2 → Declare `interface Order { total: number }` elsewhere (same scope / same module augmentation).
Step 3 → Compiler merges members: `Order` is `{ id: string; total: number }`.
Step 4 → **Non-function members** must be unique or have the **same type** (else TS2717). **Function members** with the same name become **overloads**; later declarations get higher priority (appear first).
Step 5 → For modules, to merge with an imported type use **module augmentation** (`declare module "express-serve-static-core" { ... }`) — you must be inside a module (have an `import`/`export`).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → एक जगह `interface Order { id: string }` लिखो।
Step 2 → दूसरी जगह `interface Order { total: number }` लिखो (same scope / module augmentation)।
Step 3 → Compiler members merge कर देता है: `Order` बन जाता है `{ id: string; total: number }`।
Step 4 → **Non-function members** unique होने चाहिए या उनका **same type** होना चाहिए (वरना TS2717)। **Function members** same नाम के हों तो **overloads** बन जाते हैं; बाद वाली declaration की priority ज़्यादा होती है।
Step 5 → Imported type के साथ merge करने के लिए **module augmentation** (`declare module "..." { ... }`) चाहिए — file में कम से कम एक `import`/`export` होना ज़रूरी है।

---

## 🟡 Real World Example
**Swiggy's order service**: the base `Order` interface comes from a shared package (`id`, `items`). The delivery team adds `riderId` and `eta`; the payments team adds `paymentStatus` in their own file. Both teams write `interface Order { ... }` in their module augmentation — the final `Order` has all fields and nobody edited the shared package. Same trick: Express `Request` gets `user` after JWT middleware.

## 🟡 Real Example Hindi mein
**Swiggy की order service**: base `Order` interface shared package से आता है (`id`, `items`)। Delivery team `riderId` और `eta` जोड़ती है; payments team अपनी file में `paymentStatus` जोड़ती है। दोनों teams अपने module augmentation में `interface Order { ... }` लिखती हैं — final `Order` में सारे fields होते हैं और किसी ने shared package edit नहीं किया। यही trick: JWT middleware के बाद Express `Request` में `user` आ जाता है।

---

## 💻 Code Example — Basic

```typescript
// Interface merging: same name twice = one combined interface
interface Order { id: string; items: string[] } // base fields
interface Order { total: number }               // merged in: adds total

// Both declarations are visible together
const order: Order = { id: "o-101", items: ["Biryani"], total: 349 }; // needs all 3
console.log(order.id, order.total);
// Output:
// o-101 349
```

```typescript
// Function members with same name become OVERLOADS when merged
interface Parser { parse(input: string): string[] }   // first declaration
interface Parser { parse(input: number): number[] }   // second: adds overload

declare const parser: Parser; // pretend implementation exists
const a = parser.parse("a,b");  // picks string overload -> string[]
const b = parser.parse(42);     // picks number overload -> number[]
const lens: [number, number] = [a.length, b.length]; // both typed correctly
export { lens };
```

```typescript
// class + interface merge: add instance members without touching the class body
class Wallet { balance = 0 }                  // class with one field
interface Wallet { topUp(n: number): void }   // interface adds a method signature
// Wallet.prototype.topUp must be provided at runtime (TS only declares it)
Wallet.prototype.topUp = function (this: Wallet, n: number) { this.balance += n; };

const w = new Wallet(); // instance has both balance and topUp
w.topUp(500);           // compiles because of the merge
console.log(w.balance);
// Output:
// 500
```

## 💻 Code Example — Advanced

```typescript
// function + namespace merge: a function that carries static helpers
function createOrderId(prefix: string): string {
  return `${prefix}-${createOrderId.counter++}`; // uses the merged static member
}
namespace createOrderId {
  export let counter = 1; // exported so it becomes a property on the function
}
console.log(createOrderId("SW"), createOrderId("SW"));
// Output:
// SW-1 SW-2
```

```typescript
// enum + namespace merge: add helper functions to an enum
enum PaymentStatus { Pending, Paid, Failed } // numeric enum

namespace PaymentStatus {
  // Helper lives under the same name: PaymentStatus.isFinal(...)
  export function isFinal(s: PaymentStatus): boolean {
    return s === PaymentStatus.Paid || s === PaymentStatus.Failed;
  }
}
console.log(PaymentStatus.isFinal(PaymentStatus.Paid), PaymentStatus.isFinal(PaymentStatus.Pending));
// Output:
// true false
```

---

## 🟠 Node/Express + React Integration

```typescript
// file: types/express.d.ts   (module augmentation: has an import => it is a module)
import "express"; // makes this file a module so declare module = AUGMENT, not replace

declare module "express-serve-static-core" {
  // Express's Request extends this interface, so we re-open it
  interface Request {
    user?: { id: string; role: "admin" | "customer" }; // set by auth middleware
    requestId: string;                                  // set by logging middleware
  }
}
```

```typescript
// file: auth.ts   (uses the augmented Request, no casts)
import type { Request, Response, NextFunction } from "express";
import "./types/express"; // ensure augmentation file is part of the program

export function requireAdmin(req: Request, res: Response, next: NextFunction): void {
  // req.user is typed thanks to declaration merging
  if (req.user?.role !== "admin") {
    res.status(403).json({ error: "Admins only", requestId: req.requestId });
    return;
  }
  next(); // allowed
}
```

```tsx
// React: merging a global interface so window.__PRELOADED_STATE__ is typed
declare global {
  interface Window { __PRELOADED_STATE__?: { cartCount: number } } // merged into Window
}

export function Badge() {
  const count = window.__PRELOADED_STATE__?.cartCount ?? 0; // typed, no `any`
  return <span>{count}</span>;
}
```

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: Trying to merge `type` aliases or conflicting property types.**

```typescript
// ❌ Conflicting property type + duplicate type alias
interface Order { id: string; amount: number }
interface Order { amount: string } // wrong: same property, different type
type Cart = { id: string };
type Cart = { total: number };     // wrong: type aliases never merge
// error TS2717: Subsequent property declarations must have the same type.  Property 'amount' must be of type 'number', but here has type 'string'.
// error TS2300: Duplicate identifier 'Cart'.
```

```typescript
// ✅ Use interface for mergeable shapes, or an intersection for aliases
interface Order { id: string; amount: number }
interface Order { currency: "INR" | "USD" } // new property => fine
type Cart = { id: string };
type CartWithTotal = Cart & { total: number }; // alias: use & instead of redeclare
const c: CartWithTotal = { id: "c1", total: 10 };
console.log(c.total);
// Output:
// 10
```

**Mistake 2: Forgetting the file must be a module for augmentation.** If `express.d.ts` has no `import`/`export`, `declare module "express-serve-static-core"` becomes an *ambient declaration that replaces* instead of augmenting, and your `Request` loses all its original members. Always add `import "express"` or `export {}`.

**Mistake 3: Augmentation file not included.** If it is not in `tsconfig` `include`/`files`, `req.user` still errors even though the declaration exists.

---

## 🧠 Tricky Interview Question

```typescript
interface A { f(x: string): "s" }
interface A { f(x: number): "n" }
declare const a: A;
const r = a.f("hi"); // what type is r?
console.log(typeof r === "string");
```
**Answer:** `r` is `"s"`. The two `f` signatures merge into overloads; the string argument matches the first overload. Order matters for ambiguous cases: **later interface declarations' overloads are placed first** (higher priority), *except* signatures with a single string-literal parameter type which bubble to the top. Here the types are disjoint, so there is no ambiguity. (This `declare const` has no runtime value, so only the type is checked.)

---

## ⚫ Interview Questions + Answers

**Q1: What can and cannot be merged?**
A1: Can: interface+interface, namespace+namespace, class+interface, function+namespace, enum+namespace (and namespace into class). Cannot: type+type (TS2300), class+class, `let/const` twice.

**Q2: How do you add `user` to Express `Request`?**
A2: Create a `.d.ts` that is a module (`import "express"`) and write `declare module "express-serve-static-core" { interface Request { user?: JwtUser } }` (or `declare global { namespace Express { interface Request {...} } }`). Make sure it is included by `tsconfig`.

**Q3: Why `interface` for library-extension and not `type`?**
A3: Interfaces are open (mergeable), type aliases are closed. Libraries that expect augmentation (Express, Vue, Window) expose interfaces on purpose.

**Q4: What happens if two merged interfaces have the same non-function property with different types?**
A4: Compile error TS2717 ("Subsequent property declarations must have the same type"). Identical types are fine.

**Q5: Does merging create runtime code?**
A5: Interface merging is erased (types only). Namespace/enum/function merges emit real JS (the namespace IIFE adds properties onto the function/enum object). Class+interface merging declares members only; you must still implement them at runtime.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Extending third-party types you cannot edit (Express `Request`, `Window`, `process.env`)
- Adding static helpers to a function/enum (`namespace` merge)
- Splitting a large interface across files (plugins register their own fields)

❌ Avoid when:
- You own the type — just edit it or use `extends`/`&`
- You need a closed, exact shape (use `type`)
- It hides where a field comes from in a large codebase (document the augmentation file)

---

## 📊 Visual Diagram
```
 file A:  interface Order { id; items }  ─┐
 file B:  interface Order { riderId }    ─┼─►  Order = { id; items; riderId; paymentStatus }
 file C:  interface Order { paymentStatus}┘

 type Cart = {...}  +  type Cart = {...}   ✖ TS2300 Duplicate identifier
 function + namespace  ✔   enum + namespace ✔   class + interface ✔
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Declaration merging | Same-name declarations combine | Same नाम की declarations का जुड़ना |
| Module augmentation | `declare module "x"` to extend an import | Imported module को extend करना |
| Overload merge | Same method names become overloads | Same method names overloads बनते हैं |
| Ambient module | `declare module` without import (replaces) | बिना import वाला declare module |
| Open vs closed | interface is open, type alias closed | interface खुला, type बंद |

---

## ⚡ 3-Line Summary
English:
1. Same-named `interface`, `namespace`, `class+interface`, `function+namespace`, `enum+namespace` declarations merge; `type` aliases do not.
2. Use module augmentation (`declare module`, in a file with an import) to add fields like `req.user` to library types.
3. Conflicting property types give TS2717; the augmentation file must be included in `tsconfig`.

Hindi:
1. Same नाम की `interface`, `namespace`, `class+interface`, `function+namespace`, `enum+namespace` merge होती हैं; `type` alias नहीं।
2. Library types में `req.user` जैसे fields जोड़ने के लिए module augmentation (`declare module`, import वाली file में) इस्तेमाल करो।
3. Conflicting property types पर TS2717 आता है; augmentation file `tsconfig` में included होनी चाहिए।

---

## ➡️ Next Topic
**36. Modules, import type and export type** — how ES modules are typed, why `import type` erases at runtime, and `verbatimModuleSyntax`.
