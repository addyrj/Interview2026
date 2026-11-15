# 129. Interpolation
# हिंदी में: Interpolation — एक value को दूसरी range में बदलना
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 (check current docs — APIs change between SDKs). इसमें `Animated.Value.interpolate` (core) और Reanimated का `interpolate` / `interpolateColor` दोनों दिखाए हैं।

---

## 🔵 Simple Definition (English)
Interpolation maps an input range to an output range. Example: scroll offset `0 → 100` becomes header opacity `1 → 0`. One animated number can drive many properties: opacity, rotation, color, size.

## 🔵 सरल परिभाषा (Hindi)
Interpolation एक input range को output range में map करता है। जैसे scroll offset `0 → 100` से header opacity `1 → 0`। एक animated number कई properties चला सकता है: opacity, rotation, color, size।

---

## 🔴 Problem it Solves
```
Animated.Value is just a number (0..1).
But UI needs: '0deg'->'360deg', '#fff'->'#e23744', 40px->120px, opacity 1->0.
Without interpolation: create & sync many Animated.Values by hand.
With interpolation: ONE value (progress) drives everything, always in sync.
```

## 🔴 यह क्यों बना? (Hindi)
```
Animated.Value बस एक number (0..1) है।
पर UI को चाहिए: '0deg'->'360deg', '#fff'->'#e23744', 40px->120px, opacity 1->0।
Interpolation के बिना: कई Animated.Values हाथ से बनाओ और sync करो।
Interpolation से: एक value (progress) सब कुछ चलाती है, हमेशा sync में।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → progress = Animated.Value(0)
Step 2 → inputRange: [0, 1]            (values progress can take)
Step 3 → outputRange: ['0deg','360deg'] (matching outputs, same length)
Step 4 → value.interpolate({ inputRange, outputRange }) returns a NEW animated node
Step 5 → Put the node in style. Animate progress -> style follows automatically
Step 6 → extrapolate: 'clamp' stops values going beyond the output range
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → progress = Animated.Value(0)
Step 2 → inputRange: [0, 1]            (progress की values)
Step 3 → outputRange: ['0deg','360deg'] (इनके बराबर outputs, same length)
Step 4 → value.interpolate({ inputRange, outputRange }) एक नया animated node देता है
Step 5 → उस node को style में लगाओ। progress animate करो -> style अपने आप चलती है
Step 6 → extrapolate: 'clamp' output range से बाहर जाने से रोकता है
```

---

## 🟡 Real World Example
**Swiggy restaurant page collapsing header:** as you scroll `0 → 150px`, the big banner fades (`opacity 1 → 0`), the title shrinks, and the sticky bar background turns from transparent to white. One `scrollY` value, three interpolations.

## 🟡 Real Example Hindi mein
**Swiggy restaurant page का collapsing header:** scroll `0 → 150px` होने पर बड़ा banner fade होता है (`opacity 1 → 0`), title छोटा होता है, और sticky bar का background transparent से white हो जाता है। एक `scrollY` value, तीन interpolations।

---

## 💻 Code Example — Basic

```jsx
import React, { useRef } from 'react';                         // React + ref
import { View, Text, Animated, Pressable, StyleSheet } from 'react-native'; // core

export default function InterpolateBasic() {
  const progress = useRef(new Animated.Value(0)).current;      // single driver value 0..1

  const play = () => {                                          // animate 0 -> 1
    progress.setValue(0);                                       // reset
    Animated.timing(progress, { toValue: 1, duration: 1000, useNativeDriver: false }).start(); // JS driver (color)
  };

  const rotate = progress.interpolate({                         // number -> degrees string
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });
  const bg = progress.interpolate({                             // number -> color
    inputRange: [0, 1],
    outputRange: ['#ffffff', '#e23744'],
  });
  const size = progress.interpolate({                           // number -> size
    inputRange: [0, 0.5, 1],                                    // multi-point range
    outputRange: [60, 140, 60],                                 // grow then shrink
  });

  return (
    <View style={styles.container}>
      <Animated.View
        style={[styles.box, { width: size, height: size, backgroundColor: bg, transform: [{ rotate }] }]}
      />
      <Pressable style={styles.btn} onPress={play}><Text style={{ color: '#fff' }}>Play</Text></Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  box: { borderWidth: 2, borderColor: '#e23744', borderRadius: 8 },
  btn: { marginTop: 40, padding: 12, backgroundColor: '#222', borderRadius: 8 },
});
```

## 💻 Code Example — Advanced

```jsx
import React from 'react';                                     // React
import { View, Text, Animated, Platform, StyleSheet } from 'react-native'; // core

const HEADER_MAX = 200;                                        // expanded height
const HEADER_MIN = Platform.OS === 'ios' ? 96 : 72;            // collapsed height (iOS has notch)
const RANGE = HEADER_MAX - HEADER_MIN;                         // scroll distance

export default function CollapsingHeader() {
  const scrollY = React.useRef(new Animated.Value(0)).current; // scroll offset

  const height = scrollY.interpolate({                         // header shrinks as we scroll
    inputRange: [0, RANGE],
    outputRange: [HEADER_MAX, HEADER_MIN],
    extrapolate: 'clamp',                                      // do NOT go beyond min/max
  });
  const bannerOpacity = scrollY.interpolate({                  // banner fades out
    inputRange: [0, RANGE / 2, RANGE],
    outputRange: [1, 0.4, 0],
    extrapolate: 'clamp',
  });
  const titleScale = scrollY.interpolate({                     // title becomes smaller
    inputRange: [0, RANGE],
    outputRange: [1.4, 1],
    extrapolate: 'clamp',
  });

  return (
    <View style={{ flex: 1 }}>
      <Animated.View style={[styles.header, { height }]}>      {/* height is a layout prop -> JS driver */}
        <Animated.Text style={[styles.banner, { opacity: bannerOpacity }]}>50% OFF up to ₹100</Animated.Text>
        <Animated.Text style={[styles.title, { transform: [{ scale: titleScale }] }]}>Biryani Blues</Animated.Text>
      </Animated.View>

      <Animated.ScrollView
        scrollEventThrottle={16}                               // 60 events/sec (needed on iOS for smoothness)
        onScroll={Animated.event(                              // map scroll offset into scrollY
          [{ nativeEvent: { contentOffset: { y: scrollY } } }],
          { useNativeDriver: false }                           // false because height is animated
        )}
        contentContainerStyle={{ paddingTop: HEADER_MAX }}     // content starts below header
      >
        {Array.from({ length: 30 }).map((_, i) => (            // dummy menu rows
          <Text key={i} style={styles.row}>Dish #{i + 1}</Text>
        ))}
      </Animated.ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { position: 'absolute', top: 0, left: 0, right: 0, backgroundColor: '#e23744', zIndex: 10, justifyContent: 'flex-end', padding: 16 },
  banner: { color: '#ffe', fontSize: 14 },
  title: { color: '#fff', fontSize: 24, fontWeight: '800', transformOrigin: 'left' }, // transformOrigin: RN 0.73+
  row: { padding: 20, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: '#ccc' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| interpolate API | Same | Same |
| Collapsed header height | Status bar handled separately (72) | Notch/dynamic island needs more (96) |
| scrollEventThrottle | Ignored mostly | Required (default 0 = only one event) |
| Overscroll (negative scrollY) | No bounce by default | Rubber-band bounce -> use `extrapolate: 'clamp'` |
| Color interpolation | Works | Works |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Core: no install. Reanimated version (comes with Expo SDK template):
import { interpolate, interpolateColor, useSharedValue, useAnimatedStyle } from 'react-native-reanimated';
```
CLI way:
```jsx
// Core: same. Reanimated: npm i react-native-reanimated, add
// plugin 'react-native-reanimated/plugin' LAST in babel.config.js, rebuild native app.
import { interpolate, interpolateColor } from 'react-native-reanimated';
```

Reanimated syntax (for comparison):
```jsx
const style = useAnimatedStyle(() => ({                        // runs on UI thread
  opacity: interpolate(scrollY.value, [0, 100], [1, 0], 'clamp'),            // number mapping
  backgroundColor: interpolateColor(scrollY.value, [0, 100], ['#fff', '#e23744']), // color mapping
}));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `inputRange` not ascending, or different length than `outputRange`.
✅ Correct: Same length, strictly ascending input values.

❌ Mistake 2: Forgetting `extrapolate: 'clamp'`, so values overshoot (e.g., opacity -0.5 or scale 5).
✅ Correct: Add `extrapolate: 'clamp'` (or `extrapolateLeft/Right`).

❌ Mistake 3: `useNativeDriver: true` while interpolating height/color.
✅ Correct: Only transform & opacity can use native driver.

❌ Mistake 4: Mixing units in outputRange (`['0deg', '1rad']`, `['10px','20']`).
✅ Correct: Keep consistent units.

---

## 🧠 Tricky Interview Question
```jsx
const v = new Animated.Value(0);
const o = v.interpolate({ inputRange: [0, 1], outputRange: [0, 100] });
v.setValue(2);
```
What is `o` now?

Answer: **200** with default extrapolate (`'extend'`), the line continues beyond the range. With `extrapolate: 'clamp'` it would stay at 100.

---

## ⚫ Interview Questions + Answers
Q1: What does interpolate return?
A1: A new `Animated.AnimatedInterpolation` node linked to the parent value; it updates automatically.

Q2: Extrapolate options?
A2: `'extend'` (default), `'clamp'`, `'identity'` (returns input as is).

Q3: How to animate rotation?
A3: Interpolate to degree strings: `outputRange: ['0deg','360deg']` and use in `transform: [{ rotate }]`.

Q4: Can interpolation run on native driver?
A4: Yes if final style is transform/opacity. Colors and layout need JS driver (core Animated).

Q5: Difference from Reanimated `interpolate`?
A5: Reanimated's is a plain function called inside a worklet on the UI thread; it also supports colors via `interpolateColor` without JS-driver limits.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- One value must drive many properties
- Scroll-linked effects (parallax, collapsing header)

❌ Avoid when:
- Simple one-property animation (direct timing is enough)
- Heavy gesture-driven UI (use Reanimated)

---

## 📊 Visual Diagram
```
scrollY:   0 ───── 50 ───── 100
             │       │        │
opacity:     1      0.5       0
height:    200      150      100
bgColor:  white    pink      red

 inputRange  [0, 50, 100]
 outputRange [1, 0.5, 0]     (same length!)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| inputRange | source values | इनपुट सीमा |
| outputRange | target values | आउटपुट सीमा |
| extrapolate | behavior outside range | range के बाहर का व्यवहार |
| clamp | stop at the edges | किनारे पर रोकना |
| interpolateColor | color mapping (Reanimated) | रंग mapping |

---

## ⚡ 3-Line Summary
English: Interpolation maps one number range to another.
One driver value can control opacity, color, size, rotation.
Use `extrapolate: 'clamp'` to avoid overshoot.

Hindi: Interpolation एक number range को दूसरी में बदलता है।
एक driver value से opacity, color, size, rotation चल सकते हैं।
Overshoot रोकने के लिए `extrapolate: 'clamp'` लगाओ।

---

## ➡️ Next Topic
**131. useSharedValue** — Reanimated की मूल value जो UI thread पर रहती है (130 में architecture पढ़ चुके हैं)।
