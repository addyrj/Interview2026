# 168. Flipper Debugging
# हिंदी में: Flipper से Debugging
# Platform: Android ✅ | iOS ✅ | Both ✅ (अब deprecated दिशा में)

> Target: **Expo SDK 52 (check current docs — APIs change between SDKs)**, RN 0.76। **महत्वपूर्ण:** RN 0.73 से Flipper का default integration हटना शुरू हुआ और नए templates में यह शामिल नहीं; RN 0.76 के आसपास **React Native DevTools** (Chrome DevTools आधारित) प्राथमिक debugger है। Expo ने कभी Flipper को default नहीं रखा। इसलिए Flipper को legacy मानो और अपने version के docs जाँचो।

---

## 🔵 Simple Definition (English)
**Flipper** is a desktop debugging app by Meta. It connects to your running app and gives plugins: **Logs, Network inspector, Layout inspector, React DevTools, Databases, Shared Preferences, Hermes debugger and performance tools**. It was the standard RN debugging tool in the 0.62-0.72 era.

## 🔵 सरल परिभाषा (Hindi)
**Flipper** Meta का desktop debugging app है। यह चलते हुए app से जुड़ता है और plugins देता है: **Logs, Network inspector, Layout inspector, React DevTools, Databases, Shared Preferences, Hermes debugger, performance tools**। RN 0.62-0.72 के दौर में यह standard debugging tool था।

---

## 🔴 Problem it Solves
```
पहले:
  Network calls देखने के लिए console.log या अलग proxy (Charles)
  Layout देखने के लिए अंदाज़ा
  Native logs के लिए Android Studio/Xcode अलग-अलग खोलना
  AsyncStorage/SQLite का data देखना मुश्किल

Flipper: सब कुछ एक जगह, device/emulator से live
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले network, layout, native logs, storage देखने के लिए अलग-अलग tools चाहिए थे।
Flipper ने एक ही desktop app में सब दे दिया (live, device से जुड़ा हुआ)।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Desktop पर Flipper app install (fbflipper.com)
Step 2 → App debug build में Flipper SDK (native) चलता है
Step 3 → Dev मशीन और device/emulator एक ही network/ADB से जुड़ें
Step 4 → Flipper device खोज लेता है, app चुनो
Step 5 → Plugins चालू करो: Network, Logs, Layout, Databases, React DevTools
Step 6 → Network tab में हर fetch/axios request, headers, response दिखता है
Step 7 → Hermes debugger से breakpoints; (अब RN DevTools यही काम करता है)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Desktop पर Flipper install
Step 2 → Debug build में Flipper SDK चलता है
Step 3 → Machine और device एक ही network/ADB पर
Step 4 → Flipper device खोजता है
Step 5 → Plugins चालू करो
Step 6 → Network tab में हर request दिखती है
Step 7 → Hermes debugger से breakpoints
```

पुराने RN CLI projects में तैयारी (जहाँ Flipper अभी भी है):
```bash
# iOS
cd ios && pod install                 # Flipper pods (debug में)
# Android: android/app/src/debug/java/.../ReactNativeFlipper.java पहले से template में था
npx react-native run-android           # debug build चलाओ, फिर Flipper खोलो
```

---

## 🟡 Real World Example
Swiggy/Zomato जैसी टीमें पहले Flipper से देखती थीं कि home screen API की 12 requests में कौन सी 3 सेकंड ले रही है (Network plugin), और Layout Inspector से पता करती थीं कि card में अनावश्यक nested Views कहाँ हैं। आज वही काम **React Native DevTools, Reactotron, Charles/Proxyman और Android Studio/Xcode profilers** से होता है।

## 🟡 Real Example Hindi mein
Swiggy/Zomato जैसी टीमें पहले Flipper के Network plugin से देखती थीं कि home API की कौन सी request धीमी है, और Layout Inspector से अनावश्यक nested Views। आज वही काम React Native DevTools, Reactotron, Charles/Proxyman और Android Studio/Xcode से होता है।

---

## 💻 Code Example — Basic
```jsx
// Basic: Flipper/DevTools में लॉग दिखाना और Network देखना
import React, { useEffect } from 'react';                            // React
import { View, Text } from 'react-native';                           // UI

export default function Debug() {
  useEffect(() => {
    console.log('Home mounted');                                     // Logs plugin / DevTools console में दिखेगा
    fetch('https://jsonplaceholder.typicode.com/todos/1')            // demo API
      .then(r => r.json())                                           // JSON parse
      .then(d => console.log('todo', d))                             // Network tab में request भी दिखेगी
      .catch(e => console.warn('fetch failed', e));                  // error भी log
  }, []);

  return <View style={{ padding: 24 }}><Text>Check Flipper / DevTools</Text></View>;
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: dev-only logger और performance markers (Flipper हो या DevTools, दोनों में काम करे)
import React, { useEffect, useRef } from 'react';
import { View, Text, Platform } from 'react-native';

// केवल dev में चलने वाला logger — production में कोई overhead नहीं
const log = (...args) => { if (__DEV__) console.log('[app]', ...args); };

// किसी component का render-count (re-render समस्या ढूँढने के लिए)
function useRenderCount(name) {
  const n = useRef(0);                                               // count ref (re-render नहीं करता)
  n.current += 1;                                                    // हर render पर +1
  if (__DEV__) log(`${name} render #${n.current}`);                  // dev में लॉग
}

export default function Profile() {
  useRenderCount('Profile');                                         // इस component का count

  useEffect(() => {
    const t0 = global.performance?.now?.() ?? Date.now();            // शुरू का समय
    return () => {
      const dt = (global.performance?.now?.() ?? Date.now()) - t0;   // unmount तक का समय
      log('Profile visible for', Math.round(dt), 'ms');              // log
    };
  }, []);

  return (
    <View style={{ padding: 24 }}>
      <Text>{Platform.OS} profile</Text>
    </View>
  );
}

// Flipper में कस्टम plugin के लिए react-native-flipper package था (ab legacy) — नए projects में
// इसकी जगह Reactotron / RN DevTools / Sentry performance उपयोग करो।
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Connection | ADB (USB/emulator) | Local network / simulator |
| Native logs | Logcat Flipper में | Console/OSLog सीमित |
| Layout Inspector | Native layout view | Native layout view |
| Setup issues | Port/ADB conflicts | Pod/Flipper-Folly build errors आम |
| Alternative profiler | Android Studio Profiler | Xcode Instruments |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo Go / dev client में Flipper default नहीं।
// उपयोग करो: npx expo start → 'j' दबाओ (DevTools), या React Native DevTools
// Network: Reactotron / Proxyman / Charles
```
CLI way:
```jsx
// RN 0.62-0.72: Flipper template में था (debug builds)
// RN 0.73+: default हटा; RN 0.76: React Native DevTools:
//   Metro terminal में 'j' दबाओ → DevTools खुलता है (Hermes + Chrome DevTools frontend)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Release builds में Flipper चालू छोड़ना।
✅ Correct: Flipper सिर्फ debug में; release में हटाओ (security + size)।

❌ Mistake 2: नए RN version में Flipper setup में घंटों लगाना।
✅ Correct: RN DevTools / Reactotron इस्तेमाल करो।

❌ Mistake 3: Network tab में sensitive tokens वाले logs पर ध्यान न देना।
✅ Correct: Debug data screenshots में share न करो।

❌ Mistake 4: Performance Flipper से मापकर निष्कर्ष निकालना (dev build)।
✅ Correct: Release build और native profilers भी।

---

## 🧠 Tricky Interview Question
"RN 0.73+ पर Flipper plugin ढूँढ रहे हैं पर app में Flipper दिख ही नहीं रहा। क्या app ग़लत है?"

Answer: नहीं। RN ने default templates से Flipper integration हटा दिया (Flipper का maintenance Meta ने घटाया और RN DevTools को प्राथमिकता दी)। Flipper चाहिए तो manual integration, पर recommend नहीं; React Native DevTools (Metro में `j`), Reactotron और native profilers इस्तेमाल करो।

---

## ⚫ Interview Questions + Answers
Q1: Flipper क्या है?
A1: Meta का desktop debugging platform: Logs, Network, Layout, DB, Hermes debugger आदि plugins।

Q2: अब Flipper का status?
A2: RN 0.73+ में default से हटा; RN DevTools प्राथमिक है। (अपने version के release notes देखो।)

Q3: Network requests कहाँ देखें आज?
A3: Reactotron, Proxyman/Charles, या Android Studio Network profiler। RN DevTools का Network panel version-dependent है — docs जाँचो।

Q4: Re-render कैसे ढूँढें?
A4: React DevTools Profiler, "Highlight updates", या `why-did-you-render`।

Q5: Production में debugging?
A5: Sentry/Firebase Crashlytics/Performance, न कि Flipper।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- पुराना RN project (≤0.72) जहाँ Flipper पहले से है
- Native + JS एक ही tool में चाहिए

❌ Avoid when:
- नया project (RN 0.73+/Expo): DevTools इस्तेमाल करो
- Release builds

---

## 📊 Visual Diagram
```
 [Your App (debug)] ◄──ADB/Wi-Fi──► [Flipper Desktop]
        │                               ├─ Logs
        │  Flipper SDK                  ├─ Network
        ▼                               ├─ Layout Inspector
   JS + Native events ─────────────────►├─ React DevTools
                                        └─ Hermes Debugger
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Flipper | Meta's debug desktop tool | Meta का debugging tool |
| Plugin | Feature module inside Flipper | Flipper के अंदर का feature |
| Logcat | Android system log | Android का system log |
| Layout Inspector | Shows view tree | View tree दिखाने वाला tool |
| React Native DevTools | Modern RN debugger | आधुनिक RN debugger |
| Reactotron | Desktop debugging tool | अलग debugging tool |

---

## ⚡ 3-Line Summary
English: Flipper was Meta's all-in-one RN debugger with network, logs and layout plugins. It is legacy now; React Native DevTools and Reactotron replace it. Never keep it in release builds.
Hindi: Flipper Meta का all-in-one RN debugger था जिसमें network, logs और layout plugins थे। अब यह legacy है; React Native DevTools और Reactotron इसकी जगह हैं। Release builds में कभी न रखो।

---

## ➡️ Next Topic
**169 और आगे (09-advanced)** — Performance के बाद advanced topics: native modules, new architecture आदि।
