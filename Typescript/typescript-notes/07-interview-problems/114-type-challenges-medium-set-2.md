# 114. Type-challenges: Medium Set 2
# हिंदी में: Type-challenges: Medium Set 2 (और type-level पहेलियाँ)

> TypeScript 5.x | हर block `tsc --strict` (TS 5.9) से verify हुआ। Key remapping `as` = **TS 4.1+**; template literal intrinsics (`Capitalize`, `Uncapitalize`) = 4.1+; `[T] extends [never]` trick हर version पर चलता है। पिछला set: note 113।

---

## 🔵 Simple Definition (English)
Set 2 moves from "extract and filter" to **combinatorics and string/object manipulation**: `Permutation`, `LengthOfString`, `Flatten`, `StringToUnion`, `AnyOf`, `IsNever`, `IsUnion`, `KebabCase`/`CamelCase`, `Diff`, `Merge`, `AppendToObject`, `Absolute` and a `Chainable` options builder. These test one idea above all: **distribution**: how a conditional type behaves when its checked type is a naked union or `never`.

## 🔵 सरल परिभाषा (Hindi)
Set 2 में "निकालना और filter करना" से आगे बढ़कर **combinations और string/object manipulation** आता है: `Permutation`, `LengthOfString`, `Flatten`, `StringToUnion`, `AnyOf`, `IsNever`, `IsUnion`, `KebabCase`/`CamelCase`, `Diff`, `Merge`, `AppendToObject`, `Absolute` और `Chainable` options builder। इन सबमें सबसे बड़ा विचार है **distribution**: जब conditional type का checked type कोई नंगी (naked) union या `never` हो तो वह कैसे behave करता है।

---

## 🔴 Problem it Solves
Real codebases hit these exact problems: SQL Server returns `snake_case` columns but your React app wants `camelCase` (`CamelKeys`); a PATCH payload must differ from the DB row (`Diff`, `Merge`); a query builder should accumulate options in its type (`Chainable`); a feature flag helper must answer "is any flag on?" (`AnyOf`). Interviewers use set-2 puzzles to check you know the sharp edges: `never` is the empty union, so naive conditionals on it return `never`; unions distribute; `readonly` tuples are not assignable to mutable ones.

## 🔴 यह क्यों बना? (Hindi)
Real codebases में यही समस्याएँ आती हैं: SQL Server `snake_case` columns देता है पर React को `camelCase` चाहिए (`CamelKeys`); PATCH payload DB row से अलग होता है (`Diff`, `Merge`); query builder को options type में जमा करने चाहिए (`Chainable`); feature-flag helper को जवाब देना है "कोई flag on है?" (`AnyOf`)। Interviewer set-2 से जाँचते हैं कि आप तीखे किनारे जानते हैं या नहीं: `never` खाली union है इसलिए उस पर naive conditional `never` लौटाता है; unions distribute होते हैं; `readonly` tuples mutable में assign नहीं होते।

---

## 🟢 How it Works — Step by Step
Step 1 → **Distribution rule**: `T extends U ? X : Y` with a *naked* `T` runs once per union member. Wrap in `[T] extends [U]` to turn it off.
Step 2 → `never` is the empty union: distributing over it gives `never` (no members to process). Always handle it with the `[T]` trick (`IsNever`).
Step 3 → **Recursion on tuples/strings**: peel one head with `infer H` and recurse on `infer R`, accumulating into a tuple (`StringToTuple` -> `['length']`).
Step 4 → **Combinatorics**: `Permutation<T, All = T>` uses the second type parameter as a *frozen copy* of the full union, while `T` distributes one member at a time.
Step 5 → **Object shaping**: build from `keyof A | keyof B` and decide per key which side wins (`Merge`), or use `as` to rename keys (`CamelKeys`).
Step 6 → Always add the `Expect<Equal<...>>` tests including `[]`, `never`, and single-member inputs.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Distribution का नियम**: `T extends U ? X : Y` में अगर `T` *नंगा* है तो union के हर member पर एक बार चलता है। `[T] extends [U]` में लपेटो तो बंद हो जाता है।
Step 2 → `never` खाली union है: उस पर distribute करो तो नतीजा `never` (process करने को कोई member ही नहीं)। इसे `[T]` trick से संभालो (`IsNever`)।
Step 3 → **Tuples/strings पर recursion**: `infer H` से सिर छीलो, `infer R` पर recursion, और नतीजे को tuple में जमा करो (`StringToTuple` -> `['length']`)।
Step 4 → **Combinatorics**: `Permutation<T, All = T>` में दूसरा type parameter पूरी union की *जमी हुई कॉपी* है, और `T` एक-एक member पर distribute होता है।
Step 5 → **Object बनाना**: `keyof A | keyof B` से बनाओ और हर key पर तय करो कि कौन-सा side जीतेगा (`Merge`), या `as` से key का नाम बदलो (`CamelKeys`)।
Step 6 → हमेशा `Expect<Equal<...>>` tests लिखो, जिनमें `[]`, `never` और एक-member input भी हों।

---

## 🟡 Real World Example
**Flipkart's order service** reads rows from SQL Server: `order_id`, `user_name`, `total_paise`. A single `CamelKeys<OrderRow>` type produces the exact DTO the React app consumes, and a tiny runtime `camelize()` produces the matching object. Add a column `coupon_code` to `OrderRow` and the DTO gains `couponCode` automatically; no second interface to forget.

## 🟡 Real Example Hindi mein
**Flipkart की order service** SQL Server से rows पढ़ती है: `order_id`, `user_name`, `total_paise`। एक `CamelKeys<OrderRow>` type ठीक वही DTO बनाता है जो React app लेता है, और छोटा runtime `camelize()` उससे मेल खाता object बनाता है। `OrderRow` में `coupon_code` column जोड़ो और DTO में `couponCode` अपने आप आ जाता है; दूसरा interface भूलने का सवाल ही नहीं।

---

## 💻 Code Example — Basic

Logic puzzles: `IsNever`, `IsUnion`, `Permutation`, `LengthOfString`, `Flatten`, `StringToUnion`, `AnyOf`. Compiling = all tests pass.

```typescript
type Equal<X, Y> = (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;

// 1) IsNever: [T] se wrap karo, warna never distribute hoke 'never' hi deta hai
type IsNever<T> = [T] extends [never] ? true : false;

// 2) IsUnion: T ko dobara distribute karke compare karo
type IsUnion<T, U = T> = [T] extends [never] ? false : T extends U ? ([U] extends [T] ? false : true) : never;

// 3) Permutation: union ke saare orderings (tuple)
type Permutation<T, All = T> = [T] extends [never] ? [] : T extends All ? [T, ...Permutation<Exclude<All, T>>] : never;

// 4) LengthOfString: string ko tuple me tod ke length lo
type StringToTuple<S extends string> = S extends `${infer H}${infer R}` ? [H, ...StringToTuple<R>] : [];
type LengthOfString<S extends string> = StringToTuple<S>['length'];

// 5) Flatten: nested tuple ko ek level se poora flat karo
type Flatten<T extends unknown[]> = T extends [infer H, ...infer R]
  ? H extends unknown[] ? [...Flatten<H>, ...Flatten<R>] : [H, ...Flatten<R>]
  : [];

// 6) StringToUnion
type StringToUnion<S extends string> = S extends `${infer H}${infer R}` ? H | StringToUnion<R> : never;

// 7) AnyOf: koi bhi truthy element ho to true
type Falsy = 0 | '' | false | [] | { [k: string]: never } | null | undefined;
type AnyOf<T extends readonly unknown[]> = T extends [infer H, ...infer R] ? ([H] extends [Falsy] ? AnyOf<R> : true) : false;

type Cases = [
  Expect<Equal<IsNever<never>, true>>,
  Expect<Equal<IsNever<string>, false>>,
  Expect<Equal<IsUnion<'a' | 'b'>, true>>,
  Expect<Equal<IsUnion<string>, false>>,
  Expect<Equal<IsUnion<never>, false>>,
  Expect<Equal<Permutation<'A' | 'B'>, ['A', 'B'] | ['B', 'A']>>,
  Expect<Equal<LengthOfString<'Swiggy'>, 6>>,
  Expect<Equal<Flatten<[1, [2, [3, 4]], [[[5]]]]>, [1, 2, 3, 4, 5]>>,
  Expect<Equal<StringToUnion<'abc'>, 'a' | 'b' | 'c'>>,
  Expect<Equal<AnyOf<[0, '', false, [], {}]>, false>>,
  Expect<Equal<AnyOf<[0, 'paid']>, true>>,
];
export type { Cases };
```

## 💻 Code Example — Advanced

Object and string puzzles: `KebabCase`, `CamelCase`, `CamelKeys`, `Diff`, `Merge`, `AppendToObject`, `Absolute`, `Chainable`.

```typescript
type Equal<X, Y> = (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;

// 8) KebabCase / CamelCase: API field names badalna (SQL Server snake_case <-> JSON camelCase)
type KebabCase<S extends string> = S extends `${infer H}${infer R}`
  ? R extends Uncapitalize<R> ? `${Lowercase<H>}${KebabCase<R>}` : `${Lowercase<H>}-${KebabCase<R>}`
  : S;
type CamelCase<S extends string> = S extends `${infer H}_${infer R}` ? `${Lowercase<H>}${Capitalize<CamelCase<R>>}` : Lowercase<S>;

// 9) Diff: dono object me jo keys alag hain unka object
type Diff<A, B> = Omit<A & B, keyof A & keyof B>;

// 10) Merge: second object ki keys first ko override karti hain
type Merge<F, S> = { [K in keyof F | keyof S]: K extends keyof S ? S[K] : K extends keyof F ? F[K] : never };

// 11) AppendToObject
type AppendToObject<T, K extends PropertyKey, V> = { [P in keyof T | K]: P extends keyof T ? T[P] : V };

// 12) Absolute: number/string/bigint -> string without '-'
type Absolute<T extends number | string | bigint> = `${T}` extends `-${infer N}` ? N : `${T}`;

// 13) Chainable: .option('k', v) se type jama hota hai, .get() me pura result
type Chainable<R = {}> = {
  option<K extends string, V>(key: K extends keyof R ? never : K, value: V): Chainable<Omit<R, K> & Record<K, V>>;
  get(): R;
};

// 14) MapKeys: snake_case DB row -> camelCase DTO (CamelCase + key remap)
type CamelKeys<T> = { [K in keyof T as K extends string ? CamelCase<K> : K]: T[K] };

interface OrderRow { order_id: number; user_name: string; total_paise: number }
type OrderDto = CamelKeys<OrderRow>;

type Cases = [
  Expect<Equal<KebabCase<'FooBarBaz'>, 'foo-bar-baz'>>,
  Expect<Equal<CamelCase<'order_id'>, 'orderId'>>,
  Expect<Equal<OrderDto, { orderId: number; userName: string; totalPaise: number }>>,
  Expect<Equal<Diff<{ a: 1; b: 2 }, { b: 2; c: 3 }>, { a: 1; c: 3 }>>,
  Expect<Equal<Merge<{ a: number; b: string }, { b: boolean; c: 1 }>, { a: number; b: boolean; c: 1 }>>,
  Expect<Equal<AppendToObject<{ id: 1 }, 'paid', true>, { id: 1; paid: true }>>,
  Expect<Equal<Absolute<-42>, '42'>>,
  Expect<Equal<Absolute<'-0'>, '0'>>,
];

declare const q: Chainable;
const built = q.option('table', 'orders').option('limit', 10).option('desc', true).get();
const limit: number = built.limit; // limit ka type number
export type { Cases };
export { built, limit };
```

---

## 🟠 Node/Express + React Integration

**Express**: SQL Server rows to camelCase DTO with a type that matches the runtime function (run with `npx tsx`).

```typescript
import express from 'express';

type CamelCase<S extends string> = S extends `${infer H}_${infer R}` ? `${Lowercase<H>}${Capitalize<CamelCase<R>>}` : Lowercase<S>;
type CamelKeys<T> = { [K in keyof T as K extends string ? CamelCase<K> : K]: T[K] };

// SQL Server se aayi row (snake_case columns)
interface OrderRow { order_id: number; user_name: string; total_paise: number }

// runtime function jiska return type compile-time mapping se match karta hai
function camelize<T extends object>(row: T): CamelKeys<T> {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(row)) {
    const key = k.toLowerCase().replace(/_([a-z])/g, (_, c: string) => c.toUpperCase());
    out[key] = v;
  }
  return out as CamelKeys<T>; // ek jagah cast, baaki sab type-safe
}

const row: OrderRow = { order_id: 7, user_name: 'Aditya', total_paise: 49900 };
const dto = camelize(row); // { orderId: number; userName: string; totalPaise: number }
console.log(dto.orderId, dto.userName, dto.totalPaise);

const app = express();
app.get('/orders/:orderId', (_req, res) => {
  res.json(camelize(row)); // frontend ko hamesha camelCase milega
});
export default app;
// OUTPUT:
// 7 Aditya 49900
```

**React**: consuming the DTO, with `Diff` to model "form-only" fields.

```tsx
import { useEffect, useState } from 'react';

type CamelCase<S extends string> = S extends `${infer H}_${infer R}` ? `${Lowercase<H>}${Capitalize<CamelCase<R>>}` : Lowercase<S>;
type CamelKeys<T> = { [K in keyof T as K extends string ? CamelCase<K> : K]: T[K] };
type Diff<A, B> = Omit<A & B, keyof A & keyof B>;

interface OrderRow { order_id: number; user_name: string; total_paise: number }
type OrderDto = CamelKeys<OrderRow>;
type FormOnly = Diff<OrderDto, { orderId: number; userName: string; totalPaise: number; couponCode: string }>;
// FormOnly = { couponCode: string }: server DTO me nahi, sirf form me

function OrderSummary({ id }: { id: number }) {
  const [order, setOrder] = useState<OrderDto | null>(null); // camelCase DTO
  useEffect(() => {
    fetch(`/orders/${id}`).then((r) => r.json() as Promise<OrderDto>).then(setOrder);
  }, [id]);
  const extra: FormOnly = { couponCode: 'NEW50' };
  return order ? <p>{order.userName} paid {order.totalPaise / 100} ({extra.couponCode})</p> : null;
}
export { OrderSummary };
```

**Redux note**: keep Redux state in the camelCase DTO shape (`OrderDto`), converting once in the thunk/RTK Query `transformResponse`, never in components.
**Hindi**: Redux state हमेशा camelCase DTO में रखो; conversion एक बार thunk/`transformResponse` में, components में नहीं।

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: naive `IsNever`, duplicate key in a chain, wrong flatten answer.

```typescript
type IsNever<T> = T extends never ? true : false; // ❌ naive version
type R = IsNever<never>;
const r: R = true; // never, kyunki distribute hoke kuch bacha hi nahi
type Chainable<R = {}> = {
  option<K extends string, V>(key: K extends keyof R ? never : K, value: V): Chainable<Omit<R, K> & Record<K, V>>;
  get(): R;
};
declare const q: Chainable;
q.option('table', 'orders').option('table', 'users'); // ❌ duplicate key
type Flatten<T extends unknown[]> = T extends [infer H, ...infer R] ? H extends unknown[] ? [...Flatten<H>, ...Flatten<R>] : [H, ...Flatten<R>] : [];
const f: Flatten<[1, [2]]> = [1, 3]; // ❌ galat value
// error TS2322: Type 'true' is not assignable to type 'never'.
// error TS2345: Argument of type '"table"' is not assignable to parameter of type 'never'.
// error TS2322: Type '3' is not assignable to type '2'.
// Right: IsNever = [T] extends [never] ? true : false
```

❌ Mistake 2 (no compiler error): using `Omit<A & B, keyof A & keyof B>` for `Diff` and expecting it to *preserve unions of objects*. `Omit` is not distributive; it collapses union members. For union inputs write your own distributive helper (`T extends unknown ? Omit<T, K> : never`).
✅ Hindi: `Omit` union पर distribute नहीं होता; union objects के लिए अपना distributive helper लिखो।

---

## 🧠 Tricky Interview Question

**"`type IsNever<T> = T extends never ? true : false` looks right. What does `IsNever<never>` return, and why?"**

```typescript
type Equal<X, Y> = (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;

type NaiveIsNever<T> = T extends never ? true : false; // T 'naked' hai -> distribute hota hai
type SafeIsNever<T> = [T] extends [never] ? true : false; // tuple me wrap -> distribute band

type Proof = [
  Expect<Equal<NaiveIsNever<never>, never>>, // never ke saath 0 members, to result bhi never
  Expect<Equal<SafeIsNever<never>, true>>, // wrapped version sahi true deta hai
  Expect<Equal<NaiveIsNever<string>, false>>,
];
export type { Proof };
```

Answer: `never`, not `true`. `T` is a naked type parameter, so the conditional is distributive; `never` is the union with **zero members**, so there is nothing to map over and the whole result is the empty union `never`. Wrapping both sides in tuples, `[T] extends [never]`, stops distribution: `[never]` is a normal one-element tuple type and is assignable to `[never]`. The same trick is why `IsUnion` starts with `[T] extends [never] ? false : ...`. Hindi: `never` में 0 members हैं, इसलिए distribute करने पर कुछ बचता ही नहीं; `[T]` से लपेटकर distribution बंद करो।

---

## ⚫ Interview Questions + Answers

Q1: How does `Permutation<'A' | 'B' | 'C'>` produce all six orderings?
A1: `T extends All` distributes `T` one member at a time while `All` stays the full union. For each `T` it builds `[T, ...Permutation<Exclude<All, T>>]`, recursing on the remaining members, and the final union of tuples is every ordering. Base case `[T] extends [never] ? []`.

Q2: Why compute `LengthOfString` through a tuple?
A2: The type system has no string-length operator. Turn the string into a tuple of characters (`StringToTuple`), then read `['length']`, which is a numeric literal. Limit: recursion depth, so very long strings fail.

Q3: What does `Chainable` teach?
A3: Each `.option(k, v)` returns a *new* `Chainable` whose type accumulates `Record<K, V>`; `K extends keyof R ? never : K` makes duplicate keys a compile error; `.get()` returns the accumulated object. The same idea as a typed query/DTO builder.

Q4: `Merge` vs intersection `A & B`: what is different?
A4: With `{ b: string } & { b: boolean }` the property `b` becomes `string & boolean` = `never`. `Merge` picks the second object's type for shared keys, mimicking `{ ...a, ...b }` at runtime.

Q5: Why can `CamelKeys` use `as` but `Diff` uses `Omit`?
A5: `as` remapping changes *key names* while keeping value types (`order_id` -> `orderId`). `Diff` only needs to *drop* keys, and `Omit` (itself a `Pick` + `Exclude`) does exactly that. Use whichever expresses intent most simply.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You convert between layers (DB `snake_case`, API `camelCase`) and want one source of truth.
- Building small typed DSLs: query builders, feature-flag helpers, route tables.
- Writing compile-time tests for type-heavy libraries.

❌ Avoid when:
- A simple interface does the job; clever types hurt readability.
- Recursion depth is unbounded (long strings, huge tuples): hits "Type instantiation is excessively deep".
- A codegen tool (OpenAPI, Prisma, kysely-codegen) already produces the types for you.

---

## 📊 Visual Diagram
```
DISTRIBUTION CHEAT-SHEET
  T extends U ? X : Y          (T naked)         ->  runs per member
     T = 'a' | 'b'   =>  (X|Y for 'a') | (X|Y for 'b')
     T = never       =>  never                  (no members!)

  [T] extends [U] ? X : Y      (T wrapped)       ->  runs once on whole T
     T = 'a' | 'b'   =>  one check on the union
     T = never       =>  works: [never] extends [never] = true

Permutation<'A'|'B'>:
   T='A' -> ['A', ...Permutation<'B'>] -> ['A','B']
   T='B' -> ['B', ...Permutation<'A'>] -> ['B','A']
   result: ['A','B'] | ['B','A']
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Naked type parameter | `T` alone on the left of `extends` | `extends` के बाएँ अकेला `T` |
| Distribution | Conditional runs per union member | हर union member पर अलग चलना |
| `never` | Empty union, no values | खाली union, कोई value नहीं |
| `[T] extends [U]` | Non-distributive check | Distribution बंद करने वाली जाँच |
| Key remapping (`as`) | Rename/drop keys in mapped type | Mapped type में key बदलना/हटाना |
| Permutation | All orderings of elements | तत्वों के सारे क्रम |

---

## ⚡ 3-Line Summary
English:
1. Set 2 is about distribution: naked `T` distributes over unions and returns `never` for `never`; wrap in `[T]` to stop it.
2. Strings and tuples are processed by peeling `infer H` and recursing; `['length']` gives numeric results.
3. Object puzzles use `keyof A | keyof B`, `as` remapping and `Omit`; `CamelKeys` is the real-world payoff for SQL Server rows.

Hindi:
1. Set 2 distribution के बारे में है: नंगा `T` unions पर distribute होता है और `never` पर `never` लौटाता है; `[T]` से रोको।
2. Strings और tuples को `infer H` से छीलकर recursion से process करो; `['length']` से numeric नतीजा मिलता है।
3. Object puzzles में `keyof A | keyof B`, `as` remapping और `Omit` चलते हैं; SQL Server rows के लिए `CamelKeys` असली फायदा है।

---

## ➡️ Next Topic
**115. TypeScript Interview Classics — 30 Most Asked Questions** — पूरे course का revision: 30 सबसे ज़्यादा पूछे जाने वाले सवाल, छोटे जवाबों और verified code के साथ।
