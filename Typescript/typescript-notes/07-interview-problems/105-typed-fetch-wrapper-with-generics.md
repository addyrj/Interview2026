# 105. Typed fetch Wrapper with Generics
# हिंदी में: Generics के साथ Typed fetch Wrapper

> Verified with **TypeScript 5.9.3** (`--strict`), **Node 24** (global `fetch`/`Response`), **Zod 4.6 (`z.infer`)**. Generics, No TS-5.x-only features are needed.

---

## 🔵 Simple Definition (English)
`fetch()` returns `Promise<Response>` and `response.json()` returns `Promise<any>`, so **nothing is type-checked** between your server and your UI. A **typed fetch wrapper** is a small function `request<T>(url, init)` that (1) throws a typed `HttpError` for non-2xx responses, (2) returns `Promise<T>` where **you** choose `T`, and (3) optionally **validates** the JSON at runtime (with Zod) so `T` is a fact, not a hope. Interviewers want to see that you know the difference between **compile-time claims** (`<T>`) and **runtime guarantees** (validation).

## 🔵 सरल परिभाषा (Hindi)
`fetch()` `Promise<Response>` लौटाता है और `response.json()` `Promise<any>` लौटाता है, इसलिए server और UI के बीच **कुछ भी type-check नहीं होता**। **Typed fetch wrapper** एक छोटा function `request<T>(url, init)` है जो (1) non-2xx response पर typed `HttpError` throw करता है, (2) `Promise<T>` लौटाता है जहाँ `T` **आप** चुनते हो, और (3) optionally JSON को runtime पर (Zod से) **validate** करता है ताकि `T` उम्मीद नहीं, तथ्य बने। Interviewer देखना चाहते हैं कि आपको **compile-time दावे** (`<T>`) और **runtime guarantees** (validation) का फर्क पता है।

---

## 🔴 Problem it Solves
Raw `fetch` in a React app produces three recurring bugs: (1) **`any` leaks**: `const order = await res.json()` is `any`, so `order.totl` compiles; (2) **forgotten status checks**: `fetch` does **not** reject on 404/500, so error JSON is treated as success data; (3) **copy-pasted headers/JSON/auth** in 40 places. A wrapper centralises these once, and generics give each call site a precise return type.

## 🔴 यह क्यों बना? (Hindi)
React app में raw `fetch` तीन बार-बार आने वाले bugs देता है: (1) **`any` leak**: `const order = await res.json()` `any` है, इसलिए `order.totl` भी compile हो जाता है; (2) **status check भूलना**: 404/500 पर `fetch` reject **नहीं** करता, इसलिए error JSON को success data मान लिया जाता है; (3) 40 जगह **copy-paste headers/JSON/auth**। Wrapper इन्हें एक बार centralise करता है और generics हर call site को सटीक return type देते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Write `class HttpError extends Error` carrying `status` and parsed `body`.
Step 2 → Write `async function request<T>(url: string, init?: RequestInit): Promise<T>`: call `fetch`, check `res.ok`, throw `HttpError` if not.
Step 3 → Parse JSON (handle `204 No Content` where there is no body) and return it **cast to `T`** (this is a *claim*, not a proof).
Step 4 → Add helpers `get<T>`, `post<TRes, TBody>` that set method, headers and `JSON.stringify(body)`.
Step 5 → For safety accept a **schema**: `request<S extends z.ZodTypeAny>(url, schema: S): Promise<z.infer<S>>` so `T` is derived from a runtime validator, one source of truth.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `class HttpError extends Error` लिखो जिसमें `status` और parsed `body` हो।
Step 2 → `async function request<T>(url: string, init?: RequestInit): Promise<T>` लिखो: `fetch` call करो, `res.ok` check करो, नहीं तो `HttpError` throw करो।
Step 3 → JSON parse करो (`204 No Content` संभालो जहाँ body नहीं होती) और उसे **`T` में cast** करके लौटाओ (यह *दावा* है, सबूत नहीं)।
Step 4 → `get<T>`, `post<TRes, TBody>` helpers जोड़ो जो method, headers और `JSON.stringify(body)` set करें।
Step 5 → सुरक्षा के लिए **schema** लो: `request<S extends z.ZodTypeAny>(url, schema: S): Promise<z.infer<S>>` ताकि `T` runtime validator से derive हो, single source of truth।

---

## 🟡 Real World Example
**Zomato web app** calls `GET /api/restaurants/:id`, `POST /api/cart`, `POST /api/orders`. The team's `api.ts` exports `api.get<Restaurant>(...)` and `api.post<Order, CartDto>(...)`. A 401 anywhere throws `HttpError(401)` which one global handler in React Query converts into "redirect to login". When the backend renames `total` to `grandTotal`, Zod validation fails in the **API layer** with a clear message instead of rendering `NaN` in the cart.

## 🟡 Real Example Hindi mein
**Zomato web app** `GET /api/restaurants/:id`, `POST /api/cart`, `POST /api/orders` call करती है। Team की `api.ts` में `api.get<Restaurant>(...)` और `api.post<Order, CartDto>(...)` export हैं। कहीं भी 401 आने पर `HttpError(401)` throw होता है जिसे React Query का एक global handler "login पर redirect" में बदल देता है। Backend जब `total` को `grandTotal` कर देता है तो Zod validation **API layer** में साफ़ message के साथ fail होती है, cart में `NaN` दिखाने की जगह।

---

## 💻 Code Example — Basic

```typescript
// http-basic.ts — generic wrapper + HttpError, with a mocked fetch so it is runnable
class HttpError extends Error { // typed error for non-2xx
  constructor(public status: number, public body: unknown) { // keep status and parsed body
    super(`HTTP ${status}`); // message for logs
    this.name = "HttpError"; // nicer stack traces
  }
}

async function request<T>(url: string, init?: RequestInit): Promise<T> { // T chosen by the caller
  const res = await fetch(url, init); // network call (does NOT throw on 404/500)
  const text = await res.text(); // read once, may be empty
  const body: unknown = text ? JSON.parse(text) : undefined; // parse only when there is content
  if (!res.ok) throw new HttpError(res.status, body); // convert HTTP failure into an exception
  return body as T; // a CLAIM about the shape; the compiler trusts us
}

const api = { // tiny facade
  get: <T>(url: string) => request<T>(url), // GET
  post: <TRes, TBody = unknown>(url: string, body: TBody) => // POST with typed body
    request<TRes>(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
};

// --- demo with a fake server (no network needed) ---
globalThis.fetch = (async (input: RequestInfo | URL) => { // replace fetch for the demo
  const url = String(input); // normalise
  if (url.endsWith("/orders/1")) return new Response(JSON.stringify({ id: 1, total: 499 }), { status: 200 }); // success
  return new Response(JSON.stringify({ message: "not found" }), { status: 404 }); // failure
}) as typeof fetch;

interface Order { id: number; total: number } // response shape

async function main() { // run the demo
  const o = await api.get<Order>("/orders/1"); // o: Order
  console.log(o.total); // prints 499
  try {
    await api.get<Order>("/orders/99"); // server says 404
  } catch (e) {
    if (e instanceof HttpError) console.log(e.status, e.body); // prints 404 { message: 'not found' }
  }
}
main(); // start
```

```typescript
// http-errors.ts — what the compiler catches at the call site
async function get<T>(url: string): Promise<T> { return (await fetch(url)).json() as Promise<T>; } // wrapper
interface Order { id: number; total: number } // response shape

async function demo() { // examples
  const o = await get<Order>("/orders/1"); // o: Order
  // ❌ typo on the result: caught only BECAUSE we gave T
  console.log(o.totl);
  // error TS2551: Property 'totl' does not exist on type 'Order'. Did you mean 'total'?

  // ❌ forgetting <T> leaves T as unknown, you must narrow before use
  const u = await get("/orders/1");
  console.log(u.id);
  // error TS18046: 'u' is of type 'unknown'.
}
demo(); // never run, compile-only
```

## 💻 Code Example — Advanced

```typescript
// http-advanced.ts — Zod-validated client + Result type + typed endpoint map
import { z } from "zod"; // runtime validator

class HttpError extends Error { constructor(public status: number, public body: unknown) { super(`HTTP ${status}`); } } // as before

// Schema is the single source of truth, the TS type is DERIVED from it
const OrderSchema = z.object({ id: z.number(), total: z.number(), items: z.array(z.string()) }); // runtime shape
type Order = z.infer<typeof OrderSchema>; // compile-time shape = { id: number; total: number; items: string[] }

async function requestValidated<S extends z.ZodTypeAny>(url: string, schema: S, init?: RequestInit): Promise<z.infer<S>> {
  const res = await fetch(url, init); // call
  const json: unknown = await res.json().catch(() => undefined); // never any: start from unknown
  if (!res.ok) throw new HttpError(res.status, json); // HTTP failure
  return schema.parse(json); // throws ZodError if the server lies; result type is z.infer<S>
}

// Result<T,E> instead of exceptions, forces callers to handle failure
type Result<T> = { ok: true; data: T } | { ok: false; error: HttpError | z.ZodError | Error }; // discriminated union

async function safe<T>(p: Promise<T>): Promise<Result<T>> { // turn a promise into a Result
  try { return { ok: true, data: await p }; } // success branch
  catch (e) { return { ok: false, error: e instanceof Error ? e as HttpError : new Error(String(e)) }; } // failure branch
}

// Typed endpoint map: route key decides request body and response type
interface Api { // contract shared with the backend
  "GET /orders": { res: Order[] }; // no body
  "POST /orders": { body: { items: string[] }; res: Order }; // has body
}
type Method = "GET" | "POST"; // allowed verbs

async function call<K extends keyof Api>( // K is the route
  route: K, // e.g. "POST /orders"
  ...args: Api[K] extends { body: infer B } ? [body: B] : [] // body required only for routes that declare it
): Promise<Api[K]["res"]> {
  const [method, path] = route.split(" ") as [Method, string]; // split "POST /orders"
  const init: RequestInit = { method }; // base options
  if (args.length) { init.body = JSON.stringify(args[0]); init.headers = { "Content-Type": "application/json" }; } // attach body
  const res = await fetch(path, init); // network
  if (!res.ok) throw new HttpError(res.status, await res.text()); // failure
  return (await res.json()) as Api[K]["res"]; // typed result
}

globalThis.fetch = (async () => new Response(JSON.stringify({ id: 1, total: 250, items: ["dosa"] }), { status: 200 })) as typeof fetch; // fake

async function main() { // demo
  const order = await requestValidated("/orders/1", OrderSchema); // order: Order, validated at runtime
  console.log(order.items[0]); // prints dosa
  const r = await safe(requestValidated("/orders/1", z.object({ id: z.string() }))); // wrong schema on purpose
  console.log(r.ok ? "ok" : r.error.name); // prints ZodError
  const created = await call("POST /orders", { items: ["idli"] }); // body REQUIRED and typed
  console.log(created.id); // prints 1
}
main(); // start
```

---

## 🟠 Node/Express + React Integration

```typescript
// shared-contract.ts — share the schema between Express and the React client
import { z } from "zod"; // runtime + types
import express from "express"; // express + types

export const CreateOrderBody = z.object({ items: z.array(z.string()).min(1) }); // one schema
export type CreateOrderBody = z.infer<typeof CreateOrderBody>; // type derived from it

const app = express(); // server side
app.use(express.json()); // JSON body
app.post("/orders", (req, res) => {
  const parsed = CreateOrderBody.safeParse(req.body); // validate the incoming body
  if (!parsed.success) { res.status(400).json(parsed.error.flatten()); return; } // 400 with details
  res.status(201).json({ id: 1, total: 100, items: parsed.data.items }); // typed access to items
});
// the React client imports CreateOrderBody (type + schema) and uses it with api.post<Order, CreateOrderBody>
```

```tsx
// useOrder.tsx — React hook around the typed wrapper with loading/error state
import { useEffect, useState } from "react"; // hooks

interface Order { id: number; total: number } // response shape

type State<T> = { status: "loading" } | { status: "error"; message: string } | { status: "ok"; data: T }; // discriminated union

export function useGet<T>(url: string): State<T> { // generic hook, caller picks T
  const [state, setState] = useState<State<T>>({ status: "loading" }); // starts loading
  useEffect(() => {
    const ctrl = new AbortController(); // cancel on unmount / url change
    fetch(url, { signal: ctrl.signal }) // request
      .then((r) => (r.ok ? (r.json() as Promise<T>) : Promise.reject(new Error(`HTTP ${r.status}`)))) // check status first
      .then((data) => setState({ status: "ok", data })) // success
      .catch((e: unknown) => { // failure (also fires on abort)
        if (!ctrl.signal.aborted) setState({ status: "error", message: e instanceof Error ? e.message : "unknown" }); // ignore aborts
      });
    return () => ctrl.abort(); // cleanup
  }, [url]);
  return state; // component narrows on state.status
}

export function OrderView({ id }: { id: number }) { // usage
  const s = useGet<Order>(`/api/orders/${id}`); // s: State<Order>
  if (s.status === "loading") return <p>Loading</p>; // narrow 1
  if (s.status === "error") return <p>{s.message}</p>; // narrow 2
  return <p>Total {s.data.total}</p>; // narrow 3: data exists only here
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Believing `fetch` rejects on HTTP errors
```typescript
// wrong-status.ts
async function wrong(url: string) {
  const data = await (await fetch(url)).json(); // wrong: a 500 error body is silently treated as data
  return data;
}
async function right(url: string) {
  const res = await fetch(url); // right: check ok first
  if (!res.ok) throw new Error(`HTTP ${res.status}`); // reject on 4xx/5xx
  return res.json() as Promise<unknown>; // unknown forces validation by the caller
}
console.log(typeof wrong, typeof right); // prints function function
```

❌ Mistake 2: Treating `<T>` as validation
✅ Correct: `get<Order>()` only **tells** the compiler what to assume. If the server returns something else, you crash later at `order.total.toFixed`. Validate with Zod (`schema.parse`) at the boundary.

❌ Mistake 3: Returning `any` from the wrapper
```typescript
// wrong-any.ts
async function bad(url: string) { return (await fetch(url)).json(); } // returns Promise<any>
async function good(url: string): Promise<unknown> { return (await fetch(url)).json(); } // forces narrowing
async function demo() {
  const a = await bad("/x"); // a: any
  a.anything.goes.here(); // compiles, crashes at runtime
  const g = await good("/x"); // g: unknown
  // ❌ cannot use unknown without narrowing
  g.id;
  // error TS18046: 'g' is of type 'unknown'.
}
demo(); // compile-only
```

---

## 🧠 Tricky Interview Question

```typescript
// tricky.ts — what is the type of `x`, and is that sensible?
async function get<T>(url: string): Promise<T> { return (await fetch(url)).json() as Promise<T>; } // wrapper
async function demo() {
  const x = await get("/anything"); // no <T> given
  const y: string = await get("/anything"); // T inferred from the declared variable type
  console.log(typeof x, typeof y); // prints (at runtime depends on server)
}
demo(); // compile-only
```
**Answer:** `x` is **`unknown`**: when `T` has no inference sites it defaults to its constraint, which is `unknown`. `y` compiles because TypeScript infers `T = string` from the **return-type context** (contextual typing from the annotation). That is a trap: `const y: string = await get(...)` *looks* checked but is just as unproven as `get<string>`. A function whose generic appears **only in the return type** is effectively a type assertion in disguise, which is why senior reviewers push for schema-driven return types (`z.infer<S>`) where `T` is tied to an **argument**.

---

## ⚫ Interview Questions + Answers

Q1: Why does `res.json()` return `any`, and what do you do about it?
A1: `JSON.parse` can return anything, so the DOM lib types it as `Promise<any>` for convenience. Immediately assign it to `unknown` (or pass through a schema) so you must narrow or validate before use.

Q2: Does `fetch` reject on a 404?
A2: No. It only rejects on network failure/abort. Check `res.ok` (or `res.status`) and throw your own `HttpError`.

Q3: Generic `<T>` on a return type: is that type-safe?
A3: It is a **claim**, equivalent to `as T`. Real safety comes from runtime validation (Zod, Valibot) where `T = z.infer<typeof schema>`, so the type and the check cannot drift.

Q4: How do you type a POST helper?
A4: `post<TRes, TBody>(url, body: TBody): Promise<TRes>`. Default `TBody = unknown`, or tie both to an endpoint map (`Api[K]["body"]`, `Api[K]["res"]`) so the route decides both.

Q5: How do you cancel requests and avoid race conditions in React?
A5: Pass an `AbortController.signal` to `fetch`, abort in the effect cleanup, and ignore `AbortError`. Libraries like React Query / RTK Query do this and also dedupe and cache.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any app with more than a few API calls (auth header, base URL, error mapping in one place)
- Sharing Zod schemas/types between Express and React in a monorepo

❌ Avoid when:
- You already use RTK Query / React Query / tRPC, they provide typed fetching with caching
- Streaming/binary responses (use `res.body` / `res.blob()` directly)

---

## 📊 Visual Diagram
```
 React component ──► api.get<Order>("/orders/1")
                         │
                         ▼
                request<T>(url, init)
                  │ fetch()
                  ▼
        res.ok? ──no──► throw HttpError(status, body)
          │ yes
          ▼
   schema.parse(json)? ──fail──► throw ZodError
          │ pass
          ▼
   Promise<T>   (T = z.infer<Schema>)    <-- only "proven" when validated

 `<T>` alone = compile-time CLAIM      `schema` = runtime PROOF
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Generic `<T>` | Type chosen by the caller | Caller द्वारा चुना type |
| `HttpError` | Exception carrying status/body | Status/body वाली exception |
| `z.infer` | Derive TS type from Zod schema | Zod schema से TS type |
| `unknown` | Safe top type, must narrow | Safe top type, narrow करना ज़रूरी |
| `AbortController` | Cancels an in-flight request | Chalu request रद्द करता है |
| Result type | Success/failure as a value | Success/failure value के रूप में |

---

## ⚡ 3-Line Summary
English:
1. Wrap `fetch` once: check `res.ok`, throw `HttpError`, return `Promise<T>` with `unknown` internally.
2. `<T>` on its own is only a claim; use `schema.parse` with `z.infer<S>` so type and validation come from one source.
3. In React add `AbortController`, and model loading/error/ok as a discriminated union.

Hindi:
1. `fetch` को एक बार wrap करो: `res.ok` check, `HttpError` throw, अंदर `unknown` रखकर `Promise<T>` लौटाओ।
2. अकेला `<T>` सिर्फ दावा है; `schema.parse` और `z.infer<S>` इस्तेमाल करो ताकि type और validation एक ही source से आएं।
3. React में `AbortController` जोड़ो और loading/error/ok को discriminated union बनाओ।

---

## ➡️ Next Topic
**106. Typed Redux Slice from Scratch** — build a tiny `createSlice` yourself to understand how RTK infers actions from reducers.
