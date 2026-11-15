# 28. Assertion Functions (asserts x)
# हिंदी में: Assertion Functions (`asserts x` — throw करने वाले guards)

> Verified with TypeScript 5.x (5.9) under `tsc --strict`. Assertion signatures exist since TS 3.7. They require an explicit type annotation on the function reference.

---

## 🔵 Simple Definition (English)
An **assertion function** has a return type like `asserts cond` or `asserts x is T`. If it **returns normally**, TypeScript treats the condition as true (or `x` as `T`) for ALL the code after the call. If the condition is false, the function must **throw**. It is a type guard that throws instead of returning a boolean.

## 🔵 सरल परिभाषा (Hindi)
**Assertion function** का return type `asserts cond` या `asserts x is T` होता है। अगर function **normal return** करता है, तो TypeScript call के बाद के **पूरे code** में condition को true (या `x` को `T`) मान लेता है। Condition false हो तो function को **throw** करना ही पड़ता है। यह boolean लौटाने की जगह throw करने वाला type guard है।

---

## 🔴 Problem it Solves
Guards force `if (!isX(v)) throw ...; ` boilerplate at every call site. Validation at the top of a controller or service ("this must be a logged-in user", "env var must exist") should read as one line, after which the rest of the function sees the narrowed type. Assertion functions give a "fail fast" style with compile-time narrowing.

## 🔴 यह क्यों बना? (Hindi)
Guards में हर call site पर `if (!isX(v)) throw ...;` का boilerplate लिखना पड़ता है। Controller या service के शुरू में validation ("user logged-in होना चाहिए", "env var मौजूद होनी चाहिए") एक line में पढ़ी जानी चाहिए, और उसके बाद बाकी function को narrowed type दिखे। Assertion functions "fail fast" style और compile-time narrowing दोनों देते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Condition form: `function assert(cond: unknown, msg?: string): asserts cond`.
Step 2 → Type form: `function assertIsString(x: unknown): asserts x is string`.
Step 3 → The body must throw when the check fails. TypeScript does not verify this; you must write it.
Step 4 → After `assert(x !== undefined)` returns, the rest of the scope sees `x` without `undefined`.
Step 5 → Unlike guards, there is no else branch: failure = exception.
Step 6 → The function must be called through an explicitly typed reference (a `function` declaration or a `const` with a type annotation), otherwise error TS2775.
Step 7 → Node ships `assert` in `node:assert` with assertion signatures (`assert(value)` asserts truthiness), used in tests and startup checks.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Condition form: `function assert(cond: unknown, msg?: string): asserts cond`।
Step 2 → Type form: `function assertIsString(x: unknown): asserts x is string`।
Step 3 → Check fail होने पर body को throw करना ज़रूरी है। TypeScript इसे verify नहीं करता, आपको खुद लिखना है।
Step 4 → `assert(x !== undefined)` return होने के बाद बाकी scope में `x` बिना `undefined` दिखता है।
Step 5 → Guards की तरह else branch नहीं होती: failure का मतलब exception।
Step 6 → Function को explicit type वाले reference से call करना होता है (`function` declaration या annotated `const`), वरना error TS2775।
Step 7 → Node का `node:assert` भी assertion signatures के साथ आता है (`assert(value)` truthiness assert करता है); tests और startup checks में उपयोगी।

---

## 🟡 Real World Example
**Swiggy order service** starts with `assertDefined(req.user)` and `assertPositive(qty)`. If any fails it throws a 400/401. Below that line the service uses `user.id` and `qty` with no `?.` or `!`, and the code reads like a checklist.

## 🟡 Real Example Hindi mein
**Swiggy order service** की शुरुआत `assertDefined(req.user)` और `assertPositive(qty)` से होती है। कोई भी fail हो तो 400/401 throw होता है। उस line के बाद service `user.id` और `qty` को बिना `?.` या `!` के इस्तेमाल करती है, और code एक checklist जैसा पढ़ा जाता है।

---

## 💻 Code Example — Basic

```typescript
// Condition-style assertion: if it returns, 'cond' is true
function assert(cond: unknown, msg: string): asserts cond {
  if (!cond) throw new Error(msg); // fail fast when false
}

// Type-style assertion: if it returns, 'x' is a string
function assertIsString(x: unknown): asserts x is string {
  if (typeof x !== "string") throw new TypeError("expected string"); // fail fast
}

function handle(coupon: string | undefined, raw: unknown): void {
  assert(coupon !== undefined, "coupon required"); // after this, coupon: string
  console.log(coupon.toUpperCase()); // no ? or ! needed

  assertIsString(raw); // after this, raw: string
  console.log(raw.length); // narrowed from unknown
}

handle("save10", "abcd"); // passes both
try { handle(undefined, "x"); } catch (e) { console.log((e as Error).message); } // fails first assert
```

Run with `npx tsx`:

```
SAVE10
4
coupon required
```

## 💻 Code Example — Advanced

```typescript
// Advanced: assertDefined<T>, assertNever-style exhaustive check, and class method assertion

// Generic: strips null | undefined from ANY value after the call
function assertDefined<T>(value: T, name: string): asserts value is NonNullable<T> {
  if (value === null || value === undefined) throw new Error(`${name} is missing`); // throw if absent
}

// Domain error carrying an HTTP status for Express error middleware
class HttpError extends Error { constructor(public status: number, msg: string) { super(msg); } } // status + message

// Assertion that throws a typed domain error
function assertPositive(n: number, field: string): asserts n is number {
  if (!(n > 0)) throw new HttpError(400, `${field} must be > 0`); // 400 Bad Request
}

interface User { id: number; name: string } // user shape
interface Req { user?: User; body: { qty?: number } } // request-like

function placeOrder(req: Req): string {
  assertDefined(req.user, "user"); // req.user is now User (property narrowing)
  assertDefined(req.body.qty, "qty"); // req.body.qty is now number
  assertPositive(req.body.qty, "qty"); // positive check
  return `${req.user.name} ordered ${req.body.qty}`; // both safely typed
}

console.log(placeOrder({ user: { id: 1, name: "Asha" }, body: { qty: 2 } })); // ok
for (const bad of [{ body: { qty: 2 } }, { user: { id: 1, name: "A" }, body: { qty: -1 } }] as Req[]) {
  try { placeOrder(bad); } catch (e) { console.log((e as Error).message); } // each failure
}

// Assertion METHOD on a class: 'asserts this is X'
class Session {
  userId?: number; // may be missing
  assertLoggedIn(): asserts this is Session & { userId: number } {
    if (this.userId === undefined) throw new HttpError(401, "login required"); // 401 Unauthorized
  }
}
const s: Session = new Session(); // explicit annotation is REQUIRED for assertion calls
s.userId = 7; // logged in
s.assertLoggedIn(); // narrows s
console.log(s.userId.toFixed(1)); // userId: number
```

Run with `npx tsx`:

```
Asha ordered 2
user is missing
qty must be > 0
7.0
```

---

## 🟠 Node/Express + React Integration

```typescript
// Express: startup config assertion and controller fail-fast
import express from "express"; // express
import type { Request, Response, NextFunction } from "express"; // types

// Assertion function
function assertString(v: unknown, name: string): asserts v is string {
  if (typeof v !== "string" || v.length === 0) throw new Error(`${name} must be a non-empty string`); // fail
}

const dbUrl: string | undefined = process.env.DATABASE_URL ?? "sqlserver://localhost"; // may be undefined in real life
assertString(dbUrl, "DATABASE_URL"); // after this dbUrl: string

const app = express(); // app

app.get("/orders/:id", (req: Request<{ id: string }>, res: Response) => {
  const id = Number(req.params.id); // convert path param
  if (Number.isNaN(id)) throw new Error("id must be numeric"); // sync throw reaches error middleware
  res.json({ id, db: dbUrl.length }); // dbUrl is string inside the closure (const)
});

// Central error handler turns thrown assertion errors into HTTP responses
app.use((err: unknown, _req: Request, res: Response, _next: NextFunction) => {
  res.status(400).json({ error: err instanceof Error ? err.message : "bad request" }); // narrow unknown
});
```

```tsx
// React: assert a context value exists (the classic useContext null check)
import { createContext, useContext } from "react"; // react APIs

interface CartApi { count: number } // context value
const CartCtx = createContext<CartApi | null>(null); // null until provider mounts

function assertProvided<T>(v: T | null, hook: string): asserts v is T {
  if (v === null) throw new Error(`${hook} must be used inside its Provider`); // developer error
}

export function useCart(): CartApi {
  const ctx = useContext(CartCtx); // CartApi | null
  assertProvided(ctx, "useCart"); // after this ctx: CartApi
  return ctx; // no cast needed
}
```

---

## ⚠️ Common Mistakes to Avoid

**Mistake 1: Calling an assertion through an un-annotated arrow.**

```typescript
// ❌ WRONG: arrow assigned to a const with NO type annotation
const assertOk = (v: unknown): asserts v => { if (!v) throw new Error("bad"); }; // inferred, not annotated
function f(x: string | undefined): void {
  assertOk(x); // ❌ error
}
```

Real compiler output:

```
error TS2775: Assertions require every name in the call target to be declared with an explicit type annotation.
```

```typescript
// ✅ RIGHT: use a function declaration (or annotate the const's type)
function assertOk2(v: unknown): asserts v { if (!v) throw new Error("bad"); } // declaration
function g(x: string | undefined): void {
  assertOk2(x); // fine
  console.log(x.length); // x: string
}
g("ok");
```

**Mistake 2: Using the narrowed value before the assertion.**

```typescript
// ❌ WRONG: narrowing happens only AFTER the call
function assertDef<T>(v: T): asserts v is NonNullable<T> { if (v == null) throw new Error("x"); } // assertion
function h(v: string | undefined): number {
  const len = v.length; // ❌ used too early
  assertDef(v);
  return len;
}
```

Real compiler output:

```
error TS18048: 'v' is possibly 'undefined'.
```

**Mistake 3: Writing a lying assertion (does not throw).**

```typescript
// ❌ WRONG: promises 'asserts x is string' but never throws
function assertStringBad(x: unknown): asserts x is string { /* forgot the check */ }
const v: unknown = 42; // really a number
assertStringBad(v); // compiles
console.log(v.toUpperCase()); // v: string by the lie
```

Real output of `npx tsx` on this block:

```
TypeError: v.toUpperCase is not a function
```

---

## 🧠 Tricky Interview Question

**Q: Why does `asserts x` (condition form) narrow `x`, and can it narrow a `string | number` to `string`?**

```typescript
// 'asserts cond' narrows by the EXPRESSION passed in, so typeof checks work
function assert(cond: unknown): asserts cond { if (!cond) throw new Error("assertion failed"); } // condition form

function len(v: string | number): number {
  assert(typeof v === "string"); // passes the boolean expression typeof v === "string"
  return v.length; // v: string
}
console.log(len("abcd")); // 4
try { len(5); } catch (e) { console.log((e as Error).message); } // assertion failed
```

Real output with `npx tsx`:

```
4
assertion failed
```

**Answer:** With `asserts cond`, TypeScript analyses the **argument expression** exactly as it would inside an `if`. If the call returns, that expression must be true, so `typeof v === "string"` narrows `v` to `string`. This is how `node:assert` narrows. It is not magic: the check you pass IS the proof.

---

## ⚫ Interview Questions + Answers

Q1: How is an assertion function different from a type guard?
A1: A guard returns boolean and you branch on it; an assertion returns `void`, throws on failure, and narrows everything after the call in the same scope.

Q2: Must the function actually throw?
A2: Yes, but TypeScript does not check. If you forget, the compiler's narrowing is false and you get runtime errors.

Q3: What is the TS2775 error?
A3: "Assertions require every name in the call target to be declared with an explicit type annotation." Use a `function` declaration or annotate the const's type.

Q4: `asserts x` vs `asserts x is T`?
A4: `asserts x` means x is truthy; `asserts x is T` narrows x to type `T`. The condition form narrows by the call's argument expression.

Q5: Where are they best used?
A5: Startup config validation, "must be logged in" preconditions, `useContext` null checks, tests, and invariants (`invariant(cond, msg)` in libraries).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Preconditions at the top of a function that should abort the request on failure
- Removing `null` from config/context values once
- Replacing repeated `if (!x) throw` blocks

❌ Avoid when:
- Failure is an expected outcome you want to handle (use a type guard or a Result union)
- You need to validate deep shapes (use Zod's `parse`, which throws and returns typed output)
- The call target cannot be explicitly typed (some arrow/destructured imports)

---

## 📊 Visual Diagram
```
  GUARD                          ASSERTION
  if (isOrder(v)) {              assertOrder(v);   // throws if not
     v: Order                    v: Order  ◄── for ALL following code
  } else {                       (no else: failure = exception)
     v: other
  }

  assertDefined(user)
      ├─ ok    ──► continue, user: User
      └─ fail  ──► throw HttpError(401)  → Express error middleware
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| asserts cond | Return means cond is true | Return होने पर cond सच |
| asserts x is T | Return means x is T | Return होने पर x का type T |
| Fail fast | Throw early on bad input | गलत input पर जल्दी throw |
| Invariant | Condition that must always hold | हमेशा सच रहने वाली condition |
| TS2775 | Needs explicit type annotation | Explicit type annotation चाहिए |

---

## ⚡ 3-Line Summary
English:
1. `asserts` functions throw on failure and narrow all following code on success.
2. They must be declared with explicit types and must truly throw.
3. Perfect for preconditions, config and context checks.

Hindi:
1. `asserts` functions failure पर throw करते हैं और success पर आगे का पूरा code narrow करते हैं।
2. इन्हें explicit types के साथ declare करना होता है और सच में throw करना होता है।
3. Preconditions, config और context checks के लिए बढ़िया।

---

## ➡️ Next Topic
**29. Exhaustive Checks with never** — making the compiler prove that every union case is handled.
