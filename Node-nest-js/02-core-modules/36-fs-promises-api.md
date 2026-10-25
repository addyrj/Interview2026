# 36. fs Promises API
# हिंदी में: fs Promises API — Modern Async File Operations

---

## 🔵 Simple Definition (English)
The **fs Promises API** (`require('fs/promises')` or `require('fs').promises`) is a version of every `fs` method that returns a **Promise** instead of taking a callback, enabling clean `async`/`await` syntax for file operations instead of nested callbacks.

## 🔵 सरल परिभाषा (Hindi)
**fs Promises API** (`require('fs/promises')` या `require('fs').promises`) हर `fs` method का वो version है जो callback लेने की जगह एक **Promise** return करता है, file operations के लिए nested callbacks की जगह clean `async`/`await` syntax enable करता है।

---

## 🔴 Problem it Solves
Classic callback-based `fs` code (`fs.readFile(a, (err, data) => { fs.readFile(b, (err2, data2) => { ... }) })`) leads to deeply nested "callback hell" when multiple file operations depend on each other sequentially, and error handling is scattered across many separate `if (err)` checks. Promises flatten this into sequential, readable `await` statements with a single `try/catch` for all errors — matching how the rest of modern async JavaScript (fetch, database drivers) is written.

## 🔴 यह क्यों बना? (Hindi)
Classic callback-based `fs` code (`fs.readFile(a, (err, data) => { fs.readFile(b, (err2, data2) => { ... }) })`) जब कई file operations एक दूसरे पर sequentially depend करते हैं तो deeply nested "callback hell" बन जाता है, और error handling कई अलग `if (err)` checks में बंट जाती है। Promises इसे sequential, readable `await` statements में flatten कर देते हैं एक single `try/catch` के साथ सभी errors के लिए — matching करता है कि modern async JavaScript (fetch, database drivers) कैसे लिखा जाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Import: `const fs = require('fs/promises')` (Node 14+, cleanest) or `const fs = require('fs').promises` (older style, still works).
Step 2 → Every method mirrors the callback version's name but drops the callback parameter and returns a Promise: `fs.readFile(path, encoding)` resolves with data, or rejects with an error.
Step 3 → Use with `await` inside an `async function`, or with `.then()/.catch()` directly.
Step 4 → Errors propagate as REJECTED promises — catch them with `try/catch` (when using `await`) or `.catch()` — same `err.code` values (`ENOENT`, `EACCES`, etc.) as the callback API.
Step 5 → Sequential operations read naturally top-to-bottom with `await`; independent operations can run concurrently with `Promise.all([...])` for better performance than awaiting each one individually.
Step 6 → `fs.promises` wraps the SAME underlying libuv thread-pool mechanics as the callback API — it's purely a different ergonomic layer over the exact same non-blocking I/O, not a performance difference.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Import करो: `const fs = require('fs/promises')` (Node 14+, सबसे clean) या `const fs = require('fs').promises` (older style, अभी भी काम करता है)।
Step 2 → हर method callback version के नाम जैसा ही है पर callback parameter हटाकर Promise return करता है: `fs.readFile(path, encoding)` data के साथ resolve होता है, या error के साथ reject होता है।
Step 3 → `async function` के अंदर `await` के साथ use करो, या directly `.then()/.catch()` के साथ।
Step 4 → Errors REJECTED promises की तरह propagate होते हैं — `try/catch` (जब `await` use कर रहे हो) या `.catch()` से catch करो — callback API जैसे ही `err.code` values (`ENOENT`, `EACCES`, etc.)।
Step 5 → Sequential operations `await` के साथ naturally top-to-bottom पढ़े जाते हैं; independent operations `Promise.all([...])` से concurrently चल सकते हैं हर एक को individually await करने से बेहतर performance के लिए।
Step 6 → `fs.promises` SAME underlying libuv thread-pool mechanics को wrap करता है जो callback API करता है — यह purely एक अलग ergonomic layer है same non-blocking I/O पर, कोई performance difference नहीं।

---

## 🟡 Real World Example
**Razorpay's settlement report generator:** The service reads multiple merchant transaction JSON files, merges them, calculates settlement totals, and writes a consolidated report — all expressed as a clean sequence of `await fs.readFile(...)`, processing, then `await fs.writeFile(...)`, wrapped in one `try/catch` for comprehensive error handling. The equivalent callback-based version would have required 3-4 levels of nested callbacks with duplicated error-handling code at each level.

## 🟡 Real Example Hindi mein
**Razorpay का settlement report generator:** Service कई merchant transaction JSON files पढ़ती है, merge करती है, settlement totals calculate करती है, और एक consolidated report लिखती है — सब कुछ `await fs.readFile(...)`, processing, फिर `await fs.writeFile(...)` की clean sequence की तरह, एक `try/catch` में comprehensive error handling के साथ। Equivalent callback-based version में 3-4 levels की nested callbacks चाहिए होतीं हर level पर duplicated error-handling code के साथ।

---

## 💻 Code Example — Basic

```javascript
// fsPromisesBasics.js
const fs = require('fs/promises'); // modern, recommended import path

async function main() {
  // Write a file — returns a Promise, awaited for completion
  await fs.writeFile('./data.json', JSON.stringify({ count: 1 }));

  // Read it back
  const raw = await fs.readFile('./data.json', 'utf8');
  const parsed = JSON.parse(raw);
  console.log('Parsed:', parsed); // { count: 1 }

  // Update and rewrite — sequential, readable steps
  parsed.count += 1;
  await fs.writeFile('./data.json', JSON.stringify(parsed));

  const updated = JSON.parse(await fs.readFile('./data.json', 'utf8'));
  console.log('Updated:', updated); // { count: 2 }
}

main().catch((err) => console.error('Something went wrong:', err));
```

## 💻 Code Example — Advanced

```javascript
// fsPromisesAdvanced.js — comparing callback hell vs Promise-based clarity
const fsCallback = require('fs');
const fs = require('fs/promises');

// ─── OLD STYLE: callback hell for 3 sequential file reads ──────────────────
function loadConfigOldStyle(callback) {
  fsCallback.readFile('./base.json', 'utf8', (err, base) => {
    if (err) return callback(err);
    fsCallback.readFile('./overrides.json', 'utf8', (err2, overrides) => {
      if (err2) return callback(err2);
      fsCallback.readFile('./secrets.json', 'utf8', (err3, secrets) => {
        if (err3) return callback(err3);
        const merged = { ...JSON.parse(base), ...JSON.parse(overrides), ...JSON.parse(secrets) };
        callback(null, merged);
      });
    });
  });
}

// ─── NEW STYLE: clean, flat async/await ─────────────────────────────────────
async function loadConfigModern() {
  const base = JSON.parse(await fs.readFile('./base.json', 'utf8'));
  const overrides = JSON.parse(await fs.readFile('./overrides.json', 'utf8'));
  const secrets = JSON.parse(await fs.readFile('./secrets.json', 'utf8'));
  return { ...base, ...overrides, ...secrets };
}

// ─── EVEN BETTER: parallel reads since they're independent of each other ───
async function loadConfigParallel() {
  const [baseRaw, overridesRaw, secretsRaw] = await Promise.all([
    fs.readFile('./base.json', 'utf8'),
    fs.readFile('./overrides.json', 'utf8'),
    fs.readFile('./secrets.json', 'utf8'),
  ]); // all three reads happen CONCURRENTLY, not one after another

  return {
    ...JSON.parse(baseRaw),
    ...JSON.parse(overridesRaw),
    ...JSON.parse(secretsRaw),
  };
}

// ─── Error handling: single try/catch covers the ENTIRE chain ──────────────
async function safeLoadConfig() {
  try {
    return await loadConfigParallel();
  } catch (err) {
    if (err.code === 'ENOENT') {
      console.warn('One of the config files is missing, using defaults');
      return {};
    }
    throw err; // unexpected error, propagate up
  }
}

(async () => {
  const config = await safeLoadConfig();
  console.log('Final config:', config);
})();
```

---

## 🟠 Express.js Integration

```javascript
// server.js — Express routes using fs/promises for clean async file handling
const express = require('express');
const fs = require('fs/promises');
const path = require('path');

const app = express();
app.use(express.json());

app.get('/invoice/:orderId', async (req, res) => {
  const invoicePath = path.join(__dirname, 'invoices', `${req.params.orderId}.pdf`);

  try {
    const pdfBuffer = await fs.readFile(invoicePath); // no encoding = returns raw Buffer
    res.type('application/pdf').send(pdfBuffer);
  } catch (err) {
    if (err.code === 'ENOENT') {
      return res.status(404).json({ error: 'Invoice not found' });
    }
    res.status(500).json({ error: 'Failed to retrieve invoice' });
  }
});

app.post('/reports/merge', async (req, res) => {
  const { reportIds } = req.body; // array of report IDs to merge

  try {
    // Read all requested report files IN PARALLEL for better performance
    const contents = await Promise.all(
      reportIds.map((id) => fs.readFile(path.join(__dirname, 'reports', `${id}.json`), 'utf8'))
    );
    const merged = contents.map((c) => JSON.parse(c)).flat();
    res.json({ merged });
  } catch (err) {
    res.status(500).json({ error: 'Failed to merge reports' });
  }
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mixing callback-style `fs` and `fs/promises` inconsistently
```javascript
// Wrong — mixing styles in the same function is confusing and error-prone
const fsCb = require('fs');
const fsP = require('fs/promises');

async function loadData() {
  fsCb.readFile('./a.txt', (err, data) => { // callback style — doesn't integrate with await!
    console.log(data); // this runs OUT OF ORDER relative to the rest of the async function
  });
  const b = await fsP.readFile('./b.txt', 'utf8'); // Promise style
}

// Right — pick ONE style consistently per module/function
const fs = require('fs/promises');
async function loadData() {
  const a = await fs.readFile('./a.txt', 'utf8');
  const b = await fs.readFile('./b.txt', 'utf8');
}
```

❌ Mistake 2: Sequentially `await`-ing independent operations that could run in parallel
```javascript
// Wrong — unnecessarily slow, each await blocks the next from starting
const a = await fs.readFile('./a.txt', 'utf8'); // waits fully before starting b
const b = await fs.readFile('./b.txt', 'utf8'); // waits fully before starting c
const c = await fs.readFile('./c.txt', 'utf8');

// Right — run independent reads concurrently with Promise.all
const [a, b, c] = await Promise.all([
  fs.readFile('./a.txt', 'utf8'),
  fs.readFile('./b.txt', 'utf8'),
  fs.readFile('./c.txt', 'utf8'),
]); // total time ≈ the SLOWEST single read, not the sum of all three
```

---

## 🧠 Tricky Interview Question

```javascript
const fs = require('fs/promises');

async function run() {
  try {
    await fs.readFile('./does-not-exist.txt', 'utf8');
  } catch (err) {
    console.log('Caught:', err.code);
  }
  console.log('Continuing after error...');
}
run();
```
Answer: Prints **`"Caught: ENOENT"`** then **`"Continuing after error..."`**. Unlike the callback API (where an error is just the first argument to the callback and doesn't stop execution automatically), a rejected Promise from `await` THROWS inside the `async function` — meaning it's caught by a surrounding `try/catch` just like a synchronous error would be, and execution continues normally AFTER the catch block, rather than crashing the whole process. This demonstrates why Promise-based fs is often preferred: error handling unifies with standard JS `try/catch` semantics instead of a separate callback-first-argument convention.

---

## ⚫ Interview Questions + Answers

Q1: Is `fs.promises` faster than the callback-based `fs` API?
A1: No — they're both built on the EXACT same underlying libuv thread-pool mechanism for non-blocking I/O. `fs.promises` is purely a different ERGONOMIC layer (returns Promises instead of accepting callbacks) over identical performance characteristics. The benefit is code READABILITY and error-handling consistency (via `try/catch` and `async/await`), not raw speed.

Q2: How do you import the Promise-based fs API?
A2: Two equivalent ways: `const fs = require('fs/promises')` (dedicated submodule path, cleanest, recommended for new code) or `const fs = require('fs').promises` (accessing the `.promises` property on the main `fs` module, older but still fully supported). Both give access to the same set of Promise-returning methods.

Q3: Why would you use `Promise.all()` with `fs.promises` methods instead of sequential `await` calls?
A3: When multiple file operations are INDEPENDENT of each other (don't need each other's results to proceed), awaiting them one-by-one in sequence wastes time — each `await` fully blocks before the next operation even starts, even though they could run concurrently. `Promise.all([op1, op2, op3])` dispatches all three to the thread pool AT ONCE, and the total wait time becomes roughly the duration of the SLOWEST operation rather than the SUM of all operations — a significant performance improvement for I/O-heavy code.

Q4: How does error handling differ between callback-based `fs.readFile` and `fs.promises.readFile`?
A4: Callback-based: errors arrive as the FIRST argument to the callback (`(err, data) => {...}`), requiring an explicit `if (err) { ... }` check in every single callback. Promise-based: errors REJECT the returned Promise, which either triggers a surrounding `try/catch` block (with `await`) or a chained `.catch()` handler — this integrates naturally with standard JavaScript error-handling patterns and allows ONE `try/catch` to cover MULTIPLE sequential operations instead of needing a separate check at every nested callback level.

Q5: Can you still access the original callback-based API if you've imported `fs/promises`?
A5: Not from the SAME import — `require('fs/promises')` only exposes the Promise-based methods. To use BOTH styles in the same file, you'd need two separate requires: `const fs = require('fs')` (callback/sync methods) and `const fsPromises = require('fs/promises')` (Promise methods), using whichever variable matches the style you need in context. Mixing both unnecessarily in the same logical operation is discouraged (see Common Mistakes above) for code clarity.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Writing any new async file-handling code — it's the modern, recommended default.
- Sequencing multiple dependent file operations cleanly with `async/await`.
- Combining with `Promise.all()` for concurrent independent file operations.

❌ Avoid when:
- You're in a hot, performance-critical streaming scenario better served by actual Streams (`fs.createReadStream`) rather than loading whole files via `readFile`.
- Working in an older, pure-callback-style codebase where introducing Promises inconsistently would create confusing mixed patterns — consider a full, deliberate migration instead of partial mixing.

---

## 📊 Visual Diagram
```
CALLBACK HELL vs PROMISE/ASYNC FLATTENING:
──────────────────────────────────────────────────────────

  CALLBACK STYLE (nested, hard to read):
    readFile(a, (err, data) => {
      readFile(b, (err2, data2) => {
        readFile(c, (err3, data3) => {
          // deeply nested, error handling repeated 3x
        });
      });
    });

  PROMISE/ASYNC STYLE (flat, sequential):
    const data  = await readFile(a);
    const data2 = await readFile(b);
    const data3 = await readFile(c);
    // ONE try/catch covers all three

  PARALLELIZED (fastest, independent ops):
    const [data, data2, data3] = await Promise.all([
      readFile(a), readFile(b), readFile(c)
    ]);
    // total time ≈ slowest single read, not the sum
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| fs/promises | Promise-based fs API | Promise-based fs API |
| async/await | Syntax for working with Promises | Promises के साथ काम करने का syntax |
| Promise.all() | Run multiple Promises concurrently | कई Promises को concurrently चलाना |
| Callback hell | Deeply nested callback code | गहराई से nested callback code |
| try/catch | Unified error handling for awaited code | Awaited code के लिए unified error handling |
| Rejected Promise | Promise that failed/errored | Fail/error हुआ Promise |

---

## ⚡ 3-Line Summary
English: `fs/promises` provides the same `fs` operations but returning Promises instead of callbacks, enabling clean `async/await` syntax and unified `try/catch` error handling instead of nested callback hell. It has identical performance to the callback API (same libuv thread pool underneath) — the benefit is purely code clarity and maintainability. Use `Promise.all()` to run independent file operations concurrently rather than sequentially awaiting each one.
Hindi: `fs/promises` वही `fs` operations देता है पर callbacks की जगह Promises return करता है, nested callback hell की जगह clean `async/await` syntax और unified `try/catch` error handling enable करता है। Performance callback API जैसी ही है (नीचे same libuv thread pool) — फायदा purely code clarity और maintainability है। Independent file operations को sequentially await करने की जगह `Promise.all()` से concurrently चलाओ।

---

## ➡️ Next Topic
**37. path Module — Complete Guide** — cross-platform path manipulation utilities every Node app needs.
