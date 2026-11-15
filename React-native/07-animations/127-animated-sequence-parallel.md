# 127. Animated.sequence + Animated.parallel
# हिंदी में: Animated.sequence और Animated.parallel — कई Animations को जोड़ना
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs). Core `Animated` API React Native के अंदर है, अलग package नहीं चाहिए।

---

## 🔵 Simple Definition (English)
`Animated.sequence([...])` runs animations **one after another**. `Animated.parallel([...])` runs animations **at the same time**. Along with `Animated.stagger` and `Animated.delay`, these are "composition" helpers of the core Animated API.

## 🔵 सरल परिभाषा (Hindi)
`Animated.sequence([...])` animations को **एक के बाद एक** चलाता है। `Animated.parallel([...])` animations को **एक साथ** चलाता है। `Animated.stagger` और `Animated.delay` के साथ ये core Animated API के "composition" helpers हैं।

---

## 🔴 Problem it Solves
```
One animation (timing/spring) is easy. Real UI needs combos:
  - Fade in AND slide up together        → parallel
  - Scale up, THEN scale down (bounce)   → sequence
  - Without helpers: nested callbacks
      anim1.start(() => anim2.start(() => anim3.start()))   // callback hell
  - Hard to stop/reset the whole chain
```

## 🔴 यह क्यों बना? (Hindi)
```
एक animation आसान है। असली UI में combo चाहिए:
  - Fade in और slide up एक साथ      → parallel
  - पहले बड़ा, फिर छोटा (bounce)      → sequence
  - Helper के बिना: nested callbacks (callback hell)
  - पूरी chain को stop/reset करना मुश्किल
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Create Animated.Value for each property (opacity, translateY)
Step 2 → Create animation objects: Animated.timing(value, {...})  (NOT started yet)
Step 3 → Wrap them: Animated.parallel([a, b]) or Animated.sequence([a, b])
Step 4 → Call .start(callback) on the wrapper -> whole group runs
Step 5 → .stop() on wrapper stops all children; .reset() resets values
Step 6 → Wrappers can be nested: sequence([ parallel([a,b]), c ])
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर property के लिए Animated.Value बनाओ (opacity, translateY)
Step 2 → animation objects बनाओ: Animated.timing(value, {...}) (अभी start नहीं)
Step 3 → Wrap करो: Animated.parallel([a, b]) या Animated.sequence([a, b])
Step 4 → wrapper पर .start(callback) call करो -> पूरा group चलता है
Step 5 → wrapper पर .stop() सारे children रोकता है; .reset() values reset करता है
Step 6 → Wrappers nest हो सकते हैं: sequence([ parallel([a,b]), c ])
```

---

## 🟡 Real World Example
**Zomato "Order placed" screen:** a green tick circle scales up first (sequence step 1), then the "Order Confirmed" text fades in and slides up together (parallel step 2), and finally the ETA card appears. That is `sequence([scaleTick, parallel([fadeText, slideText]), fadeCard])`.

## 🟡 Real Example Hindi mein
**Zomato "Order placed" screen:** हरा tick circle पहले scale होता है (sequence step 1), फिर "Order Confirmed" text एक साथ fade + slide up होता है (parallel step 2), और आखिर में ETA card दिखता है। यानी `sequence([scaleTick, parallel([fadeText, slideText]), fadeCard])`।

---

## 💻 Code Example — Basic

```jsx
import React, { useRef } from 'react';                       // React + useRef for stable Animated values
import { View, Text, Animated, Pressable, StyleSheet } from 'react-native'; // core RN components

export default function SequenceParallelBasic() {            // component
  const opacity = useRef(new Animated.Value(0)).current;      // starts invisible
  const translateY = useRef(new Animated.Value(40)).current;  // starts 40px lower

  const runParallel = () => {                                 // fade + slide together
    opacity.setValue(0);                                      // reset opacity
    translateY.setValue(40);                                  // reset position
    Animated.parallel([                                       // run both at the same time
      Animated.timing(opacity, { toValue: 1, duration: 500, useNativeDriver: true }),    // fade in
      Animated.timing(translateY, { toValue: 0, duration: 500, useNativeDriver: true }), // slide up
    ]).start();                                               // start the group
  };

  const runSequence = () => {                                 // fade out then fade in
    Animated.sequence([                                       // one after another
      Animated.timing(opacity, { toValue: 0.2, duration: 300, useNativeDriver: true }), // step 1
      Animated.timing(opacity, { toValue: 1, duration: 300, useNativeDriver: true }),   // step 2
    ]).start(({ finished }) => {                              // callback when everything ends
      console.log('sequence finished?', finished);            // false if it was stopped midway
    });
  };

  return (
    <View style={styles.container}>
      {/* Animated.View is required for animated styles */}
      <Animated.View style={[styles.box, { opacity, transform: [{ translateY }] }]}>
        <Text style={styles.text}>Order Confirmed</Text>
      </Animated.View>
      <Pressable style={styles.btn} onPress={runParallel}><Text style={styles.btnText}>Parallel</Text></Pressable>
      <Pressable style={styles.btn} onPress={runSequence}><Text style={styles.btnText}>Sequence</Text></Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center' }, // center everything
  box: { padding: 24, backgroundColor: '#e23744', borderRadius: 12 },     // Zomato red card
  text: { color: '#fff', fontSize: 18 },                                   // white text
  btn: { marginTop: 16, padding: 12, backgroundColor: '#222', borderRadius: 8 }, // button
  btnText: { color: '#fff' },                                              // button label
});
```

## 💻 Code Example — Advanced

```jsx
import React, { useRef, useState, useEffect } from 'react';   // hooks
import { View, Text, Animated, Easing, Platform, StyleSheet } from 'react-native'; // RN core

// Nested composition: tick scales (sequence) -> text fade+slide (parallel) -> staggered chips
export default function OrderPlacedAnimation({ onDone }) {    // onDone: parent callback
  const tickScale = useRef(new Animated.Value(0)).current;    // tick circle scale
  const textOpacity = useRef(new Animated.Value(0)).current;  // text opacity
  const textY = useRef(new Animated.Value(20)).current;       // text offset
  const chips = useRef([0, 1, 2].map(() => new Animated.Value(0))).current; // 3 info chips
  const [status, setStatus] = useState('running');            // UI state for debugging

  useEffect(() => {                                           // run once on mount
    const animation = Animated.sequence([                     // master timeline
      Animated.spring(tickScale, {                            // step 1: bouncy tick
        toValue: 1, friction: 4, tension: 80, useNativeDriver: true,
      }),
      Animated.parallel([                                     // step 2: text fade + slide together
        Animated.timing(textOpacity, { toValue: 1, duration: 400, useNativeDriver: true }),
        Animated.timing(textY, {
          toValue: 0, duration: 400, easing: Easing.out(Easing.cubic), useNativeDriver: true,
        }),
      ]),
      Animated.stagger(120, chips.map(v =>                    // step 3: chips 120ms apart
        Animated.timing(v, { toValue: 1, duration: 250, useNativeDriver: true }),
      )),
      Animated.delay(600),                                    // hold for a moment at the end
    ]);

    animation.start(({ finished }) => {                       // finished=false if cancelled
      if (finished) {                                         // only navigate when fully done
        setStatus('done');                                    // update state
        onDone && onDone();                                   // tell parent (e.g., go to tracking)
      }
    });

    return () => animation.stop();                            // CLEANUP: stop on unmount (avoids warnings)
  }, []);                                                     // empty deps -> once

  return (
    <View style={styles.wrap}>
      <Animated.View style={[styles.tick, { transform: [{ scale: tickScale }] }]}>
        <Text style={styles.tickText}>✓</Text>
      </Animated.View>
      <Animated.Text style={[styles.title, { opacity: textOpacity, transform: [{ translateY: textY }] }]}>
        Order Confirmed
      </Animated.Text>
      <View style={styles.row}>
        {['30 min', '₹349', 'UPI'].map((label, i) => (        // each chip has its own opacity
          <Animated.View key={label} style={[styles.chip, { opacity: chips[i] }]}>
            <Text>{label}</Text>
          </Animated.View>
        ))}
      </View>
      <Text style={styles.small}>{Platform.OS} - {status}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  tick: { width: 96, height: 96, borderRadius: 48, backgroundColor: '#2e7d32', alignItems: 'center', justifyContent: 'center' },
  tickText: { color: '#fff', fontSize: 48 },
  title: { marginTop: 20, fontSize: 22, fontWeight: '700' },
  row: { flexDirection: 'row', marginTop: 16 },
  chip: { padding: 8, marginHorizontal: 6, backgroundColor: '#eee', borderRadius: 16 },
  small: { marginTop: 24, color: '#888' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| sequence / parallel API | Same | Same |
| `useNativeDriver: true` | transform/opacity on UI thread | transform/opacity on UI thread |
| Low-end device jank | More visible on old phones if JS driver used | Rare, but still possible |
| Spring feel | Same math, tune friction/tension | Same math |
| Layout props (width/height) | Cannot use native driver | Cannot use native driver |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Core Animated needs no install. Works in Expo Go directly.
import { Animated } from 'react-native';
Animated.parallel([a, b]).start();
```
CLI way:
```jsx
// Same code. Nothing to link or configure for core Animated.
import { Animated } from 'react-native';
Animated.parallel([a, b]).start();
// Only difference: need to rebuild app if you add other native libs, not for this.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Calling `.start()` on each child inside parallel/sequence.
✅ Correct: Do NOT start children. Only call `.start()` on the wrapper.

❌ Mistake 2: Mixing `useNativeDriver: true` and `false` on the same Animated.Value.
✅ Correct: One value = one driver type. Use separate values for width (JS) and opacity (native).

❌ Mistake 3: Creating `new Animated.Value()` directly in the component body (resets every render).
✅ Correct: `useRef(new Animated.Value(0)).current`.

❌ Mistake 4: Forgetting to `.stop()` on unmount.
✅ Correct: return `() => animation.stop()` in useEffect cleanup.

---

## 🧠 Tricky Interview Question
```jsx
Animated.sequence([
  Animated.timing(a, { toValue: 1, duration: 500, useNativeDriver: true }),
  Animated.parallel([
    Animated.timing(b, { toValue: 1, duration: 300, useNativeDriver: true }),
    Animated.timing(c, { toValue: 1, duration: 800, useNativeDriver: true }),
  ]),
]).start();
```
Total duration?

Answer: **1300 ms**. Sequence: 500 + parallel. Parallel takes as long as its slowest child (800), not the sum (1100). So 500 + 800 = 1300.

---

## ⚫ Interview Questions + Answers
Q1: Difference between sequence and parallel?
A1: sequence = one after another (total = sum). parallel = together (total = max). Both return a composite animation with start/stop/reset.

Q2: What does `stopTogether` do in parallel?
A2: Default `true`: if any child is stopped/interrupted, all stop. Pass `{ stopTogether: false }` to let others continue.

Q3: Difference between stagger and sequence?
A3: `stagger(delay, anims)` starts each animation `delay` ms after the previous one *starts* (they overlap). sequence waits for the previous to *finish*.

Q4: How to know animation completed?
A4: `.start(({ finished }) => ...)`. `finished` is false if stopped before the end.

Q5: Can we animate width in a parallel with opacity natively?
A5: No. Layout props need the JS driver. Use Reanimated (topic 131+) or `LayoutAnimation`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Simple to medium choreography (entry animations, success screens)
- You want zero extra dependency

❌ Avoid when:
- Gesture-driven animations (use Reanimated + Gesture Handler)
- Animating layout props with 60fps need

---

## 📊 Visual Diagram
```
sequence([A, B, C])   A ████
                      B     ████
                      C         ████      total = A+B+C

parallel([A, B, C])   A ████
                      B ██████
                      C ███             total = max(A,B,C)

stagger(100,[A,B,C])  A ████
                      B  ████
                      C   ████
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| sequence | run in order | क्रम से चलाना |
| parallel | run together | एक साथ चलाना |
| stagger | staggered start | थोड़ी देरी से शुरू |
| composition | combining animations | animations जोड़ना |
| finished | completed flag | पूरा हुआ या नहीं |

---

## ⚡ 3-Line Summary
English: sequence runs in order, parallel runs together.
Start only the wrapper, not the children.
Total time: sequence = sum, parallel = max.

Hindi: sequence क्रम से चलाता है, parallel एक साथ।
सिर्फ wrapper को start करो, children को नहीं।
कुल समय: sequence = जोड़, parallel = सबसे लंबा।

---

## ➡️ Next Topic
**128. useAnimatedValue Hook** — React Native का built-in hook जो `useRef(new Animated.Value())` की boilerplate हटाता है।
