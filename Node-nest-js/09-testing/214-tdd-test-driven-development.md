# 214. TDD — Test Driven Development
# हिंदी में: TDD — पहले Test लिखो, फिर Code

---

## 🔵 Simple Definition (English)
**TDD (Test-Driven Development)** is a workflow where you write a failing test FIRST, then write the minimum code to make it pass, then refactor — repeating this **Red → Green → Refactor** cycle for every small piece of functionality. The test defines the requirement before any implementation exists.

## 🔵 सरल परिभाषा (Hindi)
**TDD (Test-Driven Development)** एक workflow है जिसमें पहले एक failing test लिखी जाती है, फिर उसे pass करने के लिए minimum code लिखा जाता है, फिर refactor किया जाता है — इस **Red → Green → Refactor** cycle को हर छोटे feature के लिए repeat किया जाता है। Test, implementation से पहले requirement define करती है।

---

## 🔴 Problem it Solves
Writing code first and tests later often means the tests get skipped under deadline pressure, or they're written to match whatever the code already does (missing real requirement validation). TDD forces you to think about the exact expected behavior and edge cases BEFORE writing implementation — this clarifies requirements upfront, naturally produces testable (decoupled) code, and guarantees test coverage exists for every piece of logic since no code is written without a driving test.

## 🔴 यह क्यों बना? (Hindi)
Code पहले लिखना और tests बाद में लिखना अक्सर मतलब होता है कि deadline pressure में tests skip हो जाते हैं, या वो सिर्फ वही verify करते हैं जो code already कर रहा है (real requirement validation miss हो जाती है)। TDD force करता है कि implementation लिखने से पहले exact expected behavior और edge cases के बारे में सोचा जाए — ये requirements को शुरू में ही clear करता है, naturally testable (decoupled) code बनाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → **RED**: Write a test for a small piece of functionality that doesn't exist yet. Run it — it fails (because the code doesn't exist)
Step 2 → **GREEN**: Write the simplest possible code to make that test pass — no more, no less
Step 3 → **REFACTOR**: Clean up the code (remove duplication, improve naming) while keeping the test green
Step 4 → Repeat: write the next failing test for the next small piece of behavior
Step 5 → Over many small cycles, the full feature emerges, fully covered by tests that were written as specifications

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **RED**: एक छोटे feature के लिए test लिखो जो अभी exist नहीं करता। चलाओ — fail होगा (क्योंकि code है ही नहीं)
Step 2 → **GREEN**: उस test को pass करने के लिए सबसे simple code लिखो — ज़्यादा नहीं, कम नहीं
Step 3 → **REFACTOR**: code को clean करो (duplication हटाओ, naming सुधारो) test को green रखते हुए
Step 4 → Repeat करो: अगले छोटे behavior के लिए next failing test लिखो
Step 5 → कई छोटे cycles के बाद, पूरा feature बन जाता है, tests से पूरी तरह covered जो specification की तरह पहले ही लिखी गई थीं

---

## 🟡 Real World Example
**Building a Zomato coupon-validation engine with TDD:** The developer first writes a test `test('rejects expired coupon', ...)` — it fails since `validateCoupon()` doesn't exist. They write the minimal code to pass it. Next test: `test('rejects coupon below minimum order value', ...)` — fails, write code to pass. Next: `test('applies percentage discount correctly', ...)`. After ~10 such cycles, the full coupon engine exists, driven entirely by test cases that double as a spec document — any future developer can read the tests to understand every business rule without reading the implementation.

## 🟡 Real Example Hindi mein
**TDD से Zomato coupon-validation engine बनाना:** Developer पहले test लिखता है `test('rejects expired coupon', ...)` — fail होता है क्योंकि `validateCoupon()` exist नहीं करता। Minimal code लिखते हैं pass करने के लिए। Next test: `test('rejects coupon below minimum order value', ...)` — fail, code लिखो pass करने के लिए। ऐसे ~10 cycles के बाद पूरा coupon engine बन जाता है, test cases driven — जो एक spec document की तरह काम करते हैं।

---

## 💻 Code Example — Basic

```javascript
// Step-by-step TDD walkthrough for a `calculateCoupon` function
// coupon.test.js — written FIRST, before coupon.js even exists

const { validateAndApplyCoupon } = require('./coupon');

describe('validateAndApplyCoupon (TDD)', () => {
  // CYCLE 1 — RED: this test fails because coupon.js doesn't exist yet
  test('rejects expired coupon', () => {
    const coupon = { code: 'SAVE10', expiryDate: '2020-01-01', discountPercent: 10 };
    expect(() => validateAndApplyCoupon(coupon, 500, new Date('2024-01-01')))
      .toThrow('Coupon expired');
  });

  // CYCLE 2 — RED: next small requirement
  test('rejects coupon if order below minimum value', () => {
    const coupon = { code: 'SAVE10', expiryDate: '2099-01-01', discountPercent: 10, minOrder: 300 };
    expect(() => validateAndApplyCoupon(coupon, 200, new Date('2024-01-01')))
      .toThrow('Order value below minimum');
  });

  // CYCLE 3 — RED: happy path
  test('applies percentage discount when valid', () => {
    const coupon = { code: 'SAVE10', expiryDate: '2099-01-01', discountPercent: 10, minOrder: 300 };
    const finalAmount = validateAndApplyCoupon(coupon, 500, new Date('2024-01-01'));
    expect(finalAmount).toBe(450); // 500 - 10% = 450
  });
});
```

```javascript
// coupon.js — written AFTER each test, with the MINIMUM code to pass it
// (this is the GREEN step, after each RED test above was written one at a time)

function validateAndApplyCoupon(coupon, orderAmount, now) {
  // Written to pass Cycle 1's test
  if (new Date(coupon.expiryDate) < now) {
    throw new Error('Coupon expired');
  }
  // Written to pass Cycle 2's test
  if (coupon.minOrder && orderAmount < coupon.minOrder) {
    throw new Error('Order value below minimum');
  }
  // Written to pass Cycle 3's test
  const discount = (orderAmount * coupon.discountPercent) / 100;
  return orderAmount - discount;
}

module.exports = { validateAndApplyCoupon };
// REFACTOR step: code is already simple here — in a real cycle you'd now
// clean up duplication, extract constants, improve names, re-run tests to confirm still green
```

## 💻 Code Example — Advanced

```javascript
// TDD for a slightly more complex feature: a rate limiter (common interview task)
// rateLimiter.test.js — tests written incrementally, driving the design

const { RateLimiter } = require('./rateLimiter');

describe('RateLimiter (TDD)', () => {
  // CYCLE 1: basic allow
  test('allows request when under limit', () => {
    const limiter = new RateLimiter(3, 1000); // max 3 requests per 1000ms
    expect(limiter.allow('user1')).toBe(true);
  });

  // CYCLE 2: blocking over limit
  test('blocks request when limit exceeded', () => {
    const limiter = new RateLimiter(2, 1000);
    limiter.allow('user1');
    limiter.allow('user1');
    expect(limiter.allow('user1')).toBe(false); // 3rd request within window
  });

  // CYCLE 3: per-user isolation
  test('tracks limits independently per user', () => {
    const limiter = new RateLimiter(1, 1000);
    limiter.allow('user1');
    expect(limiter.allow('user2')).toBe(true); // different user, not blocked
  });

  // CYCLE 4: window expiry (requires fake timers — drives a design decision)
  test('resets after the time window passes', () => {
    jest.useFakeTimers();
    const limiter = new RateLimiter(1, 1000);
    limiter.allow('user1');
    expect(limiter.allow('user1')).toBe(false); // blocked within window

    jest.advanceTimersByTime(1100); // simulate time passing beyond the window
    expect(limiter.allow('user1')).toBe(true); // allowed again after reset
    jest.useRealTimers();
  });
});
```

```javascript
// rateLimiter.js — implementation written incrementally to pass each cycle above
class RateLimiter {
  constructor(maxRequests, windowMs) {
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;
    this.requestLog = new Map(); // userId -> array of timestamps
  }

  allow(userId) {
    const now = Date.now();
    const timestamps = this.requestLog.get(userId) || [];

    // Drop timestamps outside the current window (sliding window algorithm)
    const recent = timestamps.filter(ts => now - ts < this.windowMs);

    if (recent.length >= this.maxRequests) {
      return false; // over limit — block
    }

    recent.push(now);
    this.requestLog.set(userId, recent);
    return true;
  }
}

module.exports = { RateLimiter };
```

---

## 🟠 Express.js Integration

```javascript
// Using the TDD-built RateLimiter inside Express middleware
const { RateLimiter } = require('./rateLimiter');
const limiter = new RateLimiter(100, 60 * 1000); // 100 requests/min per user

function rateLimitMiddleware(req, res, next) {
  const userId = req.user?.id || req.ip;
  if (!limiter.allow(userId)) {
    return res.status(429).json({ error: 'Too many requests, slow down' });
  }
  next();
}

app.use('/api/', rateLimitMiddleware);

// middleware.test.js — testing the middleware using the same TDD mindset:
// write the test for the behavior, then wire the middleware to satisfy it
test('returns 429 when rate limit exceeded', async () => {
  const app = express();
  app.use(rateLimitMiddleware);
  app.get('/ping', (req, res) => res.send('pong'));

  for (let i = 0; i < 100; i++) await request(app).get('/ping');
  const res = await request(app).get('/ping'); // 101st request
  expect(res.status).toBe(429);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Writing multiple tests before any implementation, then trying to pass them all at once
```javascript
// WRONG: writing 10 tests upfront then one big implementation defeats TDD's
// small-step feedback loop — you lose the "minimal code to pass ONE test" discipline

// CORRECT: one test → minimal code → green → refactor → NEXT test. One at a time.
```

❌ Mistake 2: Skipping the REFACTOR step, leaving messy code because "tests pass"
```javascript
// WRONG: tests are green but code has duplicated logic, magic numbers, bad names
function calc(a, b, t) {
  if (t === 1) return a + b * 0.1;
  if (t === 2) return a + b * 0.18;
}

// CORRECT: refactor while green — tests protect you during cleanup
const TAX_RATES = { STANDARD: 0.1, LUXURY: 0.18 };
function calculateTotal(amount, taxableBase, taxType) {
  return amount + taxableBase * TAX_RATES[taxType];
}
```

---

## 🧠 Tricky Interview Question

**Q: In TDD, is it acceptable to write a test that already passes without any new code (i.e., skip the RED step)?**
Answer: **No — if a test passes immediately without writing new code, something is wrong.** Either the test isn't actually testing new behavior (it's redundant with existing passing tests), or it has a bug that makes it trivially pass (e.g., `expect(true).toBe(true)`, or asserting something unrelated to the actual logic). The RED step is a sanity check that the test is correctly wired to fail in the absence of the feature — skipping it risks tests that give false confidence (they'd "pass" even if the feature were deleted).

---

## ⚫ Interview Questions + Answers

Q1: What are the three steps of the TDD cycle?
A1: **Red** (write a failing test for new behavior), **Green** (write the minimum code to make it pass), **Refactor** (clean up code/tests while keeping tests green). Repeat for each small increment of functionality.

Q2: What's the difference between TDD and just writing tests after the code (test-after)?
A2: TDD writes the test BEFORE the implementation, so the test defines the requirement and drives the design (forcing testable, decoupled code). Test-after writes tests for code that already exists, which risks tests that just confirm existing behavior (including bugs) rather than validating intended requirements, and is often skipped under time pressure.

Q3: Does TDD guarantee bug-free code?
A3: No. TDD guarantees that every piece of implemented behavior was driven by an explicit test, improving design and coverage — but it doesn't catch bugs in requirements you didn't think to test, or integration issues between well-tested units. It's a design discipline, not a correctness guarantee.

Q4: What is the "minimum code to pass" principle, and why does it matter?
A4: In the Green step, you write ONLY enough code to make the current failing test pass — not extra features you anticipate needing later. This avoids over-engineering and speculative code that no test demands, keeping the codebase lean and ensuring every line of code is justified by an actual test/requirement.

Q5: How does TDD influence software design even before considering correctness?
A5: Writing the test first forces you to think about the function's interface (what are its inputs/outputs, what does calling it look like) from the CALLER's perspective before worrying about internal implementation. This naturally produces decoupled, testable code — functions with clear single responsibilities and minimal hidden dependencies, since hard-to-test designs become obvious friction immediately during the Red step.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building well-defined business logic with clear expected behaviors (pricing, validation, rate limiting)
- Working on critical code where correctness and regression safety matter a lot
- You want tests that double as living documentation of requirements

❌ Avoid when:
- Exploring/prototyping unclear requirements where the design will change rapidly (write a spike first, then TDD the real implementation)
- Working with highly visual/UI-exploratory work where expected behavior is hard to define upfront in test form

---

## 📊 Visual Diagram
```
TDD CYCLE:
─────────────────────────────────────────
     ┌─────────────┐
     │  1. RED      │  Write a failing test
     │  (test fails)│  for new behavior
     └──────┬───────┘
            │
            ▼
     ┌─────────────┐
     │  2. GREEN    │  Write minimum code
     │ (test passes)│  to pass the test
     └──────┬───────┘
            │
            ▼
     ┌─────────────┐
     │ 3. REFACTOR  │  Clean up code,
     │ (still green)│  remove duplication
     └──────┬───────┘
            │
            └──────► back to step 1 for next small behavior
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TDD | Write tests before implementation | Implementation से पहले tests लिखना |
| Red | Failing test state | Test fail होने की state |
| Green | Passing test state | Test pass होने की state |
| Refactor | Clean up code while tests stay green | Tests green रखते हुए code साफ करना |
| Minimum code | Just enough code to pass current test | Current test pass करने के लिए न्यूनतम code |
| Spec-by-test | Tests act as requirement documentation | Tests ही requirement document हैं |

---

## ⚡ 3-Line Summary
English:
1. TDD follows Red → Green → Refactor: write a failing test, write minimal code to pass it, then clean up — repeated in small increments.
2. Tests double as living specifications of requirements, since every behavior exists because a test demanded it.
3. TDD improves design (testable, decoupled code) but doesn't guarantee bug-free software — it's a discipline, not a correctness proof.

Hindi:
1. TDD, Red → Green → Refactor follow करता है: पहले failing test लिखो, फिर उसे pass करने के लिए minimal code लिखो, फिर clean करो — छोटे increments में repeat करते हुए।
2. Tests requirements की living specification की तरह काम करते हैं, क्योंकि हर behavior एक test की वजह से exist करता है।
3. TDD design सुधारता है (testable, decoupled code) पर bug-free software guarantee नहीं करता — ये एक discipline है, correctness का proof नहीं।

---

## ➡️ Next Topic
**215. E2E Testing Basics** — पूरे application flow को user की तरह शुरू से आखिर तक test करना (browser automation के साथ)।
