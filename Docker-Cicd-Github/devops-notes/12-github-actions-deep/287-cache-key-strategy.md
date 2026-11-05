# 287. Cache Key Strategy
# हिंदी में: Cache Key की रणनीति

---

## 🔵 Simple Definition (English)
A cache key strategy is the rule you use to build the `key` string of `actions/cache` so that the cache changes exactly when its content should change. A good key combines: a manual version prefix, the OS/architecture, the tool version (Node/Python), and a hash of the files that define the content (lockfile). Keys are immutable: once saved, an entry with that key is never overwritten.

## 🔵 सरल परिभाषा (Hindi)
Cache key strategy वह नियम है जिससे आप `actions/cache` की `key` string बनाते हैं ताकि cache ठीक तभी बदले जब उसका content बदलना चाहिए। अच्छी key में होता है: manual version prefix, OS/architecture, tool version (Node/Python), और उन files का hash जो content तय करती हैं (lockfile)। Keys immutable हैं: एक बार save होने के बाद उस key की entry कभी overwrite नहीं होती।

---

## 🔴 Problem it Solves
Two failure modes: (1) key too static (`npm-cache`) so the cache is never refreshed and grows stale or wrong; (2) key too specific (`${{ github.sha }}`) so every commit misses and you pay upload cost with zero benefit. Also, a cache restored from the wrong Node version or OS breaks native modules. Key strategy balances hit rate against correctness.

## 🔴 यह क्यों बना? (Hindi)
दो गलतियाँ होती हैं: (1) key बहुत static (`npm-cache`) तो cache कभी refresh नहीं होता, पुराना/गलत हो जाता है; (2) key बहुत specific (`${{ github.sha }}`) तो हर commit पर miss होता है और upload का खर्च बिना फ़ायदे के। साथ ही गलत Node version या OS का cache native modules तोड़ देता है। Key strategy hit rate और correctness का संतुलन बनाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decide what defines the content (package-lock.json? Dockerfile? source?)
Step 2 → Build key from most stable to most volatile parts:
         <version-prefix>-<os>-<tool-version>-<hash of defining files>
Step 3 → Same inputs => same key => exact hit => no upload needed
Step 4 → Input changes (new dependency) => new key => miss => install => save new key
Step 5 → Add restore-keys (shorter prefixes) so a miss can start from a near cache
Step 6 → Bump the manual prefix (v1 -> v2) to invalidate everything if poisoned
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → तय करें content किससे बनता है (package-lock.json? Dockerfile? source?)
Step 2 → सबसे stable से सबसे volatile हिस्से के क्रम में key बनाएँ:
         <version-prefix>-<os>-<tool-version>-<defining files का hash>
Step 3 → वही inputs => वही key => exact hit => upload की ज़रूरत नहीं
Step 4 → Input बदला (नई dependency) => नई key => miss => install => नई key save
Step 5 → restore-keys (छोटे prefixes) जोड़ें ताकि miss पर भी नज़दीकी cache से शुरू हो
Step 6 → सब कुछ invalid करना हो तो manual prefix बढ़ाएँ (v1 -> v2)
```

---

## 🟡 Real World Example
A fintech team cached `node_modules` with key `modules-${{ hashFiles('**/package-lock.json') }}`. The `**` glob also matched lockfiles inside `node_modules/` from a previous step, so the hash changed every run and the cache never hit. They fixed it with `hashFiles('package-lock.json', 'web/package-lock.json')` and added `node-version` to the key. Hit rate went from 0% to 92%.

## 🟡 Real Example Hindi mein
एक fintech team ने `node_modules` को key `modules-${{ hashFiles('**/package-lock.json') }}` से cache किया। `**` glob पिछले step से `node_modules/` के अंदर की lockfiles भी पकड़ रहा था, इसलिए हर run में hash बदल जाता और cache कभी hit नहीं होता। उन्होंने `hashFiles('package-lock.json', 'web/package-lock.json')` लिखा और key में `node-version` जोड़ा। Hit rate 0% से 92% हो गया।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/key-basic.yml
name: key-basic                           # workflow name
on: [push]                                # trigger
jobs:
  build:
    runs-on: ubuntu-latest                # runner
    steps:
      - uses: actions/checkout@v4         # source code
      - uses: actions/cache@v4            # example version
        with:
          path: ~/.npm                    # what to cache
          # key = OS + hash of lockfile: changes only when dependencies change
          key: npm-${{ runner.os }}-${{ hashFiles('package-lock.json') }}
      - run: npm ci                       # install
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/key-advanced.yml
# Layered key: manual version + os + arch + node + lockfile (+ source for build cache)
name: key-advanced                        # workflow name
on:
  push:
    branches: [main]                      # main warms caches for everyone
  pull_request:                           # PRs read main's cache
env:
  CACHE_VERSION: v3                       # bump to invalidate all caches at once
  NODE_VERSION: '20'                      # single source of truth for the Node version
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}   # use the same variable
      - name: Dependency cache
        uses: actions/cache@v4
        with:
          path: ~/.npm                    # npm download cache
          key: ${{ env.CACHE_VERSION }}-npm-${{ runner.os }}-${{ runner.arch }}-node${{ env.NODE_VERSION }}-${{ hashFiles('package-lock.json') }}
          restore-keys: |
            ${{ env.CACHE_VERSION }}-npm-${{ runner.os }}-${{ runner.arch }}-node${{ env.NODE_VERSION }}-
      - run: npm ci                       # reproducible install
      - name: Build output cache (changes often)
        uses: actions/cache@v4
        with:
          path: .next/cache               # framework build cache
          # include source hash so a cache is saved per source change,
          # but fall back to the same lockfile family
          key: ${{ env.CACHE_VERSION }}-next-${{ runner.os }}-${{ hashFiles('package-lock.json') }}-${{ hashFiles('src/**/*.[jt]s', 'src/**/*.[jt]sx') }}
          restore-keys: |
            ${{ env.CACHE_VERSION }}-next-${{ runner.os }}-${{ hashFiles('package-lock.json') }}-
            ${{ env.CACHE_VERSION }}-next-${{ runner.os }}-
      - run: npm run build                # build uses the restored cache
```

---

## 🟠 My Stack Integration
| Stack part | What defines content | Suggested key |
|---|---|---|
| React / Node | `package-lock.json`, Node version | `v1-npm-${{ runner.os }}-node20-${{ hashFiles('package-lock.json') }}` |
| FastAPI | `requirements.txt` / `poetry.lock`, Python version | `v1-pip-${{ runner.os }}-py3.12-${{ hashFiles('requirements*.txt') }}` |
| Docker layers | Dockerfile, base image | BuildKit `type=gha,scope=api` |
| Terraform (AWS) | `.terraform.lock.hcl` | `v1-tf-${{ hashFiles('.terraform.lock.hcl') }}` |

```yaml
# Snippet: monorepo - one cache per app using a "scope" in the key
      - uses: actions/cache@v4
        with:
          path: ~/.npm
          key: v1-npm-api-${{ runner.os }}-${{ hashFiles('api/package-lock.json') }}   # api only
      - uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: v1-pip-fastapi-${{ runner.os }}-${{ hashFiles('fastapi/requirements.txt') }}   # fastapi only
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Key without a hash (`key: my-cache`). It saves once and never updates.
✅ Correct: Include `hashFiles()` of the lockfile.

❌ Mistake 2: `key: ${{ github.sha }}`. Always a miss.
✅ Correct: Use sha only for build outputs you want per commit, with `restore-keys` for the fallback.

❌ Mistake 3: `hashFiles('**/package-lock.json')` in a repo where earlier steps create nested lockfiles.
✅ Correct: Use explicit paths or exclude: `hashFiles('**/package-lock.json', '!**/node_modules/**')`.

❌ Mistake 4: Ignoring OS/arch/tool version, so a Linux cache lands on macOS runners or a different Node.
✅ Correct: Add `runner.os`, `runner.arch`, tool version.

❌ Mistake 5: Putting secrets or PR titles (user input) in the key.
✅ Correct: Keys are visible in logs. Use only non-sensitive, controlled values.

---

## 🧠 Tricky Interview Question
You changed `package.json` (a new dependency) but forgot to commit the updated `package-lock.json`. CI still shows a cache hit and installs old dependencies. Why does this show up as a "works on CI, fails on prod" bug, and what key rule protects you?

Answer: The key hashes only the lockfile, so unchanged lockfile => same key => same cache. With `npm ci`, a mismatch between `package.json` and lockfile actually fails the install, which is the safety net. With `npm install`, it would silently resolve something different. Rule: hash the file that is the source of truth (lockfile), use `npm ci`, and never hash only `package.json` unless you also have no lockfile. For apps without a lockfile, hash both and pin versions.

---

## ⚫ Interview Questions + Answers

Q1: What makes a good cache key?
A1: Deterministic, derived from content-defining files, includes OS/arch/tool version, and has a manual version prefix for forced invalidation.

Q2: Why can't we update an existing cache entry?
A2: Keys are immutable in the cache service to avoid races between concurrent jobs; to update, create a new key.

Q3: How do you invalidate all caches quickly?
A3: Bump the prefix (`v2-`), or delete caches with `gh cache delete --all` / the Actions UI.

Q4: When is `github.sha` in a key appropriate?
A4: For incremental build outputs where each commit may add small changes; combine with restore-keys so the previous commit's cache is used as a start.

Q5: How do keys interact with branch scoping?
A5: Lookup checks the current branch, then base/default branch caches. Feature branches reuse main's caches, so the same key format across branches is important.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Designing any `actions/cache` step.
- Fixing low hit rates or "mystery stale cache" bugs.
- Monorepos with several apps.

❌ Avoid when:
- Over-engineering a tiny repo; `setup-node` `cache: npm` already builds a good key.
- Trying to use cache keys as version control for artifacts.

---

## 📊 Visual Diagram
```
 key = v3 - npm - Linux - X64 - node20 - 9f2c1ab...
       |     |      |      |      |        |
       |     |      |      |      |        +-- hash(package-lock.json)  (content)
       |     |      |      |      +----------- tool version
       |     |      |      +------------------ CPU arch
       |     |      +------------------------- OS
       |     +-------------------------------- cache kind
       +-------------------------------------- manual invalidation switch

 stable  <-------------------------------------------->  volatile
 (shared by many runs)                         (changes often)
 restore-keys drop the volatile tail:  v3-npm-Linux-X64-node20-
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Immutable key | Saved entry never changes | Save होने के बाद न बदलने वाली key |
| `hashFiles()` | SHA-256 over files | Files का SHA-256 hash |
| Version prefix | Manual invalidation knob | हाथ से cache invalid करने का prefix |
| `runner.os` | OS of the runner | Runner का OS |
| Hit rate | % of runs with a hit | कितने runs में hit मिला |
| Poisoned cache | Bad content stuck in cache | खराब content वाला cache |

---

## ⚡ 3-Line Summary
English: Build keys from version prefix, OS/arch, tool version and a lockfile hash.
English: Too static means stale caches; too specific (sha) means no hits.
English: Use restore-keys for near matches and bump the prefix to invalidate everything.
Hindi: Key को version prefix, OS/arch, tool version और lockfile hash से बनाएँ।
Hindi: बहुत static मतलब पुराना cache; बहुत specific (sha) मतलब कभी hit नहीं।
Hindi: नज़दीकी match के लिए restore-keys और सब कुछ invalid करने के लिए prefix बढ़ाएँ।

---

## ➡️ Next Topic
**288. Cache Restore Keys** — how fallback prefixes pick a near-match cache.
