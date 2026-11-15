# 4. tsconfig.json Basics
# हिंदी में: tsconfig.json की बुनियादी बातें

> Version note: **TypeScript 5.x** (5.9.3 पर verify)। कुछ options version पर निर्भर हैं: `moduleResolution: "bundler"` (5.0+), `verbatimModuleSyntax` (5.0+), `erasableSyntaxOnly` (5.8+), `noUncheckedSideEffectImports` (5.6+)।

---

## 🔵 Simple Definition (English)
**`tsconfig.json`** is the configuration file that tells `tsc` (and your editor) **which files belong to the project** and **how strictly and in what output format to compile them**. Its presence marks the project root. Main parts: `compilerOptions` (how), `include` / `exclude` / `files` (which files), `extends` (inherit another config) and `references` (multi-project builds).

## 🔵 सरल परिभाषा (Hindi)
**`tsconfig.json`** वह configuration file है जो `tsc` (और आपके editor) को बताती है कि **कौन सी files project का हिस्सा हैं** और **उन्हें कितनी strictness से और किस output format में compile करना है**। इसका होना project root की पहचान है। मुख्य हिस्से: `compilerOptions` (कैसे), `include` / `exclude` / `files` (कौन सी files), `extends` (दूसरा config inherit करना) और `references` (multi-project build)।

---

## 🔴 Problem it Solves
Without a config, `tsc` uses old defaults (non-strict, ES5-ish) and you would pass 15 CLI flags every time. Worse, the editor and the build could disagree about what is an error. One shared `tsconfig.json` makes the team, the IDE, CI and Docker build all behave identically. And the wrong options cause real production pain: `target: ES5` bloats bundles, `strict: false` hides null bugs, a wrong `module` setting makes Node throw `ERR_REQUIRE_ESM`.

## 🔴 यह क्यों बना? (Hindi)
Config के बिना `tsc` पुराने defaults (non-strict, ES5 जैसा) इस्तेमाल करता है और हर बार 15 CLI flags देनी पड़ेंगी। और बुरा यह कि editor और build किसी चीज़ को error मानने पर असहमत हो सकते हैं। एक shared `tsconfig.json` team, IDE, CI और Docker build सबको एक जैसा बर्ताव देता है। गलत options से production में असली दिक्कत आती है: `target: ES5` से bundle फूलता है, `strict: false` null bugs छिपाता है, गलत `module` से Node `ERR_REQUIRE_ESM` फेंकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `tsc` looks for `tsconfig.json` from the current folder **upwards** (only when you run `tsc` without file names).
Step 2 → It merges `extends` (base config) with your own `compilerOptions` (yours win).
Step 3 → It builds the file list: `files` + `include` globs − `exclude`. Defaults: include = everything under the folder, exclude = `node_modules`, `outDir`.
Step 4 → The checker uses `strict`-family flags; the emitter uses `target`, `module`, `outDir`, `sourceMap`, `declaration`.
Step 5 → The editor (VS Code) reads the **nearest** tsconfig to each file — so a file outside `include` gets a "loose" inferred project. Check with `npx tsc --showConfig`.

Key options cheat sheet:
- `target` → JS version emitted (`ES2022` for Node 18+).
- `module` + `moduleResolution` → how imports work (`nodenext` for Node ESM/CJS, `esnext` + `bundler` for Vite/webpack).
- `strict` → turns on the whole strict family. **Always true** in new code.
- `outDir` / `rootDir` → where compiled output goes / where source starts.
- `lib` → which built-in type libs exist (`DOM` for browser code, none for Node API).
- `jsx` → `react-jsx` for React 17+.
- `skipLibCheck` → skip checking `.d.ts` of dependencies (faster, avoids third-party conflicts).
- `esModuleInterop` → allows `import express from "express"` for CommonJS packages.
- `noEmit` → only check (when Vite/esbuild builds).
- `resolveJsonModule`, `sourceMap`, `declaration`, `incremental`, `isolatedModules`, `verbatimModuleSyntax`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `tsc` current folder से **ऊपर की तरफ** `tsconfig.json` ढूँढता है (सिर्फ तब जब आप file names दिए बिना `tsc` चलाएँ)।
Step 2 → `extends` (base config) और आपके `compilerOptions` को merge करता है (आपके वाले जीतते हैं)।
Step 3 → File list बनती है: `files` + `include` globs − `exclude`। Defaults: include = folder की सब files, exclude = `node_modules`, `outDir`।
Step 4 → Checker `strict` family flags इस्तेमाल करता है; emitter `target`, `module`, `outDir`, `sourceMap`, `declaration` इस्तेमाल करता है।
Step 5 → Editor (VS Code) हर file के **सबसे नज़दीकी** tsconfig को पढ़ता है — `include` से बाहर की file को "loose" inferred project मिलता है। `npx tsc --showConfig` से देखो।

---

## 🟡 Real World Example
**A Swiggy-style monorepo** has `packages/api` (Node + Express) and `packages/web` (React + Vite). A root `tsconfig.base.json` sets `strict: true`, `skipLibCheck: true`, `target: ES2022`. `api` extends it with `module: nodenext`, `outDir: dist`, `types: ["node"]`. `web` extends it with `module: esnext`, `moduleResolution: bundler`, `jsx: react-jsx`, `lib: ["ES2022","DOM","DOM.Iterable"]`, `noEmit: true`. Same strictness everywhere, different runtime assumptions per package.

## 🟡 Real Example Hindi mein
**Swiggy जैसे monorepo** में `packages/api` (Node + Express) और `packages/web` (React + Vite) हैं। Root `tsconfig.base.json` में `strict: true`, `skipLibCheck: true`, `target: ES2022` है। `api` इसे extend करके `module: nodenext`, `outDir: dist`, `types: ["node"]` जोड़ता है। `web` इसे extend करके `module: esnext`, `moduleResolution: bundler`, `jsx: react-jsx`, `lib: ["ES2022","DOM","DOM.Iterable"]`, `noEmit: true` जोड़ता है। हर जगह strictness एक जैसी, पर हर package की runtime assumptions अलग।

---

## 💻 Code Example — Basic

Backend `tsconfig.json` (Node 20, CommonJS-or-ESM decided by package.json `"type"`):

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "dist",
    "rootDir": "src",
    "sourceMap": true,
    "types": ["node"]
  },
  "include": ["src/**/*.ts"],
  "exclude": ["node_modules", "dist", "**/*.test.ts"]
}
```

What `strict: true` actually does (verified with `npx tsc --showConfig`): it enables `noImplicitAny`, `noImplicitThis`, `strictNullChecks`, `strictFunctionTypes`, `strictBindCallApply`, `strictPropertyInitialization`, `strictBuiltinIteratorReturn` (5.6+), `alwaysStrict`, `useUnknownInCatchVariables`.

```typescript
// ❌ strict-family errors — real tsc 5.9 output (flags: --strict)
// noImplicitAny
function add(a, b) {
  return a + b;
}
// error TS7006: Parameter 'a' implicitly has an 'any' type.
// error TS7006: Parameter 'b' implicitly has an 'any' type.

// strictNullChecks
const cartCoupon: string = null;
// error TS2322: Type 'null' is not assignable to type 'string'.

// strictPropertyInitialization
class Order {
  id: string;
}
// error TS2564: Property 'id' has no initializer and is not definitely assigned in the constructor.
```

## 💻 Code Example — Advanced

Flags that are **not** part of `strict` but recommended for senior projects. Real output with these flags on `noUnusedLocals`, `noImplicitReturns`, `noUncheckedIndexedAccess`:

```typescript
// extra-flags-demo.ts — compile with:
// tsc --noEmit --strict --noUnusedLocals --noImplicitReturns --noUncheckedIndexedAccess
export function total(a: number, b: number) {
  const unused = 5;          // noUnusedLocals flags this
  if (a > 0) {
    return a + b;
  }                          // noImplicitReturns: other path returns nothing
}
const idx: number[] = [1, 2];
export const v = idx[5];     // with noUncheckedIndexedAccess: type is number | undefined
```
```
src/a.ts(1,17): error TS7030: Not all code paths return a value.
src/a.ts(2,9): error TS6133: 'unused' is declared but its value is never read.
```
(The block compiles under plain `--strict`; the two errors above appear only with the extra flags. `idx[5]` becomes `number | undefined` instead of erroring.)

A monorepo layout with `extends`:

```json
// tsconfig.base.json (root)
{
  "compilerOptions": {
    "target": "ES2022",
    "strict": true,
    "skipLibCheck": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "forceConsistentCasingInFileNames": true
  }
}
```
```json
// packages/web/tsconfig.json (Vite + React)
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "module": "esnext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "noEmit": true,
    "paths": { "@/*": ["./src/*"] },
    "baseUrl": "."
  },
  "include": ["src"]
}
```

Check what you actually got:
```bash
npx tsc --showConfig        # final merged config
npx tsc --listFilesOnly     # which files are included
npx tsc --noEmit -p packages/web
```

---

## 🟠 Node/Express + React Integration

**Node/Express package** — emits CommonJS-compatible output for a Docker image:

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "module": "nodenext",
    "outDir": "dist",
    "rootDir": "src",
    "types": ["node"],
    "declaration": false,
    "sourceMap": true,
    "noEmitOnError": true
  },
  "include": ["src"]
}
```

```typescript
// src/server.ts — uses `types: ["node"]` for process, and esModuleInterop-free ESM import
import express from "express";

const app = express();
// process.env.X is string | undefined -> strict forces us to handle the missing case
const port: number = Number(process.env.PORT ?? 3000);
app.get("/ping", (_req, res) => { res.send("pong"); });
export { app, port };
```

**React + Vite** gets *two* configs from the template: `tsconfig.app.json` (browser code, `lib: DOM`) and `tsconfig.node.json` (for `vite.config.ts`, `lib` without DOM), tied by a root `tsconfig.json` using `"references"`. Mixing them is why `window` is "not defined" in config files and `process` is "not defined" in components — that separation is on purpose.

```tsx
// src/Cart.tsx — works because jsx = "react-jsx" (no `import React` needed)
export function Cart({ items }: { items: string[] }) {
  return <ul>{items.map((i) => <li key={i}>{i}</li>)}</ul>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Leaving `strict` off ("we will turn it on later")
```json
// Wrong — null/undefined bugs and implicit any remain invisible
{ "compilerOptions": { "target": "ES2022" } }
```
```json
// Right
{ "compilerOptions": { "target": "ES2022", "strict": true } }
```

❌ Mistake 2: Putting `outDir` inside `include` or forgetting `exclude: ["dist"]` — the compiler picks up its own output, giving `TS5055: Cannot write file '...' because it would overwrite input file.`
✅ Correct: keep `include: ["src"]` and `outDir: "dist"` separate.

❌ Mistake 3: Using `paths` and expecting Node to resolve it at runtime
✅ Correct: `paths` only helps the **type-checker**. Node still sees `@/utils` and crashes with `Cannot find module`. Use a bundler alias, `tsc-alias`, or `tsx` / Node `imports` field in package.json.

❌ Mistake 4: One tsconfig for both Node and browser code, so `document` compiles in the server.
✅ Correct: separate configs with different `lib` and `types`, joined via `extends`/`references`.

---

## 🧠 Tricky Interview Question

**Question:** You run `npx tsc src/index.ts` in a project that has a strict `tsconfig.json`. Why do you see no errors for code that fails in `npm run build`?

**Answer:** When you give **file names** on the command line, `tsc` **ignores `tsconfig.json` entirely** and compiles with defaults (non-strict). `npm run build` runs plain `tsc`, which reads the config. To compile specific files with the config use `tsc -p tsconfig.json` (and put the files in `include`/`files`). A related trap: `exclude` only affects the initial file list — a file excluded but `import`ed by an included file **is still compiled**.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `include`, `files` and `exclude`?
A1: `files` is an explicit list (errors if missing). `include` takes glob patterns. `exclude` removes matches from `include` only; it does not stop a file that is imported. All paths are relative to the tsconfig.

Q2: What does `strict: true` enable, and can I override individual flags?
A2: It enables a family: `noImplicitAny`, `strictNullChecks`, `strictFunctionTypes`, `strictBindCallApply`, `strictPropertyInitialization`, `noImplicitThis`, `useUnknownInCatchVariables`, `alwaysStrict`, `strictBuiltinIteratorReturn`. You can write `"strict": true, "strictPropertyInitialization": false` to opt out of one. New TS versions can add flags to `strict`, which may produce new errors on upgrade.

Q3: `target` vs `lib` vs `module`?
A3: `target` is the JS syntax level emitted (arrow functions, optional chaining downleveled if too low). `lib` is which built-in **type** declarations exist (e.g. `Promise.allSettled`, `DOM`) — TS does not polyfill. `module` is the module format emitted (`commonjs`, `esnext`, `nodenext`).

Q4: When would you choose `moduleResolution: "bundler"` over `"nodenext"`?
A4: `bundler` (TS 5.0+) is for code processed by Vite/webpack/esbuild: it allows extensionless relative imports and supports `exports` in package.json. `nodenext` mirrors real Node ESM/CJS rules (explicit `.js` extensions in ESM). Use nodenext for plain Node services, bundler for frontends.

Q5: What are `extends` and `references`?
A5: `extends` inherits compilerOptions from another file (shared base; arrays like `include` are replaced not merged). `references` splits a repo into composite sub-projects compiled in order with `tsc -b`, enabling incremental builds (topic 075).

---

## 🔷 When to Use + When Not to Use
✅ Use / tune when:
- Always create a tsconfig; use `extends` for monorepos and `skipLibCheck` for speed
- Use separate configs for app, node tooling, and tests

❌ Avoid when:
- Don't copy a giant commented tsconfig you do not understand — each flag is a maintenance cost
- Don't switch `strict` off to "fix" errors; fix the code or use targeted `// @ts-expect-error` with a reason

---

## 📊 Visual Diagram
```
 tsconfig.json
 ├── extends ──────────► tsconfig.base.json (shared strict rules)
 ├── compilerOptions
 │     ├── CHECK : strict, noUncheckedIndexedAccess, noUnusedLocals
 │     ├── EMIT  : target, module, outDir, sourceMap, declaration
 │     └── ENV   : lib, types, jsx, moduleResolution, paths
 ├── include / exclude / files ──► which .ts files join the program
 └── references ───────────► other sub-projects (tsc -b)

 Node service:  module=nodenext   types=[node]   lib=ES2022
 React app   :  module=esnext + bundler   jsx=react-jsx   lib=DOM
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| compilerOptions | Settings controlling check and emit | Check और emit के settings |
| include/exclude | File selection globs | File चुनने के patterns |
| extends | Inherit another tsconfig | दूसरे tsconfig से inherit |
| strict | Bundle of strict checks | Strict checks का समूह |
| target | Emitted JS version | Emit होने वाला JS version |
| moduleResolution | How import paths are found | Import path ढूँढने का तरीका |
| skipLibCheck | Don't type-check .d.ts files | .d.ts files check मत करो |

---

## ⚡ 3-Line Summary
English:
1. `tsconfig.json` defines which files compile and with what strictness/output; use `strict: true` always.
2. Match `module`/`moduleResolution`/`lib`/`types` to the runtime (Node vs bundler vs browser) and share a base via `extends`.
3. `tsc file.ts` ignores tsconfig, `paths` is type-only, and `exclude` does not block imported files.

Hindi:
1. `tsconfig.json` तय करता है कौन सी files compile होंगी और कितनी strictness/output से; हमेशा `strict: true` रखो।
2. `module`/`moduleResolution`/`lib`/`types` को runtime (Node / bundler / browser) के हिसाब से रखो और `extends` से base share करो।
3. `tsc file.ts` tsconfig को ignore करता है, `paths` सिर्फ type के लिए है, और `exclude` imported files को नहीं रोकता।

---

## ➡️ Next Topic
**005. Primitive Types (string, number, boolean, bigint, symbol)** — the building blocks of every type.
