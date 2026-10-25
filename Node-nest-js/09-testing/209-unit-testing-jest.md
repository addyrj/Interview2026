# 209. Unit Testing (Jest)
# हिंदी में: Unit Testing — Jest से छोटे Functions को अलग-अलग Test करना

---

## 🔵 Simple Definition (English)
**Unit testing** means testing the smallest piece of code (a single function or module) in complete isolation — without a database, network, or other modules. **Jest** is the most popular JS testing framework: it gives you `test()`/`it()`, `expect()` assertions, mocking, and a built-in test runner + coverage reporter in one package.

## 🔵 सरल परिभाषा (Hindi)
**Unit testing** का मतलब है code के सबसे छोटे हिस्से (एक function या module) को अलग से test करना — database, network, या दूसरे modules के बिना। **Jest** सबसे popular JS testing framework है: इसमें `test()`/`it()`, `expect()` assertions, mocking, और built-in test runner + coverage report सब कुछ एक package में मिलता है।

---

## 🔴 Problem it Solves
Without automated tests, every code change needs manual testing via Postman/browser clicking — slow and error-prone. Bugs slip into production because a developer forgot to re-check an old feature after changing shared code. Unit tests catch this: run `npm test` and know in seconds if `calculateDiscount()` still returns the right value after a refactor. They also act as living documentation — reading a test tells you exactly what a function is supposed to do.

## 🔴 यह क्यों बना? (Hindi)
Automated tests के बिना, हर code change को manually Postman/browser से test करना पड़ता था — slow और error-prone। Developer किसी shared function को change करता है और भूल जाता है कि कोई पुराना feature टूट गया — bug production में चला जाता है। Unit tests इसे पकड़ लेते हैं: `npm test` चलाओ, seconds में पता चल जाता है कि refactor के बाद `calculateDiscount()` सही value दे रहा है या नहीं।

---

## 🟢 How it Works — Step by Step

Step 1 → Install Jest: `npm install --save-dev jest`
Step 2 → Write a `.test.js` file next to the source file (e.g. `discount.test.js` next to `discount.js`)
Step 3 → Use `describe()` to group related tests, `test()`/`it()` for individual cases
Step 4 → Use `expect(value).toBe(expected)` (and other matchers) to assert results
Step 5 → Run `npx jest` — Jest finds all `*.test.js` files and runs them, reporting pass/fail
Step 6 → Add `"test": "jest"` to `package.json` scripts so CI can run `npm test`

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Jest install करो: `npm install --save-dev jest`
Step 2 → Source file के बगल में `.test.js` file बनाओ (जैसे `discount.js` के साथ `discount.test.js`)
Step 3 → Related tests को group करने के लिए `describe()`, individual case के लिए `test()`/`it()` use करो
Step 4 → Result check करने के लिए `expect(value).toBe(expected)` जैसे matchers use करो
Step 5 → `npx jest` चलाओ — Jest सभी `*.test.js` files ढूंढ कर run करता है और pass/fail report देता है
Step 6 → `package.json` में `"test": "jest"` add करो ताकि CI `npm test` चला सके

---

## 🟡 Real World Example
**Swiggy's pricing team** has a `calculateDeliveryFee(distance, surge, isPrime)` function used across the checkout API, the admin dashboard, and the driver app pricing preview. Any small bug here means wrong charges to millions of orders. Instead of manually testing every combination, they write ~15 Jest unit tests covering edge cases (0 distance, surge = 2x, Prime member free delivery under 3km, negative distance should throw). Every PR runs these tests in CI; a broken pricing rule is caught before merge, not after customers complain.

## 🟡 Real Example Hindi mein
**Swiggy की pricing team** के पास एक `calculateDeliveryFee(distance, surge, isPrime)` function है जो checkout API, admin dashboard, और driver app में use होता है। यहाँ छोटी सी bug लाखों orders पर गलत charge लगा सकती है। हर combination manually test करने के बजाय, वो ~15 Jest unit tests लिखते हैं (0 distance, 2x surge, Prime member का 3km के अंदर free delivery, negative distance पर error)। हर PR पर CI में ये tests run होते हैं — गलत pricing rule merge से पहले ही पकड़ी जाती है।

---

## 💻 Code Example — Basic

```javascript
// discount.js — the function we want to test
// Calculates final price after applying a percentage discount
function calculateDiscount(price, discountPercent) {
  // Guard: price must be a positive number
  if (typeof price !== 'number' || price < 0) {
    throw new Error('Invalid price');
  }
  // Guard: discount must be between 0 and 100
  if (discountPercent < 0 || discountPercent > 100) {
    throw new Error('Invalid discount percent');
  }
  // Apply the discount formula
  const discountedPrice = price - (price * discountPercent) / 100;
  // Round to 2 decimal places (money should not have long decimals)
  return Math.round(discountedPrice * 100) / 100;
}

module.exports = { calculateDiscount };
```

```javascript
// discount.test.js — Jest unit tests for calculateDiscount
const { calculateDiscount } = require('./discount');

// describe() groups related tests together under one label
describe('calculateDiscount', () => {
  // Each test() is one independent test case
  test('applies 10% discount correctly', () => {
    // expect(actual).toBe(expected) — strict equality check
    expect(calculateDiscount(100, 10)).toBe(90);
  });

  test('returns same price when discount is 0', () => {
    expect(calculateDiscount(500, 0)).toBe(500);
  });

  test('returns 0 when discount is 100%', () => {
    expect(calculateDiscount(200, 100)).toBe(0);
  });

  test('throws error for negative price', () => {
    // toThrow() checks that calling the function throws
    expect(() => calculateDiscount(-50, 10)).toThrow('Invalid price');
  });

  test('throws error for discount above 100', () => {
    expect(() => calculateDiscount(100, 150)).toThrow('Invalid discount percent');
  });
});

// Run with: npx jest discount.test.js
```

## 💻 Code Example — Advanced

```javascript
// orderService.js — a service with a dependency (needs mocking in tests)
class OrderService {
  constructor(db, paymentGateway) {
    this.db = db;                      // injected dependency — easier to test
    this.paymentGateway = paymentGateway;
  }

  async placeOrder(userId, items, amount) {
    // Validate before touching external systems
    if (!items || items.length === 0) {
      throw new Error('Cart is empty');
    }

    // Call payment gateway (external dependency — we'll mock this in tests)
    const payment = await this.paymentGateway.charge(userId, amount);
    if (!payment.success) {
      throw new Error('Payment failed');
    }

    // Save order to DB (also mocked in unit tests — no real DB call)
    const order = await this.db.orders.create({
      userId, items, amount, paymentId: payment.id, status: 'confirmed',
    });

    return order;
  }
}

module.exports = { OrderService };
```

```javascript
// orderService.test.js — using Jest mocks for dependencies
const { OrderService } = require('./orderService');

describe('OrderService.placeOrder', () => {
  let mockDb, mockPaymentGateway, service;

  // beforeEach runs before every single test — fresh mocks each time
  beforeEach(() => {
    mockDb = {
      orders: {
        // jest.fn() creates a mock function we can control and inspect
        create: jest.fn().mockResolvedValue({ id: 'order_1', status: 'confirmed' }),
      },
    };
    mockPaymentGateway = {
      charge: jest.fn().mockResolvedValue({ success: true, id: 'pay_1' }),
    };
    service = new OrderService(mockDb, mockPaymentGateway);
  });

  test('places order successfully when payment succeeds', async () => {
    const order = await service.placeOrder('u1', [{ sku: 'ITEM1' }], 500);

    expect(order.status).toBe('confirmed');
    // toHaveBeenCalledWith verifies the mock was called with exact args
    expect(mockPaymentGateway.charge).toHaveBeenCalledWith('u1', 500);
    expect(mockDb.orders.create).toHaveBeenCalledTimes(1);
  });

  test('throws when cart is empty', async () => {
    await expect(service.placeOrder('u1', [], 500)).rejects.toThrow('Cart is empty');
    // Payment should NOT be called if validation fails early
    expect(mockPaymentGateway.charge).not.toHaveBeenCalled();
  });

  test('throws when payment fails', async () => {
    // Override the mock's resolved value just for this test
    mockPaymentGateway.charge.mockResolvedValue({ success: false });

    await expect(service.placeOrder('u1', [{ sku: 'X' }], 500))
      .rejects.toThrow('Payment failed');
    // DB create should never be called if payment failed
    expect(mockDb.orders.create).not.toHaveBeenCalled();
  });
});
```

---

## 🟠 Express.js Integration

```javascript
// controllers/orderController.js — keep business logic separate from Express
// so it can be unit tested WITHOUT starting a server
const { OrderService } = require('../services/orderService');

function createOrderController(orderService) {
  return async function placeOrderHandler(req, res) {
    try {
      const { userId, items, amount } = req.body;
      const order = await orderService.placeOrder(userId, items, amount);
      res.status(201).json(order);
    } catch (err) {
      res.status(400).json({ error: err.message });
    }
  };
}

module.exports = { createOrderController };

// orderController.test.js — unit test the handler without a real HTTP server
// by mocking req/res objects directly
const { createOrderController } = require('./orderController');

test('returns 201 and order on success', async () => {
  const mockOrderService = {
    placeOrder: jest.fn().mockResolvedValue({ id: 'o1', status: 'confirmed' }),
  };
  const handler = createOrderController(mockOrderService);

  const req = { body: { userId: 'u1', items: [{ sku: 'A' }], amount: 100 } };
  const res = { status: jest.fn().mockReturnThis(), json: jest.fn() };

  await handler(req, res);

  expect(res.status).toHaveBeenCalledWith(201);
  expect(res.json).toHaveBeenCalledWith({ id: 'o1', status: 'confirmed' });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Testing implementation details instead of behavior
```javascript
// WRONG: asserting on internal private state
expect(service._cache.size).toBe(1);  // breaks if internals change

// CORRECT: assert on observable output/behavior
expect(await service.getUser('u1')).toEqual({ id: 'u1', name: 'Amit' });
```

❌ Mistake 2: Tests depending on each other / shared mutable state
```javascript
// WRONG: test 2 depends on test 1 running first and leaving state behind
let cart = [];
test('add item', () => { cart.push('item1'); expect(cart.length).toBe(1); });
test('remove item', () => { cart.pop(); expect(cart.length).toBe(0); }); // fragile!

// CORRECT: reset state in beforeEach so tests are independent
let cart;
beforeEach(() => { cart = []; });
test('add item', () => { cart.push('item1'); expect(cart.length).toBe(1); });
test('remove item', () => { cart.push('x'); cart.pop(); expect(cart.length).toBe(0); });
```

---

## 🧠 Tricky Interview Question

```javascript
test('async test without await', () => {
  setTimeout(() => {
    expect(true).toBe(false); // this never gets checked!
  }, 100);
});
console.log('Does this test fail?');
```
Answer: **No, this test passes (incorrectly)!** Jest doesn't know to wait for the `setTimeout` callback — the `test()` function returns synchronously before the callback runs, so Jest marks it as passed. This is a classic Jest trap: you must either `return` a Promise, use `async/await`, or use the `done` callback parameter (`test('name', done => { ...; done(); })`) so Jest knows to wait. Forgetting this gives false-positive passing tests that hide real bugs.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `test()` and `it()` in Jest?
A1: They are exact aliases — `it()` is provided for BDD-style readability (`it('should return true', ...)` reads like a sentence). Functionally identical, pick one convention per project for consistency.

Q2: What is the difference between `toBe()` and `toEqual()`?
A2: `toBe()` uses `Object.is()` — strict reference/primitive equality (fails for two different objects with same content). `toEqual()` does deep recursive value equality on objects/arrays, ignoring reference. Use `toBe()` for primitives (numbers, strings), `toEqual()` for objects/arrays.

Q3: What is a mock function (`jest.fn()`) and why use it?
A3: A mock function replaces a real dependency (like a payment gateway or DB call) with a fake, controllable version. It records calls (`toHaveBeenCalledWith`), lets you set return values (`mockResolvedValue`, `mockReturnValue`), and avoids real side effects (no actual payment charged, no real DB write) — making tests fast, deterministic, and isolated.

Q4: What does code coverage mean and does 100% coverage guarantee no bugs?
A4: Coverage measures the percentage of lines/branches/functions executed by tests. No — 100% coverage only means every line RAN during tests, not that every input/edge case or logical combination was correctly asserted. A test can execute a line without actually checking its output, giving false confidence.

Q5: How do you test a function that depends on `Date.now()` or `Math.random()`?
A5: Mock them. `jest.spyOn(Date, 'now').mockReturnValue(1700000000000)` or `jest.useFakeTimers().setSystemTime(new Date('2024-01-01'))`. For randomness: `jest.spyOn(Math, 'random').mockReturnValue(0.5)`. This makes non-deterministic functions produce deterministic, testable output.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Testing pure functions, business logic, validation, calculations
- Code has clear inputs/outputs you can assert on
- You want fast feedback (unit tests run in milliseconds)

❌ Avoid when:
- You actually need to verify real DB/network behavior (use integration tests instead)
- The function is trivial (e.g., a one-line getter) — diminishing returns
- Testing third-party library internals (trust the library, test your usage of it)

---

## 📊 Visual Diagram
```
UNIT TEST STRUCTURE:
─────────────────────────────────────────────
describe('OrderService')  ← test suite (group)
   │
   ├── beforeEach()       ← setup fresh mocks before each test
   │
   ├── test('places order successfully')
   │     ├── Arrange: create mocks, inputs
   │     ├── Act: call the function
   │     └── Assert: expect(result).toBe(...)
   │
   ├── test('throws when cart is empty')
   └── test('throws when payment fails')

   Real DB ✗        Mock DB ✓
   Real Payment ✗   Mock Payment ✓
   (isolated — fast, no side effects)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Unit test | Test of one isolated function/module | एक isolated function का test |
| Jest | JS testing framework | JS testing framework |
| describe() | Groups related tests | Related tests को group करना |
| expect() | Assertion starter | Assertion शुरू करना |
| Mock | Fake replacement for a dependency | Dependency का नकली version |
| Matcher | Assertion method like toBe/toEqual | जैसे toBe/toEqual |
| Coverage | % of code executed by tests | Tests से कितना code चला |
| beforeEach | Runs before every test | हर test से पहले चलता है |

---

## ⚡ 3-Line Summary
English:
1. Unit tests check one isolated function/module in complete isolation from DB, network, and other modules, using Jest's `test()`, `expect()`, and mocking.
2. Mock dependencies (`jest.fn()`) to avoid real side effects, keep tests fast and deterministic.
3. Always handle async tests with `async/await` or returned Promises — Jest won't wait for a bare `setTimeout` callback and will falsely pass.

Hindi:
1. Unit tests एक isolated function/module को DB, network, और अन्य modules से अलग करके test करते हैं — Jest के `test()`, `expect()`, और mocking से।
2. Real side effects से बचने के लिए dependencies को mock (`jest.fn()`) करो — tests fast और deterministic बनते हैं।
3. Async tests को हमेशा `async/await` या returned Promise से handle करो — Jest बिना await के `setTimeout` callback का इंतज़ार नहीं करता और गलती से test pass हो जाता है।

---

## ➡️ Next Topic
**210. Integration Testing** — multiple modules/components together (e.g. route → service → real test DB) के साथ test करना, mocking के बिना ज़्यादा real-world behavior check करना।
