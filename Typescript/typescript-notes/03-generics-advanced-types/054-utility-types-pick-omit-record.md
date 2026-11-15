# 54. Utility Types — Pick, Omit, Record
# हिंदी में: Utility Types — Pick, Omit, Record

> TypeScript 5.x पर verify किया गया (`tsc --strict`, TS 5.9). `Pick`/`Record` TS 2.1 से, `Omit` TS 3.5 से।

---

## 🔵 Simple Definition (English)
`Pick<T, K>` builds a type with **only** the keys `K` of `T`. `Omit<T, K>` builds a type with **all keys except** `K`. `Record<K, V>` builds an object type whose keys are `K` and whose values are all `V`. They derive DTOs, view models and typed lookup maps from one source type.

## 🔵 सरल परिभाषा (Hindi)
`Pick<T, K>` `T` की **सिर्फ** चुनी हुई keys `K` वाला type बनाता है। `Omit<T, K>` `K` को छोड़कर **बाकी सब keys** वाला type। `Record<K, V>` ऐसा object type जिसकी keys `K` और values सब `V` हैं। ये एक source type से DTOs, view models और typed lookup maps निकालते हैं।

---

## 🔴 Problem it Solves
Your SQL Server `User` row has `passwordHash`, `internalNotes`, `createdAt`. The API must never return the hash. The login form only needs `email` and `password`. A dropdown needs `id` and `name`. Copy-pasting each shape creates drift. Also, a lookup such as "status to colour" typed as `{ [key: string]: string }` accepts missing statuses silently. These three utilities solve both.

## 🔴 यह क्यों बना? (Hindi)
आपकी SQL Server `User` row में `passwordHash`, `internalNotes`, `createdAt` हैं। API को hash कभी नहीं लौटाना। Login form को सिर्फ `email` और `password` चाहिए। Dropdown को `id` और `name`। हर shape copy-paste करने से drift होता है। साथ ही "status से colour" lookup को `{ [key: string]: string }` टाइप करने पर कोई status छूट जाए तो पता नहीं चलता। ये तीन utilities दोनों समस्याएँ हल करते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `Pick<T, K extends keyof T> = { [P in K]: T[P] }`. K must be keys of T, otherwise TS2344.
Step 2 → `Omit<T, K extends keyof any> = Pick<T, Exclude<keyof T, K>>`. Note K is **not** checked against `keyof T`, so typos in `Omit` keys do NOT error (a known gotcha).
Step 3 → `Record<K extends keyof any, T> = { [P in K]: T }`. With a literal union for `K` TypeScript forces **every** key to exist (exhaustive map). With `string` it is just an index signature.
Step 4 → Both `Pick` and `Omit` preserve optional/readonly modifiers (they are homomorphic via `Pick`).
Step 5 → `Omit` on a union type does not distribute: `Omit<A | B, "x">` collapses to common keys. Use a distributive version `T extends unknown ? Omit<T, K> : never`.
Step 6 → With `noUncheckedIndexedAccess`, `Record<string, V>[k]` is `V | undefined`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `Pick<T, K extends keyof T> = { [P in K]: T[P] }`। K, T की keys होनी चाहिए, नहीं तो TS2344।
Step 2 → `Omit<T, K extends keyof any> = Pick<T, Exclude<keyof T, K>>`। ध्यान दो: K की जाँच `keyof T` से **नहीं** होती, इसलिए `Omit` में typo error नहीं देता (मशहूर gotcha)।
Step 3 → `Record<K, V>` = `{ [P in K]: V }`। K literal union हो तो **हर** key मौजूद होनी चाहिए (exhaustive map)। K `string` हो तो बस index signature।
Step 4 → `Pick` और `Omit` optional/readonly modifiers बचाए रखते हैं।
Step 5 → Union पर `Omit` distribute नहीं होता; distributive version लिखो।
Step 6 → `noUncheckedIndexedAccess` में `Record<string, V>[k]` का type `V | undefined` होता है।

---

## 🟡 Real World Example
**Paytm's** user service: the DB entity `UserEntity` has 15 columns. `PublicUser = Omit<UserEntity, "passwordHash" | "pan" | "internalNotes">` is returned from APIs. `UserCard = Pick<UserEntity, "id" | "name" | "avatarUrl">` feeds a React list. `Record<TxnStatus, string>` maps `"SUCCESS" | "FAILED" | "PENDING"` to a badge colour; adding a new status `"REFUNDED"` immediately breaks that map until a colour is added, so no status is ever unstyled.

## 🟡 Real Example Hindi mein
**Paytm** की user service: DB entity `UserEntity` में 15 columns हैं। `PublicUser = Omit<UserEntity, "passwordHash" | "pan" | "internalNotes">` APIs से लौटता है। `UserCard = Pick<UserEntity, "id" | "name" | "avatarUrl">` React list को feed करता है। `Record<TxnStatus, string>` `"SUCCESS" | "FAILED" | "PENDING"` को badge colour से map करता है; नया status `"REFUNDED"` जोड़ते ही map टूट जाता है जब तक colour न जुड़े, इसलिए कोई status बिना style नहीं रहता।

---

## 💻 Code Example — Basic

```typescript
// Full entity as stored in SQL Server
interface UserEntity {
  id: number; // PK
  name: string; // name
  email: string; // email
  passwordHash: string; // never expose
  createdAt: Date; // audit
}

// Pick: keep only chosen keys
type UserCard = Pick<UserEntity, "id" | "name">;
const card: UserCard = { id: 1, name: "Asha" };

// Omit: drop sensitive keys
type PublicUser = Omit<UserEntity, "passwordHash">;
const pub: PublicUser = { id: 1, name: "Asha", email: "a@x.in", createdAt: new Date(0) };

// Record: one value per key
type Status = "SUCCESS" | "FAILED" | "PENDING";
const badge: Record<Status, string> = {
  SUCCESS: "green", // every status must be present
  FAILED: "red",
  PENDING: "orange",
};

// Record with string keys is a dictionary
const stock: Record<string, number> = { biryani: 12, dosa: 30 };
stock["pizza"] = 5; // adding a new key is fine

console.log(card.name, pub.email, badge.FAILED, Object.keys(stock).length); // Asha a@x.in red 3
```

## 💻 Code Example — Advanced

```typescript
// Advanced 1: build from scratch (interview classic)
type MyPick<T, K extends keyof T> = { [P in K]: T[P] };
type MyOmit<T, K extends keyof any> = Pick<T, Exclude<keyof T, K>>;
type MyRecord<K extends keyof any, V> = { [P in K]: V };

interface Cart { id: string; items: number; total: number }
type A = MyPick<Cart, "id" | "total">; // { id; total }
type B = MyOmit<Cart, "items">; // { id; total }
const a: A = { id: "c1", total: 100 };
const b: B = { id: "c1", total: 100 };

// Advanced 2: Omit does not check keys: a typo silently does nothing
type Oops = Omit<Cart, "itemz">; // compiles! still has items
const oops: Oops = { id: "c1", items: 2, total: 5 };
// Safer version: K must be keyof T
type StrictOmit<T, K extends keyof T> = Omit<T, K>;
type Ok = StrictOmit<Cart, "items">; // StrictOmit<Cart, "itemz"> would be an error

// Advanced 3: distributive Omit for unions (discriminated unions)
type DistOmit<T, K extends PropertyKey> = T extends unknown ? Omit<T, K> : never;
type Event =
  | { type: "paid"; id: string; amount: number }
  | { type: "failed"; id: string; reason: string };
type EventInput = DistOmit<Event, "id">; // each member loses id, keeps its own fields
const ei: EventInput = { type: "failed", reason: "declined" }; // reason still available
// With plain Omit<Event, "id"> the union collapses to just { type: ... }

// Advanced 4: Record with a mapped enum-like object, exhaustive handlers
const METHODS = ["UPI", "CARD", "COD"] as const;
type Method = (typeof METHODS)[number];
const fee: Record<Method, (amt: number) => number> = {
  UPI: () => 0, // no fee
  CARD: (amt) => Math.round(amt * 0.02), // 2 percent
  COD: () => 30, // flat
};
console.log(a.id, b.total, oops.items, ei, fee.CARD(1000)); // c1 100 2 { type: 'failed', reason: 'declined' } 20
console.log({} as Ok); // {}
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: never leak the hash; build DTOs with Omit and Pick
import express from "express";

interface UserEntity {
  id: number; // PK
  email: string; // email
  passwordHash: string; // secret
}
type PublicUser = Omit<UserEntity, "passwordHash">;
type CreateUserBody = Pick<UserEntity, "email"> & { password: string }; // input shape

const db: UserEntity[] = [{ id: 1, email: "a@x.in", passwordHash: "xxx" }];
const toPublic = ({ passwordHash: _h, ...rest }: UserEntity): PublicUser => rest; // strip

const app = express();
app.use(express.json());
app.get("/users/:id", (req, res) => {
  const u = db.find((x) => x.id === Number(req.params.id));
  if (!u) { res.status(404).end(); return; } // not found
  res.json(toPublic(u)); // typed PublicUser
});
app.post("/users", (req, res) => {
  const body = req.body as CreateUserBody; // validate with Zod in real code
  res.status(201).json({ email: body.email });
});
```

```tsx
// React: exhaustive status-to-style map with Record, props with Pick
type Status = "SUCCESS" | "FAILED" | "PENDING";
interface Txn { id: string; status: Status; amount: number; internalRef: string }

const colour: Record<Status, string> = { SUCCESS: "green", FAILED: "red", PENDING: "orange" }; // exhaustive

type RowProps = Pick<Txn, "id" | "status" | "amount">; // only what the row needs
export const TxnRow = ({ id, status, amount }: RowProps) => (
  <li style={{ color: colour[status] }}>{id}: {amount}</li>
);
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Picking a key that does not exist
```typescript
// ❌ Wrong
interface User { id: number; name: string }
type Bad = Pick<User, "id" | "email">;
// error TS2344: Type '"id" | "email"' does not satisfy the constraint 'keyof User'.
//   Type '"email"' is not assignable to type 'keyof User'.
```

❌ Mistake 2: Missing a key in an exhaustive `Record`
```typescript
// ❌ Wrong
type Status = "SUCCESS" | "FAILED" | "PENDING";
const colours: Record<Status, string> = { SUCCESS: "green", FAILED: "red" };
// error TS2741: Property 'PENDING' is missing in type '{ SUCCESS: string; FAILED: string; }' but required in type 'Record<Status, string>'.
```

❌ Mistake 3: Trusting `Omit` to catch typos
```typescript
interface User { id: number; passwordHash: string }
type Leaky = Omit<User, "passwordhash">; // lowercase h: compiles, and passwordHash is STILL there
const leak: Leaky = { id: 1, passwordHash: "secret" }; // the secret is exposed to API consumers
// ✅ Right: StrictOmit<T, K extends keyof T> = Omit<T, K>
```

---

## 🧠 Tricky Interview Question

```typescript
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "square"; side: number };
type NoKind = Omit<Shape, "kind">;
```
**What is `NoKind`?**

Answer: `{}`. `Omit<T, K>` uses `keyof T`, and for a union `keyof (A | B)` is only the **common** keys (`"kind"`). After removing `kind`, no keys remain, so the result is `{}`; `radius` and `side` are lost. Fix with a distributive omit: `type DistOmit<T, K extends PropertyKey> = T extends unknown ? Omit<T, K> : never`. This is the classic "why did my union lose its fields" interview trap.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `Pick` and `Omit`?
A1: `Pick` is an allowlist (keep these keys), `Omit` is a denylist (drop these keys). Use `Pick` for small views, `Omit` when you want almost everything. With `Omit`, new fields added later automatically flow through, which can leak data, so for security-sensitive DTOs prefer `Pick`.

Q2: Why does `Omit<User, "typo">` not error?
A2: `Omit`'s constraint is `K extends keyof any` (`string | number | symbol`), not `keyof T`, so any key is accepted. Write your own `StrictOmit` if you want checking.

Q3: What is `Record<K, V>` and how is it better than an index signature?
A3: A mapped type `{ [P in K]: V }`. With a union of literals as `K` it demands every key (exhaustive), catches missing cases when the union grows, and gives autocomplete. An index signature accepts any string key.

Q4: How do you make `Omit` work on a union?
A4: Distribute it with a conditional type: `T extends unknown ? Omit<T, K> : never`.

Q5: Implement `Pick` and `Record` from scratch.
A5: `type MyPick<T, K extends keyof T> = { [P in K]: T[P] }` and `type MyRecord<K extends keyof any, V> = { [P in K]: V }`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Deriving API DTOs, form types, list-item props from one entity
- Exhaustive lookup tables keyed by a union (`Record<Status, ...>`)
- Removing server-only fields from client-facing types

❌ Avoid when:
- Security allowlists using `Omit`; new sensitive fields leak automatically (use `Pick` or an explicit DTO class/Zod schema)
- The derived shape is very different; define a separate interface
- Unions without a distributive wrapper

---

## 📊 Visual Diagram
```
   UserEntity { id, name, email, passwordHash }

   Pick<UserEntity, "id"|"name">        ──► { id, name }                 (allowlist)
   Omit<UserEntity, "passwordHash">     ──► { id, name, email }          (denylist)
   Record<"A"|"B", number>              ──► { A: number; B: number }     (map)

   Omit<K> = Pick< T, Exclude<keyof T, K> >
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pick | Keep selected keys | चुनी हुई keys रखना |
| Omit | Remove selected keys | चुनी हुई keys हटाना |
| Record | Map keys to value type | Keys से value type का map |
| DTO | Data transfer object | Data भेजने वाला shape |
| Exhaustive | Every case present | हर case मौजूद |

---

## ⚡ 3-Line Summary
English:
1. `Pick` keeps chosen keys, `Omit` drops them, `Record<K, V>` maps every key in K to V.
2. `Omit` does not validate keys and does not distribute over unions; wrap it when needed.
3. Use `Record<Union, X>` for exhaustive maps and `Pick` for safe public DTOs.

Hindi:
1. `Pick` चुनी keys रखता है, `Omit` हटाता है, `Record<K, V>` K की हर key को V से map करता है।
2. `Omit` keys validate नहीं करता और unions पर distribute नहीं होता; ज़रूरत हो तो wrap करो।
3. Exhaustive maps के लिए `Record<Union, X>` और सुरक्षित public DTOs के लिए `Pick` इस्तेमाल करो।

---

## ➡️ Next Topic
**55. Utility Types — Exclude, Extract, NonNullable** — unions को filter करना और `null`/`undefined` हटाना।
