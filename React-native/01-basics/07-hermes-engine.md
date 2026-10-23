# 07. Hermes JavaScript Engine
# हिंदी में: Hermes JS Engine क्या है?
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
**Hermes** is a JavaScript engine built by Meta specifically for React Native apps. Unlike V8 (Chrome's engine) or JSC (JavaScriptCore — Safari's engine), Hermes is optimized for **mobile startup performance**: it pre-compiles JavaScript to bytecode at build time, so the app doesn't need to parse and compile JS when it starts — it just runs the bytecode directly.

## 🔵 सरल परिभाषा (Hindi)
**Hermes** Meta द्वारा बनाया गया JS engine है, specifically React Native apps के लिए। V8 (Chrome) या JSC (Safari) के unlike, Hermes **mobile startup performance** के लिए optimized है: यह build time पर JS को bytecode में pre-compile कर देता है, तो app start होने पर JS parse/compile करने की जरूरत नहीं — directly bytecode run होता है।

---

## 🔴 Problem it Solves
```
MOBILE APP STARTUP — The Problem:
User taps app icon → App opens
Between tap and first screen visible = TIME TO INTERACTIVE (TTI)

WITHOUT HERMES (using JSC):
Step 1 → Download/read JS bundle from disk (~5-10ms)
Step 2 → Parse JS (convert text to AST) (~50-200ms!) ← SLOW
Step 3 → Compile AST to bytecode (~30-100ms)        ← SLOW
Step 4 → Execute bytecode                            ← Fast
         Total: 100-400ms wasted on JS compilation!

WITH HERMES:
Step 1 → Read PRE-COMPILED bytecode from disk        ← Fast
Step 2 → Execute bytecode directly                   ← Fast
         No parse, no compile! 50-70% faster startup!

OTHER BENEFITS:
✅ Smaller memory footprint (mobile has limited RAM)
✅ Better garbage collection for mobile patterns
✅ Bytecode reduces bundle size on disk
✅ Supports debugging via Chrome DevTools (same protocol)
```

## 🔴 यह क्यों बना? (Hindi)
```
Mobile startup time का problem:
JSC: JS bundle read → parse → compile → execute (slow!)
Hermes: Build time पर pre-compile → runtime पर directly execute
Result: 50-70% faster startup, कम memory use
```

---

## 🟢 How it Works — Step by Step

```
WITHOUT HERMES (JSC Flow):
─────────────────────────────────────────
Build Time:
  your code → Babel transform → JS bundle (index.android.bundle)
                                ↑ just text JS

Runtime (app startup):
  Read JS bundle → Parse (AST) → Compile (bytecode) → Execute
  [All happens every time app starts — SLOW!]

WITH HERMES (Hermes Flow):
─────────────────────────────────────────
Build Time:
  your code → Babel transform → JS bundle → Hermes compiler → .hbc bytecode
                                            [happens ONCE, at build!]

Runtime (app startup):
  Read .hbc bytecode → Execute DIRECTLY (no parse, no compile)
  [JIT compilation still happens for hot code paths]
  [Much faster!]

HERMES ENGINE FEATURES:
  ├── AOT (Ahead of Time) bytecode compilation at build
  ├── Lazy property initialization (objects created faster)
  ├── Compact GC (Garbage Collector optimized for mobile)
  ├── Full ES2015+ support (async/await, generators, etc.)
  ├── Source maps: bytecode → original code for debugging
  └── Hermes Inspector: Chrome DevTools protocol for debugging
```

## 🟢 कैसे काम करता है? (Hindi)
```
Build time: JS code → Hermes compiler → Bytecode (.hbc file)
App startup: Bytecode directly execute → No parse, no compile
Fast start + कम memory!
```

---

## 🟡 Real World Example
**Swiggy app startup:** Before Hermes (using JSC): app took ~4-5 seconds to show first screen on mid-range Android phones (Redmi, Realme). With Hermes: same phone, same code — startup dropped to ~2-3 seconds. The JS parsing alone was eating 1-2 seconds on slow CPUs found in budget Android phones. Hermes is especially impactful on **budget Android phones** which have slow CPUs — exactly the dominant market in India.

## 🟡 Real Example Hindi मे
**Swiggy app startup:** Hermes से पहले: Redmi/Realme budget phones पर 4-5 second startup। Hermes के बाद: 2-3 second। JS parsing ही 1-2 second खाती थी slow CPUs पर। India में budget Android phones dominant हैं — इसीलिए Hermes especially important है।

---

## 💻 Code Example — Basic

```jsx
// Checking if Hermes is running
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

function HermesCheck() {
  // global.HermesInternal exists only when running on Hermes
  const isHermes = () => !!global.HermesInternal;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>
        JS Engine: {isHermes() ? '🔥 Hermes' : '⚡ JSC (JavaScriptCore)'}
      </Text>
      <Text style={styles.subtitle}>
        {isHermes()
          ? 'Bytecode execution — fast startup!'
          : 'JIT compilation — standard mode'}
      </Text>
    </View>
  );
}

// In package.json, check if hermes is enabled:
// For Expo: app.json → "jsEngine": "hermes"
// For CLI: android/app/build.gradle → hermesEnabled = true

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 },
  title: { fontSize: 20, fontWeight: '700', marginBottom: 8 },
  subtitle: { fontSize: 14, color: '#666', textAlign: 'center' },
});
```

## 💻 Code Example — Advanced

```jsx
// Hermes-specific: Performance monitoring
// Hermes supports sampling profiler — useful for finding JS performance issues

import { View, Text, Button, StyleSheet } from 'react-native';

// Hermes supports Performance API (React Native 0.71+)
function PerformanceDemo() {
  const measureOperation = () => {
    // Performance.now() works with Hermes
    const start = performance.now();

    // Simulate some computation
    let result = 0;
    for (let i = 0; i < 1_000_000; i++) {
      result += Math.sqrt(i);
    }

    const end = performance.now();
    console.log(`Operation took: ${(end - start).toFixed(2)}ms`);
    console.log(`Result: ${result.toFixed(0)}`);
    // Hermes is much faster here than JSC on the same device
  };

  // Hermes Sampling Profiler (for deep debugging):
  // import { HermesInternal } from 'hermes-profile-transformer';
  // global.HermesInternal?.enableSamplingProfiler?.();
  // ... do work ...
  // global.HermesInternal?.disableSamplingProfiler?.();
  // Generates a profile viewable in Chrome DevTools

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Hermes Performance Demo</Text>
      <Button title="Run 1M sqrt operations" onPress={measureOperation} />
      <Text style={styles.note}>Check Metro/console for timing</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 20, gap: 12 },
  header: { fontSize: 18, fontWeight: '700' },
  note: { fontSize: 12, color: '#888', marginTop: 8 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Default engine | Hermes (RN 0.64+) | Hermes (RN 0.64+, was JSC before) |
| Before Hermes | JavaScriptCore (JSC) | JavaScriptCore (JSC) |
| Impact | Huge — budget Android CPUs are slow | Moderate — Apple Silicon CPUs are fast |
| JSC support | Still available if disabled | Still available if disabled |
| Hermes bytecode | Bundled in APK/AAB | Bundled in IPA |

---

## 🟠 Expo vs CLI Difference

Expo way:
```json
// app.json — Hermes is default in Expo SDK 47+
{
  "expo": {
    "jsEngine": "hermes"   // default, can change to "jsc" if needed
  }
}
// Expo Go uses Hermes automatically
// EAS Build uses Hermes by default
```

CLI way:
```
android/app/build.gradle:
  project.ext.react = [
    enableHermes: true  // enables Hermes for Android
  ]

  // Or in newer RN versions:
  hermesEnabled = true  // in gradle.properties

ios/Podfile:
  :hermes_enabled => true  // add this line

Then: cd ios && pod install
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Assuming Hermes = automatic app speed (it only helps startup + memory)
```
Hermes helps:
✅ App startup time (Time to Interactive)
✅ Memory usage
✅ Battery life (less CPU work)

Hermes does NOT fix:
❌ Slow API calls
❌ Bad component re-renders
❌ Unoptimized images
❌ Heavy JS operations during runtime
❌ Poor FlatList usage (missing keyExtractor, getItemLayout)
```

❌ **Mistake 2:** Forgetting Hermes debugger setup (Chrome DevTools works differently)
```jsx
// WRONG: Expecting same debugging workflow as web React
// Hermes doesn't use the same remote debugger as JSC

// CORRECT debugging with Hermes:
// 1. Shake device → "Open Debugger"
// 2. Or: adb reverse tcp:8081 tcp:8081 (Android)
// 3. Chrome DevTools via Hermes Inspector:
//    chrome://inspect → Configure → add localhost:8081
// 4. React DevTools: npx react-devtools (works with Hermes)
```

❌ **Mistake 3:** Using JSC-only features expecting them to work with Hermes
```javascript
// ⚠️ Some older JS syntax/features had JSC-only behavior
// Always test on Hermes explicitly!

// Hermes supports ES2015+ including:
// ✅ async/await, generators, destructuring, spread, optional chaining
// ✅ Proxy, WeakRef (newer Hermes versions)
// ⚠️ Some very experimental features may differ between engines
```

---

## 🧠 Tricky Interview Question

**Q: You're debugging a crash that only happens in production (Hermes bytecode) but never in development (Metro bundle, Hermes debug mode). What could be the cause?**

**Answer:** Several possibilities: (1) **Source maps mismatch** — production bytecode source maps aren't set up, so the crash stack trace points to wrong lines. Fix: ensure source maps are uploaded to your crash tracking service (Sentry, Bugsnag). (2) **Debug/Release build difference** — in debug, `__DEV__` is `true`, some code paths are skipped; in release, they run. Check conditional code using `__DEV__`. (3) **ProGuard/R8 on Android** — Java/Kotlin code gets obfuscated, breaking native module calls. Fix: add ProGuard keep rules. (4) **Bundle optimization** — Metro production mode tree-shakes more aggressively; unused export assumptions may break dynamic imports. Always test production builds before release with `expo build` or `npx react-native build-android --mode release`.

---

## ⚫ Interview Questions + Answers

**Q1: What is Hermes and why was it created?**
A1: Hermes is a JavaScript engine built by Meta specifically for React Native. Created to solve mobile startup performance — unlike V8/JSC which compile JS at runtime (JIT), Hermes pre-compiles JavaScript to bytecode at build time (AOT). When the app starts, bytecode is executed directly with no parse/compile step. Result: 50-70% faster Time to Interactive, smaller memory footprint, better battery usage on mobile devices.

**Q2: What is the difference between Hermes and V8?**
A2: V8 (Google, used in Chrome/Node.js) is optimized for peak runtime performance — heavy JIT compilation, large memory caches, aggressive optimizations. Hermes is optimized for mobile startup and memory — AOT compilation to bytecode, compact GC, small memory footprint. V8 would be faster for long-running CPU-intensive workloads; Hermes is better for the mobile use case of "start fast, stay responsive, minimal memory." React Native uses Hermes; React for web uses V8 (Chrome) or SpiderMonkey (Firefox).

**Q3: How does Hermes handle debugging?**
A3: Hermes implements the Chrome DevTools Protocol (CDP) via Hermes Inspector. You can debug with: (1) React DevTools (`npx react-devtools`) — component tree inspection, props, state. (2) Chrome DevTools — set breakpoints, inspect variables, call stack. (3) Flipper (Meta's mobile debugging tool) — Hermes plugin for React Native. Connect via: shake device → "Open Debugger" or `adb forward tcp:8081 localabstract:webview_devtools_remote_<pid>` on Android.

**Q4: Does Hermes support all modern JavaScript?**
A4: Yes — Hermes supports ES2015+ (ES6+) including async/await, generators, arrow functions, destructuring, spread, classes, modules, optional chaining, nullish coalescing, and more. Hermes is regularly updated. Rare edge case: very new JS proposals (Stage 1-2) may not be in Hermes yet, but Babel transforms handle those in the React Native pipeline anyway, so in practice all common JS works.

**Q5: What is the difference between TTI and FPS in React Native performance?**
A5: **TTI (Time to Interactive)** = time from app launch to first interactive screen — Hermes improves this by 50-70% via bytecode. **FPS (Frames Per Second)** = animation and scroll smoothness — target is 60fps (16ms/frame). FPS is affected by JS Thread work during animations (use `useNativeDriver: true` or Reanimated v3 to move to UI thread) and by React re-renders (use `React.memo`, `useCallback`). Hermes helps TTI; FPS requires other optimizations.

---

## 🔷 When to Use + When Not to Use
✅ **Use Hermes (always):**
- All React Native projects (2024+) — it's the default
- Especially important for budget Android devices (India market)
- Production apps where startup time matters
- Apps targeting low-RAM devices (2-3GB RAM)

❌ **Disable Hermes only when:**
- Specific library is incompatible with Hermes (very rare now)
- Debugging a Hermes-specific engine bug
- Testing performance comparison between engines

---

## 📊 Visual Diagram

```
STARTUP TIME COMPARISON:
──────────────────────────────────────────────────────
  App tap → Visible screen

  JSC (Old):   [Read JS][   Parse JS   ][ Compile ][Run] = ~400ms
               ████████ ██████████████ █████████  ████

  Hermes:      [Read bytecode][         Run         ] = ~150ms
               ████████████   █████████████████████

  Hermes is 2-3x faster on startup!

HOW HERMES WORKS:
──────────────────────────────────────────────────────
  BUILD TIME (happens once, on your machine or CI):
  ┌──────────────────────────────────────────────────┐
  │  JS Code → Babel → JS Bundle → Hermes Compiler  │
  │                                        ↓        │
  │                              Bytecode (.hbc)    │
  │                              Bundled into APK   │
  └──────────────────────────────────────────────────┘

  RUNTIME (happens on user's device, every launch):
  ┌──────────────────────────────────────────────────┐
  │  Read bytecode from APK → Execute directly!     │
  │  No parsing. No compilation. Just run.          │
  └──────────────────────────────────────────────────┘

  MEMORY (Hermes vs JSC on same device):
  ┌──────────────────────────────────────────────────┐
  │  JSC:    ████████████████████ 120MB RAM         │
  │  Hermes: ██████████████ 85MB RAM  (-30%)        │
  └──────────────────────────────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hermes | Meta's JS engine for React Native | React Native के लिए Meta का JS engine |
| JSC | JavaScriptCore — Apple's/WebKit's engine | Apple का JS engine (Safari) |
| V8 | Google's JS engine (Chrome, Node.js) | Google का JS engine |
| AOT | Ahead of Time compilation (at build) | Build time compilation |
| JIT | Just In Time compilation (at runtime) | Runtime compilation |
| Bytecode | Pre-compiled intermediate code | Pre-compiled intermediate code |
| TTI | Time To Interactive — startup speed metric | App launch से first interaction तक समय |
| HBC | Hermes Bytecode (file format) | Hermes का bytecode format |

---

## ⚡ 3-Line Summary
**English:**
1. Hermes is Meta's JavaScript engine for React Native — compiles JS to bytecode at build time (AOT), so apps start 50-70% faster than with JSC.
2. It's the default engine since React Native 0.64 (Android) and 0.64 iOS, and is especially impactful on budget Android phones.
3. Hermes improves startup time and memory; it doesn't fix runtime performance issues like bad re-renders or heavy JS work.

**Hindi:**
1. Hermes Meta का React Native के लिए JS engine है — build time पर JS को bytecode में compile करता है (AOT), apps 50-70% faster start होते हैं।
2. React Native 0.64 से default engine है, budget Android phones पर especially impactful है।
3. Hermes startup time और memory improve करता है; bad re-renders या heavy JS work fix नहीं करता।

---

## ➡️ Next Topic
**08. Expo vs React Native CLI** — दोनों approaches के tradeoffs, कब क्या choose करें।
