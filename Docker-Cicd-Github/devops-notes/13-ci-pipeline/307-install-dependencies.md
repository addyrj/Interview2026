# 307. Install Dependencies
# हिंदी में: Dependencies Install करना

---

## 🔵 Simple Definition (English)
Installing dependencies in CI means downloading and installing exactly the packages your project needs, in a **reproducible** way: `npm ci` (Node), `pnpm install --frozen-lockfile`, `yarn install --immutable`, or `pip install -r requirements.txt` (Python). The lockfile decides versions, not "latest at this moment".

## 🔵 सरल परिभाषा (Hindi)
CI में dependencies install करने का मतलब है प्रोजेक्ट को चाहिए वही packages **reproducible** तरीके से download और install करना: `npm ci` (Node), `pnpm install --frozen-lockfile`, `yarn install --immutable`, या `pip install -r requirements.txt` (Python)। Versions lockfile तय करती है, "इस पल का latest" नहीं।

---

## 🔴 Problem it Solves
`npm install` can rewrite the lockfile and pick newer minor versions. Monday's green build turns red on Tuesday because a transitive dependency published a bad patch. Developers and CI get different trees ("works on my machine"). Attackers publish malicious versions of packages; unpinned installs pull them automatically. Install scripts (`postinstall`) can run arbitrary code with access to CI secrets.
A strict, locked, minimal install removes those risks.

## 🔴 यह क्यों बना? (Hindi)
`npm install` lockfile बदल सकता है और नए minor versions उठा सकता है। सोमवार का हरा build मंगलवार को लाल हो जाता है क्योंकि किसी transitive dependency ने खराब patch निकाल दिया। Developers और CI के पास अलग trees होते हैं। Attackers packages के malicious versions publish करते हैं; unpinned install उन्हें अपने आप खींच लेता है। Install scripts (`postinstall`) CI secrets के साथ कोई भी code चला सकती हैं।
सख़्त, locked, minimal install इन जोखिमों को हटाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Cache restore gives ~/.npm / ~/.cache/pip (previous topic)
Step 2 → npm ci reads package-lock.json (not package.json ranges)
Step 3 → It deletes any existing node_modules, installs exact versions
Step 4 → If lockfile and package.json disagree -> command FAILS (good)
Step 5 → Integrity hashes in lockfile verify every tarball
Step 6 → Lifecycle scripts run (unless --ignore-scripts)
Step 7 → pip: install from pinned requirements (optionally --require-hashes)
Step 8 → Next steps (lint/test/build) use the installed tree
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Cache restore से ~/.npm / ~/.cache/pip मिलता है (पिछला topic)
Step 2 → npm ci package-lock.json पढ़ता है (package.json की ranges नहीं)
Step 3 → मौजूदा node_modules हटाकर सटीक versions install करता है
Step 4 → lockfile और package.json में मेल न हो -> command FAIL होती है (अच्छी बात)
Step 5 → Lockfile के integrity hashes हर tarball verify करते हैं
Step 6 → Lifecycle scripts चलती हैं (जब तक --ignore-scripts न हो)
Step 7 → pip: pinned requirements से install (चाहें तो --require-hashes)
Step 8 → अगले steps (lint/test/build) installed tree इस्तेमाल करते हैं
```

---

## 🟡 Real World Example
A dependency `left-pad-ish` releases 2.4.1 with a regression. Teams that used `npm install` in CI got failing builds all morning and nobody could tell which commit was to blame. Teams using `npm ci` with a committed lockfile saw no change until a developer deliberately upgraded in a PR, which showed the lockfile diff and failed tests in that PR only. In another incident, a compromised package added a `postinstall` that exfiltrated env vars; teams using `--ignore-scripts` for jobs with secrets were unaffected.

## 🟡 Real Example Hindi mein
एक dependency `left-pad-ish` 2.4.1 में regression निकालती है। CI में `npm install` इस्तेमाल करने वाली teams के builds सुबह भर fail हुए और कोई नहीं बता पाया कि किस commit की गलती है। Committed lockfile के साथ `npm ci` इस्तेमाल करने वाली teams को तब तक कोई बदलाव नहीं दिखा जब तक किसी developer ने PR में जानबूझकर upgrade नहीं किया; उस PR में lockfile diff दिखा और tests सिर्फ़ वहीं fail हुए। एक और घटना में compromised package ने `postinstall` से env vars चुराने की कोशिश की; secrets वाली jobs में `--ignore-scripts` लगाने वाली teams सुरक्षित रहीं।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/install-basic.yml
name: Install Basic                 # workflow name

on: [pull_request]                  # run on PRs

jobs:
  install:
    runs-on: ubuntu-latest          # Linux runner
    steps:
      - uses: actions/checkout@v4   # get code
      - uses: actions/setup-node@v4 # Node + npm cache
        with:
          node-version: 20
          cache: npm
      - run: npm ci                 # clean, lockfile-exact install (fails on mismatch)
      - run: npm ls --depth=0       # show top-level packages for the log
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/install-advanced.yml
name: Install Advanced

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  node:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    strategy:
      matrix:
        project: [api, web]                 # two Node projects in one monorepo
    defaults:
      run:
        working-directory: ${{ matrix.project }}
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: ${{ matrix.project }}/package-lock.json

      - name: Install (locked, no scripts)
        run: npm ci --ignore-scripts --no-audit --no-fund
        # --ignore-scripts: blocks postinstall code from running
        # --no-audit/--no-fund: faster logs; audit runs in its own job

      - name: Rebuild only trusted native modules
        run: npm rebuild bcrypt sharp      # run scripts only for packages you trust

      - name: Verify lockfile is in sync
        run: |
          git diff --exit-code package-lock.json   # npm ci never writes it; any diff means something is wrong

      - name: Verify registry signatures
        run: npm audit signatures          # checks provenance/signatures (npm >= 9)

  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm audit --audit-level=high --omit=dev   # fail on high+ prod vulns
        working-directory: api

  python:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: pricing
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - name: Install pinned requirements
        run: |
          python -m venv .venv
          . .venv/bin/activate
          pip install --require-hashes -r requirements.txt   # needs hashes in the file (pip-compile --generate-hashes)
          pip check                                          # verify no broken dependency pairs
```

---

## 🟠 My Stack Integration
- **Node.js:** `npm ci` in CI and in the Dockerfile (`RUN npm ci --omit=dev` for production image).
- **React:** dev dependencies are needed to build; production runtime is just static files served by Nginx.
- **FastAPI:** `pip-compile --generate-hashes` produces locked `requirements.txt`; CI installs with `--require-hashes`.
- **VPS:** never run `npm install` on the server; build in CI/Docker and ship the result.
- **Private packages:** use `NODE_AUTH_TOKEN` env on the install step only.

```dockerfile
# Dockerfile snippet: same locked install inside the image (example tags)
FROM node:20-alpine AS deps          # stage for dependencies
WORKDIR /app                         # working directory
COPY package.json package-lock.json ./   # copy manifests first for layer cache
RUN npm ci --omit=dev                # production deps only, exactly as locked
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `npm install` in CI.
✅ Correct: `npm ci` (or `pnpm install --frozen-lockfile`, `yarn install --immutable`).

❌ Mistake 2: Not committing the lockfile (or adding it to `.gitignore`).
✅ Correct: Commit `package-lock.json` / `pnpm-lock.yaml` / `poetry.lock`; review lockfile diffs in PRs.

❌ Mistake 3: Running install scripts in jobs that hold secrets.
✅ Correct: `--ignore-scripts` then rebuild only trusted native modules; keep secrets out of install steps.

❌ Mistake 4: `pip install fastapi` without pins, or `pip install -U` in CI.
✅ Correct: Pin versions (`fastapi==0.115.0`, example) and install from a locked file.

❌ Mistake 5: Using a long-lived npm token with publish rights to install.
✅ Correct: Read-only token, passed only to the install step as `NODE_AUTH_TOKEN`.

---

## 🧠 Tricky Interview Question
**Q:** `npm ci` fails with "package.json and package-lock.json are not in sync" on CI, but `npm install` works locally. A teammate suggests changing CI to `npm install`. What is the right fix?

**Answer:** Do not weaken CI; the failure is correct. Someone edited `package.json` (or upgraded Node/npm, producing a different lockfile format) without committing the updated lockfile. Run `npm install` locally with the project's Node/npm version, commit the updated `package-lock.json`, and push. Also add a CI check or pre-commit hook so lockfile drift is caught early. `npm ci` exists precisely to expose this.

---

## ⚫ Interview Questions + Answers

Q1: `npm ci` vs `npm install`?
A1: `npm ci` requires a lockfile, deletes `node_modules`, installs exact locked versions, never writes the lockfile, and errors on mismatch. `npm install` can resolve new versions and update the lockfile. Use `ci` in CI and Docker.

Q2: Why `--omit=dev` in production images?
A2: Smaller image, fewer vulnerabilities, faster startup. Dev tools (jest, eslint, typescript) are not needed at runtime.

Q3: What is a supply-chain attack and how does installation relate?
A3: Compromise of a dependency or registry account. Installs can run `postinstall` scripts. Mitigate with lockfiles, `--ignore-scripts`, `npm audit signatures`, minimal tokens, Dependabot, and reviewing new dependencies.

Q4: What does `pip check` do?
A4: Verifies that installed packages have compatible requirements and reports conflicts.

Q5: pnpm vs npm in CI?
A5: pnpm uses a content-addressable store and hard links: faster and stricter about undeclared dependencies. Use `pnpm install --frozen-lockfile`. Install pnpm via `pnpm/action-setup` before `setup-node` caching.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every CI job needing code dependencies: strict locked install
- Production Docker builds: `npm ci --omit=dev`
- Jobs with secrets: `--ignore-scripts` plus explicit rebuild

❌ Avoid when:
- Never use plain `npm install` in CI (use it locally to change dependencies)
- Do not install in jobs that do not need dependencies (e.g. deploy-only jobs)
- Do not install dev dependencies in runtime images

---

## 📊 Visual Diagram
```
 package.json  (ranges: "^4.18.0")        package-lock.json (exact: 4.18.2 + hash)
        \                                        /
         \                                      /
          v                                    v
      npm install  -> may pick 4.19.0, rewrites lock   (NOT for CI)
      npm ci       -> reads lock only -> 4.18.2 exactly
                     |-- lock vs package.json mismatch? -> FAIL fast
                     |-- verifies integrity hashes
                     v
              node_modules (fresh, reproducible)
                     |
          lint -> types -> tests -> build
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Lockfile | Exact resolved versions + hashes | सटीक versions की file |
| `npm ci` | Clean, locked install | साफ़, locked install |
| `--ignore-scripts` | Skip lifecycle scripts | install scripts छोड़ना |
| Transitive dependency | Dependency of a dependency | dependency की dependency |
| Supply-chain attack | Attack via packages | packages के ज़रिए हमला |
| `--require-hashes` | pip verifies file hashes | pip hash जाँच |
| `--omit=dev` | Skip devDependencies | dev packages छोड़ना |

---

## ⚡ 3-Line Summary
English: Use locked, strict installs in CI: `npm ci`, `pnpm --frozen-lockfile`, or hashed pip requirements.
Commit lockfiles, pin versions, and use `--ignore-scripts` where secrets exist.
Fail on lockfile drift, audit separately, and install nothing on the VPS by hand.
Hindi: CI में locked, सख़्त installs इस्तेमाल करें: `npm ci`, `pnpm --frozen-lockfile` या hashed pip requirements।
Lockfiles commit करें, versions pin करें और जहाँ secrets हों वहाँ `--ignore-scripts` लगाएँ।
Lockfile drift पर fail करें, audit अलग चलाएँ और VPS पर हाथ से कुछ install न करें।

---

## ➡️ Next Topic
**308. Run Linting (ESLint)** — with dependencies installed, the first quality gate is static analysis.
