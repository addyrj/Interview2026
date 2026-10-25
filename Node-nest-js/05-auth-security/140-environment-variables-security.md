# 140. Environment Variables Security
# हिंदी में: Environment Variables Security

---

## 🔵 Simple Definition (English)
**Environment variables** are key-value pairs set outside your code (in the OS, a `.env` file, or deployment config) used to inject configuration and secrets (DB passwords, API keys, JWT secrets) at runtime — keeping sensitive data OUT of source code and allowing different values per environment (dev/staging/production).

## 🔵 सरल परिभाषा (Hindi)
**Environment variables** code के बाहर set की गई key-value pairs हैं (OS में, `.env` file में, या deployment config में) जो runtime पर configuration और secrets (DB password, API keys, JWT secrets) inject करती हैं — sensitive data को source code से बाहर रखती हैं और हर environment (dev/staging/production) के लिए अलग values allow करती हैं।

---

## 🔴 Problem it Solves
If secrets (database passwords, API keys) are hardcoded directly in source code, they get committed to git, visible to anyone with repo access, leaked in public repos, and can't vary between dev/staging/production without code changes. Once a secret lands in git history, it stays there FOREVER (even if deleted later, in a past commit) unless history is rewritten. Environment variables decouple config from code — the same codebase runs differently in different environments just by changing env values, and secrets never need to touch the code repository.

## 🔴 यह क्यों बना? (Hindi)
अगर secrets code में hardcode हों, वो git में commit हो जाते हैं, repo access वाले सभी को दिखते हैं, public repos में leak हो सकते हैं, और dev/staging/production के बीच बदलने के लिए code change चाहिए पड़ता। Environment variables config को code से decouple करती हैं — वही codebase अलग environments में अलग तरह से चलती है, secrets को repository कभी touch नहीं करना पड़ता।

---

## 🟢 How it Works — Step by Step

Step 1 → Create a `.env` file locally (NEVER committed — add to `.gitignore` immediately)
Step 2 → Use a library like `dotenv` to load `.env` into `process.env` during local development
Step 3 → Access values via `process.env.DB_PASSWORD`, `process.env.JWT_SECRET` throughout the app
Step 4 → In production, set environment variables through the deployment platform's secret mechanism (not a committed `.env` file) — Docker secrets, Kubernetes Secrets, AWS Secrets Manager, Heroku Config Vars, Vercel/Railway env settings
Step 5 → Provide a `.env.example` file (committed) listing variable NAMES ONLY (no real values) so new developers know what to configure
Step 6 → Validate required env vars exist at startup (fail fast if `JWT_SECRET` is missing, rather than running insecurely with `undefined`)
Step 7 → Never log `process.env` wholesale, never send it in error responses, and restrict who has access to production secret stores

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Local `.env` file बनाओ, `.gitignore` में add करो
Step 2 → `dotenv` library से `.env` को `process.env` में load करो
Step 3 → `process.env.VAR_NAME` से values access करो
Step 4 → Production में deployment platform के secret mechanism से env vars set करो
Step 5 → `.env.example` file commit करो (सिर्फ variable names, values नहीं)
Step 6 → Startup पर required env vars validate करो
Step 7 → `process.env` को कभी log मत करो, error responses में मत भेजो

---

## 🟡 Real World Example
**Swiggy's microservices:** Each service (order service, payment service, notification service) has its own set of secrets (DB connection strings, Razorpay API keys, SMS gateway tokens) injected as environment variables through Kubernetes Secrets — NOT stored in the git repo at all. The `.env.example` file in each repo shows developers exactly which variables they need (`DB_HOST`, `DB_PASSWORD`, `RAZORPAY_KEY`) without revealing actual production values. CI/CD pipelines inject real secrets at deploy time from a secure vault, never writing them into any file that gets committed.

## 🟡 Real Example Hindi mein
**Swiggy के microservices:** हर service के अपने secrets होते हैं (DB connection strings, Razorpay API keys) जो Kubernetes Secrets के through environment variables की तरह inject होते हैं — git repo में नहीं। `.env.example` file developers को बताती है कौन से variables चाहिए, actual values बिना दिखाए।

---

## 💻 Code Example — Basic

```javascript
// env-basic.js — using dotenv to load environment variables
// Run with: node env-basic.js (requires npm install dotenv and a .env file)

// .env file content (NEVER commit this file):
//   DB_PASSWORD=supersecret123
//   JWT_SECRET=a1b2c3d4e5f6g7h8
//   PORT=3000

require('dotenv').config();  // loads .env into process.env (only affects THIS process)

// ─── 1. ACCESS ENV VARIABLES ───────────────────────────────────────────────────
console.log('Port:', process.env.PORT);
console.log('JWT secret exists?', !!process.env.JWT_SECRET);  // log boolean, NEVER the actual value

// ─── 2. VALIDATE REQUIRED VARIABLES AT STARTUP ───────────────────────────────
const REQUIRED_ENV_VARS = ['DB_PASSWORD', 'JWT_SECRET', 'PORT'];

function validateEnv() {
  const missing = REQUIRED_ENV_VARS.filter((key) => !process.env[key]);
  if (missing.length > 0) {
    console.error(`Missing required environment variables: ${missing.join(', ')}`);
    process.exit(1);  // fail fast — don't let the app run in a misconfigured state
  }
}

validateEnv();
console.log('All required environment variables present. Starting app...');
```

## 💻 Code Example — Advanced

```javascript
// env-advanced.js — typed/validated env config with Zod + multi-environment support

const { z } = require('zod');
require('dotenv').config({
  path: `.env.${process.env.NODE_ENV || 'development'}`,  // .env.production, .env.development, etc.
});

// ─── 1. SCHEMA FOR ENV VARIABLES (type-safe, validated once at startup) ─────
const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'staging', 'production']).default('development'),
  PORT: z.coerce.number().int().positive().default(3000),
  DB_HOST: z.string().min(1),
  DB_PASSWORD: z.string().min(8),
  JWT_SECRET: z.string().min(32, 'JWT_SECRET must be at least 32 characters for security'),
  RAZORPAY_KEY: z.string().startsWith('rzp_'),
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
});

// ─── 2. PARSE AND EXPORT A TYPED CONFIG OBJECT ───────────────────────────────
let config;
try {
  config = envSchema.parse(process.env);  // throws if validation fails
} catch (err) {
  console.error('❌ Invalid environment configuration:');
  err.errors?.forEach((e) => console.error(`   ${e.path.join('.')}: ${e.message}`));
  process.exit(1);  // fail fast — never start with invalid/missing config
}

// ─── 3. FREEZE CONFIG TO PREVENT ACCIDENTAL MUTATION ─────────────────────────
Object.freeze(config);

// Now the rest of the app imports this `config` object instead of reading
// process.env directly everywhere — centralizes validation and typing.
module.exports = config;

// Usage elsewhere in the app:
// const config = require('./env-advanced');
// db.connect({ host: config.DB_HOST, password: config.DB_PASSWORD });
```

---

## 🟠 Express.js Integration

```javascript
// server.js
const express = require('express');
const config = require('./env-advanced');  // validated, typed config

const app = express();
app.use(express.json());

// Middleware: ensure secrets never accidentally leak in error responses
app.use((err, req, res, next) => {
  // NEVER do: res.json({ error: err.message, env: process.env })
  console.error('Error:', err.message);  // log server-side only
  res.status(500).json({ error: 'Internal server error' });  // generic client response
});

app.get('/health', (req, res) => {
  // Safe to expose NON-sensitive config (not secrets) for debugging
  res.json({
    environment: config.NODE_ENV,
    logLevel: config.LOG_LEVEL,
    // NEVER include: config.DB_PASSWORD, config.JWT_SECRET
  });
});

app.listen(config.PORT, () => {
  console.log(`Server running on port ${config.PORT} in ${config.NODE_ENV} mode`);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Committing `.env` to git (even accidentally, once)
```javascript
// WRONG: forgetting to add .env to .gitignore before the first commit
// git add . && git commit -m "initial commit"   ← .env now in git history FOREVER

// CORRECT: add to .gitignore IMMEDIATELY, before ever running git add
// .gitignore:
//   .env
//   .env.*
//   !.env.example
// If already committed: rotate ALL exposed secrets immediately (git history removal
// alone is NOT enough — assume anything ever committed is permanently compromised)
```

❌ Mistake 2: Using weak/predictable values for secret env vars
```javascript
// WRONG: short, guessable secrets
// JWT_SECRET=secret123

// CORRECT: generate strong, random secrets
// node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
// JWT_SECRET=f3a8b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1
```

---

## 🧠 Tricky Interview Question

```javascript
// .env file:
//   PORT=3000
require('dotenv').config();
console.log(typeof process.env.PORT);  // ?
console.log(process.env.PORT + 1);     // ?
```
Answer: `typeof process.env.PORT` is **`'string'`** — ALL environment variables are strings, regardless of what they "look like" (even `PORT=3000` is stored as the string `"3000"`, not the number `3000`). So `process.env.PORT + 1` performs STRING concatenation, not addition: the result is `"30001"`, not `3001`. This is a classic gotcha — any numeric env var MUST be explicitly converted: `Number(process.env.PORT) + 1` or `parseInt(process.env.PORT, 10) + 1` to get the expected arithmetic result `3001`.

---

## ⚫ Interview Questions + Answers

Q1: Why shouldn't you use `.env` files directly in production (on servers/containers)?
A1: `.env` files are a LOCAL DEVELOPMENT convenience for loading config without setting real OS environment variables manually. In production, secrets should come from a proper secret management system (cloud provider's secret manager, Kubernetes Secrets, Docker secrets, CI/CD injected env vars) which offers access control, audit logging, encryption at rest, and rotation capabilities that a flat `.env` file on disk doesn't provide. A `.env` file sitting on a production server is also a juicy target if that server is ever compromised — a readable plaintext file with all your secrets.

Q2: What's the risk of committing a secret to git even if you delete it in a later commit?
A2: Git preserves FULL HISTORY — the secret remains accessible in the old commit forever (anyone can `git log` / `git show` to find it, or it may already be cached by GitHub, forks, or CI logs). Simply deleting the line in a new commit does NOT remove it from history. The only real fixes are: (1) rewriting git history (`git filter-repo`/BFG) AND force-pushing (disruptive, and doesn't help if already cloned/forked elsewhere), or (2) — the actually reliable fix — treating the secret as PERMANENTLY COMPROMISED and rotating/regenerating it immediately (new DB password, new API key, etc.).

Q3: How do you handle different configuration for development, staging, and production environments?
A3: Common patterns: (1) separate `.env.development`, `.env.staging`, `.env.production` files (only `.development` committed as an example/template, others injected by the deployment platform), loaded conditionally based on `NODE_ENV`. (2) Deployment platforms (Heroku, Vercel, AWS) have built-in per-environment config var UIs/APIs — set different values per deployed environment without any file at all. (3) Centralize and validate config through a single schema-validated module (as shown in the advanced example) so the rest of the app doesn't care WHERE the values came from.

Q4: Why should you validate required environment variables at application startup rather than letting the app run with `undefined` values?
A4: "Failing fast" at startup surfaces configuration problems immediately and loudly (clear error message, process exits) rather than letting the app run in a broken/insecure state that only fails later, unpredictably, deep in business logic (e.g., `jwt.sign(payload, undefined)` might throw a confusing error mid-request, or worse, silently produce insecure tokens). Startup validation also serves as living documentation of exactly what config the app needs.

Q5: What's the difference between a secret and a regular config value, and does it change how you handle them?
A5: A SECRET (API keys, passwords, private keys, JWT signing secrets) grants access/capability if leaked — compromise has real security consequences. A regular CONFIG value (port number, log level, feature flags, public API base URLs) is often fine to be visible/logged. Secrets need: restricted access (not every developer needs production secrets), audit logging on access, rotation capability, and NEVER appearing in logs/error messages/client responses. Regular config can be more loosely handled, though still kept out of hardcoded source for flexibility.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any value that differs between environments (dev/staging/prod) or must stay out of source code (any secret, ever).

❌ Avoid when:
- Using flat `.env` files as the PRIMARY secret store in production — use a real secret manager there instead; `.env` + `dotenv` is appropriate for local development only.

---

## 📊 Visual Diagram

```
ENV VARIABLE FLOW:
──────────────────────────────────────────────────────────

  LOCAL DEV:
    .env file (gitignored) ──► dotenv.config() ──► process.env ──► app code

  PRODUCTION:
    Secret Manager / K8s Secrets / CI-CD injected vars
         │
         ▼
    OS environment variables (set directly, no .env file involved)
         │
         ▼
    process.env ──► app code (same access pattern as dev!)

  GIT REPOSITORY (committed):
    .env.example  →  DB_HOST=
                      DB_PASSWORD=
                      JWT_SECRET=
    (names only, NO real values — documents what's needed)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Environment variable | OS/runtime-level config key-value pair | OS/runtime level config key-value |
| `.env` file | Local file holding dev environment variables | Dev environment variables रखने वाली local file |
| dotenv | Library loading `.env` into `process.env` | `.env` को `process.env` में load करने वाली library |
| Secret rotation | Replacing a secret with a new value periodically | Secret को नई value से replace करना |
| Fail fast | Exiting immediately on invalid startup config | Invalid config पर immediately exit होना |
| Secret manager | Dedicated secure service for storing secrets | Secrets store करने वाली dedicated secure service |

---

## ⚡ 3-Line Summary
English:
1. Environment variables keep secrets and environment-specific config out of source code, loaded via `process.env` at runtime.
2. Use `.env` + dotenv for local dev only; production secrets must come from a real secret manager, never a committed file.
3. Validate required env vars at startup (fail fast), never log/expose secrets, and treat anything ever committed to git as permanently compromised.

Hindi:
1. Environment variables secrets और environment-specific config को source code से बाहर रखती हैं, `process.env` से runtime पर load होती हैं।
2. `.env` + dotenv सिर्फ local dev के लिए; production secrets real secret manager से आनी चाहिए, committed file से नहीं।
3. Startup पर required env vars validate करो, secrets कभी log/expose मत करो, git में कभी commit हुई चीज़ को permanently compromised मानो।

---

## ➡️ Next Topic
**141. Secrets Management** — Vault, AWS Secrets Manager, rotation strategies production-grade apps के लिए।
