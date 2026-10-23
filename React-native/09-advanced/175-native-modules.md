# 175. Native Modules
# हिंदी में: Native Modules क्या हैं?
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
**Native Modules** let you write platform-specific code (Java/Kotlin for Android, Objective-C/Swift for iOS) and call it from JavaScript. When React Native doesn't have a built-in or community solution for a device feature (custom encryption, proprietary SDK, hardware integration), you build a Native Module to bridge the gap. With New Architecture, Native Modules become **TurboModules** (JSI-based, lazy-loaded).

## 🔵 सरल परिभाषा (Hindi)
**Native Modules** platform-specific code (Android = Java/Kotlin, iOS = Objective-C/Swift) लिखने और JavaScript से call करने की सुविधा देते हैं। जब React Native में built-in या community solution नहीं होती (custom encryption, proprietary SDK, hardware), Native Module bridge करता है। New Architecture में Native Modules = **TurboModules** (JSI-based, lazy-loaded)।

---

## 🔴 Problem it Solves
```
PROBLEM: React Native can't do everything natively
Examples where Native Module is needed:
  ❌ Bank's proprietary biometric SDK (not standard TouchID/FaceID)
  ❌ Custom hardware like POS machine, barcode scanner integration
  ❌ Proprietary analytics SDK (only available as .aar / .framework)
  ❌ Native performance-critical audio processing (HDFC bank voice OTP)
  ❌ Custom encryption library with C++ at core
  ❌ OS-level features not yet in React Native (Android 12 dynamic color)

Native Module solution:
  ✅ Write the platform-specific code in Java/Kotlin/Swift
  ✅ Expose methods via @ReactMethod annotation
  ✅ Call from JS: NativeModules.MyModule.doSomething()
```

## 🔴 यह क्यों बना? (Hindi)
```
React Native सब device features cover नहीं कर सकता।
Bank का proprietary biometric SDK, POS hardware, custom crypto —
Native Module लिखो → Java/Kotlin/Swift में → JS से call करो।
```

---

## 🟢 How it Works — Step by Step

```
NATIVE MODULE CREATION (Android):
──────────────────────────────────────────────────────
  Step 1 → Write Kotlin class extending ReactContextBaseJavaModule
           class EncryptionModule(context: ReactApplicationContext) :
             ReactContextBaseJavaModule(context) {

             override fun getName() = "EncryptionModule"  // JS name

             @ReactMethod
             fun encrypt(data: String, key: String, promise: Promise) {
               try {
                 val encrypted = AES.encrypt(data, key)
                 promise.resolve(encrypted)
               } catch (e: Exception) {
                 promise.reject("ENCRYPT_ERROR", e)
               }
             }
           }

  Step 2 → Register in ReactPackage
  Step 3 → Call from JS:
           import { NativeModules } from 'react-native';
           const { EncryptionModule } = NativeModules;
           const result = await EncryptionModule.encrypt(data, key);

NATIVE MODULE COMMUNICATION:
  JS → Bridge/JSI → Native Code → Result
  Returns: Promise (async) or Callback
  Passes: any serializable data (strings, numbers, arrays, plain objects)

NEW ARCHITECTURE (TurboModule):
  Uses JSI for direct C++ access
  Lazy-loaded (only initialized when first called)
  Can be synchronous
  Codegen: TypeScript spec → auto-generates C++ interface
```

## 🟢 कैसे काम करता है? (Hindi)
```
Kotlin/Swift class → @ReactMethod annotation → JS से call
Promise/Callback → async result return
New Architecture: JSI via Codegen → faster, lazy loaded
```

---

## 🟡 Real World Example
**Paytm Soundbox Integration:** Paytm's Soundbox device (the speaker that says "Paytm received ₹100") uses Bluetooth LE. React Native doesn't have deep BLE audio announcement support. Paytm wrote a Native Module in Kotlin that connects to the Soundbox via BLE, sends payment notification audio commands, and returns connection status to JS. This is impossible without a Native Module.

## 🟡 Real Example Hindi मे
**Paytm Soundbox:** BLE (Bluetooth Low Energy) से Soundbox को connect करना। React Native में deep BLE audio support नहीं। Paytm ने Kotlin में Native Module लिखा — BLE connect, audio command send, status JS को return।

---

## 💻 Code Example — Basic

```kotlin
// ANDROID: EncryptionModule.kt
package com.myapp

import com.facebook.react.bridge.*
import javax.crypto.Cipher
import javax.crypto.spec.SecretKeySpec
import android.util.Base64

class EncryptionModule(private val reactContext: ReactApplicationContext) :
    ReactContextBaseJavaModule(reactContext) {

    // getName() → this is what NativeModules.EncryptionModule uses in JS
    override fun getName(): String = "EncryptionModule"

    // @ReactMethod: exposes this as a callable method from JS
    // promise: used for async return (resolve = success, reject = error)
    @ReactMethod
    fun encrypt(data: String, key: String, promise: Promise) {
        try {
            val secretKey = SecretKeySpec(key.toByteArray(), "AES")
            val cipher = Cipher.getInstance("AES")
            cipher.init(Cipher.ENCRYPT_MODE, secretKey)
            val encrypted = Base64.encodeToString(cipher.doFinal(data.toByteArray()), Base64.DEFAULT)
            promise.resolve(encrypted)    // success → resolve
        } catch (e: Exception) {
            promise.reject("ENCRYPTION_ERROR", e.message)  // failure → reject
        }
    }

    @ReactMethod
    fun decrypt(data: String, key: String, promise: Promise) {
        try {
            val secretKey = SecretKeySpec(key.toByteArray(), "AES")
            val cipher = Cipher.getInstance("AES")
            cipher.init(Cipher.DECRYPT_MODE, secretKey)
            val decoded = Base64.decode(data, Base64.DEFAULT)
            val decrypted = String(cipher.doFinal(decoded))
            promise.resolve(decrypted)
        } catch (e: Exception) {
            promise.reject("DECRYPTION_ERROR", e.message)
        }
    }
}
```

```kotlin
// ANDROID: Register the module in a ReactPackage
// MyAppPackage.kt
package com.myapp

import com.facebook.react.ReactPackage
import com.facebook.react.bridge.NativeModule
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.uimanager.ViewManager

class MyAppPackage : ReactPackage {
    override fun createNativeModules(context: ReactApplicationContext): List<NativeModule> {
        return listOf(EncryptionModule(context))  // register the module!
    }

    override fun createViewManagers(context: ReactApplicationContext): List<ViewManager<*, *>> {
        return emptyList()
    }
}
```

```kotlin
// ANDROID: Add package to MainApplication.kt
// In getPackages():
override fun getPackages(): List<ReactPackage> {
    return PackageList(this).packages.apply {
        add(MyAppPackage())  // ← add your package here
    }
}
```

```jsx
// JAVASCRIPT: Using the Native Module
import { NativeModules } from 'react-native';
const { EncryptionModule } = NativeModules;

async function encryptUserData(userData) {
  try {
    const encrypted = await EncryptionModule.encrypt(
      JSON.stringify(userData),
      'mySecretKey12345'   // in real app: use secure key management!
    );
    console.log('Encrypted:', encrypted);
    return encrypted;
  } catch (error) {
    console.error('Encryption failed:', error.message);
    throw error;
  }
}
```

## 💻 Code Example — Advanced (with TypeScript + events)

```swift
// iOS: EncryptionModule.swift
import Foundation
import CommonCrypto

@objc(EncryptionModule)
class EncryptionModule: NSObject {

    @objc
    func encrypt(_ data: String, key: String, resolve: @escaping RCTPromiseResolveBlock,
                 reject: @escaping RCTPromiseRejectBlock) {
        guard let dataBytes = data.data(using: .utf8),
              let keyBytes = key.data(using: .utf8).flatMap({ k in
                  k.count == 16 ? k : nil
              }) else {
            reject("INVALID_INPUT", "Invalid data or key", nil)
            return
        }

        var encrypted = Data(count: dataBytes.count + kCCBlockSizeAES128)
        var encryptedCount = 0

        let status = encrypted.withUnsafeMutableBytes { encPtr in
            dataBytes.withUnsafeBytes { dataPtr in
                keyBytes.withUnsafeBytes { keyPtr in
                    CCCrypt(
                        CCOperation(kCCEncrypt),
                        CCAlgorithm(kCCAlgorithmAES),
                        CCOptions(kCCOptionECBMode + kCCOptionPKCS7Padding),
                        keyPtr.baseAddress, keyBytes.count,
                        nil, dataPtr.baseAddress, dataBytes.count,
                        encPtr.baseAddress, encrypted.count,
                        &encryptedCount
                    )
                }
            }
        }

        if status == kCCSuccess {
            resolve(encrypted.prefix(encryptedCount).base64EncodedString())
        } else {
            reject("ENCRYPTION_ERROR", "Failed to encrypt: \(status)", nil)
        }
    }
}
```

```objc
// iOS: EncryptionModule.m (Objective-C bridge file)
#import <React/RCTBridgeModule.h>

@interface RCT_EXTERN_MODULE(EncryptionModule, NSObject)
RCT_EXTERN_METHOD(encrypt:(NSString *)data key:(NSString *)key
                 resolve:(RCTPromiseResolveBlock)resolve
                 reject:(RCTPromiseRejectBlock)reject)
@end
```

```typescript
// TypeScript wrapper with proper types
import { NativeModules } from 'react-native';

type EncryptionModuleType = {
  encrypt(data: string, key: string): Promise<string>;
  decrypt(data: string, key: string): Promise<string>;
};

const { EncryptionModule } = NativeModules as { EncryptionModule: EncryptionModuleType };

export const encrypt = (data: string, key: string): Promise<string> =>
  EncryptionModule.encrypt(data, key);

export const decrypt = (data: string, key: string): Promise<string> =>
  EncryptionModule.decrypt(data, key);
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Language | Kotlin / Java | Swift / Objective-C |
| Method annotation | `@ReactMethod` | `RCT_EXTERN_METHOD` / `@objc` |
| Module base class | `ReactContextBaseJavaModule` | `NSObject` |
| Registration | `ReactPackage` + `MainApplication` | `RCT_EXTERN_MODULE` in `.m` file |
| Event emitter | `ReactContext.getJSModule()` | `sendEventWithName` in `RCTEventEmitter` |
| Thread | Background thread | Background queue |

---

## 🟠 Expo vs CLI Difference

Expo way:
```
Expo MANAGED: Cannot use custom Native Modules
  (Expo Go is a fixed native shell)

Expo DEVELOPMENT BUILD:
  1. Write native module (Kotlin/Swift)
  2. Configure expo-modules-core (easier API)
  3. npx expo prebuild → generates android/ ios/
  4. eas build --profile development → custom Expo Go
  5. Call from JS
```

CLI way:
```
Full control:
  1. Write Kotlin class
  2. Write ReactPackage
  3. Register in MainApplication
  4. Write Swift + .m file for iOS
  5. npx react-native run-android/ios
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Calling Native Module from the wrong thread
```kotlin
// WRONG: UI operations on the wrong thread
@ReactMethod
fun showToast(message: String) {
    Toast.makeText(reactContext, message, Toast.LENGTH_SHORT).show()
    // ❌ CRASHES: Toast must be on UI Thread!
}

// CORRECT: Run UI operations on UI Thread
@ReactMethod
fun showToast(message: String) {
    reactContext.runOnUiQueueThread {
        Toast.makeText(reactContext, message, Toast.LENGTH_SHORT).show()
    }
}
```

❌ **Mistake 2:** Not resolving/rejecting the Promise (memory leak)
```kotlin
// WRONG: Exception can leave promise unresolved → memory leak!
@ReactMethod
fun riskyOperation(promise: Promise) {
    val result = doSomethingRisky()  // may throw uncaught exception!
    promise.resolve(result)
}

// CORRECT: Always try/catch, always resolve OR reject
@ReactMethod
fun riskyOperation(promise: Promise) {
    try {
        val result = doSomethingRisky()
        promise.resolve(result)
    } catch (e: Exception) {
        promise.reject("ERROR_CODE", e.message ?: "Unknown error", e)
    }
}
```

❌ **Mistake 3:** Forgetting to create a separate thread for blocking operations
```kotlin
// WRONG: Long running operation on JS Thread bridge
@ReactMethod
fun processLargeFile(path: String, promise: Promise) {
    val result = processFile(path)  // ❌ blocks for 5 seconds on JS bridge thread!
    promise.resolve(result)
}

// CORRECT: Run on background thread
@ReactMethod
fun processLargeFile(path: String, promise: Promise) {
    Thread {
        try {
            val result = processFile(path)
            promise.resolve(result)
        } catch (e: Exception) {
            promise.reject("FILE_ERROR", e.message)
        }
    }.start()
}
```

---

## 🧠 Tricky Interview Question

**Q: When would you choose to write a Native Module vs using `react-native-webview` to load a web SDK?**

**Answer:** `WebView` with a web SDK is a valid option for: (1) SDKs that are web-only (no mobile SDK exists). (2) When native performance isn't critical. (3) Quick integration without native code. **Native Module is better when**: (1) The SDK is specifically provided as `.aar` (Android) or `.framework` (iOS) — Java/Kotlin APIs only, no web version. (2) Performance is critical (biometrics, encryption, real-time audio). (3) Need access to device hardware directly (custom Bluetooth device, NFC). (4) WebView adds 80MB overhead to app size. (5) The feature involves security — WebView's JS context has a larger attack surface. Rule: prefer existing community npm packages → Expo SDK → WebView SDK → Native Module (most expensive, but most powerful).

---

## ⚫ Interview Questions + Answers

**Q1: What is a Native Module in React Native?**
A1: A Native Module bridges JavaScript and platform-native code (Java/Kotlin for Android, Objective-C/Swift for iOS). It allows calling platform-specific APIs or third-party SDKs from JavaScript. Use cases: proprietary device SDKs, custom crypto, OS-level features not exposed by React Native, hardware integration. You write the native class, annotate callable methods, register the module, and call it via `NativeModules.ModuleName.methodName()` from JavaScript.

**Q2: How do you pass a result back from a Native Module to JavaScript?**
A2: Two mechanisms: (1) **Promise** (`Promise` parameter) — `promise.resolve(result)` on success, `promise.reject(code, message)` on failure. Awaited in JS with `async/await`. (2) **Callback** — `Callback` parameters for success and error. Avoid callbacks in favor of Promises. For events (spontaneous notifications from native to JS), use `RCTDeviceEventEmitter.emit(eventName, data)` — subscribe in JS with `DeviceEventEmitter.addListener(eventName, handler)`.

**Q3: What is a TurboModule?**
A3: TurboModule is the New Architecture's replacement for the old Native Module system. Old modules loaded all at startup via the Bridge (slow). TurboModules: lazy-loaded (only initialized when first called), accessed via JSI (no Bridge, no serialization), can make synchronous calls (old modules could only be async). Require a TypeScript spec file (Codegen generates the C++ interface automatically). Are backwards-compatible with old modules in bridge mode. React Native 0.74+ projects should prefer writing TurboModules.

**Q4: What is `@ReactMethod` annotation on Android?**
A4: `@ReactMethod` marks a public method of a `ReactContextBaseJavaModule` as callable from JavaScript. Rules: (1) Must be `public void` or use `Promise`/`Callback` for return values (can't return directly). (2) Parameters must be serializable types: `String`, `Boolean`, `Integer`, `Double`, `ReadableArray`, `ReadableMap`, or `Promise`/`Callback`. (3) The method executes on a background thread by default (not the JS thread or UI thread). Add `isBlockingSynchronousMethod = true` for synchronous access — but this blocks the JS thread!

**Q5: How do you send events from Native to JavaScript (not in response to a JS call)?**
A5: Android: `reactContext.getJSModule(DeviceEventManagerModule.RCTDeviceEventEmitter::class.java).emit("MyEvent", params)`. iOS: `[self sendEventWithName:@"MyEvent" body:@{@"value": @42}]` (in an `RCTEventEmitter` subclass). JavaScript listener: `const subscription = DeviceEventEmitter.addListener('MyEvent', (data) => { ... })`. Cleanup: `subscription.remove()` in `useEffect`'s return. Use case: Bluetooth state changes, background download progress, push notification received while app is in foreground.

---

## 🔷 When to Use + When Not to Use
✅ **Write a Native Module when:**
- Platform SDK provided as .aar/.framework only
- Custom hardware integration (BLE device, NFC)
- Performance-critical operations (crypto, audio processing)
- OS-level features React Native doesn't expose

❌ **Don't write Native Module when:**
- Community npm package exists (check react-native.directory)
- Expo SDK covers the use case
- Web SDK in WebView would work
- Feature is available in expo-modules-core

---

## 📊 Visual Diagram

```
NATIVE MODULE ARCHITECTURE:
──────────────────────────────────────────────────────
  JavaScript:
  NativeModules.EncryptionModule.encrypt(data, key)
       │
       ▼
  OLD: Bridge (JSON serialize → Queue → deserialize)
  NEW: JSI (direct C++ call, no serialization)
       │
       ▼
  Android: Kotlin method → runs on Background Thread
  iOS: Swift method → runs on Background Queue
       │
       ▼
  Native SDK (AES, Bluetooth, Camera SDK, etc.)
       │
       ▼
  promise.resolve(result) / promise.reject(code, msg)
       │
       ▼
  JavaScript: await = resolved / catch = rejected

FILE STRUCTURE (Android):
──────────────────────────────────────────────────────
  android/app/src/main/java/com/myapp/
    ├── EncryptionModule.kt    ← the module
    ├── MyAppPackage.kt        ← registers the module
    └── MainApplication.kt    ← add package here
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Native Module | JS → Native bridge | JS से Native code call करना |
| @ReactMethod | Mark method callable from JS | JS से callable method mark |
| TurboModule | New Architecture native module | New Arch का native module |
| Promise | Async return mechanism | Async return mechanism |
| ReactPackage | Registers native modules | Native modules register करता है |
| JSI | New direct C++ bridge | Direct C++ bridge |
| Codegen | Auto-generates native interfaces | Auto-generated native interfaces |
| DeviceEventEmitter | Native to JS events | Native से JS events |

---

## ⚡ 3-Line Summary
**English:**
1. Native Modules let you write Kotlin (Android) or Swift (iOS) code callable from JavaScript — for proprietary SDKs, custom hardware, or platform APIs React Native doesn't expose.
2. Methods use `Promise` for async return; always try/catch and always resolve OR reject; run UI operations on the UI thread.
3. New Architecture: TurboModules (JSI + Codegen, lazy-loaded); prefer existing community packages or Expo SDK before writing your own Native Module.

**Hindi:**
1. Native Modules Kotlin (Android) / Swift (iOS) code JavaScript से callable बनाते हैं — proprietary SDKs, custom hardware, या React Native exposed नहीं APIs के लिए।
2. Methods `Promise` use करते हैं async return के लिए; always try/catch; always resolve या reject करो; UI operations UI thread पर चलाओ।
3. New Architecture: TurboModules (JSI + Codegen, lazy-loaded); अपना Native Module लिखने से पहले community packages या Expo SDK check करो।

---

## ➡️ Next Topic
**176. Native UI Components** — custom native views जो React Native में use हो सकें।
