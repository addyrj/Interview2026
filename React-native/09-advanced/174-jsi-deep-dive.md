# 174. JSI Deep Dive
# हिंदी में: JSI (JavaScript Interface) विस्तार से
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 54 (React Native 0.81) target** — check current docs — APIs change between SDKs. JSI is a C++ API (`jsi/jsi.h`); its headers ship with React Native. Native code below is **not run** here.

---

## 🔵 Simple Definition (English)
**JSI (JavaScript Interface)** is a lightweight C++ API that lets native code and the JavaScript engine (Hermes) talk **directly**. Native code can install functions and objects into JS, and JS can hold references to C++ objects (**HostObjects**), with no JSON serialization.

## 🔵 सरल परिभाषा (Hindi)
**JSI (JavaScript Interface)** एक हल्का C++ API है जिससे native code और JavaScript engine (Hermes) **सीधे** बात करते हैं। Native code, JS में functions और objects डाल सकता है, और JS, C++ objects (**HostObjects**) को पकड़ सकता है — JSON serialization के बिना।

---

## 🔴 Problem it Solves
```
BRIDGE ERA:
❌ JS -> JSON string -> queue -> native -> parse (slow, copies data)
❌ Only async, batched messages
❌ JS engine hard-wired (JavaScriptCore) — JSI makes engine swappable (Hermes)
❌ Libraries needing speed (MMKV, Reanimated, Skia) could not be fast
```

## 🔴 यह क्यों बना? (Hindi)
```
Bridge के समय:
❌ JS -> JSON string -> queue -> native -> parse (धीमा, data copy)
❌ सिर्फ async और batch messages
❌ JS engine fixed (JavaScriptCore) — JSI से engine बदलना आसान (Hermes)
❌ तेज़ libraries (MMKV, Reanimated, Skia) बनाना मुश्किल था
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → App starts, Hermes creates a jsi::Runtime
Step 2 → Native code gets that runtime (rt) and the global object
Step 3 → It installs a HostFunction: rt.global().setProperty(rt, "add", fn)
Step 4 → JS calls global.add(1,2) -> runs your C++ lambda directly
Step 5 → HostObject: C++ class exposing get/set -> JS sees it as normal object
Step 6 → Values convert jsi::Value <-> C++ types (numbers, strings, objects)
Step 7 → Threading: JS runtime is single-threaded; don't touch it from other threads
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → App start पर Hermes एक jsi::Runtime बनाता है
Step 2 → Native code को वह runtime (rt) और global object मिलता है
Step 3 → वह HostFunction install करता है: rt.global().setProperty(rt, "add", fn)
Step 4 → JS में global.add(1,2) call -> आपका C++ lambda सीधे चलता है
Step 5 → HostObject: C++ class जो get/set दिखाती है -> JS में normal object जैसी
Step 6 → jsi::Value <-> C++ types (numbers, strings, objects) के बीच conversion
Step 7 → Threading: JS runtime single-threaded है; दूसरे thread से न छुएँ
```

---

## 🟡 Real World Example
**react-native-mmkv** (fast key-value storage) uses JSI so `storage.getString('token')` is **synchronous** — useful for **Paytm/PhonePe** style session checks at app launch. **Reanimated 3** uses JSI worklets to run animations on the UI thread; **Zomato**-like gesture-driven bottom sheets feel native because no bridge hop occurs.

## 🟡 Real Example Hindi mein
**react-native-mmkv** (तेज़ key-value storage) JSI use करता है, इसलिए `storage.getString('token')` **synchronous** है — **Paytm/PhonePe** जैसे apps में launch पर session check के लिए उपयोगी। **Reanimated 3** JSI worklets से animations UI thread पर चलाता है; **Zomato** जैसे gesture-driven bottom sheets इसी वजह से native जैसे लगते हैं।

---

## 💻 Code Example — Basic
```cpp
// Basic JSI: install a global function `nativeAdd(a, b)` into JS (C++)
// Concept code — compile inside an RN native project (Android via JNI / iOS via ObjC++)
#include <jsi/jsi.h>               // JSI API header (ships with RN)

using namespace facebook;          // jsi lives in namespace facebook::jsi

// Call this once, with the runtime, e.g. from your native module's install()
void installNativeAdd(jsi::Runtime& rt) {
  // create a JS function named "nativeAdd" taking 2 params
  auto fn = jsi::Function::createFromHostFunction(
    rt,                                            // runtime
    jsi::PropNameID::forAscii(rt, "nativeAdd"),    // function name
    2,                                             // expected arg count
    // lambda executed when JS calls nativeAdd(...)
    [](jsi::Runtime& rt, const jsi::Value&, const jsi::Value* args, size_t count) -> jsi::Value {
      if (count < 2 || !args[0].isNumber() || !args[1].isNumber()) { // validate input
        throw jsi::JSError(rt, "nativeAdd expects two numbers");     // becomes JS Error
      }
      double sum = args[0].asNumber() + args[1].asNumber();           // do the work in C++
      return jsi::Value(sum);                                         // return to JS
    });
  // attach to the JS global object
  rt.global().setProperty(rt, "nativeAdd", std::move(fn));
}
```
```js
// JS side (after native called installNativeAdd)
// global.nativeAdd is created by native code, so guard against missing install
if (typeof global.nativeAdd === 'function') {
  console.log(global.nativeAdd(2, 3)); // 5  (synchronous, no bridge)
} else {
  console.warn('JSI function not installed (running in Expo Go?)'); // safe fallback
}
```

## 💻 Code Example — Advanced
```cpp
// Advanced: a HostObject — a C++ object whose properties JS can read (like a tiny sync store)
#include <jsi/jsi.h>
#include <unordered_map>
#include <string>

using namespace facebook;

// Inherit HostObject to expose get/set/getPropertyNames to JS
class MemoryStore : public jsi::HostObject {
 public:
  // JS: store.foo  -> get("foo")
  jsi::Value get(jsi::Runtime& rt, const jsi::PropNameID& name) override {
    auto key = name.utf8(rt);                       // property name as std::string
    if (key == "set") {                             // store.set(key, value) method
      return jsi::Function::createFromHostFunction(rt, name, 2,
        [this](jsi::Runtime& rt, const jsi::Value&, const jsi::Value* args, size_t n) -> jsi::Value {
          if (n < 2) throw jsi::JSError(rt, "set(key, value) needs 2 args"); // validate
          data_[args[0].asString(rt).utf8(rt)] = args[1].asString(rt).utf8(rt); // save
          return jsi::Value::undefined();            // returns nothing
        });
    }
    auto it = data_.find(key);                      // normal lookup
    if (it == data_.end()) return jsi::Value::undefined(); // missing -> undefined
    return jsi::String::createFromUtf8(rt, it->second);    // return stored string
  }
 private:
  std::unordered_map<std::string, std::string> data_; // our storage (not thread-safe!)
};

// Install: global.memoryStore = new MemoryStore()
void installStore(jsi::Runtime& rt) {
  auto obj = jsi::Object::createFromHostObject(rt, std::make_shared<MemoryStore>());
  rt.global().setProperty(rt, "memoryStore", std::move(obj));
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Getting the runtime | JNI: `getJavaScriptContextHolder()` pointer -> `jsi::Runtime*` | ObjC++: `RCTBridge`/`RCTCxxBridge` `runtime` or TurboModule `jsInvoker` |
| Build glue | CMake + JNI (`CMakeLists.txt`) | `.mm` Objective-C++ + podspec |
| Engine | Hermes (default) | Hermes (default) |
| Common crash | Missing `System.loadLibrary` | Header search path missing |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Raw JSI requires custom native code -> development build, NOT Expo Go
npx expo prebuild
npx expo run:android
# Easier: use Expo Modules API or existing JSI libs (react-native-mmkv, reanimated)
```
CLI way:
```bash
# Add C++ files + CMake (Android) / .mm files (iOS), then rebuild
npx react-native run-android
cd ios && bundle exec pod install && cd .. && npx react-native run-ios
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using the `jsi::Runtime` from a background thread
✅ Correct: The runtime is not thread-safe. Schedule work back onto the JS thread (e.g., via `CallInvoker`).

❌ Mistake 2: Holding `jsi::Value`/`jsi::Object` after the runtime is destroyed
✅ Correct: Keep values scoped; reload/reset invalidates them.

❌ Mistake 3: Doing long synchronous work in a HostFunction
✅ Correct: It blocks the JS thread. Offload to a thread and return a Promise.

---

## 🧠 Tricky Interview Question
**Q: JSI calls are "synchronous and fast", so should every native call be a JSI sync function?**

**Answer:** No. Sync calls block the JS thread until native returns, freezing UI logic if the work is slow (network, disk). Use sync only for tiny, non-blocking reads (e.g., MMKV get). For anything slow, return a Promise and run work on another thread.

---

## ⚫ Interview Questions + Answers

**Q1: What is JSI?**
A1: A C++ API between the JS engine and native code enabling direct, synchronous calls and shared object references.

**Q2: What is a HostObject?**
A2: A C++ object exposed to JS where property reads/writes call C++ code.

**Q3: JSI vs Bridge?**
A3: Bridge = JSON messages async; JSI = direct memory-level calls, no serialization.

**Q4: Is JSI tied to Hermes?**
A4: No, it abstracts the engine; Hermes is the default in RN.

**Q5: Which libraries use JSI?**
A5: MMKV, Reanimated worklets, Skia, WatermelonDB (JSI adapter), TurboModules.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Ultra-fast sync access (storage, crypto, image processing)
- Sharing a C++ core with JS

❌ Avoid when:
- A TurboModule/Expo Module suffices
- Your team has no C++ experience (memory bugs crash the app)

---

## 📊 Visual Diagram
```
 JS (Hermes) ──── jsi::Runtime ────► C++ HostFunction / HostObject
       ▲                                   │
       └────── jsi::Value (no JSON) ◄──────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JSI | C++ JS<->native API | JS और native का C++ API |
| Runtime | JS engine instance | JS engine का instance |
| HostFunction | C++ function callable from JS | JS से call होने वाला C++ function |
| HostObject | C++ object seen as JS object | JS में दिखने वाला C++ object |
| jsi::Value | Any JS value in C++ | C++ में JS का value |
| CallInvoker | Schedules work on JS thread | JS thread पर काम भेजने वाला |

---

## ⚡ 3-Line Summary
**English:**
1. JSI lets JS and C++ talk directly without JSON.
2. Install HostFunctions/HostObjects into the JS runtime.
3. Never touch the runtime off the JS thread; avoid long sync work.

**Hindi:**
1. JSI से JS और C++ बिना JSON के सीधे बात करते हैं।
2. JS runtime में HostFunctions/HostObjects install करो।
3. JS thread के बाहर runtime मत छुओ; लंबा sync काम मत करो।

---

## ➡️ Next Topic
**176. Native Modules (iOS — Objective-C/Swift)** — iOS पर native module बनाना (175 Android वाला पहले से मौजूद है)।
