# 176. Native Modules (iOS — Objective-C/Swift)
# हिंदी में: iOS Native Modules (Objective-C / Swift)
# Platform: iOS ✅ (Android alternative: topic 175)

> **Expo SDK 54 (React Native 0.81) target** — check current docs — APIs change between SDKs. Below: classic `RCT_EXPORT_MODULE` module (works on old arch + new arch via interop) and the **Expo Modules API** (Swift). Native code is **not run** here (no Xcode).

---

## 🔵 Simple Definition (English)
An **iOS native module** is Objective-C or Swift code exposed to JavaScript so your RN app can use Apple APIs (HealthKit, Keychain, Haptics, Apple Pay) that React Native does not wrap itself. JS calls methods; native returns values via **Promises** or **callbacks**.

## 🔵 सरल परिभाषा (Hindi)
**iOS native module** Objective-C या Swift का code है जो JavaScript को दिखाया जाता है, ताकि RN app Apple APIs (HealthKit, Keychain, Haptics, Apple Pay) use कर सके जिन्हें React Native खुद wrap नहीं करता। JS methods call करता है; native **Promise** या **callback** से जवाब देता है।

---

## 🔴 Problem it Solves
```
❌ RN ships only common APIs; new iOS features (Live Activities, Widgets) missing
❌ Third-party iOS SDKs (payment, KYC, analytics) have Swift/ObjC APIs only
❌ Heavy work (image processing) too slow in JS
✅ A native module = bridge your own Swift/ObjC to JS
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ RN सिर्फ आम APIs देता है; नए iOS features (Live Activities, Widgets) नहीं
❌ Third-party iOS SDKs (payment, KYC, analytics) सिर्फ Swift/ObjC में होते हैं
❌ भारी काम (image processing) JS में धीमा
✅ Native module = अपना Swift/ObjC code JS से जोड़ना
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Create a Swift/ObjC class in Xcode (ios/ folder)
Step 2 → Mark it exportable: RCT_EXPORT_MODULE() (ObjC) 
Step 3 → Export methods: RCT_EXPORT_METHOD(...) or RCT_REMAP_METHOD(...) for promises
Step 4 → For Swift: @objc class + an ObjC .m file using RCT_EXTERN_MODULE
Step 5 → Add a bridging header if mixing Swift + ObjC
Step 6 → JS: import { NativeModules } from 'react-native'
Step 7 → Call NativeModules.MyModule.method() -> receive Promise/callback
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Xcode में Swift/ObjC class बनाओ (ios/ folder)
Step 2 → उसे export करो: RCT_EXPORT_MODULE() (ObjC)
Step 3 → Methods export करो: RCT_EXPORT_METHOD(...) या promise के लिए RCT_REMAP_METHOD(...)
Step 4 → Swift के लिए: @objc class + ObjC .m file में RCT_EXTERN_MODULE
Step 5 → Swift + ObjC मिलाने पर bridging header जोड़ो
Step 6 → JS में: import { NativeModules } from 'react-native'
Step 7 → NativeModules.MyModule.method() call करो -> Promise/callback मिलेगा
```

---

## 🟡 Real World Example
**PhonePe/Paytm** iOS apps wrap Apple's **Keychain** and **LocalAuthentication (Face ID)** in a native module so JS can ask `isBiometricAvailable()`. **Swiggy** could expose iOS **Live Activities** (delivery tracking on lock screen) through a Swift module.

## 🟡 Real Example Hindi mein
**PhonePe/Paytm** iOS apps Apple के **Keychain** और **LocalAuthentication (Face ID)** को native module में wrap करते हैं ताकि JS `isBiometricAvailable()` पूछ सके। **Swiggy** iOS **Live Activities** (lock screen पर delivery tracking) को Swift module से JS में ला सकता है।

---

## 💻 Code Example — Basic
```objc
// ios/DeviceModule.h  — Objective-C header
#import <React/RCTBridgeModule.h>   // RN protocol for native modules

@interface DeviceModule : NSObject <RCTBridgeModule> // class must implement the protocol
@end
```
```objc
// ios/DeviceModule.m  — Objective-C implementation
#import "DeviceModule.h"
#import <UIKit/UIKit.h>            // for UIDevice

@implementation DeviceModule

RCT_EXPORT_MODULE();               // exports the module; JS name = class name "DeviceModule"

// Promise-based method: JS gets Promise<string>
RCT_REMAP_METHOD(getDeviceName,                          // JS method name
                 resolver:(RCTPromiseResolveBlock)resolve // success callback
                 rejecter:(RCTPromiseRejectBlock)reject)  // error callback
{
  NSString *name = [[UIDevice currentDevice] name];        // e.g. "Aditya's iPhone"
  if (name) {
    resolve(name);                                         // send string to JS
  } else {
    reject(@"E_NO_NAME", @"Could not read device name", nil); // send error to JS
  }
}

// Plain method with args (fire and forget)
RCT_EXPORT_METHOD(logEvent:(NSString *)name value:(nonnull NSNumber *)value)
{
  NSLog(@"Event %@ = %@", name, value);                    // prints in Xcode console
}

// Run native work off the main thread unless you touch UIKit
- (dispatch_queue_t)methodQueue {
  return dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
}

// Tell RN whether init must happen on main thread (false = background OK)
+ (BOOL)requiresMainQueueSetup { return NO; }

@end
```
```jsx
// JS usage (iOS only; guard for Android)
import { NativeModules, Platform } from 'react-native'; // access native modules

export async function getDeviceName() {
  if (Platform.OS !== 'ios') return 'n/a';              // module exists only on iOS
  const { DeviceModule } = NativeModules;               // look up by exported name
  if (!DeviceModule) throw new Error('DeviceModule not linked — run pod install & rebuild');
  return DeviceModule.getDeviceName();                  // returns a Promise
}
```

## 💻 Code Example — Advanced
```swift
// ios/Haptics.swift — Swift module: use @objc so ObjC runtime (RN) can see it
import Foundation
import UIKit

@objc(Haptics)                              // exposes class name "Haptics" to ObjC
class Haptics: NSObject {

  // UIKit work must run on main thread
  @objc static func requiresMainQueueSetup() -> Bool { return true }

  // Promise method: resolve/reject blocks come from RN
  @objc(impact:resolver:rejecter:)
  func impact(_ style: String,
              resolver resolve: @escaping RCTPromiseResolveBlock,
              rejecter reject: @escaping RCTPromiseRejectBlock) {
    DispatchQueue.main.async {              // hop to main thread for UIKit
      let feedbackStyle: UIImpactFeedbackGenerator.FeedbackStyle
      switch style {                        // map string -> style
        case "light": feedbackStyle = .light
        case "heavy": feedbackStyle = .heavy
        case "medium": feedbackStyle = .medium
        default:
          reject("E_STYLE", "Unknown style \(style)", nil) // invalid arg -> JS error
          return
      }
      UIImpactFeedbackGenerator(style: feedbackStyle).impactOccurred() // vibrate
      resolve(true)                        // success
    }
  }
}
```
```objc
// ios/Haptics.m — ObjC file that EXPOSES the Swift class to RN
#import <React/RCTBridgeModule.h>

@interface RCT_EXTERN_MODULE(Haptics, NSObject)      // RN module "Haptics"
RCT_EXTERN_METHOD(impact:(NSString *)style           // method + arguments
                  resolver:(RCTPromiseResolveBlock)resolve
                  rejecter:(RCTPromiseRejectBlock)reject)
@end
// Also: Xcode must have a bridging header importing <React/RCTBridgeModule.h> (Xcode offers to create it).
```
```swift
// Modern alternative: Expo Modules API (Swift) — much less boilerplate, works with Expo prebuild
import ExpoModulesCore

public class HapticsExpoModule: Module {
  public func definition() -> ModuleDefinition {
    Name("HapticsExpo")                              // JS: requireNativeModule('HapticsExpo')
    // AsyncFunction returns a Promise to JS
    AsyncFunction("impact") { (style: String) in
      await MainActor.run {                          // UIKit on main actor
        UIImpactFeedbackGenerator(style: style == "heavy" ? .heavy : .light).impactOccurred()
      }
    }
  }
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android (topic 175) | iOS (this topic) |
|---------|---------|-----|
| Language | Kotlin / Java | Objective-C / Swift |
| Export macro | `@ReactMethod` + `ReactContextBaseJavaModule` | `RCT_EXPORT_METHOD`, `RCT_EXTERN_MODULE` |
| Register | `ReactPackage` in `MainApplication` | Auto-discovered by `RCT_EXPORT_MODULE` |
| Promise | `Promise` object | `RCTPromiseResolveBlock` / `RejectBlock` |
| Threading | Native modules thread | `methodQueue` |
| Permissions | AndroidManifest.xml | Info.plist usage strings |
| Link step | Gradle sync | `pod install` |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Local Expo module scaffold (Swift + Kotlin together)
npx create-expo-module@latest --local
# Needs development build (not Expo Go)
npx expo prebuild && npx expo run:ios
```
CLI way:
```bash
# Put .h/.m/.swift files in ios/<AppName>/ via Xcode "Add Files"
cd ios && bundle exec pod install && cd ..
npx react-native run-ios
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting `pod install` / not rebuilding after adding native files
✅ Correct: Native changes need a rebuild; Metro reload is not enough.

❌ Mistake 2: Touching UIKit off the main thread
✅ Correct: Use `DispatchQueue.main.async` or `requiresMainQueueSetup` / `methodQueue` main queue.

❌ Mistake 3: Swift class without `@objc` or ObjC `RCT_EXTERN_MODULE` file
✅ Correct: Both are required for RN (ObjC runtime) to discover the Swift module.

---

## 🧠 Tricky Interview Question
**Q: `NativeModules.Haptics` is `undefined` in JS although the Swift file compiles. Why?**

**Answer:** Typical causes: (1) missing `Haptics.m` with `RCT_EXTERN_MODULE`; (2) Swift class lacks `@objc(Haptics)`; (3) no bridging header; (4) app not rebuilt after adding files; (5) running in Expo Go, which does not include your native code.

---

## ⚫ Interview Questions + Answers

**Q1: What does `RCT_EXPORT_MODULE()` do?**
A1: Registers the class with RN so JS can find it by name.

**Q2: How do you return a Promise?**
A2: Use `RCT_REMAP_METHOD` with `resolver:` and `rejecter:` blocks and call `resolve(...)` or `reject(...)`.

**Q3: Why `requiresMainQueueSetup`?**
A3: Tells RN whether initialization must be on the main thread (needed if the module touches UIKit in `init`).

**Q4: Swift or Objective-C?**
A4: Both work; Swift needs an ObjC shim file (or use Expo Modules API which is Swift-native).

**Q5: How does this differ with the New Architecture?**
A5: Use a TurboModule spec + Codegen for typed, lazy modules; old-style modules still run via the interop layer.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need an Apple API or iOS-only SDK
- Performance-critical native code

❌ Avoid when:
- An Expo package exists (expo-haptics, expo-local-authentication)
- Your project is Expo Go only

---

## 📊 Visual Diagram
```
 JS: NativeModules.Haptics.impact('heavy')
        │
        ▼
 RN runtime ──► Haptics.m (RCT_EXTERN_MODULE)
        │
        ▼
 Haptics.swift  ──► UIKit (main thread) ──► vibration
        │
        ▼
 resolve(true) ──► Promise in JS
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RCT_EXPORT_MODULE | Register module | Module register करना |
| RCT_EXPORT_METHOD | Expose method to JS | Method JS को दिखाना |
| Bridging header | Lets Swift see ObjC | Swift को ObjC दिखाने वाला header |
| methodQueue | Thread for methods | Methods का thread |
| Pod | iOS dependency (CocoaPods) | iOS dependency |
| Info.plist | iOS config file | iOS config file |

---

## ⚡ 3-Line Summary
**English:**
1. iOS native modules expose Objective-C/Swift APIs to JS.
2. Use `RCT_EXPORT_MODULE/METHOD`, promises, and `@objc` + `RCT_EXTERN_MODULE` for Swift.
3. Rebuild after changes; prefer Expo Modules API or TurboModules for new work.

**Hindi:**
1. iOS native modules Objective-C/Swift APIs को JS तक लाते हैं।
2. `RCT_EXPORT_MODULE/METHOD`, promises, और Swift के लिए `@objc` + `RCT_EXTERN_MODULE` use करो।
3. बदलाव के बाद rebuild करो; नए काम के लिए Expo Modules API या TurboModules चुनो।

---

## ➡️ Next Topic
**177. Native UI Components** — सिर्फ functions नहीं, पूरा native view JS में लाना।
