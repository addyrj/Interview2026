# 108. Branded IDs (UserId vs OrderId)
# हिंदी में: Branded IDs (UserId बनाम OrderId)

> Verified with **TypeScript 5.9.3** (`--strict`) and **Zod 4.6** (`.brand()`). Branding works on every TS 2.x+ version; `unique symbol` brand keys are TS 2.7+.

---

## 🔵 Simple Definition (English)
TypeScript is **structurally typed**: `type UserId = string` and `type OrderId = string` are the **same type**, so `getOrder(userId)` compiles. A **branded (nominal) type** adds a fake, compile-time-only tag: `type UserId = string & { readonly __brand: "UserId" }`. Now `UserId` and `OrderId` are **different, non-interchangeable types**, yet at runtime they are still plain strings (zero cost). You create branded values only through a **smart constructor** that validates once (or a single controlled cast), and everything downstream is safe.

## 🔵 सरल परिभाषा (Hindi)
TypeScript **structurally typed** है: `type UserId = string` और `type OrderId = string` **एक ही type** हैं, इसलिए `getOrder(userId)` compile हो जाता है। **Branded (nominal) type** एक नकली, सिर्फ compile-time वाला tag जोड़ता है: `type UserId = string & { readonly __brand: "UserId" }`। अब `UserId` और `OrderId` **अलग, आपस में न बदले जा सकने वाले types** हैं, जबकि runtime पर ये अब भी plain strings हैं (zero cost)। Branded values सिर्फ **smart constructor** से बनते हैं जो एक बार validate करता है (या एक controlled cast), और उसके बाद सब कुछ सुरक्षित रहता है।

---

## 🔴 Problem it Solves
With `string`/`number` IDs everywhere, a function `refund(orderId: string, userId: string)` can be called as `refund(userId, orderId)` and **nothing complains**. The bug ships, the refund hits the wrong record, and SQL Server returns zero rows instead of an error. Same for `number` primary keys (`UserId` 5 vs `OrderId` 5) and for **units** (`Rupees` vs `Paise`). Branding costs one line per type and kills this whole class of bug at compile time.

## 🔴 यह क्यों बना? (Hindi)
हर जगह `string`/`number` IDs होने पर `refund(orderId: string, userId: string)` को `refund(userId, orderId)` की तरह call किया जा सकता है और **कोई शिकायत नहीं करता**। Bug ship होता है, refund गलत record पर लगता है, और SQL Server error की जगह zero rows लौटाता है। यही `number` primary keys (`UserId` 5 बनाम `OrderId` 5) और **units** (`Rupees` बनाम `Paise`) के साथ होता है। Branding हर type के लिए एक line में यह पूरी class के bugs compile time पर ख़त्म कर देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Define a reusable helper: `type Brand<T, B extends string> = T & { readonly __brand: B }`.
Step 2 → Declare ID types: `type UserId = Brand<string, "UserId">`, `type OrderId = Brand<string, "OrderId">`.
Step 3 → Intersection `string & { __brand: "UserId" }` is **assignable to `string`** (you can still `.toUpperCase()`), but a plain `string` or an `OrderId` is **not** assignable to `UserId`.
Step 4 → Create values via **smart constructors**: `const toUserId = (s: string): UserId => { validate; return s as UserId; }`. The `as` cast lives in exactly **one** place.
Step 5 → Use the branded types in function signatures, DB row types, DTOs and Maps. Parse at the **boundary** (HTTP params, DB rows, `JSON.parse`) and trust inside.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Reusable helper define करो: `type Brand<T, B extends string> = T & { readonly __brand: B }`।
Step 2 → ID types declare करो: `type UserId = Brand<string, "UserId">`, `type OrderId = Brand<string, "OrderId">`।
Step 3 → Intersection `string & { __brand: "UserId" }` **`string` में assignable है** (आप अब भी `.toUpperCase()` कर सकते हो), पर plain `string` या `OrderId` `UserId` में assignable **नहीं** है।
Step 4 → Values **smart constructors** से बनाओ: `const toUserId = (s: string): UserId => { validate; return s as UserId; }`। `as` cast सिर्फ **एक** जगह रहता है।
Step 5 → Branded types को function signatures, DB row types, DTOs और Maps में इस्तेमाल करो। **Boundary** (HTTP params, DB rows, `JSON.parse`) पर parse करो और अंदर भरोसा रखो।

---

## 🟡 Real World Example
**Swiggy's refund service** has `refund(orderId, userId, amount)`. Before branding, one engineer swapped two string arguments in a retry job; 3,000 refunds failed silently because no order matched the user id. After branding (`OrderId`, `UserId`, and `Paise` for amounts) the swapped call is a red squiggle in the editor. The same trick prevents adding `Rupees` and `Paise` together.

## 🟡 Real Example Hindi mein
**Swiggy की refund service** में `refund(orderId, userId, amount)` है। Branding से पहले एक engineer ने retry job में दो string arguments की जगह बदल दी; 3,000 refunds चुपचाप fail हुए क्योंकि कोई order user id से match नहीं हुआ। Branding (`OrderId`, `UserId`, और amount के लिए `Paise`) के बाद वही swapped call editor में लाल लकीर है। यही trick `Rupees` और `Paise` को जोड़ने से भी रोकती है।

---

## 💻 Code Example — Basic

```typescript
// branded-basic.ts — Brand helper, smart constructors, safe functions
type Brand<T, B extends string> = T & { readonly __brand: B }; // compile-time tag only, no runtime cost

type UserId = Brand<string, "UserId">; // string that is known to be a user id
type OrderId = Brand<string, "OrderId">; // string that is known to be an order id

function toUserId(raw: string): UserId { // smart constructor = the ONLY place we cast
  if (!/^usr_[a-z0-9]+$/.test(raw)) throw new Error(`Invalid UserId: ${raw}`); // validate format once
  return raw as UserId; // cast after validation
}
function toOrderId(raw: string): OrderId { // same for orders
  if (!/^ord_[a-z0-9]+$/.test(raw)) throw new Error(`Invalid OrderId: ${raw}`); // validate
  return raw as OrderId; // cast after validation
}

function refund(orderId: OrderId, userId: UserId): string { // arguments can no longer be swapped
  return `refund ${orderId} for ${userId}`; // still plain strings at runtime
}

const u = toUserId("usr_42"); // u: UserId
const o = toOrderId("ord_7"); // o: OrderId
console.log(refund(o, u)); // prints refund ord_7 for usr_42
console.log(u.toUpperCase()); // prints USR_42 (a UserId IS a string, so string methods work)
console.log(JSON.stringify({ u, o })); // prints {"u":"usr_42","o":"ord_7"} (zero runtime footprint)
```

```typescript
// branded-errors.ts — what the compiler now prevents
type Brand<T, B extends string> = T & { readonly __brand: B }; // helper
type UserId = Brand<string, "UserId">; // user id
type OrderId = Brand<string, "OrderId">; // order id
declare const u: UserId; // some user id
declare const o: OrderId; // some order id
declare function getOrder(id: OrderId): void; // expects an order id

// ❌ 1. wrong brand
getOrder(u);
// error TS2345: Argument of type 'UserId' is not assignable to parameter of type 'OrderId'.
//   Type 'UserId' is not assignable to type '{ readonly __brand: "OrderId"; }'.
//     Types of property '__brand' are incompatible.
//       Type '"UserId"' is not assignable to type '"OrderId"'.

// ❌ 2. raw string literal
getOrder("ord_7");
// error TS2345: Argument of type 'string' is not assignable to parameter of type 'OrderId'.
//   Type 'string' is not assignable to type '{ readonly __brand: "OrderId"; }'.
```

## 💻 Code Example — Advanced

```typescript
// branded-advanced.ts — unique-symbol brand, numeric ids, units, Zod .brand(), and a Map keyed by brand
import { z } from "zod"; // runtime validation that can emit branded types

declare const brand: unique symbol; // a symbol that exists only in the type system
type Brand<T, B extends string> = T & { readonly [brand]: B }; // symbol key: can't be forged by JSON/objects with "__brand"

type OrderId = Brand<number, "OrderId">; // SQL Server INT IDENTITY primary key
type Rupees = Brand<number, "Rupees">; // money in rupees
type Paise = Brand<number, "Paise">; // money in paise

const rupees = (n: number): Rupees => n as Rupees; // controlled cast
const toPaise = (r: Rupees): Paise => Math.round(r * 100) as Paise; // explicit, named conversion
const addPaise = (a: Paise, b: Paise): Paise => (a + b) as Paise; // arithmetic result must be re-branded

const bill = addPaise(toPaise(rupees(199.5)), toPaise(rupees(0.5))); // 19950 + 50
console.log(bill); // prints 20000

// ❌ mixing units is now a compile error
addPaise(bill, rupees(5));
// error TS2345: Argument of type 'Rupees' is not assignable to parameter of type 'Paise'.
//   Type 'Rupees' is not assignable to type '{ readonly [brand]: "Paise"; }'.
//     Types of property '[brand]' are incompatible.
//       Type '"Rupees"' is not assignable to type '"Paise"'.

// Zod brands at the boundary: parse = validate + brand in one step
const OrderIdSchema = z.number().int().positive().brand<"OrderId">(); // zod emits z.BRAND<"OrderId">
type ZOrderId = z.infer<typeof OrderIdSchema>; // number & z.$brand<"OrderId">
const parsed: ZOrderId = OrderIdSchema.parse(42); // throws on 0, -1, 1.5, "x"
console.log(parsed + 1); // prints 43 (still a number)

// Maps and lookups key by the brand, so you cannot look up an order with a user id
const names = new Map<OrderId, string>(); // typed keys
const oid = 7 as OrderId; // for the demo
names.set(oid, "Biryani combo"); // set
console.log(names.get(oid)); // prints Biryani combo
```

---

## 🟠 Node/Express + React Integration

```typescript
// express-ids.ts — parse once at the HTTP boundary, trust the brand afterwards
import express from "express"; // express + types

type Brand<T, B extends string> = T & { readonly __brand: B }; // helper
type OrderId = Brand<number, "OrderId">; // numeric id

function parseOrderId(raw: string): OrderId | null { // returns null on bad input, no exceptions
  const n = Number(raw); // convert
  return Number.isInteger(n) && n > 0 ? (n as OrderId) : null; // validate then brand
}

async function loadOrder(id: OrderId): Promise<{ id: OrderId; total: number }> { // service layer demands the brand
  return { id, total: 499 }; // in real life: SELECT ... WHERE OrderId = @id (mssql parameter)
}

const app = express(); // app
app.get("/orders/:id", async (req, res) => {
  const id = parseOrderId(req.params.id); // string -> OrderId | null
  if (id === null) { res.status(400).json({ error: "bad order id" }); return; } // reject early
  res.json(await loadOrder(id)); // id is OrderId from here on
});
```

```tsx
// OrderLink.tsx — React props and Redux selectors stay unmixable too
import type { ReactNode } from "react"; // types

type Brand<T, B extends string> = T & { readonly __brand: B }; // helper
type OrderId = Brand<string, "OrderId">; // id types
type UserId = Brand<string, "UserId">;

interface Props { orderId: OrderId; children: ReactNode } // component API demands OrderId

export function OrderLink({ orderId, children }: Props) { // component
  return <a href={`/orders/${orderId}`}>{children}</a>; // template literal accepts it (it is a string)
}

declare const uid: UserId; // e.g. from state.auth.userId
// ❌ a user id passed where an order id is required
export const bad = <OrderLink orderId={uid}>x</OrderLink>;
// error TS2322: Type 'UserId' is not assignable to type 'OrderId'.
//   Type 'UserId' is not assignable to type '{ readonly __brand: "OrderId"; }'.
//     Types of property '__brand' are incompatible.
//       Type '"UserId"' is not assignable to type '"OrderId"'.
export const ok = <OrderLink orderId={"ord_1" as OrderId}>Open</OrderLink>; // brand must be established explicitly
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Casting everywhere with `as UserId`
```typescript
// wrong-cast.ts
type UserId = string & { readonly __brand: "UserId" }; // brand
const a = "anything" as UserId; // wrong: this defeats the whole purpose, no validation
function toUserId(s: string): UserId { // right: ONE validating constructor
  if (s.length === 0) throw new Error("empty id"); // validate
  return s as UserId; // the single allowed cast
}
console.log(a, toUserId("usr_1")); // prints anything usr_1
```
✅ Correct: grep your code base for `as UserId`; it should appear **once**.

❌ Mistake 2: Making the brand property optional
```typescript
// weak-brand.ts
type WeakUser = string & { __brand?: "UserId" }; // wrong: optional brand
const w: WeakUser = "anything"; // compiles! a raw string satisfies it, so the brand protects nothing
type StrongUser = string & { readonly __brand: "UserId" }; // right: required brand
console.log(w); // prints anything
// const s: StrongUser = "anything"; would fail with TS2322: Type 'string' is not assignable to type 'StrongUser'.
```
(Two *different* optional brands still reject each other, but a plain `string` slips in, which is the main bug you wanted to stop.)
✅ Correct: make the brand **required** (`{ readonly __brand: "UserId" }`), or use a `unique symbol` key.

❌ Mistake 3: Expecting the brand to exist at runtime (`value.__brand`, `JSON.parse` revival)
✅ Correct: brands vanish at compile time. After `JSON.parse` or a DB read you get plain strings again, so re-brand through the smart constructor (or a Zod schema) at that boundary.

---

## 🧠 Tricky Interview Question

```typescript
// tricky.ts — which lines compile?
type Brand<T, B extends string> = T & { readonly __brand: B }; // helper
type UserId = Brand<string, "UserId">; // user id
declare const u: UserId; // a branded value

const s: string = u; // (1)
const l = u.length; // (3)
// ❌ (2) concatenation returns plain string
const t: UserId = u + "x";
// error TS2322: Type 'string' is not assignable to type 'UserId'.
//   Type 'string' is not assignable to type '{ readonly __brand: "UserId"; }'.
console.log(s, l); // never run, compile-only
```
**Answer:** (1) **compiles**: `UserId` is a subtype of `string`. (3) **compiles**: it is still a string, so `.length` exists. (2) **fails**: `u + "x"` has type plain `string` (string concatenation returns `string`, the brand is lost), so assigning it to `UserId` gives `TS2322: Type 'string' is not assignable to type 'UserId'`. Branding is therefore **one-directional**: you can always widen to the base type, but any operation that produces a new value (concat, `slice`, arithmetic) loses the brand, which is exactly the behaviour you want for IDs.

---

## ⚫ Interview Questions + Answers

Q1: Why does TypeScript need branding at all?
A1: Typing is **structural**, so two aliases of `string` are identical. Branding adds a distinguishing (phantom) property so the structures differ. Classes with `private` members are nominal by accident; branding gives that for any primitive.

Q2: Is there any runtime cost?
A2: None. The brand exists only in the type system, erased on compile. The value is the raw string or number.

Q3: `__brand` property vs `unique symbol` key: which is better?
A3: A `unique symbol` key cannot be accidentally satisfied by an object literal containing `__brand: "UserId"` and does not show up in autocomplete as a normal property. The string-key version is simpler to read in error messages. Both are fine; be consistent.

Q4: How do you make branded types work with validation libraries?
A4: Zod: `z.string().uuid().brand<"UserId">()`. `parse` validates and returns the branded type. Valibot has `v.brand("UserId")`. This ties **validation to the type** so you cannot get a branded value without passing the check.

Q5: Where would you NOT brand?
A5: Local variables and short-lived strings where mix-ups are impossible. Brand IDs that cross function/module boundaries, amounts with units, and values that were validated/sanitised (`SafeHtml`, `NormalizedEmail`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many IDs of the same primitive type flow through the same functions (SQL Server keys)
- Units or states of a value matter (`Rupees` vs `Paise`, `Validated<T>`, `SafeHtml`)

❌ Avoid when:
- A small script/prototype where the ceremony outweighs the risk
- Data is mostly consumed as plain JSON (you will re-brand constantly; branding only at service boundaries is enough)

---

## 📊 Visual Diagram
```
 plain TS:   UserId = string      OrderId = string      -> SAME type, swap compiles
 branded:    UserId  = string & { __brand: "UserId"  }
             OrderId = string & { __brand: "OrderId" }  -> DIFFERENT types

        HTTP "ord_7" (string)
              │  toOrderId()  validate + one cast
              ▼
          OrderId  ──► getOrder(id: OrderId)   ok
          UserId   ──► getOrder(id: OrderId)   TS2345
          string   ──► getOrder(id: OrderId)   TS2345
          OrderId  ──► (s: string) => ...      ok (widening is allowed)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Structural typing | Types compare by shape | Types shape से compare होते हैं |
| Nominal typing | Types compare by name | Types नाम से compare होते हैं |
| Brand / phantom tag | Type-only marker property | सिर्फ type में रहने वाला marker |
| Smart constructor | Validating function that creates the value | Validate करके value बनाने वाला function |
| `unique symbol` | Type-level unique key | Type-level unique key |
| Boundary parsing | Validate where untrusted data enters | जहाँ untrusted data आता है वहाँ validate |

---

## ⚡ 3-Line Summary
English:
1. `type UserId = string & { readonly __brand: "UserId" }` makes IDs of the same primitive non-interchangeable at zero runtime cost.
2. Create branded values only through a validating smart constructor (or Zod `.brand()`), keep the `as` cast in one place.
3. Brands widen to the base type but any new computed value loses the brand, re-brand deliberately.

Hindi:
1. `type UserId = string & { readonly __brand: "UserId" }` एक ही primitive के IDs को बिना runtime cost के आपस में बदलने से रोकता है।
2. Branded values सिर्फ validate करने वाले smart constructor (या Zod `.brand()`) से बनाओ, `as` cast एक ही जगह रखो।
3. Brand base type में widen हो जाता है पर नई computed value से brand चला जाता है, जानबूझकर दोबारा brand करो।

---

## ➡️ Next Topic
**109. Typed curry / compose / pipe** — functional utilities whose types track every argument and return value.
