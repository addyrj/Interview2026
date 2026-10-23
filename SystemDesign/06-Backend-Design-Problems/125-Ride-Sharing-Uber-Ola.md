# 125. Ride Sharing (Uber / Ola / Rapido)
# हिंदी में: Ride Sharing — यात्री को पास का ड्राइवर तुरंत ढूँढकर जोड़ना (matching), किराया तय करना (surge के साथ), सफ़र की लाइव ट्रैकिंग, और सफ़र ख़त्म होने पर पेमेंट — करोड़ों rides रोज़

---

## 🔵 Simple Definition (English)
Design a ride-hailing system like **Uber / Ola / Rapido / Lyft**: a **rider** requests a trip (pickup → drop); the system **estimates fare and ETA**, **finds and dispatches a nearby driver** within seconds, both apps see **live locations**, the **trip state** is tracked (accepted → arriving → on trip → completed), the **fare** is computed (distance, time, **surge**), **payment** is collected, and **ratings/safety** features run. Core challenges: **geospatial indexing of moving drivers**, **low-latency matching**, **dynamic pricing**, **real-time location streams**, and **consistency of trip state**.

## 🔵 सरल परिभाषा (Hindi)
Uber/Ola जैसा सिस्टम: यात्री pickup और drop डालता है → किराया और ETA दिखता है → कुछ सेकंड में पास का ड्राइवर मिलता है → दोनों को एक-दूसरे की लाइव लोकेशन → सफ़र की स्थिति (आ रहा है → सफ़र में → ख़त्म) → किराया (surge के साथ) → पेमेंट और rating।
मुख्य चुनौती: लगातार चलते ड्राइवरों की लोकेशन का index, सेकंडों में matching, बदलता किराया, और trip की स्थिति एकदम सही।

---

## 🔴 Problem it Solves
- **Millions of drivers moving constantly**: their locations change every few seconds, and "find nearest available drivers" must answer in milliseconds.
- **Matching quality**: nearest by straight line ≠ fastest by road; acceptance rates; fairness to drivers.
- **Supply-demand imbalance**: rain, office hours and events cause demand spikes, so **surge pricing** balances it.
- **Trip correctness**: one driver must never get two simultaneous trips; a rider must not be charged twice; disputes need GPS history.
- **Safety & reliability**: SOS, trip sharing, route deviation detection, and working on flaky mobile networks.

## 🔴 यह क्यों बना? (Hindi)
लाखों ड्राइवर लगातार चल रहे हैं — हर कुछ सेकंड में लोकेशन बदलती है, और "सबसे पास के ख़ाली ड्राइवर" milliseconds में चाहिए। सीधी दूरी ≠ सड़क से तेज़ रास्ता; बारिश या ऑफ़िस टाइम में माँग ज़्यादा → surge; एक ड्राइवर को एक साथ दो trip नहीं; दो बार पैसा नहीं; और सुरक्षा (SOS, रास्ता बदलने पर alert)।

---

## 🟢 How it Works — Step by Step (Interview Design)

### 1. Requirements

```
Rider: set pickup/drop, see fare estimate & ETA, request ride, see driver approaching (live), cancel,
       trip tracking, pay (UPI/card/cash/wallet), rate, SOS/share trip
Driver: go online/offline, receive ride offers (accept within ~15 s), navigate, start/end trip (OTP),
        earnings
Non-functional: match within ~5–15 s; location updates every 3–5 s; strong consistency for trip
                state & driver assignment; highly available; city-level isolation; peak handling
```

### 2. Estimation

```
Active drivers at peak (one large country): 1M online × 1 update / 4 s = 250k location updates/s
Ride requests: 20M trips/day ≈ 230/s avg, peak ~1,000–2,000/s
Each request → nearby-driver query (geo index) + ETA computations for ~10–20 candidates
Location history: 250k/s × 100 B ≈ 25 MB/s ≈ 2 TB/day (Kafka → Cassandra/S3, retention for disputes)
```

### 3. Architecture

```
 Rider app ─┐                                                            ┌─ Driver app
            │ HTTPS + WebSocket                         HTTPS/MQTT + WS  │ (location every 4 s)
            ▼                                                            ▼
     ┌──────────────┐                                         ┌───────────────────┐
     │ API Gateway  │                                         │ Location ingest   │
     └──────┬───────┘                                         └─────────┬─────────┘
            ▼                                                           │ update geo index
  ┌─────────────────┐  fare quote   ┌───────────────┐                    ▼
  │ Trip service    │◄────────────►│ Pricing/Surge │        ┌───────────────────────┐
  │ (state machine) │               └───────────────┘        │ Geo index (in-memory, │
  └──┬───────┬──────┘                                        │ H3 cells → drivers)   │
     │       │ request match                                 └──────────▲────────────┘
     │       ▼                                                          │ nearby query
     │   ┌──────────────────┐  candidates + ETAs (routing/maps svc) ────┘
     │   │ Dispatch/Matching│──► offer to driver (push via WS) ──► accept / timeout → next
     │   └──────────────────┘
     ├──► Payment svc (on trip end) ──► PSP / wallet / cash ledger
     ├──► Kafka trip-events ──► notifications, ETA training, fraud/safety, analytics, receipts
     └──► Trip DB (sharded by city/trip id; strongly consistent)
 Location stream ──► Kafka ──► history store (disputes, route replay), ETA/supply analytics
```

### 4. Geospatial index for moving drivers

```
Problem: 1M points moving every few seconds; query "available drivers within 2 km of P" in ms.
Approach: H3 hexagonal cells (Uber's H3) or geohash / S2 cells
  driver update → compute cell(res 8–9) → move driver id between cell sets (in-memory, sharded by city)
  query → cell of pickup + k-ring neighbours (gridDisk) → candidate drivers → filter by status/vehicle
Alternatives: Redis GEO (GEOADD/GEOSEARCH, sorted set geohash) — great up to large scale per city;
              QuadTree (in-memory, rebuilt/updated periodically); PostGIS for non-hot queries
Why not SQL WHERE distance < 2km on every request? Too slow at this update + query rate.
```

### 5. Matching / dispatch

```
1. Rider requests → Trip CREATED (idempotency key) → dispatch
2. Candidates: available drivers in nearby cells, right vehicle type, not recently rejected this rider
3. Rank by ROAD ETA to pickup (routing service, cached graph), driver rating/acceptance, heading,
   fairness (idle time); optionally batch-optimize across requests in a zone every 1–2 s
4. Offer to best driver (WebSocket/push, 15 s timeout) → ACCEPT → atomic assignment:
     driver status AVAILABLE → ON_TRIP only if still available (compare-and-set / lock)
     trip ACCEPTED with driver id
   REJECT/TIMEOUT → next candidate (or offer to several sequentially, never assign twice)
5. No driver within N tries → "No cabs available" / expand radius / surge prompt
```

### 6. Trip state machine (strong consistency)

```
CREATED → MATCHING → DRIVER_ASSIGNED → DRIVER_ARRIVING → DRIVER_ARRIVED → ON_TRIP (OTP verified)
        → COMPLETED → PAID
  exits: CANCELLED_BY_RIDER (fee rules), CANCELLED_BY_DRIVER (re-dispatch), NO_DRIVERS
Transitions are conditional updates (WHERE status = expected) in the Trip DB (single writer per trip),
each emitting an event (outbox → Kafka). Driver availability updated atomically with assignment.
```

### 7. Pricing & surge

```
Fare estimate = base + per_km × route_km + per_min × route_min (+ tolls, taxes) × surge multiplier
Surge: per H3 cell (or zone), computed every ~1–2 min from demand (requests, app opens) vs supply
       (available drivers), smoothed & capped; shown to rider and locked for the quote (quote id, TTL)
Final fare: computed from actual GPS route/time at trip end (map-matched), compared with upfront price
            rules; fraud checks (GPS spoofing)
```

### 8. Location, tracking, safety
```
Driver app sends GPS every ~4 s (more on trip, less when idle) → location service → geo index + Kafka
Rider sees driver approaching via WebSocket (throttled) + interpolation; driver sees rider pickup pin
On-trip: route deviation detection (stream processing), SOS button → safety team + emergency contacts,
         trip sharing link, call masking (proxy phone numbers)
```

### 9. Scale & resilience
```
City-level partitioning: geo index, dispatch, surge per city (Uber's "regions/cells")
Driver app resilience: queue events offline, idempotent "trip end" (no double end/charge)
Multi-AZ, failover; degrade gracefully (simpler ETAs if routing service slow)
Payment after trip: async with retries; cash trips → driver wallet ledger
```

## 🟢 कैसे काम करता है? (Hindi)
1. ड्राइवर हर ~4 सेकंड लोकेशन भेजता है → H3 cell में उसकी id रखी जाती है (in-memory, शहर-वार) + Kafka में इतिहास।
2. यात्री request करता है → pickup के cell और आस-पास के cells से ख़ाली ड्राइवर → सड़क के रास्ते का ETA → सबसे सही ड्राइवर को offer (15 सेकंड)।
3. ड्राइवर accept करे तो atomic तरीके से assign — ड्राइवर अब भी ख़ाली हो तभी; मना/timeout → अगला ड्राइवर।
4. Trip state machine (assigned → arriving → OTP → on trip → completed → paid), हर बदलाव conditional update + event।
5. किराया = base + km + मिनट × surge (हर cell में माँग/ड्राइवर के अनुपात से); सफ़र के बाद असली रास्ते से final किराया, पेमेंट, safety (SOS, रास्ता बदलने पर alert)।

---

## 🟡 Real World Example

**Uber** — created H3 (an open-source hexagonal geospatial index) for supply/demand, surge and dispatch. It uses Kafka at massive scale for location and trip events, and **Ringpop** (consistent hashing with gossip) to shard dispatch state across nodes. Uber's "DISCO" dispatch matches riders and drivers with road ETAs, and "Cadence/Temporal" workflows orchestrate trips and payments.

**Ola / Rapido** — operate in Indian cities with bike taxis and autos, cash payments and call masking, using geo indexing (Redis or in-memory grids) and surge pricing. Rapido handles high-density bike-taxi dispatch.

**Lyft** — wrote about its dispatch evolution from greedy matching to optimization-based "Global Dispatch".

**Grab (Southeast Asia)** — runs a super-app with rides, food and payments, using similar geo services and city-level cells.

## 🟡 Real Example Hindi में
Uber ने H3 (षट्कोणीय grid) बनाया जो surge और dispatch में इस्तेमाल होता है; Kafka से लोकेशन events, Ringpop से dispatch को nodes में बाँटना, और Cadence/Temporal से trip व payment flows।
Ola/Rapido भारतीय शहरों में bike taxi, auto, cash payment और call masking के साथ इसी तरह चलते हैं। Lyft greedy matching से optimization वाले "Global Dispatch" पर गया।

---

## 🟠 My Stack Example

### Driver location → H3 cell sets (Node + Redis, sharded by city)
```js
import { latLngToCell, gridDisk } from 'h3-js';
const RES = 8;                                                         // ~0.7 km² hexagons

app.post('/api/v1/driver/location', authenticateDriver, async (req, res) => {
  const { lat, lng, heading, ts } = req.body;
  const d = req.driver, city = d.city;
  const cell = latLngToCell(lat, lng, RES);
  const prev = await redis.hGet(`driver:${d.id}`, 'cell');
  const pipe = redis.multi()
    .hSet(`driver:${d.id}`, { lat, lng, heading, ts, cell })
    .expire(`driver:${d.id}`, 60);                                     // stale drivers disappear
  if (prev !== cell) {
    if (prev) pipe.sRem(`cell:${city}:${prev}:available`, String(d.id));
    if (d.status === 'AVAILABLE') pipe.sAdd(`cell:${city}:${cell}:available`, String(d.id));
  }
  await pipe.exec();
  await producer.send({ topic: 'driver-locations', messages: [{ key: String(d.id), value: JSON.stringify({ lat, lng, ts }) }] });
  res.sendStatus(204);
});

async function candidateDrivers(city, lat, lng, k = 2) {
  const cells = gridDisk(latLngToCell(lat, lng, RES), k);             // pickup cell + 2 rings
  const ids = (await Promise.all(cells.map((c) => redis.sMembers(`cell:${city}:${c}:available`)))).flat();
  return ids.slice(0, 50);
}
```

### Atomic assignment (no double booking) — Postgres
```js
async function acceptOffer(tripId, driverId) {
  return withTx(pool, async (tx) => {
    const drv = await tx.query("UPDATE drivers SET status='ON_TRIP', current_trip=$1 WHERE id=$2 AND status='AVAILABLE' RETURNING id", [tripId, driverId]);
    if (!drv.rowCount) throw new AppError(409, 'DRIVER_NOT_AVAILABLE');
    const trip = await tx.query("UPDATE trips SET status='DRIVER_ASSIGNED', driver_id=$1, assigned_at=now() WHERE id=$2 AND status='MATCHING' RETURNING *", [driverId, tripId]);
    if (!trip.rowCount) throw new AppError(409, 'TRIP_NO_LONGER_MATCHING');   // rider cancelled / matched elsewhere
    await tx.query("INSERT INTO outbox(event_type, payload) VALUES ('DriverAssigned', $1)", [{ tripId, driverId }]);
    return trip.rows[0];
  });
}
// after commit: remove driver from available cell set; notify rider via WebSocket
```

### Surge per cell (worker every 60 s)
```python
async def compute_surge(city: str):
    for cell in active_cells(city):
        demand = await r.get(f"demand:{city}:{cell}:5m") or 0      # requests + app opens (sliding window)
        supply = await r.scard(f"cell:{city}:{cell}:available")
        ratio = (int(demand) + 1) / (supply + 1)
        multiplier = min(3.0, max(1.0, round(0.8 + 0.4 * ratio, 1)))
        prev = float(await r.get(f"surge:{city}:{cell}") or 1.0)
        smoothed = round(0.7 * prev + 0.3 * multiplier, 1)          # avoid jumpy prices
        await r.set(f"surge:{city}:{cell}", smoothed, ex=180)
```

### Fare quote locked with TTL (rider sees the same price)
```js
app.post('/api/v1/quotes', authenticate, async (req, res) => {
  const route = await maps.route(req.body.pickup, req.body.drop);            // km, minutes (cached)
  const surge = Number(await redis.get(`surge:${city}:${latLngToCell(req.body.pickup.lat, req.body.pickup.lng, RES)}`) ?? 1);
  const fare = Math.round((BASE + PER_KM * route.km + PER_MIN * route.min) * surge);
  const quoteId = crypto.randomUUID();
  await redis.set(`quote:${quoteId}`, JSON.stringify({ fare, surge, route, userId: req.user.id }), { EX: 300 });
  res.json({ quoteId, fare, surge, etaMin: await pickupEta(req.body.pickup) });
});
```

### React Native driver app essentials
```
- Background location with foreground service (Android) / significant-change + background modes (iOS)
- Offer screen: 15 s countdown, accept → POST /offers/:id/accept (idempotent)
- Trip start requires rider OTP; trip end idempotent (retry-safe) even on weak network
- Navigation deep link to Google Maps; offline queue for trip events
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you find nearby available drivers quickly when they're constantly moving?**
A1: Keep an in-memory geospatial index partitioned by city: discretize locations into cells (H3 hexagons, geohash or S2) and maintain the set of available drivers per cell, updating a driver's cell membership only when it changes (location updates every few seconds). For a pickup, query its cell plus neighbouring rings to get candidates, filter by status and vehicle, then rank by road-network ETA rather than straight-line distance. Redis GEO or in-memory quadtrees are alternatives. A relational distance query per request is too slow.

**Q2: How do you prevent a driver from being assigned two trips at once?**
A2: Make assignment an atomic compare-and-set on the driver's state (AVAILABLE to ON_TRIP only if still available), together with the trip's state transition (MATCHING to ASSIGNED), in one transaction or via a per-driver lock or a single-writer actor per driver, keyed by driver ID. Offers are sequential or carefully coordinated, and if acceptance races with another assignment or a rider cancellation, the conditional update fails and dispatch continues. All operations are idempotent.

**Q3: How does surge pricing work?**
A3: For each geographic cell or zone, the system continuously computes demand (ride requests and app opens in a recent window) and supply (available drivers nearby). The ratio maps to a multiplier, smoothed over time and capped (also subject to regulations). The multiplier is applied to fare estimates and locked into the quote for a short TTL so the rider sees a consistent price. Higher prices reduce demand and attract drivers to the area, rebalancing the market. Driver apps show heatmaps.

**Q4: How do you calculate ETAs and fares accurately?**
A4: Use a routing service over the road graph (OSRM, Valhalla, Google Maps, or in-house) with live traffic and historical speed profiles, plus ML models trained on past trips for corrections (time of day, weather, local patterns). Fare estimates use the predicted route distance and time with the surge multiplier and taxes. Final fares use the actual map-matched GPS trace (distance and time), with checks against GPS spoofing and route manipulation, and upfront-pricing rules where applicable.

**Q5: How would you design the system to stay reliable during peaks and partial failures?**
A5: Partition by city or region (dispatch, geo index, surge), so failures and load are isolated. Scale location ingestion horizontally on Kafka, and keep trip state in a strongly consistent store with idempotent APIs (request, accept, start, end, pay). Degrade non-critical features (detailed ETAs, recommendations) when dependencies are slow, using cached ETAs and fallbacks. Clients queue events offline with jittered reconnects, and payments are retried asynchronously with reconciliation. Monitor match rate, time-to-match and cancellation rate per city as key SLOs.

---

## 🔷 Trade-offs
✅ H3/in-memory cells: fast nearby queries — ❌ memory & update churn; need city sharding.
✅ Batch/global optimization: better matches — ❌ adds seconds of latency & complexity vs greedy.
✅ Surge pricing: balances market — ❌ user dissatisfaction/regulation; needs smoothing & caps.
✅ Strongly consistent trip state: correctness — ❌ single-writer constraints; must be HA.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dispatch / matching | Pairing rider with driver | यात्री और ड्राइवर को जोड़ना |
| H3 | Uber's hexagonal geo index | षट्कोणीय नक्शा grid |
| k-ring / gridDisk | Neighbouring cells | आस-पास के खाने |
| Surge pricing | Dynamic price multiplier | माँग के हिसाब से किराया |
| Quote | Locked fare estimate | तय किया गया अनुमानित किराया |
| Trip state machine | Allowed trip status changes | trip की स्थितियाँ |
| Map matching | Snapping GPS to roads | GPS को सड़क पर बैठाना |
| Road ETA | Travel time via road network | सड़क से पहुँचने का समय |
| Call masking | Proxy phone numbers | नंबर छिपाकर बात |
| Supply-demand | Drivers vs requests balance | ड्राइवर बनाम माँग |

---

## ⚡ 3-Line Summary
**English:**
1. Drivers stream GPS → in-memory H3/geo index per city (available sets per cell) + Kafka history.
2. Request → candidates from nearby cells → rank by road ETA → sequential offers → atomic CAS assignment; trip state machine with evented, idempotent transitions.
3. Surge per cell from demand/supply (smoothed, capped, quote-locked); fares from map-matched routes; city isolation, safety features, async payments.

**Hindi:**
1. ड्राइवर GPS → शहर-वार H3 index (हर cell में ख़ाली ड्राइवर) + Kafka इतिहास।
2. Request → पास के cells से candidates → सड़क ETA → offer → atomic assignment; trip state machine।
3. हर cell में माँग/आपूर्ति से surge; असली रास्ते से किराया; शहर-वार अलगाव, सुरक्षा, async पेमेंट।

---

## ➡️ Next Topic Suggestion
**126. Analytics Platform** — Every system above emits events. Next: design an analytics platform to collect billions of events and power dashboards and product analytics (event pipeline, data lake, warehouse, OLAP, real-time metrics).
