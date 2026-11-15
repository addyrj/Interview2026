# 7. Arrays and Tuples
# हिंदी में: Arrays और Tuples

> Version note: **TypeScript 5.x** (5.9.3 पर verify)। Labelled tuple elements TS 4.0+, variadic tuples 4.0+, `noUncheckedIndexedAccess` 4.1+।

---

## 🔵 Simple Definition (English)
An **array type** (`T[]` or `Array<T>`) describes a list of **any length** where every element has the **same type**. A **tuple** (`[A, B, C]`) describes a list of **fixed length** (or fixed shape) where **each position has its own type**. Both exist only at compile time; at runtime they are ordinary JS arrays. `readonly T[]` / `readonly [A, B]` are the immutable versions.

## 🔵 सरल परिभाषा (Hindi)
**Array type** (`T[]` या `Array<T>`) **किसी भी length** की list बताता है जिसके **सारे elements का type एक** होता है। **Tuple** (`[A, B, C]`) **तय length** (या तय shape) की list बताता है जिसमें **हर position का अपना type** होता है। दोनों सिर्फ compile time पर हैं; runtime में ये सामान्य JS arrays ही हैं। `readonly T[]` / `readonly [A, B]` इनके immutable रूप हैं।

---

## 🔴 Problem it Solves
In JS, `[1, "a", true]` is just an array — nobody knows what index 0 means. APIs like React's `useState` return `[value, setter]` where position matters and the two items have different types. Plain `(string | number)[]` loses that: `const [a, b] = ...` would give both `string | number`. Tuples keep per-position types. Arrays, on the other side, stop `cart.push("oops")` when `cart` should hold only `CartItem`s, and give `.map/.filter` callbacks the right element type.

## 🔴 यह क्यों बना? (Hindi)
JS में `[1, "a", true]` बस एक array है — index 0 का मतलब किसी को पता नहीं। React के `useState` जैसे APIs `[value, setter]` लौटाते हैं जहाँ position मायने रखती है और दोनों items के types अलग हैं। साधारण `(string | number)[]` यह खो देता है: `const [a, b] = ...` दोनों को `string | number` देता। Tuples हर position का type बचाते हैं। दूसरी तरफ arrays `cart.push("oops")` रोकते हैं जब `cart` में सिर्फ `CartItem` होने चाहिए, और `.map/.filter` callbacks को सही element type देते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Array: `const ids: number[] = [1, 2]` or `Array<number>` (identical; `T[]` is preferred for simple types, `Array<...>` for readability with long unions).
Step 2 → Methods are typed: `map<U>` returns `U[]`, `filter` keeps `T[]` (use a type guard to narrow), `find` returns `T | undefined`.
Step 3 → Tuple: `const row: [number, string] = [101, "Paneer"]`. Length and per-index types are checked. Reading `row[2]` is an error.
Step 4 → Tuple extras: optional `[string, number?]`, rest `[string, ...number[]]`, labelled `[id: number, name: string]` (labels are documentation + better hover/IDE hints).
Step 5 → Immutability: `readonly number[]` (or `ReadonlyArray<number>`) removes `push/pop/sort`; `as const` on an array literal gives a `readonly` tuple of literals.
Step 6 → Caveat: `arr[i]` is typed `T` even if out of range. Turn on `noUncheckedIndexedAccess` to get `T | undefined`. Also, tuples allow `push` at runtime (TS does not block `row.push(1)` on a mutable tuple) — use `readonly` tuples.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Array: `const ids: number[] = [1, 2]` या `Array<number>` (दोनों एक जैसे; सरल types के लिए `T[]` पसंद किया जाता है, लंबे unions में `Array<...>` पढ़ने में आसान)।
Step 2 → Methods typed हैं: `map<U>` `U[]` लौटाता है, `filter` `T[]` रखता है (narrow करने के लिए type guard दो), `find` `T | undefined` लौटाता है।
Step 3 → Tuple: `const row: [number, string] = [101, "Paneer"]`। Length और हर index का type checked होता है। `row[2]` पढ़ना error है।
Step 4 → Tuple extras: optional `[string, number?]`, rest `[string, ...number[]]`, labelled `[id: number, name: string]` (labels documentation + बेहतर IDE hints के लिए)।
Step 5 → Immutability: `readonly number[]` (या `ReadonlyArray<number>`) से `push/pop/sort` हट जाते हैं; array literal पर `as const` literals का `readonly` tuple देता है।
Step 6 → सावधानी: `arr[i]` का type `T` ही रहता है चाहे index range से बाहर हो। `T | undefined` पाने के लिए `noUncheckedIndexedAccess` चालू करो। साथ ही mutable tuple पर `row.push(1)` को TS नहीं रोकता — `readonly` tuples इस्तेमाल करो।

---

## 🟡 Real World Example
**Zomato cart:** `CartItem[]` is the cart; `cart.reduce((sum, i) => sum + i.qty * i.pricePaise, 0)` is a typed total. A **price range filter** is a tuple `[min: number, max: number]` — `[100, 500]`. A **latitude/longitude** is `[lat: number, lng: number]` (GeoJSON uses `[lng, lat]`, the order bug that labelled tuples help prevent). A SQL Server query result is `Row[]`, and a CSV export row is `[orderId: string, amountPaise: number, status: string]`.

## 🟡 Real Example Hindi mein
**Zomato cart:** `CartItem[]` ही cart है; `cart.reduce((sum, i) => sum + i.qty * i.pricePaise, 0)` typed total है। **Price range filter** एक tuple है `[min: number, max: number]` — `[100, 500]`। **Latitude/longitude** `[lat: number, lng: number]` है (GeoJSON में `[lng, lat]` order होता है — यह order वाला bug labelled tuples रोकने में मदद करते हैं)। SQL Server query का result `Row[]` है, और CSV export की row `[orderId: string, amountPaise: number, status: string]` है।

---

## 💻 Code Example — Basic

```typescript
// arrays-tuples-basic.ts

// Array of one element type
const dishes: string[] = ["Paneer Tikka", "Naan"];     // string[]
const prices: Array<number> = [22000, 5000];           // same as number[]
dishes.push("Dal");                                    // OK, still string

// Typed callbacks: `d` is inferred as string, result is number[]
const lengths = dishes.map((d) => d.length);           // number[]
console.log(lengths);                                  // [ 12, 4, 3 ]

// find returns T | undefined, so we must handle undefined
const firstLong = dishes.find((d) => d.length > 5);    // string | undefined
console.log(firstLong?.toUpperCase() ?? "none");       // PANEER TIKKA

// Tuple: fixed positions with different types
const row: [number, string] = [101, "Paneer Tikka"];   // [id, name]
const [id, name] = row;                                // id: number, name: string
console.log(id + 1, name.toLowerCase());               // 102 paneer tikka

// Labelled + optional tuple elements (labels are documentation only)
type Range = [min: number, max?: number];              // max is optional
const r: Range = [100];                                // OK, max omitted
console.log(r.length);                                 // 1

// Output:
// [ 12, 4, 3 ]
// PANEER TIKKA
// 102 paneer tikka
// 1
```

```typescript
// ❌ intentional errors — real tsc 5.9 output
const ids: number[] = [1, 2, 3];
ids.push("4");
// error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.

const row: [number, string] = [101, "Paneer"];
const third = row[2];
// error TS2493: Tuple type '[number, string]' of length '2' has no element at index '2'.

const bad: [number, string] = ["Paneer", 101];
// error TS2322: Type 'string' is not assignable to type 'number'.
// error TS2322: Type 'number' is not assignable to type 'string'.

const fixed: readonly number[] = [1, 2];
fixed.push(3);
// error TS2339: Property 'push' does not exist on type 'readonly number[]'.
```

## 💻 Code Example — Advanced

```typescript
// arrays-tuples-advanced.ts — readonly, as const, variadic tuples, type-guard filter

// 1) as const: array literal -> readonly tuple of literal types
const STATUSES = ["PLACED", "PACKED", "DELIVERED"] as const;   // readonly ["PLACED","PACKED","DELIVERED"]
type Status = (typeof STATUSES)[number];                       // "PLACED" | "PACKED" | "DELIVERED"
const s: Status = "PACKED";                                    // OK
console.log(STATUSES.length, s);                               // 3 PACKED

// 2) filter + type guard to remove undefined (plain filter(Boolean) does NOT narrow in older TS)
const maybe: (string | undefined)[] = ["a", undefined, "b"];
const defined = maybe.filter((x): x is string => x !== undefined); // string[]
console.log(defined.join(","));                                // a,b

// 3) Variadic / rest tuples: first element fixed, rest typed
type LogArgs = [message: string, ...ids: number[]];
function log(...args: LogArgs): string {
  const [message, ...ids] = args;                              // ids: number[]
  return `${message} -> ${ids.join("|")}`;
}
console.log(log("orders", 1, 2, 3));                           // orders -> 1|2|3

// 4) Tuple returned from a function (like useState); `as const` keeps tuple, not array
function useCounter(initial: number) {
  let value = initial;                                         // closure state
  const inc = () => { value += 1; return value; };             // setter-like
  return [value, inc] as const;                                // readonly [number, () => number]
}
const [count, inc] = useCounter(5);                            // typed separately
console.log(count, inc());                                     // 5 6

// 5) Spread two tuples (variadic tuple types, TS 4.0)
type Head = [id: number];
type Full = [...Head, name: string, paid: boolean];            // [id: number, name: string, paid: boolean]
const f: Full = [1, "A", true];
console.log(f);                                                // [ 1, 'A', true ]

// 6) Readonly param accepts both mutable and readonly arrays
function sum(xs: readonly number[]): number {                  // promise not to mutate
  return xs.reduce((a, b) => a + b, 0);
}
console.log(sum([1, 2]), sum(STATUSES.map((x) => x.length)));  // 3 21

// Output:
// 3 PACKED
// a,b
// orders -> 1|2|3
// 5 6
// [ 1, 'A', true ]
// 3 21
```

---

## 🟠 Node/Express + React Integration

**Express + SQL Server — a typed result list and a tuple for pagination:**

```typescript
// orders-api.ts
import express from "express";

interface OrderRow { id: number; customer: string; totalPaise: number }   // one DB row

// pretend result of: SELECT id, customer, totalPaise FROM Orders
async function queryOrders(): Promise<OrderRow[]> {
  return [{ id: 1, customer: "Aditya", totalPaise: 49950 }];
}

// Offset/limit as a labelled tuple: easy to destructure, hard to swap by mistake
function pageRange(page: number, size: number): [offset: number, limit: number] {
  return [(page - 1) * size, size];
}

const app = express();
app.get("/orders", async (req, res) => {
  const [offset, limit] = pageRange(Number(req.query.page ?? 1), 20); // number, number
  const rows = await queryOrders();
  res.json({ offset, limit, data: rows.slice(offset, offset + limit) }); // OrderRow[]
});
export default app;
```

**React — `useState` returns a tuple; typed array state:**

```tsx
// Cart.tsx
import { useState } from "react";

type CartItem = { sku: string; qty: number };

export function Cart() {
  // useState<CartItem[]> -> [CartItem[], Dispatch<SetStateAction<CartItem[]>>]
  const [items, setItems] = useState<CartItem[]>([]);              // [] needs the generic, else never[]
  const add = (sku: string) =>
    setItems((prev) => [...prev, { sku, qty: 1 }]);               // immutable update: new array
  return <button onClick={() => add("PIZZA")}>Cart ({items.length})</button>;
}
```
Redux Toolkit: `state.items.push(x)` inside `createSlice` reducers is fine (Immer), but selectors should return `readonly` views or memoised arrays so components don't mutate the store.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `useState([])` without a generic — type becomes `never[]`
```typescript
// ❌ Wrong — an empty array literal is inferred as never[] in strict mode
const items = [] as never[];            // what useState([]) infers
items.push({ sku: "A", qty: 1 });
// error TS2345: Argument of type '{ sku: string; qty: number; }' is not assignable to parameter of type 'never'.
```
```typescript
// ✅ Right — annotate the element type
type CartItem = { sku: string; qty: number };
const items: CartItem[] = [];
items.push({ sku: "A", qty: 1 });
console.log(items.length); // 1
```

❌ Mistake 2: Using a tuple type for a mutable array and expecting a fixed length at runtime
✅ Correct: `row.push(1)` on a mutable tuple compiles. Use `readonly [number, string]` if you need immutability.

❌ Mistake 3: `arr.filter(Boolean)` expecting `string[]` from `(string | undefined)[]`
✅ Correct: use a type guard `filter((x): x is string => x !== undefined)` (TS 5.5 infers type predicates for simple arrow functions like `x => x !== undefined`).

❌ Mistake 4: `arr[0]` assumed to exist
✅ Correct: enable `noUncheckedIndexedAccess` and handle `undefined`.

---

## 🧠 Tricky Interview Question

```typescript
const point: [number, number] = [1, 2];
point.push(3);
console.log(point.length);
const third = point[2]; // ❌ TS2493 (see answer)
```
**Question:** Does it compile? What is printed?

**Answer:** `point.push(3)` **compiles** and prints `3` — TS tuples are only checked on **construction and indexing**; mutating methods like `push` are not blocked. But `point[2]` is an error (`TS2493: Tuple type '[number, number]' of length '2' has no element at index '2'`). So the tuple lies about its length at runtime. Use `readonly [number, number]` to make `push` a compile error (`Property 'push' does not exist on type 'readonly [number, number]'`).

```typescript
// verified: compiles and prints 3
const point: [number, number] = [1, 2];
point.push(3);
console.log(point.length); // 3
```

---

## ⚫ Interview Questions + Answers

Q1: `string[]` vs `Array<string>` vs `readonly string[]`?
A1: First two are identical. `readonly string[]` is a supertype without mutating methods; a mutable array is assignable to it but not vice-versa. Prefer `readonly` for function parameters you don't mutate.

Q2: How is a tuple different from an array?
A2: An array has a uniform element type and unknown length; a tuple has fixed positions with individual types (and a fixed length unless it has optional/rest elements). Use tuples for small heterogeneous groups where order carries meaning (`[value, setter]`, `[lat, lng]`); use objects when there are more than ~3 fields or when names matter.

Q3: How do you get a union of an array's element types?
A3: `type El = (typeof arr)[number]`; with `as const` on the array literal this gives the union of literal values (`"PLACED" | "PACKED"`). This is the standard enum alternative.

Q4: Why does `const a = []` sometimes become `any[]`?
A4: With `noImplicitAny` on and no annotation, `const a = []` is an "evolving array": its type changes as you `push` values and is finalised by control flow; reading it before any push gives an implicit-any error (`TS7034`). Annotate it: `const a: string[] = []`.

Q5: Explain `noUncheckedIndexedAccess`.
A5: Makes `arr[i]` and index-signature reads `T | undefined`, forcing a check. It is not in `strict` but strongly recommended; it catches the out-of-range read that otherwise only fails at runtime.

---

## 🔷 When to Use + When Not to Use
✅ Use arrays: homogeneous lists (cart items, orders, ids). Use tuples: hook-style returns, coordinates, small fixed records, function arguments (`Parameters<T>` is a tuple).
✅ Use `readonly` / `as const`: constants, function params, Redux selectors.

❌ Avoid tuples: with more than 3-4 positions or when callers must remember what index 3 means — use an object. Avoid `any[]`; avoid `Object`/`Array` (uppercase types).

---

## 📊 Visual Diagram
```
 ARRAY   string[]            index → 0      1      2      3 ...   (any length, same type)
                                   "A"    "B"    "C"    "D"

 TUPLE   [number, string, boolean]
                 │       │       │
          index  0       1       2           (fixed positions, different types)
                 101   "Paneer"  true        row[3] → ❌ TS2493

 READONLY  readonly number[]   → no push / pop / sort / splice
 as const  ["A","B"] as const  → readonly ["A","B"]  (literal tuple)

 useState<T>() ──► [T, Dispatch<SetStateAction<T>>]   (a tuple!)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Array type | Same-type list, any length | एक type की list, कोई भी length |
| Tuple | Fixed-position, per-index types | तय positions, हर index का अपना type |
| Labelled tuple | Tuple elements with names | Tuple elements को नाम देना |
| readonly array | Array you can't mutate | जिसे बदल नहीं सकते |
| as const | Freeze literal as readonly literal types | Literal को readonly literal types बनाना |
| Variadic tuple | Tuples with spread `...T` | `...T` spread वाले tuples |
| noUncheckedIndexedAccess | `arr[i]` may be undefined | `arr[i]` undefined हो सकता है |

---

## ⚡ 3-Line Summary
English:
1. `T[]` is a uniform list of any length; `[A, B]` is a fixed-position tuple with per-index types.
2. Use `readonly` and `as const` to prevent mutation and derive literal unions; mutable tuples still allow `push`.
3. Annotate empty arrays (`useState<Item[]>([])`) and enable `noUncheckedIndexedAccess` to handle missing indexes.

Hindi:
1. `T[]` किसी भी length की एक-type list है; `[A, B]` तय positions वाला tuple है जिसमें हर index का अपना type होता है।
2. Mutation रोकने और literal unions निकालने के लिए `readonly` और `as const` इस्तेमाल करो; mutable tuple पर `push` फिर भी चलता है।
3. खाली arrays annotate करो (`useState<Item[]>([])`) और missing index संभालने के लिए `noUncheckedIndexedAccess` चालू करो।

---

## ➡️ Next Topic
**008. Objects and Type Annotations** — describing object shapes inline, optional/readonly properties and nested objects.
