# 132. Suspense for Data Fetching
# हिंदी में: Suspense से Data Fetching — loading state को declarative बनाना

---

## 🔵 Simple Definition (English)
**Suspense** lets a component "wait" for something (code, or data) while React shows a fallback UI above it. For data fetching, a Suspense-enabled source (React 19 `use()`, TanStack Query `useSuspenseQuery`, Next.js Server Components, Relay) pauses the render until the data is ready, so you do not write `if (loading)` in every component.

## 🔵 सरल परिभाषा (Hindi)
**Suspense** किसी component को किसी चीज़ (code या data) का "इंतज़ार" करने देता है, जबकि ऊपर React एक fallback UI दिखाता है। Data fetching में Suspense-enabled source (React 19 `use()`, TanStack Query `useSuspenseQuery`, Next.js Server Components, Relay) data तैयार होने तक render रोक देता है, इसलिए हर component में `if (loading)` नहीं लिखना पड़ता।

---

## 🔴 Problem it Solves

With `useEffect` + `useState`, every component manages `loading`, `error` and `data` by hand. Parents and children each show their own spinners, so the page flickers with many spinners. Fetches also start only after the component renders (a "waterfall": render → effect → fetch → render children → their fetches...).

```jsx
// PROBLEM: manual loading flags in every component, plus a request waterfall
function Menu({ id }) {
  const [data, setData] = useState(null);                // data state
  const [loading, setLoading] = useState(true);          // loading state
  useEffect(() => { fetchMenu(id).then(d => { setData(d); setLoading(false); }); }, [id]);
  if (loading) return <Spinner />;                       // spinner in every component
  return <List items={data} />;
}

// SOLUTION: the component just reads data; the boundary owns the loading UI
<Suspense fallback={<Spinner />}><Menu id={id} /></Suspense>
```

## 🔴 यह क्यों बना? (Hindi)
`useEffect` + `useState` के साथ हर component `loading`, `error` और `data` हाथ से संभालता है। Parent और child अपने-अपने spinners दिखाते हैं, इसलिए page पर कई spinners झपकते हैं। Fetch भी component के render होने के बाद ही शुरू होता है ("waterfall": render → effect → fetch → children render → उनके fetch...)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → A component reads data from a Suspense-aware source (use(promise), useSuspenseQuery, async Server Component)
Step 2 → If the data is not ready, the source "suspends": React stops rendering that component
Step 3 → React walks up to the nearest <Suspense> boundary and shows its fallback
Step 4 → The promise resolves, React retries rendering the suspended component
Step 5 → The component now has data and renders; the boundary swaps the fallback for the real UI
Step 6 → Errors are handled separately by an Error Boundary above

KEY: loading UI is decided by the boundary, not by each component
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Component Suspense-aware source से data पढ़ता है (use(promise), useSuspenseQuery, async Server Component)
Step 2 → Data तैयार न हो तो source "suspend" करता है: React उस component का render रोक देता है
Step 3 → React ऊपर के सबसे नज़दीकी <Suspense> boundary तक जाकर उसका fallback दिखाता है
Step 4 → Promise resolve होता है, React suspended component को दोबारा render करता है
Step 5 → अब component के पास data है और वह render होता है; boundary fallback की जगह असली UI दिखाता है
Step 6 → Errors को ऊपर का Error Boundary अलग से संभालता है

KEY: loading UI boundary तय करता है, हर component नहीं
```

---

## 🟡 Real World Example
**Swiggy restaurant page:** The page has a header (restaurant name), a menu list and a "reviews" section. With Suspense, the header shows immediately, the menu sits inside one `<Suspense fallback={<MenuSkeleton />}>`, and reviews inside another. If reviews are slow, the menu is not blocked: users start ordering while the reviews skeleton is still visible. Each region loads independently without any `isLoading` flags.

## 🟡 Real Example Hindi mein
**Swiggy restaurant page:** Page में header (restaurant का नाम), menu list और "reviews" section है। Suspense के साथ header तुरंत दिखता है, menu एक `<Suspense fallback={<MenuSkeleton />}>` में है, और reviews दूसरे में। Reviews धीमे हों तो menu नहीं रुकता: reviews का skeleton दिखते हुए भी users order करना शुरू कर सकते हैं। हर हिस्सा बिना किसी `isLoading` flag के अलग-अलग load होता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: React 19 `use(promise)` with Suspense (React 18 has no `use`; version-dependent)
import { Suspense, use } from 'react';                  // use() reads a promise and suspends
import { createRoot } from 'react-dom/client';          // root API

// IMPORTANT: create the promise OUTSIDE render (or cache it); a new promise per render loops forever
const menuPromise = new Promise(resolve =>              // fake network request
  setTimeout(() => resolve(['Biryani', 'Dosa', 'Paneer Tikka']), 1000) // resolves after 1 second
);

function Menu({ promise }) {
  const items = use(promise);                           // suspends until the promise resolves
  return (
    <ul>
      {items.map(i => <li key={i}>{i}</li>)}            {/* real UI once data is ready */}
    </ul>
  );
}

function App() {
  return (
    <div>
      <h1>Restaurant</h1>                               {/* shows immediately */}
      <Suspense fallback={<p>Loading menu...</p>}>      {/* boundary owns the loading UI */}
        <Menu promise={menuPromise} />                  {/* promise passed as a prop */}
      </Suspense>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: TanStack Query v5 useSuspenseQuery + nested Suspense + Error Boundary + parallel fetching
import { Suspense } from 'react';                                     // Suspense boundary
import {
  QueryClient, QueryClientProvider, useSuspenseQuery, QueryErrorResetBoundary,
} from '@tanstack/react-query';                                       // TanStack Query v5
import { ErrorBoundary } from 'react-error-boundary';                 // popular error boundary package
import { createRoot } from 'react-dom/client';                        // root API

const queryClient = new QueryClient();                                // one client for the app

const fetchJson = url => fetch(url).then(r => {                       // helper that throws on bad status
  if (!r.ok) throw new Error(`HTTP ${r.status}`);                     // lets the error boundary catch it
  return r.json();
});

function Menu({ id }) {
  // data is NEVER undefined here: the hook suspends until it is ready
  const { data } = useSuspenseQuery({
    queryKey: ['menu', id],                                           // cache key
    queryFn: () => fetchJson(`/api/restaurants/${id}/menu`),          // fetcher
  });
  return <ul>{data.map(i => <li key={i.id}>{i.name}</li>)}</ul>;     // render directly
}

function Reviews({ id }) {
  const { data } = useSuspenseQuery({
    queryKey: ['reviews', id],
    queryFn: () => fetchJson(`/api/restaurants/${id}/reviews`),
  });
  return <p>{data.length} reviews</p>;                                // render directly
}

function RestaurantPage({ id }) {
  return (
    <QueryErrorResetBoundary>{({ reset }) => (                        // resets failed queries on retry
      <ErrorBoundary
        onReset={reset}                                               // retry clears the error state
        fallbackRender={({ resetErrorBoundary }) => (
          <button onClick={resetErrorBoundary}>Something failed. Retry</button> // error UI
        )}
      >
        <h1>Restaurant {id}</h1>                                      {/* instant content */}
        <Suspense fallback={<p>Loading menu...</p>}>                  {/* independent region 1 */}
          <Menu id={id} />
        </Suspense>
        <Suspense fallback={<p>Loading reviews...</p>}>               {/* independent region 2 */}
          <Reviews id={id} />
        </Suspense>
      </ErrorBoundary>
    )}</QueryErrorResetBoundary>
  );
}

createRoot(document.getElementById('root')).render(
  <QueryClientProvider client={queryClient}>                          {/* provides the cache */}
    <RestaurantPage id="42" />
  </QueryClientProvider>
);
```

---

## 🟠 Real App Integration

In the Next.js App Router, Suspense for data is built in. Server Components can be `async` and `await` data directly; wrap slow parts in `<Suspense>` and Next.js streams the shell first, then the slow parts as they finish. A `loading.js` file creates a Suspense boundary for the whole route automatically.

```jsx
// app/restaurant/[id]/page.jsx (Server Component, async)
import { Suspense } from 'react';                          // boundary for streaming

async function Menu({ id }) {                              // async Server Component: awaits data directly
  const res = await fetch(`https://api.example.com/menu/${id}`); // runs on the server
  const items = await res.json();                          // parse JSON
  return <ul>{items.map(i => <li key={i.id}>{i.name}</li>)}</ul>;
}

async function Reviews({ id }) {                           // slower section
  const res = await fetch(`https://api.example.com/reviews/${id}`);
  const reviews = await res.json();
  return <p>{reviews.length} reviews</p>;
}

export default async function Page({ params }) {
  const { id } = await params;                             // Next.js 15+: params is a Promise
  return (
    <main>
      <h1>Restaurant {id}</h1>                             {/* streamed first */}
      <Suspense fallback={<p>Loading menu...</p>}><Menu id={id} /></Suspense>
      <Suspense fallback={<p>Loading reviews...</p>}><Reviews id={id} /></Suspense>
    </main>
  );
}
```

```jsx
// app/restaurant/[id]/loading.jsx: automatic Suspense fallback for the entire route segment
export default function Loading() {
  return <p>Loading restaurant...</p>;                     // shown instantly during navigation
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Creating the promise inside the component that calls `use()`
✅ **Correct:** Create it outside render (a Server Component, a cache, or a data library), then pass it in

```jsx
// Wrong: a new promise on every render → suspends again → infinite loop
function Menu() {
  const items = use(fetch('/api/menu').then(r => r.json())); // ❌ new promise each render
  return <List items={items} />;
}

// Right: the parent creates the promise once and passes it down
function Page() {
  const promise = useMemo(() => fetch('/api/menu').then(r => r.json()), []); // better: cache layer / framework
  return <Suspense fallback="..."><Menu promise={promise} /></Suspense>;
}
// Menu then calls use(promise) with the same promise each render
```

❌ **Mistake 2:** One giant Suspense boundary at the top
✅ **Correct:** Several boundaries around independent regions

```jsx
// Wrong: the whole page is blank until the slowest request finishes
<Suspense fallback={<FullPageSpinner />}><Menu /><Reviews /><Offers /></Suspense>  {/* ❌ */}

// Right: each region appears when ready
<Suspense fallback={<MenuSkeleton />}><Menu /></Suspense>          {/* ✅ */}
<Suspense fallback={<ReviewsSkeleton />}><Reviews /></Suspense>
```

❌ **Mistake 3:** Expecting Suspense to handle errors
✅ **Correct:** Pair it with an Error Boundary (or Next.js `error.js`)

```jsx
// Wrong: a rejected promise has no UI → the whole app crashes
<Suspense fallback="..."><Menu /></Suspense>                      // ❌ no error handling

// Right
<ErrorBoundary fallback={<p>Failed to load</p>}>                  {/* ✅ catches rejections */}
  <Suspense fallback="..."><Menu /></Suspense>
</ErrorBoundary>
```

---

## 🧠 Tricky Interview Question

```jsx
function Parent() {
  return (
    <Suspense fallback={<p>Outer</p>}>
      <A />
      <Suspense fallback={<p>Inner</p>}>
        <B />
      </Suspense>
    </Suspense>
  );
}
// A suspends for 1s; B suspends for 3s.
// Question: what does the user see at 0s, 1s and 3s?
```
**Answer:** At 0s the user sees "Outer". `A` is a direct child of the outer boundary and suspends, so the outer fallback replaces its whole subtree, including the inner boundary (the inner boundary is not even shown yet). At 1s `A` is ready, the outer boundary re-renders, `A` appears, and now `B` is rendered for the first time inside the inner boundary and suspends, so the user sees `A` plus "Inner". (If `B` had already started fetching earlier, for example through a preload, it could be ready sooner; `B` only begins suspending once React renders it, which is why waterfalls happen.) At 3s `B`'s data arrives and "Inner" is replaced by `B`. Lesson: a suspended component only affects the nearest boundary above it, and siblings under the same boundary wait together.

---

## ⚫ Interview Questions + Answers

Q1: What is Suspense and what is it used for?
A1: A component that shows a fallback while its children are not ready. Originally used with `React.lazy` for code; since React 18/19 it also covers data fetching through compatible sources (`use()`, TanStack Query, Relay, Server Components) and enables streaming SSR.

Q2: How does a component "suspend"?
A2: Internally it throws a promise (React-internal protocol). React catches it at the nearest Suspense boundary, shows the fallback, and retries the render when the promise settles. In React 19, `use(promise)` is the official way to read a promise in render.

Q3: Can you use Suspense with `useEffect` data fetching?
A3: No. Suspense does not detect fetches inside effects or event handlers. The data must be read during render through a Suspense-compatible API.

Q4: What is a request waterfall and how do you avoid it?
A4: When a child starts fetching only after the parent finishes rendering and loading, requests run in sequence. Avoid it by fetching in parallel (start promises early, `Promise.all`, route-level preloading, or Server Components that fetch on the server), and by splitting boundaries so independent data does not block each other.

Q5: Suspense vs `loading.js` in Next.js?
A5: `loading.js` is a convention that wraps the route segment in an automatic `<Suspense>` boundary using that component as fallback. Manual `<Suspense>` inside the page gives finer control over smaller regions. Both allow streaming.

---

## 🔷 When to Use + When Not to Use
✅ **Use Suspense for data when:**
- You use Server Components or a library with Suspense support (TanStack Query, Relay, `use()`)
- You want independent, progressively loading regions
- You want to remove repeated `isLoading` branches

❌ **Avoid when:**
- Your data layer is plain `useEffect` + `fetch` (it will not work)
- You need very custom per-component loading logic that boundaries cannot express
- You are on React 17 or below (limited support)

---

## 📊 Visual Diagram

```
  <Suspense fallback={Skeleton}>
        │
        ▼
     <Menu>  ── use(promise) ── not ready ──▶ SUSPEND
        │                                       │
        │          React shows fallback ◀───────┘
        │
   promise resolves ──▶ React retries Menu ──▶ data present ──▶ real UI replaces Skeleton

  Streaming (Next.js):
  t=0    HTML shell + <h1> + [Menu skeleton] [Reviews skeleton]   ← sent immediately
  t=1s   ...stream: Menu HTML replaces its skeleton
  t=3s   ...stream: Reviews HTML replaces its skeleton
```

Re-render behavior: a suspended component's render is discarded and retried, so side effects during render are unsafe. Already-visible content stays when you update inside `startTransition` (the old UI remains instead of reverting to the fallback). Performance impact: faster first paint through streaming and parallel regions, and fewer state variables.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Suspense | Boundary that shows a fallback while waiting | इंतज़ार के दौरान fallback दिखाने वाला boundary |
| Fallback | UI shown while loading | Loading के दौरान दिखने वाला UI |
| `use()` | React 19 API to read a promise or context in render | Render में promise या context पढ़ने वाला React 19 API |
| useSuspenseQuery | TanStack Query hook that suspends | Suspend करने वाला TanStack Query hook |
| Streaming SSR | Sending HTML in pieces as it is ready | तैयार होते ही HTML टुकड़ों में भेजना |
| Waterfall | Requests that run one after another | एक के बाद एक चलने वाले requests |
| Error Boundary | Catches rendering errors | Rendering errors पकड़ने वाला component |
| loading.js | Next.js route-level Suspense fallback | Next.js का route-level Suspense fallback |

---

## ⚡ 3-Line Summary
**English:**
1. Suspense lets components wait for data while a boundary shows the fallback, replacing manual `isLoading` flags.
2. It works only with Suspense-aware sources (`use()`, `useSuspenseQuery`, Server Components), not `useEffect` fetches, and needs an Error Boundary for failures.
3. Use several small boundaries and parallel fetching; in Next.js, async Server Components, `<Suspense>` and `loading.js` stream the page progressively.

**Hindi:**
1. Suspense components को data का इंतज़ार करने देता है जबकि boundary fallback दिखाता है, और हाथ के `isLoading` flags की जगह लेता है।
2. यह सिर्फ़ Suspense-aware sources (`use()`, `useSuspenseQuery`, Server Components) के साथ काम करता है, `useEffect` fetch के साथ नहीं, और failures के लिए Error Boundary चाहिए।
3. कई छोटे boundaries और parallel fetching इस्तेमाल करो; Next.js में async Server Components, `<Suspense>` और `loading.js` page को धीरे-धीरे stream करते हैं।

---

## ➡️ Next Topic
**133. Concurrent Mode** — React 18 का concurrent rendering क्या है, rendering को रोका और बाधित कैसे किया जा सकता है, और इससे UI कैसे responsive रहता है।
