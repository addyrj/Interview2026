# 212. Mocking in Tests
# हिंदी में: Mocking — Tests में Fake Dependencies Use करना

---

## 🔵 Simple Definition (English)
**Mocking** means replacing a real dependency (a database call, a payment gateway, an email service, `Date.now()`) with a fake, controllable stand-in during tests. Jest provides `jest.fn()` (mock functions), `jest.mock()` (mock entire modules), and `jest.spyOn()` (wrap/override existing methods) to make dependencies predictable, fast, and free of real side effects.

## 🔵 सरल परिभाषा (Hindi)
**Mocking** का मतलब है किसी real dependency (database call, payment gateway, email service, `Date.now()`) को एक fake, controllable version से replace करना। Jest में `jest.fn()` (mock functions), `jest.mock()` (पूरा module mock करना), और `jest.spyOn()` (existing methods को wrap/override करना) मिलता है — ताकि dependencies predictable, fast, और real side-effects-free बनें।

---

## 🔴 Problem it Solves
Testing code that calls a real payment gateway means: real money could be charged, tests fail when the network is down, tests are slow (network round-trip), and tests aren't repeatable (gateway might return different responses). Mocking removes all these problems — you control exactly what the "payment gateway" returns in each test (success, failure, timeout) without ever making a real network call, making tests fast, deterministic, and safe to run thousands of times in CI.

## 🔴 यह क्यों बना? (Hindi)
Real payment gateway को call करने वाला code test करने में problem है: real पैसे कट सकते हैं, network down होने पर test fail होगा, tests slow होंगे (network round-trip), और tests repeatable नहीं रहेंगे (gateway अलग-अलग response दे सकता है)। Mocking ये सब problems हटा देता है — तुम control करते हो कि "payment gateway" हर test में क्या return करे (success, failure, timeout) बिना कोई real network call किए — tests fast, deterministic, और CI में हजारों बार चलाने के लिए safe बन जाते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Identify the external dependency you want to isolate (DB, HTTP client, 3rd-party SDK, `Date.now`)
Step 2 → Create a mock: `jest.fn()` for a single function, `jest.mock('./module')` to auto-mock an entire module
Step 3 → Configure the mock's return behavior: `.mockReturnValue()`, `.mockResolvedValue()`, `.mockRejectedValue()`, or `.mockImplementation()`
Step 4 → Call the code under test — it calls the mock instead of the real dependency
Step 5 → Assert the mock was called correctly: `.toHaveBeenCalledWith()`, `.toHaveBeenCalledTimes()`
Step 6 → Reset mocks between tests with `jest.clearAllMocks()` / `jest.resetAllMocks()` in `afterEach` to avoid leakage

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → वो external dependency पहचानो जिसे isolate करना है (DB, HTTP client, 3rd-party SDK, `Date.now`)
Step 2 → Mock बनाओ: एक function के लिए `jest.fn()`, पूरे module को auto-mock करने के लिए `jest.mock('./module')`
Step 3 → Mock का return behavior configure करो: `.mockReturnValue()`, `.mockResolvedValue()`, `.mockRejectedValue()`, या `.mockImplementation()`
Step 4 → Test code को call करो — ये real dependency की जगह mock को call करेगा
Step 5 → Verify करो कि mock सही तरह call हुआ: `.toHaveBeenCalledWith()`, `.toHaveBeenCalledTimes()`
Step 6 → Mock leakage से बचने के लिए `afterEach` में `jest.clearAllMocks()` / `jest.resetAllMocks()` चलाओ

---

## 🟡 Real World Example
**Razorpay integration at a Zomato-like checkout service**: the `createPaymentOrder()` function calls Razorpay's SDK over the network. In tests, the team uses `jest.mock('razorpay')` to replace the entire SDK with a fake version — they simulate success, insufficient-funds failure, and gateway timeout scenarios, verifying their own retry logic and error messages work correctly in each case, all without hitting Razorpay's real servers or needing test API keys and network access in CI.

## 🟡 Real Example Hindi mein
**Zomato जैसी checkout service में Razorpay integration**: `createPaymentOrder()` function network पर Razorpay के SDK को call करता है। Tests में team `jest.mock('razorpay')` से पूरे SDK को fake version से replace करती है — वो success, insufficient-funds failure, और gateway timeout scenarios simulate करते हैं, verify करते हैं कि अपनी retry logic और error messages हर case में सही काम करते हैं — बिना Razorpay के real servers को hit किए।

---

## 💻 Code Example — Basic

```javascript
// mathUtils.js — module we'll partially mock
function add(a, b) { return a + b; }
function getRandomDiscount() { return Math.floor(Math.random() * 50); }
module.exports = { add, getRandomDiscount };
```

```javascript
// basic-mocks.test.js — jest.fn(), mockReturnValue, spyOn basics
const mathUtils = require('./mathUtils');

describe('jest.fn() basics', () => {
  test('creates a mock function and tracks calls', () => {
    const mockCallback = jest.fn(); // bare mock, returns undefined by default
    [1, 2, 3].forEach(mockCallback);

    expect(mockCallback).toHaveBeenCalledTimes(3);
    expect(mockCallback).toHaveBeenCalledWith(3, 2, [1, 2, 3]); // last call args
  });

  test('mockReturnValue controls what the mock returns', () => {
    const mockFn = jest.fn().mockReturnValue(42);
    expect(mockFn()).toBe(42);
    expect(mockFn()).toBe(42); // same value every call
  });

  test('mockResolvedValue for async/Promise-based mocks', async () => {
    const mockFetchUser = jest.fn().mockResolvedValue({ id: 1, name: 'Amit' });
    const user = await mockFetchUser();
    expect(user.name).toBe('Amit');
  });

  test('jest.spyOn wraps a real method and can restore it afterward', () => {
    // spyOn replaces getRandomDiscount but we can still assert it was called
    const spy = jest.spyOn(mathUtils, 'getRandomDiscount').mockReturnValue(25);

    expect(mathUtils.getRandomDiscount()).toBe(25); // mocked value, not real random
    expect(spy).toHaveBeenCalledTimes(1);

    spy.mockRestore(); // restores the ORIGINAL implementation
    expect(typeof mathUtils.getRandomDiscount()).toBe('number'); // real random again
  });
});
```

## 💻 Code Example — Advanced

```javascript
// paymentService.js — service that depends on an external SDK
const Razorpay = require('razorpay'); // real 3rd-party SDK

async function createPaymentOrder(amount, currency = 'INR') {
  const instance = new Razorpay({ key_id: process.env.RZP_KEY, key_secret: process.env.RZP_SECRET });
  try {
    const order = await instance.orders.create({ amount: amount * 100, currency });
    return { success: true, orderId: order.id };
  } catch (err) {
    return { success: false, error: err.message };
  }
}

module.exports = { createPaymentOrder };
```

```javascript
// paymentService.test.js — jest.mock() auto-mocks the ENTIRE 'razorpay' module
jest.mock('razorpay'); // every `new Razorpay()` returns an auto-mocked instance
const Razorpay = require('razorpay');
const { createPaymentOrder } = require('./paymentService');

describe('createPaymentOrder', () => {
  // Clear mock history before each test — prevents leakage between tests
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('returns success when Razorpay order creation succeeds', async () => {
    // Configure the mocked constructor's instance method
    Razorpay.mockImplementation(() => ({
      orders: { create: jest.fn().mockResolvedValue({ id: 'order_abc123' }) },
    }));

    const result = await createPaymentOrder(500);

    expect(result.success).toBe(true);
    expect(result.orderId).toBe('order_abc123');
  });

  test('returns failure when Razorpay throws (e.g. insufficient funds)', async () => {
    Razorpay.mockImplementation(() => ({
      orders: {
        create: jest.fn().mockRejectedValue(new Error('Insufficient funds')),
      },
    }));

    const result = await createPaymentOrder(500);

    expect(result.success).toBe(false);
    expect(result.error).toBe('Insufficient funds');
  });
});

// ─── MOCKING Date.now() / timers ──────────────────────────────────────────────
function isExpired(expiryTimestamp) {
  return Date.now() > expiryTimestamp;
}

test('isExpired works correctly with mocked time', () => {
  // Freeze time to a known value for deterministic testing
  jest.useFakeTimers().setSystemTime(new Date('2024-06-01T00:00:00Z'));

  const futureExpiry = new Date('2024-06-02T00:00:00Z').getTime();
  const pastExpiry = new Date('2024-05-30T00:00:00Z').getTime();

  expect(isExpired(futureExpiry)).toBe(false);
  expect(isExpired(pastExpiry)).toBe(true);

  jest.useRealTimers(); // restore real clock for other tests
});
```

---

## 🟠 Express.js Integration

```javascript
// orderRoutes.js — route that depends on an injected payment service
const express = require('express');

function createOrderRoutes(paymentService) {
  const router = express.Router();

  router.post('/orders', async (req, res) => {
    const result = await paymentService.createPaymentOrder(req.body.amount);
    if (!result.success) {
      return res.status(402).json({ error: result.error }); // 402 Payment Required
    }
    res.status(201).json({ orderId: result.orderId });
  });

  return router;
}

module.exports = { createOrderRoutes };

// orderRoutes.test.js — Supertest + a mocked paymentService (dependency injection)
const express = require('express');
const request = require('supertest');
const { createOrderRoutes } = require('./orderRoutes');

test('POST /orders returns 402 when payment fails', async () => {
  // Mock the whole paymentService object passed in via dependency injection
  const mockPaymentService = {
    createPaymentOrder: jest.fn().mockResolvedValue({ success: false, error: 'Card declined' }),
  };

  const app = express();
  app.use(express.json());
  app.use(createOrderRoutes(mockPaymentService));

  const res = await request(app).post('/orders').send({ amount: 500 });

  expect(res.status).toBe(402);
  expect(res.body.error).toBe('Card declined');
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to reset mocks between tests, causing state leakage
```javascript
// WRONG: mock call history carries over to the next test
test('a', () => { mockFn('x'); expect(mockFn).toHaveBeenCalledTimes(1); });
test('b', () => { mockFn('y'); expect(mockFn).toHaveBeenCalledTimes(1); }); // FAILS — actually 2

// CORRECT: reset in afterEach (or use Jest config "clearMocks": true)
afterEach(() => jest.clearAllMocks());
```

❌ Mistake 2: Over-mocking — mocking so much that the test verifies nothing real
```javascript
// WRONG: mocking the function under test itself defeats the purpose
jest.mock('./orderService', () => ({
  placeOrder: jest.fn().mockResolvedValue({ status: 'confirmed' }),
}));
// Test "passes" but tests NOTHING about actual placeOrder logic!

// CORRECT: mock only the EXTERNAL dependencies (DB, payment gateway),
// keep the function under test real so its actual logic is exercised
```

---

## 🧠 Tricky Interview Question

```javascript
const mockFn = jest.fn().mockReturnValueOnce('first').mockReturnValueOnce('second');
console.log(mockFn()); // ❓
console.log(mockFn()); // ❓
console.log(mockFn()); // ❓
```
Answer: Prints `"first"`, then `"second"`, then `undefined`. `mockReturnValueOnce()` queues up one-time return values consumed in order on successive calls; once the queue is exhausted, the mock falls back to its default `mockReturnValue()` (if set) or `undefined`. This is extremely useful for testing retry logic — e.g., mock the first two calls to fail and the third to succeed, verifying a retry mechanism works correctly.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `jest.fn()`, `jest.spyOn()`, and `jest.mock()`?
A1: `jest.fn()` creates a brand-new standalone mock function. `jest.spyOn(obj, 'method')` wraps an EXISTING method on an object, letting you track calls and optionally override behavior while still being able to `.mockRestore()` the original. `jest.mock('./module')` auto-mocks an entire module at the import level, replacing all its exports with mock functions.

Q2: What's the difference between `mockReturnValue` and `mockResolvedValue`?
A2: `mockReturnValue(x)` makes the mock return `x` synchronously. `mockResolvedValue(x)` makes the mock return a Promise that resolves to `x` — shorthand for `mockReturnValue(Promise.resolve(x))`. Use `mockResolvedValue`/`mockRejectedValue` for mocking async functions.

Q3: Why should you avoid mocking the function/module you're actually testing?
A3: If you mock the exact unit under test, the test only verifies that the mock was called — it exercises zero real logic. The point of mocking is to isolate the unit under test by faking its EXTERNAL dependencies (DB, network, time), not to fake the unit itself.

Q4: How do you mock a class instance method with Jest?
A4: Either `jest.mock('./ClassModule')` and configure `MockedClass.mockImplementation(() => ({ method: jest.fn() }))`, or use `jest.spyOn(ClassModule.prototype, 'method').mockReturnValue(...)` to mock just one method while keeping the rest of the class real.

Q5: What is "test double" and how many kinds exist?
A5: "Test double" is the general term for any fake object used in tests, replacing a real dependency. Common kinds: **Mock** (records calls, allows assertions on interaction), **Stub** (returns canned responses, no call-assertion focus), **Spy** (wraps real implementation, records calls), **Fake** (a working lightweight implementation, e.g. in-memory DB), **Dummy** (placeholder object passed but never actually used).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The dependency is slow, unreliable, costly, or has real side effects (payment, email, SMS)
- You need to test error paths that are hard to trigger for real (network timeout, DB down)
- You want deterministic time/randomness in tests

❌ Avoid when:
- Mocking the exact code under test (defeats the purpose of testing)
- Over-mocking makes the test brittle to refactors without catching real bugs (consider integration test instead)

---

## 📊 Visual Diagram
```
MOCKING LAYERS:
────────────────────────────────────────────────
  [ Code Under Test ]  ← kept REAL, actually exercised
         │
         ├──> [ Database call ]       → MOCKED (jest.fn)
         ├──> [ Razorpay SDK call ]    → MOCKED (jest.mock)
         ├──> [ Date.now() ]           → MOCKED (jest.useFakeTimers)
         └──> [ Pure internal logic ]  → NOT mocked, tested for real

  jest.fn()        → standalone mock function
  jest.spyOn()     → wrap existing method, restorable
  jest.mock()      → auto-mock whole module at import time
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Mock | Fake replacement for a dependency | Dependency का fake version |
| jest.fn() | Standalone mock function | Standalone mock function |
| jest.spyOn() | Wraps existing method, restorable | Existing method wrap करना |
| jest.mock() | Auto-mocks entire module | पूरा module mock करना |
| mockResolvedValue | Mock returns resolved Promise | Resolved Promise return करना |
| mockReturnValueOnce | One-time queued return value | एक बार का return value |
| Test double | General term for any fake test object | कोई भी fake test object |
| clearAllMocks | Resets mock call history | Mock history reset करना |

---

## ⚡ 3-Line Summary
English:
1. Mocking replaces real dependencies (DB, payment gateway, time) with controllable fakes using `jest.fn()`, `jest.mock()`, and `jest.spyOn()`.
2. Only mock external dependencies — never mock the exact function/module under test, or the test verifies nothing real.
3. Always reset mocks between tests (`jest.clearAllMocks()` in `afterEach`) to prevent call-history leakage across test cases.

Hindi:
1. Mocking real dependencies (DB, payment gateway, time) को controllable fakes से replace करता है — `jest.fn()`, `jest.mock()`, `jest.spyOn()` से।
2. केवल external dependencies mock करो — जो function/module test हो रहा है उसे कभी mock न करो, वरना test कुछ भी real verify नहीं करता।
3. हर test के बीच mocks reset करो (`afterEach` में `jest.clearAllMocks()`) ताकi call-history एक test से दूसरे में leak न हो।

---

## ➡️ Next Topic
**213. Test Coverage** — code का कितना हिस्सा tests से actually execute होता है, इसे measure और improve करना।
