# 142. OWASP Top 10 for Node.js
# हिंदी में: Node.js के लिए OWASP Top 10

---

## 🔵 Simple Definition (English)
The **OWASP Top 10** is a globally recognized list of the most critical web application security risks, published by the Open Web Application Security Project. Applied to Node.js, it's a checklist mapping each risk (broken access control, injection, cryptographic failures, etc.) to Node-specific causes and fixes — the industry-standard baseline for secure development.

## 🔵 सरल परिभाषा (Hindi)
**OWASP Top 10** सबसे critical web application security risks की globally recognized list है, Open Web Application Security Project द्वारा publish की गई। Node.js पर apply करने पर, यह हर risk को Node-specific causes और fixes से map करने वाली checklist है — secure development का industry-standard baseline।

---

## 🔴 Problem it Solves
Security is vast and easy to get lost in — developers need a prioritized, evidence-based list of what ACTUALLY causes most real-world breaches, not an endless theoretical list. OWASP surveys real incident data across thousands of applications to rank the most impactful, most common vulnerability categories. For Node.js teams, having this as a structured checklist during code review and architecture design ensures the highest-impact risks are addressed first, rather than security effort being scattered randomly.

## 🔴 यह क्यों बना? (Hindi)
Security बहुत vast है और इसमें खो जाना आसान है — developers को एक prioritized, evidence-based list चाहिए कि वास्तव में कौन सी चीज़ें ज़्यादातर real-world breaches का कारण बनती हैं। OWASP हज़ारों applications के real incident data को survey करके सबसे impactful vulnerability categories को rank करता है। Node.js teams के लिए यह structured checklist code review और architecture design में सबसे पहले सबसे बड़े risks को address करने में मदद करती है।

---

## 🟢 How it Works — Step by Step

Step 1 → **A01 Broken Access Control**: missing/incorrect authorization checks → fix with RBAC/ABAC middleware on every protected route (topics 129-130)
Step 2 → **A02 Cryptographic Failures**: weak hashing (MD5 for passwords), hardcoded secrets, missing HTTPS → fix with bcrypt, env vars/secrets manager, TLS (topics 121, 138-141)
Step 3 → **A03 Injection**: SQL/NoSQL/command injection via unsanitized input → fix with parameterized queries, input validation (topics 134, 137)
Step 4 → **A04 Insecure Design**: missing threat modeling, no rate limiting on sensitive flows → fix by designing security requirements upfront, not bolting on later
Step 5 → **A05 Security Misconfiguration**: default credentials, verbose error messages leaking stack traces, missing security headers → fix with Helmet, proper error handling, hardened configs
Step 6 → **A06 Vulnerable and Outdated Components**: outdated npm packages with known CVEs → fix with `npm audit`, Dependabot, regular dependency updates
Step 7 → **A07 Identification and Authentication Failures**: weak password policies, no MFA, session fixation → fix with bcrypt, strong JWT practices, rate-limited login
Step 8 → **A08 Software and Data Integrity Failures**: unsigned/unverified updates, insecure deserialization → fix by verifying package integrity (lockfiles, checksums), avoiding `eval`/unsafe deserialization
Step 9 → **A09 Security Logging and Monitoring Failures**: no logs of auth failures/suspicious activity → fix with structured logging + alerting on anomalies
Step 10 → **A10 Server-Side Request Forgery (SSRF)**: server fetches attacker-controlled URLs, hitting internal services → fix by validating/whitelisting outbound URLs

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **A01 Broken Access Control** — missing authorization checks, RBAC/ABAC से fix करो
Step 2 → **A02 Cryptographic Failures** — weak hashing, hardcoded secrets, bcrypt/TLS से fix करो
Step 3 → **A03 Injection** — SQL/NoSQL injection, parameterized queries से fix करो
Step 4 → **A04 Insecure Design** — upfront security design से fix करो
Step 5 → **A05 Security Misconfiguration** — Helmet, proper config से fix करो
Step 6 → **A06 Vulnerable Components** — `npm audit`, dependency updates से fix करो
Step 7 → **A07 Auth Failures** — bcrypt, strong JWT, rate limiting से fix करो
Step 8 → **A08 Integrity Failures** — lockfiles, checksums verify करो
Step 9 → **A09 Logging Failures** — structured logging + alerting से fix करो
Step 10 → **A10 SSRF** — outbound URLs whitelist करो

---

## 🟡 Real World Example
**A fintech startup's security audit (Razorpay-style company):** An external pentest finds: (A01) an internal admin API endpoint missing an `authorize('admin')` check — any logged-in user could access it; (A03) a legacy search endpoint building SQL via string concatenation; (A06) a 2-year-old `lodash` version with a known prototype-pollution CVE; (A09) no logging on failed login attempts, making a brute-force attack invisible until customers complained. Each finding maps directly to an OWASP category, letting the security team prioritize fixes by severity (A01 and A03 fixed immediately — direct data exposure risk; A06 scheduled in next sprint; A09 added as a new logging requirement).

## 🟡 Real Example Hindi mein
**Fintech startup का security audit:** External pentest में पाया जाता है — admin endpoint पर authorization check missing (A01), legacy search endpoint में SQL string concatenation (A03), outdated `lodash` में known CVE (A06), failed login attempts पर कोई logging नहीं (A09)। हर finding OWASP category से map होती है, severity के अनुसार prioritize होती है।

---

## 💻 Code Example — Basic

```javascript
// owasp-basic.js — demonstrating A03 (Injection) and A06 (Vulnerable Components) checks
// Run with: node owasp-basic.js

// ─── A03: INJECTION — vulnerable vs safe pattern ─────────────────────────────
function buildUnsafeQuery(userId) {
  // VULNERABLE: string concatenation
  return `SELECT * FROM orders WHERE user_id = ${userId}`;
}

function buildSafeQuery() {
  // SAFE: parameterized placeholder, value bound separately
  return { sql: 'SELECT * FROM orders WHERE user_id = ?', params: [] };
}

console.log('Unsafe:', buildUnsafeQuery("1 OR 1=1"));  // injectable!
console.log('Safe template:', buildSafeQuery());

// ─── A06: CHECKING FOR VULNERABLE DEPENDENCIES ───────────────────────────────
// Run this in terminal (not JS), part of CI pipeline:
//   npm audit                  → lists known vulnerabilities in dependencies
//   npm audit fix               → auto-fixes what it safely can
//   npm audit --audit-level=high --json > audit-report.json   → for CI gating

// Programmatically checking package.json for outdated/risky patterns (simplified):
const fs = require('fs');
function checkForRiskyDependencies(packageJsonPath) {
  const pkg = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  const allDeps = { ...pkg.dependencies, ...pkg.devDependencies };
  const KNOWN_RISKY = ['request'];  // e.g., 'request' package is deprecated/unmaintained
  const risky = Object.keys(allDeps).filter((dep) => KNOWN_RISKY.includes(dep));
  if (risky.length) console.log('⚠️ Risky/deprecated dependencies found:', risky);
  return risky;
}
```

## 💻 Code Example — Advanced

```javascript
// owasp-advanced.js — A01 (Access Control) + A10 (SSRF) protections combined

const { URL } = require('url');
const dns = require('dns').promises;

// ─── A01: BROKEN ACCESS CONTROL — ownership + role check middleware ─────────
function authorizeOrderAccess() {
  return async (req, res, next) => {
    const order = await Order.findById(req.params.orderId);
    if (!order) return res.status(404).json({ error: 'Order not found' });

    // Admins can access any order; customers only their own
    const isOwner = String(order.customerId) === String(req.user.id);
    const isAdmin = req.user.role === 'admin';

    if (!isOwner && !isAdmin) {
      return res.status(403).json({ error: 'Forbidden: not your order' });
    }
    req.order = order;
    next();
  };
}

// ─── A10: SSRF PREVENTION — validating user-supplied URLs before fetching ───
const BLOCKED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '169.254.169.254'];  // incl. cloud metadata endpoint!
const PRIVATE_IP_RANGES = [/^10\./, /^172\.(1[6-9]|2\d|3[01])\./, /^192\.168\./];

async function isUrlSafeForFetch(urlString) {
  let parsed;
  try {
    parsed = new URL(urlString);
  } catch {
    return false;  // malformed URL
  }

  if (parsed.protocol !== 'https:') return false;              // only allow HTTPS
  if (BLOCKED_HOSTS.includes(parsed.hostname)) return false;    // block localhost/metadata endpoints

  // Resolve hostname to IP and check it's not a private/internal address
  // (prevents DNS rebinding tricks where a public domain resolves to an internal IP)
  try {
    const { address } = await dns.lookup(parsed.hostname);
    if (PRIVATE_IP_RANGES.some((range) => range.test(address))) return false;
  } catch {
    return false;  // DNS resolution failed — treat as unsafe
  }

  return true;
}

// Example usage: a "fetch webhook preview" feature that's a classic SSRF target
async function fetchUserProvidedUrl(urlString) {
  const safe = await isUrlSafeForFetch(urlString);
  if (!safe) {
    throw new Error('URL not allowed: points to internal/private network or invalid scheme');
  }
  const response = await fetch(urlString, { redirect: 'manual' });  // don't auto-follow redirects!
  return response;
}

module.exports = { authorizeOrderAccess, isUrlSafeForFetch, fetchUserProvidedUrl };
```

---

## 🟠 Express.js Integration

```javascript
// server.js — Express app wiring OWASP-aligned middleware stack
const express = require('express');
const helmet = require('helmet');           // A05: security headers
const rateLimit = require('express-rate-limit');  // A07: brute-force protection
const { authorizeOrderAccess, fetchUserProvidedUrl } = require('./owasp-advanced');

const app = express();

app.use(helmet());                // A02/A05: secure headers, HTTPS enforcement support
app.use(express.json({ limit: '1mb' }));  // A04: limit payload size (DoS mitigation)

// A07: rate limit auth endpoints specifically
const authLimiter = rateLimit({ windowMs: 15 * 60 * 1000, max: 5 });
app.post('/auth/login', authLimiter, (req, res) => res.json({ message: 'checked' }));

// A01: access control enforced per-resource, not just per-role
app.get('/orders/:orderId', authenticate, authorizeOrderAccess(), (req, res) => {
  res.json(req.order);  // already authorized + loaded by middleware
});

// A10: SSRF-safe webhook URL testing feature
app.post('/webhooks/test', authenticate, async (req, res) => {
  try {
    const response = await fetchUserProvidedUrl(req.body.url);
    res.json({ status: response.status });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// A09: centralized error handler that logs but never leaks internals to clients
app.use((err, req, res, next) => {
  console.error(`[${new Date().toISOString()}] Error:`, err.stack);  // full detail server-side
  res.status(500).json({ error: 'Internal server error' });          // generic client-facing message
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Treating OWASP Top 10 as a one-time checklist instead of ongoing practice
```javascript
// WRONG: "we did a security review last year, we're covered"
// New code ships weekly without any re-check against these categories

// CORRECT: integrate automated checks into CI/CD continuously
// package.json scripts:
//   "audit": "npm audit --audit-level=high",
//   "lint:security": "eslint --plugin security ."
// Run on every PR, not just annually
```

❌ Mistake 2: Only checking role, ignoring ownership (incomplete A01 fix)
```javascript
// WRONG: role check alone, missing resource-level ownership check
app.get('/orders/:id', authenticate, authorize('customer'), async (req, res) => {
  const order = await Order.findById(req.params.id);
  res.json(order);  // ANY customer can view ANY other customer's order!
});

// CORRECT: combine role check with ownership verification
app.get('/orders/:id', authenticate, authorize('customer'), authorizeOrderAccess(), (req, res) => {
  res.json(req.order);  // verified to belong to this customer (or admin)
});
```

---

## 🧠 Tricky Interview Question

```javascript
// A "webhook URL preview" feature fetches whatever URL the user provides:
app.post('/preview', async (req, res) => {
  const response = await fetch(req.body.url);
  const text = await response.text();
  res.send(text);
});
// User submits: http://169.254.169.254/latest/meta-data/iam/security-credentials/
// What category of OWASP risk is this, and what can go wrong?
```
Answer: This is **A10: Server-Side Request Forgery (SSRF)**. `169.254.169.254` is the AWS (and other cloud providers') **instance metadata endpoint**, which on many cloud setups returns the server's own IAM credentials WITHOUT any authentication (it's only accessible from inside the instance — which is exactly what this server-side fetch does on the attacker's behalf). The attacker uses the server as a proxy to reach an internal-only endpoint it couldn't reach directly from the internet, potentially exfiltrating the cloud instance's IAM role credentials and gaining further access to cloud resources. Fix: validate/whitelist URLs before fetching (block private IP ranges and the metadata IP specifically), as shown in `isUrlSafeForFetch`.

---

## ⚫ Interview Questions + Answers

Q1: What changed in the OWASP Top 10 between the 2017 and 2021 editions that's relevant to Node.js developers?
A1: "Broken Access Control" moved to #1 (from #5), reflecting how common and impactful authorization bugs are in real breaches. "Insecure Deserialization" was folded into the broader "Software and Data Integrity Failures" category. "Using Components with Known Vulnerabilities" was expanded to include supply-chain risks more broadly as "Vulnerable and Outdated Components" — highly relevant to Node.js given its heavy reliance on npm packages (often hundreds of transitive dependencies per project). "Server-Side Request Forgery" was added as its own new category (#10), reflecting its rising prevalence in cloud-hosted apps.

Q2: How does `npm audit` help address OWASP's "Vulnerable and Outdated Components" risk, and what are its limitations?
A2: `npm audit` scans your `package-lock.json` against a vulnerability database, flagging known CVEs in your dependency tree with severity levels, and can auto-fix some issues via `npm audit fix`. Limitations: it only catches PUBLICLY KNOWN vulnerabilities (zero-days aren't flagged until disclosed), doesn't catch LOGIC vulnerabilities in dependencies, auto-fix can sometimes break compatibility (major version bumps), and it doesn't replace actually reading changelogs/testing after updates. CI pipelines commonly gate merges on `npm audit --audit-level=high` failing the build.

Q3: Why is "Security Logging and Monitoring Failures" (A09) often under-prioritized, and why does it matter?
A3: Logging/monitoring doesn't prevent an attack directly — it's about DETECTION and RESPONSE, which feels less urgent than fixing an active vulnerability, so teams often skip it. But without logs of failed logins, unusual access patterns, or error spikes, a breach can go undetected for months (the average breach detection time across industry reports is often measured in MONTHS, not days) — by which point damage is far more extensive. Good logging (structured, centralized, alerted) turns "we got breached and didn't know for 6 months" into "we got an alert within minutes and contained it."

Q4: Give an example of "Insecure Design" (A04) that's distinct from an implementation bug.
A4: A password reset flow that sends the NEW password directly via email (rather than a time-limited reset link) is an insecure DESIGN choice — even if implemented "correctly" (no bugs), the fundamental approach is flawed (email is often not encrypted end-to-end, and a permanent password sent in plaintext is a standing risk). Another example: a multi-step checkout flow with no server-side validation that step 2 was actually completed before step 3, relying only on client-side flow control — an attacker can skip steps by calling APIs directly. These aren't "bugs" to patch; they require redesigning the flow with security built in from the start.

Q5: How would you prioritize fixing OWASP Top 10 findings from a security audit with limited engineering time?
A5: Prioritize by (1) actual exploitability (is there a known, working proof-of-concept, or just theoretical risk), (2) impact/blast radius (data exposure for ALL users vs. one edge case), and (3) exposure (internet-facing vs. internal-only). Typically: Broken Access Control and Injection vulnerabilities on internet-facing endpoints get fixed FIRST (direct data breach risk), followed by Cryptographic Failures (weak hashing, exposed secrets), then Security Misconfiguration and Vulnerable Components (often quick wins via config/dependency updates), with Logging/Monitoring improvements planned as ongoing infrastructure work rather than an urgent "stop the bleeding" fix.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Conducting security code reviews, architecture reviews, or onboarding new engineers to security practices.
- Setting up CI/CD security gates (dependency scanning, SAST tools) — map findings to OWASP categories for prioritization.

❌ Avoid when:
- Treating it as EXHAUSTIVE — OWASP Top 10 covers the most common/impactful risks, not every possible vulnerability; dedicated threat modeling is still needed for app-specific risks beyond this general list.

---

## 📊 Visual Diagram

```
OWASP TOP 10 (2021) MAPPED TO NODE.JS DEFENSES:
──────────────────────────────────────────────────────────

  A01 Broken Access Control      → RBAC/ABAC + ownership checks
  A02 Cryptographic Failures     → bcrypt, HTTPS/TLS, secrets manager
  A03 Injection                  → parameterized queries, input validation
  A04 Insecure Design            → threat modeling, secure-by-design flows
  A05 Security Misconfiguration  → Helmet, hardened configs, no verbose errors
  A06 Vulnerable Components      → npm audit, dependency updates, lockfiles
  A07 Auth Failures              → bcrypt, rate limiting, strong session mgmt
  A08 Data Integrity Failures    → signed packages, safe deserialization
  A09 Logging/Monitoring Failures→ structured logs, alerting on anomalies
  A10 SSRF                       → URL whitelisting, block internal IP ranges
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OWASP | Organization publishing web security standards | Web security standards publish करने वाली organization |
| SSRF | Server tricked into fetching internal/malicious URLs | Server को internal URL fetch करवाना |
| CVE | Publicly cataloged known vulnerability | Publicly catalog की गई known vulnerability |
| Threat modeling | Proactively identifying potential attack vectors | Proactively attack vectors identify करना |
| SAST | Static analysis security testing (scans source code) | Source code scan करने वाला static analysis |
| Blast radius | Extent of damage if a vulnerability is exploited | Vulnerability exploit होने पर damage की extent |

---

## ⚡ 3-Line Summary
English:
1. OWASP Top 10 is the industry-standard, evidence-based checklist of the most critical web app security risks, applicable directly to Node.js apps.
2. Each category (Broken Access Control, Injection, SSRF, etc.) maps to concrete Node.js fixes: RBAC middleware, parameterized queries, Helmet, npm audit, URL whitelisting.
3. Use it as an ongoing practice in code review and CI/CD, prioritizing fixes by exploitability and blast radius, not as a one-time checklist.

Hindi:
1. OWASP Top 10 सबसे critical web app security risks की industry-standard checklist है, Node.js apps पर directly applicable।
2. हर category concrete Node.js fixes से map होती है — RBAC middleware, parameterized queries, Helmet, npm audit।
3. इसे ongoing practice बनाओ code review और CI/CD में, exploitability और blast radius से prioritize करो।

---

## ➡️ Next Topic
**143. Connecting MySQL with Node.js** — mysql2 driver से database connection setup करना।
