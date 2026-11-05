# 354. Feature Flags Deploy
# हिंदी में: Feature Flags के साथ Deploy

---

## 🔵 Simple Definition (English)
A feature flag (feature toggle) is a switch in your code that turns a feature on or off without redeploying. You deploy code with the feature hidden ("dark"), then enable it for internal users, a percentage, or everyone by changing a config value. This separates deploying from releasing.

## 🔵 सरल परिभाषा (Hindi)
Feature flag (feature toggle) आपके code में एक switch है जो बिना दोबारा deploy किए किसी feature को on या off करता है। आप code को feature छिपाकर ("dark") deploy करते हैं, फिर config बदलकर उसे internal users, कुछ प्रतिशत या सबके लिए चालू करते हैं। इससे deploy करना और release करना अलग हो जाते हैं।

---

## 🔴 Problem it Solves
Long-lived feature branches cause painful merges, and releasing a big feature means a risky deploy where rollback means reverting code. Marketing wants a launch at 10:00 sharp, not "whenever the deploy finishes". Flags let you merge small changes to main daily, release when the business is ready, and "kill" a broken feature in seconds without a rollback deploy.

## 🔴 यह क्यों बना? (Hindi)
लंबे समय की feature branches से merge मुश्किल होते हैं, और बड़े feature का release risky deploy होता है जिसमें rollback का मतलब code revert करना है। Marketing को launch ठीक 10:00 बजे चाहिए, "जब deploy खत्म हो तब" नहीं। Flags से आप छोटे बदलाव रोज़ main में merge करते हैं, business तैयार हो तब release करते हैं, और खराब feature को बिना rollback deploy के सेकंडों में बंद कर देते हैं ("kill switch")।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Wrap new code in: if (flags.isEnabled('new_checkout', user))
Step 2 → Default the flag to OFF in all environments
Step 3 → Deploy normally; users still see the old behavior
Step 4 → Turn the flag ON for staff, then 5%, 25%, 100%
Step 5 → Watch metrics; flip OFF instantly if errors rise (kill switch)
Step 6 → When fully released, delete the flag and old code path
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → नया code लपेटो: if (flags.isEnabled('new_checkout', user))
Step 2 → हर environment में flag का default OFF रखो
Step 3 → सामान्य deploy करो; users को अब भी पुराना behavior दिखता है
Step 4 → Flag staff के लिए ON करो, फिर 5%, 25%, 100%
Step 5 → Metrics देखो; errors बढ़ें तो तुरंत OFF (kill switch)
Step 6 → पूरा release होने पर flag और पुराना code path हटा दो
```

---

## 🟡 Real World Example
A ride-booking app ships a new fare-estimation algorithm. The code is deployed on Tuesday behind `new_fare_v2=false`. On Thursday it is enabled for employees, then 10% of one city. The next morning a rounding bug appears for night rides; the team turns the flag off in 5 seconds without touching the deployment. After a week at 100% the flag and the old algorithm are removed. Facebook, Uber and Swiggy use flag systems for exactly this.

## 🟡 Real Example Hindi mein
एक ride-booking app नया fare-estimation algorithm भेजता है। Code मंगलवार को `new_fare_v2=false` के पीछे deploy होता है। गुरुवार को employees के लिए, फिर एक शहर के 10% के लिए ON होता है। अगली सुबह रात की rides में rounding bug दिखता है; team 5 सेकंड में flag बंद कर देती है, deployment को छुए बिना। एक हफ्ता 100% पर चलने के बाद flag और पुराना algorithm हटा दिए जाते हैं।

---

## 💻 Code / Config Example — Basic

```javascript
// flags.js - simplest flags from environment variables (restart needed to change)
const flags = {
  // read env var; anything other than "true" means OFF
  newCheckout: process.env.FLAG_NEW_CHECKOUT === 'true',
  // second example flag with a safe default
  betaSearch: process.env.FLAG_BETA_SEARCH === 'true',
};
// export so routes can import it
module.exports = flags;
```

```javascript
// routes/checkout.js - use the flag in a route
const express = require('express');           // web framework
const flags = require('../flags');            // flag values
const router = express.Router();             // route group

router.post('/checkout', (req, res) => {
  if (flags.newCheckout) {                    // new path behind the flag
    return res.json({ flow: 'v2' });
  }
  return res.json({ flow: 'v1' });            // old, stable path
});
module.exports = router;
```

## 💻 Code / Config Example — Advanced

```json
{
  "_comment": "flags.json - stored in S3 / Redis / DB so it can change at runtime",
  "new_checkout": { "enabled": true,  "percentage": 10, "allowUsers": ["admin@example.com"] },
  "beta_search":  { "enabled": false, "percentage": 0,  "allowUsers": [] }
}
```

```javascript
// flagService.js - runtime flags with percentage rollout and a kill switch
const crypto = require('crypto');                       // for stable hashing
let cache = {};                                         // in-memory copy of flags
async function refresh(fetchFlags) {                    // call on an interval
  try { cache = await fetchFlags(); }                   // fetchFlags reads Redis/S3/API
  catch (e) { /* keep last known good flags on error */ }
}
function bucket(flagName, userId) {                     // map user to 0..99 consistently
  const h = crypto.createHash('sha256').update(`${flagName}:${userId}`).digest();
  return h.readUInt32BE(0) % 100;                       // same user -> same bucket
}
function isEnabled(flagName, user) {
  const f = cache[flagName];                            // look up the flag
  if (!f || !f.enabled) return false;                   // unknown or off => safe default
  if (f.allowUsers?.includes(user?.email)) return true; // explicit allow list
  return bucket(flagName, user?.id ?? 'anon') < f.percentage;   // percentage rollout
}
module.exports = { refresh, isEnabled };
```

```javascript
// server.js (part) - refresh flags every 15 seconds
const { refresh, isEnabled } = require('./flagService');
const fetchFlags = async () => (await fetch(process.env.FLAGS_URL)).json();   // Node 18+ fetch
refresh(fetchFlags);                                    // initial load
setInterval(() => refresh(fetchFlags), 15000).unref();  // periodic reload
```

```yaml
# .github/workflows/toggle-flag.yml - change a flag from GitHub (audited, with approval)
name: Toggle Feature Flag
on:
  workflow_dispatch:
    inputs:
      flag:
        description: "Flag name"
        required: true
      percentage:
        description: "Rollout percentage (0-100)"
        required: true
jobs:
  toggle:
    runs-on: ubuntu-latest
    environment: production                      # reviewers can approve the change
    steps:
      - uses: actions/checkout@v4                # get repo with flags.json
      - run: |
          # update the percentage with jq and write back (validate input is numeric)
          [[ "${{ inputs.percentage }}" =~ ^[0-9]+$ ]] || exit 1
          jq --arg f "${{ inputs.flag }}" --argjson p "${{ inputs.percentage }}" \
             '.[$f].percentage = $p | .[$f].enabled = ($p > 0)' flags.json > flags.new
          mv flags.new flags.json
      - uses: aws-actions/configure-aws-credentials@v4   # example version
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}     # OIDC role, no long-lived keys
          aws-region: ap-south-1
      - run: aws s3 cp flags.json s3://my-config-bucket/flags.json   # publish new flags
```

---

## 🟠 My Stack Integration
- Node.js and FastAPI read flags from Redis or an S3 JSON file and cache them for a few seconds.
- React gets evaluated flags from an API endpoint (`/api/flags`) after login, not the raw rules.
- Nginx can route using a cookie flag, as used by canary releases (352).
- For a managed service consider Unleash (self-hosted), LaunchDarkly, GrowthBook or AWS AppConfig.

```python
# FastAPI: same idea in Python
import hashlib, json, os, time
_cache = {"t": 0, "v": {}}                       # tiny in-memory cache

def load_flags():
    if time.time() - _cache["t"] > 15:           # refresh every 15 seconds
        try:
            with open(os.getenv("FLAGS_FILE", "flags.json")) as f:
                _cache["v"] = json.load(f)       # could also come from Redis
        except Exception:
            pass                                 # keep last good flags
        _cache["t"] = time.time()
    return _cache["v"]

def is_enabled(name, user_id):
    f = load_flags().get(name)
    if not f or not f.get("enabled"):
        return False                             # safe default is OFF
    h = int(hashlib.sha256(f"{name}:{user_id}".encode()).hexdigest(), 16) % 100
    return h < f.get("percentage", 0)            # same user, same result
```

Security: never trust a flag value sent by the browser for authorization. Evaluate on the server, protect the flag-admin endpoint with authentication, and audit every change.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Never removing old flags.
✅ Correct: Track flags with an owner and expiry date; delete after full rollout.

❌ Mistake 2: Random per-request decisions, so users flicker between old and new.
✅ Correct: Hash a stable user id for sticky buckets.

❌ Mistake 3: Using flags for permissions or entitlements.
✅ Correct: Flags are release controls; use real authorization for access rules.

❌ Mistake 4: Flag service down breaks the app.
✅ Correct: Cache the last known good values and default to a safe OFF.

❌ Mistake 5: Testing only the "on" path.
✅ Correct: Test both states in CI.

---

## 🧠 Tricky Interview Question
The feature flag is OFF in production, yet a database migration shipped with the feature broke production. How can a flag not protect you?

Answer: Flags protect code paths, not shared resources. Migrations, new dependencies, startup code and schema changes run regardless of the flag. Ship migrations in a backward-compatible way (expand/contract), keep risky initialization lazy, and treat the flagged code and its data changes separately.

---

## ⚫ Interview Questions + Answers

Q1: Feature flag vs canary?
A1: A canary routes traffic to a different build; a flag switches behavior inside the same build. They combine well.

Q2: What are the types of flags?
A2: Release flags (short-lived), experiment flags (A/B), ops flags (kill switches), and permission flags (long-lived).

Q3: What is flag debt?
A3: Old flags left in the code, creating dead branches and complexity; fix by removal tickets and expiry dates.

Q4: Where should flag evaluation happen?
A4: On the server for anything sensitive; the client only receives the final decision.

Q5: How does trunk-based development use flags?
A5: Incomplete work merges to main behind OFF flags, so branches stay short and main is always deployable.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want gradual rollouts, A/B tests or a kill switch.
- You practice trunk-based development with frequent deploys.

❌ Avoid when:
- A flag would hide a security fix or add needless complexity to a tiny change.
- You cannot clean flags up; they will pile up.

---

## 📊 Visual Diagram
```
 Deploy (code carries both paths)
        |
        v
  if flag(new_checkout, user)? ----no----> OLD path
        | yes
        v
     NEW path
        ^
        |  flag store (Redis / S3 / AppConfig): 0% -> 10% -> 100%
        |  change takes effect in seconds, NO redeploy
   kill switch: set enabled=false
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Feature flag | Runtime on/off switch for code | code का runtime on/off switch |
| Dark launch | Deployed but hidden | deploy हुआ पर छिपा हुआ |
| Kill switch | Flag to disable quickly | जल्दी बंद करने वाला flag |
| Percentage rollout | Enable for N% of users | N% users के लिए चालू करना |
| Flag debt | Old unused flags | पुराने बेकार flags |

---

## ⚡ 3-Line Summary
English: Flags separate deploying code from releasing features.
Use sticky percentage rollouts and a kill switch, evaluated on the server.
Remove flags after rollout and remember they do not protect migrations.
Hindi: Flags code deploy करने और feature release करने को अलग करते हैं।
Sticky percentage rollout और kill switch रखो, evaluation server पर करो।
Rollout के बाद flags हटाओ और याद रखो ये migrations को नहीं बचाते।

---

## ➡️ Next Topic
**355. Database Migrations in CD** — changing schemas safely inside an automated pipeline.
