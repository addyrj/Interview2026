# 279. Interview Problem: Build a Swipeable Card (Tinder style)
# हिंदी में: Swipeable Card बनाओ
# Platform: Both ✅ (Android ✅ | iOS ✅)
# Difficulty: ⭐⭐⭐ Medium | Asked at: Zomato, Swiggy, Dating apps, Meesho

Files: `SwipeableCard.jsx` (component + pure `decideSwipe`), `App.jsx` (deck demo).
Target: Expo SDK 54 / React Native 0.81 (check current docs — APIs change between SDKs). Core RN only.

---

## 🔵 Simple Definition (English)
A swipeable card follows your finger left or right. If you drag far enough (or flick fast) it flies off the screen and the app learns your choice (like / skip). Otherwise it springs back to the centre.

## 🔵 सरल परिभाषा (Hindi)
Swipeable card उंगली के साथ left/right चलता है। अगर आप काफी दूर खींचें (या तेज़ flick करें) तो card screen से बाहर उड़ जाता है और app को आपका choice (like / skip) पता चल जाता है। नहीं तो card वापस बीच में आ जाता है।

---

## 🔴 Problem it Solves
Buttons for "save / skip" are slow when you review many items. A swipe is one fast gesture that gives instant visual feedback (tilt + LIKE/NOPE label).

## 🔴 यह क्यों बना? (Hindi)
बहुत सारे items देखते समय "save / skip" buttons धीमे पड़ते हैं। Swipe एक तेज़ gesture है, और साथ में तुरंत visual feedback (झुकना + LIKE/NOPE label) मिलता है।

---

## 🔴 Problem Statement
Build a deck of cards. Swipe right = save, swipe left = skip. While dragging the card must rotate slightly and show a LIKE or NOPE label. Release rules: far enough or fast enough -> fly away and call `onSwipe`; else spring back. A vertical `ScrollView` around the card must not be blocked.

## 💡 Approach
```
Animated.ValueXY pos         -> card position
rotate = pos.x -> [-width..width] => [-15deg..15deg]
likeOpacity = pos.x 0 -> 30% width => 0 -> 1
nopeOpacity = pos.x -30% width -> 0 => 1 -> 0

decideSwipe(dx, vx, width):
   dx > 30% width  OR (fast flick AND dx > 20)  -> 'right'
   dx < -30% width OR (fast flick AND dx < -20) -> 'left'
   else null -> spring back
```

## 🟢 How it Works — Step by Step
```
Step 1 → onMoveShouldSetPanResponder: take the gesture only if |dx| > 8 and |dx| > |dy|
Step 2 → onPanResponderMove: Animated.event writes dx, dy into pos
Step 3 → Interpolations rotate the card and fade LIKE / NOPE labels
Step 4 → Release: decideSwipe(dx, vx, width)
Step 5 → 'left'/'right' -> Animated.timing flies card off, then onSwipe(dir, item)
Step 6 → null -> Animated.spring back to (0,0)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → gesture तभी लें जब horizontal movement vertical से ज़्यादा हो (|dx| > 8)
Step 2 → Move में Animated.event से dx, dy सीधे pos में जाते हैं
Step 3 → Interpolation से card घूमता है और LIKE / NOPE label दिखते हैं
Step 4 → छोड़ने पर decideSwipe(dx, vx, width) फ़ैसला करता है
Step 5 → left/right हो तो card उड़ता है, फिर onSwipe(dir, item) call होता है
Step 6 → नहीं तो spring से वापस (0,0)
```

---

## 🟡 Real World Example
Tinder/Bumble are the famous ones. In India: Swiggy Instamart "swipe to remove" in cart, Zomato Gold restaurant discovery cards, Meesho / Flipkart "Swipe to save to wishlist" experiments, and Gmail-style swipe-to-archive rows.

## 🟡 Real Example Hindi mein
Tinder/Bumble सबसे मशहूर हैं। भारत में: Swiggy Instamart cart में swipe-to-remove, Zomato की restaurant discovery cards, Meesho / Flipkart के wishlist में swipe-to-save, और Gmail की swipe-to-archive rows।

---

## 💻 Code Example — Basic
```jsx
import React, { useRef } from 'react';                           // hooks
import { Animated, PanResponder } from 'react-native';           // core animation + gestures

export default function DragBox() {
  const pos = useRef(new Animated.ValueXY()).current;            // x/y position
  const pan = useRef(PanResponder.create({
    onStartShouldSetPanResponder: () => true,                    // accept touch
    onPanResponderMove: Animated.event([null, { dx: pos.x, dy: pos.y }], { useNativeDriver: false }), // follow finger
    onPanResponderRelease: () =>
      Animated.spring(pos, { toValue: { x: 0, y: 0 }, useNativeDriver: false }).start(), // snap back
  })).current;
  return <Animated.View {...pan.panHandlers} style={{ width: 100, height: 100, backgroundColor: 'tomato', transform: pos.getTranslateTransform() }} />;
}
```

## 💻 Code Example — Advanced
From `SwipeableCard.jsx` — the decision logic is a pure function (easy to unit-test) and the gesture only starts on horizontal movement:
```jsx
export function decideSwipe(dx, vx, width) {
  const threshold = width * 0.3;                                 // 30% of screen
  const fast = Math.abs(vx) > 0.8;                               // flick speed
  if (dx > threshold || (fast && dx > 20)) return 'right';       // save
  if (dx < -threshold || (fast && dx < -20)) return 'left';      // skip
  return null;                                                   // snap back
}

onMoveShouldSetPanResponder: (_, g) =>
  Math.abs(g.dx) > 8 && Math.abs(g.dx) > Math.abs(g.dy),         // horizontal only -> vertical scroll still works

onPanResponderRelease: (_, g) => {
  const dir = decideSwipe(g.dx, g.vx, width);
  if (dir) {
    Animated.timing(pos, {
      toValue: { x: dir === 'right' ? width * 1.5 : -width * 1.5, y: g.dy },
      duration: 220, useNativeDriver: false,                     // ValueXY + Animated.event => JS driver
    }).start(() => onSwipe?.(dir, item));                        // notify AFTER animation
  } else {
    Animated.spring(pos, { toValue: { x: 0, y: 0 }, useNativeDriver: false, friction: 6 }).start();
  }
},
```
In `App.jsx` the card has `key={card.id}` so each new card gets a fresh `pos` value.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Shadow on card | `elevation` | `shadowColor/Opacity/Radius` |
| Back-swipe edge gesture | Android 10+ gesture nav may steal edge swipes | iOS back-swipe from left edge can conflict with stack navigator |
| Haptics | Optional `expo-haptics` (works) | `expo-haptics` gives richer feedback |
| Rotation clipping | Rotated card may clip inside `overflow: hidden` parents | Same, test both |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Core-RN version: nothing to install.
// Nicer physics: npx expo install react-native-gesture-handler react-native-reanimated
```
CLI way:
```jsx
// npm i react-native-gesture-handler react-native-reanimated
// babel plugin 'react-native-reanimated/plugin' LAST; cd ios && pod install
// Wrap app root in <GestureHandlerRootView style={{ flex: 1 }}>
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Starting the pan on any touch (`onStartShouldSetPanResponder: true`) inside a scroll view.
✅ Correct: Use `onMoveShouldSetPanResponder` with a horizontal check.

❌ Mistake 2: Calling `onSwipe` immediately on release; the next card appears while the old one is still on screen.
✅ Correct: Call it in the animation completion callback.

❌ Mistake 3: Re-using the same `Animated.ValueXY` for the next card (it is still off-screen).
✅ Correct: `key={card.id}` to remount, or `pos.setValue({x:0,y:0})`.

❌ Mistake 4: Using `useNativeDriver: true` with `Animated.event` on ValueXY here.
✅ Correct: Use `false` (or Reanimated for UI-thread gestures).

---

## 🧠 Tricky Interview Question
The user drags only 40px right but very fast. Which direction? What if they drag 150px right slowly on a 400px screen?

Answer: 40px fast -> `fast && dx > 20` -> 'right'. 150px slow -> threshold is 120px, 150 > 120 -> also 'right'. 100px slow -> null (spring back). Velocity gives short flicks the same power as long drags.

---

## ⚫ Interview Questions + Answers
Q1: Why `Animated.ValueXY`?
A1: It holds x and y together, and works with `Animated.event` and `getTranslateTransform`.

Q2: How do you rotate based on position?
A2: `interpolate` pos.x from `[-width, 0, width]` to `['-15deg','0deg','15deg']`.

Q3: Why separate `decideSwipe`?
A3: Pure logic = easy unit tests, no gesture system needed.

Q4: How to show the next card behind?
A4: Render the next card below with `scale` interpolated from `abs(pos.x)`.

Q5: Reanimated alternative?
A5: `Gesture.Pan()` + `useSharedValue` + `withSpring` keeps everything on the UI thread.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Binary decisions on many items (like/skip, archive/delete)

❌ Avoid when:
- The action is destructive and cannot be undone (add confirmation / undo)
- Accessibility matters and no button alternative exists (always add buttons too)

---

## 📊 Visual Diagram
```
   NOPE <---- drag left      center      drag right ----> LIKE
     ┌────┐                 ┌────┐                       ┌────┐
     │    │  rotate -15°    │    │     rotate +15°       │    │
     └────┘                 └────┘                       └────┘
   |dx| > 30% width or fast flick  ->  fly off + onSwipe(dir)
   otherwise                        ->  spring back to (0,0)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Threshold | Distance needed to commit | सीमा |
| Flick / velocity | Fast short swipe | तेज़ झटका |
| Interpolation | Map one range to another | मान बदलना |
| ValueXY | Animated x+y pair | x,y जोड़ी |
| Spring | Physics based return | स्प्रिंग animation |

---

## ⚡ 3-Line Summary
English: PanResponder writes dx/dy to an `Animated.ValueXY`; interpolation gives rotation and labels.
On release a pure function decides left / right / snap back using distance and velocity.
Notify the parent only after the fly-off animation ends.

Hindi: PanResponder dx/dy को `Animated.ValueXY` में लिखता है; interpolation से rotation और labels बनते हैं।
छोड़ने पर एक pure function दूरी और गति देखकर left / right / वापस का फ़ैसला करता है।
Parent को fly-off animation ख़त्म होने के बाद ही बताएँ।

---

## ✅ What was verified
react-native-web + jsdom: deck renders the first card; `decideSwipe` tested for drag, flick, small drag. Actual touch gestures and animations were not run (no device).

---

## ➡️ Next Topic
280. Build Drag and Drop List — the same gesture idea, but vertical with index maths.
