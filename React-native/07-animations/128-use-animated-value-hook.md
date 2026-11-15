# 128. useAnimatedValue Hook
# हिंदी में: useAnimatedValue Hook — Animated.Value बनाने का आसान तरीका
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 (check current docs — APIs change between SDKs). `useAnimatedValue` React Native 0.71+ में मौजूद है; पुराने versions (Expo SDK 47 या उससे पहले) में `useRef(new Animated.Value()).current` इस्तेमाल करें।

---

## 🔵 Simple Definition (English)
`useAnimatedValue(initialValue)` is a built-in React Native hook that returns a stable `Animated.Value`. It replaces the boilerplate `useRef(new Animated.Value(0)).current`.

## 🔵 सरल परिभाषा (Hindi)
`useAnimatedValue(initialValue)` React Native का built-in hook है जो एक stable `Animated.Value` देता है। यह `useRef(new Animated.Value(0)).current` वाली boilerplate की जगह लेता है।

---

## 🔴 Problem it Solves
```
Before:
  const fade = useRef(new Animated.Value(0)).current;
  - Every render creates a NEW Animated.Value object (thrown away by useRef)
  - Easy to forget .current  -> bugs
  - Long, ugly, repeated everywhere
  - Beginners write `new Animated.Value(0)` directly -> resets every render
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  const fade = useRef(new Animated.Value(0)).current;
  - हर render में एक नया Animated.Value बनता है (useRef उसे फेंक देता है)
  - .current भूलना आसान -> bugs
  - लंबा और बार-बार दोहराना पड़ता है
  - beginners सीधे `new Animated.Value(0)` लिखते हैं -> हर render पर reset
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → import { useAnimatedValue } from 'react-native'
Step 2 → const x = useAnimatedValue(0)   // stable across renders
Step 3 → Use x in Animated.timing / spring, or in style of Animated.View
Step 4 → Component re-renders -> same x object returned (no reset)
Step 5 → Optional: x.interpolate({...}) for colors, rotation etc.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → import { useAnimatedValue } from 'react-native'
Step 2 → const x = useAnimatedValue(0)   // renders के बीच stable रहता है
Step 3 → x को Animated.timing / spring या Animated.View के style में use करो
Step 4 → Component re-render हो तो वही x object वापस मिलता है (reset नहीं)
Step 5 → चाहो तो x.interpolate({...}) से color, rotation आदि बनाओ
```

---

## 🟡 Real World Example
**Swiggy "Add to cart" heart/like button:** each food card needs its own animated scale value. With `useAnimatedValue(1)` inside a `FoodCard` component, every card has its own stable value, code stays short, and re-renders (e.g., price update) never reset the animation.

## 🟡 Real Example Hindi mein
**Swiggy की "Add to cart" / heart button:** हर food card को अपनी animated scale value चाहिए। `FoodCard` component में `useAnimatedValue(1)` से हर card की अपनी stable value होती है, code छोटा रहता है, और re-render (जैसे price update) पर animation reset नहीं होती।

---

## 💻 Code Example — Basic

```jsx
import React from 'react';                                    // React
import { View, Text, Pressable, Animated, StyleSheet, useAnimatedValue } from 'react-native'; // RN 0.71+

export default function LikeButton() {                        // component
  const scale = useAnimatedValue(1);                          // stable Animated.Value starting at 1

  const onPress = () => {                                     // on tap
    Animated.sequence([                                       // bounce: grow then shrink
      Animated.timing(scale, { toValue: 1.4, duration: 120, useNativeDriver: true }), // grow
      Animated.spring(scale, { toValue: 1, friction: 3, useNativeDriver: true }),     // settle back
    ]).start();                                               // run
  };

  return (
    <View style={styles.container}>
      <Pressable onPress={onPress}>
        {/* scale is applied via transform, so native driver works */}
        <Animated.View style={{ transform: [{ scale }] }}>
          <Text style={styles.heart}>❤️</Text>
        </Animated.View>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center' }, // center
  heart: { fontSize: 56 },                                                 // big emoji
});
```

## 💻 Code Example — Advanced

```jsx
import React, { useState, useCallback } from 'react';         // hooks
import { View, Text, FlatList, Pressable, Animated, Platform, StyleSheet, useAnimatedValue } from 'react-native';

// Each card owns its own animated values via the hook
function FoodCard({ item, onToggle }) {
  const scale = useAnimatedValue(1);                          // press feedback
  const progress = useAnimatedValue(item.liked ? 1 : 0);      // 0 = unliked, 1 = liked (initial from props)

  const toggle = useCallback(() => {                          // stable handler
    const next = item.liked ? 0 : 1;                          // target value
    Animated.parallel([                                       // do both together
      Animated.timing(progress, { toValue: next, duration: 250, useNativeDriver: false }), // color needs JS driver
      Animated.sequence([
        Animated.timing(scale, { toValue: 0.9, duration: 80, useNativeDriver: true }),
        Animated.spring(scale, { toValue: 1, friction: 4, useNativeDriver: true }),
      ]),
    ]).start();
    onToggle(item.id);                                        // update parent state
  }, [item.liked, item.id, onToggle, progress, scale]);

  const bg = progress.interpolate({                           // color between two states
    inputRange: [0, 1],
    outputRange: ['#f2f2f2', '#ffe0e3'],
  });

  return (
    // NOTE: backgroundColor animates with JS driver, transform with native driver.
    // They are on DIFFERENT values (progress vs scale) so mixing is safe,
    // but they must live on DIFFERENT Animated.View nodes.
    <Animated.View style={[styles.card, { backgroundColor: bg }]}>
      <Animated.View style={{ transform: [{ scale }] }}>
        <Pressable onPress={toggle} accessibilityRole="button" accessibilityLabel={`Like ${item.name}`}>
          <Text style={styles.name}>{item.name} {item.liked ? '❤️' : '🤍'}</Text>
        </Pressable>
      </Animated.View>
    </Animated.View>
  );
}

export default function Menu() {
  const [items, setItems] = useState([                        // sample data
    { id: '1', name: 'Paneer Tikka', liked: false },
    { id: '2', name: 'Veg Biryani', liked: true },
  ]);
  const onToggle = useCallback((id) => {                      // toggle liked flag
    setItems(prev => prev.map(i => (i.id === id ? { ...i, liked: !i.liked } : i)));
  }, []);

  return (
    <FlatList
      data={items}                                            // list data
      keyExtractor={i => i.id}                                // unique key
      renderItem={({ item }) => <FoodCard item={item} onToggle={onToggle} />} // each card has own hook state
      contentContainerStyle={{ padding: 16, paddingTop: Platform.OS === 'ios' ? 56 : 16 }} // iOS status bar room
    />
  );
}

const styles = StyleSheet.create({
  card: { padding: 16, marginBottom: 12, borderRadius: 12 },
  name: { fontSize: 18 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Hook behavior | Identical | Identical |
| Native driver | Supported for transform/opacity | Supported for transform/opacity |
| Emoji rendering (❤️) | Google Noto emoji | Apple emoji |
| Shadow on animated card | `elevation` | `shadow*` props |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo SDK 48+ ships RN 0.71+, so the hook is available out of the box
import { useAnimatedValue } from 'react-native';
const fade = useAnimatedValue(0);
```
CLI way:
```jsx
// Bare RN 0.71+: same import. RN < 0.71: hook does not exist, use:
import { useRef } from 'react';
import { Animated } from 'react-native';
const fade = useRef(new Animated.Value(0)).current;
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using the hook on RN < 0.71 (import is `undefined`, crash).
✅ Correct: Check RN version or use `useRef(new Animated.Value())`.

❌ Mistake 2: Passing a changing initial value expecting it to update the animation.
✅ Correct: Initial value is used only on the first render. Drive changes with `Animated.timing` or `setValue`.

❌ Mistake 3: Calling the hook inside loops/conditions/callbacks.
✅ Correct: Hooks rules apply. For lists, make a child component (like FoodCard).

❌ Mistake 4: Using the same value with both native and JS drivers.
✅ Correct: Separate values for layout/color (JS) and transform/opacity (native).

---

## 🧠 Tricky Interview Question
```jsx
function Box() {
  const x = new Animated.Value(0);        // A
  const y = useAnimatedValue(0);          // B
  // parent re-renders every second
}
```
Which one keeps animation progress?

Answer: **B**. `A` creates a new Animated.Value each render, so the animation visually jumps back to 0 and the old node is detached. `B` returns the same stable object across renders.

---

## ⚫ Interview Questions + Answers
Q1: What does useAnimatedValue return?
A1: A stable `Animated.Value` instance, same as `useRef(new Animated.Value(init)).current`.

Q2: Since which RN version?
A2: 0.71. Expo SDK 48 and newer include it.

Q3: Can it hold an `Animated.ValueXY`?
A3: No, `useAnimatedValue` is for a single numeric value. For XY use `useRef(new Animated.ValueXY()).current`.

Q4: Does it cause re-render when value changes?
A4: No. Animated values update native views directly, not through React state.

Q5: Is it a replacement for Reanimated's `useSharedValue`?
A5: No. It is a convenience for the core Animated API only; `useSharedValue` (topic 131) is a different library.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Using core Animated API on RN 0.71+
- You want shorter, safer code

❌ Avoid when:
- Project is on old RN (< 0.71)
- You already use Reanimated (use shared values)

---

## 📊 Visual Diagram
```
Render 1:  useAnimatedValue(0) ──► [Value #A1]
Render 2:  useAnimatedValue(0) ──► [Value #A1]  (same object)
Render 3:  useAnimatedValue(0) ──► [Value #A1]

new Animated.Value(0) in body:
Render 1 ► #B1   Render 2 ► #B2 (reset!)   Render 3 ► #B3 (reset!)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Animated.Value | number that animates | animate होने वाली संख्या |
| stable reference | same object each render | हर render में वही object |
| boilerplate | repeated setup code | बार-बार लिखा जाने वाला code |
| native driver | runs animation on UI thread | UI thread पर animation |

---

## ⚡ 3-Line Summary
English: `useAnimatedValue` gives a stable Animated.Value.
It replaces `useRef(new Animated.Value()).current`.
Needs RN 0.71+ and works only with core Animated.

Hindi: `useAnimatedValue` एक stable Animated.Value देता है।
यह `useRef(new Animated.Value()).current` की जगह लेता है।
RN 0.71+ चाहिए और सिर्फ core Animated के साथ चलता है।

---

## ➡️ Next Topic
**129. Interpolation** — एक value को colors, degrees, sizes में map करना।
