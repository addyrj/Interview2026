# 21. Global vs Local Packages
# हिंदी में: Global vs Local Packages

---

## 🔵 Simple Definition (English)
**Local packages** are installed inside a specific project's `node_modules` folder (via `npm install <pkg>`) and are only usable within that project. **Global packages** are installed once system-wide (via `npm install -g <pkg>`) into a shared location, making their CLI commands available from any directory on your machine.

## 🔵 सरल परिभाषा (Hindi)
**Local packages** किसी specific project के `node_modules` folder के अंदर install होते हैं (via `npm install <pkg>`) और सिर्फ उसी project में usable होते हैं। **Global packages** एक बार system-wide install होते हैं (via `npm install -g <pkg>`) एक shared location में, जिससे उनके CLI commands machine की किसी भी directory से available हो जाते हैं।

---

## 🔴 Problem it Solves
Not every package is a project dependency — some are developer TOOLS you want available everywhere (`nodemon`, `typescript` compiler for quick scripts, `pm2` process manager). Local installs solve project-specific reproducibility (everyone gets the SAME version via lockfile); global installs solve "I want this command available in any terminal, any directory, without reinstalling per project."

## 🔴 यह क्यों बना? (Hindi)
हर package project dependency नहीं होता — कुछ developer TOOLS हैं जो हर जगह available चाहिए (`nodemon`, quick scripts के लिए `typescript` compiler, `pm2` process manager)। Local installs project-specific reproducibility solve करते हैं (lockfile से सभी को SAME version मिलती है); global installs solve करते हैं "मुझे यह command किसी भी terminal, किसी भी directory में चाहिए, per project reinstall किए बिना।"

---

## 🟢 How it Works — Step by Step

Step 1 → `npm install express` (no `-g` flag) installs into `./node_modules/express` relative to the CURRENT directory — a local install, tied to that specific project.
Step 2 → `npm install -g nodemon` installs into a GLOBAL location determined by npm's config — typically `/usr/local/lib/node_modules` (macOS/Linux) or `%AppData%\npm\node_modules` (Windows), or wherever `npm root -g` reports.
Step 3 → Global installs add the package's CLI binary to a directory already in your system `PATH` (e.g., `/usr/local/bin`), so typing `nodemon` directly in ANY terminal works without `./node_modules/.bin/` prefixing.
Step 4 → Local packages are NOT directly runnable by typing their bare command name in a terminal — you either use `npx <command>`, reference `./node_modules/.bin/<command>`, or (most commonly) call them from an npm script where `.bin` is auto-added to `PATH`.
Step 5 → `require()`-able LIBRARY code (`express`, `lodash`, `react`) should ALWAYS be a local dependency — global installs are not even on Node's module resolution path for `require()` by default, so a globally-installed library can't be imported into your code anyway.
Step 6 → CLI TOOLS that you use across many unrelated projects (`npm`, `yarn`, `pm2` for process management, `vercel`/`netlify` CLI for deployment) are reasonable global install candidates — but even these are increasingly recommended as local devDependencies + `npx`, to guarantee version consistency per project.
Step 7 → `npm list -g --depth=0` shows all currently globally-installed packages; `npm uninstall -g <pkg>` removes one.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `npm install express` (बिना `-g` flag) CURRENT directory के relative `./node_modules/express` में install होता है — एक local install, उस specific project से tied।
Step 2 → `npm install -g nodemon` npm के config से decided GLOBAL location में install होता है — typically `/usr/local/lib/node_modules` (macOS/Linux) या `%AppData%\npm\node_modules` (Windows), या `npm root -g` जो भी report करे।
Step 3 → Global installs package का CLI binary एक ऐसी directory में add करते हैं जो already system `PATH` में है (जैसे `/usr/local/bin`), इसलिए किसी भी terminal में सीधे `nodemon` type करना बिना `./node_modules/.bin/` prefix के काम करता है।
Step 4 → Local packages सीधे bare command name type करके terminal में runnable नहीं होते — आप `npx <command>` use करते हैं, `./node_modules/.bin/<command>` reference करते हैं, या (सबसे common) उन्हें npm script से call करते हैं जहाँ `.bin` auto-added है PATH में।
Step 5 → `require()`-able LIBRARY code (`express`, `lodash`, `react`) को हमेशा local dependency होना चाहिए — global installs default रूप से `require()` के Node के module resolution path पर नहीं हैं, इसलिए globally-installed library को code में import ही नहीं कर सकते।
Step 6 → CLI TOOLS जो आप कई unrelated projects में इस्तेमाल करते हैं (`npm`, `yarn`, process management के लिए `pm2`, deployment के लिए `vercel`/`netlify` CLI) reasonable global install candidates हैं — पर इन्हें भी increasingly local devDependencies + `npx` के रूप में recommend किया जाता है, per-project version consistency guarantee करने के लिए।
Step 7 → `npm list -g --depth=0` सभी currently globally-installed packages दिखाता है; `npm uninstall -g <pkg>` एक को remove करता है।

---

## 🟡 Real World Example
**A freelance developer working across Flipkart-style and Swiggy-style client codebases:** `pm2` (process manager for running Node apps in production) is installed globally since it's used as a system-level utility across every deployment, regardless of project. But `express`, `mongoose`, `jsonwebtoken` are ALWAYS local dependencies in each client's own `package.json` — because each client project might need a DIFFERENT express version, and the code literally `require()`s these libraries, which only works for locally-installed packages.

## 🟡 Real Example Hindi mein
**Flipkart-style और Swiggy-style client codebases में काम करने वाला एक freelance developer:** `pm2` (production में Node apps चलाने का process manager) globally install है क्योंकि यह हर project में एक system-level utility के रूप में इस्तेमाल होता है, project चाहे कोई भी हो। पर `express`, `mongoose`, `jsonwebtoken` हमेशा हर client के अपने `package.json` में local dependencies हैं — क्योंकि हर client project को अलग express version चाहिए हो सकता है, और code literally इन libraries को `require()` करता है, जो सिर्फ locally-installed packages के लिए काम करता है।

---

## 💻 Code Example — Basic
```javascript
// demonstrate-require-resolution.js
// Shows WHY library code must be a local dependency, not global

try {
  // This will ONLY succeed if 'express' is in THIS project's node_modules
  // Even if you have `npm install -g express` run elsewhere, require()
  // does NOT look in the global install location by default
  const express = require('express');
  console.log('express loaded from local node_modules — version:', require('express/package.json').version);
} catch (err) {
  console.log('require("express") failed:', err.message);
  console.log('This proves require() does not use global installs for library code.');
}

// Show where Node WOULD look (none of these include the global npm directory)
console.log('Module search paths:', module.paths);
```

## 💻 Code Example — Advanced
```javascript
// list-and-audit-global-packages.js
// Production-style utility: audits globally installed packages via child_process,
// useful for onboarding docs or CI environment verification scripts

const { execSync } = require('child_process');

function getGlobalPackages() {
  try {
    const output = execSync('npm list -g --depth=0 --json', { encoding: 'utf8' });
    const data = JSON.parse(output);
    return Object.entries(data.dependencies || {}).map(([name, info]) => ({
      name,
      version: info.version,
    }));
  } catch (err) {
    console.error('Failed to list global packages:', err.message);
    return [];
  }
}

function auditGlobalPackages() {
  const globals = getGlobalPackages();
  console.log(`Found ${globals.length} globally installed packages:`);

  const recommendedGlobalOnly = ['npm', 'yarn', 'pnpm', 'pm2', 'nodemon'];
  const flaggedForReview = [];

  globals.forEach(({ name, version }) => {
    const isExpected = recommendedGlobalOnly.includes(name);
    console.log(`  ${name}@${version}${isExpected ? '' : '  <-- review: should this be a devDependency instead?'}`);
    if (!isExpected) flaggedForReview.push(name);
  });

  if (flaggedForReview.length > 0) {
    console.log(`\nConsider moving these to project devDependencies for reproducibility: ${flaggedForReview.join(', ')}`);
  }
}

auditGlobalPackages();
```

---

## 🟠 Express.js Integration
```javascript
// Express project demonstrating the LOCAL dependency requirement directly
// package.json (local dependencies — these MUST be local to be require()-able):
/*
{
  "dependencies": {
    "express": "^4.19.2",
    "mongoose": "^8.3.0"
  },
  "devDependencies": {
    "nodemon": "^3.1.0"
  }
}
*/

// server.js — this ONLY works because express/mongoose are LOCAL deps
const express = require('express');   // fails if only globally installed
const mongoose = require('mongoose'); // fails if only globally installed
const app = express();

app.get('/', (req, res) => res.json({ status: 'Local deps loaded successfully' }));

app.listen(3000, () => console.log('Server on :3000'));

// Running the dev server uses a GLOBAL-style tool via a LOCAL devDependency:
// package.json: "scripts": { "dev": "nodemon server.js" }
// `nodemon` here resolves from ./node_modules/.bin/nodemon automatically
// (npm scripts add .bin to PATH) — no global nodemon install required at all
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Installing a project's actual code dependencies globally
```bash
# Wrong — express installed globally, then trying to require() it in a project
npm install -g express
# server.js: const express = require('express'); // FAILS - Cannot find module

# Correct — install it locally, as an actual project dependency
npm install express
```

❌ Mistake 2: Relying on globally-installed CLI tools for team projects (version drift risk)
```bash
# Wrong — "it works on my machine" because YOU have nodemon@3 installed globally,
# but a teammate has nodemon@1 globally — inconsistent dev experience/behavior
npm install -g nodemon

# Correct — add it as a devDependency so EVERYONE on the team (and CI) uses
# the exact same pinned version via package-lock.json
npm install --save-dev nodemon
# package.json script: "dev": "nodemon server.js"  (resolves to LOCAL nodemon)
```

---

## 🧠 Tricky Interview Question

**Q: You run `npm install -g typescript` and then, inside a project with NO local typescript installed, you run `tsc --init`. It works. But your teammate's CI build runs `npx tsc --init` inside the same project and FAILS with "command not found" after checking local `node_modules/.bin` and not finding it cached either. Why the difference?**
Answer: Your `tsc` command worked because `-g` installed it into your system `PATH` directly — `tsc` is found as a global binary, independent of the project. Your teammate's `npx tsc` behaves differently: it checks the LOCAL project's `node_modules/.bin` first (not found, since typescript isn't a local dependency), then its OWN npx cache (likely empty in a fresh CI environment), and only THEN would attempt to download from the registry — if CI has no network access or the download step wasn't configured correctly, it fails. The fix: add `typescript` as a `devDependency` in `package.json` so it's available locally and reproducibly for everyone, including CI, rather than relying on anyone's global install.

---

## ⚫ Interview Questions + Answers

Q1: Can `require()` load a globally-installed package directly?
A1: Not by default — Node's module resolution algorithm for `require()` only walks up through `node_modules` folders relative to the current file's directory; it does not automatically check the global npm installation directory unless you explicitly configure `NODE_PATH` to include it (rare and discouraged).

Q2: What kinds of packages make sense to install globally?
A2: Standalone CLI tools used across many unrelated projects, independent of any single project's dependency tree — e.g., `npm` itself, `pm2` (production process manager), or editor/IDE tooling helpers. Any package your CODE actually imports (`require`/`import`) should be local.

Q3: Why is it increasingly recommended to avoid global installs even for CLI tools?
A3: Global installs create a SINGLE shared version across all projects on your machine — if Project A needs `typescript@4.x` behavior and Project B needs `typescript@5.x`, a single global install can't satisfy both; local devDependencies + `npx` solve this by pinning per-project versions.

Q4: Where does npm store globally-installed packages?
A4: In a system-wide location reported by `npm root -g` — commonly `/usr/local/lib/node_modules` on macOS/Linux (or wherever Node itself is installed, e.g., under nvm's version folder) and `%AppData%\npm\node_modules` on Windows.

Q5: What command lists all currently installed global packages?
A5: `npm list -g --depth=0` — the `--depth=0` flag avoids recursively listing each global package's own nested dependencies, showing just the top-level globally installed tools.

---

## 🔷 When to Use + When Not to Use
✅ Use global installs when:
- Installing truly cross-project, standalone CLI utilities you use constantly and don't need pinned per-project (though even here, local + npx is often safer)

❌ Avoid global installs when:
- The package is something your code `require()`s/`import`s — it MUST be a local dependency, or your code simply won't find it

---

## 📊 Visual Diagram
```
LOCAL vs GLOBAL PACKAGE INSTALLATION
──────────────────────────────────────────────
  LOCAL (npm install express)
  /my-project/
    ├── package.json          ("dependencies": {"express": "^4.19.2"})
    ├── package-lock.json
    └── node_modules/
        └── express/           <- only usable by THIS project, via require()

  GLOBAL (npm install -g nodemon)
  /usr/local/lib/node_modules/   (shared system location)
    └── nodemon/
  /usr/local/bin/nodemon          <- symlink added to system PATH

  Terminal (any directory): `nodemon` works directly, everywhere
  Code (any file): `require('nodemon')` FAILS — require() ignores global location
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Local install | Package installed inside a project's node_modules | Project के node_modules में installed package |
| Global install | System-wide package, available from any directory | System-wide package, कहीं से भी available |
| PATH | System variable listing directories with runnable commands | Runnable commands वाली directories की list |
| npm root -g | Command showing the global install directory | Global install directory दिखाने वाला command |
| CLI tool | Command-line utility, as opposed to an importable library | Importable library के उलट, command-line utility |

---

## ⚡ 3-Line Summary
English:
1. Local packages live in a project's own `node_modules` and are what your code actually `require()`s; global packages live system-wide and provide CLI commands usable from any directory.
2. `require()` never resolves globally-installed packages — any library your code imports MUST be a local dependency.
3. Even CLI tools are increasingly installed as local devDependencies (run via `npx` or npm scripts) rather than globally, to guarantee consistent versions across teammates and CI.

Hindi:
1. Local packages project के अपने `node_modules` में रहते हैं और यही वो हैं जो आपका code actually `require()` करता है; global packages system-wide रहते हैं और किसी भी directory से usable CLI commands देते हैं।
2. `require()` globally-installed packages कभी resolve नहीं करता — आपका code जो भी library import करे वह ज़रूर local dependency होनी चाहिए।
3. CLI tools भी increasingly local devDependencies के रूप में install होते हैं (npx या npm scripts से चलते हैं) globally के बजाय, teammates और CI में consistent versions guarantee करने के लिए।

---

## ➡️ Next Topic
**22. Creating + Publishing npm Package** — Apply everything learned about package.json, versioning, and local/global installs to build and ship your own npm package.
