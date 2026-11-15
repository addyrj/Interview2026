# 21. Function Types and Return Types
# हिंदी में: Function Types और Return Types

> TypeScript 5.x | Function types are erased at runtime | Inferred type predicates in `filter` arrive in TS 5.5

---

## 🔵 Simple Definition (English)
In TypeScript a **function type** describes what a function accepts and returns: `(a: number, b: number) => number`. You can annotate parameters (required) and the **return type** (optional, often inferred). Function types can be written as a **function type expression** (`type Fn = (x: string) => void`), as a **call signature** inside an object type or interface (`{ (x: string): void; label: string }`), or as a **constructor signature** (`new (x: string) => Foo`). Special return types are `void` (result is ignored), `never` (never returns normally: throws or loops forever) and `Promise<T>` (async functions).

## 🔵 सरल परिभाषा (Hindi)
TypeScript में **function type** बताता है कि function क्या लेता है और क्या लौटाता है: `(a: number, b: number) => number`। Parameters annotate करने पड़ते हैं (ज़रूरी) और **return type** optional है (अक्सर infer हो जाता है)। Function types तीन तरह से लिखे जाते हैं: **function type expression** (`type Fn = (x: string) => void`), object type या interface के अंदर **call signature** (`{ (x: string): void; label: string }`), या **constructor signature** (`new (x: string) => Foo`)। खास return types हैं `void` (result की परवाह नहीं), `never` (कभी सामान्य रूप से नहीं लौटता: throw या अनंत loop) और `Promise<T>` (async functions)।

---

## 🔴 Problem it Solves
In JavaScript, a function's contract lives in the author's head. Callers pass the wrong number or order of arguments, forget that a function returns a Promise, or call a callback with unexpected values. In a typical Express + React app, callbacks are everywhere: route handlers, `onClick`, Redux thunks, `array.map`. Function types make each of these contracts explicit and checked: the wrong arity (`Expected 2 arguments, but got 1`), the wrong argument type or the wrong return value is a compile error, and callbacks get their parameter types for free from context (contextual typing).

## 🔴 यह क्यों बना? (Hindi)
JavaScript में function का contract लिखने वाले के दिमाग में रहता है। Callers गलत संख्या या गलत क्रम में arguments देते हैं, भूल जाते हैं कि function Promise लौटाता है, या callback को अनपेक्षित values से call करते हैं। एक सामान्य Express + React app में callbacks हर जगह हैं: route handlers, `onClick`, Redux thunks, `array.map`। Function types हर contract को साफ़ और checked बनाते हैं: गलत arity (`Expected 2 arguments, but got 1`), गलत argument type या गलत return value compile error है, और callbacks को अपने parameter types context से मुफ़्त मिल जाते हैं (contextual typing)।

---

## 🟢 How it Works — Step by Step

Step 1 → Annotate parameters: `function add(a: number, b: number)`. Without annotation under `strict`, a parameter is an error (TS7006 "implicitly has an 'any' type") unless it gets a type from context.
Step 2 → The return type is **inferred** from the `return` statements. Annotate it explicitly on exported functions and public APIs so that a wrong return is reported inside the function, not at a distant caller.
Step 3 → A function type expression `(a: number) => string` is a type; assign any function with a compatible signature to it.
Step 4 → **Parameter count**: a function with FEWER parameters is assignable to a type with more (callers just ignore extras), but a function with MORE required parameters is not (TS2322 "Target signature provides too few arguments").
Step 5 → **Contextual typing**: in `[1,2].map((n) => n * 2)` the parameter `n` gets `number` from `map`'s signature, with no annotation needed.
Step 6 → **`void` in function types is special**: a function typed `() => void` may be assigned a function that returns something; the result is simply ignored. But a function DECLARED `function f(): void` may not `return 42` (TS2322).
Step 7 → **`never`** return type: for functions that always throw or never terminate (`function fail(msg: string): never`). **async** functions always return `Promise<T>`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Parameters annotate करो: `function add(a: number, b: number)`। `strict` में बिना annotation के parameter error है (TS7006 "implicitly has an 'any' type") जब तक context से type न मिल जाए।
Step 2 → Return type `return` statements से **infer** होता है। Exported functions और public APIs पर इसे explicitly लिखो ताकि गलत return function के अंदर ही पकड़ा जाए, दूर के caller पर नहीं।
Step 3 → Function type expression `(a: number) => string` एक type है; compatible signature वाला कोई भी function उसमें assign हो सकता है।
Step 4 → **Parameter count**: कम parameters वाला function ज़्यादा parameters वाले type में assignable है (callers extra को ignore करते हैं), पर ज़्यादा required parameters वाला नहीं (TS2322 "Target signature provides too few arguments")।
Step 5 → **Contextual typing**: `[1,2].map((n) => n * 2)` में `n` को `map` की signature से `number` मिल जाता है, annotation की ज़रूरत नहीं।
Step 6 → **Function types में `void` खास है**: `() => void` type में ऐसा function assign हो सकता है जो कुछ लौटाता हो; result बस ignore होता है। पर `function f(): void` declare करके `return 42` नहीं कर सकते (TS2322)।
Step 7 → **`never`** return type: उन functions के लिए जो हमेशा throw करते हैं या कभी खत्म नहीं होते (`function fail(msg: string): never`)। **async** functions हमेशा `Promise<T>` लौटाते हैं।

---

## 🟡 Real World Example
**Razorpay's payment SDK** accepts callbacks: `onSuccess(paymentId: string): void`, `onFailure(error: PaymentError): void`, and a `verifySignature(orderId, paymentId, signature): boolean` helper. In the Node backend, a `calculateGst(amount: number): number` and an async `capturePayment(id: string): Promise<Receipt>` are the real workhorses. Typing each function exactly means a developer who calls `capturePayment(id)` and forgets `await` sees `receipt.amount` flagged immediately ("Property 'amount' does not exist on type 'Promise<Receipt>'") instead of printing `undefined` in production.

## 🟡 Real Example Hindi mein
**Razorpay के payment SDK** में callbacks हैं: `onSuccess(paymentId: string): void`, `onFailure(error: PaymentError): void`, और helper `verifySignature(orderId, paymentId, signature): boolean`। Node backend में `calculateGst(amount: number): number` और async `capturePayment(id: string): Promise<Receipt>` असली काम करते हैं। हर function को सटीक type करने का मतलब है कि जो developer `capturePayment(id)` call करके `await` भूल जाए उसे `receipt.amount` पर तुरंत error दिखता है ("Property 'amount' does not exist on type 'Promise<Receipt>'"), production में `undefined` print होने की जगह।

---

## 💻 Code Example — Basic

```typescript
// function-types-basic.ts  (TypeScript 5.x, strict)

// 1. Declaration with annotated parameters and an explicit return type
function calculateGst(amount: number, ratePercent: number): number {
  return amount * (ratePercent / 100);               // returns a number, checked against the annotation
}

// 2. Function type expression as an alias
type PriceFn = (amount: number, ratePercent: number) => number;
const gst: PriceFn = calculateGst;                   // compatible signature: ok
const flatFee: PriceFn = (amount) => amount + 10;    // fewer params is fine; types come from PriceFn

// 3. void: caller does not use the result
function logOrder(id: number): void {
  console.log(`order ${id}`);                        // no return statement needed
}

// 4. void in a callback TYPE ignores the return value
type OnDone = () => void;
const onDone: OnDone = () => 42;                     // allowed: the number is ignored
const result = onDone();                             // type is void (not number!), yet at runtime it is 42

// 5. never: function that cannot return normally
function fail(message: string): never {
  throw new Error(message);                          // always throws
}

// 6. Contextual typing: no annotations on the callback parameters
const totals = [100, 250, 75].map((amount) => gst(amount, 18)); // amount is number
const rounded = totals.map((t) => Math.round(t));    // t is number

// 7. Default result typing: inferred return type is string
const label = (id: number) => `ORD-${id}`;           // return type inferred as string

logOrder(1);
console.log(gst(200, 18), flatFee(100, 0), result, rounded, label(7));
try { fail('boom'); } catch (e) { console.log((e as Error).message); }
```

Run with `npx tsx function-types-basic.ts`. Real output:
```
order 1
36 110 42 [ 18, 45, 14 ] ORD-7
boom
```

## 💻 Code Example — Advanced

```typescript
// function-types-advanced.ts  (TypeScript 5.x)

// 1. Call signature + properties (a function that also has fields)
interface Counter {
  (step?: number): number;       // callable
  reset(): void;                 // method on the function object
  count: number;                 // property
}
function makeCounter(): Counter {
  const fn = ((step = 1) => (fn.count += step)) as Counter;  // assertion: build the callable, then attach members
  fn.count = 0;
  fn.reset = () => { fn.count = 0; };
  return fn;
}

// 2. Constructor signature
interface Ctor<T> { new (id: number): T }
class Order { constructor(public id: number) {} }
function build<T>(C: Ctor<T>, id: number): T { return new C(id); } // generic factory

// 3. Higher-order function with generics: preserves argument and return types
function withLogging<A extends unknown[], R>(fn: (...args: A) => R): (...args: A) => R {
  return (...args) => {
    console.log('call', args);          // log the arguments
    return fn(...args);                 // forward and keep the original return type
  };
}
const loggedAdd = withLogging((a: number, b: number) => a + b);  // (a: number, b: number) => number

// 4. Async function: the return type is always a Promise
async function fetchTotal(id: number): Promise<number> {
  return id * 100;                      // returns number, becomes Promise<number>
}

// 5. Callback with a typed error-first signature (Node style)
type NodeCb<T> = (err: Error | null, data?: T) => void;
function readConfig(cb: NodeCb<{ port: number }>): void {
  cb(null, { port: 3000 });
}

// 6. Utility types derive from function types
type AddArgs = Parameters<typeof loggedAdd>;      // [a: number, b: number]
type AddResult = ReturnType<typeof loggedAdd>;    // number

// 7. Function type with a generic parameter
type Mapper = <T, U>(items: T[], fn: (x: T) => U) => U[];
const mapAll: Mapper = (items, fn) => items.map(fn);

async function main() {
  const c = makeCounter();
  c(); c(5);
  console.log(c.count);                           // 6
  c.reset();
  console.log(c.count, build(Order, 9).id);
  console.log(loggedAdd(2, 3));
  console.log(await fetchTotal(4));
  readConfig((err, data) => console.log(err, data?.port));
  const args: AddArgs = [1, 2];
  const r: AddResult = loggedAdd(...args);
  console.log(r, mapAll(['a', 'bb'], (s) => s.length));
}
main();
```

Run with `npx tsx function-types-advanced.ts`. Real output:
```
6
0 9
call [ 2, 3 ]
5
400
null 3000
call [ 1, 2 ]
3 [ 1, 2 ]
```

---

## 🟠 Node/Express + React Integration

```tsx
// server.ts  (Express): handler types come from Express, you rarely write them by hand
import express, { type RequestHandler, type NextFunction, type Request, type Response } from 'express';
const app = express();

// A named handler typed with the RequestHandler function type
const getHealth: RequestHandler = (_req, res) => {  // params typed by contextual typing
  res.json({ ok: true });                           // return type is void
};
app.get('/health', getHealth);

// Middleware: (req, res, next) => void. The explicit signature documents the contract
function requireAuth(req: Request, res: Response, next: NextFunction): void {
  if (!req.headers.authorization) {
    res.status(401).json({ error: 'unauthorized' });
    return;                                          // return nothing, void
  }
  next();                                            // continue the chain
}
app.use(requireAuth);

// Async handler wrapper: generic function type that forwards rejections to Express
type AsyncHandler = (req: Request, res: Response) => Promise<void>;
const wrap = (fn: AsyncHandler): RequestHandler => (req, res, next) => {
  fn(req, res).catch(next);                          // express 4 does not catch async errors itself
};
app.get('/orders', wrap(async (_req, res) => { res.json([]); }));

// React: callback props are function types
interface CartProps {
  onAdd: (sku: string, qty: number) => void;         // called by a button
  format?: (rupees: number) => string;               // optional callback with a default
}
export function Cart({ onAdd, format = (n) => `Rs ${n}` }: CartProps) {
  return <button onClick={() => onAdd('PIZZA', 1)}>{format(299)}</button>;
}

// Redux Toolkit thunk: a function returning a function, both typed
import { createAsyncThunk } from '@reduxjs/toolkit';
export const loadOrder = createAsyncThunk('orders/load', async (id: number): Promise<{ id: number }> => {
  return { id };                                     // return type flows into the fulfilled action payload
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Wrong number of arguments
```typescript
function s(a: number, b: number): number { return a + b; }
// ❌ Wrong: too few arguments
s(1);
// error TS2554: Expected 2 arguments, but got 1.
// ❌ Wrong: too many arguments
s(1, 2, 3);
// error TS2554: Expected 2 arguments, but got 3.
```
✅ Correct: pass exactly what the signature declares, or make a parameter optional or defaulted (topic 22).

❌ Mistake 2: Returning the wrong type, or forgetting to return
```typescript
type Fn = (a: number, b: number) => number;
// ❌ Wrong: returns string
const add3: Fn = (a, b) => 'x';
// error TS2322: Type 'string' is not assignable to type 'number'.
// ❌ Wrong: no return statement
function r(): string { }
// error TS2355: A function whose declared type is neither 'undefined', 'void', nor 'any' must return a value.
// ❌ Wrong: declared void, returns a value
function g(): void { return 42; }
// error TS2322: Type 'number' is not assignable to type 'void'.
```

❌ Mistake 3: Callback with MORE required parameters than the type provides
```typescript
type Fn = (a: number, b: number) => number;
// ❌ Wrong: the caller supplies only two arguments, but this needs three
const add2: Fn = (a: number, b: number, c: number) => a;
// error TS2322: Type '(a: number, b: number, c: number) => number' is not assignable to type 'Fn'.
//   Target signature provides too few arguments. Expected 3 or more, but got 2.
```
✅ Correct: remove the extra parameter or make it optional.

❌ Mistake 4: Trusting a `void` result. `const x = cb()` where `cb: () => void` gives `x: void`; `const n: number = x` fails with `error TS2322: Type 'void' is not assignable to type 'number'.` Do not rely on the value of a callback typed to return `void`.

---

## 🧠 Tricky Interview Question

```typescript
const nums = [1, 2, 3];
const out: void[] = nums.map((n) => console.log(n));  // (1)
function f(cb: () => void) { return cb(); }
const r = f(() => 'hello');                           // (2) type of r?
console.log(r);                                       // (3) printed value?
```
Answer: (1) compiles: `console.log` returns `void`, so `map` returns `void[]`. (2) `r` has type `void`, even though the callback really returned a string, because a `() => void` function type accepts any return value and TypeScript treats the result as unusable. (3) At runtime it prints `hello`: `void` is a compile-time promise only; the string is returned unchanged. That is the exact reason `void` callbacks (like `array.forEach`) can be given functions that return values (for example `arr.forEach(x => set.add(x))`, where `add` returns the Set).

---

## ⚫ Interview Questions + Answers

Q1: `void` vs `undefined` vs `never` as a return type?
A1: `void` means "the caller must not use the result" (it is assignable from any function return when used in a function TYPE). `undefined` is a real value, so a function typed `(): undefined` must return `undefined` explicitly. `never` means the function never returns normally (throws or loops forever), so code after the call is unreachable, and it is the bottom type used for exhaustiveness checks.

Q2: Should you annotate return types or let TypeScript infer them?
A2: Infer for small local helpers and callbacks. Annotate for exported functions, public APIs, and anything recursive or complex. An explicit return type documents the contract, speeds up compilation, and reports a wrong `return` inside the function itself. ESLint's `explicit-module-boundary-types` enforces this at module boundaries.

Q3: Why can a function with fewer parameters be assigned to a type with more?
A3: Because callers pass all arguments and the receiving function simply ignores the extras (`[1,2,3].forEach(x => ...)` ignores index and array). The reverse (more required parameters) is unsafe because the caller would not provide them, hence TS2322 "Target signature provides too few arguments".

Q4: What is contextual typing?
A4: When a function expression is assigned to a place with a known function type (an argument position, a typed variable, an object property with a declared type), its parameters take types from that context. That is why `(req, res) => {}` in `app.get('/x', ...)` needs no annotations, and why a callback assigned to an `any`-typed or untyped location triggers TS7006.

Q5: How do you type a function that also has properties, or a constructor?
A5: Use an object type or interface with a call signature (`{ (x: number): string; cache: Map<...> }`) and a construct signature (`{ new (id: number): T }`). Utility types `Parameters<F>`, `ReturnType<F>`, `ConstructorParameters<C>` and `InstanceType<C>` extract the pieces.

---

## 🔷 When to Use + When Not to Use
✅ Use explicit annotations for:
- Parameters (always), exported function return types, callback props in React, Redux thunk arguments
- Function type aliases for reused callbacks (`type Handler = (req: Req) => Promise<void>`)
- `never` for helpers like `assertUnreachable(x: never): never` and `fail()`

❌ Avoid:
- Annotating every local callback's parameters when contextual typing already provides them
- Using the broad `Function` type; it accepts any function and loses arity and return information (use `(...args: never[]) => unknown` or a precise signature)
- Declaring `: void` and then returning values by habit

---

## 📊 Visual Diagram
```
  (amount: number, rate: number) => number
   └──────── parameters ───────┘    └ return type

  type Fn = (a: number) => string      function type expression
  { (a: number): string; label: string }   call signature + property
  { new (id: number): Order }              construct signature

  void  : result ignored   (can hold any returned value at runtime)
  never : never returns    (throw / infinite loop)  ──► code after is unreachable
  async : always Promise<T>

  fewer params  ──► assignable ✔        more required params ──► TS2322 ✘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Function type expression | `(x: A) => B` | Function का type लिखने का तरीका |
| Call signature | Callable inside an object type | Object type में callable |
| Contextual typing | Types flow from the context | Context से types मिलना |
| `void` | Return value is unused | Return value इस्तेमाल नहीं होती |
| `never` | Function never returns | Function कभी नहीं लौटता |
| Arity | Number of parameters | Parameters की संख्या |
| Higher-order function | Takes or returns a function | Function लेने/लौटाने वाला function |

---

## ⚡ 3-Line Summary
English:
1. Annotate parameters always; annotate return types on exported functions; let contextual typing handle callbacks.
2. `void` ignores the result, `never` never returns, async functions return `Promise<T>`; fewer parameters are assignable, more are not.
3. Use call signatures for callable objects, and `Parameters`/`ReturnType` to derive types instead of duplicating them.

Hindi:
1. Parameters हमेशा annotate करो; exported functions पर return type लिखो; callbacks के लिए contextual typing पर भरोसा करो।
2. `void` result ignore करता है, `never` कभी नहीं लौटता, async functions `Promise<T>` लौटाते हैं; कम parameters assignable हैं, ज़्यादा नहीं।
3. Callable objects के लिए call signatures और types दोहराने की जगह `Parameters`/`ReturnType` इस्तेमाल करो।

---

## ➡️ Next Topic
**22. Optional, Default and Rest Parameters** — `?`, default values, `...args` and how they change a function's signature.
