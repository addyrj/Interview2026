# 53. Utility Types — Partial, Required, Readonly
# हिंदी में: Utility Types — Partial, Required, Readonly

> TypeScript 5.x पर verify किया गया (`tsc --strict`, TS 5.9). `Partial`/`Readonly` TS 2.1 से, `Required` TS 2.8 से। `Object.freeze` और `as const` से इनका फ़र्क नीचे समझाया गया है।

---

## 🔵 Simple Definition (English)
These three built-in **mapped types** change the *modifiers* of every property of a type without changing the property types: `Partial<T>` makes all properties optional (`?`), `Required<T>` makes all of them required (removes `?`), `Readonly<T>` makes all of them `readonly`. They are shallow: nested objects keep their own modifiers.

## 🔵 सरल परिभाषा (Hindi)
ये तीनों built-in **mapped types** किसी type की हर property के *modifiers* बदलते हैं, property के types नहीं: `Partial<T>` सब properties optional (`?`) बनाता है, `Required<T>` सब required (`?` हटाता है), `Readonly<T>` सब `readonly`। ये shallow हैं: nested objects के अपने modifiers वैसे ही रहते हैं।

---

## 🔴 Problem it Solves
A `PATCH /orders/:id` request sends only changed fields, but the `Order` interface has everything required. Copying the interface into `OrderPatch` with `?` on every field is boilerplate that drifts. A config object loaded once must not be mutated by accident. A function that builds a default object needs the "complete" version of a type whose fields are optional for users. These three utilities derive each variant from one source type.

## 🔴 यह क्यों बना? (Hindi)
`PATCH /orders/:id` request सिर्फ बदले हुए fields भेजती है, पर `Order` interface में सब required है। हर field पर `?` लगाकर `OrderPatch` copy करना boilerplate है और अलग हो जाता है। एक बार load हुआ config गलती से mutate नहीं होना चाहिए। जिस type के fields user के लिए optional हैं, उसका "पूरा" version default बनाने वाले function को चाहिए। ये तीनों utilities एक source type से हर variant बनाते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `Partial<T>` is `{ [K in keyof T]?: T[K] }`. Every property becomes `T[K] | undefined` (and may be omitted).
Step 2 → `Required<T>` is `{ [K in keyof T]-?: T[K] }`. The `-?` strips the optional modifier (and the `undefined` that came from it; an explicit `string | undefined` type stays).
Step 3 → `Readonly<T>` is `{ readonly [K in keyof T]: T[K] }`. Assignments to properties are compile errors (TS2540), but it is erased at runtime: use `Object.freeze` for runtime protection.
Step 4 → All three are **shallow**. `Readonly<{ a: { b: number } }>` still lets you write `x.a.b = 1`. For depth use a recursive `DeepReadonly`.
Step 5 → They combine: `Readonly<Required<Config>>`, or `Partial<Pick<T, K>>` and `Required<Pick<T, K>>` to alter only some keys.
Step 6 → With `exactOptionalPropertyTypes` (TS 4.4), `Partial` properties accept missing but not an explicit `undefined`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `Partial<T>` = `{ [K in keyof T]?: T[K] }`। हर property optional (omit हो सकती है)।
Step 2 → `Required<T>` = `{ [K in keyof T]-?: T[K] }`। `-?` optional हटाता है।
Step 3 → `Readonly<T>` = `{ readonly [K in keyof T]: T[K] }`। Assign करने पर compile error (TS2540); runtime पर यह मिट जाता है, इसलिए runtime सुरक्षा के लिए `Object.freeze` चाहिए।
Step 4 → तीनों **shallow** हैं। `Readonly<{ a: { b: number } }>` में `x.a.b = 1` अब भी चलता है। गहराई के लिए `DeepReadonly` चाहिए।
Step 5 → इन्हें जोड़ सकते हो: `Readonly<Required<Config>>`, या कुछ ही keys बदलने के लिए `Partial<Pick<T, K>>`।
Step 6 → `exactOptionalPropertyTypes` (TS 4.4) में `Partial` की properties missing तो लेती हैं, पर explicit `undefined` नहीं।

---

## 🟡 Real World Example
**Swiggy's** order-update API: the client app sends `PATCH /orders/123` with `{ deliveryInstructions: "Ring bell" }`. Server type: `OrderPatch = Partial<Omit<Order, "id" | "createdAt">>`. The Redux slice state is `Readonly<CartState>` so reducers must return new objects, and the default config is `Required<AppConfig>` after merging user overrides with defaults, so the rest of the app never checks for `undefined`.

## 🟡 Real Example Hindi mein
**Swiggy** की order-update API: client app `PATCH /orders/123` में `{ deliveryInstructions: "Ring bell" }` भेजती है। Server type: `OrderPatch = Partial<Omit<Order, "id" | "createdAt">>`। Redux slice का state `Readonly<CartState>` है ताकि reducers नया object लौटाएँ, और default config user overrides को defaults से merge करने के बाद `Required<AppConfig>` है, इसलिए बाकी app `undefined` check नहीं करती।

---

## 💻 Code Example — Basic

```typescript
// Source type
interface Order {
  id: string; // order id
  amount: number; // amount in rupees
  note?: string; // optional customer note
  status: "PLACED" | "PAID"; // lifecycle
}

// Partial: every field optional (update payload)
const patch: Partial<Order> = { amount: 599 }; // only changed field
const empty: Partial<Order> = {}; // also valid

// Required: every field mandatory (note is no longer optional)
const full: Required<Order> = { id: "o1", amount: 499, note: "No onion", status: "PLACED" };

// Readonly: no property assignment after creation
const frozen: Readonly<Order> = { id: "o2", amount: 100, status: "PAID" };
// frozen.amount = 1; // would be an error TS2540

// Partial of a function parameter: merge defaults with overrides
function createOrder(overrides: Partial<Order> = {}): Order {
  const defaults: Order = { id: "new", amount: 0, status: "PLACED" }; // base values
  return { ...defaults, ...overrides }; // overrides win
}
console.log(createOrder(patch), full.note, frozen.id, Object.keys(empty).length);
// { id: 'new', amount: 599, status: 'PLACED' } No onion o2 0
```

## 💻 Code Example — Advanced

```typescript
// Advanced 1: update function that never lets you change id
interface Product {
  id: number; // PK
  name: string; // name
  price: number; // price in paise
  stock: number; // units
}
type ProductUpdate = Partial<Omit<Product, "id">>; // all optional except id is not allowed at all

function applyUpdate(p: Readonly<Product>, u: ProductUpdate): Product {
  return { ...p, ...u }; // returns a new object, original untouched
}
const base: Readonly<Product> = { id: 1, name: "Tea", price: 1500, stock: 10 };
console.log(applyUpdate(base, { price: 1800 })); // { id: 1, name: 'Tea', price: 1800, stock: 10 }

// Advanced 2: make only some keys optional / required (combine with Pick and Omit)
type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
type RequiredBy<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>;
type NewProduct = PartialBy<Product, "id" | "stock">; // id and stock optional on create
const np: NewProduct = { name: "Coffee", price: 2000 }; // OK
type WithNote = RequiredBy<{ a: number; note?: string }, "note">;
const wn: WithNote = { a: 1, note: "x" }; // note is mandatory here

// Advanced 3: Readonly is shallow: nested objects stay mutable
interface State {
  user: { name: string }; // nested
}
const st: Readonly<State> = { user: { name: "Asha" } };
st.user.name = "Ravi"; // compiles: only the top level is readonly
console.log(st.user.name); // Ravi

// Advanced 4: DeepReadonly fixes it; Object.freeze gives runtime protection
type DeepReadonly<T> = { readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K] };
const ds: DeepReadonly<State> = { user: { name: "Asha" } };
// ds.user.name = "x"; // error TS2540 now
const frozenRuntime = Object.freeze({ a: 1 }); // type is Readonly<{ a: number }>; also frozen at runtime
console.log(Object.isFrozen(frozenRuntime), np.name, wn.note, ds.user.name); // true Coffee x Asha
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: PATCH endpoint with Partial body + a whitelist of updatable fields
import express from "express";

interface User {
  id: number; // PK
  email: string; // email
  name: string; // display name
}
type UserPatch = Partial<Omit<User, "id">>; // id can never be patched

const users: User[] = [{ id: 1, email: "a@x.in", name: "Asha" }];
const app = express();
app.use(express.json());
app.patch("/users/:id", (req, res) => {
  const patch = req.body as UserPatch; // validate with Zod in real code
  const idx = users.findIndex((u) => u.id === Number(req.params.id));
  const current = users[idx];
  if (!current) { res.status(404).end(); return; } // not found
  users[idx] = { ...current, ...patch }; // merge
  res.json(users[idx]);
});
```

```tsx
// React + Redux style: Readonly state and Partial form updates
import { useReducer } from "react";

interface Profile {
  name: string; // name
  city: string; // city
}
type State = Readonly<Profile>; // reducers must return new objects
type Action = { type: "patch"; payload: Partial<Profile> }; // patch some fields

function reducer(s: State, a: Action): State {
  switch (a.type) {
    case "patch": return { ...s, ...a.payload }; // new object, not mutation
  }
}

export function ProfileForm() {
  const [s, dispatch] = useReducer(reducer, { name: "Asha", city: "Pune" });
  return <input value={s.city} onChange={(e) => dispatch({ type: "patch", payload: { city: e.target.value } })} />;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mutating a `Readonly` value
```typescript
// ❌ Wrong
interface Cfg { port: number }
const cfg: Readonly<Cfg> = { port: 3000 };
cfg.port = 4000;
// error TS2540: Cannot assign to 'port' because it is a read-only property.
```

❌ Mistake 2: Passing a `Partial` where the full type is needed
```typescript
// ❌ Wrong
interface Order { id: string; amount: number }
function charge(o: Order) { return o.amount; }
const draft: Partial<Order> = { id: "o1" };
charge(draft);
// error TS2345: Argument of type 'Partial<Order>' is not assignable to parameter of type 'Order'.
//   Types of property 'id' are incompatible.
//     Type 'string | undefined' is not assignable to type 'string'.
```

❌ Mistake 3: Expecting `Required` to remove an explicit `| undefined`
```typescript
interface A { x?: number; y: number | undefined }
const r: Required<A> = { x: 1, y: undefined }; // OK: y keeps its explicit undefined; only the "?" is removed
```

---

## 🧠 Tricky Interview Question

```typescript
interface User { name: string; address: { city: string } }
const u: Readonly<User> = { name: "A", address: { city: "Pune" } };
u.address.city = "Delhi";
u.name = "B"; // ❌ error TS2540: Cannot assign to 'name' because it is a read-only property.
```
**Which lines compile?**

Answer: `u.address.city = "Delhi"` compiles because `Readonly` is shallow, only top-level properties get `readonly`. `u.name = "B"` fails: `error TS2540: Cannot assign to 'name' because it is a read-only property.` A related surprise: `Readonly<T>` has **no runtime effect**; the object is still mutable via a cast or JS code. Use `Object.freeze` (shallow) or Immer's frozen drafts (what Redux Toolkit uses) for runtime protection.

---

## ⚫ Interview Questions + Answers

Q1: How would you implement `Partial` and `Required`?
A1: `type Partial<T> = { [K in keyof T]?: T[K] }` and `type Required<T> = { [K in keyof T]-?: T[K] }`. `-?` removes the optional modifier.

Q2: Are these deep or shallow? How to make them deep?
A2: Shallow. Write a recursive mapped type (`DeepPartial`, `DeepReadonly`) that applies the modifier at each object level, taking care of arrays and functions.

Q3: Does `Readonly` freeze the object at runtime?
A3: No, only the type checker enforces it. For runtime use `Object.freeze` (shallow) or libraries like Immer. `as const` also yields readonly types for literals.

Q4: When would you choose `Partial<Pick<T, K>>` over `Partial<T>`?
A4: When only specific fields may change (PATCH endpoint). It documents the allowed fields and blocks changing the ones you do not list, e.g. `id` or `createdAt`.

Q5: What is a common pitfall using `Partial` for function options?
A5: Using `Partial<Options>` as an options bag, then forgetting defaults: inside, every field can be `undefined`. Merge with defaults and return a `Required<Options>` so the rest of the code is clean.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- PATCH/update payloads, form drafts, options with defaults (`Partial`)
- After applying defaults, to express "everything is set" (`Required`)
- Redux state, config, constants that must not be mutated (`Readonly`)

❌ Avoid when:
- You need nested optionality or immutability (write Deep variants)
- You need only a few fields optional; use `PartialBy` / `Pick`
- Runtime immutability is the goal; types alone will not enforce it

---

## 📊 Visual Diagram
```
  interface Order { id: string; note?: string }

  Partial<Order>   { id?: string;  note?: string }     add  ?
  Required<Order>  { id: string;   note: string  }     remove ?
  Readonly<Order>  { readonly id: string; readonly note?: string }

  shallow:  Readonly<{ a: { b } }>   ->  a is readonly, a.b is NOT
  runtime:  type-only  (use Object.freeze / Immer for real protection)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Partial | All props optional | सब props optional |
| Required | All props mandatory | सब props ज़रूरी |
| Readonly | No reassignment | दोबारा assign नहीं |
| Shallow | Only top level | सिर्फ ऊपरी level |
| Modifier | `?` or `readonly` | `?` या `readonly` चिन्ह |

---

## ⚡ 3-Line Summary
English:
1. `Partial` adds `?`, `Required` removes it, `Readonly` blocks reassignment of every property.
2. All three are shallow mapped types and `Readonly` exists only at compile time.
3. Combine with `Pick`/`Omit` for PATCH payloads, defaults merging, and immutable Redux state.

Hindi:
1. `Partial` `?` जोड़ता है, `Required` हटाता है, `Readonly` हर property का reassignment रोकता है।
2. तीनों shallow mapped types हैं और `Readonly` सिर्फ compile time पर है।
3. PATCH payloads, defaults merge और immutable Redux state के लिए `Pick`/`Omit` के साथ जोड़ो।

---

## ➡️ Next Topic
**54. Utility Types — Pick, Omit, Record** — fields चुनना, हटाना, और key-value maps typed बनाना।
