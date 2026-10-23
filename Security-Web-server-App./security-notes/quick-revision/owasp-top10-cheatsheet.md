# OWASP Top 10 — Quick Revision Cheatsheet
# 5+ YOE Security Interview — Must Know Cold

---

## 🎯 OWASP Top 10 (2021 Edition)

```
A01 — Broken Access Control       ← #1 most common
A02 — Cryptographic Failures      ← (formerly Sensitive Data Exposure)
A03 — Injection                   ← SQL, NoSQL, OS, LDAP
A04 — Insecure Design             ← Missing security in architecture
A05 — Security Misconfiguration   ← Default creds, debug on, S3 public
A06 — Vulnerable Components       ← npm packages, dependencies
A07 — Auth Failures               ← Weak passwords, no MFA, session issues
A08 — Software Integrity          ← Supply chain, unsigned code
A09 — Logging Failures            ← No audit trails, not monitoring
A10 — SSRF                        ← Server fetches attacker-controlled URLs
```

---

## 🔴 A01 — Broken Access Control
```
What: User can access data/functions they shouldn't
Examples:
  - GET /api/orders/1234 → change to /api/orders/1235 → other user's order (IDOR)
  - POST /admin/deleteUser without admin check
  - Directory traversal: /files/../../etc/passwd

Fix:
  ✅ Check authorization on EVERY request (not just login)
  ✅ Backend validates that resource belongs to requesting user
  ✅ Default DENY — whitelist access, don't blacklist
  ✅ Log all access control failures, alert on spikes

Code:
// ❌ Vulnerable: trusts user-supplied ID
app.get('/orders/:id', auth, async (req, res) => {
  const order = await Order.findById(req.params.id);  // anyone can access!
  res.json(order);
});

// ✅ Secure: validates ownership
app.get('/orders/:id', auth, async (req, res) => {
  const order = await Order.findOne({
    _id: req.params.id,
    userId: req.user.id   // must belong to requesting user!
  });
  if (!order) return res.status(404).json({ error: 'Not found' });
  res.json(order);
});
```

---

## 🔴 A02 — Cryptographic Failures
```
What: Sensitive data exposed due to weak/missing encryption
Examples:
  - Passwords stored in plaintext or MD5
  - HTTP (not HTTPS) for login pages
  - Weak TLS (TLS 1.0/1.1)
  - Credit cards in logs

Fix:
  ✅ bcrypt/Argon2 for passwords (not MD5/SHA1)
  ✅ HTTPS everywhere, HSTS header
  ✅ Encrypt PII at rest (AES-256)
  ✅ Never log passwords, tokens, card numbers

bcrypt cost factor: 12 (2024 recommendation)
const hash = await bcrypt.hash(password, 12);  // ~250ms — intentionally slow
```

---

## 🔴 A03 — Injection
```
Types: SQL, NoSQL, OS command, LDAP, XPath

SQL Injection — most common:
  ❌ "SELECT * FROM users WHERE id='" + req.params.id + "'"
  ✅ db.execute("SELECT * FROM users WHERE id = ?", [req.params.id])

NoSQL Injection (MongoDB):
  ❌ User.find({ username: req.body.username })
     // username: { $gt: "" } → returns ALL users!
  ✅ const { username } = sanitize(req.body)
     // or use mongoose schema validation (type: String enforced)

OS Command Injection:
  ❌ exec(`convert ${req.body.filename}.png to pdf`)
  ✅ Use library (sharp, pdf-lib) instead of shell commands
  ✅ If shell needed: whitelist filenames, use execFile (no shell expansion)

Fix summary:
  ✅ Parameterized queries always
  ✅ ORMs with type-safe queries
  ✅ Input validation (whitelist)
  ✅ Least privilege DB user
```

---

## 🔴 A04 — Insecure Design
```
What: Missing security controls in architecture, not implementation bugs
Examples:
  - No rate limiting designed for login (brute force possible by design)
  - Security questions for account recovery (easily guessable)
  - Sending sensitive data in URL parameters (appears in logs/history)

Fix:
  ✅ Threat modeling during design phase
  ✅ Secure design patterns (defense in depth, fail securely, least privilege)
  ✅ Security review before implementation

Key principles:
  - Defense in depth: multiple layers, no single point of failure
  - Fail securely: default DENY, not default allow
  - Least privilege: minimum access needed
  - Separation of duties: 4 eyes for sensitive operations
```

---

## 🔴 A05 — Security Misconfiguration
```
What: Insecure default settings left unchanged
Examples:
  - Default credentials (admin/admin, mongo with no auth)
  - Debug mode in production (stack traces, verbose errors)
  - S3 bucket with public read
  - Open cloud firewall ports
  - X-Powered-By: Express (tech stack fingerprinting)
  - Error messages revealing internal paths

Fix:
  ✅ helmet() to set security headers, hide server info
  ✅ Different configs per environment (no debug in production)
  ✅ Regular security scanning (OWASP ZAP, Trivy for containers)
  ✅ IaC security scanning (checkov, tfsec for Terraform)
  ✅ Principle of least privilege for cloud IAM

Error messages:
  ❌ res.status(500).json({ error: err.stack })  // exposes internals
  ✅ res.status(500).json({ error: 'Internal server error' })  // log internally
```

---

## 🔴 A06 — Vulnerable and Outdated Components
```
What: Using dependencies with known CVEs
Examples:
  - log4shell (log4j 2021): CVSS 10.0 — remote code execution via log message
  - lodash prototype pollution
  - old express-fileupload with path traversal

Fix:
  ✅ npm audit / yarn audit in CI/CD pipeline
  ✅ Dependabot / Renovate for automatic update PRs
  ✅ Snyk / OWASP Dependency-Check for CVE scanning
  ✅ Lock file (package-lock.json) committed and checked
  ✅ Remove unused dependencies

Commands:
npm audit           # check for vulnerabilities
npm audit fix       # auto-fix non-breaking updates
npm audit fix --force  # force fix (may break — test first)
npx snyk test       # Snyk scan

npm outdated        # see outdated packages
npm update          # update within semver range
```

---

## 🔴 A07 — Identification and Authentication Failures
```
What: Weak auth, credential issues, session problems
Examples:
  - Weak passwords allowed
  - No brute force protection
  - Storing passwords in plaintext or reversible encryption
  - Session tokens that don't expire
  - JWT with weak secret (see 097)

Fix:
  ✅ Strong password policy (length > complexity)
  ✅ Multi-factor authentication (TOTP, WebAuthn)
  ✅ Rate limiting on login (5 attempts / 15 min)
  ✅ Secure session management (httpOnly, SameSite, short expiry)
  ✅ bcrypt/Argon2 (not MD5/SHA1/plain)

MFA implementation:
  - TOTP: speakeasy/otplib — 6-digit code, 30s window
  - WebAuthn: passkey — phishing-resistant, no password
  - SMS OTP: weakest — SIM swap attacks possible
```

---

## 🔴 A08 — Software and Data Integrity Failures
```
What: Code and infrastructure not verified for integrity
Examples:
  - Using npm packages without integrity check
  - Auto-update pipeline that downloads from HTTP (not HTTPS)
  - Unverified Docker images
  - Deserialization of untrusted data (Java ObjectInputStream)

Fix:
  ✅ Subresource Integrity (SRI) for CDN scripts:
     <script src="https://cdn.example.com/lib.js"
             integrity="sha384-HASHHERE"
             crossorigin="anonymous"></script>
  ✅ Package signature verification (npm --audit)
  ✅ Signed Docker images (Docker Content Trust)
  ✅ Verified CI/CD pipeline (GitHub Actions pinned to commit hash)
  ✅ SAST (static analysis) in CI

JavaScript deserialization:
  ❌ eval(userInput), Function(userInput)()
  ❌ YAML.load() (use YAML.safeLoad())
  ❌ node-serialize with untrusted data
  ✅ JSON.parse() for user data (safe)
  ✅ validate schema after parse (ajv, zod)
```

---

## 🔴 A09 — Security Logging and Monitoring Failures
```
What: No audit trail, attacks go undetected
Examples:
  - No logging of failed logins, access control failures
  - Logs stored locally only (wiped if server compromised)
  - No alerting on suspicious activity
  - Logs contain sensitive data (passwords, tokens)

What to log:
  ✅ Authentication: success, failure, logout
  ✅ Authorization failures (403/401 responses)
  ✅ Rate limit hits (429)
  ✅ Admin actions
  ✅ Security configuration changes

What NOT to log:
  ❌ Passwords (even hashed)
  ❌ JWT tokens / session IDs
  ❌ Credit card numbers / SSN
  ❌ Full request/response bodies for sensitive endpoints

Log format (structured JSON):
{
  timestamp: "2024-01-15T10:30:00Z",
  level: "WARN",
  event: "LOGIN_FAILED",
  userId: "user@email.com",  // not password!
  ip: "1.2.3.4",
  userAgent: "Mozilla/5.0...",
  requestId: "req_abc123"
}

Alert on:
  - 10+ failed logins from same IP (brute force)
  - 100+ 4xx responses per minute
  - Unusual data exports
  - Admin login from new IP/country
```

---

## 🔴 A10 — Server-Side Request Forgery (SSRF)
```
What: Server fetches attacker-controlled URLs
Attack:
  POST /fetch-url { "url": "http://169.254.169.254/latest/meta-data/" }
  → Server fetches AWS metadata → returns IAM credentials!
  
  POST /fetch-url { "url": "http://localhost:6379/" }
  → Server fetches Redis → internal data exposed

❌ Vulnerable:
app.post('/fetch', async (req, res) => {
  const response = await fetch(req.body.url);  // fetches anything!
  res.send(await response.text());
});

✅ Secure:
const ALLOWED_DOMAINS = new Set(['api.github.com', 'api.stripe.com']);

function validateUrl(url) {
  const parsed = new URL(url);
  if (!['http:', 'https:'].includes(parsed.protocol)) throw new Error('Invalid protocol');
  if (!ALLOWED_DOMAINS.has(parsed.hostname)) throw new Error('Domain not allowed');
  // Block private IP ranges:
  if (/^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.|127\.|169\.254\.)/.test(parsed.hostname))
    throw new Error('Private IP not allowed');
  return url;
}

app.post('/fetch', async (req, res) => {
  const url = validateUrl(req.body.url);
  const response = await fetch(url, { redirect: 'manual' });  // no auto-redirects!
  res.json({ status: response.status });
});
```

---

## 📊 Quick Comparison Table
```
Vulnerability       | Attack Vector    | Detection    | Primary Fix
──────────────────────────────────────────────────────────────────────
Broken Access Ctrl  | URL manipulation | Access logs  | Auth check on every request
Crypto Failures     | Traffic sniff    | SSL scan     | HTTPS + bcrypt + encrypt at rest
Injection           | Input fields     | WAF alerts   | Parameterized queries
Insecure Design     | Architecture     | Code review  | Threat modeling
Misconfiguration    | Recon            | Security scan | Hardening + helmet
Vuln Components     | Known CVE        | npm audit    | Dependency scanning in CI
Auth Failures       | Brute force      | Failed login | Rate limit + bcrypt + MFA
Integrity Failures  | Supply chain     | Pipeline     | SRI + signed images
Logging Failures    | Attack detection | SIEM alerts  | Structured logging + alerting
SSRF               | URL input        | Outbound logs | Domain whitelist + IP block
```

---

## 🚀 Top 10 Fixes — Most Impact for 5+ YOE Interview

```javascript
// 1. Parameterized queries (Injection):
db.execute('SELECT * FROM users WHERE id = ?', [userId]);

// 2. Authorization check on every route (Broken Access):
const resource = await Resource.findOne({ _id: id, userId: req.user.id });

// 3. bcrypt for passwords (Crypto):
const hash = await bcrypt.hash(password, 12);

// 4. Helmet.js (Misconfiguration):
app.use(helmet());

// 5. Rate limiting (Auth Failures):
app.use('/login', rateLimit({ max: 5, windowMs: 900000 }));

// 6. CSRF protection (Auth):
res.cookie('session', token, { httpOnly: true, sameSite: 'strict', secure: true });

// 7. CSP header (XSS / Injection):
// Content-Security-Policy: default-src 'self'; object-src 'none'

// 8. Input validation (All injection types):
import { z } from 'zod';
const schema = z.object({ email: z.string().email(), age: z.number().int().min(0) });
const data = schema.parse(req.body);  // throws if invalid

// 9. SSRF protection:
const allowed = new Set(['api.github.com']);
if (!allowed.has(new URL(req.body.url).hostname)) throw new Error('Not allowed');

// 10. Structured security logging:
logger.warn({ event: 'LOGIN_FAILED', ip: req.ip, email: req.body.email });
```

---

## ⚡ Interview One-Liners

**Q: What is OWASP Top 10?**
A: The 10 most critical web application security risks, maintained by OWASP. In 2021: Broken Access Control (#1), Cryptographic Failures, Injection, Insecure Design, Security Misconfiguration, Vulnerable Components, Auth Failures, Software Integrity Failures, Logging Failures, SSRF.

**Q: What is IDOR?**
A: Insecure Direct Object Reference — accessing resources by guessing IDs (order/1234 → order/1235). Fix: verify resource ownership on every request, use non-sequential IDs (UUIDs).

**Q: What is SSRF?**
A: Server-Side Request Forgery — server fetches attacker-controlled URL, can reach internal services (AWS metadata, Redis, localhost). Fix: strict URL allowlist, block private IPs, disable redirects.

**Q: What is the most common vulnerability in 2021?**
A: Broken Access Control — moved from #5 to #1. 94% of tested applications had some form of broken access control.

**Q: How do you protect against all 10 at once?**
A: Defense in depth: input validation (injection) → parameterized queries → authentication (rate limit, bcrypt, MFA) → authorization (per-request ownership check) → security headers (helmet, CSP, HSTS) → encrypted transport (HTTPS, HSTS) → dependency scanning (npm audit, Snyk) → structured logging + alerting.
