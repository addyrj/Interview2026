# 43. Generic Constraints (extends)
# हिंदी में: Generic Constraints (`extends` से सीमा लगाना)

> Verified with **TypeScript 5.x** (compiled with 5.9, `--strict`). Constraints have worked this way since TS 1.x; `satisfies`-style helpers need 4.9+.

---

## 🔵 Simple Definition (English)
A **generic constraint** limits which types may be used for a type parameter: `<T extends Shape>`. Inside the function the compiler now knows `T` is *at least* `Shape`, so you may use `Shape`'s members, while the caller still gets back their **own, more specific** type. `extends` here means "is assignable to", not class inheritance.

## 🔵 सरल परिभाषा (Hindi)
**Generic constraint** type parameter के लिए allowed types को सीमित करता है: `<T extends Shape>`। अब function के अंदर compiler जानता है कि `T` *कम से कम* `Shape` है, इसलिए आप `Shape` के members इस्तेमाल कर सकते हो, और caller को फिर भी उसका **अपना, ज़्यादा specific** type वापस मिलता है। यहाँ `extends` का मतलब है "assignable है", class inheritance नहीं।

---

## 🔴 Problem it Solves
Unconstrained `T` is opaque: `x.id` on `T` is an error because `T` could be a number. But typing the parameter as `{ id: string }` would **erase** the caller's type (you get back only `{ id: string }`, losing `name`, `price`...). Constraints solve both: **access to required members** *and* **preservation of the full type**.

## 🔴 यह क्यों बना? (Hindi)
Unconstrained `T` अपारदर्शी है: `T` पर `x.id` error है क्योंकि `T` number भी हो सकता है। लेकिन parameter को `{ id: string }` type देने पर caller का type **मिट** जाता है (आपको सिर्फ `{ id: string }` मिलता है, `name`, `price`... खो जाते हैं)। Constraints दोनों हल करते हैं: **ज़रूरी members तक पहुँच** *और* **पूरे type का बचाव**।

---

## 🟢 How it Works — Step by Step

Step 1 → Write `<T extends Constraint>`; `Constraint` can be an object type, union, `keyof`, function type, class constructor, or another type parameter.
Step 2 → At each call TS checks the argument type is **assignable** to `Constraint`. If not → error at the argument.
Step 3 → Inside the body `T` is treated as `Constraint` for member access.
Step 4 → The return type can still be `T`, so the caller's exact type flows out.
Step 5 → Constraints can reference earlier parameters: `<T, K extends keyof T>` — "K must be a real key of T".
Step 6 → Constraint ≠ default: `<T extends object = {}>` gives both. Remember that `T` may be a **subtype with extra members**, so you can't *create* a `T` from the constraint (`return { id: "x" }` is an error).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `<T extends Constraint>` लिखो; `Constraint` object type, union, `keyof`, function type, class constructor या कोई और type parameter हो सकता है।
Step 2 → हर call पर TS जाँचता है कि argument का type `Constraint` में **assignable** है। नहीं तो argument पर error।
Step 3 → Body के अंदर member access के लिए `T` को `Constraint` माना जाता है।
Step 4 → Return type फिर भी `T` हो सकता है, इसलिए caller का सटीक type बाहर आता है।
Step 5 → Constraints पहले के parameters को refer कर सकते हैं: `<T, K extends keyof T>` — "K, T की असली key होनी चाहिए"।
Step 6 → Constraint ≠ default: `<T extends object = {}>` दोनों देता है। याद रखो `T` **extra members वाला subtype** हो सकता है, इसलिए constraint से `T` *बना* नहीं सकते (`return { id: "x" }` error है)।

---

## 🟡 Real World Example
**Swiggy "find by id" repository helper**: `findById<T extends { id: string }>(items: T[], id: string): T | undefined`. It works for `Restaurant`, `Order`, `Rider` — anything with a string `id` — and returns the full type, so `findById(restaurants, "r1")?.cuisine` is typed. The constraint documents the contract: "I need an `id`, I don't care about the rest."

## 🟡 Real Example Hindi mein
**Swiggy का "find by id" repository helper**: `findById<T extends { id: string }>(items: T[], id: string): T | undefined`। यह `Restaurant`, `Order`, `Rider` — string `id` वाली किसी भी चीज़ — के लिए चलता है और पूरा type लौटाता है, इसलिए `findById(restaurants, "r1")?.cuisine` typed है। Constraint contract लिख देता है: "मुझे `id` चाहिए, बाकी से मतलब नहीं।"

---

## 💻 Code Example — Basic

```typescript
// T must have a string id; the caller's full type is preserved in the return
function findById<T extends { id: string }>(items: T[], id: string): T | undefined {
  return items.find((item) => item.id === id);   // item.id is allowed due to the constraint
}

interface Restaurant { id: string; name: string; cuisine: string }
const restaurants: Restaurant[] = [
  { id: "r1", name: "Meghana Foods", cuisine: "Biryani" },
  { id: "r2", name: "Vidyarthi Bhavan", cuisine: "Dosa" },
];

const found = findById(restaurants, "r2");       // Restaurant | undefined (NOT just { id: string })
console.log(found?.name, found?.cuisine);        // extra members still typed
// Output:
// Vidyarthi Bhavan Dosa
```

```typescript
// Constraint with a built-in shape: anything that has a numeric length
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;           // .length allowed; returns same T
}

console.log(longest("paneer", "dal"), longest([1, 2, 3], [4, 5]));
// Output:
// paneer [ 1, 2, 3 ]
```

## 💻 Code Example — Advanced

```typescript
// Constraint that depends on another type parameter: K must be a key of T
function getField<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];                               // safe indexing, precise result type
}

const order = { id: "o1", total: 450, paid: false };
const total = getField(order, "total");          // number
console.log(total + 50);
// getField(order, "price");                     // would be an error: not a key of order
// Output:
// 500
```

```typescript
// Constraining to a FUNCTION type + inferring pieces with extra type parameters
function timed<A extends unknown[], R>(fn: (...args: A) => R) {
  return (...args: A): { result: R; ms: number } => { // same params, richer return
    const start = Date.now();                    // measure
    const result = fn(...args);                  // call original
    return { result, ms: Date.now() - start };   // wrap result
  };
}

const add = (a: number, b: number) => a + b;
const timedAdd = timed(add);                     // (a: number, b: number) => { result: number; ms: number }
console.log(timedAdd(2, 3).result);
// Output:
// 5
```

```typescript
// Constraint to a class constructor type (factory / DI container style)
type Constructor<T = object> = new (...args: any[]) => T;

function createAll<T extends Constructor>(ctor: T, count: number): InstanceType<T>[] {
  return Array.from({ length: count }, () => new ctor() as InstanceType<T>); // build instances
}

class Cart { items: string[] = []; }
const carts = createAll(Cart, 2);                // Cart[]
carts[0].items.push("pizza");                    // typed instance members
console.log(carts.length, carts[0].items, carts[1].items);
// Output:
// 2 [ 'pizza' ] []
```

```typescript
// Constraint + DEFAULT: Paged<T> works for any object, defaults to a generic record
interface Paged<T extends object = Record<string, unknown>> {
  page: number;                                  // current page
  rows: T[];                                     // rows typed by T
}
const loose: Paged = { page: 1, rows: [{ anything: 1 }] };       // uses default
const strict: Paged<{ id: string }> = { page: 1, rows: [{ id: "a" }] }; // explicit T
console.log(loose.rows.length + strict.rows.length);
// Output:
// 2
```

---

## 🟠 Node/Express + React Integration

```typescript
import { Router } from "express";                       // Express router
import type { Request, Response } from "express";

// Repository contract: anything stored must have an id
interface Entity { id: string }

class InMemoryRepo<T extends Entity> {                  // constraint on the class type parameter
  private rows = new Map<string, T>();                  // id -> entity
  save(entity: T): T { this.rows.set(entity.id, entity); return entity; }
  get(id: string): T | undefined { return this.rows.get(id); }
}

interface Order extends Entity { total: number }
const orders = new InMemoryRepo<Order>();               // Order satisfies Entity
orders.save({ id: "o1", total: 250 });

export const router = Router();
router.get("/orders/:id", (req: Request<{ id: string }>, res: Response) => {
  const order = orders.get(req.params.id);              // Order | undefined
  if (!order) { res.status(404).json({ error: "not found" }); return; }
  res.json(order);                                      // typed Order
});
```

```tsx
import type { ReactNode } from "react";

// Generic list component: items must have an id (used as React key)
interface ListProps<T extends { id: string }> {
  items: T[];                                           // data
  render: (item: T) => ReactNode;                       // render function gets full T
}

export function List<T extends { id: string }>({ items, render }: ListProps<T>) {
  return <ul>{items.map((i) => <li key={i.id}>{render(i)}</li>)}</ul>; // i.id allowed
}

// Usage: T inferred as { id: string; name: string }
export const demo = <List items={[{ id: "r1", name: "Meghana" }]} render={(r) => r.name} />;
```

**Redux note:** `createEntityAdapter<T extends { id: EntityId }>` in Redux Toolkit uses the same idea: the adapter needs an id, but your slice keeps its full entity type.

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: Passing something that does not satisfy the constraint.**

```typescript
// ❌ id is a number but the constraint requires string
function byId<T extends { id: string }>(xs: T[], id: string) { return xs.find((x) => x.id === id); }
byId([{ id: 1 }], "a"); // wrong
// error TS2322: Type 'number' is not assignable to type 'string'.
```

**Mistake 2: Trying to construct a `T` from the constraint.**

```typescript
// ❌ T could be { id: string; extra: number }; a bare { id } is not a T
function make<T extends { id: string }>(): T {
  return { id: "x" }; // wrong
}
// error TS2322: Type '{ id: string; }' is not assignable to type 'T'.
//   '{ id: string; }' is assignable to the constraint of type 'T', but 'T' could be instantiated with a different subtype of constraint '{ id: string; }'.
```

```typescript
// ✅ Accept a factory or the value, or return the constraint type
function make<T extends { id: string }>(factory: () => T): T {
  return factory();                       // caller creates the real T
}
const o = make(() => ({ id: "x", total: 1 }));
console.log(o.total);
// Output:
// 1
```

**Mistake 3: Using the constraint type as the parameter, losing the specific type.**

```typescript
// Loses info: returns only { id: string }
function firstBad(xs: { id: string }[]): { id: string } { return xs[0]; }
// Keeps info: returns the caller's own type
function firstGood<T extends { id: string }>(xs: T[]): T { return xs[0]; }

const r = firstGood([{ id: "a", price: 10 }]);
console.log(r.price, firstBad([{ id: "b" }]).id);
// Output:
// 10 b
```

---

## 🧠 Tricky Interview Question

```typescript
function pass<T extends string | number>(x: T): T { return x; }
const a = pass("hi");
const b = pass(5);
const c: "hi" = a;
const d: 5 = b;
console.log(a, b);
// Output:
// hi 5
```
**Q:** Why are `a` and `b` literal types here, but `id("a")` with an unconstrained `T` and `let` is `string`?
**Answer:** When the constraint includes primitive types (`string | number`), TypeScript keeps the **literal** inference (`"hi"`, `5`) because widening would break the constraint-driven intent. So `const c: "hi" = a` compiles. This is the trick behind `K extends string` APIs (event names, route keys) that return exact literal types — it is why `on<K extends keyof Events>(name: K)` preserves the key. With an unconstrained `T` and a `let` variable the result widens to `string`.

---

## ⚫ Interview Questions + Answers

**Q1: Does `T extends X` mean inheritance?**
A1: No — it means "assignable to X" (structural). Any type with at least X's members (including unions of subtypes, literals) satisfies it.

**Q2: Why can't I `return { id: "x" }` from `<T extends { id: string }>(): T`?**
A2: `T` may be a *narrower subtype* chosen by the caller (extra required fields). A fresh `{ id }` is not necessarily a `T` (TS2322 "could be instantiated with a different subtype"). Take a factory or the value as a parameter, or return the constraint type.

**Q3: What is `K extends keyof T` used for?**
A3: To accept only valid property names of `T` and return `T[K]` precisely (`pick`, `getField`, typed `sort by key`). It's the backbone of type-safe property access.

**Q4: Can a constraint reference another type parameter or itself?**
A4: Yes: `<T, K extends keyof T>`, `<T extends Comparable<T>>` (F-bounded / recursive constraint) for things like `sort<T extends { compareTo(o: T): number }>`.

**Q5: Constraint vs default type parameter?**
A5: Constraint = what types are *allowed*; default = what `T` becomes if *not inferred/provided*. Often together: `<T extends object = Record<string, unknown>>`. The default must satisfy the constraint.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The body needs members (`id`, `length`, `keyof`)
- You want the caller's specific type returned, not the minimal shape
- Repositories, list components, `pick`/`getField` helpers, DI factories

❌ Avoid when:
- A plain parameter type does the job and the return type does not need `T`
- You need to *create* values of type `T` (take a factory instead)
- Over-constraining (`T extends Order`) makes the helper non-reusable

---

## 📊 Visual Diagram
```
  <T extends { id: string }>

   allowed T:                              rejected T:
   ┌──────────────────────────┐            ┌──────────────────────┐
   │ { id: string }           │            │ { id: number }  ✖    │
   │ { id: string, name }     │            │ { name: string } ✖   │
   │ Restaurant, Order, Rider │            │ string, number   ✖   │
   └───────────┬──────────────┘            └──────────────────────┘
               ▼
   inside body: T treated as { id: string }  (can use .id)
   return type: T  (caller's FULL type preserved)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Constraint | `T extends X` limit | `T` पर सीमा |
| keyof | Union of property names | Property names का union |
| Indexed access | `T[K]` type of that property | उस property का type |
| Subtype | More specific type (extra members) | ज़्यादा specific type |
| F-bounded | Constraint referencing T itself | खुद `T` को refer करने वाला constraint |
| Default type parameter | `<T = X>` fallback | `<T = X>` fallback type |

---

## ⚡ 3-Line Summary
English:
1. `<T extends X>` lets you use X's members inside the function while returning the caller's own, more specific `T`.
2. `K extends keyof T` gives type-safe property access; constraints can reference earlier type parameters.
3. You cannot construct a `T` from its constraint (TS2322) — accept a factory or value instead.

Hindi:
1. `<T extends X>` से function के अंदर X के members इस्तेमाल होते हैं और caller का अपना, ज़्यादा specific `T` ही लौटता है।
2. `K extends keyof T` type-safe property access देता है; constraints पहले के type parameters को refer कर सकते हैं।
3. Constraint से `T` बनाया नहीं जा सकता (TS2322) — factory या value parameter में लो।

---

## ➡️ Next Topic
**44. Generic Interfaces and Classes** — typed repositories, stacks, caches and API clients built from generic interfaces and classes.
