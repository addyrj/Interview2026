# 20. Trunk Based Development
# हिंदी में: Trunk Based Development

---

## 🔵 Simple Definition (English)
**Trunk Based Development (TBD)** means all developers integrate small changes into a single shared branch (the "trunk", usually `main`) at least daily. Branches, if any, live hours not weeks. Unfinished work is hidden with **feature flags**, so trunk stays releasable.

## 🔵 सरल परिभाषा (Hindi)
**Trunk Based Development (TBD)** का मतलब है कि सब developers छोटे changes को एक shared branch ("trunk", आमतौर पर `main`) में कम से कम रोज़ merge करते हैं। Branches, अगर हों भी, तो घंटों की होती हैं, हफ्तों की नहीं। अधूरा काम **feature flags** से छुपाया जाता है ताकि trunk releasable रहे।

---

## 🔴 Problem it Solves
Long-lived branches diverge; merging them causes "merge hell", late integration bugs and delayed feedback. Teams also fear releases. TBD forces continuous integration in the real sense: everyone's code meets everyone else's daily, so conflicts are tiny and CI feedback is immediate. DORA research links TBD with higher deploy frequency and lower change failure rate.

## 🔴 यह क्यों बना? (Hindi)
Long-lived branches diverge होती हैं; उन्हें merge करने से "merge hell", देर से मिलने वाले integration bugs और धीमा feedback मिलता है। Teams release से डरती भी हैं। TBD असली मायने में continuous integration करवाता है: सबका code रोज़ सबके code से मिलता है, इसलिए conflicts छोटे और CI feedback तुरंत। DORA research TBD को ज़्यादा deploy frequency और कम change failure rate से जोड़ती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pull latest trunk (main) several times a day.
Step 2 → Make a SMALL change (a few hours of work).
Step 3 → Run tests locally, push a short-lived branch (<1 day) or commit directly (small teams).
Step 4 → Fast PR review (minutes/hours), CI must be quick (<10 min).
Step 5 → Merge to trunk; unfinished feature stays behind a flag (default OFF).
Step 6 → CD deploys trunk; turn the flag on gradually (1%, 10%, 100%).
Step 7 → Remove the flag and dead code when feature is fully rolled out.
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → दिन में कई बार latest trunk (main) pull करो।
Step 2 → छोटा change करो (कुछ घंटे का काम)।
Step 3 → Local tests चलाओ, छोटी branch (<1 दिन) push करो या सीधे commit करो (छोटी teams)।
Step 4 → Fast PR review (मिनट/घंटे), CI तेज़ (<10 मिनट)।
Step 5 → Trunk में merge; अधूरा feature flag के पीछे (default OFF)।
Step 6 → CD trunk deploy करता है; flag धीरे-धीरे on करो (1%, 10%, 100%)।
Step 7 → पूरा rollout होने पर flag और dead code हटाओ।

---

## 🟡 Real World Example
Google and Facebook famously keep most code on one trunk with thousands of daily commits, relying on automated tests and flags. For you: you add a new "UPI payment" option to the Node.js API. You merge the endpoint daily but it is hidden behind `ENABLE_UPI=false`. Once ready, you set the env var to true for 10% of users, watch error metrics, then 100%.

## 🟡 Real Example Hindi mein
Google और Facebook की मशहूर practice है कि ज़्यादातर code एक trunk पर रहता है, रोज़ हज़ारों commits, और automated tests व flags पर भरोसा। आपके लिए: Node.js API में नया "UPI payment" option जोड़ रहे हैं। Endpoint रोज़ merge होता है पर `ENABLE_UPI=false` के पीछे छुपा है। तैयार होने पर 10% users के लिए true करो, error metrics देखो, फिर 100%।

---

## 💻 Code / Config Example — Basic

A minimal feature flag in Node.js (env-based) and the TBD daily loop.

```javascript
// flags.js - simplest feature flag: read an env var once at startup
const flags = {
  // "true" string turns it on; anything else (or missing) is OFF
  upiPayments: process.env.ENABLE_UPI === 'true',
};
module.exports = flags;                              // export for use in routes
```

```javascript
// routes.js - unfinished feature merged to trunk but hidden
const express = require('express');                  // web framework
const flags = require('./flags');                    // import flag values
const router = express.Router();                     // create a router

router.post('/pay/upi', (req, res) => {              // new endpoint
  if (!flags.upiPayments) return res.status(404).json({ error: 'Not found' });  // hidden when OFF
  return res.json({ ok: true });                     // placeholder behaviour when ON
});
module.exports = router;                             // export router
```

```bash
#!/usr/bin/env bash
# tbd-daily-loop.sh - small, frequent integration
set -euo pipefail                                    # strict mode
git switch main && git pull --rebase origin main     # start from newest trunk (rebase keeps history linear)
# ... make a small change + run tests ...
git add -A && git commit -m "feat(pay): add hidden UPI endpoint"   # small commit
git pull --rebase origin main                        # integrate others' work again right before push
git push origin HEAD:main                            # push; with branch protection use a short-lived PR instead
```

## 💻 Code / Config Example — Advanced

Percentage rollout flag + fast CI with required check. Deterministic bucketing so a user keeps the same experience.

```javascript
// rollout.js - percentage-based flag with stable per-user bucketing
const crypto = require('crypto');                    // built-in hashing

function bucket(userId) {
  const h = crypto.createHash('sha256').update(String(userId)).digest(); // hash user id
  return h.readUInt32BE(0) % 100;                    // map to 0..99 deterministically
}

function isEnabled(flagName, userId, percent) {
  if (percent <= 0) return false;                    // fully off
  if (percent >= 100) return true;                   // fully on
  return bucket(flagName + ':' + userId) < percent;  // include flag name so flags roll out independently
}

module.exports = { isEnabled };                      // export helper
```

```yaml
# .github/workflows/trunk-ci.yml - fast feedback for trunk based dev
name: trunk-ci                                       # workflow name
on:
  pull_request:                                      # short-lived branches
    branches: [main]
  push:
    branches: [main]                                 # post-merge verification
jobs:
  verify:
    runs-on: ubuntu-latest                           # runner
    timeout-minutes: 10                              # enforce the "CI under 10 minutes" rule
    steps:
      - uses: actions/checkout@v4                    # fetch code (example version)
      - uses: actions/setup-node@v4                  # Node setup (example version)
        with:
          node-version: 20                           # version
          cache: npm                                 # cache dependencies
      - run: npm ci                                  # install
      - run: npm run lint --if-present               # lint if script exists
      - run: npm test                                # unit tests
```

---

## 🟠 My Stack Integration
- **Node.js/FastAPI:** flags via env vars, a DB table, or a service (Unleash, GrowthBook, LaunchDarkly). For FastAPI use a dependency that reads the flag.
- **React:** hide new UI with a flag from `/api/flags`; build once, enable per user.
- **VPS/Nginx:** deploy trunk on each merge; flags can be changed without redeploy if stored in DB/Redis.
- **AWS:** AppConfig supports feature flags with gradual rollout.

```yaml
# docker-compose.yml fragment: flags as environment (changing needs container restart)
services:
  api:
    image: myorg/api:1.0.0                           # example image
    environment:
      - ENABLE_UPI=false                             # flag default OFF in production
    restart: unless-stopped                          # auto-restart
```

**Security:** flags that gate security-sensitive or payment features need access control and audit logs; never rely on hiding a UI button, enforce the flag on the server. Remove stale flags to avoid forgotten code paths.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Adopting TBD without automated tests.
✅ Correct: Build a fast, reliable test suite first.

❌ Mistake 2: Flags that live forever.
✅ Correct: Track owner and removal date; delete after rollout.

❌ Mistake 3: Calling 2-week branches "trunk based".
✅ Correct: Branches under a day or two.

❌ Mistake 4: Enforcing flags only in the frontend.
✅ Correct: Enforce on the backend.

---

## 🧠 Tricky Interview Question
How can you do a big database schema change with trunk based development and zero downtime?

**Answer:** Use expand/contract migrations: (1) add the new column/table (backward compatible), (2) deploy code writing to both, (3) backfill, (4) switch reads behind a flag, (5) remove old column later. Each step is small, mergeable to trunk and reversible.

---

## ⚫ Interview Questions + Answers

Q1: How is TBD different from GitHub Flow?
A1: Very similar; TBD emphasises even smaller, more frequent merges (at least daily) and flags, and permits direct commits for small teams.

Q2: How do you handle unfinished features?
A2: Feature flags or "branch by abstraction".

Q3: What are release branches in TBD?
A3: Optional short-lived branches cut from trunk for a release; fixes go to trunk first, then are cherry-picked.

Q4: Prerequisites?
A4: Fast reliable CI, good tests, code review culture, flags.

Q5: Why is it linked with better DORA metrics?
A5: Small batches mean faster lead time, lower risk per change and quick recovery.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Mature CI/CD, strong tests, frequent deploys.

❌ Avoid when:
- No test automation; open-source projects with untrusted contributors (fork + PR fits better).

---

## 📊 Visual Diagram

```
 trunk(main)  o-o-o-o-o-o-o-o-o-o-o-o--->   many small commits daily
               \_/   \_/                    (branches live < 1 day)
 flag:  newFeature = OFF ----> 10% ----> 100% ----> flag removed
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Trunk | Main shared branch | मुख्य shared branch |
| Feature flag | Toggle to hide features | feature छुपाने का toggle |
| Branch by abstraction | Hide change behind interface | interface के पीछे बदलाव छुपाना |
| Cherry-pick | Copy one commit to another branch | एक commit दूसरी branch में कॉपी |
| Expand/contract | Safe schema change pattern | सुरक्षित schema बदलने का तरीका |

---

## ⚡ 3-Line Summary
English: Everyone merges small changes into trunk at least daily.
Feature flags hide unfinished work so trunk stays releasable.
It needs strong automated tests and fast CI.
Hindi: सब लोग छोटे changes रोज़ trunk में merge करते हैं।
Feature flags अधूरा काम छुपाते हैं ताकि trunk releasable रहे।
इसके लिए मज़बूत automated tests और तेज़ CI चाहिए।

---

## ➡️ Next Topic
**21. Branch Naming Conventions** - consistent names that tools and humans can parse.

---
