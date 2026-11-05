# 274. Environment Variables
# हिंदी में: Environment Variables (GitHub Actions में)

---

## 🔵 Simple Definition (English)
Environment variables (`env:`) are named string values available to your steps as normal shell variables (`$NAME`). You can set them at three levels: workflow, job, and step. The most specific level wins.

## 🔵 सरल परिभाषा (Hindi)
Environment variables (`env:`) नाम वाली string values हैं जो आपके steps में सामान्य shell variables (`$NAME`) की तरह मिलती हैं। इन्हें तीन levels पर set कर सकते हैं: workflow, job और step। सबसे specific level जीतता है।

---

## 🔴 Problem it Solves
Hard-coding `NODE_ENV=production`, ports, image names or URLs in many `run:` lines leads to typos and copy-paste drift. Config also differs by environment. `env:` keeps config in one place, makes it overridable, and (via the env context) lets you pass untrusted values safely to the shell.

## 🔴 यह क्यों बना? (Hindi)
`NODE_ENV=production`, ports, image names या URLs को कई `run:` lines में hard-code करने से typos और copy-paste की गड़बड़ होती है। Config हर environment में अलग भी होती है। `env:` config को एक जगह रखता है, override करने देता है, और untrusted values को shell तक safely पहुँचाने का तरीका भी देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Declare env: at workflow top (all jobs), job level, or step level
Step 2 → Runner builds the process environment for each step
Step 3 → Precedence: step env > job env > workflow env
Step 4 → run: scripts read $VAR (bash) or $env:VAR (pwsh)
Step 5 → ${{ env.VAR }} works in expressions, but ONLY for keys that are
         evaluated on the runner (e.g. step run/with/if), not for runs-on
Step 6 → Values are plain strings; each step gets a fresh copy
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → env: workflow के top पर (सभी jobs), job level पर, या step level पर लिखो
Step 2 → Runner हर step के लिए process environment बनाता है
Step 3 → Priority: step env > job env > workflow env
Step 4 → run: scripts $VAR (bash) या $env:VAR (pwsh) पढ़ते हैं
Step 5 → ${{ env.VAR }} expressions में चलता है, पर सिर्फ उन keys में जो runner पर
         evaluate होती हैं (step के run/with/if), runs-on में नहीं
Step 6 → Values plain strings होती हैं; हर step को नई copy मिलती है
```

---

## 🟡 Real World Example
Your Node.js API pipeline sets `NODE_ENV=test` and `CI=true` at workflow level, `DATABASE_URL` pointing to the Postgres service container at job level, and a one-off `LOG_LEVEL=debug` on a single flaky test step. When the DB host changes you edit one line.

## 🟡 Real Example Hindi mein
आपका Node.js API pipeline workflow level पर `NODE_ENV=test` और `CI=true` set करता है, job level पर Postgres service container की ओर इशारा करता `DATABASE_URL`, और एक flaky test step पर अकेला `LOG_LEVEL=debug`। DB host बदले तो सिर्फ एक line बदलनी पड़ती है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/env-basic.yml
name: env-basic                        # workflow name
on: push                               # trigger

env:                                   # WORKFLOW level: visible to every job
  NODE_ENV: test                       # plain string value
  APP_NAME: my-api                     # reused in multiple steps

jobs:
  build:
    runs-on: ubuntu-latest             # runner
    env:                               # JOB level: only this job
      PORT: "3000"                     # quote numbers; env values are strings anyway
      NODE_ENV: ci                     # overrides workflow-level NODE_ENV
    steps:
      - name: Read variables
        run: |
          echo "app=$APP_NAME env=$NODE_ENV port=$PORT"   # prints my-api, ci, 3000
      - name: Step-level override
        env:                           # STEP level: only this step
          NODE_ENV: production         # wins over job + workflow
        run: echo "env=$NODE_ENV"      # prints production
      - name: Back to job value
        run: echo "env=$NODE_ENV"      # prints ci again; step env did not leak
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/env-advanced.yml
name: env-advanced                     # workflow name
on:
  pull_request:                        # PRs may contain untrusted text
    branches: [main]

env:
  REGISTRY: ghcr.io                    # container registry host
  IMAGE_NAME: ${{ github.repository }} # expression allowed in env values

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:                        # service container
        image: postgres:16-alpine      # example tag, pin and update
        env:
          POSTGRES_PASSWORD: ci_only_password   # throwaway CI password, not a real secret
          POSTGRES_DB: app             # database created at start
        ports: ["5432:5432"]           # map to localhost on runner
        options: >-                    # wait until DB is ready
          --health-cmd "pg_isready -U postgres"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10
    env:
      DATABASE_URL: postgres://postgres:ci_only_password@localhost:5432/app  # job-wide
    steps:
      - uses: actions/checkout@v4      # example version
      - uses: actions/setup-node@v4    # example version
        with:
          node-version: 20             # Node version
      - run: npm ci                    # clean install
      - name: Test with debug logs
        env:
          LOG_LEVEL: debug             # only for this noisy step
        run: npm test                  # reads process.env.DATABASE_URL, LOG_LEVEL
      - name: Safe use of untrusted text
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}   # untrusted -> goes via env
        run: 'echo "Title is: $PR_TITLE"'                     # shell treats it as data
```
Not run locally; YAML parsed only. Service options syntax is the Docker create-options format.

---

## 🟠 My Stack Integration
Node.js reads `process.env.X`, FastAPI reads `os.environ["X"]` (or pydantic Settings), React bakes `REACT_APP_*` / `VITE_*` values at build time (so they are public). Nginx and the VPS get their config from a `.env` file on the server, never from the repo.

```yaml
# snippet: build-time vs runtime config
      - name: Build React (public values only)
        env:
          VITE_API_URL: https://api.example.com   # baked into JS bundle: PUBLIC
        run: npm run build             # output goes to dist/, served by Nginx
      - name: Build FastAPI image
        run: docker build -t ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} .
        # runtime secrets are NOT passed at build; provided by docker compose on the VPS
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting passwords in workflow-level `env:` as plain text.
✅ Correct: Use `secrets.X` (`env: DB_PASS: ${{ secrets.DB_PASS }}`) and scope it to the step that needs it.

❌ Mistake 2: Using `${{ env.X }}` in `runs-on` or job-level `if:` and getting an empty value.
✅ Correct: The `env` context is not available at those keys; use `vars` or `inputs`, or a job output.

❌ Mistake 3: Expecting `export FOO=1` in one step to exist in the next step.
✅ Correct: Append to `$GITHUB_ENV`: `echo "FOO=1" >> "$GITHUB_ENV"` (see topic 276).

❌ Mistake 4: Putting secret-like values in `VITE_*` / `REACT_APP_*`.
✅ Correct: Anything in the frontend bundle is public; keep secrets on the backend.

---

## 🧠 Tricky Interview Question
You set `NODE_ENV: production` at workflow level and `NODE_ENV: test` at step level, then the step runs `npm test` but the next step shows `production`. Is something wrong?

Answer: No, that is expected. Step-level env applies only to that step and has the highest precedence, but it does not persist. The next step falls back to job/workflow values. To persist a value across steps use `$GITHUB_ENV`.

---

## ⚫ Interview Questions + Answers

Q1: What are the 3 scopes and precedence?
A1: workflow, job, step. The narrowest scope overrides the wider.

Q2: `env` vs `vars` vs `secrets`?
A2: `env` is inline config written in YAML, `vars` are configuration variables stored in repo/org/environment settings (not secret), `secrets` are encrypted and masked in logs.

Q3: Are env values always strings?
A3: Yes. `PORT: 3000` becomes the string `"3000"`; booleans too (`"true"`).

Q4: Why pass untrusted data through env?
A4: With `run: echo ${{ github.event.issue.title }}` the text is pasted into the script (injection). Through env, the shell treats it as one variable value.

Q5: Does a child process inherit env?
A5: Yes, `npm test` and anything it spawns inherit the step environment.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Shared non-secret config (NODE_ENV, image names, ports).
- Passing untrusted event text safely.
- Scoping a value to one noisy step.

❌ Avoid when:
- Storing passwords or tokens in plain YAML.
- You need the value in `runs-on` or `uses` (use `vars`/inputs).

---

## 📊 Visual Diagram
```
 workflow env:  NODE_ENV=test   APP=my-api
      |
      v
 job env:       NODE_ENV=ci     PORT=3000     (overrides workflow)
      |
      v
 step env:      NODE_ENV=production           (overrides job, this step only)
      |
      v
 process environment ->  node server.js  reads process.env.NODE_ENV
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| env | Key/value config in YAML | YAML में key/value config |
| Scope | Workflow / job / step level | Level |
| Precedence | Narrowest scope wins | सबसे specific जीतता है |
| $GITHUB_ENV | File to persist vars to later steps | आगे के steps के लिए variable save करने की file |
| Injection | Untrusted text run as code | Untrusted text का code बनना |

---

## ⚡ 3-Line Summary
English: `env:` sets string variables at workflow, job or step scope; narrowest wins.
Do not store secrets in plain env; use `secrets` and scope them tightly.
Step env does not persist; use `$GITHUB_ENV` to share.

Hindi: `env:` workflow, job या step scope पर string variables set करता है; सबसे narrow जीतता है।
Secrets को plain env में मत रखो; `secrets` use करो और scope छोटा रखो।
Step env आगे नहीं जाता; share करने के लिए `$GITHUB_ENV` use करो।

---

## ➡️ Next Topic
**275. Default Environment Variables** — GitHub already injects many variables (`GITHUB_SHA`, `GITHUB_REF`, `RUNNER_OS` ...) without you declaring them.
