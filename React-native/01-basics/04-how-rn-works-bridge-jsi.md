# 04. How React Native Works — Bridge / JSI
# हिंदी में: React Native काम कैसे करता है — Bridge और JSI
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
React Native has two "worlds" — JavaScript (your code) and Native (Android/iOS). They need to communicate. The **old way** was the **Bridge** — JSON messages sent asynchronously between both sides. The **new way** is **JSI (JavaScript Interface)** — direct memory access between JS and Native, much faster, synchronous.

## 🔵 सरल परिभाषा (Hindi)
React Native के दो "worlds" हैं — JavaScript (आपका code) और Native (Android/iOS)। इन्हें communicate करना होता है। **पुराना तरीका** था **Bridge** — दोनों sides के बीच JSON messages asynchronously भेजे जाते थे। **नया तरीका** है **JSI (JavaScript Interface)** — JS और Native के बीच direct memory access, बहुत fast, synchronous।

---

## 🔴 Problem it Solves
```
PROBLEM WITH OLD BRIDGE:
❌ Every message had to be serialized to JSON (slow)
❌ Communication was asynchronous (delay)
❌ JS thread blocked during heavy operations
❌ Dropped frames during complex animations
❌ Large data transfers were expensive

JSI SOLUTION:
✅ JS can directly reference C++ objects (no serialization)
✅ Synchronous calls possible
✅ Much faster native module calls
✅ Enables Fabric (new renderer) + TurboModules
```

## 🔴 यह क्यों बना? (Hindi)
```
Bridge की problems:
❌ हर message JSON में serialize करना → slow
❌ Asynchronous → delay
❌ Heavy operations पर frames drop
JSI: direct memory access → fast, synchronous possible
```

---

## 🟢 How it Works — Step by Step

```
OLD ARCHITECTURE (Bridge):
────────────────────────────────────────────
  Step 1 → Your JS code calls a native function
           e.g., camera.takePicture()

  Step 2 → React Native serializes call to JSON
           '{"module":"Camera","method":"takePicture","args":{}}'

  Step 3 → JSON message sent across the Bridge (async)
           JS Thread → [BRIDGE] → Native Thread

  Step 4 → Native Thread deserializes JSON, executes
           Takes picture...

  Step 5 → Result serialized back to JSON
           '{"success":true,"uri":"file://..."}'

  Step 6 → JSON sent back across Bridge
           Native Thread → [BRIDGE] → JS Thread

  Step 7 → JS deserializes, resolves Promise
           ❌ SLOW: double serialization, async overhead

NEW ARCHITECTURE (JSI):
────────────────────────────────────────────
  Step 1 → JS engine (Hermes) gets a C++ host object
           cameraRef.current → direct JS ref to C++ Camera object

  Step 2 → JS calls method DIRECTLY on C++ object
           cameraRef.takePicture() → direct call, NO JSON!

  Step 3 → C++ Camera module executes natively

  Step 4 → Returns result DIRECTLY to JS (can be synchronous!)
           ✅ FAST: no serialization, direct memory access
```

## 🟢 कैसे काम करता है? (Hindi)
```
OLD BRIDGE:
JS → JSON serialize → Bridge → JSON deserialize → Native
Native → JSON serialize → Bridge → JSON deserialize → JS
Double serialization = slow!

NEW JSI:
JS → Direct C++ object reference → Native
No JSON, no serialization = fast!
Synchronous calls possible!
```

---

## 🟡 Real World Example
**Zomato Live Tracking:** The map updates every second with delivery partner's location. Old Bridge: 60fps animation was hard — JSON serialization 60 times/second caused dropped frames. With Reanimated v3 (uses JSI): animations run entirely on the UI thread — buttery smooth 60/120fps even while JS thread is busy fetching data.

## 🟡 Real Example Hindi मे
**Zomato Live Tracking:** Map हर second update होता है। Old Bridge: 60fps animation मुश्किल था — JSON serialize/deserialize 60 बार/second frames drop करता था। Reanimated v3 (JSI use करता है): animations UI thread पर ही run — 60/120fps smooth, चाहे JS thread busy हो।

---

## 💻 Code Example — Basic

```jsx
// Understanding threads through code behavior
import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

// React Native has 3 threads:
// 1. JS Thread — your JavaScript code runs here
// 2. UI Thread (Main Thread) — renders native components
// 3. Native Modules Thread — background native operations

function ThreadDemo() {
  const [status, setStatus] = useState('Ready');

  // This runs on JS Thread
  const doHeavyJSWork = () => {
    setStatus('JS Thread busy...');

    // Simulate heavy JS computation (blocks JS thread)
    let sum = 0;
    for (let i = 0; i < 100_000_000; i++) {
      sum += i;
    }

    setStatus(`Done: ${sum}`);
    // During this loop:
    // - Old Bridge: UI animations that need JS thread FREEZE!
    // - New Architecture: UI Thread can still run animations
    //   because Fabric (new renderer) doesn't block on JS
  };

  // This runs on Native Thread (via bridge/JSI)
  const takePhoto = async () => {
    setStatus('Taking photo...');
    // Actual camera work happens on Native Thread
    // JS Thread is freed immediately (async)
    // const photo = await Camera.takePicture(); // native module call
    setStatus('Photo taken!');
  };

  return (
    <View style={styles.container}>
      <Text style={styles.status}>{status}</Text>
      <TouchableOpacity style={styles.btn} onPress={doHeavyJSWork}>
        <Text style={styles.btnText}>Heavy JS Work</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.btn} onPress={takePhoto}>
        <Text style={styles.btnText}>Take Photo (Native)</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  status: { fontSize: 16, marginBottom: 20, color: '#333' },
  btn: {
    backgroundColor: '#f97316',
    padding: 16,
    borderRadius: 8,
    marginVertical: 8,
    width: 200,
    alignItems: 'center',
  },
  btnText: { color: '#fff', fontWeight: '700' },
});
```

## 💻 Code Example — Advanced

```jsx
// JSI in action via Reanimated v3 (uses JSI for 60fps animations)
// npm install react-native-reanimated

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue,      // JSI: lives in native memory
  useAnimatedStyle,    // JSI: runs on UI thread (no bridge!)
  withSpring,          // native animation driver
  withTiming,
} from 'react-native-reanimated';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';

// This component's animation logic runs on UI Thread via JSI
// Even if JS Thread is busy → animation still smooth!
function JSIAnimatedCard() {
  // useSharedValue: lives in C++ memory, accessible from both JS and UI thread
  const translateX = useSharedValue(0);
  const scale = useSharedValue(1);

  // Gesture runs on UI thread — no bridge lag!
  const panGesture = Gesture.Pan()
    .onUpdate((event) => {
      translateX.value = event.translationX; // direct JSI write!
    })
    .onEnd(() => {
      translateX.value = withSpring(0); // spring back
    });

  const tapGesture = Gesture.Tap()
    .onStart(() => {
      scale.value = withTiming(0.95, { duration: 100 });
    })
    .onEnd(() => {
      scale.value = withTiming(1, { duration: 100 });
    });

  const composedGesture = Gesture.Simultaneous(panGesture, tapGesture);

  // useAnimatedStyle: computed on UI thread (not JS thread!)
  // This is why it's smooth even during JS thread work
  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: translateX.value },
      { scale: scale.value },
    ],
  }));

  return (
    <GestureDetector gesture={composedGesture}>
      <Animated.View style={[styles.card, animatedStyle]}>
        <Text style={styles.cardText}>Drag Me (JSI powered!)</Text>
        <Text style={styles.cardSubtext}>Runs on UI Thread</Text>
      </Animated.View>
    </GestureDetector>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#f97316',
    padding: 24,
    borderRadius: 16,
    alignItems: 'center',
    margin: 20,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
  },
  cardText: { color: '#fff', fontSize: 18, fontWeight: '700' },
  cardSubtext: { color: '#fff', fontSize: 12, marginTop: 4, opacity: 0.8 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| JS Engine | Hermes (default) | Hermes (default, also JSC) |
| Native language | Java / Kotlin | Objective-C / Swift |
| Bridge thread | Background thread | Background thread |
| UI Thread | Main Thread | Main Thread |
| JSI availability | React Native 0.66+ | React Native 0.66+ |

---

## 🟠 Expo vs CLI Difference

Expo way:
```
Expo SDK 50+ uses New Architecture by default
In app.json:
{
  "expo": {
    "newArchEnabled": true
  }
}
Expo handles all the native config — you don't touch it!
```

CLI way:
```
In android/gradle.properties:
newArchEnabled=true

In ios/Podfile:
ENV['RCT_NEW_ARCH_ENABLED'] = '1'
pod install

More manual but more control
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Blocking the JS Thread with heavy computation
```jsx
// WRONG: heavy loop blocks JS thread → UI freezes
const handlePress = () => {
  let result = 0;
  for (let i = 0; i < 1_000_000_000; i++) result += i; // ❌ UI freezes!
  setResult(result);
};

// CORRECT: use requestAnimationFrame or move to native module
const handlePress = () => {
  // For truly heavy work: use a native module or Web Worker equivalent
  // For medium work: break into chunks with requestAnimationFrame
  InteractionManager.runAfterInteractions(() => {
    // runs after animations/interactions complete
    let result = heavyComputation();
    setResult(result);
  });
};
```

❌ **Mistake 2:** Not knowing which thread your animation runs on
```jsx
// WRONG: Animated API (old) drives animations from JS thread
// Complex state-driven animations may lag if JS thread is busy
const opacity = useRef(new Animated.Value(0)).current;
// Runs on JS thread — can lag!

// CORRECT: Reanimated v3 — animations on UI thread via JSI
import { useSharedValue, withTiming } from 'react-native-reanimated';
const opacity = useSharedValue(0); // C++ shared value
opacity.value = withTiming(1);    // runs on UI thread via JSI ✅
```

---

## 🧠 Tricky Interview Question

**Q: Why does the user sometimes see janky animations in React Native even though they're using `Animated.timing`?**

**Answer:** `Animated.timing` (old API) drives animations from the **JS Thread** by default. If the JS Thread is busy (fetching data, parsing large JSON, re-rendering complex component trees), animation frames are dropped. The UI thread is waiting for values from JS, which never arrives on time. **Fix**: Use `useNativeDriver: true` on Animated (moves to UI thread) or better, use **Reanimated v3** (`withTiming`, `withSpring`) which uses JSI to run animations entirely on the UI thread — JS thread activity has zero impact.

---

## ⚫ Interview Questions + Answers

**Q1: What is the Bridge in React Native?**
A1: The Bridge is the old communication mechanism between the JavaScript thread and the Native thread. It serializes all messages to JSON, sends them asynchronously across the bridge, and deserializes on the other side. Problems: (1) All data must be serializable to JSON. (2) Communication is asynchronous only. (3) Large/frequent messages cause performance issues. (4) Can't hold references to native objects. It's been replaced by JSI in the New Architecture.

**Q2: What is JSI (JavaScript Interface)?**
A2: JSI is the new architecture's communication layer. Instead of JSON messages, JSI allows the JavaScript engine to hold **direct C++ object references**. You can call C++ functions directly from JavaScript synchronously, without serialization overhead. JSI enables: TurboModules (lazy-loaded native modules via JSI), Fabric (new renderer), Reanimated v3 (UI thread animations), and makes React Native significantly faster.

**Q3: What are the three threads in React Native?**
A3: (1) **JS Thread**: Runs JavaScript code — your business logic, state updates, React reconciliation. (2) **UI Thread (Main Thread)**: Renders native components, handles user touch input. Should never be blocked. (3) **Native Modules Thread**: Runs async native operations (camera, network, file system). With New Architecture, there's also a **Background Thread** for concurrency.

**Q4: Why are animations sometimes janky in React Native?**
A4: Old `Animated` API drives animations from the JS Thread. If JS Thread is busy (data fetching, JSON parsing), animation frame updates are delayed → dropped frames → jank. Solutions: (1) `useNativeDriver: true` on Animated — moves to UI thread. (2) Reanimated v3 with `useSharedValue` + `withTiming/withSpring` — runs entirely on UI thread via JSI. (3) Keep JS Thread work minimal during animations.

**Q5: What is the New Architecture in React Native?**
A5: New Architecture = JSI + Fabric + TurboModules. **JSI**: direct C++ communication, no JSON bridge. **Fabric**: new synchronous renderer that replaces the async Shadow Thread — enables synchronous layout calculations and better concurrent React support. **TurboModules**: lazy-loaded native modules via JSI — only the modules you actually use get loaded at startup. Together: better performance, React 18 concurrent features support, synchronous capabilities.

---

## 🔷 When to Use + When Not to Use
✅ **Enable New Architecture when:**
- New project starting fresh
- Need 60/120fps smooth animations (Reanimated v3)
- Using Expo SDK 50+ (auto-enabled)
- React Native 0.71+

❌ **Stick with old architecture when:**
- Legacy project with many third-party native modules that haven't updated
- Critical production app where testing time is limited
- Native modules that use old Bridge APIs (will break with JSI)

---

## 📊 Visual Diagram

```
OLD ARCHITECTURE (Bridge):
──────────────────────────────────────────────────────
  JS Thread          BRIDGE              Native Thread
  ┌──────────┐    ┌──────────┐         ┌────────────┐
  │ Your JS  │    │          │         │ Camera,    │
  │ code     │───►│  JSON    │────────►│ Location,  │
  │          │◄───│ Messages │◄────────│ Storage    │
  └──────────┘    └──────────┘         └────────────┘
  Asynchronous, serialization overhead, no direct references

NEW ARCHITECTURE (JSI):
──────────────────────────────────────────────────────
  JS Thread (Hermes)          C++ Layer
  ┌──────────────────┐       ┌──────────────────────┐
  │ Your JS code     │       │ TurboModules         │
  │                  │◄─────►│ Fabric Renderer      │
  │ Holds direct     │  JSI  │ Shared C++ Values    │
  │ C++ references   │       │ (Reanimated, etc.)   │
  └──────────────────┘       └──────────────────────┘
  Direct memory access, sync possible, no serialization

THREAD MODEL:
──────────────────────────────────────────────────────
  JS Thread ──── State, Logic, React rendering
  UI Thread ──── Native component rendering, touches
  BG Thread ──── Network, file I/O, camera
  (all run in parallel — don't block each other!)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bridge | Old JSON-based JS↔Native communication | पुराना JSON-based communication |
| JSI | New direct C++ JS↔Native communication | नया direct C++ communication |
| JS Thread | Thread running JavaScript code | JavaScript code चलाने वाला thread |
| UI Thread | Thread rendering native components | Native components render करने वाला |
| TurboModules | Lazy native modules via JSI | JSI से lazy-loaded native modules |
| Fabric | New native renderer | नया native renderer |
| Hermes | Optimized JS engine for RN | RN के लिए optimized JS engine |
| Serialization | Converting data to JSON string | Data को JSON string में convert करना |

---

## ⚡ 3-Line Summary
**English:**
1. React Native has two worlds — JavaScript and Native — that communicate via Bridge (old, JSON, async) or JSI (new, C++ direct, can be sync).
2. Three threads: JS Thread (your code), UI Thread (rendering, touches), Native Thread (device APIs) — never block the UI thread.
3. New Architecture (JSI + Fabric + TurboModules) = faster, synchronous, enables Reanimated v3's 60fps animations on UI thread.

**Hindi:**
1. React Native के दो worlds — JavaScript और Native — जो Bridge (पुराना, JSON, async) या JSI (नया, C++ direct, sync) से communicate करते हैं।
2. तीन threads: JS Thread (आपका code), UI Thread (rendering, touches), Native Thread (device APIs) — UI thread कभी block मत करो।
3. New Architecture (JSI + Fabric + TurboModules) = faster, synchronous, Reanimated v3 के UI thread पर 60fps animations।

---

## ➡️ Next Topic
**08. Expo vs React Native CLI** — दोनों approaches कब use करें — advantages, limitations, और कब switch करें।
