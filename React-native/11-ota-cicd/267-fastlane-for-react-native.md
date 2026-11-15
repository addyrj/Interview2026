# 267. Fastlane for React Native
# हिंदी में: React Native के लिए Fastlane
# Platform: Android ✅ | iOS ✅ | Both ✅
# Expo SDK 54 (React Native 0.81) — check current docs — APIs change between SDKs

---

## 🔵 Simple Definition (English)
**Fastlane** is an open-source Ruby tool that automates the boring release tasks: incrementing build numbers, signing, building, uploading to TestFlight / Play Store, and managing screenshots and metadata. You describe steps as **lanes** in a `Fastfile`, then run `fastlane ios beta`.

## 🔵 सरल परिभाषा (Hindi)
**Fastlane** एक open-source Ruby tool है जो release के boring काम automate करता है: build number बढ़ाना, signing, build, TestFlight / Play Store पर upload, screenshots और metadata। आप `Fastfile` में **lanes** लिखते हो और `fastlane ios beta` से चलाते हो।

---

## 🔴 Problem it Solves
```
BEFORE Fastlane:
❌ 15 manual steps in Xcode + Play Console for every release
❌ Someone forgets to bump the build number → upload rejected
❌ Certificates shared by hand → "my profile expired" chaos
❌ Release knowledge lives in one senior dev's head
```

## 🔴 यह क्यों बना? (Hindi)
```
Fastlane से पहले:
❌ हर release में Xcode + Play Console के 15 manual steps
❌ Build number बढ़ाना भूल गए → upload reject
❌ Certificates हाथ से share → "profile expire हो गया" वाली गड़बड़
❌ Release का ज्ञान सिर्फ एक senior dev के दिमाग में
Fastlane: सब steps code में → repeatable, shareable।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Install: `brew install fastlane` or Bundler (`gem install bundler`, Gemfile)
Step 2 → In ios/ and android/ run `fastlane init` → creates fastlane/Fastfile
Step 3 → Write lanes using "actions":
         build_app (gym), upload_to_testflight (pilot),
         gradle, upload_to_play_store (supply), match (certs)
Step 4 → Run lane locally: `bundle exec fastlane ios beta`
Step 5 → Put the same command in CI (GitHub Actions macOS runner)
Step 6 → Secrets (API keys, match password) come from environment variables
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Install: `brew install fastlane` या Bundler + Gemfile
Step 2 → ios/ और android/ में `fastlane init` → Fastfile बनती है
Step 3 → Lanes में actions लिखो: build_app, upload_to_testflight,
         gradle, upload_to_play_store, match
Step 4 → Local में चलाओ: `bundle exec fastlane ios beta`
Step 5 → यही command CI (macOS runner) में डालो
Step 6 → Secrets environment variables से आते हैं
```

---

## 🟡 Real World Example
A **Paytm**-like fintech app with a native-heavy bare RN codebase uses Fastlane `match` so all 40 developers share the same iOS certificates from an encrypted private git repo. Friday night the CI runs `fastlane ios beta` → build → TestFlight → Slack message "Build 1432 ready".

## 🟡 Real Example Hindi mein
**Paytm** जैसे fintech app में bare RN codebase है। Fastlane `match` से 40 developers एक ही iOS certificates encrypted private git repo से लेते हैं। शुक्रवार रात CI `fastlane ios beta` चलाता है → build → TestFlight → Slack पर "Build 1432 ready"।

---

## 💻 Code Example — Basic

`ios/fastlane/Fastfile` (Ruby):
```ruby
# Fastfile for iOS — run with: bundle exec fastlane ios beta
default_platform(:ios)            # lanes below belong to iOS

platform :ios do                  # start iOS platform block
  desc "Build and push to TestFlight"   # shown in `fastlane lanes`
  lane :beta do                   # lane name = `beta`
    # Increase build number using the latest TestFlight build + 1
    increment_build_number(
      build_number: latest_testflight_build_number + 1  # needs App Store Connect API key
    )
    # Build the .ipa (gym = build_app)
    build_app(
      workspace: "MyApp.xcworkspace",   # RN uses a CocoaPods workspace
      scheme: "MyApp",                  # Xcode scheme to archive
      export_method: "app-store"        # ready for TestFlight/App Store
    )
    # Upload to TestFlight (pilot = upload_to_testflight)
    upload_to_testflight(
      skip_waiting_for_build_processing: true  # do not block CI
    )
  end
end
```

`android/fastlane/Fastfile`:
```ruby
default_platform(:android)         # Android lanes below

platform :android do
  desc "Build AAB and upload to Play internal track"
  lane :internal do
    # Run Gradle task bundleRelease (creates app-release.aab)
    gradle(task: "bundle", build_type: "Release")
    # Upload to Play Console (supply = upload_to_play_store)
    upload_to_play_store(
      track: "internal",                    # internal testing track
      json_key: ENV["PLAY_JSON_KEY_PATH"],  # service account JSON path
      skip_upload_metadata: true,           # only upload binary
      skip_upload_images: true,
      skip_upload_screenshots: true
    )
  end
end
```

## 💻 Code Example — Advanced

Production iOS lane with `match`, API-key auth, error handling, and Slack notice:
```ruby
default_platform(:ios)

platform :ios do
  # Runs before every lane
  before_all do
    # Fail early if CI forgot to set secrets
    ensure_env_vars(env_vars: ["ASC_KEY_ID", "ASC_ISSUER_ID", "ASC_KEY_CONTENT"])
  end

  lane :release do
    # Authenticate with App Store Connect API key (no 2FA prompts in CI)
    app_store_connect_api_key(
      key_id: ENV["ASC_KEY_ID"],
      issuer_id: ENV["ASC_ISSUER_ID"],
      key_content: ENV["ASC_KEY_CONTENT"],   # contents of the .p8 file
      is_key_content_base64: false
    )
    # Create temp keychain on CI (required on fresh macOS runners)
    setup_ci if ENV["CI"]
    # Fetch certs + profiles from the encrypted git repo (read-only on CI)
    match(type: "appstore", readonly: true)
    # Bump build number from TestFlight's latest
    increment_build_number(build_number: latest_testflight_build_number + 1)
    # Build signed IPA
    build_app(workspace: "MyApp.xcworkspace", scheme: "MyApp")
    # Upload binary
    upload_to_testflight
    # Notify team
    slack(message: "iOS build uploaded", slack_url: ENV["SLACK_URL"])
  end

  # Runs when any lane fails
  error do |lane, exception|
    slack(message: "Lane #{lane} failed: #{exception.message}",
          success: false, slack_url: ENV["SLACK_URL"])
  end
end
```
GitHub Actions snippet:
```yaml
# iOS jobs need macOS runner (billed at higher rate)
jobs:
  ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with: { bundler-cache: true, working-directory: ios }
      - run: npm ci
      - run: cd ios && bundle exec pod install
      - run: cd ios && bundle exec fastlane release
        env:
          ASC_KEY_ID: ${{ secrets.ASC_KEY_ID }}
          ASC_ISSUER_ID: ${{ secrets.ASC_ISSUER_ID }}
          ASC_KEY_CONTENT: ${{ secrets.ASC_KEY_CONTENT }}
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
```
Action names/params above are real Fastlane actions, but exact params change between Fastlane versions — check `fastlane action <name>`. Not run here (needs Apple/Google accounts).

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Build action | `gradle` | `build_app` (gym) |
| Upload action | `upload_to_play_store` (supply) | `upload_to_testflight` (pilot) / `upload_to_app_store` (deliver) |
| Signing | Keystore via Gradle properties/env | `match` + provisioning profiles |
| Auth | Google service account JSON | App Store Connect API key (.p8) |
| CI runner | Linux ok | macOS only |
| Screenshots | `screengrab` | `snapshot` |

---

## 🟠 Expo vs CLI Difference
Expo way (managed): Usually you do **not** need Fastlane — `eas build` + `eas submit` replace it.
```bash
eas build --platform ios --profile production --auto-submit
```
CLI way (bare RN): Fastlane is the classic choice because you own `ios/` and `android/`.
```bash
cd ios && bundle exec fastlane beta
```
Expo can also use Fastlane after `npx expo prebuild` (generates native folders), but then you lose the "managed" benefit. EAS can also run your own scripts through custom build hooks.

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Installing Fastlane globally with different versions per developer
✅ **Correct:** Use a `Gemfile` (`gem "fastlane"`) and `bundle exec fastlane` so everyone has the same version.

❌ **Mistake 2:** Using Apple ID + password and 2FA in CI
✅ **Correct:** Use an App Store Connect **API key** (`app_store_connect_api_key`).

❌ **Mistake 3:** Running `match` without `readonly: true` on CI
✅ **Correct:** CI should only read; generate new certs from one trusted local machine.

❌ **Mistake 4:** Hardcoding secrets in Fastfile
✅ **Correct:** `ENV["..."]` and CI secrets.

---

## 🧠 Tricky Interview Question
**Q:** CI builds the iOS app fine, but `upload_to_testflight` says "build number already used". The Fastfile has `increment_build_number`. What went wrong?

**Answer:** `increment_build_number` without a value only adds +1 to the number *in the local Xcode project*, which is the same on every CI run (the change is never committed). Use `latest_testflight_build_number + 1` (queries Apple) or commit the bump back to git, or keep numbers in an external counter like `$GITHUB_RUN_NUMBER`.

---

## ⚫ Interview Questions + Answers

**Q1: What is a lane?**
A1: A named Ruby function in the Fastfile that chains actions, e.g. `lane :beta`.

**Q2: What does `fastlane match` do?**
A2: Stores certificates/profiles in an encrypted git repo or cloud bucket so the whole team and CI share the same signing identity.

**Q3: Fastlane vs EAS?**
A3: EAS is a hosted build service (builds in cloud). Fastlane is a local automation tool (builds on your machine/runner). They can complement: EAS builds, Fastlane handles metadata/screenshots.

**Q4: How do you upload Android releases?**
A4: `upload_to_play_store` with a service-account JSON key and a track (`internal`, `beta`, `production`).

**Q5: How to run Fastlane in CI for iOS?**
A5: macOS runner, `setup_ci`, `match readonly`, API key auth, then `build_app` and `upload_to_testflight`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Bare RN with native folders
- Need metadata, screenshots, certificate sharing automation
- Want to build on your own CI runners

❌ Avoid when:
- Pure Expo managed app — EAS does it with less setup
- Team has nobody comfortable with Ruby tooling

---

## 📊 Visual Diagram
```
 CI trigger ──► Fastfile lane
                   │
   ┌───────────────┼────────────────┐
   ▼               ▼                ▼
 match         build_app/gradle   upload_to_testflight
 (certs)       (compile)          upload_to_play_store
                                      │
                                      ▼
                                 Slack notify
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Lane | Named automation workflow | नाम वाला automation workflow |
| Action | Built-in step like build_app | Built-in step |
| match | Shared certificate manager | Shared certificate manager |
| gym / pilot / supply | Aliases of build_app / testflight / play upload | Actions के पुराने नाम |
| Gemfile | Ruby dependency list | Ruby dependencies की list |

---

## ⚡ 3-Line Summary
**English:**
1. Fastlane scripts your whole release: bump, sign, build, upload.
2. Lanes live in `Fastfile`; `match` shares certificates; API keys avoid 2FA in CI.
3. Expo managed apps usually use EAS instead; bare RN apps love Fastlane.

**Hindi:**
1. Fastlane पूरा release script कर देता है: bump, sign, build, upload।
2. Lanes `Fastfile` में, `match` certificates share करता है, API key से CI में 2FA नहीं।
3. Expo managed apps में आमतौर पर EAS; bare RN में Fastlane।

---

## ➡️ Next Topic
**268. Automated Screenshots** — Fastlane `snapshot`/`screengrab` से store screenshots अपने-आप बनाना।
