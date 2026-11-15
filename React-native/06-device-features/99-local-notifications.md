# 99. Local Notifications
# हिंदी में: Local Notifications (बिना server के notification)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: Expo SDK 52 (React Native 0.76) + `expo-notifications` (check current docs — APIs change between SDKs). **Version-dependent:** नए SDK में trigger object में `type` (जैसे `SchedulableTriggerInputTypes.TIME_INTERVAL`) देना ज़रूरी/recommended है और `shouldShowAlert` की जगह `shouldShowBanner` / `shouldShowList` आया है। Local notification Expo Go में चलते हैं (remote push नहीं)।

---

## 🔵 Simple Definition (English)
A **local notification** is scheduled and shown by the app itself on the device, with no server or internet. You can show it **now**, after some **seconds**, **daily at a time**, or on a specific **date**.

## 🔵 सरल परिभाषा (Hindi)
**Local notification** app खुद device पर schedule करके दिखाता है, इसमें server या internet नहीं लगता। इसे अभी, कुछ सेकंड बाद, रोज़ किसी समय, या किसी तय date पर दिखाया जा सकता है।

---

## 🔴 Problem it Solves
```
❌ Reminder ke liye server + push token ka jhanjhat
❌ Offline hone par push nahi aata
❌ User ko "medicine lo" jaisa daily nudge dena
✅ Device khud timer lagata hai; offline bhi chalta hai
```

## 🔴 यह क्यों बना? (Hindi)
```
हर reminder के लिए server और token बनाना भारी है।
Offline में push नहीं पहुँचता।
Local notification OS के scheduler में register हो जाता है,
इसलिए app बंद होने पर भी समय पर दिखता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install expo-notifications
Step 2 → Notifications.setNotificationHandler (foreground me kaise dikhe)
Step 3 → requestPermissionsAsync() (iOS + Android 13+)
Step 4 → Android: setNotificationChannelAsync('reminders', ...)
Step 5 → scheduleNotificationAsync({ content, trigger }) -> id milta hai
Step 6 → trigger: null = abhi | TIME_INTERVAL | DAILY | DATE
Step 7 → cancelScheduledNotificationAsync(id) / cancelAllScheduledNotificationsAsync()
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Permission माँगें और Android के लिए channel बनाएँ।
Step 2 → scheduleNotificationAsync में content (title/body/data) और trigger दें।
Step 3 → OS scheduler उसे सही समय पर दिखाता है, app बंद हो तब भी।
Step 4 → मिली id से cancel कर सकते हैं।
```

---

## 🟡 Real World Example
**Zomato:** "Your cart is waiting" reminder 2 hours after you add items and leave. **Swiggy One:** weekly offer reminder. **Paytm:** "Electricity bill due tomorrow" scheduled by date. **Health apps:** daily 9 AM medicine reminder.

## 🟡 Real Example Hindi mein
**Zomato:** cart में सामान छोड़ने के 2 घंटे बाद "Cart आपका इंतज़ार कर रहा है"। **Paytm:** "बिजली बिल कल due है" date के हिसाब से। **Health apps:** रोज़ सुबह 9 बजे दवा का reminder।

---

## 💻 Code Example — Basic
```jsx
// LocalBasic.jsx — 5 second baad notification
import React, { useEffect } from 'react';                              // React
import { View, Button, Platform } from 'react-native';                 // RN
import * as Notifications from 'expo-notifications';                   // API

Notifications.setNotificationHandler({                                 // foreground behaviour
  handleNotification: async () => ({
    shouldShowAlert: true,                                             // SDK 52 flag (naye SDK me shouldShowBanner/shouldShowList)
    shouldPlaySound: true,                                             // sound on
    shouldSetBadge: false,                                             // badge off
  }),
});

export default function LocalBasic() {
  useEffect(() => {
    (async () => {
      if (Platform.OS === 'android') {                                 // Android 8+ channel
        await Notifications.setNotificationChannelAsync('reminders', {
          name: 'Reminders',                                           // user ko settings me dikhega
          importance: Notifications.AndroidImportance.HIGH,            // heads-up
        });
      }
      await Notifications.requestPermissionsAsync();                   // permission prompt
    })();
  }, []);                                                              // sirf mount par

  const schedule = () =>
    Notifications.scheduleNotificationAsync({
      content: { title: 'Hello 👋', body: '5 second ho gaye', data: { screen: 'Home' } }, // message
      trigger: {
        type: Notifications.SchedulableTriggerInputTypes.TIME_INTERVAL, // time based
        seconds: 5,                                                    // 5 sec baad
        channelId: 'reminders',                                        // Android channel
      },
    });

  return <View style={{ padding: 40 }}><Button title="5s me notify karo" onPress={schedule} /></View>;
}
```

## 💻 Code Example — Advanced
```jsx
// reminders.js — daily reminder, date reminder, cancel, tap handling
import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';

const T = Notifications.SchedulableTriggerInputTypes;                  // trigger types (SDK 52+/53)

export async function ensureReady() {
  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('reminders', {
      name: 'Reminders',
      importance: Notifications.AndroidImportance.HIGH,
      vibrationPattern: [0, 250, 250, 250],                            // vibrate pattern
    });
  }
  const cur = await Notifications.getPermissionsAsync();               // current status
  if (cur.granted) return true;                                        // pehle se allowed
  const req = await Notifications.requestPermissionsAsync();           // poochho
  return req.granted;                                                  // true/false
}

// Roz subah 9:00 baje
export async function scheduleDaily(hour = 9, minute = 0) {
  if (!(await ensureReady())) throw new Error('Permission denied');    // permission zaroori
  return Notifications.scheduleNotificationAsync({
    content: { title: 'Dawai ka time', body: 'Subah ki dawai le lo' },
    trigger: { type: T.DAILY, hour, minute, channelId: 'reminders' },  // daily repeat
  });                                                                  // returns notification id
}

// Kisi ek date/time par (Paytm bill due jaisa)
export async function scheduleOnDate(date, title, body) {
  return Notifications.scheduleNotificationAsync({
    content: { title, body },
    trigger: { type: T.DATE, date, channelId: 'reminders' },           // JS Date object
  });
}

export const cancelOne = (id) => Notifications.cancelScheduledNotificationAsync(id); // ek hatao
export const cancelAll = () => Notifications.cancelAllScheduledNotificationsAsync(); // sab hatao
export const listScheduled = () => Notifications.getAllScheduledNotificationsAsync(); // pending list

// Tap par navigate (component me use karo)
export function listenTap(navigation) {
  const sub = Notifications.addNotificationResponseReceivedListener((r) => {
    const screen = r.notification.request.content.data?.screen;       // payload se screen
    if (screen) navigation.navigate(screen);                           // navigate
  });
  return () => sub.remove();                                           // cleanup
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Channel | Required (8+), sound/importance channel से तय | No channels |
| Permission | Android 13+ runtime prompt | Prompt on first request |
| Exact timing | Doze mode / battery saver में देरी संभव; exact alarm अलग permission | Generally on time |
| Max scheduled | कोई छोटी hard limit नहीं (OEM पर निर्भर) | अधिकतम **64** pending local notifications |
| Reboot | Expo scheduled ones restore करता है | OS रखता है |
| Foreground display | `setNotificationHandler` से | `setNotificationHandler` से |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-notifications ; app.json plugins: ["expo-notifications"]
import * as Notifications from 'expo-notifications';                   // Expo Go me local notif chalte hain
await Notifications.scheduleNotificationAsync({ content: { title: 'Hi' }, trigger: null }); // abhi
```
CLI way:
```jsx
// Bare RN: npm i @notifee/react-native  (ya expo-notifications with expo modules install)
import notifee from '@notifee/react-native';                           // popular local notification lib
await notifee.displayNotification({ title: 'Hi', android: { channelId: 'default' } }); // abhi
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Android पर channel बनाए बिना schedule करना।
✅ Correct: पहले `setNotificationChannelAsync`, फिर trigger में `channelId`।

❌ Mistake 2: Permission माँगे बिना schedule करना।
✅ Correct: `requestPermissionsAsync()` की `granted` जाँचें।

❌ Mistake 3: Foreground में notification नहीं दिखती, तो bug समझना।
✅ Correct: `setNotificationHandler` set करें।

❌ Mistake 4: हर बार screen खुलने पर नया reminder schedule करना (duplicate)।
✅ Correct: id store करें या पहले `cancelAllScheduledNotificationsAsync()`।

❌ Mistake 5: Trigger में सिर्फ़ `{ seconds: 5 }` देना (नए SDK में warning/error)।
✅ Correct: `type: SchedulableTriggerInputTypes.TIME_INTERVAL` जोड़ें।

---

## 🧠 Tricky Interview Question
You call `scheduleNotificationAsync` 100 times for the next 100 days on an iPhone. How many will fire?

Answer: iOS keeps only the **soonest 64** pending local notifications; the rest are dropped. Fix: schedule a rolling window (e.g. next 30), or use a `DAILY` repeating trigger, and re-schedule on app open.

हिंदी: iPhone सिर्फ़ 64 pending local notifications रखता है। इसलिए rolling window या repeating trigger रखें।

---

## ⚫ Interview Questions + Answers
Q1: Local vs push notification?
A1: Local को app खुद device पर schedule करता है (no server/internet); push server से token के ज़रिए आता है।

Q2: `trigger: null` का क्या मतलब है?
A2: Notification तुरंत दिखती है।

Q3: Scheduled notification cancel कैसे करें?
A3: `scheduleNotificationAsync` की लौटाई id से `cancelScheduledNotificationAsync(id)`, या `cancelAllScheduledNotificationsAsync()`।

Q4: Foreground में notification कैसे दिखाएँ?
A4: `setNotificationHandler` में `handleNotification` से alert/banner flags true करें।

Q5: Expo Go में local notifications चलते हैं?
A5: हाँ; Android के remote push SDK 53+ में Expo Go से हटे हैं, local नहीं।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Reminders, alarms-like nudges, habit/medicine/bill alerts
- Offline या server-free scheduling
- Cart-abandon जैसे time-delayed local nudges

❌ Avoid when:
- Server-driven events (new order, chat message) — push use करें
- Precise alarm clock behaviour (Android exact alarms अलग permission)
- 64 से ज़्यादा iOS schedules बिना strategy के

---

## 📊 Visual Diagram
```
 App ──scheduleNotificationAsync(content, trigger)──▶ OS Scheduler
                                                        │ (app band ho tab bhi)
                                        time/date/daily aaya
                                                        ▼
                                          Notification tray me dikhe
                                                        │ tap
                                                        ▼
        addNotificationResponseReceivedListener ──▶ navigate(screen)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Trigger | When to show | कब दिखाना है |
| Channel | Android notification category | Android की category |
| Handler | Foreground display rule | foreground में दिखाने का नियम |
| Schedule id | Handle to cancel | cancel करने की id |
| Badge | App icon count | icon पर संख्या |
| Doze | Android battery saver | Android का battery-बचत mode |

---

## ⚡ 3-Line Summary
English: Local notifications are scheduled on-device with expo-notifications, no server needed.
Ask permission, create an Android channel, then schedule with a trigger and cancel by id.
Remember iOS keeps only 64 pending ones.

Hindi: Local notifications expo-notifications से device पर ही schedule होते हैं, server नहीं चाहिए।
Permission लें, Android channel बनाएँ, trigger से schedule करें और id से cancel करें।
याद रखें iOS सिर्फ़ 64 pending रखता है।

---

## ➡️ Next Topic
**100. Permissions Handling** — सभी device features (camera, location, notifications) की permission एक सही pattern से कैसे संभालें।

---
