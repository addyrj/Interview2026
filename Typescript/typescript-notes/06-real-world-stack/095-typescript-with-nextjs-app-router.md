# 95. TypeScript with Next.js (App Router)
# हिंदी में: Next.js (App Router) के साथ TypeScript

> Verified with **TypeScript 5.9 (5.x)** and **Next.js 16.4** types (`next/server`, `next` Metadata). Since Next 15, `params` and `searchParams` are **Promises** - older tutorials show them as plain objects.

---

## 🔵 Simple Definition (English)
Next.js ships its own TypeScript types and a TS plugin. In the App Router (`app/` folder) you type: **pages** (`params`, `searchParams`), **layouts** (`children`), **route handlers** (`GET(req: NextRequest)` returning `Response`/`NextResponse`), **metadata** (`Metadata`), and **Server Actions** (`"use server"` async functions whose arguments cross the network). Server Components are plain `async` functions, so you can `await` data directly in them with full types.

## 🔵 सरल परिभाषा (Hindi)
Next.js अपने TypeScript types और TS plugin के साथ आता है। App Router (`app/` folder) में आप type करते हो: **pages** (`params`, `searchParams`), **layouts** (`children`), **route handlers** (`GET(req: NextRequest)` जो `Response`/`NextResponse` return करे), **metadata** (`Metadata`), और **Server Actions** (`"use server"` async functions जिनके arguments network पार करते हैं)। Server Components साधारण `async` functions हैं, इसलिए आप उनमें सीधे `await` से typed data ला सकते हो।

---

## 🔴 Problem it Solves
Next.js has many "magic" conventions (file names, exported function names, special props). In JS, a typo like `titel` in `metadata`, wrong `params` shape or a handler returning the wrong thing fails silently or at runtime. TypeScript + Next's types catch: invalid metadata keys, wrong handler signatures, un-awaited `params`, and mismatched server/client data. Server Actions are especially risky because their inputs come from the browser - types alone are not enough, you must validate.

## 🔴 यह क्यों बना? (Hindi)
Next.js में बहुत "magic" conventions हैं (file names, exported function names, special props)। JS में `metadata` में `titel` जैसी typo, गलत `params` shape या गलत return करने वाला handler चुपचाप या runtime पर fail होता है। TypeScript + Next के types पकड़ते हैं: गलत metadata keys, गलत handler signatures, बिना await किए `params`, और server/client data mismatch। Server Actions में खास जोखिम है क्योंकि inputs browser से आते हैं - सिर्फ types काफ़ी नहीं, validation ज़रूरी है।

---

## 🟢 How it Works — Step by Step
Step 1 → Create the project with TS (`create-next-app --ts`); Next generates `tsconfig.json` with the `next` plugin and `next-env.d.ts`.
Step 2 → Page: `export default async function Page({ params }: { params: Promise<{ id: string }> })` and `const { id } = await params`.
Step 3 → Layout: `{ children }: { children: React.ReactNode }`.
Step 4 → Route handler (`app/api/orders/route.ts`): `export async function GET(req: NextRequest)` returns `NextResponse.json(...)`.
Step 5 → Metadata: `export const metadata: Metadata = {...}` or `generateMetadata({ params })`.
Step 6 → Server Action: `"use server"` + typed args (validate with zod) + return a serializable result type.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Project TS के साथ बनाओ (`create-next-app --ts`); Next `next` plugin वाला `tsconfig.json` और `next-env.d.ts` generate करता है।
Step 2 → Page: `export default async function Page({ params }: { params: Promise<{ id: string }> })` और `const { id } = await params`।
Step 3 → Layout: `{ children }: { children: React.ReactNode }`।
Step 4 → Route handler (`app/api/orders/route.ts`): `export async function GET(req: NextRequest)` जो `NextResponse.json(...)` देता है।
Step 5 → Metadata: `export const metadata: Metadata = {...}` या `generateMetadata({ params })`।
Step 6 → Server Action: `"use server"` + typed args (zod से validate) + serializable result type return करो।

---

## 🟡 Real World Example
**Swiggy-style restaurant page** at `app/restaurants/[id]/page.tsx`: it is a Server Component that `await`s `params`, queries SQL Server through a typed repository, and renders. The `app/api/orders/route.ts` handler serves mobile clients. A `placeOrder` Server Action receives a form submission, validates with zod, and returns `{ ok: true, orderId } | { ok: false, error }` which the client form narrows.

## 🟡 Real Example Hindi mein
**Swiggy जैसा restaurant page** `app/restaurants/[id]/page.tsx` पर: यह Server Component `params` को `await` करता है, typed repository से SQL Server query करता है और render करता है। `app/api/orders/route.ts` handler mobile clients को serve करता है। `placeOrder` Server Action form submission लेता है, zod से validate करता है, और `{ ok: true, orderId } | { ok: false, error }` return करता है जिसे client form narrow करता है।

---

## 💻 Code Example — Basic

```tsx
// app/restaurants/[id]/page.tsx — dynamic route page (Server Component)
import type { Metadata } from "next"; // Next's metadata type

interface Restaurant { id: string; name: string; rating: number } // domain type

// Pretend DB call; in real life this would query SQL Server
async function getRestaurant(id: string): Promise<Restaurant> {
  return { id, name: "Biryani House", rating: 4.5 };
}

// Since Next 15: params / searchParams are Promises
type PageProps = {
  params: Promise<{ id: string }>;                              // matches [id] folder name
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>; // query string
};

// Typed metadata - misspelled keys are compile errors
export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { id } = await params;                                   // await before use
  const r = await getRestaurant(id);
  return { title: r.name, description: `Rated ${r.rating}` };    // checked against Metadata
}

// Server Component: an async function that returns JSX
export default async function RestaurantPage({ params, searchParams }: PageProps) {
  const { id } = await params;                                   // id: string
  const sp = await searchParams;                                 // sp: record of string|string[]|undefined
  const sort = typeof sp.sort === "string" ? sp.sort : "popular"; // narrow before use
  const r = await getRestaurant(id);                              // r: Restaurant
  return <h1>{r.name} ({sort})</h1>;
}
```

## 💻 Code Example — Advanced

```typescript
// app/api/orders/route.ts — typed route handler (GET + POST), validated with zod
import { NextRequest, NextResponse } from "next/server"; // typed request / response helpers
import { z } from "zod";                                  // runtime validation

const OrderInput = z.object({
  restaurantId: z.string().min(1),                        // required id
  items: z.array(z.object({ sku: z.string(), qty: z.number().int().positive() })).min(1),
});
type OrderInput = z.infer<typeof OrderInput>;             // static type from the schema

interface OrderResponse { orderId: string; total: number } // response contract

export async function GET(req: NextRequest) {
  const status = req.nextUrl.searchParams.get("status");   // string | null
  return NextResponse.json({ status: status ?? "all" });   // returns Response
}

export async function POST(req: NextRequest): Promise<NextResponse<OrderResponse | { error: string }>> {
  const body: unknown = await req.json();                  // unknown, NOT any - forces validation
  const parsed = OrderInput.safeParse(body);               // runtime check
  if (!parsed.success) {
    return NextResponse.json({ error: parsed.error.issues[0]?.message ?? "bad input" }, { status: 400 });
  }
  const input: OrderInput = parsed.data;                   // fully typed after validation
  const total = input.items.reduce((s, i) => s + i.qty * 100, 0); // pretend pricing
  return NextResponse.json({ orderId: "ord_1", total }, { status: 201 }); // checked vs OrderResponse
}
```

```typescript
// app/actions.ts — Server Action with a discriminated-union result
"use server"; // marks every export as a Server Action

import { z } from "zod";

const Schema = z.object({ address: z.string().min(5), phone: z.string().regex(/^\d{10}$/) });

export type ActionResult =
  | { ok: true; orderId: string }              // success shape
  | { ok: false; error: string };              // failure shape

// formData comes from the browser: treat as untrusted
export async function placeOrder(formData: FormData): Promise<ActionResult> {
  const parsed = Schema.safeParse({
    address: formData.get("address"),           // FormDataEntryValue | null
    phone: formData.get("phone"),
  });
  if (!parsed.success) return { ok: false, error: "Invalid address or phone" };
  return { ok: true, orderId: `ord_${parsed.data.phone.slice(-4)}` }; // serializable result
}
```

---

## 🟠 Node/Express + React Integration

```tsx
// Client Component calling the Server Action and the typed route handler
"use client"; // runs in the browser

import { useState, type FormEvent } from "react";

type OrderResponse = { orderId: string; total: number }; // same contract as route.ts (share via a module)

export function QuickOrder() {
  const [msg, setMsg] = useState("");                    // UI message
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();                                   // no full page reload
    const res = await fetch("/api/orders", {              // Next route handler (or an Express URL)
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ restaurantId: "r1", items: [{ sku: "dosa", qty: 2 }] }),
    });
    if (!res.ok) { setMsg("failed"); return; }
    const data = (await res.json()) as OrderResponse;     // assert after ok-check; validate for untrusted APIs
    setMsg(`Order ${data.orderId}: ₹${data.total}`);
  }
  return <form onSubmit={submit}><button>Order</button><p>{msg}</p></form>;
}
```

```typescript
// Next can also proxy an existing Express/SQL Server API from a Server Component (BFF pattern)
interface Menu { id: number; name: string }
export async function getMenu(): Promise<Menu[]> {
  const r = await fetch(process.env.API_URL + "/menu", { cache: "no-store" }); // runs on the Next server
  if (!r.ok) throw new Error(`Menu failed: ${r.status}`);
  return (await r.json()) as Menu[];                       // cast, then validate if API is not yours
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Treating `params` as a plain object (Next 15+)
```tsx
// ❌ WRONG
export default function Page({ params }: { params: Promise<{ id: string }> }) {
  return <p>{params.id}</p>;
  // error TS2339: Property 'id' does not exist on type 'Promise<{ id: string; }>'.
}
```
✅ Correct: `export default async function Page({ params }...) { const { id } = await params; ... }`

❌ Mistake 2: Misspelled metadata key
```typescript
// ❌ WRONG
import type { Metadata } from "next";
const m: Metadata = { titel: "x" };
// error TS2561: Object literal may only specify known properties, but 'titel' does not exist in type 'Metadata'. Did you mean to write 'title'?
```

❌ Mistake 3: Trusting Server Action input types
A Server Action's TS parameter type is **not enforced at runtime** - anyone can POST any payload. ✅ Correct: accept `FormData` or `unknown` and validate with zod (as in the Advanced example).

❌ Mistake 4: Importing server-only code into a Client Component
Importing a module with DB credentials into a `"use client"` file bundles it for the browser (and leaks secrets). ✅ Correct: `import "server-only"` at the top of server-only modules so the build fails.

---

## 🧠 Tricky Interview Question

```tsx
// Can this Server Component accept an `onClick` prop from its parent Server Component?
export default function Card({ onClick }: { onClick: () => void }) {
  return <button onClick={onClick}>x</button>;
}
```
**Answer:** TypeScript is happy (it compiles), but Next fails **at runtime/build**: props passed from a Server Component to a **Client** Component must be *serializable*; functions are not (except Server Actions). TS cannot see the server/client boundary, so types alone do not protect you. Mark the component `"use client"` and create the handler there, or pass a Server Action. Interview point: the RSC boundary is a runtime concern; types only describe shapes.

---

## ⚫ Interview Questions + Answers

Q1: Why are `params` Promises in Next 15+?
A1: Next can start rendering before dynamic route info is known (partial prerendering / streaming), so request-specific APIs became async. You `await params`. Synchronous access was only a temporary compatibility shim in Next 15; with the Next 16 types used here it is a compile error (see Mistake 1).

Q2: How do you type `searchParams`?
A2: `Promise<{ [key: string]: string | string[] | undefined }>`. Narrow with `typeof sp.x === "string"` before using, because a repeated query key gives an array.

Q3: Route handler return types?
A3: Return a `Response` (or `NextResponse`). For typed JSON bodies use `Promise<NextResponse<MyBody>>`. Input comes from `req.json()` (typed `any`; annotate as `unknown` and validate).

Q4: How do you share types between Server and Client Components?
A4: Put plain types/interfaces/zod schemas in a shared module with no server-only imports. Types are erased, so they cross the boundary freely; only runtime values must be serializable.

Q5: What is the `next` TS plugin / `next-env.d.ts`?
A5: `next-env.d.ts` references Next's global types (images, CSS modules). The TS plugin in `tsconfig.json` validates things like `"use client"` placement and page/layout export types inside the editor and `next build` runs full type-checking.

---

## 🔷 When to Use + When Not to Use
✅ Use Next.js + TS when:
- You need SSR/SEO pages with typed data fetching on the server
- You want one repo for UI + BFF route handlers
- Forms with Server Actions (progressive enhancement)

❌ Avoid / be careful:
- Heavy dashboards fully client-side with an existing Express API (plain Vite + React may be simpler)
- Trusting TS types for security: always validate route/action inputs
- Long-running or stateful servers (WebSockets) - keep these in Node/Express/NestJS

---

## 📊 Visual Diagram
```
app/
 ├─ layout.tsx            ({ children }: { children: ReactNode })
 ├─ restaurants/[id]/
 │    └─ page.tsx         ({ params: Promise<{id:string}> })   async Server Component
 ├─ api/orders/route.ts   GET(req: NextRequest) -> NextResponse
 └─ actions.ts            "use server"  placeOrder(FormData) -> ActionResult

Browser ──► route handler / Server Action ──► validate (zod) ──► SQL Server
                  ▲ untrusted input: unknown → parsed → typed
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| App Router | `app/` folder routing | `app/` folder वाली routing |
| Server Component | Component rendered on server | server पर render होने वाला component |
| Route Handler | `route.ts` API endpoint | `route.ts` वाला API endpoint |
| Server Action | Server function called from UI | UI से call होने वाला server function |
| Metadata | Typed SEO/head info | typed SEO/head जानकारी |
| Serializable | Can cross network as data | network पर data की तरह जा सके |

---

## ⚡ 3-Line Summary
English:
1. Type pages with `params: Promise<...>` (Next 15+), layouts with `children: ReactNode`, handlers with `NextRequest`/`NextResponse`.
2. Metadata, route and action types catch typos at compile time; return discriminated-union results from actions.
3. Types are erased: validate every request/action input with zod; the server/client boundary is a runtime rule.

Hindi:
1. Pages को `params: Promise<...>` (Next 15+), layouts को `children: ReactNode`, handlers को `NextRequest`/`NextResponse` से type करो।
2. Metadata, route और action types typos को compile time पर पकड़ते हैं; actions से discriminated-union results return करो।
3. Types runtime पर नहीं रहते: हर request/action input zod से validate करो; server/client boundary runtime का नियम है।

---

## ➡️ Next Topic
**96. TypeScript with SQL Server — mssql Typing** — typed queries, parameters and recordsets.
