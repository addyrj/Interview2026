# 169. React Native Performance Monitor
# हिंदी में: React Native Performance Monitor (App की speed नापना)
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 54 (React Native 0.81) target** — check current docs — APIs change between SDKs. Dev Menu की options RN version के हिसाब से थोड़ी बदलती हैं।

---

## 🔵 Simple Definition (English)
**Performance Monitor** is a built-in dev tool that shows live numbers while your app runs: **UI thread FPS**, **JS thread FPS**, RAM and view count. It helps you find *which thread* is slow so you fix the right problem. Other tools: React DevTools Profiler, Hermes sampling profiler, `<Profiler>`.

## 🔵 सरल परिभाषा (Hindi)
**Performance Monitor** एक built-in dev tool है जो app चलते समय live numbers दिखाता है: **UI thread FPS**, **JS thread FPS**, RAM और views की संख्या। इससे पता चलता है कि **कौन सा thread slow** है, ताकि आप सही जगह fix करें। दूसरे tools: React DevTools Profiler, Hermes profiler, `<Profiler>`।

---

## 🔴 Problem it Solves
```
BEFORE (without measuring):
❌ "App slow lag raha hai" — but WHERE? JS? UI? Network?
❌ Developers guess and add useMemo everywhere (premature optimization)
❌ Fix works on iPhone 15 but app janks on a Rs 8,000 Android phone
❌ Regressions reach production because nobody measured
```

## 🔴 यह क्यों बना? (Hindi)
```
Measure किए बिना:
❌ "App lag कर रहा है" — पर कहाँ? JS में? UI में? Network में?
❌ Developer अंदाज़े से हर जगह useMemo लगा देते हैं
❌ Fix महंगे iPhone पर चलता है, सस्ते Android पर अटकता है
Rule: पहले MEASURE करो, फिर OPTIMIZE करो!
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Open Dev Menu: shake device / Cmd+D (iOS sim) / Cmd+M or Ctrl+M (Android emu)
Step 2 → Tap "Perf Monitor" (shows overlay with UI fps + JS fps + RAM)
Step 3 → Use the slow screen (scroll list, open modal, navigate)
Step 4 → JS fps drops (<60) → JS thread busy → use React Profiler / Hermes profiler
Step 5 → UI fps drops → too many views / heavy native work → flatten views, optimize images
Step 6 → Fix ONE thing, measure again, compare numbers
Step 7 → Test on release build + low-end device (dev mode is always slower)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Dev Menu खोलो: device shake / Cmd+D (iOS) / Cmd+M (Android)
Step 2 → "Perf Monitor" पर tap करो (UI fps, JS fps, RAM दिखेगा)
Step 3 → Slow screen चलाओ (list scroll, modal, navigation)
Step 4 → JS fps गिरा → JS thread busy है → React Profiler / Hermes profiler use करो
Step 5 → UI fps गिरा → views ज़्यादा / भारी native काम → views कम करो, images optimize करो
Step 6 → एक चीज़ fix करो, फिर दोबारा measure करो
Step 7 → हमेशा release build + low-end phone पर test करो
```

---

## 🟡 Real World Example
**Swiggy / Zomato restaurant listing**: hundreds of cards with images. Team opens Perf Monitor on a budget Redmi phone, scrolls the list, and sees UI fps fall to 35. The culprit is big uncompressed images, not JS. They resize images and fps returns to ~58. **Paytm** home screen: JS fps drops on launch because of heavy JSON parsing — fixed by deferring work with `InteractionManager`.

## 🟡 Real Example Hindi mein
**Swiggy / Zomato listing**: सैकड़ों cards और images। Team सस्ते Redmi phone पर Perf Monitor खोलती है, scroll करती है, UI fps 35 तक गिर जाता है। कारण JS नहीं, बड़ी images थीं। Images छोटी करने पर fps ~58 हो गया। **Paytm** home screen में launch पर JSON parsing से JS fps गिरता था — `InteractionManager` से काम बाद में किया गया।

---

## 💻 Code Example — Basic
```jsx
// Basic: measure how long a React subtree takes to render using <Profiler>
// Works on both Android + iOS (pure JS, Expo + CLI)
import React, { Profiler, useState } from 'react'; // React + Profiler + state hook
import { View, Text, Button, StyleSheet } from 'react-native'; // RN UI parts

// onRender is called by React after every commit of the wrapped tree
function onRenderCallback(
  id,             // the "id" prop of the Profiler
  phase,          // "mount" or "update" (or "nested-update")
  actualDuration  // ms spent rendering this commit
) {
  // log so we can read it in Metro terminal
  console.log(`[Profiler] ${id} ${phase} took ${actualDuration.toFixed(2)}ms`);
}

// A deliberately heavy list to see the effect
function HeavyList({ count }) {
  // build an array of `count` items (cheap here, heavy when count is big)
  const items = Array.from({ length: count }, (_, i) => i);
  return (
    <View>
      {items.map((i) => (
        // every item is a Text node
        <Text key={i} style={styles.row}>Item {i}</Text>
      ))}
    </View>
  );
}

export default function App() {
  // state that decides how many rows we render
  const [count, setCount] = useState(50);
  return (
    <View style={styles.container}>
      {/* Wrap only the part you want to measure */}
      <Profiler id="HeavyList" onRender={onRenderCallback}>
        <HeavyList count={count} />
      </Profiler>
      {/* Press to make the list bigger and compare timings */}
      <Button title="Add 200 rows" onPress={() => setCount((c) => c + 200)} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, paddingTop: 60 }, // full screen with top gap
  row: { fontSize: 14, paddingVertical: 2 }, // small text rows
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: tiny in-app JS-thread FPS meter + defer heavy work with InteractionManager
// JS FPS = how often requestAnimationFrame fires per second (pure JS, both platforms)
import React, { useEffect, useRef, useState } from 'react'; // hooks
import { View, Text, InteractionManager, Platform, StyleSheet } from 'react-native';

// Custom hook: returns approximate JS-thread FPS, updated every second
export function useJsFps() {
  const [fps, setFps] = useState(60);        // value shown on screen
  const frames = useRef(0);                  // frames counted in the current second
  const last = useRef(Date.now());           // when current second started
  const raf = useRef(0);                     // id to cancel the loop

  useEffect(() => {
    const loop = () => {
      frames.current += 1;                   // one more frame happened
      const now = Date.now();                // current time
      if (now - last.current >= 1000) {      // one second passed?
        setFps(frames.current);              // publish the count
        frames.current = 0;                  // reset counter
        last.current = now;                  // start new second
      }
      raf.current = requestAnimationFrame(loop); // schedule next frame
    };
    raf.current = requestAnimationFrame(loop);   // start loop
    return () => cancelAnimationFrame(raf.current); // cleanup on unmount
  }, []);

  return fps; // consumer reads number
}

// Overlay component: only render in development builds
export function FpsBadge() {
  const fps = useJsFps(); // get live fps
  if (!__DEV__) return null; // never ship the badge to production
  return (
    <View style={[styles.badge, fps < 45 && styles.bad]}>
      <Text style={styles.txt}>JS {fps} fps ({Platform.OS})</Text>
    </View>
  );
}

// Example screen: do expensive parsing AFTER animations/transitions finish
export function useDeferredParse(rawJson, onDone) {
  useEffect(() => {
    // runAfterInteractions waits until navigation animations complete
    const task = InteractionManager.runAfterInteractions(() => {
      try {
        const data = JSON.parse(rawJson); // heavy work now won't block animation
        onDone(data);                     // hand the result back
      } catch (e) {
        console.warn('Parse failed', e);  // error handling
      }
    });
    return () => task.cancel();           // cancel if screen closes early
  }, [rawJson, onDone]);
}

const styles = StyleSheet.create({
  badge: { position: 'absolute', top: 50, right: 10, padding: 6, borderRadius: 6, backgroundColor: '#16a34a' }, // green = healthy
  bad: { backgroundColor: '#dc2626' },   // red when fps is low
  txt: { color: '#fff', fontSize: 12, fontWeight: '700' }, // white text
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Open Dev Menu | Cmd+M / Ctrl+M or shake, `adb shell input keyevent 82` | Cmd+D (Simulator) or shake |
| Native profiler | Android Studio Profiler, Perfetto/systrace | Xcode Instruments (Time Profiler, Core Animation) |
| Typical bottleneck | Low-end CPU, overdraw, big images | Usually fine; main issue is heavy JS or shadows |
| Frame budget | 16.6 ms (60Hz) / 8.3 ms (120Hz phones) | 16.6 ms / 8.3 ms (ProMotion) |
| Memory tool | Android Studio Memory Profiler | Instruments Allocations/Leaks |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Expo Go / dev client: shake device or press "m" in the terminal to open Dev Menu
npx expo start
# Press "m" in terminal -> toggles menu, then pick "Perf Monitor"
# For real numbers use a release-like build:
npx expo run:android --variant release   # needs prebuild (native folders generated)
```
CLI way:
```bash
# Bare React Native
npx react-native run-android --mode release   # release build (Hermes + no dev warnings)
npx react-native run-ios --mode Release       # macOS only
# Then profile with Android Studio / Xcode Instruments directly
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Judging performance in **dev mode**
✅ Correct: Dev mode has extra checks and unminified code. Always confirm with a **release build** on a real low-end device.

❌ Mistake 2: Optimizing without a measurement
✅ Correct: Record a baseline (fps / render ms), change one thing, measure again.

❌ Mistake 3: Leaving `console.log` in loops
✅ Correct: Logs are slow in dev and can hurt release too. Remove them or strip with `babel-plugin-transform-remove-console`.

---

## 🧠 Tricky Interview Question
**Q: Perf Monitor shows JS fps = 60 but UI fps = 25 while scrolling. Will adding `useMemo` help?**

**Answer:** No. The **JS thread is healthy**; the **UI (main) thread** is slow. `useMemo` only reduces JS work. Look for native cost: too many nested views, large un-resized images, heavy shadows/blur, `overflow: hidden` with `borderRadius` on many items, or complex layouts. Fix with smaller images (`expo-image`/FastImage), flatter hierarchies, `removeClippedSubviews`, and FlatList tuning.

---

## ⚫ Interview Questions + Answers

**Q1: What two FPS numbers does Perf Monitor show?**
A1: UI FPS (main/native thread drawing frames) and JS FPS (thread running your React code). Both should stay near 60.

**Q2: How do you profile React renders?**
A2: Use React DevTools Profiler (flamegraph, "why did this render") or the `<Profiler>` component with `onRender`.

**Q3: How do you find slow JavaScript functions?**
A3: Record a Hermes sampling profile (Dev Menu / Chrome DevTools via Hermes inspector) and look at the heaviest call stacks.

**Q4: What is InteractionManager for?**
A4: It lets you run work after animations/gestures finish, so heavy tasks do not drop frames during transitions.

**Q5: Why is a release build mandatory for benchmarking?**
A5: Dev builds run un-minified JS with warnings, remote debugging overhead and no optimizations; numbers are not representative.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Scroll or navigation feels janky
- Before/after an optimization to prove it worked
- Testing on low-end Android devices

❌ Avoid when:
- Benchmarking final numbers in dev mode
- You only have emulator numbers (CPU differs from real phones)
- Optimizing code that is not on a hot path

---

## 📊 Visual Diagram
```
 ┌──────────── PHONE ─────────────┐
 │  JS THREAD (Hermes)            │  <- your React code, state, logic
 │   60 fps? ── no ──► React Profiler / Hermes profiler
 │        │                       │
 │        ▼ (commits UI changes)  │
 │  UI / MAIN THREAD              │  <- draws views, handles touch
 │   60 fps? ── no ──► Xcode Instruments / Android Profiler
 └────────────────────────────────┘
 Frame budget: 16.6 ms  (miss it = visible jank)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| FPS | Frames drawn per second | प्रति सेकंड frames |
| JS thread | Thread running React code | React code चलाने वाला thread |
| UI thread | Thread drawing native views | Native views draw करने वाला thread |
| Profiler | Measures render cost | Render का समय नापने वाला tool |
| Jank | Visible stutter | अटकना / हकलाहट |
| Release build | Optimized production build | Production के लिए optimized build |

---

## ⚡ 3-Line Summary
**English:**
1. Perf Monitor shows UI FPS and JS FPS, so you know which thread is slow.
2. Use React Profiler for renders, Hermes profiler for JS, Instruments/Android Studio for native.
3. Always measure on a release build and a low-end device.

**Hindi:**
1. Perf Monitor UI FPS और JS FPS दिखाता है, इसलिए पता चलता है कौन सा thread slow है।
2. Renders के लिए React Profiler, JS के लिए Hermes profiler, native के लिए Instruments/Android Studio।
3. हमेशा release build और low-end phone पर measure करो।

---

## ➡️ Next Topic
**170. Avoiding Re-renders in RN** — अब जब slow JS thread पता चल गया, तो अनावश्यक re-renders कैसे रोकें।
