# 42. Generic Functions
# हिंदी में: Generic Functions

> Verified with **TypeScript 5.x** (compiled with 5.9, `--strict`). `NoInfer<T>` is **TS 5.4+**; `<const T>` is **TS 5.0+**.

---

## 🔵 Simple Definition (English)
A **generic function** declares one or more **type parameters** that are filled in per call. The compiler **infers** them from the arguments, so the return type (and callbacks) are precisely typed for that call. Generic functions come in several syntaxes — function declarations, arrow functions, function-type aliases, and method signatures — and can have multiple parameters (`<K, V>`), defaults, and constraints.

## 🔵 सरल परिभाषा (Hindi)
**Generic function** एक या ज़्यादा **type parameters** declare करता है जो हर call पर भर जाते हैं। Compiler arguments से उन्हें **infer** करता है, इसलिए उस call के लिए return type (और callbacks) सटीक typed होते हैं। Generic functions कई syntax में आते हैं — function declarations, arrow functions, function-type aliases और method signatures — और इनमें कई parameters (`<K, V>`), defaults और constraints हो सकते हैं।

---

## 🔴 Problem it Solves
Utility functions — `groupBy`, `retry`, `pick`, `debounce`, `fetchJson` — must work on *any* data shape, yet callers want exact types back. A non-generic version either returns `any` (no safety) or requires copy-pasting for each model. A generic function infers `T` from the call and gives `groupBy(orders, o => o.status)` the exact result type `Record<string, Order[]>`.

## 🔴 यह क्यों बना? (Hindi)
Utility functions — `groupBy`, `retry`, `pick`, `debounce`, `fetchJson` — को *किसी भी* data shape पर चलना होता है, फिर भी callers को सटीक types चाहिए। Non-generic version या तो `any` लौटाता है (कोई safety नहीं) या हर model के लिए copy-paste माँगता है। Generic function call से `T` infer करता है और `groupBy(orders, o => o.status)` को सटीक result type `Record<string, Order[]>` देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Declare: `function f<T>(...)`, `const f = <T,>(...) =>`, or a type `type Fn = <T>(x: T) => T`.
Step 2 → TS collects **inference candidates** for `T` from every argument where `T` appears.
Step 3 → If there are several candidates, it picks the **best common type**; if they conflict (e.g. `string` and `number`) it reports an error.
Step 4 → Callback parameters are **contextually typed** *after* `T` is fixed from earlier arguments — so put the data argument before the callback.
Step 5 → Multiple parameters: each is independent — `<T, K extends keyof T>` can depend on earlier ones.
Step 6 → Use `NoInfer<T>` (TS 5.4) on a parameter you do **not** want to widen `T`, and `<const T>` (TS 5.0) to keep literal types.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Declare करो: `function f<T>(...)`, `const f = <T,>(...) =>`, या type `type Fn = <T>(x: T) => T`।
Step 2 → TS हर उस argument से `T` के **inference candidates** इकट्ठा करता है जहाँ `T` आता है।
Step 3 → कई candidates हों तो वह **best common type** चुनता है; आपस में टकराएँ (जैसे `string` और `number`) तो error देता है।
Step 4 → Callback parameters `T` तय होने के *बाद* **contextually typed** होते हैं — इसलिए data argument को callback से पहले रखो।
Step 5 → कई parameters: हर एक स्वतंत्र है — `<T, K extends keyof T>` पहले वाले पर निर्भर हो सकता है।
Step 6 → जिस parameter को `T` चौड़ा नहीं करने देना, उस पर `NoInfer<T>` (TS 5.4) और literal types बचाने के लिए `<const T>` (TS 5.0) लगाओ।

---

## 🟡 Real World Example
**Razorpay-style webhook retry helper**: `retry<T>(fn: () => Promise<T>, attempts: number): Promise<T>`. Wrap `fetchPaymentStatus(id)` and the result is `Promise<PaymentStatus>`; wrap `fetchInvoice(id)` and it is `Promise<Invoice>`. One helper, zero casts. Likewise `groupBy(orders, o => o.restaurantId)` powers the "orders per restaurant" dashboard.

## 🟡 Real Example Hindi mein
**Razorpay जैसा webhook retry helper**: `retry<T>(fn: () => Promise<T>, attempts: number): Promise<T>`। `fetchPaymentStatus(id)` को wrap करो तो result `Promise<PaymentStatus>` है; `fetchInvoice(id)` wrap करो तो `Promise<Invoice>`। एक helper, कोई cast नहीं। इसी तरह `groupBy(orders, o => o.restaurantId)` "restaurant के हिसाब से orders" dashboard चलाता है।

---

## 💻 Code Example — Basic

```typescript
// Declaration style, TWO type parameters: one for key, one for value
function toPair<K, V>(key: K, value: V): [K, V] {
  return [key, value];                          // tuple typed per call
}

const p1 = toPair("table", 7);                  // [string, number]
const p2 = toPair(true, { id: "o1" });          // [boolean, { id: string }]
console.log(p1, p2[1].id);
// Output:
// [ 'table', 7 ] o1
```

```typescript
// Arrow function style (in a .ts file)
const wrapArray = <T>(x: T): T[] => [x];         // T inferred per call
const nums = wrapArray(5);                       // number[]
const strs = wrapArray("a");                     // string[]

// Generic function TYPE (alias): the type parameter belongs to the call, not the alias
type Mapper = <T, U>(items: T[], fn: (x: T) => U) => U[];
const map: Mapper = (items, fn) => items.map(fn); // implementation gets contextual types

console.log(nums, strs, map([1, 2, 3], (n) => n * 2));
// Output:
// [ 5 ] [ 'a' ] [ 2, 4, 6 ]
```

## 💻 Code Example — Advanced

```typescript
// groupBy: T = item type, K = key type (constrained to valid object keys)
function groupBy<T, K extends PropertyKey>(items: T[], keyFn: (item: T) => K): Record<K, T[]> {
  const out = {} as Record<K, T[]>;              // build result (assertion on empty object)
  for (const item of items) {
    const k = keyFn(item);                        // key for this item
    (out[k] ??= []).push(item);                   // create bucket then push
  }
  return out;
}

interface Order { id: string; status: "paid" | "pending"; total: number }
const orders: Order[] = [
  { id: "o1", status: "paid", total: 300 },
  { id: "o2", status: "pending", total: 120 },
  { id: "o3", status: "paid", total: 80 },
];

// K inferred as "paid" | "pending" -> result keys are exact
const byStatus = groupBy(orders, (o) => o.status);
console.log(byStatus.paid.length, byStatus.pending.map((o) => o.id));
// Output:
// 2 [ 'o2' ]
```

```typescript
// retry<T>: wraps any async function and returns the SAME result type
async function retry<T>(fn: () => Promise<T>, attempts: number): Promise<T> {
  let lastError: unknown;                         // keep the last failure
  for (let i = 1; i <= attempts; i++) {
    try {
      return await fn();                          // success => result is T
    } catch (e) {
      lastError = e;                              // remember and loop
    }
  }
  throw lastError;                                // all attempts failed
}

let calls = 0;
const flaky = async () => {                       // fails twice, then succeeds
  calls++;
  if (calls < 3) throw new Error("gateway timeout");
  return { status: "captured" as const, amount: 499 };
};

retry(flaky, 5).then((r) => console.log(r.status, r.amount, "after", calls, "calls"));
// Output:
// captured 499 after 3 calls
```

```typescript
// NoInfer (TS 5.4+): stop a parameter from widening T
function createFsm<S extends string>(states: S[], initial: NoInfer<S>): S {
  return initial;                                  // initial must be one of `states`
}
const start = createFsm(["idle", "paying", "paid"], "idle"); // ok, S = "idle" | "paying" | "paid"
console.log(start);
// Output:
// idle
```

```typescript
// <const T> (TS 5.0+): keep literal and readonly tuple types from arguments
function defineRoutes<const T extends readonly string[]>(paths: T): T {
  return paths;                                    // exact literal tuple returned
}
const routes = defineRoutes(["/orders", "/pay"]);   // readonly ["/orders", "/pay"], not string[]
type RoutePath = (typeof routes)[number];            // "/orders" | "/pay"
const ok: RoutePath = "/pay";                        // fine
console.log(ok, routes.length);
// Output:
// /pay 2
```

---

## 🟠 Node/Express + React Integration

```typescript
import express from "express";                      // Express runtime
import type { Request, Response, NextFunction, RequestHandler } from "express";

// Generic async wrapper: forwards rejected promises to Express error middleware.
// Keeps the handler's own Request/Response generics intact via type parameters.
function asyncHandler<P = unknown, ResBody = unknown, ReqBody = unknown>(
  fn: (req: Request<P, ResBody, ReqBody>, res: Response<ResBody>) => Promise<void>
): RequestHandler<P, ResBody, ReqBody> {
  return (req, res, next: NextFunction) => {        // returned handler
    fn(req, res).catch(next);                       // any rejection => next(err)
  };
}

const app = express();
app.post(
  "/pay",
  asyncHandler<unknown, { status: string }, { amount: number }>(async (req, res) => {
    const { amount } = req.body;                    // typed number
    res.json({ status: amount > 0 ? "ok" : "invalid" }); // body checked as { status: string }
  })
);
```

```tsx
import { useCallback, useState } from "react";       // React hooks

// Generic custom hook: one function, any payload type
function useAsync<T>(fn: () => Promise<T>) {
  const [data, setData] = useState<T | null>(null);   // T flows into state
  const run = useCallback(() => { fn().then(setData); }, [fn]); // setData accepts T
  return { data, run };                               // inferred return type
}

interface Restaurant { id: string; name: string }
export function RestaurantList() {
  const { data, run } = useAsync<Restaurant[]>(async () => [{ id: "r1", name: "Meghana" }]);
  return (
    <div>
      <button onClick={run}>Load</button>
      <ul>{data?.map((r) => <li key={r.id}>{r.name}</li>)}</ul>
    </div>
  );
}

// In .tsx files an arrow generic needs a trailing comma, else <T> parses as JSX
export const identity = <T,>(x: T): T => x;
```

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: Using members of `T` without a constraint, and conflicting inference candidates.**

```typescript
// ❌ T is unknown inside the body; also two args with different types for one T
function len<T>(x: T): number { return x.length; } // wrong
// error TS2339: Property 'length' does not exist on type 'T'.

function pair<T>(a: T, b: T): [T, T] { return [a, b]; }
pair("a", 1); // wrong: T cannot be both
// error TS2345: Argument of type 'number' is not assignable to parameter of type 'string'.
```

```typescript
// ✅ Constrain T, and use two type parameters when types may differ
function len<T extends { length: number }>(x: T): number { return x.length; }
function pair<A, B>(a: A, b: B): [A, B] { return [a, b]; }
console.log(len("abc"), pair("a", 1));
// Output:
// 3 [ 'a', 1 ]
```

**Mistake 2: Putting the callback before the data.** `fn(cb, items)` — TS cannot type `cb`'s parameter because `T` is not known yet. Order as `(items, cb)`.

**Mistake 3: A wrapper that loses `T` by returning `any`/`Promise<any>`.** `async function retry(fn: () => Promise<any>)` compiles but callers get `any`. Always thread `T` through return type.

**Mistake 4: Expecting inference to protect an "initial value" parameter.** Without `NoInfer`, `createFsm2(["idle","paying"], "done")` is *accepted* because `S` widens to include `"done"`. With `NoInfer<S>` it fails:

```typescript
// ❌ NoInfer stops "done" from widening S
function createFsm<S extends string>(states: S[], initial: NoInfer<S>): S { return initial; }
createFsm(["idle", "paying"], "done"); // wrong
// error TS2345: Argument of type '"done"' is not assignable to parameter of type '"idle" | "paying"'.
```

---

## 🧠 Tricky Interview Question

```typescript
function pick<T, K extends keyof T>(obj: T, key: K): T[K] { return obj[key]; }
const order = { id: "o1", total: 250, paid: true };
const x = pick(order, "total");
const y = pick(order, Math.random() > 2 ? "id" : "paid");
console.log(x, y);
// Output:
// 250 true
```
**Question:** What are the types of `x` and `y`?
**Answer:** `x: number` (since `K = "total"` and `T["total"]` is `number`). `y: string | boolean` — the key expression has type `"id" | "paid"`, so `K` is that union and `T[K]` distributes to `string | boolean`. Output is `250 true` because `Math.random() > 2` is always false, so the key is `"paid"`. The lesson: the return type is **computed from the key's type**, not from the runtime key.

---

## ⚫ Interview Questions + Answers

**Q1: How does TypeScript infer `T` when several arguments mention it?**
A1: It gathers a candidate from each argument and picks the best common supertype among them. If none of them is a supertype of the rest (e.g. `string` vs `number`) you get an error on the later argument (TS2345). Use two type parameters if the arguments may differ.

**Q2: Arrow generic in `.tsx` — why `<T,>`?**
A2: In TSX, `<T>` is parsed as the start of a JSX element. The trailing comma (or `<T extends unknown>`) makes the parser treat it as a type parameter list.

**Q3: What does `NoInfer<T>` do and when was it added?**
A3: TS 5.4 intrinsic type that blocks inference at a position, so `T` is inferred only from other positions. Use it for defaults/initial values (`createFsm(states, initial: NoInfer<S>)`).

**Q4: Generic function type vs generic type alias?**
A4: `type Fn = <T>(x: T) => T` — type parameter belongs to **each call** (the function stays generic). `type Fn<T> = (x: T) => T` — `T` is fixed when you *use* the alias (`Fn<number>`), and the function is not generic. Different semantics.

**Q5: How do you type a higher-order function like `debounce` without losing parameter types?**
A5: Use a tuple type parameter for the arguments: `function debounce<A extends unknown[], R>(fn: (...args: A) => R, ms: number): (...args: A) => void`. `A` captures the exact parameter list so the returned function has identical parameters.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Utilities/wrappers that must preserve input types (`retry`, `debounce`, `groupBy`, `asyncHandler`)
- Custom hooks returning data of caller-chosen shape (`useAsync<T>`, `useFetch<T>`)
- You want exact literal/union results (`K extends keyof T`)

❌ Avoid when:
- A concrete type is enough (`function total(items: Item[])`)
- `T` appears only once — use `unknown`
- Inference errors become unreadable; sometimes overloads or a union are clearer

---

## 📊 Visual Diagram
```
  groupBy(orders, o => o.status)
      │         │        │
      │         │        └─ K inferred = "paid" | "pending"   (from callback return)
      │         └─ T inferred = Order                          (from first arg)
      ▼
  Record<"paid" | "pending", Order[]>

  order of inference:   items (fixes T)  ─►  callback params typed  ─►  K from return
  conflict:             pair("a", 1) with <T,T>  ─► ERROR TS2345
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Type parameter | `T` in `<T>` | `<T>` वाला `T` |
| Inference candidate | A type found for `T` from an argument | Argument से मिला `T` का संभावित type |
| Contextual typing | Callback params typed from expected type | Expected type से callback params का type |
| NoInfer | TS 5.4 inference blocker | Inference रोकने वाला (TS 5.4) |
| const type parameter | `<const T>` keeps literals (TS 5.0) | Literals बचाने वाला (TS 5.0) |
| Higher-order function | Function taking/returning functions | Functions लेने/लौटाने वाला function |

---

## ⚡ 3-Line Summary
English:
1. A generic function infers type parameters per call so inputs, callbacks and return types stay linked and exact.
2. Put data before callbacks, use separate parameters for types that may differ, and constrain `T` (`extends`) to use its members.
3. `NoInfer` (5.4) and `<const T>` (5.0) fine-tune inference; in `.tsx` write `<T,>`.

Hindi:
1. Generic function हर call पर type parameters infer करता है ताकि inputs, callbacks और return types जुड़े और सटीक रहें।
2. Data को callback से पहले रखो, अलग हो सकने वाले types के लिए अलग parameters लो, और `T` के members इस्तेमाल करने के लिए `extends` constraint लगाओ।
3. `NoInfer` (5.4) और `<const T>` (5.0) inference को बारीकी से नियंत्रित करते हैं; `.tsx` में `<T,>` लिखो।

---

## ➡️ Next Topic
**43. Generic Constraints (extends)** — limiting what `T` can be so you can safely use its properties.
