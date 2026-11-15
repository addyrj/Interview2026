# 171. New Architecture (Fabric + TurboModules)
# हिंदी में: नया Architecture (Fabric + TurboModules)
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 54 (React Native 0.81) target** — check current docs — APIs change between SDKs. New Architecture is the default for new projects since RN 0.76 (Expo SDK 52 made it default for new apps); later SDKs move toward making it mandatory (legacy removed). Verify your SDK's release notes.

---

## 🔵 Simple Definition (English)
The **New Architecture** is the rewritten core of React Native. It removes the old asynchronous **Bridge** (JSON messages) and uses **JSI** (direct C++ calls). Its parts: **Fabric** (new renderer), **TurboModules** (new native modules), **Codegen** (type-safe glue) and **Bridgeless mode**.

## 🔵 सरल परिभाषा (Hindi)
**New Architecture** React Native का दोबारा लिखा हुआ core है। यह पुराने asynchronous **Bridge** (JSON messages) को हटाकर **JSI** (सीधे C++ calls) use करता है। इसके हिस्से: **Fabric** (नया renderer), **TurboModules** (नए native modules), **Codegen** (type-safe glue) और **Bridgeless mode**।

---

## 🔴 Problem it Solves
```
OLD BRIDGE PROBLEMS:
❌ Every JS<->native call = serialize to JSON, send async, parse
❌ All native modules loaded at startup (slow launch)
❌ UI updates were async -> flicker, "white blank" while scrolling fast
❌ No type safety between JS and native (runtime crashes)
❌ Hard to do gestures + animations that need sync measurement
```

## 🔴 यह क्यों बना? (Hindi)
```
पुराने Bridge की दिक्कतें:
❌ हर JS<->native call = JSON में बदलो, async भेजो, फिर parse करो
❌ सारे native modules app start पर load (launch slow)
❌ UI updates async -> fast scroll पर blank/flicker
❌ JS और native के बीच type safety नहीं (runtime crash)
❌ Sync measurement चाहिए ऐसे gestures/animations मुश्किल
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → JS gets a direct reference to C++ host objects via JSI (no JSON)
Step 2 → Codegen reads your TypeScript spec and generates C++/ObjC/Java glue
Step 3 → TurboModules are loaded lazily, only when first used
Step 4 → React render creates a shadow tree in C++ (Fabric), layout by Yoga
Step 5 → Fabric commits the tree and mounts native views (sync possible)
Step 6 → Bridgeless: the old bridge is not created at all
Step 7 → You enable it (app.json "newArchEnabled") and rebuild native app
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → JSI से JS को C++ objects का सीधा reference मिलता है (JSON नहीं)
Step 2 → Codegen आपके TypeScript spec से C++/ObjC/Java glue code बनाता है
Step 3 → TurboModules lazy load होते हैं — पहली बार use पर ही
Step 4 → React render से C++ में shadow tree बनता है (Fabric), layout Yoga करता है
Step 5 → Fabric tree commit करके native views mount करता है (sync संभव)
Step 6 → Bridgeless में पुराना bridge बनता ही नहीं
Step 7 → app.json में "newArchEnabled" चालू करो और native app rebuild करो
```

---

## 🟡 Real World Example
**Meta (Facebook/Instagram)** runs the New Architecture at scale. In India, apps like **Swiggy/Zomato** benefit from faster startup (lazy TurboModules) and smoother lists. **Paytm/PhonePe** style apps with many native SDKs (payments, maps, KYC camera) gain because each SDK module loads only when the user opens that flow.

## 🟡 Real Example Hindi mein
**Meta (Facebook/Instagram)** बड़े scale पर New Architecture चलाता है। भारत में **Swiggy/Zomato** जैसे apps को तेज़ startup (lazy TurboModules) और smooth lists का फ़ायदा मिलता है। **Paytm/PhonePe** जैसे apps में कई native SDKs (payments, maps, KYC camera) होते हैं — हर SDK तभी load होता है जब user वह flow खोलता है।

---

## 💻 Code Example — Basic
```json
{
  "expo": {
    "name": "FoodApp",
    "slug": "food-app",
    "sdkVersion": "54.0.0",
    "newArchEnabled": true,
    "android": { "package": "com.example.foodapp" },
    "ios": { "bundleIdentifier": "com.example.foodapp" }
  }
}
```
```jsx
// Basic: detect at runtime whether Fabric / TurboModules are active
// Works on both Android + iOS (JS only, uses internal globals — debug use only)
import React from 'react'; // React
import { View, Text, StyleSheet } from 'react-native'; // UI parts

export default function ArchInfo() {
  // nativeFabricUIManager exists on global only when Fabric is enabled
  const isFabric = global?.nativeFabricUIManager != null;
  // __turboModuleProxy exists when TurboModules are enabled (undefined in Bridgeless it may be absent; use as hint)
  const hasTurbo = global?.__turboModuleProxy != null;
  return (
    <View style={styles.box}>
      {/* show result on screen */}
      <Text style={styles.t}>Fabric: {isFabric ? 'ON' : 'OFF'}</Text>
      <Text style={styles.t}>TurboModules: {hasTurbo ? 'ON' : 'OFF'}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  box: { padding: 20, marginTop: 60 }, // container spacing
  t: { fontSize: 18, marginBottom: 6 }, // text style
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: a module-safe wrapper that works on BOTH architectures
// Why: libraries must run on old + new arch during migration
import { NativeModules, TurboModuleRegistry, Platform } from 'react-native';

// Try TurboModule first (new arch), fall back to old NativeModules (interop layer)
function getNative(name) {
  try {
    // get() returns null if module not found (getEnforcing would throw)
    const turbo = TurboModuleRegistry.get(name);
    if (turbo) return turbo; // new architecture path
  } catch (e) {
    console.warn(`TurboModule ${name} lookup failed`, e); // log, then fall back
  }
  return NativeModules[name] ?? null; // legacy path (works via interop layer)
}

// Safe call wrapper with platform handling + error handling
export async function callNative(moduleName, method, ...args) {
  const mod = getNative(moduleName);            // find module
  if (!mod) {                                    // not installed / not linked
    throw new Error(`${moduleName} not available on ${Platform.OS}`);
  }
  if (typeof mod[method] !== 'function') {      // method missing
    throw new Error(`${moduleName}.${method} missing`);
  }
  try {
    return await mod[method](...args);          // works for sync or Promise methods
  } catch (err) {
    console.error(`Native call failed: ${moduleName}.${method}`, err); // report
    throw err;                                   // let caller handle UI
  }
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Enable flag | `newArchEnabled=true` in `gradle.properties` | `RCT_NEW_ARCH_ENABLED=1 bundle exec pod install` |
| Expo flag | `"newArchEnabled": true` in app.json (both) | same |
| Native glue | Java/Kotlin + C++ (JNI) | Objective-C++/Swift + C++ |
| Build tool | Gradle + CMake | CocoaPods + Xcode |
| Codegen output | Java interfaces + C++ | ObjC++ protocols + C++ |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# app.json -> "newArchEnabled": true   (default for new SDK 52+ projects)
npx expo prebuild --clean        # regenerate android/ios with the flag
npx expo run:android             # rebuild native app (Expo Go already supports new arch in recent SDKs)
```
CLI way:
```bash
# Android: android/gradle.properties
#   newArchEnabled=true
# iOS:
cd ios && RCT_NEW_ARCH_ENABLED=1 bundle exec pod install && cd ..
npx react-native run-android      # rebuild
npx react-native run-ios          # rebuild (macOS)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Enabling the flag but not rebuilding the native app
✅ Correct: It is a native change — run a fresh native build (`prebuild --clean`/`pod install`).

❌ Mistake 2: Using libraries that do not support the New Architecture
✅ Correct: Check `reactnative.directory` for "New Architecture" support; many old libs work via the interop layer but verify.

❌ Mistake 3: Believing the New Architecture makes everything faster automatically
✅ Correct: It removes bridge overhead; slow JS and heavy renders stay slow.

---

## 🧠 Tricky Interview Question
**Q: After enabling the New Architecture, one old library crashes on launch. The app uses Bridgeless mode. What is likely wrong and what can you do?**

**Answer:** The library may access `NativeModules` / bridge APIs (`RCTBridge`, `ReactContext.getCatalystInstance`) that do not exist in Bridgeless mode. Options: upgrade to a version with New Architecture support, rely on the interop layer if it works, patch with `patch-package`, or temporarily set `newArchEnabled: false` (only on SDKs that still allow it).

---

## ⚫ Interview Questions + Answers

**Q1: What replaces the Bridge?**
A1: JSI (JavaScript Interface) — a C++ API letting JS hold references to native objects and call them directly.

**Q2: Name the four pillars.**
A2: JSI, Fabric (renderer), TurboModules (native modules), Codegen (generates type-safe bindings).

**Q3: Why does startup get faster?**
A3: TurboModules load lazily instead of all at launch, and no bridge initialization is needed in Bridgeless mode.

**Q4: What can Fabric do that the old renderer could not?**
A4: Synchronous layout reads, concurrent rendering features (Suspense, transitions), and better interop with the host platform's layout.

**Q5: Is the old Bridge removed completely?**
A5: In Bridgeless mode it is not initialized; an interop layer lets many legacy modules still work. Check release notes for what your RN version supports.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Starting any new project (it is the default)
- You need faster startup or sync native calls
- You write custom native modules/views

❌ Avoid when:
- Critical third-party libs lack support and no alternative exists (stay on legacy temporarily if your SDK permits)
- You have no time to test native builds

---

## 📊 Visual Diagram
```
OLD                                  NEW
JS ──JSON (async)──► BRIDGE ──► Native     JS ◄══ JSI (direct C++) ══► Native
 all modules loaded at start               TurboModules lazy-loaded
 old renderer (async)                      Fabric renderer (C++ shadow tree)
                                           Codegen -> typed glue
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JSI | C++ API between JS and native | JS और native का सीधा C++ interface |
| Fabric | New UI renderer | नया UI renderer |
| TurboModule | Lazy, typed native module | Lazy और typed native module |
| Codegen | Generates glue from specs | Spec से glue code बनाना |
| Bridgeless | Mode with no old bridge | बिना पुराने bridge वाला mode |
| Interop layer | Lets old modules run on new arch | पुराने modules चलाने की परत |

---

## ⚡ 3-Line Summary
**English:**
1. New Architecture = JSI + Fabric + TurboModules + Codegen, no async JSON bridge.
2. Gives lazy loading, sync access, concurrent React features and type safety.
3. Enable via `newArchEnabled`, rebuild native, check library support.

**Hindi:**
1. New Architecture = JSI + Fabric + TurboModules + Codegen, async JSON bridge नहीं।
2. Lazy loading, sync access, concurrent React features और type safety मिलती है।
3. `newArchEnabled` चालू करो, native rebuild करो, libraries का support check करो।

---

## ➡️ Next Topic
**172. Fabric Renderer** — नया renderer अंदर से कैसे काम करता है।
