# 66. Constructor Parameter Properties
# हिंदी में: Constructor Parameter Properties (constructor के parameters से ही properties बनाना)

> Verified with TypeScript 5.9 (`tsc --strict`). `erasableSyntaxOnly` flag = TS 5.8+. `override` keyword = TS 4.3+.

---

## 🔵 Simple Definition (English)
A **constructor parameter property** is a shortcut: if you put an access modifier (`public`, `private`, `protected`) or `readonly` in front of a constructor parameter, TypeScript automatically **declares a class field with the same name and assigns the argument to it**. One line replaces three (field declaration, parameter, `this.x = x`).

## 🔵 सरल परिभाषा (Hindi)
**Constructor parameter property** एक shortcut है: अगर constructor के parameter के आगे access modifier (`public`, `private`, `protected`) या `readonly` लगा दो, तो TypeScript अपने आप **उसी नाम का class field declare कर देता है और argument को उसमें assign कर देता है**। तीन lines (field declaration, parameter, `this.x = x`) की जगह सिर्फ एक line।

---

## 🔴 Problem it Solves
In service-heavy backends (Express + SQL Server) almost every class is "take dependencies in the constructor and store them". Without the shortcut you write each name **three times**: once as a field, once as a parameter, once as `this.name = name`. With 5 dependencies that is 15 lines of pure boilerplate, and it is easy to forget one assignment. Parameter properties remove this noise and keep field and parameter always in sync.

## 🔴 यह क्यों बना? (Hindi)
Backend services (Express + SQL Server) में लगभग हर class "dependencies को constructor में लो और store करो" वाली होती है। shortcut के बिना हर नाम **तीन बार** लिखना पड़ता है: field, parameter, और `this.name = name`। 5 dependencies = 15 lines का boilerplate, और कोई assignment भूलना आसान है। Parameter properties इस शोर को हटाती हैं और field व parameter को हमेशा sync रखती हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → You write `constructor(private readonly db: Database) {}`.
Step 2 → The compiler sees a modifier on the parameter, so it knows this is not a plain parameter.
Step 3 → It declares a field `db` of the same type with the same modifiers (`private readonly`).
Step 4 → At the start of the constructor body it emits `this.db = db`.
Step 5 → If the class `extends` another class, the assignments are emitted **right after `super(...)`**.
Step 6 → Parameters without a modifier stay normal local parameters (no field is created).

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → तुम लिखते हो `constructor(private readonly db: Database) {}`।
Step 2 → Compiler parameter पर modifier देखता है, यानी यह साधारण parameter नहीं है।
Step 3 → वह उसी type और उन्हीं modifiers (`private readonly`) के साथ field `db` declare कर देता है।
Step 4 → Constructor body की शुरुआत में `this.db = db` emit करता है।
Step 5 → अगर class किसी दूसरी class को `extends` करती है तो assignments **`super(...)` के ठीक बाद** emit होते हैं।
Step 6 → बिना modifier वाले parameters सामान्य local parameters ही रहते हैं (field नहीं बनता)।

---

## 🟡 Real World Example
**Razorpay-style `PaymentService`**: it needs a `PaymentGateway`, a `Logger` and a `maxRetries` number. In a NestJS/Express codebase this is the classic "constructor injection" pattern. The class never changes these dependencies after creation, so each is `private readonly`. Writing them as parameter properties makes the class header itself the documentation of what the service depends on.

## 🟡 Real Example Hindi mein
**Razorpay-जैसी `PaymentService`**: उसे एक `PaymentGateway`, एक `Logger` और एक `maxRetries` number चाहिए। NestJS/Express codebase में यह classic "constructor injection" pattern है। Class बनने के बाद ये dependencies बदलती नहीं, इसलिए हर एक `private readonly` है। Parameter properties से class का header ही बता देता है कि service किन चीज़ों पर निर्भर है।

---

## 💻 Code Example — Basic

```typescript
// Long way: every name is written three times
class OrderLong {
  readonly id: string; // 1) declare the field
  amount: number; // 1) declare the field

  constructor(id: string, amount: number) { // 2) take it as a parameter
    this.id = id; // 3) assign it manually
    this.amount = amount; // 3) assign it manually
  }
}

// Short way: parameter properties = declare + assign in one place
class Order {
  constructor(
    public readonly id: string, // becomes a public readonly field
    public amount: number, // becomes a public field
    private note: string = "none", // private field with a default value
    discount: number = 0, // NO modifier -> plain parameter, not a field
  ) {
    // discount is usable here only (it is just a local variable)
    this.amount = amount - discount; // fields are already assigned at this point
  }

  describe(): string {
    // note is private, but accessible inside the class
    return `${this.id}: Rs.${this.amount} (${this.note})`;
  }
}

const o = new Order("ORD-1", 500, "no onions", 50); // create an order
console.log(o.describe()); // ORD-1: Rs.450 (no onions)
console.log(o.amount); // 450 (public field)
// console.log(o.note);   // would be an error: note is private
const legacy = new OrderLong("ORD-0", 100); // long form works the same
console.log(legacy.id, legacy.amount); // ORD-0 100
```

## 💻 Code Example — Advanced

```typescript
// Dependency-injection style service with inheritance (Razorpay / Swiggy style)
interface Logger {
  info(msg: string): void; // minimal logger contract
}

interface PaymentGateway {
  charge(orderId: string, paise: number): Promise<{ ok: boolean; txnId: string }>;
}

class ConsoleLogger implements Logger {
  // parameter property with a default value
  constructor(private readonly prefix: string = "[app]") {}

  info(msg: string): void {
    console.log(`${this.prefix} ${msg}`); // use the auto-created field
  }
}

class BaseService {
  // protected: visible in this class and in subclasses only
  constructor(protected readonly logger: Logger) {}
}

class PaymentService extends BaseService {
  constructor(
    logger: Logger, // plain parameter: just forwarded to super
    private readonly gateway: PaymentGateway, // new private field
    private readonly maxRetries: number = 2, // new private field with default
  ) {
    super(logger); // MUST be called first, then the fields are assigned
  }

  async pay(orderId: string, rupees: number): Promise<string> {
    for (let attempt = 1; attempt <= this.maxRetries + 1; attempt++) {
      // call the injected gateway (amounts go in paise)
      const res = await this.gateway.charge(orderId, rupees * 100);
      this.logger.info(`attempt ${attempt} for ${orderId}: ${res.ok}`); // inherited protected field
      if (res.ok) return res.txnId; // success -> return transaction id
    }
    throw new Error(`Payment failed for ${orderId}`); // all retries used
  }
}

// A fake gateway that fails once and then succeeds
let calls = 0;
const fakeGateway: PaymentGateway = {
  async charge(orderId, paise) {
    calls++; // count calls
    return { ok: calls > 1, txnId: `txn_${orderId}_${paise}` };
  },
};

const svc = new PaymentService(new ConsoleLogger("[pay]"), fakeGateway);
svc.pay("ORD-7", 250).then((id) => console.log("paid:", id)); // retries once, then pays
```

---

## 🟠 Node/Express + React Integration

```typescript
import express, { Request, Response } from "express"; // Express + its types

// Repository with the SQL Server pool injected through a parameter property
interface SqlPool {
  query(sql: string, params: unknown[]): Promise<{ rows: Array<{ id: string; total: number }> }>;
}

class OrderRepository {
  constructor(private readonly pool: SqlPool) {} // one line = field + assignment

  async findById(id: string) {
    const r = await this.pool.query("SELECT id, total FROM Orders WHERE id = @p0", [id]);
    return r.rows[0]; // first row or undefined at runtime
  }
}

class OrderController {
  constructor(private readonly repo: OrderRepository) {} // controller depends on repo

  // arrow property so `this` is kept when passed to Express
  getOne = async (req: Request<{ id: string }>, res: Response): Promise<void> => {
    const order = await this.repo.findById(req.params.id); // typed route param
    if (!order) {
      res.status(404).json({ error: "not found" }); // no such order
      return;
    }
    res.json(order); // send JSON to the React client
  };
}

const fakePool: SqlPool = { query: async () => ({ rows: [{ id: "1", total: 99 }] }) };
const controller = new OrderController(new OrderRepository(fakePool)); // composition root
const app = express(); // create the app
app.get("/orders/:id", controller.getOne); // wire the route
```

```tsx
import React from "react"; // React import (needed for React.useState)
// React side: parameter properties are also handy for a small API client class
class OrdersApi {
  constructor(private readonly baseUrl: string) {} // base URL stored once

  async get(id: string): Promise<{ id: string; total: number }> {
    const res = await fetch(`${this.baseUrl}/orders/${id}`); // call Express
    return (await res.json()) as { id: string; total: number }; // trust the contract
  }
}

export function OrderTotal({ api, id }: { api: OrdersApi; id: string }) {
  const [total, setTotal] = React.useState<number | null>(null); // typed state
  React.useEffect(() => {
    api.get(id).then((o) => setTotal(o.total)); // fetch on mount
  }, [api, id]);
  return <span>{total ?? "..."}</span>; // show placeholder until loaded
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assuming a parameter without a modifier becomes a field
```typescript
class Cart {
  constructor(items: string[]) {} // no modifier -> NOT a field
  count(): number {
    return this.items.length; // ❌ error TS2339: Property 'items' does not exist on type 'Cart'.
  }
}
```
✅ Fix: write `constructor(private items: string[]) {}`.

❌ Mistake 2: Assigning to a `readonly` parameter property after construction
```typescript
class Payment {
  constructor(public readonly txnId: string) {}
}
const p = new Payment("t1");
p.txnId = "t2"; // ❌ error TS2540: Cannot assign to 'txnId' because it is a read-only property.
```

❌ Mistake 3: Touching `this` before `super()` in a subclass
```typescript
class Base {
  constructor(protected name: string) {}
}
class Child extends Base {
  constructor(private extra: number) {
    console.log(this.extra); // ❌ error TS17009: 'super' must be called before accessing 'this' in the constructor of a derived class.
    super("x");
  }
}
```

❌ Mistake 4: Parameter properties in a project that uses `erasableSyntaxOnly` (TS 5.8+) or Node's built-in type stripping
```typescript
class User {
  constructor(public name: string) {} // ❌ error TS1294: This syntax is not allowed when 'erasableSyntaxOnly' is enabled.
}
```
Node 22+ `--experimental-strip-types` cannot run this syntax, because it needs code generation, not just erasing types.

---

## 🧠 Tricky Interview Question

```typescript
class B {
  z = this.y * 2; // field initializer that reads a parameter property
  constructor(public y: number) { // y is assigned in the constructor
    console.log(this.z); // what prints for new B(5)?
  }
}
new B(5);
```
Answer: the compiler reports `error TS2729: Property 'y' is used before its initialization.` - and if you run it anyway (tsx/esbuild, target ES2022 with `useDefineForClassFields`) it prints `NaN`, because the class-field initializer `z = this.y * 2` runs **before** the constructor assigns `this.y = y` (`undefined * 2`). Fix: assign inside the constructor body (`this.z = this.y * 2`), which prints `10`. Interview point: parameter properties are assigned at the start of the constructor body, not before field initializers.

---

## ⚫ Interview Questions + Answers

Q1: What exactly is a parameter property?
A1: A constructor parameter that carries `public`, `private`, `protected`, `readonly` (or `override`). TS declares a field of that name and assigns the argument automatically.

Q2: Does `constructor(x: number)` create a field `x`?
A2: No. Only parameters with a modifier become fields. Without a modifier `x` is a local parameter that disappears after the constructor ends.

Q3: Is this ES syntax? What does the compiler emit?
A3: No, it is TypeScript-only. The compiler emits `this.x = x;` at the start of the constructor (after `super()` when extending). That is why Babel/esbuild/tsx need TS support and why Node's type stripping and `erasableSyntaxOnly` reject it (same family as `enum` and `namespace`).

Q4: Can you use `#private` with a parameter property?
A4: No. ES private names (`#x`) cannot be used on parameters. Use TS `private` (compile-time only) or declare `#x` as a normal field and assign it manually.

Q5: Why is it popular in NestJS/Angular?
A5: Constructor injection. Frameworks read the constructor parameter types (via `emitDecoratorMetadata`) to know what to inject, and parameter properties turn each injected dependency into a field in one line.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Constructor only stores dependencies (services, repositories, config)
- Small value objects with a few `readonly` fields
- Your team already uses NestJS/Angular style DI

❌ Avoid when:
- Project enables `erasableSyntaxOnly` or runs TS natively in Node (type stripping)
- You need `#private` fields or complex field initialization order
- A class has many parameters - an options object (`constructor(opts: Options)`) reads better

---

## 📊 Visual Diagram
```
 YOU WRITE                              COMPILER GENERATES
 ─────────────────────────────          ─────────────────────────────
 class Svc {                            class Svc {
   constructor(                           db;            // field
     private readonly db: Db,             log;           // field
     protected log: Logger,               constructor(db, log, retries) {
     retries: number,   <- no modifier      this.db = db;
   ) {}                                     this.log = log;
 }                                        }   // retries NOT stored
                                        }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Parameter property | Constructor param with a modifier that also becomes a field | Modifier वाला constructor param जो field भी बन जाता है |
| Access modifier | `public` / `private` / `protected` | पहुँच (access) तय करने वाला keyword |
| `readonly` | Can be set only at construction | सिर्फ construction में set हो सकता है |
| Constructor injection | Passing dependencies via constructor | Dependencies को constructor से देना |
| `erasableSyntaxOnly` | TS 5.8 flag that bans non-erasable syntax | वह flag जो ऐसा syntax रोकता है जिसे सिर्फ type हटाकर नहीं चलाया जा सकता |
| Boilerplate | Repeated code with no real logic | बार-बार लिखा जाने वाला बेकार code |

---

## ⚡ 3-Line Summary
English:
1. A modifier on a constructor parameter makes TypeScript declare and assign a field automatically.
2. Great for dependency injection (`private readonly repo: Repo`); parameters without a modifier stay local.
3. It is not erasable syntax, so it fails under `erasableSyntaxOnly` and Node type stripping.

Hindi:
1. Constructor parameter पर modifier लगाने से TypeScript field अपने आप declare और assign करता है।
2. Dependency injection के लिए बढ़िया (`private readonly repo: Repo`); बिना modifier वाला parameter local ही रहता है।
3. यह erasable syntax नहीं है, इसलिए `erasableSyntaxOnly` और Node type stripping में fail होता है।

---

## ➡️ Next Topic
**68. Mixins** - Combine behaviour from several small classes (Timestamped, Activatable) into one class, with full type safety.
