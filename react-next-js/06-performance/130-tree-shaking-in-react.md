# 130. Tree Shaking in React
# हिंदी में: Tree Shaking — बेकार code को bundle से हटाना

---

## 🔵 Simple Definition (English)
**Tree shaking** is a build step where the bundler removes exports that are never imported ("dead code") from the final JavaScript. It works because ES modules (`import`/`export`) can be analyzed statically, without running the code.

## 🔵 सरल परिभाषा (Hindi)
**Tree shaking** build का वह चरण है जिसमें bundler उन exports को final JavaScript से हटा देता है जिन्हें कोई import नहीं करता ("dead code")। यह इसलिए संभव है क्योंकि ES modules (`import`/`export`) को code चलाए बिना, static तरीके से analyze किया जा सकता है।

---

## 🔴 Problem it Solves

Libraries export dozens of helpers. An app uses two. Without tree shaking, the other 98 still ship to every user. Before ES modules (CommonJS `require`), the bundler could not tell which exports were used, because `require` can be called dynamically.

```jsx
// PROBLEM (CommonJS): everything in the file is included, usage cannot be proven statically
const utils = require('./utils');                       // whole module object
utils.formatPrice(10);

// SOLUTION (ESM): static named import lets the bundler keep only formatPrice
import { formatPrice } from './utils';                  // bundler sees exactly one used export
```

## 🔴 यह क्यों बना? (Hindi)
Libraries दर्जनों helpers export करती हैं। App दो इस्तेमाल करता है। Tree shaking के बिना बाकी 98 भी हर user तक पहुँचते हैं। ES modules से पहले (CommonJS `require`) bundler नहीं जान पाता था कि कौन से exports इस्तेमाल हुए, क्योंकि `require` dynamically भी call हो सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Bundler parses every file and builds a graph of static import/export statements
Step 2 → It marks which exports are actually imported by someone (the "used" set)
Step 3 → It follows the graph from the entry point; unreachable exports are "dead"
Step 4 → Before removing, it checks side effects: code that runs on import (e.g. polyfills) must stay
Step 5 → The minifier (Terser/esbuild/SWC) then deletes the dead code in production mode
Step 6 → Result: the output bundle contains only used code

KEY: needs ES modules + production mode + side-effect-free code
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Bundler हर file parse करके static import/export statements का graph बनाता है
Step 2 → वह चिह्नित करता है कि कौन से exports सच में किसी ने import किए ("used" set)
Step 3 → Entry point से graph follow करता है; जिन तक पहुँचा नहीं जा सकता वे "dead" हैं
Step 4 → हटाने से पहले side effects जाँचता है: import पर चलने वाला code (जैसे polyfills) रहना चाहिए
Step 5 → फिर minifier (Terser/esbuild/SWC) production mode में dead code delete करता है
Step 6 → नतीजा: output bundle में सिर्फ़ इस्तेमाल हुआ code होता है

KEY: ES modules + production mode + side-effect-free code चाहिए
```

---

## 🟡 Real World Example
**Amazon-style product page UI kit:** The company has a shared `ui-kit` package with 120 components (Button, Carousel, Rating, Table, DatePicker...). The product page uses only Button, Rating and Carousel. If the kit is published as ES modules with `"sideEffects": false`, the bundle contains just those three. If it is published as one CommonJS file, all 120 components ship, and the page gets heavier with every new component the design team adds.

## 🟡 Real Example Hindi mein
**Amazon जैसा product page UI kit:** कंपनी के पास shared `ui-kit` package है जिसमें 120 components हैं (Button, Carousel, Rating, Table, DatePicker...)। Product page सिर्फ़ Button, Rating और Carousel इस्तेमाल करता है। अगर kit ES modules में और `"sideEffects": false` के साथ publish हुई है, तो bundle में सिर्फ़ वही तीन आएँगे। अगर kit एक CommonJS file है, तो सारे 120 components आते हैं, और design team जब भी नया component जोड़ती है page भारी होता जाता है।

---

## 💻 Code Example — Basic

```jsx
// utils.js: a module with three exports (only one will be used)
export function formatPrice(n) {                        // USED by the app
  return `Rs ${n.toFixed(2)}`;                          // format a number as price
}
export function formatWeight(g) {                       // NOT used anywhere
  return `${g / 1000} kg`;                              // will be removed by tree shaking
}
export function hugeUnusedHelper() {                    // NOT used anywhere
  return Array.from({ length: 1e6 }, (_, i) => i);      // dead code in the final bundle
}
```

```jsx
// App.jsx: a named import; only formatPrice is reachable
import { formatPrice } from './utils';                  // static named import: tree-shakeable
import { createRoot } from 'react-dom/client';          // React 18/19 root API

function App() {
  return <p>Total: {formatPrice(499)}</p>;              // renders: Total: Rs 499.00
}

createRoot(document.getElementById('root')).render(<App />);
// Production build output will contain formatPrice but not formatWeight or hugeUnusedHelper
```

## 💻 Code Example — Advanced

```jsx
// Advanced: build a small library the right way so consumers can tree shake it

// icons/index.js  (barrel file): re-exports are fine if each icon is a pure module
export { CartIcon } from './CartIcon';                  // named re-export keeps static analysis possible
export { HeartIcon } from './HeartIcon';
export { StarIcon } from './StarIcon';

// icons/CartIcon.jsx: pure, no code runs at import time (no side effects)
export function CartIcon({ size = 24 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <path d="M3 3h2l3 12h10l3-8H7" fill="none" stroke="currentColor" />  {/* simple cart path */}
    </svg>
  );
}
```

```json
// package.json of the library: tell bundlers that unused modules are safe to drop
{
  "name": "@acme/icons",
  "version": "1.0.0",
  "type": "module",                                     // ship ES modules, not CommonJS
  "main": "./dist/index.cjs",                           // fallback for old tools
  "module": "./dist/index.js",                          // ESM entry used by bundlers
  "exports": { ".": { "import": "./dist/index.js", "require": "./dist/index.cjs" } },
  "sideEffects": false                                  // promise: importing a file does nothing else
}
```

```jsx
// Consumer: only the heart icon is used, so Cart and Star are removed from the output
import { HeartIcon } from '@acme/icons';                // named import of one export
import { createRoot } from 'react-dom/client';

createRoot(document.getElementById('root')).render(<HeartIcon size={32} />);
```

```jsx
// If a file DOES have side effects (CSS imports, polyfills), list it so it is not dropped:
// "sideEffects": ["*.css", "./src/polyfills.js"]
```

---

## 🟠 Real App Integration

Next.js (webpack or Turbopack/SWC) tree shakes automatically in `next build`. For libraries that expose huge barrel files, `optimizePackageImports` rewrites imports so only used modules are loaded. Server-only code is also kept out of client bundles by the `'use client'` boundary, which is a form of "tree shaking by environment".

```js
// next.config.js
module.exports = {
  experimental: {
    optimizePackageImports: ['@acme/icons', 'lucide-react'], // version-dependent; many popular packages are already handled by default
  },
};
```

```jsx
// app/product/[id]/page.jsx (Server Component)
import { marked } from 'marked';                        // heavy markdown parser: stays on the server
import AddToCart from './AddToCart';                    // only this client component's code ships

export default async function Page({ params }) {
  const { id } = await params;                          // Next.js 15+: params is a Promise
  const html = marked.parse('**Free delivery** on ' + id); // runs on the server only
  return (
    <div>
      <div dangerouslySetInnerHTML={{ __html: html }} />{/* trusted content only */}
      <AddToCart id={id} />                             {/* small client island */}
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using CommonJS (`require`) or compiling ESM to CJS before bundling
✅ **Correct:** Keep ES modules all the way to the bundler

```js
// Wrong: Babel config turns ESM into CommonJS, so the bundler cannot shake
// { "presets": [["@babel/preset-env", { "modules": "commonjs" }]] }   // ❌

// Right: let the bundler handle modules
// { "presets": [["@babel/preset-env", { "modules": false }]] }       // ✅
```

❌ **Mistake 2:** Code that runs on import (side effects) without declaring it
✅ **Correct:** Keep modules pure, set `"sideEffects"` accurately

```jsx
// Wrong: this file does work at import time, so the bundler must keep it even when unused
window.analyticsReady = true;                           // ❌ side effect at top level
export const track = () => {};

// Right: do work inside functions that are called explicitly
export function initAnalytics() { window.analyticsReady = true; } // ✅ no work at import
```

❌ **Mistake 3:** Importing a default object and calling methods on it
✅ **Correct:** Use named exports

```jsx
// Wrong: default object export is one big value; the bundler keeps all its methods
import utils from './utils';                            // ❌
utils.formatPrice(1);

// Right
import { formatPrice } from './utils';                  // ✅ the bundler tracks this single binding
```

---

## 🧠 Tricky Interview Question

```jsx
// math.js
console.log('math loaded');
export const add = (a, b) => a + b;
export const unused = () => 42;

// App.jsx
import { add } from './math';
console.log(add(1, 2));
```
**Answer:** In a production build, `unused` is removed, but the line `console.log('math loaded')` stays, because it is a top-level side effect that runs when the module is imported. The bundler can only skip a whole module if it knows nothing in it has side effects (via `"sideEffects": false` in package.json) and nothing from it is used. Here `add` is used, so the module is included, and the console.log runs. Output: `math loaded` then `3`. Tree shaking removes unused exports, not necessarily the side-effect statements of a module you still import.

---

## ⚫ Interview Questions + Answers

Q1: What is tree shaking and why does it need ES modules?
A1: It removes unused exports from the final bundle. ES `import`/`export` are static: they cannot appear inside conditions or be built from strings, so the bundler can know at build time what is used. CommonJS `require` is dynamic, so the bundler must assume everything may be used.

Q2: What does `"sideEffects": false` do?
A2: It tells the bundler that importing any file in the package does nothing except export values. Then, if no export from a file is used, the whole file can be skipped. If some files do have side effects (CSS, polyfills), list them in an array instead.

Q3: Does tree shaking work in development mode?
A3: Generally no. Most bundlers only drop dead code in production builds, where minification runs. In dev, unused exports may be marked but still present, to keep rebuilds fast.

Q4: Why can barrel files (`index.js` that re-exports everything) hurt?
A4: Importing from a barrel can force the bundler (and dev server) to load and analyze every re-exported module. If the package lacks `sideEffects: false`, unused modules may stay. Importing from the specific file path or using `optimizePackageImports` avoids this.

Q5: Is tree shaking the same as code splitting?
A5: No. Tree shaking deletes code that is never used. Code splitting keeps code that is used, but loads it later, on demand, in separate chunks. They complement each other.

---

## 🔷 When to Use + When Not to Use
✅ **Design for tree shaking when:**
- You publish a shared library or design system
- You import from large utility or icon libraries
- You care about the initial JavaScript size

❌ **Do not rely on it when:**
- Your code or dependencies are CommonJS or have import-time side effects
- You use dynamic access (`utils[key]`) or `import *` with computed use
- You expect it to remove code that is used but rarely needed (that is code splitting)

---

## 📊 Visual Diagram

```
  Source modules                    Static analysis                Output bundle
  ┌───────────────────┐
  │ utils.js          │            used?
  │  formatPrice   ───┼──────────▶  YES  ─────────────────────▶  formatPrice  ✔
  │  formatWeight  ───┼──────────▶  no   ──── removed ─────────▶  (gone)
  │  hugeHelper    ───┼──────────▶  no   ──── removed ─────────▶  (gone)
  │  console.log() ───┼─ side effect ─▶ keep (module is imported) ▶ console.log ✔
  └───────────────────┘

  ESM (static)      → bundler can PROVE usage  → shakes
  CommonJS (dynamic)→ bundler must assume all  → keeps everything
```

Re-render behavior: tree shaking happens at build time, so it has no effect on re-renders. Performance impact: smaller download and parse time, which makes hydration and the first interactions faster.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tree shaking | Removing unused exports at build time | Build समय पर unused exports हटाना |
| Dead code | Code that is never reached or used | जो code कभी इस्तेमाल नहीं होता |
| ESM | ES modules: `import`/`export` | ES modules: `import`/`export` |
| CommonJS | `require`/`module.exports` style | `require`/`module.exports` style |
| Side effect | Work done at import time | Import के समय होने वाला काम |
| `sideEffects` flag | package.json hint for bundlers | Bundlers के लिए package.json संकेत |
| Barrel file | One file re-exporting many modules | कई modules re-export करने वाली एक file |
| Minifier | Tool that shrinks and removes dead code | Code छोटा करने वाला tool |

---

## ⚡ 3-Line Summary
**English:**
1. Tree shaking removes unused exports at build time, using static ES module analysis.
2. It needs ESM, production mode, named imports and side-effect-free modules (`"sideEffects": false`).
3. It deletes unused code; code splitting defers used code. Use both.

**Hindi:**
1. Tree shaking static ES module analysis से build समय पर unused exports हटाता है।
2. इसके लिए ESM, production mode, named imports और side-effect-free modules (`"sideEffects": false`) चाहिए।
3. यह unused code हटाता है; code splitting इस्तेमाल होने वाले code को बाद में load करता है। दोनों इस्तेमाल करो।

---

## ➡️ Next Topic
**131. Code Splitting + lazy()** — app को छोटे chunks में बाँटना, `React.lazy` और `Suspense` से routes और भारी components को ज़रूरत पड़ने पर load करना।
