# 293. Interview Problem: Build a QR Code Scanner
# हिंदी में: QR Code Scanner बनाओ
# Platform: Both ✅ (Android ✅ | iOS ✅) — physical device recommended
# Difficulty: ⭐⭐⭐ Medium | Asked at: Paytm, PhonePe, Google Pay, BharatPe

File: `QRScannerScreen.jsx`.
Target: Expo SDK 52 with `expo-camera` `CameraView` (barcode scanning is built in from SDK 51; check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
Open the camera, detect QR codes in the live preview, and read their text. Show it, and open it only if it is a safe web link.

## 🔵 सरल परिभाषा (Hindi)
Camera खोलो, live preview में QR code पहचानो और उसका text पढ़ो। उसे दिखाओ, और सिर्फ़ तब खोलो जब वो सुरक्षित web link हो।

---

## 🔴 Problem it Solves
Typing UPI IDs, URLs or tickets is slow and error-prone. Scanning is instant: payments (UPI QR), login with QR, ticket check-in, product info.

## 🔴 यह क्यों बना? (Hindi)
UPI ID, URL या ticket हाथ से लिखना धीमा और ग़लती-भरा है। Scan तुरंत होता है: payments (UPI QR), QR से login, ticket check-in, product जानकारी।

---

## 🔴 Problem Statement
Build a scanner that asks for camera permission, scans only QR codes, ignores duplicate scan callbacks (they fire many times per second), shows a result card with "Scan again", confirms before opening a web link, and never opens arbitrary URL schemes automatically.

## 💡 Approach
```
useCameraPermissions() -> null (loading) | {granted:false} -> ask UI | {granted:true} -> camera
CameraView barcodeScannerSettings={{ barcodeTypes: ['qr'] }}
onBarcodeScanned: ref lock (sync, state is too slow) -> setScanned -> validate -> Alert
scanned truthy -> onBarcodeScanned={undefined} (stop listening)
reset: unlock + clear result
```

## 🟢 How it Works — Step by Step
```
Step 1 → Check permission; if not granted show "Allow" button
Step 2 → Render CameraView (back camera, only QR)
Step 3 → onBarcodeScanned fires with { data, type }
Step 4 → A ref lock ignores the repeats that arrive before React updates
Step 5 → If data starts with http(s):// show Alert "Open link?" (Cancel / Open)
Step 6 → "Scan again" resets the lock and the result
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Permission जाँचो; न हो तो "Allow" button दिखाओ
Step 2 → CameraView (पीछे वाला camera, सिर्फ़ QR)
Step 3 → onBarcodeScanned { data, type } के साथ call होता है
Step 4 → Ref lock उन repeat calls को रोकता है जो React update से पहले आ जाते हैं
Step 5 → data http(s):// से शुरू हो तो Alert "Open link?" (Cancel / Open)
Step 6 → "Scan again" lock और result reset करता है
```

---

## 🟡 Real World Example
Paytm / PhonePe / Google Pay "Scan any QR" for UPI payments, Zomato dine-in "scan table QR", WhatsApp Web login, DigiLocker and airline boarding checks.

## 🟡 Real Example Hindi mein
Paytm / PhonePe / Google Pay का UPI के लिए "Scan any QR", Zomato dine-in में table QR scan, WhatsApp Web login, DigiLocker और airline boarding checks।

---

## 💻 Code Example — Basic
```jsx
import React, { useState } from 'react';                         // state
import { View, Text, Pressable } from 'react-native';             // UI
import { CameraView, useCameraPermissions } from 'expo-camera';  // camera

export default function BasicScanner() {
  const [permission, requestPermission] = useCameraPermissions(); // permission hook
  const [result, setResult] = useState(null);                    // scanned text
  if (!permission) return <View />;                              // still loading
  if (!permission.granted)                                       // ask user
    return <Pressable onPress={requestPermission}><Text>Allow camera</Text></Pressable>;
  return (
    <View style={{ flex: 1 }}>
      <CameraView
        style={{ flex: 1 }}                                      // fill screen
        barcodeScannerSettings={{ barcodeTypes: ['qr'] }}        // only QR
        onBarcodeScanned={result ? undefined : ({ data }) => setResult(data)} // stop after first hit
      />
      {result && <Text>{result}</Text>}
    </View>
  );
}
```

## 💻 Code Example — Advanced
From `QRScannerScreen.jsx`:
```jsx
const lock = useRef(false);                                      // sync lock: callback fires many times/sec

const onScan = ({ data, type }) => {
  if (lock.current) return;                                      // ignore duplicates
  lock.current = true;                                           // lock immediately (state is async)
  setScanned({ data, type });
  if (/^https?:\/\//.test(data)) {                               // only web links, never blindly open any scheme
    Alert.alert('Open link?', data, [
      { text: 'Cancel', onPress: reset },
      { text: 'Open', onPress: () => { Linking.openURL(data); reset(); } },
    ]);
  }
};
const reset = () => { lock.current = false; setScanned(null); };
```
UPI QR codes start with `upi://pay?...`. This sample shows them as text on purpose; to support payments parse the query params (`pa`, `pn`, `am`), validate them and hand over to a UPI intent only after user confirmation. Treat all QR content as untrusted input.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Permission | `CAMERA` runtime permission | `NSCameraUsageDescription` string is mandatory |
| Scanner engine | Google ML Kit / ZXing (via Expo) | Apple Vision / AVFoundation |
| Expo Go | Works | Works |
| Barcode types | Large list | Large list (a few differ) |
| Torch / focus | Behaviour varies by device | More uniform |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-camera
// app.json plugin (text shown in iOS permission dialog):
// "plugins": [["expo-camera", { "cameraPermission": "Allow $(PRODUCT_NAME) to scan QR codes" }]]
```
CLI way:
```jsx
// npm i react-native-vision-camera  (useCodeScanner) or react-native-camera-kit
// Info.plist: NSCameraUsageDescription ; AndroidManifest: <uses-permission android:name="android.permission.CAMERA"/>
// cd ios && pod install ; rebuild
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Handling every `onBarcodeScanned` call (dozens per second) -> many alerts / navigations.
✅ Correct: Ref lock + `onBarcodeScanned={undefined}` after a hit.

❌ Mistake 2: Using `useState` as the lock (async; duplicates slip through).
✅ Correct: `useRef` for the synchronous lock.

❌ Mistake 3: `Linking.openURL(data)` for any content (`tel:`, `intent:`, `file:`).
✅ Correct: Allow-list `http(s)` and ask the user.

❌ Mistake 4: Missing iOS usage description -> app crash / App Store rejection.
✅ Correct: Add `cameraPermission` text.

---

## 🧠 Tricky Interview Question
You set `scanned` in state and hide the handler when it is truthy, yet two alerts still appear. Why?

Answer: State updates are asynchronous and batched, so the camera may call `onBarcodeScanned` again before the re-render removes the handler. A `useRef` lock changes immediately and blocks the second call.

---

## ⚫ Interview Questions + Answers
Q1: Why is `CameraView` used instead of `expo-barcode-scanner`?
A1: Barcode scanning moved into `expo-camera` (SDK 51+); the old package was deprecated/removed.

Q2: How to scan only a region?
A2: Library support is limited; commonly you validate the corner points, or use Vision Camera frame processors.

Q3: How do you handle a denied permission?
A3: Show an explanation and `Linking.openSettings()` when `canAskAgain` is false.

Q4: Security risks?
A4: Malicious links, phishing UPI requests; validate the scheme/host and always confirm.

Q5: Torch / front camera?
A5: `enableTorch` prop and `facing="front" | "back"` on `CameraView`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Payments, tickets, pairing devices, table check-in

❌ Avoid when:
- A short code can be typed, or camera permission would be unexpected for the feature

---

## 📊 Visual Diagram
```
 ┌──────────────────────┐
 │   CameraView         │
 │     ┌────────┐       │   onBarcodeScanned({data})
 │     │  QR    │       │ ─────────────────────────┐
 │     └────────┘       │                          ▼
 │                      │              lock? ──yes──► ignore
 │ ┌──────────────────┐ │                │no
 │ │ result + [Again] │ │                ▼
 │ └──────────────────┘ │       setScanned + validate + Alert
 └──────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| QR code | 2D barcode | QR कोड |
| CameraView | Expo camera component | Camera component |
| Permission | User consent | अनुमति |
| Debounce / lock | Ignore repeats | दोहराव रोकना |
| UPI | India's instant payment system | UPI भुगतान |

---

## ⚡ 3-Line Summary
English: Ask camera permission, render `CameraView` with QR-only settings.
Use a ref lock to process a scan once and allow "Scan again".
Validate content before opening it.

Hindi: Camera permission माँगें, सिर्फ़ QR वाली settings के साथ `CameraView` दिखाएँ।
Ref lock से एक scan को एक बार ही process करें और "Scan again" दें।
खोलने से पहले content जाँचें।

---

## ✅ What was verified
Under react-native-web + jsdom with `expo-camera` mocked: the screen renders the camera component and two rapid scan callbacks produce only the first result (lock works). Real camera, permission dialogs, decoding and `Linking`/`Alert` flows were not run (native, needs a device).

---

## ➡️ Next Topic
294. Build Dark Mode Toggle — a smaller UI-state problem; later, 296 wraps a permission + device API in a reusable hook.
