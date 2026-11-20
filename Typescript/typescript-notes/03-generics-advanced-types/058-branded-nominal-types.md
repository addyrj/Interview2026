# 58. Branded / Nominal Types
# हिंदी में: Branded / Nominal Types (एक जैसे दिखने वाले types को अलग करना)

> TypeScript 5.x (`tsc --strict`, TS 5.9) पर verify किया गया। Branding एक **pattern** है (कोई keyword नहीं)। `unique symbol` brand TS 2.7+; `satisfies` (TS 4.9) कुछ examples में काम आता है।

---

## 🔵 Simple Definition (English)
TypeScript is **structurally typed**: two types with the same shape are interchangeable, so `UserId` and `OrderId` (both `string`) can be swapped by mistake. A **branded (nominal) type** adds a phantom tag: `type UserId = string & { readonly __brand: "UserId" }`. At runtime it is still a plain string, but at compile time `UserId` is **not** assignable to `OrderId`. You create branded values in one controlled place (a constructor/validator function).

## 🔵 सरल परिभाषा (Hindi)
TypeScript **structurally typed** है: जिन दो types की shape एक जैसी है वे आपस में बदले जा सकते हैं, इसलिए `UserId` और `OrderId` (दोनों `string`) गलती से अदल-बदल हो सकते हैं। **Branded (nominal) type** एक phantom tag जोड़ता है: `type UserId = string & { readonly __brand: "UserId" }`। Runtime पर यह साधारण string ही रहता है, पर compile time पर `UserId`, `OrderId` को assignable **नहीं** है। Branded values एक ही नियंत्रित जगह (constructor/validator function) में बनाए जाते हैं।

---

## 🔴 Problem it Solves
`refund(paymentId: string, orderId: string)` - the compiler happily accepts `refund(orderId, paymentId)`. This is a **real production bug class**: money refunded against the wrong record, SQL queries run with a customer id where an order id was expected. Same for units: `amountInPaise` vs `amountInRupees` (both `number`) - a 100x pricing bug. Also "validated vs raw" data: an `Email` that passed validation must not be confusable with any random string. Runtime classes would fix it but cost allocation and complicate JSON; brands cost **zero runtime**.

## 🔴 यह क्यों बना? (Hindi)
`refund(paymentId: string, orderId: string)` - compiler `refund(orderId, paymentId)` भी खुशी से मान लेता है। यह **production की असली bug class** है: गलत record पर पैसा refund, या order id की जगह customer id से SQL query। Units में भी यही: `amountInPaise` बनाम `amountInRupees` (दोनों `number`) - 100 गुना price bug। "Validated बनाम raw" data में भी: validation पास कर चुका `Email` किसी भी random string से confuse नहीं होना चाहिए। Runtime classes इसे ठीक करतीं पर allocation लगती और JSON मुश्किल होता; brands का **runtime cost zero** है।

---

## 🟢 How it Works — Step by Step

Step 1 → Structural typing: `string` is assignable to `string`, regardless of meaning. Nothing distinguishes two `string` aliases.
Step 2 → Add a **phantom property** via intersection: `string & { __brand: "UserId" }`. The property never exists at runtime; it exists only in the type.
Step 3 → Different brand literals make types **mutually incompatible**: `{ __brand: "UserId" }` vs `{ __brand: "OrderId" }`.
Step 4 → A generic helper `type Brand<T, B extends string> = T & { readonly __brand: B }` keeps it DRY.
Step 5 → Plain values cannot become branded implicitly. You must go through a **smart constructor** (validate then cast with `as`) - the only place where the cast is allowed.
Step 6 → A branded type is still assignable **to** its base (`UserId` -> `string`), so you can log it, use `.length`, send it as JSON.
Step 7 → For stronger hiding, use a `declare const brand: unique symbol` key instead of a string key, so nobody can fake the brand by writing `{ __brand: "UserId" }` literally.
Step 8 → Brands vanish at runtime; if data comes from outside (HTTP, DB), validate it (Zod `.brand()`) before trusting it.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Structural typing: `string`, `string` को assignable है, मतलब चाहे जो हो। दो `string` aliases में कुछ अलग नहीं करता।
Step 2 → Intersection से **phantom property** जोड़ो: `string & { __brand: "UserId" }`। यह property runtime पर कभी नहीं होती; सिर्फ type में है।
Step 3 → अलग brand literals types को **आपस में incompatible** बना देते हैं: `{ __brand: "UserId" }` बनाम `{ __brand: "OrderId" }`।
Step 4 → Generic helper `type Brand<T, B extends string> = T & { readonly __brand: B }` से code DRY रहता है।
Step 5 → Plain value अपने आप branded नहीं बन सकती। **Smart constructor** से गुज़ारना पड़ता है (validate करो फिर `as` cast) - cast की इजाज़त सिर्फ यहीं।
Step 6 → Branded type अपने base को अब भी assignable है (`UserId` -> `string`), इसलिए log, `.length`, JSON सब चलता है।
Step 7 → ज़्यादा सुरक्षा के लिए string key की जगह `declare const brand: unique symbol` इस्तेमाल करो, ताकि कोई `{ __brand: "UserId" }` literal लिखकर brand नकली न बना सके।
Step 8 → Brands runtime पर गायब हैं; बाहर से आया data (HTTP, DB) भरोसे से पहले validate करो (Zod `.brand()`)।

---

## 🟡 Real World Example
**Razorpay's** refund API has `payment_id` (`pay_...`), `order_id` (`order_...`) and `refund_id`. All strings, all easy to swap. Their SDK typings can use `PaymentId`, `OrderId`, `RefundId` brands so `refund(orderId, ...)` fails at compile time. **Swiggy's** pricing code keeps `Paise` and `Rupees` as separate brands: adding them raw is an error, you must go through `toRupees(paise)`. A **Paytm** KYC service has `Validated<PanNumber>`: only the validator can produce it, so the rest of the system never re-checks.

## 🟡 Real Example Hindi mein
**Razorpay** के refund API में `payment_id` (`pay_...`), `order_id` (`order_...`) और `refund_id` हैं। सब strings, आसानी से swap हो जाते हैं। उनके SDK typings में `PaymentId`, `OrderId`, `RefundId` brands हो सकते हैं ताकि `refund(orderId, ...)` compile time पर ही fail हो। **Swiggy** का pricing code `Paise` और `Rupees` को अलग brands रखता है: raw जोड़ना error है, `toRupees(paise)` से गुज़रना पड़ता है। **Paytm** की KYC service में `Validated<PanNumber>` है: सिर्फ validator इसे बना सकता है, इसलिए बाकी system दोबारा check नहीं करता।

---

## 💻 Code Example — Basic

```typescript
// Generic brand helper: base type + phantom tag (exists only at compile time)
type Brand<T, B extends string> = T & { readonly __brand: B };

// Three different string-like ids
type UserId = Brand<string, "UserId">; // user identifier
type OrderId = Brand<string, "OrderId">; // order identifier

// Smart constructors: the ONLY place where the cast is allowed
function toUserId(raw: string): UserId {
  if (!raw.startsWith("usr_")) throw new Error(`bad user id: ${raw}`); // validate first
  return raw as UserId; // brand it after validation
}
function toOrderId(raw: string): OrderId {
  if (!raw.startsWith("ord_")) throw new Error(`bad order id: ${raw}`); // validate first
  return raw as OrderId; // brand it after validation
}

// A function that demands the right kind of id
function getOrder(userId: UserId, orderId: OrderId): string {
  return `user=${userId} order=${orderId}`; // brands behave like strings at runtime
}

const u = toUserId("usr_7"); // UserId
const o = toOrderId("ord_99"); // OrderId
console.log(getOrder(u, o)); // user=usr_7 order=ord_99
console.log(u.toUpperCase()); // USR_7  (still a string, methods work)

// ❌ Swapped arguments are now a compile error
getOrder(o, u);
// error TS2345: Argument of type 'OrderId' is not assignable to parameter of type 'UserId'.
//   Type 'OrderId' is not assignable to type '{ readonly __brand: "UserId"; }'.
//     Types of property '__brand' are incompatible.
//       Type '"OrderId"' is not assignable to type '"UserId"'.

// ❌ A raw string is not accepted either
getOrder("usr_7", "ord_99");
// error TS2345: Argument of type 'string' is not assignable to parameter of type 'UserId'.
//   Type 'string' is not assignable to type '{ readonly __brand: "UserId"; }'.
```

## 💻 Code Example — Advanced

```typescript
// 1) Unique-symbol brand: cannot be forged with an object literal
declare const brand: unique symbol; // type-only symbol (no runtime value emitted)
type Opaque<T, Tag extends string> = T & { readonly [brand]: Tag }; // key is the symbol

type Paise = Opaque<number, "Paise">; // money in paise (integer)
type Rupees = Opaque<number, "Rupees">; // money in rupees

const paise = (n: number): Paise => { // constructor with validation
  if (!Number.isInteger(n) || n < 0) throw new RangeError("paise must be a non-negative integer"); // guard
  return n as Paise; // brand
};
const toRupees = (p: Paise): Rupees => (p / 100) as Rupees; // the ONLY conversion path
const toPaise = (r: Rupees): Paise => Math.round(r * 100) as Paise; // reverse conversion

const price = paise(49900); // Paise
console.log(toRupees(price)); // 499
console.log(toPaise(toRupees(price))); // 49900

// ❌ Cannot add different units, or pass one where the other is expected
const total: Rupees = price;
// error TS2322: Type 'Paise' is not assignable to type 'Rupees'.
//   Type 'Paise' is not assignable to type '{ readonly [brand]: "Rupees"; }'.
//     Types of property '[brand]' are incompatible.
//       Type '"Paise"' is not assignable to type '"Rupees"'.

// 2) Validated data: Email that passed a check
type Email = Opaque<string, "Email">; // validated email
function parseEmail(s: string): Email | null {
  return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(s) ? (s as Email) : null; // null when invalid
}
function sendReceipt(to: Email): void { console.log(`mail -> ${to}`); } // only accepts validated mail
const e = parseEmail("riya@example.com"); // Email | null
if (e) sendReceipt(e); // mail -> riya@example.com  (narrowed to Email)

// 3) Branded id factory with a Result-like return
type Id<Tag extends string> = Opaque<string, Tag>; // reusable id brand
const makeId = <Tag extends string>(prefix: string) => (raw: string): Id<Tag> => {
  if (!raw.startsWith(prefix)) throw new Error(`expected ${prefix}*, got ${raw}`); // prefix check
  return raw as Id<Tag>; // brand
};
const PaymentId = makeId<"PaymentId">("pay_"); // factory for payment ids
const RefundId = makeId<"RefundId">("rfnd_"); // factory for refund ids
type PaymentId = ReturnType<typeof PaymentId>; // type with same name as the value (common idiom)
type RefundId = ReturnType<typeof RefundId>; // same idiom
function refund(p: PaymentId, r: RefundId): string { return `${p}/${r}`; } // typed refund call
console.log(refund(PaymentId("pay_1"), RefundId("rfnd_1"))); // pay_1/rfnd_1
```

---

## 🟠 Node/Express + React Integration

```typescript
import express from "express";
import { z } from "zod";

// Zod can brand at the validation boundary: parse -> branded type, in one step
const OrderIdSchema = z.string().regex(/^ord_\d+$/).brand<"OrderId">(); // brand on success
type OrderId = z.infer<typeof OrderIdSchema>; // string & z.BRAND<"OrderId">

// Repository only accepts validated ids (cannot be called with a raw req.params value)
async function loadOrder(id: OrderId): Promise<{ id: OrderId; amount: number }> {
  return { id, amount: 499 }; // would be a SQL Server query: WHERE id = @id
}

const app = express(); // create app
app.get("/orders/:id", async (req, res) => {
  const parsed = OrderIdSchema.safeParse(req.params.id); // validate + brand
  if (!parsed.success) { // invalid -> 400
    res.status(400).json({ error: "invalid order id" }); // reject
    return; // stop
  }
  res.json(await loadOrder(parsed.data)); // parsed.data is OrderId, safe to pass on
});
```

```tsx
import { useState, type ReactElement } from "react";

type Brand<T, B extends string> = T & { readonly __brand: B }; // helper
type Paise = Brand<number, "Paise">; // money type
const formatRupees = (p: Paise): string => `₹${(p / 100).toFixed(2)}`; // only accepts Paise

export function Price({ amount }: { amount: Paise }): ReactElement {
  return <b>{formatRupees(amount)}</b>; // component props enforce the unit
}

export function Demo(): ReactElement {
  const [paise] = useState<Paise>(49900 as Paise); // brand once at the data boundary
  return <Price amount={paise} />; // <Price amount={499} /> would be a compile error
}
```

```typescript
// Redux Toolkit: branded ids stop wrong-id dispatches
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
type Brand<T, B extends string> = T & { readonly __brand: B }; // helper
type CartId = Brand<string, "CartId">; // cart identifier
type ProductId = Brand<string, "ProductId">; // product identifier

const cart = createSlice({
  name: "cart",
  initialState: { id: "c1" as CartId, items: [] as ProductId[] }, // typed state
  reducers: {
    addItem(state, a: PayloadAction<ProductId>) { state.items.push(a.payload); }, // only ProductId accepted
  },
});
console.log(cart.reducer(undefined, cart.actions.addItem("p1" as ProductId)).items); // [ 'p1' ]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Casting with `as` all over the codebase
```typescript
type UserId = string & { readonly __brand: "UserId" }; // brand

// Wrong: casts everywhere defeat the purpose (any string becomes a UserId)
const a = "whatever" as UserId; // no validation!
const b = req_body_value() as UserId; // no validation!
declare function req_body_value(): string; // helper

// Right: one smart constructor, ESLint rule to forbid `as UserId` elsewhere
const toUserId = (s: string): UserId => {
  if (!/^usr_\d+$/.test(s)) throw new Error("bad id"); // validate
  return s as UserId; // only cast allowed
};
```

❌ Mistake 2: Using a plain string key brand that anyone can forge
```typescript
type Id = string & { __brand: "Id" }; // string-key brand
const forged: Id = Object.assign("x", { __brand: "Id" as const }); // compiles - brand forged anyone can do this
console.log(typeof forged); // object  (Object.assign boxed it into a String object - the forge even changes runtime behaviour)
```
✅ Correct: prefer the `unique symbol` brand (`declare const brand: unique symbol`) so the key cannot be written in an object literal, and keep the constructor as the only producer.

❌ Mistake 3: Forgetting brands are erased - trusting untrusted JSON
```typescript
type Email = string & { readonly __brand: "Email" }; // brand
// Wrong: JSON.parse returns any - this "brands" unvalidated data
const body = JSON.parse('{"email":"nope"}') as { email: Email }; // compiles, but "nope" is not an email
console.log(body.email); // nope
```
✅ Correct: validate at the boundary (Zod `.brand()`, or a `parseEmail` that returns `Email | null`).

❌ Mistake 4: Expecting arithmetic to keep the brand
```typescript
type Paise = number & { readonly __brand: "Paise" }; // brand
declare const a: Paise; // brand value
declare const b: Paise; // brand value
const sum: Paise = a + b; // ❌
// error TS2322: Type 'number' is not assignable to type 'Paise'.
//   Type 'number' is not assignable to type '{ readonly __brand: "Paise"; }'.
const sumOk = (a + b) as Paise; // re-brand explicitly inside a helper like addPaise()
```

---

## 🧠 Tricky Interview Question

```typescript
type UserId = string & { readonly __brand: "UserId" };
declare const id: UserId;

const s: string = id; // (1)
const m: Map<string, number> = new Map(); // (2)
m.set(id, 1); // (3)
const back: UserId = "usr_1"; // (4) ❌
```
**Answer:** (1) **compiles** - a brand is a *subtype* of its base, so it widens to `string` freely. (2)/(3) **compile**: `UserId` is a `string`, so it works as a Map key (and at runtime it is just the string). (4) is an **error**: the plain literal `"usr_1"` lacks the phantom `__brand`. This asymmetry is the whole design - **brand → base is free, base → brand needs a constructor**.
```typescript
type UserId2 = string & { readonly __brand: "UserId" };
const back: UserId2 = "usr_1"; // ❌
// error TS2322: Type 'string' is not assignable to type 'UserId2'.
//   Type 'string' is not assignable to type '{ readonly __brand: "UserId"; }'.
```

---

## ⚫ Interview Questions + Answers

Q1: What is nominal typing and how do you emulate it in TypeScript?
A1: Nominal typing means two types are compatible only if they have the same **declared name**; TypeScript is structural, so same shape means compatible. You emulate nominal types with **branding**: intersect a base type with a phantom tag (`string & { __brand: "UserId" }`) so otherwise identical types become incompatible, with no runtime cost.

Q2: Why not just use a class `UserId` wrapping a string?
A2: A class allocates an object per id, breaks `JSON.stringify`/equality (`===`), complicates SQL parameter binding and Redux serializability. Brands are erased: the runtime value stays a primitive string. Also private fields in classes make classes nominal-ish, but at the cost above.

Q3: Where should the cast to a branded type live?
A3: In **smart constructors / validators at the system boundary**: Zod schema with `.brand()`, a `parseUserId` function, or a DB mapper. Everything inside the core then passes branded values and never re-validates. Enforce with a lint rule (`no-restricted-syntax` on `as UserId`) so casts do not spread.

Q4: How do branded types help with money and units?
A4: `Paise` and `Rupees` are both `number`, so `rupees + paise` compiles and gives a 100x bug. With brands the addition requires explicit conversion helpers (`toRupees`), making unit mistakes compile errors. Arithmetic returns plain `number`, so wrap arithmetic in helpers (`addPaise(a, b): Paise`).

Q5: `unique symbol` brand vs string-key brand - which is better?
A5: The `unique symbol` key (`declare const brand: unique symbol; T & { [brand]: Tag }`) cannot be written by consumers (the symbol is not exported), so the brand cannot be faked with an object literal. The string key `__brand` is simpler and shows nicely in error messages (as seen above), but is forgeable. Libraries like Zod use a symbol-based `BRAND` for this reason.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Different IDs share a primitive type (`UserId`, `OrderId`, `PaymentId`) and swapping them is a real risk
- Units or states matter (`Paise` vs `Rupees`, `Sanitized` vs raw HTML, `Validated<Email>`)
- You want zero runtime cost compile-time safety, with validation at API/DB boundaries

❌ Avoid when:
- A function has a single `string` parameter and no other confusable ids (extra ceremony)
- Data is untrusted and you cannot add a validation step (brand would lie)
- The team will cast everywhere (`as UserId`) - then it is false safety; fix with constructors + lint first

---

## 📊 Visual Diagram
```
STRUCTURAL (default)                 BRANDED (nominal-like)
────────────────────────             ──────────────────────────────────
UserId  = string                     UserId  = string & { __brand:"UserId"  }
OrderId = string                     OrderId = string & { __brand:"OrderId" }
   UserId  ◄──►  OrderId  ✅ mix        UserId  ──✗──►  OrderId   ❌
                                        UserId  ───────►  string  ✅ (widening)
                                        string  ──✗──►  UserId    ❌ (needs constructor)

raw string ──► toUserId(raw) ──► UserId ──► getOrder(userId, orderId)
               (validate + cast)            (compiler enforces the kind)

Runtime: brand does not exist -> still a plain string, zero overhead
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Structural typing | Compatibility by shape | shape से compatibility |
| Nominal typing | Compatibility by declared name | declared नाम से compatibility |
| Brand / tag | Phantom property making a type unique | type को अलग करने वाली phantom property |
| Phantom type | Exists only at compile time | सिर्फ compile time पर मौजूद |
| Smart constructor | Function that validates then brands | validate करके brand लगाने वाला function |
| unique symbol | A symbol type that is distinct per declaration | हर declaration पर अलग symbol type |

---

## ⚡ 3-Line Summary
English:
1. Branding (`string & { __brand: "X" }`) makes same-shaped types incompatible with zero runtime cost.
2. Brand -> base is automatic; base -> brand only via a smart constructor or validator (Zod `.brand()`).
3. Use it for IDs, money units and validated data, and keep the `as` cast in exactly one place.

Hindi:
1. Branding (`string & { __brand: "X" }`) एक जैसी shape वाले types को incompatible बना देता है, runtime cost zero।
2. Brand -> base अपने आप चलता है; base -> brand सिर्फ smart constructor या validator (Zod `.brand()`) से।
3. IDs, money units और validated data के लिए इस्तेमाल करो, और `as` cast सिर्फ एक जगह रखो।

---

## ➡️ Next Topic
**59. Distributive Conditional Types** — why `T extends U ? X : Y` splits a union and how `[T] extends [U]` stops it.
