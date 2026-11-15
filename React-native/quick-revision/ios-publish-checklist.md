# React Native — iOS Publish Checklist
# Apple Developer → Signing → TestFlight → App Store Connect → Review
# Quick Revision

> Condensed from `10-publishing/ios/` (topics 226-257). Target in those notes: Expo SDK 52+ (React Native 0.76+). Check current docs — APIs change between SDKs. Apple fees, portal/App Store Connect labels, screenshot sizes, privacy rules, guideline numbers and review times change often: verify at developer.apple.com. Commands in the notes were not run.

---

## 🍎 Stage 1 — Apple Developer Account

**Gist:** Required for TestFlight and App Store. $99/year. Individual approval can take minutes to 48 hours; Organization takes days to weeks (needs D-U-N-S) (226).

**हिंदी:** Apple Developer account के बिना TestFlight या App Store पर कुछ नहीं जाता; $99 साल का।

- [ ] Create an Apple ID at appleid.apple.com and turn Two-Factor Auth ON — 2FA चालू करो
- [ ] Enrol at developer.apple.com/programs/enroll; choose Individual or Organization — entity चुनो
- [ ] Verify identity / legal name and pay $99 by card — ID और payment
- [ ] Organization: have the D-U-N-S number ready; expect days-weeks for approval — Organization में समय ज़्यादा
- [ ] After approval confirm access to App Store Connect and Certificates, IDs & Profiles — दोनों portal खुलें
- [ ] Paid apps / IAP: complete Agreements, Tax, and Banking (Paid Apps Agreement) or submit will fail — paid app में bank/tax ज़रूरी
- [ ] Remember: iOS builds with Xcode need a Mac; EAS Build runs on a cloud Mac so Windows/Linux works — Mac नहीं है तो EAS

---

## 🔐 Stage 2 — Bundle ID, Certificates & Provisioning

**Gist:** Four pieces form signing: Certificate (who I am, private key on your Mac), App ID/Bundle ID (which app), Devices (Development/Ad Hoc only), Provisioning Profile (links them, `.mobileprovision`) (227-230).

**हिंदी:** Certificate = मैं कौन, Bundle ID = कौन-सा app, Profile = सबको जोड़ने वाली फ़ाइल।

| Item | Detail |
|---|---|
| Development cert | Run on a real device via Xcode |
| Distribution cert | TestFlight + App Store; max 2 per account; ~1 year expiry (verify) |
| Development profile | Specific registered devices |
| Ad Hoc profile | Up to 100 registered devices (UDID) |
| App Store profile | No device limit |
| Files | `.cer` -> Keychain -> export `.p12` (with password); `.mobileprovision` |

### Bundle ID
- [ ] Pick `com.<company>.<app>` (lowercase; letters, digits, `.`, `-`); unique globally — unique रखो
- [ ] Portal → Certificates, IDs & Profiles → Identifiers → App IDs → App → Explicit Bundle ID — explicit ID बनाओ
- [ ] Tick capabilities you need (Push Notifications, Sign in with Apple, Associated Domains...) — capabilities चुनो
- [ ] Same value in `app.json` → `ios.bundleIdentifier` and in App Store Connect — तीनों जगह एक जैसा

### Certificates (manual path)
- [ ] Keychain Access → Certificate Assistant → Request a Certificate From a Certificate Authority → save CSR — CSR बनाओ
- [ ] Portal → Certificates → ➕ → Apple Development or Apple Distribution → upload CSR → download `.cer` — type चुनो
- [ ] Double-click `.cer` to install in Keychain; export cert + key as `.p12` for backup/CI — `.p12` backup रखो
- [ ] Create provisioning profile (App ID + cert + devices) and download — profile बनाओ
- [ ] Xcode: Target → Signing & Capabilities → pick Team, tick Automatically manage signing — auto-signing आसान
- [ ] Expo/EAS: let EAS create cert + profile on first build (Apple ID + 2FA prompt); use `eas credentials` to inspect — EAS खुद बना देता है

```bash
# EAS handles credentials; first build asks for Apple login
eas build --platform ios --profile production
```

---

## 🛠️ Stage 3 — Project Config, Info.plist & Build

**Gist:** In Expo, Info.plist values live in `app.json` → `ios.infoPlist`; they merge on prebuild. Missing/vague permission strings cause rejections (233, 234, 239).

**हिंदी:** Permission का कारण Info.plist में लिखना ज़रूरी है, वरना App Store reject कर देता है।

```json
{
  "expo": {
    "version": "2.5.0",
    "ios": {
      "bundleIdentifier": "com.mycompany.foodapp",
      "buildNumber": "3",
      "infoPlist": {
        "NSCameraUsageDescription": "Camera is needed to take food photos",
        "NSLocationWhenInUseUsageDescription": "Used to show nearby restaurants",
        "LSApplicationQueriesSchemes": ["whatsapp", "tez"],
        "UIBackgroundModes": ["remote-notification"]
      },
      "config": { "usesNonExemptEncryption": false }
    }
  }
}
```

| Field | app.json key | Rule |
|---|---|---|
| Version | `expo.version` (CFBundleShortVersionString) | User-visible, e.g. 2.5.0 |
| Build number | `expo.ios.buildNumber` (CFBundleVersion) | Must increase per upload |

- [ ] Set `bundleIdentifier`, `version`, `buildNumber` — तीनों जाँचो
- [ ] Bump `buildNumber` every upload (or `autoIncrement: true` in `eas.json`); duplicates are rejected — duplicate build reject
- [ ] Add a clear `NS...UsageDescription` for each permission (camera, location, etc.) — कारण साफ़ लिखो
- [ ] Standard HTTPS-only encryption: `ITSAppUsesNonExemptEncryption` false (Expo: `ios.config.usesNonExemptEncryption`) — export compliance सवाल से बचो
- [ ] Tracking (ads/cross-app): `NSUserTrackingUsageDescription` + ATT prompt (`expo-tracking-transparency`) — ATT ज़रूर
- [ ] Privacy manifest: Expo SDK 51+ modules ship manifests; add yours via `ios.privacyManifests` (verify in current docs) — privacy manifest
- [ ] App icon 1024×1024 PNG (no alpha, no rounded corners) and splash configured — icon/splash
- [ ] Build: `eas build -p ios --profile production` (cloud Mac runs `pod install` + archive -> `.ipa`) — IPA बनाओ

### Xcode manual path (needs Mac)
- [ ] Install Xcode, accept license, `xcode-select --install` — Xcode setup
- [ ] Xcode → Settings → Accounts → add Apple ID — account जोड़ो
- [ ] Expo: `npx expo prebuild --platform ios`, then `cd ios && pod install` — pods install
- [ ] Open the `.xcworkspace` (not `.xcodeproj`) — workspace खोलो
- [ ] Device "Any iOS Device (arm64)" -> Product → Archive → Distribute App → App Store Connect — archive करो

---

## ✈️ Stage 4 — TestFlight

**Gist:** Upload `.ipa` to App Store Connect; after "Processing" (10-30 min) it appears in TestFlight. Builds expire after 90 days (240-243).

**हिंदी:** पहले TestFlight पर टीम से test करवाओ; build 90 दिन में expire हो जाती है।

```json
{
  "cli": { "appVersionSource": "remote" },
  "build": { "production": { "autoIncrement": true } },
  "submit": {
    "production": {
      "ios": {
        "ascAppId": "1234567890",
        "ascApiKeyPath": "./secrets/AuthKey_ABC123DEFG.p8",
        "ascApiKeyIssuerId": "11111111-2222-3333-4444-555555555555",
        "ascApiKeyId": "ABC123DEFG"
      }
    }
  }
}
```

```bash
eas submit --platform ios --latest          # latest finished build
eas submit --platform ios --id <build-id>   # a specific build
```

- [ ] App record already exists in App Store Connect (Apps → + → New App; Name 2-30 chars, Language, Bundle ID, SKU) — पहले app record बनाओ
- [ ] Generate API Key (Users and Access → Integrations → App Store Connect API, role App Manager); `.p8` downloads only once — `.p8` एक ही बार मिलती है
- [ ] Never commit the `.p8`; add to `.gitignore` — git में मत डालो
- [ ] Note the numeric Apple ID of the app for `ascAppId` — ascAppId नोट करो
- [ ] Upload with `eas submit -p ios --latest` (or Transporter) — upload करो
- [ ] Answer export compliance (or pre-set the encryption flag) — compliance जवाब
- [ ] **Internal** testing: add teammates as ASC users, create group, enable automatic distribution; up to 100 testers, no review — Internal में review नहीं
- [ ] **External** testing: create group, fill Test Information (description, feedback email, demo account, What to Test), add testers or Public Link, submit for Beta App Review (usually up to ~24 h); up to 10,000 testers — External में Beta Review
- [ ] Later builds of the same version often skip review; a new version number triggers review again — नया version तो फिर review
- [ ] Re-upload before the 90-day expiry — 90 दिन से पहले नई build

---

## 🏬 Stage 5 — App Store Connect Setup

**Gist:** Fill App Information, Pricing, Privacy and the version Listing, then attach a build (244-250).

**हिंदी:** App Store Connect में सारी जानकारी भरो, फिर build attach करके review भेजो।

### App Information
- [ ] Name (≤30), Subtitle (≤30) per language — नाम और subtitle
- [ ] Primary (+ optional secondary) category — category
- [ ] Content Rights (third-party content?) — content rights
- [ ] Age Rating questionnaire (Apple changed it recently: check current form) — age rating
- [ ] EULA (Apple standard or custom) and Privacy Policy URL — EULA और privacy URL

### Pricing and Availability
- [ ] Free or a base-country price point (Apple derives other countries) — price तय करो
- [ ] Choose countries; optional pre-orders — countries चुनो

### App Privacy
- [ ] Public Privacy Policy URL ready — policy URL
- [ ] Answer data collection: types, purposes, linked to user?, used for tracking? — हर data type भरो
- [ ] Click **Publish** on the privacy answers — Publish दबाओ

### Version Listing
- [ ] Promotional Text (≤170, editable without review), Description (≤4000), Keywords (≤100, comma-separated, no spaces) — ASO के लिए keywords
- [ ] Support URL (required), Marketing URL (optional), What's New, Copyright — URLs और notes
- [ ] Screenshots: PNG/JPEG, no alpha, exact size; 1-10 per set; usually biggest iPhone size required (check ASC "Screenshot Specifications"); iPad set if iPad supported — sizes verify करो
- [ ] Optional App Preview video 15-30 s, max 3 — preview video
- [ ] Version Release option: Manual / Automatic / Scheduled — release कैसे हो

```bash
# Simulator screenshot (Mac)
xcrun simctl io booted screenshot shot.png
```

---

## 📤 Stage 6 — Submit for Review

**Gist:** Attach the processed build, give the reviewer everything needed to log in and use the app, then "Add for Review" → "Submit to App Review" (251, 252).

**हिंदी:** Reviewer को demo account और notes ज़रूर दो, वरना सीधा reject।

- [ ] Pre-flight: build processed, screenshots, description, privacy, age rating, price — सब पूरे
- [ ] Version page → Build → select the processed build — build चुनो
- [ ] Export compliance answered — compliance
- [ ] App Review Information: contact name/phone/email — contact info
- [ ] Sign-in required? Provide demo username/password in review notes — **demo account ज़रूर**
- [ ] Notes for hidden features, special hardware, OTP workaround — notes लिखो
- [ ] Backend services running during review — server चालू रखो
- [ ] Add for Review → Submit to App Review — submit

| Status | Meaning |
|---|---|
| Prepare for Submission | Still editing |
| Waiting for Review | In Apple's queue |
| In Review | Reviewer testing (minutes to hours) |
| Pending Developer Release | Approved, manual release chosen |
| Ready for Distribution | Live |
| Rejected | Binary problem; see Resolution Center |
| Metadata Rejected | Text/screenshots only; no new build |
| Developer Rejected | You pulled it |

### Release
- [ ] Optional: phased release (automatic updates only) — phased release
- [ ] Watch crashes (Sentry/Crashlytics) and ASC Analytics — crash देखो
- [ ] Broken? Pause phased release (up to 30 days); hotfix via OTA if JS-only, else new build — pause + hotfix

| Day | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| % auto-updating | 1 | 2 | 5 | 10 | 20 | 50 | 100 |

Users tapping "Update" manually can still get it at any time.

---

## 🚫 Stage 7 — Review Guidelines & Rejection Reasons

**Gist:** Read the five sections of App Store Review Guidelines (Safety, Performance, Business, Design, Legal) and the "Before You Submit" list; build compliance in early (254, 253). Guideline numbers can be renumbered: verify at developer.apple.com/app-store/review/guidelines.

**हिंदी:** Rejection का guideline number पढ़ो, उसी build को real device पर चलाकर issue दोहराओ, ठीक करके Resolution Center में जवाब दो।

| Guideline | Reason | Typical fix |
|---|---|---|
| 2.1 Completeness | Crashes, placeholder content, broken links, no demo account | Test release build on real devices; add demo login |
| 2.3 Accurate Metadata | Screenshots/description don't match app | Real screenshots; no competitor names in keywords |
| 3.1.1 In-App Purchase | Digital goods without Apple IAP | Use IAP (physical goods can use other gateways) |
| 4.0 / 4.2 Minimum Functionality | Just a website wrapper | Add real native value (push, offline, native UI) |
| 4.8 Login Services | Third-party login without equivalent option | Add Sign in with Apple (or qualifying option) |
| 5.1.1 Data Collection | No privacy policy / account deletion | Privacy URL + in-app account deletion |
| 5.1.2 Data Use / ATT | Tracking without ATT prompt | Show ATT; fill privacy labels correctly |
| Permission strings | Missing/vague `NS...UsageDescription` | Clear purpose strings |
| 2.5.x Software Requirements | Private APIs, hot-patching that changes app purpose | Public APIs only (OTA rule 2.5.2) |
| Privacy manifest | Required-reason APIs/SDKs missing `PrivacyInfo.xcprivacy` | Update SDKs; Expo `ios.privacyManifests` |

### Before You Submit (paraphrased from Apple's intro)
- [ ] Test for crashes and bugs — crash test
- [ ] All metadata complete and accurate — metadata सही
- [ ] Updated contact info + demo account + notes — contact info
- [ ] Backend enabled during review — backend चालू
- [ ] Non-obvious features explained in notes — छिपे features बताओ
- [ ] Chat/UGC apps: report + block + moderation — UGC में report/block
- [ ] Real-money gaming/health/kids/crypto features: check the matching guideline section first — risky features पहले देखो

### If rejected
- [ ] Read the email + Resolution Center message (guideline number) — message पढ़ो
- [ ] Reproduce on a real device with the same build — दोहराओ
- [ ] Fix code or metadata (Metadata Rejected needs no new build) — fix करो
- [ ] Reply in Resolution Center (screen recording helps) — reply दो
- [ ] Upload new build with higher `buildNumber` if needed; resubmit — resubmit

---

## 🧠 Quick Q&A

**Android versionCode equals what on iOS?** `buildNumber` (CFBundleVersion); `version` is CFBundleShortVersionString.
हिंदी: Android का versionCode = iOS का buildNumber।

**Internal vs External TestFlight?** Internal: ASC users, up to 100, no review. External: anyone, up to 10,000, Beta App Review.
हिंदी: Internal में review नहीं, External में Beta Review।

**Android upload auth vs iOS?** Android: Google Service Account JSON. iOS: App Store Connect API key (`.p8`).
हिंदी: Android में service account, iOS में `.p8` key।
