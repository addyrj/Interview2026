# 259. with: Parameters
# हिंदी में: with: Parameters (Action के Inputs)

---

## 🔵 Simple Definition (English)
`with:` is the key used on a `uses:` step to pass input parameters to an action (or to a reusable workflow job). Each key must match an `inputs:` name declared in that action's `action.yml`. All values arrive as strings.

## 🔵 सरल परिभाषा (Hindi)
`with:` वह key है जो `uses:` वाले step पर किसी action (या reusable workflow job) को input parameters देने के काम आती है। हर key उस action की `action.yml` में declared `inputs:` के नाम से match होनी चाहिए। सारी values string के रूप में पहुँचती हैं।

---

## 🔴 Problem it Solves
A shared action like `actions/setup-node` must work for every project: Node 18 or 20, npm or pnpm cache, a private registry. Without a parameter mechanism you would fork the action for each variation. `with:` makes actions configurable and reusable without editing their code.

## 🔴 यह क्यों बना? (Hindi)
`actions/setup-node` जैसे shared action को हर project के लिए चलना है: Node 18 या 20, npm या pnpm cache, private registry। Parameter mechanism के बिना हर variation के लिए action को fork करना पड़ता। `with:` actions को उनका code बदले बिना configurable और reusable बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Action author declares inputs: in action.yml (name, default, required)
Step 2 → You write uses: owner/action@version and a with: map under it
Step 3 → Runner evaluates ${{ }} expressions inside with: values
Step 4 → Each input is exposed to the action as env var INPUT_<UPPERCASE_NAME>
Step 5 → JS actions read via core.getInput('name'); composite via ${{ inputs.name }}
Step 6 → Missing input -> default is used; required and missing -> step fails
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Action author action.yml में inputs: declare करता है (name, default, required)
Step 2 → आप uses: owner/action@version लिखते हैं और उसके नीचे with: map
Step 3 → Runner with: values के अंदर ${{ }} expressions evaluate करता है
Step 4 → हर input action को env var INPUT_<UPPERCASE_NAME> के रूप में मिलता है
Step 5 → JS actions core.getInput('name') से पढ़ते हैं; composite ${{ inputs.name }} से
Step 6 → Input न दिया -> default; required है और नहीं दिया -> step fail
```

---

## 🟡 Real World Example
Your React + Node monorepo uses `actions/setup-node` with `node-version: 20` and `cache: npm`. Then `docker/build-push-action` receives `context`, `push: true`, `tags`. Then `aws-actions/configure-aws-credentials` gets `role-to-assume` and `aws-region: ap-south-1` (Mumbai region, where Indian startups like Zomato-type workloads often run for low latency).

## 🟡 Real Example Hindi mein
आपका React + Node monorepo `actions/setup-node` को `node-version: 20` और `cache: npm` देता है। फिर `docker/build-push-action` को `context`, `push: true`, `tags` मिलते हैं। फिर `aws-actions/configure-aws-credentials` को `role-to-assume` और `aws-region: ap-south-1` (Mumbai region, जहाँ Zomato-type Indian workloads low latency के लिए चलते हैं)।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/with-basic.yml
name: with-basic                       # workflow name
on: push                               # run on push
jobs:
  build:
    runs-on: ubuntu-24.04              # example runner label
    steps:
      - uses: actions/checkout@v4      # action with no inputs needed (defaults used)
      - uses: actions/setup-node@v4    # action that takes inputs
        with:                          # input map for setup-node
          node-version: 20             # which Node version to install
          cache: npm                   # cache ~/.npm keyed by package-lock.json
      - run: node --version            # run: steps do NOT use with:, they use env:
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/with-advanced.yml
name: build-and-push                   # Docker build + push to GHCR
on:
  push:
    branches: [main]                   # only main
permissions:
  contents: read                       # read repo
  packages: write                      # needed to push to GHCR
jobs:
  image:
    runs-on: ubuntu-24.04              # example runner
    steps:
      - uses: actions/checkout@v4      # get source
      - uses: docker/setup-buildx-action@v3    # example version; enables BuildKit
      - uses: docker/login-action@v3   # example version
        with:
          registry: ghcr.io            # registry host
          username: ${{ github.actor }}        # user who triggered
          password: ${{ secrets.GITHUB_TOKEN }} # auto token, no manual secret
      - id: meta                       # id so later steps can read outputs
        uses: docker/metadata-action@v5        # generates tags/labels
        with:
          images: ghcr.io/${{ github.repository }}   # image name
          tags: |                      # multi-line string = list of rules
            type=sha
            type=ref,event=branch
      - uses: docker/build-push-action@v6    # example version
        with:
          context: .                   # build context = repo root
          file: ./Dockerfile           # which Dockerfile
          push: true                   # push after build (string "true" internally)
          tags: ${{ steps.meta.outputs.tags }}       # tags from previous step
          labels: ${{ steps.meta.outputs.labels }}   # OCI labels
          cache-from: type=gha         # read GitHub Actions cache
          cache-to: type=gha,mode=max  # write cache for next run
```
Versions shown are examples; check each action's README for the current major version and exact input names. YAML was parsed locally, not executed on GitHub.

---

## 🟠 My Stack Integration
- **Node.js**: `setup-node` with `node-version-file: .nvmrc` keeps CI and local Node in sync.
- **FastAPI**: `actions/setup-python@v5` with `python-version: "3.12"` (quote it, else `3.10` becomes `3.1`) and `cache: pip`.
- **React**: `actions/upload-artifact` with `name: web-dist`, `path: dist/`, `retention-days: 7`.
- **AWS**: `configure-aws-credentials` with `role-to-assume` (OIDC) instead of static keys.
- **VPS/Nginx**: `appleboy/ssh-action`-style third-party actions take `host`, `username`, `key` via `with:` (pin them by commit SHA because they receive your key).

```yaml
      - uses: actions/setup-python@v5  # FastAPI job
        with:
          python-version: "3.12"       # quoted: otherwise 3.10 would parse as float 3.1
          cache: pip                   # cache pip downloads
      - uses: actions/upload-artifact@v4   # keep React build for deploy job
        with:
          name: web-dist               # artifact name
          path: dist/                  # folder to upload
          retention-days: 7            # auto delete after a week
          if-no-files-found: error     # fail if build produced nothing
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `python-version: 3.10` unquoted.
✅ Correct: `python-version: "3.10"`; YAML reads the unquoted one as the number 3.1.

❌ Mistake 2: Using `with:` on a `run:` step.
✅ Correct: `run:` steps take `env:` and `shell:`/`working-directory:`. Only `uses:` steps take `with:`.

❌ Mistake 3: Guessing input names (`nodeVersion`).
✅ Correct: Copy exact names from the action's README / `action.yml`; unknown inputs only produce a warning and are ignored.

❌ Mistake 4: Passing real secrets as `with:` to unpinned third-party actions (`@main`).
✅ Correct: Pin to a full commit SHA for actions that receive credentials.

❌ Mistake 5: Expecting booleans: `if: inputs.push == false` style logic inside actions.
✅ Correct: Inside the action, inputs are strings; compare with `'true'`.

---

## 🧠 Tricky Interview Question
You wrote `with: { node-version: 20, cache: npm }` but your Node project uses `yarn.lock`. The step passes but the next run is no faster. Why?

Answer: `cache: npm` makes `setup-node` look for `package-lock.json` to compute the cache key; with `yarn.lock` it either errors ("Dependencies lock file is not found") or never matches, so nothing is reused. Set `cache: yarn` (or `pnpm`), or point `cache-dependency-path` to the right lock file. Also confirm you run the install after setup-node so the cache has something to restore.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `with:` and `env:`?
A1: `with:` passes declared inputs to an action. `env:` sets environment variables for the step process. Actions may read both, but only `with:` is validated against `action.yml`.

Q2: How does an action receive `with:` values?
A2: As environment variables named `INPUT_<NAME>` (uppercased, spaces to underscores); toolkit helpers like `core.getInput` read them.

Q3: Are `with:` values typed?
A3: No. Everything is a string, even if you write `true` or `20`.

Q4: Can `with:` accept expressions?
A4: Yes, `${{ }}` is evaluated first (contexts allowed include github, needs, matrix, steps, env, vars, secrets, inputs).

Q5: Does `with:` also exist on jobs?
A5: Yes, for a job that calls a reusable workflow (`uses: ./.github/workflows/x.yml`), `with:` passes `workflow_call` inputs, and `secrets:` passes secrets.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Configuring any marketplace or local action
- Calling a reusable workflow with inputs
- Passing outputs of earlier steps to an action

❌ Avoid when:
- The step is a plain `run:` (use `env:`)
- You need to pass a large JSON blob (store in a file/artifact)
- The value is a long-lived secret to an unaudited action

---

## 📊 Visual Diagram
```
 workflow step                        action (action.yml)
 +--------------------------+         +------------------------------+
 | uses: actions/setup-node |         | inputs:                      |
 | with:                    |  --->   |   node-version: {default: ''}|
 |   node-version: 20       |         |   cache: {default: ''}       |
 |   cache: npm             |         +---------------+--------------+
 +--------------------------+                         |
                                          env INPUT_NODE-VERSION=20
                                          env INPUT_CACHE=npm
                                                      v
                                              action code runs
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| with: | Inputs passed to an action | Action को दिए जाने वाले inputs |
| inputs: | Parameters declared by action author | Action में declared parameters |
| INPUT_NAME | Env var form of an input | Input का env var रूप |
| Pinning | Fixing action to a SHA/version | Action को SHA/version पर fix करना |
| Reusable workflow | Workflow called by another | दूसरे workflow द्वारा call किया workflow |

---

## ⚡ 3-Line Summary
English: `with:` passes inputs to a `uses:` action, matching names in its `action.yml`.
Values are always strings and arrive as `INPUT_*` environment variables.
Quote versions, copy exact input names, and pin actions that receive secrets.
Hindi: `with:` एक `uses:` action को inputs देता है, जो उसकी `action.yml` के नामों से match होते हैं।
Values हमेशा string होती हैं और `INPUT_*` environment variables के रूप में पहुँचती हैं।
Versions को quote करो, input नाम सही कॉपी करो, और secrets पाने वाले actions को pin करो।

---

## ➡️ Next Topic
**260. if: Conditionals** — now that steps are configured, learn to run them only when a condition is true.
