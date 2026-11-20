# 11. Intersection Types
# हिंदी में: Intersection Types (दो या ज़्यादा types को मिलाना)

> TypeScript 5.x (`tsc --strict`, TS 5.9) पर verify किया गया। Intersection `&` शुरू से है; TS 3.9+ में impossible intersections (जैसे conflicting discriminants) `never` में reduce होते हैं।

---

## 🔵 Simple Definition (English)
An **intersection type** `A & B` describes a value that has **all** the members of `A` **and** all the members of `B` at the same time. Where a union (`A | B`) means "one of", an intersection means "all of". It is mostly used to **compose** object types: `User & Timestamps & Audit`.

## 🔵 सरल परिभाषा (Hindi)
**Intersection type** `A & B` ऐसी value बताता है जिसमें `A` के **सारे** members **और** `B` के सारे members **एक साथ** हों। Union (`A | B`) का मतलब "इनमें से कोई एक" है, intersection का मतलब "सब कुछ एक साथ"। इसका सबसे ज़्यादा इस्तेमाल object types को **compose** करने में होता है: `User & Timestamps & Audit`।

---

## 🔴 Problem it Solves
Real entities are built from reusable pieces: every DB row has `id`, `createdAt`, `updatedAt`; some also have `deletedAt` (soft delete) or `createdBy`. Copy-pasting those fields into every type causes drift. Interfaces can `extend`, but only for object types and only at declaration time. With intersection you can **build types on the fly** from small mixin-like types, also for function arguments (`req: Request & { user: AuthUser }`) without writing a new named interface each time.

## 🔴 यह क्यों बना? (Hindi)
Real entities छोटे reusable टुकड़ों से बनती हैं: हर DB row में `id`, `createdAt`, `updatedAt` होता है; कुछ में `deletedAt` (soft delete) या `createdBy` भी। ये fields हर type में copy-paste करने से drift होता है। Interface `extend` कर सकता है, पर सिर्फ object types के लिए और declaration के समय। Intersection से आप **on the fly** छोटे mixin-जैसे types जोड़कर type बना सकते हैं, function arguments में भी (`req: Request & { user: AuthUser }`), हर बार नया named interface लिखे बिना।

---

## 🟢 How it Works — Step by Step

Step 1 → `A & B` is assignable to `A` and to `B` (it has everything both need). So an intersection is a **subtype** of each part.
Step 2 → To **create** a value of `A & B`, you must supply every required property of both. Missing one is an error.
Step 3 → If both sides have the **same property with different types**, the property type becomes the **intersection of those types**: `{ id: string } & { id: number }` has `id: string & number` = `never`.
Step 4 → If conflicting properties are **literal discriminants** (`kind: "a"` vs `kind: "b"`), the whole intersection reduces to `never` (TS 3.9+).
Step 5 → Intersection **distributes over unions**: `(A | B) & C` = `(A & C) | (B & C)`. Useful for adding common fields to every union member.
Step 6 → Intersecting primitives with objects gives **branded types**: `string & { __brand: "UserId" }` (see topic 58).
Step 7 → `interface X extends A, B` and `type X = A & B` look alike, but `extends` **reports conflicts** at the declaration, while `&` silently produces `never` properties.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `A & B`, `A` को भी assignable है और `B` को भी (इसमें दोनों की ज़रूरत की हर चीज़ है)। यानी intersection हर हिस्से का **subtype** है।
Step 2 → `A & B` की value **बनाने** के लिए दोनों की हर required property देनी पड़ती है। एक भी छूटी तो error।
Step 3 → अगर दोनों में **same property अलग types** के साथ है, तो property का type उन types का **intersection** बन जाता है: `{ id: string } & { id: number }` में `id: string & number` = `never`।
Step 4 → अगर conflicting properties **literal discriminants** हैं (`kind: "a"` बनाम `kind: "b"`), तो पूरा intersection `never` में reduce हो जाता है (TS 3.9+)।
Step 5 → Intersection **union पर distribute** होता है: `(A | B) & C` = `(A & C) | (B & C)`। हर union member में common fields जोड़ने के काम आता है।
Step 6 → Primitive को object से intersect करने पर **branded types** बनते हैं: `string & { __brand: "UserId" }` (topic 58 देखें)।
Step 7 → `interface X extends A, B` और `type X = A & B` एक जैसे दिखते हैं, पर `extends` conflict **declaration पर ही बता देता है**, जबकि `&` चुपचाप `never` property बना देता है।

---

## 🟡 Real World Example
**Razorpay's** order object is `BaseEntity & { amount: number; currency: "INR" }`, and a refunded payment is `Payment & { refundId: string; refundedAt: string }`. The dashboard code that lists payments takes `Payment`, while the refund screen takes `Payment & RefundInfo` - same base, extra fields, no duplicate declarations. In **Swiggy's** admin, every list API response is `Paginated & { items: Order[] }`.

## 🟡 Real Example Hindi mein
**Razorpay** का order object `BaseEntity & { amount: number; currency: "INR" }` है, और refunded payment `Payment & { refundId: string; refundedAt: string }`। Payments list करने वाला dashboard code `Payment` लेता है, जबकि refund screen `Payment & RefundInfo` लेती है - same base, extra fields, कोई duplicate declaration नहीं। **Swiggy** के admin में हर list API response `Paginated & { items: Order[] }` है।

---

## 💻 Code Example — Basic

```typescript
// Small reusable building blocks
type WithId = { id: string }; // every DB row has an id
type WithTimestamps = { createdAt: string; updatedAt: string }; // audit times
type WithSoftDelete = { deletedAt: string | null }; // soft-delete marker

// Compose them into one entity type using &
type Order = WithId & WithTimestamps & { amount: number; status: "PLACED" | "PAID" }; // all fields required

// A value must provide EVERY field from every part
const order: Order = {
  id: "ord_101", // from WithId
  createdAt: "2026-01-01T10:00:00Z", // from WithTimestamps
  updatedAt: "2026-01-01T10:05:00Z", // from WithTimestamps
  amount: 499, // from the inline object
  status: "PAID", // literal union from the inline object
};

// Intersection is a subtype of each part, so this assignment is allowed
const justId: WithId = order; // Order has id, so it fits WithId
console.log(justId.id); // "ord_101"

// Soft-deleted order = Order + one more piece
type DeletableOrder = Order & WithSoftDelete; // adds deletedAt
const gone: DeletableOrder = { ...order, deletedAt: "2026-02-01T00:00:00Z" }; // spread + new field
console.log(gone.deletedAt); // "2026-02-01T00:00:00Z"

// ❌ Missing a field from one part of the intersection
const bad: WithId & WithTimestamps = { id: "x", createdAt: "2026-01-01" };
// error TS2741: Property 'updatedAt' is missing in type '{ id: string; createdAt: string; }' but required in type 'WithTimestamps'.
```

## 💻 Code Example — Advanced

```typescript
// 1) Conflicting property types collapse to never
type A = { id: string }; // id is string
type B = { id: number }; // id is number
type AB = A & B; // id: string & number  ->  never

// ❌ You can never build an AB value
const ab: AB = { id: "1" };
// error TS2322: Type 'string' is not assignable to type 'never'.

// 2) Conflicting literal discriminants make the WHOLE type never (TS 3.9+)
type Paid = { status: "PAID"; paidAt: string };
type Failed = { status: "FAILED"; reason: string };
type Impossible = Paid & Failed; // reduces to never

// Proof: a function taking Impossible can never be called with a real object
declare function useImpossible(x: Impossible): void; // x is never
// ❌ Any object fails
useImpossible({ status: "PAID", paidAt: "now", reason: "x" });
// error TS2322: Type 'string' is not assignable to type 'never'.

// 3) Distribution over unions: add common fields to EVERY member
type PaymentEvent =
  | { type: "CAPTURED"; amount: number } // member 1
  | { type: "REFUNDED"; refundId: string }; // member 2
type Traceable<T> = T & { traceId: string; at: number }; // add trace info
type TracedEvent = Traceable<PaymentEvent>; // (M1 & trace) | (M2 & trace)

// Narrowing still works because the discriminant `type` is kept
function describe(e: TracedEvent): string {
  switch (e.type) { // discriminated union survives the intersection
    case "CAPTURED": return `captured ${e.amount} [${e.traceId}]`; // e.amount available
    case "REFUNDED": return `refunded ${e.refundId} [${e.traceId}]`; // e.refundId available
  }
}
console.log(describe({ type: "CAPTURED", amount: 250, traceId: "t1", at: 1 })); // captured 250 [t1]

// 4) Merging two function types gives an overloaded function
type Fmt = ((x: number) => string) & ((x: string) => string); // two call signatures
const fmt: Fmt = (x: number | string) => `<${x}>`; // one implementation satisfies both
console.log(fmt(5), fmt("hi")); // <5> <hi>

// 5) Utility: Prettify makes a hover-friendly flat object
type Prettify<T> = { [K in keyof T]: T[K] } & {}; // re-maps keys to flatten the & chain
type Flat = Prettify<WithIdLike & { name: string }>; // shows { id: string; name: string }
type WithIdLike = { id: string }; // helper used above
const flat: Flat = { id: "1", name: "Aditya" }; // compiles
console.log(flat); // { id: '1', name: 'Aditya' }
```

---

## 🟠 Node/Express + React Integration

```typescript
import express, { type Request, type Response, type NextFunction } from "express";

// The authenticated user, attached by auth middleware
type AuthUser = { userId: string; role: "CUSTOMER" | "ADMIN" };

// Express Request + our extra field = intersection, no global augmentation needed
type AuthedRequest = Request & { user: AuthUser };

const app = express(); // create the app
app.use(express.json()); // parse JSON bodies

// Middleware that guarantees req.user exists before the handler runs
function requireAuth(req: Request, _res: Response, next: NextFunction): void {
  (req as AuthedRequest).user = { userId: "u_1", role: "CUSTOMER" }; // pretend JWT was verified
  next(); // continue
}

// The handler declares that it expects an authenticated request
function getMyOrders(req: AuthedRequest, res: Response): void {
  res.json({ userId: req.user.userId, orders: [] }); // req.user is typed, no optional chaining
}

// Cast at the boundary only once: Express handler params are contravariant-ish
app.get("/orders", requireAuth, (req, res) => getMyOrders(req as AuthedRequest, res)); // wire it up
```

```tsx
import type { ComponentProps, ReactElement } from "react";

// Reuse the native button props and add our own: classic intersection use in React
type PayButtonProps = ComponentProps<"button"> & { amount: number; loading?: boolean };

// Component accepts every <button> attribute (onClick, disabled...) plus amount/loading
export function PayButton({ amount, loading = false, ...rest }: PayButtonProps): ReactElement {
  return (
    <button {...rest} disabled={loading || rest.disabled}>
      {loading ? "Processing..." : `Pay ₹${amount}`}
    </button>
  );
}

// Usage: <PayButton amount={499} onClick={() => console.log("pay")} />
```

```typescript
// Redux: entity state = EntityState-like base + UI flags
type LoadState = { loading: boolean; error: string | null }; // generic async flags
type CartItem = { sku: string; qty: number }; // one cart line
type CartState = LoadState & { items: CartItem[] }; // slice state via intersection

const initial: CartState = { loading: false, error: null, items: [] }; // initial state
console.log(initial); // { loading: false, error: null, items: [] }
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting `&` on unions of primitives to "merge" them
```typescript
// Wrong idea: "string and number" is NOT a flexible type, it is never
type Weird = string & number; // never

// ❌ nothing can be assigned
const w: Weird = "x";
// error TS2322: Type 'string' is not assignable to type 'never'.

// Right: use a union when you mean "either"
type Id = string | number; // either is fine
const ok: Id = "x"; // compiles
```

❌ Mistake 2: Using `&` where `extends` would give early conflict errors
```typescript
// Wrong (silent): conflict is hidden, price becomes never
type Base = { price: number }; // number price
type Sale = Base & { price: string }; // price: number & string = never (no error here!)

// Right: interface extends reports the conflict where you wrote it
interface Item { price: number } // number price
// ❌ conflicting override
interface SaleItem extends Item { price: string } // incompatible
// error TS2430: Interface 'SaleItem' incorrectly extends interface 'Item'.
//   Types of property 'price' are incompatible.
//     Type 'string' is not assignable to type 'number'.
```

❌ Mistake 3: Thinking `A & B` means "A or B has the property"
✅ Correct: the value must satisfy **both** at once. If you want "either shape", use `A | B` and narrow with a discriminant.

---

## 🧠 Tricky Interview Question

```typescript
type X = { a: string; b: number } & { b: string; c: boolean };
declare const x: X;
const b = x.b; // what is the type of b ?
const val: X = { a: "1", b: 1, c: true }; // ❌ does this compile?
// error TS2322: Type 'number' is not assignable to type 'never'.
```
**Answer:** `b` is `number & string`, which is `never`. Since a property of type `never` can never be satisfied, **no object literal can be assigned to `X`**, so `const val: X = { a: "1", b: 1, c: true }` fails with `error TS2322: Type 'number' is not assignable to type 'never'.` Interesting detail: TypeScript does **not** reduce the whole `X` to `never` (that only happens for conflicting **literal discriminant** properties like `kind: "a"` vs `kind: "b"`), so `x.a` and `x.c` are still accessible, but you can never construct an `X`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `A & B` and `A | B`?
A1: `A | B` accepts a value that is **either** `A` or `B` (you can only safely use the common members until you narrow). `A & B` requires a value that is **both** `A` and `B` (you can use all members of both). Union widens the set of allowed values; intersection narrows it.

Q2: `interface extends` vs `type &` - what are the differences?
A2: Both compose object types. `extends` checks compatibility at declaration time and reports conflicting properties immediately; `&` never errors at the declaration and silently makes conflicting properties `never`. Interfaces are also **cached by name** and give better error messages and slightly faster checking on big codebases; intersections work on any types (unions, functions, primitives) and can be created inline. Prefer `extends` for object hierarchies, `&` for ad-hoc composition.

Q3: What does `{ id: string } & { id: number }` evaluate to, and why?
A3: The type has property `id: string & number`, which is `never`, so no real value fits it. For two different **literal** discriminants (`status: "PAID"` & `status: "FAILED"`) the entire intersection collapses to `never` (TS 3.9+). It is a sign of a modelling bug, usually fixed with `Omit<A, "id"> & B` or by using a union.

Q4: How do you type an Express `Request` that has a `user` after auth middleware?
A4: Either declaration-merge `Express.Request` (global, affects every request - topic 83) or use a local intersection `type AuthedRequest = Request & { user: AuthUser }` and cast once at the route boundary. The intersection is explicit and scoped, the augmentation is convenient but global and makes `user` look present on unauthenticated routes too.

Q5: How does intersection interact with unions?
A5: It distributes: `(A | B) & C` = `(A & C) | (B & C)`. That is why `Traceable<PaymentEvent>` keeps the discriminated union intact and adds `traceId` to every member; narrowing on `type` still works.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Composing small reusable pieces (`WithId & WithTimestamps & Payload`)
- Extending third-party types without redeclaring them (`ComponentProps<"button"> & { loading?: boolean }`, `Request & { user: AuthUser }`)
- Adding common fields to every member of a union (distribution)
- Building branded types (`string & { __brand: "OrderId" }`)

❌ Avoid when:
- You are modelling "either/or" - use a union
- Property types may overlap/conflict - use `interface extends` (errors early) or `Omit<A, K> & B`
- A deep chain of `&` makes hover/error messages unreadable - wrap in `Prettify<T>` or declare a named `interface`

---

## 📊 Visual Diagram
```
INTERSECTION  A & B  =  "has everything from A AND B"

   ┌───────────┐     ┌───────────┐
   │ A         │     │ B         │
   │ id        │     │ createdAt │
   │ amount    │     │ updatedAt │
   └─────┬─────┘     └─────┬─────┘
         └───────┬─────────┘
                 ▼
        ┌─────────────────┐
        │ A & B           │   id, amount, createdAt, updatedAt
        └─────────────────┘   (subtype of A, and of B)

  Same prop, different types  ->  string & number  =  never
  Different literal tags      ->  whole type reduces to never
  (A | B) & C  ==  (A & C) | (B & C)       (distributes)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Intersection type | `A & B`, value has all members of both | दोनों के सारे members वाला type |
| Subtype | A more specific type usable where the parent is expected | ज़्यादा specific type |
| never | Type with no possible values | ऐसा type जिसकी कोई value नहीं |
| Discriminant | Literal property used to tell union members apart | union members पहचानने वाली literal property |
| Distribution | `&` spreading over each union member | हर union member पर लागू होना |
| Prettify | Helper that flattens an `&` chain for readable hovers | `&` chain को flat करने वाला helper |

---

## ⚡ 3-Line Summary
English:
1. `A & B` means "has all members of A and B"; use it to compose entity, props and request types.
2. Conflicting property types become `never` (silently); conflicting literal discriminants make the whole type `never`.
3. It distributes over unions, so you can add common fields to every union member while keeping narrowing.

Hindi:
1. `A & B` का मतलब "A और B दोनों के सारे members"; entity, props और request types compose करने में इस्तेमाल करो।
2. Conflicting property types चुपचाप `never` बन जाते हैं; conflicting literal discriminants पूरा type `never` कर देते हैं।
3. यह unions पर distribute होता है, इसलिए हर union member में common fields जोड़ सकते हो और narrowing भी चलती रहती है।

---

## ➡️ Next Topic
**12. Literal Types** — exact values (`"PAID"`, `42`, `true`) as types, the base of discriminated unions and `as const`.
