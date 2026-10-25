# 213. Test Coverage
# हिंदी में: Test Coverage — Code का कितना हिस्सा Tests से Execute होता है

---

## 🔵 Simple Definition (English)
**Test coverage** is a percentage metric showing how much of your source code was executed while running the test suite. Jest (built on Istanbul) reports four coverage types: **statements**, **branches**, **functions**, and **lines**. High coverage doesn't guarantee correctness, but low coverage reliably signals untested code.

## 🔵 सरल परिभाषा (Hindi)
**Test coverage** एक percentage metric है जो बताता है कि test suite चलाने पर source code का कितना हिस्सा actually execute हुआ। Jest (Istanbul पर based) चार coverage types report करता है: **statements**, **branches**, **functions**, और **lines**। High coverage correctness guarantee नहीं करता, पर low coverage reliably untested code की तरफ इशारा करता है।

---

## 🔴 Problem it Solves
Without coverage metrics, a team has no visibility into which parts of the codebase have zero tests — a critical `refundPayment()` function could have been untested for months and nobody would know until it breaks in production. Coverage reports (and CI gates like "coverage must stay above 80%") give objective, enforceable visibility into testing gaps, and prevent new untested code from being merged silently.

## 🔴 यह क्यों बना? (Hindi)
Coverage metrics के बिना, team को पता नहीं चलता कि codebase के किन हिस्सों में zero tests हैं — एक critical `refundPayment()` function महीनों तक untested रह सकता है और किसी को पता नहीं चलेगा जब तक production में टूट न जाए। Coverage reports (और CI gates जैसे "coverage 80% से नीचे नहीं जाना चाहिए") testing gaps में objective, enforceable visibility देते हैं, और untested code को silently merge होने से रोकते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Run `jest --coverage` — Jest instruments the code (via Istanbul/babel-plugin-istanbul) to track which lines/branches execute
Step 2 → Each test run records which statements, branches (if/else paths), functions, and lines were hit
Step 3 → Jest generates a report: terminal summary table + an HTML report (`coverage/lcov-report/index.html`) with line-by-line highlighting (green = covered, red = not covered)
Step 4 → Set thresholds in `jest.config.js` (`coverageThreshold`) so CI fails the build if coverage drops below a set percentage
Step 5 → Review uncovered lines/branches shown in red, and decide whether they need a test or are truly unreachable (and can be ignored)

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `jest --coverage` चलाओ — Jest code को instrument करता है (Istanbul/babel-plugin-istanbul से) ताकि track कर सके कि कौन सी lines/branches execute हुईं
Step 2 → हर test run record करता है कि कौन सी statements, branches (if/else paths), functions, lines hit हुईं
Step 3 → Jest एक report बनाता है: terminal summary table + HTML report (`coverage/lcov-report/index.html`) जिसमें line-by-line highlighting होती है (green = covered, red = not covered)
Step 4 → `jest.config.js` में thresholds set करो (`coverageThreshold`) ताकि coverage set percentage से नीचे जाने पर CI build fail हो
Step 5 → Red में दिखी uncovered lines/branches review करो, decide करो कि test चाहिए या truly unreachable है (ignore किया जा सकता है)

---

## 🟡 Real World Example
**Amazon India's payments team** enforces an 85% branch coverage gate in CI for the `payments-service` repo. When a developer adds a new `applyCashback()` function with an untested edge case (cashback cap exceeded), the coverage report shows that branch in red, and the PR check fails with "Coverage dropped below threshold: branches 83% < 85%". The developer is forced to add the missing test before merging — catching a bug (cashback not capped correctly) that would have cost real money in production.

## 🟡 Real Example Hindi mein
**Amazon India की payments team** अपने `payments-service` repo में CI में 85% branch coverage gate enforce करती है। जब developer एक नया `applyCashback()` function add करता है जिसमें एक untested edge case (cashback cap exceed) है, coverage report उस branch को red में दिखाता है, और PR check fail हो जाता है: "Coverage dropped below threshold: branches 83% < 85%"। Developer को merge से पहले missing test add करना पड़ता है।

---

## 💻 Code Example — Basic

```javascript
// pricing.js — function with multiple branches to demonstrate branch coverage
function getShippingCost(weight, isPrimeMember, distanceKm) {
  // Branch 1
  if (isPrimeMember && distanceKm < 10) {
    return 0; // free shipping for Prime members nearby
  }
  // Branch 2
  if (weight > 20) {
    return 150; // heavy item surcharge
  }
  // Branch 3 (default/fallback)
  return 50;
}

module.exports = { getShippingCost };
```

```javascript
// pricing.test.js — tests that DON'T cover all branches (intentionally incomplete)
const { getShippingCost } = require('./pricing');

test('prime member nearby gets free shipping', () => {
  expect(getShippingCost(5, true, 5)).toBe(0); // covers Branch 1 (true path)
});

test('default shipping cost for normal case', () => {
  expect(getShippingCost(5, false, 20)).toBe(50); // covers Branch 3
});

// MISSING: a test for heavy item (weight > 20) — Branch 2 never executes!
// Run: npx jest --coverage pricing.test.js
// Report will show: Branches 66.6% (2 of 3), with line for "weight > 20" in RED
```

## 💻 Code Example — Advanced

```javascript
// jest.config.js — configuring coverage collection and enforcing thresholds
module.exports = {
  // Which files to INCLUDE in coverage calculation (even untested ones count as 0%)
  collectCoverageFrom: [
    'src/**/*.js',
    '!src/**/*.test.js',       // exclude test files themselves
    '!src/config/**',          // exclude config (not meaningful to test)
    '!src/index.js',           // exclude entry point (just wiring)
  ],
  coverageDirectory: 'coverage', // output folder for HTML/lcov reports
  coverageReporters: ['text', 'html', 'lcov'], // text = terminal summary, html = browsable report

  // Enforce minimum coverage — CI build FAILS if these aren't met
  coverageThreshold: {
    global: {
      statements: 80,
      branches: 75,
      functions: 80,
      lines: 80,
    },
    // Stricter rules for critical payment code
    './src/services/paymentService.js': {
      statements: 95,
      branches: 90,
    },
  },
};
```

```javascript
// pricing.complete.test.js — now covering ALL branches
const { getShippingCost } = require('./pricing');

describe('getShippingCost — full branch coverage', () => {
  test('prime member nearby: free shipping', () => {
    expect(getShippingCost(5, true, 5)).toBe(0);
  });

  test('prime member but far away: not free', () => {
    // Important: isPrimeMember=true but distanceKm >= 10 — tests the && short-circuit
    expect(getShippingCost(5, true, 15)).toBe(50);
  });

  test('heavy item surcharge applies', () => {
    expect(getShippingCost(25, false, 5)).toBe(150); // covers Branch 2
  });

  test('normal case default cost', () => {
    expect(getShippingCost(5, false, 20)).toBe(50); // covers Branch 3
  });
});
// Run: npx jest --coverage
// Report now shows: Statements 100%, Branches 100%, Functions 100%, Lines 100%
```

---

## 🟠 Express.js Integration

```javascript
// package.json scripts — wiring coverage into CI pipeline
{
  "scripts": {
    "test": "jest",
    "test:coverage": "jest --coverage",
    "test:ci": "jest --coverage --ci --maxWorkers=2"
  }
}

// .github/workflows/test.yml — GitHub Actions CI step that enforces coverage
// (fails the pipeline automatically if coverageThreshold in jest.config.js isn't met)
// steps:
//   - run: npm ci
//   - run: npm run test:ci
//   - uses: actions/upload-artifact@v4   # upload HTML coverage report for review
//     with:
//       name: coverage-report
//       path: coverage/lcov-report

// Express route example showing WHY the payment branch needs high coverage:
app.post('/refund', async (req, res) => {
  const { orderId, amount, reason } = req.body;
  if (amount > order.paidAmount) {           // branch 1 — must be tested!
    return res.status(400).json({ error: 'Refund exceeds paid amount' });
  }
  if (reason === 'fraud' && !req.user.isAdmin) { // branch 2 — must be tested!
    return res.status(403).json({ error: 'Only admin can process fraud refunds' });
  }
  const refund = await processRefund(orderId, amount);
  res.json(refund);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Chasing 100% line coverage while ignoring branch coverage
```javascript
// A ternary can be "covered" by line count but only one branch tested:
const fee = isUrgent ? 100 : 50;
// test only calls with isUrgent=true → LINE is covered, but the `: 50` BRANCH is not!

// CORRECT: always check BRANCH coverage %, not just line %, especially for conditionals
```

❌ Mistake 2: Writing tests that execute code without actually asserting anything meaningful
```javascript
// WRONG: inflates coverage % without really testing behavior
test('calls getShippingCost', () => {
  getShippingCost(5, true, 5); // no expect()! line is "covered" but nothing is verified
});

// CORRECT: always assert on the output
test('calls getShippingCost', () => {
  expect(getShippingCost(5, true, 5)).toBe(0);
});
```

---

## 🧠 Tricky Interview Question

```javascript
function isEligible(age, hasLicense) {
  return age >= 18 && hasLicense;
}
// Test suite has exactly ONE test:
test('eligible when 18+ and has license', () => {
  expect(isEligible(20, true)).toBe(true);
});
// ❓ What will line coverage show for this function? 100%?
```
Answer: **Line coverage shows 100%** (the single `return` statement executed), but **branch coverage is only 50%**. The `&&` operator short-circuits — this test never exercises the case where `age >= 18` is false, or where it's true but `hasLicense` is false. A function can have 100% LINE coverage while still having completely untested logical branches — this is exactly why relying only on line coverage is misleading, and branch coverage is the more meaningful metric for conditional logic.

---

## ⚫ Interview Questions + Answers

Q1: What are the 4 coverage metrics Jest reports?
A1: **Statements** (% of executable statements run), **Branches** (% of if/else, ternary, `&&`/`||` paths taken), **Functions** (% of functions called at least once), **Lines** (% of lines executed — similar to statements but line-based, not statement-based).

Q2: Does 100% coverage mean the code has no bugs?
A2: No. Coverage only measures that code RAN during tests — it says nothing about whether the test actually asserted the CORRECT expected output. A test with no `expect()` or a weak assertion can still count toward 100% coverage while verifying nothing meaningful. Coverage is a floor for "untested code," not a ceiling for "bug-free code."

Q3: How do you exclude certain files from coverage calculation?
A3: Use `collectCoverageFrom` with negation patterns (`!src/config/**`) in Jest config, or inline comments like `/* istanbul ignore next */` to skip a specific block (used sparingly, e.g. for genuinely unreachable defensive code).

Q4: What coverage threshold is considered "good" in production teams?
A4: There's no universal number, but 70-85% for most application code is common and pragmatic; critical paths (payments, auth, security) often target 90%+. Chasing 100% everywhere has diminishing returns and can encourage shallow, assertion-less tests just to hit the number.

Q5: How does Jest actually measure coverage under the hood?
A5: Jest uses Istanbul (via `babel-plugin-istanbul` or native V8 coverage with `--coverage-provider=v8`) to instrument the code — inserting counters at each statement/branch/function during a build step before running tests. As tests execute, these counters increment; after all tests finish, Jest aggregates counter data into the coverage report.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want objective visibility into untested code paths
- Enforcing a quality gate in CI for critical codebases (payments, auth)
- Reviewing a legacy codebase to find high-risk, zero-coverage modules

❌ Avoid when:
- Treating coverage % as the sole measure of test quality (pair it with code review of actual assertions)
- Forcing 100% coverage on trivial/generated code (diminishing returns, wastes effort)

---

## 📊 Visual Diagram
```
COVERAGE REPORT (terminal output):
──────────────────────────────────────────────────────────────
File          | % Stmts | % Branch | % Funcs | % Lines | Uncovered
──────────────────────────────────────────────────────────────
pricing.js    |   100   |   100    |   100   |   100   |
paymentSvc.js |    72   |    60    |    80   |    72   | 45-52,88
──────────────────────────────────────────────────────────────
                    ↑ RED FLAG: low branch coverage on payment logic!

HTML report (coverage/lcov-report/index.html):
  Line 45: if (amount > maxRefund) {   ← highlighted RED (never tested)
  Line 46:   throw new Error(...)       ← RED
  Line 48: return processRefund();      ← GREEN (tested)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Coverage | % of code executed by tests | Tests से चला code का % |
| Statement coverage | % of statements executed | Executed statements का % |
| Branch coverage | % of if/else paths taken | if/else paths का % |
| Function coverage | % of functions called | Called functions का % |
| coverageThreshold | Minimum required % to pass CI | CI pass करने का minimum % |
| Istanbul | Coverage instrumentation tool Jest uses | Jest का coverage tool |
| Uncovered lines | Lines never executed by any test | किसी test से न चली lines |

---

## ⚡ 3-Line Summary
English:
1. Test coverage measures the percentage of statements, branches, functions, and lines executed during tests — run with `jest --coverage`.
2. Branch coverage is more meaningful than line coverage for conditional logic — a line can be "covered" while one of its logical branches is never tested.
3. Use `coverageThreshold` in CI to enforce minimum coverage and prevent untested code from being merged, but never treat high coverage alone as proof of correctness.

Hindi:
1. Test coverage statements, branches, functions, lines का वो % measure करता है जो tests के दौरान execute हुआ — `jest --coverage` से चलाओ।
2. Conditional logic के लिए branch coverage, line coverage से ज़्यादा meaningful है — एक line "covered" हो सकती है जबकि उसकी एक logical branch कभी test नहीं हुई।
3. CI में `coverageThreshold` से minimum coverage enforce करो ताकि untested code merge न हो, पर high coverage को कभी correctness का proof मत मानो।

---

## ➡️ Next Topic
**214. TDD — Test Driven Development** — tests को implementation code से पहले लिखना, Red-Green-Refactor cycle।
