# 51. Recursive Types
# हिंदी में: Recursive Types (खुद को refer करने वाले types)

> TypeScript 5.x पर verify किया गया (`tsc --strict`, TS 5.9). Recursive type aliases (object/array/tuple) TS 3.7 से; tail-recursion optimisation for conditional types TS 4.5 से।

---

## 🔵 Simple Definition (English)
A **recursive type** refers to itself in its own definition. It models data of unknown depth: a JSON value, a comment thread, a category tree, a nested menu, a nested config. Conditional and mapped types can also recurse to transform deep structures (`DeepPartial`, `DeepReadonly`, path types).

## 🔵 सरल परिभाषा (Hindi)
**Recursive type** अपनी ही definition में खुद को refer करता है। यह ऐसे data को model करता है जिसकी depth पता नहीं होती: JSON value, comment thread, category tree, nested menu, nested config। Conditional और mapped types भी recurse करके deep structures को बदल सकते हैं (`DeepPartial`, `DeepReadonly`, path types)।

---

## 🔴 Problem it Solves
A Swiggy menu has categories inside categories (Starters > Veg > Paneer). A comment tree has replies of replies. A JSON column in SQL Server can hold any nested value. A fixed-depth interface (`children: Category[]` only one level) cannot express "any depth". Without recursion you either use `any` or invent `Level1`, `Level2`, `Level3` types.

## 🔴 यह क्यों बना? (Hindi)
Swiggy menu में categories के अंदर categories हैं (Starters > Veg > Paneer)। Comment tree में replies की replies हैं। SQL Server के JSON column में कोई भी nested value हो सकती है। Fixed-depth interface "किसी भी depth" को express नहीं कर सकता। Recursion के बिना `any` या `Level1`, `Level2`, `Level3` जैसे types बनाने पड़ते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Interfaces and object type aliases can reference themselves: `interface Node { children: Node[] }`.
Step 2 → Since TS 3.7 a type alias may reference itself inside object, array or tuple positions: `type Json = string | number | boolean | null | Json[] | { [k: string]: Json }`.
Step 3 → Recursion directly at the top level of an alias (`type A = A | string`) is not allowed: TS2456 "circularly references itself".
Step 4 → Recursive conditional types peel a type layer by layer: `T extends [infer H, ...infer R] ? [F<H>, ...Map<R>] : []`.
Step 5 → Stopping condition: always have a base case (non-match branch) that does not recurse.
Step 6 → Depth limit: about 50 nested instantiations (TS2589) for normal recursion; tail-recursive conditionals (result is the recursive call itself) go up to 1000 (TS 4.5+). Use an accumulator parameter.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Interfaces और object type aliases खुद को refer कर सकते हैं: `interface Node { children: Node[] }`।
Step 2 → TS 3.7 से type alias object, array या tuple position में खुद को refer कर सकता है: `type Json = ... | Json[] | { [k: string]: Json }`।
Step 3 → Alias के top level पर सीधी recursion (`type A = A | string`) allowed नहीं: TS2456।
Step 4 → Recursive conditional types type को परत दर परत छीलते हैं।
Step 5 → हमेशा base case रखो जो recurse न करे।
Step 6 → Depth limit: करीब 50 (TS2589); tail-recursive conditionals (TS 4.5+) 1000 तक जाते हैं। Accumulator parameter इस्तेमाल करो।

---

## 🟡 Real World Example
**Zomato's** menu API returns categories like `{ name, items, subCategories: [...] }` where `subCategories` has the same shape and can go several levels deep. A React `<CategoryTree>` renders it recursively, and a Redux selector flattens it. One recursive `Category` type types the API response, the reducer, the component props and the flatten function. Another example: Razorpay webhook payloads are arbitrary nested JSON, typed with a recursive `JsonValue`.

## 🟡 Real Example Hindi mein
**Zomato** की menu API `{ name, items, subCategories: [...] }` जैसी categories देती है जहाँ `subCategories` का वही shape है और कई level गहरा जा सकता है। React `<CategoryTree>` इसे recursively render करता है और Redux selector flatten करता है। एक recursive `Category` type API response, reducer, component props और flatten function सबको type करता है। दूसरा उदाहरण: Razorpay webhook payloads मनमाने nested JSON हैं, जो recursive `JsonValue` से type होते हैं।

---

## 💻 Code Example — Basic

```typescript
// 1) Recursive interface: a category tree of any depth
interface Category {
  name: string; // category name
  items: string[]; // dishes directly in this category
  subCategories: Category[]; // same shape, any depth
}

const menu: Category = {
  name: "Starters",
  items: [],
  subCategories: [
    { name: "Veg", items: ["Paneer Tikka"], subCategories: [] },
    { name: "Non-veg", items: ["Chicken 65"], subCategories: [{ name: "Spicy", items: ["Chilli Chicken"], subCategories: [] }] },
  ],
};

// 2) Recursive function typed by the recursive type: collect all dishes
function allItems(c: Category): string[] {
  return [...c.items, ...c.subCategories.flatMap(allItems)]; // recurse over children
}
console.log(allItems(menu)); // [ 'Paneer Tikka', 'Chicken 65', 'Chilli Chicken' ]

// 3) Recursive type alias for any JSON value (TS 3.7+)
type Json = string | number | boolean | null | Json[] | { [key: string]: Json };
const payload: Json = { event: "payment.captured", amount: 49900, tags: ["upi", null], meta: { retry: [1, 2] } };
console.log(JSON.stringify(payload)); // {"event":"payment.captured","amount":49900,"tags":["upi",null],"meta":{"retry":[1,2]}}
```

## 💻 Code Example — Advanced

```typescript
// Advanced 1: DeepPartial and DeepReadonly with mapped types
type DeepPartial<T> = T extends (infer E)[]
  ? DeepPartial<E>[] // arrays: recurse on elements
  : T extends object
    ? { [K in keyof T]?: DeepPartial<T[K]> } // objects: recurse on every field
    : T; // primitives: stop

interface Settings {
  theme: { dark: boolean; accent: string }; // nested object
  notifications: { email: boolean; push: boolean }; // nested object
}
const patch: DeepPartial<Settings> = { theme: { dark: true } }; // other fields omitted
console.log(patch); // { theme: { dark: true } }

// Advanced 2: dotted paths of a nested object ("a.b.c")
type Paths<T> = T extends object
  ? { [K in keyof T & string]: T[K] extends object ? K | `${K}.${Paths<T[K]>}` : K }[keyof T & string]
  : never;
type SettingsPath = Paths<Settings>; // "theme" | "theme.dark" | ... | "notifications.push"
const path: SettingsPath = "theme.accent";

// Advanced 3: value at a path (recursive + template literal + infer)
type PathValue<T, P extends string> = P extends `${infer K}.${infer Rest}`
  ? K extends keyof T ? PathValue<T[K], Rest> : never // go one level deeper
  : P extends keyof T ? T[P] : never; // base case
function get<T, P extends Paths<T>>(obj: T, p: P): PathValue<T, P> {
  return p.split(".").reduce<any>((acc, k) => acc?.[k], obj); // runtime walk
}
const s: Settings = { theme: { dark: false, accent: "#f00" }, notifications: { email: true, push: false } };
const accent = get(s, "theme.accent"); // string
console.log(path, accent); // theme.accent #f00

// Advanced 4: tail-recursive tuple builder (accumulator), TS 4.5+ allows depth up to 1000
type Repeat<T, N extends number, Acc extends T[] = []> = Acc["length"] extends N ? Acc : Repeat<T, N, [...Acc, T]>;
type Three = Repeat<"x", 3>; // ["x", "x", "x"]
const three: Three = ["x", "x", "x"];
console.log(three.length); // 3
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: accept a nested filter tree (AND/OR) for a SQL Server search endpoint
import express from "express";

type Filter =
  | { field: "city" | "status"; eq: string } // leaf condition
  | { and: Filter[] } // all must match
  | { or: Filter[] }; // any can match

function toSql(f: Filter): string {
  if ("and" in f) return `(${f.and.map(toSql).join(" AND ")})`; // recurse
  if ("or" in f) return `(${f.or.map(toSql).join(" OR ")})`; // recurse
  return `${f.field} = '${f.eq.replace(/'/g, "''")}'`; // leaf (real code: use parameters)
}

const app = express();
app.use(express.json());
app.post("/search", (req, res) => {
  const filter = req.body as Filter; // validate with Zod in real code
  res.json({ where: toSql(filter) });
});
```

```tsx
// React: recursive component rendering a category tree
interface Category {
  name: string; // category name
  subCategories: Category[]; // nested
}

export function CategoryTree({ node }: { node: Category }) {
  return (
    <li>
      {node.name}
      {node.subCategories.length > 0 && (
        <ul>
          {node.subCategories.map((c) => <CategoryTree key={c.name} node={c} />)}
        </ul>
      )}
    </li>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Circular alias at the top level
```typescript
// ❌ Wrong
type Bad = Bad | string;
// error TS2456: Type alias 'Bad' circularly references itself.

// ✅ Right: recursion hidden inside an object/array position
type Good = string | Good[];
```

❌ Mistake 2: Recursion without a base case or too deep
```typescript
// ❌ Wrong: no accumulator, deep recursion on a big number
type Build<N extends number, T extends unknown[] = []> = T["length"] extends N ? T : [...Build<N, [...T, 1]>];
type Big = Build<2000>;
// error TS2589: Type instantiation is excessively deep and possibly infinite.
```

❌ Mistake 3: Assuming a recursive type guarantees finite data
```typescript
interface N { next: N } // type is fine, but you can never construct a finite value
// ✅ Right: add a terminating case
interface N2 { next: N2 | null }
```

---

## 🧠 Tricky Interview Question

```typescript
type Json = string | number | boolean | null | Json[] | { [k: string]: Json };
const a: Json = { when: new Date() }; // ❌
// error TS2322: Type '{ when: Date; }' is not assignable to type 'Json'.
//   Type 'Date' is not assignable to type '{ [k: string]: Json; }'.
//     Index signature for type 'string' is missing in type 'Date'.
```
**Does this compile? Why or why not?**

Answer: No. `Date` is an object but has no string index signature, and its members (`getTime` etc.) are functions, so it is not assignable to `Json`. The compiler says: `Index signature for type 'string' is missing in type 'Date'`. This reveals that JSON only contains primitives, arrays and plain objects; Dates must be serialised to strings first. The same reason, `undefined` and functions are not in `Json`.

---

## ⚫ Interview Questions + Answers

Q1: How do you type a JSON value?
A1: `type Json = string | number | boolean | null | Json[] | { [k: string]: Json }`. Allowed since TS 3.7 because the recursion sits inside array/object positions.

Q2: Why does `type A = A | string` fail?
A2: The alias is resolved eagerly at the top level and refers to itself immediately (TS2456). Wrap the recursive reference in an object, array or tuple type, or use an interface.

Q3: What is the limit for recursive conditional types, and how to extend it?
A3: Around 50 levels (TS2589) for ordinary recursion; since TS 4.5, tail-recursive conditionals are evaluated iteratively and can reach 1000. Use an accumulator so the recursive call is the entire branch result.

Q4: How would you implement `DeepReadonly`?
A4: `type DeepReadonly<T> = { readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K] }`. Handle functions and arrays explicitly if needed, otherwise functions get mapped as objects.

Q5: How are recursive types used in React/Redux?
A5: Tree components (menus, comments), normalised state selectors, `DeepPartial<Settings>` for patch actions, and `JsonValue` for logging/analytics payloads.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Data has unknown depth (trees, comments, JSON, filter expressions)
- Transforming nested structures (`DeepPartial`, `Paths`)
- Parsing strings recursively (route params, dotted paths)

❌ Avoid when:
- Depth is known and small; a flat interface is faster to read
- Type-level recursion over very large unions (slow, TS2589)
- Runtime validation is needed anyway; Zod `z.lazy` is clearer for validated recursion

---

## 📊 Visual Diagram
```
  interface Category { name; subCategories: Category[] }

   Starters
   ├── Veg
   │    └── Paneer (items)
   └── Non-veg
        └── Spicy
             └── Chilli Chicken
        ▲
        └── every node has the SAME type  Category

  Recursive conditional:
  DeepPartial<{a:{b:1}}>  ─► { a?: DeepPartial<{b:1}> } ─► { a?: { b?: 1 } }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Recursive type | Type refers to itself | खुद को refer करने वाला type |
| Base case | Branch that stops recursion | रुकने वाली branch |
| Accumulator | Extra param carrying result | Result ले जाने वाला param |
| Tail recursion | Recursive call is the result | आखिरी call ही result |
| TS2589 | Too deep instantiation | बहुत गहरी instantiation |

---

## ⚡ 3-Line Summary
English:
1. Recursive types model data of any depth: trees, JSON, comments, nested filters.
2. Hide the self-reference inside object/array positions; recursive conditionals need a base case.
3. Watch depth limits (about 50, or 1000 for tail recursion with an accumulator).

Hindi:
1. Recursive types किसी भी depth का data model करते हैं: trees, JSON, comments, nested filters।
2. Self-reference को object/array position के अंदर रखो; recursive conditionals को base case चाहिए।
3. Depth limits का ध्यान रखो (करीब 50, या accumulator वाले tail recursion में 1000)।

---

## ➡️ Next Topic
**52. Variance (covariance / contravariance) Basics** — `Dog[]` को `Animal[]` में कब दे सकते हैं, और function parameters उल्टे क्यों चलते हैं।
