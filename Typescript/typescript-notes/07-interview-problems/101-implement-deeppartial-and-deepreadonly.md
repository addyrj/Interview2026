# 101. Implement DeepPartial and DeepReadonly
# हिंदी में: DeepPartial और DeepReadonly खुद बनाना

> Verified with **TypeScript 5.9.3** (`--strict`). Core technique (recursive mapped + conditional types) works on **TS 4.1+**; nothing here needs 5.x-only features.

---

## 🔵 Simple Definition (English)
`Partial<T>` and `Readonly<T>` from the standard library are **shallow**: they only change the first level of properties. **`DeepPartial<T>`** makes every property optional at **every depth**, and **`DeepReadonly<T>`** makes every property (and every array/nested object) read-only at every depth. You build them with a **recursive mapped type** guarded by a **conditional type** that decides when to stop recursing (primitives, functions, `Date`).

## 🔵 सरल परिभाषा (Hindi)
Standard library के `Partial<T>` और `Readonly<T>` **shallow** हैं: ये सिर्फ पहले level की properties बदलते हैं। **`DeepPartial<T>`** हर depth की हर property को optional बना देता है, और **`DeepReadonly<T>`** हर depth की हर property (और हर array/nested object) को read-only बना देता है। इन्हें **recursive mapped type** से बनाते हैं, जिसके साथ एक **conditional type** तय करता है कि recursion कब रोकना है (primitives, functions, `Date`)।

---

## 🔴 Problem it Solves
A PATCH `/orders/:id` endpoint accepts "any subset of the order, including any subset of the nested address". `Partial<Order>` lets you omit `address`, but if you send `address` you must send **every** field of it. Likewise `Readonly<Config>` freezes `config.db` but still lets `config.db.host = "x"`. Shallow utilities silently leave nested levels unprotected, so real bugs (partial updates rejected, config mutated at runtime) slip through.

## 🔴 यह क्यों बना? (Hindi)
PATCH `/orders/:id` endpoint "order का कोई भी subset, nested address का भी कोई subset" लेता है। `Partial<Order>` से आप `address` छोड़ सकते हो, लेकिन `address` भेजा तो उसके **सारे** fields भेजने पड़ेंगे। इसी तरह `Readonly<Config>` `config.db` को freeze करता है पर `config.db.host = "x"` फिर भी चलता है। Shallow utilities nested levels को चुपचाप unprotected छोड़ देती हैं, इसलिए असली bugs (partial update reject होना, config runtime में बदल जाना) निकल जाते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Start from a **mapped type**: `{ [K in keyof T]?: T[K] }` (this is `Partial`).
Step 2 → Replace `T[K]` with `DeepPartial<T[K]>`: the type now calls **itself** on every property type = recursion.
Step 3 → Add a **base case** with a conditional type: if `T` is a primitive, function or `Date`, return `T` unchanged, otherwise recurse.
Step 4 → Handle **arrays**: mapping over an array type with a homomorphic mapped type keeps it an array, but for clarity use `T extends (infer U)[] ? DeepPartial<U>[] : ...` (for `DeepReadonly` use `readonly DeepReadonly<U>[]`).
Step 5 → Test with `// ❌` cases: assigning to a deep property must fail for `DeepReadonly`, omitting nested keys must pass for `DeepPartial`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Mapped type** से शुरू करो: `{ [K in keyof T]?: T[K] }` (यही `Partial` है)।
Step 2 → `T[K]` की जगह `DeepPartial<T[K]>` लिखो: type अब हर property type पर **खुद को** call करता है = recursion।
Step 3 → Conditional type से **base case** जोड़ो: अगर `T` primitive, function या `Date` है तो उसे वैसे ही लौटाओ, वरना recurse करो।
Step 4 → **Arrays** संभालो: `T extends (infer U)[] ? DeepPartial<U>[] : ...` (`DeepReadonly` के लिए `readonly DeepReadonly<U>[]`)।
Step 5 → `// ❌` cases से test करो: `DeepReadonly` में deep property assign करना fail होना चाहिए, `DeepPartial` में nested keys छोड़ना pass होना चाहिए।

---

## 🟡 Real World Example
**Swiggy's order-edit API**: a customer changes only the delivery pin code. The client sends `{ address: { pincode: "560001" } }`. The server types the body as `DeepPartial<Order>` so nested `address` can be partial. On the other side, the server's loaded **pricing config** (GST slabs, delivery fee tiers) is typed `DeepReadonly<PricingConfig>` so no request handler can accidentally mutate a shared, in-memory object that every request reads.

## 🟡 Real Example Hindi mein
**Swiggy का order-edit API**: customer सिर्फ delivery pin code बदलता है। Client `{ address: { pincode: "560001" } }` भेजता है। Server body को `DeepPartial<Order>` type करता है ताकि nested `address` भी partial हो सके। दूसरी तरफ server का loaded **pricing config** (GST slabs, delivery fee tiers) `DeepReadonly<PricingConfig>` type होता है ताकि कोई request handler गलती से shared in-memory object को mutate न कर सके जिसे हर request पढ़ती है।

---

## 💻 Code Example — Basic

```typescript
// deep-basic.ts — the two types and a first test
type Primitive = string | number | boolean | bigint | symbol | null | undefined; // leaf types

// DeepPartial: every key optional, at every depth
type DeepPartial<T> =
  T extends Primitive | Function | Date ? T // base case: stop recursing, keep as is
  : T extends (infer U)[] ? DeepPartial<U>[] // arrays: make elements deep-partial
  : { [K in keyof T]?: DeepPartial<T[K]> }; // objects: optional + recurse

// DeepReadonly: every key readonly, at every depth
type DeepReadonly<T> =
  T extends Primitive | Function | Date ? T // base case
  : T extends (infer U)[] ? readonly DeepReadonly<U>[] // arrays become readonly arrays
  : { readonly [K in keyof T]: DeepReadonly<T[K]> }; // objects: readonly + recurse

interface Order { // sample domain type
  id: number; // order id
  address: { city: string; pincode: string }; // nested object
  items: { sku: string; qty: number }[]; // array of objects
}

const patch: DeepPartial<Order> = { address: { pincode: "560001" } }; // nested subset is fine
const empty: DeepPartial<Order> = {}; // everything optional
console.log(JSON.stringify(patch), JSON.stringify(empty)); // prints {"address":{"pincode":"560001"}} {}
```

```typescript
// deep-readonly-error.ts — shallow Readonly vs DeepReadonly
type Primitive = string | number | boolean | bigint | symbol | null | undefined; // leaves
type DeepReadonly<T> =
  T extends Primitive | Function | Date ? T // base
  : T extends (infer U)[] ? readonly DeepReadonly<U>[] // arrays
  : { readonly [K in keyof T]: DeepReadonly<T[K]> }; // objects

interface Config { db: { host: string; port: number }; tags: string[] } // sample config

const shallow: Readonly<Config> = { db: { host: "a", port: 1 }, tags: [] }; // shallow only
shallow.db.host = "b"; // compiles: Readonly is NOT deep (this is the gap we are fixing)

const deep: DeepReadonly<Config> = { db: { host: "a", port: 1 }, tags: [] }; // deep version

// ❌ nested write is blocked
deep.db.host = "b";
// error TS2540: Cannot assign to 'host' because it is a read-only property.
```

## 💻 Code Example — Advanced

```typescript
// deep-advanced.ts — tuples, readonly arrays, Map/Set, and a runtime deepFreeze that matches the type
type Primitive = string | number | boolean | bigint | symbol | null | undefined; // leaves

type DeepReadonly<T> =
  T extends Primitive | Function | Date ? T // leaves, functions, dates untouched
  : T extends ReadonlyMap<infer K, infer V> ? ReadonlyMap<DeepReadonly<K>, DeepReadonly<V>> // Map
  : T extends ReadonlySet<infer E> ? ReadonlySet<DeepReadonly<E>> // Set
  : { readonly [K in keyof T]: DeepReadonly<T[K]> }; // objects, arrays AND tuples (homomorphic map keeps tuple shape)

// A homomorphic mapped type over a tuple keeps it a tuple, over an array keeps it an array
type T1 = DeepReadonly<[string, { n: number }]>; // readonly [string, { readonly n: number }]
const t1: T1 = ["gst", { n: 18 }]; // fine to create
// t1[1].n = 5; would be TS2540, we check below

// runtime counterpart: freeze recursively so JS also enforces what the type promises
function deepFreeze<T extends object>(obj: T): DeepReadonly<T> {
  Object.values(obj).forEach((v) => { // visit every own value
    if (typeof v === "object" && v !== null) deepFreeze(v); // recurse into nested objects/arrays
  });
  return Object.freeze(obj) as DeepReadonly<T>; // freeze this level, cast to the deep type
}

const pricing = deepFreeze({ gst: { food: 5, delivery: 18 }, slabs: [0, 100, 500] }); // frozen config
console.log(pricing.gst.food, pricing.slabs.length); // prints 5 3
```

```typescript
// deep-partial-merge.ts — DeepPartial used by a typed deep-merge (PATCH apply)
type Primitive = string | number | boolean | bigint | symbol | null | undefined; // leaves
type DeepPartial<T> =
  T extends Primitive | Function | Date ? T // base
  : T extends (infer U)[] ? DeepPartial<U>[] // arrays
  : { [K in keyof T]?: DeepPartial<T[K]> }; // objects

interface Order { id: number; address: { city: string; pincode: string }; note?: string } // domain

function isPlainObject(v: unknown): v is Record<string, unknown> { // runtime guard for recursion
  return typeof v === "object" && v !== null && !Array.isArray(v); // object but not array/null
}

function merge(base: Record<string, unknown>, patch: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = { ...base }; // shallow copy of the base
  for (const [k, pv] of Object.entries(patch)) { // each key in the patch
    const bv = out[k]; // existing value
    out[k] = isPlainObject(bv) && isPlainObject(pv) ? merge(bv, pv) : pv; // recurse or replace
  }
  return out; // merged result
}

function applyPatch<T extends object>(base: T, patch: DeepPartial<T>): T {
  // one cast at the boundary: the public signature is typed, the internals are untyped
  return merge(base as Record<string, unknown>, patch as Record<string, unknown>) as T;
}

const before: Order = { id: 7, address: { city: "Pune", pincode: "411001" } }; // stored order
const after = applyPatch(before, { address: { pincode: "560001" } }); // only pincode changes
console.log(after); // prints { id: 7, address: { city: 'Pune', pincode: '560001' } }
```

---

## 🟠 Node/Express + React Integration

```typescript
// patch-route.ts — Express PATCH with DeepPartial body
import express from "express"; // express + @types/express

type Primitive = string | number | boolean | bigint | symbol | null | undefined; // leaves
type DeepPartial<T> =
  T extends Primitive | Function | Date ? T // base
  : T extends (infer U)[] ? DeepPartial<U>[] // arrays
  : { [K in keyof T]?: DeepPartial<T[K]> }; // objects

interface Order { id: number; address: { city: string; pincode: string }; status: "placed" | "shipped" } // domain

const app = express(); // app instance
app.use(express.json()); // parse JSON bodies

// Request<Params, ResBody, ReqBody>: third generic types req.body
app.patch("/orders/:id", (req: express.Request<{ id: string }, unknown, DeepPartial<Order>>, res) => {
  const city: string | undefined = req.body.address?.city; // nested access needs ?. because it is optional
  res.json({ id: Number(req.params.id), changedCity: city ?? null }); // echo
});
```

```tsx
// SettingsForm.tsx — React: form state is DeepPartial until submit
import { useState } from "react"; // hooks

type Primitive = string | number | boolean | bigint | symbol | null | undefined; // leaves
type DeepPartial<T> =
  T extends Primitive | Function | Date ? T // base
  : T extends (infer U)[] ? DeepPartial<U>[] // arrays
  : { [K in keyof T]?: DeepPartial<T[K]> }; // objects

interface Profile { name: string; address: { city: string; pincode: string } } // full shape

export function SettingsForm() { // component
  const [draft, setDraft] = useState<DeepPartial<Profile>>({}); // user has typed nothing yet
  return (
    <input
      value={draft.address?.pincode ?? ""} // optional chain because every level is optional
      onChange={(e) => setDraft({ ...draft, address: { ...draft.address, pincode: e.target.value } })} // nested update
    />
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting the base case, so `Date`/functions get mapped into garbage
```typescript
// wrong-base.ts
type BadDeepPartial<T> = { [K in keyof T]?: BadDeepPartial<T[K]> }; // wrong: no base case
type GoodDeepPartial<T> = T extends Date | Function | string | number | boolean | null | undefined
  ? T // right: stop at leaves
  : { [K in keyof T]?: GoodDeepPartial<T[K]> };

interface Event { at: Date } // has a Date
const e: GoodDeepPartial<Event> = { at: new Date(0) }; // OK, Date kept intact
// With BadDeepPartial, "at" would be an object whose methods (getTime...) are all optional,
// so even {} would be accepted for "at".
const weak: BadDeepPartial<Event> = { at: {} }; // compiles: type is too loose
console.log(e.at?.getTime(), typeof weak.at); // prints 0 object
```

❌ Mistake 2: Using `DeepReadonly` but passing the object to a function that wants a mutable type
```typescript
// wrong-mutable.ts
type DeepReadonly<T> = T extends string | number | boolean ? T
  : T extends (infer U)[] ? readonly DeepReadonly<U>[]
  : { readonly [K in keyof T]: DeepReadonly<T[K]> }; // same helper

function addTag(tags: string[]): void { tags.push("new"); } // mutates its argument
const cfg: DeepReadonly<{ tags: string[] }> = { tags: ["a"] }; // frozen shape

// ❌ readonly string[] is not assignable to string[]
addTag(cfg.tags);
// error TS2345: Argument of type 'readonly string[]' is not assignable to parameter of type 'string[]'.
//   The type 'readonly string[]' is 'readonly' and cannot be assigned to the mutable type 'string[]'.
```
✅ Correct: change the parameter to `readonly string[]` if the function does not mutate, or copy with `[...cfg.tags]` first.

❌ Mistake 3: Expecting `DeepReadonly` to freeze at runtime
✅ Correct: it is **compile-time only**. Use `Object.freeze` recursively (`deepFreeze` above) if you also need runtime protection.

---

## 🧠 Tricky Interview Question

```typescript
// tricky.ts — what is the type of R, and does the last line compile?
type DeepPartial<T> = T extends (infer U)[] ? DeepPartial<U>[]
  : T extends object ? { [K in keyof T]?: DeepPartial<T[K]> } : T;

type R = DeepPartial<{ a: { b: number }[] }>; // what is R?
const r: R = { a: [{}] }; // does this compile?
console.log(JSON.stringify(r)); // prints {"a":[{}]}
```
**Answer:** `R` is `{ a?: { b?: number }[] }`. The array branch makes the **element** deep-partial, so `{}` is a valid element and the code compiles. Note the property `a` is optional but the **array itself** is not sparse. A common wrong answer: "arrays are not objects so they stay unchanged". Without the `(infer U)[]` branch, a homomorphic mapped type would still handle arrays correctly (TS maps over elements), the explicit branch just makes intent clear and works on generic `T` too.

---

## ⚫ Interview Questions + Answers

Q1: Why are `Partial` and `Readonly` called shallow?
A1: They are one-level mapped types: `{ [K in keyof T]?: T[K] }`. `T[K]` is used as-is, so nested object types are untouched.

Q2: How do you stop the recursion?
A2: A conditional type base case: `T extends Primitive | Function | Date ? T : ...`. Without it functions, `Date`, `Map` etc. get structurally mapped and lose their meaning.

Q3: Does TypeScript limit recursion depth?
A3: Yes. Instantiation depth is capped (about 50 for plain recursion, more with tail-recursive conditional types since TS 4.5). Very deep or self-referential types give "Type instantiation is excessively deep and possibly infinite" (TS2589).

Q4: How does `DeepReadonly` treat arrays and tuples?
A4: A homomorphic mapped type (`{ readonly [K in keyof T]: ... }` where `T` is a type parameter) preserves tuple and array shape and adds `readonly`, so `string[]` becomes `readonly string[]`.

Q5: DeepPartial for PATCH: what runtime risk remains?
A5: The type only describes shape, it does not validate. Clients may send extra or wrongly-typed keys, so validate with Zod (`schema.deepPartial()` exists in Zod 3) before merging.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- PATCH bodies, form drafts, test fixtures/factories (`makeOrder({ address: { city: "X" } })`)
- Shared immutable config or Redux-style state you must never mutate

❌ Avoid when:
- Type contains classes with private fields, `Map`/`Set`, or branded types without extra branches
- A simple `Pick`/`Omit` + `Partial` on one level is enough, deep types slow the compiler

---

## 📊 Visual Diagram
```
DeepPartial<Order>
─────────────────────────────────────────────
Order                         DeepPartial<Order>
 ├─ id: number          ──►    id?: number
 ├─ address: {...}      ──►    address?: DeepPartial<{...}>
 │    ├─ city: string   ──►        city?: string
 │    └─ pincode        ──►        pincode?: string
 └─ items: Item[]       ──►    items?: DeepPartial<Item>[]

Decision per node:
  primitive/function/Date ?  ── yes ──► keep T
        │ no
        ▼
  array ? ── yes ──► DeepX<element>[]
        │ no
        ▼
  object ─────────► { [K in keyof T]?: DeepX<T[K]> }   (recurse)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Mapped type | Build a type by looping over keys | Keys पर loop करके type बनाना |
| Recursive type | Type that refers to itself | खुद को refer करने वाला type |
| Base case | Condition that stops recursion | Recursion रोकने की condition |
| Homomorphic | Mapped type over `keyof T` of same `T` | Same `T` के keyof पर mapped type |
| Shallow vs deep | One level vs all levels | एक level बनाम सभी levels |
| `deepFreeze` | Runtime recursive `Object.freeze` | Runtime पर recursive freeze |

---

## ⚡ 3-Line Summary
English:
1. `Partial`/`Readonly` are shallow, deep versions recurse through a mapped type with `T[K]` replaced by `DeepX<T[K]>`.
2. Always add a base case (primitives, functions, `Date`) and decide how arrays/Map/Set behave.
3. Types are compile-time only, pair `DeepReadonly` with `deepFreeze` and `DeepPartial` with runtime validation.

Hindi:
1. `Partial`/`Readonly` shallow हैं, deep versions mapped type में `T[K]` की जगह `DeepX<T[K]>` लगाकर recurse करते हैं।
2. हमेशा base case (primitives, functions, `Date`) जोड़ो और तय करो कि arrays/Map/Set कैसे बर्ताव करेंगे।
3. Types सिर्फ compile-time के हैं, `DeepReadonly` के साथ `deepFreeze` और `DeepPartial` के साथ runtime validation लगाओ।

---

## ➡️ Next Topic
**102. Implement Pick, Omit, Record from Scratch** — rebuilding the built-in utility types with `keyof`, mapped types and `Exclude`.
