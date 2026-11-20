# 59. Distributive Conditional Types
# हिंदी में: Distributive Conditional Types (union पर बँटकर लगने वाले conditional types)

> TypeScript 5.x (`tsc --strict`, TS 5.9) पर verify किया गया। Conditional types TS 2.8 से हैं और distribution शुरू से उनका नियम है; `infer ... extends` constraint TS 4.7+।

---

## 🔵 Simple Definition (English)
A conditional type `T extends U ? X : Y` is **distributive** when `T` is a **naked type parameter** (just `T`, not wrapped in `[T]`, `T[]`, `Promise<T>` etc.) and a **union** is passed in. TypeScript then applies the conditional to **each member separately** and unions the results: `ToArray<A | B>` = `ToArray<A> | ToArray<B>`. Wrap in a tuple `[T] extends [U]` to **turn distribution off**.

## 🔵 सरल परिभाषा (Hindi)
Conditional type `T extends U ? X : Y` तब **distributive** होता है जब `T` एक **naked type parameter** हो (सिर्फ `T`, `[T]`, `T[]`, `Promise<T>` आदि में लिपटा नहीं) और उसे **union** दिया जाए। तब TypeScript conditional को union के **हर member पर अलग-अलग** लगाता है और नतीजों का union बना देता है: `ToArray<A | B>` = `ToArray<A> | ToArray<B>`। Distribution **बंद** करने के लिए `[T] extends [U]` लिखो।

---

## 🔴 Problem it Solves
Without distribution, `Exclude<"UPI" | "COD", "COD">` would test the **whole** union against `"COD"` once and return either everything or nothing - useless for filtering. Distribution is what lets `Exclude`, `Extract`, `NonNullable` and every "map over union members" utility work. But it also **surprises**: `IsNever<never>` returns `never` instead of `true`, and `IsUnion<"a" | "b">` is wrongly `boolean`. Knowing when distribution happens (and how to stop it) is a classic senior-level interview topic.

## 🔴 यह क्यों बना? (Hindi)
Distribution न होती तो `Exclude<"UPI" | "COD", "COD">` पूरे union को एक बार `"COD"` से test करता और या तो सब लौटाता या कुछ नहीं - filtering के लिए बेकार। Distribution की वजह से ही `Exclude`, `Extract`, `NonNullable` और union के हर member पर चलने वाली हर utility काम करती है। पर यह **चौंकाती** भी है: `IsNever<never>` `true` की जगह `never` देता है, और `IsUnion<"a" | "b">` गलत तरीके से `boolean` बन जाता है। Distribution कब होती है (और कैसे रोकें) यह senior interviews का classic सवाल है।

---

## 🟢 How it Works — Step by Step

Step 1 → Write `type F<T> = T extends string ? "S" : "N"`. Here the checked type is the naked parameter `T`.
Step 2 → Call `F<string | number>`. TS splits the union: `F<string> | F<number>` = `"S" | "N"`.
Step 3 → Each member is evaluated alone, so you can **keep, drop or transform** members: `T extends U ? never : T` drops (this is `Exclude`).
Step 4 → `never` is the **empty union**: distributing over zero members yields zero results, so `F<never>` = `never` (not `"S"` or `"N"`).
Step 5 → **Opt out** by wrapping both sides: `[T] extends [U] ? X : Y`. Now the whole union is tested at once.
Step 6 → Distribution only happens for a **type parameter** being checked. `string | number extends string ? ...` written with concrete types does **not** distribute.
Step 7 → A helper alias can force distribution on a non-naked position: `type Dist<T> = T extends unknown ? Wrap<T> : never`.
Step 8 → `boolean` is `true | false` internally, so it distributes too: `ToArray<boolean>` = `true[] | false[]`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `type F<T> = T extends string ? "S" : "N"` लिखो। यहाँ जाँचा जाने वाला type naked parameter `T` है।
Step 2 → `F<string | number>` call करो। TS union को बाँट देता है: `F<string> | F<number>` = `"S" | "N"`।
Step 3 → हर member अकेले evaluate होता है, इसलिए members को **रखना, हटाना या बदलना** आसान है: `T extends U ? never : T` हटाता है (यही `Exclude` है)।
Step 4 → `never` **खाली union** है: शून्य members पर distribute करने से शून्य नतीजे, इसलिए `F<never>` = `never` (`"S"` या `"N"` नहीं)।
Step 5 → **बंद करना**: दोनों तरफ wrap करो `[T] extends [U] ? X : Y`। अब पूरा union एक साथ test होता है।
Step 6 → Distribution सिर्फ जाँचे जा रहे **type parameter** पर होती है। Concrete types से लिखा `string | number extends string ? ...` distribute **नहीं** करता।
Step 7 → Non-naked जगह पर distribution ज़बरदस्ती: `type Dist<T> = T extends unknown ? Wrap<T> : never`।
Step 8 → `boolean` अंदर से `true | false` है, इसलिए वह भी distribute होता है: `ToArray<boolean>` = `true[] | false[]`।

---

## 🟡 Real World Example
**Swiggy's** order-event union: `Placed | Accepted | PickedUp | Delivered`. A utility `PayloadOf<E> = E extends { payload: infer P } ? P : never` distributes, so `PayloadOf<OrderEvent>` is the union of **every** event's payload - used to type one generic logger. In **Razorpay's** SDK, `ApiResult<T> = T extends Error ? { ok: false; error: T } : { ok: true; value: T }` distributes over `Payment | RefundError`, producing a proper discriminated union automatically.

## 🟡 Real Example Hindi mein
**Swiggy** का order-event union: `Placed | Accepted | PickedUp | Delivered`। Utility `PayloadOf<E> = E extends { payload: infer P } ? P : never` distribute होती है, इसलिए `PayloadOf<OrderEvent>` **हर** event के payload का union है - एक generic logger को type करने के काम आता है। **Razorpay** के SDK में `ApiResult<T> = T extends Error ? { ok: false; error: T } : { ok: true; value: T }` `Payment | RefundError` पर distribute होकर अपने आप सही discriminated union बनाता है।

---

## 💻 Code Example — Basic

```typescript
// A distributive conditional: T is a naked type parameter
type ToArray<T> = T extends unknown ? T[] : never; // wraps EACH member separately

type A = ToArray<string | number>; // string[] | number[]   (distributed)

// Non-distributive version: [T] wraps the parameter, so the union is checked as a whole
type ToArrayAll<T> = [T] extends [unknown] ? T[] : never; // one array of the union
type B = ToArrayAll<string | number>; // (string | number)[]

const a: A = ["x"]; // OK: string[] is a member of A
const b: B = ["x", 1]; // OK: mixed array fits (string | number)[]
console.log(a, b); // [ 'x' ] [ 'x', 1 ]

// ❌ Mixed array does NOT fit the distributed result
const c: A = ["x", 1];
// error TS2322: Type '(string | number)[]' is not assignable to type 'A'.
//   Type '(string | number)[]' is not assignable to type 'string[]'.
//     Type 'string | number' is not assignable to type 'string'.
//       Type 'number' is not assignable to type 'string'.

// Exclude is just distribution + never
type MyExclude<T, U> = T extends U ? never : T; // never members vanish from the union
type Online = MyExclude<"UPI" | "CARD" | "COD", "COD">; // "UPI" | "CARD"
const method: Online = "UPI"; // OK
console.log(method); // UPI

// never is the empty union: distribution yields never
type OnNever = ToArray<never>; // never (NOT never[])
const nothing: OnNever[] = []; // an array of never
console.log(nothing.length); // 0
```

## 💻 Code Example — Advanced

```typescript
// 1) The IsNever trap and its fix
type IsNeverBad<T> = T extends never ? true : false; // distributes over zero members
type R1 = IsNeverBad<never>; // never  (surprise! not true)

type IsNever<T> = [T] extends [never] ? true : false; // wrapped: no distribution
type R2 = IsNever<never>; // true
type R3 = IsNever<string>; // false
const t: R2 = true; // OK
console.log(t); // true

// 2) IsUnion: use distribution on purpose, then compare with the original
type IsUnion<T, U = T> = T extends unknown // distributes: T is ONE member here
  ? [U] extends [T] // U is the WHOLE union; does the whole fit in one member?
    ? false // yes -> T was not a union
    : true // no -> more than one member
  : never; // unreachable
type U1 = IsUnion<"a" | "b">; // true
type U2 = IsUnion<"a">; // false
const u1: U1 = true; // OK
console.log(u1); // true

// 3) Payload extraction from an event union (infer + distribution)
type OrderEvent =
  | { type: "PLACED"; payload: { orderId: string; amount: number } } // event 1
  | { type: "PAID"; payload: { orderId: string; txnId: string } } // event 2
  | { type: "CANCELLED" }; // event 3 has no payload

type PayloadOf<E> = E extends { payload: infer P } ? P : never; // each member alone
type AllPayloads = PayloadOf<OrderEvent>; // union of the two payload objects
const p: AllPayloads = { orderId: "o1", txnId: "t1" }; // OK
console.log(p.orderId); // o1

// 4) Distribute a transformation: add a trace id to every event, keep narrowing
type WithTrace<E> = E extends unknown ? E & { traceId: string } : never; // per-member intersection
type Traced = WithTrace<OrderEvent>; // 3 members, each with traceId
function describe(e: Traced): string {
  switch (e.type) { // discriminant survives distribution
    case "PLACED": return `placed ${e.payload.amount} @${e.traceId}`; // payload typed
    case "PAID": return `paid ${e.payload.txnId} @${e.traceId}`; // payload typed
    case "CANCELLED": return `cancelled @${e.traceId}`; // no payload here
  }
}
console.log(describe({ type: "PAID", payload: { orderId: "o1", txnId: "t9" }, traceId: "tr1" })); // paid t9 @tr1

// 5) Distribute over keys: make a union of "get" function names from a model
type Model = { id: string; amount: number; status: "NEW" | "PAID" }; // data model
type Getter<K extends string> = K extends string ? `get${Capitalize<K>}` : never; // distributes over keys
type Getters = Getter<keyof Model & string>; // "getId" | "getAmount" | "getStatus"
const g: Getters = "getAmount"; // OK
console.log(g); // getAmount

// 6) Boolean distributes too
type Flip<T> = T extends true ? "yes" : "no"; // checks each of true/false
type F = Flip<boolean>; // "yes" | "no"
const f: F = "no"; // OK
console.log(f); // no
```

---

## 🟠 Node/Express + React Integration

```typescript
import express from "express";

// Result type that distributes over success/error union returned by a service
class RefundError extends Error { constructor(public code: "LIMIT" | "NOT_FOUND") { super(code); } }
type Payment = { id: string; amount: number }; // success shape

// Distributes: Payment -> ok:true, RefundError -> ok:false
type ApiResult<T> = T extends Error ? { ok: false; error: T["message"] } : { ok: true; value: T };

// Service returns either a Payment or a RefundError
function refund(id: string): Payment | RefundError {
  return id === "p1" ? { id, amount: 499 } : new RefundError("NOT_FOUND"); // fake lookup
}

// Mapper turns the union into a proper discriminated union
function toResult<T>(v: T): ApiResult<T> {
  return (v instanceof Error ? { ok: false, error: v.message } : { ok: true, value: v }) as ApiResult<T>; // single cast
}

const app = express(); // create app
app.post("/refund/:id", (req, res) => {
  const r = toResult(refund(String(req.params.id))); // ApiResult<Payment | RefundError>
  if (r.ok) res.json(r.value); // narrowed to { ok: true; value: Payment }
  else res.status(404).json({ error: r.error }); // narrowed to { ok: false; error: string }
});
```

```tsx
import { useState, type ReactElement } from "react";

// Props that depend on a union: distribute so each "kind" has its own required fields
type Notice = { kind: "success"; orderId: string } | { kind: "error"; message: string };
type NoticeProps<N> = N extends { kind: infer K } ? { kind: K } & Omit<N, "kind"> : never; // per-member props

export function Banner(props: NoticeProps<Notice>): ReactElement {
  return props.kind === "success" ? <p>Order {props.orderId} placed</p> : <p>Error: {props.message}</p>; // narrowing works
}

export function Demo(): ReactElement {
  const [ok] = useState(true); // demo state
  return ok ? <Banner kind="success" orderId="o1" /> : <Banner kind="error" message="failed" />; // both valid
}
```

```typescript
// Redux Toolkit: action-type union -> payload union (distribution over a union of actions)
type Action = { type: "cart/add"; payload: string } | { type: "cart/clear" } | { type: "cart/coupon"; payload: { code: string } };
type PayloadOfAction<A> = A extends { payload: infer P } ? P : undefined; // undefined when no payload
type CartPayload = PayloadOfAction<Action>; // string | { code: string } | undefined
const sample: CartPayload = { code: "SAVE10" }; // OK
console.log(sample); // { code: 'SAVE10' }
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Checking `never` without wrapping
```typescript
type IsNever<T> = T extends never ? true : false; // distributes over never -> never
type X = IsNever<never>; // never
const x: X = true;
// ❌ error TS2322: Type 'true' is not assignable to type 'never'.  (X is never, nothing fits)

// Right: wrap in a tuple to stop distribution
type IsNeverOk<T> = [T] extends [never] ? true : false; // true for never
const y: IsNeverOk<never> = true; // compiles
```

❌ Mistake 2: Expecting a single check for "is any member a string?"
```typescript
type HasString<T> = T extends string ? true : false; // distributes
type H = HasString<string | number>; // boolean (true | false), not true
// Right: decide what you want. "ALL members strings?":
type AllStrings<T> = [T] extends [string] ? true : false; // whole union at once
type Z = AllStrings<string | number>; // false
```

❌ Mistake 3: Believing concrete unions distribute
✅ Correct: only a **naked type parameter** distributes. `type Bad = string | number extends string ? 1 : 2` is just `2` (no parameter involved). Inside a generic alias use `T`, or add a helper alias.

---

## 🧠 Tricky Interview Question

```typescript
type Wrap<T> = T extends any ? { v: T } : never;
type NoDist<T> = [T] extends [any] ? { v: T } : never;

type P = Wrap<string | number>;
type Q = NoDist<string | number>;
type R = Wrap<boolean>;
type S = Wrap<never>;
```
**Answer:** `P = { v: string } | { v: number }` (two object types). `Q = { v: string | number }` (one object whose `v` is the union). `R = { v: true } | { v: false }` because `boolean` is `true | false`. `S = never` - distributing over an empty union gives an empty result. Proof:
```typescript
type Wrap2<T> = T extends any ? { v: T } : never;
const p: Wrap2<string | number> = { v: "x" }; // OK, matches { v: string }
const bad: Wrap2<string | number> = { v: "x" as string | number }; // ❌
// error TS2322: Type '{ v: string | number; }' is not assignable to type '{ v: string; } | { v: number; }'.
//   Type '{ v: string | number; }' is not assignable to type '{ v: number; }'.
//     Types of property 'v' are incompatible.
//       Type 'string | number' is not assignable to type 'number'.
//         Type 'string' is not assignable to type 'number'.
```

---

## ⚫ Interview Questions + Answers

Q1: When is a conditional type distributive?
A1: When the checked type is a **naked type parameter** (`T extends U ? ...` where `T` is a type parameter, not `[T]`, `T[]` or an object containing it) and a **union** is supplied. TS evaluates the conditional once per member and unions the results. `Exclude`, `Extract` and `NonNullable` (pre-4.8) rely on it.

Q2: How do you prevent distribution?
A2: Wrap both sides of `extends` in a tuple: `[T] extends [U] ? X : Y`. The union is then compared as a whole. Used in `IsNever`, `IsEqual`-style helpers, and when you need "all members satisfy U".

Q3: Why does `type IsNever<T> = T extends never ? true : false` return `never` for `never`?
A3: `never` is the empty union. A distributive conditional maps over each member; with zero members the result is the empty union, i.e. `never` again - the branches never run. The fix is `[T] extends [never] ? true : false`.

Q4: How would you write a type that returns the keys of a discriminated union's discriminant values?
A4: `type Tags<E extends { type: string }> = E extends unknown ? E["type"] : never` - it distributes, so you get `"PLACED" | "PAID" | "CANCELLED"`. Even simpler is `E["type"]` (indexed access on a union already unions the results), but the distributive form allows per-member transformation (like `Extract<E, { type: K }>`).

Q5: How does distribution affect `boolean` and enums?
A5: `boolean` is `true | false`, so a distributive conditional returns two branches (`Flip<boolean>` = `"yes" | "no"`). A union enum distributes over its members too. If you need to treat `boolean` as one unit, use `[T] extends [boolean]`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want to filter/map each member of a union (`Exclude`, payload extraction, adding fields per member)
- Building discriminated unions from a generic input (`ApiResult<T>`)
- Writing utility types over event/action unions in Redux or message buses

❌ Avoid / switch off when:
- You need to test the union **as a whole** (`[T] extends [U]`)
- You are checking for `never` (always wrap)
- Distribution makes error messages explode on huge unions (performance: each member is evaluated separately)

---

## 📊 Visual Diagram
```
type F<T> = T extends string ? "S" : "N"

F<string | number | boolean>
   │
   ├── F<string>  ─► "S"
   ├── F<number>  ─► "N"
   ├── F<true>    ─► "N"      (boolean = true | false)
   └── F<false>   ─► "N"
   ▼
 "S" | "N"                         ← union of the results

Opt out:  [T] extends [string] ? "S" : "N"
   F2<string | number> ─► "N"      (whole union tested once)

never:    F<never> ─► never         (zero members, zero results)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Distributive conditional | Conditional applied per union member | union के हर member पर लगने वाला conditional |
| Naked type parameter | `T` alone, not wrapped | अकेला `T`, किसी में लिपटा नहीं |
| Non-distributive wrap | `[T] extends [U]` | distribution बंद करने वाला tuple wrap |
| never | Empty union / no values | खाली union |
| infer | Capture a type inside `extends` | `extends` के अंदर type पकड़ना |
| Discriminant | Literal tag property in a union | union की पहचान वाली literal property |

---

## ⚡ 3-Line Summary
English:
1. `T extends U ? X : Y` with a naked `T` splits a union and evaluates each member separately.
2. `never` distributes to `never`; use `[T] extends [never]` to detect it, and `[T] extends [U]` to stop distribution.
3. `Exclude`, `Extract` and payload-extraction utilities are all distribution plus `never` filtering.

Hindi:
1. Naked `T` के साथ `T extends U ? X : Y` union को बाँटकर हर member अलग evaluate करता है।
2. `never` distribute होकर `never` ही रहता है; उसे पहचानने के लिए `[T] extends [never]` और distribution रोकने के लिए `[T] extends [U]` लगाओ।
3. `Exclude`, `Extract` और payload-extraction utilities सब distribution + `never` filtering हैं।

---

## ➡️ Next Topic
**60. Type-level Programming Patterns** — recursion, tuples as counters and string parsing at the type level.
