# 14. npm vs yarn vs pnpm
# हिंदी में: npm vs yarn vs pnpm

---

## 🔵 Simple Definition (English)
**npm**, **yarn**, and **pnpm** are all JavaScript package managers that install dependencies from the npm registry and run scripts — they differ mainly in installation speed, disk space usage, and how they structure `node_modules`. npm is the default (ships with Node.js); yarn and pnpm are alternatives built to fix npm's historical pain points.

## 🔵 सरल परिभाषा (Hindi)
**npm**, **yarn**, और **pnpm** तीनों JavaScript package managers हैं जो npm registry से dependencies install करते हैं और scripts चलाते हैं — ये मुख्यतः installation speed, disk space usage, और `node_modules` के structure में अलग हैं। npm default है (Node.js के साथ आता है); yarn और pnpm npm की historical problems fix करने के लिए बने alternatives हैं।

---

## 🔴 Problem it Solves
Early npm (v2-v3 era) had slow installs, non-deterministic dependency trees (same `package.json` could resolve differently on different machines), and a flat/duplicated `node_modules` wasting huge disk space across projects. Yarn (2016, by Facebook) introduced lockfiles and faster parallel installs. pnpm went further, using a content-addressable store and symlinks to eliminate duplicate package copies entirely across your whole machine.

## 🔴 यह क्यों बना? (Hindi)
Early npm (v2-v3 era) में slow installs, non-deterministic dependency trees (same `package.json` अलग machines पर अलग resolve हो सकता था), और flat/duplicated `node_modules` जो हर project में disk space waste करता था। Yarn (2016, Facebook द्वारा) ने lockfiles और faster parallel installs दिए। pnpm ने आगे जाकर content-addressable store और symlinks से पूरी machine पर duplicate package copies पूरी तरह खत्म कर दी।

---

## 🟢 How it Works — Step by Step

Step 1 → **npm** (default, bundled with Node.js): reads `package.json`, resolves dependency tree, writes `package-lock.json` for deterministic installs, stores packages in a nested/hoisted `node_modules` folder.
Step 2 → **yarn** (Classic v1, and modern Yarn Berry v2+): uses `yarn.lock`, historically faster than old npm via better caching and parallel downloads; Yarn Berry introduced "Plug'n'Play" (PnP) mode that can skip `node_modules` entirely, resolving packages from a `.yarn/cache` zip-based store.
Step 3 → **pnpm**: stores every package version ONCE globally in a content-addressable store (`~/.pnpm-store`), then creates hard links/symlinks into each project's `node_modules` — massive disk savings when you have many projects sharing dependencies (e.g., React, lodash).
Step 4 → **pnpm's strict `node_modules` structure**: unlike npm/yarn's traditional flat hoisting (which lets packages accidentally access dependencies they didn't declare — "phantom dependencies"), pnpm creates a symlinked structure that only exposes packages you explicitly listed in `package.json`, catching bugs npm/yarn would silently allow.
Step 5 → All three support **workspaces** (monorepo support) — managing multiple packages in one repository with shared dependency hoisting, though syntax/config differs slightly.
Step 6 → Lockfiles (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`) are NOT interchangeable — a project should pick ONE package manager and commit only its lockfile, never mix them (mixing causes dependency resolution conflicts).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **npm** (default, Node.js के साथ bundled): `package.json` पढ़ता है, dependency tree resolve करता है, deterministic installs के लिए `package-lock.json` लिखता है, packages को nested/hoisted `node_modules` folder में रखता है।
Step 2 → **yarn** (Classic v1, modern Yarn Berry v2+): `yarn.lock` use करता है, historically old npm से faster था better caching और parallel downloads से; Yarn Berry का "Plug'n'Play" (PnP) mode `node_modules` को पूरी तरह skip कर सकता है, packages `.yarn/cache` zip-based store से resolve होते हैं।
Step 3 → **pnpm**: हर package version को एक बार globally content-addressable store (`~/.pnpm-store`) में रखता है, फिर हर project के `node_modules` में hard links/symlinks बनाता है — कई projects एक जैसी dependencies share करें तो disk savings बहुत बड़ी (जैसे React, lodash)।
Step 4 → **pnpm का strict `node_modules` structure**: npm/yarn के traditional flat hoisting (जिसमें packages accidentally undeclared dependencies access कर सकते हैं — "phantom dependencies") के उलट, pnpm symlinked structure बनाता है जो सिर्फ `package.json` में explicitly listed packages expose करता है, bugs catch करता है जो npm/yarn silently allow करते।
Step 5 → तीनों **workspaces** (monorepo support) support करते हैं — एक repository में कई packages manage करना shared dependency hoisting के साथ, syntax/config थोड़ा अलग है।
Step 6 → Lockfiles (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`) interchangeable नहीं हैं — एक project को ONE package manager चुनना चाहिए और सिर्फ उसका lockfile commit करना चाहिए, कभी mix न करें (mixing से dependency resolution conflicts होते हैं)।

---

## 🟡 Real World Example
**A large e-commerce company like Flipkart running 50+ microservices/frontends:** switching their monorepo from npm to pnpm cut CI install times significantly and reduced disk usage across developer laptops and CI runners, because shared dependencies (React, lodash, axios, TypeScript) used by dozens of packages are stored ONCE on disk instead of duplicated per-package. pnpm's strict dependency resolution also caught several "phantom dependency" bugs where a package was using a library it never declared in its own `package.json`.

## 🟡 Real Example Hindi mein
**Flipkart जैसी बड़ी e-commerce company जो 50+ microservices/frontends चलाती है:** उनके monorepo को npm से pnpm में switch करने से CI install times काफ़ी कम हुए और developer laptops और CI runners पर disk usage कम हुआ, क्योंकि कई packages द्वारा shared dependencies (React, lodash, axios, TypeScript) disk पर एक बार store होती हैं, हर package में duplicate नहीं होतीं। pnpm की strict dependency resolution ने कई "phantom dependency" bugs भी पकड़े जहाँ कोई package ऐसी library इस्तेमाल कर रहा था जो उसने अपने `package.json` में declare ही नहीं की थी।

---

## 💻 Code Example — Basic
```bash
# package-manager-comparison.sh
# Not JavaScript — comparing equivalent commands across the three tools

# ─── INSTALL DEPENDENCIES ──────────────────────────────────────────────────
npm install                  # npm
yarn install                 # yarn
pnpm install                 # pnpm

# ─── ADD A NEW DEPENDENCY ──────────────────────────────────────────────────
npm install express          # npm
yarn add express             # yarn
pnpm add express             # pnpm

# ─── ADD A DEV DEPENDENCY ──────────────────────────────────────────────────
npm install --save-dev jest
yarn add --dev jest
pnpm add --save-dev jest

# ─── RUN A SCRIPT DEFINED IN package.json ──────────────────────────────────
npm run build
yarn build                   # yarn allows dropping "run" for custom scripts
pnpm run build

# ─── CHECK DISK USAGE DIFFERENCE (conceptual, run on a real multi-project setup) ─
du -sh node_modules          # npm/yarn: often large, duplicated across projects
du -sh node_modules          # pnpm: much smaller, mostly symlinks to global store
```

## 💻 Code Example — Advanced
```javascript
// detect-package-manager.js
// A Node.js script that detects which package manager a project SHOULD use,
// based on which lockfile is present — useful in postinstall/CI scripts
// to prevent accidental lockfile mixing

const fs = require('fs');
const path = require('path');

function detectPackageManager(projectRoot = process.cwd()) {
  const lockfiles = {
    'package-lock.json': 'npm',
    'yarn.lock': 'yarn',
    'pnpm-lock.yaml': 'pnpm',
  };

  const found = Object.keys(lockfiles).filter((file) =>
    fs.existsSync(path.join(projectRoot, file))
  );

  if (found.length === 0) {
    console.warn('No lockfile found — no package manager enforced yet.');
    return null;
  }

  if (found.length > 1) {
    // Multiple lockfiles present = someone used the WRONG package manager at some point
    console.error(`
      MULTIPLE LOCKFILES DETECTED: ${found.join(', ')}
      This causes dependency resolution conflicts!
      Delete all but one, and standardize on a single package manager.
    `);
    process.exit(1);
  }

  const manager = lockfiles[found[0]];
  console.log(`Detected package manager: ${manager} (via ${found[0]})`);
  return manager;
}

detectPackageManager();

// Usage: add as a "preinstall" script to catch mixed-lockfile mistakes early:
// "scripts": { "preinstall": "node detect-package-manager.js" }
```

---

## 🟠 Express.js Integration
```javascript
// Express project — package.json shows package-manager-specific configuration
// (This illustrates project setup rather than runtime Express code)

// package.json excerpt enforcing a single package manager via Corepack (Node 16.9+)
/*
{
  "name": "razorpay-style-api",
  "packageManager": "pnpm@8.15.0",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  }
}
*/
// With "packageManager" set, running `corepack enable` makes `npm install` or
// `yarn install` in this folder automatically redirect to the correct pnpm
// version — preventing teammates from accidentally using the wrong tool.

const express = require('express');
const app = express();

app.get('/pm-info', (req, res) => {
  // Report which package manager this project is configured for
  const pkg = require('./package.json');
  res.json({ packageManager: pkg.packageManager || 'npm (default)' });
});

app.listen(3000, () => console.log('Server on :3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Mixing package managers in one project (committing both `package-lock.json` AND `yarn.lock`)
```bash
# Wrong — a teammate ran `yarn install`, another ran `npm install` — now
# both lockfiles exist and disagree on resolved versions, causing bugs

# Correct — pick ONE, delete the others, add a guard script or use Corepack's
# "packageManager" field in package.json to enforce it team-wide
rm yarn.lock   # if standardizing on npm
npm install
```

❌ Mistake 2: Relying on npm/yarn's lenient hoisting, accidentally using "phantom dependencies"
```javascript
// Wrong — your code uses `lodash` but you never added it to package.json;
// it "works" only because another dependency happens to also depend on
// lodash and npm/yarn hoisted it into your top-level node_modules
const _ = require('lodash'); // works today, breaks silently when that OTHER
                               // package removes its lodash dependency later

// Correct — explicitly declare every package you directly import
// npm install lodash --save
const _ = require('lodash'); // now properly declared in YOUR package.json
```

---

## 🧠 Tricky Interview Question

**Q: Your project uses pnpm, but `require('some-package')` works even though it's not in your `package.json` dependencies, only a transitive dependency's dependency. In npm/yarn this "just works," but in pnpm it throws "Cannot find module." Why?**
Answer: pnpm deliberately creates a STRICT `node_modules` structure using symlinks — only packages you've explicitly declared in your own `package.json` are placed at the top level where `require()` can find them directly. Transitive dependencies are nested and not directly accessible, unlike npm/yarn's traditional flat hoisting which exposes everything to everyone ("phantom dependencies"). This is pnpm's INTENTIONAL design — it catches undeclared dependency usage that would otherwise be a silent, fragile bug waiting to break when the dependency tree shifts.

---

## ⚫ Interview Questions + Answers

Q1: What is a lockfile and why does every package manager generate one?
A1: A lockfile (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`) records the EXACT resolved version of every dependency and sub-dependency, ensuring that `npm/yarn/pnpm install` produces an identical `node_modules` tree on every machine and in CI — without it, semver ranges (`^1.2.3`) could resolve to different versions over time.

Q2: What is pnpm's main architectural advantage over npm/yarn?
A2: A single, global, content-addressable package store shared across ALL projects on your machine, linked into each project via symlinks/hard links — this saves significant disk space and speeds up installs when you work with multiple projects sharing common dependencies.

Q3: What are "phantom dependencies" and which package manager best prevents them?
A3: Phantom dependencies occur when your code imports a package that works only because it was hoisted into `node_modules` by SOME OTHER dependency, without you declaring it yourself — a silent, fragile bug. pnpm's strict, non-flat `node_modules` structure prevents this by not exposing undeclared packages.

Q4: What is Corepack and how does it relate to package manager choice?
A4: Corepack (bundled with Node.js 16.9+) lets a project pin its required package manager AND version via the `"packageManager"` field in `package.json` (e.g., `"packageManager": "pnpm@8.15.0"`); when enabled, it automatically uses the correct tool/version, preventing teammates from accidentally using a different manager.

Q5: Can you mix npm, yarn, and pnpm lockfiles in the same project?
A5: No — you should pick exactly one and commit only its lockfile. Each tool resolves and structures dependencies slightly differently; having multiple lockfiles present leads to inconsistent `node_modules` states and hard-to-debug version mismatches between teammates/environments.

---

## 🔷 When to Use + When Not to Use
✅ Use npm when:
- You want zero extra setup (it ships with Node.js) for small/simple projects

✅ Use pnpm when:
- Working across many projects/monorepos where disk space and install speed matter, and you want stricter dependency hygiene

❌ Avoid when:
- Switching package managers mid-project without fully migrating (deleting old lockfiles/node_modules) — this is the #1 source of "works on my machine" dependency bugs

---

## 📊 Visual Diagram
```
NODE_MODULES STRUCTURE COMPARISON
──────────────────────────────────────────────────
  npm / yarn (classic hoisting):
  project-A/node_modules/  ┐
    ├── express/            ├── each project has its OWN
    ├── lodash/              │   full copy of every package
    └── ...                  ┘   (disk space adds up fast)
  project-B/node_modules/
    ├── express/   (duplicate copy)
    ├── lodash/    (duplicate copy)
    └── ...

  pnpm (content-addressable store + symlinks):
  ~/.pnpm-store/            <- ONE copy of each package version, globally
       │
       ├─symlink─> project-A/node_modules/express
       └─symlink─> project-B/node_modules/express
  (massive disk savings, strict access to only declared deps)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Lockfile | File pinning exact resolved dependency versions | Exact resolved dependency versions वाली file |
| Hoisting | Flattening dependencies into a shared top-level folder | Dependencies को top-level folder में flatten करना |
| Phantom dependency | Using an undeclared package that happens to be available | बिना declare किए काम करने वाली dependency |
| Content-addressable store | Single global storage of package versions by hash | Hash से global package storage |
| Corepack | Node.js tool enforcing a project's chosen package manager | Package manager enforce करने वाला Node.js tool |
| Workspaces | Monorepo support for managing multiple packages | कई packages manage करने का monorepo feature |

---

## ⚡ 3-Line Summary
English:
1. npm, yarn, and pnpm all manage JavaScript dependencies from the npm registry but differ in speed, disk usage, and `node_modules` structure.
2. pnpm uses a global content-addressable store and symlinks to save disk space and enforce stricter, phantom-dependency-free resolution.
3. Never mix lockfiles across package managers in one project — pick one, enforce it with Corepack's `packageManager` field, and commit only that lockfile.

Hindi:
1. npm, yarn, और pnpm तीनों npm registry से JavaScript dependencies manage करते हैं पर speed, disk usage, और `node_modules` structure में अलग हैं।
2. pnpm global content-addressable store और symlinks use करके disk space बचाता है और stricter, phantom-dependency-free resolution देता है।
3. एक project में कभी lockfiles mix न करें — एक चुनें, Corepack के `packageManager` field से enforce करें, और सिर्फ वही lockfile commit करें।

---

## ➡️ Next Topic
**15. package.json — Complete Guide** — Now dive deep into the single most important config file every one of these package managers reads.
