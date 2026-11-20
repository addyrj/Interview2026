# 63. readonly and static Members
# हिंदी में: readonly और static Members

> TypeScript 5.x (`tsc --strict`, TS 5.9) पर verify किया गया। `readonly` TS 2.0 से; `static` blocks (`static { ... }`) TS 4.4+; `override` static members पर TS 4.3+; `accessor` और `const` type parameters TS 5.0+।

---

## 🔵 Simple Definition (English)
- **`readonly`** marks a property that can be assigned **only at declaration or inside the constructor**; afterwards the compiler rejects writes. It is compile-time only and **shallow** (a `readonly items: string[]` still allows `items.push`).
- **`static`** members belong to the **class itself**, not to instances: accessed as `ClassName.member`, shared by everyone, and not available on `this`/instances. Typical uses: counters, constants, factories (`Order.from(...)`), registries and caches.

## 🔵 सरल परिभाषा (Hindi)
- **`readonly`** ऐसी property को mark करता है जो **सिर्फ declaration पर या constructor के अंदर** assign हो सकती है; बाद में compiler writes reject करता है। यह सिर्फ compile-time है और **shallow** है (`readonly items: string[]` में `items.push` अब भी चलता है)।
- **`static`** members **class के अपने** होते हैं, instances के नहीं: `ClassName.member` से access होते हैं, सब में shared रहते हैं, और `this`/instance पर नहीं मिलते। आम उपयोग: counters, constants, factories (`Order.from(...)`), registries और caches।

---

## 🔴 Problem it Solves
Order ids, creation times and currency should **never change** after an order is created - but without `readonly`, any bug can do `order.id = "x"` and corrupt data. Likewise shared helpers (id generator, tax rate, "create from DB row" factory) do not need an instance; without `static` you would create throw-away objects or loose global variables. `readonly` documents and enforces immutability; `static` groups class-level behaviour next to the class instead of in scattered globals.

## 🔴 यह क्यों बना? (Hindi)
Order id, creation time और currency order बनने के बाद **कभी नहीं बदलने** चाहिए - पर `readonly` के बिना कोई भी bug `order.id = "x"` करके data corrupt कर सकता है। इसी तरह shared helpers (id generator, tax rate, "DB row से बनाओ" factory) को instance नहीं चाहिए; `static` के बिना throw-away objects या बिखरे global variables बनाने पड़ते। `readonly` immutability को document और enforce करता है; `static` class-level behaviour को class के पास रखता है, scattered globals में नहीं।

---

## 🟢 How it Works — Step by Step

Step 1 → `readonly id: string` - assignable in the declaration or the constructor (also in a subclass-free context only; subclasses cannot assign the base's readonly field).
Step 2 → Writing `obj.id = ...` anywhere else is **TS2540**. It is erased at runtime, so JS code or `as any` can still mutate.
Step 3 → Readonly is **shallow**: `readonly cfg: { retries: number }` still lets you do `cfg.retries++`. Use `Readonly<T>`, `ReadonlyArray<T>`, `as const` or `Object.freeze` for depth.
Step 4 → **Parameter property** shortcut: `constructor(public readonly id: string)` declares and assigns.
Step 5 → `static x = 0;` lives on the constructor function: `Order.x`. Instances do **not** have it, and `this.x` inside an instance method is an error (use `Order.x`).
Step 6 → Inside **static methods**, `this` is the class itself, so `static create() { return new this() }` supports subclass factories.
Step 7 → `static readonly TAX = 0.18` makes a true class constant; combine with `as const` literals for narrow types.
Step 8 → **Static blocks** `static { ... }` (TS 4.4+) run once when the class is defined, to initialise complex statics.
Step 9 → Static members are **inherited** by subclasses (`Child.helper()` works), and can be `private`/`protected`/`#`.
Step 10 → Generic class parameters **cannot** be used in static members (`static x: T` is TS2302) because statics are shared across all `T`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `readonly id: string` - declaration या constructor में assign होता है (subclass base का readonly field assign नहीं कर सकती)।
Step 2 → कहीं और `obj.id = ...` लिखना **TS2540** है। Runtime पर यह erase हो जाता है, इसलिए JS code या `as any` अब भी बदल सकता है।
Step 3 → Readonly **shallow** है: `readonly cfg: { retries: number }` में भी `cfg.retries++` चल जाता है। गहराई के लिए `Readonly<T>`, `ReadonlyArray<T>`, `as const` या `Object.freeze`।
Step 4 → **Parameter property** shortcut: `constructor(public readonly id: string)` declare और assign दोनों करता है।
Step 5 → `static x = 0;` constructor function पर रहता है: `Order.x`। Instances में यह **नहीं** होता, और instance method में `this.x` error है (`Order.x` लिखो)।
Step 6 → **Static methods** में `this` खुद class है, इसलिए `static create() { return new this() }` subclass factories को support करता है।
Step 7 → `static readonly TAX = 0.18` असली class constant बनाता है; narrow types के लिए `as const` literals के साथ मिलाओ।
Step 8 → **Static blocks** `static { ... }` (TS 4.4+) class define होते समय एक बार चलते हैं, complex statics initialise करने के लिए।
Step 9 → Static members subclasses में **inherit** होते हैं (`Child.helper()` चलता है), और `private`/`protected`/`#` हो सकते हैं।
Step 10 → Generic class parameters static members में **इस्तेमाल नहीं** हो सकते (`static x: T` TS2302) क्योंकि statics सभी `T` में shared हैं।

---

## 🟡 Real World Example
A **Zomato** `Order` has `readonly id`, `readonly createdAt` and `readonly restaurantId` (never change), while `status` is mutable. A `static fromRow(row)` converts a SQL Server row to an `Order`, and `static readonly GST_RATE = 0.05` stores the tax constant. A **Razorpay** `Money` value object has all fields `readonly`, so adding two `Money` values returns a **new** object instead of mutating - safe to share across Redux and React.

## 🟡 Real Example Hindi mein
**Zomato** के `Order` में `readonly id`, `readonly createdAt` और `readonly restaurantId` हैं (कभी नहीं बदलते), जबकि `status` mutable है। `static fromRow(row)` SQL Server row को `Order` में बदलता है, और `static readonly GST_RATE = 0.05` tax constant रखता है। **Razorpay** के `Money` value object के सारे fields `readonly` हैं, इसलिए दो `Money` जोड़ने पर mutate की जगह **नया** object मिलता है - Redux और React में बेफिक्र share करो।

---

## 💻 Code Example — Basic

```typescript
class Order {
  static readonly GST_RATE = 0.05; // class constant: shared, never reassigned
  private static nextId = 1; // class-level counter (shared across instances)

  readonly id: string; // set once
  readonly createdAt: Date; // set once
  status: "PLACED" | "PAID" | "DELIVERED" = "PLACED"; // mutable on purpose

  constructor(public readonly amount: number) { // parameter property: public + readonly
    this.id = `ord_${Order.nextId++}`; // readonly may be assigned in the constructor
    this.createdAt = new Date(0); // fixed date keeps the demo output stable
  }

  // static method: needs no instance
  static fromRow(row: { amount: number }): Order {
    return new Order(row.amount); // factory that builds an Order from a DB row
  }

  get totalWithTax(): number {
    return this.amount * (1 + Order.GST_RATE); // statics are read through the class name
  }
}

const o1 = new Order(1000); // ord_1
const o2 = Order.fromRow({ amount: 500 }); // ord_2 via factory
o1.status = "PAID"; // allowed: status is not readonly
console.log(o1.id, o2.id, o1.totalWithTax, o1.status); // ord_1 ord_2 1050 PAID

// ❌ Writing to a readonly property
o1.id = "hacked";
// error TS2540: Cannot assign to 'id' because it is a read-only property.

// ❌ Reading a static through the instance
console.log(o1.GST_RATE);
// error TS2576: Property 'GST_RATE' does not exist on type 'Order'. Did you mean to access the static member 'Order.GST_RATE' instead?

// ❌ Assigning a static readonly
Order.GST_RATE = 0.18;
// error TS2540: Cannot assign to 'GST_RATE' because it is a read-only property.
```

## 💻 Code Example — Advanced

```typescript
// 1) readonly is SHALLOW: the reference is fixed, the contents are not
class Cart {
  readonly items: string[] = []; // readonly array reference
  readonly config = { maxItems: 5 }; // readonly object reference
}
const cart = new Cart(); // instance
cart.items.push("BIRYANI"); // allowed! push mutates the array, not the property
cart.config.maxItems = 10; // allowed! nested property is not readonly
console.log(cart.items.length, cart.config.maxItems); // 1 10

// ❌ Reassigning the property itself is blocked
cart.items = [];
// error TS2540: Cannot assign to 'items' because it is a read-only property.

// Deep immutability: ReadonlyArray + Readonly<T>
class SafeCart {
  readonly items: ReadonlyArray<string> = ["A"]; // no push/pop/splice on this type
  readonly config: Readonly<{ maxItems: number }> = { maxItems: 5 }; // nested props readonly too
}
const safe = new SafeCart(); // instance
// ❌ Mutating through the readonly array type
safe.items.push("B");
// error TS2339: Property 'push' does not exist on type 'readonly string[]'.

// 2) Immutable value object: methods return NEW instances
class Money {
  private constructor(readonly paise: number, readonly currency: "INR") {} // private: use factories
  static of(paise: number): Money { return new Money(paise, "INR"); } // factory
  static readonly ZERO = Money.of(0); // static initialised by another static
  add(other: Money): Money { return new Money(this.paise + other.paise, this.currency); } // returns new
}
const total = Money.of(49900).add(Money.of(10000)).add(Money.ZERO); // chain of new objects
console.log(total.paise); // 59900

// 3) Static blocks (TS 4.4+): run once at class definition
class Registry {
  static readonly handlers = new Map<string, () => string>(); // shared registry
  static {
    Registry.handlers.set("upi", () => "pay via UPI"); // pre-register defaults
    Registry.handlers.set("card", () => "pay via card"); // pre-register defaults
  }
  static run(name: string): string { return Registry.handlers.get(name)?.() ?? "unknown"; } // lookup
}
console.log(Registry.run("upi"), Registry.run("cod")); // pay via UPI unknown

// 4) `this` in static methods: polymorphic factories
class Gateway {
  static create<T extends typeof Gateway>(this: T): InstanceType<T> { return new this() as InstanceType<T>; } // new this()
  name(): string { return "base"; } // instance method
}
class Razorpay extends Gateway { override name(): string { return "razorpay"; } } // subclass
console.log(Razorpay.create().name()); // razorpay   (static is inherited and `this` = Razorpay)

// ❌ Class type parameters cannot be used in static members
class Box<T> {
  static empty: T; // statics are shared across all T
}
// error TS2302: Static members cannot reference class type parameters.

// 5) Static counter + readonly instance field: unique ids
class Ticket {
  private static counter = 0; // shared counter
  readonly no = ++Ticket.counter; // initialiser runs per instance
}
console.log(new Ticket().no, new Ticket().no); // 1 2
```

---

## 🟠 Node/Express + React Integration

```typescript
import express from "express";

// Immutable config singleton loaded once
class AppConfig {
  static readonly instance = new AppConfig(); // single shared instance
  readonly port: number = Number(process.env.PORT ?? 3000); // readonly settings
  readonly dbUrl: string = process.env.DB_URL ?? "mssql://localhost/orders"; // SQL Server connection string
  private constructor() {} // nobody else can create another
}

// Static helper that maps a SQL Server row into a domain object
interface OrderRow { Id: number; AmountPaise: number } // SQL Server columns (PascalCase)
class OrderDto {
  private constructor(readonly id: string, readonly amount: number) {} // immutable DTO
  static fromRow(r: OrderRow): OrderDto { return new OrderDto(`ord_${r.Id}`, r.AmountPaise / 100); } // mapper
}

const app = express(); // create app
app.get("/orders/:id", (req, res) => {
  const row: OrderRow = { Id: Number(req.params.id), AmountPaise: 49900 }; // pretend DB result
  res.json(OrderDto.fromRow(row)); // JSON.stringify keeps readonly props
});
console.log(AppConfig.instance.port); // 3000
```

```tsx
import { memo, type ReactElement } from "react";

// readonly props: React props are immutable by contract, make it explicit
interface PriceProps { readonly amountPaise: number; readonly items: ReadonlyArray<string> } // readonly everywhere

export const Price = memo(function Price({ amountPaise, items }: PriceProps): ReactElement {
  // items.push("x");  // would be a compile error, matching React's "do not mutate props" rule
  return <p>{items.length} items - ₹{amountPaise / 100}</p>; // pure render
});
```

```typescript
// Redux Toolkit: Readonly state types catch accidental mutation outside reducers
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
interface CartState { readonly items: ReadonlyArray<{ sku: string; qty: number }> } // consumers cannot mutate
const slice = createSlice({
  name: "cart",
  initialState: { items: [] } as CartState, // typed initial state
  reducers: {
    add: (state, a: PayloadAction<{ sku: string; qty: number }>) => ({ items: [...state.items, a.payload] }), // return a new object (immer allows both styles)
  },
});
console.log(slice.reducer(undefined, slice.actions.add({ sku: "B1", qty: 1 })).items.length); // 1
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assuming `readonly` makes the object deeply immutable
```typescript
class Settings { readonly retry = { max: 3 }; }
const s = new Settings();
s.retry.max = 99; // compiles! readonly is shallow
// Right: Readonly<{ max: number }> for the type, or Object.freeze + as const for the value
class Settings2 { readonly retry: Readonly<{ max: number }> = { max: 3 }; }
const s2 = new Settings2();
s2.retry.max = 99; // ❌
// error TS2540: Cannot assign to 'max' because it is a read-only property.
```

❌ Mistake 2: Using `this.static` inside instance methods
```typescript
class Counter {
  static total = 0; // class-level
  inc(): void { this.total++; } // ❌ wrong: total is not on the instance
}
// error TS2576: Property 'total' does not exist on type 'Counter'. Did you mean to access the static member 'Counter.total' instead?
// Right: Counter.total++;
```

❌ Mistake 3: Mutable static state shared in tests/requests
✅ Correct: A `static cache = new Map()` is **process-wide**; in a Node server it is shared across all requests (a memory leak or data leak between users). Keep per-request data in instances or request context; keep statics for constants and pure helpers. In tests reset statics between cases.

❌ Mistake 4: Expecting `readonly` to survive JSON/any
✅ Correct: `readonly` is erased. `(obj as any).id = "x"` or a JS caller still mutates. Use `Object.freeze` (runtime) or `#private` + getter for real immutability.

---

## 🧠 Tricky Interview Question

```typescript
class A {
  static x = 1;
  y = A.x + 1;
}
class B extends A {
  static x = 10;
}
console.log(new B().y, B.x, A.x);
```
**Answer:** `2 10 1`. The instance field `y` is initialised inside `A`'s constructor with `A.x` (hard-coded class name), so `B.x = 10` does not affect it: `y = 2`. `B.x` is `B`'s own static (10) that **shadows** the inherited one; `A.x` stays 1. If `y` were `this.constructor.x`-style it would differ, but that needs a cast. Statics are inherited through the constructor prototype chain (`B.__proto__ === A`), yet `static x = 10` creates a **new own property** on `B`.
```typescript
class A3 { static x = 1; }
class B3 extends A3 { static x = "ten"; } // ❌ static side must stay compatible
// error TS2417: Class static side 'typeof B3' incorrectly extends base class static side 'typeof A3'.
//   Types of property 'x' are incompatible.
//     Type 'string' is not assignable to type 'number'.
```

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `readonly` and `const`?
A1: `const` applies to **variables** (cannot rebind the identifier). `readonly` applies to **properties** (cannot reassign the property after construction). Both are shallow and compile-time-wise `readonly` is erased. Use `const` for locals, `readonly` for class/interface fields; `as const` makes a whole literal deeply readonly.

Q2: Can a `readonly` property be set after the constructor?
A2: No, only in the declaration or the constructor of the same class. Methods get `TS2540`. A subclass cannot assign it either. If you need a late-initialised-once value, use a private field with a getter, or `Object.defineProperty`-style tricks (not type safe).

Q3: Where do static members live, and how do you access them?
A3: On the class constructor function object; access via `ClassName.member` (or `this` inside static methods). Instances do not see them (`instance.member` is an error). They are inherited by subclasses via the constructor prototype chain, and can be overridden by redeclaring.

Q4: Why can't a generic class use its type parameter in a static member?
A4: Statics exist once per class, not once per instantiation (`Box<string>` and `Box<number>` share the same `Box.empty`), so a `T` would have no single meaning. TS reports TS2302. Declare the generic on the static method itself: `static of<U>(v: U): Box<U>`.

Q5: When would you use a static factory instead of `new`?
A5: When construction needs a name (`Order.fromRow`, `Money.fromRupees`), validation that returns an error/`null`, caching/singletons, or multiple constructors with different inputs (JS has only one `constructor`). Combine with a `private constructor` to force use of the factories.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- `readonly` for ids, timestamps, injected dependencies (`constructor(private readonly repo: Repo)`), value objects
- `static readonly` for constants (tax rates, limits, event names)
- `static` factories/mappers (`fromRow`, `fromJSON`) and registries initialised once

❌ Avoid when:
- You need deep immutability - add `Readonly<T>`, `ReadonlyArray`, `Object.freeze`
- Mutable `static` state would be shared between requests or tests (hidden global)
- A plain module function or `as const` object would do (no need for a class just for constants)

---

## 📊 Visual Diagram
```
                 ┌──────────────── class Order (constructor function) ───────────────┐
                 │  static GST_RATE = 0.05        static fromRow()      static nextId  │ ◄── STATIC SIDE
                 └───────────────────────────────────────────────────────────────────┘     Order.GST_RATE
                                          │ new Order(...)
                                          ▼
                 ┌──────────────── instance ─────────────────┐
                 │ readonly id         "ord_1"   ✅ set in ctor │ ◄── INSTANCE SIDE
                 │ readonly createdAt  Date      ✅ set in ctor │     o1.id = "x"  ❌ TS2540
                 │ status              "PLACED"  ✏️ mutable     │     o1.GST_RATE  ❌ TS2576
                 └───────────────────────────────────────────┘

 readonly is SHALLOW:  readonly items: string[]  -> items.push() still OK
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| readonly | Assign only at declaration/constructor | सिर्फ declaration/constructor में assign |
| static | Member of the class, not instances | class का member, instance का नहीं |
| Shallow immutability | Reference fixed, contents mutable | reference fixed, contents mutable |
| Static factory | Static method that builds instances | instances बनाने वाला static method |
| Static block | `static { }` initialisation code | class define पर चलने वाला init code |
| Value object | Immutable object compared by value | value से compare होने वाला immutable object |

---

## ⚡ 3-Line Summary
English:
1. `readonly` fixes a property after construction (shallow, compile-time only); `static` puts a member on the class itself.
2. Use `readonly` for ids, timestamps and dependencies, and `static readonly`/factories for constants and mappers.
3. For real immutability add `Readonly<T>`/`ReadonlyArray`/`Object.freeze`, and avoid mutable statics in servers.

Hindi:
1. `readonly` construction के बाद property को fix करता है (shallow, सिर्फ compile-time); `static` member को class पर रखता है।
2. Ids, timestamps और dependencies के लिए `readonly`, constants और mappers के लिए `static readonly`/factories।
3. असली immutability के लिए `Readonly<T>`/`ReadonlyArray`/`Object.freeze` जोड़ो, और servers में mutable statics से बचो।

---

## ➡️ Next Topic
**64. Abstract Classes** — partially implemented base classes that subclasses must complete.
