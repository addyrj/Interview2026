# 56. Utility Types — ReturnType, Parameters, ConstructorParameters, InstanceType
# हिंदी में: Utility Types — ReturnType, Parameters, ConstructorParameters, InstanceType

> TypeScript 5.x (सारे code blocks `tsc --strict` के साथ TypeScript 5.9 पर verify किए गए हैं)

---

## 🔵 Simple Definition (English)
These four built-in utility types **extract type information out of functions and classes** instead of making you re-type it by hand:
- `ReturnType<F>` — the type a function returns.
- `Parameters<F>` — the parameter list of a function as a **tuple**.
- `ConstructorParameters<C>` — the constructor's parameter list of a class, as a tuple.
- `InstanceType<C>` — the type of the object you get from `new C(...)`.

All four are built with conditional types + `infer` (note 49). They give you a **single source of truth**: change the function and every derived type updates.

## 🔵 सरल परिभाषा (Hindi)
ये चार built-in utility types **functions और classes से type की जानकारी निकाल लेते हैं**, ताकि आपको उसे हाथ से दोबारा न लिखना पड़े:
- `ReturnType<F>` — function जो type return करता है।
- `Parameters<F>` — function के parameters की list, एक **tuple** के रूप में।
- `ConstructorParameters<C>` — class के constructor के parameters, tuple में।
- `InstanceType<C>` — `new C(...)` से जो object मिलता है उसका type।

चारों `infer` + conditional types से बने हैं। इनसे **single source of truth** मिलता है — function बदलो, तो उससे बने सारे types अपने-आप बदल जाते हैं।

---

## 🔴 Problem it Solves
In a big codebase you write a function like `getOrderSummary` and then need its return type in a Redux slice, a React prop, a test mock and an API response. If you copy the shape by hand into an `interface`, it **drifts** the moment someone adds a field to the function. Wrapping a function (logging, retry, debounce, middleware) also needs the *same parameter list*, and retyping it is error-prone. These utilities derive types from the real code so they cannot go out of sync.

## 🔴 यह क्यों बना? (Hindi)
बड़े codebase में आप `getOrderSummary` जैसा function लिखते हैं, और फिर उसका return type Redux slice, React prop, test mock और API response में चाहिए होता है। अगर shape को हाथ से `interface` में copy करें, तो function में field जुड़ते ही दोनों **अलग हो जाते हैं (drift)**। किसी function को wrap करना (logging, retry, debounce, middleware) हो तो वही parameter list दोबारा लिखनी पड़ती है — गलती की गुंजाइश। ये utilities असली code से type निकालती हैं, इसलिए कभी out-of-sync नहीं होतीं।

---

## 🟢 How it Works — Step by Step

Step 1 → Definition: `type ReturnType<T extends (...args: any) => any> = T extends (...args: any) => infer R ? R : any`.
Step 2 → You pass a **function type**, not a function value. For a value use `typeof fn` (note 32): `ReturnType<typeof fn>`.
Step 3 → TypeScript matches the function against the pattern and **infers** the slot (`R` for return, `P` for params).
Step 4 → `Parameters<F>` gives a tuple like `[orderId: string, qty: number]`. Labels are preserved and you can index it: `Parameters<F>[0]`.
Step 5 → For classes, `typeof ClassName` is the *constructor* type. `ConstructorParameters<typeof C>` and `InstanceType<typeof C>` work on that.
Step 6 → Combine with `Awaited` (note 57): `Awaited<ReturnType<typeof asyncFn>>` unwraps the `Promise`.
Step 7 → Overloaded functions: inference sees only the **last overload signature** (classic interview gotcha).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Definition: `ReturnType<T> = T extends (...args: any) => infer R ? R : any`।
Step 2 → आप **function का type** देते हो, function value नहीं। Value हो तो `typeof fn` लिखो: `ReturnType<typeof fn>`।
Step 3 → TypeScript function को pattern से match करके `R` (return) या `P` (params) **infer** करता है।
Step 4 → `Parameters<F>` एक tuple देता है जैसे `[orderId: string, qty: number]`। Labels बचे रहते हैं और `Parameters<F>[0]` से index कर सकते हो।
Step 5 → Class के लिए `typeof ClassName` असल में *constructor* का type है। `ConstructorParameters<typeof C>` और `InstanceType<typeof C>` उसी पर चलते हैं।
Step 6 → `Awaited` के साथ जोड़ो: `Awaited<ReturnType<typeof asyncFn>>` से `Promise` हट जाता है।
Step 7 → Overloaded function में inference सिर्फ़ **आख़िरी overload** देखता है (interview का classic gotcha)।

---

## 🟡 Real World Example
**Razorpay-style payment service**: a `createPaymentLink(orderId, amountPaise, options)` function lives in the backend. The React checkout page needs the exact link object it returns, and a `retry()` helper must accept the same arguments. Instead of writing `PaymentLink` and `CreateLinkArgs` interfaces separately, the team writes `type PaymentLink = Awaited<ReturnType<typeof createPaymentLink>>` and `type CreateLinkArgs = Parameters<typeof createPaymentLink>`. When product adds an `expiresAt` field, the frontend type, retry helper and test mocks all update instantly.

## 🟡 Real Example Hindi mein
**Razorpay जैसी payment service**: backend में `createPaymentLink(orderId, amountPaise, options)` function है। React checkout page को उसका return किया हुआ ठीक वही link object चाहिए, और `retry()` helper को वही arguments लेने हैं। `PaymentLink` और `CreateLinkArgs` interfaces अलग से लिखने की जगह team लिखती है `type PaymentLink = Awaited<ReturnType<typeof createPaymentLink>>` और `type CreateLinkArgs = Parameters<typeof createPaymentLink>`। जब product `expiresAt` field जोड़ता है, तो frontend type, retry helper और test mocks सब एक साथ update हो जाते हैं।

---

## 💻 Code Example — Basic

```typescript
// basic-utility-extract.ts — TypeScript 5.x, strict mode
// A normal function: Swiggy-style order total calculator
function calcOrderTotal(itemPrice: number, qty: number, couponPct: number) {
  // gross amount before discount
  const gross = itemPrice * qty;
  // discount amount from the coupon percentage
  const discount = (gross * couponPct) / 100;
  // return an object so the inferred return type is interesting
  return { gross, discount, payable: gross - discount };
}

// ReturnType needs a TYPE, so `typeof` turns the function VALUE into a type
type OrderTotal = ReturnType<typeof calcOrderTotal>; // { gross: number; discount: number; payable: number }

// Parameters gives a tuple of the argument types (labels are kept)
type TotalArgs = Parameters<typeof calcOrderTotal>; // [itemPrice: number, qty: number, couponPct: number]

// Index the tuple like an array type to get ONE parameter's type
type CouponType = TotalArgs[2]; // number

// A wrapper that spreads the tuple so its args stay identical to the original
function logged(...args: TotalArgs): OrderTotal {
  // call the original with the exact same arguments
  const result = calcOrderTotal(...args);
  // log the call for debugging
  console.log("calcOrderTotal", args, "->", result);
  // return the original result unchanged
  return result;
}

// use the derived coupon type
const coupon: CouponType = 10;
// call the wrapper: 2 items at Rs 200 with 10% off
logged(200, 2, coupon);
// Output (real, tsx): calcOrderTotal [ 200, 2, 10 ] -> { gross: 400, discount: 40, payable: 360 }
```

## 💻 Code Example — Advanced

```typescript
// advanced-utility-extract.ts — classes, async, generic wrappers (TS 5.x)

// A repository class like one that talks to SQL Server
class OrderRepo {
  // constructor takes a connection string and an optional pool size
  constructor(public readonly conn: string, public readonly poolSize: number = 10) {}
  // async method returning a Promise of rows
  async findByUser(userId: number): Promise<{ id: number; total: number }[]> {
    // fake data standing in for a real query result
    return [{ id: userId, total: 499 }];
  }
}

// ConstructorParameters works on `typeof Class` (the constructor function type)
type RepoCtorArgs = ConstructorParameters<typeof OrderRepo>; // [conn: string, poolSize?: number]
// InstanceType gives the type of `new OrderRepo(...)`
type RepoInstance = InstanceType<typeof OrderRepo>;
// Awaited + ReturnType: unwrap the Promise of a method found by indexed access
type Rows = Awaited<ReturnType<RepoInstance["findByUser"]>>;

// A typed factory: args and result are both derived from the class itself
function create<C extends new (...a: any[]) => any>(Ctor: C, ...args: ConstructorParameters<C>): InstanceType<C> {
  // construct and return; InstanceType<C> keeps the precise type for callers
  return new Ctor(...args);
}

// A retry helper that reuses the wrapped function's exact params and return type
async function withRetry<F extends (...a: any[]) => Promise<any>>(
  fn: F, times: number, ...args: Parameters<F>
): Promise<Awaited<ReturnType<F>>> {
  // remember the last failure to rethrow
  let last: unknown;
  // try up to `times` attempts
  for (let i = 0; i < times; i++) {
    try { return await fn(...args); } catch (e) { last = e; }
  }
  // all attempts failed
  throw last;
}

// repo is inferred as OrderRepo, and bad ctor args would be a compile error
const repo = create(OrderRepo, "Server=sql1;Db=orders", 20);
// a one-element tuple is valid because poolSize is optional
const args: RepoCtorArgs = ["x"];

async function main() {
  // args after `3` must be [userId: number] because of Parameters<F>
  const rows: Rows = await withRetry(repo.findByUser.bind(repo), 3, 7);
  // print rows, the tuple and the pool size
  console.log(rows, args, repo.poolSize);
}
main();
// Output (real, tsx): [ { id: 7, total: 499 } ] [ 'x' ] 20
```

---

## 🟠 Node/Express + React Integration

```typescript
// express-react-derive.ts — derive types from real code (no hand-written duplicates)
import express from "express";

// service function: the single source of truth for the API response
async function getCart(userId: string) {
  // pretend SQL Server result
  return { userId, items: [{ sku: "BIRYANI-1", qty: 2, price: 249 }], total: 498 };
}

// Express handler: Res type is DERIVED from the service, so route and client agree
type CartResponse = Awaited<ReturnType<typeof getCart>>;

// build the app
const app = express();
// GET /cart/:userId
app.get("/cart/:userId", async (req, res) => {
  // req.params.userId is string, which matches Parameters<typeof getCart>[0]
  const userId: Parameters<typeof getCart>[0] = req.params.userId;
  // await the service call
  const cart: CartResponse = await getCart(userId);
  // send JSON
  res.json(cart);
});

// ---- Redux side: RootState derived from the reducer, never written by hand ----
// a hand-written reducer function (same idea as RTK's rootReducer)
function cartReducer(state = { count: 0 }, action: { type: "add" }) {
  // add one item on "add"
  return action.type === "add" ? { count: state.count + 1 } : state;
}
// RootState = whatever the reducer returns
type CartState = ReturnType<typeof cartReducer>; // { count: number }
// a selector typed from the derived state
const selectCount = (s: CartState) => s.count;
// use it so the file is not "unused"
console.log(selectCount(cartReducer(undefined, { type: "add" })));
```

```tsx
// CartView.tsx — React props derived from a function's return type
import { useState } from "react";

// the data loader used by the component
function loadSummary(id: number) {
  // shape that the UI cares about
  return { id, label: "Order #" + id, paid: true };
}
// props type derived from the loader, not duplicated
type SummaryProps = { summary: ReturnType<typeof loadSummary> };

// presentational component
function Summary({ summary }: SummaryProps) {
  // render label and paid flag
  return <p>{summary.label} {summary.paid ? "PAID" : "DUE"}</p>;
}

// container component keeps the loader result in state
export function CartView() {
  // useState infers the same derived type
  const [s] = useState(() => loadSummary(42));
  // pass down
  return <Summary summary={s} />;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Passing the function VALUE instead of its type, wrong argument types, and using `InstanceType` on the class itself.
```typescript
// ❌ intentional errors — real tsc output is pasted below
function pay(orderId: string, amount: number) { return { orderId, amount }; }
// ❌ wrong: `pay` is a value, not a type
type R = ReturnType<pay>;
// error TS2749: 'pay' refers to a value, but is being used as a type here. Did you mean 'typeof pay'?

// ❌ wrong: the tuple says amount is number
const a: Parameters<typeof pay> = ["o1", "100"];
// error TS2322: Type 'string' is not assignable to type 'number'.

class C { constructor(public n: number) {} }
// ❌ wrong: `C` is the instance type; the constructor is `typeof C`
type I = InstanceType<C>;
// error TS2344: Type 'C' does not satisfy the constraint 'abstract new (...args: any) => any'.
//   Type 'C' provides no match for the signature 'new (...args: any): any'.

// ✅ right
type R2 = ReturnType<typeof pay>;
const a2: Parameters<typeof pay> = ["o1", 100];
type I2 = InstanceType<typeof C>;
```

❌ Mistake 2: Using `ReturnType` on an **overloaded** function and expecting a union.
```typescript
// ❌ intentional error — only the LAST overload is used
function f(a: string): string;
function f(a: number): number;
function f(a: string | number) { return a; }
// ReturnType sees only `(a: number): number`
type RF = ReturnType<typeof f>; // number, NOT string | number
// ❌ so this fails:
const x: RF = "s";
// error TS2322: Type 'string' is not assignable to type 'number'.
```

❌ Mistake 3 (no compiler error, silent bug): `ReturnType` of an `async` function is `Promise<T>`, not `T`. Always wrap with `Awaited<...>` when you want the resolved value.

---

## 🧠 Tricky Interview Question

```typescript
class Order { constructor(public id: number) {} }
type A = InstanceType<typeof Order>;
type B = typeof Order;
type C = Order;
// Which two are the same type? What is `typeof Order` exactly?
```
Answer: `A` and `C` are the same (`Order`, the instance shape). `B` is the **constructor function type** `typeof Order` (`new (id: number) => Order` plus static members). A class name in a *type* position means the instance; in a *value* position it means the constructor. This is why `InstanceType<Order>` fails and `InstanceType<typeof Order>` works.

---

## ⚫ Interview Questions + Answers

Q1: How is `ReturnType` implemented?
A1: `type ReturnType<T extends (...args: any) => any> = T extends (...args: any) => infer R ? R : any`. A conditional type with `infer R` captures whatever sits in the return position. `Parameters` does the same with `infer P` in the parameter position.

Q2: Why do we write `ReturnType<typeof fn>` and not `ReturnType<fn>`?
A2: `fn` is a value; type arguments need a type. `typeof fn` (type-position `typeof`) converts the value to its type. The error otherwise is TS2749.

Q3: How would you type a generic `debounce` that preserves the wrapped function's signature?
A3: `function debounce<F extends (...a: any[]) => void>(fn: F, ms: number): (...args: Parameters<F>) => void`. `Parameters<F>` keeps names and optional/rest params; callers get full autocomplete.

Q4: Get the resolved type of an `async` service function for the frontend.
A4: `type Res = Awaited<ReturnType<typeof svc>>`. `ReturnType` alone yields `Promise<X>`; `Awaited` (TS 4.5+) strips it, including nested promises.

Q5: What happens with overloads and generic functions?
A5: For overloads the **last** signature is used. For generic functions, type parameters are replaced by their constraints (`unknown` if none), so `ReturnType<typeof identity>` for `<T>(x: T) => T` gives `unknown`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A type should always match a real function/class (service to controller to client, reducer to `RootState`).
- Writing wrappers, HOFs, decorators, middleware that forward arguments.
- Mocking: `jest.fn<ReturnType<typeof f>, Parameters<typeof f>>()` style helpers.

❌ Avoid when:
- The function is overloaded or heavily generic (inference gives a lossy answer).
- A public API contract is better as an explicit `interface` (stable across refactors, readable in error messages).
- You only need it once; a named interface may be clearer for juniors.

---

## 📊 Visual Diagram
```
function  fn(a: string, b: number): Promise<User>
            │            │                 │
            │            │                 └── ReturnType<typeof fn>  = Promise<User>
            │            │                     Awaited<...>           = User
            └────────────┴──────────────────── Parameters<typeof fn>  = [a: string, b: number]

class Repo { constructor(url: string) {} }
   typeof Repo ──► ConstructorParameters<typeof Repo> = [url: string]
   typeof Repo ──► InstanceType<typeof Repo>          = Repo
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ReturnType | Function's return type | Function का return type |
| Parameters | Params as a tuple | Parameters की tuple |
| ConstructorParameters | Class ctor params as tuple | Class constructor के params |
| InstanceType | Type of `new C()` result | `new C()` से बने object का type |
| typeof (type position) | Value to its type | Value से उसका type निकालना |
| infer | Capture a type inside a conditional | Conditional type के अंदर type पकड़ना |
| Single source of truth | One real definition drives all types | एक असली definition, बाकी उससे derived |

---

## ⚡ 3-Line Summary
English:
1. These utilities pull return, parameter, constructor and instance types out of real code so types never drift.
2. Always pass `typeof fn` / `typeof Class`, and add `Awaited` for async functions.
3. Overloads give only the last signature; generics collapse to constraints.

Hindi:
1. ये utilities असली code से return, parameter, constructor और instance types निकालती हैं, इसलिए types drift नहीं होते।
2. हमेशा `typeof fn` / `typeof Class` दो, और async functions के लिए `Awaited` जोड़ो।
3. Overloads में सिर्फ़ आख़िरी signature मिलता है; generics अपनी constraint पर आ जाते हैं।

---

## ➡️ Next Topic
**57. Utility Types — Awaited, NoInfer, Uppercase/Lowercase** — unwrapping promises, blocking unwanted inference (TS 5.4+), and string-case helpers.
