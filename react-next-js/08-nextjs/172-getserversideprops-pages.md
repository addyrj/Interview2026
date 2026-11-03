# 172. getServerSideProps (Pages)
# हिंदी में: getServerSideProps — हर Request पर Server पर Data लाना (Pages Router)

---

## 🔵 Simple Definition (English)
`getServerSideProps` is a function you export from a file in the Next.js **Pages Router** (`pages/`). Next.js runs it on the server **on every request**, and the object it returns becomes the props of the page component. The HTML is built fresh for each visitor.

## 🔵 सरल परिभाषा (Hindi)
`getServerSideProps` एक function है जिसे आप Next.js के **Pages Router** (`pages/`) की file से export करते हैं। Next.js इसे **हर request पर** server पर चलाता है, और जो object यह return करता है वही page component के props बन जाते हैं। हर visitor के लिए HTML नए सिरे से बनता है।

---

## 🔴 Problem it Solves

In plain React (client-side rendering) the browser first gets an empty `<div id="root">`, then downloads JavaScript, then calls an API, then shows data. The user sees a spinner, and search engines may see an empty page. Some pages also need data that is **different for every request**: the logged-in user's orders, a live stock count, or a cookie-based language. Static HTML cannot do that. `getServerSideProps` fetches the data on the server before sending HTML, so the browser receives a complete page that is already personalised and fresh.

```jsx
// PROBLEM: client-side fetch → empty HTML first, spinner, poor SEO
export default function Orders() {
  const [orders, setOrders] = useState(null);              // null until the API answers
  useEffect(() => {
    fetch('/api/orders').then(r => r.json()).then(setOrders); // runs only AFTER the page loads
  }, []);
  if (!orders) return <p>Loading...</p>;                    // user (and Google) first sees this
  return <ul>{orders.map(o => <li key={o.id}>{o.name}</li>)}</ul>;
}
```

## 🔴 यह क्यों बना? (Hindi)
सादे React (client-side rendering) में browser को पहले खाली `<div id="root">` मिलता है, फिर JavaScript download होती है, फिर API call होती है, तब जाकर data दिखता है। User को spinner दिखता है और search engine को खाली page दिख सकता है। कुछ pages को ऐसा data चाहिए जो **हर request पर अलग** हो: logged-in user के orders, live stock, या cookie से भाषा। Static HTML यह नहीं कर सकता। `getServerSideProps` HTML भेजने से पहले server पर data ले आता है, इसलिए browser को पूरा, personalised और fresh page मिलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Browser requests /orders (full page load or Link navigation)
Step 2 → Next.js server sees that pages/orders.js exports getServerSideProps
Step 3 → It calls getServerSideProps(context) with req, res, params, query, cookies
Step 4 → Your function fetches data (DB, internal API, cookies) on the server
Step 5 → It returns { props: {...} } or { notFound: true } or { redirect: {...} }
Step 6 → Next.js renders the page component to HTML using those props
Step 7 → HTML + JSON props are sent; React hydrates the page in the browser
Step 8 → On client-side Link navigation, Next.js fetches only the JSON from the server

KEY: this code NEVER runs in the browser, and it runs again on EVERY request
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Browser /orders माँगता है (पूरा page load या Link से navigation)
Step 2 → Next.js server देखता है कि pages/orders.js में getServerSideProps export है
Step 3 → वह getServerSideProps(context) को req, res, params, query, cookies के साथ call करता है
Step 4 → आपका function server पर data लाता है (DB, internal API, cookies)
Step 5 → वह { props: {...} } या { notFound: true } या { redirect: {...} } return करता है
Step 6 → Next.js उन props से page component को HTML में render करता है
Step 7 → HTML + JSON props भेजे जाते हैं; browser में React hydrate करता है
Step 8 → Link से client-side navigation पर Next.js server से सिर्फ JSON लेता है

KEY: यह code browser में कभी नहीं चलता, और हर request पर दोबारा चलता है
```

---

## 🟡 Real World Example
**Swiggy "My Orders" page:** Every user sees different orders, and the order status (preparing, out for delivery) changes every minute. The page reads the session cookie in `getServerSideProps`, asks the orders database for that user, and returns the list. The HTML arrives with the orders already inside. If there is no cookie, the function redirects to `/login` before anything is rendered. Another example is an Amazon-style "Deals near you" page that depends on the request's location header.

## 🟡 Real Example Hindi mein
**Swiggy "My Orders" page:** हर user को अलग orders दिखते हैं और order का status (preparing, out for delivery) हर मिनट बदलता है। Page `getServerSideProps` में session cookie पढ़ता है, उस user के orders database से माँगता है और list return करता है। HTML में orders पहले से मौजूद होते हैं। अगर cookie नहीं है तो कुछ भी render होने से पहले function `/login` पर redirect कर देता है। दूसरा उदाहरण Amazon जैसा "आपके पास के Deals" page है जो request के location header पर निर्भर करता है।

---

## 💻 Code Example — Basic

```jsx
// pages/quote.js (Pages Router). Every refresh shows a fresh server-side time.

// Page component: receives the props returned by getServerSideProps
export default function QuotePage({ renderedAt, userAgent }) {
  return (
    <main>
      <h1>Server Rendered Page</h1>                              {/* plain HTML for crawlers */}
      <p>Rendered at: {renderedAt}</p>                           {/* changes on every request */}
      <p>Your browser: {userAgent}</p>                           {/* read from the request */}
    </main>
  );
}

// Runs ONLY on the server, on EVERY request
export async function getServerSideProps(context) {
  const { req } = context;                                       // Node.js request object
  return {
    props: {                                                     // must be JSON-serialisable
      renderedAt: new Date().toISOString(),                      // string, NOT a Date object
      userAgent: req.headers['user-agent'] ?? 'unknown',         // header sent by the browser
    },
  };
}
```

## 💻 Code Example — Advanced

```jsx
// pages/orders/[id].js : authenticated, dynamic, with redirect / 404 / caching header
import Head from 'next/head';                                    // sets <title> in Pages Router
import { getOrder } from '../../lib/orders';                     // hypothetical DB helper (server only)
import { getUserFromSession } from '../../lib/auth';             // hypothetical session helper

export default function OrderPage({ order }) {
  return (
    <>
      <Head><title>Order #{order.id} | FoodApp</title></Head>    {/* per-page title */}
      <h1>Order #{order.id}</h1>
      <p>Status: {order.status}</p>
      <ul>
        {order.items.map((item) => (
          <li key={item.sku}>{item.name} x {item.qty}</li>       // key: stable sku from data
        ))}
      </ul>
    </>
  );
}

export async function getServerSideProps({ params, req, res, locale }) {
  // 1. Auth: look at cookies on the server
  const user = await getUserFromSession(req);                    // reads the session cookie
  if (!user) {
    return {
      redirect: { destination: '/login', permanent: false },     // 307 redirect, no page render
    };
  }

  // 2. Fetch: params.id comes from the file name [id].js
  let order;
  try {
    order = await getOrder(params.id, user.id);                  // user.id stops reading others' orders
  } catch (err) {
    console.error('order fetch failed', err);                    // log on the server only
    throw err;                                                   // Next.js shows pages/500.js
  }
  if (!order) return { notFound: true };                         // renders pages/404.js with status 404

  // 3. Optional HTTP caching: let a CDN reuse the HTML for a short time
  //    (only safe when the page is NOT personalised; here it is, so we use private)
  res.setHeader('Cache-Control', 'private, no-store');           // never share user data across users

  return {
    props: {
      // Date, Map, undefined are NOT serialisable → convert first
      order: JSON.parse(JSON.stringify(order)),                  // simple way to drop Dates/undefined
      locale: locale ?? 'en',                                    // i18n locale chosen by Next.js
    },
  };
}
```

---

## 🟠 Next.js Connection

`getServerSideProps` exists **only in the Pages Router**. The App Router (`app/`) has no such function. Instead, a Server Component is `async` and fetches directly, and you opt into per-request rendering with dynamic APIs (`cookies()`, `headers()`) or `export const dynamic = 'force-dynamic'`.

```jsx
// App Router equivalent of the advanced example above (Next.js 14/15)
// app/orders/[id]/page.jsx  (Server Component by default)
import { cookies } from 'next/headers';                          // using this makes the route dynamic
import { redirect, notFound } from 'next/navigation';            // helpers instead of return objects
import { getOrder } from '@/lib/orders';                         // hypothetical DB helper
import { getUserFromToken } from '@/lib/auth';                   // hypothetical auth helper

export default async function OrderPage({ params }) {
  const { id } = await params;                                   // Next.js 15: params is a Promise
  const cookieStore = await cookies();                           // Next.js 15: cookies() is async (14: sync)
  const user = await getUserFromToken(cookieStore.get('session')?.value);
  if (!user) redirect('/login');                                 // same as the redirect return object
  const order = await getOrder(id, user.id);                     // fetched on the server
  if (!order) notFound();                                        // same as { notFound: true }
  return <h1>Order #{order.id}: {order.status}</h1>;             // no props object needed
}
```
Version-dependent: whether `cookies()` and `params` need `await` depends on Next.js 14 vs 15.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Calling your own API route from `getServerSideProps` with `fetch('/api/...')`
✅ **Correct:** Import the shared function (DB or service code) and call it directly. A relative URL fails on the server, and it adds an unnecessary extra network hop.

```jsx
// Wrong: relative URL has no origin on the server → "Invalid URL" error
export async function getServerSideProps() {
  const res = await fetch('/api/orders');                        // ❌
  return { props: { orders: await res.json() } };
}

// Right: call the logic directly
import { listOrders } from '../lib/orders';
export async function getServerSideProps() {
  const orders = await listOrders();                             // ✅ no HTTP hop
  return { props: { orders } };
}
```

❌ **Mistake 2:** Returning non-serialisable values such as `Date`, `undefined` or class instances
✅ **Correct:** Convert to strings, numbers and plain objects (`createdAt.toISOString()`), and use `null` instead of `undefined`.

```jsx
// Wrong: Error "`object` ("[object Date]") cannot be serialized as JSON"
return { props: { createdAt: new Date(), coupon: undefined } };  // ❌

// Right
return { props: { createdAt: new Date().toISOString(), coupon: null } }; // ✅
```

❌ **Mistake 3:** Using `getServerSideProps` for data that rarely changes (a blog, a docs page)
✅ **Correct:** Use `getStaticProps` (topic 173). SSR runs on every hit, so it is slower and costs more server time. Also never import browser-only code (`window`) or expose secrets in props: props are visible in the page source (`__NEXT_DATA__`).

```jsx
// Wrong: a blog post re-fetched from the DB for every visitor
export async function getServerSideProps({ params }) { /* ... */ } // ❌ for static content

// Right: build once, revalidate occasionally
export async function getStaticProps({ params }) {
  return { props: { post: await getPost(params.slug) }, revalidate: 60 }; // ✅
}
```

---

## 🧠 Tricky Interview Question

```jsx
// pages/counter.js
let hits = 0;                                    // module-level variable on the SERVER

export async function getServerSideProps() {
  hits += 1;                                     // runs on the server per request
  console.log('server hits:', hits);
  return { props: { hits } };
}

export default function Counter({ hits }) {
  console.log('component render, hits:', hits);  // where does this log appear?
  return <p>{hits}</p>;
}
// User A opens /counter, then User B opens /counter. What do they see?
```
**Answer:** User A sees `1`, User B sees `2`. The terminal prints `server hits: 1`, then `server hits: 2` (and `component render` also prints on the server for the HTML render, and again in the browser console when hydrating). Module-level variables live as long as the Node.js process, so they are **shared between users**. This works in `next dev` or a single server, but on serverless platforms (Vercel) each function instance has its own memory, so the number can reset or differ. Lesson: never store per-user data in module-level variables, and never rely on them for counters; use a database.

---

## ⚫ Interview Questions + Answers

Q1: What is `getServerSideProps` and when does it run?
A1: A Pages Router function exported from a page file. It runs on the server for every request (and for client-side navigations as a JSON request to the server). It never runs in the browser and is removed from the client bundle. Its returned `props` are passed to the page component.

Q2: What can `getServerSideProps` return?
A2: Exactly one of three shapes: `{ props: {...} }` to render, `{ notFound: true }` to show the 404 page, or `{ redirect: { destination, permanent } }` to redirect. The props must be JSON-serialisable.

Q3: What is in the `context` argument?
A3: `params` (dynamic route values), `query` (query string), `req` and `res` (Node.js request and response, so you can read cookies and set headers), `resolvedUrl`, `locale`/`locales`/`defaultLocale`, `preview`/`previewData` (draft mode data) and, in newer versions, `draftMode`.

Q4: What are the trade-offs of SSR with `getServerSideProps`?
A4: Pros: always fresh and personalised data, good SEO, access to cookies and headers. Cons: slower TTFB because the page waits for your data; every request uses server compute; it cannot be fully cached on a CDN; the whole page is blocked if the fetch is slow. If data does not change per request, prefer static generation with ISR.

Q5: How does this differ from the App Router?
A5: The App Router has no `getServerSideProps`. Server Components are `async` and fetch data inline. A route becomes dynamic (rendered per request) when it uses `cookies()`, `headers()`, `searchParams`, or `dynamic = 'force-dynamic'`/`fetch(..., { cache: 'no-store' })`. Redirect and 404 are done with `redirect()` and `notFound()`.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- The data depends on the request (cookies, session, headers, query string)
- The data must be fresh on every visit (live prices, stock, order status)
- You need SEO for personalised or frequently changing content

❌ **Avoid when:**
- The content is the same for everyone and changes rarely (use `getStaticProps` + `revalidate`)
- Only a small part of the page is dynamic (render the shell statically, fetch the rest on the client)
- You are starting a new project on the App Router (use async Server Components instead)

---

## 📊 Visual Diagram

```
  Every request:

  Browser ──GET /orders/42──▶ Next.js Server
                                   │
                                   ▼
                       getServerSideProps(ctx)
                         ├─ read cookie ───────▶ Auth
                         ├─ fetch order ───────▶ Database
                         └─ return { props }
                                   │
                                   ▼
                      render <OrderPage {...props} />
                                   │
  Browser ◀── HTML + __NEXT_DATA__ ┘   (fresh for THIS user)
     │
     └─ hydrate → page becomes interactive

  Re-render behavior: props change only on a new navigation/request.
  Performance: TTFB = server time + your data fetch time (no CDN cache by default).
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SSR | Rendering HTML on the server per request | हर request पर server पर HTML बनाना |
| context | Argument with req, res, params, query | req, res, params, query वाला argument |
| props | Data object passed to the page | Page को दिया जाने वाला data |
| Serialisable | Can be converted to JSON | JSON में बदलने लायक |
| notFound | Return value that shows the 404 page | 404 page दिखाने वाली return value |
| redirect | Return value that sends the user elsewhere | User को दूसरे URL पर भेजना |
| TTFB | Time to first byte | पहला byte आने में लगा समय |
| Hydration | React attaching events to server HTML | Server HTML में React को जोड़ना |

---

## ⚡ 3-Line Summary
**English:**
1. `getServerSideProps` runs only on the server, on every request, and returns props (or `notFound` / `redirect`) for a Pages Router page.
2. Use it for personalised or always-fresh data; the cost is slower TTFB and no easy CDN caching.
3. Props must be serialisable, never call your own API route from it, and in the App Router use async Server Components instead.

**Hindi:**
1. `getServerSideProps` सिर्फ server पर, हर request पर चलता है और Pages Router के page के लिए props (या `notFound` / `redirect`) return करता है।
2. Personalised या हमेशा fresh data के लिए इस्तेमाल करो; कीमत है धीमा TTFB और CDN caching की कठिनाई।
3. Props serialisable होने चाहिए, अपने ही API route को इसमें call मत करो, और App Router में इसकी जगह async Server Components इस्तेमाल करो।

---

## ➡️ Next Topic
**173. getStaticProps (Pages)** — जब data हर request पर नहीं बदलता, तब page को build time पर एक बार बनाकर CDN से परोसना कैसे होता है, और `revalidate` (ISR) से उसे कैसे ताज़ा रखते हैं।
