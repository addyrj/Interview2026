# 72. Module Resolution (node16, bundler, paths)
# हिंदी में: Module Resolution (import का path TypeScript कैसे ढूँढता है)

> Verified with TypeScript 5.9 and Node 24. `moduleResolution: "bundler"` = TS 5.0. `node16`/`nodenext` = TS 4.7 / 4.7+. `node10` (old name `node`) is deprecated in TS 6 - prefer the modern modes.

---

## 🔵 Simple Definition (English)
**Module resolution** is the algorithm TypeScript uses to turn the string in `import x from "<string>"` into an actual file (`.ts`, `.tsx`, `.d.ts`, or a package's types). You choose the algorithm with `compilerOptions.moduleResolution`: **`node16` / `nodenext`** (follows real Node.js rules, including ESM vs CommonJS and the `exports` map), **`bundler`** (what Vite/webpack/esbuild do: no file extensions needed, `exports` supported), or legacy **`node10`**. `paths` and `baseUrl` add aliases such as `@/utils/money`.

## 🔵 सरल परिभाषा (Hindi)
**Module resolution** वह algorithm है जिससे TypeScript `import x from "<string>"` की string को असली file (`.ts`, `.tsx`, `.d.ts` या किसी package के types) तक पहुँचाता है। Algorithm `compilerOptions.moduleResolution` से चुनते हैं: **`node16` / `nodenext`** (असली Node.js के नियम, ESM बनाम CommonJS और `exports` map समेत), **`bundler`** (Vite/webpack/esbuild जैसा: file extension ज़रूरी नहीं, `exports` support), या पुराना **`node10`**। `paths` और `baseUrl` aliases देते हैं, जैसे `@/utils/money`।

---

## 🔴 Problem it Solves
TypeScript only **type-checks**; it does not decide how your code runs. If the compiler thinks `import "./money"` is fine but Node at runtime needs `./money.js`, you get `ERR_MODULE_NOT_FOUND` in production even though `tsc` was green. Likewise `paths` aliases make `tsc` happy but are **not rewritten** in the emitted JS. Choosing the right `moduleResolution` makes the compiler apply the **same rules as the runtime/bundler** that will actually load your code.

## 🔴 यह क्यों बना? (Hindi)
TypeScript सिर्फ **type-check** करता है; code कैसे चलेगा यह वह तय नहीं करता। अगर compiler को `import "./money"` ठीक लगे पर runtime पर Node को `./money.js` चाहिए, तो `tsc` हरा होने के बावजूद production में `ERR_MODULE_NOT_FOUND` आता है। इसी तरह `paths` aliases `tsc` को खुश कर देते हैं पर emitted JS में **बदले नहीं जाते**। सही `moduleResolution` चुनने से compiler वही नियम लगाता है जो असली runtime/bundler लगाएगा।

---

## 🟢 How it Works — Step by Step

Step 1 → For a **relative** import (`./x`, `../x`) TS tries `x.ts`, `x.tsx`, `x.d.ts`, then `x/index.ts` (`node10`/`bundler`).
Step 2 → In `node16`/`nodenext` **ESM files** (`.mts`, or `.ts` under `"type": "module"`) relative imports need an explicit extension - and you write `.js` even though the source file is `.ts`.
Step 3 → For a **bare** import (`express`, `zod`) TS walks up `node_modules/`, reads the package's `package.json` (`exports` -> `types` -> `main`), then falls back to `@types/<name>`.
Step 4 → `paths` (e.g. `"@/*": ["src/*"]`) is tried **before** node_modules for matching names.
Step 5 → The file format decides the system: `.ts` under `"type": "module"` is ESM, under `"type": "commonjs"` is CJS, `.mts` is always ESM, `.cts` is always CJS.
Step 6 → **TypeScript does not rewrite import strings** in output. Whatever you write is what ships. Aliases then need a bundler, `tsx`/`tsc-alias`, or Node `imports` (`#/...`).

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → **Relative** import (`./x`, `../x`) के लिए TS `x.ts`, `x.tsx`, `x.d.ts`, फिर `x/index.ts` आज़माता है (`node10`/`bundler`)।
Step 2 → `node16`/`nodenext` में **ESM files** (`.mts`, या `"type": "module"` में `.ts`) के relative imports में extension लिखना ज़रूरी है - और source `.ts` होने पर भी `.js` लिखते हैं।
Step 3 → **Bare** import (`express`, `zod`) के लिए TS `node_modules/` में ऊपर की ओर खोजता है, package की `package.json` (`exports` -> `types` -> `main`) पढ़ता है, फिर `@types/<name>` देखता है।
Step 4 → `paths` (जैसे `"@/*": ["src/*"]`) matching नामों के लिए node_modules से **पहले** आज़माया जाता है।
Step 5 → File का format system तय करता है: `"type": "module"` में `.ts` ESM, `"type": "commonjs"` में CJS, `.mts` हमेशा ESM, `.cts` हमेशा CJS।
Step 6 → **TypeScript output में import strings नहीं बदलता।** जो लिखा वही जाता है। Aliases के लिए bundler, `tsx`/`tsc-alias` या Node की `imports` (`#/...`) चाहिए।

---

## 🟡 Real World Example
**A Razorpay-style payments service** runs on Node 22 as native ESM (`"type": "module"`), compiled by `tsc`. The team uses `module: nodenext` so that `tsc` behaves like Node. After a refactor someone writes `import { rupees } from "../utils/money"` - `tsc` immediately flags it (TS2835) instead of the service crashing on startup. The **React admin dashboard** of the same company is built with Vite, so there they use `moduleResolution: bundler` with an `@/` alias - Vite resolves the alias at build time.

## 🟡 Real Example Hindi mein
**Razorpay-जैसी payments service** Node 22 पर native ESM (`"type": "module"`) में चलती है और `tsc` से compile होती है। Team `module: nodenext` रखती है ताकि `tsc` Node जैसा व्यवहार करे। Refactor के बाद कोई `import { rupees } from "../utils/money"` लिख दे तो `tsc` तुरंत पकड़ लेता है (TS2835), service startup पर crash नहीं करती। उसी कंपनी का **React admin dashboard** Vite से बनता है, इसलिए वहाँ `moduleResolution: bundler` और `@/` alias है - Vite alias को build time पर resolve करता है।

---

## 💻 Code Example — Basic

The three common tsconfig setups (each checked with `tsc -p` on a sample project):

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "strict": true,
    "outDir": "dist"
  }
}
```

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "esnext",
    "moduleResolution": "bundler",
    "strict": true,
    "noEmit": true,
    "paths": { "@/*": ["./src/*"] }
  }
}
```

Real compiler result of an extension-less relative import under `nodenext` with `"type": "module"` (this is a multi-file case, so it is shown as output):

```text
// src/services/pay.ts
import { rupees } from "../utils/money";

$ tsc --module nodenext --moduleResolution nodenext
src/services/pay.ts(1,24): error TS2835: Relative import paths need explicit file extensions
in ECMAScript imports when '--moduleResolution' is 'node16' or 'nodenext'. Did you mean '../utils/money.js'?
```

The same file under `bundler` compiles without errors. The corrected `nodenext` imports (real run: `tsc -p . && node dist/main.js`):

```text
// src/main.ts   (ESM, "type": "module")
import { show } from "./services/pay.js";   // write .js - the file on disk is pay.ts
console.log(show(49900));
// output:  Rs.499.00
```

```typescript
// Built-in Node modules use the node: prefix and need no extension
import { readFile } from "node:fs/promises"; // typed by @types/node
import path from "node:path"; // default import works under esModuleInterop-style rules

const file = path.join("config", "app.json"); // build a path
console.log(typeof readFile, file); // function config/app.json
```

---

## 💻 Code Example — Advanced

```typescript
// Self-contained checks you can run on any file: resolution failures give TS2307.
import { gstOn } from "./does-not-exist"; // ❌ error TS2307: Cannot find module './does-not-exist' or its corresponding type declarations.
console.log(gstOn(100));
```

```text
// What `paths` does and does NOT do (real run, nodenext, "paths": { "@/*": ["./src/*"] })
// src/main2.ts
import { rupees } from "@/utils/money.js";

$ tsc -p .                      -> rc=0   (compiler is happy: alias resolved at type level)
$ head -1 dist3/main2.js        -> import { rupees } from "@/utils/money.js";   (UNCHANGED!)
$ node dist3/main2.js           -> Error [ERR_MODULE_NOT_FOUND]: Cannot find package '@/utils' ...
```

```typescript
// Bare imports: TS finds express's own package.json, then @types/express
import express from "express"; // resolves to @types/express (express ships no types)
import { EventEmitter } from "node:events"; // resolves to @types/node

const app = express(); // typed Express application
const bus = new EventEmitter(); // typed emitter
console.log(typeof app.get, bus.listenerCount("x")); // function 0
```

Package `exports` subpaths (e.g. `import "lib/pay"`) are honoured by `node16`/`nodenext`/`bundler` (real run: both resolved a test package with `exports: { "./pay": { types, default } }`); old `node10` ignores `exports` and only looks for physical files such as `lib/pay.d.ts`.

---

## 🟠 Node/Express + React Integration

```json
// Node/Express service (package.json: "type": "module") - tsconfig.json
{
  "compilerOptions": {
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "target": "ES2022",
    "strict": true,
    "rootDir": "src",
    "outDir": "dist",
    "verbatimModuleSyntax": true
  },
  "include": ["src"]
}
```

```typescript
// src/server.ts - ESM Express app under nodenext
import express from "express"; // default import works via esModuleInterop-like rules in nodenext
import type { Request, Response } from "express"; // type-only import (erased) - needed with verbatimModuleSyntax

const app = express();

app.get("/health", (_req: Request, res: Response) => {
  res.json({ ok: true }); // typed response
});

app.listen(3000, () => console.log("up")); // starts server on 3000
```

```json
// React (Vite) app - tsconfig.json: bundler mode + alias, Vite config must mirror the alias
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "esnext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noEmit": true,
    "allowImportingTsExtensions": true,
    "paths": { "@/*": ["./src/*"] }
  }
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Omitting the extension in Node ESM
```text
import { rupees } from "../utils/money";            // tsc nodenext: error TS2835 (see above)
// If someone silences it, node fails at runtime:
// Error [ERR_MODULE_NOT_FOUND]: Cannot find module '.../dist2/utils/money' imported from .../dist2/services/pay.js
```
✅ Right: `from "../utils/money.js"` (yes, `.js`, even though the source is `.ts`).

❌ Mistake 2: Believing `paths` makes the alias work at runtime
Real run above: `tsc` passes, emitted JS keeps `"@/utils/money.js"`, `node` throws `ERR_MODULE_NOT_FOUND: Cannot find package '@/utils'`. Use a bundler, `tsx`, `tsc-alias`, or Node's `package.json` `"imports": { "#utils/*": "./dist/utils/*" }`.

❌ Mistake 3: `moduleResolution: node16` with `module: esnext`
```text
tsconfig: { "module": "esnext", "moduleResolution": "node16" }
error TS5110: Option 'module' must be set to 'Node16' when option 'moduleResolution' is set to 'Node16'.
```
✅ Pair them: `module: nodenext` + `moduleResolution: nodenext` (or `esnext` + `bundler`).

❌ Mistake 4: Using `bundler` for code that is run directly by Node (`tsc` -> `node dist/`)
`bundler` allows extension-less imports that Node will reject at runtime. Use `bundler` only when a bundler/`tsx`/Vite actually loads the code.

---

## 🧠 Tricky Interview Question

Why do you write `import "./money.js"` in a file that is really `money.ts`?

Answer: TypeScript never rewrites import specifiers. Under `nodenext` the specifier must be the **runtime** path (`.js`) because the emitted JS file is `money.js`. The compiler maps `.js` -> `.ts` (or `.d.ts`) while resolving types. `.ts` extensions are only allowed with `allowImportingTsExtensions` (needs `noEmit`/`emitDeclarationOnly`) or `rewriteRelativeImportExtensions` (TS 5.7+).

---

## ⚫ Interview Questions + Answers

Q1: `node16` vs `nodenext`?
A1: `node16` is frozen at the Node 16 behaviour; `nodenext` tracks the latest Node behaviour and may change with TS releases. For new projects use `nodenext`.

Q2: When do I choose `bundler`?
A2: When Vite/webpack/esbuild/Next.js (or `tsx`) loads your code. It supports `exports`, allows extension-less relative imports and index files, and is used with `noEmit` or `emitDeclarationOnly` usually.

Q3: What does `baseUrl` do now that `paths` exists?
A3: Since TS 4.1 `paths` works without `baseUrl` (use `./` prefixed targets). `baseUrl` also makes bare names like `utils/money` resolve from the root, which hides real packages and is discouraged.

Q4: How does TS decide CJS vs ESM for a `.ts` file under `nodenext`?
A4: By the nearest `package.json` `"type"` field; `.mts` is always ESM and `.cts` always CJS. In a CJS file `import x from "esm-only-pkg"` is compiled to `require`, which fails for ESM-only packages (use dynamic `import()`).

Q5: How are types for a package found?
A5: `exports["."].types` / `types` field / `index.d.ts` next to `main`, else `node_modules/@types/<pkg>`, else TS2307 (or TS7016 for untyped JS).

---

## 🔷 When to Use + When Not to Use
✅ Use `nodenext` when:
- `tsc` output runs directly in Node (APIs, workers, CLIs)

✅ Use `bundler` when:
- Vite/webpack/Next.js/`tsx` handles the build (React apps, monorepo front-ends)

❌ Avoid:
- `node10` for new code (ignores `exports`, deprecated)
- `paths` aliases in published libraries (consumers cannot resolve them)

---

## 📊 Visual Diagram
```
 import x from "<specifier>"
        │
        ├── starts with ./ or ../  --> relative file lookup
        │       nodenext (ESM): needs "./x.js"        bundler: "./x" is OK
        │
        ├── matches "paths" pattern (@/*) --> mapped file   (type-level only!)
        │
        └── bare name ("express")  --> node_modules/express/package.json
                                         exports -> types -> main
                                         else node_modules/@types/express
                                         else error TS2307 / TS7016
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| moduleResolution | Lookup algorithm for imports | Imports ढूँढने का algorithm |
| nodenext | Mirrors current Node ESM/CJS rules | Node के ESM/CJS नियम |
| bundler | Mirrors bundlers (no extensions needed) | Bundler जैसे नियम |
| paths | Alias mapping, type-level only | Alias mapping (सिर्फ type स्तर पर) |
| exports map | package.json entry points | Package के entry points |
| `.mts` / `.cts` | Always-ESM / always-CJS TS files | हमेशा ESM / हमेशा CJS |

---

## ⚡ 3-Line Summary
English:
1. Pick `nodenext` when Node runs your `tsc` output, `bundler` when a bundler/Vite loads it.
2. Under `nodenext` ESM, relative imports need `.js` extensions; TS never rewrites specifiers.
3. `paths` aliases are type-only: the emitted JS still contains the alias and fails at runtime without a bundler.

Hindi:
1. Node तुम्हारा `tsc` output चलाए तो `nodenext`, bundler/Vite चलाए तो `bundler` चुनो।
2. `nodenext` ESM में relative imports पर `.js` extension चाहिए; TS specifiers नहीं बदलता।
3. `paths` aliases सिर्फ type स्तर के हैं: emitted JS में alias वैसा ही रहता है और bundler के बिना runtime पर fail होता है।

---

## ➡️ Next Topic
**73. Declaration Files (.d.ts) and @types** - How TypeScript gets types for plain JavaScript packages.
