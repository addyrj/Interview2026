# 64. Abstract Classes
# हिंदी में: Abstract Classes (अधूरी base classes)

> TypeScript 5.x (`tsc --strict`, TS 5.9) पर verify किया गया। `abstract` classes TS 1.6 से; `abstract` constructor types (`abstract new () => T`) TS 4.2+; `override` TS 4.3+।

---

## 🔵 Simple Definition (English)
An **abstract class** is a base class that **cannot be instantiated** directly (`new Base()` is an error). It can contain **concrete members** (shared, already-implemented code) and **`abstract` members** (signatures without a body) that every non-abstract subclass **must implement**. It is a mix of an **interface** (a contract) and a **normal class** (shared implementation). Unlike interfaces, abstract classes **exist at runtime** (they emit a real JS class).

## 🔵 सरल परिभाषा (Hindi)
**Abstract class** ऐसी base class है जिसका सीधे **instance नहीं बन सकता** (`new Base()` error है)। इसमें **concrete members** (shared, पहले से लिखा code) और **`abstract` members** (बिना body के signatures) हो सकते हैं जिन्हें हर non-abstract subclass को **implement करना ही पड़ेगा**। यह **interface** (contract) और **normal class** (shared implementation) का मिश्रण है। Interfaces के उलट, abstract classes **runtime पर मौजूद** रहती हैं (असली JS class emit होती है)।

---

## 🔴 Problem it Solves
Payment gateways (Razorpay, Paytm, PhonePe) all need the same **flow**: validate -> call provider -> log -> return result. Only the "call provider" step differs. Copy-pasting the flow into each class causes drift; an interface alone cannot hold the shared flow. With an abstract class, the **template** (shared steps) lives once in the base, and each gateway must fill in just the missing abstract steps - the compiler refuses a subclass that forgets one. It prevents accidental `new BasePayment()` of an incomplete object, too.

## 🔴 यह क्यों बना? (Hindi)
Payment gateways (Razorpay, Paytm, PhonePe) सबका **flow** एक जैसा है: validate -> provider call -> log -> result। सिर्फ "provider call" वाला step अलग है। हर class में flow copy-paste करने पर drift होता है; सिर्फ interface shared flow नहीं रख सकता। Abstract class में **template** (shared steps) एक बार base में रहता है, और हर gateway को सिर्फ छूटे abstract steps भरने पड़ते हैं - कोई subclass एक भी भूले तो compiler मना कर देता है। यह अधूरे `new BasePayment()` को भी रोकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Write `abstract class Gateway { ... }`. The `abstract` keyword makes `new Gateway()` illegal.
Step 2 → Declare **abstract members** with no body: `abstract charge(paise: number): Promise<string>;`. They can be methods, properties (`abstract readonly name: string`) or accessors.
Step 3 → Add **concrete members** with real code (`pay()` that calls `this.charge(...)`): the **Template Method** pattern.
Step 4 → A subclass (`class RazorpayGateway extends Gateway`) must implement **all** abstract members or itself be `abstract`.
Step 5 → Mark implementations with `override` (TS 4.3+) so renames in the base break loudly.
Step 6 → The subclass constructor must call `super(...)` first; the abstract class **can** have a constructor (it runs when the subclass is instantiated).
Step 7 → You **can** use the abstract class as a **type**: `function run(g: Gateway)` accepts any concrete subclass (polymorphism).
Step 8 → `typeof Gateway` is an **abstract constructor**; to accept "a class that extends Gateway" use `abstract new (...args: any[]) => Gateway` (TS 4.2+) or `new () => Gateway` for concrete ones.
Step 9 → Abstract classes **exist at runtime** (usable in `instanceof`), unlike interfaces which are erased.
Step 10 → You cannot call an abstract method from the **base constructor** safely: the subclass fields are not yet initialised at that moment.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `abstract class Gateway { ... }` लिखो। `abstract` keyword `new Gateway()` को illegal बना देता है।
Step 2 → **Abstract members** बिना body के declare करो: `abstract charge(paise: number): Promise<string>;`। ये methods, properties (`abstract readonly name: string`) या accessors हो सकते हैं।
Step 3 → असली code वाले **concrete members** जोड़ो (`pay()` जो `this.charge(...)` call करता है): यही **Template Method** pattern है।
Step 4 → Subclass (`class RazorpayGateway extends Gateway`) को **सारे** abstract members implement करने होंगे वरना वह खुद `abstract` हो।
Step 5 → Implementations पर `override` लगाओ (TS 4.3+) ताकि base में rename होने पर साफ़ error आए।
Step 6 → Subclass constructor में पहले `super(...)` call करो; abstract class का constructor हो सकता है (subclass instantiate होने पर चलता है)।
Step 7 → Abstract class को **type** की तरह इस्तेमाल कर सकते हो: `function run(g: Gateway)` कोई भी concrete subclass लेता है (polymorphism)।
Step 8 → `typeof Gateway` एक **abstract constructor** है; "Gateway को extend करने वाली class" लेने के लिए `abstract new (...args: any[]) => Gateway` (TS 4.2+) या concrete के लिए `new () => Gateway`।
Step 9 → Abstract classes **runtime पर मौजूद** हैं (`instanceof` में चलती हैं), interfaces की तरह erase नहीं होतीं।
Step 10 → Base constructor से abstract method call करना सुरक्षित नहीं: उस समय subclass के fields initialise नहीं हुए होते।

---

## 🟡 Real World Example
**Razorpay-style** checkout: `abstract class PaymentGateway` has `pay(order)` (validate, call `charge`, log, build receipt) and abstract `charge()` plus abstract `readonly name`. `UpiGateway`, `CardGateway` and `NetBankingGateway` only implement `charge()`. **Swiggy's** notification system: `abstract class Notifier` implements retries and logging, while `SmsNotifier`, `PushNotifier`, `EmailNotifier` implement `deliver()`.

## 🟡 Real Example Hindi mein
**Razorpay जैसा** checkout: `abstract class PaymentGateway` में `pay(order)` (validate, `charge` call, log, receipt) है और abstract `charge()` तथा abstract `readonly name`। `UpiGateway`, `CardGateway` और `NetBankingGateway` सिर्फ `charge()` implement करती हैं। **Swiggy** का notification system: `abstract class Notifier` retries और logging संभालती है, जबकि `SmsNotifier`, `PushNotifier`, `EmailNotifier` `deliver()` implement करती हैं।

---

## 💻 Code Example — Basic

```typescript
// Abstract base: shared flow + missing steps
abstract class PaymentGateway {
  abstract readonly name: string; // every gateway must declare its name
  abstract charge(paise: number): string; // provider-specific step (no body here)

  // Concrete method: the template that calls the abstract step
  pay(paise: number): string {
    if (paise <= 0) throw new RangeError("amount must be positive"); // shared validation
    const ref = this.charge(paise); // call the subclass-specific part
    return `[${this.name}] paid ₹${paise / 100} ref=${ref}`; // shared formatting
  }
}

// Concrete subclass: must implement every abstract member
class UpiGateway extends PaymentGateway {
  readonly name = "UPI"; // implements the abstract property
  charge(paise: number): string { return `upi_${paise}`; } // implements the abstract method
}

class CardGateway extends PaymentGateway {
  readonly name = "CARD"; // implements the abstract property
  charge(paise: number): string { return `card_${paise}`; } // implements the abstract method
}

// Polymorphism: the abstract class is usable as a type
function checkout(g: PaymentGateway, paise: number): string { return g.pay(paise); } // any subclass works
console.log(checkout(new UpiGateway(), 49900)); // [UPI] paid ₹499 ref=upi_49900
console.log(checkout(new CardGateway(), 1000)); // [CARD] paid ₹10 ref=card_1000

// ❌ Cannot instantiate an abstract class
const g = new PaymentGateway();
// error TS2511: Cannot create an instance of an abstract class.

// ❌ A subclass that forgets an abstract member
class BrokenGateway extends PaymentGateway {
  readonly name = "BROKEN"; // charge() is missing
}
// error TS2515: Non-abstract class 'BrokenGateway' does not implement inherited abstract member charge from class 'PaymentGateway'.
```

## 💻 Code Example — Advanced

```typescript
// Template Method with hooks, protected helpers and an async abstract step
abstract class Notifier {
  protected constructor(protected readonly maxRetries = 2) {} // abstract-ish: only subclasses call super

  protected abstract deliver(to: string, msg: string): Promise<void>; // the one thing subclasses implement
  protected onFail(attempt: number, err: unknown): void { // optional hook with a default
    console.log(`attempt ${attempt} failed: ${(err as Error).message}`); // default logging
  }

  async send(to: string, msg: string): Promise<boolean> { // the template
    for (let attempt = 1; attempt <= this.maxRetries + 1; attempt++) { // retry loop shared by all
      try { await this.deliver(to, msg); return true; } // success path
      catch (e) { this.onFail(attempt, e); } // failure hook (overridable)
    }
    return false; // all attempts failed
  }
}

class FlakySms extends Notifier {
  private calls = 0; // simulate failures
  constructor() { super(2); } // pass retries to the base
  protected override async deliver(to: string, msg: string): Promise<void> {
    if (++this.calls < 3) throw new Error("gateway timeout"); // fail twice, then succeed
    console.log(`SMS to ${to}: ${msg}`); // delivered
  }
}
void new FlakySms().send("+91-98xxxxxx01", "Order placed").then((ok) => console.log("sent:", ok));
// attempt 1 failed: gateway timeout
// attempt 2 failed: gateway timeout
// SMS to +91-98xxxxxx01: Order placed
// sent: true

// Abstract constructor types: factories that accept abstract classes (TS 4.2+)
type AbstractCtor<T> = abstract new (...args: never[]) => T; // "a class that builds T, may be abstract"
function isGatewayClass(c: AbstractCtor<PaymentGateway2>): string { return c.name; } // just inspect the class
abstract class PaymentGateway2 { abstract id(): string; } // abstract class for the demo
class A2 extends PaymentGateway2 { id(): string { return "a2"; } } // concrete class
console.log(isGatewayClass(A2), isGatewayClass(PaymentGateway2)); // A2 PaymentGateway2

// instanceof works because the abstract class is a real runtime class
const impl: PaymentGateway2 = new A2(); // typed as the abstract base
console.log(impl instanceof PaymentGateway2); // true

// An abstract class may implement an interface and leave members abstract
interface Auditable { auditLog(): string[] } // contract
abstract class AuditedService implements Auditable {
  protected logs: string[] = []; // shared state
  abstract auditLog(): string[]; // pass the obligation down (allowed)
}
class RefundService extends AuditedService {
  auditLog(): string[] { return this.logs; } // implement it here
}
console.log(new RefundService().auditLog().length); // 0

// Abstract members can be accessors/properties, and a subclass can stay abstract
abstract class Shape { abstract get area(): number; describe(): string { return `area=${this.area}`; } }
abstract class Polygon extends Shape { abstract sides: number; } // still abstract: adds more requirements
class Square extends Polygon { sides = 4; constructor(private s: number) { super(); } get area(): number { return this.s ** 2; } }
console.log(new Square(3).describe(), new Square(3).sides); // area=9 4

// ❌ Abstract methods cannot have bodies
abstract class Bad { abstract run(): void { } }
// error TS1245: Method 'run' cannot have an implementation because it is marked abstract.
```

---

## 🟠 Node/Express + React Integration

```typescript
import express from "express";

// Abstract repository: shared SQL-style flow, subclasses define table + mapping
abstract class Repository<T extends { id: number }> {
  protected abstract readonly table: string; // table name per entity
  protected abstract map(row: Record<string, unknown>): T; // row -> entity

  async findById(id: number): Promise<T | null> {
    const rows: Record<string, unknown>[] = await this.query(`SELECT * FROM ${this.table} WHERE Id = @id`, { id }); // shared query flow
    return rows[0] ? this.map(rows[0]) : null; // shared null handling + mapping
  }

  // Fake driver for the demo; real code would use mssql's pool.request().input(...)
  protected async query(_sql: string, params: { id: number }): Promise<Record<string, unknown>[]> {
    return [{ Id: params.id, AmountPaise: 49900 }]; // pretend result
  }
}

interface Order { id: number; amount: number } // domain type
class OrderRepository extends Repository<Order> {
  protected readonly table = "Orders"; // satisfies the abstract property
  protected map(r: Record<string, unknown>): Order { return { id: Number(r.Id), amount: Number(r.AmountPaise) / 100 }; } // mapping
}

const repo = new OrderRepository(); // concrete repository
const app = express(); // create app
app.get("/orders/:id", async (req, res) => {
  const order = await repo.findById(Number(req.params.id)); // typed Order | null
  if (!order) { res.status(404).json({ error: "not found" }); return; } // handle missing
  res.json(order); // respond
});
```

```tsx
import { Component, type ReactNode } from "react";

// Abstract React class component base: shared error handling, subclasses implement renderContent
abstract class SafeView<P> extends Component<P, { failed: boolean }> {
  state = { failed: false }; // shared state
  protected abstract renderContent(): ReactNode; // subclass UI

  static getDerivedStateFromError(): { failed: boolean } { return { failed: true }; } // runs on render error
  render(): ReactNode { return this.state.failed ? <p>Oops</p> : this.renderContent(); } // template
}

export class OrderSummary extends SafeView<{ total: number }> {
  protected renderContent(): ReactNode { return <p>Total ₹{this.props.total}</p>; } // only the unique part
}
```

```typescript
// Redux-friendly: abstract class for non-store services (keep the store plain objects)
abstract class ApiClient {
  protected abstract baseUrl: string; // provided by subclass
  url(path: string): string { return `${this.baseUrl}${path}`; } // shared helper
}
class OrdersApi extends ApiClient { protected baseUrl = "https://api.example.com/orders"; } // concrete
console.log(new OrdersApi().url("/42")); // https://api.example.com/orders/42
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling an abstract method from the base constructor
```typescript
abstract class Base {
  constructor() { console.log(this.label()); } // runs BEFORE subclass fields are set
  abstract label(): string;
}
class Child extends Base {
  private prefix = "child"; // initialised AFTER super() returns
  label(): string { return this.prefix.toUpperCase(); } // prefix is still undefined here!
}
// new Child() -> TypeError: Cannot read properties of undefined (reading 'toUpperCase')   (verified with tsx)
```
✅ Correct: do not call abstract/overridable methods from a constructor; use a separate `init()` or a factory.

❌ Mistake 2: Using an abstract class where an interface is enough
```typescript
// Wrong: forces inheritance for a pure contract and emits runtime code
abstract class Logger { abstract log(msg: string): void; }
// Right: an interface is erased, can be implemented by classes AND plain objects
interface ILogger { log(msg: string): void }
const consoleLogger: ILogger = { log: (m) => console.log(m) }; // plain object satisfies it
```

❌ Mistake 3: Forgetting `abstract` on the subclass that stays incomplete
```typescript
abstract class Base2 { abstract a(): void; abstract b(): void; }
class Half extends Base2 { a(): void {} } // ❌ b() missing
// error TS2515: Non-abstract class 'Half' does not implement inherited abstract member b from class 'Base2'.
```
✅ Correct: mark `Half` as `abstract class Half`, or implement `b()`.

---

## 🧠 Tricky Interview Question

```typescript
abstract class Animal {
  abstract speak(): string;
  constructor() { console.log(this.speak()); }
}
class Dog extends Animal {
  sound = "woof";
  speak(): string { return this.sound; }
}
new Dog();
```
**Answer:** It prints `undefined`. The `Animal` constructor runs **before** `Dog`'s field initialisers, so `this.sound` is still `undefined` when `speak()` is called from the base constructor (TS does not warn). `useDefineForClassFields` does not change this ordering: fields of the subclass are always initialised **after** `super()` returns. Fix: avoid calling overridable methods in constructors, or make `speak()` not depend on subclass fields (e.g. return a literal).

---

## ⚫ Interview Questions + Answers

Q1: Abstract class vs interface - when to use which?
A1: Use an **interface** for a pure contract (no code, erased at runtime, can be implemented by many unrelated classes/objects, multiple `implements`). Use an **abstract class** when you want to share **implementation** (template method, default behaviour, protected state/helpers), need `instanceof` or constructors, and subclasses form an "is-a" hierarchy. A class can `implements` many interfaces but `extends` only one class.

Q2: Can an abstract class have a constructor, and can you call `new` on it?
A2: Yes it can have a constructor (called via `super(...)` from subclasses) but `new AbstractClass()` is `TS2511`. A `protected constructor` is a related trick to block `new` on a concrete class from outside (error `TS2674`).

Q3: What is the Template Method pattern and how do abstract classes support it?
A3: The base class defines the **skeleton** of an algorithm in a concrete method (`pay`, `send`) and delegates **variable steps** to abstract/protected hooks (`charge`, `deliver`). Subclasses fill in steps without changing the order. TS enforces that all steps exist (abstract) and lets hooks have defaults (concrete protected methods).

Q4: How do you type a parameter that accepts "a class that extends abstract Base" (the class itself, not an instance)?
A4: For concrete subclasses: `new (...args: any[]) => Base`. If the class itself may be abstract, use an **abstract construct signature** `abstract new (...args: any[]) => Base` (TS 4.2+). Remember `typeof Base` is the constructor type with statics too.

Q5: Are abstract members present in the emitted JavaScript?
A5: No - `abstract` methods/properties emit nothing; only concrete members exist. The abstract **class** itself is emitted as a regular class (so `instanceof` works), and TS adds no runtime check preventing `new` - only the compiler does, so JS callers can still instantiate it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several subclasses share a **workflow** and differ in a few steps (gateways, notifiers, repositories, parsers)
- You need shared protected state/helpers and `instanceof` checks
- You want the compiler to force subclasses to implement required members

❌ Avoid when:
- A pure contract is enough - use an `interface` (cheaper, more flexible, mockable with plain objects)
- The hierarchy is getting deep (3+ levels) - prefer composition (inject a strategy object)
- You need multiple inheritance - use interfaces/mixins (topic 68)

---

## 📊 Visual Diagram
```
                 abstract class PaymentGateway
                 ┌─────────────────────────────────────────┐
                 │ abstract readonly name: string          │  ← must implement
                 │ abstract charge(paise): string          │  ← must implement
                 │                                         │
                 │ pay(paise) {                            │  ← shared template
                 │    validate → this.charge() → format    │
                 │ }                                       │
                 └───────────────▲─────────────▲───────────┘
                                 │             │
                      UpiGateway─┘             └─CardGateway
                      name = "UPI"                name = "CARD"
                      charge() {...}              charge() {...}

   new PaymentGateway()  ❌ TS2511        class Broken (no charge) ❌ TS2515
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Abstract class | Base class that cannot be instantiated | जिसका instance नहीं बनता वाली base class |
| Abstract member | Signature without body, subclass must implement | बिना body का member, subclass को implement करना है |
| Template Method | Base defines flow, subclass fills steps | base flow तय करती है, subclass steps भरती है |
| Concrete member | Fully implemented member | पूरी तरह implement किया member |
| Polymorphism | Using subclasses through the base type | base type से subclasses इस्तेमाल करना |
| Abstract constructor type | `abstract new (...) => T` | abstract class लेने वाला constructor type |

---

## ⚡ 3-Line Summary
English:
1. An abstract class is a non-instantiable base with shared code plus `abstract` members subclasses must implement.
2. It enables the Template Method pattern (gateways, notifiers, repositories) and survives at runtime for `instanceof`.
3. Prefer interfaces for pure contracts, and never call abstract methods from the base constructor.

Hindi:
1. Abstract class ऐसी base है जिसका instance नहीं बनता, इसमें shared code और `abstract` members होते हैं जिन्हें subclasses implement करती हैं।
2. यह Template Method pattern (gateways, notifiers, repositories) संभव बनाती है और `instanceof` के लिए runtime पर मौजूद रहती है।
3. Pure contracts के लिए interfaces चुनो, और base constructor से abstract methods कभी call मत करो।

---

## ➡️ Next Topic
**65. implements vs extends** — contracts versus inheritance and when to combine them.
