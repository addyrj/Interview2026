# 94. Push Notifications
# हिंदी में: Push Notifications — FCM, APNs, Expo Notifications
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
**Push Notifications** are messages sent from your server to a user's device even when the app is not open. Android uses **FCM** (Firebase Cloud Messaging), iOS uses **APNs** (Apple Push Notification Service). In React Native: `expo-notifications` (Expo) or `@notifee/react-native` / `react-native-push-notification` (CLI) handle receiving, displaying, and handling taps on notifications.

## 🔵 सरल परिभाषा (Hindi)
**Push Notifications** server से user के device पर messages — app open न हो तब भी। Android: **FCM** (Firebase Cloud Messaging), iOS: **APNs** (Apple Push Notification service)। React Native में: `expo-notifications` (Expo) या `@notifee/react-native` (CLI) notifications receive, display और tap handle करते हैं।

---

## 🔴 Problem it Solves
```
USE CASES:
  ✅ Swiggy: "Your order is out for delivery! 🛵"
  ✅ Zomato: "Flash Deal: 50% off next 30 minutes"
  ✅ PhonePe: "₹500 received from Rahul"
  ✅ WhatsApp: "New message from Priya"
  ✅ News app: "Breaking: Match starts in 10 minutes"

WITHOUT PUSH:
  User must open app to check order status
  Deals expire before user finds out
  Transaction confirmations only visible when app is open

WITH PUSH:
  Real-time alerts → app closed, still notified
  Drives re-engagement (80% of mobile re-opens are from push)
  Time-sensitive info delivered instantly
```

---

## 🟢 How It Works — Step by Step

```
PUSH NOTIFICATION ARCHITECTURE:
──────────────────────────────────────────────────────

  1. USER REGISTERS:
     App launches → request permission → get device token
     Android: FCM token (unique per device + app)
     iOS: APNs token (unique per device + app)

  2. TOKEN SENT TO YOUR SERVER:
     App sends token to your backend: POST /users/push-token
     Backend stores token in database with userId

  3. SERVER SENDS NOTIFICATION:
     Backend → FCM API (Android) or APNs API (iOS)
     {
       to: "device_fcm_token",
       notification: { title: "Order Update", body: "Out for delivery!" },
       data: { orderId: "123", type: "ORDER_UPDATE" }
     }

  4. PLATFORM DELIVERS:
     FCM / APNs → delivers to device
     Even if app is killed!

  5. APP RECEIVES:
     Foreground: notification handler fires (you decide what to show)
     Background: system shows notification automatically
     Tap: notification tap handler fires with data payload

  EXPO PUSH NOTIFICATIONS (abstraction layer):
     Your server → Expo Push API → FCM/APNs → Device
     Simpler: one API for both Android + iOS
     Expo handles FCM credentials + APNs certificates
```

---

## 🟡 Real World Example
**Swiggy order tracking:** User places order. Backend stores user's Expo push token in DB with their userId. Order status changes: Backend sends `POST https://exp.host/--/api/v2/push/send` with token + "Your order has been picked up! 🛵". FCM (Android) or APNs (iOS) delivers instantly. User sees notification even with app closed. User taps notification → app opens → navigates to Order Tracking screen (orderId in notification data). Real-time delivery experience without polling.

---

## 💻 Code Example — Expo Notifications

```tsx
// notificationSetup.ts — Initialize push notifications
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';

// How to display notifications when app is IN FOREGROUND
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,     // show notification banner
    shouldPlaySound: true,     // play sound
    shouldSetBadge: true,      // update app badge count
  }),
});

// GET PUSH TOKEN — call this on app startup
export async function registerForPushNotifications(): Promise<string | null> {
  // Simulators can't receive push notifications
  if (!Device.isDevice) {
    console.log('Must use physical device for push notifications');
    return null;
  }

  // Check current permission status
  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  // Request if not granted
  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') {
    console.log('Push notification permission denied');
    return null;
  }

  // Get Expo push token (works for both Android + iOS!)
  const token = (await Notifications.getExpoPushTokenAsync({
    projectId: 'your-expo-project-id',  // from app.json expo.extra.eas.projectId
  })).data;

  console.log('Push token:', token);
  // → "ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]"

  // Android: create notification channel
  if (Platform.OS === 'android') {
    Notifications.setNotificationChannelAsync('orders', {
      name: 'Order Updates',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#e23744',
    });
  }

  // Send token to your backend
  await sendTokenToServer(token);
  return token;
}

async function sendTokenToServer(token: string) {
  await fetch('https://api.yourapp.com/users/push-token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token }),
  });
}
```

```tsx
// App.tsx — Handle notification interactions
import React, { useEffect, useRef } from 'react';
import * as Notifications from 'expo-notifications';
import { useNavigation } from '@react-navigation/native';
import { registerForPushNotifications } from './notificationSetup';

export default function App() {
  const navigation = useNavigation();
  const notificationListener = useRef<any>();
  const responseListener = useRef<any>();

  useEffect(() => {
    // Register for push notifications on mount
    registerForPushNotifications();

    // FOREGROUND notification received (app is open)
    notificationListener.current = Notifications.addNotificationReceivedListener(
      (notification) => {
        console.log('Notification received:', notification);
        // notification.request.content.title
        // notification.request.content.body
        // notification.request.content.data  (your custom data)
      }
    );

    // NOTIFICATION TAPPED (app was background/killed, user tapped)
    responseListener.current = Notifications.addNotificationResponseReceivedListener(
      (response) => {
        const data = response.notification.request.content.data;

        // Navigate based on notification type
        if (data.type === 'ORDER_UPDATE') {
          navigation.navigate('OrderTracking', { orderId: data.orderId });
        } else if (data.type === 'PROMO') {
          navigation.navigate('PromoDetail', { promoId: data.promoId });
        } else if (data.type === 'MESSAGE') {
          navigation.navigate('Chat', { chatId: data.chatId });
        }
      }
    );

    // CHECK IF APP OPENED FROM NOTIFICATION (was killed)
    Notifications.getLastNotificationResponseAsync().then((response) => {
      if (response) {
        const data = response.notification.request.content.data;
        // Handle initial navigation from killed state
        if (data.type === 'ORDER_UPDATE') {
          // Use setTimeout to ensure navigation is ready
          setTimeout(() => {
            navigation.navigate('OrderTracking', { orderId: data.orderId });
          }, 100);
        }
      }
    });

    // Cleanup listeners
    return () => {
      notificationListener.current?.remove();
      responseListener.current?.remove();
    };
  }, []);

  return <RootNavigator />;
}
```

```javascript
// YOUR BACKEND — Send notification via Expo Push API
// Node.js / Express example
const { Expo } = require('expo-server-sdk');
const expo = new Expo();

async function sendOrderUpdateNotification(userId, orderId, statusMessage) {
  // Get user's push token from database
  const user = await db.users.findById(userId);
  const pushToken = user.expoPushToken;

  // Validate token
  if (!Expo.isExpoPushToken(pushToken)) {
    console.error(`Invalid push token: ${pushToken}`);
    return;
  }

  // Send notification
  const messages = [{
    to: pushToken,
    sound: 'default',
    title: 'Order Update 🛵',
    body: statusMessage,
    data: {
      type: 'ORDER_UPDATE',
      orderId: orderId,
    },
    // Android-specific:
    channelId: 'orders',
    priority: 'high',
    // iOS badge:
    badge: 1,
  }];

  const chunks = expo.chunkPushNotifications(messages);
  for (const chunk of chunks) {
    try {
      const receipts = await expo.sendPushNotificationsAsync(chunk);
      // Check receipts for errors (DeviceNotRegistered = token expired)
      for (const receipt of receipts) {
        if (receipt.status === 'error') {
          if (receipt.details?.error === 'DeviceNotRegistered') {
            // Remove stale token from database
            await db.users.updateOne({ _id: userId }, { $unset: { expoPushToken: 1 } });
          }
        }
      }
    } catch (error) {
      console.error('Push send failed:', error);
    }
  }
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Service | FCM (Firebase) | APNs (Apple) |
| Permission prompt | Not required (Android 12 and below) | Required (must request) |
| Android 13+ | Must request `POST_NOTIFICATIONS` | N/A |
| Notification channels | Required (Android 8+) | Not needed |
| Background delivery | ✅ | ✅ (APNs handles) |
| Silent push (data-only) | ✅ `content-available` | ✅ `content-available` |
| FCM config | `google-services.json` in app | Not needed |
| APNs config | Not needed | APNs key in Expo/EAS |

---

## 🟠 Expo vs CLI Difference

Expo way:
```bash
npx expo install expo-notifications expo-device
# Configure in app.json:
# "plugins": ["expo-notifications"]
# For FCM: add google-services.json via plugin
# For APNs: EAS handles certificates automatically
```

CLI way:
```bash
# More complex — choose one:
npm install @notifee/react-native   # most feature-rich
# OR
npm install react-native-push-notification @react-native-firebase/messaging

# Android: google-services.json + build.gradle changes
# iOS: APNs certificate setup + Xcode capabilities
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Not handling the killed state (app was fully closed when notification arrived)
```tsx
// WRONG: Only handles foreground + background, misses killed state
useEffect(() => {
  Notifications.addNotificationResponseReceivedListener(response => {
    navigateTo(response.notification.request.content.data);
  });
}, []);

// CORRECT: Also check getLastNotificationResponseAsync for killed state
useEffect(() => {
  // Handles foreground + background tap
  const sub = Notifications.addNotificationResponseReceivedListener(handler);

  // Handles KILLED state (user tapped notification to open app)
  Notifications.getLastNotificationResponseAsync().then(response => {
    if (response) handler(response);
  });

  return () => sub.remove();
}, []);
```

❌ **Mistake 2:** Using simulator/emulator to test push
```
Push notifications don't work on iOS Simulator or Android Emulator (mostly)
Always test on a real physical device!
Use Expo Go on a real device for basic testing
```

---

## ⚫ Interview Questions + Answers

**Q1: How do push notifications work in React Native?**
A1: App registers → gets device token (FCM for Android, APNs for iOS) → sends token to your backend → your server calls FCM/APNs API with the token + notification payload → platform delivers to device even when app is closed. In the app: `expo-notifications` provides `addNotificationResponseReceivedListener` for tap handling and `getLastNotificationResponseAsync` for the killed-state launch case.

**Q2: What is the difference between FCM and APNs?**
A2: FCM (Firebase Cloud Messaging) is Google's service for delivering push notifications to Android devices (also works for iOS via FCM). APNs (Apple Push Notification Service) is Apple's service for iOS. In production React Native apps: Expo Push Notifications or Firebase abstracts both — you send to one API and it routes to FCM/APNs automatically. Direct APNs requires an APNs auth key (p8 file) from Apple Developer portal.

**Q3: What are notification channels (Android)?**
A3: Android 8+ (API 26+) requires notifications to be assigned to a channel. Channels let users control notification behavior per category (e.g., "Order Updates" can be high priority with sound; "Promotions" can be silent). Create with `Notifications.setNotificationChannelAsync('channelId', { name, importance, sound, vibration })`. Without a channel on Android 8+, notifications are silently dropped.

**Q4: How do you handle deep linking from a notification tap?**
A4: In `addNotificationResponseReceivedListener`, read `response.notification.request.content.data` for your custom payload (e.g., `{ type: 'ORDER_UPDATE', orderId: '123' }`). Then use `navigation.navigate()` to go to the relevant screen. For the killed state, use `getLastNotificationResponseAsync()` — delay navigation with `setTimeout` to ensure the navigator is mounted. Pass the relevant ID as route params, not the full data object.

**Q5: What is a "silent" or "data-only" push notification?**
A5: A push with no visible alert — just data payload sent to the app. App processes it in the background (sync data, update cache) without showing any notification to the user. Configured with `content-available: 1` (iOS) and no `notification` object (Android). Use case: background data sync (chat app reads new messages silently), invalidating a cache entry, updating a local database. iOS has strict limits on background execution time (~30 seconds).

---

## 📊 Visual Diagram

```
PUSH NOTIFICATION DELIVERY:
──────────────────────────────────────────────────────

  Your Server
  │
  │ POST https://exp.host/--/api/v2/push/send
  │ { to: "ExponentPushToken[xxx]",
  │   title: "Order shipped!",
  │   data: { orderId: "123" } }
  │
  ▼
  Expo Push Service
  │
  ├──────────────────────┬──────────────────────┐
  ▼                      ▼                      │
  FCM (Google)          APNs (Apple)            │
  │                      │                      │
  ▼                      ▼                      │
  Android Device        iOS Device              │
  (app background)      (app background)        │
  Shows notification    Shows notification      │
                                                │
  User TAPS notification:                       │
  → App opens                                   │
  → addNotificationResponseReceivedListener     │
  → Navigate to OrderTracking screen            │

  App killed when notification arrives:
  → User taps → app launches
  → getLastNotificationResponseAsync() returns it
  → Navigate appropriately
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| FCM | Firebase Cloud Messaging (Android) | Android push service |
| APNs | Apple Push Notification Service | iOS push service |
| Push Token | Unique device identifier for push | Device का unique push identifier |
| Notification Channel | Android 8+ category for notifications | Android notification category |
| Foreground | App is open and active | App open और active |
| Background | App is open but not in focus | App open but not in focus |
| Killed | App is fully closed | App completely closed |
| Silent Push | Data-only, no visible alert | सिर्फ data, no alert |

---

## ⚡ 3-Line Summary
**English:**
1. Push notifications: app registers → gets FCM/APNs token → token sent to your server → server calls Expo/FCM/APNs API → notification delivered even when app is closed.
2. Handle 3 states: foreground (app open, `addNotificationReceivedListener`), background (app open but not focused, auto-shown by OS), killed (use `getLastNotificationResponseAsync`).
3. Android requires Notification Channels (Android 8+); iOS requires explicit permission request; test only on real physical devices.

**Hindi:**
1. Push notifications: app register → FCM/APNs token मिलता है → server को भेजो → server Expo/FCM/APNs को call → notification deliver even app closed।
2. 3 states handle करो: foreground (listener), background (OS handle), killed (`getLastNotificationResponseAsync`)।
3. Android: Notification Channels (Android 8+) जरूरी। iOS: permission request जरूरी। Testing: हमेशा real device पर।

---

## ➡️ Next Topic
**95. Local Notifications** — Schedule notifications without a server।
