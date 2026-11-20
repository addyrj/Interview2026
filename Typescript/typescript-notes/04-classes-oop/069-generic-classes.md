# 69. Generic Classes
# हिंदी में: Generic Classes (type को parameter बनाने वाली classes)

> Verified with TypeScript 5.9 (`tsc --strict`). `const` type parameters = TS 5.0. `NoInfer` = TS 5.4.

---

## 🔵 Simple Definition (English)
A **generic class** is a class with one or more **type parameters** written in angle brackets: `class Stack<T> { ... }`. The class body uses `T` as a placeholder, and each user decides the real type when creating an instance: `new Stack<number>()`. You write the logic once and get full type safety for every type.

## 🔵 सरल परिभाषा (Hindi)
**Generic class** वह class है जिसके नाम के साथ angle brackets में एक या ज़्यादा **type parameters** होते हैं: `class Stack<T> { ... }`। Class के अंदर `T` एक placeholder है, और instance बनाते समय user असली type चुनता है: `new Stack<number>()`। Logic एक बार लिखो, हर type के लिए पूरी type safety पाओ।

---

## 🔴 Problem it Solves
Without generics, a reusable `Repository` or `Cache` class must use `any` (no safety, bugs found in production) or be copy-pasted per entity (`OrderRepository`, `UserRepository`, `PaymentRepository` - same code, three times). Generic classes give **one implementation, many types**: `Repository<Order>` returns `Order`, never `any`.

## 🔴 यह क्यों बना? (Hindi)
Generics के बिना reusable `Repository` या `Cache` class में या तो `any` इस्तेमाल करना पड़ता है (कोई safety नहीं, bug production में पकड़ में आते हैं) या हर entity के लिए copy-paste (`OrderRepository`, `UserRepository`, `PaymentRepository` - वही code तीन बार)। Generic class से **एक implementation, कई types**: `Repository<Order>` हमेशा `Order` देती है, `any` नहीं।

---

## 🟢 How it Works — Step by Step

Step 1 → Declare type parameters after the class name: `class Box<T>`.
Step 2 → Use `T` for fields, constructor params, method params and return types.
Step 3 → Add constraints with `extends`: `class Repo<T extends { id: number }>` so the body may use `item.id`.
Step 4 → Add defaults: `class Cache<K = string, V = unknown>`.
Step 5 → At `new`, TS infers `T` from constructor arguments (`new Box(5)` -> `Box<number>`) or you give it explicitly.
Step 6 → **Static members cannot use the class type parameters** (statics belong to the class, not to an instance with a specific `T`).

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Class के नाम के बाद type parameters लिखो: `class Box<T>`।
Step 2 → Fields, constructor params, method params और return types में `T` इस्तेमाल करो।
Step 3 → `extends` से constraint लगाओ: `class Repo<T extends { id: number }>` ताकि body में `item.id` चल सके।
Step 4 → Defaults दो: `class Cache<K = string, V = unknown>`।
Step 5 → `new` पर TS `T` को constructor arguments से infer करता है (`new Box(5)` -> `Box<number>`) या तुम explicitly दो।
Step 6 → **Static members class के type parameters इस्तेमाल नहीं कर सकते** (statics class के होते हैं, किसी खास `T` वाले instance के नहीं)।

---

## 🟡 Real World Example
**Paytm-style data layer**: `Wallet`, `Transaction` and `Merchant` records all need `findById`, `save`, `list`. A single `InMemoryRepository<T extends { id: string }>` serves all three. A second generic class, `ApiResult<T>`, wraps every Express response as `{ data: T }` or `{ error: string }`. Interviewers love asking you to build exactly these two classes.

## 🟡 Real Example Hindi mein
**Paytm-जैसी data layer**: `Wallet`, `Transaction` और `Merchant` records सबको `findById`, `save`, `list` चाहिए। एक `InMemoryRepository<T extends { id: string }>` तीनों को चलाती है। दूसरी generic class `ApiResult<T>` हर Express response को `{ data: T }` या `{ error: string }` में लपेटती है। Interview में ये दो classes बनाने को अक्सर कहा जाता है।

---

## 💻 Code Example — Basic

```typescript
// A generic Stack: T is chosen by the caller
class Stack<T> {
  private items: T[] = []; // internal array of T

  push(item: T): void {
    this.items.push(item); // add on top
  }

  pop(): T | undefined {
    return this.items.pop(); // remove top (undefined if empty)
  }

  peek(): T | undefined {
    return this.items[this.items.length - 1]; // look at top without removing
  }

  get size(): number {
    return this.items.length; // how many items
  }
}

const cart = new Stack<string>(); // explicit T = string
cart.push("Paneer Tikka"); // OK
cart.push("Naan"); // OK
// cart.push(42);          // would be an error: number is not string
console.log(cart.pop(), cart.size); // Naan 1

// const amounts = new Stack(10); // error TS2554: Expected 0 arguments, but got 1. (Stack has no constructor param)
```

```typescript
// Inference from constructor arguments
class Box<T> {
  constructor(public value: T) {} // T is inferred from the argument
  map<U>(fn: (v: T) => U): Box<U> {
    return new Box(fn(this.value)); // a method can have ITS OWN type parameter U
  }
}

const b1 = new Box(499); // inferred Box<number>
const b2 = b1.map((n) => `Rs.${n}`); // Box<string>
console.log(b2.value); // Rs.499
```

## 💻 Code Example — Advanced

```typescript
// Constraint: every stored item must have a string id
interface HasId {
  id: string;
}

// Generic repository with constraint + default type parameter
class InMemoryRepository<T extends HasId, TKey extends keyof T = keyof T> {
  private store = new Map<string, T>(); // id -> entity

  save(entity: T): T {
    this.store.set(entity.id, entity); // OK: T extends HasId so .id exists
    return entity; // return what was stored
  }

  findById(id: string): T | undefined {
    return this.store.get(id); // undefined when missing
  }

  // pluck one property from every entity, typed by the key
  pluck<K extends TKey>(key: K): Array<T[K]> {
    return [...this.store.values()].map((e) => e[key]);
  }

  // filter with a type-safe predicate
  where(pred: (e: T) => boolean): T[] {
    return [...this.store.values()].filter(pred);
  }
}

interface Wallet extends HasId {
  owner: string;
  balance: number;
}

const wallets = new InMemoryRepository<Wallet>(); // T = Wallet
wallets.save({ id: "w1", owner: "Asha", balance: 1200 });
wallets.save({ id: "w2", owner: "Ravi", balance: 80 });

console.log(wallets.pluck("balance")); // [ 1200, 80 ]  (number[])
console.log(wallets.where((w) => w.balance > 100).map((w) => w.owner)); // [ 'Asha' ]
console.log(wallets.findById("w9")?.owner ?? "not found"); // not found

// Generic Result wrapper (like an API envelope)
class ApiResult<T, E = string> {
  private constructor(
    public readonly data: T | null,
    public readonly error: E | null,
  ) {}

  static ok<T>(data: T): ApiResult<T> { // statics declare THEIR OWN <T>
    return new ApiResult<T>(data, null);
  }

  static fail<T = never>(error: string): ApiResult<T> {
    return new ApiResult<T>(null, error);
  }
}

const r = ApiResult.ok({ id: "w1", balance: 10 }); // ApiResult<{ id: string; balance: number }>
console.log(r.data?.balance, r.error); // 10 null
```

---

## 🟠 Node/Express + React Integration

```typescript
import express, { Request, Response } from "express"; // Express

interface HasId { id: string }
interface Order extends HasId { total: number; status: "PLACED" | "PAID" }

// Reusable generic controller: one class for any resource
class CrudController<T extends HasId> {
  private rows = new Map<string, T>(); // fake table; replace with SQL Server pool

  list = (_req: Request, res: Response<T[]>): void => {
    res.json([...this.rows.values()]); // typed response body: T[]
  };

  create = (req: Request<{}, T, T>, res: Response<T>): void => {
    this.rows.set(req.body.id, req.body); // body typed as T
    res.status(201).json(req.body); // echo created row
  };
}

const orders = new CrudController<Order>(); // controller for orders
const app = express();
app.use(express.json());
app.get("/orders", orders.list); // GET list
app.post("/orders", orders.create); // POST create
```

```tsx
import React from "react";
import { useEffect, useState } from "react";

// Generic class used from React: a typed API client per resource
class ResourceClient<T> {
  constructor(private readonly url: string) {} // e.g. "/orders"
  async list(): Promise<T[]> {
    const res = await fetch(this.url); // call Express
    return (await res.json()) as T[]; // cast once, at the boundary
  }
}

interface Order { id: string; total: number }
const ordersClient = new ResourceClient<Order>("/orders"); // module-level instance

export function OrderList() {
  const [orders, setOrders] = useState<Order[]>([]); // state typed with the same T
  useEffect(() => {
    ordersClient.list().then(setOrders); // result is Order[], not any
  }, []);
  return <ul>{orders.map((o) => <li key={o.id}>Rs.{o.total}</li>)}</ul>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a static member with the class type parameter
```typescript
class Registry<T> {
  static defaultItem: T; // ❌ error TS2302: Static members cannot reference class type parameters.
}
```
✅ Fix: give the static method its own type parameter: `static create<U>(): Registry<U>`.

❌ Mistake 2: Using a property without a constraint
```typescript
class Repo<T> {
  find(items: T[], id: string): T | undefined {
    return items.find((i) => i.id === id); // ❌ error TS2339: Property 'id' does not exist on type 'T'.
  }
}
```
✅ Fix: `class Repo<T extends { id: string }>`.

❌ Mistake 3: Pushing the wrong type into an instance
```typescript
class Stack<T> { private items: T[] = []; push(i: T) { this.items.push(i); } }
const s = new Stack<number>();
s.push("100"); // ❌ error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.
```

❌ Mistake 4: Assuming `new Foo()` with no arguments gives a useful `T`
```typescript
class Store<T> { items: T[] = []; }
const st = new Store(); // no error here: T silently becomes `unknown`
const first: number = st.items[0]; // ❌ error TS2322: Type 'unknown' is not assignable to type 'number'.
```
✅ Fix: write `new Store<number>()`.

---

## 🧠 Tricky Interview Question

```typescript
class Box<T> { constructor(public v: T) {} }
const a = new Box("x"); // type?
const b = new Box<"x">("x"); // type?
let c = new Box("x");
c = new Box("y"); // error?
```
Answer (checked with tsc): `a` is `Box<string>` (the literal `"x"` is widened because `v` is a mutable property) and `b` is `Box<"x">`. `c = new Box("y")` is fine because `c` is `Box<string>`. But `let d: Box<"x"> = new Box("y")` fails with `error TS2322: Type 'Box<"y">' is not assignable to type 'Box<"x">'.` To keep the literal use `new Box("x" as const)` or an explicit `<"x">`.

---

## ⚫ Interview Questions + Answers

Q1: Why can't static members use the class's `T`?
A1: Statics exist once per class, not per instance, while `T` is fixed per instance. A static method can declare its own `<U>`.

Q2: How do you restrict `T` to objects with an `id`?
A2: `class Repo<T extends { id: string }>`; the body can then use `item.id`.

Q3: Can a generic class have a default type parameter?
A3: Yes: `class Cache<V = unknown>`. Callers may omit it; defaults must come after required parameters.

Q4: Difference between a class type parameter and a method type parameter?
A4: Class `T` is fixed when the instance is created. Method `<U>` is chosen at each call (like `Box.map<U>`).

Q5: Are generics erased at runtime?
A5: Yes. `Stack<number>` and `Stack<string>` are the same JS class; `T` cannot be used in `instanceof` or `new T()`. To create instances pass a constructor: `create(ctor: new () => T)`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Containers/collections (Stack, Queue, Cache, Result)
- Repositories, API clients, controllers reused across entities
- A class's methods must relate input type to output type

❌ Avoid when:
- Only one concrete type is ever used - a plain class is simpler
- You keep adding `any` casts inside - the design needs a constraint or an interface

---

## 📊 Visual Diagram
```
 class Repo<T extends HasId> { ... }
                  │
     ┌────────────┼────────────┐
     ▼            ▼            ▼
 Repo<Wallet>  Repo<Order>  Repo<User>      (compile time, 3 types)
     │            │            │
     └────────────┴────────────┘
              one JS class                 (runtime, T is erased)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Type parameter | Placeholder `T` in `<T>` | `<T>` वाला placeholder type |
| Constraint | `T extends X` bound | `T` पर शर्त |
| Default type parameter | `T = string` fallback | `T` का default type |
| Inference | TS deduces `T` from arguments | Arguments से `T` का अनुमान |
| Type erasure | Types removed in emitted JS | Emit होने पर types हट जाते हैं |
| Repository | Class hiding data access | Data access छुपाने वाली class |

---

## ⚡ 3-Line Summary
English:
1. `class Foo<T>` lets one class work safely with many types; `T` is inferred or given at `new`.
2. Use `T extends X` to allow property access; defaults make parameters optional.
3. Statics cannot use `T`, and `T` does not exist at runtime.

Hindi:
1. `class Foo<T>` एक class को कई types के साथ safe बनाती है; `T` `new` पर infer होता या दिया जाता है।
2. Property access के लिए `T extends X` लगाओ; defaults parameters को optional बनाते हैं।
3. Statics `T` इस्तेमाल नहीं कर सकते, और runtime में `T` मौजूद नहीं होता।

---

## ➡️ Next Topic
**70. this Typing in Classes + Method Chaining** - Polymorphic `this` type, fluent builders, and why `this` can bite in callbacks.
