# 288. Cache Restore Keys
# हिंदी में: Cache Restore Keys (fallback keys)

---

## 🔵 Simple Definition (English)
`restore-keys` is an ordered, multi-line list of key **prefixes** that `actions/cache` tries when the exact `key` is not found. The service returns the most recently created cache whose key starts with the first matching prefix. A restore-key match counts as a partial hit: `cache-hit` is `'false'`, files are still restored, and the job saves a new cache under the full `key` after it finishes.

## 🔵 सरल परिभाषा (Hindi)
`restore-keys` key **prefixes** की क्रमबद्ध multi-line list है जिसे `actions/cache` तब आज़माता है जब exact `key` न मिले। Service पहले मेल खाने वाले prefix से शुरू होने वाला सबसे हाल का बना cache लौटाती है। Restore-key match आंशिक hit है: `cache-hit` `'false'` रहता है, files फिर भी restore होती हैं, और job खत्म होने पर पूरी `key` के नाम से नया cache save होता है।

---

## 🔴 Problem it Solves
Without fallbacks, adding one npm package changes the lockfile hash, the exact key misses, and the whole dependency tree downloads again, even though 99% of it is unchanged. Restore keys start from the previous cache (almost complete) and the package manager only fetches the delta. This matters for incremental build caches (Gradle, `.next/cache`, Rust `target/`) where "close enough" is hugely faster than "nothing".

## 🔴 यह क्यों बना? (Hindi)
Fallback के बिना, एक npm package जोड़ने से lockfile hash बदलता है, exact key miss होती है, और पूरा dependency tree फिर download होता है, जबकि 99% वही है। Restore keys पिछले (लगभग पूरे) cache से शुरू करती हैं और package manager सिर्फ़ फ़र्क़ लाता है। यह incremental build caches (Gradle, `.next/cache`, Rust `target/`) में बहुत मायने रखता है, जहाँ "लगभग सही" "कुछ नहीं" से कहीं तेज़ है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Service tries the exact "key"  -> hit? stop (cache-hit = true)
Step 2 → Miss: take restore-keys in the written order, top to bottom
Step 3 → For each prefix, find caches whose key STARTS WITH it
Step 4 → If several match, newest one (by creation time) wins
Step 5 → Restore it (cache-hit = false, but files present)
Step 6 → Build/install updates the files (delta only)
Step 7 → Post step saves everything under the NEW exact key
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Service पहले exact "key" आज़माती है -> hit? रुक जाओ (cache-hit = true)
Step 2 → Miss: restore-keys को लिखे क्रम में, ऊपर से नीचे लो
Step 3 → हर prefix के लिए वे caches खोजो जिनकी key उससे शुरू होती है
Step 4 → कई मिलें तो सबसे नया (creation time से) जीतता है
Step 5 → उसे restore करो (cache-hit = false, पर files मौजूद)
Step 6 → Build/install files को update करता है (सिर्फ़ delta)
Step 7 → Post step सब कुछ नई exact key के नाम से save करता है
```

---

## 🟡 Real World Example
A Java/Gradle microservice repo had a 1.5 GB Gradle cache. Every dependency bump meant a cold 6-minute build. With `restore-keys: gradle-${{ runner.os }}-`, the new run restored the previous cache, downloaded only the changed jars, and the build took 90 seconds. The same applies to a Node `.next/cache` for a Swiggy-like storefront, where the previous build's cache makes the incremental compile fast.

## 🟡 Real Example Hindi mein
एक Java/Gradle microservice repo में 1.5 GB का Gradle cache था। हर dependency bump पर 6 मिनट का cold build होता था। `restore-keys: gradle-${{ runner.os }}-` लगाने पर नया run पिछला cache restore करता, सिर्फ़ बदले jars download होते, और build 90 सेकंड में हो गया। यही बात Swiggy जैसे storefront के Node `.next/cache` पर लागू होती है, जहाँ पिछले build का cache incremental compile तेज़ कर देता है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/restore-basic.yml
name: restore-basic                       # workflow name
on: [push]                                # trigger
jobs:
  build:
    runs-on: ubuntu-latest                # runner
    steps:
      - uses: actions/checkout@v4         # source
      - id: c                             # id so we can inspect outputs
        uses: actions/cache@v4            # example version
        with:
          path: ~/.npm                    # cached directory
          key: npm-${{ runner.os }}-${{ hashFiles('package-lock.json') }}   # exact key
          restore-keys: |
            npm-${{ runner.os }}-
      - run: echo "exact hit = '${{ steps.c.outputs.cache-hit }}'"   # '', 'true' or 'false'
      - run: npm ci                       # installs only what is missing from restored cache
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/restore-advanced.yml
# Ordered fallbacks from most specific to most generic + info in the job summary
name: restore-advanced                    # workflow name
on:
  push:
    branches: [main]
  pull_request:
env:
  V: v2                                   # manual invalidation prefix
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - name: Restore build cache
        id: bc
        uses: actions/cache@v4
        with:
          path: |
            .next/cache
            node_modules/.cache
          # EXACT key: unique per lockfile + source version
          key: ${{ env.V }}-build-${{ runner.os }}-${{ hashFiles('package-lock.json') }}-${{ hashFiles('src/**') }}
          # FALLBACKS (tried in order, each is a PREFIX):
          #  1) same dependencies, older source  -> best near-match
          #  2) any build cache for this OS      -> still useful
          restore-keys: |
            ${{ env.V }}-build-${{ runner.os }}-${{ hashFiles('package-lock.json') }}-
            ${{ env.V }}-build-${{ runner.os }}-
      - run: npm ci
      - run: npm run build
      - name: Report cache result         # visible on the run summary page
        if: always()                      # even when the build failed
        run: |
          echo "### Cache" >> "$GITHUB_STEP_SUMMARY"
          echo "- exact hit: '${{ steps.bc.outputs.cache-hit }}'" >> "$GITHUB_STEP_SUMMARY"
          echo "- matched key: ${{ steps.bc.outputs.cache-matched-key }}" >> "$GITHUB_STEP_SUMMARY"
```
(`cache-matched-key` is an output of `actions/cache@v4`; confirm in the Action README for your version.)

---

## 🟠 My Stack Integration
- **React/Vite/Next**: fallback to the previous build cache for fast incremental builds.
- **FastAPI**: pip cache with `restore-keys: pip-${{ runner.os }}-py3.12-` so adding one library does not redownload numpy.
- **Docker**: BuildKit handles layer fallback itself, you rarely need restore-keys there.
- **Monorepo on VPS pipeline**: order fallbacks by app so `web` never restores `api` data.

```yaml
# Snippet: FastAPI pip fallback
      - uses: actions/cache@v4
        with:
          path: ~/.cache/pip              # pip wheel cache
          key: pip-${{ runner.os }}-py3.12-${{ hashFiles('api/requirements.txt') }}
          restore-keys: |
            pip-${{ runner.os }}-py3.12-
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: A restore-key that is too generic (`cache-`), restoring another project's or another OS's data.
✅ Correct: Keep OS, tool version and cache kind inside the prefix.

❌ Mistake 2: Thinking restore-keys are regexes or globs. They are plain prefixes.
✅ Correct: Write the leading part of the key, ending with `-`.

❌ Mistake 3: Placing the generic prefix first. Order matters (first match wins), the generic one would shadow better matches.
✅ Correct: Most specific first, most generic last.

❌ Mistake 4: Using restore-keys for correctness-critical data (compiled artifacts reused blindly).
✅ Correct: Only for caches the tool can validate/repair itself (npm, pip, Gradle, incremental compilers).

❌ Mistake 5: Cache growth: each new key stores a full copy plus restored stale files, so size creeps up.
✅ Correct: Prune before save (e.g. `npm cache verify`, `pip cache purge` of old wheels) or periodically bump the prefix.

---

## 🧠 Tricky Interview Question
Your logs say "Cache restored from key: npm-Linux-aaa111", but `steps.c.outputs.cache-hit` is `'false'`. A colleague says that is a bug. Is it?

Answer: No. `cache-hit` is `'true'` only when the exact `key` matched. Here a restore-key prefix matched an older entry (`aaa111`), so files were restored, `cache-hit` is `'false'`, and the post step will save a new cache under the current key. Conditions like `if: steps.c.outputs.cache-hit != 'true'` for "install" are therefore correct: you still run the install to fix the delta. A key point to add in the interview: the empty string appears when nothing matched at all.

---

## ⚫ Interview Questions + Answers

Q1: What is the lookup order?
A1: Exact key, then each restore key in order; for prefix matches the newest cache with that prefix.

Q2: Is the restored cache saved again under the old key?
A2: No. It is saved under the new exact key, as long as the job succeeds.

Q3: Can restore-keys cross branches?
A3: Scope rules still apply: current branch, base branch, default branch. A PR's job can restore from `main` caches, but not from sibling feature branches.

Q4: Why use `restore-keys` with a build cache but not with, say, a compiled binary used for deploy?
A4: Build tools know how to reuse partial state safely; a deploy binary must match source exactly, so use an exact key or artifacts.

Q5: Does a restore-key hit reduce correctness risk?
A5: It slightly increases it (stale files). Mitigate with `npm ci`/clean steps, version prefix and periodic invalidation.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Large caches where deltas are small (Gradle, node, pip, Rust).
- Incremental compilation caches.
- You want PRs to start from main's cache.

❌ Avoid when:
- Data must match exactly (deploy bundles).
- Cache is tiny and cold start is cheap.
- Prefix would be too generic and mix unrelated data.

---

## 📊 Visual Diagram
```
 want key:   v2-build-Linux-LOCK2-SRC9     (miss)
                    |
   restore-keys #1: v2-build-Linux-LOCK2-  --> any entry? (newest)
        found: v2-build-Linux-LOCK2-SRC7   --> RESTORE (cache-hit=false)
                    |
   (if #1 had nothing)
   restore-keys #2: v2-build-Linux-         --> newest: v2-build-Linux-LOCK1-SRC4
                    |
   (if nothing) -> cold build, cache-hit=''
                    v
   build updates files -> post step saves as v2-build-Linux-LOCK2-SRC9
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Restore key | Fallback key prefix | Fallback key prefix |
| Partial hit | Prefix match, `cache-hit=false` | आंशिक hit |
| Prefix match | Key starts with text | Key जिस text से शुरू हो |
| `cache-matched-key` | Key that was restored | जो key restore हुई |
| Delta | Only changed parts | सिर्फ़ बदला हुआ हिस्सा |
| Scope | Branch visibility of caches | Cache किन branches को दिखता है |

---

## ⚡ 3-Line Summary
English: `restore-keys` are ordered prefixes tried after an exact-key miss; newest match wins.
English: A prefix match restores files but `cache-hit` stays false, and a new cache is saved.
English: Put specific prefixes first, keep OS/tool in them, and use only for self-healing caches.
Hindi: `restore-keys` exact-key miss के बाद आज़माए जाने वाले क्रमबद्ध prefixes हैं; सबसे नया match जीतता है।
Hindi: Prefix match में files restore होती हैं पर `cache-hit` false रहता है, और नया cache save होता है।
Hindi: Specific prefixes पहले रखें, उनमें OS/tool रखें, और सिर्फ़ self-healing caches के लिए इस्तेमाल करें।

---

## ➡️ Next Topic
**289. Job Outputs** — passing small values (versions, flags) from one job to another.
