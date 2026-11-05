# 26. Code Review Process
# हिंदी में: Code Review Process

---

## 🔵 Simple Definition (English)
**Code review** is the practice where one or more teammates examine a change before it is merged, to catch bugs, security issues and design problems, share knowledge and keep the code consistent. On GitHub it happens inside Pull Requests with comments, suggestions and approvals.

## 🔵 सरल परिभाषा (Hindi)
**Code review** वह practice है जिसमें merge से पहले एक या ज़्यादा teammates change को जाँचते हैं, ताकि bugs, security issues और design problems पकड़े जाएँ, knowledge share हो और code consistent रहे। GitHub पर यह Pull Requests में comments, suggestions और approvals के ज़रिए होता है।

---

## 🔴 Problem it Solves
Single-person code goes to production with hidden bugs, hard-coded secrets, SQL injection or performance traps. Knowledge stays in one head ("bus factor 1"). Reviews done badly (nit-picking, personal tone, week-long delays) hurt morale and speed. A defined process makes review fast, kind and effective, with machines handling style so humans focus on logic.

## 🔴 यह क्यों बना? (Hindi)
अकेले व्यक्ति का code छुपे bugs, hard-coded secrets, SQL injection या performance traps के साथ production पहुँच जाता है। Knowledge एक ही सिर में रहती है ("bus factor 1")। बुरी तरह किए गए reviews (छोटी-छोटी बातों पर अटकना, personal tone, हफ्ते भर की देरी) morale और speed बिगाड़ते हैं। तय process review को तेज़, विनम्र और असरदार बनाता है, जहाँ style मशीनें देखती हैं और इंसान logic पर ध्यान देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Author self-reviews, CI is green, PR has description + test steps.
Step 2 → Reviewer is assigned (CODEOWNERS / rotation); target first response < 1 working day.
Step 3 → Reviewer reads context first (issue, description), then the diff.
Step 4 → Checklist: correctness, tests, security, performance, readability, error handling, backward compatibility.
Step 5 → Comments are labeled: blocking vs nit vs question vs suggestion.
Step 6 → Author replies/fixes; reviewer re-checks only changed parts.
Step 7 → Approve (or request changes) -> merge when required checks pass.
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Author खुद review करता है, CI green, PR में description + test steps।
Step 2 → Reviewer assign (CODEOWNERS / rotation); पहला जवाब < 1 working day।
Step 3 → Reviewer पहले context (issue, description) पढ़ता है, फिर diff।
Step 4 → Checklist: correctness, tests, security, performance, readability, error handling, backward compatibility।
Step 5 → Comments label करो: blocking, nit, question, suggestion।
Step 6 → Author जवाब/fix देता है; reviewer सिर्फ बदले हिस्से दोबारा देखता है।
Step 7 → Approve (या request changes) -> required checks पास होने पर merge।

---

## 🟡 Real World Example
A developer adds a "download invoice" endpoint to the Node.js API. The reviewer notices the file path is built from user input (`../` path traversal) and no auth check exists. A blocking comment with a suggested fix prevents a data breach. A second, labelled `nit:` comment about variable naming is optional. The author fixes the blocking issue, CI passes, and the PR merges the same day.

## 🟡 Real Example Hindi mein
एक developer Node.js API में "download invoice" endpoint जोड़ता है। Reviewer देखता है कि file path user input से बन रहा है (`../` path traversal) और auth check नहीं है। Suggested fix के साथ blocking comment data breach रोक देता है। Variable naming पर `nit:` वाला दूसरा comment optional है। Author blocking issue ठीक करता है, CI पास, और उसी दिन merge।

---

## 💻 Code / Config Example — Basic

Review from the terminal with `gh` (needs `gh auth login`; replace the PR number).

```bash
#!/usr/bin/env bash
# review-basic.sh - review a PR locally
set -euo pipefail                                          # strict mode

PR="${1:?usage: review-basic.sh PR_NUMBER}"                # PR number required
gh pr view "$PR"                                           # read description, status and checks summary
gh pr checks "$PR"                                         # see CI results
gh pr checkout "$PR"                                       # fetch the PR branch locally so you can run it
npm ci && npm test                                         # run the code yourself (use your stack's commands)
gh pr diff "$PR"                                           # read the diff in the terminal
gh pr review "$PR" --comment --body "nit: rename tmp to invoicePath"        # non-blocking comment
# gh pr review "$PR" --request-changes --body "blocking: validate invoiceId"   # block merge with reason
# gh pr review "$PR" --approve --body "LGTM, tests cover the edge cases"       # approve
```

## 💻 Code / Config Example — Advanced

Automate the boring parts so humans review logic: lint, tests, dependency review and security scan on every PR. Action versions are examples.

```yaml
# .github/workflows/review-automation.yml
name: review-automation                                  # workflow name
on:
  pull_request:                                          # run on PRs
    branches: [main]
permissions:
  contents: read                                         # read code
  security-events: write                                 # CodeQL uploads results
  pull-requests: read                                    # dependency review reads PR info
jobs:
  lint-test:
    runs-on: ubuntu-latest                               # runner
    steps:
      - uses: actions/checkout@v4                        # fetch code
      - uses: actions/setup-node@v4                      # Node setup
        with:
          node-version: 20                               # version
          cache: npm                                     # cache
      - run: npm ci                                      # install
      - run: npm run lint --if-present                   # style rules (machines enforce style)
      - run: npm test                                    # tests
  dependency-review:
    runs-on: ubuntu-latest                               # runner
    steps:
      - uses: actions/checkout@v4                        # fetch code
      - uses: actions/dependency-review-action@v4        # blocks PRs adding known-vulnerable deps
        with:
          fail-on-severity: high                         # fail on high or critical advisories
  codeql:
    runs-on: ubuntu-latest                               # runner
    steps:
      - uses: actions/checkout@v4                        # fetch code
      - uses: github/codeql-action/init@v3               # initialise CodeQL
        with:
          languages: javascript-typescript               # scan Node/React code
      - uses: github/codeql-action/analyze@v3            # run analysis and upload alerts
```

---

## 🟠 My Stack Integration
- **Node.js review checklist:** input validation, auth on every route, no `eval`, parameterised DB queries, async errors handled, no secrets in code.
- **FastAPI:** Pydantic models validate input, dependencies enforce auth, no blocking calls in async routes.
- **React:** no `dangerouslySetInnerHTML` with user data, no tokens in localStorage if avoidable, bundle size check.
- **Nginx/Docker infra:** review headers, `proxy_pass`, exposed ports, base image tags, non-root user, `.dockerignore`.

```yaml
# Branch protection expressed as a GitHub Ruleset import (JSON-like intent, shown as YAML for readability)
# Configure in: Settings > Rules > Rulesets (UI/API format differs; this lists the intent)
target: branch                         # applies to branches
include: ["refs/heads/main"]           # protect main
rules:
  pull_request:
    required_approving_review_count: 1 # at least one approval
    require_code_owner_review: true    # CODEOWNERS must approve
    dismiss_stale_reviews_on_push: true  # new commits need re-approval
  required_status_checks: [lint-test, dependency-review]   # CI must pass
  non_fast_forward: true               # block force-push
  deletion: true                       # block branch deletion
```
(Illustrative intent only, not a literal API payload.)

**Security:** reviewers are a security control; require CODEOWNER review for `/.github/`, `/infra/` and auth code. Keep authors from approving their own PR. Watch for leaked secrets, over-broad permissions, and newly added dependencies.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Rubber-stamping with "LGTM" without running or reading.
✅ Correct: Check tests, edge cases, security; run it if risky.

❌ Mistake 2: Arguing style by hand.
✅ Correct: Automate with linters/formatters (Prettier, ESLint, Black).

❌ Mistake 3: Harsh or personal comments ("this is stupid").
✅ Correct: Critique the code, ask questions, offer suggestions.

❌ Mistake 4: Letting reviews wait days.
✅ Correct: Agree a response-time target; small PRs help.

---

## 🧠 Tricky Interview Question
CI is green and two people approved, yet the change causes a production outage. Does that mean review failed?

**Answer:** Not necessarily; review reduces risk but cannot prove correctness. Add safety nets beyond review: integration tests, canary/blue-green deploys, feature flags, monitoring and fast rollback. In the post-mortem, ask what check would have caught it and add that to the checklist or pipeline, without blaming the reviewers.

---

## ⚫ Interview Questions + Answers

Q1: What should a reviewer look for?
A1: Correctness, tests, security, performance, readability, maintainability, compatibility and operational impact (logging, config, migrations).

Q2: What do `blocking`, `nit`, `suggestion` mean?
A2: Blocking must be fixed before merge; nit is a minor optional point; suggestion proposes an alternative (GitHub can apply it with one click).

Q3: How do you review a large PR?
A3: Ask to split it; otherwise review commit by commit, start from tests and the main logic.

Q4: How do you handle disagreement?
A4: Discuss with data, pull in a third reviewer or tech lead, document the decision.

Q5: Pair programming vs code review?
A5: Pairing gives real-time review; teams often still keep a lightweight PR for traceability and CI.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every change to shared/production code, especially security, payments, infra.

❌ Avoid when:
- Review becomes a bottleneck for trivial typo fixes: allow auto-merge for docs-only/bot dependency PRs after checks.

---

## 📊 Visual Diagram

```
 Author                 Machines                  Reviewer
   |  open PR --------> lint/test/scan  ------>     |
   |                       (green?)                 |
   |                                    read context + diff
   | <--- comments (blocking / nit / question) ---- |
   |  fix + push ------------------------------->   |
   |                                       approve  |
   +------------- required checks + approval --> MERGE --> deploy
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Code review | Peer check before merge | merge से पहले साथियों की जाँच |
| LGTM | "Looks good to me" | "मुझे ठीक लग रहा है" |
| Nit | Minor optional comment | छोटी optional टिप्पणी |
| Request changes | Block until fixed | ठीक होने तक रोकना |
| Bus factor | People who hold key knowledge | key knowledge वाले लोगों की संख्या |
| Linter | Automated style/bug checker | style/bug जाँचने वाला tool |

---

## ⚡ 3-Line Summary
English: Code review is a peer check that catches bugs and spreads knowledge.
Let tools handle style; humans focus on logic, security and design.
Be fast, specific and kind, and keep branch protection on.
Hindi: Code review साथियों की जाँच है जो bugs पकड़ती और knowledge फैलाती है।
Style tools देखें; इंसान logic, security और design पर ध्यान दें।
तेज़, specific और विनम्र रहो, और branch protection चालू रखो।

---

## ➡️ Next Topic
**27. Branch Protection Rules** (next in the Git/GitHub section) - enforcing reviews and checks automatically.

---
