# 109. Typed curry / compose / pipe
# हिंदी में: Typed curry / compose / pipe

> Verified with **TypeScript 5.9.3** (`--strict`). Uses overloads, tuple types, variadic tuple spreads (`[...infer R]`, **TS 4.0+**) and recursive conditional types.

---

## 🔵 Simple Definition (English)
- **`pipe(f, g, h)(x)`** = `h(g(f(x)))`: run functions **left to right**, each one's output feeds the next.
- **`compose(f, g, h)(x)`** = `f(g(h(x)))`: the same chain **right to left** (Redux's `compose` works this way).
- **`curry(fn)`** turns `fn(a, b, c)` into `fn(a)(b)(c)` (or `fn(a, b)(c)`), letting you **partially apply** arguments and reuse the result.

The interview challenge is typing them: every step's **output type must equal the next step's input type**, and `curry` must track **how many arguments are still missing**. That needs overloads, generics, tuple inference and recursive conditional types.

## 🔵 सरल परिभाषा (Hindi)
- **`pipe(f, g, h)(x)`** = `h(g(f(x)))`: functions **बाएँ से दाएँ** चलते हैं, हर एक का output अगले का input बनता है।
- **`compose(f, g, h)(x)`** = `f(g(h(x)))`: वही chain **दाएँ से बाएँ** (Redux का `compose` ऐसे ही काम करता है)।
- **`curry(fn)`** `fn(a, b, c)` को `fn(a)(b)(c)` (या `fn(a, b)(c)`) में बदलता है, जिससे आप arguments को **partially apply** करके नतीजा दोबारा इस्तेमाल कर सकते हो।

Interview की चुनौती इन्हें type करना है: हर step का **output type अगले step के input type के बराबर** होना चाहिए, और `curry` को **track करना है कि कितने arguments बाकी हैं**। इसके लिए overloads, generics, tuple inference और recursive conditional types चाहिए।

---

## 🔴 Problem it Solves
Untyped functional helpers return `any`: `pipe(parse, validate, save)` gives you an `any` function and all type information is lost, so a step that returns `number` feeding a step that wants `string` slips through. Hand-nesting calls (`save(validate(parse(x)))`) reads inside-out and gets unreadable at 5+ steps. Typed `pipe` keeps the readable left-to-right order **and** the compiler verifies every joint.

## 🔴 यह क्यों बना? (Hindi)
Untyped functional helpers `any` लौटाते हैं: `pipe(parse, validate, save)` से `any` function मिलता है और सारी type जानकारी खो जाती है, इसलिए `number` लौटाने वाला step जब `string` माँगने वाले step को feed करे तो वह निकल जाता है। हाथ से nested calls (`save(validate(parse(x)))`) अंदर से बाहर पढ़ने पड़ते हैं और 5+ steps पर अपठनीय हो जाते हैं। Typed `pipe` readable left-to-right क्रम **और** हर जोड़ की compiler-जाँच दोनों देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → **pipe**: write overloads `pipe(f1)`, `pipe(f1, f2)`, `pipe(f1, f2, f3)`... Each overload links types: `f1: (...a: A) => B`, `f2: (b: B) => C`, result `(...a: A) => C`. The shared `B`, `C` letters force output = next input.
Step 2 → **Implementation signature** is loose (`...fns: Function[]`) and reduces left to right; only the overloads are public. (This is how RxJS `pipe` is typed, with overloads up to 9.)
Step 3 → **compose** is the same with the overloads reversed: `compose(f2: (b: B) => C, f1: (...a: A) => B)`.
Step 4 → **curry (unary)**: `Curried<[A, B, C], R> = (a: A) => Curried<[B, C], R>`, recursion on a tuple with `[infer H, ...infer T]`, stop at `[]` returning `R`.
Step 5 → **curry (flexible)**: allow calling with **any prefix** of the remaining arguments. Compute `Prefixes<A>` (all non-empty leading tuples) and a `Rest<A, Given>` that drops what was supplied.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **pipe**: overloads लिखो `pipe(f1)`, `pipe(f1, f2)`, `pipe(f1, f2, f3)`...। हर overload types जोड़ता है: `f1: (...a: A) => B`, `f2: (b: B) => C`, नतीजा `(...a: A) => C`। साझा अक्षर `B`, `C` output = अगला input मजबूर करते हैं।
Step 2 → **Implementation signature** ढीली होती है (`...fns: Function[]`) और बाएँ से दाएँ reduce करती है; सिर्फ overloads public हैं। (RxJS का `pipe` ऐसे ही type है, 9 तक overloads।)
Step 3 → **compose** वही है पर overloads उलटे: `compose(f2: (b: B) => C, f1: (...a: A) => B)`।
Step 4 → **curry (unary)**: `Curried<[A, B, C], R> = (a: A) => Curried<[B, C], R>`, tuple पर `[infer H, ...infer T]` से recursion, `[]` पर `R` लौटाकर रुको।
Step 5 → **curry (flexible)**: बाकी arguments के **किसी भी prefix** के साथ call करने दो। `Prefixes<A>` (सभी non-empty leading tuples) और `Rest<A, Given>` (जो दिया उसे हटाए) निकालो।

---

## 🟡 Real World Example
**Swiggy checkout pricing** is a pipeline: `items -> subtotal -> applyCoupon("SAVE20") -> addDeliveryFee -> addGST -> format`. With `pipe`, every stage is a tiny testable function and the compiler guarantees `subtotal` (number) goes into `applyCoupon` (number) and that `format` (number -> string) is last. `curry` lets you create `applyCoupon("SAVE20")` once and reuse it for every cart: `const save20 = curry(applyCoupon)("SAVE20")`.

## 🟡 Real Example Hindi mein
**Swiggy checkout pricing** एक pipeline है: `items -> subtotal -> applyCoupon("SAVE20") -> addDeliveryFee -> addGST -> format`। `pipe` से हर stage एक छोटा testable function है और compiler गारंटी देता है कि `subtotal` (number) `applyCoupon` (number) में जाए और `format` (number -> string) सबसे आखिर में हो। `curry` से `applyCoupon("SAVE20")` एक बार बनाकर हर cart के लिए reuse कर सकते हो: `const save20 = curry(applyCoupon)("SAVE20")`।

---

## 💻 Code Example — Basic

```typescript
// pipe-basic.ts — typed pipe via overloads, plus compose
type Fn<A extends unknown[] = any[], R = any> = (...args: A) => R; // generic function shape

function pipe<A extends unknown[], B>(f1: Fn<A, B>): Fn<A, B>; // 1 function
function pipe<A extends unknown[], B, C>(f1: Fn<A, B>, f2: Fn<[B], C>): Fn<A, C>; // 2: f1 output B feeds f2
function pipe<A extends unknown[], B, C, D>(f1: Fn<A, B>, f2: Fn<[B], C>, f3: Fn<[C], D>): Fn<A, D>; // 3
function pipe<A extends unknown[], B, C, D, E>(f1: Fn<A, B>, f2: Fn<[B], C>, f3: Fn<[C], D>, f4: Fn<[D], E>): Fn<A, E>; // 4
function pipe(...fns: Fn[]): Fn { // implementation signature (not visible to callers)
  return (...args) => fns.slice(1).reduce((acc, f) => f(acc), fns[0]!(...args)); // run left to right
}

function compose<A extends unknown[], B, C>(f2: Fn<[B], C>, f1: Fn<A, B>): Fn<A, C>; // 2 functions, right to left
function compose<A extends unknown[], B, C, D>(f3: Fn<[C], D>, f2: Fn<[B], C>, f1: Fn<A, B>): Fn<A, D>; // 3
function compose(...fns: Fn[]): Fn { // implementation
  return (...args) => fns.slice(0, -1).reduceRight((acc, f) => f(acc), fns[fns.length - 1]!(...args)); // last function first
}

const subtotal = (prices: number[]) => prices.reduce((a, b) => a + b, 0); // number[] -> number
const withGst = (n: number) => Math.round(n * 1.18); // number -> number
const label = (n: number) => `Rs ${n}`; // number -> string

const checkout = pipe(subtotal, withGst, label); // (prices: number[]) => string, all inferred
console.log(checkout([100, 200])); // prints Rs 354
const checkout2 = compose(label, withGst, subtotal); // same chain, written right-to-left
console.log(checkout2([100, 200])); // prints Rs 354
const s: string = checkout([1]); // result type is string, verified
console.log(s); // prints Rs 1
```

```typescript
// pipe-errors.ts — the compiler checks every joint
type Fn<A extends unknown[] = any[], R = any> = (...args: A) => R; // function shape
declare function pipe<A extends unknown[], B, C>(f1: Fn<A, B>, f2: Fn<[B], C>): Fn<A, C>; // typed overload

const len = (s: string) => s.length; // string -> number
const shout = (s: string) => s.toUpperCase(); // string -> string

// ❌ len returns number, but shout expects string
pipe(len, shout);
// error TS2345: Argument of type '(s: string) => number' is not assignable to parameter of type 'Fn<[s: string], string>'.
//   Type 'number' is not assignable to type 'string'.
```

## 💻 Code Example — Advanced

```typescript
// curry-advanced.ts — flexible curry: supply any prefix of the arguments each call
type Prefixes<A extends unknown[]> = A extends [infer H, ...infer T] ? [H] | [H, ...Prefixes<T>] : never; // [number,string] -> [number] | [number,string]
type Rest<A extends unknown[], G extends unknown[]> = // drop as many leading items as were given
  G extends [unknown, ...infer GT] ? (A extends [unknown, ...infer AT] ? Rest<AT, GT> : []) : A;
type Curried<A extends unknown[], R> = // callable with any prefix of A
  <G extends Prefixes<A>>(...args: G) => Rest<A, G> extends [] ? R : Curried<Rest<A, G>, R>; // all given -> R, else keep currying

function curry<A extends unknown[], R>(fn: (...args: A) => R): Curried<A, R> { // runtime uses fn.length
  const c = (...got: unknown[]): unknown => // collect arguments across calls
    got.length >= fn.length ? fn(...(got as A)) : (...more: unknown[]) => c(...got, ...more); // enough? call : wait for more
  return c as Curried<A, R>; // one cast: the runtime matches the type
}

const price = (base: number, gst: number, coupon: string) => `${base + gst} ${coupon}`; // 3-arg function
const cp = curry(price); // Curried<[number, number, string], string>

const a = cp(100)(18)("A"); // one at a time
const b = cp(100, 18)("A"); // two then one
const c = cp(100)(18, "A"); // one then two
const d = cp(100, 18, "A"); // all at once
const all: string[] = [a, b, c, d]; // every route returns string
console.log(all.join(" | ")); // prints 118 A | 118 A | 118 A | 118 A

const withFee = cp(100); // partial application, reusable
console.log(withFee(18)("WELCOME")); // prints 118 WELCOME

// ❌ wrong argument type at the first step
cp("x");
// error TS2345: Argument of type '["x"]' is not assignable to parameter of type '[number] | [number, number] | [number, number, string]'.
//   Type '["x"]' is not assignable to type '[number]'.
//     Type 'string' is not assignable to type 'number'.

// ❌ wrong argument type at the last step
cp(100)(18)(5);
// error TS2345: Argument of type 'number' is not assignable to parameter of type 'string'.
```

```typescript
// curry-unary.ts — the simplest typed curry (one argument per call), easiest to explain on a whiteboard
type CurriedUnary<A extends unknown[], R> = // recurse over the argument tuple
  A extends [infer H, ...infer T] ? (arg: H) => CurriedUnary<T, R> : R; // peel one parameter per call

function curryUnary<A extends unknown[], R>(fn: (...args: A) => R): CurriedUnary<A, R> { // wrapper
  const go = (acc: unknown[]) => (arg: unknown): unknown => // closure remembers earlier arguments
    acc.length + 1 >= fn.length ? fn(...([...acc, arg] as A)) : go([...acc, arg]); // last arg? call fn
  return go([]) as CurriedUnary<A, R>; // start with no arguments
}

const addGst = (rate: number, amount: number) => amount + (amount * rate) / 100; // 2 params
const gst18 = curryUnary(addGst)(18); // (amount: number) => number
console.log(gst18(1000)); // prints 1180
```

---

## 🟠 Node/Express + React Integration

```typescript
// express-pipe.ts — build a typed request transformation pipeline for an Express handler
import express from "express"; // express + types

type Fn<A extends unknown[] = any[], R = any> = (...args: A) => R; // shape
function pipe<A extends unknown[], B, C, D>(f1: Fn<A, B>, f2: Fn<[B], C>, f3: Fn<[C], D>): Fn<A, D>; // typed overload
function pipe(...fns: Fn[]): Fn { return (...a) => fns.slice(1).reduce((acc, f) => f(acc), fns[0]!(...a)); } // implementation

interface CartBody { prices: number[]; coupon?: string } // incoming JSON
const parse = (b: CartBody) => b.prices.reduce((x, y) => x + y, 0) - (b.coupon === "SAVE20" ? 20 : 0); // body -> number
const addGst = (n: number) => Math.round(n * 1.18); // number -> number
const toResponse = (n: number) => ({ payable: n, currency: "INR" as const }); // number -> DTO
const price = pipe(parse, addGst, toResponse); // (b: CartBody) => { payable: number; currency: "INR" }

const app = express(); // app
app.use(express.json()); // JSON body parser
app.post("/price", (req: express.Request<unknown, unknown, CartBody>, res) => {
  res.json(price(req.body)); // whole pipeline in one typed call
});
```

```tsx
// useDiscount.tsx — React: curried selector factory keeps components tidy
import { useMemo } from "react"; // hooks

const discountBy = (percent: number) => (amount: number) => Math.round(amount * (1 - percent / 100)); // hand-curried
// the same idea as curry(fn)(percent), reusable across components

export function PriceTag({ amount, percent }: { amount: number; percent: number }) { // component
  const apply = useMemo(() => discountBy(percent), [percent]); // build the specialised function once per percent
  return <span>Rs {apply(amount)}</span>; // reuse it
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Typing `pipe` with `any`
```typescript
// wrong-pipe.ts
function badPipe(...fns: Function[]) { return (x: any): any => fns.reduce((acc, f) => f(acc), x); } // wrong: any in, any out
const f = badPipe((s: string) => s.length, (s: string) => s.toUpperCase()); // compiles, crashes at runtime
console.log(typeof f); // prints function
// at runtime f("ab") throws: s.toUpperCase is not a function
```
✅ Correct: use the overload style so each joint is checked (see Basic).

❌ Mistake 2: Forgetting that `fn.length` ignores default and rest params
```typescript
// wrong-length.ts
const withDefault = (a: number, b = 2) => a + b; // fn.length is 1, not 2
const optional = (a: number, b?: number) => a + (b ?? 0); // fn.length is 2
console.log(withDefault.length, optional.length); // prints 1 2
```
✅ Correct: runtime `curry` relies on `fn.length`; for functions with defaults/rest pass the arity explicitly (`curry(fn, 2)`), as lodash does.

❌ Mistake 3: Passing a generic function as the FIRST step of `pipe`
```typescript
// wrong-generic.ts
type Fn<A extends unknown[] = any[], R = any> = (...args: A) => R; // shape
declare function pipe<A extends unknown[], B, C>(f1: Fn<A, B>, f2: Fn<[B], C>): Fn<A, C>; // typed overload
const identity = <T,>(x: T) => x; // generic function

// ❌ nothing tells TS what T is, so it becomes unknown and the next step rejects it
pipe(identity, (n: number) => n);
// error TS2345: Argument of type '<T>(x: T) => T' is not assignable to parameter of type 'Fn<[x: unknown], number>'.
//   Type 'unknown' is not assignable to type 'number'.
```
✅ Correct: wrap or annotate the first step: `pipe((n: number) => identity(n), (n: number) => n)`. A generic function in a **later** position can often be inferred from the previous result, the first position cannot.

---

## 🧠 Tricky Interview Question

```typescript
// tricky.ts — what are the types of x and y, and which line errors?
type Fn<A extends unknown[] = any[], R = any> = (...args: A) => R; // shape
declare function pipe<A extends unknown[], B, C>(f1: Fn<A, B>, f2: Fn<[B], C>): Fn<A, C>; // overload

const f = pipe((a: number, b: number) => a + b, (n) => n.toFixed(1)); // n is contextually typed
const x = f(1, 2); // x: string
console.log(x); // prints 3.0 if run
// ❌ f needs two arguments because the FIRST function decides the parameters
f(1);
// error TS2554: Expected 2 arguments, but got 1.
```
**Answer:** In `pipe`, only the **first function** may take multiple arguments (`A extends unknown[]`), every later one takes exactly one (the previous result `[B]`). The parameter `n` in the second function needs **no annotation**: TypeScript infers `B = number` from the first argument and uses it as the contextual type for the second (left-to-right inference through overloads). That contextual flow is why `pipe` is written with parameters in **left-to-right order**, while `compose`, whose first-written function is the *last* to run, needs more annotations.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `pipe` and `compose`?
A1: Same chain, opposite order. `pipe(f, g)(x) = g(f(x))` (reads left to right), `compose(f, g)(x) = f(g(x))` (mathematical order, used by Redux `compose` for enhancers/middleware).

Q2: Why overloads and not a single variadic signature?
A2: A variadic `...fns: Fn[]` cannot say "output of item *i* equals input of item *i+1*". Overloads link neighbouring type parameters explicitly. A mapped-tuple approach exists but is hard to read and fragile; libraries (RxJS, fp-ts) ship overloads up to 9-10.

Q3: What is currying vs partial application?
A3: Currying transforms a function of N arguments into N nested unary functions. Partial application fixes some arguments and returns a function for the rest. Flexible `curry` helpers (lodash, Ramda) support both styles.

Q4: How do you type `curry` for exactly N arguments?
A4: Recurse on the parameter tuple: `A extends [infer H, ...infer T] ? (arg: H) => Curried<T, R> : R`. For multi-argument calls build the union of prefixes and drop the supplied part (`Rest`).

Q5: How would you type an **async** pipe?
A5: Each step may return `T | Promise<T>`. Use `Awaited<B>` for the next input: `pipeAsync<A, B, C>(f1: Fn<A, B>, f2: Fn<[Awaited<B>], C>): (...a: A) => Promise<Awaited<C>>`. `Awaited` needs **TS 4.5+**.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Data transformation pipelines (pricing, parsing, normalising API responses) built from small pure functions
- Composing Redux enhancers/middleware (`compose`) or RxJS operators (`pipe`)

❌ Avoid when:
- A team unfamiliar with FP will struggle to debug point-free chains, simple named variables read better
- Steps need early exit, branching or async control flow, use `async/await` and plain statements

---

## 📊 Visual Diagram
```
 pipe(f1, f2, f3)             compose(f3, f2, f1)
 x ─► f1 ─► f2 ─► f3 ─► y     x ─► f1 ─► f2 ─► f3 ─► y   (same data flow, written reversed)

 types:  f1: (...A) => B
         f2: (B)    => C       the SAME letters B, C force output = next input
         f3: (C)    => D
         result: (...A) => D

 curry((a:number, b:number, c:string) => R)
   cp(1)           ──► Curried<[number,string], R>
   cp(1)(2)        ──► Curried<[string], R>
   cp(1)(2)("x")   ──► R
   cp(1,2,"x")     ──► R
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| pipe | Left-to-right function chain | बाएँ से दाएँ function chain |
| compose | Right-to-left function chain | दाएँ से बाएँ function chain |
| Currying | N-arg function -> nested unary functions | N-argument function से nested unary functions |
| Partial application | Fix some args, return rest | कुछ args तय करके बाकी का function |
| Overload | Several call signatures for one function | एक function के कई call signatures |
| Variadic tuple | Tuple with spread `[...T]` | Spread वाला tuple |

---

## ⚡ 3-Line Summary
English:
1. Type `pipe`/`compose` with overloads where shared letters (`B`, `C`) force each output to equal the next input.
2. Type `curry` with recursive conditional types over the parameter tuple (`[infer H, ...infer T]`), optionally with `Prefixes` and `Rest` for multi-argument calls.
3. Only the first function in a pipe may take many arguments; later ones are unary and get contextual types for free.

Hindi:
1. `pipe`/`compose` को overloads से type करो जहाँ साझा अक्षर (`B`, `C`) हर output को अगले input के बराबर मजबूर करते हैं।
2. `curry` को parameter tuple पर recursive conditional types (`[infer H, ...infer T]`) से type करो, multi-argument calls के लिए `Prefixes` और `Rest` जोड़ो।
3. Pipe में सिर्फ पहला function कई arguments ले सकता है; बाद वाले unary होते हैं और उन्हें contextual types मुफ्त मिलते हैं।

---

## ➡️ Next Topic
**110. Type-safe Builder Pattern** — a fluent builder that refuses `.build()` until all required fields are set.
