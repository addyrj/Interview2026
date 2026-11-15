# 198. AndroidManifest.xml — Important Settings
# हिंदी में: AndroidManifest.xml — ज़रूरी Settings
# Platform: Android ✅ | iOS ❌ (iOS का equivalent Info.plist है)

> Target: **Expo SDK 52 (React Native 0.76)** — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
`AndroidManifest.xml` is the "ID card" of your Android app. It tells the Android OS the app's package name, permissions, screens (Activities), deep links and hardware needs. Without it, Android will not install or launch your app.

## 🔵 सरल परिभाषा (Hindi)
`AndroidManifest.xml` आपके Android app का "ID card" है। इसमें app का package name, permissions, screens (Activities), deep links और hardware requirements लिखी होती हैं। इसके बिना Android app को install या launch नहीं करेगा।

---

## 🔴 Problem it Solves
- Android OS needs to know *before* running code: what permissions, which Activity opens first, which URLs the app handles.
- Play Store uses it to filter devices (e.g. app needs camera → hide from devices without camera).
- Without a central declaration, every app could silently access the camera/location.

## 🔴 यह क्यों बना? (Hindi)
- Android को code चलाने से *पहले* पता होना चाहिए कि app को कौन-सी permissions चाहिए और पहली screen कौन-सी है।
- Play Store इसी file से तय करता है कि app किस device पर दिखेगा।
- Manifest की वजह से कोई app बिना बताए camera/location access नहीं कर सकता।

---

## 🟢 How it Works — Step by Step
```
Step 1 → Build tool (Gradle) merges ALL manifests: your app + every library's manifest
Step 2 → Final merged manifest is packed inside the APK/AAB
Step 3 → Play Store reads it → shows permissions, filters devices
Step 4 → On install, Android reads <uses-permission> → grants install-time permissions
Step 5 → On launch, Android finds the <activity> with MAIN + LAUNCHER → starts it
Step 6 → React Native's MainActivity loads the JS bundle and shows your UI
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Gradle आपके app और सभी libraries के manifests को merge करता है
Step 2 → Final manifest APK/AAB के अंदर pack हो जाता है
Step 3 → Play Store इसे पढ़कर permissions और device filter दिखाता है
Step 4 → Install पर Android <uses-permission> पढ़कर permissions देता है
Step 5 → Launch पर MAIN + LAUNCHER वाली <activity> start होती है
Step 6 → MainActivity JS bundle load करके आपकी UI दिखाती है
```

---

## 🟡 Real World Example
**Swiggy** opens `swiggy://restaurant/123` from a WhatsApp link — that works because the manifest has an `intent-filter` for the `swiggy` scheme. **Paytm** declares `CAMERA` (QR scan) and `READ_SMS`-style permissions in the manifest; **Zomato** declares `ACCESS_FINE_LOCATION` to find nearby restaurants.

## 🟡 Real Example Hindi mein
**Swiggy** में WhatsApp link `swiggy://restaurant/123` पर tap करने से app खुलता है — क्योंकि manifest में `swiggy` scheme का `intent-filter` है। **Paytm** QR scan के लिए `CAMERA` permission declare करता है, **Zomato** nearby restaurants के लिए `ACCESS_FINE_LOCATION`।

---

## 💻 Code Example — Basic
Bare/CLI project: `android/app/src/main/AndroidManifest.xml`
```xml
<!-- Root tag of the manifest; xmlns:android defines the "android:" prefix -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Permission: allow network calls (fetch/axios) -->
    <uses-permission android:name="android.permission.INTERNET" />
    <!-- Permission: needed for camera features (asked at runtime also) -->
    <uses-permission android:name="android.permission.CAMERA" />

    <!-- Hardware: camera is optional, so app still shows on devices without one -->
    <uses-feature android:name="android.hardware.camera" android:required="false" />

    <!-- Application tag: global app settings -->
    <application
        android:name=".MainApplication"            <!-- Application class that starts React Native -->
        android:label="@string/app_name"           <!-- Name shown under the launcher icon -->
        android:icon="@mipmap/ic_launcher"         <!-- Normal app icon -->
        android:roundIcon="@mipmap/ic_launcher_round" <!-- Round icon for some launchers -->
        android:allowBackup="false"                <!-- Do not back up app data to Google Drive -->
        android:theme="@style/AppTheme">           <!-- Theme (also controls splash) -->

        <!-- Main screen: React Native has a single Activity -->
        <activity
            android:name=".MainActivity"
            android:exported="true"                 <!-- REQUIRED on Android 12+ when intent-filter exists -->
            android:launchMode="singleTask"         <!-- Reuse existing instance, helps deep links -->
            android:windowSoftInputMode="adjustResize" <!-- Keyboard resizes the layout -->
            android:screenOrientation="portrait">   <!-- Lock to portrait -->

            <!-- This filter makes it the launcher screen -->
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```
> Note: XML comments inside a tag (as above) are for teaching only — real XML does not allow `<!-- -->` inside a start tag. Remove them before copying.

## 💻 Code Example — Advanced
Deep links + cleartext + Expo config (managed workflow, `app.json`). Expo generates the manifest for you:
```json
{
  "expo": {
    "name": "FoodApp",
    "slug": "food-app",
    "scheme": "foodapp",
    "orientation": "portrait",
    "android": {
      "package": "com.mycompany.foodapp",
      "versionCode": 12,
      "permissions": ["CAMERA", "ACCESS_FINE_LOCATION"],
      "blockedPermissions": ["android.permission.RECORD_AUDIO"],
      "softwareKeyboardLayoutMode": "resize",
      "allowBackup": false,
      "intentFilters": [
        {
          "action": "VIEW",
          "autoVerify": true,
          "data": [{ "scheme": "https", "host": "foodapp.in", "pathPrefix": "/restaurant" }],
          "category": ["BROWSABLE", "DEFAULT"]
        }
      ]
    },
    "plugins": [
      ["expo-build-properties", { "android": { "usesCleartextTraffic": false } }]
    ]
  }
}
```
```bash
# Generate the native android/ folder from app.json (managed -> prebuild)
npx expo prebuild --platform android
# Open and inspect the generated manifest
cat android/app/src/main/AndroidManifest.xml
# See the FINAL merged manifest of a built APK (Android SDK build-tools needed)
aapt2 dump xmltree app-release.apk --file AndroidManifest.xml
```
**Error handling tip:** if build fails with "Manifest merger failed", check library conflicts and use `tools:replace="android:allowBackup"` on `<application>` (add `xmlns:tools="http://schemas.android.com/tools"` on root).

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Config file | `AndroidManifest.xml` | `Info.plist` + entitlements |
| Permissions | `<uses-permission>` | Usage description strings (`NSCameraUsageDescription`) |
| Deep links | `<intent-filter>` | URL Types + Associated Domains |
| App name/icon | `android:label`, `android:icon` | `CFBundleDisplayName`, Asset Catalog |
| Expo key | `expo.android.*` | `expo.ios.infoPlist`, `expo.ios.*` |

---

## 🟠 Expo vs CLI Difference
Expo way (edit `app.json`, no XML touching):
```json
{ "expo": { "android": { "permissions": ["CAMERA"], "package": "com.mycompany.foodapp" } } }
```
CLI way (edit XML directly):
```xml
<uses-permission android:name="android.permission.CAMERA" />
```
> Expo: changes are regenerated on every `prebuild`/EAS build — manual XML edits in a managed project get overwritten. Use a **config plugin** for custom edits. CLI: you own the file.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting `android:exported="true"` on Activity with intent-filter (Android 12+ install fails).
✅ Correct: Add `android:exported="true"` to the launcher/deep-link Activity.

❌ Mistake 2: Adding all permissions "just in case" — Play Store review flags sensitive ones (SMS, call log, background location).
✅ Correct: Request only what you use; use `blockedPermissions` to remove library-added ones.

❌ Mistake 3: Hand-editing manifest in an Expo managed project.
✅ Correct: Change `app.json` or write a config plugin.

❌ Mistake 4: Declaring `INTERNET` missing in release build (works in debug because debug manifest adds it).
✅ Correct: Declare `INTERNET` in the main manifest.

---

## 🧠 Tricky Interview Question
"App works in debug build but all API calls fail in release. No code changed. Why?"

Answer: The **debug** manifest (`android/app/src/debug/AndroidManifest.xml`) adds `INTERNET` and allows Metro connection. If the main manifest lacks `INTERNET`, release builds have no network. Another cause: release blocks HTTP (cleartext) traffic from API 28+ — use HTTPS or set `usesCleartextTraffic` deliberately.

---

## ⚫ Interview Questions + Answers
Q1: What is `android:exported`?
A1: It says whether other apps/OS can start the component. From Android 12 (API 31) it must be set explicitly for components with an intent-filter.

Q2: Difference between `versionCode` and `versionName`?
A2: `versionCode` is an integer Play Store uses to order releases (must increase each upload). `versionName` is the human-readable string like "1.4.2".

Q3: How are manifests merged?
A3: Gradle manifest merger combines app + library manifests; conflicts are resolved with `tools:` attributes (`replace`, `remove`, `merge`).

Q4: How to change permissions in Expo managed workflow?
A4: `android.permissions` / `blockedPermissions` in `app.json`, or via a library's config plugin.

Q5: What does `launchMode="singleTask"` do?
A5: Keeps one instance of the Activity, so a deep link reuses the running app rather than opening a second copy.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Adding permissions, deep links, orientation lock, keyboard behaviour.
- Debugging install failures or "app not visible on Play Store for my device".

❌ Avoid when:
- You are in Expo managed workflow — prefer `app.json`/config plugins over direct edits.
- Setting values you can set at runtime (e.g. orientation via `expo-screen-orientation`).

---

## 📊 Visual Diagram
```
 app.json (Expo)                  android/app/src/main/AndroidManifest.xml
      │  prebuild                              │
      └──────────────► generates ◄─────────────┘
                              │
   Library manifests ──► Gradle Manifest Merger ──► Final Manifest ──► APK/AAB
                                                          │
                                   ┌──────────────────────┼───────────────────┐
                                   ▼                      ▼                   ▼
                              Play Store            Android OS           Package installer
                          (device filter)     (launch Activity,       (shows permissions)
                                                 deep links)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Manifest | App declaration file | App की declaration file |
| Activity | One screen/entry point | एक screen/entry point |
| Intent-filter | Declares what URLs/actions app handles | कौन से URL/actions app handle करेगा |
| Permission | Access to protected resource | Protected resource की access |
| versionCode | Integer build number | Integer build number |
| Manifest merger | Combines all manifests | सभी manifests को जोड़ना |

---

## ⚡ 3-Line Summary
English: AndroidManifest.xml declares package, permissions, Activities and deep links.
In Expo you configure it via `app.json`; in CLI you edit the XML.
Always set `exported`, keep permissions minimal, and bump `versionCode` per release.

Hindi: AndroidManifest.xml में package, permissions, Activities और deep links declare होते हैं।
Expo में `app.json` से configure करते हैं; CLI में सीधे XML edit करते हैं।
`exported` set करो, permissions कम रखो, और हर release पर `versionCode` बढ़ाओ।

---

## ➡️ Next Topic
**199. App Permissions in Android** — manifest में declare करने के बाद runtime पर permission कैसे माँगें।
