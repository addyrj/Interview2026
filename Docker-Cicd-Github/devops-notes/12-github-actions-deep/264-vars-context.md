# 264. vars Context
# हिंदी में: vars Context (Configuration Variables)

---

## 🔵 Simple Definition (English)
The `vars` context gives you configuration variables stored in GitHub settings at organization, repository or environment level, read as `${{ vars.NAME }}`. They are plain text (not encrypted, not masked), meant for non-sensitive config like region, host name or feature flags.

## 🔵 सरल परिभाषा (Hindi)
`vars` context आपको GitHub settings में organization, repository या environment level पर रखे configuration variables देता है, जिन्हें `${{ vars.NAME }}` से पढ़ते हैं। ये plain text हैं (encrypted या masked नहीं), और region, host name या feature flags जैसी non-sensitive config के लिए हैं।

---

## 🔴 Problem it Solves
Before `vars`, teams stored harmless values (AWS region, domain name) in secrets because there was nowhere else, or hard-coded them in YAML. Secrets are write-only and masked, so a wrong region is hard to debug, and YAML edits need a commit/PR for every config change. `vars` lets you change config in the UI, share it across repos, and see the value.

## 🔴 यह क्यों बना? (Hindi)
`vars` से पहले टीमें harmless values (AWS region, domain name) को secrets में रखती थीं क्योंकि और कोई जगह नहीं थी, या YAML में hard-code करती थीं। Secrets write-only और masked होते हैं, इसलिए गलत region debug करना मुश्किल, और YAML बदलने के लिए हर config बदलाव पर commit/PR। `vars` UI से config बदलने, repos में share करने और value देखने देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Admin creates a variable: Settings > Secrets and variables > Actions > Variables
Step 2 → Scope is one of: organization (with repo access policy), repository, environment
Step 3 → Run starts: GitHub resolves vars; narrower scope wins (environment > repo > org)
Step 4 → You read ${{ vars.NAME }} in jobs, steps, if:, with:, runs-on, environment
Step 5 → Value is injected as plain text (visible in logs and UI)
Step 6 → Changing the variable affects the NEXT run; no commit needed
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Admin variable बनाता है: Settings > Secrets and variables > Actions > Variables
Step 2 → Scope: organization (repo access policy के साथ), repository, या environment
Step 3 → Run शुरू: GitHub vars resolve करता है; narrow scope जीतता है (environment > repo > org)
Step 4 → आप jobs, steps, if:, with:, runs-on, environment में ${{ vars.NAME }} पढ़ते हैं
Step 5 → Value plain text में आती है (logs और UI में दिखती है)
Step 6 → Variable बदलने का असर अगले run पर; commit नहीं चाहिए
```

---

## 🟡 Real World Example
A company runs the same deploy workflow for staging and production. Each GitHub Environment defines `API_URL`, `VPS_HOST` and `REPLICAS` as variables; secrets hold only `SSH_KEY`. Ops changes `REPLICAS` from 2 to 4 before a sale (Flipkart-like traffic spike) in the UI, then re-runs the workflow; no code change, and the audit log records who changed it.

## 🟡 Real Example Hindi mein
एक कंपनी staging और production के लिए वही deploy workflow चलाती है। हर GitHub Environment में `API_URL`, `VPS_HOST` और `REPLICAS` variables हैं; secrets में सिर्फ `SSH_KEY`। Sale (Flipkart जैसे traffic spike) से पहले Ops UI में `REPLICAS` 2 से 4 करता है और workflow re-run करता है; कोई code change नहीं, और audit log में दर्ज होता है किसने बदला।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/vars-basic.yml
name: vars-basic                       # workflow name
on: workflow_dispatch                  # manual run for the demo
jobs:
  show:
    runs-on: ubuntu-24.04              # example runner
    steps:
      - name: Read configuration variables   # simple read
        run: |                         # shell block
          echo "region = ${{ vars.AWS_REGION }}"     # e.g. ap-south-1
          echo "host   = ${{ vars.VPS_HOST }}"       # e.g. app.example.com
      - name: Default when missing     # undefined vars are empty strings
        run: echo "log level = ${{ vars.LOG_LEVEL || 'info' }}"   # fallback to info
```
Create the variables first in repository Settings; undefined names evaluate to an empty string (no error).

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/vars-advanced.yml
name: deploy-by-environment            # same file, different config per environment
on:
  workflow_dispatch:
    inputs:
      target:
        type: environment              # dropdown of repo environments
        description: Where to deploy
jobs:
  deploy:
    runs-on: ${{ vars.RUNNER_LABEL || 'ubuntu-24.04' }}   # vars allowed in runs-on, with fallback
    environment: ${{ inputs.target }}  # selects environment-scoped vars + secrets
    if: ${{ vars.DEPLOY_ENABLED != 'false' }}   # kill switch variable (job-level if allows vars)
    env:
      API_URL: ${{ vars.API_URL }}     # environment > repo > org precedence
      REPLICAS: ${{ vars.REPLICAS || '2' }}   # default 2
    steps:
      - uses: actions/checkout@v4      # source
      - uses: aws-actions/configure-aws-credentials@v4   # example version
        with:
          role-to-assume: ${{ vars.AWS_ROLE_ARN }}   # ARN is not secret; vars is fine
          aws-region: ${{ vars.AWS_REGION }}         # region from variable
      - name: Deploy                   # use vars + secret together
        env:
          SSH_KEY: ${{ secrets.VPS_SSH_KEY }}        # only the key is secret
        run: |                         # shell
          echo "Deploying to $API_URL with $REPLICAS replicas"   # variables visible in log
          # ssh -i ... deploy@${{ vars.VPS_HOST }} "docker compose up -d --scale api=$REPLICAS"  # real command
```
YAML parsed locally; OIDC role/permissions (`id-token: write`) must be added for the AWS action to work; not run on GitHub.

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: `vars.APP_PORT`, `vars.LOG_LEVEL` for the container; secrets only for DB passwords.
- **React**: `vars.API_URL` becomes `VITE_API_URL` at build; it is public anyway.
- **Nginx/VPS**: `vars.VPS_HOST`, `vars.DEPLOY_PATH`, `vars.DOMAIN` used in ssh/rsync and certbot steps.
- **AWS**: `vars.AWS_REGION`, `vars.ECR_REPOSITORY`, `vars.AWS_ROLE_ARN`.
- **Security**: a variable's value is readable by anyone with repo read access (and in logs). Never put passwords or tokens in `vars`.

```yaml
      - name: Build React with public config   # public values come from vars
        env:
          VITE_API_URL: ${{ vars.API_URL }}    # non-secret, baked into JS bundle
        run: npm ci && npm run build           # build step
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting a database password in `vars`.
✅ Correct: Use `secrets`; `vars` are not masked.

❌ Mistake 2: Putting region and host names in secrets, then being unable to debug.
✅ Correct: Use `vars` for non-sensitive config.

❌ Mistake 3: Expecting a typo like `vars.AWS_REGON` to error.
✅ Correct: It silently evaluates to empty. Validate required vars in a first step (`test -n "$AWS_REGION"`).

❌ Mistake 4: Forgetting that environment variables only load when the job declares `environment:`.
✅ Correct: Add `environment: production` to the job.

❌ Mistake 5: Assuming fork PRs get repo variables.
✅ Correct: Treat variables as unavailable/unreliable from forks; do not depend on them there.

---

## 🧠 Tricky Interview Question
The same variable `API_URL` exists at org, repo and environment (`production`) level with three different values. The job has no `environment:` key. Which value is used?

Answer: The repository value. Environment-level variables are only loaded when the job references that environment. Precedence among those available is environment > repository > organization, so with no `environment:` the repo value overrides the org value. Adding `environment: production` switches it to the environment value.

---

## ⚫ Interview Questions + Answers

Q1: `vars` vs `secrets`?
A1: `vars` are plain, visible, for config; `secrets` are encrypted, masked, write-only, for credentials.

Q2: Can `vars` be used in `runs-on` and job `if`?
A2: Yes. That is a key advantage over `env`, which cannot be used there.

Q3: `vars` vs `env:` in YAML?
A3: `env:` is versioned with code and scoped by YAML; `vars` live in settings, are shareable across repos and editable without a commit.

Q4: Are there default variables?
A4: Yes, GitHub sets default env vars like `GITHUB_*`, `RUNNER_*`, `CI`. These are not in `vars`.

Q5: Is there a size limit?
A5: Variables are limited in size (about 48 KB each) and count per scope; check current docs. Not for large blobs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Config differs per environment (URLs, regions, replicas)
- Ops needs to toggle behaviour without code change
- Sharing non-secret values across many repositories

❌ Avoid when:
- Value is sensitive
- Value should be reviewed with code (put in YAML)
- Config is large or structured (use a config file in repo)

---

## 📊 Visual Diagram
```
 Organization vars  (API_URL=org)         lowest priority
        |
 Repository vars    (API_URL=repo)
        |
 Environment vars   (API_URL=prod)        highest (only if job has environment:)
        v
  ${{ vars.API_URL }}  -->  plain text in YAML, logs, UI
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| vars | Config variable context | Config variable context |
| Environment | Named deploy target with its own vars/secrets | अपने vars/secrets वाला deploy target |
| Org variable | Shared across repos | Repos में साझा variable |
| Masking | Hiding value in logs | Logs में value छुपाना |
| Kill switch | Flag to disable action | कुछ बंद करने वाला flag |

---

## ⚡ 3-Line Summary
English: `vars` holds non-secret configuration at org, repo or environment scope.
It is plain text and works in `runs-on` and job `if`, unlike `env`.
Undefined names are empty, so validate required ones; never store credentials.
Hindi: `vars` org, repo या environment scope पर non-secret configuration रखता है।
यह plain text है और `env` के विपरीत `runs-on` तथा job `if` में चलता है।
Undefined नाम खाली होते हैं, इसलिए ज़रूरी वाले validate करो; credentials कभी मत रखो।

---

## ➡️ Next Topic
**265. secrets Context** — encrypted credentials and how to use them safely.
