# F03. Rendering Patterns — CSR vs SSR vs SSG vs ISR
# हिंदी में: Rendering Patterns — पेज का HTML कहाँ और कब बनता है: ब्राउज़र में (CSR), हर request पर सर्वर में (SSR), build के समय (SSG), या समय-समय पर दोबारा (ISR)

---

## 🔵 Simple Definition (English)
Rendering patterns decide **where and when HTML is generated**:
- **CSR (Client-Side Rendering):** the server sends an almost empty HTML shell + JS bundle; the browser fetches data and renders everything (classic React SPA, Create React App, Vite).
- **SSR (Server-Side Rendering):** the server renders full HTML **on each request** (with data), then the browser **hydrates** it with JS to make it interactive.
- **SSG (Static Site Generation):** HTML is generated **at build time** and served from a CDN; super fast, but data is as fresh as the last build.
- **ISR (Incremental Static Regeneration):** static pages that **regenerate in the background** after a revalidation period or on demand (Next.js).
Plus modern variants: **streaming SSR**, **React Server Components** (F04), **partial prerendering**, and **islands architecture** (Astro).

## 🔵 सरल परिभाषा (Hindi)
पेज का HTML कहाँ बनेगा: CSR = ब्राउज़र में JS से (React SPA); SSR = हर request पर सर्वर में, फिर ब्राउज़र में hydration; SSG = build के समय पहले से बने HTML, CDN से; ISR = static पेज जो कुछ समय बाद या ज़रूरत पर पीछे से दोबारा बन जाते हैं।
सही चुनाव से speed, SEO और ख़र्च तय होते हैं।

---

## 🔴 Problem it Solves
Each pattern solves a different problem:
- **CSR** made rich, app-like UIs easy, but gives a **blank screen until JS loads**, **poor SEO** (crawlers may not run JS well) and slow first load on low-end phones.
- **SSR** gives **fast first content and SEO** for dynamic, personalized pages, but costs **server time per request** and has a **hydration delay**.
- **SSG** gives the **fastest, cheapest pages** (CDN), but rebuilding millions of pages on every change is slow.
- **ISR** combines static speed with **fresh-enough data** for large catalogs (e-commerce, blogs).

Choosing per page/route is a core frontend architecture decision and a favourite interview question.

## 🔴 यह क्यों बना? (Hindi)
CSR से rich ऐप आसान बने पर पहले सफ़ेद स्क्रीन, SEO कमज़ोर; SSR से जल्दी content और SEO, पर हर request पर सर्वर का ख़र्च; SSG सबसे तेज़ और सस्ता, पर लाखों pages हर बदलाव पर दोबारा build करना धीमा; ISR दोनों का मेल — static की स्पीड, काफ़ी ताज़ा डेटा।
हर route के लिए सही तरीका चुनना frontend architecture का मुख्य फ़ैसला है।

---

## 🟢 How it Works — Step by Step

### Timelines

```
CSR:  request → [empty HTML + JS] → download JS → run → fetch data → render → interactive
      Screen: ⬜⬜⬜⬜⬜⬜ spinner ... content (late FCP/LCP, interactive ≈ same time)

SSR:  request → server fetches data + renders HTML → [full HTML] → browser paints content quickly
      → downloads JS → HYDRATE (attach event handlers) → interactive
      Screen: content early 🟩, clicks work only after hydration (TTI gap)

SSG:  build time: render all pages → upload to CDN
      request → CDN returns HTML instantly → hydrate
      Fastest TTFB/LCP; data = as of last build

ISR:  page built once (or on first request), cached at CDN/server
      request after revalidate window → serve STALE page instantly + regenerate in background
      → next visitors get fresh page (stale-while-revalidate for HTML)
      on-demand: revalidateTag/revalidatePath when CMS/product changes
```

### Comparison

```
┌──────────────┬───────────────┬───────────────┬───────────────┬───────────────────────┐
│              │ CSR           │ SSR           │ SSG           │ ISR                   │
├──────────────┼───────────────┼───────────────┼───────────────┼───────────────────────┤
│ HTML made    │ Browser       │ Server/request│ Build time    │ Build + background    │
│ First paint  │ Slow          │ Fast          │ Fastest       │ Fastest               │
│ SEO          │ Weak*         │ Great         │ Great         │ Great                 │
│ Data fresh-  │ Real-time     │ Per request   │ Stale till    │ Fresh within N sec /  │
│ ness         │               │               │ rebuild       │ on-demand             │
│ Server cost  │ Low (static)  │ High          │ Lowest        │ Low                   │
│ Personalized │ Yes           │ Yes           │ No (or client)│ No (or client islands)│
│ Best for     │ Dashboards,   │ Personalized/ │ Docs, blogs,  │ Product pages, large  │
│              │ admin, apps   │ real-time     │ marketing     │ catalogs, news        │
│              │ behind login  │ pages, search │ pages         │                       │
└──────────────┴───────────────┴───────────────┴───────────────┴───────────────────────┘
* Google can render JS, but slower and less reliably; other crawlers/social previews often can't.
```

### Hydration (the hidden cost of SSR/SSG with React)

```
Server sends HTML → browser shows it → React downloads the SAME components' JS → re-runs them →
attaches event listeners → state becomes live.
Problems: big JS → long hydration → page looks ready but clicks don't work ("uncanny valley");
          hydration mismatch errors if server & client render differently (Date.now(), window checks)
Mitigations: React Server Components (less JS shipped — F04), streaming + selective hydration
             (React 18), islands (hydrate only interactive parts), code splitting, partial prerendering
```

### Mixing patterns per route (typical e-commerce in Next.js)

```
/                      → ISR (revalidate 60s) + client fetch for personalized widgets
/product/[slug]        → ISR (revalidate 300s + on-demand revalidateTag on price change)
/search?q=             → SSR (dynamic, SEO for category searches) or CSR for filters
/cart, /checkout       → CSR/SSR dynamic (personal, never cached publicly)
/account/*             → SSR with auth (or CSR behind login)
/blog/*, /help/*       → SSG
/admin                 → CSR SPA (no SEO)
```

### Edge rendering & streaming
```
Edge SSR (Vercel/Cloudflare Workers): render close to user → lower TTFB (watch DB latency from edge!)
Streaming SSR: send HTML shell immediately, stream slower sections as data resolves (<Suspense>)
Partial Prerendering (Next.js): static shell from CDN + dynamic holes streamed per request
```

## 🟢 कैसे काम करता है? (Hindi)
1. CSR: ख़ाली HTML + JS → ब्राउज़र JS चलाकर डेटा लाता और दिखाता है — पहले spinner, SEO कमज़ोर; login के पीछे वाले dashboards के लिए ठीक।
2. SSR: हर request पर सर्वर डेटा लाकर पूरा HTML भेजता है → जल्दी दिखता है → फिर hydration से clicks चालू।
3. SSG: build के समय HTML बनकर CDN पर — सबसे तेज़, पर डेटा आख़िरी build जितना पुराना।
4. ISR: static पेज, तय समय बाद (या product बदलने पर) पीछे से दोबारा बनता है — पुराना तुरंत दिखाओ, नया पीछे बनाओ।
5. Hydration महँगा है (बड़ा JS) — Server Components, streaming, islands से कम करो; हर route के लिए अलग तरीका चुनो।

---

## 🟡 Real World Example

**Flipkart / Myntra / Amazon** — product and category pages are server-rendered or statically regenerated for SEO and fast first paint on mobile. Personalized parts (recommendations, cart count) load client-side, and checkout is dynamic.

**Netflix** — the logged-out landing page moved away from heavy client-side React to server-rendered HTML with minimal JS, and reported significantly faster load times. Personalization happens after login.

**Vercel / Next.js adopters (Notion's marketing site, Nike, TikTok web, Hashnode)** — use SSG/ISR for content and marketing pages and SSR or RSC for dynamic pages. ISR lets large catalogs avoid full rebuilds.

**Dashboards (Razorpay dashboard, admin panels)** — commonly CSR SPAs behind login, where SEO doesn't matter and rich interactivity does.

## 🟡 Real Example Hindi में
Flipkart/Myntra के product pages SEO और जल्दी दिखने के लिए server पर बनते हैं (SSR/ISR), recommendations और cart बाद में client पर; checkout dynamic।
Netflix ने logged-out landing page को भारी React से server-rendered HTML पर बदला और load काफ़ी तेज़ हुआ। Razorpay जैसे dashboards login के पीछे CSR SPA होते हैं।

---

## 🟠 My Stack Example

### Next.js App Router — choose per route
```tsx
// app/blog/[slug]/page.tsx — SSG (build time) for known slugs
export async function generateStaticParams() {
  return (await getAllPosts()).map((p) => ({ slug: p.slug }));
}
export default async function Post({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;                    // Next.js 15+: params is a Promise
  const post = await getPost(slug);                 // runs at build time
  return <Article post={post} />;
}

// app/product/[slug]/page.tsx — ISR: regenerate every 5 min + on-demand by tag
export const revalidate = 300;
export default async function Product({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const p = await fetch(`${API}/catalog/${slug}`, { next: { tags: [`product-${slug}`] } }).then(r => r.json());
  return <ProductView product={p} />;               // price/stock island refreshes client-side
}

// app/search/page.tsx — SSR per request (dynamic)
export const dynamic = 'force-dynamic';
export default async function Search({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const { q = '' } = await searchParams;
  const results = await fetch(`${API}/search?q=${encodeURIComponent(q)}`, { cache: 'no-store' }).then(r => r.json());
  return <Results items={results} />;
}

// app/dashboard/page.tsx — client-rendered interactive area
'use client';
export default function Dashboard() {
  const { data } = useQuery({ queryKey: ['stats'], queryFn: getStats });
  return <Charts data={data} />;
}
```

### On-demand revalidation (CMS/admin changes price → regenerate page)
```ts
// app/api/revalidate/route.ts
import { revalidateTag } from 'next/cache';
export async function POST(req: Request) {
  const { tag, secret } = await req.json();
  if (secret !== process.env.REVALIDATE_SECRET) return new Response('Unauthorized', { status: 401 });
  revalidateTag(tag);                              // e.g. "product-iphone-16"
  return Response.json({ revalidated: true });
}
// Node backend after price update: POST https://shop.myapp.com/api/revalidate { tag: "product-iphone-16" }
```

### Streaming SSR with Suspense (fast shell, slow parts later)
```tsx
export default async function ProductPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return (
    <>
      <ProductHeader slug={slug} />                         {/* fast */}
      <Suspense fallback={<ReviewsSkeleton />}>
        <Reviews slug={slug} />                             {/* slow API → streamed when ready */}
      </Suspense>
    </>
  );
}
```

### Avoid hydration mismatches
```tsx
// ❌ different on server and client
<span>{new Date().toLocaleTimeString()}</span>
// ✅ render on client only after mount, or pass a server-generated value
const [now, setNow] = useState<string | null>(null);
useEffect(() => setNow(new Date().toLocaleTimeString()), []);
```

### Plain React + Vite SPA (CSR) — when it's the right call
```
Internal tools / admin dashboards / apps behind login → Vite + React Router + React Query is simple,
cheap to host (S3 + CloudFront), and fast enough with code splitting.
```

### React Native perspective
```
RN apps are "client-rendered" natively — no SEO concern; first-screen speed comes from bundle size,
Hermes bytecode, cached data (MMKV/React Query persist), and skeletons (Topics M03, M06).
```

---

## ⚫ Interview Questions + Answers

**Q1: Compare CSR, SSR, SSG and ISR.**
A1: CSR renders in the browser after downloading JS. It's cheap to host and highly interactive, but has a slow first paint and weaker SEO, so it fits authenticated apps and dashboards. SSR renders HTML per request on the server, giving fast content and SEO for dynamic or personalized pages, at the cost of server load and a hydration delay. SSG pre-renders at build time and serves from a CDN, the fastest and cheapest option, but data is only as fresh as the last build, so it fits docs and marketing. ISR is static pages regenerated periodically or on demand in the background, which gives static speed with fresh-enough data for large catalogs.

**Q2: What is hydration and what problems does it cause?**
A2: After server-rendered HTML is displayed, the client downloads the JavaScript for the same components, re-executes them to rebuild the virtual tree and attaches event handlers, which makes the page interactive. Problems: a delay between visible and interactive (heavy JS, poor INP or TTI), duplicated work (render twice), and hydration mismatch bugs when server and client output differ. Mitigations: ship less JS (Server Components, islands), selective or streaming hydration, code splitting, and deterministic rendering.

**Q3: Which rendering strategy would you choose for an e-commerce site?**
A3: Mix per route. The home page and product and category pages use SSG or ISR (with on-demand revalidation when prices or stock change) for SEO and fast loads, with personalized and volatile bits (recommendations, live stock, cart count) fetched client-side or streamed. Search results use SSR or ISR for SEO landing pages and CSR for interactive filtering. Cart, checkout and account pages are dynamic SSR or CSR, never publicly cached. Admin uses a CSR SPA.

**Q4: How does ISR work under the hood?**
A4: A page is generated at build time or on first request and cached (CDN or server). For requests after the revalidation window, the cached stale page is served immediately while a background regeneration fetches fresh data and re-renders. Once done, the cache is replaced and later visitors see the new version (stale-while-revalidate for HTML). On-demand revalidation (`revalidateTag`/`revalidatePath`) invalidates specific pages when data changes, typically triggered by a webhook from the CMS or backend.

**Q5: When is SSR a bad idea?**
A5: For highly interactive apps behind login where SEO doesn't matter (dashboards, editors), where SSR adds server cost and complexity without much benefit. For pages whose data is slow to fetch, where SSR delays TTFB unless you stream. Under extreme traffic for content that could be static or cached (use SSG/ISR plus a CDN). And when the team can't handle server infrastructure and hydration pitfalls. Also, edge SSR far from the database can increase latency.

---

## 🔷 Trade-offs
✅ CSR: simple hosting, rich interactivity — ❌ slow first paint, SEO, low-end devices.
✅ SSR: SEO + fast content + personalization — ❌ server cost, TTFB, hydration.
✅ SSG: fastest, cheapest, most reliable — ❌ stale data, long builds for huge sites.
✅ ISR: static speed + freshness — ❌ brief staleness, platform-specific (Next.js), cache invalidation care.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CSR | Rendering in the browser | ब्राउज़र में बनाना |
| SSR | Rendering on server per request | हर request पर सर्वर में |
| SSG | Rendering at build time | build के समय बनाना |
| ISR | Background regeneration of static pages | पीछे से दोबारा बनाना |
| Hydration | Attaching JS interactivity to HTML | HTML में JS जान डालना |
| TTFB | Time to first byte | पहला बाइट आने का समय |
| Streaming SSR | Sending HTML in chunks | HTML टुकड़ों में भेजना |
| Revalidation | Refreshing cached page | cache पेज ताज़ा करना |
| Islands architecture | Hydrate only interactive parts | सिर्फ़ interactive हिस्से |
| Edge rendering | Rendering near the user | यूज़र के पास render |

---

## ⚡ 3-Line Summary
**English:**
1. CSR (browser), SSR (server per request), SSG (build time), ISR (static + background regeneration) trade off speed, SEO, freshness and cost.
2. SSR/SSG still pay hydration cost — reduce JS with RSC, streaming, islands; avoid hydration mismatches.
3. Choose per route: content/catalog → SSG/ISR, personalized/real-time → SSR/streaming, logged-in apps → CSR.

**Hindi:**
1. CSR, SSR, SSG, ISR — speed, SEO, ताज़गी और ख़र्च में अलग-अलग फ़ायदे।
2. SSR/SSG में भी hydration का ख़र्च — RSC, streaming, islands से JS घटाओ।
3. हर route के लिए चुनो: catalog → SSG/ISR, personalized → SSR, login वाले ऐप → CSR।

---

## ➡️ Next Topic Suggestion
**F04. React Server Components + Streaming (Next.js App Router)** — The newest rendering model: components that run only on the server, ship zero JS, stream to the client and reduce hydration. Next: how RSC, Suspense streaming and Server Actions work.
