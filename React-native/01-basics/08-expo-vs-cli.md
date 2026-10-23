# 08. Expo vs React Native CLI
# हिंदी में: Expo और React Native CLI में क्या फर्क है?
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
**React Native CLI** = the official, bare-metal way to create React Native apps. You get full control over native Android/iOS code (Java/Kotlin/Swift/ObjC). **Expo** = a platform built ON TOP of React Native CLI that abstracts native complexity. Expo gives you a managed build system (EAS), a large SDK of pre-built native modules, and Expo Go for instant testing — without touching native code.

## 🔵 सरल परिभाषा (Hindi)
**React Native CLI** = official, bare-metal तरीका। Full control over native Android/iOS code। **Expo** = React Native CLI के ऊपर बना platform। Native complexity abstract करता है — EAS Build system, pre-built native modules का बड़ा SDK, और Expo Go for instant testing — native code छुए बिना।

---

## 🔴 Problem it Solves
```
PROBLEM WITH BARE CLI:
❌ Setting up Android Studio + Xcode is hard (hours of setup)
❌ Need a Mac to build iOS (legally required by Apple)
❌ Managing signing certificates is complex
❌ Every native library needs manual setup (gradle, podfile, etc.)
❌ OTA updates need custom setup
❌ CI/CD pipeline for mobile is complex

EXPO SOLUTION:
✅ Zero native setup: npx create-expo-app → working in 2 min
✅ Build iOS on Windows/Linux using EAS cloud build
✅ EAS handles signing automatically
✅ 80+ pre-configured native modules (camera, location, etc.)
✅ EAS Update: instant OTA updates
✅ EAS Build: cloud CI/CD included
```

## 🔴 यह क्यों बना? (Hindi)
```
CLI का problem: setup complex, Mac required for iOS, native code scary
Expo: सब कुछ abstract — setup 2 minutes, cloud build for iOS,
pre-built modules, automatic signing = faster development
```

---

## 🟢 How it Works — Step by Step

```
EXPO ARCHITECTURE:
──────────────────────────────────────────────────────
  Your JS/TS Code
       │
       ▼
  Expo SDK (pre-built modules: camera, location, etc.)
       │
       ▼
  React Native Core
       │
       ▼
  Native Platform (Android / iOS)

  EXPO GO: Pre-built native shell app
    → You write JS, Expo Go loads and runs it
    → No build needed for development!
    → Limitation: can't use custom native modules

  EAS Build (cloud):
    → Sends your project to Expo's build servers
    → Servers have Android Studio + Xcode installed
    → Returns APK/AAB or IPA
    → You don't need Mac for iOS builds!

REACT NATIVE CLI ARCHITECTURE:
──────────────────────────────────────────────────────
  Your JS/TS Code + Your Native Code (optional)
       │
       ▼
  React Native Core
       │
       ▼
  Native Platform (Android / iOS)

  METRO BUNDLER runs locally
  BUILDS happen on your machine (need Android Studio + Xcode)
  FULL CONTROL: can write Kotlin/Swift, modify any native file
```

## 🟢 कैसे काम करता है? (Hindi)
```
Expo: Your JS → Expo SDK → React Native → Native
      Cloud builds, pre-built modules, no Mac needed for iOS

CLI: Your JS + Native code → React Native → Native
     Local builds, full control, Mac required for iOS
```

---

## 🟡 Real World Example
**Startup vs Enterprise:** A **startup** building India's next food delivery app: use Expo — get to market in weeks, not months. No time wasted on Xcode certificates and Gradle config. **HDFC Bank** building their mobile banking app: use React Native CLI — they need custom biometric encryption that no Expo SDK covers, they need full control over network security layer in Java/Kotlin, their security team must audit all native code. Rule: startup speed → Expo; enterprise custom native → CLI.

## 🟡 Real Example Hindi मे
**Startup vs Enterprise:** Startup (नई food delivery app): Expo use करो — weeks में market, Xcode certificates की tension नहीं। **HDFC Bank**: CLI use करेगा — custom biometric encryption, network security layer, security audit — सब native code पर full control चाहिए।

---

## 💻 Code Example — Basic

Expo way:
```bash
# Install Expo CLI
npm install -g expo-cli

# Create app (2 minutes!)
npx create-expo-app MyApp --template blank-typescript

# Run instantly (no build needed)
cd MyApp
npx expo start

# Opens Expo Go on your phone — scan QR code
# Works on Android AND iOS without any native setup!
```

CLI way:
```bash
# Requires: Android Studio + Android SDK + Xcode (Mac only for iOS)
# Environment setup: ~2-4 hours

# Create app
npx react-native@latest init MyApp --template react-native-template-typescript

# Run on Android (Android Studio + emulator/device needed)
cd MyApp
npx react-native run-android

# Run on iOS (Mac + Xcode required)
npx react-native run-ios
```

## 💻 Code Example — Advanced

```jsx
// Using Expo SDK modules (no native setup needed!)
import { Camera, CameraType } from 'expo-camera';        // camera
import * as Location from 'expo-location';               // GPS
import * as Notifications from 'expo-notifications';     // push
import * as ImagePicker from 'expo-image-picker';        // gallery
import * as SecureStore from 'expo-secure-store';        // keychain

// All of the above: just npm install + import
// NO changes to android/build.gradle or ios/Podfile needed!

import React, { useState, useEffect } from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';

function ExpoFeaturesDemo() {
  const [location, setLocation] = useState(null);
  const [cameraPermission, requestCameraPermission] = Camera.useCameraPermissions();

  // Get location — Expo handles the native bridge
  const getLocation = async () => {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') return;

    const loc = await Location.getCurrentPositionAsync({});
    setLocation(loc.coords);
  };

  // Expo modules: same API on Android and iOS!
  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.8,
    });

    if (!result.canceled) {
      console.log('Selected image:', result.assets[0].uri);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Expo Features Demo</Text>

      <Button title="Get My Location" onPress={getLocation} />
      {location && (
        <Text style={styles.info}>
          Lat: {location.latitude.toFixed(4)}, Lng: {location.longitude.toFixed(4)}
        </Text>
      )}

      <Button title="Pick Image from Gallery" onPress={pickImage} />

      {!cameraPermission?.granted && (
        <Button title="Request Camera Access" onPress={requestCameraPermission} />
      )}
    </View>
  );
}

// EQUIVALENT CLI (React Native CLI):
// Would need to:
// 1. npm install react-native-camera react-native-geolocation-service
// 2. android/app/build.gradle: add permissions + link package
// 3. android/AndroidManifest.xml: add permission entries
// 4. ios/Podfile: add pod entry + pod install
// 5. ios/Info.plist: add NSCameraUsageDescription
// Same feature = 30 min of native config in CLI!

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 20, gap: 12 },
  title: { fontSize: 20, fontWeight: '700', textAlign: 'center' },
  info: { fontSize: 14, color: '#666', textAlign: 'center' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Build without Mac | Both CLI and Expo work | Only Expo EAS (CLI needs Mac) |
| Signing | Keystore file | Certificates + Provisioning Profiles |
| Expo Go available | Yes (Play Store) | Yes (App Store) |
| Custom native code | AndroidManifest + build.gradle | Info.plist + Podfile |

---

## 🟠 Expo vs CLI Difference (The Core Comparison)

Expo Managed Workflow:
```bash
# No native files — Expo manages them
npx create-expo-app MyApp
npx expo start                    # instant dev, Expo Go
eas build --platform android      # cloud build, no Android Studio
eas submit --platform android     # direct to Play Store
eas update                        # OTA update, no store review!
```

CLI (Bare Workflow):
```bash
npx react-native@latest init MyApp
npx react-native run-android      # needs Android Studio
cd ios && pod install && cd ..
npx react-native run-ios          # needs Xcode + Mac
# Build: Android Studio → Build → Generate Signed Bundle
# OR: fastlane / GitHub Actions (manual CI/CD setup)
```

Expo with Custom Native (Expo + bare):
```bash
# "Eject" from managed → get native files but keep Expo SDK
npx expo eject              # exposes android/ and ios/ folders
# or just add custom native module:
npx expo install react-native-vision-camera
# If it has native code → needs prebuild
npx expo prebuild           # generates android/ ios/ from app.json
npx expo run:android        # run with native code
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Thinking Expo = always slower/worse than CLI
```
WRONG belief: "Real apps use CLI, Expo is for beginners"
REALITY:
- Myntra, Shopify, Discord — all use Expo in production
- Expo SDK wraps the same React Native core
- Expo apps on Play Store and App Store = same as CLI apps
- EAS Build = professional CI/CD used by major companies
- The app user CANNOT tell if you used Expo or CLI
```

❌ **Mistake 2:** Using `expo eject` unnecessarily
```
// Old Expo (SDK < 41) had actual "eject" that broke everything
// New Expo has "prebuild" — generates native files but stays connected
// Don't "eject" unless you truly need custom native code
// 90% of native features are in Expo SDK — check expo.dev/sdk first!
```

❌ **Mistake 3:** Not knowing when to use bare CLI
```
SHOULD USE CLI when:
- Custom C++/Java/Kotlin/Swift native modules
- Specific NDK libraries
- Complex background audio/video processing
- Enterprise security requirements (specific native crypto)
- Brownfield (adding RN to existing native app)

SHOULD USE EXPO when:
- New app from scratch
- Team is small / startup
- Don't need deep native customization
- Need fast iteration and OTA updates
- Building for both platforms
```

---

## 🧠 Tricky Interview Question

**Q: An Expo app can't access a native library that only has a React Native CLI version. What are your options?**

**Answer:** Three approaches: (1) **Check Expo SDK first** — often Expo has its own version (`expo-camera` covers most `react-native-camera` use cases). (2) **Expo Development Build** — instead of Expo Go, create a custom development client that includes your native library: `eas build --profile development`. This gives you Expo's workflow but with custom native modules. (3) **Expo Prebuild** — run `npx expo prebuild` to generate `android/` and `ios/` folders while keeping the Expo SDK and EAS. Install the library, configure native files, and use `npx expo run:android`. You keep Expo's convenience while getting full native access. Only if none of these work should you fully migrate to bare CLI.

---

## ⚫ Interview Questions + Answers

**Q1: What is the main difference between Expo and React Native CLI?**
A1: React Native CLI is the official tool that gives you full access to native Android/iOS code — you own the `android/` and `ios/` folders. Expo is a platform built on top that abstracts native complexity: EAS Build handles builds in the cloud (so iOS builds work on Windows), Expo SDK provides 80+ pre-built modules, and Expo Go lets you test without building. The final app is identical to the user — they can't tell which you used.

**Q2: Can you build an iOS app using Expo without a Mac?**
A2: Yes — with **EAS Build**. You run `eas build --platform ios` from any OS (Windows, Linux, Mac). EAS sends your project to Expo's cloud servers which have Xcode installed, builds the IPA, and returns it. You can even submit directly to App Store with `eas submit --platform ios`. This is one of Expo's biggest advantages — small teams or Windows developers can ship iOS apps without owning a Mac.

**Q3: What is EAS and what does it stand for?**
A3: EAS = **Expo Application Services**. Three main services: (1) **EAS Build** — cloud build service for Android + iOS, handles signing automatically, returns APK/AAB/IPA. (2) **EAS Submit** — submits directly to Google Play Store or Apple App Store. (3) **EAS Update** — OTA (Over The Air) updates — ship JS bundle changes instantly without going through store review (allowed by both stores for JS-only changes). EAS is the reason many teams choose Expo for production apps.

**Q4: What is Expo Go? What are its limitations?**
A4: Expo Go is a pre-built app (on Play Store and App Store) that can load any Expo app by scanning a QR code — no build step needed for development. Limitation: Expo Go only supports Expo SDK modules. If you need a custom native library (say, `react-native-vision-camera` for camera ML features), Expo Go can't run it. Solution: create an **Expo Development Build** with `eas build --profile development` — a custom Expo Go that includes your native libraries.

**Q5: When would you choose React Native CLI over Expo for a new project?**
A5: Choose CLI when: (1) Need custom C++/Java/Kotlin/Swift native modules not covered by Expo SDK. (2) Adding React Native to an existing native app (brownfield integration). (3) Specific enterprise security requirements (custom crypto, custom network layer). (4) Very large team with dedicated mobile engineers who are comfortable with native tooling. For most new projects (especially startups), Expo is the better choice for faster iteration. Even with custom native needs, Expo Prebuild lets you keep most of Expo's benefits.

---

## 🔷 When to Use + When Not to Use
✅ **Use Expo when:**
- New project (2024+) — default choice
- Small-medium team
- Need both Android and iOS from day 1
- OTA updates important
- Team isn't experienced with native mobile setup

✅ **Use React Native CLI when:**
- Brownfield app (adding RN to existing native app)
- Custom native C++/Java/Kotlin/Swift modules
- Large enterprise with dedicated mobile native team
- Library that only supports CLI (very rare now)

---

## 📊 Visual Diagram

```
EXPO vs CLI — DECISION TREE:
──────────────────────────────────────────────────────
  New Project?
       │
       ├── YES → Need custom native C++/Java/Swift?
       │              │
       │              ├── NO → Use EXPO (managed)
       │              │         npx create-expo-app
       │              │         eas build, eas update
       │              │
       │              └── YES → Use EXPO PREBUILD
       │                        or React Native CLI
       │
       └── NO (existing native app) → React Native CLI
                                       (brownfield)

COMPARISON TABLE:
──────────────────────────────────────────────────────
  Feature              │ Expo (Managed) │ React Native CLI
  ─────────────────────┼────────────────┼─────────────────
  Setup time           │ 2 min          │ 2-4 hours
  iOS build on Windows │ YES (EAS)      │ NO (need Mac)
  Native code access   │ Expo SDK only  │ Full
                       │ (or prebuild)  │
  OTA updates          │ EAS Update     │ Manual setup
  Build system         │ EAS (cloud)    │ Local / custom CI
  Learning curve       │ Low            │ High
  Production ready     │ YES            │ YES
  App Store difference │ None           │ None
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Expo | Platform built on RN with abstractions | RN के ऊपर बना platform |
| EAS | Expo Application Services (build/submit/update) | Expo की cloud services |
| Expo Go | Pre-built test app (scan QR to run) | QR scan करके app test करने का tool |
| EAS Build | Cloud build service for Android + iOS | Cloud build service |
| EAS Update | OTA update without store review | Store review बिना update |
| Prebuild | Generate native folders while keeping Expo | Native folders generate करना |
| Managed Workflow | Expo handles all native config | Expo सब native config handle करे |
| Bare Workflow | Expo SDK + your own native files | Expo SDK + खुद के native files |

---

## ⚡ 3-Line Summary
**English:**
1. Expo abstracts native complexity — 2-minute setup, cloud iOS builds (no Mac needed), 80+ pre-built modules, OTA updates via EAS.
2. React Native CLI gives full native access — needed for custom C++/Java/Kotlin/Swift code, brownfield apps, or enterprise native requirements.
3. For 90% of apps (startups, side projects, product teams): use Expo; even with custom native needs, Expo Prebuild gives you the best of both.

**Hindi:**
1. Expo native complexity abstract करता है — 2-minute setup, cloud iOS builds (Mac नहीं चाहिए), 80+ pre-built modules, EAS से OTA updates।
2. React Native CLI full native access देता है — custom native code, brownfield apps, enterprise requirements के लिए।
3. 90% apps के लिए Expo; custom native जरूरत हो तो Expo Prebuild दोनों का best combination देता है।

---

## ➡️ Next Topic
**09. When to Use Expo vs CLI** — Real project scenarios, migration paths, EAS detailed guide।
