# 63. assert Module
# हिंदी में: assert Module — Runtime Checks और Testing

---

## 🔵 Simple Definition (English)
The **`assert`** module (`require('assert')`) provides functions to test/verify that a condition is true — if it's NOT true, `assert` throws an `AssertionError`. It's used for writing tests (though most projects use a dedicated test framework like Jest/Mocha on top of or instead of it) and for runtime "this should never happen" invariant checks inside application code.

## 🔵 सरल परिभाषा (Hindi)
**`assert`** module functions देता है यह verify करने के लिए कि कोई condition true है — अगर NOT true है, `assert` `AssertionError` throw करता है। यह tests लिखने के लिए (हालांकि ज़्यादातर projects Jest/Mocha जैसा dedicated test framework use करते हैं) और application code में runtime "यह कभी नहीं होना चाहिए" invariant checks के लिए इस्तेमाल होता है।

---

## 🔴 Problem it Solves
Writing manual `if (condition !== expected) { throw new Error(...) }` checks everywhere is verbose and inconsistent — every developer writes slightly different error messages and comparison logic. `assert` standardizes this into a small, zero-dependency, always-available (core module) library with clear semantics: `assert.strictEqual(actual, expected)`, `assert.deepStrictEqual(obj1, obj2)`, etc. It's especially valuable for quick scripts, internal tooling, and sanity-checking function outputs during development, without pulling in an external testing library.

## 🔴 यह क्यों बना? (Hindi)
हर जगह manual `if (condition !== expected) { throw ... }` checks लिखना verbose और inconsistent है। `assert` इसे एक छोटी, zero-dependency, हमेशा available (core module) library में standardize करता है, clear semantics के साथ। यह quick scripts, internal tooling, और development के दौरान sanity-checking के लिए valuable है, बिना external testing library pull किए।

---

## 🟢 How it Works — Step by Step

Step 1 → Basic truthy check: `assert(value)` or `assert.ok(value)` — throws `AssertionError` if `value` is falsy.
Step 2 → Equality checks: `assert.equal(a, b)` (loose, `==`-style, DEPRECATED in favor of strict), `assert.strictEqual(a, b)` (strict, `===`-style, preferred).
Step 3 → Deep equality for objects/arrays: `assert.deepEqual(obj1, obj2)` (loose) vs `assert.deepStrictEqual(obj1, obj2)` (strict — checks types too, e.g., `1` vs `'1'` would fail strict but pass loose).
Step 4 → Inequality checks: `assert.notEqual()`, `assert.notStrictEqual()`, `assert.notDeepStrictEqual()` — the negated versions.
Step 5 → Error-throwing checks: `assert.throws(fn, expectedError)` verifies a function throws (optionally matching a specific error type/message); `assert.doesNotThrow(fn)` verifies it doesn't.
Step 6 → `assert.rejects(asyncFn)`/`assert.doesNotReject(asyncFn)` — Promise-aware versions for testing async code that should/shouldn't reject.
Step 7 → All `assert.*` functions accept an optional final argument for a CUSTOM error message, making failures easier to diagnose.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Basic truthy check: `assert(value)` — falsy होने पर throw करता है।
Step 2 → Equality: `assert.equal()` (loose, deprecated), `assert.strictEqual()` (strict, preferred)।
Step 3 → Deep equality: `assert.deepEqual()` vs `assert.deepStrictEqual()` (types भी check करता है)।
Step 4 → Negated versions: `assert.notEqual()`, `assert.notStrictEqual()` आदि।
Step 5 → Error checks: `assert.throws(fn)` function throw करे यह verify करता है; `assert.doesNotThrow()` उल्टा।
Step 6 → `assert.rejects()`/`assert.doesNotReject()` — async code के लिए Promise-aware versions।
Step 7 → सभी functions optional custom error message accept करते हैं।

---

## 🟡 Real World Example
**PhonePe's internal data-migration script sanity checks:** Before running a production database migration that updates millions of wallet balance records, an engineer writes a quick Node script using `assert` to validate assumptions: `assert.strictEqual(typeof record.balance, 'number', 'Balance must be a number')`, `assert.ok(record.balance >= 0, 'Balance cannot be negative')`. If ANY record violates these invariants, the script immediately throws and halts BEFORE committing any changes — a cheap, dependency-free safety net for a one-off critical script, rather than pulling in a full test framework for a 50-line migration tool.

## 🟡 Real Example Hindi mein
**PhonePe internal data-migration script sanity checks:** Production migration चलाने से पहले, engineer `assert` से assumptions validate करता है — balance number है, negative नहीं। कोई भी record violate करे तो script तुरंत throw करके रुक जाता है, changes commit होने से पहले। यह एक cheap, dependency-free safety net है, 50-line migration tool के लिए पूरा test framework नहीं चाहिए।

---

## 💻 Code Example — Basic
```javascript
// assert-basics.js
const assert = require('assert');

// 1. BASIC TRUTHY CHECK
assert(1 + 1 === 2); // passes silently, no output
try {
  assert(1 + 1 === 3, 'Math is broken!'); // custom error message
} catch (err) {
  console.log('Caught:', err.message); // "Math is broken!"
}

// 2. STRICT EQUALITY (preferred over loose equal())
assert.strictEqual(5, 5); // passes
try {
  assert.strictEqual(5, '5'); // fails -- strict mode checks TYPE too
} catch (err) {
  console.log('Caught:', err.message); // shows expected vs actual
}

// 3. DEEP EQUALITY for objects/arrays
assert.deepStrictEqual({ a: 1, b: 2 }, { a: 1, b: 2 }); // passes -- same structure/values
try {
  assert.deepStrictEqual({ a: 1 }, { a: '1' }); // fails -- 1 !== '1' (type mismatch)
} catch (err) {
  console.log('Deep equal caught:', err.message);
}

// 4. ASSERT.THROWS -- verify a function throws an error
assert.throws(
  () => { throw new Error('Expected failure'); },
  /Expected failure/, // can match against a regex or error constructor
  'Function should have thrown'
);
console.log('assert.throws passed -- function threw as expected');

// 5. ASSERT.DOESNOTTHROW -- verify a function does NOT throw
assert.doesNotThrow(() => { const x = 1 + 1; }, undefined, 'Should not throw');
console.log('All basic assertions completed');
```

## 💻 Code Example — Advanced
```javascript
// assert-advanced.js -- production patterns
const assert = require('assert');
const assertStrict = require('assert').strict; // all methods default to strict behavior

// ─── 1. VALIDATING FUNCTION INPUTS WITH ASSERTIONS (defensive programming) ────
function calculateDiscount(price, discountPercent) {
  assert.strictEqual(typeof price, 'number', 'price must be a number');
  assert.ok(price >= 0, 'price cannot be negative');
  assert.ok(discountPercent >= 0 && discountPercent <= 100, 'discountPercent must be 0-100');

  return price - (price * discountPercent) / 100;
}

try {
  console.log(calculateDiscount(1000, 20)); // 800
  calculateDiscount(1000, 150); // throws -- invalid discount percentage
} catch (err) {
  console.error('Validation failed:', err.message);
}

// ─── 2. ASSERT.REJECTS FOR TESTING ASYNC CODE ────────────────────────────────
async function fetchUserOrThrow(id) {
  if (id < 0) throw new Error('Invalid user ID');
  return { id, name: 'Sample User' };
}

async function testFetchUser() {
  // Verify the promise RESOLVES successfully for valid input
  const user = await fetchUserOrThrow(1);
  assert.strictEqual(user.id, 1);

  // Verify the promise REJECTS for invalid input
  await assert.rejects(
    fetchUserOrThrow(-1),
    { message: 'Invalid user ID' }, // can match against an object pattern
    'Should reject for negative ID'
  );
  console.log('Async assertions passed');
}
testFetchUser();

// ─── 3. DATA MIGRATION SANITY CHECKS (real production pattern) ──────────────
function validateRecordBeforeMigration(record) {
  assert.strictEqual(typeof record.id, 'string', `Record ${JSON.stringify(record)} has invalid id type`);
  assert.strictEqual(typeof record.balance, 'number', `Record ${record.id} has non-numeric balance`);
  assert.ok(record.balance >= 0, `Record ${record.id} has negative balance: ${record.balance}`);
  assert.ok(Number.isFinite(record.balance), `Record ${record.id} has non-finite balance`);
}

function runMigration(records) {
  // Validate ALL records BEFORE making any changes -- fail fast, fail safe
  records.forEach(validateRecordBeforeMigration);
  console.log(`All ${records.length} records passed validation. Proceeding with migration...`);
  // ... actual migration logic here ...
}

try {
  runMigration([
    { id: 'u1', balance: 500 },
    { id: 'u2', balance: 1200 },
  ]);
} catch (err) {
  console.error('MIGRATION ABORTED:', err.message);
  process.exit(1); // halt before any data is touched
}

module.exports = { calculateDiscount, validateRecordBeforeMigration };
```

---

## 🟠 Express.js Integration
```javascript
const express = require('express');
const assert = require('assert');
const app = express();

app.use(express.json());

// 1. USING ASSERT FOR INTERNAL INVARIANT CHECKS (NOT for user-facing validation --
//    use a proper validator like Joi/Zod for that; assert is for catching BUGS)
function processOrder(order) {
  // These are INTERNAL invariants that should NEVER fail if upstream code is correct --
  // if they DO fail, it indicates a BUG in our own code, not bad user input
  assert.strictEqual(typeof order.total, 'number', 'INTERNAL BUG: order.total must be a number');
  assert.ok(order.total >= 0, 'INTERNAL BUG: order.total cannot be negative at this point');
  return { ...order, status: 'processed' };
}

app.post('/orders', (req, res) => {
  // User input validation (SEPARATE from internal assertions) -- proper error response
  if (typeof req.body.total !== 'number' || req.body.total < 0) {
    return res.status(400).json({ error: 'Invalid order total' });
  }

  try {
    const processed = processOrder(req.body); // internal assert() calls run here as a safety net
    res.json(processed);
  } catch (err) {
    // An AssertionError here means a BUG slipped past validation -- log it as critical
    console.error('CRITICAL: Internal assertion failed', err.message);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 2. STARTUP SANITY CHECKS (verify environment/config before the server starts)
function validateEnvironment() {
  assert.ok(process.env.DATABASE_URL, 'DATABASE_URL environment variable is required');
  assert.ok(process.env.PORT, 'PORT environment variable is required');
  console.log('Environment validation passed');
}

try {
  validateEnvironment();
  app.listen(process.env.PORT || 3000);
} catch (err) {
  console.error('Startup validation failed:', err.message);
  process.exit(1); // refuse to start with invalid configuration
}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `assert.equal()` (loose) instead of `assert.strictEqual()` (strict)
```javascript
// Wrong -- loose equal() uses == semantics, hiding type mismatches
assert.equal(5, '5'); // PASSES silently -- but these are different types!

// Correct -- strictEqual catches the type mismatch
assert.strictEqual(5, '5'); // THROWS -- correctly flags the type difference
```

❌ Mistake 2: Using `assert` for user-facing input validation instead of internal invariants
```javascript
// Wrong -- AssertionError isn't meant to be a user-facing HTTP error; messages/format aren't ideal
app.post('/signup', (req, res) => {
  assert.ok(req.body.email, 'Email is required'); // crashes the request handler ungracefully
});

// Correct -- use a validation library (Joi, Zod, express-validator) for user input,
// reserve assert for INTERNAL "this should never happen" checks
app.post('/signup', (req, res) => {
  if (!req.body.email) return res.status(400).json({ error: 'Email is required' });
});
```

❌ Mistake 3: Forgetting that `assert.deepEqual()` (loose) doesn't check types, unlike `deepStrictEqual()`
```javascript
// Wrong -- using loose deepEqual, missing a real bug in production migration code
assert.deepEqual({ count: 5 }, { count: '5' }); // PASSES -- type difference hidden!

// Correct -- deepStrictEqual catches this
assert.deepStrictEqual({ count: 5 }, { count: '5' }); // THROWS -- correctly flags the bug
```

---

## 🧠 Tricky Interview Question
```javascript
const assert = require('assert');

console.log('Test 1:');
try {
  assert.equal(0, false); // loose equality
  console.log('Passed');
} catch (err) { console.log('Failed:', err.message); }

console.log('Test 2:');
try {
  assert.strictEqual(0, false); // strict equality
  console.log('Passed');
} catch (err) { console.log('Failed:', err.message); }
```
Answer: Test 1 prints `'Passed'` and Test 2 prints `'Failed: ...'`. `assert.equal()` uses LOOSE (`==`) comparison semantics — JavaScript's `==` operator coerces `false` to `0` for comparison, so `0 == false` is `true`, and the assertion passes. `assert.strictEqual()` uses STRICT (`===`) comparison — no type coercion occurs, and since `0` (a number) and `false` (a boolean) are different TYPES, `0 === false` is `false`, causing the assertion to throw. This demonstrates exactly why `strictEqual`/`deepStrictEqual` are recommended over their loose counterparts — loose equality's implicit coercion can mask real bugs (type mismatches) that strict equality correctly catches.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `assert.equal()` and `assert.strictEqual()`?
A1: `assert.equal(a, b)` uses loose (`==`) comparison, which performs type coercion before comparing (e.g., `'5' == 5` is `true`). `assert.strictEqual(a, b)` uses strict (`===`) comparison with NO type coercion — values must be the same type AND value to pass. `strictEqual` is universally recommended because loose equality can silently pass tests/checks that should actually fail due to a type mismatch, hiding real bugs.

Q2: When would you use `assert` in application code versus using a dedicated testing framework like Jest or Mocha?
A2: `assert` (the core module) is best for: quick scripts/tooling without wanting an external dependency, and INTERNAL runtime invariant checks within application logic ("this condition should always be true if the rest of the code is correct — if not, something is seriously broken"). Dedicated frameworks (Jest, Mocha + Chai) are better for actual TEST SUITES — they provide test runners, better reporting, mocking, snapshot testing, and nicer assertion syntax (`expect(x).toBe(y)`), which `assert` alone doesn't offer; many frameworks use `assert`-like logic under the hood but wrap it in much richer tooling.

Q3: What's the difference between `assert.deepEqual()` and `assert.deepStrictEqual()`?
A3: Both recursively compare the structure/contents of objects/arrays for equality, but `deepEqual()` uses loose comparison rules for individual values (so `{ a: 1 }` and `{ a: '1' }` would be considered equal), while `deepStrictEqual()` also checks that types match at every level (so that same comparison would FAIL) AND additionally checks that the objects have the same prototype/constructor. `deepStrictEqual()` is the recommended default for the same reason `strictEqual()` is preferred over `equal()`.

Q4: How do you test that an async function properly rejects/throws using the `assert` module?
A4: Use `await assert.rejects(asyncFunctionCall(), expectedErrorOrMatcher)` — it awaits the given Promise and asserts that it REJECTS, optionally verifying the rejection reason matches a given error class, regex, or object shape. There's a corresponding `assert.doesNotReject()` to verify a Promise resolves successfully (doesn't reject) — both are async-aware counterparts to the synchronous `assert.throws()`/`assert.doesNotThrow()`.

Q5: Is it a good practice to use `assert()` for validating user-supplied HTTP request data? Why or why not?
A5: Generally NO — `assert` throws an `AssertionError` with a stack trace and a format meant for developer-facing diagnostics, not a clean, user-friendly HTTP error response. For user input validation, use a dedicated schema-validation library (Joi, Zod, express-validator, class-validator) that integrates with your HTTP error-response conventions (consistent JSON error shapes, field-level messages, proper status codes). Reserve `assert` for INTERNAL invariants — conditions that reflect bugs in YOUR OWN code if violated, not conditions that depend on external/user input that's expected to sometimes be invalid.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Writing quick scripts/tools that need lightweight sanity checks without external dependencies
- Validating internal invariants in application code ("this should never be false if my code is correct")
- Pre-flight sanity checks before risky operations (data migrations, destructive scripts)

❌ Avoid when:
- Validating user-facing input in an HTTP API — use a proper validation library with clean error responses instead
- Building a full test suite — use Jest/Mocha/Vitest for proper test organization, mocking, and reporting
- You need loose equality checks for legitimate reasons — prefer the strict variants by default, use loose deliberately and rarely

---

## 📊 Visual Diagram
```
ASSERT FUNCTION FAMILY:

  Truthy check:        assert(value) / assert.ok(value)
  Equality (loose):     assert.equal(a, b)           -- == semantics, coercion
  Equality (strict):    assert.strictEqual(a, b)     -- === semantics, NO coercion (preferred)
  Deep equality (loose): assert.deepEqual(obj1, obj2)
  Deep equality (strict): assert.deepStrictEqual(obj1, obj2)  -- preferred
  Error expectation:    assert.throws(fn, matcher)
  No-error expectation: assert.doesNotThrow(fn)
  Async rejection:       assert.rejects(promiseOrFn)
  Async no-rejection:    assert.doesNotReject(promiseOrFn)

FLOW ON FAILURE:
  assert.strictEqual(actual, expected)
       │
       ▼ mismatch detected
  throws new AssertionError({ actual, expected, operator: 'strictEqual' })
       │
       ▼ uncaught
  Process crashes (or caught by try/catch for graceful handling)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| AssertionError | Error thrown when assertion fails | Assertion fail होने पर thrown error |
| strictEqual | === comparison, no coercion | === comparison, coercion नहीं |
| deepStrictEqual | Recursive strict object comparison | Recursive strict object comparison |
| assert.throws | Verify a function throws | Function throw करे यह verify करना |
| assert.rejects | Verify a Promise rejects | Promise reject करे यह verify करना |
| invariant | Condition that must always hold | हमेशा सच रहने वाली condition |

---

## ⚡ 3-Line Summary
English: `assert` provides lightweight, dependency-free checks that throw `AssertionError` when a condition fails — useful for quick scripts, internal invariant checks, and data-migration sanity checks. Always prefer `strictEqual`/`deepStrictEqual` over their loose counterparts to catch type mismatches. Use a real validation library for user-facing input, and a proper test framework for test suites.

Hindi: `assert` lightweight, dependency-free checks देता है जो condition fail होने पर `AssertionError` throw करते हैं — quick scripts, internal invariant checks, data-migration sanity checks के लिए useful। हमेशा `strictEqual`/`deepStrictEqual` prefer करो। User-facing input के लिए real validation library, test suites के लिए proper test framework use करो।

---

## ➡️ Next Topic
**64. dns Module** — performing DNS lookups and resolution programmatically in Node.js (already covered in this directory — see 64-dns-module.md).
