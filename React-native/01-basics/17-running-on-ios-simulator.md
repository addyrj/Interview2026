# 17. Running on iOS Simulator
# हिंदी में: iOS Simulator पर App चलाना
# Platform: iOS ✅ (सिर्फ Mac पर) | Android ❌

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs)। Simulator सिर्फ **macOS + Xcode** पर चलता है।

---

## 🔵 Simple Definition (English)
The iOS Simulator is an Apple tool (part of Xcode) that runs a virtual iPhone/iPad on your Mac. You use it to run and debug your React Native app without a real iPhone.

## 🔵 सरल परिभाषा (Hindi)
iOS Simulator Apple का tool है (Xcode के साथ आता है) जो आपके Mac पर virtual iPhone/iPad चलाता है। इसमें आप बिना असली iPhone के अपना React Native app चला और debug कर सकते हो।

---

## 🔴 Problem it Solves
```
❌ हर बार असली iPhone ढूँढना और cable लगाना
❌ अलग-अलग iPhone sizes (SE, 15, 15 Pro Max) एक साथ test नहीं हो सकते
❌ अलग iOS versions पर test करने के लिए कई devices चाहिए
```

## 🔴 यह क्यों बना? (Hindi)
```
Developer को तेज़ feedback चाहिए। Simulator से कई iPhone models और iOS
versions एक ही Mac पर चलते हैं, इसलिए device खरीदने की ज़रूरत कम होती है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Mac App Store से Xcode install करो (बड़ा download ~10GB+)
Step 2 → Xcode खोलो, license accept करो, "Command Line Tools" चुनो
         (Xcode → Settings → Locations → Command Line Tools)
Step 3 → Xcode → Settings → Platforms/Components में iOS Simulator runtime download करो
Step 4 → Project folder में:  npx expo start
Step 5 → Terminal में  i  दबाओ  (या  npx expo run:ios )
Step 6 → Simulator खुलता है, Expo Go install होकर app load होता है
Step 7 → Code save करो → Fast Refresh से UI बदल जाता है
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Mac App Store से Xcode install करो
Step 2 → Xcode खोलकर license accept करो, Command Line Tools चुनो
Step 3 → iOS Simulator runtime download करो
Step 4 → Project में  npx expo start  चलाओ
Step 5 → Terminal में  i  दबाओ
Step 6 → Simulator खुलेगा और app load होगा
Step 7 → Code save करते ही Fast Refresh से बदलाव दिखेगा
```

---

## 🟡 Real World Example
**Zomato**, **Swiggy** और **Paytm** जैसी teams नई screen बनाते समय पहले iPhone SE (छोटी screen) और iPhone 15 Pro Max (बड़ी screen) simulators पर layout जाँचती हैं, फिर असली device पर camera/location/payment जैसी चीज़ें test करती हैं।

## 🟡 Real Example Hindi mein
Swiggy की team cart screen बनाते समय iPhone SE simulator पर देखती है कि button कट तो नहीं रहा, और Pro Max पर देखती है कि बहुत खाली जगह तो नहीं। असली payment (UPI) बाद में real device पर होती है।

---

## 💻 Code Example — Basic
```jsx
// Basic: Simulator पर पता करो कि app iOS पर चल रहा है
import React from 'react';                               // React import
import { View, Text, Platform, StyleSheet } from 'react-native'; // core components

export default function App() {
  return (
    <View style={styles.box}>{/* पूरी screen का container */}
      <Text style={styles.text}>
        Running on: {Platform.OS}{/* iOS simulator पर "ios" दिखेगा */}
      </Text>
      <Text>iOS version: {String(Platform.Version)}</Text>{/* जैसे "17.5" */}
    </View>
  );
}

const styles = StyleSheet.create({
  box: { flex: 1, justifyContent: 'center', alignItems: 'center' }, // बीच में रखो
  text: { fontSize: 20, fontWeight: '600' },             // बड़ा text
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: Simulator पहचानना + dev-only warning (expo-device)
// Install:  npx expo install expo-device
import React from 'react';                               // React
import { View, Text, StyleSheet } from 'react-native';   // UI
import * as Device from 'expo-device';                   // device info (Expo SDK 52)

export default function SimInfo() {
  // Device.isDevice → false मतलब simulator/emulator, true मतलब real device
  const isSimulator = !Device.isDevice;                  // simulator है या नहीं

  return (
    <View style={styles.box}>
      <Text>Model: {Device.modelName ?? 'unknown'}</Text>{/* जैसे "iPhone 15" */}
      <Text>OS: {Device.osName} {Device.osVersion}</Text>{/* iOS 17.5 */}
      {isSimulator && (                                  // सिर्फ simulator पर दिखाओ
        <Text style={styles.warn}>
          Simulator: push notifications / camera यहाँ काम नहीं करेंगे
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  box: { flex: 1, justifyContent: 'center', padding: 16 },
  warn: { color: '#b45309', marginTop: 12 },             // चेतावनी का रंग
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android Emulator | iOS Simulator |
|---------|------------------|---------------|
| कहाँ चलता है | Windows / Mac / Linux | **सिर्फ Mac** |
| Tool | Android Studio (AVD) | Xcode |
| Type | असली Android OS (x86/ARM image) | Mac पर iOS का simulation (Mac architecture) |
| Camera | Virtual camera मिलता है | ❌ असली camera नहीं |
| Push notifications | Google Play image पर संभव | ❌ ज़्यादातर नहीं (नए Xcode में सीमित) |
| Shortcut (Expo) | `a` | `i` |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Expo Go में चलाना — Xcode बस simulator के लिए चाहिए
npx expo start          # Metro शुरू
# फिर terminal में  i  दबाओ
npx expo run:ios        # native build (dev build) — Xcode ज़रूरी, ios/ folder बनता है
```
CLI way:
```bash
# Bare React Native CLI
cd ios && pod install && cd ..     # CocoaPods dependencies (पहली बार और native lib के बाद)
npx react-native run-ios                        # default simulator
npx react-native run-ios --simulator="iPhone 15" # खास simulator चुनो
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Windows/Linux पर iOS simulator चलाने की कोशिश
✅ Correct: Simulator सिर्फ macOS पर है। Windows पर Expo Go + असली iPhone या EAS Build cloud इस्तेमाल करो।

❌ Mistake 2: Xcode install किया पर Command Line Tools select नहीं किए
✅ Correct: Xcode → Settings → Locations → Command Line Tools में Xcode version चुनो, वरना `xcrun` error आता है।

❌ Mistake 3: CLI project में `pod install` भूल जाना
✅ Correct: नई native library जोड़ने के बाद `cd ios && pod install`।

---

## 🧠 Tricky Interview Question
**Q: Simulator पर आपका push notification test क्यों काम नहीं कर रहा, जबकि Android emulator पर करता है?**

Answer: Remote push के लिए APNs token असली device से मिलता है; iOS simulator पर आमतौर पर remote push token नहीं मिलता (नए Xcode/macOS में सीमित local simulation संभव है, version-dependent)। इसलिए push, camera, biometrics (Face ID simulate हो सकता है) की असली जाँच real device पर करनी चाहिए।

---

## ⚫ Interview Questions + Answers
Q1: iOS Simulator Windows पर चल सकता है?
A1: नहीं, सिर्फ macOS पर (Xcode के साथ)।

Q2: Simulator और Emulator में अंतर?
A2: Simulator host की architecture पर OS की नकल करता है (iOS); Emulator असली hardware को emulate करके असली OS image चलाता है (Android)।

Q3: Expo में simulator कैसे खोलें?
A3: `npx expo start` फिर `i` दबाओ।

Q4: खास iPhone model पर कैसे चलाएँ?
A4: CLI: `npx react-native run-ios --simulator="iPhone 15"`; Xcode में Window → Devices and Simulators से भी।

Q5: Reload / Dev menu का shortcut?
A5: Reload: `R`; Dev menu: `Cmd + D` (या `Ctrl + Cmd + Z`)।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- UI / layout / navigation की तेज़ जाँच
- अलग screen sizes और iOS versions test करना

❌ Avoid when:
- Camera, push, Bluetooth, NFC, असली performance जाँचनी हो
- Payment/UPI flows की final testing

---

## 📊 Visual Diagram
```
 Mac (macOS)
   ├── Xcode ──► iOS Simulator (virtual iPhone)
   └── Terminal: npx expo start
            │  press  i
            ▼
        Metro Bundler ──JS bundle──► Simulator (Expo Go / Dev Build)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Simulator | Mac पर iOS की नकल | iOS का नकली device |
| Xcode | Apple का IDE | Apple का development tool |
| CocoaPods | iOS dependency manager | iOS की libraries manager |
| Expo Go | Expo का sandbox app | Expo का test app |
| Dev Build | अपनी native code वाला build | custom development build |

---

## ⚡ 3-Line Summary
English:
1. iOS Simulator runs a virtual iPhone on a Mac via Xcode.
2. In Expo press `i` after `npx expo start`; in CLI use `npx react-native run-ios`.
3. Test camera, push and payments on a real device.

Hindi:
1. iOS Simulator Mac पर Xcode से virtual iPhone चलाता है।
2. Expo में `npx expo start` के बाद `i`; CLI में `npx react-native run-ios`।
3. Camera, push, payment की जाँच real device पर करो।

---

## ➡️ Next Topic
**18. Running on Real Device** — असली फोन पर चलाना, जहाँ सब hardware features काम करते हैं।
