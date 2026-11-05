---

# 34. CODEOWNERS File
# हिंदी में: CODEOWNERS File (फ़ाइलों के मालिक)

---

## 🔵 Simple Definition (English)
A **CODEOWNERS** file maps file paths to the people or teams responsible for them. When a pull request changes those files, GitHub automatically requests a review from the owners, and branch protection can make their approval mandatory.

## 🔵 सरल परिभाषा (Hindi)
**CODEOWNERS** file file-paths को उनके ज़िम्मेदार लोगों या teams से जोड़ती है। जब PR उन files को बदलता है तो GitHub अपने-आप owners से review माँगता है, और branch protection उनका approval अनिवार्य बना सकता है।

---

## 🔴 Problem it Solves
In a growing repo nobody knows who should review the nginx config or the payment module. Reviews go to random people, risky files (`.github/workflows`, `infra/`, `Dockerfile`) get merged by someone who does not understand them, and important reviewers are missed. CODEOWNERS makes ownership explicit and automatic.

## 🔴 यह क्यों बना? (Hindi)
बढ़ती repo में किसी को नहीं पता कि nginx config या payment module कौन review करे। Reviews random लोगों के पास जाते हैं, जोखिम वाली files (`.github/workflows`, `infra/`, `Dockerfile`) ऐसे लोग merge कर देते हैं जो उन्हें समझते नहीं, और ज़रूरी reviewers छूट जाते हैं। CODEOWNERS ownership को साफ़ और स्वचालित बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create the file in .github/CODEOWNERS (or CODEOWNERS at root, or docs/CODEOWNERS)
Step 2 → Each line: <path pattern>  <@user or @org/team or email> ...
Step 3 → Patterns work like .gitignore; the LAST matching line wins
Step 4 → Open a PR that touches matching files -> GitHub auto-adds owners as reviewers
Step 5 → In branch protection enable "Require review from Code Owners"
Step 6 → PR cannot merge until an owner (with write access) approves the changed files
Step 7 → Check validity: repo -> file view shows errors for invalid lines
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → file बनाओ: .github/CODEOWNERS (या root पर CODEOWNERS, या docs/CODEOWNERS)
Step 2 → हर line: <path pattern>  <@user या @org/team या email>
Step 3 → Patterns .gitignore जैसे चलते हैं; आख़िरी मिलती-जुलती line जीतती है
Step 4 → मिलती files बदलने वाले PR पर GitHub owners को अपने-आप reviewer बनाता है
Step 5 → Branch protection में "Require review from Code Owners" चालू करो
Step 6 → जब तक owner (write access वाला) approve न करे, PR merge नहीं होगा
Step 7 → मान्यता जाँच: file view में अमान्य lines की errors दिखती हैं
```

---

## 🟡 Real World Example
A SaaS company: the `payments/` folder is owned by `@acme/payments-team`; `infra/` and `.github/` by `@acme/devops`; the React frontend by `@acme/frontend`. A frontend dev changes `deploy.yml` to "speed up the build" and accidentally adds `pull_request_target`. GitHub automatically requests review from `@acme/devops`, they spot the risk and reject it. Without CODEOWNERS, a frontend teammate could have approved it unknowingly.

## 🟡 Real Example Hindi mein
एक SaaS कंपनी: `payments/` folder `@acme/payments-team` का है; `infra/` और `.github/` `@acme/devops` के; React frontend `@acme/frontend` का। एक frontend dev "build तेज़ करने" के लिए `deploy.yml` बदलता है और ग़लती से `pull_request_target` जोड़ देता है। GitHub अपने-आप `@acme/devops` से review माँगता है, वे जोखिम पकड़कर reject करते हैं। CODEOWNERS के बिना कोई frontend साथी अनजाने में approve कर सकता था।

---

## 💻 Code / Config Example — Basic

```text
# .github/CODEOWNERS  (basic)
# Format: pattern   owner1 owner2 ...
# Lines starting with # are comments. The LAST matching pattern wins.

# Default owner for everything not matched below
*                       @addyrj

# Frontend (React) belongs to frontend folks
/frontend/              @addyrj

# Backend FastAPI
/backend/               @addyrj

# Any Dockerfile anywhere in the repo
Dockerfile              @addyrj
```

## 💻 Code / Config Example — Advanced

```text
# .github/CODEOWNERS  (production, team based)
# Teams must be written as @org/team-slug and the team needs WRITE access to the repo.
# Order matters: general rules first, most specific LAST (last match wins).

# 1) Fallback: platform lead reviews anything unowned
*                           @acme/tech-leads

# 2) Application code
/apps/web/                  @acme/frontend
/apps/api/                  @acme/backend
/apps/worker/               @acme/backend
/packages/shared/           @acme/frontend @acme/backend   # two teams: either team can satisfy the requirement

# 3) Documentation can be reviewed by anyone on docs or leads
*.md                        @acme/docs
/docs/                      @acme/docs

# 4) Risky files: infrastructure and CI/CD need DevOps review
/infra/                     @acme/devops
/.github/                   @acme/devops
/.github/CODEOWNERS         @acme/tech-leads              # who may change ownership rules themselves
**/Dockerfile               @acme/devops
**/docker-compose*.yml      @acme/devops
/infra/nginx/               @acme/devops @acme/security

# 5) Security-sensitive paths
/apps/api/app/auth/         @acme/security
/apps/api/app/payments/     @acme/payments @acme/security

# 6) Lock files: let a bot or any dev handle (empty owner list = no owner, overrides earlier rules)
/package-lock.json
```

---

## 🟠 My Stack Integration
Map your stack: React to a frontend owner, FastAPI to backend, `infra/nginx` and workflows to whoever controls the VPS/AWS. Then require Code Owner review in the ruleset from topic 33. Also have CI verify the file exists so it is never deleted silently:

```yaml
# .github/workflows/codeowners-check.yml - fail PR if CODEOWNERS is missing or has bad syntax markers
name: CODEOWNERS check                      # name in Actions tab
on:
  pull_request:                             # on every PR
    branches: [main]                        # into main
jobs:
  check:                                    # job id
    runs-on: ubuntu-latest                  # hosted runner
    steps:
      - uses: actions/checkout@v4           # get the code (example version)
      - name: File exists and is not empty  # step label
        run: |                              # shell
          test -s .github/CODEOWNERS        # -s: file exists and has size > 0
      - name: No line without an owner except intended ones   # light sanity check
        run: |                              # shell
          # print any non-comment line having only a pattern (no @owner); review by eye
          grep -vE '^\s*(#|$)' .github/CODEOWNERS | awk 'NF==1 {print "No owner on line: " $0}'
```
Security: ownership of `.github/` and `infra/` by DevOps is a core control, because workflows read secrets and deploy to production. An attacker with write access could otherwise alter the workflow in a PR approved by a non-expert.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Owner team has only Read access, so its approval does not count.
✅ Correct: Code owners must have Write permission to the repo.

❌ Mistake 2: Writing a broad rule last (`* @lead`), overriding all specific rules above.
✅ Correct: Put `*` first and specific paths later (last match wins).

❌ Mistake 3: Creating CODEOWNERS but never enabling "Require review from Code Owners".
✅ Correct: Turn it on in branch protection/ruleset; otherwise it only suggests reviewers.

❌ Mistake 4: Owner is one person, so PRs stall when they are on leave.
✅ Correct: Use teams with 2+ members and a backup.

---

## 🧠 Tricky Interview Question
CODEOWNERS says `/infra/ @acme/devops`, and a PR changes only `infra/nginx.conf`. A devops member approves. But the author is also a devops member. Can they self-approve?

Answer: No. GitHub does not let a PR author approve their own PR. With "Require review from Code Owners" on, another owner (not the author) must approve. This is why a team needs at least 2 members; with "Require approval of the most recent push" the last pusher also cannot approve.

---

## ⚫ Interview Questions + Answers

Q1: Where can CODEOWNERS live?
A1: `.github/CODEOWNERS`, repo root, or `docs/`. GitHub uses the first found in that order.

Q2: How are patterns evaluated?
A2: Like `.gitignore` patterns, last matching pattern takes precedence. Later specific rules override earlier general ones.

Q3: Does CODEOWNERS block merges by itself?
A3: No. It only requests reviewers. Enforcement requires "Require review from Code Owners" in branch protection or a ruleset.

Q4: How to assign multiple owners?
A4: List them on one line; ANY one of them satisfying review is enough (for one rule).

Q5: How do you remove ownership for a path?
A5: Add a line with the pattern and no owners, placed after the general rule.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- More than 2-3 contributors, or sensitive folders (infra, auth, payments)
- You need compliance evidence of who reviewed what

❌ Avoid when:
- Solo project (no one else to review)
- Overly granular ownership for every file, causing reviewer fatigue

---

## 📊 Visual Diagram
```
 PR changes:  apps/web/App.tsx      infra/nginx/app.conf     .github/workflows/deploy.yml
                  |                       |                          |
          CODEOWNERS match        CODEOWNERS match           CODEOWNERS match
                  v                       v                          v
           @acme/frontend           @acme/devops               @acme/devops
                  \_______________________|___________________________/
                                          v
                   auto-requested reviewers + required in branch protection
                                          v
                               merge only after all owners approve
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Code owner | Person/team responsible for a path | path का ज़िम्मेदार |
| Pattern | Path glob like .gitignore | path pattern |
| Last match wins | Later rule overrides earlier | आख़िरी rule मान्य |
| Required review | Branch rule needing owner approval | अनिवार्य review |
| Team slug | `@org/team-name` handle | team का नाम |
| Self-approval | Author approving own PR (not allowed) | खुद का approval (मना) |

---

## ⚡ 3-Line Summary
English: CODEOWNERS maps paths to responsible reviewers who are auto-requested on PRs.
Enforce it with "Require review from Code Owners"; last matching pattern wins.
Always protect `.github/` and `infra/` with a DevOps owner team.
Hindi: CODEOWNERS paths को ज़िम्मेदार reviewers से जोड़ती है जो PR पर अपने-आप माँगे जाते हैं।
इसे "Require review from Code Owners" से लागू करो; आख़िरी मिलता pattern जीतता है।
`.github/` और `infra/` हमेशा DevOps owner team को दो।

---

## ➡️ Next Topic
**35. GitHub Environments**: add per-stage rules (staging vs production) with manual approvals and environment-specific secrets.

---
