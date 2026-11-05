# 295. Sequential Jobs
# हिंदी में: Sequential Jobs (क्रम से चलने वाले jobs)

---

## 🔵 Simple Definition (English)
Sequential jobs run one after another, enforced with `needs:`. A job with `needs: build` starts only after `build` finishes **successfully**; if `build` fails or is skipped, the dependent job is skipped. This creates stages such as build -> test -> deploy. The runner for each job is new, so data is passed via outputs/artifacts, not the filesystem.

## 🔵 सरल परिभाषा (Hindi)
Sequential jobs एक के बाद एक चलते हैं, जिसे `needs:` लागू करता है। `needs: build` वाला job तभी शुरू होता है जब `build` **सफलतापूर्वक** खत्म हो; `build` fail या skip हो तो dependent job skip हो जाता है। इससे build -> test -> deploy जैसे stages बनते हैं। हर job का runner नया होता है, इसलिए data filesystem से नहीं, outputs/artifacts से जाता है।

---

## 🔴 Problem it Solves
Some steps must not start before others: you must not deploy before tests pass, and you must not run the smoke test before the deploy completed. Without explicit ordering, parallel default would deploy untested code. `needs` provides a safety gate and a clear pipeline shape.

## 🔴 यह क्यों बना? (Hindi)
कुछ steps दूसरों से पहले शुरू नहीं होने चाहिए: tests पास होने से पहले deploy नहीं होना चाहिए, और deploy पूरा होने से पहले smoke test नहीं चलना चाहिए। साफ़ क्रम के बिना parallel default untested code deploy कर देता। `needs` सुरक्षा का gate और pipeline का साफ़ ढाँचा देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Job "test" has   needs: build
Step 2 → GitHub waits until build is complete
Step 3 → build success    -> test is queued and runs
         build failure    -> test is SKIPPED (and so is everything depending on test)
         build cancelled  -> test is skipped
Step 4 → Override with  if: always()  (runs regardless)  or  if: failure()  (cleanup, notify)
Step 5 → needs.<job>.result is one of: success | failure | cancelled | skipped
Step 6 → Each job: new runner => pass data via artifacts / outputs
Step 7 → Sequential chain total time = sum of jobs + startup overhead of each
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Job "test" में   needs: build
Step 2 → GitHub build के पूरा होने तक रुकता है
Step 3 → build सफल     -> test queue होकर चलता है
         build fail    -> test SKIP (और test पर निर्भर सब कुछ भी)
         build cancel  -> test skip
Step 4 → Override: if: always() (हमेशा चले) या if: failure() (cleanup, notify)
Step 5 → needs.<job>.result इनमें से एक: success | failure | cancelled | skipped
Step 6 → हर job: नया runner => data artifacts / outputs से भेजें
Step 7 → Sequential chain का कुल समय = jobs का जोड़ + हर job का startup overhead
```

---

## 🟡 Real World Example
A Zomato-like order service deploys to a VPS via `build -> test -> deploy-staging -> smoke-test -> deploy-prod`. Staging deploy must finish before the smoke test, and production deploy happens only after the smoke test passes and a human approves the `production` environment. When the smoke test fails, a `notify-failure` job (`if: failure()`) posts to Slack and the pipeline stops before touching production.

## 🟡 Real Example Hindi mein
Zomato जैसी order service VPS पर `build -> test -> deploy-staging -> smoke-test -> deploy-prod` से deploy होती है। Smoke test से पहले staging deploy पूरा होना चाहिए, और production deploy तब होता है जब smoke test पास हो और कोई इंसान `production` environment approve करे। Smoke test fail हो तो `notify-failure` job (`if: failure()`) Slack पर सूचना देता है और pipeline production को छुए बिना रुक जाती है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/sequential-basic.yml
name: sequential-basic                    # workflow name
on: [push]                                # trigger
jobs:
  build:                                  # stage 1
    runs-on: ubuntu-latest                # runner
    steps:
      - run: echo "building"              # real build goes here
  test:                                   # stage 2
    needs: build                          # starts only after build succeeds
    runs-on: ubuntu-latest
    steps:
      - run: echo "testing"
  deploy:                                 # stage 3
    needs: test                           # starts only after test succeeds
    runs-on: ubuntu-latest
    steps:
      - run: echo "deploying"
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/pipeline.yml
# build -> test -> staging -> smoke -> production (+ failure notification)
name: pipeline                            # workflow name
on:
  push:
    branches: [main]                      # deploy pipeline for main only
permissions:
  contents: read                          # least privilege
concurrency:
  group: pipeline-main                    # never overlap two pipelines on main
  cancel-in-progress: false               # let a running deploy finish
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.t.outputs.tag }}     # image tag for later stages
    steps:
      - uses: actions/checkout@v4
      - id: t
        run: echo "tag=${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"   # short SHA as tag
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci && npm run build      # build once
      - run: tar -czf dist.tgz dist       # package
      - uses: actions/upload-artifact@v4
        with: { name: dist, path: dist.tgz, retention-days: 3 }
  test:
    needs: build                          # gate 1
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci && npm test           # unit tests
  staging:
    needs: [build, test]                  # needs build for outputs, test for the gate
    runs-on: ubuntu-latest
    environment: staging                  # staging secrets
    steps:
      - uses: actions/download-artifact@v4
        with: { name: dist }              # same bytes that were tested
      - run: echo "deploy ${{ needs.build.outputs.tag }} to staging"   # replace with rsync/ssh
  smoke:
    needs: staging                        # after staging deploy completed
    runs-on: ubuntu-latest
    steps:
      - run: curl --fail --retry 5 --retry-delay 3 https://staging.example.com/health   # example URL
  production:
    needs: [build, smoke]                 # only if smoke passed
    runs-on: ubuntu-latest
    environment: production               # required reviewers = manual approval
    steps:
      - uses: actions/download-artifact@v4
        with: { name: dist }
      - run: echo "deploy ${{ needs.build.outputs.tag }} to production"
  notify-failure:
    needs: [build, test, staging, smoke, production]   # watch the whole chain
    if: failure()                         # true when any needed job failed
    runs-on: ubuntu-latest
    steps:
      - run: echo "Pipeline failed at $GITHUB_SHA"   # swap for Slack webhook curl
```

---

## 🟠 My Stack Integration
- **Node/React + Nginx VPS**: build -> test -> deploy (rsync + nginx reload) -> smoke (`curl /health`).
- **FastAPI**: build image -> pytest -> push -> deploy compose -> alembic migration step -> smoke.
- **AWS**: `terraform plan` -> manual approval (environment) -> `terraform apply`.
- **Rollback**: `if: failure()` job re-deploys previous tag from a saved output or file.

```yaml
# Snippet: cleanup that always runs after deploy attempt
  cleanup:
    needs: production
    if: always()                          # run on success, failure or cancel
    runs-on: ubuntu-latest
    steps:
      - run: echo "result was ${{ needs.production.result }}"   # success | failure | cancelled | skipped
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Expecting files from `build` to exist in `test` job.
✅ Correct: New runner. Use artifacts or rebuild.

❌ Mistake 2: Using `if: always()` on a deploy job after test, so it deploys even when tests fail.
✅ Correct: `always()` only for cleanup/notify. Keep deploy on default success rule.

❌ Mistake 3: Making everything sequential, so 5 independent checks take 5x as long.
✅ Correct: Sequence only the dependent chain.

❌ Mistake 4: Deploy job reading `needs.build.outputs.x` without listing `build` in `needs`.
✅ Correct: Name every producer job directly.

❌ Mistake 5: Reusing the same job in a cycle (`a needs b`, `b needs a`).
✅ Correct: GitHub rejects circular dependencies; reshape the graph.

---

## 🧠 Tricky Interview Question
`deploy` has `needs: [test]` and `if: always()`. The `test` job fails. Does `deploy` run? What if you wrote `if: success()` or nothing?

Answer: With `if: always()` yes, deploy runs even though tests failed, which is dangerous. With no `if` at all, the implicit condition is `success()`, so deploy is skipped when a needed job did not succeed. The key rule: if your `if:` contains a status-check function (`always()`, `failure()`, `cancelled()`, `success()`), the implicit `success()` is NOT added. A plain `if: github.ref == 'refs/heads/main'` (no status function) still gets the implicit `success() &&`. A safe pattern for gated jobs is `if: ${{ !cancelled() && needs.test.result == 'success' }}`.

---

## ⚫ Interview Questions + Answers

Q1: How do you run job B after job A?
A1: `needs: A` in job B.

Q2: What if A fails?
A2: B is skipped (default). Override with `if: always()` or `if: failure()`.

Q3: Can `needs` take a list?
A3: Yes, `needs: [a, b]` waits for all listed jobs.

Q4: How do you require manual approval between stages?
A4: Attach an `environment` with required reviewers to the later job.

Q5: How to pass the built output to later stages?
A5: Artifacts for files, job outputs for small values, a registry for images.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Order matters: build before test, test before deploy.
- You need approval gates between stages.
- Later steps need results of earlier ones.

❌ Avoid when:
- Steps are independent (run them in parallel).
- A single job with multiple steps is simpler and faster (shared filesystem, one startup).

---

## 📊 Visual Diagram
```
 build --> test --> staging --> smoke --> [approval] --> production
   |         |         |          |                          |
   +---------+---------+----------+--------------------------+
                          any failure
                               v
                       notify-failure (if: failure())
 Skipped chain: if "test" fails -> staging, smoke, production = skipped
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `needs` | Run after listed jobs | सूचीबद्ध jobs के बाद चले |
| Stage | Group of ordered jobs | क्रमबद्ध jobs का समूह |
| `success()` | Implicit default condition | डिफ़ॉल्ट शर्त |
| `always()` | Run regardless | हर हाल में चले |
| Environment | Gate with approvals/secrets | Approval/secrets वाला gate |
| Smoke test | Quick post-deploy health check | Deploy के बाद की त्वरित जाँच |

---

## ⚡ 3-Line Summary
English: `needs` makes a job wait for others and skips it if they did not succeed.
English: Sequential chains pass data by artifacts/outputs and use environments for approvals.
English: Use `always()` or `failure()` only for cleanup, rollback and notification.
Hindi: `needs` job को दूसरों का इंतज़ार कराता है और उनके सफल न होने पर skip कर देता है।
Hindi: Sequential chains data artifacts/outputs से भेजती हैं और approvals के लिए environments इस्तेमाल करती हैं।
Hindi: `always()` या `failure()` सिर्फ़ cleanup, rollback और notification के लिए इस्तेमाल करें।

---

## ➡️ Next Topic
**296. Job Dependencies (needs:)** — the full semantics of `needs`, graphs, results and conditions.
