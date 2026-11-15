# 67. Decorators (experimental vs TC39 standard)
# हिंदी में: Decorators (experimental बनाम TC39 standard)

> Verified with **TypeScript 5.x** (compiled with 5.9, `--strict`). **Standard (TC39 Stage 3) decorators = TS 5.0** — no flag needed. **Legacy/experimental decorators** = `--experimentalDecorators` flag (the NestJS / TypeORM / Angular world). The two are **not compatible**.

---

## 🔵 Simple Definition (English)
A **decorator** is a function that wraps or annotates a class or a class member (method, getter/setter, field, accessor). You attach it with `@name` above the declaration. It receives the thing being decorated and may **replace it** with a new version — for example, wrapping a method to add logging, caching or retry.

TypeScript supports **two different decorator systems**:
- **Standard decorators (TS 5.0+)** — follow the TC39 proposal (Stage 3, shipping in JS engines). Signature: `(value, context) => newValue | void`. No compiler flag.
- **Experimental decorators (legacy)** — the old TS 1.5 design. Signature: `(target, propertyKey, descriptor)`. Needs `"experimentalDecorators": true`. Also supports **parameter decorators** and `emitDecoratorMetadata` (needed by NestJS DI and TypeORM).

## 🔵 सरल परिभाषा (Hindi)
**Decorator** एक function है जो किसी class या class के member (method, getter/setter, field, accessor) को wrap या annotate करता है। आप उसे declaration के ऊपर `@name` लिखकर जोड़ते हो। उसे decorate होने वाली चीज़ मिलती है और वह उसे **नए version से replace** कर सकता है — जैसे method को wrap करके logging, caching या retry जोड़ना।

TypeScript में **दो अलग decorator systems** हैं:
- **Standard decorators (TS 5.0+)** — TC39 proposal (Stage 3) को follow करते हैं। Signature: `(value, context) => newValue | void`। कोई compiler flag नहीं।
- **Experimental decorators (legacy)** — पुराना TS 1.5 design। Signature: `(target, propertyKey, descriptor)`। `"experimentalDecorators": true` चाहिए। **Parameter decorators** और `emitDecoratorMetadata` भी सपोर्ट करता है (NestJS DI और TypeORM को चाहिए)।

---

## 🔴 Problem it Solves
Cross-cutting concerns — logging, timing, caching, auth checks, retry — get copy-pasted into every method:

```
async createOrder() { console.log("start"); const t = Date.now(); ...; console.log(Date.now() - t); }
async refundPayment() { console.log("start"); const t = Date.now(); ...; console.log(Date.now() - t); }
```

A decorator lets you write that wrapper **once** and apply it with one line: `@logged`. Frameworks use the same idea declaratively: `@Controller("orders")`, `@Get(":id")`, `@Injectable()`.

## 🔴 यह क्यों बना? (Hindi)
Cross-cutting काम — logging, timing, caching, auth check, retry — हर method में copy-paste हो जाते हैं:

```
async createOrder() { console.log("start"); const t = Date.now(); ...; console.log(Date.now() - t); }
async refundPayment() { console.log("start"); const t = Date.now(); ...; console.log(Date.now() - t); }
```

Decorator से वह wrapper **एक बार** लिखो और एक line में लगाओ: `@logged`। Frameworks यही idea declaratively use करते हैं: `@Controller("orders")`, `@Get(":id")`, `@Injectable()`।

---

## 🟢 How it Works — Step by Step

Step 1 → A standard decorator is a function `(value, context)`. `value` is the original method/class; `context` describes it (`context.kind`, `context.name`, `context.addInitializer`).
Step 2 → For a **method decorator**, you return a replacement function (or nothing to keep the original).
Step 3 → Type the pieces with `ClassMethodDecoratorContext`, `ClassDecoratorContext`, `ClassFieldDecoratorContext`, `ClassAccessorDecoratorContext` (built into `lib.decorators.d.ts`).
Step 4 → Decorators run **once, at class definition time** (not per call). The wrapper they return runs per call.
Step 5 → Multiple decorators apply **bottom-to-top** (closest to the member first), like function composition.
Step 6 → Legacy decorators: enable `experimentalDecorators`; the method decorator gets `(target, key, descriptor)` and mutates `descriptor.value`. **Never mix** the two styles in one project — the flag decides which system the compiler uses.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Standard decorator एक function `(value, context)` है। `value` original method/class है; `context` उसका description (`context.kind`, `context.name`, `context.addInitializer`)।
Step 2 → **Method decorator** में आप replacement function return करते हो (या कुछ नहीं, तो original रहता है)।
Step 3 → Pieces को `ClassMethodDecoratorContext`, `ClassDecoratorContext`, `ClassFieldDecoratorContext`, `ClassAccessorDecoratorContext` से type करो (`lib.decorators.d.ts` में built-in)।
Step 4 → Decorators **class definition के समय एक बार** चलते हैं (हर call पर नहीं)। जो wrapper वे return करते हैं वह हर call पर चलता है।
Step 5 → कई decorators **नीचे से ऊपर** apply होते हैं (member के सबसे पास वाला पहले), function composition की तरह।
Step 6 → Legacy decorators: `experimentalDecorators` on करो; method decorator को `(target, key, descriptor)` मिलता है और आप `descriptor.value` बदलते हो। एक project में दोनों styles **कभी mix न करें** — flag तय करता है कि compiler कौन सा system लेगा।

---

## 🟡 Real World Example
**Razorpay-style payments service**: `PaymentService.capture()` calls a flaky bank API. The team writes `@retry(3)` and `@timed` once and stamps them on `capture`, `refund` and `verifySignature`. On the NestJS side the same team uses legacy decorators (`@Controller`, `@Post`, `@Body`) because Nest still relies on `experimentalDecorators` + `emitDecoratorMetadata` for dependency injection.

## 🟡 Real Example Hindi mein
**Razorpay-style payments service**: `PaymentService.capture()` एक flaky bank API call करता है। टीम `@retry(3)` और `@timed` एक बार लिखती है और `capture`, `refund`, `verifySignature` पर लगा देती है। NestJS side पर वही टीम legacy decorators (`@Controller`, `@Post`, `@Body`) use करती है क्योंकि Nest अभी भी dependency injection के लिए `experimentalDecorators` + `emitDecoratorMetadata` पर टिका है।

---

## 💻 Code Example — Basic

```typescript
// Standard (TC39) method decorator — TS 5.0+, NO compiler flag needed
// A decorator factory-less decorator that logs every call of a method

// 'value' = the original method, 'context' = info about the decorated member
function logged<This, Args extends unknown[], Return>(
  value: (this: This, ...args: Args) => Return, // the original method's type
  context: ClassMethodDecoratorContext<This, (this: This, ...args: Args) => Return> // metadata type
) {
  const methodName = String(context.name); // name of the method, e.g. "total"
  // return a replacement method with the same signature
  return function (this: This, ...args: Args): Return {
    console.log(`-> ${methodName}(${args.join(", ")})`); // log before the call
    const result = value.call(this, ...args); // call the original with the right 'this'
    console.log(`<- ${methodName} = ${String(result)}`); // log after the call
    return result; // pass the original result through
  };
}

class Cart {
  // fields: price list in rupees
  constructor(private prices: number[]) {}

  @logged // applied ONCE when the class is defined
  total(discountPercent: number): number {
    const sum = this.prices.reduce((a, b) => a + b, 0); // add all item prices
    return sum - (sum * discountPercent) / 100; // apply discount
  }
}

const cart = new Cart([250, 180, 90]); // Zomato-style cart
cart.total(10); // logs the call and the result
// Real output (tsx 5.x run):
// -> total(10)
// <- total = 468
```

## 💻 Code Example — Advanced

```typescript
// Decorator FACTORIES (take config), class decorator, field decorator, stacking order

// Factory: retry(times) returns the actual decorator
function retry(times: number) {
  // returned function is the real method decorator
  return function <This, Args extends unknown[], Return>(
    value: (this: This, ...args: Args) => Promise<Return>, // only async methods allowed
    _context: ClassMethodDecoratorContext<This, (this: This, ...args: Args) => Promise<Return>>
  ) {
    return async function (this: This, ...args: Args): Promise<Return> {
      let lastError: unknown; // remember the last failure
      for (let attempt = 1; attempt <= times; attempt++) {
        try {
          return await value.call(this, ...args); // success -> return immediately
        } catch (e) {
          lastError = e; // store and try again
          console.log(`attempt ${attempt} failed`);
        }
      }
      throw lastError; // all attempts failed
    };
  };
}

// Class decorator: seals the class so nobody can add properties to the prototype
function sealed<T extends new (...args: never[]) => object>(
  value: T, // the class constructor
  _context: ClassDecoratorContext<T> // class context
) {
  Object.seal(value); // freeze the constructor shape
  Object.seal(value.prototype); // and the prototype
}

// Field decorator: runs an initializer function to transform the initial value
function upper(_value: undefined, _context: ClassFieldDecoratorContext<object, string>) {
  // returning a function lets us change the initial value of the field
  return (initial: string) => initial.toUpperCase();
}

let calls = 0; // simulate a flaky bank API: fails twice, then works

@sealed
class PaymentService {
  @upper
  currency = "inr"; // becomes "INR" after the field decorator

  @retry(3)
  async capture(orderId: string): Promise<string> {
    calls++; // count attempts
    if (calls < 3) throw new Error("bank timeout"); // first two calls fail
    return `captured ${orderId}`; // third call succeeds
  }
}

async function main() {
  const svc = new PaymentService(); // create the service
  console.log(svc.currency); // field decorator applied
  console.log(await svc.capture("ORD-501")); // retried automatically
}
main();
// Real output (tsx 5.x run):
// INR
// attempt 1 failed
// attempt 2 failed
// captured ORD-501
```

---

## 🟠 Node/Express + React Integration

```typescript
// exp: experimentalDecorators ON (legacy) — what NestJS / TypeORM style code uses
// Legacy decorator: (target, key, descriptor). Here: a tiny route registry for Express.
import express from "express";

type Handler = (req: express.Request, res: express.Response) => void; // Express handler type
const routes: { method: "get" | "post"; path: string; handler: Handler }[] = []; // global registry

// factory: Get("/orders") registers the decorated method as an Express route
function Get(path: string) {
  return function (_target: object, _key: string, descriptor: PropertyDescriptor) {
    routes.push({ method: "get", path, handler: descriptor.value as Handler }); // store the method
  };
}

class OrderController {
  @Get("/orders") // legacy method decorator
  list(_req: express.Request, res: express.Response) {
    res.json([{ id: 1, item: "Biryani", amount: 320 }]); // hard-coded demo data
  }
}

const app = express(); // create app
const controller = new OrderController(); // instance for 'this'
for (const r of routes) {
  // bind each handler to the controller instance, then mount it
  app[r.method](r.path, (req, res) => r.handler.call(controller, req, res));
}
```

React side: **React itself does not use decorators** (class components with `@observer` from MobX are the only common case). Redux Toolkit does not need them. In a Next.js/Vite front-end, keep `experimentalDecorators` OFF; it is only a back-end (Nest/TypeORM) concern. In a monorepo, give the API package its own `tsconfig` with the flag and leave the React package on the standard system.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a **legacy** decorator signature without the flag (TS 5 uses the standard system by default)
```typescript
// ❌ legacy signature (target, key, descriptor) while experimentalDecorators is OFF
function oldLog(_target: object, _key: string, descriptor: PropertyDescriptor) {
  console.log(descriptor.value);
}
class A {
  @oldLog
  run() {}
}
// Real compiler message:
// error TS1241: Unable to resolve signature of method decorator when called as an expression.
//   This expression is not callable. ...
```
✅ Fix: either turn on `"experimentalDecorators": true` (and stay legacy everywhere), or rewrite as `(value, context)`.

❌ Mistake 2: Putting a decorator on the wrong kind of member
```typescript
// ❌ method decorator used on a field
function m(_v: Function, _c: ClassMethodDecoratorContext) {}
class B {
  @m
  x = 1;
}
```
✅ Fix: use `ClassFieldDecoratorContext` for fields, and match the decorator to the member kind.

❌ Mistake 3: Using **parameter decorators** (`@Body() dto`) with standard decorators
✅ Correct: standard decorators have **no parameter decorators**. That is exactly why NestJS stays on `experimentalDecorators`. Do not migrate Nest code just because TS 5 shipped new decorators.

---

## 🧠 Tricky Interview Question

```typescript
function a(_v: Function, c: ClassMethodDecoratorContext) { console.log("a", c.name); }
function b(_v: Function, c: ClassMethodDecoratorContext) { console.log("b", c.name); }
class T {
  @a
  @b
  go() {}
}
new T(); new T();
```
**Q: What is printed?**
**Answer:** `b go` then `a go`, printed **once** — not twice. Decorators run at **class definition**, not per instance, and the one closest to the method (`@b`) is applied first. Creating two instances prints nothing more. (Decorator *expressions* are evaluated top-to-bottom, but *applied* bottom-to-top.)

---

## ⚫ Interview Questions + Answers

Q1: What are the two decorator systems in TypeScript?
A1: Experimental/legacy (`experimentalDecorators`, signature `(target, key, descriptor)`, supports parameter decorators and `emitDecoratorMetadata`) and standard TC39 (TS 5.0+, signature `(value, context)`, no flag, no parameter decorators yet).

Q2: Why does NestJS still use experimental decorators?
A2: Its DI relies on `emitDecoratorMetadata` (constructor parameter types emitted at runtime) and on parameter decorators like `@Body()`/`@Param()`. Standard decorators offer neither, so Nest, TypeORM and Angular stay on the legacy system.

Q3: When does a decorator run - at class definition or on each call?
A3: At class definition (once). What it **returns** — a wrapper function — runs on each call. Confusing these two is the most common interview slip.

Q4: What is a decorator factory?
A4: A function that returns a decorator, so you can pass config: `@retry(3)`. `retry(3)` is evaluated first and yields the real decorator.

Q5: How do you type a standard method decorator?
A5: Generic over `This`, `Args` and `Return`: `(value: (this: This, ...args: Args) => Return, context: ClassMethodDecoratorContext<This, ...>)` and return a function with the same signature, so the decorated method keeps its type.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You apply the same cross-cutting wrapper (log, retry, cache, authz) to many methods
- You work with a framework built on decorators (NestJS, TypeORM, Angular)
- New code with no framework constraint: prefer **standard** decorators

❌ Avoid when:
- A plain higher-order function does the job (`withRetry(fn)`) — simpler, easier to debug
- You need parameter decorators or `emitDecoratorMetadata` (stay legacy)
- You would mix both systems in one project (the flag is global)

---

## 📊 Visual Diagram
```
DECORATORS — TWO SYSTEMS
──────────────────────────────────────────────
 STANDARD (TS 5.0+)            LEGACY (flag)
 (value, context)              (target, key, descriptor)
 no flag                       experimentalDecorators
 no param decorators           param decorators + metadata
        │                              │
        └── runs ONCE at class definition ──┘

  @a            apply order
  @b      ──►   b first, then a (bottom -> top)
  go() {}

  call go() ─► wrapper from a ─► wrapper from b ─► original go()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Decorator | Function wrapping a class/member | Class/member को wrap करने वाला function |
| Decorator factory | Function returning a decorator | Decorator return करने वाला function |
| context object | Metadata passed to a standard decorator | Standard decorator को मिला metadata |
| experimentalDecorators | Flag for the legacy system | Legacy system का flag |
| emitDecoratorMetadata | Emits runtime type info (DI) | Runtime type info emit करना (DI) |
| Cross-cutting concern | Logic shared across many methods | कई methods में साझा logic |

---

## ⚡ 3-Line Summary
English:
1. TS 5.0+ has **standard decorators** `(value, context)` with no flag; the old `experimentalDecorators` system is separate and incompatible.
2. Decorators run once at class definition; the wrapper they return runs on every call; stacked ones apply bottom-to-top.
3. NestJS/TypeORM/Angular still need the legacy system (parameter decorators + metadata); for new code without a framework, use standard decorators.

Hindi:
1. TS 5.0+ में बिना flag के **standard decorators** `(value, context)` हैं; पुराना `experimentalDecorators` system अलग और incompatible है।
2. Decorators class definition पर एक बार चलते हैं; उनका returned wrapper हर call पर; stacked decorators नीचे से ऊपर apply होते हैं।
3. NestJS/TypeORM/Angular को अभी legacy system चाहिए (parameter decorators + metadata); framework के बिना नए code में standard decorators use करो।

---

## ➡️ Next Topic
**68. Mixins** — Composing behaviour from several small classes when TypeScript only allows a single `extends`.
