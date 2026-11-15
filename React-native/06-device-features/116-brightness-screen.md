# 116. Brightness + Screen
# हिंदी में: Brightness और Screen Control
# Platform: Android ✅ | iOS ✅ | Both ✅

---

**Expo SDK 52 / React Native 0.76 (check current docs — APIs change between SDKs).** Libraries: `expo-brightness`, `expo-keep-awake`, `expo-screen-orientation`।

---

## 🔵 Simple Definition (English)
Screen control means changing how the display behaves: **brightness** (make it brighter for a QR code), **keep awake** (stop the screen from sleeping during navigation or video), and **orientation** (lock portrait or landscape). Expo gives one small library for each.

## 🔵 सरल परिभाषा (Hindi)
Screen control यानी display का व्यवहार बदलना: **brightness** (QR code के लिए तेज़ करना), **keep awake** (navigation या video में screen को सोने से रोकना), और **orientation** (portrait/landscape lock)। Expo में हर काम के लिए छोटी library है।

---

## 🔴 Problem it Solves
```
PROBLEM:
  Metro/movie ticket QR कम brightness पर scan नहीं होता.
  Recipe या tracking screen 30 सेकंड में बंद हो जाती है.
  Video देखते समय screen अपने आप portrait में घूम जाती है.

SOLUTION:
  ✅ Brightness.setBrightnessAsync(1)  -> QR साफ़ दिखे
  ✅ useKeepAwake()                    -> screen जागती रहे
  ✅ ScreenOrientation.lockAsync(...)  -> orientation fix
```

## 🔴 यह क्यों बना? (Hindi)
कम brightness में QR scan नहीं होता, tracking screen बार-बार बंद हो जाती है, और video में orientation अपने आप बदल जाती है। इन तीन समस्याओं के लिए अलग APIs बनाई गईं ताकि app screen का व्यवहार नियंत्रित कर सके।

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install expo-brightness expo-keep-awake expo-screen-orientation
Step 2 → Brightness: permission माँगो (Android पर system brightness बदलने के लिए)
Step 3 → setBrightnessAsync(0..1) से app की brightness बदलो
Step 4 → पुरानी brightness save करके screen छोड़ते समय restore करो
Step 5 → useKeepAwake() hook component में डालो; unmount पर अपने आप बंद
Step 6 → ScreenOrientation.lockAsync(OrientationLock.LANDSCAPE) जैसा lock लगाओ
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → तीनों libraries install करो
Step 2 → Brightness के लिए permission माँगो
Step 3 → setBrightnessAsync से brightness (0 से 1) बदलो
Step 4 → पुरानी value save करो और बाहर निकलते समय वापस लगाओ
Step 5 → useKeepAwake() से screen जगी रखो (unmount पर बंद)
Step 6 → ScreenOrientation से orientation lock करो
```

---

## 🟡 Real World Example
**BookMyShow / IRCTC** टिकट QR दिखाते समय brightness बढ़ा देते हैं ताकि gate scanner पढ़ ले, बाहर आने पर पहले जैसी करते हैं। **Swiggy** delivery tracking screen और **Google Maps** navigation में screen जगी रहती है। **YouTube/Hotstar** video fullscreen में landscape lock करते हैं।

## 🟡 Real Example Hindi mein
BookMyShow टिकट QR पर brightness बढ़ाता है और वापस आने पर पुरानी कर देता है। Swiggy tracking में screen बंद नहीं होती। Hotstar fullscreen में landscape lock करता है।

---

## 💻 Code Example — Basic
```jsx
// ScreenBasic.jsx — QR screen: brightness 100% और screen जगी रहे
import React, { useEffect } from 'react';                        // hooks
import { View, Text } from 'react-native';                       // UI
import * as Brightness from 'expo-brightness';                   // npx expo install expo-brightness
import { useKeepAwake } from 'expo-keep-awake';                  // npx expo install expo-keep-awake

export default function ScreenBasic() {                          // component
  useKeepAwake();                                                // जब तक यह screen mounted है, display सोएगा नहीं

  useEffect(() => {                                              // mount पर
    let old = null;                                              // पुरानी brightness यहाँ रखेंगे
    (async () => {                                               // async IIFE
      const { status } = await Brightness.requestPermissionsAsync(); // permission माँगो
      if (status !== 'granted') return;                          // नहीं मिली तो छोड़ो
      old = await Brightness.getBrightnessAsync();               // पुरानी value (0..1)
      await Brightness.setBrightnessAsync(1);                    // पूरी brightness
    })();                                                        // तुरंत चलाओ
    return () => {                                               // unmount cleanup
      if (old !== null) Brightness.setBrightnessAsync(old);      // वापस पुरानी value
    };                                                           // cleanup खत्म
  }, []);                                                        // एक बार

  return (                                                       // UI
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: '#fff' }}>{/* सफेद background QR के लिए */}
      <Text>QR code यहाँ दिखेगा</Text>{/* placeholder */}
    </View>
  );                                                             // return खत्म
}                                                                // component खत्म
```

## 💻 Code Example — Advanced
```jsx
// VideoScreen.jsx — brightness slider, keep-awake toggle, orientation lock, AppState restore
import React, { useEffect, useRef, useState } from 'react';      // hooks
import { View, Text, Switch, AppState, StyleSheet } from 'react-native'; // core
import Slider from '@react-native-community/slider';             // npx expo install @react-native-community/slider
import * as Brightness from 'expo-brightness';                   // brightness
import { activateKeepAwakeAsync, deactivateKeepAwake } from 'expo-keep-awake'; // manual keep-awake
import * as ScreenOrientation from 'expo-screen-orientation';    // orientation

export default function VideoScreen() {                          // component
  const [value, setValue] = useState(0.5);                       // slider value
  const [awake, setAwake] = useState(false);                     // keep-awake state
  const original = useRef(null);                                 // पुरानी brightness

  useEffect(() => {                                              // setup
    (async () => {                                               // async
      try {                                                      // error handling
        const { status } = await Brightness.requestPermissionsAsync(); // permission
        if (status === 'granted') {                              // मिली
          original.current = await Brightness.getBrightnessAsync(); // save
          setValue(original.current);                            // slider sync
        }                                                        // if खत्म
        await ScreenOrientation.lockAsync(ScreenOrientation.OrientationLock.LANDSCAPE); // landscape lock
      } catch (e) {                                              // failure
        console.warn('Setup failed', e.message);                 // log
      }                                                          // catch खत्म
    })();                                                        // run
    const sub = AppState.addEventListener('change', (s) => {     // app background/foreground
      if (s === 'active' && original.current !== null) Brightness.setBrightnessAsync(value).catch(() => {}); // वापस आने पर फिर लगाओ
    });                                                          // listener खत्म
    return () => {                                               // cleanup
      sub.remove();                                              // listener हटाओ
      deactivateKeepAwake();                                     // keep awake बंद
      ScreenOrientation.lockAsync(ScreenOrientation.OrientationLock.PORTRAIT_UP).catch(() => {}); // वापस portrait
      if (original.current !== null) Brightness.restoreSystemBrightnessAsync?.(); // system brightness restore (Android)
    };                                                           // cleanup खत्म
  }, []);                                                        // एक बार (value deliberately excluded)

  const onBrightness = async (v) => {                            // slider बदला
    setValue(v);                                                 // UI update
    try { await Brightness.setBrightnessAsync(v); } catch (e) {} // apply, error ignore
  };                                                             // function खत्म

  const onAwake = async (on) => {                                // switch बदला
    setAwake(on);                                                // state
    on ? await activateKeepAwakeAsync('video') : deactivateKeepAwake('video'); // tag के साथ चालू/बंद
  };                                                             // function खत्म

  return (                                                       // UI
    <View style={s.c}>{/* container */}
      <Text>Brightness {Math.round(value * 100)}%</Text>{/* label */}
      <Slider style={s.slider} minimumValue={0} maximumValue={1} value={value} onValueChange={onBrightness} />{/* slider */}
      <View style={s.row}><Text>Keep screen awake</Text><Switch value={awake} onValueChange={onAwake} /></View>{/* switch */}
    </View>
  );                                                             // return खत्म
}                                                                // component खत्म

const s = StyleSheet.create({                                    // styles
  c: { flex: 1, padding: 24, justifyContent: 'center', gap: 16 },// layout
  slider: { height: 40 },                                        // slider height
  row: { flexDirection: 'row', justifyContent: 'space-between' },// row
});                                                              // खत्म
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| `setBrightnessAsync` | सिर्फ app window की brightness | System-wide brightness बदलती है |
| Restore | `restoreSystemBrightnessAsync()` (Android only) | खुद पुरानी value लगानी पड़ती है |
| System brightness | `setSystemBrightnessAsync` (WRITE_SETTINGS permission) | उपलब्ध नहीं |
| Brightness permission | Expo SDK 52 में `requestPermissionsAsync` | वही API |
| Keep awake | WAKE_LOCK based | `idleTimerDisabled` |
| Orientation | Manifest `screenOrientation` + lock | `UISupportedInterfaceOrientations` + lock |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: तीनों libraries तैयार, config plugin अपने आप
import * as Brightness from 'expo-brightness';        // npx expo install expo-brightness
import { useKeepAwake } from 'expo-keep-awake';       // npx expo install expo-keep-awake
import * as ScreenOrientation from 'expo-screen-orientation'; // orientation
// app.json: "orientation": "default" रखो वरना lock का असर सीमित हो सकता है
```
CLI way:
```jsx
// CLI: community libraries या Expo modules
import DeviceBrightness from '@adrianso/react-native-device-brightness'; // npm i, pod install
import KeepAwake from 'react-native-keep-awake';      // npm i react-native-keep-awake
import Orientation from 'react-native-orientation-locker'; // npm i react-native-orientation-locker
Orientation.lockToLandscape();                        // orientation lock
// Android: WAKE_LOCK / WRITE_SETTINGS permission manifest में खुद जोड़ो
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Brightness बदलकर पुरानी value restore न करना।
✅ Correct: Save करो और cleanup में restore करो।

❌ Mistake 2: `useKeepAwake()` पूरे app में लगा देना।
✅ Correct: सिर्फ ज़रूरी screen में; battery बचाओ।

❌ Mistake 3: Orientation lock लगाकर unlock/reset न करना।
✅ Correct: Screen छोड़ते समय portrait/default वापस करो।

❌ Mistake 4: Permission check किए बिना `setBrightnessAsync`।
✅ Correct: `requestPermissionsAsync` का status देखो।

---

## 🧠 Tricky Interview Question
`setBrightnessAsync(1)` बुलाने के बाद user app बंद करके home screen पर गया। Android और iOS पर brightness क्या रहेगी?

Answer: Android पर यह सिर्फ app window की brightness है, app छोड़ते ही system brightness लौट आती है। iOS पर यह system-wide value बदलती है, इसलिए app छोड़ने के बाद भी brightness 100% रह सकती है, जब तक आप खुद restore न करें (या user बदले)। इसीलिए iOS पर AppState/unmount में restore ज़रूरी है।

---

## ⚫ Interview Questions + Answers
Q1: `useKeepAwake` और `activateKeepAwakeAsync` में फर्क?
A1: पहला hook है (mount पर चालू, unmount पर बंद); दूसरा manual control देता है और tag से group कर सकते हैं।

Q2: Brightness value range?
A2: 0 से 1 (float)।

Q3: Orientation lock कब काम नहीं करता?
A3: app.json में `orientation: "portrait"` जैसी fixed value हो तो runtime unlock सीमित रहता है; "default" रखें।

Q4: Keep awake का नुकसान?
A4: Battery drain और OLED burn-in; सिर्फ ज़रूरत पर लगाओ।

Q5: Brightness permission क्यों?
A5: Android में system settings बदलने के लिए; app-level बदलाव के लिए Expo की permission API देखो और status handle करो।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- QR/ticket/boarding pass दिखाना
- Navigation, recipe, tracking, video
- Landscape-only game/video

❌ Avoid when:
- Normal screens (battery)
- User की brightness settings का सम्मान करना हो
- Orientation को बिना ज़रूरत लॉक करना (accessibility)

---

## 📊 Visual Diagram
```
 Screen mount
   |-- save old brightness
   |-- setBrightness(1)
   |-- useKeepAwake()  --> display सोता नहीं
   |-- lock orientation
   |
 Screen unmount
   |-- restore brightness
   |-- keep-awake off
   |-- unlock/portrait
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Brightness | Display light level (0..1) | स्क्रीन की चमक |
| Keep awake | Prevent screen sleep | Screen को सोने से रोकना |
| Orientation lock | Fix portrait/landscape | दिशा लॉक करना |
| Wake lock | Android power flag | Android का जागने वाला flag |
| Restore | Return to old value | पुरानी value लौटाना |

---

## ⚡ 3-Line Summary
English: Use expo-brightness, expo-keep-awake and expo-screen-orientation to control the display.
Always save and restore brightness, and clean up locks on unmount.
Android brightness is per-app window, iOS is system-wide.

Hindi: Display नियंत्रित करने के लिए expo-brightness, expo-keep-awake, expo-screen-orientation use करो।
Brightness save करके restore करो और unmount पर locks हटाओ।
Android में brightness app-window की है, iOS में system-wide।

---

## ➡️ Next Topic
**117. Secure Storage (expo-secure-store)**, अब tokens और passwords सुरक्षित रखना सीखेंगे।
