# 22. Creating + Publishing npm Package
# हिंदी में: npm Package बनाना और Publish करना

---

## 🔵 Simple Definition (English)
Creating an npm package means organizing reusable JavaScript code with a proper `package.json`, then **publishing** it (`npm publish`) uploads it to the npm registry — making it installable by anyone worldwide via `npm install <your-package-name>`.

## 🔵 सरल परिभाषा (Hindi)
npm package बनाने का मतलब है reusable JavaScript code को proper `package.json` के साथ organize करना, फिर **publish** करना (`npm publish`) उसे npm registry पर upload करता है — जिससे दुनिया भर में कोई भी `npm install <your-package-name>` से install कर सके।

---

## 🔴 Problem it Solves
Without a standard publishing mechanism, sharing reusable code across teams/companies/the world would require manually copying files or maintaining private git submodules. npm's publish flow standardizes packaging, versioning, and distribution — turning any well-organized folder of code into a globally installable, versioned dependency for others (or your own other projects/teams).

## 🔴 यह क्यों बना? (Hindi)
एक standard publishing mechanism के बिना teams/companies/दुनिया भर में reusable code share करने के लिए manually files copy करना या private git submodules maintain करना पड़ता। npm का publish flow packaging, versioning, और distribution standardize करता है — किसी भी well-organized code folder को globally installable, versioned dependency बना देता है दूसरों (या आपके अपने दूसरे projects/teams) के लिए।

---

## 🟢 How it Works — Step by Step

Step 1 → Create a project folder, run `npm init` to generate `package.json` — the `name` field MUST be unique on the npm registry (or scoped like `@yourcompany/package-name` for organization-scoped packages, which can be unlisted/private).
Step 2 → Write your reusable code, exposing a clear public API via `module.exports` (CommonJS) or the `exports` field (modern), and specify the `main` field pointing to the entry file.
Step 3 → Add a `files` field (or `.npmignore`) to control EXACTLY which files get published — you don't want to accidentally publish test files, `.env`, or source maps.
Step 4 → Write tests and a README — the README is what renders on the npmjs.com package page, critical for adoption/trust.
Step 5 → Run `npm login` (one-time, authenticates your npm account via browser or token).
Step 6 → Run `npm publish` — for your FIRST publish of a scoped package, you may need `npm publish --access public` (scoped packages default to private, which requires a paid plan unless made explicitly public).
Step 7 → To release a new version: bump it with `npm version patch|minor|major` (updates `package.json`, creates a git commit+tag), then `npm publish` again — you can NEVER republish the same version number, each publish must have a strictly higher version.
Step 8 → Consumers now run `npm install your-package-name` and it resolves exactly like any other registry package, following the same SemVer/lockfile rules covered in earlier topics.
Step 9 → For private, internal-only packages, companies typically use a PRIVATE registry (npm Enterprise, GitHub Packages, Verdaccio, Artifactory) with the same `npm publish` workflow pointed at a different registry URL via `.npmrc`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → एक project folder बनाएं, `npm init` चलाएं `package.json` बनाने के लिए — `name` field npm registry पर UNIQUE होना चाहिए (या organization-scoped packages के लिए `@yourcompany/package-name` जैसा scoped, जो unlisted/private हो सकता है)।
Step 2 → अपना reusable code लिखें, `module.exports` (CommonJS) या `exports` field (modern) से clear public API expose करें, और `main` field entry file की तरफ specify करें।
Step 3 → `files` field (या `.npmignore`) जोड़ें यह control करने के लिए कि EXACTLY कौन सी files publish हों — आप गलती से test files, `.env`, या source maps publish नहीं करना चाहते।
Step 4 → Tests और README लिखें — README वही है जो npmjs.com package page पर render होता है, adoption/trust के लिए critical।
Step 5 → `npm login` चलाएं (one-time, browser या token से आपके npm account को authenticate करता है)।
Step 6 → `npm publish` चलाएं — scoped package के FIRST publish के लिए `npm publish --access public` चाहिए हो सकता है (scoped packages default से private होते हैं, जिसके लिए paid plan चाहिए जब तक explicitly public न बनाएं)।
Step 7 → नया version release करने के लिए: `npm version patch|minor|major` से bump करें (package.json update करता है, git commit+tag बनाता है), फिर फिर से `npm publish` — आप कभी same version number republish नहीं कर सकते, हर publish में strictly higher version होना चाहिए।
Step 8 → Consumers अब `npm install your-package-name` चलाते हैं और यह exactly किसी और registry package जैसे resolve होता है, वही SemVer/lockfile rules follow करता है जो पहले topics में cover हुए।
Step 9 → Private, internal-only packages के लिए companies typically एक PRIVATE registry (npm Enterprise, GitHub Packages, Verdaccio, Artifactory) इस्तेमाल करती हैं same `npm publish` workflow के साथ, `.npmrc` में अलग registry URL point करके।

---

## 🟡 Real World Example
**An internal "razorpay-logger" package:** A fintech company builds a standardized structured-logging utility used across 20+ internal microservices (for consistent log formats feeding into their observability stack). Instead of copy-pasting the logger code into each service, they publish it as `@internal-org/razorpay-logger` to a private npm registry (GitHub Packages). Every microservice simply runs `npm install @internal-org/razorpay-logger`, and when the logging format needs a company-wide update, bumping the package version and having each service update its dependency is far more reliable than manually syncing copy-pasted files.

## 🟡 Real Example Hindi mein
**एक internal "razorpay-logger" package:** एक fintech company एक standardized structured-logging utility बनाती है जो 20+ internal microservices में इस्तेमाल होती है (consistent log formats के लिए जो उनके observability stack में जाते हैं)। हर service में logger code copy-paste करने के बजाय, वे इसे `@internal-org/razorpay-logger` के रूप में एक private npm registry (GitHub Packages) पर publish करते हैं। हर microservice सिर्फ `npm install @internal-org/razorpay-logger` चलाता है, और जब logging format में company-wide update चाहिए हो, package version bump करके हर service का dependency update करना copy-pasted files को manually sync करने से कहीं ज़्यादा reliable है।

---

## 💻 Code Example — Basic
```javascript
// my-first-package/index.js
// A tiny reusable utility — the actual package code

/**
 * Calculates discount price given an original price and discount percentage.
 * @param {number} price - original price
 * @param {number} percent - discount percentage (0-100)
 * @returns {number} discounted price, rounded to nearest integer
 */
function calculateDiscount(price, percent) {
  if (typeof price !== 'number' || typeof percent !== 'number') {
    throw new TypeError('price and percent must be numbers');
  }
  if (percent < 0 || percent > 100) {
    throw new RangeError('percent must be between 0 and 100');
  }
  return Math.round(price - (price * percent) / 100);
}

module.exports = { calculateDiscount }; // public API of this package

/*
my-first-package/package.json:
{
  "name": "discount-calculator-demo",
  "version": "1.0.0",
  "description": "A tiny utility to calculate discounted prices",
  "main": "index.js",
  "files": ["index.js", "README.md"],
  "keywords": ["discount", "price", "utility"],
  "license": "MIT",
  "repository": { "type": "git", "url": "https://github.com/you/discount-calculator-demo" }
}
*/

// Publishing (run from inside my-first-package/):
// npm login
// npm publish
```

## 💻 Code Example — Advanced
```javascript
// publish-workflow-script.js
// A production-style pre-publish validation script
// (run via "prepublishOnly" npm script to prevent accidental bad publishes)

const fs = require('fs');
const { execSync } = require('child_process');

function runPrepublishChecks() {
  console.log('Running pre-publish checks...');

  // 1. Ensure tests pass BEFORE allowing a publish
  try {
    execSync('npm test', { stdio: 'inherit' });
  } catch {
    console.error('Tests failed — aborting publish.');
    process.exit(1);
  }

  // 2. Ensure no .env or secret files are accidentally included
  const pkg = JSON.parse(fs.readFileSync('./package.json', 'utf8'));
  const filesField = pkg.files || [];
  const dangerousPatterns = ['.env', 'secret', 'credentials'];

  const dangerous = filesField.filter((f) =>
    dangerousPatterns.some((pattern) => f.toLowerCase().includes(pattern))
  );
  if (dangerous.length > 0) {
    console.error('DANGER: potentially sensitive files in "files" field:', dangerous);
    process.exit(1);
  }

  // 3. Verify version hasn't already been published (common mistake: forgetting to bump)
  try {
    const publishedVersions = execSync(`npm view ${pkg.name} versions --json`, {
      encoding: 'utf8',
    });
    const versions = JSON.parse(publishedVersions);
    if (versions.includes(pkg.version)) {
      console.error(`Version ${pkg.version} is already published! Bump it first with "npm version patch".`);
      process.exit(1);
    }
  } catch {
    console.log('Package not found on registry yet (first publish) — OK to proceed.');
  }

  console.log('All pre-publish checks passed.');
}

runPrepublishChecks();

/*
package.json:
{
  "scripts": {
    "prepublishOnly": "node publish-workflow-script.js"
  }
}
"prepublishOnly" runs automatically and ONLY before `npm publish`
(unlike "prepublish" which historically ran on `npm install` too — avoid that one)
*/
```

---

## 🟠 Express.js Integration
```javascript
// Example: an internal Express middleware package your company publishes
// and other internal Express services then consume

// Package: @internal-org/request-logger-middleware/index.js
function requestLogger(options = {}) {
  const { logLevel = 'info' } = options;
  return function (req, res, next) {
    const start = Date.now();
    res.on('finish', () => {
      const duration = Date.now() - start;
      console.log(`[${logLevel}] ${req.method} ${req.url} - ${res.statusCode} (${duration}ms)`);
    });
    next();
  };
}
module.exports = requestLogger;

// Consumer service: any internal Express app installs and uses it
/*
npm install @internal-org/request-logger-middleware
*/
const express = require('express');
const requestLogger = require('@internal-org/request-logger-middleware');
const app = express();

app.use(requestLogger({ logLevel: 'info' })); // published package used as middleware

app.get('/', (req, res) => res.json({ status: 'ok' }));
app.listen(3000, () => console.log('Server using internal published package, on :3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Publishing sensitive files (`.env`, API keys, internal configs) by forgetting to restrict the `files` field or `.npmignore`
```javascript
// Wrong — no "files" field or .npmignore means EVERYTHING in the folder
// (including .env, test fixtures with real-looking data, etc.) gets published
// package.json: { "name": "my-pkg", "version": "1.0.0" }  // no "files" restriction!

// Correct — explicitly whitelist only what should be public
// package.json: { "files": ["dist/", "README.md", "LICENSE"] }
```

❌ Mistake 2: Forgetting to bump the version before republishing
```bash
# Wrong — npm publish fails outright if the version already exists on the registry
npm publish
# npm error: You cannot publish over the previously published versions: 1.0.0

# Correct — always bump first
npm version patch   # or minor/major as appropriate
npm publish
```

---

## 🧠 Tricky Interview Question

**Q: You publish `my-package@1.0.0`, then immediately realize you published broken code. You fix it and try `npm publish` again without bumping the version. What happens, and why is this actually a GOOD safety feature?**
Answer: `npm publish` fails with an error ("cannot publish over previously published version"). npm registry versions are IMMUTABLE by design once published — you can `npm unpublish` within a short window (72 hours, with restrictions, and it's discouraged since others may have already installed it), but you cannot silently overwrite a version. This is intentional: if overwriting were allowed, anyone who already installed `1.0.0` could get DIFFERENT code later without any version change, breaking reproducibility guarantees for the entire ecosystem (the same guarantee `package-lock.json` depends on). The correct fix is always to bump to `1.0.1` and publish that.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between a scoped package (`@org/name`) and an unscoped one?
A1: Scoped packages are namespaced under an organization/user (`@myorg/my-package`), avoiding naming collisions on the public registry and allowing grouped private packages (private by default unless `--access public` is specified); unscoped packages (`my-package`) share one global namespace and must have a globally unique name.

Q2: Can you republish or overwrite an already-published version?
A2: No — npm enforces immutability per version; once `1.0.0` is published, you cannot publish different code under that exact version number again. You must publish a NEW version number (patch/minor/major bump) for any change, even a tiny fix.

Q3: What does the `files` field in `package.json` control?
A3: It's a whitelist of exactly which files/folders get included when the package is packed/published (via `npm pack` or `npm publish`) — anything not matching is excluded, protecting against accidentally publishing tests, secrets, or build artifacts. `.npmignore` works as a blacklist alternative/complement.

Q4: What is the purpose of the `prepublishOnly` script?
A4: It's an npm lifecycle hook that runs automatically right before `npm publish` executes (and NOT during `npm install`, unlike the older/deprecated `prepublish` hook) — commonly used to run tests, linting, or build steps to ensure only validated code gets published.

Q5: How do companies publish INTERNAL, non-public npm packages?
A5: By pointing npm at a private registry (self-hosted like Verdaccio/Artifactory, or managed like GitHub Packages/npm Enterprise) via a project or user-level `.npmrc` file specifying a custom `registry` URL and auth token, while using the exact same `npm publish`/`npm install` commands as the public registry.

---

## 🔷 When to Use + When Not to Use
✅ Publish a package when:
- Code is genuinely reusable across multiple projects/teams and benefits from versioned, dependency-managed distribution

❌ Avoid publishing (or publish privately) when:
- The code is a one-off internal utility not meant for public use (use a private registry/scope), or contains any sensitive business logic/secrets that shouldn't be publicly inspectable

---

## 📊 Visual Diagram
```
NPM PUBLISH WORKFLOW
──────────────────────────────────────────────
  Write code + package.json
         │
         ▼
  npm login  (authenticate once)
         │
         ▼
  npm test / lint  (via prepublishOnly hook, automatic)
         │
         ▼
  npm publish  ──────────► npm registry (registry.npmjs.org or private)
         │                        │
         ▼                        ▼
  Version 1.0.0 now LOCKED   Anyone runs:
  (cannot be overwritten)    npm install your-package-name
         │                        │
         ▼                        ▼
  Need a fix?               Gets exactly 1.0.0's code,
  npm version patch          forever, until they upgrade
  npm publish  -> 1.0.1
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| npm registry | Central server hosting published packages | Published packages host करने वाला central server |
| Scoped package | Namespaced package (@org/name) | Namespaced package (@org/name) |
| npm publish | Command uploading a package to the registry | Package को registry पर upload करने वाला command |
| Immutable version | A published version that can never change | कभी न बदलने वाला published version |
| prepublishOnly | Hook running right before publish, not install | Publish से पहले चलने वाला hook, install पर नहीं |
| Private registry | Internal, non-public package host | Internal, non-public package host |

---

## ⚡ 3-Line Summary
English:
1. Publishing an npm package means organizing code with a proper `package.json`, then running `npm publish` to upload it to the registry for anyone (or your org, if private) to install.
2. Published versions are immutable — you can never overwrite `1.0.0`, only publish a new, higher version via `npm version` + `npm publish`.
3. Control exactly what gets published via the `files` field/`.npmignore`, and use `prepublishOnly` to enforce tests/checks before every release.

Hindi:
1. npm package publish करने का मतलब है proper `package.json` के साथ code organize करना, फिर `npm publish` चलाकर registry पर upload करना ताकि कोई भी (या आपकी org, अगर private है) install कर सके।
2. Published versions immutable हैं — `1.0.0` को कभी overwrite नहीं कर सकते, सिर्फ `npm version` + `npm publish` से नया, higher version publish कर सकते हैं।
3. `files` field/`.npmignore` से exactly control करें क्या publish हो, और हर release से पहले tests/checks enforce करने के लिए `prepublishOnly` use करें।

---

## ➡️ Next Topic
**23. CommonJS — require/module.exports** — Having covered the full package ecosystem, dive into the module system itself that makes `require()` and `module.exports` work.
