# 138. Server Components (RSC)
# हिंदी में: Server Components (RSC) — Server पर चलने वाले React Components

---

## 🔵 Simple Definition (English)
**React Server Components (RSC)** are components that run **only on the server** (at request time or build time). They can read databases and files directly, they send their rendered result (not their code) to the browser, and they add **zero JavaScript** to the client bundle. They cannot use state, effects or browser APIs.

## 🔵 सरल परिभाषा (Hindi)
**React Server Components (RSC)** ऐसे components हैं जो **सिर्फ server पर** चलते हैं (request के समय या build के समय)। ये database और files सीधे पढ़ सकते हैं, browser को अपना rendered नतीजा भेजते हैं (code नहीं), और client bundle में **शून्य JavaScript** जोड़ते हैं। इनमें state, effects या browser APIs नहीं चलते।

---

## 🔴 Problem it Solves

In classic client-side React, to show a product page the browser downloads a big JS bundle, runs it, then makes an API call (`useEffect` + `fetch`), then renders. This creates **waterfalls** (JS first, then data), large bundles (a Markdown or date library ships to every user), and secrets that must never reach the client. Server-side rendering (SSR) improved the first paint but still sent all component JS to the browser to hydrate.

```jsx
// PROBLEM (client-only React): bundle + waterfall
function Product({ id }) {
  const [p, setP] = useState(null);                       // empty at first
  useEffect(() => { fetch(`/api/p/${id}`).then(r => r.json()).then(setP); }, [id]); // fetch AFTER JS loads
  return p ? <h1>{p.name}</h1> : <Spinner />;             // user stares at a spinner
}
```

## 🔴 यह क्यों बना? (Hindi)
Classic client-side React में product page दिखाने के लिए browser पहले बड़ा JS bundle download करता है, चलाता है, फिर API call (`useEffect` + `fetch`) करता है, फिर render होता है। इससे **waterfall** (पहले JS, फिर data), बड़े bundles (Markdown या date library हर user को जाती है), और ऐसे secrets की समस्या बनती है जो client तक नहीं पहुँचने चाहिए। SSR ने पहला paint सुधारा, पर hydrate करने के लिए सारा component JS फिर भी browser को भेजना पड़ता था।

---

## 🟢 How it Works — Step by Step

```
Step 1 → A request arrives; React renders Server Components on the server
Step 2 → A Server Component can be async and await data (DB, fetch, file system) directly
Step 3 → React serializes the result into the RSC Payload (a compact tree description, not HTML)
Step 4 → Client Components ('use client') appear in the payload as references to JS chunks
Step 5 → The server also produces HTML from the payload for a fast first paint (SSR)
Step 6 → The browser shows HTML, loads only Client Component JS, then hydrates those parts
Step 7 → On navigation, the client fetches a new payload and React merges it, keeping client state

Re-render behavior: Server Components never re-render in the browser. They re-run only when the
server sends a new payload (navigation, router.refresh(), after a Server Action).
Performance impact: smaller bundles, fewer round trips, data next to the source; but every
server render costs CPU and needs a server (or cached output).
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Request आती है; React server पर Server Components render करता है
Step 2 → Server Component async हो सकता है और data (DB, fetch, file) सीधे await करता है
Step 3 → React नतीजे को RSC Payload में बदलता है (tree का compact वर्णन, HTML नहीं)
Step 4 → Client Components ('use client') payload में JS chunks के references की तरह आते हैं
Step 5 → Server उसी payload से तेज़ पहले paint के लिए HTML भी बनाता है (SSR)
Step 6 → Browser HTML दिखाता है, सिर्फ Client Component का JS लोड करता है, फिर उन्हें hydrate करता है
Step 7 → Navigation पर client नया payload लेता है और React उसे merge करता है, client state बनी रहती है

Re-render behavior: Server Components browser में कभी re-render नहीं होते। वे तभी दोबारा चलते हैं जब
server नया payload भेजे (navigation, router.refresh(), Server Action के बाद)।
Performance impact: छोटे bundles, कम round trips, data source के पास; पर हर server render में CPU लगता है।
```

---

## 🟡 Real World Example
**Amazon product page:** The title, price, description, specs and reviews list come from the database and are mostly static for the user. They are Server Components: no JS shipped for them, and the DB password stays on the server. The "Add to Cart" button, quantity selector and image zoom are Client Components, because they need `onClick`, state and browser events. The page loads fast and only the interactive parts become heavy.

## 🟡 Real Example Hindi mein
**Amazon product page:** Title, price, description, specs और reviews की list database से आती है और user के लिए ज़्यादातर static है। ये Server Components हैं: इनका JS नहीं जाता और DB password server पर ही रहता है। "Add to Cart" बटन, quantity selector और image zoom Client Components हैं, क्योंकि इन्हें `onClick`, state और browser events चाहिए। Page तेज़ खुलता है और सिर्फ interactive हिस्से भारी होते हैं।

---

## 💻 Code Example — Basic

```jsx
// Basic: an async Server Component (Next.js App Router, no 'use client' = server by default)
// app/products/page.jsx
async function getProducts() {
  const res = await fetch('https://fakestoreapi.com/products?limit=5'); // runs on the server only
  if (!res.ok) throw new Error('Failed to load products');              // error boundary will catch
  return res.json();                                                   // parsed JSON
}

export default async function ProductsPage() {       // async component: allowed only on the server
  const products = await getProducts();              // await directly, no useEffect, no loading state
  return (
    <ul>
      {products.map((p) => (                         // plain JSX list
        <li key={p.id}>{p.title} - ${p.price}</li>   // sent to the browser as rendered output
      ))}
    </ul>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// Advanced: Server Component + Client Component islands + Suspense streaming
// app/product/[id]/page.jsx  (Server Component)
import { Suspense } from 'react';                       // lets slow parts stream later
import AddToCart from './AddToCart';                    // Client Component (interactive)
import { db } from '@/lib/db';                          // server-only data layer (hypothetical)
import 'server-only';                                   // build error if imported in a client file

async function Reviews({ id }) {                        // slow section: streamed after the shell
  const reviews = await db.reviews.findMany({ where: { productId: id } }); // direct DB access
  return (
    <ul>{reviews.map((r) => <li key={r.id}>{r.stars}★ {r.text}</li>)}</ul>
  );
}

export default async function ProductPage({ params }) {
  const { id } = await params;                          // Next.js 15: params is a Promise
  const product = await db.products.findUnique({ where: { id } }); // fast, awaited first
  return (
    <main>
      <h1>{product.name}</h1>                           {/* server-rendered, no JS */}
      <p>Rs. {product.price}</p>
      <AddToCart productId={product.id} />              {/* client island: only this ships JS */}
      <Suspense fallback={<p>Loading reviews...</p>}>   {/* page shell shows immediately */}
        <Reviews id={id} />                             {/* streamed when ready */}
      </Suspense>
    </main>
  );
}
```

```jsx
// app/product/[id]/AddToCart.jsx  (Client Component)
'use client';                                           // boundary: this file and its imports go to the browser
import { useState } from 'react';

export default function AddToCart({ productId }) {     // props must be serializable (no functions)
  const [qty, setQty] = useState(1);                    // state is allowed here
  return (
    <div>
      <button onClick={() => setQty((q) => Math.max(1, q - 1))}>-</button>
      <span>{qty}</span>
      <button onClick={() => setQty((q) => q + 1)}>+</button>
      <button onClick={() => console.log('add', productId, qty)}>Add to Cart</button>
    </div>
  );
}
```

---

## 🟠 Next.js Connection

The Next.js **App Router** (13.4+, stable in 14/15) is the main production implementation of RSC. Every component in `app/` is a Server Component unless the file begins with `'use client'`. Next.js also adds data caching, `loading.js` (automatic Suspense), `error.js` and Server Actions on top. Caching defaults changed between Next.js 14 and 15 (`fetch` is no longer cached by default in 15): version-dependent, check the docs for your version.

```jsx
// app/layout.jsx (Server Component): shared layout stays on the server
import './globals.css';                                 // global styles

export const metadata = { title: 'Shop' };              // static metadata, no <Head> needed

export default function RootLayout({ children }) {      // children can be server OR client components
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `useState`/`useEffect`/`onClick` in a Server Component
✅ **Correct:** Move the interactive part into a small Client Component

```jsx
// Wrong: Server Component cannot hold state or handlers
export default function Page() {
  const [n, setN] = useState(0);                         // ❌ build error
  return <button onClick={() => setN(n + 1)}>{n}</button>;
}
// Right: put 'use client' in Counter.jsx and import it                  ✅
```

❌ **Mistake 2:** Adding `'use client'` at the top of every file "to be safe"
✅ **Correct:** Keep the boundary low in the tree; everything imported by a client file also becomes client code

```jsx
// Wrong: the whole page, including the heavy markdown library, ships to the browser
'use client';                                            // ❌ at page level
import { marked } from 'marked';

// Right: render markdown in a Server Component, send only the HTML result      ✅
```

❌ **Mistake 3:** Passing a function or class instance from a Server to a Client Component as a prop
✅ **Correct:** Pass serializable data (strings, numbers, plain objects, Dates, Maps, Promises) or a Server Action

```jsx
// Wrong
<AddToCart onAdd={() => db.add()} />                     // ❌ functions cannot cross the boundary
// Right
<AddToCart productId={product.id} />                     // ✅ plain data; the client calls a Server Action
```

---

## 🧠 Tricky Interview Question

```jsx
// ServerPage.jsx (Server Component)
import ClientWidget from './ClientWidget';   // has 'use client'
import ServerStats from './ServerStats';     // Server Component using a DB

export default function Page() {
  return (
    <ClientWidget>
      <ServerStats />                        {/* server component passed as children */}
    </ClientWidget>
  );
}
```
**Answer:** This is valid and is the recommended pattern. A Client Component cannot **import** a Server Component (the import would turn it into client code), but it can **receive** one as `children` or another prop, because the parent Server Component renders `ServerStats` on the server first and passes the already rendered result into the client slot. `ClientWidget` can add state or toggling around it without ever running the DB code in the browser.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between SSR and Server Components?
A1: SSR renders components to HTML on the server, but all component code is still sent to the browser and hydrated. RSC components run only on the server and never ship their code or hydrate. Most apps use both: RSC for the tree, SSR to turn the initial result into HTML.

Q2: What can and can't a Server Component do?
A2: It can be async, read databases and files, use secrets, and import heavy libraries without bundle cost. It cannot use state, effects, context consumption, event handlers, or browser-only APIs (`window`, `localStorage`).

Q3: What does `'use client'` do?
A3: It marks the boundary between server and client module graphs. The file and everything it imports become Client Components. They are still pre-rendered to HTML on the server, then hydrated in the browser. It does not mean "client only".

Q4: What is the RSC Payload?
A4: A compact serialized description of the rendered server tree, with placeholders for Client Components and their props. React uses it on the client to update the DOM without a full reload, and it is streamed so Suspense boundaries can fill in later.

Q5: How do you share data between components without prop drilling or duplicate fetches?
A5: In Next.js you can call the same data function in several Server Components. Request deduplication (`fetch` memoisation within a render, or React `cache()` for non-fetch calls) prevents duplicate work. For client interactivity, use context in a Client Component provider, but providers cannot be used from Server Components.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Content is data-heavy and mostly read-only (catalogs, blogs, dashboards, listings)
- You want smaller bundles and direct, secure data access
- You want streaming with Suspense for slow parts

❌ **Avoid (use a Client Component) when:**
- You need state, effects, event handlers, refs or browser APIs
- You rely on client-only libraries (many animation or chart libraries)
- You need instant, offline-capable interaction (a pure SPA may suit better)

---

## 📊 Visual Diagram

```
 SERVER                                         BROWSER
 ┌──────────────────────────────┐
 │ <Page>  (server)             │
 │   ├─ <Header/>   (server)    │   RSC payload + HTML
 │   ├─ <Reviews/>  (server, DB)│ ─────────────────────►  shows HTML instantly
 │   └─ <AddToCart/> ('use client')                         loads ONLY AddToCart.js
 └──────────────────────────────┘                          hydrates AddToCart
                                                          (Header, Reviews: 0 KB of JS)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Server Component | Component rendered only on server | सिर्फ server पर चलने वाला component |
| Client Component | Component hydrated in browser | Browser में चलने वाला component |
| RSC Payload | Serialized server render result | Server render का serialized नतीजा |
| 'use client' | Server/client boundary directive | Server/client सीमा बताने वाला directive |
| Hydration | Attach JS to server HTML | Server HTML से JS जोड़ना |
| Streaming | Send UI in chunks | UI को टुकड़ों में भेजना |
| Serializable props | Data that can cross the boundary | Boundary पार कर सकने वाला data |
| server-only | Package to block client imports | Client import रोकने वाला package |

---

## ⚡ 3-Line Summary
**English:**
1. Server Components run only on the server, can fetch data directly, and add no JavaScript to the client.
2. Interactive parts are small Client Components marked with `'use client'`; props between them must be serializable.
3. Keep the client boundary low, pass server components as `children`, and stream slow parts with Suspense.

**Hindi:**
1. Server Components सिर्फ server पर चलते हैं, data सीधे लाते हैं, और client में JavaScript नहीं जोड़ते।
2. Interactive हिस्से छोटे Client Components हैं जिन पर `'use client'` लगता है; उनके बीच props serializable होने चाहिए।
3. Client सीमा नीचे रखो, server components को `children` से पास करो, और धीमे हिस्सों को Suspense से stream करो।

---

## ➡️ Next Topic
**147. Adapter Pattern in React** — Server और client का data अलग-अलग shape में आता है। Adapter pattern से API के data को अपने UI के अनुकूल shape में बदलना सीखेंगे।
