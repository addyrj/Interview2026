# 206. EAS Build — Expo Application Services
# हिंदी में: EAS Build — Expo की Cloud Build Service
# Platform: Android ✅ | iOS ✅ (Both)

> Target: **Expo SDK 52 (React Native 0.76)** with `eas-cli` — check current docs — EAS plans, limits and CLI flags change over time.

---

## 🔵 Simple Definition (English)
**EAS (Expo Application Services)** is a paid/free cloud platform by Expo. **EAS Build** compiles your React Native app into APK/AAB/IPA on Expo's servers, so you do not need Android Studio or a Mac. Other EAS services: Submit, Update (OTA), Credentials.

## 🔵 सरल परिभाषा (Hindi)
**EAS (Expo Application Services)** Expo की cloud platform है (free + paid plans)। **EAS Build** आपके React Native app को Expo के servers पर APK/AAB/IPA में बदलता है, इसलिए Android Studio या Mac की ज़रूरत नहीं। दूसरी services: Submit, Update (OTA), Credentials।

---

## 🔴 Problem it Solves
- Building iOS needs a Mac + Xcode; Android needs SDK, JDK, Gradle setup — "works on my machine" problems.
- Managing keystores/certificates manually is error-prone.
- Teams need reproducible builds and CI.

## 🔴 यह क्यों बना? (Hindi)
- iOS के लिए Mac + Xcode और Android के लिए SDK/JDK/Gradle setup चाहिए — "मेरी machine पर चलता है" वाली दिक्कतें।
- Keystore/certificates हाथ से संभालना जोखिम भरा है।
- Teams को reproducible builds और CI चाहिए।

---

## 🟢 How it Works — Step by Step
```
Step 1 → eas build → CLI zips your project (respects .gitignore / .easignore)
Step 2 → Uploads to EAS servers; build job enters a queue (free tier waits longer)
Step 3 → EAS spins up a clean VM (Linux for Android, macOS for iOS)
Step 4 → npm/yarn install, expo prebuild (if managed), Gradle/Xcode build
Step 5 → Signs with credentials stored on EAS (keystore / certs)
Step 6 → Uploads artifact (.apk/.aab/.ipa) to EAS storage
Step 7 → You get a URL/QR; optionally --auto-submit to the stores
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → eas build → CLI आपके project को zip करता है
Step 2 → EAS servers पर upload होकर queue में जाता है
Step 3 → साफ़ VM चालू होती है (Android: Linux, iOS: macOS)
Step 4 → dependencies install, prebuild, Gradle/Xcode build
Step 5 → EAS पर रखी credentials से sign होता है
Step 6 → Artifact EAS storage में upload होता है
Step 7 → URL/QR मिलता है; चाहो तो --auto-submit
```

**Console screens (described):** At `expo.dev` → your project → **Builds** tab: a table of builds with columns Platform (Android/Apple icon), Profile, Status chip (green Finished / blue In progress / red Errored), version, commit message and time. Clicking one opens details with **Logs** (collapsible phases) and download/install buttons.

---

## 🟡 Real World Example
A 5-member team building a Zomato-like app: the Windows developers trigger iOS builds without owning a Mac. GitHub Actions calls `eas build --non-interactive` on every release tag.

## 🟡 Real Example Hindi mein
Zomato जैसा app बना रही 5 लोगों की team: Windows वाले developers बिना Mac के iOS build चलाते हैं। हर release tag पर GitHub Actions `eas build --non-interactive` चलाता है।

---

## 💻 Code Example — Basic
```bash
# Install and login
npm install -g eas-cli          # install CLI globally
eas login                       # login to expo.dev account
eas whoami                      # confirm login
# Build for both platforms using production profile
eas build --platform all --profile production
```

## 💻 Code Example — Advanced
GitHub Actions workflow for CI (not run here; syntax only):
```yaml
name: EAS Build
on:
  push:
    tags: ['v*']                         # run on version tags
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4        # get code
      - uses: actions/setup-node@v4      # install Node
        with:
          node-version: 20
          cache: npm
      - uses: expo/expo-github-action@v8 # installs eas-cli and authenticates
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}   # personal/robot access token
      - run: npm ci                      # install dependencies
      - run: eas build --platform android --profile production --non-interactive --no-wait
```
Query and manage builds from CLI:
```bash
eas build:list --platform android --status finished --limit 3   # recent builds
eas build:view <BUILD_ID>                                       # details of one build
eas build:cancel                                                # cancel in-progress build
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Build VM | Linux | macOS |
| Credentials | Keystore (auto-generated) | Apple account login, certs, profiles |
| Account needed | Google Play ($25) only to publish | Apple Developer ($99/yr) required to build for devices |
| Typical time | ~5-15 min (+ queue) | ~10-20 min (+ queue) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
eas build -p android --profile production   # cloud
```
CLI way:
```bash
cd android && ./gradlew bundleRelease       # your own machine
```
> EAS Build also works for bare React Native projects (needs `eas.json`; no Expo SDK required to build).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Not committing/ignoring files properly → huge upload or missing files.
✅ Correct: Maintain `.gitignore` / `.easignore`; keep `node_modules` out.

❌ Mistake 2: Putting secrets in `eas.json` `env`, which is committed.
✅ Correct: `eas secret:create` / EAS environment variables on expo.dev.

❌ Mistake 3: Running interactive build in CI.
✅ Correct: `--non-interactive` + `EXPO_TOKEN`.

❌ Mistake 4: Assuming free tier builds are instant.
✅ Correct: Queue times vary; check plan details on expo.dev.

---

## 🧠 Tricky Interview Question
"Build passes locally with `npx expo run:android` but fails on EAS with a dependency error. Why?"

Answer: EAS builds from a clean environment with your lockfile. Local node_modules may hide missing/mismatched deps (e.g. peer deps, wrong SDK version). Fix by `npx expo install --check`, `npx expo-doctor`, and committing the lockfile.

---

## ⚫ Interview Questions + Answers
Q1: What is EAS?
A1: Expo's cloud services: Build, Submit, Update, Metadata, Credentials.

Q2: Can EAS build non-Expo projects?
A2: Yes, bare React Native projects work with `eas build`.

Q3: What is a development build?
A3: A custom dev client (`developmentClient: true`) with your native modules; replaces Expo Go.

Q4: How is the build authenticated in CI?
A4: `EXPO_TOKEN` environment variable.

Q5: EAS Build vs EAS Update?
A5: Build makes a new binary; Update ships JS/asset changes OTA without store review.

---

## 🔷 When to Use + When Not to Use
✅ Use when: no Mac, small team, want managed credentials, CI.

❌ Avoid when: strict policy against third-party builds, or free-tier queue is too slow (use `--local`).

---

## 📊 Visual Diagram
```
 Laptop ── eas build ──► EAS Queue ──► Build VM (Android: Linux | iOS: macOS)
                                           │ install → prebuild → compile → sign
                                           ▼
                              Artifact storage (.apk/.aab/.ipa)
                                  │                    │
                            Download/QR          eas submit → Play / App Store
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| EAS | Expo Application Services | Expo की cloud services |
| Profile | Build config in eas.json | eas.json का config |
| Credentials | Keystore/certs | Keystore/certificates |
| Dev client | Custom dev app | Custom development app |
| Queue | Waiting list for builds | Build की प्रतीक्षा सूची |

---

## ⚡ 3-Line Summary
English: EAS Build compiles your app in the cloud and manages credentials.
Configure with eas.json, run `eas build`.
Works for Android and iOS, even without a Mac.

Hindi: EAS Build आपका app cloud में compile करता है और credentials संभालता है।
eas.json से configure करो, `eas build` चलाओ।
Android और iOS दोनों के लिए, बिना Mac के भी।

---

## ➡️ Next Topic
**207. EAS Build Setup + Configuration** — पहली बार setup step by step।
