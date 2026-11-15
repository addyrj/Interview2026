# 55. Utility Types — Exclude, Extract, NonNullable
# हिंदी में: Utility Types — Exclude, Extract, NonNullable

> TypeScript 5.x पर verify किया गया (`tsc --strict`, TS 5.9). `Exclude`/`Extract` TS 2.8 से। `NonNullable<T>` TS 4.8 से `T & {}` के रूप में define है (पहले conditional type था)।

---

## 🔵 Simple Definition (English)
These utilities **filter union types**. `Exclude<T, U>` removes from `T` every member assignable to `U`. `Extract<T, U>` keeps only the members of `T` assignable to `U`. `NonNullable<T>` removes `null` and `undefined`. All three are built on distributive conditional types.

## 🔵 सरल परिभाषा (Hindi)
ये utilities **union types को filter** करते हैं। `Exclude<T, U>` `T` के वे सारे members हटाता है जो `U` को assignable हैं। `Extract<T, U>` सिर्फ वही members रखता है जो `U` को assignable हैं। `NonNullable<T>` `null` और `undefined` हटाता है। तीनों distributive conditional types पर बने हैं।

---

## 🔴 Problem it Solves
A payment method union is `"UPI" | "CARD" | "NETBANKING" | "COD"`. The online gateway only supports the first three; COD is handled separately. Re-typing the subset duplicates and drifts. An API field `user?: User | null` needs a version that is definitely present after a check. A union of actions must be narrowed to "only actions with a payload". These utilities derive subsets from the full union.

## 🔴 यह क्यों बना? (Hindi)
Payment method union है `"UPI" | "CARD" | "NETBANKING" | "COD"`। Online gateway सिर्फ पहले तीन support करता है; COD अलग संभलता है। Subset को दोबारा लिखने पर duplicate और drift होता है। API field `user?: User | null` का वह version चाहिए जो check के बाद पक्का मौजूद हो। Actions के union से "सिर्फ payload वाले actions" निकालने हैं। ये utilities पूरे union से subsets निकालते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `Exclude<T, U> = T extends U ? never : T`. Distributes over the union `T`; members assignable to `U` become `never` (vanish).
Step 2 → `Extract<T, U> = T extends U ? T : never`. The opposite: keep matching members.
Step 3 → `NonNullable<T> = T & {}` (TS 4.8+). Intersecting with `{}` removes `null`/`undefined`; earlier versions used `T extends null | undefined ? never : T`.
Step 4 → `U` can be a type, not just literals: `Extract<Event, { type: "paid" }>` picks the object member with `type: "paid"`; `Exclude<T, Function>` removes functions.
Step 5 → `Exclude` removes members, it does not remove **properties**; for properties use `Omit`.
Step 6 → After a runtime check (`if (x != null)`), TS narrows automatically; use `NonNullable` for **declaring** types, e.g. return type of a function that guarantees presence.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `Exclude<T, U> = T extends U ? never : T`। Union `T` पर distribute होता है; जो members `U` को assignable हैं वे `never` बनकर गायब।
Step 2 → `Extract<T, U> = T extends U ? T : never`। उल्टा: match होने वाले members रखो।
Step 3 → `NonNullable<T> = T & {}` (TS 4.8+)। `{}` से intersect करने पर `null`/`undefined` हट जाते हैं।
Step 4 → `U` सिर्फ literals नहीं, कोई भी type हो सकता है: `Extract<Event, { type: "paid" }>` वह object member चुनता है।
Step 5 → `Exclude` members हटाता है, **properties** नहीं; properties के लिए `Omit` है।
Step 6 → Runtime check (`if (x != null)`) के बाद TS खुद narrow करता है; `NonNullable` types **declare** करते समय काम आता है।

---

## 🟡 Real World Example
**Swiggy's** order events are a discriminated union: `Placed | Accepted | PickedUp | Delivered | Cancelled`. A "live tracking" screen only reacts to `Extract<OrderEvent, { type: "PickedUp" | "Delivered" }>`. A refund service handles `Exclude<OrderEvent, { type: "Placed" }>`. For user profiles, `NonNullable<Profile["phone"]>` gives the `string` type after the app verified the phone exists.

## 🟡 Real Example Hindi mein
**Swiggy** के order events एक discriminated union हैं: `Placed | Accepted | PickedUp | Delivered | Cancelled`। "Live tracking" screen सिर्फ `Extract<OrderEvent, { type: "PickedUp" | "Delivered" }>` पर react करती है। Refund service `Exclude<OrderEvent, { type: "Placed" }>` संभालती है। User profile में `NonNullable<Profile["phone"]>` वह `string` type देता है जब app verify कर ले कि phone है।

---

## 💻 Code Example — Basic

```typescript
// A union of payment methods
type Method = "UPI" | "CARD" | "NETBANKING" | "COD";

// Exclude: remove members
type Online = Exclude<Method, "COD">; // "UPI" | "CARD" | "NETBANKING"
const o: Online = "UPI";

// Extract: keep only members assignable to the second argument
type Cashless = Extract<Method, "UPI" | "CARD" | "WALLET">; // "UPI" | "CARD" (WALLET is not in Method)
const c: Cashless = "CARD";

// NonNullable: drop null and undefined
type MaybePhone = string | null | undefined;
type Phone = NonNullable<MaybePhone>; // string
const p: Phone = "9876543210";

// Works on mixed unions too
type Mixed = string | number | boolean | (() => void);
type NoFn = Exclude<Mixed, Function>; // string | number | boolean
type OnlyStr = Extract<Mixed, string>; // string
const n: NoFn = 5;
const s: OnlyStr = "x";

console.log(o, c, p, n, s); // UPI CARD 9876543210 5 x
```

## 💻 Code Example — Advanced

```typescript
// Advanced 1: filter a discriminated union by its tag
type OrderEvent =
  | { type: "PLACED"; id: string }
  | { type: "PICKED_UP"; id: string; rider: string }
  | { type: "DELIVERED"; id: string; at: number }
  | { type: "CANCELLED"; id: string; reason: string };

type Live = Extract<OrderEvent, { type: "PICKED_UP" | "DELIVERED" }>; // two members remain
function track(e: Live): string {
  return e.type === "PICKED_UP" ? `Rider ${e.rider}` : `Delivered at ${e.at}`; // narrowing still works
}
console.log(track({ type: "PICKED_UP", id: "o1", rider: "Ravi" })); // Rider Ravi

type NotCancelled = Exclude<OrderEvent, { type: "CANCELLED" }>; // three members
const nc: NotCancelled = { type: "PLACED", id: "o2" };

// Advanced 2: a reusable ByType helper using Extract
type ByType<U extends { type: string }, T extends U["type"]> = Extract<U, { type: T }>;
type Delivered = ByType<OrderEvent, "DELIVERED">; // { type: "DELIVERED"; id; at }
const d: Delivered = { type: "DELIVERED", id: "o3", at: 1700000000 };

// Advanced 3: keys filtered by value type (Extract on keys)
interface Product { id: number; name: string; price: number; tags: string[] }
type NumericKeys = { [K in keyof Product]: Product[K] extends number ? K : never }[keyof Product]; // "id" | "price"
type StringKeys = Extract<keyof Product, "name" | "tags" | "sku">; // "name" | "tags"
const nk: NumericKeys = "price";
const sk: StringKeys = "name";

// Advanced 4: NonNullable on nested, and a typed filter(Boolean) helper
function compact<T>(xs: readonly T[]): NonNullable<T>[] {
  return xs.filter((x): x is NonNullable<T> => x != null); // type guard keeps the type honest
}
const ids = compact([1, null, 3, undefined]); // number[]
console.log(nc.type, d.at, nk, sk, ids); // PLACED 1700000000 price name [ 1, 3 ]
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: separate online and cash handlers by narrowing the method type
import express from "express";

type Method = "UPI" | "CARD" | "COD";
type OnlineMethod = Exclude<Method, "COD">;

function payOnline(m: OnlineMethod, amount: number): string {
  return `charged ${amount} via ${m} gateway`; // COD cannot reach here
}
function isOnline(m: Method): m is OnlineMethod {
  return m !== "COD"; // runtime check matching the type
}

const app = express();
app.use(express.json());
app.post("/pay", (req, res) => {
  const { method, amount } = req.body as { method: Method; amount: number }; // validate in real code
  res.json({ msg: isOnline(method) ? payOnline(method, amount) : "pay cash on delivery" });
});
```

```tsx
// React: props that must not be null after a loading gate (NonNullable)
import { useState } from "react";

interface User { name: string; phone: string | null }

function PhoneBadge({ phone }: { phone: NonNullable<User["phone"]> }) {
  return <span>{phone}</span>; // phone is string here, no null check needed
}

export function Profile({ user }: { user: User }) {
  const [shown] = useState(true);
  return shown && user.phone ? <PhoneBadge phone={user.phone} /> : <span>No phone</span>; // narrowing at call site
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `Exclude` to remove object properties
```typescript
interface User { id: number; password: string }
type Wrong = Exclude<User, { password: string }>; // never! the whole member is excluded, not the property
const w: Wrong = { id: 1 }; // ❌
// error TS2322: Type '{ id: number; }' is not assignable to type 'never'.
// ✅ Right: Omit<User, "password">
```

❌ Mistake 2: Assigning a removed member
```typescript
type Method = "UPI" | "CARD" | "COD";
const m: Exclude<Method, "COD"> = "COD"; // ❌
// error TS2322: Type '"COD"' is not assignable to type '"UPI" | "CARD"'.
```

❌ Mistake 3: Thinking `NonNullable` removes optionality of a property
```typescript
interface Form { phone?: string | null }
type P = NonNullable<Form["phone"]>; // string (index access gives string | null | undefined; NonNullable gives string)
type F = NonNullable<Form>; // still { phone?: string | null }: it is the object, which is not null
const f: F = {}; // OK: use Required<Form> for properties
```

---

## 🧠 Tricky Interview Question

```typescript
type T1 = Extract<string | number | (() => void), Function>;
type T2 = Exclude<"a" | "b" | "c", "a" | "z">;
type T3 = NonNullable<string | null | undefined | 0>;
```
**What are T1, T2, T3?**

Answer: `T1 = () => void` (the only member assignable to `Function`). `T2 = "b" | "c"` (`"z"` is just ignored because Exclude only removes members that actually exist). `T3 = string | 0`, since `NonNullable` removes only `null` and `undefined`, not falsy values like `0` or `""`. Common trap: people think `NonNullable` is the same as "truthy". Also remember `NonNullable<T> = T & {}` in TS 4.8+, which also makes `NonNullable<unknown>` equal `{}`.

---

## ⚫ Interview Questions + Answers

Q1: How are `Exclude` and `Extract` implemented?
A1: `type Exclude<T, U> = T extends U ? never : T` and `type Extract<T, U> = T extends U ? T : never`. They work because conditional types distribute over naked union type parameters.

Q2: What is the difference between `Exclude` and `Omit`?
A2: `Exclude` filters **members of a union**. `Omit` removes **properties of an object type**. `Omit` is implemented using `Exclude` on `keyof T` plus `Pick`.

Q3: How has `NonNullable` changed in recent TypeScript?
A3: Before TS 4.8: `T extends null | undefined ? never : T`. Since 4.8: `T & {}`, which improved narrowing (`NonNullable<T>` for a generic `T` now narrows inside `if (x != null)`). Behaviour for concrete unions is the same.

Q4: How do you get one variant out of a discriminated union?
A4: `Extract<Union, { type: "x" }>`. Works because the object member is assignable to `{ type: "x" }`. This also covers Redux action unions, e.g. `Extract<Action, { type: "cart/add" }>["payload"]`.

Q5: How would you implement "remove null from every property" (a `NonNullableFields<T>`)?
A5: `type NonNullableFields<T> = { [K in keyof T]: NonNullable<T[K]> }`. A mapped type applying `NonNullable` per property; add `-?` to also make them required.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Deriving subsets of a union (supported methods, event subtypes, permitted roles)
- Declaring "definitely present" types after a validation step
- Building helpers like `ByType`, `OmitByType`

❌ Avoid when:
- You want to remove properties (use `Omit`)
- A simple runtime guard with narrowing is enough
- You would end up listing the subset anyway; a named union can be clearer

---

## 📊 Visual Diagram
```
  Method = UPI | CARD | NETBANKING | COD

  Exclude<Method, "COD">     ──►  UPI | CARD | NETBANKING        (remove)
  Extract<Method, "UPI"|"COD"> ──► UPI | COD                      (keep)
  NonNullable<string|null>   ──►  string                         (drop null/undefined)

  Distribution:  Exclude<A|B|C, A>  =  Excl<A> | Excl<B> | Excl<C>
                                    =   never  |    B     |    C
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Exclude | Remove union members | Union के members हटाना |
| Extract | Keep matching members | Match वाले members रखना |
| NonNullable | Remove null/undefined | null/undefined हटाना |
| Distributive | Applied per member | हर member पर अलग |
| Discriminated union | Union with tag field | Tag field वाला union |

---

## ⚡ 3-Line Summary
English:
1. `Exclude` removes union members, `Extract` keeps matching ones, `NonNullable` drops `null` and `undefined`.
2. They are distributive conditional types; use `Omit` (not `Exclude`) to remove object properties.
3. `Extract<Union, { type: "x" }>` is the easy way to pick one variant of a discriminated union.

Hindi:
1. `Exclude` union members हटाता है, `Extract` match वाले रखता है, `NonNullable` `null` और `undefined` हटाता है।
2. ये distributive conditional types हैं; object properties हटाने के लिए `Exclude` नहीं `Omit` चाहिए।
3. Discriminated union का एक variant चुनने का आसान तरीका `Extract<Union, { type: "x" }>` है।

---

## ➡️ Next Topic
**56. Utility Types — ReturnType, Parameters, ConstructorParameters, InstanceType** — functions और classes से types निकालना।
