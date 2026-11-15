# 194. Build Types (debug vs release)
# हिंदी में: Build Types — Debug बनाम Release
# Platform: Android ✅ | iOS ❌ (iOS में Debug/Release configurations अलग हैं — यहाँ Android फोकस)

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs). Commands और Hermes/R8 defaults version के साथ बदल सकते हैं। इस note में commands चलाए नहीं गए (not run).

---

## 🔵 Simple Definition (English)
A **build type** is a Gradle configuration that decides how the app is compiled. **Debug** = development build: debuggable, connects to Metro, no code shrinking, signed with the debug key. **Release** = production build: JS bundled inside the app, optimized (Hermes bytecode, R8/ProGuard), signed with your release/upload key.

## 🔵 सरल परिभाषा (Hindi)
**Build type** एक Gradle configuration है जो तय करती है कि app कैसे compile होगा। **Debug** = development build: debug हो सकता है, Metro से जुड़ता है, code shrink नहीं, debug key से sign। **Release** = production build: JS app के अंदर bundle, optimized (Hermes bytecode, R8/ProGuard), release/upload key से sign।

---

## 🔴 Problem it Solves
```
एक ही build से development और production दोनों नहीं चल सकते:
  ❌ Debug build धीमा, बड़ा, Metro server माँगता है
  ❌ Debug build में logs/dev menu/debuggable=true → security risk
  ❌ Release build में हर बार debugger नहीं चाहिए
Build types:
  ✅ Dev के लिए fast iteration (hot reload)
  ✅ Prod के लिए छोटा, तेज़, सुरक्षित APK/AAB
```

## 🔴 यह क्यों बना? (Hindi)
```
Development में आराम (hot reload, logs) चाहिए,
Production में speed और सुरक्षा।
दो अलग configurations से दोनों ज़रूरतें पूरी होती हैं।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Gradle में buildTypes { debug {...} release {...} } होते हैं
Step 2 → Debug: JS Metro server से load (dev server), DevSupport ON
Step 3 → Release: createBundleReleaseJsAndAssets से JS bundle बनता है, assets में embed
Step 4 → Hermes bytecode (default new RN) → तेज़ startup
Step 5 → minifyEnabled true → R8 code shrink/obfuscate (rules: proguard-rules.pro)
Step 6 → Signing: debug = debug.keystore, release = आपकी upload keystore
Step 7 → Commands: ./gradlew assembleDebug | assembleRelease | bundleRelease
Step 8 → Expo: eas build --profile development / preview / production
```

## 🟢 कैसे काम करता है? (Hindi)
```
Debug: app खुलते ही Metro से JS माँगता है (laptop चालू होना चाहिए)।
Release: JS पहले से app के अंदर, इंटरनेट/laptop नहीं चाहिए।
Release में code छोटा और obfuscate होता है।
```

---

## 🟡 Real World Example
**Zomato/Swiggy** टीम: developer रोज़ **debug** build से काम करती है (hot reload)। QA को **release-like "preview"/staging** build (internal APK) मिलता है — असली performance जाँचने के लिए। Play Store पर **release (production) AAB** जाता है। Staging और production अलग API URLs/App IDs के साथ चलते हैं ताकि दोनों एक phone पर install हो सकें।

## 🟡 Real Example Hindi mein
Developer debug से काम करता है, QA को release जैसा staging APK मिलता है, और Play Store पर production AAB जाता है। Staging का अलग applicationId होता है ताकि दोनों एक फोन में चलें।

---

## 💻 Code Example — Basic
```bash
# ---------- Bare RN / prebuild: Gradle commands ----------
cd android                                  # android folder में जाओ

./gradlew assembleDebug                     # Debug APK → app/build/outputs/apk/debug/app-debug.apk
./gradlew assembleRelease                   # Release APK → .../apk/release/app-release.apk (signing config ज़रूरी)
./gradlew bundleRelease                     # Release AAB → .../bundle/release/app-release.aab

# Device पर सीधे चलाना (RN CLI)
npx react-native run-android                # debug build + install + Metro
npx react-native run-android --mode release # release build device पर (बिना Metro)
# (पुराने RN versions में: --variant=release)

# Expo
npx expo run:android                        # local debug build (prebuild होने पर)
npx expo run:android --variant release      # local release build
```

## 💻 Code Example — Advanced
```groovy
// ---------- android/app/build.gradle — custom build types ----------
android {
    defaultConfig {
        applicationId "com.example.shop"            // prod application ID
    }
    signingConfigs {
        release {                                   // (ऊपर 191 में बताया gradle.properties approach)
            storeFile file(System.getenv("KEYSTORE_PATH") ?: "debug.keystore")
            storePassword System.getenv("KEYSTORE_PASSWORD")
            keyAlias System.getenv("KEY_ALIAS")
            keyPassword System.getenv("KEY_PASSWORD")
        }
    }
    buildTypes {
        debug {
            applicationIdSuffix ".debug"            // debug अलग app की तरह install (prod के साथ)
            versionNameSuffix "-debug"              // version में दिखे
            debuggable true                         // debugger attach हो सके
            signingConfig signingConfigs.debug      // default debug key
        }
        staging {                                   // custom build type (QA)
            initWith release                        // release की settings copy
            applicationIdSuffix ".staging"          // अलग ID
            matchingFallbacks = ['release']         // libraries में 'staging' न हो तो release
            signingConfig signingConfigs.debug      // आसान install (internal)
            debuggable false
        }
        release {
            minifyEnabled true                      // R8 shrink + obfuscate
            shrinkResources true                    // unused resources हटाओ
            proguardFiles getDefaultProguardFile("proguard-android.txt"), "proguard-rules.pro"
            signingConfig signingConfigs.release    // upload key
            debuggable false                        // कभी true नहीं
        }
    }
}
// Note: custom build type 'staging' के लिए RN में कुछ libraries/Metro config
// समस्या कर सकती हैं (bundle task naming) — check current docs.
```
```jsonc
// ---------- Expo: eas.json (JSON — comments सिर्फ समझाने के लिए) ----------
{
  "build": {
    "development": { "developmentClient": true, "distribution": "internal",
                     "android": { "buildType": "apk" } },
    "preview":     { "distribution": "internal", "android": { "buildType": "apk" } },
    "production":  { "android": { "buildType": "app-bundle" } }
  }
}
// Commands: eas build -p android --profile development|preview|production
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Terms | buildTypes: debug, release | Configurations: Debug, Release (Xcode schemes) |
| Optimization | R8/ProGuard + Hermes | Compiler optimizations (-O) + Hermes |
| Signing | Debug keystore auto | Development vs Distribution certificate |
| Output | APK/AAB | .app (sim) / .ipa |
| Dev server | Debug में Metro (adb reverse) | Debug में Metro (localhost) |
| Cleartext HTTP | Debug में OK, release में block (Android 9+) | ATS block दोनों में |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
eas build -p android --profile development   # dev client (hot reload वाला)
eas build -p android --profile preview       # QA APK (release-like)
eas build -p android --profile production    # Play Store AAB
```
CLI way:
```bash
cd android && ./gradlew assembleDebug        # dev APK
cd android && ./gradlew assembleRelease      # release APK
cd android && ./gradlew bundleRelease        # Play AAB
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Performance debug build पर नापना
✅ Correct: Release build पर test (debug 2-10x धीमा हो सकता है)

❌ Mistake 2: Release में `console.log` भरे रहना (sensitive data leak, slow)
✅ Correct: `babel-plugin-transform-remove-console` या logger wrapper

❌ Mistake 3: Release पर API URL `localhost`/`http://10.0.2.2`
✅ Correct: env-based config, HTTPS production URL

❌ Mistake 4: R8 के बाद crash (class हटा दी गई)
✅ Correct: `proguard-rules.pro` में `-keep` rules, mapping.txt सुरक्षित रखो

❌ Mistake 5: Release को debug key से sign करके Play पर डालना
✅ Correct: Upload key से (191 देखो)

---

## 🧠 Tricky Interview Question
App debug में ठीक चलता है, पर release APK में start होते ही crash या API call fail होती है। 3 संभावित कारण?

Answer: (1) R8/ProGuard ने कोई class/reflection हटा दी (keep rules चाहिए)। (2) Cleartext HTTP traffic — debug में allow था, release में Android 9+ block (HTTPS या network security config)। (3) Release में Metro नहीं है और env/config गलत, या INTERNET permission सिर्फ debug manifest में है (debug/AndroidManifest.xml)। Debug के लिए `adb logcat` में release crash trace देखो और mapping.txt से deobfuscate करो।

---

## ⚫ Interview Questions + Answers
Q1: Debug build में JS कहाँ से आता है?
A1: Metro dev server से (network पर) — इसलिए hot reload, पर Metro बंद तो app load नहीं होगा।

Q2: Release build में JS कहाँ?
A2: Build के समय bundle होकर assets में (index.android.bundle, Hermes में compile)।

Q3: `applicationIdSuffix` क्यों?
A3: Debug/staging और prod एक phone पर साथ install करने के लिए अलग ID।

Q4: Product flavors क्या हैं?
A4: build types के ऊपर variants (जैसे dev/prod या अलग brand) — हर flavor+buildType = variant (`devDebug`, `prodRelease`)।

Q5: `debuggable true` release में खतरा क्यों?
A5: कोई भी debugger attach करके data/memory देख सकता है; Play Store भी release में debuggable build reject करता है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Debug: daily development, hot reload, debugging
- Release/Staging: performance, QA, store submission

❌ Avoid when:
- Debug build को users/QA को देना (धीमा, असुरक्षित)
- Release पर heavy debugging (source maps/Flipper के बिना कठिन)

---

## 📊 Visual Diagram
```
  DEBUG                              RELEASE
  ─────                              ───────
  JS ◄── Metro (laptop)              JS bundle app के अंदर (Hermes bytecode)
  debuggable = true                  debuggable = false
  no R8                              R8 shrink + obfuscate
  debug.keystore                     upload/release keystore
  fast iterate, slow runtime         slow build, fast runtime
```

---

## 🖥️ Console/Tool Screens (वर्णन)
```
Android Studio → left-bottom "Build Variants" panel: dropdown में debug/release (और staging) —
  चुनने पर Run बटन उसी variant से build करता है।
EAS dashboard (expo.dev) → project → Builds: हर row में profile (development/preview/production),
  status (Finished/In progress), और "Install"/"Download" बटन।
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Build type | Debug/release config | Build का प्रकार |
| R8/ProGuard | Shrink/obfuscate tool | Code छोटा/छुपाने वाला |
| Hermes | RN JS engine (bytecode) | RN का JS engine |
| Metro | JS bundler/dev server | JS bundler |
| Flavor | Product variant | Product प्रकार |
| mapping.txt | R8 name map | Crash decode map |

---

## ⚡ 3-Line Summary
English: Debug is for development (Metro, debuggable); release is optimized, bundled and signed for users.
Test performance and QA on release-like builds.
Keep staging IDs separate and keep R8 mapping files.

Hindi: Debug development के लिए (Metro, debuggable); release users के लिए optimized, bundled और signed।
Performance और QA release जैसे builds पर test करो।
Staging का अलग ID रखो और R8 mapping files सुरक्षित रखो।

---

## ➡️ Next Topic
**195. Generate APK vs AAB** — build commands से actual files कैसे बनती हैं।

---
