# 47. Mapped Types
# हिंदी में: Mapped Types (हर property को transform करना)

> TypeScript 5.x पर verify किया गया (`tsc --strict`, TS 5.9). Key remapping with `as` TS 4.1 से; `-?`/`-readonly` modifiers TS 2.8 से।

---

## 🔵 Simple Definition (English)
A **mapped type** builds a new object type by looping over the keys of another type: `{ [K in keyof T]: Transform<T[K]> }`. For each key `K` it creates a property whose type you control. It can add or remove modifiers (`readonly`, `?`) using `+`/`-`, and rename keys with `as`. `Partial`, `Readonly`, `Pick` and `Record` are all mapped types.

## 🔵 सरल परिभाषा (Hindi)
**Mapped type** किसी दूसरे type की keys पर loop चलाकर नया object type बनाता है: `{ [K in keyof T]: Transform<T[K]> }`। हर key `K` के लिए एक property बनती है जिसका type आप तय करते हो। `+`/`-` से `readonly` और `?` modifiers जोड़ या हटा सकते हो, और `as` से key का नाम बदल सकते हो। `Partial`, `Readonly`, `Pick`, `Record` सब mapped types हैं।

---

## 🔴 Problem it Solves
You have `Order` and need `OrderUpdate` (all fields optional), `OrderForm` (all fields as strings, since HTML inputs give strings), `OrderErrors` (each field maps to an error message), `OrderGetters` (`getId`, `getAmount`). Hand-writing each copy duplicates fields; when `Order` changes, the copies silently drift. Mapped types derive them from one source of truth.

## 🔴 यह क्यों बना? (Hindi)
आपके पास `Order` है और चाहिए `OrderUpdate` (सब fields optional), `OrderForm` (सब strings, क्योंकि HTML input string देता है), `OrderErrors` (हर field का error message), `OrderGetters` (`getId`, `getAmount`)। हर copy हाथ से लिखने पर fields duplicate होते हैं और `Order` बदलने पर copies चुपचाप अलग हो जाती हैं। Mapped types एक ही source से सब derive करते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Syntax: `type M<T> = { [K in keyof T]: T[K] }`. This is an identity (homomorphic) copy.
Step 2 → `K in keyof T` loops over each key; `T[K]` is that key's value type.
Step 3 → Change the value: `{ [K in keyof T]: string }` or `{ [K in keyof T]: T[K] | null }`.
Step 4 → Modifiers: `+readonly` / `-readonly`, `+?` / `-?`. `-?` removes optionality (that is how `Required` works).
Step 5 → Key remapping (TS 4.1+): `{ [K in keyof T as `get${Capitalize<K & string>}`]: () => T[K] }`. Mapping a key to `never` removes it (filtering).
Step 6 → Homomorphic mapped types (`in keyof T`) preserve the source's modifiers. Mapping over a plain union (`[K in "a" | "b"]`) does not copy modifiers.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Syntax: `type M<T> = { [K in keyof T]: T[K] }`। यह identity (homomorphic) copy है।
Step 2 → `K in keyof T` हर key पर loop चलाता है; `T[K]` उस key का value type है।
Step 3 → Value बदलो: `{ [K in keyof T]: string }` या `{ [K in keyof T]: T[K] | null }`।
Step 4 → Modifiers: `+readonly` / `-readonly`, `+?` / `-?`। `-?` optional हटाता है (`Required` ऐसे ही बना है)।
Step 5 → Key remapping (TS 4.1+): `as` से नाम बदलो; key को `never` map करो तो वह हट जाती है (filter)।
Step 6 → Homomorphic mapped types (`in keyof T`) source के modifiers सुरक्षित रखते हैं। सीधे union पर map करो (`[K in "a" | "b"]`) तो modifiers copy नहीं होते।

---

## 🟡 Real World Example
**Paytm's** KYC form has fields `name`, `pan`, `aadhaar`, `dob`. The backend model uses real types (`dob: Date`). The React form state needs every field as `string` (inputs), and a validation object needs every field as `string | undefined` error text. With mapped types: `FormState<T> = { [K in keyof T]: string }` and `Errors<T> = { [K in keyof T]?: string }`. Add `address` to the model and both the form and the error type get it automatically.

## 🟡 Real Example Hindi mein
**Paytm** के KYC form में `name`, `pan`, `aadhaar`, `dob` fields हैं। Backend model में असली types हैं (`dob: Date`)। React form state में हर field `string` चाहिए (inputs), और validation object में हर field का error text। Mapped types से: `FormState<T> = { [K in keyof T]: string }` और `Errors<T> = { [K in keyof T]?: string }`। Model में `address` जोड़ो तो form और error दोनों types में अपने आप आ जाता है।

---

## 💻 Code Example — Basic

```typescript
// Source of truth
interface Kyc {
  name: string; // full name
  pan: string; // PAN number
  dob: Date; // date of birth
  verified: boolean; // KYC status
}

// 1) Every field becomes a string (form inputs)
type FormState<T> = { [K in keyof T]: string };
const form: FormState<Kyc> = { name: "Asha", pan: "ABCDE1234F", dob: "1995-04-02", verified: "false" };

// 2) Every field becomes optional (error messages)
type Errors<T> = { [K in keyof T]?: string };
const errors: Errors<Kyc> = { pan: "Invalid PAN" }; // only some keys present

// 3) Make everything nullable
type Nullable<T> = { [K in keyof T]: T[K] | null };
const draft: Nullable<Kyc> = { name: "Asha", pan: null, dob: null, verified: false };

// 4) Reimplement built-ins: Readonly and Required (modifier control)
type MyReadonly<T> = { +readonly [K in keyof T]: T[K] }; // add readonly
type MyRequired<T> = { [K in keyof T]-?: T[K] }; // remove optional
type Optional = { a?: number; b: string };
const r: MyRequired<Optional> = { a: 1, b: "x" }; // a is now required
const ro: MyReadonly<Optional> = { b: "y" }; // fields are readonly

console.log(form.name, errors.pan, draft.pan, r.a, ro.b); // Asha Invalid PAN null 1 y
```

## 💻 Code Example — Advanced

```typescript
// Advanced: key remapping with `as` (TS 4.1+) and filtering by value type
interface Order {
  id: string; // order id
  amount: number; // amount
  status: "PLACED" | "PAID"; // state
  notes?: string; // optional notes
}

// Getters: id -> getId, amount -> getAmount
type Getters<T> = {
  [K in keyof T as `get${Capitalize<K & string>}`]-?: () => T[K]; // rename key, remove optional
};
const g: Getters<Order> = {
  getId: () => "o1",
  getAmount: () => 499,
  getStatus: () => "PAID",
  getNotes: () => undefined, // returns string | undefined
};

// Filter: keep only keys whose value is number (map others to never)
type OnlyNumbers<T> = {
  [K in keyof T as T[K] extends number ? K : never]: T[K];
};
type NumericOrder = OnlyNumbers<Order>; // { amount: number }
const n: NumericOrder = { amount: 10 };

// Deep readonly via recursion (mapped type calling itself)
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};
interface Config {
  db: { host: string; port: number }; // nested object
}
const cfg: DeepReadonly<Config> = { db: { host: "sql.local", port: 1433 } };
// cfg.db.port = 1; // would be an error TS2540

// Event handler map from a union of event names
type EventName = "click" | "submit";
type Handlers = { [E in EventName as `on${Capitalize<E>}`]: (e: Event) => void };
const h: Handlers = { onClick: () => {}, onSubmit: () => {} };

console.log(g.getId(), g.getAmount(), n.amount, cfg.db.host, Object.keys(h)); // o1 499 10 sql.local [ 'onClick', 'onSubmit' ]
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: map a SQL Server row (snake_case) to a camelCase DTO, typed end to end
import express from "express";

interface OrderRow {
  order_id: number; // INT column
  total_amount: number; // DECIMAL column
  created_at: Date; // DATETIME2 column
}

// Mapped type that converts snake_case keys to camelCase (template literal + as)
type CamelCase<S extends string> = S extends `${infer A}_${infer B}` ? `${A}${Capitalize<CamelCase<B>>}` : S;
type Camelize<T> = { [K in keyof T as CamelCase<K & string>]: T[K] };

type OrderDto = Camelize<OrderRow>; // { orderId; totalAmount; createdAt }

function toDto(row: OrderRow): OrderDto {
  return { orderId: row.order_id, totalAmount: row.total_amount, createdAt: row.created_at }; // compiler verifies keys
}

const app = express();
app.get("/orders/1", (_req, res) => {
  res.json(toDto({ order_id: 1, total_amount: 499, created_at: new Date() })); // typed response
});
```

```tsx
// React: generic form state derived from the model with a mapped type
import { useState, type ChangeEvent } from "react";

interface Address {
  city: string; // city
  pin: number; // pincode
}
type FormOf<T> = { [K in keyof T]: string }; // everything is a string in inputs

export function AddressForm() {
  const [form, setForm] = useState<FormOf<Address>>({ city: "", pin: "" }); // string fields
  const onChange = (key: keyof Address) => (e: ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value })); // update one key
  return (
    <form>
      <input value={form.city} onChange={onChange("city")} />
      <input value={form.pin} onChange={onChange("pin")} />
    </form>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `in` on a type that is not a key union
```typescript
// ❌ Wrong
type Bad<T> = { [K in T]: string };
// error TS2322: Type 'T' is not assignable to type 'string | number | symbol'.

// ✅ Right: constrain to PropertyKey, or use keyof
type Good<T extends PropertyKey> = { [K in T]: string };
```

❌ Mistake 2: Forgetting that `?` and `readonly` are copied (homomorphic) so a "plain copy" is not plain
```typescript
interface A { x?: number }
type Copy<T> = { [K in keyof T]: T[K] };
const c: Copy<A> = {}; // still optional: OK
// To remove it, write -?
```

❌ Mistake 3: Mutating a readonly mapped result
```typescript
// ❌ Wrong
type RO<T> = { readonly [K in keyof T]: T[K] };
const o: RO<{ n: number }> = { n: 1 };
o.n = 2;
// error TS2540: Cannot assign to 'n' because it is a read-only property.
```

---

## 🧠 Tricky Interview Question

```typescript
type Mystery<T> = { [K in keyof T]: T[K] };
type R = Mystery<[string, number]>;
type S = Mystery<{ a?: string }>;
```
**What are `R` and `S`?**

Answer: `R` is `[string, number]`, a tuple, not an object. Homomorphic mapped types over arrays and tuples map element-wise and keep the tuple shape. `S` is `{ a?: string }`; the optional modifier is preserved because `keyof T` makes the mapped type homomorphic. Compare `{ [K in "a"]: string }`, which has no such copying. Also note: homomorphic mapped types distribute over unions of object types.

---

## ⚫ Interview Questions + Answers

Q1: What is a mapped type, and give an example from the standard library?
A1: A type that loops over keys with `[K in Keys]`. `Partial<T> = { [K in keyof T]?: T[K] }`, `Readonly<T>`, `Pick<T, K> = { [P in K]: T[P] }` and `Record<K, V> = { [P in K]: V }` are all mapped types.

Q2: How do `-?` and `-readonly` work?
A2: `-?` removes the optional flag (so `T[K]` no longer includes `undefined` from optionality) and `-readonly` removes readonly. `+` is the default prefix. `Required<T>` is `{ [K in keyof T]-?: T[K] }`.

Q3: What is key remapping with `as` and what is it used for?
A3: TS 4.1 lets you rename keys: `{ [K in keyof T as `get${Capitalize<K & string>}`]: () => T[K] }`. If the `as` clause yields `never`, the key is dropped, which gives filtering (`OmitByType`). Without `as`, `Omit` has to use `Pick<T, Exclude<keyof T, K>>`.

Q4: What does "homomorphic" mean here?
A4: A mapped type of the form `{ [K in keyof T]: ... }` where T is a type parameter. It preserves modifiers (`?`, `readonly`) of the original, maps arrays and tuples element by element, and distributes over unions.

Q5: What are the performance and readability caveats?
A5: Deeply recursive mapped types (like `DeepPartial` on huge generated types) can slow the compiler and hit "Type instantiation is excessively deep" (TS2589). Hover output may show the expanded shape, which is hard to read; wrap with a named alias and keep each mapping small.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Deriving form state, error maps, DTOs, getters/handlers from one model
- Making all or some fields optional/readonly/nullable
- Renaming or filtering keys (camelCase conversion, event handler maps)

❌ Avoid when:
- A built-in utility (`Partial`, `Pick`, `Omit`) already does it
- You only need two or three fields; a plain interface is simpler
- The recursion depth is large and slows editor feedback

---

## 📊 Visual Diagram
```
  type Getters<T> = { [K in keyof T as `get${Capitalize<K & string>}`]: () => T[K] }

   Order                       loop over keys                Getters<Order>
  ┌──────────────┐            ┌──────────────────┐         ┌─────────────────────────┐
  │ id: string   │ ─ K="id" ─►│ get + Id         │────────►│ getId: () => string     │
  │ amount: number│─ K="amount"►│ get + Amount     │────────►│ getAmount: () => number │
  └──────────────┘            └──────────────────┘         └─────────────────────────┘

  modifiers:  +readonly  -readonly  +?  -?      filter: as never  → key removed
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Mapped type | Type built by looping keys | Keys पर loop से बना type |
| Homomorphic | Uses `in keyof T`, keeps modifiers | Modifiers बचाने वाला mapping |
| Modifier | `readonly` or `?` | readonly / optional चिन्ह |
| Key remapping | Rename keys with `as` | `as` से key का नाम बदलना |
| Filtering | Map key to `never` to drop | Key को `never` कर के हटाना |

---

## ⚡ 3-Line Summary
English:
1. A mapped type `{ [K in keyof T]: ... }` derives a new type by transforming every property of T.
2. `+/-readonly`, `+/-?` change modifiers and `as` renames or filters keys (TS 4.1+).
3. Partial, Required, Readonly, Pick and Record are all mapped types, so one model can drive forms, errors and DTOs.

Hindi:
1. Mapped type `{ [K in keyof T]: ... }` T की हर property को transform करके नया type बनाता है।
2. `+/-readonly`, `+/-?` modifiers बदलते हैं और `as` keys का नाम बदलता या filter करता है (TS 4.1+)।
3. Partial, Required, Readonly, Pick, Record सब mapped types हैं, इसलिए एक model से forms, errors और DTOs derive होते हैं।

---

## ➡️ Next Topic
**48. Conditional Types** — `T extends U ? X : Y` से type-level if/else लिखना।
