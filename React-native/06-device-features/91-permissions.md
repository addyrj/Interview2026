# 91. Permissions in React Native
# हिंदी में: React Native में Permissions कैसे Handle करें?
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
Before accessing device features like camera, location, microphone, or contacts, you must **request permission** from the user at runtime. On iOS, permissions must be declared in `Info.plist` with a reason string. On Android, they must be in `AndroidManifest.xml`. For apps using Expo, use `expo-*` modules which handle permission declarations automatically. For bare React Native, use `react-native-permissions` for a unified API.

## 🔵 सरल परिभाषा (Hindi)
Camera, location, microphone, या contacts access करने से पहले user से runtime पर **permission request** करनी होती है। iOS पर permissions `Info.plist` में reason string के साथ declare करनी होती हैं। Android पर `AndroidManifest.xml` में। Expo apps में `expo-*` modules permission declarations automatically handle करते हैं। Bare React Native में `react-native-permissions` unified API देता है।

---

## 🔴 Problem it Solves
```
SECURITY PROBLEM: Apps shouldn't access private data without user consent
  Camera → captures photos/video of user
  Location → tracks user's real-time position (Zomato tracking!)
  Contacts → user's entire contact list
  Microphone → records audio
  Notifications → sends push messages

WITHOUT PERMISSIONS:
  App: "Let me just access your location..." 
  → Privacy violation! Users don't control their data.

WITH PERMISSIONS:
  App shows dialog: "Allow 'Swiggy' to access your location while using the app?"
  User: "Allow" / "Don't Allow" / "Allow Once"
  → User is in control ✅

TWO LEVELS:
  1. DECLARATION (build time): Tell the OS what permissions you MIGHT use
     Android: AndroidManifest.xml
     iOS: Info.plist with usage description

  2. REQUEST (runtime): Actually ask the user when you need it
     Show system dialog → user grants/denies
```

## 🔴 यह क्यों बना? (Hindi)
```
Privacy protection: user की camera, location, contacts बिना consent access नहीं होनी चाहिए।
OS permission system: user control देता है।
App का काम: पहले declare करो (manifest/plist), फिर request करो (runtime dialog)।
```

---

## 🟢 How it Works — Step by Step

```
PERMISSION LIFECYCLE:
──────────────────────────────────────────────────────
  Step 1 → App build:
           Android: AndroidManifest.xml में permission add
           iOS: Info.plist में NSLocationWhenInUseUsageDescription etc.

  Step 2 → App runs, user does something requiring permission
           e.g., taps "Take Photo"

  Step 3 → App checks current status:
           'granted' → proceed
           'denied' → show settings redirect
           'unavailable' → feature not on this device
           'blocked' → user blocked, must go to Settings
           'limited' → iOS photo library partial access

  Step 4 → Status is 'undetermined' → request!
           System shows OS permission dialog
           User taps Allow/Don't Allow

  Step 5 → Response: 'granted' or 'denied'
           If denied: show reason + guide to settings

PERMISSION STATUS VALUES:
  RESULTS.GRANTED     → ✅ user allowed
  RESULTS.DENIED      → ❌ user denied (can request again on Android)
  RESULTS.BLOCKED     → 🚫 user denied multiple times (only Settings can fix)
  RESULTS.UNAVAILABLE → device doesn't have this feature
  RESULTS.LIMITED     → iOS 14+ photo partial access
```

## 🟢 कैसे काम करता है? (Hindi)
```
Check status → undetermined? → request → user grants/denies
Denied: Android पर फिर request हो सकती है
Blocked: Settings पर redirect करना पड़ेगा
हर platform का behavior अलग है!
```

---

## 🟡 Real World Example
**Swiggy Delivery Tracking:** App taps "Track Order" → needs location permission. (1) Checks current permission. (2) If not granted: shows dialog "Swiggy needs your location to show accurate delivery tracking". (3) User taps Allow → location updates begin → map shows delivery partner. (4) If user taps Deny: shows message "Location access needed for tracking. Enable in Settings" with a button to open Settings. (5) Background location (for delivery partner app): requires additional `ACCESS_BACKGROUND_LOCATION` permission on Android.

## 🟡 Real Example Hindi मे
**Swiggy Tracking:** "Track Order" tap → location permission check → not granted? → dialog show → user allow → location updates शुरू → delivery partner map पर। Deny: Settings redirect button। Background location (delivery partner): additional permission चाहिए।

---

## 💻 Code Example — Basic (Expo)

```jsx
// EXPO WAY — using expo-location (no native config needed!)
import * as Location from 'expo-location';
import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, Linking } from 'react-native';

function LocationPermissionExample() {
  const [location, setLocation] = useState(null);
  const [status, setStatus] = useState('unknown');

  const requestLocation = async () => {
    // Request foreground location permission
    const { status: permStatus } = await Location.requestForegroundPermissionsAsync();
    setStatus(permStatus);

    if (permStatus === 'granted') {
      // Permission granted — get location
      const loc = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
      });
      setLocation(loc.coords);
    } else if (permStatus === 'denied') {
      // User denied — explain and offer Settings
      Alert.alert(
        'Location Required',
        'Location access is needed to show nearby restaurants. Please enable it in Settings.',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Open Settings', onPress: () => Linking.openSettings() },
        ]
      );
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.status}>Permission: {status}</Text>
      {location && (
        <Text style={styles.location}>
          Lat: {location.latitude.toFixed(4)}, Lng: {location.longitude.toFixed(4)}
        </Text>
      )}
      <TouchableOpacity style={styles.button} onPress={requestLocation}>
        <Text style={styles.buttonText}>Get My Location</Text>
      </TouchableOpacity>
    </View>
  );
}

// Camera permission with expo-camera:
import { Camera } from 'expo-camera';

function CameraPermissionExample() {
  const [permission, requestPermission] = Camera.useCameraPermissions();
  // permission.status: 'granted' | 'denied' | 'undetermined'

  if (!permission) return null;

  if (!permission.granted) {
    return (
      <View>
        <Text>Camera access needed to take photos</Text>
        <TouchableOpacity onPress={requestPermission}>
          <Text>Allow Camera</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return <Camera style={{ flex: 1 }} />;
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 20, gap: 12 },
  status: { fontSize: 16, textAlign: 'center' },
  location: { fontSize: 14, color: '#666', textAlign: 'center' },
  button: { backgroundColor: '#f97316', padding: 16, borderRadius: 8, alignItems: 'center' },
  buttonText: { color: '#fff', fontWeight: '700' },
});
```

## 💻 Code Example — Advanced (React Native CLI + react-native-permissions)

```jsx
// CLI WAY — react-native-permissions
// npm install react-native-permissions
// Requires native config in android/app/build.gradle + ios/Podfile

import {
  check,
  request,
  PERMISSIONS,
  RESULTS,
  openSettings,
  Permission,
} from 'react-native-permissions';
import { Platform, Alert } from 'react-native';

// Platform-specific permission constants
const LOCATION_PERMISSION = Platform.select({
  android: PERMISSIONS.ANDROID.ACCESS_FINE_LOCATION,
  ios: PERMISSIONS.IOS.LOCATION_WHEN_IN_USE,
});

const CAMERA_PERMISSION = Platform.select({
  android: PERMISSIONS.ANDROID.CAMERA,
  ios: PERMISSIONS.IOS.CAMERA,
});

// Reusable permission request utility
async function requestPermission(
  permission: Permission,
  {
    title = 'Permission Required',
    message = 'This feature requires permission.',
  } = {}
): Promise<boolean> {

  // Step 1: Check current status
  const currentStatus = await check(permission);
  console.log('Current status:', currentStatus);

  switch (currentStatus) {
    case RESULTS.GRANTED:
      return true;  // already granted!

    case RESULTS.DENIED:
      // Can ask again (Android: first time; iOS: first time)
      const newStatus = await request(permission);
      return newStatus === RESULTS.GRANTED;

    case RESULTS.BLOCKED:
    case RESULTS.LIMITED:
      // User permanently denied — must go to Settings
      Alert.alert(
        title,
        `${message} Please enable it in the app settings.`,
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Open Settings', onPress: openSettings },
        ]
      );
      return false;

    case RESULTS.UNAVAILABLE:
      Alert.alert('Not Available', 'This feature is not available on your device.');
      return false;

    default:
      return false;
  }
}

// Usage:
async function takePhoto() {
  const granted = await requestPermission(CAMERA_PERMISSION, {
    title: 'Camera Access',
    message: 'Swiggy needs camera access to let you add food photos.',
  });

  if (granted) {
    // Open camera
  }
}

async function showNearbyRestaurants() {
  const granted = await requestPermission(LOCATION_PERMISSION, {
    title: 'Location Access',
    message: 'Find restaurants near you.',
  });

  if (granted) {
    // Start location tracking
  }
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Declaration | `AndroidManifest.xml` | `Info.plist` (with description string) |
| Runtime request | First time only (can re-request after denial) | First time only (then must go to Settings) |
| "Deny" behavior | Can ask again | "Never ask again" after second denial |
| Background location | Separate `ACCESS_BACKGROUND_LOCATION` | `LOCATION_ALWAYS` (not `WHEN_IN_USE`) |
| Photo library | Full access | Full or limited (iOS 14+) |
| Request at startup | Bad practice | Bad practice |

---

## 🟠 Expo vs CLI Difference

Expo way:
```json
// app.json — declare permissions (Expo handles manifest/plist)
{
  "expo": {
    "android": {
      "permissions": ["ACCESS_FINE_LOCATION", "CAMERA"]
    },
    "ios": {
      "infoPlist": {
        "NSLocationWhenInUseUsageDescription": "To show nearby restaurants",
        "NSCameraUsageDescription": "To take food photos"
      }
    }
  }
}
// Then: import * as Location from 'expo-location'; (handles runtime request)
```

CLI way:
```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.CAMERA" />
```

```xml
<!-- ios/MyApp/Info.plist -->
<key>NSLocationWhenInUseUsageDescription</key>
<string>To show nearby restaurants</string>
<key>NSCameraUsageDescription</key>
<string>To take food photos</string>
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Requesting permissions at app launch (before need)
```jsx
// WRONG: Ask for all permissions when app opens
useEffect(() => {
  requestLocationPermission();  // ❌ user didn't trigger this!
  requestCameraPermission();    // ❌ before they need camera
  requestNotifications();       // ❌ all at once = user rejects all
}, []);

// CORRECT: Request Just In Time (when user triggers the feature)
const handleTakePhoto = async () => {
  const granted = await requestPermission(CAMERA_PERMISSION);
  if (granted) launchCamera();
};

// Users are much more likely to grant permission when they understand WHY
// "App wants camera access" vs "You just tapped Take Photo" = very different!
```

❌ **Mistake 2:** Not handling BLOCKED status
```jsx
// WRONG: Just check if granted, ignore blocked
const status = await check(CAMERA_PERMISSION);
if (status !== RESULTS.GRANTED) {
  await request(CAMERA_PERMISSION);  // ❌ requesting when BLOCKED does nothing!
}

// CORRECT: Handle all states
if (status === RESULTS.BLOCKED) {
  // Must redirect to Settings — request() has no effect!
  Alert.alert('Camera Blocked', 'Please enable in Settings', [
    { text: 'Open Settings', onPress: openSettings }
  ]);
}
```

❌ **Mistake 3:** Missing NSCameraUsageDescription (iOS rejection)
```
iOS App Store REJECTS apps that:
  ❌ Access camera without NSCameraUsageDescription in Info.plist
  ❌ Access location without NSLocationWhenInUseUsageDescription
  ❌ Have vague description strings like "This app uses camera"

CORRECT: Specific, user-facing reason:
  ✅ "Allow Swiggy to access your camera to scan restaurant QR codes"
  ✅ "Your location helps us find nearby restaurants and deliver accurately"
  Apple reviewers check these!
```

---

## 🧠 Tricky Interview Question

**Q: A user denied camera permission twice on iOS. Now `request()` does nothing. How do you guide them to re-enable it?**

**Answer:** After the second denial on iOS, the permission is `BLOCKED` — `request()` silently does nothing (no dialog is shown). The ONLY way to fix this is: (1) Check status is `RESULTS.BLOCKED`. (2) Show a custom in-app dialog explaining WHY the camera is needed. (3) Provide a button that calls `Linking.openSettings()` (or `openSettings()` from react-native-permissions). This takes the user to the app's settings page where they can manually toggle camera access. (4) When the user comes back to the app (via `AppState` change), re-check the permission. This is the only flow — you cannot programmatically grant permissions. On Android, there's a third chance: "Never ask again" checkbox in the denial dialog; before that, `request()` works on the second attempt.

---

## ⚫ Interview Questions + Answers

**Q1: What are the possible permission status values in React Native?**
A1: Five values (from `react-native-permissions`): `GRANTED` — user allowed. `DENIED` — user denied (can still ask again, especially on Android). `BLOCKED` — user denied multiple times / selected "Never ask again" (only Settings can fix). `UNAVAILABLE` — feature doesn't exist on this device (e.g., camera on a device with no camera). `LIMITED` — iOS 14+ photo library partial access. In Expo modules, these map to `'granted'`, `'denied'`, `'undetermined'` (not yet asked), and need `Linking.openSettings()` when denied.

**Q2: What is the difference between foreground and background location?**
A2: **Foreground location** (`ACCESS_FINE_LOCATION` / `LOCATION_WHEN_IN_USE`): app can track location only while the user is actively using the app. **Background location** (`ACCESS_BACKGROUND_LOCATION` / `LOCATION_ALWAYS`): app can track location even when in background. Background location requires: (1) Additional permission declaration. (2) Google Play Store asks for a specific use case justification. (3) iOS requires `LOCATION_ALWAYS` permission + "Always" selected by user. (4) iOS 13+: user must first grant "While Using" then separately select "Always". Use case: delivery partner apps (Dunzo, Swiggy delivery side) need background tracking; Swiggy customer app only needs foreground.

**Q3: How do you declare permissions in an Expo app?**
A3: In `app.json` under `expo.android.permissions` (array of Android permission strings) and `expo.ios.infoPlist` (object of iOS usage description keys). Example: `{ "expo": { "android": { "permissions": ["CAMERA", "ACCESS_FINE_LOCATION"] }, "ios": { "infoPlist": { "NSCameraUsageDescription": "To scan QR codes" } } } }`. EAS Build uses these to generate the correct native files. With `expo-*` modules, some permissions are added automatically when you install the module.

**Q4: Why is it bad practice to request all permissions at app startup?**
A4: (1) Users see a barrage of permission dialogs before understanding the app's value — they click "Deny" reflexively. (2) Denied permissions at startup = feature broken when needed later, frustrating UX. (3) App stores penalize apps with excessive permissions (both Google Play and App Store review processes). (4) Users' trust: "Why does a calculator need my location?" Best practice: request permission exactly when the user triggers the feature — the context makes the request feel natural and justified.

**Q5: How do you handle the case where the user comes back from Settings after enabling a permission?**
A5: Use `AppState` from React Native to detect when the app returns to the foreground. When `AppState.currentState` changes to `'active'` (from `'background'`), re-check the permission status. If it changed to `GRANTED`, proceed. Pattern: `const subscription = AppState.addEventListener('change', state => { if (state === 'active') { checkPermission().then(status => { if (status === RESULTS.GRANTED) proceedWithFeature(); }); } })`. Don't forget to `remove()` the subscription in cleanup.

---

## 🔷 When to Use + When Not to Use
✅ **Request permissions when:**
- User taps a button that requires the permission (camera button → camera permission)
- First time a feature that needs permission is used
- Context clearly explains why permission is needed

❌ **Don't request permissions:**
- At app startup
- Without clear UI explaining why
- Multiple permissions in one go
- After "blocked" status (redirect to Settings instead)

---

## 📊 Visual Diagram

```
PERMISSION FLOW:
──────────────────────────────────────────────────────
  User taps "Take Photo"
       │
       ▼
  check(CAMERA_PERMISSION)
       │
       ├── GRANTED → Open Camera ✅
       │
       ├── UNDETERMINED → request() → OS Dialog shown
       │      │
       │      ├── User taps "Allow" → GRANTED → Open Camera ✅
       │      └── User taps "Don't Allow" → DENIED
       │             │
       │             └── Show in-app explanation
       │
       ├── DENIED → request() → (Android: try again) → (iOS: blocked after 2nd)
       │
       ├── BLOCKED → Custom dialog + "Open Settings" button
       │             → openSettings() → user manually enables
       │             → user returns → AppState 'active' → re-check
       │
       └── UNAVAILABLE → "Camera not available on this device"

ANDROID vs iOS DECLARATION:
──────────────────────────────────────────────────────
  Android (AndroidManifest.xml):         iOS (Info.plist):
  <uses-permission                       NSCameraUsageDescription:
    android:name="android.permission     "Used to scan QR codes"
    .CAMERA" />

  Expo: app.json "permissions"           Expo: app.json "infoPlist"
  array handles this automatically       object handles this automatically
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Permission | Right to access device feature | Device feature access का अधिकार |
| GRANTED | User allowed | User ने allow किया |
| DENIED | User denied (can ask again) | User ने deny किया (फिर पूछ सकते) |
| BLOCKED | Permanently denied | Permanently deny किया |
| Foreground location | Location only while app in use | App use के दौरान location |
| Background location | Location even when backgrounded | Background में भी location |
| Info.plist | iOS permission declarations | iOS permission declarations |
| AndroidManifest | Android permission declarations | Android permission declarations |

---

## ⚡ 3-Line Summary
**English:**
1. Always check permission status before accessing device features; request Just In Time (when user triggers the feature, not at startup).
2. Status values: `GRANTED` (proceed), `DENIED` (can request again), `BLOCKED` (redirect to Settings), `UNAVAILABLE` (device lacks feature).
3. Expo: declare in `app.json` + use `expo-*` modules; CLI: `AndroidManifest.xml` + `Info.plist` + `react-native-permissions` for runtime checks.

**Hindi:**
1. Device features access से पहले हमेशा permission status check करो; Just In Time request करो (startup पर नहीं)।
2. Status: `GRANTED` (proceed), `DENIED` (फिर request), `BLOCKED` (Settings redirect), `UNAVAILABLE` (device में नहीं)।
3. Expo: `app.json` में declare; CLI: `AndroidManifest.xml` + `Info.plist` + `react-native-permissions`।

---

## ➡️ Next Topic
**92. Camera — expo-camera / react-native-vision-camera** — photos, video, QR scanning।
