# 3. DevOps Culture + Principles
# हिंदी में: DevOps Culture और सिद्धांत

---

## 🔵 Simple Definition (English)
**DevOps culture** is the set of shared values and habits that make DevOps work: shared ownership, collaboration, automation, fast feedback, continuous improvement and blameless learning. The best-known framework is **CALMS** (Culture, Automation, Lean, Measurement, Sharing).

## 🔵 सरल परिभाषा (Hindi)
**DevOps culture** साझा values और आदतों का set है जिससे DevOps काम करता है: साझा ownership, सहयोग, automation, तेज़ feedback, लगातार सुधार और blameless सीख। सबसे जाना-माना framework **CALMS** है (Culture, Automation, Lean, Measurement, Sharing)।

---

## 🔴 Problem it Solves
You can install every DevOps tool and still fail if people behave the old way:
- Blame culture: after an outage, people hide mistakes, so the same failure repeats.
- Hero culture: only one person knows how to deploy; when they are on leave, nothing ships.
- "Not my job": Dev ignores production problems; Ops ignores code quality.
- Fear of change: because releases hurt, people avoid releasing, which makes releases even bigger and more painful.

## 🔴 यह क्यों बना? (Hindi)
सारे DevOps tools install करके भी fail हो सकते हैं अगर लोग पुराने तरीके से व्यवहार करें:
- Blame culture: outage के बाद लोग गलतियाँ छिपाते हैं, इसलिए वही failure दोहराता है।
- Hero culture: सिर्फ एक व्यक्ति को deploy आता है; वह छुट्टी पर तो कुछ ship नहीं होता।
- "मेरा काम नहीं": Dev production problems को ignore करता, Ops code quality को।
- बदलाव का डर: releases दर्द देती हैं तो लोग release से बचते हैं, जिससे releases और बड़ी और दर्दनाक होती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 -> Shared ownership: the team that writes a service also runs it ("you build it, you run it")
Step 2 -> Automate repeated work (build, test, deploy, provisioning)
Step 3 -> Work in small batches (small PRs, small releases)
Step 4 -> Measure everything (DORA metrics, error rate, latency)
Step 5 -> Fast feedback (CI results in minutes, alerts in seconds)
Step 6 -> Blameless post-mortem after incidents: fix the system, not the person
Step 7 -> Share knowledge (runbooks, docs, demos) and improve continuously
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 -> साझा ownership: जो team service बनाती है वही चलाती भी है ("you build it, you run it")
Step 2 -> बार-बार होने वाला काम automate करो (build, test, deploy, provisioning)
Step 3 -> छोटे batches में काम (छोटे PRs, छोटी releases)
Step 4 -> सब कुछ नापो (DORA metrics, error rate, latency)
Step 5 -> तेज़ feedback (CI result मिनटों में, alerts सेकंडों में)
Step 6 -> Incident के बाद blameless post-mortem: system ठीक करो, व्यक्ति को नहीं
Step 7 -> ज्ञान साझा करो (runbooks, docs, demos) और लगातार सुधारो
```

---

## 🟡 Real World Example
**An outage at a Swiggy-like company.** A developer's change doubled database load and the app slowed for 20 minutes. In a blame culture, the developer is scolded and next time hides small risky changes. In a DevOps culture, the team holds a blameless post-mortem: "Why could a change like this reach production without a load check? Why did the alert fire only after 15 minutes?" Result: a load test is added to the pipeline and the alert threshold is fixed. The same failure cannot happen again.

**Your VPS:** if only you know the deployment steps, you are the single point of failure. Put steps in a pipeline and a short runbook (`RUNBOOK.md`) so anyone can deploy or roll back.

## 🟡 Real Example Hindi mein
**Swiggy जैसी कंपनी में outage।** एक developer के change से database load दोगुना हो गया और app 20 मिनट धीमा रहा। Blame culture में developer को डाँट पड़ती है और अगली बार वह छोटे risky changes छिपाता है। DevOps culture में team blameless post-mortem करती है: "ऐसा change load check के बिना production तक कैसे पहुँचा? Alert 15 मिनट बाद ही क्यों बजा?" नतीजा: pipeline में load test जुड़ा और alert threshold ठीक हुआ। वही failure दोबारा नहीं हो सकता।

**आपका VPS:** अगर deploy के steps सिर्फ आपको पता हैं तो आप single point of failure हैं। Steps को pipeline और छोटे runbook (`RUNBOOK.md`) में डालिए ताकि कोई भी deploy या rollback कर सके।

---

## 💻 Code / Config Example — Basic
Culture as code: a pull-request template and CODEOWNERS enforce review and shared ownership.

```markdown
<!-- .github/pull_request_template.md -->
<!-- Shown automatically in every new pull request -->
## What changed?
<!-- one or two lines in simple words -->

## How was it tested?
<!-- unit tests, manual steps, screenshots -->

## Risk and rollback
<!-- what can break? how do we undo it (revert commit / previous image tag)? -->

## Checklist
- [ ] Tests added or updated
- [ ] No secrets in the diff
- [ ] Docs / runbook updated if behavior changed
```

```text
# .github/CODEOWNERS
# Each line: path pattern, then the owners who must review changes there
*                    @your-org/backend-team
/frontend/           @your-org/frontend-team
/.github/workflows/  @your-org/platform-team
/nginx/              @your-org/platform-team
```

## 💻 Code / Config Example — Advanced
Automated feedback: a PR gate that blocks merge without tests, and a blameless post-mortem issue template.

```yaml
# .github/workflows/pr-gate.yml
name: PR Gate                                   # shows as a required check on PRs
on:
  pull_request:                                 # run for every pull request
    branches: [main]                            # targeting main
permissions:
  contents: read                                # read-only token
  pull-requests: write                          # allow commenting on the PR
concurrency:
  group: pr-${{ github.event.pull_request.number }}   # one run per PR
  cancel-in-progress: true                      # new push cancels the old run (fast feedback)
jobs:
  checks:
    runs-on: ubuntu-latest                      # runner
    timeout-minutes: 10                         # fail fast, never hang
    steps:
      - uses: actions/checkout@v4               # get code
      - uses: actions/setup-node@v4             # Node.js
        with:
          node-version: 20                      # version
          cache: npm                            # cache
      - run: npm ci                             # install
      - run: npm run lint --if-present          # style rules shared by whole team
      - run: npm test -- --coverage             # tests plus coverage (measurement)
      - name: Post summary                      # share results with the team
        if: always()                            # even when tests fail
        run: echo "### PR checks finished with status ${{ job.status }}" >> "$GITHUB_STEP_SUMMARY"   # visible on the run page
```

```yaml
# .github/ISSUE_TEMPLATE/postmortem.yml
name: Blameless post-mortem                     # template name in the issue picker
description: Learn from an incident without blaming people   # short help text
title: "[Post-mortem] "                         # default issue title prefix
labels: ["postmortem"]                          # auto label
body:
  - type: textarea                              # free-text box
    id: timeline                                # field id
    attributes:
      label: Timeline                           # label shown to the user
      description: What happened and when (UTC)?   # hint
    validations:
      required: true                            # cannot submit empty
  - type: textarea
    id: causes                                  # contributing factors
    attributes:
      label: Contributing factors (system, not people)   # focus on process
    validations:
      required: true
  - type: textarea
    id: actions                                 # follow-up work
    attributes:
      label: Action items with owner and due date   # makes learning concrete
    validations:
      required: true
```

---

## 🟠 My Stack Integration
- **Node.js / React / FastAPI:** the same CI gate runs for all; coding standards (ESLint, Prettier, `ruff` or `flake8` for Python) are enforced by the pipeline, not by arguments.
- **Nginx / VPS:** keep `RUNBOOK.md` in the repo with: how to deploy, how to roll back, where logs are (`docker logs`, `/var/log/nginx`), who to call.
- **AWS:** tag resources with `owner` and `team` so ownership is visible; set budget alerts so cost is everyone's concern.
- Enable branch protection on `main`: require PR, require passing checks, require 1 review.

```yaml
# Branch protection via GitHub CLI - run once (bash), needs admin rights
# gh api -X PUT repos/OWNER/REPO/branches/main/protection --input protection.json
# protection.json (shown as YAML-like idea, the API takes JSON):
required_status_checks:                         # checks that must pass
  strict: true                                  # branch must be up to date
  contexts: ["checks"]                          # job name from pr-gate.yml
required_pull_request_reviews:
  required_approving_review_count: 1            # at least one teammate reviews
enforce_admins: true                            # rules apply to admins too
```
Security: shared responsibility means security reviews and secret scanning are part of everyone's PR, not a final gate by another team.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Hiring a "DevOps person" and expecting culture to change.
✅ Correct: Leaders must change incentives: reward stability and speed together; share on-call.

❌ Mistake 2: Post-mortems that end with "human error".
✅ Correct: Ask "why was it possible?" and fix the system (tests, guardrails, alerts).

❌ Mistake 3: Measuring individuals (commits per person).
✅ Correct: Measure team outcomes (DORA metrics).

❌ Mistake 4: Knowledge locked in one head.
✅ Correct: Write runbooks, pair on deploys, rotate on-call.

---

## 🧠 Tricky Interview Question
**"A junior engineer deleted a production database table by mistake. What should the company do?"**

Answer: Do not punish; run a blameless post-mortem. The real question is why one person could delete production data without a guard. Fixes: least-privilege access (juniors have read-only prod), backups with tested restore, approval for destructive actions, staging for experiments. Punishing teaches people to hide mistakes. (Accountability still exists, but it is about improving the system and learning, not shaming.)

---

## ⚫ Interview Questions + Answers

Q1: What does CALMS stand for?
A1: Culture, Automation, Lean, Measurement, Sharing. It is a checklist for judging how DevOps-ready a team is.

Q2: What is "you build it, you run it"?
A2: A principle (popularised by Amazon) where the development team owns the service in production, including on-call. It gives developers a direct incentive to build reliable software.

Q3: What is a blameless post-mortem?
A3: A written review after an incident that records timeline, causes and actions, focusing on process and system gaps rather than individual fault, so people report problems honestly.

Q4: What are the Three Ways of DevOps?
A4: From "The Phoenix Project": (1) Flow: speed work from Dev to Ops to customer, (2) Feedback: fast loops from production back, (3) Continual learning and experimentation.

Q5: How do you measure whether DevOps culture is working?
A5: DORA metrics (deployment frequency, lead time, change failure rate, MTTR), plus team signals such as on-call load, post-mortem action completion and developer satisfaction.

---

## 🔷 When to Use + When Not to Use
✅ Use these principles when:
- Teams are growing and handoffs cause delays.
- Outages repeat with similar causes.
- You want developers and ops to share one goal.

❌ Avoid / be careful when:
- Culture is forced from the top with no change in incentives (it becomes slogans).
- "Blameless" is misused to ignore repeated negligence; accountability for learning still matters.

---

## 📊 Visual Diagram
```
                 CALMS
   +---------+---------+------+-------------+---------+
   | Culture |Automation| Lean | Measurement | Sharing |
   +----+----+----+----+--+---+------+------+----+----+
        |         |       |          |           |
   shared goals  CI/CD  small     DORA, SLOs   docs,
   blameless    IaC     batches   dashboards   runbooks
        \_________|_______|__________|___________/
                          |
                  Better, faster, safer delivery
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CALMS | Culture, Automation, Lean, Measurement, Sharing | DevOps के पाँच स्तंभ |
| Blameless | Focus on system causes, not people | व्यक्ति नहीं, system पर ध्यान |
| Post-mortem | Review after an incident | Incident के बाद की समीक्षा |
| On-call | Being reachable to fix incidents | Incident ठीक करने के लिए उपलब्ध रहना |
| Runbook | Step-by-step guide for operations | Operations के लिए step-by-step guide |
| Single point of failure | One thing whose failure stops everything | एक चीज़ जिसके fail होने से सब रुक जाए |

---

## ⚡ 3-Line Summary
English: DevOps culture means shared ownership, collaboration and blameless learning.
Automation, measurement and small batches turn those values into daily practice.
Tools without culture fail; culture without tools does not scale.

Hindi: DevOps culture यानी साझा ownership, सहयोग और blameless सीख।
Automation, measurement और छोटे batches इन values को रोज़ की आदत बनाते हैं।
Culture के बिना tools fail होते हैं; tools के बिना culture scale नहीं होता।

---

## ➡️ Next Topic
**4. DevOps Lifecycle** — now that you know the mindset, see the actual loop of phases (Plan to Monitor) the team runs.
