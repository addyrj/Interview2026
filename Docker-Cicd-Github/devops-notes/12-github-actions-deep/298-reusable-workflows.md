# 298. Reusable Workflows
# हिंदी में: Reusable Workflows (दोबारा इस्तेमाल होने वाले Workflows)

---

## 🔵 Simple Definition (English)
A **reusable workflow** is a normal workflow file that uses `on: workflow_call`. Other workflows call it as a whole **job** with `uses: owner/repo/.github/workflows/file.yml@ref`. You pass `inputs` and `secrets` in, and read `outputs` back.
It is "a function for pipelines".

## 🔵 सरल परिभाषा (Hindi)
**Reusable workflow** एक सामान्य workflow file होती है जिसमें `on: workflow_call` होता है। दूसरे workflows इसे पूरी **job** की तरह `uses: owner/repo/.github/workflows/file.yml@ref` से call करते हैं। आप `inputs` और `secrets` अंदर भेजते हैं और `outputs` वापस पढ़ते हैं।
यह "pipelines का function" है।

---

## 🔴 Problem it Solves
Your company has 12 Node.js services and 5 FastAPI services. Each repo has a copy-pasted 120-line CI file. When you change the Node version or add a security scan, you must edit 17 repos, and they drift apart. Copy-paste also means one repo forgets the scan and ships a vulnerability.
Reusable workflows give **one source of truth**.

## 🔴 यह क्यों बना? (Hindi)
आपकी company में 12 Node.js services और 5 FastAPI services हैं। हर repo में 120 lines की CI file copy-paste की हुई है। Node version बदलना या security scan जोड़ना हो तो 17 repos edit करने पड़ते हैं, और वे अलग-अलग हो जाते हैं। एक repo scan भूल गया तो vulnerability ship हो जाती है।
Reusable workflows **एक ही source of truth** देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create .github/workflows/ci-node.yml with  on: workflow_call
Step 2 → Declare inputs: (node-version, working-directory) and secrets:
Step 3 → Write jobs: as usual; use ${{ inputs.xxx }} inside
Step 4 → Declare outputs: mapping job outputs to workflow outputs
Step 5 → In the caller workflow, create a job with
         uses: ./.github/workflows/ci-node.yml   (same repo)
         or    org/repo/.github/workflows/ci-node.yml@v1  (other repo)
Step 6 → Pass with: (inputs) and secrets: (or secrets: inherit)
Step 7 → Read results with needs.<job>.outputs.<name>
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → .github/workflows/ci-node.yml बनाओ जिसमें  on: workflow_call हो
Step 2 → inputs: (node-version, working-directory) और secrets: declare करो
Step 3 → jobs: सामान्य तरह लिखो; अंदर ${{ inputs.xxx }} इस्तेमाल करो
Step 4 → outputs: में job outputs को workflow outputs से map करो
Step 5 → Caller workflow में एक job बनाओ:
         uses: ./.github/workflows/ci-node.yml   (उसी repo में)
         या    org/repo/.github/workflows/ci-node.yml@v1  (दूसरे repo में)
Step 6 → with: (inputs) और secrets: (या secrets: inherit) pass करो
Step 7 → needs.<job>.outputs.<name> से result पढ़ो
```

---

## 🟡 Real World Example
A platform team at a Bengaluru fintech keeps a repo `acme/.github-workflows` with `ci-node.yml`, `ci-python.yml`, and `deploy-vps.yml`. Every service repo has a 15-line caller file. When security wants Trivy scans added, the platform team edits one file, tags `v2`, and teams upgrade `@v1` to `@v2` by PR. Compliance can show that all 17 services run the same checks.

## 🟡 Real Example Hindi mein
Bengaluru की एक fintech का platform team `acme/.github-workflows` repo रखता है जिसमें `ci-node.yml`, `ci-python.yml` और `deploy-vps.yml` हैं। हर service repo में सिर्फ 15 lines की caller file है। Security team Trivy scan जुड़वाना चाहे तो platform team एक file edit करके `v2` tag लगाता है, और teams PR से `@v1` को `@v2` कर लेती हैं। Compliance साबित कर सकता है कि सभी 17 services वही checks चलाती हैं।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/ci-node.yml   (the CALLED / reusable workflow)
name: Reusable Node CI              # name shown in UI

on:
  workflow_call:                    # makes this workflow callable
    inputs:
      node-version:                 # input name
        description: "Node version"
        required: false             # optional input
        type: string                # types: string | number | boolean
        default: "20"               # used when caller omits it

jobs:
  test:
    runs-on: ubuntu-latest          # runner is chosen by the called workflow
    steps:
      - uses: actions/checkout@v4   # get code of the CALLER repo
      - uses: actions/setup-node@v4 # install Node
        with:
          node-version: ${{ inputs.node-version }}  # use the input
          cache: npm                # cache ~/.npm
      - run: npm ci                 # clean install from lockfile
      - run: npm test               # run tests
```

```yaml
# .github/workflows/ci.yml          (the CALLER workflow, same repo)
name: CI

on:
  pull_request:                     # run on PRs

jobs:
  node-ci:                          # this job IS the reusable workflow
    uses: ./.github/workflows/ci-node.yml   # path in the same repo (no @ref)
    with:
      node-version: "22"            # override the default
```

## 💻 Code / Config Example — Advanced
```yaml
# acme/platform-workflows/.github/workflows/deploy-vps.yml
name: Reusable VPS deploy

on:
  workflow_call:
    inputs:
      app-name:                     # e.g. billing-api
        type: string
        required: true
      environment:                  # staging | production
        type: string
        required: true
      image-tag:                    # git sha of the built image
        type: string
        required: true
    secrets:
      SSH_PRIVATE_KEY:              # secret must be declared to be passed
        required: true
      SSH_HOST:
        required: true
    outputs:
      deployed-url:                 # workflow-level output
        description: "URL after deploy"
        value: ${{ jobs.deploy.outputs.url }}   # maps from job output

permissions:
  contents: read                    # called workflow cannot exceed caller's perms

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}   # approval rules per environment
    outputs:
      url: ${{ steps.done.outputs.url }}     # job output from a step
    steps:
      - name: Prepare SSH key
        run: |                                # write key to disk with safe mode
          install -m 600 /dev/null key
          printf '%s\n' "$KEY" > key
        env:
          KEY: ${{ secrets.SSH_PRIVATE_KEY }} # via env, never inline in script
      - name: Deploy over SSH
        run: |
          ssh -i key -o StrictHostKeyChecking=accept-new deploy@"$HOST" \
            "cd /srv/${APP} && IMAGE_TAG=${TAG} docker compose pull && docker compose up -d"
        env:
          HOST: ${{ secrets.SSH_HOST }}       # VPS hostname
          APP: ${{ inputs.app-name }}         # input as env avoids injection
          TAG: ${{ inputs.image-tag }}
      - id: done                              # step that sets the output
        run: echo "url=https://${{ inputs.app-name }}.example.com" >> "$GITHUB_OUTPUT"
```

```yaml
# service repo: .github/workflows/release.yml  (CALLER from another repo)
name: Release

on:
  push:
    branches: [main]

jobs:
  deploy-prod:
    uses: acme/platform-workflows/.github/workflows/deploy-vps.yml@v1   # pin tag
    with:
      app-name: billing-api
      environment: production
      image-tag: ${{ github.sha }}
    secrets:
      SSH_PRIVATE_KEY: ${{ secrets.PROD_SSH_KEY }}   # explicit mapping
      SSH_HOST: ${{ secrets.PROD_SSH_HOST }}
    # alternative: secrets: inherit   (same org only, passes all secrets)

  smoke:
    needs: deploy-prod                              # wait for the called workflow
    runs-on: ubuntu-latest
    steps:
      - run: curl -fsS "${{ needs.deploy-prod.outputs.deployed-url }}/health"
```

---

## 🟠 My Stack Integration
- **Node.js / React:** one `ci-node.yml` with inputs `working-directory` and `node-version`; React app and Express API both call it.
- **FastAPI:** `ci-python.yml` with `python-version` input; runs ruff + pytest.
- **VPS + Nginx:** `deploy-vps.yml` above SSHes in, runs `docker compose up -d`, then `nginx -t && nginx -s reload`.
- **AWS:** a reusable workflow that uses OIDC (`id-token: write`) to assume a role; the caller must also grant `id-token: write`.

```yaml
# caller for your monorepo: two jobs reuse the same template
jobs:
  api:
    uses: ./.github/workflows/ci-node.yml    # reusable in same repo
    with:
      working-directory: api                 # folder of Express API
  web:
    uses: ./.github/workflows/ci-node.yml
    with:
      working-directory: web                 # folder of React app
```
(For this the called workflow must declare the `working-directory` input and use `defaults.run.working-directory`.)

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting `uses:` on a step instead of a job. Reusable workflows are called at job level.
✅ Correct: `jobs.<id>.uses: path@ref`. Steps use actions; jobs use workflows.

❌ Mistake 2: Forgetting to declare `secrets:` in `workflow_call`, then passing them.
✅ Correct: Declare each secret under `on.workflow_call.secrets` or use `secrets: inherit` (same org/enterprise).

❌ Mistake 3: Referencing `@main` of a shared repo. Anyone with push access can change every pipeline instantly.
✅ Correct: Pin to a tag (`@v1`) or a full commit SHA for sensitive pipelines.

❌ Mistake 4: Expecting `env:` of the caller workflow to be visible inside the called one. It is not.
✅ Correct: Pass values through `inputs`. Contexts like `vars` of the caller repo are available, `env` is not.

❌ Mistake 5: Nesting too deep. Limits: up to 10 levels of nesting (caller + 9 levels, check current docs) and 50 unique reusable workflows per run.
✅ Correct: Keep it flat; one level of reuse is plenty.

---

## 🧠 Tricky Interview Question
**Q:** A called workflow has `runs-on: ubuntu-latest`. The caller job says `runs-on: self-hosted`. Which runner is used?

**Answer:** The caller job cannot have `runs-on` at all; a job that uses `uses:` is only allowed `with`, `secrets`, `needs`, `if`, `permissions`, `strategy`, `concurrency`. The runner is decided inside the called workflow. If you want caller-controlled runners, pass a `runner` input and write `runs-on: ${{ inputs.runner }}` in the called workflow. Also remember the `GITHUB_TOKEN` permissions of the called workflow can only be equal or lower than the caller's.

---

## ⚫ Interview Questions + Answers

Q1: Reusable workflow vs composite action?
A1: A reusable workflow contains whole **jobs** (own runners, `needs`, matrix, environments, secrets). A composite action bundles **steps** and runs inside the caller's job on the same runner. Use workflows for pipelines, composites for repeated step groups.

Q2: How do you return data from a reusable workflow?
A2: Define `on.workflow_call.outputs` with `value: ${{ jobs.<id>.outputs.<name> }}`, and the caller reads `needs.<job>.outputs.<name>`.

Q3: What does `secrets: inherit` do and what is the risk?
A3: It passes all caller secrets to the called workflow without naming them. Risk: the called workflow gets more secrets than it needs; prefer explicit mapping for external or shared repos.

Q4: Can a private repo's reusable workflow be used by another repo?
A4: Yes, if the repo's Actions settings allow access ("Accessible from repositories in the organization"). Public repos can call workflows from public repos.

Q5: How do you test a change to a shared workflow safely?
A5: Create a branch or pre-release tag in the shared repo and point one test caller to `@my-branch`; once it works, merge and release `v1.x`, then move the `v1` tag.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many repos need the same CI/CD stages
- You want centralized security/compliance steps
- You need a full job (runner, matrix, environment) as a template

❌ Avoid when:
- You only repeat 3-4 steps (use a composite action)
- Only one repo uses it (extra indirection, harder debugging)
- You need dynamic number of jobs decided at runtime (use matrix or generate YAML)

---

## 📊 Visual Diagram
```
 service-a/ci.yml      service-b/ci.yml      service-c/ci.yml
 jobs:                 jobs:                 jobs:
  ci:                   ci:                   ci:
   uses: ...@v1          uses: ...@v1          uses: ...@v1
   with: {node: 20}      with: {node: 22}      with: {node: 20}
        \                    |                    /
         \                   |                   /
          v                  v                  v
        +--------------------------------------------+
        | platform-workflows/.github/workflows/      |
        |   ci-node.yml   (on: workflow_call)        |
        |   inputs -> jobs -> outputs                |
        +--------------------------------------------+
                          |
                outputs back to callers (needs.ci.outputs.*)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `workflow_call` | Trigger that makes a workflow callable | workflow को callable बनाने वाला trigger |
| Caller | Workflow that uses another workflow | call करने वाला workflow |
| Called workflow | The reusable workflow | जिसे call किया जाए |
| `inputs` | Parameters passed with `with:` | parameters |
| `secrets: inherit` | Pass all secrets implicitly | सारे secrets अपने आप pass |
| `outputs` | Values returned to caller | caller को लौटाए values |
| Pin to SHA/tag | Fix version of shared workflow | version fix करना |

---

## ⚡ 3-Line Summary
English: A reusable workflow uses `on: workflow_call` and is called from a job with `uses:`.
Inputs, secrets, and outputs make it a function for pipelines, giving one source of truth across repos.
Pin it to a tag or SHA, pass secrets explicitly, and use composite actions when you only need shared steps.
Hindi: Reusable workflow `on: workflow_call` इस्तेमाल करता है और job में `uses:` से call होता है।
Inputs, secrets और outputs इसे pipelines का function बनाते हैं, जिससे सभी repos में एक ही source of truth रहता है।
इसे tag या SHA पर pin करें, secrets साफ़-साफ़ pass करें, और सिर्फ steps share करने हों तो composite action लें।

---

## ➡️ Next Topic
**299. Composite Actions** — when you only need to share a group of steps (not whole jobs), a composite action is lighter than a reusable workflow.
