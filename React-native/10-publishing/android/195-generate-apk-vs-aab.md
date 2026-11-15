# 195. Generate APK vs AAB
# हिंदी में: APK और AAB कैसे बनाएँ (Step by Step)
# Platform: Android ✅ | iOS ❌ (iOS में .ipa बनता है)

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs). EAS/Play Console के नाम और menu बदल सकते हैं। इस note में commands चलाए नहीं गए (not run).

---

## 🔵 Simple Definition (English)
This topic is the **how-to**: building an **APK** (installable file for testing/sideloading) and an **AAB** (Android App Bundle — the file you upload to Play Store). You can build them locally with Gradle or in the cloud with EAS Build.

## 🔵 सरल परिभाषा (Hindi)
यह topic **कैसे बनाएँ** के बारे में है: **APK** (testing/sideload के लिए install होने वाली file) और **AAB** (Android App Bundle — Play Store पर upload करने वाली file)। इन्हें Gradle से local या EAS Build से cloud में बना सकते हैं।

---

## 🔴 Problem it Solves
```
❌ "Build कैसे बनाऊँ?" — Gradle/EAS/Android Studio के कई रास्ते, भ्रम
❌ Play Store AAB माँगता है, दोस्त/QA को APK चाहिए
❌ Wrong build type/profile से गलत file बन जाती है
यह guide:
  ✅ हर target के लिए सही command और output path
```

## 🔴 यह क्यों बना? (Hindi)
```
QA को APK चाहिए (सीधा install), Play Store को AAB।
दोनों के commands और output अलग हैं — यह guide वही साफ़ करती है।
```

---

## 🟢 How it Works — Step by Step
```
LOCAL (Bare RN / prebuild):
Step 1 → Keystore + signing config तैयार (191 देखो)
Step 2 → version bump: versionCode/versionName (Expo: app.json android.versionCode)
Step 3 → cd android && ./gradlew clean (ज़रूरत हो तो)
Step 4 → APK: ./gradlew assembleRelease
Step 5 → AAB: ./gradlew bundleRelease
Step 6 → Output ढूँढो: app/build/outputs/apk/release/ या .../bundle/release/
Step 7 → APK phone में: adb install app-release.apk
CLOUD (EAS):
Step 8 → npm i -g eas-cli ; eas login ; eas build:configure
Step 9 → eas.json में profile (apk vs app-bundle)
Step 10 → eas build -p android --profile preview (APK) / production (AAB)
Step 11 → Build पूरा होने पर link से download/ QR से install
```

## 🟢 कैसे काम करता है? (Hindi)
```
assembleRelease → APK बनता है (सब architectures + resources एक file में)।
bundleRelease → AAB बनता है (Play Store बाद में हर device के लिए छोटा APK निकालता है)।
EAS ये सब cloud में चलाता है, आपके laptop पर Android SDK नहीं चाहिए।
```

---

## 🟡 Real World Example
**Swiggy-जैसी टीम:** हर PR पर CI **APK** (preview) बनाकर Slack में link भेजता है ताकि QA/PM install करके देखें। Release के दिन CI **AAB** बनाकर Play Console की internal testing track पर upload करता है। Delivery partners की app के लिए कभी-कभी सीधा APK (sideload) भी बाँटा जाता है, जहाँ Play Store ठीक नहीं बैठता।

## 🟡 Real Example Hindi mein
हर PR पर CI APK बनाकर QA को देता है; release पर AAB बनाकर Play Console पर upload करता है।

---

## 💻 Code Example — Basic
```bash
# ---------- LOCAL (Android SDK + JDK 17 installed; RN 0.76 के लिए JDK 17) ----------
cd android                                   # android folder

./gradlew clean                              # पुराना build साफ़ (optional)
./gradlew assembleRelease                    # APK बनाओ (release signing config के साथ)
ls app/build/outputs/apk/release/            # → app-release.apk

./gradlew bundleRelease                      # AAB बनाओ
ls app/build/outputs/bundle/release/         # → app-release.aab

# APK को connected phone/emulator में install
adb devices                                  # device दिख रहा है?
adb install -r app/build/outputs/apk/release/app-release.apk   # -r = reinstall/replace

# AAB को local test करना हो तो bundletool (Google का tool)
# bundletool build-apks --bundle=app-release.aab --output=app.apks --mode=universal \
#   --ks=upload-keystore.jks --ks-key-alias=upload
# bundletool install-apks --apks=app.apks
```

## 💻 Code Example — Advanced
```jsonc
// ---------- eas.json (EAS Build) — JSON, comments सिर्फ समझाने को ----------
{
  "cli": { "version": ">= 12.0.0", "appVersionSource": "remote" },   // EAS CLI min version
  "build": {
    "preview": {
      "distribution": "internal",                // Play Store के बिना बाँटो
      "android": { "buildType": "apk" },         // APK output
      "env": { "API_URL": "https://staging.example.com" }
    },
    "production": {
      "autoIncrement": true,                     // versionCode खुद बढ़े (remote version source)
      "android": { "buildType": "app-bundle" },  // AAB output (production का default भी यही)
      "env": { "API_URL": "https://api.example.com" }
    }
  },
  "submit": {
    "production": {
      "android": {
        "serviceAccountKeyPath": "./play-service-account.json",  // Play API key (git में नहीं)
        "track": "internal"                       // पहले internal testing
      }
    }
  }
}
```
```bash
# ---------- EAS commands ----------
npm i -g eas-cli                                  # install
eas login                                         # Expo account login
eas build:configure                               # eas.json बनाता है
eas build -p android --profile preview            # APK → build page से download/QR
eas build -p android --profile production         # AAB
eas build -p android --profile production --local # अपनी मशीन पर build (Android SDK चाहिए)
eas submit -p android --latest                    # latest AAB Play Console पर भेजो

# ---------- GitHub Actions (संक्षेप) ----------
# - uses: expo/expo-github-action@v8
#   with: { eas-version: latest, token: ${{ secrets.EXPO_TOKEN }} }
# - run: eas build -p android --profile production --non-interactive
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Output | `.apk` (testing) / `.aab` (store) | `.ipa` (store/TestFlight), `.app` (simulator) |
| Direct install | APK किसी भी phone में (unknown sources allow) | .ipa सिर्फ registered devices/TestFlight से |
| Local build tool | Gradle (Windows/Mac/Linux) | Xcode (सिर्फ macOS) |
| Store format | AAB अनिवार्य (नए apps, Aug 2021 से) | .ipa upload via Xcode/Transporter/EAS |
| Cloud build | EAS Android | EAS iOS (Apple account चाहिए) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
eas build -p android --profile preview      # APK
eas build -p android --profile production   # AAB
# Local alternative: npx expo prebuild --platform android && cd android && ./gradlew bundleRelease
```
CLI way:
```bash
cd android && ./gradlew assembleRelease     # APK
cd android && ./gradlew bundleRelease       # AAB
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Play Store पर APK upload करने की कोशिश (नए apps में नहीं चलेगा)
✅ Correct: AAB upload

❌ Mistake 2: `versionCode` नहीं बढ़ाया → "Version code already used"
✅ Correct: हर upload पर बढ़ाओ (EAS `autoIncrement`)

❌ Mistake 3: EAS पर `preview` profile में `buildType` नहीं दिया → AAB बना, phone में install नहीं हुआ
✅ Correct: `"buildType": "apk"`

❌ Mistake 4: JDK version mismatch (build fail)
✅ Correct: RN 0.76 के लिए JDK 17 (check current docs)

❌ Mistake 5: `assembleDebug` को "release" समझकर बाँटना
✅ Correct: `assembleRelease`

---

## 🧠 Tricky Interview Question
`bundleRelease` से बनी `.aab` को क्या आप सीधा phone में install कर सकते हैं?

Answer: नहीं। AAB publishing format है, installable नहीं। Play Store इससे device-specific APKs बनाता है। Local test के लिए `bundletool` से `.apks` बनाकर install करो, या सीधा `assembleRelease` से APK बनाओ। EAS पर `preview` profile में `buildType: apk` रखो।

---

## ⚫ Interview Questions + Answers
Q1: Universal APK क्या है?
A1: एक APK जिसमें सारे ABIs/densities/languages होते हैं — बड़ा, पर हर device पर चलता है। AAB से Play device-specific छोटा APK देता है।

Q2: `versionCode` और `versionName`?
A2: versionCode integer (हर upload पर बढ़ना ज़रूरी, Play इसे compare करता है); versionName user को दिखने वाला string ("1.2.3")।

Q3: APK छोटा कैसे करें?
A3: AAB use, `enableProguardInReleaseBuilds`/R8, `shrinkResources`, Hermes, ABI splits, images compress, unused libraries हटाओ।

Q4: EAS local build कब?
A4: Build minutes बचाने या custom environment के लिए: `eas build --local`।

Q5: Output file कहाँ मिलती है?
A5: `android/app/build/outputs/apk/release/` और `.../bundle/release/`; EAS में build page पर download link।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- APK: QA/internal sharing, sideloading
- AAB: Play Store release

❌ Avoid when:
- Debug APK बाँटना
- AAB को direct share करना

---

## 📊 Visual Diagram
```
 Source ─► Gradle/EAS ─┬─► assembleRelease ─► app-release.apk ─► adb install / share
                       └─► bundleRelease  ─► app-release.aab ─► Play Console ─► device APKs
```

---

## 🖥️ Console Screens (वर्णन)
```
EAS (expo.dev) → Project → Builds: सबसे ऊपर नई build row — status badge ("In queue" → "In progress" → "Finished"),
  Finished होने पर दाईं ओर "Install" (QR code popup) और "Download" बटन।
Play Console → Test and release → Testing → Internal testing → "Create new release":
  "App bundles" बॉक्स में AAB drag-and-drop; नीचे release name और release notes टेक्स्ट बॉक्स।
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| APK | Installable Android package | Install होने वाली file |
| AAB | Publishing bundle | Store के लिए bundle |
| assembleRelease | Gradle APK task | APK बनाने का task |
| bundleRelease | Gradle AAB task | AAB बनाने का task |
| EAS Build | Expo cloud builds | Expo का cloud build |
| versionCode | Integer build number | Build नंबर |

---

## ⚡ 3-Line Summary
English: Use `assembleRelease` or EAS `apk` profile for APK, `bundleRelease` or EAS `app-bundle` for AAB.
Bump versionCode every upload; Play needs AAB.
AAB cannot be installed directly.

Hindi: APK के लिए `assembleRelease` या EAS `apk` profile; AAB के लिए `bundleRelease` या `app-bundle`।
हर upload पर versionCode बढ़ाओ; Play को AAB चाहिए।
AAB सीधा install नहीं होता।

---

## ➡️ Next Topic
**196. APK vs AAB — Difference** — दोनों में असली अंतर और कब कौन सा।

---
