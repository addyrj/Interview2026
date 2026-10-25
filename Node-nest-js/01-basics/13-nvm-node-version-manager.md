# 13. NVM — Node Version Manager
# हिंदी में: NVM — Node Version Manager

---

## 🔵 Simple Definition (English)
**nvm (Node Version Manager)** is a command-line tool that lets you install, manage, and switch between multiple Node.js versions on the same machine, per-project if needed — without touching system-level Node installations.

## 🔵 सरल परिभाषा (Hindi)
**nvm (Node Version Manager)** एक command-line tool है जो आपको एक ही machine पर कई Node.js versions install, manage, और switch करने देता है, ज़रूरत पड़ने पर per-project — system-level Node installation को छुए बिना।

---

## 🔴 Problem it Solves
Different projects often require different Node.js versions (an old legacy service pinned to Node 14, a new microservice needing Node 20). Installing Node.js directly via the OS package manager gives you ONE global version, making it painful to switch. Permission issues also arise with global npm installs (`sudo npm install -g`). nvm solves both: isolated, user-level Node installations you can switch between instantly, no `sudo` needed.

## 🔴 यह क्यों बना? (Hindi)
अलग-अलग projects को अक्सर अलग Node.js versions चाहिए होती हैं (एक पुराना legacy service Node 14 पर, एक नया microservice Node 20 चाहता है)। OS package manager से directly Node.js install करने पर सिर्फ ONE global version मिलती है, switch करना मुश्किल हो जाता है। Global npm installs (`sudo npm install -g`) में permission issues भी आती हैं। nvm दोनों solve करता है: isolated, user-level Node installations जिन्हें instantly switch कर सकते हैं, `sudo` की ज़रूरत नहीं।

---

## 🟢 How it Works — Step by Step

Step 1 → Install nvm itself via a shell script: `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash` — this adds nvm's loader to your shell profile (`.bashrc`/`.zshrc`).
Step 2 → `nvm install 20` downloads and installs Node.js v20 into `~/.nvm/versions/node/v20.x.x/` — completely separate from any system Node install.
Step 3 → `nvm use 20` switches your CURRENT shell session to use that version — updates `PATH` to point at that version's `node`/`npm` binaries.
Step 4 → `nvm install 18 && nvm install 20` lets you have BOTH installed simultaneously; `nvm ls` lists all installed versions; `nvm use 18` switches back anytime.
Step 5 → `nvm alias default 20` sets which version loads automatically in NEW shell sessions, so you don't have to run `nvm use` every time you open a terminal.
Step 6 → A `.nvmrc` file in a project's root (containing just `20` or `20.11.0`) lets you run `nvm use` (no argument) inside that directory — nvm reads the file and switches automatically, letting teams standardize per-project Node versions in version control.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → nvm को shell script से install करें: `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash` — यह आपके shell profile (`.bashrc`/`.zshrc`) में nvm का loader जोड़ता है।
Step 2 → `nvm install 20` Node.js v20 को `~/.nvm/versions/node/v20.x.x/` में install करता है — system Node install से पूरी तरह अलग।
Step 3 → `nvm use 20` आपके CURRENT shell session को उस version पर switch करता है — `PATH` उस version के `node`/`npm` binaries की तरफ update होता है।
Step 4 → `nvm install 18 && nvm install 20` से दोनों simultaneously install हो सकते हैं; `nvm ls` सारे installed versions list करता है; `nvm use 18` से वापस switch हो सकता है।
Step 5 → `nvm alias default 20` set करता है कि नए shell sessions में automatically कौन सा version load हो, ताकि हर बार terminal खोलने पर `nvm use` न चलाना पड़े।
Step 6 → Project root में `.nvmrc` file (जिसमें सिर्फ `20` या `20.11.0` हो) रखकर उस directory में `nvm use` (बिना argument) चला सकते हैं — nvm file पढ़कर automatically switch करता है, teams per-project Node versions को version control में standardize कर सकती हैं।

---

## 🟡 Real World Example
**A consultancy maintaining multiple client projects:** One client's legacy e-commerce backend (like an older Flipkart-style monolith) requires Node 16, while a new client's microservice needs Node 20. A developer switches context by simply `cd`-ing into each project directory — if both have `.nvmrc` files and the shell is configured with nvm's auto-use hook, the correct Node version loads automatically, avoiding "works on my machine" version mismatch bugs entirely.

## 🟡 Real Example Hindi mein
**कई client projects maintain करने वाली एक consultancy:** एक client का legacy e-commerce backend (जैसे पुराना Flipkart-style monolith) Node 16 चाहता है, जबकि नए client का microservice Node 20 चाहता है। Developer हर project directory में `cd` करके context switch करता है — अगर दोनों में `.nvmrc` files हैं और shell nvm के auto-use hook से configured है, सही Node version automatically load होता है, "works on my machine" version mismatch bugs पूरी तरह avoid होते हैं।

---

## 💻 Code Example — Basic
```bash
# nvm-basic-commands.sh
# Not JavaScript — these are terminal commands for using nvm itself

# Install nvm (one-time setup)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Install specific Node versions
nvm install 18
nvm install 20
nvm install 22

# List all installed versions (shows current with an arrow)
nvm ls

# Switch to a specific version for THIS shell session
nvm use 20

# Check active version
node --version   # v20.x.x

# Set default version for all NEW terminal sessions
nvm alias default 20

# Uninstall a version you no longer need
nvm uninstall 18
```

## 💻 Code Example — Advanced
```javascript
// detect-and-guard-node-version.js
// A Node.js script (run via `node`) that programmatically verifies
// the developer is on an nvm-managed version matching project requirements.
// Place this as a "preinstall" or "predev" npm script.

const fs = require('fs');
const path = require('path');

function readNvmrc() {
  const nvmrcPath = path.join(process.cwd(), '.nvmrc');
  if (!fs.existsSync(nvmrcPath)) return null;
  return fs.readFileSync(nvmrcPath, 'utf8').trim(); // e.g. "20.11.0" or "20"
}

function checkVersion() {
  const required = readNvmrc();
  const current = process.version.replace('v', ''); // e.g. "20.11.0"

  if (!required) {
    console.warn('No .nvmrc found — skipping version check.');
    return;
  }

  // Simple major-version comparison (good enough for most teams)
  const requiredMajor = required.split('.')[0];
  const currentMajor = current.split('.')[0];

  if (requiredMajor !== currentMajor) {
    console.error(`
      Node.js version mismatch!
      Project requires: ${required} (see .nvmrc)
      You are running: ${current}
      Fix with: nvm install && nvm use
    `);
    process.exit(1);
  }
  console.log(`Node.js version OK (${current} matches .nvmrc: ${required})`);
}

checkVersion();
```

---

## 🟠 Express.js Integration
```javascript
// Express project setup demonstrating a typical nvm-based workflow
// (file: package.json excerpt + .nvmrc + server.js)

// .nvmrc (place in project root, plain text file):
// 20.11.0

// package.json excerpt:
/*
{
  "scripts": {
    "predev": "node scripts/check-node-version.js",
    "dev": "nodemon server.js"
  },
  "engines": { "node": "20.11.0" }
}
*/

// server.js
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.json({ message: 'Running on nvm-managed Node.js', version: process.version });
});

app.listen(3000, () => {
  console.log(`Server started with Node.js ${process.version} (managed via nvm)`);
});

// Team workflow:
// 1. git clone the repo
// 2. cd into project directory (with .nvmrc present)
// 3. run: nvm install && nvm use   (installs + switches to the pinned version)
// 4. npm install && npm run dev
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Installing global npm packages before switching nvm versions, then wondering why they "disappeared"
```bash
# Wrong — global packages are installed PER nvm version, not shared
nvm use 18
npm install -g typescript
nvm use 20
tsc --version  # "command not found" — typescript was only installed under v18!

# Correct — reinstall global packages for each version you use, or use
# `nvm install 20 --reuse-npm-config` / manage global tools via npx instead
nvm use 20
npm install -g typescript
```

❌ Mistake 2: Forgetting `nvm use` after opening a new terminal, then debugging a "wrong version" mystery
```bash
# Wrong — assuming the shell remembers your last `nvm use` forever
# (it only persists for that session; new terminals use the default alias)

# Correct — set a sensible default AND use .nvmrc + shell auto-switching hooks
nvm alias default 20
# Add this to .zshrc/.bashrc for automatic .nvmrc detection on `cd`:
# autoload -U add-zsh-hook  (zsh) or equivalent bash hook from nvm's docs
```

---

## 🧠 Tricky Interview Question

**Q: You run `npm install -g pm2` while on Node 18 via nvm. Later you `nvm use 20` and try `pm2 --version` — it fails with "command not found." Why?**
Answer: nvm installs each Node.js version with its OWN isolated `node_modules` and global package directory under `~/.nvm/versions/node/v18.x.x/lib/node_modules/`. Global packages are NOT shared across nvm-managed versions — each version has its own global package set. You must reinstall global tools (`npm install -g pm2`) separately under each Node version you plan to use them with, or rely on `npx` to avoid needing global installs at all.

---

## ⚫ Interview Questions + Answers

Q1: What problem does nvm solve that a system package manager (apt/brew) doesn't?
A1: System package managers typically install ONE global Node.js version, requiring `sudo` to change, and make switching between projects needing different versions cumbersome. nvm installs versions per-user, side-by-side, switchable instantly without elevated permissions.

Q2: What is a `.nvmrc` file used for?
A2: It's a plain text file in a project's root containing the required Node.js version (e.g., `20.11.0`). Running `nvm use` with no arguments inside that directory reads the file and switches to that version automatically — useful for team-wide consistency.

Q3: Does `nvm use` change the Node version permanently?
A3: No — it only affects the CURRENT shell session's `PATH`. To make a version persist across new terminal sessions, you set it as the default with `nvm alias default <version>`, or rely on `.nvmrc` + shell hooks for automatic per-directory switching.

Q4: What's the difference between nvm and tools like `n`, `fnm`, or Volta?
A4: They solve the same core problem (multiple Node version management) with different implementations — `fnm` and Volta are written in Rust and are notably faster at version switching than nvm's shell-script-based approach; Volta also manages per-project package manager versions (npm/yarn/pnpm) and auto-switches without manual commands.

Q5: Can you use nvm in a CI/CD pipeline or production server?
A5: It's common in CI (to match the exact Node version from `.nvmrc`), but production deployments more often use Docker images pinned to a specific Node version (`FROM node:20-alpine`) directly, rather than invoking nvm inside the container, for simplicity and smaller image size.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Developing locally across multiple projects with different Node.js version requirements
- Needing to test your code against multiple Node versions before release

❌ Avoid when:
- In production containers — prefer pinning the Docker base image to an exact Node version instead of running nvm inside the container at runtime

---

## 📊 Visual Diagram
```
NVM: ISOLATED NODE VERSIONS PER USER
──────────────────────────────────────────────
  ~/.nvm/versions/node/
  ├── v16.20.2/   (legacy project)
  │   └── lib/node_modules/  (own global packages)
  ├── v18.19.0/
  │   └── lib/node_modules/
  └── v20.11.0/   (current default, via `nvm alias default 20`)
      └── lib/node_modules/

  Project A (.nvmrc: 16.20.2)  → `cd` here → `nvm use` → Node 16 active
  Project B (.nvmrc: 20.11.0)  → `cd` here → `nvm use` → Node 20 active

  PATH updates dynamically based on which version is "in use"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| nvm | Node Version Manager tool | Node Version Manager tool |
| .nvmrc | File pinning a project's required Node version | Project का Node version बताने वाली file |
| alias default | Version loaded automatically in new shells | नए shells में automatically load होने वाला version |
| Global packages | npm packages installed outside a project, per Node version | Project के बाहर, per-version installed npm packages |
| PATH | Shell variable determining which binaries run | कौन से binaries चलेंगे, यह बताने वाला shell variable |

---

## ⚡ 3-Line Summary
English:
1. nvm lets you install and switch between multiple isolated Node.js versions on one machine, without `sudo` or system-wide conflicts.
2. `.nvmrc` files let teams pin a project's exact required Node version in version control, with `nvm use` auto-detecting it.
3. Global npm packages are NOT shared across nvm-managed versions — you must reinstall them per version, or avoid globals via `npx`.

Hindi:
1. nvm एक machine पर कई isolated Node.js versions install और switch करने देता है, बिना `sudo` या system-wide conflicts के।
2. `.nvmrc` files teams को project का exact Node version version control में pin करने देती हैं, `nvm use` उसे auto-detect करता है।
3. Global npm packages nvm-managed versions में shared नहीं होतीं — हर version के लिए अलग से install करना पड़ता है, या `npx` से globals avoid करें।

---

## ➡️ Next Topic
**14. npm vs yarn vs pnpm** — Now that Node version management is clear, compare the package managers that run on top of it.
