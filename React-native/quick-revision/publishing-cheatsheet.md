# React Native — Publishing Cheatsheet
# Play Store + App Store + OTA Updates
# Quick Revision

---

## 🤖 Android Publishing

### Required Files
```
app-release.aab          ← upload to Play Store (NOT APK)
myapp-release-key.keystore ← NEVER LOSE THIS (backup in 3 places!)
google-services.json     ← for Firebase
```

### Build Commands
```bash
# Signed AAB (manual):
cd android && ./gradlew bundleRelease
# Output: android/app/build/outputs/bundle/release/app-release.aab

# EAS Build (cloud, recommended):
eas build --platform android --profile production

# EAS Submit (auto upload to Play Console):
eas submit --platform android
```

### Keystore Generation (once!)
```bash
keytool -genkey -v \
  -keystore myapp-release.keystore \
  -alias myapp-key \
  -keyalg RSA -keysize 2048 \
  -validity 10000
```

### Version Rules
```
versionCode: 1, 2, 3... (integer, must ALWAYS increment per upload)
versionName: "1.0.0" (user-visible, flexible)
```

### gradle.properties (passwords — NEVER in git)
```
MYAPP_RELEASE_STORE_FILE=myapp-release.keystore
MYAPP_RELEASE_KEY_ALIAS=myapp-key
MYAPP_RELEASE_STORE_PASSWORD=...
MYAPP_RELEASE_KEY_PASSWORD=...
```

### Tracks
```
Internal Testing → instant (no review), up to 100 testers
Closed Testing (Alpha) → limited group
Open Testing (Beta) → public beta
Production → live (rolling release recommended: start 10%)
```

### What You Need for Submission
```
✅ Developer account ($25 one-time)
✅ Signed AAB
✅ App icon: 512×512 PNG (no alpha!)
✅ Feature graphic: 1024×500
✅ Screenshots: min 2 phone screenshots
✅ Privacy Policy URL
✅ Content rating questionnaire (IARC)
✅ Data Safety section (April 2022+ required)
```

---

## 🍎 iOS Publishing

### Required Setup
```
Apple Developer Account: $99/year
Distribution Certificate: .p12 (1 year expiry, max 2 per account)
Provisioning Profile: .mobileprovision
Bundle ID: com.yourcompany.yourapp (unique globally)
```

### EAS Build + Submit (recommended)
```bash
eas build --platform ios --profile production
# EAS handles certificates, provisioning profiles, signs IPA on Mac cloud

eas submit --platform ios
# Uploads IPA to TestFlight via App Store Connect API
```

### Version Rules
```
version (CFBundleShortVersionString): "1.0.0" — user-visible
buildNumber (CFBundleVersion): "1", "2", "3"... — must increment per upload
```

### TestFlight Flow
```
Upload IPA → App Store Connect → TestFlight
├── Internal (instant, 25 team members, no review)
└── External (Beta App Review: 1-2 days, up to 10,000 testers)
    → Builds expire after 90 days
```

### App Store Submission
```
Submit build for review → "Waiting for Review" → "In Review" (1-3 days)
→ "Approved" → Choose: Manual release or Phased release (7 days, 1%→100%)
→ OR "Rejected" → Fix → Resubmit
```

### What You Need
```
✅ Signed IPA
✅ App icon: 1024×1024 PNG (no rounded corners, no alpha)
✅ Screenshots: iPhone 6.7" (1290×2796) + iPhone 5.5" (1242×2208) REQUIRED
✅ Privacy Policy URL
✅ App name (max 30 chars), subtitle (max 30 chars)
✅ Keywords (max 100 chars) — for ASO!
✅ Review notes + TEST ACCOUNT credentials (login required)
✅ Age rating questionnaire
```

### Common Rejection Reasons
```
❌ Missing test credentials in review notes
❌ Crashes during review
❌ Metadata mismatch (screenshots don't match app)
❌ No Privacy Policy URL
❌ IAP not using Apple StoreKit (digital goods)
❌ Minimum functionality (too basic)
❌ Missing ATT prompt for tracking
```

---

## 🔄 OTA Updates (EAS Update)

```bash
# Push JS-only changes without store review
eas update --branch production --message "fix cart discount"

# Check updates in app (expo-updates):
const update = await Updates.checkForUpdateAsync();
if (update.isAvailable) {
  await Updates.fetchUpdateAsync();
  Updates.reloadAsync();  // or prompt user
}
```

### What CAN be OTA updated
```
✅ JavaScript/TypeScript code
✅ React components
✅ Images, fonts, JSON (assets)
✅ API URLs, feature flags
```

### What CANNOT be OTA updated
```
❌ Native code (Kotlin/Swift/C++)
❌ New native dependencies
❌ AndroidManifest.xml / Info.plist changes
❌ Expo SDK major version
❌ App icon, splash screen
Rule: Did you run pod install or change build.gradle? → Store build
```

### Branch model
```
production → live users
staging → TestFlight / internal beta
development → dev builds

eas update --branch production   # reaches production app users
Runtime version must match between update and installed build
```

---

## ⚡ Version Number Quick Reference

```
ANDROID:
  versionCode:  1 → 2 → 3 (every Play Store upload, any track)
  versionName: "1.0.0" → "1.0.1" → "1.1.0" (user-visible, flexible)

iOS:
  buildNumber: "1" → "2" → "3" (every TestFlight/App Store upload)
  version: "1.0.0" → "1.0.1" (user-visible, flexible)

EAS auto-increment:
  eas build --auto-increment  → bumps versionCode/buildNumber
```

---

## 🚨 Critical Rules (Never Forget)

```
1. KEYSTORE BACKUP:
   Never commit to git
   Backup in 3 places: password manager + cloud + team vault
   Enable Play App Signing → if upload key lost, Google can issue new one

2. CERTIFICATE BACKUP (iOS):
   Download .p12 from Keychain + provisioning profile
   EAS credentials manages automatically — still download + backup

3. VERSION CODES:
   MUST increment for every store upload — even hotfixes
   Play Store: versionCode never goes backward
   App Store: buildNumber never repeats

4. TEST ACCOUNT:
   For iOS: ALWAYS add in App Store Connect → Review Notes
   For Android: Add in Play Console → App Content → Review
   No test account for login app = rejection

5. PRIVACY POLICY:
   Required for ANY app with: login, location, analytics, ads
   URL must be live and accessible (no 404)
   Use: privacypolicygenerator.info

6. OTA vs STORE BUILD:
   New native dependency → Store build
   JS-only change → OTA update (eas update)
   When in doubt: test on both OS and check if native code changed
```

---

## 🏃 EAS CLI Quick Commands

```bash
# Setup
npm install -g eas-cli
eas login
eas build:configure   # creates eas.json

# Android
eas build --platform android --profile production
eas submit --platform android

# iOS
eas build --platform ios --profile production
eas submit --platform ios

# Both platforms
eas build --platform all --profile production

# OTA update
eas update --branch production --message "bug fix"
eas update --branch staging --message "test new feature"

# Credentials
eas credentials  # view/manage certs and keystores

# Channels
eas channel:list  # show all channels
```

---

## 📊 Android vs iOS at a Glance

| Feature | Android | iOS |
|---------|---------|-----|
| Store | Google Play Console | App Store Connect |
| Dev fee | $25 (once) | $99/year |
| Sign with | Keystore (.jks) | Certificate (.p12) |
| Upload format | AAB (.aab) | IPA (.ipa) |
| Review time | Hours–2 days | 1–3 days |
| Beta | Internal/External testing | TestFlight |
| Rolling release | % controlled | 7-day phased |
| OTA updates | ✅ JS-only | ✅ JS-only (same functionality) |
| IAP required | Google Play Billing (digital) | Apple StoreKit (digital) |
| Sideloading | ✅ APK directly | ❌ Only through Apple |
