# 61. Classes in TypeScript
# हिंदी में: TypeScript में Classes

> TypeScript 5.x (`tsc --strict`, TS 5.9) पर verify किया गया। `strictPropertyInitialization` `strict` का हिस्सा (TS 2.7+); `override` keyword TS 4.3+; `accessor` keyword और standard decorators TS 5.0+; `useDefineForClassFields` ES2022 target पर default `true`।

---

## 🔵 Simple Definition (English)
A **class** is a blueprint for objects: it declares **fields** (data), a **constructor** (setup), and **methods** (behaviour). TypeScript adds **static types** to JavaScript classes: every field has a type, constructor and method parameters are checked, and `strict` mode verifies that fields are **definitely assigned**. A class declares both a **value** (the constructor function) and a **type** (the instance shape).

## 🔵 सरल परिभाषा (Hindi)
**Class** objects का blueprint है: इसमें **fields** (data), **constructor** (setup) और **methods** (behaviour) declare होते हैं। TypeScript JavaScript classes में **static types** जोड़ता है: हर field का type होता है, constructor और method के parameters check होते हैं, और `strict` mode जाँचता है कि fields **पक्का assign** हुए हैं। Class एक साथ **value** (constructor function) और **type** (instance की shape) दोनों declare करती है।

---

## 🔴 Problem it Solves
Plain JS classes let you forget to initialise a field, call a method with the wrong argument, or read `this.total` that was never set - failing only at runtime (`undefined is not a function`). In a payments or cart service this means NaN totals or missing-field crashes in production. TypeScript classes give compile-time checks for field initialisation, method signatures, `this` usage, inheritance (`override`) and interface contracts, while compiling to normal JS classes.

## 🔴 यह क्यों बना? (Hindi)
Plain JS classes में field initialise करना भूल सकते हो, method को गलत argument से call कर सकते हो, या ऐसा `this.total` पढ़ सकते हो जो कभी set नहीं हुआ - सब runtime पर fail होता है (`undefined is not a function`)। Payments या cart service में इसका मतलब NaN totals या missing-field crashes। TypeScript classes compile time पर field initialisation, method signatures, `this` usage, inheritance (`override`) और interface contracts check करती हैं, और normal JS classes में compile होती हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Declare fields with types: `amount: number;`. Under `strict`, each field must be assigned in the constructor or have an initialiser (`strictPropertyInitialization`).
Step 2 → `constructor(...)` receives and validates arguments; assign with `this.amount = amount`.
Step 3 → Methods are normal functions on the prototype; their parameter and return types are checked. `this` inside refers to the instance.
Step 4 → Optional fields use `?` (type becomes `T | undefined`); a field assigned later can use the definite-assignment assertion `field!: T` (use sparingly).
Step 5 → **Getters/setters** (`get total()` / `set total(v)`) look like properties. A getter alone makes the property read-only.
Step 6 → Inheritance with `extends` + `super(...)`; mark overridden methods with **`override`** (TS 4.3+, enforced by `noImplicitOverride`).
Step 7 → A class name is also a **type**: `const o: Order = new Order(...)`. The type contains only **instance** members (not static ones).
Step 8 → Classes are **structurally typed**: any object with the same public shape matches the class type (private/protected members make it nominal-ish, topic 62).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Fields को types के साथ declare करो: `amount: number;`। `strict` में हर field constructor में assign हो या initialiser रखे (`strictPropertyInitialization`)।
Step 2 → `constructor(...)` arguments लेता और validate करता है; `this.amount = amount` से assign।
Step 3 → Methods prototype पर normal functions हैं; उनके parameter और return types check होते हैं। अंदर `this` instance है।
Step 4 → Optional fields के लिए `?` (type `T | undefined` हो जाता है); बाद में assign होने वाले field के लिए definite-assignment assertion `field!: T` (कम इस्तेमाल करो)।
Step 5 → **Getters/setters** (`get total()` / `set total(v)`) property जैसे दिखते हैं। सिर्फ getter हो तो property read-only बन जाती है।
Step 6 → `extends` + `super(...)` से inheritance; override किए methods पर **`override`** लगाओ (TS 4.3+, `noImplicitOverride` से enforce)।
Step 7 → Class का नाम एक **type** भी है: `const o: Order = new Order(...)`। इस type में सिर्फ **instance** members होते हैं (static नहीं)।
Step 8 → Classes **structurally typed** हैं: जिस object की public shape वही हो वह class type से match करता है (private/protected members इसे nominal-जैसा बना देते हैं, topic 62)।

---

## 🟡 Real World Example
A **Swiggy** backend `Cart` class holds `items`, `couponCode` and methods `addItem`, `applyCoupon` and a `total` getter. The `Order` class extends a `BaseEntity` (id, createdAt). In a **Razorpay**-like service, `PaymentService` is a class whose constructor receives a `Database` and a `Logger`, and whose methods (`capture`, `refund`) are typed so that calling `refund(orderId)` with a number fails to compile.

## 🟡 Real Example Hindi mein
**Swiggy** backend की `Cart` class में `items`, `couponCode` और methods `addItem`, `applyCoupon` तथा `total` getter है। `Order` class `BaseEntity` (id, createdAt) को extend करती है। **Razorpay** जैसी service में `PaymentService` class है जिसके constructor को `Database` और `Logger` मिलते हैं, और methods (`capture`, `refund`) इस तरह typed हैं कि `refund(orderId)` को number देने पर compile नहीं होता।

---

## 💻 Code Example — Basic

```typescript
// A cart line item type
interface CartItem { sku: string; price: number; qty: number } // plain data

class Cart {
  // Fields: typed, and assigned either here or in the constructor (strict mode)
  items: CartItem[] = []; // initialiser: starts empty
  couponCode?: string; // optional: string | undefined
  readonly userId: string; // set once in constructor, never changed

  constructor(userId: string) { // setup code
    this.userId = userId; // assign required field
  }

  // Method: parameter and return types are checked
  addItem(sku: string, price: number, qty = 1): this {
    this.items.push({ sku, price, qty }); // mutate state
    return this; // allow chaining: cart.addItem(...).addItem(...)
  }

  // Getter: accessed like a property (cart.total), no parentheses
  get total(): number {
    return this.items.reduce((sum, i) => sum + i.price * i.qty, 0); // sum of price * qty
  }

  applyCoupon(code: string): void {
    this.couponCode = code.toUpperCase(); // normalise and store
  }
}

const cart = new Cart("u1"); // instance of Cart
cart.addItem("BIRYANI", 250, 2).addItem("RAITA", 40); // chaining works because we return this
cart.applyCoupon("save10"); // sets couponCode
console.log(cart.total, cart.couponCode); // 540 SAVE10

// ❌ Wrong argument type
cart.addItem("NAAN", "30");
// error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.

// ❌ Assigning to a getter-only property
cart.total = 0;
// error TS2540: Cannot assign to 'total' because it is a read-only property.
```

## 💻 Code Example — Advanced

```typescript
// Strict property initialisation: every field must be definitely assigned
class Payment {
  id: string; // no initialiser -> must be set in constructor
  amount: number; // same
  status: "CREATED" | "CAPTURED" | "REFUNDED" = "CREATED"; // initialiser with literal union

  constructor(id: string, amount: number) {
    this.id = id; // assigned
    this.amount = amount; // assigned
  }
}

// ❌ Forgetting to assign a field
class BrokenPayment {
  id: string;
  amount: number;
  constructor(id: string) { this.id = id; } // amount never set
}
// error TS2564: Property 'amount' has no initializer and is not definitely assigned in the constructor.

// Inheritance + override + super
class BaseEntity {
  readonly createdAt: Date = new Date(0); // fixed date for deterministic demo
  describe(): string { return `entity@${this.createdAt.getFullYear()}`; } // base behaviour
}
class Order extends BaseEntity {
  constructor(public readonly orderId: string, private amountPaise: number) { super(); } // super() first
  override describe(): string { return `order ${this.orderId} ₹${this.amountPaise / 100}`; } // override keyword (TS 4.3+)
}
const order = new Order("ord_1", 49900); // Order instance
console.log(order.describe()); // order ord_1 ₹499

// ❌ `override` on a method that does not exist in the base class
class TypoOrder extends BaseEntity {
  override describee(): string { return "x"; } // typo
}
// error TS4117: This member cannot have an 'override' modifier because it is not declared in the base class 'BaseEntity'. Did you mean 'describe'?

// Getters + setters with validation
class Wallet {
  private _balance = 0; // backing field (underscore is a convention)
  get balance(): number { return this._balance; } // read access
  set balance(v: number) { // write access with a guard
    if (v < 0) throw new RangeError("balance cannot be negative"); // invariant
    this._balance = v; // store
  }
}
const w = new Wallet(); // create wallet
w.balance = 500; // calls the setter
console.log(w.balance); // 500

// Class as a type AND as a value; static members are NOT on the instance type
class IdGen {
  static next = 1; // static: lives on the class itself
  readonly id = IdGen.next++; // each instance takes the next number
}
const a = new IdGen(); // id = 1
const b = new IdGen(); // id = 2
console.log(a.id, b.id, IdGen.next); // 1 2 3

// Structural typing: a plain object can satisfy a class type (public members only)
class Point { constructor(public x: number, public y: number) {} } // class with public fields
const p: Point = { x: 1, y: 2 }; // OK: same shape, no `new` needed
console.log(p.x + p.y); // 3

// Class expressions and generics in a field
const Counter = class { count = 0; inc(): number { return ++this.count; } }; // anonymous class
console.log(new Counter().inc()); // 1
```

---

## 🟠 Node/Express + React Integration

```typescript
import express from "express";

// A service class: dependencies come in through the constructor
interface OrderRow { id: string; amountPaise: number } // DB row
class OrderRepository {
  private rows = new Map<string, OrderRow>([["o1", { id: "o1", amountPaise: 49900 }]]); // fake store
  findById(id: string): OrderRow | undefined { return this.rows.get(id); } // SQL Server SELECT in real life
}

class OrderService {
  constructor(private readonly repo: OrderRepository) {} // parameter property: declares + assigns
  getTotalRupees(id: string): number | null {
    const row = this.repo.findById(id); // may be undefined
    return row ? row.amountPaise / 100 : null; // convert paise -> rupees
  }
}

const service = new OrderService(new OrderRepository()); // wire dependencies (manual DI)
const app = express(); // create app
app.get("/orders/:id/total", (req, res) => {
  const total = service.getTotalRupees(String(req.params.id)); // typed number | null
  if (total === null) { res.status(404).json({ error: "not found" }); return; } // handle missing
  res.json({ total }); // respond
});
```

```tsx
import { Component, type ReactNode } from "react";

// Class components are typed with generics for props and state (still seen in legacy code, error boundaries)
interface Props { children: ReactNode } // props type
interface State { hasError: boolean } // state type

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }; // typed initial state

  static getDerivedStateFromError(): State { return { hasError: true }; } // static method on the class

  render(): ReactNode {
    return this.state.hasError ? <p>Something went wrong</p> : this.props.children; // props typed via Props
  }
}
```

```typescript
// Redux: keep state plain objects, but classes are fine for non-serialisable helpers (not in the store)
class PriceFormatter {
  constructor(private readonly locale = "en-IN") {} // default param + parameter property
  format(paise: number): string {
    return new Intl.NumberFormat(this.locale, { style: "currency", currency: "INR" }).format(paise / 100); // ₹ format
  }
}
console.log(new PriceFormatter().format(49900)); // ₹499.00
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `!` to silence "not initialized" instead of initialising
```typescript
class Bad {
  token!: string; // "trust me" - nothing assigns it
  size(): number { return this.token.length; } // runtime crash if init() not called
}
new Bad().size(); // TypeError at runtime: Cannot read properties of undefined (reading 'length')

class Good {
  token: string | null = null; // honest type
  size(): number { return this.token?.length ?? 0; } // safe
}
```

❌ Mistake 2: Losing `this` when passing a method as a callback
```typescript
class Counter {
  count = 0;
  inc() { this.count++; } // normal method: `this` depends on how it is called
  incArrow = () => { this.count++; }; // arrow field: `this` is bound to the instance
}
const c = new Counter();
const f = c.inc; // detached method
// f(); // would throw at runtime: Cannot read properties of undefined (reading 'count')
const g = c.incArrow; // safe to pass to onClick={g}, setTimeout(g), emitter.on("x", g)
g(); // works
console.log(c.count); // 1
```

❌ Mistake 3: Expecting `private`/TS-only checks at runtime (see topic 62)
✅ Correct: TS `private` is erased at runtime; use `#field` for true runtime privacy.

❌ Mistake 4: Forgetting `super()` before touching `this` in a subclass
```typescript
class Base { constructor(public id: string) {} }
class Child extends Base {
  constructor(id: string, public extra: number) {
    this.extra = extra; // ❌ too early!
    super(id);
  }
}
// error TS17009: 'super' must be called before accessing 'this' in the constructor of a derived class.
```

---

## 🧠 Tricky Interview Question

```typescript
class A {
  x = 1;
  getX() { return this.x; }
}
class B extends A {
  x = 2;
}
console.log(new B().getX()); // ?
```
**Answer:** `2`. The field initialiser in the subclass runs **after** `super()` returns and overwrites `x`; `getX` reads `this.x` dynamically. A related trap: with `useDefineForClassFields: true` (default when target >= ES2022) a subclass that merely **redeclares** a field (`x!: number;`) would **redefine it as `undefined`**, wiping the value set by the base class, so the compiler rejects it: `error TS2612: Property 'x' will overwrite the base property in 'A'. If this is intentional, add an initializer. Otherwise, add a 'declare' modifier or remove the redundant declaration.` Use `declare x: number;` in the subclass to only refine the type without emitting a field.
```typescript
class P { name = "p"; }
class Q extends P { declare name: "p"; } // type narrowing only, no re-initialisation
console.log(new Q().name); // p
```

---

## ⚫ Interview Questions + Answers

Q1: What does `strictPropertyInitialization` do?
A1: With `strict` (or `strictNullChecks` + this flag), every non-optional field must be assigned in the declaration or constructor, or typed to include `undefined`. It prevents "undefined field" crashes. Escape hatches: `field!: T` (definite assignment assertion) for DI frameworks or lifecycle hooks, but prefer honest types like `T | null`.

Q2: Is a TypeScript class nominally or structurally typed?
A2: Structurally for public members: `const p: Point = { x: 1, y: 2 }` compiles. But a class with `private` or `protected` members becomes **nominal-like**: only instances of that class (or subclasses) are assignable, because the private member's declaration origin is part of compatibility.

Q3: What is `override` and why use `noImplicitOverride`?
A3: `override` (TS 4.3+) marks a method as overriding a base-class method; the compiler errors if the base has no such method (typo or the base was renamed). `noImplicitOverride` forces you to write it, so renaming a base method breaks subclasses at compile time rather than silently becoming new methods.

Q4: Difference between a method and an arrow-function property?
A4: A method lives on the prototype (one copy, `this` depends on the call site, `super.method()` works). An arrow property is created per instance (more memory, `this` bound lexically, no `super` call). Use arrow properties for callbacks passed to React/emitters; use methods otherwise and bind explicitly when needed.

Q5: What does a class name represent - type, value or both?
A5: Both. As a **value** it is the constructor function (with statics). As a **type** it is the instance shape. To type the constructor itself use `typeof Cart` (e.g. `new () => Cart` for factories).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have stateful objects with behaviour and invariants (`Cart`, `Wallet`, `PaymentService`)
- Dependency injection (NestJS, manual constructor injection) and lifecycle (`onModuleInit`)
- Error hierarchies (`class NotFoundError extends HttpError`)

❌ Avoid when:
- You just need data: use an `interface`/`type` + plain object (serialisable, works in Redux)
- A few functions would do; modules + closures are lighter
- You need immutability and structural equality: prefer plain objects with `readonly`

---

## 📊 Visual Diagram
```
class Cart {                          Two things are created:
  items: CartItem[] = []     ───┐
  readonly userId: string       │      VALUE  (runtime)         TYPE (compile-time)
  constructor(userId) {...}     ├──►   Cart  (constructor fn)   Cart (instance shape)
  addItem(...): this            │      Cart.prototype.addItem   { items; userId; addItem; total }
  get total(): number        ───┘      static members live on    static members are NOT part
}                                      the constructor            of the instance type

new Cart("u1")  ──►  instance { items: [], userId: "u1" } ──► proto: addItem, total
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Field / property | Data member of a class | class का data member |
| Constructor | Setup function run on `new` | `new` पर चलने वाला setup function |
| Getter / setter | Property-like accessor methods | property जैसे accessor methods |
| strictPropertyInitialization | Fields must be definitely assigned | fields का पक्का assign होना |
| override | Marks overriding a base method | base method को override करना |
| Definite assignment `!` | "Trust me, it is set" assertion | "यह set है" वाला assertion |

---

## ⚡ 3-Line Summary
English:
1. A TS class gives typed fields, constructor and methods, and is both a runtime value and a compile-time type.
2. `strict` forces fields to be assigned; `override`/`noImplicitOverride` keeps inheritance safe.
3. Use classes for stateful services and error hierarchies; use plain typed objects for Redux state and DTOs.

Hindi:
1. TS class typed fields, constructor और methods देती है, और runtime value व compile-time type दोनों है।
2. `strict` fields को assign करवाता है; `override`/`noImplicitOverride` inheritance को सुरक्षित रखता है।
3. Stateful services और error hierarchies के लिए classes, Redux state और DTOs के लिए plain typed objects।

---

## ➡️ Next Topic
**62. Access Modifiers (public, private, protected, #private)** — controlling who can touch your class members.
