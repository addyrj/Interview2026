# 291. Build Payment API (Stripe/Razorpay)
# हिंदी में: Payment API (Stripe/Razorpay) कैसे बनायें

---

## 🔵 Simple Definition (English)
A **payment API** integrates with a payment gateway (Stripe, Razorpay) to create orders, collect payments securely (card/UPI/wallet), verify payment status via **webhooks**, and update your own order/wallet state — all while never touching raw card data directly (PCI compliance is offloaded to the gateway).

## 🔵 सरल परिभाषा (Hindi)
**Payment API** एक payment gateway (Stripe, Razorpay) से integrate होकर orders बनाता है, payment securely collect करता है (card/UPI/wallet), **webhooks** से payment status verify करता है, और अपना order/wallet state update करता है — raw card data कभी खुद handle नहीं करता (PCI compliance gateway पर offload होती है)।

---

## 🔴 Problem it Solves
Handling card numbers yourself means massive PCI-DSS compliance burden, security risk, and fraud liability. Also, payments are inherently async and unreliable (network drops mid-transaction) — your server needs a reliable way to know "did the money actually arrive?" independent of whether the client's browser tab stayed open. Gateways + webhooks solve both.

## 🔴 यह क्यों बना? (Hindi)
खुद card numbers handle करना PCI-DSS compliance burden, security risk, fraud liability लाता है। साथ ही payments inherently async और unreliable होते हैं (network बीच में drop हो सकता है) — server को reliably पता होना चाहिए "पैसा actually आया या नहीं" चाहे client का browser tab बंद हो जाए। Gateway + webhooks दोनों problems solve करते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Client requests checkout → your server creates an **order** on the gateway (Razorpay `orders.create` / Stripe `PaymentIntent.create`) with amount + currency, stores it as `pending` in your DB.
Step 2 → Server returns `orderId`/`client_secret` to frontend; frontend uses the gateway's JS SDK to collect card/UPI details and confirm payment — card data never touches your server.
Step 3 → Gateway processes payment with the bank/network, then calls YOUR server's **webhook** endpoint with the result (`payment.captured`, `payment.failed`).
Step 4 → Server verifies the webhook signature (critical!) to ensure it really came from the gateway, not a forged request.
Step 5 → Server updates order status in DB idempotently (checking `paymentId` hasn't been processed before) and triggers downstream (send receipt, release order to kitchen, etc).
Step 6 → Frontend polls or gets a websocket push once the webhook has updated order state, showing "Payment Successful".

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Client checkout request करता है → server gateway पर **order** बनाता है (Razorpay `orders.create` / Stripe `PaymentIntent.create`) amount+currency के साथ, DB में `pending` status से store करता है।
Step 2 → Server `orderId`/`client_secret` frontend को देता है; frontend gateway का JS SDK use करके card/UPI details collect + confirm करता है — card data कभी server तक नहीं आता।
Step 3 → Gateway bank/network से payment process करता है, फिर आपके server के **webhook** endpoint को result भेजता है (`payment.captured`, `payment.failed`)।
Step 4 → Server webhook signature verify करता है (बहुत ज़रूरी!) ताकि confirm हो यह genuine gateway से आया है, forged request नहीं।
Step 5 → Server DB में order status idempotently update करता है (check करता है कि यह `paymentId` पहले process नहीं हुआ) और downstream trigger करता है (receipt भेजना, kitchen को order release करना)।
Step 6 → Frontend webhook से update होने के बाद poll या websocket push से "Payment Successful" दिखाता है।

---

## 🟡 Real World Example
**Razorpay + Swiggy**: User taps "Pay ₹450". Swiggy backend creates a Razorpay order, frontend opens Razorpay Checkout (collects UPI/card — PCI scope stays with Razorpay). User completes UPI payment in their bank app. Razorpay sends a webhook `payment.captured` to Swiggy's server; Swiggy verifies the signature with its webhook secret, marks the order "paid", and pushes the order to the restaurant's kitchen dashboard — all without Swiggy ever seeing card/UPI credentials.

## 🟡 Real Example Hindi mein
**Razorpay + Swiggy**: User "₹450 Pay" दबाता है। Swiggy backend Razorpay order बनाता है, frontend Razorpay Checkout खोलता है (UPI/card collect — PCI scope Razorpay के पास रहता है)। User अपने bank app में UPI payment complete करता है। Razorpay Swiggy के server को `payment.captured` webhook भेजता है; Swiggy signature verify करके order "paid" mark करता है और restaurant kitchen dashboard पर order भेजता है — Swiggy ने कभी card/UPI credentials नहीं देखे।

---

## 💻 Code Example — Basic

```javascript
// payment-basic.js
// Simulated payment order creation + webhook handling (no real gateway, demonstrates the FLOW)
// Run: node payment-basic.js
const crypto = require('crypto');

// In-memory "DB"
const orders = new Map();

// Fake "gateway secret" shared between your server and the gateway (set in dashboard + env var)
const WEBHOOK_SECRET = 'whsec_test_123';

// Step 1: Create an order (like Razorpay orders.create)
function createOrder(amountInPaise, currency = 'INR') {
  const orderId = 'order_' + crypto.randomBytes(6).toString('hex');
  orders.set(orderId, { amount: amountInPaise, currency, status: 'created' });
  console.log(`Order created: ${orderId} for ₹${amountInPaise / 100}`);
  return orderId;
}

// Step 2: Simulate the gateway signing a webhook payload with HMAC-SHA256
function simulateGatewaySignature(payload) {
  return crypto.createHmac('sha256', WEBHOOK_SECRET).update(JSON.stringify(payload)).digest('hex');
}

// Step 3: Verify webhook signature on your server — NEVER trust an unsigned webhook
function verifyWebhookSignature(payload, signature) {
  const expected = crypto.createHmac('sha256', WEBHOOK_SECRET).update(JSON.stringify(payload)).digest('hex');
  // Use timing-safe comparison to avoid timing attacks
  return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(signature));
}

// Step 4: Handle the incoming webhook event
function handleWebhook(payload, signature) {
  if (!verifyWebhookSignature(payload, signature)) {
    console.log('Invalid webhook signature — REJECTED');
    return;
  }
  const order = orders.get(payload.orderId);
  if (!order) return console.log('Unknown order');

  if (payload.event === 'payment.captured') {
    order.status = 'paid';
    console.log(`Order ${payload.orderId} marked PAID`);
  } else if (payload.event === 'payment.failed') {
    order.status = 'failed';
    console.log(`Order ${payload.orderId} marked FAILED`);
  }
}

// --- Demo flow ---
const orderId = createOrder(45000); // ₹450.00
const webhookPayload = { orderId, event: 'payment.captured', paymentId: 'pay_xyz1' };
const signature = simulateGatewaySignature(webhookPayload); // gateway would compute & send this
handleWebhook(webhookPayload, signature);
console.log(orders.get(orderId));
```

## 💻 Code Example — Advanced

```javascript
// payment-advanced.js
// Production-style Razorpay integration with Express, idempotency, and raw-body signature verification
// npm i express razorpay
const crypto = require('crypto');
const Razorpay = require('razorpay'); // real Razorpay SDK

const razorpay = new Razorpay({
  key_id: process.env.RAZORPAY_KEY_ID,
  key_secret: process.env.RAZORPAY_KEY_SECRET,
});

// Simulated DB with idempotency tracking
const db = {
  orders: new Map(),
  processedPayments: new Set(), // tracks paymentIds already handled -> prevents double-processing
};

// 1. Create a Razorpay order
async function createPaymentOrder(amountRupees, receiptId) {
  const order = await razorpay.orders.create({
    amount: amountRupees * 100, // Razorpay expects paise
    currency: 'INR',
    receipt: receiptId,
  });
  db.orders.set(order.id, { status: 'created', amount: amountRupees });
  return order; // { id, amount, currency, ... } -> send order.id + key_id to frontend
}

// 2. Verify webhook signature (Razorpay signs with HMAC-SHA256 using webhook secret)
function isValidWebhookSignature(rawBody, signatureHeader, webhookSecret) {
  const expected = crypto.createHmac('sha256', webhookSecret).update(rawBody).digest('hex');
  // timingSafeEqual requires equal-length buffers, guard against length mismatch throwing
  if (expected.length !== signatureHeader.length) return false;
  return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(signatureHeader));
}

// 3. Process webhook event idempotently
async function processWebhookEvent(event) {
  const paymentId = event.payload.payment.entity.id;

  // Idempotency guard: if we've already processed this paymentId, skip (webhooks can be sent MORE THAN ONCE)
  if (db.processedPayments.has(paymentId)) {
    console.log(`Payment ${paymentId} already processed, skipping (idempotent)`);
    return;
  }

  const orderId = event.payload.payment.entity.order_id;
  const order = db.orders.get(orderId);
  if (!order) throw new Error(`Unknown order ${orderId}`);

  if (event.event === 'payment.captured') {
    order.status = 'paid';
    db.processedPayments.add(paymentId);
    // Trigger downstream: send receipt email, release goods, update ledger
    console.log(`Order ${orderId} PAID via payment ${paymentId}`);
  } else if (event.event === 'payment.failed') {
    order.status = 'failed';
    db.processedPayments.add(paymentId);
    console.log(`Order ${orderId} payment FAILED`);
  }
}

module.exports = { createPaymentOrder, isValidWebhookSignature, processWebhookEvent };
```

---

## 🟠 Express.js Integration

```javascript
// server.js — critical: webhook route needs the RAW body, not JSON-parsed, for signature verification
const express = require('express');
const { createPaymentOrder, isValidWebhookSignature, processWebhookEvent } = require('./payment-advanced');

const app = express();

// Normal routes use JSON parsing
app.use('/checkout', express.json());

app.post('/checkout/order', async (req, res) => {
  const { amount, receiptId } = req.body;
  const order = await createPaymentOrder(amount, receiptId);
  res.json({ orderId: order.id, amount: order.amount, keyId: process.env.RAZORPAY_KEY_ID });
});

// IMPORTANT: webhook route must use express.raw() — Razorpay/Stripe sign the EXACT raw bytes,
// and re-serializing parsed JSON would produce a different byte string, breaking signature check
app.post('/webhooks/razorpay', express.raw({ type: 'application/json' }), (req, res) => {
  const signature = req.headers['x-razorpay-signature'];
  const rawBody = req.body; // Buffer, not parsed object

  if (!isValidWebhookSignature(rawBody, signature, process.env.RAZORPAY_WEBHOOK_SECRET)) {
    return res.status(400).json({ error: 'Invalid signature' });
  }

  const event = JSON.parse(rawBody.toString());
  processWebhookEvent(event).catch(console.error);

  // Always respond 200 quickly — gateway retries on non-200, do heavy work async
  res.status(200).json({ received: true });
});

app.listen(3000, () => console.log('Payment API on :3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Marking an order "paid" based on the frontend's success callback alone
✅ Correct: Only trust the server-side webhook as the source of truth — the frontend callback can be faked/manipulated or lost on network drop

```javascript
// Wrong — client could spoof this call or close tab before it fires
app.post('/payment-success', (req, res) => {
  markOrderPaid(req.body.orderId); // NEVER trust client-reported success
});

// Right — only the signed webhook confirms payment
app.post('/webhooks/razorpay', express.raw({ type: 'application/json' }), handleWebhook);
```

❌ Mistake 2: Using `express.json()` globally before the webhook route
✅ Correct: Apply `express.raw()` specifically to the webhook route BEFORE any global JSON parsing middleware consumes the body

```javascript
// Wrong — global JSON parser consumes/re-serializes body, breaking signature verification
app.use(express.json());
app.post('/webhooks/razorpay', handleWebhook); // body already parsed+mutated!

// Right — raw body parsing scoped to webhook route only, registered before global json()
app.post('/webhooks/razorpay', express.raw({ type: 'application/json' }), handleWebhook);
app.use(express.json()); // other routes
```

---

## 🧠 Tricky Interview Question

```javascript
// Gateway retries a webhook delivery (network blip) -> same event arrives TWICE
processWebhookEvent({ event: 'payment.captured', payload: { payment: { entity: { id: 'pay_1', order_id: 'order_1' } } } });
processWebhookEvent({ event: 'payment.captured', payload: { payment: { entity: { id: 'pay_1', order_id: 'order_1' } } } });
```
Answer: Without an idempotency check, the second call would re-trigger downstream side effects (sending a second receipt email, double-crediting a wallet, re-releasing inventory) even though it's the SAME payment. The advanced example guards this with `db.processedPayments.has(paymentId)` — webhooks are "at-least-once delivery" by design (gateways retry on timeout/non-200), so your handler MUST be idempotent, keyed by the gateway's unique payment/event ID, not just the order ID.

---

## ⚫ Interview Questions + Answers

Q1: Why must webhook signature verification use the raw request body?
A1: The gateway computes the HMAC signature over the exact bytes it sent. If Express (or any middleware) parses the body to JSON and you re-serialize it to verify, whitespace/key-ordering differences produce a different byte string, making the signature mismatch even for a legitimate request. You must capture and verify against the untouched raw bytes.

Q2: What's the difference between a payment "authorized" and "captured" state (Stripe/Razorpay)?
A2: "Authorized" means the bank has reserved the funds but money hasn't moved yet (common for pre-auth flows like hotel bookings). "Captured" means the funds are actually transferred to the merchant. Some integrations auto-capture; others require an explicit capture API call within a time window (e.g., 5 days), useful for order-confirmation-before-charge flows.

Q3: How do you handle a payment that's captured but your server crashes before updating the DB?
A3: Design the webhook handler to be safely retried — gateways retry undelivered/failed webhooks automatically. Also implement a periodic reconciliation job that polls the gateway's API for recent payments and cross-checks against your DB for any "paid at gateway but pending in DB" mismatches, self-healing the gap.

Q4: How do you prevent a user from double-paying by clicking "Pay" twice quickly?
A4: Disable the pay button immediately on click (frontend), and more importantly, use a unique `receipt`/idempotency key per checkout attempt on the gateway's order-creation API so duplicate order-creation calls with the same key return the same order instead of creating two.

Q5: How would you implement refunds?
A5: Call the gateway's refund API with the original `paymentId` and amount (full or partial), store a `refund` record linked to the payment, and listen for a `refund.processed` webhook to confirm completion since refunds can also be asynchronous (especially for bank transfers/UPI).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need to accept real money payments without PCI-DSS card-storage burden
- You need reliable "did payment succeed" state via webhooks, not just frontend callbacks

❌ Avoid when:
- Building a pure sandbox/demo with no real transactions — mock the gateway rather than wiring real keys
- Internal credit systems where a simpler ledger without external gateway suffices

---

## 📊 Visual Diagram
```
 Frontend          Your Server            Gateway (Razorpay/Stripe)        Bank/UPI
    │   create order    │                         │                          │
    │───────────────────▶  orders.create()  ──────▶                          │
    │◀── orderId ────────│◀────────────────────────                          │
    │  checkout UI (SDK, no card data touches your server)                   │
    │─────────────────────────────────────────────▶ confirm payment ─────────▶
    │                    │                         │◀──── bank result ───────│
    │                    │◀──── webhook (signed) ───│
    │                    │ verify signature          
    │                    │ idempotent DB update      
    │◀── poll/socket ────│ "Payment Successful"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Webhook | Gateway-initiated callback to your server | Gateway से server को callback |
| Idempotency | Processing same event twice = same effect once | दो बार process करने पर भी effect एक बार |
| PCI-DSS | Card data security compliance standard | Card data security standard |
| Capture | Actually transferring reserved funds | Reserved funds को transfer करना |
| HMAC signature | Cryptographic proof of authenticity | Authenticity का cryptographic proof |

---

## ⚡ 3-Line Summary
English: Payment APIs delegate card handling to a gateway (Stripe/Razorpay), create an order, let the gateway's SDK collect payment details, and treat the signed webhook — not the frontend callback — as the source of truth for payment success. Idempotent webhook processing and raw-body signature verification are non-negotiable.
Hindi: Payment APIs card handling gateway (Stripe/Razorpay) को देते हैं, order बनाते हैं, gateway का SDK payment details collect करता है, और payment success का source of truth signed webhook होता है — frontend callback नहीं। Idempotent webhook processing और raw-body signature verification ज़रूरी हैं।

---

## ➡️ Next Topic
**292. Build OTP System** — rate limiting, expiry, and secure verification flows.
