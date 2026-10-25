# 12. Node.js Versions (LTS vs Current)
# हिंदी में: Node.js Versions (LTS vs Current)

---

## 🔵 Simple Definition (English)
Node.js releases a new major version every 6 months. Even-numbered versions (18, 20, 22...) become **LTS (Long Term Support)** — stable, supported for ~30 months, recommended for production. Odd-numbered versions (19, 21, 23...) are **Current** releases — get new features first, but are NOT recommended for production and reach end-of-life quickly.

## 🔵 सरल परिभाषा (Hindi)
Node.js हर 6 महीने में एक नया major version release करता है। Even-numbered versions (18, 20, 22...) **LTS (Long Term Support)** बनते हैं — stable, ~30 महीने supported, production के लिए recommended। Odd-numbered versions (19, 21, 23...) **Current** releases हैं — नए features पहले मिलते हैं, पर production के लिए recommended नहीं और जल्दी end-of-life हो जाते हैं।

---

## 🔴 Problem it Solves
Without a predictable release/support schedule, teams can't plan upgrades, security patching, or dependency compatibility confidently. Node.js's LTS schedule gives enterprises a clear, long-lived target to build against (with security patches guaranteed for ~30 months) while still letting the project innovate rapidly on "Current" releases for early adopters.

## 🔴 यह क्यों बना? (Hindi)
Predictable release/support schedule के बिना teams upgrades, security patching, dependency compatibility को confidently plan नहीं कर सकतीं। Node.js का LTS schedule enterprises को एक clear, लंबे समय तक चलने वाला target देता है (~30 महीने security patches की guarantee के साथ) जबकि "Current" releases पर project तेज़ी से innovate भी कर सकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → A new major version ships every April and October.
Step 2 → The **April release** (odd number, e.g., 19, 21) starts as "Current" — gets 6 months of active development visibility, then reaches end-of-life without ever becoming LTS.
Step 3 → The **October release** (even number, e.g., 18, 20, 22) also starts as "Current" for 6 months, then graduates to **"Active LTS"** the following April.
Step 4 → **Active LTS** phase (~12 months): receives new backported features, bug fixes, and security patches — the recommended phase for production adoption.
Step 5 → **Maintenance LTS** phase (~18 months after Active LTS): only critical bug fixes and security patches — no new features — still safe for production but you should be planning your upgrade.
Step 6 → **End-of-Life (EOL)**: no more patches at all, even for security vulnerabilities — running EOL versions in production is a real security risk.
Step 7 → Companies typically track the Node.js release schedule (nodejs.org/en/about/previous-releases) and standardize on the current Active LTS version for new projects.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → हर अप्रैल और अक्टूबर में एक नया major version आता है।
Step 2 → **अप्रैल release** (odd number, जैसे 19, 21) "Current" के रूप में शुरू होता है — 6 महीने active development, फिर कभी LTS न बनकर end-of-life हो जाता है।
Step 3 → **अक्टूबर release** (even number, जैसे 18, 20, 22) भी "Current" के रूप में 6 महीने शुरू होता है, फिर अगले अप्रैल **"Active LTS"** बन जाता है।
Step 4 → **Active LTS** phase (~12 महीने): नए backported features, bug fixes, security patches मिलते हैं — production adoption के लिए recommended phase।
Step 5 → **Maintenance LTS** phase (Active LTS के बाद ~18 महीने): सिर्फ critical bug fixes और security patches — नए features नहीं — अभी भी production के लिए safe पर upgrade plan करना शुरू करें।
Step 6 → **End-of-Life (EOL)**: कोई patches नहीं, security vulnerabilities के लिए भी नहीं — EOL versions production में चलाना असली security risk है।
Step 7 → Companies typically Node.js release schedule track करती हैं और नए projects के लिए current Active LTS version standardize करती हैं।

---

## 🟡 Real World Example
**A Razorpay-style fintech backend:** For a production payment service, the engineering team pins their Docker base image to `node:20-alpine` (an LTS version) rather than `node:21` (Current, non-LTS). This ensures 30 months of security patches, predictable upgrade windows, and avoids the risk of a Current release introducing breaking changes or lacking critical security fixes that only LTS receives on a stable schedule.

## 🟡 Real Example Hindi mein
**Razorpay जैसी fintech backend:** Production payment service के लिए engineering team अपनी Docker base image `node:20-alpine` (एक LTS version) पर pin करती है, `node:21` (Current, non-LTS) पर नहीं। इससे 30 महीने security patches, predictable upgrade windows मिलते हैं, और Current release में breaking changes या सिर्फ LTS में मिलने वाले critical security fixes की कमी का risk avoid होता है।

---

## 💻 Code Example — Basic
```javascript
// check-node-version.js
// Check your runtime version and compare against engine requirements

console.log('Node.js version:', process.version);              // e.g. "v20.11.0"
console.log('Major version:', process.versions.node.split('.')[0]); // "20"

// Programmatically enforce a minimum version (common in production scripts)
const [major] = process.versions.node.split('.').map(Number);
const MIN_SUPPORTED_MAJOR = 18;

if (major < MIN_SUPPORTED_MAJOR) {
  console.error(`This app requires Node.js ${MIN_SUPPORTED_MAJOR}+, you have ${process.version}`);
  process.exit(1);
}
console.log('Node.js version check passed.');
```

## 💻 Code Example — Advanced
```javascript
// package-engines-advanced.js
// Not runnable JS logic alone — demonstrates package.json "engines" field usage
// plus a runtime guard pattern used in production entrypoints

// package.json excerpt (place in your project root):
/*
{
  "name": "razorpay-style-service",
  "engines": {
    "node": ">=20.0.0 <23.0.0"   // restrict to supported LTS range
  },
  "engineStrict": false           // npm 7+ removed true strict enforcement by default;
                                   // use a preinstall/check script instead for hard enforcement
}
*/

// scripts/check-engine.js — run via "preinstall": "node scripts/check-engine.js"
const semver = require('semver'); // npm install semver
const pkg = require('../package.json');

const required = pkg.engines && pkg.engines.node;
if (required && !semver.satisfies(process.version, required)) {
  console.error(
    `Incompatible Node.js version. Required: ${required}, Found: ${process.version}`
  );
  process.exit(1);
}
console.log(`Node.js version ${process.version} satisfies "${required}" — OK to proceed.`);
```

---

## 🟠 Express.js Integration
```javascript
// Express app startup guard ensuring it only runs on supported Node.js versions
const express = require('express');
const semver = require('semver'); // npm install semver

const SUPPORTED_RANGE = '>=18.0.0'; // matches current Active LTS baseline

if (!semver.satisfies(process.version, SUPPORTED_RANGE)) {
  console.error(`FATAL: Node.js ${SUPPORTED_RANGE} required, running ${process.version}`);
  process.exit(1);
}

const app = express();
app.get('/version', (req, res) => {
  res.json({ nodeVersion: process.version, v8Version: process.versions.v8 });
});

app.listen(3000, () => {
  console.log(`Server started on Node.js ${process.version} (:3000)`);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Deploying production services on an odd-numbered "Current" release
```javascript
// Wrong — Dockerfile pinned to a non-LTS version
// FROM node:21-alpine   <- Current release, short support window, risky for prod

// Correct — pin to the latest Active LTS even-numbered version
// FROM node:20-alpine   <- LTS, ~30 months of support
```

❌ Mistake 2: Letting a production app silently run on an EOL (End-of-Life) Node.js version
```javascript
// Wrong — no version enforcement, app quietly runs on Node 14 (EOL since 2023)
// with no security patches ever being applied again

// Correct — enforce supported versions at startup/CI, and set calendar reminders
// around each LTS's documented EOL date from nodejs.org/en/about/previous-releases
if (!semver.satisfies(process.version, '>=18.0.0')) {
  throw new Error('Unsupported/EOL Node.js version detected');
}
```

---

## 🧠 Tricky Interview Question

**Q: A team is starting a new production project today. Should they use the newest Node.js version released last month, or an older one?**
Answer: It depends on WHICH kind of "newest." If the newest release is an odd-numbered Current version (e.g., 23), avoid it for production — it will reach end-of-life without ever becoming LTS. If an even-numbered version just became Active LTS (e.g., 22), that IS the right production choice — newest AND most supported. The key interview insight: "newest" and "most stable/supported" are not always the same release in Node.js's schedule.

---

## ⚫ Interview Questions + Answers

Q1: What does LTS stand for and why does it matter?
A1: Long Term Support — it means that version will receive bug fixes and security patches for an extended period (~30 months total across Active + Maintenance phases), making it safe and predictable for production use, unlike Current releases.

Q2: How often does Node.js release a new major version?
A2: Every 6 months — April and October each year, following a predictable, documented release cadence.

Q3: What's the difference between "Active LTS" and "Maintenance LTS"?
A3: Active LTS (~12 months) still receives new backported features plus fixes/patches. Maintenance LTS (~18 months after that) only receives critical bug fixes and security patches — no new features — signaling it's time to plan an upgrade.

Q4: How can you check if your current Node.js version is still supported?
A4: Check the official Node.js release schedule at nodejs.org, or run `node --version` and compare against the documented EOL dates; tools/libraries like `semver` can programmatically validate version ranges in CI/CD pipelines.

Q5: Why shouldn't a company run a Current (non-LTS) release in production?
A5: Current releases have a much shorter total support window (6 months before EOL, since they never become LTS if odd-numbered), may contain less-battle-tested features, and risk breaking changes landing without the stability guarantees LTS provides.

---

## 🔷 When to Use + When Not to Use
✅ Use LTS when:
- Deploying any production service — predictability and long security support matter most

❌ Avoid relying on Current releases when:
- Building anything beyond local experimentation/early feature testing — their short lifecycle makes them unsuitable for production commitments

---

## 📊 Visual Diagram
```
NODE.JS RELEASE LIFECYCLE
─────────────────────────────────────────────────────
  Version 20 (even, released October):
  [Current: 6mo] → [Active LTS: ~12mo] → [Maintenance LTS: ~18mo] → [EOL]
       │                  │                      │
   new features      recommended for         security-fixes-only,
   first appear      PRODUCTION use           plan your upgrade

  Version 21 (odd, released April):
  [Current: 6mo] → [EOL]          <- never becomes LTS, avoid in production
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LTS | Long Term Support, stable production release | Stable production release |
| Current | Newest release, short-lived, feature-first | नवीनतम release, कम समय, नए features पहले |
| EOL | End-of-Life, no more patches/support | कोई patches/support नहीं |
| semver range | Version constraint syntax (e.g. `>=18.0.0`) | Version constraint syntax |
| engines field | package.json field declaring Node version requirement | Node version requirement बताने वाला field |

---

## ⚡ 3-Line Summary
English:
1. Node.js releases a new major version every 6 months; even numbers become LTS (production-recommended, ~30 months support), odd numbers stay Current (short-lived, never LTS).
2. LTS progresses through Active (new features + fixes) then Maintenance (fixes only) phases before reaching End-of-Life.
3. Always pin production deployments to an Active or Maintenance LTS version, and enforce version checks via `engines` in package.json or CI validation.

Hindi:
1. Node.js हर 6 महीने में नया major version release करता है; even numbers LTS बनते हैं (production-recommended, ~30 महीने support), odd numbers Current रहते हैं (कम समय, कभी LTS नहीं बनते)।
2. LTS Active (नए features + fixes) फिर Maintenance (सिर्फ fixes) phases से गुज़रकर End-of-Life तक पहुँचता है।
3. Production deployments को हमेशा Active या Maintenance LTS version पर pin करें, और `engines` field या CI validation से version checks enforce करें।

---

## ➡️ Next Topic
**13. NVM — Node Version Manager** — Learn the practical tool for installing and switching between multiple Node.js versions on your machine.
