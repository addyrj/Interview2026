# 176. API Routes in Next.js
# हिंदी में: Next.js में API Routes — Route Handlers से Backend Endpoints बनाना

---

## 🔵 Simple Definition (English)
**API Routes** (in the App Router they are called **Route Handlers**) let you write backend HTTP endpoints inside your Next.js app. You create a `route.js` file and export functions named `GET`, `POST`, `PUT`, `DELETE`, and Next.js turns them into an API at that URL.

## 🔵 सरल परिभाषा (Hindi)
**API Routes** (App Router में इन्हें **Route Handlers** कहते हैं) से आप अपने Next.js app के अंदर ही backend HTTP endpoints लिख सकते हैं। आप `route.js` file बनाते हैं और उसमें `GET`, `POST`, `PUT`, `DELETE` नाम के functions export करते हैं, और Next.js उस URL पर API चला देता है।

---

## 🔴 Problem it Solves

Earlier, a React frontend needed a separate Express server for even small things: a webhook from Razorpay, a form submission, a search suggestion endpoint. That meant two repos, two deployments, CORS problems and duplicated config. Route Handlers keep the backend next to the frontend, share the same deploy, and run on the server so secrets (database URL, API keys) never reach the browser.

```jsx
// PROBLEM: separate Express server just for one endpoint
// frontend (port 3000) → CORS → backend (port 5000) → database

// SOLUTION: one file inside the Next.js app
// app/api/hello/route.js
export async function GET() {
  return Response.json({ message: 'Hello from Next.js' }); // served at /api/hello
}
```

## 🔴 यह क्यों बना? (Hindi)
पहले एक छोटे से काम (Razorpay का webhook, form submit, search suggestion) के लिए भी React frontend को अलग Express server चाहिए था। मतलब दो repos, दो deployments, CORS की दिक्कतें और दोहराया हुआ config। Route Handlers backend को frontend के साथ ही रखते हैं, एक ही deploy होता है, और code server पर चलता है इसलिए secrets (database URL, API keys) browser तक नहीं पहुँचते।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a folder under app/api/... with a file named route.js (or route.ts)
Step 2 → Export async functions named after HTTP methods: GET, POST, PUT, PATCH, DELETE
Step 3 → Each function receives a Request (Web standard) and a context with params
Step 4 → Read input: request.json(), request.nextUrl.searchParams, request.headers
Step 5 → Return a Response (or NextResponse) with data and a status code
Step 6 → Next.js maps the folder path to the URL: app/api/orders/route.js → /api/orders

Rules: a route.js cannot live in the same folder as a page.js for the same path
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → app/api/... के नीचे folder बनाओ और उसमें route.js (या route.ts) file रखो
Step 2 → HTTP method के नाम वाले async functions export करो: GET, POST, PUT, PATCH, DELETE
Step 3 → हर function को एक Request (Web standard) और params वाला context मिलता है
Step 4 → Input पढ़ो: request.json(), request.nextUrl.searchParams, request.headers
Step 5 → data और status code के साथ Response (या NextResponse) return करो
Step 6 → Next.js folder path को URL बना देता है: app/api/orders/route.js → /api/orders

नियम: एक ही path पर page.js और route.js साथ नहीं रह सकते
```

---

## 🟡 Real World Example
**Swiggy order tracking:** The mobile app and the website both call `GET /api/orders/123/status` to know where the delivery partner is. The same Next.js app also exposes `POST /api/webhooks/payment` which the payment gateway calls when a payment succeeds. Both are Route Handlers: one serves your own UI, the other receives events from a third party, and neither exposes the database credentials to the browser.

## 🟡 Real Example Hindi mein
**Swiggy order tracking:** Mobile app और website दोनों `GET /api/orders/123/status` call करते हैं ताकि पता चले delivery partner कहाँ है। वही Next.js app `POST /api/webhooks/payment` भी देता है जिसे payment gateway पेमेंट सफल होने पर call करता है। दोनों Route Handlers हैं: एक आपके UI को data देता है, दूसरा third party से events लेता है, और database credentials कहीं browser में नहीं जाते।

---

## 💻 Code Example — Basic

```jsx
// app/api/products/route.js  → available at /api/products
import { NextResponse } from 'next/server';          // helper for JSON responses and cookies

const products = [                                    // fake in-memory data (use a DB in real apps)
  { id: 1, name: 'iPhone 15', price: 79900 },         // product 1
  { id: 2, name: 'Boat Earbuds', price: 1499 },       // product 2
];

export async function GET(request) {                  // handles GET /api/products
  const { searchParams } = request.nextUrl;           // read the query string
  const q = searchParams.get('q')?.toLowerCase() ?? ''; // ?q=boat → "boat"
  const result = products.filter(p => p.name.toLowerCase().includes(q)); // simple search
  return NextResponse.json(result);                   // 200 OK with JSON body
}

export async function POST(request) {                 // handles POST /api/products
  const body = await request.json();                  // parse the JSON request body
  if (!body.name || typeof body.price !== 'number') { // basic validation
    return NextResponse.json({ error: 'name and price required' }, { status: 400 }); // bad request
  }
  const created = { id: products.length + 1, ...body }; // pretend to save it
  products.push(created);                             // store in memory
  return NextResponse.json(created, { status: 201 }); // 201 Created
}
```

## 💻 Code Example — Advanced

```jsx
// app/api/orders/[id]/route.js → dynamic route: /api/orders/123
import { NextResponse } from 'next/server';           // JSON + cookies helper
import { cookies } from 'next/headers';               // read request cookies on the server

// Fake DB helpers (replace with Prisma, see topic 185)
const db = new Map([['123', { id: '123', userId: 'u1', status: 'OUT_FOR_DELIVERY' }]]);

// Next.js 15+: params is a Promise. In Next.js 14 it is a plain object (version-dependent).
export async function GET(request, { params }) {
  const { id } = await params;                        // read the dynamic segment
  const session = (await cookies()).get('session')?.value; // Next.js 15+: cookies() is async
  if (!session) {                                     // not logged in
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  const order = db.get(id);                           // look up the order
  if (!order) {                                       // unknown id
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }
  return NextResponse.json(order, {                   // success response
    headers: { 'Cache-Control': 'private, max-age=5' }, // short private cache
  });
}

export async function PATCH(request, { params }) {    // update the order status
  const { id } = await params;                        // dynamic segment
  let body;
  try {
    body = await request.json();                      // body may be invalid JSON
  } catch {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 });
  }
  const allowed = ['PREPARING', 'OUT_FOR_DELIVERY', 'DELIVERED']; // whitelist of statuses
  if (!allowed.includes(body.status)) {               // never trust client input
    return NextResponse.json({ error: 'Bad status' }, { status: 422 });
  }
  const order = db.get(id);
  if (!order) return NextResponse.json({ error: 'Not found' }, { status: 404 });
  order.status = body.status;                         // apply the change
  return NextResponse.json(order);                    // return the updated order
}

export async function DELETE(_request, { params }) {  // cancel an order
  const { id } = await params;
  db.delete(id);                                      // remove it
  return new Response(null, { status: 204 });         // 204 No Content
}
```

---

## 🟠 Real App Integration

Call the handler from a Client Component with `fetch`. In Server Components you usually do NOT call your own API; call the database or a shared function directly, which saves a network hop.

```jsx
// app/orders/TrackOrder.jsx
'use client';                                          // uses hooks, so it is a Client Component
import { useEffect, useState } from 'react';

export default function TrackOrder({ id }) {
  const [order, setOrder] = useState(null);            // order data from our own API
  const [error, setError] = useState(null);            // error message if any

  useEffect(() => {
    const controller = new AbortController();          // cancel fetch on unmount
    fetch(`/api/orders/${id}`, { signal: controller.signal })
      .then(res => (res.ok ? res.json() : Promise.reject(new Error(res.statusText))))
      .then(setOrder)                                  // save the data
      .catch(e => { if (e.name !== 'AbortError') setError(e.message); }); // ignore aborts
    return () => controller.abort();                   // cleanup
  }, [id]);

  if (error) return <p>Error: {error}</p>;             // error UI
  if (!order) return <p>Loading...</p>;                // loading UI
  return <p>Order {order.id}: {order.status}</p>;      // success UI
}
```

Caching note (version-dependent): in Next.js 14, `GET` handlers without dynamic input were cached by default. In Next.js 15, `GET` handlers are NOT cached by default; opt in with `export const dynamic = 'force-static'`.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using the old Pages Router style (`export default function handler(req, res)`) inside `app/`
✅ **Correct:** In the App Router, export named functions per HTTP method

```jsx
// Wrong: pages/api style does not work in app/api/.../route.js
export default function handler(req, res) {       // ❌ ignored in App Router
  res.status(200).json({ ok: true });
}

// Right: named method exports returning a Response
export async function GET() {                      // ✅ handles GET
  return Response.json({ ok: true });
}
```

❌ **Mistake 2:** Trusting request data without validation, and returning 200 for errors
✅ **Correct:** Validate input and return correct status codes (400, 401, 404, 422)

```jsx
// Wrong: crashes with a 500 if the body is empty, trusts the client
export async function POST(request) {
  const { qty } = await request.json();           // ❌ throws on invalid JSON
  return Response.json({ total: qty * 100 });     // ❌ qty could be a string or negative
}

// Right: guard and validate
export async function POST(request) {
  const body = await request.json().catch(() => null); // ✅ null on invalid JSON
  if (!body || !Number.isInteger(body.qty) || body.qty < 1) {
    return Response.json({ error: 'qty must be a positive integer' }, { status: 422 });
  }
  return Response.json({ total: body.qty * 100 });
}
```

---

## 🧠 Tricky Interview Question

```jsx
// app/api/hello/route.js
export async function GET() {
  return Response.json({ time: Date.now() });
}

// app/api/hello/page.js  (also exists)
export default function Page() { return <p>hi</p>; }
```
**Answer:** Next.js reports a build/dev error: a `route.js` and a `page.js` cannot exist at the same route segment, because both claim the same URL and one would answer HTML while the other answers an API response. The fix is to put the API under a different path (for example `app/api/hello/route.js` and a page at `app/hello/page.js`). A related gotcha: in Next.js 14 a plain `GET` like the one above could be statically cached at build time, so `time` would never change in production. In Next.js 15 it is dynamic by default (version-dependent).

---

## ⚫ Interview Questions + Answers

Q1: What are Route Handlers in Next.js?
A1: Functions in a `route.js` file inside `app/` that handle HTTP methods (`GET`, `POST`, etc.) using the Web `Request` and `Response` APIs. They are the App Router replacement for `pages/api`.

Q2: What is the difference between API Routes in the Pages Router and Route Handlers?
A2: Pages Router uses a default-exported `handler(req, res)` in `pages/api` with Node-style `req` and `res`. Route Handlers use named exports per method with the Web standard `Request` and `Response`, support Edge and Node runtimes, and live in `app/`.

Q3: Should a Server Component call your own Route Handler?
A3: Usually no. Server Components run on the server already, so they should call the database or a shared function directly. Calling your own API adds an extra network request and no benefit. Route Handlers are for clients, webhooks and third parties.

Q4: How do you read the body, query and params?
A4: Body with `await request.json()` (or `formData()`, `text()`), query with `request.nextUrl.searchParams`, dynamic params from the second argument `{ params }` (a Promise in Next.js 15+), headers with `request.headers` or `headers()`.

Q5: Are Route Handlers cached?
A5: In Next.js 14, `GET` handlers that did not use `Request` or dynamic functions were cached by default. In Next.js 15 this default changed to uncached. You can opt in with `export const dynamic = 'force-static'` or `revalidate` (version-dependent).

---

## 🔷 When to Use + When Not to Use
✅ **Use Route Handlers when:**
- A client (mobile app, browser `fetch`) needs a JSON endpoint
- You receive webhooks (Razorpay, Stripe, GitHub)
- You need a proxy to hide an API key from the browser

❌ **Avoid Route Handlers when:**
- A Server Component can read the data directly
- You only need form mutations (Server Actions are simpler, topic 184)
- You need long-running WebSocket servers (serverless does not suit that)

---

## 📊 Visual Diagram

```
  Browser / Mobile / Razorpay
          │  HTTP request
          ▼
  ┌──────────────────────────────┐
  │ Next.js server               │
  │  app/api/orders/[id]/route.js│
  │    GET  → read order         │
  │    PATCH→ update status      │
  │    DELETE→ cancel            │
  └──────────────┬───────────────┘
                 ▼
        Database / external API (secrets stay here)
                 │
                 ▼
          JSON Response (status code + body)

  Re-render behavior: Route Handlers have NO React rendering. They run once per
  request on the server. The calling Client Component re-renders only when its
  own state (data, error) changes.
  Performance: no extra server to deploy, but each call is a network request,
  so avoid calling your own API from Server Components.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Route Handler | `route.js` exporting HTTP method functions | HTTP method वाले functions का route.js |
| NextResponse | Next.js helper extending Response | Response का Next.js helper |
| Dynamic segment | `[id]` folder name for variable path | `[id]` जैसा बदलने वाला path हिस्सा |
| Webhook | Third party calling your endpoint | तीसरे पक्ष का आपके endpoint को call करना |
| Status code | Number telling result (200, 404) | नतीजा बताने वाला नंबर |
| Request body | Data sent by the client | Client द्वारा भेजा गया data |
| force-static | Opt in to static caching of a handler | Handler को static cache करना |
| CORS | Browser rule for cross-origin calls | दूसरे origin से calls का browser नियम |

---

## ⚡ 3-Line Summary
**English:**
1. Route Handlers are `route.js` files that export `GET`, `POST` and other HTTP method functions using Web `Request` and `Response`.
2. They give you a backend inside the same Next.js app, with secrets staying on the server.
3. Validate input, return correct status codes, and do not call your own API from Server Components.

**Hindi:**
1. Route Handlers ऐसी `route.js` files हैं जो Web `Request` और `Response` के साथ `GET`, `POST` आदि functions export करती हैं।
2. ये उसी Next.js app में backend देते हैं, और secrets server पर ही रहते हैं।
3. Input validate करो, सही status codes दो, और Server Components से अपनी ही API call मत करो।

---

## ➡️ Next Topic
**177. Middleware in Next.js** — request पूरा होने से पहले उसे रोककर redirect, rewrite, auth check या headers add करना, और `matcher` से यह तय करना कि middleware किन paths पर चले।
