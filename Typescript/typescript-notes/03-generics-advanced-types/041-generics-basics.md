# 41. Generics Basics
# हिंदी में: Generics की बुनियादी बातें

> Verified with **TypeScript 5.x** (compiled with 5.9, `--strict`). Generics exist since TS 0.9; `const` type parameters (`<const T>`) are **TS 5.0** (mentioned below).

---

## 🔵 Simple Definition (English)
**Generics** let you write a function, interface, type or class that works with **many types** while still remembering *which* type was used. You declare a **type parameter** (conventionally `T`) in angle brackets, and the compiler fills it in at each use: `Box<number>`, `Box<string>`. Think of `T` as a *variable for a type* — the function takes it as input and uses it in its parameters and return type, so the output type is linked to the input type.

## 🔵 सरल परिभाषा (Hindi)
**Generics** से आप ऐसा function, interface, type या class लिख सकते हो जो **कई types** के साथ चले, फिर भी याद रखे कि *कौन सा* type इस्तेमाल हुआ। आप angle brackets में एक **type parameter** (आम तौर पर `T`) declare करते हो और compiler हर use पर उसे भर देता है: `Box<number>`, `Box<string>`। `T` को *type के लिए variable* समझो — function उसे input की तरह लेता है और parameters व return type में इस्तेमाल करता है, इसलिए output type, input type से जुड़ा रहता है।

---

## 🔴 Problem it Solves
Without generics you have two bad options:
1. **Duplicate code**: `firstNumber(xs: number[])`, `firstString(xs: string[])`, `firstOrder(xs: Order[])`...
2. **Use `any`**: `first(xs: any[]): any` — one function, but the result is `any`, so `first(orders).totall` (typo) compiles and explodes at runtime.

Generics give one implementation **and** full type safety: `first(orders)` is `Order | undefined`, and the typo is a compile error.

## 🔴 यह क्यों बना? (Hindi)
Generics के बिना दो खराब विकल्प हैं:
1. **Code duplicate करना**: `firstNumber(xs: number[])`, `firstString(xs: string[])`, `firstOrder(xs: Order[])`...
2. **`any` इस्तेमाल करना**: `first(xs: any[]): any` — function एक है पर result `any` है, इसलिए `first(orders).totall` (typo) compile हो जाता है और runtime पर फटता है।

Generics एक implementation **और** पूरी type safety देते हैं: `first(orders)` का type `Order | undefined` है और typo compile error बन जाती है।

---

## 🟢 How it Works — Step by Step

Step 1 → Declare a type parameter after the name: `function first<T>(xs: T[]): T | undefined`.
Step 2 → Use `T` in parameter and return positions to **link** them (input element type = output type).
Step 3 → At a call, TypeScript **infers** `T` from the arguments: `first([1, 2, 3])` → `T = number`.
Step 4 → Or you pass it **explicitly**: `first<string>(["a"])`. Needed when inference has nothing to work with (e.g., `new Map<string, number>()`).
Step 5 → Generic **types** work the same: `interface ApiResponse<T> { data: T; ok: boolean }` → `ApiResponse<Order[]>`.
Step 6 → Inside the body, `T` is *opaque*: you can only do what is true for **every** type (pass it around, store it). To do more, add a constraint (topic 43).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → नाम के बाद type parameter declare करो: `function first<T>(xs: T[]): T | undefined`।
Step 2 → Parameter और return positions में `T` इस्तेमाल करके उन्हें **जोड़ो** (input का element type = output type)।
Step 3 → Call पर TypeScript arguments से `T` **infer** करता है: `first([1, 2, 3])` → `T = number`।
Step 4 → या आप **explicitly** देते हो: `first<string>(["a"])`। जब inference के पास कुछ न हो (जैसे `new Map<string, number>()`) तब ज़रूरी।
Step 5 → Generic **types** भी वैसे ही चलते हैं: `interface ApiResponse<T> { data: T; ok: boolean }` → `ApiResponse<Order[]>`।
Step 6 → Body के अंदर `T` *अपारदर्शी* है: आप सिर्फ वही कर सकते हो जो **हर** type के लिए सच हो (आगे pass करना, store करना)। ज़्यादा करने के लिए constraint जोड़ो (topic 43)।

---

## 🟡 Real World Example
**Swiggy backend API envelope**: every endpoint returns `{ ok: boolean; data: T; error?: string }`. Restaurants list: `T = Restaurant[]`; order detail: `T = Order`; payment status: `T = PaymentStatus`. The team defines `ApiResponse<T>` **once**, and the frontend's `fetchJson<T>(url)` helper returns `Promise<ApiResponse<T>>`. Autocomplete on `res.data` is correct for each endpoint and one refactor updates all of them.

## 🟡 Real Example Hindi mein
**Swiggy backend API envelope**: हर endpoint `{ ok: boolean; data: T; error?: string }` लौटाता है। Restaurants list: `T = Restaurant[]`; order detail: `T = Order`; payment status: `T = PaymentStatus`। टीम `ApiResponse<T>` **एक बार** define करती है, और frontend का `fetchJson<T>(url)` helper `Promise<ApiResponse<T>>` लौटाता है। हर endpoint के लिए `res.data` पर autocomplete सही आता है और एक refactor सबको update कर देता है।

---

## 💻 Code Example — Basic

```typescript
// A generic function: T links the input element type to the output type
function first<T>(items: T[]): T | undefined {
  return items[0]; // first element, or undefined for empty arrays
}

// T is inferred from the argument each time
const n = first([10, 20, 30]);                  // T = number  -> number | undefined
const s = first(["biryani", "dosa"]);           // T = string  -> string | undefined
const none = first<boolean>([]);                // explicit T because [] gives no hint

console.log(n, s, none);
// Output:
// 10 biryani undefined
```

```typescript
// A generic CLASS: Box remembers what it holds
class Box<T> {
  constructor(public value: T) {}               // field typed with T
  map<U>(fn: (v: T) => U): Box<U> {             // method with its OWN type parameter U
    return new Box(fn(this.value));             // new box, possibly different type
  }
}

const price = new Box(499);                     // Box<number>
const label = price.map((p) => `Rs ${p}`);      // Box<string>
console.log(label.value.toUpperCase());         // string methods available (typed)
// Output:
// RS 499
```

## 💻 Code Example — Advanced

```typescript
// Generic interface + generic type alias with TWO parameters
interface ApiResponse<T> {                       // API envelope
  ok: boolean;                                   // success flag
  data: T;                                       // payload of any type
}
type Result<T, E = string> =                     // success OR failure (E has a default)
  | { ok: true; value: T }
  | { ok: false; error: E };

interface Order { id: string; total: number }   // domain type

// Generic helper: wraps any payload in the envelope
function wrap<T>(data: T): ApiResponse<T> {
  return { ok: true, data };                     // return type linked to T
}

// Generic function returning Result<T>
function parseJson<T>(text: string): Result<T> {
  try {
    return { ok: true, value: JSON.parse(text) as T }; // caller states the expected T
  } catch {
    return { ok: false, error: "invalid json" };       // E defaults to string
  }
}

const r = wrap<Order[]>([{ id: "o1", total: 250 }]);     // ApiResponse<Order[]>
console.log(r.data[0].total);                             // typed: number

const parsed = parseJson<Order>('{"id":"o2","total":99}'); // Result<Order, string>
if (parsed.ok) console.log(parsed.value.id);               // narrowed to success branch
else console.log(parsed.error);                            // narrowed to failure branch
// Output:
// 250
// o2
```

```typescript
// Generic with a tuple return: a tiny typed "state hook" without React
function createState<T>(initial: T): [() => T, (next: T) => void] {
  let current = initial;                          // closure holds T
  return [() => current, (next) => { current = next; }]; // getter + setter typed with T
}

const [getQty, setQty] = createState(1);          // T inferred as number
setQty(3);                                        // ok
// setQty("3");                                   // would be a compile error (string not number)
console.log(getQty());
// Output:
// 3
```

---

## 🟠 Node/Express + React Integration

```typescript
import express from "express";                    // express runtime
import type { Response } from "express";          // types only

interface ApiResponse<T> { ok: boolean; data: T } // envelope
interface Order { id: string; total: number }

const app = express();

// Response<ResBody> is itself generic: 1st type argument = body type passed to res.json
app.get("/orders/:id", (_req, res: Response<ApiResponse<Order>>) => {
  res.json({ ok: true, data: { id: "o1", total: 250 } }); // body checked against ApiResponse<Order>
  // res.json({ ok: true, data: "oops" });                 // would be a compile error
});
```

```tsx
import { useState } from "react";                 // useState<S> is a generic function

interface Order { id: string; total: number }

export function OrderBox() {
  // No initial value hint for the "later" case => pass T explicitly
  const [order, setOrder] = useState<Order | null>(null); // state is Order | null
  return (
    <div>
      <button onClick={() => setOrder({ id: "o1", total: 250 })}>Load</button>
      {order ? <p>{order.id}: Rs {order.total}</p> : <p>No order</p>}
    </div>
  );
}
```

**Redux note:** `PayloadAction<T>` (Redux Toolkit) and `createSlice<State>` are generics too — `PayloadAction<Order>` says "this action's payload is an `Order`", linking reducers to action creators.

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: Passing the wrong thing for `T` or using the result as a different type.**

```typescript
// ❌ Explicit T says number, but a string is passed
class Box<T> { constructor(public value: T) {} }
const b = new Box<number>("100"); // wrong
// error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.

function first<T>(xs: T[]): T { return xs[0]; }
const n: string = first([1, 2, 3]); // wrong: T is number
// error TS2322: Type 'number' is not assignable to type 'string'.
```

```typescript
// ✅ Let inference or the explicit argument match the data
class Box<T> { constructor(public value: T) {} }
const b = new Box<number>(100); // ok
function first<T>(xs: T[]): T { return xs[0]; }
const n: number = first([1, 2, 3]); // ok
console.log(b.value + n);
// Output:
// 101
```

**Mistake 2: Using `any` instead of a type parameter.** `function first(xs: any[]): any` compiles for every misuse (`first(orders).totall`) and loses autocomplete. If the output depends on the input, you want `<T>`, not `any`.

**Mistake 3: Useless generics.** `function log<T>(x: T): void` where `T` is used only once adds nothing — use `unknown`. A type parameter should appear **at least twice** (linking two positions), otherwise it is just noise.

**Mistake 4 (TSX gotcha):** in `.tsx` files `<T>(x: T) => x` is parsed as a JSX tag. Write `<T,>(x: T) => x` or use a `function` declaration.

---

## 🧠 Tricky Interview Question

```typescript
function id<T>(x: T): T { return x; }
const a = id("a");  // type?
let b = id("a");    // type?
const t1: "a" = a;  // compiles?
b = "zzz";          // compiles?
console.log(a, b);
// Output:
// a zzz
```
**Answer:** `a` has the literal type `"a"` (a `const` keeps the narrow inferred literal), so `const t1: "a" = a` compiles. `b` is declared with `let`, so the inferred type widens to `string`, and `b = "zzz"` compiles. (Verified: assigning `a` to type `1` gives `error TS2322: Type '"a"' is not assignable to type '1'.`) Types are erased, so the output is just `a zzz`. This shows that generic inference follows the same literal-widening rules as ordinary variables.

---

## ⚫ Interview Questions + Answers

**Q1: What problem do generics solve compared to `any`?**
A1: `any` turns off checking, so the output is unrelated to the input. A generic keeps a **relationship** between types (`T` in and `T` out), so the compiler still checks every use. One implementation, many typed uses.

**Q2: Inference vs explicit type arguments — when do you need explicit?**
A2: Inference works when `T` appears in parameters. If `T` only appears in the return type (`new Map<K, V>()`, `useState<Order | null>(null)`, `JSON.parse<T>`-style helpers), TS has nothing to infer from, so specify it.

**Q3: What does `T` mean inside the function body?**
A3: An unknown type that could be anything; you can only use operations valid for all types. `x.length` on `T` is an error (`TS2339: Property 'length' does not exist on type 'T'`). Add a constraint (`T extends { length: number }`) to unlock members.

**Q4: Difference between `function f<T>(x: T)` and `function f(x: unknown)`?**
A4: `unknown` forgets the type after the call; generics remember it and can return it (`T`). Use `unknown` when you do not need the link.

**Q5: What is `<const T>` (TS 5.0)?**
A5: A modifier that makes inference behave as if arguments were written with `as const`, keeping literal/readonly tuple types: `function tuple<const T extends readonly unknown[]>(x: T): T`. Useful for route tables and config helpers. Not available before 5.0.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Output type depends on input type (`first`, `map`, `wrap`)
- Reusable containers/envelopes (`ApiResponse<T>`, `Result<T, E>`, repositories)
- React hooks and Redux helpers that must stay typed per usage

❌ Avoid when:
- The type parameter is used only once (use `unknown` or a concrete type)
- The function only ever handles one known type
- You are generic-ifying "just in case" — it makes error messages harder to read

---

## 📊 Visual Diagram
```
  function first<T>( items: T[] ): T | undefined
                     │      │            │
        call site:   │      │            └── output linked to T
   first([10, 20])   ▼      ▼
                   number[]  T = number   ──►  number | undefined
   first(["a"])             T = string   ──►  string | undefined

   interface ApiResponse<T> { ok: boolean; data: T }
   ApiResponse<Order[]>  ──►  { ok: boolean; data: Order[] }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Generic | Code parameterised by types | Types से parameterise किया code |
| Type parameter | Placeholder like `T` | `T` जैसा placeholder |
| Type argument | Actual type given: `Box<number>` | असली type जो दिया जाता है |
| Inference | Compiler deduces `T` from args | Compiler का `T` निकालना |
| Generic constraint | Limit what `T` can be (`extends`) | `T` पर सीमा लगाना |
| Type erasure | Generics vanish at runtime | Runtime पर generics गायब |

---

## ⚡ 3-Line Summary
English:
1. Generics (`<T>`) let one function/type/class work for many types while linking input and output types.
2. `T` is inferred from arguments or given explicitly (`useState<Order | null>(null)`); prefer generics over `any`.
3. Use a type parameter only when it appears at least twice; inside the body `T` is opaque until you add a constraint.

Hindi:
1. Generics (`<T>`) से एक function/type/class कई types के लिए चलता है और input व output types जुड़े रहते हैं।
2. `T` arguments से infer होता है या explicitly दिया जाता है (`useState<Order | null>(null)`); `any` की जगह generics को प्राथमिकता दो।
3. Type parameter तभी इस्तेमाल करो जब वह कम से कम दो बार आए; body में `T` तब तक अपारदर्शी है जब तक constraint न जोड़ो।

---

## ➡️ Next Topic
**42. Generic Functions** — arrow generics, multiple type parameters, inference rules, callbacks and generic function types.
