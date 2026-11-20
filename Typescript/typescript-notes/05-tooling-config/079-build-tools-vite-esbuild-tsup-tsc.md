# 79. Build Tools — Vite, esbuild, tsup, tsc
# हिंदी में: Build Tools — Vite, esbuild, tsup, tsc

> Verified with **TypeScript 5.9.x**, esbuild 0.2x, tsup 8, Vite 5/6/7 config typings. `verbatimModuleSyntax` / `moduleResolution: "bundler"` need TS 5.0+.

---

## 🔵 Simple Definition (English)
A **build tool** turns your TypeScript source into runnable JavaScript. `tsc` is the official compiler and the **only** one that fully type-checks. **esbuild** (Go) and **swc** (Rust) are ultra-fast transpilers that just **erase types** without checking them. **tsup** wraps esbuild for libraries (also emits `.d.ts`). **Vite** is a dev server + bundler for frontends (esbuild in dev, Rollup/Rolldown in prod).

## 🔵 सरल परिभाषा (Hindi)
**Build tool** आपके TypeScript source को चलने लायक JavaScript में बदलता है। `tsc` official compiler है और **अकेला** है जो पूरा type-check करता है। **esbuild** (Go) और **swc** (Rust) बहुत तेज़ transpilers हैं जो बस types **हटा देते** हैं, check नहीं करते। **tsup** esbuild को libraries के लिए wrap करता है (`.d.ts` भी बनाता है)। **Vite** frontend के लिए dev server + bundler है।

---

## 🔴 Problem it Solves
Browsers and Node cannot run `.ts`. Plain `tsc` is slow on big monorepos and does not bundle (no tree-shaking, no CSS/asset handling, no dev server with HMR). Teams need: instant dev feedback, small prod bundles, and `.d.ts` for libraries — plus a **separate** type-check step, because the fast tools skip it.

## 🔴 यह क्यों बना? (Hindi)
Browser और Node `.ts` नहीं चला सकते। बड़े monorepo में सिर्फ `tsc` धीमा है और bundle भी नहीं करता (tree-shaking, CSS/assets, HMR वाला dev server नहीं)। Teams को चाहिए: तुरंत dev feedback, छोटे prod bundles, libraries के लिए `.d.ts` — और एक **अलग** type-check step, क्योंकि तेज़ tools इसे skip करते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → **Transpile**: strip types, downlevel syntax per `target` (esbuild/swc/tsc all do this).
Step 2 → **Type-check**: only `tsc --noEmit` (or `vue-tsc`, IDE) does this. esbuild/Vite/tsup never report type errors.
Step 3 → **Bundle** (optional): follow imports, merge into few files, tree-shake, minify (esbuild, Rollup, Vite).
Step 4 → **Emit declarations**: `tsc --emitDeclarationOnly` or `tsup --dts` generate `.d.ts` for library consumers.
Step 5 → **Wire scripts**: `dev` = Vite/tsx, `build` = bundler, `typecheck` = `tsc --noEmit`, run all three in CI.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Transpile**: types हटाओ और `target` के हिसाब से syntax नीचे करो (esbuild/swc/tsc सब करते हैं)।
Step 2 → **Type-check**: सिर्फ `tsc --noEmit` (या IDE) करता है। esbuild/Vite/tsup कभी type error नहीं बताते।
Step 3 → **Bundle** (optional): imports follow करो, कुछ files में जोड़ो, tree-shake, minify।
Step 4 → **Declarations emit**: library users के लिए `tsc --emitDeclarationOnly` या `tsup --dts` से `.d.ts` बनाओ।
Step 5 → **Scripts जोड़ो**: `dev` = Vite/tsx, `build` = bundler, `typecheck` = `tsc --noEmit`; CI में तीनों चलाओ।

---

## 🟡 Real World Example
A **Swiggy-style monorepo**: the React web app uses **Vite** (HMR in dev, Rollup bundle in prod); the shared `@acme/pricing` package (delivery fee, GST calculators) is built with **tsup** into ESM + CJS + `.d.ts`; the Express API runs through **tsc** into `dist/` for Azure App Service. CI runs `tsc --noEmit` on all three, because Vite and tsup would happily ship a type error.

## 🟡 Real Example Hindi mein
**Swiggy जैसा monorepo**: React web app **Vite** से (dev में HMR, prod में Rollup bundle); shared `@acme/pricing` package (delivery fee, GST calculators) **tsup** से ESM + CJS + `.d.ts` में; Express API **tsc** से `dist/` में, Azure App Service के लिए। CI तीनों पर `tsc --noEmit` चलाता है, क्योंकि Vite और tsup type error को भी खुशी से ship कर देंगे।

---

## 💻 Code Example — Basic

```typescript
// build-esbuild.ts — a tiny esbuild build script, typed by esbuild's own types
import { build, type BuildOptions } from "esbuild"; // `type` import is erased at runtime

// Options object is checked against esbuild's BuildOptions interface
const options: BuildOptions = {
  entryPoints: ["src/server.ts"], // start file of the API
  outfile: "dist/server.js",      // single bundled output file
  bundle: true,                   // inline imported local modules
  platform: "node",               // target Node (do not polyfill browser APIs)
  target: "node20",               // match your Azure runtime
  format: "esm",                  // output ES modules
  sourcemap: true,                // emit dist/server.js.map (see topic 78)
  packages: "external",           // do not bundle node_modules, require them at runtime
};

// Run the build; errors from esbuild are SYNTAX errors, never TYPE errors
build(options).then(() => console.log("build ok")); // prints: build ok
```

```typescript
// ❌ esbuild does NOT type-check. This file builds fine with esbuild, but tsc rejects it.
const total: number = "499"; // wrong type on purpose
console.log(total);
// tsc --noEmit  →  error TS2322: Type 'string' is not assignable to type 'number'.
// esbuild a.ts  →  (real output, no error at all)
//   const total = "499";
//   console.log(total);
```

```json
// package.json scripts — the standard trio
{
  "scripts": {
    "dev": "tsx watch src/server.ts",
    "build": "node --import tsx build-esbuild.ts",
    "typecheck": "tsc --noEmit"
  }
}
```

## 💻 Code Example — Advanced

```typescript
// tsup.config.ts — build a shared library (ESM + CJS + .d.ts)
import { defineConfig } from "tsup"; // typed helper gives autocomplete + checks

export default defineConfig({
  entry: ["src/index.ts"],      // library public entry
  format: ["esm", "cjs"],       // dual package: import and require both work
  dts: true,                    // generate index.d.ts (uses the TS compiler API, slower, but needed)
  sourcemap: true,              // ship maps
  clean: true,                  // wipe dist/ before building
  treeshake: true,              // drop unused exports
  target: "es2022",             // output syntax level
  external: ["react"],          // peer dependency: never bundle it
});
```

```typescript
// vite.config.ts — React + TS app with an API proxy to Express
import { defineConfig } from "vite"; // typed config helper

export default defineConfig({
  server: {
    port: 5173, // dev server port
    proxy: {
      // browser calls /api/* → forwarded to Express, avoids CORS in dev
      "/api": { target: "http://localhost:4000", changeOrigin: true },
    },
  },
  build: {
    target: "es2022",     // modern browsers
    sourcemap: "hidden",  // maps for Sentry, not linked in bundle
    outDir: "dist",       // static files for Azure Static Web Apps
  },
  esbuild: {
    drop: ["console", "debugger"], // strip console.* from prod bundle
  },
});
```

```json
// tsconfig.json for a Vite app — "noEmit" because Vite does the emitting
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",   // TS 5.0+ : matches how bundlers resolve imports
    "verbatimModuleSyntax": true,    // TS 5.0+ : force `import type` where needed (esbuild-safe)
    "isolatedModules": true,         // each file must be transpilable alone (required for esbuild/swc)
    "noEmit": true,                  // tsc only checks
    "jsx": "react-jsx",
    "strict": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}
```

---

## 🟠 Node/Express + React Integration

```typescript
// src/api/server.ts — Express API compiled by plain tsc (simple, type-checked, no bundler)
import express from "express"; // default import (esModuleInterop-style)

const app = express(); // create app
app.use(express.json()); // parse JSON bodies

app.get("/health", (_req, res) => {
  res.json({ ok: true }); // used by Azure health probe
});

const port = Number(process.env.PORT ?? 4000); // PORT from Azure or default
app.listen(port, () => console.log(`API on ${port}`)); // start server
```

```typescript
// src/web/main.tsx — React entry, bundled by Vite
import { createRoot } from "react-dom/client"; // React 18 root API

// `!`: index.html always has #root (see topic 20 on the non-null assertion)
const root = createRoot(document.getElementById("root")!);
root.render(<h1>Swiggy Clone</h1>); // JSX is compiled by esbuild inside Vite
```

**Rule of thumb:** Node service → `tsc` (or `tsx` in dev). Library → `tsup`. Web app → `Vite`. All three → add `tsc --noEmit` in CI.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Relying on `vite build` or `tsup` to catch type errors.
✅ Add `"typecheck": "tsc --noEmit"` and run it in CI before build (many teams use `vite build && tsc --noEmit` or `tsc -b && vite build`).

❌ Mistake 2: `isolatedModules` off, then `export { SomeType } from "./types"` breaks under esbuild (it cannot know SomeType is a type).
```typescript
// ❌ re-exporting a type without `type` — a single-file transpiler cannot know Order is a type
export { Order } from "./order-types";
// real tsc output with --isolatedModules:
// error TS1205: Re-exporting a type when 'isolatedModules' is enabled requires using 'export type'.

// ✅ Right: mark it; erased safely, esbuild-friendly
// export type { Order } from "./order-types";
```

❌ Mistake 3: Using `const enum` or `namespace` merging across files with esbuild/swc — single-file transpile cannot inline cross-file `const enum`.
✅ Use plain `enum`, `as const` objects, or string unions (topic 16).

❌ Mistake 4: Bundling `node_modules` into a Node service by accident (huge file, native-module crashes).
✅ `packages: "external"` (esbuild) or `external: [...]` (tsup).

---

## 🧠 Tricky Interview Question
**Q:** "Your Vite build is green, but production shows `undefined is not a function`. `tsc --noEmit` fails locally with 11 errors. Why was the build green, and what is the correct pipeline?"

**A:** Vite (esbuild) only **strips** types — it never runs the type checker, so a type error cannot fail the build. Correct pipeline: `tsc --noEmit` (or `tsc -b`) **first**, then `vite build`; in CI make type-check a required step. For libraries, also let `tsup --dts` or `tsc --emitDeclarationOnly` produce declarations, and enable `isolatedModules` so the fast transpiler and tsc agree on what is a type-only import.

---

## ⚫ Interview Questions + Answers

Q1: Why is esbuild so much faster than tsc?
A1: It is written in Go, parallel, and does a single-file transform with no type analysis. tsc must build the whole program graph and resolve types across files.

Q2: When do you choose tsup over Vite?
A2: tsup is for **libraries/CLIs** (multiple formats, `.d.ts`, no HTML/dev server). Vite is for **applications** with an HTML entry, HMR, and asset handling (Vite also has a library mode).

Q3: What does `isolatedModules` guarantee?
A3: Every file can be transpiled without information from other files. It forbids things like re-exporting types without `type`, and `const enum` use across files — exactly what esbuild/swc cannot handle.

Q4: What does `moduleResolution: "bundler"` change?
A4: (TS 5.0+) It allows extensionless relative imports and `exports`/`imports` in package.json like a bundler does, without requiring `.js` extensions as `node16/nodenext` does. Use it with `noEmit` + a bundler, not for code that runs directly in Node.

Q5: How do you ship types for a library built with tsup?
A5: `dts: true` in `tsup.config.ts`, and in `package.json` set `"types"`, and `"exports": { ".": { "import": {...}, "require": {...} } }` pointing at `.mjs/.js` + `.d.ts/.d.cts` files for each condition.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- `tsc` for Node services you can compile straight to `dist/` and for the CI type-check
- `Vite` for React apps; `tsup` for shared packages; `esbuild` for custom scripts/Lambda bundles

❌ Avoid when:
- You use decorators with `emitDecoratorMetadata` (NestJS) — esbuild does not emit metadata; use `tsc` or swc
- You think a fast bundler replaces type-checking — it does not

---

## 📊 Visual Diagram
```
                 ┌────────────── type-check? ──────────────┐
 .ts source ──►  │ tsc          YES  (emit optional)       │
                 │ esbuild/swc  NO   (strip types, FAST)   │
                 │ tsup         NO   (esbuild) +dts via tsc│
                 │ Vite         NO   (esbuild dev, Rollup)  │
                 └──────────────────────────────────────────┘
 CI pipeline:   tsc --noEmit  ─►  vite build / tsup / tsc  ─►  deploy
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Transpile | Convert TS to JS | TS को JS में बदलना |
| Bundle | Merge modules into few files | Modules को कुछ files में जोड़ना |
| Tree-shaking | Drop unused exports | Unused code हटाना |
| `isolatedModules` | Each file compiles alone | हर file अकेली compile हो सके |
| `noEmit` | Check only, write nothing | सिर्फ check, output नहीं |
| HMR | Hot Module Replacement | बिना reload के live update |
| `.d.ts` | Declaration (types-only) file | सिर्फ types वाली file |

---

## ⚡ 3-Line Summary
English:
1. Only `tsc` type-checks; esbuild, swc, tsup and Vite just strip types fast.
2. Apps → Vite, libraries → tsup, Node services → tsc/tsx, and always run `tsc --noEmit` in CI.
3. Turn on `isolatedModules` + `verbatimModuleSyntax` so fast transpilers and tsc agree.

Hindi:
1. सिर्फ `tsc` type-check करता है; esbuild, swc, tsup और Vite बस तेज़ी से types हटाते हैं।
2. Apps → Vite, libraries → tsup, Node services → tsc/tsx, और CI में हमेशा `tsc --noEmit` चलाओ।
3. `isolatedModules` + `verbatimModuleSyntax` चालू रखो ताकि तेज़ transpilers और tsc एक जैसा समझें।

---

## ➡️ Next Topic
**80. Migrating a JS Project to TypeScript** — step-by-step `allowJs` → `checkJs` → strict plan for a real Express codebase.
