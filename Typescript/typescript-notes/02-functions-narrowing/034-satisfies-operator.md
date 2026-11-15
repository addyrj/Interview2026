# 34. satisfies Operator
# हिंदी में: satisfies Operator (type check बिना type चौड़ा किए)

> Verified with **TypeScript 5.x** (compiled with 5.9, `--strict`). `satisfies` is **TS 4.9+** feature. `as const satisfies` combo works on 5.x.

---

## 🔵 Simple Definition (English)
`expr satisfies T` checks that the expression **matches** type `T`, but it does **not** change the inferred type of the expression. A type annotation (`const x: T = ...`) *widens* the variable to `T` and throws away the precise literal information. `satisfies` gives you both: validation against `T` **and** the narrow inferred type (exact keys, literal values, tuples).

## 🔵 सरल परिभाषा (Hindi)
`expr satisfies T` सिर्फ **check** करता है कि expression type `T` से match करता है, लेकिन expression का inferred type **बदलता नहीं**। Annotation (`const x: T = ...`) variable को `T` तक **चौड़ा (widen)** कर देता है और exact keys/literal values खो जाती हैं। `satisfies` दोनों देता है: `T` के against validation **और** narrow inferred type (exact keys, literals, tuples)।

---

## 🔴 Problem it Solves
Before 4.9 you had two bad choices for a config object:
1. Annotate it (`const routes: Record<string, Route>`) — typos like `routes.ordres` compile silently because *any* string key is allowed, and every value is just `Route` (no literal info).
2. Don't annotate — you lose the safety net: a wrong value (`auth: "yes"`) is only caught far away where the object is used.

`satisfies` fixes this: the object is validated **at the definition site**, yet keeps its exact shape (`routes.orders` exists, `routes.ordres` is an error).

## 🔴 यह क्यों बना? (Hindi)
4.9 से पहले config object के लिए दो खराब रास्ते थे:
1. Annotate करो (`const routes: Record<string, Route>`) — तब `routes.ordres` जैसी typo चुपचाप compile हो जाती है क्योंकि कोई भी string key allowed है, और हर value सिर्फ `Route` रह जाती है।
2. Annotate मत करो — तब safety नहीं मिलती; गलत value (`auth: "yes"`) object use करते समय दूर कहीं पकड़ी जाती है।

`satisfies` इसे ठीक करता है: object **वहीं definition पर** validate हो जाता है, फिर भी उसकी exact shape बनी रहती है।

---

## 🟢 How it Works — Step by Step

Step 1 → Write the expression normally (object literal, array, etc.).
Step 2 → Add `satisfies SomeType` after it. The compiler checks assignability of the expression to `SomeType`.
Step 3 → The expression is **contextually typed** by `SomeType` (so `"GET"` stays the literal `"GET"`, `[1,2,3]` can become a tuple).
Step 4 → If it fails, you get an error **pointing at the exact wrong property** (excess property checks also run).
Step 5 → The resulting type is the *inferred* type of the expression, NOT `SomeType`. Combine with `as const` for fully readonly literals.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Expression (object literal, array आदि) normal लिखो।
Step 2 → उसके बाद `satisfies SomeType` जोड़ो। Compiler check करता है कि expression `SomeType` में assign हो सकता है या नहीं।
Step 3 → Expression को `SomeType` से **contextual typing** मिलती है (इसलिए `"GET"` literal `"GET"` ही रहता है, `[1,2,3]` tuple बन सकता है)।
Step 4 → Fail हो तो error **ठीक उसी गलत property** पर आता है (excess property check भी चलता है)।
Step 5 → Result type expression का *inferred* type होता है, `SomeType` नहीं। पूरी तरह readonly literals के लिए `as const` साथ लगाओ।

---

## 🟡 Real World Example
**Razorpay-style checkout config**: a frontend team keeps a `paymentMethods` object — `upi`, `card`, `netbanking` — each with `label`, `fee` and `enabled`. They want TypeScript to reject a wrong shape (`fee: "2%"`) but still want `paymentMethods.upi.fee` to be a `number` and `keyof typeof paymentMethods` to be exactly `"upi" | "card" | "netbanking"` — so the dropdown and the Redux `selectedMethod` type are derived automatically. An annotation would reduce the keys to `string`; `satisfies` keeps them.

## 🟡 Real Example Hindi mein
**Razorpay जैसा checkout config**: frontend team में `paymentMethods` object है — `upi`, `card`, `netbanking` — हर एक में `label`, `fee`, `enabled`। उन्हें चाहिए कि गलत shape (`fee: "2%"`) reject हो, लेकिन `paymentMethods.upi.fee` फिर भी `number` रहे और `keyof typeof paymentMethods` ठीक `"upi" | "card" | "netbanking"` हो — ताकि dropdown और Redux का `selectedMethod` type अपने-आप बन जाए। Annotation से keys `string` बन जाती; `satisfies` उन्हें बचाकर रखता है।

---

## 💻 Code Example — Basic

```typescript
// Shape every route must follow
type Route = { path: string; auth: boolean }; // contract for one route

// satisfies validates against Record<string, Route> but keeps exact keys
const routes = {
  orders: { path: "/orders", auth: true }, // ok: matches Route
  pay: { path: "/pay", auth: true },       // ok: matches Route
} satisfies Record<string, Route>;          // check only, no widening

// Exact keys survive -> autocomplete shows "orders" | "pay"
type RouteName = keyof typeof routes; // "orders" | "pay" (NOT string)
const name: RouteName = "pay";        // ok

// Value type is still the precise inferred one
console.log(routes.orders.path.toUpperCase()); // string methods work
console.log(name);                              // prints the key
// Output:
// /ORDERS
// pay
```

```typescript
// ❌ Wrong value is rejected AT the definition, pointing at the exact property
type Route = { path: string; auth: boolean };
const routes = {
  orders: { path: "/orders", auth: true },
  pay: { path: "/pay", auth: "yes" }, // wrong: auth must be boolean
} satisfies Record<string, Route>;
// error TS2322: Type 'string' is not assignable to type 'boolean'.
```

## 💻 Code Example — Advanced

```typescript
// Union value type: each colour is a string OR an RGB tuple
type Rgb = [number, number, number]; // tuple type
type Colour = "red" | "green" | "blue"; // allowed keys

// satisfies checks keys (all 3 required) and value union
const palette = {
  red: [255, 0, 0],      // contextually typed as a tuple, not number[]
  green: "#00ff00",      // stays a string
  blue: [0, 0, 255],     // tuple again
} satisfies Record<Colour, string | Rgb>;

// red is a tuple, so .map works and the result is typed
const redHex = palette.red.map((n) => n.toString(16).padStart(2, "0")).join(""); // "ff0000"
// green is a plain string, so string methods work WITHOUT narrowing
const greenUpper = palette.green.toUpperCase(); // "#00FF00"
console.log(redHex, greenUpper);
// Output:
// ff0000 #00FF00
```

```typescript
// as const + satisfies: deeply readonly literals AND contract check
type PaymentMethod = { label: string; fee: number; enabled: boolean };

const paymentMethods = {
  upi: { label: "UPI", fee: 0, enabled: true },
  card: { label: "Credit/Debit Card", fee: 2, enabled: true },
  netbanking: { label: "Net Banking", fee: 1.5, enabled: false },
} as const satisfies Record<string, PaymentMethod>; // TS 5.0+ friendly order

// Derive the union for Redux state / dropdown from the object itself
type MethodId = keyof typeof paymentMethods; // "upi" | "card" | "netbanking"

// fee is the literal type 2 (not number) thanks to as const
const cardFee: 2 = paymentMethods.card.fee; // ok: exact literal preserved

function labelOf(id: MethodId): string {
  return paymentMethods[id].label; // indexing is safe: id is a known key
}
console.log(labelOf("netbanking"), cardFee);
// Output:
// Net Banking 2
```

---

## 🟠 Node/Express + React Integration

```typescript
import type { Request, Response, NextFunction } from "express"; // express types

// A signature every handler must follow
type Handler = (req: Request, res: Response, next: NextFunction) => void;

// Handlers table: validated as Handler, but each key is kept
export const orderHandlers = {
  list: (_req, res) => { res.json([{ id: "o1", total: 499 }]); }, // params typed contextually
  create: (req, res) => { res.status(201).json({ received: req.body }); },
} satisfies Record<string, Handler>;

// Key names are exact, so wiring is checked: orderHandlers.lst would error
export type OrderAction = keyof typeof orderHandlers; // "list" | "create"
```

```tsx
import type { CSSProperties } from "react"; // style type from React

// Styles object: every value must be valid CSS, keys stay exact
const styles = {
  card: { padding: 16, border: "1px solid #ddd" },
  title: { fontWeight: 600, color: "#222" },
} satisfies Record<string, CSSProperties>;

export function OrderCard({ title }: { title: string }) {
  // styles.card / styles.title autocomplete; styles.body would be a compile error
  return (
    <div style={styles.card}>
      <h3 style={styles.title}>{title}</h3>
    </div>
  );
}
```

```typescript
// Redux Toolkit: initial state validated against the state interface
interface CartState { items: string[]; status: "idle" | "loading" } // state contract

const initialState = {
  items: [],            // contextually typed as string[]
  status: "idle",       // stays the literal "idle", not widened string
} satisfies CartState;  // typo like status: "idel" would be an error here

export type InitialStatus = typeof initialState.status; // "idle"
```

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: Using an annotation and then expecting exact keys.**

```typescript
// ❌ Annotation widens: any key is "valid", typo silently compiles
type Route = { path: string; auth: boolean };
const routes: Record<string, Route> = {
  orders: { path: "/orders", auth: true },
};
routes.ordres.path; // compiles! runtime: TypeError (undefined.path)
// (no compile error at all - that is the bug)
```

```typescript
// ✅ satisfies keeps keys exact, so the typo is caught
type Route = { path: string; auth: boolean };
const routes = {
  orders: { path: "/orders", auth: true },
} satisfies Record<string, Route>;
console.log(routes.orders.path); // ok
// routes.ordres -> error TS2551: Property 'ordres' does not exist on type
// '{ orders: { path: string; auth: true; }; }'. Did you mean 'orders'?
// Output:
// /orders
```

**Mistake 2: Thinking `satisfies` is a cast.** It never changes the type and never silences errors — it only adds a check. Use `as` only when you know better than the compiler; use `satisfies` when you want the compiler to verify.

---

## 🧠 Tricky Interview Question

**Q:** What is the type of `x.status` below, and what does `y.status` give?

```typescript
type S = { status: "ok" | "fail" };
const x = { status: "ok" } satisfies S; // satisfies
const y: S = { status: "ok" };          // annotation
const a: "ok" = x.status; // compiles?
console.log(x.status, y.status);
// Output:
// ok ok
```

**Answer:** `x.status` is the literal type `"ok"` (satisfies contextual typing keeps the literal, and the variable keeps its inferred type), so `const a: "ok" = x.status` compiles. `y.status` is the wider union `"ok" | "fail"` because the annotation replaced the inferred type — assigning `y.status` to `"ok"` would fail. Runtime output is identical: types are erased. Note: for a `let`/mutable property of a non-contextual string, TypeScript would widen to `string`; it is the contextual type from `satisfies` that preserves the literal.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between `: T` and `satisfies T`?**
A1: `: T` sets the variable's type to `T` (widening, losing exact keys/literals). `satisfies T` only validates the value against `T` and keeps the inferred type. Use annotation for a public contract, `satisfies` for config/lookup tables where you want both validation and precision.

**Q2: Which TS version added `satisfies`, and how does it relate to `as const`?**
A2: TS 4.9. `as const` makes literals deeply readonly; `satisfies` validates shape. They combine: `{...} as const satisfies Record<string, X>`. Before TS 5.0 the `as const satisfies` form needed the readonly-friendly target type (e.g. `readonly string[]`) to avoid "readonly not assignable to mutable" errors.

**Q3: Does `satisfies` do excess property checking?**
A3: Yes. An object literal with an unknown key against a closed type errors at that key, just like a normal assignment. For `Record<string, X>` any key is allowed, so use a union of keys (`Record<"a"|"b", X>`) to force exact key sets.

**Q4: Can `satisfies` replace type assertions (`as`)?**
A4: No. `as` overrides the compiler (can lie); `satisfies` verifies and never changes the type. If the expression does not match, `satisfies` errors while `as` may allow a wrong cast. Prefer `satisfies` whenever you can.

**Q5: Give a real use in a React/Redux app.**
A5: Route tables, theme/token objects (`satisfies Record<string, CSSProperties>`), RTK `initialState` (`satisfies State`), feature-flag maps and Express handler maps. All need validation at definition plus exact keys for `keyof typeof` derivations.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Config/lookup objects where you need both validation and exact keys/literals
- You derive types from values (`keyof typeof obj`, `typeof obj.field`)
- You want a union-typed field to keep its specific member (tuple vs string)

❌ Avoid when:
- You want the variable to be treated as the wider type on purpose (public API return type) — use an annotation
- Function/class members — `satisfies` is for expressions, not declarations
- You are targeting TS < 4.9 (use a generic identity helper `const defineRoutes = <T extends Record<string, Route>>(r: T) => r`)

---

## 📊 Visual Diagram
```
  const x: T = value              value satisfies T
  ─────────────────               ──────────────────
  check value against T           check value against T
         │                               │
         ▼                               ▼
  type of x  = T  (WIDE)          type of x = typeof value (NARROW)
  keys: string                    keys: "orders" | "pay"
  values: Route                   values: { path: string; auth: true }
  typo x.ordres -> OK (bug!)      typo x.ordres -> ERROR (caught)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| satisfies | Validate without changing type (TS 4.9) | बिना type बदले validate करना |
| Widening | Annotation replaces precise type with wider one | Precise type का चौड़ा हो जाना |
| Contextual typing | Expected type guides inference of literals/tuples | Expected type से inference |
| as const | Deeply readonly literal types | Readonly literal types |
| Excess property check | Unknown keys in literal are errors | Extra keys पर error |
| keyof typeof | Union of an object's keys from a value | Value से keys का union |

---

## ⚡ 3-Line Summary
English:
1. `satisfies` validates an expression against a type while keeping its narrow inferred type (TS 4.9+).
2. Annotations widen (typos compile); `satisfies` keeps exact keys, literals and tuples.
3. Combine with `as const` for readonly config tables and derive unions via `keyof typeof`.

Hindi:
1. `satisfies` expression को type के against check करता है और उसका narrow inferred type बनाए रखता है (TS 4.9+)।
2. Annotation type चौड़ा कर देता है (typo compile हो जाती है); `satisfies` exact keys, literals और tuples बचाता है।
3. Readonly config tables के लिए `as const` के साथ लगाओ और `keyof typeof` से unions निकालो।

---

## ➡️ Next Topic
**35. Declaration Merging** — how multiple `interface`, `namespace` and `class` declarations with the same name combine into one type (the basis for extending Express `Request`).
