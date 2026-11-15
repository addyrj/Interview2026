# 139. Lottie Animations
# हिंदी में: Lottie Animations — Designer की बनाई JSON animations
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76, lottie-react-native 7.x (check current docs — APIs change between SDKs). Expo में `npx expo install lottie-react-native`। Lottie Expo Go में चलता है (Expo SDK में bundled version के लिए docs देखें); custom version हो तो dev build चाहिए।

---

## 🔵 Simple Definition (English)
Lottie plays vector animations exported from Adobe After Effects (via the Bodymovin plugin) as small JSON (or `.lottie`) files. The `lottie-react-native` component renders them natively, so designers can ship complex animations without developers coding each frame.

## 🔵 सरल परिभाषा (Hindi)
Lottie, Adobe After Effects (Bodymovin plugin) से export की गई vector animations को छोटी JSON (या `.lottie`) files से चलाता है। `lottie-react-native` component इन्हें native तरीके से render करता है, इसलिए designers बिना developer के हर frame code किए complex animations दे सकते हैं।

---

## 🔴 Problem it Solves
```
Complex animation (success tick with confetti, empty-state illustration, onboarding):
  - GIF: huge size, pixelated, no control, no transparency quality
  - MP4: no transparency, not interactive
  - Code with Animated/Reanimated: very long, designer cannot iterate
Lottie: vector (sharp at any size), tiny JSON (KBs), controllable (play/pause/progress), cross platform.
```

## 🔴 यह क्यों बना? (Hindi)
```
Complex animation (confetti के साथ success tick, empty-state illustration, onboarding):
  - GIF: बहुत भारी, धुंधली, कोई control नहीं
  - MP4: transparency नहीं, interactive नहीं
  - Animated/Reanimated code: बहुत लंबा, designer iterate नहीं कर सकता
Lottie: vector (किसी भी size पर साफ), छोटी JSON (KB), control (play/pause/progress), cross platform।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Designer makes animation in After Effects, exports JSON with Bodymovin (or LottieFiles)
Step 2 → Put file in project: assets/animations/success.json
Step 3 → npx expo install lottie-react-native
Step 4 → <LottieView source={require('./assets/animations/success.json')} autoPlay loop />
Step 5 → Native renderer (lottie-android / lottie-ios) draws vector layers each frame
Step 6 → Control through ref: play(), pause(), reset(), or drive `progress` with Animated/Reanimated
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Designer After Effects में animation बनाता है, Bodymovin (या LottieFiles) से JSON export
Step 2 → File project में रखो: assets/animations/success.json
Step 3 → npx expo install lottie-react-native
Step 4 → <LottieView source={require('./assets/animations/success.json')} autoPlay loop />
Step 5 → Native renderer (lottie-android / lottie-ios) हर frame में vector layers बनाता है
Step 6 → ref से control: play(), pause(), reset(), या `progress` को Animated/Reanimated से चलाओ
```

---

## 🟡 Real World Example
**Swiggy/Zomato order success & Paytm payment success:** after UPI payment, a green tick draws itself with a burst. **Swiggy** empty cart shows an animated illustration. **Zomato** delivery tracking uses a scooter animation. All of these are typically Lottie files designed once and used on Android + iOS + web.

## 🟡 Real Example Hindi mein
**Swiggy/Zomato order success और Paytm payment success:** UPI payment के बाद हरा tick खुद बनता है और burst होता है। **Swiggy** के खाली cart में animated illustration दिखता है। **Zomato** delivery tracking में scooter animation है। ये सब आम तौर पर Lottie files होती हैं जो एक बार design होकर Android + iOS + web पर चलती हैं।

---

## 💻 Code Example — Basic

```jsx
import React from 'react';                                      // React
import { View, Text, StyleSheet } from 'react-native';          // core
import LottieView from 'lottie-react-native';                   // Lottie component

export default function PaymentSuccess() {
  return (
    <View style={styles.container}>
      <LottieView
        source={require('../assets/animations/success.json')}   // local JSON file (you must add it)
        autoPlay                                                // start automatically
        loop={false}                                            // play once
        style={styles.lottie}                                   // MUST give width/height
      />
      <Text style={styles.text}>Payment Successful ₹499</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: '#fff' },
  lottie: { width: 200, height: 200 },                          // size is required, otherwise nothing shows
  text: { marginTop: 16, fontSize: 20, fontWeight: '700' },
});
```

## 💻 Code Example — Advanced

```jsx
import React, { useRef, useState, useEffect } from 'react';     // React hooks
import { View, Text, Pressable, Animated, Easing, AccessibilityInfo, Platform, StyleSheet } from 'react-native';
import LottieView from 'lottie-react-native';

// 1) Play once, then do something when finished (onAnimationFinish)
// 2) Drive Lottie with `progress` (scrubbing) via Animated.Value
// 3) Respect "Reduce Motion" accessibility setting
// 4) Remote JSON with a fallback when load fails
export default function LottieDemo({ onDone }) {
  const ref = useRef(null);                                     // LottieView ref (play/pause/reset)
  const progress = useRef(new Animated.Value(0)).current;       // 0..1 timeline position
  const [reduceMotion, setReduceMotion] = useState(false);      // accessibility flag
  const [failed, setFailed] = useState(false);                  // load error flag

  useEffect(() => {                                             // read accessibility setting once
    AccessibilityInfo.isReduceMotionEnabled().then(setReduceMotion);
    const sub = AccessibilityInfo.addEventListener('reduceMotionChanged', setReduceMotion); // listen changes
    return () => sub.remove();                                  // cleanup
  }, []);

  const scrub = () => {                                         // animate progress manually
    progress.setValue(0);
    Animated.timing(progress, {
      toValue: 1, duration: 2000, easing: Easing.linear,
      useNativeDriver: Platform.OS !== 'web',                   // native driver for progress prop works on native
    }).start();
  };

  if (failed || reduceMotion) {                                 // fallback: static content
    return <View style={styles.center}><Text style={styles.big}>✅ Order placed</Text></View>;
  }

  return (
    <View style={styles.center}>
      {/* A) autoPlay version with finish callback */}
      <LottieView
        ref={ref}
        source={{ uri: 'https://assets.example.com/lottie/order-placed.json' }} // replace with your real URL
        autoPlay
        loop={false}
        speed={1}                                               // 1 = normal; 2 = double speed
        resizeMode="contain"                                    // fit inside box
        onAnimationFinish={(isCancelled) => {                   // fires when finished (or cancelled)
          if (!isCancelled && onDone) onDone();                 // only if completed
        }}
        onAnimationFailure={() => setFailed(true)}              // JSON invalid/network failed (v6+)
        style={styles.box}
      />

      {/* B) progress-driven version (no autoPlay) */}
      <LottieView source={require('../assets/animations/loader.json')} progress={progress} style={styles.small} />
      <Pressable style={styles.btn} onPress={scrub}><Text style={{ color: '#fff' }}>Scrub 0 → 1</Text></Pressable>
      <Pressable style={styles.btn} onPress={() => ref.current?.reset()}><Text style={{ color: '#fff' }}>Replay A</Text></Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  box: { width: 220, height: 220 },
  small: { width: 100, height: 100 },
  big: { fontSize: 24 },
  btn: { marginTop: 10, padding: 10, backgroundColor: '#222', borderRadius: 8 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Renderer | lottie-android | lottie-ios (Core Animation / Main-thread engine) |
| Some After Effects features | Some effects/blend modes unsupported on both, differences exist | Same but differently |
| Performance hint | `renderMode="HARDWARE"` (default AUTOMATIC) can speed up | `renderMode` mostly Android-specific |
| Memory | Big composition = more RAM on low-end phones | Usually fine |
| Reduced Motion | Respect via AccessibilityInfo | Same |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install lottie-react-native
// Works in Expo Go (bundled version) and dev builds / EAS builds
import LottieView from 'lottie-react-native';
```
CLI way:
```jsx
// npm i lottie-react-native ; cd ios && pod install ; rebuild (Android: gradle sync)
// lottie-react-native 7.x targets the New Architecture / also works on old (check README)
import LottieView from 'lottie-react-native';
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No `width/height` style (animation invisible).
✅ Correct: Always set size in `style`.

❌ Mistake 2: Large, complex JSON (MBs, hundreds of layers) -> jank & memory.
✅ Correct: Ask designer to optimize; use `.lottie` (dotLottie) compressed files; test on a low-end device.

❌ Mistake 3: Looping animations that never stop when screen is hidden.
✅ Correct: Pause on blur (`useIsFocused`) or unmount.

❌ Mistake 4: Using unsupported After Effects features (expressions, some effects).
✅ Correct: Check LottieFiles preview / supported-features list, test in the real app.

---

## 🧠 Tricky Interview Question
You use `<LottieView source={require('./a.json')} autoPlay loop={false} />` inside a modal that opens many times. The animation plays only the first time. Why?

Answer: If the component stays mounted (modal just hides), `autoPlay` runs only on mount. On reopen call `ref.current?.reset()` / `play()`, or give it a `key` that changes, or conditionally mount it only when visible.

---

## ⚫ Interview Questions + Answers
Q1: Lottie vs GIF?
A1: Lottie = vector, small, sharp at any scale, controllable. GIF = raster, large, 256 colours, no control.

Q2: How to play only part of the animation?
A2: `play(startFrame, endFrame)` on ref, or drive `progress` between values.

Q3: How to change colours at runtime?
A3: `colorFilters` prop (array of `{ keypath, color }`), supported in lottie-react-native; or ask designer for variants.

Q4: Performance tips?
A4: Smaller JSON, fewer layers/masks, avoid unnecessary loop, set `renderMode="HARDWARE"` on Android where suitable, cache remote files.

Q5: Can Lottie run in the JS thread?
A5: Rendering is native, so JS load does not stop it; but controlling via JS timing (Animated) is subject to normal JS-thread rules.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Success/failure states, onboarding, empty states, loaders
- Designer-owned animations

❌ Avoid when:
- Simple fade/scale (Reanimated is lighter)
- Photographic/video content (use video)

---

## 📊 Visual Diagram
```
 After Effects ──Bodymovin──► animation.json (vector layers, keyframes)
                                   │
              require()/uri        ▼
 React Native: <LottieView/> ──► native Lottie engine ──► frames on screen
                      ▲
          ref.play() / progress / speed / loop
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Lottie | JSON vector animation format | JSON vector animation format |
| Bodymovin | After Effects exporter plugin | After Effects का exporter |
| progress | timeline position 0..1 | timeline की जगह 0..1 |
| dotLottie | compressed `.lottie` file | compressed Lottie file |
| autoPlay | play on mount | mount पर चलाना |

---

## ⚡ 3-Line Summary
English: Lottie plays designer-made vector animations from JSON.
Set a size, use autoPlay/loop or control via ref/progress.
Keep files small and respect Reduce Motion.

Hindi: Lottie designer की बनाई vector animations JSON से चलाता है।
size दो, autoPlay/loop लगाओ या ref/progress से control करो।
files छोटी रखो और Reduce Motion का सम्मान करो।

---

## ➡️ Next Topic
**140. Skeleton Loading Animation** — data आने तक shimmer placeholder।
