# 65. implements vs extends
# हिंदी में: implements बनाम extends

> TypeScript 5.x (`tsc --strict`, TS 5.9) पर verify किया गया। `implements` और `extends` TS के शुरू से हैं; `override` TS 4.3+; `satisfies` TS 4.9+ (alternative के रूप में mention)।

---

## 🔵 Simple Definition (English)
- **`extends`** = **inheritance**. The subclass **gets** the parent's members and implementation (`class B extends A`), a class can extend **only one** class. Interfaces can also `extend` other interfaces (many allowed).
- **`implements`** = **contract check**. The class **promises** to have the shape of one or more interfaces (or even another class used as an interface) but **gets nothing for free**: you must write every member yourself. `implements` is erased at runtime; it only makes the compiler verify the class.

## 🔵 सरल परिभाषा (Hindi)
- **`extends`** = **inheritance**। Subclass को parent के members और implementation **मिल जाते हैं** (`class B extends A`), एक class **सिर्फ एक** class को extend कर सकती है। Interfaces भी दूसरे interfaces को `extend` कर सकते हैं (कई allowed)।
- **`implements`** = **contract check**। Class एक या ज़्यादा interfaces की shape का **वादा** करती है (या किसी और class को interface की तरह) पर **मुफ़्त में कुछ नहीं मिलता**: हर member खुद लिखना पड़ता है। `implements` runtime पर erase हो जाता है; यह सिर्फ compiler से class verify करवाता है।

---

## 🔴 Problem it Solves
Your app has `Logger`, `Cache`, `PaymentGateway`: several implementations each (console/file logger, in-memory/Redis cache, Razorpay/Paytm gateway). Callers should depend on a **contract**, not a concrete class, so you can swap implementations and mock them in tests. `implements` makes the compiler **prove** each implementation matches the contract. Meanwhile `extends` is for **reusing code** (shared base behaviour). Mixing them up leads to deep, fragile inheritance trees, or to classes that "implement" an interface incorrectly and fail at runtime.

## 🔴 यह क्यों बना? (Hindi)
आपके app में `Logger`, `Cache`, `PaymentGateway` हैं, हर एक की कई implementations (console/file logger, in-memory/Redis cache, Razorpay/Paytm gateway)। Callers को concrete class पर नहीं, **contract** पर निर्भर होना चाहिए ताकि implementation बदली और tests में mock की जा सके। `implements` compiler से **साबित** करवाता है कि हर implementation contract से मेल खाती है। वहीं `extends` **code reuse** (shared base behaviour) के लिए है। दोनों को गड़बड़ाने से गहरे, कमज़ोर inheritance trees बनते हैं, या ऐसी classes जो interface को गलत "implement" करके runtime पर fail होती हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `class X implements IFoo` - compiler checks X's **instance side** has every member of `IFoo` with compatible types. Failing = error listing the missing member.
Step 2 → `implements` does **not** add members, change types or provide default implementations. E.g. method parameters in your class are **not** contextually typed from the interface (a classic gotcha).
Step 3 → A class can implement **many** interfaces: `class X implements A, B, C`.
Step 4 → `class X extends Base` copies Base's prototype chain: methods/fields/constructor are inherited and can be `override`n; **only one** base class is allowed.
Step 5 → Combine: `class X extends Base implements A, B` - inherit code from one parent and promise multiple contracts.
Step 6 → A class can `implements` **another class** (treating it as an interface of its public shape) - rarely a good idea, it ignores implementation and private members make it impossible.
Step 7 → `interface I extends A, B` composes interfaces (type-level only); `interface I extends SomeClass` inherits the class's **shape including private members** (then only that class's subclasses can implement it).
Step 8 → `implements` is only about the **instance** side. Static members are checked by `typeof` / `satisfies` patterns instead.
Step 9 → **Prefer composition**: inject a collaborator typed by an interface instead of extending a concrete class.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `class X implements IFoo` - compiler जाँचता है कि X के **instance side** में `IFoo` का हर member compatible types के साथ है। न हो तो error बताता है कौन सा member गायब है।
Step 2 → `implements` कोई member **जोड़ता नहीं**, types नहीं बदलता, default implementation नहीं देता। जैसे आपकी class के method parameters interface से contextually typed **नहीं** होते (classic gotcha)।
Step 3 → एक class **कई** interfaces implement कर सकती है: `class X implements A, B, C`।
Step 4 → `class X extends Base` Base की prototype chain लेती है: methods/fields/constructor inherit होते हैं और `override` हो सकते हैं; **सिर्फ एक** base class allowed।
Step 5 → मिलाकर: `class X extends Base implements A, B` - एक parent से code inherit करो और कई contracts का वादा करो।
Step 6 → Class दूसरी **class को भी implement** कर सकती है (उसकी public shape को interface मानकर) - शायद ही अच्छा idea, implementation नज़रअंदाज़ होती है और private members इसे असंभव बनाते हैं।
Step 7 → `interface I extends A, B` interfaces compose करता है (सिर्फ type-level); `interface I extends SomeClass` class की **private members समेत shape** inherit करता है (तब सिर्फ उसी class की subclasses implement कर सकती हैं)।
Step 8 → `implements` सिर्फ **instance** side के बारे में है। Static members `typeof` / `satisfies` patterns से check होते हैं।
Step 9 → **Composition को प्राथमिकता**: concrete class extend करने की जगह interface-typed collaborator inject करो।

---

## 🟡 Real World Example
**Swiggy's** backend defines `interface Notifier { send(to: string, msg: string): Promise<void> }`. `SmsNotifier`, `PushNotifier` and `FakeNotifier` (for tests) **implement** it; `OrderService` takes a `Notifier` in its constructor and never knows which one. Separately, `BaseRepository` holds shared SQL helpers and `OrderRepository extends BaseRepository implements Repository<Order>` - it **extends** to reuse code and **implements** to guarantee the contract.

## 🟡 Real Example Hindi mein
**Swiggy** का backend `interface Notifier { send(to: string, msg: string): Promise<void> }` define करता है। `SmsNotifier`, `PushNotifier` और `FakeNotifier` (tests के लिए) इसे **implement** करते हैं; `OrderService` constructor में `Notifier` लेती है और उसे कभी पता नहीं चलता कौन सा है। अलग से, `BaseRepository` में shared SQL helpers हैं और `OrderRepository extends BaseRepository implements Repository<Order>` - code reuse के लिए **extends** और contract की गारंटी के लिए **implements**।

---

## 💻 Code Example — Basic

```typescript
// Contract: what a notifier must be able to do
interface Notifier {
  send(to: string, msg: string): string; // returns a delivery id (sync for simplicity)
}

// implements: we write everything ourselves, the compiler only verifies the shape
class SmsNotifier implements Notifier {
  send(to: string, msg: string): string { return `sms:${to}:${msg}`; } // required member
}
class PushNotifier implements Notifier {
  send(to: string, msg: string): string { return `push:${to}:${msg}`; } // another implementation
}

// Consumers depend on the contract, not on a class
function notifyAll(list: Notifier[], to: string): string[] {
  return list.map((n) => n.send(to, "Order placed")); // works with ANY implementation
}
console.log(notifyAll([new SmsNotifier(), new PushNotifier()], "u1")); // [ 'sms:u1:Order placed', 'push:u1:Order placed' ]

// extends: inherit code from ONE parent
class BaseEntity {
  constructor(public readonly id: string) {} // shared field
  describe(): string { return `entity ${this.id}`; } // shared method
}
class Order extends BaseEntity {
  constructor(id: string, public amount: number) { super(id); } // must call super first
}
const o = new Order("o1", 499); // gets describe() for free
console.log(o.describe(), o.amount); // entity o1 499

// ❌ implements without implementing everything
class BrokenNotifier implements Notifier {
  // send() is missing
}
// error TS2420: Class 'BrokenNotifier' incorrectly implements interface 'Notifier'.
//   Property 'send' is missing in type 'BrokenNotifier' but required in type 'Notifier'.

// ❌ extends can only name ONE class
class Combo extends BaseEntity, SmsNotifier {}
// error TS1174: Classes can only extend a single class.
```

## 💻 Code Example — Advanced

```typescript
// 1) extends + implements together; implements checks the final shape
interface Repository<T> {
  findById(id: string): T | undefined; // read
  save(item: T): void; // write
}
abstract class InMemoryBase<T extends { id: string }> {
  protected readonly store = new Map<string, T>(); // shared storage (inherited code)
  size(): number { return this.store.size; } // shared helper
}
interface Product { id: string; name: string } // entity
class ProductRepo extends InMemoryBase<Product> implements Repository<Product> {
  findById(id: string): Product | undefined { return this.store.get(id); } // contract method
  save(p: Product): void { this.store.set(p.id, p); } // contract method
}
const repo = new ProductRepo(); // concrete repository
repo.save({ id: "p1", name: "Biryani" }); // contract call
console.log(repo.findById("p1")?.name, repo.size()); // Biryani 1

// 2) GOTCHA: implements does NOT contextually type parameters
interface Handler { handle(e: { type: string }): void } // interface method parameter type
// ❌ In the class, `e` is NOT inferred from the interface -> implicit any
class OrderHandler implements Handler {
  handle(e) { console.log(e); } // parameter 'e' has no annotation
}
// error TS7006: Parameter 'e' implicitly has an 'any' type.
class OrderHandlerOk implements Handler {
  handle(e: { type: string }): void { console.log(e.type); } // annotate explicitly
}
new OrderHandlerOk().handle({ type: "PLACED" }); // PLACED

// 3) Implementing several interfaces; members must satisfy ALL of them
interface Closable { close(): void } // contract 1
interface Pingable { ping(): boolean } // contract 2
class DbConnection implements Closable, Pingable {
  close(): void { console.log("closed"); } // from Closable
  ping(): boolean { return true; } // from Pingable
}
const conn: Closable & Pingable = new DbConnection(); // assignable to the intersection
conn.close(); // closed

// 4) Interface extends interface (type composition) and class implements the composite
interface HasId { id: string } // base contract
interface Auditable extends HasId { updatedAt: Date } // composes HasId
class Invoice implements Auditable {
  constructor(public id: string, public updatedAt: Date) {} // parameter properties satisfy it
}
console.log(new Invoice("inv1", new Date(0)).id); // inv1

// 5) Implementing a class (shape only) is legal but fragile
class Point { constructor(public x: number, public y: number) {} } // class used as a type
class FakePoint implements Point { x = 0; y = 0; } // allowed: only public shape matters
console.log(new FakePoint().x); // 0
class WithPrivate { private secret = 1; } // a private member exists
// ❌ Cannot implement a class that has private members
class Imposter implements WithPrivate { private secret = 2; }
// error TS2720: Class 'Imposter' incorrectly implements class 'WithPrivate'. Did you mean to extend 'WithPrivate' and inherit its members as a subclass?
//   Types have separate declarations of a private property 'secret'.

// 6) override safety on extends
class Gateway { fee(paise: number): number { return Math.round(paise * 0.02); } } // base logic
class PremiumGateway extends Gateway {
  override fee(paise: number): number { return Math.round(paise * 0.01); } // cheaper override
}
console.log(new Gateway().fee(10000), new PremiumGateway().fee(10000)); // 200 100

// 7) Composition over inheritance: inject the contract
interface Sender { send(to: string, msg: string): string } // small contract (same idea as Notifier above)
class OrderService {
  constructor(private readonly notifier: Sender) {} // depends on the interface, any impl works
  place(userId: string): string { return this.notifier.send(userId, "placed"); } // delegate
}
class FakeNotifier implements Sender { sent: string[] = []; send(to: string, msg: string): string { this.sent.push(`${to}:${msg}`); return "fake"; } } // test double
const fake = new FakeNotifier(); // spy
new OrderService(fake).place("u9"); // run
console.log(fake.sent); // [ 'u9:placed' ]
```

---

## 🟠 Node/Express + React Integration

```typescript
import express from "express";

// Contract for payment providers: Express route depends only on this
interface PaymentProvider {
  readonly name: string; // identifier
  charge(paise: number): Promise<{ id: string; ok: boolean }>; // async charge
}

class RazorpayProvider implements PaymentProvider {
  readonly name = "razorpay"; // contract field
  async charge(paise: number): Promise<{ id: string; ok: boolean }> { return { id: `rzp_${paise}`, ok: true }; } // fake API call
}
class PaytmProvider implements PaymentProvider {
  readonly name = "paytm"; // contract field
  async charge(paise: number): Promise<{ id: string; ok: boolean }> { return { id: `ptm_${paise}`, ok: paise < 100000 }; } // fake rule
}

// Registry keyed by name; the route does not know concrete classes
const providers: Record<string, PaymentProvider> = {
  razorpay: new RazorpayProvider(), // register
  paytm: new PaytmProvider(), // register
};

const app = express(); // create app
app.use(express.json()); // parse JSON
app.post("/pay/:provider", async (req, res) => {
  const provider = providers[String(req.params.provider)]; // PaymentProvider (noUncheckedIndexedAccess would add undefined)
  if (!provider) { res.status(404).json({ error: "unknown provider" }); return; } // guard
  const body = req.body as { paise: number }; // unvalidated body (use zod in real code)
  res.json(await provider.charge(body.paise)); // polymorphic call
});
```

```tsx
import { Component, type ReactNode } from "react";

// Shared contract for tiles; class components can implement it while extending React.Component
interface Trackable { trackName(): string } // analytics contract

export class OrderTile extends Component<{ id: string }> implements Trackable {
  trackName(): string { return `order-tile-${this.props.id}`; } // contract method
  render(): ReactNode { return <div data-track={this.trackName()}>Order {this.props.id}</div>; } // inherited lifecycle from Component
}
```

```typescript
// Redux: a thunk dependency typed by interface = easy to fake in tests (extraArgument)
interface OrdersApi { fetchAll(): Promise<{ id: string }[]> } // contract
class HttpOrdersApi implements OrdersApi { async fetchAll() { return [{ id: "o1" }]; } } // real
class FakeOrdersApi implements OrdersApi { async fetchAll() { return []; } } // test double
async function load(api: OrdersApi): Promise<number> { return (await api.fetchAll()).length; } // depends on contract
void load(new HttpOrdersApi()).then(console.log); // 1
void load(new FakeOrdersApi()).then(console.log); // 0
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Thinking `implements` gives you the interface's members/typing
```typescript
interface Greeter { greet(name: string): string }
// Wrong assumption: `name` will be typed string automatically
class Hello implements Greeter {
  greet(name) { return `hi ${name}`; } // ❌ implicit any
}
// error TS7006: Parameter 'name' implicitly has an 'any' type.
// Right: annotate, or use `satisfies`/typed object literal for plain objects
class Hello2 implements Greeter { greet(name: string): string { return `hi ${name}`; } }
```

❌ Mistake 2: Extending a concrete class just to "reuse a few methods"
```typescript
// Wrong: Order IS-A Logger? No. Inheritance only for "is-a"
class Logger { log(m: string): void { console.log(m); } }
class OrderSvc extends Logger { place(): void { this.log("placed"); } } // tight coupling, leaks log() as public API

// Right: HAS-A (composition) with an interface
interface ILogger { log(m: string): void }
class OrderSvc2 { constructor(private readonly logger: ILogger) {} place(): void { this.logger.log("placed"); } }
```

❌ Mistake 3: Expecting `implements` to exist at runtime
```typescript
interface Printable { print(): void }
class Doc implements Printable { print(): void {} }
const d = new Doc();
console.log(d instanceof Printable); // ❌ not possible: interfaces are erased
// error TS2693: 'Printable' only refers to a type, but is being used as a value here.
```
✅ Correct: use a type guard (`"print" in d`) or an abstract class if you need `instanceof`.

❌ Mistake 4: Forgetting `super()` / `override`
✅ Correct: call `super(...)` before `this`, and use `override` so renamed base methods are caught (topic 61).

---

## 🧠 Tricky Interview Question

```typescript
interface A { x: number }
class B implements A {
  x = 1;
  y = 2;
}
const a: A = new B();
console.log(a.y); // ❌ ?
class C implements A { x: number | string = 1; } // ❌
```
**Answer:** `a.y` is a **compile error** (`error TS2339: Property 'y' does not exist on type 'A'.`) - through the `A` type you only see `x`, even though `y` exists at runtime (it would print `2`). And `class C` is also an **error**: `implements` requires the class property type to be **assignable to** the interface's, and `number | string` is wider than `number`:
```typescript
interface A2 { x: number }
class C2 implements A2 { x: number | string = 1; } // ❌
// error TS2416: Property 'x' in type 'C2' is not assignable to the same property in base type 'A2'.
//   Type 'string | number' is not assignable to type 'number'.
//     Type 'string' is not assignable to type 'number'.
```
Narrower implementations (e.g. `x: 1`) are fine; wider are not.

---

## ⚫ Interview Questions + Answers

Q1: What is the core difference between `implements` and `extends` for classes?
A1: `extends` is **inheritance**: you get the parent's implementation and prototype chain (one parent only). `implements` is a **compile-time check** that your class matches an interface's shape: you inherit nothing, write all members, can implement many interfaces, and it vanishes at runtime.

Q2: Can a class both extend and implement? Show the syntax and the order.
A2: Yes: `class OrderRepo extends BaseRepo implements Repository<Order>, Disposable { ... }`. `extends` comes first (one class), then `implements` with a comma-separated list. The extended base's inherited members count toward satisfying the interface.

Q3: Why is "prefer composition over inheritance" often given as advice, and how do interfaces help?
A3: Deep hierarchies couple subclasses to base internals (the "fragile base class" problem), and a class can only extend one parent. Injecting collaborators typed by **interfaces** (`constructor(private notifier: Notifier)`) lets you swap implementations, fake them in tests and avoids inheriting unwanted public methods.

Q4: What happens if an interface and the class's property types differ slightly (e.g. optional vs required)?
A4: The class member must be **assignable to** the interface member. A required property satisfies an optional one; an optional property does not satisfy a required one (`TS2416`: Type 'number | undefined' is not assignable to type 'number'); wider types (`string | number` vs `number`) fail with `TS2416`. Method parameters follow bivariance for methods and are checked strictly for function-typed properties under `strictFunctionTypes`.

Q5: When would you choose an abstract class over an interface + base class?
A5: When you want one construct that gives both the **contract** (abstract members) and **shared code**, and `instanceof` support. Use an interface when multiple unrelated classes (or plain objects) must satisfy it, or when mocking with plain objects. A common design: interface for the contract, an optional abstract base for convenience, concrete classes `extends Base implements Interface`.

---

## 🔷 When to Use + When Not to Use
✅ Use `implements` when:
- You want the compiler to verify a class against a contract (providers, repositories, notifiers)
- Several interchangeable implementations exist (real vs fake in tests)
- A class needs to satisfy multiple contracts

✅ Use `extends` when:
- There is a true **is-a** relation and real shared code (BaseEntity, BaseRepository, HttpError hierarchy)
- You need `super` calls, `instanceof` checks and protected members

❌ Avoid when:
- `extends` just to reuse a couple of helpers: use composition or standalone functions
- `implements` for plain data objects: `satisfies` / typed object literals are lighter
- Deep (3+ levels) inheritance trees

---

## 📊 Visual Diagram
```
 interface Notifier { send() }                      class BaseEntity { id; describe() }
        ▲  ▲  ▲                                              ▲
        │  │  │  implements (contract, nothing inherited)    │ extends (code inherited, ONE parent)
   Sms  Push  Fake                                          Order, Invoice

 class OrderRepo  extends BaseRepo  implements Repository<Order>, Disposable
                  └──── code ─────┘            └────── contracts (many) ──────┘

 runtime:  extends  -> real prototype chain          implements -> erased (0 bytes of JS)
 compile:  extends  -> inherits types too             implements -> "does my shape match?" check
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| extends | Inherit from a parent class/interface | parent से inherit करना |
| implements | Promise to satisfy an interface | interface पूरा करने का वादा |
| Contract | Required members and types | ज़रूरी members और types का समझौता |
| Composition | Holding collaborators instead of inheriting | inherit की जगह collaborators रखना |
| Fragile base class | Base changes break subclasses | base बदलने से subclasses टूटना |
| Test double | Fake implementation of a contract | contract की नकली implementation |

---

## ⚡ 3-Line Summary
English:
1. `extends` inherits implementation from one parent; `implements` only verifies that a class matches one or many interfaces.
2. `implements` is erased at runtime and adds no types or code - you must annotate and write everything.
3. Depend on interfaces, inject them (composition), and `extend` only for true is-a hierarchies with shared code.

Hindi:
1. `extends` एक parent से implementation inherit करता है; `implements` सिर्फ जाँचता है कि class एक या कई interfaces से मेल खाती है।
2. `implements` runtime पर erase हो जाता है और कोई types या code नहीं जोड़ता - annotate करना और सब लिखना आपका काम है।
3. Interfaces पर निर्भर रहो, उन्हें inject करो (composition), और `extend` सिर्फ असली is-a hierarchy में करो जहाँ code share होता है।

---

## ➡️ Next Topic
**66. Constructor Parameter Properties** — declare and assign fields right in the constructor signature.
