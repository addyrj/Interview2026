# 25. CommonJS vs ES Modules in Node
# हिंदी में: CommonJS vs ES Modules — तुलना और Migration

---

## 🔵 Simple Definition (English)
**CommonJS (CJS)** and **ES Modules (ESM)** are Node's two module systems. CJS uses `require()`/`module.exports`, loads synchronously, and has been Node's default since 2009. ESM uses `import`/`export`, loads asynchronously, is the official JavaScript standard, and is Node's forward-looking direction since v12+.

## 🔵 सरल परिभाषा (Hindi)
**CommonJS (CJS)** और **ES Modules (ESM)** Node के दो module systems हैं। CJS `require()`/`module.exports` use करता है, synchronously load होता है, और 2009 से Node का default रहा है। ESM `import`/`export` use करता है, asynchronously load होता है, official JavaScript standard है, और v12+ से Node की आगे की direction है।

---

## 🔴 Problem it Solves
Node started with CJS because no standard existed when Node launched (2009). By the time ES2015 standardized `import`/`export`, millions of CJS packages already existed on npm. Node couldn't abandon CJS overnight, so it had to support BOTH systems simultaneously, with careful interop rules — this created a real, common interview and real-world problem: "which system am I in, and how do I bridge them?" Understanding the differences (sync vs async loading, live bindings vs copied exports, extension requirements) is essential for migrating codebases, debugging `ERR_REQUIRE_ESM` errors, and writing dual-format npm packages.

## 🔴 यह क्यों बना? (Hindi)
Node ने CJS से शुरुआत की क्योंकि जब Node launch हुआ (2009) तब कोई standard नहीं था। जब तक ES2015 ने `import`/`export` standardize किया, npm पर लाखों CJS packages बन चुके थे। Node रातोंरात CJS छोड़ नहीं सकता था, इसलिए दोनों systems को साथ support करना पड़ा, careful interop rules के साथ — इससे एक real, common interview और real-world problem बनी: "मैं किस system में हूँ, और इन्हें कैसे bridge करूँ?" Differences समझना (sync vs async loading, live bindings vs copied exports, extension requirements) codebases migrate करने, `ERR_REQUIRE_ESM` errors debug करने, और dual-format npm packages लिखने के लिए ज़रूरी है।

---

## 🟢 How it Works — Step by Step

Step 1 → Node determines module type per-file: `.mjs` → always ESM; `.cjs` → always CJS; `.js` → depends on nearest `package.json`'s `"type"` field (`"module"` = ESM, `"commonjs"` or absent = CJS).
Step 2 → CJS: `require()` is synchronous, can be called conditionally/inside `if` blocks, inside functions, anywhere.
Step 3 → ESM: `import` statements must be top-level (not inside `if`/functions) and are hoisted — but `import()` (dynamic, function-like) CAN be used anywhere and returns a Promise.
Step 4 → CJS gives copied exports (values at time of destructure); ESM gives live bindings (always current value).
Step 5 → Interop: ESM can `import` CJS packages (Node wraps CJS module.exports as the default export). CJS CANNOT `require()` ESM — must use `await import()`.
Step 6 → `__dirname`/`__filename` exist natively in CJS but NOT in ESM — ESM uses `import.meta.url` instead, converted via `fileURLToPath`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Node हर file के लिए module type decide करता है: `.mjs` → हमेशा ESM; `.cjs` → हमेशा CJS; `.js` → nearest `package.json` के `"type"` field पर depend (`"module"` = ESM, `"commonjs"` या absent = CJS)।
Step 2 → CJS: `require()` synchronous है, `if` blocks के अंदर, functions के अंदर, कहीं भी conditionally call हो सकता है।
Step 3 → ESM: `import` statements top-level होने चाहिए (`if`/functions के अंदर नहीं) और hoisted होते हैं — लेकिन `import()` (dynamic, function-like) कहीं भी use हो सकता है, Promise return करता है।
Step 4 → CJS copied exports देता है (destructure के समय का value); ESM live bindings देता है (हमेशा current value)।
Step 5 → Interop: ESM CJS packages को `import` कर सकता है (Node CJS के module.exports को default export की तरह wrap करता है)। CJS ESM को `require()` नहीं कर सकता — `await import()` use करना पड़ता है।
Step 6 → `__dirname`/`__filename` CJS में natively मौजूद हैं पर ESM में नहीं — ESM `import.meta.url` use करता है, `fileURLToPath` से convert करके।

---

## 🟡 Real World Example
**Flipkart's checkout microservice migration:** The team had a 5-year-old CJS codebase. To adopt newer tooling that required ESM (modern test runners, certain cloud SDKs shipping ESM-only), they migrated incrementally — renamed new feature files to `.mjs`, kept legacy files as `.cjs`, and used `createRequire()` in ESM files to still pull in a few CJS-only internal packages during the transition, avoiding a risky big-bang rewrite.

## 🟡 Real Example Hindi mein
**Flipkart का checkout microservice migration:** Team का 5 साल पुराना CJS codebase था। Newer tooling अपनाने के लिए जिसे ESM चाहिए था (modern test runners, कुछ cloud SDKs जो ESM-only ship करते हैं), उन्होंने incrementally migrate किया — नए feature files को `.mjs` नाम दिया, legacy files `.cjs` रहने दी, और ESM files में `createRequire()` use करके transition के दौरान कुछ CJS-only internal packages अभी भी pull किए, risky big-bang rewrite से बचते हुए।

---

## 💻 Code Example — Basic

```javascript
// ===== CommonJS style (greet.cjs) =====
function greet(name) {
  return `Hello, ${name}!`; // simple greeting function
}
module.exports = { greet }; // CJS export

// consumer.cjs
const { greet } = require('./greet.cjs'); // sync require
console.log(greet('Zomato')); // "Hello, Zomato!"

// ===== ES Module style (greet.mjs) =====
export function greetESM(name) {
  return `Hi, ${name}!`; // same logic, ESM export
}

// consumer.mjs
import { greetESM } from './greet.mjs'; // static import, extension required
console.log(greetESM('Swiggy')); // "Hi, Swiggy!"
```

## 💻 Code Example — Advanced

```javascript
// interop.mjs — demonstrates ESM importing CJS, and the __dirname replacement

import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';

// ESM has no __dirname/__filename — recreate them manually:
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
console.log('Current dir:', __dirname);

// ESM importing a CJS package works fine (Node interop handles it):
import lodash from 'lodash'; // lodash ships CJS; Node wraps module.exports as default
console.log(lodash.chunk([1, 2, 3, 4], 2)); // [[1,2],[3,4]]

// Using a CJS-only internal module that has no ESM build:
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url); // recreate require() in ESM scope
const legacyHelper = require('./legacyHelper.cjs'); // now require() works here
console.log(legacyHelper.doSomething());

// -------------------------------------------------------

// bridge.cjs — CJS consuming an ESM-only module (dynamic import, async-only)
async function loadAndUse() {
  // require('./esmOnly.mjs') would throw ERR_REQUIRE_ESM
  const { default: esmFn } = await import('./esmOnly.mjs'); // dynamic import works
  console.log(esmFn());
}
loadAndUse();
```

---

## 🟠 Express.js Integration

```javascript
// Dual-compatible Express app structure for a migrating codebase:

// server.mjs — the main ESM entry point
import express from 'express';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url); // bridge for legacy CJS routes
const legacyPaymentRoutes = require('./routes/payments.cjs'); // old CJS router, untouched

const app = express();
app.use('/payments', legacyPaymentRoutes); // mount legacy CJS router inside new ESM app

// New routes written fresh in ESM:
import userRoutes from './routes/users.mjs';
app.use('/users', userRoutes);

app.listen(3000, () => console.log('Hybrid CJS/ESM server running on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trying to `require()` an ESM-only package
```javascript
// Wrong — many modern packages (e.g. node-fetch v3+) are ESM-only
const fetch = require('node-fetch'); // Error [ERR_REQUIRE_ESM]

// Right — use dynamic import inside an async function in CJS
async function getFetch() {
  const { default: fetch } = await import('node-fetch');
  return fetch;
}
```

❌ Mistake 2: Assuming `"type": "module"` only affects `.js`, forgetting it breaks bare `require()`
```javascript
// Wrong — package.json has "type": "module", but file still uses require()
const fs = require('fs'); // ReferenceError: require is not defined in ES module scope

// Right — switch to import, or rename this specific file to .cjs to opt out of ESM
import fs from 'node:fs';
```

---

## 🧠 Tricky Interview Question

```javascript
// a.cjs
module.exports.value = 10;
setTimeout(() => { module.exports.value = 20; }, 100);

// b.cjs
const a = require('./a.cjs');
console.log(a.value); // ?
setTimeout(() => console.log(a.value), 200); // ?
```
Answer: Prints **`10`** then **`20`**. Even though CJS exports are often described as "copied, not live," this example still works because `a` is a reference to the SAME `module.exports` object — `require()` doesn't deep-clone the object, it returns the live object reference. What's NOT live in CJS is destructuring: `const { value } = require('./a.cjs')` WOULD capture `10` as a primitive snapshot and never see the update to `20`. The "copy" happens at destructure-time, not at require-time — a subtle but common interview trap.

---

## ⚫ Interview Questions + Answers

Q1: What are the main syntactic and behavioral differences between CJS and ESM?
A1: Syntax: CJS uses `require()`/`module.exports`; ESM uses `import`/`export`. Loading: CJS is synchronous (blocks until file loaded); ESM is asynchronous (module graph resolved before execution). Scope: CJS has `__dirname`/`__filename`/`require` globals per file; ESM doesn't — use `import.meta.url` instead. Bindings: CJS exports are object references (not deep copies, but destructured primitives are snapshots); ESM exports are true live bindings. File resolution: CJS allows omitting extensions; ESM requires explicit extensions.

Q2: How do you detect which module system a given `.js` file uses?
A2: Check the nearest `package.json` walking up from the file: if it has `"type": "module"`, all `.js`/`.mjs`-eligible files in that package tree are ESM; if `"type": "commonjs"` or the field is absent, they're CJS. This is overridden per-file by explicit extension: `.mjs` always forces ESM, `.cjs` always forces CJS regardless of `package.json`.

Q3: Can a single npm package support both CJS and ESM consumers?
A3: Yes — via the `"exports"` field in `package.json` with conditional exports: `{"exports": {".": {"import": "./esm/index.js", "require": "./cjs/index.js"}}}`. Tools like `tsup`, `rollup`, or `tsc` with dual configs build both output formats, and the correct one is automatically chosen based on whether the consumer does `import` or `require()`. This is called a "dual package" and is the standard way modern npm libraries ship.

Q4: Why does `require()` fail with `ERR_REQUIRE_ESM` for some packages?
A4: Because the package's `package.json` has `"type": "module"` and no CJS build/export condition — meaning the package ONLY ships ESM code. CJS's `require()` is synchronous and can't load ESM's async module graph. The fix: either switch your own file to ESM (`import`) or use a dynamic `await import()` inside an async function/wrapper, since dynamic import works from both module systems.

Q5: What replaces `__dirname` and `__filename` in ES Modules?
A5: ESM provides `import.meta.url` (a `file://` URL string of the current module). To get a usable filesystem path, convert it: `import { fileURLToPath } from 'node:url'; const __filename = fileURLToPath(import.meta.url); const __dirname = path.dirname(__filename);`. This is a very common boilerplate snippet needed when migrating path-dependent CJS code to ESM.

---

## 🔷 When to Use + When Not to Use
✅ Use CJS when:
- Maintaining a large legacy codebase where migration cost/risk outweighs benefit right now.
- Writing quick scripts/tools where synchronous conditional `require()` is simpler.

✅ Use ESM when:
- Starting fresh projects — it's the standard going forward with better tooling support.
- You need top-level `await`, static analysis, tree-shaking, or cross-platform (browser+Node) code sharing.

❌ Avoid mixing without a plan:
- Don't randomly scatter `.mjs`/`.cjs` files without a clear migration strategy — it causes confusing interop bugs (`ERR_REQUIRE_ESM`, missing `__dirname`, etc).

---

## 📊 Visual Diagram
```
CJS vs ESM — SIDE BY SIDE:
──────────────────────────────────────────────────────────
                     CommonJS              ES Modules
  Syntax:         require()/module.exports   import/export
  Loading:        synchronous                asynchronous
  File ext req:   optional                    required
  Top-level await: NO                         YES
  __dirname:      built-in                    via import.meta.url
  Bindings:       object ref (copy on destructure) live bindings
  Can require ESM: NO (use dynamic import())  N/A
  Can import CJS:  N/A                        YES (wrapped as default)

INTEROP BRIDGE:
  CJS  ──require()──X──►  ESM   (blocked, must use await import())
  ESM  ──import────────►  CJS   (allowed, Node auto-wraps)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CJS | CommonJS module system | require/module.exports वाला system |
| ESM | ECMAScript Modules | import/export वाला standard system |
| Dual package | npm package shipping both formats | दोनों format ship करने वाला package |
| Interop | Bridging CJS and ESM | दोनों systems को जोड़ना |
| createRequire | Recreate require() inside ESM | ESM में require() बनाना |
| import.meta.url | Current module's file URL in ESM | ESM में current file का URL |
| conditional exports | package.json exports map by format | Format के हिसाब से exports |

---

## ⚡ 3-Line Summary
English: CJS (`require`/`module.exports`, sync) and ESM (`import`/`export`, async) are Node's two module systems, chosen per-file via extension (`.cjs`/`.mjs`) or `package.json`'s `"type"` field. ESM can import CJS automatically, but CJS can never statically `require()` ESM — only dynamic `await import()` bridges that direction. Modern packages ship "dual" builds via conditional exports so consumers on either system work seamlessly.
Hindi: CJS (`require`/`module.exports`, sync) और ESM (`import`/`export`, async) Node के दो module systems हैं, extension (`.cjs`/`.mjs`) या `package.json` के `"type"` field से चुने जाते हैं। ESM automatically CJS import कर सकता है, पर CJS कभी statically ESM को `require()` नहीं कर सकता — केवल dynamic `await import()` इस direction को bridge करता है। Modern packages conditional exports के through "dual" builds ship करते हैं ताकि दोनों systems के consumers seamlessly काम करें।

---

## ➡️ Next Topic
**26. __dirname + __filename** — resolving current file/folder paths in CJS, and the ESM equivalent pattern.
