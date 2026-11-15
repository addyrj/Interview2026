# 266. EAS Build in CI/CD
# हिंदी में: CI/CD में EAS Build चलाना
# Platform: Android ✅ | iOS ✅ | Both ✅
# Expo SDK 54 (React Native 0.81) — check current docs — APIs change between SDKs

---

## 🔵 Simple Definition (English)
**EAS Build** is Expo's cloud service that compiles your app into an `.aab/.apk` (Android) or `.ipa` (iOS). Running it inside **CI/CD** (GitHub Actions, GitLab CI, Bitbucket) means every merge to `main` automatically triggers a build — no developer laptop, no Xcode, no Android Studio needed.

## 🔵 सरल परिभाषा (Hindi)
**EAS Build** Expo की cloud service है जो आपके app को `.aab/.apk` (Android) या `.ipa` (iOS) में compile करती है। इसे **CI/CD** (GitHub Actions आदि) में चलाने का मतलब है कि हर `main` merge पर build अपने-आप शुरू हो — किसी developer के laptop, Xcode या Android Studio की ज़रूरत नहीं।

---

## 🔴 Problem it Solves
```
BEFORE (manual builds):
❌ "Works on my machine" — build only on one dev's Mac
❌ iOS build needs a Mac + Xcode + certificates on that Mac
❌ Keystore / .p12 files shared on WhatsApp or pen drives (security risk!)
❌ Release takes half a day: build → rename → upload → tell QA
❌ Different Node/Gradle versions = different build results
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले (manual build):
❌ Build सिर्फ एक developer के Mac पर होता था
❌ iOS build के लिए Mac + Xcode + certificates चाहिए
❌ Keystore / .p12 files WhatsApp पर share होती थीं (security risk)
❌ Release में आधा दिन: build → upload → QA को बताना
❌ अलग Node/Gradle version = अलग build result
EAS + CI: credentials cloud में safe, build हर बार same environment में।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Developer pushes / merges code to GitHub (main or tag v1.2.0)
Step 2 → GitHub Actions workflow starts on a Linux runner
Step 3 → Workflow installs Node + eas-cli (expo/expo-github-action)
         and authenticates using the EXPO_TOKEN secret
Step 4 → `eas build --profile production --platform all --non-interactive`
         uploads your project source to EAS servers
Step 5 → EAS builds on its own macOS (iOS) / Linux (Android) workers
         using credentials stored on EAS (keystore, certs, profiles)
Step 6 → Artifact (.aab / .ipa) is stored on EAS; link posted in logs
Step 7 → Optional: --auto-submit sends it to Play Store / TestFlight
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Developer code GitHub पर push/merge करता है
Step 2 → GitHub Actions workflow Linux runner पर शुरू होता है
Step 3 → Node + eas-cli install होता है, EXPO_TOKEN secret से login
Step 4 → `eas build --non-interactive` source को EAS servers पर भेजता है
Step 5 → EAS अपने workers पर build करता है (credentials EAS में सुरक्षित)
Step 6 → .aab / .ipa EAS पर store होता है, link logs में मिलता है
Step 7 → चाहो तो --auto-submit से सीधे Play Store / TestFlight भेजो
```

---

## 🟡 Real World Example
A team like **Swiggy** or **Zomato** merges 30+ PRs a day. A tag like `v5.4.0` triggers CI: it builds a production AAB and IPA, uploads them to Play Console internal track and TestFlight, and posts the build link on Slack for QA. Nobody on the team needs the release keystore on their laptop.

## 🟡 Real Example Hindi mein
**Swiggy/Zomato** जैसी team रोज़ 30+ PR merge करती है। `v5.4.0` tag लगते ही CI production AAB और IPA बनाता है, Play Console internal track और TestFlight पर भेजता है और Slack पर QA को link भेज देता है। किसी के laptop में release keystore नहीं होती।

---

## 💻 Code Example — Basic

`eas.json` (project root) — defines build profiles:
```json
{
  "cli": {
    "version": ">= 12.0.0",
    "appVersionSource": "remote"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
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

Basic GitHub Actions workflow `.github/workflows/eas-build.yml`:
```yaml
# Name shown in the GitHub Actions tab
name: EAS Build
# Trigger: every push to main
on:
  push:
    branches: [main]
jobs:
  build:
    # Cheap Linux runner — actual build happens on EAS servers
    runs-on: ubuntu-latest
    steps:
      # 1. Get the code
      - uses: actions/checkout@v4
      # 2. Install Node
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      # 3. Install eas-cli and log in using the EXPO_TOKEN secret
      - uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      # 4. Install JS dependencies (exact versions from lockfile)
      - run: npm ci
      # 5. Start preview build for Android; --no-wait = do not block CI
      - run: eas build --platform android --profile preview --non-interactive --no-wait
```

## 💻 Code Example — Advanced

Production pipeline: tag-triggered, both platforms, tests first, auto-submit, Slack-friendly output.
```yaml
# Release pipeline — runs only when a version tag like v1.2.0 is pushed
name: Release
on:
  push:
    tags: ['v*.*.*']
# Prevent two release builds for the same ref at once
concurrency:
  group: release-${{ github.ref }}
  cancel-in-progress: false
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      # Fail fast: do not spend EAS build minutes on broken code
      - run: npm run lint
      - run: npm test -- --ci
  build:
    # Build only if tests passed
    needs: test
    runs-on: ubuntu-latest
    strategy:
      # Build Android and iOS in parallel jobs
      matrix:
        platform: [android, ios]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: npm ci
      # --auto-submit: after build finishes EAS Submit uploads to the store
      # --non-interactive: CI has no keyboard; fails instead of asking questions
      # --json: machine-readable output you can parse in later steps
      - name: Build and submit
        run: |
          eas build \
            --platform ${{ matrix.platform }} \
            --profile production \
            --non-interactive \
            --auto-submit
        env:
          # Runtime env visible to the build command (not the app bundle)
          EXPO_PUBLIC_API_URL: ${{ vars.PROD_API_URL }}
```
Notes: store credentials for non-interactive iOS builds beforehand with `eas credentials` (run once locally). For Android submit you need a Google Service Account key set in `eas.json` under `submit.production.android.serviceAccountKeyPath` or stored on EAS. These are not run here — verify against current EAS docs.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Output file | `.aab` (store) / `.apk` (testing) | `.ipa` |
| Credentials | Keystore (EAS can generate and store) | Distribution cert + provisioning profile (needs Apple Developer account, $99/yr) |
| First CI run | Works fully non-interactive after first keystore generation | Needs credentials set up once via `eas credentials` / interactive build |
| Store upload | Google Play service account JSON | App Store Connect API key |
| Build time | ~8-15 min | ~12-25 min (macOS worker, queue longer on free plan) |
| Internal testing | APK link / Play internal track | Ad-hoc (registered UDIDs) / TestFlight |

---

## 🟠 Expo vs CLI Difference
Expo way (managed / prebuild — EAS builds in cloud):
```bash
# Login token created once on expo.dev → Account → Access Tokens
eas build --platform all --profile production --non-interactive
```
CLI way (bare React Native — you manage native build yourself in CI):
```yaml
# Android build on GitHub runner with Gradle (free, but you manage keystore secrets)
- run: cd android && ./gradlew bundleRelease
# iOS needs a macOS runner (10x cost on GitHub minutes) + fastlane/xcodebuild
- run: xcodebuild -workspace ios/App.xcworkspace -scheme App archive
```
Note: a bare RN project can ALSO use EAS Build (it supports any RN project with an `eas.json`). So "CLI app" does not mean "cannot use EAS".

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Forgetting `--non-interactive` in CI
✅ **Correct:** CI has no terminal, so prompts hang until timeout. Always pass `--non-interactive`.

❌ **Mistake 2:** Committing `EXPO_TOKEN` or keystore into the repo
✅ **Correct:** Put token in GitHub → Settings → Secrets → Actions. Let EAS hold the keystore.

❌ **Mistake 3:** Waiting for the build in CI and burning runner minutes
✅ **Correct:** Use `--no-wait` for non-release builds, or use the EAS Workflows / webhooks to notify on completion.

❌ **Mistake 4:** `appVersionSource: local` with `autoIncrement` in CI — version numbers reset each run
✅ **Correct:** Use `"appVersionSource": "remote"` so EAS keeps the build number counter.

---

## 🧠 Tricky Interview Question
**Q:** Your CI job shows green in 40 seconds, but QA says "no new build available". Why?

**Answer:** You probably used `--no-wait`. The GitHub job only *queues* the build on EAS and exits; the real build runs later on EAS servers and may even fail there. A green CI tick means "request submitted", not "build succeeded". Fix: remove `--no-wait` for release pipelines, or add a webhook/notification on EAS build completion.

---

## ⚫ Interview Questions + Answers

**Q1: Why use EAS Build instead of building on GitHub runners?**
A1: No macOS runner cost, managed credentials, consistent environments, build caching, and iOS builds without owning a Mac.

**Q2: How does CI authenticate with EAS?**
A2: With a personal/robot access token stored as the `EXPO_TOKEN` secret; `expo-github-action` exposes it to `eas-cli`.

**Q3: What do build profiles in eas.json do?**
A3: They define variants (development, preview, production) — distribution type, build type (apk vs aab), env vars, channel, auto-increment.

**Q4: How do you build only when native code changes, and use OTA otherwise?**
A4: Use a fingerprint check (`@expo/fingerprint`) in CI; if the fingerprint is unchanged publish `eas update`, otherwise run `eas build`. Check current EAS Workflows docs for the built-in fingerprint/repack features.

**Q5: How do you auto-increment versions?**
A5: `"autoIncrement": true` in the profile with `appVersionSource: remote` — EAS bumps Android `versionCode` and iOS `buildNumber`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Team has no Mac for every dev, or iOS builds are needed on Linux CI
- You want repeatable, auditable release builds
- You want credentials managed centrally

❌ Avoid when:
- Strict policy forbids uploading source to third-party cloud (use self-hosted build with Gradle/Xcode)
- Free-tier queue time is unacceptable and you cannot pay for priority

---

## 📊 Visual Diagram
```
 Developer ──push tag──► GitHub ──► Actions runner (Linux)
                                        │ eas build (token)
                                        ▼
                                 ┌───────────────┐
                                 │  EAS Servers  │  credentials stored here
                                 │ Android│ macOS│
                                 └──────┬────────┘
                       .aab ────────────┼──────────── .ipa
                         ▼                              ▼
                   Play Console                   TestFlight
                   (internal track)               (App Store Connect)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CI/CD | Automatic build/test/release pipeline | Automatic build-test-release pipeline |
| EXPO_TOKEN | Secret used to log in eas-cli in CI | CI में login के लिए secret token |
| Build profile | Named config in eas.json | eas.json में नाम वाला config |
| --non-interactive | No prompts mode | बिना सवाल पूछे चलने वाला mode |
| AAB | Android App Bundle for Play Store | Play Store के लिए Android bundle |
| autoIncrement | Auto bump build number | Build number अपने-आप बढ़ाना |

---

## ⚡ 3-Line Summary
**English:**
1. EAS Build compiles your app in Expo's cloud; CI just triggers it with `eas build --non-interactive`.
2. Authenticate with `EXPO_TOKEN`, define variants in `eas.json`, optionally `--auto-submit` to stores.
3. Green CI with `--no-wait` only means "queued" — not "built".

**Hindi:**
1. EAS Build app को Expo cloud में compile करता है; CI सिर्फ `eas build --non-interactive` चलाता है।
2. `EXPO_TOKEN` से login, `eas.json` में profiles, चाहो तो `--auto-submit` से store पर भेजो।
3. `--no-wait` के साथ CI green का मतलब सिर्फ "queue हुआ" है — "build हो गया" नहीं।

---

## ➡️ Next Topic
**267. Fastlane for React Native** — EAS के बिना या साथ में, build/sign/upload को scripts से automate करना।
