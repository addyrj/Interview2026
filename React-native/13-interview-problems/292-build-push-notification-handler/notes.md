# 292. Interview Problem: Build a Push Notification Handler
# हिंदी में: Push Notification Handler बनाओ
# Platform: Both ✅ (Android ✅ | iOS ✅) — physical device required for push tokens
# Difficulty: ⭐⭐⭐⭐ Hard | Asked at: Swiggy, Zomato, Paytm, Ola, Dream11

Files: `NotificationHandler.jsx` (`useNotificationHandler` hook), `PushDemoScreen.jsx`.
Target: Expo SDK 52 with `expo-notifications` (check current docs — APIs change between SDKs). SDK 53+ changes are marked below.

---

## 🔵 Simple Definition (English)
A push handler asks notification permission, gets a push token for the device, shows notifications while the app is open, and runs your code when the user taps a notification (for example to open the order screen).

## 🔵 सरल परिभाषा (Hindi)
Push handler notification की permission माँगता है, device का push token लेता है, app खुला हो तब भी notification दिखाता है, और user के tap करने पर आपका code चलाता है (जैसे order screen खोलना)।

---

## 🔴 Problem it Solves
Apps need to reach users when closed: order updates, OTP, offers. Handling every state (foreground, background, killed) and permissions correctly is the hard part.

## 🔴 यह क्यों बना? (Hindi)
Apps को बंद होने पर भी users तक पहुँचना होता है: order update, OTP, offers। असली मुश्किल हर state (foreground, background, killed) और permissions को सही तरह से संभालना है।

---

## 🔴 Problem Statement
Write a hook `useNotificationHandler(onOpen, onToken)` that: creates an Android channel; requests permission; gets an Expo push token (device only); shows notifications in the foreground; calls `onOpen(data)` when a notification is tapped, including when the tap launched a killed app; removes all listeners on unmount.

## 💡 Approach
```
Module level : Notifications.setNotificationHandler  (foreground display rules)
registerForPush():
   Android -> setNotificationChannelAsync('default')   (before permission on Android 13+)
   Device.isDevice? -> getPermissionsAsync -> requestPermissionsAsync -> getExpoPushTokenAsync({projectId})
Hook (useEffect once):
   addNotificationReceivedListener          (foreground arrival)
   addNotificationResponseReceivedListener  (user tapped)
   getLastNotificationResponseAsync         (app killed -> opened by tap)
   cleanup: subscription.remove()
```

## 🟢 How it Works — Step by Step
```
Step 1 → Set the foreground handler (alert/sound/badge choices)
Step 2 → Create the Android channel 'default'
Step 3 → Check device, ask permission, get Expo push token with your EAS projectId
Step 4 → Send the token to your backend
Step 5 → Backend sends a push (Expo push API / FCM / APNs) with data { orderId }
Step 6 → Tap -> response listener -> onOpen(data) -> navigate to the right screen
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Foreground handler सेट करो (alert/sound/badge क्या दिखे)
Step 2 → Android channel 'default' बनाओ
Step 3 → Device check, permission माँगो, EAS projectId से Expo push token लो
Step 4 → Token अपने backend को भेजो
Step 5 → Backend push भेजता है (Expo push API / FCM / APNs) data { orderId } के साथ
Step 6 → Tap -> response listener -> onOpen(data) -> सही screen पर navigate
```

---

## 🟡 Real World Example
Swiggy "Your order is out for delivery", Zomato offers, Paytm payment received, Ola "driver arrived", Dream11 "lineups out". Tapping opens the exact order / match screen.

## 🟡 Real Example Hindi mein
Swiggy "आपका order निकल गया है", Zomato offers, Paytm "payment मिला", Ola "driver पहुँच गया", Dream11 "lineups आ गए"। Tap करने पर सीधे उसी order / match की screen खुलती है।

---

## 💻 Code Example — Basic
Schedule a local notification (works without a server, good for testing):
```jsx
import * as Notifications from 'expo-notifications';             // notifications API

// Show how notifications look while the app is open
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,                                       // SDK <= 52. SDK 53+: shouldShowBanner + shouldShowList
    shouldPlaySound: true,                                       // play sound
    shouldSetBadge: false,                                       // do not touch badge
  }),
});

export const test = () =>
  Notifications.scheduleNotificationAsync({
    content: { title: 'Order on the way', body: 'Rider is 5 mins away', data: { orderId: '42' } }, // payload
    trigger: { seconds: 2 },                                     // after 2s (newer SDKs may need type: 'timeInterval' - check docs)
  });
```

## 💻 Code Example — Advanced
From `NotificationHandler.jsx`:
```jsx
async function registerForPush() {
  if (Platform.OS === 'android') {                               // channel BEFORE permission (Android 13+)
    await Notifications.setNotificationChannelAsync('default', {
      name: 'Default', importance: Notifications.AndroidImportance.MAX });
  }
  if (!Device.isDevice) return null;                             // simulator cannot get a token
  let { status } = await Notifications.getPermissionsAsync();
  if (status !== 'granted') ({ status } = await Notifications.requestPermissionsAsync());
  if (status !== 'granted') return null;                         // denied
  const projectId = Constants.expoConfig?.extra?.eas?.projectId ?? Constants.easConfig?.projectId;
  const token = await Notifications.getExpoPushTokenAsync({ projectId });
  return token.data;                                             // "ExponentPushToken[xxxx]"
}

export function useNotificationHandler(onOpen, onToken) {
  useEffect(() => {
    registerForPush().then((t) => t && onToken?.(t)).catch((e) => console.warn('Push setup failed', e));
    const received = Notifications.addNotificationReceivedListener((n) => { /* foreground arrival */ });
    const response = Notifications.addNotificationResponseReceivedListener((r) =>
      onOpen?.(r.notification.request.content.data));            // user tapped
    Notifications.getLastNotificationResponseAsync().then((r) =>
      r && onOpen?.(r.notification.request.content.data));       // killed app opened by tap
    return () => { received.remove(); response.remove(); };      // cleanup
  }, []);
}
```
Production notes: add `expo-notifications` plugin config in app.json, upload FCM credentials (Android) and APNs key (iOS) through `eas credentials`, validate the payload `data` before navigating, and never put secrets in the payload.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Permission | Runtime permission on Android 13+ (`POST_NOTIFICATIONS`) | Always asked; one chance, then user must use Settings |
| Channels | Required (8+): importance, sound, vibration per channel | No channels |
| Delivery service | FCM | APNs |
| Expo Go | Remote push NOT supported in Expo Go on Android from SDK 53 - use a dev build | Works in Expo Go for development |
| Simulator | Emulator with Google Play services can sometimes get a token | iOS simulator can not get a remote token |
| Badge | Launcher-dependent | `setBadgeCountAsync` standard |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-notifications expo-device expo-constants
// app.json: "plugins": ["expo-notifications"]  + EAS projectId in extra.eas
// eas credentials  (FCM v1 service account for Android, APNs key for iOS)
// token = (await Notifications.getExpoPushTokenAsync({ projectId })).data
```
CLI way:
```jsx
// Bare RN: @react-native-firebase/messaging  (FCM for both, APNs via Firebase)
// import messaging from '@react-native-firebase/messaging';
// await messaging().requestPermission(); const token = await messaging().getToken();
// messaging().onMessage(...) ; messaging().onNotificationOpenedApp(...) ; messaging().getInitialNotification()
// plus google-services.json / GoogleService-Info.plist and native setup
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Testing on a simulator and expecting a token.
✅ Correct: Use a physical device and check `Device.isDevice`.

❌ Mistake 2: No Android channel -> no notification on Android 8+.
✅ Correct: Create the channel before asking permission.

❌ Mistake 3: Forgetting to remove listeners (duplicate callbacks after remount).
✅ Correct: `subscription.remove()` in cleanup.

❌ Mistake 4: Ignoring the "killed app" case.
✅ Correct: `getLastNotificationResponseAsync()` on startup.

❌ Mistake 5: Using `shouldShowAlert` on SDK 53+ (deprecated).
✅ Correct: Use `shouldShowBanner` and `shouldShowList` there.

---

## 🧠 Tricky Interview Question
A user taps a notification while the app is killed. Which listener runs?

Answer: The response listener is not registered yet (JS was not running). On launch you read `getLastNotificationResponseAsync()` (or `useLastNotificationResponse`) to get that tap, then navigate. Navigation must wait until the navigator is ready.

---

## ⚫ Interview Questions + Answers
Q1: Local vs remote notification?
A1: Local is scheduled by the app on the device; remote comes through FCM/APNs from a server.

Q2: Expo push token vs FCM token?
A2: Expo token is an Expo-service id (backend calls Expo push API); `getDevicePushTokenAsync` returns the raw FCM/APNs token.

Q3: Foreground behaviour?
A3: The OS does not show notifications in the foreground by default; `setNotificationHandler` decides.

Q4: Data vs notification messages?
A4: Notification messages are displayed by the OS; data-only messages need app code (and may be limited in the background, especially on iOS).

Q5: How do you deep-link from a tap?
A5: Put a screen/id in `data`, read it in `onOpen`, then `navigation.navigate` (or a `url` with Expo Router).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Time-sensitive info: order tracking, OTP, chat, reminders

❌ Avoid when:
- Spamming marketing; users will disable notifications. Ask permission at a meaningful moment, not on first launch.

---

## 📊 Visual Diagram
```
 Your server ──► Expo Push / FCM / APNs ──► Device
                                              │
        app open ──► handler -> banner + received listener
        app background ──► OS shows it ──► tap ──► response listener ─┐
        app killed ──► OS shows it ──► tap ──► app launches ──► getLastNotificationResponseAsync ─┤
                                                                                 onOpen(data) ◄───┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Push token | Address of a device for pushes | Device का पता |
| Channel | Android notification category | Android श्रेणी |
| FCM / APNs | Google / Apple push services | Push सेवाएँ |
| Foreground handler | Rule for app-open display | App खुला होने पर नियम |
| Deep link | Open a specific screen | सीधे screen खोलना |

---

## ⚡ 3-Line Summary
English: Create the Android channel, ask permission, get the token on a real device.
Set a foreground handler and listen for received and tapped events.
Handle the killed-app case and clean up listeners.

Hindi: Android channel बनाएँ, permission माँगें, असली device पर token लें।
Foreground handler सेट करें और received व tapped events सुनें।
Killed-app case संभालें और listeners हटाएँ।

---

## ✅ What was verified
Under react-native-web + jsdom with a fully mocked `expo-notifications`, `expo-device` and `expo-constants`: the hook returns the token to the screen and a simulated tap delivers its `data` to `onOpen`. Real permission dialogs, real tokens, FCM/APNs, channels and background/killed behaviour were not run (native, needs a device and credentials).

---

## ➡️ Next Topic
293. Build QR Code Scanner — another native-permission feature, using the camera.
