# 104. Biometric Authentication
# हिंदी में: Biometric Authentication (fingerprint / चेहरे से पहचान)
# Platform: Android ✅ | iOS ✅ | Both ✅ (real device चाहिए)

> Target: Expo SDK 52 (React Native 0.76) + `expo-local-authentication` + `expo-secure-store` (check current docs — APIs change between SDKs). iOS पर Face ID के लिए Expo Go में दिक्कत होती है — development build use करें (देखें Topic 105).

---

## 🔵 Simple Definition (English)
**Biometric authentication** lets the user prove who they are with a fingerprint or face instead of typing a password. `expo-local-authentication` shows the system prompt and tells you **success or failure** — the biometric data itself never reaches your app.

## 🔵 सरल परिभाषा (Hindi)
**Biometric authentication** में user password की जगह fingerprint या चेहरे से अपनी पहचान साबित करता है। `expo-local-authentication` system का prompt दिखाता है और सिर्फ़ **success या failure** बताता है — biometric डेटा app तक कभी नहीं पहुँचता।

---

## 🔴 Problem it Solves
```
❌ Baar-baar password / PIN type karna (slow, insecure)
❌ App khulte hi koi bhi paisa dekh/bhej sakta hai
✅ Ek touch / face se secure unlock
✅ Native OS ka prompt: hamesha trusted UI
```

## 🔴 यह क्यों बना? (Hindi)
```
बार-बार password डालना धीमा और असुरक्षित है।
फ़ोन किसी और के हाथ लगे तो banking app खुल सकता है।
OS का biometric prompt तेज़ और भरोसेमंद है, और डेटा OS के अंदर ही रहता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install expo-local-authentication expo-secure-store
Step 2 → hasHardwareAsync() -> sensor hai?
Step 3 → isEnrolledAsync() -> user ne fingerprint/face set kiya hai?
Step 4 → authenticateAsync({ promptMessage, fallbackLabel, cancelLabel })
Step 5 → result.success true/false; false me result.error ('user_cancel', 'lockout', ...)
Step 6 → Success par app unlock ya SecureStore se token padho
Step 7 → Fail par PIN fallback / retry / password login
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले जाँचें: hardware है? और user ने biometric enroll किया है?
Step 2 → authenticateAsync system prompt खोलता है।
Step 3 → नतीजा { success, error } आता है।
Step 4 → success -> unlock; failure -> PIN/password का रास्ता दें।
```

---

## 🟡 Real World Example
**Paytm / PhonePe / Google Pay:** app lock — opening the app or approving a payment asks for fingerprint/face. **HDFC / SBI YONO:** biometric login instead of MPIN. **Groww / Zerodha Kite:** app lock with fingerprint/face before showing your portfolio.

## 🟡 Real Example Hindi mein
**Paytm / PhonePe / Google Pay:** App lock — app खोलने या payment approve करने पर fingerprint/face माँगता है। **HDFC / SBI YONO:** MPIN की जगह biometric login। यह मुख्य रूप से पैसे/privacy वाले apps में इस्तेमाल होता है।

---

## 💻 Code Example — Basic
```jsx
// BioBasic.jsx — ek button se fingerprint/face check
import React, { useState } from 'react';                               // React + state
import { View, Text, Button } from 'react-native';                     // RN UI
import * as LocalAuthentication from 'expo-local-authentication';      // biometric API

export default function BioBasic() {
  const [msg, setMsg] = useState('Locked 🔒');                         // UI message

  const unlock = async () => {
    const hasHw = await LocalAuthentication.hasHardwareAsync();        // sensor hai?
    if (!hasHw) return setMsg('Is device me biometric nahi hai');      // nahi hai
    const enrolled = await LocalAuthentication.isEnrolledAsync();      // user ne set kiya?
    if (!enrolled) return setMsg('Settings me fingerprint/face set karo'); // enroll nahi
    const res = await LocalAuthentication.authenticateAsync({          // system prompt
      promptMessage: 'App unlock karo',                                // prompt text
      cancelLabel: 'Cancel',                                           // cancel button text
    });
    setMsg(res.success ? 'Unlocked ✅' : `Failed: ${res.error}`);      // result dikhao
  };

  return (
    <View style={{ padding: 40, gap: 12 }}>
      <Text>{msg}</Text>
      <Button title="Unlock" onPress={unlock} />
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// useBiometricGate.js — fallback, lockout handling, SecureStore token
import { useCallback, useState } from 'react';
import { Platform } from 'react-native';
import * as LocalAuthentication from 'expo-local-authentication';
import * as SecureStore from 'expo-secure-store';

export async function biometricStatus() {
  const hardware = await LocalAuthentication.hasHardwareAsync();       // sensor
  const enrolled = await LocalAuthentication.isEnrolledAsync();        // enrolled
  const level = await LocalAuthentication.getEnrolledLevelAsync();     // NONE / SECRET (PIN) / BIOMETRIC_WEAK / BIOMETRIC_STRONG
  return { hardware, enrolled, level };
}

export function useBiometricGate() {
  const [error, setError] = useState(null);                            // last error

  const authenticate = useCallback(async (reason = 'Payment confirm karo') => {
    setError(null);
    try {
      const { hardware, enrolled } = await biometricStatus();
      if (!hardware || !enrolled) {
        setError('not_available');                                     // PIN/password flow par bhejo
        return false;
      }
      const res = await LocalAuthentication.authenticateAsync({
        promptMessage: reason,                                         // prompt
        fallbackLabel: 'Use PIN',                                      // iOS: passcode button label
        cancelLabel: 'Cancel',                                         // cancel text
        disableDeviceFallback: false,                                  // true => sirf biometric (PIN band)
      });
      if (!res.success) {
        // res.error examples: 'user_cancel', 'user_fallback', 'lockout', 'authentication_failed', 'not_enrolled'
        setError(res.error);
        return false;
      }
      return true;                                                     // verified
    } catch (e) {
      setError(String(e));                                             // unexpected
      return false;
    }
  }, []);

  // Biometric ke baad hi token padho (secret ko SecureStore me rakho)
  const readToken = useCallback(async () => {
    if (!(await authenticate('Login ke liye verify karo'))) return null;
    return SecureStore.getItemAsync('auth_token');                     // Keychain / Keystore
  }, [authenticate]);

  return { authenticate, readToken, error, isIOS: Platform.OS === 'ios' };
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Types | Fingerprint, Face (device-dependent), Iris | Touch ID, Face ID |
| Permission | `USE_BIOMETRIC` (Expo plugin adds) | `NSFaceIDUsageDescription` (Face ID) |
| Fallback label | `fallbackLabel` ignored; "Use PIN" system provided | `fallbackLabel` customizable (shows after failure) |
| Biometric strength | Weak vs Strong classes (`getEnrolledLevelAsync`) | Single level |
| Cancel button | `cancelLabel` | `cancelLabel` |
| Lockout | After ~5 fails, ~30s lockout; more fails -> permanent until PIN | Passcode required after 5 fails |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-local-authentication ; plugin: ["expo-local-authentication", { "faceIDPermission": "Face ID se unlock" }]
import * as LocalAuthentication from 'expo-local-authentication';   // JS only
const r = await LocalAuthentication.authenticateAsync({ promptMessage: 'Unlock' });
```
CLI way:
```jsx
// npm i react-native-biometrics ; cd ios && pod install ; Info.plist: NSFaceIDUsageDescription
import ReactNativeBiometrics from 'react-native-biometrics';        // popular CLI library
const rnBiometrics = new ReactNativeBiometrics();                    // instance
const { success } = await rnBiometrics.simplePrompt({ promptMessage: 'Unlock' }); // prompt
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `hasHardwareAsync` / `isEnrolledAsync` जाँचे बिना सीधे authenticate।
✅ Correct: पहले दोनों जाँचें और fallback दें।

❌ Mistake 2: "biometric success" को ही server-side proof मान लेना।
✅ Correct: यह सिर्फ़ local gate है; असली secret `SecureStore` में रखें और server token verify करे।

❌ Mistake 3: Face ID की usage string न देना (iOS)।
✅ Correct: `faceIDPermission` plugin option।

❌ Mistake 4: Failure पर user को अटका देना।
✅ Correct: PIN/password fallback और साफ़ error message।

❌ Mistake 5: Emulator पर test करके निष्कर्ष निकालना।
✅ Correct: Emulator में biometric enroll करके या real device पर।

---

## 🧠 Tricky Interview Question
`authenticateAsync` returns `{ success: false, error: 'user_cancel' }`. Should you show "Wrong fingerprint"?

Answer: No. `user_cancel` means the user dismissed the prompt; a wrong fingerprint is `authentication_failed` (usually the OS retries inside the prompt). Cancel, lockout (`lockout`), not enrolled (`not_enrolled`) and fallback (`user_fallback`) each need different UX — e.g. show PIN login for `user_fallback`/`lockout`, do nothing for `user_cancel`.

हिंदी: `user_cancel` का मतलब user ने prompt बंद किया, गलत fingerprint नहीं। हर error code का अलग UX होना चाहिए।

---

## ⚫ Interview Questions + Answers
Q1: Biometric डेटा app को मिलता है?
A1: नहीं। OS सिर्फ़ success/failure बताता है; template secure hardware में रहता है।

Q2: Biometric से token कैसे सुरक्षित रखें?
A2: Token `expo-secure-store` में रखें; पढ़ने से पहले biometric gate लगाएँ (या `requireAuthentication` option, platform support जाँचें)।

Q3: Fallback कैसे दें?
A3: `disableDeviceFallback: false` (device PIN), या app का अपना PIN/password screen।

Q4: Enrolled न हो तो?
A4: `isEnrolledAsync()` false -> user को Settings में biometric जोड़ने को कहें या PIN login दें।

Q5: Android में weak vs strong biometric?
A5: `getEnrolledLevelAsync()` से पता चलता है; sensitive कामों के लिए strong चाहिए।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Banking / wallet app lock, payment confirmation
- Sensitive screen (health records) खोलना
- Re-auth पुराने session पर

❌ Avoid when:
- Biometric को अकेला server authentication बनाना
- Device में biometric नहीं / enroll नहीं (fallback ज़रूर रखें)
- Low-risk public content

---

## 📊 Visual Diagram
```
 hasHardwareAsync() ──false──▶ PIN / password login
        │ true
 isEnrolledAsync()  ──false──▶ "Settings me enroll karo"
        │ true
 authenticateAsync() ─▶ OS Biometric Prompt (Secure hardware)
        │
  success ──▶ unlock / SecureStore.getItemAsync(token)
  error   ──▶ user_cancel | lockout | user_fallback ─▶ matching UX
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Biometric | Body-based ID | शरीर आधारित पहचान |
| Enrolled | Biometric registered | पंजीकृत |
| Fallback | Alternate method (PIN) | विकल्प (PIN) |
| Lockout | Temporarily blocked | अस्थायी रोक |
| Secure hardware | Protected chip | सुरक्षित chip |
| SecureStore | Encrypted key-value | encrypted storage |

---

## ⚡ 3-Line Summary
English: expo-local-authentication shows the OS biometric prompt and returns only success or error.
Check hardware and enrollment first and always offer a fallback.
Keep secrets in SecureStore, not in plain storage.

Hindi: expo-local-authentication OS का biometric prompt दिखाकर सिर्फ़ success या error देता है।
पहले hardware और enrollment जाँचें, और हमेशा fallback दें।
Secrets SecureStore में रखें, साधारण storage में नहीं।

---

## ➡️ Next Topic
**105. Face ID + Touch ID** — iOS की इन दो सुविधाओं की बारीकियाँ, permissions और types पहचानना।

---
