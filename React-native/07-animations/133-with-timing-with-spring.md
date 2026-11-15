# 133. withTiming + withSpring
# हिंदी में: withTiming और withSpring — Reanimated के दो मुख्य animation functions
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76, react-native-reanimated 3.x (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
`withTiming(toValue, config)` moves a shared value to a target in a **fixed duration** with an easing curve. `withSpring(toValue, config)` moves it using **physics** (mass, damping, stiffness), so it overshoots and settles naturally; there is no fixed duration.

## 🔵 सरल परिभाषा (Hindi)
`withTiming(toValue, config)` shared value को **तय समय (duration)** में easing curve के साथ target तक ले जाता है। `withSpring(toValue, config)` **physics** (mass, damping, stiffness) से चलाता है, इसलिए यह थोड़ा आगे जाकर स्वाभाविक रूप से रुकता है; इसकी कोई तय duration नहीं होती।

---

## 🔴 Problem it Solves
```
Setting sv.value = 100 -> instant jump (no animation).
We need to describe HOW to get there:
  withTiming : predictable (300ms, ease-out)  -> fades, progress bars
  withSpring : natural, bouncy, interruptible -> buttons, sheets, drag release
Both run entirely on UI thread and can be interrupted smoothly mid-way.
```

## 🔴 यह क्यों बना? (Hindi)
```
sv.value = 100 लिखने से value तुरंत कूद जाती है (animation नहीं)।
हमें बताना होता है वहाँ पहुँचना KAISE है:
  withTiming : अनुमानित (300ms, ease-out)  -> fade, progress bar
  withSpring : स्वाभाविक, उछलता, बीच में रोका जा सकता -> button, sheet, drag छोड़ना
दोनों UI thread पर चलते हैं और बीच में बदलाव पर भी smooth रहते हैं।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → sv.value = withTiming(1, { duration: 500, easing: Easing.out(Easing.cubic) })
Step 2 → Reanimated records start value, target, start time
Step 3 → On every frame (UI thread) it computes the current value from the curve
Step 4 → withSpring does the same but integrates spring physics each frame
Step 5 → When done, optional callback: (finished, current) => {...} runs on UI thread
Step 6 → If you assign a new animation mid-way, the old one is cancelled and the new one
         starts from the current value (spring keeps velocity -> feels natural)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → sv.value = withTiming(1, { duration: 500, easing: Easing.out(Easing.cubic) })
Step 2 → Reanimated start value, target और start time याद रखता है
Step 3 → हर frame (UI thread) पर curve से मौजूदा value निकालता है
Step 4 → withSpring वही करता है पर हर frame spring physics जोड़ता है
Step 5 → खत्म होने पर callback: (finished, current) => {...} UI thread पर चलता है
Step 6 → बीच में नई animation दो तो पुरानी cancel होती है और नई मौजूदा value से शुरू
         (spring velocity बनाए रखता है -> स्वाभाविक लगता है)
```

---

## 🟡 Real World Example
**Swiggy bottom sheet / PhonePe "Pay" button:** the "View Cart" bar slides up with `withSpring` (bouncy, friendly). The progress line of "Order is being prepared" fills with `withTiming` linearly over the exact ETA. Tapping the Paytm "Pay" button scales to 0.95 on press-in and springs back on release.

## 🟡 Real Example Hindi mein
**Swiggy bottom sheet / PhonePe "Pay" button:** "View Cart" bar `withSpring` से ऊपर आती है (उछलती, friendly)। "Order is being prepared" की progress line `withTiming` से ETA के ठीक समय में linearly भरती है। Paytm "Pay" button press-in पर 0.95 तक छोटा होता है और छोड़ने पर spring से वापस आता है।

---

## 💻 Code Example — Basic

```jsx
import React from 'react';                                      // React
import { View, Pressable, Text, StyleSheet } from 'react-native'; // core
import Animated, {
  useSharedValue, useAnimatedStyle, withTiming, withSpring, Easing,
} from 'react-native-reanimated';                               // Reanimated 3

export default function TimingVsSpring() {
  const a = useSharedValue(0);                                   // box A translateX (timing)
  const b = useSharedValue(0);                                   // box B translateX (spring)

  const aStyle = useAnimatedStyle(() => ({ transform: [{ translateX: a.value }] })); // A style
  const bStyle = useAnimatedStyle(() => ({ transform: [{ translateX: b.value }] })); // B style

  const go = () => {                                             // toggle both to 200 or 0
    const target = a.value === 0 ? 200 : 0;                      // choose direction
    a.value = withTiming(target, {                               // fixed 600ms
      duration: 600,                                             // ms
      easing: Easing.out(Easing.exp),                            // fast start, slow end
    });
    b.value = withSpring(target, {                               // physics
      damping: 8,                                                // lower = more bounce
      stiffness: 120,                                            // higher = faster
      mass: 1,                                                   // heavier = slower
    });
  };

  return (
    <View style={styles.container}>
      <Animated.View style={[styles.box, { backgroundColor: '#e23744' }, aStyle]} />
      <Animated.View style={[styles.box, { backgroundColor: '#5f259f' }, bStyle]} />
      <Pressable style={styles.btn} onPress={go}><Text style={{ color: '#fff' }}>Go</Text></Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, justifyContent: 'center' },
  box: { width: 60, height: 60, borderRadius: 10, marginBottom: 20 },
  btn: { padding: 12, backgroundColor: '#222', borderRadius: 8, alignSelf: 'flex-start' },
});
```

## 💻 Code Example — Advanced

```jsx
import React, { useState } from 'react';                        // React
import { Text, Pressable, View, Platform, StyleSheet } from 'react-native'; // core
import Animated, {
  useSharedValue, useAnimatedStyle, withTiming, withSpring, runOnJS, Easing, cancelAnimation,
} from 'react-native-reanimated';                               // Reanimated 3

// "View Cart" bar: springs in, scales on press, progress fills with timing,
// with completion callback and cancel handling.
export default function CartBar({ itemCount, onCheckout }) {
  const y = useSharedValue(120);                                 // starts off-screen (below)
  const pressed = useSharedValue(0);                             // 0 or 1 for press scale
  const progress = useSharedValue(0);                            // 0..1 fill bar
  const [done, setDone] = useState(false);                       // JS-side flag

  React.useEffect(() => {
    y.value = itemCount > 0 ? withSpring(0, { damping: 14, stiffness: 140 }) : withTiming(120, { duration: 200 });
  }, [itemCount]);                                               // react to prop change

  const barStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: y.value }, { scale: 1 - pressed.value * 0.04 }], // press shrink 4%
  }));
  const fillStyle = useAnimatedStyle(() => ({ width: `${progress.value * 100}%` })); // percent string is OK

  const startCheckout = () => {
    cancelAnimation(progress);                                   // stop any running fill
    progress.value = 0;                                          // restart
    progress.value = withTiming(1, { duration: 1500, easing: Easing.linear }, (finished) => {
      // runs on UI thread; finished=false if cancelled
      if (finished) runOnJS(setDone)(true);                      // go back to JS thread for state
      if (finished) runOnJS(onCheckout)();                       // notify parent
    });
  };

  return (
    <Animated.View style={[styles.bar, barStyle]}>
      <Pressable
        onPressIn={() => { pressed.value = withTiming(1, { duration: 80 }); }}      // press down
        onPressOut={() => { pressed.value = withSpring(0); }}                        // spring release
        onPress={startCheckout}
        style={styles.inner}
      >
        <Text style={styles.text}>{itemCount} items | {done ? 'Done!' : 'View Cart'}</Text>
        <View style={styles.track}><Animated.View style={[styles.fill, fillStyle]} /></View>
      </Pressable>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  bar: {
    position: 'absolute', left: 16, right: 16, bottom: Platform.OS === 'ios' ? 34 : 16, // iOS home indicator
    backgroundColor: '#60b246', borderRadius: 12,
    ...Platform.select({ ios: { shadowOpacity: 0.25, shadowRadius: 6 }, android: { elevation: 6 } }),
  },
  inner: { padding: 16 },
  text: { color: '#fff', fontWeight: '700' },
  track: { height: 4, backgroundColor: 'rgba(255,255,255,0.3)', marginTop: 8, borderRadius: 2, overflow: 'hidden' },
  fill: { height: 4, backgroundColor: '#fff' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| withTiming / withSpring | Same API and math | Same API and math |
| Bottom offset | Nav bar / gesture area varies | Safe area (home indicator) ~34 |
| Shadow | `elevation` | `shadow*` |
| Dropped frames (low-end) | Possible with heavy layouts | Less common |
| Animator duration scale (dev option) | Can slow/disable animations | Not applicable |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install react-native-reanimated
import { withTiming, withSpring, Easing } from 'react-native-reanimated';
```
CLI way:
```jsx
// npm i react-native-reanimated, babel plugin LAST, pod install, rebuild
import { withTiming, withSpring, Easing } from 'react-native-reanimated';
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `withTiming(...)` called but not assigned: `withTiming(1)`.
✅ Correct: `sv.value = withTiming(1)`; it returns an animation descriptor.

❌ Mistake 2: Giving `duration` to `withSpring` (older versions ignore it) and expecting fixed time.
✅ Correct: Tune `damping/stiffness/mass`. (Reanimated 3.x also has `duration` mode via `dampingRatio`, check docs.)

❌ Mistake 3: Calling `setState` in the callback directly.
✅ Correct: `runOnJS(setState)(value)`.

❌ Mistake 4: Spring never "settles" (tiny oscillation).
✅ Correct: Tune `restDisplacementThreshold`, `restSpeedThreshold` or raise damping.

---

## 🧠 Tricky Interview Question
```jsx
sv.value = withTiming(100, { duration: 1000 });
setTimeout(() => { sv.value = withTiming(0, { duration: 1000 }); }, 500);
```
How long to return to 0, and from where does it start?

Answer: At 500 ms the value is partway (about 50 with linear easing; default easing is `Easing.inOut(Easing.quad)`, so ~50 too at the midpoint). The new animation starts **from the current value** and takes the **full 1000 ms** (not proportional). So return finishes at 1500 ms total.

---

## ⚫ Interview Questions + Answers
Q1: When prefer withSpring over withTiming?
A1: Interactive/physical UI (drag release, button press, sheets) because it keeps velocity and feels natural. withTiming for exact-duration effects (fade, progress).

Q2: Key spring parameters?
A2: `damping` (resistance), `stiffness` (pull strength), `mass` (inertia), `overshootClamping` (no overshoot), `velocity`.

Q3: What is the animation callback signature?
A3: `(finished?: boolean, current?: AnimatableValue) => void`, runs on UI thread.

Q4: How to stop an animation?
A4: `cancelAnimation(sv)` or assign a plain number.

Q5: Default easing of withTiming?
A5: `Easing.inOut(Easing.quad)` and default duration 300ms.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- timing: fades, progress, color changes with exact duration
- spring: touch-driven, bouncy, interruptible motion

❌ Avoid when:
- Spring for opacity (overshoot gives opacity > 1 weirdness; clamp it)
- Layout-heavy lists at 60fps (animate transforms instead)

---

## 📊 Visual Diagram
```
value
 100 ┤            withTiming         withSpring
     │          ______________      ___╭╮__ ___
     │       __/                  _╭─╯  ╰─╯
     │     _/                    /
   0 ┼────/──────────────►     _/────────────────► time
       fixed duration (600ms)   overshoot, then settles
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| easing | speed curve | गति का वक्र |
| damping | spring resistance | spring का अवरोध |
| stiffness | spring tightness | spring की कसावट |
| overshoot | going past target | target से आगे जाना |
| cancelAnimation | stop running animation | चलती animation रोकना |

---

## ⚡ 3-Line Summary
English: withTiming = fixed duration + easing; withSpring = physics.
Always assign the result to `sv.value`.
Use `runOnJS` in callbacks to touch React state.

Hindi: withTiming = तय समय + easing; withSpring = physics।
नतीजा हमेशा `sv.value` में assign करो।
callback में React state के लिए `runOnJS` लगाओ।

---

## ➡️ Next Topic
**134. withSequence + withDelay** — कई animations को क्रम और देरी से जोड़ना।
