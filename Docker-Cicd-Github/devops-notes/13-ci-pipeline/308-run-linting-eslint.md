# 308. Run Linting (ESLint)
# हिंदी में: Linting चलाना (ESLint)

---

## 🔵 Simple Definition (English)
**Linting** is static analysis: a tool reads your code without running it and reports bugs, risky patterns, and style problems. **ESLint** is the standard linter for JavaScript and TypeScript. In CI, `npm run lint` fails the job when rules are broken, so bad code cannot be merged.

## 🔵 सरल परिभाषा (Hindi)
**Linting** static analysis है: tool आपका code चलाए बिना पढ़ता है और bugs, जोखिम भरे patterns और style की समस्याएँ बताता है। **ESLint** JavaScript और TypeScript का मानक linter है। CI में `npm run lint` rules टूटने पर job fail कर देता है, इसलिए खराब code merge नहीं हो पाता।

---

## 🔴 Problem it Solves
Code review wastes time on "missing await", "unused variable", "use const", and tabs vs spaces. Real bugs slip through: an `async` function called without `await`, `==` instead of `===`, `useEffect` with missing dependencies, a hook called inside a condition. Each developer formats differently, making diffs noisy.
Linting automates the boring review and catches whole bug classes before tests run.

## 🔴 यह क्यों बना? (Hindi)
Code review में समय "await भूल गए", "unused variable", "const इस्तेमाल करो" और tabs बनाम spaces पर जाता है। असली bugs निकल जाते हैं: `async` function बिना `await` के call, `==` की जगह `===`, missing dependencies वाला `useEffect`, condition के अंदर hook call। हर developer अलग format करता है, जिससे diffs शोरभरे हो जाते हैं।
Linting उबाऊ review को automate करती है और tests से पहले ही bugs की पूरी श्रेणियाँ पकड़ लेती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Install eslint + plugins as devDependencies (typescript-eslint, react-hooks)
Step 2 → Config file: eslint.config.js (flat config, ESLint 9+) or .eslintrc.*
Step 3 → package.json script:  "lint": "eslint ."
Step 4 → CI runs npm run lint after npm ci
Step 5 → ESLint parses files to AST, applies each rule, collects problems
Step 6 → Severity: "error" -> exit code 1 (job fails); "warn" -> just printed
Step 7 → --max-warnings 0 turns warnings into failures
Step 8 → Output format (e.g. github/stylish) shows annotations on the PR
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → eslint + plugins devDependencies में install (typescript-eslint, react-hooks)
Step 2 → Config file: eslint.config.js (flat config, ESLint 9+) या .eslintrc.*
Step 3 → package.json script:  "lint": "eslint ."
Step 4 → CI npm ci के बाद npm run lint चलाता है
Step 5 → ESLint files को AST में parse करके हर rule लगाता है, समस्याएँ इकट्ठा करता है
Step 6 → Severity: "error" -> exit code 1 (job fail); "warn" -> सिर्फ़ print
Step 7 → --max-warnings 0 warnings को failures बना देता है
Step 8 → Output format PR पर annotations दिखाता है
```

---

## 🟡 Real World Example
A startup's React dashboard had a recurring production bug: stale data because `useEffect` dependency arrays were wrong. They enabled `react-hooks/exhaustive-deps` as an error and added `no-floating-promises` for the Express API. In the first week CI flagged 23 real bugs. The lint step takes 25 s, runs in parallel with tests, and PR reviewers stopped commenting on style.

## 🟡 Real Example Hindi mein
एक startup के React dashboard में बार-बार production bug आता था: गलत `useEffect` dependency arrays की वजह से stale data। उन्होंने `react-hooks/exhaustive-deps` को error किया और Express API के लिए `no-floating-promises` जोड़ा। पहले हफ़्ते में CI ने 23 असली bugs पकड़े। Lint step 25 सेकंड लेता है, tests के साथ parallel चलता है, और reviewers ने style पर comment करना बंद कर दिया।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/lint-basic.yml
name: Lint Basic                    # workflow name

on: [pull_request]                  # lint every PR

jobs:
  lint:
    runs-on: ubuntu-latest          # Linux runner
    steps:
      - uses: actions/checkout@v4   # get code
      - uses: actions/setup-node@v4 # Node + cache
        with:
          node-version: 20
          cache: npm
      - run: npm ci                 # install exact dependencies
      - run: npm run lint           # package.json: "lint": "eslint ."
```

```javascript
// eslint.config.js  (ESLint 9 flat config, minimal; CommonJS so it needs no "type": "module")
const js = require('@eslint/js');                 // ESLint's recommended rules

module.exports = [
  js.configs.recommended,                          // base rule set
  {
    files: ['**/*.js'],                            // apply to JS files
    languageOptions: { sourceType: 'commonjs', ecmaVersion: 2022 }, // Node/CommonJS code
    rules: {
      'no-unused-vars': 'error',                   // unused variables fail CI
      eqeqeq: 'error',                             // force === instead of ==
    },
  },
  { ignores: ['dist/**', 'node_modules/**', 'coverage/**'] }, // never lint build output
];
```

## 💻 Code / Config Example — Advanced
```javascript
// eslint.config.mjs  (TypeScript + React + Node; ESLint 9 flat config)
// npm i -D eslint @eslint/js typescript-eslint eslint-plugin-react-hooks globals
import js from '@eslint/js';                          // base JS rules
import tseslint from 'typescript-eslint';             // TS parser + rules
import reactHooks from 'eslint-plugin-react-hooks';   // hooks rules
import globals from 'globals';                        // known global variables

export default tseslint.config(
  { ignores: ['dist/**', 'build/**', 'coverage/**', '.next/**'] }, // skip generated files
  js.configs.recommended,                             // JS best practices
  ...tseslint.configs.recommendedTypeChecked,         // TS rules that use type info
  {
    languageOptions: {
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname }, // enable type-aware linting
    },
  },
  {
    files: ['web/**/*.{ts,tsx}'],                     // React app only
    languageOptions: { globals: globals.browser },    // window, document...
    plugins: { 'react-hooks': reactHooks },           // register plugin
    rules: {
      'react-hooks/rules-of-hooks': 'error',          // hooks only at top level
      'react-hooks/exhaustive-deps': 'error',         // correct dependency arrays
    },
  },
  {
    files: ['api/**/*.ts'],                           // Node API only
    languageOptions: { globals: globals.node },       // process, Buffer...
    rules: {
      '@typescript-eslint/no-floating-promises': 'error',  // always await/handle promises
      'no-console': ['error', { allow: ['warn', 'error'] }], // use a logger, not console.log
    },
  },
);
```

```yaml
# .github/workflows/lint-advanced.yml
name: Lint Advanced

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read
  checks: write                       # needed only if an action posts check annotations

concurrency:
  group: lint-${{ github.ref }}
  cancel-in-progress: true            # cancel superseded lint runs

jobs:
  eslint:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm
      - run: npm ci --ignore-scripts

      - name: Cache ESLint results
        uses: actions/cache@v4
        with:
          path: .eslintcache                       # file written by --cache
          key: eslint-${{ runner.os }}-${{ hashFiles('package-lock.json', 'eslint.config.mjs') }}
          restore-keys: eslint-${{ runner.os }}-

      - name: ESLint (fail on any warning)
        run: npx eslint . --cache --max-warnings 0 --format github
        # --cache: only re-lint changed files
        # --max-warnings 0: warnings fail the build
        # --format github: inline PR annotations (formatter bundled with ESLint >= 9.x; verify for your version)

      - name: Prettier check (formatting)
        run: npx prettier --check .                # fails if files are not formatted
```

---

## 🟠 My Stack Integration
- **Node.js (Express/Nest):** `@typescript-eslint/no-floating-promises`, `no-console`, `eqeqeq`, security plugin `eslint-plugin-security`.
- **React:** `react-hooks/*` and `jsx-a11y` rules for accessibility.
- **FastAPI counterpart:** Python uses `ruff check .` and `ruff format --check .` in the same CI position.
- **Nginx / VPS:** lint shell scripts with `shellcheck deploy.sh` and YAML with `yamllint` or `actionlint` in the same job family.
- **Local DX:** run lint in a pre-commit hook (husky + lint-staged) so CI is a safety net, not the first catch.

```json
{
  "scripts": {
    "lint": "eslint . --max-warnings 0",
    "lint:fix": "eslint . --fix",
    "format:check": "prettier --check ."
  }
}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Rules set to `warn` that nobody reads; warnings pile up to thousands.
✅ Correct: Use `error` for rules you care about and `--max-warnings 0`.

❌ Mistake 2: Linting `dist/`, `build/`, `.next/`, `coverage/`. Slow and noisy.
✅ Correct: Add them to `ignores`.

❌ Mistake 3: Using `--fix` in CI and committing changes silently, or letting CI "fix" and pass.
✅ Correct: CI only checks (`eslint .`); developers fix locally with `--fix` or a pre-commit hook.

❌ Mistake 4: Mixing old `.eslintrc` knowledge with ESLint 9. Flat config (`eslint.config.js`) is the default there and `.eslintrc` is no longer read unless a flag is used.
✅ Correct: Check your ESLint major version and use the matching config format.

❌ Mistake 5: Using ESLint to also enforce formatting through many style rules, fighting Prettier.
✅ Correct: ESLint for bugs, Prettier for format (`prettier --check`), and no overlapping style rules.

---

## 🧠 Tricky Interview Question
**Q:** Lint passes on your laptop but fails in CI with "Parsing error: Cannot read file tsconfig.json" or with rules you never saw. What are the likely causes?

**Answer:** (1) Different ESLint/plugin versions: laptop used a globally installed ESLint, CI uses the lockfile. Fix by running only `npx eslint` from local `node_modules` and committing the lockfile. (2) Type-aware linting resolves `tsconfig.json` relative to the working directory; in a monorepo CI runs from another folder, so set `tsconfigRootDir` or `working-directory`. (3) Case-sensitive paths: macOS is case-insensitive, Linux is not, so an import `./Button` of `button.tsx` passes locally but fails in CI. (4) Different OS line endings or Node versions. Always reproduce with `npm ci && npm run lint` in a clean clone.

---

## ⚫ Interview Questions + Answers

Q1: Linter vs formatter vs type checker?
A1: Linter (ESLint) finds suspicious code patterns; formatter (Prettier) rewrites layout; type checker (tsc) verifies types. All three run in CI because they catch different problems.

Q2: What does `--max-warnings 0` do?
A2: Makes ESLint exit with failure if any warning exists, so warnings cannot silently accumulate.

Q3: How do you introduce ESLint to a large legacy codebase?
A3: Start with recommended rules as `warn`, fix automatically with `--fix`, then raise rules to `error` gradually; or lint only changed files (`lint-staged`) so new code is clean without a huge refactor.

Q4: How can lint be a security tool?
A4: Plugins such as `eslint-plugin-security` and rules like `no-eval`, `no-implied-eval`, `no-new-func` flag dangerous patterns; `no-floating-promises` prevents silently ignored failures.

Q5: Should lint run in parallel with tests?
A5: Yes. Lint needs no build and is fast; run it as a separate job so developers see style failures within seconds while tests continue.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every JS/TS project; every PR
- Enforcing team conventions and catching bug patterns
- Pre-commit plus CI together

❌ Avoid when:
- Treat lint as supplement, not replacement, for tests
- Do not lint generated or vendored code
- Do not use ESLint style rules where Prettier already handles formatting

---

## 📊 Visual Diagram
```
 source files (.ts .tsx .js)
        |
        v
  +-------------+     +-----------------+     +---------------------+
  | eslint      |---->| AST + rules     |---->| problems list       |
  | config      |     | (hooks, promises|     |  error  -> exit 1   |
  +-------------+     |  security...)   |     |  warn   -> printed  |
                      +-----------------+     +---------------------+
                                                       |
                  CI: npm ci -> npm run lint --------->|
                                                       v
                            PR check RED (blocked)  or  GREEN (continue to tests)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Linter | Static code analyzer | static code विश्लेषक |
| ESLint | JS/TS linter | JS/TS का linter |
| Flat config | `eslint.config.js` format (ESLint 9+) | नया config format |
| Rule severity | off / warn / error | rule की गंभीरता |
| `--max-warnings` | Fail when warnings exceed N | warnings की सीमा |
| Prettier | Code formatter | code formatter |
| AST | Tree form of code | code का tree रूप |

---

## ⚡ 3-Line Summary
English: ESLint statically analyzes JS/TS and fails CI on rule violations.
Use flat config, `error` severity, `--max-warnings 0`, and ignore generated folders.
Pair it with Prettier and type checking, and run it as a fast parallel job.
Hindi: ESLint JS/TS का static विश्लेषण करता है और rules टूटने पर CI fail करता है।
Flat config, `error` severity, `--max-warnings 0` इस्तेमाल करें और generated folders ignore करें।
इसे Prettier और type checking के साथ जोड़ें और तेज़ parallel job में चलाएँ।

---

## ➡️ Next Topic
**309. Run Type Checking (TypeScript)** — linting finds suspicious patterns; the compiler proves the types are consistent.
