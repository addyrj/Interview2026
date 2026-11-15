# 88. AsyncStorage
# हिंदी में: AsyncStorage (फ़ोन में छोटा डेटा सेव करना)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: Expo SDK 52 (React Native 0.76) + `@react-native-async-storage/async-storage` (check current docs — APIs change between SDKs; Expo Go में यह पहले से bundled है, version `npx expo install` से मिलता है).
> Note: `89-asyncstorage-vs-mmkv.md` में comparison है; यहाँ API की basics + production pattern है।

---

## 🔵 Simple Definition (English)
**AsyncStorage** is a simple, unencrypted, asynchronous key-value store that keeps **string** data on the phone's disk. Data stays after the app is closed. Objects must be converted with `JSON.stringify` before saving.

## 🔵 सरल परिभाषा (Hindi)
**AsyncStorage** फ़ोन की disk पर **string** डेटा रखने वाला आसान, बिना encryption वाला, asynchronous key-value store है। App बंद होने के बाद भी डेटा बना रहता है। Object को save करने से पहले `JSON.stringify` करना पड़ता है।

---

## 🔴 Problem it Solves
```
❌ useState का डेटा app restart पर उड़ जाता है
❌ हर बार server से theme / language / onboarding flag माँगना
❌ Native file system API सीधे use करना मुश्किल
✅ एक छोटा key-value API: setItem / getItem / removeItem
✅ Offline cache, "pehli baar app khola" flag, draft text
```

## 🔴 यह क्यों बना? (Hindi)
```
React state RAM में रहता है, app बंद होते ही मिट जाता है।
Theme, language, login-onboarding जैसी छोटी चीज़ें
बार-बार server से लाना बेकार है।
AsyncStorage एक आसान API देता है जो दोनों OS पर एक जैसा चलता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install @react-native-async-storage/async-storage
Step 2 → import AsyncStorage from '@react-native-async-storage/async-storage'
Step 3 → await AsyncStorage.setItem('key', 'string')          (save)
Step 4 → const v = await AsyncStorage.getItem('key')          (read, null if missing)
Step 5 → Object ho to JSON.stringify (save) / JSON.parse (read)
Step 6 → removeItem(key) ya clear() se delete
Step 7 → Android: SQLite file | iOS: file/manifest me native storage hota hai
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Package install करें।
Step 2 → हर call async है, इसलिए await / .then use करें।
Step 3 → Value हमेशा string होती है; object को JSON में बदलें।
Step 4 → Key न मिले तो getItem null देता है (error नहीं)।
Step 5 → Native तरफ़ Android में SQLite और iOS में file-based storage होता है।
```

---

## 🟡 Real World Example
**Swiggy / Zomato:** The last selected delivery address, the "onboarding already seen" flag and dark-mode choice are stored locally so the app opens instantly. **Paytm:** keeps a non-sensitive "language = hi" preference. (Tokens/passwords must go to `expo-secure-store`, not AsyncStorage.)

## 🟡 Real Example Hindi mein
**Swiggy / Zomato:** आख़िरी चुना हुआ address, "onboarding देख ली" flag और dark-mode की पसंद फ़ोन में रखी जाती है ताकि app तुरंत खुले। **Paytm:** भाषा "hi" जैसी non-sensitive पसंद सेव होती है। (Token / password के लिए `expo-secure-store` use करें, AsyncStorage नहीं।)

---

## 💻 Code Example — Basic
```jsx
// AsyncBasic.jsx — ek naam save karo aur app restart ke baad wapas dikhao
import React, { useEffect, useState } from 'react';                    // React + hooks
import { View, Text, TextInput, Button, StyleSheet } from 'react-native'; // RN UI
import AsyncStorage from '@react-native-async-storage/async-storage';  // storage

const KEY = 'user_name';                                               // storage key (constant)

export default function AsyncBasic() {
  const [name, setName] = useState('');                                // input ka text
  const [saved, setSaved] = useState(null);                            // storage se aaya naam

  useEffect(() => {                                                    // mount par ek baar chalega
    AsyncStorage.getItem(KEY).then((v) => setSaved(v));                // purani value padho (null ho sakti hai)
  }, []);                                                              // empty deps = sirf ek baar

  const save = async () => {                                           // Save button handler
    await AsyncStorage.setItem(KEY, name);                             // string save karo
    setSaved(name);                                                    // UI update
  };

  const remove = async () => {                                         // Delete button handler
    await AsyncStorage.removeItem(KEY);                                // key hatao
    setSaved(null);                                                    // UI reset
  };

  return (
    <View style={styles.box}>
      <TextInput style={styles.input} value={name} onChangeText={setName} placeholder="Naam likho" />
      <Button title="Save" onPress={save} />
      <Button title="Delete" onPress={remove} />
      <Text>Saved: {saved ?? 'kuch nahi'}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  box: { padding: 24, gap: 12 },                                       // container
  input: { borderWidth: 1, padding: 8 },                               // input border
});
```

## 💻 Code Example — Advanced
```jsx
// storage.js + useStoredState.js — typed JSON helper, error handling, multi ops
import { useEffect, useState, useCallback } from 'react';              // hooks
import AsyncStorage from '@react-native-async-storage/async-storage';  // storage

// ---- Safe JSON helpers (crash nahi karte) ----
export async function getJSON(key, fallback = null) {
  try {
    const raw = await AsyncStorage.getItem(key);                       // string ya null
    return raw != null ? JSON.parse(raw) : fallback;                   // parse; missing => fallback
  } catch (e) {
    console.warn('getJSON failed', key, e);                            // corrupt JSON / IO error
    return fallback;                                                   // app ko crash mat karo
  }
}

export async function setJSON(key, value) {
  try {
    await AsyncStorage.setItem(key, JSON.stringify(value));            // object => string
    return true;                                                       // success
  } catch (e) {
    console.warn('setJSON failed', key, e);                            // disk full etc.
    return false;
  }
}

// ---- Hook: useState jaisa, par persist hota hai ----
export function useStoredState(key, initial) {
  const [value, setValue] = useState(initial);                         // in-memory value
  const [ready, setReady] = useState(false);                           // storage se load hua?

  useEffect(() => {
    let alive = true;                                                  // unmount guard
    getJSON(key, initial).then((v) => {
      if (alive) { setValue(v); setReady(true); }                      // hydrate
    });
    return () => { alive = false; };                                   // cleanup
  }, [key]);                                                           // eslint-disable-line

  const update = useCallback((next) => {
    setValue(next);                                                    // UI turant update
    setJSON(key, next);                                                // background me save
  }, [key]);

  return [value, update, ready];                                       // [value, setter, loaded]
}

// ---- Multi operations (ek saath kai keys) ----
export async function saveSession(user, prefs) {
  await AsyncStorage.multiSet([                                        // batch write
    ['user', JSON.stringify(user)],
    ['prefs', JSON.stringify(prefs)],
  ]);
}
export async function loadSession() {
  const pairs = await AsyncStorage.multiGet(['user', 'prefs']);        // [[key, value], ...]
  return Object.fromEntries(pairs.map(([k, v]) => [k, v ? JSON.parse(v) : null]));
}
export async function mergePrefs(patch) {
  await AsyncStorage.mergeItem('prefs', JSON.stringify(patch));        // existing JSON me merge
}
export async function logout() {
  await AsyncStorage.multiRemove(['user', 'prefs']);                   // sirf apni keys hatao
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Native storage | SQLite database | Files (manifest + chunks) |
| Size limit | Default ~6 MB total (configurable in native `gradle.properties`) | No hard limit, but each value should be small |
| Encryption | None by default | None by default |
| Backup | Android Auto Backup may restore it | iCloud/iTunes backup may include it |
| Clear on uninstall | Yes | Yes (but Keychain data stays — not AsyncStorage) |
| API | Same JS API | Same JS API |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install @react-native-async-storage/async-storage   (SDK-compatible version)
import AsyncStorage from '@react-native-async-storage/async-storage'; // Expo Go me bhi chalta hai
await AsyncStorage.setItem('theme', 'dark');                          // seedha use
```
CLI way:
```jsx
// npm i @react-native-async-storage/async-storage && cd ios && pod install
import AsyncStorage from '@react-native-async-storage/async-storage'; // autolinking karta hai
await AsyncStorage.setItem('theme', 'dark');                          // same API
// Android size badhani ho: android/gradle.properties me AsyncStorage_db_size_in_MB=20
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Object seedha save karna: `setItem('user', {a:1})` — यह "[object Object]" बन जाता है / error देता है।
✅ Correct: `setItem('user', JSON.stringify(user))` और पढ़ते समय `JSON.parse`.

❌ Mistake 2: `await` भूल जाना और `getItem` का Promise render करना।
✅ Correct: `useEffect` में `await`/`.then` से पढ़ें, फिर state में रखें।

❌ Mistake 3: Token / password / OTP AsyncStorage में रखना (unencrypted)।
✅ Correct: `expo-secure-store` (Keychain / Keystore) use करें।

❌ Mistake 4: `clear()` से पूरा storage साफ़ कर देना (दूसरे libraries का data भी जाता है)।
✅ Correct: `multiRemove([...अपनी keys])`.

❌ Mistake 5: बड़ा data (images, 1000s items) और बार-बार तेज़ writes।
✅ Correct: File system / SQLite / MMKV use करें।

---

## 🧠 Tricky Interview Question
```jsx
await AsyncStorage.setItem('count', 5);
const v = await AsyncStorage.getItem('count');
console.log(typeof v, v + 1);
```
What is printed?

Answer: Values must be strings. In current versions passing a number can throw a type/warning error (older ones silently converted). If it saved "5", `typeof v` is `"string"` and `v + 1` is `"51"` (string concatenation), not 6. Correct way: `setItem('count', String(5))` and `Number(v) + 1`.

हिंदी: Value हमेशा string होती है, इसलिए पढ़ने के बाद `"5" + 1 = "51"` आता है। `Number()` से बदलकर जोड़ें।

---

## ⚫ Interview Questions + Answers
Q1: Is AsyncStorage synchronous?
A1: No, it is asynchronous (Promise-based) and does not block the JS thread. MMKV is the synchronous alternative.

Q2: Is AsyncStorage secure for tokens?
A2: No. It is unencrypted plain storage. Use `expo-secure-store` or `react-native-keychain`.

Q3: How do you store an object or array?
A3: `JSON.stringify` before `setItem`, `JSON.parse` after `getItem`; wrap in try/catch.

Q4: What does `getItem` return when the key does not exist?
A4: `null` (no error thrown).

Q5: What is the difference between `mergeItem` and `setItem`?
A5: `setItem` replaces the whole value; `mergeItem` deep-merges a JSON object into the existing stored JSON.

Q6 (bonus): Why do apps hydrate state from AsyncStorage?
A6: To restore user preferences and cached data on launch (e.g. Zustand `persist` middleware uses AsyncStorage as its storage).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Small non-sensitive data: theme, language, onboarding flag, drafts
- Simple offline cache of a few KBs
- Persisting Zustand / Redux state

❌ Avoid when:
- Secrets and tokens (use SecureStore)
- Large or frequently written data (use MMKV / SQLite)
- Relational/queryable data (use SQLite / WatermelonDB)

---

## 📊 Visual Diagram
```
 Component ──setItem(key, JSON string)──▶ AsyncStorage (JS API)
                                              │
                                  Native module (bridge / JSI)
                                              │
                      ┌───────────────────────┴──────────────────────┐
                      ▼                                              ▼
               Android: SQLite                              iOS: files on disk
                      └───────────── disk (survives restart) ────────┘
 Component ◀──getItem(key) → string | null──
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Key-value store | Data saved as key → value pairs | key से value मिलने वाला store |
| Persistent | Survives app restart | app बंद होने पर भी बना रहे |
| Serialize | Convert object to string | object को string बनाना |
| multiGet/multiSet | Batch read/write | एक साथ कई keys |
| Hydrate | Load saved data into state | saved डेटा state में भरना |
| Unencrypted | Not protected | बिना सुरक्षा के |

---

## ⚡ 3-Line Summary
English: AsyncStorage is an async key-value store for small string data.
Use JSON.stringify/parse for objects and never keep secrets in it.
For speed or size use MMKV; for secrets use SecureStore.

Hindi: AsyncStorage छोटा string डेटा रखने वाला async key-value store है।
Object के लिए JSON.stringify/parse करें और secrets यहाँ कभी न रखें।
तेज़ी या बड़े डेटा के लिए MMKV, secrets के लिए SecureStore।

---

## ➡️ Next Topic
**89. AsyncStorage vs MMKV** — जानें कब AsyncStorage छोड़कर तेज़ synchronous MMKV लेना चाहिए।

---
