# 77. Graceful Degradation
# हिंदी में: Graceful Degradation — किसी हिस्से के फ़ेल होने पर पूरा ऐप बंद करने की जगह, कम फ़ीचर्स के साथ ज़रूरी काम चालू रखना

---

## 🔵 Simple Definition (English)
**Graceful degradation** means designing a system so that when a **component fails or is overloaded**, the product keeps working in a **reduced but useful mode**, instead of failing completely. Non-essential features are **turned off, simplified, or served from cache/defaults**, while **core user journeys** (browse, order, pay) keep working.

## 🔵 सरल परिभाषा (Hindi)
Graceful degradation यानी किसी हिस्से के ख़राब होने पर भी ऐप चलता रहे — कम फ़ीचर्स के साथ।
जैसे recommendations न आएँ तो उनके बिना home screen दिखाओ, पर ऑर्डर और पेमेंट चलते रहें।

---

## 🔴 Problem it Solves
Modern apps depend on **dozens of services**: recommendations, reviews, offers, maps, search, analytics, chat, A/B testing. Statistically, **something is always partially broken**. If every dependency is treated as critical:
- Availability multiplies down (Topic 19): 20 dependencies at 99.9% → ~98% overall.
- A failing "offers banner" service makes the **whole home page fail**.

Graceful degradation separates **must-have** from **nice-to-have**, so failures of the latter are **invisible or minor** to users, protecting revenue and trust.

## 🔴 यह क्यों बना? (Hindi)
आज के ऐप दर्जनों services पर टिके हैं — recommendations, reviews, offers, maps, search। हर समय कोई न कोई थोड़ी ख़राब होती है।
सबको ज़रूरी मानो तो offers banner फ़ेल होने से पूरा home page गिर जाएगा। Graceful degradation ज़रूरी और "अच्छा हो तो ठीक" फ़ीचर्स अलग करता है, ताकि छोटी ख़राबी यूज़र को पता भी न चले।

---

## 🟢 How it Works — Step by Step

### Step 1: Classify features by criticality

```
Tier 0 (must work):     login, browse menu, add to cart, place order, pay, order tracking
Tier 1 (important):     search, ratings, ETA from maps, coupons
Tier 2 (nice-to-have):  recommendations, "people also ordered", banners, reviews text,
                        personalization, analytics events, chat widget, A/B experiments
Rule: Tier 0 must NOT synchronously depend on Tier 2.
```

### Step 2: Define a degraded behaviour for each dependency

```
┌──────────────────────┬─────────────────────────────────────────────────────┐
│ Dependency down       │ Degraded behaviour                                  │
├──────────────────────┼─────────────────────────────────────────────────────┤
│ Recommendations       │ Show popular items in city (precomputed) or hide    │
│ Search engine         │ Basic DB search / category browsing                 │
│ Maps ETA API          │ Estimate ETA from distance; show "30–40 min"        │
│ Reviews service       │ Show rating stars from cache, hide review text      │
│ Personalization       │ Generic home screen                                 │
│ Image CDN slow        │ Low-res placeholders / blurhash                     │
│ Payment gateway A     │ Route to gateway B; hide failing method (e.g. one   │
│                       │ bank's UPI) with message                            │
│ Analytics/logging     │ Drop or buffer events locally — never block request │
│ Write path DB down    │ Read-only mode: browse works, "ordering paused"     │
│ Entire region down    │ Static status page from CDN, failover region        │
└──────────────────────┴─────────────────────────────────────────────────────┘
```

### Step 3: Mechanisms

```
- Timeouts + circuit breakers + fallbacks on every non-critical call (Topics 73, 79)
- Parallel calls with Promise.allSettled → partial responses
- Cached/stale data (stale-while-revalidate, last-known-good)
- Feature flags / kill switches to turn features off instantly ("panic mode")
- Load shedding of low-priority traffic (Topic 78)
- Static fallbacks served by CDN (status page, cached home)
- Client-side resilience: show cached screens offline, skeletons, retry buttons
- Async instead of sync: queue emails/analytics, don't block on them
```

### Partial response design (API contract)

```json
{
  "restaurants": [ ... ],
  "recommendations": null,
  "offers": [],
  "degraded": ["recommendations", "offers"]
}
Client renders whatever is present; hides empty sections. Never crash on missing optional data.
```

### Degradation levels during a big event (pre-planned "brownout" switches)
```
Level 1: disable recommendations & personalization
Level 2: disable reviews, rich images; increase cache TTLs
Level 3: disable search suggestions, non-essential APIs; queue non-critical writes
Level 4: read-only / waiting room for checkout
Each level = feature flags flipped by on-call (or automatically by load metrics).
```

## 🟢 कैसे काम करता है? (Hindi)
1. फ़ीचर्स को श्रेणी में बाँटो: ज़रूरी (login, menu, ऑर्डर, पेमेंट), महत्वपूर्ण (search, ETA), अच्छा-हो-तो (recommendations, banners)।
2. हर dependency के लिए तय करो कि वो गिरे तो क्या दिखाना है — cache, default, अनुमान (ETA दूरी से), या छिपा दो।
3. ग़ैर-ज़रूरी कॉल्स पर timeout + circuit breaker + fallback; `Promise.allSettled` से आधा-अधूरा पर काम का जवाब।
4. Feature flags से "panic mode" — भारी समय में ग़ैर-ज़रूरी फ़ीचर्स एक click में बंद।
5. ऐप (client) भी तैयार रहे: ख़ाली section छिपाए, cache दिखाए, crash न हो।

---

## 🟡 Real World Example

**Netflix** — if the personalization service fails, the home screen falls back to a generic list of popular titles. If ratings fail, titles show without stars. Users can still play videos, which is the core journey. Netflix designs every page this way.

**Hotstar / JioCinema "panic mode"** — during IPL peaks, they have switches to turn off non-essential features (some personalization, recommendations, heavy API calls), so capacity is reserved for streaming and the scorecard.

**Amazon Prime Day** — non-critical widgets (some recommendations, "customers also bought") degrade or are served from cache under load, while search, cart and checkout keep working.

**UPI apps (PhonePe, GPay, Paytm)** — if a particular bank is down, the app shows "Bank X is facing issues, try another account" instead of failing all payments. That's degradation at bank granularity.

**Twitter "fail whale" (2008)** — the opposite: a single failure showed a full-page error. Twitter later invested heavily in isolation and partial rendering.

## 🟡 Real Example Hindi में
Netflix में personalization फ़ेल हो तो popular titles की सामान्य लिस्ट दिखती है, ratings फ़ेल हों तो बिना stars — पर वीडियो चलता रहता है।
Hotstar IPL के समय "panic mode" से ग़ैर-ज़रूरी फ़ीचर्स बंद कर देता है ताकि streaming चलती रहे। UPI ऐप्स बताते हैं "Bank X में दिक़्क़त है, दूसरा अकाउंट चुनें" — पूरा ऐप बंद नहीं होता।

---

## 🟠 My Stack Example

### Node.js — home API with partial response
```js
const withTimeout = (p, ms) => Promise.race([p, new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), ms))]);

app.get('/api/v1/home', authenticate, async (req, res) => {
  const [restaurants, recs, offers] = await Promise.allSettled([
    getNearbyRestaurants(req.query.lat, req.query.lng),               // Tier 0 — critical
    flags.enabled('recommendations') ? withTimeout(recoBreaker.fire(req.user.id), 300) : Promise.resolve(null),
    flags.enabled('offers') ? withTimeout(getOffers(req.user.id), 300) : Promise.resolve([]),
  ]);

  if (restaurants.status === 'rejected') {
    const cached = await redis.get(`home:fallback:${cityOf(req.query)}`);   // last known good
    if (!cached) return res.status(503).json({ error: 'TEMPORARILY_UNAVAILABLE' });
    return res.json({ ...JSON.parse(cached), degraded: ['live_restaurants'] });
  }

  const degraded = [];
  if (recs.status === 'rejected') degraded.push('recommendations');
  if (offers.status === 'rejected') degraded.push('offers');
  res.json({
    restaurants: restaurants.value,
    recommendations: recs.status === 'fulfilled' ? recs.value : await popularInCity(req.query),  // precomputed
    offers: offers.status === 'fulfilled' ? offers.value : [],
    degraded,
  });
});
```

### Feature flags / kill switches (simple Redis-backed)
```js
const flags = {
  cache: new Map(), loadedAt: 0,
  async refresh() { this.cache = new Map(Object.entries(await redis.hGetAll('flags'))); this.loadedAt = Date.now(); },
  enabled(name) { return this.cache.get(name) !== 'off'; },
};
setInterval(() => flags.refresh().catch(() => {}), 5000);   // keep last known flags if Redis down
// on-call: HSET flags recommendations off   → disabled across all servers within 5 s
// (LaunchDarkly / Unleash / GrowthBook / AWS AppConfig for managed flags)
```

### Read-only mode when the primary DB is unhealthy
```js
app.use((req, res, next) => {
  if (flags.enabled('read_only_mode') === false) return next();
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(req.method) && !req.path.startsWith('/auth'))
    return res.status(503).json({ error: 'ORDERING_PAUSED', message: 'We are fixing an issue. Browsing still works.' });
  next();
});
```

### FastAPI — graceful ETA
```python
async def eta(origin, dest):
    try:
        return {"eta_min": await asyncio.wait_for(maps_eta(origin, dest), timeout=0.5), "source": "maps"}
    except Exception:
        km = haversine(origin, dest)
        return {"eta_min": round(15 + km * 4), "source": "estimate"}    # degraded but useful
```

### React Native — render what you have, never crash
```tsx
function Home() {
  const { data, isError } = useQuery({ queryKey: ['home'], queryFn: getHome, staleTime: 60_000,
                                       placeholderData: (prev) => prev });          // keep old data
  if (!data && isError) return <OfflineHome cached={mmkv.getString('home_cache')} />;
  return (
    <ScrollView>
      {data?.offers?.length ? <OffersCarousel offers={data.offers} /> : null}
      <RestaurantList items={data?.restaurants ?? []} />
      {data?.recommendations ? <Recs items={data.recommendations} /> : null}
    </ScrollView>
  );
}
// Images: show blurhash/placeholder if CDN slow; analytics: buffer locally, send later
```

### Next.js — static fallback
```
- ISR/static pages keep serving last good HTML if the API is down (revalidation fails → old page stays)
- error.tsx boundaries per section → one widget crashing doesn't blank the page
- Status page on separate infra (e.g. Instatus/Statuspage) for full outages
```

---

## ⚫ Interview Questions + Answers

**Q1: What is graceful degradation?**
A1: Designing the system so that when dependencies fail or capacity is exceeded, it continues to provide core functionality with reduced features or quality, rather than failing entirely. Non-critical features are disabled, simplified or served from cache or defaults, and the key user journeys keep working.

**Q2: How would you apply graceful degradation to an e-commerce home page?**
A2: Classify the components. Product listing and cart are critical. Recommendations, banners, reviews and personalization are optional. Call optional services in parallel with tight timeouts and circuit breakers, and fall back to cached or popular items or hide the section. Return partial responses with a `degraded` list. Keep a cached "last good" home page per city as the fallback. Add feature flags to disable expensive widgets under load. Make the client render whatever sections are present.

**Q3: What techniques enable graceful degradation?**
A3: Dependency criticality classification, timeouts, circuit breakers with fallbacks, parallel calls with `allSettled` and partial responses, caching and stale-while-revalidate, last-known-good data, feature flags and kill switches, load shedding by priority, asynchronous processing for non-critical side effects, read-only modes, static or CDN fallbacks, and resilient clients (offline cache, placeholders, error boundaries).

**Q4: Difference between graceful degradation and fault tolerance?**
A4: Fault tolerance aims to keep full functionality despite failures, usually through redundancy (replicas, failover), so users notice nothing. Graceful degradation accepts reduced functionality when failures exceed what redundancy covers, or when redundancy is too expensive for non-critical features. In practice you use both: redundancy for critical paths, degradation for the rest.

**Q5: How do you test graceful degradation?**
A5: Chaos and fault-injection tests in staging and production (kill or slow down dependencies, inject latency and errors with tools like Gremlin, Chaos Mesh, Toxiproxy or Istio fault injection), and verify core flows still work and degraded sections behave as designed. Run game days with feature-flag "panic levels", load tests that push past capacity, and contract tests ensuring clients handle missing optional fields. Monitor degradation counters in production.

---

## 🔷 Trade-offs
✅ Advantages:
- Higher perceived availability; protects revenue-critical flows; better UX during incidents.

❌ Disadvantages:
- More code paths (fallbacks) to build and test; stale data risk.
- Hidden degradation can go unnoticed → must monitor/alert on degraded modes.
- Product decisions needed on what's "core".

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Graceful degradation | Reduced but working functionality | कम फ़ीचर्स के साथ चालू |
| Core journey | Most important user flow | सबसे ज़रूरी यूज़र रास्ता |
| Fallback | Alternative when dependency fails | विकल्प |
| Partial response | Response with some parts missing | आधा-अधूरा पर काम का जवाब |
| Kill switch | Flag to instantly disable feature | फ़ीचर तुरंत बंद करने का स्विच |
| Read-only mode | Only reads allowed | सिर्फ़ पढ़ने की अनुमति |
| Last-known-good | Most recent valid cached data | आख़िरी सही डेटा |
| Panic mode / brownout | Planned feature shedding | योजनाबद्ध फ़ीचर बंदी |

---

## ⚡ 3-Line Summary
**English:**
1. Graceful degradation keeps core journeys working when parts fail, by dropping or simplifying non-essential features.
2. Classify dependencies, add timeouts/breakers/fallbacks, return partial responses, use caches and kill switches.
3. Make clients resilient too, and test with chaos/fault injection; monitor degraded modes.

**Hindi:**
1. Graceful degradation = हिस्सा गिरे तो भी ज़रूरी काम चलते रहें, बाक़ी फ़ीचर्स बंद या सरल।
2. Dependencies को श्रेणी में बाँटो, timeout/breaker/fallback, आधा जवाब, cache और kill switch।
3. ऐप भी मज़बूत बनाओ, chaos testing करो, और degraded हालत पर नज़र रखो।

---

## ➡️ Next Topic Suggestion
**78. Load Shedding** — When traffic exceeds capacity, it's better to reject some requests quickly than to serve everyone slowly and crash. Next: load shedding strategies and request prioritization.
