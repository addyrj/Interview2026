# 278. Interview Problem: Build a Bottom Sheet
# हिंदी में: Bottom Sheet बनाओ (Snap Points के साथ)
# Platform: Both ✅ (Android ✅ | iOS ✅)
# Difficulty: ⭐⭐⭐ Medium-Hard | Asked at: Zomato, Swiggy, Uber, PhonePe

Files in this folder: `BottomSheet.jsx` (reusable component), `App.jsx` (demo).
Target: Expo SDK 54 / React Native 0.81 (check current docs — APIs change between SDKs). Only core RN is used: `Animated` + `PanResponder`, no extra library.

---

## 🔵 Simple Definition (English)
A bottom sheet is a panel that slides up from the bottom of the screen. The user can drag it between "snap points" (for example 40% and 85% of the screen height) or drag it down to close it.

## 🔵 सरल परिभाषा (Hindi)
Bottom sheet एक panel है जो screen के नीचे से ऊपर slide होता है। User इसे "snap points" (जैसे screen का 40% या 85%) के बीच drag कर सकता है, या नीचे खींचकर बंद कर सकता है।

---

## 🔴 Problem it Solves
`Modal` covers the full screen and feels heavy. A bottom sheet keeps the context visible (the restaurant list behind), shows quick actions (filters, sort, payment options) and matches the gesture people already know from Google Maps, Zomato and Swiggy.

## 🔴 यह क्यों बना? (Hindi)
`Modal` पूरी screen ढक देता है और भारी लगता है। Bottom sheet में पीछे की screen (restaurant list) दिखती रहती है, और filters, sort, payment जैसे quick actions मिलते हैं। Zomato / Swiggy / Google Maps में user यह gesture पहले से जानता है।

---

## 🔴 Problem Statement
Build a reusable `<BottomSheet>` that:
- opens and closes from a `visible` prop and calls `onClose` when it is closed
- has two snap points (40% and 85% of screen height) and snaps to the nearest one after a drag
- follows the finger while dragging and respects release velocity (flick)
- dims the background (backdrop) and closes on backdrop tap
- works on both platforms (shadow on iOS, `elevation` on Android)

## 💡 Approach
```
STATE (refs, not React state - we do not want re-render on every pixel):
  translateY   Animated.Value   -> 0 = fully open, sheetH = hidden below screen
  currentY     number ref       -> plain copy of translateY (PanResponder reads it)
  startY       number ref       -> translateY when finger touched

SNAP POSITIONS:
  sheetH      = screenH * biggest snap          (sheet is as tall as the biggest snap)
  position(f) = sheetH - screenH * f            (f = 0.85 -> 0, f = 0.4 -> bigger = lower)
  closed      = sheetH

GESTURE:
  grant   -> stop spring, remember startY
  move    -> translateY = clamp(startY + dy)
  release -> pickSnap(y, velocity) -> Animated.spring to that position
             if the target is "closed" -> onClose()
```

## 🟢 How it Works — Step by Step
```
Step 1 → visible=true  -> spring translateY to the first (lowest) open snap
Step 2 → User touches the drag handle -> PanResponder grant -> stop animation
Step 3 → Finger moves -> translateY.setValue(startY + dy), clamped between top and closed
Step 4 → Finger lifts -> pickSnap projects y + velocity*120ms, chooses the nearest snap
Step 5 → Animated.spring moves to it; if it is "closed", call onClose()
Step 6 → Backdrop opacity is interpolated from translateY (0.5 when open, 0 when closed)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → visible=true होते ही translateY को पहले snap तक spring करते हैं
Step 2 → User drag handle छूता है -> चल रही animation रोक देते हैं
Step 3 → उंगली चलती है -> translateY = startY + dy (top और closed के बीच clamp)
Step 4 → उंगली उठती है -> y + velocity*120 से "projected" जगह निकालते हैं, सबसे नज़दीकी snap चुनते हैं
Step 5 → spring से वहाँ पहुँचते हैं; अगर वो "closed" है तो onClose() call होता है
Step 6 → Backdrop की opacity translateY से interpolate होती है (open में 0.5, closed में 0)
```

---

## 🟡 Real World Example
Zomato's "Filters" and Swiggy's "Cart / Address picker" open as a sheet from the bottom. Uber's ride panel and Google Maps' place card snap between a small peek and a large state. Paytm's "Choose payment method" is also a sheet.

## 🟡 Real Example Hindi mein
Zomato का "Filters" और Swiggy का Cart / Address picker नीचे से sheet की तरह खुलते हैं। Uber का ride panel और Google Maps का place card छोटे (peek) और बड़े state के बीच snap होता है। Paytm का "Payment method चुनें" भी sheet है।

---

## 💻 Code Example — Basic
Using the finished component (see `App.jsx`):
```jsx
import React, { useState } from 'react';                         // React + state
import { Text, Pressable } from 'react-native';                  // UI
import BottomSheet from './BottomSheet';                         // our component

export default function Demo() {
  const [open, setOpen] = useState(false);                       // sheet visibility
  return (
    <>
      <Pressable onPress={() => setOpen(true)}><Text>Filters</Text></Pressable>
      {/* snapPoints are fractions of the screen height */}
      <BottomSheet visible={open} onClose={() => setOpen(false)} snapPoints={[0.4, 0.85]}>
        <Text>Pure Veg</Text>
      </BottomSheet>
    </>
  );
}
```

## 💻 Code Example — Advanced
The core (full file: `BottomSheet.jsx`). Pure helpers are exported so they can be unit-tested:
```jsx
// Pick where the sheet settles. y = current translateY, vy = release velocity (px/ms)
export function pickSnap(y, vy, positions) {
  const projected = y + vy * 120;                                // inertia: where we would end up
  return positions.reduce(                                       // closest snap wins
    (best, p) => (Math.abs(p - projected) < Math.abs(best - projected) ? p : best),
    positions[0]
  );
}

// Inside the component: PanResponder on the HANDLE only (so inner ScrollViews still scroll)
const pan = useMemo(() => PanResponder.create({
  onStartShouldSetPanResponder: () => true,                      // claim touch
  onPanResponderGrant: () => {
    translateY.stopAnimation();                                  // stop running spring
    startY.current = currentY.current;                           // remember start
  },
  onPanResponderMove: (_, g) =>                                  // follow finger, clamp
    translateY.setValue(clamp(startY.current + g.dy, topY, closedY)),
  onPanResponderRelease: (_, g) =>                               // settle with velocity
    snapTo(pickSnap(currentY.current, g.vy, positions), g.vy),
  onPanResponderTerminate: () => snapTo(pickSnap(currentY.current, 0, positions)),
}), [positions]);

// Platform-specific shadow
...Platform.select({
  ios: { shadowColor: '#000', shadowOpacity: 0.2, shadowRadius: 10 },
  android: { elevation: 16 },
})
```
Production tip: for complex sheets use `@gorhom/bottom-sheet` (needs react-native-reanimated + react-native-gesture-handler). The hand-made version is what interviewers want to see first.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Shadow | `elevation` | `shadowColor/Opacity/Radius/Offset` |
| Back button | Hardware back should close the sheet (add `BackHandler` in real app) | No hardware back; swipe-down only |
| Keyboard | Window resizes (adjustResize) so inputs move up | Use `KeyboardAvoidingView` / keyboard listeners |
| Home indicator | Gesture nav bar can overlap bottom content | Add `useSafeAreaInsets().bottom` padding |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Core-RN version above needs no native setup. For @gorhom/bottom-sheet:
// npx expo install react-native-reanimated react-native-gesture-handler
// (babel-preset-expo already includes the Reanimated plugin)
```
CLI way:
```jsx
// npm i react-native-reanimated react-native-gesture-handler @gorhom/bottom-sheet
// babel.config.js -> plugins: ['react-native-reanimated/plugin']  (must be LAST)
// iOS: cd ios && pod install ; rebuild the app
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Storing the drag position in `useState` (re-render on every pixel -> janky).
✅ Correct: Use `Animated.Value` + refs; React state only for open/closed.

❌ Mistake 2: Attaching the pan gesture to the whole sheet, so a `FlatList` inside can not scroll.
✅ Correct: Attach `panHandlers` to the handle area only.

❌ Mistake 3: Tiny drag handle (5px) as the only touch target.
✅ Correct: Give the handle area padding (44px+ touch target) like `handleArea`.

❌ Mistake 4: Forgetting to clean listeners (`addListener`) -> memory leak.
✅ Correct: Remove them in the `useEffect` cleanup.

---

## 🧠 Tricky Interview Question
The user flicks the sheet down quickly but only moved 20px. Should it close?

Answer: Yes. That is why `pickSnap` uses `y + vy * 120`: velocity is projected forward, so a fast flick lands on the "closed" snap even though the distance is small. A pure distance check feels broken to users.

---

## ⚫ Interview Questions + Answers
Q1: Why `Animated.Value` and not `useState` for position?
A1: State updates re-render React on every frame; `Animated.Value` updates the view directly (and with `useNativeDriver: true` on the UI thread).

Q2: Why is `useNativeDriver: true` allowed here?
A2: We only animate `transform` and `opacity`, which the native driver supports. Layout props (height, top) are not supported.

Q3: How do you stop a running spring when the user touches again?
A3: `translateY.stopAnimation()` in `onPanResponderGrant`, and read the live value from a ref kept up to date by `addListener`.

Q4: How do you make it respond to screen rotation?
A4: Use `useWindowDimensions()`; positions are derived from the height and recomputed with `useMemo`.

Q5: Reanimated vs Animated for this?
A5: Reanimated 3 runs gestures and animation fully on the UI thread (smoother, no bridge); `Animated + PanResponder` is fine for simple sheets and needs no install.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Short, contextual choices (filters, sort, share, address)
- You want the background to stay visible

❌ Avoid when:
- Long forms or a whole new flow (use a screen)
- Critical blocking alerts (use `Alert` / `Modal`)

---

## 📊 Visual Diagram
```
 ┌──────────────┐     translateY
 │  screen      │
 │   (dimmed)   │
 ├──────────────┤  <- snap 0.85  (translateY = 0)
 │      ──      │  <- drag handle
 │   content    │
 ├──────────────┤  <- snap 0.40
 └──────────────┘  <- closed (translateY = sheetH, below screen)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Snap point | Position where the sheet rests | रुकने की जगह |
| Backdrop | Dark layer behind sheet | पीछे की dim परत |
| PanResponder | Core RN gesture system | Gesture handler |
| Velocity | Speed of finger on release | उंगली की गति |
| translateY | Vertical offset transform | ऊर्ध्वाधर खिसकाव |

---

## ⚡ 3-Line Summary
English: A bottom sheet is an absolutely positioned view moved by `translateY`.
A PanResponder on the handle drags it; on release a pure `pickSnap` function chooses the nearest snap using velocity.
Backdrop opacity is interpolated from the same value.

Hindi: Bottom sheet एक absolute view है जिसे `translateY` से खिसकाया जाता है।
Handle पर PanResponder drag करता है; छोड़ने पर `pickSnap` velocity के हिसाब से सबसे पास का snap चुनता है।
Backdrop की opacity उसी value से interpolate होती है।

---

## ✅ What was verified
Rendered under react-native-web + jsdom: App renders, the toggle inside the sheet works, `pickSnap` and `clamp` return expected values. Real drag gestures, the native driver and Android/iOS shadows were not run (no device).

---

## ➡️ Next Topic
279. Build Swipeable Card — the same PanResponder + Animated idea, but horizontal with a decision threshold.
