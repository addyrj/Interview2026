# 296. Job Dependencies (needs:)
# हिंदी में: Job Dependencies (needs:)

---

## 🔵 Simple Definition (English)
`jobs.<job_id>.needs` takes a job id or a list of ids that must complete before this job starts. It builds a directed acyclic graph (DAG) of jobs. By default the job runs only if all needed jobs **succeeded**. The `needs` context exposes `needs.<id>.result` (`success`, `failure`, `cancelled`, `skipped`) and `needs.<id>.outputs.<name>` of the **directly** listed jobs only.

## 🔵 सरल परिभाषा (Hindi)
`jobs.<job_id>.needs` एक job id या ids की list लेता है जिन्हें इस job से पहले पूरा होना है। यह jobs का directed acyclic graph (DAG) बनाता है। Default रूप से job तभी चलता है जब सारे needed jobs **सफल** हों। `needs` context सिर्फ़ **सीधे** लिखे jobs का `needs.<id>.result` (`success`, `failure`, `cancelled`, `skipped`) और `needs.<id>.outputs.<name>` देता है।

---

## 🔴 Problem it Solves
Pipelines are graphs: tests need a build, deploy needs tests and a scan, notification needs everything. Without a way to describe dependencies, you would use one giant job (slow, no parallelism) or fragile scheduling. `needs` lets independent branches run in parallel and joins them where required, with automatic skipping when upstream fails.

## 🔴 यह क्यों बना? (Hindi)
Pipelines graph होती हैं: tests को build चाहिए, deploy को tests और scan, notification को सब कुछ। Dependencies बताने का तरीका न हो तो या एक विशाल job (धीमा, parallelism नहीं) या नाज़ुक scheduling। `needs` स्वतंत्र शाखाओं को parallel चलने देता है, ज़रूरत की जगह उन्हें जोड़ता है, और upstream fail हो तो अपने आप skip करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write  needs: build            (single)  or  needs: [build, scan]  (all of them)
Step 2 → GitHub validates the graph: unknown id or a cycle => workflow is invalid
Step 3 → A job becomes runnable when ALL needed jobs are finished
Step 4 → Default condition is  success() && (all needs succeeded)
Step 5 → If a needed job failed/skipped/cancelled, this job is skipped
         unless  if: always() | failure() | !cancelled()  etc. is used
Step 6 → Inside the job: needs.<id>.result and needs.<id>.outputs.* (direct needs only)
Step 7 → "needs.*.result" with contains() lets an aggregator inspect many jobs at once
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → लिखें  needs: build            (एक)  या  needs: [build, scan]  (सबके लिए)
Step 2 → GitHub graph validate करता है: अनजान id या cycle => workflow अमान्य
Step 3 → Job तब runnable होता है जब सारे needed jobs खत्म हो जाएँ
Step 4 → Default शर्त  success() && (सारे needs सफल)
Step 5 → कोई needed job fail/skip/cancel हो तो यह job skip होता है
         जब तक  if: always() | failure() | !cancelled()  आदि न लगा हो
Step 6 → Job के अंदर: needs.<id>.result और needs.<id>.outputs.* (सिर्फ़ सीधे needs)
Step 7 → "needs.*.result" और contains() से aggregator कई jobs एक साथ जाँच सकता है
```

---

## 🟡 Real World Example
An e-commerce release workflow: `lint`, `unit`, `build-web`, `build-api` run in parallel. `integration` needs `[build-web, build-api]` (it spins up both). `scan` needs `build-api`. `deploy` needs `[unit, lint, integration, scan]`. `notify` needs `[deploy]` with `if: always()` so ops hear about failures too. The DAG shows in the Actions UI as a graph, so reviewers instantly see which stage blocked a release.

## 🟡 Real Example Hindi mein
E-commerce release workflow: `lint`, `unit`, `build-web`, `build-api` parallel चलते हैं। `integration` को `[build-web, build-api]` चाहिए (दोनों चलाता है)। `scan` को `build-api` चाहिए। `deploy` को `[unit, lint, integration, scan]` चाहिए। `notify` को `[deploy]` चाहिए और `if: always()` है ताकि failure की खबर ops को भी मिले। Actions UI में DAG graph की तरह दिखता है, इसलिए reviewers तुरंत देखते हैं कि कौन सा stage release रोक रहा है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/needs-basic.yml
name: needs-basic                         # workflow name
on: [push]                                # trigger
jobs:
  a:                                      # root job: no needs
    runs-on: ubuntu-latest
    steps:
      - run: echo "A"
  b:                                      # depends on one job
    needs: a                              # waits for a
    runs-on: ubuntu-latest
    steps:
      - run: echo "B"
  c:                                      # runs in parallel with b (both need only a)
    needs: a
    runs-on: ubuntu-latest
    steps:
      - run: echo "C"
  d:                                      # join: waits for both b and c
    needs: [b, c]                         # list = wait for all
    runs-on: ubuntu-latest
    steps:
      - run: echo "D"
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/dag.yml
# Diamond graph + outputs + results + conditional notify + cleanup
name: dag                                 # workflow name
on:
  push:
    branches: [main]
permissions:
  contents: read                          # least privilege
jobs:
  meta:
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.t.outputs.tag }}     # exposed to direct dependents only
    steps:
      - id: t
        run: echo "tag=${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"   # short sha
  build-web:
    needs: meta
    runs-on: ubuntu-latest
    steps:
      - run: echo "web ${{ needs.meta.outputs.tag }}"
  build-api:
    needs: meta
    runs-on: ubuntu-latest
    steps:
      - run: echo "api ${{ needs.meta.outputs.tag }}"
  integration:
    needs: [build-web, build-api]         # join of two builds
    runs-on: ubuntu-latest
    steps:
      - run: echo "integration tests"
  scan:
    needs: build-api                      # branch that only needs the API
    runs-on: ubuntu-latest
    steps:
      - run: echo "image scan"
  deploy:
    needs: [meta, integration, scan]      # list meta too, to read its outputs (not transitive)
    runs-on: ubuntu-latest
    environment: production               # approval gate
    steps:
      - run: echo "deploy ${{ needs.meta.outputs.tag }}"
  notify:
    needs: [integration, scan, deploy]
    if: always()                          # also run when upstream failed
    runs-on: ubuntu-latest
    steps:
      - name: Summarize
        env:
          RESULTS: ${{ toJSON(needs) }}   # {"integration":{"result":"success",...},...}
        run: echo "$RESULTS"              # inspect results safely through env
      - name: Fail loudly if deploy did not succeed
        if: needs.deploy.result != 'success'      # failure, cancelled or skipped
        run: |
          echo "deploy result: ${{ needs.deploy.result }}"
          exit 1
```

---

## 🟠 My Stack Integration
- **Node + FastAPI + React**: `web`, `api`, `fastapi` build jobs run in parallel; `integration` (docker compose up in CI) needs all of them.
- **VPS/Nginx**: `deploy` needs `[build, test, scan]`; `smoke` needs `deploy`; `rollback` runs with `if: failure() && needs.deploy.result == 'success'` (deploy ok but smoke failed).
- **AWS**: `terraform-plan` -> `approval` environment -> `terraform-apply`.
- **Reusable workflows**: a caller job's `needs` can depend on a `uses:` job; its outputs flow through `workflow_call.outputs`.

```yaml
# Snippet: rollback only when deploy succeeded but smoke test failed
  rollback:
    needs: [deploy, smoke]
    if: ${{ always() && needs.deploy.result == 'success' && needs.smoke.result == 'failure' }}
    runs-on: ubuntu-latest
    steps:
      - run: echo "ssh to VPS and switch symlink to previous release"
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Expecting transitive access (`c` needs `b`, `b` needs `a`, reading `needs.a.outputs`).
✅ Correct: List `a` in `c`'s `needs` as well, or forward output via `b`.

❌ Mistake 2: Using a job `name:` instead of the job id in `needs`.
✅ Correct: Use the YAML key (`build-api`), not the display name.

❌ Mistake 3: `if: needs.test.result == 'failure'` without `always()` or `failure()`. The implicit `success()` skips the job first.
✅ Correct: `if: always() && needs.test.result == 'failure'`.

❌ Mistake 4: Circular dependency `a -> b -> a`.
✅ Correct: Split shared work into a third job both depend on.

❌ Mistake 5: Treating `skipped` as success in gates.
✅ Correct: Check explicitly: `contains(needs.*.result, 'failure')` and `'cancelled'`; decide what to do with `skipped` (e.g. conditional jobs).

---

## 🧠 Tricky Interview Question
An aggregator job `ready` has `needs: [lint, unit]` and no `if`. `unit` fails. Branch protection requires `ready`. What does the PR show, and can it be merged?

Answer: `ready` is skipped (not failed) because its needed job failed and the implicit `success()` condition is false. In branch protection, a required check that is **skipped** is treated as passing, so the PR could be merged despite failing tests. This is the well-known trap. Fix: give `ready` `if: always()` and make it explicitly fail when any need failed or was cancelled (`contains(needs.*.result, 'failure')`), so the required check is red, not skipped.

---

## ⚫ Interview Questions + Answers

Q1: Does `needs` accept names or ids?
A1: Job ids (the YAML keys), as a string or list.

Q2: Which needs' outputs can I read?
A2: Only jobs directly listed in this job's `needs`.

Q3: What happens when a needed job is skipped?
A3: Dependent job is skipped by default too (cascade), unless a status function like `always()` is used.

Q4: What are possible values of `needs.<id>.result`?
A4: `success`, `failure`, `cancelled`, `skipped`.

Q5: How does `needs` interact with a matrix job?
A5: A job needing a matrix job waits for all of its combinations; `result` is failure if any combination failed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Defining stage order and fan-in/fan-out graphs.
- Reading outputs from earlier jobs.
- Building aggregator gates and cleanup/notify jobs.

❌ Avoid when:
- Jobs are independent (needless `needs` slows the pipeline).
- You need conditional ordering based on data only known at runtime (use outputs + `if:`).

---

## 📊 Visual Diagram
```
           +------+
           | meta |
           +--+---+
        +-----+------+
        v            v
  +-----------+ +-----------+
  | build-web | | build-api |
  +-----+-----+ +-----+-----+
        |             |  \
        +------+------+   \
               v           v
        +-------------+  +------+
        | integration |  | scan |
        +------+------+  +--+---+
               +-----+------+
                     v
               +-----------+       +---------------------------+
               |  deploy   | ----> | notify (if: always())     |
               +-----------+       +---------------------------+
 (deploy lists meta in needs too: outputs are NOT transitive)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| DAG | Graph without cycles | बिना चक्र वाला graph |
| Fan-out / Fan-in | Split / join branches | शाखाएँ बाँटना / जोड़ना |
| `needs.<id>.result` | Final status of a needed job | Needed job की अंतिम स्थिति |
| Transitive | Indirect dependency | अप्रत्यक्ष निर्भरता |
| Aggregator | Gate summarizing results | नतीजों का gate |
| Skipped | Not run because of conditions | शर्तों के कारण नहीं चला |

---

## ⚡ 3-Line Summary
English: `needs` defines the job graph; a job runs after all needed jobs succeed, else it is skipped.
English: Outputs and results are available only from directly listed jobs.
English: Use `always()` aggregators that fail explicitly, because a skipped required check passes branch protection.
Hindi: `needs` job graph तय करता है; job सारे needed jobs के सफल होने पर चलता है, वरना skip होता है।
Hindi: Outputs और results सिर्फ़ सीधे लिखे jobs से मिलते हैं।
Hindi: `always()` वाले aggregator इस्तेमाल करें जो साफ़ fail हों, क्योंकि skipped required check branch protection में पास माना जाता है।

---

## ➡️ Next Topic
**297. Conditional Jobs** — running jobs only when `if:` conditions are true.
