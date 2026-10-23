# 230. iOS Certificates & Provisioning Profiles
# हिंदी में: iOS App Signing — Certificates और Provisioning Profiles
# Platform: Android ❌ | iOS ✅

---

## 🔵 Simple Definition (English)
iOS app signing uses **certificates** (who you are) + **provisioning profiles** (what your app is allowed to do + which devices it runs on). Unlike Android (one keystore file), iOS has a 3-part system: Apple Developer Account → Certificate → Provisioning Profile → Signed App. Required to run on real devices and submit to App Store.

## 🔵 सरल परिभाषा (Hindi)
iOS app signing में **certificates** (आप कौन हो) + **provisioning profiles** (आपकी app क्या कर सकती है + किन devices पर run होगी) use होते हैं। Android (एक keystore) के unlike, iOS में 3-part system है: Apple Developer Account → Certificate → Provisioning Profile → Signed App। Real devices पर run करने और App Store submit करने के लिए जरूरी।

---

## 🔴 Why iOS Signing is Complex
```
APPLE'S SECURITY MODEL:
  iOS is a closed ecosystem — Apple controls what runs on iPhones
  No sideloading without developer account (unlike Android APK)

3-PART VERIFICATION:
  1. WHO ARE YOU? → Certificate (your identity, signed by Apple)
  2. WHAT CAN YOUR APP DO? → App ID + Entitlements (push, iCloud, etc.)
  3. WHERE CAN IT RUN? → Provisioning Profile (links app ID + cert + devices)

WITHOUT PROPER SIGNING:
  "This app cannot be installed because its integrity could not be verified."
  App crashes on launch
  TestFlight distribution fails
  App Store review rejected

WITH PROPER SIGNING:
  App installs on registered devices
  TestFlight distribution works
  App Store accepts the build
```

---

## 🟢 How It Works — Step by Step

```
iOS SIGNING FLOW:
──────────────────────────────────────────────────────
  Step 1: Apple Developer Account ($99/year)
    → developer.apple.com/account
    → Individual or Company (Company needs D-U-N-S number)

  Step 2: Create App ID (Bundle Identifier)
    → "com.company.appname" (must be unique globally)
    → Enables specific capabilities: Push Notifications, iCloud,
      Sign in with Apple, HealthKit, etc.

  Step 3: Create Certificate
    → Development Certificate: for running on real device via Xcode
    → Distribution Certificate: for TestFlight + App Store
    → Max 2 Distribution Certificates per Apple account
    → Download as .cer → install in Keychain → export as .p12

  Step 4: Create Provisioning Profile
    → LINKS: App ID + Certificate + Device UDIDs
    → Development Profile: specific registered devices only
    → Ad Hoc Profile: up to 100 specific registered devices
    → App Store Profile: no device limit (for App Store distribution)
    → Download as .mobileprovision

  Step 5: Build in Xcode (or EAS Build)
    → Xcode: Sign & Capabilities tab → select team + profile
    → XCode auto-signing: handles Steps 3-4 automatically

  Step 6: Archive + Upload
    → Xcode: Product → Archive → Distribute App
    → Upload to App Store Connect (previously iTunes Connect)
    → OR use EAS Build / Fastlane
```

---

## 🟡 Real World Example
**Paytm iOS release:** Team sets up Distribution Certificate on CI server. EAS Build stores the `.p12` certificate + provisioning profile in encrypted vault. When CI triggers `eas build --platform ios --profile production`, EAS pulls the certificate, signs the IPA, and uploads to TestFlight via `eas submit`. QA team gets TestFlight notification, tests for 2 days. Team submits for App Store review — 1-2 day review. App goes live. All of this happens without any developer needing macOS locally (EAS runs Xcode on Mac cloud machines).

---

## 💻 Code Example — Manual Certificate Setup

```bash
# ─── STEP 1: Generate Certificate Signing Request (CSR) ───────────────
# On macOS:
# Keychain Access → Certificate Assistant → Request a Certificate from a CA
# → Save to disk as CertificateSigningRequest.certSigningRequest

# ─── STEP 2: At developer.apple.com ─────────────────────────────────────
# Certificates, Identifiers & Profiles → Certificates → + button
# → iOS Distribution → upload CSR file → download Distribution.cer
# → Double-click to install in Keychain
# → In Keychain: right-click cert → Export → save as Distribution.p12
#   (p12 = certificate + private key combined — keep it secure!)

# ─── STEP 3: Create App ID ───────────────────────────────────────────────
# Identifiers → + button → App IDs → App
# Bundle ID: com.yourcompany.yourapp
# Enable capabilities: Push Notifications, Associated Domains, etc.

# ─── STEP 4: Create Provisioning Profile ────────────────────────────────
# Profiles → + button → App Store (for production)
# → Select App ID: com.yourcompany.yourapp
# → Select Certificate: your Distribution certificate
# → Name: "YourApp App Store"
# → Download: YourApp_AppStore.mobileprovision

# ─── STEP 5: Xcode Setup ─────────────────────────────────────────────────
# Project settings → Signing & Capabilities
# → Uncheck "Automatically manage signing" (for manual)
# → Team: select your team
# → Provisioning Profile: select the downloaded .mobileprovision
```

```bash
# ─── EAS BUILD: Handles Everything Automatically ─────────────────────────

# app.json / app.config.js — iOS bundle identifier
{
  "expo": {
    "name": "MyApp",
    "slug": "myapp",
    "ios": {
      "bundleIdentifier": "com.yourcompany.myapp",
      "buildNumber": "1"
    }
  }
}

# eas.json — build profiles
{
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": {
        "simulator": false
      }
    },
    "preview": {
      "distribution": "internal",   // TestFlight internal testers
      "ios": {
        "buildConfiguration": "Release"
      }
    },
    "production": {
      "ios": {
        "buildConfiguration": "Release"
      }
    }
  }
}

# Build for App Store:
eas build --platform ios --profile production
# EAS asks: "Would you like to set up iOS credentials?"
# → Log in to Apple Developer account via CLI
# → EAS creates/manages certificates + provisioning profiles
# → Builds on Mac cloud, downloads IPA, stores credentials

# Submit to TestFlight / App Store:
eas submit --platform ios
# → Uploads IPA to App Store Connect automatically
```

```bash
# ─── ENVIRONMENT VARIABLES FOR CI/CD ────────────────────────────────────
# If doing manual CI (GitHub Actions without EAS):

# APPLE_ID=your@email.com
# APPLE_TEAM_ID=XXXXXXXXXX (from developer.apple.com → Membership)
# APP_STORE_CONNECT_API_KEY_ID=XXXXXXXXXX
# APP_STORE_CONNECT_ISSUER_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
# APP_STORE_CONNECT_API_KEY_PATH=./AuthKey_XXXXXXXXXX.p8

# Generate API Key:
# App Store Connect → Users and Access → Keys → + button
# Download .p8 key file (can only download once!)
# Use this with Fastlane or EAS for CI authentication

# PREFERRED: Use EAS secrets instead of managing all this manually:
eas secret:create --scope project --name APPLE_ID --value your@email.com
```

---

## 📱 Android vs iOS Difference
| Feature | Android (Keystore) | iOS (Certificates) |
|---------|------------------|-------------------|
| Sign with | .keystore / .jks file | .p12 certificate + .mobileprovision |
| Generated by | Developer (keytool) | Apple (developer.apple.com) |
| Expires | ~27 years (10000 days) | 1 year (Distribution cert) |
| Lost it? | Lose app (without Play App Signing) | Create new cert (limit: 2 per account) |
| Cloud option | EAS Build | EAS Build |
| Devices restriction | None | Dev/Ad Hoc: up to 100 UDIDs |

---

## 🟠 Expo vs CLI Difference

Expo/EAS way:
```bash
# EAS manages all certificates — you just log in to Apple account
eas build --platform ios
# EAS CLI:
# → Logs in to Apple Developer portal via Apple ID
# → Creates/downloads certificate automatically
# → Creates/downloads provisioning profile automatically
# → Stores everything in Expo's encrypted vault
# → You can download anytime: eas credentials
```

CLI (Xcode manual):
```bash
# You manage everything manually:
# 1. Create CSR in Keychain Access
# 2. Upload to developer.apple.com → get .cer
# 3. Create provisioning profile on developer.apple.com
# 4. Download + install in Xcode
# 5. Archive in Xcode → upload to App Store Connect
# OR use Fastlane to automate this:
# fastlane match → syncs certs + profiles from encrypted git repo
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting to increment `buildNumber` before uploading
```
ERROR: "This build is invalid... The bundle version must be higher..."
Each upload to TestFlight/App Store requires a new buildNumber
Even if you're fixing a bug and version stays "1.2.0"
buildNumber (CFBundleVersion): "1", "2", "3" ... must always increase
```

❌ **Mistake 2:** Using Development profile for App Store submission
```
ERROR: "Invalid Provisioning Profile"
Development profile → only registered devices (for testing)
App Store profile → required for App Store / TestFlight external testers
Make sure eas.json production profile uses App Store distribution
```

❌ **Mistake 3:** Exceeding certificate limit without cleanup
```
Apple allows max 2 iOS Distribution Certificates
If you have 2 and create another: must revoke old one
Revoking: any apps signed with that cert still work
But: you need to regenerate provisioning profiles (they reference the cert)
EAS handles this automatically; manual process is error-prone
```

---

## 🧠 Tricky Interview Question

**Q: Your iOS Distribution Certificate expires. What happens to existing App Store users? What do you need to do?**

**Answer:** Existing users are **not affected** — apps already installed on devices continue to work normally. The certificate is only used at build time to sign the IPA; once installed, iOS doesn't re-check the certificate expiry. However, you **cannot submit new builds** to TestFlight or the App Store with an expired certificate. You must: (1) Renew the certificate at developer.apple.com (or let EAS handle it) — this creates a new certificate. (2) Regenerate provisioning profiles that reference the old certificate — they become invalid. (3) Sign new builds with the new certificate. EAS Build handles certificate renewal automatically if you run `eas credentials` or on the next build. In Xcode, auto-signing handles this. For manual CI pipelines: add a certificate expiry check to your monitoring.

---

## ⚫ Interview Questions + Answers

**Q1: What is an iOS Distribution Certificate?**
A1: A Distribution Certificate is issued by Apple and proves your identity as an iOS developer. It's used to cryptographically sign your app for distribution via TestFlight or the App Store. Apple allows max 2 distribution certificates per developer account. The certificate + private key is exported as a `.p12` file. Expires after 1 year — must renew annually. Without it, you cannot submit builds.

**Q2: What is a Provisioning Profile?**
A2: A provisioning profile links three things: (1) your App ID (bundle identifier), (2) your distribution certificate, (3) allowed devices (for development/ad hoc) or unlimited (App Store). Download as `.mobileprovision`. Types: Development (specific devices), Ad Hoc (up to 100 UDIDs), App Store (for submission). Must be regenerated when the certificate changes.

**Q3: What is Xcode's "Automatic Signing"?**
A3: Xcode's automatic signing manages certificates and provisioning profiles for you. Enable in Project → Signing & Capabilities → "Automatically manage signing". Xcode creates/renews certificates and provisioning profiles as needed. Works well for individual developers. For teams (shared CI), manual signing or EAS Build is more reliable — automatic signing requires a logged-in Apple account on the build machine.

**Q4: What is EAS Credentials and how does it help?**
A4: EAS (Expo Application Services) Credentials is a vault that stores your iOS certificates and provisioning profiles encrypted on Expo's servers. During `eas build`, EAS automatically uses the stored credentials to sign your iOS build — no need for a Mac with Xcode locally. Run `eas credentials` to manage them: view, download, upload new, or let EAS auto-generate from your Apple account via App Store Connect API key.

**Q5: What is the difference between App Store and Ad Hoc distribution?**
A5: **App Store**: signed for unlimited users via App Store (or TestFlight external testing). Submitted to App Store Connect. Requires Apple review for public distribution. **Ad Hoc**: signed for up to 100 specific device UDIDs registered in your Apple Developer account. Installed directly (no App Store). Used for beta testing with known testers. Testers must register their device UDID before you create the profile. For most teams: use TestFlight (App Store profile, internal testing, no UDID needed) instead of Ad Hoc.

---

## 📊 Visual Diagram

```
iOS SIGNING CHAIN:
──────────────────────────────────────────────────────

  Apple Certificate Authority (root of trust)
            │
            ▼
  Distribution Certificate (.p12)
  "This developer account (TEAM_ID) is verified"
  Expires: 1 year
            │
            ▼
  Provisioning Profile (.mobileprovision)
  Links: Bundle ID (com.company.app)
       + Distribution Certificate
       + Devices (unlimited for App Store)
       + Entitlements (push, iCloud, etc.)
            │
            ▼
  Signed IPA
  = React Native bundle
    + iOS frameworks
    + Assets
    + Signed with Certificate
    + Embedded Provisioning Profile
            │
            ▼
  App Store Connect (iTunes Connect)
            │
            ▼
  TestFlight (beta) → App Store (public)

EAS BUILD FLOW (simplified):
  eas build --platform ios
    → EAS pulls credentials from vault
    → Runs xcodebuild on Mac cloud server
    → Signs IPA with your cert
    → Returns download URL for IPA
  eas submit --platform ios
    → Uploads IPA to App Store Connect
    → Triggers TestFlight processing
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Certificate | Cryptographic identity proof | Cryptographic identity proof |
| .p12 | Certificate + private key file | Certificate + private key file |
| Provisioning Profile | Links app + cert + devices | App + cert + devices को link |
| Bundle Identifier | Unique app ID (com.x.y) | App का unique ID |
| CSR | Certificate Signing Request | Certificate के लिए request file |
| Ad Hoc | Distribution to specific devices | Specific devices पर distribution |
| TestFlight | Apple's beta testing platform | Apple का beta testing platform |
| Entitlements | App capabilities (push, iCloud) | App capabilities |
| buildNumber | iOS build version (must increment) | हर upload पर बढ़ने वाला number |

---

## ⚡ 3-Line Summary
**English:**
1. iOS signing requires: Distribution Certificate (your identity, from Apple, 1-year expiry) + Provisioning Profile (links bundle ID + cert + devices).
2. Easiest path: EAS Build — logs into Apple account via API key, manages certs + profiles automatically, builds on Mac cloud (works on Windows/Linux too).
3. Critical numbers: `buildNumber` must increment for every TestFlight/App Store upload; `CFBundleShortVersionString` (version) is user-visible ("1.2.0").

**Hindi:**
1. iOS signing: Distribution Certificate (आपकी identity, Apple से, 1 year expiry) + Provisioning Profile (bundle ID + cert + devices link)।
2. आसान रास्ता: EAS Build — Apple account से login, certs + profiles automatically manage, Mac cloud पर build (Windows/Linux पर भी काम)।
3. Important: हर TestFlight/App Store upload पर `buildNumber` increment करना जरूरी।

---

## ➡️ Next Topic
**231. TestFlight Distribution** — Internal + external beta testing, review process।
