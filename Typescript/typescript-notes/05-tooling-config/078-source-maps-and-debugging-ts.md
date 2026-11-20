# 78. Source Maps and Debugging TS
# हिंदी में: Source Maps और TypeScript Debug करना

> Verified with **TypeScript 5.9.x** (`tsc --strict`) and `tsx`. Features marked with version tags where they matter.

---

## 🔵 Simple Definition (English)
A **source map** (`.js.map`) is a JSON file that maps every position in the generated JavaScript back to the original `.ts` line and column. Debuggers (VS Code, Chrome DevTools) and stack-trace libraries use it so you can set breakpoints and read errors in your **TypeScript**, even though Node/the browser actually runs **JavaScript**.

## 🔵 सरल परिभाषा (Hindi)
**Source map** (`.js.map`) एक JSON file है जो generate हुए JavaScript की हर position को वापस original `.ts` की line और column से जोड़ती है। Debugger (VS Code, Chrome DevTools) इसी से आपको **TypeScript** में breakpoint लगाने और error पढ़ने देते हैं, जबकि Node/browser असल में **JavaScript** चलाता है।

---

## 🔴 Problem it Solves
TypeScript is compiled (or stripped) to JS before it runs. Without maps, a production crash says `at dist/orders/checkout.js:1:48213` (a minified bundle line) — useless. You cannot place a breakpoint on `order.total` in `checkout.ts`. Source maps give you the original file, line, and variable names back, for debugging **and** for error monitoring tools (Sentry, Azure Application Insights).

## 🔴 यह क्यों बना? (Hindi)
TypeScript, चलने से पहले JS में compile (या strip) होता है। Maps के बिना production crash में `dist/orders/checkout.js:1:48213` जैसा minified line दिखता है — बेकार। आप `checkout.ts` में `order.total` पर breakpoint नहीं लगा सकते। Source maps original file, line और variable names वापस देते हैं — debugging के लिए **और** error monitoring tools (Sentry, Azure Application Insights) के लिए भी।

---

## 🟢 How it Works — Step by Step

Step 1 → In `tsconfig.json` set `"sourceMap": true` — `tsc` emits `checkout.js` plus `checkout.js.map`.
Step 2 → The last line of `checkout.js` gets a comment: `//# sourceMappingURL=checkout.js.map`.
Step 3 → The `.map` file holds `sources` (original files), `mappings` (VLQ-encoded position table) and optionally `sourcesContent` (the original TS text embedded).
Step 4 → Debugger/DevTools reads the comment, loads the map, and shows `.ts` while running `.js`.
Step 5 → For stack traces in plain Node, run `node --enable-source-maps dist/server.js` (Node 12.12+) so `err.stack` shows `.ts` lines.
Step 6 → For `tsx`/`ts-node` you get this automatically — they register their own source-map support.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `tsconfig.json` में `"sourceMap": true` करो — `tsc` `checkout.js` के साथ `checkout.js.map` भी बनाता है।
Step 2 → `checkout.js` की आख़िरी line में comment जुड़ता है: `//# sourceMappingURL=checkout.js.map`।
Step 3 → `.map` file में `sources` (original files), `mappings` (VLQ-encoded position table) और optional `sourcesContent` (original TS का text) होता है।
Step 4 → Debugger/DevTools वो comment पढ़कर map load करता है और चलता `.js` है पर दिखता `.ts` है।
Step 5 → Plain Node में stack trace के लिए `node --enable-source-maps dist/server.js` चलाओ ताकि `err.stack` में `.ts` lines दिखें।
Step 6 → `tsx`/`ts-node` में ये अपने आप मिलता है।

---

## 🟡 Real World Example
A **Razorpay-style payments service** crashes at 2 AM: `TypeError: Cannot read properties of undefined (reading 'amount')`. The deployed bundle is minified, so the stack says `index.js:1:90211`. Because the CI build uploads `.map` files **privately** to Sentry (not to the public CDN), Sentry rewrites the trace to `src/payments/capture.ts:42:17` — the exact line. The team fixes it in minutes.

## 🟡 Real Example Hindi mein
**Razorpay जैसी payments service** रात 2 बजे crash होती है: `TypeError: Cannot read properties of undefined (reading 'amount')`। Deployed bundle minified है, इसलिए stack में `index.js:1:90211` दिखता है। CI build `.map` files को Sentry पर **private** upload करता है (public CDN पर नहीं), तो Sentry trace को `src/payments/capture.ts:42:17` में बदल देता है — बिल्कुल सही line। Team मिनटों में fix कर देती है।

---

## 💻 Code Example — Basic

```json
// tsconfig.json — the flags that control source maps (JSON with comments; tsc allows it)
{
  "compilerOptions": {
    "target": "ES2022",        // modern output, keeps code readable for debugging
    "module": "NodeNext",      // Node ESM/CJS aware output
    "outDir": "dist",          // compiled JS + .map land here
    "rootDir": "src",          // keeps dist/ layout identical to src/
    "strict": true,            // always on
    "sourceMap": true,         // emits dist/*.js.map  (the key flag)
    "inlineSources": true,     // embeds TS text inside the map (no need to ship src/)
    "declarationMap": true     // lets "Go to Definition" jump from .d.ts to .ts in libraries
  }
}
```

```typescript
// src/checkout.ts — a function we will debug through the map
interface CartItem { name: string; price: number; qty: number } // one cart line

// Sum up the cart; a bug here is easy to spot with a breakpoint on the reduce
export function cartTotal(items: CartItem[]): number {
  return items.reduce((sum, i) => sum + i.price * i.qty, 0); // breakpoint here in VS Code
}

// Throw a typed error so the stack trace is interesting
export function assertPositive(total: number): void {
  if (total <= 0) throw new Error(`Invalid cart total: ${total}`); // stack points to THIS .ts line
}

// Demo run
const total = cartTotal([{ name: "Paneer Tikka", price: 220, qty: 2 }]); // 440
assertPositive(total); // passes, nothing thrown
console.log(total); // 440
```

```bash
# Terminal commands (not TS) — run and see .ts lines in a crash
npx tsc                                   # emits dist/checkout.js and dist/checkout.js.map
node --enable-source-maps dist/checkout.js  # stack traces now reference src/checkout.ts
npx tsx src/checkout.ts                   # tsx: no build step, maps handled automatically
```

## 💻 Code Example — Advanced

```json
// .vscode/launch.json — debug Express+TS in VS Code with breakpoints in .ts files
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug API (tsx)",
      "type": "node",
      "request": "launch",
      "runtimeExecutable": "npx",                 // run via npx
      "runtimeArgs": ["tsx", "--inspect-brk"],    // tsx with the inspector paused on line 1
      "args": ["src/server.ts"],                  // entry file in TypeScript
      "skipFiles": ["<node_internals>/**"],       // do not step into Node internals
      "console": "integratedTerminal"             // see logs in VS Code terminal
    },
    {
      "name": "Debug compiled dist",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/dist/server.js", // run the built JS
      "preLaunchTask": "tsc: build - tsconfig.json",  // build first so maps are fresh
      "sourceMaps": true,                             // use the .map files
      "outFiles": ["${workspaceFolder}/dist/**/*.js"] // where the debugger looks for maps
    }
  ]
}
```

```typescript
// src/errors/report.ts — production: log the stack WITH source-map support
// Run with:  node --enable-source-maps dist/server.js
interface ErrorReport {
  message: string;       // human text
  stack: string;         // already mapped back to .ts by Node
  orderId?: string;      // business context for the on-call engineer
}

// Build a report from anything that was thrown (catch gives `unknown` under strict)
export function toReport(err: unknown, orderId?: string): ErrorReport {
  if (err instanceof Error) {
    // err.stack shows src/*.ts lines when --enable-source-maps is set
    return { message: err.message, stack: err.stack ?? "", orderId };
  }
  // Non-Error throws (strings, objects) are still possible in JS land
  return { message: String(err), stack: "", orderId };
}

// Programmatic toggle (Node 16.6+) — useful in tests / serverless handlers
export function enableMaps(): void {
  // process.setSourceMapsEnabled is typed in @types/node >= 16.6
  process.setSourceMapsEnabled(true);
}
```

---

## 🟠 Node/Express + React Integration

```typescript
// server.ts — Express error middleware that logs a mapped stack
import express, { type ErrorRequestHandler } from "express"; // `type` import = erased at runtime

const app = express(); // create the app

app.get("/boom", () => {
  throw new Error("Payment gateway timeout"); // stack will point to this .ts line
});

// 4-argument signature = Express error middleware
const onError: ErrorRequestHandler = (err: unknown, _req, res, _next) => {
  const stack = err instanceof Error ? err.stack : String(err); // mapped when --enable-source-maps
  console.error(stack);                                         // goes to Azure Log Stream / App Insights
  res.status(500).json({ error: "Internal Server Error" });     // never leak the stack to the client
};
app.use(onError); // register LAST

export default app; // listen() lives in another file
```

```typescript
// vite.config.ts — React frontend: maps for prod, hidden from browsers
import { defineConfig } from "vite"; // Vite's typed config helper

export default defineConfig({
  build: {
    // "hidden" = emit .map files but do NOT add the //# sourceMappingURL comment
    // upload the maps to Sentry/App Insights in CI, then delete them from the CDN folder
    sourcemap: "hidden",
  },
});
```

**Azure tip:** on App Service set `NODE_OPTIONS=--enable-source-maps` in *Configuration > Application settings* so every stack in Log Stream is mapped.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Shipping `.map` files to the public CDN (anyone can read your original source).
✅ Use `sourcemap: "hidden"` (Vite) / upload to Sentry, then delete the `.map` files from the public folder.

❌ Mistake 2: Compiled with `sourceMap: true` but forgot `--enable-source-maps`, so Node stacks still show `dist/*.js`.
✅ Add `NODE_OPTIONS=--enable-source-maps` or start with the flag.

❌ Mistake 3: Using a type error as a "debugging" shortcut — source maps debug **runtime**; compile errors need `tsc`. Example the compiler catches before any map matters:

```typescript
// ❌ Compile-time bug — a debugger would never even get to run this safely
const port: number = process.env.PORT;
// error TS2322: Type 'string | undefined' is not assignable to type 'number'.
//   Type 'undefined' is not assignable to type 'number'.

// ✅ Fix: parse and default
const portOk: number = Number(process.env.PORT ?? 3000); // 3000 when PORT is unset
console.log(portOk);
```

❌ Mistake 4: `rootDir` missing, so `dist/` layout changes and the `sources` paths in maps break.
✅ Set `rootDir` and `outDir` explicitly.

---

## 🧠 Tricky Interview Question
**Q:** "`tsx src/app.ts` shows correct TS lines in errors, but after `tsc` + `node dist/app.js` the same error shows `dist/app.js:17`. Why, and what are three fixes?"

**A:** `tsx` registers its own source-map support at runtime. Plain `node` does **not** read `.map` files by default. Fixes: (1) `node --enable-source-maps dist/app.js`; (2) `NODE_OPTIONS=--enable-source-maps`; (3) `process.setSourceMapsEnabled(true)` early in startup (Node 16.6+). Also check that `sourceMap: true` was actually on and the `.map` sits next to the `.js`. Note the cost: `--enable-source-maps` makes accessing `err.stack` slower — measurable if you throw thousands of errors per second.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `sourceMap`, `inlineSourceMap`, and `inlineSources`?
A1: `sourceMap` writes a separate `.js.map`. `inlineSourceMap` base64-embeds the map inside the `.js` (one file, bigger output, handy for tests). `inlineSources` embeds the original `.ts` **text** into the map's `sourcesContent`, so the debugger works even when `src/` is not deployed.

Q2: What does `declarationMap` do?
A2: It emits `.d.ts.map` so that editor "Go to Definition" on an imported library type jumps to the real `.ts` source, not the generated `.d.ts`. It matters for monorepos and published packages.

Q3: Why use `hidden` source maps in production?
A3: They are generated but not linked from the bundle, so browsers do not download them and users cannot read your source. Error-tracking tools get the maps through an upload step and still de-minify traces.

Q4: How do you debug a TS Express app in VS Code without a build step?
A4: A `launch.json` with `runtimeExecutable: "npx"`, `runtimeArgs: ["tsx", "--inspect-brk"]`, `args: ["src/server.ts"]`. Breakpoints in `.ts` files work because `tsx` emits maps in-memory.

Q5: Does a source map change runtime behaviour or performance?
A5: No change to program logic. The `.map` is only read by tooling. In Node, `--enable-source-maps` adds overhead when stacks are generated, and larger bundles with inline maps slow cold start, so prefer external or hidden maps in prod.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Debugging in VS Code or DevTools in dev (always on)
- Production error monitoring (Sentry, App Insights) with **hidden/uploaded** maps
- Published libraries (`declarationMap` for go-to-definition)

❌ Avoid / be careful when:
- Maps would be publicly served and your code is proprietary
- Serverless cold-start-sensitive code with huge inline maps
- You rely on maps to find **type** bugs — use `tsc --noEmit` in CI for that

---

## 📊 Visual Diagram
```
 src/checkout.ts ──tsc/esbuild──► dist/checkout.js  ──runs in──► Node / Browser
        ▲                              │  (last line)
        │                              ▼  //# sourceMappingURL=checkout.js.map
        │                        dist/checkout.js.map
        │                        { sources, mappings, sourcesContent }
        │                              │
        └──── Debugger / Sentry ◄──────┘
              "dist/checkout.js:1:48213"  ──►  "src/checkout.ts:42:17"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Source map | Maps generated JS positions to TS source | Generated JS की position को TS से जोड़ने वाली file |
| `sourceMap` | tsc flag to emit `.js.map` | `.js.map` बनाने वाला flag |
| `inlineSources` | Embed TS text in the map | Map में TS का text रखना |
| `sourceMappingURL` | Trailing comment pointing to the map | Map की ओर इशारा करने वाला comment |
| `--enable-source-maps` | Node flag to map stack traces | Stack trace को map करने वाला Node flag |
| Hidden source map | Map emitted but not linked | बना हुआ पर link न किया गया map |
| `declarationMap` | Map from `.d.ts` to `.ts` | `.d.ts` से `.ts` तक का map |

---

## ⚡ 3-Line Summary
English:
1. Source maps let debuggers and monitors show your original `.ts` while JS runs.
2. Use `sourceMap` + `inlineSources`, `node --enable-source-maps`, and `hidden` maps in production.
3. `tsx` handles maps for you; compiled `node dist/...` does not unless you opt in.

Hindi:
1. Source maps debugger और monitoring tools को JS चलते समय भी original `.ts` दिखाने देते हैं।
2. `sourceMap` + `inlineSources`, `node --enable-source-maps` और production में `hidden` maps इस्तेमाल करो।
3. `tsx` maps अपने आप संभालता है; compiled `node dist/...` में खुद चालू करना पड़ता है।

---

## ➡️ Next Topic
**79. Build Tools — Vite, esbuild, tsup, tsc** — which tool to pick for apps vs libraries, and why most of them do **not** type-check.
