# 82. Typing Express Request, Response and Middleware
# हिंदी में: Express Request, Response और Middleware को Type करना

> Verified with **TypeScript 5.9.x** and `@types/express`. The generics order `Request<Params, ResBody, ReqBody, Query, Locals>` is stable across 4.x/5.x typings.

---

## 🔵 Simple Definition (English)
Express's `Request` and `Response` types are **generic**. `Request<P, ResBody, ReqBody, ReqQuery, Locals>` lets you describe route params (`P`), response body, request body, and query string. `Response<ResBody, Locals>` types what `res.json()` accepts and what `res.locals` holds. Middleware is typed with `RequestHandler<...same generics>`, `ErrorRequestHandler`, and `NextFunction`.

## 🔵 सरल परिभाषा (Hindi)
Express के `Request` और `Response` types **generic** हैं। `Request<P, ResBody, ReqBody, ReqQuery, Locals>` से आप route params (`P`), response body, request body और query string describe करते हैं। `Response<ResBody, Locals>` बताता है कि `res.json()` क्या ले सकता है और `res.locals` में क्या है। Middleware को `RequestHandler<...वही generics>`, `ErrorRequestHandler` और `NextFunction` से type करते हैं।

---

## 🔴 Problem it Solves
By default `req.body` is `any`, `req.query` is a loose `ParsedQs`, and `res.json()` accepts anything. A handler can read `req.body.totl` or send `{ total: "x" }` where the frontend expects a number, and TS says nothing. Generics turn the HTTP contract of each route into a compile-time contract.

## 🔴 यह क्यों बना? (Hindi)
Default में `req.body` `any` है, `req.query` ढीला `ParsedQs` है और `res.json()` कुछ भी ले लेता है। Handler `req.body.totl` पढ़ सकता है या frontend जहाँ number चाहता है वहाँ `{ total: "x" }` भेज सकता है, TS कुछ नहीं कहता। Generics हर route के HTTP contract को compile-time contract बना देते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `Request<Params>`: first generic is the route-param object, e.g. `{ orderId: string }` for `/orders/:orderId`.
Step 2 → `Request<P, ResBody, ReqBody>`: second is the response body type, third is `req.body`. Use `{}` or `Record<string, never>` for "none".
Step 3 → Fourth generic is the query object: `Request<P, R, B, { page?: string }>`. Query values are strings (or arrays) — convert yourself.
Step 4 → Define the whole signature once with `RequestHandler<P, ResBody, ReqBody, Query>` so `req` and `res` are inferred together.
Step 5 → Middleware: `(req, res, next) => void`; call `next()` to continue or `next(err)` to jump to the error handler. Error handlers have **4 params** and type `ErrorRequestHandler`.
Step 6 → Per-request data between middlewares goes in `res.locals` (typed with the `Locals` generic) or on `req` (via declaration merging, topic 83).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `Request<Params>`: पहला generic route-param object है, जैसे `/orders/:orderId` के लिए `{ orderId: string }`।
Step 2 → `Request<P, ResBody, ReqBody>`: दूसरा response body type, तीसरा `req.body`। "कुछ नहीं" के लिए `{}` या `Record<string, never>`।
Step 3 → चौथा generic query object है: `Request<P, R, B, { page?: string }>`। Query values strings (या arrays) होती हैं — खुद convert करो।
Step 4 → पूरा signature एक बार `RequestHandler<P, ResBody, ReqBody, Query>` से define करो ताकि `req` और `res` साथ में infer हों।
Step 5 → Middleware: `(req, res, next) => void`; आगे जाने के लिए `next()`, error handler पर जाने के लिए `next(err)`। Error handlers में **4 params** होते हैं, type `ErrorRequestHandler`।
Step 6 → Middlewares के बीच per-request data `res.locals` (`Locals` generic) या `req` पर (declaration merging, topic 83)।

---

## 🟡 Real World Example
A **Swiggy "restaurant search"** endpoint: `GET /restaurants/:cityId?cuisine=north&page=2`. Params = `{ cityId: string }`, query = `{ cuisine?: string; page?: string }`, response = `{ items: Restaurant[]; page: number }`. A logging middleware stamps `res.locals.requestId`, and a typed auth middleware rejects missing tokens.

## 🟡 Real Example Hindi mein
**Swiggy का "restaurant search"** endpoint: `GET /restaurants/:cityId?cuisine=north&page=2`। Params = `{ cityId: string }`, query = `{ cuisine?: string; page?: string }`, response = `{ items: Restaurant[]; page: number }`। Logging middleware `res.locals.requestId` लगाता है, और typed auth middleware बिना token वाली requests reject करता है।

---

## 💻 Code Example — Basic

```typescript
// basic-request-typing.ts
import express, { type Request, type Response } from "express"; // types are erased at runtime

const app = express();   // create app
app.use(express.json()); // populate req.body

interface Restaurant { id: string; name: string; cuisine: string } // one result row

// Request<Params, ResBody, ReqBody, Query>
type SearchReq = Request<
  { cityId: string },                       // 1. route params   :cityId
  { items: Restaurant[]; page: number },    // 2. response body
  {},                                       // 3. request body (none for GET)
  { cuisine?: string; page?: string }       // 4. query string (always strings)
>;

app.get("/restaurants/:cityId", (req: SearchReq, res: Response<{ items: Restaurant[]; page: number }>) => {
  const { cityId } = req.params;                  // typed string
  const page = Number(req.query.page ?? "1");     // query value is string|undefined -> number
  const cuisine = req.query.cuisine;              // string | undefined
  const items: Restaurant[] = [{ id: "r1", name: `Dhaba in ${cityId}`, cuisine: cuisine ?? "any" }];
  res.json({ items, page });                      // res.json is checked against the response type
});

app.listen(3000); // start
```

```typescript
// ❌ Express does not coerce: params are strings, and body is `any` unless you type it
import express from "express";
const app2 = express();
app2.get("/orders/:id", (req, res) => {
  const id: number = req.params.id;
  // error TS2322: Type 'string' is not assignable to type 'number'.
  res.json({ id });
});
app2.post("/orders", (req, res) => {
  console.log(req.body.total.toFixed(2)); // compiles! req.body is `any`, crashes at runtime if total missing
  res.sendStatus(201);
});
```

## 💻 Code Example — Advanced

```typescript
// advanced-middleware.ts — RequestHandler, res.locals, error handler, generic helper
import express, {
  type RequestHandler, type ErrorRequestHandler, type NextFunction, type Request, type Response,
} from "express";

const app = express();   // app
app.use(express.json()); // body parser

// 1) Locals: what middleware A puts on res.locals for handler B
interface Locals { requestId: string; startedAt: number }

// RequestHandler<Params, ResBody, ReqBody, Query, Locals>
const stamp: RequestHandler<{}, any, any, any, Locals> = (_req, res, next) => {
  res.locals.requestId = crypto.randomUUID(); // typed string (Node 19+ global crypto)
  res.locals.startedAt = Date.now();          // typed number
  next();                                     // continue the chain
};
app.use(stamp as RequestHandler); // app-level use() wants the default generics; cast once here

// 2) A handler declared with its WHOLE contract in one type
interface PayBody { orderId: string; amount: number; method: "upi" | "card" }
interface PayRes  { paymentId: string; status: "captured" | "failed" }

const pay: RequestHandler<{}, PayRes | { error: string }, PayBody> = (req, res) => {
  const { amount, method } = req.body;          // typed PayBody
  if (amount <= 0) {
    res.status(400).json({ error: "amount must be positive" }); // matches union member
    return;
  }
  // method is "upi" | "card" -> switch is exhaustive-checkable (topic 29)
  const status = method === "upi" ? "captured" : "failed";
  res.json({ paymentId: `pay_${Date.now()}`, status }); // must fit PayRes
};
app.post("/pay", pay); // handler's generics must agree with the route

// 3) Middleware factory: returns a typed middleware (role guard)
function requireHeader(name: string): RequestHandler {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.header(name)) {                           // header() -> string | undefined
      res.status(401).json({ error: `${name} required` });
      return;                                          // stop the chain
    }
    next();                                            // header present
  };
}
app.use("/admin", requireHeader("x-api-key"));         // typed, reusable

// 4) Error middleware: exactly 4 params
const onError: ErrorRequestHandler = (err: unknown, _req, res, _next) => {
  const msg = err instanceof Error ? err.message : "Unknown";
  res.status(500).json({ error: msg });
};
app.use(onError); // register LAST
```

---

## 🟠 Node/Express + React Integration

```typescript
// shared/contracts.ts — ONE contract used by Express handler AND React fetch
export interface PayBody { orderId: string; amount: number; method: "upi" | "card" }
export interface PayRes  { paymentId: string; status: "captured" | "failed" }
```

```typescript
// server/routes/pay.ts — handler typed from the shared contract
import type { RequestHandler } from "express";
import type { PayBody, PayRes } from "../../shared/contracts"; // type-only import

export const payHandler: RequestHandler<{}, PayRes, PayBody> = (req, res) => {
  res.json({ paymentId: `pay_${req.body.orderId}`, status: "captured" }); // res.json must be PayRes
};
```

```typescript
// web/src/pay.ts — frontend call, same types, so a field rename breaks BOTH sides at compile time
import type { PayBody, PayRes } from "../../shared/contracts";

export async function pay(body: PayBody): Promise<PayRes> {
  const r = await fetch("/api/pay", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return (await r.json()) as PayRes; // trusted cast; validate with zod in real apps (topic 86)
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trusting `req.body` types as runtime guarantees.
✅ The generic is only a **promise to the compiler**. Clients can send anything; validate with zod (topic 86) and then assign the type.

❌ Mistake 2: Using `Request<{ id: number }>` — params are always strings.
```typescript
// ❌ Lies to the compiler: "id" is really "42"
// Request<{ id: number }>
// ✅ Request<{ id: string }> then Number(req.params.id), check Number.isNaN
```

❌ Mistake 3: Writing error middleware with 3 parameters — Express treats it as normal middleware and never calls it for errors. The 4th param (even if unused, `_next`) is required.

❌ Mistake 4: Forgetting to stop after sending a response. `res.status(400).json(...)` without `return` keeps executing the rest of the handler (a second `res.json` throws "Cannot set headers after they are sent"). ✅ `res.status(400).json(...); return;` (returning `res.json(...)` also compiles with `@types/express` 5.x, but keep one style).

❌ Mistake 5: Casting `req as any` to attach `req.user`. ✅ Declaration merging (topic 83).

---

## 🧠 Tricky Interview Question
**Q:** "`app.get('/a/:id', (req: Request<{ id: string }>, res) => { ... })` compiles. Does TypeScript verify that the route string actually contains `:id`?"

**A:** Only if you do NOT annotate. With an explicit `Request<{ id: string }>` the route string is unrelated, so renaming the route to `/a/:orderId` still compiles and `req.params.id` becomes `undefined` at runtime. Without an annotation, `@types/express-serve-static-core` infers params from the literal path using template-literal types (`RouteParameters<Route>`); I verified that `app.get("/a/:id", (req, res) => req.params.foo)` fails with `error TS2339: Property 'foo' does not exist on type '{ id: string; }'.` and `const n: number = req.params.id` fails with TS2322. Best practice: let Express **infer** params from the literal path, and annotate only body/response generics. Template-literal route extraction is topic 112.

---

## ⚫ Interview Questions + Answers

Q1: What are the generics of `Request`?
A1: `Request<ReqParams, ResBody, ReqBody, ReqQuery, Locals>` — params, response body, request body, query, and `res.locals`. The defaults are loose (`ParamsDictionary`, `any`, `any`, `ParsedQs`).

Q2: Why is `req.query.page` not a number?
A2: Query strings are text; Express's parser gives `string | string[] | ParsedQs | ParsedQs[] | undefined`. Narrow and convert (`Number(...)`), or validate with zod coerce.

Q3: How is error middleware typed and identified by Express?
A3: `ErrorRequestHandler` = `(err: any, req, res, next) => void`. Express detects it by `function.length === 4`, so keep all four params.

Q4: `RequestHandler` vs a plain arrow function?
A4: `RequestHandler<...>` gives contextual typing to `req`/`res`/`next` so you don't annotate each, and keeps generics in sync. A plain arrow function needs explicit types or inference from `app.get(...)`.

Q5: How to share data from middleware to handlers in a typed way?
A5: Either the `Locals` generic with `res.locals` (scoped, no global types) or augment `Express.Request` (global) — topic 83. `res.locals` is safer for a few fields; augmentation for `req.user` used everywhere.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every route handler in a TS Express app (params + body + response)
- Writing reusable middleware (auth, validation, rate limit)

❌ Avoid / do not over-rely when:
- You depend on generics as validation (they are erased)
- Deeply nested generic types make handlers unreadable — extract named `type`s

---

## 📊 Visual Diagram
```
 Request< Params , ResBody , ReqBody , Query , Locals >
            │         │         │        │       │
   /:cityId─┘         │         │        │       └─ res.locals shape
   response json ─────┘         │        └─ ?page=2&cuisine=x  (strings)
   req.body ────────────────────┘

 client ─► [stamp] ─► [auth] ─► [validate] ─► handler ─► res.json<ResBody>
                │         │           │
                └─────────┴───────────┴── next(err) ──► ErrorRequestHandler (4 params)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `Request<P,R,B,Q>` | Generic request type | Generic request type |
| `RequestHandler` | Typed middleware/handler | Typed middleware/handler |
| `ErrorRequestHandler` | 4-param error middleware | 4-param error middleware |
| `NextFunction` | Call to continue chain | Chain आगे बढ़ाने वाला function |
| `res.locals` | Per-request scratch object | Per-request अस्थायी data |
| `ParsedQs` | Parsed query string type | Parse हुआ query string type |
| Contract | Agreed shape of request/response | Request/response की तय shape |

---

## ⚡ 3-Line Summary
English:
1. `Request<Params, ResBody, ReqBody, Query, Locals>` types every part of an Express route.
2. Params and query are strings, `req.body` is `any` by default; generics are erased, so still validate at runtime.
3. Error middleware needs 4 parameters; share typed data via `res.locals` or declaration merging.

Hindi:
1. `Request<Params, ResBody, ReqBody, Query, Locals>` Express route के हर हिस्से को type करता है।
2. Params और query strings होते हैं, `req.body` default में `any`; generics erase हो जाते हैं, इसलिए runtime validation फिर भी चाहिए।
3. Error middleware में 4 parameters ज़रूरी; typed data `res.locals` या declaration merging से share करो।

---

## ➡️ Next Topic
**83. Extending Express Request (Declaration Merging)** — add `req.user` safely instead of casting to `any`.
