# 297. Build Custom Hook — useCamera
# हिंदी में: Custom Hook बनाओ — useCamera
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 52 / React Native 0.76** (check current docs — APIs change between SDKs). `CameraView` + `useCameraPermissions` is the `expo-camera` API from SDK 51+; older SDKs used `<Camera>` and `Camera.requestCameraPermissionsAsync()`.
> Files: [`useCamera.js`](./useCamera.js) · [`CameraScreen.jsx`](./CameraScreen.jsx)
> Install: `npx expo install expo-camera`

---

## 🔵 Simple Definition (English)
A **custom hook** is a function starting with `use` that bundles state and logic so many screens can reuse it. `useCamera` wraps permission, front/back flip, flash and `takePictureAsync` in one place, so a screen only calls `const cam = useCamera()`.

## 🔵 सरल परिभाषा (Hindi)
**Custom hook** एक ऐसा function है जिसका नाम `use` से शुरू होता है और जो state + logic को एक जगह बाँध देता है, ताकि कई screens उसे दोबारा use कर सकें। `useCamera` permission, front/back flip, flash और `takePictureAsync` सब एक जगह रखता है; screen को बस `const cam = useCamera()` लिखना होता है।

---

## 🔴 Problem it Solves
```
❌ हर screen (profile photo, KYC, document scan) में वही permission + ref + try/catch code copy-paste
❌ Double tap पर दो बार फोटो खिंच जाती है
❌ Permission loading / denied / granted की states अलग-अलग तरह से handle होती हैं
❌ Camera logic और UI mix -> test करना मुश्किल
```

## 🔴 यह क्यों बना? (Hindi)
```
Paytm और PhonePe के KYC में selfie, Aadhaar photo और profile photo - तीन अलग screens
में कैमरा चाहिए। अगर हर जगह वही 40 lines लिखें तो bug भी 3 जगह होंगे।
Hook में logic एक बार लिखो, screen सिर्फ UI बनाए। इसे "separation of concerns" कहते हैं।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → useCameraPermissions() gives [permission, requestPermission] (permission is null until loaded)
Step 2 → useRef() creates cameraRef; screen attaches it: <CameraView ref={cam.cameraRef} />
Step 3 → State: facing ('back'|'front'), flash ('off'|'on'), photo, busy, error
Step 4 → takePhoto(): guard (no ref or busy -> return) -> busy=true -> takePictureAsync -> setPhoto
Step 5 → try/catch/finally: error text on failure, busy=false always
Step 6 → Screen branches: loading -> ask permission -> preview photo -> live camera
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → useCameraPermissions() से [permission, requestPermission] मिलता है (load होने तक null)
Step 2 → useRef() से cameraRef बनता है; screen में <CameraView ref={cam.cameraRef} /> लगाओ
Step 3 → State: facing, flash, photo, busy, error
Step 4 → takePhoto(): ref नहीं है या busy है तो return -> busy=true -> takePictureAsync -> photo save
Step 5 → try/catch/finally: fail होने पर error text, और busy हमेशा false
Step 6 → Screen चार हालतें दिखाती है: loading -> permission माँगो -> photo preview -> live camera
```

---

## 🟡 Real World Example
**Paytm / PhonePe KYC** asks for a selfie with a front camera and a Retake button. **Zomato** lets delivery partners and restaurants upload photos. **Instagram** profile photo capture uses the same flow: permission, preview, retake, use.

## 🟡 Real Example Hindi mein
**Paytm / PhonePe KYC** में front camera से selfie और "Retake" button होता है। **Zomato** में delivery partner और restaurant photos upload करते हैं। **Instagram** की profile photo भी यही flow है: permission, preview, retake, use।

---

## 💻 Code Example — Basic
Hook-less version: everything inside the screen (works, but not reusable).

```jsx
// Basic: no custom hook, logic lives inside the screen
import React, { useRef, useState } from 'react'; // React + hooks
import { View, Button, Text } from 'react-native'; // UI
import { CameraView, useCameraPermissions } from 'expo-camera'; // camera API (SDK 51+)

export default function BasicCamera() {
  const ref = useRef(null); // handle to the camera view
  const [perm, askPerm] = useCameraPermissions(); // null until loaded
  const [uri, setUri] = useState(null); // taken photo path

  if (!perm) return <View />; // still loading permission status
  if (!perm.granted) return <Button title="Allow camera" onPress={askPerm} />; // ask user

  const snap = async () => {
    const p = await ref.current?.takePictureAsync(); // capture
    setUri(p?.uri ?? null); // keep the file path
  };

  return (
    <View style={{ flex: 1 }}>
      {/* live preview */}
      <CameraView ref={ref} style={{ flex: 1 }} />
      <Button title="Capture" onPress={snap} />
      {uri && <Text>Saved: {uri}</Text>}
    </View>
  );
}
```

## 💻 Code Example — Advanced
Full code: [`useCamera.js`](./useCamera.js) + [`CameraScreen.jsx`](./CameraScreen.jsx). Key part:

```js
// useCamera.js (key part)
const takePhoto = useCallback(async () => {
  if (!cameraRef.current || busy) return null;             // not ready / already capturing -> ignore
  setBusy(true); setError(null);                           // lock the button, clear old error
  try {
    const result = await cameraRef.current.takePictureAsync({ quality: 0.7 }); // compress a bit
    setPhoto(result);                                      // { uri, width, height } for preview
    return result;                                         // caller can also use it directly
  } catch (e) {
    setError(e.message ?? 'Capture failed');               // show message in UI
    return null;
  } finally {
    setBusy(false);                                        // always unlock
  }
}, [busy]);
```
```jsx
// CameraScreen.jsx (key part) - four states from one hook
if (!cam.permission) return <View />;                      // 1. loading
if (!cam.permission.granted) { /* ask button */ }          // 2. permission
if (cam.photo) { /* Image + Retake + Use photo */ }        // 3. preview
return <CameraView ref={cam.cameraRef} facing={cam.facing} flash={cam.flash} />; // 4. live
```

> Verified: rendered under jsdom (react-native-web, `expo-camera` mocked): permission prompt -> grant -> flip (front) -> flash on -> failed capture shows error -> successful capture shows preview -> Retake returns to camera -> "Use photo" calls `onDone`. The real camera hardware, OS permission dialog and `takePictureAsync` on a device: not run.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Permission declared in | `CAMERA` permission via `expo-camera` config plugin | `NSCameraUsageDescription` in Info.plist (plugin `cameraPermission`) |
| Permission dialog | Can ask again until "Don't ask again" | Asks only once; later must open Settings |
| Simulator/emulator | Emulator has a virtual camera | Simulator has **no** camera (CameraView shows black) |
| Flash `'on'` with front camera | Usually ignored (no flash unit) | Ignored/uses screen flash depending on device |
| Photo orientation (EXIF) | Some devices return rotated EXIF | Normalised by default |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx expo install expo-camera        # installs version matching your SDK
```
```json
// app.json (explain WHY you need the camera - iOS rejects blank text)
{ "expo": { "plugins": [["expo-camera", { "cameraPermission": "Allow $(PRODUCT_NAME) to take your profile photo" }]] } }
```
CLI way:
```bash
npm install react-native-vision-camera     # popular CLI alternative
cd ios && pod install && cd ..             # link iOS pod
```
```jsx
// vision-camera API differs: useCameraDevice('back'), <Camera device={device} isActive photo />, ref.takePhoto()
// Add NSCameraUsageDescription to Info.plist and <uses-permission android:name="android.permission.CAMERA"/> manually
```
(`expo-camera` also works in a bare app that has the `expo` package installed.)

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Rendering `<CameraView>` before permission is granted (black screen or crash).
✅ **Correct:** Branch on `permission?.granted` first.

❌ **Mistake 2:** No `busy` guard, so double tap takes two photos and races two `setPhoto` calls.
✅ **Correct:** Guard with `busy` and `disabled={busy}` on the button.

❌ **Mistake 3:** Forgetting `cameraRef` on `<CameraView>` -> `cameraRef.current` is null.
✅ **Correct:** `<CameraView ref={cam.cameraRef} />` and check for null before calling.

❌ **Mistake 4:** Using old API (`Camera.Constants.Type.back`, `type=`) on SDK 51+.
✅ **Correct:** `facing="back"` prop on `CameraView`.

❌ **Mistake 5:** Leaving the camera mounted on a hidden tab (battery drain).
✅ **Correct:** Render `CameraView` only when the screen is focused (`useIsFocused()`).

---

## 🧠 Tricky Interview Question
**Q:** In `takePhoto` the `busy` check reads state. User taps Capture twice within the same frame. Can two photos still be taken?

**Answer:** Yes, possibly. `busy` is state, so `setBusy(true)` is applied on the next render; two taps in the same event batch both read `busy === false` from the same closure. The button `disabled={busy}` only helps after the re-render. A safer guard is a ref: `const busyRef = useRef(false); if (busyRef.current) return; busyRef.current = true;` and reset it in `finally`. Refs update synchronously.

---

## ⚫ Interview Questions + Answers

**Q1: Why a custom hook instead of a component?**
A1: A hook shares logic (state, effects, refs) without UI. A component shares UI. Several different screens with different UI can reuse the same `useCamera`.

**Q2: Rules of hooks that apply here?**
A2: Call hooks only at the top level and only from components or other hooks. `useCamera` calls `useRef`, `useState`, `useCallback` unconditionally.

**Q3: Why `useCallback` on `toggleFacing` / `takePhoto`?**
A3: Stable function identity avoids re-rendering memoized children and unnecessary effect re-runs. Note `takePhoto` changes when `busy` changes because it is in the dependency list.

**Q4: How do you get a smaller image for upload?**
A4: `takePictureAsync({ quality: 0.7 })` compresses JPEG; for resize use `expo-image-manipulator` after capture. Smaller files upload faster on 4G.

**Q5: How would you test the hook?**
A5: Mock `expo-camera`, then use `renderHook` from `@testing-library/react-native` and call `act(() => result.current.toggleFacing())`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Camera is needed on 2+ screens (profile, KYC, document upload)
- You want UI and logic separated for testing

❌ Avoid when:
- Single one-off screen (the Basic version is simpler)
- You need frame processors / QR / ML (use `react-native-vision-camera`)

---

## 📊 Visual Diagram
```
 CameraScreen (UI only)
      │  const cam = useCamera()
      ▼
 ┌────────────── useCamera ───────────────┐
 │ permission ◀── useCameraPermissions()   │
 │ cameraRef  ──▶ <CameraView ref=...>     │
 │ facing / flash / photo / busy / error   │
 │ takePhoto() ─▶ takePictureAsync()       │
 └─────────────────────────────────────────┘
 states shown:  loading → ask → live camera → preview(Retake / Use)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Custom hook | Function with `use` prefix that reuses logic | अपना बनाया reusable hook |
| Ref | Handle to a mounted component | Component का handle |
| `facing` | Which camera: back or front | कौन सा कैमरा |
| Permission | User's OS-level consent | OS की अनुमति |
| `busy` guard | Flag that blocks double actions | डबल tap रोकने वाला flag |
| EXIF | Metadata inside a photo (rotation etc.) | फोटो का metadata |

---

## ⚡ 3-Line Summary
**English:**
1. `useCamera` packs permission, ref, flip, flash and capture into one reusable hook.
2. A `busy` guard plus try/catch/finally keeps capture safe and the UI consistent.
3. The screen only decides what to show: loading, ask, live camera or preview.

**Hindi:**
1. `useCamera` permission, ref, flip, flash और capture को एक reusable hook में रखता है।
2. `busy` guard और try/catch/finally से capture सुरक्षित और UI consistent रहती है।
3. Screen सिर्फ यह तय करती है कि क्या दिखाना है: loading, permission, live camera या preview।

---

## ➡️ Next Topic
**298. Build Custom Hook - useNetInfo** - अब network स्थिति को hook में लपेटना: offline banner और payment block।
