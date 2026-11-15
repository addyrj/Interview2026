# 287. Interview Problem: Build an Animated Splash Screen
# हिंदी में: Animated Splash Screen बनाओ
# Platform: Both ✅ (Android ✅ | iOS ✅)
# Difficulty: ⭐⭐ Medium | Asked at: Zomato, Swiggy, Paytm, CRED

File: `AnimatedSplash.jsx`.
Target: Expo SDK 52 with `expo-splash-screen` (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
The native splash screen is shown while the app starts. An animated splash keeps it visible while we load fonts/data, then plays a short JS animation (fade and scale of the logo) before showing the real app.

## 🔵 सरल परिभाषा (Hindi)
App शुरू होते समय native splash screen दिखती है। Animated splash में हम native splash को तब तक रोके रखते हैं जब तक fonts/data load हों, फिर logo की छोटी animation (fade + scale) चलाकर असली app दिखाते हैं।

---

## 🔴 Problem it Solves
Without control, the native splash disappears before assets are ready and the user sees a white flash or half-loaded UI. The native splash can only be a static image, so brand animation has to be done in JS.

## 🔴 यह क्यों बना? (Hindi)
Control न हो तो native splash assets ready होने से पहले ही हट जाती है और white flash या अधूरा UI दिखता है। Native splash सिर्फ़ static image हो सकती है, इसलिए brand animation JS में करनी पड़ती है।

---

## 🔴 Problem Statement
Keep the native splash until assets are ready, hide it smoothly (no flicker), play a logo fade/scale animation in the same background colour, then render children. The animation must not start before the native splash is gone.

## 💡 Approach
```
module level : SplashScreen.preventAutoHideAsync()
ready        : after loading assets/tokens (try/finally so we never get stuck)
render null  : while !ready (native splash is still visible)
onLayout     : when our view is laid out and ready -> SplashScreen.hideAsync()
animDone     : Animated.sequence(fade+spring in, delay, fade out).start(() => setAnimDone(true))
```

## 🟢 How it Works — Step by Step
```
Step 1 → preventAutoHideAsync() at import time keeps the native splash
Step 2 → Load fonts / tokens / config, then setReady(true) (always, even on error)
Step 3 → Render a root View with the animated splash (same background colour as native)
Step 4 → onLayout fires -> hideAsync() -> user sees our splash, no white flash
Step 5 → Logo fades+scales in, holds 400ms, fades out
Step 6 → onFinish -> setAnimDone(true) -> render real app
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → import के समय preventAutoHideAsync() native splash रोके रखता है
Step 2 → fonts / tokens / config load करो, फिर setReady(true) (error हो तब भी)
Step 3 → वही background colour वाला animated splash view render करो
Step 4 → onLayout आने पर hideAsync() -> user को बिना white flash के हमारी splash दिखती है
Step 5 → Logo fade+scale होकर आता है, 400ms रुकता है, फिर fade out
Step 6 → onFinish -> setAnimDone(true) -> असली app दिखता है
```

---

## 🟡 Real World Example
Zomato (red splash + logo), Swiggy (orange splash with logo bounce), CRED and Paytm brand intros, Spotify. They all start with a native static splash and continue with an in-app animation of the same colour.

## 🟡 Real Example Hindi mein
Zomato (लाल splash + logo), Swiggy (orange splash और logo bounce), CRED और Paytm के brand intro, Spotify। सब पहले native static splash दिखाते हैं और उसी रंग में app के अंदर animation चलाते हैं।

---

## 💻 Code Example — Basic
```jsx
import React, { useEffect, useRef } from 'react';                // hooks
import { View, Text, Animated } from 'react-native';             // UI

export default function Splash({ onFinish }) {
  const opacity = useRef(new Animated.Value(0)).current;         // starts invisible
  useEffect(() => {
    Animated.timing(opacity, { toValue: 1, duration: 600, useNativeDriver: true }) // fade in
      .start(() => onFinish());                                  // tell parent when done
  }, [opacity, onFinish]);
  return (
    <View style={{ flex: 1, backgroundColor: '#E23744', alignItems: 'center', justifyContent: 'center' }}>
      <Animated.Text style={{ color: '#fff', fontSize: 40, opacity }}>MyApp</Animated.Text>
    </View>
  );
}
```

## 💻 Code Example — Advanced
From `AnimatedSplash.jsx`:
```jsx
SplashScreen.preventAutoHideAsync().catch(() => {});             // keep native splash (module level)

export default function AppWithSplash({ children }) {
  const [ready, setReady] = useState(false);                     // assets loaded
  const [animDone, setAnimDone] = useState(false);               // animation finished

  useEffect(() => {
    (async () => {
      try { await loadFontsAndConfig(); }                        // your real loading here
      finally { setReady(true); }                                // never get stuck on splash
    })();
  }, []);

  const onLayout = useCallback(async () => {
    if (ready) await SplashScreen.hideAsync();                   // hide native one only after layout
  }, [ready]);

  if (!ready) return null;                                       // native splash still visible
  return (
    <View style={{ flex: 1 }} onLayout={onLayout}>
      {animDone ? children : <Splash onFinish={() => setAnimDone(true)} />}
    </View>
  );
}
// Splash: Animated.sequence([ parallel(fade in, spring scale), delay(400), fade out ]).start(onFinish)
```
Config for the native part (app.json, Expo config plugin — check docs for your SDK):
```json
{ "expo": { "plugins": [["expo-splash-screen", { "backgroundColor": "#E23744", "image": "./assets/splash-icon.png" }]] } }
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Native splash | Android 12+ uses the system SplashScreen API (icon in circle, can not be a full image) | Launch storyboard, full image allowed |
| Duration | System controls the very first frames | Shown until first frame |
| Dark mode | Separate colours in config | Same via config |
| Hiding | `hideAsync()` | `hideAsync()` |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-splash-screen   +  config plugin in app.json
// SplashScreen.preventAutoHideAsync(); ... SplashScreen.hideAsync();
```
CLI way:
```jsx
// Android: res/values/styles.xml SplashTheme + androidx.core:core-splashscreen (or react-native-bootsplash)
// iOS: edit LaunchScreen.storyboard in Xcode
// JS side: react-native-bootsplash -> RNBootSplash.hide({ fade: true })
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting `hideAsync()` -> app stuck on splash forever.
✅ Correct: Always hide, use `try/finally`.

❌ Mistake 2: Calling `preventAutoHideAsync()` late (inside a component) - the splash may already be hidden.
✅ Correct: Call at module level, before render.

❌ Mistake 3: JS splash colour differs from native splash -> visible colour jump.
✅ Correct: Use the same background colour.

❌ Mistake 4: Long animations (3-4 seconds) just to look cool.
✅ Correct: Keep it under ~1.5s; real data loading should drive the duration.

---

## 🧠 Tricky Interview Question
Why do we `return null` while `!ready` instead of rendering the animated splash right away?

Answer: The native splash is still visible and covers the screen. Rendering our animation underneath would run it where the user cannot see it. We start the animation only after the native splash is gone (`hideAsync` in `onLayout`), or the user misses the first frames. (In this sample the animation starts when `ready` becomes true and the view is laid out; for strict ordering, start it inside `onLayout` after `hideAsync` resolves.)

---

## ⚫ Interview Questions + Answers
Q1: Native splash vs JS splash?
A1: Native is shown by the OS before JS loads (static). JS splash runs after the bundle loads (animated).

Q2: What does `preventAutoHideAsync` do?
A2: Stops the native splash from hiding when the first screen renders, until you call `hideAsync`.

Q3: Why `useNativeDriver: true`?
A3: Opacity/transform animations then run on the UI thread, so they stay smooth even if JS is busy.

Q4: Where would Lottie fit?
A4: Replace the `Animated` logo with `lottie-react-native` (`npx expo install lottie-react-native`) and call `onFinish` in its `onAnimationFinish`.

Q5: How to handle errors while loading?
A5: `try/catch/finally` and still hide the splash, optionally show an error screen.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need to load fonts, auth token or remote config before the first screen
- Brand identity animation is wanted

❌ Avoid when:
- It just adds delay; a plain native splash is enough

---

## 📊 Visual Diagram
```
 App launch
    │
    ▼
 [ native splash ]  ── preventAutoHideAsync ──┐
    │  (JS loads, assets load)                │
    ▼                                         │
 ready = true → render <View onLayout>        │
    │                                         │
    ▼                                         │
 onLayout → hideAsync()  ◄────────────────────┘
    │
    ▼
 [ JS splash: fade+scale in → hold → fade out ]
    │ onFinish
    ▼
 [ real app ]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Splash screen | Screen shown at launch | शुरुआती screen |
| Native driver | Animation on UI thread | UI thread animation |
| Animated.sequence | Run animations one by one | एक के बाद एक |
| Animated.parallel | Run together | साथ-साथ |
| onLayout | Called when view is measured | Layout होने पर call |

---

## ⚡ 3-Line Summary
English: Keep the native splash with `preventAutoHideAsync`, load assets, then `hideAsync` after layout.
Play a short `Animated` logo animation in the same colour.
Render the real app after the animation finishes.

Hindi: `preventAutoHideAsync` से native splash रोकें, assets load करें, layout के बाद `hideAsync` करें।
उसी रंग में छोटी `Animated` logo animation चलाएँ।
Animation ख़त्म होने पर असली app दिखाएँ।

---

## ✅ What was verified
react-native-web + jsdom with `expo-splash-screen` mocked: renders nothing while loading, shows the logo after load, and shows the children after the animation finishes (JS fallback animation). The real native splash, Android 12 splash API and `useNativeDriver` were not run (no device).

---

## ➡️ Next Topic
288. Build Skeleton Loader — better perceived performance while data loads.
