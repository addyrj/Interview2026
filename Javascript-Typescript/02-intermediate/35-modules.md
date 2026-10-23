# 35. Modules — import/export, ES Modules vs CommonJS
# हिंदी में: Modules — Code को Organize और Share करना

---

## 🔵 Simple Definition (English)
A **module** is a file with its own scope — variables and functions are not global by default. ES Modules (`import`/`export`) is the modern standard. CommonJS (`require`/`module.exports`) is Node.js's older system. Both let you split code into reusable pieces.

## 🔵 सरल परिभाषा (Hindi)
Module एक file है जिसका अपना scope होता है — variables और functions default से global नहीं होते। ES Modules (`import`/`export`) modern standard है। CommonJS (`require`/`module.exports`) Node.js का पुराना system है। दोनों code को reusable pieces में split करने देते हैं।

---

## 🟢 Quick Reference

```javascript
// ES MODULES (modern — browser + Node.js 14+):
export const PI = 3.14;          // named export
export function add(a, b) { ... } // named export
export default class App { ... }  // default export (one per file)

import { PI, add } from "./math.js";    // named import
import App from "./App.js";             // default import
import * as Math from "./math.js";      // namespace import

// COMMONJS (Node.js legacy):
module.exports = { PI, add };     // export object
const { PI, add } = require("./math.js"); // destructure require
```

---

## 🟡 Real World Example
```javascript
// utils/currency.js
export const formatINR = (amount) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(amount);

export const addGST = (price, rate = 0.18) => price * (1 + rate);

export default {
  formatINR,
  addGST,
};

// In component:
import CurrencyUtils, { formatINR, addGST } from "../utils/currency.js";

formatINR(1234);    // "₹1,234.00"
addGST(299);        // 352.82
```

---

## 💻 Code Example — Basic
```javascript
// ── NAMED EXPORTS ────────────────────────

// math.js:
export const PI = 3.14159;
export const E = 2.71828;

export function add(a, b) { return a + b; }
export function subtract(a, b) { return a - b; }
export function multiply(a, b) { return a * b; }

// Export at end (alternative style):
// function add(a, b) { return a + b; }
// export { add, subtract, multiply };

// ── DEFAULT EXPORT ───────────────────────

// Only one default per file:
export default function formatDate(date) {
  return new Date(date).toLocaleDateString("en-IN");
}

// OR:
// export default class { ... }
// export default { key: value };

// ── IMPORTING ────────────────────────────

// Named imports:
import { PI, add, multiply } from "./math.js";

// Rename on import:
import { add as sum, subtract as minus } from "./math.js";
sum(1, 2);   // 3
minus(5, 2); // 3

// Default import (name can be anything):
import formatDate from "./formatDate.js";
import myFormat from "./formatDate.js"; // same file, different name — fine

// Both in one import:
import formatDate, { PI, add } from "./mathUtils.js";

// Namespace import (all named exports as one object):
import * as MathUtils from "./math.js";
MathUtils.PI;       // 3.14159
MathUtils.add(1,2); // 3

// ── RE-EXPORTING ─────────────────────────

// index.js — barrel file:
export { formatINR, addGST } from "./currency.js";
export { validateEmail } from "./validators.js";
export { default as Button } from "./Button.jsx";
// Now consumers import from one place:
// import { formatINR, validateEmail, Button } from "../utils";

// ── COMMONJS (Node.js old) ───────────────

// math.cjs:
const PI = 3.14159;
function add(a, b) { return a + b; }
module.exports = { PI, add }; // export object
// OR:
module.exports.PI = 3.14;
module.exports.add = add;

// Consuming:
const { PI, add } = require("./math.cjs");
const MathUtils = require("./math.cjs"); // whole object

// ── DYNAMIC IMPORT ───────────────────────
// Load modules on demand (code splitting):

// Static import — always loaded upfront:
import { heavyLib } from "./heavy.js"; // loaded at startup

// Dynamic import — loaded when needed:
const loadChart = async () => {
  const { Chart } = await import("./ChartLib.js"); // lazy loaded
  return new Chart(data);
};

// Use with condition:
if (userWantsReport) {
  const { generatePDF } = await import("./pdfGenerator.js");
  generatePDF(data);
}
```

## 💻 Code Example — Advanced
```javascript
// ── BARREL PATTERN (index.js) ────────────

// Without barrel:
import { Button } from "../../components/Button/Button.jsx";
import { Input } from "../../components/Input/Input.jsx";
import { Modal } from "../../components/Modal/Modal.jsx";

// With barrel (components/index.js re-exports everything):
export { Button } from "./Button/Button.jsx";
export { Input } from "./Input/Input.jsx";
export { Modal } from "./Modal/Modal.jsx";

// Consumers:
import { Button, Input, Modal } from "../../components"; // clean!

// ── MODULE CIRCULAR DEPENDENCY TRAP ──────

// a.js: import { b } from "./b.js"; export const a = 1;
// b.js: import { a } from "./a.js"; export const b = 2;
// → Circular dep — a may be undefined when b initializes

// Fix: extract shared code to c.js that neither a nor b imports from the other

// ── CONFIGURING NODE.JS FOR ES MODULES ───

// package.json:
// { "type": "module" } → all .js files are ES modules
// Without it: .js files are CommonJS, use .mjs for ES modules

// Top-level await (only in ES modules):
// const data = await fetch("/api").then(r => r.json()); // works in .mjs

// ── CONDITIONAL IMPORTS ──────────────────

// Node.js conditional exports in package.json:
// {
//   "exports": {
//     ".": {
//       "import": "./dist/index.mjs",  // for ES module consumers
//       "require": "./dist/index.cjs"  // for CommonJS consumers
//     }
//   }
// }

// ── TREE SHAKING (IMPORTANT FOR PERFORMANCE) ──

// Named exports enable tree shaking (bundlers remove unused code):
import { add } from "./math.js";  // bundler only includes 'add', not PI, multiply, etc.

// Default object export PREVENTS tree shaking:
import MathUtils from "./math.js";
MathUtils.add; // bundler has to include EVERYTHING (can't tell what's used)

// Best practice: named exports for libraries
```

---

## 🟠 React/Next.js Connection
```jsx
// ── REACT COMPONENT EXPORTS ───────────────

// Button.jsx:
export function Button({ children, onClick, variant = "primary" }) {
  return <button className={`btn-${variant}`} onClick={onClick}>{children}</button>;
}

export function IconButton({ icon, ...props }) {
  return <Button {...props}><span>{icon}</span></Button>;
}

// Default for main component:
export default Button;

// ── CUSTOM HOOKS AS MODULES ───────────────

// hooks/useCart.js:
import { useState, useCallback } from "react";

export function useCart(initialItems = []) {
  const [items, setItems] = useState(initialItems);

  const addItem = useCallback((item) => {
    setItems(prev => [...prev, { ...item, id: Date.now() }]);
  }, []);

  const removeItem = useCallback((id) => {
    setItems(prev => prev.filter(i => i.id !== id));
  }, []);

  const total = items.reduce((sum, i) => sum + i.price * i.qty, 0);

  return { items, addItem, removeItem, total };
}

// ── NEXT.JS DYNAMIC IMPORTS ───────────────

import dynamic from "next/dynamic";

// Lazy-load heavy component (code splits it):
const HeavyChart = dynamic(() => import("./HeavyChart"), {
  loading: () => <p>Loading chart...</p>,
  ssr: false, // disable server-side rendering for this component
});

// ── NEXT.JS ROUTE HANDLERS ────────────────

// app/api/products/route.js:
import { NextResponse } from "next/server";
import { db } from "@/lib/db";  // @ = src root alias

export async function GET() {
  const products = await db.product.findMany();
  return NextResponse.json(products);
}

export async function POST(request) {
  const body = await request.json();
  const product = await db.product.create({ data: body });
  return NextResponse.json(product, { status: 201 });
}

// ── UTILS ORGANIZED AS MODULES ────────────

// lib/utils.js:
export const cn = (...classes) => classes.filter(Boolean).join(" ");
export const sleep = (ms) => new Promise(r => setTimeout(r, ms));
export const chunk = (arr, size) =>
  Array.from({ length: Math.ceil(arr.length / size) }, (_, i) =>
    arr.slice(i * size, i * size + size)
  );

// Import only what you use — tree shaking removes rest
import { cn, sleep } from "@/lib/utils";
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Mixing CommonJS and ES Modules
```javascript
// WRONG in ES module (.mjs or package.json "type":"module"):
const { PI } = require("./math.js"); // ❌ require not defined in ESM

// CORRECT: use import
import { PI } from "./math.js"; // ✅
```

❌ **Mistake 2:** Default import with wrong name (confusing)
```javascript
// button.jsx:
export default function Button() { ... }

// WRONG (imports fine but confusing):
import MyButton from "./button.jsx"; // works but misleading name

// CORRECT: match the exported name
import Button from "./button.jsx"; // ✅ clear
```

❌ **Mistake 3:** Circular imports (circular dependencies)
```javascript
// a.js imports b.js and b.js imports a.js
// Both files work at the top level, but inside functions/modules
// the imported value may be undefined during initialization

// Fix: move shared code to a third file c.js
// OR: restructure to remove the circular dependency
```

---

## 🧠 Tricky Interview Output Question
```javascript
// counter.js:
let count = 0;
export function increment() { count++; }
export function getCount() { return count; }

// main.js:
import { increment, getCount } from "./counter.js";
import { increment as inc } from "./counter.js"; // same module

increment();
inc();
console.log(getCount()); // ?
```
**Answer:** `2`  
**Why:** ES modules are **live bindings** — both `increment` and `inc` point to the same module instance. Both increments affect the same `count`.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between ES Modules and CommonJS?**
A1: **ES Modules** (ESM): `import`/`export`, static (analyzed at build time, enables tree shaking), asynchronous loading, live bindings, works in browser natively. **CommonJS** (CJS): `require`/`module.exports`, dynamic (can require conditionally), synchronous, returns copies, Node.js default. Modern code should use ESM. CJS is still common in older Node.js projects and packages.

**Q2: What is a barrel file and what are its tradeoffs?**
A2: A barrel file (usually `index.js`) re-exports from multiple files in one module — `export { Button } from "./Button"`. Benefits: clean imports (`from "../components"` instead of long paths), single entry point. Tradeoffs: can hurt tree shaking (bundler may not optimize well), can create circular dependencies, larger initial bundle if not careful. Balance: use for public APIs, not everywhere.

**Q3: What is dynamic import and when would you use it?**
A3: `import("./module.js")` returns a Promise — loads the module lazily at runtime. Use for: (1) Code splitting in large apps — don't load all code upfront. (2) Conditional imports — only load heavy lib if user needs it. (3) Next.js `dynamic()` for lazy-loading React components. (4) Polyfills — only load for old browsers. It's async, so use with `await` or `.then()`.

**Q4: What is tree shaking?**
A4: Tree shaking is a bundler optimization that removes unused code (dead code elimination). It only works with **static named exports** — the bundler statically analyzes which exports are imported. If you import `{ add }` from a library with 50 functions, only `add` ends up in the bundle. Default exports and dynamic requires prevent tree shaking since bundlers can't determine usage at build time.

**Q5: What are live bindings in ES Modules?**
A5: ES Module imports are **live bindings** — not copies. If the exporting module changes a variable, the importing module sees the updated value. This enables patterns like: module state (`let count = 0; export { count }`) and re-exports that stay in sync. CommonJS `require` returns copies — changes to the original don't propagate. This is why ESM is preferred for stateful shared modules.

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Fireship — ES Modules](https://www.youtube.com/results?search_query=es+modules+javascript+fireship) | ESM vs CJS visual guide |
| 📝 Article | [javascript.info — Modules](https://javascript.info/modules-intro) | Complete module tutorial |
| 📝 Article | [MDN — ES Modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules) | Browser module guide |
| 📝 Article | [Node.js ESM docs](https://nodejs.org/api/esm.html) | Node.js ESM interop |

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Module | File with own scope | अपने scope वाली file |
| Named export | Specific exported identifier | Specific export |
| Default export | One primary export per file | एक primary export |
| Tree shaking | Remove unused code | Unused code हटाना |
| Barrel file | Re-export index file | Re-export करने वाली index file |
| Dynamic import | Lazy-load module at runtime | Runtime पर module load |
| Live binding | Import reflects source changes | Import में source changes दिखें |

---

## ⚡ 3-Line Summary
**English:**
1. ES Modules (`import`/`export`) = static, tree-shakeable, browser-native. CommonJS (`require`) = dynamic, synchronous, Node.js legacy.
2. Named exports for tree-shakeable libraries; default exports for main component/function per file.
3. Dynamic `import()` for code splitting; barrel files for clean public APIs.

**Hindi:**
1. ES Modules (`import`/`export`) = static, tree-shakeable, browser-native। CommonJS (`require`) = dynamic, synchronous, Node.js legacy।
2. Libraries के लिए named exports (tree-shakeable); file की main चीज़ के लिए default export।
3. Code splitting के लिए dynamic `import()`; clean APIs के लिए barrel files।

---

## ➡️ Next Topic
**36. Symbols and Well-Known Symbols** — JavaScript's unique identifier type और built-in hooks।
