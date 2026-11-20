# 110. Type-safe Builder Pattern
# हिंदी में: Type-safe Builder Pattern

> Verified with **TypeScript 5.9.3** (`--strict`). Uses a phantom type parameter, `this` parameters, key remapping with `as` (**TS 4.1+**) and template literal types. Nothing needs 5.x-only features.

---

## 🔵 Simple Definition (English)
The **Builder pattern** constructs a complex object step by step with a fluent API: `new OrderBuilder().customer("c1").items([...]).address("Pune").build()`. A **type-safe builder** goes one step further: it tracks **which required fields have been set** in a type parameter (a "phantom" type that only exists at compile time), and **`.build()` refuses to compile until every required field is provided**. In interviews this tests whether you can carry **state in the type system**.

## 🔵 सरल परिभाषा (Hindi)
**Builder pattern** किसी जटिल object को fluent API से step-by-step बनाता है: `new OrderBuilder().customer("c1").items([...]).address("Pune").build()`। **Type-safe builder** एक कदम आगे जाता है: वह एक type parameter में (एक "phantom" type जो सिर्फ compile time पर होता है) **ट्रैक करता है कि कौन से required fields set हो चुके हैं**, और **जब तक हर required field न दिया जाए `.build()` compile नहीं होता**। Interview में यह परखा जाता है कि क्या आप **type system में state** रख सकते हो।

---

## 🔴 Problem it Solves
Objects with many fields and optional bits suffer from: **telescoping constructors** (`new Order(a, b, undefined, undefined, c)`), **half-built objects** (a builder whose `.build()` throws at runtime "address is required"), and **argument order mistakes**. A plain builder moves the problem to runtime. A type-state builder makes "forgot a required field" a **compile error**, and it also removes already-used setters or flags duplicates.

## 🔴 यह क्यों बना? (Hindi)
कई fields और optional हिस्सों वाले objects में ये दिक्कतें आती हैं: **telescoping constructors** (`new Order(a, b, undefined, undefined, c)`), **अधूरे objects** (ऐसा builder जिसका `.build()` runtime पर "address is required" throw करे), और **arguments के क्रम की गलतियाँ**। साधारण builder समस्या को runtime पर धकेल देता है। Type-state builder "required field भूल गए" को **compile error** बना देता है, और इस्तेमाल हो चुके setters हटा सकता है या duplicates पकड़ सकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Describe the target type (`Order`) and list its **required keys** (`"customerId" | "items" | "address"`).
Step 2 → Make the builder class generic over a **phantom** parameter `Set extends keyof Order = never`: the union of keys already provided. Start with `never` (nothing set).
Step 3 → Each setter returns a **new builder type** with the key added: `customer(id): OrderBuilder<Set | "customerId">`. The runtime object is immutable (copy on write), so builders can be reused safely.
Step 4 → Type `build` with a **`this` parameter**: `build(this: [Exclude<Required, Set>] extends [never] ? OrderBuilder<Set> : { missing: Exclude<Required, Set> })`. If anything is missing the `this` type becomes `{ missing: ... }` and the call fails, and the error text **names the missing keys**.
Step 5 → For a **generic** builder over any `T`, use a mapped type with key remapping (``as `with${Capitalize<K>}` ``) and remove setters for keys already set.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Target type (`Order`) बताओ और उसकी **required keys** की सूची बनाओ (`"customerId" | "items" | "address"`)।
Step 2 → Builder class को **phantom** parameter `Set extends keyof Order = never` पर generic बनाओ: अब तक दी गई keys का union। शुरुआत `never` (कुछ set नहीं) से करो।
Step 3 → हर setter **नया builder type** लौटाता है जिसमें key जुड़ी होती है: `customer(id): OrderBuilder<Set | "customerId">`। Runtime object immutable (copy on write) है, इसलिए builders को सुरक्षित रूप से reuse किया जा सकता है।
Step 4 → `build` को **`this` parameter** से type करो: `build(this: [Exclude<Required, Set>] extends [never] ? OrderBuilder<Set> : { missing: Exclude<Required, Set> })`। कुछ बाकी हो तो `this` type `{ missing: ... }` बन जाता है और call fail होता है, और error text में **missing keys के नाम** दिखते हैं।
Step 5 → किसी भी `T` के **generic** builder के लिए key remapping वाला mapped type (``as `with${Capitalize<K>}` ``) इस्तेमाल करो और set हो चुकी keys के setters हटा दो।

---

## 🟡 Real World Example
**Razorpay order creation** needs `amount`, `currency`, `receipt` (required) and `notes`, `partialPayment` (optional). A support-tool developer calls `createOrder(...)` with an `amount` but forgets `currency`; the API returns 400 in production. With a typed builder, `.build()` underlines in the editor with "missing: currency". The same pattern builds **SQL queries** safely: `select(...)` and `from(...)` are required before `build()` can produce a statement.

## 🟡 Real Example Hindi mein
**Razorpay order creation** में `amount`, `currency`, `receipt` (required) और `notes`, `partialPayment` (optional) चाहिए। Support-tool का developer `amount` के साथ `createOrder(...)` call करता है पर `currency` भूल जाता है; production में API 400 लौटाती है। Typed builder के साथ `.build()` editor में "missing: currency" के साथ underline हो जाता है। यही pattern **SQL queries** को सुरक्षित बनाता है: `build()` से statement मिलने से पहले `select(...)` और `from(...)` ज़रूरी हैं।

---

## 💻 Code Example — Basic

```typescript
// order-builder.ts — class-based type-state builder
interface OrderItem { sku: string; qty: number } // one line item
interface Order { customerId: string; items: OrderItem[]; address: string; coupon?: string } // target type
type RequiredKeys = "customerId" | "items" | "address"; // coupon is optional

class OrderBuilder<Set extends keyof Order = never> { // Set = keys provided so far (phantom, compile-time only)
  private constructor(private readonly data: Partial<Order>) {} // private: start via create()
  static create(): OrderBuilder { return new OrderBuilder({}); } // nothing set yet, Set = never

  customer(id: string): OrderBuilder<Set | "customerId"> { // adds "customerId" to the set
    return new OrderBuilder({ ...this.data, customerId: id }); // immutable: new builder, copied data
  }
  items(items: OrderItem[]): OrderBuilder<Set | "items"> { // adds "items"
    return new OrderBuilder({ ...this.data, items }); // copy + new field
  }
  address(a: string): OrderBuilder<Set | "address"> { // adds "address"
    return new OrderBuilder({ ...this.data, address: a }); // copy + new field
  }
  coupon(c: string): OrderBuilder<Set | "coupon"> { // optional field
    return new OrderBuilder({ ...this.data, coupon: c }); // copy + new field
  }

  build( // callable only when no required key is missing
    this: [Exclude<RequiredKeys, Set>] extends [never] ? OrderBuilder<Set> : { missing: Exclude<RequiredKeys, Set> },
  ): Order {
    return (this as OrderBuilder<Set>).data as Order; // safe: the type check above proved all required keys exist
  }
}

const order = OrderBuilder.create() // start
  .customer("c1") // + customerId
  .address("Pune") // + address (any order is fine)
  .items([{ sku: "dosa", qty: 2 }]) // + items
  .build(); // all required present -> compiles
console.log(order); // prints { customerId: 'c1', address: 'Pune', items: [ { sku: 'dosa', qty: 2 } ] } (Node wraps it over several lines)

// ❌ items and address are missing
OrderBuilder.create().customer("c1").build();
// error TS2684: The 'this' context of type 'OrderBuilder<"customerId">' is not assignable to method's 'this' of type '{ missing: "items" | "address"; }'.
//   Property 'missing' is missing in type 'OrderBuilder<"customerId">' but required in type '{ missing: "items" | "address"; }'.
```

## 💻 Code Example — Advanced

```typescript
// generic-builder.ts — ONE builder factory for ANY type, generated setters via key remapping + Proxy
type Builder<T, Req extends keyof T, Set extends keyof T = never> = // Req = required keys, Set = provided keys
  { [K in Exclude<keyof T, Set> as `with${Capitalize<K & string>}`]-?: (value: T[K]) => Builder<T, Req, Set | K> } & // one setter per UNSET key
  ([Exclude<Req, Set>] extends [never] ? { build(): T } : {}); // build() exists only when all required keys are set

function builder<T, Req extends keyof T>(): Builder<T, Req> { // factory
  const data: Record<string, unknown> = {}; // collected values
  const proxy: unknown = new Proxy({}, { // intercept withXxx / build
    get(_target, prop: string) { // property access
      if (prop === "build") return () => ({ ...data }); // return a copy
      if (prop.startsWith("with")) { // withOrderId -> orderId
        const key = prop[4]!.toLowerCase() + prop.slice(5); // lower-case first letter
        return (value: unknown) => { data[key] = value; return proxy; }; // store, keep chaining
      }
      return undefined; // anything else does not exist
    },
  });
  return proxy as Builder<T, Req>; // one cast: runtime matches the type
}

interface Payment { orderId: string; amount: number; currency: "INR" | "USD"; note?: string } // target

const pay = builder<Payment, "orderId" | "amount" | "currency">() // required keys listed explicitly
  .withOrderId("o1") // setter generated from the key name
  .withAmount(1999) // number only
  .withCurrency("INR") // literal union only
  .build(); // exists now
console.log(pay); // prints { orderId: 'o1', amount: 1999, currency: 'INR' }

// ❌ 1. build() does not exist until required keys are set
builder<Payment, "orderId" | "amount">().withOrderId("o1").build();
// error TS2339: Property 'build' does not exist on type '{ withAmount: (value: number) => Builder<Payment, "orderId" | "amount", "orderId" | "amount">; withCurrency: (value: "INR" | "USD") => { withAmount: (value: number) => Builder<...>; withNote: (value: string | undefined) => { ...; }; }; withNote: (value: string | undefined) => { ...; }; }'.
// (tsc prints the expanded mapped type; the point is that "build" is simply not a member yet)

// ❌ 2. a setter that was already used disappears, so duplicates are caught
builder<Payment, "orderId">().withOrderId("o1").withOrderId("o2");
// error TS2339: Property 'withOrderId' does not exist on type 'Builder<Payment, "orderId", "orderId">'.

// ❌ 3. wrong value type for a setter
builder<Payment, "orderId">().withAmount("1999");
// error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.
```

---

## 🟠 Node/Express + React Integration

```typescript
// sql-builder.ts — parameterised SQL Server query builder (mssql style), select + from are mandatory
interface Q { cols: string[]; table: string; where: string[]; params: Record<string, unknown> } // internal state

class SqlBuilder<Has extends "select" | "from" = never> { // phantom: which mandatory parts exist
  private constructor(private readonly q: Partial<Q>) {} // private constructor
  static create(): SqlBuilder { return new SqlBuilder({ where: [], params: {} }); } // empty query

  select(...cols: string[]): SqlBuilder<Has | "select"> { return new SqlBuilder({ ...this.q, cols }); } // columns
  from(table: string): SqlBuilder<Has | "from"> { return new SqlBuilder({ ...this.q, table }); } // table
  where(clause: string, params: Record<string, unknown>): SqlBuilder<Has> { // parameters, never string concatenation
    return new SqlBuilder({ ...this.q, where: [...(this.q.where ?? []), clause], params: { ...this.q.params, ...params } });
  }

  build( // needs both parts: same this-parameter trick as OrderBuilder
    this: ["select" | "from"] extends [Has] ? SqlBuilder<Has> : { missing: Exclude<"select" | "from", Has> },
  ): { text: string; params: Record<string, unknown> } {
    const q = (this as SqlBuilder<Has>).q as Q; // internal access
    const w = q.where.length ? ` WHERE ${q.where.join(" AND ")}` : ""; // optional WHERE
    return { text: `SELECT ${q.cols.join(", ")} FROM ${q.table}${w}`, params: q.params }; // final statement
  }
}

const query = SqlBuilder.create().select("OrderId", "Total").from("dbo.Orders").where("UserId = @uid", { uid: 42 }).build(); // ok
console.log(query.text, query.params); // prints SELECT OrderId, Total FROM dbo.Orders WHERE UserId = @uid { uid: 42 }

// ❌ "from" is missing
SqlBuilder.create().select("*").build();
// error TS2684: The 'this' context of type 'SqlBuilder<"select">' is not assignable to method's 'this' of type '{ missing: "from"; }'.
//   Property 'missing' is missing in type 'SqlBuilder<"select">' but required in type '{ missing: "from"; }'.
// in Express: const rows = await pool.request().input("uid", query.params.uid).query(query.text);
```

```tsx
// FormConfig.tsx — React: builder for a typed form definition, rendered by one generic component
type Field = { name: string; label: string; required: boolean }; // one field

class FormBuilder { // simple fluent builder (no required-ness tracking needed here)
  private fields: Field[] = []; // collected fields
  text(name: string, label: string, required = false): this { // `this` return type keeps subclass chaining
    this.fields.push({ name, label, required }); // add
    return this; // fluent
  }
  build(): readonly Field[] { return this.fields; } // finish
}

const checkoutForm = new FormBuilder().text("name", "Full name", true).text("pin", "PIN code", true).text("note", "Note").build(); // definition

export function GenericForm({ fields }: { fields: readonly Field[] }) { // renders any definition
  return <form>{fields.map((f) => <label key={f.name}>{f.label}{f.required ? "*" : ""}<input name={f.name} /></label>)}</form>; // inputs
}
export const CheckoutForm = () => <GenericForm fields={checkoutForm} />; // usage
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: A builder that only fails at runtime
```typescript
// wrong-builder.ts
class BadBuilder {
  private d: { id?: string; amount?: number } = {}; // everything optional
  id(v: string) { this.d.id = v; return this; } // setter
  amount(v: number) { this.d.amount = v; return this; } // setter
  build(): { id: string; amount: number } { // wrong: nothing proves the fields exist
    if (this.d.id === undefined || this.d.amount === undefined) throw new Error("incomplete"); // runtime only
    return { id: this.d.id, amount: this.d.amount }; // fine after the check
  }
}
try { new BadBuilder().id("x").build(); } catch (e) { console.log((e as Error).message); } // prints incomplete
```
✅ Correct: track set keys in a phantom type parameter (Basic example), so the **compiler** reports the missing field.

❌ Mistake 2: Mutating the builder in setters and reusing it
```typescript
// shared-state.ts
class Mutable {
  items: string[] = []; // shared mutable state
  add(i: string) { this.items.push(i); return this; } // mutates in place
}
const base = new Mutable().add("tea"); // intended as a template
const a = base.add("samosa"); // a === base !
const b = base.add("jalebi"); // b === base !
console.log(a.items, a === b); // prints [ 'tea', 'samosa', 'jalebi' ] true
```
✅ Correct: return a **new** builder from every setter (copy on write) so templates stay intact.

❌ Mistake 3: Phantom parameter never used structurally
✅ Correct: if the type parameter appears nowhere in the class's members, TypeScript treats `OrderBuilder<"a">` and `OrderBuilder<"b">` as the **same** type. Using it in method return types and in the `this` parameter (as above) makes it matter. If a builder ever ignores errors, check that the phantom is referenced.

---

## 🧠 Tricky Interview Question

```typescript
// tricky.ts — why does build() compile after calling the same setter twice?
interface Cfg { host: string; port: number } // target
class CfgBuilder<Set extends keyof Cfg = never> { // phantom set
  private constructor(private readonly d: Partial<Cfg>) {} // private
  static create(): CfgBuilder { return new CfgBuilder({}); } // start
  host(h: string): CfgBuilder<Set | "host"> { return new CfgBuilder({ ...this.d, host: h }); } // add host
  port(p: number): CfgBuilder<Set | "port"> { return new CfgBuilder({ ...this.d, port: p }); } // add port
  build(this: [Exclude<keyof Cfg, Set>] extends [never] ? CfgBuilder<Set> : { missing: Exclude<keyof Cfg, Set> }): Cfg {
    return (this as CfgBuilder<Set>).d as Cfg; // proven by the this-check
  }
}
const c = CfgBuilder.create().host("a").host("b").port(80).build(); // two host() calls
console.log(c.host, c.port); // prints b 80
```
**Answer:** It compiles and prints `b 80`: `Set | "host"` applied twice is still just `"host" | "port"`, and the **last value wins** at runtime. A union type has no notion of "how many times". To **forbid duplicates** remove the setter once used (the generic `Builder` in the Advanced example does this with `Exclude<keyof T, Set>`), or make the setter's `this` type require `"host"` to be absent from `Set`.

---

## ⚫ Interview Questions + Answers

Q1: What is a phantom type parameter?
A1: A type parameter that is not used to store data but to carry **compile-time information** (here, which keys are set). It has no runtime representation.

Q2: Why a `this` parameter on `build`?
A2: A `this` parameter lets a method declare what **type of receiver** it accepts. When the builder's `Set` is incomplete, the receiver type becomes `{ missing: ... }`, so the call fails and the message names the missing keys. It is erased at runtime.

Q3: Why return a new builder from each setter?
A3: Because each step has a **different type** (`Set` grows), returning `this` would keep the old type. Immutability also makes partially-built templates reusable.

Q4: How do key-remapped mapped types create setters?
A4: ``{ [K in keyof T as `with${Capitalize<K & string>}`]-?: (v: T[K]) => ... }`` generates a `withX` method for every key `K`, with the right value type, and `-?` strips optionality so setters stay callable.

Q5: Builder vs object literal with defaults?
A5: A literal plus `satisfies`/required fields is simpler and should be the default. A builder pays off for **many optional parts, ordering rules, derived values or a step-wise DSL** (queries, test fixtures, HTTP requests, form definitions).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Constructing objects with many optional parts or validation rules (SQL queries, HTTP requests, test data factories)
- You want "forgot a required field" to be a compile error

❌ Avoid when:
- The object has 3-4 fields, a plain object literal typed with the interface is clearer
- You only need defaults/overrides: `{ ...defaults, ...overrides }` is enough

---

## 📊 Visual Diagram
```
 OrderBuilder<never>
     │ .customer("c1")
     ▼
 OrderBuilder<"customerId">
     │ .address("Pune")
     ▼
 OrderBuilder<"customerId" | "address">     .build()  ✗  { missing: "items" }
     │ .items([...])
     ▼
 OrderBuilder<"customerId" | "address" | "items">   .build()  ✓  -> Order

 build(this: [Exclude<Required, Set>] extends [never] ? Builder : { missing: ... })
                   └──── nothing left to set? ────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Builder pattern | Step-by-step object construction | Step-by-step object निर्माण |
| Fluent API | Chained method calls returning the builder | Chain होने वाले method calls |
| Phantom type | Type parameter with no runtime data | Runtime data के बिना type parameter |
| Type-state | State of a process encoded in a type | Process की state type में |
| `this` parameter | Declares the receiver type of a method | Method के receiver का type |
| Key remapping | `as` clause renaming keys in mapped types | Mapped type में keys का नाम बदलना |

---

## ⚡ 3-Line Summary
English:
1. A type-safe builder tracks provided keys in a phantom type parameter and each setter returns a builder with the key added.
2. `build()` uses a `this` parameter (or exists only conditionally) so it compiles only when all required keys are set, and the error names what is missing.
3. Return new builders from setters (immutability) and use key-remapped mapped types to generate setters for any `T`.

Hindi:
1. Type-safe builder दी गई keys को phantom type parameter में ट्रैक करता है और हर setter key जुड़ा हुआ builder लौटाता है।
2. `build()` में `this` parameter (या conditional अस्तित्व) होता है, इसलिए यह तभी compile होता है जब सारी required keys set हों, और error बताता है क्या बाकी है।
3. Setters से नए builders लौटाओ (immutability) और किसी भी `T` के setters बनाने के लिए key-remapped mapped types इस्तेमाल करो।

---

## ➡️ Next Topic
**111. Typed Dependency Injection Container** — registering and resolving services with token-to-type maps.
