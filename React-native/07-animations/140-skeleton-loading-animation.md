# 140. Skeleton Loading Animation
# हिंदी में: Skeleton Loading Animation — डेटा आने तक shimmer placeholder
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76, react-native-reanimated 3.x (check current docs — APIs change between SDKs). Basic version सिर्फ core `Animated` से बनता है, कोई extra package नहीं।

---

## 🔵 Simple Definition (English)
A skeleton screen shows grey placeholder shapes (lines, circles, cards) in the layout of the real content while data loads. A pulse or shimmer animation tells the user "content is coming", so the app feels faster than a blank screen or a spinner.

## 🔵 सरल परिभाषा (Hindi)
Skeleton screen में data load होने तक असली content की layout जैसी grey placeholder shapes (lines, circles, cards) दिखती हैं। pulse या shimmer animation बताती है कि "content आ रहा है", इसलिए खाली screen या spinner से app तेज़ लगता है।

---

## 🔴 Problem it Solves
```
Blank screen / spinner:  user feels waiting, layout jumps when data arrives.
Skeleton:  shows the structure instantly (perceived performance),
           reserves the same space => no layout shift,
           shimmer = "alive" feedback.
```

## 🔴 यह क्यों बना? (Hindi)
```
खाली screen / spinner:  user को इंतज़ार लगता है, data आने पर layout उछलता है।
Skeleton:  structure तुरंत दिखता है (perceived performance),
           उतनी ही जगह घेरता है => layout shift नहीं,
           shimmer = "ज़िंदा" feedback।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Build a <Skeleton width height radius /> primitive: a grey rounded View
Step 2 → Animate: opacity loop 0.4 <-> 1 (pulse) OR a light gradient moving left->right (shimmer)
Step 3 → Compose into <RestaurantCardSkeleton /> matching the real card layout
Step 4 → Render skeletons while `loading === true`, real list when data arrives
Step 5 → Use ONE shared animation value for all skeletons on screen (in sync, cheaper)
Step 6 → Stop animation on unmount, hide from screen readers (accessibility)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → <Skeleton width height radius /> primitive बनाओ: grey गोल कोनों वाला View
Step 2 → Animate: opacity loop 0.4 <-> 1 (pulse) या हल्का gradient बाएँ->दाएँ (shimmer)
Step 3 → असली card जैसा <RestaurantCardSkeleton /> बनाओ
Step 4 → `loading === true` पर skeletons, data आने पर असली list
Step 5 → screen के सभी skeletons के लिए एक shared animation value (sync, सस्ता)
Step 6 → unmount पर animation रोको, screen reader से छुपाओ (accessibility)
```

---

## 🟡 Real World Example
**Swiggy/Zomato home feed:** when you open the app on slow network, grey restaurant cards with a moving shine appear instantly. **Instagram/LinkedIn** feeds and **Hotstar** carousels use the same trick. As soon as the API responds, the skeletons are swapped with real cards.

## 🟡 Real Example Hindi mein
**Swiggy/Zomato home feed:** slow network पर app खोलने से तुरंत चमकते हुए grey restaurant cards दिखते हैं। **Instagram/LinkedIn** feeds और **Hotstar** carousels भी यही तरीका अपनाते हैं। API जवाब देते ही skeletons असली cards से बदल जाते हैं।

---

## 💻 Code Example — Basic

```jsx
import React, { useEffect, useRef } from 'react';               // React hooks
import { View, Animated, StyleSheet } from 'react-native';      // core only, no extra package

// Reusable skeleton block with a pulse animation
export function Skeleton({ width, height, radius = 8, style }) {
  const opacity = useRef(new Animated.Value(0.4)).current;      // start dim

  useEffect(() => {
    const loop = Animated.loop(                                  // repeat forever
      Animated.sequence([                                        // dim -> bright -> dim
        Animated.timing(opacity, { toValue: 1, duration: 700, useNativeDriver: true }),
        Animated.timing(opacity, { toValue: 0.4, duration: 700, useNativeDriver: true }),
      ]),
    );
    loop.start();                                                // begin
    return () => loop.stop();                                    // cleanup on unmount
  }, [opacity]);

  return (
    <Animated.View
      accessible={false}                                         // not read by screen reader
      importantForAccessibility="no-hide-descendants"            // Android hide
      style={[{ width, height, borderRadius: radius, backgroundColor: '#e0e0e0', opacity }, style]}
    />
  );
}

export default function RestaurantCardSkeleton() {
  return (
    <View style={styles.card}>
      <Skeleton width="100%" height={140} radius={12} />          {/* image area */}
      <Skeleton width="60%" height={18} style={styles.gap} />     {/* title */}
      <Skeleton width="40%" height={14} style={styles.gap} />     {/* subtitle */}
    </View>
  );
}

const styles = StyleSheet.create({
  card: { padding: 16 },
  gap: { marginTop: 10 },
});
```

## 💻 Code Example — Advanced

```jsx
import React, { useEffect, useState, useCallback } from 'react'; // React
import { View, Text, FlatList, Platform, StyleSheet, useWindowDimensions } from 'react-native';
import Animated, {
  useSharedValue, useAnimatedStyle, withRepeat, withTiming, interpolate, Easing, useReducedMotion,
} from 'react-native-reanimated';                               // Reanimated 3
import { LinearGradient } from 'expo-linear-gradient';          // npx expo install expo-linear-gradient

// A shimmer: a translucent gradient strip sliding across a grey block (UI thread, 60fps)
function Shimmer({ width, height, radius = 8 }) {
  const { width: screenW } = useWindowDimensions();
  const progress = useSharedValue(0);                           // 0 -> 1 loop
  const reduce = useReducedMotion();                            // accessibility

  useEffect(() => {
    if (reduce) return;                                         // no animation if user prefers
    progress.value = withRepeat(withTiming(1, { duration: 1200, easing: Easing.linear }), -1, false);
  }, [reduce]);

  const stripStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: interpolate(progress.value, [0, 1], [-screenW, screenW]) }], // slide
  }));

  return (
    <View style={[{ width, height, borderRadius: radius, backgroundColor: '#e3e3e3', overflow: 'hidden' }]}>
      <Animated.View style={[StyleSheet.absoluteFill, stripStyle]}>
        <LinearGradient
          colors={['transparent', 'rgba(255,255,255,0.6)', 'transparent']} // light band
          start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}                      // horizontal
          style={StyleSheet.absoluteFill}
        />
      </Animated.View>
    </View>
  );
}

function CardSkeleton() {
  return (
    <View style={styles.card} accessibilityElementsHidden importantForAccessibility="no-hide-descendants">
      <Shimmer width="100%" height={150} radius={12} />
      <View style={{ height: 10 }} />
      <Shimmer width="65%" height={18} />
      <View style={{ height: 8 }} />
      <Shimmer width="40%" height={14} />
    </View>
  );
}

// Fake API with delay + error simulation
const fetchRestaurants = () =>
  new Promise((resolve, reject) =>
    setTimeout(() => (Math.random() < 0.9 ? resolve([{ id: '1', name: 'Biryani Blues' }, { id: '2', name: 'Dosa Plaza' }]) : reject(new Error('Network error'))), 2000));

export default function Home() {
  const [data, setData] = useState(null);                       // null = not loaded yet
  const [error, setError] = useState(null);

  const load = useCallback(() => {
    setError(null); setData(null);                              // show skeleton again
    fetchRestaurants().then(setData).catch(setError);
  }, []);
  useEffect(load, [load]);

  if (error) return <View style={styles.center}><Text onPress={load}>Failed. Tap to retry</Text></View>;

  return (
    <FlatList
      data={data ?? [1, 2, 3, 4]}                               // 4 placeholders while loading
      keyExtractor={(item, i) => (data ? item.id : `sk-${i}`)}
      renderItem={({ item }) =>
        data ? <View style={styles.card}><Text style={styles.name}>{item.name}</Text></View> : <CardSkeleton />}
      contentContainerStyle={{ paddingTop: Platform.OS === 'ios' ? 56 : 16 }}
    />
  );
}

const styles = StyleSheet.create({
  card: { padding: 16 },
  name: { fontSize: 18, fontWeight: '700' },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Animation code | Same | Same |
| `overflow: hidden` + radius | Works | Works |
| Screen-reader hiding | `importantForAccessibility="no-hide-descendants"` | `accessibilityElementsHidden` |
| Many animated nodes | Can hurt low-end devices, share one value | Fine |
| Native shimmer (iOS only) | No | No built-in; libs only |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-linear-gradient react-native-reanimated
import { LinearGradient } from 'expo-linear-gradient';
```
CLI way:
```jsx
// npm i react-native-linear-gradient react-native-reanimated ; pod install ; rebuild
import LinearGradient from 'react-native-linear-gradient';   // default import, different package
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Skeleton shapes that don't match final layout, so content jumps.
✅ Correct: Use same widths/heights/margins as real components.

❌ Mistake 2: Each skeleton runs its own loop (20 loops).
✅ Correct: One shared value / one parent animation.

❌ Mistake 3: Using a skeleton for a short (<300ms) load, causing flicker.
✅ Correct: Show skeleton only after a small delay or for known slow screens.

❌ Mistake 4: Never showing error/empty state; skeleton spins forever.
✅ Correct: Handle error and retry like the example above.

---

## 🧠 Tricky Interview Question
Skeleton uses `Animated.loop` with `useNativeDriver: true` to animate `width` for a "growing" shimmer. What happens?

Answer: Error/warning: "Style property 'width' is not supported by native animated module". Native driver supports only non-layout props (transform, opacity). Animate `translateX` of a strip (as above) or use Reanimated.

---

## ⚫ Interview Questions + Answers
Q1: Skeleton vs spinner?
A1: Skeleton shows the content structure, reduces layout shift and improves perceived speed; spinner gives no layout hint. Spinners suit short/unknown, small actions.

Q2: How to build shimmer cheaply?
A2: A single gradient strip translated across a clipped container (transform only, native/UI thread).

Q3: Accessibility?
A3: Hide skeletons from screen readers, and announce loading state with `accessibilityLiveRegion`/`AccessibilityInfo.announceForAccessibility("Loading")`. Respect Reduce Motion.

Q4: Ready libraries?
A4: `moti/skeleton`, `react-native-skeleton-placeholder`, `react-native-reanimated-skeleton` (verify maintenance/compat before using).

Q5: How many placeholders to render?
A5: Enough to fill the viewport (e.g. 4-6), not hundreds.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- List/feeds/detail screens with network data
- Content layout is predictable

❌ Avoid when:
- Very fast loads or tiny actions (use inline spinner)
- Layout unknown (generic spinner is honest)

---

## 📊 Visual Diagram
```
 loading=true                    loading=false
 ┌───────────────┐              ┌───────────────┐
 │▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒│  ──data──►   │  [food image] │
 │▒▒▒▒▒▒         │              │  Biryani Blues│
 │▒▒▒▒           │              │  4.5★ 30 min  │
 └───────────────┘              └───────────────┘
   shimmer ─►─►─►  (light band sliding left to right)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| skeleton | placeholder shapes | placeholder आकृतियाँ |
| shimmer | moving light effect | चमकती रोशनी का प्रभाव |
| perceived performance | how fast it feels | कितना तेज़ महसूस होता है |
| layout shift | content jumping | content का उछलना |
| Reduce Motion | OS accessibility setting | animation कम करने की सेटिंग |

---

## ⚡ 3-Line Summary
English: Skeletons mimic the final layout while data loads.
Animate with pulse or a sliding gradient on transform/opacity.
Share one animation, handle errors, respect accessibility.

Hindi: Skeleton data load होते समय अंतिम layout की नकल करता है।
pulse या सरकते gradient (transform/opacity) से animate करो।
एक shared animation, error handling और accessibility का ध्यान रखो।

---

## ➡️ Next Topic
**141. Shared Element Transition** — एक screen से दूसरी में element का smooth transition।
