# 173. getStaticProps (Pages)
# हिंदी में: getStaticProps — Build Time पर Data लाकर Static Page बनाना (Pages Router)

---

## 🔵 Simple Definition (English)
`getStaticProps` is a **Pages Router** function that runs on the server **at build time** (and again during revalidation if you set `revalidate`). The props it returns are used to generate a static HTML file once, which a CDN can serve to everyone very fast.

## 🔵 सरल परिभाषा (Hindi)
`getStaticProps` **Pages Router** का function है जो server पर **build time** पर चलता है (और `revalidate` सेट हो तो revalidation के समय दोबारा)। इसके return किए props से एक बार static HTML file बनती है, जिसे CDN सबको बहुत तेज़ी से परोस सकता है।

---

## 🔴 Problem it Solves

Server-side rendering on every request is slow and costly for pages that look the same to everyone: a blog post, a product category, a marketing page. Each visitor would wait for the database even though the answer is identical. Client-side fetching is worse for SEO and shows a spinner. `getStaticProps` moves the work to build time. The HTML is ready before any user arrives, so the response is just a file from the CDN. With `revalidate`, the page can be refreshed in the background so it does not go stale (this is called ISR, Incremental Static Regeneration).

```jsx
// PROBLEM: same blog post hits the database for every visitor
export async function getServerSideProps({ params }) {
  const post = await db.post.findUnique({ where: { slug: params.slug } }); // runs 10,000 times a day
  return { props: { post } };                                              // identical result each time
}
```

## 🔴 यह क्यों बना? (Hindi)
जिन pages पर सबको एक जैसा content दिखता है (blog post, product category, marketing page), उनके लिए हर request पर server-side rendering धीमा और महंगा है। जवाब एक जैसा होने पर भी हर visitor database का इंतज़ार करता है। Client-side fetching SEO के लिए और बुरा है और spinner दिखाता है। `getStaticProps` काम को build time पर ले जाता है। कोई user आए, उससे पहले HTML तैयार होता है, इसलिए response सिर्फ CDN से एक file होता है। `revalidate` के साथ page background में refresh हो सकता है ताकि वह पुराना न रहे (इसे ISR, Incremental Static Regeneration कहते हैं)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You run `next build`
Step 2 → Next.js finds pages exporting getStaticProps and calls each one on the server
Step 3 → Your function fetches data (CMS, DB, file system) and returns { props }
Step 4 → Next.js renders the page to HTML + a JSON file with the props
Step 5 → Files are stored and served from the CDN: no server work per visit
Step 6 → With revalidate: 60, after 60s the NEXT visitor still gets the old page
         while Next.js regenerates a new one in the background (stale-while-revalidate)
Step 7 → The following visitors get the new page

KEY: in `next dev` it runs on every request, so you only see static behaviour after
`next build && next start`
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप `next build` चलाते हैं
Step 2 → Next.js getStaticProps वाले pages ढूँढता है और हर एक को server पर call करता है
Step 3 → आपका function data लाता है (CMS, DB, file system) और { props } return करता है
Step 4 → Next.js page को HTML + props की JSON file में render करता है
Step 5 → Files CDN पर रखी और वहीं से परोसी जाती हैं: हर visit पर server का काम नहीं
Step 6 → revalidate: 60 के साथ, 60 सेकंड बाद अगले visitor को पुराना page ही मिलता है
         जबकि Next.js background में नया page बनाता है (stale-while-revalidate)
Step 7 → उसके बाद के visitors को नया page मिलता है

KEY: `next dev` में यह हर request पर चलता है, इसलिए static behaviour सिर्फ
`next build && next start` के बाद दिखता है
```

---

## 🟡 Real World Example
**Flipkart product category / Zomato "Best restaurants in Pune" page:** The list changes a few times a day, not every second, and a million people see the same page. The team uses `getStaticProps` with `revalidate: 300`. The page is served from the CDN in milliseconds, Google crawls complete HTML, and the data is at most five minutes old. A personalised "My cart" page, in contrast, would use SSR or client fetching.

## 🟡 Real Example Hindi mein
**Flipkart product category / Zomato "Pune के Best restaurants" page:** List दिन में कुछ बार बदलती है, हर सेकंड नहीं, और लाखों लोग वही page देखते हैं। Team `getStaticProps` को `revalidate: 300` के साथ इस्तेमाल करती है। Page CDN से milliseconds में आता है, Google को पूरा HTML मिलता है और data ज़्यादा से ज़्यादा पाँच मिनट पुराना होता है। इसके उलट personalised "My cart" page में SSR या client fetching चलेगी।

---

## 💻 Code Example — Basic

```jsx
// pages/offers.js : static page built once at `next build`

export default function OffersPage({ offers, builtAt }) {
  return (
    <main>
      <h1>Today's Offers</h1>
      <p>Page built at: {builtAt}</p>                           {/* does NOT change per visit */}
      <ul>
        {offers.map((o) => (
          <li key={o.id}>{o.title}</li>                         // key: id from the data
        ))}
      </ul>
    </main>
  );
}

// Runs at build time on the server only
export async function getStaticProps() {
  const res = await fetch('https://example.com/api/offers');    // absolute URL needed on the server
  if (!res.ok) throw new Error('Failed to fetch offers');       // fail the build rather than ship bad data
  const offers = await res.json();                              // parse JSON
  return {
    props: { offers, builtAt: new Date().toISOString() },       // serialisable props only
  };
}
```

## 💻 Code Example — Advanced

```jsx
// pages/restaurants/[city].js : ISR with fallback-safe data, 404 and error handling
import Head from 'next/head';
import { getRestaurantsByCity } from '../../lib/restaurants';  // hypothetical server helper

export default function CityPage({ city, restaurants, updatedAt }) {
  return (
    <>
      <Head>
        <title>Best restaurants in {city}</title>              {/* SEO title in static HTML */}
        <meta name="description" content={`Top ${restaurants.length} places in ${city}`} />
      </Head>
      <h1>Restaurants in {city}</h1>
      <small>Updated: {updatedAt}</small>
      <ul>
        {restaurants.map((r) => (
          <li key={r.id}>{r.name} ({r.rating})</li>
        ))}
      </ul>
    </>
  );
}

// context: params (from [city]), locale, preview / draftMode data
export async function getStaticProps({ params }) {
  try {
    const restaurants = await getRestaurantsByCity(params.city); // DB / CMS call

    if (!restaurants || restaurants.length === 0) {
      return { notFound: true, revalidate: 60 };               // 404, retry generation after 60s
    }

    return {
      props: {
        city: params.city,
        restaurants,
        updatedAt: new Date().toISOString(),
      },
      revalidate: 300,                                         // ISR: refresh at most every 5 minutes
    };
  } catch (err) {
    console.error('city page failed', err);                    // log on the server
    // Throwing during a revalidation keeps the previous good page (Next.js keeps the last success)
    throw err;
  }
}

// Needed because this is a dynamic route; see topic 174 for getStaticPaths
export async function getStaticPaths() {
  return {
    paths: [{ params: { city: 'pune' } }, { params: { city: 'delhi' } }], // pre-build top cities
    fallback: 'blocking',                                      // other cities render on first visit, then cache
  };
}
```

---

## 🟠 Next.js Connection

`getStaticProps` belongs to the Pages Router. In the App Router the same idea is **the default**: a Server Component that only uses cached `fetch` (or no dynamic APIs) is statically rendered, and you set revalidation with `export const revalidate = 300` or `fetch(url, { next: { revalidate: 300 } })`. Tag-based on-demand revalidation uses `revalidateTag` / `revalidatePath`.

```jsx
// App Router equivalent (Next.js 14/15), app/restaurants/[city]/page.jsx
import { notFound } from 'next/navigation';

export const revalidate = 300;                                 // ISR: regenerate at most every 5 minutes

export default async function CityPage({ params }) {
  const { city } = await params;                               // Next.js 15: params is a Promise
  const res = await fetch(`https://example.com/api/restaurants?city=${city}`, {
    next: { revalidate: 300 },                                 // per-fetch cache lifetime
  });
  if (!res.ok) notFound();                                     // like { notFound: true }
  const restaurants = await res.json();
  return (
    <ul>
      {restaurants.map((r) => <li key={r.id}>{r.name}</li>)}
    </ul>
  );
}
```
Version-dependent: Next.js 15 changed `fetch` to be **uncached by default** (14 cached by default), so check your version and set `cache: 'force-cache'` or `revalidate` explicitly. On-demand revalidation for the Pages Router uses `res.revalidate('/path')` in an API route.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Expecting request-specific data (`req`, cookies) in `getStaticProps`
✅ **Correct:** There is no request at build time. Use `getServerSideProps` for per-request data, or fetch user data on the client after the static shell loads.

```jsx
// Wrong: context has no req/res here, so this crashes
export async function getStaticProps({ req }) {
  const user = req.cookies.session;                             // ❌ req is undefined
  return { props: { user } };
}

// Right: static shell + client-side user data
export async function getStaticProps() {
  return { props: { menu: await getMenu() } };                  // ✅ same for everyone
}
// then in the component: useSWR('/api/me') for the personal part
```

❌ **Mistake 2:** Testing in `next dev` and thinking the page is static
✅ **Correct:** In dev, the function runs on every request. Verify with `next build && next start`. The build output marks the page with a filled circle (SSG) or the revalidate time.

```jsx
// Wrong assumption: "console.log in getStaticProps prints once, so it's static"
// In `next dev` it prints on EVERY refresh. ❌
// Right: run `next build && next start` and refresh. The log appears only at build time. ✅
```

❌ **Mistake 3:** Not setting `revalidate`, so the page stays stale until the next deploy
✅ **Correct:** Add `revalidate` (seconds) or trigger on-demand revalidation when content changes.

```jsx
// Wrong: price changes in the CMS never appear until a new build
return { props: { price } };                                    // ❌ frozen forever

// Right
return { props: { price }, revalidate: 120 };                   // ✅ at most 2 minutes old
```

---

## 🧠 Tricky Interview Question

```jsx
// pages/time.js  (production build, revalidate: 10)
export async function getStaticProps() {
  return { props: { t: new Date().toLocaleTimeString() }, revalidate: 10 };
}
export default function Time({ t }) {
  return <p>{t}</p>;
}
// Build at 10:00:00. A visitor arrives at 10:00:05, another at 10:00:15,
// another at 10:00:16. What time does each one see?
```
**Answer:** Visitor 1 (10:00:05) sees `10:00:00` because the page is still within the 10-second window. Visitor 2 (10:00:15) arrives after the window, so Next.js serves the **stale** `10:00:00` page immediately and triggers regeneration in the background. Visitor 3 (10:00:16) sees the newly generated page, with a time around `10:00:15`. So the user who triggers regeneration does not get the fresh page; the next one does (stale-while-revalidate). If regeneration throws an error, the old page keeps being served and Next.js retries on a later request.

---

## ⚫ Interview Questions + Answers

Q1: When does `getStaticProps` run?
A1: At build time on the server, and, if `revalidate` is set, again in the background after the interval passes and a request arrives. In `next dev` it runs on every request. It never runs in the browser and is excluded from the client bundle.

Q2: What does `revalidate` do?
A2: It is the number of seconds after which a cached static page may be regenerated. It enables ISR: serve the cached page instantly, and rebuild it in the background when it is older than the interval. Without it the page is fixed until the next build (unless you use on-demand revalidation).

Q3: What can `getStaticProps` return?
A3: `{ props }` (JSON-serialisable), `{ notFound: true }`, or `{ redirect }`. Each can also include `revalidate`. It receives `params`, `preview`, `previewData`, `locale`, `locales` and `defaultLocale`, but no `req`/`res`.

Q4: `getStaticProps` vs `getServerSideProps`?
A4: `getStaticProps` runs once per build/revalidation and serves a cached file (fast, cheap, same for everyone). `getServerSideProps` runs on every request (fresh, personalised, slower). Choose static whenever the page can be pre-rendered ahead of the user's request.

Q5: How do you update a static page immediately when content changes?
A5: Use on-demand revalidation. In the Pages Router, call `res.revalidate('/path')` inside an API route (for example from a CMS webhook, protected by a secret). In the App Router use `revalidatePath` or `revalidateTag`. This avoids waiting for the time-based interval.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Content is the same for all users: blogs, docs, marketing, product and category pages
- You want the best speed and lowest server cost, with CDN caching
- Data can be a little stale (use `revalidate` to bound it)

❌ **Avoid when:**
- Data depends on the user or request (cookies, auth, geolocation)
- Data must be accurate to the second (live stock, bidding)
- You have millions of pages that change constantly (build time and cache churn become a problem)

---

## 📊 Visual Diagram

```
  BUILD TIME                               RUNTIME (users)
  ──────────                               ───────────────
  next build
     │ getStaticProps()
     ▼
  page.html + page.json  ───▶  CDN  ◀──── Browser A  (instant, 0 server work)
                                 ▲   ◀──── Browser B
                                 │
   revalidate: 60                │
   after 60s, next request:      │
     serve OLD file ─────────────┘
     in background: getStaticProps() again → replace file with new one

  Re-render behavior: page props never change in the browser; a new version
  only arrives on the next navigation/refresh after regeneration.
  Performance: best TTFB of all rendering modes (static file from the edge).
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SSG | Static Site Generation at build time | Build time पर static page बनाना |
| ISR | Incremental Static Regeneration | Static page को background में दोबारा बनाना |
| revalidate | Seconds before a page may be rebuilt | Page दोबारा बनने से पहले के सेकंड |
| Stale-while-revalidate | Serve old, refresh in background | पुराना परोसो, background में नया बनाओ |
| CDN | Network of edge servers serving files | Edge servers का नेटवर्क जो files परोसता है |
| On-demand revalidation | Manual trigger to rebuild a page | Page को ख़ुद trigger करके दोबारा बनाना |
| notFound | Return value for a 404 page | 404 page के लिए return value |
| Build time | When `next build` runs | जब `next build` चलता है |

---

## ⚡ 3-Line Summary
**English:**
1. `getStaticProps` runs at build time (and on revalidation) to generate a static page that a CDN serves to everyone.
2. Add `revalidate` for ISR so content refreshes in the background, and use `notFound` or `redirect` for special cases.
3. It cannot see the request; use `getServerSideProps` for personal data. In the App Router, static rendering is the default.

**Hindi:**
1. `getStaticProps` build time पर (और revalidation पर) चलकर ऐसा static page बनाता है जिसे CDN सबको परोसता है।
2. ISR के लिए `revalidate` जोड़ो ताकि content background में refresh हो, और खास स्थितियों के लिए `notFound` या `redirect` इस्तेमाल करो।
3. यह request नहीं देख सकता; personal data के लिए `getServerSideProps` लो। App Router में static rendering ही default है।

---

## ➡️ Next Topic
**174. getStaticPaths (Pages)** — `[slug].js` जैसे dynamic routes के लिए build time पर कौन से URLs बनाने हैं, यह `getStaticPaths` से तय होता है, और `fallback` option से बाकी URLs कैसे संभलते हैं।
