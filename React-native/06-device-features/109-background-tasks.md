# 109. Background Tasks
# हिंदी में: Background Tasks (app बंद होने पर भी छोटा काम)
# Platform: Android ✅ | iOS ✅ | Both ✅ (OS के नियमों से सीमित, real device)

> Target: Expo SDK 52 (React Native 0.76) + `expo-task-manager` + `expo-background-fetch`. **Version-dependent:** `expo-background-fetch` SDK 53 में deprecated हुआ और नया `expo-background-task` (WorkManager / BGTaskScheduler आधारित) आया — नए SDK में उसे चुनें (check current docs — APIs change between SDKs). Expo Go में background tasks सीमित/अनिश्चित — development build पर test करें।

---

## 🔵 Simple Definition (English)
A **background task** is a small piece of JS the OS wakes up **now and then** while your app is in the background or closed — for example to sync data. You **cannot** choose the exact time; the OS decides based on battery, network and app usage.

## 🔵 सरल परिभाषा (Hindi)
**Background task** JS का छोटा हिस्सा है जिसे OS app के background में या बंद होने पर **कभी-कभी** जगाकर चलाता है — जैसे data sync। आप सटीक समय **तय नहीं** कर सकते; OS battery, network और app के इस्तेमाल के हिसाब से तय करता है।

---

## 🔴 Problem it Solves
```
❌ User ne app khola to purana data dikhe (sync nahi hua)
❌ Har minute chalne wala loop battery khatam karta hai
❌ Android/iOS ke alag background APIs (WorkManager, BGTaskScheduler)
✅ OS-approved periodic task: battery-friendly
```

## 🔴 यह क्यों बना? (Hindi)
```
App खोलते ही पुराना data दिखे तो बुरा लगता है।
Background में हमेशा चलता loop battery खा जाता है।
Android और iOS दोनों के अपने scheduler हैं (WorkManager, BGTaskScheduler);
expo-task-manager + background API इन्हें एक जैसा बना देते हैं।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install expo-task-manager expo-background-fetch
Step 2 → TaskManager.defineTask('SYNC', async () => {...}) — FILE KE TOP LEVEL par (component ke bahar)
Step 3 → Task ke andar kaam karo, phir result return karo (NewData / NoData / Failed)
Step 4 → BackgroundFetch.registerTaskAsync('SYNC', { minimumInterval: 15 * 60, stopOnTerminate: false, startOnBoot: true })
Step 5 → OS apne hisaab se (>= 15 min, aksar zyada) task chalata hai
Step 6 → unregisterTaskAsync('SYNC') jab zaroorat na ho
Step 7 → (SDK 53+) expo-background-task: BackgroundTask.registerTaskAsync('SYNC', { minimumInterval: 15 }) (minutes)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Task को file के सबसे ऊपर (global scope) define करें; React component में नहीं।
Step 2 → Task के अंदर छोटा काम करें (API call, local DB update) और result लौटाएँ।
Step 3 → Register करें; न्यूनतम अंतराल 15 मिनट के आसपास होता है।
Step 4 → OS जब ठीक समझे तब चलाता है — गारंटी नहीं।
```

---

## 🟡 Real World Example
**Swiggy / Zomato:** refresh cached restaurants or pending order status in background. **Paytm:** sync new transactions so the passbook is ready on open. **Gmail / WhatsApp:** background message fetch (via push mostly). **Fitness apps:** periodically write step data.

## 🟡 Real Example Hindi mein
**Swiggy / Zomato:** background में cached restaurants या pending order status ताज़ा करना। **Paytm:** नए transactions sync ताकि app खुलते ही passbook तैयार हो। **Fitness apps:** समय-समय पर steps का डेटा सेव करना।

---

## 💻 Code Example — Basic
```jsx
// BackgroundBasic.jsx — task define + register (SDK 52: expo-background-fetch)
import React, { useEffect, useState } from 'react';                    // React
import { View, Text, Button } from 'react-native';                     // RN UI
import * as TaskManager from 'expo-task-manager';                      // task registry
import * as BackgroundFetch from 'expo-background-fetch';              // periodic fetch

const TASK = 'BACKGROUND_SYNC';                                        // task ka naam

// IMPORTANT: global scope me define karo (component ke bahar)
TaskManager.defineTask(TASK, async () => {
  try {
    console.log('Background sync chala', new Date().toISOString());    // yaha API call karo
    return BackgroundFetch.BackgroundFetchResult.NewData;              // naya data mila
  } catch (e) {
    return BackgroundFetch.BackgroundFetchResult.Failed;               // fail report
  }
});

export default function BackgroundBasic() {
  const [on, setOn] = useState(false);                                 // registered?

  useEffect(() => {
    TaskManager.isTaskRegisteredAsync(TASK).then(setOn);               // pehle se registered?
  }, []);

  const toggle = async () => {
    if (on) await BackgroundFetch.unregisterTaskAsync(TASK);           // band karo
    else await BackgroundFetch.registerTaskAsync(TASK, {
      minimumInterval: 15 * 60,                                        // seconds (min ~15 min)
      stopOnTerminate: false,                                          // Android: app kill ke baad bhi
      startOnBoot: true,                                               // Android: reboot ke baad
    });
    setOn(!on);                                                        // UI update
  };

  return (
    <View style={{ padding: 40, gap: 12 }}>
      <Text>Background sync: {on ? 'ON' : 'OFF'}</Text>
      <Button title={on ? 'Disable' : 'Enable'} onPress={toggle} />
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// backgroundSync.js — status check, safe task, retry-friendly result, cleanup (SDK 52)
import * as TaskManager from 'expo-task-manager';
import * as BackgroundFetch from 'expo-background-fetch';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const SYNC_TASK = 'ORDERS_SYNC';

// Global scope: app start par ek baar evaluate hona chahiye (index.js se import karo)
TaskManager.defineTask(SYNC_TASK, async ({ error }) => {
  if (error) {                                                         // task manager error
    console.warn('Task error', error.message);
    return BackgroundFetch.BackgroundFetchResult.Failed;
  }
  try {
    const res = await fetch('https://example.com/api/orders/pending'); // chhota network kaam
    if (!res.ok) throw new Error(`HTTP ${res.status}`);                // 4xx/5xx
    const data = await res.json();                                     // parse
    await AsyncStorage.setItem('pending_orders', JSON.stringify(data)); // cache
    return data.length
      ? BackgroundFetch.BackgroundFetchResult.NewData                  // naya mila
      : BackgroundFetch.BackgroundFetchResult.NoData;                  // kuch naya nahi
  } catch (e) {
    console.warn('Sync failed', e);
    return BackgroundFetch.BackgroundFetchResult.Failed;               // OS ko batao
  }
});

export async function enableSync() {
  const status = await BackgroundFetch.getStatusAsync();               // Available / Denied / Restricted
  if (status !== BackgroundFetch.BackgroundFetchStatus.Available) {    // user ne Background Refresh band kiya
    return { ok: false, status };
  }
  await BackgroundFetch.registerTaskAsync(SYNC_TASK, {
    minimumInterval: 15 * 60,
    stopOnTerminate: false,
    startOnBoot: true,
  });
  return { ok: true, status };
}

export async function disableSync() {
  if (await TaskManager.isTaskRegisteredAsync(SYNC_TASK)) {
    await BackgroundFetch.unregisterTaskAsync(SYNC_TASK);              // cleanup
  }
}

// --- SDK 53+ (expo-background-task) equivalent ---
// import * as BackgroundTask from 'expo-background-task';
// TaskManager.defineTask(SYNC_TASK, async () => { /* work */ });      // return value zaroori nahi
// await BackgroundTask.registerTaskAsync(SYNC_TASK, { minimumInterval: 15 }); // minutes
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Scheduler | WorkManager / JobScheduler | BGTaskScheduler (BGAppRefreshTask) |
| Minimum interval | ~15 minutes | OS decides (often hours), no guarantee |
| After force-quit | Works with `stopOnTerminate:false` | **Does not run** after user swipe-kills app |
| Setup | `RECEIVE_BOOT_COMPLETED` for startOnBoot | `UIBackgroundModes: fetch` (+ `processing`) via plugin |
| User control | Battery optimisation / Doze delays it | Settings -> Background App Refresh off => `Denied` |
| Run time | ~10 minutes max (WorkManager) | ~30 seconds budget |
| Simulator | Emulator ok-ish | Debug via Xcode "Simulate Background Fetch" |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-task-manager expo-background-fetch  (SDK 53+: expo-background-task)
// app.json plugin adds iOS background modes; dev build use karo
import * as TaskManager from 'expo-task-manager';                      // define + register
TaskManager.defineTask('SYNC', async () => BackgroundFetch.BackgroundFetchResult.NewData);
```
CLI way:
```jsx
// npm i react-native-background-fetch ; pod install ; Info.plist BGTaskSchedulerPermittedIdentifiers + UIBackgroundModes
import BackgroundFetch from 'react-native-background-fetch';           // popular CLI lib
await BackgroundFetch.configure({ minimumFetchInterval: 15 }, async (taskId) => {
  console.log('fetch', taskId);                                        // kaam karo
  BackgroundFetch.finish(taskId);                                      // OS ko batao khatam
}, (taskId) => BackgroundFetch.finish(taskId));                        // timeout handler
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `defineTask` को component/useEffect के अंदर रखना।
✅ Correct: Global scope में, app entry पर import होने वाली file में।

❌ Mistake 2: मान लेना कि task ठीक हर 15 मिनट पर चलेगा।
✅ Correct: यह सिर्फ़ न्यूनतम अंतराल है; OS देर कर सकता है।

❌ Mistake 3: Task में भारी काम (बड़ी file download) करना।
✅ Correct: छोटा, तेज़ काम; भारी काम के लिए server push + foreground।

❌ Mistake 4: Result return न करना (SDK 52 fetch में)।
✅ Correct: `NewData` / `NoData` / `Failed` लौटाएँ।

❌ Mistake 5: Expo Go पर परखकर निष्कर्ष निकालना।
✅ Correct: Development build पर, iOS में Xcode से simulate करें।

---

## 🧠 Tricky Interview Question
You registered a background fetch with `minimumInterval: 60` (1 min) and `stopOnTerminate: false`. On iPhone, after you swipe the app away, does it run every minute?

Answer: No. (1) `minimumInterval` is only a **minimum hint**; Android clamps to ~15 min and iOS chooses its own (often hours). (2) On iOS, if the user **force-quits** the app, the OS won't relaunch it for background fetch. (3) `stopOnTerminate` is Android-only. For real-time updates use **push notifications**, not background fetch.

हिंदी: न्यूनतम अंतराल सिर्फ़ संकेत है; iOS में swipe-kill के बाद task नहीं चलता; `stopOnTerminate` सिर्फ़ Android का है। Real-time के लिए push use करें।

---

## ⚫ Interview Questions + Answers
Q1: Background task और foreground service में फ़र्क?
A1: Background task OS के अनुसार कभी-कभी चलता है; foreground service (Android) notification के साथ लगातार चलती है (जैसे music, navigation)।

Q2: `defineTask` global scope में क्यों?
A2: OS app को headless जगाता है; तब React tree नहीं बनता, सिर्फ़ JS bundle evaluate होता है, इसलिए task पहले से defined होना चाहिए।

Q3: Background में location या download के लिए क्या?
A3: Location के लिए `Location.startLocationUpdatesAsync` (background permission) और downloads के लिए `expo-file-system` का background-capable download (platform सीमा के साथ)।

Q4: SDK 53+ में क्या बदला?
A4: `expo-background-fetch` deprecated; `expo-background-task` आया, interval minutes में और task का return value ज़रूरी नहीं।

Q5: Test कैसे करें?
A5: Android: adb से WorkManager job trigger; iOS: Xcode -> Debug -> Simulate Background Fetch।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Periodic छोटा sync (orders, messages cache)
- Time-insensitive cleanup/upload
- Prefetch content

❌ Avoid when:
- सटीक समय पर काम (alarm/reminder -> Local Notification)
- Real-time updates (Push)
- भारी computation / long download

---

## 📊 Visual Diagram
```
 App code (global): TaskManager.defineTask('SYNC', fn)
            │
 registerTaskAsync('SYNC', {minimumInterval})
            │
   OS Scheduler (WorkManager | BGTaskScheduler)
            │  battery/network/usage ok?
            ▼
   OS wakes app headless ──▶ run fn ──▶ return NewData/NoData/Failed
            │
   (iOS force-quit?) ──✖ no run
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Background task | Work while app not visible | app न दिखे तब का काम |
| Headless | Runs without UI | बिना UI के |
| WorkManager | Android scheduler | Android का scheduler |
| BGTaskScheduler | iOS scheduler | iOS का scheduler |
| Doze | Android battery saver | Android battery-बचत |
| minimumInterval | Minimum gap hint | न्यूनतम अंतराल |

---

## ⚡ 3-Line Summary
English: Define the task at global scope, register it, and the OS runs it occasionally in background.
Timing is never guaranteed and iOS skips it after a force-quit.
Keep it short; use push for real-time needs.

Hindi: Task को global scope में define करें, register करें, OS उसे कभी-कभी background में चलाता है।
समय की गारंटी नहीं और iOS में force-quit के बाद नहीं चलता।
काम छोटा रखें; real-time के लिए push इस्तेमाल करें।

---

## ➡️ Next Topic
**110. App State (foreground/background)** — app कब active/background हुआ यह सुनकर सही काम करना।

---
