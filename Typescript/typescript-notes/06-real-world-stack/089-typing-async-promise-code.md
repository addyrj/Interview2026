# 89. Typing async/Promise Code
# हिंदी में: async/Promise Code को Type करना

> Verified with **TypeScript 5.9 (5.x)**, `tsc --strict --target ES2022`. `Awaited` = TS 4.5+, `satisfies` = TS 4.9+.

---

## 🔵 Simple Definition (English)
Every `async` function in TypeScript **always returns `Promise<T>`**, where `T` is the type of the value you `return`. Typing async code means: annotate the *resolved* type (`Promise<Order>`), let `await` unwrap it (`Awaited<T>`), and type combinators like `Promise.all`, `Promise.allSettled` and `Promise.race` so each result keeps its own type.

## 🔵 सरल परिभाषा (Hindi)
TypeScript में हर `async` function **हमेशा `Promise<T>` return करता है**, जहाँ `T` वो type है जो आप `return` करते हो। Async code को type करने का मतलब: *resolved* type annotate करो (`Promise<Order>`), `await` को unwrap करने दो (`Awaited<T>`), और `Promise.all`, `Promise.allSettled`, `Promise.race` जैसे combinators के हर result का अपना type सुरक्षित रखो।

---

## 🔴 Problem it Solves
In plain JavaScript you cannot tell what a function returns: a value or a promise? Forgetting one `await` gives you a `Promise` object where you expected data, and you only discover it at runtime (`[object Promise]` in the UI, `undefined.total` in a payment flow). Errors in `catch` are untyped, `Promise.all` loses per-slot types, and callbacks-to-promise wrappers (`new Promise`) hide the resolved type. TypeScript makes the **missing `await` a compile error**.

## 🔴 यह क्यों बना? (Hindi)
Plain JavaScript में पता नहीं चलता कि function value दे रहा है या promise। एक `await` भूल गए तो data की जगह `Promise` object मिलता है और गलती सिर्फ runtime पर दिखती है (UI में `[object Promise]`, payment flow में `undefined.total`)। `catch` का error untyped होता है, `Promise.all` हर slot का type खो देता है, और `new Promise` wrappers resolved type छुपा देते हैं। TypeScript **भूले हुए `await` को compile error** बना देता है।

---

## 🟢 How it Works — Step by Step
Step 1 → `async function f(): Promise<T>` — the annotation is `Promise<T>`, never bare `T`.
Step 2 → Inside, `return value` must be assignable to `T` (TS wraps it for you).
Step 3 → `await expr` has type `Awaited<typeof expr>` — nested promises are flattened recursively.
Step 4 → `Promise.all([a, b])` takes a tuple and returns `Promise<[A, B]>` — positions are preserved.
Step 5 → `Promise.allSettled` returns a **discriminated union** (`status: "fulfilled" | "rejected"`) — narrow before reading `.value`.
Step 6 → `catch (e)` is `unknown` under `strict` (`useUnknownInCatchVariables`) — narrow with `instanceof Error`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `async function f(): Promise<T>` — annotation हमेशा `Promise<T>` होता है, सिर्फ `T` नहीं।
Step 2 → अंदर `return value` का type `T` में fit होना चाहिए (wrapping TS खुद करता है)।
Step 3 → `await expr` का type `Awaited<typeof expr>` होता है — nested promises recursively flatten होते हैं।
Step 4 → `Promise.all([a, b])` tuple लेता है और `Promise<[A, B]>` देता है — positions सुरक्षित रहती हैं।
Step 5 → `Promise.allSettled` एक **discriminated union** देता है (`status: "fulfilled" | "rejected"`) — `.value` पढ़ने से पहले narrow करो।
Step 6 → `strict` में `catch (e)` का type `unknown` है — `instanceof Error` से narrow करो।

---

## 🟡 Real World Example
**Swiggy order screen** loads the order, the delivery partner and the restaurant at the same time. The three calls return different shapes. With `Promise.all` typed as a tuple, `const [order, rider, restaurant] = await Promise.all([...])` gives each variable its own correct type, and if the "rider" call fails but the rest succeed, `allSettled` lets the screen still render with a fallback.

## 🟡 Real Example Hindi mein
**Swiggy order screen** एक साथ order, delivery partner और restaurant load करती है। तीनों calls के shapes अलग हैं। `Promise.all` को tuple की तरह type करने से `const [order, rider, restaurant] = await Promise.all([...])` में हर variable का सही type मिलता है। अगर "rider" call fail हो पर बाकी चलें, तो `allSettled` से screen fallback के साथ फिर भी render हो सकती है।

---

## 💻 Code Example — Basic

```typescript
// async-basic.ts — compiles with: tsc --noEmit --strict
interface Order { id: number; total: number; status: "PLACED" | "PAID" } // shape of an order

// A fake API call: returns a Promise that resolves to an Order after 10 ms
function fetchOrder(id: number): Promise<Order> {
  // new Promise<Order> tells TS what resolve() must be called with
  return new Promise<Order>((resolve) => {
    setTimeout(() => resolve({ id, total: 499, status: "PLACED" }), 10); // resolve with an Order
  });
}

// async function: return annotation is Promise<number>, NOT number
async function getOrderTotal(id: number): Promise<number> {
  const order = await fetchOrder(id); // await unwraps Promise<Order> -> Order
  return order.total;                 // returning number; TS wraps it in Promise<number>
}

// Awaited<T> extracts the resolved type from a promise-returning function
type TotalType = Awaited<ReturnType<typeof getOrderTotal>>; // = number

async function main(): Promise<void> {
  const total: TotalType = await getOrderTotal(7); // total is number
  console.log("Total:", total);                    // prints the number
}

main(); // fire the demo
// Output (run with npx tsx): Total: 499
```

## 💻 Code Example — Advanced

```typescript
// async-advanced.ts — parallel calls, allSettled, typed catch, timeout, retry
interface Order { id: number; total: number }       // order shape
interface Rider { name: string; phone: string }     // rider shape
interface Restaurant { name: string; rating: number } // restaurant shape

// Three independent API stubs with different return types
const getOrder = async (id: number): Promise<Order> => ({ id, total: 350 });
const getRider = async (_id: number): Promise<Rider> => { throw new Error("rider service down"); };
const getRestaurant = async (_id: number): Promise<Restaurant> => ({ name: "Biryani House", rating: 4.4 });

// 1) Promise.all keeps a TUPLE type: [Order, Restaurant]
async function loadBasic(id: number) {
  const [order, restaurant] = await Promise.all([getOrder(id), getRestaurant(id)]); // each typed separately
  return `${order.total} from ${restaurant.name}`; // order is Order, restaurant is Restaurant
}

// 2) allSettled returns a discriminated union per slot - narrow by status
async function loadTolerant(id: number) {
  const [o, r] = await Promise.allSettled([getOrder(id), getRider(id)]); // PromiseSettledResult<...>[]
  const order = o.status === "fulfilled" ? o.value : null;               // narrowed: o.value is Order
  const rider = r.status === "fulfilled" ? r.value : null;               // narrowed: r.value is Rider
  const reason = r.status === "rejected" ? String(r.reason) : "";        // reason is `any` -> convert safely
  return { order, rider, reason };                                       // rider is Rider | null
}

// 3) Generic timeout helper: T flows through, so the caller keeps the type
function withTimeout<T>(p: Promise<T>, ms: number): Promise<T> {
  const timer = new Promise<never>((_, reject) =>            // never: this promise never resolves a value
    setTimeout(() => reject(new Error(`timeout ${ms}ms`)), ms)); // rejects after ms
  return Promise.race([p, timer]);                            // race of T and never = T
}

// 4) Generic retry: works for ANY async fn, returns the same T
async function retry<T>(fn: () => Promise<T>, times: number): Promise<T> {
  let lastError: unknown;                                    // catch gives unknown, so store as unknown
  for (let i = 0; i < times; i++) {                          // try up to `times`
    try { return await fn(); }                               // success -> return T
    catch (e) { lastError = e; }                             // failure -> remember and loop
  }
  throw lastError instanceof Error ? lastError : new Error("retry failed"); // narrow unknown
}

async function main(): Promise<void> {
  console.log(await loadBasic(1));            // uses tuple destructuring
  const t = await loadTolerant(1);            // rider fails, order succeeds
  console.log(t.order?.total, t.rider, t.reason);
  const o = await withTimeout(getOrder(2), 100); // o is Order (T preserved)
  console.log(o.id);
  console.log(await retry(() => getRestaurant(3), 3)); // returns Restaurant
}
main();
// Output (npx tsx):
// 350 from Biryani House
// 350 null Error: rider service down
// 2
// { name: 'Biryani House', rating: 4.4 }
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: async handlers and the Promise<void> contract
import express, { type Request, type Response, type NextFunction, type RequestHandler } from "express";

interface Payment { id: string; amount: number } // Razorpay-style payment record
const findPayment = async (id: string): Promise<Payment | null> => // pretend DB call
  id === "p1" ? { id, amount: 1200 } : null;

// Wrapper so async errors reach Express error middleware (Express 4 does not catch rejections)
const asyncHandler =
  (fn: (req: Request, res: Response, next: NextFunction) => Promise<unknown>): RequestHandler =>
  (req, res, next) => { fn(req, res, next).catch(next); }; // forward rejection to next(err)

const app = express(); // create the app
app.get("/payments/:id", asyncHandler(async (req, res) => {
  const p = await findPayment(String(req.params.id)); // p: Payment | null
  if (!p) { res.status(404).json({ error: "not found" }); return; } // narrow out null
  res.json(p);                                        // p is Payment here
}));
```

```tsx
// React: typed async data loading with a discriminated union state
import { useEffect, useState } from "react";

interface Order { id: number; total: number } // order shape

// Each state carries only the data valid for it
type Load<T> =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ok"; data: T };

async function fetchOrders(): Promise<Order[]> { return [{ id: 1, total: 250 }]; } // stub

export function Orders() {
  const [state, setState] = useState<Load<Order[]>>({ status: "loading" }); // start loading
  useEffect(() => {
    let alive = true; // guard against setState after unmount
    fetchOrders()
      .then((data) => { if (alive) setState({ status: "ok", data }); })               // data: Order[]
      .catch((e: unknown) => {                                                         // e is unknown
        if (alive) setState({ status: "error", message: e instanceof Error ? e.message : "failed" });
      });
    return () => { alive = false; }; // cleanup
  }, []);
  if (state.status === "loading") return <p>Loading...</p>;      // narrowed
  if (state.status === "error") return <p>{state.message}</p>;   // message exists only here
  return <ul>{state.data.map((o) => <li key={o.id}>{o.total}</li>)}</ul>; // data exists only here
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Annotating an async function with the bare type
```typescript
// ❌ WRONG
interface Order { id: number; total: number }
declare function fetchOrder(id: number): Promise<Order>;
async function bad(): Order { return fetchOrder(1); }
// error TS1064: The return type of an async function or method must be the global
// Promise<T> type. Did you mean to write 'Promise<Order>'?
```
```typescript
// ✅ RIGHT
interface Order { id: number; total: number }
declare function fetchOrder(id: number): Promise<Order>;
async function good(): Promise<Order> { return fetchOrder(1); } // Promise<Order>
```

❌ Mistake 2: Forgetting `await`
```typescript
// ❌ WRONG
interface Order { id: number; total: number }
declare function fetchOrder(id: number): Promise<Order>;
async function main() {
  const o: Order = fetchOrder(1);
  // error TS2739: Type 'Promise<Order>' is missing the following properties from type 'Order': id, total
}
```
✅ Correct: `const o: Order = await fetchOrder(1);`

❌ Mistake 3: Reading `.value` from `allSettled` without narrowing
```typescript
// ❌ WRONG
interface Order { id: number }
declare function fetchOrder(id: number): Promise<Order>;
async function main() {
  const r = await Promise.allSettled([fetchOrder(1)]);
  console.log(r[0].value);
  // error TS2339: Property 'value' does not exist on type 'PromiseSettledResult<Order>'.
  //   Property 'value' does not exist on type 'PromiseRejectedResult'.
}
```
✅ Correct: `if (r[0].status === "fulfilled") console.log(r[0].value);`

❌ Mistake 4: Mixing types in `Promise.all` and assuming one type
```typescript
// ❌ WRONG
interface Order { id: number }
declare function fetchOrder(id: number): Promise<Order>;
async function main() {
  const [a, b] = await Promise.all([fetchOrder(1), Promise.resolve("x")]);
  const n: number = b;
  // error TS2322: Type 'string' is not assignable to type 'number'.
}
```
✅ Correct: tuple positions are preserved, so `b` is `string`; use it as a string.

---

## 🧠 Tricky Interview Question

```typescript
// What is the type of `x`, and does `await` add another Promise layer?
async function f() { return Promise.resolve(Promise.resolve(5)); }
type R = ReturnType<typeof f>;      // ?
type X = Awaited<R>;                // ?
const x: X = 5;
export {};
```
**Answer:** `R` is `Promise<number>` (not `Promise<Promise<number>>`) because a promise returned from an `async` function is flattened, and `Awaited<R>` is `number`. `Awaited<T>` (TS 4.5) recursively unwraps thenables, which is exactly the runtime behaviour of `await`. A common follow-up: `Promise.all` on a tuple uses `Awaited` for each slot.

---

## ⚫ Interview Questions + Answers

Q1: Why must an async function be typed `Promise<T>` and not `T`?
A1: Because the function returns immediately with a promise object; the value arrives later. The compiler enforces this with TS1064. Inside the body you `return T`, outside the caller sees `Promise<T>`.

Q2: What does `Awaited<T>` do and why was it added?
A2: It recursively unwraps `Promise`-like types (`Awaited<Promise<Promise<number>>>` = `number`). It makes `await` and `Promise.all` typings precise and is the standard way to get "the resolved type of an async function": `Awaited<ReturnType<typeof fn>>`.

Q3: `Promise.all` vs `Promise.allSettled` for typing?
A3: `all` returns a tuple of resolved values and rejects on the first failure. `allSettled` never rejects and returns `PromiseSettledResult<T>[]`, a discriminated union on `status`, so you must narrow before using `.value` or `.reason`.

Q4: How do you type `catch (e)`?
A4: Under `strict` it is `unknown`. Narrow with `e instanceof Error` or a custom guard. Never annotate `catch (e: Error)` (not allowed); use `unknown` or `any` only.

Q5: How do you write a reusable `retry`/`timeout` helper without losing the type?
A5: Make it generic: `function retry<T>(fn: () => Promise<T>): Promise<T>`. `T` is inferred from the callback, so the caller gets the exact resolved type back.

---

## 🔷 When to Use + When Not to Use
✅ Use explicit `Promise<T>` annotations:
- On exported functions, service methods and API clients (documents the contract)
- When a function has multiple return paths (`Promise<Order | null>`)
- Generic helpers (`retry`, `withTimeout`, `batch`)

❌ Avoid:
- Annotating every tiny local callback; inference already gives `Promise<T>`
- `async` on functions that never `await` (adds a wrapper promise for nothing, and hides sync throws)
- `Promise<any>` (turns the safety off for everything downstream)

---

## 📊 Visual Diagram
```
async function getOrder(): Promise<Order>
        │ returns immediately
        ▼
   Promise<Order> ──await──► Order            (Awaited<Promise<Order>>)

Promise.all([ Promise<Order>, Promise<Rider> ])
        ▼
   Promise<[Order, Rider]>      tuple, order preserved

Promise.allSettled([...])
        ▼
   [ {status:"fulfilled", value:Order}
   | {status:"rejected",  reason:any} , ... ]  -> narrow on status
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Promise<T> | Value of type T available later | बाद में मिलने वाली T type की value |
| Awaited<T> | Resolved type after unwrapping promises | Promise unwrap के बाद का type |
| Tuple | Fixed-length typed array | fixed length typed array |
| allSettled | Waits for all, never rejects | सबका इंतज़ार, कभी reject नहीं |
| unknown (catch) | Safe type for caught errors | caught error का safe type |
| Thenable | Object with a `.then` method | `.then` वाला object |

---

## ⚡ 3-Line Summary
English:
1. `async` functions always return `Promise<T>`; annotate `Promise<T>`, never bare `T` (TS1064).
2. `Awaited<T>` unwraps promises; `Promise.all` keeps a typed tuple; `allSettled` needs narrowing on `status`.
3. `catch (e)` is `unknown` - narrow it; write generic helpers (`retry<T>`) so types flow through.

Hindi:
1. `async` function हमेशा `Promise<T>` देता है; `Promise<T>` लिखो, सिर्फ `T` नहीं (TS1064)।
2. `Awaited<T>` promise unwrap करता है; `Promise.all` typed tuple रखता है; `allSettled` में `status` पर narrow करना पड़ता है।
3. `catch (e)` `unknown` है - narrow करो; `retry<T>` जैसे generic helpers लिखो ताकि type बना रहे।

---

## ➡️ Next Topic
**90. TypeScript with React — Props, Children, Events** — typing component props, `children` and DOM events.
