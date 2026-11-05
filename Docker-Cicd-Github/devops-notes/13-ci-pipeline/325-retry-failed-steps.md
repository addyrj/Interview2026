# 325. Retry Failed Steps
# हिंदी में: Failed Steps को Retry करना

---

## 🔵 Simple Definition (English)
**Retrying** means re-running a step (or a whole job) automatically when it fails for a transient reason such as a network blip or a rate limit. GitHub Actions has no built-in `retry:` key for steps, so you use a retry action (for example `nick-fields/retry`), a shell loop, or a tool's own retry flags; whole workflows can be re-run from the UI or with `gh run rerun --failed`.

## 🔵 सरल परिभाषा (Hindi)
**Retry** का मतलब है किसी step (या पूरे job) को अपने आप दोबारा चलाना जब वह किसी अस्थायी कारण से fail हो, जैसे network blip या rate limit। GitHub Actions में step के लिए built-in `retry:` key नहीं है, इसलिए retry action (जैसे `nick-fields/retry`), shell loop, या tool के अपने retry flags इस्तेमाल होते हैं; पूरा workflow UI से या `gh run rerun --failed` से दोबारा चल सकता है।

---

## 🔴 Problem it Solves
`npm ci` fails with ECONNRESET, `docker pull` gets a 503 from the registry, a health check races the container start. The code is fine; the pipeline is red. Developers re-run manually, lose trust in CI and start ignoring red builds. Retrying only the flaky external call fixes noise without hiding real bugs.

## 🔴 यह क्यों बना? (Hindi)
`npm ci` ECONNRESET से fail होता है, `docker pull` को registry से 503 मिलता है, health check container start से race कर जाता है। Code ठीक है, पर pipeline red है। Developers manually re-run करते हैं, CI पर भरोसा खो देते हैं और red builds को ignore करने लगते हैं। सिर्फ flaky external call को retry करने से noise ठीक होता है और असली bugs नहीं छुपते।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Identify which failures are transient (network, registry, startup race), not logic
Step 2 → Wrap ONLY that command in a retry (action, shell loop, or tool flag)
Step 3 → Use limited attempts (2-3) with a wait between them (backoff)
Step 4 → Log every attempt so flakiness is visible, not hidden
Step 5 → Keep tests themselves un-retried; fix flaky tests instead
Step 6 → For a whole bad run use `gh run rerun <id> --failed` (reruns only failed jobs)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → पहचानो कि कौन से failures अस्थायी हैं (network, registry, startup race), logic वाले नहीं
Step 2 → सिर्फ उसी command को retry में लपेटो (action, shell loop, या tool flag)
Step 3 → Attempts सीमित रखो (2-3) और बीच में wait (backoff) रखो
Step 4 → हर attempt log करो ताकि flakiness दिखे, छुपे नहीं
Step 5 → Tests को खुद retry मत करो; flaky tests को ठीक करो
Step 6 → पूरे खराब run के लिए `gh run rerun <id> --failed` (सिर्फ failed jobs दोबारा चलाता है)
```

---

## 🟡 Real World Example
A Flipkart-style storefront builds a React app. During a sale-week deploy, the npm registry returned intermittent 502s and 1 in 8 CI runs failed at `npm ci`. Engineers re-ran by hand, delaying hotfixes. Wrapping `npm ci` in a 3-attempt retry with a 20-second wait cut false reds to almost zero, while the unit tests stayed strictly un-retried so real regressions still failed immediately.

## 🟡 Real Example Hindi mein
Flipkart-जैसा storefront React app build करता है। Sale-week deploy के दौरान npm registry बीच-बीच में 502 देती थी और हर 8 में से 1 CI run `npm ci` पर fail होता था। Engineers हाथ से re-run करते थे और hotfix देर से जाते थे। `npm ci` को 20 सेकंड wait वाले 3-attempt retry में लपेटने से false reds लगभग खत्म हो गए, जबकि unit tests retry नहीं हुए इसलिए असली regression तुरंत fail होता रहा।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/retry-basic.yml
name: Retry Basic                   # workflow name
on: [push]                          # run on push
jobs:                               # jobs
  build:                            # job id
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 15             # always cap total time
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout code
      - uses: actions/setup-node@v4 # install node
        with:                       # inputs
          node-version: 20          # Node 20
      - name: Install with shell retry  # step name
        run: |                      # shell script
          for attempt in 1 2 3; do                  # up to 3 attempts
            echo "Attempt $attempt"                 # log which attempt
            npm ci && exit 0                        # success -> leave step with 0
            echo "npm ci failed, sleeping 20s"      # log failure
            sleep 20                                # simple wait before retry
          done                                      # end loop
          exit 1                                    # all attempts failed -> fail the step
      - run: npm test               # tests are NOT retried
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/retry-advanced.yml
name: Retry Advanced                # workflow name
on:                                 # triggers
  push:                             # push events
    branches: [main]                # main only
permissions:                        # least privilege
  contents: read                    # read repo
jobs:                               # jobs
  build:                            # job
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 20             # job cap
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - uses: actions/setup-node@v4 # node
        with:                       # inputs
          node-version: 20          # version
          cache: npm                # cache lowers network calls = fewer flakes
      - name: npm ci with retry action  # third-party action, pin by SHA in production
        uses: nick-fields/retry@v3  # example version; check the current release before use
        with:                       # inputs of the retry action
          timeout_minutes: 5        # each attempt max 5 minutes
          max_attempts: 3           # try at most 3 times
          retry_wait_seconds: 20    # wait between attempts
          command: npm ci           # command to run
      - name: Build                 # compile app
        run: npm run build          # not retried: a build error is a real error
      - name: Docker pull with tool-level retry  # tool flags beat wrappers when available
        run: |                      # shell
          docker pull node:20-alpine || (sleep 15 && docker pull node:20-alpine)  # one manual second try
      - name: Download with curl retry  # curl has built-in retry
        run: curl --fail --silent --show-error --retry 5 --retry-delay 3 --retry-connrefused -o out.json https://example.com/data.json  # example URL
      - name: Pip install with retries  # pip has --retries
        run: pip install --retries 5 --timeout 30 -r requirements.txt  # 5 retries, 30s socket timeout
  rerun-on-failure:                 # optional: auto rerun failed jobs once
    needs: build                    # wait for build
    if: failure() && github.run_attempt == 1   # only if build failed and this is the first attempt
    runs-on: ubuntu-latest          # runner
    permissions:                    # this job needs to rerun workflows
      actions: write                # permission to call rerun API
    steps:                          # steps
      - name: Rerun failed jobs once  # step
        env:                        # env
          GH_TOKEN: ${{ github.token }}  # token for gh CLI
        run: gh run rerun ${{ github.run_id }} --failed --repo ${{ github.repository }}  # rerun only failed jobs
```

---

## 🟠 My Stack Integration
Retry the network-bound parts of your Node/FastAPI/React + VPS flow: dependency installs, image pulls, and the post-deploy health check behind Nginx. Never retry unit tests or the `docker compose up` itself blindly.

```yaml
# Excerpt: post-deploy health check with polling (retry) against the Nginx front door
      - name: Wait for app to become healthy  # step
        timeout-minutes: 3              # cap
        run: |                          # shell
          for i in $(seq 1 18); do                                   # 18 tries x 10s = 3 min
            code=$(curl -s -o /dev/null -w '%{http_code}' https://app.example.com/api/health)  # example host
            [ "$code" = "200" ] && echo "healthy" && exit 0         # success
            echo "status=$code, retry $i"                           # log
            sleep 10                                                # wait
          done                                                      # end loop
          echo "unhealthy after deploy" >&2                         # error
          exit 1                                                    # fail -> trigger rollback job
```

Security: pin third-party retry actions to a full commit SHA (a moved tag could run malicious code with your secrets). Do not retry steps that are non-idempotent such as "charge customer" or "send emails".

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Retrying the whole test suite 3 times so flaky tests go green.
✅ Correct: Fix or quarantine flaky tests; retry only external I/O.

❌ Mistake 2: Retrying with no delay, hammering a rate-limited registry.
✅ Correct: Add a wait or exponential backoff between attempts.

❌ Mistake 3: Retrying non-idempotent actions (database migrations, payments, publishing a package).
✅ Correct: Make the operation idempotent first or do not retry it.

❌ Mistake 4: Hiding retries so nobody notices the flakiness trend.
✅ Correct: Log each attempt and track how often retries fire.

---

## 🧠 Tricky Interview Question
**Q:** Your deploy step runs `docker compose up -d` and then a migration `npm run migrate`. The step failed after the migration partly ran. Should you wrap both in a retry loop?

Answer: No. Migrations are usually not safely repeatable; a retry could apply a half-done change twice or hit a "table exists" error that masks the real problem. Retry only the idempotent, network-sensitive parts (pull image, health check). Make migrations idempotent through a migration tool that tracks applied versions (Alembic, Prisma Migrate), run them as their own step, and fail loudly so a human decides.

---

## ⚫ Interview Questions + Answers

Q1: Does GitHub Actions have a native step retry?
A1: Not as a built-in step key. You use a marketplace action, a shell loop, or tool flags. You can re-run failed jobs natively from the UI, API or `gh run rerun --failed`.

Q2: What is the difference between "Re-run all jobs" and "Re-run failed jobs"?
A2: Re-run failed jobs only re-executes jobs that failed (and those depending on them), reusing earlier successful results; re-run all repeats everything. Both increment `run_attempt`.

Q3: Why retry with backoff instead of immediately?
A3: Immediate retries often hit the same outage or worsen rate limiting. A delay (ideally exponential with jitter) gives the remote system time to recover.

Q4: What should never be retried automatically?
A4: Non-idempotent operations: payments, emails, database migrations, package publishing, and any action with irreversible side effects.

Q5: How do you see how often retries happen?
A5: Echo attempt numbers in logs, or emit a summary line into `$GITHUB_STEP_SUMMARY`, then review trends.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Failure is a known transient (network, registry, startup race).
- The command is idempotent.
- You cap attempts and add a delay.

❌ Avoid when:
- It would mask real test failures.
- The operation has side effects.
- The failure is deterministic (a retry just wastes minutes).

---

## 📊 Visual Diagram
```
step: npm ci
  |
  v
attempt 1 --fail (ECONNRESET)--> wait 20s
  |
  v
attempt 2 --fail (502)---------> wait 20s
  |
  v
attempt 3 --success--> continue pipeline
  |
  +--fail--> step FAILED (max_attempts reached) -> job red

[tests]  -> never wrapped in retry: first failure = red immediately
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Transient failure | Temporary, self-healing error | अस्थायी error |
| Idempotent | Safe to repeat, same result | दोहराने पर भी वही नतीजा |
| Backoff | Growing wait between retries | retries के बीच बढ़ता इंतज़ार |
| Flaky test | Passes/fails randomly | कभी pass कभी fail test |
| `run_attempt` | Counter of workflow re-runs | workflow दोबारा चलने की गिनती |

---

## ⚡ 3-Line Summary
English: Actions has no native step retry; use a retry action, shell loop or tool flags.
English: Retry only transient, idempotent network steps with limited attempts and backoff.
English: Never retry tests, migrations or payments; fix flakiness at the source.

Hindi: Actions में native step retry नहीं है; retry action, shell loop या tool flags इस्तेमाल करो।
Hindi: सिर्फ अस्थायी, idempotent network steps को सीमित attempts और backoff के साथ retry करो।
Hindi: Tests, migrations या payments को retry मत करो; flakiness को जड़ से ठीक करो।

---

## ➡️ Next Topic
**326. CI Pipeline for Node.js** — now we assemble lint, test, build and caching into a full Node.js pipeline.
