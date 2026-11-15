# 31. keyof Operator
# हिंदी में: `keyof` Operator (object की keys का union type)

> Verified with TypeScript 5.x (5.9) under `tsc --strict`.

---

## 🔵 Simple Definition (English)
`keyof T` produces a **union of the property names** of type `T` as string (or number/symbol) literal types. For `{ id: number; name: string }`, `keyof` gives `"id" | "name"`. It works on types only, and is the basis of safe property access, mapped types and most utility types.

## 🔵 सरल परिभाषा (Hindi)
`keyof T` type `T` की **property names का union** बनाता है, string (या number/symbol) literal types के रूप में। `{ id: number; name: string }` के लिए `keyof` का नतीजा `"id" | "name"` है। यह सिर्फ़ types पर काम करता है, और safe property access, mapped types और ज़्यादातर utility types की बुनियाद है।

---

## 🔴 Problem it Solves
Functions like `getField(obj, "name")`, `sortBy(rows, "price")` and `updateField(form, "email", value)` take a key as a string. If the parameter is plain `string`, typos like `"pirce"` compile and return `undefined`. With `keyof`, only real keys are accepted, and rename-refactors update everywhere.

## 🔴 यह क्यों बना? (Hindi)
`getField(obj, "name")`, `sortBy(rows, "price")` और `updateField(form, "email", value)` जैसे functions key को string के रूप में लेते हैं। Parameter सादा `string` हो तो `"pirce"` जैसी typo compile हो जाती है और `undefined` लौटता है। `keyof` से सिर्फ़ असली keys स्वीकार होती हैं, और rename-refactor हर जगह update हो जाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `type K = keyof Order` gives the union of Order's property names.
Step 2 → Use it for parameters: `function pick(o: Order, k: keyof Order)`.
Step 3 → To make the RETURN type precise, use a generic: `function get<T, K extends keyof T>(o: T, k: K): T[K]` (indexed access, next notes).
Step 4 → `keyof` of a type with a string index signature `{ [k: string]: X }` is `string | number` (numbers are valid keys in JS).
Step 5 → `keyof any` is `string | number | symbol` = `PropertyKey`.
Step 6 → `keyof (A | B)` = keys common to both; `keyof (A & B)` = keys of either (union of keys).
Step 7 → `Object.keys(obj)` returns `string[]`, NOT `(keyof T)[]`, on purpose (objects can have extra runtime keys). Cast knowingly or use a typed helper.
Step 8 → `keyof typeof value` gets the keys of a runtime object (next topic, 32).

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → `type K = keyof Order` Order की property names का union देता है।
Step 2 → Parameters के लिए इस्तेमाल करो: `function pick(o: Order, k: keyof Order)`।
Step 3 → RETURN type सही करने के लिए generic लो: `function get<T, K extends keyof T>(o: T, k: K): T[K]` (indexed access, आगे के notes में)।
Step 4 → String index signature `{ [k: string]: X }` वाले type का `keyof` `string | number` होता है (JS में numbers भी valid keys हैं)।
Step 5 → `keyof any` = `string | number | symbol` = `PropertyKey`।
Step 6 → `keyof (A | B)` = दोनों की common keys; `keyof (A & B)` = किसी की भी keys (keys का union)।
Step 7 → `Object.keys(obj)` `string[]` लौटाता है, `(keyof T)[]` नहीं, जानबूझकर (runtime पर extra keys हो सकती हैं)। सोच-समझकर cast करो या typed helper बनाओ।
Step 8 → Runtime object की keys के लिए `keyof typeof value` (अगला topic, 32)।

---

## 🟡 Real World Example
**Zomato restaurant list sorting**: the UI lets users sort by `rating`, `deliveryTime` or `price`. `sortBy(restaurants, "rating")` uses `keyof Restaurant`, so the dropdown values are checked by the compiler and `"ratng"` is a build error.

## 🟡 Real Example Hindi mein
**Zomato restaurant list sorting**: UI में user `rating`, `deliveryTime` या `price` से sort कर सकता है। `sortBy(restaurants, "rating")` `keyof Restaurant` इस्तेमाल करता है, इसलिए dropdown की values compiler जाँचता है और `"ratng"` build error बन जाता है।

---

## 💻 Code Example — Basic

```typescript
// Domain type
interface Restaurant {
  id: number; // numeric id
  name: string; // display name
  rating: number; // 0..5
}

// keyof gives the union of property names
type RestaurantKey = keyof Restaurant; // "id" | "name" | "rating"

// Parameter restricted to real keys
function describe(r: Restaurant, key: RestaurantKey): string {
  return `${key} = ${r[key]}`; // r[key] type: string | number (union of value types)
}

const r: Restaurant = { id: 1, name: "Biryani House", rating: 4.5 }; // sample
console.log(describe(r, "name")); // valid key
console.log(describe(r, "rating")); // valid key
```

Run with `npx tsx`:

```
name = Biryani House
rating = 4.5
```

```typescript
// ❌ A typo is now a compile error
interface Restaurant { id: number; name: string; rating: number } // shape
function pick(r: Restaurant, key: keyof Restaurant): unknown { return r[key]; } // typed key
const r: Restaurant = { id: 1, name: "A", rating: 4 }; // value
pick(r, "ratng"); // ❌ typo
```

Real compiler output:

```
error TS2345: Argument of type '"ratng"' is not assignable to parameter of type 'keyof Restaurant'.
```

## 💻 Code Example — Advanced

```typescript
// Advanced: generic get/set with K extends keyof T, typed sortBy, and a typed Object.keys

// Precise return type: T[K] is the type of THAT property
function get<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key]; // returns exactly the property's type
}

// Type-safe setter: value must match the property's type
function set<T, K extends keyof T>(obj: T, key: K, value: T[K]): void {
  obj[key] = value; // allowed because value is T[K]
}

interface Order { id: number; status: "paid" | "pending"; amount: number } // order
const o: Order = { id: 9, status: "pending", amount: 499 }; // sample

const amount = get(o, "amount"); // type number (not string | number | ...)
set(o, "status", "paid"); // value must be "paid" | "pending"
console.log(amount, o.status); // 499 paid

// Sort any array by a key whose value is number or string
function sortBy<T, K extends keyof T>(rows: T[], key: K): T[] {
  return [...rows].sort((a, b) => (a[key] < b[key] ? -1 : a[key] > b[key] ? 1 : 0)); // generic compare
}
const sorted = sortBy([{ n: "b", p: 2 }, { n: "a", p: 3 }], "n"); // sort by name
console.log(sorted.map((x) => x.n).join(",")); // a,b

// keyof with only keys whose VALUE is a number (key remapping + indexed access)
type NumericKeys<T> = { [K in keyof T]: T[K] extends number ? K : never }[keyof T]; // filter keys
type OrderNumeric = NumericKeys<Order>; // "id" | "amount"
const nk: OrderNumeric = "amount"; // valid
console.log(nk);

// Typed Object.keys helper (use only when you know the object has no extra keys)
function typedKeys<T extends object>(o: T): (keyof T)[] {
  return Object.keys(o) as (keyof T)[]; // deliberate cast
}
console.log(typedKeys(o)); // [ 'id', 'status', 'amount' ]
```

Run with `npx tsx`:

```
499 paid
a,b
amount
[ 'id', 'status', 'amount' ]
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: whitelist sortable columns so user input never reaches SQL unchecked
import express from "express"; // express
import type { Request, Response } from "express"; // types

interface ProductRow { id: number; name: string; price: number } // SQL Server table row

// Runtime whitelist built from the type's keys (kept in sync via 'satisfies')
const sortable = ["id", "name", "price"] as const satisfies readonly (keyof ProductRow)[]; // TS 4.9+ satisfies
type SortKey = (typeof sortable)[number]; // "id" | "name" | "price"

function isSortKey(v: unknown): v is SortKey {
  return typeof v === "string" && (sortable as readonly string[]).includes(v); // runtime check
}

const app = express(); // app
app.get("/products", (req: Request, res: Response) => {
  const sort = req.query.sort; // unknown shape from the client
  if (!isSortKey(sort)) { res.status(400).json({ error: "invalid sort" }); return; } // reject
  // sort is a safe column name now; use it to build ORDER BY (still never concatenate user text without whitelist)
  res.json({ sql: `SELECT * FROM Products ORDER BY ${sort}` }); // safe because whitelisted
});
```

```tsx
// React: table headers typed by keyof, so column ids match the row type
import type { ReactNode } from "react"; // type

interface Row { sku: string; qty: number } // row shape
type Column<T> = { key: keyof T; title: string }; // a column refers to a real key

const cols: Column<Row>[] = [{ key: "sku", title: "SKU" }, { key: "qty", title: "Qty" }]; // typo-proof

export function Table({ rows }: { rows: Row[] }): ReactNode {
  return (
    <table>
      <thead><tr>{cols.map((c) => <th key={String(c.key)}>{c.title}</th>)}</tr></thead>
      <tbody>{rows.map((r) => <tr key={r.sku}>{cols.map((c) => <td key={String(c.key)}>{r[c.key]}</td>)}</tr>)}</tbody>
    </table>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: Using `string` for a key parameter.**

```typescript
// ❌ WRONG: any string is accepted, and indexing fails under strict
interface Order { id: number; status: string } // shape
function read(o: Order, key: string): unknown {
  return o[key]; // ❌ error
}
```

Real compiler output:

```
error TS7053: Element implicitly has an 'any' type because expression of type 'string' can't be used to index type 'Order'.
  No index signature with a parameter of type 'string' was found on type 'Order'.
```

**Mistake 2: Assuming `Object.keys` returns `(keyof T)[]`.**

```typescript
// ❌ WRONG: Object.keys returns string[]
interface Order { id: number; amount: number } // shape
const o: Order = { id: 1, amount: 5 }; // value
for (const k of Object.keys(o)) {
  console.log(o[k]); // ❌ error
}
```

Real compiler output:

```
error TS7053: Element implicitly has an 'any' type because expression of type 'string' can't be used to index type 'Order'.
  No index signature with a parameter of type 'string' was found on type 'Order'.
```

**Mistake 3: Writing a wrongly-typed setter (value type loses the link).**

```typescript
// ❌ WRONG: value: unknown loses the relationship with the key
interface Order { id: number; status: string } // shape
function setBad<T, K extends keyof T>(o: T, k: K, v: unknown): void {
  o[k] = v; // ❌ error
}
```

Real compiler output:

```
error TS2322: Type 'unknown' is not assignable to type 'T[K]'.
  'T[K]' could be instantiated with an arbitrary type which could be unrelated to 'unknown'.
```

---

## 🧠 Tricky Interview Question

**Q: What is `keyof` for an object with a string index signature, and for a union of types?**

```typescript
// Compile-time questions: both lines compile only if the answers are right
type A = keyof { [k: string]: boolean }; // ?
type B = keyof ({ id: number; name: string } | { id: number; price: number }); // ?
const a1: A = 5; // is a number allowed?
const b1: B = "id"; // allowed
// const b2: B = "name"; // not allowed (see answer)
console.log(typeof a1, b1);
```

Real output with `npx tsx`:

```
number id
```

**Answer:** `keyof { [k: string]: boolean }` is `string | number` because `obj[5]` is the same as `obj["5"]`, so `5` is allowed. `keyof (X | Y)` is the keys common to BOTH (`"id"`), because a value of the union is only guaranteed to have those. (For intersections `keyof (X & Y)` is the union of keys.) The `"name"` line is a compile error (uncommented, tsc says `error TS2322: Type '"name"' is not assignable to type '"id"'.`): only `"id"` is a key of the union.

---

## ⚫ Interview Questions + Answers

Q1: What does `keyof T` return?
A1: A union of the literal property names of `T` (`"id" | "name"`), including `number` or `string | number` for index signatures.

Q2: Why `K extends keyof T` rather than `key: keyof T`?
A2: The generic `K` captures the specific literal passed in, so the return can be `T[K]` (exact property type). With `keyof T` the return would be the union of all value types.

Q3: Why does `Object.keys(obj)` return `string[]`?
A3: Because an object may have more keys at runtime than its static type lists (structural typing), so `keyof T` would be unsound. Cast when you know it is safe.

Q4: `keyof` vs `typeof`?
A4: `keyof` takes a TYPE and gives its keys. `typeof` (type position) takes a VALUE and gives its type. They combine: `keyof typeof config`.

Q5: What does `keyof` do on arrays and tuples?
A5: It includes `number` plus all array method names (`"length" | "push" | ...`). For tuples it also includes `"0" | "1"`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Parameters are property names: sort, pick, update, column definitions
- Building generics (`get`, `set`, `pluck`) and mapped types
- Whitelisting query/sort fields from the client

❌ Avoid when:
- The key set is truly dynamic user data (use an index signature or `Map`)
- Iterating `Object.keys` unless you accept a cast
- A simple string-literal union is clearer and you do not need the link to a type

---

## 📊 Visual Diagram
```
 interface Order { id: number; status: string; amount: number }

 keyof Order  ─────►  "id" | "status" | "amount"
                          │
        get<T, K extends keyof T>(o: T, k: K): T[K]
                          │
        get(order, "amount")  ─►  number   ✅
        get(order, "amout")   ─►  compile error ❌
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| keyof | Union of a type's keys | Type की keys का union |
| PropertyKey | string \| number \| symbol | string \| number \| symbol |
| K extends keyof T | Generic key constraint | Generic key की शर्त |
| Indexed access T[K] | Type of property K | Property K का type |
| Whitelist | Allowed value list | अनुमत values की list |

---

## ⚡ 3-Line Summary
English:
1. `keyof T` is the union of T's property-name literals.
2. Pair with `K extends keyof T` and `T[K]` for typed get/set/sort helpers.
3. `Object.keys` stays `string[]`; whitelist client-provided keys.

Hindi:
1. `keyof T` T की property-name literals का union है।
2. Typed get/set/sort helpers के लिए `K extends keyof T` और `T[K]` साथ लगाओ।
3. `Object.keys` `string[]` ही रहता है; client से आई keys को whitelist करो।

---

## ➡️ Next Topic
**32. typeof Operator (type position)** — derive a type from an existing runtime value.
