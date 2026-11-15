# 16. Running on Android Emulator
# हिंदी में: Android Emulator पर App चलाना
# Platform: Android ✅ | iOS ❌ | Android only

> Target: Expo SDK 52 / React Native 0.76. Expo SDK NN (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
Running on an **Android emulator** means starting a virtual Android phone (AVD) on your computer, installing your app on it, and connecting it to Metro so you can test without a physical device.

## 🔵 सरल परिभाषा (Hindi)
**Android emulator** पर चलाने का मतलब है अपने computer पर एक virtual Android फ़ोन (AVD) चालू करना, उसमें अपना app install करना और Metro से जोड़ना, ताकि बिना असली फ़ोन के test हो सके।

---

## 🔴 Problem it Solves
```
❌ Don't own many Android phones (sizes, versions)
❌ Need to test Android 8 and Android 15 behaviour
❌ Need quick reset of app data / permissions
❌ Want screenshots, location, network throttle controls
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ कई Android phones (sizes, versions) हमारे पास नहीं होते
❌ Android 8 और Android 15 का behaviour test करना है
❌ App data / permissions जल्दी reset करना है
❌ Screenshots, location, network throttle controls चाहिए
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Android Studio -> Device Manager -> Create/Start an AVD

Step 2 → Verify:     adb devices   -> "emulator-5554   device"

Step 3 → Expo Go:    npx expo start  -> press "a"
         (Expo installs Expo Go on the emulator if missing and opens your app)

Step 4 → Dev build:  npx expo run:android
         CLI:        npx react-native run-android

Step 5 → App loads JS from Metro (emulator reaches host at 10.0.2.2:8081
         or via adb reverse)

Step 6 → Dev menu: Ctrl+M (Windows/Linux) or Cmd+M (Mac)
         Reload: press "r" twice, or "r" in the Metro terminal

Step 7 → Logs:  adb logcat *:E  (errors)  or the Metro terminal
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Android Studio -> Device Manager -> AVD बनाएँ/चालू करें
Step 2 → जाँचें: adb devices -> "emulator-5554   device"
Step 3 → Expo Go: npx expo start -> "a" दबाएँ
         (Expo Go न हो तो खुद install कर देता है और app खोलता है)
Step 4 → Dev build: npx expo run:android
         CLI: npx react-native run-android
Step 5 → App, Metro से JS लेता है (emulator host को 10.0.2.2:8081 या adb reverse से पाता है)
Step 6 → Dev menu: Ctrl+M (Windows/Linux) या Cmd+M (Mac)
         Reload: "r" दो बार दबाएँ, या Metro terminal में "r"
Step 7 → Logs: adb logcat *:E (errors) या Metro terminal
```

### Screen descriptions (what you will see)
- **Emulator window:** a phone frame with a floating toolbar on the right: power, volume, rotate, screenshot, zoom and a "..." button for Extended controls (Location, Cellular, Battery, Camera).
- **Dev menu (Cmd/Ctrl+M):** a list: Reload, Open Debugger, Show Element Inspector, Show Perf Monitor, Toggle Fast Refresh.
- **Red error screen:** a full-screen red page with the error message and stack; "Dismiss" and "Reload" buttons at the bottom.

---

## 🟡 Real World Example
A developer for a **Swiggy-like** app tests the delivery-tracking screen with fake GPS. In emulator Extended controls -> Location she sets a route in Bengaluru and watches the map marker move, without leaving her desk.

## 🟡 Real Example Hindi mein
**Swiggy जैसे** app की developer delivery-tracking screen को fake GPS से test करती है। Emulator के Extended controls -> Location में वह Bengaluru का route सेट करती है और अपनी कुर्सी से ही map marker को चलता देखती है।

---

## 💻 Code Example — Basic

```bash
# Basic: run on the Android emulator (each line commented)
emulator -list-avds              # list available virtual devices
emulator -avd Pixel_6_API_35 &   # boot one (name from the list above); & = background (Mac/Linux)
adb devices                      # confirm it shows as "device"
npx expo start                   # start Metro (Expo)
# then press "a" in the terminal to open the app on the emulator
```

## 💻 Code Example — Advanced

```jsx
// Advanced: a screen that detects emulator/real device, handles Android back button
// and uses the right localhost for API calls on the Android emulator.
import React, { useEffect } from 'react'; // React
import { Alert, BackHandler, Platform, StyleSheet, Text, View } from 'react-native'; // core
import * as Device from 'expo-device'; // npx expo install expo-device

// On Android emulator "localhost" is the emulator itself; host machine is 10.0.2.2
const HOST = Platform.OS === 'android' ? '10.0.2.2' : 'localhost'; // pick the right host
const API = `http://${HOST}:3000`; // local dev API (HTTP => needs cleartext allowed in dev)

export default function EmulatorInfo() {
  useEffect(() => {
    // Handle hardware back button (Android only)
    const sub = BackHandler.addEventListener('hardwareBackPress', () => {
      Alert.alert('Exit?', 'Close the app?', [
        { text: 'No', style: 'cancel' }, // stay
        { text: 'Yes', onPress: () => BackHandler.exitApp() }, // quit
      ]);
      return true; // true = we handled it
    });
    return () => sub.remove(); // cleanup listener
  }, []);

  return (
    <View style={styles.box}>
      {/* Device.isDevice is false on emulators/simulators */}
      <Text>Real device? {String(Device.isDevice)}</Text>
      <Text>Model: {Device.modelName ?? 'unknown'}</Text>
      <Text>API base: {API}</Text>
    </View>
  );
}

// Styles
const styles = StyleSheet.create({
  box: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 8 }, // centre
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android Emulator | iOS Simulator |
|---------|------------------|---------------|
| Host machine address | `10.0.2.2` | `localhost` |
| Dev menu | Ctrl/Cmd+M | Cmd+D |
| Start from Expo | press `a` | press `i` |
| Fidelity | Runs a real Android image | Runs iOS code on Mac, not a real iPhone |
| Push notifications | Works with Google Play images | Limited in simulator (needs device for APNs, with exceptions on recent Xcode) |
| Platform | Win/Mac/Linux | Mac only |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx expo start            # press "a": installs Expo Go and opens project
npx expo run:android      # build a development build locally
```
CLI way:
```bash
npx react-native start             # terminal 1
npx react-native run-android       # terminal 2: build, install, launch
npx react-native run-android --mode release   # test a release build (newer CLI: --mode)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Calling `http://localhost:3000` from the emulator.
✅ Correct: use `http://10.0.2.2:3000` (or `adb reverse tcp:3000 tcp:3000`).

❌ Mistake 2: Emulator is slow because of no hardware acceleration.
✅ Correct: enable virtualization (BIOS / WHPX / Hypervisor.Framework) and use a matching CPU image.

❌ Mistake 3: Cleartext `http://` blocked in release builds.
✅ Correct: use HTTPS in production; for dev builds allow cleartext via `expo-build-properties` (`android.usesCleartextTraffic: true`).

❌ Mistake 4: Multiple devices connected and run-android picks the wrong one.
✅ Correct: `adb devices` then `--deviceId`.

---

## 🧠 Tricky Interview Question
**Q:** "Your API works in the iOS simulator at `http://localhost:3000` but fails in the Android emulator. Same code. Why?"

Answer: In the Android emulator `localhost` refers to the emulator's own loopback, not your computer. Use `10.0.2.2` or `adb reverse`. In the iOS simulator `localhost` is the Mac, so it works there.

---

## ⚫ Interview Questions + Answers
Q1: How to open the dev menu on an emulator?
A1: Ctrl+M (Win/Linux) or Cmd+M (Mac), or `adb shell input keyevent 82`.

Q2: How to see logs?
A2: `adb logcat` or Android Studio Logcat.

Q3: How to wipe app data?
A3: Long-press app -> App info -> Storage -> Clear, or `adb shell pm clear <package>`.

Q4: What does `adb reverse` do?
A4: Forwards a device port to the host port, so `localhost:PORT` on the device reaches your computer.

Q5: Emulator vs real device for performance testing?
A5: Always final-check on a real mid-range device; emulators are faster/slower in different ways.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Layout testing across screens and API levels
- Simulating GPS, network, battery

❌ Avoid when:
- Testing performance, camera, biometrics, BLE (use a real device)

---

## 📊 Visual Diagram
```
 Computer                         Emulator (AVD)
 ┌──────────────┐  10.0.2.2:8081 ┌──────────────┐
 │ Metro :8081  │◄───────────────│ Your app     │
 │ API  :3000   │◄── adb reverse │ (localhost)  │
 └──────────────┘                └──────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| AVD | Android Virtual Device | virtual Android फ़ोन |
| 10.0.2.2 | Emulator alias for host | emulator से computer का पता |
| adb reverse | Port forward device->host | device से computer तक port |
| Logcat | Android log stream | Android logs |
| Dev menu | Debug options menu | debug options का menu |
| Cold boot | Fresh emulator start | emulator नए सिरे से चालू |

---

## ⚡ 3-Line Summary
English: Start an AVD, check adb devices, then press a or run run-android.
Use 10.0.2.2 or adb reverse to reach your computer.
Final-test on real devices.

Hindi: AVD चालू करें, adb devices जाँचें, फिर "a" दबाएँ या run-android चलाएँ।
Computer तक पहुँचने के लिए 10.0.2.2 या adb reverse use करें।
अंतिम test असली devices पर करें।

---

## ➡️ Next Topic
**17. Running on iOS Simulator** — the same flow on Mac with Xcode Simulator.

---
