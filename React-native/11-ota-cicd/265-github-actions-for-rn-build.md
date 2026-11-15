# 265. GitHub Actions for RN Build
# हिंदी में: React Native Build के लिए GitHub Actions
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52+ examples (check current docs — APIs change between SDKs). Action versions (`actions/checkout@v4`, `actions/setup-node@v4`, `expo/expo-github-action@v8`) were current when written; check the marketplace pages for newer majors. YAML here was not run on GitHub.

---

## 🔵 Simple Definition (English)
GitHub Actions runs workflows defined in `.github/workflows/*.yml` when events happen (push, PR, tag, manual). For React Native/Expo, a workflow installs dependencies, runs tests, and triggers EAS Build/Update or Gradle/Xcode builds.

## 🔵 सरल परिभाषा (Hindi)
GitHub Actions `.github/workflows/*.yml` में लिखे workflows चलाता है जब कोई event होता है (push, PR, tag, manual)। React Native/Expo में workflow dependencies install करता है, tests चलाता है और EAS Build/Update या Gradle/Xcode build trigger करता है।

---

## 🔴 Problem it Solves
```
PROBLEM: Builds and OTA pushes depend on someone's laptop.
SOLUTION: Workflow in the repo, secrets in GitHub, runs for everyone the same way.
```

## 🔴 यह क्यों बना? (Hindi)
Build किसी के laptop पर निर्भर न रहे - workflow repo में रहता है, secrets GitHub में, और सबके लिए एक जैसा चलता है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → Create Expo access token: expo.dev -> Account Settings -> Access Tokens -> Create
Step 2 → GitHub repo -> Settings -> Secrets and variables -> Actions -> New repository secret: EXPO_TOKEN
Step 3 → Add .github/workflows/ci.yml (tests on PR)
Step 4 → Add .github/workflows/update.yml (OTA on push to main)
Step 5 → Add .github/workflows/build.yml (EAS build on tag v*)
Step 6 → Push -> Actions tab shows runs, logs, and green/red status
Step 7 → Branch protection: require "CI" check before merge
```

### Console screens (in words)
- **expo.dev -> avatar menu -> Account settings -> Access tokens**: a "Create Token" button, a name box, then a one-time visible token string; copy it immediately.
- **GitHub repo -> Settings -> Secrets and variables -> Actions**: tab "Secrets", green "New repository secret" button, fields Name and Secret.
- **GitHub repo -> Actions tab**: left list of workflows, right list of runs with coloured status icons; clicking a run shows job graph and expandable step logs.

## 🟢 कैसे काम करता है? (Hindi)
1. expo.dev पर Access Token बनाओ।
2. GitHub में `EXPO_TOKEN` नाम से repository secret जोड़ो।
3. PR पर चलने वाला `ci.yml` बनाओ।
4. main पर OTA के लिए `update.yml` बनाओ।
5. tag `v*` पर EAS build के लिए `build.yml` बनाओ।
6. Actions tab में logs देखो।
7. Branch protection में CI check ज़रूरी करो।

---

## 🟡 Real World Example
Zomato-जैसी टीम में PR पर lint+test, main merge पर staging channel पर OTA, और `v3.2.0` tag पर Android+iOS production build चलता है; build पूरा होते ही Slack में link आता है। छोटी टीमें इसी pattern को Expo + GitHub Actions से 30 मिनट में बना लेती हैं।

## 🟡 Real Example Hindi mein
PR पर tests, main पर staging OTA, और version tag पर production build - यह आम pattern है। Build ख़त्म होने पर Slack में link आ जाता है।

---

## 💻 Code Example — Basic (CI on pull requests)
```yaml
# .github/workflows/ci.yml
name: CI                                   # name shown in Actions tab
on:                                        # events that trigger this workflow
  pull_request:                            # run on every PR
    branches: [main]                       # targeting main
jobs:
  test:                                    # job id
    runs-on: ubuntu-latest                 # Linux runner (cheap, enough for JS tests)
    steps:
      - uses: actions/checkout@v4          # get the code
      - uses: actions/setup-node@v4        # install Node
        with:
          node-version: 20                 # Node version
          cache: npm                       # cache npm downloads
      - run: npm ci                        # clean install from lockfile
      - run: npm run lint                  # ESLint
      - run: npx tsc --noEmit              # type-check (remove if no TypeScript)
      - run: npm test -- --ci              # Jest tests
      - run: npx expo-doctor               # check dependency/config health
```

## 💻 Code Example — Advanced (OTA on main + EAS build on tag)
```yaml
# .github/workflows/update.yml - publish OTA to staging when main changes
name: OTA Staging
on:
  push:
    branches: [main]                       # every merge to main
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - uses: expo/expo-github-action@v8   # installs expo + eas CLI and authenticates
        with:
          eas-version: latest              # use latest EAS CLI
          token: ${{ secrets.EXPO_TOKEN }} # secret created in step 2
      - run: npm ci
      - run: eas update --branch staging --message "${{ github.sha }}" --non-interactive  # publish OTA
```
```yaml
# .github/workflows/build.yml - production builds when a version tag is pushed
name: EAS Build
on:
  push:
    tags: ['v*']                           # e.g. v2.5.0
jobs:
  build:
    runs-on: ubuntu-latest                 # EAS builds on Expo's cloud; runner only triggers
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: npm ci
      - run: eas build --platform all --profile production --non-interactive --no-wait  # queue build, do not wait
```
Add `--auto-submit` to also submit to the stores (needs store credentials set up in EAS). Also available: `workflow_dispatch:` for manual runs.

```yaml
# Bare React Native Android build on GitHub runner (no EAS)
# jobs.android.steps:
#   - uses: actions/setup-java@v4
#     with: { distribution: temurin, java-version: 17 }
#   - run: npm ci
#   - run: cd android && ./gradlew bundleRelease
#   - uses: actions/upload-artifact@v4
#     with: { name: app-release, path: android/app/build/outputs/bundle/release/*.aab }
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Runner for local build | ubuntu-latest | macos-latest (more expensive minutes) |
| Signing in CI | Base64 keystore secret + passwords | Certs/profiles via match or EAS |
| Artifact | .aab/.apk | .ipa |
| Upload action | r0adkll/upload-google-play or EAS Submit | Fastlane / EAS Submit |
| Build duration | Shorter | Longer |
| Debug on CI | Emulator (reactivecircus/android-emulator-runner) | Simulator on macOS runner |

---

## 🟠 Expo vs CLI Difference
Expo way:
```yaml
- run: eas build -p all --profile production --non-interactive --no-wait   # runner just calls EAS
```
CLI way:
```yaml
- run: cd android && ./gradlew bundleRelease        # runner compiles itself (ubuntu)
- run: cd ios && pod install && xcodebuild -workspace MyApp.xcworkspace -scheme MyApp -configuration Release archive   # macos runner
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Printing secrets or putting them in YAML.
✅ Correct: Use `${{ secrets.NAME }}`; GitHub masks them in logs.

❌ Mistake 2: Forgetting `--non-interactive`.
✅ Correct: CI cannot answer prompts; the job would hang or fail.

❌ Mistake 3: Using `macos-latest` for everything.
✅ Correct: Use ubuntu for tests/EAS triggers; macOS only when you must compile iOS yourself.

❌ Mistake 4: Floating action versions (`@main`).
✅ Correct: Pin major versions (`@v4`) or commit SHAs.

---

## 🧠 Tricky Interview Question
Your workflow runs `eas build ...` without `--no-wait`. It succeeds in 25 minutes but you are billed 25 GitHub runner minutes. How to avoid?

Answer: Add `--no-wait` so the runner only queues the build on EAS and exits in seconds. The build then runs on Expo's infrastructure (billed under your EAS plan). Poll status or use webhooks/EAS notifications for the result.

---

## ⚫ Interview Questions + Answers
Q1: Where is the workflow file?
A1: `.github/workflows/<name>.yml`.

Q2: What does expo-github-action do?
A2: Installs Node tooling (expo/eas CLI) and authenticates using your token.

Q3: How do you trigger on tags?
A3: `on: push: tags: ['v*']`.

Q4: How to run manually?
A4: Add `workflow_dispatch:` under `on:`.

Q5: Cache dependencies how?
A5: `actions/setup-node` with `cache: npm`, or `actions/cache`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Repo is on GitHub; you want PR checks and automated EAS builds/OTA

❌ Avoid when:
- You need heavy macOS builds daily and cost matters (consider EAS Build, Codemagic, Bitrise)

---

## 📊 Visual Diagram
```
 push / PR / tag
      |
 GitHub runner: checkout -> setup-node -> npm ci -> tests
      |                                  |
      |                    expo-github-action (EXPO_TOKEN)
      |                                  |
      +--> eas update (OTA)   or   eas build --no-wait --> Expo cloud --> artifacts/stores
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Workflow | YAML pipeline file | Pipeline फाइल |
| Runner | Machine running jobs | Job चलाने वाली मशीन |
| Secret | Hidden credential | छुपी key |
| Artifact | Saved build output | सहेजी फाइल |
| workflow_dispatch | Manual trigger | हाथ से चलाना |

---

## ⚡ 3-Line Summary
English: GitHub Actions runs YAML workflows on push, PR or tag.
For Expo: set `EXPO_TOKEN`, use expo-github-action, call eas update/build with `--non-interactive`.
Use ubuntu for most jobs; macOS only for local iOS builds.

Hindi: GitHub Actions push, PR या tag पर YAML workflows चलाता है।
Expo में `EXPO_TOKEN` रखो, expo-github-action लो और `--non-interactive` से eas चलाओ।
ज़्यादातर jobs ubuntu पर; macOS सिर्फ local iOS build के लिए।

---

## ➡️ Next Topic
**266 onward** — अगले section की शुरुआत; यहाँ तक publishing और OTA/CI-CD पूरा।
