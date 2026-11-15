# 259. Expo Updates (OTA)
# हिंदी में: Expo Updates — expo-updates library
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52+ examples (check current docs — APIs change between SDKs). Topic 260 covers the EAS Update service workflow; this note covers the `expo-updates` client library and config.

---

## 🔵 Simple Definition (English)
`expo-updates` is the library inside your app that checks for, downloads and launches updated JS bundles. It is configured in app.json (`updates`, `runtimeVersion`) and controlled in code with `Updates.checkForUpdateAsync`, `fetchUpdateAsync`, `reloadAsync` and the `useUpdates` hook.

## 🔵 सरल परिभाषा (Hindi)
`expo-updates` app के अंदर की library है जो नए JS bundle को check, download और launch करती है। इसे app.json (`updates`, `runtimeVersion`) में configure करते हैं और code में `checkForUpdateAsync`, `fetchUpdateAsync`, `reloadAsync` और `useUpdates` hook से control करते हैं।

---

## 🔴 Problem it Solves
```
PROBLEM: App needs a safe, standard way to pull new JS and fall back if it fails.
SOLUTION: expo-updates handles manifest check, download, caching, launch, and fallback.
```

## 🔴 यह क्यों बना? (Hindi)
हर टीम अपना OTA system बनाए तो गलतियाँ होंगी। expo-updates manifest check, download, cache, launch और fallback standard तरीके से संभालता है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → On app start native code loads the newest valid cached update, else embedded bundle
Step 2 → If updates.checkAutomatically allows, it asks the server for a manifest
Step 3 → Manifest compared by runtimeVersion + channel (request header) + update id
Step 4 → New assets/bundle downloaded to local storage
Step 5 → fallbackToCacheTimeout decides how long launch waits for the download
Step 6 → New bundle used now (if downloaded in time) or on next launch
```

### Key config (app.json)
| Key | Purpose |
|-----|---------|
| `updates.url` | Update server URL (`https://u.expo.dev/<projectId>`) |
| `updates.enabled` | Turn updates on/off |
| `updates.checkAutomatically` | `ON_LOAD` (default), `ON_ERROR_RECOVERY`, `WIFI_ONLY`, `NEVER` |
| `updates.fallbackToCacheTimeout` | ms to wait for download at launch (0 = launch immediately) |
| `runtimeVersion` | String or `{ "policy": ... }` |

### API (from `expo-updates`)
| API | Use |
|-----|-----|
| `Updates.isEnabled` | false in dev mode |
| `Updates.checkForUpdateAsync()` | returns `{ isAvailable, manifest }` |
| `Updates.fetchUpdateAsync()` | downloads it |
| `Updates.reloadAsync()` | restart into new bundle |
| `Updates.useUpdates()` | hook with `isUpdateAvailable`, `isUpdatePending`, `isChecking`, `isDownloading`, `downloadError`, etc. |
| `Updates.channel`, `Updates.runtimeVersion`, `Updates.updateId` | info about current update |

## 🟢 कैसे काम करता है? (Hindi)
1. App start पर सबसे नया valid cached update चलता है, नहीं तो embedded bundle।
2. `checkAutomatically` allow करे तो server से manifest माँगा जाता है।
3. runtimeVersion + channel से match देखा जाता है।
4. नया bundle/assets download होते हैं।
5. `fallbackToCacheTimeout` तय करता है कि launch पर download का कितना इंतज़ार करें।
6. नया bundle तुरंत (समय पर मिला तो) या अगले launch पर चलता है।

---

## 🟡 Real World Example
Zomato-जैसा app WiFi पर बड़ा update लेना चाहे तो `checkAutomatically: "WIFI_ONLY"` रखता है ताकि mobile data बचे। Paytm-जैसा app लेन-देन के बीच reload नहीं करना चाहता, इसलिए update चुपचाप download करके user के home screen पर लौटने पर "Restart" prompt देता है।

## 🟡 Real Example Hindi mein
Data बचाने के लिए update सिर्फ WiFi पर लो। Payment के बीच अचानक restart न हो, इसलिए download करके बाद में user से "Restart" पूछो।

---

## 💻 Code Example — Basic (manual check on button)
```jsx
// CheckUpdate.jsx - manual OTA check, fetch, reload
import React, { useState } from 'react';                         // React + state
import { View, Text, Button, Alert } from 'react-native';       // UI
import * as Updates from 'expo-updates';                         // OTA API

export default function CheckUpdate() {                          // component
  const [msg, setMsg] = useState('');                            // status text

  const run = async () => {                                      // button handler
    if (!Updates.isEnabled) { setMsg('Updates disabled in dev'); return; } // dev mode guard
    try {                                                        // network may fail
      setMsg('Checking...');                                     // status
      const r = await Updates.checkForUpdateAsync();             // ask server
      if (!r.isAvailable) { setMsg('You are up to date'); return; } // nothing new
      setMsg('Downloading...');                                  // status
      await Updates.fetchUpdateAsync();                          // download bundle
      Alert.alert('Update ready', 'Restart now?', [              // ask user
        { text: 'Later', style: 'cancel' },                      // keep using old
        { text: 'Restart', onPress: () => Updates.reloadAsync() }, // apply now
      ]);
    } catch (e) {
      setMsg('Error: ' + e.message);                             // show error
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <Text>Runtime: {Updates.runtimeVersion ?? 'n/a'}</Text>
      <Text>Channel: {Updates.channel ?? 'n/a'}</Text>
      <Button title="Check for update" onPress={run} />
      <Text>{msg}</Text>
    </View>
  );
}
```

## 💻 Code Example — Advanced (config + silent download on app foreground)
```json
{
  "expo": {
    "version": "2.5.0",
    "runtimeVersion": { "policy": "appVersion" },
    "updates": {
      "url": "https://u.expo.dev/YOUR-PROJECT-ID",
      "checkAutomatically": "WIFI_ONLY",
      "fallbackToCacheTimeout": 0
    }
  }
}
```
```jsx
// useSilentUpdate.js - download in background when app returns to foreground
import { useEffect, useRef } from 'react';                       // hooks
import { AppState } from 'react-native';                         // app foreground events
import * as Updates from 'expo-updates';                         // OTA

export function useSilentUpdate() {                              // use once in App root
  const busy = useRef(false);                                    // avoid parallel checks
  useEffect(() => {
    const sub = AppState.addEventListener('change', async (s) => { // listen to state changes
      if (s !== 'active' || busy.current || !Updates.isEnabled) return; // only when foreground
      busy.current = true;                                       // lock
      try {
        const r = await Updates.checkForUpdateAsync();           // check
        if (r.isAvailable) await Updates.fetchUpdateAsync();     // download only; apply next launch
      } catch (e) {
        console.warn('OTA check failed', e);                     // never crash
      } finally {
        busy.current = false;                                    // unlock
      }
    });
    return () => sub.remove();                                   // cleanup listener
  }, []);
}
```
Not run (needs a real build with expo-updates enabled).

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Config source | AndroidManifest meta-data (generated by prebuild) | Expo.plist (generated) |
| Embedded bundle | in APK/AAB assets | in IPA |
| Reload behaviour | Process restart of JS context | Same |
| Store policy | Play policy: no misleading changes | 2.5.2 limits |
| Dev mode | Updates disabled | Updates disabled |
| Native rollback | Fallback to embedded/older update | Same |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx expo install expo-updates && eas update:configure   # writes app.json entries
eas build -p all --profile production                    # binary embeds config
eas update --channel production --message "fix"         # publish
```
CLI way:
```bash
npm i expo-updates                 # in bare RN after install-expo-modules
npx pod-install                    # iOS
# set EXUpdatesURL / runtimeVersion in Expo.plist and AndroidManifest.xml manually
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Calling `checkForUpdateAsync` in dev and expecting results.
✅ Correct: Guard with `Updates.isEnabled`; test on a preview build.

❌ Mistake 2: Using `reloadAsync` in the middle of a payment or form.
✅ Correct: Reload at a safe moment, after asking the user.

❌ Mistake 3: Same runtimeVersion after native change.
✅ Correct: Change runtimeVersion (e.g. use `fingerprint` policy or bump version).

❌ Mistake 4: Setting a long `fallbackToCacheTimeout` and blocking launch on bad network.
✅ Correct: Keep it small (0 to a few seconds).

---

## 🧠 Tricky Interview Question
With `fallbackToCacheTimeout: 0` and `checkAutomatically: ON_LOAD`, when does a user first see your new update?

Answer: On the launch after the one that downloaded it. With 0, the app starts immediately using the cached/embedded bundle while the new one downloads in the background; it will be used on the next cold start (unless you call `reloadAsync`).

---

## ⚫ Interview Questions + Answers
Q1: Which hook gives update state?
A1: `Updates.useUpdates()`.

Q2: How do you disable automatic checks?
A2: `updates.checkAutomatically: "NEVER"` and check manually.

Q3: What is `Updates.updateId` for?
A3: Identifies the running update; useful in crash reports (Sentry tags).

Q4: Why is `isEnabled` false in dev?
A4: Dev builds load JS from Metro, not from update bundles.

Q5: What decides compatibility?
A5: `runtimeVersion`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Expo-managed or bare apps with expo-updates; JS-only fixes

❌ Avoid when:
- Native module changes; very tightly regulated apps without release approval for OTA

---

## 📊 Visual Diagram
```
 app.json -> binary (updates.url, runtimeVersion)
 launch -> load cached/embedded
        -> check manifest (runtime+channel)
        -> fetch -> store
        -> next launch / reloadAsync
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Manifest | Update description JSON | Update का विवरण |
| fallbackToCacheTimeout | Max wait at launch | Launch पर इंतज़ार |
| checkAutomatically | Auto-check policy | अपने-आप check |
| reloadAsync | Restart JS with new bundle | नया bundle लोड |
| updateId | Unique update id | Update पहचान |

---

## ⚡ 3-Line Summary
English: expo-updates checks, downloads, and launches new JS bundles.
Configure with app.json and control with the Updates API/hook.
Keep runtimeVersion correct and avoid reloading mid-task.

Hindi: expo-updates नए JS bundle को check, download और launch करता है।
app.json से configure करो और Updates API/hook से control करो।
runtimeVersion सही रखो और काम के बीच reload मत करो।

---

## ➡️ Next Topic
**260. EAS Update (OTA)** (already written) then **261. CodePush** — पुराना OTA विकल्प।
