# 304. Setup Node.js (actions/setup-node)
# हिंदी में: Node.js Setup करना (actions/setup-node)

---

## 🔵 Simple Definition (English)
`actions/setup-node` installs a chosen **Node.js version** on the runner, puts `node` and `npm` on the PATH, can **cache** package manager downloads (npm, yarn, pnpm), and can configure a registry token for installing or publishing private packages.

## 🔵 सरल परिभाषा (Hindi)
`actions/setup-node` runner पर चुना हुआ **Node.js version** install करती है, `node` और `npm` को PATH में डालती है, package manager के downloads (npm, yarn, pnpm) **cache** कर सकती है, और private packages install या publish करने के लिए registry token भी configure कर सकती है।

---

## 🔴 Problem it Solves
GitHub runners ship with some default Node version that changes when images update. Your app needs Node 20, your laptop has 20, the runner has 18 today and 22 tomorrow. Builds break randomly ("works yesterday"). Also, downloading all packages from scratch on every run wastes minutes.
`setup-node` pins the version and caches dependencies.

## 🔴 यह क्यों बना? (Hindi)
GitHub runners पर कोई default Node version होता है जो image update होने पर बदल जाता है। आपके app को Node 20 चाहिए, laptop पर 20 है, runner पर आज 18 और कल 22 हो सकता है। Builds अचानक टूटते हैं ("कल तक चलता था")। साथ ही हर run में सारे packages नए सिरे से download करना minutes बर्बाद करता है।
`setup-node` version pin करती है और dependencies cache करती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Step reads node-version (or node-version-file like .nvmrc)
Step 2 → Looks in the runner tool cache for that version
Step 3 → If missing, downloads it from the Node distribution and adds to PATH
Step 4 → If cache: npm|yarn|pnpm is set, finds lockfile, computes cache key
Step 5 → Restores package-manager cache (~/.npm etc.) from earlier runs
Step 6 → Optional: writes .npmrc for registry-url using NODE_AUTH_TOKEN
Step 7 → Post step saves the cache if lockfile hash changed
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Step node-version (या .nvmrc जैसी node-version-file) पढ़ता है
Step 2 → Runner के tool cache में वह version ढूँढता है
Step 3 → न मिले तो Node distribution से download करके PATH में जोड़ता है
Step 4 → cache: npm|yarn|pnpm हो तो lockfile ढूँढकर cache key बनाता है
Step 5 → पुराने runs का package-manager cache (~/.npm आदि) restore करता है
Step 6 → Optional: registry-url के लिए NODE_AUTH_TOKEN से .npmrc लिखता है
Step 7 → Post step lockfile hash बदलने पर cache save करता है
```

---

## 🟡 Real World Example
An Indian SaaS company runs a Next.js frontend and an Express API. Both repos have `.nvmrc` with `20`. Their CI uses `node-version-file: .nvmrc` so upgrading Node means changing one file. Caching cut `npm ci` from 55 seconds to 12 seconds. A publishing workflow uses `registry-url` to push an internal package to GitHub Packages.

## 🟡 Real Example Hindi mein
एक भारतीय SaaS कंपनी का Next.js frontend और Express API है। दोनों repos में `.nvmrc` में `20` लिखा है। उनकी CI `node-version-file: .nvmrc` इस्तेमाल करती है, इसलिए Node upgrade का मतलब बस एक file बदलना। Caching से `npm ci` 55 सेकंड से 12 सेकंड पर आ गया। Publish workflow `registry-url` से internal package GitHub Packages पर push करता है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/node-basic.yml
name: Node Basic                    # workflow name

on: [push, pull_request]            # run on push and PR

jobs:
  test:
    runs-on: ubuntu-latest          # Linux runner
    steps:
      - uses: actions/checkout@v4   # get code first
      - uses: actions/setup-node@v4 # install Node
        with:
          node-version: 20          # major version; latest 20.x is used
          cache: npm                # cache ~/.npm using package-lock.json hash
      - run: node --version         # prove the version
      - run: npm ci                 # install exact dependencies
      - run: npm test               # run tests
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/node-advanced.yml
name: Node Advanced

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read                    # read-only token

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15             # avoid hung jobs
    strategy:
      fail-fast: false              # let all matrix versions finish
      matrix:
        node: [20, 22]              # test against two LTS lines (example versions)
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false

      - name: Setup Node ${{ matrix.node }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}        # from the matrix
          cache: npm                              # npm | yarn | pnpm
          cache-dependency-path: |                # monorepo: where lockfiles live
            api/package-lock.json
            web/package-lock.json
          registry-url: https://registry.npmjs.org  # writes .npmrc using NODE_AUTH_TOKEN
          check-latest: false                     # use cached version, do not check for newer

      - name: Install API deps
        working-directory: api
        run: npm ci --prefer-offline --no-audit   # use cache; skip audit here (audit has own job)
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_READ_TOKEN }}   # for private @acme packages

      - name: Install web deps
        working-directory: web
        run: npm ci --prefer-offline --no-audit
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_READ_TOKEN }}

      - name: Tests
        working-directory: api
        run: npm test -- --ci

  # Version from file (single source of truth) and pnpm example
  pnpm-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4                # pnpm must be installed BEFORE setup-node cache
        with:
          version: 9                              # example version
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc               # reads "20" from the file
          cache: pnpm                             # uses pnpm-lock.yaml
      - run: pnpm install --frozen-lockfile       # like npm ci
      - run: pnpm build
```

---

## 🟠 My Stack Integration
- **Node.js (Express/Nest):** `node-version-file: .nvmrc` and the same version in your `Dockerfile` (`FROM node:20-alpine`) so CI and production match.
- **React/Vite/Next:** `cache: npm` + `npm ci` + `npm run build`.
- **FastAPI:** not needed, but if the repo also builds a React frontend, use `setup-node` only in that job.
- **Nginx / VPS:** build static React files in CI, upload as artifact, `rsync` to `/var/www/app` on the VPS.
- **AWS:** use matrix on Node 20 to mirror the Lambda runtime you deploy.

```yaml
# keep Docker and CI in sync: read the version from one file
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc          # contains: 20
          cache: npm
      # Dockerfile has:  ARG NODE_VERSION=20  FROM node:${NODE_VERSION}-alpine
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `cache: npm` but having no `package-lock.json` committed. The step fails ("Dependencies lock file is not found").
✅ Correct: Commit the lockfile, or set `cache-dependency-path` to the right file in monorepos.

❌ Mistake 2: Writing `node-version: 20.10` as a number in YAML in a matrix, e.g. `node: [18, 20.10]` and `20.10` becomes `20.1`.
✅ Correct: Quote versions: `"20.10"`.

❌ Mistake 3: Setting `cache: pnpm` before pnpm is installed. The step cannot find pnpm.
✅ Correct: Run `pnpm/action-setup` first, then `setup-node`.

❌ Mistake 4: Storing registry tokens inline or committing `.npmrc` with `_authToken`.
✅ Correct: Use `registry-url` + `NODE_AUTH_TOKEN: ${{ secrets.X }}` and keep `.npmrc` token-free.

❌ Mistake 5: Caching `node_modules` directly.
✅ Correct: Cache the package manager download cache (`~/.npm`) and always run `npm ci`; `node_modules` can have platform-specific binaries and stale files.

---

## 🧠 Tricky Interview Question
**Q:** `cache: npm` is set. You change `package-lock.json` and CI is still just as slow on the first run. Then the second run is fast. Why, and is the cache shared with other branches?

**Answer:** The cache key includes the hash of the lockfile. A changed lockfile means a new key, so the first run is a cache miss (it may use a restore-key fallback but still downloads new packages); the post step saves the new cache and the second run hits it. Caches are scoped: a branch can read caches from its own branch, the base branch, and the default branch, but not from sibling branches. So the first PR run can reuse `main`'s cache, but two different PRs do not share with each other. Caches also count against a 10 GB per-repo limit with least-recently-used eviction.

---

## ⚫ Interview Questions + Answers

Q1: `node-version: 20` vs `20.11.1` vs `lts/*`?
A1: `20` picks the latest 20.x; an exact version pins fully for reproducibility; `lts/*` follows the newest LTS which can change under you. Prefer a major version or exact version from `.nvmrc`.

Q2: What is `node-version-file`?
A2: It reads the version from `.nvmrc`, `.node-version`, `.tool-versions`, or `package.json` `volta`/`engines`, so CI follows the same file developers use.

Q3: What does the `cache` input actually cache?
A3: The package manager's global download cache (npm: `~/.npm`), keyed by OS, architecture and lockfile hash. Not `node_modules`.

Q4: How do you install from a private registry?
A4: Set `registry-url` (and `scope` if needed), then pass `NODE_AUTH_TOKEN` as env in the install step. The action creates a temporary `.npmrc` referencing that variable.

Q5: How do you test on multiple Node versions?
A5: A `strategy.matrix.node` list with `node-version: ${{ matrix.node }}`; use `fail-fast: false` so all versions report.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any Node/React/Next/Nest build or test
- You want reproducible versions and fast installs
- Publishing to npm or GitHub Packages

❌ Avoid when:
- The job runs inside a container image that already has Node (`container: node:20`) with its own caching
- Python-only jobs
- You build only inside Docker (`docker build` handles Node itself)

---

## 📊 Visual Diagram
```
 .nvmrc ("20") ----------+
                         v
   actions/setup-node@v4
     |-- tool cache hit? --yes--> add node 20.x to PATH
     |                    no ---> download node 20.x -> PATH
     |
     |-- cache: npm
     |     key = npm-Linux-X64-<hash(package-lock.json)>
     |        hit  -> restore ~/.npm  (fast npm ci)
     |        miss -> empty cache; post-step saves new one
     v
   npm ci  ->  npm test  ->  npm run build
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `node-version` | Version to install | install करने का version |
| `.nvmrc` | File holding Node version | Node version वाली file |
| `cache` | Package manager cache option | package manager का cache |
| Lockfile | Exact dependency tree file | सटीक dependency सूची |
| `registry-url` | Registry for .npmrc | registry का URL |
| `NODE_AUTH_TOKEN` | Env var with registry token | registry token वाला env |
| Matrix | Run job for many versions | कई versions पर job |

---

## ⚡ 3-Line Summary
English: `setup-node` installs a pinned Node version and caches the package manager download cache.
Read the version from `.nvmrc`, commit your lockfile, and use `npm ci`.
Use `registry-url` with `NODE_AUTH_TOKEN` for private packages and a matrix to test several Node versions.
Hindi: `setup-node` pinned Node version install करती है और package manager का download cache रखती है।
Version `.nvmrc` से पढ़ें, lockfile commit करें और `npm ci` चलाएँ।
Private packages के लिए `registry-url` के साथ `NODE_AUTH_TOKEN` और कई Node versions के लिए matrix इस्तेमाल करें।

---

## ➡️ Next Topic
**305. Setup Python (actions/setup-python)** — the same idea for your FastAPI services.
