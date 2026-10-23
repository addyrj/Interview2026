# 93a. BFF — Backend For Frontend ⭐
# हिंदी में: BFF — हर तरह के frontend (mobile ऐप, web, smart TV) के लिए उसका अपना छोटा backend, जो कई services से डेटा लाकर ठीक उस स्क्रीन के हिसाब से जवाब तैयार करता है

---

## 🔵 Simple Definition (English)
The **Backend For Frontend (BFF)** pattern creates a **dedicated backend layer per client type** (mobile BFF, web BFF, partner BFF), often owned by the **frontend team**. Each BFF **aggregates** calls to downstream microservices, **shapes** responses for its UI (screen-ready JSON), handles **client-specific concerns** (auth/session handling, pagination style, payload size, versioning for old app releases), and keeps generic services **UI-agnostic**.

## 🔵 सरल परिभाषा (Hindi)
BFF में हर frontend (mobile, web) का अपना backend होता है — वो कई microservices को एक साथ बुलाकर, ठीक उसी स्क्रीन के लिए तैयार JSON देता है।
इससे mobile को कम कॉल और छोटा डेटा मिलता है, web को अलग ज़रूरत का डेटा, और अंदर की services किसी एक UI से बँधती नहीं।

---

## 🔴 Problem it Solves
A single general-purpose API for all clients causes friction:
- **Mobile** on 4G needs **one call per screen** with **small payloads**; web dashboards want **rich data**; TV needs a different layout.
- The mobile home screen needs data from **6 services** → 6 round trips × 100 ms RTT = slow.
- Old **mobile app versions** (can't force update) need **old response shapes**; web always runs the latest.
- Backend teams get flooded with "add this field for iOS only" requests; generic services bloat with UI-specific hacks.
- Browser security: you want **tokens kept server-side** (HttpOnly session) rather than in JS.

The BFF gives each experience **its own tailored API**, owned by the team that builds the UI.

## 🔴 यह क्यों बना? (Hindi)
एक ही API सबके लिए हो तो दिक़्क़त: mobile को एक कॉल और छोटा डेटा चाहिए, web dashboard को ज़्यादा; home screen के लिए 6 services की 6 कॉल; पुराने mobile versions को पुराना format चाहिए।
Backend टीम पर "सिर्फ़ iOS के लिए यह field" जैसी माँगें; BFF हर frontend को उसकी अपनी तैयार API देता है, जिसे frontend टीम ही संभालती है।

---

## 🟢 How it Works — Step by Step

```
   📱 iOS/Android (RN)            🌐 Next.js Web             🤝 Partners
          │                            │                         │
   ┌──────▼──────┐             ┌───────▼───────┐          ┌──────▼──────┐
   │ Mobile BFF  │             │   Web BFF     │          │ Public API  │
   │ - 1 call per│             │ (Next.js      │          │ Gateway     │
   │   screen    │             │  server /     │          │ (keys,      │
   │ - small JSON│             │  route        │          │  quotas)    │
   │ - app-ver   │             │  handlers)    │          │             │
   │   compat    │             │ - SSR data    │          │             │
   └──┬───┬───┬──┘             └──┬────┬───┬───┘          └──┬──────┬───┘
      │   │   │   parallel calls  │    │   │                 │      │
      ▼   ▼   ▼                   ▼    ▼   ▼                 ▼      ▼
   [restaurants] [offers] [user] [orders] [reco] [cart] ... generic domain microservices
```

### Example: mobile home screen in ONE call

```
GET /mobile/v3/home?lat=19.07&lng=72.87          (BFF)
  ├─ parallel: restaurant-svc.nearby(lat,lng)     200 ms
  ├─ parallel: offer-svc.forUser(uid)             120 ms   (timeout 300 ms → optional)
  ├─ parallel: user-svc.profile(uid)               30 ms
  ├─ parallel: reco-svc.forUser(uid)              250 ms   (breaker + fallback)
  └─ parallel: order-svc.activeOrder(uid)          40 ms
  → merge + trim fields + format money/ETA strings for display
  → { header: {...}, activeOrderCard: {...}, offers: [...], sections: [...] }   ~15 KB
Total ≈ max(200, 300) + BFF overhead ≈ 320 ms instead of 5 sequential client round trips
```

### What belongs in a BFF
```
✓ Aggregation & orchestration of READ calls for a screen
✓ Response shaping: only needed fields, display-ready formats, image URLs sized for device
✓ Client-specific auth/session handling (web: HttpOnly cookies → tokens server-side)
✓ Version compatibility for old app releases (per X-App-Version)
✓ Feature flags / experiments for that client
✓ Caching per screen, graceful degradation of optional sections
✗ Core business rules (pricing, payments, inventory) → stay in domain services
✗ Shared logic copy-pasted across BFFs → push down into services or a shared library
```

### BFF vs API Gateway vs GraphQL
```
API Gateway  → generic edge: auth, rate limiting, routing (often in front of BFFs)
BFF          → client-specific composition layer (REST, often one per client type)
GraphQL      → one flexible schema; clients pick fields → can act as a "universal BFF"
               (Netflix/Airbnb use GraphQL federation as BFF layer)
Common combo: Gateway → BFF (REST or GraphQL) → domain microservices
```

### Ownership
```
"You build it, you run it": the frontend team owns its BFF → can ship screen changes
without waiting on backend teams. Backend teams own domain services & stable contracts.
```

## 🟢 कैसे काम करता है? (Hindi)
1. Mobile ऐप एक ही कॉल करता है: `GET /mobile/v3/home`।
2. BFF अंदर से एक साथ (parallel) 5 services बुलाता है — restaurants, offers, profile, recommendations, active order।
3. जवाब मिलाकर, सिर्फ़ ज़रूरी fields, दिखाने लायक format (₹, ETA) में छोटा JSON भेजता है; optional हिस्से timeout पर छोड़ देता है।
4. पुराने ऐप versions के लिए पुराना format भी यहीं संभालता है; web BFF (Next.js server) tokens को browser से दूर रखता है।
5. BFF में business नियम (pricing, payment) मत डालो — वो domain services में रहें; BFF frontend टीम की ज़िम्मेदारी है।

---

## 🟡 Real World Example

**SoundCloud** — where the BFF pattern was named (Phil Calçado, ~2015). They moved from one public API used by all clients to a separate BFF per client, which let mobile and web teams iterate independently.

**Netflix** — device-specific adapter layers (originally Groovy scripts written by UI teams on the API server, later GraphQL federation) shape responses for hundreds of TV and phone device types.

**Swiggy / Zomato** — mobile apps call screen-oriented endpoints ("home", "restaurant page", "cart") assembled by aggregation layers from many microservices, tuned for small payloads on Indian mobile networks and versioned per app release.

**Next.js apps everywhere** — Route Handlers and Server Components effectively act as a web BFF: the server fetches from internal APIs with service credentials and returns HTML or JSON shaped for the page.

## 🟡 Real Example Hindi में
SoundCloud ने BFF नाम दिया — हर client के लिए अलग backend, ताकि mobile और web टीमें आज़ादी से काम कर सकें।
Swiggy/Zomato ऐप "home", "restaurant page" जैसे screen-वाले endpoints बुलाते हैं, जो कई services से डेटा मिलाकर छोटा JSON देते हैं। Next.js का server हिस्सा अपने आप web BFF बन जाता है।

---

## 🟠 My Stack Example

### Mobile BFF in Node.js (Express/Fastify)
```js
const opt = (p, ms, fallback) => Promise.race([p, sleep(ms).then(() => fallback)]).catch(() => fallback);

app.get('/mobile/v3/home', authenticate, async (req, res) => {
  const { lat, lng } = req.query, uid = req.user.id;
  const [restaurants, offers, profile, recs, active] = await Promise.all([
    restaurantSvc.nearby({ lat, lng, limit: 20 }),                          // required
    opt(offerSvc.forUser(uid), 300, []),                                     // optional
    userSvc.profile(uid),
    opt(recoBreaker.fire(uid), 300, null),
    opt(orderSvc.active(uid), 200, null),
  ]);

  const appVersion = req.get('X-App-Version') ?? '0.0.0';
  res.set('Cache-Control', 'private, max-age=15').json({
    greeting: `Hi ${profile.firstName}`,
    activeOrder: active && { id: active.id, status: active.statusLabel, etaText: `${active.etaMin} min` },
    offers: offers.slice(0, 5).map((o) => ({ id: o.id, title: o.title, imageUrl: cdnImg(o.image, 600) })),
    sections: [
      ...(recs ? [{ type: 'carousel', title: 'For you', items: recs.slice(0, 10).map(card) }] : []),
      { type: semver.gte(appVersion, '4.10.0') ? 'grid' : 'list', title: 'Restaurants near you', items: restaurants.map(card) },
    ],
  });
});
const card = (r) => ({ id: r.id, name: r.name, rating: r.rating?.toFixed(1), eta: `${r.etaMin}-${r.etaMin + 10} min`,
                       priceForTwo: `₹${r.priceForTwo}`, imageUrl: cdnImg(r.image, 400), veg: r.isPureVeg });
```

### Web BFF with Next.js App Router (Server Component + route handler)
```tsx
// app/(shop)/page.tsx — runs on the server; tokens never reach the browser
import { cookies } from 'next/headers';
export default async function Home() {
  const session = await getSession(cookies());                         // HttpOnly cookie → server session
  const headers = { Authorization: `Bearer ${session.accessToken}` };
  const [restaurants, offers] = await Promise.all([
    fetch(`${INTERNAL_API}/restaurants?city=${session.city}`, { headers, next: { revalidate: 60 } }).then(r => r.json()),
    fetch(`${INTERNAL_API}/offers`, { headers, cache: 'no-store' }).then(r => r.json()).catch(() => []),
  ]);
  return <HomeView restaurants={restaurants} offers={offers} />;
}

// app/api/cart/route.ts — BFF endpoint for client-side interactions
export async function POST(req: Request) {
  const session = await getSession(cookies());
  const body = await req.json();
  const r = await fetch(`${INTERNAL_API}/carts/${session.userId}/items`, {
    method: 'POST', headers: { Authorization: `Bearer ${session.accessToken}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ itemId: body.itemId, qty: body.qty }),
  });
  return Response.json(await r.json(), { status: r.status });
}
```

### FastAPI as a BFF for an admin/partner portal
```python
@app.get("/partner/dashboard")
async def dashboard(user=Depends(current_partner)):
    stats, live, payouts = await asyncio.gather(
        stats_svc.today(user.restaurant_id),
        order_svc.live_orders(user.restaurant_id),
        payout_svc.upcoming(user.restaurant_id),
        return_exceptions=True)
    return {
        "todayRevenue": None if isinstance(stats, Exception) else f"₹{stats['revenue']:,}",
        "liveOrders": [] if isinstance(live, Exception) else [shape(o) for o in live],
        "nextPayout": None if isinstance(payouts, Exception) else payouts[0],
    }
```

### Shared typed contracts (monorepo)
```
apps/mobile  ─┐
apps/web     ─┼─ import types from packages/bff-contracts (zod schemas for each screen response)
apps/bff-mobile ┘  → mobile TS types generated from the same schema → no drift
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the BFF pattern and why use it?**
A1: Backend For Frontend: a dedicated server-side layer per client type (mobile, web, TV, partner) that aggregates and adapts data from downstream services for that client's screens. It reduces round trips and payload size (critical on mobile), isolates client-specific needs and versioning from generic services, lets frontend teams evolve their API independently, and can keep sensitive tokens server-side for web.

**Q2: How is a BFF different from an API gateway?**
A2: An API gateway is a generic, shared edge component handling cross-cutting concerns (TLS, auth validation, rate limiting, routing) for all clients. A BFF is client-specific application code that composes multiple service calls and shapes responses for particular UI screens. A typical setup is gateway, then BFF per client, then domain services. Some teams merge them for small systems.

**Q3: What logic should and shouldn't live in a BFF?**
A3: Should: aggregation of reads, response shaping and formatting, client-specific pagination, caching and degradation, session or token handling for that client, feature flags for that UI, and compatibility shims for old app versions. Shouldn't: core business rules (pricing, payments, inventory, authorization decisions on domain data), which belong in domain services so all clients behave consistently. Duplicated logic across BFFs should be pushed down into services.

**Q4: BFF vs GraphQL — when choose which?**
A4: GraphQL provides one flexible schema where clients choose fields, so it can serve many clients without separate BFFs, and works well with many teams via federation. But it adds complexity (resolvers, N+1, cost limits, caching). REST BFFs per client are simpler, very cacheable, and let each team design screen-specific endpoints, at the cost of more services to maintain. Many companies use GraphQL as the BFF layer. Smaller teams often prefer a REST BFF, or Next.js server components.

**Q5: What are the risks of BFFs?**
A5: Code duplication across BFFs. More deployable services to operate. BFFs becoming bloated with business logic. Fan-out latency and failures if aggregation isn't parallelized with timeouts and fallbacks. And inconsistent behaviour between clients. Mitigate with shared libraries, clear ownership rules, timeouts and circuit breakers, contract tests, and keeping domain rules in services.

---

## 🔷 Trade-offs
✅ Advantages:
- Optimal APIs per client (fewer calls, smaller payloads), frontend team autonomy, cleaner generic services, safer web auth.

❌ Disadvantages:
- More services to build/run; duplication risk; another hop; possible inconsistency across clients.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BFF | Backend dedicated to one frontend | एक frontend का अपना backend |
| Aggregation | Combining multiple service calls | कई कॉल्स को जोड़ना |
| Response shaping | Tailoring JSON for a screen | स्क्रीन के हिसाब से जवाब |
| Screen-oriented API | Endpoint per screen | हर स्क्रीन का endpoint |
| Fan-out | One request → many downstream calls | एक request से कई कॉल्स |
| Domain service | Generic business service | मूल business service |
| Federation | Combining GraphQL schemas | GraphQL schemas जोड़ना |
| Payload | Data size sent to client | भेजा गया डेटा |

---

## ⚡ 3-Line Summary
**English:**
1. BFF = a backend per client type (mobile/web/partner) that aggregates downstream services and shapes screen-ready responses.
2. Cuts round trips and payload (great for mobile), handles app-version compatibility and web session security; owned by frontend team.
3. Keep business rules in domain services; parallelize calls with timeouts/fallbacks; GraphQL can act as a universal BFF.

**Hindi:**
1. BFF = हर client (mobile/web) का अपना backend, जो कई services से डेटा लाकर स्क्रीन के लिए तैयार जवाब देता है।
2. कम कॉल्स, छोटा डेटा, पुराने ऐप versions का ध्यान, web पर tokens सुरक्षित; frontend टीम की ज़िम्मेदारी।
3. Business नियम domain services में; parallel कॉल्स timeout/fallback के साथ; GraphQL भी BFF बन सकता है।

---

## ➡️ Next Topic Suggestion
**94. Service Mesh (Istio)** — The gateway and BFF handle traffic entering the system. Next: how a service mesh manages service-to-service traffic (mTLS, retries, timeouts, traffic splitting, observability) without changing application code.
