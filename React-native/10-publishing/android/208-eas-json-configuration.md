# 208. eas.json Configuration
# हिंदी में: eas.json Configuration
# Platform: Android ✅ | iOS ✅ (Both)

> Target: **Expo SDK 52 (React Native 0.76)** with `eas-cli` — check current docs — keys may be added/deprecated between EAS CLI versions; only keys documented at https://docs.expo.dev/eas/json/ are valid.

---

## 🔵 Simple Definition (English)
`eas.json` is the settings file for EAS. It has three main parts: `cli` (CLI behaviour), `build` (named build profiles like development/preview/production) and `submit` (store upload settings).

## 🔵 सरल परिभाषा (Hindi)
`eas.json` EAS की settings file है। इसमें तीन मुख्य हिस्से हैं: `cli` (CLI का behaviour), `build` (development/preview/production जैसे नाम वाले profiles) और `submit` (store upload की settings)।

---

## 🔴 Problem it Solves
- One app needs different builds: a dev client for developers, an APK for testers, an AAB for the store.
- Different API URLs, channels and signing per environment.
- Without profiles you would pass many flags every time.

## 🔴 यह क्यों बना? (Hindi)
- एक app के अलग builds चाहिए: developers के लिए dev client, testers के लिए APK, store के लिए AAB।
- हर environment का API URL, channel और signing अलग।
- Profiles न हों तो हर बार बहुत सारे flags देने पड़ें।

---

## 🟢 How it Works — Step by Step
```
Step 1 → eas build --profile <name> reads build.<name> from eas.json
Step 2 → If profile has "extends", base profile values are merged first
Step 3 → Platform sections (android / ios) override common values
Step 4 → "env" values become environment variables during the build
Step 5 → "distribution": "store" → for stores; "internal" → shareable link/QR
Step 6 → "channel" ties the build to an EAS Update channel (OTA)
Step 7 → eas submit --profile <name> reads submit.<name>
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → eas build --profile <name> से build.<name> पढ़ा जाता है
Step 2 → "extends" हो तो base profile पहले merge होता है
Step 3 → android / ios sections common values को override करते हैं
Step 4 → "env" build के दौरान environment variables बनते हैं
Step 5 → "distribution": "store" → store के लिए; "internal" → link/QR
Step 6 → "channel" build को EAS Update channel से जोड़ता है
Step 7 → eas submit --profile <name> submit.<name> पढ़ता है
```

---

## 🟡 Real World Example
Paytm-style team: `development` (dev client for engineers), `staging` (APK to QA with staging API), `production` (AAB, auto-increment, production API, channel `production`).

## 🟡 Real Example Hindi mein
Paytm जैसी team: `development` (engineers के लिए dev client), `staging` (QA को APK, staging API), `production` (AAB, auto-increment, production API, channel `production`)।

---

## 💻 Code Example — Basic
```json
{
  "cli": {
    "version": ">= 12.0.0",
    "appVersionSource": "remote"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "android": { "buildType": "apk" }
    },
    "preview": {
      "distribution": "internal",
      "android": { "buildType": "apk" }
    },
    "production": {
      "autoIncrement": true
    }
  },
  "submit": {
    "production": {}
  }
}
```

## 💻 Code Example — Advanced
```json
{
  "cli": { "version": ">= 12.0.0", "appVersionSource": "remote" },
  "build": {
    "base": {
      "node": "20.18.0",
      "env": { "APP_ENV": "development" }
    },
    "development": {
      "extends": "base",
      "developmentClient": true,
      "distribution": "internal",
      "channel": "development",
      "android": { "buildType": "apk", "gradleCommand": ":app:assembleDebug" }
    },
    "staging": {
      "extends": "base",
      "distribution": "internal",
      "channel": "staging",
      "env": { "APP_ENV": "staging", "API_URL": "https://staging.api.foodapp.in" },
      "android": { "buildType": "apk" }
    },
    "production": {
      "extends": "base",
      "autoIncrement": true,
      "channel": "production",
      "env": { "APP_ENV": "production", "API_URL": "https://api.foodapp.in" },
      "android": { "buildType": "app-bundle" }
    }
  },
  "submit": {
    "production": {
      "android": {
        "serviceAccountKeyPath": "./secrets/play-service-account.json",
        "track": "internal",
        "releaseStatus": "draft"
      }
    }
  }
}
```
Validate the JSON before committing (Node):
```js
// validate-eas.js - run: node validate-eas.js
const fs = require('fs');                                  // file system
const cfg = JSON.parse(fs.readFileSync('eas.json', 'utf8')); // throws if invalid JSON
const profiles = Object.keys(cfg.build || {});             // list profile names
console.log('Profiles:', profiles.join(', '));             // show them
for (const [name, p] of Object.entries(cfg.build)) {      // check each profile
  if (p.extends && !cfg.build[p.extends]) {                // extends must exist
    throw new Error(`${name} extends missing profile ${p.extends}`);
  }
}
console.log('eas.json looks OK');                          // success
```

---

## 📱 Android vs iOS Difference
| Key | Android | iOS |
|-----|---------|-----|
| Build type | `android.buildType`: `apk` / `app-bundle` | `ios.simulator`, `ios.buildConfiguration` |
| Custom command | `android.gradleCommand` | `ios.scheme` |
| Submit | `submit.*.android.{serviceAccountKeyPath, track, releaseStatus}` | `submit.*.ios.{appleId, ascAppId}` |
| Image | `android.image` | `ios.image` |

---

## 🟠 Expo vs CLI Difference
Expo way:
```json
{ "build": { "production": { "autoIncrement": true } } }
```
CLI way (bare RN): same `eas.json`; native versions are read from `android/app/build.gradle` when `appVersionSource` is `local`:
```groovy
defaultConfig { versionCode 12; versionName "1.2.0" }
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Committing `play-service-account.json`.
✅ Correct: Add to `.gitignore`; supply through CI secret/file.

❌ Mistake 2: Using `distribution: "store"` for QA sharing.
✅ Correct: `internal` for APK sharing.

❌ Mistake 3: Invalid JSON (trailing commas).
✅ Correct: Validate with `node -e "JSON.parse(require('fs').readFileSync('eas.json'))"`.

❌ Mistake 4: Putting secrets in `env`.
✅ Correct: EAS secrets/environment variables.

---

## 🧠 Tricky Interview Question
"Production profile has `channel: production`, but OTA updates published to branch `main` don't reach users. Why?"

Answer: Builds listen to a *channel*; updates are published to a *branch*. You must link them (`eas channel:edit production --branch main`) — otherwise the channel points to a different branch. Also `runtimeVersion` must match between update and build.

---

## ⚫ Interview Questions + Answers
Q1: `development` vs `preview` vs `production`?
A1: Dev client with Metro / internal APK for testers / store build.

Q2: What does `autoIncrement` do?
A2: Increments `versionCode`/`buildNumber` on every build.

Q3: What is `appVersionSource`?
A3: `remote` (EAS stores versions) or `local` (project files).

Q4: Where do I set Play track?
A4: `submit.<profile>.android.track`.

Q5: Can profiles inherit?
A5: Yes, via `extends`.

---

## 🔷 When to Use + When Not to Use
✅ Use when: multi-environment builds, CI.

❌ Avoid when: putting runtime app logic here — it's build-time config only.

---

## 📊 Visual Diagram
```
 eas.json
 ├── cli    { version, appVersionSource }
 ├── build
 │    ├── development ─► dev client (APK)
 │    ├── preview     ─► internal APK
 │    └── production  ─► store AAB (autoIncrement, channel)
 └── submit
      └── production ─► Play track + service account
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Profile | Build configuration | Build configuration |
| distribution | internal vs store | Link से या store से |
| channel | OTA update stream | OTA update की धारा |
| track | Play release lane | Play की release lane |
| extends | Inherit profile | Profile विरासत में लेना |

---

## ⚡ 3-Line Summary
English: eas.json = cli + build profiles + submit settings.
Use extends, env, channel, buildType and autoIncrement.
Validate JSON and keep secrets out.

Hindi: eas.json = cli + build profiles + submit settings।
extends, env, channel, buildType और autoIncrement इस्तेमाल करो।
JSON validate करो और secrets बाहर रखो।

---

## ➡️ Next Topic
**209. EAS Submit to Play Store** — बने हुए AAB को automatically upload करना।
