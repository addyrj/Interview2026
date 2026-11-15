# 106. Barcode + QR Scanner
# हिंदी में: Barcode और QR Code Scanner
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 54 (React Native 0.81) ke hisaab se likha gaya hai — (check current docs — APIs change between SDKs). `expo-camera` ka `CameraView` + `onBarcodeScanned` SDK 51+ me available hai. Purana `expo-barcode-scanner` deprecated/removed hai.

---

## 🔵 Simple Definition (English)
A **barcode/QR scanner** uses the phone camera to read a code (QR, EAN-13, Code128 etc.) and gives you the text inside it as a string. In Expo you do this with `CameraView` from `expo-camera` and its `onBarcodeScanned` callback.

## 🔵 सरल परिभाषा (Hindi)
**Barcode/QR scanner** phone के camera से कोई code (QR, EAN-13, Code128 आदि) पढ़ता है और उसके अंदर का text आपको string में देता है। Expo में यह `expo-camera` के `CameraView` और उसके `onBarcodeScanned` callback से होता है।

---

## 🔴 Problem it Solves
```
BEFORE:
❌ User ko UPI ID / amount haath se type karna padta tha
❌ Product barcode manually search karna padta tha
❌ Native camera + ML Kit / AVFoundation ka alag code (Kotlin + Swift)
❌ Third-party scanner apps kholne padte the, phir result wapas laana mushkil
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
❌ User को UPI ID / amount हाथ से type करना पड़ता था
❌ Product barcode manually search करना पड़ता था
❌ Android (ML Kit) और iOS (AVFoundation) का अलग native code
✅ अब: एक component, दोनों platforms, app के अंदर ही scan
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Install expo-camera (npx expo install expo-camera)
Step 2 → Ask camera permission (useCameraPermissions)
Step 3 → Render <CameraView barcodeScannerSettings={{ barcodeTypes: ['qr'] }} />
Step 4 → Native layer (Android ML Kit / iOS AVFoundation) detects code in frames
Step 5 → onBarcodeScanned({ type, data }) fires with the decoded string
Step 6 → You set a "scanned" flag so the callback doesn't fire 30 times/second
Step 7 → Handle data (open payment screen, add product to cart...)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → expo-camera install करो
Step 2 → Camera permission माँगो (useCameraPermissions)
Step 3 → <CameraView> render करो और barcodeTypes बताओ
Step 4 → Native layer हर frame में code detect करता है
Step 5 → onBarcodeScanned({ type, data }) में decoded string आती है
Step 6 → "scanned" flag लगाओ ताकि callback बार-बार न चले
Step 7 → data को handle करो (payment screen, cart आदि)
```

---

## 🟡 Real World Example
**Paytm / PhonePe / Google Pay** "Scan any QR" screen: camera opens, UPI QR (`upi://pay?pa=shop@bank&pn=Shop&am=100`) is decoded and the pay screen opens with the amount pre-filled. **Zomato/Swiggy Instamart** delivery partners scan parcel barcodes; **Blinkit** pickers scan product EAN codes.

## 🟡 Real Example Hindi mein
**Paytm / PhonePe / Google Pay** का "Scan any QR" screen: camera खुलता है, UPI QR (`upi://pay?pa=shop@bank&am=100`) decode होता है और payment screen में amount पहले से भरा आता है। **Swiggy Instamart / Blinkit** के delivery/picker लोग parcel और product के barcode scan करते हैं।

---

## 💻 Code Example — Basic
```jsx
// Basic QR scanner - Expo SDK 54, works on Android + iOS
import React, { useState } from 'react';                         // React + state hook
import { View, Text, Button, StyleSheet, Alert } from 'react-native'; // core UI pieces
import { CameraView, useCameraPermissions } from 'expo-camera';  // camera component + permission hook

export default function BasicScanner() {
  const [permission, requestPermission] = useCameraPermissions(); // permission object + request fn
  const [scanned, setScanned] = useState(false);                  // true after first successful scan

  if (!permission) return <View />;                               // permission still loading -> blank

  if (!permission.granted) {                                      // user has not allowed camera yet
    return (
      <View style={styles.center}>
        <Text>Camera permission chahiye</Text>
        <Button title="Allow Camera" onPress={requestPermission} />
      </View>
    );
  }

  // called by the camera whenever a code is detected
  const onScan = ({ type, data }) => {
    if (scanned) return;                                          // ignore repeated callbacks
    setScanned(true);                                             // lock scanning
    Alert.alert('Scanned', `${type}\n${data}`, [                  // show decoded value
      { text: 'Scan again', onPress: () => setScanned(false) },   // unlock to scan another
    ]);
  };

  return (
    <View style={styles.container}>
      <CameraView
        style={StyleSheet.absoluteFill}                           // camera fills the whole screen
        facing="back"                                             // use back camera
        barcodeScannerSettings={{ barcodeTypes: ['qr', 'ean13'] }} // only detect these formats
        onBarcodeScanned={scanned ? undefined : onScan}           // undefined stops scanning
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },                                         // full screen
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' }, // center content
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: Paytm-style UPI QR scanner with torch, overlay, parsing, error handling
import React, { useCallback, useRef, useState } from 'react';      // hooks
import { View, Text, Pressable, StyleSheet, Platform, Linking } from 'react-native'; // UI + Linking
import { CameraView, useCameraPermissions } from 'expo-camera';    // camera API
import { useIsFocused } from '@react-navigation/native';           // only scan when screen focused

// parse "upi://pay?pa=x@bank&pn=Name&am=100" into an object
export function parseUpi(data) {
  if (typeof data !== 'string' || !data.startsWith('upi://pay')) return null; // not a UPI QR
  const query = data.split('?')[1] || '';                          // part after "?"
  const out = {};                                                  // result object
  query.split('&').forEach((pair) => {                             // each key=value
    const [k, v = ''] = pair.split('=');                           // split pair
    out[k] = decodeURIComponent(v);                                // decode %20 etc.
  });
  return out.pa ? out : null;                                      // pa (payee address) is mandatory
}

export default function UpiScanner({ onPay }) {
  const [permission, requestPermission] = useCameraPermissions();  // permission state
  const [torch, setTorch] = useState(false);                       // flashlight toggle
  const [error, setError] = useState('');                          // user-facing error text
  const lockRef = useRef(false);                                   // ref lock: avoids duplicate callbacks (state is async)
  const isFocused = useIsFocused();                                // false when another screen is on top

  const handleScan = useCallback(({ data }) => {
    if (lockRef.current) return;                                   // already handling a scan
    lockRef.current = true;                                        // lock immediately (sync)
    const upi = parseUpi(data);                                    // try to parse
    if (!upi) {                                                    // invalid / non-UPI QR
      setError('Ye UPI QR nahi hai');                              // show message
      setTimeout(() => { lockRef.current = false; setError(''); }, 1500); // retry after 1.5s
      return;
    }
    onPay?.(upi);                                                  // hand data to payment screen
  }, [onPay]);

  if (!permission) return null;                                    // loading
  if (!permission.granted) {
    return (
      <View style={styles.center}>
        <Text style={styles.msg}>Scan karne ke liye camera allow karo</Text>
        <Pressable style={styles.btn} onPress={requestPermission}>
          <Text style={styles.btnText}>Allow</Text>
        </Pressable>
        {!permission.canAskAgain && (                              // user chose "don't ask again"
          <Pressable onPress={() => Linking.openSettings()}>       // open app settings
            <Text style={styles.link}>Open Settings</Text>
          </Pressable>
        )}
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {isFocused && (                                              // unmount camera when screen not focused (saves battery)
        <CameraView
          style={StyleSheet.absoluteFill}
          facing="back"
          enableTorch={torch}                                      // flashlight on/off
          barcodeScannerSettings={{ barcodeTypes: ['qr'] }}        // only QR
          onBarcodeScanned={handleScan}                            // decode callback
          onMountError={(e) => setError(e.message)}                // camera failed to start
        />
      )}
      <View style={styles.frame} pointerEvents="none" />           {/* square scan frame overlay */}
      {!!error && <Text style={styles.error}>{error}</Text>}
      <Pressable style={styles.torch} onPress={() => setTorch((t) => !t)}>
        <Text style={styles.btnText}>{torch ? 'Torch OFF' : 'Torch ON'}</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24 },
  msg: { fontSize: 16, marginBottom: 12, textAlign: 'center' },
  btn: { backgroundColor: '#00baf2', paddingHorizontal: 24, paddingVertical: 10, borderRadius: 8 },
  btnText: { color: '#fff', fontWeight: '700' },
  link: { color: '#00baf2', marginTop: 16 },
  frame: {
    position: 'absolute', top: '30%', alignSelf: 'center',        // centered square
    width: 240, height: 240, borderWidth: 3, borderColor: '#fff', borderRadius: 16,
  },
  error: { position: 'absolute', bottom: 140, alignSelf: 'center', color: '#fff',
    backgroundColor: 'rgba(200,0,0,0.8)', padding: 8, borderRadius: 6 },
  torch: { position: 'absolute', bottom: 60, alignSelf: 'center',
    backgroundColor: 'rgba(0,0,0,0.6)', padding: 12, borderRadius: 24,
    ...Platform.select({ android: { elevation: 4 }, ios: {} }) },  // Android shadow only
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Permission | `CAMERA` permission dialog | `NSCameraUsageDescription` in Info.plist (expo-camera plugin adds it) |
| Detection engine | Google ML Kit | AVFoundation (Apple Vision) |
| Supported formats | Slightly different list (e.g. `itf14` etc.) — check docs | Different subset (e.g. `codabar` only newer iOS) |
| Torch | `enableTorch` works | `enableTorch` works |
| Expo Go | Works (Expo Go has camera) | Works |
| Emulator | Virtual scene camera only | Simulator has NO camera |
| Scan region | Whole preview scanned | Whole preview scanned (no `rectOfInterest` prop in CameraView) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Install and use expo-camera
// npx expo install expo-camera
import { CameraView, useCameraPermissions } from 'expo-camera'; // permission plugin auto-configured via app.json
// app.json: { "expo": { "plugins": [["expo-camera", { "cameraPermission": "Allow $(PRODUCT_NAME) to scan QR codes" }]] } }
```
CLI way:
```jsx
// Bare RN CLI: use react-native-vision-camera (+ frame processor/code scanner)
// npm i react-native-vision-camera && cd ios && pod install
// Add CAMERA to AndroidManifest.xml and NSCameraUsageDescription to Info.plist manually
import { Camera, useCodeScanner } from 'react-native-vision-camera'; // VisionCamera v3/v4 API
// (expo-camera also works in bare apps after installing expo modules)
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Not locking after first scan — callback fires many times per second, opens screen 20 times.
✅ **Correct:** Use a `useRef` lock or pass `onBarcodeScanned={scanned ? undefined : handler}`.

❌ **Mistake 2:** Not specifying `barcodeTypes` — slow, and random formats trigger false scans.
✅ **Correct:** `barcodeScannerSettings={{ barcodeTypes: ['qr'] }}`.

❌ **Mistake 3:** Using deprecated `expo-barcode-scanner` / `BarCodeScanner`.
✅ **Correct:** Use `CameraView` from `expo-camera` (SDK 51+).

❌ **Mistake 4:** Keeping camera mounted on a hidden tab/screen — drains battery.
✅ **Correct:** Render `CameraView` only when `useIsFocused()` is true.

---

## 🧠 Tricky Interview Question
**Q: You set `setScanned(true)` inside `onBarcodeScanned` but the alert still shows twice. Why?**

**Answer:** `setState` is asynchronous/batched. Before the re-render happens, the camera already fired a second callback with the old `scanned === false` closure. Fix with a `useRef` flag (updates synchronously) — `if (lockRef.current) return; lockRef.current = true;`.

---

## ⚫ Interview Questions + Answers

**Q1: Which package scans QR codes in modern Expo?**
A1: `expo-camera` — `CameraView` with `onBarcodeScanned` and `barcodeScannerSettings`. `expo-barcode-scanner` is deprecated.

**Q2: How do you scan only QR codes?**
A2: `barcodeScannerSettings={{ barcodeTypes: ['qr'] }}`.

**Q3: How do you handle denied permission?**
A3: Check `permission.granted`; if `canAskAgain` is false, show a message and call `Linking.openSettings()`.

**Q4: How to scan a QR from a gallery image?**
A4: `CameraView.scanFromURLAsync(uri, ['qr'])` is available in expo-camera (check docs for your SDK); pick the image with `expo-image-picker`.

**Q5: Scanner in CLI app without Expo?**
A5: `react-native-vision-camera` with `useCodeScanner`, or install expo modules in the bare app and use `expo-camera`.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- UPI / payment QR, ticket check-in, product lookup, login via QR (WhatsApp Web style)

❌ **Avoid when:**
- You need advanced vision (ML, OCR, frame processors) — use VisionCamera
- Only a link needs opening — a deep link might be simpler

---

## 📊 Visual Diagram
```
 Camera frames ──► Native detector (ML Kit / AVFoundation)
                          │
                          ▼
              onBarcodeScanned({type, data})
                          │
              lock? ──yes──► ignore
                │no
                ▼
        parse data ──invalid──► show error, unlock after 1.5s
                │valid
                ▼
        navigate / pay / add to cart
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| QR code | 2D matrix code | 2D चौकोर code |
| EAN-13 | Retail product barcode | दुकान का product barcode |
| CameraView | expo-camera component | Camera दिखाने वाला component |
| barcodeTypes | Formats to detect | कौन से code detect करने हैं |
| Torch | Camera flashlight | कैमरे की टॉर्च |
| Permission | User consent | उपयोगकर्ता की अनुमति |

---

## ⚡ 3-Line Summary
**English:**
1. Use `CameraView` from `expo-camera` with `onBarcodeScanned`.
2. Ask permission, restrict `barcodeTypes`, and lock after the first scan.
3. Stop the camera when the screen is not focused.

**Hindi:**
1. `expo-camera` का `CameraView` और `onBarcodeScanned` use करो।
2. Permission माँगो, `barcodeTypes` सीमित रखो और पहले scan के बाद lock लगाओ।
3. Screen focus में न हो तो camera बंद रखो।

---

## ➡️ Next Topic
**107. Audio + Video Playback** — scan के बाद अब media (audio/video) चलाना सीखेंगे।
