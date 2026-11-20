# 75. Project References and Incremental Builds
# हिंदी में: Project References और Incremental Builds

> Verified with TypeScript 5.9 (`tsc -b`) on a real 2-package monorepo. `composite` + `references` = TS 3.0, `tsc -b` = TS 3.0, `incremental` = TS 3.4. `tsc -b` ("build mode") is the only mode that understands references.

---

## 🔵 Simple Definition (English)
**Project references** let you split one big TypeScript codebase into **several smaller tsconfig projects** that depend on each other (`"references": [{ "path": "../shared" }]`). **`tsc --build` (`tsc -b`)** builds them in dependency order and **only rebuilds what changed** using `.tsbuildinfo` files (**incremental builds**). A referenced project must set `composite: true`, which forces `declaration` output and a predictable file list.

## 🔵 सरल परिभाषा (Hindi)
**Project references** से एक बड़े TypeScript codebase को **कई छोटे tsconfig projects** में बाँटा जाता है जो एक-दूसरे पर निर्भर होते हैं (`"references": [{ "path": "../shared" }]`)। **`tsc --build` (`tsc -b`)** उन्हें dependency के क्रम में build करता है और `.tsbuildinfo` files से **सिर्फ वही दोबारा build करता है जो बदला** (**incremental builds**)। जिस project को reference किया जाए उसमें `composite: true` ज़रूरी है, जो `declaration` output और तय file list लागू करता है।

---

## 🔴 Problem it Solves
In a monorepo (shared types + Express API + worker + React admin) a single giant `tsc` run re-checks **every file** on every change - minutes for large repos, slow editor startup, and nothing stops the API from importing private files from the React app. Project references give you: (1) **faster builds** (unchanged projects are skipped), (2) **faster editor** (the language server reads the small `.d.ts` outputs of referenced projects instead of re-checking their source), and (3) **enforced boundaries** (a project can only import from projects it references).

## 🔴 यह क्यों बना? (Hindi)
Monorepo में (shared types + Express API + worker + React admin) एक बड़ा `tsc` हर बदलाव पर **हर file** दोबारा check करता है - बड़े repos में मिनटों का समय, editor धीरे खुलता है, और API को React app की private files import करने से कोई नहीं रोकता। Project references देते हैं: (1) **तेज़ builds** (न बदले projects छूट जाते हैं), (2) **तेज़ editor** (language server referenced projects का source नहीं, उनके छोटे `.d.ts` outputs पढ़ता है), और (3) **सीमाओं का पालन** (project सिर्फ उन्हीं projects से import कर सकता है जिन्हें वह reference करता है)।

---

## 🟢 How it Works — Step by Step

Step 1 → Make a shared base config (`tsconfig.base.json`) with `composite: true`, `declaration: true`, strict flags.
Step 2 → Each package has its own `tsconfig.json` that `extends` the base and sets `rootDir`, `outDir`, `include`.
Step 3 → A package that depends on another lists it under `"references": [{ "path": "../shared" }]`.
Step 4 → A root `tsconfig.json` with `"files": []` and `references` to every package is the "solution" file.
Step 5 → Run `tsc -b` (or `tsc -b packages/api`). TS builds `shared` first, writes `dist/*.js`, `dist/*.d.ts` and `tsconfig.tsbuildinfo`, then builds `api` against shared's `.d.ts`.
Step 6 → Second `tsc -b` with no changes prints "up to date" and does almost nothing. Change only a function **body** in `shared` and `api` is not recompiled (its `.d.ts` did not change - it just gets its timestamps updated).
Step 7 → Useful flags: `-v` (verbose reasons), `--clean` (delete outputs), `--force` (rebuild all), `-w` (watch).
Step 8 → For a **single** project use `"incremental": true` (or `composite`) to get a `.tsbuildinfo` cache without references.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → एक साझा base config (`tsconfig.base.json`) बनाओ जिसमें `composite: true`, `declaration: true` और strict flags हों।
Step 2 → हर package की अपनी `tsconfig.json` होती है जो base को `extends` करती है और `rootDir`, `outDir`, `include` तय करती है।
Step 3 → जो package दूसरे पर निर्भर है वह उसे `"references": [{ "path": "../shared" }]` में लिखता है।
Step 4 → Root `tsconfig.json` में `"files": []` और हर package का `references` - यही "solution" file है।
Step 5 → `tsc -b` (या `tsc -b packages/api`) चलाओ। TS पहले `shared` build करता है, `dist/*.js`, `dist/*.d.ts` और `tsconfig.tsbuildinfo` लिखता है, फिर `api` को shared के `.d.ts` के against build करता है।
Step 6 → बिना बदलाव दूसरा `tsc -b` "up to date" बताता है और लगभग कुछ नहीं करता। `shared` में सिर्फ function की **body** बदलो तो `api` दोबारा compile नहीं होता (उसका `.d.ts` नहीं बदला - सिर्फ timestamps update होते हैं)।
Step 7 → काम के flags: `-v` (कारण दिखाओ), `--clean` (outputs मिटाओ), `--force` (सब दोबारा), `-w` (watch)।
Step 8 → **अकेले** project के लिए `"incremental": true` (या `composite`) से references के बिना `.tsbuildinfo` cache मिलता है।

---

## 🟡 Real World Example
**A Razorpay-style monorepo**: `packages/shared` (Money, Order DTOs, Zod schemas), `packages/api` (Express + SQL Server), `packages/web` (React admin, Vite). `api` and `web` both reference `shared`; `web` does **not** reference `api`, so nobody can accidentally import server code (SQL credentials!) into the browser bundle. CI runs `tsc -b` and caches the `*.tsbuildinfo`/`dist` folders, cutting type-check time on pull requests dramatically.

## 🟡 Real Example Hindi mein
**Razorpay-जैसा monorepo**: `packages/shared` (Money, Order DTOs, Zod schemas), `packages/api` (Express + SQL Server), `packages/web` (React admin, Vite)। `api` और `web` दोनों `shared` को reference करते हैं; `web`, `api` को reference **नहीं** करता, इसलिए कोई गलती से server code (SQL credentials!) browser bundle में import नहीं कर सकता। CI में `tsc -b` चलता है और `*.tsbuildinfo`/`dist` folders cache होते हैं, जिससे pull requests पर type-check का समय बहुत घट जाता है।

---

## 💻 Code Example — Basic

Folder layout (real project used for the verification):

```text
q75/
├── package.json                 {"type":"module"}
├── tsconfig.base.json           shared options (composite, declaration, strict)
├── tsconfig.json                solution file: files:[] + references
└── packages/
    ├── shared/
    │   ├── package.json         name "@shop/shared", exports -> dist
    │   ├── tsconfig.json
    │   └── src/money.ts
    └── api/
        ├── package.json
        ├── tsconfig.json        references ../shared
        └── src/main.ts
```

```json
// tsconfig.base.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "strict": true,
    "skipLibCheck": true,
    "types": [],
    "declaration": true,
    "composite": true
  }
}
```

```json
// tsconfig.json  (solution file - builds nothing itself)
{ "files": [], "references": [{ "path": "packages/shared" }, { "path": "packages/api" }] }
```

```json
// packages/api/tsconfig.json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": { "rootDir": "src", "outDir": "dist" },
  "include": ["src"],
  "references": [{ "path": "../shared" }]
}
```

```typescript
// packages/shared/src/money.ts - the shared project
export interface Money { paise: number } // DTO used by api AND web
export const toRupees = (m: Money): string => `Rs.${(m.paise / 100).toFixed(2)}`; // helper
console.log(toRupees({ paise: 12345 })); // Rs.123.45
```

## 💻 Code Example — Advanced

Real `tsc -b` session on that project (outputs are copy-pasted):

```text
$ tsc -b -v        # first build
Project 'packages/shared/tsconfig.json' is out of date because output file 'packages/shared/tsconfig.tsbuildinfo' does not exist
Building project '.../packages/shared/tsconfig.json'...
Project 'packages/api/tsconfig.json' is out of date because output file 'packages/api/tsconfig.tsbuildinfo' does not exist
Building project '.../packages/api/tsconfig.json'...

$ node packages/api/dist/main.js
Rs.123.45

$ tsc -b -v        # nothing changed
Project 'packages/shared/tsconfig.json' is up to date because newest input 'packages/shared/src/money.ts' is older than output 'packages/shared/tsconfig.tsbuildinfo'
Project 'packages/api/tsconfig.json' is up to date because newest input 'packages/api/src/main.ts' is older than output 'packages/api/tsconfig.tsbuildinfo'

$ (edit only the body of toRupees: toFixed(2) -> toFixed(1)) && tsc -b -v
Project 'packages/shared/tsconfig.json' is out of date because output '...tsbuildinfo' is older than input 'packages/shared/src/money.ts'
Building project '.../packages/shared/tsconfig.json'...
Project 'packages/api/tsconfig.json' is up to date with .d.ts files from its dependencies   <-- api NOT recompiled
Updating output timestamps of project '.../packages/api/tsconfig.json'...
```

If `shared` has a type error, the build stops there (real output):

```text
$ tsc -b
packages/shared/src/money.ts(3,14): error TS2322: Type 'string' is not assignable to type 'number'.
```

The `api` code using the referenced project (imports by package name, resolved through `node_modules/@shop/shared` created by npm/pnpm workspaces):

```text
// packages/api/src/main.ts
import { toRupees } from "@shop/shared";
console.log(toRupees({ paise: 12345 }));
// Before shared is built (real): error TS2307: Cannot find module '@shop/shared' or its corresponding type declarations.
// After `tsc -b`: compiles and prints Rs.123.45
```

Single project, no references - just caching:

```json
{ "compilerOptions": { "incremental": true, "tsBuildInfoFile": ".cache/app.tsbuildinfo" } }
```

---

## 🟠 Node/Express + React Integration

```json
// packages/web/tsconfig.json - React app (Vite bundles; tsc only type-checks/emits .d.ts). Verified: tsc -b built it.
// With Vite installed, use "types": ["vite/client"].
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "module": "esnext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "emitDeclarationOnly": true,
    "outDir": "dist-types",
    "rootDir": "src",
    "types": []
  },
  "include": ["src"],
  "references": [{ "path": "../shared" }]
}
```

```typescript
// packages/shared/src/order.ts - ONE definition used by Express and React
export interface OrderDTO {
  id: string; // order id
  paise: number; // amount in paise
  status: "PLACED" | "PAID" | "SHIPPED"; // limited statuses
}

export const isPaid = (o: OrderDTO): boolean => o.status === "PAID"; // shared rule
console.log(isPaid({ id: "o1", paise: 100, status: "PAID" })); // true
```

```text
// root package.json scripts
"build":     "tsc -b",            // builds shared -> api -> web in order
"typecheck": "tsc -b"             // a composite build already type-checks; --noEmit is rejected (mistake 5)
"clean":     "tsc -b --clean"
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Referencing a project that is not `composite`
```text
packages/api/tsconfig.json(1,161): error TS6306: Referenced project '.../packages/web' must have setting "composite": true.
```
(Real output - `web` had no `composite`.) ✅ Fix: set `composite: true` in every referenced project (usually via the base config).

❌ Mistake 2: Importing another project's `src` by relative path instead of through the reference
```text
packages/api/src/main.ts(1,26): error TS6059: File '.../packages/shared/src/money.ts' is not under 'rootDir' '.../packages/api/src'. 'rootDir' is expected to contain all source files.
packages/api/src/main.ts(1,26): error TS6307: File '.../packages/shared/src/money.ts' is not listed within the file list of project '.../packages/api/tsconfig.json'. Projects must list all files or use an 'include' pattern.
```
(Real output with `import "../../shared/src/money.js"` and no reference.) ✅ Fix: import by package name (`@shop/shared` through workspaces) and add the `references` entry. Even with a reference, a relative `src` import runs the TS file at runtime, not the built JS, which Node cannot load (`ERR_MODULE_NOT_FOUND ... shared/src/money.js`).

❌ Mistake 3: Running plain `tsc -p packages/api` and expecting dependencies to be built
Real output: `error TS2307: Cannot find module '@shop/shared'` because `shared/dist` did not exist yet. Always use `tsc -b`, which builds references first.

❌ Mistake 4: Committing `dist` / `*.tsbuildinfo` to git
They are build artefacts; add them to `.gitignore` and cache them in CI instead.

❌ Mistake 5: Using `--noEmit` with `tsc -b` on referenced projects
```text
packages/api/tsconfig.json(1,136): error TS6310: Referenced project '.../packages/shared' may not disable emit.
```
(Real output.) Composite projects must emit declarations; use `emitDeclarationOnly` for pure type-check packages (React apps compiled by Vite).

---

## 🧠 Tricky Interview Question

Q: You change the body of a function in `shared` (no signature change). Does `api` get recompiled when you run `tsc -b`? And if you add a parameter?

Answer: Body-only change: `shared` is rebuilt, but TS sees that its emitted `.d.ts` is unchanged and **does not recompile `api`**; it only touches its output timestamps (real log line: "up to date with .d.ts files from its dependencies"). Adding a parameter changes the `.d.ts`, so `api` is out of date and gets rebuilt and re-checked. This is why public API signatures should be explicit (also good for `isolatedDeclarations`, TS 5.5): fewer accidental `.d.ts` changes means fewer rebuilds.

---

## ⚫ Interview Questions + Answers

Q1: What does `composite: true` do?
A1: It enables features needed for references: forces `declaration: true`, enables `incremental`, requires that all files are matched by `include`/`files`, and makes `rootDir` default to the config's directory.

Q2: `tsc` vs `tsc -b`?
A2: `tsc -p` checks one project and does not build references. `tsc -b` builds referenced projects first, in order, skipping up-to-date ones.

Q3: `incremental` vs project references?
A3: `incremental` caches information (`.tsbuildinfo`) for **one** project to speed re-runs. References split the codebase into multiple projects with enforced dependencies; each of them also uses incremental caching.

Q4: Do references replace a bundler or Turborepo/Nx?
A4: No. They only handle type-checking/emit with `tsc`. Task runners (Turborepo, Nx) add caching across tools (lint, test, bundle) and can call `tsc -b`.

Q5: Why must the root solution `tsconfig.json` have `"files": []`?
A5: So it does not compile any source itself (otherwise it would include everything under it with default settings); it only lists projects for `tsc -b`, and editors use it to discover projects.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Monorepo with shared types, API, worker, web
- Type-check time or editor startup is slow
- You want to forbid some packages from importing others

❌ Avoid when:
- A small single-package app: plain `incremental: true` is enough
- Your bundler/test runner already does all type-checking via another mechanism and you never run `tsc`

---

## 📊 Visual Diagram
```
 tsc -b
   │
   ├── packages/shared  (composite)  ──► dist/*.js  dist/*.d.ts  tsconfig.tsbuildinfo
   │         ▲  ▲
   │         │  └────────────────────────────┐
   ├── packages/api  (references shared) ──► uses shared's .d.ts, never its src
   └── packages/web  (references shared) ──► emitDeclarationOnly

   Edit shared body only → shared rebuilt → .d.ts same → api skipped ✔
   Edit shared signature → .d.ts changes   → api rebuilt ✔
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Project reference | `references` entry to another tsconfig | दूसरे tsconfig की ओर reference |
| `composite` | Required for referenced projects | Reference होने के लिए ज़रूरी setting |
| `tsc -b` | Build mode, builds in dependency order | Dependency क्रम में build |
| `.tsbuildinfo` | Cache file for incremental builds | Incremental build का cache |
| Solution file | Root tsconfig with `files: []` + references | सिर्फ references वाली root tsconfig |
| `emitDeclarationOnly` | Emit only `.d.ts` | सिर्फ `.d.ts` बनाना |

---

## ⚡ 3-Line Summary
English:
1. Split a monorepo into composite projects linked by `references`; build them with `tsc -b`.
2. `.tsbuildinfo` makes rebuilds incremental: unchanged projects, and dependants of body-only changes, are skipped.
3. Import across projects by package name, not relative `src` paths; errors TS6306/TS6059/TS6307 mean config or boundary mistakes.

Hindi:
1. Monorepo को `references` से जुड़े composite projects में बाँटो; `tsc -b` से build करो।
2. `.tsbuildinfo` rebuild को incremental बनाता है: न बदले projects और सिर्फ body बदलने पर उन पर निर्भर projects छूट जाते हैं।
3. Projects के बीच package नाम से import करो, relative `src` path से नहीं; TS6306/TS6059/TS6307 errors config या सीमा की गलती बताते हैं।

---

## ➡️ Next Topic
**76. Running TS - ts-node, tsx, swc, esbuild** - Executing TypeScript directly without a separate build step, and what each tool skips.
