# 243. Circuit Breaker in Node
# हिंदी में: Node में Circuit Breaker

---

## 🔵 Simple Definition (English)
A circuit breaker is a pattern that stops a service from repeatedly calling a dependency that's known to be failing, instead "failing fast" with a fallback response — just like an electrical circuit breaker trips to stop current flow when there's a fault, preventing cascading damage to the rest of the system.

## 🔵 सरल परिभाषा (Hindi)
Circuit breaker एक pattern है जो किसी service को उस dependency को बार-बार call करने से रोकता है जो known रूप से fail हो रही है, इसके बजाय "fail fast" करता है एक fallback response के साथ — exactly जैसे electrical circuit breaker fault होने पर current flow रोकने के लिए trip करता है, बाकी system को cascading damage से बचाता है।

---

## 🔴 Problem it Solves
When Service A calls Service B and B is down or extremely slow, A's requests pile up waiting on B (each hanging until its timeout), exhausting A's own connection pool/memory/threads — this can cascade and take DOWN Service A too, even though A's own logic is fine. The circuit breaker solves this by detecting repeated failures to B, then "opening" to immediately reject/fallback further calls to B without even trying — protecting A's resources and giving B time to recover without being hammered by retries.

## 🔴 यह क्यों बना? (Hindi)
जब Service A, Service B को call करता है और B down या extremely slow है, A की requests B का wait करते हुए ढेर हो जाती हैं (हर एक अपने timeout तक hang होती है), A का अपना connection pool/memory/threads खत्म हो जाता है — यह cascade होकर Service A को भी DOWN कर सकता है, भले ही A की अपनी logic ठीक हो। Circuit breaker B की repeated failures detect करके, फिर "open" होकर आगे की calls को बिना try किए immediately reject/fallback करके यह solve करता है — A के resources protect करता है और B को recover होने का time देता है बिना retries से hammer हुए।

---

## 🟢 How it Works — Step by Step

Step 1 → The circuit breaker wraps calls to a potentially unreliable dependency and starts in the **CLOSED** state (calls pass through normally).
Step 2 → It tracks failures (errors, timeouts) over a rolling window.
Step 3 → If failures exceed a configured threshold (e.g., 50% of the last 20 requests failed), the breaker trips to the **OPEN** state.
Step 4 → While OPEN, calls to the dependency are immediately rejected/fallback-handled WITHOUT even attempting the real call — this is the "fail fast" behavior.
Step 5 → After a cooldown period, the breaker moves to **HALF-OPEN**, allowing a small number of test calls through to check if the dependency has recovered.
Step 6 → If test calls succeed, the breaker closes again (resumes normal operation); if they fail, it goes back to OPEN and waits longer before trying again.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Circuit breaker किसी potentially unreliable dependency की calls को wrap करता है और **CLOSED** state में शुरू होता है (calls normally pass through होती हैं)।
Step 2 → यह rolling window में failures (errors, timeouts) track करता है।
Step 3 → अगर failures configured threshold से ज्यादा हों (जैसे last 20 requests में से 50% fail), breaker **OPEN** state में trip करता है।
Step 4 → OPEN रहते हुए, dependency की calls immediately reject/fallback-handled होती हैं बिना real call try किए — यह "fail fast" behavior है।
Step 5 → एक cooldown period के बाद, breaker **HALF-OPEN** में जाता है, कुछ test calls को pass होने देता है यह check करने के लिए कि dependency recover हुआ है या नहीं।
Step 6 → अगर test calls succeed होती हैं, breaker फिर close हो जाता है (normal operation resume); अगर fail होती हैं, वापस OPEN हो जाता है और फिर try करने से पहले ज्यादा wait करता है।

---

## 🟡 Real World Example
**Razorpay calling a third-party bank API:** When a partner bank's API becomes slow/unresponsive during an outage, without a circuit breaker, every incoming payment request would hang waiting on the bank API's timeout (say 30s), quickly exhausting Razorpay's connection pool and threads, potentially taking down the ENTIRE payment service for ALL banks, not just the one having issues. A circuit breaker around calls to that specific bank's API trips open after detecting repeated failures, instantly failing those specific requests with a clear "bank temporarily unavailable" response (or routing to a backup bank), while payments to OTHER banks continue working normally.

## 🟡 Real Example Hindi mein
**Razorpay किसी third-party bank API को call करते हुए:** जब एक partner bank का API outage के दौरान slow/unresponsive हो जाए, बिना circuit breaker के, हर आने वाली payment request bank API के timeout (मान लो 30s) तक hang होगी, जल्दी ही Razorpay का connection pool और threads खत्म हो जाएंगे, शायद पूरी payment service को ALL banks के लिए down कर देगा, सिर्फ issue वाले bank के लिए नहीं। उस specific bank के API calls के around circuit breaker repeated failures detect करके open हो जाता है, उन specific requests को instantly एक clear "bank temporarily unavailable" response से fail करता है (या backup bank पर route करता है), जबकि OTHER banks की payments normally काम करती रहती हैं।

---

## 💻 Code Example — Basic

```javascript
// circuit-breaker-basic.js — manual, minimal circuit breaker implementation
// Run: node circuit-breaker-basic.js

class CircuitBreaker {
  constructor(fn, { failureThreshold = 3, cooldownMs = 5000 } = {}) {
    this.fn = fn;                      // the risky function to wrap (e.g., an API call)
    this.failureThreshold = failureThreshold;
    this.cooldownMs = cooldownMs;
    this.failureCount = 0;
    this.state = 'CLOSED';             // CLOSED | OPEN | HALF_OPEN
    this.nextAttemptTime = 0;
  }

  async call(...args) {
    if (this.state === 'OPEN') {
      if (Date.now() < this.nextAttemptTime) {
        throw new Error('Circuit is OPEN — failing fast without calling dependency');
      }
      this.state = 'HALF_OPEN';   // cooldown passed, allow a test call
    }

    try {
      const result = await this.fn(...args);
      this.onSuccess();
      return result;
    } catch (err) {
      this.onFailure();
      throw err;
    }
  }

  onSuccess() {
    this.failureCount = 0;
    this.state = 'CLOSED';   // recovery confirmed, back to normal
  }

  onFailure() {
    this.failureCount++;
    if (this.failureCount >= this.failureThreshold) {
      this.state = 'OPEN';
      this.nextAttemptTime = Date.now() + this.cooldownMs;
      console.log('Circuit OPENED — failing fast for', this.cooldownMs, 'ms');
    }
  }
}

// Simulate an unreliable dependency
async function unreliableBankApi() {
  if (Math.random() < 0.8) throw new Error('Bank API timeout');
  return { status: 'success' };
}

const breaker = new CircuitBreaker(unreliableBankApi, { failureThreshold: 3, cooldownMs: 3000 });

(async () => {
  for (let i = 0; i < 8; i++) {
    try {
      const result = await breaker.call();
      console.log(`Call ${i}: SUCCESS`, result);
    } catch (err) {
      console.log(`Call ${i}: FAILED — ${err.message}`);
    }
    await new Promise(r => setTimeout(r, 500));
  }
})();
```

## 💻 Code Example — Advanced

```javascript
// circuit-breaker-advanced.js — using the `opossum` library with fallback
// Run: node circuit-breaker-advanced.js (requires npm i opossum axios)

const CircuitBreaker = require('opossum');
const axios = require('axios');

// The risky operation: calling an external bank API
async function callBankApi(paymentData) {
  const response = await axios.post('http://bank-api.example.com/process', paymentData, { timeout: 2000 });
  return response.data;
}

const options = {
  timeout: 2000,                  // if callBankApi takes longer than this, count as failure
  errorThresholdPercentage: 50,   // open the circuit if 50% of requests fail
  resetTimeout: 10000,            // after 10s in OPEN state, try HALF_OPEN
  rollingCountTimeout: 10000,     // 10s rolling window for failure percentage calculation
};

const breaker = new CircuitBreaker(callBankApi, options);

// FALLBACK: executed immediately when the circuit is open or the call fails
breaker.fallback((paymentData, err) => {
  console.warn('Fallback triggered:', err?.message);
  return { status: 'queued', message: 'Bank temporarily unavailable, payment queued for retry' };
});

// Event hooks for monitoring/alerting
breaker.on('open', () => console.log('🔴 Circuit OPENED — bank API failing'));
breaker.on('halfOpen', () => console.log('🟡 Circuit HALF-OPEN — testing recovery'));
breaker.on('close', () => console.log('🟢 Circuit CLOSED — bank API healthy again'));

async function processPayment(paymentData) {
  try {
    const result = await breaker.fire(paymentData);
    return result;
  } catch (err) {
    // This only throws if even the fallback fails
    throw new Error('Payment processing completely unavailable: ' + err.message);
  }
}

processPayment({ amount: 500, orderId: 'order_1' }).then(console.log);
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const CircuitBreaker = require('opossum');
const axios = require('axios');

const app = express();
app.use(express.json());

async function callInventoryService(itemId) {
  const res = await axios.get(`http://inventory-service:4003/items/${itemId}`, { timeout: 1500 });
  return res.data;
}

const inventoryBreaker = new CircuitBreaker(callInventoryService, {
  timeout: 1500,
  errorThresholdPercentage: 50,
  resetTimeout: 5000,
});

inventoryBreaker.fallback(() => ({ stock: 'unknown', message: 'Using cached/default stock info' }));

app.get('/products/:id/availability', async (req, res) => {
  // Even if Inventory Service is down, this endpoint responds quickly with a fallback
  const stockInfo = await inventoryBreaker.fire(req.params.id);
  res.json(stockInfo);
});

app.listen(3000, () => console.log('Express app with circuit breaker on 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Not setting a timeout alongside the circuit breaker, letting slow (not just failing) calls hang
✅ Correct: Always combine a per-call timeout with the circuit breaker — a hanging call should count as a failure too

```javascript
// Wrong — breaker only catches thrown errors, not calls that hang forever
const breaker = new CircuitBreaker(callApi);   // no timeout configured

// Right
const breaker = new CircuitBreaker(callApi, { timeout: 2000 });   // hangs count as failures
```

❌ Mistake 2: No fallback — letting the caller receive a raw "circuit open" error with no graceful degradation
✅ Correct: Always define a sensible fallback (cached data, default value, queued-for-retry message)

```javascript
// Wrong
const result = await breaker.fire(data);   // throws an unhandled, unhelpful error when circuit is open

// Right
breaker.fallback(() => ({ status: 'degraded', message: 'Service temporarily unavailable' }));
```

---

## 🧠 Tricky Interview Question

```javascript
// Circuit breaker is OPEN due to repeated failures of Service B.
// A burst of 1000 requests hits Service A, which calls the breaker-wrapped Service B.
// How many of those 1000 requests actually reach Service B's network?
```
Answer: Essentially ZERO (until the cooldown/resetTimeout expires and the breaker transitions to HALF-OPEN, which allows only a small number of test calls through). While OPEN, the breaker fails fast for ALL 1000 requests without making any real network call to Service B at all — this is precisely the point: it protects both Service A (no resource exhaustion waiting on B) and Service B (no additional load while it's trying to recover) by short-circuiting calls entirely rather than letting them all attempt and individually time out.

---

## ⚫ Interview Questions + Answers

Q1: What are the three states of a circuit breaker, and what triggers transitions between them?
A1: CLOSED (normal operation, calls pass through, failures are counted) → transitions to OPEN when failures exceed a configured threshold within a rolling window. OPEN (calls fail immediately without attempting the real call) → after a cooldown/resetTimeout period elapses, transitions to HALF-OPEN. HALF-OPEN (a limited number of test calls are allowed through to check recovery) → transitions back to CLOSED if test calls succeed, or back to OPEN if they fail (often with a longer cooldown next time).

Q2: How does a circuit breaker prevent cascading failures in a microservices system?
A2: Without a breaker, a failing downstream service causes callers to pile up waiting requests (each hanging until timeout), consuming the caller's own resources (connections, memory, event loop capacity) — this can make the CALLER also become slow/unresponsive, and if that caller is itself called by others, the failure cascades upward through the whole system. By failing fast once a dependency is known to be unhealthy, the breaker stops resource exhaustion at the first hop, containing the failure instead of letting it propagate.

Q3: Why must a circuit breaker always be paired with a reasonable timeout on the underlying call?
A3: The breaker counts failures to decide when to trip open — but a call that hangs indefinitely (no timeout) never "fails," so the breaker never sees it as a failure and never opens, defeating its purpose. A timeout ensures slow calls are treated as failures within a bounded time, both protecting the caller from waiting too long and feeding accurate failure signals into the breaker's threshold logic.

Q4: What is a good fallback strategy when a circuit breaker is open, and why does it matter?
A4: A good fallback returns a degraded-but-useful response instead of a raw error: cached/stale data, a default value, a "feature temporarily unavailable" message, or queuing the request for later retry (e.g., via a message queue). This matters because it lets the overall user experience degrade gracefully rather than failing completely — e.g., showing "estimated delivery time unavailable" instead of crashing the whole order page because one estimation microservice is down.

Q5: How would you tune the failure threshold and reset timeout of a circuit breaker for a specific dependency?
A5: Base it on the dependency's actual reliability characteristics and the cost of being wrong in either direction: a LOW failure threshold (trips quickly) is good for a dependency where even small degradation signals real trouble, but risks false positives from transient blips; a longer resetTimeout avoids repeatedly hammering a struggling service with test calls, but delays recovery detection. In practice, you tune these using real traffic data/metrics (error rates, latency percentiles) for that specific dependency, often iterating after observing production behavior, rather than guessing fixed numbers upfront.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Calling external dependencies (third-party APIs, other microservices) that can become slow or unavailable
- You want to protect the caller's own resources from being exhausted by a failing dependency
- Graceful degradation (fallback) is possible and meaningfully better than a hard failure

❌ Avoid when:
- The dependency is extremely reliable and local (e.g., an in-memory cache) — overhead isn't justified
- There's no sensible fallback behavior and failing immediately provides no benefit over waiting (rare, but possible for strictly synchronous critical operations with no degraded mode)

---

## 📊 Visual Diagram
```
        failures exceed threshold
   CLOSED ─────────────────────────▶ OPEN
     ▲                                 │
     │                          cooldown elapsed
     │ test call succeeds              ▼
     └──────────────────────────  HALF-OPEN
                                       │
                              test call fails
                                       ▼
                                     OPEN (longer cooldown)

CLOSED: calls pass through normally
OPEN: calls fail FAST, no real attempt made
HALF-OPEN: a few test calls allowed to check recovery
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Circuit breaker | Pattern that fails fast on a known-bad dependency | Known-bad dependency पर fail fast करने वाला pattern |
| CLOSED state | Normal operation, calls pass through | Normal operation, calls pass through होती हैं |
| OPEN state | Calls fail immediately, no attempt made | Calls immediately fail, कोई attempt नहीं |
| HALF-OPEN state | Test calls allowed to check recovery | Recovery check करने के लिए test calls allowed |
| Fallback | Degraded response used when circuit is open | Circuit open होने पर use होने वाला degraded response |
| Cascading failure | One service's failure spreading to others | एक service की failure दूसरों तक फैलना |

---

## ⚡ 3-Line Summary
**English:**
1. A circuit breaker fails fast on calls to a known-unhealthy dependency, preventing resource exhaustion and cascading failures.
2. It moves between CLOSED, OPEN, and HALF-OPEN states based on failure rates and cooldown periods.
3. Always pair it with a timeout and a sensible fallback for graceful degradation.

**Hindi:**
1. Circuit breaker known-unhealthy dependency की calls पर fail fast करता है, resource exhaustion और cascading failures रोकता है।
2. यह failure rates और cooldown periods के आधार पर CLOSED, OPEN, और HALF-OPEN states के बीच move करता है।
3. इसे हमेशा एक timeout और sensible fallback के साथ pair करो graceful degradation के लिए।

---

## ➡️ Next Topic
**244. Health Check Endpoints** — Exposing service health status so load balancers and orchestrators can make routing decisions.
