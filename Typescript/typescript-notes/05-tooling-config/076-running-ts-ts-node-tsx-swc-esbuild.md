# 76. Running TS — ts-node, tsx, swc, esbuild
# हिंदी में: TypeScript चलाना — ts-node, tsx, swc, esbuild

> Verified with TypeScript 5.9, tsx 4.x, ts-node 10.x, esbuild, @swc/core and **Node 24** (native type stripping). Native `node file.ts` = Node 22.6+ (flag) / unflagged in 23.6+ / 22.18+. `erasableSyntaxOnly` = TS 5.8.

---

## 🔵 Simple Definition (English)
Browsers and Node run **JavaScript**, not TypeScript. To run `.ts` you either **compile first** (`tsc` then `node dist/`) or use a tool that **transpiles on the fly**: **`tsx`** and **`esbuild`** (very fast, use esbuild; they only **strip types** and do **no type-checking**), **`swc`** (Rust-based, same idea), **`ts-node`** (older; uses the real TypeScript compiler, so it can type-check but is slow), and **Node itself** (v22.6+/24: `node file.ts` strips types natively but only supports *erasable* syntax). The key interview point: **fast runners do not type-check - `tsc --noEmit` still must run in CI.**

## 🔵 सरल परिभाषा (Hindi)
Browser और Node **JavaScript** चलाते हैं, TypeScript नहीं। `.ts` चलाने के दो रास्ते हैं: **पहले compile** करो (`tsc` फिर `node dist/`) या ऐसा tool इस्तेमाल करो जो **उसी समय transpile** कर दे: **`tsx`** और **`esbuild`** (बहुत तेज़; ये सिर्फ **types हटाते** हैं, **type-check नहीं करते**), **`swc`** (Rust वाला, वही idea), **`ts-node`** (पुराना; असली TypeScript compiler इस्तेमाल करता है, इसलिए type-check कर सकता है पर धीमा है), और **Node खुद** (v22.6+/24: `node file.ts` types को natively हटा देता है पर सिर्फ *erasable* syntax चलता है)। Interview का मुख्य बिंदु: **तेज़ runners type-check नहीं करते - CI में `tsc --noEmit` फिर भी चलाना ज़रूरी है।**

---

## 🔴 Problem it Solves
The classic dev loop `tsc && node dist/server.js` is slow for scripts, migrations, seed files and dev servers. Developers want `run this .ts file now`. At the same time, correctness still needs a type-check somewhere. The tool landscape (ts-node -> tsx/esbuild/swc -> native Node) exists to separate two jobs: **(1) executing code quickly** and **(2) checking types thoroughly**.

## 🔴 यह क्यों बना? (Hindi)
पुराना dev loop `tsc && node dist/server.js` scripts, migrations, seed files और dev servers के लिए धीमा है। Developers चाहते हैं "यह .ts file अभी चलाओ"। साथ ही type-check कहीं न कहीं ज़रूरी रहता है। Tools की यह दुनिया (ts-node -> tsx/esbuild/swc -> native Node) दो काम अलग करने के लिए है: **(1) code जल्दी चलाना** और **(2) types की गहरी जाँच**।

---

## 🟢 How it Works — Step by Step

Step 1 → **Transpile-only tools** (`tsx`, `esbuild`, `swc`) parse the file, delete type annotations/interfaces, convert syntax (enums, JSX, decorators) to JS, and run it. They look at **one file at a time** - they cannot know types from other files.
Step 2 → **`ts-node`** hooks `require`, calls the real TypeScript compiler API per file, reports type errors (e.g. `TS2322`) before running. Add `--transpile-only` (or `swc: true`) to skip checking.
Step 3 → **Native Node** (`node app.ts`) strips only *erasable* syntax. `enum`, `namespace`, and constructor parameter properties are **not erasable** -> `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX`. Pair it with `"erasableSyntaxOnly": true` so `tsc` warns you earlier.
Step 4 → **Single-file transpilation** has consequences: you need `isolatedModules` / `verbatimModuleSyntax` so that re-exports of types are explicit (`export type`), and `const enum` across files is unsafe.
Step 5 → **Production**: compile with `tsc` (or a bundler such as esbuild/tsup/Vite) and run plain JS. Use `tsc --noEmit` as a separate CI step.
Step 6 → **Dev**: `tsx watch src/server.ts` restarts on change; `ts-node-dev`/`nodemon` are older equivalents.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → **Transpile-only tools** (`tsx`, `esbuild`, `swc`) file parse करते हैं, type annotations/interfaces हटाते हैं, syntax (enums, JSX, decorators) को JS में बदलते हैं और चला देते हैं। वे **एक बार में एक file** देखते हैं - दूसरी files के types उन्हें पता नहीं होते।
Step 2 → **`ts-node`** `require` को hook करता है, हर file पर असली TypeScript compiler API चलाता है, चलाने से पहले type errors (जैसे `TS2322`) बताता है। जाँच छोड़ने के लिए `--transpile-only` (या `swc: true`) लगाओ।
Step 3 → **Native Node** (`node app.ts`) सिर्फ *erasable* syntax हटाता है। `enum`, `namespace` और constructor parameter properties **erasable नहीं** हैं -> `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX`। इसके साथ `"erasableSyntaxOnly": true` लगाओ ताकि `tsc` पहले ही चेतावनी दे।
Step 4 → **Single-file transpilation** के नतीजे: `isolatedModules` / `verbatimModuleSyntax` चाहिए ताकि types के re-export साफ (`export type`) हों, और `const enum` files के पार असुरक्षित है।
Step 5 → **Production**: `tsc` (या esbuild/tsup/Vite जैसे bundler) से compile करो और साधारण JS चलाओ। `tsc --noEmit` को अलग CI step रखो।
Step 6 → **Dev**: `tsx watch src/server.ts` बदलाव पर restart करता है; `ts-node-dev`/`nodemon` पुराने विकल्प हैं।

---

## 🟡 Real World Example
**A Swiggy-style backend team**: local dev uses `tsx watch src/server.ts` (restart in ~100 ms); DB seed script `scripts/seed.ts` runs via `tsx`; Docker image is built with `tsc` -> `node dist/server.js`; CI runs `tsc --noEmit` + ESLint. When a developer pushed code where `price: number = "499"`, the dev server **happily ran it** (tsx does not check) - only the CI `tsc --noEmit` step caught it. Nobody was surprised, because the team knew the rule: runner != checker.

## 🟡 Real Example Hindi mein
**Swiggy-जैसी backend team**: local dev में `tsx watch src/server.ts` (~100 ms में restart); DB seed script `scripts/seed.ts` `tsx` से चलती है; Docker image `tsc` -> `node dist/server.js` से बनता है; CI में `tsc --noEmit` + ESLint चलते हैं। जब किसी ने `price: number = "499"` वाला code push किया तो dev server ने उसे **आराम से चला दिया** (tsx check नहीं करता) - सिर्फ CI के `tsc --noEmit` ने पकड़ा। किसी को हैरानी नहीं हुई, क्योंकि team को नियम पता था: runner != checker।

---

## 💻 Code Example — Basic

A file with a deliberate type error, run through each tool (real outputs from this machine):

```typescript
// bad.ts - has a type error on purpose
const price: number = "499"; // ❌ error TS2322: Type 'string' is not assignable to type 'number'.
console.log("ran with a type error, price =", price, typeof price);
```

```text
$ npx tsc --noEmit --strict bad.ts
bad.ts(1,7): error TS2322: Type 'string' is not assignable to type 'number'.

$ npx tsx bad.ts                         # no type-check -> runs!
ran with a type error, price = 499 string

$ node bad.ts                            # Node 24 native stripping -> runs, with a warning
ran with a type error, price = 499 string
(ExperimentalWarning: Type Stripping is an experimental feature ...)

$ npx ts-node bad.ts                     # real compiler -> stops before running
TSError: ⨯ Unable to compile TypeScript:
bad.ts(1,7): error TS2322: Type 'string' is not assignable to type 'number'.

$ npx ts-node --transpile-only bad.ts    # skip checking -> runs
ran with a type error, price = 499 string

$ npx esbuild bad.ts --format=cjs        # output = same JS with the types removed
const price = "499";
console.log("ran with a type error, price =", price, typeof price);
```

A correct file for comparison:

```typescript
// ok.ts
interface Order { id: string; total: number } // erased at runtime
const o: Order = { id: "ORD-1", total: 499 }; // typed object
console.log(`Order ${o.id}: Rs.${o.total}`); // Order ORD-1: Rs.499 (same output in tsx, node, ts-node, swc)
```

## 💻 Code Example — Advanced

Syntax that is **not erasable** (valid TypeScript, passes `tsc --strict`, but native Node refuses):

```typescript
// enum.ts
enum Status { Placed, Paid } // enum = real runtime object, needs code generation
console.log(Status.Paid); // tsx prints 1

class Payment {
  constructor(public amount: number) {} // parameter property = needs code generation (note 66)
}
console.log(new Payment(1).amount); // tsx prints 1
```

```text
$ npx tsx enum.ts
1
1
$ node enum.ts
SyntaxError [ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX]: TypeScript enum is not supported in strip-only mode
```

tsconfig and scripts for a modern Node service (type-check with tsc, execute with tsx, ship compiled JS):

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "strict": true,
    "verbatimModuleSyntax": true,
    "isolatedModules": true,
    "erasableSyntaxOnly": true,
    "noEmit": true,
    "skipLibCheck": true
  },
  "include": ["src", "scripts"]
}
```

```json
{
  "scripts": {
    "dev": "tsx watch src/server.ts",
    "seed": "tsx scripts/seed.ts",
    "typecheck": "tsc --noEmit",
    "build": "esbuild src/server.ts --bundle --platform=node --outfile=dist/server.js",
    "start": "node dist/server.js"
  }
}
```

esbuild and swc CLI usage (real runs): `esbuild ok.ts --bundle --platform=node --outfile=out.js` produced `out.js 106b` in 9 ms and `node out.js` printed `Order ORD-1: Rs.499`; `swc ok.ts -o s.js` (with `.swcrc` `{"jsc":{"parser":{"syntax":"typescript"},"target":"es2022"}}`) printed `Successfully compiled 1 file with swc.`

---

## 🟠 Node/Express + React Integration

```typescript
// server.ts - run with: npx tsx server.ts   (type-checked separately with tsc --noEmit)
import express, { type Request, type Response } from "express"; // `type` modifier = erased import (verbatimModuleSyntax-friendly)

interface Order { id: string; totalPaise: number } // response shape
const orders: Order[] = [{ id: "ORD-1", totalPaise: 49900 }]; // fake data

const app = express(); // create app
app.get("/orders/:id", (req: Request<{ id: string }>, res: Response<Order | { error: string }>) => {
  const found = orders.find((o) => o.id === req.params.id); // typed lookup
  if (!found) {
    res.status(404).json({ error: "not found" }); // typed error body
    return;
  }
  res.json(found); // typed success body
});

const server = app.listen(3077, () => console.log("listening on 3077")); // start
setTimeout(() => server.close(), 4000); // demo only: stop after 4 s
// Real run: GET /orders/ORD-1 -> {"id":"ORD-1","totalPaise":49900}   GET /orders/X -> 404
```

```tsx
// React side: Vite uses esbuild to transpile TSX in dev - so it also does NOT type-check.
// That is why package.json has: "build": "tsc --noEmit && vite build"
import React from "react";

export function Price({ paise }: { paise: number }) {
  return <b>Rs.{(paise / 100).toFixed(2)}</b>; // a type error here shows in the editor and in `tsc --noEmit`, not in `vite dev`
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assuming "it runs" means "it type-checks"
```typescript
const qty: number = "3"; // ❌ error TS2322: Type 'string' is not assignable to type 'number'.  (tsx / esbuild / swc / node still run it!)
```
✅ Always keep `tsc --noEmit` in CI (and pre-push if you like).

❌ Mistake 2: Using `enum` / parameter properties with native `node file.ts`
Real output: `SyntaxError [ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX]: TypeScript enum is not supported in strip-only mode`. ✅ Use `as const` objects / union types, or run with `tsx`, and turn on `erasableSyntaxOnly`.

❌ Mistake 3: `ts-node` with modern `module`/`moduleResolution` config mismatches
Real output when ts-node found no suitable tsconfig: `error TS5109: Option 'moduleResolution' must be set to 'NodeNext' (or left unspecified) when option 'module' is set to 'NodeNext'.` ✅ Provide a tsconfig (`"module": "commonjs"`), or migrate to `tsx`; `ts-node` has weaker ESM support and is rarely updated.

❌ Mistake 4: Running TS directly in production
Startup cost (transpile on every start), no type-check, dev dependencies needed in the image. ✅ Build once, ship JS.

❌ Mistake 5: Re-exporting types without `export type` in a single-file transpiler
`export { Order } from "./types"` is ambiguous for esbuild/swc (it cannot tell type from value). Use `export type { Order } from "./types"` and turn on `isolatedModules`/`verbatimModuleSyntax`.

---

## 🧠 Tricky Interview Question

Q: Your teammate says "tsx compiled it, so the types are fine". True? And why can `esbuild` not do `const enum` across files correctly?

Answer: False. `tsx`/`esbuild` only **erase** types; they never evaluate them (real run: `const price: number = "499"` executed and printed `499 string`). Type correctness comes only from `tsc` (or your IDE's tsserver). `const enum` values are meant to be **inlined** using type information from the other file; a single-file transpiler cannot see that file, so it must treat it like a normal enum (or fail) - this is why `isolatedModules` forbids ambient const enums and why many teams ban `const enum`.

---

## ⚫ Interview Questions + Answers

Q1: `tsx` vs `ts-node`?
A1: `tsx` = esbuild-based, zero config, fast, ESM+CJS, **no type-check**. `ts-node` = TypeScript compiler API, **type-checks** by default, slower, ESM support is fragile. Today most teams use `tsx` to run and `tsc --noEmit` to check.

Q2: `swc` vs `esbuild`?
A2: Both are native-speed transpilers that strip types without checking. swc (Rust) is plugin-friendly and used by Next.js/Jest transforms and supports decorator metadata (needed by NestJS); esbuild (Go) is the bundler behind Vite dev, tsup and tsx.

Q3: Can Node run TypeScript without any tool?
A3: Node 22.6+ (flag) / 23.6+ and 22.18+ (default) strips erasable syntax. No `enum`, `namespace`, parameter properties; no type-checking; relative imports must include the `.ts` extension. Use `erasableSyntaxOnly` to stay compatible.

Q4: What do `isolatedModules` and `verbatimModuleSyntax` do?
A4: They make `tsc` report code that single-file transpilers cannot compile correctly (type re-exports, `import` of types without `type`, ambient const enums). They are the compatibility flags for esbuild/swc/tsx/Babel.

Q5: How do you ship a Node service?
A5: Build with `tsc` or a bundler (`esbuild --bundle`, `tsup`) to JS, run `node dist/server.js`, and run `tsc --noEmit` + tests in CI.

---

## 🔷 When to Use + When Not to Use
✅ Use `tsx` / `esbuild` / `swc` when:
- Local dev servers, scripts, seeders, tests, quick prototypes

✅ Use `ts-node` when:
- You must type-check at startup in an existing legacy setup (consider migrating)

❌ Avoid:
- Running transpile-on-the-fly in production containers
- Relying on any runner as your only type check

---

## 📊 Visual Diagram
```
                  type-check?   speed       use for
 tsc              YES           slow        CI, library builds, .d.ts
 ts-node          YES (opt-out) slow        legacy scripts
 tsx (esbuild)    NO            very fast   dev, scripts, tests
 swc              NO            very fast   Next.js/Jest/Nest builds
 esbuild          NO            fastest     bundling, Vite dev
 node file.ts     NO            instant     erasable syntax only

 Good pipeline:   edit ──► tsx watch (run)      CI ──► tsc --noEmit (check) ──► build ──► node dist/
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Transpile-only | Remove types, no checking | सिर्फ types हटाना, जाँच नहीं |
| Type stripping | Node natively deleting type syntax | Node का types हटाना |
| Erasable syntax | Syntax removable without codegen | बिना code generation हटाने योग्य syntax |
| `isolatedModules` | Each file must compile alone | हर file अकेली compile हो सके |
| `verbatimModuleSyntax` | Imports/exports kept exactly as written | Imports जैसे लिखे वैसे रहें |
| `tsc --noEmit` | Type-check only | सिर्फ type-check |

---

## ⚡ 3-Line Summary
English:
1. tsx, esbuild, swc and native Node only strip types - they never type-check; ts-node can.
2. Keep `tsc --noEmit` in CI, run dev code with `tsx`, ship compiled JS.
3. Native Node cannot run enums/namespaces/parameter properties: use `erasableSyntaxOnly`.

Hindi:
1. tsx, esbuild, swc और native Node सिर्फ types हटाते हैं - type-check कभी नहीं करते; ts-node कर सकता है।
2. CI में `tsc --noEmit` रखो, dev में `tsx` से चलाओ, production में compiled JS भेजो।
3. Native Node enums/namespaces/parameter properties नहीं चला सकता: `erasableSyntaxOnly` लगाओ।

---

## ➡️ Next Topic
**77. ESLint + typescript-eslint** - Catching bugs that the compiler allows (floating promises, unsafe any) with type-aware lint rules.
