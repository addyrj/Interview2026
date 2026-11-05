# 320. PR Comments with Results
# हिंदी में: PR में Results के Comments

---

## 🔵 Simple Definition (English)
A PR comment bot is a workflow step that posts (or updates) a comment on the pull request with CI results: test summary, coverage change, scan findings, preview URL. It uses the GitHub API through `actions/github-script` or a ready-made action, authenticated with `GITHUB_TOKEN` and `pull-requests: write`.

## 🔵 सरल परिभाषा (Hindi)
PR comment bot workflow का एक step है जो pull request पर CI results (test summary, coverage बदलाव, scan findings, preview URL) का comment post या update करता है। यह `actions/github-script` या तैयार action से GitHub API इस्तेमाल करता है, `GITHUB_TOKEN` और `pull-requests: write` permission के साथ।

---

## 🔴 Problem it Solves
Reviewers should not open five tabs and scroll through 3000 log lines to learn that coverage fell 4%. Failure reasons buried in logs get ignored. A single clear comment on the PR puts the important numbers where the discussion happens.

## 🔴 यह क्यों बना? (Hindi)
Reviewers को यह जानने के लिए पाँच tabs खोलने और 3000 log lines पढ़ने की ज़रूरत नहीं होनी चाहिए कि coverage 4% गिरा। Logs में दबे failure कारण अनदेखे रह जाते हैं। PR पर एक साफ़ comment ज़रूरी संख्याएँ वहीं रखता है जहाँ चर्चा होती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Workflow triggers on pull_request
Step 2 → Earlier steps produce results (junit, coverage-summary.json, trivy output)
Step 3 → A step builds a markdown body (table, emojis, links)
Step 4 → Job has permissions: pull-requests: write (GITHUB_TOKEN)
Step 5 → github-script lists existing comments and looks for a hidden marker
Step 6 → Marker found → update that comment; not found → create a new one
Step 7 → Comment appears in the PR; next push edits it (no spam)
Step 8 → Same data is also written to $GITHUB_STEP_SUMMARY as a fallback
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Workflow pull_request पर trigger होता है
Step 2 → पहले के steps results बनाते हैं (junit, coverage-summary.json, trivy output)
Step 3 → एक step markdown body बनाता है (table, emojis, links)
Step 4 → Job में permissions: pull-requests: write है (GITHUB_TOKEN)
Step 5 → github-script मौजूदा comments देखकर छिपा marker खोजता है
Step 6 → Marker मिला → वही comment update; नहीं मिला → नया comment
Step 7 → PR में comment दिखता है; अगला push उसे edit करता है (spam नहीं)
Step 8 → वही data fallback के तौर पर $GITHUB_STEP_SUMMARY में भी लिखा जाता है
```

---

## 🟡 Real World Example
Each PR to your FastAPI repo gets one comment: "Tests: 212 passed, 0 failed. Coverage: 84.2% (-0.3%). Trivy: 0 critical, 2 high. Preview: https://pr-57.staging.example.com". Pushing 10 more commits only updates this single comment. The reviewer decides in seconds whether the PR is healthy.

## 🟡 Real Example Hindi mein
आपके FastAPI repo के हर PR पर एक comment आता है: "Tests: 212 passed, 0 failed. Coverage: 84.2% (-0.3%). Trivy: 0 critical, 2 high. Preview: https://pr-57.staging.example.com"। 10 और commits push करने पर भी यही एक comment update होता है। Reviewer सेकंडों में तय कर लेता है कि PR ठीक है या नहीं।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/pr-comment.yml  (basic: post one comment)
name: PR Comment                       # Workflow name

on: [pull_request]                     # Only for PRs

permissions:
  pull-requests: write                 # Allow creating/updating PR comments
  contents: read                       # Allow checkout

jobs:
  comment:
    runs-on: ubuntu-latest             # Runner
    steps:
      - uses: actions/github-script@v7 # Run JS with an authenticated Octokit client
        with:
          script: |
            // Create an issue comment (PRs are issues in the API)
            await github.rest.issues.createComment({
              owner: context.repo.owner,      // Repository owner
              repo: context.repo.repo,        // Repository name
              issue_number: context.issue.number,   // PR number
              body: 'CI finished for ' + context.sha.slice(0, 7),   // Comment text
            });
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/pr-comment.yml  (tests + coverage summary, update-in-place sticky comment)
name: CI with PR Report

on:
  pull_request:

permissions:
  contents: read
  pull-requests: write                 # Needed for comments on same-repo PRs

jobs:
  test-and-report:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: backend/package-lock.json
      - run: npm ci
      - name: Run tests with coverage
        id: tests
        continue-on-error: true        # Allow the report step to run, gate at the end
        run: npx jest --ci --coverage --coverageReporters=json-summary
      - name: Build markdown report
        if: always()
        id: report
        run: |
          # Read total line coverage with node (jq also works)
          PCT=$(node -p "require('./coverage/coverage-summary.json').total.lines.pct")
          STATUS="${{ steps.tests.outcome }}"          # success or failure
          {
            echo "<!-- ci-report -->"                  # Hidden marker to find this comment later
            echo "### CI report for \`${GITHUB_SHA::7}\`"
            echo ""
            echo "| Check | Result |"
            echo "|-------|--------|"
            echo "| Unit tests | ${STATUS} |"
            echo "| Line coverage | ${PCT}% |"
            echo ""
            echo "[Full run](${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID})"
          } > report.md
          cat report.md >> "$GITHUB_STEP_SUMMARY"      # Also show on the run page
      - name: Create or update PR comment
        if: always() && github.event.pull_request.head.repo.full_name == github.repository   # Skip forks (read-only token)
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');                                  // Node file API
            const body = fs.readFileSync('backend/report.md', 'utf8'); // Our markdown
            const { owner, repo } = context.repo;                      // Repo coordinates
            const issue_number = context.issue.number;                 // PR number
            const comments = await github.paginate(                    // Handle >30 comments
              github.rest.issues.listComments, { owner, repo, issue_number });
            const existing = comments.find(c => c.body && c.body.includes('<!-- ci-report -->'));
            if (existing) {                                            // Update, do not spam
              await github.rest.issues.updateComment({ owner, repo, comment_id: existing.id, body });
            } else {                                                   // First time: create
              await github.rest.issues.createComment({ owner, repo, issue_number, body });
            }
      - name: Fail job if tests failed   # Gate after reporting
        if: steps.tests.outcome == 'failure'
        run: exit 1
```

The same sticky behaviour with a ready-made action (alternative to writing JS):
```yaml
      - uses: marocchino/sticky-pull-request-comment@v2   # Third-party; pin to SHA in production
        with:
          header: ci-report            # Identifies the comment to update
          path: backend/report.md      # Markdown file to post
```

---

## 🟠 My Stack Integration
- **Node.js:** Parse `coverage-summary.json` or jest-junit XML into a table.
- **FastAPI:** `pytest --junitxml` + `coverage xml`; a small Python/`jq` step builds the markdown.
- **React/Next.js preview:** Deploy a preview to a VPS path or Vercel-like URL and comment the link.
- **Terraform/AWS plans:** Same pattern posts `terraform plan` output in a collapsible `<details>` block.
- **Security:** Comments are public to anyone who can see the PR. Never include secrets, tokens, internal IPs or full stack traces. Escape untrusted text (PR titles, branch names) to avoid markdown/script injection.

```yaml
# Collapsible long output inside a comment body (GitHub renders <details>)
# <details><summary>Trivy findings (click)</summary>
#
# CVE-... HIGH libexpat1 ... (put the long output here, inside a code fence)
#
# </details>
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Missing `pull-requests: write`, giving "Resource not accessible by integration".
✅ Correct: Add the permission at workflow or job level.

❌ Mistake 2: Creating a new comment on every push, so PRs get 40 bot comments.
✅ Correct: Find by hidden marker and update.

❌ Mistake 3: Using `pull_request_target` to get write access on fork PRs and checking out fork code.
✅ Correct: Keep `pull_request`; for fork reporting use a separate `workflow_run` workflow that only reads artifacts, never runs fork code with secrets.

❌ Mistake 4: Interpolating `${{ github.event.pull_request.title }}` directly into `run:`, allowing script injection.
✅ Correct: Pass untrusted values via `env:` and quote them in the shell.

❌ Mistake 5: Post only on success, so failures stay invisible.
✅ Correct: `if: always()` on the report step.

---

## 🧠 Tricky Interview Question
The comment step works for your team's PRs but fails with 403 on PRs from external contributors' forks. Why, and how do you safely fix it?

Answer: For `pull_request` events from forks, GitHub gives `GITHUB_TOKEN` read-only permissions and withholds secrets. Switching to `pull_request_target` gives a write token but runs in the base repo context, so checking out and executing the fork's code would let an attacker steal secrets. Safe pattern: the untrusted `pull_request` workflow only produces an artifact (the markdown). A second workflow on `workflow_run` (trusted, base-branch code) downloads that artifact as data and posts the comment, never executing it.

---

## ⚫ Interview Questions + Answers

Q1: Why is it `issues.createComment` for a PR?
A1: In GitHub's API, PR conversation comments are issue comments; review comments on diff lines use `pulls.createReviewComment`.

Q2: What is `$GITHUB_STEP_SUMMARY`?
A2: A file whose markdown content is rendered on the workflow run summary page. No special permissions needed, works for forks too.

Q3: How do you avoid duplicate comments?
A3: Add a hidden HTML comment marker, list comments, update the one containing it.

Q4: Where does `GITHUB_TOKEN` get its power?
A4: From the `permissions:` block; default can be read-only depending on org settings, so declare what you need explicitly.

Q5: Review comment vs issue comment?
A5: Issue comment is general conversation; review comment attaches to a line/file in the diff (used by linters, SARIF annotations).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Reviewers need coverage/test/scan summaries quickly.
- You post preview URLs or `terraform plan` output.
- You want one updating comment per PR.

❌ Avoid when:
- Output is huge; link to artifacts instead.
- Data is sensitive; the comment is visible to all readers.
- Fork PR automation without the safe `workflow_run` pattern.

---

## 📊 Visual Diagram
```
  PR push ──▶ Workflow
                 │
   tests ─┐      │
 coverage ─┼──▶ report.md  (with <!-- ci-report --> marker)
  scans  ─┘      │
                 ▼
        github-script (GITHUB_TOKEN, pull-requests: write)
                 │
        list comments ── marker found? ──┐
                 │ no                    │ yes
                 ▼                       ▼
          createComment            updateComment
                 └───────────┬───────────┘
                             ▼
                  💬 one tidy comment on the PR
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| GITHUB_TOKEN | Auto-generated per-run API token | हर run का स्वतः बना API token |
| github-script | Action to run JS against GitHub API | GitHub API पर JS चलाने वाली action |
| Sticky comment | Comment updated in place | जगह पर ही update होने वाला comment |
| Marker | Hidden text used to find a comment | comment खोजने का छिपा text |
| Step summary | Markdown shown on run page | run page पर दिखने वाला markdown |
| workflow_run | Trigger after another workflow ends | दूसरे workflow के बाद चलने वाला trigger |

---

## ⚡ 3-Line Summary
English: A PR comment step posts CI results where reviewers already look.
English: Use `pull-requests: write`, a hidden marker and update-in-place to avoid spam.
English: Handle fork PRs with the safe `workflow_run` pattern and never leak secrets.
Hindi: PR comment step CI results वहीं रखता है जहाँ reviewers पहले से देखते हैं।
Hindi: `pull-requests: write`, छिपा marker और update-in-place से spam रोकें।
Hindi: Fork PRs के लिए सुरक्षित `workflow_run` pattern अपनाएँ और secrets कभी leak न करें।

Note: YAML parsed and embedded JS not executed on GitHub; action versions are examples.

---

## ➡️ Next Topic
321. Status Checks for PR: how each job becomes a pass/fail check on the pull request.
