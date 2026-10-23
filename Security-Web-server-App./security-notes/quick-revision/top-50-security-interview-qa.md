# Top 50 Security Interview Q&A
# 5+ YOE — Web Security + Server Security + Cloud Security

---

## 🔴 Category 1: Injection Attacks (Q1-Q8)

**Q1. What are the three types of SQL Injection?**
**A:** (1) **In-band SQLi** — result returned in response: Classic (data in page), Error-based (data in error messages), Union-based (append extra SELECT). (2) **Blind SQLi** — no visible output: Boolean-based (true/false differences in response), Time-based (`SLEEP(5)` → detects injectable field). (3) **Out-of-band** — data exfiltrated via DNS/HTTP request from DB server. Fix: parameterized queries, ORMs, whitelist for ORDER BY column names.

**Q2. How does NoSQL injection differ from SQL injection?**
**A:** NoSQL (MongoDB) doesn't use SQL syntax — injection uses MongoDB operators. Example: `{ username: { $gt: "" } }` — `$gt: ""` means "username greater than empty string" — returns ALL users. Or `{ password: { $regex: ".*" } }` — matches any password. Fix: use Mongoose schemas (enforces type: String, rejects objects), validate with joi/zod, or explicitly extract only string values: `const username = String(req.body.username)`.

**Q3. What is OS Command Injection and how do you prevent it?**
**A:** Attacker injects shell commands via user input. Example: `exec("ping " + userInput)` — attacker sends `; cat /etc/passwd`. Prevention: (1) Use library instead of shell (node `dns.lookup()` instead of `ping`). (2) If shell is unavoidable: use `execFile(['ping', userInput])` — no shell expansion, treats userInput as an argument, not a command. (3) Whitelist valid values. (4) Use a sandbox (Docker container with no shell). Never use `eval`, `exec`, `system` with user-controlled data.

**Q4. What is XPath injection?**
**A:** XPath queries XML data. Injection is similar to SQL: `//user[name/text()='admin' and password/text()='' or '1'='1']` — the `or '1'='1'` part always returns true, bypassing auth. Less common than SQL injection but found in legacy enterprise apps and XML-heavy systems. Prevention: parameterized XPath queries or use a safe XPath library that doesn't accept user-provided query strings directly.

**Q5. What is the difference between first-order and second-order SQL injection?**
**A:** **First-order**: malicious input is used immediately in a SQL query — classic in login forms. **Second-order** (stored): malicious input is stored safely but later retrieved and used unsafely in another context. Example: attacker creates username `admin'--`. Username is inserted safely (parameterized). Later, admin resets attacker's "password" using: `UPDATE users SET password='X' WHERE username='admin'--'` — the `--` comments out the WHERE clause, changing admin's password! Prevention: use parameterized queries everywhere, not just at input time.

**Q6. How do you test an application for SQL injection?**
**A:** (1) Manual: add `'`, `''`, `; DROP TABLE`, `1=1`, `1=2` to inputs, observe response differences. (2) Automated: sqlmap (`sqlmap -u "https://app.com/users?id=1" --dbs`). (3) Error-based: send malformed input, check if database errors appear in response. (4) Time-based: `1'; WAITFOR DELAY '0:0:5'--` — if response delays 5s, it's injectable. (5) Check all input surfaces: GET params, POST body, JSON, Headers (User-Agent, Referer, X-Forwarded-For — often logged and queried).

**Q7. What is LDAP injection?**
**A:** LDAP injection injects into LDAP queries for directory services. Example: login filter `(&(uid=USER)(password=PASS))` — attacker sends `*)(uid=*))(|(uid=*` — closes the filter and adds OR condition, bypassing auth. Common in enterprise apps using Active Directory. Prevention: escape special characters (`(`, `)`, `*`, `\`, `NUL`), use LDAP libraries with parameterized queries, validate input strictly.

**Q8. What is a prepared statement and how does it prevent injection?**
**A:** A prepared statement separates SQL code from data — the query structure is compiled once, then data is substituted at execution time as parameters (not as query text). The DB treats parameters as literal values, never as SQL code. Even if a parameter contains `'; DROP TABLE users--`, the DB sees it as the literal string `'; DROP TABLE users--`, not SQL. Contrast: string concatenation builds the query as text first — the DB can't distinguish injected SQL from intended SQL.

---

## 🟠 Category 2: XSS + CSRF (Q9-Q15)

**Q9. What are the three types of XSS and their severity?**
**A:** (1) **Stored/Persistent XSS** — malicious script saved to DB, served to all users who view the page. Most dangerous — no user interaction needed after initial injection, affects many users. (2) **Reflected XSS** — script in URL parameter, reflected in response, victim must click crafted link. Requires social engineering. (3) **DOM-based XSS** — script manipulated via DOM (location.hash, document.URL), never goes to server — invisible in server logs, hardest to detect. Severity: Stored > DOM > Reflected.

**Q10. How does React prevent XSS and what are its exceptions?**
**A:** React HTML-encodes all values in JSX expressions `{}` by default — `<script>` becomes `&lt;script&gt;`, displayed as text. Exceptions: (1) `dangerouslySetInnerHTML` — bypasses encoding, must use DOMPurify. (2) `href` with user input — `href={userUrl}` could be `javascript:evil()`. Validate: `url.startsWith('http') || url.startsWith('https')`. (3) `data-` attributes with `dangerouslySetInnerHTML`. (4) Third-party library that renders HTML. Rule: `dangerouslySetInnerHTML` must always go through DOMPurify.

**Q11. What is Content Security Policy and how does it prevent XSS?**
**A:** CSP is an HTTP header that whitelists resource sources. `script-src 'self'` — only scripts from same origin run; injected `<script src="https://evil.com/steal.js">` is blocked by browser. Nonce-based CSP: every legitimate script gets a unique nonce `<script nonce="abc">`, CSP specifies `script-src 'nonce-abc'` — injected scripts without the nonce are blocked even if same-origin. CSP is defense-in-depth — doesn't prevent the injection, but breaks its execution. Report-only mode lets you test before enforcing.

**Q12. Can XSS still cause damage if HttpOnly cookies are set?**
**A:** Yes. HttpOnly prevents `document.cookie` from reading protected cookies, but XSS can: (1) Capture keystrokes as user types (steal credentials live). (2) Hijack form submissions (steal data before it's sent). (3) Make authenticated API calls via `fetch()` — browser auto-attaches httpOnly cookies to same-origin requests! (4) Create a UI overlay (fake login form), redirect to phishing site. (5) Exfiltrate page content, steal visible data. HttpOnly limits one attack vector (cookie theft), not all XSS damage.

**Q13. Explain the CSRF attack flow and prevention.**
**A:** Attack: victim logs into bank.com (gets session cookie). Attacker's page has hidden form posting to bank.com/transfer. Victim visits evil.com → form auto-submits → browser attaches bank.com cookies → bank processes transfer. Prevention: (1) **CSRF tokens** — server generates unpredictable token per session, embeds in forms, verifies on submission. Attacker can't read the token (same-origin policy). (2) **SameSite=Strict cookies** — browser refuses to send cookie in cross-site requests. (3) **Origin/Referer header check** — verify request came from expected origin. (4) **Custom headers** — `X-Requested-With: XMLHttpRequest` can't be set by HTML forms.

**Q14. How do you handle CSRF in a SPA with JWTs?**
**A:** JWT in Authorization header: NOT vulnerable to CSRF. HTML forms/images can't set custom headers (like Authorization) cross-origin — attacker can't forge the request with the JWT. Only a JS fetch with `credentials: 'include'` can send cookies. JWTs in httpOnly cookies: potentially CSRF-vulnerable. Mitigation: `SameSite=Strict` + CSRF token. For pure JWT/Authorization header approach (React SPA): no CSRF concern, but XSS concern → strict CSP, no localStorage. For SSR with cookies: use `SameSite=Strict` and a CSRF token middleware.

**Q15. What is the Same-Origin Policy and what does it NOT protect against?**
**A:** SOP prevents JavaScript from reading responses from different origins (different protocol, domain, or port). Does NOT prevent: (1) Sending requests (CSRF — cookies are sent). (2) Loading resources (images, scripts via `<img>`, `<script>` tags). (3) Form submissions (always worked cross-origin). (4) Postmessage if message origin not validated. Protects: XHR/fetch reading cross-origin response bodies. So attackers can SEND data cross-origin (CSRF) but not READ it (SOP blocks), unless CORS explicitly allows it.

---

## 🟡 Category 3: Authentication + JWT (Q16-Q22)

**Q16. How should passwords be stored?**
**A:** Use bcrypt (or Argon2). Never: MD5, SHA1, SHA256 (fast hashes — GPU can crack 10B/sec), plaintext, reversible encryption. bcrypt: adaptive cost factor (12 recommended in 2024 — ~250ms), includes built-in salt (prevents rainbow tables). `const hash = await bcrypt.hash(password, 12)`. Argon2id: better for new systems — resistant to GPU and side-channel attacks, 3 parameters (memory, time, parallelism). Salt prevents rainbow table attacks — same password generates different hash each time.

**Q17. Explain JWT algorithm confusion attack.**
**A:** RS256 uses asymmetric keys — private key signs, public key verifies. HS256 uses symmetric key — same secret for both. Attack: if a server accepts both RS256 and HS256, attacker creates HS256 token signed with the public key (which is public!). Server verifies with public key — which matches for HS256. Prevention: explicitly whitelist algorithms in `jwt.verify(token, publicKey, { algorithms: ['RS256'] })` — never include HS256 in a service that only has the public key.

**Q18. What is the alg:none JWT attack?**
**A:** JWT header specifies the signing algorithm. If a server accepts `alg: none`, no signature verification is needed — attacker modifies the payload (e.g., role: 'admin') and sends a token with empty signature. Some older JWT libraries defaulted to allowing this. Fix: always pass `algorithms: ['HS256']` to `jwt.verify()` — explicitly exclude 'none'.

**Q19. What should go in a JWT payload?**
**A:** JWT payload is base64url ENCODED, not ENCRYPTED. Anyone with the token can decode it (browser devtools, server logs, proxies). Include: `userId`, `role`, `exp` (expiry), `iss` (issuer), `aud` (audience), `jti` (unique ID for revocation). Never include: passwords, credit card numbers, SSN, secrets, medical records, full PII. For sensitive data: store server-side, reference by ID in JWT, or use JWE (JSON Web Encryption) which encrypts the payload.

**Q20. How do you implement secure logout?**
**A:** Logout must invalidate tokens server-side — deleting the client-side cookie/localStorage is not enough. (1) For session-based auth: `req.session.destroy()` removes server-side session. (2) For JWT: add JWT ID (`jti`) to a Redis blocklist on logout, check blocklist on every verification. (3) Refresh token rotation: revoking the refresh token prevents getting new access tokens. (4) Clear httpOnly cookies server-side: `res.clearCookie('accessToken')` + `res.clearCookie('refreshToken')`. Without server-side invalidation, a stolen token remains valid until expiry.

**Q21. What is refresh token rotation and why does it enable breach detection?**
**A:** On each use of a refresh token, revoke it and issue a new one. If a refresh token is stolen: attacker uses it first → original token revoked. When the legitimate user tries to refresh (using their now-revoked token): server detects "this revoked token is being used!" → suspicious → revoke ALL tokens for this user. Without rotation, a stolen refresh token is usable silently for its entire lifetime with no detection mechanism.

**Q22. How do you implement MFA (Multi-Factor Authentication)?**
**A:** TOTP (most common): (1) Generate secret per user on enrollment: `speakeasy.generateSecret()`. (2) Show QR code for authenticator app (Google Authenticator, Authy). (3) Store encrypted secret in DB. (4) On login: verify `speakeasy.totp.verify({ secret, token: userInput, window: 1 })` (window=1 allows ±30s clock drift). WebAuthn/Passkeys (most secure, phishing-resistant): uses public key crypto on device (Touch ID, Face ID) — no shared secret that can be phished. SMS OTP: weakest — vulnerable to SIM swap, SS7 attacks; avoid for high-security applications.

---

## 🟢 Category 4: Security Headers + CORS (Q23-Q28)

**Q23. What does helmet() do?**
**A:** Helmet.js sets 11+ HTTP security headers in one middleware call: `Content-Security-Policy` (controls what scripts/styles load), `Strict-Transport-Security` (force HTTPS), `X-Frame-Options: DENY` (clickjacking), `X-Content-Type-Options: nosniff` (MIME sniffing), `Referrer-Policy` (Referer header control), `Cross-Origin-Embedder-Policy`, `Cross-Origin-Opener-Policy`, removes `X-Powered-By`. Single call: `app.use(helmet())`. Each can be customized or disabled.

**Q24. What is clickjacking and how is it prevented?**
**A:** Attacker places your site in a transparent iframe overlaid on their page. Victim clicks a "button" on attacker's page, actually clicking your site's button (transfer funds, approve action). Prevention: `X-Frame-Options: DENY` — browser refuses to render page in iframe. Modern: `Content-Security-Policy: frame-ancestors 'none'` — same effect, more flexible (can allow specific origins). CSP frame-ancestors supersedes X-Frame-Options in browsers that support it.

**Q25. What is HSTS and what happens if you set too short a max-age?**
**A:** HTTP Strict Transport Security tells browsers "only use HTTPS for this domain for N seconds." Too short max-age (e.g., 300s = 5 min): browsers frequently re-validate, wasted requests, HSTS protection often not in effect when user visits. Recommended: 63072000 (2 years). HSTS preload list (browser vendors) requires ≥1 year max-age, `includeSubDomains`, and `preload` directive. Once preloaded: browser uses HTTPS even for first visit (no initial HTTP request that could be downgraded).

**Q26. What is the difference between `Access-Control-Allow-Origin: *` and `Access-Control-Allow-Origin: https://app.com`?**
**A:** `*` (wildcard) allows any origin to read the response, but cannot be combined with `credentials: true` (browsers reject the combination per spec). `https://app.com` allows exactly that origin, can be combined with credentials. For authenticated APIs: always use specific origin(s) from a whitelist — never `*` for endpoints that return user-specific data. For truly public data (public CDN assets, open APIs): `*` is appropriate.

**Q27. Why is `Vary: Origin` important for CORS?**
**A:** When your server returns different CORS headers based on the Origin (whitelist check), CDNs and caches may cache a response with one origin's CORS headers and serve it to a different origin. `Vary: Origin` tells caches: "this response varies by Origin header — cache separately per Origin value." Without it: CDN caches `Access-Control-Allow-Origin: https://app.com` for one requester, serves it (with that CORS header) to a request from `evil.com` — wrong headers, potential security confusion.

**Q28. What is a preflight request?**
**A:** An automatic OPTIONS request the browser sends before non-simple cross-origin requests to ask if the server allows it. Non-simple: methods other than GET/HEAD/POST, custom headers, Content-Type: application/json. The preflight includes `Access-Control-Request-Method` and `Access-Control-Request-Headers`. Server responds with `Access-Control-Allow-Methods/Headers`. If approved → actual request sent. If denied → actual request blocked. Benefits security: prevents cross-origin state-changing requests without explicit server approval.

---

## 🔵 Category 5: Rate Limiting + DDoS (Q29-Q32)

**Q29. How do you prevent brute force attacks on login?**
**A:** (1) **Rate limit per IP**: 5 attempts / 15 minutes. (2) **Rate limit per account**: 10 attempts / 15 minutes (defeats IP rotation). (3) **Progressive delays**: 1st-5th: normal; 6-10th: 1s delay; 11th+: lockout. (4) **Account lockout**: after 5 failures, lock 30 min + email notification. (5) **CAPTCHA**: after 3 failures. (6) **Constant time response**: same response time for "user not found" and "wrong password" (prevents timing attacks). (7) **Alert**: monitor for spikes in 429 responses.

**Q30. What is the difference between rate limiting algorithms?**
**A:** **Fixed window**: count requests in time slots (0-60s, 60-120s). Problem: boundary burst (100 req at t=59s + 100 at t=61s = 200 in 2s). **Sliding window**: count requests in last N seconds from now. No boundary burst, requires timestamp storage in Redis (sorted sets). **Token bucket**: bucket fills at fixed rate, each request consumes a token. Allows short bursts (burst = bucket capacity). **Leaky bucket**: requests drain at constant rate regardless of arrival — smooths traffic. Sliding window is most accurate; token bucket most appropriate for APIs with burst allowance.

**Q31. What is credential stuffing and how is it different from brute force?**
**A:** **Brute force**: systematically tries all possible passwords for one account. **Credential stuffing**: uses breached username/password pairs from other sites (HaveIBeenPwned 10B+ records). Attacker tries `user@email.com:password123` from a Netflix breach on your banking app — works because users reuse passwords. Defense: rate limiting still helps, but not enough. Add: (1) MFA. (2) Breach password checking (HaveIBeenPwned Pwned Passwords API). (3) Behavioral analysis (new device, new location → step-up auth). (4) Device fingerprinting.

**Q32. How do you protect against DDoS at the application level?**
**A:** Application-level (Layer 7) DDoS defense: (1) Rate limiting per IP (express-rate-limit + Redis). (2) Request validation (drop malformed requests early). (3) Connection limits (nginx `limit_conn`, `limit_req`). (4) Caching (reduce database load). (5) Circuit breakers (stop cascading failures). But real DDoS (millions of req/sec) can't be stopped at app level — needs edge protection: (1) **Cloudflare**: absorbs traffic at edge, 121 Tbps capacity, WAF, bot detection. (2) **AWS Shield**: DDoS protection for AWS infrastructure. (3) **AWS WAF**: Layer 7 rules, rate limiting before traffic hits your servers.

---

## ⚫ Category 6: Secure Coding Practices (Q33-Q40)

**Q33. What is input validation and how should it be implemented?**
**A:** Input validation verifies data is in expected format before processing. Key principles: (1) **Whitelist over blacklist**: define what's allowed, reject everything else. (2) **Validate type, range, format**: email must match regex, age must be 0-120, username alphanumeric. (3) **Validate server-side** (client validation is UX, not security). (4) **Fail fast**: reject at entry, not deep in business logic. (5) **Encode output** separately — validation and encoding are both needed. Libraries: `zod` (TypeScript-first), `joi`, `express-validator`, class-validator (NestJS).

**Q34. What is the principle of least privilege?**
**A:** Every component should have only the minimum access required for its function. DB user: SELECT/INSERT/UPDATE on specific tables, no DROP, no CREATE, no access to other schemas. API key: only the permissions it needs (read-only for data export, not admin). IAM role: `AmazonS3ReadOnlyAccess` for the service that only reads, not full S3 access. Container: non-root user, minimal file system access. Why: if a component is compromised, attacker only gets minimal access — can't pivot to full system compromise.

**Q35. How do you handle secrets in a Node.js application?**
**A:** (1) `.env` file locally (never commit to git — add to `.gitignore`). (2) Environment variables in production (set by deployment system). (3) **Secrets manager**: AWS Secrets Manager, HashiCorp Vault, Azure Key Vault — centralized, audited, rotatable. (4) Never hardcode: `const secret = 'mypassword'` — it ends up in git history. (5) Pre-commit hooks: git-secrets, truffleHog, detect-secrets scan for accidentally committed secrets. (6) Rotate secrets regularly and immediately on suspected exposure. CI/CD: GitHub Actions secrets, not in workflow YAML.

**Q36. What is a timing attack and how do you prevent it?**
**A:** Timing attack exploits the fact that string comparison (`===`) short-circuits — different lengths or early character mismatch returns faster than full match. Attacker measures response time to infer partial secrets (HMAC tokens, API keys). Prevention: use constant-time comparison: Node.js `crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b))` — compares all bytes regardless of where mismatch occurs. Also: constant-time response for login failures (use `bcrypt.compare()` even if user doesn't exist — compare against a dummy hash to prevent email enumeration via timing).

**Q37. What is security in depth?**
**A:** Defense in depth applies multiple independent security controls — if one fails, others remain. Example for login: (1) Input validation (reject malformed input). (2) Rate limiting (limit attempts). (3) bcrypt (slow, salted hash). (4) Account lockout (after N failures). (5) MFA (requires physical device). (6) Anomaly detection (new IP/device → step-up). Each layer independently prevents an attack class. Attacker must defeat all layers. Contrast with single control: if only rate limiting, compromised Redis = no protection.

**Q38. How do you securely handle file uploads?**
**A:** (1) **Validate file type** server-side: check magic bytes (not just extension): `import('file-type').then(({ fileTypeFromBuffer }) => ...)`. (2) **Scan for malware**: virus scanner (ClamAV, cloud AV API). (3) **Rename files**: never use user-provided filename — generate UUID. (4) **Store outside webroot**: don't serve from `/public/uploads` — serve via API endpoint that streams the file. (5) **Restrict size**: `multer({ limits: { fileSize: 10 * 1024 * 1024 } })`. (6) **Sanitize SVG**: SVG can contain JavaScript — run through DOMPurify before storing. (7) **CDN with separate origin**: serve uploads from `uploads.app.com`, not `app.com` — isolates any XSS in uploads.

**Q39. What is prototype pollution and how do you prevent it?**
**A:** JavaScript object prototype chain means setting `obj.__proto__.isAdmin = true` affects ALL objects. Vulnerability: `Object.assign({}, JSON.parse(userInput))` where userInput is `{"__proto__": {"isAdmin": true}}` — now all plain objects have `isAdmin: true`. Found in lodash merge, jQuery extend, handlebars. Prevention: (1) Use `JSON.parse()` with schema validation (`zod`, `ajv`). (2) Use `Object.freeze(Object.prototype)` in Node.js (aggressive). (3) Use `Object.create(null)` for key-value maps (no prototype). (4) Update dependencies (lodash 4.17.21+ fixed). (5) `if (key === '__proto__') return` when merging objects.

**Q40. What is path traversal and how do you prevent it?**
**A:** Attacker uses `../` sequences in file paths to access files outside intended directory. `GET /file?name=../../etc/passwd` — server joins with `/uploads/../../etc/passwd` = `/etc/passwd`. Prevention: (1) `path.resolve('/uploads/', userInput)` then verify it starts with `/uploads/`. (2) `path.basename(userInput)` — strips all directory components. (3) Whitelist filenames (only alphanumeric + extension). (4) Use cloud storage (S3) — no filesystem traversal possible. Example: `if (!resolved.startsWith(uploadDir)) throw new Error('Invalid path')`.

---

## 🔵 Category 7: Cloud + Infrastructure Security (Q41-Q50)

**Q41. What is SSRF and why is it especially dangerous in cloud environments?**
**A:** SSRF (Server-Side Request Forgery) allows attackers to make the server fetch arbitrary URLs. In cloud (AWS/GCP/Azure), the instance metadata endpoint (`http://169.254.169.254/latest/meta-data/`) is accessible from the instance and returns IAM credentials! Capital One breach (2019): SSRF via a WAF misconfiguration → AWS metadata endpoint → temporary IAM credentials → 100M customer records exfiltrated. Fix: whitelist allowed domains, block private IP ranges (169.254.0.0/16, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.0/8), disable redirects.

**Q42. How do you secure an S3 bucket?**
**A:** (1) Block public access at account level (S3 Block Public Access). (2) Never use `"Principal": "*"` in bucket policy. (3) Enable bucket versioning (recover from accidental deletes). (4) Enable server-side encryption (SSE-S3 or SSE-KMS). (5) Enable access logging. (6) Use S3 pre-signed URLs for temporary access instead of making buckets public. (7) VPC endpoint for internal service access (traffic stays in AWS network). (8) AWS Config rule: `s3-bucket-public-read-prohibited`. Common breach: developers make a bucket public during testing and forget to restrict it.

**Q43. What is the principle of least privilege for IAM?**
**A:** Each service/role/user gets only the minimum AWS permissions needed. EC2 instance that only reads from S3: attach role with `AmazonS3ReadOnlyAccess` or better, a custom policy scoped to specific bucket + `s3:GetObject` only. Avoid: `"Action": "*"`, `"Resource": "*"` (admin). Use: (1) IAM Access Analyzer — identifies overly permissive policies. (2) AWS Organizations SCPs — guardrails at organization level. (3) Resource-based policies — specific bucket/queue allows specific role. (4) Condition keys: `aws:SourceIp`, `aws:RequestedRegion` for additional constraints.

**Q44. How do you secure environment variables and secrets?**
**A:** (1) `.env` locally (gitignore). (2) Platform secrets in CI/CD (GitHub Actions Secrets, not in code). (3) AWS Secrets Manager / Parameter Store in production — rotation, auditing, fine-grained IAM. (4) Kubernetes Secrets (base64 encoded — not encrypted by default; use KMS envelope encryption or Sealed Secrets). (5) Never log environment variables (`process.env` dump to logs). (6) Rotate on exposure. (7) `detect-secrets` pre-commit hook — prevents accidental commit. (8) Audit who has access to production secrets (least privilege).

**Q45. What is a WAF and what does it protect against?**
**A:** Web Application Firewall inspects HTTP traffic and blocks malicious patterns. Protects against: SQLi, XSS, CSRF, path traversal, bot attacks, DDoS (Layer 7). Types: (1) **Cloud WAF**: Cloudflare, AWS WAF, Akamai — edge-based, absorbs traffic before your server. (2) **Nginx ModSecurity**: open-source, self-hosted, OWASP Core Rule Set. (3) **Application-level middleware**: express-validator, custom middleware. Limitations: WAF can be bypassed (encoding tricks, fragmented payloads) — it's a layer, not a complete solution. Must combine with proper input validation and secure coding.

**Q46. What is container security and how do you harden Docker images?**
**A:** (1) **Non-root user**: `USER node` in Dockerfile (never run as root). (2) **Minimal base image**: `node:20-alpine` (5MB) vs `node:20` (1GB) — fewer attack surface. (3) **Multi-stage build**: build stage installs devDependencies, final stage copies only production artifacts. (4) **Scan for CVEs**: `trivy image myapp:latest`, `docker scan` (Snyk). (5) **Read-only filesystem**: `docker run --read-only`. (6) **No secrets in image**: use environment variables, not baked-in. (7) **Pin versions**: `node:20.10.0-alpine3.19` not `node:latest`. (8) `docker run --cap-drop ALL` — remove Linux capabilities.

**Q47. What is a supply chain attack in the context of npm packages?**
**A:** Attackers compromise npm packages to run malicious code in dependent projects. Types: (1) **Typosquatting**: publish `lodsh` or `reqeust` (typos of popular packages) — unsuspecting developers install wrong package. (2) **Account takeover**: compromise maintainer account, publish malicious version (event-stream incident 2018). (3) **Dependency confusion**: publish packages with same name as internal packages on public npm — build system installs public version. (4) **Post-install scripts**: `package.json` scripts run on install. Prevention: `npm audit`, pin exact versions, lock file, private registry for internal packages, review `postinstall` scripts.

**Q48. Explain the difference between authentication and authorization.**
**A:** **Authentication** (AuthN): "Who are you?" — verifying identity. Mechanisms: password, OAuth, JWT, certificate, biometric. Result: "This is user ID 123." **Authorization** (AuthZ): "What can you do?" — verifying access rights. Mechanisms: RBAC (role-based), ABAC (attribute-based), ACL (access control list). Result: "User 123 can read order 456 but not order 789." Common mistake: checking authentication but not authorization — user is logged in (authenticated) but accessing another user's data (failed authorization = Broken Access Control, OWASP #1).

**Q49. What is HTTPS and what does TLS protect against?**
**A:** HTTPS = HTTP over TLS (Transport Layer Security). TLS provides: (1) **Encryption** (confidentiality) — data encrypted in transit, prevents eavesdropping. (2) **Authentication** — server certificate proves identity, prevents impersonation. (3) **Integrity** — MAC (message authentication code) detects tampering in transit. TLS does NOT protect: data at rest (need encryption at rest separately), application-level vulnerabilities (SQLi, XSS still work over HTTPS), server-side processing. Minimum: TLS 1.2 (deprecate 1.0/1.1), prefer TLS 1.3 (faster, more secure). Check: `openssl s_client -connect app.com:443`.

**Q50. How would you approach a security review for a new feature?**
**A:** Structured threat modeling: (1) **Define scope**: what data flows, what's new. (2) **Identify threats** (STRIDE): Spoofing (can attacker impersonate?), Tampering (can data be modified?), Repudiation (can actions be denied?), Information Disclosure (what data could leak?), Denial of Service (can it be overwhelmed?), Elevation of Privilege (can permissions be escalated?). (3) **Check OWASP Top 10** against the feature. (4) **Review code**: injection points, auth checks, input validation, error handling (no internal details exposed). (5) **Test**: OWASP ZAP, manual testing. (6) **Document**: threat model, mitigations. For 5+ YOE: expected to lead this process, not just participate.
