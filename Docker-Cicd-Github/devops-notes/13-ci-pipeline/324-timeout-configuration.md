# 324. Timeout Configuration
# हिंदी में: Timeout Configuration (job और step की समय-सीमा)

---

## 🔵 Simple Definition (English)
A **timeout** is a maximum run time you set so a stuck job or step is killed automatically. In GitHub Actions use `jobs.<id>.timeout-minutes` and `steps[*].timeout-minutes`. The default job limit is 360 minutes (6 hours), which is far too long for most CI.

## 🔵 सरल परिभाषा (Hindi)
**Timeout** एक अधिकतम run time है जिसके बाद अटका हुआ job या step अपने आप kill हो जाता है। GitHub Actions में `jobs.<id>.timeout-minutes` और `steps[*].timeout-minutes` इस्तेमाल होते हैं। Default job limit 360 मिनट (6 घंटे) है, जो ज़्यादातर CI के लिए बहुत ज़्यादा है।

---

## 🔴 Problem it Solves
Tests hang: a database connection never closes, an `npm install` waits on a network socket, a Jest worker deadlocks, an SSH deploy waits for a password prompt. Without a timeout the runner sits idle for up to 6 hours, burning paid minutes, blocking the concurrency queue and leaving the PR "pending" so nobody can merge.

## 🔴 यह क्यों बना? (Hindi)
Tests अटकते हैं: database connection बंद नहीं होता, `npm install` network socket पर रुका रहता है, Jest worker deadlock हो जाता है, SSH deploy password prompt का इंतज़ार करता है। Timeout न हो तो runner 6 घंटे तक बेकार बैठा रहता है, paid minutes जलते हैं, concurrency queue रुक जाती है और PR "pending" रहता है, कोई merge नहीं कर पाता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Measure your normal duration (look at last 10 green runs)
Step 2 → Set job timeout-minutes to about 2-3x the normal time
Step 3 → Set tighter step-level timeouts on risky steps (network, SSH, tests)
Step 4 → When time exceeds the limit, Actions cancels the job/step and marks it failed
Step 5 → Cleanup steps with `if: always()` still get a short window to run
Step 6 → Re-tune the numbers every few months as the test suite grows
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Normal duration नापो (पिछले 10 green runs देखो)
Step 2 → Job timeout-minutes को normal समय का लगभग 2-3 गुना रखो
Step 3 → Risky steps (network, SSH, tests) पर और कड़ा step-level timeout लगाओ
Step 4 → समय limit पार करे तो Actions job/step cancel करके failed mark कर देता है
Step 5 → `if: always()` वाले cleanup steps को थोड़ा समय फिर भी मिलता है
Step 6 → Test suite बढ़ने पर numbers हर कुछ महीने में फिर tune करो
```

---

## 🟡 Real World Example
A Razorpay-style payments API runs integration tests that call a mock bank service. One night the mock container failed to start; the test runner waited on a TCP connect forever. Eleven PRs queued behind it and the runner pool was exhausted until someone cancelled manually at 6 AM. After adding `timeout-minutes: 15` on the job and `timeout-minutes: 2` on the "wait for service" step, the same failure now turns red in 2 minutes with a clear message.

## 🟡 Real Example Hindi mein
Razorpay-जैसे payments API के integration tests एक mock bank service को call करते हैं। एक रात mock container start नहीं हुआ और test runner TCP connect पर हमेशा के लिए रुका रहा। 11 PRs queue में फँस गए और सुबह 6 बजे किसी के manually cancel करने तक runner pool खत्म रहा। Job पर `timeout-minutes: 15` और "wait for service" step पर `timeout-minutes: 2` लगाने के बाद वही failure 2 मिनट में साफ message के साथ red हो जाती है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/timeout-basic.yml
name: Timeout Basic                 # workflow name
on: [push]                          # run on every push
jobs:                               # jobs
  test:                             # single job
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 10             # kill the whole job after 10 minutes (default would be 360)
    steps:                          # steps
      - uses: actions/checkout@v4   # get code
      - uses: actions/setup-node@v4 # install node
        with:                       # inputs
          node-version: 20          # Node 20
          cache: npm                # cache npm downloads
      - run: npm ci                 # install dependencies
        timeout-minutes: 5          # install must finish in 5 min or fail
      - run: npm test               # run tests (limited by job timeout of 10 min)
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/timeout-advanced.yml
name: Timeout Advanced              # workflow name
on:                                 # triggers
  pull_request:                     # PRs
    branches: [main]                # to main
permissions:                        # least privilege
  contents: read                    # read only
jobs:                               # jobs
  api-tests:                        # FastAPI tests with Postgres
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 15             # job budget (normal run ~5 min)
    services:                       # sidecar services
      db:                           # hostname db
        image: postgres:16          # example tag
        env:                        # env
          POSTGRES_PASSWORD: test   # CI-only password
        ports: ['5432:5432']        # publish port
        options: >-                 # health check so tests do not start early
          --health-cmd "pg_isready -U postgres" --health-interval 5s --health-timeout 3s --health-retries 10
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
        timeout-minutes: 2          # slow network should not hang checkout
      - uses: actions/setup-python@v5  # python
        with:                       # inputs
          python-version: '3.12'    # version
          cache: pip                # pip cache
      - name: Install deps          # readable name
        run: pip install -r requirements.txt  # install packages
        timeout-minutes: 5          # PyPI hiccup guard
      - name: Wait for Postgres     # explicit readiness loop
        timeout-minutes: 2          # hard stop for the wait
        run: |                      # multi-line shell
          for i in $(seq 1 30); do                      # try up to 30 times
            pg_isready -h localhost -p 5432 && exit 0   # success -> leave
            sleep 2                                     # wait 2 seconds
          done                                          # loop end
          echo "Postgres never became ready" >&2        # message to stderr
          exit 1                                        # fail the step
      - name: Pytest                # tests
        run: pytest -x --timeout=60 # -x stop on first failure; per-test 60s (needs pytest-timeout plugin)
        timeout-minutes: 8          # whole test step cap
      - name: Dump logs on failure  # debugging aid
        if: failure()               # only when something above failed
        timeout-minutes: 1          # keep cleanup short
        run: docker ps -a           # show containers for debugging
  deploy-check:                     # post-deploy smoke test
    needs: api-tests                # after tests
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 5              # short job
    steps:                          # steps
      - name: Curl health with limits  # step name
        run: curl --fail --max-time 10 --retry 3 https://example.com/health  # curl's own timeout, example URL
```

---

## 🟠 My Stack Integration
For a VPS deploy over SSH, the biggest hang risk is the SSH step waiting on host-key prompts or a dead server. Give the deploy job a short timeout and also use SSH's own options so the connection fails by itself.

```yaml
# Excerpt: deploy job to a VPS with layered timeouts
jobs:                               # jobs
  deploy:                           # deploy job
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 10             # job-level cap
    steps:                          # steps
      - name: Deploy over SSH       # step name
        timeout-minutes: 6          # step cap
        env:                        # env from secrets
          SSH_KEY: ${{ secrets.VPS_SSH_KEY }}  # private key in repo secret
        run: |                      # shell
          install -m 600 /dev/null key && echo "$SSH_KEY" > key  # write key with 600 perms
          ssh -i key -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=3 \
            -o StrictHostKeyChecking=accept-new deploy@203.0.113.10 \
            'cd /srv/app && docker compose pull && docker compose up -d'  # 203.0.113.10 is a doc IP
```

Also run `docker compose up -d --wait` on the VPS so Compose itself waits for healthchecks. Security: never `echo` a secret without it being masked; the key file must be deleted or live only on the ephemeral runner.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Leaving the default 360-minute limit on every job.
✅ Correct: Set `timeout-minutes` on every job based on measured duration.

❌ Mistake 2: Setting the timeout equal to the normal duration, so a slightly slow day fails randomly.
✅ Correct: Use about 2-3x normal time; tight enough to catch hangs, loose enough to avoid flakes.

❌ Mistake 3: Only a job timeout, so a hung step wastes all 30 minutes before you learn which step hung.
✅ Correct: Add step-level timeouts on network/SSH/test steps for faster, clearer failure.

❌ Mistake 4: Putting a timeout on a long legitimate job (full e2e) too small and getting constant red.
✅ Correct: Split the job or give it its own higher limit.

---

## 🧠 Tricky Interview Question
**Q:** A job has `timeout-minutes: 10`, and a step inside has `timeout-minutes: 20`. What actually happens when the step runs 15 minutes?

Answer: The job is cancelled at 10 minutes. The job timeout is an upper bound for everything inside it; the larger step value cannot extend it. Steps that have `if: always()` may still run briefly for cleanup, but the job ends failed with a timeout message. Also note a step timeout cannot be larger than the remaining job time in effect.

---

## ⚫ Interview Questions + Answers

Q1: What is the default timeout for a GitHub Actions job?
A1: 360 minutes (6 hours) by default. GitHub-hosted runners cap a job at 6 hours; self-hosted runners allow longer jobs (documented limit is 5 days), so set explicit timeouts anyway.

Q2: Where do you set a timeout?
A2: `jobs.<job_id>.timeout-minutes` for jobs and `jobs.<job_id>.steps[*].timeout-minutes` for steps.

Q3: Why add timeouts if the tool has its own?
A3: Tool timeouts (pytest-timeout, curl `--max-time`) catch one operation; workflow timeouts are a safety net for anything you did not anticipate, including infrastructure stalls.

Q4: Is a timed-out job "failed" or "cancelled"?
A4: It is shown as failed (timed out). That makes the required status check red, which is what you want.

Q5: How would you pick the right number?
A5: Take the p95 duration of recent successful runs, multiply by 2-3, and review quarterly.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Always, on every job in every workflow.
- Steps touch network, SSH, databases or external APIs.

❌ Avoid when:
- (Rarely) very long legitimate jobs such as full model training; set a deliberate, large value instead of none.
- Do not use one tiny timeout to hide a slow suite; fix the suite.

---

## 📊 Visual Diagram
```
time ------------------------------------------------------------>
0        5          10 min (job timeout)
|--------|-----------|
[checkout][npm ci ][ npm test ........ hangs ......]
                                       ^
                                       | runner cancels at 10:00
                                       v
                      job = FAILED (timed out) -> PR red -> runner freed

Without timeout:  ....................................... 6 hours wasted
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `timeout-minutes` | Max run time for job/step | अधिकतम चलने का समय |
| Hang | Process waiting forever | अटक जाना |
| p95 duration | 95% of runs finish within this | 95% runs इसके भीतर खत्म |
| Runner minutes | Billed compute time | billed compute समय |
| Safety net | Backup guard | सुरक्षा जाल |

---

## ⚡ 3-Line Summary
English: Always set `timeout-minutes` on jobs and risky steps; the default is 6 hours.
English: Choose about 2-3x normal duration so hangs die fast but slow days still pass.
English: Combine with tool-level timeouts such as SSH `ConnectTimeout` and `curl --max-time`.

Hindi: हर job और risky step पर `timeout-minutes` लगाओ; default 6 घंटे है।
Hindi: Normal समय का 2-3 गुना रखो ताकि hang जल्दी मरे पर धीमे दिन में pass हो जाए।
Hindi: SSH `ConnectTimeout` और `curl --max-time` जैसे tool-level timeouts भी साथ लगाओ।

---

## ➡️ Next Topic
**325. Retry Failed Steps** — a timeout kills a hang, but some failures are transient network blips that a retry fixes.
