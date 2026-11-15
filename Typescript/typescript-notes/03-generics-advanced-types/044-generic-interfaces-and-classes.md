# 44. Generic Interfaces and Classes
# हिंदी में: Generic Interfaces और Classes

> Verified with **TypeScript 5.x** (compiled with 5.9, `--strict`). Generic interfaces/classes are stable across all TS versions.

---

## 🔵 Simple Definition (English)
A **generic interface** or **generic class** has type parameters on the declaration itself: `interface Repository<T>`, `class Stack<T>`. The type parameter is fixed when you **use** the type (`Repository<Order>`, `new Stack<string>()`) and applies to every member that mentions `T`. Unlike generic functions, `T` is chosen once per **type/instance**, not per method call (a method may still add its own `<U>`).

## 🔵 सरल परिभाषा (Hindi)
**Generic interface** या **generic class** में type parameters declaration पर ही होते हैं: `interface Repository<T>`, `class Stack<T>`। Type parameter तब तय होता है जब आप type को **use** करते हो (`Repository<Order>`, `new Stack<string>()`) और वह हर उस member पर लागू होता है जो `T` को mention करता है। Generic functions से अलग, `T` हर **type/instance** के लिए एक बार चुना जाता है, हर method call पर नहीं (method अपना `<U>` जोड़ सकता है)।

---

## 🔴 Problem it Solves
Containers and service layers repeat the same structure for different data: `OrderRepository`, `UserRepository`, `PaymentRepository` — all with `get`, `save`, `delete`. Without generics you copy the code per model or type everything as `any`. A single `Repository<T>` contract and one `InMemoryRepository<T>` / `MssqlRepository<T>` class give consistency, reuse and full type safety for each entity.

## 🔴 यह क्यों बना? (Hindi)
Containers और service layers अलग-अलग data के लिए वही structure दोहराते हैं: `OrderRepository`, `UserRepository`, `PaymentRepository` — सबमें `get`, `save`, `delete`। Generics के बिना आप हर model के लिए code copy करते हो या सब कुछ `any` बना देते हो। एक `Repository<T>` contract और एक `InMemoryRepository<T>` / `MssqlRepository<T>` class consistency, reuse और हर entity के लिए पूरी type safety देते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Declare: `interface Repository<T> { get(id: string): T | undefined }`.
Step 2 → A class can `implements Repository<Order>` (fixed `T`) or stay generic: `class MemRepo<T> implements Repository<T>`.
Step 3 → Instantiate with a type argument: `new MemRepo<Order>()`. With constructor arguments, TS can often infer `T`: `new Box(5)` → `Box<number>`.
Step 4 → Add **constraints** (`T extends { id: string }`) and **defaults** (`<T, ID = string>`) when you need them.
Step 5 → **Static members cannot use the class's `T`** (statics belong to the class, not an instance) → TS2302.
Step 6 → Generics are **erased** at runtime — `Repository<Order>` and `Repository<User>` are the same JS class. You cannot do `x instanceof Repository<Order>` or `new T()`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Declare करो: `interface Repository<T> { get(id: string): T | undefined }`।
Step 2 → Class `implements Repository<Order>` कर सकती है (तय `T`) या generic रह सकती है: `class MemRepo<T> implements Repository<T>`।
Step 3 → Type argument के साथ instantiate करो: `new MemRepo<Order>()`। Constructor arguments हों तो TS अक्सर `T` infer कर लेता है: `new Box(5)` → `Box<number>`।
Step 4 → ज़रूरत हो तो **constraints** (`T extends { id: string }`) और **defaults** (`<T, ID = string>`) जोड़ो।
Step 5 → **Static members class का `T` इस्तेमाल नहीं कर सकते** (statics class के हैं, instance के नहीं) → TS2302।
Step 6 → Generics runtime पर **erase** हो जाते हैं — `Repository<Order>` और `Repository<User>` एक ही JS class हैं। `x instanceof Repository<Order>` या `new T()` नहीं हो सकता।

---

## 🟡 Real World Example
**Paytm-style backend**: a `Repository<T extends { id: string }>` interface defines `findById`, `save`, `delete`. `InMemoryRepository<T>` is used in unit tests, and `MssqlRepository<T>` runs real SQL Server queries in production. Services depend on the **interface** (`Repository<Payment>`), so swapping storage means changing one line of wiring, with every call still type-checked.

## 🟡 Real Example Hindi mein
**Paytm जैसा backend**: `Repository<T extends { id: string }>` interface में `findById`, `save`, `delete` define हैं। Unit tests में `InMemoryRepository<T>` और production में असली SQL Server queries चलाने वाला `MssqlRepository<T>` इस्तेमाल होता है। Services **interface** (`Repository<Payment>`) पर निर्भर रहती हैं, इसलिए storage बदलना wiring की एक line बदलना है और हर call फिर भी type-checked रहती है।

---

## 💻 Code Example — Basic

```typescript
// Generic class: the type parameter lives on the class, shared by all members
class Stack<T> {
  private items: T[] = [];                   // storage typed by T
  push(item: T): void { this.items.push(item); }          // accepts only T
  pop(): T | undefined { return this.items.pop(); }       // returns T or undefined
  peek(): T | undefined { return this.items[this.items.length - 1]; }
  get size(): number { return this.items.length; }        // accessor
}

const undoStack = new Stack<string>();       // T = string for this instance
undoStack.push("add pizza");
undoStack.push("add coke");
console.log(undoStack.pop(), undoStack.size);
// undoStack.push(42);                       // would be a compile error: number not string
// Output:
// add coke 1
```

```typescript
// Generic interface for a response envelope + generic type alias with default
interface Page<T> {
  items: T[];                                // rows on this page
  nextCursor?: string;                       // optional pagination cursor
}
type Maybe<T = string> = T | null;           // default type parameter

const page: Page<{ id: string; total: number }> = {
  items: [{ id: "o1", total: 199 }],
};
const label: Maybe = "ok";                   // uses default => string | null
console.log(page.items[0].total, label);
// Output:
// 199 ok
```

## 💻 Code Example — Advanced

```typescript
// Generic repository contract + two implementations (in-memory and "SQL Server" style)
interface Entity { id: string }              // every stored thing has an id

interface Repository<T extends Entity> {
  findById(id: string): Promise<T | undefined>; // async lookup
  save(entity: T): Promise<T>;                  // insert/update
  delete(id: string): Promise<boolean>;         // true if something was removed
}

// Implementation 1: generic class implementing the generic interface
class InMemoryRepository<T extends Entity> implements Repository<T> {
  protected rows = new Map<string, T>();                // id -> entity
  async findById(id: string) { return this.rows.get(id); }   // returns Promise<T | undefined>
  async save(entity: T) { this.rows.set(entity.id, entity); return entity; }
  async delete(id: string) { return this.rows.delete(id); }
}

// Implementation 2: a SQL Server-style repo (fake query function keeps it runnable)
type Query = (sql: string, params: unknown[]) => Promise<Record<string, unknown>[]>;

class MssqlRepository<T extends Entity> implements Repository<T> {
  constructor(private table: string, private run: Query) {}   // parameter properties
  async findById(id: string) {
    const rows = await this.run(`SELECT * FROM ${this.table} WHERE id = @p0`, [id]);
    return rows[0] as T | undefined;                           // row -> T (trust or validate!)
  }
  async save(entity: T) {
    await this.run(`MERGE ${this.table} ... /* upsert */`, [entity]);
    return entity;
  }
  async delete(id: string) {
    await this.run(`DELETE FROM ${this.table} WHERE id = @p0`, [id]);
    return true;
  }
}

interface Payment extends Entity { amount: number; status: "paid" | "failed" }

// Service depends on the INTERFACE, not on a concrete class
async function refund(repo: Repository<Payment>, id: string): Promise<string> {
  const p = await repo.findById(id);                  // Payment | undefined
  if (!p) return "not found";
  return p.status === "paid" ? `refund ${p.amount}` : "nothing to refund"; // typed fields
}

async function main() {
  const repo = new InMemoryRepository<Payment>();     // swap for MssqlRepository in prod
  await repo.save({ id: "p1", amount: 499, status: "paid" });
  console.log(await refund(repo, "p1"), "|", await refund(repo, "zzz"));

  const fakeSql: Query = async () => [{ id: "p2", amount: 10, status: "failed" }];
  console.log(await refund(new MssqlRepository<Payment>("Payments", fakeSql), "p2"));
}
main();
// Output:
// refund 499 | not found
// nothing to refund
```

```typescript
// Generic class with TWO parameters, a constraint, a default and a method-level generic
class TtlCache<K extends string | number, V = unknown> {
  private store = new Map<K, { value: V; expires: number }>(); // entries with expiry
  constructor(private ttlMs: number) {}                         // time to live
  set(key: K, value: V): void {
    this.store.set(key, { value, expires: Date.now() + this.ttlMs });
  }
  get(key: K): V | undefined {
    const hit = this.store.get(key);
    if (!hit || hit.expires < Date.now()) return undefined;     // missing or expired
    return hit.value;
  }
  // method-level type parameter U: independent of the class's K and V
  getAs<U extends V>(key: K): U | undefined { return this.get(key) as U | undefined; }
}

const menuCache = new TtlCache<string, { name: string; price: number }>(1000);
menuCache.set("m1", { name: "Masala Dosa", price: 90 });
console.log(menuCache.get("m1")?.price, menuCache.get("nope"));
// Output:
// 90 undefined
```

---

## 🟠 Node/Express + React Integration

```typescript
import express from "express";                         // Express runtime
import type { Response } from "express";

interface Entity { id: string }
interface Repository<T extends Entity> { findById(id: string): Promise<T | undefined> }

// Generic controller factory: builds a GET /:id handler for ANY repository
function getByIdHandler<T extends Entity>(repo: Repository<T>) {
  return async (req: express.Request<{ id: string }>, res: Response<T | { error: string }>) => {
    const row = await repo.findById(req.params.id);    // T | undefined
    if (!row) { res.status(404).json({ error: "not found" }); return; }
    res.json(row);                                      // typed as T
  };
}

interface Restaurant extends Entity { name: string }
const restaurantRepo: Repository<Restaurant> = {
  findById: async (id) => (id === "r1" ? { id, name: "Meghana Foods" } : undefined),
};

const app = express();
app.get("/restaurants/:id", getByIdHandler(restaurantRepo)); // T inferred = Restaurant
```

```tsx
import type { ReactNode } from "react";

// Generic table component: column definitions are typed against the row type
interface Column<T> {
  header: string;                                       // column title
  cell: (row: T) => ReactNode;                          // how to render a row
}
interface TableProps<T extends { id: string }> {
  rows: T[];
  columns: Column<T>[];
}

export function Table<T extends { id: string }>({ rows, columns }: TableProps<T>) {
  return (
    <table>
      <thead><tr>{columns.map((c) => <th key={c.header}>{c.header}</th>)}</tr></thead>
      <tbody>
        {rows.map((r) => (
          <tr key={r.id}>{columns.map((c) => <td key={c.header}>{c.cell(r)}</td>)}</tr>
        ))}
      </tbody>
    </table>
  );
}

interface Order { id: string; total: number }
export const OrdersTable = () => (
  <Table<Order>                                         // T = Order, so r.total is typed
    rows={[{ id: "o1", total: 250 }]}
    columns={[{ header: "Total", cell: (r) => `Rs ${r.total}` }]}
  />
);
```

**Redux note:** a normalized state shape is naturally generic: `interface EntityState<T> { ids: string[]; entities: Record<string, T> }` — Redux Toolkit's `EntityState<T>` and `createEntityAdapter<T>()` work exactly like this.

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: Forgetting the type argument, or using the class `T` in a `static`.**

```typescript
// ❌ Missing type argument; static member using the class type parameter
interface Repo<T> { get(id: string): T | undefined }
const r: Repo = { get: () => undefined }; // wrong: Repo needs <T>
// error TS2314: Generic type 'Repo<T>' requires 1 type argument(s).

class Stack<T> { static empty: T[] = []; } // wrong: statics have no T
// error TS2302: Static members cannot reference class type parameters.
```

```typescript
// ✅ Provide the argument (or a default); make the static generic on its own
interface Repo<T = unknown> { get(id: string): T | undefined }
const r: Repo = { get: () => undefined };            // default T = unknown

class Stack<T> {
  static create<U>(): Stack<U> { return new Stack<U>(); } // static method with its OWN <U>
}
console.log(r.get("a"), Stack.create<number>() instanceof Stack);
// Output:
// undefined true
```

**Mistake 2: Trying to use `T` at runtime.** `new T()`, `T.name`, `x instanceof T`, `if (typeof x === T)` are all invalid because types are erased. Pass the constructor in: `constructor(private ctor: new () => T)`.

**Mistake 3: Assuming `Repository<Order>` and `Repository<User>` are different at runtime.** They are the same JS class — keep a discriminator (table name, schema) if you need runtime distinction.

**Mistake 4: Returning a row from SQL as `T` without validating.** `rows[0] as T` is a promise, not a check. Validate with Zod at the boundary (topic 86) if the DB schema may drift.

---

## 🧠 Tricky Interview Question

```typescript
class Box<T> { constructor(public value: T) {} }
const a = new Box(5);
const b = new Box<number | string>(5);
// b = a;  // Does `const b: Box<number|string> = a` compile?
const c: Box<number | string> = a;
c.value = "now a string";
console.log(typeof a.value);
// Output:
// string
```
**Answer:** It **compiles** (verified) because TypeScript treats generic type arguments **covariantly** for property types, so `Box<number>` is assignable to `Box<number | string>`. But `c` and `a` are the *same object*, so writing a string through `c` silently corrupts `a` — at runtime `typeof a.value` is `"string"` while the compiler still believes it is `number`. TS is deliberately unsound here for mutable properties (usability over strictness). To be strict, make the property `readonly` or use `in`/`out` variance annotations (TS 4.7, topic 52).

---

## ⚫ Interview Questions + Answers

**Q1: Generic interface vs generic function — when is `T` decided?**
A1: Generic function: at each **call**. Generic interface/class: when the **type is referenced/instance created** (`Repository<Order>`, `new Stack<string>()`). Methods in a generic class can add their own type parameters too.

**Q2: Why can't a static member use the class's `T`?**
A2: Statics live on the constructor function, shared by all instances regardless of `T`. Since `T` differs per instance type, TS reports TS2302. Give the static method its own `<U>`.

**Q3: How do you implement a generic interface in a class?**
A3: Either fix it (`class OrderRepo implements Repository<Order>`) or pass through (`class MemRepo<T extends Entity> implements Repository<T>`). The class must satisfy every member with the substituted `T`.

**Q4: Can you create `new T()` in a generic class?**
A4: No — `T` does not exist at runtime. Accept a constructor parameter typed `new () => T` (or `new (...args: any[]) => T`) and call that.

**Q5: When should a type parameter have a default?**
A5: When most users use the same type and you want `Repo` to mean `Repo<unknown>` / `Result<T>` to mean `Result<T, string>`. Defaults must come after required parameters and must satisfy the constraint.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Reusable data structures (Stack, Queue, Cache, EventEmitter)
- Repository/service contracts across many entities
- Typed UI building blocks (Table<T>, Select<T>, List<T>)
- API clients and envelopes (`ApiClient`, `Page<T>`, `Result<T, E>`)

❌ Avoid when:
- Only one concrete type will ever be used
- You need runtime behaviour that depends on `T` (pass a constructor/schema instead)
- Heavy generic hierarchies make errors unreadable — prefer composition and small interfaces

---

## 📊 Visual Diagram
```
 interface Repository<T extends Entity>        class InMemoryRepository<T> implements Repository<T>
        │                                               │
        ├── Repository<Payment>   ◄── used by ──  new InMemoryRepository<Payment>()
        ├── Repository<Order>                      new MssqlRepository<Order>("Orders", run)
        └── Repository<Rider>
 compile time:  distinct, fully typed
 runtime:       ONE class each (generics erased) ── no `new T()`, no `instanceof Repository<X>`

 class Stack<T> { push(x: T) ... }   instance type fixed at creation
 new Stack<string>()  → push(string) only
 static members: NO access to T   (TS2302)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Generic interface | Interface with type parameters | Type parameters वाला interface |
| Generic class | Class parameterised by types | Types से parameterised class |
| Type erasure | No generics at runtime | Runtime पर generics नहीं |
| Repository pattern | Abstract data-access interface | Data access का abstract interface |
| Parameter property | `constructor(private x: T)` shorthand | Constructor में field बनाने का shortcut |
| Covariance | `Box<Cat>` assignable to `Box<Animal>` | Subtype को supertype की जगह मानना |

---

## ⚡ 3-Line Summary
English:
1. Generic interfaces/classes take type parameters on the declaration, fixed per type or instance (`Repository<Order>`, `new Stack<string>()`).
2. Combine constraints and defaults (`<T extends Entity = Order>`); statics can't use the class `T`, and `T` doesn't exist at runtime.
3. Program against generic interfaces (repositories, API clients, `Table<T>`) so implementations can be swapped with full type safety.

Hindi:
1. Generic interfaces/classes में type parameters declaration पर होते हैं और type या instance के लिए तय रहते हैं (`Repository<Order>`, `new Stack<string>()`)।
2. Constraints और defaults मिलाओ (`<T extends Entity = Order>`); statics class का `T` इस्तेमाल नहीं कर सकते और `T` runtime पर मौजूद नहीं।
3. Generic interfaces (repositories, API clients, `Table<T>`) के against code लिखो ताकि implementations पूरी type safety के साथ बदले जा सकें।

---

## ➡️ Next Topic
**45. Default Type Parameters** — giving type parameters fallback types so generic APIs stay simple for the common case.
