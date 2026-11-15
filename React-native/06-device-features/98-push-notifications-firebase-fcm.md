# 98. Push Notifications — Firebase (FCM)
# हिंदी में: Push Notifications — Firebase Cloud Messaging (FCM)
# Platform: Android ✅ | iOS ✅ | Both ✅ (real device + dev build / bare CLI)

> Target: Expo SDK 52 (React Native 0.76) + `@react-native-firebase/app` + `@react-native-firebase/messaging` (check current docs — APIs change between SDKs / RNFirebase majors). Expo Go में यह नहीं चलता — **development build** (`eas build --profile development`) चाहिए।
> Note: `94` overview है, `97` expo-notifications है; यह file सीधे Firebase SDK (React Native Firebase) के बारे में है।

---

## 🔵 Simple Definition (English)
**FCM (Firebase Cloud Messaging)** is Google's free service that delivers push messages to Android and iOS (iOS via APNs behind the scenes). With React Native Firebase, the app gets an **FCM token**, your server sends messages to that token through the FCM HTTP v1 API, and the app handles them in foreground, background or killed state.

## 🔵 सरल परिभाषा (Hindi)
**FCM** Google की free service है जो Android और iOS (iOS में पीछे APNs के ज़रिए) पर push message पहुँचाती है। React Native Firebase से app को **FCM token** मिलता है, आपका server उस token पर FCM HTTP v1 API से message भेजता है, और app foreground, background या killed — हर state में उसे संभालता है।

---

## 🔴 Problem it Solves
```
❌ Server app ko tab message nahi bhej sakta jab app band ho
❌ Polling se battery aur data khatam hota hai
❌ Android (GCM/FCM) aur iOS (APNs) ke alag protocols
✅ FCM ek hi API se dono platforms, topics, segments
✅ Notification vs Data message dono supported
```

## 🔴 यह क्यों बना? (Hindi)
```
App बंद हो तो server सीधे फ़ोन तक नहीं पहुँच सकता।
बार-बार server से पूछना (polling) battery खाता है।
FCM एक ही जगह से Android + iOS दोनों को message भेजता है,
topics (जैसे "offers") पर group message भी भेज सकता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Firebase Console me project banao, Android/iOS app add karo
Step 2 → google-services.json (Android) + GoogleService-Info.plist (iOS) download
Step 3 → npx expo install @react-native-firebase/app @react-native-firebase/messaging
Step 4 → app.json: android.googleServicesFile, ios.googleServicesFile, plugins: ["@react-native-firebase/app"]
Step 5 → iOS: Apple Developer me APNs Auth Key (.p8) banao -> Firebase Console me upload
Step 6 → Android 13+: POST_NOTIFICATIONS runtime permission; iOS: messaging().requestPermission()
Step 7 → messaging().getToken() -> backend ko bhejo
Step 8 → Backend FCM HTTP v1 (service account OAuth) se message bhejta hai
Step 9 → onMessage (foreground) / setBackgroundMessageHandler (bg/killed) / onNotificationOpenedApp (tap)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Firebase project बनाएँ, दोनों platform की config files लें।
Step 2 → Packages install करें और app.json में files + plugin जोड़ें।
Step 3 → iOS के लिए APNs key Firebase में upload करें।
Step 4 → Permission लें और token backend को भेजें।
Step 5 → Foreground में onMessage चलता है; background/killed में
         setBackgroundMessageHandler; tap पर onNotificationOpenedApp / getInitialNotification।
```

---

## 🟡 Real World Example
**Zomato:** "50% off tonight" push is sent to the topic `offers_delhi`, so all Delhi users subscribed get it. **Swiggy:** a **data message** with `orderId` wakes the app in the background to update live tracking. **Paytm:** "Payment received" notification; tapping opens the transaction detail screen.

## 🟡 Real Example Hindi mein
**Zomato:** "आज रात 50% off" push topic `offers_delhi` पर भेजा जाता है, उस topic को subscribe करने वाले सब Delhi users को मिलता है। **Swiggy:** `orderId` वाला **data message** app को background में जगाकर live tracking अपडेट करता है। **Paytm:** "Payment received" पर tap करने से transaction detail खुलती है।

---

## 💻 Code Example — Basic
```jsx
// FcmBasic.jsx — permission + token + foreground message
import React, { useEffect, useState } from 'react';                  // React
import { View, Text, Alert, Platform, PermissionsAndroid } from 'react-native'; // RN
import messaging from '@react-native-firebase/messaging';            // FCM SDK

async function askPermission() {
  if (Platform.OS === 'android' && Platform.Version >= 33) {         // Android 13+ me runtime permission
    const r = await PermissionsAndroid.request(
      PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS              // notification permission
    );
    return r === PermissionsAndroid.RESULTS.GRANTED;                 // true/false
  }
  const status = await messaging().requestPermission();              // iOS prompt (Android <13 me auto granted)
  return (
    status === messaging.AuthorizationStatus.AUTHORIZED ||           // allowed
    status === messaging.AuthorizationStatus.PROVISIONAL             // quietly allowed
  );
}

export default function FcmBasic() {
  const [token, setToken] = useState('');                            // FCM token state

  useEffect(() => {
    (async () => {
      if (!(await askPermission())) return;                          // user ne mana kiya
      const t = await messaging().getToken();                        // device ka FCM token
      setToken(t);                                                   // screen par dikhao
    })();

    const unsub = messaging().onMessage(async (msg) => {             // app khula (foreground) hai
      Alert.alert(msg.notification?.title ?? 'New', msg.notification?.body ?? ''); // simple alert
    });
    return unsub;                                                    // cleanup: listener hatao
  }, []);

  return <View style={{ padding: 40 }}><Text selectable>{token || 'No token yet'}</Text></View>;
}
```

## 💻 Code Example — Advanced
```jsx
// index.js (entry) — background handler ko React ke bahar, top level par register karo
import { AppRegistry } from 'react-native';                          // RN registry
import messaging from '@react-native-firebase/messaging';            // FCM
import App from './App';                                             // root

messaging().setBackgroundMessageHandler(async (remoteMessage) => {   // bg + killed state
  console.log('BG message:', remoteMessage.messageId, remoteMessage.data); // headless JS, UI nahi
});
AppRegistry.registerComponent('main', () => App);                    // Expo me expo-router/entry ya registerRootComponent
```
```jsx
// useFcm.js — token refresh, tap navigation, topics, error handling
import { useEffect } from 'react';
import messaging from '@react-native-firebase/messaging';

export function useFcm(navigation, saveTokenToServer) {
  useEffect(() => {
    // 1) Token refresh: FCM kabhi bhi token badal sakta hai
    const offRefresh = messaging().onTokenRefresh((t) => {
      saveTokenToServer(t).catch(console.warn);                      // naya token server ko
    });

    // 2) Background me tha, notification tap hua
    const offOpen = messaging().onNotificationOpenedApp((m) => {
      if (m.data?.orderId) navigation.navigate('Tracking', { id: m.data.orderId });
    });

    // 3) App killed tha, notification tap se khula
    messaging().getInitialNotification().then((m) => {
      if (m?.data?.orderId) navigation.navigate('Tracking', { id: m.data.orderId });
    });

    // 4) Topic subscribe (server se group message ke liye)
    messaging().subscribeToTopic('offers_delhi').catch(console.warn);

    return () => { offRefresh(); offOpen(); };                       // cleanup
  }, [navigation, saveTokenToServer]);
}

// ---- Backend (Node, firebase-admin) : data + notification message ----
// await admin.messaging().send({
//   token: deviceToken,
//   notification: { title: 'Order update', body: 'Out for delivery' },
//   data: { orderId: '42' },                    // data values hamesha string
//   android: { priority: 'high' },
//   apns: { payload: { aps: { sound: 'default' } } },
// });
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Delivery path | FCM directly | FCM -> APNs -> device |
| Setup file | `google-services.json` | `GoogleService-Info.plist` + APNs `.p8` key |
| Permission | Android 13+ `POST_NOTIFICATIONS` runtime | `requestPermission()` always (alert/badge/sound) |
| Simulator | Emulator with Google Play works | Remote push needs real device (newer simulators limited) |
| Notification channel | Required (Android 8+), FCM default channel auto | Not applicable |
| Background capability | Works by default | Need "Push Notifications" + "Background Modes -> Remote notifications" capability |
| Silent push | data-only high priority | `content-available: 1` (throttled by OS) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// app.json (config plugin) — prebuild native folders khud banata hai; Expo Go me NAHI chalega
// {
//   "expo": {
//     "android": { "googleServicesFile": "./google-services.json" },
//     "ios": { "googleServicesFile": "./GoogleService-Info.plist" },
//     "plugins": ["@react-native-firebase/app", "@react-native-firebase/messaging"]
//   }
// }
// iOS pe static frameworks chahiye: expo-build-properties plugin => ios.useFrameworks: "static"
// eas build --profile development --platform all
import messaging from '@react-native-firebase/messaging';        // JS code same
```
CLI way:
```jsx
// npm i @react-native-firebase/app @react-native-firebase/messaging
// Android: google-services.json -> android/app/, classpath + apply plugin 'com.google.gms.google-services'
// iOS: GoogleService-Info.plist ko Xcode me add karo, cd ios && pod install, Xcode me capabilities on
import messaging from '@react-native-firebase/messaging';        // JS code same
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Expo Go में FCM test करना।
✅ Correct: Development build (`eas build --profile development`) बनाएँ — native module चाहिए।

❌ Mistake 2: `setBackgroundMessageHandler` को component के अंदर register करना।
✅ Correct: `index.js` में top-level पर, React render के बाहर।

❌ Mistake 3: iOS पर APNs key Firebase में upload करना भूल जाना (token मिलता है पर push नहीं आता)।
✅ Correct: Apple Developer से `.p8` key बनाकर Firebase Console -> Cloud Messaging में upload करें।

❌ Mistake 4: Android 13+ पर `POST_NOTIFICATIONS` न माँगना।
✅ Correct: `PermissionsAndroid.request(PERMISSIONS.POST_NOTIFICATIONS)`।

❌ Mistake 5: `data` में number/object भेजना।
✅ Correct: `data` की सब values string होनी चाहिए (object को JSON string बनाएँ)।

❌ Mistake 6: Token एक बार save करके भूल जाना।
✅ Correct: `onTokenRefresh` सुनें और server अपडेट करें।

---

## 🧠 Tricky Interview Question
App is **killed**. Server sends a message containing both `notification` and `data`. Which handler runs — `onMessage` or `setBackgroundMessageHandler`? And what if it is **data-only**?

Answer: `onMessage` runs only in the **foreground**. With a `notification` payload and the app in background/killed, the **system tray shows it automatically** (no JS runs); tapping triggers `getInitialNotification` / `onNotificationOpenedApp`. A **data-only** message runs `setBackgroundMessageHandler` (headless JS) on Android; on iOS data-only needs `content-available` and the OS may throttle/skip it, and a force-quit (swiped) iOS app will not wake for silent push.

हिंदी: `onMessage` सिर्फ़ foreground में चलता है। Notification payload वाला message background/killed में system खुद दिखाता है। Data-only message पर `setBackgroundMessageHandler` चलता है। iOS में swipe-kill किए app को silent push नहीं जगाता।

---

## ⚫ Interview Questions + Answers
Q1: FCM token क्या है और कब बदलता है?
A1: Device+app instance की unique ID. App reinstall, data clear, restore, या FCM के rotate करने पर बदलता है; इसलिए `onTokenRefresh` सुनें।

Q2: Notification message vs data message?
A2: Notification message system tray में खुद दिखता है (limited control). Data message हमेशा app code को मिलता है — custom UI/logic के लिए।

Q3: FCM vs expo-notifications (Expo push)?
A3: Expo push एक wrapper है जो token + HTTP API देता है और पीछे FCM/APNs use करता है. Direct FCM में topics, analytics, full control मिलता है, पर dev build + native setup लगता है।

Q4: iOS पर FCM कैसे काम करता है?
A4: FCM message APNs को देता है; इसलिए APNs `.p8` key Firebase में upload और capabilities चालू होनी ज़रूरी हैं।

Q5: Topic क्या है?
A5: Server-side group; `subscribeToTopic('offers')` करने वाले सब devices को एक ही send से message जाता है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Topics, segments, Firebase Analytics / A/B जैसे features चाहिए
- Bare React Native (CLI) project है
- Backend पहले से Firebase Admin use करता है

❌ Avoid when:
- Quick prototype in Expo Go (expo-notifications ज़्यादा आसान)
- Team को native config नहीं संभालना
- सिर्फ़ local reminders चाहिए (Local Notifications use करें)

---

## 📊 Visual Diagram
```
 Your Server ──(HTTP v1 + OAuth)──▶ FCM (Google)
                                      │
                 ┌────────────────────┴───────────────┐
                 ▼                                    ▼
           Android device                    APNs (Apple) ──▶ iPhone
                 │                                    │
   foreground: onMessage()              foreground: onMessage()
   bg/killed + notification: system tray
   bg/killed + data-only: setBackgroundMessageHandler()
   tap: onNotificationOpenedApp / getInitialNotification
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| FCM | Firebase Cloud Messaging | Google की push service |
| APNs | Apple Push Notification service | Apple की push service |
| FCM token | Unique device id for push | device की पहचान |
| Topic | Group to broadcast to | समूह जिसे message भेजें |
| Data message | Custom payload for app code | app के लिए custom डेटा |
| Headless JS | JS run without UI | बिना screen के JS चलना |

---

## ⚡ 3-Line Summary
English: FCM sends push to Android and iOS (via APNs) using a per-device token.
Handle foreground with onMessage, background with setBackgroundMessageHandler, taps with opened/initial notification.
It needs a dev build or bare CLI, not Expo Go.

Hindi: FCM token के ज़रिए Android और iOS (APNs से) पर push भेजता है।
Foreground में onMessage, background में setBackgroundMessageHandler, tap पर opened/initial notification।
इसके लिए dev build या bare CLI चाहिए, Expo Go नहीं।

---

## ➡️ Next Topic
**99. Local Notifications** — बिना server के app खुद reminder / schedule notification दिखाए।

---
