# 60. Type-level Programming Patterns
# हिंदी में: Type-level Programming Patterns (types से computation करना)

> TypeScript 5.x (`tsc --strict`, TS 5.9) पर verify किया गया। Recursive conditional types TS 4.1+; tail-recursion optimisation TS 4.5+ (limit ~1000 depth, non-tail ~50); `const` type parameters TS 5.0+।

---

## 🔵 Simple Definition (English)
**Type-level programming** means using TypeScript's type system as a small functional language: **conditional types** are `if`, **recursion** is a loop, **tuples** are arrays/counters, **template literal types** are string functions, **mapped types** are `map`, and **`infer`** is pattern matching. The "program" runs inside the compiler and produces types - there is **no runtime code**.

## 🔵 सरल परिभाषा (Hindi)
**Type-level programming** का मतलब TypeScript के type system को एक छोटी functional language की तरह इस्तेमाल करना: **conditional types** `if` हैं, **recursion** loop है, **tuples** arrays/counters हैं, **template literal types** string functions हैं, **mapped types** `map` हैं, और **`infer`** pattern matching है। यह "program" compiler के अंदर चलता है और types पैदा करता है - **कोई runtime code नहीं**।

---

## 🔴 Problem it Solves
Libraries like Express, Zod, tRPC, Prisma and Redux Toolkit give you types that **follow your data**: `app.get("/users/:id/orders/:orderId")` knows `req.params` has `id` and `orderId`; `z.object({...})` knows the output shape. Without type-level computation, you would write those types by hand and they would drift from the runtime values. Type-level patterns let a **single source of truth** (a string, an array, a schema) generate the types around it. Also a favourite senior interview area ("implement `Reverse`, `Length`, `Split`, `Get<T, "a.b.c">`").

## 🔴 यह क्यों बना? (Hindi)
Express, Zod, tRPC, Prisma और Redux Toolkit जैसी libraries ऐसे types देती हैं जो **आपके data को follow** करते हैं: `app.get("/users/:id/orders/:orderId")` जानता है कि `req.params` में `id` और `orderId` हैं; `z.object({...})` को output shape पता है। Type-level computation के बिना ये types हाथ से लिखने पड़ते और runtime values से अलग हो जाते। Type-level patterns से **एक single source of truth** (string, array, schema) अपने आसपास के types खुद generate करता है। यह senior interviews का पसंदीदा क्षेत्र भी है ("`Reverse`, `Length`, `Split`, `Get<T, "a.b.c">` implement करो")।

---

## 🟢 How it Works — Step by Step

Step 1 → **Branching**: `T extends U ? X : Y`. Booleans are the types `true` / `false`.
Step 2 → **Pattern matching**: `T extends `${infer Head}.${infer Tail}`` or `T extends [infer First, ...infer Rest]` captures pieces.
Step 3 → **Recursion**: a type alias may reference itself inside a conditional; the base case returns the accumulator.
Step 4 → **Accumulators**: add a second type parameter `Acc` with a default (`Acc extends unknown[] = []`) and build the result there; this also enables **tail recursion** (the recursive call is the last thing, so TS reuses the frame, depth up to ~1000).
Step 5 → **Counting**: tuples have a `length`. `[...Acc, unknown]["length"]` is "Acc + 1" - addition without numbers.
Step 6 → **String parsing**: template literals with `infer` split, trim, replace and join strings (route params, SQL column names).
Step 7 → **Mapping**: mapped types with `as` re-map keys; **keyof + indexed access** walks object paths.
Step 8 → **Guard rails**: use `extends string`/`extends unknown[]` constraints, cap recursion depth, and write **type tests** (`Expect<Equal<A, B>>`) next to every utility.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Branching**: `T extends U ? X : Y`। Booleans यहाँ `true` / `false` types हैं।
Step 2 → **Pattern matching**: `T extends `${infer Head}.${infer Tail}`` या `T extends [infer First, ...infer Rest]` से टुकड़े पकड़ो।
Step 3 → **Recursion**: type alias conditional के अंदर खुद को refer कर सकता है; base case में accumulator लौटाओ।
Step 4 → **Accumulators**: दूसरा type parameter `Acc` (default `Acc extends unknown[] = []`) जोड़ो और result उसमें बनाओ; इससे **tail recursion** भी मिलती है (recursive call सबसे आखिरी हो तो TS frame reuse करता है, depth ~1000 तक)।
Step 5 → **Counting**: tuples की `length` होती है। `[...Acc, unknown]["length"]` यानी "Acc + 1" - बिना numbers के addition।
Step 6 → **String parsing**: template literals + `infer` से strings split, trim, replace, join होते हैं (route params, SQL column names)।
Step 7 → **Mapping**: `as` वाले mapped types keys re-map करते हैं; **keyof + indexed access** object paths पर चलता है।
Step 8 → **Guard rails**: `extends string`/`extends unknown[]` constraints, recursion depth की सीमा, और हर utility के साथ **type tests** (`Expect<Equal<A, B>>`)।

---

## 🟡 Real World Example
**Express's** own typings parse `"/users/:id/orders/:orderId"` at the type level into `{ id: string; orderId: string }` for `req.params` (this is the `RouteParameters` type). **tRPC** and **Zod** infer entire API shapes from schemas. In a **Swiggy** codebase you may write `type Path<T>` so `getIn(order, "restaurant.address.city")` autocompletes only valid dotted paths and returns the exact leaf type - catching typos in analytics event paths at compile time.

## 🟡 Real Example Hindi mein
**Express** की अपनी typings `"/users/:id/orders/:orderId"` को type level पर parse करके `req.params` के लिए `{ id: string; orderId: string }` बनाती हैं (यह `RouteParameters` type है)। **tRPC** और **Zod** schemas से पूरे API shapes infer करते हैं। **Swiggy** जैसे codebase में आप `type Path<T>` लिख सकते हैं ताकि `getIn(order, "restaurant.address.city")` सिर्फ valid dotted paths autocomplete करे और सही leaf type लौटाए - analytics event paths की typos compile time पर पकड़ी जाती हैं।

---

## 💻 Code Example — Basic

```typescript
// ===== Type-level "functions" over tuples and strings =====

// Length: read the tuple length property
type Length<T extends readonly unknown[]> = T["length"]; // number literal type
type L = Length<["UPI", "CARD", "COD"]>; // 3

// First / Last using infer pattern matching
type First<T extends unknown[]> = T extends [infer F, ...unknown[]] ? F : never; // head
type Last<T extends unknown[]> = T extends [...unknown[], infer L] ? L : never; // tail
type F1 = First<["a", "b", "c"]>; // "a"
type L1 = Last<["a", "b", "c"]>; // "c"

// Reverse: recursion with pattern matching
type Reverse<T extends unknown[]> = T extends [infer H, ...infer R] ? [...Reverse<R>, H] : []; // loop
type Rev = Reverse<[1, 2, 3]>; // [3, 2, 1]

// Split a string on a separator
type Split<S extends string, D extends string> = S extends `${infer A}${D}${infer B}`
  ? [A, ...Split<B, D>] // take first piece, recurse on rest
  : [S]; // no more separators
type Parts = Split<"restaurant.address.city", ".">; // ["restaurant", "address", "city"]

// Type-level assertions: compile-time "unit tests"
type Equal<A, B> = (<T>() => T extends A ? 1 : 2) extends (<T>() => T extends B ? 1 : 2) ? true : false; // strict equality
type Expect<T extends true> = T; // errors unless T is true

type T1 = Expect<Equal<L, 3>>; // passes
type T2 = Expect<Equal<Rev, [3, 2, 1]>>; // passes
type T3 = Expect<Equal<Parts, ["restaurant", "address", "city"]>>; // passes

const ok: [T1, T2, T3] = [true, true, true]; // all tests green
console.log(ok); // [ true, true, true ]

// ❌ A wrong expectation fails at compile time
type Bad = Expect<Equal<Reverse<[1, 2]>, [1, 2]>>;
// error TS2344: Type 'false' does not satisfy the constraint 'true'.
```

## 💻 Code Example — Advanced

```typescript
// ===== 1) Dotted object paths: Path<T> and Get<T, P> =====
type Path<T> = T extends object // only objects have paths
  ? { [K in keyof T & string]: T[K] extends object ? K | `${K}.${Path<T[K]>}` : K }[keyof T & string]
  : never; // leaf values have no sub-path

type Get<T, P extends string> = P extends `${infer H}.${infer R}` // split at the first dot
  ? H extends keyof T ? Get<T[H], R> : never // go one level deeper
  : P extends keyof T ? T[P] : never; // last segment: read the property

interface Order {
  id: string; // plain field
  total: number; // plain field
  restaurant: { name: string; address: { city: string; pin: number } }; // nested object
}
type OrderPaths = Path<Order>; // "id" | "total" | "restaurant" | "restaurant.name" | "restaurant.address" | ...

function getIn<T, P extends Path<T> & string>(obj: T, path: P): Get<T, P> {
  return path.split(".").reduce((acc: any, key) => acc?.[key], obj); // runtime walk, `any` only inside
}
const order: Order = { id: "o1", total: 499, restaurant: { name: "Biryani House", address: { city: "Pune", pin: 411001 } } };
const city = getIn(order, "restaurant.address.city"); // type: string
const pin = getIn(order, "restaurant.address.pin"); // type: number
console.log(city, pin); // Pune 411001

// ❌ A typo in the path is a compile error
getIn(order, "restaurant.adress.city");
// error TS2345: Argument of type '"restaurant.adress.city"' is not assignable to parameter of type '"id" | "total" | "restaurant" | "restaurant.name" | "restaurant.address" | "restaurant.address.city" | "restaurant.address.pin"'.

// ===== 2) Arithmetic with tuples: BuildTuple, Add, tail-recursive Repeat =====
type BuildTuple<N extends number, Acc extends unknown[] = []> =
  Acc["length"] extends N ? Acc : BuildTuple<N, [...Acc, unknown]>; // grow until length === N (tail call)
type Add<A extends number, B extends number> = [...BuildTuple<A>, ...BuildTuple<B>]["length"]; // concat tuples
type Five = Add<2, 3>; // 5
const five: Five = 5; // OK
console.log(five); // 5

// ===== 3) Route params from a path string (what Express does internally) =====
type ParamNames<S extends string> =
  S extends `${string}:${infer P}/${infer Rest}` ? P | ParamNames<`/${Rest}`> // param followed by more path
  : S extends `${string}:${infer P}` ? P // last param
  : never; // no params
type RouteParams<S extends string> = { [K in ParamNames<S>]: string }; // each param is a string

function route<S extends string>(_path: S, handler: (params: RouteParams<S>) => string): (p: RouteParams<S>) => string {
  return handler; // returns the typed handler
}
const handle = route("/users/:userId/orders/:orderId", (p) => `${p.userId}/${p.orderId}`); // p is typed
console.log(handle({ userId: "u1", orderId: "o9" })); // u1/o9

// ===== 4) Key remapping: setters and getters generated from a model =====
type Accessors<T> = { [K in keyof T & string as `get${Capitalize<K>}`]: () => T[K] } & { [K in keyof T & string as `set${Capitalize<K>}`]: (v: T[K]) => void };
type CartAcc = Accessors<{ total: number; coupon: string }>; // getTotal, getCoupon, setTotal, setCoupon
const acc: CartAcc = { getTotal: () => 100, getCoupon: () => "SAVE10", setTotal: () => {}, setCoupon: () => {} }; // all four required
console.log(acc.getCoupon()); // SAVE10

// ===== 5) Tuple -> union and object from list (const type parameter, TS 5.0+) =====
function keyed<const T extends readonly string[]>(keys: T): { [K in T[number]]: K } { // const keeps literals
  return Object.fromEntries(keys.map((k) => [k, k])) as { [K in T[number]]: K }; // runtime map
}
const STATUS = keyed(["PLACED", "PAID", "DELIVERED"]); // { PLACED: "PLACED"; PAID: "PAID"; DELIVERED: "DELIVERED" }
console.log(STATUS.PAID); // PAID
```

---

## 🟠 Node/Express + React Integration

```typescript
import express from "express";

// Express already computes req.params from the route string with these exact techniques
const app = express(); // create app
app.get("/users/:userId/orders/:orderId", (req, res) => {
  const { userId, orderId } = req.params; // typed: { userId: string; orderId: string }
  res.json({ userId, orderId }); // respond
});

// Your own helper: a typed API client generated from a route table
type Routes = {
  "GET /orders/:id": { response: { id: string; total: number } }; // route 1
  "POST /orders": { response: { id: string }; body: { amount: number } }; // route 2
};
type ResponseOf<K extends keyof Routes> = Routes[K]["response"]; // pick the response type

async function api<K extends keyof Routes>(route: K, _body?: Routes[K] extends { body: infer B } ? B : never): Promise<ResponseOf<K>> {
  return { id: "o1", total: 499 } as ResponseOf<K>; // fake fetch for the demo
}
void api("GET /orders/:id").then((o) => console.log(o)); // typed as { id: string; total: number }
```

```tsx
import { useState, type ReactElement } from "react";

// Typed form field names from a model path (reused from Path<T> idea, flat version)
type Fields<T> = Extract<keyof T, string>; // string keys only
type Profile = { name: string; phone: string; email: string }; // form model

function Field<T>({ name, onChange }: { name: Fields<T>; onChange: (n: Fields<T>, v: string) => void }): ReactElement {
  return <input name={name} onChange={(e) => onChange(name, e.target.value)} />; // name is a real key
}

export function ProfileForm(): ReactElement {
  const [values, setValues] = useState<Partial<Record<Fields<Profile>, string>>>({}); // state keyed by model
  return (
    <form>
      <Field<Profile> name="phone" onChange={(n, v) => setValues({ ...values, [n]: v })} />
      <pre>{JSON.stringify(values)}</pre>
    </form>
  );
}
```

```typescript
// Redux Toolkit style: action creator map -> union of actions (mapped type + indexed access)
type Creators = { add: (sku: string) => { sku: string }; clear: () => undefined }; // action creators
type ActionUnion = { [K in keyof Creators]: { type: K; payload: ReturnType<Creators[K]> } }[keyof Creators]; // union
const a: ActionUnion = { type: "add", payload: { sku: "B1" } }; // OK
console.log(a.type); // add
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Non-tail recursion hits the depth limit
```typescript
// Wrong: the recursive call is wrapped in a tuple spread, NOT in tail position
type CountDown<N extends number, Acc extends unknown[] = []> =
  Acc["length"] extends N ? Acc : [...CountDown<N, [...Acc, unknown]>]; // wrapped -> not a tail call

type TooBig = CountDown<2000>;
// ❌ error TS2589: Type instantiation is excessively deep and possibly infinite.
```
```typescript
// Right: put the recursive call in tail position (nothing wraps it)
type CountDownOk<N extends number, Acc extends unknown[] = []> =
  Acc["length"] extends N ? Acc : CountDownOk<N, [...Acc, unknown]>; // tail call -> TS 4.5+ iterates
type Ok = CountDownOk<500>["length"]; // 500
```

❌ Mistake 2: Writing type-level code with no tests
✅ Correct: add `Expect<Equal<Actual, Expected>>` lines. A silent wrong result (`never` or `any`) otherwise ships and poisons every call site.

❌ Mistake 3: Using type tricks where a runtime value is simpler
```typescript
// Wrong: a 40-line recursive type to rebuild what a plain object already says
const ROUTES = { orders: "/orders", users: "/users" } as const; // as const keeps the literals
type RouteKey = keyof typeof ROUTES; // "orders" | "users"  (one line is enough)
type RouteValue = (typeof ROUTES)[RouteKey]; // "/orders" | "/users"
```
✅ Correct: prefer `keyof typeof`, indexed access and `as const` first; reach for recursion only when the shape is truly computed.

---

## 🧠 Tricky Interview Question

```typescript
type Mystery<T extends unknown[]> = T extends [infer H, ...infer R] ? [...Mystery<R>, H] : [];
type X = Mystery<[1, 2, 3]>;
type Y = Mystery<[]>;
type Z = Mystery<number[]>;
```
**Answer:** `Mystery` is `Reverse`. `X = [3, 2, 1]`, `Y = []`. `Z = []`: a plain array `number[]` is not assignable to the tuple pattern `[infer H, ...infer R]` (which needs at least one element), so the conditional takes the false branch and returns `[]`. Lesson: type-level list code assumes **tuples**; always test with `number[]` and `readonly` inputs.
```typescript
type Rev2<T extends unknown[]> = T extends [infer H, ...infer R] ? [...Rev2<R>, H] : [];
const z: Rev2<number[]> = [1]; // ❌
// error TS2322: Type '[number]' is not assignable to type '[]'.
//   Source has 1 element(s) but target allows only 0.
```

---

## ⚫ Interview Questions + Answers

Q1: What building blocks make TypeScript's type system Turing-complete-ish?
A1: Conditional types (branching), `infer` (pattern matching/binding), recursive type aliases (loops), tuple types with variadic spreads (data structures and counters), template literal types (string processing) and mapped types (iteration over keys). Together they can encode arithmetic, parsers, even simple interpreters (type-challenges).

Q2: Implement `Get<T, "a.b.c">`.
A2: `type Get<T, P extends string> = P extends `${infer H}.${infer R}` ? H extends keyof T ? Get<T[H], R> : never : P extends keyof T ? T[P] : never`. Split off the head at the first dot, check it is a key, recurse into `T[H]`; when no dot remains, read the last key. Pair it with `Path<T>` for autocomplete of valid paths.

Q3: How do you "add numbers" in types?
A3: Build tuples of that length with a tail-recursive `BuildTuple<N, Acc>` and concatenate: `[...BuildTuple<A>, ...BuildTuple<B>]["length"]`. TS has no numeric arithmetic in types; the tuple length is the integer representation. Limit: depth ~1000 for tail recursion.

Q4: What is the recursion limit and how do you work around it?
A4: Non-tail recursive conditional types fail around 50 levels (`TS2589`); tail-recursive ones (TS 4.5+) can iterate to about 1000. Work around by using an accumulator parameter so the recursive call is in tail position, by processing in chunks, or by moving the logic to runtime codegen.

Q5: When is type-level programming a bad idea in a team codebase?
A5: When it slows the compiler/IDE (deep recursion over big unions), produces unreadable error messages, or reimplements something the runtime schema already knows. Prefer Zod/`z.infer`, `as const`, `keyof typeof`, and keep clever types in a small, tested, documented `types/` module.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building library-grade APIs where types must follow a string/schema (routes, form paths, event names)
- Eliminating duplicate declarations (one const -> many derived types)
- Writing small, well-tested helpers (`Get`, `Path`, `Split`, `Reverse`) once and reusing them

❌ Avoid when:
- A simple union, `keyof typeof`, or `z.infer` solves it
- The type takes minutes to understand but saves seconds of typing
- It slows `tsc`/IDE or hits `TS2589`; consider simplifying or generating types in a build step

---

## 📊 Visual Diagram
```
TYPE-LEVEL PROGRAMMING = a small functional language run by the compiler

  value-level (JS)            type-level (TS)
  ─────────────────           ──────────────────────────────
  if / ternary         ◄──►   T extends U ? X : Y
  variable binding     ◄──►   infer X
  loop / recursion     ◄──►   type Rec<T> = ... Rec<Next> ...
  array                ◄──►   tuple  [A, B, C]
  array.length         ◄──►   T["length"]  (a number literal type)
  string.split         ◄──►   `${infer H}.${infer R}`
  Object.map           ◄──►   { [K in keyof T as ...]: ... }

 "restaurant.address.city"
        │  Split on "."
        ▼
 ["restaurant","address","city"] ─► walk Order ─► string
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Type-level programming | Computing types with types | types से types की computation |
| Recursive conditional type | Alias that references itself | खुद को refer करने वाला conditional type |
| Tail recursion | Recursive call in last position, no wrapping | आखिरी position में recursive call |
| Accumulator | Extra type parameter carrying partial result | partial result ले जाने वाला extra parameter |
| infer | Bind a piece of a matched type | match हुए type का हिस्सा पकड़ना |
| Type test | `Expect<Equal<A, B>>` compile-time assertion | compile-time unit test |

---

## ⚡ 3-Line Summary
English:
1. Conditional types, `infer`, recursion, tuples and template literals together form a type-level language (`Split`, `Reverse`, `Get`, `Add`).
2. Put the recursive call in tail position with an accumulator, and test every helper with `Expect<Equal<...>>`.
3. Use it to derive types from one source of truth (routes, schemas, paths), not to show off.

Hindi:
1. Conditional types, `infer`, recursion, tuples और template literals मिलकर type-level language बनाते हैं (`Split`, `Reverse`, `Get`, `Add`)।
2. Recursive call को accumulator के साथ tail position में रखो, और हर helper को `Expect<Equal<...>>` से test करो।
3. इसे एक source of truth (routes, schemas, paths) से types निकालने के लिए इस्तेमाल करो, दिखावे के लिए नहीं।

---

## ➡️ Next Topic
**61. Classes in TypeScript** — fields, constructors, methods and how `strictPropertyInitialization` protects you.
