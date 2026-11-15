# 135. Gesture Handler Library (react-native-gesture-handler)
# हिंदी में: Gesture Handler Library — Touch Gestures की native library
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76, react-native-gesture-handler 2.x (check current docs — APIs change between SDKs). Gesture Handler 2 का नया API `Gesture.*` + `GestureDetector` है; पुराना `PanGestureHandler` component API अभी भी चलता है पर deprecated है।

---

## 🔵 Simple Definition (English)
`react-native-gesture-handler` (RNGH) recognizes touch gestures (tap, pan, pinch, rotation, long press, fling) **natively**, not in JS. It works with Reanimated so gesture callbacks run on the UI thread as worklets.

## 🔵 सरल परिभाषा (Hindi)
`react-native-gesture-handler` (RNGH) touch gestures (tap, pan, pinch, rotation, long press, fling) को **native** में पहचानता है, JS में नहीं। यह Reanimated के साथ काम करता है, इसलिए gesture callbacks UI thread पर worklet की तरह चलते हैं।

---

## 🔴 Problem it Solves
```
RN's built-in PanResponder / Touchable:
  - gestures go: native -> JS thread -> back to native => lag when JS is busy
  - hard to combine (swipe inside a scroll, pan + pinch together)
  - conflicts with ScrollView, nested touchables
RNGH:
  - native gesture recognizers (UIGestureRecognizer / Android touch system)
  - composable: Gesture.Simultaneous, Exclusive, Race
  - integrates with ScrollView, FlatList via waitFor / simultaneousWithExternalGesture
```

## 🔴 यह क्यों बना? (Hindi)
```
RN का built-in PanResponder / Touchable:
  - gesture: native -> JS thread -> वापस native => JS busy हो तो lag
  - जोड़ना मुश्किल (scroll के अंदर swipe, pan + pinch साथ)
  - ScrollView, nested touchables से टकराव
RNGH:
  - native gesture recognizers (UIGestureRecognizer / Android touch system)
  - composable: Gesture.Simultaneous, Exclusive, Race
  - ScrollView, FlatList के साथ waitFor / simultaneousWithExternalGesture से जुड़ता है
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Install: npx expo install react-native-gesture-handler
Step 2 → Wrap the app root: <GestureHandlerRootView style={{ flex: 1 }}>
Step 3 → Create a gesture: const tap = Gesture.Tap().onEnd(() => {...})
Step 4 → Attach: <GestureDetector gesture={tap}><Animated.View/></GestureDetector>
Step 5 → Native recognizer tracks fingers; callbacks: onBegin, onStart, onUpdate, onEnd, onFinalize
Step 6 → Callbacks are worklets (with Reanimated) => update shared values at 60fps
Step 7 → Compose: Gesture.Simultaneous(pan, pinch), Gesture.Exclusive(doubleTap, singleTap)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Install: npx expo install react-native-gesture-handler
Step 2 → App root लपेटो: <GestureHandlerRootView style={{ flex: 1 }}>
Step 3 → Gesture बनाओ: const tap = Gesture.Tap().onEnd(() => {...})
Step 4 → जोड़ो: <GestureDetector gesture={tap}><Animated.View/></GestureDetector>
Step 5 → Native recognizer उंगलियाँ track करता है; callbacks: onBegin, onStart, onUpdate, onEnd, onFinalize
Step 6 → Reanimated के साथ callbacks worklets हैं => shared values 60fps पर update
Step 7 → Compose: Gesture.Simultaneous(pan, pinch), Gesture.Exclusive(doubleTap, singleTap)
```

---

## 🟡 Real World Example
**Instagram & WhatsApp:** double-tap a photo for a heart (Tap with `numberOfTaps(2)`), long-press a chat for the context menu (LongPress), swipe a WhatsApp message right to reply (Pan), pinch-zoom images (Pinch). **Swiggy** map screen: pan and pinch at the same time.

## 🟡 Real Example Hindi mein
**Instagram और WhatsApp:** photo पर double-tap से heart (Tap, `numberOfTaps(2)`), chat पर long-press से menu (LongPress), WhatsApp message को दाएँ swipe करके reply (Pan), images pinch-zoom (Pinch)। **Swiggy** map screen: pan और pinch एक साथ।

---

## 💻 Code Example — Basic

```jsx
import React from 'react';                                      // React
import { Text, StyleSheet } from 'react-native';                // core
import { Gesture, GestureDetector, GestureHandlerRootView } from 'react-native-gesture-handler'; // RNGH 2
import Animated, { useSharedValue, useAnimatedStyle, withSpring } from 'react-native-reanimated'; // Reanimated

export default function DoubleTapHeart() {
  const scale = useSharedValue(0);                               // heart scale, hidden at 0

  const doubleTap = Gesture.Tap()                                // create tap gesture
    .numberOfTaps(2)                                             // needs two taps
    .onEnd((_e, success) => {                                    // worklet on UI thread
      if (success) {                                             // only if recognized (not cancelled)
        scale.value = withSpring(1, {}, () => {                  // pop in
          scale.value = withSpring(0);                           // then disappear
        });
      }
    });

  const heartStyle = useAnimatedStyle(() => ({                   // style reading shared value
    transform: [{ scale: scale.value }],
    opacity: scale.value,
  }));

  return (
    <GestureHandlerRootView style={styles.root}>                {/* REQUIRED at app root */}
      <GestureDetector gesture={doubleTap}>                      {/* attaches gesture to child */}
        <Animated.View style={styles.photo}>
          <Text>Double tap me</Text>
          <Animated.Text style={[styles.heart, heartStyle]}>❤️</Animated.Text>
        </Animated.View>
      </GestureDetector>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  photo: { width: 300, height: 300, backgroundColor: '#ddd', alignItems: 'center', justifyContent: 'center' },
  heart: { position: 'absolute', fontSize: 80 },
});
```

## 💻 Code Example — Advanced

```jsx
import React from 'react';                                      // React
import { Text, Alert, Platform, StyleSheet } from 'react-native'; // core
import { Gesture, GestureDetector, GestureHandlerRootView } from 'react-native-gesture-handler';
import Animated, { useSharedValue, useAnimatedStyle, withSpring, runOnJS } from 'react-native-reanimated';

// Compose gestures: single tap vs double tap (Exclusive), plus long press (Race)
export default function PostCard() {
  const heart = useSharedValue(0);                               // heart animation
  const bg = useSharedValue(0);                                  // press highlight 0/1

  const onLike = () => console.log('liked');                     // JS callbacks (not worklets)
  const onOpen = () => console.log('open post');
  const onMenu = () => Alert.alert('Post options', 'Save / Report');

  const doubleTap = Gesture.Tap().numberOfTaps(2).maxDuration(250)  // fast double tap
    .onEnd((_e, ok) => {
      if (!ok) return;                                           // cancelled
      heart.value = withSpring(1, {}, () => { heart.value = withSpring(0); });
      runOnJS(onLike)();                                         // JS fn from worklet
    });

  const singleTap = Gesture.Tap().numberOfTaps(1)
    .onBegin(() => { bg.value = withSpring(1); })                // highlight on touch down
    .onFinalize(() => { bg.value = withSpring(0); })             // always un-highlight
    .onEnd((_e, ok) => { if (ok) runOnJS(onOpen)(); });

  const longPress = Gesture.LongPress().minDuration(500)         // 0.5 second hold
    .onStart(() => { runOnJS(onMenu)(); });

  // Exclusive: doubleTap gets priority, singleTap waits until doubleTap fails
  const taps = Gesture.Exclusive(doubleTap, singleTap);
  // Race: first one to activate wins, other is cancelled
  const composed = Gesture.Race(longPress, taps);

  const heartStyle = useAnimatedStyle(() => ({ transform: [{ scale: heart.value }], opacity: heart.value }));
  const cardStyle = useAnimatedStyle(() => ({ opacity: 1 - bg.value * 0.2 }));

  return (
    <GestureHandlerRootView style={styles.root}>
      <GestureDetector gesture={composed}>
        <Animated.View style={[styles.card, cardStyle]}>
          <Text style={styles.text}>Biryani photo (tap / double tap / long press)</Text>
          <Animated.Text style={[styles.heart, heartStyle]}>❤️</Animated.Text>
        </Animated.View>
      </GestureDetector>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, justifyContent: 'center', padding: 16 },
  card: {
    height: 260, borderRadius: 16, backgroundColor: '#fff', alignItems: 'center', justifyContent: 'center',
    ...Platform.select({ ios: { shadowOpacity: 0.2, shadowRadius: 8 }, android: { elevation: 4 } }),
  },
  text: { fontSize: 16 },
  heart: { position: 'absolute', fontSize: 90 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Root view | `GestureHandlerRootView` required (inside Modal also needs its own root) | Same API, more forgiving |
| Pan activation | Touch slop (~8dp) before start | Starts almost immediately |
| Back gesture | System back swipe may conflict with edge pans | Edge-swipe back may conflict with left-edge pans |
| Hover (mouse/stylus) | Supported newer versions | iPad pointer supported |
| Testing | Real device or emulator | Simulator OK |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install react-native-gesture-handler  (included in Expo Go and default templates)
// expo-router / react-navigation already wrap the app in GestureHandlerRootView
import { GestureHandlerRootView } from 'react-native-gesture-handler';
```
CLI way:
```jsx
// npm i react-native-gesture-handler ; cd ios && pod install ; rebuild
// index.js: first line  import 'react-native-gesture-handler';
// Android older versions: MainActivity createRootView wrapper (RN 0.7x template does this)
import { GestureHandlerRootView } from 'react-native-gesture-handler';
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No `GestureHandlerRootView` => gestures silently do nothing on Android.
✅ Correct: Wrap the app (and each Modal's content) in it.

❌ Mistake 2: Using non-worklet functions inside gesture callbacks.
✅ Correct: `runOnJS(fn)(args)` or mark function `'worklet'`.

❌ Mistake 3: Mixing old `PanGestureHandler` and new `GestureDetector` for same view.
✅ Correct: Use one API consistently.

❌ Mistake 4: Putting `GestureDetector` around a plain `View` and animating it with styles (needs Animated.View when style is animated).
✅ Correct: Child must be a native view/`Animated.View`.

---

## 🧠 Tricky Interview Question
```jsx
const single = Gesture.Tap().onEnd(() => console.log('single'));
const double = Gesture.Tap().numberOfTaps(2).onEnd(() => console.log('double'));
const g = Gesture.Simultaneous(single, double);
```
User double taps. What logs?

Answer: Both recognizers can be active together, so `single` logs on the first tap and `single` + `double` log again on the second (it is not exclusive). To make single wait for the double to fail, use `Gesture.Exclusive(double, single)`, which logs only `double`.

---

## ⚫ Interview Questions + Answers
Q1: Why not PanResponder?
A1: PanResponder runs in JS; RNGH recognizes natively and works with Reanimated worklets, so no round-trip lag.

Q2: Gesture state lifecycle?
A2: UNDETERMINED -> BEGAN -> ACTIVE -> END (or FAILED/CANCELLED). Callbacks: onBegin, onStart, onUpdate, onEnd, onFinalize.

Q3: Simultaneous vs Exclusive vs Race?
A3: Simultaneous: all can be active (pan + pinch). Exclusive: priority order, later waits for earlier to fail. Race: first to activate wins.

Q4: How to use pan inside a ScrollView?
A4: `Gesture.Pan().activeOffsetX([-10, 10])` + `failOffsetY([-5, 5])`, or `.simultaneousWithExternalGesture(scrollGesture)`.

Q5: Is RNGH used by React Navigation?
A5: Yes. Stack/drawer swipe gestures rely on it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Drag, pinch, swipe, long press, complex gesture composition
- Gesture should drive Reanimated values

❌ Avoid when:
- Simple button press (Pressable is enough)
- Expo Go with a version mismatch (use dev build)

---

## 📊 Visual Diagram
```
 Finger ─► Native recognizer ─► callback worklet (UI thread) ─► sharedValue
                                                              │
 JS thread (idle, not needed) ◄── runOnJS only when needed    ▼
                                                    useAnimatedStyle ─► view
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Gesture.Pan | drag | खींचना |
| Gesture.Pinch | two-finger zoom | दो उंगलियों से zoom |
| GestureDetector | attaches gesture to view | view पर gesture जोड़ना |
| Simultaneous | run together | एक साथ |
| Exclusive | priority order | प्राथमिकता क्रम |
| Race | first wins | जो पहले हो |

---

## ⚡ 3-Line Summary
English: RNGH recognizes gestures natively and runs callbacks on the UI thread.
Wrap root in GestureHandlerRootView, attach with GestureDetector.
Compose with Simultaneous, Exclusive, Race.

Hindi: RNGH gestures को native में पहचानता है और callbacks UI thread पर चलाता है।
Root को GestureHandlerRootView में लपेटो, GestureDetector से जोड़ो।
Simultaneous, Exclusive, Race से compose करो।

---

## ➡️ Next Topic
**136. Pan Gesture (Drag)** — view को उंगली से खींचना।
