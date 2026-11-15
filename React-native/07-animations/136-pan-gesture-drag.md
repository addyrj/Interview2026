# 136. Pan Gesture (Drag)
# हिंदी में: Pan Gesture — उंगली से View को खींचना
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76, react-native-gesture-handler 2.x + react-native-reanimated 3.x (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
`Gesture.Pan()` detects a finger dragging across the screen and gives `translationX/Y`, `velocityX/Y` and absolute positions. Used to build draggable cards, sliders, bottom sheets and swipe actions.

## 🔵 सरल परिभाषा (Hindi)
`Gesture.Pan()` स्क्रीन पर उंगली के खींचने (drag) को पहचानता है और `translationX/Y`, `velocityX/Y` और absolute positions देता है। इससे draggable cards, sliders, bottom sheets और swipe actions बनते हैं।

---

## 🔴 Problem it Solves
```
Need: view follows finger exactly, then settles (snap back / fling) with momentum.
PanResponder: JS-thread, laggy, verbose.
Pan gesture + Reanimated: runs on UI thread, translation is delta since gesture start,
so we keep a "start" value to make dragging resume correctly from where it was.
```

## 🔴 यह क्यों बना? (Hindi)
```
ज़रूरत: view उंगली के साथ चले, फिर momentum से रुके (snap back / fling)।
PanResponder: JS thread, laggy, लंबा code।
Pan gesture + Reanimated: UI thread, translation gesture शुरू होने से अब तक का delta है,
इसलिए "start" value रखते हैं ताकि अगली बार drag वहीं से शुरू हो जहाँ पिछली रुकी थी।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → x, y = useSharedValue(0); startX, startY = useSharedValue(0)
Step 2 → onBegin: startX = x, startY = y  (remember where the view was)
Step 3 → onUpdate(e): x = startX + e.translationX; y = startY + e.translationY
Step 4 → onEnd(e): decide: snap back withSpring(0) OR keep momentum withDecay({velocity})
Step 5 → useAnimatedStyle maps x,y to transform translateX/Y
Step 6 → Clamp inside screen bounds so the view can't be lost off-screen
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → x, y = useSharedValue(0); startX, startY = useSharedValue(0)
Step 2 → onBegin: startX = x, startY = y  (view कहाँ था याद रखो)
Step 3 → onUpdate(e): x = startX + e.translationX; y = startY + e.translationY
Step 4 → onEnd(e): तय करो: snap back withSpring(0) या momentum withDecay({velocity})
Step 5 → useAnimatedStyle x,y को transform translateX/Y में बदलता है
Step 6 → Screen की सीमा में clamp करो ताकि view screen से बाहर न खो जाए
```

---

## 🟡 Real World Example
**Swiggy floating cart button / Zomato bubble:** a draggable circular shortcut that follows your finger and snaps to the nearest screen edge when released. Same idea as WhatsApp's floating video-call window.

## 🟡 Real Example Hindi mein
**Swiggy floating cart button / Zomato bubble:** गोल shortcut जो उंगली के साथ चलता है और छोड़ने पर सबसे पास की screen edge पर चिपक जाता है। WhatsApp की floating video-call window भी ऐसी ही है।

---

## 💻 Code Example — Basic

```jsx
import React from 'react';                                      // React
import { StyleSheet } from 'react-native';                      // core
import { Gesture, GestureDetector, GestureHandlerRootView } from 'react-native-gesture-handler'; // gestures
import Animated, { useSharedValue, useAnimatedStyle, withSpring } from 'react-native-reanimated'; // animation

export default function DragBasic() {
  const x = useSharedValue(0);                                   // current X offset
  const y = useSharedValue(0);                                   // current Y offset
  const startX = useSharedValue(0);                              // X when drag began
  const startY = useSharedValue(0);                              // Y when drag began

  const pan = Gesture.Pan()                                      // create pan gesture
    .onBegin(() => {                                             // finger down
      startX.value = x.value;                                    // remember X
      startY.value = y.value;                                    // remember Y
    })
    .onUpdate((e) => {                                           // finger moving
      x.value = startX.value + e.translationX;                   // follow finger X
      y.value = startY.value + e.translationY;                   // follow finger Y
    })
    .onEnd(() => {                                               // finger up
      x.value = withSpring(0);                                   // snap back home X
      y.value = withSpring(0);                                   // snap back home Y
    });

  const style = useAnimatedStyle(() => ({                        // apply offsets
    transform: [{ translateX: x.value }, { translateY: y.value }],
  }));

  return (
    <GestureHandlerRootView style={styles.root}>
      <GestureDetector gesture={pan}>
        <Animated.View style={[styles.circle, style]} />
      </GestureDetector>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  circle: { width: 90, height: 90, borderRadius: 45, backgroundColor: '#fc8019' }, // Swiggy orange
});
```

## 💻 Code Example — Advanced

```jsx
import React from 'react';                                      // React
import { Text, useWindowDimensions, Platform, StyleSheet } from 'react-native'; // core
import { Gesture, GestureDetector, GestureHandlerRootView } from 'react-native-gesture-handler';
import Animated, { useSharedValue, useAnimatedStyle, withSpring, withDecay, clamp } from 'react-native-reanimated';
import { useSafeAreaInsets, SafeAreaProvider } from 'react-native-safe-area-context'; // safe areas

const SIZE = 64;                                                // bubble size

function Bubble() {
  const { width, height } = useWindowDimensions();              // screen size
  const insets = useSafeAreaInsets();                           // notch / home indicator
  const minX = 8, maxX = width - SIZE - 8;                      // horizontal bounds
  const minY = insets.top + 8, maxY = height - SIZE - insets.bottom - 8; // vertical bounds

  const x = useSharedValue(maxX);                               // start at right edge
  const y = useSharedValue(height / 2);                         // start in middle
  const ctx = useSharedValue({ x: 0, y: 0 });                   // remembers drag start
  const dragging = useSharedValue(false);                       // visual state

  const pan = Gesture.Pan()
    .minDistance(4)                                             // small slop to still allow tap
    .onBegin(() => {
      ctx.value = { x: x.value, y: y.value };                   // store start
      dragging.value = true;                                    // lift effect
    })
    .onUpdate((e) => {
      x.value = clamp(ctx.value.x + e.translationX, minX, maxX); // clamp inside screen X
      y.value = clamp(ctx.value.y + e.translationY, minY, maxY); // clamp inside screen Y
    })
    .onEnd((e) => {
      // Momentum on Y, bounded; snap X to nearest edge using the spring
      y.value = withDecay({ velocity: e.velocityY, clamp: [minY, maxY] }); // inertia
      const snapRight = x.value + SIZE / 2 > width / 2;         // closer to right?
      x.value = withSpring(snapRight ? maxX : minX, { velocity: e.velocityX, damping: 18 }); // snap
    })
    .onFinalize(() => { dragging.value = false; });             // always reset

  const style = useAnimatedStyle(() => ({
    transform: [
      { translateX: x.value },
      { translateY: y.value },
      { scale: withSpring(dragging.value ? 1.15 : 1) },         // lift while dragging
    ],
  }));

  return (
    <GestureDetector gesture={pan}>
      <Animated.View style={[styles.bubble, style]}>
        <Text style={styles.cart}>🛒</Text>
      </Animated.View>
    </GestureDetector>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <GestureHandlerRootView style={{ flex: 1 }}>
        <Bubble />
      </GestureHandlerRootView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  bubble: {
    position: 'absolute', top: 0, left: 0,                      // positioned using translate only
    width: SIZE, height: SIZE, borderRadius: SIZE / 2, backgroundColor: '#fc8019',
    alignItems: 'center', justifyContent: 'center',
    ...Platform.select({ ios: { shadowOpacity: 0.3, shadowRadius: 6, shadowOffset: { width: 0, height: 3 } }, android: { elevation: 8 } }),
  },
  cart: { fontSize: 28 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Pan API | Same | Same |
| Touch slop | Pan activates after ~8dp move | Activates earlier |
| Edge area | Bottom gesture bar / back gesture can steal edge drags | Home indicator and left-edge back swipe |
| Safe area | `insets` smaller | Notch / Dynamic Island, home indicator |
| Shadow | `elevation` | `shadow*` |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install react-native-gesture-handler react-native-reanimated react-native-safe-area-context
// Works in Expo Go; custom native versions need a dev build.
```
CLI way:
```jsx
// npm i react-native-gesture-handler react-native-reanimated react-native-safe-area-context
// cd ios && pod install ; babel plugin: react-native-reanimated/plugin (last) ; rebuild
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `x.value = e.translationX` only (view jumps back to 0 on 2nd drag).
✅ Correct: `x.value = start + e.translationX`, with `start` saved in `onBegin`/`onStart`.

❌ Mistake 2: Using `useState` for x/y (re-render each frame).
✅ Correct: Shared values.

❌ Mistake 3: Forgetting `GestureHandlerRootView`.
✅ Correct: Wrap root.

❌ Mistake 4: No bounds, so the view is lost off-screen.
✅ Correct: `clamp` and `withDecay({ clamp: [min, max] })`.

---

## 🧠 Tricky Interview Question
A draggable box uses `.onUpdate(e => { x.value = e.translationX })`. The user drags 100px right, lifts, and drags again 20px right. Where is the box?

Answer: At **20px**, not 120. `translationX` resets to 0 at every gesture start, so the box jumps back to near origin at the start of the second drag. Fix by storing `start = x.value` in `onBegin` and setting `x.value = start + translationX`.

---

## ⚫ Interview Questions + Answers
Q1: translationX vs absoluteX?
A1: `translationX` = change since gesture started (relative). `absoluteX` = finger X in window coordinates.

Q2: What is withDecay?
A2: Animation that continues with initial velocity and slows by friction (like scroll inertia). Options: `velocity`, `deceleration`, `clamp`.

Q3: How to make drag only horizontal?
A3: `.activeOffsetX([-10, 10]).failOffsetY([-10, 10])` so vertical movement fails the gesture, letting ScrollView take over.

Q4: How to pass event data to JS?
A4: `runOnJS(fn)(e.translationX)`.

Q5: Pan inside FlatList?
A5: Use activeOffset/failOffset or `simultaneousWithExternalGesture`; avoid blocking list scroll.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Draggable bubbles, sliders, sheets, swipe cards

❌ Avoid when:
- Just detecting a tap (use Gesture.Tap / Pressable)
- Simple list scrolling (use ScrollView)

---

## 📊 Visual Diagram
```
 onBegin   : start = x
 onUpdate  : x = start + translationX    ──► view follows finger
 onEnd     : snap (spring) / fling (decay)
 onFinalize: cleanup

   start ●────────────● finger
         |<-translation->|
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| translation | delta since gesture start | gesture शुरू से बदलाव |
| velocity | speed (px/sec) | गति |
| withDecay | momentum animation | momentum वाली animation |
| clamp | limit within range | सीमा में रखना |
| activeOffset | slop before activation | activate होने की दूरी |

---

## ⚡ 3-Line Summary
English: Pan gives translation relative to gesture start.
Save the start position in onBegin and add translation.
Finish with withSpring (snap) or withDecay (fling).

Hindi: Pan gesture शुरू होने से अब तक का translation देता है।
onBegin में start position सेव करो और translation जोड़ो।
अंत में withSpring (snap) या withDecay (fling) लगाओ।

---

## ➡️ Next Topic
**137. Pinch + Zoom Gesture** — दो उंगलियों से scale।
