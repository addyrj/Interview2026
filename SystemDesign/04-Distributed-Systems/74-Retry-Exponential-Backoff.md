# 74. Retry + Exponential Backoff
# हिंदी में: Retry + Exponential Backoff — फ़ेल हुई request को दोबारा भेजना, पर हर बार पहले से दुगुना इंतज़ार करके (1s, 2s, 4s, 8s…), ताकि सर्वर पर बोझ न बढ़े

---

## 🔵 Simple Definition (English)
A **retry** re-sends a request that failed due to a **transient error** (timeout, connection reset, 503, 429). **Exponential backoff** increases the wait between attempts exponentially (`base × 2^attempt`, e.g. 100 ms, 200 ms, 400 ms, 800 ms…), capped at a maximum and limited to a few attempts. It gives the failing system **time to recover** instead of flooding it.
It's almost always combined with **jitter** (randomness, next topic).

## 🔵 सरल परिभाषा (Hindi)
Retry यानी अस्थायी गड़बड़ी (timeout, 503, नेटवर्क टूटना) पर request दोबारा भेजना। Exponential backoff में हर retry से पहले इंतज़ार दुगुना होता है — 1s, 2s, 4s…
इससे सर्वर को संभलने का समय मिलता है; और retries की संख्या सीमित रखी जाती है।

---

## 🔴 Problem it Solves
Distributed systems have **constant transient failures**: network blips, a pod restarting during deploy, a DB failover (30 s), brief throttling (429), a GC pause. A single retry often turns a failure into a success, which is invisible to users.

But **naive retries are dangerous**:
- **Immediate retries in a tight loop** hammer an already overloaded service → it never recovers.
- **Retry amplification:** if each of 5 layers retries 3×, one user request can become 3⁵ = **243 calls** to the bottom service.
- **Non-idempotent retries** create duplicate orders or payments.

Exponential backoff + limits + idempotency make retries **helpful, not harmful**.

## 🔴 यह क्यों बना? (Hindi)
Distributed सिस्टम में छोटी-छोटी अस्थायी गड़बड़ियाँ लगातार होती हैं — एक retry से अक्सर काम बन जाता है।
पर तुरंत, बार-बार retry पहले से बीमार सर्वर को और गिरा देता है; 5 परतों में 3-3 retry = 243 गुना बोझ; और non-idempotent retry से दो बार ऑर्डर। Backoff + सीमा + idempotency से retry फ़ायदेमंद बनता है।

---

## 🟢 How it Works — Step by Step

### The formula

```
delay(attempt) = min(maxDelay, baseDelay × 2^attempt)     (+ jitter, Topic 75)

base = 200 ms, max = 10 s, maxAttempts = 5
attempt 0 → fail → wait 200 ms
attempt 1 → fail → wait 400 ms
attempt 2 → fail → wait 800 ms
attempt 3 → fail → wait 1.6 s
attempt 4 → fail → give up → return error / DLQ / fallback
Total worst case ≈ 3 s of waiting + attempt times (must fit the caller's deadline!)
```

### What to retry — and what NOT

```
✅ RETRY (transient):                      ❌ DON'T RETRY (permanent):
- Connection refused/reset, DNS hiccup     - 400 Bad Request, 422 Validation
- Timeouts (ONLY if operation idempotent)  - 401/403 (fix auth instead; maybe refresh token once)
- 502, 503, 504                            - 404 Not Found
- 429 Too Many Requests (honor Retry-After)- 409 Conflict (business conflict)
- Deadlock / serialization failure (DB)    - Business rule failures (insufficient balance)
- Kafka/SQS transient broker errors        - 500 caused by a bug (retrying won't fix it… usually)

⚠️ Non-idempotent operations (POST /payments): retry ONLY with an Idempotency-Key (Topic 64)
```

### Retry amplification — the big danger

```
Mobile app (3 tries) → API Gateway (3) → Order Svc (3) → Payment Svc (3) → Bank API
One user tap = up to 3 × 3 × 3 × 3 = 81 calls to the Bank API during an outage 💥

Fixes:
1. Retry at ONE layer (usually closest to the user, or at the edge of the failing call)
2. Retry budgets: allow retries only up to e.g. 10% of total requests (Envoy, gRPC, Finagle)
3. Circuit breakers stop retries when dependency is down (Topic 73)
4. Propagate deadlines: if the caller has 2s left, don't start a 5s retry chain
5. Honor overload signals (Retry-After, "don't retry" hints) → longer backoff or shed load
```

### Where retries are built in (know them)
```
AWS SDKs: exponential backoff + jitter by default ("standard"/"adaptive" retry modes)
gRPC: retry policy in service config; hedging
Kafka producer: retries + idempotent producer
SQS/Lambda: redelivery after visibility timeout; DLQ after maxReceiveCount
BullMQ/Celery: attempts + backoff config per job
HTTP clients: axios-retry, got (built-in), urllib3 Retry, tenacity (Python)
React Query / SWR: retry + exponential retryDelay by default
```

### Retries for background jobs vs user requests
```
User-facing request: few retries (1–3), short total time (fit in ~2–5 s), then fail fast/fallback
Background job/queue: many retries over minutes/hours (exponential up to e.g. 1 h), then DLQ (Topic 86)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Request फ़ेल हुई → देखो error अस्थायी है या स्थायी; सिर्फ़ अस्थायी (timeout, 503, 429, नेटवर्क) पर retry।
2. इंतज़ार = base × 2^attempt (200ms, 400ms, 800ms…), एक अधिकतम सीमा तक, और 3-5 कोशिशों के बाद रुक जाओ।
3. 429 में `Retry-After` का पालन करो; non-idempotent काम (पेमेंट) सिर्फ़ Idempotency-Key के साथ retry।
4. ख़तरा: हर परत retry करे तो बोझ कई गुना — सिर्फ़ एक परत पर retry, retry budget, और circuit breaker।
5. यूज़र request में कम retries और कम समय; background jobs में ज़्यादा retries, फिर DLQ।

---

## 🟡 Real World Example

**AWS** — all AWS SDKs implement exponential backoff with jitter by default. AWS's Builders' Library article "Timeouts, retries and backoff with jitter" is the industry reference, and it warns about retry amplification across layers.

**Google SRE book** — describes cascading failures caused by retries and recommends per-request retry limits, retry budgets (≤10% extra load), and server-side signals telling clients not to retry when overloaded.

**Mobile apps on Indian networks** — apps like PhonePe and Swiggy retry idempotent GETs with backoff when switching from Wi-Fi to 4G or in elevators, while payment POSTs use idempotency keys plus a status check before any retry.

**The 2015 AWS DynamoDB outage (us-east-1)** — a metadata service got overloaded and client retries amplified the load, prolonging the outage until capacity was added and request rates were throttled.

## 🟡 Real Example Hindi में
AWS के सारे SDKs default में exponential backoff + jitter करते हैं। Google SRE book बताती है कि ग़लत retries से पूरा सिस्टम गिर सकता है, इसलिए retry budget (≤10%) रखो।
2015 में AWS DynamoDB के outage में clients के retries ने बोझ और बढ़ा दिया और outage लंबा चला।

---

## 🟠 My Stack Example

### Node.js — generic retry helper (with jitter and retryable check)
```js
export async function retry(fn, {
  attempts = 4, baseMs = 200, maxMs = 5000,
  isRetryable = (e) => ['ECONNRESET', 'ETIMEDOUT', 'ECONNREFUSED', 'EAI_AGAIN'].includes(e.code) || [429, 502, 503, 504].includes(e.status),
  deadline = Date.now() + 10_000,
} = {}) {
  for (let i = 0; ; i++) {
    try { return await fn(i); }
    catch (e) {
      if (i >= attempts - 1 || !isRetryable(e)) throw e;
      const retryAfter = e.retryAfterMs;                                   // from 429 Retry-After
      const backoff = Math.min(maxMs, baseMs * 2 ** i);
      const delay = retryAfter ?? Math.random() * backoff;                 // full jitter (Topic 75)
      if (Date.now() + delay > deadline) throw e;                          // respect caller's deadline
      await new Promise((r) => setTimeout(r, delay));
    }
  }
}

// usage: idempotent GET to partner API
const eta = await retry(() => fetchJson(`${MAPS}/eta?o=${o}&d=${d}`, { timeoutMs: 1500 }));

// non-idempotent POST: same idempotency key across attempts
const key = crypto.randomUUID();
await retry(() => fetchJson(`${PAY}/charges`, { method: 'POST', headers: { 'Idempotency-Key': key }, body }));
```

### axios-retry (web & React Native)
```ts
import axiosRetry from 'axios-retry';
axiosRetry(api, {
  retries: 3,
  retryDelay: axiosRetry.exponentialDelay,                       // includes randomization
  retryCondition: (err) =>
    axiosRetry.isNetworkOrIdempotentRequestError(err) || err.response?.status === 429,
});
```

### React Query defaults (already exponential)
```ts
new QueryClient({ defaultOptions: {
  queries: { retry: (count, err: any) => count < 3 && (!err.response || err.response.status >= 500),
             retryDelay: (n) => Math.min(1000 * 2 ** n, 15000) },
  mutations: { retry: 0 },                                       // don't auto-retry writes blindly
}});
```

### Python — tenacity
```python
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type
import httpx

@retry(stop=stop_after_attempt(4), wait=wait_random_exponential(multiplier=0.2, max=5),
       retry=retry_if_exception_type((httpx.TransportError, httpx.HTTPStatusError)), reraise=True)
async def call_partner(payload):
    async with httpx.AsyncClient(timeout=2.0) as c:
        r = await c.post(PARTNER_URL, json=payload, headers={"Idempotency-Key": payload["id"]})
        if r.status_code in (429, 502, 503, 504): r.raise_for_status()
        return r.json()
```

### Background jobs (BullMQ) — long exponential backoff + DLQ
```js
await queue.add('send-invoice', { orderId }, {
  attempts: 8,
  backoff: { type: 'exponential', delay: 2000 },       // 2s, 4s, 8s ... ~4 min
  removeOnFail: false,                                  // keep failed jobs (acts as DLQ for inspection)
});
```

### DB transaction retry
Retry on serialization failures and deadlocks (SQLSTATE 40001 / 40P01) using the `withTx` helper from Topic 33.

---

## ⚫ Interview Questions + Answers

**Q1: What is exponential backoff and why use it?**
A1: A retry strategy where the delay between attempts grows exponentially (base × 2^n, capped at a maximum), with a limited number of attempts. It gives an overloaded or recovering dependency time to recover, spreads retry load over time, and avoids hammering. It's combined with jitter so clients don't retry in sync.

**Q2: Which errors should be retried?**
A2: Transient ones: network errors, connection resets and refusals, DNS hiccups, timeouts (only for idempotent operations or with idempotency keys), 502, 503 and 504, 429 (respecting Retry-After), and DB deadlocks or serialization failures. Don't retry client errors (400, 401, 403, 404, 409, 422), business rule failures or deterministic bugs, since retrying wastes resources and can't succeed.

**Q3: What is retry amplification and how do you prevent it?**
A3: When multiple layers each retry, a single failure multiplies into many downstream calls (3 retries across 4 layers is up to 81 calls), which can turn a partial outage into a full one. Prevent it by retrying at a single layer, using retry budgets (cap retries as a percentage of traffic), circuit breakers, propagating deadlines and timeouts, honouring server overload signals (Retry-After, "don't retry" hints), and adding jitter.

**Q4: How do you safely retry a non-idempotent request like creating a payment?**
A4: Attach a unique idempotency key generated once per logical operation and reused on every retry. The server deduplicates and returns the original result. If unsure whether the first attempt succeeded (timeout), query the operation's status before retrying, or rely on the provider's idempotency. Never blindly retry POSTs without this.

**Q5: How many retries and what delays would you configure for a user-facing API call vs a background job?**
A5: User-facing: 1–3 retries with small exponential delays (e.g. 100 ms–1 s, jittered), within a total deadline that matches UX tolerance (2–5 s), then fail fast with a fallback or clear error. Background job: more attempts (e.g. 5–10) with exponential backoff growing to minutes or an hour, then move to a dead-letter queue for inspection or alerting, with idempotent processing throughout.

---

## 🔷 Trade-offs
✅ Advantages:
- Masks transient failures; improves success rate and UX; simple to add with libraries.

❌ Disadvantages:
- Increases latency; can amplify load and cause cascading failures if misused.
- Dangerous for non-idempotent operations without keys.
- Needs coordination with timeouts, deadlines, breakers.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Retry | Sending the request again | दोबारा भेजना |
| Exponential backoff | Delay doubles each attempt | हर बार दुगुना इंतज़ार |
| Transient error | Temporary failure | अस्थायी गड़बड़ी |
| Max attempts | Retry limit | अधिकतम कोशिशें |
| Retry amplification | Retries multiplying across layers | परतों में retries का गुणा |
| Retry budget | Cap on retry traffic % | retry की सीमा |
| Deadline propagation | Pass remaining time downstream | बचा समय आगे भेजना |
| Dead-letter queue | Holding failed messages | फ़ेल मैसेज की अलग queue |
| Retry-After | Server says when to retry | कब दोबारा कोशिश करें |

---

## ⚡ 3-Line Summary
**English:**
1. Retry transient failures with exponential backoff (base × 2^n, capped) + jitter, few attempts, within a deadline.
2. Retry only retryable errors; retry non-idempotent ops only with idempotency keys.
3. Prevent amplification: retry at one layer, retry budgets, circuit breakers; background jobs retry longer then DLQ.

**Hindi:**
1. अस्थायी गड़बड़ी पर exponential backoff (दुगुना इंतज़ार) + jitter के साथ सीमित retry।
2. सिर्फ़ retry लायक errors पर; पेमेंट जैसे काम सिर्फ़ Idempotency-Key के साथ।
3. एक ही परत पर retry, retry budget, circuit breaker; background jobs में ज़्यादा retry फिर DLQ।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [ByteByteGo — Retry and Backoff](https://www.youtube.com/results?search_query=retry+exponential+backoff+system+design+bytebytego) | Why naive retry causes thundering herd, jitter fix |
| 📝 Article | [AWS — Exponential Backoff and Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) | AWS blog: the definitive explanation with math and charts |
| 📝 Article | [Google Cloud — Retry strategy](https://cloud.google.com/storage/docs/retry-strategy) | Idempotency, deadlines, per-RPC vs per-call retry |
| 📝 Article | [Stripe — Idempotent requests](https://stripe.com/docs/idempotency) | How Stripe handles retries safely in payments |
| 🐙 GitHub | [async-retry](https://github.com/vercel/async-retry) | Tiny Node.js retry library — read to understand backoff in 50 lines |

---

## ➡️ Next Topic Suggestion
**75. Jitter** — Backoff alone isn't enough: if 10,000 clients fail at the same moment, they all retry at the same moments too. Next: adding randomness (jitter) to break synchronization.
