# 9. Type Inference
# हिंदी में: Type Inference (TypeScript खुद type पहचानना)

> Version note: **TypeScript 5.x** (5.9.3 पर verify)। Inferred type predicates TS 5.5+, `const` type parameters TS 5.0+, `NoInfer` TS 5.4+, `satisfies` TS 4.9+।

---

## 🔵 Simple Definition (English)
**Type inference** is TypeScript working out types **without you writing them**. The compiler looks at initial values (`const n = 5` → `number`), return statements, how a value is used, and the **context** it appears in (a callback passed to `.map` gets its parameter type from the array). You annotate only where inference cannot see enough: function parameters, empty containers, and public API boundaries.

## 🔵 सरल परिभाषा (Hindi)
**Type inference** यानी TypeScript का types **बिना आपके लिखे** पहचान लेना। Compiler शुरुआती values (`const n = 5` → `number`), return statements, value के इस्तेमाल और उस **context** को देखता है जहाँ वह आई है (`.map` में दिए callback का parameter type array से मिलता है)। आप सिर्फ वहाँ annotate करते हैं जहाँ inference को काफ़ी जानकारी नहीं मिलती: function parameters, खाली containers और public API boundaries।

---

## 🔴 Problem it Solves
If every variable needed a written type, TypeScript would feel like Java in 2005: `const items: Array<{ sku: string; qty: number }> = ...` everywhere. Inference gives type safety **with JavaScript-like code**. The flip side: engineers who do not understand inference get surprised by *widening* (`"PLACED"` becoming `string`), `never[]`, and over-wide return types that leak through function boundaries. Knowing the rules tells you exactly where to add an annotation.

## 🔴 यह क्यों बना? (Hindi)
अगर हर variable का type लिखना पड़ता तो TypeScript 2005 के Java जैसा लगता: हर जगह `const items: Array<{ sku: string; qty: number }> = ...`। Inference JavaScript जैसे code में ही type safety दे देता है। उल्टा पहलू: जो engineers inference के नियम नहीं समझते उन्हें *widening* (`"PLACED"` का `string` बन जाना), `never[]` और function boundaries से बाहर निकलते बहुत चौड़े return types चौंकाते हैं। नियम जानने से पता चलता है कि annotation ठीक कहाँ लगाना है।

---

## 🟢 How it Works — Step by Step

Step 1 → **Initializer inference:** `let n = 5` → `number`; `const n = 5` → literal `5`. `let s = "a"` → `string`; `const s = "a"` → `"a"`.
Step 2 → **Widening:** mutable positions (`let`, object properties, array elements) widen literals to their base type (`string`, `number`). `as const` or an annotation stops it.
Step 3 → **Best common type:** `[1, "a"]` → `(string | number)[]`; `[1, 2]` → `number[]`; object literal → structural type `{ id: number; name: string }`.
Step 4 → **Return type inference:** the function's return type is the union of all `return` expressions. Great for private helpers; for exported APIs annotate it so the contract doesn't change accidentally.
Step 5 → **Contextual typing:** when a function expression is passed where a function type is expected, its parameters get types from that context: `orders.filter(o => o.paid)` → `o: Order`.
Step 6 → **Generic inference:** `identity(5)` infers `T = number`; `useState(0)` infers `number`; `useState<string | null>(null)` needs help because `null` alone infers `null`.
Step 7 → **Control-flow analysis:** `let x: string | number`; after `x = "a"` TS knows it is `string` until the next assignment. Narrowing uses the same engine (topic 025).
Step 8 → Where inference **fails** (→ `any` error under `noImplicitAny`): untyped function parameters (not contextual), `let x;` (evolving any), `[]` / `{}` literals you later fill.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Initializer inference:** `let n = 5` → `number`; `const n = 5` → literal `5`। `let s = "a"` → `string`; `const s = "a"` → `"a"`।
Step 2 → **Widening:** mutable जगहों (`let`, object properties, array elements) पर literals अपने base type (`string`, `number`) में widen हो जाते हैं। `as const` या annotation इसे रोकता है।
Step 3 → **Best common type:** `[1, "a"]` → `(string | number)[]`; `[1, 2]` → `number[]`; object literal → structural type `{ id: number; name: string }`।
Step 4 → **Return type inference:** function का return type सारे `return` expressions का union होता है। private helpers के लिए बढ़िया; exported APIs में annotate करो ताकि contract गलती से न बदले।
Step 5 → **Contextual typing:** जब function expression ऐसी जगह दिया जाए जहाँ function type अपेक्षित है, तो उसके parameters को context से types मिलते हैं: `orders.filter(o => o.paid)` → `o: Order`।
Step 6 → **Generic inference:** `identity(5)` से `T = number`; `useState(0)` से `number`; `useState<string | null>(null)` में मदद चाहिए क्योंकि अकेला `null` बस `null` infer होता है।
Step 7 → **Control-flow analysis:** `let x: string | number`; `x = "a"` के बाद अगले assignment तक TS जानता है कि वह `string` है। Narrowing भी इसी engine से होती है (topic 025)।
Step 8 → जहाँ inference **फेल** होता है (`noImplicitAny` में `any` error): बिना type के function parameters (contextual नहीं हों तो), `let x;` (evolving any), और बाद में भरे जाने वाले `[]` / `{}` literals।

---

## 🟡 Real World Example
**A React + Redux Toolkit checkout:** `const dispatch = useAppDispatch()` and `const items = useAppSelector(s => s.cart.items)` — no annotations in the component; the types flow from `RootState` through the typed hooks. `items.map(i => i.pricePaise)` — `i` is inferred as `CartItem`. In the Express layer, `const total = items.reduce((s, i) => s + i.qty * i.pricePaise, 0)` is `number` without a single annotation. The senior skill: knowing the **three places to annotate** — function parameters, exported return types, and `useState` with `null`/empty initial values.

## 🟡 Real Example Hindi mein
**React + Redux Toolkit checkout:** `const dispatch = useAppDispatch()` और `const items = useAppSelector(s => s.cart.items)` — component में कोई annotation नहीं; types `RootState` से typed hooks के रास्ते बहकर आते हैं। `items.map(i => i.pricePaise)` में `i` का type `CartItem` infer होता है। Express layer में `const total = items.reduce((s, i) => s + i.qty * i.pricePaise, 0)` बिना एक भी annotation के `number` है। Senior की कला: **annotation के तीन ठिकाने** जानना — function parameters, exported return types, और `null`/खाली initial value वाला `useState`।

---

## 💻 Code Example — Basic

```typescript
// inference-basic.ts — hover each variable in your editor to see the inferred type

let count = 3;                      // number (widened, because let)
const label = "Cart";               // "Cart"  (literal, because const)
const flags = [true, false];        // boolean[]
const mixed = [1, "a"];             // (string | number)[]
const order = { id: "SW-1", qty: 2, paid: false }; // { id: string; qty: number; paid: boolean }

// Return type is inferred from the return expression: number
function totalPaise(qty: number, unitPaise: number) {
  return qty * unitPaise;
}
const t = totalPaise(2, 19900);     // number
console.log(count, label, flags.length, mixed.length, order.id, t);

// Contextual typing: `o` gets its type from the array element type, no annotation needed
const orders = [
  { id: "A", paid: true, amountPaise: 100 },
  { id: "B", paid: false, amountPaise: 250 },
];
const unpaid = orders.filter((o) => !o.paid);                   // o inferred; result same element type
const ids = unpaid.map((o) => o.id.toLowerCase());              // string[]
console.log(ids);                                               // [ 'b' ]

// Output:
// 3 Cart 2 2 SW-1 39800
// [ 'b' ]
```

```typescript
// ❌ intentional errors — real tsc 5.9 output
let count = 3;
count = "three";
// error TS2322: Type 'string' is not assignable to type 'number'.

// no context, no initializer => implicit any
const double = (x) => x * 2;
// error TS7006: Parameter 'x' implicitly has an 'any' type.

// widening trap: the object property widens "PLACED" to string
type Status = "PLACED" | "DELIVERED";
function setStatus(s: Status): void { console.log(s); }
const o = { status: "PLACED" };
setStatus(o.status);
// error TS2345: Argument of type 'string' is not assignable to parameter of type 'Status'.
```

## 💻 Code Example — Advanced

```typescript
// inference-advanced.ts — widening fixes, const type params, return inference, evolving any

// 1) Three ways to stop widening
type Status = "PLACED" | "DELIVERED";
function setStatus(s: Status): string { return `status=${s}`; }

const a = { status: "PLACED" as const };                  // fix 1: as const on the value
const b = { status: "PLACED" } as const;                  // fix 2: freeze whole object (readonly)
const c: { status: Status } = { status: "PLACED" };       // fix 3: annotate target
const d = { status: "PLACED" } satisfies { status: Status }; // fix 4: satisfies checks shape AND keeps "PLACED"
console.log(setStatus(a.status), setStatus(b.status), setStatus(c.status));
console.log(typeof d.status);                             // string (runtime always string)

// 2) Return types are unions of all returns — explicit annotation guards the contract
function discount(code: string) {
  if (code === "WELCOME") return 5000;                    // number
  if (code === "FREE") return "FREE_DELIVERY";            // string
  return null;                                            // null
}
const dres = discount("X");                               // string | number | null
console.log(dres);                                        // null

// 3) Generic inference: arguments drive T; `const` type parameter (TS 5.0) keeps literals
function pick<T>(v: T): T { return v; }
const p1 = pick("PLACED");                                // "PLACED" (T inferred as literal for primitives in const-ish context)
const p2 = pick({ k: 1 });                                // { k: number }
function pickConst<const T>(v: T): T { return v; }
const p3 = pickConst({ k: 1, tags: ["a"] });              // { readonly k: 1; readonly tags: readonly ["a"] }
console.log(p1, p2.k, p3.tags[0]);                        // PLACED 1 a

// 4) Evolving types with control flow (let with no annotation and no initial value)
let result;                                               // implicit "evolving any" — allowed, tracked
result = 100;                                             // now number
console.log(result.toFixed(1));                           // 100.0 (TS knows it is number here)
result = "done";                                          // now string
console.log(result.toUpperCase());                        // DONE

// 5) Inferred type predicate (TS 5.5+): no need to write `x is string`
const raw: (string | null)[] = ["a", null, "b"];
const clean = raw.filter((x) => x !== null);              // string[] in TS 5.5+, (string|null)[] before
console.log(clean.map((s) => s.toUpperCase()).join(""));  // AB

// 6) typeof / ReturnType reuse inferred types instead of rewriting them
const defaultOrder = { id: "SW-0", totalPaise: 0, items: [] as string[] };
type OrderShape = typeof defaultOrder;                    // { id: string; totalPaise: number; items: string[] }
const copy: OrderShape = { ...defaultOrder, id: "SW-1" };
console.log(copy.id);                                     // SW-1

// Output:
// status=PLACED status=PLACED status=PLACED
// string
// null
// PLACED 1 a
// 100.0
// DONE
// AB
// SW-1
```

Note on fix 4 (verified): with `satisfies { status: Status }` the property type of `d.status` stays the literal `"PLACED"` (the contextual type contains literals), so `setStatus(d.status)` compiles too. That is the main reason to prefer `satisfies` over an annotation: the shape is checked, but the specific type is kept (an annotation like fix 3 would widen `c.status` to the whole `Status` union).

---

## 🟠 Node/Express + React Integration

**Express — let inference flow from a typed service function:**

```typescript
// inference-express.ts
import express from "express";

// Annotate the PARAMETER and (for exported APIs) the RETURN type — everything else is inferred
interface CartItem { sku: string; qty: number; pricePaise: number }
export function cartTotal(items: CartItem[]): number {
  return items.reduce((sum, i) => sum + i.qty * i.pricePaise, 0);   // sum: number, i: CartItem
}

const app = express();
app.use(express.json());
app.get("/total", (_req, res) => {                                  // _req, res inferred from express route typings
  const items = [{ sku: "PIZZA", qty: 2, pricePaise: 19900 }];      // shape inferred
  res.json({ totalPaise: cartTotal(items) });                       // items matches CartItem[] structurally
});
export default app;
```

**React — where inference needs help: `useState(null)`:**

```tsx
// Profile.tsx
import { useEffect, useState } from "react";

type User = { id: number; name: string };

export function Profile() {
  const [count, setCount] = useState(0);              // number (inferred from 0)
  const [user, setUser] = useState<User | null>(null); // must annotate: null alone infers `null`
  useEffect(() => {
    setUser({ id: 1, name: "Aditya" });               // OK because of the generic above
    setCount((c) => c + 1);                           // c inferred as number
  }, []);
  return <p>{user ? user.name : "loading"} {count}</p>;
}
```
Redux Toolkit: `createSlice({ name, initialState, reducers })` infers the whole state type from `initialState` — define it with an annotation (`const initialState: CartState = ...`) when it contains empty arrays or `null` (topic 094).

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Letting `useState([])` / `useState(null)` infer `never[]` / `null`
```typescript
// ❌ Wrong — what the compiler thinks `const [user] = useState(null)` is
let user = null as null;
user = { id: 1 };
// error TS2322: Type '{ id: number; }' is not assignable to type 'null'.
```
✅ Correct: `useState<User | null>(null)` and `useState<CartItem[]>([])`.

❌ Mistake 2: Relying on inferred return type of a public function
```typescript
// ⚠️ Wrong-ish — return type silently changes to string | number | null when someone edits a branch
export function discount(code: string) {
  return code === "WELCOME" ? 5000 : null;
}
// ✅ Right — annotate exported functions so callers are protected
export function discount2(code: string): number | null {
  return code === "WELCOME" ? 5000 : null;
}
```

❌ Mistake 3: Annotating with a wider type than the value and losing information
```typescript
// ⚠️ Wrong-ish — annotation widens: you lose the literal / tuple type
const roles: string[] = ["admin", "user"];       // can't derive union from this
// ✅ Right — keep the precise type
const ROLES = ["admin", "user"] as const;
type Role = (typeof ROLES)[number];              // "admin" | "user"
const r: Role = "admin";
console.log(r);
```

❌ Mistake 4: Fighting inference with `as` assertions everywhere (topic 020) — usually a sign the types upstream need fixing.

---

## 🧠 Tricky Interview Question

```typescript
const a = "x";
let b = "x";
const c = { v: "x" };
const d = ["x"] as const;
// Types of a, b, c.v, d ?
```
**Answer:** `a: "x"`, `b: string`, `c: { v: string }` (property is mutable so the literal widens), `d: readonly ["x"]`. Follow-up: `function f(v: "x") {}`; `f(a)` OK, `f(b)` ❌, `f(c.v)` ❌, `f(d[0])` OK. The rule: **literal types survive only in immutable positions** (`const` primitives, `as const`, or when a contextual type asks for the literal).

```typescript
// verified output of the follow-up
function f(v: "x"): void {}
const a = "x";
let b = "x";
const c = { v: "x" };
const d = ["x"] as const;
f(a);      // OK
f(b);      // ❌ error TS2345: Argument of type 'string' is not assignable to parameter of type '"x"'.
f(c.v);    // ❌ error TS2345: Argument of type 'string' is not assignable to parameter of type '"x"'.
f(d[0]);   // OK
```

---

## ⚫ Interview Questions + Answers

Q1: What are the main kinds of inference TypeScript does?
A1: Initializer (variable from its value), return-type, contextual (from where a function/literal is used), generic argument inference (`T` from arguments), and control-flow based narrowing/assignment analysis.

Q2: When should I explicitly annotate?
A2: Function parameters (no context), exported function return types, class properties, empty `[]`/`null` initial values (`useState`), and when you want a wider/narrower type than the initializer gives. Otherwise prefer inference to avoid duplication.

Q3: What is widening and how do you control it?
A3: A literal type from a mutable location is replaced by its base type (`"a"` → `string`). Prevent with `as const`, a literal-containing contextual type/annotation, `satisfies`, or `const` type parameters (TS 5.0).

Q4: What is contextual typing?
A4: Types flowing *into* an expression from where it's used: arrow function parameters in `.map`, event handlers (`onClick={(e) => ...}` gives `e` a `MouseEvent`), `Promise.then` callbacks. It is why callbacks rarely need annotations.

Q5: What does `noImplicitAny` do with inference?
A5: If inference can't determine a type and falls back to `any` (untyped param, evolving `let` that can't be resolved), `noImplicitAny` (part of `strict`) reports an error (TS7006, TS7034). It forces explicit annotations only at the necessary places.

---

## 🔷 When to Use + When Not to Use
✅ Rely on inference for: local variables, `const` values, callbacks, array method chains, private helpers, generic calls.
✅ Add annotations for: function parameters, exported APIs, `useState<T | null>`, `createSlice` `initialState`, and complex literals you want checked.

❌ Don't over-annotate (`const n: number = 5`) or under-annotate public contracts (inferred return type leaking an internal union). Don't use `as` to silence inference problems.

---

## 📊 Visual Diagram
```
   VALUE / CONTEXT                    INFERRED TYPE
 ──────────────────────────────────────────────────────────
 const a = "x"                  ──►  "x"                (literal)
 let   b = "x"                  ──►  string             (widened)
 const c = { v: "x" }           ──►  { v: string }      (property widened)
 const d = ["x"] as const       ──►  readonly ["x"]     (frozen)
 [1, "a"]                       ──►  (string | number)[]
 orders.map(o => o.id)          ──►  o: Order           (contextual)
 useState(null)                 ──►  null   ✋ annotate: useState<User | null>(null)
 function f(x) {}               ──►  ❌ implicit any
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Type inference | Compiler deduces types | Compiler खुद types निकालता है |
| Widening | Literal → base type in mutable spot | Literal का base type बन जाना |
| Contextual typing | Type from the surrounding usage | आस-पास के इस्तेमाल से type |
| Best common type | Union/shared type of array elements | Array elements का साझा/union type |
| Control-flow analysis | Tracks types through branches/assignments | Branches और assignments में type track करना |
| Evolving any | `let x;` type changes as assigned | `let x;` का type assign के साथ बदलना |
| noImplicitAny | Error when inference gives `any` | Inference `any` दे तो error |

---

## ⚡ 3-Line Summary
English:
1. TS infers types from initializers, return statements, context, generics and control flow — you annotate only the gaps.
2. `const` keeps literals, `let`/object properties widen them; `as const`, annotations or `satisfies` control that.
3. Always annotate parameters, exported return types, and `useState`/empty-container initial values.

Hindi:
1. TS types को initializers, return statements, context, generics और control flow से infer करता है — आप सिर्फ़ खाली जगह annotate करते हैं।
2. `const` literals रखता है, `let`/object properties उन्हें widen करते हैं; `as const`, annotation या `satisfies` से इसे control करो।
3. Parameters, exported return types और `useState`/खाली containers की initial values हमेशा annotate करो।

---

## ➡️ Next Topic
**010. Union Types** — `A | B`, narrowing a union, and modelling "one of several" values.
