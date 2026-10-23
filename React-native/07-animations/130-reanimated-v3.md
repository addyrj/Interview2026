# 130. Reanimated v3 (react-native-reanimated)
# हिंदी में: Reanimated v3 — UI Thread Animations
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
**Reanimated v3** is a React Native animation library that runs animations **entirely on the UI thread** using JSI (JavaScript Interface) — no Bridge communication during animation. The result: buttery 60-120fps animations even when the JS thread is busy. Supports ALL CSS properties (unlike Animated API which only supports transform/opacity with `useNativeDriver`). The standard for complex gestures + animations in production apps.

## 🔵 सरल परिभाषा (Hindi)
**Reanimated v3** React Native animation library है जो animations को **UI thread पर ही** run करती है JSI use करके — animation के दौरान Bridge communication नहीं। Result: JS thread busy हो तो भी 60-120fps animations। सभी CSS properties support (unlike Animated API जो सिर्फ transform/opacity `useNativeDriver` से)। Production apps में complex gestures + animations के लिए standard।

---

## 🔴 Problem it Solves
```
ANIMATED API LIMITATIONS:
  useNativeDriver: true → only transform + opacity on UI thread
  useNativeDriver: false → runs on JS thread (janky when JS is busy!)
  No support: backgroundColor, width, height → always JS thread
  Gesture + animation combo: gesture runs on UI thread, animation on JS thread
                             → at least 1 frame delay → noticeable lag!

REANIMATED V3 SOLUTION:
  All animations run on UI thread (JSI-powered, no Bridge)
  Works for: transform, opacity, color, width, height, borderRadius...
  Gesture + animation: BOTH on UI thread → zero lag!
  Shared values: C++ objects accessed directly from JS + UI thread
  60-120fps animations that never jank
```

---

## 🟢 How it Works — Step by Step

```
REANIMATED V3 ARCHITECTURE:
──────────────────────────────────────────────────────
  JS Thread:
    useSharedValue(0) → creates C++ object (accessible from both threads)
    useAnimatedStyle(() => ({...})) → worklet compiled to C++ bytecode
    withTiming(1, { duration: 300 }) → schedules animation on UI thread

  UI Thread:
    Runs animation loop at 60/120fps
    No JS thread communication needed during animation!
    Reads/writes sharedValue directly (it's a C++ object)
    Applies style updates to native views

  WORKLET:
    Special function that runs on UI thread
    Marked with 'worklet' directive (or auto-detected)
    Has access to: sharedValues, JS closures (by value, not reference)
    CANNOT call regular JS functions (they run on JS thread)

  FLOW:
  JS Thread creates animation → UI Thread runs it → Native renders
  Zero JS thread involvement during the actual animation!
```

---

## 🟡 Real World Example
**Swiggy food ordering:** Draggable floating cart button. User drags it around screen — gesture runs on UI thread (GestureHandler). Button position animates with the drag — animation runs on UI thread (Reanimated). Result: 120fps animation with zero lag even if Swiggy's JS thread is parsing restaurant data. With old Animated API: gesture on UI thread → sends to JS → computes new position → sends to UI thread → renders. 2-frame minimum lag = noticeable rubber-band effect. Reanimated eliminates this entirely.

---

## 💻 Code Example — Basic

```tsx
import React from 'react';
import { View, Pressable, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  withSpring,
  withRepeat,
  withSequence,
  Easing,
} from 'react-native-reanimated';

export default function AnimationExamples() {
  // ─── SHARED VALUE: C++ value, accessible from JS + UI thread ───────────
  const opacity = useSharedValue(1);       // number
  const scale = useSharedValue(1);         // number
  const rotation = useSharedValue(0);      // number (degrees)
  const backgroundColor = useSharedValue('#e23744');  // string

  // ─── ANIMATED STYLE: worklet that runs on UI thread ────────────────────
  const animatedStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
    transform: [
      { scale: scale.value },
      { rotate: `${rotation.value}deg` },
    ],
  }));

  // backgroundColor needs a separate style (interpolation)
  const bgStyle = useAnimatedStyle(() => ({
    backgroundColor: backgroundColor.value,
  }));

  // ─── FADE IN ────────────────────────────────────────────────────────────
  const fadeIn = () => {
    opacity.value = 0;
    opacity.value = withTiming(1, { duration: 500, easing: Easing.out(Easing.quad) });
  };

  // ─── SPRING SCALE ───────────────────────────────────────────────────────
  const springScale = () => {
    scale.value = withSpring(1.3, { damping: 10, stiffness: 100 }, () => {
      // This callback runs on UI thread after animation completes
      scale.value = withSpring(1);
    });
  };

  // ─── SPINNING LOADER ────────────────────────────────────────────────────
  const startSpin = () => {
    rotation.value = withRepeat(
      withTiming(360, { duration: 1000, easing: Easing.linear }),
      -1,       // -1 = infinite
      false,    // false = don't reverse direction
    );
  };

  // ─── PULSE ANIMATION ────────────────────────────────────────────────────
  const pulse = () => {
    scale.value = withRepeat(
      withSequence(
        withTiming(1.1, { duration: 400 }),
        withTiming(1.0, { duration: 400 }),
      ),
      3,        // repeat 3 times
      false,
    );
  };

  return (
    <View style={styles.container}>
      {/* Use Animated.View (not View) for Reanimated styles */}
      <Animated.View style={[styles.box, animatedStyle, bgStyle]} />

      <Pressable style={styles.btn} onPress={fadeIn}><Animated.Text style={styles.btnText}>Fade In</Animated.Text></Pressable>
      <Pressable style={styles.btn} onPress={springScale}><Animated.Text style={styles.btnText}>Spring</Animated.Text></Pressable>
      <Pressable style={styles.btn} onPress={startSpin}><Animated.Text style={styles.btnText}>Spin</Animated.Text></Pressable>
      <Pressable style={styles.btn} onPress={pulse}><Animated.Text style={styles.btnText}>Pulse</Animated.Text></Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 12 },
  box: { width: 100, height: 100, borderRadius: 16, backgroundColor: '#e23744', marginBottom: 24 },
  btn: { backgroundColor: '#f0f0f0', paddingHorizontal: 20, paddingVertical: 10, borderRadius: 8 },
  btnText: { fontWeight: '600' },
});
```

## 💻 Code Example — Advanced (Draggable Card with Gesture)

```tsx
import React from 'react';
import { View, Text, StyleSheet, Dimensions } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  runOnJS,
  interpolate,
  Extrapolation,
} from 'react-native-reanimated';
import { Gesture, GestureDetector, GestureHandlerRootView } from 'react-native-gesture-handler';

const { width: SCREEN_WIDTH } = Dimensions.get('window');
const SWIPE_THRESHOLD = SCREEN_WIDTH * 0.3;  // 30% of screen = swipe to dismiss

type CardProps = {
  name: string;
  price: string;
  onLike: () => void;
  onDislike: () => void;
};

function SwipeCard({ name, price, onLike, onDislike }: CardProps) {
  // ─── SHARED VALUES (C++ objects, no Bridge) ──────────────────────────────
  const translateX = useSharedValue(0);
  const translateY = useSharedValue(0);
  const rotation = useSharedValue(0);

  // ─── PAN GESTURE — runs on UI thread ─────────────────────────────────────
  const panGesture = Gesture.Pan()
    .onUpdate((event) => {
      // This runs on UI thread — no JS thread needed!
      translateX.value = event.translationX;
      translateY.value = event.translationY * 0.3;  // less vertical movement
      rotation.value = (event.translationX / SCREEN_WIDTH) * 15;  // tilt
    })
    .onEnd((event) => {
      // Swipe left far enough → dislike
      if (event.translationX < -SWIPE_THRESHOLD) {
        translateX.value = withTiming(-SCREEN_WIDTH * 1.5, { duration: 300 });
        runOnJS(onDislike)();   // call JS function from UI thread
        return;
      }
      // Swipe right far enough → like
      if (event.translationX > SWIPE_THRESHOLD) {
        translateX.value = withTiming(SCREEN_WIDTH * 1.5, { duration: 300 });
        runOnJS(onLike)();      // runOnJS bridges back to JS thread
        return;
      }
      // Not far enough → snap back to center
      translateX.value = withSpring(0);
      translateY.value = withSpring(0);
      rotation.value = withSpring(0);
    });

  // ─── ANIMATED STYLE — worklet on UI thread ────────────────────────────────
  const cardStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: translateX.value },
      { translateY: translateY.value },
      { rotate: `${rotation.value}deg` },
    ],
  }));

  // Like/Dislike indicators fade in as you swipe
  const likeOpacity = useAnimatedStyle(() => ({
    opacity: interpolate(
      translateX.value,
      [0, SWIPE_THRESHOLD],
      [0, 1],
      Extrapolation.CLAMP,
    ),
  }));

  const dislikeOpacity = useAnimatedStyle(() => ({
    opacity: interpolate(
      translateX.value,
      [-SWIPE_THRESHOLD, 0],
      [1, 0],
      Extrapolation.CLAMP,
    ),
  }));

  return (
    <GestureDetector gesture={panGesture}>
      <Animated.View style={[styles.card, cardStyle]}>
        {/* LIKE indicator */}
        <Animated.View style={[styles.indicator, styles.likeIndicator, likeOpacity]}>
          <Text style={styles.indicatorText}>LIKE ✓</Text>
        </Animated.View>

        {/* DISLIKE indicator */}
        <Animated.View style={[styles.indicator, styles.dislikeIndicator, dislikeOpacity]}>
          <Text style={styles.indicatorText}>PASS ✗</Text>
        </Animated.View>

        <Text style={styles.cardName}>{name}</Text>
        <Text style={styles.cardPrice}>{price}</Text>
      </Animated.View>
    </GestureDetector>
  );
}

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>  {/* Required wrapper! */}
      <View style={styles.container}>
        <SwipeCard
          name="Butter Chicken"
          price="₹350"
          onLike={() => console.log('Liked!')}
          onDislike={() => console.log('Disliked!')}
        />
      </View>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: '#f5f5f5' },
  card: {
    width: SCREEN_WIDTH * 0.85,
    height: 400,
    backgroundColor: 'white',
    borderRadius: 20,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 5,
    justifyContent: 'flex-end',
  },
  indicator: {
    position: 'absolute',
    top: 24,
    padding: 8,
    borderRadius: 8,
    borderWidth: 3,
  },
  likeIndicator: { left: 20, borderColor: '#4CAF50' },
  dislikeIndicator: { right: 20, borderColor: '#e23744' },
  indicatorText: { fontWeight: '800', fontSize: 18 },
  cardName: { fontSize: 24, fontWeight: '700', color: '#1a1a1a' },
  cardPrice: { fontSize: 18, color: '#888', marginTop: 4 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Frame rate | 60fps (standard) | 60fps / 120fps (ProMotion) |
| Reanimated support | ✅ Full | ✅ Full |
| GestureHandler | ✅ | ✅ |
| JSI availability | ✅ (New Arch or Reanimated JSI) | ✅ |
| `runOnJS` | Same on both | Same |

---

## 🟠 Expo vs CLI Difference

Expo way:
```bash
npx expo install react-native-reanimated react-native-gesture-handler
# babel.config.js — REQUIRED plugin:
module.exports = {
  presets: ['babel-preset-expo'],
  plugins: ['react-native-reanimated/plugin'],  // must be LAST plugin
};
```

CLI way:
```bash
npm install react-native-reanimated react-native-gesture-handler
# android/app/build.gradle: auto-linked
# ios: pod install
# babel.config.js: same plugin requirement
# MainApplication.kt: add JSI package (auto with RN 0.71+)
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting Babel plugin (Reanimated won't work!)
```js
// babel.config.js — MUST have this, MUST be last plugin
module.exports = {
  presets: ['babel-preset-expo'],
  plugins: [
    // other plugins first...
    'react-native-reanimated/plugin',  // ← LAST always!
  ],
};
// Without this: useSharedValue won't be on UI thread → crashes
```

❌ **Mistake 2:** Calling JS functions directly in worklets
```tsx
// WRONG: console.log is a JS function, can't call from UI thread worklet
const style = useAnimatedStyle(() => {
  console.log(sharedValue.value);  // crashes! console.log is JS-only
  return { opacity: sharedValue.value };
});

// CORRECT: Use runOnJS for JS thread calls
const logValue = (val: number) => console.log(val);  // JS function

const style = useAnimatedStyle(() => {
  runOnJS(logValue)(sharedValue.value);  // bridge to JS thread
  return { opacity: sharedValue.value };
});
```

❌ **Mistake 3:** Not wrapping app in `GestureHandlerRootView`
```tsx
// WRONG: Gestures don't work without root view
export default function App() {
  return <Navigator />;  // gesture-handler won't initialize
}

// CORRECT:
export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <Navigator />
    </GestureHandlerRootView>
  );
}
```

---

## 🧠 Tricky Interview Question

**Q: What is a "worklet" in Reanimated v3, and what are its limitations?**

**Answer:** A worklet is a JavaScript function that Reanimated compiles to bytecode and runs on the UI thread instead of the JS thread. In Reanimated v3, `useAnimatedStyle`, `useAnimatedGestureHandler`, and `useDerivedValue` callbacks are automatically worklets — no need for the `'worklet'` directive inside them (though you still need it for custom functions called from these hooks). Limitations: (1) **Cannot call regular JS functions** — `console.log`, `setState`, `navigation.navigate` cannot be called directly from a worklet. Use `runOnJS(fn)(args)` to bridge back to JS thread. (2) **Closures capture values by copy at creation time**, not by reference — if a JS variable changes after the worklet is created, the worklet sees the old value. Use `sharedValues` for values that need to be current. (3) **Cannot use React hooks** inside worklets. (4) Not all third-party libraries work inside worklets — only those designed for it.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between Animated API and Reanimated v3?**
A1: Animated API: `useNativeDriver: true` moves transform/opacity animations to the UI thread, but color/layout animations still run on JS thread. Gesture + animation have at least 1 frame lag due to Bridge. Reanimated v3: ALL animations and gestures run on the UI thread via JSI — no Bridge. Supports every CSS property on UI thread. Zero lag for gesture-driven animations. The trade-off: Reanimated has more setup (Babel plugin, GestureHandlerRootView) and a steeper learning curve.

**Q2: What is `useSharedValue`?**
A2: `useSharedValue(initialValue)` creates a shared value — a C++ object accessible from both the JS thread and the UI thread simultaneously without serialization. Reading: `sharedValue.value`. Writing: `sharedValue.value = 1` (direct assignment triggers UI update). Used as the "animated variable" for Reanimated animations. Never use `useState` for animated values — state updates cause React re-renders; shared values update the UI directly without re-rendering.

**Q3: What is `useAnimatedStyle`?**
A3: `useAnimatedStyle(() => ({ transform: [...], opacity: ... }))` — a worklet that runs on the UI thread to compute styles based on shared values. The returned style object is applied to an `Animated.View` (or `Animated.Text`, `Animated.Image`). Whenever a shared value read inside this worklet changes, the worklet re-runs on the UI thread and the style updates instantly — no JS thread, no React render cycle.

**Q4: What is `runOnJS` and when do you need it?**
A4: `runOnJS(fn)(args)` schedules a JS thread function call from the UI thread (worklet). Needed when: (1) updating React state after animation (`runOnJS(setIsVisible)(false)`), (2) navigating after animation completes (`runOnJS(navigation.navigate)('Home')`), (3) calling analytics/logging from a gesture handler. Without it, calling JS functions from worklets crashes. The opposite — `runOnUI(fn)(args)` — runs a worklet from the JS thread.

**Q5: What is `withSpring` vs `withTiming` in Reanimated?**
A5: `withTiming(value, { duration, easing })` — duration-based, linear or eased. Predictable, good for UI transitions (fade, slide, expand). `withSpring(value, { damping, stiffness, mass })` — physics simulation, overshoots and settles naturally. Feels organic, good for gesture-released animations (card snap-back, drawer close). Spring has no fixed duration — it plays until the physics settle. Use timing for intentional UI animations, spring for anything that mimics physical objects.

---

## 📊 Visual Diagram

```
REANIMATED v3 vs ANIMATED API — Thread Model:
──────────────────────────────────────────────────────

  ANIMATED API (useNativeDriver: true):
  ┌─────────────┐   Bridge   ┌─────────────┐
  │  JS Thread  │ ──────────▶ │  UI Thread  │
  │             │            │             │
  │ setState()  │            │ Renders     │
  │ onGesture() │ ◀───────── │ Gesture     │
  │             │  1 frame   │ events      │
  └─────────────┘  delay     └─────────────┘
  Gesture → JS → computes → UI: 1-2 frame lag!

  REANIMATED V3 (JSI):
  ┌─────────────┐           ┌─────────────┐
  │  JS Thread  │  Shared   │  UI Thread  │
  │             │  Values   │             │
  │ Creates     │ ◀────────▶ │ Gesture     │
  │ animation   │  C++ obj  │ Animation   │
  │ config once │           │ 60-120fps   │
  └─────────────┘           └─────────────┘
  Once set up: UI thread handles everything — zero lag!

SUPPORTED PROPERTIES:
  Animated API (useNativeDriver: true):
    ✅ transform (translateX, translateY, scale, rotate)
    ✅ opacity
    ❌ backgroundColor, width, height, borderRadius → JS thread only

  Reanimated v3:
    ✅ Everything above
    ✅ backgroundColor, color
    ✅ width, height, borderRadius
    ✅ ALL layout properties — on UI thread!
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| useSharedValue | C++ value, JS + UI thread accessible | C++ value, दोनों threads accessible |
| useAnimatedStyle | Worklet for UI-thread styles | UI thread पर styles compute करे |
| worklet | Function that runs on UI thread | UI thread पर run होने वाला function |
| withTiming | Duration-based animation | Duration-based animation |
| withSpring | Physics-based animation | Physics-based animation |
| withRepeat | Repeat animation N times | Animation N बार repeat |
| runOnJS | Call JS function from UI thread | UI thread से JS function call |
| Gesture.Pan() | Pan/drag gesture handler | Pan/drag gesture |
| GestureDetector | Wraps view with gesture | View को gesture से wrap |
| interpolate | Map input range to output range | Input range → output range map |

---

## ⚡ 3-Line Summary
**English:**
1. Reanimated v3 runs ALL animations on the UI thread via JSI — no Bridge, no JS thread blocking, 60-120fps for any CSS property including color, width, height.
2. Core API: `useSharedValue` (C++ animated variable), `useAnimatedStyle` (worklet that computes styles on UI thread), `withTiming`/`withSpring` (animation curves).
3. For gestures + animations: combine with `react-native-gesture-handler` (`Gesture.Pan()`, `GestureDetector`) — both run on UI thread for zero-lag gesture-driven animations.

**Hindi:**
1. Reanimated v3 सभी animations UI thread पर run करता है JSI से — no Bridge, no JS blocking, 60-120fps, color/width/height सब।
2. Core API: `useSharedValue` (animated variable), `useAnimatedStyle` (UI thread पर styles), `withTiming`/`withSpring` (animation curves)।
3. Gestures + animations: `react-native-gesture-handler` के साथ combine करो (`Gesture.Pan()`) — दोनों UI thread पर = zero lag।

---

## ➡️ Next Topic
**131. Reanimated Layout Animations** — Entering/exiting animations, shared element transitions।
