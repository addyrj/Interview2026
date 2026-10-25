# 272. Node.js Production Checklist
# हिंदी में: Node.js Production Checklist

---

## 🔵 Simple Definition (English)
A **production checklist** is the set of security, performance, reliability, and observability steps that must be verified BEFORE a Node.js app goes live — covering things like env vars, logging, process management, error handling, security headers, and monitoring. It catches the common mistakes that work fine in dev but break under real traffic.

## 🔵 सरल परिभाषा (Hindi)
**Production checklist** वो security, performance, reliability, और observability steps हैं जो Node.js app live करने से पहले verify करनी ज़रूरी हैं — env vars, logging, process management, error handling, security headers, monitoring। ये common mistakes पकड़ती है जो dev में तो ठीक चलती हैं पर real traffic में टूट जाती हैं।

---

## 🔴 Problem it Solves
Dev environments are forgiving: single user, no real load, console.log for debugging, crashes are just annoying. Production is hostile: thousands of concurrent users, malicious traffic, memory leaks that take days to surface, and silent failures that lose revenue. A checklist converts "it worked on my machine" tribal knowledge into a repeatable, auditable gate — preventing outages caused by missing env vars, unhandled promise rejections crashing the process, or exposed stack traces leaking internals to attackers.

## 🔴 यह क्यों बना? (Hindi)
Dev environment forgiving होता है: single user, real load नहीं, debugging के लिए console.log, crashes सिर्फ annoying। Production hostile होता है: हज़ारों concurrent users, malicious traffic, memory leaks जो दिनों बाद दिखें, silent failures जो revenue खो दें। Checklist "मेरे machine पर चला" वाले tribal knowledge को repeatable, auditable gate में बदलती है — missing env vars, unhandled rejections से crash, या exposed stack traces से होने वाले outages रोकती है।

---

## 🟢 How it Works — Step by Step

Step 1 → **Security**: helmet middleware, rate limiting, input validation, secrets in env vars not code, dependency audit (`npm audit`), CORS locked to known origins.
Step 2 → **Process management**: PM2/cluster mode for multi-core use, auto-restart on crash, graceful shutdown handling SIGTERM.
Step 3 → **Error handling**: global `uncaughtException`/`unhandledRejection` handlers that log and exit cleanly (never silently swallow), centralized Express error middleware.
Step 4 → **Logging & monitoring**: structured JSON logs (Winston/Pino), shipped to a log aggregator (CloudWatch, Datadog), APM for performance (New Relic), uptime monitoring (health check endpoint polled externally).
Step 5 → **Performance**: compression middleware, caching layer (Redis) for hot paths, database connection pooling, avoid blocking the Event Loop.
Step 6 → **Config & secrets**: `NODE_ENV=production` set, all required env vars validated at boot, no `.env` file baked into Docker images.
Step 7 → **Infra**: HTTPS enforced (SSL via Let's Encrypt/ALB), health check endpoint for load balancer, horizontal scaling tested, database backups configured.
Step 8 → **CI/CD**: automated tests run before deploy, zero-downtime deployment strategy (rolling/blue-green), rollback plan documented.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Security**: helmet, rate limiting, input validation, secrets env vars में, `npm audit`, CORS locked।
Step 2 → **Process management**: PM2/cluster mode, crash पर auto-restart, SIGTERM पर graceful shutdown।
Step 3 → **Error handling**: global `uncaughtException`/`unhandledRejection` handlers जो log करके clean exit करें, centralized Express error middleware।
Step 4 → **Logging & monitoring**: structured JSON logs, log aggregator को ship, APM, external health check polling।
Step 5 → **Performance**: compression, caching (Redis), DB connection pooling, Event Loop block न हो।
Step 6 → **Config**: `NODE_ENV=production`, boot पर required env vars validate, `.env` Docker image में बेक न हो।
Step 7 → **Infra**: HTTPS enforced, load balancer health check, horizontal scaling tested, DB backups।
Step 8 → **CI/CD**: deploy से पहले automated tests, zero-downtime deployment, rollback plan documented।

---

## 🟡 Real World Example
**Paytm's** payment processing service follows a strict pre-launch checklist before any new feature goes live: `npm audit --production` must show zero high/critical vulnerabilities, load testing at 3x expected peak traffic (festival sale days), a documented rollback runbook, PagerDuty alerting wired to error rate thresholds, and a staging environment that mirrors production exactly (same env var SHAPE, different values). One missed item — forgetting to set connection pool limits — once caused a cascading DB connection exhaustion during a flash sale; it's now item #1 on their checklist.

## 🟡 Real Example Hindi mein
**Paytm** का payment processing service किसी भी नए feature को live करने से पहले strict checklist follow करता है: `npm audit --production` में zero high/critical vulnerabilities, 3x expected peak traffic पर load testing, documented rollback runbook, error rate thresholds पर PagerDuty alerting। एक बार connection pool limits set करना भूल जाने से flash sale के दौरान DB connection exhaustion हुआ था — अब ये checklist का item #1 है।

---

## 💻 Code Example — Basic

```javascript
// checklist-basic.js — minimal "production-safe" bootstrap for any Node app
// Run with: NODE_ENV=production node checklist-basic.js

// 1. Fail fast if critical env vars are missing
const required = ['PORT', 'DATABASE_URL', 'JWT_SECRET'];
const missing = required.filter((k) => !process.env[k]);
if (missing.length) {
  console.error(`Missing env vars: ${missing.join(', ')}`);
  process.exit(1);
}

// 2. Catch uncaught errors instead of crashing silently or hanging
process.on('uncaughtException', (err) => {
  console.error('Uncaught Exception:', err);
  process.exit(1); // exit cleanly so PM2/orchestrator can restart
});

process.on('unhandledRejection', (reason) => {
  console.error('Unhandled Rejection:', reason);
  process.exit(1);
});

// 3. Handle graceful shutdown (important for zero-downtime deploys)
process.on('SIGTERM', () => {
  console.log('SIGTERM received — shutting down gracefully');
  process.exit(0);
});

console.log(`App starting in ${process.env.NODE_ENV} mode on port ${process.env.PORT}`);
```

## 💻 Code Example — Advanced

```javascript
// checklist-advanced.js
// A fuller production bootstrap combining several checklist items together
const express = require('express');
const helmet = require('helmet');           // npm install helmet
const compression = require('compression'); // npm install compression
const rateLimit = require('express-rate-limit'); // npm install express-rate-limit

const app = express();

// ─── Security headers ──────────────────────────────────────────────────────
app.use(helmet()); // sets X-Content-Type-Options, X-Frame-Options, CSP basics, etc.

// ─── Compression for all responses ─────────────────────────────────────────
app.use(compression());

// ─── Rate limiting to prevent abuse/DoS ────────────────────────────────────
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,                  // 100 requests per IP per window
  standardHeaders: true,
  legacyHeaders: false,
});
app.use('/api/', apiLimiter);

// ─── CORS locked to known origins (never use '*' with credentials) ────────
const ALLOWED_ORIGINS = ['https://yourdomain.com', 'https://www.yourdomain.com'];
app.use((req, res, next) => {
  const origin = req.headers.origin;
  if (ALLOWED_ORIGINS.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  }
  next();
});

// ─── JSON body parsing with size limit (prevent large-payload DoS) ────────
app.use(express.json({ limit: '1mb' }));

// ─── Health check endpoint for load balancer / orchestrator ───────────────
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', uptime: process.uptime() });
});

// ─── Business routes ────────────────────────────────────────────────────────
app.get('/api/orders/:id', (req, res) => {
  res.json({ orderId: req.params.id, status: 'confirmed' });
});

// ─── Centralized error handler — NEVER leak stack traces in production ────
app.use((err, req, res, next) => {
  console.error(err); // log full error server-side for debugging
  const isProd = process.env.NODE_ENV === 'production';
  res.status(err.status || 500).json({
    error: isProd ? 'Internal Server Error' : err.message, // hide details in prod
  });
});

// ─── 404 handler ─────────────────────────────────────────────────────────────
app.use((req, res) => {
  res.status(404).json({ error: 'Not Found' });
});

const server = app.listen(process.env.PORT || 3000, () => {
  console.log(`Production-ready server on port ${process.env.PORT || 3000}`);
});

// ─── Graceful shutdown: stop accepting new connections, finish in-flight ones
process.on('SIGTERM', () => {
  console.log('SIGTERM received, closing server...');
  server.close(() => {
    console.log('Server closed, exiting process');
    process.exit(0);
  });
  // Force exit if shutdown takes too long (hung connections)
  setTimeout(() => process.exit(1), 10000);
});
```

---

## 🟠 Express.js Integration

```javascript
// production-checklist-middleware.js
// A reusable module encoding checklist items as pluggable Express middleware

const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan'); // npm install morgan — request logging

function applyProductionDefaults(app) {
  app.set('trust proxy', 1); // behind Nginx/ALB — needed for correct req.ip, req.secure
  app.use(helmet());
  app.use(compression());

  // Structured request logging — JSON format for log aggregators in prod
  if (process.env.NODE_ENV === 'production') {
    app.use(morgan('combined')); // Apache-style combined log format
  } else {
    app.use(morgan('dev')); // colored, concise for local dev
  }

  app.disable('x-powered-by'); // don't leak "Express" in headers (minor info leak)

  return app;
}

module.exports = { applyProductionDefaults };

// server.js
const express = require('express');
const { applyProductionDefaults } = require('./production-checklist-middleware');

const app = express();
applyProductionDefaults(app);

app.get('/', (req, res) => res.send('Production-ready app'));

app.listen(process.env.PORT || 3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Leaving `NODE_ENV` unset in production (defaults to development behavior in many libraries)
✅ Correct: Always explicitly set `NODE_ENV=production` — Express disables verbose error pages and enables view caching automatically when it's set.

```javascript
// Wrong: deploy script just runs `node server.js`
// → Express runs in "development" mode: verbose errors, no view caching, slower

// Right: deploy script / Dockerfile / PM2 ecosystem file sets it explicitly
// NODE_ENV=production node server.js
// or in ecosystem.config.js: env: { NODE_ENV: 'production' }
```

❌ Mistake 2: No global error handlers — one unhandled rejection crashes the whole process silently
✅ Correct: Register `process.on('uncaughtException', ...)` and `process.on('unhandledRejection', ...)` at the TOP of your entry file, before anything else runs.

```javascript
// Wrong: no handlers — Node prints a warning and (in future versions) crashes
// with no clean logging, no alerting, no graceful cleanup

// Right: handlers log clearly and exit so PM2 can restart with visibility
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});
```

---

## 🧠 Tricky Interview Question

```javascript
// This "works" in dev. What's wrong with it in production?
app.get('/api/user/:id', async (req, res) => {
  const user = await db.findUser(req.params.id);
  res.json(user);
});
// No try/catch, no error middleware call
```
Answer: If `db.findUser` throws (e.g. DB connection lost), this is an async function — the rejection becomes an unhandled promise rejection UNLESS caught. In Express 4.x, errors thrown inside async route handlers are NOT automatically passed to `next(err)` — they crash the process (if you have strict `unhandledRejection` handlers) or hang the request (if you don't). The fix: wrap in try/catch and call `next(err)`, or use `express-async-errors` / Express 5's native async error handling, or wrap routes in a helper: `const wrap = fn => (req, res, next) => fn(req, res, next).catch(next);`. This is one of the most common production incidents in Express apps — a single DB blip takes down the entire server instead of just failing that one request.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `process.exit(1)` in an error handler vs letting the process hang?
A1: `process.exit(1)` terminates the process immediately with a non-zero exit code, signaling failure to the process manager (PM2, systemd, Kubernetes), which then restarts it — this is the SAFE behavior after an uncaught exception, because the app may be in a corrupted/unknown state. Letting the process "hang" (not exiting) after a critical error means it keeps accepting requests in a broken state, which is worse — it may serve wrong responses or leak memory indefinitely. Always exit cleanly and let the orchestrator restart.

Q2: Why is `app.disable('x-powered-by')` considered a security best practice?
A2: By default, Express sends an `X-Powered-By: Express` header on every response. This leaks information about your tech stack to attackers, who can then target known Express/Node vulnerabilities more precisely. It's a minor "defense in depth" measure — disabling it doesn't stop a determined attacker (response timing/headers can still fingerprint Express) but removes easy reconnaissance. `helmet()` also disables this automatically.

Q3: What should a `/health` endpoint actually check?
A3: A good health check verifies the app can actually serve traffic, not just that the process is alive. Shallow check: just return 200 if the process responds (used for basic liveness probes). Deep check: also verify DB connectivity (`SELECT 1`), Redis connectivity, and critical downstream dependencies — but with a timeout, since a hanging health check can cause the load balancer to wrongly mark ALL instances unhealthy. Many teams expose `/health/live` (shallow, for restart decisions) and `/health/ready` (deep, for traffic-routing decisions) separately — matching Kubernetes' liveness/readiness probe pattern.

Q4: How does connection pooling prevent production outages?
A4: Without a pool, each DB query might open a new connection — under load, you exhaust the database's max connection limit (e.g. Postgres default 100), causing new queries to fail with "too many connections" errors, cascading into total outage. A pool (e.g. `pg.Pool` with `max: 20`) reuses a fixed number of connections across all requests, queuing excess requests briefly rather than overwhelming the DB. Tuning pool size correctly (based on DB capacity ÷ number of app instances) is a critical pre-launch checklist item.

Q5: What's the role of `npm audit` in a production checklist, and its limitations?
A5: `npm audit` scans `package-lock.json` against a vulnerability database and flags known CVEs in dependencies (and their transitive dependencies), categorized by severity. It should run in CI and block deploys on high/critical findings (`npm audit --audit-level=high`). Limitation: it only catches KNOWN, publicly disclosed vulnerabilities — zero-days or logic bugs in your own code aren't caught. It's one layer of defense, not a complete security review; should be paired with dependency pinning, minimal dependency count, and periodic manual review of critical packages.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Before every production deployment, as a mandatory gate (ideally automated in CI)
- Onboarding a new service/team to standardize what "production ready" means
- After an incident post-mortem, to add the missed item permanently to the checklist

❌ Avoid when:
- Rapid prototyping/hackathon code with no real users — full checklist is overkill, focus on just not committing secrets
- Internal tools with a single trusted user and no sensitive data — a lighter checklist suffices

---

## 📊 Visual Diagram
```
PRE-DEPLOY CHECKLIST GATE
──────────────────────────────────────────────────────────
  [ ] npm audit --production        → 0 high/critical vulns
  [ ] All required env vars set      → validated at boot
  [ ] NODE_ENV=production            → explicit, not implied
  [ ] Global error handlers          → uncaughtException, unhandledRejection
  [ ] Graceful shutdown (SIGTERM)     → in-flight requests finish
  [ ] Rate limiting + helmet          → abuse/DoS protection
  [ ] Structured logging              → shipped to aggregator
  [ ] Health check endpoint           → load balancer polls this
  [ ] DB connection pool sized         → matches DB max_connections
  [ ] HTTPS enforced                   → SSL cert valid, HSTS set
  [ ] Automated tests pass in CI        → before deploy triggers
  [ ] Rollback plan documented          → can revert in <5 min
──────────────────────────────────────────────────────────
         ALL CHECKED → deploy to production
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Graceful Shutdown | Finishing in-flight requests before exit | Exit से पहले चल रही requests पूरी करना |
| Health Check | Endpoint reporting app's ability to serve traffic | App traffic serve कर सकती है या नहीं बताने वाला endpoint |
| Connection Pool | Reused set of DB connections | Reuse होने वाले DB connections का set |
| Helmet | Middleware setting security HTTP headers | Security HTTP headers set करने वाला middleware |
| npm audit | Scans dependencies for known vulnerabilities | Dependencies में known vulnerabilities scan करता है |
| Rollback Plan | Documented steps to revert a bad deploy | बुरे deploy को revert करने के documented steps |

---

## ⚡ 3-Line Summary
English: 1. A production checklist converts tribal "it worked for me" knowledge into a repeatable gate covering security, process management, logging, and performance. 2. The most common real-world failures are missing error handlers, unbounded connection pools, and unset `NODE_ENV`. 3. Automate as much of the checklist as possible in CI so humans can't skip steps under deadline pressure.
Hindi: 1. Production checklist tribal knowledge को repeatable gate में बदलती है — security, process management, logging, performance cover करती है। 2. सबसे common real-world failures: missing error handlers, unbounded connection pools, unset `NODE_ENV`। 3. Checklist को जितना हो सके CI में automate करो ताकि deadline pressure में steps skip न हों।

---

## ➡️ Next Topic
**273. Build REST API from Scratch** — एक complete production-style REST API बनाना शुरू से।
