# 140. Streaming SSR
# हिंदी में: Streaming SSR — Page को टुकड़ों में भेजना

---

## 🔵 Simple Definition (English)
**Streaming SSR** sends the HTML of a page to the browser in pieces as each part becomes ready, instead of waiting for the whole page. Slow parts are wrapped in `<Suspense>`; the browser first shows the fast shell with a fallback, and the slow part streams in later.

## 🔵 सरल परिभाषा (Hindi)
**Streaming SSR** page का HTML एक बार में नहीं, बल्कि टुकड़ों में भेजता है, जैसे-जैसे हर हिस्सा तैयार होता है। धीमे हिस्सों को `<Suspense>` में लपेटते हैं; browser पहले तेज़ shell और fallback दिखाता है, और धीमा हिस्सा बाद में अपने आप आ जाता है।

---

## 🔴 Problem it Solves

Traditional SSR is all-or-nothing: the server must fetch ALL data, render ALL HTML, then the browser downloads ALL JS, then hydrates ALL components. One slow query (for example "recommendations") blocks the whole page, so the user stares at a blank screen (bad TTFB and FCP).

```jsx
// PROBLEM (classic SSR): the slowest query decides when ANYTHING appears
export default async function Page() {
  const product = await getProduct();          // 50ms
  const reviews = await getReviews();          // 2500ms ← blocks the entire page
  return <><Product p={product} /><Reviews r={reviews} /></>;
}

// SOLUTION: stream. Product shows at ~50ms, Reviews streams in when ready
import { Suspense } from 'react';
export default async function Page() {
  const product = await getProduct();          // fast: part of the shell
  return (
    <>
      <Product p={product} />
      <Suspense fallback={<p>Loading reviews...</p>}>  {/* shell shows this immediately */}
        <Reviews />                                    {/* async component fetches itself */}
      </Suspense>
    </>
  );
}
```

## 🔴 यह क्यों बना? (Hindi)
पारंपरिक SSR में सब कुछ या कुछ नहीं: server को सारा data लाना पड़ता है, सारा HTML बनाना पड़ता है, फिर browser सारा JS download करता है और सब कुछ hydrate करता है। एक धीमी query (जैसे "recommendations") पूरे page को रोक देती है और user को खाली screen दिखती है (खराब TTFB और FCP)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Browser requests the page; server starts rendering immediately
Step 2 → React renders as far as it can; at a <Suspense> boundary with pending data it emits the fallback HTML
Step 3 → The server sends the shell (layout + fast parts + fallbacks) over a chunked HTTP response and keeps the connection open
Step 4 → When the slow data resolves, React renders that part and sends the extra HTML + a tiny inline script
Step 5 → The script swaps the fallback with the real content (no full-page reload)
Step 6 → Hydration is selective: each Suspense boundary hydrates independently, and a boundary the user clicks is prioritized
Step 7 → Response ends when every boundary has finished

APIs: renderToPipeableStream / renderToReadableStream (React 18+), automatic in Next.js App Router
Re-render: streamed parts do not re-render, they are inserted once; client islands hydrate once
Performance: lower TTFB/FCP, better LCP when the hero is in the shell; total time is the same, perceived time is shorter
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Browser page माँगता है; server तुरंत render करना शुरू कर देता है
Step 2 → React जितना हो सके render करता है; pending data वाले <Suspense> पर fallback का HTML देता है
Step 3 → Server shell (layout + तेज़ हिस्से + fallbacks) chunked HTTP response में भेजता है और connection खुला रखता है
Step 4 → धीमा data आने पर React उस हिस्से को render करता है और अतिरिक्त HTML + छोटी inline script भेजता है
Step 5 → Script fallback को असली content से बदल देती है (पूरा page reload नहीं)
Step 6 → Hydration selective होता है: हर Suspense boundary अलग से hydrate होती है, और user जिस पर click करे वह पहले होती है
Step 7 → जब सारी boundaries पूरी हो जाती हैं तब response खत्म होता है

APIs: renderToPipeableStream / renderToReadableStream (React 18+), Next.js App Router में अपने आप
Re-render: streamed हिस्से दोबारा render नहीं होते, एक बार insert होते हैं
Performance: TTFB/FCP कम, कुल समय वही पर महसूस होने वाला समय कम
```

---

## 🟡 Real World Example
**Amazon product page:** The title, price and "Buy now" box appear almost instantly. "Customers also bought", reviews and sponsored products are slower, so they show skeleton boxes first and fill in one by one as each service responds. If the recommendation service is slow, the user can still buy the item.

## 🟡 Real Example Hindi mein
**Amazon product page:** Title, price और "Buy now" box लगभग तुरंत दिखते हैं। "Customers also bought", reviews और sponsored products धीमे हैं, इसलिए पहले skeleton boxes दिखते हैं और हर service के जवाब देने पर एक-एक करके भर जाते हैं। Recommendation service धीमी हो तो भी user सामान खरीद सकता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: Suspense boundaries stream two slow sections independently (Next.js App Router page)
import { Suspense } from 'react';                          // Suspense marks stream boundaries

const sleep = (ms) => new Promise((r) => setTimeout(r, ms)); // fake network delay helper

async function Reviews() {                                  // async Server Component
  await sleep(2000);                                        // pretend slow API: 2s
  return <p>4.6 stars from 12,300 ratings</p>;              // streamed in after 2s
}

async function Recommendations() {                          // another async Server Component
  await sleep(4000);                                        // even slower: 4s
  return <p>Customers also bought: Cable, Case</p>;         // streamed in after 4s
}

export default function Page() {                            // the page itself is instant
  return (
    <main>
      <h1>Wireless Earbuds</h1>                             {/* shell: sent immediately */}
      <Suspense fallback={<p>Loading reviews...</p>}>       {/* shows until Reviews resolves */}
        <Reviews />
      </Suspense>
      <Suspense fallback={<p>Loading suggestions...</p>}>   {/* independent boundary */}
        <Recommendations />
      </Suspense>
    </main>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// Advanced: raw streaming with renderToPipeableStream in a Node/Express server (without a framework)
import express from 'express';                             // HTTP server
import { renderToPipeableStream } from 'react-dom/server';  // React 18+ streaming API
import App from './App.js';                                 // your root component (uses Suspense)

const app = express();                                      // create the server

app.get('/', (req, res) => {
  let didError = false;                                     // track shell errors
  const { pipe, abort } = renderToPipeableStream(<App />, {
    bootstrapScripts: ['/client.js'],                       // JS bundle that hydrates on the client
    onShellReady() {                                        // shell (outside Suspense) is ready
      res.statusCode = didError ? 500 : 200;                // status is decided here
      res.setHeader('Content-Type', 'text/html');           // tell the browser it is HTML
      pipe(res);                                            // start streaming; later chunks follow
    },
    onShellError(err) {                                     // shell failed: send a safe fallback page
      res.statusCode = 500;
      res.send('<h1>Something went wrong</h1>');
    },
    onError(err) {                                          // any error (also inside Suspense)
      didError = true;
      console.error(err);                                   // log to your monitoring tool
    },
  });
  setTimeout(() => abort(), 10000);                         // give up after 10s: client renders instead
});

app.listen(3000);                                           // run on port 3000

// ---------- App.js: the component tree being streamed ----------
import { Suspense } from 'react';
import Comments from './Comments.js';                       // reads data with use()/a Suspense-enabled lib

export default function App() {
  return (
    <html>
      <body>
        <h1>Post</h1>                                       {/* in the shell */}
        <Suspense fallback={<p>Loading comments...</p>}>    {/* streamed later */}
          <Comments />
        </Suspense>
        <script src="/client.js" async />                   {/* hydration entry */}
      </body>
    </html>
  );
}

// ---------- client.js: selective hydration ----------
import { hydrateRoot } from 'react-dom/client';
import App from './App.js';
hydrateRoot(document, <App />);                              // each boundary hydrates independently
```

---

## 🟠 Next.js Connection

In the App Router, streaming is on by default. A `loading.js` file next to `page.js` automatically wraps the page in a Suspense boundary with that UI as the fallback. For finer control, wrap individual async components in `<Suspense>` yourself. Dynamic rendering (cookies, headers, uncached fetch) is what makes streaming valuable; static pages are pre-rendered at build time. Partial Prerendering (PPR) combines both (experimental in Next.js 14/15, version-dependent; check the docs of your version).

```jsx
// app/dashboard/loading.jsx → instant fallback for the whole route segment
export default function Loading() {
  return <div className="skeleton">Loading dashboard...</div>;   // shown while page.jsx streams
}

// app/dashboard/page.jsx
import { Suspense } from 'react';
import Stats from './Stats';                                      // slow async Server Component
export default function Page() {
  return (
    <>
      <h1>Dashboard</h1>                                          {/* shell */}
      <Suspense fallback={<p>Loading stats...</p>}><Stats /></Suspense> {/* streamed */}
    </>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Awaiting everything at the top of the page, so there is nothing to stream
✅ **Correct:** Move slow fetches into child components inside `<Suspense>`

```jsx
// Wrong: the page waits for both before sending anything
export default async function Page() {
  const [a, b] = await Promise.all([getFast(), getSlow()]);   // ❌ blocks the shell on getSlow
  return <><A d={a} /><B d={b} /></>;
}

// Right: only await the fast one; let the slow one suspend
export default async function Page() {
  const a = await getFast();                                   // ✅ small wait
  return <><A d={a} /><Suspense fallback={<Skel />}><SlowB /></Suspense></>;
}
```

❌ **Mistake 2:** One giant `<Suspense>` around the whole page
✅ **Correct:** Use several small boundaries so independent parts appear independently

```jsx
// Wrong: everything waits for the slowest child
<Suspense fallback={<Spinner />}><Reviews /><Recs /><Ads /></Suspense>   // ❌ one fallback for all

// Right: independent boundaries
<Suspense fallback={<Skel1 />}><Reviews /></Suspense>                    // ✅
<Suspense fallback={<Skel2 />}><Recs /></Suspense>
```

❌ **Mistake 3:** Putting data that decides the HTTP status/redirect/SEO meta inside a late boundary
✅ **Correct:** Resolve status-critical data (404, redirect) before the shell is sent, because headers are already sent once streaming starts

```jsx
// Wrong: notFound() inside a streamed child, status is already 200
// Right: call notFound() in the page before returning JSX (or use generateMetadata for meta)
```

---

## 🧠 Tricky Interview Question

```jsx
import { Suspense } from 'react';
async function Slow() { await new Promise(r => setTimeout(r, 3000)); return <p>Slow</p>; }
async function Fast() { return <p>Fast</p>; }

export default function Page() {
  return (
    <Suspense fallback={<p>Loading</p>}>
      <Fast />
      <Slow />
    </Suspense>
  );
}
```
**Answer:** The user sees "Loading" for about 3 seconds, then both "Fast" and "Slow" appear together. A Suspense boundary reveals its content only when ALL suspended children inside it are ready, so `Fast` is held back by `Slow`. To show `Fast` immediately, put each in its own `<Suspense>`.

---

## ⚫ Interview Questions + Answers

Q1: What is Streaming SSR and why is it useful?
A1: The server sends HTML in chunks as parts finish instead of waiting for the full page. It improves TTFB and FCP, so users see useful content sooner, and slow data no longer blocks the whole page.

Q2: How does React replace the fallback with real content in a streamed response?
A2: The server sends the real HTML in a hidden element plus a small inline script. The script moves the HTML into the place of the fallback. No JavaScript bundle is needed for this swap, and hydration happens later.

Q3: What is selective hydration?
A3: With Suspense, React hydrates each boundary independently, and starts with the one the user interacts with. A slow component's code or data no longer blocks the rest of the page from becoming interactive.

Q4: What is the downside of streaming?
A4: HTTP status and headers are sent first, so you cannot change them after streaming starts. Some crawlers/proxies buffer responses, and layout shifts happen if fallbacks differ in size from content. Use skeletons with the same dimensions.

Q5: How do you enable streaming in Next.js?
A5: It is on by default in the App Router. Add `loading.js` for route-level fallback or wrap async components in `<Suspense>`. Pages that are fully static do not stream because they are prebuilt.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- A page mixes fast and slow data (product + recommendations)
- Slow third-party or personalized widgets should not block the page
- You want better perceived performance and Core Web Vitals

❌ **Avoid when:**
- The page is fully static (use SSG/ISR instead)
- The slow part decides status/redirect/SEO-critical data
- A fallback would cause big layout shifts and cannot be sized well

---

## 📊 Visual Diagram

```
 CLASSIC SSR                              STREAMING SSR
 time ─────────────────────────▶          time ─────────────────────────▶
 server: [fetch all][render all]──▶HTML   server: [shell]▶[reviews]▶[recs]
 browser: ........blank.........[page]    browser: [shell+skeletons]→[+reviews]→[+recs]
          0         2.5s                           0.05s             2.5s       4s

 HTTP response (chunked):
 chunk 1: <html>...<h1>..</h1><div>Loading reviews...</div>
 chunk 2: <template>real reviews</template><script>swap()</script>
 chunk 3: <template>real recs</template><script>swap()</script>
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Streaming | Sending HTML in chunks | HTML को टुकड़ों में भेजना |
| Shell | Part of the page outside Suspense, sent first | Suspense के बाहर का हिस्सा, पहले भेजा जाता है |
| Fallback | UI shown while content is pending | इंतज़ार के दौरान दिखने वाला UI |
| TTFB | Time to first byte | पहले byte तक का समय |
| Selective hydration | Hydrate boundaries independently | हर boundary को अलग hydrate करना |
| `loading.js` | Next.js route-level fallback file | Route स्तर का fallback file |
| Chunked transfer | HTTP mode that keeps the response open | Response खुला रखने वाला HTTP तरीका |
| PPR | Static shell + streamed dynamic holes (version-dependent) | Static shell + streamed dynamic हिस्से |

---

## ⚡ 3-Line Summary
**English:**
1. Streaming SSR sends the shell first and fills slow `<Suspense>` parts later in the same response.
2. Hydration is selective, so users can interact with ready parts earlier.
3. Use many small boundaries, resolve status-critical data before the shell, and size skeletons to avoid layout shift.

**Hindi:**
1. Streaming SSR पहले shell भेजता है और धीमे `<Suspense>` हिस्सों को उसी response में बाद में भरता है।
2. Hydration selective होता है, इसलिए तैयार हिस्सों से user जल्दी interact कर सकता है।
3. छोटी-छोटी कई boundaries रखो, status वाला जरूरी data shell से पहले resolve करो, और layout shift से बचने के लिए skeleton का size सही रखो।

---

## ➡️ Next Topic
**141. React Suspense — Deep Dive** — Suspense अंदर से कैसे काम करता है, `use()`, lazy loading, error boundaries और transitions के साथ।
