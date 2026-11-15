# 06. JSI — JavaScript Interface
# हिंदी में: JSI — JavaScript Interface (JS और Native की सीधी बातचीत)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: Expo SDK 52 / React Native 0.76 (New Architecture default). Expo SDK NN (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
**JSI (JavaScript Interface)** is a lightweight C++ layer that lets JavaScript hold a **direct reference** to native (C++) objects and call native functions **synchronously** — without converting everything to JSON and sending async messages over the old Bridge.

## 🔵 सरल परिभाषा (Hindi)
**JSI (JavaScript Interface)** एक हल्की C++ layer है जिससे JavaScript सीधे native (C++) objects का **reference** रख सकती है और native functions को **synchronously** call कर सकती है — पुराने Bridge की तरह हर चीज़ JSON में बदलकर async message भेजने की ज़रूरत नहीं।

---

## 🔴 Problem it Solves
```
OLD BRIDGE problems:
❌ Every call = JSON.stringify -> async queue -> JSON.parse (slow)
❌ Only async: JS could not ask native "what is the value?" and wait
❌ Big data (images, lists) = serialization cost
❌ Native modules loaded at startup, even if never used
❌ JS engine was tied to Bridge (hard to swap engines)
```

## 🔴 यह क्यों बना? (Hindi)
```
पुराने Bridge की दिक्कतें:
❌ हर call = JSON बनाओ -> async queue -> JSON parse करो (slow)
❌ सिर्फ async: JS native से value माँगकर wait नहीं कर सकती थी
❌ बड़ा data (images, lists) = serialization का भारी खर्च
❌ सारे native modules app start पर load होते थे
❌ JS engine, Bridge से बंधा था (engine बदलना मुश्किल)
JSI ने solve किया: direct reference + sync call + lazy loading
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → JS engine (Hermes) starts and exposes a C++ API (jsi::Runtime)

Step 2 → Native (C++) code installs "HostObjects" / "HostFunctions"
         into the JS global scope (e.g. global.nativeFoo)

Step 3 → JS calls global.nativeFoo(10) like a normal function

Step 4 → The call goes straight into C++ -> no JSON, no queue

Step 5 → C++ can return a value immediately (SYNC) or a Promise (ASYNC)

Step 6 → TurboModules, Fabric, Reanimated, MMKV, Skia, VisionCamera
         are all built on top of JSI
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → JS engine (Hermes) start होता है और C++ API (jsi::Runtime) देता है
Step 2 → Native C++ code "HostObject/HostFunction" को JS global में डालता है
         (जैसे global.nativeFoo)
Step 3 → JS उसे normal function की तरह call करती है: nativeFoo(10)
Step 4 → Call सीधे C++ में जाती है -> JSON नहीं, queue नहीं
Step 5 → C++ value तुरंत (SYNC) या Promise (ASYNC) लौटा सकता है
Step 6 → TurboModules, Fabric, Reanimated, MMKV, Skia, VisionCamera
         सब JSI के ऊपर बने हैं
```

---

## 🟡 Real World Example
**Paytm / PhonePe** style apps store tokens and flags in local storage on every launch. With **react-native-mmkv** (built on JSI) a read like `storage.getString('token')` returns **instantly and synchronously**, so the home screen can decide "logged in or not" before the first render. **Swiggy / Zomato** style animated cards and map pins use **Reanimated 3**, which runs worklets on the UI thread through JSI, so the 60 fps scroll animation does not wait for the JS thread.

## 🟡 Real Example Hindi mein
**Paytm / PhonePe** जैसे apps हर launch पर token और flags पढ़ते हैं। **react-native-mmkv** (JSI पर बना) से `storage.getString('token')` **तुरंत और synchronously** मिल जाता है, इसलिए पहले render से पहले ही तय हो जाता है कि user logged in है या नहीं। **Swiggy / Zomato** जैसे animated cards और map pins **Reanimated 3** use करते हैं, जो JSI के ज़रिए UI thread पर worklets चलाता है, इसलिए 60 fps animation JS thread का इंतज़ार नहीं करती।

---

## 💻 Code Example — Basic

```jsx
// Basic: see JSI-powered sync call in action using react-native-mmkv
// Install (Expo dev build needed, NOT Expo Go): npx expo install react-native-mmkv
import React, { useState } from 'react'; // React + state hook
import { View, Text, Pressable, StyleSheet } from 'react-native'; // core UI
import { MMKV } from 'react-native-mmkv'; // MMKV uses JSI under the hood

// Create one storage instance (native C++ object, JS holds a direct reference)
const storage = new MMKV();

export default function JsiBasic() {
  // Read synchronously during first render - no await, no Promise
  const [count, setCount] = useState(storage.getNumber('count') ?? 0);

  // Increment and persist in one synchronous step
  const onPress = () => {
    const next = count + 1; // compute new value
    storage.set('count', next); // sync write straight into native memory
    setCount(next); // update UI state
  };

  return (
    <View style={styles.box}>
      {/* Show the persisted counter */}
      <Text style={styles.text}>Opened-count taps: {count}</Text>
      {/* Button to increment */}
      <Pressable style={styles.btn} onPress={onPress}>
        <Text style={styles.btnText}>Tap (sync save)</Text>
      </Pressable>
    </View>
  );
}

// Styles for the screen
const styles = StyleSheet.create({
  box: { flex: 1, justifyContent: 'center', alignItems: 'center' }, // centre content
  text: { fontSize: 20, marginBottom: 12 }, // counter text
  btn: { backgroundColor: '#E23744', padding: 12, borderRadius: 8 }, // Zomato-red button
  btnText: { color: '#fff', fontWeight: '600' }, // button label
});
```

## 💻 Code Example — Advanced

```jsx
// Advanced: Reanimated worklet runs on the UI thread (JSI), with platform + error handling
// Install: npx expo install react-native-reanimated (Reanimated 3, babel plugin comes with babel-preset-expo)
import React from 'react'; // React
import { Platform, StyleSheet, Text } from 'react-native'; // core
import Animated, {
  useSharedValue, // value that lives on the UI thread (shared via JSI)
  useAnimatedStyle, // style computed on the UI thread
  withSpring, // spring animation helper
} from 'react-native-reanimated'; // Reanimated 3
import { Gesture, GestureDetector } from 'react-native-gesture-handler'; // gestures

export default function DragCard() {
  // Shared values: JS and UI thread see the same memory, no Bridge hop
  const x = useSharedValue(0); // horizontal offset
  const y = useSharedValue(0); // vertical offset

  // Pan gesture: callbacks are worklets that run on the UI thread
  const pan = Gesture.Pan()
    .onUpdate((e) => {
      'worklet'; // marks the function to run on UI thread
      x.value = e.translationX; // follow the finger on X
      y.value = e.translationY; // follow the finger on Y
    })
    .onEnd(() => {
      'worklet'; // still UI thread
      x.value = withSpring(0); // snap back with spring
      y.value = withSpring(0); // snap back with spring
    });

  // Animated style recomputed on the UI thread every frame
  const style = useAnimatedStyle(() => ({
    transform: [{ translateX: x.value }, { translateY: y.value }], // move card
  }));

  // Defensive: warn if a native feature is missing (e.g. running inside plain Expo Go builds with older version)
  if (typeof useSharedValue !== 'function') {
    console.warn('Reanimated not linked correctly'); // error handling
    return <Text>Animation unavailable</Text>; // fallback UI
  }

  return (
    <GestureDetector gesture={pan}>
      {/* Swiggy-style draggable order card */}
      <Animated.View style={[styles.card, style]}>
        <Text style={styles.title}>Drag me ({Platform.OS})</Text>
      </Animated.View>
    </GestureDetector>
  );
}

// Styles
const styles = StyleSheet.create({
  card: {
    width: 220, // fixed width
    padding: 20, // inner space
    borderRadius: 14, // rounded corners
    backgroundColor: '#FC8019', // Swiggy orange
    alignSelf: 'center', // centre horizontally
    marginTop: 120, // push down
    elevation: 4, // Android shadow
    shadowColor: '#000', // iOS shadow colour
    shadowOpacity: 0.2, // iOS shadow strength
    shadowRadius: 6, // iOS blur
  },
  title: { color: '#fff', fontWeight: '700' }, // label
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| JSI layer language | C++ via JNI glue to Kotlin/Java | C++ via Objective-C++ glue |
| JS engine | Hermes (default) | Hermes (default) |
| Native module glue | Kotlin/Java TurboModule + C++ | Objective-C++/Swift TurboModule |
| Sync call overhead | JNI hop is small but not zero | Direct ObjC++ call, very low |
| Debugging | Android Studio + Hermes debugger | Xcode + Hermes debugger |
| Chrome remote debugging | Not usable with JSI sync calls | Not usable with JSI sync calls |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: JSI libraries (MMKV, Reanimated, Skia) need a development build, not Expo Go
// Terminal:
//   npx expo install react-native-mmkv
//   npx expo prebuild          // generate android/ + ios/ folders
//   npx expo run:android       // or: npx expo run:ios (Mac only)
// Reanimated is bundled inside Expo Go, but custom JSI libs are not.
```
CLI way:
```jsx
// CLI: you link everything yourself
// Terminal:
//   npm install react-native-mmkv
//   cd ios && pod install && cd ..   // iOS native deps (Mac only)
//   npx react-native run-android     // or run-ios
// Writing your OWN JSI module = write C++ + register it in MainApplication / AppDelegate
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Thinking JSI and TurboModules are the same thing.
✅ Correct: JSI is the **base layer**. TurboModules (native modules) and Fabric (renderer) are **built on top** of JSI.

❌ Mistake 2: Using JSI libraries (MMKV, Skia) inside **Expo Go**.
✅ Correct: Use a **development build** (`npx expo run:android` or EAS dev build). Expo Go ships only a fixed set of native code.

❌ Mistake 3: Using Chrome remote debugger and expecting JSI sync functions to work.
✅ Correct: Use the **Hermes debugger / React Native DevTools**. Remote JS debugging runs JS in Chrome, where native JSI objects do not exist.

❌ Mistake 4: Doing heavy sync work in a JSI call on the JS thread.
✅ Correct: Sync is fast but it still **blocks** the JS thread. Offload heavy work to a worklet or native thread.

---

## 🧠 Tricky Interview Question
**Q:** "If JSI removes the Bridge, does it mean all native calls are now synchronous and the JS thread can never freeze?"

Answer: **No.** JSI *allows* sync calls, but a library author chooses sync or async. A slow sync call (for example reading a huge file) **blocks the JS thread** and freezes the UI logic. JSI removes serialization cost, not the threading rules. Also, the old Bridge still exists in a compatibility "interop layer" for old modules in New Architecture.

---

## ⚫ Interview Questions + Answers
Q1: What is JSI?
A1: A C++ API of the JS engine that lets JS and native share objects and call each other directly, without JSON serialization.

Q2: How is JSI different from the Bridge?
A2: Bridge = async, batched, JSON messages. JSI = direct reference, sync or async, no serialization.

Q3: Which engines support JSI?
A3: Hermes (default), JavaScriptCore, and V8 (via community builds). JSI is engine-agnostic by design.

Q4: Name libraries built on JSI.
A4: react-native-reanimated 3, react-native-mmkv, react-native-skia, react-native-vision-camera, TurboModules, Fabric.

Q5: Can JSI be used in Expo Go?
A5: Only for libraries already bundled in Expo Go (e.g. Reanimated). Custom JSI libs need a development build.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need synchronous reads (storage, device info) at startup
- Heavy data transfer (images, frames, big arrays)
- High-frequency events (gestures, animations, camera frames)
- Writing a native library for the New Architecture

❌ Avoid when:
- A normal async API (fetch, AsyncStorage) is enough
- Your team has no C++ knowledge and a ready library exists
- You are only learning basics (just use libraries)

---

## 📊 Visual Diagram
```
OLD BRIDGE                          JSI (NEW)
┌────────┐   JSON    ┌────────┐     ┌────────┐         ┌────────┐
│   JS   │ ───────►  │ Native │     │   JS   │ ◄─────► │ Native │
│ thread │ ◄─────── │ thread │     │ engine │ C++ ref │  (C++) │
└────────┘  async    └────────┘     └────────┘ sync/   └────────┘
   serialize + queue                  async, no JSON
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JSI | C++ interface between JS engine and native | JS और native के बीच C++ पुल |
| HostObject | C++ object exposed to JS | JS को दिया गया C++ object |
| HostFunction | C++ function callable from JS | JS से call होने वाला C++ function |
| Serialization | Converting data to JSON/bytes | Data को JSON में बदलना |
| Worklet | JS function that runs on UI thread | UI thread पर चलने वाला function |
| TurboModule | Lazy-loaded native module over JSI | JSI वाला lazy native module |

---

## ⚡ 3-Line Summary
English: JSI is a C++ layer that gives JS direct access to native objects.
It removes JSON serialization and allows synchronous calls.
TurboModules, Fabric, Reanimated and MMKV are all built on it.

Hindi: JSI एक C++ layer है जो JS को native objects तक सीधी पहुँच देती है।
यह JSON serialization हटाती है और sync calls की सुविधा देती है।
TurboModules, Fabric, Reanimated और MMKV सब इसी पर बने हैं।

---

## ➡️ Next Topic
**09. When to Use Expo vs CLI** — now that you know the architecture, you will decide which workflow suits your project and team.

---
