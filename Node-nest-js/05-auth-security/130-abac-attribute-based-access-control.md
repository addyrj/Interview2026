# 130. ABAC — Attribute Based Access Control
# हिंदी में: ABAC — Attribute आधारित Access Control

---

## 🔵 Simple Definition (English)
**ABAC (Attribute-Based Access Control)** grants or denies access based on **attributes** of the user, the resource, the action, and the environment (time, location, device) — evaluated by policy rules, instead of just a fixed role. It answers: "Given WHO you are, WHAT you're accessing, WHEN/WHERE/HOW — are you allowed?"

## 🔵 सरल परिभाषा (Hindi)
**ABAC** access को **attributes** के base पर grant/deny करता है — user के attributes, resource के attributes, action, और environment (time, location, device) को policy rules से evaluate करके — सिर्फ fixed role नहीं। यह check करता है: "तुम कौन हो, क्या access कर रहे हो, कब/कहाँ/कैसे — allowed हो या नहीं?"

---

## 🔴 Problem it Solves
RBAC alone breaks down with rules like: "a doctor can view a patient's record ONLY IF they're assigned to that patient's department" or "an employee can approve an expense ONLY IF the amount is under their approval limit AND it's during business hours." These rules depend on dynamic attributes (department match, amount, time), not just a role name. Modeling this in RBAC means creating hundreds of micro-roles (`doctor_cardiology_night_shift`) — a combinatorial explosion. ABAC solves it by writing policies that reference attributes directly, no role explosion needed.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ RBAC से rules नहीं बन पाते जैसे: "doctor patient record देख सके सिर्फ अगर उसी department में assigned है" या "employee expense approve करे सिर्फ अगर amount limit के अंदर है AND business hours में है"। ये dynamic attributes पर depend करते हैं, सिर्फ role नाम पर नहीं। RBAC में ये हज़ारों micro-roles बना देता (combinatorial explosion)। ABAC policies attributes को directly reference करके यह solve करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Identify attributes: Subject (user.department, user.clearanceLevel), Resource (document.department, document.sensitivity), Action (read/write/delete), Environment (time, IP, device)
Step 2 → Write policy rules: `ALLOW read IF user.department === resource.department`
Step 3 → At request time, gather all attributes: user attrs from JWT/DB, resource attrs from DB, env attrs from request (time, IP)
Step 4 → Evaluate policy engine against gathered attributes → returns allow/deny
Step 5 → Enforce decision in middleware before controller runs
Step 6 → Log decision for audit (who accessed what, when, why allowed/denied)

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Attributes identify करो: Subject, Resource, Action, Environment
Step 2 → Policy rules लिखो
Step 3 → Request time पर सभी attributes gather करो
Step 4 → Policy engine evaluate करे attributes पर → allow/deny return करे
Step 5 → Middleware में decision enforce करो controller से पहले
Step 6 → Decision log करो audit के लिए

---

## 🟡 Real World Example
**Razorpay's internal transaction dashboard:** A support agent can view a transaction ONLY IF: `agent.region === transaction.region` AND `transaction.amount < agent.viewLimit` AND `currentTime is within agent's shift hours`. A finance manager can approve a refund ONLY IF `refund.amount <= manager.approvalLimit` AND `refund.status === 'pending'`. These rules change dynamically per transaction — pure RBAC (just checking `role === 'support_agent'`) cannot express this; ABAC evaluates the actual attributes of each transaction against the agent's attributes in real time.

## 🟡 Real Example Hindi mein
**Razorpay का internal transaction dashboard:** Support agent transaction तब ही देख सकता है जब agent की region transaction की region से match करे, amount limit के अंदर हो, और current time agent की shift में हो। ये dynamic rules pure RBAC से नहीं बनते — ABAC हर transaction के actual attributes को real time में evaluate करता है।

---

## 💻 Code Example — Basic

```javascript
// abac-basic.js
// Run with: node abac-basic.js

// ─── 1. SAMPLE DATA: user, resource, environment attributes ─────────────────
const user = { id: 1, department: 'cardiology', clearanceLevel: 3 };
const document = { id: 101, department: 'cardiology', sensitivity: 2 };
const env = { currentHour: 14 }; // 2 PM

// ─── 2. SIMPLE POLICY FUNCTION ────────────────────────────────────────────────
function canReadDocument(user, document, env) {
  // Rule 1: same department
  const sameDept = user.department === document.department;
  // Rule 2: clearance level must be >= sensitivity
  const enoughClearance = user.clearanceLevel >= document.sensitivity;
  // Rule 3: only during business hours (9 AM - 6 PM)
  const businessHours = env.currentHour >= 9 && env.currentHour < 18;

  return sameDept && enoughClearance && businessHours; // ALL must be true
}

// ─── 3. TEST ───────────────────────────────────────────────────────────────────
console.log(canReadDocument(user, document, env));  // true

const outsideHours = { currentHour: 22 };
console.log(canReadDocument(user, document, outsideHours));  // false (after hours)

const wrongDept = { ...document, department: 'neurology' };
console.log(canReadDocument(user, wrongDept, env));  // false (dept mismatch)
```

## 💻 Code Example — Advanced

```javascript
// abac-advanced.js — Policy engine with named, composable rules

// ─── 1. POLICY DEFINITIONS (declarative, reusable) ───────────────────────────
const policies = {
  'document:read': [
    {
      name: 'same-department',
      check: (ctx) => ctx.user.department === ctx.resource.department,
    },
    {
      name: 'sufficient-clearance',
      check: (ctx) => ctx.user.clearanceLevel >= ctx.resource.sensitivity,
    },
    {
      name: 'business-hours',
      check: (ctx) => ctx.env.currentHour >= 9 && ctx.env.currentHour < 18,
    },
  ],
  'refund:approve': [
    {
      name: 'within-approval-limit',
      check: (ctx) => ctx.resource.amount <= ctx.user.approvalLimit,
    },
    {
      name: 'is-pending',
      check: (ctx) => ctx.resource.status === 'pending',
    },
  ],
  'transaction:view': [
    {
      // admin bypasses all other rules for this action
      name: 'admin-override',
      check: (ctx) => ctx.user.role === 'admin',
      isOverride: true,
    },
    {
      name: 'same-region',
      check: (ctx) => ctx.user.region === ctx.resource.region,
    },
    {
      name: 'within-view-limit',
      check: (ctx) => ctx.resource.amount < ctx.user.viewLimit,
    },
  ],
};

// ─── 2. POLICY EVALUATION ENGINE ──────────────────────────────────────────────
function evaluate(action, ctx) {
  const rules = policies[action];
  if (!rules) return { allowed: false, reason: `No policy defined for ${action}` };

  // If any override rule passes, allow immediately (e.g., admin bypass)
  const overrideRule = rules.find((r) => r.isOverride && r.check(ctx));
  if (overrideRule) {
    return { allowed: true, reason: `Override: ${overrideRule.name}` };
  }

  // Otherwise ALL non-override rules must pass
  const normalRules = rules.filter((r) => !r.isOverride);
  for (const rule of normalRules) {
    if (!rule.check(ctx)) {
      return { allowed: false, reason: `Failed rule: ${rule.name}` };
    }
  }
  return { allowed: true, reason: 'All rules passed' };
}

// ─── 3. USAGE ──────────────────────────────────────────────────────────────────
const ctx1 = {
  user: { id: 5, role: 'support_agent', region: 'IN', viewLimit: 50000 },
  resource: { id: 900, region: 'IN', amount: 20000 },
  env: { currentHour: 11 },
};
console.log(evaluate('transaction:view', ctx1));
// { allowed: true, reason: 'All rules passed' }

const ctx2 = {
  user: { id: 6, role: 'support_agent', region: 'IN', viewLimit: 50000 },
  resource: { id: 901, region: 'US', amount: 20000 },  // region mismatch
  env: { currentHour: 11 },
};
console.log(evaluate('transaction:view', ctx2));
// { allowed: false, reason: 'Failed rule: same-region' }

module.exports = { evaluate, policies };
```

---

## 🟠 Express.js Integration

```javascript
// server.js
const express = require('express');
const { evaluate } = require('./abac-advanced');

const app = express();
app.use(express.json());

// Generic ABAC enforcement middleware factory
function enforcePolicy(action, resourceLoader) {
  return async (req, res, next) => {
    try {
      const resource = await resourceLoader(req);  // fetch resource attributes from DB
      const ctx = {
        user: req.user,        // from auth middleware: { id, role, department, region, ... }
        resource,
        env: { currentHour: new Date().getHours(), ip: req.ip },
      };

      const decision = evaluate(action, ctx);
      // Audit log: critical for ABAC since rules are dynamic
      console.log(`[ABAC] user=${req.user.id} action=${action} allowed=${decision.allowed} reason="${decision.reason}"`);

      if (!decision.allowed) {
        return res.status(403).json({ error: 'Forbidden', reason: decision.reason });
      }
      req.resource = resource;  // pass loaded resource to controller, avoid re-fetching
      next();
    } catch (err) {
      res.status(500).json({ error: 'Policy evaluation failed' });
    }
  };
}

// View a transaction — ABAC policy checks region + view limit + admin override
app.get(
  '/transactions/:id',
  authenticate,
  enforcePolicy('transaction:view', async (req) => {
    return Transaction.findById(req.params.id);  // loads { region, amount, ... }
  }),
  (req, res) => {
    res.json(req.resource);  // already loaded by enforcePolicy
  }
);

// Approve a refund — ABAC policy checks approval limit + pending status
app.post(
  '/refunds/:id/approve',
  authenticate,
  enforcePolicy('refund:approve', async (req) => Refund.findById(req.params.id)),
  async (req, res) => {
    req.resource.status = 'approved';
    await req.resource.save();
    res.json({ message: 'Refund approved' });
  }
);

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Evaluating policy using stale/client-supplied attributes
```javascript
// WRONG: trusting attributes sent by the client in request body
const allowed = evaluate('refund:approve', {
  user: req.body.user,        // attacker can fake viewLimit/approvalLimit!
  resource: req.body.resource,
});

// CORRECT: load trusted attributes server-side from DB/JWT
const allowed = evaluate('refund:approve', {
  user: req.user,                              // from verified JWT
  resource: await Refund.findById(req.params.id), // from DB, not client input
});
```

❌ Mistake 2: No audit logging for policy decisions
```javascript
// Wrong: silent allow/deny — impossible to debug "why was this denied?" later
if (!decision.allowed) return res.status(403).end();

// Right: always log decision + reason for compliance/debugging
console.log(`[ABAC] user=${req.user.id} action=${action} allowed=${decision.allowed} reason="${decision.reason}"`);
if (!decision.allowed) return res.status(403).json({ error: decision.reason });
```

---

## 🧠 Tricky Interview Question

```javascript
const rules = [
  { name: 'r1', check: (ctx) => ctx.user.age > 18 },
  { name: 'r2', check: (ctx) => { throw new Error('DB down'); } },
];

for (const rule of rules) {
  if (!rule.check({ user: { age: 20 } })) {
    console.log('denied by', rule.name);
  }
}
console.log('reached end');
```
Answer: `r1` passes (`20 > 18` is true, so the `if` is false, nothing logged). Then `r2.check()` throws an uncaught `Error('DB down')` — this crashes the loop immediately. **"reached end" is never printed**, and if this were inside an Express route handler without try/catch, the process could crash (unhandled exception) or Express would return a generic 500 depending on whether it's sync or wrapped in a promise. Lesson: ABAC policy checks that touch the DB or external calls MUST be wrapped in try/catch — a single failing rule shouldn't crash the whole request or leak details.

---

## ⚫ Interview Questions + Answers

Q1: What's the fundamental difference between RBAC and ABAC?
A1: RBAC: access decision = f(role). Fixed, coarse-grained, easy to audit, but creates role explosion for complex conditional rules. ABAC: access decision = f(subject attributes, resource attributes, action, environment attributes). Fine-grained, flexible, can express conditions like "only during business hours" or "only if same department" without creating new roles — but harder to audit/visualize since rules are code/policy, not a simple role list.

Q2: Can RBAC and ABAC be combined?
A2: Yes — this is very common in production ("hybrid RBAC"). Use RBAC for broad access tiers (admin/owner/customer), then layer ABAC-style attribute checks (ownership, region, time, amount limits) on top for fine-grained control, as shown in the `canEditRestaurant` + `authorize` pattern. This gives you RBAC's simplicity for coarse decisions and ABAC's flexibility where needed.

Q3: What are the four categories of attributes in ABAC?
A3: (1) **Subject attributes** — who is requesting (user.department, user.clearanceLevel, user.role). (2) **Resource attributes** — what's being accessed (document.sensitivity, document.owner). (3) **Action attributes** — what operation (read, write, delete, approve). (4) **Environment attributes** — context of the request (time of day, IP address, device type, geolocation).

Q4: What is a policy engine, and name a real-world tool used for ABAC?
A4: A policy engine evaluates attribute-based rules against a request context and returns allow/deny. Real tools: **OPA (Open Policy Agent)** with its Rego language — language-agnostic, used widely in Kubernetes and microservices for authorization; **Casbin** — a Node.js/multi-language authorization library supporting RBAC, ABAC, and custom models; AWS IAM policies are also attribute-based (condition keys like `aws:RequestedRegion`).

Q5: How do you handle performance when ABAC policies require DB lookups for every request?
A5: Each policy evaluation may need resource attributes from DB (e.g., document's department) — adding latency per request. Mitigations: (1) Cache frequently accessed resource attributes (Redis) with short TTL and invalidate on update. (2) Batch-load attributes needed for the request in one query instead of N+1 lookups. (3) For hot paths, denormalize critical attributes (store `department` directly on related documents to avoid joins). (4) Use a dedicated policy decision point (PDP) service with its own cache, separate from the main app, for complex organizations.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Access rules depend on dynamic context: ownership, time, location, amount thresholds, department matching.
- RBAC alone would require too many specialized roles (role explosion).
- Compliance requires fine-grained, auditable, context-aware access decisions (healthcare, fintech).

❌ Avoid when:
- Your access model is genuinely simple (few roles, static permissions) — ABAC adds unnecessary complexity and performance overhead.
- You can't afford the latency of fetching multiple attributes per request in very high-throughput paths.

---

## 📊 Visual Diagram

```
ABAC DECISION FLOW:
──────────────────────────────────────────────────────────

  Request: GET /transactions/900
       │
       ▼
  Gather attributes:
    Subject  → { role: 'support_agent', region: 'IN', viewLimit: 50000 }
    Resource → { region: 'IN', amount: 20000 }   (fetched from DB)
    Action   → 'transaction:view'
    Env      → { currentHour: 11 }
       │
       ▼
  Policy Engine evaluates rules:
    ✓ same-region        (IN === IN)
    ✓ within-view-limit  (20000 < 50000)
       │
       ▼
  Decision: ALLOW ✅ → log → next() → controller runs

  (If resource.region = 'US')
       ▼
  ✗ same-region fails → DENY ❌ → 403 Forbidden
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Attribute | A property of subject/resource/env | Subject/resource/env की property |
| Policy | A rule combining attribute checks | Attribute checks को combine करने वाला rule |
| Policy engine | Evaluates policies against context | Context पर policies evaluate करता है |
| PDP (Policy Decision Point) | Component that makes allow/deny decision | Allow/deny decision लेने वाला component |
| Override rule | Rule that bypasses other checks | बाकी checks को bypass करने वाला rule |
| Context | All gathered attributes for a request | Request के सभी gathered attributes |

---

## ⚡ 3-Line Summary
English:
1. ABAC decides access using dynamic attributes of subject, resource, action, and environment — not just a fixed role.
2. Implement as named policy rules that are all evaluated against a request context, with optional override rules (like admin bypass).
3. Always load attributes server-side (JWT/DB), never trust client-supplied attributes, and always audit-log allow/deny decisions.

Hindi:
1. ABAC subject, resource, action, environment के dynamic attributes से access decide करता है — सिर्फ fixed role नहीं।
2. Named policy rules बनाओ जो request context पर evaluate हों, override rules (जैसे admin bypass) के साथ।
3. Attributes हमेशा server-side से लोड करो, client से trust मत करो, decisions audit-log करो।

---

## ➡️ Next Topic
**131. CORS — Complete Guide** — Cross-origin requests को browser कैसे control करता है और Express में configure करना।
