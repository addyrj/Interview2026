# 317. SAST Scanning (CodeQL)
# हिंदी में: SAST Scanning (CodeQL)

---

## 🔵 Simple Definition (English)
SAST (Static Application Security Testing) analyses your own source code for security flaws without running it. CodeQL is GitHub's SAST engine: it turns code into a queryable database and runs security queries (SQL injection, XSS, path traversal, hard-coded credentials). Results appear in the repository's Security tab and on PRs.

## 🔵 सरल परिभाषा (Hindi)
SAST (Static Application Security Testing) आपके अपने source code को बिना चलाए security flaws के लिए जाँचता है। CodeQL GitHub का SAST engine है: यह code को query-योग्य database में बदलता है और security queries (SQL injection, XSS, path traversal, hard-coded credentials) चलाता है। नतीजे repository के Security tab और PRs पर दिखते हैं।

---

## 🔴 Problem it Solves
Dependency scanners only find bugs in other people's code. Vulnerabilities you write yourself, such as `res.send(req.query.name)` (XSS) or `db.query("..." + id)` (injection), are invisible to them. CodeQL traces data from untrusted sources (request params) to dangerous sinks (SQL, shell, HTML) and flags the flow.

## 🔴 यह क्यों बना? (Hindi)
Dependency scanners सिर्फ़ दूसरों के code के bugs ढूँढते हैं। जो vulnerabilities आप खुद लिखते हैं, जैसे `res.send(req.query.name)` (XSS) या `db.query("..." + id)` (injection), वे उन्हें दिखती ही नहीं। CodeQL untrusted sources (request params) से खतरनाक sinks (SQL, shell, HTML) तक data का रास्ता trace करके उसे flag करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Workflow runs on push/PR and on a weekly schedule
Step 2 → github/codeql-action/init picks languages (javascript-typescript, python)
Step 3 → For interpreted languages it extracts source directly (no build needed)
Step 4 → Code becomes a relational CodeQL database
Step 5 → analyze runs the query suite (default, or security-extended)
Step 6 → Data-flow queries track source → sink paths
Step 7 → Results are uploaded as SARIF to Code Scanning
Step 8 → Alerts show in Security tab; PR gets annotations on changed lines
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Workflow push/PR पर और साप्ताहिक schedule पर चलता है
Step 2 → github/codeql-action/init भाषाएँ चुनता है (javascript-typescript, python)
Step 3 → Interpreted languages के लिए source सीधे extract होता है (build नहीं चाहिए)
Step 4 → Code एक relational CodeQL database बन जाता है
Step 5 → analyze query suite चलाता है (default, या security-extended)
Step 6 → Data-flow queries source → sink रास्ते trace करती हैं
Step 7 → नतीजे SARIF के रूप में Code Scanning में upload होते हैं
Step 8 → Alerts Security tab में दिखते हैं; PR की बदली lines पर annotations आते हैं
```

---

## 🟡 Real World Example
Your Express route does `const file = path.join('/uploads', req.params.name); res.sendFile(file)`. CodeQL reports "Uncontrolled data used in path expression" (path traversal: `../../etc/passwd`). The PR shows an annotation on that exact line. The fix is `path.basename()` plus a check that the resolved path starts with the uploads directory.

## 🟡 Real Example Hindi mein
आपका Express route `const file = path.join('/uploads', req.params.name); res.sendFile(file)` करता है। CodeQL बताता है "Uncontrolled data used in path expression" (path traversal: `../../etc/passwd`)। PR में उसी line पर annotation दिखता है। Fix है `path.basename()` और जाँच कि resolved path uploads directory से शुरू होता है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/codeql.yml  (basic, JavaScript only)
name: CodeQL                           # Workflow name

on:
  pull_request:                        # Scan PRs
  push:
    branches: [main]                   # Scan main

jobs:
  analyze:
    runs-on: ubuntu-latest             # Runner
    permissions:
      contents: read                   # Read code
      security-events: write           # Upload results to Code Scanning
    steps:
      - uses: actions/checkout@v4      # Get code
      - uses: github/codeql-action/init@v3      # Prepare CodeQL
        with:
          languages: javascript-typescript      # Language to analyse
      - uses: github/codeql-action/analyze@v3   # Run queries and upload SARIF
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/codeql.yml  (JS/TS + Python matrix, extended queries, schedule, config file)
name: CodeQL

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: "17 4 * * 3"               # Wednesdays 04:17 UTC; new queries run on old code

concurrency:
  group: codeql-${{ github.ref }}
  cancel-in-progress: true

jobs:
  analyze:
    name: Analyze (${{ matrix.language }})   # Check name per language
    runs-on: ubuntu-latest
    timeout-minutes: 30
    permissions:
      contents: read
      security-events: write           # Required to publish alerts
      actions: read                    # Needed in private repos for workflow run info
    strategy:
      fail-fast: false                 # One language failing must not hide the other
      matrix:
        language: [javascript-typescript, python]   # Node/React + FastAPI
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
          queries: security-extended   # More security queries than default (more findings)
          config-file: ./.github/codeql/codeql-config.yml   # Path filters
      - uses: github/codeql-action/analyze@v3
        with:
          category: "/language:${{ matrix.language }}"      # Separate result streams
```

`.github/codeql/codeql-config.yml`:
```yaml
# .github/codeql/codeql-config.yml
name: "Custom CodeQL config"           # Display name
paths-ignore:                          # Do not analyse these paths
  - "**/node_modules/**"               # Third-party code
  - "**/dist/**"                       # Build output
  - "**/tests/**"                      # Test code (reduces noise)
  - "**/migrations/**"                 # Generated migrations
```

---

## 🟠 My Stack Integration
- **Node.js/Express/NestJS:** Detects SQL/NoSQL injection, XSS via `res.send`, prototype pollution, ReDoS, insecure randomness, missing rate limits, hard-coded secrets.
- **FastAPI:** Detects SQL injection with raw queries, SSRF with `requests.get(user_url)`, command injection with `subprocess(shell=True)`, unsafe `yaml.load`.
- **React/Next.js:** DOM XSS via `dangerouslySetInnerHTML`, open redirects.
- **Required check:** After the first run, add "CodeQL" / "Analyze (...)" as a required status check (topic 322).
- **Cost:** CodeQL is free for public repos; private repos need GitHub Advanced Security (Code Security).
- **VPS/Nginx:** CodeQL does not scan Nginx config; use separate linting for those.

```yaml
# Gate deploys on the security scan finishing in the same workflow file
jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions: { contents: read, security-events: write }
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with: { languages: javascript-typescript }
      - uses: github/codeql-action/analyze@v3
  deploy:
    needs: [analyze]                   # Deploy only after analysis completes
    runs-on: ubuntu-latest
    steps:
      - run: echo "deploy to VPS"      # Placeholder
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Missing `security-events: write`, so upload fails with "Resource not accessible".
✅ Correct: Add the permission on the job.

❌ Mistake 2: Analysing `node_modules` and tests, creating huge noise and slow runs.
✅ Correct: Use `paths-ignore` in the config file.

❌ Mistake 3: Dismissing alerts without reading data flow.
✅ Correct: Review the path; dismiss with a reason only if truly a false positive.

❌ Mistake 4: Running only on PRs.
✅ Correct: Also scan `main` and weekly, because query packs update.

❌ Mistake 5: Using `autobuild` for JS/Python out of habit.
✅ Correct: Not needed for interpreted languages; only compiled ones (Java, C++, Go) need builds.

---

## 🧠 Tricky Interview Question
CodeQL did not flag your SQL injection even though `db.query("SELECT ... " + id)` is obviously unsafe. Why might it miss it?

Answer: SAST depends on recognised sources and sinks. If you use a custom wrapper `runSql(q)` that CodeQL's library does not model, or the data passes through an unmodelled function or dynamic property access, taint tracking breaks (a false negative). Also the code may be in an ignored path, a language not enabled, or generated at runtime. Mitigate with `security-extended` queries, custom models/queries, code review, parameterised queries as policy, and complementary DAST/penetration tests. SAST is not a guarantee.

---

## ⚫ Interview Questions + Answers

Q1: SAST vs DAST vs SCA?
A1: SAST scans source statically; DAST attacks a running app from outside; SCA (Snyk, npm audit) scans third-party dependencies.

Q2: What is SARIF?
A2: Static Analysis Results Interchange Format, a JSON standard that GitHub Code Scanning ingests from many tools.

Q3: Why `fail-fast: false` in the matrix?
A3: So a failure in one language does not cancel the other analysis.

Q4: How do alerts block merges?
A4: Make the analysis a required status check and set a Code Scanning "merge protection" ruleset for severity levels, so high alerts block PRs.

Q5: How do you reduce false positives?
A5: Exclude generated paths, tune query suites, dismiss with documented reason, write custom sanitiser models.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You write backend code handling user input (APIs, auth, uploads).
- Compliance asks for SAST evidence.
- You want PR annotations on risky lines.

❌ Avoid when:
- Private repo without Advanced Security license (use free alternatives like Semgrep).
- You expect it to catch business-logic flaws (it cannot).
- As a replacement for secure coding review.

---

## 📊 Visual Diagram
```
 push / PR / weekly cron
        │
        ▼
 codeql-action/init  ──▶ extract source ──▶ CodeQL database
                                                  │
                         queries (default / security-extended)
                                                  ▼
   untrusted SOURCE ──▶ ... data flow ... ──▶ dangerous SINK
   (req.query.id)                             (db.query / res.send)
                                                  │
                                                  ▼
                                   SARIF ──▶ Security tab alerts
                                                  │
                                       PR annotation on the line
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SAST | Static code security analysis | static code security जाँच |
| CodeQL | GitHub's query-based analysis engine | GitHub का query-आधारित analysis engine |
| Source / Sink | Where tainted data enters / is dangerous | दूषित data कहाँ आता है / कहाँ खतरनाक |
| Taint tracking | Following untrusted data through code | untrusted data का पीछा करना |
| SARIF | Result exchange JSON format | नतीजों का JSON format |
| False negative | Real issue not detected | असली समस्या जो पकड़ी नहीं गई |

---

## ⚡ 3-Line Summary
English: CodeQL builds a database of your code and runs security queries via data-flow analysis.
English: Give the job `security-events: write`, scan each language, ignore noisy paths.
English: Run on PRs, main and weekly; make it a required check; it complements, not replaces, review.
Hindi: CodeQL आपके code का database बनाकर data-flow analysis से security queries चलाता है।
Hindi: Job को `security-events: write` दें, हर भाषा scan करें, शोर वाले paths ignore करें।
Hindi: PR, main और साप्ताहिक चलाएँ; इसे required check बनाएँ; यह review का विकल्प नहीं, पूरक है।

Note: workflow and config YAML parsed locally; action versions are examples; not run on GitHub.

---

## ➡️ Next Topic
318. Docker Image Build in CI: code is verified; now we build the container image with caching and tags.
