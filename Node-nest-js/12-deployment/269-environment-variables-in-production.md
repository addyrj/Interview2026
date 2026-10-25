# 269. Environment Variables in Production
# हिंदी में: Production में Environment Variables

---

## 🔵 Simple Definition (English)
**Environment variables** are key-value configs injected into your app from OUTSIDE the code (OS, hosting platform, secrets manager) — things like `DATABASE_URL`, `JWT_SECRET`, `PORT`. In production, you never hardcode secrets; you load them from the environment so the same code works across dev/staging/prod with different values.

## 🔵 सरल परिभाषा (Hindi)
**Environment variables** code के बाहर से inject की जाने वाली key-value configs हैं (OS, hosting platform, secrets manager) — जैसे `DATABASE_URL`, `JWT_SECRET`, `PORT`। Production में secrets code में hardcode नहीं करते; environment से load करते हैं जिससे same code dev/staging/prod में अलग values के साथ चले।

---

## 🔴 Problem it Solves
Without env vars: database passwords, API keys, JWT secrets sit directly in source code → committed to Git → leaked publicly (GitHub secret scanners find these daily, e.g. AWS key leaks cost companies thousands). Also: switching from dev DB to prod DB means editing code and redeploying. Env vars solve both: secrets never touch the repo, and the SAME build/image runs in every environment — only the injected variables change.

## 🔴 यह क्यों बना? (Hindi)
Env vars के बिना: DB passwords, API keys, JWT secrets source code में directly होते हैं → Git में commit → publicly leak (GitHub scanners daily पकड़ते हैं, AWS key leaks से companies को हज़ारों डॉलर का नुकसान)। साथ ही dev से prod DB बदलने के लिए code edit + redeploy करना पड़ता। Env vars दोनों solve करते हैं: secrets repo में नहीं जाते, और SAME build हर environment में चलता है — सिर्फ injected variables बदलते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Define variables in `.env` file locally (never committed — add to `.gitignore`).
Step 2 → `dotenv` package loads `.env` into `process.env` during local development only.
Step 3 → In production, the hosting platform (Railway, AWS, Docker, PM2 ecosystem file) injects env vars directly into the process — no `.env` file needed/used.
Step 4 → Code reads `process.env.VAR_NAME` everywhere config is needed.
Step 5 → Validate required env vars at startup — crash early with a clear error if something critical is missing, instead of failing mysteriously later.
Step 6 → Rotate secrets periodically using the platform's secret manager (AWS Secrets Manager, Railway variables, GitHub Actions secrets) without touching code.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Local development में `.env` file में variables define करो (कभी commit नहीं — `.gitignore` में add करो)।
Step 2 → `dotenv` package `.env` को `process.env` में load करता है — सिर्फ local development में।
Step 3 → Production में hosting platform (Railway, AWS, Docker, PM2) directly process में env vars inject करता है — `.env` file की ज़रूरत नहीं।
Step 4 → Code हर जगह `process.env.VAR_NAME` से config पढ़े।
Step 5 → Startup पर required env vars validate करो — कुछ missing हो तो clear error के साथ जल्दी crash करो।
Step 6 → Secrets को platform के secret manager से periodically rotate करो, code छुए बिना।

---

## 🟡 Real World Example
**Razorpay's** payment service runs identical Docker images in staging and production. The ONLY difference: environment variables — `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `DATABASE_URL` point to test keys/test DB in staging, and live keys/prod DB in production. If a developer accidentally hardcoded the live Razorpay secret key in `config.js` and pushed to GitHub, bots scanning public repos would detect and misuse it within minutes — this is why Razorpay enforces env-var-only secrets via pre-commit hooks that block any file containing `rzp_live_`.

## 🟡 Real Example Hindi mein
**Razorpay** का payment service staging और production में identical Docker images चलाता है। सिर्फ फ़र्क env variables का है — `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET` staging में test keys, production में live keys। अगर developer गलती से live secret key `config.js` में hardcode करके GitHub पर push कर दे, तो bots मिनटों में उसे ढूंढ कर misuse कर सकते हैं — इसलिए Razorpay pre-commit hooks से `rzp_live_` वाली कोई भी file block करता है।

---

## 💻 Code Example — Basic

```javascript
// env-basic.js
// Run with: node env-basic.js  (set PORT=4000 node env-basic.js to override)

// process.env is a plain object — every OS/platform env var lands here
console.log('NODE_ENV:', process.env.NODE_ENV || 'not set');
console.log('PORT:', process.env.PORT || 'not set (will default)');

// Simple pattern: value from env, fallback if missing
const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || 'development';

console.log(`App would start on port ${PORT} in ${NODE_ENV} mode`);

// Try it: PORT=5000 NODE_ENV=production node env-basic.js
// Output changes based on what you pass on the command line
```

## 💻 Code Example — Advanced

```javascript
// env-advanced.js
// Production-ready env loading + validation
// npm install dotenv

// Only load .env file in non-production environments.
// In production, the platform (Docker/PM2/Railway) injects vars directly —
// loading a .env file there is unnecessary and can even override real secrets.
if (process.env.NODE_ENV !== 'production') {
  require('dotenv').config(); // reads .env into process.env
}

// ─── 1. Define required variables with a schema (fail fast) ──────────────────
const REQUIRED_VARS = ['DATABASE_URL', 'JWT_SECRET', 'PORT'];

function validateEnv() {
  const missing = REQUIRED_VARS.filter((key) => !process.env[key]);
  if (missing.length > 0) {
    // Crash immediately with a clear message — don't let the app start half-broken
    console.error(`❌ Missing required env vars: ${missing.join(', ')}`);
    process.exit(1);
  }
}

validateEnv();

// ─── 2. Centralized config object — single source of truth ───────────────────
const config = {
  port: Number(process.env.PORT) || 3000,
  env: process.env.NODE_ENV || 'development',
  databaseUrl: process.env.DATABASE_URL,
  jwtSecret: process.env.JWT_SECRET,
  // Type coercion: env vars are ALWAYS strings, convert explicitly
  isProduction: process.env.NODE_ENV === 'production',
  logLevel: process.env.LOG_LEVEL || 'info',
};

// ─── 3. Never log secrets — mask them ─────────────────────────────────────────
function maskSecret(value) {
  if (!value) return 'undefined';
  return value.slice(0, 4) + '****' + value.slice(-2);
}

console.log('Config loaded:', {
  ...config,
  jwtSecret: maskSecret(config.jwtSecret), // never print the real secret
  databaseUrl: maskSecret(config.databaseUrl),
});

module.exports = config;
```

---

## 🟠 Express.js Integration

```javascript
// config.js — single place every other file imports from
if (process.env.NODE_ENV !== 'production') {
  require('dotenv').config();
}

const requiredVars = ['DATABASE_URL', 'JWT_SECRET', 'PORT', 'RAZORPAY_KEY_SECRET'];
const missing = requiredVars.filter((k) => !process.env[k]);
if (missing.length) {
  throw new Error(`Missing env vars: ${missing.join(', ')}`);
}

module.exports = {
  port: Number(process.env.PORT),
  dbUrl: process.env.DATABASE_URL,
  jwtSecret: process.env.JWT_SECRET,
  razorpayKeySecret: process.env.RAZORPAY_KEY_SECRET,
  isProd: process.env.NODE_ENV === 'production',
};

// server.js
const express = require('express');
const config = require('./config');
const app = express();

app.get('/health', (req, res) => {
  // Never expose actual secret values in responses, even in dev
  res.json({ status: 'ok', env: config.isProd ? 'production' : 'development' });
});

app.listen(config.port, () => {
  console.log(`Server running on port ${config.port} [${config.isProd ? 'PROD' : 'DEV'}]`);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Committing `.env` file to Git
✅ Correct: Add `.env` to `.gitignore` on day one; commit only `.env.example` with placeholder keys (no real values).

```javascript
// Wrong: .env committed with real secrets, visible in Git history forever
// (even deleting it later doesn't remove it from history — must rotate the secret!)

// Right: .gitignore
// .env
// .env.local
// .env.*.local

// .env.example (safe to commit)
// DATABASE_URL=postgres://user:password@localhost:5432/mydb
// JWT_SECRET=change_me_in_production
```

❌ Mistake 2: Not validating required vars, app crashes deep in request handling
✅ Correct: Validate ALL required vars at startup, before `app.listen()`.

```javascript
// Wrong: app starts fine, crashes on first DB query 2 hours later in prod
const pool = new Pool({ connectionString: process.env.DATABASE_URL }); // undefined if missing!

// Right: fail immediately at boot
if (!process.env.DATABASE_URL) {
  console.error('DATABASE_URL is required');
  process.exit(1);
}
```

---

## 🧠 Tricky Interview Question

```javascript
// What does this print?
process.env.PORT = 3000;
console.log(typeof process.env.PORT);
console.log(process.env.PORT + 1);
```
Answer: `string` then `30001`. ALL values in `process.env` are strings, regardless of what you assign — Node.js coerces them. `process.env.PORT + 1` does string concatenation (`"3000" + 1` → `"30001"`), not numeric addition. This is why `Number(process.env.PORT)` or `+process.env.PORT` is required before doing any math or comparisons (e.g. `if (process.env.PORT > 1000)` would compare strings lexically, giving wrong results for some values).

---

## ⚫ Interview Questions + Answers

Q1: Why shouldn't `.env` files be used in production containers/platforms?
A1: `.env` files are a local-development convenience loaded by `dotenv`. In production (Docker, Kubernetes, PM2, Railway, AWS ECS), the orchestration platform injects env vars directly into the process environment through its own secret-management system (AWS Secrets Manager, Docker `--env-file`/secrets, Kubernetes Secrets). Baking a `.env` file into a Docker image means secrets are embedded in the image layer — anyone who gets the image gets the secrets. Platform-injected vars are not part of the image and can be rotated without rebuilding.

Q2: How do you handle different configs for dev/staging/production?
A2: Use `NODE_ENV` to branch logic + separate `.env.development`, `.env.staging`, `.env.production` files locally (loaded conditionally), but in real staging/production deployments the actual values come from the platform's env var settings (not files). Keep a single `config.js` that reads from `process.env` with sensible defaults, so the rest of the app never checks `NODE_ENV` directly — it reads from the centralized config.

Q3: What's the risk of logging `process.env` directly?
A3: `console.log(process.env)` dumps EVERY environment variable including secrets like `JWT_SECRET`, `DATABASE_URL` (which often contains the password), cloud credentials, etc. into logs — and logs are often shipped to third-party services (Datadog, CloudWatch) or stored in plaintext files. Always mask or whitelist specific non-sensitive vars (`PORT`, `NODE_ENV`) when logging config at startup.

Q4: How do secret managers (AWS Secrets Manager, HashiCorp Vault) improve on plain env vars?
A4: Plain env vars are static — once set, they sit in the process memory and container spec. Secret managers add: (1) encryption at rest, (2) automatic rotation (e.g. DB password changes every 30 days without code changes), (3) fine-grained IAM access control over who/what can read a secret, (4) audit logs of every access. Node apps typically fetch secrets from the manager at startup via an SDK call, then populate `process.env` or an in-memory config object — avoiding ever writing the raw secret to disk.

Q5: What happens if two conflicting env vars are set — one in `.env` and one in the shell?
A5: Shell/platform-injected environment variables take precedence over `.env` file values when using `dotenv`, because `dotenv.config()` by default does NOT override already-set `process.env` keys. This is intentional — it lets platform-level overrides win over local defaults. Pass `{ override: true }` to `dotenv.config()` if you explicitly want `.env` to win, but this is rarely desired in production-like setups.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Storing any secret (API keys, DB credentials, JWT secrets, third-party tokens)
- Values differ between dev/staging/production (ports, feature flags, URLs)
- You need the same codebase/image to run in multiple environments

❌ Avoid when:
- Storing large structured config (nested JSON) — use a config file loaded conditionally instead, env vars are flat strings
- Values change extremely frequently at runtime (feature flags that toggle per-request) — use a feature-flag service/DB instead
- Non-secret, build-time constants that never change — can be baked into code/build

---

## 📊 Visual Diagram
```
LOCAL DEV                         PRODUCTION (e.g. Docker/Railway/ECS)
─────────────                     ──────────────────────────────────
.env file                         Platform secret store
  DATABASE_URL=...                  DATABASE_URL=... (injected)
  JWT_SECRET=...                    JWT_SECRET=...   (injected)
      │                                    │
      ▼ dotenv.config()                    ▼ (no dotenv needed)
  process.env  ◄─────────── same shape ────► process.env
      │                                    │
      ▼                                    ▼
  config.js (validates + centralizes)  config.js (validates + centralizes)
      │                                    │
      ▼                                    ▼
  app reads config.port, config.dbUrl  app reads config.port, config.dbUrl
  (SAME CODE PATH — only values differ)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| process.env | Node object holding all env vars (as strings) | सभी env vars (string रूप में) रखने वाला object |
| dotenv | npm package to load .env into process.env | `.env` को `process.env` में load करने वाला package |
| NODE_ENV | Standard var for environment (dev/prod) | Environment बताने वाला standard variable |
| Secrets Manager | Service for storing/rotating secrets securely | Secrets को securely store/rotate करने वाली service |
| .env.example | Template file with placeholder keys, safe to commit | Placeholder keys वाली template file, commit करना safe |

---

## ⚡ 3-Line Summary
English: 1. Env vars keep secrets and environment-specific config OUT of source code. 2. Use `dotenv` only in local dev; production platforms inject vars directly. 3. Always validate required vars at startup and never log raw secret values.
Hindi: 1. Env vars secrets और environment-specific config को source code से बाहर रखते हैं। 2. `dotenv` सिर्फ local dev में; production platforms directly vars inject करते हैं। 3. Startup पर required vars हमेशा validate करो, raw secrets कभी log न करो।

---

## ➡️ Next Topic
**270. SSL Setup with Let's Encrypt** — HTTPS कैसे enable करें production domain पर free certificates से।
