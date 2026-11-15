# 207. EAS Build Setup + Configuration
# हिंदी में: EAS Build Setup और Configuration
# Platform: Android ✅ | iOS ✅ (Both)

> Target: **Expo SDK 52 (React Native 0.76)** with `eas-cli` — check current docs — CLI commands (e.g. `eas secret:*` vs newer `eas env:*`) change between versions.

---

## 🔵 Simple Definition (English)
Setup means: create an Expo account, install `eas-cli`, log in, link your project to EAS (`eas init`), generate `eas.json` (`eas build:configure`), and set the app identifiers in `app.json`. After this one-time setup, every build is one command.

## 🔵 सरल परिभाषा (Hindi)
Setup का मतलब: Expo account बनाना, `eas-cli` install करना, login करना, project को EAS से जोड़ना (`eas init`), `eas.json` बनाना (`eas build:configure`) और `app.json` में app identifiers डालना। यह एक बार का काम है, फिर हर build एक command में होता है।

---

## 🔴 Problem it Solves
- First build fails for avoidable reasons: no package name, not logged in, project not linked, no `eas.json`.
- A clear checklist avoids these failures.

## 🔴 यह क्यों बना? (Hindi)
- पहला build अक्सर आसान कारणों से fail होता है: package name नहीं, login नहीं, project link नहीं, `eas.json` नहीं।
- Checklist से ये गलतियाँ बच जाती हैं।

---

## 🟢 How it Works — Step by Step
```
Step 1 → Sign up at https://expo.dev (free)
Step 2 → npm install -g eas-cli         (or use: npx eas-cli <command>)
Step 3 → eas login                       → enter username/email + password (+ 2FA if on)
Step 4 → eas whoami                      → prints your username (confirms login)
Step 5 → cd my-app && eas init           → creates project on expo.dev, adds extra.eas.projectId to app.json
Step 6 → eas build:configure             → asks platform(s), writes eas.json
Step 7 → Edit app.json: name, slug, version, android.package, ios.bundleIdentifier
Step 8 → npx expo-doctor                 → checks dependency/SDK issues
Step 9 → eas build -p android --profile preview   → first build
Step 10 → For CI: create token at expo.dev → Account settings → Access tokens → set EXPO_TOKEN
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → expo.dev पर free account बनाओ
Step 2 → npm install -g eas-cli  (या npx eas-cli)
Step 3 → eas login → username/password (और 2FA)
Step 4 → eas whoami → login confirm
Step 5 → eas init → expo.dev पर project बनता है, app.json में projectId जुड़ता है
Step 6 → eas build:configure → platform चुनो, eas.json बनता है
Step 7 → app.json में name, slug, version, android.package डालो
Step 8 → npx expo-doctor → समस्याएँ check करो
Step 9 → eas build -p android --profile preview → पहला build
Step 10 → CI के लिए expo.dev से access token बनाओ → EXPO_TOKEN
```

**Console screens (described):**
- **expo.dev dashboard:** left sidebar lists Projects, Builds, Updates, Credentials, Settings. After `eas init` your project card appears with slug and owner.
- **Access tokens page (Account settings → Access tokens):** "Create Token" button opens a dialog with a name field; the token string is shown only once — copy it immediately.
- **Terminal first build:** prompts "Generate a new Android Keystore?" → Yes.

---

## 🟡 Real World Example
A freelancer cloning a Swiggy-like app sets up EAS once on a Windows laptop; then a client can run builds from their own expo.dev organisation by transferring the project.

## 🟡 Real Example Hindi mein
Swiggy जैसा app बनाने वाला freelancer Windows laptop पर EAS एक बार setup करता है; फिर project transfer करके client अपने expo.dev organisation से builds चला सकता है।

---

## 💻 Code Example — Basic
```json
{
  "expo": {
    "name": "FoodApp",
    "slug": "food-app",
    "version": "1.0.0",
    "android": { "package": "com.mycompany.foodapp" },
    "ios": { "bundleIdentifier": "com.mycompany.foodapp" },
    "extra": { "eas": { "projectId": "<added-by-eas-init>" } }
  }
}
```
```bash
npm install -g eas-cli
eas login
eas init
eas build:configure
```

## 💻 Code Example — Advanced
Dynamic config with environment variables and EAS env:
```js
// app.config.js - reads env set per EAS build profile
module.exports = ({ config }) => ({
  ...config,                                              // keep app.json values
  name: process.env.APP_ENV === 'production' ? 'FoodApp' : 'FoodApp Stg', // name per env
  android: {
    ...config.android,                                    // keep android settings
    package: 'com.mycompany.foodapp',                     // fixed package
  },
  extra: {
    ...config.extra,                                      // keep eas.projectId
    apiUrl: process.env.API_URL ?? 'https://staging.api.foodapp.in', // safe default
  },
});
```
```json
{
  "cli": { "version": ">= 12.0.0", "appVersionSource": "remote" },
  "build": {
    "base": { "node": "20.18.0" },
    "development": { "extends": "base", "developmentClient": true, "distribution": "internal" },
    "preview": {
      "extends": "base",
      "distribution": "internal",
      "env": { "APP_ENV": "staging", "API_URL": "https://staging.api.foodapp.in" },
      "android": { "buildType": "apk" }
    },
    "production": {
      "extends": "base",
      "autoIncrement": true,
      "env": { "APP_ENV": "production", "API_URL": "https://api.foodapp.in" }
    }
  }
}
```
```bash
# Store sensitive values on EAS servers (command names are version-dependent; newer CLIs use `eas env:create`)
eas secret:create --scope project --name SENTRY_AUTH_TOKEN --value "xxxx"
# Validate the setup before a long build
npx expo-doctor
npx expo install --check
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Identifier | `android.package` | `ios.bundleIdentifier` |
| Version | `versionCode` | `buildNumber` |
| First-build prompt | Generate keystore | Log in to Apple account, create certs |
| Extra account | Not needed to build | Apple Developer Program required |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
eas init && eas build:configure   # app.json is source of truth
```
CLI way (bare RN):
```bash
eas build:configure   # still works; identifiers come from android/app/build.gradle and Xcode
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Missing `android.package` → build asks or fails.
✅ Correct: Set unique reverse-domain id before first build.

❌ Mistake 2: Using a different Expo account than the project owner.
✅ Correct: `eas whoami`; check `owner` in app.json.

❌ Mistake 3: Mixed SDK versions of packages.
✅ Correct: `npx expo install <pkg>` and `npx expo install --check`.

❌ Mistake 4: Storing `EXPO_TOKEN` in repo.
✅ Correct: GitHub Secrets / CI secret store.

---

## 🧠 Tricky Interview Question
"After `eas build:configure` you notice `eas.json` has `appVersionSource`. What does `remote` mean for `versionCode` in `app.json`?"

Answer: With `remote`, EAS stores the version code on its servers and increments it (with `autoIncrement`). The `android.versionCode` in `app.json` is ignored for builds (in that mode). With `local`, the values in your project files are used.

---

## ⚫ Interview Questions + Answers
Q1: Which command links the project to EAS?
A1: `eas init` (adds `extra.eas.projectId`).

Q2: What does `extends` do in eas.json?
A2: A profile inherits values from another profile.

Q3: How do I use env vars?
A3: `env` in a profile, EAS environment variables/secrets, read in `app.config.js` via `process.env`.

Q4: What is `expo-doctor`?
A4: A tool that checks project config and dependency compatibility.

Q5: How do I pin Node version?
A5: `"node": "20.x.x"` in the build profile.

---

## 🔷 When to Use + When Not to Use
✅ Use when: every project that builds through EAS.

❌ Avoid when: purely local Gradle builds.

---

## 📊 Visual Diagram
```
 expo.dev account ─► eas login ─► eas init ─► projectId in app.json
                                      │
                           eas build:configure ─► eas.json (profiles)
                                      │
                           eas build -p android --profile X ─► artifact
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| projectId | Link to EAS project | EAS project से link |
| Profile | Named build setup | नाम वाला build setup |
| EXPO_TOKEN | CI auth token | CI के लिए token |
| expo-doctor | Config checker | Config जाँचने वाला tool |

---

## ⚡ 3-Line Summary
English: Install eas-cli, login, `eas init`, `eas build:configure`.
Set package name and profiles; verify with expo-doctor.
Use EXPO_TOKEN for CI.

Hindi: eas-cli install करो, login करो, `eas init`, `eas build:configure`।
Package name और profiles set करो; expo-doctor से जाँचो।
CI के लिए EXPO_TOKEN इस्तेमाल करो।

---

## ➡️ Next Topic
**208. eas.json Configuration** — हर key का मतलब विस्तार से।
