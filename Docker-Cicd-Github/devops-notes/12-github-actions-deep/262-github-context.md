# 262. github Context
# हिंदी में: github Context

---

## 🔵 Simple Definition (English)
The `github` context holds information about the workflow run and the event that triggered it: repository, commit SHA, branch/tag, actor, event name, the full event payload (`github.event`), run ids and the automatic `GITHUB_TOKEN`. Most values are also exported as `GITHUB_*` environment variables.

## 🔵 सरल परिभाषा (Hindi)
`github` context में workflow run और उसे trigger करने वाले event की जानकारी होती है: repository, commit SHA, branch/tag, actor, event name, पूरा event payload (`github.event`), run ids और automatic `GITHUB_TOKEN`। ज़्यादातर values `GITHUB_*` environment variables के रूप में भी मिलती हैं।

---

## 🔴 Problem it Solves
Your pipeline must know which commit to build, which branch is deploying, who pushed, whether it is a PR from a fork, and link back to the run in a Slack message. Without this context you would call the Git CLI or REST API in every job and still not have the original event data (labels, PR number, release tag).

## 🔴 यह क्यों बना? (Hindi)
आपकी pipeline को पता होना चाहिए कौन सा commit build करना है, कौन सी branch deploy हो रही है, किसने push किया, क्या यह fork का PR है, और Slack message में run का link देना है। इस context के बिना हर job में Git CLI या REST API call करनी पड़ती और फिर भी original event data (labels, PR number, release tag) नहीं मिलता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Webhook event arrives (push, pull_request, release ...)
Step 2 → GitHub builds github.* fields (sha, ref, actor, repository ...)
Step 3 → The raw webhook JSON is attached as github.event
Step 4 → github.token is minted: a short-lived GITHUB_TOKEN for this run
Step 5 → You read fields via ${{ github.X }} anywhere contexts are allowed
Step 6 → Inside shell you can use the same data as $GITHUB_SHA, $GITHUB_REF ...
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Webhook event आता है (push, pull_request, release ...)
Step 2 → GitHub github.* fields बनाता है (sha, ref, actor, repository ...)
Step 3 → Raw webhook JSON github.event के रूप में जुड़ता है
Step 4 → github.token बनता है: इस run के लिए short-lived GITHUB_TOKEN
Step 5 → आप ${{ github.X }} से fields पढ़ते हैं जहाँ contexts allowed हैं
Step 6 → Shell में वही data $GITHUB_SHA, $GITHUB_REF ... के रूप में मिलता है
```

---

## 🟡 Real World Example
A release workflow triggers on `release: published`. It reads `github.event.release.tag_name` to tag the Docker image `v1.4.2`, `github.repository` for the ECR repo name, `github.actor` for the audit line "deployed by priya", and `github.server_url/github.repository/actions/runs/github.run_id` for the Slack link. Swiggy-style on-call teams love that link in alerts.

## 🟡 Real Example Hindi mein
एक release workflow `release: published` पर trigger होता है। वह Docker image को `v1.4.2` tag करने के लिए `github.event.release.tag_name` पढ़ता है, ECR repo नाम के लिए `github.repository`, audit line "deployed by priya" के लिए `github.actor`, और Slack link के लिए `github.server_url/github.repository/actions/runs/github.run_id`। Swiggy-style on-call टीमों को alerts में यह link बहुत काम आता है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/github-ctx-basic.yml
name: github-ctx-basic                 # workflow name
on: [push, pull_request]               # two events
jobs:
  info:
    runs-on: ubuntu-24.04              # example runner
    steps:
      - name: Print key fields         # print most-used fields
        run: |                         # shell block
          echo "event       : ${{ github.event_name }}"     # push / pull_request
          echo "repository  : ${{ github.repository }}"     # owner/repo
          echo "owner       : ${{ github.repository_owner }}"  # owner only
          echo "ref         : ${{ github.ref }}"            # refs/heads/main
          echo "ref_name    : ${{ github.ref_name }}"       # main (short)
          echo "ref_type    : ${{ github.ref_type }}"       # branch or tag
          echo "sha         : ${{ github.sha }}"            # 40-char commit
          echo "actor       : ${{ github.actor }}"          # who pushed
          echo "run         : ${{ github.run_id }} #${{ github.run_number }} attempt ${{ github.run_attempt }}"  # ids
          echo "workflow    : ${{ github.workflow }} / job ${{ github.job }}"   # names
          echo "url         : ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"  # link
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/github-ctx-advanced.yml
name: release-deploy                   # tag-driven release
on:
  push:
    tags: ['v*.*.*']                   # semantic version tags
  pull_request:
    branches: [main]                   # PR checks
permissions:
  contents: read                       # least privilege token
  pull-requests: write                 # allow commenting on PRs
concurrency:
  group: deploy-${{ github.workflow }}-${{ github.ref }}   # one run per ref
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}  # cancel old PR runs only
jobs:
  build:
    runs-on: ubuntu-24.04              # example runner
    steps:
      - uses: actions/checkout@v4      # get code at github.sha
      - name: Compute version          # derive image tag
        id: v                          # step id
        env:
          REF_TYPE: ${{ github.ref_type }}      # branch or tag
          REF_NAME: ${{ github.ref_name }}      # untrusted-ish, pass via env
          HEAD_REF: ${{ github.head_ref }}      # PR source branch (empty on push)
        run: |                         # bash logic
          if [ "$REF_TYPE" = "tag" ]; then          # release build
            echo "tag=${REF_NAME#v}" >> "$GITHUB_OUTPUT"   # strip leading v
          else                                      # branch or PR build
            echo "tag=${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"  # short sha
          fi
      - name: Comment on PR            # only for PRs from same repo
        if: github.event_name == 'pull_request' && github.event.pull_request.head.repo.full_name == github.repository
        env:
          GH_TOKEN: ${{ github.token }}         # same as secrets.GITHUB_TOKEN
          PR: ${{ github.event.pull_request.number }}   # PR number from payload
        run: gh pr comment "$PR" --body "Built ${{ steps.v.outputs.tag }}"   # gh CLI preinstalled on hosted runners
```
Parsed as YAML locally; not executed on GitHub. `gh` is preinstalled on GitHub-hosted runners but verify for self-hosted.

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: Docker tag = `ghcr.io/${{ github.repository }}:${{ github.sha }}`; the VPS pulls the exact commit.
- **React**: show build info: `VITE_COMMIT=${{ github.sha }}` visible on an about page for support.
- **Nginx/VPS**: deploy only `if: github.ref == 'refs/heads/main'`; log `github.actor` in `/var/log/deploy.log`.
- **AWS**: OIDC trust policy conditions use the `sub` claim built from `repo:${{ github.repository }}:ref:...`; role session name `gh-${{ github.run_id }}`.
- **Security**: `github.token` only has the permissions listed under `permissions:`; set them explicitly.

```yaml
      - name: Audit line on VPS        # record who deployed what
        run: ssh deploy@$VPS "echo '$(date -u +%FT%TZ) ${{ github.actor }} ${{ github.sha }}' >> /var/log/deploy.log"
        # actor is a GitHub username (safe charset), sha is hex: both safe; never do this with branch names or PR titles
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `github.ref` for the branch name and getting `refs/heads/main` in image tags (slashes break tags).
✅ Correct: Use `github.ref_name`; for PRs use `github.head_ref`.

❌ Mistake 2: `github.sha` on `pull_request` assumed to be the PR head commit.
✅ Correct: On PR events it is the merge commit; the head commit is `github.event.pull_request.head.sha`.

❌ Mistake 3: `echo "${{ github.event.head_commit.message }}"` in `run:`.
✅ Correct: Commit messages are attacker-controlled; pass via `env:`.

❌ Mistake 4: Forgetting `permissions:` so the token has broad default rights.
✅ Correct: Declare minimal `permissions:` at workflow or job level.

❌ Mistake 5: Expecting `github.head_ref` on push events.
✅ Correct: `head_ref` and `base_ref` are only set for `pull_request` events.

---

## 🧠 Tricky Interview Question
A PR from a fork runs your workflow. A step reads `${{ secrets.NPM_TOKEN }}` and `${{ github.token }}`. What do they contain and why?

Answer: For `pull_request` from a fork, secrets (other than the token) are empty and `github.token` is read-only. This protects secrets from malicious PR code. With `pull_request_target` the workflow runs in the base repo context with secrets, which is dangerous if you also check out and run the fork's code; treat that pattern as high risk.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `github.ref`, `ref_name`, `head_ref`?
A1: `ref` = full ref (`refs/heads/x`), `ref_name` = short name (`x`), `head_ref` = source branch of a PR (PR events only).

Q2: What is `github.event`?
A2: The full webhook payload, e.g. `github.event.pull_request.number`, `github.event.release.tag_name`. Its shape depends on the event.

Q3: `github.token` vs `secrets.GITHUB_TOKEN`?
A3: Same token. Its scope is controlled by `permissions:`; it expires when the job ends.

Q4: How to view the whole context?
A4: `${{ toJSON(github) }}` in a debug step (not in prod; it may expose tokens in some fields masked but still avoid).

Q5: Which fields identify a re-run?
A5: `run_id` stays the same, `run_attempt` increments on re-run.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Tagging images/artifacts with sha, ref, run number
- Branching logic on event type or ref
- Linking back to the run in notifications

❌ Avoid when:
- Interpolating free-text fields (title, body, commit message) into shell
- You need data not in the event (call the API with `gh`)
- You rely on `github.sha` for PR head commits

---

## 📊 Visual Diagram
```
 GitHub event (webhook JSON)
        |
        v
  +--------------------- github context ---------------------+
  | repository  sha  ref  ref_name  actor  event_name         |
  | run_id  run_number  run_attempt  workflow  job            |
  | token (GITHUB_TOKEN)   server_url   workspace             |
  | event ---> { pull_request{number,head{sha}}, release{...} } |
  +-----------------------------------------------------------+
        |                           |
  ${{ github.sha }}            $GITHUB_SHA (shell)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| github.sha | Commit SHA of the run | Run का commit SHA |
| github.ref_name | Short branch/tag name | छोटा branch/tag नाम |
| github.event | Raw webhook payload | Raw webhook payload |
| github.actor | User who triggered | Trigger करने वाला user |
| GITHUB_TOKEN | Short-lived auth token | Short-lived auth token |

---

## ⚡ 3-Line Summary
English: `github` holds run and event data: sha, ref, actor, repository, event payload and token.
Use `ref_name` for names and `event.pull_request.head.sha` for PR heads.
Pass attacker-controlled fields through `env:` and set minimal `permissions:`.
Hindi: `github` में run और event data है: sha, ref, actor, repository, event payload और token।
नाम के लिए `ref_name` और PR head के लिए `event.pull_request.head.sha` इस्तेमाल करो।
Attacker-controlled fields `env:` से पास करो और minimal `permissions:` रखो।

---

## ➡️ Next Topic
**263. env Context** — reading the environment variables you defined at workflow, job and step level.
