# 88. Typed fetch / axios API Client
# हिंदी में: Typed fetch / axios API Client

> Verified with **TypeScript 5.9.x**, `axios` 1.x types, zod 4.x, Node 20+ global `fetch`. Outputs are real `tsx` runs against a mocked `fetch`.

---

## 🔵 Simple Definition (English)
A **typed API client** is one small module that wraps `fetch` (or `axios`) so every call has a **known request type and response type**, handles errors in one place, and exposes functions like `api.getOrder(id)` instead of raw URLs. The key trap: `res.json()` returns `Promise<any>` and `axios.get<T>()`'s `T` is just a promise to the compiler — neither validates the data at runtime.

## 🔵 सरल परिभाषा (Hindi)
**Typed API client** एक छोटा module है जो `fetch` (या `axios`) को wrap करता है ताकि हर call का **request type और response type पता हो**, errors एक जगह संभलें, और raw URLs की जगह `api.getOrder(id)` जैसे functions मिलें। असली जाल: `res.json()` `Promise<any>` लौटाता है और `axios.get<T>()` का `T` बस compiler से किया वादा है — दोनों runtime पर data validate **नहीं** करते।

---

## 🔴 Problem it Solves
Raw `fetch` scattered across React components means: copy-pasted headers/auth tokens, `fetch` not rejecting on 404/500 (a classic bug), `any` flowing from `res.json()` into Redux state, and typos in URLs. A typed client centralizes base URL, auth, timeouts, error mapping, and gives components `Promise<Order>` — and with zod, data that **is** an `Order`.

## 🔴 यह क्यों बना? (Hindi)
React components में बिखरा raw `fetch` मतलब: copy-paste headers/auth tokens, `fetch` का 404/500 पर reject न होना (classic bug), `res.json()` का `any` Redux state में घुसना, और URL typos। Typed client base URL, auth, timeouts, error mapping एक जगह रखता है और components को `Promise<Order>` देता है — और zod के साथ ऐसा data जो **सच में** `Order` है।

---

## 🟢 How it Works — Step by Step

Step 1 → Define wire types (or zod schemas) for each endpoint: `Order`, `CreateOrderBody`.
Step 2 → Write a generic core: `request<T>(method, path, body?, schema?) : Promise<T>`.
Step 3 → Core builds URL (base + path + query via `URLSearchParams`), sets JSON headers, adds the auth token, applies timeout with `AbortSignal.timeout`.
Step 4 → Check `res.ok`; if not, parse the error body and throw a typed `ApiError` (`status`, `code`).
Step 5 → Parse JSON; if a zod `schema` is passed, `schema.parse(json)` so `T` is **proven**, else cast (trusting server).
Step 6 → Export thin typed functions (`getOrder`, `createOrder`) — components/Redux thunks use only these.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → हर endpoint के wire types (या zod schemas) define करो: `Order`, `CreateOrderBody`।
Step 2 → Generic core लिखो: `request<T>(method, path, body?, schema?) : Promise<T>`।
Step 3 → Core URL बनाता है (base + path + `URLSearchParams` से query), JSON headers, auth token, और `AbortSignal.timeout` से timeout लगाता है।
Step 4 → `res.ok` check करो; नहीं तो error body parse करके typed `ApiError` (`status`, `code`) throw करो।
Step 5 → JSON parse करो; zod `schema` दिया हो तो `schema.parse(json)` ताकि `T` **सिद्ध** हो, वरना cast (server पर भरोसा)।
Step 6 → पतले typed functions export करो (`getOrder`, `createOrder`) — components/Redux thunks सिर्फ इन्हें इस्तेमाल करें।

---

## 🟡 Real World Example
A **Paytm-style wallet app** calls `GET /wallet/balance`, `POST /transfers`, `GET /transactions?page=2`. One `apiClient.ts` adds the bearer token, retries nothing it should not (POST transfers are **not** auto-retried to avoid double debit), maps 401 to a logout action, and returns typed `Transaction[]`. Components never see `fetch`.

## 🟡 Real Example Hindi mein
**Paytm जैसा wallet app** `GET /wallet/balance`, `POST /transfers`, `GET /transactions?page=2` call करता है। एक `apiClient.ts` bearer token लगाता है, जो retry नहीं होना चाहिए उसे retry नहीं करता (POST transfers auto-retry **नहीं** होते ताकि दोहरा debit न हो), 401 को logout action से map करता है, और typed `Transaction[]` लौटाता है। Components कभी `fetch` नहीं देखते।

---

## 💻 Code Example — Basic

```typescript
// ❌ Mistake: forgetting that an un-awaited call returns a Promise, so `.id` does not exist
async function get<T>(url: string): Promise<T> {
  const r = await fetch(url);                 // fetch returns Response
  return r.json();                            // r.json() is Promise<any> -> silently becomes T (unchecked!)
}
interface Order { id: string }
const o = get<Order>("/o");
console.log(o.id);
// error TS2339: Property 'id' does not exist on type 'Promise<Order>'.
```

```typescript
// api-basic.ts — a minimal generic fetch wrapper. Run: npx tsx api-basic.ts
class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); } // keep HTTP status
}

// T = the response type the CALLER expects (a promise to the compiler, not a guarantee)
async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...init,                                                  // method, body, etc.
    headers: { "Content-Type": "application/json", ...init?.headers }, // default JSON header
  });
  if (!res.ok) throw new ApiError(res.status, `HTTP ${res.status}`);    // fetch does NOT reject on 4xx/5xx!
  return (await res.json()) as T;                             // res.json() is any -> assert T
}

interface Order { id: string; total: number }

// --- demo with a fake fetch so the file runs offline ---
globalThis.fetch = (async (url: string | URL | Request) => {
  const ok = String(url).endsWith("/orders/o1");
  return new Response(ok ? JSON.stringify({ id: "o1", total: 450 }) : "{}", { status: ok ? 200 : 404 });
}) as typeof fetch;

const order = await request<Order>("/orders/o1");            // top-level await (ESM)
console.log(order.total);                                    // real output: 450
try { await request<Order>("/orders/zzz"); }
catch (e) { console.log(e instanceof ApiError ? e.status : e); } // real output: 404
```

## 💻 Code Example — Advanced

```typescript
// api-advanced.ts — typed client: query params, zod-validated responses, timeout, auth, endpoint map
import { z } from "zod";

// 1) Schemas are the source of truth for response types
const OrderSchema = z.object({ id: z.string(), total: z.number(), status: z.enum(["pending", "paid"]) });
type Order = z.infer<typeof OrderSchema>;

class ApiError extends Error {
  constructor(public status: number, public code: string, message: string) { super(message); }
}

// 2) Core: schema is a runtime validator that also fixes the return type
async function request<S extends z.ZodType>(
  method: "GET" | "POST" | "PUT" | "DELETE",
  path: string,
  opts: { schema: S; body?: unknown; query?: Record<string, string | number | undefined>; token?: string },
): Promise<z.output<S>> {
  const qs = new URLSearchParams();                                   // builds ?a=1&b=2 safely (encodes values)
  for (const [k, v] of Object.entries(opts.query ?? {})) if (v !== undefined) qs.set(k, String(v));
  const url = `https://api.example.in${path}${qs.size ? `?${qs}` : ""}`; // base + path + query

  const res = await fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(opts.token ? { Authorization: `Bearer ${opts.token}` } : {}), // conditional header
    },
    body: opts.body === undefined ? undefined : JSON.stringify(opts.body), // only send body when present
    signal: AbortSignal.timeout(8000),                                  // abort after 8s (Node 18+/modern browsers)
  });

  if (!res.ok) {                                                        // map HTTP failure to typed error
    const err = (await res.json().catch(() => ({}))) as { code?: string; message?: string };
    throw new ApiError(res.status, err.code ?? "HTTP_ERROR", err.message ?? res.statusText);
  }
  return opts.schema.parse(await res.json());                           // runtime proof, not a cast
}

// 3) The only API the app uses: small typed functions
export const api = {
  getOrder: (id: string, token: string): Promise<Order> =>
    request("GET", `/orders/${encodeURIComponent(id)}`, { schema: OrderSchema, token }),
  listOrders: (page: number, token: string): Promise<Order[]> =>
    request("GET", "/orders", { schema: z.array(OrderSchema), query: { page }, token }),
  createOrder: (body: { sku: string; qty: number }, token: string): Promise<Order> =>
    request("POST", "/orders", { schema: OrderSchema, body, token }),
};

// --- offline demo with fake fetch ---
globalThis.fetch = (async (url: string | URL | Request) => {
  console.log("GET", String(url));
  return new Response(JSON.stringify([{ id: "o1", total: 450, status: "paid" }]), { status: 200 });
}) as typeof fetch;
console.log(await api.listOrders(2, "tok"));
// real output:
// GET https://api.example.in/orders?page=2
// [ { id: 'o1', total: 450, status: 'paid' } ]
```

```typescript
// axios variant — the generic goes on the CALL; interceptors centralize auth + errors
import axios, { AxiosError, type AxiosInstance } from "axios";

interface Order { id: string; total: number }
interface ApiErrorBody { code: string; message: string }

export function createClient(getToken: () => string | null): AxiosInstance {
  const http = axios.create({ baseURL: "https://api.example.in", timeout: 8000 }); // shared config
  http.interceptors.request.use((cfg) => {
    const t = getToken();                              // read latest token (Redux store / storage)
    if (t) cfg.headers.set("Authorization", `Bearer ${t}`); // typed headers API (AxiosHeaders)
    return cfg;
  });
  return http;
}

export async function getOrder(http: AxiosInstance, id: string): Promise<Order> {
  try {
    const res = await http.get<Order>(`/orders/${id}`); // res.data: Order (unchecked, like `as Order`)
    return res.data;                                    // axios already throws on 4xx/5xx
  } catch (e) {                                         // e: unknown
    if (axios.isAxiosError<ApiErrorBody>(e)) {          // type guard from axios
      throw new Error(e.response?.data.message ?? e.message); // e.response.data typed ApiErrorBody
    }
    throw e;                                            // not an axios error: rethrow
  }
}
```

---

## 🟠 Node/Express + React Integration

```typescript
// web/src/store/ordersSlice.ts — Redux Toolkit thunk uses ONLY the typed client (topic 94)
import { createAsyncThunk } from "@reduxjs/toolkit";

interface Order { id: string; total: number }
// stand-in for: import { api } from "../api"
declare const api: { getOrder(id: string, token: string): Promise<Order> };

export const fetchOrder = createAsyncThunk<Order, { id: string; token: string }>(
  "orders/fetch",                                   // action type prefix
  async ({ id, token }) => api.getOrder(id, token), // return type must be Order; thrown error => rejected action
);
```

```typescript
// web/src/useOrder.ts — a typed hook: loading | error | data as a discriminated union (topic 26)
import { useEffect, useState } from "react";

interface Order { id: string; total: number }
type State = { status: "loading" } | { status: "error"; message: string } | { status: "ok"; data: Order };

export function useOrder(id: string, load: (id: string) => Promise<Order>): State {
  const [state, setState] = useState<State>({ status: "loading" }); // initial state
  useEffect(() => {
    let cancelled = false;                                          // avoid setState after unmount
    load(id)
      .then((data) => { if (!cancelled) setState({ status: "ok", data }); })
      .catch((e: unknown) => { if (!cancelled) setState({ status: "error", message: e instanceof Error ? e.message : "Failed" }); });
    return () => { cancelled = true; };                             // cleanup
  }, [id, load]);
  return state;                                                     // caller narrows by `status`
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assuming `fetch` rejects on HTTP errors. It only rejects on network failure. ✅ Always check `res.ok`.

❌ Mistake 2: Trusting `get<Order>()` / `res.json() as Order`. The generic is an assertion — a renamed backend field still "type-checks". ✅ Parse with zod at the client boundary for critical data (payments), or generate types from OpenAPI.

❌ Mistake 3: Awaiting nothing / forgetting `await` (see the real `TS2339` above) — `Promise<Order>` has no `.id`. ✅ `await` or `.then`.

❌ Mistake 4: Retrying non-idempotent calls automatically (POST /payments) → double charge. ✅ Retry only GET/idempotent calls, or send an `Idempotency-Key` header.

❌ Mistake 5: Catching with `catch (e: any)`. ✅ `unknown` + `axios.isAxiosError(e)` / `instanceof ApiError`.

❌ Mistake 6: Building query strings by hand (`"?q=" + text`) — unescaped input breaks URLs. ✅ `URLSearchParams`.

---

## 🧠 Tricky Interview Question
**Q:** "`const data = await res.json()` — what type is `data`, and what happens with `const data: Order = await res.json()`?"

**A:** `Response.json()` is declared as `Promise<any>`, so `data` is `any`. Annotating `const data: Order = await res.json()` compiles with **no check at all**, because `any` is assignable to everything — it is a silent assertion. If the server returns `{ total: "450" }` the app crashes later at `data.total.toFixed`. Safer: type the result as `unknown` and parse with a schema (`OrderSchema.parse(await res.json())`), or at least a type guard. Some teams turn on the `@typescript-eslint/no-unsafe-assignment` rule to catch this.

---

## ⚫ Interview Questions + Answers

Q1: `fetch` vs `axios` — differences that matter?
A1: axios throws on non-2xx by default, auto-parses JSON, has interceptors/timeouts/cancel built in, and browser + Node adapters. `fetch` is built in (zero bundle cost), needs manual `res.ok` + `res.json()`, and uses `AbortSignal` for timeouts. Typing: both give `any`/unchecked data; axios lets `get<T>` generic (assertion).

Q2: How do you type a generic `get<T>` function properly?
A2: `async function get<T>(url: string): Promise<T>`. Better: accept a schema and infer `T` from it so the type is backed by runtime validation: `get<S extends z.ZodType>(url, schema: S): Promise<z.output<S>>`.

Q3: How do you cancel an in-flight request in React?
A3: Pass an `AbortSignal` (`new AbortController()`; abort in the effect cleanup) to `fetch`/axios (`signal`). Handle the `AbortError` (`e.name === "AbortError"`) without showing an error.

Q4: How do you keep client types in sync with the Express API?
A4: Shared types/zod schemas in a monorepo package, or generate from OpenAPI (`openapi-typescript`), or tRPC. Avoid hand-copying interfaces in two repos.

Q5: Where should the auth token come from?
A5: A function `getToken()` injected into the client (interceptor / header builder) reading the Redux store or secure storage at call time — not captured once at module load, so refresh works.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any React/Node code calling HTTP APIs more than once
- You want one place for auth, errors, timeouts, logging

❌ Avoid when:
- Single one-off call in a script (plain `fetch` + zod is enough)
- You already have generated clients (RTK Query, tRPC, OpenAPI codegen) — do not hand-write a parallel layer (topic 94)

---

## 📊 Visual Diagram
```
 Component / Thunk
      │ api.getOrder("o1")          : Promise<Order>
      ▼
 request<S>(method, path, {schema, body, query, token})
      │  URL + headers + auth + timeout(AbortSignal)
      ▼
   fetch ──► Express API
      │
   res.ok? ──no──► throw ApiError(status, code)
      │yes
   res.json()  : any
      │
   schema.parse(...)  ──► Order  (typed AND checked)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| API client | Module wrapping HTTP calls | HTTP calls को wrap करने वाला module |
| `Response.json()` | Returns `Promise<any>` | `Promise<any>` लौटाता है |
| `AbortSignal` | Cancels/limits a request | Request cancel/time-limit करता है |
| Interceptor | axios hook on request/response | axios का request/response hook |
| Idempotency | Same request repeated is safe | बार-बार भेजना सुरक्षित |
| `URLSearchParams` | Safe query-string builder | Safe query-string builder |
| Type assertion | Telling compiler a type | Compiler को type बताना |

---

## ⚡ 3-Line Summary
English:
1. Wrap `fetch`/axios in one typed client: base URL, auth, timeout, `res.ok` check, `ApiError`.
2. `res.json()` is `any` and `get<T>()` is an unchecked promise to the compiler — validate with zod for critical data.
3. Never auto-retry non-idempotent POSTs; use `URLSearchParams`, `AbortSignal`, and `unknown` in `catch`.

Hindi:
1. `fetch`/axios को एक typed client में wrap करो: base URL, auth, timeout, `res.ok` check, `ApiError`।
2. `res.json()` `any` है और `get<T>()` compiler से किया बिना-जाँच वादा है — ज़रूरी data के लिए zod से validate करो।
3. Non-idempotent POST को auto-retry कभी नहीं; `URLSearchParams`, `AbortSignal` और `catch` में `unknown` इस्तेमाल करो।

---

## ➡️ Next Topic
**89. Typing async/Promise Code** — `Promise<T>`, `Awaited`, `Promise.all` tuples, and async error typing.
