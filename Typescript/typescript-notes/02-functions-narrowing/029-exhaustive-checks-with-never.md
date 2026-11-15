# 29. Exhaustive Checks with never
# हिंदी में: `never` से Exhaustive Checks (हर case handle हुआ या नहीं)

> Verified with TypeScript 5.x (5.9) under `tsc --strict`. `satisfies never` form needs TS 4.9+.

---

## 🔵 Simple Definition (English)
An **exhaustive check** uses the `never` type to make the compiler prove that every member of a union has been handled. In the final `default` branch the remaining type is `never`; assigning it to a `never` variable compiles only if nothing is left. If you later add a new union member and forget a case, the build **fails** at that exact line.

## 🔵 सरल परिभाषा (Hindi)
**Exhaustive check** `never` type का उपयोग करके compiler से साबित करवाता है कि union का हर member handle हो चुका है। आख़िरी `default` branch में बचा हुआ type `never` होता है; उसे `never` variable में assign करना तभी compile होता है जब कुछ बचा न हो। बाद में नया union member जोड़कर कोई case भूल जाओ तो build उसी line पर **fail** हो जाता है।

---

## 🔴 Problem it Solves
Add `"refunded"` to an order status union and every `switch` in the codebase silently falls through to a wrong default (maybe returning `undefined`). These bugs surface in production. An exhaustive check turns "you forgot a case" into a compile error in every place that needs updating.

## 🔴 यह क्यों बना? (Hindi)
Order status union में `"refunded"` जोड़ो तो codebase के हर `switch` में वह चुपचाप गलत default पर चला जाता है (शायद `undefined` लौटाता है)। ऐसे bugs production में दिखते हैं। Exhaustive check "case भूल गए" को हर उस जगह compile error बना देता है जहाँ update ज़रूरी है।

---

## 🟢 How it Works — Step by Step

Step 1 → `never` is the type with NO values (empty set). Nothing is assignable to `never` except `never`.
Step 2 → Narrowing removes handled members from the union branch by branch.
Step 3 → After all cases, the remaining type is `never`.
Step 4 → In `default`, write `const _x: never = value;` (or call `assertNever(value)`).
Step 5 → If a member is missing, `value` is that member, not `never`, so the assignment errors.
Step 6 → `assertNever(x: never): never` also throws at runtime, protecting against bad data that bypassed types (API sends an unknown status).
Step 7 → Modern alternative: `value satisfies never` (TS 4.9+). Also `noImplicitReturns` + a function return type catches missing returns.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → `never` वह type है जिसकी कोई value नहीं (खाली set)। `never` में सिर्फ़ `never` ही assign हो सकता है।
Step 2 → Narrowing branch-दर-branch handled members को union से हटाती जाती है।
Step 3 → सब cases के बाद बचा हुआ type `never` होता है।
Step 4 → `default` में `const _x: never = value;` लिखो (या `assertNever(value)` बुलाओ)।
Step 5 → कोई member छूटा हो तो `value` वही member है, `never` नहीं, इसलिए assignment error देता है।
Step 6 → `assertNever(x: never): never` runtime पर throw भी करता है, ताकि API से आया अनजान status (types को bypass करके) पकड़ा जाए।
Step 7 → आधुनिक विकल्प: `value satisfies never` (TS 4.9+)। साथ में `noImplicitReturns` और function return type भी छूटे हुए return पकड़ते हैं।

---

## 🟡 Real World Example
**Zomato order tracking** has statuses `placed | preparing | out_for_delivery | delivered`. Product adds `cancelled`. With an exhaustive `statusLabel()` the build immediately points to the label function, the colour function and the notification mapper that need a new case.

## 🟡 Real Example Hindi mein
**Zomato order tracking** में statuses `placed | preparing | out_for_delivery | delivered` हैं। Product `cancelled` जोड़ता है। Exhaustive `statusLabel()` होने पर build तुरंत label function, colour function और notification mapper दिखा देता है जिनमें नया case चाहिए।

---

## 💻 Code Example — Basic

```typescript
// Union of order statuses
type Status = "placed" | "preparing" | "delivered"; // three states for now

// Helper: only accepts 'never', so it compiles only when all cases are handled
function assertNever(x: never): never {
  throw new Error(`Unhandled value: ${JSON.stringify(x)}`); // runtime safety net too
}

function label(s: Status): string {
  switch (s) {
    case "placed":
      return "Order placed"; // s: "placed"
    case "preparing":
      return "Cooking..."; // s: "preparing"
    case "delivered":
      return "Delivered"; // s: "delivered"
    default:
      return assertNever(s); // s: never here, so this compiles
  }
}

console.log(label("placed"), "|", label("delivered")); // runs fine
```

Run with `npx tsx`:

```
Order placed | Delivered
```

```typescript
// ❌ Now imagine product adds "cancelled" but nobody updates label()
type Status2 = "placed" | "preparing" | "delivered" | "cancelled"; // new member
function assertNever2(x: never): never { throw new Error(String(x)); } // helper
function label2(s: Status2): string {
  switch (s) {
    case "placed": return "Order placed"; // handled
    case "preparing": return "Cooking..."; // handled
    case "delivered": return "Delivered"; // handled
    default: return assertNever2(s); // ❌ s is "cancelled" here
  }
}
```

Real compiler output:

```
error TS2345: Argument of type '"cancelled"' is not assignable to parameter of type 'never'.
```

## 💻 Code Example — Advanced

```typescript
// Advanced: exhaustive Record mapping, satisfies never, and reducer with action union

type Action =
  | { type: "add"; sku: string; qty: number } // add item
  | { type: "remove"; sku: string } // remove item
  | { type: "clear" }; // clear cart

type State = Record<string, number>; // sku -> qty

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "add": return { ...state, [action.sku]: (state[action.sku] ?? 0) + action.qty }; // add
    case "remove": { const next = { ...state }; delete next[action.sku]; return next; } // remove
    case "clear": return {}; // clear
    default: {
      action satisfies never; // TS 4.9+: errors at compile time if a new action is unhandled
      return state; // unreachable at type level
    }
  }
}

// Exhaustive lookup table: a Record keyed by the union forces every key to exist
type Method = "upi" | "card" | "cod"; // payment methods
const feePercent: Record<Method, number> = {
  upi: 0, // free
  card: 2, // 2 percent
  cod: 0, // cash
}; // removing a key or adding a Method without a key is a compile error

// Extra runtime-safe handling when data comes from outside (API may send new values)
function fee(m: string): number {
  if (m in feePercent) return feePercent[m as Method]; // known value
  throw new Error(`unknown method: ${m}`); // unknown at runtime
}

let s: State = {}; // start empty
s = reducer(s, { type: "add", sku: "dosa", qty: 2 }); // add 2
s = reducer(s, { type: "add", sku: "dosa", qty: 1 }); // add 1 more
console.log(s, fee("card")); // { dosa: 3 } 2
s = reducer(s, { type: "clear" }); // clear
console.log(Object.keys(s).length); // 0
```

Run with `npx tsx`:

```
{ dosa: 3 } 2
0
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: map domain errors to HTTP status exhaustively
import express from "express"; // express
import type { Request, Response, NextFunction } from "express"; // types

// Union of known domain errors
type DomainError =
  | { kind: "not_found"; entity: string } // 404
  | { kind: "invalid"; field: string } // 400
  | { kind: "conflict"; reason: string }; // 409

function toStatus(e: DomainError): number {
  switch (e.kind) {
    case "not_found": return 404; // e.entity available
    case "invalid": return 400; // e.field available
    case "conflict": return 409; // e.reason available
    default: { const _never: never = e; return _never; } // adding a member breaks the build here
  }
}

const app = express(); // app
app.get("/orders/:id", (_req: Request, res: Response, next: NextFunction) => {
  const err: DomainError = { kind: "not_found", entity: "order" }; // pretend lookup failed
  next(err); // hand over to error middleware
});
app.use((err: DomainError, _req: Request, res: Response, _next: NextFunction) => {
  res.status(toStatus(err)).json(err); // exhaustive mapping
});
```

```tsx
// React: exhaustive rendering of a state union
import type { ReactNode } from "react"; // type

type Load = { s: "idle" } | { s: "loading" } | { s: "error"; msg: string } | { s: "ok"; n: number }; // states

export function Panel({ v }: { v: Load }): ReactNode {
  switch (v.s) {
    case "idle": return null; // nothing yet
    case "loading": return <p>Loading</p>; // spinner
    case "error": return <p>{v.msg}</p>; // error text
    case "ok": return <p>{v.n} items</p>; // data
    default: { const _x: never = v; return _x; } // new state forces an update here
  }
}
```

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: A `default` that returns a fallback (hides missing cases).**

```typescript
// ❌ WRONG: the quiet default swallows new members and compiles forever
type Role = "admin" | "user" | "guest";
function canDelete(r: Role): boolean {
  switch (r) {
    case "admin": return true; // only admin
    default: return false; // silently covers "user", "guest", and any future role
  }
}
console.log(canDelete("user")); // false, no warning when a new role appears
// ✅ RIGHT: list every case and end with assertNever(r) so a new role breaks the build.
```

**Mistake 2: Missing return (no default at all).**

```typescript
// ❌ WRONG: function can fall off the end for a missing member
type Color = "red" | "green" | "blue";
function hex(c: Color): string {
  switch (c) {
    case "red": return "#f00";
    case "green": return "#0f0";
  } // blue not handled
}
```

Real compiler output:

```
error TS2366: Function lacks ending return statement and return type does not include 'undefined'.
```

**Mistake 3: Passing a non-narrowed value to `assertNever` (wrong type).**

```typescript
// ❌ WRONG: assertNever called in a branch where a member is still possible
function assertNever(x: never): never { throw new Error("x"); } // helper
function f(v: "a" | "b"): string {
  if (v === "a") return "A";
  return assertNever(v); // ❌ v is "b" here
}
```

Real compiler output:

```
error TS2345: Argument of type '"b"' is not assignable to parameter of type 'never'.
```

---

## 🧠 Tricky Interview Question

**Q: The reducer is exhaustive at compile time. A newer backend now sends `{ type: "refund" }` and the old front-end bundle still runs. What happens, and how do you defend?**

```typescript
// Compile-time exhaustive, but data came from outside via JSON
type Action = { type: "add" } | { type: "clear" }; // known actions

function assertNever(x: never): never {
  throw new Error(`Unhandled action: ${JSON.stringify(x)}`); // runtime defence
}
function handle(a: Action): string {
  switch (a.type) {
    case "add": return "added"; // known
    case "clear": return "cleared"; // known
    default: return assertNever(a); // compile-time proof + runtime throw
  }
}

const fromServer = JSON.parse('{"type":"refund"}') as Action; // lie: cast from JSON
try { handle(fromServer); } catch (e) { console.log((e as Error).message); } // what prints?
```

Real output with `npx tsx`:

```
Unhandled action: {"type":"refund"}
```

**Answer:** Types are erased at runtime; `never` guarantees nothing about data that bypassed the type system (here a lying `as` cast). Because `assertNever` also **throws**, the unknown action is caught loudly instead of silently ignored. Real defence: validate server data (Zod discriminated union) at the boundary, and keep `assertNever`'s runtime throw.

---

## ⚫ Interview Questions + Answers

Q1: What is the `never` type?
A1: The empty type: no value can have it. It is the return type of functions that never return (throw/infinite loop), the result of fully narrowed unions, and the bottom type assignable to everything.

Q2: How does an exhaustive switch work?
A2: Each `case` narrows the union. After all cases the leftover type is `never`, so `const x: never = value` compiles. A missing case leaves a real type, which is not assignable to `never`, causing the error.

Q3: `assertNever` vs `satisfies never`?
A3: `assertNever(x)` gives a compile check and a runtime throw. `x satisfies never` (TS 4.9+) is compile-only with no helper function.

Q4: Why is a default returning a fallback dangerous?
A4: It compiles forever and hides new union members, defeating the purpose. Use `assertNever` in `default`.

Q5: Does `Record<Union, T>` give exhaustiveness?
A5: Yes. Every key of the union must exist in the object, so adding a member without a key fails to compile. Use it for label/colour/handler maps.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Switching over discriminated unions, status enums, reducers, action types, error kinds
- Mapping tables keyed by a union (`Record<Union, X>`)
- Anywhere a new variant must force code updates

❌ Avoid when:
- A deliberate fallback is correct (e.g., "all other roles are denied"), but then comment it
- The input is external and not validated: also keep a runtime throw, or validate first
- The union is open-ended (plain `string`)

---

## 📊 Visual Diagram
```
 type Status = A | B | C
 switch(s):
   case A  →  remaining: B | C
   case B  →  remaining: C
   case C  →  remaining: never
   default →  s: never  ✅ compiles (all handled)

 Add D to the union:
   default →  s: D      ❌  "Type 'D' is not assignable to type 'never'"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| never | Type with no values | बिना किसी value वाला type |
| Exhaustive check | Proof all cases handled | सब cases handled होने का प्रमाण |
| assertNever | Helper taking `never`, throws | `never` लेने वाला, throw करने वाला helper |
| Bottom type | Subtype of every type | हर type का subtype |
| satisfies never | Compile-only exhaustive check (4.9+) | सिर्फ़ compile-time exhaustive check (4.9+) |

---

## ⚡ 3-Line Summary
English:
1. After handling every union member the leftover type is `never`.
2. Assign it to `never` (or `assertNever`) in `default` so new members break the build.
3. Keep a runtime throw too, because external data can bypass types.

Hindi:
1. Union का हर member handle करने के बाद बचा type `never` होता है।
2. `default` में उसे `never` में assign करो (या `assertNever`) ताकि नए members build तोड़ें।
3. Runtime throw भी रखो, क्योंकि बाहर का data types को bypass कर सकता है।

---

## ➡️ Next Topic
**30. Index Signatures** — typing objects whose keys are not known in advance (dictionaries, query params, headers).
