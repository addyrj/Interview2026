# 29. dotenv Package
# हिंदी में: dotenv Package — .env File से Config Load करना

---

## 🔵 Simple Definition (English)
**dotenv** is a zero-dependency npm package that loads key-value pairs from a `.env` file into `process.env`, so developers don't have to manually `export` variables in their shell every time during local development. It reads the file once at app startup and copies its contents into `process.env`.

## 🔵 सरल परिभाषा (Hindi)
**dotenv** एक zero-dependency npm package है जो `.env` file से key-value pairs को `process.env` में load करता है, ताकि developers को local development के दौरान हर बार manually shell में `export` न करना पड़े। यह app startup पर file को एक बार पढ़ता है और उसका content `process.env` में copy कर देता है।

---

## 🔴 Problem it Solves
Setting environment variables manually every time you run a script (`DATABASE_URL=... PORT=... JWT_SECRET=... node app.js`) is tedious and error-prone, especially with many variables. Shell profile exports (`~/.bashrc`) are global to the machine, not per-project, causing collisions between projects. `dotenv` solves this by letting each project keep its own `.env` file (git-ignored) at the project root, loaded automatically into `process.env` with one line of code — making local setup as simple as copying `.env.example` to `.env` and filling in values.

## 🔴 यह क्यों बना? (Hindi)
हर बार script run करते समय manually environment variables set करना (`DATABASE_URL=... PORT=... JWT_SECRET=... node app.js`) tedious और error-prone है, especially कई variables के साथ। Shell profile exports (`~/.bashrc`) पूरी machine के लिए global होते हैं, per-project नहीं, जिससे projects के बीच collisions होते हैं। `dotenv` इसे solve करता है — हर project अपनी `.env` file (git-ignored) project root में रख सकता है, एक line code से automatically `process.env` में load हो जाती है — local setup बस `.env.example` को `.env` में copy करके values भरने जितना simple हो जाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Install: `npm install dotenv`.
Step 2 → Create a `.env` file at project root: `PORT=4000\nDATABASE_URL=postgres://...`.
Step 3 → At the VERY TOP of your entry file (before anything that reads `process.env`), call `require('dotenv').config();`.
Step 4 → `dotenv` reads the `.env` file synchronously, parses each `KEY=VALUE` line, and sets `process.env.KEY = VALUE` for any key NOT already set in the real environment (by default, it does NOT override existing `process.env` values — real/platform env vars always win).
Step 5 → After `config()` runs, the rest of your app reads `process.env.X` exactly as if it had been set normally — the app code has NO idea whether the value came from `.env` or the real shell/OS.
Step 6 → `.env` is added to `.gitignore`; a `.env.example` with placeholder values is committed so teammates know what's needed.
Step 7 → In production, `.env` files are usually NOT used at all — real secrets are injected via the platform (Docker, Kubernetes Secrets, CI/CD variables) directly into `process.env`, bypassing dotenv entirely (though calling `dotenv.config()` is harmless if no `.env` file exists — it just does nothing).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Install करो: `npm install dotenv`।
Step 2 → Project root पर `.env` file बनाओ: `PORT=4000\nDATABASE_URL=postgres://...`।
Step 3 → अपनी entry file के बिल्कुल ऊपर (`process.env` पढ़ने वाली किसी भी चीज़ से पहले) `require('dotenv').config();` call करो।
Step 4 → `dotenv` `.env` file को synchronously पढ़ता है, हर `KEY=VALUE` line parse करता है, और `process.env.KEY = VALUE` set करता है उन keys के लिए जो real environment में already set नहीं हैं (default रूप से existing `process.env` values को override नहीं करता — real/platform env vars हमेशा जीतते हैं)।
Step 5 → `config()` run होने के बाद, बाकी app `process.env.X` को normally पढ़ता है जैसे वो सामान्य रूप से set हुआ हो — app code को पता नहीं होता value `.env` से आई या real shell/OS से।
Step 6 → `.env` को `.gitignore` में add किया जाता है; placeholder values वाली `.env.example` commit होती है ताकि teammates को पता चले क्या चाहिए।
Step 7 → Production में `.env` files usually use नहीं होतीं — real secrets platform से directly `process.env` में inject होते हैं (Docker, Kubernetes Secrets, CI/CD variables), dotenv को bypass करते हुए (हालाँकि `dotenv.config()` call करना harmless है अगर `.env` file नहीं मिलती — कुछ नहीं करता)।

---

## 🟡 Real World Example
**Amazon seller-dashboard microservice (local dev setup):** New engineers joining the team clone the repo, run `npm install`, copy `.env.example` to `.env`, fill in their own local DB credentials and a sandbox Razorpay test key, and run `npm run dev`. The app's `require('dotenv').config()` call at the top of `index.js` loads all of it instantly — no manual shell exports, no onboarding doc needed beyond "copy this file." In production (AWS ECS), the exact same code runs, but `.env` doesn't exist there — ECS task definitions inject real secrets directly into `process.env`, and `dotenv.config()` silently does nothing since there's no `.env` file to find.

## 🟡 Real Example Hindi mein
**Amazon seller-dashboard microservice (local dev setup):** नए engineers repo clone करते हैं, `npm install` run करते हैं, `.env.example` को `.env` में copy करते हैं, अपने local DB credentials और sandbox Razorpay test key भरते हैं, और `npm run dev` run करते हैं। App की `index.js` के top पर `require('dotenv').config()` call सब कुछ instantly load कर देती है — कोई manual shell exports नहीं, "इस file को copy करो" के अलावा कोई onboarding doc नहीं चाहिए। Production (AWS ECS) में वही exact code चलता है, पर वहाँ `.env` exist नहीं करती — ECS task definitions real secrets directly `process.env` में inject करते हैं, और `dotenv.config()` silently कुछ नहीं करता क्योंकि कोई `.env` file नहीं मिलती।

---

## 💻 Code Example — Basic

```javascript
// .env (at project root — DO NOT commit this file)
// PORT=4000
// DATABASE_URL=postgres://localhost:5432/mydb
// JWT_SECRET=dev_secret_key_123

// -------------------------------------------------------

// index.js — must require+config dotenv BEFORE reading process.env
require('dotenv').config(); // reads .env, populates process.env

console.log('PORT:', process.env.PORT);               // "4000" (string)
console.log('DATABASE_URL:', process.env.DATABASE_URL); // "postgres://localhost:5432/mydb"
console.log('JWT_SECRET:', process.env.JWT_SECRET);     // "dev_secret_key_123"

// If a variable is NOT in .env and NOT set in shell, it's undefined
console.log('MISSING_VAR:', process.env.MISSING_VAR);  // undefined
```

## 💻 Code Example — Advanced

```javascript
// config/env.js — production-grade dotenv setup with environment-specific files
const path = require('path');
const dotenv = require('dotenv');

// Decide which .env file to load based on NODE_ENV
// e.g. .env.development, .env.test, .env.production (rarely used in real prod)
const envFile = `.env.${process.env.NODE_ENV || 'development'}`;
const envPath = path.join(__dirname, '..', envFile);

// Load the environment-specific file (silently does nothing if the file is missing)
const result = dotenv.config({ path: envPath });

if (result.error && process.env.NODE_ENV !== 'production') {
  // In production we expect .env files to be absent (secrets come from the platform)
  console.warn(`Warning: could not load ${envFile} — using existing process.env values`);
}

// dotenv does NOT override already-set process.env values by default —
// so real platform secrets (Docker/K8s) always take priority over .env file contents.
// This is "safe layering": .env for local convenience, platform env for real deploys.

module.exports = {
  nodeEnv: process.env.NODE_ENV || 'development',
  port: Number(process.env.PORT) || 3000,
  databaseUrl: process.env.DATABASE_URL,
};

// -------------------------------------------------------

// dotenv-expand pattern — referencing one env var inside another (needs dotenv-expand package)
// .env:
//   BASE_URL=https://api.example.com
//   USERS_ENDPOINT=${BASE_URL}/users
// require('dotenv-expand').expand(dotenv.config());
// process.env.USERS_ENDPOINT → "https://api.example.com/users"
```

---

## 🟠 Express.js Integration

```javascript
// server.js — Express app loading dotenv FIRST, before any other require
require('dotenv').config(); // MUST be the very first line (or very early) in the entry file

const express = require('express');
const app = express();

// By the time this runs, process.env is fully populated from .env
const PORT = process.env.PORT || 3000;
const DB_URL = process.env.DATABASE_URL;

if (!DB_URL) {
  console.error('FATAL: DATABASE_URL is not set. Check your .env file.');
  process.exit(1); // fail fast rather than limping along misconfigured
}

app.get('/', (req, res) => res.send('API running'));

app.listen(PORT, () => console.log(`Server listening on port ${PORT}`));
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling `dotenv.config()` AFTER modules that already read `process.env`
```javascript
// Wrong — db.js reads process.env.DATABASE_URL at require-time, BEFORE dotenv loads it
const db = require('./db');          // db.js does: const url = process.env.DATABASE_URL (undefined here!)
require('dotenv').config();           // too late — db.js already captured undefined

// Right — load dotenv FIRST, before requiring any module that reads process.env
require('dotenv').config();           // load env vars first
const db = require('./db');          // now db.js sees the correct DATABASE_URL
```

❌ Mistake 2: Committing `.env` to git, or forgetting `.env.example`
```javascript
// Wrong — .env (with real secrets) gets committed because .gitignore wasn't set up
// git add . && git commit -m "add env"   ← secrets now in git history forever

// Right — .gitignore contains:
//   .env
// And a safe .env.example is committed with placeholder values:
//   DATABASE_URL=postgres://user:pass@localhost:5432/dbname
//   JWT_SECRET=replace_me
```

---

## 🧠 Tricky Interview Question

```javascript
// .env file contains: PORT=5000

// Terminal:
// $ PORT=9000 node app.js

// app.js:
require('dotenv').config();
console.log(process.env.PORT); // ?
```
Answer: Prints **`9000`**, NOT `5000`. By default, `dotenv.config()` does **NOT override** environment variables that are already set in `process.env` before it runs. Since the shell set `PORT=9000` before launching Node, `process.env.PORT` already equals `"9000"` by the time `dotenv.config()` executes — dotenv sees the key already exists and skips it. This "existing env wins" behavior is intentional: it lets real deployment platforms (which set env vars directly) always take priority over a `.env` file, even if both happen to be present. (You CAN force override with `dotenv.config({ override: true })`, but this is rarely desired.)

---

## ⚫ Interview Questions + Answers

Q1: Does `dotenv` work in production?
A1: Technically yes — `require('dotenv').config()` is harmless even if no `.env` file exists (it just silently does nothing, or logs an error you can choose to ignore). But it's generally NOT the recommended way to manage secrets in production. Production environments typically inject secrets directly via the platform (Docker env files, Kubernetes Secrets, cloud provider parameter stores, CI/CD pipeline secrets) which is more secure and auditable than a flat text `.env` file sitting on a server's disk.

Q2: What happens if you call `dotenv.config()` after a module that reads `process.env` has already loaded?
A2: That module already captured `undefined` (or whatever was previously set) for any variable it read at require-time, because `require()` executes the module's top-level code immediately and synchronously. Loading dotenv afterward doesn't retroactively fix values already read into local variables. The fix: always `require('dotenv').config()` as the FIRST line in your application's entry point, before requiring any other module.

Q3: Does dotenv override existing `process.env` values by default?
A3: No — by default, if a key already exists in `process.env` (set by the OS/shell/platform BEFORE Node started), dotenv will NOT overwrite it with the `.env` file's value. This means real environment variables always take priority over `.env` file contents, which is the safe default for layering local dev convenience under real deployment configuration. Pass `{ override: true }` to `config()` to change this behavior if truly needed.

Q4: What's the format of a `.env` file, and are there any gotchas?
A4: Simple `KEY=VALUE` lines, one per line, no `export`, no quotes needed for simple strings (though quotes are supported for values with spaces: `NAME="John Doe"`). Comments start with `#`. Gotchas: no built-in support for referencing other variables within the file (`${OTHER_VAR}`) unless you also use the companion `dotenv-expand` package; trailing whitespace/comments on the same line as a value can sometimes cause parsing surprises; and multiline values need explicit `\n` escaping or quoting.

Q5: How would you manage different `.env` files for different environments (dev, test, staging)?
A5: Create separate files like `.env.development`, `.env.test`, `.env.production.local`, and load the right one based on `NODE_ENV`: `dotenv.config({ path: `.env.${process.env.NODE_ENV}` })`. Tools like `dotenv-flow` or Next.js's built-in env handling automate this cascading pattern (e.g., `.env`, then `.env.local` overrides, then `.env.[mode]` overrides) so you don't have to hand-roll the file-selection logic yourself for larger projects.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Setting up local development environments where team members need project-specific config without touching global shell profiles.
- Prototyping or small projects without a full secrets-management platform yet.
- Keeping onboarding simple: "copy `.env.example` to `.env` and fill in values."

❌ Avoid when:
- Managing production secrets at scale — prefer platform-native secret injection (Kubernetes Secrets, AWS Secrets Manager, Vault) over flat `.env` files on disk.
- You need secret rotation, audit logs, or fine-grained access control — `.env` files have none of this.

---

## 📊 Visual Diagram
```
DOTENV LOADING FLOW:
──────────────────────────────────────────────────────────

  Project root/
    .env            ← PORT=4000, DB_URL=... (git-ignored, local only)
    .env.example    ← PORT=3000, DB_URL=placeholder (committed, safe)
    index.js

  index.js execution order:
    1. require('dotenv').config()
         → reads .env file
         → for each KEY=VALUE:
             if process.env.KEY already set → SKIP (platform env wins)
             else → process.env.KEY = VALUE
    2. require('./config')   ← now safely reads fully-populated process.env
    3. require('./server')   ← app starts with correct config

  PRODUCTION (no .env file present):
    dotenv.config() → finds no file → does nothing
    process.env already populated by Docker/K8s/CI → app works identically
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| dotenv | Package loading .env into process.env | .env को process.env में load करने वाला package |
| .env | Local file with KEY=VALUE pairs | KEY=VALUE pairs वाली local file |
| .env.example | Committed template with placeholders | Placeholder वाला committed template |
| override option | Force dotenv to overwrite existing vars | Existing vars को force overwrite करना |
| dotenv-expand | Companion package for var references | Variable references के लिए companion package |
| Fail fast | Crash immediately on missing config | Missing config पर immediately crash |

---

## ⚡ 3-Line Summary
English: `dotenv` loads a local `.env` file's key-value pairs into `process.env`, giving each project its own config without manual shell exports, purely for local development convenience. It must be required and configured FIRST in the entry file, before any other module reads `process.env`, and it never overrides already-set real environment variables by default. Production environments should inject secrets via the platform directly, treating `.env` files as a dev-only convenience, never committed to git.
Hindi: `dotenv` local `.env` file के key-value pairs को `process.env` में load करता है, हर project को अपना config देता है बिना manual shell exports के, सिर्फ local development convenience के लिए। इसे entry file में सबसे पहले require और configure करना चाहिए, किसी भी दूसरे module के `process.env` पढ़ने से पहले, और यह default रूप से already-set real environment variables को override नहीं करता। Production environments को secrets platform से directly inject करना चाहिए, `.env` files को सिर्फ dev-only convenience समझो, git में कभी commit मत करो।

---

## ➡️ Next Topic
**30. Command Line Arguments (process.argv)** — parsing arguments passed to a Node script from the terminal.
