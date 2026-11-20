# 84. Typed Error Handling in Express
# हिंदी में: Express में Typed Error Handling

> Verified with **TypeScript 5.9.x**. `useUnknownInCatchVariables` (part of `strict`) is TS 4.4+. `Error` `cause` option needs `lib: ES2022`.

---

## 🔵 Simple Definition (English)
Typed error handling in Express means: (1) a small **hierarchy of error classes** (`AppError`, `NotFoundError`, `ValidationError`) carrying `status` and a machine-readable `code`; (2) an **async wrapper** so rejected promises reach Express; (3) one **central error middleware** (4 params) that converts any `unknown` thrown value into a consistent JSON response; and optionally (4) a **`Result<T, E>`** type for expected failures.

## 🔵 सरल परिभाषा (Hindi)
Express में typed error handling का मतलब: (1) **error classes की छोटी hierarchy** (`AppError`, `NotFoundError`, `ValidationError`) जिनमें `status` और machine-readable `code` हो; (2) **async wrapper** ताकि rejected promises Express तक पहुँचें; (3) एक **central error middleware** (4 params) जो किसी भी `unknown` thrown value को consistent JSON response में बदले; और optionally (4) expected failures के लिए **`Result<T, E>`** type।

---

## 🔴 Problem it Solves
In strict TS, `catch (err)` gives `err: unknown` — you cannot read `err.message` without narrowing. In Express 4, an `async` handler that throws leaves the request **hanging** (unhandled rejection) because Express doesn't await handlers. And ad-hoc `res.status(500).json({ msg: ... })` in 40 places creates 40 different error shapes the React app must parse. A typed pipeline gives one shape, correct status codes, and no leaked stack traces.

## 🔴 यह क्यों बना? (Hindi)
Strict TS में `catch (err)` से `err: unknown` मिलता है — narrowing के बिना `err.message` नहीं पढ़ सकते। Express 4 में `async` handler throw करे तो request **लटकी** रह जाती है (unhandled rejection) क्योंकि Express handlers को await नहीं करता। और 40 जगह अलग-अलग `res.status(500).json({ msg: ... })` से 40 अलग error shapes बनते हैं जिन्हें React app को parse करना पड़ता है। Typed pipeline एक shape, सही status codes और बिना stack trace leak के error देती है।

---

## 🟢 How it Works — Step by Step

Step 1 → Define `AppError extends Error` with `status`, `code`, optional `details`; subclasses fix the status.
Step 2 → Set `Object.setPrototypeOf(this, new.target.prototype)` only if you target ES5; with ES2022 `instanceof` works natively.
Step 3 → Wrap async handlers: `asyncHandler(fn)` calls `fn(...).catch(next)`. (Express 5 does this automatically.)
Step 4 → Throw domain errors inside services/controllers: `throw new NotFoundError("Order", id)`.
Step 5 → Error middleware narrows `unknown`: `AppError` → its status; `ZodError` → 400; anything else → 500 with a generic message, and log the real error.
Step 6 → Contract: all error bodies are `{ error: { code, message, details? } }` — a type shared with React.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `AppError extends Error` बनाओ जिसमें `status`, `code`, optional `details` हो; subclasses status तय करती हैं।
Step 2 → `Object.setPrototypeOf(this, new.target.prototype)` सिर्फ ES5 target पर चाहिए; ES2022 में `instanceof` अपने आप चलता है।
Step 3 → Async handlers wrap करो: `asyncHandler(fn)` `fn(...).catch(next)` करता है। (Express 5 में यह अपने आप होता है।)
Step 4 → Services/controllers में domain errors throw करो: `throw new NotFoundError("Order", id)`।
Step 5 → Error middleware `unknown` narrow करे: `AppError` → उसका status; `ZodError` → 400; बाकी सब → generic message के साथ 500, असली error log करो।
Step 6 → Contract: सारे error bodies `{ error: { code, message, details? } }` — React के साथ shared type।

---

## 🟡 Real World Example
A **Zomato checkout**: `POST /orders` fails for four reasons — invalid body (400), restaurant closed (409), coupon not found (404), DB down (500). The React cart reads `error.code` (`"RESTAURANT_CLOSED"`) to show a friendly banner; it never parses message strings. The 500 case logs the full stack server-side but returns only "Something went wrong" plus a request id.

## 🟡 Real Example Hindi mein
**Zomato checkout**: `POST /orders` चार वजहों से fail होता है — invalid body (400), restaurant बंद (409), coupon नहीं मिला (404), DB down (500)। React cart `error.code` (`"RESTAURANT_CLOSED"`) पढ़कर friendly banner दिखाता है; message strings parse नहीं करता। 500 पर पूरा stack server में log होता है पर client को सिर्फ "Something went wrong" और request id जाता है।

---

## 💻 Code Example — Basic

```typescript
// ❌ strict mode: catch variable is `unknown`, not `any`
try {
  JSON.parse("{");
} catch (err) {
  console.log(err.message);
  // error TS18046: 'err' is of type 'unknown'.
}
```

```typescript
// errors.ts — the error hierarchy
export class AppError extends Error {
  constructor(
    public readonly status: number,   // HTTP status to send
    public readonly code: string,     // stable machine-readable code for the frontend
    message: string,                  // human message
    public readonly details?: unknown, // optional extra info (field errors etc.)
  ) {
    super(message);                   // sets Error.message
    this.name = new.target.name;      // "NotFoundError" etc. (nice in logs)
  }
}

export class NotFoundError extends AppError {
  constructor(entity: string, id: string | number) {
    super(404, "NOT_FOUND", `${entity} ${id} not found`); // fixed status + code
  }
}

export class ConflictError extends AppError {
  constructor(code: string, message: string) {
    super(409, code, message); // e.g. RESTAURANT_CLOSED
  }
}

// Type guard that works on `unknown`
export function isAppError(e: unknown): e is AppError {
  return e instanceof AppError; // class-based narrowing
}

// Demo: narrowing an unknown thrown value
try {
  throw new NotFoundError("Order", 42);
} catch (e) {                          // e: unknown
  if (isAppError(e)) console.log(e.status, e.code, e.message); // 404 NOT_FOUND Order 42 not found
}
```

## 💻 Code Example — Advanced

```typescript
// error-middleware.ts — async wrapper + central handler + wire-up
import express, {
  type Request, type Response, type NextFunction, type RequestHandler, type ErrorRequestHandler,
} from "express";

class AppError extends Error {
  constructor(public status: number, public code: string, message: string, public details?: unknown) {
    super(message);
  }
}
class NotFoundError extends AppError {
  constructor(entity: string, id: string) { super(404, "NOT_FOUND", `${entity} ${id} not found`); }
}

// Shared wire format (also imported by React)
interface ErrorBody { error: { code: string; message: string; requestId?: string; details?: unknown } }

// asyncHandler: keeps the handler's generics and forwards rejections to next()
const asyncHandler = <P = {}, ResB = unknown, ReqB = unknown, Q = qs>(
  fn: (req: Request<P, ResB, ReqB, Q>, res: Response<ResB>, next: NextFunction) => Promise<void>,
): RequestHandler<P, ResB, ReqB, Q> =>
  (req, res, next) => { fn(req, res, next).catch(next); }; // any rejection -> error middleware
type qs = import("qs").ParsedQs; // default query type used by Express

// Central error middleware: takes ANY thrown value
const errorHandler: ErrorRequestHandler = (err: unknown, _req, res: Response<ErrorBody>, _next) => {
  if (err instanceof AppError) {                     // known, expected error
    res.status(err.status).json({ error: { code: err.code, message: err.message, details: err.details } });
    return;
  }
  if (err instanceof SyntaxError && "body" in err) { // express.json() bad JSON produces SyntaxError with .body
    res.status(400).json({ error: { code: "BAD_JSON", message: "Malformed JSON body" } });
    return;
  }
  console.error(err);                                // unknown => log full thing server-side
  res.status(500).json({ error: { code: "INTERNAL", message: "Something went wrong" } }); // no leaks
};

const app = express();
app.use(express.json());

// async handler that throws a domain error
const orders = new Map<string, { id: string; total: number }>([["o1", { id: "o1", total: 450 }]]);
app.get("/orders/:id", asyncHandler<{ id: string }>(async (req, res) => {
  const order = orders.get(req.params.id);
  if (!order) throw new NotFoundError("Order", req.params.id); // becomes 404 JSON via errorHandler
  res.json(order);
}));

app.use(errorHandler); // LAST
```

```typescript
// result.ts — for EXPECTED failures, return instead of throw (small Result type)
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E }; // discriminated union (topic 26)

type PayError = "INSUFFICIENT_FUNDS" | "CARD_DECLINED"; // closed set of business errors

function charge(balance: number, amount: number): Result<number, PayError> {
  if (amount > balance) return { ok: false, error: "INSUFFICIENT_FUNDS" }; // no exception
  return { ok: true, value: balance - amount };                            // new balance
}

const r = charge(100, 250);
if (!r.ok) {
  console.log("failed:", r.error); // failed: INSUFFICIENT_FUNDS  (r.error is PayError here)
} else {
  console.log(r.value);            // r.value is number here
}
```

---

## 🟠 Node/Express + React Integration

```typescript
// shared/errors.ts — one wire contract
export interface ApiErrorBody { error: { code: string; message: string; details?: unknown } }
```

```typescript
// web/src/api/http.ts — React/Redux side: turn error responses into a typed exception
import type { ApiErrorBody } from "../../shared/errors";

export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string) { super(message); }
}

export async function http<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);                       // fetch only rejects on network failure
  if (!res.ok) {
    const body = (await res.json().catch(() => null)) as ApiErrorBody | null; // body may be missing/not JSON
    throw new ApiError(res.status, body?.error.code ?? "UNKNOWN", body?.error.message ?? res.statusText);
  }
  return (await res.json()) as T;                           // success body
}

// Redux Toolkit thunk usage (topic 94): rejectWithValue({ code: err.code })
// UI: if (err.code === "RESTAURANT_CLOSED") showBanner(...)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `catch (err: any)` just to silence the compiler.
✅ Keep `unknown` and narrow: `err instanceof Error ? err.message : String(err)`.

❌ Mistake 2: `async` handler without a wrapper in Express 4 — thrown errors never reach the error middleware, and the request hangs.
```typescript
// ❌ Express 4: rejected promise is NOT passed to next(); the client waits until timeout
// app.get("/x", async (req, res) => { throw new Error("boom"); });
// ✅ app.get("/x", asyncHandler(async (req, res) => { throw new Error("boom"); }));
// (Express 5 forwards rejected promises automatically.)
```

❌ Mistake 3: Leaking `err.stack` or SQL messages in the response. ✅ Log server-side, send a code + generic message for unknown errors.

❌ Mistake 4: Checking `err.name === "AppError"` strings instead of `instanceof`; subclass names differ and minification renames classes. ✅ `instanceof AppError` (or a `code` field).

❌ Mistake 5: Throwing for every business outcome ("insufficient funds") and using exceptions as control flow. ✅ `Result<T,E>` for expected failures, exceptions for the unexpected.

---

## 🧠 Tricky Interview Question
**Q:** "Why does `err instanceof NotFoundError` sometimes return `false` even though you clearly threw `new NotFoundError(...)`?"

**A:** Common causes: (1) **target ES5** — extending built-ins like `Error` breaks the prototype chain; fix with `Object.setPrototypeOf(this, new.target.prototype)` or target ES2015+. (2) **Duplicate module instances** — the class is loaded twice (monorepo, two copies of a package, or CJS/ESM dual-package hazard), so the `NotFoundError` constructor identity differs. (3) The error crossed a **process/worker/serialization boundary** (JSON, `postMessage`) and lost its prototype. For robust checks, also add a discriminant field (`code`) and an `isAppError` guard that tests `typeof e.code === "string"` structurally.

---

## ⚫ Interview Questions + Answers

Q1: Why is `catch (err)` typed `unknown` and how do you handle it?
A1: With `strict` (`useUnknownInCatchVariables`) anything can be thrown in JS (strings, objects), so TS won't assume `Error`. Narrow with `instanceof Error`, a custom guard, or a helper `toError(e: unknown): Error`.

Q2: How do async errors reach Express error middleware?
A2: Express 4: call `next(err)` — wrap async handlers with `fn(...).catch(next)` (`express-async-errors` or your own `asyncHandler`). Express 5: returned rejected promises are forwarded automatically.

Q3: How do you identify an error middleware to Express?
A3: By arity — a function with exactly 4 parameters `(err, req, res, next)`. It must be registered after routes.

Q4: Exceptions or `Result` types?
A4: Exceptions for truly exceptional/unrecoverable (DB down, bug). `Result<T, E>` (discriminated union) for expected business failures so the compiler forces callers to handle them. Often combine: service returns `Result`, controller maps to HTTP.

Q5: What should a good API error body contain?
A5: A stable `code` (for clients/i18n), a human `message`, optional `details` (field errors), correlation/request id, and the right HTTP status. Never the stack.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every non-trivial Express API; shared by all controllers
- You need consistent client handling (React/Redux)

❌ Avoid / careful when:
- Deep class hierarchies (keep it 1–2 levels, use `code` strings)
- Using exceptions for normal flow in hot paths (they are slow and obscure control flow)

---

## 📊 Visual Diagram
```
 handler ──throw NotFoundError──┐
 service ──throw ConflictError──┤  asyncHandler: fn().catch(next)
 zod     ──throw ZodError───────┤
 DB lib  ──throw Error──────────┘
                                ▼
                     errorHandler(err: unknown, req, res, next)   ← 4 params
                       ├─ AppError   → status + {code,message}
                       ├─ ZodError   → 400 + details
                       └─ other      → log + 500 "Something went wrong"
                                ▼
                    { error: { code, message } }  ──► React/Redux
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `unknown` in catch | Thrown value of unknown type | Thrown value जिसका type पता नहीं |
| `AppError` | Base class for domain errors | Domain errors की base class |
| Error middleware | 4-param Express handler | 4-param Express handler |
| `asyncHandler` | Forwards promise rejections | Promise rejections को forward करता है |
| `Result<T,E>` | Success-or-error union | Success या error union |
| Error code | Stable machine-readable id | Stable machine-readable पहचान |
| `instanceof` guard | Class-based narrowing | Class के आधार पर narrowing |

---

## ⚡ 3-Line Summary
English:
1. Build `AppError` subclasses with `status` + `code`; narrow `unknown` in `catch` using `instanceof`.
2. Wrap async handlers (Express 4) and use one central 4-param error middleware with one JSON shape.
3. Use `Result<T,E>` for expected failures; log unknown errors, never leak stacks.

Hindi:
1. `status` + `code` वाली `AppError` subclasses बनाओ; `catch` में `unknown` को `instanceof` से narrow करो।
2. Async handlers wrap करो (Express 4) और एक central 4-param error middleware से एक ही JSON shape दो।
3. Expected failures के लिए `Result<T,E>`; unknown errors log करो, stack कभी leak नहीं।

---

## ➡️ Next Topic
**85. Typed REST Controllers + DTOs** — layering routes, controllers, services, and DTO types.
