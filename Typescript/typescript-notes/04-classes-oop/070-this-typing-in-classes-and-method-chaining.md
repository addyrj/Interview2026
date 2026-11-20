# 70. this Typing in Classes + Method Chaining
# हिंदी में: Classes में `this` की typing और Method Chaining

> Verified with TypeScript 5.9 (`tsc --strict`). `this` types and `this is T` guards: TS 1.7 / 2.0. `strictBindCallApply` + `noImplicitThis` are part of `strict`.

---

## 🔵 Simple Definition (English)
Inside a class, TypeScript has a special **polymorphic `this` type**: a method declared as `setX(): this` returns "the type of whatever object it was called on", including **subclasses**. That is what makes **method chaining** (`qb.select().from().where()`) stay correctly typed across inheritance. Related tools: the `this` parameter (fake first parameter that types `this`), `this is T` type guards, and the classic JavaScript trap of **losing `this`** when a method is passed as a callback.

## 🔵 सरल परिभाषा (Hindi)
Class के अंदर TypeScript में एक special **polymorphic `this` type** होता है: `setX(): this` जैसा method "जिस object पर call हुआ उसी का type" return करता है, **subclasses समेत**। इसी से **method chaining** (`qb.select().from().where()`) inheritance में भी सही typed रहती है। संबंधित tools: `this` parameter (नकली पहला parameter जो `this` को type करता है), `this is T` type guards, और JavaScript का पुराना जाल - method को callback में देने पर **`this` खो जाना**।

---

## 🔴 Problem it Solves
Two real problems. (1) **Fluent builders with inheritance**: if `setName()` in a base class is typed to return `Base`, then after calling it you lose the subclass methods (`.setEmail()` is gone). (2) **Lost `this`**: `button.onClick = this.handleClick` - when React/Express calls it later, `this` is `undefined` and the code crashes at runtime. TypeScript can catch both when you type `this` properly.

## 🔴 यह क्यों बना? (Hindi)
दो असली समस्याएँ। (1) **Inheritance के साथ fluent builders**: अगर base class का `setName()` return type `Base` है, तो call के बाद subclass के methods (`.setEmail()`) गायब हो जाते हैं। (2) **`this` खो जाना**: `button.onClick = this.handleClick` - बाद में React/Express इसे call करता है तो `this` `undefined` होता है और runtime पर crash। `this` को सही type करने से TypeScript दोनों पकड़ लेता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Declare a chainable method with return type `this`: `where(c: string): this { ...; return this; }`.
Step 2 → In a subclass instance, `this` means the **subclass**, so the chain keeps all subclass methods.
Step 3 → For standalone functions, add a fake first parameter `this: Type` - erased in JS, checked by TS (`noImplicitThis`).
Step 4 → For type guards in classes use `isAdmin(): this is AdminUser` to narrow `this`.
Step 5 → To stop losing `this` in callbacks use an **arrow-function property** (`handle = () => {...}`) or `.bind(this)`.
Step 6 → With `strictBindCallApply`, `bind/call/apply` are checked against the function's `this` and parameter types.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Chainable method का return type `this` रखो: `where(c: string): this { ...; return this; }`।
Step 2 → Subclass के instance में `this` का मतलब **subclass** होता है, इसलिए chain में subclass के सारे methods बने रहते हैं।
Step 3 → अलग function के लिए नकली पहला parameter `this: Type` जोड़ो - JS में हट जाता है, TS check करता है (`noImplicitThis`)।
Step 4 → Class में type guard के लिए `isAdmin(): this is AdminUser` लिखो ताकि `this` narrow हो।
Step 5 → Callback में `this` न खोने के लिए **arrow-function property** (`handle = () => {...}`) या `.bind(this)` इस्तेमाल करो।
Step 6 → `strictBindCallApply` के साथ `bind/call/apply` function के `this` और parameter types के against check होते हैं।

---

## 🟡 Real World Example
**Zomato search query builder**: `new RestaurantQuery().city("Pune").veg().maxCost(400).sortBy("rating")`. A `PaidQuery` subclass adds `.onlyOpenNow()`. Because every method returns `this`, `new PaidQuery().city("Pune").onlyOpenNow()` compiles - after `.city(...)` we still hold a `PaidQuery`. The same pattern powers Knex, TypeORM `QueryBuilder`, and Zod's `z.string().min(3).max(10)`.

## 🟡 Real Example Hindi mein
**Zomato search query builder**: `new RestaurantQuery().city("Pune").veg().maxCost(400).sortBy("rating")`। `PaidQuery` subclass में `.onlyOpenNow()` जुड़ता है। हर method `this` return करता है, इसलिए `new PaidQuery().city("Pune").onlyOpenNow()` compile होता है - `.city(...)` के बाद भी हमारे पास `PaidQuery` ही है। यही pattern Knex, TypeORM `QueryBuilder` और Zod (`z.string().min(3).max(10)`) में है।

---

## 💻 Code Example — Basic

```typescript
// Fluent builder: every setter returns `this`
class RestaurantQuery {
  protected filters: string[] = []; // collected conditions
  protected orderBy = "rating"; // default ordering

  city(name: string): this { // `this` = the exact subclass at the call site
    this.filters.push(`city = '${name}'`); // add a filter
    return this; // return same object -> chaining
  }

  veg(): this {
    this.filters.push("isVeg = 1"); // another filter
    return this;
  }

  sortBy(col: string): this {
    this.orderBy = col; // change ordering
    return this;
  }

  build(): string {
    const where = this.filters.length ? ` WHERE ${this.filters.join(" AND ")}` : "";
    return `SELECT * FROM Restaurants${where} ORDER BY ${this.orderBy} DESC`; // final SQL Server text
  }
}

// Subclass adds its own chainable method
class PaidQuery extends RestaurantQuery {
  onlyOpenNow(): this {
    this.filters.push("isOpen = 1"); // extra filter
    return this;
  }
}

// `city` returns `this` (= PaidQuery), so onlyOpenNow is still available
const sql = new PaidQuery().city("Pune").veg().onlyOpenNow().sortBy("cost").build();
console.log(sql);
// SELECT * FROM Restaurants WHERE city = 'Pune' AND isVeg = 1 AND isOpen = 1 ORDER BY cost DESC
```

## 💻 Code Example — Advanced

```typescript
// 1) `this` parameter: types `this` for a standalone function
interface Wallet {
  owner: string;
  balance: number;
}

function describe(this: Wallet, currency: string): string {
  return `${this.owner} has ${this.balance} ${currency}`; // `this` is typed as Wallet
}

const w: Wallet = { owner: "Asha", balance: 900 };
console.log(describe.call(w, "INR")); // Asha has 900 INR  (call is type-checked)

// 2) `this is T` type guard inside a class hierarchy
class Account {
  constructor(public id: string) {}

  isBusiness(): this is BusinessAccount { // narrows `this`
    return this instanceof BusinessAccount;
  }
}

class BusinessAccount extends Account {
  gstin = "27ABCDE1234F1Z5"; // only business accounts have a GSTIN
}

function invoiceTo(a: Account): string {
  return a.isBusiness() ? `GST invoice for ${a.gstin}` : "Plain receipt"; // a narrowed here
}
console.log(invoiceTo(new BusinessAccount("b1"))); // GST invoice for 27ABCDE1234F1Z5
console.log(invoiceTo(new Account("p1"))); // Plain receipt

// 3) Losing `this`, and the two fixes
class Counter {
  count = 0;

  incMethod() { // normal method: `this` depends on how it is called
    this.count++;
    return this.count;
  }

  incArrow = () => { // arrow property: `this` is fixed to the instance
    this.count++;
    return this.count;
  };
}

const c = new Counter();
const arrow = c.incArrow; // detach it
console.log(arrow()); // 1  (works)

const bound = c.incMethod.bind(c); // bind fixes `this` (type-checked)
console.log(bound()); // 2

// 4) Typed fluent builder with a generic "step" - builder returns new types
class OrderBuilder<T extends object = {}> {
  private constructor(private readonly data: T) {} // build via static factory

  static create(): OrderBuilder {
    return new OrderBuilder({});
  }

  with<K extends string, V>(key: K, value: V): OrderBuilder<T & Record<K, V>> {
    return new OrderBuilder({ ...this.data, [key]: value } as T & Record<K, V>); // grows the type
  }

  build(): T {
    return this.data; // final accumulated type
  }
}

const order = OrderBuilder.create().with("id", 1).with("total", 499).build();
console.log(order.id, order.total); // 1 499  (both known to the compiler)
```

---

## 🟠 Node/Express + React Integration

```typescript
import express, { Request, Response } from "express"; // Express

class OrderController {
  private served = 0; // how many requests handled

  // PROBLEM: normal method loses `this` when Express calls it
  badHandler(_req: Request, res: Response): void {
    res.json({ served: this.served }); // at runtime `this` would be undefined
  }

  // FIX 1: arrow property keeps `this`
  goodHandler = (_req: Request, res: Response): void => {
    this.served++; // safe: `this` is the controller
    res.json({ served: this.served });
  };
}

const ctrl = new OrderController();
const app = express();
app.get("/bad", ctrl.badHandler.bind(ctrl)); // FIX 2: bind explicitly
app.get("/good", ctrl.goodHandler); // arrow property, nothing else needed
```

```tsx
import React from "react";

// Old-style class components show the same trap
class Cart extends React.Component<{}, { count: number }> {
  state = { count: 0 }; // typed state

  add = (): void => { // arrow property: no manual bind in the constructor
    this.setState((s) => ({ count: s.count + 1 })); // `this` is the component
  };

  render() {
    return <button onClick={this.add}>Items: {this.state.count}</button>; // safe to pass
  }
}
export default Cart;
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Returning the class name instead of `this` in a chainable base method
```typescript
class Base {
  setName(n: string): Base { return this; } // returns Base, not `this`
}
class Child extends Base {
  setEmail(e: string): this { return this; }
}
new Child().setName("a").setEmail("b"); // ❌ error TS2339: Property 'setEmail' does not exist on type 'Base'.
```
✅ Fix: `setName(n: string): this`.

❌ Mistake 2: Calling a function with a `this` parameter on the wrong object
```typescript
interface Wallet { balance: number }
function show(this: Wallet): number { return this.balance; }
show(); // ❌ error TS2684: The 'this' context of type 'void' is not assignable to method's 'this' of type 'Wallet'.
```

❌ Mistake 3: Detaching a method that uses `this`
```typescript
class Greeter {
  name = "Zomato";
  hello() { return `Hi ${this.name}`; }
}
const g = new Greeter();
const f = g.hello; // detached: `this` lost
f(); // TypeScript allows this (no error) but at runtime: TypeError: Cannot read properties of undefined (reading 'name')
```
✅ Fix: arrow property or `g.hello.bind(g)`.

❌ Mistake 4: Using `this` inside a plain function in a method
```typescript
class Timer {
  ticks = 0;
  start() {
    setTimeout(function () {
      this.ticks++; // ❌ error TS2683: 'this' implicitly has type 'any' because it does not have a type annotation.
    }, 100);
  }
}
```
✅ Fix: use an arrow function `() => { this.ticks++; }`.

---

## 🧠 Tricky Interview Question

```typescript
class A {
  who(): this { return this; }
}
class B extends A { b = 1; }
const x = new B().who();
const y = (new B() as A).who();
```
Answer: `x` is `B` (polymorphic `this` resolves to the receiver's type), `y` is `A` (the receiver was widened to `A` by the cast). Follow-up: `this` as a return type is **not** the same as the class name - it also means subclass overrides must return their own `this`. And the polymorphic `this` type cannot be used in `static` members.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between returning `this` and returning the class name?
A1: The class name is fixed (`Base`), so subclass members are lost after the call. `this` is polymorphic: it is the type of the object the method was called on, which keeps chaining correct in subclasses.

Q2: What is the `this` parameter and is it emitted in JavaScript?
A2: A fake first parameter (`function f(this: T, ...)`) that only tells the compiler what `this` must be. It is erased from the output. Calls with the wrong receiver fail with TS2684.

Q3: Why do class methods lose `this` when passed to Express/React?
A3: `this` is decided at call time in JS, not definition time. A detached method is called with `this === undefined` (strict mode). Use arrow properties or `.bind(this)`.

Q4: Arrow property vs method - trade-offs?
A4: Arrow properties are created per instance (more memory, not on the prototype, hard to override with `super.method()` or spy on prototype). Methods are shared on the prototype. Use arrows only for callbacks.

Q5: What is `this is T` ?
A5: A type predicate on `this`: `isBusiness(): this is BusinessAccount`. When it returns true, TS narrows the receiver, like a normal user-defined type guard.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Builders, query builders, fluent configuration APIs, especially with subclasses
- Passing handlers to Express/React (arrow properties or bind)
- Narrowing based on instance state (`this is X`)

❌ Avoid when:
- Immutable chaining is better: return a **new** object instead of mutating `this`
- A plain options object is clearer than a 10-step chain

---

## 📊 Visual Diagram
```
 new PaidQuery().city("Pune").veg().onlyOpenNow().build()
        │            │         │          │
        ▼            ▼         ▼          ▼
   PaidQuery  -> this=PaidQuery -> this=PaidQuery -> this=PaidQuery -> string

 If city() returned `RestaurantQuery` (class name):
   PaidQuery -> RestaurantQuery -> .onlyOpenNow()  X  (lost subclass type)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Polymorphic `this` | Return type meaning "the receiver's type" | "जिस पर call हुआ उसका type" |
| Method chaining | `a.b().c().d()` | एक के बाद एक method call |
| `this` parameter | Fake first param that types `this` | `this` को type करने वाला नकली parameter |
| Type predicate | `x is T` / `this is T` | Narrow करने वाला return type |
| Arrow property | `fn = () => {}` in a class | Class में arrow function वाली property |
| `bind` | Fix `this` of a function | Function का `this` तय करना |

---

## ⚡ 3-Line Summary
English:
1. Return `this` (not the class name) from chainable methods so subclasses keep their own type.
2. Use a `this:` parameter or `this is T` to type or narrow `this`.
3. Detached methods lose `this`: use arrow properties or `.bind(this)` for Express/React callbacks.

Hindi:
1. Chainable methods में class का नाम नहीं, `this` return करो ताकि subclass का type बना रहे।
2. `this` को type या narrow करने के लिए `this:` parameter या `this is T` इस्तेमाल करो।
3. Detach किया गया method `this` खो देता है: Express/React callbacks के लिए arrow property या `.bind(this)` लगाओ।

---

## ➡️ Next Topic
**71. tsconfig Deep Dive - strict Family Flags** - What each flag in `strict` really turns on, and which extra flags (like `noUncheckedIndexedAccess`) you should add.
