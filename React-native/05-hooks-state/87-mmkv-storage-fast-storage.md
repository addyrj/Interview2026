# 87. MMKV Storage (Fast Storage)
# हिंदी में: MMKV Storage (तेज़ Storage)
# Platform: Android ✅ | iOS ✅ | Both ✅ (Expo Go ❌ — development build चाहिए)

> **Expo SDK version:** examples target **Expo SDK 52 (React Native 0.76)** with **react-native-mmkv v3.x** — check current docs — APIs change between SDKs/versions. **Version-dependent:** v3 uses `new MMKV()` and `storage.delete(key)`; the newer v4 (Nitro-based, requires `react-native-nitro-modules` and the New Architecture) uses `createMMKV()` and `storage.remove(key)`. अपने installed version का README देखें।

---

## 🔵 Simple Definition (English)
**MMKV** is a very fast key-value storage originally from WeChat (Tencent), exposed to RN via **`react-native-mmkv`**. It uses **memory-mapped files** and **JSI**, so reads and writes are **synchronous** (no `await`) and much faster than **AsyncStorage**. It also supports **encryption** and multiple instances.

## 🔵 सरल परिभाषा (Hindi)
**MMKV** WeChat (Tencent) का बहुत तेज़ key-value storage है, जिसे RN में **`react-native-mmkv`** से use करते हैं। यह **memory-mapped files** और **JSI** use करता है, इसलिए read/write **synchronous** (बिना `await`) और **AsyncStorage** से बहुत तेज़ हैं। **Encryption** और कई instances भी support हैं।

---

## 🔴 Problem it Solves
```
❌ AsyncStorage: async (await), bridge-based (purane arch me), slow for many reads
❌ App start par token/theme read karne ke liye await -> splash delay, flicker
❌ Unencrypted by default
✅ MMKV: sync get/set, ~30x faster (library ke benchmarks ke mutabiq), encryption option
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ AsyncStorage: async (await), (पुराने arch में) bridge-based, बहुत reads पर धीमा
❌ App start पर token/theme पढ़ने को await -> splash delay, flicker
❌ Default में encrypted नहीं
✅ MMKV: sync get/set, (library के benchmarks के अनुसार) ~30x तक तेज़, encryption option
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install react-native-mmkv  (Expo: then expo prebuild / dev build)
Step 2 → const storage = new MMKV()          (v3)  — one instance, create at module level
Step 3 → storage.set('token', 'abc')         -> writes through memory-mapped file (sync)
Step 4 → storage.getString('token')          -> 'abc' immediately (no await)
Step 5 → Types: set(string|number|boolean|ArrayBuffer); getString/getNumber/getBoolean
Step 6 → Objects: JSON.stringify before set, JSON.parse after get
Step 7 → React hooks: useMMKVString / useMMKVNumber / useMMKVBoolean (re-render on change)
Step 8 → Encryption: new MMKV({ id, encryptionKey }) — key must be stored safely (Keychain/Keystore)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → npx expo install react-native-mmkv  (Expo: फिर dev build / prebuild)
Step 2 → const storage = new MMKV()          (v3) — module level पर एक instance
Step 3 → storage.set('token', 'abc')         -> memory-mapped file में sync लिखता है
Step 4 → storage.getString('token')          -> तुरंत 'abc' (await नहीं)
Step 5 → Types: set(string|number|boolean|ArrayBuffer); getString/getNumber/getBoolean
Step 6 → Objects: set से पहले JSON.stringify, get के बाद JSON.parse
Step 7 → Hooks: useMMKVString / useMMKVNumber / useMMKVBoolean (बदलने पर re-render)
Step 8 → Encryption: new MMKV({ id, encryptionKey }) — key को Keychain/Keystore में रखो
```

---

## 🟡 Real World Example
**Swiggy/Zomato**: remember the last selected city, theme and "seen onboarding" flag, read **synchronously at first render** (no flicker). **Paytm**: cache the last balance for instant display. **Redux/Zustand persist**: store state in MMKV so cold start is faster than AsyncStorage. (Secrets like auth tokens: prefer `expo-secure-store`/Keychain, or MMKV with an encryption key kept in secure storage.)

## 🟡 Real Example Hindi mein
**Swiggy/Zomato**: आख़िरी चुना शहर, theme और "onboarding देख लिया" flag को **पहले render में synchronously** पढ़ना (flicker नहीं)। **Paytm**: आख़िरी balance cache करके तुरंत दिखाना। **Redux/Zustand persist**: state MMKV में रखो, cold start AsyncStorage से तेज़। (Secrets जैसे auth token: `expo-secure-store`/Keychain बेहतर, या MMKV + secure जगह रखी encryption key।)

---

## 💻 Code Example — Basic
```jsx
// Basic: MMKV instance + simple get/set + hooks   (react-native-mmkv v3 API)
// npx expo install react-native-mmkv   -> needs a development build (NOT Expo Go)
import React from 'react';                                          // React
import { View, Text, Button, Switch } from 'react-native';          // UI
import { MMKV, useMMKVString, useMMKVBoolean, useMMKVNumber } from 'react-native-mmkv'; // lib

export const storage = new MMKV();                                  // default instance (create ONCE)

export default function BasicMMKV() {
  // Hooks read/write the same storage and re-render when the key changes
  const [city, setCity] = useMMKVString('city');                    // string | undefined
  const [dark, setDark] = useMMKVBoolean('darkMode');               // boolean | undefined
  const [visits, setVisits] = useMMKVNumber('visits');              // number | undefined

  return (
    <View style={{ padding: 20, gap: 10 }}>
      <Text>City: {city ?? 'not set'}</Text>
      <Button title="Set Mumbai" onPress={() => setCity('Mumbai')} />
      <Button title="Clear city" onPress={() => setCity(undefined)} />{/* undefined deletes key */}

      <Switch value={!!dark} onValueChange={setDark} />{/* persisted switch */}

      <Text>Visits: {visits ?? 0}</Text>
      <Button title="+1 visit" onPress={() => setVisits((visits ?? 0) + 1)} />

      {/* Direct, synchronous API without hooks */}
      <Button title="Log all keys" onPress={() => console.log(storage.getAllKeys())} />
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: typed JSON helpers, encrypted instance, migration from AsyncStorage,
// and adapters for Zustand persist + redux-persist  (react-native-mmkv v3 API)
import { MMKV } from 'react-native-mmkv';                           // lib
import AsyncStorage from '@react-native-async-storage/async-storage'; // only for migration

// 1. Separate instances: app data vs user data (clear user data on logout)
//    encryptionKey: get it from secure storage in production (never hard-code!)
export const appStorage = new MMKV({ id: 'app' });                  // non-sensitive
export const userStorage = new MMKV({
  id: 'user-data',                                                  // separate file
  encryptionKey: 'REPLACE_WITH_KEY_FROM_SECURE_STORE',              // AES; placeholder only
});

// 2. JSON helpers with safe parsing
export function setJSON(store, key, value) {
  store.set(key, JSON.stringify(value));                            // objects -> string
}
export function getJSON(store, key, fallback = null) {
  const raw = store.getString(key);                                 // string | undefined
  if (raw == null) return fallback;                                 // missing
  try { return JSON.parse(raw); }                                   // parse
  catch { return fallback; }                                        // corrupt data -> fallback
}

// 3. One-time migration from AsyncStorage -> MMKV (run at app start)
export async function migrateFromAsyncStorage() {
  if (appStorage.getBoolean('migrated')) return;                    // already done
  const keys = await AsyncStorage.getAllKeys();                     // all old keys
  const pairs = await AsyncStorage.multiGet(keys);                  // [[key, value], ...]
  pairs.forEach(([k, v]) => { if (v != null) appStorage.set(k, v); }); // copy as strings
  appStorage.set('migrated', true);                                 // flag
  await AsyncStorage.multiRemove(keys);                             // cleanup old data
}

// 4. Logout: wipe only user data
export function onLogout() {
  userStorage.clearAll();                                           // remove all keys in this instance
}

// 5. Zustand `persist` storage adapter (createJSONStorage expects this shape)
export const zustandMMKVStorage = {
  setItem: (name, value) => appStorage.set(name, value),            // value is already a string
  getItem: (name) => appStorage.getString(name) ?? null,            // null if missing
  removeItem: (name) => appStorage.delete(name),                    // v3: delete (v4: remove)
};
// usage: persist(store, { name: 'cart', storage: createJSONStorage(() => zustandMMKVStorage) })

// 6. redux-persist storage adapter (returns Promises)
export const reduxPersistMMKVStorage = {
  setItem: (key, value) => { appStorage.set(key, value); return Promise.resolve(true); },
  getItem: (key) => Promise.resolve(appStorage.getString(key)),
  removeItem: (key) => { appStorage.delete(key); return Promise.resolve(); },
};
// usage: persistReducer({ key: 'root', storage: reduxPersistMMKVStorage }, rootReducer)
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Native implementation | C++ MMKV core via JNI | C++ MMKV core via Objective-C++ |
| Data location | App-private files dir | App's Application Support / sandbox |
| Backup | Android Auto Backup may include files (configure `allowBackup`) | iCloud backup may include files |
| Encryption | AES-CFB-128 (library feature) | Same |
| Debugging remote JS | Sync JSI does NOT work in old remote debugger (Chrome) — use Hermes/React Native DevTools | Same |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Native module -> NOT available in Expo Go. Use a development build:
npx expo install react-native-mmkv
npx expo prebuild            # or: eas build --profile development
npx expo run:android         # / npx expo run:ios  (needs Xcode on Mac)
# Fallback for Expo Go: @react-native-async-storage/async-storage
```
CLI way:
```bash
npm install react-native-mmkv
cd ios && pod install && cd ..
npx react-native run-android   # rebuild (native code) — JS reload alone is not enough
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using MMKV in Expo Go
✅ Correct: create a development build (`expo-dev-client`, `eas build`), or use AsyncStorage in Expo Go.

❌ Mistake 2: Creating `new MMKV()` inside a component (new instance every render)
✅ Correct: create once at module level and export it.

❌ Mistake 3: Storing objects directly
```jsx
storage.set('user', { name: 'A' });   // ❌ not supported types
```
✅ Correct: `storage.set('user', JSON.stringify(user))` and parse on read.

❌ Mistake 4: Hard-coding the encryption key or storing secrets plainly
✅ Correct: keep keys in Keychain/Keystore (`expo-secure-store`), use MMKV encryption for extra protection only.

❌ Mistake 5: Assuming `await` is required (or using the v3 API on v4)
✅ Correct: sync API; check your version for `delete` vs `remove`, `new MMKV` vs `createMMKV`.

---

## 🧠 Tricky Interview Question
**Q: MMKV is synchronous. Doesn't synchronous storage block the UI thread? Why is it still recommended?**

**Answer:** The calls run on the JS thread through **JSI** and read/write a **memory-mapped file** — the OS maps the file into memory, so a read is basically a memory access and a write goes to RAM first, with the OS flushing to disk later. Each call takes microseconds, so it doesn't noticeably block. AsyncStorage must cross to a native thread and serialise results (an async hop), which is slower for many small reads. Caveat: don't store huge blobs (MBs) in a key — large values still cost time — and sync means a very large `getAllKeys` + parse loop *can* block the JS thread.

---

## ⚫ Interview Questions + Answers

**Q1: MMKV vs AsyncStorage?**
A1: MMKV: sync, much faster, encryption, hooks, but a native module (needs dev build). AsyncStorage: async, simpler, works in Expo Go, slower and size-limited.

**Q2: Is MMKV secure for tokens?**
A2: It supports AES encryption, but the key must come from secure storage. For highly sensitive tokens prefer Keychain/Keystore (`expo-secure-store`, `react-native-keychain`).

**Q3: How do you store objects/arrays?**
A3: `JSON.stringify` / `JSON.parse` (or store as ArrayBuffer).

**Q4: How to use MMKV with Redux/Zustand?**
A4: Write a storage adapter (`getItem/setItem/removeItem`) and pass to redux-persist / Zustand `persist` (see Advanced example).

**Q5: How do you migrate from AsyncStorage?**
A5: At startup copy all key/values to MMKV once, set a `migrated` flag, then delete old keys.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Frequent small reads/writes (settings, flags, cache, drafts)
- You need sync access at first render
- Persisting Zustand/Redux state

❌ Avoid when:
- You must stay in Expo Go
- Large structured/relational data (use SQLite/WatermelonDB/Realm)
- Storing raw secrets without encryption/secure key handling

---

## 📊 Visual Diagram
```
AsyncStorage:  JS ──await──► bridge/native thread ──► SQLite/file ──► back to JS
MMKV:          JS ──JSI (direct C++ call, sync)──► mmap'd file (RAM-like) 
                          │
                          └─ OS flushes to disk in background

Instances:  [app]  [user-data (encrypted)]  -> clearAll() on logout for user only
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| MMKV | Fast key-value store | तेज़ key-value store |
| JSI | Direct JS ↔ native calls | JS ↔ native सीधी call |
| mmap | File mapped into memory | File को memory में map करना |
| Synchronous | No await needed | बिना await के |
| Encryption key | Secret to encrypt data | Data encrypt करने की key |
| Dev build | Custom Expo client with native code | Native code वाला custom Expo client |
| Migration | Move data from old storage | पुराने storage से data ले जाना |

---

## ⚡ 3-Line Summary
**English:**
1. MMKV is a synchronous, very fast, optionally encrypted key-value store via JSI.
2. Needs a development build (not Expo Go); create one instance and use hooks or adapters.
3. Not for huge/relational data or unprotected secrets; check v3 vs v4 API.

**Hindi:**
1. MMKV JSI से synchronous, बहुत तेज़, optional encryption वाला key-value store है।
2. Development build चाहिए (Expo Go में नहीं); एक instance बनाओ, hooks या adapters use करो।
3. बड़े/relational data या unprotected secrets के लिए नहीं; v3 बनाम v4 API देखो।

---

## ➡️ Next Topic
**88. Context vs Redux vs Zustand** (अगला state-management comparison) और **89. AsyncStorage vs MMKV** (पहले से मौजूद) — सही storage/state tool चुनना।
