# 263. When Full Build is Required
# हिंदी में: कब Full Build ज़रूरी है
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52+ examples (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
A full build (new APK/AAB/IPA through EAS Build, Gradle or Xcode, followed by store release) is required whenever native code, native configuration or the Expo SDK / React Native version changes, because OTA can only replace the JS bundle and assets.

## 🔵 सरल परिभाषा (Hindi)
Full build (EAS Build/Gradle/Xcode से नया APK/AAB/IPA और store release) तब ज़रूरी है जब native code, native configuration या Expo SDK / React Native version बदलता है, क्योंकि OTA सिर्फ JS bundle और assets बदल सकता है।

---

## 🔴 Problem it Solves
```
PROBLEM: Team pushes an OTA that needs native code -> app crashes for everyone.
SOLUTION: Clear list of triggers that require a new binary.
```

## 🔴 यह क्यों बना? (Hindi)
Native code चाहिए पर OTA भेज दिया तो सबके app crash होंगे। यह list बताती है कि कब नया binary बनाना अनिवार्य है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → Identify trigger (see table)
Step 2 → Bump version (+ buildNumber / versionCode) and runtimeVersion if needed
Step 3 → eas build --platform all --profile production
Step 4 → Test on devices (preview/internal testing)
Step 5 → Submit: eas submit (Play Console / App Store Connect)
Step 6 → After rollout, publish OTAs against the NEW runtimeVersion only
```

### Full-build triggers
| Trigger | Why |
|---------|-----|
| Add/remove/upgrade a native module (expo-camera, react-native-maps, notifications SDK) | Native code lives in binary |
| Change permissions (AndroidManifest / Info.plist strings) | Declared at install time |
| Change app icon, splash, adaptive icon, app name, bundle id/package | Native resources |
| Expo SDK / React Native upgrade | New native runtime |
| Change URL schemes, deep-link intent filters, associated domains | Native config |
| Add config plugins or edit entitlements (push, Apple Sign-In capability) | Native project changes |
| Enable Hermes/New Architecture settings | Native build config |
| Firebase `google-services.json` / `GoogleService-Info.plist` changes | Bundled at build |
| Update to fix native crash | Native layer bug |

## 🟢 कैसे काम करता है? (Hindi)
1. Trigger पहचानो (ऊपर table)।
2. version/buildNumber/versionCode और ज़रूरत पर runtimeVersion बढ़ाओ।
3. `eas build` चलाओ।
4. Real devices पर test करो।
5. `eas submit` से store में भेजो।
6. Rollout के बाद OTA सिर्फ नए runtimeVersion के लिए भेजो।

---

## 🟡 Real World Example
Zomato-जैसे app में नया map SDK या Google Pay SDK जोड़ना, push notification की नई permission, या Android 15 target SDK upgrade - सबके लिए नया binary चाहिए। Swiggy का नया app icon (festival icon) भी native resource है, इसलिए OTA से नहीं बदलता (iOS alternate icons अलग API से binary में पहले से bundled होते हैं)।

## 🟡 Real Example Hindi mein
नया payment SDK, नई permission, app icon बदलना, Expo SDK upgrade - इन सबके लिए नया build और store release चाहिए।

---

## 💻 Code Example — Basic (eas.json with profiles)
```json
{
  "cli": { "version": ">= 12.0.0", "appVersionSource": "remote" },
  "build": {
    "development": { "developmentClient": true, "distribution": "internal" },
    "preview": { "distribution": "internal", "channel": "preview" },
    "production": { "autoIncrement": true, "channel": "production" }
  },
  "submit": { "production": {} }
}
```
```bash
eas build --platform all --profile production    # builds Android AAB + iOS IPA
eas submit --platform all --latest               # sends to both stores
```

## 💻 Code Example — Advanced (runtime guard: refuse OTA code if native feature missing)
```jsx
// nativeGuard.js - JS can detect missing native modules instead of crashing
import { requireOptionalNativeModule } from 'expo-modules-core';   // returns null if module is absent (expo-modules-core)

export const hasCameraModule = () =>
  requireOptionalNativeModule('ExpoCamera') != null;               // true only if binary includes expo-camera

// CameraGate.jsx
import React from 'react';                                         // React
import { View, Text, Linking, Platform } from 'react-native';      // UI

export default function CameraGate({ children }) {                 // wrap camera features
  if (!hasCameraModule()) {                                        // old binary without module
    return (
      <View style={{ padding: 20 }}>
        <Text>Please update the app to use this feature.</Text>
        <Text
          onPress={() => Linking.openURL(Platform.OS === 'ios'
            ? 'itms-apps://apps.apple.com/app/id1234567890'        // App Store (example id)
            : 'market://details?id=com.example.app')}             // Play Store (example id)
          style={{ color: 'blue' }}>Update now</Text>
      </View>
    );
  }
  return children;                                                 // safe to render camera UI
}
```
`requireOptionalNativeModule` exists in `expo-modules-core` (SDK 50+ as far as I know); verify the export and the native module name for your SDK. Not run.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Build artifact | AAB (store) / APK (direct) | IPA |
| Version fields to bump | versionCode, versionName | buildNumber, version |
| Permission change | AndroidManifest | Info.plist usage strings |
| Icon/splash | mipmap / adaptive icon | Asset catalog |
| Build tool | Gradle (local Linux/Mac/Win) | Xcode (Mac only) or EAS cloud |
| Capability change | Manifest/Gradle | Entitlements + provisioning profile regenerate |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx expo install expo-camera           # add native module
eas build -p all --profile production  # cloud builds, no Xcode/Android Studio needed
```
CLI way:
```bash
npm i react-native-vision-camera
cd ios && pod install                  # link iOS
cd android && ./gradlew bundleRelease  # build AAB
# Xcode Archive for iOS
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Bumping SDK and publishing OTA to old binaries.
✅ Correct: New runtimeVersion; old users stay on old JS until they update.

❌ Mistake 2: Forgetting to bump versionCode / buildNumber.
✅ Correct: `autoIncrement` in eas.json.

❌ Mistake 3: Not testing the new native build on real devices.
✅ Correct: Preview build + internal testing + TestFlight first.

❌ Mistake 4: Dropping support for old binaries silently.
✅ Correct: Keep backend backwards compatible or force an update.

---

## 🧠 Tricky Interview Question
You added `NSFaceIDUsageDescription` to app.json and ran `eas update`. Face ID prompt still crashes the app. Why?

Answer: Info.plist strings are compiled into the binary at build time. An OTA update changes only JS/assets, so the installed app still lacks the key, and iOS terminates it when Face ID is requested. You need a new iOS build (and review).

---

## ⚫ Interview Questions + Answers
Q1: Does changing app name need a build?
A1: Yes for the home-screen name (native). Some in-app text is JS.

Q2: Does an Expo SDK upgrade need a build?
A2: Yes.

Q3: What if both JS and native changed?
A3: Build and release the binary first; OTA targets the new runtimeVersion afterward.

Q4: Can you build iOS without a Mac?
A4: Yes via EAS Build (cloud).

Q5: How to reduce build frequency?
A5: Use dev client with common native modules pre-included, and batch native changes into planned releases.

---

## 🔷 When to Use + When Not to Use
✅ Full build when:
- Anything native changes, SDK upgrade, permissions, icons

❌ Avoid when:
- Only JS changed (use OTA)

---

## 📊 Visual Diagram
```
 Change type
   |-- JS/asset ------> OTA
   |-- Native/config --> bump versions -> eas build -> eas submit -> review -> rollout
                                   |
                       new runtimeVersion for future OTA
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Native module | Platform code exposed to JS | Native code |
| Entitlement | iOS capability permission | iOS क्षमता |
| versionCode | Android build number | Android build क्रमांक |
| AAB | Android App Bundle | Android bundle |
| IPA | iOS app archive | iOS app file |

---

## ⚡ 3-Line Summary
English: Native code, permissions, icons and SDK upgrades need a full build.
OTA cannot change what is compiled into the binary.
Bump versions and runtimeVersion, then release through the stores.

Hindi: Native code, permissions, icons और SDK upgrade के लिए full build चाहिए।
OTA binary में compile हुई चीज़ें नहीं बदल सकता।
Version और runtimeVersion बढ़ाकर stores से release करो।

---

## ➡️ Next Topic
**264. CI/CD for React Native** — builds और releases को automate करना।
