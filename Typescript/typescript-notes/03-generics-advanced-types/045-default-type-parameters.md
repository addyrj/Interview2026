# 45. Default Type Parameters
# हिंदी में: Default Type Parameters (generic का default type)

> TypeScript 5.x पर verify किया गया (`tsc --strict`, TS 5.9). Default type parameters TypeScript 2.3 से available हैं।

---

## 🔵 Simple Definition (English)
A **default type parameter** lets a generic declare a fallback type: `interface ApiResponse<T = unknown>`. If the caller does not pass `T` and TypeScript cannot infer it, the default is used. It works like default values for function arguments, but at the type level.

## 🔵 सरल परिभाषा (Hindi)
**Default type parameter** generic को एक fallback type देता है: `interface ApiResponse<T = unknown>`। अगर caller `T` नहीं देता और TypeScript infer भी नहीं कर पाता, तो default इस्तेमाल होता है। यह function arguments के default values जैसा है, बस type level पर।

---

## 🔴 Problem it Solves
Without defaults, every use of a generic type must spell out all type arguments, even when 90% of call sites use the same one. `ApiResponse<unknown>` everywhere is noisy. Also, when you add a new type parameter to a widely used type, every existing usage breaks with `TS2314: Generic type requires 1 type argument(s)`. A default makes the new parameter backward compatible.

## 🔴 यह क्यों बना? (Hindi)
Defaults के बिना हर जगह सारे type arguments लिखने पड़ते हैं, चाहे 90% call sites में same type हो। `ApiResponse<unknown>` बार-बार लिखना बेकार है। और अगर किसी पुराने, बहुत use होने वाले type में नया type parameter जोड़ो, तो हर पुराना usage टूट जाता है (`TS2314`)। Default लगाने से नया parameter backward compatible हो जाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Write the default after `=` in the type parameter list: `<T = string>`.
Step 2 → If the caller passes an explicit argument, it wins: `Box<number>`.
Step 3 → If the caller writes just `Box` (a generic type with all-default params), the default is used: `Box` means `Box<string>`.
Step 4 → For generic **functions**, inference runs first. The default is only a fallback when there is no inference candidate.
Step 5 → Rule: parameters with defaults must come **after** required ones. A default can reference earlier parameters: `<T, K extends keyof T = keyof T>`.
Step 6 → A default must satisfy the constraint: `<T extends object = {}>` is fine, `<T extends object = string>` is an error.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `=` के बाद default लिखो: `<T = string>`।
Step 2 → Caller explicit argument दे तो वही चलता है: `Box<number>`।
Step 3 → Caller सिर्फ `Box` लिखे (सारे params default वाले हों), तो default लगता है: `Box` मतलब `Box<string>`।
Step 4 → Generic **functions** में पहले inference चलता है। Default सिर्फ तब काम आता है जब inference का कोई candidate न मिले।
Step 5 → Rule: default वाले parameters हमेशा required parameters के **बाद** आते हैं। Default पिछले parameter को refer कर सकता है: `<T, K extends keyof T = keyof T>`।
Step 6 → Default को constraint satisfy करना होगा: `<T extends object = string>` error है।

---

## 🟡 Real World Example
**Razorpay's** API wrapper returns `{ status, data, error }` for every call. Most helper functions (health checks, webhooks ping) do not care about the payload shape, so `data` is `unknown`. Only the order-create call returns a typed `Order`. With `ApiResponse<T = unknown>`, the generic helper just says `ApiResponse` and the order call says `ApiResponse<Order>`. Similarly a Redux `Action<P = void>` lets "logout" actions carry no payload while "addToCart" carries `CartItem`.

## 🟡 Real Example Hindi mein
**Razorpay** का API wrapper हर call पर `{ status, data, error }` लौटाता है। ज़्यादातर helpers (health check, webhook ping) को payload से मतलब नहीं, तो `data` `unknown` रहता है। सिर्फ order-create call typed `Order` लौटाती है। `ApiResponse<T = unknown>` से generic helper सिर्फ `ApiResponse` लिखता है और order call `ApiResponse<Order>`। ऐसे ही Redux में `Action<P = void>`: logout action में payload नहीं, addToCart में `CartItem`।

---

## 💻 Code Example — Basic

```typescript
// Default type parameter: T falls back to unknown when not supplied
interface ApiResponse<T = unknown> {
  status: number; // HTTP status code
  data: T; // payload, typed by T
}

// Uses the default: data is unknown
const ping: ApiResponse = { status: 200, data: "pong" };

// Explicit argument overrides the default
interface Order {
  id: string; // order id
  amount: number; // amount in paise
}
const created: ApiResponse<Order> = { status: 201, data: { id: "ord_1", amount: 49900 } };

// data is unknown, so we must narrow before use
if (typeof ping.data === "string") {
  console.log(ping.data.toUpperCase()); // OK after narrowing
}
console.log(created.data.amount); // typed: number

// Defaults can reference earlier params and be combined with constraints
type Getter<T, K extends keyof T = keyof T> = (obj: T) => T[K];
const getAny: Getter<Order> = (o) => o.id; // K defaults to "id" | "amount"
console.log(getAny({ id: "ord_2", amount: 100 })); // ord_2
```

```typescript
// Function inference beats the default; the default is the fallback
function makeList<T = string>(...items: T[]): T[] {
  return items; // returns the same items typed as T[]
}

const a = makeList(1, 2, 3); // T inferred as number (inference wins)
const b = makeList(); // no candidates -> default string is used
const c = makeList<boolean>(true); // explicit wins

// Hover types (verified with tsc):
const checkA: number[] = a; // OK
const checkB: string[] = b; // OK, default kicked in
const checkC: boolean[] = c; // OK
console.log(a, b, c); // [ 1, 2, 3 ] [] [ true ]
```

## 💻 Code Example — Advanced

```typescript
// Advanced: Redux-style Action with a defaulted payload, plus a defaulted error type
interface Action<Type extends string = string, Payload = void> {
  type: Type; // action discriminator
  payload: Payload; // void when action has no payload
}

// Helper that builds action creators; Payload defaults to void
function createAction<Type extends string, Payload = void>(type: Type) {
  // returns a function; when Payload is void the arg is optional
  return (...args: Payload extends void ? [] : [payload: Payload]): Action<Type, Payload> => ({
    type,
    payload: args[0] as Payload, // cast: runtime has either 0 or 1 args
  });
}

interface CartItem {
  sku: string; // product id
  qty: number; // quantity
}

const logout = createAction("auth/logout"); // Payload = void
const addToCart = createAction<"cart/add", CartItem>("cart/add"); // explicit payload

console.log(logout()); // no args needed
console.log(addToCart({ sku: "BIRYANI-1", qty: 2 })); // payload required

// Result<T, E = Error>: most functions fail with Error, some with custom codes
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };

function parseQty(raw: string): Result<number> {
  const n = Number(raw); // convert string to number
  return Number.isInteger(n) && n > 0 ? { ok: true, value: n } : { ok: false, error: new Error("bad qty") };
}

class PaymentError extends Error {
  constructor(public code: "DECLINED" | "TIMEOUT") {
    super(code); // pass code as message
  }
}
type PayResult = Result<{ txnId: string }, PaymentError>; // override E
const failed: PayResult = { ok: false, error: new PaymentError("DECLINED") };
console.log(parseQty("3"), failed.ok); // { ok: true, value: 3 } false
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: a typed JSON helper where body type defaults to unknown
import express, { type Response } from "express";

interface Envelope<T = null> {
  success: boolean; // true if request worked
  data: T; // payload (null by default for no-body responses)
  message?: string; // optional human message
}

// Generic sender: T defaults to null, so send(res) works for 204-like replies
function send<T = null>(res: Response, body: Envelope<T>, status = 200): void {
  res.status(status).json(body); // writes JSON
}

const app = express();
app.get("/health", (_req, res) => {
  send(res, { success: true, data: null }); // T inferred as null
});
app.get("/orders/:id", (req, res) => {
  send(res, { success: true, data: { id: req.params.id, total: 499 } }); // T inferred as object
});
```

```tsx
// React: component props with a defaulted generic for the row type
import { useState } from "react";

interface ListProps<Row = { id: string; label: string }> {
  rows: Row[]; // list data
  render?: (row: Row) => string; // optional custom renderer
}

// Default Row works with plain {id,label} lists; other shapes pass Row explicitly
function SimpleList<Row = { id: string; label: string }>({ rows, render }: ListProps<Row>) {
  const [count] = useState(rows.length); // count of rows
  return (
    <ul data-count={count}>
      {rows.map((r, i) => (
        <li key={i}>{render ? render(r) : JSON.stringify(r)}</li>
      ))}
    </ul>
  );
}

export function Demo() {
  return <SimpleList rows={[{ id: "1", label: "Dal Makhani" }]} />; // Row inferred
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Required parameter after an optional (defaulted) one
```typescript
// ❌ Wrong
type Pair<A = string, B> = [A, B];
// error TS2706: Required type parameters may not follow optional type parameters.

// ✅ Right: required first, defaulted after
type PairOk<B, A = string> = [A, B];
```

❌ Mistake 2: Default that violates the constraint
```typescript
// ❌ Wrong
interface Repo<T extends { id: number } = { name: string }> { get(id: number): T }
// error TS2344: Type '{ name: string; }' does not satisfy the constraint '{ id: number; }'.

// ✅ Right
interface RepoOk<T extends { id: number } = { id: number }> { get(id: number): T }
```

❌ Mistake 3: Thinking the default beats inference
```typescript
function wrap<T = string>(x?: T): T | undefined { return x; }
const w = wrap(42); // T is number, NOT string; default is used only with no candidates
```

---

## 🧠 Tricky Interview Question

```typescript
declare function create<T = string>(init?: T): T[];

const x = create();
const y = create(5);
const z = create<number>();
```
**What are the types of `x`, `y`, `z`?**

Answer: `x: string[]` (no inference candidate, so the default applies), `y: number[]` (inference from the argument wins over the default), `z: number[]` (explicit argument). Interviewers use this to check that you know **inference > default**, and that default is a fallback, not a forced type.

---

## ⚫ Interview Questions + Answers

Q1: What is a default type parameter and what is its syntax?
A1: A fallback type for a generic parameter, written `<T = Default>`. It is used when the caller does not supply `T` and inference has no candidate. It exists on interfaces, type aliases, classes and functions.

Q2: In what order must type parameters with defaults appear?
A2: After all required ones (TS2706 otherwise). Later defaults may reference earlier parameters, e.g. `<T, K extends keyof T = keyof T>`.

Q3: Why add a default when extending a public generic type?
A3: Backward compatibility. Existing code writes `Store<State>`; if you add `Store<State, Ext>` with no default, every usage fails with TS2314. With `Ext = {}` or `unknown`, old code still compiles. Redux Toolkit's `configureStore` generics use this idea heavily.

Q4: Does the default override inference in generic functions?
A4: No. Inference runs first; the default is used only if no candidates exist. `makeList(1,2)` is `number[]` even with `<T = string>`.

Q5: What is a good default for "unknown payload": `any` or `unknown`?
A5: `unknown`. It forces consumers to narrow, so it is type safe. `any` silently disables checking. Only use `any` as a default in rare cases like function-parameter positions where contravariance requires it (e.g. `(...args: any[]) => any` in constraints).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Most call sites use one type (envelope `T = unknown`, `Result<T, E = Error>`)
- You are evolving a public generic and must not break users
- You want shorter signatures in React props (`Props<T = DefaultRow>`)

❌ Avoid when:
- The type argument should be inferred anyway (the default hides missing info)
- A wrong silent fallback would hide a bug; prefer making the parameter required

---

## 📊 Visual Diagram
```
  Box<T = string>

  Box<number>  ──► explicit  ──► T = number
  Box          ──► omitted   ──► T = string   (default)

  function f<T = string>(x?: T)
  f(5)   ──► inference candidate number ──► T = number
  f()    ──► no candidate ──► default     ──► T = string

  Priority:  explicit  >  inference  >  default  >  constraint (if no default)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Default type parameter | Fallback type `<T = X>` | Type parameter का default |
| Inference | Compiler deduces T from args | Compiler का T अपने आप समझना |
| Constraint | `extends` limit on T | T पर सीमा |
| Backward compatible | Old code still compiles | पुराना code चलता रहे |
| TS2706 | Required param after optional | Required param default के बाद आया |

---

## ⚡ 3-Line Summary
English:
1. `<T = X>` gives a generic a fallback type used only when T is neither given nor inferred.
2. Defaulted params go last, must satisfy constraints, and make new generics backward compatible.
3. Priority is explicit argument, then inference, then default.

Hindi:
1. `<T = X>` generic को fallback type देता है, जो तभी लगता है जब T न दिया गया हो न infer हुआ हो।
2. Default वाले params आखिर में आते हैं, constraint satisfy करने होते हैं, और नए generics को backward compatible बनाते हैं।
3. Priority: explicit argument, फिर inference, फिर default।

---

## ➡️ Next Topic
**46. keyof with Generics** — `K extends keyof T` से type-safe property access (`getProp`, `pluck`) कैसे बनता है।
