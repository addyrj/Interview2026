# 28. process.env — Environment Variables
# हिंदी में: process.env — Environment Variables से Configuration

---

## 🔵 Simple Definition (English)
`process.env` is an object exposing all **environment variables** available to the running Node.js process — set by the OS, shell, deployment platform, or `.env` files. It's the standard way to inject configuration (database URLs, API keys, ports, feature flags) into an app WITHOUT hardcoding them in source code.

## 🔵 सरल परिभाषा (Hindi)
`process.env` एक object है जो running Node.js process को available सभी **environment variables** expose करता है — OS, shell, deployment platform, या `.env` files से set होते हैं। यह config (database URLs, API keys, ports, feature flags) को app में inject करने का standard तरीका है, source code में hardcode किए बिना।

---

## 🔴 Problem it Solves
Hardcoding secrets (DB passwords, API keys) and environment-specific values (dev vs staging vs prod URLs) directly in source code is a security and maintainability disaster — secrets leak into git history, and switching environments means editing code. Environment variables solve this: the SAME code deploys everywhere, reading different values from `process.env` depending on where it's running, and secrets never touch version control.

## 🔴 यह क्यों बना? (Hindi)
Secrets (DB passwords, API keys) और environment-specific values (dev vs staging vs prod URLs) को directly source code में hardcode करना एक security और maintainability disaster है — secrets git history में leak हो जाते हैं, और environment बदलने के लिए code edit करना पड़ता है। Environment variables इसे solve करते हैं: वही code हर जगह deploy होता है, जहाँ चल रहा है उसके हिसाब से `process.env` से अलग values पढ़ता है, और secrets कभी version control में नहीं जाते।

---

## 🟢 How it Works — Step by Step

Step 1 → The OS/shell/platform sets environment variables BEFORE launching the Node process: `PORT=4000 node app.js` or exported in shell profile, or set in Docker/Kubernetes/PM2 config.
Step 2 → Node automatically populates `process.env` with all of these at process startup — a plain JS object, read-only keys are NOT enforced (you CAN mutate it at runtime, though it's unusual to do so).
Step 3 → Access any variable: `process.env.DATABASE_URL`. If not set, it's `undefined` — always provide a fallback: `process.env.PORT || 3000`.
Step 4 → ALL values are strings — even `process.env.DEBUG = true` in your shell becomes the string `"true"` inside Node, requiring explicit conversion for numbers/booleans.
Step 5 → For local development, a `.env` file (loaded via the `dotenv` package, covered next topic) simulates setting these variables without needing to export them in your shell every time.
Step 6 → NEVER commit `.env` files with real secrets to git — use `.gitignore`, and provide a `.env.example` template with dummy values for teammates.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → OS/shell/platform environment variables Node process launch होने से PEHLE set करता है: `PORT=4000 node app.js` या shell profile में exported, या Docker/Kubernetes/PM2 config में set।
Step 2 → Node process startup पर इन सभी से `process.env` automatically populate करता है — एक plain JS object, keys read-only enforce नहीं होती (runtime पर mutate कर सकते हो, पर यह unusual है)।
Step 3 → कोई भी variable access करो: `process.env.DATABASE_URL`। अगर set नहीं है, तो `undefined` होता है — हमेशा fallback दो: `process.env.PORT || 3000`।
Step 4 → सभी values strings होते हैं — shell में `process.env.DEBUG = true` भी Node के अंदर string `"true"` बन जाता है, numbers/booleans के लिए explicit conversion चाहिए।
Step 5 → Local development के लिए, `.env` file (`dotenv` package के through load होती है, अगला topic) हर बार shell में export किए बिना इन variables को simulate करती है।
Step 6 → `.env` files में real secrets को कभी git में commit मत करो — `.gitignore` use करो, teammates के लिए dummy values वाला `.env.example` template दो।

---

## 🟡 Real World Example
**Razorpay's multi-environment payment API:** The same codebase runs in dev, staging, and production. `process.env.RAZORPAY_KEY_ID`, `process.env.RAZORPAY_KEY_SECRET`, `process.env.DATABASE_URL` differ per environment — set via Kubernetes Secrets in prod, via `.env` locally, via CI/CD pipeline secrets in staging. The code itself never changes: `const razorpay = new Razorpay({ key_id: process.env.RAZORPAY_KEY_ID, key_secret: process.env.RAZORPAY_KEY_SECRET });` — same line of code, different real secrets depending on where it's deployed, with zero secrets committed to the repo.

## 🟡 Real Example Hindi mein
**Razorpay का multi-environment payment API:** वही codebase dev, staging, और production में चलता है। `process.env.RAZORPAY_KEY_ID`, `process.env.RAZORPAY_KEY_SECRET`, `process.env.DATABASE_URL` हर environment में अलग होते हैं — prod में Kubernetes Secrets से set, local में `.env` से, staging में CI/CD pipeline secrets से। Code खुद कभी नहीं बदलता: `const razorpay = new Razorpay({ key_id: process.env.RAZORPAY_KEY_ID, key_secret: process.env.RAZORPAY_KEY_SECRET });` — same code line, deploy कहाँ हुआ उसके हिसाब से अलग real secrets, repo में zero secrets committed।

---

## 💻 Code Example — Basic

```javascript
// envBasics.js — reading environment variables
console.log('NODE_ENV:', process.env.NODE_ENV); // undefined if not explicitly set

// Always provide fallbacks for optional config
const port = process.env.PORT || 3000; // string "3000" OR number 3000 — note the type!
console.log('Port (raw):', port, typeof port);

// Convert types explicitly — process.env values are ALWAYS strings
const portNumber = Number(process.env.PORT) || 3000;
console.log('Port (number):', portNumber, typeof portNumber);

// Boolean conversion — common bug source
const isDebugString = process.env.DEBUG; // e.g. "false" (a STRING, not a boolean)
const isDebugBoolean = process.env.DEBUG === 'true'; // correct way to check boolean-like env vars
console.log('DEBUG string:', isDebugString, '| DEBUG boolean:', isDebugBoolean);

// Run with: PORT=4000 DEBUG=true node envBasics.js
```

## 💻 Code Example — Advanced

```javascript
// config.js — centralized, validated environment config (production pattern)

// Fail fast: validate required env vars at startup, not mid-request
const REQUIRED_VARS = ['DATABASE_URL', 'JWT_SECRET', 'RAZORPAY_KEY_ID'];

function validateEnv() {
  const missing = REQUIRED_VARS.filter((key) => !process.env[key]); // find unset required vars
  if (missing.length > 0) {
    // Crash immediately at boot — better than a mysterious runtime failure later
    throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
  }
}

validateEnv(); // call at module load time, so the app never starts misconfigured

// Centralize all config reads in ONE place — never scatter process.env.X across the codebase
const config = Object.freeze({
  env: process.env.NODE_ENV || 'development',
  port: Number(process.env.PORT) || 3000,
  databaseUrl: process.env.DATABASE_URL,
  jwtSecret: process.env.JWT_SECRET,
  isProduction: process.env.NODE_ENV === 'production',
  razorpay: {
    keyId: process.env.RAZORPAY_KEY_ID,
    keySecret: process.env.RAZORPAY_KEY_SECRET,
  },
  // Numeric with sane default and bounds checking
  maxRetries: Math.min(Number(process.env.MAX_RETRIES) || 3, 10),
});

module.exports = config;

// -------------------------------------------------------

// server.js — consumes the centralized config, never touches process.env directly
const config = require('./config');
console.log(`Starting in ${config.env} mode on port ${config.port}`);

if (config.isProduction) {
  console.log('Production safety checks enabled');
}
```

---

## 🟠 Express.js Integration

```javascript
// server.js — Express app driven entirely by environment config
require('dotenv').config(); // load .env file into process.env (covered next topic)
const express = require('express');
const config = require('./config'); // the validated config module from above

const app = express();

// Conditionally enable middleware based on environment
if (!config.isProduction) {
  const morgan = require('morgan');
  app.use(morgan('dev')); // verbose request logging only in dev/staging
}

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', environment: config.env }); // never leak secrets in responses!
});

app.listen(config.port, () => {
  console.log(`Server running in ${config.env} on port ${config.port}`);
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Treating `process.env` values as their "natural" type
```javascript
// Wrong — Boolean("false") is TRUE because any non-empty string is truthy!
if (Boolean(process.env.FEATURE_FLAG)) {
  enableFeature(); // enables even when FEATURE_FLAG="false"
}

// Right — explicitly compare the string value
if (process.env.FEATURE_FLAG === 'true') {
  enableFeature(); // only enables when the string is exactly "true"
}
```

❌ Mistake 2: Committing `.env` files (with real secrets) to git
```javascript
// Wrong — .env with real DB_PASSWORD=supersecret123 committed to the repo
// Now it's in git history FOREVER, even if deleted in a later commit

// Right — add .env to .gitignore, commit only a .env.example with placeholders
// .gitignore:
//   .env
// .env.example (committed, safe):
//   DATABASE_URL=postgres://user:password@localhost:5432/dbname
//   JWT_SECRET=replace_with_real_secret
```

---

## 🧠 Tricky Interview Question

```javascript
// run: node app.js  (no NODE_ENV set)
console.log(process.env.NODE_ENV);                  // ?
console.log(process.env.NODE_ENV === undefined);    // ?
console.log(typeof process.env.NODE_ENV);            // ?

process.env.NODE_ENV = 'production'; // mutate inside the running process
console.log(process.env.NODE_ENV);                  // ?
```
Answer: First three print **`undefined`**, **`true`**, **`"undefined"`** (note: `typeof undefined` is the STRING `"undefined"`). After the mutation, it prints **`"production"`**. The tricky part: `process.env` is a real, MUTABLE plain object inside the current process — you CAN assign to it at runtime, and that change is visible to any code in the same process reading `process.env.NODE_ENV` afterward (though it does NOT change the actual OS-level environment variable or affect other already-running processes — only this process's in-memory `process.env` object).

---

## ⚫ Interview Questions + Answers

Q1: What type are all values in `process.env`, and why does this matter?
A1: All values are STRINGS, regardless of how they look. `process.env.PORT` is `"3000"` not `3000`; `process.env.DEBUG` is `"false"` not `false`. This matters because naive type coercion (`Boolean("false")` → `true`) causes real bugs — always explicitly convert: `Number(x)` for numbers, `x === 'true'` for booleans.

Q2: How do you validate that required environment variables are set before the app starts?
A2: At module load time (before the server starts listening), loop through a list of required keys and check `process.env[key]` is truthy; if any are missing, `throw` an error or call `process.exit(1)` immediately. This "fail fast" pattern catches misconfiguration at deploy/boot time rather than causing a confusing runtime error deep in a request handler hours later. Libraries like `envalid` or `joi` can formalize this with schema validation.

Q3: What's the difference between setting an env var in the shell vs. in a `.env` file?
A3: Shell-exported variables (`export PORT=4000` or `PORT=4000 node app.js`) are set at the OS/shell process level and are inherited by the Node process automatically — no code needed. `.env` file variables are NOT automatically loaded by Node — you need a package like `dotenv` to read the file and manually copy its key-values INTO `process.env` at app startup. `.env` files are purely a developer convenience for local environments; real deployments typically use actual OS/platform-level environment variables or secret managers.

Q4: Is it safe to log `process.env` for debugging?
A4: No — `process.env` typically contains secrets (API keys, DB passwords, JWT secrets). Logging the entire object (`console.log(process.env)`) risks leaking secrets into log files, error-tracking services (Sentry), or CI/CD console output, which may be less secure than the secrets themselves. Log only specific, non-sensitive keys you need to debug, and mask anything secret-like.

Q5: How would you support different config per environment (dev/staging/production) cleanly?
A5: Centralize ALL `process.env` reads into a single `config.js` module (as shown in the Advanced example) that validates and exposes typed, well-named values. Set `NODE_ENV` to distinguish environments, and either (a) load different `.env.development`/`.env.production` files conditionally, or (b) rely on the deployment platform (Kubernetes ConfigMaps/Secrets, Docker Compose env files, CI/CD secret stores) to inject the right values per environment — the application code itself stays identical across all environments.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Storing any config that differs between environments: DB URLs, API keys, feature flags, ports.
- Keeping secrets OUT of source code and version control.
- Needing the same build/image to run correctly across dev/staging/prod with different behavior.

❌ Avoid when:
- Storing large, structured, or frequently-changing config (env vars are best for small key-value pairs, not entire JSON config blobs — use a config file or remote config service for that).
- Storing highly sensitive production secrets with no rotation/audit trail — consider a dedicated secret manager (AWS Secrets Manager, HashiCorp Vault) for stricter environments, using env vars only as the final injection mechanism.

---

## 📊 Visual Diagram
```
ENVIRONMENT VARIABLE FLOW:
──────────────────────────────────────────────────────────

  Shell / OS            Docker/K8s Secrets         .env file (dev only)
  export PORT=4000       env: DATABASE_URL=...       PORT=3000
       │                       │                           │
       └───────────────┬───────┴─────────────┬─────────────┘
                        ▼                     ▼
                 process.env (populated at process startup)
                        │
                        ▼
              config.js (centralized, validated, typed)
                        │
                        ▼
              app code reads config.port, config.databaseUrl, ...
              (never reads process.env directly, scattered everywhere)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| process.env | Object of environment variables | Environment variables का object |
| NODE_ENV | Standard var for environment name | Environment का नाम बताने वाला var |
| .env file | Local file simulating env vars | Local env variables वाली file |
| Fail fast | Crash at startup on bad config | Startup पर ही crash हो जाना |
| Secret manager | Secure secret storage service | Secrets रखने वाली secure service |
| Type coercion bug | Wrong type assumption causing bugs | गलत type assume करने से bug |

---

## ⚡ 3-Line Summary
English: `process.env` holds all environment variables as strings — the standard way to inject per-environment config and secrets without hardcoding them in source. Always explicitly convert types (`Number()`, `=== 'true'`) and validate required variables at startup to fail fast on misconfiguration. Never commit real `.env` secrets to git — use `.gitignore` plus a `.env.example` template.
Hindi: `process.env` सभी environment variables को strings की तरह रखता है — per-environment config और secrets को source में hardcode किए बिना inject करने का standard तरीका। हमेशा types को explicitly convert करो (`Number()`, `=== 'true'`) और startup पर required variables validate करो ताकि misconfiguration पर fail fast हो। Real `.env` secrets को कभी git में commit मत करो — `.gitignore` plus `.env.example` template use करो।

---

## ➡️ Next Topic
**29. dotenv Package** — how to load `.env` files into `process.env` for local development.
