# 132. useAnimatedStyle
# हिंदी में: useAnimatedStyle — Shared value से animated style बनाना
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76, react-native-reanimated 3.x (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
`useAnimatedStyle(() => ({...}))` returns a style object that updates automatically when the shared values read inside it change. The function is a worklet and runs on the UI thread. You apply the result to an `Animated.View` (or `Animated.Text`, `Animated.Image`).

## 🔵 सरल परिभाषा (Hindi)
`useAnimatedStyle(() => ({...}))` ऐसा style object देता है जो अंदर पढ़ी गई shared values बदलते ही अपने आप update होता है। यह function worklet है और UI thread पर चलता है। नतीजा `Animated.View` (या `Animated.Text`, `Animated.Image`) पर लगाते हैं।

---

## 🔴 Problem it Solves
```
Old way (Animated API):
  style={{ opacity: anim }}  -> need interpolate() for everything, limited props
  Color/width with native driver -> NOT possible

useAnimatedStyle:
  - Write plain JS inside: conditions, math, any style prop
  - Runs on UI thread -> no jank
  - Auto-tracks shared values (no dependency arrays in most cases)
```

## 🔴 यह क्यों बना? (Hindi)
```
पुराना तरीका (Animated API):
  style={{ opacity: anim }}  -> हर चीज़ के लिए interpolate(), सीमित props
  Color/width native driver से -> संभव नहीं

useAnimatedStyle:
  - अंदर साधारण JS लिखो: conditions, math, कोई भी style prop
  - UI thread पर चलता है -> jank नहीं
  - shared values अपने आप track होती हैं (अक्सर dependency array नहीं चाहिए)
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → const w = useSharedValue(100)
Step 2 → const style = useAnimatedStyle(() => ({ width: w.value }))
Step 3 → Babel plugin turns the arrow fn into a worklet
Step 4 → Reanimated notes: this worklet reads w -> subscribe
Step 5 → w.value changes -> worklet re-runs on UI thread -> new style object
Step 6 → <Animated.View style={[styles.box, style]} /> receives native update
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → const w = useSharedValue(100)
Step 2 → const style = useAnimatedStyle(() => ({ width: w.value }))
Step 3 → Babel plugin arrow function को worklet बना देता है
Step 4 → Reanimated देखता है कि worklet w पढ़ता है -> subscribe
Step 5 → w.value बदला -> worklet UI thread पर दोबारा चला -> नया style object
Step 6 → <Animated.View style={[styles.box, style]} /> को native update मिलता है
```

---

## 🟡 Real World Example
**Zomato veg/non-veg toggle & Instagram heart:** a toggle's background changes colour and its knob slides. One `progress` shared value drives `backgroundColor` and `translateX` inside two `useAnimatedStyle` hooks. Instagram's double-tap heart uses scale + opacity styles the same way.

## 🟡 Real Example Hindi mein
**Zomato veg/non-veg toggle और Instagram heart:** toggle का background color बदलता है और knob slide होता है। एक `progress` shared value दो `useAnimatedStyle` में `backgroundColor` और `translateX` चलाती है। Instagram का double-tap heart भी scale + opacity styles इसी तरह use करता है।

---

## 💻 Code Example — Basic

```jsx
import React from 'react';                                     // React
import { View, Pressable, Text, StyleSheet } from 'react-native'; // core
import Animated, { useSharedValue, useAnimatedStyle, withTiming } from 'react-native-reanimated'; // Reanimated

export default function GrowBox() {
  const size = useSharedValue(80);                              // width/height in px

  const boxStyle = useAnimatedStyle(() => ({                    // worklet
    width: size.value,                                          // layout props allowed (unlike native Animated)
    height: size.value,                                         // same
    borderRadius: size.value / 4,                               // computed with math
  }));

  const toggle = () => {                                        // press handler
    size.value = withTiming(size.value === 80 ? 160 : 80, { duration: 400 }); // 80 <-> 160
  };

  return (
    <View style={styles.container}>
      <Animated.View style={[styles.box, boxStyle]} />          {/* static + animated style array */}
      <Pressable style={styles.btn} onPress={toggle}><Text style={{ color: '#fff' }}>Toggle size</Text></Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  box: { backgroundColor: '#e23744' },                          // static style (color)
  btn: { marginTop: 24, padding: 12, backgroundColor: '#222', borderRadius: 8 },
});
```

## 💻 Code Example — Advanced

```jsx
import React, { useState } from 'react';                       // React + state
import { Pressable, Platform, StyleSheet, AccessibilityInfo } from 'react-native'; // core
import Animated, {
  useSharedValue, useAnimatedStyle, withSpring, interpolateColor, interpolate, useReducedMotion,
} from 'react-native-reanimated';                              // Reanimated

const W = 64, H = 34, KNOB = 28;                                // toggle dimensions

export default function VegToggle({ onChange }) {
  const [isVeg, setIsVeg] = useState(false);                    // real state for app logic
  const progress = useSharedValue(0);                           // 0 = off, 1 = on (animation driver)
  const reduceMotion = useReducedMotion();                      // user accessibility setting

  const trackStyle = useAnimatedStyle(() => ({                  // background color blend
    backgroundColor: interpolateColor(progress.value, [0, 1], ['#bdbdbd', '#2e7d32']),
  }));

  const knobStyle = useAnimatedStyle(() => ({                   // knob slide + tiny squash
    transform: [
      { translateX: interpolate(progress.value, [0, 1], [3, W - KNOB - 3]) },
      { scaleX: interpolate(progress.value, [0, 0.5, 1], [1, 1.15, 1]) },
    ],
  }));

  const onPress = () => {
    const next = !isVeg;                                        // flip
    setIsVeg(next);                                             // update React state
    progress.value = reduceMotion                               // respect reduced motion
      ? (next ? 1 : 0)                                          // jump without animation
      : withSpring(next ? 1 : 0, { damping: 15, stiffness: 180 }); // spring animation
    onChange && onChange(next);                                 // inform parent
  };

  return (
    <Pressable onPress={onPress} accessibilityRole="switch" accessibilityState={{ checked: isVeg }} accessibilityLabel="Veg only">
      <Animated.View style={[styles.track, trackStyle]}>
        <Animated.View style={[styles.knob, knobStyle]} />
      </Animated.View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  track: { width: W, height: H, borderRadius: H / 2, justifyContent: 'center' },
  knob: {
    width: KNOB, height: KNOB, borderRadius: KNOB / 2, backgroundColor: '#fff',
    ...Platform.select({ ios: { shadowOpacity: 0.25, shadowRadius: 2, shadowOffset: { width: 0, height: 1 } }, android: { elevation: 2 } }),
  },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Animated style output | Same | Same |
| Shadow on animated view | `elevation` (doesn't animate smoothly with opacity) | `shadow*` props animate fine |
| `overflow: hidden` + borderRadius animation | Fine | Fine, but clipping cost on big views |
| Reduced motion | Developer option "Animator duration scale" | Accessibility > Reduce Motion |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install react-native-reanimated
// Works in Expo Go (Expo's bundled Reanimated version) and dev builds.
import Animated, { useAnimatedStyle } from 'react-native-reanimated';
```
CLI way:
```jsx
// npm i react-native-reanimated + babel plugin (last) + pod install + rebuild
// After changing babel config run: npx react-native start --reset-cache
import Animated, { useAnimatedStyle } from 'react-native-reanimated';
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using the style on a normal `View`.
✅ Correct: Use `Animated.View` (or `Animated.createAnimatedComponent(MyComp)`).

❌ Mistake 2: Reading `useState` values inside without thinking (captured by value at render; stale or re-creates worklet).
✅ Correct: Keep animation inputs in shared values.

❌ Mistake 3: Calling a normal JS function inside the worklet (crash: "Tried to synchronously call a non-worklet function").
✅ Correct: Mark it `'worklet'` or use `runOnJS(fn)()`.

❌ Mistake 4: Putting a style object with `transform` in static style AND animated style both.
✅ Correct: Animated `transform` replaces the static one, put all transforms in one place.

---

## 🧠 Tricky Interview Question
```jsx
const x = useSharedValue(0);
const s = useAnimatedStyle(() => ({ left: x.value }));
x.value = 100;           // in render body, directly
```
What happens?

Answer: It works, but it is a bad practice: writing a shared value during render is a side effect (Reanimated warns in strict mode). The view jumps to 100 with no animation. Write in event handlers, `useEffect`, or gesture callbacks, and use `withTiming` to animate.

---

## ⚫ Interview Questions + Answers
Q1: Where does the useAnimatedStyle callback run?
A1: On the UI thread, as a worklet, re-run when any shared value read inside changes.

Q2: Do we need a dependency array?
A2: Usually no (auto-tracked via Babel plugin). Add one only when reading plain JS variables in some setups (e.g., web without plugin).

Q3: Can it return any style prop?
A3: Any prop supported by the native view, including layout, color, and transform. Not everything is cheap: animating layout (width/height) triggers layout each frame.

Q4: How do you combine static and animated styles?
A4: Array: `style={[styles.box, animatedStyle]}`.

Q5: useAnimatedStyle vs useAnimatedProps?
A5: Style is for style props. `useAnimatedProps` animates non-style props (e.g., SVG `r`, TextInput `text`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any Reanimated-driven visual change
- Need color/layout animations with 60fps

❌ Avoid when:
- Static styling (plain StyleSheet is cheaper)
- Value is needed in React render (use state)

---

## 📊 Visual Diagram
```
 sharedValue ──read──► useAnimatedStyle worklet ──► style object
     ▲                         (UI thread)               │
     │                                                   ▼
 withTiming/gesture                              <Animated.View />
                                                  native view updated
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Animated.View | view that accepts animated style | animated style लेने वाला view |
| worklet | UI-thread function | UI thread function |
| interpolateColor | blend colors by progress | progress से रंग मिलाना |
| useAnimatedProps | animate non-style props | non-style props animate करना |

---

## ⚡ 3-Line Summary
English: useAnimatedStyle builds a live style from shared values.
It runs as a worklet on the UI thread and needs Animated components.
Use it for colors, layout and transforms alike.

Hindi: useAnimatedStyle shared values से live style बनाता है।
यह UI thread पर worklet की तरह चलता है और Animated components चाहिए।
रंग, layout और transform सब के लिए use करो।

---

## ➡️ Next Topic
**133. withTiming + withSpring** — values को सचमुच animate करने वाले functions।
