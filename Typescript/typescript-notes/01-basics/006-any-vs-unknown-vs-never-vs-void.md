# 6. any vs unknown vs never vs void
# हिंदी में: any, unknown, never और void में अंतर

> Version note: **TypeScript 5.x** (5.9.3 पर verify)। `useUnknownInCatchVariables` (4.4+) `strict` में शामिल है।

---

## 🔵 Simple Definition (English)
These four are TypeScript's **special types**:
- **`any`** — "turn the type checker off". Anything goes in, anything comes out.
- **`unknown`** — the **type-safe `any`**: can hold any value, but you must **narrow** it before using it. It is the *top type*.
- **`never`** — the type of values that **never happen** (a function that always throws, an impossible branch). It is the *bottom type*: assignable to everything, nothing assignable to it.
- **`void`** — "this function returns no useful value". It is used for return types of functions whose result is ignored.

## 🔵 सरल परिभाषा (Hindi)
ये चारों TypeScript के **खास types** हैं:
- **`any`** — "type checker बंद कर दो"। कुछ भी अंदर, कुछ भी बाहर।
- **`unknown`** — **type-safe `any`**: कोई भी value रख सकता है, लेकिन इस्तेमाल से पहले उसे **narrow** करना पड़ता है। यह *top type* है।
- **`never`** — उन values का type जो **कभी होती ही नहीं** (जो function हमेशा throw करे, कोई असंभव branch)। यह *bottom type* है: हर type में assign हो सकता है, पर इसमें कुछ assign नहीं होता।
- **`void`** — "यह function कोई काम की value नहीं लौटाता"। जिन functions का result ignore होता है उनके return type में लिखते हैं।

---

## 🔴 Problem it Solves
Real programs deal with data of unknown shape: `JSON.parse`, `req.body`, `catch (e)`, third-party callbacks, `localStorage`. Before `unknown` (TS 3.0), people used `any` for these — which silently disabled checking and spread like a virus (`any` infects everything it touches). `unknown` forces a runtime check before use. `never` lets the compiler **prove** that a `switch` handled every case of a union, so adding a new `OrderStatus` produces a compile error exactly where you forgot to handle it. `void` documents "no result" so you cannot accidentally use the return value.

## 🔴 यह क्यों बना? (Hindi)
असली programs में ऐसा data आता है जिसका shape पता नहीं होता: `JSON.parse`, `req.body`, `catch (e)`, third-party callbacks, `localStorage`। `unknown` (TS 3.0) से पहले लोग इनके लिए `any` लगाते थे — जो चुपचाप checking बंद कर देता है और virus की तरह फैलता है (`any` जिसे छूता है उसे भी `any` बना देता है)। `unknown` इस्तेमाल से पहले runtime check ज़रूरी कर देता है। `never` compiler को **साबित** करने देता है कि `switch` ने union का हर case संभाला; नया `OrderStatus` जुड़ते ही ठीक उसी जगह compile error आता है जहाँ handle करना भूले। `void` बताता है "कोई result नहीं" ताकि return value गलती से इस्तेमाल न हो।

---

## 🟢 How it Works — Step by Step

Step 1 → `any`: assignable **to and from** every type; property access, calls, arithmetic — all unchecked. Turns `noImplicitAny` errors off when you write it explicitly.
Step 2 → `unknown`: anything is assignable **to** `unknown`, but `unknown` is assignable only to `unknown` and `any`. To use it: `typeof`, `instanceof`, `in`, a type guard, or an assertion.
Step 3 → `never`: no value exists. Functions that `throw` or loop forever are inferred `never`. After narrowing away all union members, the leftover variable is `never`.
Step 4 → `void`: a function with no `return` has return type `void`. A **callback** typed `() => void` may still return something (the value is ignored) — this is intentional, so `arr.forEach(x => list.push(x))` works.
Step 5 → `void` vs `undefined`: `undefined` is a real value type; `void` means "the caller must not use the result". With explicit `undefined` return type you must `return undefined`.

Ranking (top to bottom): `unknown` (accepts all) → everything → `never` (accepts none). `any` is outside this lattice: it is both top and bottom, which is why it is dangerous.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `any`: हर type में **और से** assign हो सकता है; property access, calls, arithmetic — कुछ भी checked नहीं। साफ़ लिखने पर `noImplicitAny` के errors भी बंद।
Step 2 → `unknown`: कुछ भी `unknown` में assign हो सकता है, पर `unknown` सिर्फ `unknown` और `any` में assign होता है। इस्तेमाल के लिए: `typeof`, `instanceof`, `in`, type guard, या assertion।
Step 3 → `never`: कोई value नहीं होती। जो functions `throw` करें या हमेशा loop करें उन्हें `never` infer होता है। Union के सारे members narrow करके हटाने पर बचा variable `never` होता है।
Step 4 → `void`: बिना `return` वाले function का return type `void`। `() => void` type का **callback** कुछ लौटा भी सकता है (value ignore होती है) — यह जानबूझकर है ताकि `arr.forEach(x => list.push(x))` चले।
Step 5 → `void` बनाम `undefined`: `undefined` असली value type है; `void` का मतलब "caller result इस्तेमाल न करे"। साफ़ `undefined` return type हो तो `return undefined` लिखना पड़ेगा।

क्रम (ऊपर से नीचे): `unknown` (सब लेता है) → बाकी सब → `never` (कुछ नहीं लेता)। `any` इस lattice से बाहर है: वह top भी है और bottom भी, इसलिए खतरनाक है।

---

## 🟡 Real World Example
**Razorpay webhook handler:** the HTTP body of `/webhook` is untrusted — typed `unknown`. The handler narrows it to `{ event: "payment.captured"; payload: ... }` using a guard or Zod. In the `catch` block, `err` is `unknown` (strict), so the code checks `err instanceof Error` before reading `err.message`. A `switch (event.type)` over `"payment.captured" | "payment.failed" | "refund.created"` ends with `default: assertNever(event)` — when Razorpay adds `"dispute.created"`, the build fails until it is handled. And `logAudit(): void` is a fire-and-forget logger.

## 🟡 Real Example Hindi mein
**Razorpay webhook handler:** `/webhook` की HTTP body untrusted है — type `unknown`। Handler उसे guard या Zod से `{ event: "payment.captured"; payload: ... }` में narrow करता है। `catch` block में `err` `unknown` है (strict), इसलिए `err.message` पढ़ने से पहले `err instanceof Error` check होता है। `"payment.captured" | "payment.failed" | "refund.created"` पर `switch (event.type)` का अंत `default: assertNever(event)` से होता है — Razorpay `"dispute.created"` जोड़े तो build तब तक fail रहेगा जब तक उसे handle न करें। और `logAudit(): void` एक fire-and-forget logger है।

---

## 💻 Code Example — Basic

```typescript
// special-types-basic.ts — any, unknown, never, void side by side

// any: no checks at all (AVOID)
let a: any = "SW-101";          // holds a string now
a = 49950;                      // now a number, no complaint
// a.toUpperCase();            // WOULD compile with any, but crashes at runtime: TypeError: a.toUpperCase is not a function

// unknown: accepts anything, but forces you to check before use
let u: unknown = "SW-101";      // holds a string
if (typeof u === "string") {    // typeof narrows unknown -> string
  console.log(u.toUpperCase()); // SW-101 (safe now)
}

// void: function that returns no useful value
function logOrder(id: string): void {
  console.log(`order ${id} logged`); // side effect only
}
logOrder("SW-101");

// never: function that never returns normally
function fail(message: string): never {
  throw new Error(message);     // always throws -> return type never
}

// Using never to get a safe fallback value
const getOrFail = (v: string | undefined): string => v ?? fail("value missing");
console.log(getOrFail("ok"));   // ok

// Output:
// SW-101
// order SW-101 logged
// ok
```

```typescript
// ❌ intentional errors — real tsc 5.9 output
let u: unknown = "hello";
u.toUpperCase();
// error TS18046: 'u' is of type 'unknown'.

const n: number = u;
// error TS2322: Type 'unknown' is not assignable to type 'number'.

function onlyThrow(): never {
  return 5;
}
// error TS2322: Type '5' is not assignable to type 'never'.

const x: never = "a" as string;
// error TS2322: Type 'string' is not assignable to type 'never'.
```

## 💻 Code Example — Advanced

```typescript
// special-types-advanced.ts — webhook narrowing + exhaustive switch + catch(unknown)

// Union of webhook events (discriminated by `type`)
type WebhookEvent =
  | { type: "payment.captured"; paymentId: string; amountPaise: number }
  | { type: "payment.failed"; paymentId: string; reason: string }
  | { type: "refund.created"; refundId: string };

// Helper: compile-time exhaustiveness check. `never` param can only receive impossible values
function assertNever(x: never): never {
  throw new Error(`Unhandled event: ${JSON.stringify(x)}`); // runtime safety net too
}

function handle(e: WebhookEvent): string {
  switch (e.type) {                                          // narrow by discriminant
    case "payment.captured":
      return `captured ${e.amountPaise / 100}`;              // e: captured variant
    case "payment.failed":
      return `failed: ${e.reason}`;                          // e: failed variant
    case "refund.created":
      return `refund ${e.refundId}`;                         // e: refund variant
    default:
      return assertNever(e);                                 // e is `never` here -> OK
  }
}

// Narrowing unknown input (the untrusted HTTP body)
function parseEvent(body: unknown): WebhookEvent {
  if (typeof body !== "object" || body === null) throw new Error("body must be object");
  const o = body as Record<string, unknown>;                 // one controlled assertion
  if (o.type === "payment.captured" && typeof o.paymentId === "string" && typeof o.amountPaise === "number") {
    return { type: "payment.captured", paymentId: o.paymentId, amountPaise: o.amountPaise };
  }
  throw new Error("unsupported event");
}

// catch variable is unknown under strict: narrow before reading
function safeParse(raw: string): string {
  try {
    return handle(parseEvent(JSON.parse(raw)));              // JSON.parse -> any, passed as unknown
  } catch (err) {                                            // err: unknown
    if (err instanceof Error) return `error: ${err.message}`; // narrowed to Error
    return "error: unknown failure";                         // thrown non-Error (e.g. a string)
  }
}

console.log(safeParse('{"type":"payment.captured","paymentId":"pay_1","amountPaise":49950}'));
console.log(safeParse('{"type":"nope"}'));
console.log(safeParse("not json"));
// Output:
// captured 499.5
// error: unsupported event
// error: Unexpected token 'o', "not json" is not valid JSON
```

---

## 🟠 Node/Express + React Integration

**Express — typed error middleware with `unknown`:**

```typescript
// error-middleware.ts — errors are unknown; map them to a safe response
import express, { NextFunction, Request, Response } from "express";

class HttpError extends Error {
  constructor(public status: number, message: string) { super(message); } // status + message
}

const app = express();
app.use(express.json());

app.post("/pay", (req: Request, res: Response) => {
  const body: unknown = req.body;                          // untrusted -> unknown, not any
  if (typeof body !== "object" || body === null || !("amountPaise" in body)) {
    throw new HttpError(400, "amountPaise missing");       // `in` narrows the object
  }
  res.json({ ok: true });
});

// 4-arg signature marks this as an error handler; err is typed unknown by us
app.use((err: unknown, _req: Request, res: Response, _next: NextFunction): void => {
  if (err instanceof HttpError) {                          // narrow to our class
    res.status(err.status).json({ error: err.message });
    return;
  }
  res.status(500).json({ error: "internal error" });       // never leak unknown error details
});
export default app;
```

**React — `void` callbacks and `unknown` for JSON:**

```tsx
// OrderActions.tsx — void return type for event callbacks
type Props = { orderId: string; onCancel: (id: string) => void }; // result of onCancel is ignored

export function OrderActions({ orderId, onCancel }: Props) {
  return <button onClick={() => onCancel(orderId)}>Cancel</button>;
}
// A parent may pass an async function (id) => api.cancel(id): returns Promise<void>, still assignable to `=> void`.
```
Redux note: in `createAsyncThunk` the `rejectValue` and `catch` payloads are `unknown` — narrow before dispatching `rejected` messages. `any` in `RootState` selectors breaks inference for the whole component tree.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `any` for API responses
```typescript
// ⚠️ Wrong — typo and wrong type pass silently
async function getTotal(): Promise<number> {
  const res: any = await fetch("/api/cart").then((r) => r.json());
  return res.totl;                // typo compiles, returns undefined at runtime
}
```
```typescript
// ✅ Right — unknown + narrowing (or Zod)
async function getTotal2(): Promise<number> {
  const res: unknown = await fetch("/api/cart").then((r) => r.json());
  if (typeof res === "object" && res !== null && "total" in res && typeof res.total === "number") {
    return res.total;             // `in` + typeof narrowed total to number
  }
  throw new Error("bad cart response");
}
```

❌ Mistake 2: Using `Function`/`Object`/`{}` as "any function / any object"
✅ Correct: use `(...args: never[]) => unknown` for "any function" and `Record<string, unknown>` or `object` for "any object". `{}` means "any non-null value" (includes strings!).

❌ Mistake 3: Writing `void` as a union with a value: `string | void`
✅ Correct: use `string | undefined`. `void` in a union is confusing and can't be narrowed well.

❌ Mistake 4: Casting `catch (e)` to `any` — `catch (e: any)` is allowed but unsafe.
✅ Correct: keep `unknown`, then `e instanceof Error`.

---

## 🧠 Tricky Interview Question

```typescript
function run(cb: () => void) { return cb(); }
const r = run(() => 42);
console.log(r);

function runStrict(): void { return 42; } // ❌ TS2322 (see verified output below)
```
**Question:** Does each compile? What does `r` print?

**Answer:** `run(() => 42)` **compiles** — a function type returning `void` accepts functions returning any value (the result is simply ignored by contract). `r` has type `void` yet at runtime prints `42` (void is a compile-time promise, not a runtime guarantee). But a function *declaration* with an explicit `: void` return type **cannot** `return 42` — `error TS2322: Type 'number' is not assignable to type 'void'.` (verified below). The asymmetry exists so callbacks like `forEach(x => arr.push(x))` keep working.

```typescript
// ❌ verified compiler output for the second half of the question
function runStrict(): void {
  return 42;
}
// error TS2322: Type 'number' is not assignable to type 'void'.
```

```typescript
// the first half compiles and prints 42
function run(cb: () => void) { return cb(); }
const r = run(() => 42);
console.log(r); // 42
```

---

## ⚫ Interview Questions + Answers

Q1: `any` vs `unknown` — which do you prefer and why?
A1: `unknown`. Both accept any value, but `any` lets you do anything with it (no checks, infects other types), while `unknown` forces narrowing (`typeof`, `instanceof`, guards, Zod) before use. Use `any` only as a documented escape hatch (e.g. migrating legacy code, hard-to-type third-party libs).

Q2: When does TypeScript infer `never`?
A2: (a) functions that always throw or never end, (b) the remainder of a union after all members are narrowed away, (c) intersections of incompatible primitives like `string & number`, (d) an empty array literal `[]` typed as `never[]` under some settings. It powers exhaustive checks.

Q3: Why is `void` different from `undefined`?
A3: `void` is the return type of functions whose result should be ignored; a `() => void` type accepts functions that return anything. `undefined` is an actual value. A function typed `(): undefined` must explicitly return `undefined` (TS 5.1 relaxed this for functions without any `return`).

Q4: How do you do an exhaustive `switch`?
A4: Add `default: const _x: never = value; throw ...` or call `assertNever(value)` where the parameter is `never`. If a new union member exists, `value` is no longer `never` and compilation fails.

Q5: How does `catch (e)` behave in strict mode?
A5: With `useUnknownInCatchVariables` (part of `strict`, TS 4.4+), `e` is `unknown`. Narrow with `e instanceof Error` (or a custom guard) before reading `.message`. Remember anything can be thrown in JS, even strings or `null`.

---

## 🔷 When to Use + When Not to Use
✅ Use:
- `unknown` for external input (HTTP body, `JSON.parse`, `catch`), generic "bag" params
- `never` for exhaustive checks and functions that throw
- `void` for callbacks and side-effect functions (loggers, dispatchers)

❌ Avoid:
- `any` in application code; enable `@typescript-eslint/no-explicit-any`
- `void` inside unions; `never` as a type for variables you intend to assign
- `unknown` for values you control — give them a real type

---

## 📊 Visual Diagram
```
                 unknown   (top type: accepts everything)
                    │
   string  number  boolean  object  Order  null  undefined ...
                    │
                  never     (bottom type: accepts nothing, assignable to all)

   any ◄──────► everything     (breaks the lattice, switches checking OFF)

   function f(): void   ── result ignored by contract
   function g(): never  ── never returns (throws / infinite loop)

   narrowing:  u: unknown ──typeof──► string ──► use safely
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| any | Opt-out of type checking | Type checking से बाहर निकलना |
| unknown | Safe top type; must narrow | Safe top type; narrow ज़रूरी |
| never | Type with no values (bottom type) | बिना values का type (bottom type) |
| void | No meaningful return value | कोई काम की return value नहीं |
| Top type | Accepts every value | हर value लेने वाला type |
| Exhaustiveness check | Compiler proves all cases handled | Compiler का सब cases handle होने का प्रमाण |
| Type narrowing | Refining a type via checks | Checks से type को सीमित करना |

---

## ⚡ 3-Line Summary
English:
1. `any` disables checking; `unknown` accepts anything but must be narrowed — prefer `unknown` for untrusted data.
2. `never` = impossible value; use it for exhaustive switches and always-throwing functions.
3. `void` = "ignore the result"; `() => void` callbacks may still return values, but `: void` declarations cannot.

Hindi:
1. `any` checking बंद करता है; `unknown` सब कुछ लेता है पर narrow करना पड़ता है — untrusted data के लिए `unknown` चुनो।
2. `never` = असंभव value; exhaustive switch और हमेशा throw करने वाले functions में इस्तेमाल करो।
3. `void` = "result ignore करो"; `() => void` callbacks कुछ लौटा सकते हैं, पर `: void` वाले declaration नहीं।

---

## ➡️ Next Topic
**007. Arrays and Tuples** — typing lists, fixed-length tuples, readonly arrays and labelled tuple elements.
