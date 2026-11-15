# 149. Background Fetch
# हिंदी में: Background Fetch — App बंद होने पर भी data sync
# Platform: Android ✅ | iOS ✅ | Both ✅ (दोनों पर OS के नियम अलग)

> **Expo SDK 52 target (check current docs — APIs change between SDKs).** `expo-background-fetch` + `expo-task-manager`। **Version note:** नए SDKs में `expo-background-fetch` deprecated होकर `expo-background-task` से बदला जा रहा है (Expo docs में check करो कि तुम्हारे SDK में कौन सा current है)। यहाँ का code SDK 52 के `expo-background-fetch` API पर है। यह **Expo Go में पूरी तरह भरोसेमंद नहीं** — development build पर test करो।

---

## 🔵 Simple Definition (English)
**Background fetch** lets the OS wake your app briefly, even when it is closed or in the background, to run a small task such as refreshing data. You do not control the exact time; the OS decides.

## 🔵 सरल परिभाषा (Hindi)
**Background fetch** में OS आपकी app को थोड़ी देर के लिए जगाता है — भले ही app बंद या background में हो — ताकि वह छोटा काम (जैसे data refresh) कर सके। सही समय आप तय नहीं करते; OS तय करता है।

---

## 🔴 Problem it Solves
```
User app खोले, तब data लाना = धीमा, spinner।
चाहिए: app खुलने से पहले ही नया data तैयार (news, orders, balances)।

पर: app बंद होने पर JS चलता ही नहीं।
Background fetch: OS-approved छोटा window, battery का ध्यान रखते हुए।
```

## 🔴 यह क्यों बना? (Hindi)
```
App बंद हो तो code नहीं चलता।
OS battery बचाने के लिए सीमित और अनियमित समय पर app को जगाता है।
इसी से data पहले से fresh रहता है।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → TaskManager.defineTask(NAME, handler) — GLOBAL scope में (component के बाहर)
Step 2 → BackgroundFetch.registerTaskAsync(NAME, { minimumInterval, stopOnTerminate, startOnBoot })
Step 3 → iOS में app.json में UIBackgroundModes: ["fetch"] (config), Android में अपने आप
Step 4 → OS अपनी मर्ज़ी से (battery, network, user usage देखकर) task चलाता है
Step 5 → handler में छोटा काम (≈ 30 sec से कम) → NewData / NoData / Failed return
Step 6 → return value OS को बताती है कि भविष्य में कितना बुलाना है
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. Task को component के बाहर define करो।
2. registerTaskAsync से register करो (minimumInterval सिर्फ़ सुझाव है)।
3. iOS में UIBackgroundModes: fetch चाहिए।
4. OS अपने हिसाब से चलाता है — गारंटी नहीं।
5. छोटा काम करो और सही result return करो।
```

---

## 🟡 Real World Example
**News apps (Inshorts):** सुबह app खुलने से पहले ताज़ा खबरें cache हो जाती हैं। **Swiggy:** active order का status background में sync (पर live tracking के लिए push notification/ foreground service असली तरीका)। **Paytm:** pending transaction status refresh। ध्यान: "हर 5 मिनट" की गारंटी नहीं मिलती।

## 🟡 Real Example Hindi mein
**Inshorts** जैसे news app में सुबह आपके उठने से पहले background fetch ताज़ा खबरें cache कर देता है, इसलिए app खुलते ही data तैयार मिलता है। पर OS हर बार नहीं चलाता — user कम इस्तेमाल करे तो iOS कम बुलाएगा।

---

## 💻 Code Example — Basic

```jsx
// backgroundTask.js — define + register (import this file at app entry)
import * as BackgroundFetch from 'expo-background-fetch';        // fetch API
import * as TaskManager from 'expo-task-manager';                // task registry
import AsyncStorage from '@react-native-async-storage/async-storage'; // cache

export const TASK_NAME = 'refresh-feed-task';                    // unique name

// 1) GLOBAL scope में define करो (component के अंदर नहीं!)
TaskManager.defineTask(TASK_NAME, async () => {
  try {
    const res = await fetch('https://jsonplaceholder.typicode.com/posts?_limit=5'); // छोटा request
    if (!res.ok) return BackgroundFetch.BackgroundFetchResult.Failed;               // HTTP fail
    const data = await res.json();                                // parse
    await AsyncStorage.setItem('cache:feed', JSON.stringify(data)); // cache में रखो
    return BackgroundFetch.BackgroundFetchResult.NewData;         // नया data मिला
  } catch {
    return BackgroundFetch.BackgroundFetchResult.Failed;          // error
  }
});

// 2) Register (app में कहीं एक बार call)
export async function registerBackgroundFetch() {
  await BackgroundFetch.registerTaskAsync(TASK_NAME, {
    minimumInterval: 15 * 60,                                     // सेकंड; सिर्फ़ न्यूनतम सुझाव
    stopOnTerminate: false,                                       // app kill पर भी (Android)
    startOnBoot: true,                                            // reboot के बाद (Android)
  });
}
```

## 💻 Code Example — Advanced

```jsx
// BackgroundStatus.jsx — safe registration with status checks
import React, { useEffect, useState } from 'react';              // hooks
import { View, Text, Button, Platform } from 'react-native';     // UI
import * as BackgroundFetch from 'expo-background-fetch';        // API
import * as TaskManager from 'expo-task-manager';                // manager
import { TASK_NAME, registerBackgroundFetch } from './backgroundTask'; // from above

export default function BackgroundStatus() {
  const [status, setStatus] = useState(null);                    // OS permission status
  const [registered, setRegistered] = useState(false);           // task registered?

  const refresh = async () => {
    setStatus(await BackgroundFetch.getStatusAsync());           // Available/Denied/Restricted
    setRegistered(await TaskManager.isTaskRegisteredAsync(TASK_NAME)); // registered?
  };

  useEffect(() => { refresh(); }, []);                           // mount पर

  const toggle = async () => {
    try {
      if (registered) await BackgroundFetch.unregisterTaskAsync(TASK_NAME); // बंद करो
      else await registerBackgroundFetch();                      // चालू करो
    } catch (e) {
      console.warn('Background fetch error', e);                 // Expo Go आदि में fail हो सकता है
    }
    refresh();                                                   // UI update
  };

  const label = status === BackgroundFetch.BackgroundFetchStatus.Available ? 'Available'
    : status === BackgroundFetch.BackgroundFetchStatus.Denied ? 'Denied (user ने बंद किया)'
    : status === BackgroundFetch.BackgroundFetchStatus.Restricted ? 'Restricted (Low Power/policy)'
    : 'Unknown';

  return (
    <View style={{ padding: 20 }}>
      <Text>Platform: {Platform.OS}</Text>
      <Text>Status: {label}</Text>
      <Text>Registered: {String(registered)}</Text>
      <Button title={registered ? 'Disable' : 'Enable'} onPress={toggle} />
    </View>
  );
}
// app.json (iOS): { "expo": { "ios": { "infoPlist": { "UIBackgroundModes": ["fetch"] } } } }
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Scheduler | JobScheduler/WorkManager | BGTaskScheduler / background fetch |
| Interval control | `minimumInterval` काफी माना जाता है (न्यूनतम ≈15 min) | सिर्फ़ hint; OS usage patterns से तय |
| After app kill | `stopOnTerminate: false` से चलता है | Force-quit के बाद नहीं चलता |
| Run time | ~ कुछ मिनट तक (OS policy) | ~30 sec |
| Config | Manifest में अपने आप | `UIBackgroundModes: fetch` जरूरी |
| Battery saver/Low Power | Doze में देर | Low Power Mode में बंद |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-background-fetch expo-task-manager
// app.json में iOS UIBackgroundModes (ऊपर)
// Development build बनाओ: npx expo prebuild / eas build --profile development
```
CLI way:
```jsx
// npm i react-native-background-fetch   (transistorsoft) — अधिक विकल्प, headless task
// cd ios && pod install; Xcode में Background Modes → Background fetch + processing
// Android: Headless JS / WorkManager config library docs के अनुसार
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `defineTask` को component के अंदर लिखना।
✅ Correct: Global scope (module top-level)।

❌ Mistake 2: "ठीक 15 मिनट में चलेगा" मानना।
✅ Correct: OS का फैसला — गारंटी नहीं। Critical काम के लिए push notification।

❌ Mistake 3: लंबा/भारी काम (बड़ी file download)।
✅ Correct: छोटा, ~30 sec से कम।

❌ Mistake 4: Return value न देना।
✅ Correct: `NewData/NoData/Failed` return करो।

---

## 🧠 Tricky Interview Question
iOS पर user ने app को swipe up करके force-quit किया। क्या background fetch चलेगा?

Answer: नहीं — iOS पर force-quit के बाद app को background में जगाया नहीं जाता (जब तक user दोबारा न खोले)। Android पर `stopOnTerminate: false` से चल सकता है (OEM battery policy छोड़कर)। इसलिए time-critical updates के लिए push notification use करो।

---

## ⚫ Interview Questions + Answers
Q1: Background fetch और push notification में फर्क?
A1: Fetch — OS-controlled, अनियमित; Push — server तुरंत भेजता है (silent/data push भी)।

Q2: Task global में क्यों?
A2: OS app को JS context के बिना जगा सकता है; task registry को app load पर ही तैयार होना चाहिए।

Q3: Expo Go में चलेगा?
A3: भरोसेमंद नहीं; development build पर test करें।

Q4: नए SDK में क्या बदला?
A4: `expo-background-task` आ रहा है/आ चुका (WorkManager/BGTaskScheduler आधारित); अपने SDK के docs देखो।

Q5: Debugging कैसे?
A5: Android: `adb` से job trigger; iOS: Xcode में Debug → Simulate Background Fetch; `TaskManager.getRegisteredTasksAsync`।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Non-urgent refresh (feed, cache warm-up)

❌ Avoid when:
- Real-time/urgent updates (chat, live order) — push/WebSocket use करो
- भारी processing

---

## 📊 Visual Diagram
```
 defineTask(NAME)  ─┐
 registerTaskAsync ─┴► OS scheduler (battery, network, usage)
                          │  (कभी भी, गारंटी नहीं)
                          ▼
                 app wake (छोटी window) ─► handler: fetch + cache
                          │
                          ▼ return NewData / NoData / Failed
                    OS अगला schedule तय करता है
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Task | Named background job | नामित background काम |
| minimumInterval | Min gap hint | न्यूनतम अंतराल का सुझाव |
| stopOnTerminate | Stop when app killed | App kill पर रुकना |
| Headless | Runs without UI | बिना UI के |
| Doze | Android power saving | Android की power बचत |

---

## ⚡ 3-Line Summary
English: Background fetch lets the OS run a short task while the app is closed.
Define the task globally and register it; timing is not guaranteed.
Use push notifications for urgent updates.

Hindi: Background fetch में OS app बंद होने पर भी छोटा task चलाता है।
Task global में define करके register करो; समय की गारंटी नहीं।
जरूरी updates के लिए push notification।

---

## ➡️ Next Topic
**150. WebSocket in React Native** — real-time, दो-तरफ़ा connection।
