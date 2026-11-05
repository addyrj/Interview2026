# 273. Functions in Expressions
# हिंदी में: Expressions में Functions

---

## 🔵 Simple Definition (English)
Built-in functions you can call inside `${{ }}`: `contains`, `startsWith`, `endsWith`, `format`, `join`, `toJSON`, `fromJSON`, `hashFiles`, and job status functions `success()`, `failure()`, `always()`, `cancelled()`.
You cannot define your own; only these built-ins exist.

## 🔵 सरल परिभाषा (Hindi)
`${{ }}` के अंदर call होने वाले built-in functions: `contains`, `startsWith`, `endsWith`, `format`, `join`, `toJSON`, `fromJSON`, `hashFiles`, और job status functions `success()`, `failure()`, `always()`, `cancelled()`।
अपने functions define नहीं कर सकते; सिर्फ यही built-ins हैं।

---

## 🔴 Problem it Solves
Operators alone cannot answer "does the commit message contain [skip ci]", "build a cache key from package-lock.json", "run a cleanup step even when tests fail", or "turn a JSON string output into a matrix". Functions fill those gaps without extra scripting.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ operators से यह नहीं पूछ सकते "commit message में [skip ci] है क्या", "package-lock.json से cache key बनाओ", "tests fail होने पर भी cleanup चलाओ", या "JSON string output को matrix बनाओ"। Functions ये gaps बिना extra scripting के भरते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write function name + args: contains(github.event.head_commit.message, 'skip')
Step 2 → Args are evaluated first (contexts resolved)
Step 3 → Function returns a value (bool / string / object)
Step 4 → Result is used by if: / env: / with: / matrix
Step 5 → Status functions (success/failure/always) are special: they
         decide whether a step runs after earlier steps failed
Step 6 → hashFiles() reads files from $GITHUB_WORKSPACE on the runner
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Function name + args लिखो: contains(github.event.head_commit.message, 'skip')
Step 2 → पहले args evaluate होते हैं (contexts resolve)
Step 3 → Function value return करता है (bool / string / object)
Step 4 → Result if: / env: / with: / matrix में use होता है
Step 5 → Status functions (success/failure/always) खास हैं: ये तय करते हैं कि
         पिछला step fail होने के बाद अगला step चले या नहीं
Step 6 → hashFiles() runner पर $GITHUB_WORKSPACE की files पढ़ता है
```

---

## 🟡 Real World Example
A Swiggy-like backend: dependency cache key uses `hashFiles('**/package-lock.json')` so the cache refreshes only when dependencies change. A Slack notification step uses `if: failure()` to alert on broken builds, and a cleanup step uses `if: always()` to stop the test database container whatever happens.

## 🟡 Real Example Hindi mein
Swiggy जैसा backend: dependency cache key `hashFiles('**/package-lock.json')` से बनती है, ताकि cache तभी बदले जब dependencies बदलें। Slack notification step `if: failure()` से broken build पर alert देता है, और cleanup step `if: always()` से हर हाल में test database container बंद करता है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/functions-basic.yml
name: functions-basic                  # workflow name
on: push                               # run on push

jobs:
  demo:
    runs-on: ubuntu-latest             # runner
    steps:
      - uses: actions/checkout@v4      # example version; needed so hashFiles sees files

      - name: contains / startsWith / endsWith
        run: |
          echo "msg has fix?  ${{ contains(github.event.head_commit.message, 'fix') }}"   # true/false
          echo "is release?   ${{ startsWith(github.ref, 'refs/tags/v') }}"              # tag check
          echo "is yaml?      ${{ endsWith('ci.yml', '.yml') }}"                          # suffix check

      - name: format and join
        run: |
          echo "${{ format('Deploying {0} to {1}', github.sha, 'prod') }}"   # {0},{1} placeholders
          echo "${{ join(fromJSON('["a","b","c"]'), '-') }}"                  # prints a-b-c

      - name: toJSON for debugging
        run: echo '${{ toJSON(github.event_name) }}'     # quoted JSON string

      - name: hashFiles
        run: echo "lock hash=${{ hashFiles('package-lock.json') }}"   # empty string if file missing
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/functions-advanced.yml
name: functions-advanced               # workflow name
on:
  push:
    branches: [main]                   # main only

jobs:
  plan:
    runs-on: ubuntu-latest
    outputs:
      services: ${{ steps.pick.outputs.services }}   # JSON array string
    steps:
      - id: pick                       # step id for outputs
        run: echo 'services=["api","worker"]' >> "$GITHUB_OUTPUT"   # emit JSON

  build:
    needs: plan                        # wait for plan
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: ${{ fromJSON(needs.plan.outputs.services) }}  # JSON -> real array
    steps:
      - uses: actions/checkout@v4      # example version
      - name: Cache key demo
        run: echo "key=${{ runner.os }}-${{ matrix.service }}-${{ hashFiles('**/package-lock.json', '**/requirements.txt') }}"
        # hashFiles accepts several patterns; result is a SHA-256 string
      - name: Run tests
        run: echo "tests for ${{ matrix.service }}"   # replace with real test command
      - name: Notify on failure
        if: failure()                  # runs only if an earlier step failed
        run: echo "send slack alert"   # curl to a webhook in real life
      - name: Cleanup
        if: always()                   # runs on success, failure and cancel
        run: echo "docker compose down -v"   # always stop test containers
      - name: Only when not cancelled
        if: ${{ !cancelled() && contains(fromJSON('["main","release"]'), github.ref_name) }}
        run: echo "post-build report"  # contains(array, item) checks array membership
```
Not run locally; YAML structure parsed only. Check `hashFiles` limits (workspace only, 120 s timeout) in the current docs.

---

## 🟠 My Stack Integration
For a monorepo with Node.js API, FastAPI service and React app, key your caches on each lock file, and use `failure()` to print Nginx/Docker logs from the VPS when a deploy fails.

```yaml
# snippet: per-stack cache keys + failure diagnostics
      - uses: actions/cache@v4         # example version
        with:
          path: ~/.npm                 # npm cache folder
          key: npm-${{ hashFiles('api/package-lock.json') }}   # Node.js API
      - uses: actions/cache@v4
        with:
          path: ~/.cache/pip           # pip cache folder
          key: pip-${{ hashFiles('fastapi/requirements.txt') }}  # FastAPI
      - name: Show remote logs on failure
        if: failure()
        run: ssh deploy@${{ vars.VPS_HOST }} "docker compose logs --tail=100 && sudo nginx -t"
        # assumes SSH set up earlier; VPS_HOST is a repository variable
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `if: success()` expectations after a failed step and then adding a custom `if: steps.x.outcome == 'failure'` without `always()`; the step is still skipped.
✅ Correct: A custom `if:` without a status function gets an implicit `success() &&`. Add `always()` or `failure()` explicitly.

❌ Mistake 2: Calling `hashFiles` before `actions/checkout`; files do not exist, result is empty.
✅ Correct: Checkout first, then compute the key.

❌ Mistake 3: Passing a JSON string to `matrix` without `fromJSON`.
✅ Correct: `matrix: { service: ${{ fromJSON(needs.plan.outputs.services) }} }`.

❌ Mistake 4: `contains('abc', 'B')` expecting false; matching is case-insensitive.
✅ Correct: Normalise or use a shell test when case matters.

---

## 🧠 Tricky Interview Question
A cleanup step has `if: steps.test.outcome == 'failure'` but never runs when tests fail. Why?

Answer: A step with an `if:` that has no status-check function is wrapped as `success() && (your condition)`. After the failed test step, `success()` is false, so the step is skipped. Use `if: always() && steps.test.outcome == 'failure'` (or `failure() && ...`).

---

## ⚫ Interview Questions + Answers

Q1: Difference between `steps.x.outcome` and `steps.x.conclusion`?
A1: `outcome` is the raw result before `continue-on-error` is applied; `conclusion` is the result after it. Both can be success, failure, cancelled, skipped.

Q2: What does `always()` do vs `failure()`?
A2: `always()` runs the step even if cancelled or failed; `failure()` runs only when a previous step/job failed. `always()` can run after a cancel, so prefer `!cancelled()` when you do not want that.

Q3: What does `hashFiles` return when nothing matches?
A3: An empty string. Cache keys then collide, so check patterns.

Q4: Why `fromJSON`?
A4: Outputs and inputs are strings. `fromJSON` parses a JSON string to an object/array/number/boolean so you can build matrices or compare numbers.

Q5: How do you debug a context?
A5: `echo '${{ toJSON(github) }}'` (never print `secrets` context; secrets are masked but do not rely on it).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Cache keys, dynamic matrices, status gates, message checks.
- Debug dumps with `toJSON`.

❌ Avoid when:
- You need functions not provided (regex, date math): use shell/script.
- `toJSON(github)` in public logs where event data is sensitive.

---

## 📊 Visual Diagram
```
 package-lock.json --hashFiles()--> a3f9...e1  --> cache key "Linux-npm-a3f9...e1"

 step1 ok --> step2 FAIL --> step3 (if: failure())  RUNS  -> alert
                         \-> step4 (if: always())   RUNS  -> cleanup
                         \-> step5 (default)        SKIP
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Function | Built-in helper inside `${{ }}` | Built-in helper |
| Status check function | success/failure/always/cancelled | Step चलने की शर्त वाले functions |
| hashFiles | SHA-256 of matched files | Files का hash |
| fromJSON / toJSON | Parse / serialize JSON | JSON parse / बनाना |
| outcome vs conclusion | Result before / after continue-on-error | continue-on-error से पहले / बाद का result |

---

## ⚡ 3-Line Summary
English: Only built-in functions exist: string helpers, JSON helpers, hashFiles, status checks.
A custom `if:` is implicitly `success() &&`, so add `always()`/`failure()` for cleanup.
Use `fromJSON` for dynamic matrices and `hashFiles` for cache keys.

Hindi: सिर्फ built-in functions हैं: string helpers, JSON helpers, hashFiles, status checks।
Custom `if:` में अपने-आप `success() &&` लगता है, इसलिए cleanup के लिए `always()`/`failure()` जोड़ो।
Dynamic matrix के लिए `fromJSON` और cache key के लिए `hashFiles` use करो।

---

## ➡️ Next Topic
**274. Environment Variables** — after expressions, see how `env:` values reach your shell commands at workflow, job and step level.
