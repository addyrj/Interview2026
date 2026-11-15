# 117. Secure Storage (expo-secure-store)
# हिंदी में: Secure Storage — सुरक्षित Data Storage
# Platform: Android ✅ | iOS ✅ | Both ✅ (Web ❌)

---

**Expo SDK 52 / React Native 0.76 (check current docs — APIs change between SDKs).** Library: `expo-secure-store`। Web पर support नहीं है।

---

## 🔵 Simple Definition (English)
**expo-secure-store** saves small secrets (auth token, refresh token, PIN) in encrypted storage: the **iOS Keychain** and **Android Keystore-backed encrypted SharedPreferences**. Unlike AsyncStorage, which is plain text, the data is protected by the OS.

## 🔵 सरल परिभाषा (Hindi)
**expo-secure-store** छोटे secrets (auth token, refresh token, PIN) को encrypted storage में रखता है: **iOS Keychain** और **Android Keystore** आधारित encrypted storage। AsyncStorage plain text होता है, जबकि इसमें data OS द्वारा सुरक्षित रहता है।

---

## 🔴 Problem it Solves
```
PROBLEM:
  AsyncStorage में JWT token रखा -> rooted phone / backup से पढ़ा जा सकता है.
  Token चोरी = किसी का account hijack.

SECURE STORE:
  ✅ Encrypted at rest (Keychain / Keystore)
  ✅ Simple API: setItemAsync / getItemAsync / deleteItemAsync
  ✅ Optional biometric requirement (requireAuthentication)
  ✅ Login tokens के लिए सही जगह
```

## 🔴 यह क्यों बना? (Hindi)
AsyncStorage में सब कुछ plain text में रहता है; rooted phone या backup से token निकल सकता है। Token चोरी होने का मतलब account hijack। Secure Store OS की encrypted storage use करता है, इसलिए login tokens वहाँ रखना सही है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install expo-secure-store
Step 2 → Login के बाद SecureStore.setItemAsync('token', value)
Step 3 → OS key बनाता है (Keychain/Keystore) और value encrypt करके रखता है
Step 4 → App खुलने पर SecureStore.getItemAsync('token') से पढ़ो
Step 5 → Logout पर SecureStore.deleteItemAsync('token')
Step 6 → Value null हो तो user को login screen भेजो
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → expo-secure-store install करो
Step 2 → Login के बाद setItemAsync से token रखो
Step 3 → OS key बनाकर value encrypt करता है
Step 4 → App खुलने पर getItemAsync से पढ़ो
Step 5 → Logout पर deleteItemAsync
Step 6 → null मिले तो login screen दिखाओ
```

---

## 🟡 Real World Example
**PhonePe / Paytm / CRED** जैसे apps access token और refresh token secure storage में रखते हैं, ताकि हर बार login न करना पड़े पर token सुरक्षित रहे। **Zerodha Kite** जैसे trading apps session token ऐसे ही रखते हैं। App lock का PIN भी यहीं (hash बनाकर) रखा जाता है।

## 🟡 Real Example Hindi mein
PhonePe/CRED access और refresh token secure storage में रखते हैं ताकि user बार-बार login न करे और token सुरक्षित रहे। Zerodha जैसे apps session token भी ऐसे ही रखते हैं।

---

## 💻 Code Example — Basic
```jsx
// SecureBasic.jsx — token save / read / delete
import React, { useState } from 'react';                        // state
import { View, Text, Button } from 'react-native';              // UI
import * as SecureStore from 'expo-secure-store';               // npx expo install expo-secure-store

export default function SecureBasic() {                         // component
  const [token, setToken] = useState(null);                     // दिखाने के लिए

  const save = async () => {                                    // save
    await SecureStore.setItemAsync('authToken', 'abc123');      // key और value (दोनों string)
  };                                                            // खत्म

  const read = async () => {                                    // read
    const v = await SecureStore.getItemAsync('authToken');      // नहीं मिले तो null
    setToken(v);                                                // state में रखो
  };                                                            // खत्म

  const remove = async () => {                                  // delete
    await SecureStore.deleteItemAsync('authToken');             // हटाओ
    setToken(null);                                             // UI साफ़
  };                                                            // खत्म

  return (                                                      // UI
    <View style={{ flex: 1, justifyContent: 'center', padding: 24, gap: 10 }}>{/* container */}
      <Button title="Save" onPress={save} />{/* save */}
      <Button title="Read" onPress={read} />{/* read */}
      <Button title="Delete" onPress={remove} />{/* delete */}
      <Text>Token: {token ?? 'none'}</Text>{/* result */}
    </View>
  );                                                            // return खत्म
}                                                               // component खत्म
```

## 💻 Code Example — Advanced
```jsx
// tokenStore.js + useAuth.js — JSON session, biometric-protected key, safe wrapper
import * as SecureStore from 'expo-secure-store';               // storage
import { useEffect, useState, useCallback } from 'react';       // hooks

const KEY = 'session';                                          // key नाम (सिर्फ alphanumeric, ".", "-", "_" allowed)

// Session object (token + expiry) save करना
export async function saveSession(session) {                    // session = {access, refresh, exp}
  try {                                                         // error handling
    const json = JSON.stringify(session);                       // string बनाओ (limit: values ~2KB से छोटी रखो)
    await SecureStore.setItemAsync(KEY, json, {                 // options के साथ save
      keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY, // iOS: phone unlock हो तभी, backup/नए phone पर नहीं
    });                                                         // options खत्म
    return true;                                                // सफल
  } catch (e) {                                                 // fail
    console.warn('saveSession failed', e.message);              // log
    return false;                                               // असफल
  }                                                             // catch खत्म
}                                                               // function खत्म

// Session पढ़ना
export async function loadSession() {                           // load
  try {                                                         // error handling
    const raw = await SecureStore.getItemAsync(KEY);            // पढ़ो
    return raw ? JSON.parse(raw) : null;                        // parse या null
  } catch (e) {                                                 // corrupt / key invalid
    await SecureStore.deleteItemAsync(KEY).catch(() => {});     // खराब data हटाओ
    return null;                                                // null
  }                                                             // catch खत्म
}                                                               // function खत्म

// Sensitive item जिसे पढ़ने से पहले biometric चाहिए
export async function savePin(pinHash) {                        // PIN hash save
  await SecureStore.setItemAsync('pinHash', pinHash, {          // options
    requireAuthentication: true,                                // पढ़ते समय biometric/passcode माँगे
    authenticationPrompt: 'Unlock to continue',                 // prompt text
  });                                                           // खत्म
}                                                               // function खत्म

export function useSession() {                                  // hook
  const [session, setSession] = useState(null);                 // current session
  const [loading, setLoading] = useState(true);                 // startup loading

  useEffect(() => {                                             // app start
    loadSession().then((s) => { setSession(s); setLoading(false); }); // restore
  }, []);                                                       // एक बार

  const logout = useCallback(async () => {                      // logout
    await SecureStore.deleteItemAsync(KEY);                     // हटाओ
    setSession(null);                                           // state खाली
  }, []);                                                       // dependency नहीं

  return { session, loading, setSession, logout };              // return
}                                                               // खत्म
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Backend | Keystore-backed encrypted SharedPreferences | Keychain |
| App uninstall | Data हट जाता है | Keychain data reinstall के बाद भी बचा रह सकता है |
| Backup | Auto Backup में exclude नहीं किया तो समस्या; Expo इसे संभालता है | `keychainAccessible` से तय (`..._THIS_DEVICE_ONLY`) |
| `requireAuthentication` | Biometric/device credential | Face ID / Touch ID / passcode |
| Expo Go | काम करता है (biometric option सीमित) | काम करता है, पर `requireAuthentication` में Face ID के लिए development build चाहिए |
| Size limit | ~2048 bytes की सलाह | वही सलाह |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: सीधा expo-secure-store
import * as SecureStore from 'expo-secure-store';          // npx expo install expo-secure-store
await SecureStore.setItemAsync('token', 'abc');            // save
```
CLI way:
```jsx
// CLI: या तो expo-secure-store (Expo modules install के बाद) या react-native-keychain
import * as Keychain from 'react-native-keychain';         // npm i react-native-keychain; cd ios && pod install
await Keychain.setGenericPassword('user', 'abc');          // save
const creds = await Keychain.getGenericPassword();         // read -> { username, password } या false
await Keychain.resetGenericPassword();                     // delete
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Token AsyncStorage में रखना।
✅ Correct: Secrets के लिए SecureStore।

❌ Mistake 2: Key में space या खास अक्षर (जैसे `auth token!`)।
✅ Correct: सिर्फ अक्षर, अंक, `.`, `-`, `_`।

❌ Mistake 3: बड़ा JSON/image यहाँ रखना।
✅ Correct: छोटे secrets ही; बड़ा data SQLite/file में, बस उसकी encryption key यहाँ।

❌ Mistake 4: Logout पर delete न करना।
✅ Correct: `deleteItemAsync` हमेशा।

---

## 🧠 Tricky Interview Question
User app uninstall करके दोबारा install करता है। iOS पर पुराना token मिल गया और user logged-in दिखा। Android पर नहीं। क्यों?

Answer: iOS Keychain data app uninstall के बाद भी रह सकता है, जबकि Android पर app data के साथ हट जाता है। समाधान: पहली launch पर एक flag (AsyncStorage में) जाँचो और नहीं मिले तो Keychain के पुराने tokens साफ़ करो। साथ ही `WHEN_UNLOCKED_THIS_DEVICE_ONLY` इस्तेमाल से backup/restore का जोखिम कम होता है।

---

## ⚫ Interview Questions + Answers
Q1: SecureStore और AsyncStorage में फर्क?
A1: SecureStore encrypted (Keychain/Keystore) है और छोटे secrets के लिए; AsyncStorage plain text है और सामान्य data के लिए।

Q2: Data types?
A2: सिर्फ strings; object के लिए JSON.stringify।

Q3: Biometric से कैसे सुरक्षित करें?
A3: `requireAuthentication: true` option के साथ save।

Q4: Web पर?
A4: Support नहीं; `Platform.OS === 'web'` पर fallback (जैसे memory/localStorage) रखो।

Q5: Large data कहाँ?
A5: Encrypted SQLite/MMKV में रखो, और उसकी key SecureStore में।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- JWT/refresh token, PIN hash, API secrets (user-level)
- Biometric-protected items

❌ Avoid when:
- Theme, language जैसी सामान्य settings (AsyncStorage)
- बड़ा data / lists (SQLite)
- App में hardcode करने वाले secrets (वे वैसे भी सुरक्षित नहीं)

---

## 📊 Visual Diagram
```
 JS: setItemAsync(key, value)
         |
         v
   expo-secure-store (native)
     |               |
  Android          iOS
  Keystore key     Keychain
  encrypt+store    encrypted item
         |
   getItemAsync -> decrypt -> JS
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Keychain | iOS secure store | iOS की सुरक्षित storage |
| Keystore | Android key vault | Android का key vault |
| Encrypted at rest | Stored encrypted | Storage में encrypted |
| requireAuthentication | Ask biometric to read | पढ़ने से पहले biometric |
| keychainAccessible | iOS access rule | iOS access नियम |

---

## ⚡ 3-Line Summary
English: SecureStore keeps small secrets in Keychain/Keystore, encrypted by the OS.
Use it for tokens and PIN hashes, never for large data.
Delete on logout and remember iOS may keep data after uninstall.

Hindi: SecureStore छोटे secrets को OS की encrypted Keychain/Keystore में रखता है।
Tokens और PIN hash के लिए use करो, बड़े data के लिए नहीं।
Logout पर delete करो और याद रखो iOS पर uninstall के बाद भी data रह सकता है।

---

## ➡️ Next Topic
**118. SQLite in React Native**, अब बड़ा structured data local database में रखना सीखेंगे।
