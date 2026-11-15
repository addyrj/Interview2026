# 236. Splash Screen Setup (iOS)
# हिंदी में: iOS Splash Screen सेटअप
# Platform: Android ❌ (अलग Android 12 splash API) | iOS ✅

> Expo SDK 52+ (React Native 0.76+)। Expo SDK 52 (check current docs — APIs change between SDKs). Expo में splash config `expo-splash-screen` config plugin की तरफ shift हुआ है; पुराना `splash` key पुराने SDKs में चलता है — अपने SDK के docs verify करें।

---

## 🔵 Simple Definition (English)
The splash screen is the first screen iOS shows while your app launches. On iOS it is a static **LaunchScreen** (storyboard) shown instantly; you cannot run JavaScript there. You can keep it visible a bit longer from JS until your app is ready.

## 🔵 सरल परिभाषा (Hindi)
Splash screen वह पहली screen है जो app खुलते समय iOS दिखाता है। iOS पर यह static **LaunchScreen** (storyboard) होती है जो तुरंत दिखती है; वहाँ JavaScript नहीं चलती। JS से हम इसे app तैयार होने तक थोड़ा लंबा रोक सकते हैं।

---

## 🔴 Problem it Solves
- App load होते समय सफेद/काली खाली screen दिखती थी — खराब अनुभव।
- JS bundle load होने में समय लगता है।

## 🔴 यह क्यों बना? (Hindi)
iOS खुद launch screen तुरंत दिखाता है ताकि app तेज़ लगे। फिर JS तैयार होने पर हम उसे हटाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Logo image तैयार करो (PNG, पारदर्शी या सादा, जैसे 1024 वर्ग में बीच में)
Step 2 → Expo: "expo-splash-screen" plugin में image, backgroundColor, imageWidth दो
Step 3 → Build पर LaunchScreen/SplashScreen storyboard अपने आप बनता है
Step 4 → App launch → iOS storyboard तुरंत दिखाता है
Step 5 → JS में SplashScreen.preventAutoHideAsync() से रोके रखो
Step 6 → Fonts/data तैयार → SplashScreen.hideAsync()
```

## 🟢 कैसे काम करता है? (Hindi)
Native layer (storyboard) पहले दिखता है; React Native लोड होने के बाद अगर आपने `preventAutoHideAsync()` बुलाया हो तो splash बना रहता है। फिर `hideAsync()` से fade-out। CLI में `ios/<App>/LaunchScreen.storyboard` Xcode में खोलकर image/background बदलते हैं।
**Xcode screen:** Interface Builder में सफेद canvas, बीच में UIImageView और ऊपर से Background colour; दाईं तरफ Attributes inspector में Image और Content Mode (Aspect Fit) चुनते हैं।
**ध्यान:** iOS launch screen cache करता है — बदलाव न दिखें तो app delete करके दोबारा install करो।

---

## 🟡 Real World Example
Swiggy का नारंगी background पर सफेद logo वाला splash तुरंत खुलता है और home data आने तक दिखता रहता है। Zomato का लाल splash भी वैसा ही — सब native storyboard से, इसलिए कोई सफेद flash नहीं।

## 🟡 Real Example Hindi mein
Paytm app खुलते ही नीला splash दिखाता है जबकि पीछे login state और config load होता है; तैयार होते ही सीधे home।

---

## 💻 Code Example — Basic
```jsx
// app.json — splash plugin config
// {
//   "expo": {
//     "plugins": [
//       ["expo-splash-screen", {
//         "image": "./assets/splash-icon.png",   // logo image
//         "backgroundColor": "#FF5200",          // पृष्ठभूमि का रंग
//         "imageWidth": 200                      // logo की चौड़ाई (pt)
//       }]
//     ]
//   }
// }
// पुराने SDKs में: "splash": { "image": "./assets/splash.png", "resizeMode": "contain", "backgroundColor": "#FF5200" }
```

## 💻 Code Example — Advanced
```jsx
import React, { useCallback, useEffect, useState } from 'react'; // React hooks
import { View, Text } from 'react-native'; // UI
import * as SplashScreen from 'expo-splash-screen'; // splash control
import * as Font from 'expo-font'; // fonts load

SplashScreen.preventAutoHideAsync(); // JS तैयार होने तक splash रोके रखो

export default function App() { // root component
  const [ready, setReady] = useState(false); // तैयार है या नहीं

  useEffect(() => {
    (async () => { // async setup
      try {
        await Font.loadAsync({}); // यहाँ अपने fonts load करो
        await new Promise((r) => setTimeout(r, 500)); // demo: असली API/config call यहाँ
      } catch (e) {
        console.warn(e); // error log — फिर भी app दिखाओ
      } finally {
        setReady(true); // तैयार
      }
    })();
  }, []);

  const onLayout = useCallback(async () => { // root view layout होने पर
    if (ready) await SplashScreen.hideAsync(); // splash हटाओ
  }, [ready]);

  if (!ready) return null; // तैयार नहीं तो कुछ मत दिखाओ (splash दिख रहा है)

  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }} onLayout={onLayout}>
      <Text>Home</Text>
    </View>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Mechanism | Android 12+ SplashScreen API (icon + background) | LaunchScreen storyboard |
| Full-image splash | Android 12+ में सीमित | संभव, पर Apple HIG logo/सादा सुझाता है |
| Dark mode | अलग drawable/theme | Storyboard में dynamic colours / config में dark option (SDK देखें) |
| Cache | कम | ज़्यादा — reinstall करना पड़ सकता है |
| JS control | expo-splash-screen | वही |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// ["expo-splash-screen", { "image": "...", "backgroundColor": "#fff" }]
// SplashScreen.preventAutoHideAsync() / hideAsync()
```
CLI way:
```jsx
// ios/<App>/LaunchScreen.storyboard — Xcode में खोलकर design
// Info.plist: UILaunchStoryboardName = LaunchScreen
// JS control के लिए: npm i expo-splash-screen (bare में extra setup) या react-native-bootsplash
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: बहुत बड़ी full-screen image लगाना (अलग-अलग iPhone sizes पर कटती है)।
✅ Correct: सादा background + बीच में logo।

❌ Mistake 2: `hideAsync()` बुलाना भूल जाना।
✅ Correct: Ready होने पर हमेशा hide करो (error पर भी)।

❌ Mistake 3: बदलाव न दिखने पर code को दोष देना।
✅ Correct: Simulator/device से app delete करके दोबारा install।

---

## 🧠 Tricky Interview Question
Q: Splash बदला पर simulator पर पुराना ही दिख रहा है। क्यों?

Answer: iOS launch screen snapshot cache करता है, और splash native है इसलिए OTA से नहीं बदलता। App uninstall/reinstall और नया build चाहिए।

---

## ⚫ Interview Questions + Answers
Q1: Splash में JS चल सकती है?
A1: नहीं, वह native है; JS सिर्फ उसे रोक/हटा सकती है।

Q2: Splash बहुत देर दिख रहा है, क्यों?
A2: `hideAsync()` नहीं बुलाया या JS में error/hang।

Q3: OTA से splash बदलेगा?
A3: नहीं, नया build चाहिए।

Q4: App Store पर splash की ज़रूरत?
A4: Launch screen अनिवार्य है (storyboard), नहीं तो iPhone पर letterbox दिखता है।

Q5: Bare CLI में?
A5: LaunchScreen.storyboard edit करो।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Fonts/auth/config लोड होने तक सफेद flash रोकना हो।

❌ Avoid when:
- Splash को loading animation की तरह लंबा रखना — Apple इसे पसंद नहीं करता।

---

## 📊 Visual Diagram
```
 Tap icon ─► iOS LaunchScreen (native, instant) ─► JS starts ─► preventAutoHide ─► load fonts/data ─► hideAsync ─► Home
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Splash | Startup screen | शुरुआती screen |
| Storyboard | iOS UI layout file | iOS layout फ़ाइल |
| preventAutoHide | Keep splash visible | splash रोकना |
| hideAsync | Hide splash | splash हटाना |
| Launch screen | iOS native splash | iOS का native splash |

---

## ⚡ 3-Line Summary
English: iOS splash is a native storyboard shown instantly.
English: Use preventAutoHideAsync/hideAsync to control it from JS.
English: Splash changes need a rebuild and reinstall.
Hindi: iOS splash native storyboard है जो तुरंत दिखता है।
Hindi: JS से preventAutoHideAsync/hideAsync से नियंत्रण।
Hindi: Splash बदलने पर rebuild और reinstall चाहिए।

---

## ➡️ Next Topic
237. Build Release IPA (Expo) — EAS से final IPA बनाना।
