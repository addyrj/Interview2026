# 60. util Module
# हिंदी में: util Module — Node.js की Utility Belt

---

## 🔵 Simple Definition (English)
The **`util`** module (`require('util')`) is Node's collection of general-purpose helper functions that don't fit elsewhere: `promisify()` (convert callback-style functions to return Promises), `inspect()` (pretty-print objects, what `console.log` uses internally), `format()` (printf-style string formatting), `types` (runtime type-checking helpers), and `deprecate()` (mark functions as deprecated with warnings).

## 🔵 सरल परिभाषा (Hindi)
**`util`** module Node की general-purpose helper functions का collection है जो कहीं और fit नहीं होते: `promisify()` (callback-style functions को Promise-returning बनाना), `inspect()` (objects को pretty-print करना, `console.log` अंदर से यही use करता है), `format()` (printf-style string formatting), `types` (runtime type-checking), और `deprecate()` (functions को deprecated mark करना, warning के साथ)।

---

## 🔴 Problem it Solves
Node's history spans callback-based APIs (pre-ES6, pre-async/await) through modern Promise-based ones — `util.promisify()` bridges this gap, letting developers use old callback-style APIs (`fs.readFile`, custom legacy functions) with modern `async/await` without manually rewriting them. Similarly, debugging complex nested objects via plain string concatenation is painful (`'Object: ' + obj` gives `'[object Object]'`) — `util.inspect()` solves this by recursively formatting objects, arrays, and circular references into readable output. `util` collects these recurring cross-cutting needs into one core module.

## 🔴 यह क्यों बना? (Hindi)
Node का history callback-based APIs (async/await से पहले) से modern Promise-based APIs तक फैला है — `util.promisify()` यह gap bridge करता है, पुराने callback-style APIs को modern `async/await` के साथ use करने देता है बिना manually rewrite किए। Complex nested objects को plain string concatenation से debug करना मुश्किल है (`'Object: ' + obj` देता है `'[object Object]'`) — `util.inspect()` recursively format करता है। `util` इन recurring needs को एक core module में collect करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → **`util.promisify(fn)`**: takes a function following Node's `(err, result) => {}` callback convention and returns a NEW function that returns a Promise instead — `const readFileAsync = util.promisify(fs.readFile); await readFileAsync(path)`.
Step 2 → **`util.callbackify(asyncFn)`**: the REVERSE — converts an `async` function back into a callback-style one, useful for integrating modern code with legacy callback-expecting APIs.
Step 3 → **`util.inspect(obj, options)`**: converts any value into a readable string representation, with options like `depth` (how deeply to recurse into nested objects), `colors` (ANSI colors for terminal output), and `showHidden` (include non-enumerable properties).
Step 4 → **`util.format(formatString, ...args)`**: printf-style formatting — `%s` (string), `%d` (number), `%j` (JSON), `%o`/`%O` (object inspection) placeholders.
Step 5 → **`util.types`**: runtime checks like `util.types.isPromise(val)`, `util.types.isAsyncFunction(fn)` — more reliable than `instanceof` for certain built-in types across different realms/contexts.
Step 6 → **`util.deprecate(fn, message)`**: wraps a function so calling it logs a deprecation warning once, helping developers migrate away from old APIs gracefully.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **`util.promisify(fn)`**: callback convention वाले function को Promise return करने वाला बनाता है।
Step 2 → **`util.callbackify(asyncFn)`**: उल्टा — async function को callback-style बनाता है।
Step 3 → **`util.inspect(obj, options)`**: किसी भी value को readable string में बदलता है, options: `depth`, `colors`, `showHidden`।
Step 4 → **`util.format()`**: printf-style formatting — `%s`, `%d`, `%j`, `%o`/`%O` placeholders।
Step 5 → **`util.types`**: runtime type checks, `instanceof` से ज़्यादा reliable।
Step 6 → **`util.deprecate(fn, message)`**: function को wrap करता है, call होने पर deprecation warning देता है।

---

## 🟡 Real World Example
**Amazon's legacy-to-modern codebase migration:** Amazon's internal order-processing system had years-old callback-based database functions (`db.query(sql, (err, rows) => {...})`). When the team modernized the codebase to use `async/await` throughout, instead of rewriting every single database call site, they used `util.promisify(db.query)` once to create an async-compatible wrapper — letting new code use clean `await db.queryAsync(sql)` syntax while the underlying legacy function remained unchanged, minimizing migration risk and effort.

## 🟡 Real Example Hindi mein
**Amazon का legacy-to-modern codebase migration:** Order-processing system में पुराने callback-based database functions थे। Codebase को `async/await` में modernize करते समय, हर call site rewrite करने के बजाय, `util.promisify(db.query)` एक बार use किया — नया code clean `await` syntax use कर सकता है, पुराना function बिना बदले रहा, migration risk कम हुआ।

---

## 💻 Code Example — Basic
```javascript
// util-basics.js
const util = require('util');
const fs = require('fs');

// 1. promisify() -- convert a callback-style function to return a Promise
const readFileAsync = util.promisify(fs.readFile);

async function readConfig() {
  const data = await readFileAsync('./package.json', 'utf8'); // clean async/await syntax
  console.log('File read via promisified function, length:', data.length);
}
readConfig();

// 2. util.inspect() -- deep, readable object formatting (what console.log uses internally)
const complexObject = {
  name: 'Rahul',
  nested: { address: { city: 'Delhi', pincode: '110001' } },
  items: [1, 2, 3],
};
console.log(util.inspect(complexObject, { depth: null, colors: true }));
// Shows the FULL nested structure, with colors in a terminal

// 3. util.format() -- printf-style string formatting
const message = util.format('User %s placed order #%d worth ₹%d', 'Priya', 12345, 2500);
console.log(message); // "User Priya placed order #12345 worth ₹2500"

// 4. util.types -- reliable runtime type checks
console.log(util.types.isPromise(Promise.resolve(1))); // true
console.log(util.types.isAsyncFunction(async () => {})); // true
console.log(util.types.isDate(new Date())); // true

// 5. util.deprecate() -- mark an old function as deprecated
const oldFunction = util.deprecate(
  () => console.log('Running old logic'),
  'oldFunction() is deprecated, use newFunction() instead'
);
oldFunction(); // logs the deprecation warning ONCE, then runs the function
oldFunction(); // warning NOT repeated on subsequent calls
```

## 💻 Code Example — Advanced
```javascript
// util-advanced.js -- production patterns
const util = require('util');

// ─── 1. PROMISIFYING A CUSTOM LEGACY CALLBACK FUNCTION ────────────────────────
function legacyDatabaseQuery(sql, callback) {
  // Simulates an old-style DB driver with (err, result) callback convention
  setTimeout(() => {
    if (sql.includes('DROP')) {
      callback(new Error('Dangerous query blocked'));
    } else {
      callback(null, [{ id: 1, name: 'Sample Row' }]);
    }
  }, 100);
}

const queryAsync = util.promisify(legacyDatabaseQuery);

async function runQuery() {
  try {
    const rows = await queryAsync('SELECT * FROM orders');
    console.log('Query result:', rows);
  } catch (err) {
    console.error('Query failed:', err.message);
  }
}
runQuery();

// ─── 2. CUSTOM PROMISIFY BEHAVIOR WITH util.promisify.custom ────────────────
// For functions with a non-standard callback signature (e.g., multiple return values)
function customApiCall(id, callback) {
  setTimeout(() => callback(null, { data: id }, { statusCode: 200 }), 50);
}
customApiCall[util.promisify.custom] = (id) => {
  return new Promise((resolve) => {
    customApiCall(id, (err, data, meta) => resolve({ data, meta })); // combine into one object
  });
};
const customApiCallAsync = util.promisify(customApiCall);

// ─── 3. DEEP OBJECT DEBUGGING WITH util.inspect() FOR LOGGING ────────────────
function logDebugInfo(label, obj) {
  console.log(`[DEBUG] ${label}:`, util.inspect(obj, {
    depth: 4,         // how many levels deep to recurse
    colors: false,    // disable colors for file-based logs
    maxArrayLength: 20, // limit array output size for huge arrays
    breakLength: 100, // line-wrap width
  }));
}

// ─── 4. CALLBACKIFY -- converting a modern async function for legacy consumers ─
async function modernFetchUser(id) {
  return { id, name: 'Fetched User' }; // simulated async operation
}
const fetchUserCallback = util.callbackify(modernFetchUser);

fetchUserCallback(42, (err, user) => {
  if (err) return console.error(err);
  console.log('Fetched via callback style:', user); // for legacy code expecting callbacks
});

module.exports = { queryAsync, customApiCallAsync, logDebugInfo, fetchUserCallback };
```

---

## 🟠 Express.js Integration
```javascript
const express = require('express');
const util = require('util');
const app = express();

// 1. PROMISIFYING LEGACY MIDDLEWARE/DRIVERS FOR USE IN ASYNC ROUTE HANDLERS
const legacyDbDriver = {
  findUser: (id, callback) => setTimeout(() => callback(null, { id, name: 'User' }), 50),
};
const findUserAsync = util.promisify(legacyDbDriver.findUser);

app.get('/users/:id', async (req, res) => {
  try {
    const user = await findUserAsync(req.params.id); // clean async syntax for a legacy driver
    res.json(user);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 2. STRUCTURED DEBUG LOGGING MIDDLEWARE USING util.inspect()
app.use((req, res, next) => {
  if (process.env.DEBUG) {
    console.log(util.format('[%s] %s %s', new Date().toISOString(), req.method, req.url));
    console.log(util.inspect({ headers: req.headers, body: req.body }, { depth: 2 }));
  }
  next();
});

// 3. MARKING A DEPRECATED ROUTE HANDLER WHILE KEEPING IT FUNCTIONAL
const oldSearchHandler = util.deprecate(
  (req, res) => res.json({ message: 'Old search endpoint (deprecated)' }),
  'GET /search is deprecated, use GET /v2/search instead'
);
app.get('/search', express.json(), oldSearchHandler);

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `util.promisify()` on a function that doesn't follow the `(err, result)` convention
```javascript
// Wrong -- promisify assumes the LAST argument is a callback shaped like (err, result)
function weirdApi(id, onSuccess, onError) { /* two separate callbacks, not (err, result) */ }
const promisified = util.promisify(weirdApi); // produces INCORRECT behavior

// Correct -- wrap manually with a real Promise when the signature doesn't match the convention
function weirdApiAsync(id) {
  return new Promise((resolve, reject) => {
    weirdApi(id, (result) => resolve(result), (err) => reject(err));
  });
}
```

❌ Mistake 2: Using `console.log(obj)` and being confused by `[Object]` truncation for deeply nested data
```javascript
// Wrong -- console.log has a default inspection depth (2), deeper levels show as [Object]
console.log(deeplyNestedObject); // "{ a: { b: { c: [Object] } } }" -- info lost!

// Correct -- use util.inspect() with depth: null to see everything
console.log(util.inspect(deeplyNestedObject, { depth: null }));
```

❌ Mistake 3: Relying on `typeof`/`instanceof` for checks that `util.types` handles more reliably
```javascript
// Wrong -- instanceof can fail across different "realms" (e.g., vm module contexts, some edge cases)
if (value instanceof Promise) { /* may fail for promises from a different context */ }

// Correct -- util.types provides more robust checks for built-in types
const util = require('util');
if (util.types.isPromise(value)) { /* works reliably across contexts */ }
```

---

## 🧠 Tricky Interview Question
```javascript
const util = require('util');

function myCallbackFn(a, b, callback) {
  setTimeout(() => callback(null, a + b), 10);
}

const myAsyncFn = util.promisify(myCallbackFn);

myAsyncFn(2, 3).then(console.log);
console.log('This line runs first or second?');
```
Answer: `'This line runs first or second?'` prints FIRST, then (after ~10ms) `5` prints. `util.promisify()` wraps the callback-style function, but the underlying function still executes ASYNCHRONOUSLY (via `setTimeout`) — calling `myAsyncFn(2, 3)` returns a PENDING Promise immediately and execution continues past it to the next synchronous line. The `.then(console.log)` callback only runs once the Promise resolves, which happens later on the event loop's timer phase. This demonstrates that `promisify()` changes the API SHAPE (callback → Promise) but doesn't change the underlying TIMING/behavior of the wrapped function — it's still asynchronous exactly as before, just exposed through a different interface.

---

## ⚫ Interview Questions + Answers

Q1: What does `util.promisify()` require of the function it wraps?
A1: The function must follow Node's standard "error-first callback" convention: the LAST parameter must be a callback function shaped as `(err, result) => {}`, where `err` is `null`/`undefined` on success. `promisify()` returns a new function that, when called (without the callback), returns a Promise that resolves with `result` or rejects with `err`. Functions with non-standard callback shapes (multiple result arguments, two separate success/error callbacks) need custom handling via `util.promisify.custom` or a manual Promise wrapper.

Q2: How does `util.inspect()` differ from `JSON.stringify()` for debugging objects?
A2: `util.inspect()` can represent values `JSON.stringify()` cannot handle well or at all — functions, `undefined`, `Symbol`, circular references (it detects and marks them as `[Circular]` instead of throwing), class instances with their constructor name shown, and `Map`/`Set` contents. `JSON.stringify()` throws on circular references, silently drops `undefined`/function values, and produces output meant for data interchange, not human debugging readability (though `console.log()` uses `util.inspect()`-like formatting internally, not JSON).

Q3: What's the practical use of `util.callbackify()`, and when would you need it?
A3: It converts a modern `async` function into one that accepts a traditional Node-style `(err, result)` callback as its last argument — the reverse of `promisify()`. Useful when you've written new code using `async/await` but need to pass that function into an OLDER API or library that expects a callback-style function (e.g., an older framework's plugin/hook system that hasn't been updated to support Promises).

Q4: Why would a library author use `util.deprecate()` instead of just removing an old function immediately?
A4: `util.deprecate()` allows a GRACEFUL migration path — existing consumers of the old function keep working (no breaking change), but they see a console warning informing them the function will eventually be removed/changed, giving them time to migrate to the new API at their own pace. Immediately removing a function would be a breaking change that could crash dependent applications without warning.

Q5: Give an example of a `util.types` check that's more reliable than a native JavaScript operator for the same purpose.
A5: `util.types.isAsyncFunction(fn)` reliably detects if a function was declared with the `async` keyword, something that's awkward to check natively (checking `fn.constructor.name === 'AsyncFunction'` works but is fragile/stringly-typed). Similarly, `util.types.isArrayBuffer(val)` or `util.types.isDate(val)` provide canonical, engine-level checks that work correctly even for values originating from different VM contexts/realms (e.g., objects passed across the `vm` module's sandboxes), where `instanceof` checks can incorrectly return `false` due to different global prototype chains.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Converting legacy callback-based APIs to Promise-based for use with `async/await` (`promisify`)
- Debugging complex nested objects in logs (`inspect`)
- Formatting log messages with placeholders (`format`)
- Gracefully deprecating old functions while maintaining backward compatibility (`deprecate`)

❌ Avoid when:
- The function you're promisifying doesn't follow the standard `(err, result)` callback shape — write a manual wrapper instead
- You need structured, machine-parseable serialization — use `JSON.stringify()`, not `util.inspect()`, for that purpose

---

## 📊 Visual Diagram
```
util.promisify() TRANSFORMATION:

  BEFORE (callback style):              AFTER (Promise style):
  fn(arg1, arg2, (err, result) => {})   const fnAsync = util.promisify(fn);
       │                                      │
       ▼                                      ▼
  Nested callbacks, harder to          await fnAsync(arg1, arg2)
  compose with async/await             Clean, composable with try/catch

util.inspect() vs JSON.stringify():

  Value: { fn: () => {}, circular: <self-reference>, date: new Date() }
       │                                    │
       ▼ util.inspect()                     ▼ JSON.stringify()
  "{ fn: [Function (anonymous)],       THROWS: "Converting circular
    circular: [Circular *1],            structure to JSON"
    date: 2024-01-01T00:00:00.000Z }"
  (readable, handles everything)       (fails on circular refs, drops functions)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| promisify() | Callback → Promise converter | Callback से Promise में convert |
| callbackify() | Promise/async → callback converter | Promise से callback में convert |
| inspect() | Deep, readable object formatting | Deep, readable object formatting |
| format() | printf-style string formatting | printf-style string formatting |
| types | Runtime type-checking helpers | Runtime type-checking helpers |
| deprecate() | Mark function deprecated with warning | Function को deprecated mark करना |

---

## ⚡ 3-Line Summary
English: `util` is Node's utility belt — `promisify()` bridges callback APIs to async/await, `inspect()` enables deep object debugging (used internally by `console.log`), and `types`/`format`/`deprecate` round out common cross-cutting helper needs. `promisify()` requires the standard `(err, result)` callback convention to work correctly.

Hindi: `util` Node की utility belt है — `promisify()` callback APIs को async/await से जोड़ता है, `inspect()` deep object debugging देता है (`console.log` अंदर से यही use करता है), `types`/`format`/`deprecate` बाकी common needs पूरी करते हैं। `promisify()` को standard `(err, result)` callback convention चाहिए।

---

## ➡️ Next Topic
**61. readline Module** — reading input line-by-line from streams, used for CLI tools, interactive prompts, and processing text files line-by-line.
