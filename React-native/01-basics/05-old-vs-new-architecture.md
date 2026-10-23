# 05. Old Architecture vs New Architecture
# हिंदी में: पुरानी Architecture vs नई Architecture
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
React Native's **Old Architecture** (pre-2022) had the Bridge at its core — all JS↔Native communication went through JSON messages asynchronously. The **New Architecture** (2022–present, default in RN 0.74+) replaces the Bridge with JSI, replaces the async renderer with Fabric, and replaces eager-loaded native modules with lazy TurboModules.

## 🔵 सरल परिभाषा (Hindi)
React Native की **Old Architecture** (2022 से पहले) में Bridge core था — सब JS↔Native communication JSON messages से asynchronously होती थी। **New Architecture** (2022–present, RN 0.74+ में default) Bridge को JSI से, async renderer को Fabric से, और eager-loaded native modules को lazy TurboModules से replace करती है।

---

## 🔴 Problem it Solves
```
OLD ARCHITECTURE PROBLEMS:
❌ All data must be JSON-serializable (no ArrayBuffer, no BigInt)
❌ Always async — can't make sync native calls
❌ ALL native modules loaded at startup (slow startup time)
❌ Shadow Thread separate from UI Thread — sync layout impossible
❌ React 18 concurrent features impossible (async rendering needed)
❌ 60fps animation from JS thread was unreliable

NEW ARCHITECTURE SOLUTIONS:
✅ JSI: any JS type can reference native, no serialization limit
✅ Synchronous calls possible when needed
✅ TurboModules: lazy load — only used modules initialize
✅ Fabric: sync layout, direct UIManager access
✅ React 18 Concurrent Mode works!
✅ Reanimated v3 on UI thread = guaranteed 60/120fps
```

## 🔴 यह क्यों बना? (Hindi)
```
Old Architecture की problems:
- JSON serialization slow + limited
- All modules startup पर load = slow start
- React 18 Concurrent Mode support नहीं

New Architecture:
- JSI = direct C++ access, no JSON
- TurboModules = lazy load = fast startup
- Fabric = sync renderer = React 18 support ✅
```

---

## 🟢 How it Works — Step by Step

```
OLD ARCHITECTURE — 4 Threads:
──────────────────────────────────────────────────────
  1. JS Thread
     - Runs JavaScript (your app code)
     - Communicates via Bridge only (async)

  2. Shadow Thread
     - Runs Yoga layout engine
     - Calculates positions/sizes
     - Sends results to UI Thread (async!)

  3. UI Thread (Main Thread)
     - Receives layout from Shadow Thread
     - Renders native components
     - Handles user input

  4. Native Modules Thread
     - Runs camera, location, storage, etc.
     - Communicates with JS via Bridge

  PROBLEM: Everything is async, JSON-serialized, 3 threads need sync!

NEW ARCHITECTURE — Streamlined:
──────────────────────────────────────────────────────
  1. JS Thread (Hermes engine)
     - Uses JSI to hold C++ references directly
     - Can call TurboModules synchronously

  2. UI Thread + Fabric Renderer
     - Fabric can be called synchronously from JS via JSI
     - Layout calculation (Yoga) integrated, not separate thread
     - "Commits" happen synchronously when needed

  3. Background Thread
     - Handles truly async work (network, file I/O)
     - TurboModules live here for async operations

  BENEFIT: Fewer async hops, sync when needed, no JSON overhead!
```

## 🟢 कैसे काम करता है? (Hindi)
```
OLD: JS Thread → Bridge (JSON) → Shadow Thread → UI Thread
     हर step async + JSON serialize = slow!

NEW: JS Thread → JSI (direct C++) → Fabric → UI Thread  
     Direct access, sync possible, no JSON = fast!
```

---

## 🟡 Real World Example
**PhonePe UPI Payments:** Old Architecture: tapping "Pay" button triggers a chain — JS serializes to JSON, Bridge sends to Native, Native does fingerprint auth, result serialized back, Bridge returns to JS. Multiple async hops = 200-400ms delay felt by user. New Architecture: JS calls biometric native module synchronously via JSI — fingerprint result comes back in the same call frame — perceived as instant response.

## 🟡 Real Example Hindi मे
**PhonePe UPI:** Old: "Pay" button tap → JSON serialize → Bridge → Native fingerprint → JSON back → Bridge → JS = 200-400ms delay। New: JSI से directly native fingerprint module call → instant response।

---

## 💻 Code Example — Basic

```jsx
// Checking which architecture is running
import { TurboModuleRegistry } from 'react-native';

// TurboModuleRegistry is available only in New Architecture
// Old Architecture uses NativeModules (always fully loaded)
const isNewArchitecture = TurboModuleRegistry !== undefined;

console.log(
  isNewArchitecture
    ? '✅ New Architecture (JSI + TurboModules)'
    : '⚠️ Old Architecture (Bridge)'
);

// In New Architecture: modules are loaded lazily
// const cameraModule = TurboModuleRegistry.get('RNCCamera');
// → only loaded when first accessed, not at startup!

// In Old Architecture: ALL modules loaded at startup
// require('@react-native-camera/camera'); → camera loads immediately
```

## 💻 Code Example — Advanced

```jsx
// Reanimated v3 ONLY works smoothly with New Architecture
// (It does work on old arch but loses some sync benefits)
import Animated, {
  useSharedValue,     // stored in C++ (JSI)
  useAnimatedStyle,   // runs on UI thread (Fabric + JSI)
  withSpring,
  runOnJS,            // explicitly call JS from UI thread
  runOnUI,            // explicitly call UI thread from JS
} from 'react-native-reanimated';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import { View, Text, StyleSheet } from 'react-native';

function NewArchDemo() {
  const offsetY = useSharedValue(0);   // C++ shared value
  const isActive = useSharedValue(false);

  // This entire gesture handler runs on UI Thread (Fabric)
  // No JS Thread involvement during dragging!
  const panGesture = Gesture.Pan()
    .onBegin(() => {
      isActive.value = true;  // direct UI thread write
    })
    .onUpdate((e) => {
      offsetY.value = e.translationY;   // no bridge, direct!
    })
    .onEnd(() => {
      offsetY.value = withSpring(0);    // spring physics, UI thread
      isActive.value = false;
      // runOnJS to call JS thread from UI thread (if needed)
      runOnJS(console.log)('Drag ended — calling JS from UI thread');
    });

  // Computed on UI thread — guaranteed smooth even if JS is busy
  const animStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: offsetY.value }],
    backgroundColor: isActive.value ? '#ea580c' : '#f97316',
  }));

  return (
    <GestureDetector gesture={panGesture}>
      <Animated.View style={[styles.box, animStyle]}>
        <Text style={styles.text}>Drag Me</Text>
        <Text style={styles.sub}>UI Thread powered (New Arch)</Text>
      </Animated.View>
    </GestureDetector>
  );
}

const styles = StyleSheet.create({
  box: {
    width: 200, height: 80,
    borderRadius: 12, justifyContent: 'center', alignItems: 'center',
    margin: 20,
  },
  text: { color: '#fff', fontWeight: '700', fontSize: 16 },
  sub: { color: '#fff', fontSize: 11, opacity: 0.8 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| New Arch default | RN 0.74+ | RN 0.74+ |
| Hermes default | RN 0.64+ | RN 0.64+ |
| Enable flag | `android/gradle.properties` | `ios/Podfile` ENV var |
| Play Store impact | Smaller APK with Hermes | App Store same |

---

## 🟠 Expo vs CLI Difference

Expo way:
```json
// app.json — New Architecture enabled by default in SDK 50+
{
  "expo": {
    "newArchEnabled": true
  }
}
// No native files to touch — Expo handles everything
```

CLI way:
```
android/gradle.properties:
  newArchEnabled=true

ios/Podfile:
  ENV['RCT_NEW_ARCH_ENABLED'] = '1'

Then:
  cd ios && pod install
  npx react-native run-android
  npx react-native run-ios
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Enabling New Architecture without checking library compatibility
```bash
# WRONG: Enable new arch, then crash on production
# Many older libraries DON'T support New Architecture yet

# CORRECT: Check before enabling
# 1. Search https://reactnative.directory with "new arch" filter
# 2. Check library's GitHub for "New Architecture" support status
# 3. Test thoroughly on both platforms before release

# Libraries that need checking:
# ❌ react-native-maps (check version carefully)
# ❌ older react-native-firebase versions
# ✅ react-native-reanimated v3 — fully supports New Arch
# ✅ react-native-gesture-handler v2+ — supports New Arch
```

❌ **Mistake 2:** Assuming New Architecture = automatic performance improvement
```
// Wrong expectation: "Just enable new arch → app becomes fast"
// Reality: 
// - Most performance issues are BAD CODE (heavy JS thread, bad FlatList usage)
// - New Arch helps with: animations, startup time, sync operations
// - New Arch doesn't fix: unnecessary re-renders, large bundle size, 
//   slow API calls, unoptimized images, bad state management
```

---

## 🧠 Tricky Interview Question

**Q: If New Architecture is so much better, why don't all apps use it?**

**Answer:** Three reasons: (1) **Library compatibility** — thousands of React Native libraries rely on the old Bridge API. Migrating takes time; many popular libraries (Firebase, Maps) only recently completed New Architecture support. (2) **Migration risk** — existing production apps work fine on old arch. Enabling New Architecture can break subtle things (gesture handling, animation timing). The "if it ain't broke, don't fix it" mindset. (3) **Gradual rollout** — Meta itself rolled it out to Facebook/Instagram gradually, testing on millions of devices. New projects should use it; old projects should migrate carefully with extensive testing.

---

## ⚫ Interview Questions + Answers

**Q1: What are the 3 main changes in React Native's New Architecture?**
A1: (1) **JSI (JavaScript Interface)**: replaces the Bridge — JS holds direct C++ references, sync calls possible, no JSON serialization. (2) **Fabric**: new native renderer — replaces the async Shadow Thread, enables synchronous layout, supports React 18 concurrent features. (3) **TurboModules**: lazy-loaded native modules — only modules you use are initialized, improving startup time.

**Q2: What was the Bridge and why was it a problem?**
A2: The Bridge was the only communication channel between JS Thread and Native Thread. Every message was serialized to a JSON string, sent async, and deserialized on the other side. Problems: (1) All data must be JSON-serializable (no typed arrays, etc.). (2) Everything is async — can't get sync results. (3) High overhead from double serialization. (4) Bottleneck at high message frequency (animations at 60fps). (5) All native modules loaded eagerly = slow startup.

**Q3: What is Fabric in React Native?**
A3: Fabric is the new native renderer (replaces UIManager). Old renderer used a separate Shadow Thread for layout calculations — results came back async. Fabric integrates layout calculation with the rendering pipeline and uses JSI for synchronous access. Key benefits: (1) Can render synchronously (useful for `<Suspense>` boundaries). (2) Supports React 18 concurrent features (startTransition, etc.). (3) Direct C++ access from JS via JSI.

**Q4: What are TurboModules?**
A4: TurboModules are the New Architecture's native module system. Old system: ALL native modules (camera, location, contacts, etc.) were loaded and initialized at app startup — even if never used. TurboModules: lazy-loaded, initialized only when first accessed via JSI. Result: faster startup time (only loads what you need), better memory usage, and synchronous access possible.

**Q5: How do you enable New Architecture in an Expo app?**
A5: In `app.json`: `{ "expo": { "newArchEnabled": true } }`. Expo SDK 50+ enables it by default for new projects. Then rebuild: `npx expo run:android` / `npx expo run:ios` (not just `npx expo start`). With EAS Build: `eas build --platform android` will use the setting automatically. Note: This requires a native build — Expo Go doesn't support New Architecture apps.

---

## 🔷 When to Use + When Not to Use
✅ **Enable New Architecture when:**
- New project (2024+) — always start with it
- Expo SDK 50+ — it's the default
- Need Reanimated v3 / Gesture Handler v2 best performance
- Need React 18 concurrent features

❌ **Stay on Old Architecture when:**
- Existing large project with unconfirmed library compatibility
- Using libraries that haven't migrated yet
- Don't have time for thorough testing before next release

---

## 📊 Visual Diagram

```
OLD ARCHITECTURE:
────────────────────────────────────────────────────────
  ┌─────────────┐    ┌──────────────────────────┐
  │  JS Thread  │    │       BRIDGE              │
  │  Your code  │◄──►│  JSON serialization       │
  │  Yoga calc  │    │  Async message queue      │
  └─────────────┘    └──────────┬───────────────┘
                                │
         ┌──────────────────────┼──────────────────┐
         ▼                      ▼                  ▼
  ┌─────────────┐    ┌──────────────────┐   ┌──────────────┐
  │Shadow Thread│    │  Native Modules  │   │  UI Thread   │
  │Layout calc  │    │  (ALL loaded)    │   │  (Main)      │
  └─────────────┘    └──────────────────┘   └──────────────┘

NEW ARCHITECTURE:
────────────────────────────────────────────────────────
  ┌──────────────────┐     JSI      ┌──────────────────────┐
  │   JS Thread      │◄────────────►│   C++ Layer          │
  │   (Hermes)       │   Direct     │   TurboModules       │
  │   Holds C++ refs │   memory     │   Fabric Renderer    │
  └──────────────────┘              └──────────┬───────────┘
                                               │
                                    ┌──────────▼───────────┐
                                    │   UI Thread (Main)   │
                                    │   Native components  │
                                    └──────────────────────┘
  Key difference: No Bridge, no JSON, sync possible!
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Old Architecture | Bridge-based RN system | Bridge-based RN system |
| New Architecture | JSI + Fabric + TurboModules | JSI + Fabric + TurboModules |
| Fabric | New synchronous native renderer | नया synchronous native renderer |
| TurboModules | Lazy-loaded native modules via JSI | Lazy-loaded native modules |
| Shadow Thread | Old separate layout thread | पुराना separate layout thread |
| React 18 | Concurrent React (startTransition, etc.) | Concurrent React features |
| Yoga | Layout engine (flexbox) | Layout engine (flexbox) |

---

## ⚡ 3-Line Summary
**English:**
1. Old Architecture used an async JSON Bridge for all JS↔Native communication — slow, limited to JSON types, all modules loaded at startup.
2. New Architecture (RN 0.74+ default) uses JSI (direct C++ access) + Fabric (sync renderer) + TurboModules (lazy modules) — faster, synchronous possible, smaller startup cost.
3. Enable in new projects; migrate existing projects carefully after verifying all third-party libraries support New Architecture.

**Hindi:**
1. Old Architecture async JSON Bridge use करती थी — slow, JSON types तक limited, सारे modules startup पर load।
2. New Architecture (RN 0.74+ default) JSI (direct C++ access) + Fabric (sync renderer) + TurboModules (lazy modules) use करती है — faster, synchronous possible।
3. New projects में हमेशा enable करो; existing projects में carefully migrate करो — सभी third-party libraries की compatibility check करने के बाद।

---

## ➡️ Next Topic
**06. JSI — JavaScript Interface** — JSI अंदर से कैसे काम करता है, C++ host objects, synchronous native calls।
