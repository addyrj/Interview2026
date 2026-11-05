---

# 37. GitHub Variables
# हिंदी में: GitHub Variables (साधारण configuration मान)

---

## 🔵 Simple Definition (English)
**GitHub Variables** store non-sensitive configuration (URLs, regions, feature flags, image names) at repository, environment or organization level. Workflows read them with the `vars` context: `${{ vars.NAME }}`. Unlike secrets, they are plain text, visible in the UI and not masked in logs.

## 🔵 सरल परिभाषा (Hindi)
**GitHub Variables** गैर-संवेदनशील configuration (URLs, regions, feature flags, image names) को repository, environment या organization स्तर पर रखते हैं। Workflows इन्हें `vars` context से पढ़ते हैं: `${{ vars.NAME }}`। Secrets के उलट ये plain text हैं, UI में दिखते हैं और logs में masked नहीं होते।

---

## 🔴 Problem it Solves
Developers used to hardcode `https://staging.example.com` or `ap-south-1` in many workflow files, or abuse secrets for harmless values (making debugging hard because secrets are masked and unreadable). Changing one URL meant editing five YAML files and a PR. Variables centralize config so you can change it in one place without a code change.

## 🔴 यह क्यों बना? (Hindi)
Developers `https://staging.example.com` या `ap-south-1` कई workflow files में hardcode करते थे, या बेकार में secrets इस्तेमाल करते थे (जिससे debug मुश्किल, क्योंकि secrets masked और unreadable हैं)। एक URL बदलने के लिए पाँच YAML files और PR बदलना पड़ता था। Variables config को एक जगह रखते हैं, बिना code बदले।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Settings -> Secrets and variables -> Actions -> Variables tab -> New repository variable
          (or: gh variable set NAME --body value)
Step 2 → Choose scope: Repository, Environment (per stage), or Organization (shared by chosen repos)
Step 3 → Workflow reads:  ${{ vars.NAME }}   (in `env:`, `with:`, `if:`, `run:`)
Step 4 → Precedence: Environment > Repository > Organization (same name -> most specific wins)
Step 5 → Value is plain text; visible to anyone with repo read access; shown in logs
Step 6 → Change the value -> next run uses it. No commit needed. (Re-run old jobs use the NEW value too!)
Step 7 → Default variables also exist: github.*, runner.*, env.* (different from vars.*)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Settings -> Secrets and variables -> Actions -> Variables tab -> New repository variable
          (या: gh variable set NAME --body value)
Step 2 → Scope चुनो: Repository, Environment (हर stage), या Organization
Step 3 → Workflow में पढ़ो:  ${{ vars.NAME }}  (`env:`, `with:`, `if:`, `run:` में)
Step 4 → प्राथमिकता: Environment > Repository > Organization (एक ही नाम पर सबसे specific जीतता है)
Step 5 → Value plain text है; repo पढ़ सकने वाले सबको दिखती है; logs में भी दिखती है
Step 6 → Value बदलो -> अगला run नई value लेगा। commit नहीं चाहिए। (पुराने job re-run भी NEW value लेते हैं!)
Step 7 → Default variables भी हैं: github.*, runner.*, env.* (vars.* से अलग)
```

---

## 🟡 Real World Example
A team has `staging` and `production` environments. Each defines `API_BASE_URL`, `AWS_REGION`, `IMAGE_NAME`, and `ENABLE_NEW_CHECKOUT` as **variables**; only `SSH_KEY` and `DB_URL` are secrets. The same workflow file deploys to both: `${{ vars.API_BASE_URL }}` resolves per environment. When the company moves from `ap-south-1` to `ap-south-2`, the DevOps engineer edits one org variable instead of opening 12 PRs. The React build reads `VITE_API_URL` from this variable at build time.

## 🟡 Real Example Hindi mein
एक team में `staging` और `production` environments हैं। हर एक में `API_BASE_URL`, `AWS_REGION`, `IMAGE_NAME`, `ENABLE_NEW_CHECKOUT` **variables** हैं; सिर्फ `SSH_KEY` और `DB_URL` secrets हैं। एक ही workflow file दोनों में deploy करती है: `${{ vars.API_BASE_URL }}` हर environment के हिसाब से बदलता है। कंपनी जब `ap-south-1` से `ap-south-2` जाती है तो DevOps engineer 12 PRs की जगह एक org variable बदलता है। React build `VITE_API_URL` इसी variable से लेता है।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/vars-basic.yml
# Prereq: create variables APP_URL and AWS_REGION in Settings -> Secrets and variables -> Actions -> Variables
name: Variables basic                       # workflow name
on:
  workflow_dispatch:                        # manual trigger
jobs:
  show:                                     # job id
    runs-on: ubuntu-latest                  # hosted runner
    env:
      APP_URL: ${{ vars.APP_URL }}          # copy repo variable into an env var for all steps
    steps:
      - name: Print config                  # step label
        run: |                              # shell
          echo "App URL: $APP_URL"          # plain text, visible in logs (so never store secrets here)
          echo "Region: ${{ vars.AWS_REGION }}"   # read a variable inline
      - name: Conditional on a flag         # step label
        if: ${{ vars.ENABLE_BETA == 'true' }}   # variables are always strings, compare as text
        run: echo "Beta feature enabled"    # runs only when flag equals the string 'true'
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/build-deploy.yml - one workflow, per-environment config from variables
name: Build and deploy                      # workflow name
on:
  push:
    branches: [main]                        # run after merge to main
permissions:
  contents: read                            # minimal permissions
env:
  IMAGE_NAME: ${{ vars.IMAGE_NAME || 'myorg/api' }}   # variable with a fallback default if not defined
jobs:
  build:                                    # job 1: build the React app with env-specific API url
    runs-on: ubuntu-latest                  # hosted runner
    environment: staging                    # use staging variables for the build
    steps:
      - uses: actions/checkout@v4           # code (example version)
      - uses: actions/setup-node@v4         # Node
        with:
          node-version: ${{ vars.NODE_VERSION || '20' }}   # Node version managed centrally
          cache: npm                        # npm cache
      - run: npm ci                         # install
      - name: Build frontend                # step label
        env:
          VITE_API_URL: ${{ vars.API_BASE_URL }}   # baked into the bundle at build time (public by design!)
        run: npm run build                  # produce dist/
  deploy:                                   # job 2: deploy per environment via matrix
    needs: build                            # after build
    runs-on: ubuntu-latest                  # hosted runner
    strategy:
      matrix:
        target: [staging, production]       # run for both environments
      max-parallel: 1                       # deploy one after another (staging first)
    environment: ${{ matrix.target }}       # each matrix leg uses its own environment variables and secrets
    steps:
      - name: Show resolved config          # step label
        run: |                              # shell
          echo "Deploying ${{ vars.IMAGE_NAME }} to ${{ vars.API_BASE_URL }} in ${{ vars.AWS_REGION }}"
      - name: Write health check target     # step label
        run: echo "HEALTH_URL=${{ vars.API_BASE_URL }}/health" >> "$GITHUB_ENV"   # export for later steps
      - name: Smoke test                    # step label
        run: curl --fail --silent --show-error "$HEALTH_URL" || echo "health check not reachable in this demo"
```
Note: with `matrix` and `environment`, production would still need approval if configured. Not executed on GitHub; YAML syntax parsed locally only. `max-parallel: 1` does not guarantee order across matrix items; use separate jobs when strict ordering is needed.

---

## 🟠 My Stack Integration
For React (Vite) the API URL is public after build, so a variable is correct (never put secrets in `VITE_*`). For FastAPI/Node, keep non-secret settings (`LOG_LEVEL`, `CORS_ORIGINS`, `AWS_REGION`) as variables and secrets (`DATABASE_URL`, `JWT_SECRET`) in secrets, and write the server `.env` at deploy time:

```yaml
# snippet: generate server env file from variables + secrets (steps inside a deploy job)
- name: Create .env on the VPS              # step label
  env:
    LOG_LEVEL: ${{ vars.LOG_LEVEL }}        # non-secret from variable
    CORS_ORIGINS: ${{ vars.CORS_ORIGINS }}  # non-secret from variable
    DATABASE_URL: ${{ secrets.DATABASE_URL }}   # secret
  run: |                                    # shell executed on the runner
    printf 'LOG_LEVEL=%s\nCORS_ORIGINS=%s\nDATABASE_URL=%s\n' "$LOG_LEVEL" "$CORS_ORIGINS" "$DATABASE_URL" > app.env
    chmod 600 app.env                       # restrict file permissions before copying with scp
```
Security: variables are readable by anyone with repo read access and are echoed in logs; use them only for non-sensitive data. Anyone who can edit the workflow can print them, so never rely on variables to hide information. Org-level variables should be limited to selected repositories.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting passwords or tokens in variables.
✅ Correct: Use secrets for anything sensitive; variables only for public config.

❌ Mistake 2: Using `secrets.` for harmless values like region, making debugging impossible.
✅ Correct: Use `vars.` so values are visible and easy to audit.

❌ Mistake 3: Comparing a boolean variable as `if: vars.FLAG` or `== true`.
✅ Correct: Variables are strings: `if: ${{ vars.FLAG == 'true' }}`.

❌ Mistake 4: Confusing `vars.X`, `env.X` and `${{ github.X }}`.
✅ Correct: `vars` = stored in GitHub settings; `env` = set in the workflow; `github` = event/run metadata.

---

## 🧠 Tricky Interview Question
You change the variable `API_BASE_URL` after yesterday's deployment and click "Re-run all jobs" on yesterday's run. Which URL is used, and why does it matter for audits?

Answer: The NEW value. Re-runs reuse the same commit and workflow file but evaluate `vars.*` at run time, so the rerun is not an exact replica of yesterday. For reproducible deployments, bake configuration into the artifact (image/tag) or keep versioned config in the repo and log the effective values (non-secret) in the job summary.

---

## ⚫ Interview Questions + Answers

Q1: Difference between variables and secrets?
A1: Variables are plain text, readable and logged; secrets are encrypted, write-only and masked. Use variables for non-sensitive config.

Q2: What scopes exist and what is the precedence?
A2: Organization, repository and environment. Environment overrides repository, which overrides organization for the same name.

Q3: How do you set one from the CLI?
A3: `gh variable set NAME --body "value"` (add `--env production` or `--org myorg`); list with `gh variable list`.

Q4: Can a job output a variable to later jobs?
A4: Use job `outputs` or `$GITHUB_OUTPUT`/`$GITHUB_ENV`; `vars.*` is available in every job already.

Q5: Are variables available in reusable workflows?
A5: The caller's `vars` are not automatically available in a called workflow in all contexts; pass values via `inputs` to be explicit (check docs for current behavior).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Environment-specific non-sensitive config (URLs, regions, versions, flags)
- One shared value used by many workflows/repos

❌ Avoid when:
- Value is a credential or personal data
- Value must be pinned for reproducibility (put it in the repo or the artifact)

---

## 📊 Visual Diagram
```
 Organization var  REGION=ap-south-1
        |  overridden by
 Repository var    REGION=ap-south-2
        |  overridden by
 Environment var   REGION=eu-west-1   (environment: production)
        v
 ${{ vars.REGION }} in the job  ->  eu-west-1
 (plain text, visible in logs; secrets would be ***)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Variable | Plain-text config stored in GitHub | साधारण config मान |
| vars context | Expression to read variables | variables पढ़ने का context |
| Scope | Org / repo / environment level | स्तर |
| Precedence | Most specific scope wins | प्राथमिकता |
| Feature flag | Toggle for enabling features | feature चालू/बंद स्विच |
| Reproducibility | Same input gives same result | दोहराने योग्य परिणाम |

---

## ⚡ 3-Line Summary
English: Variables hold non-sensitive config read via `vars.NAME` at repo, environment or org scope.
They are plain text and logged, so never store secrets in them.
Most specific scope wins; values are evaluated at run time, even on re-runs.
Hindi: Variables गैर-संवेदनशील config रखते हैं जो `vars.NAME` से repo, environment या org स्तर पर पढ़े जाते हैं।
ये plain text हैं और logs में दिखते हैं, इसलिए secrets कभी इनमें मत रखो।
सबसे specific scope जीतता है; value run time पर तय होती है, re-run पर भी।

---

## ➡️ Next Topic
**38. GitHub Packages**: publish and consume your own npm, Docker and Python packages from GitHub itself.

---
