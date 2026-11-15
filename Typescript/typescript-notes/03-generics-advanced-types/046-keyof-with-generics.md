# 46. keyof with Generics
# हिंदी में: Generics के साथ keyof

> TypeScript 5.x पर verify किया गया (`tsc --strict`, TS 5.9). `keyof` और `K extends keyof T` पुराने features हैं (TS 2.1+). `const` type parameters TS 5.0 में आए।

---

## 🔵 Simple Definition (English)
`keyof T` produces a union of the property names of `T`. Combined with generics, `K extends keyof T` says "K must be one of the keys of T". Then `T[K]` (an indexed access type) gives the exact type of that property. Together they let you write functions like `getProp(obj, "name")` whose return type is exactly the type of `obj.name`, and typos in the key are compile errors.

## 🔵 सरल परिभाषा (Hindi)
`keyof T` एक union देता है जिसमें `T` के सारे property names होते हैं। Generics के साथ `K extends keyof T` का मतलब है "K, T की keys में से कोई एक होना चाहिए"। फिर `T[K]` (indexed access type) उस property का exact type देता है। इनसे `getProp(obj, "name")` जैसे functions बनते हैं जिनका return type ठीक `obj.name` का type होता है, और key में typo compile error बन जाता है।

---

## 🔴 Problem it Solves
Plain JS helpers like `pluck(obj, "price")` take a string and return `any`. A typo `"pricee"` compiles and returns `undefined` at runtime, which in a payments or cart flow becomes `NaN` totals. Typing the key as `string` is no better: `obj[key]` errors under strict (`TS7053`) or yields `any`. We need the key type to depend on the object type.

## 🔴 यह क्यों बना? (Hindi)
JS के `pluck(obj, "price")` जैसे helpers string लेते हैं और `any` लौटाते हैं। `"pricee"` typo compile हो जाता है और runtime पर `undefined` आता है, जो cart/payment में `NaN` total बन जाता है। Key को `string` type देना भी काफी नहीं: `obj[key]` strict mode में `TS7053` देता है। हमें ऐसा key type चाहिए जो object के type पर निर्भर हो।

---

## 🟢 How it Works — Step by Step

Step 1 → `keyof Order` evaluates to `"id" | "amount" | "status"`, a string-literal union.
Step 2 → Declare two type params: `T` for the object, `K extends keyof T` for the key.
Step 3 → When called, TypeScript infers `T` from the object and `K` from the literal key (kept as a literal because of the `extends keyof T` constraint).
Step 4 → Return `T[K]`, so the result type is the property's real type, not `any`.
Step 5 → For arrays of keys use `K extends keyof T` with `K[]` and return `Pick<T, K>` or `T[K][]`.
Step 6 → Remember: `keyof` of an index signature `{[k: string]: X}` is `string | number`; `keyof any` is `string | number | symbol`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `keyof Order` का मतलब `"id" | "amount" | "status"` (string-literal union)।
Step 2 → दो type params लो: object के लिए `T`, key के लिए `K extends keyof T`।
Step 3 → Call पर TypeScript `T` को object से और `K` को literal key से infer करता है।
Step 4 → `T[K]` return करो, तो result का type property का असली type होता है, `any` नहीं।
Step 5 → Keys की array के लिए `K[]` लो और `Pick<T, K>` या `T[K][]` लौटाओ।
Step 6 → याद रखो: index signature `{[k: string]: X}` का `keyof` `string | number` होता है; `keyof any` = `string | number | symbol`।

---

## 🟡 Real World Example
**Swiggy's** admin dashboard has a generic table: you pass `rows: Restaurant[]` and `sortBy: "rating" | "deliveryTime" | "name"`. Instead of hand-writing that union for every entity (Restaurant, Order, Rider), the table component is `<T>(rows: T[], sortBy: keyof T)`. Add a field to `Restaurant` and the allowed sort keys update automatically; rename a field and every wrong usage lights up red.

## 🟡 Real Example Hindi mein
**Swiggy** के admin dashboard में generic table है: `rows: Restaurant[]` और `sortBy: "rating" | "deliveryTime" | "name"`। हर entity (Restaurant, Order, Rider) के लिए यह union हाथ से लिखने की जगह table component `<T>(rows: T[], sortBy: keyof T)` है। `Restaurant` में field जोड़ो तो sort keys अपने आप update; field rename करो तो हर गलत usage लाल हो जाता है।

---

## 💻 Code Example — Basic

```typescript
// An order shape used throughout the examples
interface Order {
  id: string; // order id
  amount: number; // amount in rupees
  status: "PLACED" | "PAID" | "DELIVERED"; // lifecycle state
}

type OrderKeys = keyof Order; // "id" | "amount" | "status"
const k: OrderKeys = "amount"; // OK: one of the keys

// Type-safe property getter: K is tied to T
function getProp<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key]; // T[K] is the exact property type
}

const order: Order = { id: "ord_9", amount: 749, status: "PAID" };
const amt = getProp(order, "amount"); // inferred: number
const st = getProp(order, "status"); // inferred: "PLACED" | "PAID" | "DELIVERED"
console.log(amt + 1, st.toLowerCase(), k); // 750 paid amount
```

```typescript
// Setter keeps value type tied to the key: you cannot assign a string to amount
function setProp<T, K extends keyof T>(obj: T, key: K, value: T[K]): void {
  obj[key] = value; // allowed because value is exactly T[K]
}

// Pluck: extract one field from an array of objects
function pluck<T, K extends keyof T>(items: T[], key: K): T[K][] {
  return items.map((item) => item[key]); // map each item to its field
}

interface CartLine {
  sku: string; // product id
  qty: number; // quantity
  price: number; // unit price
}
const cart: CartLine[] = [
  { sku: "A1", qty: 2, price: 120 },
  { sku: "B2", qty: 1, price: 350 },
];
const prices = pluck(cart, "price"); // number[]
console.log(prices.reduce((s, p) => s + p, 0)); // 470

const line = cart[0]!; // non-null assertion: array has items
setProp(line, "qty", 5); // OK: number to number
console.log(line.qty); // 5
```

## 💻 Code Example — Advanced

```typescript
// Advanced: groupBy with a key constraint that only allows string/number-valued fields
type KeysMatching<T, V> = {
  [K in keyof T]-?: T[K] extends V ? K : never; // keep keys whose value extends V
}[keyof T]; // index the mapped type to get the union of kept keys

function groupBy<T, K extends KeysMatching<T, string | number>>(
  items: T[],
  key: K,
): Map<T[K], T[]> {
  const out = new Map<T[K], T[]>(); // result map keyed by the field value
  for (const item of items) {
    const bucket = out.get(item[key]) ?? []; // existing bucket or new array
    bucket.push(item); // add the item
    out.set(item[key], bucket); // store back
  }
  return out; // return grouped map
}

interface Payment {
  id: string; // payment id
  method: "UPI" | "CARD" | "NETBANKING"; // payment method
  amount: number; // amount
  meta: { retries: number }; // nested object: NOT groupable
}
const payments: Payment[] = [
  { id: "p1", method: "UPI", amount: 100, meta: { retries: 0 } },
  { id: "p2", method: "UPI", amount: 250, meta: { retries: 1 } },
  { id: "p3", method: "CARD", amount: 900, meta: { retries: 0 } },
];
const byMethod = groupBy(payments, "method"); // OK: string field
console.log([...byMethod.keys()], byMethod.get("UPI")?.length); // [ 'UPI', 'CARD' ] 2

// Typed event map: keyof drives the handler signatures
interface Events {
  paid: { orderId: string; amount: number }; // payload for paid
  failed: { orderId: string; reason: string }; // payload for failed
}
function on<E extends keyof Events>(name: E, handler: (payload: Events[E]) => void): void {
  console.log(`registered ${String(name)}`); // pretend registration
  handler({ orderId: "o1", amount: 1, reason: "x" } as Events[E]); // demo call
}
on("paid", (p) => console.log(p.amount)); // p is { orderId; amount }
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: whitelist sortable columns so user input never reaches SQL Server unchecked
import express from "express";

interface Product {
  id: number; // PK
  name: string; // product name
  price: number; // price
}
const SORTABLE = ["name", "price"] as const satisfies readonly (keyof Product)[]; // satisfies: TS 4.9+
type SortKey = (typeof SORTABLE)[number]; // "name" | "price"

function isSortKey(v: unknown): v is SortKey {
  return typeof v === "string" && (SORTABLE as readonly string[]).includes(v); // runtime check
}

const app = express();
app.get("/products", (req, res) => {
  const sort = isSortKey(req.query.sort) ? req.query.sort : "name"; // safe default
  // Column name is whitelisted, so interpolating into ORDER BY is safe
  res.json({ sql: `SELECT id, name, price FROM Products ORDER BY ${sort}` });
});
```

```tsx
// React: generic sortable table; columns are keyof T
interface TableProps<T> {
  rows: T[]; // data
  columns: (keyof T & string)[]; // only real keys allowed
}

function DataTable<T extends Record<string, unknown>>({ rows, columns }: TableProps<T>) {
  return (
    <table>
      <thead>
        <tr>{columns.map((c) => <th key={c}>{c}</th>)}</tr>
      </thead>
      <tbody>
        {rows.map((r, i) => (
          <tr key={i}>{columns.map((c) => <td key={c}>{String(r[c])}</td>)}</tr>
        ))}
      </tbody>
    </table>
  );
}

export const Demo = () => (
  <DataTable rows={[{ name: "Dosa", price: 90 }]} columns={["name", "price"]} /> // "pric" would be an error
);
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Typing the key as `string`
```typescript
// ❌ Wrong
function getBad<T>(obj: T, key: string) {
  return obj[key];
}
// error TS7053: Element implicitly has an 'any' type because expression of type 'string' can't be used to index type 'unknown'.

// ✅ Right
function getGood<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
```

❌ Mistake 2: A key that does not exist
```typescript
// ❌ Wrong
interface User { name: string; age: number }
function get<T, K extends keyof T>(o: T, k: K): T[K] { return o[k]; }
get({ name: "Asha", age: 30 }, "email");
// error TS2345: Argument of type '"email"' is not assignable to parameter of type '"name" | "age"'.
```

❌ Mistake 3: Assigning a wrong value type through a generic setter
```typescript
// ❌ Wrong
function set<T, K extends keyof T>(o: T, k: K, v: T[K]) { o[k] = v; }
set({ qty: 1 }, "qty", "two");
// error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.
```

---

## 🧠 Tricky Interview Question

```typescript
type A = keyof { [k: string]: number };
type B = keyof string[];
```
**What are `A` and `B`?**

Answer: `A` is `string | number`, because JS converts numeric keys to strings so an index signature accepts both. `B` is `number | "length" | "push" | "map" | ...` (all array method names plus `number`). Interviewers use this to see if you know `keyof` includes inherited members and numeric index signatures, so `keyof` of a class or array is rarely a short union.

---

## ⚫ Interview Questions + Answers

Q1: What does `keyof T` return?
A1: A union of the known public property names of `T` (string/number/symbol literal types). For `{a: 1; b: 2}` it is `"a" | "b"`. For an index signature it is `string | number`.

Q2: Why do we need `K extends keyof T` instead of `key: string`?
A2: The constraint makes TypeScript (1) reject keys that are not in `T`, (2) infer `K` as the literal, and (3) let `T[K]` resolve to the exact property type. With plain `string`, indexing fails with TS7053 or returns `any`.

Q3: How do you get only keys whose values are of a certain type?
A3: Use a mapped type plus indexed access: `{ [K in keyof T]-?: T[K] extends V ? K : never }[keyof T]`, as in `KeysMatching` above. The `-?` removes optionality so `undefined` does not leak into the union.

Q4: What is the difference between `keyof typeof obj` and `keyof Type`?
A4: `typeof obj` first converts the runtime value to its type, then `keyof` gets the key names. It is the common pattern for `const` config objects: `type Role = keyof typeof ROLES`. `keyof Type` works directly on a type.

Q5: How is `keyof` used in Redux Toolkit or React code?
A5: Generic reducers that update a form field (`updateField<K extends keyof Form>(key: K, value: Form[K])`), generic selectors `pick<K extends keyof State>`, and table/column components. The pattern ensures the `value` type always matches the field.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Writing helpers that access properties by name (`pluck`, `groupBy`, `sortBy`, `setField`)
- Building typed event maps, form handlers, column definitions
- Whitelisting query params (sort, filter) from the request

❌ Avoid when:
- The set of keys is fixed and tiny; a plain union is clearer
- The type has a wide index signature, since `keyof` becomes `string | number` and loses safety

---

## 📊 Visual Diagram
```
  interface Order { id: string; amount: number; status: Status }

  keyof Order  ──►  "id" | "amount" | "status"
                      ▲
                      │ K extends keyof T
  getProp(order, "amount")
        T = Order, K = "amount"
        return T[K]  ──►  Order["amount"]  ──►  number

  getProp(order, "email")  ──►  ✗ TS2345 (not in keyof Order)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| keyof | Union of property names | Property names का union |
| K extends keyof T | Key tied to object type | Key को object से जोड़ना |
| Indexed access `T[K]` | Type of a property | Property का type |
| Mapped type | Transform each key | हर key को बदलना |
| Whitelist | Allowed values only | सिर्फ allowed values |

---

## ⚡ 3-Line Summary
English:
1. `keyof T` gives the union of T's keys; `K extends keyof T` ties a key parameter to the object.
2. Return `T[K]` so the result type is the property's real type, not `any`.
3. Use it for pluck, groupBy, setters, event maps and safe sort/filter whitelists.

Hindi:
1. `keyof T` T की keys का union देता है; `K extends keyof T` key parameter को object से जोड़ता है।
2. `T[K]` return करो ताकि result का type property का असली type हो, `any` नहीं।
3. pluck, groupBy, setters, event maps और safe sort/filter whitelist में इस्तेमाल करो।

---

## ➡️ Next Topic
**47. Mapped Types** — `{ [K in keyof T]: ... }` से एक type की हर property को transform करना।
