# 25. Pull Request Best Practices
# हिंदी में: Pull Request के Best Practices

---

## 🔵 Simple Definition (English)
A **Pull Request (PR)** is a request to merge your branch into another (usually `main`) that lets teammates review, discuss and automatically test the change first. Best practices keep PRs small, well described, tested and quick to review.

## 🔵 सरल परिभाषा (Hindi)
**Pull Request (PR)** आपकी branch को दूसरी branch (आमतौर पर `main`) में merge करने का अनुरोध है, जिससे merge से पहले teammates review, discussion और automatic testing कर सकें। Best practices PRs को छोटा, अच्छी तरह described, tested और जल्दी review होने लायक रखती हैं।

---

## 🔴 Problem it Solves
Huge PRs ("1,500 files changed") get a lazy "LGTM" and bugs slip in. PRs without description force reviewers to guess intent. PRs left open for a week create merge conflicts and block others. Good PR habits catch bugs early, spread knowledge, and keep lead time short.

## 🔴 यह क्यों बना? (Hindi)
बहुत बड़े PRs ("1,500 files changed") पर आलसी "LGTM" मिलता है और bugs निकल जाते हैं। बिना description वाले PRs में reviewer को intent का अंदाज़ा लगाना पड़ता है। हफ्ते भर खुले PRs merge conflicts बनाते हैं और दूसरों को रोकते हैं। अच्छी PR आदतें bugs जल्दी पकड़ती हैं, knowledge फैलाती हैं और lead time छोटा रखती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Keep it small: one purpose, ideally < 400 changed lines.
Step 2 → Self-review the diff first; remove debug code and stray files.
Step 3 → Title in Conventional Commit style; description: what, why, how to test, screenshots, risks, linked issue.
Step 4 → Open as Draft if early; mark Ready when CI is green.
Step 5 → Request specific reviewers (CODEOWNERS adds them automatically).
Step 6 → Respond to every comment; push fixes as new commits, resolve threads.
Step 7 → Squash/merge when approved + checks pass; delete the branch.
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → छोटा रखो: एक उद्देश्य, बेहतर है < 400 changed lines।
Step 2 → पहले अपना diff खुद review करो; debug code और फालतू files हटाओ।
Step 3 → Title Conventional Commit style में; description में: क्या, क्यों, test कैसे करें, screenshots, risks, linked issue।
Step 4 → शुरुआती हो तो Draft खोलो; CI green होने पर Ready करो।
Step 5 → ख़ास reviewers माँगो (CODEOWNERS अपने-आप जोड़ता है)।
Step 6 → हर comment का जवाब दो; fixes नए commits में push करो, threads resolve करो।
Step 7 → Approval + checks pass होने पर squash/merge; branch delete।

---

## 🟡 Real World Example
Swiggy-style team: a dev changes delivery-fee calculation. PR title `fix(pricing): cap surge fee at 2x`, description links ticket PRC-88, explains the formula, includes test steps and a screenshot of the cart. CODEOWNERS auto-requests the pricing team. CI runs unit tests and a preview deploy. Two reviews later, it merges in 3 hours.

## 🟡 Real Example Hindi mein
Swiggy जैसी team: एक dev delivery-fee calculation बदलता है। PR title `fix(pricing): cap surge fee at 2x`, description में ticket PRC-88 का link, formula की व्याख्या, test steps और cart का screenshot। CODEOWNERS pricing team को अपने-आप request करता है। CI unit tests और preview deploy चलाती है। दो reviews के बाद 3 घंटे में merge।

---

## 💻 Code / Config Example — Basic

PR template (saved as `.github/pull_request_template.md`). Every field prompts the author.

```markdown
<!-- .github/pull_request_template.md : GitHub pre-fills new PR descriptions with this -->
## What
<!-- One or two sentences: what changed -->

## Why
<!-- Link the issue/ticket: Closes #123 -->

## How to test
<!-- Exact commands or steps a reviewer can follow -->
1.
2.

## Screenshots / logs
<!-- UI changes: before and after -->

## Checklist
- [ ] Tests added/updated
- [ ] No secrets or .env committed
- [ ] Docs/CHANGELOG updated if needed
- [ ] Backward compatible (or marked BREAKING)
```

## 💻 Code / Config Example — Advanced

CODEOWNERS, plus a workflow that checks PR size and runs tests. CODEOWNERS paths are examples.

```bash
# .github/CODEOWNERS - auto request reviews by path (last matching rule wins)
*                 @myorg/engineering        # default reviewers for everything
/api/             @myorg/backend            # Node.js API owners
/ml/              @myorg/ml-team            # FastAPI/ML owners
/web/             @myorg/frontend           # React owners
/infra/           @myorg/devops             # Docker, Nginx, workflows
/.github/         @myorg/devops             # CI changes need devops review
```

```yaml
# .github/workflows/pr-checks.yml
name: pr-checks                                        # workflow name
on:
  pull_request:                                        # on PR events
    branches: [main]                                   # targeting main
permissions:
  contents: read                                       # read-only token
  pull-requests: read                                  # allow reading PR file list
jobs:
  size:
    runs-on: ubuntu-latest                             # runner
    steps:
      - uses: actions/checkout@v4                      # fetch code (example version)
        with:
          fetch-depth: 0                               # need history to diff against base
      - name: Warn on large PR
        env:
          BASE: ${{ github.event.pull_request.base.sha }}   # base commit SHA (safe, not user text)
        run: |
          CHANGED=$(git diff --shortstat "$BASE"...HEAD | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' || echo 0)   # lines added
          echo "Lines added: $CHANGED"                 # show number in logs
          if [ "$CHANGED" -gt 800 ]; then              # soft limit of 800 additions
            echo "::warning::PR is large ($CHANGED lines). Consider splitting it."   # annotation, not failure
          fi
  test:
    runs-on: ubuntu-latest                             # runner
    steps:
      - uses: actions/checkout@v4                      # fetch code
      - uses: actions/setup-node@v4                    # Node setup
        with:
          node-version: 20                             # version
          cache: npm                                   # cache
      - run: npm ci && npm test                        # install and test
```

---

## 🟠 My Stack Integration
- **Required checks on main:** `test`, `lint`, `docker build` must pass before merge.
- **Preview deploys:** build the PR image, run on the VPS under `pr-<number>.preview.example.com` via Nginx wildcard; delete when the PR closes.
- **Monorepo:** CODEOWNERS per folder (api/ml/web/infra) gives the right reviewer automatically.
- **Squash merge** + Conventional Commit PR titles = clean `main` history and automatic changelogs.

```yaml
# Docker build check on PRs (does not push, only verifies the image builds)
jobs:
  docker-build:
    runs-on: ubuntu-latest                              # runner
    steps:
      - uses: actions/checkout@v4                       # fetch code
      - uses: docker/build-push-action@v6               # example version
        with:
          context: .                                    # build context
          push: false                                   # never push from PRs
          tags: myorg/api:pr-test                       # throwaway local tag
```

**Security:** for PRs from forks, secrets are not exposed to `pull_request` workflows (good). Never use `pull_request_target` with a checkout of untrusted PR code; it runs with secrets and write token. Run secret scanning, Dependabot and CodeQL on PRs.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Giant PRs mixing refactor + feature + formatting.
✅ Correct: Separate PRs, or at least separate commits.

❌ Mistake 2: Empty descriptions.
✅ Correct: Use a template: what, why, how to test.

❌ Mistake 3: Force-pushing after reviews started, losing comment context.
✅ Correct: Push new commits; squash at merge.

❌ Mistake 4: Merging with failing/skipped checks "just this once".
✅ Correct: Required status checks and no admin bypass.

---

## 🧠 Tricky Interview Question
A PR from a fork needs a deploy secret to run integration tests. How do you do it safely?

**Answer:** Do not expose secrets to fork PR code. Options: run secret-needing tests only after a maintainer reviews and merges (or labels it, with a separate workflow using `workflow_run`/environment approval), use mocks or ephemeral test services in the PR workflow, and never check out and execute untrusted code inside `pull_request_target`.

---

## ⚫ Interview Questions + Answers

Q1: Ideal PR size?
A1: Small, single-purpose, commonly under ~400 lines so it can be reviewed in under an hour.

Q2: Merge, squash or rebase merge?
A2: Squash for clean history per PR; rebase for linear history of well-crafted commits; merge commit to preserve everything.

Q3: What is a Draft PR?
A3: A PR marked not ready; it cannot be merged and signals early feedback is welcome.

Q4: What is CODEOWNERS?
A4: A file mapping paths to users/teams who are auto-requested (and can be required) as reviewers.

Q5: How do you keep a PR updated with main?
A5: Merge or rebase `main` into the branch, re-run CI.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any change to a shared branch.

❌ Avoid when:
- Trivial emergency fixes may use an expedited, but still reviewed, hotfix PR; direct pushes to main should stay disabled.

---

## 📊 Visual Diagram

```
 branch --push--> [Open PR] --> CI (test/lint/build) --+
                      |                                |
                 reviewers (CODEOWNERS)                v
                      |                         all checks green?
                      +-- comments/fixes <-----------+ no
                                                       | yes
                                                  approvals ok? --> squash merge --> deploy
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pull Request | Merge proposal | merge का प्रस्ताव |
| Draft PR | Not yet ready PR | अभी तैयार नहीं PR |
| CODEOWNERS | File that assigns reviewers | reviewers तय करने वाली file |
| Status check | Required CI result | ज़रूरी CI नतीजा |
| Squash merge | Combine commits on merge | merge पर commits जोड़ना |

---

## ⚡ 3-Line Summary
English: Keep PRs small, described, tested and reviewed fast.
Use templates, CODEOWNERS and required checks.
Never run untrusted PR code with secrets.
Hindi: PRs छोटे, described, tested रखो और जल्दी review करो।
Templates, CODEOWNERS और required checks use करो।
Untrusted PR code को secrets के साथ कभी मत चलाओ।

---

## ➡️ Next Topic
**26. Code Review Process** - how reviewers and authors should work on a PR.

---
