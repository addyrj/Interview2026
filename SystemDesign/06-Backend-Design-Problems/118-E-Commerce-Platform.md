# 118. E-Commerce Platform (Amazon / Flipkart)
# हिंदी में: E-Commerce Platform — products की सूची, search, cart, stock (inventory), checkout, payment, orders और flash sale संभालने वाला पूरा सिस्टम

---

## 🔵 Simple Definition (English)
Design an online marketplace like **Amazon / Flipkart / Myntra**: **catalog** (millions of products, variants, sellers, prices), **search & browse** (filters, ranking), **product detail pages**, **cart**, **inventory** (stock per warehouse/seller), **checkout** (address, pricing, coupons, taxes, delivery estimate), **payments**, **order management** (lifecycle, cancellations, returns), **notifications**, and **flash sales** with huge spikes. It's a composition of many services with very different consistency and scale needs.

## 🔵 सरल परिभाषा (Hindi)
Amazon/Flipkart जैसा सिस्टम: करोड़ों products, search और filters, product page, cart, गोदाम-वार stock, checkout (पता, कीमत, coupon, tax, delivery तारीख़), payment, order का पूरा जीवन (cancel, return), और flash sale की भारी भीड़।
हर हिस्से की अलग ज़रूरत — browsing तेज़ और थोड़ा पुराना चलेगा, पर stock और payment बिल्कुल सही होने चाहिए।

---

## 🔴 Problem it Solves
An e-commerce system must:
- Serve **browsing** (99% of traffic) **fast and cheaply** from caches, CDNs and search indexes.
- Keep **inventory correct**: never sell stock you don't have (oversell), especially in flash sales with 100× traffic on a few SKUs.
- Make **checkout and payment reliable**: no double charges, no lost orders, money reconciled.
- Coordinate **many services** (catalog, pricing, inventory, orders, payments, logistics) without distributed transactions.
- Survive **Big Billion Days / Prime Day** spikes.

## 🔴 यह क्यों बना? (Hindi)
99% ट्रैफ़िक browsing का — उसे cache, CDN, search से तेज़ और सस्ता परोसना; stock कभी ग़लत न हो (oversell नहीं), ख़ासकर flash sale में; checkout और payment में दोहरा पैसा या खोया ऑर्डर नहीं; कई services बिना distributed transaction के तालमेल में; और Big Billion Days जैसी भीड़ झेलनी।

---

## 🟢 How it Works — Step by Step (Interview Design)

### 1. Requirements

```
Functional: browse/search catalog, product page (price, stock status, delivery ETA, reviews),
  cart (persistent, multi-device), checkout (address, coupon, tax, shipping), payment,
  order tracking, cancel/return/refund, seller inventory updates, flash sales
Non-functional:
  - Browse/search: p99 < 200 ms, highly available (AP; stale price/stock display OK briefly)
  - Inventory & orders: strongly consistent at reservation/purchase time (no oversell)
  - Payment: exactly-once effect, reconciled
  - Scale: 50M DAU, 100k RPS browsing peak; sale: 10k orders/s for minutes
```

### 2. Estimation

```
Catalog: 100M SKUs × 5 KB = 500 GB (+ images in S3/CDN)
Browse: 50M DAU × 30 page views = 1.5B/day ≈ 17k RPS avg, 100k peak → CDN/cache/search
Orders: 5M/day normal ≈ 60/s; sale peak 10k/s for a few minutes
Cart writes: 20M/day; Inventory checks: every product page view (cached availability)
```

### 3. Services & data stores

```
┌───────────────┬─────────────────────────────────────┬─────────────────────────────────────┐
│ Service       │ Responsibility                      │ Store                               │
├───────────────┼─────────────────────────────────────┼─────────────────────────────────────┤
│ Catalog       │ products, variants, attributes      │ Postgres/Mongo (source) + cache     │
│ Search        │ text search, filters, facets, rank  │ Elasticsearch (fed by CDC/events)   │
│ Pricing/Promo │ price, discounts, coupons, offers   │ Postgres + Redis cache              │
│ Inventory     │ stock per SKU per warehouse,        │ Postgres (strong) + Redis (fast     │
│               │ reservations                        │ counters for flash sales)           │
│ Cart          │ user carts                          │ Redis/DynamoDB (+ durable copy)     │
│ Checkout/Order│ order creation, lifecycle (saga)    │ Postgres (ACID), outbox → Kafka     │
│ Payment       │ gateway integration, ledger         │ Postgres (Topic 119)                │
│ Logistics     │ serviceability, ETA, shipments      │ Postgres + geo data                 │
│ Reviews       │ ratings, reviews                    │ Mongo/Cassandra + aggregates        │
│ Notification  │ order updates                       │ (Topic 114)                         │
└───────────────┴─────────────────────────────────────┴─────────────────────────────────────┘
```

### 4. Architecture

```
 📱/🌐 ── CDN (images, static, cached PDP fragments) ── API Gateway / BFF
                                              │
       ┌──────────────┬───────────────┬───────┴──────┬──────────────┬──────────────┐
       ▼              ▼               ▼              ▼              ▼              ▼
   Search svc     Catalog svc     Cart svc     Checkout/Order   Inventory     Payment svc
   (Elastic)      (+Redis cache)  (Redis)      svc (saga)       svc           ──► PG gateways
       ▲              │                            │   ▲            ▲              (Razorpay/
       │  CDC/events  │                            │   └─reserve────┘               Juspay)
       └──────────────┘                            ▼
                                     Kafka: OrderPlaced, PaymentCaptured, OrderShipped ...
                                       ├─► Logistics / warehouse (pick-pack-ship)
                                       ├─► Notifications
                                       ├─► Analytics / recommendations
                                       └─► Seller payouts / accounting
```

### 5. Checkout flow (saga, Topic 70)

```
1. Validate cart: re-price on server (never trust client prices), apply coupon rules, compute tax
   & shipping, check serviceability (pincode)
2. Create order PENDING_PAYMENT (idempotency key = checkout attempt id)
3. RESERVE inventory with TTL (e.g. 10–15 min): decrement available, increment reserved
4. Create payment order with gateway → client completes payment (UPI/card/netbanking)
5. Payment webhook/verification: CAPTURED → order CONFIRMED → reservation → committed (sold)
   FAILED/TIMEOUT → release reservation → order CANCELLED (compensation)
6. Emit OrderConfirmed → warehouse fulfilment, notifications, invoice
Reconciliation job: gateway settlements vs orders (Topic 68)
```

### 6. Inventory: preventing oversell

```
Normal traffic: Postgres atomic conditional update
  UPDATE inventory SET available = available - :q, reserved = reserved + :q
  WHERE sku = :sku AND warehouse = :w AND available >= :q;        -- 0 rows → out of stock
Flash sale (10k req/s on ONE SKU → hot row):
  - Pre-load stock into Redis; Lua script atomic DECRBY-if-available (Topic 44)
  - Successful reservations → queue → create orders asynchronously at a sustainable rate
  - Virtual waiting room / token admission at edge (Topic 78)
  - Per-user purchase limits; bot protection
  - Reconcile Redis with DB; reservations expire if payment not completed
Display stock ("Only 3 left") from cache — approximate is fine; final check at reservation.
```

### 7. Catalog & product page (read path)

```
Product page = catalog (title, images, specs) + price (pricing svc) + availability + delivery ETA
              + reviews summary + seller info + recommendations
- BFF aggregates in parallel with timeouts; optional parts degrade gracefully (Topic 77)
- Heavy caching: product docs in Redis (TTL + event invalidation), CDN for images,
  SSR/ISR pages for SEO (Next.js)
- Price & stock change often → short TTL or pushed invalidation; final values re-validated at checkout
Search: Elasticsearch with facets (brand, price range, size), typo tolerance, ranking signals
        (sales, CTR, rating, sponsored), synced from catalog/pricing/inventory via events
```

### 8. Cart
```
Cart in Redis hash (fast) + async persistence (DynamoDB/Postgres) for durability & multi-device
Guest cart (cookie/device id) merged into user cart on login
Prices in cart are indicative; re-priced at checkout ("price changed" notice)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Browsing: product page कई services (catalog, कीमत, stock, ETA, reviews) से एक साथ, cache और CDN से तेज़; search Elasticsearch से (events से sync)।
2. Cart Redis में तेज़, DB में भी सुरक्षित; login पर guest cart मिल जाता है; checkout पर कीमत दोबारा सर्वर पर।
3. Checkout saga: order PENDING → stock reserve (15 मिनट) → payment → सफल = CONFIRMED; फ़ेल = stock वापस, order cancel।
4. Oversell रोकना: `UPDATE ... WHERE available >= q`; flash sale में Redis Lua से atomic घटाना + waiting room + प्रति-यूज़र सीमा।
5. Order events Kafka में → warehouse, notifications, analytics, seller payouts; रोज़ gateway से reconciliation।

---

## 🟡 Real World Example

**Amazon** — pioneered service-oriented e-commerce. The product detail page aggregates dozens of services within strict latency budgets. The Dynamo paper came from making the shopping cart always writable (AP).

**Flipkart Big Billion Days** — handles massive spikes with months of capacity planning, a queue-based order intake for hot deals, inventory reservation systems, rate limiting and waiting rooms, and graceful degradation of non-critical widgets.

**Myntra / Meesho / Nykaa** — use Elasticsearch-based search with rich facets, Redis-heavy caching for catalog, and event-driven order pipelines on Kafka.

**Flash sale failures** — early Indian smartphone flash sales (2014–2015, e.g. Xiaomi on Flipkart) famously sold out in seconds amid site slowdowns, which pushed adoption of registration-based sales, waiting rooms and token systems.

## 🟡 Real Example Hindi में
Amazon का product page दर्जनों services से कुछ milliseconds में बनता है; Dynamo paper cart को हमेशा चालू रखने के लिए बना था।
Flipkart बिग बिलियन डेज़ के लिए महीनों पहले तैयारी करता है — hot deals के लिए queue, stock reservation, waiting room। 2014-15 के Xiaomi flash sales में साइट धीमी हुई, तब से registration और token वाली sales शुरू हुईं।

---

## 🟠 My Stack Example

### Inventory reservation with TTL (Postgres + expiry job)
```sql
CREATE TABLE inventory (sku TEXT, warehouse_id INT, available INT NOT NULL CHECK (available >= 0),
                        reserved INT NOT NULL DEFAULT 0, PRIMARY KEY (sku, warehouse_id));
CREATE TABLE reservations (id UUID PRIMARY KEY, order_id BIGINT, sku TEXT, warehouse_id INT, qty INT,
                           status TEXT DEFAULT 'HELD', expires_at TIMESTAMPTZ);
```
```js
async function reserve(tx, orderId, items) {
  for (const it of items) {
    const { rowCount } = await tx.query(
      `UPDATE inventory SET available = available - $1, reserved = reserved + $1
       WHERE sku = $2 AND warehouse_id = $3 AND available >= $1`, [it.qty, it.sku, it.warehouseId]);
    if (!rowCount) throw new AppError(409, `OUT_OF_STOCK:${it.sku}`);      // whole tx rolls back
    await tx.query(`INSERT INTO reservations(id, order_id, sku, warehouse_id, qty, expires_at)
                    VALUES (gen_random_uuid(), $1, $2, $3, $4, now() + interval '15 minutes')`,
                   [orderId, it.sku, it.warehouseId, it.qty]);
  }
}
// cron every minute: release expired HELD reservations (available += qty, reserved -= qty, status = EXPIRED)
```

### Checkout endpoint (server-side pricing, idempotent)
```js
app.post('/api/v1/checkout', authenticate, idempotent(), async (req, res) => {
  const cart = await cartSvc.get(req.user.id);
  const priced = await pricing.quote(cart, req.body.couponCode, req.body.addressId);   // never trust client totals
  if (!(await logistics.serviceable(req.body.addressId, cart))) return res.status(422).json({ error: 'NOT_SERVICEABLE' });
  const order = await withTx(pool, async (tx) => {
    const o = await createOrder(tx, req.user.id, priced, 'PENDING_PAYMENT');
    await reserve(tx, o.id, priced.items);
    await outbox(tx, 'OrderCreated', { orderId: o.id, amount: priced.total });
    return o;
  });
  const pg = await payments.createGatewayOrder(order.id, priced.total);          // Razorpay order id
  res.status(201).json({ orderId: order.id, amount: priced.total, gatewayOrderId: pg.id });
});
```

### Flash sale: Redis Lua admission + async order creation
```js
const RESERVE = `local s = tonumber(redis.call('GET', KEYS[1]) or '0')
  local bought = tonumber(redis.call('HGET', KEYS[2], ARGV[2]) or '0')
  if bought >= tonumber(ARGV[3]) then return -2 end              -- per-user limit
  if s < tonumber(ARGV[1]) then return -1 end                    -- sold out
  redis.call('DECRBY', KEYS[1], ARGV[1]); redis.call('HINCRBY', KEYS[2], ARGV[2], ARGV[1]); return s - tonumber(ARGV[1])`;

app.post('/api/v1/flash/:saleId/buy', authenticate, waitingRoomToken, async (req, res) => {
  const left = await redis.eval(RESERVE, { keys: [`flash:${req.params.saleId}:stock`, `flash:${req.params.saleId}:users`],
                                           arguments: ['1', String(req.user.id), '1'] });
  if (left === -1) return res.status(409).json({ error: 'SOLD_OUT' });
  if (left === -2) return res.status(409).json({ error: 'LIMIT_REACHED' });
  await flashOrders.add('create', { saleId: req.params.saleId, userId: req.user.id }, { jobId: `${req.params.saleId}:${req.user.id}` });
  res.status(202).json({ status: 'RESERVED', payWithinSeconds: 600 });            // client proceeds to payment
});
```

### Product page aggregation in BFF (graceful)
```js
const [product, price, stock, eta, reviews] = await Promise.allSettled([
  catalog.get(sku), pricing.get(sku), opt(inventory.status(sku), 150, 'UNKNOWN'),
  opt(logistics.eta(sku, pincode), 200, null), opt(reviewsSvc.summary(sku), 200, null),
]);
```

### Next.js PDP with ISR (SEO + speed)
```tsx
export const revalidate = 300;                        // regenerate product HTML every 5 min
export default async function Product({ params }) {
  const p = await fetch(`${API}/catalog/${params.sku}`, { next: { tags: [`product-${params.sku}`] } }).then(r => r.json());
  return <ProductView product={p} />;                 // price/stock fetched client-side (fresh) or streamed
}
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you prevent overselling inventory?**
A1: Check and decrement stock atomically at reservation time: a conditional update (`UPDATE ... SET available = available - q WHERE available >= q`) in the inventory DB, or an atomic Redis Lua script for hot flash-sale SKUs. Reserve stock with a TTL when the order is created, and commit the reservation on successful payment or release it on failure or expiry. Never rely on the stock shown on product pages (cached and approximate). Reconcile the Redis and DB counts.

**Q2: Walk through the checkout process across services.**
A2: The BFF or checkout service re-prices the cart on the server (pricing, coupons, tax, shipping) and checks serviceability. It creates an order in PENDING_PAYMENT with an idempotency key, reserves inventory (TTL), and creates a gateway payment order. The client pays, and the gateway webhook or a server-side verification marks it captured. The order is confirmed, the reservation committed, and OrderConfirmed is emitted to fulfilment and notifications. On failure or timeout, compensations release stock and cancel the order. It's implemented as an orchestrated saga with an outbox, idempotent consumers and reconciliation.

**Q3: How would you design for a flash sale with 1M users trying to buy 10,000 phones at 12:00?**
A3: Pre-register users and use a virtual waiting room or token admission at the edge to let users in at a controlled rate. Cache and pre-render product pages on the CDN, and keep sale stock in Redis with atomic Lua decrements plus per-user limits and bot protection. Successful reservations go into a queue for asynchronous order creation at a sustainable DB rate, with payment windows and reservation expiry. Autoscale and pre-scale, isolate the sale path (bulkheads) from normal shopping, and degrade non-critical features. Communicate clearly ("you're in queue", "sold out").

**Q4: Which parts need strong consistency and which can be eventual?**
A4: Strong: inventory reservation and decrement, order creation and state transitions, payment and ledger, coupon redemption limits, and refunds. Eventual: catalog display, search index, displayed prices and stock badges (re-validated at checkout), reviews and ratings aggregates, recommendations, analytics, and seller dashboards. Carts can be eventually consistent with merge semantics.

**Q5: How do you keep search results in sync with catalog, price and stock changes?**
A5: Treat the catalog, pricing and inventory DBs as sources of truth, and publish change events via the outbox or CDC (Debezium) to Kafka. An indexer service builds denormalized product documents and upserts them into Elasticsearch idempotently. Stock badges may update via partial updates or be filtered at query time from a fast availability cache. For mapping changes, reindex into a new index and swap the alias. Monitor indexing lag, since a few seconds of staleness is acceptable.

---

## 🔷 Trade-offs
✅ Microservices per domain: independent scaling (search vs orders), team ownership.
❌ Distributed transactions → sagas, reconciliation; more ops.
✅ Redis inventory for flash sales: handles hot SKUs — ❌ must reconcile with DB; durability care.
✅ Cached/ISR product pages: fast & cheap — ❌ stale price/stock (validate at checkout).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SKU | Stock keeping unit (variant) | product का एक प्रकार |
| Catalog | Product information store | products की जानकारी |
| Inventory reservation | Hold stock temporarily for an order | ऑर्डर के लिए stock रोकना |
| Oversell | Selling more than available | stock से ज़्यादा बेचना |
| Checkout saga | Multi-step order/payment workflow | ऑर्डर-पेमेंट का कई-कदम flow |
| PDP | Product detail page | product पेज |
| Facets | Filter counts in search | search के filters |
| Flash sale | Limited stock, huge spike | सीमित stock, भारी भीड़ |
| Waiting room | Queue users before entry | अंदर से पहले लाइन |
| Reconciliation | Matching orders vs payments | ऑर्डर और पेमेंट मिलाना |

---

## ⚡ 3-Line Summary
**English:**
1. Split into catalog, search, pricing, cart, inventory, order/checkout, payment, logistics, notification services; browsing served from CDN/cache/search.
2. Checkout = saga: server-side pricing → order PENDING → reserve stock (TTL) → payment → confirm or compensate; idempotency + reconciliation.
3. Prevent oversell with atomic conditional updates (Redis Lua for flash sales) plus waiting rooms, per-user limits and async order intake.

**Hindi:**
1. Catalog, search, pricing, cart, inventory, order, payment, logistics अलग services; browsing CDN/cache/search से।
2. Checkout saga: सर्वर पर कीमत → order PENDING → stock reserve → payment → पक्का या वापस; idempotency + reconciliation।
3. Oversell रोकने को atomic update (flash sale में Redis Lua), waiting room, प्रति-यूज़र सीमा और queue।

---

## ➡️ Next Topic Suggestion
**119. Payment System** — The most correctness-critical part of e-commerce: design a payment system with gateways, UPI and cards, idempotency, ledgers, webhooks, refunds and reconciliation.
