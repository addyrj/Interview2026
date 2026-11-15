# 134. withSequence + withDelay
# हिंदी में: withSequence और withDelay — Reanimated में क्रम और देरी
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76, react-native-reanimated 3.x (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
`withSequence(a, b, c)` runs animations for one shared value **one after another**. `withDelay(ms, animation)` **waits** before starting. `withRepeat(animation, n, reverse)` repeats. Combined, they build choreography on the UI thread. (Note: in Reanimated a single value is sequenced; to run different values together, just assign each.)

## 🔵 सरल परिभाषा (Hindi)
`withSequence(a, b, c)` एक shared value की animations को **एक के बाद एक** चलाता है। `withDelay(ms, animation)` शुरू होने से पहले **इंतज़ार** करता है। `withRepeat(animation, n, reverse)` दोहराता है। मिलकर ये UI thread पर choreography बनाते हैं। (ध्यान: Reanimated में एक value sequence होती है; अलग values को एक साथ चलाने के लिए बस सबको assign कर दो।)

---

## 🔴 Problem it Solves
```
Animated API: Animated.sequence / delay / stagger objects, callbacks, JS-thread timing.
Reanimated: setTimeout chains would run on JS thread (can jank, hard to cancel).
Need declarative, UI-thread timeline:
   shake: 0 -> -10 -> 10 -> -10 -> 0
   staggered list: item i waits i*100ms
```

## 🔴 यह क्यों बना? (Hindi)
```
Animated API: Animated.sequence / delay / stagger objects, callbacks, JS thread timing।
Reanimated में setTimeout chains JS thread पर चलेंगी (jank, cancel मुश्किल)।
ज़रूरत: declarative, UI-thread timeline:
   shake: 0 -> -10 -> 10 -> -10 -> 0
   staggered list: item i, i*100ms इंतज़ार करे
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → sv.value = withSequence(withTiming(-10), withTiming(10), withTiming(0))
Step 2 → Reanimated plays child 1; when it finishes, starts child 2 from its end value...
Step 3 → withDelay(300, withSpring(1)) holds the current value for 300ms, then springs
Step 4 → withRepeat(withSequence(...), -1, true): infinite, reverse=true plays back and forth
Step 5 → Staggering: index * 100 as the delay for each list item's own shared value
Step 6 → Final callback fires on UI thread when the whole sequence finishes
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → sv.value = withSequence(withTiming(-10), withTiming(10), withTiming(0))
Step 2 → पहली animation चलती है; खत्म होने पर दूसरी उसकी end value से शुरू...
Step 3 → withDelay(300, withSpring(1)) 300ms मौजूदा value थामे रखता है, फिर spring
Step 4 → withRepeat(withSequence(...), -1, true): अनंत, reverse=true आगे-पीछे चलाता है
Step 5 → Staggering: हर list item की अपनी shared value में index * 100 की delay
Step 6 → पूरा sequence खत्म होने पर final callback UI thread पर चलता है
```

---

## 🟡 Real World Example
**Paytm wrong-PIN shake & Swiggy offers list:** entering a wrong UPI PIN shakes the dots left-right-left (`withSequence`). The Swiggy "Offers for you" cards slide in one by one (`withDelay(index * 100, ...)`). The Zomato Gold crown "pulses" forever (`withRepeat`).

## 🟡 Real Example Hindi mein
**Paytm गलत PIN shake और Swiggy offers list:** गलत UPI PIN डालने पर dots बाएँ-दाएँ-बाएँ हिलते हैं (`withSequence`)। Swiggy "Offers for you" cards एक-एक करके आते हैं (`withDelay(index * 100, ...)`)। Zomato Gold का crown हमेशा धड़कता है (`withRepeat`)।

---

## 💻 Code Example — Basic

```jsx
import React from 'react';                                      // React
import { View, Text, Pressable, StyleSheet } from 'react-native'; // core
import Animated, {
  useSharedValue, useAnimatedStyle, withSequence, withTiming, withDelay, withRepeat,
} from 'react-native-reanimated';                               // Reanimated 3

export default function ShakeBasic() {
  const x = useSharedValue(0);                                   // horizontal offset
  const scale = useSharedValue(1);                               // pulse scale

  const shakeStyle = useAnimatedStyle(() => ({ transform: [{ translateX: x.value }] })); // shake
  const pulseStyle = useAnimatedStyle(() => ({ transform: [{ scale: scale.value }] }));  // pulse

  const shake = () => {
    x.value = withSequence(                                      // 4 quick moves then back to 0
      withTiming(-12, { duration: 50 }),                         // left
      withTiming(12, { duration: 100 }),                         // right (twice the distance)
      withTiming(-12, { duration: 100 }),                        // left again
      withTiming(0, { duration: 50 }),                           // center
    );
  };

  const startPulse = () => {
    scale.value = withDelay(                                     // wait 300ms first
      300,
      withRepeat(                                                // then repeat
        withSequence(withTiming(1.2, { duration: 400 }), withTiming(1, { duration: 400 })), // grow, shrink
        -1,                                                      // infinite
        false,                                                   // no reverse (sequence already returns)
      ),
    );
  };

  return (
    <View style={styles.container}>
      <Animated.View style={[styles.box, shakeStyle]}><Text style={{ color: '#fff' }}>Wrong PIN</Text></Animated.View>
      <Pressable style={styles.btn} onPress={shake}><Text style={{ color: '#fff' }}>Shake</Text></Pressable>
      <Animated.View style={[styles.dot, pulseStyle]} />
      <Pressable style={styles.btn} onPress={startPulse}><Text style={{ color: '#fff' }}>Pulse</Text></Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  box: { padding: 20, backgroundColor: '#d32f2f', borderRadius: 8 },
  dot: { width: 40, height: 40, borderRadius: 20, backgroundColor: '#fc8019', marginTop: 24 },
  btn: { marginTop: 12, padding: 10, backgroundColor: '#222', borderRadius: 8 },
});
```

## 💻 Code Example — Advanced

```jsx
import React, { useEffect } from 'react';                       // React
import { FlatList, Text, Vibration, Platform, StyleSheet, Pressable } from 'react-native'; // core
import Animated, {
  useSharedValue, useAnimatedStyle, withDelay, withSpring, withTiming, withSequence, runOnJS, Easing,
} from 'react-native-reanimated';                               // Reanimated

const OFFERS = ['50% off', 'Free delivery', '₹100 cashback', 'Gold member deal']; // sample data

// One card: its own shared values, entry delay = index * 100
function OfferCard({ text, index }) {
  const y = useSharedValue(40);                                  // slide from below
  const opacity = useSharedValue(0);                             // fade in

  useEffect(() => {
    y.value = withDelay(index * 100, withSpring(0, { damping: 14 }));      // staggered spring
    opacity.value = withDelay(index * 100, withTiming(1, { duration: 300, easing: Easing.out(Easing.quad) }));
  }, []);                                                        // once on mount

  const style = useAnimatedStyle(() => ({
    opacity: opacity.value,
    transform: [{ translateY: y.value }],
  }));
  return <Animated.View style={[styles.card, style]}><Text style={styles.cardText}>{text}</Text></Animated.View>;
}

// PIN dots with error shake + haptic vibrate on JS side after shake ends
export function PinDots({ error, onShakeEnd }) {
  const x = useSharedValue(0);

  useEffect(() => {
    if (!error) return;                                          // only when error becomes true
    if (Platform.OS === 'android') Vibration.vibrate(80);        // android: short vibration (iOS ignores duration)
    else Vibration.vibrate();                                    // iOS: fixed short vibrate
    x.value = withSequence(
      withTiming(-10, { duration: 50 }),
      withTiming(10, { duration: 100 }),
      withTiming(-10, { duration: 100 }),
      withTiming(0, { duration: 50 }, (finished) => {            // last step with callback
        if (finished && onShakeEnd) runOnJS(onShakeEnd)();       // tell JS the shake is done
      }),
    );
  }, [error]);

  const style = useAnimatedStyle(() => ({ transform: [{ translateX: x.value }] }));
  return <Animated.Text style={[styles.pin, style]}>● ● ● ●</Animated.Text>;
}

export default function Offers() {
  return (
    <FlatList
      data={OFFERS}
      keyExtractor={(t) => t}
      renderItem={({ item, index }) => <OfferCard text={item} index={index} />} // each card staggered
      contentContainerStyle={{ padding: 16 }}
    />
  );
}

const styles = StyleSheet.create({
  card: { padding: 20, marginBottom: 12, backgroundColor: '#fff3e6', borderRadius: 12 },
  cardText: { fontSize: 18, color: '#fc8019' },
  pin: { fontSize: 32, letterSpacing: 8, textAlign: 'center' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| withSequence/withDelay | Same | Same |
| Vibration | `Vibration.vibrate(ms)` honors duration; needs VIBRATE permission (in manifest by default in RN) | Duration ignored, fixed short buzz |
| Haptics (better) | `expo-haptics` works | `expo-haptics` works (Taptic Engine) |
| Many simultaneous delayed items | OK | OK |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install react-native-reanimated expo-haptics
import * as Haptics from 'expo-haptics';
Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
```
CLI way:
```jsx
// npm i react-native-reanimated ; babel plugin ; pod install ; rebuild
// For haptics use react-native-haptic-feedback or core Vibration API
import { Vibration } from 'react-native';
Vibration.vibrate(80);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `withSequence` to animate DIFFERENT shared values.
✅ Correct: It sequences one value only. For two values assign both separately (they run in parallel), use `withDelay` to offset.

❌ Mistake 2: `withRepeat(anim, 0)` thinking it is infinite.
✅ Correct: `-1` (or `Infinity`) is infinite; `0` means no repeat.

❌ Mistake 3: Forgetting to cancel infinite repeat on unmount.
✅ Correct: `useEffect(() => () => cancelAnimation(sv), [])`.

❌ Mistake 4: Delay in `setTimeout` for stagger.
✅ Correct: `withDelay(index * 100, ...)` stays on UI thread.

---

## 🧠 Tricky Interview Question
```jsx
x.value = withRepeat(withTiming(100, { duration: 500 }), 3, true);
```
Where does x end, and how long does it take?

Answer: `numberOfReps = 3` with `reverse = true`: 0 -> 100 -> 0 -> 100 (3 legs), so it ends at **100**, total **1500 ms**. With an even count (e.g. 4) it would end back at 0.

---

## ⚫ Interview Questions + Answers
Q1: What does withDelay do?
A1: Delays the start of the wrapped animation; value holds until then.

Q2: How to loop forever?
A2: `withRepeat(anim, -1, reverse)`.

Q3: How is it different from Animated.sequence?
A3: Reanimated version works per shared value, declaratively, fully on UI thread. Animated.sequence composes animation objects for separate values on core Animated.

Q4: How to stagger list items?
A4: Each item `withDelay(index * ms, ...)`. For layout enter/exit, `entering={FadeInDown.delay(index*100)}` layout animations.

Q5: How to stop?
A5: `cancelAnimation(sv)`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Shake, pulse, wobble, entry stagger
- Repeating loaders

❌ Avoid when:
- Simple enter/exit (layout animations `FadeIn` are shorter)
- Long infinite loops on many items (battery cost)

---

## 📊 Visual Diagram
```
withSequence(T1, T2, T3)    ┃T1┃T2┃T3┃
withDelay(300, T)           ┃....300....┃  T  ┃
withRepeat(S, 3, true)      ┃S→┃←S┃S→┃
Stagger i=0,1,2:  card0 ┃ T ┃
                  card1  ┃.100┃ T ┃
                  card2   ┃..200..┃ T ┃
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| sequence | steps in order | क्रम से steps |
| delay | wait before start | शुरू से पहले इंतज़ार |
| repeat | loop animation | दोहराना |
| stagger | offset starts | क्रमशः देरी से शुरू |
| reverse | play backward on alternate loops | उल्टा चलाना |

---

## ⚡ 3-Line Summary
English: withSequence chains steps on one value.
withDelay waits, withRepeat loops (-1 = infinite).
All run on the UI thread, cancel with cancelAnimation.

Hindi: withSequence एक value पर steps जोड़ता है।
withDelay इंतज़ार, withRepeat दोहराव (-1 = अनंत)।
सब UI thread पर चलते हैं, रोकने के लिए cancelAnimation।

---

## ➡️ Next Topic
**135. Gesture Handler Library** — touch gestures (drag, pinch, swipe) जो इन animations को चलाते हैं।
