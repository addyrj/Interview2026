# 119. Payment System (Design)
# हिंदी में: Payment System — ग्राहक से पैसा लेना (UPI, card, netbanking), सही-सही ledger में लिखना, refund, merchant/seller को settlement, और हर रुपये का हिसाब मिलाना (reconciliation) — बिना दोहरा पैसा काटे

---

## 🔵 Simple Definition (English)
Design a **payment system** for a platform (e-commerce, food delivery, ride-hailing) or a payment company (Razorpay/Stripe-like) that **accepts payments** through **payment gateways / PSPs** (UPI, cards, netbanking, wallets), tracks **payment state**, records every money movement in a **double-entry ledger**, handles **refunds, failures, retries and webhooks**, **pays out** merchants/sellers/drivers, and **reconciles** with banks and gateways, with **exactly-once money movement**, **auditability**, **security (PCI-DSS)** and **compliance (RBI)**.

## 🔵 सरल परिभाषा (Hindi)
Payment system ग्राहक से UPI/card/netbanking से पैसा लेता है (payment gateway के ज़रिए), हर रुपये का हिसाब double-entry ledger में रखता है, refund और फ़ेल payments संभालता है, sellers/drivers को पैसे (payout) भेजता है, और रोज़ बैंक/gateway के रिकॉर्ड से मिलान करता है।
सबसे ज़रूरी: पैसा कभी दो बार न कटे, न खोए — और हर चीज़ का audit हो।

---

## 🔴 Problem it Solves
Money bugs are the most expensive bugs:
- **Double charges** from retries and double taps → angry customers, chargebacks, regulatory complaints.
- **"Money debited but order failed"**: the payment succeeded at the bank but our system missed it (lost webhook, timeout).
- **Inconsistent balances** from non-atomic updates; **lost money** that no one can trace.
- **Security:** card data theft; PCI-DSS scope; fraud.
- **Settlement mismatches** with gateways and banks (T+1 settlements, fees, GST).

A payment system design must make money movement **idempotent, auditable, reconcilable and secure**.

## 🔴 यह क्यों बना? (Hindi)
पैसे वाले bugs सबसे महँगे होते हैं: retry या double-tap से दो बार पैसा कटना, "पैसा कटा पर order फ़ेल" (webhook खो गया), balance में गड़बड़, पता न चलने वाला खोया पैसा, card data चोरी, और gateway/बैंक के settlement से हिसाब न मिलना।
Design ऐसा हो कि हर लेन-देन idempotent, audit होने लायक, मिलान होने लायक और सुरक्षित हो।

---

## 🟢 How it Works — Step by Step (Interview Design)

### 1. Requirements

```
Functional:
  - Create payment for an order; support UPI (intent/collect/QR), cards, netbanking, wallets
  - Payment status: CREATED → PENDING → AUTHORIZED/CAPTURED → (REFUNDED / FAILED)
  - Webhooks from gateway; status polling fallback; retries
  - Refunds (full/partial), payouts to sellers/drivers, wallets/credits (optional)
  - Ledger of all money movements; reconciliation; reports for finance
Non-functional:
  - Correctness > everything: no double charge, no lost payment (exactly-once EFFECT)
  - Availability 99.99% for payment initiation; strong consistency for ledger
  - Security: PCI-DSS (avoid storing card data — tokenize), encryption, audit, RBI compliance
  - Latency: initiation < 500 ms (excluding user bank auth time)
```

### 2. Key concepts

```
Payment Gateway / PSP (Razorpay, Stripe, PayU, Cashfree, Juspay): talks to card networks & banks
Acquirer (merchant's bank), Issuer (customer's bank), Network (Visa/Mastercard/RuPay), NPCI (UPI)
Authorization vs Capture (cards): authorize = hold funds; capture = actually take money (can be later)
Settlement: gateway transfers collected money (minus fees) to merchant account T+1/T+2
Chargeback: customer disputes with bank → merchant must prove/refund
Tokenization: card replaced by token (RBI mandate) → you never store PAN/CVV
```

### 3. Architecture

```
 📱 Client ──1. place order──► Order svc ──2. create payment──► PAYMENT SERVICE
                                                                │  - idempotency (order/attempt key)
                                                                │  - payment record CREATED
                                                                │  - call PSP: create gateway order
 📱 Client ◄──3. gatewayOrderId + SDK params──────────────────────┘
 📱 Client ──4. pays in PSP SDK (UPI app / card 3DS / netbanking) ──► PSP ──► bank/NPCI
                                                                       │
              5. PSP webhook "payment.captured" (signed) ──► Webhook handler ──► verify signature
                                                               │                 dedup event id
                                                               ▼
                                                   PAYMENT SERVICE: state → CAPTURED
                                                   LEDGER: double-entry rows (atomic)
                                                   outbox → Kafka "PaymentCaptured"
                                                               │
                         ┌─────────────────────────────────────┼───────────────────────┐
                         ▼                                     ▼                       ▼
                   Order svc confirms                  Notifications          Payout/settlement svc
 6. Client also asks GET /payments/{id} (poll) — never trust client "success" callback alone
 7. Recon job (daily): PSP settlement files vs ledger vs orders → mismatches → auto-fix/alerts
 8. Timeout/unknown → status query to PSP after N seconds (status checker worker)
```

### 4. Payment state machine

```
CREATED ──► PENDING (user paying) ──► CAPTURED ──► PARTIALLY_REFUNDED / REFUNDED
   │              │                      │
   │              ├──► FAILED            └──► (chargeback) DISPUTED
   │              └──► EXPIRED (no completion in N min) — but late success possible → reconcile!
State transitions: only valid ones allowed (WHERE status = 'PENDING'), each recorded with event & timestamp.
```

### 5. Double-entry ledger (the accounting core)

```
Every money movement = ≥ 2 entries that sum to ZERO (debits = credits). Immutable, append-only.

Customer pays ₹500 for order 9001 (gateway fee ₹10, platform commission ₹50, seller gets ₹440):
  entry_id  txn_id    account                       amount
  1         t-9001    customer_payments_receivable   -500     (money coming from gateway)
  2         t-9001    seller:77:payable              +440
  3         t-9001    platform:commission_revenue    +50
  4         t-9001    expense:gateway_fees           +10
  SUM = 0 ✅
Refund ₹500 → NEW reversing entries (never edit/delete old ones).
Balances = SUM(amount) per account (materialized/cached, but derivable from entries).
Benefits: auditability, catches bugs (sum ≠ 0), supports reconciliation & financial reporting.
```

### 6. Idempotency everywhere (Topic 64)

```
Client → Payment API:      Idempotency-Key per checkout attempt
Payment svc → PSP:         PSP idempotency (order id / receipt / Idempotency-Key header)
PSP → Webhook:             dedup by PSP event id (webhooks are retried, at-least-once)
Payment → Ledger:          unique (txn_id, leg) constraint; state transition guarded by status
Refunds:                   refund id idempotency (never refund twice on retry)
```

### 7. Handling uncertainty (the hardest part)

```
Timeout calling PSP → status UNKNOWN (not FAILED!) → status-check worker polls PSP with backoff
Webhook missed      → periodic sweep: PENDING payments older than X min → query PSP status
Late success        → payment captured after order auto-cancelled → auto-refund or revive order
Client says success but no server confirmation → show "Verifying payment…", poll server
Daily reconciliation catches anything left: PSP report vs ledger vs orders
```

### 8. Payouts & settlement
```
Sellers/drivers payable balances from ledger → payout batches (daily/weekly) via payout APIs (RazorpayX,
Cashfree Payouts, bank NEFT/IMPS/UPI) → idempotent payout ids → status webhooks → ledger entries
Hold periods (returns window), TDS/GST deductions, failed payout retries
```

### 9. Security & compliance
```
- Never touch raw card data: use PSP hosted fields/SDK (reduces PCI scope to SAQ-A); tokenization (RBI)
- Verify webhook signatures (HMAC), allow-list PSP IPs, TLS everywhere
- Encrypt PII; strict access control; audit logs; maker-checker for manual adjustments
- Fraud checks: velocity rules, device fingerprint, risk scoring (or PSP's)
- RBI: data localization (payment data stored in India), 2FA/AFA for cards, auto-reversal TAT for failed UPI
```

### 10. Multi-PSP routing (scale & resilience)
```
Payment orchestrator routes by method/bank/success rate/cost: if PSP A's UPI success drops → route to B
(circuit breaker per PSP/method/bank) — Juspay/Razorpay Optimizer style
```

## 🟢 कैसे काम करता है? (Hindi)
1. Order बनते ही payment service एक record (CREATED) बनाती है और gateway (Razorpay) पर gateway-order बनाती है — idempotency key के साथ।
2. ग्राहक gateway के SDK में पैसे देता है (UPI ऐप/card OTP); gateway signed webhook भेजता है → signature जाँचो, event id से dedup, स्थिति CAPTURED।
3. उसी transaction में double-entry ledger: ग्राहक से -500, seller +440, कमीशन +50, gateway fee +10 = कुल 0। गलती सुधारनी हो तो उल्टी entry, कभी edit नहीं।
4. Timeout = "पता नहीं" — status-check worker gateway से पूछता है; छूटे webhooks के लिए sweep; रोज़ gateway रिपोर्ट से reconciliation।
5. Card data कभी ख़ुद मत रखो (gateway SDK + tokenization), webhooks verify करो, RBI नियम (डेटा भारत में), sellers को payouts idempotent।

---

## 🟡 Real World Example

**Stripe** — idempotency keys on every POST, a robust webhook system with retries, and a ledger-based internal architecture. Stripe's engineering blog on idempotency is the industry reference.

**Razorpay / Juspay (India)** — payment orchestration across multiple banks and PSPs for UPI, cards and netbanking with smart routing on success rates. Razorpay's "Optimizer" routes to the best-performing gateway per transaction.

**UPI (NPCI)** — 13+ billion transactions a month. Failed transactions where money was debited trigger automatic reversal, and RBI mandates turnaround times and compensation for delays. This is reconciliation and compensation at national scale.

**Uber / Airbnb payments** — Uber rebuilt its payment platform around a double-entry ledger (LedgerStore) for billions of transactions, and Airbnb wrote about its payments platform migrations for correctness and auditability.

**Double-charge incidents** — many companies have had retry bugs that charged customers twice, typically fixed with idempotency keys and status checks before retrying.

## 🟡 Real Example Hindi में
Stripe हर POST पर idempotency key और मज़बूत webhooks देता है। Razorpay/Juspay कई बैंकों और gateways के बीच सफलता दर देखकर payment भेजते हैं।
UPI में महीने के 1300 करोड़+ transactions हैं — पैसा कटा पर फ़ेल हुआ तो अपने आप वापसी (RBI की समय-सीमा के साथ)। Uber ने अपना payment सिस्टम double-entry ledger पर दोबारा बनाया।

---

## 🟠 My Stack Example

### Tables (Postgres)
```sql
CREATE TABLE payments (
  id UUID PRIMARY KEY, order_id BIGINT NOT NULL, amount_paise BIGINT NOT NULL CHECK (amount_paise > 0),
  currency CHAR(3) DEFAULT 'INR', status TEXT NOT NULL, psp TEXT, psp_order_id TEXT UNIQUE, psp_payment_id TEXT UNIQUE,
  idempotency_key TEXT UNIQUE NOT NULL, created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE ledger_entries (
  id BIGSERIAL PRIMARY KEY, txn_id TEXT NOT NULL, account TEXT NOT NULL, amount_paise BIGINT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(), UNIQUE (txn_id, account)
);
CREATE TABLE processed_webhooks (event_id TEXT PRIMARY KEY, received_at TIMESTAMPTZ DEFAULT now());
-- invariant check (nightly): SELECT txn_id FROM ledger_entries GROUP BY txn_id HAVING SUM(amount_paise) <> 0;
```

### Create payment (idempotent) with Razorpay
```js
app.post('/api/v1/payments', authenticate, async (req, res) => {
  const key = req.get('Idempotency-Key');
  const existing = await db.oneOrNone('SELECT * FROM payments WHERE idempotency_key = $1', [key]);
  if (existing) return res.json(toClient(existing));                           // replay

  const order = await orders.getForUser(req.body.orderId, req.user.id);       // server-side amount!
  const id = crypto.randomUUID();
  await db.none("INSERT INTO payments(id, order_id, amount_paise, status, idempotency_key) VALUES ($1,$2,$3,'CREATED',$4)",
                [id, order.id, order.totalPaise, key]);
  const rp = await razorpay.orders.create({ amount: order.totalPaise, currency: 'INR', receipt: id });   // receipt = our id
  await db.none("UPDATE payments SET psp='razorpay', psp_order_id=$1, status='PENDING' WHERE id=$2", [rp.id, id]);
  res.status(201).json({ paymentId: id, razorpayOrderId: rp.id, amount: order.totalPaise, key: RZP_KEY_ID });
});
```

### Webhook: verify, dedup, transition, ledger — all atomic
```js
app.post('/webhooks/razorpay', express.raw({ type: 'application/json' }), async (req, res) => {
  const sig = req.get('X-Razorpay-Signature');
  const expected = crypto.createHmac('sha256', WEBHOOK_SECRET).update(req.body).digest('hex');
  if (!sig || sig.length !== expected.length ||
      !crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expected))) return res.sendStatus(400);
  const evt = JSON.parse(req.body);
  const eventId = req.get('X-Razorpay-Event-Id');

  await withTx(pool, async (tx) => {
    const fresh = await tx.query('INSERT INTO processed_webhooks(event_id) VALUES ($1) ON CONFLICT DO NOTHING', [eventId]);
    if (!fresh.rowCount) return;                                               // duplicate delivery
    if (evt.event === 'payment.captured') {
      const p = evt.payload.payment.entity;
      const { rows: [pay] } = await tx.query(
        `UPDATE payments SET status='CAPTURED', psp_payment_id=$1, updated_at=now()
         WHERE psp_order_id=$2 AND status IN ('PENDING','CREATED','EXPIRED') RETURNING *`, [p.id, p.order_id]);
      if (!pay) return;                                                        // already captured
      if (p.amount !== Number(pay.amount_paise)) { await flagMismatch(tx, pay, p); return; }
      await postLedger(tx, `pay:${pay.id}`, [
        ['psp:razorpay:receivable', p.amount - 0], ['customer:payments', -p.amount],   // simplified legs summing to 0
      ]);
      await tx.query("INSERT INTO outbox(event_type, payload) VALUES ('PaymentCaptured', $1)", [{ paymentId: pay.id, orderId: pay.order_id }]);
    }
  });
  res.sendStatus(200);                                                         // ack fast
});

async function postLedger(tx, txnId, legs) {
  if (legs.reduce((s, [, a]) => s + a, 0) !== 0) throw new Error('UNBALANCED_LEDGER');
  for (const [account, amount] of legs)
    await tx.query('INSERT INTO ledger_entries(txn_id, account, amount_paise) VALUES ($1,$2,$3) ON CONFLICT DO NOTHING', [txnId, account, amount]);
}
```

### Status checker for unknown/pending payments (FastAPI worker)
```python
async def sweep_pending():
    rows = await db.fetch_all("SELECT id, psp_order_id FROM payments WHERE status='PENDING' AND created_at < now() - interval '3 minutes'")
    for row in rows:
        payments = razorpay.order.payments(row["psp_order_id"])["items"]
        captured = next((p for p in payments if p["status"] == "captured"), None)
        if captured:
            await apply_capture(row["id"], captured)        # same idempotent path as webhook
        elif created_long_ago(row):
            await mark_expired_and_release(row["id"])        # release inventory; late success → auto-refund
```

### Client (React Native) — never trust the SDK callback alone
```ts
RazorpayCheckout.open({ key, order_id: razorpayOrderId, amount, name: 'MyApp', prefill: { contact: phone } })
  .then(() => navigation.replace('PaymentVerifying', { paymentId }))        // poll server for CAPTURED
  .catch(() => navigation.replace('PaymentVerifying', { paymentId }));      // even on "failure" → verify (late success!)
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you guarantee a customer is never charged twice?**
A1: Use idempotency at every boundary: a client idempotency key per checkout attempt (the server returns the existing payment on retry), one payment record per order attempt with unique constraints, a provider-side idempotency key or receipt ID when creating gateway orders and refunds, webhook deduplication by event ID, and guarded state transitions (`WHERE status='PENDING'`). On timeouts, query the payment status instead of creating a new payment. Disable double taps in the UI. Reconciliation detects and auto-refunds any duplicates.

**Q2: Why a double-entry ledger?**
A2: Every money movement is recorded as balanced entries (debits equal credits, summing to zero) in an immutable, append-only log. It gives a complete audit trail, makes balances derivable and verifiable (the sum per transaction must be zero, which catches bugs), supports corrections via reversing entries rather than edits, enables reconciliation with external statements, and maps directly to accounting and financial reporting. Mutable balance columns alone lose history and hide errors.

**Q3: How do you handle a payment where the gateway call timed out?**
A3: Treat the status as unknown, not failed. Record it as pending or unknown and don't retry by creating a new charge. A status-check worker queries the gateway (by our order ID or receipt) with backoff, and the webhook may arrive later. If captured, proceed. If definitively failed, release inventory and notify. If it succeeds after the order was cancelled, auto-refund or reinstate. The client UI shows "verifying payment" and polls the server.

**Q4: How do you reconcile payments?**
A4: Daily (and intraday for high volume), ingest gateway or bank settlement reports and compare them against our payments and ledger by transaction IDs and amounts. Categorize mismatches: captured at the gateway but not in our system (missed webhook, so apply the capture), in our system but not at the gateway (investigate or reverse), amount differences, fee or GST discrepancies, and missing settlements. Auto-fix the known categories, alert finance or ops for the rest, and track until resolved. Verify that ledger totals per account match the settlement amounts.

**Q5: How do you stay PCI-DSS compliant and secure?**
A5: Never let card data touch your servers. Use the PSP's hosted checkout, SDK or iframe fields and card tokenization (mandated by RBI), which shrinks PCI scope dramatically. Use TLS everywhere, verify webhook signatures, restrict and audit access to payment systems, encrypt sensitive data, manage secrets in a vault or KMS, require maker-checker approval for manual adjustments and refunds above thresholds, run fraud detection, and meet RBI rules (data localization, additional factor authentication, failed-transaction reversal timelines).

---

## 🔷 Trade-offs
✅ Gateway/PSP integration: fast to market, PCI handled — ❌ fees, dependency, less control.
✅ Multi-PSP orchestration: higher success & resilience — ❌ complexity, more reconciliation.
✅ Ledger + immutable events: auditability — ❌ more storage/complexity than a balance column.
✅ Async webhooks: scalable — ❌ eventual confirmation, need status checks & UX for "processing".

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Payment gateway / PSP | Processes payments with banks | बैंकों से पेमेंट कराने वाला |
| Authorization / Capture | Hold funds / take funds | पैसा रोकना / लेना |
| Settlement | Gateway pays merchant | merchant को पैसा पहुँचना |
| Double-entry ledger | Balanced debit/credit entries | दोहरी प्रविष्टि वाला हिसाब |
| Webhook | Gateway's async notification | gateway की सूचना |
| Idempotency key | Prevents duplicate charges | दोहरा पैसा रोकने की key |
| Reconciliation | Matching records with gateway/bank | हिसाब मिलाना |
| Refund / Chargeback | Return money / bank dispute | पैसा लौटाना / विवाद |
| Tokenization | Replace card with token | card की जगह token |
| PCI-DSS | Card data security standard | card डेटा सुरक्षा मानक |

---

## ⚡ 3-Line Summary
**English:**
1. Payment service creates idempotent payment records, integrates PSPs via SDK/hosted flows, and confirms via signed, deduplicated webhooks + status polling.
2. Every money movement goes to an immutable double-entry ledger (sum = 0) atomically with state transitions; outbox events drive orders/payouts.
3. Treat timeouts as unknown, sweep pending payments, reconcile daily, never store card data, follow RBI/PCI rules, and route across PSPs.

**Hindi:**
1. Payment service idempotent records बनाती है, gateway SDK से पेमेंट, और signed webhooks + status जाँच से पुष्टि।
2. हर लेन-देन double-entry ledger में (कुल 0), स्थिति बदलने के साथ उसी transaction में।
3. Timeout = पता नहीं; pending की जाँच; रोज़ reconciliation; card data कभी नहीं; RBI/PCI नियम।

---

## ➡️ Next Topic Suggestion
**120. File Storage (Google Drive)** — Next: storing and syncing users' files across devices, with chunked uploads, deduplication, versioning, sharing permissions and sync conflict resolution.
