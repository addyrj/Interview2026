# P04. Swiggy/Zomato — Customer App + Restaurant Panel + Delivery App (End-to-End Design)
# हिंदी में: Swiggy/Zomato का पूरा डिज़ाइन — तीन तरफ़ का बाज़ार: ग्राहक का ऐप (खोजो, order करो, track करो), restaurant का panel (order लो, तैयार करो, menu संभालो) और delivery partner का ऐप (उठाओ, पहुँचाओ) — एक ही order की ज़िंदगी में तीनों और backend का तालमेल

---

## 🔵 Simple Definition (English)
Food delivery is a **three-sided marketplace** coordinated through one **order lifecycle**:
- **Customer app** (RN mobile + Next.js web): location and serviceability, restaurant discovery and search, menus with live availability, cart, offers/coupons, checkout (UPI/cards/wallet/COD), live order tracking, support.
- **Restaurant partner app/panel** (tablet/phone app + web dashboard): **loud, reliable new-order alerts**, accept/reject with prep time, mark "food ready", menu and item availability toggles, timings and busy mode, payouts and analytics.
- **Delivery partner app** (RN + foreground service): online/offline, assignment offers, navigate to restaurant, pickup verification, navigate to customer, delivery confirmation (OTP for some orders), cash handling, earnings.
- **Backend**:
  - catalog/menu, search, serviceability and **ETA prediction** (prep + travel)
  - cart and pricing (offers, fees, GST)
  - **order service** (state machine) and payments (PSP like Razorpay/Juspay)
  - **restaurant notification** with escalations
  - **delivery assignment** (just-in-time, batching)
  - real-time tracking, notifications, refunds and support
Backend detail is in **Topic 124 (Food Delivery)**. This file focuses on all three clients plus the backend end to end.

## 🔵 सरल परिभाषा (Hindi)
Food delivery तीन तरफ़ का बाज़ार है जो एक order की ज़िंदगी से जुड़ता है: ग्राहक ऐप/web — location, restaurant खोजना, menu (कौन-सा item उपलब्ध), cart, coupons, भुगतान (UPI/card/COD), live tracking; Restaurant panel — तेज़ आवाज़ वाला नया-order alert, accept/reject + तैयारी का समय, "खाना तैयार", item बंद/चालू, busy mode; Delivery partner ऐप — online, assignment, restaurant तक, pickup, ग्राहक तक, delivery (कभी OTP), नक़द, कमाई।
Backend — menu, search, ETA (तैयारी + सफ़र), cart/pricing (offers, fees, GST), order state machine, payments, restaurant को बार-बार सूचना, rider assignment (सही समय पर, batching), tracking, refunds।

---

## 🔴 Problem it Solves
Each side has different needs, devices and failure modes:
- Customers want **accurate ETAs, correct menus (no "item unavailable" after paying), fast checkout and live tracking**, on budget phones and 4G.
- Restaurants run busy kitchens with a **tablet on flaky Wi-Fi**. A missed order alert means a cancelled order and an angry customer.
- Delivery partners need **simple, vernacular, battery-efficient apps** that work in the background (M04/M20), and **minimal waiting** at restaurants (time is their income).
- The platform must **assign riders at the right time** (too early wastes rider time, too late lets food go cold), handle **demand spikes** (rain, IPL finals, New Year's Eve), and keep **payments and refunds consistent** across cancellations.
It tests **multi-client coordination, state machines, real-time notifications, ETA/assignment logic and Indian payment/ops realities**.

## 🔴 यह क्यों बना? (Hindi)
हर पक्ष की ज़रूरत, device और मुश्किल अलग: ग्राहक — सही ETA, सही menu (पैसे देने के बाद "item उपलब्ध नहीं" नहीं), जल्दी checkout, live tracking — सस्ते फ़ोन और 4G पर; restaurant — व्यस्त रसोई में flaky Wi-Fi वाला tablet, छूटा alert = cancel order; delivery partner — आसान, अपनी भाषा वाला, battery-बचाऊ ऐप और restaurant पर कम इंतज़ार (समय = कमाई)।
Platform को rider सही समय पर भेजना (जल्दी = rider का समय बर्बाद, देर = ठंडा खाना), बारिश/IPL/नए साल की भीड़ संभालना, और cancel पर भुगतान/refund सही रखना।

---

## 🟢 How it Works — Step by Step

### 1. Requirements & scale

```
Customer: address & serviceability, home (server-driven widgets), search, menu (variants/add-ons),
          cart (one restaurant), coupons, fees (delivery, packaging, platform), GST, pay (UPI/cards/
          wallet/COD), live tracking, rate, help/refunds
Restaurant: new-order alert (sound + vibration, repeated), accept/reject within N min, prep time,
            mark ready, item/variant out-of-stock toggle, busy/closed mode, order history, payouts
Delivery: online/offline, assignment offers, pickup/drop flows, OTP/photo proof, cash collection,
          earnings, incentives, vernacular UI
Scale (assume): 2–3M orders/day, dinner peak ~3–5× average (~150–250 orders/s), NYE/IPL spikes higher;
                300k+ restaurants, 300k+ active delivery partners at peak
Latency: menu load < 1 s, checkout < 2 s, restaurant alert < 2 s, tracking freshness ~5 s
```

### 2. Architecture

```
Customer app (RN) / web (Next.js)   Restaurant app (tablet RN) + web panel   Delivery app (RN, FG service)
          │ BFF REST + WS/SSE                 │ WS + push + IVR fallback            │ WS/REST + push + location stream
          ▼                                    ▼                                     ▼
┌──────────────────────────────────────────── Backend ─────────────────────────────────────────────┐
│ Customer BFF · Partner BFF · Rider BFF · Real-time gateway                                         │
│ Catalog/Menu svc (Postgres + Redis cache; availability toggles → events) · Search (Elasticsearch)  │
│ Serviceability & ETA svc (polygons/H3, prep-time model + travel-time model)                        │
│ Cart & Pricing svc (offers engine, fees, GST) · Order svc (state machine, Postgres, outbox→Kafka)  │
│ Payment svc (PSP: Razorpay/Juspay/Paytm; UPI intent/collect; webhooks; refunds)                     │
│ Restaurant Notification svc (WS → push → repeated sound → IVR call → ops escalation)               │
│ Delivery Assignment svc (just-in-time, batching, H3 rider index) · Location svc · Tracking         │
│ Notification svc (push/SMS/WhatsApp) · Support & refunds · Analytics (Kafka → ClickHouse)          │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3. Order lifecycle (state machine across three apps)

```
CART ─checkout─► PAYMENT_PENDING ─PSP success webhook─► PLACED ─────────────► (Restaurant app rings)
                     │ fail/timeout → PAYMENT_FAILED                │
                                                                     ▼
                              RESTAURANT_ACCEPTED (prep_time=15m) ◄──┘   (no accept in 3–5 min → auto-
                                     │                                   cancel + refund, or ops call)
                                     │ assignment at T = ready_time − rider_travel_time (just-in-time)
                                     ▼
                              RIDER_ASSIGNED ─► RIDER_AT_RESTAURANT ─► FOOD_READY ─► PICKED_UP
                                                                                       │
                                                         OUT_FOR_DELIVERY ◄────────────┘
                                                                │ OTP / handover
                                                                ▼
                                                           DELIVERED ─► RATED
Cancels: by customer (before accept: free; after: fee policy), restaurant (item unavailable → refund),
         platform (no rider) → refund via PSP (idempotent), coupons restored
Each transition → event (Kafka) → push/WS to the right apps
```

### 4. Customer app flows

```
- Address: GPS + draggable pin + flat/landmark (M20) → serviceability check (polygon/H3) → home
- Home & menus: server-driven widgets (M09); menu cached briefly, AVAILABILITY refreshed often (item
  toggles from restaurants pushed via events → cache invalidation → menu API reflects within seconds)
- Cart: local (Zustand + MMKV) for instant UI + server cart for pricing; reprice on every change
  (offers, delivery fee by distance/surge, packaging, GST) → show breakdown
- Checkout: create order (idempotency key) → PAYMENT_PENDING → UPI intent / card SDK → poll/WS for
  payment status (never trust client result) → PLACED → tracking screen
- Tracking: WS/SSE events + rider location interpolation; push for key milestones; iOS Live Activity
- Web: Next.js SSR/ISR for restaurant & dish pages (SEO "biryani near me"), CSR for cart/checkout
```

### 5. Restaurant app/panel (reliability first)

```
- Kitchen tablet app keeps a persistent socket; new order → loud repeating ringtone until acknowledged
- If socket down: high-priority push; if not accepted in ~60–90 s → automated IVR call to restaurant;
  then ops escalation → finally auto-cancel + refund (protect customer)
- Accept with prep time (default from history) → can extend ("+5 min") → updates ETA
- Item/variant availability toggle → instant (optimistic) → event to catalog → customer menus update
- Busy mode / pause orders during rush; printing KOT (kitchen order ticket) via Bluetooth/LAN printer
- Works on flaky Wi-Fi: local queue of actions (accept, ready) with idempotency; status sync on reconnect
- Web dashboard (Next.js): menu management, reports, payouts, reviews, ads
```

### 6. Delivery partner app

```
- Online → foreground service + adaptive location (M04/M20); OEM battery guide
- Assignment offer (socket + push backup) → accept → navigate to restaurant (Maps intent)
- Arrive (geofence) → wait if food not ready (timer visible to ops) → pickup (match order id / OTP)
- Navigate to customer → call customer (masked number) → deliver (OTP for high-value / photo proof)
- COD: collect cash, cash-in-hand limits, deposit flows
- Vernacular UI (Hindi, Tamil, Kannada…), big buttons, voice prompts; offline-tolerant actions queue
```

### 7. Just-in-time assignment & batching

```
Goal: rider reaches restaurant when food is ready (min rider wait, min food wait)
assign_at ≈ predicted_ready_time − predicted_travel_time(rider → restaurant) − buffer
Prep-time model: restaurant history, item complexity, current load (open orders), time of day
Batching: two orders from same/nearby restaurants to nearby customers → one rider (route feasible,
          ETA promise kept)
Scarcity (rain): increase radius, surge delivery fee / rider incentives, show "high demand" ETA,
          temporarily restrict far restaurants (serviceability shrink)
```

### 8. Payments & refunds (India)

```
UPI intent (PhonePe/GPay/Paytm), UPI collect, cards (tokenized per RBI), wallets, COD, Swiggy/Zomato
money; PSP webhooks are source of truth → order PLACED only after verified success
Idempotency: order create, payment create, refund create all keyed; reconcile daily with PSP reports
Refunds: partial (item missing), full (cancel); instant to wallet or 5–7 days to source
GST invoice per order (restaurant + platform fee components)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Order state machine: CART → PAYMENT_PENDING → (PSP webhook से पक्का) PLACED → restaurant ACCEPTED (तैयारी का समय) → rider ASSIGNED (सही समय पर) → FOOD_READY → PICKED_UP → OUT_FOR_DELIVERY → DELIVERED; cancel पर नियम के हिसाब से refund; हर बदलाव event से तीनों ऐप तक।
2. ग्राहक ऐप: pin + flat/landmark → serviceability; menu कुछ देर cache, पर item की उपलब्धता जल्दी ताज़ा (restaurant toggle → event → cache invalidate); cart local + server repricing (offers, fees, GST); भुगतान का नतीजा सर्वर से; tracking WS + push + Live Activity।
3. Restaurant ऐप भरोसे पर बना: socket पर तेज़ बार-बार बजने वाली ring; socket बंद तो push; 60–90 सेकंड में accept नहीं तो IVR call, फिर ops, आख़िर में auto-cancel + refund; item बंद/चालू तुरंत; flaky Wi-Fi पर actions की local कतार; KOT printing।
4. Delivery ऐप: foreground service, offer (socket + push), restaurant पर geofence, pickup मिलान, masked call, OTP/फ़ोटो से delivery, COD सीमा, अपनी भाषा में बड़ा और आसान UI।
5. Just-in-time assignment: rider को तब भेजो जब वो खाना तैयार होने पर पहुँचे (तैयारी model − सफ़र का समय); पास-पास के orders batch; बारिश में radius बढ़ाओ, incentives, "high demand" ETA; भुगतान PSP webhook से पक्का, सब idempotent, रोज़ reconciliation।

---

## 🟡 Real World Example

**Swiggy & Zomato engineering** — both have written about ML-based delivery-time prediction (prep time plus travel plus last-mile), rider assignment and batching, and handling peak days. New Year's Eve and big cricket nights are publicized as record order days, with capacity planned weeks ahead.

**Restaurant order acceptance** — food platforms commonly escalate unaccepted orders from app alerts to automated phone calls and ops teams before auto-cancelling. A missed tablet alert is one of the biggest causes of cancellations.

**Quick commerce (Swiggy Instamart, Zomato's Blinkit, Zepto)** — the same three-sided pattern, with dark stores replacing restaurants: picking and packing apps, 10-minute promises, and inventory accuracy as the "menu availability" problem.

**UPI-first payments** — UPI dominates Indian digital payments (NPCI reports well over 10 billion transactions a month), so food apps optimize UPI intent flows, handle pending or timeout states, and reconcile via PSP webhooks. COD remains important in some segments.

## 🟡 Real Example Hindi में
Swiggy और Zomato ने तैयारी + सफ़र + आख़िरी मील वाले ML ETA, rider assignment और batching पर लिखा है; नया साल और बड़े cricket मैच वाली रातें record order वाले दिन होते हैं — हफ़्तों पहले से capacity की तैयारी।
Accept न हुए order पर app alert → automated phone call → ops → फिर auto-cancel आम तरीका है; Instamart, Blinkit, Zepto में वही तीन-तरफ़ा pattern, restaurant की जगह dark stores; UPI (हर महीने 10 अरब+ लेन-देन) सबसे बड़ा भुगतान तरीका।

---

## 🟠 My Stack Example

### Order service: transitions with outbox (Node + Postgres)
```js
const ALLOWED = {
  PAYMENT_PENDING: ['PLACED', 'PAYMENT_FAILED'],
  PLACED: ['RESTAURANT_ACCEPTED', 'CANCELLED'],
  RESTAURANT_ACCEPTED: ['RIDER_ASSIGNED', 'FOOD_READY', 'CANCELLED'],
  RIDER_ASSIGNED: ['RIDER_AT_RESTAURANT', 'FOOD_READY', 'CANCELLED'],
  RIDER_AT_RESTAURANT: ['FOOD_READY', 'PICKED_UP'], FOOD_READY: ['PICKED_UP'],
  PICKED_UP: ['OUT_FOR_DELIVERY'], OUT_FOR_DELIVERY: ['DELIVERED'],
};

export async function transition(orderId, to, { actor, data = {}, expectedVersion }) {
  return db.tx(async (t) => {
    const o = await t.one('SELECT * FROM orders WHERE id=$1 FOR UPDATE', [orderId]);
    if (expectedVersion != null && o.version !== expectedVersion) throw conflict('STALE_VERSION', o);
    if (o.status === to) return o;                                            // idempotent repeat
    if (!ALLOWED[o.status]?.includes(to)) throw conflict('INVALID_TRANSITION', o);
    const u = await t.one(`UPDATE orders SET status=$2, version=version+1, updated_at=now(), data=data||$3 WHERE id=$1 RETURNING *`, [orderId, to, data]);
    await t.none(`INSERT INTO outbox (topic, key, payload) VALUES ('order-events', $1, $2)`, [orderId, { type: 'order.status', to, actor, order: publicView(u) }]);
    return u;
  });
}
// Outbox relay → Kafka → consumers: notification svc, assignment svc, tracking WS fan-out, analytics
```

### Restaurant notification escalation (worker)
```python
async def on_order_placed(order):
    await realtime.send(f"restaurant:{order.restaurant_id}", {"t": "order.new", "order": order.summary()})
    await push.send_to_restaurant(order.restaurant_id, title="New order 🔔", sound="order_ring", priority="high")
    await scheduler.at(seconds=75, job="escalate_accept", order_id=order.id, level=1)

async def escalate_accept(order_id: str, level: int):
    order = await orders.get(order_id)
    if order.status != "PLACED": return                                       # accepted/cancelled already
    if level == 1:
        await ivr.call(order.restaurant_phone, script="new_order_pending", order_ref=order.short_id)
        await scheduler.at(seconds=90, job="escalate_accept", order_id=order_id, level=2)
    elif level == 2:
        await ops_queue.raise_alert("UNACCEPTED_ORDER", order_id)
        await scheduler.at(seconds=120, job="escalate_accept", order_id=order_id, level=3)
    else:
        await orders.transition(order_id, "CANCELLED", actor="system", data={"reason": "RESTAURANT_UNRESPONSIVE"})
        await payments.refund_full(order_id, idempotency_key=f"refund:{order_id}")
        await notify_customer(order_id, "Sorry! The restaurant didn't respond. Full refund initiated.")
```

### Restaurant tablet app: ring until acknowledged + offline-safe actions (RN)
```tsx
export function useNewOrderAlerts() {
  const sound = useRef<Audio.Sound>();
  useEffect(() => realtime.subscribe(`restaurant:${restaurantId}`, async (e) => {
    if (e.t !== 'order.new') return;
    ordersStore.add(e.order);
    if (!sound.current) { const { sound: s } = await Audio.Sound.createAsync(require('@/assets/order_ring.mp3'), { isLooping: true, volume: 1 }); sound.current = s; }
    await sound.current.playAsync();                                         // loops until accepted/rejected
    activateKeepAwakeAsync();                                                 // screen stays on in kitchen
  }), []);
  const accept = async (orderId: string, prepMin: number) => {
    ordersStore.markAccepted(orderId, prepMin);                               // optimistic
    await sound.current?.stopAsync();
    await outbox.enqueue({ type: 'ACCEPT_ORDER', orderId, prepMin, idempotencyKey: `accept:${orderId}` });   // survives flaky Wi-Fi
  };
  return { accept };
}
```

### Item availability toggle → menu cache invalidation
```js
app.post('/partner/items/:itemId/availability', partnerAuth, async (req, res) => {
  const { available } = req.body;
  await Items.setAvailability(req.params.itemId, req.partner.restaurantId, available);
  await redis.del(`menu:${req.partner.restaurantId}`);                         // customer menu cache
  await kafka.send({ topic: 'menu-events', messages: [{ key: req.partner.restaurantId, value: JSON.stringify({ itemId: req.params.itemId, available }) }] });
  res.json({ ok: true });
});
// Checkout re-validates availability & prices server-side → never charge for unavailable items
```

### Just-in-time assignment trigger
```python
async def on_restaurant_accepted(order):
    ready_at = order.accepted_at + timedelta(minutes=predict_prep_minutes(order))
    travel = await eta.rider_to_restaurant_estimate(order.restaurant_location)   # from nearby rider supply
    assign_at = max(now(), ready_at - travel - timedelta(minutes=2))
    await scheduler.at(when=assign_at, job="assign_rider", order_id=order.id)    # re-planned if prep time changes
```

### Customer checkout (RN): create → pay → verify
```ts
export async function checkout(cartId: string, method: 'UPI' | 'CARD' | 'COD') {
  const key = `order:${cartId}`;                                              // same key on retries
  const order = await http.post('/orders', { cartId, method }, { headers: { 'Idempotency-Key': key } }).then((r) => r.data);
  if (method === 'COD') return order;                                        // PLACED directly
  await payWith(method, order.payment);                                      // UPI intent / card SDK
  return waitForStatus(order.id, ['PLACED', 'PAYMENT_FAILED'], { timeoutMs: 120_000 });   // WS + polling fallback
}
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you make sure restaurants never miss orders?**
A1: Use multiple escalating channels. A persistent socket on the restaurant tablet triggers a loud, looping alert with keep-awake until acknowledged. High-priority push serves as backup if the socket is down. If not accepted within about a minute, an automated IVR call goes to the restaurant, then an alert to the ops team. After a deadline, the order is auto-cancelled with an instant refund to protect the customer. Actions from the tablet are queued locally with idempotency keys to survive flaky Wi-Fi, and acceptance rates and latencies are monitored per restaurant.

**Q2: When should you assign a delivery partner to an order?**
A2: Just in time: assign so the rider arrives about when the food is ready. Compute the predicted ready time (an ML prep-time model using restaurant history, item complexity and current kitchen load) minus the predicted rider travel time from nearby supply and a small buffer, and schedule assignment then, re-planning if the restaurant updates prep time. Too early wastes riders' paid time and clogs restaurants; too late makes food wait and breaks ETAs. Batch compatible orders when routes and promises allow, and during scarcity widen the radius and adjust incentives.

**Q3: How do you keep menus accurate so customers don't order unavailable items?**
A3: Restaurants toggle item or variant availability in their app, which writes to the catalog and emits an event that invalidates menu caches, so customer-facing menu APIs reflect changes within seconds. Clients refetch menus on screen focus and use short cache TTLs for availability. The authoritative check happens server-side at cart repricing and checkout: unavailable items are blocked before payment. If an item becomes unavailable after the order is placed, the restaurant marks it, the customer is notified and offered alternatives, and a partial refund is issued automatically.

**Q4: How do you handle payments and refunds reliably?**
A4: Create the order and payment with idempotency keys and set the order to PAYMENT_PENDING. The client completes UPI or card flows via the PSP, but the order becomes PLACED only after a verified PSP webhook or server-side status check. Pending and timeout states are polled and reconciled, so a payment that eventually succeeds still places the order or is auto-refunded. Refunds (full or partial) are idempotent API calls tied to order events, and daily reconciliation against PSP settlement reports catches mismatches. Store money as integer paise and generate GST invoices.

**Q5: How do you handle a sudden spike, like heavy rain in Bengaluru at dinner time?**
A5: Demand rises while rider supply drops. Pre-scale stateless services and caches, and protect core paths with rate limiting and load shedding (non-critical widgets off). Adjust the marketplace: surge delivery fees and rider incentives, a temporarily shrunk serviceability radius for far restaurants, batching more orders per rider, realistic ETAs shown as "high demand", and restaurants pausing via busy mode. Monitor order-to-rider ratios per zone in real time and communicate proactively to customers, using feature flags to toggle these modes instantly.

---

## 🔷 Trade-offs
✅ Just-in-time assignment: less rider idle time — ❌ risk of late riders if predictions are off (buffers, re-planning).
✅ Aggressive restaurant escalation (IVR): fewer missed orders — ❌ cost & restaurant annoyance (tune thresholds).
✅ Server-driven home/menus: change without releases — ❌ cache freshness vs load trade-off for availability.
✅ Batching orders: efficiency — ❌ slightly longer delivery for one customer (respect ETA promise).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Three-sided marketplace | Customers, restaurants, riders | तीन पक्षों का बाज़ार |
| Serviceability | Can we deliver here now? | यहाँ delivery संभव? |
| Prep-time prediction | ML estimate of cooking time | पकने के समय का अनुमान |
| Just-in-time assignment | Assign rider to arrive at ready time | सही समय पर rider |
| Batching | Multiple orders per rider | एक rider कई orders |
| KOT | Kitchen order ticket | रसोई का order पर्चा |
| IVR escalation | Automated call when unaccepted | अपने-आप फ़ोन call |
| PSP webhook | Payment provider callback | भुगतान की पुष्टि |
| Reconciliation | Matching records with PSP | हिसाब मिलान |
| Busy mode | Restaurant pauses/slows orders | व्यस्त मोड |

---

## ⚡ 3-Line Summary
**English:**
1. One server-authoritative order state machine (with outbox → Kafka events) coordinates the customer app, restaurant panel and delivery app.
2. Restaurant reliability via socket + loud alerts + push + IVR + ops escalation + auto-cancel/refund; accurate menus via availability events and server-side checkout validation.
3. Just-in-time rider assignment from prep-time and travel models, batching, surge strategies, UPI-first payments verified by webhooks with idempotent refunds and reconciliation.

**Hindi:**
1. सर्वर पर एक order state machine (outbox → Kafka) ग्राहक, restaurant और delivery ऐप को जोड़ती है।
2. Restaurant के लिए socket + तेज़ alert + push + IVR + ops + auto-cancel/refund; सही menu के लिए availability events और checkout पर जाँच।
3. तैयारी और सफ़र के model से सही समय पर rider, batching, भीड़ की रणनीति, UPI भुगतान webhook से पक्का, idempotent refunds।

---

## ➡️ Next Topic Suggestion
**P05. Google Docs — Collaborative Editor** — Real-time collaboration at its hardest: many people editing the same document at once. Next: OT vs CRDT, presence, offline editing, version history and permissions, across web and mobile.
