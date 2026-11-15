# 22. Optional, Default and Rest Parameters
# हिंदी में: Optional, Default और Rest Parameters

> TypeScript 5.x | Labeled tuple elements for rest params since TS 4.0 | Variadic tuple types since TS 4.0

---

## 🔵 Simple Definition (English)
TypeScript lets a function accept a flexible number of arguments in three ways. An **optional parameter** (`b?: number`) may be omitted; inside the function its type is `number | undefined`. A **default parameter** (`b = 10`) supplies a value when the argument is omitted or `undefined`; its type is inferred from the default, and callers may omit it. A **rest parameter** (`...items: string[]`) collects all remaining arguments into an array (or a typed tuple). Rules: optional and default parameters must come after required ones (a default can come earlier but then callers must pass `undefined` explicitly), and the rest parameter must be last.

## 🔵 सरल परिभाषा (Hindi)
TypeScript में function तीन तरीकों से flexible संख्या में arguments ले सकता है। **Optional parameter** (`b?: number`) छोड़ा जा सकता है; function के अंदर उसका type `number | undefined` होता है। **Default parameter** (`b = 10`) argument छूटने या `undefined` होने पर value देता है; type default से infer होता है और callers उसे छोड़ सकते हैं। **Rest parameter** (`...items: string[]`) बाकी सारे arguments को एक array (या typed tuple) में इकट्ठा करता है। नियम: optional और default parameters required के **बाद** आने चाहिए (default पहले आ सकता है पर तब callers को `undefined` explicitly देना पड़ता है), और rest parameter हमेशा **आखिरी** होता है।

---

## 🔴 Problem it Solves
JavaScript functions silently accept any number of arguments: a missing argument becomes `undefined` and a later calculation yields `NaN`, and extra arguments are ignored. Libraries therefore document "optional" behaviour in comments only. Explicit optional, default and rest parameters turn that into a checked contract: calling `applyDiscount(500)` is fine when `percent` is optional, calling `applyDiscount()` is a compile error (`Expected 1-2 arguments, but got 0`), and `sum('a')` is rejected for a `...nums: number[]` rest parameter. It also replaces the old `arguments` object with a real, typed array.

## 🔴 यह क्यों बना? (Hindi)
JavaScript functions चुपचाप किसी भी संख्या के arguments ले लेते हैं: छूटा argument `undefined` बन जाता है और आगे की गणना `NaN` देती है, और extra arguments ignore हो जाते हैं। इसलिए libraries "optional" व्यवहार सिर्फ़ comments में लिखती हैं। Explicit optional, default और rest parameters इसे checked contract बना देते हैं: `percent` optional हो तो `applyDiscount(500)` ठीक है, `applyDiscount()` compile error है (`Expected 1-2 arguments, but got 0`), और `...nums: number[]` rest parameter के लिए `sum('a')` reject होता है। यह पुराने `arguments` object की जगह असली, typed array भी देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Optional: `function f(a: number, b?: number)`. Callers can write `f(1)` or `f(1, 2)`. Inside, `b` is `number | undefined`, so narrow it or use `??` before arithmetic.
Step 2 → Default: `function f(a: number, b = 10)`. The type of `b` is inferred as `number`, callers may omit it or pass `undefined` (which also triggers the default), and inside `b` is plain `number` (never undefined).
Step 3 → A default can hold an expression evaluated on each call (`created = new Date()`), and can reference earlier parameters (`b = a * 2`).
Step 4 → Order: a **required** parameter after an **optional** one is an error (TS1016). A **default** parameter before a required one is allowed, but callers must pass `undefined` to use the default.
Step 5 → Rest: `function f(label: string, ...nums: number[])` collects extra arguments into `nums`. The rest parameter must be the last and must have an array or tuple type.
Step 6 → Rest with tuples gives positional typing: `...args: [id: number, note?: string]` behaves like two (one optional) parameters, and the labels show in editor tooltips.
Step 7 → Spread on the call side (`f(...list)`) needs a tuple or a rest-parameter to match; spreading a plain `number[]` into fixed parameters is an error (TS2556).
Step 8 → Optional/default parameters appear in the function type as `(a: number, b?: number) => number`; a default parameter is shown as optional to callers.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Optional: `function f(a: number, b?: number)`। Callers `f(1)` या `f(1, 2)` लिख सकते हैं। अंदर `b` का type `number | undefined` है, इसलिए arithmetic से पहले narrow करो या `??` इस्तेमाल करो।
Step 2 → Default: `function f(a: number, b = 10)`। `b` का type `number` infer होता है, callers उसे छोड़ सकते हैं या `undefined` दे सकते हैं (इससे भी default लगता है), और अंदर `b` सादा `number` है (कभी undefined नहीं)।
Step 3 → Default में ऐसी expression हो सकती है जो हर call पर evaluate हो (`created = new Date()`), और पिछले parameters को refer कर सकती है (`b = a * 2`)।
Step 4 → क्रम: optional के बाद **required** parameter error है (TS1016)। Required से पहले **default** parameter चलता है, पर तब default पाने के लिए callers को `undefined` देना पड़ता है।
Step 5 → Rest: `function f(label: string, ...nums: number[])` extra arguments को `nums` में इकट्ठा करता है। Rest parameter आखिरी होना चाहिए और उसका type array या tuple होना चाहिए।
Step 6 → Tuples के साथ rest positional typing देता है: `...args: [id: number, note?: string]` दो (एक optional) parameters की तरह काम करता है, और labels editor tooltips में दिखते हैं।
Step 7 → Call की तरफ़ spread (`f(...list)`) के लिए tuple या rest-parameter चाहिए; सादे `number[]` को fixed parameters में spread करना error है (TS2556)।
Step 8 → Optional/default parameters function type में `(a: number, b?: number) => number` की तरह दिखते हैं; default parameter callers को optional दिखता है।

---

## 🟡 Real World Example
**Swiggy's order total calculator**: `calculateTotal(subtotal: number, deliveryFee = 40, couponPercent?: number)`. The delivery fee has a sensible default (Rs 40), the coupon is genuinely optional (most users have none), and a logger helper `logEvent(name: string, ...details: unknown[])` accepts any number of extra details. `Math.max(...prices)` is the same rest-and-spread idea in the standard library. Making the default explicit means every call site (React checkout, Express invoice route, tests) agrees on Rs 40, instead of each writing `fee || 40` and breaking when the fee is intentionally `0`.

## 🟡 Real Example Hindi mein
**Swiggy का order total calculator**: `calculateTotal(subtotal: number, deliveryFee = 40, couponPercent?: number)`। Delivery fee का समझदार default है (Rs 40), coupon सच में optional है (ज़्यादातर users के पास नहीं होता), और logger helper `logEvent(name: string, ...details: unknown[])` जितने चाहें extra details ले लेता है। `Math.max(...prices)` standard library में यही rest-और-spread idea है। Default को explicit रखने से हर call site (React checkout, Express invoice route, tests) Rs 40 पर सहमत रहता है, हर कोई `fee || 40` नहीं लिखता, जो fee जानबूझकर `0` होने पर टूट जाता।

---

## 💻 Code Example — Basic

```typescript
// params-basic.ts  (TypeScript 5.x, strict)

// 1. Optional parameter: type inside is number | undefined
function applyDiscount(price: number, percent?: number): number {
  if (percent === undefined) return price;           // narrow: undefined removed below
  return price - price * (percent / 100);            // percent is number here
}

// 2. Default parameter: type inferred from the default, no ? needed
function calculateTotal(subtotal: number, deliveryFee = 40): number {
  return subtotal + deliveryFee;                     // deliveryFee is number (never undefined)
}

// 3. Rest parameter: all remaining arguments collected into an array
function sum(label: string, ...nums: number[]): string {
  const total = nums.reduce((a, b) => a + b, 0);     // nums is number[]
  return `${label}: ${total}`;
}

// 4. Default that depends on a previous parameter and is evaluated per call
function makeOrder(id: number, items: string[] = [], createdAt = new Date(0)) {
  return { id, count: items.length, year: createdAt.getUTCFullYear() };
}

// 5. Spread on the call side with a rest parameter
const prices = [100, 250, 75];
console.log(Math.max(...prices));                    // spread into Math.max's rest parameter
console.log(sum('cart', ...prices));                 // spread into our rest parameter

console.log(applyDiscount(500), applyDiscount(500, 10));
console.log(calculateTotal(200), calculateTotal(200, 0), calculateTotal(200, undefined));
console.log(sum('empty'));
console.log(makeOrder(1), makeOrder(2, ['pizza']));
```

Run with `npx tsx params-basic.ts`. Real output:
```
250
cart: 425
500 450
240 200 240
empty: 0
{ id: 1, count: 0, year: 1970 } { id: 2, count: 1, year: 1970 }
```

## 💻 Code Example — Advanced

```typescript
// params-advanced.ts  (TypeScript 5.x)

// 1. Rest parameter typed as a labeled tuple: positional, partly optional
function track(...args: [event: string, userId?: number, ...tags: string[]]): string {
  const [event, userId = 0, ...tags] = args;          // destructure the tuple
  return `${event}:${userId}:${tags.join('|')}`;
}

// 2. Options object instead of many optional parameters (preferred beyond 3 params)
interface ChargeOptions { currency?: 'INR' | 'USD'; retries?: number; note?: string }
function charge(amount: number, { currency = 'INR', retries = 3, note = '' }: ChargeOptions = {}): string {
  return `${amount} ${currency} x${retries}${note ? ' ' + note : ''}`;  // defaults per key
}

// 3. Generic rest: keep each argument type (variadic tuple)
function tuple<T extends unknown[]>(...args: T): T {
  return args;                                         // T is the exact tuple of argument types
}
const t = tuple('order', 42, true);                    // [string, number, boolean]

// 4. Wrapping a function: forward parameters with Parameters<F> (keeps optional/default info)
function logged<F extends (...a: never[]) => unknown>(fn: F) {
  return (...args: Parameters<F>): ReturnType<F> => {
    console.log('args', args);
    return fn(...args) as ReturnType<F>;
  };
}
const loggedTotal = logged((subtotal: number, fee = 40) => subtotal + fee);
// loggedTotal's parameter list is (subtotal: number, fee?: number)

// 5. Default parameter and "undefined vs null": only undefined triggers the default
function greet(name: string = 'guest'): string { return `hi ${name}`; }
console.log(greet(undefined));                         // 'hi guest' (default used)
// greet(null) would be an error under strictNullChecks

// 6. Callback overloading by arity using optional callback parameters (like Node style)
function readOrder(id: number, cb?: (err: Error | null, row?: { id: number }) => void): Promise<{ id: number }> | void {
  const row = { id };
  if (cb) { cb(null, row); return; }                   // callback style
  return Promise.resolve(row);                         // promise style
}

console.log(track('click'), track('buy', 7, 'vip', 'upi'));
console.log(charge(500), charge(500, { currency: 'USD', note: 'gift' }));
console.log(t, loggedTotal(100), loggedTotal(100, 0));
readOrder(5, (err, row) => console.log(err, row));
readOrder(6)?.then((r) => console.log(r));
```

Run with `npx tsx params-advanced.ts`. Real output:
```
hi guest
click:0: buy:7:vip|upi
500 INR x3 500 USD x3 gift
[ 'order', 42, true ]
args [ 100 ]
args [ 100, 0 ]
140 100
null { id: 5 }
{ id: 6 }
```
(The first line comes from the `greet(undefined)` call that runs before the final `console.log` lines; `140 100` are the two `loggedTotal` results printed after their `args` logs.)

---

## 🟠 Node/Express + React Integration

```tsx
// server.ts  (Express): optional/default parameters for query handling
import express from 'express';
const app = express();

// Default parameters give pagination a safe baseline
function paginate<T>(items: T[], page = 1, pageSize = 10): T[] {
  const start = (page - 1) * pageSize;                // page and pageSize are number
  return items.slice(start, start + pageSize);
}

app.get('/orders', (req, res) => {
  // req.query values are strings; parse then pass, `undefined` triggers the defaults
  const page = typeof req.query.page === 'string' ? Number(req.query.page) : undefined;
  const rows = Array.from({ length: 25 }, (_, i) => ({ id: i + 1 }));
  res.json(paginate(rows, page));                      // page undefined -> default 1
});

// Rest parameter for a tiny logger used in middleware
function logRequest(method: string, path: string, ...extra: unknown[]): void {
  console.log(method, path, ...extra);                 // spread the rest into console.log
}
app.use((req, _res, next) => { logRequest(req.method, req.path); next(); });

// React: optional props with defaults (the idiomatic place for "default parameters")
interface PriceTagProps { amount: number; currency?: 'INR' | 'USD'; showFree?: boolean }
export function PriceTag({ amount, currency = 'INR', showFree = true }: PriceTagProps) {
  if (amount === 0 && showFree) return <b>Free</b>;    // destructured defaults
  return <b>{currency} {amount}</b>;
}

// Redux Toolkit: prepare callback uses optional parameter for the payload
import { createSlice } from '@reduxjs/toolkit';
const cart = createSlice({
  name: 'cart',
  initialState: [] as { sku: string; qty: number }[],
  reducers: {
    added: {
      reducer(state, action: { type: string; payload: { sku: string; qty: number } }) { state.push(action.payload); },
      prepare(sku: string, qty = 1) { return { payload: { sku, qty } }; }, // dispatch(added('PIZZA'))
    },
  },
});
export const { added } = cart.actions;
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Required parameter after an optional one
```typescript
// ❌ Wrong: b is required but follows the optional a
function h(a?: number, b: number) {}
// error TS1016: A required parameter cannot follow an optional parameter.
```
```typescript
// ✅ Right: put required first, or give the earlier parameter a default
function h(b: number, a?: number) {}
function h2(a: number | undefined, b: number) {}   // explicit undefined is allowed; caller must pass something
```

❌ Mistake 2: Wrong type in a rest argument
```typescript
function rr(...xs: number[]) {}
// ❌ Wrong: 'a' is not a number
rr('a');
// error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.
```

❌ Mistake 3: Omitting a required argument next to a default
```typescript
function dd2(a: number, b = 5) {}
// ❌ Wrong: a is required, only b has a default
dd2();
// error TS2554: Expected 1-2 arguments, but got 0.
```
✅ Correct: `dd2(1)` or `dd2(1, 9)`.

❌ Mistake 4: Spreading a plain array into fixed parameters
```typescript
function add(a: number, b: number) { return a + b; }
const pair = [1, 2];          // number[], length unknown
// ❌ Wrong: the compiler cannot prove two elements exist
add(...pair);
// error TS2556: A spread argument must either have a tuple type or be passed to a rest parameter.
```
✅ Correct: `const pair = [1, 2] as const;` (a `readonly [1, 2]` tuple) or `const pair: [number, number] = [1, 2];`.

❌ Mistake 5: Using `||` for a default inside the body (`const fee = deliveryFee || 40`) turns an intentional `0` into `40`. Use a default parameter or `??`.

---

## 🧠 Tricky Interview Question

```typescript
function f(a: number, b = a * 2, c?: number) {
  return [a, b, c];
}
console.log(f(1));
console.log(f(1, undefined, 3));
console.log(f(1, 0));
```
Answer: Output is `[ 1, 2, undefined ]`, then `[ 1, 2, 3 ]`, then `[ 1, 0, undefined ]`. The default for `b` is evaluated at call time using the earlier parameter `a`. Passing `undefined` explicitly triggers the default, which is how you "skip" a default parameter to supply a later one. Passing `0` does NOT trigger the default (only `undefined` does), unlike `b || a * 2`. The type of the function is `(a: number, b?: number, c?: number) => (number | undefined)[]`: a default parameter is optional for callers.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `b?: number` and `b = 10`?
A1: Optional (`?`) means the caller may omit it and inside the function it is `number | undefined`, so you must handle it. A default parameter supplies a value when the argument is omitted or `undefined`, so inside the function it is plain `number`. Both appear optional in the function's type from the caller's perspective, but you cannot use `?` and a default on the same parameter.

Q2: Where may optional, default and rest parameters appear?
A2: Optional parameters must follow all required ones (TS1016 otherwise). Default parameters may appear anywhere, but a default before a required parameter forces callers to pass `undefined` to use it. A rest parameter must be last, only one is allowed, and it must have an array or tuple type.

Q3: Why prefer an options object over many optional parameters?
A3: With `f(a, b?, c?, d?)` callers must write `f(1, undefined, undefined, true)` to set `d`, and order mistakes are not caught if types match. An options object (`f(1, { d: true })`) is self-documenting, order-independent and easy to extend without breaking callers. Use destructured defaults to supply per-key defaults.

Q4: How do you type a function that forwards all arguments to another function?
A4: Use a generic over the function type and `Parameters<F>` / `ReturnType<F>`, or a generic rest tuple (`<A extends unknown[], R>(fn: (...args: A) => R) => (...args: A) => R`). This preserves optional and default-ness, labels and return types, which is how wrappers like `withRetry`, `debounce` or `memoize` stay type-safe.

Q5: What is a variadic tuple / labeled tuple rest parameter?
A5: Since TS 4.0 a rest parameter can be a tuple: `...args: [id: number, note?: string, ...tags: string[]]`. It gives per-position types, optional positions and readable names in IDE tooltips, and can be composed with spreads in generic signatures (`[...A, ...B]`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Optional: a truly optional input where "not provided" has a clear meaning
- Default: a sensible fallback (page size, currency, timeout) that callers rarely change
- Rest: variadic helpers (loggers, `sum`, `compose`, `path.join`-like utilities)
- Options object with destructured defaults when there are 3 or more optional inputs

❌ Avoid when:
- A parameter is required in practice: do not mark `?` to "make the error go away"
- More than 3 positional optionals: switch to an options object
- You need a value to be intentionally `undefined`: a default parameter will override it
- Using the legacy `arguments` object; rest parameters are typed and work in arrow functions

---

## 📊 Visual Diagram
```
 function f(a: number,  b?: number,   c = 10,        ...rest: string[])
              │          │             │               │
          required   number|undefined  number        string[] (must be last)
                      (can omit)       (can omit,
                                        undefined also
                                        triggers default)

 f(1)            -> a=1 b=undefined c=10 rest=[]
 f(1, 2, 3, 'x') -> a=1 b=2 c=3 rest=['x']
 f(1, undefined, undefined, 'x', 'y')   // skip middle params with undefined

 Order rule:  required ... optional/default ... ...rest
              (required AFTER optional = TS1016)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Optional parameter | `b?: T`, may be omitted | `b?: T`, छोड़ सकते हैं |
| Default parameter | `b = value`, used if undefined | `undefined` पर default value |
| Rest parameter | `...xs: T[]`, collects extras | बाकी arguments का array |
| Spread | `f(...arr)` expands an array | Array को arguments में फैलाना |
| Arity | Number of parameters | Parameters की संख्या |
| Variadic tuple | Tuple types with spreads | Spread वाले tuple types |
| Options object | One object param with named keys | Named keys वाला एक object |

---

## ⚡ 3-Line Summary
English:
1. Optional (`?`) gives `T | undefined`; a default (`= v`) gives plain `T` inside and is optional for callers; rest (`...xs`) collects extras and must be last.
2. Required parameters must come before optional ones; only `undefined` (not `null` or `0`) triggers a default.
3. For many options use an options object with destructured defaults; use `Parameters<F>` or generic rest tuples to forward arguments safely.

Hindi:
1. Optional (`?`) अंदर `T | undefined` देता है; default (`= v`) अंदर सादा `T` देता है और callers के लिए optional है; rest (`...xs`) extras इकट्ठा करता है और आखिरी होना चाहिए।
2. Required parameters optional से पहले आएँ; सिर्फ़ `undefined` (`null` या `0` नहीं) default को चलाता है।
3. ज़्यादा options के लिए destructured defaults वाला options object लो; arguments सुरक्षित forward करने के लिए `Parameters<F>` या generic rest tuples इस्तेमाल करो।

---

## ➡️ Next Topic
**23. Function Overloads** — multiple call signatures for one function, so the return type depends on the arguments.
