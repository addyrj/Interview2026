# 262. When OTA Update is Enough
# हिंदी में: कब OTA Update काफ़ी है
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52+ examples (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
OTA is enough when your change touches only JavaScript, TypeScript, styles, JSON config and bundled assets (images, fonts already loaded by existing native code) and the installed binary already contains every native module your new JS needs.

## 🔵 सरल परिभाषा (Hindi)
OTA तब काफ़ी है जब बदलाव सिर्फ JavaScript, TypeScript, styles, JSON config और assets में हो और installed binary में नया JS चलाने के लिए ज़रूरी सारे native modules पहले से हों।

---

## 🔴 Problem it Solves
```
PROBLEM: Teams do full store releases for a one-line text fix.
SOLUTION: A simple decision rule: JS-only + native-compatible => OTA.
```

## 🔴 यह क्यों बना? (Hindi)
एक लाइन के fix के लिए पूरा store release करना समय की बर्बादी है। यह नियम बताता है कि कब OTA से काम चल जाएगा।

---

## 🟢 How it Works — Step by Step
```
Step 1 → What files changed? (git diff --stat)
Step 2 → Any change in package.json native deps, app.json native config, ios/ android/ ?
Step 3 → NO -> JS-only: continue.  YES -> need a full build (topic 263)
Step 4 → Does the new JS import a native module missing from the installed binary?
Step 5 → NO -> publish to a staging channel, test, then production channel
Step 6 → Monitor crash rate; republish previous update if bad
```

### OTA-friendly changes (examples)
| Change | OTA OK? |
|--------|---------|
| Fix a typo, change colour, spacing | Yes |
| Fix logic bug in a reducer / API call | Yes |
| New screen built with existing components | Yes |
| New pure-JS library (e.g. date-fns, zustand) | Yes |
| Change API base URL / feature flags | Yes |
| Update images/fonts imported via JS assets | Yes (assets ship with update) |
| Update only translation JSON | Yes |

## 🟢 कैसे काम करता है? (Hindi)
1. `git diff` से देखो क्या बदला।
2. native dependencies, app.json native config या ios/android folder बदला है?
3. नहीं -> JS-only -> आगे बढ़ो; हाँ -> full build चाहिए।
4. नया JS ऐसा native module तो नहीं माँग रहा जो binary में नहीं?
5. नहीं -> पहले staging channel पर test, फिर production पर publish।
6. Crash rate देखो; खराब हो तो पुराना update दोबारा भेजो।

---

## 🟡 Real World Example
Swiggy-जैसे app में "Free delivery above ₹199" को "₹149" करना, restaurant card का spacing बदलना, या cart total के rounding bug को ठीक करना - सब OTA योग्य हैं। Paytm-जैसे app में नया pure-JS "split bill" screen भी OTA से जा सकता है अगर कोई नया native SDK नहीं चाहिए (और company की compliance policy इसकी अनुमति दे)।

## 🟡 Real Example Hindi mein
ऑफ़र का text बदलना, cart total का bug, नया pure-JS screen - ये सब OTA से हो सकते हैं। नया camera या payment SDK जोड़ना हो तो नहीं।

---

## 💻 Code Example — Basic (guard: is this OTA safe? script)
```js
// ota-check.js - run in CI: fails if native-affecting files changed since last release tag
const { execSync } = require('child_process');                       // run git commands

const base = process.argv[2] || 'origin/main';                       // compare against this ref
const changed = execSync(`git diff --name-only ${base}...HEAD`)     // list changed files
  .toString().split('\n').filter(Boolean);                           // clean empty lines

const nativePatterns = [                                             // files that need a new build
  /^ios\//, /^android\//,                                            // native folders (bare/prebuild)
  /^app\.(json|config\.(js|ts))$/,                                   // Expo config (may include native config)
  /^package\.json$/, /^package-lock\.json$/, /^yarn\.lock$/,         // dependency changes (check manually)
];

const risky = changed.filter(f => nativePatterns.some(p => p.test(f))); // matched files
if (risky.length) {                                                  // some risky file changed
  console.log('Build may be required. Review:\n' + risky.join('\n'));
  process.exit(1);                                                   // fail the OTA job
}
console.log('JS-only change. OTA likely OK.');                        // pass
```
Heuristic only: package.json changes can be JS-only deps; a human review (or the `@expo/fingerprint` tool) is the final decision.

## 💻 Code Example — Advanced (fingerprint-based decision, Expo)
```bash
# @expo/fingerprint hashes the native-relevant project state (SDK 50+ policy "fingerprint" uses it)
npx @expo/fingerprint . > fingerprint.json           # write current fingerprint
# compare with the fingerprint saved when the production binary was built:
npx @expo/fingerprint diff old-fingerprint.json fingerprint.json   # same hash => OTA safe; different => build needed
```
```json
{
  "expo": {
    "runtimeVersion": { "policy": "fingerprint" }
  }
}
```
With the `fingerprint` runtimeVersion policy, an update is only delivered to binaries whose native fingerprint matches. Verify subcommand names and flags in current `@expo/fingerprint` docs; this snippet was not run.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| JS/asset OTA | Allowed | Allowed (2.5.2 conditions) |
| Big feature via OTA | Possible but check policy | Risky if it changes primary purpose |
| Permissions UI | Runtime permission uses declared manifest permissions | Needs Info.plist strings in binary |
| New asset fonts | Via expo-font (JS) OK | Same |
| Rollout control | Channels/branches | Same |
| Testing | Preview build / internal track | Preview build / TestFlight |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
eas update --branch production --message "Fix offer text"   # JS-only publish
```
CLI way:
```bash
# bare RN with expo-updates: same command works if expo-updates is configured
eas update --branch production --message "Fix offer text"
# no expo-updates? then a store build is the only way (or Revopush / self-hosted)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Pushing OTA straight to production.
✅ Correct: staging channel -> verify on a real device -> promote.

❌ Mistake 2: Adding a native-dependency package and calling it "JS only".
✅ Correct: Anything with native code (`expo-*` modules, RN community libs with android/ios) needs a build.

❌ Mistake 3: Ignoring the runtimeVersion.
✅ Correct: Same runtimeVersion = same native code.

❌ Mistake 4: Skipping release notes/messages.
✅ Correct: `--message` helps trace which update is live.

---

## 🧠 Tricky Interview Question
You upgrade `zustand` (pure JS) from 4 to 5 and also change a splash image in app.json. OTA enough?

Answer: Not entirely. The zustand upgrade is JS (OTA-able), but the splash image configured in app.json is baked into the native binary (native splash resources), so changing it needs a new build. An OTA can still deliver the JS part but the splash change will not appear.

---

## ⚫ Interview Questions + Answers
Q1: Is changing an image used inside a screen OTA-able?
A1: Yes, if it is a JS-required asset; it ships with the update.

Q2: Is adding `expo-camera` OTA-able?
A2: No; it is a native module.

Q3: Is changing the API URL via `Constants.expoConfig.extra` OTA-able?
A3: Values in `extra` come from the app config embedded in the update manifest, so they can change via OTA; verify with your setup.

Q4: Safest way to know?
A4: Fingerprint policy + staging test.

Q5: Can OTA fix a crash on startup?
A5: Only if the app can still launch long enough to fetch it (or the bad update triggers fallback); otherwise users must update from the store.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Bug fixes, copy changes, new JS-only screens, flags

❌ Avoid when:
- Native modules, permissions, icons, splash, SDK upgrade

---

## 📊 Visual Diagram
```
 Change --> touches ios/ android/ native deps / permissions ?
              | no                         | yes
              v                            v
        eas update (OTA)            full build + store
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JS-only change | No native code touched | सिर्फ JS बदलाव |
| Fingerprint | Hash of native state | Native स्थिति का hash |
| Staging channel | Test update stream | Test channel |
| Promote | Move update to production | Production में भेजना |
| Message | Label of an update | Update का नाम |

---

## ⚡ 3-Line Summary
English: OTA is enough for JS, styles, JSON and assets.
Check native changes and runtimeVersion first.
Test on staging then promote.

Hindi: JS, styles, JSON और assets के लिए OTA काफ़ी है।
पहले native बदलाव और runtimeVersion जाँचो।
Staging पर test करके फिर promote करो।

---

## ➡️ Next Topic
**263. When Full Build is Required** — ठीक उल्टा सवाल: कब OTA नहीं चलेगा।
