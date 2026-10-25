# 249. Environment Config Management
# हिंदी में: Environment Config Management — Environment के हिसाब से Settings

---

## 🔵 Simple Definition (English)
**Environment Config Management** is the practice of keeping all environment-specific values (DB URLs, API keys, ports, secrets) outside the code — in environment variables or config files — so the same codebase runs correctly in development, staging, and production without code changes. Node.js apps typically use `.env` files with the `dotenv` package, or a proper config layer (`config`, `convict`, `zod`-validated env) for larger systems.

## 🔵 सरल परिभाषा (Hindi)
**Environment Config Management** का मतलब है सभी environment-specific values (DB URL, API keys, port, secrets) को code से बाहर रखना — environment variables या config files में — ताकि same codebase development, staging, production में बिना code बदले सही तरीके से चले। Node.js apps में `.env` file + `dotenv` package common है, बड़े systems में proper validated config layer use होता है।

---

## 🔴 Problem it Solves
```
WITHOUT CONFIG MANAGEMENT:
  const dbUrl = "mongodb://prod-user:password123@prod-cluster.com/db";
  const stripeKey = "sk_live_51H8xxxxxxxxxxxx";

  Problems:
    1. Secrets committed to git — leaked on GitHub, scraped by bots in seconds
    2. Same hardcoded value for dev/staging/prod — can't switch environments
    3. Changing a value needs a code change + redeploy
    4. Different developers need different local DB — conflicts in code
    5. No single source of truth — same key spread across 10 files

WITH CONFIG MANAGEMENT:
  // .env (NOT committed, in .gitignore)
  DATABASE_URL=mongodb://localhost:27017/myapp_dev
  STRIPE_SECRET_KEY=sk_test_xxxx
  PORT=5000

  // code reads from process.env, never hardcoded
  const dbUrl = process.env.DATABASE_URL;

  Benefits:
    1. Secrets never touch git history
    2. Same code, different .env per environment (dev/staging/prod)
    3. Change config without redeploying code (just restart with new env)
    4. Easy onboarding — copy `.env.example`, fill your own values
    5. Centralized — one file, one source of truth
```

## 🔴 यह क्यों बना? (Hindi)
```
Pehle: secrets code में hardcoded, git पर push ho jaate, bots scrape kar lete
Problem: ek hi code, alag-alag environment (dev/staging/prod) ke liye kaam nahi karta tha
Solution: .env file + process.env — secrets bahar, code environment-agnostic ban gaya
```

---

## 🟢 How it Works — Step by Step

Step 1 → Create `.env` file at project root with KEY=VALUE pairs (no spaces around `=`).
Step 2 → Add `.env` to `.gitignore` so it's never committed; commit `.env.example` with dummy values instead.
Step 3 → Load env vars early using `require('dotenv').config()` before any other code runs.
Step 4 → Access values via `process.env.KEY_NAME` anywhere in the app.
Step 5 → Validate required env vars at startup (fail fast) — missing `DATABASE_URL`? Crash immediately, don't run with `undefined`.
Step 6 → Use different `.env` files per environment: `.env.development`, `.env.production`, `.env.test`, loaded conditionally via `NODE_ENV`.
Step 7 → In production (Docker, PM2, cloud), inject env vars directly via the platform (no `.env` file at all) — more secure than shipping a file.

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → root में .env file banao KEY=VALUE format mein
Step 2 → .gitignore mein .env add karo, .env.example commit karo (dummy values ke saath)
Step 3 → dotenv.config() sabse pehle call karo
Step 4 → process.env.KEY_NAME se access karo
Step 5 → startup pe zaroori vars validate karo — missing ho to app crash kare, silently undefined na chale
Step 6 → NODE_ENV ke hisaab se alag .env file load karo (dev/staging/prod)
Step 7 → production mein .env file ship mat karo — Docker/PM2/cloud platform se directly env vars inject karo
```

---

## 🟡 Real World Example
**Swiggy backend:** The order-service repo has one codebase but runs in 4 environments — local dev, QA, staging, production. Each environment has its own `DATABASE_URL`, `REDIS_URL`, `RAZORPAY_KEY`, and `LOG_LEVEL`. Developers never see production secrets — those are injected directly into the Kubernetes pod via Secrets Manager (AWS Secrets Manager / HashiCorp Vault), while local devs use a `.env` file copied from `.env.example` with sandboxed test keys. A startup validator (using `zod`) checks that all 15 required env vars exist and are the right type — if `RAZORPAY_KEY` is missing, the pod fails health checks and never serves traffic, catching misconfiguration before it reaches customers.

## 🟡 Real Example Hindi mein
Swiggy ke order-service mein ek hi code 4 environments (dev, QA, staging, prod) mein chalta hai. Har environment ki apni `DATABASE_URL`, `REDIS_URL`, `RAZORPAY_KEY` hoti hai. Production secrets developers ko nahi dikhte — wo Kubernetes Secrets Manager se directly inject hote hain. Startup pe `zod` validator check karta hai ki saare 15 required vars maujood hain — missing hone par pod traffic serve nahi karta, galti production tak pahunchne se pehle hi pakdi jaati hai.

---

## 💻 Code Example — Basic

```javascript
// config-basics.js
// npm install dotenv

require('dotenv').config();  // loads .env file into process.env (call this FIRST, before other requires)

// Reading values with sensible fallbacks for optional vars
const config = {
  port: process.env.PORT || 3000,                 // fallback to 3000 if not set
  nodeEnv: process.env.NODE_ENV || 'development',  // default environment
  dbUrl: process.env.DATABASE_URL,                 // no fallback — this MUST be set
  jwtSecret: process.env.JWT_SECRET,               // no fallback — secret, must be set
  logLevel: process.env.LOG_LEVEL || 'info',
};

// Fail fast: crash immediately if critical vars are missing
// (better to crash at startup than fail mysteriously later at runtime)
const requiredVars = ['dbUrl', 'jwtSecret'];
for (const key of requiredVars) {
  if (!config[key]) {
    console.error(`FATAL: Missing required config: ${key}`);
    process.exit(1);  // exit code 1 = error, container orchestrators detect this
  }
}

console.log(`Starting app in ${config.nodeEnv} mode on port ${config.port}`);
module.exports = config;

// .env file (create this in project root, add to .gitignore):
// PORT=4000
// NODE_ENV=development
// DATABASE_URL=mongodb://localhost:27017/myapp_dev
// JWT_SECRET=dev-only-secret-change-in-prod
// LOG_LEVEL=debug
```

## 💻 Code Example — Advanced

```javascript
// config-advanced.js — Validated, typed config layer using zod
// npm install dotenv zod

const path = require('path');
const dotenv = require('dotenv');
const { z } = require('zod');

// Load the right .env file based on NODE_ENV
// e.g. .env.production, .env.staging, .env.development, .env.test
const envFile = `.env.${process.env.NODE_ENV || 'development'}`;
dotenv.config({ path: path.resolve(process.cwd(), envFile) });
dotenv.config();  // also load base .env as fallback for shared values

// Define a schema — this is the single source of truth for what config should look like
const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'staging', 'production', 'test']).default('development'),
  PORT: z.coerce.number().int().positive().default(3000),  // coerce string "3000" -> number 3000
  DATABASE_URL: z.string().url(),                           // must be a valid URL, required
  REDIS_URL: z.string().url().optional(),
  JWT_SECRET: z.string().min(32, 'JWT_SECRET must be at least 32 chars'),  // enforce strong secret
  JWT_REFRESH_SECRET: z.string().min(32),
  RAZORPAY_KEY: z.string().min(1),
  RAZORPAY_SECRET: z.string().min(1),
  LOG_LEVEL: z.enum(['error', 'warn', 'info', 'debug']).default('info'),
  MAX_UPLOAD_MB: z.coerce.number().default(10),
});

// Parse process.env against schema — throws with a detailed message on any mismatch
function loadConfig() {
  try {
    const parsed = envSchema.parse(process.env);
    return {
      env: parsed.NODE_ENV,
      port: parsed.PORT,
      db: { url: parsed.DATABASE_URL },
      redis: { url: parsed.REDIS_URL },
      jwt: { secret: parsed.JWT_SECRET, refreshSecret: parsed.JWT_REFRESH_SECRET },
      razorpay: { key: parsed.RAZORPAY_KEY, secret: parsed.RAZORPAY_SECRET },
      logLevel: parsed.LOG_LEVEL,
      maxUploadMb: parsed.MAX_UPLOAD_MB,
      isProd: parsed.NODE_ENV === 'production',
    };
  } catch (err) {
    // ZodError lists exactly which keys are missing/invalid — great for debugging deploys
    console.error('❌ Invalid environment configuration:');
    console.error(err.errors?.map((e) => `  - ${e.path.join('.')}: ${e.message}`).join('\n') || err.message);
    process.exit(1);  // never let the app boot with bad config
  }
}

const config = loadConfig();  // runs once, at module load (fail fast at startup)

module.exports = config;

// Usage elsewhere in the app:
// const config = require('./config-advanced');
// mongoose.connect(config.db.url);
// if (config.isProd) { /* enable production-only behavior */ }
```

---

## 🟠 Express.js Integration

```javascript
// server.js — wiring validated config into an Express app
const express = require('express');
const mongoose = require('mongoose');
const config = require('./config-advanced');  // validated at import time — crashes early if bad

const app = express();
app.use(express.json());

// Use config values instead of process.env scattered everywhere
mongoose.connect(config.db.url)
  .then(() => console.log('MongoDB connected'))
  .catch((err) => {
    console.error('DB connection failed:', err.message);
    process.exit(1);
  });

app.get('/health', (req, res) => {
  // Never leak secrets in health responses — only non-sensitive info
  res.json({ status: 'ok', env: config.env, uptime: process.uptime() });
});

app.post('/payments/order', (req, res) => {
  // razorpay key comes from validated config, not raw process.env
  const razorpay = require('razorpay')({
    key_id: config.razorpay.key,
    key_secret: config.razorpay.secret,
  });
  res.json({ message: 'order created (demo)' });
});

app.listen(config.port, () => {
  console.log(`Server running on port ${config.port} [${config.env}]`);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Committing `.env` file to git
```javascript
// WRONG: .env with real secrets gets pushed, scraped by bots within minutes
// git add .env   ❌

// CORRECT: .gitignore entry + commit .env.example with placeholders
// .gitignore:
// .env
// .env.*.local

// .env.example (safe to commit):
// DATABASE_URL=mongodb://localhost:27017/myapp
// JWT_SECRET=replace_with_long_random_string
```

❌ Mistake 2: Reading `process.env` directly all over the codebase
```javascript
// WRONG: scattered, untyped, no validation, string everywhere
app.listen(process.env.PORT);  // PORT is a string "3000", could be undefined

// CORRECT: centralize + validate once, import typed config everywhere
const config = require('./config');
app.listen(config.port);  // number, guaranteed to exist, validated at startup
```

---

## 🧠 Tricky Interview Question

```javascript
// .env file:
// PORT=3000

// code:
require('dotenv').config();
console.log(typeof process.env.PORT);
console.log(process.env.PORT + 1);
```
Answer: `typeof process.env.PORT` prints `"string"` — **all values from `process.env` are always strings**, even if the `.env` file looks like a number. So `process.env.PORT + 1` does **string concatenation**, not addition, printing `"30001"` not `3001`. This is a classic gotcha — always explicitly convert with `Number(process.env.PORT)` or `parseInt()`, or use a schema validator like `zod` with `z.coerce.number()` to convert types safely.

---

## ⚫ Interview Questions + Answers

Q1: Why should `.env` files never be committed to git?
A1: `.env` contains secrets (DB passwords, API keys, JWT secrets). Once committed, it lives in git history forever — even deleting the file later doesn't remove it from history. Public repos get scraped by bots within seconds of a push; even private repos risk leaking secrets if the repo is ever made public or a collaborator's account is compromised. Always add `.env` to `.gitignore` and commit a `.env.example` with placeholder values instead.

Q2: What's the difference between `.env`, `.env.development`, `.env.production`?
A2: `.env` holds values shared across all environments or acts as a fallback. `.env.development`, `.env.production`, `.env.test` hold environment-specific overrides, loaded conditionally based on `NODE_ENV`. Tools like `dotenv-flow` or custom loading logic read the environment-specific file first, then fall back to `.env` for anything not overridden. This lets you keep one dev DB URL and a different prod DB URL without any code change.

Q3: Why validate environment variables at startup instead of using them directly?
A3: Without validation, a missing or malformed env var (e.g., `DATABASE_URL` is `undefined`) causes a confusing runtime error deep in the code — maybe minutes after the app looked like it started fine. Validating at startup with a schema (zod, joi, convict) makes the app **fail fast**: it crashes immediately with a clear error message ("DATABASE_URL is required") before serving any traffic. This is critical in production — container orchestrators (Kubernetes, ECS) see the crash and can alert or roll back instead of serving broken requests.

Q4: In production (Docker/Kubernetes), should you still use a `.env` file?
A4: Generally no. Shipping a `.env` file inside a Docker image bakes secrets into the image layer, which is a security risk (anyone with image access can extract it). Instead, inject env vars directly through the platform: Docker `-e` flags or `--env-file` passed at `docker run` time (not baked into the image), Kubernetes `Secrets`/`ConfigMaps` mounted as env vars, or a cloud secrets manager (AWS Secrets Manager, Vault) that injects values at container startup. The app code doesn't change — it still reads `process.env.X` — only how the values get there changes.

Q5: How do you handle config that differs per microservice but shares some common values?
A5: Use a layered approach: a shared base config (common `LOG_LEVEL`, `NODE_ENV` conventions) combined with service-specific overrides. In practice: a shared `.env` or shared config package for conventions, plus each service's own `.env`/secrets for things like its specific `DATABASE_URL` and `SERVICE_NAME`. Many teams also centralize non-secret shared config in a Config Server or shared ConfigMap, while secrets stay in a dedicated secrets manager per service, scoped by least-privilege access.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any value differs between dev/staging/production (URLs, keys, flags)
- You have secrets (DB passwords, API keys, JWT secrets) that must never be in code
- You want to validate configuration shape fails fast at startup

❌ Avoid when:
- A value is truly a universal constant with no environment variance (e.g., `Math.PI`) — just keep it in code
- Over-engineering: a tiny script/CLI tool doesn't need a full zod schema layer, plain `dotenv` is enough

---

## 📊 Visual Diagram
```
CONFIG LOADING FLOW:
──────────────────────────────────────────────────────────

  .env.example  ──(committed, template)──▶  developer copies
                                                   │
                                                   ▼
                                          .env (gitignored, real local values)
                                                   │
  App starts  ──▶  dotenv.config()  ──▶  process.env populated
                                                   │
                                                   ▼
                                    Schema validation (zod/joi)
                                           │           │
                                      ✅ valid      ❌ invalid
                                           │           │
                                    app boots    process.exit(1)
                                    normally     clear error logged

PRODUCTION (no .env file shipped):
  Secrets Manager / K8s Secret ──▶ injected as env vars ──▶ process.env ──▶ same validation layer
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `.env` | File holding environment variables locally | Local environment variables file |
| `dotenv` | npm package that loads `.env` into `process.env` | `.env` ko load karne wala package |
| `process.env` | Node's global object holding all env vars (always strings) | Node ka env vars object |
| Fail fast | Crash immediately on bad config rather than later | Galat config par turant crash |
| Secrets Manager | Cloud service to store/inject secrets securely | Secrets store/inject karne wali cloud service |
| `.env.example` | Committed template with placeholder values | Placeholder values wali committed template file |
| Schema validation | Checking env var shape/type before use | Env vars ka shape/type check karna |

---

## ⚡ 3-Line Summary
English:
1. Keep all environment-specific values and secrets in `process.env`, loaded via `.env` files locally and injected directly by the platform in production.
2. Never commit `.env` to git — commit `.env.example` instead, and validate required vars at startup with a schema so the app fails fast on misconfiguration.
3. `process.env` values are always strings — convert types explicitly or use a coercing schema validator (zod/joi).

Hindi:
1. Saare environment-specific values aur secrets `process.env` mein rakho — local mein `.env` se, production mein platform se directly inject.
2. `.env` ko kabhi commit mat karo — `.env.example` commit karo, aur startup pe required vars validate karo taaki galat config par app turant fail ho.
3. `process.env` ke values hamesha string hote hain — explicitly convert karo ya coercing schema validator use karo.

---

## ➡️ Next Topic
**250. Logging — Winston + Morgan** — Structured application logging setup, request logging middleware, log transports for production.
