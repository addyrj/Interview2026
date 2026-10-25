# 199. Error Handling — try/catch
# हिंदी में: Error Handling — try/catch

---

## 🔵 Simple Definition (English)
**`try/catch`** is JavaScript's structured error-handling mechanism: code that might throw goes in the `try` block, and if it does throw, control jumps to the `catch` block instead of crashing the program. In Node.js, it works seamlessly with `async`/`await` to catch rejected promises, but it does NOT automatically catch errors from callbacks or un-awaited promises — those need different handling strategies.

## 🔵 सरल परिभाषा (Hindi)
**`try/catch`** JavaScript का structured error-handling तरीका है: जो code fail हो सकता है वो `try` block में जाता है, fail होने पर control `catch` block में चला जाता है, program crash नहीं होता। Node.js में यह `async`/`await` के साथ अच्छे से काम करता है rejected promises catch करने के लिए, लेकिन callbacks या un-awaited promises के errors को automatically catch नहीं करता — उनके लिए अलग strategy चाहिए।

---

## 🔴 Problem it Solves
```
PROBLEM WITHOUT ERROR HANDLING:
  An uncaught exception in Node.js crashes the ENTIRE process
  (not just the request that caused it) — bringing down the whole server
  for every user, even ones with unrelated, perfectly fine requests

TRY/CATCH SOLUTION:
  Contain failures to the specific operation that failed
  Let the rest of the application keep running normally
  Give you a chance to log, clean up, retry, or return a friendly error
  to the specific user who triggered it, instead of taking everyone down
```

## 🔴 यह क्यों बना? (Hindi)
```
Problem: बिना error handling, uncaught exception पूरा process crash कर देता है
सिर्फ एक request का problem पूरे server को नीचे ले जाता है
try/catch solution: failure को उस specific operation तक contain करो
बाकी application normally चलती रहे, friendly error दो
```

---

## 🟢 How it Works — Step by Step

Step 1 → Code that might throw goes inside `try { ... }`
Step 2 → If a `throw` statement executes (or a built-in operation throws), control immediately jumps to the matching `catch (err) { ... }` block — remaining code in `try` is SKIPPED
Step 3 → `catch` receives the thrown value (usually an `Error` object) and can log it, transform it, or re-throw it
Step 4 → `finally { ... }` (optional) always runs after try/catch, whether an error occurred or not — good for cleanup (closing connections, releasing locks)
Step 5 → With `async`/`await`, a rejected awaited promise behaves exactly like a `throw` — it's catchable with regular `try/catch` around the `await`

## 🟢 कैसे काम करता है? (Hindi)
```
1. जो code fail हो सकता है वो try{} में जाता है
2. throw होने पर control catch(err){} में jump करता है, बाकी try{} code skip होता है
3. catch error value receive करता है — log, transform, या re-throw कर सकता है
4. finally{} हमेशा चलता है, error हो या न हो
5. async/await में await का reject होना throw जैसा behave करता है — try/catch से catch होता है
```

---

## 🟡 Real World Example
**Razorpay payment gateway call:** When calling an external bank API to process a payment, many things can go wrong — network timeout, bank API returning a 500, invalid card data, insufficient funds. Razorpay's integration code wraps the entire bank call in `try/catch`: on success it marks the payment captured; on `catch`, it inspects the specific error type (timeout vs. decline vs. invalid data) and returns the RIGHT error code to the merchant, logs it for their fraud/ops team, and crucially does NOT let that one failed payment crash the server process handling thousands of OTHER concurrent payments.

## 🟡 Real Example Hindi mein
**Razorpay payment gateway:** Bank API call में network timeout, 500 error, invalid card — कुछ भी हो सकता है। पूरे bank call को `try/catch` में wrap किया जाता है। `catch` में error type check करके सही error code merchant को भेजा जाता है, log होता है — एक payment fail होने से पूरा server crash नहीं होता।

---

## 💻 Code Example — Basic

```javascript
// basic-try-catch.js
// Run: node basic-try-catch.js

function parseConfig(jsonString) {
  try {
    // JSON.parse throws SyntaxError on invalid JSON
    const config = JSON.parse(jsonString);
    console.log('Parsed config:', config);
    return config;
  } catch (err) {
    // Control lands here if JSON.parse throws
    console.error('Failed to parse config:', err.message);
    return null;  // return a safe fallback instead of crashing
  } finally {
    // Runs whether parsing succeeded or failed — good for cleanup/logging
    console.log('Config parsing attempt finished');
  }
}

parseConfig('{"port": 3000}');       // valid — logs parsed config
parseConfig('{invalid json}');        // invalid — logs error, returns null, no crash

// Async version — try/catch around an await
async function fetchConfig() {
  try {
    const result = await Promise.reject(new Error('Network down'));
    console.log(result);  // never reached
  } catch (err) {
    console.error('Async catch:', err.message);
  }
}
fetchConfig();
```

## 💻 Code Example — Advanced

```javascript
// advanced-error-handling.js
// Production pattern: custom error classes, centralized handling, retry logic

// Custom error classes carry more context than generic Error
class ValidationError extends Error {
  constructor(message, field) {
    super(message);
    this.name = 'ValidationError';
    this.field = field;
    this.statusCode = 400;
  }
}

class PaymentGatewayError extends Error {
  constructor(message, isRetryable) {
    super(message);
    this.name = 'PaymentGatewayError';
    this.isRetryable = isRetryable;  // some failures (timeout) can be retried, others (declined) can't
    this.statusCode = 502;
  }
}

function validateOrder(order) {
  if (!order.amount || order.amount <= 0) {
    throw new ValidationError('Amount must be positive', 'amount');
  }
}

function callBankApi(order) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (order.amount > 100000) {
        // Simulate a retryable timeout for very large amounts
        return reject(new PaymentGatewayError('Gateway timeout', true));
      }
      resolve({ transactionId: 'txn_123', amount: order.amount });
    }, 50);
  });
}

// Retry wrapper — retries only errors explicitly marked retryable
async function withRetry(fn, maxAttempts = 3) {
  let lastError;
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();  // success — return immediately
    } catch (err) {
      lastError = err;
      if (!(err instanceof PaymentGatewayError) || !err.isRetryable) {
        throw err;  // non-retryable error — fail fast, don't retry
      }
      console.log(`Attempt ${attempt} failed (retryable), retrying...`);
    }
  }
  throw lastError;  // all attempts exhausted
}

async function processPayment(order) {
  try {
    validateOrder(order);  // throws ValidationError synchronously
    const result = await withRetry(() => callBankApi(order));
    return result;
  } catch (err) {
    // Differentiate error TYPES to decide the right response
    if (err instanceof ValidationError) {
      console.error(`Validation failed on field "${err.field}": ${err.message}`);
    } else if (err instanceof PaymentGatewayError) {
      console.error(`Payment gateway failed: ${err.message}`);
    } else {
      console.error('Unexpected error:', err.message);
    }
    throw err;  // re-throw so the caller (e.g., Express route) can respond appropriately
  }
}

processPayment({ amount: 500 }).then((r) => console.log('Success:', r)).catch(() => {});
processPayment({ amount: -10 }).catch(() => {});  // triggers ValidationError
```

---

## 🟠 Express.js Integration

```javascript
// Express centralized error-handling middleware pattern
const express = require('express');
const app = express();
app.use(express.json());

class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
  }
}

app.post('/api/orders', async (req, res, next) => {
  try {
    const { amount } = req.body;
    if (!amount || amount <= 0) {
      throw new AppError('Amount must be positive', 400);  // throw a typed error
    }
    // Simulate an async DB call that might fail
    const order = await createOrder(amount);
    res.status(201).json(order);
  } catch (err) {
    next(err);  // forward to the centralized error-handling middleware below
  }
});

async function createOrder(amount) {
  if (amount > 1000000) throw new AppError('Amount exceeds limit', 422);
  return { orderId: 'ord_1', amount };
}

// Express error-handling middleware: MUST have 4 params (err, req, res, next)
// Express recognizes this signature specifically and routes errors here
app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  console.error(`[${statusCode}] ${err.message}`);
  res.status(statusCode).json({ error: err.message });
});

// Catch truly unexpected crashes so the PROCESS doesn't die silently
process.on('unhandledRejection', (reason) => {
  console.error('Unhandled Promise Rejection:', reason);
});

app.listen(3000, () => console.log('Server on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Wrapping code in `try/catch` but swallowing the error silently (empty `catch` block) — hides real bugs, makes debugging production issues nearly impossible.
✅ Correct: Always at minimum log the error, even if you decide to continue execution.

```javascript
// Wrong — error vanishes silently, you'll never know this failed
try {
  riskyOperation();
} catch (err) {}

// Right
try {
  riskyOperation();
} catch (err) {
  console.error('riskyOperation failed:', err);
}
```

❌ Mistake 2: Using `try/catch` around a promise WITHOUT `await` — the `catch` never fires because the promise rejection happens asynchronously, after the `try` block has already finished executing.
✅ Correct: Either `await` the promise inside `try`, or chain `.catch()` directly on the promise.

```javascript
// Wrong — catch never runs; rejection becomes an unhandled rejection
try {
  somePromiseReturningFn();  // missing await!
} catch (err) {
  console.error(err);  // never reached
}

// Right
try {
  await somePromiseReturningFn();
} catch (err) {
  console.error(err);
}
```

❌ Mistake 3: Catching an error and re-throwing a NEW generic error, losing the original stack trace and context, making root-cause debugging harder.
✅ Correct: Either re-throw the original error, or attach it as a `cause`: `throw new Error('Order failed', { cause: err })`.

---

## 🧠 Tricky Interview Question

```javascript
async function risky() {
  try {
    throw new Error('inner error');
  } finally {
    return 'finally value';  // notice: return inside finally!
  }
}

risky().then(console.log).catch(console.error);
```
What is logged?
Answer:
```
finally value
```
**Explanation:** This is a famous JS gotcha — a `return` statement inside a `finally` block OVERRIDES any pending exception (or return value) from the `try`/`catch`. Even though `try` threw an error that would normally propagate and reject the promise, the `finally` block's explicit `return` SWALLOWS that error entirely and makes the function resolve successfully with `'finally value'` instead. This is considered bad practice precisely because it can silently hide real errors — interviewers use this to test whether you understand `finally`'s override behavior.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `throw` and `reject()`?
A1: `throw` is used in synchronous code (or inside an `async` function body) to signal an error — it immediately halts normal execution flow and is caught by the nearest `try/catch`. `reject()` is the Promise-specific way to signal failure when manually constructing a `new Promise((resolve, reject) => ...)`. Inside an `async` function, a `throw` automatically becomes a rejected promise — they're unified at that boundary.

Q2: Why doesn't `try/catch` catch errors from callback-based async functions?
A2: Because the callback executes LATER, asynchronously, after the `try` block has already finished running (the call stack for that `try` is gone by the time the callback fires). `try/catch` only catches synchronous throws (or `await`ed promise rejections) that happen WHILE that `try` block's code is actively executing. Callback-based errors must be handled via the error-first callback pattern (`if (err) {...}`), not `try/catch`.

Q3: What is `unhandledRejection` and why should you listen for it?
A3: It's a `process`-level event Node.js emits when a Promise rejects but nothing (`.catch()` or `try/catch`) ever handles that rejection. Listening to `process.on('unhandledRejection', handler)` lets you log/alert on these otherwise-silent failures. In modern Node.js, unhandled rejections can even crash the process by default (`--unhandled-rejections=strict`), so catching them matters for production stability.

Q4: How do custom Error classes (extending `Error`) help with error handling?
A4: They let you attach structured metadata (status codes, error codes, "is this retryable" flags, which field failed validation) directly to the error object, and let `catch` blocks use `instanceof` checks to handle different failure types differently — e.g., returning 400 for validation errors vs 502 for upstream gateway failures — instead of parsing error message strings.

Q5: What's the role of Express's 4-argument error-handling middleware?
A5: Express specifically recognizes middleware functions with the signature `(err, req, res, next)` as ERROR handlers, distinct from normal `(req, res, next)` middleware. Calling `next(err)` anywhere in the request chain skips all remaining normal middleware and jumps straight to the nearest matching error-handling middleware, centralizing error-to-HTTP-response translation in one place instead of duplicating it in every route.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Wrapping any operation that can throw synchronously or any `await`ed async operation
- Centralizing error-to-response translation in Express via error middleware
- Differentiating error types (validation vs system vs upstream) with custom Error classes

❌ Avoid when:
- Using `try/catch` around code with NO possibility of throwing — unnecessary overhead/noise
- Swallowing errors silently with an empty `catch` — always at least log
- Wrapping a non-awaited promise in `try/catch` expecting it to catch async rejections — it won't

---

## 📊 Visual Diagram
```
TRY/CATCH/FINALLY FLOW
──────────────────────────────────────────
try {
   statement 1       ──▶ runs
   statement 2 throws ──▶ remaining try code SKIPPED
   statement 3       ──▶ SKIPPED
} catch (err) {
   handle error       ──▶ runs (err = thrown value)
} finally {
   cleanup             ──▶ ALWAYS runs, error or not
}

ASYNC VERSION:
async function f() {
  try {
    await promiseThatRejects();  // throws here on reject
  } catch (err) {
    // caught, just like sync throw
  }
}
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| try/catch/finally | Structured error handling blocks | Structured error handling blocks |
| Custom Error class | Error subclass with extra context | Extra context वाला Error subclass |
| unhandledRejection | Event for uncaught promise rejections | Uncaught promise rejections का event |
| Error middleware | Express's centralized error handler | Express का centralized error handler |
| Retryable error | Error that's safe to retry | Retry करने लायक error |

---

## ⚡ 3-Line Summary
English:
1. `try/catch` catches synchronous throws and awaited promise rejections — never un-awaited promise rejections or callback errors.
2. Custom Error classes with `instanceof` checks let you route different failure types to different handling logic.
3. Centralize error-to-response translation using Express's 4-arg error middleware and always listen for `unhandledRejection`.

Hindi:
1. `try/catch` sync throws और awaited promise rejections catch करता है — un-awaited promises या callback errors नहीं।
2. Custom Error classes से `instanceof` check करके अलग-अलग error types अलग handle करो।
3. Express के 4-arg error middleware से centralize करो, `unhandledRejection` भी सुनो।

---

## ➡️ Next Topic
**200. Promise.all + Promise.allSettled** — Deep dive into composing multiple promises for parallel execution.
