# P08. Amazon/Flipkart — Product Page + Cart + Checkout (End-to-End Design)
# हिंदी में: Amazon/Flipkart का पूरा ख़रीदारी रास्ता — Product page (तेज़, SEO वाला, सही कीमत और stock), Cart (हर device पर एक जैसा), और Checkout (पता, delivery date, UPI/card/EMI/COD, सही order) — Big Billion Days जैसी flash sale की भीड़ में भी

---

## 🔵 Simple Definition (English)
Design the e-commerce **purchase funnel** end to end across web (Next.js) and mobile (React Native):
- **Product Detail Page (PDP)**:
  - static-ish content (title, images, specs, description) rendered fast and **SEO-friendly** (SSR/ISR, structured data)
  - **dynamic** parts (price, offers, stock, delivery date for the user's **pincode**, seller "buy box") fetched fresh
  - lazy-loaded reviews, Q&A and recommendations
- **Cart**: a **server-side cart** synced across devices, a guest cart merged on login, continuous **repricing** (offers, coupons, fees), stock warnings, save for later.
- **Checkout**:
  - address and delivery-slot selection
  - payment (UPI, cards, net banking, EMI/BNPL, wallets, **COD**)
  - **inventory reservation**, **idempotent order placement**, payment confirmation via PSP webhooks, and order confirmation
- **Flash sales** (Big Billion Days, Prime Day): queueing/waiting rooms, atomic inventory, cache pre-warming, graceful degradation.
Backend detail is in **Topic 118 (E-Commerce)** and **119 (Payments)**. This file covers the client-to-backend flow and UX/perf concerns.

## 🔵 सरल परिभाषा (Hindi)
E-commerce का ख़रीदारी रास्ता web और mobile पर: PDP — स्थिर हिस्सा (नाम, फ़ोटो, specs) तेज़ और SEO वाला (SSR/ISR), बदलने वाला हिस्सा (कीमत, offers, stock, आपके pincode पर delivery date, seller) ताज़ा, reviews/recommendations बाद में; Cart — सर्वर पर, हर device पर एक जैसा, guest cart login पर मिल जाए, कीमत बार-बार दोबारा गिनी जाए; Checkout — पता, delivery slot, भुगतान (UPI, card, EMI, COD), stock आरक्षित, order एक ही बार, PSP webhook से पुष्टि; Flash sale — कतार (waiting room), stock की atomic गिनती, cache पहले से गर्म।

---

## 🔴 Problem it Solves
The funnel is where revenue happens, and it fails in expensive ways:
- **Slow PDPs lose sales.** A widely cited Amazon finding linked every 100 ms of latency to about 1% of sales, and mobile users on 4G with mid-range phones feel heavy pages most.
- **Wrong price or stock** shown on the PDP or cart means angry users, legal or regulatory issues, and cancellations.
- **Overselling** in flash sales: 1 lakh users trying to buy 10,000 phones at 12:00:00 means the database melts and some customers get orders that can't be fulfilled.
- **Double orders or double charges** from retries and back-button taps.
- **Payment drop-offs**: UPI pending states, OTP failures and app switches.
- **Cart inconsistencies** across app and web, and lost guest carts after login.
- **SEO**: product pages must be crawlable, with rich results (price, rating), for organic traffic.

## 🔴 यह क्यों बना? (Hindi)
यही रास्ता पैसा कमाता है और यहीं महँगी ग़लतियाँ होती हैं: धीमा PDP = कम बिक्री (Amazon की मशहूर बात — हर 100 ms देरी ≈ 1% बिक्री कम); PDP या cart में ग़लत कीमत/stock = नाराज़ यूज़र और cancellations; flash sale में 1 लाख लोग 10,000 फ़ोन पर 12:00:00 बजे — DB बैठ जाए और ज़्यादा orders बिक जाएँ (overselling); retry या back बटन से दो बार order/charge; UPI pending, OTP fail; app और web का cart अलग; और SEO के लिए product pages crawl होने चाहिए।

---

## 🟢 How it Works — Step by Step

### 1. Requirements & scale

```
PDP: images gallery (zoom/swipe), variants (size/colour/storage), price & MRP & discount, bank offers,
     stock & delivery ETA by pincode, seller selection, specs, reviews & ratings, Q&A, recommendations,
     add to cart / buy now, wishlist, share; SEO + rich snippets
Cart: add/update/remove, multi-device sync, guest→user merge, coupons, fees, save for later, price/stock alerts
Checkout: address book, serviceability, delivery slots, payment options (UPI/cards/EMI/COD/wallet),
          order summary, place order, confirmation, failure recovery
Non-functional: PDP LCP < 2.5 s on 4G mobile, checkout success high, no oversell, idempotent orders,
          flash sale: 50–100× normal traffic for minutes
```

### 2. PDP rendering strategy (web)

```
Split by volatility:
  STATIC-ish (changes rarely): title, images, specs, description, breadcrumbs
      → ISR (revalidate minutes) + on-demand revalidation on catalog update → CDN → great LCP & SEO
  DYNAMIC (per user/pincode/second): price, offers, stock, delivery ETA, seller buy box, cart count
      → streamed server component (Suspense) or client fetch from a low-latency "offer/price" API
      (cached seconds), never cached in shared HTML for personalized bits
  LAZY (below the fold): reviews, Q&A, similar products → loaded on scroll (IntersectionObserver)
Structured data: JSON-LD Product (name, image, offers.price, availability, aggregateRating) → rich results
LCP: hero image preloaded (priority), responsive srcset; JS budget small; images CDN AVIF/WebP (F17)
```

### 3. PDP on mobile (RN)

```
Screen shell renders instantly from list-page data passed in (title, image, price) → then full PDP fetch
Image gallery: horizontal pager, pinch zoom (Reanimated + Gesture Handler), prefetch next images
Sticky bottom bar: price + "Add to cart" / "Buy now" (always reachable)
Pincode/location remembered (MMKV) → delivery ETA shown immediately
Deep links from ads/shares open PDP directly (M11); server-driven sections for offers/banners
```

### 4. Cart

```
Server-side cart (source of truth) keyed by user (or guest token); client keeps optimistic copy
- Add: POST /cart/items {sku, qty, sellerId} (idempotency key) → returns repriced cart
- Every read/write → REPRICE: current price per seller, offers/coupons, delivery fee, platform fee, GST
  → surface changes ("Price dropped ₹500", "Only 2 left", "Out of stock — moved to saved")
- Guest cart (device token) → on login: merge (sum quantities, cap by stock & per-user limits)
- Multi-device: version number on cart; clients refetch on focus; conflicts resolved server-side (ops-based)
- Storage: Redis (hot) + DB (durable); TTL for abandoned guest carts; analytics for cart abandonment
```

### 5. Checkout & order placement (correctness)

```
1. POST /checkout/sessions {cartId} → validates serviceability, stock, prices → session with
   locked price summary (valid ~10–15 min) + available payment methods + delivery slots
2. Select address & slot → recompute fees/ETA
3. POST /orders {checkoutSessionId, paymentMethod} + Idempotency-Key
     → create order PAYMENT_PENDING
     → RESERVE inventory (soft hold with TTL, e.g., 10 min) — atomic decrement per SKU/warehouse
     → create payment with PSP (UPI intent/collect, card 3DS, EMI, wallet) or COD → CONFIRMED directly
4. Client completes payment (UPI app / 3DS OTP) → PSP webhook (source of truth) → order CONFIRMED →
   reservation becomes permanent (allocated) → confirmation screen, email/SMS/push
5. Payment fails/abandoned → reservation expires (TTL) → stock released; order FAILED/cancelled; user can retry
   with the same order (new payment attempt) rather than a duplicate order
```

### 6. Flash sale (Big Billion Days) design

```
Before: pre-warm CDN & caches (PDP static content, images), pre-scale services, load test, freeze deploys,
        feature flags for degradation (turn off recommendations/reviews widgets if needed)
Traffic control: virtual WAITING ROOM / queue (tokens issued in order, admitted at sustainable rate);
        rate limits per user/device; bot protection (attestation, CAPTCHA, purchase limits per user)
Inventory: hot SKUs in Redis with atomic Lua decrement (check stock & per-user limit in one step) →
        winners get a reservation token → async order creation via queue → DB write-behind
        → never let DB be the hot counter for 1 lakh concurrent buyers
UX: countdown synced to server time, "You're in line — 2 min", clear "Sold out" quickly, no infinite spinners
After: reconcile Redis reservations with DB orders; release unpaid reservations
```

### 7. Payments (India specifics)

```
UPI (intent on Android, collect/QR), cards (RBI tokenization — no raw card storage; 3DS/OTP), net banking,
EMI/no-cost EMI, BNPL, wallets, COD (with COD fee/limits, OTP on delivery for high value), gift cards
Pending UPI: show "Waiting for payment confirmation", poll/WS up to minutes, auto-reconcile via webhook
Bank offers ("10% off with HDFC cards"): eligibility needs BIN check at payment step → final price adjusts
```

## 🟢 कैसे काम करता है? (Hindi)
1. PDP को बदलाव की रफ़्तार से बाँटो: नाम/फ़ोटो/specs → ISR + CDN (तेज़ LCP, SEO, JSON-LD rich snippets); कीमत/offers/stock/pincode ETA/seller → ताज़ा API या streaming (shared HTML में cache नहीं); reviews/Q&A/similar → scroll पर।
2. Mobile PDP: list से मिला नाम/फ़ोटो/कीमत तुरंत दिखाओ, फिर पूरा डेटा; zoom वाली gallery, नीचे sticky "Add to cart", pincode याद रखो, deep link से सीधे PDP।
3. Cart सर्वर पर (हर device पर एक), हर बार repricing (कीमत, coupon, fees, GST) और बदलाव दिखाओ ("कीमत ₹500 घटी", "सिर्फ़ 2 बचे"); guest cart login पर merge; version से multi-device।
4. Checkout: session में कीमत 10–15 मिनट lock → order (Idempotency-Key) PAYMENT_PENDING → stock का TTL वाला आरक्षण → PSP से भुगतान → webhook से CONFIRMED; fail/छोड़ने पर TTL से stock वापस, उसी order पर दोबारा कोशिश (नया order नहीं)।
5. Flash sale: पहले से cache गर्म और scale, waiting room कतार, per-user सीमा और bot सुरक्षा; hot SKU का stock Redis में Lua से atomic घटाओ (DB नहीं), विजेताओं को reservation token, order queue से async; सर्वर समय वाला countdown, जल्दी "Sold out"; बाद में reconcile।

---

## 🟡 Real World Example

**Flipkart Big Billion Days** — Flipkart prepares for months: capacity planning, load tests, deploy freezes and war rooms. Its engineering talks describe queue-based traffic shaping, inventory handling for hot deals, and mobile-first performance work (Flipkart Lite PWA history), since most Indian shoppers buy on mobile.

**Amazon's latency research** — the often-quoted finding that every 100 ms of latency cost about 1% of sales (attributed to Amazon experiments by Greg Linden and others) is why PDP performance is treated as a revenue metric industry-wide.

**Indian payments** — RBI's card-on-file tokenization rules (effective 2022) mean merchants store network tokens instead of card numbers. UPI dominates checkout, which is why flows handle intent apps, collect requests and pending states with webhook reconciliation.

**Rich results SEO** — e-commerce sites (Amazon, Flipkart, Myntra, Nykaa) use structured Product data so Google shows price, availability and ratings in results, which drives organic traffic to SSR/ISR PDPs.

## 🟡 Real Example Hindi में
Flipkart Big Billion Days के लिए महीनों पहले से तैयारी करता है — capacity planning, load tests, deploy freeze, war rooms, कतार से traffic नियंत्रण और hot deals के stock की ख़ास व्यवस्था; ज़्यादातर भारतीय ख़रीदार mobile पर।
Amazon की मशहूर बात — हर 100 ms देरी ≈ 1% बिक्री कम — इसलिए PDP की speed revenue metric है; RBI के card tokenization नियम (2022) से merchants card नंबर नहीं, token रखते हैं; UPI checkout पर हावी है; structured Product data से Google में कीमत, उपलब्धता और rating दिखती है।

---

## 🟠 My Stack Example

### Next.js PDP: ISR static shell + streamed dynamic price/stock + JSON-LD
```tsx
// app/p/[slug]/page.tsx
import { Suspense } from 'react';
export const revalidate = 600;                                            // static content; on-demand revalidateTag on catalog change

export default async function PDP({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const product = await getCatalogProduct(slug);                          // fetch(..., { next: { tags: [`product-${slug}`] } })
  const jsonLd = { '@context': 'https://schema.org', '@type': 'Product', name: product.title, image: product.images.map((i) => i.url),
                   brand: product.brand, aggregateRating: { '@type': 'AggregateRating', ratingValue: product.rating, reviewCount: product.reviewCount } };
  return (
    <main>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c') }} />
      <Gallery images={product.images} />                                  {/* first image priority (LCP) */}
      <h1>{product.title}</h1>
      <Suspense fallback={<PriceSkeleton />}>
        <LivePriceAndStock sku={product.defaultSku} />                      {/* dynamic, per pincode — streamed */}
      </Suspense>
      <Specs specs={product.specs} />
      <LazySection><Reviews productId={product.id} /></LazySection>          {/* client loads on scroll */}
    </main>
  );
}

// components/LivePriceAndStock.tsx (Server Component, dynamic)
import { cookies } from 'next/headers';
export async function LivePriceAndStock({ sku }: { sku: string }) {
  const pincode = (await cookies()).get('pincode')?.value ?? '560001';
  const o = await fetch(`${OFFER_API}/offers/${sku}?pincode=${pincode}`, { cache: 'no-store' }).then((r) => r.json());
  return (<section aria-label="Price and delivery">
    <p><strong>₹{(o.price / 100).toLocaleString('en-IN')}</strong> <s>₹{(o.mrp / 100).toLocaleString('en-IN')}</s> {o.discountPct}% off</p>
    <p>{o.inStock ? `Delivery by ${o.deliveryDate} to ${pincode}` : 'Currently out of stock'}</p>
    <AddToCartButton sku={sku} sellerId={o.sellerId} disabled={!o.inStock} />   {/* client island */}
  </section>);
}
```

### Cart API with repricing and guest merge (Node)
```js
app.post('/cart/items', identify, idempotent, async (req, res) => {
  const cartId = req.user ? `u:${req.user.id}` : `g:${req.guestToken}`;
  const { sku, qty, sellerId } = req.body;
  await carts.addItem(cartId, { sku, qty, sellerId });                     // op-based (no lost updates)
  res.json(await reprice(cartId, req.pincode));
});

app.post('/auth/login/complete', async (req, res) => {
  const user = await finishLogin(req);
  if (req.guestToken) await carts.merge(`g:${req.guestToken}`, `u:${user.id}`, { capByStock: true, perUserLimits: true });
  res.json({ user, cart: await reprice(`u:${user.id}`, req.pincode) });
});

async function reprice(cartId, pincode) {
  const cart = await carts.get(cartId);
  const offers = await offerSvc.bulk(cart.items.map((i) => ({ sku: i.sku, sellerId: i.sellerId, pincode })));
  const lines = cart.items.map((i, idx) => ({ ...i, unitPrice: offers[idx].price, inStock: offers[idx].stock >= i.qty, priceChanged: offers[idx].price !== i.lastSeenPrice }));
  const totals = await pricing.compute(lines, cart.coupon);               // fees, GST, coupon validation
  return { id: cartId, version: cart.version, lines, totals, warnings: buildWarnings(lines) };
}
```

### Flash-sale atomic reservation (Redis Lua)
```lua
-- KEYS[1] = stock:{sku}, KEYS[2] = bought:{sku}:{userId}   ARGV[1] = qty, ARGV[2] = perUserLimit, ARGV[3] = ttlSec
local stock = tonumber(redis.call('GET', KEYS[1]) or '0')
local bought = tonumber(redis.call('GET', KEYS[2]) or '0')
local q = tonumber(ARGV[1])
if bought + q > tonumber(ARGV[2]) then return -2 end      -- per-user limit
if stock < q then return -1 end                            -- sold out
redis.call('DECRBY', KEYS[1], q)
redis.call('INCRBY', KEYS[2], q); redis.call('EXPIRE', KEYS[2], 86400)
return 1                                                   -- reserved (caller writes reservation with TTL & enqueues order)
```
```js
const r = await redis.eval(RESERVE_LUA, 2, `stock:${sku}`, `bought:${sku}:${userId}`, 1, 2, 600);
if (r === -1) return res.status(409).json({ error: { code: 'SOLD_OUT' } });
if (r === -2) return res.status(429).json({ error: { code: 'LIMIT_REACHED' } });
await queue.publish('sale.orders', { reservationId: uuid(), sku, userId, expiresAt: Date.now() + 600_000 });   // async order creation
// Expired unpaid reservations → INCRBY stock back (sweeper job) + reconcile with DB
```

### Checkout placement (idempotent) + PSP webhook (FastAPI)
```python
@app.post("/orders")
async def place_order(body: PlaceOrder, idem: str = Header(alias="Idempotency-Key"), user=Depends(current_user)):
    if existing := await idempotency.get(user.id, idem): return existing
    session = await checkout_sessions.get_valid(body.checkout_session_id, user.id)      # locked prices, not expired
    async with db.transaction():
        order = await orders.create(user.id, session, status="PAYMENT_PENDING")
        await inventory.reserve(order.lines, ttl_minutes=10, ref=order.id)            # atomic per SKU/warehouse
    payment = await psp.create_payment(order.id, amount_paise=order.total_paise, method=body.payment_method) \
              if body.payment_method != "COD" else None
    resp = {"orderId": order.id, "payment": payment and payment.client_payload}
    await idempotency.save(user.id, idem, resp)
    return resp

@app.post("/webhooks/psp")
async def psp_webhook(request: Request):
    event = verify_psp_signature(await request.body(), request.headers)                 # never trust unsigned
    if event.type == "payment.captured":
        await orders.confirm(event.order_id)                                           # PAYMENT_PENDING → CONFIRMED (idempotent)
        await inventory.allocate(event.order_id)
    elif event.type == "payment.failed":
        await orders.mark_payment_failed(event.order_id)                               # reservation will expire
    return {"ok": True}
```

---

## ⚫ Interview Questions + Answers

**Q1: How would you render a product page for speed and SEO when price and stock change constantly?**
A1: Separate content by volatility. Serve the stable parts (title, images, specs, description) via SSG or ISR from a CDN with on-demand revalidation when the catalog changes, which gives fast LCP and full SEO with JSON-LD structured data. Fetch volatile and personalized parts (price, offers, stock, pincode-based delivery date, seller, cart count) from a low-latency offer API, streamed into the page via Suspense or loaded client-side, never baked into shared cached HTML. Lazy-load reviews, Q&A and recommendations below the fold, and preload the hero image.

**Q2: How do you prevent overselling during a flash sale?**
A2: Don't use the relational database as the hot counter. Keep hot SKU stock in Redis and reserve with an atomic script that checks stock and per-user limits and decrements in one step. Winners get a time-limited reservation and their orders are created asynchronously via a queue, while losers see "sold out" immediately. Put a waiting room or queue and rate limits in front to admit traffic at a sustainable rate, and use bot protection. Expire unpaid reservations to release stock, then reconcile Redis counts with database orders after the sale.

**Q3: How do you make "Place order" safe against double clicks and retries?**
A3: The client sends an idempotency key, generated once per checkout attempt, with the place-order request. The server stores the key with the response and returns the same order for repeated requests instead of creating new ones. Order creation, inventory reservation and payment creation also use the order ID as an idempotency reference with the PSP. Payment confirmation comes from signed PSP webhooks processed idempotently. A failed payment can be retried against the same order, and the UI disables the button and shows progress while waiting.

**Q4: How should carts work across devices and for guests?**
A4: Make the cart server-side and authoritative, keyed by user ID, or by a guest token stored on the device. Clients keep an optimistic local copy and refetch on focus. Changes are sent as operations (add 1, remove item) so edits from multiple devices combine without lost updates, and a version number detects staleness. On login, merge the guest cart into the user cart, capping quantities by stock and purchase limits. Every read reprices from current offers, coupons and fees and surfaces changes such as price drops, low stock or unavailable items.

**Q5: How do you handle UPI payments that stay "pending"?**
A5: Treat the PSP's server-side status as authoritative. After the user returns from the UPI app, show a clear "waiting for confirmation" state while polling the backend (or listening via WebSocket) for a few minutes. The backend receives signed PSP webhooks and also polls the PSP's status API for pending payments. If the payment succeeds late, confirm the order and notify the user; if it fails or times out, release the reservation and let the user retry. Daily reconciliation against PSP settlements catches mismatches, and any amount debited without an order is auto-refunded.

---

## 🔷 Trade-offs
✅ ISR + dynamic islands: fast, SEO, fresh prices — ❌ complexity of splitting data sources.
✅ Redis hot inventory: survives flash traffic — ❌ reconciliation needed; Redis as critical dependency.
✅ Waiting room: protects systems & fairness — ❌ users wait; must communicate well.
✅ Locked checkout prices: trust — ❌ short validity windows; repricing UX if expired.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| PDP | Product detail page | product का page |
| Buy box | Selected seller offer | चुना गया seller |
| Serviceability | Can deliver to pincode | pincode पर delivery संभव |
| Repricing | Recompute totals on change | कीमत दोबारा गिनना |
| Guest cart merge | Combine carts on login | login पर cart मिलाना |
| Inventory reservation | Temporary stock hold | stock अस्थायी रोकना |
| Idempotency key | Prevent duplicate orders | दोहरा order रोकना |
| PSP webhook | Payment confirmation callback | भुगतान पुष्टि |
| Waiting room | Queue for flash traffic | भीड़ की कतार |
| JSON-LD | Structured data for SEO | SEO के लिए structured डेटा |

---

## ⚡ 3-Line Summary
**English:**
1. PDP: static content via ISR/CDN with JSON-LD; volatile price/stock/ETA via fresh API or streaming; lazy reviews/recos; mobile shell from list data + sticky CTA.
2. Cart: server-side, op-based, repriced on every change, guest merge on login; checkout: locked session → idempotent order → TTL inventory reservation → PSP webhook confirmation.
3. Flash sales: waiting room, rate limits, bot defence, Redis atomic reservations with async order creation, pre-warmed caches, degradation flags and post-sale reconciliation.

**Hindi:**
1. PDP: स्थिर content ISR/CDN + JSON-LD; कीमत/stock/ETA ताज़ा API से; reviews बाद में; mobile पर तुरंत shell + sticky बटन।
2. Cart सर्वर पर, हर बदलाव पर repricing, login पर merge; checkout: lock session → idempotent order → TTL आरक्षण → webhook से पुष्टि।
3. Flash sale: waiting room, सीमाएँ, bot सुरक्षा, Redis में atomic आरक्षण, async orders, cache गर्म, बाद में reconcile।

---

## ➡️ Next Topic Suggestion
**P09. Notification Center (In-app + Push + Email)** — After the order, users need updates on every channel. Next: a unified notification platform with preferences, routing, frequency control and an in-app inbox synced across web and mobile.
