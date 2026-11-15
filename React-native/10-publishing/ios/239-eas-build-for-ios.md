# 239. EAS Build for iOS
# हिंदी में: iOS के लिए EAS Build — Cloud में IPA बनाना
# Platform: Android ❌ | iOS ✅ (Android का equivalent: `eas build -p android`)

> Targets: **Expo SDK 52 (check current docs — APIs change between SDKs)**, React Native 0.76, eas-cli recent version. `eas.json` keys बदल सकती हैं — हमेशा docs देखो।

---

## 🔵 Simple Definition (English)
**EAS Build** is Expo's cloud service that compiles your React Native app into a signed iOS `.ipa` file on a Mac in the cloud. You do not need a Mac or Xcode on your own machine. It also manages certificates and provisioning profiles for you.

## 🔵 सरल परिभाषा (Hindi)
**EAS Build** Expo की cloud service है जो आपके React Native app को cloud के Mac पर compile करके signed iOS `.ipa` file बनाती है। आपके पास खुद का Mac या Xcode होना ज़रूरी नहीं। Certificates और provisioning profiles भी यही manage करती है।

---

## 🔴 Problem it Solves
- iOS app बनाने के लिए पहले **Mac + Xcode + certificates + provisioning profile** ज़रूरी था (topic 230 देखो)।
- Windows/Linux developer iOS build नहीं कर सकता था।
- Signing की गड़बड़ी ("No matching provisioning profile") में घंटे बर्बाद होते थे।
- Team में हर developer के Mac पर अलग Xcode version = अलग build result।

## 🔴 यह क्यों बना? (Hindi)
iOS build सिर्फ Apple hardware पर हो सकती है। EAS Build ने यह काम cloud में ले लिया: एक command, same environment, auto signing। Team में सबका build reproducible रहता है और CI/CD (GitHub Actions) से जुड़ सकता है।

---

## 🟢 How it Works — Step by Step
1. `eas-cli` install करो और `eas login` करो।
2. `eas build:configure` से `eas.json` बनाओ।
3. `app.json` में `ios.bundleIdentifier` set करो (unique, reverse-domain).
4. `eas build -p ios --profile production` चलाओ।
5. पहली बार EAS Apple Developer account (Apple ID + 2FA) माँगेगा और distribution certificate + provisioning profile बना देगा।
6. Project upload होता है → queue → Mac VM पर `pod install` + Xcode archive → `.ipa`.
7. Build URL मिलता है; `eas submit` से App Store Connect पर भेजो (topic 241)।

```
Step 1 → npm i -g eas-cli && eas login
Step 2 → eas build:configure        (eas.json बनता है)
Step 3 → bundleIdentifier set in app.json
Step 4 → eas build -p ios --profile production
Step 5 → Apple login + auto credentials (cert + profile)
Step 6 → Cloud Mac: pod install → xcodebuild archive → .ipa
Step 7 → Download link / eas submit → TestFlight
```

## 🟢 कैसे काम करता है? (Hindi)
1. `eas-cli` install करके login करो।
2. `eas build:configure` से `eas.json` बनता है।
3. `app.json` में bundle identifier डालो।
4. `eas build -p ios --profile production` चलाओ।
5. पहली बार Apple ID + 2FA देना पड़ता है; EAS certificate और profile खुद बना देता है।
6. Cloud Mac पर code compile होकर `.ipa` बनती है।
7. Link से download करो या सीधे `eas submit` से TestFlight भेजो।

**Console/Terminal screens (screenshot description):**
- Terminal पर पहले "Select a platform / Log in to your Apple Developer account" prompt आता है; Apple ID, password, फिर 6-digit 2FA code पूछता है।
- Prompt: "Generate a new Apple Distribution Certificate? (Y/n)" — Y दबाओ।
- अंत में terminal एक `https://expo.dev/accounts/<you>/projects/<app>/builds/<id>` link print करता है। Web page पर progress bar (Queued → In progress → Finished) और "Install"/"Download" बटन दिखता है।

---

## 🟡 Real World Example
Think of **Swiggy-like** startup team: designers use Windows laptops, only one dev has a Mac. With EAS Build every PR on `main` triggers `eas build -p ios --profile preview`, and QA gets an install link. **Paytm**-style fintech apps use `production` profile with fixed build image so that release builds are identical each time.

## 🟡 Real Example Hindi mein
Swiggy जैसी team में ज़्यादातर Windows laptops हैं और सिर्फ एक के पास Mac है। EAS Build से हर PR पर iOS preview build बनती है और QA को install link मिलता है। Paytm जैसे fintech apps `production` profile से हर बार same environment में release build बनाते हैं।

---

## 💻 Code Example — Basic
```json
// eas.json — पूरी file (comments JSON में allowed नहीं, इसलिए नीचे explain किया है)
{
  "cli": { "version": ">= 12.0.0", "appVersionSource": "remote" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal"
    },
    "production": {
      "autoIncrement": true
    }
  },
  "submit": { "production": {} }
}
```
```bash
# eas-cli global install करो
npm install -g eas-cli
# Expo account में login
eas login
# project को EAS से link + eas.json बनाओ
eas build:configure
# iOS production build शुरू करो (cloud में)
eas build --platform ios --profile production
```
नोट: `developmentClient` = dev build (expo-dev-client), `internal` = Apple ad-hoc distribution (registered devices), `autoIncrement` = हर build पर buildNumber +1।

## 💻 Code Example — Advanced
```json
// app.json — iOS-specific config (Expo SDK 52)
{
  "expo": {
    "name": "FoodApp",
    "slug": "foodapp",
    "version": "1.2.0",
    "ios": {
      "bundleIdentifier": "com.mycompany.foodapp",
      "supportsTablet": false,
      "infoPlist": {
        "NSCameraUsageDescription": "Scan QR code at restaurant table",
        "ITSAppUsesNonExemptEncryption": false
      }
    }
  }
}
```
```json
// eas.json — advanced iOS profiles
{
  "cli": { "appVersionSource": "remote" },
  "build": {
    "preview": {
      "distribution": "internal",
      "ios": { "simulator": false, "resourceClass": "m-medium" },
      "env": { "API_URL": "https://staging.api.example.com" }
    },
    "simulator": {
      "ios": { "simulator": true }
    },
    "production": {
      "autoIncrement": true,
      "ios": { "resourceClass": "m-medium" },
      "env": { "API_URL": "https://api.example.com" }
    }
  }
}
```
```bash
# Ad-hoc build के लिए test device register करो (UDID लेकर)
eas device:create
# Credentials देखो/manage करो (cert, profile, push key)
eas credentials --platform ios
# Build + successful होते ही auto submit to TestFlight
eas build --platform ios --profile production --auto-submit
# CI में non-interactive (Apple API key पहले से credentials में set होना चाहिए)
eas build --platform ios --profile production --non-interactive
```
Error handling: build fail हो तो web page पर "Run fastlane / Install pods" phase का log खोलो; ज़्यादातर errors = bundle ID mismatch, missing capability, या pod version issue।

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Output file | `.aab` / `.apk` | `.ipa` |
| Signing | Keystore (तुम खुद रख सकते हो) | Apple certificate + provisioning profile |
| Apple account | ज़रूरी नहीं | $99/year Apple Developer Program ज़रूरी |
| Local build | कहीं भी (Android SDK) | सिर्फ Mac + Xcode |
| Internal distribution | APK link से install | Ad-hoc: device UDID register करना पड़ता है |
| Version counter | `versionCode` | `buildNumber` (CFBundleVersion) |
| Simulator build | emulator APK | `ios.simulator: true` → `.app` |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Expo managed/prebuild: cloud build, auto credentials
eas build -p ios --profile production
```
CLI way:
```bash
# Bare React Native CLI: Mac पर manual
cd ios && pod install && cd ..          # native dependencies install
# फिर Xcode खोलो: Product → Archive → Distribute App
# या command line:
xcodebuild -workspace ios/App.xcworkspace -scheme App \
  -configuration Release archive -archivePath build/App.xcarchive
```
(Bare RN भी EAS Build इस्तेमाल कर सकता है अगर `ios/` folder repo में हो — EAS bare projects support करता है।)

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `bundleIdentifier` न डालना या App Store Connect के app से अलग रखना।
✅ Correct: `app.json` और App Store Connect में bundle ID बिल्कुल same रखो।

❌ Mistake 2: Production build में `distribution: "internal"` छोड़ देना — TestFlight/App Store को वह build नहीं चलेगी।
✅ Correct: Store के लिए `production` profile (default `store` distribution) इस्तेमाल करो।

❌ Mistake 3: Camera/Location जैसी permission का `infoPlist` description भूलना → App Store rejection।
✅ Correct: हर permission के लिए साफ़ usage description लिखो।

❌ Mistake 4: `ITSAppUsesNonExemptEncryption` न देना → हर upload पर export compliance सवाल।
✅ Correct: सिर्फ standard HTTPS use हो तो `false` set करो।

---

## 🧠 Tricky Interview Question
"मैंने Windows पर `eas build -p ios` चलाया, build success हुई, लेकिन iPhone पर install नहीं हो रही। क्यों?"

Answer: `.ipa` तभी install होता है जब (a) store distribution है → सिर्फ TestFlight/App Store से, या (b) internal/ad-hoc है → device का UDID provisioning profile में registered हो। Unregistered device पर install fail होगा। Fix: `eas device:create`, फिर build दोबारा करो (profile regenerate होती है)।

---

## ⚫ Interview Questions + Answers
Q1: EAS Build क्या है?
A1: Expo की cloud build service; Android/iOS binaries बनाती है, credentials manage करती है।

Q2: Mac के बिना iOS build कैसे बनाएं?
A2: `eas build -p ios` — build Expo के Mac servers पर होती है। Apple Developer account फिर भी चाहिए।

Q3: `preview` और `production` profile में क्या फर्क?
A3: preview = internal/ad-hoc distribution (registered devices); production = store distribution (TestFlight/App Store)।

Q4: `appVersionSource: "remote"` क्या करता है?
A4: Build number EAS server पर track होता है; `autoIncrement` से हर build पर अपने-आप बढ़ता है।

Q5: Local में EAS build चला सकते हैं?
A5: `eas build --local` से — लेकिन iOS के लिए Mac और Xcode चाहिए।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Mac नहीं है या team में consistent builds चाहिए।
- CI/CD से auto TestFlight upload करना है।
- Credentials manually संभालना नहीं चाहते।

❌ Avoid when:
- Build minutes/queue time का budget नहीं (free tier slow queue)।
- Company policy कहती है कि source code third-party cloud पर न जाए (तब `--local` / self-hosted Mac)।

---

## 📊 Visual Diagram
```
 Your Laptop (Win/Mac/Linux)          Expo Cloud (macOS VM)            Apple
 ┌───────────────┐  upload   ┌───────────────────────────┐
 │ eas build     │ ────────► │ npm ci → pod install      │
 │ -p ios        │           │ sign (cert + profile) ◄───┼──── Apple Dev account
 └───────────────┘           │ xcodebuild archive        │
        ▲                    └────────────┬──────────────┘
        │   build URL / .ipa              ▼
        └──────────────────────────   .ipa ──► eas submit ──► App Store Connect
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| IPA | iOS app package file | iOS app की file |
| Provisioning Profile | Links app + certificate + devices | app को चलाने की permission file |
| Distribution Certificate | Proves you are the signer | Apple की signing identity |
| Ad-hoc / internal | Install on registered devices only | सिर्फ registered phones पर |
| buildNumber | Internal build counter | build की गिनती |
| resourceClass | Size of cloud machine | cloud machine का size |

---

## ⚡ 3-Line Summary
English: EAS Build compiles your iOS app on Expo's cloud Macs.
It handles certificates, profiles and build numbers for you.
Use `production` profile for the store and `preview` for registered test devices.

Hindi: EAS Build आपके iOS app को Expo के cloud Mac पर build करता है।
Certificates, profiles और build number यह खुद संभालता है।
Store के लिए `production` और test devices के लिए `preview` profile इस्तेमाल करो।

---

## ➡️ Next Topic
**240. TestFlight — Complete Guide** — build बन गई, अब उसे testers तक पहुँचाने का Apple का official तरीका समझते हैं।
