# 23. CommonJS (require/module.exports)
# हिंदी में: CommonJS — require/module.exports Module System

---

## 🔵 Simple Definition (English)
**CommonJS** is Node.js's original module system. It lets you split code into files (modules) and share code between them using `require()` to import and `module.exports` to export. Every `.js` file in Node is treated as its own module with its own scope — nothing leaks globally unless you explicitly export it.

## 🔵 सरल परिभाषा (Hindi)
**CommonJS** Node.js का original module system है। इससे code को files (modules) में split करके `require()` से import और `module.exports` से export किया जाता है। Node में हर `.js` file अपना खुद का module है, अपने scope के साथ — कुछ भी globally leak नहीं होता जब तक explicitly export न करो।

---

## 🔴 Problem it Solves
Before modules, all JavaScript in browsers ran in one global scope — variables from one file would clash with another file's variables (`var count` in `a.js` could overwrite `count` in `b.js`). As apps grew, this caused naming collisions and made code impossible to organize into reusable pieces. CommonJS (created for server-side JS, adopted by Node in 2009) solved this by wrapping every file in its own function scope, giving each file a private `require`, `module`, `exports`, `__filename`, `__dirname`. Code only becomes visible to other files when explicitly exported.

## 🔴 यह क्यों बना? (Hindi)
Modules से पहले, browser में सारा JavaScript एक global scope में चलता था — एक file का variable दूसरी file के variable से clash कर जाता था (`a.js` का `var count` `b.js` के `count` को overwrite कर सकता था)। App बड़ा होने पर naming collisions होने लगे और code को reusable pieces में organize करना मुश्किल हो गया। CommonJS (server-side JS के लिए बना, 2009 में Node ने अपनाया) ने हर file को अपने function scope में wrap करके यह solve किया — हर file को private `require`, `module`, `exports`, `__filename`, `__dirname` मिलते हैं। Code दूसरी files को तभी दिखता है जब explicitly export किया जाए।

---

## 🟢 How it Works — Step by Step

Step 1 → Node wraps every file's code inside a function: `(function(exports, require, module, __filename, __dirname) { ...your code... })`
Step 2 → `module.exports` is an empty object `{}` by default — you attach values/functions to it to make them public.
Step 3 → `require('./file')` reads the target file, runs it once, and returns whatever `module.exports` was set to.
Step 4 → Node **caches** the module after first `require()` — calling `require()` again returns the same cached object, the file doesn't re-run.
Step 5 → `require()` resolution: relative paths (`./`, `../`) → local files; bare names (`express`) → looks in `node_modules` up the directory tree; core modules (`fs`, `path`) → built-in, no lookup needed.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Node हर file के code को function में wrap कर देता है: `(function(exports, require, module, __filename, __dirname) { ...code... })`
Step 2 → `module.exports` default रूप से empty object `{}` होता है — values/functions इसमें attach करके public बनाओ।
Step 3 → `require('./file')` target file को read करता है, एक बार run करता है, और जो भी `module.exports` में था वो return करता है।
Step 4 → Node module को पहली बार `require()` के बाद **cache** कर लेता है — दोबारा `require()` करने पर same cached object मिलता है, file फिर से run नहीं होती।
Step 5 → Resolution: relative paths (`./`, `../`) → local files; bare names (`express`) → `node_modules` में ऊपर तक search; core modules (`fs`, `path`) → built-in, कोई lookup नहीं।

---

## 🟡 Real World Example
**Swiggy's backend codebase:** The order service has `orderCalculator.js` which exports functions like `calculateTotal`, `applyDiscount`, `calculateDeliveryFee`. The main `orderController.js` does `const { calculateTotal, applyDiscount } = require('./orderCalculator')` to use them, without duplicating pricing logic across controllers. Config values live in `config.js` with `module.exports = { dbUrl, razorpayKey, maxRetries }`, required wherever needed — change once, reflects everywhere thanks to module caching (same object reference).

## 🟡 Real Example Hindi mein
**Swiggy का backend codebase:** Order service में `orderCalculator.js` है जो `calculateTotal`, `applyDiscount`, `calculateDeliveryFee` जैसे functions export करता है। Main `orderController.js` में `const { calculateTotal, applyDiscount } = require('./orderCalculator')` से इन्हें use किया जाता है, बिना pricing logic को हर controller में duplicate किए। Config values `config.js` में रहते हैं `module.exports = { dbUrl, razorpayKey, maxRetries }` — जहाँ भी ज़रूरत हो वहाँ require करो, एक जगह बदलो, module caching की वजह से हर जगह reflect होता है (same object reference)।

---

## 💻 Code Example — Basic

```javascript
// mathUtils.js — a module that exports multiple functions
function add(a, b) {
  return a + b; // simple addition
}

function multiply(a, b) {
  return a * b; // simple multiplication
}

// Attach functions to module.exports to make them public
module.exports = { add, multiply };

// -------------------------------------------------------

// app.js — consumes the module
const { add, multiply } = require('./mathUtils'); // destructure named exports

console.log(add(2, 3));      // 5
console.log(multiply(4, 5)); // 20

// Each file is its own module — "add" and "multiply" don't exist
// in app.js's scope unless destructured from the required object.
```

## 💻 Code Example — Advanced

```javascript
// logger.js — demonstrates module caching + singleton pattern
let logCount = 0; // private state, not exported directly

function log(message) {
  logCount++;
  console.log(`[LOG #${logCount}] ${message}`);
}

function getLogCount() {
  return logCount; // controlled read-only access to private state
}

module.exports = { log, getLogCount };

// -------------------------------------------------------

// serviceA.js
const logger = require('./logger');
logger.log('Service A started');

// -------------------------------------------------------

// serviceB.js
const logger = require('./logger'); // SAME cached instance as serviceA.js
logger.log('Service B started');
console.log(logger.getLogCount()); // 2 — shared state proves single cached module

// -------------------------------------------------------

// exports vs module.exports — the real gotcha
// "exports" is just a reference to "module.exports" initially.
// Reassigning "exports" breaks the link; mutating it keeps the link.

// WRONG pattern (common bug):
exports = { foo: 'bar' }; // breaks the link — require() still gets old module.exports {}

// RIGHT pattern:
exports.foo = 'bar'; // mutates the same object module.exports points to — works
// OR always reassign module.exports directly:
module.exports = { foo: 'bar' }; // always safe
```

---

## 🟠 Express.js Integration

```javascript
// routes/userRoutes.js — CommonJS module exporting an Express Router
const express = require('express');
const router = express.Router(); // create a mini router instance
const userController = require('../controllers/userController'); // require sibling module

router.get('/users', userController.getAllUsers);   // GET /users
router.post('/users', userController.createUser);   // POST /users

module.exports = router; // export the configured router object

// -------------------------------------------------------

// app.js — main entry file wires everything together
const express = require('express');
const userRoutes = require('./routes/userRoutes'); // require the router module

const app = express();
app.use(express.json());
app.use('/api', userRoutes); // mount router under /api prefix

app.listen(3000, () => console.log('Server running on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Reassigning `exports` instead of `module.exports`
```javascript
// Wrong — breaks the reference, require() gets {} not { foo }
exports = { foo: 'bar' };

// Right — directly set module.exports
module.exports = { foo: 'bar' };
```

❌ Mistake 2: Forgetting `require()` caches — mutating state unexpectedly shared across files
```javascript
// Wrong — assuming require() gives a fresh copy every time
const config = require('./config');
config.apiKey = 'temp-override'; // mutates the CACHED object — affects every other file requiring config.js!

// Right — don't mutate shared module state; clone if you need a local copy
const config = { ...require('./config') }; // shallow copy, safe to mutate locally
```

---

## 🧠 Tricky Interview Question

```javascript
// counter.js
let count = 0;
module.exports = {
  increment: () => ++count,
  getCount: () => count,
};

// main.js
const counterA = require('./counter');
const counterB = require('./counter');

counterA.increment();
counterA.increment();
console.log(counterB.getCount()); // ?
```
Answer: **`2`**. Because Node **caches** modules by resolved file path — `require('./counter')` in `counterA` and `counterB` both return the exact same cached object (same `count` closure). There's only one `counter.js` instance running in the whole process, so mutations through `counterA` are visible through `counterB`. This is the basis of Node's "singleton module" pattern.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `exports` and `module.exports`?
A1: `exports` is a variable that initially points to the same object as `module.exports`. `require()` always returns `module.exports`, not `exports`. If you do `exports.foo = 1`, it mutates the shared object — visible via require. But if you do `exports = { foo: 1 }`, you rebind the local `exports` variable to a NEW object, while `module.exports` still points to the old one — so `require()` won't see `foo`. Safe rule: always assign to `module.exports` directly, use `exports.x =` only for adding properties.

Q2: Is `require()` synchronous or asynchronous?
A2: Synchronous. `require()` blocks execution until the target file is fully read, compiled, and executed. This is why CommonJS is well suited to server-side Node (file reads are fast, local disk) but considered problematic for browsers (network loads would block the UI) — which is one reason ES Modules support async loading (`import()`).

Q3: What does Node do on the first vs. second `require()` call for the same file?
A3: First call: Node resolves the path, reads the file, wraps it in the module function, executes it top-to-bottom, and stores the resulting `module.exports` in `require.cache` keyed by absolute file path. Second call (anywhere in the app): Node checks the cache, finds the entry, and returns the cached `module.exports` immediately — the file's code does NOT run again. This is why top-level `console.log` in a module only prints once no matter how many files require it.

Q4: How does Node resolve `require('lodash')` vs `require('./utils')`?
A4: For bare names (no `./`, `../`, `/`), Node looks for a `node_modules` folder in the current directory, then walks up parent directories until found (or throws `MODULE_NOT_FOUND`) — checking `package.json` "main" field or `index.js`. For relative/absolute paths, Node resolves directly against the current file's directory, trying exact file, then `.js`/`.json`/`.node` extensions, then `index.js` if it's a directory. Core modules (`fs`, `path`, `http`) are checked first and bypass file-system lookup entirely.

Q5: Can you clear the require cache? Why would you?
A5: Yes — `delete require.cache[require.resolve('./file')]` removes the cached entry, so the next `require()` re-executes the file fresh. Used in hot-reloading dev tools (like `nodemon` doesn't need this since it restarts the process, but custom plugin systems or CLI tools that reload config files at runtime do). Caution: stale references held by other modules won't automatically update — only new `require()` calls get the fresh module.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Writing plain Node.js scripts/CLIs/servers without a bundler (default `.js` files, no `"type": "module"` in `package.json`).
- Working in an existing CommonJS codebase (most legacy Node apps, many npm packages still ship CJS).
- You need `require()`'s synchronous, conditional-loading flexibility (e.g., `if (env) require('./devTools')`).

❌ Avoid when:
- Building for modern ESM-first tooling (Next.js, Vite, newer frameworks) — use ES Modules (`import`/`export`) instead.
- You need top-level `await`, which CommonJS modules cannot use directly (ESM supports it natively).
- Publishing a package meant to tree-shake well in bundlers — ESM's static analysis enables better dead-code elimination.

---

## 📊 Visual Diagram
```
COMMONJS MODULE WRAPPING:
──────────────────────────────────────────────────────────
  your file.js:
    const x = 5;
    module.exports = { x };

  Node wraps it as:
    (function(exports, require, module, __filename, __dirname) {
       const x = 5;
       module.exports = { x };
    })(module.exports, require, module, __filename, __dirname);

REQUIRE CACHE FLOW:
  require('./counter')  ──┐
                           ├──► checked against require.cache
  require('./counter')  ──┘         │
                                     ▼
                        found? ──Yes──► return cached module.exports
                             │
                             No
                             ▼
                 read file → wrap → execute → cache → return
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CommonJS | Node's module system (require/exports) | Node का module system |
| require() | Import a module (sync) | Module import करना |
| module.exports | Object to export from a file | Export करने वाला object |
| exports | Shortcut reference to module.exports | module.exports का reference |
| require.cache | Stores already-loaded modules | Loaded modules की cache |
| Module scope | Each file has its own private scope | हर file का अपना scope |
| __dirname | Absolute path of current file's folder | Current folder का path |

---

## ⚡ 3-Line Summary
English: CommonJS is Node's module system using `require()` to import and `module.exports` to export, giving every file its own private scope. Node caches modules after first `require()`, so the same file never re-executes and shared state persists across requires. Always assign to `module.exports` (not bare `exports =`) to avoid the classic reference-breaking bug.
Hindi: CommonJS Node का module system है — `require()` import के लिए, `module.exports` export के लिए, हर file का अपना private scope। Node पहली बार `require()` के बाद module को cache कर लेता है, इसलिए file दोबारा run नहीं होती और shared state बनी रहती है। हमेशा `module.exports` को assign करो (bare `exports =` नहीं) ताकि classic reference-breaking bug से बचा जा सके।

---

## ➡️ Next Topic
**24. ES Modules (import/export) in Node** — Node's modern, standard JavaScript module system, how it differs from CommonJS, and how to enable it.
