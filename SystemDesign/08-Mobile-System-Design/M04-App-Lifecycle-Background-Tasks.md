# M04. App Lifecycle + Background Tasks
# हिंदी में: App Lifecycle + Background Tasks — ऐप की अवस्थाएँ (सामने चल रहा, पीछे गया, रुका हुआ, OS ने बंद किया) और ऐप के पीछे जाने के बाद भी upload, sync, location जैसे काम भरोसे से कैसे चलाएँ

---

## 🔵 Simple Definition (English)
The **app lifecycle** is the set of states the OS moves your app through:
- **iOS**: Not running → Inactive → **Active** (foreground) → **Background** (a few seconds to run) → **Suspended** (frozen in memory) → terminated (killed for memory, without notice).
- **Android**: Activity callbacks `onCreate → onStart → onResume` (foreground) → `onPause → onStop` (background) → `onDestroy`. The **process can be killed anytime** in the background (low memory, Doze, aggressive OEM battery savers).
**Background tasks** are the OS-approved ways to do work when the app isn't in the foreground:
- iOS: `beginBackgroundTask` (short finish-up), **BGTaskScheduler** (app refresh / processing), **background URLSession** (uploads/downloads continue even if the app is suspended or killed), background modes (location, audio, VoIP), silent push.
- Android: **WorkManager** (deferrable, guaranteed work with constraints), **foreground services** (ongoing user-visible work with a notification: navigation, ride tracking, music), JobScheduler, FCM high-priority messages.
- React Native: `AppState`, `expo-task-manager`, `expo-background-task`, background location, Headless JS (Android), background upload libraries.

## 🔵 सरल परिभाषा (Hindi)
App lifecycle = OS ऐप को किन अवस्थाओं से गुज़ारता है — सामने चल रहा (Active), पीछे गया (Background, कुछ सेकंड काम कर सकता है), जमा हुआ (Suspended), और बिना बताए बंद (memory कम होने पर)। Android पर background में process कभी भी मारा जा सकता है (Doze, Xiaomi/Oppo/Vivo जैसे फ़ोन के battery saver)।
Background tasks = OS की अनुमति वाले तरीके: iOS में BGTaskScheduler, background URLSession (ऐप बंद हो तब भी upload चलता रहे), location/audio modes; Android में WorkManager (शर्तों के साथ पक्का काम), foreground service (notification के साथ लगातार काम — ride tracking); RN में AppState, expo-task-manager वग़ैरह।

---

## 🔴 Problem it Solves
Mobile OSes aggressively protect **battery and memory**, so apps **cannot run freely in the background**. Naive apps break in common situations:
- A user starts a **video upload**, switches to WhatsApp, and the upload dies. Or the app is killed and the upload is lost.
- A **chat message sent offline** is never delivered because the app was closed.
- A **delivery partner's location stops updating** when the screen turns off. This is common on Chinese-OEM phones popular in India, whose battery optimizers kill background apps.
- After the OS kills the app in the background, the user returns to a **blank or reset screen** and loses form input.
- Polling in the background **drains battery**, causing bad reviews and OS restrictions.
Understanding the lifecycle lets you **persist state, resume work, and use the right background API** for each job.

## 🔴 यह क्यों बना? (Hindi)
OS battery और memory बचाने के लिए ऐप को background में मनमर्ज़ी से चलने नहीं देता। लापरवाह ऐप टूटते हैं: video upload शुरू किया, WhatsApp खोला — upload मर गया; offline भेजा message कभी नहीं गया; screen बंद होते ही delivery partner की location रुकी (भारत में लोकप्रिय Xiaomi/Oppo/Vivo के battery saver ऐप मार देते हैं); वापस आने पर form ख़ाली; background polling से battery ख़त्म।
Lifecycle समझकर: state सहेजो, काम दोबारा शुरू करो, और हर काम के लिए सही background API चुनो।

---

## 🟢 How it Works — Step by Step

### App states (simplified)

```
iOS                                         Android
┌────────────┐  user leaves   ┌──────────┐   onResume ┌───────────┐ onPause/onStop ┌────────────┐
│  ACTIVE    │ ─────────────► │BACKGROUND│            │FOREGROUND │ ─────────────► │ BACKGROUND │
│ (fg, input)│ ◄───────────── │ (~secs)  │            │ (visible) │ ◄───────────── │ (cached)   │
└────────────┘  user returns  └────┬─────┘            └───────────┘                └─────┬──────┘
      ▲ INACTIVE (calls, control    │ time up                                            │ low memory /
      │ center, app switcher)       ▼                                                    │ Doze / OEM killer
                               ┌──────────┐  memory pressure  ┌────────────┐              ▼
                               │SUSPENDED │ ────────────────► │ TERMINATED │       PROCESS DEATH
                               │ (frozen) │  (no callback!)   └────────────┘ (restore saved state on return)
                               └──────────┘
React Native AppState: 'active' | 'background' | 'inactive' (iOS only)
```

### Picking the right background mechanism

```
┌─────────────────────────────────┬──────────────────────────────────┬──────────────────────────────────┐
│ Job                             │ iOS                              │ Android                          │
├─────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┤
│ Finish a quick save/request     │ beginBackgroundTask (~30 s)      │ just do it / WorkManager expedited│
│ Large upload/download           │ Background URLSession (system    │ WorkManager (+ foreground service │
│                                 │ continues even if app killed)    │ type dataSync for long uploads)   │
│ Periodic sync (feed, outbox)    │ BGAppRefreshTask (OS decides when│ WorkManager periodic (≥ 15 min,   │
│                                 │ — not guaranteed, ~30 s budget)  │ constraints: network, battery)    │
│ Heavy processing (ML, cleanup)  │ BGProcessingTask (often charging,│ WorkManager w/ requiresCharging   │
│                                 │ idle)                            │                                  │
│ Continuous location (ride/      │ Background location mode +       │ Foreground service (type=location)│
│ delivery tracking)              │ "Always" permission / significant│ + persistent notification         │
│                                 │ location changes                 │                                  │
│ Music/podcast playback          │ Audio background mode            │ Foreground service (mediaPlayback)│
│ Incoming calls (VoIP)           │ PushKit + CallKit                │ FCM high-priority + ConnectionSvc │
│ Wake app with new data          │ Silent push (content-available,  │ FCM data message (high priority   │
│                                 │ throttled, not guaranteed)       │ for user-visible notifications)   │
└─────────────────────────────────┴──────────────────────────────────┴──────────────────────────────────┘
Rule: background execution is a PRIVILEGE the OS may deny — design so correctness never depends on it.
```

### Android realities (important in India)

```
- Doze mode: screen off + stationary → network & jobs deferred to maintenance windows
- App Standby Buckets: rarely-used apps get fewer jobs/alarms
- Android 12+: can't start foreground services from background (exceptions exist); Android 14 requires
  declaring foreground service TYPES (location, dataSync, mediaPlayback, …) + matching permissions
- OEM battery optimizers (Xiaomi MIUI/HyperOS, Oppo/Realme ColorOS, Vivo FuntouchOS, Samsung) kill
  background apps aggressively → guide users to "Allow background activity / No restrictions"
  (dontkillmyapp.com documents per-OEM steps); detect and show an in-app guide for delivery partners
```

### Designing for lifecycle (patterns)

```
1. Persist early: write user input/drafts/outbox to storage immediately (MMKV/SQLite), not on "exit"
2. On background: flush analytics, close sockets, pause timers/animations, save navigation state
3. On foreground: refresh stale data, reconnect sockets, flush outbox, re-check permissions & auth
4. Process death: restore navigation state + drafts; reload data from local DB (source of truth)
5. Long jobs: hand to OS-managed systems (background URLSession / WorkManager) with resumable,
   idempotent operations; track job state in DB; show progress via notification
6. Wake-ups: use push for server-initiated updates instead of background polling
7. Battery: batch work, respect constraints (Wi-Fi/charging for big syncs), back off on failures
```

## 🟢 कैसे काम करता है? (Hindi)
1. iOS: Active → Background (कुछ सेकंड) → Suspended (जमा) → बिना बताए बंद; Android: onResume/onPause/onStop, और background में process कभी भी मर सकता है — RN में `AppState` से पता चलता है।
2. सही तरीका चुनो: छोटा काम ख़त्म करना — beginBackgroundTask; बड़ा upload — iOS background URLSession / Android WorkManager; समय-समय पर sync — BGAppRefresh/WorkManager periodic (OS तय करता है कब); लगातार location — iOS background location / Android foreground service + notification।
3. भारत में ज़रूरी: Doze, Android 12+ और 14 के नियम (foreground service type), और Xiaomi/Oppo/Vivo के battery optimizer — delivery partners को "No restrictions" सेट करने का in-app guide दिखाओ।
4. Pattern: input/draft/outbox तुरंत save; background में sockets बंद, analytics flush; foreground पर refresh, reconnect, outbox flush; process मरने के बाद navigation और drafts वापस।
5. Background चलना OS की मेहरबानी है — सही काम उस पर निर्भर न हो; server से नई ख़बर के लिए push, polling नहीं; बड़े sync Wi-Fi/charging पर।

---

## 🟡 Real World Example

**Uber / Ola / Rapido driver apps** — use Android foreground services with a persistent "You're online" notification and iOS background location, so trip tracking continues with the screen off. They throttle GPS frequency based on trip state to save battery.

**Swiggy / Zomato / Zepto delivery partner apps** — commonly guide partners through OEM-specific battery settings (MIUI, ColorOS) so the app isn't killed, because aggressive OEM killers on budget phones would otherwise stop location updates and order alerts.

**WhatsApp / Google Photos** — media uploads and backups run via OS-managed background transfers or WorkManager with constraints (Wi-Fi only, charging), and resume after interruptions.

**Spotify / JioSaavn** — use the audio background mode and media foreground services, with lock-screen controls via platform media sessions.

## 🟡 Real Example Hindi में
Uber/Ola/Rapido के driver ऐप Android पर foreground service ("आप online हैं" notification) और iOS पर background location से screen बंद होने पर भी trip tracking चलाते हैं; trip की स्थिति के हिसाब से GPS कम-ज़्यादा।
Swiggy/Zomato/Zepto के delivery partner ऐप आम तौर पर MIUI/ColorOS की battery settings बदलवाने का guide दिखाते हैं; WhatsApp/Google Photos के backup Wi-Fi और charging की शर्त पर background में चलते हैं।

---

## 🟠 My Stack Example

### React Native: lifecycle hooks
```ts
// src/platform/lifecycle.ts
import { AppState, AppStateStatus } from 'react-native';
let current: AppStateStatus = AppState.currentState;
AppState.addEventListener('change', async (next) => {
  if (current.match(/inactive|background/) && next === 'active') {
    realtime.connect(); outbox.flush(); queryClient.invalidateQueries({ queryKey: ['orders'] });
    await checkPermissionsStillGranted();            // user may have revoked location in Settings
  }
  if (next === 'background') { realtime.close(); analytics.flush(); saveNavigationState(); }
  current = next;
});
```

### Periodic background sync with expo-background-task (OS-scheduled, best-effort)
```ts
import * as TaskManager from 'expo-task-manager';
import * as BackgroundTask from 'expo-background-task';

const SYNC_TASK = 'outbox-sync';
TaskManager.defineTask(SYNC_TASK, async () => {         // must be defined at module top-level (runs headless)
  try {
    const sent = await outbox.flush({ timeoutMs: 20_000 });   // keep under OS time budget
    await ordersRepo.refresh();
    return BackgroundTask.BackgroundTaskResult.Success;
  } catch { return BackgroundTask.BackgroundTaskResult.Failed; }
});
export async function registerBackgroundSync() {
  await BackgroundTask.registerTaskAsync(SYNC_TASK, { minimumInterval: 15 });   // minutes; OS decides actual timing
}
```

### Upload that survives backgrounding (iOS background session via expo-file-system)
```ts
import * as FileSystem from 'expo-file-system';     // Expo SDK 54+: this classic API is at 'expo-file-system/legacy'
const res = await FileSystem.uploadAsync(presignedUrl, localVideoUri, {
  httpMethod: 'PUT',
  uploadType: FileSystem.FileSystemUploadType.BINARY_CONTENT,
  sessionType: FileSystem.FileSystemSessionType.BACKGROUND,   // iOS: continues when app is backgrounded
  headers: { 'Content-Type': 'video/mp4' },
});
// For very large files use chunked/resumable upload (M21) with per-chunk state persisted in DB
```

### Continuous location for a delivery partner (foreground service on Android)
```ts
import * as Location from 'expo-location';
const LOCATION_TASK = 'partner-location';
TaskManager.defineTask(LOCATION_TASK, async ({ data, error }) => {
  if (error) return;
  const { locations } = data as { locations: Location.LocationObject[] };
  await locationBuffer.append(locations);                 // persist first (MMKV/SQLite)
  await locationBuffer.flushIfDue();                      // batch POST every ~10–15 s
});

export async function goOnline() {
  const fg = await Location.requestForegroundPermissionsAsync();
  const bg = await Location.requestBackgroundPermissionsAsync();          // "Allow all the time"
  if (fg.status !== 'granted' || bg.status !== 'granted') return showPermissionHelp();
  await Location.startLocationUpdatesAsync(LOCATION_TASK, {
    accuracy: Location.Accuracy.High, distanceInterval: 25, timeInterval: 5000,
    foregroundService: { notificationTitle: 'You are online', notificationBody: 'Sharing location for deliveries', killServiceOnDestroy: false },
    pausesUpdatesAutomatically: false, activityType: Location.ActivityType.AutomotiveNavigation,  // iOS
    showsBackgroundLocationIndicator: true,
  });
}
```
```json
// app.json (Expo config) — declare permissions & background modes
{ "expo": {
  "ios": { "infoPlist": { "UIBackgroundModes": ["location", "fetch", "processing"],
    "NSLocationAlwaysAndWhenInUseUsageDescription": "We share your location with customers during deliveries." } },
  "android": { "permissions": ["ACCESS_FINE_LOCATION", "ACCESS_BACKGROUND_LOCATION", "FOREGROUND_SERVICE", "FOREGROUND_SERVICE_LOCATION"] } } }
```

### Guide users through OEM battery settings (Android)
```ts
import * as IntentLauncher from 'expo-intent-launcher';
import * as Device from 'expo-device';
export async function openBatteryOptimizationSettings() {
  if (['Xiaomi', 'OPPO', 'vivo', 'realme', 'OnePlus'].includes(Device.manufacturer ?? '')) showOemGuide(Device.manufacturer!);
  await IntentLauncher.startActivityAsync('android.settings.IGNORE_BATTERY_OPTIMIZATION_SETTINGS');
}
```

---

## ⚫ Interview Questions + Answers

**Q1: What happens to an app when it goes to the background on iOS vs Android?**
A1: On iOS the app moves to the background state with a few seconds to finish work (extendable briefly via `beginBackgroundTask`), then is suspended: frozen in memory with no code running. It may be terminated without notice under memory pressure. It can only run in the background via specific mechanisms (background URLSession, BGTaskScheduler, declared modes like location or audio, silent push). On Android, `onPause/onStop` are called and the process stays cached but can be killed anytime. Background work should use WorkManager or foreground services, subject to Doze, standby buckets, Android 12+/14 restrictions and OEM battery killers.

**Q2: How would you make a large video upload reliable when the user leaves the app?**
A2: Persist an upload job record (file URI, upload session ID, uploaded chunks) in the local DB. Use OS-managed transfers: a background URLSession on iOS (continues while suspended or after termination) and WorkManager on Android (optionally a dataSync foreground service with a progress notification). Upload in resumable chunks to presigned URLs (multipart or tus). On interruption, resume from the last acknowledged chunk. Make the finalize call idempotent, show progress and completion via notifications, and retry with backoff under network constraints.

**Q3: How do you handle process death on Android?**
A3: Assume the process can be killed whenever the app is backgrounded. Persist important state continuously (drafts, form input, outbox, current screen and params) to fast storage, use the local DB as the data source of truth, and restore the navigation state and inputs on relaunch. Make in-flight operations resumable and idempotent. Test by enabling "Don't keep activities" or killing the process via adb while the app is backgrounded.

**Q4: How would you implement continuous location tracking for a ride app without killing battery?**
A4: Request foreground and background ("Always") location permission with clear rationale. Run tracking in an Android foreground service (location type) with a persistent notification, and use iOS background location mode. Adapt accuracy and frequency to trip state (high accuracy and every few seconds on an active trip; low frequency or significant-change when idle or offline), use distance filters, batch uploads every 10–15 s over a single connection, buffer locally when offline, stop tracking promptly when the driver goes offline, and monitor battery impact. More in M20.

**Q5: Can you rely on background fetch or silent push for syncing?**
A5: Not for correctness. iOS background app refresh and silent pushes are scheduled at the OS's discretion, throttled based on usage, battery and Low Power Mode, and don't run if the user force-quit the app. Android periodic work is subject to Doze and standby buckets and OEM killers. Use them as opportunistic optimizations. Guarantee correctness by syncing on app foreground, using user-visible push notifications for important events, server-side retries, and OS-managed transfers for uploads.

---

## 🔷 Trade-offs
✅ OS-managed background work (URLSession, WorkManager): reliable, battery-friendly — ❌ timing not under your control.
✅ Foreground services: continuous work — ❌ persistent notification, strict policies, battery drain, Play Store scrutiny.
✅ Silent push / background fetch: freshness — ❌ throttled, not guaranteed.
✅ Persist-everything approach: resilient to kills — ❌ more storage writes and migration care.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Foreground / Active | App visible & interactive | ऐप सामने चालू |
| Background | Not visible, limited time | पीछे, सीमित समय |
| Suspended | Frozen in memory | memory में जमा हुआ |
| Process death | OS kills the app process | OS ने ऐप मार दिया |
| BGTaskScheduler | iOS scheduled background tasks | iOS के background काम |
| Background URLSession | iOS system-managed transfers | iOS का background transfer |
| WorkManager | Android guaranteed deferrable work | Android का पक्का background काम |
| Foreground service | Android ongoing work + notification | notification वाला लगातार काम |
| Doze | Android deep battery saving | Android की गहरी battery बचत |
| OEM battery killer | Vendor background restrictions | फ़ोन कंपनी की पाबंदी |

---

## ⚡ 3-Line Summary
**English:**
1. Apps get backgrounded, suspended and killed without notice; persist state early and restore it (local DB, drafts, navigation, outbox).
2. Use the right OS mechanism: background URLSession/WorkManager for transfers, BGTask/periodic work for opportunistic sync, foreground services/background location for continuous tracking.
3. Never depend on background execution for correctness: sync on foreground, push for server events, handle Doze/OEM killers, respect battery.

**Hindi:**
1. ऐप बिना बताए background, suspend और बंद होता है — state तुरंत save करो और वापस लाओ।
2. सही OS तरीका: transfers के लिए URLSession/WorkManager, sync के लिए BGTask, tracking के लिए foreground service।
3. सही काम background पर निर्भर न हो: foreground पर sync, server events के लिए push, Doze/OEM killers और battery का ध्यान।

---

## ➡️ Next Topic Suggestion
**M05. Local Storage (AsyncStorage, MMKV, SQLite, WatermelonDB, Keychain)** — Persisting state is the foundation of reliable apps. Next: the storage options on React Native, when to use each, and how to keep data fast, migrated and secure.
