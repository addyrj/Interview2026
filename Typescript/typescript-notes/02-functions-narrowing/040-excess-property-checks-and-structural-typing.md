# 40. Excess Property Checks and Structural Typing
# हिंदी में: Excess Property Checks और Structural Typing

> Verified with **TypeScript 5.x** (compiled with 5.9, `--strict`). Rules below are stable across 5.x. `satisfies` mentioned here is TS 4.9+.

---

## 🔵 Simple Definition (English)
**Structural typing** means TypeScript decides whether two types are compatible by their **shape** (members and their types), not by their declared names. If a value has *at least* the required properties, it fits ("duck typing, checked at compile time"). **Excess property checking** is a special extra rule: when you assign a **fresh object literal** directly to a typed target, TypeScript also rejects properties the target does not know about — to catch typos.

## 🔵 सरल परिभाषा (Hindi)
**Structural typing** का मतलब: TypeScript दो types को compatible तब मानता है जब उनकी **shape** (members और उनके types) मिलती हो — declared नाम नहीं देखे जाते। अगर value में *कम से कम* ज़रूरी properties हैं तो वह fit हो जाती है ("duck typing, जो compile time पर check होती है")। **Excess property checking** एक अलग extra rule है: जब आप **fresh object literal** को सीधे typed target में assign करते हो, तो TypeScript वे properties भी reject करता है जो target को पता नहीं — typos पकड़ने के लिए।

---

## 🔴 Problem it Solves
- **Structural typing** lets you pass any object with the right fields to a function — no `implements` ceremony, easy mocking in tests, works with JSON from APIs, and interoperates with plain JavaScript.
- But pure structural typing would accept `{ amount: 100, curreny: "INR" }` for `{ amount: number; currency?: string }` — the typo `curreny` is just an "extra" property. **Excess property checks** close that hole for literals, where the typo is almost certainly a bug.

## 🔴 यह क्यों बना? (Hindi)
- **Structural typing** से आप सही fields वाला कोई भी object function को दे सकते हो — `implements` की औपचारिकता नहीं, tests में mocking आसान, API के JSON के साथ ठीक, और plain JavaScript के साथ मेल।
- लेकिन सिर्फ structural typing `{ amount: 100, curreny: "INR" }` को `{ amount: number; currency?: string }` के लिए भी मान लेता — `curreny` typo बस एक "extra" property होती। **Excess property checks** literals के लिए यह कमी बंद करते हैं, जहाँ typo लगभग हमेशा bug होती है।

---

## 🟢 How it Works — Step by Step

Step 1 → Assignability: `S` is assignable to `T` if for each property in `T`, `S` has a compatible property. Extra properties in `S` are **fine**.
Step 2 → A **fresh** object literal (written directly at the assignment/call/return site) is also checked for properties **not in** `T` → error TS2353.
Step 3 → Once the literal is stored in a variable, it is no longer "fresh". Passing the variable skips the excess check.
Step 4 → **Weak types** (all properties optional) have an extra rule: the source must share **at least one** property, else TS2559, even for non-fresh values.
Step 5 → `private`/`protected` members and `#private` make a class **nominal-ish**: two classes with identical public shape but separate private declarations are not compatible.
Step 6 → To intentionally allow extra keys use an index signature (`[key: string]: unknown`), spread (`{...base, extra}`), or a type assertion.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Assignability: `S`, `T` में assign हो सकता है अगर `T` की हर property के लिए `S` में compatible property हो। `S` की extra properties **ठीक** हैं।
Step 2 → **Fresh** object literal (assignment/call/return की जगह सीधे लिखा) में उन properties की भी जाँच होती है जो `T` में **नहीं** हैं → error TS2353।
Step 3 → Literal को variable में रखते ही वह "fresh" नहीं रहता। Variable pass करने पर excess check skip हो जाता है।
Step 4 → **Weak types** (सारी properties optional) का एक अतिरिक्त नियम: source में **कम से कम एक** common property होनी चाहिए, वरना TS2559, non-fresh values पर भी।
Step 5 → `private`/`protected` members और `#private` classes को **nominal जैसा** बना देते हैं: public shape एक जैसी हो पर private declarations अलग हों तो classes compatible नहीं।
Step 6 → जान-बूझकर extra keys चाहिए तो index signature (`[key: string]: unknown`), spread (`{...base, extra}`) या type assertion इस्तेमाल करो।

---

## 🟡 Real World Example
**Zomato order API**: the `createOrder(input: { restaurantId: string; items: string[]; couponCode?: string })` function. The mobile team sends `{ restaurantId, items, couponcode }` (lowercase c) — with a literal, the compiler catches the typo immediately; with a pre-built variable it would silently ignore the coupon and customers would complain about missing discounts. Knowing **when** the check applies explains this bug class.

## 🟡 Real Example Hindi mein
**Zomato order API**: `createOrder(input: { restaurantId: string; items: string[]; couponCode?: string })` function। Mobile team `{ restaurantId, items, couponcode }` (छोटा c) भेजती है — literal हो तो compiler typo तुरंत पकड़ लेता है; पहले से बने variable में यह चुपचाप coupon ignore कर देता और customers discount न मिलने की शिकायत करते। **कब** check लगता है यह जानना इसी तरह के bug को समझाता है।

---

## 💻 Code Example — Basic

```typescript
// Target type: what createOrder accepts
interface OrderInput { restaurantId: string; items: string[]; couponCode?: string }

function createOrder(input: OrderInput): string {
  return `${input.restaurantId}:${input.items.length}:${input.couponCode ?? "none"}`; // summary
}

// Structural typing: extra property on a VARIABLE is fine (not fresh)
const fromApp = { restaurantId: "r1", items: ["Dosa"], couponcode: "SAVE10" }; // typo'd key kept
console.log(createOrder(fromApp)); // compiles! typo silently ignored at runtime
// Output:
// r1:1:none
```

```typescript
// ❌ Same typo as a FRESH literal passed directly => excess property check fires
interface OrderInput { restaurantId: string; items: string[]; couponCode?: string }
declare function createOrder(input: OrderInput): string; // signature only, enough to type-check
createOrder({ restaurantId: "r1", items: ["Dosa"], couponcode: "SAVE10" });
// error TS2561: Object literal may only specify known properties, but 'couponcode' does not exist in type 'OrderInput'. Did you mean to write 'couponCode'?
```

## 💻 Code Example — Advanced

```typescript
// Structural compatibility between unrelated declarations (no `implements` needed)
interface Payable { amount: number; currency: string } // what the payment fn needs

class UpiPayment {            // a class that happens to have the same shape
  constructor(public amount: number, public currency: string, public vpa: string) {}
}
const plain = { amount: 250, currency: "INR", note: "dinner" }; // plain object with extra field

function pay(p: Payable): string { return `${p.amount} ${p.currency}`; } // accepts anything with shape

console.log(pay(new UpiPayment(100, "INR", "a@upi")), "|", pay(plain)); // both OK
// Output:
// 100 INR | 250 INR
```

```typescript
// Opt-in to extra keys: index signature on the target
interface EventPayload { type: string; [extra: string]: unknown } // extra keys allowed

const evt: EventPayload = { type: "click", x: 10, y: 20 }; // no excess error, extras unknown
// Spread bypass: fresh-ness is about the literal's own written properties
interface Base { id: string }
const withExtra: Base = { ...{ id: "a", leaked: true } }; // compiles: spread source is not checked
console.log(evt.type, Object.keys(withExtra).join(","));
// Output:
// click id,leaked
```

```typescript
// Private members make classes (nearly) nominal: same shape is not enough
class Money {
  #paise: number;                       // ECMAScript private field
  constructor(paise: number) { this.#paise = paise; }
  get rupees(): number { return this.#paise / 100; }
}
function show(m: Money): number { return m.rupees; }

console.log(show(new Money(2599)));                 // real Money: fine
// show({ rupees: 25.99 });                         // would be an error: missing #paise
// Output:
// 25.99
```

---

## 🟠 Node/Express + React Integration

```typescript
import express from "express";                  // express runtime
import type { Request, Response } from "express";

interface CreateOrderBody { restaurantId: string; items: string[] } // DTO shape

const app = express();
app.use(express.json());

app.post("/orders", (req: Request<unknown, unknown, CreateOrderBody>, res: Response) => {
  // req.body is TYPED as CreateOrderBody but at RUNTIME it can have any extra keys!
  // Structural typing is compile-time only: still validate/strip with Zod in real code.
  const { restaurantId, items } = req.body;       // destructure only what you trust
  res.status(201).json({ restaurantId, count: items.length }); // fresh literal: checked vs nothing
});
```

```tsx
// React props: excess property check also applies to JSX attributes
interface BadgeProps { label: string }
function Badge({ label }: BadgeProps) { return <b>{label}</b>; }

export const ok = <Badge label="Hot" />;                  // fine
const extra = { label: "Hot", color: "red" };            // variable with extra field
export const spreadOk = <Badge {...extra} />;             // spread: no excess check, compiles
```

```tsx
// ❌ Explicit extra attribute on JSX is a fresh-literal-like check
function Badge({ label }: { label: string }) { return <b>{label}</b>; }
export const bad = <Badge label="a" color="red" />; // wrong: color is not a prop
// error TS2322: Type '{ label: string; color: string; }' is not assignable to type 'IntrinsicAttributes & { label: string; }'.
//   Property 'color' does not exist on type 'IntrinsicAttributes & { label: string; }'.
```

**Redux note:** `dispatch({ type: "cart/add", payload, extra: 1 })` on a typed `Action` union gets excess checks only when the literal is written inline. Action creators (`cartSlice.actions.add(payload)`) avoid the typo class entirely.

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: Assuming excess property checks protect every assignment.**

```typescript
// ❌ Typo through an intermediate variable: excess check is skipped, only the weak-type rule fires
interface Opts { timeout?: number; retries?: number }
const o = { timeOut: 5 };      // note capital O
const p: Opts = o;             // this is a WEAK TYPE check, not an excess check
// error TS2559: Type '{ timeOut: number; }' has no properties in common with type 'Opts'.
```

Here the weak-type rule saved us because there was *no* overlap. If `o` had also contained `retries: 3`, it would compile silently with `timeOut` ignored.

```typescript
// ✅ Use satisfies to get literal-style checking while keeping the precise type
interface Opts { timeout?: number; retries?: number }
const o = { timeout: 5, retries: 2 } satisfies Opts; // typo here would error (TS 4.9+)
console.log(o.timeout);
// Output:
// 5
```

**Mistake 2: Expecting two identical-looking classes to be interchangeable.**

```typescript
// ❌ Private declarations are separate => not compatible
class A { private id = 1; name = "a" }
class B { private id = 1; name = "a" }
const a: A = new B(); // wrong
// error TS2322: Type 'B' is not assignable to type 'A'.
//   Types have separate declarations of a private property 'id'.
```

**Mistake 3: Trusting the compile-time shape of request bodies.** `Request<..., Body>` only *labels* `req.body`. Clients can send anything; use Zod `.strict()` / `.strip()` to enforce at runtime.

---

## 🧠 Tricky Interview Question

```typescript
// ❌ (line 2 is intentionally wrong)
interface P { a: number }
const o = { a: 1, b: 2 };
const x: P = o;              // (1)
const y: P = { a: 1, b: 2 }; // (2) ❌ wrong: fresh literal with excess b
// error TS2353: Object literal may only specify known properties, and 'b' does not exist in type 'P'.
const z: P = { a: 1, b: 2 } as P; // (3)
```
**Answer:** (1) compiles — `o` is not fresh, extra `b` is allowed by structural typing. (2) **errors** with TS2353 (the real message is quoted above) — fresh literal, `b` is excess. (3) compiles — a type assertion switches off the excess check (and is why `as` can hide typos). Same data, three outcomes: the difference is purely *freshness*. Runtime behaviour of all three is identical because types are erased.

---

## ⚫ Interview Questions + Answers

**Q1: What is structural typing and how is it different from nominal typing?**
A1: Compatibility is determined by member shapes, not declared names. In nominal systems (Java, C#) `class A` and `class B` with the same members are different types. In TS they are interchangeable unless private/protected members or branding (topic 58) separate them.

**Q2: What is an excess property check and when does it NOT run?**
A2: It flags unknown properties on a *fresh object literal* assigned/passed/returned to a typed target. It does NOT run for non-fresh values (variables), spreads, type assertions, or when the target has an index signature / is `object`/`any`.

**Q3: What is a "weak type" error (TS2559)?**
A3: A target whose properties are all optional. Any source with zero overlapping properties is rejected even if not fresh, preventing accidentally passing a totally unrelated object.

**Q4: How can you make a TS type behave nominally?**
A4: Use a `private`/`#private` member in classes, or add a brand: `type UserId = string & { readonly __brand: "UserId" }` (topic 58).

**Q5: Why is `req.body: CreateOrderBody` not a real guarantee in Express?**
A5: Because structural types are erased; the actual JSON can have missing or extra fields. Runtime validation (Zod/Joi) is required — `z.infer` gives you the matching static type.

---

## 🔷 When to Use + When Not to Use
✅ Rely on structural typing when:
- Writing functions that need only a few fields (accept the narrowest interface)
- Mocking dependencies in tests (any object with the right shape)
- Consuming JSON/DTOs from other services

✅ Keep excess property checks (fresh literals / `satisfies`) when:
- Building config/option objects where typos are likely

❌ Don't depend on them when:
- Security-sensitive input (mass-assignment!) — always strip unknown keys at runtime
- You need real identity (IDs, money) — use branded/nominal types

---

## 📊 Visual Diagram
```
 value ──► target type
   │
   ├─ has all required props with right types? ── no ──► ERROR (missing/incompatible)
   │            │ yes
   │            ▼
   ├─ is it a FRESH object literal? ── yes ─► any prop not in target? ─► ERROR TS2353
   │            │ no (variable/spread/as)              │ no
   │            ▼                                       ▼
   └─ target is weak (all optional)? ── yes ─► shares ≥1 prop? ── no ─► ERROR TS2559
                                  │ no                     │ yes
                                  ▼                         ▼
                                OK  ◄───────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Structural typing | Compatibility by shape | Shape के आधार पर compatibility |
| Nominal typing | Compatibility by declared name | नाम के आधार पर compatibility |
| Fresh literal | Object literal written at the use site | उसी जगह लिखा object literal |
| Excess property check | Unknown keys in fresh literal are errors | Fresh literal में अनजान keys पर error |
| Weak type | All properties optional | सारी properties optional वाला type |
| Brand | Fake tag making a type nominal | Type को nominal बनाने वाला tag |

---

## ⚡ 3-Line Summary
English:
1. TS compares types by shape: any value with the required properties fits, extra properties included.
2. Fresh object literals get an extra excess-property check (TS2353); variables, spreads and `as` skip it; weak types need one shared property (TS2559).
3. Types vanish at runtime, so validate untrusted input with Zod and use `satisfies`/brands where you need stricter guarantees.

Hindi:
1. TS types को shape से compare करता है: ज़रूरी properties वाली कोई भी value fit होती है, extra properties के साथ भी।
2. Fresh object literals पर अतिरिक्त excess-property check (TS2353) लगता है; variables, spreads और `as` उसे skip करते हैं; weak types में एक common property ज़रूरी है (TS2559)।
3. Types runtime पर गायब हैं, इसलिए untrusted input को Zod से validate करो और सख़्त guarantee चाहिए तो `satisfies`/brands इस्तेमाल करो।

---

## ➡️ Next Topic
**41. Generics Basics** — writing one function or type that works for many types without losing type safety (`<T>`).
