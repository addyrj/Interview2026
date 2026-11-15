# 137. Pinch + Zoom Gesture
# हिंदी में: Pinch और Zoom Gesture — दो उंगलियों से बड़ा/छोटा करना
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76, react-native-gesture-handler 2.x + react-native-reanimated 3.x (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
`Gesture.Pinch()` detects two fingers moving closer/farther. It gives `scale` (relative to gesture start, starts at 1) and `focalX/focalY` (centre between fingers). Combined with `Gesture.Pan()` via `Gesture.Simultaneous`, it makes a pinch-to-zoom image viewer.

## 🔵 सरल परिभाषा (Hindi)
`Gesture.Pinch()` दो उंगलियों के पास/दूर जाने को पहचानता है। यह `scale` (gesture शुरू से relative, 1 से शुरू) और `focalX/focalY` (उंगलियों का केंद्र) देता है। `Gesture.Simultaneous` से `Gesture.Pan()` के साथ जोड़ने पर pinch-to-zoom image viewer बनता है।

---

## 🔴 Problem it Solves
```
Product images, maps, documents need zoom. 
Without native pinch: you must track two touches manually (math, lag).
Pitfall: event.scale restarts at 1 for each pinch => must multiply with saved scale.
Also: zoom around the fingers (focal point), not the image centre, for natural feel.
```

## 🔴 यह क्यों बना? (Hindi)
```
Product images, maps, documents में zoom चाहिए।
Native pinch के बिना: दो touches हाथ से track करने पड़ते (math, lag)।
समस्या: event.scale हर pinch में 1 से शुरू होता है => पुराने saved scale से गुणा करना होगा।
साथ ही: image के केंद्र की बजाय उंगलियों के focal point पर zoom हो तो natural लगता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → scale = useSharedValue(1); savedScale = useSharedValue(1)
Step 2 → Pinch.onUpdate(e): scale = clamp(savedScale * e.scale, 1, 5)
Step 3 → Pinch.onEnd: savedScale = scale (save for next pinch)
Step 4 → Pan (for moving the zoomed image): translateX/Y with saved start values
Step 5 → Gesture.Simultaneous(pinch, pan) so both work together
Step 6 → Double-tap: toggle between 1x and 2x (withTiming)
Step 7 → If scale < 1 on end, spring back to 1 and reset pan to 0
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → scale = useSharedValue(1); savedScale = useSharedValue(1)
Step 2 → Pinch.onUpdate(e): scale = clamp(savedScale * e.scale, 1, 5)
Step 3 → Pinch.onEnd: savedScale = scale (अगली pinch के लिए सेव)
Step 4 → Pan (zoom की हुई image खिसकाने के लिए): translateX/Y, start values के साथ
Step 5 → Gesture.Simultaneous(pinch, pan) ताकि दोनों साथ चलें
Step 6 → Double-tap: 1x और 2x के बीच toggle (withTiming)
Step 7 → End पर scale < 1 हो तो spring से 1 पर लौटाओ और pan 0 करो
```

---

## 🟡 Real World Example
**Amazon / Flipkart product gallery & Swiggy Instamart image:** pinch a product photo to see fabric detail, drag to look around, double-tap to zoom in/out. **Google Maps-like** screens inside Ola/Uber use pinch to zoom the map (native map handles it).

## 🟡 Real Example Hindi mein
**Amazon / Flipkart product gallery और Swiggy Instamart image:** product photo को pinch करके कपड़े की बारीकी देखो, drag करके इधर-उधर देखो, double-tap से zoom in/out। **Ola/Uber** की map screens में pinch से map zoom होता है (native map खुद संभालता है)।

---

## 💻 Code Example — Basic

```jsx
import React from 'react';                                      // React
import { StyleSheet } from 'react-native';                      // core
import { Gesture, GestureDetector, GestureHandlerRootView } from 'react-native-gesture-handler';
import Animated, { useSharedValue, useAnimatedStyle, withTiming } from 'react-native-reanimated';

export default function PinchBasic() {
  const scale = useSharedValue(1);                               // current zoom
  const saved = useSharedValue(1);                               // zoom at the end of last pinch

  const pinch = Gesture.Pinch()                                  // two-finger gesture
    .onUpdate((e) => {                                           // fingers moving
      scale.value = saved.value * e.scale;                       // e.scale starts at 1 each time
    })
    .onEnd(() => {                                               // fingers lifted
      saved.value = scale.value;                                 // remember zoom
    });

  const style = useAnimatedStyle(() => ({ transform: [{ scale: scale.value }] })); // apply zoom

  return (
    <GestureHandlerRootView style={styles.root}>
      <GestureDetector gesture={pinch}>
        <Animated.Image
          source={{ uri: 'https://picsum.photos/600/400' }}       // sample image
          style={[styles.img, style]}
        />
      </GestureDetector>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: '#000' },
  img: { width: 300, height: 200 },
});
```

## 💻 Code Example — Advanced

```jsx
import React from 'react';                                      // React
import { StyleSheet, useWindowDimensions } from 'react-native'; // core
import { Gesture, GestureDetector, GestureHandlerRootView } from 'react-native-gesture-handler';
import Animated, { useSharedValue, useAnimatedStyle, withSpring, withTiming, clamp } from 'react-native-reanimated';

const MIN = 1, MAX = 5;                                         // zoom limits

// Zoomable product image: pinch + pan + double tap, clamped, focal-point aware
export default function ZoomableImage({ uri }) {
  const { width } = useWindowDimensions();                      // screen width
  const height = (width * 3) / 4;                               // 4:3 image

  const scale = useSharedValue(1);                              // zoom now
  const savedScale = useSharedValue(1);                         // zoom at last end
  const tx = useSharedValue(0);                                 // pan X
  const ty = useSharedValue(0);                                 // pan Y
  const savedTx = useSharedValue(0);                            // pan start X
  const savedTy = useSharedValue(0);                            // pan start Y
  const focalX = useSharedValue(0);                             // pinch centre (relative to image centre)
  const focalY = useSharedValue(0);

  const pinch = Gesture.Pinch()
    .onStart((e) => {                                           // fingers placed
      focalX.value = e.focalX - width / 2;                      // focal point vs centre
      focalY.value = e.focalY - height / 2;
    })
    .onUpdate((e) => {
      scale.value = clamp(savedScale.value * e.scale, MIN * 0.8, MAX); // allow slight under-zoom rubber band
    })
    .onEnd(() => {
      if (scale.value < MIN) {                                  // below 1x -> go back home
        scale.value = withSpring(MIN);
        tx.value = withSpring(0);
        ty.value = withSpring(0);
        savedTx.value = 0; savedTy.value = 0;
      }
      savedScale.value = Math.max(scale.value, MIN);            // store
    });

  const pan = Gesture.Pan()
    .minPointers(1).maxPointers(2)                              // 1 or 2 fingers
    .onStart(() => { savedTx.value = tx.value; savedTy.value = ty.value; })
    .onUpdate((e) => {
      if (scale.value <= 1) return;                             // no panning when not zoomed
      const maxX = (width * (scale.value - 1)) / 2;             // max drag horizontally
      const maxY = (height * (scale.value - 1)) / 2;            // max drag vertically
      tx.value = clamp(savedTx.value + e.translationX, -maxX, maxX);
      ty.value = clamp(savedTy.value + e.translationY, -maxY, maxY);
    });

  const doubleTap = Gesture.Tap().numberOfTaps(2).onEnd((_e, ok) => {
    if (!ok) return;
    const target = scale.value > 1 ? 1 : 2.5;                   // toggle
    scale.value = withTiming(target);
    savedScale.value = target;
    if (target === 1) { tx.value = withTiming(0); ty.value = withTiming(0); savedTx.value = 0; savedTy.value = 0; }
  });

  // pinch + pan together; double tap runs alongside (Race would cancel others)
  const gesture = Gesture.Simultaneous(pinch, pan, doubleTap);

  const style = useAnimatedStyle(() => ({
    transform: [
      { translateX: tx.value },                                 // pan
      { translateY: ty.value },
      { scale: scale.value },                                   // zoom (applied around view centre)
    ],
  }));

  return (
    <GestureHandlerRootView style={styles.root}>
      <GestureDetector gesture={gesture}>
        <Animated.Image source={{ uri }} style={[{ width, height }, style]} resizeMode="contain" />
      </GestureDetector>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({ root: { flex: 1, backgroundColor: '#000', justifyContent: 'center' } });
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Pinch API | Same | Same |
| Multi-touch emulator testing | Emulator: Ctrl+drag, limited | Simulator: Option+drag for two fingers |
| ScrollView with ScrollView zoom | N/A | `ScrollView maximumZoomScale` built-in zoom (iOS only!) |
| Image quality on zoom | Use high-res + `resizeMode` | Same; also consider `expo-image` for caching |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install react-native-gesture-handler react-native-reanimated
// Image: you may use expo-image (npx expo install expo-image) with Animated via Animated.createAnimatedComponent
```
CLI way:
```jsx
// npm i react-native-gesture-handler react-native-reanimated ; pod install ; babel plugin ; rebuild
// For zoom-only viewer, libraries like react-native-image-zoom-viewer exist (verify maintenance first)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `scale.value = e.scale` (resets to 1 on every new pinch).
✅ Correct: `scale.value = savedScale.value * e.scale` and update `savedScale` on end.

❌ Mistake 2: No min/max clamp (image becomes microscopic or 50x).
✅ Correct: `clamp(value, MIN, MAX)`.

❌ Mistake 3: Pan and Pinch composed with `Race`/`Exclusive`, so only one works.
✅ Correct: `Gesture.Simultaneous`.

❌ Mistake 4: Panning without bounds (image flies off-screen).
✅ Correct: Limit by `(size * (scale - 1)) / 2`.

---

## 🧠 Tricky Interview Question
```jsx
Pinch.onUpdate(e => { scale.value = e.scale; })
// no onEnd
```
User pinches to 2x, lifts fingers, then pinches slightly bigger. What happens?

Answer: The image **snaps back to about 1x** at the start of the second pinch because `e.scale` restarts at 1. It also visually jumps. Fix: store `savedScale` on end and multiply.

---

## ⚫ Interview Questions + Answers
Q1: What does e.scale represent?
A1: Ratio of current finger distance to distance when the pinch began. Always starts at 1.

Q2: How do we zoom around the focal point?
A2: Use `focalX/focalY`; translate so the point under fingers stays fixed: `tx += (focal - centre) * (1 - newScale/oldScale)`, or use a transform origin approach. Simple versions zoom around centre.

Q3: Why Simultaneous?
A3: By default, recognizers can block each other. Simultaneous allows pan and pinch to be active together.

Q4: How to stop Pan from stealing a one-finger scroll when not zoomed?
A4: Return early when `scale <= 1`, or enable the pan only when zoomed with `.enabled(...)` state.

Q5: Does RN have built-in zoom?
A5: iOS `ScrollView` supports `maximumZoomScale`/`minimumZoomScale`; Android does not. So gesture-based is cross-platform.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Image/document viewers, custom canvases

❌ Avoid when:
- Maps (use native map zoom)
- Static images (no gesture needed)

---

## 📊 Visual Diagram
```
  ●        ●          ●                ●
   \      /      →     \              /       e.scale = d2 / d1
    d1=100             d2=200                 scale = saved * e.scale
 
 Pinch(2 fingers) ─┐
 Pan(1-2 fingers) ─┼─ Simultaneous ─► transform: translate + scale
 DoubleTap ────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| pinch | two-finger spread/close | दो उंगलियों से फैलाना/समेटना |
| focal point | centre between fingers | उंगलियों का केंद्र |
| saved scale | zoom stored after gesture | gesture के बाद सेव zoom |
| clamp | limit range | सीमा बाँधना |
| Simultaneous | gestures together | gestures साथ-साथ |

---

## ⚡ 3-Line Summary
English: Pinch gives scale starting at 1 each time.
Multiply by saved scale and clamp min/max.
Combine with Pan and DoubleTap using Simultaneous.

Hindi: Pinch का scale हर बार 1 से शुरू होता है।
saved scale से गुणा करो और min/max में clamp करो।
Simultaneous से Pan और DoubleTap के साथ जोड़ो।

---

## ➡️ Next Topic
**138. Swipe to Delete** — list item को खींचकर delete करना।
