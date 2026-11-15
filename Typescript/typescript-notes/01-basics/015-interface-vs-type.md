# 15. interface vs type — When to Use Which
# हिंदी में: interface बनाम type — कब कौन सा?

> TypeScript 5.x | This is one of the most asked TypeScript interview questions

---

## 🔵 Simple Definition (English)
Both `interface` and `type` can describe the shape of an object, and for plain objects they are almost interchangeable. The real differences are: (1) `type` can name ANY type (unions, tuples, primitives, conditional and mapped types), an `interface` only object shapes; (2) `interface` supports **declaration merging**, `type` does not; (3) `interface` uses `extends`, `type` uses `&` (intersection); (4) `interface` has no implicit index signature, so it is not assignable to `Record<string, unknown>`, while an object `type` alias is. A good default: use `interface` for public object contracts and class shapes, use `type` for everything else.

## 🔵 सरल परिभाषा (Hindi)
`interface` और `type` दोनों object की shape बता सकते हैं और सादे objects के लिए लगभग एक जैसे हैं। असली फ़र्क ये हैं: (1) `type` **कोई भी** type (unions, tuples, primitives, conditional और mapped types) को नाम दे सकता है, `interface` सिर्फ़ object shapes को; (2) `interface` **declaration merging** support करता है, `type` नहीं; (3) `interface` `extends` इस्तेमाल करता है, `type` `&` (intersection); (4) `interface` में implicit index signature नहीं होती, इसलिए वह `Record<string, unknown>` में assignable नहीं, जबकि object `type` alias होता है। अच्छा default: public object contracts और class shapes के लिए `interface`, बाकी सब के लिए `type`।

---

## 🔴 Problem it Solves
Teams argue endlessly ("interface everywhere" vs "type everywhere") and code reviews waste time. Worse, picking wrongly causes real bugs: a library type declared with `type` cannot be augmented by consumers; an `interface` cannot represent `'a' | 'b'`; two files that both declare `interface Config` silently merge into one when you wanted two. Knowing the exact semantic differences lets you choose by reason, and answer the interview question precisely instead of saying "they are mostly the same".

## 🔴 यह क्यों बना? (Hindi)
Teams में अंतहीन बहस होती है ("हर जगह interface" बनाम "हर जगह type") और code review में समय जाता है। उससे बुरा, गलत चुनाव असली bugs देता है: `type` से declare की गई library type को consumers augment नहीं कर सकते; `interface` से `'a' | 'b'` नहीं बन सकता; दो files में `interface Config` चुपचाप एक में merge हो जाते हैं जबकि आपको दो चाहिए थे। सटीक semantic फ़र्क पता हों तो आप कारण के साथ चुनते हैं और interview में "ये लगभग एक जैसे हैं" की जगह सही जवाब देते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → For a simple object both work: `interface A { x: number }` and `type A = { x: number }` accept the same values.
Step 2 → Extension syntax differs: `interface B extends A { y: string }` versus `type B = A & { y: string }`. Interface `extends` reports conflicts immediately (TS2430); an intersection silently produces `never` for conflicting members.
Step 3 → Merging: repeat `interface A` and members combine; repeat `type A` and you get TS2300 duplicate identifier.
Step 4 → Expressiveness: only `type` can do `type S = 'a' | 'b'`, `type T = [number, string]`, `type F<T> = T extends string ? 1 : 2`, `type M = { [K in Keys]: ... }`.
Step 5 → Index signature compatibility: an object `type` literal is assignable to `Record<string, unknown>`; an `interface` is not (TS2322 "Index signature for type 'string' is missing").
Step 6 → Classes can `implements` either, as long as it is an object type (not a union).
Step 7 → Performance: the compiler caches interface relationships by name, so large `extends` chains are usually cheaper than long chains of intersections.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → सादे object के लिए दोनों चलते हैं: `interface A { x: number }` और `type A = { x: number }` वही values accept करते हैं।
Step 2 → Extension syntax अलग है: `interface B extends A { y: string }` बनाम `type B = A & { y: string }`। Interface `extends` conflict तुरंत बताता है (TS2430); intersection conflicting members को चुपचाप `never` बना देता है।
Step 3 → Merging: `interface A` दोहराओ तो members जुड़ जाते हैं; `type A` दोहराओ तो TS2300 duplicate identifier।
Step 4 → Expressiveness: सिर्फ़ `type` से `type S = 'a' | 'b'`, `type T = [number, string]`, `type F<T> = T extends string ? 1 : 2`, `type M = { [K in Keys]: ... }` बन सकते हैं।
Step 5 → Index signature compatibility: object `type` literal `Record<string, unknown>` में assignable है; `interface` नहीं (TS2322 "Index signature for type 'string' is missing")।
Step 6 → Classes दोनों को `implements` कर सकती हैं, बस वह object type हो (union नहीं)।
Step 7 → Performance: compiler interface relationships को नाम से cache करता है, इसलिए लंबी `extends` chains आमतौर पर लंबी intersection chains से सस्ती हैं।

---

## 🟡 Real World Example
At a fintech like **Razorpay**, the SDK team ships `interface RazorpayOptions` so that merchants can add plugin-specific fields through declaration merging, and `interface Customer` for class-implementable contracts. The same codebase uses `type PaymentMethod = 'upi' | 'card'` and `type Result<T> = { ok: true; data: T } | { ok: false; error: string }` because only `type` can express unions. A reviewer who knows the difference can justify each choice in one sentence.

## 🟡 Real Example Hindi mein
**Razorpay** जैसी fintech में SDK team `interface RazorpayOptions` देती है ताकि merchants declaration merging से plugin-specific fields जोड़ सकें, और class-implementable contracts के लिए `interface Customer`। उसी codebase में `type PaymentMethod = 'upi' | 'card'` और `type Result<T> = { ok: true; data: T } | { ok: false; error: string }` हैं क्योंकि union सिर्फ़ `type` बना सकता है। जो reviewer फ़र्क जानता है वह हर चुनाव एक वाक्य में justify कर सकता है।

---

## 💻 Code Example — Basic

```typescript
// vs-basic.ts  (TypeScript 5.x, strict)

// ---- Same thing, two spellings ----
interface IProduct { id: number; name: string }     // interface form
type TProduct = { id: number; name: string };       // type alias form

const p1: IProduct = { id: 1, name: 'Biryani' };    // both accept the same value
const p2: TProduct = p1;                            // and they are mutually assignable

// ---- Extending ----
interface IFood extends IProduct { veg: boolean }   // interface: extends
type TFood = TProduct & { veg: boolean };           // type: intersection

const f1: IFood = { id: 2, name: 'Paneer', veg: true };
const f2: TFood = f1;                               // still assignable: same shape

// ---- Only type can do these ----
type PaymentMethod = 'upi' | 'card';                // union
type Pair = [id: number, qty: number];              // tuple
type Id = string;                                   // primitive alias

// ---- Only interface can merge ----
interface Config { apiUrl: string }
interface Config { retries: number }                // merges with the one above
const cfg: Config = { apiUrl: '/api', retries: 3 }; // must satisfy BOTH

const m: PaymentMethod = 'upi';
const pair: Pair = [1, 2];
const id: Id = 'x';
console.log(p2.name, f2.veg, cfg.retries, m, pair, id);
```

Run with `npx tsx vs-basic.ts`. Real output:
```
Biryani true 3 upi [ 1, 2 ] x
```

## 💻 Code Example — Advanced

```typescript
// vs-advanced.ts  (TypeScript 5.x)

// 1. Implicit index signature: object `type` literals pass, interfaces fail
interface IUser { id: number }
type TUser = { id: number };
const iu: IUser = { id: 1 };
const tu: TUser = { id: 2 };
const ok: Record<string, unknown> = tu;      // ok: type alias gets an implicit index signature
// const bad: Record<string, unknown> = iu;  // see "Common Mistakes" for the TS2322 error
console.log(iu.id);                          // keep iu used

// 2. interface extends reports conflicts; intersection hides them
interface Base { status: string }
type Hidden = Base & { status: number };     // no error here...
type Check = Hidden['status'];               // ...but status is string & number = never
const neverUsed: Check[] = [];               // an array of never can only be empty

// 3. Declaration merging in practice: augmenting a shape from another file
interface AppEnv { NODE_ENV: 'development' | 'production' }
interface AppEnv { DATABASE_URL: string }    // e.g. added by a plugin file
const env: AppEnv = { NODE_ENV: 'production', DATABASE_URL: 'mssql://db' };

// 4. Interfaces are lazily evaluated: mutually recursive shapes read naturally
interface Category { name: string; products: Product[] }
interface Product { name: string; category: Category }

// 5. type is needed for unions, even when each member is an interface
interface Card { kind: 'card'; last4: string }
interface Upi { kind: 'upi'; vpa: string }
type Payment = Card | Upi;                   // a union of two interfaces

function describe(p: Payment): string {
  return p.kind === 'card' ? `card ****${p.last4}` : `upi ${p.vpa}`; // narrowing by literal tag
}

// 6. Class can implement an object type alias too
type Logger = { log(msg: string): void };
class ConsoleLogger implements Logger {
  log(msg: string): void { console.log(msg); }
}

new ConsoleLogger().log(describe({ kind: 'upi', vpa: 'a@upi' }));
console.log(Object.keys(ok).length, env.DATABASE_URL, neverUsed.length);
```

Run with `npx tsx vs-advanced.ts`. Real output:
```
1
upi a@upi
1 mssql://db 0
```

---

## 🟠 Node/Express + React Integration

```tsx
// A practical convention used in many Node + React codebases:
//   interface -> props, API contracts, class shapes, things others may extend
//   type      -> unions, utility compositions, action types, function types

// ---------- shared/types.ts ----------
export interface Order { id: number; total: number }       // DTO: interface
export type OrderStatus = 'placed' | 'delivered';            // union: must be type
export type ApiResult<T> = { data: T } | { error: string };  // union generic: type

// ---------- server (Express) ----------
import express from 'express';
import type React from 'react';
const app = express();

// Augmenting Express Request needs INTERFACE merging (types cannot merge)
declare global {
  namespace Express {
    interface Request { requestId?: string }   // merged into Express's own interface
  }
}
app.use((req, _res, next) => { req.requestId = 'r-1'; next(); });

// ---------- React ----------
// Props: interface (conventional, readable errors, extendable)
interface BadgeProps { status: OrderStatus; count?: number }
export function Badge({ status, count = 0 }: BadgeProps) {
  return <span>{status} ({count})</span>;
}

// Extending props of a DOM element: interface extends works with library types
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> { variant: 'primary' | 'ghost' }
export const Btn = ({ variant, ...rest }: ButtonProps) => <button data-variant={variant} {...rest} />;

// ---------- Redux Toolkit ----------
import type { PayloadAction } from '@reduxjs/toolkit';
type SetStatus = PayloadAction<{ id: number; status: OrderStatus }>;  // action payload: type
export const reducer = (state: Order[], action: SetStatus) => state; // alias reused
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trying to extend a union with an interface
```typescript
type U = { a: string } | { b: number };
// ❌ Wrong: an interface cannot extend a union
interface I extends U {}
// error TS2312: An interface can only extend an object type or intersection of object types with statically known members.
```
```typescript
type U = { a: string } | { b: number };
// ✅ Right: use a type alias (intersection of the union is distributed)
type I = U & { extra: boolean };
const x: I = { a: 'x', extra: true };
```

❌ Mistake 2: Passing an interface where `Record<string, unknown>` is expected
```typescript
interface IUser { id: number }
declare const iu: IUser;
// ❌ Wrong: interfaces have no implicit index signature
const r2: Record<string, unknown> = iu;
// error TS2322: Type 'IUser' is not assignable to type 'Record<string, unknown>'.
//   Index signature for type 'string' is missing in type 'IUser'.
```
✅ Correct: declare it with `type IUser = { id: number }`, or accept a generic `<T extends object>` instead of `Record<string, unknown>`.

❌ Mistake 3: Interface `extends` with an incompatible member
```typescript
interface A1 { x: string }
// ❌ Wrong: x must stay assignable to string
interface B1 extends A1 { x: number }
// error TS2430: Interface 'B1' incorrectly extends interface 'A1'.
//   Types of property 'x' are incompatible.
//     Type 'number' is not assignable to type 'string'.
```
✅ Correct: pick a compatible type or use `Omit<A1, 'x'> & { x: number }`. (With `&` alone there is no error, you just get `never`.)

---

## 🧠 Tricky Interview Question

```typescript
interface Point { x: number }
interface Point { y: number }

type Coord = { x: number };
// type Coord = { y: number };   // what happens if you uncomment this?

const p: Point = { x: 1, y: 2 };
```
Answer: `Point` is declared twice and the two declarations merge into `{ x: number; y: number }`, so the assignment is valid. Uncommenting the second `type Coord` gives `error TS2300: Duplicate identifier 'Coord'.` because type aliases are closed. This is the single behavioural difference interviewers most want to hear, plus the fact that merging is why libraries (Express, Jest) expose `interface`s for extension.

---

## ⚫ Interview Questions + Answers

Q1: What are the differences between `interface` and `type`?
A1: (1) `type` can alias unions, tuples, primitives, conditional and mapped types; `interface` only objects. (2) Interfaces merge, aliases give TS2300. (3) `extends` versus `&`, where `extends` checks compatibility and `&` can silently yield `never`. (4) Object aliases get an implicit index signature, interfaces do not. (5) Interfaces tend to be faster to check in large graphs and print their name in error messages.

Q2: Which one do you use for React props and why?
A2: Either works. Many teams use `interface` for props because errors show the name, `extends React.ButtonHTMLAttributes<...>` is natural, and consumers can augment. Use `type` when props are a union (`type Props = A | B`) or derived (`Omit`, `Pick`). Consistency inside the codebase matters more than the choice.

Q3: Can a class implement a `type` alias?
A3: Yes, if the alias resolves to an object type with statically known members (`type Logger = { log(m: string): void }`). It cannot implement a union type.

Q4: How would you add a `user` property to Express `Request`?
A4: Use declaration merging with `declare global { namespace Express { interface Request { user?: User } } }`. This only works because `Request` is an interface, which is why you cannot do it to a type alias.

Q5: Does the choice affect runtime?
A5: No. Both are erased. The only effect is at compile time: merging, error messages, compile speed and what shapes can be expressed.

---

## 🔷 When to Use + When Not to Use
✅ Use `interface` when:
- Defining object contracts, DTOs, props and class shapes
- Others must be able to extend or augment (library public API, Express `Request`)
- Using deep `extends` hierarchies

✅ Use `type` when:
- Unions, tuples, function types, primitives, mapped, conditional or template literal types
- Composing with `Pick`, `Omit`, `Partial` and other utility types
- You want to forbid accidental merging

❌ Avoid:
- Mixing both randomly for the same kind of thing in one codebase; follow a written convention
- Using `&` to "override" a property; use `Omit<T, K> & {...}` or an interface `extends` to be told about conflicts

---

## 📊 Visual Diagram
```
                       interface            type alias
 object shape             ✔                    ✔
 union / tuple / prim     ✘                    ✔
 conditional / mapped     ✘                    ✔
 declaration merging      ✔                    ✘ (TS2300)
 extends                  ✔ (checks)           & (can give never)
 implicit index sig       ✘                    ✔ (object literal types)
 implements by class      ✔                    ✔ (object types only)

 Rule of thumb:  objects/contracts -> interface    everything else -> type
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Declaration merging | Same-name interfaces combine | एक नाम के interfaces का जुड़ना |
| Intersection | `A & B`, value must satisfy both | दोनों को satisfy करने वाला type |
| Implicit index signature | Aliases of object literals fit `Record<string, X>` | Object alias का अपने-आप index signature |
| Augmentation | Adding members to an existing interface | मौजूदा interface में members जोड़ना |
| Closed type | Cannot be re-declared (type alias) | जिसे दोबारा declare नहीं कर सकते |

---

## ⚡ 3-Line Summary
English:
1. For plain objects they are nearly the same; `type` is more expressive (unions, tuples, mapped), `interface` is open (merging) and extends cleanly.
2. Only interfaces merge (Express `Request` augmentation); only aliases get an implicit index signature and can name unions.
3. Default: `interface` for object contracts and public APIs, `type` for everything else, and stay consistent.

Hindi:
1. सादे objects के लिए दोनों लगभग एक हैं; `type` ज़्यादा expressive है (unions, tuples, mapped), `interface` open है (merging) और साफ़ `extends` करता है।
2. सिर्फ़ interfaces merge होते हैं (Express `Request` augmentation); सिर्फ़ aliases को implicit index signature मिलता है और वे unions को नाम दे सकते हैं।
3. Default: object contracts और public APIs के लिए `interface`, बाकी के लिए `type`, और consistent रहो।

---

## ➡️ Next Topic
**16. Enums (numeric, string, const) + Alternatives** — fixed sets of named constants, their runtime cost, and why many teams prefer `as const` objects.
