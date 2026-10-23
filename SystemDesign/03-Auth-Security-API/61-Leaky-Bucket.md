# 61. Leaky Bucket Algorithm
# हिंदी में: Leaky Bucket — नीचे छेद वाली बाल्टी: requests ऊपर से कितनी भी तेज़ आएँ, नीचे से एक तय, समान रफ़्तार से ही निकलती हैं; बाल्टी भरी तो नई requests गिरा दी जाती हैं

---

## 🔵 Simple Definition (English)
In the **leaky bucket** algorithm, incoming requests are put into a **queue (the bucket) of fixed size**. Requests **leak out (are processed) at a constant rate**, e.g. 10/second. If requests arrive faster than they leak and the bucket is **full**, new requests are **dropped (rejected)**.
Result: a **smooth, constant output rate**, with bursts absorbed by the queue rather than passed downstream.

## 🔵 सरल परिभाषा (Hindi)
Leaky bucket एक क़तार (queue) है जिसका आकार तय है। requests कितनी भी तेज़ आएँ, उन्हें एक समान रफ़्तार (जैसे 10/सेकंड) से ही आगे भेजा जाता है।
क़तार भर जाए तो नई requests मना कर दी जाती हैं। इससे पीछे वाले सिस्टम पर हमेशा एक जैसा, शांत बोझ जाता है।

---

## 🔴 Problem it Solves
Some downstream systems **can't handle bursts at all**:
- An **SMS/email provider** that allows exactly 100 messages/second.
- A **legacy bank/core system** that falls over above 50 TPS.
- A **payment partner** API with strict per-second contracts.
- **Network links** (the original use): smoothing packet bursts to fit the line rate.

A token bucket would let a burst of 1,000 through instantly. A leaky bucket **smooths** traffic so the downstream always sees a steady rate. It's traffic **shaping**, not just limiting.

## 🔴 यह क्यों बना? (Hindi)
कुछ सिस्टम अचानक की भीड़ बिल्कुल नहीं सह सकते — SMS provider (100/सेकंड), पुराना बैंक सिस्टम (50 TPS), सख़्त partner API।
Token bucket एक साथ 1000 requests जाने देगा; leaky bucket उन्हें queue में रखकर समान रफ़्तार से भेजता है — इसे traffic shaping कहते हैं।

---

## 🟢 How it Works — Step by Step

```
     bursty incoming requests
       ▼ ▼ ▼▼▼▼ ▼   ▼▼▼▼▼▼▼
   ┌──────────────────────┐
   │  ▒▒▒▒▒▒▒▒▒▒▒▒▒       │  bucket = FIFO queue, capacity C (e.g. 100)
   │  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒     │  full? → new request DROPPED (429 / reject)
   └──────────┬───────────┘
              │  leaks at constant rate R (e.g. 10/s)
              ▼
     ● . . ● . . ● . . ●     smooth, evenly spaced output → downstream
```

```
Step 1 → Request arrives
Step 2 → If queue length < capacity → enqueue; else reject
Step 3 → A worker/scheduler dequeues one request every 1/R seconds and processes/forwards it
Step 4 → Output rate never exceeds R, regardless of input burstiness
```

### Two flavours

```
1. Leaky bucket AS A QUEUE (shaper)
   - requests wait in queue → processed at fixed rate
   - adds LATENCY (queueing delay) but never overloads downstream
   - e.g. outgoing SMS queue, job workers with fixed concurrency/rate

2. Leaky bucket AS A METER (policer) — no actual queue
   - track "water level" = count that decreases at rate R over time
   - request arrives: level = max(0, level - elapsed×R); if level + 1 ≤ C → allow, level += 1; else reject
   - mathematically equivalent to a token bucket (mirror image) → this is what Nginx limit_req does
   - "GCRA" (Generic Cell Rate Algorithm) is an efficient form of this (used by redis-cell, Shopify-like limiters)
```

### Leaky bucket vs token bucket

```
┌──────────────────┬───────────────────────────────┬────────────────────────────────┐
│                  │ Token bucket                  │ Leaky bucket (queue)           │
├──────────────────┼───────────────────────────────┼────────────────────────────────┤
│ Bursts           │ Allowed up to capacity        │ Absorbed in queue, smoothed    │
│ Output rate      │ Can be bursty                 │ Constant                       │
│ Excess requests  │ Rejected when no tokens       │ Queued; rejected when full     │
│ Latency          │ No added delay                │ Adds queueing delay            │
│ Best for         │ User-facing APIs              │ Protecting fragile downstreams,│
│                  │                               │ outbound calls, network shaping│
└──────────────────┴───────────────────────────────┴────────────────────────────────┘
```

### Nginx limit_req = leaky bucket
```
limit_req zone=api rate=10r/s;                → leak rate 10/s, no queue → excess rejected
limit_req zone=api rate=10r/s burst=20;       → queue up to 20 excess, released at 10/s (delayed)
limit_req zone=api rate=10r/s burst=20 nodelay; → allow 20 burst immediately, then 10/s
                                                (behaves like token bucket with capacity 20)
```

## 🟢 कैसे काम करता है? (Hindi)
1. आने वाली requests एक तय आकार की queue (बाल्टी) में जाती हैं।
2. एक worker हर 1/R सेकंड में एक request निकालकर आगे भेजता है — रफ़्तार हमेशा R।
3. Queue भरी हो तो नई request मना (429)।
4. नुक़सान: requests को queue में इंतज़ार करना पड़ता है (latency); फ़ायदा: पीछे का सिस्टम कभी ओवरलोड नहीं होता।
5. Nginx का `limit_req` leaky bucket है; `burst` = queue का आकार, `nodelay` से यह token bucket जैसा बन जाता है।

---

## 🟡 Real World Example

**Shopify API** — historically used a **leaky bucket** for REST Admin API limits: a bucket of 40 requests that leaks at 2 per second per store, exposed via the `X-Shopify-Shop-Api-Call-Limit: 32/40` header. App developers had to pace their calls.

**SMS / WhatsApp / email sending (MSG91, Twilio, Amazon SES)** — providers enforce per-second send rates. Companies queue outgoing messages and send them at a steady rate, so a campaign of 1M messages doesn't get throttled or blocked.

**Bank and NPCI integrations** — payment aggregators shape traffic towards each bank to stay within agreed TPS, queuing excess briefly and failing fast when queues overflow.

**Networking (ATM, routers)** — the original leaky bucket/GCRA was designed for ATM networks to police cell rates. Linux traffic control (`tc tbf`) shapes bandwidth similarly.

## 🟡 Real Example Hindi में
Shopify API पहले leaky bucket इस्तेमाल करती थी — हर store की 40 requests की बाल्टी, जो 2/सेकंड से ख़ाली होती थी; header में "32/40" दिखता था।
SMS/WhatsApp campaign में 10 लाख मैसेज queue में डालकर provider की तय रफ़्तार से भेजे जाते हैं, ताकि block न हों।

---

## 🟠 My Stack Example

### Outbound shaping with BullMQ (Redis queue) — exactly a leaky bucket
```js
import { Queue, Worker } from 'bullmq';
const smsQueue = new Queue('sms', { connection: redisConn });

// Producer: API enqueues instantly (bucket). Reject if backlog too large (bucket full).
app.post('/api/v1/campaigns/:id/send', authenticate, async (req, res) => {
  const waiting = await smsQueue.getWaitingCount();
  if (waiting > 1_000_000) return res.status(429).json({ error: 'QUEUE_FULL' });
  await smsQueue.addBulk(req.body.recipients.map((to) => ({ name: 'send', data: { to, text: req.body.text } })));
  res.status(202).json({ queued: req.body.recipients.length });
});

// Consumer: leaks at a constant rate — max 100 jobs per second across ALL workers
new Worker('sms', async (job) => smsProvider.send(job.data.to, job.data.text), {
  connection: redisConn,
  limiter: { max: 100, duration: 1000 },       // global rate limit (BullMQ uses Redis)
  concurrency: 20,
});
```

### Nginx shaping inbound traffic to a fragile service
```nginx
limit_req_zone $server_name zone=legacy:1m rate=50r/s;   # GLOBAL (keyed by server), not per IP
location /legacy/ {
  limit_req zone=legacy burst=100;      # queue up to 100, released at 50/s (adds delay)
  proxy_pass http://legacy_core;
}
```

### GCRA (leaky bucket as meter) in Redis — redis-cell module
```bash
CL.THROTTLE user:42 15 30 60 1
#           key     burst  count/period(30 per 60s)  cost
# → [0 = allowed/1 = limited, limit, remaining, retry_after_s, reset_after_s]
```

### Python asyncio — constant-rate dispatcher
```python
class LeakyBucket:
    def __init__(self, rate_per_sec: float, capacity: int):
        self.q: asyncio.Queue = asyncio.Queue(maxsize=capacity)
        self.interval = 1 / rate_per_sec

    def submit(self, coro_fn) -> bool:
        try: self.q.put_nowait(coro_fn); return True
        except asyncio.QueueFull: return False          # bucket full → reject

    async def run(self):
        while True:
            fn = await self.q.get()
            asyncio.create_task(fn())                   # process
            await asyncio.sleep(self.interval)          # constant leak rate

bank_bucket = LeakyBucket(rate_per_sec=50, capacity=500)
# on startup: asyncio.create_task(bank_bucket.run())
```

### Mobile angle
- A React Native app syncing 5,000 offline records shouldn't fire 5,000 requests at once. Process a local queue at a steady rate (e.g. 5 per second) with batching. That's a client-side leaky bucket, which keeps your API and the user's battery happy.

---

## ⚫ Interview Questions + Answers

**Q1: Explain the leaky bucket algorithm.**
A1: Requests enter a fixed-capacity FIFO queue (the bucket) and are processed or forwarded at a constant rate R (the leak). If requests arrive faster than R, they accumulate. When the queue is full, new arrivals are dropped. The output is perfectly smooth regardless of input bursts, at the cost of queueing delay. A "meter" variant tracks a level that drains at R and rejects instead of queuing, which is equivalent to a token bucket (GCRA).

**Q2: Token bucket vs leaky bucket?**
A2: Both control average rate. A token bucket allows bursts up to its capacity to pass immediately (bursty output), which is good for user-facing APIs. A leaky bucket (as a queue) emits at a constant rate, smoothing bursts into delay, which is good for protecting fragile downstream systems or meeting strict per-second contracts. As meters without a queue, they're mathematically equivalent, with tokens as the inverse of water level.

**Q3: Where would you use a leaky bucket in a real system?**
A3: Outbound integrations with strict rate limits (SMS, email, push providers, bank and payment partners, third-party APIs), job processing where workers must not exceed DB or partner capacity, smoothing writes to a legacy system, network traffic shaping, and webhook delivery to customers (pace deliveries per endpoint).

**Q4: What are the downsides of the queue-based leaky bucket?**
A4: Added latency, since requests wait in the queue, which is bad for interactive APIs where users expect fast responses or failures. Memory or storage for the queue, and possible stale work if requests sit too long (add TTLs or deadlines). And a full queue still rejects requests, so you need backpressure signalling to producers. Size the queue by the acceptable wait time (capacity / R = maximum delay).

**Q5: How does Nginx's `limit_req` relate to leaky bucket?**
A5: Nginx `limit_req` implements a leaky bucket. `rate` is the leak rate. Without `burst`, excess requests are rejected (pure policing). With `burst=N`, up to N excess requests are queued and released at the configured rate (shaping, adding delay). With `burst=N nodelay`, the burst is served immediately but its slots are freed at the rate, which behaves like a token bucket with capacity N.

---

## 🔷 Trade-offs
✅ Advantages:
- Perfectly smooth output; protects fragile downstreams; simple to reason about (max rate = R).

❌ Disadvantages:
- Adds queueing latency; bursts aren't served fast.
- Queue memory and stale requests; drops when full.
- Less friendly for interactive user traffic than token bucket.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Leaky bucket | Queue drained at constant rate | समान रफ़्तार से ख़ाली होने वाली क़तार |
| Leak rate | Fixed processing rate | निकलने की तय रफ़्तार |
| Bucket capacity | Max queued requests | queue का अधिकतम आकार |
| Traffic shaping | Smoothing output over time | ट्रैफ़िक को समान करना |
| Policing | Dropping excess without queue | ज़्यादा requests सीधे गिराना |
| GCRA | Efficient leaky-bucket meter | leaky bucket का तेज़ रूप |
| Backpressure | Signal producers to slow down | भेजने वाले को धीमा करने का संकेत |
| Queueing delay | Wait time in queue | queue में इंतज़ार |

---

## ⚡ 3-Line Summary
**English:**
1. Leaky bucket = fixed-size queue drained at constant rate R; excess dropped when full → smooth output.
2. Great for protecting downstreams and outbound integrations (SMS, banks, partners); adds latency.
3. Token bucket allows bursts (APIs); leaky bucket smooths them (shaping); Nginx limit_req is a leaky bucket.

**Hindi:**
1. Leaky bucket = तय आकार की queue, समान रफ़्तार से ख़ाली; भरी तो नई requests मना।
2. पीछे के कमज़ोर सिस्टम और SMS/बैंक/partner calls के लिए बढ़िया; इंतज़ार बढ़ता है।
3. Token bucket burst देता है, leaky bucket समान करता है; Nginx limit_req leaky bucket है।

---

## ➡️ Next Topic Suggestion
**62. Sliding Window Algorithm** — Fixed windows have edge bursts and logs use too much memory. Next: the sliding window log and sliding window counter, the accurate and cheap approach used by many API gateways.
