# M02. How React Native Works (Bridge vs New Architecture — JSI, Fabric, TurboModules)
# हिंदी में: React Native अंदर से कैसे काम करता है — JavaScript में लिखा React code असली native iOS/Android views कैसे बनाता है; पुराना "Bridge" तरीका और नया Architecture (JSI, Fabric, TurboModules) जो इसे तेज़ और सीधा बनाता है

---

## 🔵 Simple Definition (English)
**React Native (RN)** lets you write React components in JavaScript/TypeScript that render **real native UI views** (`UIView` on iOS, `android.view.View` on Android), not a WebView.
Key moving parts:
- A **JavaScript engine** (**Hermes** by default) runs your React code.
- A **renderer** turns the React tree into native views, with **Yoga** computing flexbox layout.
- **Native modules** expose platform APIs (camera, storage, Bluetooth) to JS.
Two architectures:
- **Old architecture (Bridge)**: JS and native communicate through an **asynchronous, batched, JSON-serialized message queue**. It's simple, but has serialization overhead, no synchronous calls, and all native modules are initialized at startup.
- **New Architecture** (default since RN 0.76; legacy removed in recent versions):
  - **JSI (JavaScript Interface)**: C++ API letting JS hold references to native objects and call them **directly (sync or async)**, with no JSON bridge.
  - **Fabric**: the new **renderer** with a C++ shadow tree, synchronous layout when needed, and support for **React 18+ concurrent features**.
  - **TurboModules**: **lazily loaded**, type-safe native modules over JSI.
  - **Codegen**: generates C++/Java/ObjC glue from TypeScript specs, giving type safety across the boundary.
  - **Bridgeless mode**: the bridge is fully removed.

## 🔵 सरल परिभाषा (Hindi)
React Native में आप JavaScript/TypeScript में React components लिखते हैं और वो असली native views बनाते हैं (WebView नहीं)। Hermes engine JS चलाता है, renderer React tree को native views में बदलता है (layout Yoga गिनता है), और native modules camera/storage जैसे फ़ोन के APIs JS को देते हैं।
पुराना तरीका "Bridge" — JS और native के बीच JSON messages की async कतार (धीमा, sync call नहीं, सारे modules start पर लोड)। नया Architecture — JSI (JS सीधे native objects को call करे), Fabric (नया renderer, concurrent React), TurboModules (ज़रूरत पर लोड होने वाले typed modules), Codegen (TypeScript से glue code)।

---

## 🔴 Problem it Solves
**Why RN exists:** building the same app twice (Swift + Kotlin) doubles cost and slows teams. Web skills (React) can't directly build native apps, and hybrid WebView apps (Cordova) felt slow and non-native. RN gives **one codebase, native UI, web-like developer experience (fast refresh) and OTA updates**.

**Why the New Architecture exists:** the bridge caused real problems at scale:
- **Serialization overhead**: every call and every UI update is converted to JSON and copied, which is slow for large data and frequent events (scroll, gestures, animations).
- **Async-only**: you can't measure a view synchronously, so you get layout jumps and "flicker" (e.g., tooltips positioned a frame late).
- **Startup cost**: all native modules are initialized eagerly, even unused ones.
- **No type safety** between JS and native, and **no concurrent React** (Suspense, transitions) in rendering.

## 🔴 यह क्यों बना? (Hindi)
RN क्यों: एक ही ऐप Swift और Kotlin में दो बार बनाना = दोगुना ख़र्च; WebView वाले hybrid ऐप धीमे लगते थे। RN = एक codebase, असली native UI, React जैसा developer अनुभव, OTA updates।
नया Architecture क्यों: Bridge में हर call/UI update JSON बनकर copy होता (scroll, gestures पर धीमा), सिर्फ़ async (view का size तुरंत नहीं नाप सकते → झपकना), सारे native modules start पर लोड (धीमा startup), JS-native के बीच types नहीं, और concurrent React नहीं चलता था।

---

## 🟢 How it Works — Step by Step

### Threads in a React Native app

```
┌──────────────────────┐  ┌──────────────────────────┐  ┌─────────────────────────────┐
│ JS thread            │  │ UI / main thread         │  │ Background threads          │
│ - Hermes runs React  │  │ - native views drawn     │  │ - native modules work       │
│ - your components,   │  │ - touch events captured  │  │   (network, DB, image decode)│
│   state, business    │  │ - native animations      │  │ - (old arch) shadow thread   │
│   logic              │  │   (Reanimated worklets)  │  │   for Yoga layout            │
└──────────────────────┘  └──────────────────────────┘  └─────────────────────────────┘
If the JS thread is busy (heavy loop, big JSON parse) → taps/JS animations lag even though the
UI thread is free. If the UI thread is busy → dropped frames everywhere. (Topic M14)
```

### Old architecture: the Bridge

```
JS thread                         BRIDGE (async, batched, JSON)                 Native
──────────                        ─────────────────────────────                ──────
React diff → "createView(tag 12, 'RCTView', {style...})"  ──serialize──►  UIManager creates UIView
Camera.takePicture() ──► {"module":"Camera","method":"take","args":[...]} ──► native module runs
                     ◄── {"callbackId": 7, "result": "file://..."} ◄────────── result (async)
onScroll events (60/s) ◄────────── serialized JSON every frame ◄──────────────── native scroll
Problems: copies + JSON for everything; can't call sync; queue congestion during heavy traffic
```

### New Architecture: JSI + Fabric + TurboModules

```
JS (Hermes) ──JSI (C++ host objects/functions)──► C++ core ──► iOS (ObjC++/Swift) / Android (JNI/Kotlin)
   - JS holds a reference to a native object and calls methods directly (sync or async)
   - no JSON serialization; shared memory possible (e.g., MMKV, VisionCamera frame processors, Skia)

Fabric renderer:
  React (reconciler) → commit → C++ SHADOW TREE (immutable, shared across threads)
     → Yoga layout (can run synchronously on UI thread when needed, e.g., measuring)
     → mount: create/update host views on the UI thread
  + Concurrent React: Suspense, transitions, automatic batching
  + Synchronous layout reads (measure) → no flicker for tooltips/popovers
  + View flattening: removes "layout-only" Views from the native hierarchy → fewer native views

TurboModules:
  Loaded lazily on first use (faster startup), typed via Codegen specs, callable over JSI
Codegen:
  TypeScript spec (NativeMyModule.ts) → generated C++/ObjC/Java interfaces → compile-time type safety
Bridgeless mode: no bridge at all; interop layers let most old-arch libraries keep working
```

### Rendering pipeline (Fabric) for one state update

```
setState → React render (JS thread) → diff → commit new shadow tree (C++)
→ layout (Yoga) → diff with previous tree → mount operations → UI thread updates native views → frame
Phases are: Render (JS) → Commit (layout) → Mount (UI)
```

### Ecosystem layers you'll mention

```
Expo: managed toolchain (EAS Build/Update, config plugins, Expo Modules API in Swift/Kotlin, Expo Router)
React Navigation / Expo Router: native-stack uses native navigation primitives
Reanimated: animations as "worklets" on the UI thread (smooth even if JS is busy)
Gesture Handler: native gesture recognition
FlashList: recycling list (M13); MMKV: JSI-based fast storage (M05); VisionCamera: JSI frame processors
React Native Skia: GPU 2D drawing via JSI
```

## 🟢 कैसे काम करता है? (Hindi)
1. तीन मुख्य धागे: JS thread (Hermes पर React और आपका logic), UI thread (native views बनाना, touch, native animations), background threads (network, DB, image decode); JS thread भारी काम में फँसा हो तो taps और JS animations अटकते हैं।
2. पुराना Bridge: JS और native के बीच हर बात JSON बनकर async कतार से जाती — copy का ख़र्च, sync call नहीं, scroll events पर भीड़।
3. JSI: JS सीधे C++ के native objects को पकड़कर call कर सकता है (sync या async) — JSON नहीं; MMKV, VisionCamera, Skia इसी से तेज़ हैं।
4. Fabric: React का नया tree C++ shadow tree में, Yoga से layout (ज़रूरत पर sync, जैसे नापना), फिर UI thread पर views; concurrent React (Suspense, transitions) और view flattening (कम native views)।
5. TurboModules ज़रूरत पड़ने पर ही लोड (तेज़ startup) और Codegen TypeScript spec से type-safe glue बनाता है; Bridgeless में bridge पूरी तरह हटा, interop से पुरानी libraries चलती रहती हैं।

---

## 🟡 Real World Example

**Meta** — built RN (open-sourced 2015) and uses it across Facebook, Instagram, Messenger desktop and Quest apps. The New Architecture was rolled out inside Meta's apps first (e.g., Facebook Marketplace) before becoming the open-source default.

**Shopify** — committed to RN for all its mobile apps (2020) and later migrated its large apps to the New Architecture, sharing learnings about interop and performance.

**Microsoft** — uses RN (and React Native for Windows/macOS) in parts of Office, Outlook, Teams and Xbox apps.

**Discord, Coinbase** — Coinbase rewrote its app in RN (2021). Discord uses RN for its mobile apps and invested heavily in RN performance (Hermes, list rendering).

## 🟡 Real Example Hindi में
Meta ने 2015 में RN open-source किया और Facebook, Instagram, Messenger, Quest ऐप्स में इस्तेमाल करता है — नया Architecture पहले Meta के अपने ऐप्स (जैसे Marketplace) में आया, फिर सबके लिए default बना।
Shopify ने 2020 में सारे mobile ऐप RN में बनाने का फ़ैसला किया और बाद में बड़े ऐप्स को नए Architecture पर ले गया; Microsoft Office/Teams के हिस्सों में, Coinbase (2021 में पूरा rewrite) और Discord भी RN पर।

---

## 🟠 My Stack Example

### Enable / verify New Architecture (Expo)
```json
// app.json — New Architecture is default in recent Expo SDKs; shown for clarity
{ "expo": { "newArchEnabled": true, "jsEngine": "hermes", "plugins": ["expo-router"] } }
```
```ts
// Check at runtime (dev)
console.log('Fabric:', !!(global as any).nativeFabricUIManager, 'Hermes:', !!(global as any).HermesInternal);
```

### Writing a native module with Expo Modules API (Kotlin/Swift, JSI under the hood)
```swift
// ios/BatteryModule.swift
import ExpoModulesCore
public class BatteryModule: Module {
  public func definition() -> ModuleDefinition {
    Name("Battery")
    Function("getLevel") { () -> Float in                    // synchronous JSI call
      UIDevice.current.isBatteryMonitoringEnabled = true
      return UIDevice.current.batteryLevel
    }
    AsyncFunction("isLowPowerMode") { () -> Bool in ProcessInfo.processInfo.isLowPowerModeEnabled }
  }
}
```
```kotlin
// android/.../BatteryModule.kt
class BatteryModule : Module() {
  override fun definition() = ModuleDefinition {
    Name("Battery")
    Function("getLevel") {
      val bm = appContext.reactContext!!.getSystemService(Context.BATTERY_SERVICE) as BatteryManager
      bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY) / 100f
    }
    AsyncFunction("isLowPowerMode") { (appContext.reactContext!!.getSystemService(Context.POWER_SERVICE) as PowerManager).isPowerSaveMode }
  }
}
```
```ts
// JS usage
import { requireNativeModule } from 'expo-modules-core';
const Battery = requireNativeModule('Battery');
const level = Battery.getLevel();                 // sync — no bridge round trip
if (level < 0.15 || (await Battery.isLowPowerMode())) reduceLocationFrequency();   // battery-aware (M20)
```

### TurboModule spec (bare RN with Codegen)
```ts
// specs/NativeDeviceInfo.ts
import type { TurboModule } from 'react-native';
import { TurboModuleRegistry } from 'react-native';
export interface Spec extends TurboModule {
  getDeviceId(): string;                          // sync
  getFreeDiskBytes(): Promise<number>;            // async
}
export default TurboModuleRegistry.getEnforcing<Spec>('NativeDeviceInfo');
// Codegen generates the native interfaces; module loads lazily on first import
```

### Keep work off the JS thread: UI-thread animation with Reanimated
```tsx
import Animated, { useSharedValue, useAnimatedStyle, withSpring } from 'react-native-reanimated';
function CartBadge({ count }: { count: number }) {
  const scale = useSharedValue(1);
  useEffect(() => { scale.value = withSpring(1.3, {}, () => { scale.value = withSpring(1); }); }, [count]);
  const style = useAnimatedStyle(() => ({ transform: [{ scale: scale.value }] }));  // runs on UI thread
  return <Animated.Text style={style}>{count}</Animated.Text>;
}
```

### Synchronous measurement with Fabric (no flicker)
```tsx
// useLayoutEffect + measure works synchronously in the New Architecture → position tooltip before paint
useLayoutEffect(() => { anchorRef.current?.measureInWindow((x, y, w, h) => setTooltipPos({ x, y: y + h })); }, []);
```

---

## ⚫ Interview Questions + Answers

**Q1: How does React Native render native UI?**
A1: React runs in a JS engine (Hermes) and produces a tree of host components (View, Text, Image). In the New Architecture, Fabric commits that tree to an immutable C++ shadow tree, Yoga computes flexbox layout, and the renderer diffs it against the previous tree to produce mount operations that create or update real platform views on the UI thread. Native modules (TurboModules) expose platform APIs. The result is genuine native UI driven by React state, not a WebView.

**Q2: What was wrong with the old bridge?**
A2: All communication between JS and native went through an asynchronous, batched message queue with JSON serialization. That added copying and serialization overhead, especially for high-frequency events like scroll, gestures and animation and for large payloads. It made synchronous calls and measurements impossible (layout flicker), forced eager initialization of all native modules at startup, offered no type safety across the boundary, and couldn't support concurrent React rendering.

**Q3: Explain JSI, Fabric and TurboModules.**
A3: JSI is a C++ interface that lets the JS runtime hold references to native (C++) host objects and invoke their methods directly, synchronously or asynchronously, without serialization, and it's engine-agnostic. Fabric is the new renderer built on JSI, with a C++ shadow tree shared across threads, synchronous layout when needed, view flattening and support for React 18+ concurrent features. TurboModules are native modules accessed via JSI, lazily loaded on first use and type-safe through Codegen-generated interfaces from TypeScript specs. Together with bridgeless mode they replace the bridge.

**Q4: Why does a busy JS thread cause jank, and how do you avoid it?**
A4: In React Native, your component logic, state updates, JS-driven animations and event handlers run on the JS thread. If it's blocked by heavy computation, large JSON parsing, expensive renders or synchronous storage, taps and JS-based animations wait, even though the UI thread could draw. Avoid it by running animations on the UI thread (Reanimated worklets, the native driver), keeping renders cheap (memoization, FlashList), deferring non-urgent work, moving heavy work to native modules or background threads, paginating data, and using fast JSI-based storage like MMKV.

**Q5: When would you write a native module?**
A5: When you need platform capabilities or performance that JS libraries don't provide: hardware or SDK access (custom Bluetooth devices, payment SDKs, proprietary maps or AR SDKs), heavy computation better done in native or C++ (image processing, encryption), synchronous low-latency access (key-value storage, sensors), or deep OS integration (widgets, background services). Prefer existing community or Expo modules first, then use the Expo Modules API or TurboModules with Codegen for type-safe, lazy, JSI-based modules.

---

## 🔷 Trade-offs
✅ RN: one codebase, native UI, fast iteration, OTA, React skills — ❌ native expertise still needed for edge cases; library compatibility during upgrades.
✅ New Architecture: faster, sync calls, concurrent React, lazy modules — ❌ migration effort, some old libraries need updates (interop helps).
✅ JSI direct calls: speed — ❌ sync calls on the JS thread can block it if the native work is slow (keep sync calls tiny).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bridge | Old async JSON JS↔native channel | पुराना JSON वाला पुल |
| JSI | Direct JS↔C++ interface | JS और native का सीधा रास्ता |
| Fabric | New RN renderer | नया renderer |
| TurboModules | Lazy, typed native modules | ज़रूरत पर लोड native modules |
| Codegen | Generates native glue from TS | TS से glue code बनाना |
| Shadow tree | Layout tree before mounting | layout वाला पेड़ |
| Yoga | Flexbox layout engine | flexbox layout engine |
| JS thread / UI thread | Logic thread / drawing thread | logic धागा / drawing धागा |
| Bridgeless | No bridge at all | बिना पुल के |
| Hermes | RN-optimized JS engine | RN का JS engine |

---

## ⚡ 3-Line Summary
**English:**
1. RN runs React in Hermes and renders real native views; layout via Yoga; native modules expose platform APIs.
2. The old Bridge used async JSON messages (overhead, no sync, eager modules); the New Architecture uses JSI direct calls, Fabric renderer (C++ shadow tree, concurrent React) and lazy, typed TurboModules via Codegen.
3. Keep the JS thread free: UI-thread animations (Reanimated), cheap renders, fast JSI storage, native modules for heavy work.

**Hindi:**
1. RN में React Hermes पर चलता है और असली native views बनते हैं; layout Yoga से; native modules से फ़ोन के APIs।
2. पुराना Bridge = async JSON (धीमा, sync नहीं); नया = JSI सीधी calls, Fabric renderer, ज़रूरत पर लोड TurboModules।
3. JS thread ख़ाली रखो: Reanimated से animations, हल्के renders, MMKV, भारी काम native में।

---

## ➡️ Next Topic Suggestion
**M03. Hermes + App Startup Time** — The first thing users feel is how fast the app opens. Next: how Hermes works (bytecode, GC), the phases of cold start, and techniques to make React Native apps open in under 2 seconds on low-end phones.
