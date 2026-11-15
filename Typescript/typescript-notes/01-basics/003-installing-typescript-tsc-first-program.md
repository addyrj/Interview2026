# 3. Installing TypeScript + tsc + First Program
# हिंदी में: TypeScript install करना, tsc और पहला program

> Version note: **TypeScript 5.x** (5.9.3 पर test किया)। Node.js 18+ मानकर चलें।

---

## 🔵 Simple Definition (English)
**`tsc`** is the TypeScript compiler command that ships in the `typescript` npm package. You install it **per project** (`npm i -D typescript`), run it with `npx tsc`, and it reads `.ts` files (plus `tsconfig.json`), reports type errors and emits `.js`. A "first program" is: write a `.ts` file → compile → run the `.js` with Node.

## 🔵 सरल परिभाषा (Hindi)
**`tsc`** TypeScript compiler का command है जो `typescript` npm package के साथ आता है। इसे **हर project में अलग** install करते हैं (`npm i -D typescript`), `npx tsc` से चलाते हैं, और यह `.ts` files (और `tsconfig.json`) पढ़कर type errors बताता है और `.js` बनाता है। "पहला program" यानी: `.ts` file लिखो → compile करो → Node से `.js` चलाओ।

---

## 🔴 Problem it Solves
Node.js and browsers cannot execute `.ts`. Beginners also hit environment problems: a global `tsc` of one version and a project expecting another, or CI using a different version than a developer's laptop → "works on my machine" type errors. The recommended setup — **local devDependency + `npx tsc` + npm scripts** — pins the compiler version in `package.json` so every developer and the CI pipeline use the identical TypeScript.

## 🔴 यह क्यों बना? (Hindi)
Node.js और browsers `.ts` नहीं चला सकते। Beginners को environment की दिक्कतें भी आती हैं: global `tsc` एक version का और project को दूसरा चाहिए, या CI का version laptop से अलग → "मेरी machine पर चल रहा है" वाले type errors। Recommended setup — **local devDependency + `npx tsc` + npm scripts** — compiler version को `package.json` में pin कर देता है ताकि हर developer और CI pipeline एक ही TypeScript इस्तेमाल करे।

---

## 🟢 How it Works — Step by Step

Step 1 → Create a project: `mkdir order-api && cd order-api && npm init -y`.
Step 2 → Install: `npm install -D typescript @types/node` (types for Node's built-in `process`, `fs` ...).
Step 3 → Generate config: `npx tsc --init` (creates `tsconfig.json`; in TS 5.9 it has `strict: true` and `types: []`, so add `"types": ["node"]`).
Step 4 → Write `src/index.ts`.
Step 5 → Compile: `npx tsc` (emits to `outDir`, e.g. `dist/`). Check only: `npx tsc --noEmit`. Watch: `npx tsc --watch`.
Step 6 → Run: `node dist/index.js`. Faster dev loop: `npx tsx src/index.ts` (esbuild-based, no type-check).
Step 7 → Add scripts to `package.json`: `"build": "tsc"`, `"typecheck": "tsc --noEmit"`, `"dev": "tsx watch src/index.ts"`.

Shell session:
```bash
mkdir order-api && cd order-api
npm init -y
npm install -D typescript @types/node tsx
npx tsc --version        # Version 5.9.3
npx tsc --init           # writes tsconfig.json
npx tsc                  # compile -> dist/
node dist/index.js       # run compiled JS
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Project बनाओ: `mkdir order-api && cd order-api && npm init -y`।
Step 2 → Install: `npm install -D typescript @types/node` (Node के built-in `process`, `fs` ... के types)।
Step 3 → Config बनाओ: `npx tsc --init` (`tsconfig.json` बनता है; TS 5.9 में `strict: true` और `types: []` आता है, इसलिए `"types": ["node"]` खुद जोड़ो)।
Step 4 → `src/index.ts` लिखो।
Step 5 → Compile: `npx tsc` (`outDir`, जैसे `dist/`, में emit होता है)। सिर्फ check: `npx tsc --noEmit`। Watch: `npx tsc --watch`।
Step 6 → चलाओ: `node dist/index.js`। तेज़ dev loop: `npx tsx src/index.ts` (esbuild-based, type-check नहीं करता)।
Step 7 → `package.json` में scripts: `"build": "tsc"`, `"typecheck": "tsc --noEmit"`, `"dev": "tsx watch src/index.ts"`।

---

## 🟡 Real World Example
At a fintech like **Razorpay**, a service repo's `package.json` has `"typescript": "5.6.3"` pinned (exact, no caret) and a CI step `npm run typecheck`. A new developer clones the repo, runs `npm ci`, and gets the exact compiler used in production builds. The Docker build runs `npm run build` (`tsc`) and the container starts with `node dist/server.js` — no TypeScript, no `ts-node`, in the production image except as a build-stage dependency.

## 🟡 Real Example Hindi mein
**Razorpay** जैसी fintech में service repo के `package.json` में `"typescript": "5.6.3"` exact (बिना caret) pin होता है और CI में `npm run typecheck` step है। नया developer clone करके `npm ci` चलाता है और production build वाला वही compiler पाता है। Docker build `npm run build` (`tsc`) चलाता है और container `node dist/server.js` से शुरू होता है — production image में TypeScript या `ts-node` नहीं होता (सिर्फ build-stage में)।

---

## 💻 Code Example — Basic

```typescript
// src/index.ts — your first TypeScript program
// Compile: npx tsc   |   Run: node dist/index.js

// A typed function: takes a name and an order count, returns a string
function greet(name: string, orders: number): string {
  // Template literal joins text and values; types guarantee name is text, orders a number
  return `Namaste ${name}, you have ${orders} active orders.`;
}

// Call it with correct types
const message: string = greet("Aditya", 2); // OK
console.log(message);                        // Namaste Aditya, you have 2 active orders.

// process comes from @types/node; argv[2] is string | undefined under strict
const cliName: string = process.argv[2] ?? "Guest"; // fallback when no argument given
console.log(greet(cliName, 0));                      // Namaste Guest, you have 0 active orders.
```

```typescript
// ❌ intentional error — what `npx tsc` prints when you break it
function greet(name: string, orders: number): string {
  return `Namaste ${name}, you have ${orders} active orders.`;
}
greet("Aditya", "two");
// src/index.ts:5:17 - error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.
// (real tsc output format: file:line:col - error TS#### : message)
```

Real raw output of `tsc --noEmit` for the failing file (as we ran it):
```
error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.
```

## 💻 Code Example — Advanced

```typescript
// src/advanced.ts — typed CLI using Node's built-in modules + async
import { readFile } from "node:fs/promises"; // typed by @types/node

// Shape of an order line in orders.json
interface OrderLine {
  sku: string;        // product code
  qty: number;        // quantity ordered
  pricePaise: number; // unit price in paise
}

// async function: return type is Promise<number>
async function totalPaise(path: string): Promise<number> {
  const text = await readFile(path, "utf8");            // string
  const lines: OrderLine[] = JSON.parse(text);          // JSON.parse -> any; we assert shape (trusting file!)
  // reduce with explicit generic accumulator type number
  return lines.reduce<number>((sum, l) => sum + l.qty * l.pricePaise, 0);
}

// Top-level main wrapper (works in CommonJS too, no top-level await needed)
async function main(): Promise<void> {
  try {
    const t = await totalPaise("./orders.json"); // may throw if the file is missing
    console.log(`Total: Rs ${(t / 100).toFixed(2)}`);
  } catch (err) {
    // err is unknown under strict (useUnknownInCatchVariables) -> narrow before use
    const msg = err instanceof Error ? err.message : String(err);
    console.error("Failed:", msg);
    process.exitCode = 1; // non-zero exit for CI/scripts
  }
}

void main(); // `void` marks the promise as intentionally not awaited
```

Useful `tsc` CLI flags to know:
```bash
npx tsc --noEmit                 # type-check only (use in CI)
npx tsc --watch                  # incremental recompile on save
npx tsc --showConfig             # print the final merged config
npx tsc --listFiles              # which files are in the program
npx tsc -p tsconfig.build.json   # use another config file
npx tsc --init                   # create tsconfig.json
```

---

## 🟠 Node/Express + React Integration

**Express starter (`src/server.ts`):**

```typescript
// src/server.ts — minimal typed Express server
// npm i express && npm i -D typescript tsx @types/node @types/express
import express from "express";

const app = express();                          // typed Express application
const PORT = Number(process.env.PORT ?? 3000);  // env vars are string | undefined -> convert

app.get("/health", (_req, res) => {             // req/res types are inferred from the route
  res.json({ ok: true, ts: Date.now() });       // JSON response
});

export default app;                             // export app; call listen in a separate file
export { PORT };                                // so tests can import without opening a port
```

`package.json` scripts:
```json
{
  "scripts": {
    "dev": "tsx watch src/server.ts",
    "build": "tsc",
    "start": "node dist/server.js",
    "typecheck": "tsc --noEmit"
  }
}
```

**React (Vite) already ships with TS:** `npm create vite@latest shop -- --template react-ts` gives `tsconfig.json`, `.tsx` files and a `tsc -b && vite build` script. Remember: **Vite only strips types**; `tsc -b` in the build script is what actually checks them.

```tsx
// src/App.tsx — first typed React component in a Vite react-ts project
import { useState } from "react";

export default function App() {
  const [count, setCount] = useState(0);           // inferred number
  return <button onClick={() => setCount(count + 1)}>Cart: {count}</button>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `npm install -g typescript` and trusting the global version
```bash
# Wrong — every machine ends up with a different compiler
npm install -g typescript

# Right — pin per project, run via npx / npm scripts
npm install -D typescript
npx tsc --version
```

❌ Mistake 2: Running `node src/index.ts` (older Node) or expecting `tsc` to run the code
✅ Correct: `tsc` only **compiles**. Run `node dist/index.js`. (Node 22.6+ has `--experimental-strip-types`, and Node 23.6+/24 strips types by default, but it only handles erasable syntax and does no type-checking.)

❌ Mistake 3: Missing `@types/node` — `process`, `Buffer`, `node:fs` unknown
```typescript
// ❌ Without @types/node (reproduced with "types": [] in tsconfig) real tsc 5.9 prints:
// error TS2591: Cannot find name 'process'. Do you need to install type definitions for node? Try `npm i --save-dev @types/node` and then add 'node' to the types field in your tsconfig.
const port = process.env.PORT;
```
(In TS 5.9 the old TS2580 became TS2591, which also reminds you to add `"types": ["node"]` to tsconfig.)

❌ Mistake 4: Running `tsc file.ts` in a project with `tsconfig.json`
✅ Correct: when you pass file names on the command line, `tsc` **ignores tsconfig.json** (and uses defaults, non-strict). Use `npx tsc -p .` or just `npx tsc`.

---

## 🧠 Tricky Interview Question

**Question:** You run `npx tsc` on a file with a type error. Is `dist/index.js` created? What is the exit code?

**Answer:** Yes — by default `tsc` **still emits** `index.js` even with type errors (unless `noEmitOnError: true`), but exits with a **non-zero code (2 or 1)**, so CI fails while a naive `node dist/index.js` would still run the buggy build. That is why production builds often set `noEmitOnError: true` and CI runs `tsc --noEmit` separately from the bundler.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `tsc`, `ts-node`, `tsx` and `npx`?
A1: `tsc` compiles (and type-checks) to JS. `ts-node` compiles+runs on the fly with optional type-check (slower, older). `tsx` runs TS via esbuild — very fast but **no type-check**. `npx` is just the npm tool that runs a locally installed binary like `tsc`.

Q2: Why install TypeScript as devDependency?
A2: The production container only needs the emitted JS. TS is a build-time tool, so it belongs in `devDependencies`; installing it in production just bloats the image (use multi-stage Docker builds).

Q3: What does `npx tsc --init` generate in TS 5.x?
A3: A commented `tsconfig.json`. In TS 5.9 (verified) the active options are: `module: nodenext`, `target: esnext`, `types: []`, `sourceMap`, `declaration`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `strict`, `jsx: react-jsx`, `verbatimModuleSyntax`, `isolatedModules`, `skipLibCheck`. Note `types: []` — you must add `"types": ["node"]` yourself for Node globals. Older 5.x versions generated a different, longer template.

Q4: How do you see which files and which config `tsc` actually uses?
A4: `npx tsc --showConfig` prints the resolved configuration, and `npx tsc --listFiles` (or `--explainFiles`) lists every file in the program and why it was included.

Q5: What is `@types/node` and why is it needed?
A5: TypeScript's lib files describe JS built-ins only. Node's globals (`process`, `Buffer`, `__dirname`) and modules (`fs`, `path`) come from the DefinitelyTyped package `@types/node`; install version-matched to your Node major.

---

## 🔷 When to Use + When Not to Use
✅ Use `tsc` (build) when:
- Producing the production artifact (`dist/`), emitting `.d.ts` for libraries
- CI type-check gate (`tsc --noEmit`)

❌ Don't use plain `tsc --watch` as your only dev server when:
- You need hot reload for React (use Vite) or fast Node restarts (use `tsx watch`) — then keep `tsc --noEmit --watch` in a second terminal for type feedback.

---

## 📊 Visual Diagram
```
 npm i -D typescript @types/node
          │
          ▼
  src/index.ts ──► npx tsc ──► dist/index.js ──► node dist/index.js
       │              │
       │              └─ prints ❌ TS errors (exit code != 0)
       │
       └─► npx tsx src/index.ts   (fast dev: strips types, NO type-check)

  package.json scripts:  dev | build | start | typecheck
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| tsc | TypeScript compiler CLI | TypeScript compiler command |
| devDependency | Needed only while developing/building | सिर्फ development/build में चाहिए |
| outDir | Folder where compiled JS goes | Compiled JS का folder |
| --noEmit | Check types but write no files | Types check करो, files मत लिखो |
| tsx | Fast TS runner (no type-check) | तेज़ TS runner (type-check नहीं) |
| @types/node | Type declarations for Node APIs | Node APIs के type declarations |
| noEmitOnError | Don't emit JS if errors exist | Errors हों तो JS मत बनाओ |

---

## ⚡ 3-Line Summary
English:
1. Install TypeScript locally (`npm i -D typescript @types/node`) and run it with `npx tsc` / npm scripts.
2. `tsc` compiles `.ts` to `.js` and reports errors; run the output with Node, or use `tsx` for fast dev (no type-check).
3. Use `tsc --noEmit` in CI; note that `tsc file.ts` ignores `tsconfig.json`.

Hindi:
1. TypeScript को project में local install करो (`npm i -D typescript @types/node`) और `npx tsc` / npm scripts से चलाओ।
2. `tsc` `.ts` को `.js` बनाता है और errors बताता है; output Node से चलाओ, या तेज़ dev के लिए `tsx` (type-check नहीं)।
3. CI में `tsc --noEmit` चलाओ; ध्यान रखो `tsc file.ts` `tsconfig.json` को ignore करता है।

---

## ➡️ Next Topic
**004. tsconfig.json Basics** — the important compiler options: `target`, `module`, `strict`, `outDir`, `include`.
