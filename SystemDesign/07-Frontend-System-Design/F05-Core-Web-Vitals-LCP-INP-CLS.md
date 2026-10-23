# F05. Core Web Vitals (LCP, INP, CLS)
# हिंदी में: Core Web Vitals — Google के तीन मुख्य नाप जो बताते हैं कि असली यूज़र के लिए पेज कितना तेज़, कितना जल्दी जवाब देने वाला और कितना स्थिर है: LCP (लोड), INP (जवाब), CLS (स्थिरता)

---

## 🔵 Simple Definition (English)
**Core Web Vitals (CWV)** are Google's user-centric metrics for page experience, measured on **real users**:
- **LCP — Largest Contentful Paint:** time until the largest visible element (hero image, heading, big text block) is rendered. **Good ≤ 2.5 s.**
- **INP — Interaction to Next Paint:** responsiveness. The latency from a user interaction (tap, click, key) to the next frame painted, taking roughly the worst interaction over the visit. **Good ≤ 200 ms.** (INP replaced FID in March 2024.)
- **CLS — Cumulative Layout Shift:** visual stability. How much content unexpectedly moves (largest burst of layout shifts). **Good ≤ 0.1.**
A page "passes" when the **75th percentile** of real page loads (mobile and desktop separately) is in the "good" range.
Supporting metrics: **TTFB** (server response), **FCP** (first content), **TBT** (lab proxy for INP).

## 🔵 सरल परिभाषा (Hindi)
Core Web Vitals असली यूज़र्स पर नापे गए तीन मुख्य नंबर हैं: LCP — सबसे बड़ा content (hero image/heading) कितनी देर में दिखा (≤ 2.5 सेकंड अच्छा); INP — tap/click के बाद स्क्रीन कितनी जल्दी बदली (≤ 200 ms अच्छा); CLS — content कितना अचानक खिसका (≤ 0.1 अच्छा)।
75% यूज़र्स के अनुभव (75th percentile) अच्छे range में हों तो पेज पास।

---

## 🔴 Problem it Solves
Old metrics like "page load time" or `onload` didn't reflect what users feel:
- A page can fire `load` quickly but show its main content late (LCP), or look loaded but not respond to taps (INP).
- Content jumping while you try to tap (CLS) causes mis-clicks, such as tapping an ad or "Buy" by accident.
- Teams needed **shared, measurable targets** that correlate with business outcomes (bounce rate, conversions).

CWV give standard thresholds, field measurement (CrUX), and they are a **Google Search ranking signal** (page experience), so performance becomes a business priority.

## 🔴 यह क्यों बना? (Hindi)
पुराने नाप ("page load time") यूज़र का अनुभव नहीं बताते थे — पेज load दिखा पर असली content देर से आया, या tap का जवाब नहीं मिला, या content खिसकने से ग़लत बटन दब गया।
CWV सबको एक जैसे, नापने लायक लक्ष्य देते हैं जो bounce rate और बिक्री से जुड़े हैं, और Google search ranking में भी गिने जाते हैं।

---

## 🟢 How it Works — Step by Step

### Thresholds (at p75 of real users)

```
             GOOD        NEEDS IMPROVEMENT     POOR
LCP        ≤ 2.5 s        2.5 – 4.0 s          > 4.0 s
INP        ≤ 200 ms       200 – 500 ms         > 500 ms
CLS        ≤ 0.1          0.1 – 0.25           > 0.25
(supporting) TTFB ≤ 0.8 s, FCP ≤ 1.8 s
```

### LCP — breakdown and fixes

```
LCP = TTFB + resource load delay + resource load time + element render delay

TTFB slow?            → CDN, caching (SSG/ISR), faster backend, edge, avoid redirects
Load delay?           → LCP image discovered late (in CSS/JS) → put <img> in HTML, preload,
                        fetchpriority="high"; don't lazy-load the LCP image!
Load time?            → compress, modern formats (AVIF/WebP), right size (srcset), CDN
Render delay?         → render-blocking CSS/JS, client-side rendering of hero → SSR, inline critical CSS,
                        defer JS, font-display: swap
```

### INP — what happens in one interaction

```
User taps ──► [input delay] ──► [event handler processing] ──► [presentation delay] ──► next paint
              main thread busy   your JS (setState, work)        style/layout/paint of update
              with other tasks

Fixes:
- Break long tasks (yield: scheduler.yield(), setTimeout), avoid heavy work in handlers
- Show feedback immediately; defer non-urgent work (startTransition / useDeferredValue in React)
- Reduce hydration & third-party scripts (tag managers, chat widgets, ads)
- Debounce expensive input handlers; virtualize big lists; avoid huge DOM
- Move CPU work to Web Workers
- Avoid layout thrashing; keep re-renders small (memo, state colocation)
```

### CLS — causes and fixes

```
Cause                                       Fix
──────────────────────────────────────────  ────────────────────────────────────────────────
Images/videos without width/height          width/height attrs or CSS aspect-ratio
Ads/embeds/iframes injected late            reserve space (min-height), placeholders
Content inserted above existing content     insert below, or on user action; use transform
  (cookie banner, "app download" bar)         overlays, not push-down
Web fonts swapping (FOUT changes size)      font-display: optional/swap + size-adjust, preload fonts
Animations of top/height                    animate transform instead
Note: shifts within 500 ms after a user input don't count (expected changes)
```

### Field vs lab data

```
FIELD (RUM — real users)                          LAB (synthetic)
- CrUX (Chrome UX Report, 28-day p75)             - Lighthouse, PageSpeed Insights lab section,
- Search Console CWV report                         WebPageTest, Chrome DevTools Performance
- Your own RUM: web-vitals JS library → analytics - Repeatable, good for debugging & CI budgets
- The truth for ranking & users                   - Can't measure INP directly → use TBT as proxy
Always validate lab fixes against field data (devices/networks differ, esp. India: low-end Android, 4G)
```

### Performance budgets in CI

```
Lighthouse CI on each PR: LCP < 2.5s (simulated mobile), TBT < 200ms, CLS < 0.1, JS < 170 KB gz
Bundle size check (size-limit) → fail PR if main chunk grows > X KB
```

## 🟢 कैसे काम करता है? (Hindi)
1. LCP = सर्वर जवाब (TTFB) + image खोजने में देरी + डाउनलोड + render; सुधार: CDN/SSG, hero image HTML में, preload + fetchpriority, सही size/AVIF, LCP image को lazy-load नहीं।
2. INP = tap से अगले paint तक का समय; सुधार: लंबे JS काम तोड़ो, handler हल्का, startTransition, कम third-party scripts, Web Worker, virtualization।
3. CLS = अचानक खिसकना; सुधार: images को width/height या aspect-ratio, ads/banners के लिए जगह पहले से, ऊपर content मत घुसाओ, fonts सही से।
4. Field data (असली यूज़र — CrUX, web-vitals library) असली सच है; lab (Lighthouse) debugging के लिए; lab में INP की जगह TBT।
5. CI में performance budget रखो — LCP, TBT, CLS और JS size की सीमा पार हो तो PR fail।

---

## 🟡 Real World Example

**The Economic Times (India)** — a web.dev case study reports that the team brought CLS and LCP into the "good" range by reserving space for ads and images and optimizing loading, and saw a large reduction in bounce rate (reported ~43%).

**redBus (India)** — a web.dev case study describes improving INP by reducing main-thread work and optimizing input handlers on their search and listing pages, which was associated with a reported ~7% increase in sales.

**Vodafone (Italy)** — an A/B test reported that a ~31% LCP improvement led to ~8% more sales, a widely cited example linking LCP to revenue.

**Google Search ranking** — CWV are part of page experience signals. Search Console shows URL groups failing CWV based on CrUX field data.

## 🟡 Real Example Hindi में
The Economic Times ने ads और images के लिए पहले से जगह रखकर और loading सुधारकर CLS और LCP ठीक किए — bounce rate काफ़ी घटा (लगभग 43% बताया गया)।
redBus ने main-thread का काम घटाकर INP सुधारा और बिक्री में लगभग 7% बढ़ोतरी बताई। Vodafone में LCP 31% बेहतर होने पर 8% ज़्यादा बिक्री।

---

## 🟠 My Stack Example

### Collect field Web Vitals (Next.js / React) → backend analytics
```tsx
// app/web-vitals.tsx
'use client';
import { useReportWebVitals } from 'next/web-vitals';

export function WebVitals() {
  useReportWebVitals((metric) => {
    // metric: { name: 'LCP'|'INP'|'CLS'|'FCP'|'TTFB', value, rating, id, navigationType }
    const body = JSON.stringify({ ...metric, page: location.pathname, conn: (navigator as any).connection?.effectiveType });
    navigator.sendBeacon?.('/api/vitals', body) || fetch('/api/vitals', { method: 'POST', body, keepalive: true });
  });
  return null;
}
// For plain React/Vite: import { onLCP, onINP, onCLS } from 'web-vitals'; onINP(send, { reportAllChanges: false })
```

```python
# FastAPI collector → store in ClickHouse/Postgres, dashboard p75 by page/device/connection
@app.post("/api/vitals")
async def vitals(req: Request):
    m = await req.json()
    await db.execute("INSERT INTO web_vitals(name, value, rating, page, conn, ts) VALUES ($1,$2,$3,$4,$5, now())",
                     m["name"], m["value"], m["rating"], m["page"], m.get("conn"))
    return Response(status_code=204)
# SELECT page, percentile_cont(0.75) WITHIN GROUP (ORDER BY value) FROM web_vitals WHERE name='LCP' GROUP BY page;
```

### LCP: hero image done right
```tsx
<Image src={product.heroUrl} alt={product.name} width={800} height={800}
       priority                       /* preload + fetchpriority=high, no lazy */
       sizes="(max-width: 768px) 100vw, 50vw" />
```

### INP: keep the handler light, defer the heavy update
```tsx
'use client';
import { useState, useTransition, useDeferredValue } from 'react';

function ProductFilter({ products }: { products: Product[] }) {
  const [query, setQuery] = useState('');
  const deferred = useDeferredValue(query);                    // urgent: input; non-urgent: list filter
  const filtered = useMemo(() => products.filter(p => p.name.toLowerCase().includes(deferred.toLowerCase())), [products, deferred]);
  return (<>
    <input value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Search products" />
    <VirtualList items={filtered} />                              {/* virtualized → small DOM */}
  </>);
}
```

### CLS: reserve space for dynamic stuff
```css
.ad-slot { min-height: 250px; }                 /* ad loads into reserved box */
.banner-top { position: fixed; bottom: 0; }     /* app-install banner as overlay, not push-down */
img, video { max-width: 100%; height: auto; }  /* with width/height attrs set, browsers derive aspect-ratio → space reserved */
```

### Lighthouse CI budget (GitHub Actions)
```yaml
- name: Lighthouse CI
  run: npx @lhci/cli autorun --collect.url=https://preview.myapp.com --assert.preset=lighthouse:recommended
       --assert.assertions.largest-contentful-paint="['error',{maxNumericValue:2500}]"
       --assert.assertions.cumulative-layout-shift="['error',{maxNumericValue:0.1}]"
       --assert.assertions.total-blocking-time="['warn',{maxNumericValue:200}]"
```

### React Native equivalents (no CWV, but same ideas)
```
Startup: TTI / time-to-first-screen (Topic M03), frame drops (JS & UI thread fps), tap-to-response latency,
layout jumps when images load (give fixed dimensions). Measure with Sentry/Firebase Performance, Flashlight.
```

---

## ⚫ Interview Questions + Answers

**Q1: What are Core Web Vitals and their thresholds?**
A1: LCP measures loading: time to render the largest visible content element, good ≤ 2.5 s. INP measures responsiveness: latency from user interactions to the next paint across the visit, good ≤ 200 ms (it replaced FID in 2024). CLS measures visual stability: the largest burst of unexpected layout shifts, good ≤ 0.1. They're assessed at the 75th percentile of real-user page loads, separately for mobile and desktop.

**Q2: How would you improve a poor LCP?**
A2: Break LCP into TTFB, load delay, load time and render delay, then fix the biggest piece. TTFB: CDN, caching (SSG/ISR), faster backend. Load delay: make the LCP image discoverable in HTML, preload it with `fetchpriority=high`, and don't lazy-load it. Load time: right-sized responsive images in AVIF/WebP from a CDN. Render delay: remove render-blocking CSS and JS, server-render the hero instead of client-rendering it, and handle fonts with swap and preload.

**Q3: What causes poor INP and how do you fix it?**
A3: Long main-thread tasks (heavy hydration, third-party scripts, large re-renders, expensive event handlers, big DOM updates) delay processing and painting after input. Fixes: break up long tasks and yield to the main thread, make handlers do minimal work and give instant visual feedback, defer non-urgent updates with `startTransition`/`useDeferredValue`, memoize and colocate state to shrink re-renders, virtualize long lists, move compute to Web Workers, reduce JS and hydration (RSC, code splitting), and audit third-party scripts.

**Q4: How do you prevent layout shifts?**
A4: Always reserve space for media and embeds with width/height attributes or `aspect-ratio`. Reserve fixed slots for ads and late content. Never insert content above existing content unless in response to user interaction (use overlays or append below). Use `transform` animations instead of animating layout properties. Handle web fonts with preload, `font-display`, and metric-compatible fallbacks (`size-adjust`) so text doesn't reflow.

**Q5: What's the difference between lab and field data, and which do you trust?**
A5: Lab data (Lighthouse, WebPageTest) runs synthetic tests in a controlled environment. It's reproducible and great for debugging and CI budgets, but it simulates one device and network and can't truly measure INP (it uses TBT as a proxy). Field data (RUM, CrUX) comes from real users across devices, networks and interactions, and reflects actual experience, including in Search ranking. Use lab data to diagnose and prevent regressions, and field data to set priorities and confirm improvements.

---

## 🔷 Trade-offs
✅ Clear, user-centric targets tied to business and SEO.
❌ p75 can hide very poor experiences for the slowest 25% → also track p90/p95 and segments (device, network, region).
❌ Optimizing for metrics can be gamed (e.g., tiny hero) → focus on real UX.
❌ Third-party scripts (ads, analytics) often hurt CWV but bring revenue → negotiate budgets, load them lazily.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LCP | Largest Contentful Paint | सबसे बड़ा content दिखने का समय |
| INP | Interaction to Next Paint | tap के बाद जवाब का समय |
| CLS | Cumulative Layout Shift | content का खिसकना |
| FID | First Input Delay (old, replaced) | पुराना नाप |
| TTFB | Time to First Byte | पहला बाइट आने का समय |
| TBT | Total Blocking Time (lab) | main thread रुकने का समय |
| p75 | 75th percentile | 75% यूज़र्स की सीमा |
| RUM | Real User Monitoring | असली यूज़र का नाप |
| CrUX | Chrome UX Report | Chrome का field डेटा |
| Performance budget | Max allowed size/time | सीमा तय करना |

---

## ⚡ 3-Line Summary
**English:**
1. LCP ≤ 2.5 s (loading), INP ≤ 200 ms (responsiveness), CLS ≤ 0.1 (stability), judged at p75 of real users.
2. Fix LCP via TTFB/discovery/size/render-blocking; INP via shorter tasks & lighter handlers; CLS via reserved space.
3. Measure in the field (web-vitals → RUM, CrUX) and guard in CI with Lighthouse + bundle budgets.

**Hindi:**
1. LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 — असली यूज़र्स के p75 पर।
2. LCP: सर्वर, image खोज, size; INP: छोटे JS काम; CLS: पहले से जगह।
3. असली यूज़र से नापो (RUM, CrUX), CI में Lighthouse और bundle budget लगाओ।

---

## ➡️ Next Topic Suggestion
**F06. Bundling, Code Splitting + Lazy Loading** — The biggest lever for LCP and INP is usually how much JavaScript you ship. Next: bundlers, tree shaking, route and component splitting, lazy loading, and bundle budgets.
