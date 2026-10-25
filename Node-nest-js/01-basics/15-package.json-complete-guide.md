# 15. package.json — Complete Guide
# हिंदी में: package.json — Complete Guide

---

## 🔵 Simple Definition (English)
**`package.json`** is the manifest file at the root of every Node.js project — it declares the project's name, version, dependencies, scripts, entry point, and metadata. Every `npm`/`yarn`/`pnpm` command reads this file to know what to install and how to run your project.

## 🔵 सरल परिभाषा (Hindi)
**`package.json`** हर Node.js project की root में मौजूद manifest file है — यह project का name, version, dependencies, scripts, entry point, और metadata बताती है। हर `npm`/`yarn`/`pnpm` command इसी file को पढ़कर जानता है क्या install करना है और project कैसे चलाना है।

---

## 🔴 Problem it Solves
Without a standard manifest, every project would need custom documentation for "how do I install this" and "how do I run this." `package.json` standardizes project metadata and automation (via `scripts`) so ANY Node.js developer can run `npm install && npm start` on ANY project and expect it to work — a universal contract across the entire ecosystem.

## 🔴 यह क्यों बना? (Hindi)
एक standard manifest के बिना हर project को "इसे कैसे install करें" और "इसे कैसे चलाएं" के लिए custom documentation चाहिए होती। `package.json` project metadata और automation (via `scripts`) को standardize करता है ताकि कोई भी Node.js developer किसी भी project पर `npm install && npm start` चला सके और काम करने की उम्मीद रख सके — पूरे ecosystem में एक universal contract।

---

## 🟢 How it Works — Step by Step

Step 1 → `npm init` (or `npm init -y` for defaults) generates a basic `package.json` interactively or instantly.
Step 2 → Core identity fields: `name`, `version` (semver), `description`, `main` (entry point file, e.g., `"index.js"`), `author`, `license`.
Step 3 → **`dependencies`**: packages required at RUNTIME (e.g., `express`, `pg`) — installed in production too.
Step 4 → **`devDependencies`**: packages needed only during DEVELOPMENT (e.g., `jest`, `eslint`, `nodemon`) — skipped with `npm install --production` or `NODE_ENV=production npm ci`.
Step 5 → **`scripts`**: named shell commands runnable via `npm run <name>` (e.g., `"start": "node server.js"`, `"test": "jest"`) — the project's automation entry points.
Step 6 → **`engines`**: specifies compatible Node.js/npm version ranges (e.g., `{"node": ">=18"}`) — informational by default, enforceable via tooling/CI.
Step 7 → **`type`**: `"module"` makes `.js` files use ES Modules (`import`/`export`) by default instead of CommonJS; omitting it or setting `"commonjs"` keeps the traditional `require()` system.
Step 8 → **`exports`**: controls what parts of a published package are importable from outside, enabling encapsulation (modern alternative/addition to `main`).
Step 9 → Running any `npm`/`yarn`/`pnpm` command re-reads this file EVERY time — it's the single source of truth for the whole project's tooling.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `npm init` (या defaults के लिए `npm init -y`) interactively या instantly basic `package.json` बनाता है।
Step 2 → Core identity fields: `name`, `version` (semver), `description`, `main` (entry point file, जैसे `"index.js"`), `author`, `license`।
Step 3 → **`dependencies`**: RUNTIME पर ज़रूरी packages (जैसे `express`, `pg`) — production में भी install होती हैं।
Step 4 → **`devDependencies`**: सिर्फ DEVELOPMENT में ज़रूरी packages (जैसे `jest`, `eslint`, `nodemon`) — `npm install --production` या `NODE_ENV=production npm ci` से skip होती हैं।
Step 5 → **`scripts`**: named shell commands जो `npm run <name>` से चलती हैं (जैसे `"start": "node server.js"`, `"test": "jest"`) — project की automation entry points।
Step 6 → **`engines`**: compatible Node.js/npm version ranges बताता है (जैसे `{"node": ">=18"}`) — default रूप से informational, tooling/CI से enforceable।
Step 7 → **`type`**: `"module"` से `.js` files default रूप से ES Modules (`import`/`export`) use करती हैं CommonJS की जगह; छोड़ने या `"commonjs"` set करने पर traditional `require()` system रहता है।
Step 8 → **`exports`**: control करता है published package के किस हिस्से को बाहर से import किया जा सकता है, encapsulation देता है (`main` का modern alternative/addition)।
Step 9 → कोई भी `npm`/`yarn`/`pnpm` command हर बार इस file को फिर पढ़ता है — यह पूरे project tooling का single source of truth है।

---

## 🟡 Real World Example
**A Zomato-style backend microservice's `package.json`:** `dependencies` includes `express`, `pg`, `redis`, `jsonwebtoken` (needed in production); `devDependencies` includes `jest`, `supertest`, `nodemon`, `eslint` (dev-only). `scripts` defines `"start": "node src/server.js"` for production, `"dev": "nodemon src/server.js"` for local development with auto-restart, and `"test": "jest --coverage"` for CI. The `engines` field pins `"node": ">=20.0.0"` to match the team's Docker base image, preventing version drift between developer laptops and production.

## 🟡 Real Example Hindi mein
**Zomato-style backend microservice का `package.json`:** `dependencies` में `express`, `pg`, `redis`, `jsonwebtoken` (production में ज़रूरी); `devDependencies` में `jest`, `supertest`, `nodemon`, `eslint` (सिर्फ dev में)। `scripts` में `"start": "node src/server.js"` production के लिए, `"dev": "nodemon src/server.js"` local development के लिए auto-restart के साथ, और `"test": "jest --coverage"` CI के लिए। `engines` field `"node": ">=20.0.0"` pin करता है team की Docker base image से match करने के लिए, developer laptops और production के बीच version drift रोकता है।

---

## 💻 Code Example — Basic
```javascript
// generate-package-json.js
// Programmatically create a minimal, valid package.json (what `npm init -y` does)

const fs = require('fs');

const packageJson = {
  name: 'zomato-style-order-service',
  version: '1.0.0',
  description: 'Order management microservice',
  main: 'src/server.js',
  type: 'commonjs', // or "module" for ESM
  scripts: {
    start: 'node src/server.js',
    dev: 'nodemon src/server.js',
    test: 'jest',
  },
  engines: {
    node: '>=18.0.0',
  },
  license: 'MIT',
};

fs.writeFileSync('./package.json', JSON.stringify(packageJson, null, 2));
console.log('package.json created:', JSON.stringify(packageJson, null, 2));
```

## 💻 Code Example — Advanced
```javascript
// read-and-validate-package-json.js
// Production pattern: validate a package.json has required fields before deploy

const fs = require('fs');
const path = require('path');

function loadPackageJson(dir = process.cwd()) {
  const filePath = path.join(dir, 'package.json');
  if (!fs.existsSync(filePath)) {
    throw new Error('package.json not found in ' + dir);
  }
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function validatePackageJson(pkg) {
  const required = ['name', 'version', 'main', 'scripts'];
  const missing = required.filter((field) => !pkg[field]);

  if (missing.length > 0) {
    throw new Error(`package.json missing required fields: ${missing.join(', ')}`);
  }

  if (!pkg.scripts.start) {
    console.warn('Warning: no "start" script defined — deployment platforms may fail');
  }

  // Check for accidentally committed devDependencies in dependencies (common mistake)
  const devToolsInProd = ['nodemon', 'jest', 'eslint', 'webpack'];
  const prodDeps = Object.keys(pkg.dependencies || {});
  const misplaced = prodDeps.filter((dep) => devToolsInProd.includes(dep));
  if (misplaced.length > 0) {
    console.warn(`Warning: dev-only tools found in "dependencies": ${misplaced.join(', ')}`);
  }

  console.log(`package.json for "${pkg.name}@${pkg.version}" is valid.`);
  return true;
}

try {
  const pkg = loadPackageJson();
  validatePackageJson(pkg);
} catch (err) {
  console.error('Validation failed:', err.message);
  process.exit(1);
}
```

---

## 🟠 Express.js Integration
```javascript
// Express server reading metadata FROM its own package.json at runtime
const express = require('express');
const pkg = require('./package.json'); // Node.js allows requiring JSON directly

const app = express();

// Expose version/health info derived from package.json — common pattern
// for ops/monitoring to verify which build is deployed
app.get('/version', (req, res) => {
  res.json({
    name: pkg.name,
    version: pkg.version,
    nodeRequired: pkg.engines ? pkg.engines.node : 'not specified',
  });
});

app.listen(3000, () => {
  console.log(`${pkg.name} v${pkg.version} started on :3000`);
});

// package.json excerpt for this service:
/*
{
  "name": "swiggy-style-tracking-service",
  "version": "2.3.1",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": { "express": "^4.19.2" },
  "devDependencies": { "nodemon": "^3.1.0" },
  "engines": { "node": ">=18.0.0" }
}
*/
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting development-only tools in `dependencies` instead of `devDependencies`
```javascript
// Wrong — bloats production installs, slows deploys, increases attack surface
// package.json:
// "dependencies": { "express": "^4.19.2", "nodemon": "^3.1.0", "jest": "^29.0.0" }

// Correct — separate runtime needs from dev-only tooling
// "dependencies": { "express": "^4.19.2" }
// "devDependencies": { "nodemon": "^3.1.0", "jest": "^29.0.0" }
```

❌ Mistake 2: Manually editing `package.json` version numbers instead of using `npm version`
```bash
# Wrong — manually typing "version": "1.2.4" risks typos, forgetting to tag git commits
# Correct — let npm handle it atomically (also creates a git commit + tag)
npm version patch   # 1.2.3 -> 1.2.4
npm version minor   # 1.2.3 -> 1.3.0
npm version major   # 1.2.3 -> 2.0.0
```

---

## 🧠 Tricky Interview Question

```javascript
// package.json has: "main": "index.js"
// but there's no index.js file in the project root, only "src/app.js"

const myLib = require('my-local-package'); // installed via `npm link` or file: path
```
Answer: If `main` points to a non-existent file and no `exports` field exists, Node.js will throw `MODULE_NOT_FOUND` when something tries to `require()` that package as a whole. The `main` field must point to an actual file that serves as the package's public entry point — this is a very common real-world bug when publishing/linking local packages where the entry file was moved or renamed without updating `package.json`.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `dependencies` and `devDependencies`?
A1: `dependencies` are required at runtime in production (e.g., `express`); `devDependencies` are only needed during development/testing/building (e.g., `jest`, `eslint`, `webpack`) and are typically excluded from production installs via `npm ci --omit=dev` or `NODE_ENV=production`.

Q2: What does the `main` field do, and how does `exports` differ from it?
A2: `main` specifies the default entry file loaded when someone does `require('your-package')`. `exports` (newer, more powerful) can define MULTIPLE named entry points and restrict which internal files are importable from outside, giving package authors explicit control over their public API surface.

Q3: What happens if you don't specify `"type"` in package.json?
A3: Node.js defaults to `"commonjs"` — `.js` files use `require()`/`module.exports`. Setting `"type": "module"` switches ALL `.js` files in that package to ES Module syntax (`import`/`export`) by default; you can override per-file using `.cjs`/`.mjs` extensions regardless of the `type` setting.

Q4: Why is the `scripts` field important for team collaboration?
A4: It standardizes how to run common tasks (`start`, `test`, `build`, `lint`) across the whole team and CI/CD pipelines — anyone can run `npm run test` without needing to know or remember the underlying tool/command, and CI configs stay simple and portable.

Q5: What is `npm ci` and how does it differ from `npm install` in relation to package.json/lockfile?
A5: `npm ci` installs EXACTLY what's in `package-lock.json`, deleting `node_modules` first, and FAILS if `package.json` and the lockfile are out of sync — it's faster and stricter, designed for CI/CD and reproducible production builds, whereas `npm install` may update the lockfile if versions have drifted.

---

## 🔷 When to Use + When Not to Use
✅ Always maintain package.json correctly when:
- Any Node.js project, no exceptions — it's the foundational contract for tooling, CI/CD, and collaboration

❌ Common anti-pattern to avoid:
- Hand-editing version numbers or dependency entries directly without using `npm install`/`npm version`, risking inconsistency with the actual installed `node_modules`/lockfile

---

## 📊 Visual Diagram
```
PACKAGE.JSON — KEY SECTIONS
──────────────────────────────────────────────
{
  "name": "...",           ┐
  "version": "1.0.0",       ├─ IDENTITY
  "description": "...",     ┘

  "main": "index.js",       ┐
  "type": "commonjs",        ├─ MODULE RESOLUTION
  "exports": {...},          ┘

  "scripts": {               ┐
    "start": "node index.js",├─ AUTOMATION
    "test": "jest"           ┘
  },

  "dependencies": {...},     ┐─ RUNTIME NEEDS (shipped to prod)
  "devDependencies": {...},  ┘─ DEV-ONLY NEEDS (not shipped)

  "engines": { "node": ">=18" }  ─ VERSION CONSTRAINTS
}
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Manifest | File describing a project's metadata/config | Project की metadata/config बताने वाली file |
| dependencies | Runtime-required packages | Runtime पर ज़रूरी packages |
| devDependencies | Development-only packages | सिर्फ development में ज़रूरी packages |
| scripts | Named automation commands | Named automation commands |
| main | Package's default entry file | Package की default entry file |
| exports | Controlled public API surface of a package | Package का controlled public API |
| engines | Declared compatible Node/npm versions | Compatible Node/npm versions की घोषणा |

---

## ⚡ 3-Line Summary
English:
1. `package.json` is the manifest every Node.js project needs — declaring identity, dependencies, scripts, and version constraints that all tooling reads.
2. Separate runtime needs (`dependencies`) from dev-only tooling (`devDependencies`) to keep production installs lean and secure.
3. Use `npm version`/`npm install` to modify it programmatically rather than hand-editing, keeping it in sync with the actual lockfile and installed packages.

Hindi:
1. `package.json` हर Node.js project की manifest है — identity, dependencies, scripts, और version constraints बताती है जो सारा tooling पढ़ता है।
2. Runtime needs (`dependencies`) को dev-only tooling (`devDependencies`) से अलग रखें ताकि production installs lean और secure रहें।
3. इसे hand-edit करने के बजाय `npm version`/`npm install` से modify करें, ताकि lockfile और installed packages से sync रहे।

---

## ➡️ Next Topic
**16. package-lock.json — Why Important** — Dive into the companion file that guarantees your `package.json` resolves identically everywhere.
