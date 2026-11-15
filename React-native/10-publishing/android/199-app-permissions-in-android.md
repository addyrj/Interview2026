# 199. App Permissions in Android
# हिंदी में: Android में App Permissions
# Platform: Android ✅ | iOS ✅ (concept same, API अलग)

> Target: **Expo SDK 52 (React Native 0.76)** — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
Permissions are the user's "yes/no" for your app to use sensitive things: camera, location, contacts, notifications. Normal permissions are auto-granted; **dangerous** ones must be asked at runtime (Android 6+).

## 🔵 सरल परिभाषा (Hindi)
Permissions user की "हाँ/ना" होती हैं — camera, location, contacts, notifications जैसी sensitive चीज़ें use करने के लिए। Normal permissions अपने आप मिल जाती हैं, लेकिन **dangerous** permissions runtime पर माँगनी पड़ती हैं (Android 6+)।

---

## 🔴 Problem it Solves
- Before Android 6, installing = granting everything. Users could not refuse one permission.
- Malicious apps read SMS/location silently.
- Now users decide at the moment of use and can revoke from Settings.

## 🔴 यह क्यों बना? (Hindi)
- Android 6 से पहले install करते ही सब permissions मिल जाती थीं, user मना नहीं कर सकता था।
- Malicious apps चुपचाप SMS/location पढ़ लेते थे।
- अब user उसी समय तय करता है और Settings से वापस ले सकता है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → Declare permission in manifest (app.json "permissions" or <uses-permission>)
Step 2 → At the feature moment, check current status
Step 3 → If not granted → show a short reason (rationale) to the user
Step 4 → Call request API → OS shows the system dialog
Step 5 → Result: granted / denied / "never ask again" (blocked)
Step 6 → If blocked → send user to app Settings (Linking.openSettings())
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Manifest में permission declare करो
Step 2 → Feature use होने से ठीक पहले status check करो
Step 3 → Granted नहीं है तो user को कारण (rationale) बताओ
Step 4 → Request API call करो → OS का dialog आएगा
Step 5 → Result: granted / denied / "never ask again"
Step 6 → Blocked हो तो Linking.openSettings() से Settings खोलो
```

---

## 🟡 Real World Example
**Paytm** asks for Camera only when you tap "Scan QR", not at app start. **Zomato** asks Location when you open the home screen to show nearby restaurants, and shows a "Enter location manually" fallback if denied. **Swiggy** asks Notification permission (Android 13+) after the first order so it can send delivery updates.

## 🟡 Real Example Hindi mein
**Paytm** Camera permission तभी माँगता है जब आप "Scan QR" दबाते हो, app खुलते ही नहीं। **Zomato** Home screen पर Location माँगता है; मना करने पर "manually location डालें" का option देता है। **Swiggy** पहले order के बाद Notification permission (Android 13+) माँगता है ताकि delivery updates भेज सके।

---

## 💻 Code Example — Basic
Core RN API (works in CLI and Expo dev builds), Android only:
```jsx
// Import React and UI pieces
import React from 'react';
// Import Android permission API and Platform check
import { View, Button, PermissionsAndroid, Platform, Alert } from 'react-native';

// Function that asks for CAMERA permission
async function askCamera() {
  // iOS has no PermissionsAndroid, so exit early
  if (Platform.OS !== 'android') return true;
  try {
    // Show the system dialog with a custom rationale text
    const result = await PermissionsAndroid.request(
      PermissionsAndroid.PERMISSIONS.CAMERA, // which permission
      {
        title: 'Camera Permission',            // rationale title
        message: 'We need camera to scan QR',  // rationale message
        buttonPositive: 'Allow',               // positive button label
        buttonNegative: 'Deny',                // negative button label
      }
    );
    // Compare with the GRANTED constant
    return result === PermissionsAndroid.RESULTS.GRANTED;
  } catch (e) {
    // Unexpected native error
    console.warn(e);
    return false;
  }
}

// Simple screen
export default function Basic() {
  return (
    <View style={{ flex: 1, justifyContent: 'center' }}>
      {/* Button asks permission and shows result */}
      <Button
        title="Scan QR"
        onPress={async () => Alert.alert((await askCamera()) ? 'Granted' : 'Denied')}
      />
    </View>
  );
}
```

## 💻 Code Example — Advanced
Expo way with `expo-camera` hook, blocked-state handling and notification permission (Android 13+):
```jsx
// React and hooks
import React from 'react';
// UI components, Linking for Settings, Platform for OS check
import { View, Text, Button, Linking, Platform } from 'react-native';
// Expo camera: component + permission hook
import { CameraView, useCameraPermissions } from 'expo-camera';
// Expo notifications for POST_NOTIFICATIONS on Android 13+
import * as Notifications from 'expo-notifications';

export default function Advanced() {
  // permission = current status object, request = function to ask
  const [permission, requestPermission] = useCameraPermissions();

  // Still loading status from native side
  if (!permission) return <View />;

  // Granted: show camera
  if (permission.granted) {
    return <CameraView style={{ flex: 1 }} facing="back" />;
  }

  // Not granted: explain and offer action
  return (
    <View style={{ flex: 1, justifyContent: 'center', padding: 24 }}>
      <Text>We need camera access to scan QR codes.</Text>
      {/* canAskAgain=false means user chose "don't ask again" */}
      {permission.canAskAgain ? (
        <Button title="Allow Camera" onPress={requestPermission} />
      ) : (
        // Only way now is the system Settings screen
        <Button title="Open Settings" onPress={() => Linking.openSettings()} />
      )}
      {/* Android 13+ runtime notification permission */}
      <Button
        title="Enable Notifications"
        onPress={async () => {
          // On Android 13+ a channel must exist before the dialog appears
          if (Platform.OS === 'android') {
            await Notifications.setNotificationChannelAsync('default', {
              name: 'default',
              importance: Notifications.AndroidImportance.DEFAULT,
            });
          }
          // Triggers the system prompt
          await Notifications.requestPermissionsAsync();
        }}
      />
    </View>
  );
}
```
`app.json` plugin config (version-dependent: `cameraPermission` key is for expo-camera plugin in SDK 51+):
```json
{
  "expo": {
    "android": { "permissions": ["CAMERA", "POST_NOTIFICATIONS"] },
    "plugins": [["expo-camera", { "cameraPermission": "Allow FoodApp to scan QR codes" }]]
  }
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Declare | `<uses-permission>` in manifest | `NS...UsageDescription` in Info.plist |
| Ask again after deny | 2nd time allowed; then "don't ask again" | Only once; then Settings only |
| Rationale | `shouldShowRequestPermissionRationale` | Your own pre-prompt screen |
| Core RN API | `PermissionsAndroid` | None (use libraries) |
| Notifications | Needs runtime ask from API 33 | Always ask |
| Location levels | Fine/Coarse, background separate | While-using / Always |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Each Expo module has its own hook/request function
const [perm, request] = useCameraPermissions(); // expo-camera
```
CLI way:
```jsx
// Core RN for Android; for iOS use react-native-permissions
import { PermissionsAndroid } from 'react-native';
await PermissionsAndroid.request(PermissionsAndroid.PERMISSIONS.CAMERA);
// Also edit AndroidManifest.xml and ios/Info.plist by hand
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Requesting without declaring in manifest — request silently returns denied.
✅ Correct: Declare first, then request.

❌ Mistake 2: Asking all permissions at app launch.
✅ Correct: Ask in context, when the feature is used.

❌ Mistake 3: Not handling "never ask again".
✅ Correct: Check `canAskAgain` and open Settings.

❌ Mistake 4: Asking `READ_SMS`/background location without Play policy approval.
✅ Correct: Use alternatives (SMS User Consent API) or fill Play's Permissions Declaration form.

---

## 🧠 Tricky Interview Question
"You call `PermissionsAndroid.request(POST_NOTIFICATIONS)` on Android 12 device. What result?"

Answer: `POST_NOTIFICATIONS` is a runtime permission only on Android 13+ (API 33). On Android 12 and below notifications are allowed by default, so there is no dialog to show; the call's result is not meaningful there. Guard it: `Platform.OS === 'android' && Platform.Version >= 33`, otherwise skip the request.

---

## ⚫ Interview Questions + Answers
Q1: Normal vs dangerous permissions?
A1: Normal (INTERNET, VIBRATE) are granted at install. Dangerous (CAMERA, LOCATION, CONTACTS) need runtime consent.

Q2: How do you detect "never ask again"?
A2: `PermissionsAndroid.RESULTS.NEVER_ASK_AGAIN` or Expo's `canAskAgain === false`.

Q3: What happens to permissions if the user does not use the app for months?
A3: Android 11+ auto-resets permissions of unused apps.

Q4: How to remove a permission a library added?
A4: `blockedPermissions` in `app.json` or `tools:node="remove"` in the manifest.

Q5: Can you request multiple permissions together?
A5: Yes, `PermissionsAndroid.requestMultiple([...])`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Feature truly needs the resource and user just triggered it.

❌ Avoid when:
- Alternatives exist (image picker needs no storage permission; Photo Picker on Android 13+).
- You request at first launch with no context.

---

## 📊 Visual Diagram
```
 Feature tapped
      │
      ▼
 Check status ──granted──► Use feature
      │
   not granted
      ▼
 canAskAgain? ──yes──► Rationale ─► System dialog ─► granted? ─► Use feature
      │                                                  │
      no                                                no
      ▼                                                  ▼
 Open Settings ◄──────────────────────────────── Show fallback UI
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Runtime permission | Asked while app runs | App चलते समय माँगी गई permission |
| Rationale | Reason shown to user | User को दिया गया कारण |
| Blocked | User picked "don't ask again" | User ने दोबारा न पूछने को कहा |
| Config plugin | Edits native config from app.json | app.json से native config बदलना |

---

## ⚡ 3-Line Summary
English: Declare permissions in the manifest, then ask at runtime in context.
Handle denied and blocked states with fallbacks and Settings link.
Android 13+ needs runtime notification permission.

Hindi: पहले manifest में declare करो, फिर सही समय पर runtime पर माँगो।
Denied और blocked state के लिए fallback और Settings link दो।
Android 13+ में notification permission भी runtime पर चाहिए।

---

## ➡️ Next Topic
**200. App Icons Setup (Android)** — permissions के बाद app की पहचान: icon।
