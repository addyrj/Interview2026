# 201. Splash Screen Setup (Android)
# हिंदी में: Android में Splash Screen Setup
# Platform: Android ✅ | iOS ✅ (LaunchScreen storyboard)

> Target: **Expo SDK 52 (React Native 0.76)** with `expo-splash-screen` config plugin — check current docs — APIs change between SDKs (older SDKs used the top-level `splash` key).

---

## 🔵 Simple Definition (English)
A splash screen is the first screen shown while your app loads. On Android 12+ the OS itself draws it (icon on a coloured background); you can only customise the icon and colours.

## 🔵 सरल परिभाषा (Hindi)
Splash screen app load होते समय दिखने वाली पहली screen है। Android 12+ में OS खुद इसे बनाता है (रंगीन background पर icon); आप सिर्फ icon और colours बदल सकते हो।

---

## 🔴 Problem it Solves
- JS bundle takes 1-2 seconds to load; without splash users see a blank white screen.
- Brand recall: logo on screen while loading.
- Android 12 forced a standard splash; old full-image splashes got an extra system splash (double splash).

## 🔴 यह क्यों बना? (Hindi)
- JS bundle load में 1-2 सेकंड लगते हैं; splash के बिना सफ़ेद blank screen दिखती है।
- Loading के समय brand logo दिखाने के लिए।
- Android 12 ने standard splash अनिवार्य किया, इसलिए पुराने full-image splash में दो splash दिखने लगे।

---

## 🟢 How it Works — Step by Step
```
Step 1 → User taps icon → Android starts process and shows the splash (native theme)
Step 2 → Splash stays while native code + JS bundle load
Step 3 → Your App mounts; you call SplashScreen.preventAutoHideAsync() early
Step 4 → You load fonts/auth token/API data
Step 5 → When ready, call SplashScreen.hideAsync() → splash fades, UI appears
Step 6 → Splash config is native → needs a rebuild after any change
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Icon tap → Android process शुरू करके native splash दिखाता है
Step 2 → Native code और JS bundle load होने तक splash रहता है
Step 3 → App mount होने पर जल्दी SplashScreen.preventAutoHideAsync() call करो
Step 4 → Fonts / auth token / API data load करो
Step 5 → तैयार होने पर SplashScreen.hideAsync() call करो
Step 6 → Splash config native है → बदलाव के बाद rebuild करो
```

---

## 🟡 Real World Example
**Swiggy** and **Paytm** show a brand-colour splash with a centred logo, then (while checking login token) keep it visible and open directly to Home or Login — the user never sees a flicker of the wrong screen.

## 🟡 Real Example Hindi mein
**Swiggy** और **Paytm** brand colour वाला splash और बीच में logo दिखाते हैं, login token check होने तक splash रुका रहता है, फिर सीधे Home या Login खुलता है — गलत screen की flicker नहीं दिखती।

---

## 💻 Code Example — Basic
`app.json` with the config plugin (SDK 52 style):
```json
{
  "expo": {
    "name": "FoodApp",
    "slug": "food-app",
    "plugins": [
      [
        "expo-splash-screen",
        {
          "image": "./assets/splash-icon.png",
          "imageWidth": 200,
          "resizeMode": "contain",
          "backgroundColor": "#E23744",
          "dark": { "backgroundColor": "#121212" }
        }
      ]
    ]
  }
}
```
Install: `npx expo install expo-splash-screen`

## 💻 Code Example — Advanced
Keep splash until fonts and auth are ready:
```jsx
// React hooks
import React, { useCallback, useEffect, useState } from 'react';
// Basic UI
import { View, Text } from 'react-native';
// Splash control API
import * as SplashScreen from 'expo-splash-screen';
// Font loader hook
import { useFonts } from 'expo-font';

// Prevent auto hide – must be called at module level, before first render
SplashScreen.preventAutoHideAsync();

export default function App() {
  // Load custom font (path must exist in your project)
  const [fontsLoaded, fontError] = useFonts({
    Poppins: require('./assets/fonts/Poppins-Regular.ttf'),
  });
  // Track simulated auth/bootstrap work
  const [ready, setReady] = useState(false);

  // Do async startup work once
  useEffect(() => {
    (async () => {
      try {
        // Example: read token, call /me API
        await new Promise((r) => setTimeout(r, 500)); // placeholder for real work
      } catch (e) {
        console.warn(e); // do not crash on startup errors
      } finally {
        setReady(true); // allow the UI to appear
      }
    })();
  }, []);

  // Hide splash when layout is done and everything is ready
  const onLayout = useCallback(async () => {
    if ((fontsLoaded || fontError) && ready) {
      await SplashScreen.hideAsync(); // fade out splash
    }
  }, [fontsLoaded, fontError, ready]);

  // Render nothing while loading (splash still visible)
  if (!(fontsLoaded || fontError) || !ready) return null;

  return (
    <View style={{ flex: 1, justifyContent: 'center' }} onLayout={onLayout}>
      <Text style={{ fontFamily: 'Poppins' }}>Welcome</Text>
    </View>
  );
}
```
Android 12+ sizes (from Android docs): icon with background: 240dp icon inside a 160dp circle; icon without background: 288dp inside a 192dp circle. Safe design: centre the logo, keep it inside the circle.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Mechanism | Android 12+ SplashScreen API (icon + colour) | LaunchScreen.storyboard (can be full layout) |
| Custom full image | Not on Android 12+ (system draws icon only) | Possible |
| Animation | System fade; optional animated icon | None at OS level |
| Dark mode | `dark` option in plugin | `dark` option in plugin |
| CLI file | `res/values/styles.xml` + `androidx.core:core-splashscreen` | `LaunchScreen.storyboard` |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Config plugin in app.json + SplashScreen.hideAsync() in code
```
CLI way:
```xml
<!-- res/values/styles.xml (AndroidX core-splashscreen) -->
<style name="Theme.App.Starting" parent="Theme.SplashScreen">
    <item name="windowSplashScreenBackground">#E23744</item>
    <item name="windowSplashScreenAnimatedIcon">@drawable/splash_icon</item>
    <item name="postSplashScreenTheme">@style/AppTheme</item>
</style>
```
```kotlin
// MainActivity.kt: call before super.onCreate
SplashScreen.installSplashScreen(this) // from androidx.core.splashscreen
super.onCreate(null)
```
Also add `implementation "androidx.core:core-splashscreen:1.0.1"` to `build.gradle` (use current version).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using a full-screen image and seeing it stretched/cropped on Android 12+.
✅ Correct: Small centred logo on solid colour.

❌ Mistake 2: Calling `preventAutoHideAsync` inside a component after render.
✅ Correct: Call it at module top level.

❌ Mistake 3: Never calling `hideAsync` → app stuck on splash.
✅ Correct: Hide in `finally`, so errors also release it.

❌ Mistake 4: Testing splash in Expo Go (it shows Expo's own).
✅ Correct: Use a development/preview build.

---

## 🧠 Tricky Interview Question
"Why do users see TWO splash screens on Android 12+ in an older RN app?"

Answer: The OS shows its automatic system splash (app icon on window background), then your legacy custom splash Activity/layout appears. Fix: adopt the SplashScreen API (`Theme.SplashScreen`) and remove the custom splash Activity/long-lived image view.

---

## ⚫ Interview Questions + Answers
Q1: How to keep splash while loading data?
A1: `SplashScreen.preventAutoHideAsync()` early, `hideAsync()` when ready.

Q2: Can splash be changed via OTA update?
A2: No, it is native config; new build needed.

Q3: Which Android version introduced the system splash?
A3: Android 12 (API 31); AndroidX core-splashscreen backports it.

Q4: What is `resizeMode`?
A4: `contain`, `cover` or `native` — how the image fits the splash (mostly relevant to iOS / older Android).

Q5: Why shouldn't splash last too long?
A5: Hurts perceived performance; keep loading under ~1-2s and prefer skeleton UI after.

---

## 🔷 When to Use + When Not to Use
✅ Use when: branding + waiting for fonts/auth.

❌ Avoid when: you want to show animated marketing videos — use an in-app onboarding screen.

---

## 📊 Visual Diagram
```
 Tap icon ─► [Native splash: logo on colour] ─► JS loads ─► hideAsync() ─► Home UI
                    ▲                                 │
          preventAutoHideAsync()            fonts + token ready
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Splash | First loading screen | पहली loading screen |
| Cold start | App launch from killed state | App पूरी तरह बंद से शुरू |
| Config plugin | Modifies native files | Native files बदलने वाला plugin |
| Safe zone | Area not cropped | कटने से सुरक्षित क्षेत्र |

---

## ⚡ 3-Line Summary
English: Android 12+ splash = icon on colour, controlled by the system.
Configure with expo-splash-screen plugin; hide it manually when data is ready.
Rebuild after changes.

Hindi: Android 12+ में splash = रंग पर icon, system control करता है।
expo-splash-screen plugin से configure करो; data तैयार होने पर manually hide करो।
बदलाव के बाद rebuild करो।

---

## ➡️ Next Topic
**202. Adaptive Icons (Android)** — launcher के हिसाब से बदलने वाला icon।
