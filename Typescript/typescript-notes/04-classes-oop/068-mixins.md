# 68. Mixins
# हिंदी में: Mixins (कई छोटी classes का behaviour एक class में जोड़ना)

> Verified with TypeScript 5.9 (`tsc --strict`). Mixin constructor rule (`any[]` rest) is stable since TS 2.2. Decorators are NOT used here.

---

## 🔵 Simple Definition (English)
A **mixin** is a function that takes a class and returns a **new class that extends it** with extra properties/methods. Because JavaScript/TypeScript classes allow only **single inheritance** (`extends A, B` is illegal), mixins let you "snap together" reusable behaviours - `Timestamped`, `SoftDeletable`, `Auditable` - on top of a base class: `class Order extends Timestamped(SoftDeletable(Base))`.

## 🔵 सरल परिभाषा (Hindi)
**Mixin** एक function है जो एक class लेता है और उसे `extend` करने वाली **नई class return करता है**, जिसमें extra properties/methods होते हैं। JavaScript/TypeScript में **single inheritance** ही है (`extends A, B` लिखना मना है), इसलिए mixins से हम reusable behaviours - `Timestamped`, `SoftDeletable`, `Auditable` - को base class के ऊपर "जोड़" सकते हैं: `class Order extends Timestamped(SoftDeletable(Base))`।

---

## 🔴 Problem it Solves
In a SQL Server backend, `Order`, `User`, `Payment` all need `createdAt/updatedAt`, many need soft-delete (`deletedAt`), some need audit info. With single inheritance you either (1) put everything in one fat `BaseEntity` (every class gets features it does not need), (2) copy-paste the same fields, or (3) build a deep chain `A -> B -> C` that is rigid. Mixins let each class **pick exactly the capabilities it needs**, and TypeScript tracks the resulting type.

## 🔴 यह क्यों बना? (Hindi)
SQL Server backend में `Order`, `User`, `Payment` सबको `createdAt/updatedAt` चाहिए, कुछ को soft-delete (`deletedAt`), कुछ को audit info। Single inheritance में या तो (1) सब कुछ एक मोटी `BaseEntity` में डालो (हर class को वो features भी मिलते हैं जो नहीं चाहिए), (2) fields copy-paste करो, या (3) गहरी chain `A -> B -> C` बनाओ जो rigid है। Mixins से हर class **सिर्फ वही capabilities चुनती है जो चाहिए**, और TypeScript final type track करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Declare a constructor type: `type Constructor<T = {}> = new (...args: any[]) => T;`.
Step 2 → Write a function `function Timestamped<TBase extends Constructor>(Base: TBase)`.
Step 3 → Inside, `return class extends Base { ... }` - an anonymous class that extends whatever was passed in.
Step 4 → The `...args: any[]` constructor is required: TypeScript demands a mixin class constructor take a single rest parameter of type `any[]`.
Step 5 → The return type is inferred as `{ new (...args): (anonymous class) } & TBase`, so the new members are typed automatically.
Step 6 → Compose: `class Order extends Timestamped(SoftDeletable(BaseEntity))`. Order of application = order of inheritance chain.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Constructor type declare करो: `type Constructor<T = {}> = new (...args: any[]) => T;`।
Step 2 → Function लिखो `function Timestamped<TBase extends Constructor>(Base: TBase)`।
Step 3 → अंदर `return class extends Base { ... }` - एक anonymous class जो जो भी pass हुआ उसे extend करती है।
Step 4 → `...args: any[]` constructor ज़रूरी है: TypeScript mixin class के constructor में सिर्फ एक rest parameter `any[]` माँगता है।
Step 5 → Return type अपने आप `{ new (...args): (anonymous class) } & TBase` infer होता है, इसलिए नए members typed मिलते हैं।
Step 6 → Compose करो: `class Order extends Timestamped(SoftDeletable(BaseEntity))`। जिस क्रम में apply किया, वही inheritance chain का क्रम है।

---

## 🟡 Real World Example
**Swiggy's order service**: `Order`, `Restaurant` and `Coupon` entities all stored in SQL Server. `Order` needs timestamps + soft-delete + an audit trail; `Coupon` needs only timestamps. The team writes three tiny mixins once and each entity composes only what it needs. A repository function can then require "anything that is `Timestamped`" without caring about the concrete class.

## 🟡 Real Example Hindi mein
**Swiggy की order service**: `Order`, `Restaurant` और `Coupon` entities SQL Server में रहती हैं। `Order` को timestamps + soft-delete + audit trail चाहिए; `Coupon` को सिर्फ timestamps। Team तीन छोटे mixins एक बार लिखती है और हर entity सिर्फ वही compose करती है जो चाहिए। फिर repository function कह सकता है "कोई भी `Timestamped` चीज़ चलेगी", concrete class की परवाह किए बिना।

---

## 💻 Code Example — Basic

```typescript
// 1) A "constructor type": anything you can call with `new`
type Constructor<T = {}> = new (...args: any[]) => T;

// 2) Mixin: adds createdAt/updatedAt + touch() to ANY class
function Timestamped<TBase extends Constructor>(Base: TBase) {
  return class Timestamped extends Base { // anonymous-ish class extending the input
    createdAt = new Date(); // new field added by the mixin
    updatedAt = new Date(); // another new field

    touch(): void {
      this.updatedAt = new Date(); // update the timestamp
    }
  };
}

// 3) Mixin: adds soft delete support
function SoftDeletable<TBase extends Constructor>(Base: TBase) {
  return class SoftDeletable extends Base {
    deletedAt: Date | null = null; // null means "still alive"

    softDelete(): void {
      this.deletedAt = new Date(); // mark as deleted, row stays in SQL table
    }

    get isDeleted(): boolean {
      return this.deletedAt !== null; // computed flag
    }
  };
}

// 4) A plain base class
class Entity {
  constructor(public readonly id: number) {} // every entity has an id
}

// 5) Compose: Order gets BOTH behaviours
class Order extends Timestamped(SoftDeletable(Entity)) {
  constructor(id: number, public total: number) {
    super(id); // goes down the chain to Entity(id)
  }
}

const order = new Order(101, 499); // create an order
order.touch(); // from Timestamped
order.softDelete(); // from SoftDeletable
console.log(order.id, order.total, order.isDeleted); // 101 499 true
console.log(order.createdAt instanceof Date); // true
```

## 💻 Code Example — Advanced

```typescript
type Constructor<T = {}> = new (...args: any[]) => T;

// ----- Constrained mixin: only classes that already have `id` -----
type HasId = { id: number };

function Auditable<TBase extends Constructor<HasId>>(Base: TBase) {
  return class Auditable extends Base {
    private auditLog: string[] = []; // private to the mixin class

    audit(action: string): void {
      // we can use `this.id` because TBase is constrained to HasId
      this.auditLog.push(`#${this.id}: ${action}`);
    }

    getAudit(): readonly string[] {
      return this.auditLog; // expose read-only view
    }
  };
}

// ----- Mixin that adds a static member and uses a generic -----
function Serializable<TBase extends Constructor<HasId>>(Base: TBase) {
  return class Serializable extends Base {
    static fromJSON<T extends Serializable>(
      this: new (...args: any[]) => T, // `this` type = the concrete class
      json: string,
    ): T {
      const data = JSON.parse(json) as Record<string, unknown>; // parse text
      return Object.assign(new this(data.id as number), data); // build + copy fields
    }

    serialize(): string {
      return JSON.stringify({ ...this }); // plain JSON of all fields (spread avoids toJSON recursion)
    }
  };
}

class Base {
  constructor(public id: number) {} // minimal base with id
}

class Payment extends Serializable(Auditable(Base)) {
  amount = 0; // domain field
}

const p = new Payment(7); // create payment #7
p.amount = 250;
p.audit("captured"); // from Auditable
p.audit("refunded"); // from Auditable
console.log(p.getAudit()); // [ '#7: captured', '#7: refunded' ]  (real output)
const json = p.serialize(); // from Serializable
console.log(json.includes('"amount":250')); // true

// ----- Type of "anything Auditable" for function parameters -----
type AuditableInstance = InstanceType<ReturnType<typeof Auditable<Constructor<HasId>>>>;
function report(x: AuditableInstance): number {
  return x.getAudit().length; // works for every Auditable class
}
console.log(report(p)); // 2
```

---

## 🟠 Node/Express + React Integration

```typescript
import express from "express"; // Express server

type Constructor<T = {}> = new (...args: any[]) => T;

// Reusable mixin for DB entities mapped from SQL Server rows
function WithTimestamps<TBase extends Constructor>(Base: TBase) {
  return class extends Base {
    createdAt = new Date(); // set when object is created
    updatedAt = new Date();
  };
}

class OrderRow {
  constructor(public id: number, public total: number) {} // columns from Orders table
}

class OrderEntity extends WithTimestamps(OrderRow) {} // row + timestamps

const app = express(); // create app
app.get("/orders/:id", (req, res) => {
  const e = new OrderEntity(Number(req.params.id), 750); // pretend we loaded it
  res.json({ id: e.id, total: e.total, createdAt: e.createdAt }); // typed access
});
```

```tsx
// React: a Redux-style "entity" shape shared with the server (plain data, no classes)
import React from "react";

interface OrderDTO {
  id: number;
  total: number;
  createdAt: string; // Date arrives as ISO string in JSON
}

export function OrderRowView({ order }: { order: OrderDTO }) {
  // Mixins live on the server; React receives plain DTOs (class instances are
  // NOT serializable, so never put them in Redux state)
  return (
    <li>
      #{order.id} - Rs.{order.total} ({new Date(order.createdAt).toLocaleDateString()})
    </li>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mixin constructor with specific parameters
```typescript
type Constructor<T = {}> = new (...args: any[]) => T;
function Bad<TBase extends Constructor>(Base: TBase) {
  return class extends Base {
    constructor(name: string) { // ❌ error TS2545: A mixin class must have a constructor with a single rest parameter of type 'any[]'.
      super();
    }
  };
}
```
✅ Fix: `constructor(...args: any[]) { super(...args); }`.

❌ Mistake 2: Forgetting the `Constructor` constraint
```typescript
function NoConstraint<TBase>(Base: TBase) {
  return class extends Base {}; // ❌ error TS2507: Type 'TBase' is not a constructor function type.
}
```

❌ Mistake 3: Calling a method the mixin did not add
```typescript
type Constructor<T = {}> = new (...args: any[]) => T;
function Timestamped<TBase extends Constructor>(Base: TBase) {
  return class extends Base { touch() {} };
}
class Entity {}
class Coupon extends Timestamped(Entity) {}
new Coupon().softDelete(); // ❌ error TS2339: Property 'softDelete' does not exist on type 'Coupon'.
```

❌ Mistake 4: Exporting a mixin whose class has a `private` member while `declaration: true`
```typescript
type Constructor<T = {}> = new (...args: any[]) => T;
export function Counted<TBase extends Constructor>(Base: TBase) {
  return class extends Base {
    private n = 0; // ❌ error TS4094: Property 'n' of exported anonymous class type may not be private or protected.
    inc() { return ++this.n; }
  };
}
```
Fix (checked with `--declaration`): use an ES `#n` private field or keep the mixin non-exported.

---

## 🧠 Tricky Interview Question

```typescript
type Constructor<T = {}> = new (...args: any[]) => T;
function A<T extends Constructor>(B: T) { return class extends B { who = "A"; }; }
function B<T extends Constructor>(Base: T) { return class extends Base { who = "B"; }; }
class Root {}
class X extends A(B(Root)) {}
console.log(new X().who);
```
Answer: `"A"`. `A(B(Root))` creates the chain `Root -> B-class -> A-class -> X`. Field initializers run from the base downward, so `B` sets `who = "B"` first and then `A` overwrites it with `"A"`. **The outermost mixin wins.** Verified by running it with `tsx`: prints `A`, and `tsc --strict` raises no error - same-named members silently override, so mixin order matters.

---

## ⚫ Interview Questions + Answers

Q1: What is a mixin and why not just use inheritance?
A1: A function `Class -> Class` that adds behaviour. Single inheritance forces one parent; mixins give composition of several capabilities without a deep tree.

Q2: Why must the mixin constructor be `(...args: any[])`?
A2: The compiler cannot know the base constructor's parameters at generic level, so it requires the constructor to forward everything. TS2545 otherwise.

Q3: Mixins vs interface + `implements`?
A3: `implements` only checks shape, no code is shared. A mixin shares **implementation** and the type. Interfaces are for contracts, mixins for reuse.

Q4: Mixins vs composition (has-a)?
A4: Composition (`this.audit = new AuditTrail()`) is simpler and avoids name collisions; prefer it unless you need the behaviour to appear directly on the instance or to be used across many entities.

Q5: How do you constrain a mixin to classes that already have certain members?
A5: `Constructor<HasId>` - e.g., `TBase extends Constructor<{ id: number }>`; inside the mixin `this.id` is then typed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several unrelated classes share the same small capability (timestamps, soft delete, events)
- You need to stack behaviours in different combinations

❌ Avoid when:
- Plain composition or a helper function is enough
- Members could collide (same names) - debugging order becomes painful
- Instances must be serialized into Redux/React state (use plain DTOs)

---

## 📊 Visual Diagram
```
 class Order extends Timestamped(SoftDeletable(Entity))

   Entity            id
     ▲
 SoftDeletable(...)  + deletedAt, softDelete(), isDeleted
     ▲
 Timestamped(...)    + createdAt, updatedAt, touch()
     ▲
   Order             + total          (final class)

 Constructor call: new Order(1, 99) -> goes up the chain via super(...args)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Mixin | Function returning an extended class | Extended class return करने वाला function |
| Constructor type | `new (...args: any[]) => T` | `new` से बनने वाली चीज़ का type |
| Single inheritance | A class can extend only one class | एक class सिर्फ एक class extend कर सकती है |
| Composition | Holding objects instead of inheriting | Inherit करने की जगह objects रखना |
| Soft delete | Mark deleted, keep the row | Row हटाओ नहीं, सिर्फ deleted mark करो |
| Constraint | `extends` bound on a generic | Generic पर लगी शर्त |

---

## ⚡ 3-Line Summary
English:
1. A mixin is a function `(Base) => class extends Base {...}` that adds typed behaviour to any class.
2. The constructor must be `(...args: any[])` and the generic must extend `Constructor`.
3. Stack them (`A(B(Base))`); the outermost wins on name clashes; prefer composition when simpler.

Hindi:
1. Mixin एक function `(Base) => class extends Base {...}` है जो किसी भी class में typed behaviour जोड़ता है।
2. Constructor `(...args: any[])` होना चाहिए और generic को `Constructor` extend करना चाहिए।
3. इन्हें stack करो (`A(B(Base))`); नाम टकराए तो सबसे बाहरी जीतता है; आसान हो तो composition चुनो।

---

## ➡️ Next Topic
**69. Generic Classes** - Classes parameterised by type (`Repository<T>`, `Stack<T>`), with constraints and defaults.
