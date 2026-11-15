# 131. useSharedValue
# हिंदी में: useSharedValue — Reanimated की साझा value
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76, react-native-reanimated 3.x (check current docs — APIs change between SDKs). Expo में `npx expo install react-native-reanimated`।

---

## 🔵 Simple Definition (English)
`useSharedValue(initial)` creates a value that lives on **both** the JS thread and the UI thread. You read and write it through `.value`. Changing it does **not** re-render the component; animated styles that use it update directly on the UI thread.

## 🔵 सरल परिभाषा (Hindi)
`useSharedValue(initial)` ऐसी value बनाता है जो **JS thread और UI thread दोनों** पर उपलब्ध है। इसे `.value` से पढ़ते/लिखते हैं। इसे बदलने पर component **re-render नहीं** होता; इसे use करने वाली animated styles सीधे UI thread पर update होती हैं।

---

## 🔴 Problem it Solves
```
useState:   change -> React re-render -> JS work -> bridge/commit -> slow for 60fps
Animated.Value: only through special Animated components, limited props
Need: a value that
  - changes 60+ times/second without re-rendering React
  - can be read inside UI-thread functions (worklets)
  - persists across renders
  -> useSharedValue
```

## 🔴 यह क्यों बना? (Hindi)
```
useState:   बदलाव -> React re-render -> JS काम -> commit -> 60fps के लिए धीमा
Animated.Value: सिर्फ खास Animated components, सीमित props
ज़रूरत: ऐसी value जो
  - सेकंड में 60+ बार बदले और React re-render न हो
  - UI-thread functions (worklets) के अंदर पढ़ी जा सके
  - renders के बीच बनी रहे
  -> useSharedValue
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → const x = useSharedValue(0)            // object { value: 0 }, memory shared by both threads
Step 2 → Write:  x.value = 50                    // instantly visible to UI thread
Step 3 → Read inside worklet: useAnimatedStyle(() => ({ left: x.value }))
Step 4 → Reanimated tracks which shared values the worklet reads (dependencies)
Step 5 → When x.value changes -> only that style is recomputed on UI thread
Step 6 → NO React re-render happens (that is the whole point)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → const x = useSharedValue(0)            // { value: 0 } object, दोनों threads में share
Step 2 → Write:  x.value = 50                    // UI thread को तुरंत दिखता है
Step 3 → worklet के अंदर पढ़ो: useAnimatedStyle(() => ({ left: x.value }))
Step 4 → Reanimated देखता है कि worklet कौन सी shared values पढ़ता है (dependencies)
Step 5 → x.value बदलते ही सिर्फ वही style UI thread पर दोबारा बनती है
Step 6 → React re-render नहीं होता (यही असली फायदा है)
```

---

## 🟡 Real World Example
**Paytm "Scan & Pay" torch button / PhonePe slider:** a draggable amount slider keeps `translateX` in a shared value. The thumb follows the finger at 60fps and the amount text updates without re-rendering the whole payment screen.

## 🟡 Real Example Hindi mein
**Paytm "Scan & Pay" / PhonePe slider:** draggable amount slider `translateX` को shared value में रखता है। Thumb उंगली के साथ 60fps पर चलता है और पूरी payment screen re-render किए बिना amount text बदलता है।

---

## 💻 Code Example — Basic

```jsx
import React from 'react';                                      // React
import { View, Pressable, Text, StyleSheet } from 'react-native'; // core
import Animated, { useSharedValue, useAnimatedStyle, withSpring } from 'react-native-reanimated'; // Reanimated 3

export default function SharedValueBasic() {
  const offset = useSharedValue(0);                              // creates { value: 0 }, lives across renders

  const animatedStyle = useAnimatedStyle(() => ({                // worklet on UI thread
    transform: [{ translateX: offset.value }],                   // reads .value (tracked automatically)
  }));

  const moveRight = () => {                                      // JS handler
    offset.value = withSpring(offset.value + 60);                // assign an animation to .value
  };
  const reset = () => {                                          // reset instantly (no animation)
    offset.value = 0;                                            // direct assignment
  };

  return (
    <View style={styles.container}>
      <Animated.View style={[styles.box, animatedStyle]} />      {/* Animated.View, not View */}
      <Pressable style={styles.btn} onPress={moveRight}><Text style={styles.t}>Move</Text></Pressable>
      <Pressable style={styles.btn} onPress={reset}><Text style={styles.t}>Reset</Text></Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  box: { width: 80, height: 80, backgroundColor: '#5f259f', borderRadius: 12 }, // Paytm-like purple
  btn: { marginTop: 16, padding: 12, backgroundColor: '#222', borderRadius: 8 },
  t: { color: '#fff' },
});
```

## 💻 Code Example — Advanced

```jsx
import React, { useCallback, useState } from 'react';           // hooks
import { View, Text, Platform, StyleSheet } from 'react-native'; // core
import Animated, {
  useSharedValue, useAnimatedStyle, useDerivedValue, useAnimatedReaction,
  runOnJS, withTiming, interpolate, Extrapolation,
} from 'react-native-reanimated';                                // Reanimated 3 APIs
import { Gesture, GestureDetector, GestureHandlerRootView } from 'react-native-gesture-handler'; // gestures

const TRACK = 260;                                              // slider width
const THUMB = 36;                                               // thumb size
const MAX_AMOUNT = 10000;                                       // Rs max

export default function AmountSlider() {
  const x = useSharedValue(0);                                  // thumb position (UI thread)
  const startX = useSharedValue(0);                             // where drag started
  const [amount, setAmount] = useState(0);                      // React state ONLY for text display

  // Derived shared value: recomputed on UI thread whenever x changes
  const progress = useDerivedValue(() => x.value / (TRACK - THUMB)); // 0..1

  const updateAmount = useCallback((v) => setAmount(v), []);    // JS function to be called from UI thread

  // React to shared value changes; throttle by rounding to nearest Rs 100
  useAnimatedReaction(
    () => Math.round((progress.value * MAX_AMOUNT) / 100) * 100, // "prepare": compute on UI thread
    (current, previous) => {                                    // "react": runs when prepare result changes
      if (current !== previous) runOnJS(updateAmount)(current); // jump to JS thread only on change
    },
  );

  const pan = Gesture.Pan()                                     // drag gesture
    .onBegin(() => { startX.value = x.value; })                 // remember start
    .onUpdate((e) => {                                          // finger moving (UI thread worklet)
      const next = startX.value + e.translationX;               // new position
      x.value = Math.min(Math.max(next, 0), TRACK - THUMB);     // clamp inside track
    })
    .onEnd(() => { x.value = withTiming(Math.round(x.value)); }); // settle on whole pixel

  const thumbStyle = useAnimatedStyle(() => ({                  // thumb follows x
    transform: [{ translateX: x.value }],
  }));
  const fillStyle = useAnimatedStyle(() => ({                   // filled part of track
    width: interpolate(x.value, [0, TRACK - THUMB], [THUMB / 2, TRACK], Extrapolation.CLAMP),
  }));

  return (
    <GestureHandlerRootView style={styles.root}>                {/* required root for gestures */}
      <Text style={styles.amount}>₹{amount}</Text>
      <View style={styles.track}>
        <Animated.View style={[styles.fill, fillStyle]} />
        <GestureDetector gesture={pan}>
          <Animated.View style={[styles.thumb, thumbStyle]} />
        </GestureDetector>
      </View>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  amount: { fontSize: 32, fontWeight: '700', marginBottom: 24 },
  track: { width: TRACK, height: THUMB, borderRadius: THUMB / 2, backgroundColor: '#e6dcf5', justifyContent: 'center' },
  fill: { position: 'absolute', height: THUMB, borderRadius: THUMB / 2, backgroundColor: '#b79be0' },
  thumb: {
    position: 'absolute', width: THUMB, height: THUMB, borderRadius: THUMB / 2, backgroundColor: '#5f259f',
    ...Platform.select({ ios: { shadowOpacity: 0.3, shadowRadius: 4, shadowOffset: { width: 0, height: 2 } }, android: { elevation: 4 } }),
  },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| useSharedValue behavior | Same | Same |
| Shadow on thumb | `elevation` | `shadow*` |
| Gesture feel | Slight touch-slop delay | Immediate |
| Reduced motion setting | "Remove animations" | "Reduce Motion" (use `useReducedMotion`) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// terminal: npx expo install react-native-reanimated
// babel.config.js: Expo SDK 50+ preset adds the plugin automatically (check docs)
import { useSharedValue } from 'react-native-reanimated';
```
CLI way:
```jsx
// terminal: npm i react-native-reanimated ; cd ios && pod install
// babel.config.js -> plugins: ['react-native-reanimated/plugin']   (must be LAST)
// rebuild the app (npx react-native run-android / run-ios)
import { useSharedValue } from 'react-native-reanimated';
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Treating it like state: `const v = useSharedValue(0); <Text>{v.value}</Text>`.
✅ Correct: Shared values do not trigger re-render. Show them via `useAnimatedProps`/`useAnimatedStyle` or copy to state with `runOnJS`.

❌ Mistake 2: Mutating nested objects: `obj.value.x = 5`.
✅ Correct: Reassign whole value: `obj.value = { ...obj.value, x: 5 }`.

❌ Mistake 3: Reading `.value` on the JS thread in render body (can cause warnings/jank).
✅ Correct: Read inside worklets, gesture callbacks, or `useDerivedValue`.

❌ Mistake 4: Forgetting the Babel plugin -> "Failed to create a worklet".
✅ Correct: Add `react-native-reanimated/plugin` last in babel plugins, clear cache `npx expo start -c`.

---

## 🧠 Tricky Interview Question
```jsx
const count = useSharedValue(0);
const onPress = () => {
  count.value = count.value + 1;
  console.log(count.value);
};
```
Does the Text `<Text>{count.value}</Text>` update on press? What does console.log print?

Answer: console.log prints the new value (1, 2, ...) because the write is synchronous on the JS side. But the `<Text>` does **not** update, since no re-render is triggered and plain `Text` is not an animated component. Use `useState`, or `Animated` text with `useAnimatedProps` + `TextInput` trick.

---

## ⚫ Interview Questions + Answers
Q1: Difference between useSharedValue and useState?
A1: shared value: no re-render, UI-thread accessible, mutable via `.value`. state: re-render, JS-thread only.

Q2: Difference from useRef?
A2: useRef is JS-only and not readable by worklets on the UI thread. Shared value is.

Q3: What is a worklet?
A3: A function marked with the `'worklet'` directive (or auto-workletized in `useAnimatedStyle`, gesture callbacks) which Reanimated can run on the UI thread.

Q4: How to call a JS function (setState) from a worklet?
A4: `runOnJS(fn)(args)`.

Q5: What is useDerivedValue?
A5: A read-only shared value computed from other shared values, auto-updated on the UI thread.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Animations, gestures, scroll-linked effects
- Values that change very often

❌ Avoid when:
- Data that should show in normal React UI (use useState)
- Data needed only for business logic

---

## 📊 Visual Diagram
```
 JS Thread                      UI Thread
 ─────────                      ─────────
 sv = useSharedValue(0)  ◄───►  same memory { value }
 sv.value = 50 ─────────────►   worklet sees 50 instantly
                                useAnimatedStyle recomputes
                                native view updated
 (NO React render)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| shared value | value visible to both threads | दोनों threads की साझा value |
| worklet | function run on UI thread | UI thread पर चलने वाला function |
| runOnJS | call JS fn from worklet | worklet से JS function बुलाना |
| derived value | computed shared value | दूसरी values से बनी value |

---

## ⚡ 3-Line Summary
English: useSharedValue stores a value readable on both threads.
Read/write with `.value`; it does not re-render React.
Use `runOnJS` to reach JS-side code like setState.

Hindi: useSharedValue ऐसी value रखता है जो दोनों threads पर पढ़ी जाती है।
`.value` से पढ़ो/लिखो; React re-render नहीं होता।
setState जैसे JS code के लिए `runOnJS` use करो।

---

## ➡️ Next Topic
**132. useAnimatedStyle** — shared values को सचमुच के styles में बदलना।
