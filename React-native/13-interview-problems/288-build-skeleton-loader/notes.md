# 288. Interview Problem: Build a Skeleton Loader
# हिंदी में: Skeleton Loader बनाओ
# Platform: Both ✅ (Android ✅ | iOS ✅)
# Difficulty: ⭐⭐ Easy-Medium | Asked at: Zomato, Swiggy, Flipkart, Myntra

Files: `Skeleton.jsx` (`SkeletonBox`, `RestaurantCardSkeleton`), `RestaurantListScreen.jsx`.
Target: Expo SDK 52 (check current docs — APIs change between SDKs). Core RN only.

---

## 🔵 Simple Definition (English)
A skeleton loader shows grey, softly pulsing placeholder shapes in the same layout as the real content while data is loading, instead of a spinner.

## 🔵 सरल परिभाषा (Hindi)
Skeleton loader data आने तक असली content जैसी ही layout में धूसर (grey), हल्के चमकते placeholder shapes दिखाता है, spinner की जगह।

---

## 🔴 Problem it Solves
A blank screen or a spinner feels slow and the layout jumps when data arrives. A skeleton shows the structure immediately, so the app feels faster (perceived performance) and nothing jumps.

## 🔴 यह क्यों बना? (Hindi)
खाली screen या spinner धीमा लगता है और data आने पर layout उछलता है। Skeleton तुरंत structure दिखाता है, इसलिए app तेज़ महसूस होता है (perceived performance) और layout नहीं उछलता।

---

## 🔴 Problem Statement
Build a reusable pulsing `SkeletonBox`, compose a restaurant-card skeleton from it, show 4 skeletons while the list loads (about 1.5 s fake API), then swap to the real `FlatList`. Animations must stop on unmount.

## 💡 Approach
```
SkeletonBox: Animated.Value opacity, loop(sequence(0.4 -> 1 -> 0.4)), stop on unmount
RestaurantCardSkeleton: same sizes as the real card (image 140, title 18, subtitle 14)
Screen: data === null -> 4 skeletons ; else FlatList
```

## 🟢 How it Works — Step by Step
```
Step 1 → data starts as null (means "loading")
Step 2 → Render 4 RestaurantCardSkeleton
Step 3 → Each SkeletonBox runs Animated.loop between opacity 0.4 and 1
Step 4 → API resolves -> setData(list)
Step 5 → Screen renders the FlatList; skeletons unmount and loops stop (cleanup)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → data शुरू में null है (मतलब loading)
Step 2 → 4 RestaurantCardSkeleton दिखाओ
Step 3 → हर SkeletonBox की opacity 0.4 और 1 के बीच loop में चलती है
Step 4 → API जवाब दे -> setData(list)
Step 5 → FlatList दिखती है; skeletons हटते हैं और cleanup से loop रुकता है
```

---

## 🟡 Real World Example
Swiggy and Zomato show grey restaurant cards before the list; Flipkart and Myntra show grey product grids; LinkedIn, YouTube, Facebook use the same pattern.

## 🟡 Real Example Hindi mein
Swiggy और Zomato list से पहले grey restaurant cards दिखाते हैं; Flipkart और Myntra grey product grid; LinkedIn, YouTube, Facebook भी यही pattern इस्तेमाल करते हैं।

---

## 💻 Code Example — Basic
```jsx
import React, { useEffect, useRef } from 'react';                // hooks
import { Animated } from 'react-native';                         // animation

// One grey block that pulses
export function SkeletonBox({ width = '100%', height = 16, radius = 6, style }) {
  const opacity = useRef(new Animated.Value(0.4)).current;       // pulse value
  useEffect(() => {
    const loop = Animated.loop(Animated.sequence([               // repeat forever
      Animated.timing(opacity, { toValue: 1, duration: 700, useNativeDriver: true }),   // brighten
      Animated.timing(opacity, { toValue: 0.4, duration: 700, useNativeDriver: true }), // dim
    ]));
    loop.start();                                                // run
    return () => loop.stop();                                    // cleanup (avoid leaks)
  }, [opacity]);
  return <Animated.View style={[{ width, height, borderRadius: radius, backgroundColor: '#E1E1E1', opacity }, style]} />;
}
```

## 💻 Code Example — Advanced
Compose a card skeleton and switch on loading state (`RestaurantListScreen.jsx`):
```jsx
export function RestaurantCardSkeleton() {
  return (
    <View style={{ padding: 16 }}>
      <SkeletonBox height={140} radius={12} />                   {/* image */}
      <SkeletonBox width="60%" height={18} style={{ marginTop: 10 }} />  {/* title */}
      <SkeletonBox width="40%" height={14} style={{ marginTop: 6 }} />   {/* subtitle */}
    </View>
  );
}

const [data, setData] = useState(null);                          // null = loading
useEffect(() => {
  const t = setTimeout(() => setData([...]), 1500);              // replace with fetch()
  return () => clearTimeout(t);                                  // cleanup
}, []);

if (!data) return <View>{[0, 1, 2, 3].map((i) => <RestaurantCardSkeleton key={i} />)}</View>;
return <FlatList data={data} keyExtractor={(i) => i.id} renderItem={...} />;
```
Upgrades: a shimmer (moving gradient) with `expo-linear-gradient` + `translateX` animation; handle the "error" and "empty" states separately (do not show a skeleton forever); respect reduced motion with `AccessibilityInfo.isReduceMotionEnabled()`.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Opacity animation | Smooth with native driver | Smooth with native driver |
| Shimmer gradient | `expo-linear-gradient` fine, many layers can drop frames on low-end phones | Smooth |
| Dark mode colour | Pick a darker grey for dark theme | Same |
| Reduce motion setting | Remove animations setting | Reduce Motion |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Pulse version: no install.
// Shimmer: npx expo install expo-linear-gradient
```
CLI way:
```jsx
// Pulse version: no install.
// Shimmer: npm i react-native-linear-gradient ; cd ios && pod install
// Or: npm i react-native-skeleton-placeholder
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Skeleton with different height than the real card -> layout jump.
✅ Correct: Same dimensions.

❌ Mistake 2: Not stopping the loop on unmount (memory/CPU leak).
✅ Correct: `return () => loop.stop()`.

❌ Mistake 3: Showing a skeleton forever when the API fails.
✅ Correct: Error + retry UI.

❌ Mistake 4: Skeleton for very fast loads (flash of grey for 100 ms).
✅ Correct: Delay showing it by ~200-300 ms.

---

## 🧠 Tricky Interview Question
Why is `Animated.loop` run in `useEffect` with cleanup, and what happens without cleanup after the screen unmounts?

Answer: `Animated.loop` keeps scheduling frames forever. Without `loop.stop()` the animation keeps running on a detached value, wasting CPU and possibly warning about updates on unmounted components. The cleanup stops it when the skeleton disappears.

---

## ⚫ Interview Questions + Answers
Q1: Skeleton vs spinner?
A1: Skeleton conveys structure and feels faster; spinner is fine for short, unknown-shape actions (button submit).

Q2: Why `useNativeDriver: true`?
A2: Opacity is supported natively; it runs off the JS thread.

Q3: How to make shimmer?
A3: A `LinearGradient` wider than the box, animate `translateX`, clip with `overflow: 'hidden'`.

Q4: Many skeleton items — performance?
A4: One shared `Animated.Value` for all boxes instead of one per box.

Q5: Accessibility?
A5: Mark the container `accessibilityLabel="Loading"` / `accessibilityState={{ busy: true }}`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Lists, cards, profile pages that load from an API

❌ Avoid when:
- Loads under ~200ms or purely actions (use button spinner)

---

## 📊 Visual Diagram
```
 LOADING                         LOADED
 ┌──────────────────────┐        ┌──────────────────────┐
 │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ image  │ [Paradise photo]     │
 │ ▓▓▓▓▓▓▓▓▓            │ title  │ Paradise             │
 │ ▓▓▓▓▓▓               │ sub    │ Biryani • 4.3        │
 └──────────────────────┘        └──────────────────────┘
  opacity pulses 0.4 ↔ 1          same sizes = no jump
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Skeleton | Placeholder shape | ढाँचा / placeholder |
| Shimmer | Moving highlight | चमकती लहर |
| Perceived performance | How fast it feels | महसूस होने वाली गति |
| Layout shift | Content jumping | Layout का उछलना |
| Animated.loop | Repeat animation | दोहराने वाली animation |

---

## ⚡ 3-Line Summary
English: Show grey pulsing boxes shaped like the real content while loading.
Use `Animated.loop` with cleanup, and keep sizes identical to avoid layout jumps.
Handle error and fast-load cases separately.

Hindi: Loading के समय असली content जैसे आकार के grey pulsing boxes दिखाएँ।
`Animated.loop` को cleanup के साथ चलाएँ और sizes एक जैसे रखें ताकि layout न उछले।
Error और बहुत तेज़ load के cases अलग संभालें।

---

## ✅ What was verified
react-native-web + jsdom: skeleton phase renders (no data text), then after ~1.5 s the real list text appears. The native-driver pulse and low-end device performance were not run (no device).

---

## ➡️ Next Topic
289. Build Custom Tab Bar — another reusable UI piece, now tied to navigation.
