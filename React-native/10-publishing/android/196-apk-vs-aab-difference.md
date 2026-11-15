# 196. APK vs AAB — Difference
# हिंदी में: APK और AAB में अंतर
# Platform: Android ✅ | iOS ❌

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs). Play Store size limits और नियम बदल सकते हैं (check current docs). इस note में कोई command चलाया नहीं गया (not run).

---

## 🔵 Simple Definition (English)
**APK** (Android Package) is a ready-to-install file containing everything for all devices. **AAB** (Android App Bundle) is a publishing format you upload to Google Play; Play uses it to generate smaller, device-specific APKs (split APKs) for each user. You cannot install an AAB directly.

## 🔵 सरल परिभाषा (Hindi)
**APK** (Android Package) सीधे install होने वाली file है, जिसमें सारे devices के लिए सब कुछ होता है। **AAB** (Android App Bundle) Google Play पर upload करने का format है; Play इससे हर user के device के हिसाब से छोटे **split APKs** बनाता है। AAB को सीधा install नहीं कर सकते।

---

## 🔴 Problem it Solves
```
APK की समस्या:
  ❌ Universal APK में सारे CPU architectures (arm64, armeabi, x86), सारी screen densities, सारी भाषाएँ
  ❌ User को 80 MB download, जबकि उसके phone को 40 MB ही चाहिए
  ❌ Multiple APKs का versionCode/manage मुश्किल
AAB:
  ✅ Play हर device के लिए सिर्फ ज़रूरी हिस्से देता है (~15-30% छोटा, app पर निर्भर)
  ✅ Play Feature Delivery / Asset Delivery (on-demand modules)
  ✅ Play App Signing के साथ सुरक्षित re-signing
```

## 🔴 यह क्यों बना? (Hindi)
```
भारत में कम storage और slow internet वाले phones बहुत हैं।
AAB से हर user को सिर्फ अपने device का हिस्सा मिलता है — download छोटा।
इसलिए Google ने नए apps के लिए AAB अनिवार्य किया (Aug 2021)।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → आप bundleRelease से AAB बनाते हो (upload key से signed)
Step 2 → Play Console पर upload
Step 3 → Play AAB से modules/splits निकालता है: base + ABI split + density split + language split
Step 4 → User का device बताता है: arm64, xxhdpi, Hindi
Step 5 → Play उस device के लिए सिर्फ base.apk + config splits देता है
Step 6 → Google अपनी app signing key से हर split sign करता है
Step 7 → Install: कई split APKs मिलकर एक app
APK path: build → एक universal APK → सीधे share/sideload
```

## 🟢 कैसे काम करता है? (Hindi)
```
AAB = सामान का पूरा डिब्बा (blueprint)।
Play = दुकान जो हर ग्राहक को उसके नाप का सामान भेजती है।
APK = तैयार पूरा पैकेज जो सबको एक जैसा जाता है।
```

---

## 🟡 Real World Example
**Zomato/Swiggy** Play Store पर AAB देते हैं, इसलिए कम-storage वाले Redmi/Realme phone वाले user को छोटा download मिलता है। वही टीम QA और बाहरी delivery partners को **APK** बाँटती है, क्योंकि APK सीधे install हो जाता है। चीन/non-Play stores (Huawei, Samsung Galaxy Store के कुछ rules) में कई बार APK माँगा जाता है।

## 🟡 Real Example Hindi mein
Play Store पर AAB (छोटा download), QA/partners को APK (सीधा install), कुछ non-Play stores में APK।

---

## 💻 Code Example — Basic
```bash
# दोनों बनाओ और size compare करो (Bare RN)
cd android
./gradlew assembleRelease          # universal APK
./gradlew bundleRelease            # AAB

# size देखो
ls -lh app/build/outputs/apk/release/app-release.apk
ls -lh app/build/outputs/bundle/release/app-release.aab

# AAB से device-specific APK निकालकर देखो (bundletool, Google का open-source tool)
# bundletool get-size total --apks=app.apks      # अनुमानित download size
```

## 💻 Code Example — Advanced
```groovy
// ---------- android/app/build.gradle — AAB splits और APK ABI splits ----------
android {
    bundle {                                         // AAB settings
        language { enableSplit = true }              // भाषा-आधारित splits (default true)
        density  { enableSplit = true }              // screen density splits
        abi      { enableSplit = true }              // CPU architecture splits
    }

    // सिर्फ APK (assembleRelease) के लिए ABI splits — size घटाने को
    splits {
        abi {
            reset()                                  // पुरानी list साफ़
            enable true                              // splits चालू
            include "armeabi-v7a", "arm64-v8a"       // ज़रूरी architectures
            universalApk false                       // true = अलग से universal भी
        }
    }
}
// Hermes + R8 दोनों के साथ ये और छोटा होगा।
// ध्यान: ABI splits में हर APK का versionCode अलग रखना पड़ता है (Play पर APKs के लिए);
// AAB में यह सब Play खुद संभालता है — इसलिए AAB आसान है।
```
```bash
# Expo/EAS में चुनाव
# eas.json:  "android": { "buildType": "apk" }         → APK
#            "android": { "buildType": "app-bundle" }  → AAB
```

---

## 📱 Android vs iOS Difference
| Feature | APK / AAB (Android) | iOS (.ipa) |
|---------|---------------------|------------|
| Device-specific delivery | AAB → Play split APKs | App Thinning (slicing) — Apple खुद करता है |
| Direct install | APK ✅ / AAB ❌ | .ipa सिर्फ provisioning/TestFlight से |
| Store upload | AAB (Play) | .ipa (App Store Connect) |
| Size limit | Base module 200MB compressed (Play limits, check current docs) | Over-the-air cellular limit settings (docs देखो) |
| Signing | Play App Signing re-sign | Apple signs distribution |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
eas build -p android --profile production   # buildType: app-bundle → AAB
eas build -p android --profile preview      # buildType: apk → APK
```
CLI way:
```bash
cd android && ./gradlew bundleRelease       # AAB
cd android && ./gradlew assembleRelease     # APK
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: सोचना कि AAB user के phone में install होता है
✅ Correct: Play AAB से split APKs बनाकर देता है

❌ Mistake 2: Play पर APK upload (नए app में reject)
✅ Correct: AAB

❌ Mistake 3: AAB बनाकर WhatsApp पर दोस्त को भेजना
✅ Correct: APK भेजो (या bundletool से universal APK)

❌ Mistake 4: ABI splits के साथ एक ही versionCode
✅ Correct: Play पर AAB use करो, APK splits के लिए अलग versionCode

❌ Mistake 5: Native libs (x86) हटाना बिना emulator test
✅ Correct: arm64 + armeabi-v7a (devices), x86 सिर्फ emulator के लिए

---

## 🧠 Tricky Interview Question
App का universal APK 60 MB है। Play पर AAB upload करने पर user का download कितना होगा — हमेशा आधा?

Answer: नहीं, "हमेशा" कुछ नहीं। Savings app के content पर निर्भर: अगर app में बहुत native libs (कई ABIs) और बहुत सारी भाषाएँ/densities के resources हैं तो बचत ज़्यादा (कभी 20-50%)। अगर app पहले से सिर्फ JS + सिर्फ एक ABI है तो बचत कम। असली अनुमान: Play Console → App bundle explorer / bundletool `get-size total`। AAB में एक user के लिए base + config splits मिलते हैं, पर कुल installed size में असर इतना बड़ा नहीं हो सकता जितना download size में।

---

## ⚫ Interview Questions + Answers
Q1: AAB क्यों अनिवार्य हुआ?
A1: छोटे downloads, dynamic features और Play App Signing के साथ बेहतर सुरक्षा; Google ने Aug 2021 से नए apps के लिए अनिवार्य किया।

Q2: Split APKs क्या हैं?
A2: Base APK + config APKs (ABI, density, language) जो मिलकर एक app बनाते हैं; Play इन्हें हर device के लिए चुनता है।

Q3: AAB local में कैसे चलाएँ?
A3: `bundletool build-apks` + `install-apks`, या Play internal testing track से install।

Q4: कब APK ही चाहिए?
A4: Sideload/QA, non-Play stores, enterprise distribution, Firebase App Distribution (APK/AAB दोनों support)।

Q5: AAB में on-demand features कैसे?
A5: Dynamic feature modules (Play Feature Delivery) — RN में सामान्य नहीं, native modules में संभव।

---

## 🔷 When to Use + When Not to Use
✅ Use AAB when:
- Google Play Store release
- App size/download कम करना हो

✅ Use APK when:
- QA/internal sharing, sideload, non-Play distribution

❌ Avoid when:
- AAB को सीधे install के लिए देना
- Debug APK production में

---

## 📊 Visual Diagram
```
 APK (universal)                         AAB
 ┌────────────────────┐          ┌──────────────────────────┐
 │ arm64 + armv7 + x86│          │ base + ABI + density +   │
 │ all densities/langs│          │ language modules         │
 └─────────┬──────────┘          └────────────┬─────────────┘
           │ install                           │ upload to Play
           ▼                                   ▼
      every phone same                Play builds per-device splits
      (bigger)                        (smaller download)
```

---

## 🖥️ Console Screens (वर्णन)
```
Play Console → App → "Test and release" → "App bundle explorer":
  ऊपर version dropdown, बीच में table: device/ABI के हिसाब से "Download size" और "Install size" की list;
  बाईं ओर tabs: "Downloads", "App signing" — इससे अनुमान मिलता है कि AAB से कितनी बचत हुई।
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| APK | Installable package | Install होने वाली file |
| AAB | Upload bundle | Upload का bundle |
| Split APK | Device-specific parts | Device के हिसाब से हिस्से |
| ABI | CPU architecture | CPU प्रकार |
| bundletool | Google's AAB tool | AAB का tool |
| Universal APK | One APK for all | सबके लिए एक APK |

---

## ⚡ 3-Line Summary
English: APK installs directly; AAB is for Play, which creates smaller device-specific APKs.
Play requires AAB for new apps; use APK for QA and sideloading.
AAB cannot be installed directly; use bundletool to test it locally.

Hindi: APK सीधा install होता है; AAB Play के लिए है, जो छोटे device-specific APKs बनाता है।
नए apps में Play को AAB चाहिए; QA/sideload के लिए APK।
AAB सीधा install नहीं होता; local test के लिए bundletool।

---

## ➡️ Next Topic
**197. app.json + app.config.js Setup** — package name, version, permissions जैसी config सही तरह सेट करना।

---
