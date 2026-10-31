---

# Q186. Build Rate Limiter
# Category: Real World Problems
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Build a `RateLimiter(limit, windowMs)` that allows at most `limit` requests per user in any sliding `windowMs` window. `allow(userId)` returns `true`/`false`.

```javascript
const limiter = new RateLimiter(3, 1000);
limiter.allow('u1'); // true (max 3 per second)
```

---

## 💡 Quick Concept (2 lines only)
Keep a list of request timestamps per user, drop those older than the window, allow only if count < limit.
हिंदी: हर user के request timestamps रखो; window से पुराने हटाओ और limit देखकर allow/deny करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

class RateLimiter {
  constructor(limit, windowMs, now = () => Date.now()) {
    this.limit = limit;                          // Step 1: max requests per window
    this.windowMs = windowMs;                    // window size
    this.now = now;                              // injectable clock
    this.hits = new Map();                       // userId -> [timestamps]
  }

  allow(userId) {
    const t = this.now();                        // Step 2: current time
    const list = (this.hits.get(userId) || [])   // existing timestamps
      .filter((ts) => t - ts < this.windowMs);   // Step 3: keep only inside window
    if (list.length >= this.limit) {             // Step 4: over limit?
      this.hits.set(userId, list);               // save cleaned list
      return false;                              // reject
    }
    list.push(t);                                // Step 5: record this request
    this.hits.set(userId, list);                 // save
    return true;                                 // accept
  }
}

// ============================================
// TEST CASES
// ============================================

let time = 0;                                    // fake clock
const limiter = new RateLimiter(3, 1000, () => time);

console.log(limiter.allow('u1'), limiter.allow('u1'), limiter.allow('u1')); // Expected: true true true
console.log(limiter.allow('u1'));                // Expected: false (4th in window)
console.log(limiter.allow('u2'));                // Expected: true (other user unaffected)
time = 1001;                                     // window slides past old hits
console.log(limiter.allow('u1'));                // Expected: true
```

---

## 🔍 Why This Works (3 lines max)
Filtering timestamps makes the window slide smoothly instead of resetting at fixed boundaries. Each user has an independent list, so one noisy user does not block others.
हिंदी: Sliding window में पुराने timestamps हटते रहते हैं, इसलिए limit सही तरह से लागू होती है।

---

## ⚡ Alternative Solution
```javascript
// Token bucket: refills continuously, allows small bursts, O(1) memory per user
class TokenBucket {
  constructor(capacity, refillPerSec, now = () => Date.now()) {
    Object.assign(this, { capacity, refillPerSec, now, tokens: capacity, last: now() });
  }
  allow() {
    const t = this.now();                        // current time
    this.tokens = Math.min(this.capacity, this.tokens + ((t - this.last) / 1000) * this.refillPerSec); // refill
    this.last = t;                               // update time
    if (this.tokens < 1) return false;           // no token left
    this.tokens -= 1;                            // spend one
    return true;
  }
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: fixed window counter reset -> 2x burst possible at the boundary
if (t - windowStart > windowMs) { count = 0; windowStart = t; }

// ✅ Correct: sliding window log (or token bucket) smooths boundaries
```

---

## 🎯 Interview Tip (1 line)
Compare fixed window, sliding window, and token bucket, and mention Redis for distributed limiting.

---

## 🔗 Related Questions
→ Q082 (throttle) | Q184 (request queue) | Q185 (cache with TTL) | Q309 (throttle real use case)
