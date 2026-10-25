# 280. Build Webhook Handler
# हिंदी में: Webhook Handler बनाना

---

## 🔵 Simple Definition (English)
A **webhook handler** is an API endpoint that receives asynchronous event notifications pushed FROM a third-party service (Razorpay, Stripe, GitHub) — e.g. "payment succeeded," "subscription cancelled." Unlike normal APIs where you pull data, webhooks let the third party push data to you the instant something happens, and your handler must verify authenticity and process it reliably.

## 🔵 सरल परिभाषा (Hindi)
**Webhook handler** एक API endpoint है जो third-party service (Razorpay, Stripe, GitHub) से asynchronous event notifications receive करता है — जैसे "payment succeeded", "subscription cancelled"। Normal APIs में आप data pull करते हैं, webhooks में third party आपको event होते ही data push करती है, और handler को authenticity verify करके reliably process करना होता है।

---

## 🔴 Problem it Solves
Without webhooks, you'd have to POLL the third-party API repeatedly ("has the payment completed yet? has it completed yet?") — wasteful, slow (delay = polling interval), and often rate-limited by the provider. Webhooks invert this: the provider calls YOUR server the instant the event happens, giving near-real-time updates with zero polling overhead. The challenge webhooks introduce: your endpoint must verify the request genuinely came from the claimed provider (not a forged request), handle duplicate deliveries (providers often retry if they don't get a fast 200 response), and process events reliably even if your server is briefly down.

## 🔴 यह क्यों बना? (Hindi)
Webhooks के बिना, आपको third-party API बार-बार POLL करना पड़ता ("payment complete हुआ क्या?") — wasteful, slow, और अक्सर rate-limited। Webhooks इसे invert करते हैं: provider event होते ही आपके server को call करता है, near-real-time updates बिना polling overhead के। चुनौती: आपके endpoint को verify करना होता है कि request genuinely claimed provider से आई है, duplicate deliveries handle करना होता है, और reliably process करना होता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Third-party service sends a `POST` request to your registered webhook URL whenever a relevant event occurs, with event data in the body.
Step 2 → The request includes a **signature header** (e.g. `X-Razorpay-Signature`, `Stripe-Signature`) — an HMAC hash computed using a shared secret, over the raw request body.
Step 3 → Your handler recomputes the same HMAC using YOUR copy of the shared secret, and compares it to the received signature — if they don't match, REJECT the request (it's forged or tampered).
Step 4 → **Critical gotcha**: signature verification requires the RAW, unparsed request body (exact bytes as sent) — if Express's `express.json()` middleware has already parsed it into an object, the raw bytes are lost and signature verification fails. Use `express.raw()` or capture the raw body specifically for the webhook route.
Step 5 → Respond with `200 OK` QUICKLY (within a few seconds) — providers interpret timeout/non-200 as failure and will RETRY, potentially causing duplicate processing.
Step 6 → Do the actual heavy processing (updating DB, sending confirmation emails) ASYNCHRONOUSLY (e.g. enqueue a background job) AFTER acknowledging receipt, so the webhook response isn't blocked by slow downstream work.
Step 7 → Handle **idempotency**: store the event's unique ID and check if you've already processed it before, since providers may deliver the same event more than once (at-least-once delivery guarantee, not exactly-once).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Third-party service event होने पर आपके registered webhook URL पर `POST` request भेजती है।
Step 2 → Request में **signature header** होता है — shared secret से computed HMAC hash।
Step 3 → आपका handler same HMAC recompute करे अपने secret से, compare करे — न मिले तो REJECT।
Step 4 → **Critical gotcha**: signature verification के लिए RAW body चाहिए — `express.json()` parse कर दे तो raw bytes खो जाते हैं।
Step 5 → जल्दी `200 OK` respond करो — timeout/non-200 पर provider RETRY करेगा।
Step 6 → Actual heavy processing ASYNCHRONOUSLY करो (background job) acknowledge करने के बाद।
Step 7 → **Idempotency** handle करो — event ID store करके duplicate processing रोको।

---

## 🟡 Real World Example
**Razorpay's** payment webhook sends `payment.captured` events to merchants' registered endpoints. A food-delivery startup's handler verifies the `X-Razorpay-Signature` header using HMAC-SHA256 over the raw body with their webhook secret, checks if `event.payload.payment.entity.id` has already been processed (stored in a `processed_webhook_events` table with a unique constraint), and if new, marks the corresponding order as "paid" and enqueues an order-confirmation email job — all within 200ms, responding `200 OK` immediately. If Razorpay doesn't get a 200 within its timeout, it retries the SAME event up to several times over 24 hours, which is exactly why the idempotency check matters — without it, a slow response once would cause duplicate order confirmations.

## 🟡 Real Example Hindi mein
**Razorpay** का payment webhook `payment.captured` events merchants के registered endpoints को भेजता है। Food-delivery startup का handler `X-Razorpay-Signature` HMAC-SHA256 से verify करता है, check करता है कि payment ID पहले process हुआ या नहीं (unique constraint वाली table में), नया हो तो order को "paid" mark करता है और confirmation email job enqueue करता है — सब 200ms में, immediately `200 OK` respond करता है।

---

## 💻 Code Example — Basic

```javascript
// basic-webhook.js — minimal signature-verified webhook handler
// npm install express
// Run: node basic-webhook.js

const express = require('express');
const crypto = require('crypto');
const app = express();

const WEBHOOK_SECRET = 'my-shared-webhook-secret'; // from provider's dashboard, store in env var

// CRITICAL: use express.raw() for webhook routes, NOT express.json()
// We need the exact raw bytes to verify the signature correctly
app.post('/webhooks/payment', express.raw({ type: 'application/json' }), (req, res) => {
  const signature = req.headers['x-webhook-signature'];
  const rawBody = req.body; // this is a Buffer because of express.raw()

  // Recompute the expected signature using our secret
  const expectedSignature = crypto
    .createHmac('sha256', WEBHOOK_SECRET)
    .update(rawBody)
    .digest('hex');

  // Timing-safe comparison — prevents timing attacks on signature comparison
  const isValid = crypto.timingSafeEqual(
    Buffer.from(signature, 'hex'),
    Buffer.from(expectedSignature, 'hex')
  );

  if (!isValid) {
    console.warn('Invalid webhook signature — possible forged request');
    return res.status(401).json({ error: 'Invalid signature' });
  }

  // NOW safe to parse the body as JSON
  const event = JSON.parse(rawBody.toString());
  console.log('Verified webhook event:', event.type);

  res.status(200).json({ received: true }); // acknowledge quickly
});

app.listen(3000, () => console.log('Webhook server on port 3000'));
```

## 💻 Code Example — Advanced

```javascript
// advanced-webhook.js — idempotency, async processing, multiple event types
// npm install express
// (In production, pair this with BullMQ for the async processing step)

const express = require('express');
const crypto = require('crypto');
const app = express();

const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || 'secret';

// In-memory idempotency store (use a real DB table with a unique constraint in production)
const processedEventIds = new Set();

function verifySignature(rawBody, signature, secret) {
  const expected = crypto.createHmac('sha256', secret).update(rawBody).digest('hex');
  try {
    return crypto.timingSafeEqual(Buffer.from(signature, 'hex'), Buffer.from(expected, 'hex'));
  } catch {
    return false; // lengths mismatched or invalid hex — definitely not valid
  }
}

// Simulate enqueuing heavy work to a background job queue (e.g. BullMQ)
async function enqueueOrderConfirmation(orderId) {
  console.log(`[queued] Sending confirmation for order ${orderId}`);
  // In real code: await queue.add('send-confirmation', { orderId });
}

app.post(
  '/webhooks/payment',
  express.raw({ type: 'application/json', limit: '1mb' }),
  async (req, res) => {
    const signature = req.headers['x-webhook-signature'];
    const rawBody = req.body;

    // ─── 1. Verify signature FIRST, before touching the payload ───────────
    if (!signature || !verifySignature(rawBody, signature, WEBHOOK_SECRET)) {
      return res.status(401).json({ error: 'Invalid signature' });
    }

    let event;
    try {
      event = JSON.parse(rawBody.toString());
    } catch {
      return res.status(400).json({ error: 'Malformed JSON payload' });
    }

    // ─── 2. Idempotency check — has this exact event already been handled? ─
    const eventId = event.id;
    if (processedEventIds.has(eventId)) {
      console.log(`Duplicate delivery of event ${eventId} — acknowledging without reprocessing`);
      return res.status(200).json({ received: true, duplicate: true });
    }

    // ─── 3. Respond FAST — acknowledge before doing slow downstream work ──
    res.status(200).json({ received: true });

    // ─── 4. Process asynchronously AFTER responding ───────────────────────
    try {
      processedEventIds.add(eventId); // mark as seen (do this in a DB transaction in production)

      switch (event.type) {
        case 'payment.captured':
          console.log(`Payment captured for order ${event.data.orderId}`);
          await enqueueOrderConfirmation(event.data.orderId);
          break;
        case 'payment.failed':
          console.log(`Payment failed for order ${event.data.orderId}`);
          // handle failure — notify user, release inventory hold, etc.
          break;
        default:
          console.log(`Unhandled event type: ${event.type}`);
      }
    } catch (err) {
      // Logged here, NOT sent back to the provider (response already sent above)
      // Use proper alerting (Sentry, PagerDuty) so this doesn't go unnoticed
      console.error(`Error processing webhook event ${eventId}:`, err);
    }
  }
);

app.listen(3000, () => console.log('Advanced webhook server on port 3000'));
```

---

## 🟠 Express.js Integration

```javascript
// Handling MULTIPLE webhook sources on different routes, each with its own secret/raw-body need
const express = require('express');
const crypto = require('crypto');
const app = express();

// IMPORTANT: apply express.raw() ONLY to webhook routes, express.json() to everything else
// Order matters — more specific raw-body routes must be registered before the global json parser
app.post('/webhooks/razorpay', express.raw({ type: '*/*' }), (req, res) => {
  const sig = req.headers['x-razorpay-signature'];
  const expected = crypto.createHmac('sha256', process.env.RAZORPAY_WEBHOOK_SECRET).update(req.body).digest('hex');
  if (sig !== expected) return res.status(401).end();
  res.status(200).json({ ok: true });
});

app.post('/webhooks/github', express.raw({ type: '*/*' }), (req, res) => {
  const sig = req.headers['x-hub-signature-256']; // format: "sha256=<hash>"
  const expected = 'sha256=' + crypto.createHmac('sha256', process.env.GITHUB_WEBHOOK_SECRET).update(req.body).digest('hex');
  if (sig !== expected) return res.status(401).end();
  res.status(200).json({ ok: true });
});

// Regular JSON parsing applies to all OTHER routes, registered after the raw webhook routes
app.use(express.json());

app.get('/api/health', (req, res) => res.json({ status: 'ok' }));

app.listen(3000, () => console.log('Multi-provider webhook server on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Parsing the body with `express.json()` BEFORE signature verification
✅ Correct: Use `express.raw()` specifically for webhook routes so the EXACT bytes the provider signed are available for HMAC comparison — JSON.stringify(JSON.parse(body)) is NOT guaranteed to produce byte-identical output (key ordering, whitespace differences), breaking signature verification.

```javascript
// Wrong: global express.json() consumes and transforms the body before your handler runs
app.use(express.json()); // applies to ALL routes including webhooks
app.post('/webhooks/payment', (req, res) => {
  // req.body is now a parsed OBJECT — original raw bytes are gone, signature check will fail
});

// Right: raw body parser scoped to just the webhook route
app.post('/webhooks/payment', express.raw({ type: 'application/json' }), (req, res) => {
  // req.body is a Buffer — exact original bytes, safe for HMAC verification
});
```

❌ Mistake 2: Doing slow processing BEFORE responding, causing timeouts and duplicate retries
✅ Correct: Acknowledge receipt (200 OK) immediately after verification, then do heavy work asynchronously — most providers have a tight timeout (often 5-10 seconds) and will treat a slow response as failure, triggering a retry (and potential duplicate processing if your work wasn't idempotent).

```javascript
// Wrong: webhook times out if sendConfirmationEmail + updateInventory + generateInvoice takes >10s
app.post('/webhooks/payment', async (req, res) => {
  await sendConfirmationEmail(data);   // slow
  await updateInventory(data);          // slow
  await generateInvoice(data);          // slow
  res.status(200).json({ received: true }); // provider may have already retried by now!
});

// Right: respond fast, enqueue the slow work
app.post('/webhooks/payment', (req, res) => {
  res.status(200).json({ received: true }); // immediate ack
  backgroundQueue.add('process-payment', data); // slow work happens separately
});
```

---

## 🧠 Tricky Interview Question

```javascript
// The provider says webhooks are delivered "at least once." What does this mean
// for this handler, and what's missing?
app.post('/webhooks/payment', verifySignature, async (req, res) => {
  const event = JSON.parse(req.body);
  await db.query('UPDATE orders SET status = ? WHERE id = ?', ['paid', event.orderId]);
  await emailService.sendConfirmation(event.orderId); // sends an email EVERY time this runs
  res.status(200).json({ received: true });
});
```
Answer: "At least once" delivery means the SAME event can arrive MORE than once (due to network retries, provider-side retry logic if your server was slow/down momentarily, or provider bugs) — it's never "exactly once" without extra work on your end. This handler is missing **idempotency**: if the webhook is delivered twice for the same `event.id`, `sendConfirmation` runs twice, emailing the customer TWICE for one payment. The fix: before processing, check (and atomically record) whether `event.id` has already been handled — e.g. an `INSERT ... ON CONFLICT DO NOTHING` into a `processed_events` table with `event_id` as a UNIQUE column, and only proceed with side effects (email, status update) if the insert actually happened (wasn't a duplicate).

---

## ⚫ Interview Questions + Answers

Q1: Why must webhook signature verification use the RAW request body instead of the re-serialized parsed object?
A1: HMAC signatures are computed over the EXACT bytes the provider sent. `JSON.stringify(JSON.parse(rawBody))` can produce a DIFFERENT byte sequence than the original (different key ordering if the parser doesn't preserve it, different whitespace/number formatting, e.g. `1.0` vs `1`). Even a single-byte difference produces a completely different HMAC hash, causing legitimate requests to fail verification. This is why raw-body capture (via `express.raw()` or a middleware storing `req.rawBody` before any JSON parsing) is mandatory for webhook routes specifically.

Q2: What's the security risk of NOT verifying webhook signatures at all?
A2: Without verification, your `/webhooks/payment` endpoint is a PUBLIC URL that anyone can POST to — an attacker could forge a `payment.captured` event claiming a fake order was paid, tricking your system into shipping goods or granting access without actual payment. Signature verification proves the request genuinely came from the provider (who holds the matching secret), not an arbitrary forged request.

Q3: How should you handle webhook retries from the provider's perspective (what counts as "success")?
A3: Return `2xx` (typically `200`) ONLY when you've successfully received and at least acknowledged the event (even if async processing is still pending) — this tells the provider "don't retry." Return `4xx`/`5xx`/timeout if you genuinely couldn't process it (invalid signature, malformed payload, your server down) — this signals the provider to retry later. Never return `200` prematurely if you haven't even validated the signature, since a forged/garbage request would then stop being retried (not relevant since it was fake anyway) but you also shouldn't accidentally return non-200 for valid events due to slow downstream code — hence the "verify fast, ack fast, process async" pattern.

Q4: How would you test a webhook handler locally when the third-party provider needs a public URL to send to?
A4: Use a tunneling tool like **ngrok** (`ngrok http 3000`) to expose your local server via a temporary public HTTPS URL, which you register as the webhook endpoint in the provider's dashboard/test mode. Most providers (Stripe, Razorpay) also offer a CLI tool (`stripe listen --forward-to localhost:3000/webhooks`) that forwards real or simulated events directly to your local server without needing ngrok, and lets you trigger specific test events on demand.

Q5: What happens if your database write succeeds but your process crashes BEFORE sending the 200 response — will the provider retry, and is that a problem?
A5: Yes, the provider will retry (it never received a 200, so from its perspective the delivery failed/timed out). This IS handled correctly by proper idempotency: on retry, your handler re-checks `processed_events` for that `event.id` — if the DB write already happened (it did, before the crash), the idempotency check prevents re-applying the side effects (like re-sending a confirmation email), while still allowing the handler to respond with 200 this time. This is exactly why the idempotency marker should be written atomically WITH or BEFORE the side-effect-causing action, using a DB transaction/unique constraint, not as an afterthought.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Integrating with any third-party service that offers event-driven notifications (payment gateways, GitHub, Twilio, Shopify)
- You need near-real-time reaction to external events without polling overhead

❌ Avoid when:
- Building your OWN internal event system between services you control — a message queue (BullMQ, SQS, Kafka) or direct API call is usually more appropriate than reinventing webhook-style HTTP push for internal-only communication
- The third-party service doesn't offer webhooks and only supports polling — in that case, polling with sensible intervals/backoff is your only option

---

## 📊 Visual Diagram
```
THIRD-PARTY PROVIDER (e.g. Razorpay)        YOUR SERVER
──────────────────────────────────           ─────────────────────────────────
Payment captured event occurs
        │
        ▼
POST /webhooks/payment                 ──►  1. express.raw() captures exact bytes
  X-Razorpay-Signature: abc123...             │
  body: { id: "evt_1", type: "payment.captured", ... }
                                               ▼
                                         2. Recompute HMAC with shared secret
                                               │
                                         ┌─────┴─────┐
                                   mismatch        match
                                         │             │
                                         ▼             ▼
                                   401 Rejected   3. Check idempotency (event.id seen before?)
                                                       │
                                                 ┌─────┴─────┐
                                             duplicate      new
                                                 │             │
                                                 ▼             ▼
                                         200 (no reprocess)  4. 200 OK (ack immediately)
                                                               5. Enqueue async processing
                                                                  (update DB, send email, etc.)

IF no 200 received within timeout → Provider RETRIES the same event (at-least-once delivery)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Webhook | Provider-initiated HTTP push notification of an event | Provider से event की HTTP push notification |
| HMAC Signature | Cryptographic proof the payload wasn't tampered with | Payload tamper न हुआ, इसका cryptographic proof |
| Raw Body | Exact unparsed bytes of the request | Request के exact unparsed bytes |
| Idempotency | Processing the same event twice has no extra effect | Same event दो बार process होने पर extra असर नहीं |
| At-least-once delivery | Provider guarantees delivery but may duplicate | Provider delivery guarantee देता पर duplicate हो सकता |
| Timing-safe comparison | Comparison immune to timing-attack information leaks | Timing-attack से बचाने वाली comparison |

---

## ⚡ 3-Line Summary
English: 1. Webhook handlers must verify an HMAC signature over the RAW request body before trusting any incoming event, rejecting mismatches as potentially forged. 2. Respond `200 OK` immediately after verification and do heavy processing asynchronously, since providers retry on timeout/non-200 responses. 3. Track processed event IDs to guarantee idempotency — "at-least-once" delivery means duplicates WILL happen, and side effects (emails, payments) must not double-fire.
Hindi: 1. Webhook handlers को किसी भी incoming event पर trust करने से पहले RAW body पर HMAC signature verify करना चाहिए, mismatch को forged मानकर reject करना चाहिए। 2. Verification के बाद immediately `200 OK` respond करो और heavy processing asynchronously करो। 3. Idempotency guarantee के लिए processed event IDs track करो — duplicates ज़रूर होंगे, side effects double-fire नहीं होने चाहिए।

---

## ➡️ Next Topic
**281. Build Email Service (Nodemailer)** — Nodemailer से transactional email service बनाना, templates और retries के साथ।
