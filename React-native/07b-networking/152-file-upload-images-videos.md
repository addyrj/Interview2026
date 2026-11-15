# 152. File Upload (Images/Videos)
# हिंदी में: File Upload — Image/Video चुनकर server पर भेजना
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 52 target (check current docs — APIs change between SDKs).** `expo-image-picker` ~16.x, `axios` 1.x। Picker/camera native-only है — **यहाँ का code device पर test करना होगा।** Large video upload के लिए `expo-file-system` का upload API (नीचे) docs में अपने SDK के अनुसार देखो।

---

## 🔵 Simple Definition (English)
**File upload** sends a local image or video from the phone to a server. In React Native you pick the file (gallery or camera), put its `uri`, `name` and `type` into a `FormData` object, and send it as `multipart/form-data`.

## 🔵 सरल परिभाषा (Hindi)
**File upload** में phone की local image/video server पर भेजी जाती है। React Native में file चुनकर (gallery या camera), उसका `uri`, `name` और `type` `FormData` में डालते हैं और `multipart/form-data` के रूप में भेजते हैं।

---

## 🔴 Problem it Solves
```
Profile photo, KYC documents, Instagram reels, delivery proof photo — सब upload चाहिए।
समस्या:
  - JSON में binary नहीं जाता (base64 = 33% बड़ा, memory भारी)
  - बड़ी file पर progress, cancel, retry चाहिए
  - Permissions और अलग-अलग file URIs (content:// vs file://)
```

## 🔴 यह क्यों बना? (Hindi)
```
Binary file को multipart/form-data में भेजते हैं (web जैसा)।
RN में FormData file object को {uri, name, type} रूप में समझता है और native layer से stream करता है।
base64 से बचो — memory और size दोनों बढ़ते हैं।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Permission माँगो (gallery: Android 13+/iOS photo picker में अक्सर जरूरत नहीं; camera: जरूरी)
Step 2 → ImagePicker.launchImageLibraryAsync / launchCameraAsync → result.assets[0]
Step 3 → asset से uri, mimeType/ fileName (कभी null हो सकता है!), fileSize
Step 4 → FormData: form.append('file', { uri, name, type })
Step 5 → axios.post(url, form, { headers: multipart, onUploadProgress })
          (Content-Type boundary खुद सेट होने दो)
Step 6 → Progress bar, error/retry, cancel (AbortController)
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. Permission (camera के लिए जरूर)।
2. Picker से file का uri मिलता है।
3. FormData में {uri, name, type} डालो।
4. axios से POST; onUploadProgress से प्रतिशत।
5. Cancel और retry की व्यवस्था।
```

---

## 🟡 Real World Example
**Instagram:** Reel upload — progress bar, background में चलता है, fail होने पर retry। **Swiggy delivery partner app:** delivery की photo proof। **Paytm KYC:** Aadhaar/PAN photo upload (compress करके)। **WhatsApp:** photo भेजने से पहले compress।

## 🟡 Real Example Hindi mein
**Paytm KYC** में आप PAN की फोटो खींचते हैं; app उसे compress करके (कम size) server पर multipart से भेजता है और progress दिखाता है। बड़ी 12MB फोटो सीधे भेजना खराब अनुभव है।

---

## 💻 Code Example — Basic

```jsx
// UploadBasic.jsx — pick image + upload with progress
import React, { useState } from 'react';                          // hooks
import { View, Text, Button, Image } from 'react-native';          // UI
import * as ImagePicker from 'expo-image-picker';                 // picker
import axios from 'axios';                                        // http

export default function UploadBasic() {
  const [asset, setAsset] = useState(null);                       // चुनी हुई file
  const [progress, setProgress] = useState(0);                    // 0..100
  const [msg, setMsg] = useState('');                             // status

  const pick = async () => {
    const res = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],                                     // SDK 52: array form; पुराने SDK में MediaTypeOptions
      quality: 0.7,                                               // compress (0..1)
    });
    if (!res.canceled) setAsset(res.assets[0]);                   // cancel न हुआ तो save
  };

  const upload = async () => {
    if (!asset) return;                                           // कुछ चुना नहीं
    const form = new FormData();                                  // multipart body
    form.append('file', {
      uri: asset.uri,                                             // file:// या content:// जैसा मिला वैसा दो
      name: asset.fileName ?? 'photo.jpg',                        // fileName null हो सकता है
      type: asset.mimeType ?? 'image/jpeg',                       // MIME type
    });
    try {
      setMsg('Uploading...');
      await axios.post('https://api.example.com/upload', form, { // तुम्हारा endpoint
        headers: { 'Content-Type': 'multipart/form-data' },       // boundary RN/axios जोड़ देता है
        onUploadProgress: (e) => setProgress(Math.round((e.loaded * 100) / (e.total || 1))),
        timeout: 60000,                                           // बड़ी file के लिए ज़्यादा
      });
      setMsg('Done');                                             // सफल
    } catch (e) {
      setMsg('Failed: ' + e.message);                             // fail
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <Button title="Pick image" onPress={pick} />
      {asset && <Image source={{ uri: asset.uri }} style={{ width: 200, height: 200, marginVertical: 10 }} />}
      <Button title="Upload" onPress={upload} disabled={!asset} />
      <Text>{progress}% {msg}</Text>
    </View>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// uploadService.js — validate size/type, cancel, retry (logic)
import axios from 'axios';                                        // http

const MAX_BYTES = 10 * 1024 * 1024;                               // 10 MB सीमा
const ALLOWED = ['image/jpeg', 'image/png', 'video/mp4'];         // अनुमत types

export function validateAsset(asset) {                            // upload से पहले जाँच
  if (!asset?.uri) return 'File नहीं मिली';                       // uri जरूरी
  const type = asset.mimeType ?? '';                              // MIME
  if (!ALLOWED.includes(type)) return 'यह file type समर्थित नहीं';
  if (asset.fileSize && asset.fileSize > MAX_BYTES) return 'File 10MB से बड़ी है';
  return null;                                                    // ठीक
}

export function uploadFile(asset, { onProgress, token } = {}) {
  const error = validateAsset(asset);                             // validate
  if (error) return { promise: Promise.reject(new Error(error)), cancel: () => {} };

  const controller = new AbortController();                       // cancel के लिए
  const form = new FormData();                                    // body
  form.append('file', { uri: asset.uri, name: asset.fileName ?? `upload-${Date.now()}`, type: asset.mimeType });
  form.append('kind', asset.mimeType.startsWith('video') ? 'video' : 'image'); // अतिरिक्त field

  const promise = axios.post('https://api.example.com/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    onUploadProgress: (e) => onProgress?.(e.total ? e.loaded / e.total : 0), // 0..1
    signal: controller.signal,                                    // abort
    timeout: 120000,                                              // 2 min
    maxBodyLength: Infinity, maxContentLength: Infinity,          // axios की default सीमा हटाओ
  });
  return { promise, cancel: () => controller.abort() };           // caller को दोनों
}

export async function uploadWithRetry(asset, opts, retries = 2) { // network fail पर दोबारा
  for (let i = 0; ; i++) {
    try { return await uploadFile(asset, opts).promise; }
    catch (e) {
      if (axios.isCancel(e) || i >= retries || e.response) throw e; // cancel/HTTP error पर नहीं
      await new Promise((r) => setTimeout(r, 1000 * 2 ** i));     // backoff
    }
  }
}
// बड़ी videos: presigned URL (S3/GCS) पर सीधे PUT करना बेहतर — server पर load नहीं।
// Compress: expo-image-manipulator (images)। Video compress के लिए third-party library।
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| URI scheme | `file://` या `content://` | `file://` (ph:// नहीं, picker copy देता है) |
| Gallery permission | Android 13+ Photo Picker: permission अक्सर नहीं | PHPicker: permission नहीं (limited access) |
| Camera permission | `CAMERA` (config plugin) | `NSCameraUsageDescription` जरूरी |
| HEIC photos | कम | iPhone photos HEIC; picker JPEG में बदल सकता है — asset.mimeType देखो |
| Background upload | Foreground service/WorkManager | `NSURLSession` background — RN में limited |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-image-picker
// app.json plugin:
// ["expo-image-picker", { "photosPermission": "Allow $(PRODUCT_NAME) to access photos",
//                         "cameraPermission": "Allow $(PRODUCT_NAME) to use the camera" }]
```
CLI way:
```jsx
// npm i react-native-image-picker
// iOS Info.plist: NSPhotoLibraryUsageDescription, NSCameraUsageDescription
// Android: CAMERA permission (AndroidManifest)
// cd ios && pod install
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: File को base64 बनाकर JSON में भेजना।
✅ Correct: `FormData` multipart।

❌ Mistake 2: `Content-Type` में boundary हाथ से लिखना (`multipart/form-data; boundary=...`)।
✅ Correct: Header छोड़ो या सिर्फ़ `multipart/form-data` — boundary अपने आप।

❌ Mistake 3: `asset.fileName` को हमेशा मौजूद मानना।
✅ Correct: Fallback `?? 'photo.jpg'`, MIME भी fallback।

❌ Mistake 4: बिना compress 12MB photo।
✅ Correct: `quality: 0.7` / manipulator, size validate।

❌ Mistake 5: Permission deny का handling नहीं।
✅ Correct: `requestCameraPermissionsAsync()` देखो और Settings का रास्ता दिखाओ।

---

## 🧠 Tricky Interview Question
`form.append('file', { uri, name, type })` — यह web के `FormData` में क्यों नहीं चलेगा पर RN में चलता है?

Answer: Web में `append` को `Blob/File` चाहिए; RN का FormData polyfill ऐसे plain object `{uri, name, type}` को पहचानकर native layer को file path देता है, ताकि file JS memory में लोड हुए बिना stream हो। यह RN-specific extension है (TypeScript में cast की जरूरत पड़ सकती है)।

---

## ⚫ Interview Questions + Answers
Q1: Upload progress कैसे दिखाएँ?
A1: axios का `onUploadProgress`। RN का `fetch` upload progress नहीं देता (XHR `upload.onprogress` या axios)।

Q2: Large video कैसे upload करें?
A2: Presigned URL से सीधे storage पर, chunked/resumable (tus), background-capable library; server पर direct मत भेजो।

Q3: Image compress कैसे?
A3: Picker `quality`, `expo-image-manipulator` resize/compress।

Q4: Upload cancel?
A4: AbortController signal।

Q5: Multiple files?
A5: कई `form.append('files', ...)`; picker में `allowsMultipleSelection: true`।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Profile photo, documents, media posts

❌ Avoid when:
- बहुत बड़े files को API server से गुज़ारना (presigned URL बेहतर)
- Base64 के रूप में भेजना

---

## 📊 Visual Diagram
```
 Picker ─► asset { uri, mimeType, fileName }
              │
 FormData.append('file', {uri,name,type})
              │
 axios.post(multipart) ─► native layer streams file ─► Server
              ▲                       │
   onUploadProgress  ◄────────────────┘      cancel: AbortController
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| multipart/form-data | File upload format | File भेजने का format |
| FormData | Body builder | Body बनाने वाला object |
| URI | File location | File का पता |
| MIME type | File kind | File का प्रकार |
| Presigned URL | Temporary upload link | अस्थायी upload link |

---

## ⚡ 3-Line Summary
English: Pick the file, append `{uri, name, type}` to FormData and POST as multipart.
Use axios for upload progress and AbortController for cancel.
Validate size and type; use presigned URLs for big videos.

Hindi: File चुनो, FormData में `{uri, name, type}` डालो और multipart POST करो।
Progress के लिए axios और cancel के लिए AbortController।
Size/type जाँचो; बड़े videos के लिए presigned URL।

---

## ➡️ Next Topic
**153. Download Files** — server से file लाकर phone में सहेजना।
