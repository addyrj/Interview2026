# 231. GitHub Actions — What + Why
# हिंदी में: GitHub Actions — क्या है और क्यों

---

## 🔵 Simple Definition (English)
**GitHub Actions** is GitHub's built-in automation and CI/CD platform. You describe a **workflow** in a YAML file inside `.github/workflows/`; GitHub runs it on a virtual machine (a **runner**) whenever an **event** happens (push, pull request, schedule, manual button). Typical jobs: run tests, build a Docker image, push it to a registry, and deploy to a VPS or AWS.

## 🔵 सरल परिभाषा (Hindi)
**GitHub Actions** GitHub का built-in automation और CI/CD platform है। आप `.github/workflows/` में YAML file से **workflow** बताते हो; जब कोई **event** होता है (push, pull request, schedule, manual button) तो GitHub उसे एक virtual machine (**runner**) पर चलाता है। आम काम: tests चलाना, Docker image बनाना, registry में push करना, और VPS या AWS पर deploy करना।

---

## 🔴 Problem it Solves
Without automation, a release is a manual checklist: SSH into the server, `git pull`, `npm install`, restart, hope. People forget steps, skip tests "just this once", deploy from a laptop with a different Node version, and nobody knows who deployed what. Running Jenkins yourself fixes that, but then you must install, patch, secure and scale a CI server. GitHub Actions removes that: the CI lives next to your code, needs no server of your own, and every run is logged against a commit.

## 🔴 यह क्यों बना? (Hindi)
Automation के बिना release एक manual checklist है: server पर SSH, `git pull`, `npm install`, restart, और उम्मीद। लोग steps भूलते हैं, "बस इस बार" tests छोड़ देते हैं, अलग Node version वाले laptop से deploy करते हैं, और किसी को पता नहीं कि किसने क्या deploy किया। Jenkins खुद चलाने से यह हल होता है, पर फिर CI server install, patch, secure और scale करना पड़ता है। GitHub Actions यह हटा देता है: CI आपके code के पास रहता है, अपना server नहीं चाहिए, और हर run एक commit से जुड़ा log होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write .github/workflows/ci.yml and commit it.
Step 2 → An EVENT happens (push to main, pull_request opened, cron schedule, workflow_dispatch).
Step 3 → GitHub reads the matching workflow and queues its JOBS.
Step 4 → Each job gets a fresh RUNNER (ubuntu-latest VM, or your self-hosted machine).
Step 5 → The runner executes STEPS in order: `uses:` (a ready-made action) or `run:` (a shell command).
Step 6 → Logs, status check (green/red), artifacts and secrets usage are shown on the commit/PR.
Step 7 → Branch protection can block merging until the checks pass.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → आप .github/workflows/ci.yml लिखकर commit करते हो।
Step 2 → कोई EVENT होता है (main पर push, pull_request खुला, cron schedule, workflow_dispatch)।
Step 3 → GitHub matching workflow पढ़कर उसके JOBS queue करता है।
Step 4 → हर job को नया RUNNER मिलता है (ubuntu-latest VM, या आपकी self-hosted मशीन)।
Step 5 → Runner STEPS क्रम से चलाता है: `uses:` (तैयार action) या `run:` (shell command)।
Step 6 → Logs, status check (हरा/लाल), artifacts और secrets का उपयोग commit/PR पर दिखता है।
Step 7 → Branch protection checks पास होने तक merge रोक सकता है।
```

Main building blocks / मुख्य हिस्से:

| Piece | What it is | Hindi |
|-------|-----------|-------|
| Workflow | One YAML automation file | एक automation YAML |
| Event (`on:`) | Trigger | शुरू करने वाली घटना |
| Job | Group of steps on one runner | एक runner पर steps का group |
| Step | One command or action | एक command या action |
| Action (`uses:`) | Reusable packaged step | दोबारा उपयोग होने वाला step |
| Runner | Machine that runs the job | Job चलाने वाली मशीन |
| Secrets | Encrypted values | Encrypted values |

---

## 🟡 Real World Example
A team of six builds a Node.js API and a React admin panel. Earlier, deploys were done by one senior developer on Fridays. Now: every pull request automatically runs lint + unit tests (3 minutes) and shows a green tick; merging to `main` builds the Docker image, pushes it to GHCR and SSHes to the VPS to run `docker compose up -d`. Any developer can deploy at any time, every deploy is traceable to a commit, and a failed test blocks the merge. Open-source projects use the same setup, with free minutes for public repos.

## 🟡 Real Example Hindi mein
छह लोगों की team Node.js API और React admin panel बनाती है। पहले deploy शुक्रवार को एक senior developer करता था। अब: हर pull request पर lint + unit tests अपने-आप चलते हैं (3 मिनट) और हरा tick दिखता है; `main` में merge होने पर Docker image बनकर GHCR में जाती है और VPS पर SSH करके `docker compose up -d` चलता है। कोई भी developer कभी भी deploy कर सकता है, हर deploy एक commit से trace होता है, और fail हुआ test merge रोक देता है। Open-source projects भी यही setup इस्तेमाल करते हैं, public repos के लिए free minutes के साथ।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/ci.yml - run tests on every push and pull request
name: CI                                   # name shown in the Actions tab
on:                                        # triggers
  push:
    branches: [main]                       # run when code is pushed to main
  pull_request:                            # run on every pull request
jobs:
  test:                                    # job id
    runs-on: ubuntu-latest                 # GitHub-hosted Linux runner
    steps:
      - uses: actions/checkout@v4          # download the repo code (example version, check latest)
      - uses: actions/setup-node@v4        # install Node.js (example version)
        with:
          node-version: 20                 # Node version to use
          cache: npm                       # cache ~/.npm to speed up installs
      - run: npm ci                        # clean install from package-lock.json
      - run: npm test                      # run the test suite; non-zero exit = red build
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/deploy.yml - test, build image, push to GHCR, deploy to VPS over SSH
name: CI-CD                                # workflow name
on:
  push:
    branches: [main]                       # deploy only from main
  workflow_dispatch: {}                    # allow manual run from the UI
concurrency:
  group: deploy-${{ github.ref }}          # one deploy per branch at a time
  cancel-in-progress: false                # do not cancel a running deploy
permissions:
  contents: read                           # least privilege for the token
  packages: write                          # allow pushing to GHCR
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:                            # service container for integration tests
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: test          # test-only password
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U postgres"
          --health-interval 5s
          --health-timeout 3s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm test
        env:
          DATABASE_URL: postgres://postgres:test@localhost:5432/postgres   # points at the service container
  build:
    needs: test                            # only if tests passed
    runs-on: ubuntu-latest
    outputs:
      tag: sha-${{ github.sha }}           # pass the tag to the deploy job
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3       # log in to GHCR with the built-in token
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6  # build and push the image
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}/api:sha-${{ github.sha }}
          cache-from: type=gha             # reuse layers cached in GitHub
          cache-to: type=gha,mode=max
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production                # can require manual approval + holds prod secrets
    steps:
      - name: Deploy over SSH
        env:
          SSH_KEY: ${{ secrets.VPS_SSH_KEY }}      # private key stored as a secret
          HOST: ${{ secrets.VPS_HOST }}            # server address
          TAG: ${{ needs.build.outputs.tag }}      # image tag to run
        run: |
          install -m 600 /dev/null key.pem                # create key file with safe permissions
          printf '%s\n' "$SSH_KEY" > key.pem              # write the key
          ssh -i key.pem -o StrictHostKeyChecking=accept-new deploy@"$HOST" \
            "cd /opt/app && TAG=$TAG docker compose pull && TAG=$TAG docker compose up -d"   # pull + restart
```

Checked: YAML parses and every job has `runs-on` and steps with `uses`/`run`. Not executed on GitHub. Action versions are examples; check each action's latest release. `StrictHostKeyChecking=accept-new` trusts the host on first connect; better to pin the host key in a secret. / YAML parse हुआ; GitHub पर नहीं चलाया।

---

## 🟠 My Stack Integration
- **Node.js**: `setup-node` + `npm ci` + test; build the image; **FastAPI**: `setup-python` + `pip install -r requirements.txt` + `pytest`, then image build.
- **React**: `npm run build`, then either copy `dist/` to the VPS Nginx or S3 + CloudFront invalidation, or bake into an Nginx image.
- **Nginx**: ship config as part of the image or sync it, and run `nginx -t` in CI via a container.
- **VPS**: SSH deploy (above) or a self-hosted runner on the VPS (no inbound SSH needed, but treat as trusted code only).
- **AWS**: use OIDC (`aws-actions/configure-aws-credentials`) for ECR/ECS, no long-lived keys.
- **Security**: store secrets in repo/environment secrets, limit `permissions`, pin third-party actions to a commit SHA, and never run untrusted PR code with secrets (`pull_request_target` pitfalls).
- **Cost**: public repos free; private repos have a monthly free minute quota (varies by plan), Linux minutes are cheapest (macOS and Windows cost a multiplier).

```yaml
# Minimal FastAPI CI for your stack
name: fastapi-ci
on: [push, pull_request]                   # short form of triggers
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5      # example version
        with: { python-version: "3.12", cache: pip }
      - run: pip install -r requirements.txt   # install dependencies
      - run: pytest -q                     # run tests
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Committing secrets (keys, passwords) in the workflow or repo.
✅ Correct: `secrets.*` and Environments; rotate anything that leaked.

❌ Mistake 2: Wrong folder or extension (`.github/workflow/ci.yaml`, `.github/workflows/ci.txt`).
✅ Correct: `.github/workflows/*.yml` or `.yaml`, folder name plural `workflows`.

❌ Mistake 3: Using `npm install` and no cache, making slow and non-reproducible builds.
✅ Correct: `npm ci` with `cache: npm`.

❌ Mistake 4: Using third-party actions at `@main` or unpinned tags.
✅ Correct: Pin to a version, preferably a full commit SHA, for supply-chain safety.

❌ Mistake 5: Giving the token write access to everything by default.
✅ Correct: Set `permissions:` explicitly (least privilege).

---

## 🧠 Tricky Interview Question
**Q:** A workflow works on `push` but the same job fails on a pull request from a fork with "secret is empty / permission denied". Why, and is it safe to switch to `pull_request_target` to fix it?

**Answer:** For security, GitHub does not pass repository secrets, and gives a read-only token, to workflows triggered by `pull_request` from forks, since a stranger could edit the workflow to print the secrets. `pull_request_target` runs in the context of the base repository with secrets, so it is dangerous if it checks out and runs the PR's code (a classic "pwn request"). Safe approach: keep untrusted code in `pull_request` without secrets, and use a separate trusted workflow (e.g. `workflow_run` or label-gated approval) for steps needing secrets, never executing fork code there.

---

## ⚫ Interview Questions + Answers

Q1: What are the main parts of GitHub Actions?
A1: Workflow (YAML file), event, job, step, action, runner, plus secrets, variables, artifacts and caches.

Q2: GitHub-hosted vs self-hosted runners?
A2: Hosted: fresh VM per job, no maintenance, limited minutes, can't reach your private network. Self-hosted: your machine, access to private resources and custom hardware, but you secure and maintain it (never use on public repos with untrusted PRs).

Q3: Do jobs share files?
A3: No. Each job runs on a separate fresh runner. Use `needs:` for order, artifacts/cache to pass files, and job `outputs` to pass small values.

Q4: How do you deploy without storing AWS keys?
A4: OIDC: GitHub issues a short-lived token that AWS exchanges for temporary role credentials through a trust policy limited to your repo/branch.

Q5: How do you stop two deploys from colliding?
A5: `concurrency` groups, plus environments with required reviewers.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Code is on GitHub and you want CI/CD with no server to manage
- You need PR checks, scheduled jobs and deployments in one place
- Big ecosystem of ready-made actions (Docker, AWS, Slack, Terraform)

❌ Avoid when:
- Code is not on GitHub (GitLab CI fits better)
- Very heavy, long builds that exhaust minutes (use self-hosted runners)
- Strict air-gapped environments (use self-hosted GitHub Enterprise or Jenkins)

---

## 📊 Visual Diagram
```
 Developer --git push--> GitHub repo
                           |  EVENT (push / PR / cron / manual)
                           v
              .github/workflows/deploy.yml
                           |
          +----------------+----------------+
          v                v                v
     job: test  --->  job: build  --->  job: deploy
     (runner 1)       (runner 2)        (runner 3, env: production)
      npm test      docker build/push     ssh -> docker compose up -d
          \                |                /
           +--> logs, status checks, artifacts, secrets <--+
                           v
                  PR gets green/red tick
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CI/CD | Automate build, test, deploy | Build, test, deploy का automation |
| Workflow | YAML automation file | Automation की YAML file |
| Runner | Machine executing jobs | Jobs चलाने वाली मशीन |
| Action | Reusable step | Reusable step |
| Event | Trigger | Trigger |
| Secret | Encrypted config value | Encrypted value |

---

## ⚡ 3-Line Summary
English: GitHub Actions runs YAML-defined workflows on GitHub-managed runners when events happen.
It automates tests, Docker builds and deploys with no CI server of your own.
Secure it with least-privilege tokens, secrets, pinned actions and OIDC.

Hindi: GitHub Actions events होने पर GitHub के runners पर YAML-defined workflows चलाता है।
यह बिना अपने CI server के tests, Docker builds और deploys को automate करता है।
Least-privilege tokens, secrets, pinned actions और OIDC से इसे सुरक्षित रखो।

---

## ➡️ Next Topic
**232. GitHub Actions vs Jenkins vs GitLab CI vs CircleCI** - how GitHub Actions compares with other CI/CD tools, and when to pick which.
