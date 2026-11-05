# 303. Checkout Code (actions/checkout)
# हिंदी में: Code Checkout करना (actions/checkout)

---

## 🔵 Simple Definition (English)
`actions/checkout` is the official action that downloads your repository's code onto the runner's disk (into `$GITHUB_WORKSPACE`) at the commit that triggered the workflow. A new runner VM starts empty, so without checkout there are no files to build or test.

## 🔵 सरल परिभाषा (Hindi)
`actions/checkout` official action है जो आपके repository का code runner की disk पर (`$GITHUB_WORKSPACE` में) उसी commit पर download करती है जिसने workflow trigger किया। नया runner VM खाली होता है, इसलिए checkout के बिना build या test करने के लिए files ही नहीं होतीं।

---

## 🔴 Problem it Solves
Each job runs on a fresh, empty virtual machine. Your repo is not there. You could `git clone` manually, but then you must handle authentication for private repos, the correct PR merge commit, submodules, LFS files, shallow history, and credential cleanup. Doing this by hand is error-prone and can leak tokens.
The action does all this correctly with sane defaults.

## 🔴 यह क्यों बना? (Hindi)
हर job एक नई, खाली virtual machine पर चलती है। आपका repo वहाँ नहीं होता। आप हाथ से `git clone` कर सकते हैं, पर तब private repos की authentication, सही PR merge commit, submodules, LFS files, shallow history और credentials की सफ़ाई खुद संभालनी पड़ेगी। यह गलतियों वाला है और tokens leak कर सकता है।
यह action ये सब सही defaults के साथ कर देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Runner starts with an empty workspace folder
Step 2 → actions/checkout reads github.sha / github.ref of the event
         (push: the pushed commit; pull_request: refs/pull/N/merge)
Step 3 → It auths using GITHUB_TOKEN (token input default)
Step 4 → git init + fetch only what is needed (default fetch-depth: 1)
Step 5 → git checkout of that commit (detached HEAD)
Step 6 → Persists credentials in .git/config (persist-credentials: true default)
Step 7 → Later steps run inside the workspace; post-step cleans up credentials
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Runner खाली workspace folder के साथ शुरू होता है
Step 2 → actions/checkout event का github.sha / github.ref पढ़ता है
         (push: pushed commit; pull_request: refs/pull/N/merge)
Step 3 → GITHUB_TOKEN (token input का default) से auth करता है
Step 4 → git init + सिर्फ़ ज़रूरी fetch (default fetch-depth: 1)
Step 5 → उस commit का git checkout (detached HEAD)
Step 6 → Credentials .git/config में रखता है (persist-credentials: true default)
Step 7 → बाद के steps workspace में चलते हैं; post-step credentials साफ़ करता है
```

---

## 🟡 Real World Example
A release job needs the full git history to generate a changelog between tags: it uses `fetch-depth: 0`. A CI job for a React app only needs the latest commit: default shallow clone makes checkout 2 seconds instead of 40 on a repo with 8 years of history. A deploy job needs a private "infra" repo too, so it checks out two repos into different paths.

## 🟡 Real Example Hindi mein
Release job को tags के बीच changelog बनाने के लिए पूरा git history चाहिए: वह `fetch-depth: 0` इस्तेमाल करती है। React app की CI job को सिर्फ़ latest commit चाहिए: default shallow clone से 8 साल पुराने history वाले repo में checkout 40 के बजाय 2 सेकंड में होता है। Deploy job को private "infra" repo भी चाहिए, इसलिए वह दो repos अलग-अलग paths में checkout करती है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/checkout-basic.yml
name: Checkout Basic               # workflow name

on: [push]                         # run on every push

jobs:
  show:
    runs-on: ubuntu-latest         # empty Linux VM
    steps:
      - name: Before checkout      # prove the workspace is empty
        run: ls -la "$GITHUB_WORKSPACE"     # prints nothing useful
      - uses: actions/checkout@v4  # download the repo (shallow, 1 commit)
      - name: After checkout       # now files exist
        run: ls -la "$GITHUB_WORKSPACE"     # shows your project files
      - run: git log --oneline -n 3         # only 1 commit visible (shallow)
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/checkout-advanced.yml
name: Checkout Advanced

on:
  push:
    tags: ["v*"]                   # release tags

permissions:
  contents: read                   # checkout needs only read

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      # 1. Main repo with full history for changelog generation
      - name: Checkout app
        uses: actions/checkout@v4
        with:
          fetch-depth: 0           # full history + tags (0 = all)
          submodules: recursive    # also init nested submodules
          lfs: false               # set true only if you track big files with Git LFS
          persist-credentials: false   # do not leave token in .git/config (safer)

      # 2. A second, private repo placed in a sub-folder
      - name: Checkout infra repo
        uses: actions/checkout@v4
        with:
          repository: acme/infra-config          # owner/name of other repo
          ref: main                              # branch, tag or SHA
          path: infra                            # clone into ./infra
          token: ${{ secrets.INFRA_REPO_PAT }}   # fine-grained PAT with read access
          persist-credentials: false

      # 3. Sparse checkout: only needed folders (big monorepos)
      - name: Sparse checkout of web only
        uses: actions/checkout@v4
        with:
          path: web-only
          sparse-checkout: |                     # git sparse-checkout patterns
            web
            package.json
          sparse-checkout-cone-mode: false       # allow file patterns like package.json

      - name: Generate changelog
        run: |
          PREV=$(git describe --tags --abbrev=0 "${GITHUB_REF_NAME}^" 2>/dev/null || true)
          git log --pretty='- %s' ${PREV:+$PREV..}"$GITHUB_REF_NAME" > CHANGELOG.txt
          cat CHANGELOG.txt
      - name: Show the config repo
        run: ls infra
```

---

## 🟠 My Stack Integration
- **Node.js / React:** default shallow checkout, then `setup-node` + `npm ci`.
- **FastAPI:** same; if you compute version from `git describe`, use `fetch-depth: 0`.
- **Nginx / VPS:** check out the repo containing `deploy/nginx.conf`, then `scp` only that folder to the VPS; never leave a token in `.git/config` on artifacts you upload (use `persist-credentials: false`).
- **AWS:** checkout `infra` repo with a read-only deploy key or fine-grained PAT to fetch Terraform/CloudFormation templates.

```yaml
# Typical first steps in every one of your jobs
    steps:
      - uses: actions/checkout@v4           # code for this repo
        with:
          persist-credentials: false        # tokens not stored on disk
      - uses: actions/setup-node@v4         # next: runtime (topic 304)
        with:
          node-version: 20
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting checkout, then `npm ci` fails with "package.json not found".
✅ Correct: Put `actions/checkout` as the first step.

❌ Mistake 2: Using `git describe`, `git log` over tags, or version-from-git tools with the default shallow clone.
✅ Correct: `fetch-depth: 0` for jobs that need history or tags.

❌ Mistake 3: Uploading the whole workspace as an artifact while `.git/config` holds the token (default `persist-credentials: true`).
✅ Correct: `persist-credentials: false` unless you need to `git push` later in the job.

❌ Mistake 4: Using `pull_request_target` and checking out `github.event.pull_request.head.sha`. This runs untrusted PR code with secrets.
✅ Correct: Use `pull_request`, or do not check out PR code in privileged workflows.

❌ Mistake 5: Checking out a private repo with `GITHUB_TOKEN` (it only has access to the current repo).
✅ Correct: Use a deploy key (`ssh-key:`) or a fine-grained PAT / GitHub App token.

---

## 🧠 Tricky Interview Question
**Q:** On a `pull_request` run, you print `git rev-parse HEAD` and it does not match the latest commit shown on the PR. Is checkout broken?

**Answer:** No. For `pull_request` the default ref is the **merge commit** `refs/pull/<n>/merge`, a temporary commit of the PR head merged into the base branch. So `HEAD` is a different SHA, and `github.sha` is also that merge SHA. This is intentional: you test what the code will look like after merging. If you need the actual PR head commit, use `ref: ${{ github.event.pull_request.head.sha }}` (and think about security), or read the head from `HEAD^2`.

---

## ⚫ Interview Questions + Answers

Q1: Why is `fetch-depth: 1` the default?
A1: Speed. Only the single commit is fetched, which saves time and bandwidth on large repos. Use `0` for full history, or a number for partial history.

Q2: How does checkout authenticate for the current private repo?
A2: With the automatic `GITHUB_TOKEN` (the `token` input defaults to it). Its permissions come from the `permissions:` block (needs `contents: read`).

Q3: What does `path:` do?
A3: Clones into a sub-folder of `$GITHUB_WORKSPACE`, allowing several repos in one job. Subsequent steps need `working-directory` or paths adjusted.

Q4: What is `clean` and what happens on self-hosted runners?
A4: `clean: true` (default) runs `git clean -ffdx` and reset before checkout so old build files do not leak between runs. On self-hosted runners the workspace persists, so stale files and leaked secrets are real risks.

Q5: How do you handle submodules and LFS?
A5: `submodules: true|recursive` and `lfs: true`. Private submodules need a token/SSH key that can read them.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any job needs your source files (almost all)
- You need tags/history (use `fetch-depth: 0`)
- You need extra repos (`repository`, `path`)

❌ Avoid when:
- The job only uses artifacts or published images (no code needed; skip checkout)
- Doing a deploy-only job that just SSHes to a server
- Using untrusted PR code in privileged workflows

---

## 📊 Visual Diagram
```
 Runner VM (fresh)               GitHub repo
 +---------------------+         +--------------------+
 | $GITHUB_WORKSPACE   |         |  main ... A--B--C  |
 | (empty)             |         |  PR #12 -> merge M |
 +---------------------+         +--------------------+
          |                                |
          |  actions/checkout@v4           |
          |  token = GITHUB_TOKEN          |
          |  fetch-depth: 1                |
          +------------------------------->|
          |<--- files at commit/merge M ---+
          v
 +---------------------+
 | package.json src/.. |  -> next steps: setup-node, npm ci, test
 | .git (shallow)      |
 +---------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `actions/checkout` | Action that downloads repo code | repo का code लाने वाली action |
| `GITHUB_WORKSPACE` | Folder where code is placed | code वाला folder |
| `fetch-depth` | How many commits to fetch | कितने commits लाने हैं |
| Shallow clone | Clone with limited history | सीमित history वाला clone |
| `persist-credentials` | Keep token in git config | token को git config में रखना |
| Sparse checkout | Fetch only chosen folders | चुने folders ही लाना |
| Merge commit ref | `refs/pull/N/merge` for PRs | PR का merge commit |

---

## ⚡ 3-Line Summary
English: `actions/checkout` puts your code on the empty runner, shallow by default.
Use `fetch-depth: 0` for history, `path` and `repository` for extra repos, and `persist-credentials: false` for safety.
PR runs check out the merge commit, not the PR head.
Hindi: `actions/checkout` खाली runner पर आपका code रखता है, default में shallow।
History के लिए `fetch-depth: 0`, extra repos के लिए `path` और `repository`, और सुरक्षा के लिए `persist-credentials: false` इस्तेमाल करें।
PR runs में merge commit checkout होता है, PR head नहीं।

---

## ➡️ Next Topic
**304. Setup Node.js (actions/setup-node)** — with code on the runner, the next step is installing the right Node version.
