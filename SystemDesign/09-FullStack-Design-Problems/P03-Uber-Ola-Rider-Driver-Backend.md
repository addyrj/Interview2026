# P03. Uber/Ola — Rider App + Driver App + Backend (End-to-End Design)
# हिंदी में: Uber/Ola का पूरा डिज़ाइन — सवारी (rider) ऐप, चालक (driver) ऐप और backend: pickup चुनना, किराया, पास के driver से मिलान (matching), live tracking, OTP से ride शुरू, भुगतान (UPI/नक़द) और rating

---

## 🔵 Simple Definition (English)
Design a ride-hailing platform end to end with **two mobile apps and a real-time backend**:
- **Rider app**: choose pickup and drop on a map, see fare estimates per vehicle type (bike, auto, mini, sedan), request a ride, get matched, **track the driver live**, share the **ride OTP** to start, pay (UPI/card/wallet/cash) and rate.
- **Driver app**: go online, stream location continuously (even with the screen off), receive **ride offers** with a countdown, accept, navigate to pickup, verify OTP, run the trip, end the trip, see earnings.
- **Backend**:
  - **location ingestion** and an in-memory **geo index** (H3/geohash)
  - **dispatch/matching**
  - **pricing and surge**
  - **ETA/routing**
  - a server-authoritative **trip state machine**
  - **payments**
  - **notifications** and real-time channels
  - **safety** (SOS, trip sharing) and **fraud** checks
Backend internals are covered in **Topic 125 (Ride Sharing)**. This file covers the full system with both clients.

## 🔵 सरल परिभाषा (Hindi)
दो mobile ऐप और real-time backend वाला ride system: Rider ऐप — map पर pickup/drop, हर गाड़ी का किराया (bike, auto, mini, sedan), ride माँगना, driver मिलना, live tracking, OTP बताकर ride शुरू, भुगतान (UPI/card/नक़द) और rating; Driver ऐप — online होना, लगातार location भेजना (screen बंद हो तब भी), countdown के साथ ride offer, accept, pickup तक navigation, OTP जाँच, trip ख़त्म, कमाई।
Backend — location ingest + geo index (H3), matching, किराया और surge, ETA, सर्वर-प्रधान trip state machine, payments, notifications, safety और धोखा जाँच।

---

## 🔴 Problem it Solves
Ride-hailing coordinates **two sets of users in the physical world in real time**:
- Hundreds of thousands of drivers send GPS every few seconds, so **writes are massive** and must be indexed instantly for "nearby" queries.
- **Matching must be fast (seconds) and correct**: a driver must never get two rides at once, and a rider must never get two drivers.
- **Networks drop mid-trip** (tunnels, flyovers, basements), yet the trip, fare and payment must stay consistent.
- The driver app must work **in the background** reliably on budget Android phones with aggressive battery killers (M04).
- **Indian realities**: bikes and autos, cash payments, OTP-based ride start, pickup points in crowded lanes, surge during rain and peak office hours, GPS spoofing fraud.
It tests **real-time geo systems, state machines, mobile background execution, maps UX and consistency**.

## 🔴 यह क्यों बना? (Hindi)
Ride-hailing असली दुनिया में दो तरह के यूज़र्स को real time में जोड़ता है: लाखों drivers हर कुछ सेकंड GPS भेजते हैं — बहुत सारे writes, जिन्हें "पास में कौन" के लिए तुरंत index करना है; matching सेकंडों में और सही — एक driver को एक साथ दो rides नहीं; trip के बीच नेटवर्क टूटे फिर भी trip, किराया, भुगतान सही; driver ऐप सस्ते Android पर background में भरोसे से चले; भारत की हक़ीक़त — bike/auto, नक़द, OTP से शुरुआत, भीड़ वाली गलियाँ, बारिश में surge, नक़ली GPS।

---

## 🟢 How it Works — Step by Step

### 1. Requirements

```
Rider: set pickup (GPS + pin + suggested pickup points), drop (search), fare estimates per product,
       request, cancel (with policy), live driver location + ETA, ride OTP, in-trip route, SOS/share trip,
       pay (UPI/card/wallet/cash), rate & tip, receipts, ride history
Driver: online/offline, location streaming, ride offers (accept within ~15 s), navigation, OTP start,
        end trip, cash collection, earnings, incentives, documents/KYC
Non-functional: match in < 10 s p90, offer delivery < 1 s, location freshness 3–5 s, high availability,
        no double assignment, trip & payment consistency, battery-efficient driver app
Scale (assume, one large country): 1M drivers online at peak × location every 4 s ≈ 250k writes/s;
        100k ride requests/min at peak (rain + office hours)
```

### 2. High-level architecture

```
 Rider app (RN)                       Driver app (RN + foreground service)
   │ REST (BFF)  │ WS/SSE (trip events)    │ location stream (WS/gRPC/MQTT) │ REST │ push (offers backup)
   ▼             ▼                         ▼                                ▼
┌──────────────────────────────────── Backend ─────────────────────────────────────────┐
│ API Gateway / BFFs (rider, driver)          Real-time Gateway (sockets, presence)    │
│  ├─ Location service: ingest → validate (accuracy, speed, mock) → H3 cell index      │
│  │   (Redis: cell → available driver set; driver → last position) → Kafka (history)  │
│  ├─ Pricing service: base fare + distance/time (routing) + SURGE per H3 cell          │
│  │   (demand/supply ratio, updated every ~1 min) → fare quote (signed, valid 5 min)  │
│  ├─ Dispatch service: candidates from H3 k-rings → ETA ranking → offer → lock driver │
│  ├─ Trip service: state machine (Postgres, source of truth) + events (Kafka)         │
│  ├─ ETA/Routing (OSRM/Valhalla/own maps) · Maps/geocoding (Ola Maps/Mappls/Google)    │
│  ├─ Payments (UPI intent/collect, cards, wallet; cash reconciliation for drivers)     │
│  ├─ Notifications (FCM/APNs), Safety (SOS, trip share), Fraud/risk                    │
│  └─ Ratings, Earnings & payouts, Support                                              │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

### 3. Trip state machine (server-authoritative)

```
REQUESTED ──match──► DRIVER_ASSIGNED ──driver moving──► DRIVER_ARRIVING ──at pickup──► ARRIVED
    │                      │                                                       │ OTP ok
    │ no driver (timeout)  │ rider/driver cancel                                   ▼
    ▼                      ▼                                                   IN_PROGRESS ──► COMPLETED ──► PAID
 NO_DRIVERS_FOUND       CANCELLED (fee rules)                                        │
                                                                                      └─ SOS/incident flags
Every transition: validated (actor, allowed from-state, preconditions), versioned (optimistic lock),
idempotent (request id), emitted as event → rider/driver apps update via WS + push
```

### 4. Matching flow (dispatch)

```
1. Rider requests with quoteId (fare locked) → trip REQUESTED
2. Dispatch: H3 cell of pickup → k-ring (rings 1..3) → available drivers of requested vehicle type
3. Rank by ETA (road distance, not straight line), driver rating/acceptance, heading, fairness
4. Offer to best driver: LOCK driver (Redis SET driver:{id}:lock trip NX EX 20) → send offer
   via driver's socket (+ high-priority push backup) with 15 s countdown
5. Accept within TTL → assign (trip DRIVER_ASSIGNED, driver BUSY) ; Reject/timeout → release lock →
   next candidate (or batch offers in high-demand areas)
6. Expand radius over time; after ~2–3 min → NO_DRIVERS_FOUND (suggest other vehicle types)
Guarantee: lock + DB transaction (driver status AVAILABLE→BUSY with version check) → never double-assigned
```

### 5. Driver app (mobile specifics)

```
- Online toggle → start foreground service (Android, type=location) + iOS background location (M04/M20)
- Adaptive location: online-idle every 10–15 s; en route to pickup / in trip every 3–5 s; batch upload
- Persistent socket for offers; if socket down → FCM high-priority data message → full-screen offer
  (Android full-screen intent, loud ringtone), even if app backgrounded
- Offer UI: pickup distance/ETA, drop area (or hidden until accept), fare, countdown ring; one-tap accept
- Trip state persisted locally (MMKV/SQLite) → app crash or kill → restore screen from server state on reopen
- Navigation: hand off to Google Maps/Ola Maps intent or embedded SDK; keep location service running
- OTP entry to start; End trip → final fare from server; cash trips: collect & confirm
- Battery & OEM killers: in-app guide to whitelist; detect location gaps and alert driver
```

### 6. Rider app (mobile specifics)

```
- Pickup selection: GPS + draggable pin + snap to suggested pickup points (gates, landmarks)
- Fare estimates: GET /quotes (per product, surge multiplier shown, quote valid 5 min)
- Request → "Finding your ride" (animated) → assigned: driver card (name, photo, vehicle no., rating, ETA)
- Live tracking via WS/SSE: interpolated marker movement, route polyline, ETA updates (M20)
- Ride OTP shown on screen (4 digits) → share verbally with driver → prevents wrong-car rides
- Background: push notifications for "Driver arrived", "Trip started", receipts; iOS Live Activity /
  Android ongoing notification with ETA
- Payment: UPI intent (verify server-side), saved cards (tokenized), wallet, cash; failed payment → dues
```

### 7. API contract (selected)

```
POST /quotes {pickup, drop, products[]} → [{product, fare:{amount, currency}, surge, etaMin, quoteId, expiresAt}]
POST /trips {quoteId, paymentMethod, idempotencyKey} → {tripId, status:"REQUESTED"}
WS  /rider/trips/{id}/events ← driver.location, status.changed, eta.updated
POST /trips/{id}/cancel {reason}
Driver:
WS  /driver/stream → {t:"loc", points:[…]} ; ← {t:"offer", tripId, pickup, fare, expiresAt}
POST /driver/offers/{tripId}/accept {idempotencyKey} → 200 {trip} | 409 {code:"OFFER_EXPIRED"}
POST /driver/trips/{id}/start {otp} → 200 | 422 {code:"OTP_INVALID"}
POST /driver/trips/{id}/end {odometer?, lastPoints[]} → {fare breakdown}
```

### 8. Pricing & surge

```
fare = base + per_km × route_km + per_min × route_min (+ tolls, platform fee) × surge(cell, time)
surge computed per H3 cell every ~60 s from open requests vs available drivers (smoothed, capped)
Quote locks price for N minutes (signed token) → user sees the price they pay; final fare adjusts only
for route changes/waiting time per policy
```

### 9. Failure handling

```
Driver loses network mid-trip: app buffers points locally; trip continues; on reconnect, upload backlog →
   server reconstructs route for fare (or uses estimate + policy)
Rider app killed: on reopen GET /trips/active → resume tracking screen
Dispatch service crash: trip requests in durable queue; locks expire (TTL) → safe retry
Payment failure: trip COMPLETED, payment PENDING → retry/collect later; driver paid per policy
Duplicate accept taps: idempotency key + state version check → one assignment
```

## 🟢 कैसे काम करता है? (Hindi)
1. Driver ऐप online होते ही foreground service से location भेजता है (idle में 10–15 सेकंड, trip में 3–5 सेकंड, batch में); सर्वर जाँचकर (accuracy, रफ़्तार, mock) H3 cell index (Redis) में रखता है।
2. Rider quote लेता है (किराया = base + km + मिनट × उस cell का surge, 5 मिनट के लिए lock) → request → dispatch H3 के आसपास के rings में ख़ाली drivers ढूँढकर सड़क की ETA से rank करता है → सबसे अच्छे driver को Redis lock के साथ 15 सेकंड का offer (socket + high-priority push) → accept तो assign, नहीं तो अगला।
3. Trip state machine सर्वर पर सच: REQUESTED → ASSIGNED → ARRIVING → ARRIVED → (OTP) IN_PROGRESS → COMPLETED → PAID; हर बदलाव जाँचा हुआ, version वाला, idempotent, और events से दोनों ऐप तक।
4. Rider ऐप: pin + सुझाए pickup points, driver card, interpolated live tracking, OTP दिखाना, push/Live Activity; Driver ऐप: पूरी screen वाला offer, navigation intent, OTP डालना, नक़द पुष्टि, trip की स्थिति local में भी।
5. नेटवर्क टूटे तो driver ऐप points जमा रखे और बाद में भेजे; ऐप बंद होने पर `/trips/active` से वापसी; lock TTL से अपने-आप छूटें; दो बार accept tap पर idempotency + version से एक ही assignment; payment fail हो तो बाद में वसूली।

---

## 🟡 Real World Example

**Uber H3 & dispatch** — Uber open-sourced **H3** (2018), a hexagonal hierarchical geospatial index, used for surge pricing zones, supply/demand forecasting and dispatch. Their dispatch system (DISCO) matches supply and demand using road ETAs rather than straight-line distance.

**Ola Maps (2024)** — Ola moved its mapping stack from Google Maps to its own Ola Maps in 2024, reporting large annual cost savings. It shows how map and routing API costs matter for Indian ride-hailing at scale.

**Ride OTP in India** — Uber, Ola and Rapido use a 4-digit OTP the rider shares with the driver to start the trip, preventing wrong-vehicle boardings and certain fraud. It's a simple, effective safety feature common in India.

**Rapido (bike taxis) & autos** — Indian ride-hailing heavily features two- and three-wheelers with cash payments, short trips and extreme demand spikes during rain, so drivers' budget Android phones and battery-killer issues are core engineering constraints.

## 🟡 Real Example Hindi में
Uber ने 2018 में **H3** (षट्भुज वाला geo index) open-source किया — surge zones, माँग/आपूर्ति अनुमान और dispatch में; matching सीधी दूरी नहीं, सड़क की ETA से।
2024 में Ola ने Google Maps छोड़कर अपना Ola Maps अपनाया (बड़ी बचत); भारत में Uber/Ola/Rapido 4 अंक का ride OTP इस्तेमाल करते हैं (ग़लत गाड़ी में बैठने से बचाव); Rapido की bike taxis और autos — नक़द, छोटी trips, बारिश में भारी माँग और सस्ते फ़ोन मुख्य चुनौतियाँ।

---

## 🟠 My Stack Example

### Location ingestion → H3 index (Node + Redis)
```js
import { latLngToCell, gridDisk } from 'h3-js';
const RES = 8;                                                // ~0.7 km² hexagons

export async function ingestDriverPoints(driverId, points, status, vehicle) {
  const good = points.filter((p) => p.acc <= 50 && !p.mocked && plausible(driverId, p));
  if (!good.length) return;
  const last = good.at(-1);
  const cell = latLngToCell(last.lat, last.lng, RES);
  const prev = await redis.hget(`drv:${driverId}`, 'cell');
  const m = redis.multi()
    .hset(`drv:${driverId}`, { lat: last.lat, lng: last.lng, cell, heading: last.bearing ?? 0, ts: last.ts, status, vehicle })
    .expire(`drv:${driverId}`, 60);                                                   // stale drivers vanish
  if (status === 'AVAILABLE') { if (prev && prev !== cell) m.srem(`cell:${prev}:${vehicle}`, driverId); m.sadd(`cell:${cell}:${vehicle}`, driverId); }
  else if (prev) m.srem(`cell:${prev}:${vehicle}`, driverId);
  await m.exec();
  await kafka.send({ topic: 'driver-locations', messages: good.map((p) => ({ key: driverId, value: JSON.stringify(p) })) });
  const trip = await activeTrip(driverId);
  if (trip) await redis.publish(`trip:${trip}`, JSON.stringify({ t: 'driver.location', ...last }));   // to rider WS
}

export async function nearbyAvailable(lat, lng, vehicle, k = 2) {
  const cells = gridDisk(latLngToCell(lat, lng, RES), k);       // pickup cell + rings
  const ids = (await Promise.all(cells.map((c) => redis.smembers(`cell:${c}:${vehicle}`)))).flat();
  return ids;
}
```

### Dispatch with lock + state transition (no double assignment)
```js
export async function dispatch(tripId) {
  const trip = await Trips.get(tripId);
  for (let ring = 1; ring <= 4; ring++) {
    const candidates = await rankByEta(await nearbyAvailable(trip.pickup.lat, trip.pickup.lng, trip.vehicle, ring), trip.pickup);
    for (const d of candidates.slice(0, 5)) {
      const locked = await redis.set(`lock:drv:${d.id}`, tripId, 'NX', 'EX', 20);    // one offer at a time per driver
      if (!locked) continue;
      const accepted = await offerAndWait(d.id, trip, 15_000);                       // socket + push backup
      if (accepted) return;                                                          // assignment done in accept handler
      await redis.del(`lock:drv:${d.id}`);
    }
  }
  await Trips.transition(tripId, 'REQUESTED', 'NO_DRIVERS_FOUND');
}

// Accept handler: idempotent, version-checked transaction
app.post('/driver/offers/:tripId/accept', driverAuth, idempotent, async (req, res) => {
  const { tripId } = req.params; const driverId = req.driver.id;
  if ((await redis.get(`lock:drv:${driverId}`)) !== tripId) return res.status(409).json({ error: { code: 'OFFER_EXPIRED' } });
  const ok = await db.tx(async (t) => {
    const trip = await t.one(`UPDATE trips SET status='DRIVER_ASSIGNED', driver_id=$2, version=version+1
                              WHERE id=$1 AND status='REQUESTED' RETURNING *`, [tripId, driverId]).catch(() => null);
    if (!trip) return null;
    await t.none(`UPDATE drivers SET status='BUSY' WHERE id=$1 AND status='AVAILABLE'`, [driverId]);
    return trip;
  });
  if (!ok) return res.status(409).json({ error: { code: 'TRIP_ALREADY_ASSIGNED' } });
  await events.publish('trip.assigned', ok);                                         // rider WS + push
  res.json(ok);
});
```

### Driver app: offer screen even when backgrounded (FCM data → full-screen notification)
```ts
// background handler (index.js) — @react-native-firebase/messaging + notifee
messaging().setBackgroundMessageHandler(async (msg) => {
  if (msg.data?.type !== 'RIDE_OFFER') return;
  await notifee.displayNotification({
    title: `New ride • ₹${msg.data.fare}`, body: `Pickup ${msg.data.pickupEtaMin} min away`,
    android: { channelId: 'offers', category: AndroidCategory.CALL, importance: AndroidImportance.HIGH,
               fullScreenAction: { id: 'default', launchActivity: 'default' }, sound: 'ride_offer', timeoutAfter: 15_000,
               actions: [{ title: 'Accept', pressAction: { id: 'accept' } }] },
    data: msg.data,
  });
});
```

### Rider app: active trip resume + live events
```ts
export function useActiveTrip() {
  const qc = useQueryClient();
  const q = useQuery({ queryKey: ['trip', 'active'], queryFn: () => http.get('/trips/active').then((r) => r.data), staleTime: 0 });
  useEffect(() => {
    if (!q.data?.id) return;
    return realtime.subscribe(`trip:${q.data.id}`, (e) => {
      if (e.t === 'status.changed') qc.setQueryData(['trip', 'active'], (t: any) => (e.version > t.version ? { ...t, ...e.trip } : t));
      if (e.t === 'driver.location') driverMarker.animateTo(e);                     // interpolated (M20)
    });
  }, [q.data?.id]);
  return q;
}
```

### OTP start (server)
```python
@app.post("/driver/trips/{trip_id}/start")
async def start_trip(trip_id: str, body: StartTrip, driver=Depends(current_driver)):
    trip = await trips.get(trip_id)
    if trip.driver_id != driver.id or trip.status != "ARRIVED": raise HTTPException(409, "INVALID_STATE")
    if await redis.incr(f"otp_attempts:{trip_id}") > 5: raise HTTPException(429, "TOO_MANY_ATTEMPTS")
    if not hmac.compare_digest(trip.otp_hash, hash_otp(trip_id, body.otp)): raise HTTPException(422, "OTP_INVALID")
    return await trips.transition(trip_id, "ARRIVED", "IN_PROGRESS", actor=driver.id)
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you find nearby drivers quickly?**
A1: Maintain an in-memory geo index updated on every driver location ping. Map the position to a hexagonal H3 cell (or geohash) and keep per-cell sets of available drivers by vehicle type, plus each driver's last position with a short TTL so stale drivers disappear. For a pickup, compute its cell and the surrounding k-ring cells, union the sets, then rank candidates by road-network ETA (not straight-line distance) along with acceptance rate, heading and fairness. Expand rings over time if no one accepts. Persist the location stream to Kafka for analytics and trip reconstruction.

**Q2: How do you prevent a driver from being assigned two rides?**
A2: Offer to one driver at a time with a per-driver lock in Redis (SET NX with a TTL equal to the offer window), so concurrent dispatchers can't offer the same driver. On accept, run a database transaction that transitions the trip from REQUESTED to DRIVER_ASSIGNED only if it's still REQUESTED (conditional update or version check) and the driver from AVAILABLE to BUSY. Idempotency keys handle repeated taps, and a lost race returns 409. Locks expire automatically if a dispatcher crashes.

**Q3: How does the driver app keep working in the background on Android?**
A3: When online, it runs a foreground service of type location with a persistent notification, requests background location permission, adapts GPS frequency to trip state, and batches uploads over a persistent connection. Ride offers arrive over the socket, with FCM high-priority data messages as backup to show a full-screen, ringing notification even if the app is backgrounded. It guides drivers to disable OEM battery optimizations, persists trip state locally, and detects location gaps to alert the driver and ops.

**Q4: What happens if the driver loses connectivity during a trip?**
A4: The trip continues. The driver app keeps collecting GPS points locally and queues state actions with idempotency keys. The server keeps the trip IN_PROGRESS and the rider sees "Driver location updating". On reconnect, the app uploads the buffered points (the server reconstructs the route for fare calculation) and replays queued actions like ending the trip. The server validates them against the state machine. If ending happened offline, the fare is computed from the reconstructed route or an estimate per policy, with payment processed afterwards.

**Q5: How do surge pricing and fare quotes work?**
A5: A pricing service periodically (around every minute) computes a demand-to-supply ratio per H3 cell from open requests, app opens and available drivers, smooths it, and maps it to a capped surge multiplier. A quote request computes route distance and time via the routing engine and applies base, per-km and per-minute rates, fees and the cell's surge, then returns a signed quote valid for a few minutes. Requesting a ride references the quote ID so the rider pays the price they saw, with adjustments only for route changes or waiting time per policy.

---

## 🔷 Trade-offs
✅ Sequential offers with locks: no double assignment, fair — ❌ slower matching in high demand (use batched offers).
✅ H3 cells in Redis: fast nearby search — ❌ memory & churn at high update rates (shard by city/region).
✅ Locked quotes: price transparency — ❌ business risk if conditions change (short validity).
✅ Frequent GPS: accurate tracking & fares — ❌ battery & data on driver phones (adaptive rates).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| H3 | Hexagonal geo index | षट्भुज वाला geo index |
| k-ring | Neighbouring cells around a cell | आसपास के cells |
| Dispatch | Matching riders to drivers | rider-driver मिलान |
| Offer / lock | Exclusive ride offer to a driver | एक driver को अकेला offer |
| Trip state machine | Allowed trip status transitions | trip की स्थितियाँ |
| Surge | Demand-based price multiplier | माँग के हिसाब से किराया |
| Quote | Locked fare estimate | तय किराया अनुमान |
| ETA | Estimated time of arrival | पहुँचने का अनुमानित समय |
| Ride OTP | Code to start a trip | ride शुरू करने का कोड |
| Foreground service | Android continuous background work | लगातार चलने वाली सेवा |

---

## ⚡ 3-Line Summary
**English:**
1. Driver apps stream adaptive GPS via foreground services; backend validates and indexes into H3 cells (Redis) and streams history to Kafka.
2. Quote (route + surge, signed) → request → dispatch over k-rings ranked by ETA → per-driver lock + 15 s offer (socket + push) → transactional accept; server-authoritative trip state machine with idempotent transitions.
3. Rider app: pin + pickup points, live interpolated tracking, OTP start, push/Live Activity, UPI/cash; handle offline drivers, app kills and payment failures gracefully.

**Hindi:**
1. Driver ऐप foreground service से GPS भेजते हैं; backend H3 cells (Redis) में index और Kafka में इतिहास।
2. Quote (route + surge) → request → k-rings में ETA से rank → driver lock + 15 सेकंड का offer → transaction से accept; सर्वर पर trip state machine।
3. Rider ऐप: pin + pickup points, smooth tracking, OTP, push; offline driver, ऐप बंद होना और payment failure को संभालो।

---

## ➡️ Next Topic Suggestion
**P04. Swiggy/Zomato — Customer app + Restaurant panel + Delivery app** — A three-sided marketplace: customers order, restaurants prepare, delivery partners move. Next: coordinating three clients and the backend through one order lifecycle.
