# 108. Video Recording
# हिंदी में: Video Record करना
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 54 (React Native 0.81) — (check current docs — APIs change between SDKs). `expo-camera` ka `CameraView` with `mode="video"` aur `recordAsync()` use hota hai.

---

## 🔵 Simple Definition (English)
**Video recording** lets your app capture video (and audio) from the camera and save it as a file. With `expo-camera` you call `ref.recordAsync()` on a `CameraView` and get back `{ uri }` when recording stops.

## 🔵 सरल परिभाषा (Hindi)
**Video recording** से आपका app camera (और microphone) से video capture करके file में save करता है। `expo-camera` में `CameraView` के ref पर `recordAsync()` call करते हैं और रुकने पर `{ uri }` मिलता है।

---

## 🔴 Problem it Solves
```
BEFORE:
❌ Camera app kholkar video lena, phir app me wapas aana
❌ Custom UI (timer, flip camera) possible nahi
❌ Native MediaRecorder (Android) / AVCaptureMovieFileOutput (iOS) alag code
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
❌ System camera app खोलकर video लेना
❌ अपना UI (timer, flip) नहीं बना सकते थे
❌ Android और iOS का अलग native code
✅ अब: app के अंदर ही custom recording screen
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install expo-camera (add "expo-camera" plugin in app.json)
Step 2 → Ask camera + microphone permission
Step 3 → <CameraView ref={cameraRef} mode="video" />
Step 4 → const video = await cameraRef.current.recordAsync({ maxDuration: 30 })
Step 5 → To stop manually: cameraRef.current.stopRecording()
Step 6 → recordAsync resolves with { uri } (file in cache)
Step 7 → Move/upload/share the file (expo-file-system, MediaLibrary)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → expo-camera install और plugin add करो
Step 2 → Camera + microphone permission माँगो
Step 3 → <CameraView ref mode="video" /> render करो
Step 4 → recordAsync({ maxDuration: 30 }) से recording शुरू
Step 5 → stopRecording() से manually रोको
Step 6 → recordAsync का promise { uri } देता है (cache में file)
Step 7 → File upload/save/share करो
```

---

## 🟡 Real World Example
**Instagram/Moj/Josh** story & reel recording with timer and flip camera. **Zomato** delivery-partner KYC "record selfie video", **Swiggy** food review videos, bank apps' **video KYC**.

## 🟡 Real Example Hindi mein
**Instagram/Moj/Josh** में story/reel recording (timer + camera flip)। **Zomato** delivery partner का KYC selfie video, **Swiggy** के review videos और bank apps का **video KYC**।

---

## 💻 Code Example — Basic
```jsx
// Basic video recorder - expo-camera, Android + iOS
import React, { useRef, useState } from 'react';                    // hooks
import { View, Button, Text } from 'react-native';                  // UI
import { CameraView, useCameraPermissions, useMicrophonePermissions } from 'expo-camera'; // camera API

export default function BasicRecorder() {
  const cameraRef = useRef(null);                                   // ref to call recordAsync
  const [camPerm, askCam] = useCameraPermissions();                 // camera permission
  const [micPerm, askMic] = useMicrophonePermissions();             // mic permission (needed for audio)
  const [recording, setRecording] = useState(false);                // UI flag
  const [uri, setUri] = useState(null);                             // saved file path

  if (!camPerm?.granted || !micPerm?.granted) {                     // need both permissions
    return (
      <View style={{ flex: 1, justifyContent: 'center' }}>
        <Button title="Allow Camera" onPress={askCam} />
        <Button title="Allow Microphone" onPress={askMic} />
      </View>
    );
  }

  const start = async () => {
    setRecording(true);                                             // show Stop button
    const video = await cameraRef.current?.recordAsync({ maxDuration: 15 }); // waits until stopped / 15s
    setRecording(false);                                            // recording finished
    setUri(video?.uri ?? null);                                     // keep result file uri
  };

  const stop = () => cameraRef.current?.stopRecording();            // triggers recordAsync to resolve

  return (
    <View style={{ flex: 1 }}>
      <CameraView ref={cameraRef} style={{ flex: 1 }} mode="video" facing="back" />
      <Button title={recording ? 'Stop' : 'Record'} onPress={recording ? stop : start} />
      {uri && <Text>Saved: {uri}</Text>}
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: timer, flip camera, error handling, save to gallery
import React, { useEffect, useRef, useState, useCallback } from 'react'; // hooks
import { View, Text, Pressable, Alert, StyleSheet, Platform } from 'react-native'; // UI
import { CameraView, useCameraPermissions, useMicrophonePermissions } from 'expo-camera'; // camera
import * as MediaLibrary from 'expo-media-library';                  // save to gallery

const MAX_SECONDS = 30;                                              // limit like Reels

export default function ReelRecorder({ onDone }) {
  const cameraRef = useRef(null);                                    // camera handle
  const timerRef = useRef(null);                                     // interval handle
  const [camPerm, askCam] = useCameraPermissions();                  // permissions
  const [micPerm, askMic] = useMicrophonePermissions();
  const [facing, setFacing] = useState('back');                      // back/front
  const [recording, setRecording] = useState(false);                 // status
  const [seconds, setSeconds] = useState(0);                         // elapsed time

  useEffect(() => () => clearInterval(timerRef.current), []);        // cleanup timer on unmount

  const start = useCallback(async () => {
    if (!cameraRef.current || recording) return;                     // guard double tap
    try {
      setRecording(true);                                            // UI -> recording
      setSeconds(0);                                                 // reset timer
      timerRef.current = setInterval(() => setSeconds((s) => s + 1), 1000); // tick every second
      const video = await cameraRef.current.recordAsync({ maxDuration: MAX_SECONDS }); // resolves on stop
      clearInterval(timerRef.current);                               // stop timer
      setRecording(false);
      if (!video?.uri) return;                                       // nothing recorded
      const media = await MediaLibrary.requestPermissionsAsync();    // ask gallery write permission
      if (media.granted) await MediaLibrary.saveToLibraryAsync(video.uri); // save to gallery
      onDone?.(video.uri);                                           // return uri to caller
    } catch (e) {
      clearInterval(timerRef.current);                               // always stop timer
      setRecording(false);
      Alert.alert('Recording failed', String(e?.message ?? e));      // tell user
    }
  }, [recording, onDone]);

  const stop = () => cameraRef.current?.stopRecording();             // finish early

  if (!camPerm || !micPerm) return null;                             // still loading
  if (!camPerm.granted || !micPerm.granted) {
    return (
      <View style={styles.center}>
        <Text>Camera + Mic permission chahiye</Text>
        <Pressable onPress={async () => { await askCam(); await askMic(); }}>
          <Text style={styles.link}>Allow</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <View style={styles.flex}>
      <CameraView ref={cameraRef} style={styles.flex} mode="video" facing={facing}
        videoQuality="720p" />
      <Text style={styles.timer}>{String(Math.floor(seconds / 60)).padStart(2, '0')}:{String(seconds % 60).padStart(2, '0')}</Text>
      <View style={styles.bar}>
        <Pressable disabled={recording} onPress={() => setFacing((f) => (f === 'back' ? 'front' : 'back'))}>
          <Text style={styles.btn}>Flip</Text>
        </Pressable>
        <Pressable onPress={recording ? stop : start}>
          <Text style={[styles.btn, recording && { color: 'red' }]}>{recording ? 'STOP' : 'REC'}</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  link: { color: '#0a84ff', marginTop: 12 },
  timer: { position: 'absolute', top: Platform.OS === 'ios' ? 60 : 30, alignSelf: 'center', color: '#fff', fontSize: 18 },
  bar: { position: 'absolute', bottom: 40, width: '100%', flexDirection: 'row', justifyContent: 'space-around' },
  btn: { color: '#fff', fontSize: 20, fontWeight: '700' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Permissions | `CAMERA`, `RECORD_AUDIO` | `NSCameraUsageDescription`, `NSMicrophoneUsageDescription` |
| Output format | mp4 | mov (mp4 container possible via options; check docs) |
| `videoQuality` | Supported values may vary by device | Supported |
| Stabilization | `videoStabilizationMode` support varies | Supported (iOS devices) |
| Simulator | Emulator camera is fake | Simulator has no camera |
| Gallery save | Needs MediaLibrary permission | Needs "Add photos" permission string |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-camera expo-media-library
// app.json plugins: [["expo-camera", { "microphonePermission": "Allow mic for videos" }]]
const video = await cameraRef.current.recordAsync({ maxDuration: 30 }); // returns { uri }
```
CLI way:
```jsx
// npm i react-native-vision-camera ; add permissions manually
// const camera = useRef(null);
// camera.current.startRecording({ onRecordingFinished: (v) => console.log(v.path), onRecordingError: console.error });
// camera.current.stopRecording();
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Forgetting microphone permission — recording is silent or fails.
✅ **Correct:** Request both camera and mic permission.

❌ **Mistake 2:** Using `mode="picture"` (default) and calling `recordAsync`.
✅ **Correct:** Set `mode="video"`.

❌ **Mistake 3:** Treating `recordAsync` as "start only" — it returns only after recording stops.
✅ **Correct:** Call `stopRecording()` elsewhere; `await` result for `uri`.

❌ **Mistake 4:** Uploading huge files raw.
✅ **Correct:** Limit `maxDuration`, lower `videoQuality`, compress before upload.

---

## 🧠 Tricky Interview Question
**Q: `const v = await cameraRef.current.recordAsync(); console.log('started')` — when does "started" print?**

**Answer:** Only after recording finishes (stop, maxDuration or error), because `recordAsync` resolves with the final file. So don't put "recording started" UI updates after the await — set state before it.

---

## ⚫ Interview Questions + Answers

**Q1: How to record video in Expo?**
A1: `CameraView` with `mode="video"` + `recordAsync()`/`stopRecording()`.

**Q2: How to limit duration/size?**
A2: `recordAsync({ maxDuration, maxFileSize })`.

**Q3: Where is the file stored?**
A3: In app cache (`uri` file://). Move with `expo-file-system` or save to gallery with `expo-media-library`.

**Q4: How to switch front/back camera?**
A4: Change the `facing` prop ('front' | 'back').

**Q5: How to upload the video?**
A5: Use `fetch` with `FormData` (`{ uri, name, type: 'video/mp4' }`) or a resumable upload to S3 with a pre-signed URL.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Custom in-app recording (video KYC, reels, reviews)

❌ **Avoid when:**
- Simple "pick a video" — use `expo-image-picker` (launchCameraAsync) instead
- Pro editing/filters needed — use VisionCamera frame processors

---

## 📊 Visual Diagram
```
 Permission(cam+mic) ─► CameraView mode="video"
                              │ recordAsync()
                              ▼
                       [ recording... timer ]
                              │ stopRecording() / maxDuration
                              ▼
                        { uri: file://... }
                              │
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
          upload API     save to gallery    preview (expo-video)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| recordAsync | Start recording, resolves at end | Recording शुरू; खत्म होने पर result |
| maxDuration | Time limit in seconds | अधिकतम समय |
| facing | Which camera | कौन सा camera |
| Cache | Temp storage | अस्थायी storage |
| Video KYC | Identity check via video | Video से पहचान सत्यापन |
| Compression | Reduce size | Size घटाना |

---

## ⚡ 3-Line Summary
**English:**
1. `CameraView mode="video"` + `recordAsync()` records; `stopRecording()` stops.
2. Needs camera AND microphone permission.
3. Result is a cache file `uri` — upload, save or preview it.

**Hindi:**
1. `CameraView mode="video"` + `recordAsync()` से record, `stopRecording()` से stop।
2. Camera और microphone दोनों permission चाहिए।
3. Result cache file का `uri` है — upload, save या preview करो।

---

## ➡️ Next Topic
**109. Background Tasks** — app बंद/background में भी काम चलाना।
