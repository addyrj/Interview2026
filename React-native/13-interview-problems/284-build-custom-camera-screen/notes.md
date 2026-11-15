# 284. Interview Problem: Build Custom Camera Screen
# हिंदी में: Custom Camera Screen बनाओ
# Platform: Android ✅ | iOS ✅ | Both ✅
# Difficulty: ⭐⭐⭐ Medium-Hard | Asked at: Paytm (KYC), PhonePe, Instagram, Zomato
# Expo SDK 52 / React Native 0.76 (check current docs — APIs change between SDKs)

> Code files in this folder: `CameraScreen.jsx`. Copy them into your Expo project and import the main one in `App.js`.
> **Verification note:** syntax-checked with esbuild only. Native APIs need a real device / dev build: not run.

---

## 🔴 Problem Statement
Build an in-app camera: permission screen, live preview, flip front/back, flash toggle, shutter button, then a preview with Retake.

---

## 🔵 Simple Definition (English)
`expo-camera` gives a `CameraView` component for live preview and `takePictureAsync` to capture.

## 🔵 सरल परिभाषा (Hindi)
`expo-camera` का `CameraView` live preview दिखाता है और `takePictureAsync` से फोटो लेते हैं।

---

## 🔴 Problem it Solves
The stock picker cannot show your own overlay (guide frame, custom buttons). A custom camera gives full UI control (KYC selfie, document scan).

## 🔴 यह क्यों बना? (Hindi)
stock picker में अपना overlay (guide frame, custom बटन) नहीं लगता। Custom camera से पूरा UI कंट्रोल मिलता है (KYC selfie, document scan)।

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install expo-camera
Step 2 → useCameraPermissions() -> ask if not granted
Step 3 → render <CameraView ref facing flash/>
Step 4 → overlay buttons with position absolute
Step 5 → ref.takePictureAsync() -> show preview
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → npx expo install expo-camera
Step 2 → useCameraPermissions() से permission माँगो
Step 3 → <CameraView ref facing flash/> दिखाओ
Step 4 → ऊपर absolute position से बटन
Step 5 → ref.takePictureAsync() -> preview
```

---

## 🟡 Real World Example
Paytm KYC selfie screen: a circular guide, shutter button and Retake/Confirm after capture.

## 🟡 Real Example Hindi mein
Paytm KYC selfie screen: गोल guide, shutter बटन और फोटो के बाद Retake/Confirm।

---

## 💻 Code Example — Basic
```jsx
// Minimal camera
import { CameraView, useCameraPermissions } from 'expo-camera'; // API (SDK 51+)
const [perm, ask] = useCameraPermissions(); // permission hook
// <CameraView style={{ flex: 1 }} facing="back" ref={ref} />
// const pic = await ref.current.takePictureAsync(); // capture
```

## 💻 Code Example — Advanced (complete solution, every line commented)
**File: `CameraScreen.jsx`**
```jsx
// Expo SDK 52 (check current docs - APIs change between SDKs)
// Install: npx expo install expo-camera   (CameraView API exists from SDK 51; older used <Camera>)
import React, { useRef, useState } from 'react'; // hooks
import { View, Text, Image, Pressable, StyleSheet } from 'react-native'; // RN core
import { CameraView, useCameraPermissions } from 'expo-camera'; // camera + permission hook

export default function CameraScreen() {
  const cameraRef = useRef(null); // handle to camera methods
  const [permission, requestPermission] = useCameraPermissions(); // permission state
  const [facing, setFacing] = useState('back'); // 'back' | 'front'
  const [flash, setFlash] = useState('off'); // 'off' | 'on' | 'auto'
  const [photo, setPhoto] = useState(null); // captured photo

  if (!permission) return <View />; // still loading permission status
  if (!permission.granted) { // not allowed yet
    return (
      <View style={styles.center}>
        <Text>Camera access is needed</Text>
        <Pressable style={styles.btn} onPress={requestPermission}>
          <Text style={styles.btnText}>Allow Camera</Text>
        </Pressable>
      </View>
    );
  }

  const capture = async () => {
    try {
      const pic = await cameraRef.current?.takePictureAsync({ quality: 0.8 }); // take photo
      if (pic) setPhoto(pic); // save {uri,width,height}
    } catch (e) {
      console.warn('Capture failed', e); // log error
    }
  };

  if (photo) { // preview mode
    return (
      <View style={styles.flex}>
        <Image source={{ uri: photo.uri }} style={styles.flex} resizeMode="contain" />
        <Pressable style={styles.btn} onPress={() => setPhoto(null)}>
          <Text style={styles.btnText}>Retake</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <View style={styles.flex}>
      <CameraView ref={cameraRef} style={styles.flex} facing={facing} flash={flash} /> 
      <View style={styles.controls}>
        <Pressable onPress={() => setFacing((f) => (f === 'back' ? 'front' : 'back'))}>
          <Text style={styles.ctrl}>Flip</Text>
        </Pressable>
        <Pressable onPress={capture} style={styles.shutter} />
        <Pressable onPress={() => setFlash((f) => (f === 'off' ? 'on' : 'off'))}>
          <Text style={styles.ctrl}>Flash {flash}</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 }, // fill
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' }, // centre
  controls: { position: 'absolute', bottom: 40, width: '100%', flexDirection: 'row', justifyContent: 'space-around', alignItems: 'center' }, // overlay
  ctrl: { color: '#fff', fontSize: 16 }, // control text
  shutter: { width: 70, height: 70, borderRadius: 35, backgroundColor: '#fff', borderWidth: 4, borderColor: '#ccc' }, // shutter
  btn: { backgroundColor: '#E23744', padding: 12, borderRadius: 8, margin: 16 }, // button
  btnText: { color: '#fff', fontWeight: '600', textAlign: 'center' }, // button text
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Permission | Runtime CAMERA permission | NSCameraUsageDescription required in Info.plist (plugin does it) |
| Flash | Torch/flash behaviour differs by device | Front flash is a screen flash |
| Orientation | Preview may be rotated on some devices; use `skipProcessing`/EXIF carefully | EXIF-based rotation, usually correct |
| Simulator | Emulator has fake camera | iOS simulator has NO camera: test on device |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx expo install expo-camera
# app.json plugin: ["expo-camera", { "cameraPermission": "Allow camera" }]
```
CLI way (bare React Native):
```bash
npm i expo-camera  # after npx install-expo-modules
# or react-native-vision-camera (popular, different API)
cd ios && pod install
```
Expo Go includes expo-camera. SDK 50 and older used `<Camera>` and `Camera.requestCameraPermissionsAsync()`; SDK 51+ uses `CameraView`. Check docs for your SDK.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using old `<Camera type={Camera.Constants.Type.back}>` on new SDKs.
✅ Correct: Use `CameraView` with `facing="back"`.

❌ Mistake 2: Calling takePictureAsync before the camera is ready.
✅ Correct: Use optional chaining and `onCameraReady` if needed.

❌ Mistake 3: Camera stays on while screen is in background.
✅ Correct: Render CameraView only when screen is focused (`useIsFocused`).

---

## 🧠 Tricky Interview Question
Preview is black on Android after permission was just granted. Why?

Answer: The component mounted before permission granted state propagated, or another screen holds the camera. Render CameraView only after `permission.granted`, and unmount it on blur. Hindi: permission मिलने के बाद ही CameraView दिखाओ।

---

## ⚫ Interview Questions + Answers
Q1: Why `useRef` for camera?
A1: Methods like takePictureAsync live on the instance.

Q2: How to save to gallery?
A2: expo-media-library `saveToLibraryAsync(uri)` (needs its own permission).

Q3: Camera vs ImagePicker?
A3: ImagePicker uses system UI; Camera gives custom UI.

Q4: How to record video?
A4: `recordAsync()` and `stopRecording()` with microphone permission.

Q5: How to reduce memory?
A5: Lower `quality`, set `skipProcessing`, use smaller picture size.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Custom overlay, KYC, scanning, in-app video

❌ Avoid when:
- Only need to choose/take a simple photo (use ImagePicker)

---

## 📊 Visual Diagram
```
permission? --no--> [Allow button]
   | yes
   v
<CameraView facing flash ref>
   | overlay: Flip | Shutter | Flash
   v
takePictureAsync -> photo state -> <Image/> + Retake
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CameraView | Camera preview component | camera preview कॉम्पोनेंट |
| facing | back or front lens | पीछे/आगे का कैमरा |
| Shutter | Capture button | फोटो खींचने का बटन |
| Torch/Flash | Light for photo | फोटो के लिए रोशनी |
| Ref | Handle to instance | instance का हैंडल |

---

## ⚡ 3-Line Summary
English: CameraView + useCameraPermissions build a custom camera.
Capture with ref.takePictureAsync.
Unmount the camera when not focused.
Hindi: CameraView और useCameraPermissions से custom camera बनता है।
ref.takePictureAsync से फोटो लो।
फोकस न हो तो camera unmount करो।

---

## ➡️ Next Topic
285 — Build Maps with Markers: another native-module screen with API keys.
