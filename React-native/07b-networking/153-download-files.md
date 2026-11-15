# 153. Download Files
# हिंदी में: Download Files — Server से file लाकर phone में सहेजना
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 52 target (check current docs — APIs change between SDKs).** `expo-file-system` ~18.x (`createDownloadResumable`, `downloadAsync`, `documentDirectory`, `cacheDirectory`), `expo-sharing`, `expo-media-library`। **Version note:** नए SDKs में `expo-file-system` का नया object-based API आया है और पुराना API `expo-file-system/legacy` में गया है — अपने SDK के docs में import path जाँचो। Native-only; device पर test करो।

---

## 🔵 Simple Definition (English)
**Downloading a file** means fetching it from a URL and saving it into the app's storage (documents or cache folder). You can show progress, pause and resume, then open or share the file.

## 🔵 सरल परिभाषा (Hindi)
**File download** का मतलब URL से file लाकर app के storage (documents या cache folder) में सहेजना है। Progress दिखा सकते हैं, pause/resume कर सकते हैं, फिर file खोल या share कर सकते हैं।

---

## 🔴 Problem it Solves
```
Invoice PDF, offline video, ticket, statement — user को file चाहिए।
समस्या:
  - fetch().blob() बड़ी file को memory में भर देता है
  - progress/pause/resume नहीं
  - File कहाँ सहेजें? (sandbox, gallery, Downloads)
```

## 🔴 यह क्यों बना? (Hindi)
```
FileSystem API file को सीधे disk पर stream करता है (memory में नहीं)।
Progress callback और resumable download मिलते हैं।
Sandbox folder में सहेजना आसान; gallery/Downloads में रखने के लिए अलग step।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → destination तय: FileSystem.documentDirectory + 'invoice.pdf' (स्थायी)
          या cacheDirectory (OS साफ़ कर सकता है)
Step 2 → FileSystem.createDownloadResumable(url, fileUri, options, progressCallback)
Step 3 → downloadAsync() → { uri, status, headers }; status 200 जाँचो
Step 4 → progress: totalBytesWritten / totalBytesExpectedToWrite
Step 5 → pauseAsync() → savable() state; resumeAsync() से आगे
Step 6 → खोलना/share: Sharing.shareAsync(uri); gallery: MediaLibrary.saveToLibraryAsync(uri)
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. Save करने की जगह चुनो (documents = स्थायी, cache = अस्थायी)।
2. createDownloadResumable से download शुरू।
3. Progress callback से प्रतिशत।
4. Pause/resume संभव।
5. Download के बाद Sharing या MediaLibrary से खोलो/gallery में डालो।
```

---

## 🟡 Real World Example
**Paytm / PhonePe:** Transaction statement PDF download करके share। **Swiggy:** order invoice PDF। **Hotstar/Netflix:** offline videos (DRM, encrypted — standard FileSystem से नहीं होता)। **WhatsApp:** media download progress के साथ।

## 🟡 Real Example Hindi mein
**Swiggy** में order का invoice PDF download होता है — app उसे documents folder में सेव करती है और "Share/Open" का option देती है। Hotstar के offline video DRM वाले होते हैं, इसलिए सामान्य file download जैसे नहीं।

---

## 💻 Code Example — Basic

```jsx
// DownloadBasic.jsx — download PDF with progress, then share
import React, { useState } from 'react';                          // hooks
import { View, Text, Button } from 'react-native';                // UI
import * as FileSystem from 'expo-file-system';                   // SDK 52 API (नए SDK में /legacy देखो)
import * as Sharing from 'expo-sharing';                          // share sheet

const URL = 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf'; // demo PDF

export default function DownloadBasic() {
  const [pct, setPct] = useState(0);                              // progress
  const [uri, setUri] = useState(null);                           // saved file
  const [err, setErr] = useState('');                             // error text

  const download = async () => {
    setErr(''); setPct(0);                                        // reset
    const target = FileSystem.documentDirectory + 'sample.pdf';   // सहेजने की जगह
    const task = FileSystem.createDownloadResumable(
      URL,                                                        // source
      target,                                                     // destination
      {},                                                         // options (headers आदि)
      (p) => setPct(Math.round((p.totalBytesWritten / (p.totalBytesExpectedToWrite || 1)) * 100)) // progress
    );
    try {
      const res = await task.downloadAsync();                     // शुरू
      if (!res || res.status !== 200) throw new Error('HTTP ' + res?.status); // status जाँचो!
      setUri(res.uri);                                            // सफल
    } catch (e) {
      setErr(e.message);                                          // fail
    }
  };

  const share = async () => {
    if (uri && (await Sharing.isAvailableAsync())) await Sharing.shareAsync(uri); // share sheet
  };

  return (
    <View style={{ padding: 20 }}>
      <Button title="Download" onPress={download} />
      <Text>{pct}%</Text>
      {uri && <Button title="Open / Share" onPress={share} />}
      {!!err && <Text>Error: {err}</Text>}
    </View>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// downloader.js — pause/resume persisted across app restart + gallery save + cleanup
import * as FileSystem from 'expo-file-system';                   // file system (SDK 52 path)
import * as MediaLibrary from 'expo-media-library';               // gallery
import AsyncStorage from '@react-native-async-storage/async-storage'; // resume data store

const RESUME_KEY = 'download:resume';                             // key

export function startDownload(url, fileName, onProgress) {
  const target = FileSystem.documentDirectory + fileName;         // destination
  let savedState = null;                                          // resume data

  const task = FileSystem.createDownloadResumable(url, target, {}, (p) => {
    onProgress?.(p.totalBytesExpectedToWrite ? p.totalBytesWritten / p.totalBytesExpectedToWrite : 0);
  });

  return {
    async start() {
      const res = await task.downloadAsync();                     // पूरा download
      if (!res || res.status !== 200) {                           // fail: partial file हटाओ
        await FileSystem.deleteAsync(target, { idempotent: true });
        throw new Error('Download failed: ' + res?.status);
      }
      await AsyncStorage.removeItem(RESUME_KEY);                  // resume data अब बेकार
      return res.uri;
    },
    async pause() {
      await task.pauseAsync();                                    // रोको
      savedState = task.savable();                                // {url, fileUri, options, resumeData}
      await AsyncStorage.setItem(RESUME_KEY, JSON.stringify(savedState)); // app बंद होने पर भी
    },
    async resume() {
      const res = await task.resumeAsync();                       // आगे बढ़ाओ
      return res?.uri;
    },
  };
}

export async function resumeFromDisk(onProgress) {                // app restart के बाद
  const raw = await AsyncStorage.getItem(RESUME_KEY);             // saved state
  if (!raw) return null;
  const s = JSON.parse(raw);
  const task = new FileSystem.DownloadResumable(                  // class से दोबारा बनाओ
    s.url, s.fileUri, s.options,
    (p) => onProgress?.(p.totalBytesWritten / (p.totalBytesExpectedToWrite || 1)),
    s.resumeData
  );
  return task.resumeAsync();                                      // continue
}

export async function saveToGallery(fileUri) {                    // image/video को gallery में
  const perm = await MediaLibrary.requestPermissionsAsync(true);  // writeOnly=true (जहाँ supported)
  if (!perm.granted) throw new Error('Gallery permission नहीं मिली');
  return MediaLibrary.saveToLibraryAsync(fileUri);                // सिर्फ़ image/video/audio
}
// Free space जाँच: await FileSystem.getFreeDiskStorageAsync(); बड़ी file से पहले करो।
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| App sandbox | `documentDirectory` = app-private | `documentDirectory` = app-private (Files app में दिखा सकते हैं config से) |
| Public "Downloads" folder | सीधे नहीं; Storage Access Framework (`StorageAccessFramework`) या MediaStore | नहीं; Share sheet → "Save to Files" |
| Gallery save | MediaLibrary (Android 10+ scoped storage) | MediaLibrary → Photos permission |
| Cache clearing | OS/ user "clear cache" | OS storage कम होने पर cacheDirectory साफ़ |
| Open file | Intent (Sharing/IntentLauncher) | Share sheet / Quick Look |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-file-system expo-sharing expo-media-library
// app.json plugin (MediaLibrary): ["expo-media-library", { "photosPermission": "...", "savePhotosPermission": "..." }]
```
CLI way:
```jsx
// npm i react-native-blob-util   (या react-native-fs)
// ReactNativeBlobUtil.config({ fileCache: true, addAndroidDownloads: { useDownloadManager: true, notification: true } }).fetch('GET', url)
// cd ios && pod install; Android: Download Manager से notification मिलता है
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `fetch().blob()` से बड़ी file।
✅ Correct: `createDownloadResumable` (disk पर stream)।

❌ Mistake 2: `res.status` न जाँचना → 404 का HTML "file" के रूप में सेव।
✅ Correct: `status === 200` जाँचो, नहीं तो file हटाओ।

❌ Mistake 3: Important file `cacheDirectory` में।
✅ Correct: `documentDirectory`।

❌ Mistake 4: Android पर PDF को gallery में डालने की कोशिश।
✅ Correct: MediaLibrary सिर्फ़ media के लिए; PDF के लिए Share/SAF।

❌ Mistake 5: Free space न जाँचना।
✅ Correct: `getFreeDiskStorageAsync()`।

---

## 🧠 Tricky Interview Question
Download के बाद PDF खुल नहीं रहा, file size 2KB है। कारण?

Answer: Server ने शायद error (401/404) का HTML/JSON लौटाया और `downloadAsync` ने उसे फ़ाइल की तरह सेव कर दिया — `downloadAsync` HTTP error पर throw नहीं करता, `status` देता है। हल: `res.status === 200` जाँचो, auth headers `options.headers` में दो, और fail पर file हटाओ।

---

## ⚫ Interview Questions + Answers
Q1: documentDirectory बनाम cacheDirectory?
A1: Documents स्थायी (backup में जा सकता है); cache अस्थायी, OS हटा सकता है।

Q2: Progress कैसे?
A2: `createDownloadResumable` का callback: `totalBytesWritten / totalBytesExpectedToWrite`।

Q3: Pause/resume?
A3: `pauseAsync()`, `savable()` से state सहेजो, `resumeAsync()`; server को Range requests समर्थित होनी चाहिए।

Q4: Private (auth) file कैसे?
A4: `options.headers: { Authorization: ... }` या short-lived signed URL।

Q5: Background में download?
A5: Expo FileSystem में सीमित (`sessionType: BACKGROUND` iOS पर विकल्प, docs देखो); भरोसेमंद के लिए native libs (react-native-blob-util DownloadManager)।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- PDF/invoice, offline media, attachments

❌ Avoid when:
- छोटा JSON (fetch काफी)
- DRM-protected video (विशेष SDK)

---

## 📊 Visual Diagram
```
 URL ──► createDownloadResumable ──► stream to disk
                │ progress callback (bytes written / expected)
                ▼
      documentDirectory/file.pdf
          │            │             │
       Sharing      MediaLibrary    pause/resume
      (open/share)  (gallery)       (savable state)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| documentDirectory | Persistent app folder | स्थायी app folder |
| cacheDirectory | Temporary folder | अस्थायी folder |
| Resumable | Can continue later | बाद में जारी रखने योग्य |
| Scoped storage | Android file access rules | Android के file नियम |
| Range request | Partial download | आंशिक download |

---

## ⚡ 3-Line Summary
English: Use `createDownloadResumable` to stream a file to disk with progress.
Always check the HTTP status and save important files in documentDirectory.
Use Sharing or MediaLibrary to open or export the file.

Hindi: `createDownloadResumable` से file को progress के साथ disk पर stream करो।
HTTP status जाँचो और जरूरी file documentDirectory में रखो।
खोलने/export के लिए Sharing या MediaLibrary।

---

## ➡️ Next Topic
**154+ (अगला section)** — networking के बाद state management और storage के topics।
