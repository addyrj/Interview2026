# 280. Environment Secrets
# हिंदी में: Environment Secrets (staging / production के अलग secrets)

---

## 🔵 Simple Definition (English)
A GitHub **environment** (for example `staging`, `production`) is a named deployment target in a repository. Secrets and variables stored on it are only released to jobs that declare `environment: <name>`, and only after the environment's protection rules pass (required reviewers, wait timer, allowed branches).

## 🔵 सरल परिभाषा (Hindi)
GitHub **environment** (जैसे `staging`, `production`) repository में एक नाम वाला deployment target है। इस पर रखे secrets और variables सिर्फ उन jobs को मिलते हैं जो `environment: <name>` declare करते हैं, और वह भी environment के protection rules (required reviewers, wait timer, allowed branches) पास होने के बाद।

---

## 🔴 Problem it Solves
Repository-level secrets are visible to every job on every branch. A feature-branch workflow could read your production SSH key. Staging and production also need different values under the same variable name. Environments solve both: separate values per target plus a human approval gate for production.

## 🔴 यह क्यों बना? (Hindi)
Repository-level secrets हर branch के हर job को दिखते हैं। एक feature-branch workflow आपकी production SSH key पढ़ सकता है। Staging और production को एक ही variable नाम पर अलग values भी चाहिए। Environments दोनों समस्याएँ हल करते हैं: हर target की अलग values और production के लिए इंसानी approval gate।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Repo Settings > Environments > New environment: "production"
Step 2 → Add protection rules: Required reviewers, Wait timer,
         Deployment branches (only main / protected branches)
Step 3 → Add environment secrets (VPS_HOST, VPS_SSH_KEY) and variables
Step 4 → Job declares:  environment: production
Step 5 → Run pauses at "Waiting for review"; reviewer approves
Step 6 → Only now secrets for that environment are injected into the job
```

Notes: environments are available on public repos for all plans; private repos need a paid plan for protection rules (check current GitHub plan docs). Environment secrets override repo and org secrets of the same name.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Repo Settings > Environments > New environment: "production"
Step 2 → Protection rules जोड़ो: Required reviewers, Wait timer,
         Deployment branches (सिर्फ main / protected branches)
Step 3 → Environment secrets (VPS_HOST, VPS_SSH_KEY) और variables जोड़ो
Step 4 → Job में लिखो:  environment: production
Step 5 → Run "Waiting for review" पर रुकता है; reviewer approve करता है
Step 6 → अब उस environment के secrets job में inject होते हैं
```

नोट: Public repos पर environments सभी plans में हैं; private repos में protection rules के लिए paid plan चाहिए (current GitHub docs देखें)। Environment secrets उसी नाम के repo/org secrets को override करते हैं।

---

## 🟡 Real World Example
A fintech team has two VPS servers. Pushes to `develop` auto-deploy to `staging` using staging keys. Pushes to `main` build the same image, then wait for the CTO to approve the `production` environment; only then are production DB credentials and SSH key released. A junior developer's feature branch cannot even request production, because deployment branches are limited to `main`.

## 🟡 Real Example Hindi mein
एक fintech team के पास दो VPS servers हैं। `develop` पर push होने पर staging keys से `staging` में auto-deploy होता है। `main` पर push वही image build करता है, फिर `production` environment के लिए CTO की approval का इंतज़ार करता है; तभी production DB credentials और SSH key मिलते हैं। Junior developer की feature branch production request भी नहीं कर सकती, क्योंकि deployment branches सिर्फ `main` तक सीमित हैं।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/env-basic.yml
name: env-secrets-basic                # workflow name
on:
  push:
    branches: [main]                   # triggers on main

jobs:
  deploy:
    runs-on: ubuntu-latest             # runner
    environment: production            # unlocks production secrets AFTER approvals
    steps:
      - name: Show which target
        run: echo "Deploying to $TARGET_NAME"      # TARGET_NAME comes from env var below
        env:
          TARGET_NAME: ${{ vars.TARGET_NAME }}     # environment variable (not secret)
      - name: Use environment secret
        env:
          HOST: ${{ secrets.VPS_HOST }}            # production's VPS_HOST (overrides repo-level)
        run: 'echo "would ssh to host ending ...${HOST: -4}"'   # never print the full value
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/promote.yml
name: promote                          # workflow name
on:
  push:
    branches: [develop, main]          # two long-lived branches

permissions:
  contents: read                       # least privilege

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.t.outputs.tag }}  # image tag for deploy jobs
    steps:
      - uses: actions/checkout@v4      # example version
      - id: t
        run: echo "tag=${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"   # short SHA
      - run: echo "build and push image my-api:${{ steps.t.outputs.tag }}"   # real build omitted

  deploy-staging:
    needs: build                       # after build
    if: github.ref == 'refs/heads/develop'      # only develop goes to staging
    runs-on: ubuntu-latest
    environment:
      name: staging                    # staging secrets / vars
      url: https://staging.example.com # link shown on the run page
    steps:
      - run: echo "deploy ${{ needs.build.outputs.tag }} to staging"

  deploy-production:
    needs: build
    if: github.ref == 'refs/heads/main'          # only main goes to production
    runs-on: ubuntu-latest
    environment:
      name: production                 # requires reviewers (configured in Settings)
      url: https://app.example.com
    concurrency: production-deploy     # one production deploy at a time
    steps:
      - name: Deploy
        env:
          SSH_KEY: ${{ secrets.VPS_SSH_KEY }}      # production-only key
          HOST: ${{ secrets.VPS_HOST }}            # production-only host
          TAG: ${{ needs.build.outputs.tag }}      # passed via env, injection-safe
        run: |
          install -m 700 -d ~/.ssh
          printf '%s\n' "$SSH_KEY" > ~/.ssh/id_ed25519 && chmod 600 ~/.ssh/id_ed25519
          ssh -o StrictHostKeyChecking=accept-new deploy@"$HOST" "IMAGE_TAG=$TAG docker compose up -d"
          # accept-new trusts a host the first time only; pin known_hosts for real production
```
Not run locally; YAML parsed only. Reviewer rules and branch rules are configured in the GitHub UI or API, not in YAML.

---

## 🟠 My Stack Integration
Map one environment per VPS: `staging` (small VPS, Nginx `staging.example.com`) and `production` (bigger VPS or AWS EC2 behind a load balancer). The same Docker image goes through both; only the environment secrets (DB URL, SSH key, host) differ. This is "build once, promote the same artifact".

```yaml
# snippet: same compose file, different env values per environment
      - name: Render .env from environment secrets
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}   # different per environment
          JWT_SECRET: ${{ secrets.JWT_SECRET }}       # different per environment
        run: |
          umask 077                                  # file mode 600
          printf 'DATABASE_URL=%s\nJWT_SECRET=%s\n' "$DATABASE_URL" "$JWT_SECRET" > .env
          scp .env deploy@"$HOST":/srv/app/.env      # copy to the target VPS
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Declaring `environment:` but expecting secrets in a job that has no `environment:`.
✅ Correct: Only jobs that name the environment get its secrets.

❌ Mistake 2: Leaving "Deployment branches" as "All branches".
✅ Correct: Limit production to `main` or protected branches/tags.

❌ Mistake 3: Required reviewers includes the person who triggers (can self-approve).
✅ Correct: Enable "Prevent self-review" and use a separate approver.

❌ Mistake 4: Same secret name with different meaning across levels, causing confusion.
✅ Correct: Document names; keep environment-specific ones only on the environment.

---

## 🧠 Tricky Interview Question
A job has `environment: production` but the approval is pending for 2 days. Do the earlier steps in the same job run in the meantime?

Answer: No. The whole job waits; the approval gate is evaluated before the job starts, so no step runs and no environment secrets are exposed until approval. Other jobs without that environment keep running. Pending runs time out after 30 days.

---

## ⚫ Interview Questions + Answers

Q1: What protection rules exist?
A1: Required reviewers (up to 6), wait timer, deployment branch/tag restrictions, and custom protection rules via GitHub Apps.

Q2: Which wins for the same name: repo or environment secret?
A2: Environment secret.

Q3: Can you reference environment secrets in `needs` jobs?
A3: Only in the job that declares the environment.

Q4: How do you create one with CLI?
A4: `gh secret set NAME --env production`.

Q5: Does `environment:` help the deployment history?
A5: Yes. GitHub records deployments per environment, with the URL, shown on the repo's Deployments page.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Different credentials for staging and production.
- You need manual approval before production.

❌ Avoid when:
- A single-environment hobby project with no approval need.
- You rely on rules unavailable on your plan (check plan limits).

---

## 📊 Visual Diagram
```
 push to main
     |
 build job (no secrets)
     |
 deploy-production job  --environment: production-->  [ protection rules ]
                                                        reviewers approve?
                                                        branch allowed?
                                                              |
                                              yes ------------+------------ no -> job never starts
                                               |
                          environment secrets released (VPS_SSH_KEY, DATABASE_URL)
                                               |
                                         ssh deploy to VPS
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Environment | Named deploy target with rules | नियमों वाला deploy target |
| Required reviewers | People who must approve | जिन्हें approve करना है |
| Deployment branches | Branches allowed to deploy | Deploy की अनुमति वाली branches |
| Wait timer | Delay before deploy starts | Deploy से पहले की देरी |
| Promote | Move same artifact to next env | वही artifact अगले env में भेजना |

---

## ⚡ 3-Line Summary
English: Environment secrets are released only to jobs naming that environment after protection rules pass.
Use them for per-target credentials and production approvals.
They override repository and organization secrets of the same name.

Hindi: Environment secrets सिर्फ उन jobs को मिलते हैं जो उस environment का नाम लें, protection rules पास होने के बाद।
Per-target credentials और production approvals के लिए use करो।
ये उसी नाम के repository और organization secrets को override करते हैं।

---

## ➡️ Next Topic
**281. secrets.GITHUB_TOKEN** — the automatic token GitHub creates for every run, and how to restrict its permissions.
