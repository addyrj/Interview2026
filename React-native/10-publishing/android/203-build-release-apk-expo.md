# 203. Build Release APK (Expo)
# हिंदी में: Expo से Release APK बनाना
# Platform: Android ✅ | iOS ❌ (iOS में IPA बनता है)

> Target: **Expo SDK 52 (React Native 0.76)** with `eas-cli` — check current docs — APIs change between SDKs and EAS CLI versions.

---

## 🔵 Simple Definition (English)
An **APK** is an installable Android file you can send on WhatsApp or install by tapping. With Expo you build it in the cloud using EAS Build with `"buildType": "apk"`. Good for testing; Play Store needs AAB (next topic).

## 🔵 सरल परिभाषा (Hindi)
**APK** एक installable Android file है जिसे WhatsApp पर भेजकर या tap करके install कर सकते हैं। Expo में EAS Build से cloud में `"buildType": "apk"` के साथ बनाते हैं। Testing के लिए अच्छा है; Play Store को AAB चाहिए (अगला topic)।

---

## 🔴 Problem it Solves
- Testers/QA/clients need a real installable app without Play Store review.
- Expo Go cannot run custom native code or show real icon/splash.
- No Android Studio/Mac needed: EAS builds in the cloud.

## 🔴 यह क्यों बना? (Hindi)
- Testers/QA/client को Play Store review के बिना असली app चाहिए।
- Expo Go में custom native code और असली icon/splash नहीं चलते।
- Android Studio की ज़रूरत नहीं; EAS cloud में build करता है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → Install CLI:           npm install -g eas-cli
Step 2 → Login:                 eas login        (check with: eas whoami)
Step 3 → Configure project:     eas build:configure   (creates eas.json)
Step 4 → Add a profile with android.buildType = "apk" in eas.json
Step 5 → Set unique android.package in app.json (e.g. com.mycompany.foodapp)
Step 6 → Run:                   eas build --platform android --profile preview
Step 7 → First time: EAS asks "Generate a new Android Keystore?" → answer Yes
Step 8 → Build queued on EAS servers (watch progress in terminal / expo.dev)
Step 9 → On finish you get a URL + QR code to download the .apk
Step 10 → Install on phone (allow "Install unknown apps") or: adb install app.apk
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → CLI install:  npm install -g eas-cli
Step 2 → Login:        eas login
Step 3 → Configure:    eas build:configure  (eas.json बनता है)
Step 4 → eas.json में profile बनाओ जिसमें android.buildType = "apk"
Step 5 → app.json में unique android.package डालो
Step 6 → चलाओ:         eas build --platform android --profile preview
Step 7 → पहली बार keystore पूछे तो "Yes" (EAS generate करेगा)
Step 8 → Build EAS servers पर queue होता है
Step 9 → ख़त्म होने पर download URL + QR code मिलता है
Step 10 → Phone में install करो (Unknown sources allow) या adb install
```

**Console screens (described):**
- **Terminal:** After the command you see "Compressing project files", "Uploading to EAS Build", then a link like `https://expo.dev/accounts/<you>/projects/<slug>/builds/<id>`.
- **expo.dev build page:** Top shows status chip (In queue / In progress / Finished in green). Below: platform Android, profile `preview`, SDK version, app version, a big **Install** button with QR code and an **Artifact** download link (`.apk`). A **Logs** section lists phases: Spin up build environment, Install dependencies, Prebuild, Run gradlew, Upload artifact.

---

## 🟡 Real World Example
A startup building a Swiggy-like app sends a `preview` APK to 10 delivery partners over WhatsApp every Friday for field testing, while the Play Store version stays untouched.

## 🟡 Real Example Hindi mein
Swiggy जैसा app बना रही startup हर शुक्रवार `preview` APK 10 delivery partners को WhatsApp पर भेजती है ताकि field testing हो, और Play Store वाला version वैसा ही रहता है।

---

## 💻 Code Example — Basic
`eas.json`:
```json
{
  "cli": { "version": ">= 12.0.0" },
  "build": {
    "preview": {
      "distribution": "internal",
      "android": { "buildType": "apk" }
    },
    "production": {
      "autoIncrement": true
    }
  }
}
```
```bash
# Build APK for testers
eas build --platform android --profile preview
```

## 💻 Code Example — Advanced
Local build (needs Android SDK + Java on your machine) and install via adb, with env vars:
```json
{
  "cli": { "version": ">= 12.0.0", "appVersionSource": "remote" },
  "build": {
    "preview": {
      "distribution": "internal",
      "channel": "preview",
      "env": { "API_URL": "https://staging.api.foodapp.in" },
      "android": { "buildType": "apk", "gradleCommand": ":app:assembleRelease" }
    }
  }
}
```
```bash
# Build on your own machine instead of EAS servers (needs Android SDK)
eas build --platform android --profile preview --local
# Wait-free: do not block terminal
eas build -p android --profile preview --no-wait
# List recent builds
eas build:list --platform android --limit 5
# Install the downloaded APK on a connected device
adb install -r ./build-123.apk        # -r = replace existing app
# Check device is connected first
adb devices
```
**Error handling:** if build fails, open the failed build's "Run gradlew" log phase; most failures are version conflicts or missing `android.package`. Rerun after fixing; `eas build --clear-cache` clears stale caches.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Installable artifact | `.apk` (direct install) | `.ipa` (needs signing + device registration or TestFlight) |
| Share outside store | Anyone with the file | Only registered devices (ad hoc) or TestFlight |
| Account needed | None for APK | Apple Developer ($99/yr) |
| EAS key | `android.buildType: "apk"` | `distribution: internal` + device UDIDs |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// eas build -p android --profile preview   (cloud, no Android Studio)
```
CLI way:
```bash
# Inside android/ folder of a bare project
./gradlew assembleRelease
# Output: android/app/build/outputs/apk/release/app-release.apk
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Uploading the APK to Play Store (new apps need AAB).
✅ Correct: Use APK for testing only; AAB for store.

❌ Mistake 2: Forgetting `buildType: "apk"` → default `preview` builds AAB which cannot be installed directly.
✅ Correct: Set `"buildType": "apk"`.

❌ Mistake 3: Using the debug keystore for production.
✅ Correct: Let EAS manage keystore; back it up with `eas credentials`.

❌ Mistake 4: Pointing to localhost API in release.
✅ Correct: Use a public/staging URL via `env`.

---

## 🧠 Tricky Interview Question
"You built an APK with the `development` profile and it shows 'No development servers found' on launch. Why?"

Answer: `developmentClient: true` builds include the dev launcher UI and need Metro. For a standalone app use a `preview`/`production` profile without `developmentClient`.

---

## ⚫ Interview Questions + Answers
Q1: APK vs AAB?
A1: APK is a full installable package; AAB is a publishing format Google Play converts into optimized per-device APKs.

Q2: Where do I get the APK from EAS?
A2: The build page on expo.dev or the URL printed in terminal.

Q3: Who holds the keystore?
A3: EAS stores it; view/download with `eas credentials`.

Q4: Can I build without EAS?
A4: `eas build --local` or `npx expo prebuild` + `./gradlew assembleRelease`.

Q5: What does `distribution: internal` mean?
A5: Build is for direct sharing (link/QR), not store submission.

---

## 🔷 When to Use + When Not to Use
✅ Use when: QA, demo to clients, sideloading to devices.

❌ Avoid when: publishing to Play Store (use AAB), or distributing publicly (security/update issues).

---

## 📊 Visual Diagram
```
 Your code ─► eas build ─► EAS cloud (Gradle assembleRelease, signs with keystore)
                                   │
                                   ▼
                         app.apk + install link/QR
                                   │
                  WhatsApp / adb install / expo.dev ─► Tester's phone
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| APK | Installable Android package | Install होने वाली Android file |
| EAS Build | Expo cloud build service | Expo की cloud build service |
| Profile | Named build config | नाम वाला build config |
| Sideload | Install outside store | Store के बाहर install |
| adb | Android Debug Bridge | Android debug tool |

---

## ⚡ 3-Line Summary
English: Set `buildType: "apk"` in an eas.json profile and run `eas build -p android --profile preview`.
Download the APK from the link and install it for testing.
Use AAB for Play Store.

Hindi: eas.json profile में `buildType: "apk"` रखो और `eas build -p android --profile preview` चलाओ।
Link से APK download करके testing के लिए install करो।
Play Store के लिए AAB use करो।

---

## ➡️ Next Topic
**204. Build Release AAB (Expo)** — Play Store के लिए सही format।
