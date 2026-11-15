# 97. Push Notifications — expo-notifications
# हिंदी में: Push Notifications — expo-notifications
# Platform: Android ✅ | iOS ✅ | Both ✅ (real device चाहिए)

> Target: Expo SDK 52 (React Native 0.76) + expo-notifications + expo-device (check current docs — APIs change between SDKs; Expo Go पर Android remote push SDK 53+ में हटाया गया है — dev build use करें).
> Note: repo me `94-push-notifications.md` overview hai; ye file expo-notifications API detail me hai.

---

## 🔵 Simple Definition (English)
**expo-notifications** lets your app receive push notifications from a server and show local ones. You get an **Expo push token**, send it to your backend, the backend calls Expo's push service, and Expo forwards it to FCM (Android) / APNs (iOS).

## 🔵 सरल परिभाषा (Hindi)
**expo-notifications** से app server से भेजे गए push notifications पा सकता है और local notifications भी दिखा सकता है। App को **Expo push token** मिलता है, जो backend को दिया जाता है; backend Expo की push service को call करता है और वह FCM (Android) / APNs (iOS) तक पहुँचाती है।

---

## 🔴 Problem it Solves
```
❌ App band hone par user tak message kaise pahunche?
❌ FCM + APNs ka alag-alag setup, token, certificates
✅ Expo push service: ek token, ek HTTP API, dono platforms
✅ Listeners: foreground, tap (response), background
```

## 🔴 यह क्यों बना? (Hindi)
```
App बंद होने पर भी user को message पहुँचाना ज़रूरी है।
FCM और APNs अलग-अलग सेटअप माँगते हैं।
Expo एक token और एक API से दोनों संभाल देता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install expo-notifications expo-device expo-constants
Step 2 → Android: notification channel banao (setNotificationChannelAsync)
Step 3 → Real device check (Device.isDevice)
Step 4 → getPermissionsAsync → requestPermissionsAsync
Step 5 → getExpoPushTokenAsync({ projectId }) → "ExponentPushToken[xxxx]"
Step 6 → Token backend ko bhejo (user ke saath save)
Step 7 → Backend POST https://exp.host/--/api/v2/push/send
Step 8 → Expo → FCM/APNs → device
Step 9 → addNotificationReceivedListener (foreground), addNotificationResponseReceivedListener (tap)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Packages install, Android के लिए channel बनाएँ।
Step 2 → Permission माँगें, फिर Expo push token लें।
Step 3 → Token अपने backend में user के साथ save करें।
Step 4 → Backend Expo API को token और message भेजता है।
Step 5 → Foreground में handler तय करता है कि alert दिखे या नहीं; tap पर response listener navigate करता है।
```

---

## 🟡 Real World Example
**Swiggy:** "Your order is out for delivery" push arrives when the app is closed; tapping it opens the Order Tracking screen (response listener reads `data.orderId`). **Paytm:** cashback offers. While the app is open, the `setNotificationHandler` decides whether to show a banner.

## 🟡 Real Example Hindi mein
**Swiggy:** App बंद होने पर भी "Order out for delivery" push आता है; tap करने पर Order Tracking खुलता है (`data.orderId` से)। App खुला हो तो `setNotificationHandler` तय करता है कि banner दिखे या नहीं।

---

## 💻 Code Example — Basic
```jsx
// PushBasic.jsx — token lena aur dikhana
import React, { useEffect, useState } from 'react';           // React
import { View, Text, Platform } from 'react-native';          // RN
import * as Device from 'expo-device';                        // real device check
import * as Notifications from 'expo-notifications';          // push API
import Constants from 'expo-constants';                       // projectId ke liye

// Foreground me notification aaye to banner dikhao
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,                                    // alert (SDK 52; naye SDK me shouldShowBanner/List — docs dekho)
    shouldPlaySound: true,                                    // sound
    shouldSetBadge: false,                                    // badge nahi
  }),
});

async function registerForPush() {
  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', { // Android 8+ channel zaroori
      name: 'default',
      importance: Notifications.AndroidImportance.MAX,
    });
  }
  if (!Device.isDevice) return null;                          // simulator par push nahi
  let { status } = await Notifications.getPermissionsAsync(); // current permission
  if (status !== 'granted') {
    ({ status } = await Notifications.requestPermissionsAsync()); // prompt
  }
  if (status !== 'granted') return null;                      // user ne mana kiya
  const projectId = Constants.expoConfig?.extra?.eas?.projectId ?? Constants.easConfig?.projectId; // EAS projectId
  const { data } = await Notifications.getExpoPushTokenAsync({ projectId }); // token
  return data;                                                // ExponentPushToken[...]
}

export default function PushBasic() {
  const [token, setToken] = useState('');                     // token state
  useEffect(() => { registerForPush().then((t) => t && setToken(t)); }, []); // mount par register
  return <View style={{ padding: 40 }}><Text selectable>{token || 'No token'}</Text></View>;
}
```

## 💻 Code Example — Advanced
```jsx
// usePushNotifications.js — listeners + tap navigation + cleanup + backend send (Node snippet below)
import { useEffect, useRef } from 'react';
import * as Notifications from 'expo-notifications';

export function usePushNotifications(navigation) {
  const received = useRef();                                  // foreground listener ref
  const response = useRef();                                  // tap listener ref

  useEffect(() => {
    received.current = Notifications.addNotificationReceivedListener((n) => {
      console.log('Foreground push:', n.request.content.title); // app khula tha
    });

    response.current = Notifications.addNotificationResponseReceivedListener((r) => {
      const data = r.notification.request.content.data;       // payload data
      if (data?.orderId) navigation.navigate('Tracking', { id: data.orderId }); // deep navigate
    });

    // App killed state se tap karke khula ho to:
    Notifications.getLastNotificationResponseAsync().then((r) => {
      const id = r?.notification.request.content.data?.orderId;
      if (id) navigation.navigate('Tracking', { id });
    });

    return () => {                                            // cleanup
      received.current?.remove();                             // listener hatao
      response.current?.remove();
    };
  }, [navigation]);
}

// ---- Backend (Node 18+) : push bhejna ----
// await fetch('https://exp.host/--/api/v2/push/send', {
//   method: 'POST',
//   headers: { 'Content-Type': 'application/json' },
//   body: JSON.stringify({ to: 'ExponentPushToken[xxxx]', title: 'Order update', body: 'Out for delivery', data: { orderId: '42' } }),
// });
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Permission | Android 13+ me runtime `POST_NOTIFICATIONS` | Hamesha prompt |
| Channel | Zaroori (importance, sound) | Nahi hota |
| Credentials | FCM (google-services.json, FCM v1 key in EAS) | APNs key (EAS manage kar sakta hai) |
| Simulator | Emulator + Google Play services me kuch chalta | Simulator me remote push nahi (Xcode 14+ drag-drop local test) |
| Background tasks | Data-only possible | `content-available` + limits |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-notifications expo-device expo-constants
// app.json plugin: ["expo-notifications", { "icon": "./assets/noti.png", "color": "#fc8019" }]
// eas credentials / FCM v1 service account upload; dev build use karo
const { data } = await Notifications.getExpoPushTokenAsync({ projectId });
```
CLI way:
```jsx
// Bare RN: Expo modules install karke expo-notifications chala sakte ho,
// ya seedha @react-native-firebase/messaging (FCM token, topic 98 dekho)
// iOS: Push Notifications capability + APNs key, pod install
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Simulator/emulator par token mangna.
✅ Correct: `Device.isDevice` check + real device.

❌ Mistake 2: Android channel na banana — Android 8+ par notification nahi dikhti.
✅ Correct: `setNotificationChannelAsync` token se pehle.

❌ Mistake 3: `projectId` na dena (SDK 49+ me chahiye).
✅ Correct: `getExpoPushTokenAsync({ projectId })`.

❌ Mistake 4: Listener cleanup bhoolna — duplicate navigations.
✅ Correct: `.remove()` in cleanup.

❌ Mistake 5: Token ko hardcode/share karna aur refresh na sunna.
✅ Correct: har login par token backend sync.

---

## 🧠 Tricky Interview Question
App **killed** hai, user notification tap karta hai. `addNotificationResponseReceivedListener` kyun nahi chalta?

Answer: Listener tab register hota hai jab JS chalta hai; tap se app launch hone par listener tak event aa chuka hota hai. Isliye `getLastNotificationResponseAsync()` (ya `useLastNotificationResponse`) se launch notification padhte hain.

---

## ⚫ Interview Questions + Answers
Q1: Expo push token vs FCM token?
A1: Expo token Expo ka wrapper (ExponentPushToken) hai, Expo service route karti hai. FCM token directly Firebase ka device token hai.

Q2: Foreground me notification kyun nahi dikhti?
A2: Default me suppress; `setNotificationHandler` me show karo.

Q3: Local vs remote?
A3: Local app schedule karta hai (topic 99); remote server push bhejta hai.

Q4: Android 13 me kya naya?
A4: Runtime permission `POST_NOTIFICATIONS`.

Q5: Expo Go limitations?
A5: Android remote push Expo Go me SDK 53+ se supported nahi; dev build.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Order updates, offers, chat alerts, OTP-like alerts

❌ Avoid when:
- Spam/marketing zyada (users disable kar dete hain)
- Critical data sirf push par depend (delivery guarantee nahi)

---

## 📊 Visual Diagram
```
 App ── token ──► Your Backend ──► Expo Push API ──► FCM (Android)
  ▲                                                └► APNs (iOS)
  └────────────── notification ◄──────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Push token | Device address for push | Push का पता |
| FCM | Google push service | Google का push |
| APNs | Apple push service | Apple का push |
| Channel | Android notification category | Android श्रेणी |
| Payload | Message data | संदेश का data |

---

## ⚡ 3-Line Summary
English: expo-notifications gets a push token, sends it to your server and shows notifications.
Create Android channel, ask permission, use real device.
Handle tap with response listener and getLastNotificationResponseAsync.

Hindi: expo-notifications push token लेकर server को देता है और notification दिखाता है।
Android channel बनाएँ, permission माँगें, real device पर चलाएँ।
Tap के लिए response listener और getLastNotificationResponseAsync इस्तेमाल करें।

---

## ➡️ Next Topic
**98. Push Notifications — Firebase (FCM)** — Expo के बिना सीधे Firebase से।

---
