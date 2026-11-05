# 332. Deploy on Push to Main
# हिंदी में: Main पर Push होते ही Deploy

---

## 🔵 Simple Definition (English)
**Deploy on push to main** is a workflow with `on: push: branches: [main]` that, after a merge, builds the image and deploys it automatically. It is the simplest form of continuous deployment: merging a pull request is the release button.

## 🔵 सरल परिभाषा (Hindi)
**Deploy on push to main** एक workflow है जिसमें `on: push: branches: [main]` होता है और merge के बाद वह अपने आप image बनाकर deploy करता है। यह continuous deployment का सबसे सरल रूप है: pull request merge करना ही release का button है।

---

## 🔴 Problem it Solves
Without it a developer merges, then remembers (or forgets) to SSH into the VPS and deploy. Production lags behind main, hotfixes wait for a human, and "what is deployed?" has no answer. Auto-deploy ties production to the reviewed, tested state of `main`.

## 🔴 यह क्यों बना? (Hindi)
इसके बिना developer merge करता है, फिर VPS में SSH करके deploy करना याद रखता (या भूल जाता) है। Production main से पीछे रहता है, hotfix इंसान का इंतज़ार करते हैं, और "क्या deploy है?" का जवाब नहीं होता। Auto-deploy production को `main` की reviewed, tested स्थिति से बाँध देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Branch protection forces PR + green CI before anything lands on main
Step 2 → Merge creates a push event on main
Step 3 → Workflow triggers (optionally filtered by paths or ignoring docs-only changes)
Step 4 → Build image tagged with github.sha and push to registry
Step 5 → SSH to the VPS (or call AWS) and run the deploy script
Step 6 → Health check through Nginx; fail the job if unhealthy
Step 7 → Concurrency group serializes deploys so two merges never race
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Branch protection main पर कुछ भी आने से पहले PR + green CI ज़रूरी करती है
Step 2 → Merge से main पर push event बनता है
Step 3 → Workflow trigger होता है (optionally paths filter या docs-only changes ignore)
Step 4 → github.sha tag वाली image build करके registry में push
Step 5 → VPS पर SSH (या AWS call) करके deploy script चलाओ
Step 6 → Nginx के ज़रिए health check; unhealthy हो तो job fail
Step 7 → Concurrency group deploys को क्रम में रखता है ताकि दो merges race न करें
```

---

## 🟡 Real World Example
An internal HR portal (Node API + React) at a mid-size company is deployed to one EC2 instance. Earlier, Friday deploys waited for "the person who knows the steps". After enabling deploy-on-push, merging a reviewed PR updates production in 3 minutes. When two PRs merged within seconds, the concurrency group queued the second deploy so the server never ran half of each.

## 🟡 Real Example Hindi mein
किसी mid-size कंपनी का internal HR portal (Node API + React) एक EC2 instance पर deploy है। पहले शुक्रवार के deploys "वह व्यक्ति जिसे steps पता हैं" का इंतज़ार करते थे। Deploy-on-push चालू करने के बाद reviewed PR merge होते ही 3 मिनट में production अपडेट हो जाता है। जब दो PRs सेकंडों में merge हुए, तो concurrency group ने दूसरा deploy queue में रखा ताकि server कभी दोनों का आधा-आधा न चलाए।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/deploy.yml  (basic: deploy to VPS on push to main)
name: Deploy                        # workflow name
on:                                 # triggers
  push:                             # push events
    branches: [main]                # only main
jobs:                               # jobs
  deploy:                           # job id
    runs-on: ubuntu-latest          # runner
    steps:                          # steps
      - name: Deploy over SSH       # step name
        env:                        # secrets into env (never inline in the script)
          SSH_KEY: ${{ secrets.VPS_SSH_KEY }}  # private key stored in repo secrets
          HOST: ${{ secrets.VPS_HOST }}        # server IP or hostname
        run: |                      # shell commands
          install -m 600 /dev/null key && echo "$SSH_KEY" > key   # write key, owner-only perms
          ssh -i key -o StrictHostKeyChecking=accept-new deploy@"$HOST" \
            'cd /srv/app && git pull --ff-only && docker compose up -d --build'  # pull code and rebuild on server
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/deploy.yml  (production: build image, push, deploy, verify)
name: Deploy                        # workflow name
on:                                 # triggers
  push:                             # push events
    branches: [main]                # only main
    paths-ignore:                   # skip when only docs change
      - '**.md'                     # markdown files
      - 'docs/**'                   # docs folder
  workflow_dispatch:                # allow manual re-run from the UI
concurrency:                        # serialize deploys
  group: deploy-prod                # single lane
  cancel-in-progress: false         # queue instead of cancelling a running deploy
permissions:                        # least privilege
  contents: read                    # read repo
  packages: write                   # push to GHCR
env:                                # workflow-level env
  IMAGE: ghcr.io/${{ github.repository }}  # image name (repository must be lowercase)
jobs:                               # jobs
  build:                            # build+push
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 20             # cap
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - uses: docker/setup-buildx-action@v3  # buildx
      - uses: docker/login-action@v3  # login
        with:                       # inputs
          registry: ghcr.io         # registry
          username: ${{ github.actor }}  # user
          password: ${{ secrets.GITHUB_TOKEN }}  # token
      - uses: docker/build-push-action@v6  # build+push
        with:                       # inputs
          context: .                # context
          push: true                # push
          tags: |                   # two tags
            ${{ env.IMAGE }}:${{ github.sha }}
            ${{ env.IMAGE }}:latest
          cache-from: type=gha      # cache in
          cache-to: type=gha,mode=max  # cache out
  deploy:                           # remote deploy
    needs: build                    # after image exists
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 10             # cap
    environment:                    # link to GitHub environment
      name: production              # environment name
      url: https://app.example.com  # shown on the run page (example URL)
    steps:                          # steps
      - name: Prepare SSH           # key + known host
        env:                        # env
          SSH_KEY: ${{ secrets.VPS_SSH_KEY }}      # private key
          KNOWN_HOSTS: ${{ secrets.VPS_KNOWN_HOSTS }}  # output of ssh-keyscan, pinned
        run: |                      # shell
          mkdir -p ~/.ssh && chmod 700 ~/.ssh                  # ssh dir
          echo "$SSH_KEY" > ~/.ssh/id_deploy && chmod 600 ~/.ssh/id_deploy  # key file
          echo "$KNOWN_HOSTS" > ~/.ssh/known_hosts             # trust only the real server
      - name: Run remote deploy     # update containers
        env:                        # env
          HOST: ${{ secrets.VPS_HOST }}  # host
          TAG: ${{ github.sha }}    # image tag to deploy
        run: |                      # shell
          ssh -i ~/.ssh/id_deploy deploy@"$HOST" "IMAGE_TAG=$TAG bash /srv/app/deploy.sh"  # server-side script
      - name: Verify health         # post-deploy check
        run: |                      # shell
          for i in $(seq 1 12); do                                          # 12 tries x 5s
            curl -fsS https://app.example.com/health && exit 0              # example URL via Nginx
            sleep 5                                                         # wait
          done                                                              # end loop
          echo "health check failed" >&2                                    # message
          exit 1                                                            # fail job
```

---

## 🟠 My Stack Integration
On the VPS, `/srv/app/deploy.sh` pulls the new image, records the previous tag for rollback and restarts containers. Nginx keeps serving while containers restart (short blip for single-container setups). Store `VPS_SSH_KEY`, `VPS_HOST`, `VPS_KNOWN_HOSTS` as secrets.

```bash
#!/usr/bin/env bash
# /srv/app/deploy.sh  (runs on the VPS as user deploy)
set -euo pipefail                                    # stop on error / unset var
cd /srv/app                                          # app directory with docker-compose.yml
PREV=$(cat .current_tag 2>/dev/null || echo none)    # remember the last good tag
echo "$PREV" > .previous_tag                         # keep for rollback
export IMAGE_TAG="${IMAGE_TAG:?IMAGE_TAG required}"  # fail if tag missing
docker compose pull                                  # download new image
if docker compose up -d --wait; then                 # start and wait for healthchecks
  echo "$IMAGE_TAG" > .current_tag                   # mark success
else
  echo "deploy failed, rolling back to $PREV" >&2    # log
  [ "$PREV" != none ] && IMAGE_TAG="$PREV" docker compose up -d --wait  # restore old version
  exit 1                                             # report failure to Actions
fi
docker image prune -f                                # clean dangling images
```

Security: the `deploy` user should only manage Docker (no sudo), use a key dedicated to this repo, pin host keys, and require a protected `main` so only reviewed code deploys.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Allowing direct pushes to main, so unreviewed code auto-deploys.
✅ Correct: Branch protection with required reviews and checks.

❌ Mistake 2: Deploying without waiting for CI (deploy workflow runs in parallel with tests).
✅ Correct: Trigger from `workflow_run` of CI success, or include tests as a `needs` job.

❌ Mistake 3: `StrictHostKeyChecking=no`, open to man-in-the-middle attacks.
✅ Correct: Pin the server's host key in a secret.

❌ Mistake 4: `git pull` + build on the production server.
✅ Correct: Build once in CI, pull the image.

---

## 🧠 Tricky Interview Question
**Q:** Someone force-pushes a revert to main, and the deploy workflow runs. Two quick merges also happen. How do you stop old code from overwriting new code?

Answer: Use a `concurrency` group with `cancel-in-progress: false`, which queues runs in order, and deploy by immutable SHA tag so each run deploys exactly its own commit. For stricter safety, in the deploy job compare `github.sha` with the current `main` HEAD (`git ls-remote`) and skip if a newer commit exists. Also disable force-push on main via branch protection.

---

## ⚫ Interview Questions + Answers

Q1: Does merging a PR trigger `push` or `pull_request`?
A1: A `push` event on the target branch (main). `pull_request` ran on the PR before merging.

Q2: How do you avoid deploying on README changes?
A2: `paths-ignore` (or `paths`) under the `push` trigger.

Q3: How do you stop deploying code that failed tests?
A3: Make the deploy depend on CI: `needs` within one workflow, or `workflow_run` with `conclusion == 'success'`.

Q4: Why `cancel-in-progress: false` for deploys?
A4: Cancelling mid-deploy can leave a half-updated server. Queue runs instead.

Q5: How do you allow a manual redeploy?
A5: Add `workflow_dispatch` (optionally with an input for the SHA to deploy).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Small/medium team, good tests, reviewed PRs, easy rollback.
- Internal tools and staging environments.

❌ Avoid when:
- Regulated production that needs a human approval (use gates, topic 333).
- No monitoring or tests (auto-deploy amplifies mistakes).

---

## 📊 Visual Diagram
```
developer -> PR -> review + CI green -> MERGE
                                          |
                                   push event (main)
                                          v
                         [build image :SHA -> GHCR]
                                          |
                                  concurrency lane
                                          v
                     SSH -> VPS: docker compose pull/up --wait
                                          |
                              curl https://app/health
                               OK |         | FAIL
                                  v         v
                              success   rollback to previous tag
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Push event | Triggered when commits land on a branch | branch पर commits आने पर trigger |
| `paths-ignore` | Skip trigger for these files | इन files पर trigger न हो |
| Concurrency group | Serializes runs | runs को क्रम में चलाना |
| Host key pinning | Trust only known server key | सिर्फ जाने-पहचाने server की key पर भरोसा |
| `workflow_dispatch` | Manual trigger | हाथ से trigger |

---

## ⚡ 3-Line Summary
English: `on: push: branches: [main]` makes every merge a release.
English: Protect main, depend on green CI, queue deploys, and verify health.
English: Deploy immutable SHA tags and pin the server host key.

Hindi: `on: push: branches: [main]` हर merge को release बना देता है।
Hindi: main protect करो, green CI पर निर्भर रहो, deploys queue करो और health जाँचो।
Hindi: Immutable SHA tags deploy करो और server की host key pin करो।

---

## ➡️ Next Topic
**333. Manual Approval Gates** — when a human must say "yes" before production.
