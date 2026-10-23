# M19. Mobile CI/CD (EAS Build, Fastlane, GitHub Actions)
# हिंदी में: Mobile CI/CD — हर code बदलाव पर अपने-आप जाँच (lint, tests), iOS/Android ऐप बनाना और sign करना, E2E tests चलाना, testers तक पहुँचाना और store पर भेजना — EAS Build, Fastlane और GitHub Actions से

---

## 🔵 Simple Definition (English)
**Mobile CI/CD** automates the path from a commit to users' phones:
- **CI (Continuous Integration)**: on every PR, run type-checks, lint, unit and component tests (Jest + React Native Testing Library), and optionally build and run **E2E tests** (Detox, **Maestro**) on emulators/simulators or device farms.
- **CD (Continuous Delivery)**:
  - **build** release binaries (`.aab` for Play, `.ipa` for App Store)
  - **code-sign** them (Android keystore / Play App Signing; iOS certificates + provisioning profiles)
  - **distribute** to testers (TestFlight, Play internal track, Firebase App Distribution, EAS internal distribution)
  - **submit** to stores with staged rollout (M18)
  - publish **OTA updates** for JS-only changes (M17)
Tools:
- **EAS Build/Submit/Update** (Expo's cloud build service with managed credentials)
- **Fastlane** (Ruby automation for builds, signing with `match`, screenshots, uploads via `supply`, `deliver` and `pilot`)
- **GitHub Actions** (workflow orchestration; macOS runners for iOS)
- Gradle/Xcode build caches; device farms (Firebase Test Lab, BrowserStack, AWS Device Farm)

## 🔵 सरल परिभाषा (Hindi)
Mobile CI/CD = commit से यूज़र के फ़ोन तक का रास्ता अपने-आप: CI — हर PR पर type-check, lint, unit/component tests, और ज़रूरत हो तो build बनाकर E2E tests (Detox, Maestro) emulator या device farm पर; CD — release binary बनाना (.aab, .ipa), sign करना (Android keystore, iOS certificates/profiles), testers को देना (TestFlight, Play internal, Firebase App Distribution), store पर staged rollout के साथ भेजना, और JS-only बदलाव के लिए OTA।
Tools: EAS Build/Submit/Update, Fastlane, GitHub Actions, device farms।

---

## 🔴 Problem it Solves
Manual mobile releases are slow and error-prone:
- "It builds on my Mac": different Xcode/CocoaPods/Gradle versions, so builds aren't reproducible.
- **Code signing hell**: expired certificates, missing provisioning profiles, a lost Android keystore (you can't update your app without it, though Play App Signing mitigates this).
- Releases depend on one engineer's laptop and a 2-hour checklist, so mistakes like a wrong environment (staging API in production) or a forgotten version bump happen.
- Regressions slip through without automated tests on real device configurations.
- QA waits for builds and PMs can't try features before merge.
CI/CD gives **reproducible builds, safe credential handling, fast feedback, preview builds per PR and push-button releases**.

## 🔴 यह क्यों बना? (Hindi)
हाथ से release धीमी और ग़लतियों भरी: "मेरे Mac पर बनता है" (Xcode/Pods/Gradle के अलग versions); signing की मुसीबत (certificate ख़त्म, profile ग़ायब, Android keystore खो जाना); एक engineer के laptop और 2 घंटे की checklist पर निर्भरता — production में staging API, version बढ़ाना भूलना; बिना automated tests के regressions; QA और PM builds का इंतज़ार करें।
CI/CD = एक जैसे builds, credentials सुरक्षित, जल्दी feedback, हर PR का preview build, और एक बटन से release।

---

## 🟢 How it Works — Step by Step

### Pipeline overview

```
PR opened ──► CI (GitHub Actions, Linux runner, ~5–10 min)
              ├─ install (cached node_modules)  ├─ tsc --noEmit  ├─ eslint  ├─ jest (unit + RNTL)
              ├─ fingerprint check: native changed? → label "needs-native-build"
              └─ PREVIEW: JS-only → eas update --branch pr-123 (QR code comment for QA/PM on dev client)
                          native changed → eas build --profile preview (internal distribution)
Merge to main ──► nightly/beta builds → E2E (Maestro/Detox) on emulator + device farm subset
              ──► distribute to dogfood: TestFlight internal, Play internal track
Release branch / tag ──► production builds (EAS Build or Fastlane on macOS runner)
              ──► sign (managed credentials / fastlane match) ──► submit (eas submit / fastlane supply+deliver)
              ──► Play staged rollout 5% / iOS phased release ──► monitoring gates (M18)
JS hotfix ──► eas update --channel production --rollout-percentage 10 (M17)
```

### Code signing basics

```
Android:
  upload key (yours, in CI secrets) signs .aab → Google Play App Signing re-signs with app signing key
  (Google-held) → lost upload key can be reset via Play support; NEVER commit keystores
  Debug vs release keystores; SHA-256 of app signing cert needed for App Links & Google APIs
iOS:
  Apple Developer account → distribution certificate (private key!) + provisioning profile (app id,
  entitlements: push, associated domains, app groups) → signs .ipa
  Manage with EAS (stores credentials server-side) or fastlane match (encrypted git/S3 repo of certs)
  App Store Connect API key (.p8) for CI uploads (no 2FA prompts)
```

### Testing pyramid for RN

```
Many:  unit tests (pure logic: reducers, formatters ₹, date utils, sync engine) — Jest
Some:  component/integration (React Native Testing Library: render screen, fire press, assert) with
       MSW/mocked API
Few:   E2E on real builds: Maestro (YAML flows, easy) or Detox (gray-box, synchronizes with RN)
       critical flows only: login OTP (test number), search → add to cart → checkout (sandbox payment),
       deep link opens order
Device coverage: emulator per OS major version + device farm runs for top devices (Redmi, Samsung A-series,
       Realme, iPhone SE/13) nightly
Perf checks: Flashlight score / startup measurement on a reference Android device nightly (M03/M14)
```

### Speed & cost

```
- Linux runners for JS checks & Android builds; macOS runners (expensive) only for iOS builds
- Caches: npm/yarn, Gradle (~/.gradle), CocoaPods (Pods/), ccache; EAS has built-in caching
- Fingerprint-based skipping: no native change → no native build needed (use OTA/preview update)
- Parallelize jobs; run E2E nightly/merge rather than every PR for long suites
```

### Environments & secrets

```
Profiles: development (dev client), preview (internal QA, staging API), production (prod API)
Config via app.config.ts reading APP_ENV → API_URL, Sentry DSN, feature flag keys (public ones only)
Secrets: GitHub Actions secrets / EAS environment variables (marked secret) → never in repo
Public env vars embedded in the bundle (EXPO_PUBLIC_*) are visible to anyone → no secrets there (M15)
```

## 🟢 कैसे काम करता है? (Hindi)
1. हर PR पर CI: install (cache), TypeScript जाँच, ESLint, Jest tests; fingerprint से पता करो native बदला या नहीं — JS-only हो तो PR का OTA preview (QR code), native बदला हो तो preview build।
2. Main पर merge: nightly/beta builds, Maestro/Detox E2E emulator और device farm (Redmi, Samsung A, iPhone SE) पर, फिर TestFlight/Play internal पर कर्मचारियों के लिए।
3. Release: EAS Build या Fastlane से production build, managed credentials या fastlane match से signing, `eas submit` / fastlane से store, Play 5% staged / iOS phased, फिर monitoring gates।
4. Signing: Android upload key (CI secret) → Play App Signing; iOS distribution certificate + provisioning profile (push, associated domains) — EAS या match से; keystore/certificate कभी repo में नहीं।
5. तेज़ी और ख़र्च: JS jobs Linux पर, macOS सिर्फ़ iOS build के लिए; Gradle/Pods cache; native न बदले तो build skip; profiles (dev/preview/prod) और secrets GitHub/EAS में — EXPO_PUBLIC वाले मान सबको दिखते हैं।

---

## 🟡 Real World Example

**Uber (SubmitQueue)** — published research (2019) on its mobile monorepo merge system, SubmitQueue, which keeps the mainline green for thousands of daily changes by speculatively building and testing commits before landing. This shows CI at massive mobile scale.

**Fastlane** — created by Felix Krause (2014), later part of Fabric/Twitter and then Google, and now community-maintained. It became the standard for iOS/Android release automation, including `match` for team code signing and `supply`/`deliver` for store uploads.

**Expo EAS** — many RN teams (startups to large apps) use EAS Build for cloud iOS/Android builds without maintaining Macs, EAS Submit for store uploads, and per-PR preview updates for QA.

**Device farms** — Firebase Test Lab, BrowserStack and AWS Device Farm let Indian teams test on popular budget devices (Redmi, Realme, Samsung Galaxy A/M series) that dominate the market but are rare in engineers' hands.

## 🟡 Real Example Hindi में
Uber ने 2019 में SubmitQueue पर शोध छापा — mobile monorepo में रोज़ हज़ारों बदलाव पहले से build/test करके main को हमेशा ठीक रखना। Fastlane (Felix Krause, 2014) iOS/Android release automation का मानक बना — `match` से signing, `supply`/`deliver` से upload।
कई RN टीमें EAS Build से बिना Mac रखे cloud builds और हर PR का preview update बनाती हैं; Firebase Test Lab/BrowserStack से Redmi, Realme, Samsung A जैसे सस्ते फ़ोन पर testing, जो भारत में सबसे ज़्यादा चलते हैं।

---

## 🟠 My Stack Example

### CI on every PR (GitHub Actions): checks + fingerprint + preview
```yaml
# .github/workflows/mobile-ci.yml
name: mobile-ci
on: pull_request
jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npx tsc --noEmit
      - run: npx eslint . --max-warnings=0
      - run: npx jest --ci --coverage

  preview:
    needs: checks
    runs-on: ubuntu-latest
    permissions: { pull-requests: write }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - uses: expo/expo-github-action@v8
        with: { eas-version: latest, token: '${{ secrets.EXPO_TOKEN }}' }
      - name: Publish PR preview update (JS-only) and comment QR code
        uses: expo/expo-github-action/preview@v8
        with: { command: eas update --auto --branch pr-${{ github.event.number }} }
```

### Release builds + submit with EAS (tag-triggered)
```yaml
# .github/workflows/mobile-release.yml
name: mobile-release
on: { push: { tags: ['v*.*.*'] } }
jobs:
  build-submit:
    runs-on: ubuntu-latest                      # EAS builds in the cloud (macOS handled by EAS)
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - uses: expo/expo-github-action@v8
        with: { eas-version: latest, token: '${{ secrets.EXPO_TOKEN }}' }
      - run: eas build --platform all --profile production --non-interactive --auto-submit   # submit after build
```

### Fastlane alternative (bare RN, self-managed signing)
```ruby
# ios/fastlane/Fastfile
default_platform(:ios)
platform :ios do
  lane :beta do
    setup_ci
    app_store_connect_api_key(key_id: ENV["ASC_KEY_ID"], issuer_id: ENV["ASC_ISSUER_ID"], key_content: ENV["ASC_KEY_P8"])
    match(type: "appstore", readonly: true)                         # pull certs/profiles from encrypted repo
    increment_build_number(build_number: ENV["GITHUB_RUN_NUMBER"])
    build_app(scheme: "QuickBite", export_method: "app-store")
    upload_to_testflight(skip_waiting_for_build_processing: true)
  end
end

# android/fastlane/Fastfile
platform :android do
  lane :internal do
    gradle(task: "bundle", build_type: "Release", properties: {
      "android.injected.signing.store.file" => ENV["UPLOAD_KEYSTORE_PATH"],
      "android.injected.signing.store.password" => ENV["UPLOAD_KEYSTORE_PASSWORD"],
      "android.injected.signing.key.alias" => ENV["UPLOAD_KEY_ALIAS"],
      "android.injected.signing.key.password" => ENV["UPLOAD_KEY_PASSWORD"] })
    upload_to_play_store(track: "internal", aab: "app/build/outputs/bundle/release/app-release.aab")
  end
end
```

### E2E flow with Maestro (runs on emulator in CI nightly)
```yaml
# e2e/checkout.yaml
appId: in.quickbite.app
---
- launchApp: { clearState: true }
- tapOn: "Continue with phone"
- inputText: "9999900000"                # test number with fixed OTP in staging
- tapOn: "Send OTP"
- inputText: "123456"
- tapOn: "Search"
- inputText: "biryani"
- tapOn: { text: "Hyderabadi Biryani House" }
- tapOn: { id: "add-dish-chicken-biryani" }
- tapOn: "View cart"
- assertVisible: "To pay"
- tapOn: "Place order"                   # sandbox payment in staging
- assertVisible: "Order placed"
```

### Component test (React Native Testing Library)
```tsx
it('adds dish to cart and updates badge', async () => {
  render(<MenuScreen restaurantId="42" />, { wrapper: TestProviders });
  await screen.findByText('Paneer Tikka');
  fireEvent.press(screen.getByLabelText('Add Paneer Tikka'));
  expect(await screen.findByLabelText('1 items in cart')).toBeTruthy();
});
```

### app.config.ts: environment per profile (public values only)
```ts
const ENV = process.env.APP_ENV ?? 'development';
const cfg = { development: { api: 'http://10.0.2.2:8000' }, preview: { api: 'https://staging-api.quickbite.in' }, production: { api: 'https://api.quickbite.in' } }[ENV];
export default ({ config }) => ({ ...config, extra: { apiUrl: cfg.api, env: ENV } });
```

---

## ⚫ Interview Questions + Answers

**Q1: Describe a CI/CD pipeline for a React Native app.**
A1: On every PR, run install with caching, type-checking, linting and unit and component tests on Linux runners. A fingerprint check decides between a JS-only preview (an OTA update on a PR branch with a QR code for QA) and a native preview build. On merge, produce beta builds and run E2E tests (Maestro or Detox) on emulators and a device-farm subset, then distribute internally (TestFlight, Play internal). On release tags, build signed production binaries via EAS Build or Fastlane on macOS for iOS, submit to stores with staged rollout and monitoring gates, and handle JS hotfixes via OTA channels. Secrets live in CI or EAS, never in the repo.

**Q2: How do you manage code signing in CI?**
A2: For Android, store the upload keystore and passwords as CI secrets (or EAS-managed credentials) and enroll in Play App Signing so Google holds the app signing key and a lost upload key can be reset. For iOS, use EAS-managed credentials or fastlane match (certificates and profiles in an encrypted repo shared by the team), plus an App Store Connect API key for non-interactive uploads. Profiles must include the needed entitlements (push, associated domains). Rotate credentials, restrict access and never commit signing material.

**Q3: How do you keep mobile CI fast and affordable?**
A3: Run JS checks and Android builds on Linux runners and reserve expensive macOS runners for iOS builds (or offload to EAS). Cache dependencies and build outputs (npm, Gradle, CocoaPods, ccache). Skip native builds when the fingerprint shows no native changes and use OTA previews instead. Parallelize jobs, run long E2E suites nightly or on merge rather than every PR, keep PR E2E to a smoke subset, and fail fast on cheap checks.

**Q4: What would you E2E test in a food delivery app?**
A4: Only critical user journeys, against a stable staging backend with test data: OTP login with a test number, location selection, search to restaurant to add items to cart, coupon application, checkout with a sandbox payment, order confirmation and tracking screen, a deep link opening a restaurant, and logout. Add a push notification tap if feasible. Run them on representative Android and iOS versions and popular budget devices via device farms, and keep them deterministic (mock time, stable IDs, retries for flaky waits).

**Q5: What's the role of preview builds and updates?**
A5: They let QA, designers and PMs try each PR on real devices before merge. For JS-only changes, an OTA update published to a PR branch loads instantly in a development or preview client via QR code. For native changes, an internal-distribution build is produced. This shortens feedback loops, catches UX issues early, and avoids "works in simulator only" surprises, without touching production channels.

---

## 🔷 Trade-offs
✅ EAS Build: no Macs to maintain, managed credentials — ❌ cost, queue times, less low-level control.
✅ Fastlane + own runners: full control — ❌ maintenance of macOS machines, Ruby tooling.
✅ E2E on every PR: catches regressions early — ❌ slow/flaky → smoke subset per PR, full nightly.
✅ Device farms: real device coverage — ❌ cost, test flakiness.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CI | Automated checks per change | हर बदलाव पर जाँच |
| CD | Automated build & delivery | अपने-आप build और भेजना |
| EAS Build | Expo cloud builds | Expo का cloud build |
| Fastlane | Mobile release automation | mobile release automation |
| Code signing | Cryptographically sign app | ऐप पर digital हस्ताक्षर |
| Provisioning profile | iOS app/device/entitlement permit | iOS अनुमति file |
| Play App Signing | Google-held signing key | Google के पास signing key |
| E2E test | Full user-flow test on app | पूरे flow की जाँच |
| Device farm | Cloud real devices | cloud पर असली फ़ोन |
| Preview build | Per-PR test build | PR का test build |

---

## ⚡ 3-Line Summary
**English:**
1. CI on every PR: types, lint, unit/component tests; fingerprint decides OTA preview vs native preview build.
2. CD: reproducible signed builds (EAS or Fastlane), credentials in secrets/managed stores, distribute to testers, submit with staged rollout + gates, OTA for JS hotfixes.
3. Keep it fast & reliable: Linux for JS/Android, macOS only for iOS, caching, E2E (Maestro/Detox) for critical flows nightly, device farms for budget phones.

**Hindi:**
1. हर PR पर types, lint, tests; fingerprint तय करे OTA preview या native build।
2. CD: एक जैसे signed builds (EAS/Fastlane), secrets सुरक्षित, testers तक, store पर staged rollout, JS hotfix OTA से।
3. तेज़ और भरोसेमंद: Linux पर JS/Android, iOS के लिए macOS, cache, nightly E2E, सस्ते फ़ोन के लिए device farm।

---

## ➡️ Next Topic Suggestion
**M20. Location Tracking + Maps** — Many Indian apps (Uber, Ola, Swiggy, Rapido, Zomato) are built around maps. Next: getting location accurately and battery-efficiently, permissions, sending updates, and rendering smooth live-tracking maps.
