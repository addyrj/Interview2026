# 24. ES Modules (import/export) in Node
# हिंदी में: ES Modules — Node में import/export System

---

## 🔵 Simple Definition (English)
**ES Modules (ESM)** is the official, standardized JavaScript module system (`import`/`export` syntax) that Node.js supports natively since v12+. Unlike CommonJS, ESM is statically analyzable (imports/exports are determined at parse time, not runtime) and supports asynchronous loading, top-level `await`, and tree-shaking in bundlers.

## 🔵 सरल परिभाषा (Hindi)
**ES Modules (ESM)** official, standardized JavaScript module system है (`import`/`export` syntax) जिसे Node.js v12+ से natively support करता है। CommonJS के विपरीत, ESM statically analyzable है (imports/exports parse time पर ही पता चल जाते हैं, runtime पर नहीं) और asynchronous loading, top-level `await`, bundlers में tree-shaking को support करता है।

---

## 🔴 Problem it Solves
CommonJS was Node-specific — it never became a browser/web standard, so the JS ecosystem had two incompatible module systems (CommonJS for Node, no native standard for browsers, leading to bundler-only solutions like Browserify/Webpack simulating `require()`). ES2015 (ES6) standardized `import`/`export` as part of the JavaScript language itself, meant to work identically everywhere — browsers, Node, Deno, Bun. Node adopted it to let one codebase/syntax work across server and browser, enable static analysis for tooling (autocomplete, tree-shaking, dead-code elimination), and support async-by-default module loading needed for things like dynamic `import()`.

## 🔴 यह क्यों बना? (Hindi)
CommonJS केवल Node-specific था — यह कभी browser/web standard नहीं बना, इसलिए JS ecosystem में दो incompatible module systems थे (Node के लिए CommonJS, browsers के लिए कोई native standard नहीं, जिसकी वजह से Browserify/Webpack जैसे bundler-only solutions `require()` simulate करते थे)। ES2015 (ES6) ने `import`/`export` को JavaScript language का हिस्सा बनाकर standardize किया, ताकि हर जगह एक जैसा काम करे — browsers, Node, Deno, Bun। Node ने इसे अपनाया ताकि एक codebase/syntax server और browser दोनों पर चले, tooling के लिए static analysis (autocomplete, tree-shaking, dead-code elimination) possible हो, और dynamic `import()` जैसी async-by-default module loading support हो सके।

---

## 🟢 How it Works — Step by Step

Step 1 → Enable ESM in a file either by naming it `.mjs`, or by setting `"type": "module"` in the nearest `package.json`.
Step 2 → Use `export` keyword to make values public: `export const x = 5;` or `export default function() {}`.
Step 3 → Use `import { x } from './file.js'` (note: file extension is REQUIRED in Node ESM, unlike CommonJS).
Step 4 → ESM is loaded asynchronously — Node parses the whole module graph (resolving all imports) BEFORE executing any code, enabling live bindings (imported values update if the exporting module changes them).
Step 5 → Top-level `await` is allowed directly in ESM files (not in CommonJS) — e.g., `const data = await fetch(url);` at the top of a module.
Step 6 → To use CommonJS modules from ESM: `import pkg from 'cjs-package'` works for default-style CJS exports; to use ESM from CommonJS: must use dynamic `const mod = await import('./esm-file.mjs')` (no static `require()` of ESM).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → ESM enable करो file को `.mjs` नाम देकर, या nearest `package.json` में `"type": "module"` set करके।
Step 2 → `export` keyword से values public करो: `export const x = 5;` या `export default function() {}`।
Step 3 → `import { x } from './file.js'` use करो (ध्यान दें: Node ESM में file extension ज़रूरी है, CommonJS के विपरीत)।
Step 4 → ESM asynchronously load होता है — Node पूरा module graph parse करता है (सारे imports resolve करके) किसी भी code को execute करने से पहले, जिससे live bindings मिलती हैं (exporting module value बदले तो imported value भी update होती है)।
Step 5 → Top-level `await` सीधे ESM files में allowed है (CommonJS में नहीं) — जैसे `const data = await fetch(url);` module के top पर।
Step 6 → CommonJS modules को ESM से use करने के लिए: `import pkg from 'cjs-package'` default-style CJS exports के लिए काम करता है; ESM को CommonJS से use करने के लिए: dynamic `const mod = await import('./esm-file.mjs')` ज़रूरी है (ESM को static `require()` नहीं कर सकते)।

---

## 🟡 Real World Example
**Razorpay's internal SDK repo:** The team migrated their payment-gateway utility library to ESM (`"type": "module"` in `package.json`) to ship a dual CJS+ESM build via `exports` map in `package.json`, enabling tree-shaking so frontend bundlers only pull in the specific payment method (UPI, card, netbanking) a merchant's checkout page actually uses — reducing bundle size significantly instead of importing the whole SDK.

## 🟡 Real Example Hindi mein
**Razorpay का internal SDK repo:** Team ने अपनी payment-gateway utility library को ESM में migrate किया (`package.json` में `"type": "module"`) ताकि `package.json` के `exports` map के through dual CJS+ESM build ship हो सके, जिससे tree-shaking possible हो — frontend bundlers केवल उस specific payment method (UPI, card, netbanking) को pull करते हैं जो merchant की checkout page actually use करती है, पूरे SDK import करने की बजाय bundle size काफी कम हो जाता है।

---

## 💻 Code Example — Basic

```javascript
// mathUtils.mjs — ESM module (note the .mjs extension)
export function add(a, b) {
  return a + b; // named export
}

export function multiply(a, b) {
  return a * b; // named export
}

export default function subtract(a, b) {
  return a - b; // default export — one per module
}

// -------------------------------------------------------

// app.mjs — consumes the ESM module
import subtract, { add, multiply } from './mathUtils.mjs'; // default + named in one import

console.log(add(2, 3));       // 5
console.log(multiply(4, 5));  // 20
console.log(subtract(10, 4)); // 6

// Run with: node app.mjs
```

## 💻 Code Example — Advanced

```javascript
// config.mjs — ESM with top-level await
import fs from 'node:fs/promises'; // core modules use "node:" prefix (recommended in ESM)

// Top-level await — NOT possible in CommonJS without wrapping in an async IIFE
const raw = await fs.readFile('./config.json', 'utf8');
export const config = JSON.parse(raw); // export the parsed config object

// -------------------------------------------------------

// dynamicLoader.mjs — dynamic import() for conditional/lazy loading
async function loadPaymentProvider(providerName) {
  // import() returns a Promise — works in both ESM and CommonJS
  const module = await import(`./providers/${providerName}.mjs`);
  return module.default; // access default export
}

const upiProvider = await loadPaymentProvider('upi');
upiProvider.processPayment(500);

// -------------------------------------------------------

// interop.cjs — using an ESM module from CommonJS (must be async)
async function main() {
  // require('./config.mjs') would throw — ESM cannot be require()'d directly
  const { config } = await import('./config.mjs'); // dynamic import works from CJS
  console.log(config);
}
main();

// -------------------------------------------------------

// package.json for this project:
// {
//   "type": "module",      // makes .js files treated as ESM by default
//   "exports": {
//     ".": {
//       "import": "./dist/esm/index.js",   // consumers using import get this
//       "require": "./dist/cjs/index.js"   // consumers using require get this
//     }
//   }
// }
```

---

## 🟠 Express.js Integration

```javascript
// server.mjs — Express app written in ES Modules
import express from 'express';          // default export import
import { readFile } from 'node:fs/promises'; // named import from core module

const app = express();

// Top-level await to load a JSON file before the server starts
const products = JSON.parse(await readFile('./products.json', 'utf8'));

app.get('/products', (req, res) => {
  res.json(products); // serve pre-loaded data
});

// Dynamic import for lazy-loaded route modules (code-splitting style)
app.get('/admin', async (req, res) => {
  const { renderAdminDashboard } = await import('./adminDashboard.mjs');
  res.send(renderAdminDashboard());
});

app.listen(3000, () => console.log('ESM Express server running on port 3000'));

// package.json must have "type": "module" for this file to run as .js,
// or the file must be named server.mjs (as above) regardless of package.json.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting the file extension in imports
```javascript
// Wrong — Node ESM requires explicit extensions, unlike CommonJS/webpack
import { add } from './mathUtils'; // ERR_MODULE_NOT_FOUND

// Right — always include .js/.mjs extension
import { add } from './mathUtils.js';
```

❌ Mistake 2: Mixing `require()` inside an ESM file
```javascript
// Wrong — require is not defined in ESM scope
const fs = require('fs'); // ReferenceError: require is not defined

// Right — use import, or recreate require via createRequire if truly needed
import fs from 'node:fs';
// OR, to use a CJS-only package that lacks an ESM build:
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const legacyPkg = require('legacy-cjs-package');
```

---

## 🧠 Tricky Interview Question

```javascript
// counter.mjs
export let count = 0;
export function increment() {
  count++;
}

// main.mjs
import { count, increment } from './counter.mjs';
console.log(count);  // ?
increment();
console.log(count);  // ?
```
Answer: Prints **`0`** then **`1`**. This is the key difference from CommonJS: ESM exports are **live bindings**, not copied values. `count` in `main.mjs` is a live reference to the exporter's variable — when `increment()` mutates `count` inside `counter.mjs`, the imported `count` in `main.mjs` reflects the new value automatically. In CommonJS, `module.exports.count` would be a snapshot value at require-time and would NOT auto-update this way (you'd need a getter function to see live changes).

---

## ⚫ Interview Questions + Answers

Q1: How do you enable ES Modules in a Node.js project?
A1: Two ways: (1) Add `"type": "module"` to the project's `package.json` — all `.js` files in that package are then treated as ESM. (2) Name individual files with the `.mjs` extension regardless of `package.json` settings — this always runs as ESM. Conversely, `.cjs` always forces CommonJS even inside a `"type": "module"` package, useful for mixed codebases during migration.

Q2: What are the two types of exports in ESM — named vs. default?
A2: **Named exports** (`export const x = 5`) can have multiple per file, imported with matching names in curly braces: `import { x } from './file.js'`. **Default export** (`export default function() {}`) is at most one per file, imported without braces and any local name: `import myFunc from './file.js'`. You can combine both in one file; a module can have many named exports plus one default export.

Q3: Why can't CommonJS `require()` an ES Module directly?
A3: Because ESM loading is inherently asynchronous (the module graph is resolved before any execution), while `require()` is synchronous. Node cannot block synchronously to resolve an async module graph. The workaround is dynamic `import()`, which returns a Promise and must be awaited — meaning the consuming CommonJS code must be inside an `async` function.

Q4: What does "live binding" mean in ES Modules, and how is it different from CommonJS?
A4: In ESM, an imported name is a direct reference to the exporting module's binding — if the exporter changes the value later, every importer sees the updated value automatically (shown in the tricky question above). In CommonJS, `module.exports` is a plain object — once destructured/accessed, you typically get the value AT THAT TIME; if the module later reassigns `module.exports.x`, old references in consumers that destructured it earlier won't auto-update (though accessing via the object reference, e.g., `config.x`, would reflect updates since objects are passed by reference).

Q5: Can you use top-level `await` in CommonJS?
A5: No, not directly — CommonJS's module wrapper function is NOT `async`, so `await` at the top level throws a syntax error. The classic workaround is wrapping code in an async IIFE: `(async () => { const data = await fetchData(); })();`. ESM modules, by contrast, support top-level `await` natively because the module system itself loads modules asynchronously and can pause module graph resolution for pending awaits.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Starting a new Node.js project (the ecosystem and tooling are converging on ESM as default).
- You need top-level `await`, better static analysis, or tree-shaking-friendly package builds.
- Code needs to be shared between Node and browser/frontend bundlers with identical syntax.

❌ Avoid when:
- Working in a large legacy CommonJS codebase where a full migration isn't worth the risk/time yet — interop friction can slow things down.
- Depending heavily on CJS-only packages without ESM builds and no bandwidth to handle interop (`createRequire`) complexity.
- Writing quick one-off scripts where CommonJS's synchronous simplicity (`require()` anywhere) is faster to write.

---

## 📊 Visual Diagram
```
COMMONJS vs ES MODULES LOADING:
──────────────────────────────────────────────────────────

  COMMONJS (synchronous, eager):
    require('./a')  →  read file a.js  →  execute a.js  →  return exports
                                                              (blocks until done)

  ES MODULES (asynchronous, two-phase):
    Phase 1: PARSE                     Phase 2: EXECUTE
    import './a.js'   ─┐               Run a.js
    import './b.js'   ─┼─► build graph  Run b.js        (live bindings
    import './c.js'   ─┘   (static)     Run c.js          connected)
                                         Run main.js

  Static imports = known at parse time (enables tree-shaking)
  require() calls = only known at runtime (no tree-shaking)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ESM | ECMAScript Modules — import/export | Standard JS module system |
| import | Bring in exported values | Values को import करना |
| export | Expose values from a module | Values को export करना |
| default export | One per-module main export | Module का main export |
| named export | Multiple exports by name | नाम से multiple exports |
| live binding | Imported value auto-updates | Live reference, auto-update |
| top-level await | await outside async function in ESM | Module के top पर await |
| dynamic import() | Async, runtime module loading | Runtime पर async import |

---

## ⚡ 3-Line Summary
English: ES Modules is the standardized `import`/`export` syntax, enabled via `"type": "module"` or `.mjs`, offering static analysis, live bindings, and top-level `await` unlike CommonJS. File extensions are mandatory in imports, and CJS cannot synchronously `require()` ESM — only dynamic `import()` bridges them. Modern tooling and new Node projects increasingly default to ESM for better tree-shaking and cross-environment compatibility.
Hindi: ES Modules standardized `import`/`export` syntax है, `"type": "module"` या `.mjs` से enable होता है, static analysis, live bindings, और top-level `await` देता है जो CommonJS में नहीं है। Imports में file extension ज़रूरी है, और CJS synchronously ESM को `require()` नहीं कर सकता — केवल dynamic `import()` इन्हें bridge करता है। Modern tooling और नए Node projects बेहतर tree-shaking और cross-environment compatibility के लिए ESM को default बना रहे हैं।

---

## ➡️ Next Topic
**25. CommonJS vs ES Modules in Node** — direct side-by-side comparison, interop strategies, and migration guidance.
