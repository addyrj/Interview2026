# 299. Build Custom Hook — useNotification
# हिंदी में: Custom Hook बनाओ — useNotification
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 52 / React Native 0.76** (check current docs — APIs change between SDKs). Version-dependent points: from **SDK 53** `shouldShowAlert` is replaced by `shouldShowBanner` + `shouldShowList`; from SDK 52 a scheduled `trigger` needs a `type` field; from SDK 53 remote push does not work in **Expo Go on Android** (use a development build).
> Files: [`useNotification.js`](./useNotification.js) · [`NotificationScreen.jsx`](./NotificationScreen.jsx)
> Install: `npx expo install expo-notifications expo-device expo-constants`

---

## 🔵 Simple Definition (English)
`useNotification` is a custom hook that asks notification permission, gets the **Expo push token**, and listens for notifications (received while app is open, and tapped by the user). A screen just reads `expoPushToken`, `notification` and `lastResponse`.

## 🔵 सरल परिभाषा (Hindi)
`useNotification` एक custom hook है जो notification की permission माँगता है, **Expo push token** लेता है, और notifications सुनता है (app खुली हो तब आई, और user ने tap की)। Screen सिर्फ `expoPushToken`, `notification` और `lastResponse` पढ़ती है।

---

## 🔴 Problem it Solves
```
❌ Permission, Android channel, token, 2 listeners - सब App.js में बिखरे हुए
❌ Listener हटाना भूल गए -> एक notification पर दो बार handler चलता है
❌ Emulator पर token माँगा -> crash / error
❌ projectId न दिया -> getExpoPushTokenAsync fail
```

## 🔴 यह क्यों बना? (Hindi)
```
Swiggy "Order out for delivery", Zomato offers, Paytm payment alerts - सब push से आते हैं।
Token backend को भेजना पड़ता है, और tap पर सही screen खोलनी होती है।
यह सारा setup हर app में एक जैसा है, इसलिए एक hook में रख दो और बाकी app साफ़ रखो।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → setNotificationHandler (once, outside the hook): show banner + sound in foreground
Step 2 → Android: create a channel first (needed for Android 8+, and for the Android 13 prompt)
Step 3 → Real device check (Device.isDevice) -> push tokens do not work on emulators
Step 4 → getPermissionsAsync -> if not granted, requestPermissionsAsync
Step 5 → getExpoPushTokenAsync({ projectId }) -> "ExponentPushToken[xxxx]" -> send to backend
Step 6 → addNotificationReceivedListener (foreground) + addNotificationResponseReceivedListener (tap)
Step 7 → Cleanup: .remove() both subscriptions on unmount
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → setNotificationHandler (एक बार, hook के बाहर): foreground में भी banner + sound
Step 2 → Android: पहले channel बनाओ (Android 8+ और Android 13 के prompt के लिए ज़रूरी)
Step 3 → असली फ़ोन check करो (Device.isDevice) -> emulator पर push token नहीं चलता
Step 4 → getPermissionsAsync -> granted नहीं तो requestPermissionsAsync
Step 5 → getExpoPushTokenAsync({ projectId }) -> "ExponentPushToken[xxxx]" -> backend को भेजो
Step 6 → addNotificationReceivedListener (foreground) + addNotificationResponseReceivedListener (tap)
Step 7 → Cleanup: unmount पर दोनों subscriptions .remove() करो
```

---

## 🟡 Real World Example
**Swiggy** sends "Order out for delivery"; tapping it opens the live tracking screen. **Zomato** sends offers at lunchtime. **Paytm** sends payment received alerts, and **IRCTC** sends PNR/train status updates.

## 🟡 Real Example Hindi mein
**Swiggy** "Order out for delivery" भेजता है; tap करने पर live tracking screen खुलती है। **Zomato** लंच के समय offers भेजता है। **Paytm** payment मिलने का alert भेजता है, और **IRCTC** PNR / train status भेजता है।

---

## 💻 Code Example — Basic
Local (on-device) notification only - no server, no token:

```jsx
// Basic: schedule a local notification after 2 seconds
import React from 'react'; // React
import { Button, View } from 'react-native'; // UI
import * as Notifications from 'expo-notifications'; // notifications API

export default function BasicLocal() {
  const fire = async () => {
    await Notifications.requestPermissionsAsync(); // ask permission (needed on iOS and Android 13+)
    await Notifications.scheduleNotificationAsync({
      content: { title: 'Order placed', body: 'Biryani on the way' }, // what the user sees
      // SDK 52+: trigger needs a type; older SDKs accepted { seconds: 2 }
      trigger: { type: Notifications.SchedulableTriggerInputTypes.TIME_INTERVAL, seconds: 2 },
    });
  };
  return (
    <View style={{ padding: 40 }}>
      {/* press, then background the app to see the banner */}
      <Button title="Notify me" onPress={fire} />
    </View>
  );
}
```

## 💻 Code Example — Advanced
Full code: [`useNotification.js`](./useNotification.js) + [`NotificationScreen.jsx`](./NotificationScreen.jsx). Key part:

```js
// useNotification.js (key part)
async function registerForPush() {
  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'default', importance: Notifications.AndroidImportance.MAX, // channel first
    });
  }
  if (!Device.isDevice) throw new Error('Push needs a physical device'); // no emulator tokens
  let { status } = await Notifications.getPermissionsAsync();           // current status
  if (status !== 'granted') status = (await Notifications.requestPermissionsAsync()).status; // OS dialog
  if (status !== 'granted') throw new Error('Notification permission denied');
  const projectId = Constants.expoConfig?.extra?.eas?.projectId ?? Constants.easConfig?.projectId;
  if (!projectId) throw new Error('Missing EAS projectId');             // set by `eas init`
  return (await Notifications.getExpoPushTokenAsync({ projectId })).data; // "ExponentPushToken[...]"
}
// inside the hook:
useEffect(() => {
  registerForPush().then(setToken).catch((e) => setError(e.message));
  const a = Notifications.addNotificationReceivedListener(setNotification);       // foreground arrival
  const b = Notifications.addNotificationResponseReceivedListener(setLastResponse); // user tapped
  return () => { a.remove(); b.remove(); };                                        // cleanup
}, []);
```

> Verified: rendered under jsdom (react-native-web, `expo-notifications` / `expo-device` / `expo-constants` mocked): permission denied shows the error; granted shows `ExponentPushToken[pid1]`; emitting a received and a response event updates "Last" and "Tapped"; the "Test in 2s" button schedules a `timeInterval` trigger with 2 seconds; unmount removes both listeners. Real push delivery, OS permission dialogs, FCM/APNs setup and the real `getExpoPushTokenAsync`: not run.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Permission prompt | Android 13+ (API 33) shows prompt; before that auto-granted | Always shows prompt (first time) |
| Channels | Required (Android 8+); user controls per channel | Not applicable |
| Push service | FCM (needs `google-services.json`) | APNs (needs Apple credentials via EAS) |
| Emulator/simulator | Emulator with Google Play can receive FCM, Expo token still needs a real device in this hook | Simulator cannot get a remote push token (recent Xcode can drop local pushes only) |
| Expo Go | Remote push removed in Expo Go from SDK 53 -> use a dev build | Works in Expo Go (check current docs) |
| Denied permission | Can ask again, else open Settings | Asked only once, then Settings |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx expo install expo-notifications expo-device expo-constants   # SDK-matched
eas init                                                          # writes extra.eas.projectId
```
```json
// app.json (plugin config; icon/color are Android notification icon settings)
{ "expo": { "plugins": [["expo-notifications", { "color": "#fc8019" }]] } }
```
CLI way:
```bash
npm install @react-native-firebase/app @react-native-firebase/messaging   # FCM directly
cd ios && pod install && cd ..                                            # iOS pods
```
```js
import messaging from '@react-native-firebase/messaging';         // CLI-side API
const token = await messaging().getToken();                       // FCM/APNs token (not an Expo token)
messaging().onMessage(async (msg) => { /* foreground */ });       // foreground listener
messaging().setBackgroundMessageHandler(async (msg) => { /* background */ }); // background
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Calling `setNotificationHandler` inside the component (runs every render).
✅ **Correct:** Call it once at module level.

❌ **Mistake 2:** No `.remove()` on listeners -> duplicate handlers after remounts.
✅ **Correct:** Remove both subscriptions in cleanup.

❌ **Mistake 3:** Asking permission before creating the Android channel (Android 13+).
✅ **Correct:** `setNotificationChannelAsync` first, then request permission.

❌ **Mistake 4:** Missing `projectId` in `getExpoPushTokenAsync`.
✅ **Correct:** Run `eas init`; read it from `Constants.expoConfig.extra.eas.projectId`.

❌ **Mistake 5:** Testing push on an emulator and thinking the code is broken.
✅ **Correct:** Use a physical device (the hook throws a clear message).

---

## 🧠 Tricky Interview Question
**Q:** The app is **killed** and a push arrives. The user taps it. Does `addNotificationResponseReceivedListener` fire?

**Answer:** Not by itself - the listener is registered only after the JS bundle starts, which is after the tap launched the app. Use `Notifications.getLastNotificationResponseAsync()` (or the `useLastNotificationResponse()` hook) on startup to read the tap that launched the app. Our hook covers foreground and background taps; cold-start taps need that extra call (check current docs for the exact timing in your SDK).

---

## ⚫ Interview Questions + Answers

**Q1: Expo push token vs FCM/APNs token?**
A1: Expo token is a wrapper address (`ExponentPushToken[...]`) used with Expo's push service, which forwards to FCM/APNs. With `getDevicePushTokenAsync` you get the raw native token.

**Q2: Where do you send the token?**
A2: To your backend after login (store per user + device), and refresh it when it changes or on logout (delete it).

**Q3: Local vs remote notification?**
A3: Local is scheduled on the device (`scheduleNotificationAsync`), no internet needed (reminders). Remote is sent from a server via Expo/FCM/APNs.

**Q4: How to deep-link from a notification tap?**
A4: Put `data: { screen: 'Orders' }` in the payload; in the response listener read `response.notification.request.content.data` and call `navigation.navigate`.

**Q5: Why is `setNotificationHandler` needed?**
A5: By default, notifications received while the app is in the foreground are not shown. The handler decides to show banner/sound/badge.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- App needs order, payment or chat alerts (Swiggy, Paytm, WhatsApp-like)
- You want all notification setup in one testable place

❌ Avoid when:
- Only simple in-app messages (use a toast/banner)
- You need advanced FCM features in a bare app (data-only messages, topics) -> use `@react-native-firebase/messaging`

---

## 📊 Visual Diagram
```
 useNotification()
   │ 1. channel (Android) ─▶ 2. permission ─▶ 3. getExpoPushTokenAsync ─▶ token ─▶ your backend
   │
   ├─ addNotificationReceivedListener ──▶ notification   (app open)
   └─ addNotificationResponseReceivedListener ─▶ lastResponse (user tapped) ─▶ navigate(data.screen)

 Server ─▶ Expo Push Service ─▶ FCM (Android) / APNs (iOS) ─▶ device
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Push token | Address of a device for push | Device का push पता |
| FCM | Firebase Cloud Messaging (Android push) | Android का push service |
| APNs | Apple Push Notification service | iOS का push service |
| Channel | Android category with sound/importance | Android notification श्रेणी |
| Handler | Decides foreground display | Foreground में दिखाने का नियम |
| Response | User's tap on a notification | Notification पर user का tap |

---

## ⚡ 3-Line Summary
**English:**
1. `useNotification` does channel, permission, Expo token and both listeners in one place.
2. Set the handler once, always remove listeners, and test on a real device with an EAS projectId.
3. Cold-start taps need `getLastNotificationResponseAsync`, not only the listener.

**Hindi:**
1. `useNotification` channel, permission, Expo token और दोनों listeners एक जगह सँभालता है।
2. Handler एक बार set करो, listeners हमेशा हटाओ, और असली फ़ोन पर EAS projectId के साथ test करो।
3. App बंद होने के बाद tap के लिए सिर्फ listener नहीं, `getLastNotificationResponseAsync` भी चाहिए।

---

## ➡️ Next Topic
**300. Full App - Food Delivery UI Clone** - अब सब मिलाकर एक पूरा app: navigation, cart context, search और bill।
