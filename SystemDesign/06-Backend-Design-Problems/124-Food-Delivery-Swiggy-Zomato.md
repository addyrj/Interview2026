# 124. Food Delivery (Swiggy / Zomato)
# हिंदी में: Food Delivery Platform — पास के रेस्टोरेंट ढूँढना, मेन्यू, cart, payment, रेस्टोरेंट को ऑर्डर, डिलीवरी पार्टनर assign करना, लाइव ट्रैकिंग और ETA — तीन ऐप्स (ग्राहक, रेस्टोरेंट, डिलीवरी) एक backend पर

---

## 🔵 Simple Definition (English)
Design a **three-sided marketplace** like **Swiggy / Zomato / DoorDash**: **customers** discover restaurants (serviceable to their location), browse menus, order and pay; **restaurants** accept and prepare orders; **delivery partners (DEs)** are **assigned** to pick up and deliver; everyone sees **real-time tracking and ETAs**. Core challenges: **geo-based discovery/serviceability**, **order lifecycle**, **dispatch/assignment optimization**, **live location at scale**, **ETA prediction**, and **dinner-peak spikes**.

## 🔵 सरल परिभाषा (Hindi)
Swiggy/Zomato तीन लोगों का बाज़ार है: ग्राहक (पास के रेस्टोरेंट, मेन्यू, ऑर्डर, पेमेंट), रेस्टोरेंट (ऑर्डर स्वीकार करके बनाना), और डिलीवरी पार्टनर (assign होकर उठाना और पहुँचाना)।
मुख्य चुनौतियाँ: लोकेशन के हिसाब से रेस्टोरेंट, ऑर्डर का पूरा flow, सही डिलीवरी पार्टनर चुनना, लाखों की लाइव लोकेशन, सही ETA, और रात के खाने के समय की भीड़।

---

## 🔴 Problem it Solves
- "Which restaurants can deliver to me **right now**?" depends on distance, delivery zones, restaurant open status, rider availability and rain/surge.
- Orders involve **three parties and payments**; failures at any step need compensation (refunds).
- Assigning the **right rider** (nearby, free or about to be free, going in the right direction, batching two orders) affects cost and delivery time.
- **Hundreds of thousands of riders** sending GPS every few seconds.
- **Dinner peaks** (7–10 PM), weekend and festive spikes, IPL nights, rain.

## 🔴 यह क्यों बना? (Hindi)
"अभी मेरे पते पर कौन-से रेस्टोरेंट डिलीवर करेंगे?" — दूरी, zone, रेस्टोरेंट खुला है या नहीं, riders उपलब्ध हैं या नहीं, बारिश — सब पर निर्भर। तीन पक्ष और पेमेंट, कहीं भी गड़बड़ी तो refund; सही rider चुनना (पास, ख़ाली, उसी दिशा में, दो ऑर्डर साथ); लाखों riders का GPS; और रात 7-10 बजे की भीड़।

---

## 🟢 How it Works — Step by Step (Interview Design)

### 1. Requirements

```
Customer: search/browse restaurants by location (filters, ratings, cuisine, ETA, offers), menu, cart,
          checkout (coupons, payment), live tracking, ETA, cancel/refund, rate & review, support chat
Restaurant: receive orders (tablet/app), accept/reject, mark ready, manage menu/availability/hours
Delivery partner: go online/offline, receive assignment offers, navigate, pickup/deliver confirmations
              (OTP), earnings
Non-functional: listing < 300 ms; order placement highly reliable; assignment within ~30 s;
                location updates every 3–5 s; ETA accuracy; handle 3–5× dinner peaks; city-level isolation
```

### 2. Estimation (large Indian city platform)

```
Orders/day: 2M nationwide → dinner peak hour ≈ 20% → 400k/hour ≈ 110 orders/s (peak minute 200/s)
Active riders at peak: 200k × 1 location / 4 s = 50k location updates/s
Customers tracking: 300k concurrent orders → updates fanned out to customers every few seconds
Listing requests: 10M sessions × 5 = 50M/day, peak ~5k RPS (cacheable per geo-cell)
```

### 3. Services

```
┌────────────────────┬───────────────────────────────────────────────────────────────┐
│ Service            │ Responsibility                                                │
├────────────────────┼───────────────────────────────────────────────────────────────┤
│ Discovery/Listing  │ restaurants serviceable to a location, ranked (ETA, rating, ads)│
│ Search             │ dishes/restaurants text search (Elasticsearch + geo)           │
│ Catalog/Menu       │ menus, items, prices, availability (restaurant-managed)        │
│ Serviceability     │ zones/polygons, distance, rider supply, surge/rain multipliers │
│ Cart & Pricing     │ cart, fees, taxes, coupons/offers                              │
│ Order (orchestrator)│ order state machine, saga across payment/restaurant/dispatch  │
│ Payment            │ (Topic 119)                                                    │
│ Restaurant gateway │ push orders to restaurant devices/POS, accept/reject, prep time│
│ Dispatch/Assignment│ match orders to riders (batching, optimization)                │
│ Location           │ ingest rider GPS, latest positions (geo index), history        │
│ ETA                │ ML predictions: prep time + pickup travel + drop travel        │
│ Tracking           │ push live location/status to customer (WebSocket/SSE)          │
│ Notification       │ (Topic 114)                                                    │
└────────────────────┴───────────────────────────────────────────────────────────────┘
```

### 4. Order lifecycle (state machine + events)

```
CREATED → PAYMENT_PENDING → PLACED → RESTAURANT_ACCEPTED → (rider) ASSIGNED → RIDER_AT_RESTAURANT
       → PICKED_UP → ARRIVED → DELIVERED
  side exits: PAYMENT_FAILED, RESTAURANT_REJECTED/TIMEOUT → CANCELLED + REFUND, RIDER reassignment
Each transition → event on Kafka (order-events) → tracking, notifications, ETA, analytics, payouts
Orchestrated saga (Topic 70) with timeouts: restaurant must accept within 3 min else auto-cancel/refund
```

### 5. Discovery & serviceability (geo)

```
Divide the city into cells (H3 hexagons / geohash). For a customer location:
  1. cell = H3(lat, lng, res 8)
  2. candidate restaurants = those serving that cell (precomputed per cell → cache) & open now
  3. filter by delivery radius/zone polygons, rider availability in area ("not serviceable" if no riders)
  4. ETA estimate per restaurant (prep + travel) → rank by relevance, ETA, rating, offers, ads
  5. cache the listing per (cell, time-slot) for ~30–60 s → most requests hit cache
Search: Elasticsearch with geo_distance filter + text (Topic 53a)
```

### 6. Dispatch / assignment (the hardest problem)

```
Inputs: order (restaurant location, food ready time estimate, drop location), riders (location, status,
        current task, direction, rating, vehicle), constraints (max batch size, max detour)
Naive: nearest free rider (GEOSEARCH radius) → greedy, poor globally
Better ⭐: batch matching every few seconds per zone:
   build bipartite graph orders × candidate riders (within X km) with cost =
     pickup ETA + wait at restaurant + delay to existing orders (batching) − ...
   solve assignment (Hungarian / min-cost matching / heuristics) → send offers
Key ideas: assign rider so arrival ≈ food ready time (avoid waiting); batch 2 orders from same
  restaurant/nearby; consider riders about to finish; re-assign if rider rejects/timeouts (30 s)
Supply-demand: surge fees, incentives, "rain mode" (expand ETAs, limit serviceability)
```

### 7. Location & tracking

```
Rider app → location every 3–5 s (batched, HTTP/MQTT) → Location svc
  → Redis GEO (latest positions per city) for dispatch queries
  → Kafka (history) → Cassandra/S3 (for disputes, analytics, ETA model training)
Customer tracking: order:{id} channel → WebSocket/SSE push of rider position (throttled, every 3–5 s)
  + client-side marker animation; background → milestone pushes only (Topic 97)
```

### 8. ETA
```
ETA = restaurant prep time (ML: item types, current load, historical) + rider-to-restaurant travel
      + restaurant-to-customer travel (road network, traffic, weather, time of day)
Shown at listing (estimate), checkout (promise), and live (updated with rider position)
Models trained on historical deliveries; online features from current load
```

### 9. Scaling & resilience
```
- City-level sharding/cells: each city's dispatch & location independent (blast radius)
- Peak: pre-scale listing & order services; cache listings; queue non-critical work
- Graceful degradation: turn off recommendations, reduce tracking frequency, simpler ranking
- Restaurant device offline → IVR call / SMS fallback; auto-cancel with refund on timeout
- Idempotency for order placement & payments; outbox for events
```

## 🟢 कैसे काम करता है? (Hindi)
1. ग्राहक की लोकेशन → H3 cell → उस cell में डिलीवर करने वाले खुले रेस्टोरेंट (पहले से गिने, cache में) → riders की उपलब्धता, ETA, rating से क्रम।
2. ऑर्डर state machine: बना → पेमेंट → रेस्टोरेंट स्वीकार (3 मिनट में, नहीं तो refund) → rider assign → उठाया → पहुँचाया; हर बदलाव Kafka event।
3. Dispatch: हर कुछ सेकंड में zone के ऑर्डर्स और पास के riders का मिलान — rider ऐसे समय पहुँचे जब खाना तैयार हो, पास के दो ऑर्डर साथ, मना करे तो दूसरा rider।
4. Rider हर 3-5 सेकंड लोकेशन भेजता है → Redis GEO (dispatch के लिए) + Kafka (इतिहास); ग्राहक को WebSocket से लाइव, marker smooth।
5. ETA = बनाने का समय + rider का रेस्टोरेंट तक + ग्राहक तक (ML); शहर-वार अलग सिस्टम, peak पर pre-scale, बारिश में "rain mode"।

---

## 🟡 Real World Example

**Swiggy** — has written about its delivery assignment system (batch matching with optimization), serviceability engines, the use of geospatial indexing, Kafka-based event pipelines for order lifecycle and location, and ML-based ETA and prep-time prediction. "Rain mode" adjusts serviceability and ETAs during bad weather.

**Zomato** — handles dinner and New Year's Eve peaks (record orders per minute) with pre-scaling, and runs real-time order tracking and ML-based ETAs. Zomato's engineering blog discusses its migrations to AWS services and Kafka.

**DoorDash** — its "Dasher dispatch" uses batch matching as an optimization problem with ML predictions of prep time and travel, and the company moved to cell-based architecture for reliability.

**Uber Eats** — reuses Uber's dispatch platform, H3 geospatial indexing and ETA services.

## 🟡 Real Example Hindi में
Swiggy ने अपने delivery assignment (batch matching), serviceability, geo indexing, Kafka events और ML वाले ETA के बारे में लिखा है; बारिश में "rain mode" ETA और दूरी बदल देता है।
Zomato New Year's Eve जैसी भीड़ pre-scaling से संभालता है। DoorDash dispatch को optimization समस्या की तरह हल करता है; Uber Eats Uber का dispatch और H3 grid इस्तेमाल करता है।

---

## 🟠 My Stack Example

### Serviceable restaurants by H3 cell (Node + Redis cache)
```js
import { latLngToCell, gridDisk } from 'h3-js';

app.get('/api/v1/restaurants', authenticateOptional, async (req, res) => {
  const { lat, lng } = req.query;
  const cell = latLngToCell(Number(lat), Number(lng), 8);
  const key = `listing:${cell}:${slot(Date.now())}`;                      // 1-min slots
  let list = await redis.get(key).then((v) => v && JSON.parse(v));
  if (!list) {
    const candidates = await db.query(
      `SELECT r.id, r.name, r.rating, r.lat, r.lng, r.avg_prep_min FROM restaurant_cells rc JOIN restaurants r ON r.id = rc.restaurant_id
       WHERE rc.cell = $1 AND r.is_open = true`, [cell]);
    const supply = await riderSupply(gridDisk(cell, 2));                   // riders nearby
    list = candidates.rows
      .map((r) => ({ ...r, etaMin: estimateEta(r, { lat, lng }, supply) }))
      .filter((r) => r.etaMin <= 60 && supply > 0)
      .sort((a, b) => rankScore(b) - rankScore(a));
    await redis.set(key, JSON.stringify(list), { EX: 60 });
  }
  res.json({ restaurants: list.slice(0, 50) });
});
```

### Rider location ingest + geo index
```js
app.post('/api/v1/rider/location', authenticateRider, async (req, res) => {
  const { lat, lng, ts, heading, speed } = req.body;
  const city = req.rider.city;
  await redis.multi()
    .geoAdd(`riders:${city}`, { longitude: lng, latitude: lat, member: String(req.rider.id) })
    .hSet(`rider:${req.rider.id}`, { lat, lng, ts, heading, speed, status: req.rider.status })
    .exec();
  await producer.send({ topic: 'rider-locations', messages: [{ key: String(req.rider.id), value: JSON.stringify({ lat, lng, ts }) }] });
  const order = await redis.get(`rider:${req.rider.id}:order`);
  if (order) emitter.to(`order:${order}`).emit('rider:location', { lat, lng, ts });
  res.sendStatus(204);
});
```

### Simple batch dispatcher (every 5 s per zone) — greedy cost matching
```js
async function dispatchTick(zone) {
  const orders = await pendingOrders(zone);                    // RESTAURANT_ACCEPTED, unassigned
  const pairs = [];
  for (const o of orders) {
    const near = await redis.geoSearch(`riders:${zone.city}`, { longitude: o.rLng, latitude: o.rLat },
                                       { radius: 4, unit: 'km' }, { SORT: 'ASC', COUNT: 15 });
    for (const riderId of near) {
      const r = await riderState(riderId);
      if (!r.available && !r.canBatchWith(o)) continue;
      const arrive = travelMin(r, o);                          // map/ETA service
      const cost = Math.abs(arrive - o.minutesUntilReady) + (r.canBatchWith(o) ? r.batchDetour(o) : 0);
      pairs.push({ o, r, cost });
    }
  }
  pairs.sort((a, b) => a.cost - b.cost);                       // (production: min-cost matching solver)
  const usedO = new Set(), usedR = new Set();
  for (const p of pairs) {
    if (usedO.has(p.o.id) || usedR.has(p.r.id)) continue;
    usedO.add(p.o.id); usedR.add(p.r.id);
    await offerToRider(p.r.id, p.o.id, { expiresInSec: 30 });  // push offer; on reject/timeout → back to pool
  }
}
```

### Order state machine transition (guarded)
```sql
UPDATE orders SET status = 'PICKED_UP', picked_up_at = now()
WHERE id = $1 AND rider_id = $2 AND status = 'RIDER_AT_RESTAURANT'
RETURNING id;      -- 0 rows → invalid transition / not this rider's order
```

### React Native apps (three apps, one backend)
```
Customer app: listing (cached per cell), cart, Razorpay checkout, tracking screen (WebSocket + map animation)
Restaurant app: order notifications (high-priority push + in-app sound), accept with prep time, mark ready
Rider app: background location (foreground service on Android), offer screen with 30 s timer,
           pickup/drop OTP verification, offline queue for events in weak network areas
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you show restaurants that can deliver to a user right now?**
A1: Index the city with geospatial cells (H3 or geohash), and precompute which restaurants serve each cell, based on delivery radius, zone polygons and business rules. At request time, compute the user's cell, fetch candidate restaurants, filter by open status, current rider supply and surge or rain restrictions, estimate ETAs, and rank by relevance, ETA, rating, offers and ads. Cache the results per cell and time slot for 30–60 seconds, since many nearby users share the same answer.

**Q2: How would you assign delivery partners to orders?**
A2: Run a dispatcher per zone every few seconds that considers all unassigned orders and nearby candidate riders (geo queries on the latest positions). Compute costs based on predicted rider arrival vs food-ready time, travel distance, batching opportunities with orders the rider already carries, fairness and rider acceptance probability. Solve a matching or optimization problem (min-cost bipartite matching or heuristics), send time-limited offers, and re-dispatch on rejection or timeout. Greedy nearest-rider assignment is simpler but globally worse.

**Q3: How do you handle real-time tracking for hundreds of thousands of active orders?**
A3: Rider apps send batched GPS updates every 3–5 seconds to a location service, which updates the latest position in Redis GEO (for dispatch) and appends to Kafka (history, analytics, ETA training). For each active order, the update is published to an order channel, and WebSocket or SSE gateways push it to the customer app, which animates the marker smoothly. When the customer app is in the background, only milestone push notifications are sent. Updates are throttled and coalesced under load.

**Q4: What happens if the restaurant doesn't accept an order?**
A4: The order saga has a timeout. The restaurant is notified via its device app or POS (high-priority push, sound alerts), with escalation via automated IVR call or SMS if unacknowledged. If there's still no acceptance within the SLA (around 3–5 minutes), or the restaurant rejects, the order is auto-cancelled: the payment is refunded or voided (compensation), the customer is notified with alternatives, and restaurant reliability metrics are updated (which affects ranking). All transitions are idempotent and evented.

**Q5: How do you prepare for the dinner peak and events like IPL finals or New Year's Eve?**
A5: Capacity planning and pre-scaling of the listing, order, dispatch and tracking services. Aggressive caching of listings per cell, city-level isolation so one city's issues don't spread, and queueing non-critical work. Graceful degradation switches (disable recommendations, lower tracking frequency, simplify ranking), rider supply incentives and surge pricing, and serviceability adjustments (rain mode, limiting radius). Payment-provider failover, war-room monitoring of orders per minute per city, and load tests and game days beforehand.

---

## 🔷 Trade-offs
✅ Batch matching: better global assignments — ❌ few seconds of delay, solver complexity.
✅ Cached listings per cell: cheap & fast — ❌ slightly stale availability/ETA (revalidate at checkout).
✅ Frequent location updates: smooth tracking — ❌ battery/data/server cost (adaptive frequency).
✅ City cells: isolation & scale — ❌ cross-city features need care.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Three-sided marketplace | Customers, restaurants, riders | तीन पक्षों का बाज़ार |
| Serviceability | Can we deliver to this location now | क्या अभी डिलीवरी संभव है |
| H3 / geohash | Geospatial grid cells | नक्शे के खाने |
| Dispatch / assignment | Matching orders to riders | ऑर्डर और rider का मिलान |
| Batching | One rider carries multiple orders | एक rider कई ऑर्डर |
| ETA | Estimated time of arrival | पहुँचने का अनुमानित समय |
| Prep time | Restaurant cooking time | खाना बनने का समय |
| Order state machine | Allowed status transitions | ऑर्डर की स्थितियाँ |
| Surge / rain mode | Demand-supply adjustments | माँग-आपूर्ति के हिसाब से बदलाव |
| Geo index | Index for location queries | लोकेशन खोजने का index |

---

## ⚡ 3-Line Summary
**English:**
1. Geo discovery via H3 cells + serviceability (zones, open status, rider supply) + ETA ranking, cached per cell.
2. Order = saga/state machine across payment, restaurant acceptance (timeouts), dispatch, pickup, delivery; all transitions evented on Kafka.
3. Dispatch via periodic batch matching on Redis GEO rider positions; live tracking via location pipeline + WebSocket; ML ETAs; city isolation and peak readiness.

**Hindi:**
1. H3 cells से पास के रेस्टोरेंट + डिलीवरी संभव है या नहीं + ETA ranking, cell-वार cache।
2. ऑर्डर = state machine/saga: पेमेंट → रेस्टोरेंट (timeout) → rider → pickup → delivery; हर बदलाव Kafka में।
3. Redis GEO पर batch matching से rider; location pipeline + WebSocket से ट्रैकिंग; ML ETA; शहर-वार अलगाव।

---

## ➡️ Next Topic Suggestion
**125. Ride Sharing (Uber/Ola)** — Similar geo plus real-time matching, but with a moving pickup point, surge pricing, trip state and driver supply. Next: the full Uber/Ola design.
