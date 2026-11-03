# 181. Next.js Loading + Error Pages
# हिंदी में: Next.js Loading + Error Pages — Route-level loading, error और 404 UI

---

## 🔵 Simple Definition (English)
In the App Router, special files in a route folder define UI for states: **`loading.js`** shows while the route loads (a Suspense fallback), **`error.js`** shows when something throws (an Error Boundary), and **`not-found.js`** shows for missing content. Next.js wires them automatically.

## 🔵 सरल परिभाषा (Hindi)
App Router में route folder की special files अलग-अलग states का UI तय करती हैं: **`loading.js`** route load होते समय दिखती है (Suspense fallback), **`error.js`** तब दिखती है जब कुछ throw हो (Error Boundary), और **`not-found.js`** तब जब content मिले नहीं। Next.js इन्हें अपने आप जोड़ देता है।

---

## 🔴 Problem it Solves

Before this, every page handled `isLoading` and `error` by hand, wrapped parts in `Suspense` and `ErrorBoundary` classes, and a single failing component could blank the whole page. With server data fetching, a slow query used to hold the entire page back with a white screen. File-based states give instant feedback and contain failures to one part of the page.

```jsx
// PROBLEM: manual state juggling in every page
if (loading) return <Spinner />;
if (error) return <ErrorBox error={error} />;

// SOLUTION: add files next to page.js and Next.js wires them
// app/orders/loading.js  → skeleton
// app/orders/error.js    → friendly error with retry
```

## 🔴 यह क्यों बना? (Hindi)
इससे पहले हर page में `isLoading` और `error` हाथ से संभालने पड़ते थे, हिस्सों को `Suspense` और `ErrorBoundary` classes में लपेटना पड़ता था, और एक component फेल होने पर पूरा page खाली हो सकता था। Server पर data fetch करने में धीमी query पूरे page को white screen पर रोक देती थी। File-based states तुरंत feedback देती हैं और failure को page के एक हिस्से तक सीमित रखती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Add loading.js next to page.js: Next.js wraps page.js in <Suspense fallback={<Loading/>}>
Step 2 → Navigation shows the loading UI immediately while the server streams the page
Step 3 → Add error.js ('use client' required): wraps the segment in an Error Boundary
Step 4 → If page or child throws, error.js renders with { error, reset }; layout above stays alive
Step 5 → reset() tries to re-render the segment (works for client-side retry)
Step 6 → not-found.js renders when notFound() is called or the URL matches nothing
Step 7 → global-error.js handles errors in the root layout (must define its own <html>/<body>)

Nesting: the nearest file up the tree handles the state
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → page.js के बगल में loading.js रखो: Next.js page.js को <Suspense fallback={<Loading/>}> में लपेट देता है
Step 2 → Navigation पर server page stream करते समय loading UI तुरंत दिखता है
Step 3 → error.js जोड़ो ('use client' ज़रूरी): segment को Error Boundary में लपेटता है
Step 4 → अगर page या child throw करे तो error.js { error, reset } के साथ render होती है; ऊपर का layout चालू रहता है
Step 5 → reset() segment को फिर से render करने की कोशिश करता है (client-side retry के लिए)
Step 6 → notFound() call होने पर या URL कहीं match न होने पर not-found.js render होती है
Step 7 → global-error.js root layout की errors संभालती है (इसमें अपना <html>/<body> देना पड़ता है)

Nesting: पेड़ में ऊपर की सबसे नज़दीकी file उस state को संभालती है
```

---

## 🟡 Real World Example
**Swiggy order history:** Opening "Your Orders" fetches from a slow database. `loading.js` instantly shows grey order-card skeletons, so the user sees progress. If the orders service fails, `error.js` shows "Could not load orders" with a "Try again" button, while the header and bottom nav (in the layout) keep working. If the user opens `/orders/99999`, `not-found.js` shows "Order not found".

## 🟡 Real Example Hindi mein
**Swiggy order history:** "Your Orders" खोलने पर धीमे database से data आता है। `loading.js` तुरंत grey order-card skeletons दिखाती है, तो user को progress दिखती है। अगर orders service फेल हो जाए तो `error.js` "Could not load orders" और "Try again" बटन दिखाती है, जबकि header और bottom nav (layout में) चलते रहते हैं। `/orders/99999` खोलने पर `not-found.js` "Order not found" दिखाती है।

---

## 💻 Code Example — Basic

```jsx
// app/orders/loading.jsx: shown instantly while page.jsx is loading
export default function Loading() {
  return (
    <ul aria-busy="true">                              {/* tells screen readers content is loading */}
      {[1, 2, 3].map(i => (
        <li key={i} style={{ height: 60, background: '#eee', margin: 8, borderRadius: 8 }} /> // skeleton card
      ))}
    </ul>
  );
}
```

```jsx
// app/orders/error.jsx: must be a Client Component
'use client';                                          // required for error boundaries

export default function Error({ error, reset }) {      // error: the thrown error, reset: retry function
  return (
    <div role="alert">                                 {/* announced by screen readers */}
      <h2>Could not load orders</h2>
      <button onClick={() => reset()}>Try again</button> {/* re-render the segment */}
    </div>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// app/orders/page.jsx: async Server Component that can be slow or fail
import { notFound } from 'next/navigation';           // triggers the nearest not-found.js

const sleep = (ms) => new Promise(r => setTimeout(r, ms)); // simulate slow network

async function getOrders() {
  await sleep(1500);                                   // slow data, so loading.jsx will show
  if (Math.random() < 0.3) throw new Error('Orders service down'); // sometimes fails → error.jsx
  return [{ id: 1, item: 'Paneer Tikka' }, { id: 2, item: 'Masala Dosa' }];
}

export default async function OrdersPage() {
  const orders = await getOrders();                    // thrown errors are caught by error.jsx
  if (orders.length === 0) notFound();                 // example: empty state → not-found.jsx
  return (
    <ul>
      {orders.map(o => <li key={o.id}>{o.item}</li>)}  {/* normal success UI */}
    </ul>
  );
}
```

```jsx
// app/orders/error.jsx (advanced): log the error and show a digest for support
'use client';
import { useEffect } from 'react';

export default function Error({ error, reset }) {
  useEffect(() => {
    console.error(error);                              // send to Sentry/Datadog in real apps
  }, [error]);                                         // runs when the error changes

  return (
    <div role="alert">
      <h2>Something went wrong</h2>
      {/* In production, server error messages are hidden; only error.digest is available */}
      {error.digest && <p>Error ID: {error.digest}</p>}
      <button onClick={() => reset()}>Try again</button>
    </div>
  );
}
```

```jsx
// app/global-error.jsx: handles errors thrown in the ROOT layout
'use client';

export default function GlobalError({ reset }) {
  return (
    <html lang="en">                                   {/* must include html and body: it replaces the root layout */}
      <body>
        <h1>The app crashed</h1>
        <button onClick={() => reset()}>Reload</button>
      </body>
    </html>
  );
}
```

---

## 🟠 Real App Integration

Use `loading.js` for the whole route, and use `<Suspense>` yourself for finer parts of the page, so the header and the static parts show immediately while only the slow widget streams in.

```jsx
// app/orders/page.jsx: granular streaming with Suspense
import { Suspense } from 'react';                      // React Suspense
import OrderList from './OrderList';                   // async Server Component (slow)
import Recommendations from './Recommendations';       // another async Server Component

export default function Page() {
  return (
    <>
      <h1>Your Orders</h1>                             {/* renders instantly */}
      <Suspense fallback={<p>Loading orders...</p>}>   {/* only this part waits */}
        <OrderList />
      </Suspense>
      <Suspense fallback={<p>Loading offers...</p>}>   {/* independent stream */}
        <Recommendations />
      </Suspense>
    </>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Writing `error.js` without `'use client'`
✅ **Correct:** Error boundaries must be Client Components

```jsx
// Wrong: build error, error boundaries need client features
export default function Error({ error, reset }) {      // ❌ no 'use client'
  return <button onClick={reset}>Retry</button>;
}

// Right
'use client';                                           // ✅
export default function Error({ error, reset }) {
  return <button onClick={() => reset()}>Retry</button>;
}
```

❌ **Mistake 2:** Expecting `error.js` to catch errors from the layout in the same folder
✅ **Correct:** `error.js` wraps the page and children, not its own `layout.js`; use the parent's `error.js` or `global-error.js`

```jsx
// Wrong assumption: app/dashboard/error.jsx will catch a throw in app/dashboard/layout.jsx
// ❌ The boundary is INSIDE the layout, so it cannot catch the layout's own errors.

// Right: put the error file one level up
// app/error.jsx            → catches errors from app/dashboard/layout.jsx
// app/dashboard/error.jsx  → catches errors from app/dashboard/page.jsx and below
```

---

## 🧠 Tricky Interview Question

```jsx
// app/shop/layout.jsx
export default async function Layout({ children }) {
  throw new Error('layout broke');
}

// app/shop/error.jsx
'use client';
export default function Error() { return <p>Oops</p>; }
```
**Answer:** The user will NOT see "Oops". `app/shop/error.jsx` wraps `page.jsx` and its children inside `layout.jsx`; the layout renders outside that boundary. The error bubbles up to the nearest error boundary above, such as `app/error.jsx`, and if none exists (or the root layout itself throws) to `global-error.jsx` (in production) or the default Next.js error page. To handle layout errors, place `error.jsx` in the parent segment.

---

## ⚫ Interview Questions + Answers

Q1: What does `loading.js` do under the hood?
A1: It makes Next.js wrap the segment's `page.js` (and children) in a React `<Suspense fallback={<Loading/>}>`, so the fallback shows while the async Server Component streams.

Q2: Why must `error.js` be a Client Component?
A2: It is a React Error Boundary, which relies on client-side state to catch errors and support `reset()`.

Q3: What does `reset()` do?
A3: It asks Next.js to re-render the error segment's content. If the problem was temporary, the UI recovers without a full page reload.

Q4: How do you show a 404 for a specific resource?
A4: Call `notFound()` from `next/navigation` in a Server Component. Next.js renders the nearest `not-found.js` and sends a 404 status (with streaming, the status may already be sent as 200 in some cases; version-dependent).

Q5: Are server error messages shown to users in production?
A5: No. For security, errors from Server Components are replaced with a generic message and an `error.digest` hash that you can search in your server logs.

---

## 🔷 When to Use + When Not to Use
✅ **Use these files when:**
- A route has data fetching that can be slow or fail
- You want to keep layout and navigation alive while content loads or breaks
- You need a branded 404 and error experience

❌ **Avoid / adjust when:**
- You need different fallbacks for different parts of one page (use `<Suspense>` directly)
- You want to handle expected form errors (return them from a Server Action instead of throwing)
- You rely on `loading.js` for tiny pages that load instantly (it adds a flash)

---

## 📊 Visual Diagram

```
  app/orders/
  ├── layout.jsx     (always visible: header, nav)
  ├── error.jsx      ┐  <ErrorBoundary fallback=Error>
  ├── loading.jsx    │    <Suspense fallback=Loading>
  ├── not-found.jsx  │      <page.jsx />   ← async, may be slow, may throw
  └── page.jsx       ┘

  Slow ──► Loading skeleton ──► real page streams in
  Throw ─► Error UI (+ Try again) ──► reset() ──► re-render
  notFound() ─► not-found.jsx

  Re-render behavior: loading UI is replaced when data arrives (no extra
  re-render of the layout). reset() re-renders only the segment.
  Performance: streaming improves perceived speed (TTFB and first paint),
  and error boundaries limit the blast radius of a failure.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| loading.js | Fallback UI while route loads | Route load होते समय का UI |
| error.js | Error boundary UI for a segment | Segment का error UI |
| not-found.js | UI for missing content | Content न मिलने का UI |
| global-error.js | Handles root layout errors | Root layout की errors |
| Suspense | React way to show fallback while waiting | इंतज़ार में fallback दिखाना |
| Error Boundary | Catches render errors in children | Children की render errors पकड़ना |
| reset | Retry rendering the segment | Segment फिर से render करना |
| Streaming | Sending HTML in pieces | HTML को टुकड़ों में भेजना |
| digest | Hash to find the error in logs | Logs में error खोजने का hash |

---

## ⚡ 3-Line Summary
**English:**
1. `loading.js`, `error.js` and `not-found.js` give route-level loading, error and 404 UI without manual state code.
2. `error.js` must be a Client Component, and it cannot catch errors from the layout beside it.
3. Combine with `<Suspense>` for finer streaming and report errors using `error.digest`.

**Hindi:**
1. `loading.js`, `error.js` और `not-found.js` बिना manual state code के route-level loading, error और 404 UI देती हैं।
2. `error.js` Client Component होनी चाहिए, और यह अपने बगल वाले layout की errors नहीं पकड़ सकती।
3. बारीक streaming के लिए `<Suspense>` के साथ मिलाओ और errors को `error.digest` से track करो।

---

## ➡️ Next Topic
**182. Next.js Parallel Routes** — `@slot` folders से एक ही layout में कई pages एक साथ, independently load और error handle करते हुए दिखाना।
