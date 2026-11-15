# 18. Running on Real Device
# हिंदी में: असली Phone पर App चलाना
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs)।

---

## 🔵 Simple Definition (English)
Running on a real device means installing and testing your app on an actual phone connected to your dev server. It is the only way to test real camera, sensors, push notifications and true performance.

## 🔵 सरल परिभाषा (Hindi)
Real device पर चलाने का मतलब अपने असली फोन पर app चलाकर test करना। Camera, sensors, push notification और असली performance जाँचने का यही सही तरीका है।

---

## 🔴 Problem it Solves
```
❌ Emulator पर camera, Bluetooth, biometrics, NFC ठीक से नहीं चलते
❌ Emulator की speed असली फोन जैसी नहीं (सस्ते Android phones पर app slow हो सकता है)
❌ Push notifications और deep links की असली जाँच नहीं हो पाती
```

## 🔴 यह क्यों बना? (Hindi)
```
भारत में बहुत लोग कम RAM वाले सस्ते Android फोन इस्तेमाल करते हैं।
Laptop पर तेज़ चलने वाला app उन फोनों पर अटक सकता है, इसलिए real device test ज़रूरी है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 (Expo Go, सबसे आसान) → फोन में "Expo Go" app install करो (Play Store / App Store)
Step 2 → Laptop और फोन को **एक ही Wi-Fi** से जोड़ो
Step 3 → npx expo start  चलाओ, terminal में QR code आएगा
Step 4 → Android: Expo Go से QR scan करो | iOS: Camera app से QR scan करो
Step 5 → App फोन पर load होगा, code बदलो तो Fast Refresh से update होगा

Android (USB, CLI/dev build):
  Phone → Settings → About phone → Build number 7 बार tap → Developer options
  → USB debugging ON → cable जोड़ो → adb devices (device दिखे)
  → npx expo run:android  (या  npx react-native run-android )

iOS (dev build, free Apple ID से भी चलता है पर 7 दिन valid):
  Xcode में Apple ID जोड़ो → iPhone पर Developer Mode ON (Settings → Privacy & Security)
  → npx expo run:ios --device
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → फोन में Expo Go install करो
Step 2 → लैपटॉप और फोन एक ही Wi-Fi पर रखो
Step 3 → npx expo start से QR code लो
Step 4 → Android में Expo Go से scan, iPhone में Camera app से scan
Step 5 → App खुल जाएगा, save करते ही बदलाव दिखेगा

Android USB: Build number 7 बार tap → Developer options → USB debugging ON
→ cable लगाओ → adb devices → npx expo run:android
iOS: Developer Mode ON, Xcode में Apple ID जोड़ो → npx expo run:ios --device
```

---

## 🟡 Real World Example
**Swiggy** delivery-partner app में GPS tracking और background location सिर्फ असली फोन पर सही test होती है। **PhonePe/Paytm** में UPI app-switch और biometric lock असली device पर ही जाँचते हैं।

## 🟡 Real Example Hindi mein
Zomato जैसी app में "rider live location" देखना हो तो असली फोन चाहिए। Emulator में GPS नकली होता है और सस्ते फोन की slow performance भी वहाँ पता नहीं चलती।

---

## 💻 Code Example — Basic
```jsx
// Basic: असली device पर चलने का सबूत — Platform info
import React from 'react';                                   // React
import { View, Text, Platform, StyleSheet } from 'react-native'; // core UI

export default function App() {
  return (
    <View style={styles.box}>{/* container */}
      <Text style={styles.t}>OS: {Platform.OS}</Text>{/* android / ios */}
      <Text style={styles.t}>Version: {String(Platform.Version)}</Text>{/* OS version */}
    </View>
  );
}

const styles = StyleSheet.create({
  box: { flex: 1, justifyContent: 'center', alignItems: 'center' }, // बीच में
  t: { fontSize: 18, marginVertical: 4 },                    // text style
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: Dev server का IP/host दिखाओ + real device vs simulator चेतावनी
// Install: npx expo install expo-device expo-constants
import React from 'react';                                   // React
import { View, Text, StyleSheet } from 'react-native';       // UI
import * as Device from 'expo-device';                       // device info
import Constants from 'expo-constants';                      // app/dev server info

export default function DevInfo() {
  // hostUri dev mode में "192.168.x.x:8081" जैसा होता है (production में undefined)
  const host = Constants.expoConfig?.hostUri ?? 'N/A (production build)';

  return (
    <View style={styles.box}>
      <Text>Real device: {Device.isDevice ? 'Yes' : 'No (simulator/emulator)'}</Text>
      <Text>Brand: {Device.brand ?? 'unknown'}</Text>{/* जैसे Samsung / Apple */}
      <Text>Model: {Device.modelName ?? 'unknown'}</Text>{/* मॉडल का नाम */}
      <Text>RAM (bytes): {Device.totalMemory ?? 'n/a'}</Text>{/* कम RAM पर careful */}
      <Text>Dev server: {host}</Text>{/* अगर connect न हो तो यहाँ देखो */}
    </View>
  );
}

const styles = StyleSheet.create({
  box: { flex: 1, justifyContent: 'center', padding: 16, gap: 6 }, // spacing
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Expo Go से QR scan | Expo Go app के अंदर से | Camera app से |
| USB setup | USB debugging + `adb` | Developer Mode + Xcode, Mac ज़रूरी |
| Dev build किस OS पर बने | Windows/Mac/Linux | **सिर्फ Mac** (या EAS cloud build) |
| Free install | ✅ APK sideload आसान | Free Apple ID: 7 दिन valid; paid ($99/yr) लंबा |
| Wi-Fi न हो तो | `adb reverse tcp:8081 tcp:8081` से USB से Metro | Xcode wired connection |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Expo Go — कोई native build नहीं
npx expo start
# QR scan करो। अगर Wi-Fi block हो तो tunnel:
npx expo start --tunnel
```
CLI way:
```bash
# Bare RN CLI — native build ज़रूरी
adb devices                      # Android: device दिखना चाहिए
npx react-native run-android     # USB से install + run
npx react-native run-ios --device "My iPhone"  # iOS (Mac, signing set होनी चाहिए)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: फोन और laptop अलग Wi-Fi पर
✅ Correct: दोनों एक ही network पर रखो, या `npx expo start --tunnel` इस्तेमाल करो।

❌ Mistake 2: Office/College Wi-Fi का "client isolation" device-to-device block करता है
✅ Correct: फोन का hotspot चलाओ या tunnel इस्तेमाल करो।

❌ Mistake 3: Expo Go में custom native library चलाने की कोशिश
✅ Correct: Expo Go सिर्फ built-in modules support करता है; बाकी के लिए development build (`npx expo run:android` / EAS dev client)।

---

## 🧠 Tricky Interview Question
**Q: App Expo Go में बढ़िया चल रहा है, पर production build में crash कर रहा है। क्यों?**

Answer: Expo Go में debug mode, ज़्यादा permissions और pre-bundled modules होते हैं। Release build में Hermes bytecode, minification (ProGuard/R8), और असली native config (permissions, `app.json` plugins) लगते हैं। इसलिए release बनाकर (`eas build` / `--variant release`) real device पर test करो।

---

## ⚫ Interview Questions + Answers
Q1: QR scan के बाद "Could not connect to development server" क्यों?
A1: अलग Wi-Fi, firewall, या VPN। हल: एक network, firewall खोलो, या `--tunnel`।

Q2: `adb devices` में device "unauthorized" दिखे तो?
A2: फोन पर "Allow USB debugging" prompt accept करो; ज़रूरत हो तो USB debugging बंद-चालू करो।

Q3: iOS पर Mac के बिना real device पर कैसे test करें?
A3: Expo Go (App Store से) + QR scan; native build के लिए EAS Build।

Q4: Expo Go और Dev Build में फ़र्क?
A4: Expo Go पहले से बना sandbox है; Dev Build आपके app की अपनी native code के साथ बनता है।

Q5: असली device पर performance क्यों ज़रूरी?
A5: Low-end Android पर frame drops, memory की कमी आदि सिर्फ वहीं दिखते हैं।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Camera, location, push, biometrics, Bluetooth, UPI intent test करना
- Performance और असली network speed जाँचनी हो

❌ Avoid when:
- हर छोटे UI बदलाव के लिए (simulator तेज़ है)
- बिना USB/Wi-Fi setup के CI automation में

---

## 📊 Visual Diagram
```
 Laptop (Metro :8081) ◄──── same Wi-Fi ────► Phone (Expo Go / Dev build)
        │                                          ▲
        └──── QR code scan / USB (adb) ────────────┘
 Tunnel mode:  Phone ──► ngrok-style tunnel ──► Laptop
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| adb | Android Debug Bridge | Android से बात करने का tool |
| Developer Mode | iOS का dev switch | iPhone का developer मोड |
| Tunnel | Network बाधा पार करने का रास्ता | tunnel connection |
| Expo Go | Prebuilt Expo app | Expo का test app |
| Dev Build | Custom native dev app | अपना development build |

---

## ⚡ 3-Line Summary
English:
1. Real device testing is needed for camera, push, sensors and performance.
2. Expo Go + QR is the fastest; USB/dev builds are needed for custom native code.
3. Same Wi-Fi, USB debugging (Android) and Developer Mode (iOS) are the usual fixes.

Hindi:
1. Camera, push, sensors, performance के लिए real device ज़रूरी है।
2. Expo Go + QR सबसे आसान; custom native code के लिए dev build।
3. Same Wi-Fi, USB debugging और Developer Mode आम समाधान हैं।

---

## ➡️ Next Topic
**19. Metro Bundler — How it Works** — फोन तक JS code कौन पहुँचाता है।
