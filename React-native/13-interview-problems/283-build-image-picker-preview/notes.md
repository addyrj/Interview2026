# 283. Interview Problem: Build Image Picker + Preview
# हिंदी में: Image Picker + Preview बनाओ
# Platform: Android ✅ | iOS ✅ | Both ✅
# Difficulty: ⭐⭐ Medium | Asked at: Paytm, PhonePe, Instagram, Zomato
# Expo SDK 52 / React Native 0.76 (check current docs — APIs change between SDKs)

> Code files in this folder: `ImagePickerScreen.jsx`. Copy them into your Expo project and import the main one in `App.js`.
> **Verification note:** syntax-checked with esbuild only. Native APIs need a real device / dev build: not run.

---

## 🔴 Problem Statement
Let the user choose a photo from the gallery or take one with the camera, show a square preview, allow removing it, and handle denied permissions (offer 'Open Settings').

---

## 🔵 Simple Definition (English)
`expo-image-picker` opens the system photo gallery or camera and returns the chosen image's `uri`.

## 🔵 सरल परिभाषा (Hindi)
`expo-image-picker` सिस्टम की gallery या camera खोलता है और चुनी गई image का `uri` लौटाता है।

---

## 🔴 Problem it Solves
Writing native gallery/camera code for both OSes is long. The library gives one JS API and handles the native pickers.

## 🔴 यह क्यों बना? (Hindi)
दोनों OS के लिए native gallery/camera कोड लिखना लंबा है। यह लाइब्रेरी एक ही JS API देती है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install expo-image-picker
Step 2 → request permission (gallery or camera)
Step 3 → launchImageLibraryAsync / launchCameraAsync
Step 4 → check result.canceled
Step 5 → save result.assets[0] in state, show <Image source={{uri}}/>
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → npx expo install expo-image-picker
Step 2 → permission माँगो (gallery या camera)
Step 3 → launchImageLibraryAsync / launchCameraAsync चलाओ
Step 4 → result.canceled चेक करो
Step 5 → result.assets[0] को state में रखो और <Image> में दिखाओ
```

---

## 🟡 Real World Example
Paytm / PhonePe profile photo upload, Zomato review photo upload: pick image, crop, preview, then upload.

## 🟡 Real Example Hindi mein
Paytm / PhonePe की profile photo और Zomato review photo upload में: image चुनो, crop करो, preview देखो, फिर upload।

---

## 💻 Code Example — Basic
```jsx
// Minimal picker
import * as ImagePicker from 'expo-image-picker'; // library

const pick = async () => {
  const res = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ['images'] }); // open gallery (SDK 52+ array form)
  if (!res.canceled) console.log(res.assets[0].uri); // chosen file uri
};
```

## 💻 Code Example — Advanced (complete solution, every line commented)
**File: `ImagePickerScreen.jsx`**
```jsx
// Expo SDK 52 (check current docs - APIs change between SDKs)
// Install: npx expo install expo-image-picker
// mediaTypes: ['images'] needs SDK 52+; older SDKs use ImagePicker.MediaTypeOptions.Images
import React, { useState } from 'react'; // state
import { View, Text, Image, Pressable, Alert, Linking, StyleSheet } from 'react-native'; // RN core
import * as ImagePicker from 'expo-image-picker'; // picker module

export default function ImagePickerScreen() {
  const [image, setImage] = useState(null); // picked asset {uri,width,height}

  const pickFromGallery = async () => {
    // Android 13+/iOS photo picker needs no permission, but request is harmless
    const perm = await ImagePicker.requestMediaLibraryPermissionsAsync(); // ask permission
    if (!perm.granted) { // user denied
      Alert.alert('Permission needed', 'Allow photo access in Settings', [
        { text: 'Cancel' }, // dismiss
        { text: 'Open Settings', onPress: () => Linking.openSettings() }, // go to settings
      ]);
      return; // stop
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'], // only images
      allowsEditing: true, // crop UI
      aspect: [1, 1], // square crop (Android; iOS ignores)
      quality: 0.7, // compress 0..1
    });
    if (!result.canceled) setImage(result.assets[0]); // assets is an array
  };

  const takePhoto = async () => {
    const perm = await ImagePicker.requestCameraPermissionsAsync(); // camera permission
    if (!perm.granted) return Alert.alert('Camera permission denied'); // stop if denied
    const result = await ImagePicker.launchCameraAsync({ quality: 0.7 }); // open camera
    if (!result.canceled) setImage(result.assets[0]); // save photo
  };

  return (
    <View style={styles.container}>
      {image ? (
        <Image source={{ uri: image.uri }} style={styles.preview} /> // preview
      ) : (
        <View style={[styles.preview, styles.placeholder]}>
          <Text>No image selected</Text>
        </View>
      )}
      <Pressable style={styles.btn} onPress={pickFromGallery}><Text style={styles.btnText}>Gallery</Text></Pressable>
      <Pressable style={styles.btn} onPress={takePhoto}><Text style={styles.btnText}>Camera</Text></Pressable>
      {image && (
        <Pressable style={[styles.btn, { backgroundColor: '#999' }]} onPress={() => setImage(null)}>
          <Text style={styles.btnText}>Remove</Text>
        </Pressable>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 16 }, // centre
  preview: { width: 250, height: 250, borderRadius: 12, marginBottom: 16 }, // preview box
  placeholder: { backgroundColor: '#eee', alignItems: 'center', justifyContent: 'center' }, // empty box
  btn: { backgroundColor: '#E23744', padding: 12, borderRadius: 8, marginVertical: 4, width: 200 }, // button
  btnText: { color: '#fff', textAlign: 'center', fontWeight: '600' }, // button text
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Permission | Android 13+ photo picker needs no permission; older needs READ_MEDIA/STORAGE | iOS 14+ PHPicker needs no library permission; camera needs NSCameraUsageDescription |
| Crop UI | `allowsEditing` + `aspect` honoured | `aspect` ignored, fixed square-ish editor |
| Activity kill | Android may restart app while picker open: use `getPendingResultAsync` | Not an issue |
| Info.plist text | Not needed | Provide usage strings in app.json plugin config |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx expo install expo-image-picker
# app.json: ["expo-image-picker", { "photosPermission": "Allow access to photos", "cameraPermission": "Allow camera" }]
```
CLI way (bare React Native):
```bash
npm i expo-image-picker  # needs expo modules installed (npx install-expo-modules)
# or use react-native-image-picker (different API)
cd ios && pod install
# add NSPhotoLibraryUsageDescription / NSCameraUsageDescription to Info.plist
```
Different library in bare CLI projects is common (`react-native-image-picker`); the API differs, do not mix them. Check your SDK docs: `mediaTypes` changed from `MediaTypeOptions.Images` to `['images']` in SDK 52.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Reading `result.uri` (old API).
✅ Correct: Use `result.assets[0].uri` and check `result.canceled`.

❌ Mistake 2: Ignoring denied permission, app does nothing.
✅ Correct: Show alert with `Linking.openSettings()`.

❌ Mistake 3: Uploading the huge original image.
✅ Correct: Set `quality` (0.7) or resize with expo-image-manipulator.

---

## 🧠 Tricky Interview Question
Same code worked on SDK 49 but `result.cancelled` is undefined on SDK 52. Why?

Answer: The property was renamed to `canceled` (and `uri` moved into `assets[]`) in SDK 48+. Old checks `if (!result.cancelled)` are always truthy so you read undefined assets. Hindi: नाम बदल गया — `canceled` और `assets[0].uri` इस्तेमाल करो।

---

## ⚫ Interview Questions + Answers
Q1: Does Android 13+ need storage permission for picking?
A1: No, the system photo picker returns a temporary read grant.

Q2: How to allow multiple images?
A2: `allowsMultipleSelection: true` and `selectionLimit`; read all `result.assets`.

Q3: Why is the URI not uploadable directly?
A3: It is a local `file://` / content URI; send via FormData with name and type.

Q4: expo-image-picker vs react-native-image-picker?
A4: First is Expo module; second is community bare module with different options.

Q5: How to compress?
A5: `quality` option or expo-image-manipulator.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Profile photo, document upload, review photos

❌ Avoid when:
- Need custom camera UI (use expo-camera, topic 284)

---

## 📊 Visual Diagram
```
Button -> requestPermission -> launchLibrary/Camera
                                  |
                          canceled? -> stop
                                  |
                       assets[0].uri -> state -> <Image/>
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| URI | Location of file | file का पता |
| Asset | Picked media object | चुना हुआ media object |
| canceled | User closed picker | यूज़र ने picker बंद किया |
| Permission | OS access grant | OS की अनुमति |
| quality | Compression 0-1 | compression 0 से 1 |

---

## ⚡ 3-Line Summary
English: expo-image-picker returns assets with uri.
Always handle canceled and denied permission.
Compress before upload.
Hindi: expo-image-picker uri वाले assets लौटाता है।
canceled और permission denied हमेशा संभालो।
upload से पहले compress करो।

---

## ➡️ Next Topic
284 — Build Custom Camera Screen: when the stock picker is not enough.
