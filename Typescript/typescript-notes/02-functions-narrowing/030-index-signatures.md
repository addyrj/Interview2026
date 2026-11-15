# 30. Index Signatures
# हिंदी में: Index Signatures (अनजान keys वाले objects)

> Verified with TypeScript 5.x (5.9) under `tsc --strict`. `noUncheckedIndexedAccess` (TS 4.1+) is NOT part of `strict`; it is shown separately.

---

## 🔵 Simple Definition (English)
An **index signature** describes an object whose **property names are not known in advance** but whose values all share one type: `{ [key: string]: number }`. Any string key is allowed and reading it gives `number`. It is the typed version of a JavaScript dictionary / hash map.

## 🔵 सरल परिभाषा (Hindi)
**Index signature** ऐसे object को describe करता है जिसके **property names पहले से पता नहीं** होते लेकिन सारी values का type एक ही होता है: `{ [key: string]: number }`। कोई भी string key चलती है और पढ़ने पर `number` मिलता है। यह JavaScript dictionary / hash map का typed रूप है।

---

## 🔴 Problem it Solves
Objects like `{ "pay_1": 500, "pay_2": 250 }`, HTTP headers, query strings, i18n dictionaries and price tables have dynamic keys. You cannot list them as named properties. Without an index signature, `obj[someKey]` gives "implicitly has an 'any' type" errors; with it you get safe, typed dictionary access.

## 🔴 यह क्यों बना? (Hindi)
`{ "pay_1": 500, "pay_2": 250 }`, HTTP headers, query strings, i18n dictionaries और price tables जैसे objects की keys dynamic होती हैं। इन्हें named properties के रूप में list नहीं किया जा सकता। Index signature के बिना `obj[someKey]` पर "implicitly has an 'any' type" error आता है; इसके साथ typed dictionary access मिलती है।

---

## 🟢 How it Works — Step by Step

Step 1 → Syntax: `{ [key: string]: ValueType }`. The name `key` is only documentation.
Step 2 → Key type can be `string`, `number`, `symbol`, a template literal pattern (`` `sku_${string}` ``), or a union of these (TS 4.4+).
Step 3 → Every explicitly named property must be assignable to the index value type.
Step 4 → A `number` index must have a value type assignable to the `string` index's value type (JS converts number keys to strings).
Step 5 → Reading `obj["anything"]` returns `ValueType` even if the key does not exist, which is a lie at runtime (undefined).
Step 6 → Enable `noUncheckedIndexedAccess` to make reads `ValueType | undefined`, forcing you to check.
Step 7 → For a fixed, known set of keys prefer `Record<"a" | "b", T>`, and use `Map<K, V>` when keys are not strings or you need ordering and size.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Syntax: `{ [key: string]: ValueType }`। नाम `key` सिर्फ़ documentation के लिए है।
Step 2 → Key type `string`, `number`, `symbol`, template literal pattern (`` `sku_${string}` ``) या इनका union हो सकता है (TS 4.4+)।
Step 3 → हर explicitly named property का type index value type में assignable होना चाहिए।
Step 4 → `number` index का value type `string` index के value type में assignable होना चाहिए (JS number keys को string बना देता है)।
Step 5 → `obj["anything"]` पढ़ने पर `ValueType` मिलता है भले key मौजूद न हो, जो runtime पर झूठ है (undefined)।
Step 6 → `noUncheckedIndexedAccess` चालू करो तो reads `ValueType | undefined` हो जाते हैं और check करना पड़ता है।
Step 7 → Fixed, ज्ञात keys के लिए `Record<"a" | "b", T>` बेहतर है, और जब keys string न हों या order/size चाहिए तो `Map<K, V>` लो।

---

## 🟡 Real World Example
**Paytm price table by SKU**: `{ [sku: string]: number }` stores `{ "RECHARGE_199": 199, "DTH_450": 450 }`. SKUs come from a DB and change daily, so no fixed property list can exist. The code looks up `prices[sku] ?? 0`.

## 🟡 Real Example Hindi mein
**Paytm की SKU के हिसाब से price table**: `{ [sku: string]: number }` में `{ "RECHARGE_199": 199, "DTH_450": 450 }` रहता है। SKUs DB से आते हैं और रोज़ बदलते हैं, इसलिए fixed property list नहीं हो सकती। Code `prices[sku] ?? 0` से lookup करता है।

---

## 💻 Code Example — Basic

```typescript
// String index signature: any string key maps to a number
interface PriceTable {
  [sku: string]: number; // key name 'sku' is only a label
}

const prices: PriceTable = { RECHARGE_199: 199, DTH_450: 450 }; // dynamic keys
prices["WIFI_999"] = 999; // adding a new key is allowed
const p = prices["RECHARGE_199"]; // type: number
console.log(p, Object.keys(prices).length); // 199 3

// Index signature + a known property: known must match the index value type
interface Cart {
  [sku: string]: number; // quantity per sku
  total: number; // OK: number is assignable to number
}
const cart: Cart = { total: 2, BIRYANI: 2 }; // total is just another number key
console.log(cart.total, cart["BIRYANI"]); // 2 2

// The runtime lie: missing key still typed as number
const missing = prices["NOPE"]; // static type: number, runtime: undefined
console.log(missing); // undefined
```

Run with `npx tsx`:

```
199 3
2 2
undefined
```

## 💻 Code Example — Advanced

```typescript
// Advanced: template-literal keys, readonly, Record, Map, noUncheckedIndexedAccess-style safe lookup

// Only keys that START with "sku_" are allowed (TS 4.4+ pattern index signatures)
interface Inventory {
  [key: `sku_${string}`]: number; // pattern signature
  location: string; // normal property is allowed because its key does not match the pattern
}
const inv: Inventory = { location: "Pune", sku_a: 5, sku_b: 0 }; // valid
console.log(inv.sku_a + inv.sku_b, inv.location); // 5 Pune

// Readonly index signature: reads only
interface Headers {
  readonly [name: string]: string | undefined; // header values may be missing
}
const h: Headers = { "content-type": "application/json" }; // ok
console.log(h["content-type"]?.toUpperCase()); // APPLICATION/JSON, ? because of undefined

// Union with a fixed key set: Record is better than an index signature
type Method = "upi" | "card"; // known methods
const fees: Record<Method, number> = { upi: 0, card: 2 }; // exhaustive keys, no extras allowed

// Safe lookup helper that makes the "maybe missing" case explicit
function lookup<T>(dict: { [k: string]: T }, key: string): T | undefined {
  return Object.prototype.hasOwnProperty.call(dict, key) ? dict[key] : undefined; // own keys only
}
console.log(lookup({ a: 1 }, "a"), lookup({ a: 1 }, "toString")); // 1 undefined (no prototype leak)

// Map for dynamic keys when you need size, ordering, or non-string keys
const stock = new Map<string, number>([["dosa", 10]]); // typed map
stock.set("idli", 4); // add
console.log(stock.get("dosa"), stock.get("vada"), stock.size); // 10 undefined 2 (get is T | undefined)
```

Run with `npx tsx`:

```
5 Pune
APPLICATION/JSON
1 undefined
10 undefined 2
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: req.headers and req.query are index-signature shaped
import express from "express"; // express
import type { Request, Response } from "express"; // types

// Group SQL rows by a string key into a dictionary
interface Row { restaurant: string; amount: number } // row from SQL Server

function totalsByRestaurant(rows: Row[]): { [restaurant: string]: number } {
  const out: { [restaurant: string]: number } = {}; // empty dictionary
  for (const r of rows) {
    out[r.restaurant] = (out[r.restaurant] ?? 0) + r.amount; // ?? handles missing key
  }
  return out; // dictionary of totals
}

const app = express(); // app
app.get("/report", (_req: Request, res: Response) => {
  const rows: Row[] = [{ restaurant: "A", amount: 100 }, { restaurant: "A", amount: 50 }, { restaurant: "B", amount: 70 }]; // fake data
  res.json(totalsByRestaurant(rows)); // { A: 150, B: 70 }
});

// Headers: Node types give string | string[] | undefined, so narrow before use
app.get("/ua", (req: Request, res: Response) => {
  const ua = req.headers["user-agent"]; // string | undefined
  res.json({ ua: ua ?? "unknown" }); // safe default
});
```

```tsx
// React: dictionary of form errors keyed by field name
import { useState } from "react"; // hook

type Errors = { [field: string]: string | undefined }; // dynamic form fields

export function Checkout() {
  const [errors, setErrors] = useState<Errors>({}); // start with no errors
  const validate = (phone: string): void => {
    setErrors({ phone: phone.length === 10 ? undefined : "Enter 10 digits" }); // set by key
  };
  return (
    <div>
      <input onChange={(e) => validate(e.target.value)} />
      {errors["phone"] && <span role="alert">{errors["phone"]}</span>}
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: A named property that conflicts with the index value type.**

```typescript
// ❌ WRONG: 'name' is a string but the index signature says all values are number
interface Bad {
  [key: string]: number; // everything is a number
  name: string; // ❌ conflict
}
```

Real compiler output:

```
error TS2411: Property 'name' of type 'string' is not assignable to 'string' index type 'number'.
```

```typescript
// ✅ RIGHT: widen the index value type with a union
interface Good {
  [key: string]: number | string; // union covers both
  name: string; // ok
  qty: number; // ok
}
const g: Good = { name: "Dosa", qty: 2 }; // valid
console.log(g.name, g.qty);
```

**Mistake 2: Trusting a missing key (the "undefined" lie) and showing `noUncheckedIndexedAccess`.**

```typescript
// ❌ RISK: compiles but crashes at runtime
const prices: { [sku: string]: number } = { A: 10 }; // dictionary
const price = prices["B"]; // typed number, actually undefined
console.log(price.toFixed(2)); // TypeError at runtime
```

Real output of `npx tsx`:

```
TypeError: Cannot read properties of undefined (reading 'toFixed')
```

With `"noUncheckedIndexedAccess": true` in tsconfig the same read is `number | undefined`, and the last line fails to compile:

```
error TS18048: 'price' is possibly 'undefined'.
```

**Mistake 3: Using a `number` index whose value type is not assignable to the `string` index.**

```typescript
// ❌ WRONG: numeric index returns string, string index says number
interface Weird {
  [k: string]: number; // string index: number
  [n: number]: string; // ❌ conflict
}
```

Real compiler output:

```
error TS2413: 'number' index type 'string' is not assignable to 'string' index type 'number'.
```

---

## 🧠 Tricky Interview Question

**Q: What does this print, and why does `"toString"` matter?**

```typescript
// Plain-object dictionary and prototype keys
const counts: { [word: string]: number } = {}; // empty dictionary
const words = ["a", "toString", "a"]; // note: toString is also an Object.prototype member
for (const w of words) {
  counts[w] = (counts[w] ?? 0) + 1; // ?? does NOT treat a function as missing
}
console.log(counts["a"], typeof counts["toString"]); // ?
```

Real output with `npx tsx`:

```
2 string
```

**Answer:** The first `"toString"` read returns the inherited function (not `undefined`), so `?? 0` keeps the function and `function + 1` becomes a string like `"function toString() ..."1`. The static type says `number` throughout, so TypeScript cannot warn you. Fixes: `Object.create(null)`, `Map<string, number>`, or `Object.hasOwn(counts, w)` (ES2022).

---

## ⚫ Interview Questions + Answers

Q1: What is an index signature?
A1: `{ [key: string]: T }`: it says any property with a key of that type has value type `T`. Use it for dictionaries with unknown keys.

Q2: Why must named properties match the index value type?
A2: Named properties are also reachable through the index, so TS requires each to be assignable to `T`. Use a union (`number | string`) if mixing.

Q3: `Record<string, T>` vs `{ [k: string]: T }`?
A3: They are equivalent for `string` keys. `Record` is a mapped type and also works with union keys (exact key sets), so it is preferred for fixed keys.

Q4: What does `noUncheckedIndexedAccess` do?
A4: It makes index reads return `T | undefined` (also array index reads), forcing a check. It is not in `strict`; many teams turn it on for safety.

Q5: Index signature vs `Map`?
A5: Objects have prototype keys and only string/symbol keys, and need `hasOwn` care. `Map` has any key type, insertion order, `size`, no prototype clash, and `get` returns `T | undefined`. For hot dictionaries, `Map` is often better.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Keys are dynamic: price tables by SKU, headers, query params, translation maps, form errors
- Typing JSON dictionaries from APIs
- Grouping/counting results by key

❌ Avoid when:
- Keys are a known fixed set (use `Record<Union, T>` or an interface)
- You need non-string keys or reliable ordering (use `Map`)
- Prototype keys such as `constructor` could collide (use `Map` or `Object.create(null)`)

---

## 📊 Visual Diagram
```
 interface PriceTable { [sku: string]: number }

   prices["RECHARGE_199"] ─► number
   prices["WIFI_999"]     ─► number
   prices["ANYTHING"]     ─► number   (runtime: maybe undefined ⚠)

 Safer:
   noUncheckedIndexedAccess  ─► number | undefined
   Record<"upi"|"card", T>   ─► exact keys only
   Map<string, number>       ─► get() : number | undefined
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Index signature | Type for dynamic keys | Dynamic keys के लिए type |
| Dictionary | Key to value object | Key-value object |
| Record | Mapped type for key sets | Key set के लिए mapped type |
| noUncheckedIndexedAccess | Reads become `T \| undefined` | Reads `T \| undefined` हो जाते हैं |
| Pattern key | Template-literal index key | Template-literal वाली key |

---

## ⚡ 3-Line Summary
English:
1. `{ [key: string]: T }` types dictionaries with unknown keys.
2. Reads are typed `T` even for missing keys; enable `noUncheckedIndexedAccess` or use `Map`.
3. For fixed keys use `Record<Union, T>` instead.

Hindi:
1. `{ [key: string]: T }` अनजान keys वाले dictionaries को type करता है।
2. Missing key पर भी read का type `T` मिलता है; `noUncheckedIndexedAccess` चालू करो या `Map` लो।
3. Fixed keys के लिए `Record<Union, T>` इस्तेमाल करो।

---

## ➡️ Next Topic
**31. keyof Operator** — turn an object type's keys into a union of string literals.
