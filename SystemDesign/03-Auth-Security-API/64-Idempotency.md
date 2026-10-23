# 64. Idempotency
# हिंदी में: Idempotency — एक ही request को कितनी भी बार भेजो, नतीजा वही रहे जो एक बार भेजने पर होता (जैसे पेमेंट दो बार न कटे)

---

## 🔵 Simple Definition (English)
An operation is **idempotent** if performing it **once or many times has the same effect**. For APIs, this means a client can **safely retry** a request (after a timeout, network drop or crash) **without causing duplicates**: no double charge, no two orders, no two emails.
Non-idempotent operations (like `POST /payments`) are made idempotent using an **Idempotency-Key**: a unique ID per logical operation that the server uses to **detect and de-duplicate retries**.

## 🔵 सरल परिभाषा (Hindi)
Idempotent काम वो है जिसे एक बार करो या दस बार, असर एक जैसा रहे।
Mobile पर नेटवर्क टूटे और ऐप "Pay ₹500" दोबारा भेजे, तो पैसे दो बार नहीं कटने चाहिए — इसके लिए हर काम के साथ एक unique Idempotency-Key भेजी जाती है, जिससे सर्वर दोहराई गई request पहचान लेता है।

---

## 🔴 Problem it Solves
In distributed systems, **you can't tell "the request failed" from "the response got lost"**:
```
App ── POST /payments ₹500 ──► Server ── charges card ✓ ──► response ──X (network drops)
App: "timeout... retry!" ── POST /payments ₹500 ──► Server charges AGAIN ❌ ₹1000 gone
```
This happens constantly: mobile networks drop, users double-tap "Pay", load balancers retry, message queues redeliver (at-least-once), and workers crash after doing work but before ACKing.
**Idempotency turns "at-least-once delivery" into "exactly-once effect."**

## 🔴 यह क्यों बना? (Hindi)
Distributed सिस्टम में पता ही नहीं चलता कि request फ़ेल हुई या सिर्फ़ जवाब खो गया। नेटवर्क टूटा, ऐप ने retry किया — और पैसे दो बार कट गए।
यूज़र का double-tap, LB का retry, queue का दोबारा मैसेज देना — सब आम हैं। Idempotency से "कई बार पहुँचना" भी "एक ही बार असर" बन जाता है।

---

## 🟢 How it Works — Step by Step

### HTTP methods & idempotency (recap from Topic 5)

```
GET, HEAD, OPTIONS   → safe + idempotent (read only)
PUT                  → idempotent (set to this state)        PUT /users/42 {name:"A"} ×3 = same
DELETE               → idempotent (gone is gone)             2nd call → 404/204, state same
PATCH                → depends: {name:"A"} yes; {"op":"increment"} NO
POST                 → NOT idempotent by default             POST /orders ×3 = 3 orders ❌
```

### Idempotency-Key flow (Stripe-style)

```
Client generates key ONCE per user action (UUID v4), reuses it for every retry of that action.

 App                                        Server                                  DB
  │ POST /payments                            │                                      │
  │ Idempotency-Key: 7f3a-...  {amount: 500}  │                                      │
  │──────────────────────────────────────────►│ 1. INSERT idempotency_keys(key, user,│
  │                                           │    request_hash, status='processing')│
  │                                           │    (UNIQUE key → only first wins) ──►│
  │                                           │ 2. do the work (charge, create order)│
  │                                           │ 3. store response (status code+body),│
  │                                           │    status='completed' ──────────────►│
  │  ✗ response lost                          │                                      │
  │ (retry) POST /payments                    │                                      │
  │ Idempotency-Key: 7f3a-... (SAME)          │                                      │
  │──────────────────────────────────────────►│ 4. key exists & completed →          │
  │◄────────── SAME stored response ──────────│    return saved response, NO new work│

Edge cases:
  - Same key, still 'processing' → 409 Conflict ("in progress, retry later")
  - Same key, DIFFERENT body → 422 (key reused for another operation — client bug)
  - Keys expire after 24h–7d
```

### Other ways to achieve idempotency

```
1. Natural unique constraint
   orders(client_order_id UNIQUE) → INSERT ... ON CONFLICT DO NOTHING RETURNING *
2. Upsert / set state instead of increment
   UPDATE orders SET status='PAID' WHERE id=$1 AND status='PENDING'   (state machine)
   vs ❌ UPDATE wallet SET balance = balance - 500   (retry subtracts again)
3. Dedup table for message consumers
   processed_messages(message_id PRIMARY KEY) — insert in SAME transaction as the effect
4. Conditional requests (HTTP)
   If-Match: "etag-v3" → 412 if already changed
5. Idempotent producers (Kafka enable.idempotence) / exactly-once transactions
```

### Idempotent message consumers (very important with queues)

```
Queues (SQS, Kafka, RabbitMQ) deliver AT LEAST ONCE → duplicates WILL happen.

consume(msg):
  BEGIN
    INSERT INTO processed_messages(id) VALUES (msg.id)   -- fails if duplicate → skip
    ... apply effect (create shipment, send credit) ...
  COMMIT
  ACK msg
Crash after COMMIT but before ACK → redelivered → INSERT fails → skipped ✅
```

### Webhooks (receiving payments from Razorpay/Stripe)
```
Providers retry webhooks until you return 2xx → you WILL get duplicates.
Use the provider's event id (e.g. razorpay "id": "evt_...") as dedup key; verify signature first.
Process async: store event → return 200 fast → worker processes idempotently.
```

### Client responsibilities
```
✓ Generate key when the user INITIATES the action (on "Pay" tap), not per HTTP attempt
✓ Persist it (in memory + local storage for app restarts) until a final response
✓ Retry with SAME key on timeouts/5xx/network errors (with backoff)
✓ Disable the button / show "Processing…" to avoid double taps (UX + server protection)
```

## 🟢 कैसे काम करता है? (Hindi)
1. यूज़र "Pay" दबाता है → ऐप एक नई UUID (Idempotency-Key) बनाता है और हर retry में वही भेजता है।
2. सर्वर key को DB में UNIQUE रूप से सेव करता है — पहली request ही काम करती है।
3. काम पूरा होने पर response key के साथ सेव होता है।
4. वही key दोबारा आई → सर्वर नया काम नहीं करता, सेव किया response लौटा देता है। अलग body के साथ वही key → error।
5. Queue consumers में message id को dedup table में उसी transaction में डालो; webhooks में provider की event id से dedup।

---

## 🟡 Real World Example

**Stripe** — every POST accepts an `Idempotency-Key` header. Stripe stores the first response for 24 hours and replays it for retries with the same key. Their official SDKs auto-generate keys and retry safely. Stripe's engineering blog on idempotency is a classic.

**Razorpay / UPI** — orders have a unique `receipt`/order ID, and payments are tied to orders. Webhooks (`payment.captured`) can arrive multiple times, so merchants must deduplicate by event and payment ID. Double debits in UPI are reversed automatically, but merchants still must not ship twice.

**Uber/Swiggy order creation** — the app sends a client-generated request ID. If the user's network flickers during "Place Order", the retry returns the same order instead of creating a second one.

**AWS APIs** — many EC2 and other APIs accept a `ClientToken` for idempotent instance launches, so retries don't launch duplicate servers.

## 🟡 Real Example Hindi में
Stripe हर POST पर `Idempotency-Key` लेता है और 24 घंटे तक पहला response दोबारा देता है — retry से दो बार पैसे नहीं कटते।
Razorpay के webhooks कई बार आ सकते हैं — merchants event id से dedup करते हैं। Swiggy में "Place Order" के समय नेटवर्क टूटे तो retry पर वही order मिलता है, नया नहीं।

---

## 🟠 My Stack Example

### Postgres table
```sql
CREATE TABLE idempotency_keys (
  key            TEXT NOT NULL,
  user_id        BIGINT NOT NULL,
  request_hash   TEXT NOT NULL,
  status         TEXT NOT NULL DEFAULT 'processing',   -- processing | completed
  response_code  INT,
  response_body  JSONB,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, key)                           -- scope keys per user
);
-- cleanup job: DELETE FROM idempotency_keys WHERE created_at < now() - interval '7 days';
```

### Express middleware (reusable)
```js
import crypto from 'node:crypto';
const hash = (o) => crypto.createHash('sha256').update(JSON.stringify(o)).digest('hex');

export function idempotent() {
  return async (req, res, next) => {
    const key = req.get('Idempotency-Key');
    if (!key) return res.status(400).json({ error: 'IDEMPOTENCY_KEY_REQUIRED' });
    const reqHash = hash({ path: req.path, body: req.body });

    const ins = await pool.query(
      `INSERT INTO idempotency_keys(key, user_id, request_hash) VALUES ($1,$2,$3)
       ON CONFLICT DO NOTHING RETURNING key`, [key, req.user.id, reqHash]);

    if (ins.rowCount === 0) {                                     // key seen before
      const { rows: [row] } = await pool.query(
        'SELECT * FROM idempotency_keys WHERE key=$1 AND user_id=$2', [key, req.user.id]);
      if (row.request_hash !== reqHash) return res.status(422).json({ error: 'KEY_REUSED_WITH_DIFFERENT_REQUEST' });
      if (row.status === 'processing') return res.status(409).json({ error: 'REQUEST_IN_PROGRESS' });
      return res.status(row.response_code).json(row.response_body);   // replay
    }

    // first time: capture the response to store it
    const originalJson = res.json.bind(res);
    res.json = (body) => {
      pool.query(`UPDATE idempotency_keys SET status='completed', response_code=$1, response_body=$2
                  WHERE key=$3 AND user_id=$4`, [res.statusCode, body, key, req.user.id])
          .catch((e) => logger.error({ e }, 'store idempotent response failed'));
      return originalJson(body);
    };
    res.on('close', () => {   // on crash/5xx before completion, release key so client can retry
      if (res.statusCode >= 500)
        pool.query("DELETE FROM idempotency_keys WHERE key=$1 AND user_id=$2 AND status='processing'", [key, req.user.id]).catch(() => {});
    });
    next();
  };
}

app.post('/api/v1/orders', authenticate, idempotent(), createOrder);
app.post('/api/v1/payments', authenticate, idempotent(), createPayment);
```
(For full safety, do the business write and the "completed" update in the **same DB transaction**.)

### Simpler: natural idempotency with a unique client id
```sql
ALTER TABLE orders ADD COLUMN client_request_id UUID UNIQUE;
INSERT INTO orders(user_id, total, client_request_id) VALUES ($1, $2, $3)
ON CONFLICT (client_request_id) DO UPDATE SET client_request_id = EXCLUDED.client_request_id  -- no-op
RETURNING *;          -- always returns THE order, first time or retry
```

### Idempotent webhook handler (Razorpay) — FastAPI
```python
@app.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request):
    body = await request.body()
    sig = request.headers.get("X-Razorpay-Signature", "")
    expected = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        raise HTTPException(400, "bad signature")
    event = json.loads(body)
    event_id = request.headers.get("X-Razorpay-Event-Id") or event["payload"]["payment"]["entity"]["id"]
    async with session.begin():
        inserted = await session.execute(
            text("INSERT INTO processed_events(id) VALUES (:id) ON CONFLICT DO NOTHING RETURNING id"), {"id": event_id})
        if inserted.first() is None:
            return {"ok": True}                       # duplicate → already handled
        if event["event"] == "payment.captured":
            await mark_order_paid(session, event["payload"]["payment"]["entity"]["order_id"])   # state transition
    return {"ok": True}
```

### State-machine updates are naturally idempotent
```sql
UPDATE orders SET status = 'PAID', paid_at = now()
WHERE id = $1 AND status = 'PENDING_PAYMENT';      -- 2nd time: 0 rows, no harm
```

### React Native — key per action, reuse on retry
```ts
async function placeOrder(cart: Cart) {
  const key = cart.pendingRequestId ?? (cart.pendingRequestId = uuid.v4());   // persist with cart (MMKV)
  for (let attempt = 0; attempt < 4; attempt++) {
    try {
      const { data } = await api.post('/api/v1/orders', cart.payload, { headers: { 'Idempotency-Key': key }, timeout: 15000 });
      cart.pendingRequestId = undefined;
      return data;
    } catch (e: any) {
      const s = e.response?.status;
      if (s && s < 500 && s !== 409) throw e;                     // client error → don't retry
      await sleep(Math.random() * 1000 * 2 ** attempt);           // backoff + jitter
    }
  }
  throw new Error('Could not confirm order. Check "My Orders" before retrying.');
}
// UI: disable "Place Order" button while in flight
```

---

## ⚫ Interview Questions + Answers

**Q1: What is idempotency and why does it matter in distributed systems?**
A1: An operation is idempotent if repeating it has the same effect as doing it once. In distributed systems, clients can't distinguish a failed request from a lost response, and retries happen everywhere (mobile networks, load balancers, SDKs, at-least-once queues, webhooks). Without idempotency, retries cause duplicate charges, orders or messages. With it, retries are safe, which effectively gives exactly-once effects on top of at-least-once delivery.

**Q2: How do you implement an idempotency key for a payment API?**
A2: The client generates a unique key per logical operation and sends it in an `Idempotency-Key` header on every retry. The server atomically inserts the key (scoped per user, with a request fingerprint) into a store with a unique constraint and status "processing". The first request performs the work and saves the response. Subsequent requests with the same key replay the stored response, return 409 if still processing, or 422 if the payload differs. Keys expire after 24 hours to 7 days. Ideally the business write and key completion are in one transaction.

**Q3: Which HTTP methods are idempotent?**
A3: GET, HEAD, OPTIONS, PUT and DELETE are idempotent by definition (GET, HEAD and OPTIONS are also safe). POST is not, and PATCH may or may not be, depending on the operation (setting a value is, incrementing isn't). Idempotency is about server state, not identical responses: a second DELETE may return 404, but the state is the same.

**Q4: How do you make message queue consumers idempotent?**
A4: Assume duplicates. Give each message a unique ID. In the consumer, insert the ID into a processed-messages table inside the same database transaction that applies the effect. If the insert conflicts, skip. ACK only after commit. Alternatively design effects as upserts or state transitions (`UPDATE ... WHERE status='PENDING'`) that are naturally idempotent. Avoid side effects outside the transaction (emails), or make them idempotent too (dedup by message ID at the provider).

**Q5: A user double-tapped "Place Order" and the network was slow. How do you guarantee only one order?**
A5: Client-side: disable the button and show progress, and generate one idempotency key per checkout attempt that's reused on retries and persisted across app restarts. Server-side: an idempotency middleware or a unique `client_request_id` constraint, so both requests map to one order. The second gets the same response (or 409 while in progress). Payments are tied to the order ID, and webhook handlers dedupe by event ID. Reconciliation jobs catch anything missed.

---

## 🔷 Trade-offs
✅ Advantages:
- Safe retries everywhere; no duplicate charges/orders; enables at-least-once systems to be correct.

❌ Disadvantages:
- Extra storage and a lookup per request; key lifecycle management.
- Complexity in edge cases (in-progress requests, crashes mid-operation, different payloads).
- Requires client discipline (generate once, reuse on retry).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Idempotent | Same effect no matter how many times | कितनी भी बार, असर एक |
| Idempotency key | Unique id per logical operation | हर काम की अनोखी key |
| Retry | Sending the request again | दोबारा भेजना |
| At-least-once delivery | Messages may arrive multiple times | कम से कम एक बार (कई बार भी) |
| Exactly-once effect | Effect applied only once | असर सिर्फ़ एक बार |
| Deduplication | Detecting and skipping duplicates | दोहराव पहचानकर छोड़ना |
| Webhook | Server-to-server event callback | सर्वर से सर्वर event सूचना |
| State machine | Allowed status transitions | स्थिति बदलने के नियम |
| Upsert | Insert or update if exists | डालो या अपडेट करो |

---

## ⚡ 3-Line Summary
**English:**
1. Idempotent = repeating has the same effect; essential because retries and duplicate deliveries are unavoidable.
2. For POSTs use an Idempotency-Key (stored with unique constraint + saved response) or natural unique IDs; consumers/webhooks dedupe by message/event id in the same transaction.
3. Clients generate the key once per action, reuse it on retries, and prevent double taps.

**Hindi:**
1. Idempotent = बार-बार करने पर भी एक जैसा असर; retry और दोहराए मैसेज से बचाव के लिए ज़रूरी।
2. POST के लिए Idempotency-Key (unique + सेव response) या unique id; queue/webhooks में event id से dedup।
3. ऐप हर काम पर एक बार key बनाए, retry में वही भेजे, और double-tap रोके।

---

## ➡️ Next Topic Suggestion
**🎉 Auth, Security & API complete!** Next: **65. CAP Theorem** in `04-Distributed-Systems/`. Once data and services spread across machines and regions, you must choose between consistency and availability during network failures. That's the foundation of all distributed system design.
