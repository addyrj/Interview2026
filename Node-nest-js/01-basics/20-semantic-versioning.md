# 20. Semantic Versioning (^, ~, *)
# हिंदी में: Semantic Versioning (^, ~, *)

---

## 🔵 Simple Definition (English)
**Semantic Versioning (SemVer)** is a `MAJOR.MINOR.PATCH` version numbering convention (e.g., `4.18.2`) where each part has a strict meaning. The symbols `^` (caret), `~` (tilde), and `*` (asterisk) in `package.json` define how FLEXIBLE a dependency's allowed version range is when you run `npm install`.

## 🔵 सरल परिभाषा (Hindi)
**Semantic Versioning (SemVer)** एक `MAJOR.MINOR.PATCH` version numbering convention है (जैसे `4.18.2`) जहाँ हर part का strict मतलब है। `package.json` में `^` (caret), `~` (tilde), और `*` (asterisk) symbols बताते हैं कि `npm install` चलाने पर dependency का allowed version range कितना FLEXIBLE है।

---

## 🔴 Problem it Solves
Without a shared convention, there'd be no way to know if upgrading a dependency is SAFE (bug fix) or RISKY (breaking change) just by looking at a version number. SemVer gives every package author and consumer a universal signal: increment PATCH for safe bug fixes, MINOR for safe new features, MAJOR for breaking changes — letting tools (npm) automate "safe" auto-upgrades within a declared range.

## 🔴 यह क्यों बना? (Hindi)
Shared convention के बिना सिर्फ version number देखकर पता नहीं चलता कि dependency upgrade करना SAFE है (bug fix) या RISKY (breaking change)। SemVer हर package author और consumer को एक universal signal देता है: PATCH बढ़ाएं safe bug fixes के लिए, MINOR safe नए features के लिए, MAJOR breaking changes के लिए — tools (npm) को declared range के अंदर "safe" auto-upgrades automate करने देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → A version like `4.18.2` breaks down as: **MAJOR** (`4`) = breaking changes, **MINOR** (`18`) = new backward-compatible features, **PATCH** (`2`) = backward-compatible bug fixes.
Step 2 → **`^4.18.2` (caret, npm's default)**: allows updates that do NOT change the leftmost non-zero digit — so `4.19.0`, `4.99.5` are allowed, but `5.0.0` is NOT. This is the most common and generally recommended range.
Step 3 → **`~4.18.2` (tilde)**: allows only PATCH-level updates — `4.18.3`, `4.18.9` are allowed, but `4.19.0` is NOT. More conservative than caret.
Step 4 → **`*` (asterisk) or `latest`**: allows ANY version, including major breaking changes — rarely recommended for production dependencies since it offers zero stability guarantee.
Step 5 → **Exact version** (`4.18.2`, no symbol): locks to that EXACT version only — npm will never auto-upgrade it, even for patches. Used when you need absolute certainty (rare, usually for known-problematic packages).
Step 6 → **Special case for 0.x versions**: for `^0.18.2`, caret behaves MORE conservatively — it only allows patch updates (treats the MINOR digit as the "important" one when MAJOR is 0), since pre-1.0 packages are considered unstable by convention; `^0.0.3` allows ONLY that exact version.
Step 7 → `npm install <pkg>` without `--save-exact` defaults to writing `^<version>` into `package.json`; `npm install <pkg> --save-exact` writes the exact pinned version instead.
Step 8 → `npm outdated` shows which installed packages have newer versions available within vs beyond your declared ranges; `npm update` upgrades within the allowed ranges only.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `4.18.2` जैसा version टूटता है: **MAJOR** (`4`) = breaking changes, **MINOR** (`18`) = backward-compatible नए features, **PATCH** (`2`) = backward-compatible bug fixes।
Step 2 → **`^4.18.2` (caret, npm का default)**: उन updates को allow करता है जो leftmost non-zero digit न बदलें — तो `4.19.0`, `4.99.5` allowed हैं, पर `5.0.0` नहीं। यह सबसे common और generally recommended range है।
Step 3 → **`~4.18.2` (tilde)**: सिर्फ PATCH-level updates allow करता है — `4.18.3`, `4.18.9` allowed, पर `4.19.0` नहीं। Caret से ज़्यादा conservative।
Step 4 → **`*` (asterisk) या `latest`**: कोई भी version allow करता है, major breaking changes सहित — production dependencies के लिए rarely recommended क्योंकि कोई stability guarantee नहीं।
Step 5 → **Exact version** (`4.18.2`, कोई symbol नहीं): सिर्फ उस EXACT version पर lock करता है — npm कभी auto-upgrade नहीं करेगा, patches के लिए भी नहीं। Absolute certainty चाहिए होने पर इस्तेमाल होता है (rare, usually known-problematic packages के लिए)।
Step 6 → **0.x versions के लिए special case**: `^0.18.2` के लिए caret ज़्यादा conservative behave करता है — सिर्फ patch updates allow करता है (MAJOR 0 होने पर MINOR digit को "important" मानता है), क्योंकि pre-1.0 packages convention से unstable माने जाते हैं; `^0.0.3` सिर्फ वह exact version allow करता है।
Step 7 → `npm install <pkg>` बिना `--save-exact` के default रूप से `^<version>` लिखता है `package.json` में; `npm install <pkg> --save-exact` exact pinned version लिखता है।
Step 8 → `npm outdated` दिखाता है कौन से installed packages के newer versions available हैं आपकी declared ranges के अंदर vs बाहर; `npm update` सिर्फ allowed ranges के अंदर upgrade करता है।

---

## 🟡 Real World Example
**A Paytm backend service pinning `jsonwebtoken`:** The team deliberately uses `"jsonwebtoken": "~9.0.0"` (tilde, not caret) for this security-critical library — they want PATCH-level security fixes automatically, but want to manually review and test any MINOR version bump themselves before adopting it, since JWT validation logic changes carry real security implications even in "non-breaking" minor releases.

## 🟡 Real Example Hindi mein
**Paytm backend service जो `jsonwebtoken` pin करती है:** Team deliberately इस security-critical library के लिए `"jsonwebtoken": "~9.0.0"` (tilde, caret नहीं) इस्तेमाल करती है — वे PATCH-level security fixes automatically चाहते हैं, पर किसी भी MINOR version bump को खुद manually review और test करना चाहते हैं adopt करने से पहले, क्योंकि JWT validation logic changes में real security implications होते हैं "non-breaking" minor releases में भी।

---

## 💻 Code Example — Basic
```javascript
// semver-range-checker.js
// Using the 'semver' package (npm install semver) to check version ranges
// This mirrors exactly what npm does internally when resolving dependencies

const semver = require('semver');

const testVersion = '4.19.2';

console.log('Does 4.19.2 satisfy ^4.18.2?', semver.satisfies(testVersion, '^4.18.2')); // true
console.log('Does 4.19.2 satisfy ~4.18.2?', semver.satisfies(testVersion, '~4.18.2')); // false
console.log('Does 4.19.2 satisfy *?', semver.satisfies(testVersion, '*'));             // true
console.log('Does 4.19.2 satisfy 4.18.2 (exact)?', semver.satisfies(testVersion, '4.18.2')); // false

// Parsing a version into its components
const parsed = semver.parse('4.18.2');
console.log('Major:', parsed.major, 'Minor:', parsed.minor, 'Patch:', parsed.patch);

// Comparing versions
console.log('Is 5.0.0 greater than 4.99.9?', semver.gt('5.0.0', '4.99.9')); // true
console.log('Is 4.18.2 a prerelease?', semver.prerelease('4.18.2')); // null (not a prerelease)
console.log('Is 4.18.2-beta.1 a prerelease?', semver.prerelease('4.18.2-beta.1')); // ['beta', 1]
```

## 💻 Code Example — Advanced
```javascript
// dependency-risk-analyzer.js
// Production-style script: scans package.json and flags "risky" version ranges
// (useful in a pre-merge CI check to enforce dependency version discipline)

const fs = require('fs');

function analyzeDependencyRisk(packageJsonPath = './package.json') {
  const pkg = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  const allDeps = { ...pkg.dependencies, ...pkg.devDependencies };

  const risky = [];
  const conservative = [];
  const flexible = [];

  for (const [name, range] of Object.entries(allDeps)) {
    if (range === '*' || range === 'latest') {
      risky.push({ name, range, reason: 'Unbounded — any version, including breaking changes' });
    } else if (range.startsWith('~')) {
      conservative.push({ name, range });
    } else if (range.startsWith('^')) {
      flexible.push({ name, range });
    } else if (/^\d/.test(range)) {
      conservative.push({ name, range, reason: 'Exact pin — no auto-updates at all' });
    }
  }

  console.log(`\nRISKY ranges (${risky.length}) — review these:`);
  risky.forEach((d) => console.log(`  ${d.name}: "${d.range}" — ${d.reason}`));

  console.log(`\nConservative ranges (${conservative.length}):`);
  conservative.forEach((d) => console.log(`  ${d.name}: "${d.range}"`));

  console.log(`\nFlexible (caret) ranges (${flexible.length}):`);
  flexible.forEach((d) => console.log(`  ${d.name}: "${d.range}"`));

  if (risky.length > 0) {
    console.error('\nFAILED: Unbounded version ranges detected. Pin them explicitly.');
    process.exit(1);
  }
  console.log('\nAll dependency ranges look reasonable.');
}

analyzeDependencyRisk();
```

---

## 🟠 Express.js Integration
```javascript
// Express project's package.json illustrating deliberate SemVer range choices
/*
{
  "dependencies": {
    "express": "^4.19.2",         // caret OK — mature, stable, well-tested framework
    "jsonwebtoken": "~9.0.2",     // tilde — security-critical, review minors manually
    "stripe": "14.25.0",          // exact pin — payment SDK, zero surprise tolerance
    "lodash": "^4.17.21"          // caret OK — stable utility library
  },
  "devDependencies": {
    "nodemon": "^3.1.0",          // caret fine — dev-only, low production risk
    "jest": "^29.7.0"
  }
}
*/

const express = require('express');
const jwt = require('jsonwebtoken');
const app = express();

app.get('/verify', (req, res) => {
  try {
    const decoded = jwt.verify(req.query.token, process.env.JWT_SECRET);
    res.json({ valid: true, decoded });
  } catch (err) {
    res.status(401).json({ valid: false, error: err.message });
  }
});

app.listen(3000, () => console.log('Server on :3000 — see package.json for SemVer strategy'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `*` or `latest` for any production dependency
```json
// Wrong — zero protection against breaking changes landing silently
{ "dependencies": { "some-critical-lib": "*" } }

// Correct — at minimum use caret, or pin exactly for critical packages
{ "dependencies": { "some-critical-lib": "^2.3.1" } }
```

❌ Mistake 2: Assuming caret (`^`) is always safe because "it's SemVer, so no breaking changes"
```javascript
// Wrong assumption: "caret guarantees zero breaking changes, ever"
// Reality: SemVer is a CONVENTION, not an enforced guarantee — a package author
// can accidentally (or carelessly) publish a breaking change as a MINOR or PATCH
// bump. Always run your test suite after any dependency update, regardless of
// the declared range, and read changelogs for critical dependencies.
```

---

## 🧠 Tricky Interview Question

**Q: `package.json` has `"some-lib": "^0.4.2"`. A new version `0.5.0` is published. Does `npm install` pick it up automatically?**
Answer: NO. For `0.x` versions, npm's caret behaves specially: since the MAJOR version is `0` (meaning "unstable/pre-release" by SemVer convention), caret treats the MINOR digit as the significant one — `^0.4.2` only allows `0.4.x` patch updates (e.g., `0.4.3`, `0.4.9`), NOT `0.5.0`. This differs from `^4.2.0`, where caret allows `4.x.x` freely. This 0.x caret behavior is a classic SemVer interview trap.

---

## ⚫ Interview Questions + Answers

Q1: What do the three numbers in a SemVer version (e.g., `2.5.1`) represent?
A1: MAJOR.MINOR.PATCH — MAJOR increments for breaking/incompatible API changes, MINOR increments for new backward-compatible functionality, PATCH increments for backward-compatible bug fixes.

Q2: What's the difference between `^1.2.3` and `~1.2.3`?
A2: `^1.2.3` allows any version up to (but not including) the next MAJOR version (e.g., up to `<2.0.0`) — so MINOR and PATCH updates are both allowed. `~1.2.3` is stricter, allowing only PATCH-level updates within the same MINOR version (e.g., up to `<1.3.0`).

Q3: Why does caret (`^`) behave differently for `0.x.y` versions?
A3: Because SemVer convention treats any `0.MAJOR.MINOR` version as potentially unstable/experimental — for these, caret only allows PATCH updates (treating MINOR as the "breaking-change-prone" digit), since a MINOR bump in a pre-1.0 package is more likely to include real breaking changes.

Q4: How do you lock a dependency to an EXACT version with no auto-updates at all?
A4: Omit the range symbol entirely in `package.json` (e.g., `"pkg": "4.18.2"`), or install with `npm install pkg --save-exact` — npm will never auto-upgrade it, even across patch releases, without an explicit manual bump.

Q5: Is SemVer enforced by npm, or is it just a convention package authors follow?
A5: It's a convention, not an enforced rule. npm's tooling (version ranges, `npm update`) assumes authors follow SemVer correctly, but nothing technically prevents a package from publishing a breaking change under a MINOR or PATCH bump — which is why lockfiles, CI test suites, and careful changelog review remain essential even with "safe" version ranges.

---

## 🔷 When to Use + When Not to Use
✅ Use `^` (caret, npm default) when:
- The dependency is mature, well-maintained, and you trust its SemVer discipline — the common case for most packages

✅ Use `~` (tilde) or exact pins when:
- The dependency is security-critical, a payment/crypto SDK, or has a history of "accidental" breaking minor releases

❌ Avoid `*`/`latest` when:
- Writing ANY production `package.json` — it provides no stability guarantee whatsoever

---

## 📊 Visual Diagram
```
SEMVER RANGE BEHAVIOR for base version 4.18.2
──────────────────────────────────────────────
  ^4.18.2   allows: 4.18.2, 4.18.9, 4.19.0, 4.99.9   NOT: 5.0.0
            |────────────── wide range ──────────────|

  ~4.18.2   allows: 4.18.2, 4.18.3, 4.18.9            NOT: 4.19.0
            |─── narrow range ───|

  4.18.2    allows: 4.18.2 ONLY                        NOT: anything else
            |exact|

  *         allows: ANYTHING, including 5.0.0, 99.0.0  (no protection)
            |────────────────── unbounded ──────────────────|

  SPECIAL CASE for 0.x:
  ^0.4.2    allows: 0.4.2, 0.4.9                       NOT: 0.5.0 (acts like ~)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SemVer | MAJOR.MINOR.PATCH version convention | MAJOR.MINOR.PATCH version convention |
| Caret (^) | Allows minor+patch updates, no major | Minor+patch updates allow, major नहीं |
| Tilde (~) | Allows only patch updates | सिर्फ patch updates allow |
| Exact pin | No symbol, locks to one exact version | कोई symbol नहीं, exact version पर lock |
| Breaking change | Incompatible API change (MAJOR bump) | Incompatible API change |
| Prerelease | Version with suffix like -beta.1 | -beta.1 जैसा suffix वाला version |

---

## ⚡ 3-Line Summary
English:
1. SemVer (`MAJOR.MINOR.PATCH`) gives a version number inherent meaning: MAJOR = breaking, MINOR = new features, PATCH = bug fixes.
2. `^` (caret, npm default) allows minor+patch updates; `~` (tilde) allows only patch updates; `*` allows anything — choose based on how much stability a dependency needs.
3. SemVer is a convention, not an enforced guarantee — always run tests after updates and consider exact pins or tildes for security/payment-critical dependencies.

Hindi:
1. SemVer (`MAJOR.MINOR.PATCH`) version number को inherent meaning देता है: MAJOR = breaking, MINOR = नए features, PATCH = bug fixes।
2. `^` (caret, npm default) minor+patch updates allow करता है; `~` (tilde) सिर्फ patch updates; `*` कुछ भी allow करता है — dependency को कितनी stability चाहिए उस आधार पर चुनें।
3. SemVer एक convention है, enforced guarantee नहीं — updates के बाद हमेशा tests चलाएं और security/payment-critical dependencies के लिए exact pins या tildes consider करें।

---

## ➡️ Next Topic
**21. Global vs Local Packages** — Apply SemVer understanding to the practical question of where and how packages get installed.
