# 77. ESLint + typescript-eslint
# हिंदी में: ESLint + typescript-eslint (compiler से आगे की bugs पकड़ना)

> Verified with ESLint 10.x (flat config `eslint.config.mjs`), typescript-eslint 8.x, TypeScript 5.9. `projectService` option = typescript-eslint 8 (stable); `tseslint.config()` helper and flat config work from ESLint 9 onward. Old `.eslintrc` is legacy.

---

## 🔵 Simple Definition (English)
**ESLint** is a static analysis tool that applies **rules** to your code to find bugs and style issues. **typescript-eslint** is the plugin + parser that lets ESLint understand TypeScript, and - most importantly - run **type-aware rules** (they ask the TypeScript compiler for the types) such as `no-floating-promises`, `no-misused-promises` and `no-unsafe-*`. `tsc` answers "is this type-correct?"; ESLint answers "is this **safe, consistent and idiomatic**?" Both run in CI.

## 🔵 सरल परिभाषा (Hindi)
**ESLint** एक static analysis tool है जो आपके code पर **rules** लगाकर bugs और style की गलतियाँ ढूँढता है। **typescript-eslint** वह plugin + parser है जिससे ESLint TypeScript समझता है, और सबसे ज़रूरी - **type-aware rules** चला सकता है (ये TypeScript compiler से types पूछते हैं), जैसे `no-floating-promises`, `no-misused-promises` और `no-unsafe-*`। `tsc` पूछता है "क्या यह type के हिसाब से सही है?"; ESLint पूछता है "क्या यह **सुरक्षित, एक-सा और idiomatic** है?" दोनों CI में चलते हैं।

---

## 🔴 Problem it Solves
The compiler accepts a lot of **legal but dangerous** code: a forgotten `await` (the payment promise rejects and nobody sees it), an `async` function passed to `forEach` (errors vanish), `any` spreading through the codebase, `||` instead of `??` (a `0` coupon discount treated as missing), `!` non-null assertions. These are exactly the bugs that reach production in Node/Express code. typescript-eslint rules close this gap and enforce team conventions (`import type`, naming, no unused variables).

## 🔴 यह क्यों बना? (Hindi)
Compiler बहुत सा **वैध पर खतरनाक** code स्वीकार कर लेता है: भूला हुआ `await` (payment का promise reject होता है और किसी को पता नहीं चलता), `forEach` में दिया गया `async` function (errors गायब), पूरे codebase में फैलता `any`, `??` की जगह `||` (`0` discount को "नहीं है" मान लेना), `!` non-null assertions। Node/Express code में production तक पहुँचने वाले bugs ठीक यही होते हैं। typescript-eslint के rules यह अंतर भरते हैं और team conventions (`import type`, naming, unused variables) लागू करते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Install: `npm i -D eslint @eslint/js typescript-eslint` (typescript is already there).
Step 2 → Create `eslint.config.mjs` (flat config): start from `eslint.configs.recommended`, then spread a typescript-eslint preset.
Step 3 → Pick a preset: `recommended` (safe, few rules) -> `strict` (more opinionated) -> `*TypeChecked` variants (add type-aware rules) -> `stylistic*`. Senior teams usually use `strictTypeChecked` + `stylisticTypeChecked`.
Step 4 → Turn on typed linting with `languageOptions.parserOptions.projectService: true` (+ `tsconfigRootDir`). ESLint then uses the same program as the editor, so files must be covered by a tsconfig.
Step 5 → Override rules per team: `"@typescript-eslint/consistent-type-imports": "error"`, relax rules for test files with `files: ["**/*.test.ts"]`.
Step 6 → Run `npx eslint .` in CI (and in the editor via the ESLint extension). `--fix` auto-fixes some rules (`import type`, `prefer-const`, `??`).
Step 7 → Keep **Prettier** for formatting; do not use ESLint for formatting.
Step 8 → Disable a rule narrowly: `// eslint-disable-next-line @typescript-eslint/no-explicit-any` with a reason, never whole-file.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Install: `npm i -D eslint @eslint/js typescript-eslint` (typescript पहले से है)।
Step 2 → `eslint.config.mjs` (flat config) बनाओ: `eslint.configs.recommended` से शुरू करो, फिर typescript-eslint का preset spread करो।
Step 3 → Preset चुनो: `recommended` (सुरक्षित, कम rules) -> `strict` (ज़्यादा सख्त) -> `*TypeChecked` versions (type-aware rules जोड़ते हैं) -> `stylistic*`। Senior teams आम तौर पर `strictTypeChecked` + `stylisticTypeChecked` लेती हैं।
Step 4 → Typed linting के लिए `languageOptions.parserOptions.projectService: true` (+ `tsconfigRootDir`) लगाओ। तब ESLint editor जैसा ही program इस्तेमाल करता है, इसलिए files किसी tsconfig में शामिल होनी चाहिए।
Step 5 → Team के हिसाब से rules बदलो: `"@typescript-eslint/consistent-type-imports": "error"`, test files के लिए `files: ["**/*.test.ts"]` से rules ढीले करो।
Step 6 → CI में `npx eslint .` चलाओ (और editor में ESLint extension से)। `--fix` कुछ rules अपने आप ठीक करता है (`import type`, `prefer-const`, `??`)।
Step 7 → Formatting के लिए **Prettier** रखो; ESLint से formatting मत कराओ।
Step 8 → Rule संकरे दायरे में बंद करो: कारण के साथ `// eslint-disable-next-line @typescript-eslint/no-explicit-any`, पूरी file के लिए कभी नहीं।

---

## 🟡 Real World Example
**A Zomato-style payments API**: a refactor made `savePayment()` async. One caller forgot the `await`; the order was marked "paid" while the DB write failed silently (unhandled rejection). `tsc` was green. After adding `@typescript-eslint/no-floating-promises` the same pull request failed in CI with "Promises must be awaited...". The team also enabled `no-misused-promises` (catches `async` callbacks passed to `forEach`/Express handlers where the return value is ignored) and `prefer-nullish-coalescing` (a `0` rupees discount was being treated as "no discount" by `||`).

## 🟡 Real Example Hindi mein
**Zomato-जैसी payments API**: refactor में `savePayment()` async हो गया। एक caller में `await` छूट गया; DB write चुपचाप fail हुआ पर order "paid" मार्क हो गया (unhandled rejection)। `tsc` हरा था। `@typescript-eslint/no-floating-promises` जोड़ने के बाद वही pull request CI में "Promises must be awaited..." से fail हुआ। Team ने `no-misused-promises` (`forEach`/Express handlers में दिए `async` callbacks पकड़ता है जिनका return value ignore होता है) और `prefer-nullish-coalescing` भी चालू किए (`||` की वजह से `0` रुपये का discount "discount नहीं है" माना जा रहा था)।

---

## 💻 Code Example — Basic

Flat config used for all runs below (`eslint.config.mjs`):

```javascript
// @ts-check
import eslint from "@eslint/js";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist/**", "eslint.config.mjs"] }, // never lint build output / this file
  eslint.configs.recommended, // core JS rules
  ...tseslint.configs.strictTypeChecked, // strict + type-aware rules
  ...tseslint.configs.stylisticTypeChecked, // consistency rules
  {
    languageOptions: {
      parserOptions: {
        projectService: true, // use the TS project (typed linting)
        tsconfigRootDir: import.meta.dirname, // where tsconfig.json lives
      },
    },
    rules: {
      "@typescript-eslint/consistent-type-imports": "error", // force `import type`
      "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }], // _ prefix = intentionally unused
    },
  },
  {
    files: ["**/*.test.ts"], // relax a rule for tests only
    rules: { "@typescript-eslint/no-non-null-assertion": "off" },
  },
);
```

Code that **compiles under `tsc --strict`** but ESLint rejects (each message is real output of `npx eslint src/bad.ts`):

```typescript
import { Request } from "express"; // eslint: All imports in the declaration are only used as types. Use `import type`  (consistent-type-imports)

async function savePayment(id: string): Promise<void> {
  await Promise.resolve(id); // pretend DB write
}

export function handler(req: Request, data: any): void { // eslint: Unexpected any. Specify a different type  (no-explicit-any)
  savePayment("p1"); // eslint: Promises must be awaited, end with a call to .catch, ... or be explicitly marked as ignored with the `void` operator  (no-floating-promises)
  const amount = data.amount; // eslint: Unsafe assignment of an `any` value (no-unsafe-assignment) + Unsafe member access .amount on an `any` value (no-unsafe-member-access)
  const user = req.body as { name: string }; // req.body is typed any
  console.log(amount, user!.name); // eslint: Forbidden non-null assertion (no-non-null-assertion) + This assertion is unnecessary since it does not change the type of the expression (no-unnecessary-type-assertion)
  let unused = 1; // eslint: 'unused' is never reassigned. Use 'const' instead (prefer-const) + 'unused' is assigned a value but never used (no-unused-vars)
  [1, 2].forEach(async (n) => { // eslint: Promise returned in function argument where a void return was expected (no-misused-promises)
    await savePayment(String(n));
  });
}
```

Real summary line: `10 problems (10 errors, 0 warnings)` and `3 errors ... potentially fixable with the --fix option`.

## 💻 Code Example — Advanced

The same logic rewritten to be lint-clean (verified: `npx eslint src/good.ts` prints nothing, `tsc` passes):

```typescript
import type { Request, Response, NextFunction } from "express"; // type-only import
import { z } from "zod"; // runtime validation instead of `any`

const PaymentBody = z.object({ id: z.string(), amount: z.number().positive() }); // schema

async function savePayment(id: string): Promise<void> {
  await Promise.resolve(id); // pretend DB write
}

export async function handler(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const body = PaymentBody.parse(req.body); // body is now typed { id: string; amount: number }
    await savePayment(body.id); // awaited -> no floating promise
    res.json({ ok: true, amount: body.amount });
  } catch (err) {
    next(err); // let the Express error middleware handle it
  }
}

export async function saveAll(ids: string[]): Promise<void> {
  await Promise.all(ids.map((id) => savePayment(id))); // map + Promise.all instead of async forEach
}
```

More rules worth knowing (real output on a second file):

```typescript
interface Order { id: string; coupon?: string }

export function f(o: Order, n: number | null): string {
  const label = o.coupon || "none"; // eslint: Prefer using nullish coalescing operator (`??`) instead of a logical or (`||`) ...  (prefer-nullish-coalescing)
  if (o.id) { return label; }
  return String(n!); // eslint: Forbidden non-null assertion  (no-non-null-assertion)
}

export async function g(): Promise<number> { return 1; } // eslint: Async function 'g' has no 'await' expression  (require-await)
export function h(x: unknown) { return (x as any).y; } // eslint: Unsafe return of a value of type `any` (no-unsafe-return)
```

---

## 🟠 Node/Express + React Integration

```javascript
// eslint.config.mjs - extra block for a React + Node monorepo (add React rules per app)
// npm i -D eslint-plugin-react-hooks   (hooks rules are separate from typescript-eslint; this block was not executed here)
import reactHooks from "eslint-plugin-react-hooks";

export const reactBlock = {
  files: ["packages/web/**/*.{ts,tsx}"], // only the frontend
  plugins: { "react-hooks": reactHooks },
  rules: {
    "react-hooks/rules-of-hooks": "error", // hooks only at top level
    "react-hooks/exhaustive-deps": "warn", // dependency arrays must be complete
  },
};
```

```tsx
// no-misused-promises also protects React event handlers
import React from "react";

async function pay(): Promise<void> {
  await Promise.resolve();
}

export function PayButton() {
  // <button onClick={pay}> -> eslint: Promise-returning function provided to attribute where a void return was expected (no-misused-promises)
  // Fix: handle the promise explicitly
  return (
    <button
      onClick={() => {
        void pay(); // explicit "fire and forget" marker accepted by no-floating-promises
      }}
    >
      Pay
    </button>
  );
}
```

```json
{
  "scripts": {
    "lint": "eslint .",
    "lint:fix": "eslint . --fix",
    "typecheck": "tsc --noEmit",
    "ci": "npm run typecheck && npm run lint && npm test"
  }
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using only `recommended` (not type-checked) and expecting promise safety
`tseslint.configs.recommended` has **no** `no-floating-promises`. You need a `*TypeChecked` preset or enable the rule by hand, plus `projectService`.

❌ Mistake 2: Typed linting with a file not covered by tsconfig
Result: `Parsing error: ... was not found by the project service`. Add the folder to tsconfig `include` (or a `tsconfig.eslint.json`), or `ignores` it.

❌ Mistake 3: Unresolved imports make *everything* "unsafe"
Real run: when `zod` was not installed, the lint of `good.ts` printed 18 errors such as `Unsafe call of a type that could not be resolved` (`no-unsafe-call`) and `Unsafe assignment of an error typed value` - alongside `tsc`'s `error TS2307: Cannot find module 'zod'`. Fix the install first; do not silence the `no-unsafe-*` rules.

❌ Mistake 4: Silencing with `// eslint-disable` at the top of the file or `as any`
```typescript
// eslint-disable-next-line @typescript-eslint/no-explicit-any -- legacy SDK has no types, tracked in JIRA-123
export const sdk: any = (globalThis as Record<string, unknown>)["legacySdk"];
```
Always disable one line, name the rule, give a reason.

❌ Mistake 5: Using ESLint for formatting
Mixing `eslint-plugin-prettier` or style rules slows linting and causes diff noise. Use Prettier directly (`prettier --check .`).

---

## 🧠 Tricky Interview Question

```typescript
import { readFile } from "node:fs/promises";

export function load(): void {
  readFile("config.json", "utf8").then((txt) => { console.log(txt.length); });
}
```
Q: `tsc --strict` passes. What does typescript-eslint say, and what are the ways to fix it?

Answer: `@typescript-eslint/no-floating-promises` - the promise returned by `.then(...)` is neither awaited, nor has `.catch`/a rejection handler, so a failed read becomes an **unhandled rejection** (process crash on Node 15+). Fixes: (1) make `load` async and `await` it inside try/catch, (2) add `.catch(handleError)`, (3) mark deliberate fire-and-forget with `void readFile(...)` (the rule's `ignoreVoid` option defaults to true). The point of the question: the type system does not track **promise handling** - only the linter does.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `tsc` and ESLint?
A1: `tsc` verifies type correctness. ESLint (with typescript-eslint) finds patterns that are type-correct but risky/inconsistent (floating promises, `any` leaks, wrong `||`, unused vars) and enforces conventions. Run both.

Q2: What is a type-aware rule and what does it cost?
A2: A rule that needs type information (via the TS program), e.g. `no-floating-promises`, `no-unsafe-*`, `prefer-nullish-coalescing`. It is slower (needs full program) and requires `projectService`/`project` config. Use presets with `TypeChecked` suffix.

Q3: `recommended` vs `strict` vs `stylistic`?
A3: `recommended` = likely-bug rules, low noise. `strict` = additional rules, can change in minor versions. `stylistic` = consistency rules (e.g. `consistent-type-definitions`). Typed variants add type-aware rules.

Q4: How do you adopt it in a legacy codebase?
A4: Start with `recommended`, fix, then add type-aware rules as `warn`, ratchet to `error` per folder with `files:` overrides, use `eslint --max-warnings 0` in CI, and fix with `--fix` where safe.

Q5: Why prefer `@ts-expect-error` over `@ts-ignore` and which rule enforces it?
A5: `@typescript-eslint/ban-ts-comment` (in `recommended`) bans `@ts-ignore`; `@ts-expect-error` is allowed with a description because it fails when the error disappears.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every serious TS project: Node APIs (promise safety), React apps (hooks rules), libraries
- You want conventions enforced automatically in PRs

❌ Avoid / limit when:
- Typed linting on a huge repo without project references - split the config or lint only changed files in pre-commit
- Using it as a formatter (use Prettier)

---

## 📊 Visual Diagram
```
 source.ts ──► tsc --noEmit        "is it type-correct?"
     │
     └──────► ESLint
                ├─ @eslint/js recommended          (JS bugs)
                ├─ typescript-eslint strictTypeChecked
                │      └─ asks TypeScript for types ──► no-floating-promises
                │                                       no-misused-promises
                │                                       no-unsafe-assignment / member-access / call / return
                └─ team rules (consistent-type-imports, per-folder overrides)

 CI:  tsc --noEmit  &&  eslint .  &&  tests  &&  build
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Flat config | `eslint.config.mjs` array-based config | Array वाली नई ESLint config |
| Type-aware rule | Rule that uses TS type info | Type जानकारी इस्तेमाल करने वाला rule |
| `projectService` | Loads the TS project for linting | Linting के लिए TS project लोड करना |
| Floating promise | Promise created but never handled | बनाया गया पर कभी handle न हुआ promise |
| `no-unsafe-*` | Rules against `any` flowing around | `any` के फैलाव के खिलाफ rules |
| Preset | Ready-made set of rules | तैयार rules का समूह |

---

## ⚡ 3-Line Summary
English:
1. ESLint + typescript-eslint catch legal-but-risky code that `tsc` accepts: floating promises, `any` leaks, `||` vs `??`.
2. Use `strictTypeChecked` + `stylisticTypeChecked` with `projectService: true` in an `eslint.config.mjs`.
3. Run `tsc --noEmit` and `eslint .` in CI; disable rules only line by line with a reason.

Hindi:
1. ESLint + typescript-eslint वह code पकड़ते हैं जो वैध है पर जोखिम भरा, जिसे `tsc` स्वीकार करता है: floating promises, `any` का रिसाव, `||` बनाम `??`।
2. `eslint.config.mjs` में `projectService: true` के साथ `strictTypeChecked` + `stylisticTypeChecked` इस्तेमाल करो।
3. CI में `tsc --noEmit` और `eslint .` दोनों चलाओ; rules सिर्फ एक-एक line पर कारण के साथ बंद करो।

---

## ➡️ Next Topic
**78. Source Maps and Debugging TS** - Stepping through TypeScript in VS Code/Chrome even though Node runs compiled JavaScript.
