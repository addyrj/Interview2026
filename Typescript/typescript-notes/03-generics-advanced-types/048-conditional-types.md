# 48. Conditional Types
# हिंदी में: Conditional Types (type level का if/else)

> TypeScript 5.x पर verify किया गया (`tsc --strict`, TS 5.9). Conditional types TS 2.8 से available हैं।

---

## 🔵 Simple Definition (English)
A **conditional type** picks one of two types depending on a check: `T extends U ? X : Y`. If `T` is assignable to `U` the result is `X`, otherwise `Y`. It is an if/else that runs at compile time on types. When `T` is a naked type parameter and a union is passed in, it is applied to each member separately (distribution).

## 🔵 सरल परिभाषा (Hindi)
**Conditional type** एक check के आधार पर दो types में से एक चुनता है: `T extends U ? X : Y`। अगर `T`, `U` को assign हो सकता है तो result `X`, वरना `Y`। यह compile time पर types पर चलने वाला if/else है। अगर `T` naked type parameter है और union दिया जाए, तो यह हर member पर अलग-अलग लगता है (distribution)।

---

## 🔴 Problem it Solves
A function `fetchData(raw: boolean)` returns `string` or `Parsed` depending on an option, but a plain union return forces every caller to narrow. A Redux `Payload<A>` must be `void` for "logout" actions but `CartItem` for "add". Overloads work, but do not scale to dozens of cases. Conditional types let the **output type depend on the input type** in one reusable definition.

## 🔴 यह क्यों बना? (Hindi)
`fetchData(raw: boolean)` option के आधार पर `string` या `Parsed` लौटाता है, पर simple union return से हर caller को narrow करना पड़ता है। Redux `Payload<A>` "logout" के लिए `void` और "add" के लिए `CartItem` चाहिए। Overloads चलते हैं पर दर्जनों cases में scale नहीं होते। Conditional types से **output type, input type पर निर्भर** होता है, वह भी एक reusable definition में।

---

## 🟢 How it Works — Step by Step

Step 1 → Syntax: `type IsString<T> = T extends string ? "yes" : "no"`.
Step 2 → TypeScript tests whether `T` is assignable to `string`. True gives the first branch, false the second.
Step 3 → Nest them for multiple cases: `T extends string ? A : T extends number ? B : C`.
Step 4 → Distribution: if `T` is a naked type parameter and you pass `string | number`, the check runs per member and the results are unioned. Wrap in `[T]` to stop it: `[T] extends [string] ? ...`.
Step 5 → `never` as input gives `never` for distributive conditionals (the empty union distributes to nothing).
Step 6 → Inside a generic function body, the conditional is **deferred** until T is known, so returning a value usually needs a cast.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Syntax: `type IsString<T> = T extends string ? "yes" : "no"`।
Step 2 → TypeScript जाँचता है कि `T`, `string` को assignable है या नहीं। True तो पहली branch, false तो दूसरी।
Step 3 → कई cases के लिए nest करो: `T extends string ? A : T extends number ? B : C`।
Step 4 → Distribution: `T` naked type parameter है और `string | number` दिया, तो check हर member पर चलता है और results का union बनता है। रोकना हो तो `[T]` में लपेटो: `[T] extends [string] ? ...`।
Step 5 → इनपुट `never` हो तो distributive conditional का नतीजा `never` आता है।
Step 6 → Generic function के अंदर conditional **deferred** रहता है जब तक T पता न हो, इसलिए value return करने के लिए अक्सर cast चाहिए।

---

## 🟡 Real World Example
**Swiggy's** API layer has `ApiResult<T>`. For `GET` endpoints the result is `T`; for `DELETE` endpoints the result is `void`. One type `ResultOf<M, T> = M extends "DELETE" ? void : T` removes the need for two near-identical types. Another case: a feature flag service returns `boolean` for toggles but `string` for variants; `FlagValue<K>` picks the type from the flag's kind.

## 🟡 Real Example Hindi mein
**Swiggy** की API layer में `ApiResult<T>` है। `GET` endpoints का result `T` होता है; `DELETE` का `void`। एक type `ResultOf<M, T> = M extends "DELETE" ? void : T` से दो लगभग एक जैसे types की ज़रूरत ख़त्म। दूसरा case: feature flag service toggle के लिए `boolean` और variant के लिए `string` देती है; `FlagValue<K>` flag की kind से type चुनता है।

---

## 💻 Code Example — Basic

```typescript
// Basic conditional type
type IsString<T> = T extends string ? "yes" : "no";
type A = IsString<"hi">; // "yes"
type B = IsString<42>; // "no"

// Distribution over a union: applied to each member, results are unioned
type C = IsString<string | number>; // "yes" | "no"

// Prevent distribution by wrapping both sides in a tuple
type IsStringStrict<T> = [T] extends [string] ? "yes" : "no";
type D = IsStringStrict<string | number>; // "no"

// Compile-time assertions using conditional equality helper
type Expect<T extends true> = T;
type Equal<X, Y> = (<G>() => G extends X ? 1 : 2) extends <G>() => G extends Y ? 1 : 2 ? true : false;
type _t1 = Expect<Equal<A, "yes">>; // passes
type _t2 = Expect<Equal<B, "no">>; // passes
type _t3 = Expect<Equal<C, "yes" | "no">>; // passes
type _t4 = Expect<Equal<D, "no">>; // passes

// A practical one: unwrap an array element type, or keep the type
type ElementOf<T> = T extends readonly (infer E)[] ? E : T;
const e1: ElementOf<string[]> = "x"; // string
const e2: ElementOf<number> = 5; // number
console.log(e1, e2); // x 5
```

## 💻 Code Example — Advanced

```typescript
// Advanced 1: action creators where payload presence depends on the payload type
interface Actions {
  "cart/add": { sku: string; qty: number }; // needs payload
  "cart/clear": void; // no payload
  "auth/login": { token: string }; // needs payload
}
type ActionArgs<K extends keyof Actions> = Actions[K] extends void ? [] : [payload: Actions[K]];

function dispatch<K extends keyof Actions>(type: K, ...args: ActionArgs<K>): string {
  return JSON.stringify({ type, payload: args[0] }); // serialise the action
}
console.log(dispatch("cart/clear")); // {"type":"cart/clear"}
console.log(dispatch("cart/add", { sku: "A1", qty: 2 })); // {"type":"cart/add","payload":{"sku":"A1","qty":2}}

// Advanced 2: return type depends on an option (alternative to overloads)
interface Options {
  raw?: boolean; // return raw string if true
}
type FetchResult<O extends Options> = O extends { raw: true } ? string : { total: number };

function getReport<O extends Options = {}>(opts?: O): FetchResult<O> {
  const data = { total: 1200 }; // pretend report
  return (opts?.raw ? JSON.stringify(data) : data) as FetchResult<O>; // cast because deferred
}
const r1 = getReport(); // { total: number }
const r2 = getReport({ raw: true as const }); // string
console.log(r1.total, r2.length); // 1200 14

// Advanced 3: filter union members (this is how Exclude / Extract work)
type MyExclude<T, U> = T extends U ? never : T; // distributive: removes members assignable to U
type Method = "UPI" | "CARD" | "COD";
type Online = MyExclude<Method, "COD">; // "UPI" | "CARD"
const m: Online = "UPI";
console.log(m); // UPI
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: typed response body that depends on the HTTP verb
import express from "express";

type Verb = "GET" | "POST" | "DELETE";
type Body<V extends Verb, T> = V extends "DELETE" ? { deleted: true } : V extends "POST" ? { created: T } : T;

interface Product {
  id: number; // id
  name: string; // name
}

function handler<V extends Verb>(verb: V, p: Product): Body<V, Product> {
  if (verb === "DELETE") return { deleted: true } as Body<V, Product>; // cast: deferred
  if (verb === "POST") return { created: p } as Body<V, Product>;
  return p as Body<V, Product>;
}

const app = express();
app.get("/p/1", (_q, res) => { res.json(handler("GET", { id: 1, name: "Tea" })); }); // Product
app.delete("/p/1", (_q, res) => { res.json(handler("DELETE", { id: 1, name: "Tea" })); }); // { deleted: true }
```

```tsx
// React: props that change based on a variant (conditional props)
type ButtonProps<V extends "link" | "action"> = V extends "link"
  ? { variant: V; href: string } // link needs href
  : { variant: V; onClick: () => void }; // action needs onClick

function Btn<V extends "link" | "action">(props: ButtonProps<V>) {
  if (props.variant === "link") {
    return <a href={(props as ButtonProps<"link">).href}>go</a>; // narrow by cast
  }
  return <button onClick={(props as ButtonProps<"action">).onClick}>do</button>;
}

export const Demo = () => (
  <>
    <Btn variant="link" href="/cart" />
    <Btn variant="action" onClick={() => console.log("clicked")} />
  </>
);
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting distribution and getting a union
```typescript
type ToArray<T> = T extends unknown ? T[] : never;
type X = ToArray<string | number>; // string[] | number[]  (NOT (string | number)[])
// To get (string | number)[] use [T] extends [unknown] ? T[] : never
```

❌ Mistake 2: Returning a concrete value inside a generic function
```typescript
// ❌ Wrong
type Out<T> = T extends string ? number : boolean;
function f<T>(x: T): Out<T> {
  return 1;
}
// error TS2322: Type '1' is not assignable to type 'Out<T>'.

// ✅ Right: accept the cast (conditional is deferred) or use overloads
function g<T>(x: T): Out<T> {
  return 1 as Out<T>;
}
```

❌ Mistake 3: Checking with `extends` the wrong direction
```typescript
type IsNever<T> = T extends never ? true : false;
type N = IsNever<never>; // never, not true! (distributes over empty union)
type IsNeverOk<T> = [T] extends [never] ? true : false; // true
```

---

## 🧠 Tricky Interview Question

```typescript
type IsAny<T> = 0 extends 1 & T ? true : false;
type T1 = IsAny<any>;
type T2 = IsAny<unknown>;
type T3 = IsAny<never>;
```
**What are `T1`, `T2`, `T3`?**

Answer: `T1 = true`, `T2 = false`, `T3 = false`. `1 & any` is `any`, and `0 extends any` is true. For `unknown`, `1 & unknown` is `1`, and `0` does not extend `1`. For `never`, `1 & never` is `never`; since `T` is not the checked (naked) type here (the checked type is `0`) distribution does not apply, so the answer is false. This trick is a classic for detecting `any`.

---

## ⚫ Interview Questions + Answers

Q1: What is a conditional type?
A1: `T extends U ? X : Y`, a type-level ternary. It resolves to `X` if T is assignable to U, else `Y`. Used by `Exclude`, `Extract`, `NonNullable`, `ReturnType`, `Awaited`.

Q2: What is a distributive conditional type?
A2: When the checked type is a naked type parameter and a union is supplied, TypeScript applies the condition to each union member and unions the results. `Exclude<"a"|"b", "a">` gives `"b"` because of this. Wrap in `[T]` to disable.

Q3: Why does `IsNever<never>` return `never`?
A3: `never` is an empty union, so distribution produces an empty union of results. Use `[T] extends [never]`.

Q4: Why do I need `as` casts when returning conditional types from generic functions?
A4: Inside the body T is unknown, so the compiler cannot decide which branch applies; the conditional stays deferred and no concrete value is assignable to it. Options: cast, overloads, or restructure with a lookup map type (`Map[K]`) which is easier for the compiler.

Q5: When prefer a lookup type over a conditional type?
A5: When the mapping is a fixed set of keys. `interface Actions { "cart/add": X }` plus `Actions[K]` is faster and more readable than a nested chain of `extends ? :`. Conditionals are for structural tests (is it a function, array, Promise?).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Output type depends on an input type (payload present or void, array unwrap)
- Filtering unions (`Exclude`-like), detecting shapes (function, array, Promise)
- Building utility types combined with `infer`

❌ Avoid when:
- A lookup interface or overloads express the same thing more simply
- You need to return concrete values inside the generic body (casts spread everywhere)
- Chains grow long; compile time and error messages suffer

---

## 📊 Visual Diagram
```
   T extends U ? X : Y

        ┌─────────────┐   yes   ┌─────┐
   T ──►│ T assignable│────────►│  X  │
        │   to U ?    │   no    ├─────┤
        └─────────────┘────────►│  Y  │
                                └─────┘

   Distribution (naked T, union input):
   IsString<string | number>
      = IsString<string> | IsString<number>
      = "yes" | "no"
   [T] extends [..]  ──►  no distribution
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Conditional type | `T extends U ? X : Y` | Type level if/else |
| Distributive | Applied per union member | Union के हर member पर |
| Naked type parameter | `T` not wrapped in `[]`/object | बिना लपेटा type parameter |
| Deferred | Unresolved until T known | T पता होने तक रुका हुआ |
| Assignable | Value of one fits other | एक type दूसरे में fit |

---

## ⚡ 3-Line Summary
English:
1. `T extends U ? X : Y` chooses a type at compile time based on assignability.
2. Naked type parameters distribute over unions; wrap in `[T]` to stop it (and to handle `never`).
3. Inside generic bodies conditionals are deferred, so use casts, overloads or lookup maps.

Hindi:
1. `T extends U ? X : Y` assignability के आधार पर compile time पर type चुनता है।
2. Naked type parameters unions पर distribute होते हैं; रोकने (और `never` handle करने) के लिए `[T]` में लपेटो।
3. Generic body के अंदर conditionals deferred रहते हैं, इसलिए cast, overloads या lookup maps इस्तेमाल करो।

---

## ➡️ Next Topic
**49. infer Keyword** — conditional type के अंदर type को "पकड़ना" (extract) जैसे `ReturnType`, `Awaited`।
