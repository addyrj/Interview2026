# 92. Camera — react-native-vision-camera
# हिंदी में: Camera — react-native-vision-camera (हाई-परफॉर्मेंस कैमरा)
# Platform: Android ✅ | iOS ✅ | Both ✅ (Expo Go ❌ — dev build चाहिए)

> Target: Expo SDK 52 (React Native 0.76) + react-native-vision-camera v4 (check current docs — APIs change between SDKs and between Vision Camera majors).

---

## 🔵 Simple Definition (English)
**react-native-vision-camera** is a fast, native camera library. It gives live preview, photo/video capture, QR/barcode scanning and **frame processors** (run JS/native code on every camera frame) — much more powerful than `expo-camera`. It needs native code, so it does NOT run in Expo Go.

## 🔵 सरल परिभाषा (Hindi)
**react-native-vision-camera** एक तेज़ native camera library है। इससे live preview, photo/video, QR/barcode scan और **frame processors** (हर camera frame पर code चलाना) मिलते हैं — `expo-camera` से ज़्यादा powerful। यह native code use करती है, इसलिए Expo Go में नहीं चलती।

---

## 🔴 Problem it Solves
```
expo-camera ki limits:
❌ Frame-by-frame processing (face detect, OCR live) mushkil
❌ Fine control: format, fps, HDR, zoom, focus, low-light
❌ Multiple cameras / lens switching limited
❌ Heavy scanning (QR + ML) slow

VisionCamera:
✅ Native speed, 60 fps+ preview
✅ Frame Processors (worklets, react-native-worklets-core)
✅ useCameraDevice / useCameraFormat se full control
✅ Code scanner built in (useCodeScanner)
```

## 🔴 यह क्यों बना? (Hindi)
```
Basic camera libraries सिर्फ फोटो खींचती थीं।
Live face detection, OCR, AR जैसे काम हर frame पर करने पड़ते हैं।
VisionCamera frame processors से native speed पर ये काम JS से संभव करती है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npm i react-native-vision-camera (Expo: npx expo install + config plugin)
Step 2 → Permissions config: Android CAMERA, iOS NSCameraUsageDescription
Step 3 → Camera.requestCameraPermission() (ya useCameraPermission hook)
Step 4 → useCameraDevice('back') se device lo
Step 5 → <Camera device={device} isActive photo /> render karo
Step 6 → ref.current.takePhoto() → file path milta hai
Step 7 → (Optional) frame processor / code scanner attach karo
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Library install + config plugin।
Step 2 → Permission text (iOS Info.plist / Android manifest) डालें।
Step 3 → useCameraPermission से user से permission माँगें।
Step 4 → useCameraDevice('back') से पीछे का camera चुनें।
Step 5 → <Camera /> render करें, ref से takePhoto() बुलाएँ।
Step 6 → File path मिलता है — उसे Image में दिखाएँ या upload करें।
```

---

## 🟡 Real World Example
**Paytm / PhonePe QR scanner:** the "Scan & Pay" screen opens the camera, detects a UPI QR within milliseconds and jumps to the payment screen. This is `useCodeScanner({ codeTypes: ['qr'] })`. **Zomato** uses live camera for bill/ID document capture; an app doing live OCR (PAN card reading) uses a frame processor.

## 🟡 Real Example Hindi mein
**Paytm QR scanner:** "Scan & Pay" खुलते ही camera चालू, UPI QR millisecond में पकड़ता है और payment screen खुलती है — यह `useCodeScanner` से होता है। PAN card live पढ़ने वाले apps frame processor use करते हैं।

---

## 💻 Code Example — Basic
```jsx
// PhotoScreen.jsx — permission + preview + takePhoto
import React, { useRef, useState } from 'react';              // React + hooks
import { View, Text, Pressable, Image, StyleSheet, Linking } from 'react-native'; // RN UI
import { Camera, useCameraDevice, useCameraPermission } from 'react-native-vision-camera'; // v4 API

export default function PhotoScreen() {
  const { hasPermission, requestPermission } = useCameraPermission(); // permission hook
  const device = useCameraDevice('back');                      // back camera (null agar nahi mila)
  const camera = useRef(null);                                 // Camera ref (takePhoto ke liye)
  const [photoPath, setPhotoPath] = useState(null);            // clicked photo ka path

  if (!hasPermission) {                                        // permission nahi hai
    return (
      <View style={styles.center}>
        <Text>Camera permission chahiye</Text>
        <Pressable onPress={requestPermission}><Text style={styles.btn}>Allow</Text></Pressable>
      </View>
    );
  }
  if (device == null) return <Text>No camera found</Text>;     // simulator pe aksar null

  const capture = async () => {
    const photo = await camera.current.takePhoto({ flash: 'off' }); // photo.path = file path
    setPhotoPath('file://' + photo.path);                      // Image ke liye file:// prefix
  };

  if (photoPath) return <Image source={{ uri: photoPath }} style={StyleSheet.absoluteFill} />; // preview

  return (
    <View style={{ flex: 1 }}>
      <Camera ref={camera} style={StyleSheet.absoluteFill} device={device} isActive={true} photo={true} />
      <Pressable style={styles.shutter} onPress={capture} />   {/* shutter button */}
    </View>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' }, // center layout
  btn: { color: 'blue', marginTop: 12 },                       // allow button
  shutter: { position: 'absolute', bottom: 40, alignSelf: 'center', width: 70, height: 70, borderRadius: 35, backgroundColor: '#fff' }, // round button
});
```

## 💻 Code Example — Advanced
```jsx
// ScannerScreen.jsx — QR scanner + app-state aware + torch + error handling
import React, { useCallback, useState } from 'react';
import { View, Text, StyleSheet, Alert, Platform, Pressable } from 'react-native';
import { useIsFocused } from '@react-navigation/native';       // screen focus
import { Camera, useCameraDevice, useCodeScanner, useCameraPermission } from 'react-native-vision-camera';
import { useAppState } from '@react-native-community/hooks';   // foreground state (npm i)

export default function ScannerScreen({ navigation }) {
  const { hasPermission, requestPermission } = useCameraPermission(); // permission
  const device = useCameraDevice('back');                      // back camera
  const isFocused = useIsFocused();                            // is screen visible?
  const appState = useAppState();                              // 'active' | 'background'
  const [torch, setTorch] = useState('off');                   // torch toggle

  // Camera sirf tab active jab screen focused + app foreground (battery bachao)
  const isActive = isFocused && appState === 'active';

  const onCodeScanned = useCallback((codes) => {               // har detection par
    const value = codes[0]?.value;                             // pehla QR value
    if (!value) return;                                        // empty ignore
    if (value.startsWith('upi://')) {                          // UPI QR check
      navigation.navigate('Pay', { upi: value });              // payment screen
    } else {
      Alert.alert('Unknown QR', value);                        // unsupported QR
    }
  }, [navigation]);

  const codeScanner = useCodeScanner({
    codeTypes: ['qr', 'ean-13'],                               // jo formats chahiye
    onCodeScanned,                                             // callback
  });

  if (!hasPermission) {
    requestPermission();                                       // pehli baar prompt
    return <Text>Permission required</Text>;
  }
  if (!device) return <Text>Camera unavailable</Text>;

  return (
    <View style={{ flex: 1 }}>
      <Camera
        style={StyleSheet.absoluteFill}
        device={device}
        isActive={isActive}                                    // false = camera band
        codeScanner={codeScanner}                              // scanner attach
        torch={device.hasTorch ? torch : 'off'}                // torch sirf jahan support ho
        onError={(e) => console.warn('Camera error', e.code)}  // CameraRuntimeError
      />
      {device.hasTorch && (
        <Pressable style={styles.torch} onPress={() => setTorch((t) => (t === 'off' ? 'on' : 'off'))}>
          <Text>{Platform.OS === 'ios' ? 'Torch' : 'Flash'}</Text>
        </Pressable>
      )}
    </View>
  );
}
const styles = StyleSheet.create({ torch: { position: 'absolute', top: 60, right: 20, padding: 12, backgroundColor: '#fff' } });
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Permission | `android.permission.CAMERA` | `NSCameraUsageDescription` (Info.plist) |
| Microphone (video) | `RECORD_AUDIO` | `NSMicrophoneUsageDescription` |
| Photo path | `/data/user/0/.../cache/mrousavy...jpg` | `/var/mobile/.../tmp/...jpg` |
| Simulator | Emulator me virtual camera limited | Simulator me camera nahi (device chahiye) |
| Frame processors | Needs `react-native-worklets-core` | Same |
| Permission denied twice | "Don't ask again" → Settings | Sirf ek baar prompt → Settings |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install react-native-vision-camera
// app.json plugins (check current docs for exact options):
// ["react-native-vision-camera", { "cameraPermissionText": "Scan QR ke liye camera chahiye" }]
// Expo Go me NAHI chalega: npx expo prebuild && npx expo run:android  (ya EAS dev build)
```
CLI way:
```jsx
// npm i react-native-vision-camera
// iOS: Info.plist me NSCameraUsageDescription, cd ios && pod install
// Android: AndroidManifest.xml me <uses-permission android:name="android.permission.CAMERA" />
// npx react-native run-android / run-ios
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Expo Go me chalane ki koshish.
✅ Correct: development build (`expo run:*` ya EAS).

❌ Mistake 2: `isActive` hamesha `true` rakhna — background me bhi camera on, battery drain.
✅ Correct: `isActive = isFocused && appState === 'active'`.

❌ Mistake 3: iOS me `NSCameraUsageDescription` na dalna — app crash.
✅ Correct: Info.plist / config plugin me text daalo.

❌ Mistake 4: `photo={true}` prop bhool jana, phir `takePhoto()` error deta hai.
✅ Correct: `<Camera photo />` jab photo lena ho (video ke liye `video`).

❌ Mistake 5: Photo path ko `file://` ke bina Image me dena (iOS/Android).
✅ Correct: `'file://' + photo.path`.

---

## 🧠 Tricky Interview Question
```jsx
const device = useCameraDevice('back');
return <Camera device={device} isActive photo />;
```
Ye iOS simulator par crash/blank kyu hota hai?

Answer: Simulator me physical camera nahi hota, to `device` **`undefined/null`** aata hai aur `<Camera device={null}>` error deta hai. Hamesha `if (!device)` guard lagao aur real device par test karo.

---

## ⚫ Interview Questions + Answers
Q1: VisionCamera vs expo-camera?
A1: VisionCamera = zyada control + frame processors + performance, dev build zaroori. expo-camera = easy, Expo Go me chalta hai, basic features.

Q2: Frame processor kya hai?
A2: Ek worklet function jo har camera frame par native thread par chalta hai (face detect, OCR). `react-native-worklets-core` / `useFrameProcessor` chahiye.

Q3: Camera battery kaise bachayein?
A3: `isActive` ko screen focus + AppState se control karo; unmount par band.

Q4: QR scan kaise?
A4: `useCodeScanner({ codeTypes: ['qr'], onCodeScanned })` aur `<Camera codeScanner={...} />`.

Q5: Permission denied hone par?
A5: `Linking.openSettings()` se app settings kholo; dobara prompt nahi aata.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- QR/barcode scanner, live OCR, ML kit, custom camera UI
- Video recording with fps/format control

❌ Avoid when:
- Sirf ek photo lena — expo-image-picker / expo-camera kaafi hai
- Project Expo Go-only hai aur dev build nahi banana

---

## 📊 Visual Diagram
```
 <Camera device isActive photo codeScanner frameProcessor>
        │
  ┌─────┴───────────── Native (Camera2/CameraX | AVFoundation)
  │  frames ──► Frame Processor (worklet) ──► JS callbacks
  │  frames ──► Code Scanner ──► onCodeScanned
  └─ takePhoto() ──► file path ──► Image / upload
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Frame Processor | Code run per camera frame | हर frame पर चलने वाला code |
| Worklet | JS function on separate thread | अलग thread का JS function |
| Code Scanner | Built-in QR/barcode reader | QR पढ़ने वाला |
| Device format | Resolution/fps option | Camera की setting |
| Dev build | Custom native app build | कस्टम native build |

---

## ⚡ 3-Line Summary
English: VisionCamera is a high-performance native camera with scanners and frame processors.
It needs a development build (no Expo Go) and camera permissions.
Control `isActive` with focus + app state to save battery.

Hindi: VisionCamera तेज़ native camera है जिसमें scanner और frame processor मिलते हैं।
इसके लिए development build और camera permission चाहिए।
Battery बचाने के लिए `isActive` को focus और app state से कंट्रोल करें।

---

## ➡️ Next Topic
**93. Image Picker — expo-image-picker** — camera के बाद gallery से photo चुनना।

---
