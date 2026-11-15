# 264. CI/CD for React Native
# हिंदी में: React Native के लिए CI/CD
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52+ examples (check current docs — APIs change between SDKs). Tool names/prices (EAS Workflows, Bitrise, Codemagic, GitHub Actions) change often; verify on their docs.

---

## 🔵 Simple Definition (English)
CI (Continuous Integration) automatically installs, lints, type-checks and tests your code on every push/PR. CD (Continuous Delivery/Deployment) automatically builds the app and ships it to testers, stores, or as an OTA update.

## 🔵 सरल परिभाषा (Hindi)
CI (Continuous Integration) हर push/PR पर अपने-आप code install, lint, type-check और test करता है। CD (Continuous Delivery/Deployment) अपने-आप app build करके testers, stores या OTA update के रूप में भेजता है।

---

## 🔴 Problem it Solves
```
MANUAL RELEASES:
  "Works on my machine", forgotten tests, wrong env vars, one person holds certificates,
  Friday-night manual builds.
CI/CD:
  Same steps every time, tests gate merges, secrets stored safely, one-click release.
```

## 🔴 यह क्यों बना? (Hindi)
Manual release में गलतियाँ होती हैं: test भूल गए, गलत environment, certificates सिर्फ एक आदमी के पास। CI/CD हर बार एक जैसी प्रक्रिया चलाता है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → Developer opens PR
Step 2 → CI: checkout -> install (npm ci) -> lint -> tsc -> jest
Step 3 → PR needs green checks + review -> merge to main
Step 4 → CD on main: expo-doctor, then
           (a) JS-only: eas update --branch staging
           (b) native: eas build --profile preview (internal testers)
Step 5 → Tag release (v2.5.0): eas build --profile production --auto-submit
Step 6 → Store review + phased rollout; OTA hotfixes via production channel
Step 7 → Notify team (Slack) with build links
```

### Pipeline stages
| Stage | Tools | Fails when |
|-------|-------|-----------|
| Lint | ESLint | style/bug patterns |
| Types | `tsc --noEmit` | type errors |
| Unit tests | Jest + React Native Testing Library | logic breaks |
| Health | `npx expo-doctor` | dependency mismatches |
| E2E (optional) | Maestro / Detox | flows break |
| Build | EAS Build / Fastlane + Gradle/Xcode | native build errors |
| Deliver | EAS Submit / Fastlane / OTA | credentials, review |

### CI/CD options
| Option | Notes |
|--------|-------|
| GitHub Actions + EAS | Most common for Expo; builds run on Expo's cloud |
| EAS Workflows | Expo's own YAML pipelines (check current docs) |
| Bitrise / Codemagic | Mobile-focused CI with macOS machines |
| Fastlane | Scripted signing, build, upload (bare RN) |
| Jenkins/GitLab | Self-managed; needs macOS agent for iOS |

## 🟢 कैसे काम करता है? (Hindi)
1. PR खुलता है।
2. CI: install -> lint -> type-check -> test।
3. सब green हो और review मिले तो merge।
4. main पर: JS-only हो तो `eas update`, native बदला हो तो `eas build`।
5. Release tag पर production build + store submit।
6. Review और phased rollout; hotfix OTA से।
7. Slack में build link भेजो।

---

## 🟡 Real World Example
Swiggy/Zomato जैसी बड़ी टीमों में हर PR पर test और lint चलता है, हर merge पर internal "nightly" build testers को जाता है, और release branch से store builds निकलते हैं। छोटे startups EAS + GitHub Actions से यही काम कम setup में करते हैं।

## 🟡 Real Example Hindi mein
बड़ी टीमों में हर PR पर tests चलते हैं और हर merge पर testers को नया build मिलता है। Startup EAS + GitHub Actions से यही सस्ते में कर लेते हैं।

---

## 💻 Code Example — Basic (package.json scripts used by CI)
```json
{
  "scripts": {
    "lint": "eslint . --ext .js,.jsx,.ts,.tsx",
    "typecheck": "tsc --noEmit",
    "test": "jest --ci --coverage",
    "doctor": "npx expo-doctor",
    "ci": "npm run lint && npm run typecheck && npm test"
  }
}
```
```bash
npm ci            # clean, lockfile-exact install (use in CI instead of npm install)
npm run ci        # one command the pipeline calls
```

## 💻 Code Example — Advanced (Fastlane lane for bare RN iOS to TestFlight)
```ruby
# ios/fastlane/Fastfile - bare React Native iOS lane (Mac runner required)
default_platform(:ios)                                   # this file is for iOS

platform :ios do                                         # iOS lanes
  desc "Build and upload to TestFlight"                  # description shown in `fastlane lanes`
  lane :beta do                                          # lane name
    setup_ci                                             # create temp keychain on CI machines
    match(type: "appstore", readonly: true)              # fetch signing certs from private repo (fastlane match)
    increment_build_number(                              # unique build number
      build_number: ENV["GITHUB_RUN_NUMBER"]             # use CI run number
    )
    build_app(                                           # archive the app
      workspace: "MyApp.xcworkspace",                    # your workspace
      scheme: "MyApp"                                    # your scheme
    )
    upload_to_testflight(                                # upload IPA
      api_key_path: "fastlane/asc_key.json",             # App Store Connect API key JSON
      skip_waiting_for_build_processing: true            # do not block CI
    )
  end
end
```
Neither block was run (needs Mac + signing credentials). Action names (`setup_ci`, `match`, `build_app`, `upload_to_testflight`) are standard Fastlane actions.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Runner OS | Linux/Mac/Windows | macOS required for local builds (EAS handles it) |
| Signing | Keystore (upload key) | Certificates + provisioning profiles |
| Upload target | Play Console (service account JSON) | App Store Connect (API key) |
| Build time | Often faster | Often slower, queue for Macs |
| Secrets | keystore + passwords | .p8 key, certs |
| Beta channel | Internal testing track | TestFlight |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
eas build --platform all --profile production --non-interactive   # cloud build in CI
eas update --branch production --message "$GITHUB_SHA" --non-interactive
```
CLI way:
```bash
cd android && ./gradlew bundleRelease          # Android AAB on Linux runner
fastlane ios beta                              # iOS lane on macOS runner
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Committing keystores / .env / API keys.
✅ Correct: Use CI secrets; EAS stores credentials.

❌ Mistake 2: `npm install` in CI.
✅ Correct: `npm ci` for reproducible installs.

❌ Mistake 3: Building for every commit (cost and queue).
✅ Correct: Test on PRs; build only on main/tags; use path filters.

❌ Mistake 4: No caching.
✅ Correct: Cache node_modules/Gradle/CocoaPods.

---

## 🧠 Tricky Interview Question
CI passes, but the production app crashes on launch from your release build. Why might CI not catch it?

Answer: Unit tests run in Node/Jest, not on a real device with Hermes, ProGuard/R8 or release-only code paths. Missing env vars, minification or native config problems appear only in a release build. Add a smoke test: build a preview/release binary and run an E2E (Maestro/Detox) flow on an emulator/simulator.

---

## ⚫ Interview Questions + Answers
Q1: CI vs CD?
A1: CI validates code; CD builds and delivers it.

Q2: Why `npm ci`?
A2: Uses the lockfile exactly and is faster/cleaner for CI.

Q3: How do you handle iOS signing in CI?
A3: EAS manages it, or Fastlane match with a secure repo.

Q4: Where do secrets live?
A4: CI secret store (GitHub Secrets) and EAS secrets; never in git.

Q5: What gate before merge?
A5: Lint, types, tests, review.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Team of 2+, regular releases, multiple environments

❌ Avoid over-engineering when:
- One-person prototype; manual EAS commands are enough

---

## 📊 Visual Diagram
```
 PR --> [lint][types][test] --> merge --> main
                                         |
                  JS-only? --yes--> eas update (staging)
                         --no---> eas build (preview) --> testers
                                         |
                              tag --> eas build prod --> eas submit --> stores
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CI | Auto test on commit | लगातार integration |
| CD | Auto deliver build | लगातार delivery |
| Pipeline | Ordered automated steps | स्वचालित steps |
| Lane | Fastlane workflow | Fastlane प्रक्रिया |
| Artifact | Build output | Build की फाइल |

---

## ⚡ 3-Line Summary
English: CI checks every change; CD builds and ships it.
Use `npm ci`, secrets, caching and environments.
Expo teams often use GitHub Actions + EAS.

Hindi: CI हर बदलाव जाँचता है; CD उसे build करके भेजता है।
`npm ci`, secrets, caching और environments इस्तेमाल करो।
Expo टीमें अक्सर GitHub Actions + EAS लेती हैं।

---

## ➡️ Next Topic
**265. GitHub Actions for RN Build** — एक पूरा working workflow।
