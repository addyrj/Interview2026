# 112. Clipboard API
# हिंदी में: Clipboard API (copy / paste)
# Platform: Android ✅ | iOS ✅ | Both ✅ (Web ✅ with browser permission)

> Target: Expo SDK 52 (React Native 0.76) + `expo-clipboard` (check current docs — APIs change between SDKs). **Note:** React Native core का `Clipboard` हटा दिया गया है; अब `expo-clipboard` या `@react-native-clipboard/clipboard` use करें। Expo Go में चलता है।

---

## 🔵 Simple Definition (English)
The **Clipboard API** lets your app **copy** text to the system clipboard and **read** (paste) what is currently copied. With `expo-clipboard` you use `setStringAsync`, `getStringAsync` and `hasStringAsync`.

## 🔵 सरल परिभाषा (Hindi)
**Clipboard API** से app text को system clipboard में **copy** कर सकता है और जो अभी copy है उसे **पढ़** (paste) सकता है। `expo-clipboard` में `setStringAsync`, `getStringAsync` और `hasStringAsync` इस्तेमाल होते हैं।

---

## 🔴 Problem it Solves
```
❌ User referral code / UPI ID / OTP haath se type kare
❌ Link share karne ke liye user ko text select karna pade
✅ "Copy" button ek tap me
✅ Paste button se code auto-fill
```

## 🔴 यह क्यों बना? (Hindi)
```
User को referral code, UPI ID या OTP हाथ से टाइप करना पड़ता है।
Text select करके copy करना कठिन और ग़लती-प्रवण है।
Clipboard API से "Copy" और "Paste" एक tap में हो जाते हैं।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install expo-clipboard
Step 2 → import * as Clipboard from 'expo-clipboard'
Step 3 → Copy: await Clipboard.setStringAsync('REF1234')
Step 4 → Paste: const text = await Clipboard.getStringAsync()
Step 5 → Check: await Clipboard.hasStringAsync() (kya kuch copied hai?)
Step 6 → Feedback: "Copied!" toast/text 1-2 sec ke liye
Step 7 → (Optional) addClipboardListener se clipboard change sunna
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Copy के लिए setStringAsync(text)।
Step 2 → Paste के लिए getStringAsync() जो string लौटाता है।
Step 3 → User को "Copied!" जैसा feedback ज़रूर दिखाएँ।
Step 4 → Paste सिर्फ़ user की क्रिया (button tap) पर पढ़ें, चुपके से नहीं।
```

---

## 🟡 Real World Example
**Zomato / Swiggy:** "Copy coupon code" button on offers. **Paytm / PhonePe:** copy UPI ID or transaction ID. **Amazon / Flipkart:** tap to copy tracking ID or order ID. **Referral screens:** "Copy referral link" and share.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy:** Offers पर "Copy coupon code" बटन। **Paytm / PhonePe:** UPI ID या transaction ID copy। **Amazon / Flipkart:** tracking ID tap करके copy। **Referral screen:** "Referral link copy करें"।

---

## 💻 Code Example — Basic
```jsx
// ClipBasic.jsx — coupon copy + paste
import React, { useState } from 'react';                               // React + state
import { View, Text, Button, TextInput } from 'react-native';          // RN UI
import * as Clipboard from 'expo-clipboard';                           // clipboard API

export default function ClipBasic() {
  const [pasted, setPasted] = useState('');                            // paste ka text
  const [copied, setCopied] = useState(false);                         // "Copied!" flag

  const copy = async () => {
    await Clipboard.setStringAsync('SWIGGY50');                        // clipboard me daalo
    setCopied(true);                                                   // feedback on
    setTimeout(() => setCopied(false), 1500);                          // 1.5s baad off
  };

  const paste = async () => {
    const text = await Clipboard.getStringAsync();                     // clipboard padho
    setPasted(text);                                                   // input me dikhao
  };

  return (
    <View style={{ padding: 40, gap: 12 }}>
      <Text>Code: SWIGGY50</Text>
      <Button title={copied ? 'Copied ✅' : 'Copy'} onPress={copy} />
      <Button title="Paste" onPress={paste} />
      <TextInput value={pasted} onChangeText={setPasted} style={{ borderWidth: 1, padding: 8 }} />
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// useClipboard.js — copy with feedback + safe paste + OTP extractor + auto-clear
import { useCallback, useEffect, useRef, useState } from 'react';
import { Platform, ToastAndroid } from 'react-native';
import * as Clipboard from 'expo-clipboard';

// Pure helper: text me se 6 digit OTP nikalo
export function extractOtp(text, length = 6) {
  if (!text) return null;                                              // khaali
  const m = String(text).match(new RegExp(`\\b\\d{${length}}\\b`));    // exact N digit
  return m ? m[0] : null;                                              // mila ya null
}

export function useClipboard() {
  const [copied, setCopied] = useState(false);                         // UI feedback
  const timer = useRef(null);                                          // timeout id

  useEffect(() => () => clearTimeout(timer.current), []);              // unmount par timer saaf

  const copy = useCallback(async (text, { sensitive = false } = {}) => {
    try {
      await Clipboard.setStringAsync(String(text));                    // copy
      setCopied(true);
      if (Platform.OS === 'android' && Platform.Version < 33) {        // Android 13+ system khud dikhata hai
        ToastAndroid.show('Copied', ToastAndroid.SHORT);               // chhota toast
      }
      clearTimeout(timer.current);
      timer.current = setTimeout(() => setCopied(false), 1500);        // flag reset
      if (sensitive) {                                                 // password/OTP: kuch der baad clipboard saaf
        setTimeout(() => Clipboard.setStringAsync(''), 30000);         // 30 sec baad khaali (best effort)
      }
      return true;
    } catch (e) {
      console.warn('copy failed', e);                                  // error handle
      return false;
    }
  }, []);

  const pasteOtp = useCallback(async () => {                           // user ke tap par hi
    if (!(await Clipboard.hasStringAsync())) return null;              // kuch copied nahi
    return extractOtp(await Clipboard.getStringAsync());               // OTP nikalo
  }, []);

  return { copied, copy, pasteOtp };
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Copy feedback | Android 13+ shows system "Copied" preview; older: show own toast | iOS shows nothing on copy — show your own feedback |
| Paste notice | Android 12+ shows toast "app pasted from clipboard" when app reads it | iOS 14+ shows "pasted from..." banner |
| Background read | Blocked on Android 10+ (app must be focused) | Allowed only when app active; banner appears |
| Sensitive flag | `EXTRA_IS_SENSITIVE` hides preview (Android 13+) | Not available via expo-clipboard |
| `hasStringAsync` | Does not trigger paste notice | Avoids paste banner on iOS 14+ (use before `getStringAsync`) |
| Universal Clipboard | N/A | Syncs across Apple devices (privacy note) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install expo-clipboard
import * as Clipboard from 'expo-clipboard';                           // Expo Go me chalta hai
await Clipboard.setStringAsync('hello');                               // copy
const s = await Clipboard.getStringAsync();                            // paste
```
CLI way:
```jsx
// npm i @react-native-clipboard/clipboard && cd ios && pod install
import Clipboard from '@react-native-clipboard/clipboard';             // community library
Clipboard.setString('hello');                                          // copy (sync)
const s = await Clipboard.getString();                                 // paste (async)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: पुराना `import { Clipboard } from 'react-native'` use करना (हटाया जा चुका है)।
✅ Correct: `expo-clipboard` या `@react-native-clipboard/clipboard`।

❌ Mistake 2: `await` भूलना — `getStringAsync()` Promise लौटाता है।
✅ Correct: `const t = await Clipboard.getStringAsync()`।

❌ Mistake 3: App खुलते ही चुपचाप clipboard पढ़ना (privacy, OS banner/toast)।
✅ Correct: user के "Paste" tap पर पढ़ें।

❌ Mistake 4: Copy का कोई feedback न देना।
✅ Correct: "Copied!" text/toast; iOS पर ख़ासकर ज़रूरी।

❌ Mistake 5: Password/OTP हमेशा clipboard में छोड़ देना।
✅ Correct: संवेदनशील डेटा न रखें या कुछ देर बाद साफ़ करें, या sensitive flag समर्थन जाँचें।

---

## 🧠 Tricky Interview Question
```jsx
Clipboard.setStringAsync('A');
const t = await Clipboard.getStringAsync();
console.log(t);
```
Is `t` guaranteed to be `'A'`?

Answer: Not guaranteed. `setStringAsync` returns a Promise and was **not awaited**, so `getStringAsync` may run before the write finishes and return the old clipboard value. Use `await Clipboard.setStringAsync('A')` first. (Also, clipboard content can be changed by other apps at any time.)

हिंदी: `setStringAsync` को await नहीं किया, इसलिए `get` पुरानी value दे सकता है। पहले `await` करें।

---

## ⚫ Interview Questions + Answers
Q1: React Native का built-in `Clipboard` कहाँ गया?
A1: Core से हटा दिया गया (lean core); अब `expo-clipboard` या `@react-native-clipboard/clipboard`।

Q2: Clipboard में image copy हो सकती है?
A2: हाँ, `expo-clipboard` में `setImageAsync` / `getImageAsync` (base64) जैसे APIs हैं; platform सीमाएँ देखें।

Q3: Paste से पहले `hasStringAsync` क्यों?
A3: Clipboard खाली है या नहीं पता चलता है और iOS 14+ में paste-banner से बचाव होता है।

Q4: Clipboard में sensitive डेटा क्यों ख़तरनाक?
A4: कोई भी foreground app (या Universal Clipboard से दूसरे Apple devices) उसे पढ़ सकता है।

Q5: Clipboard बदलाव कैसे सुनें?
A5: `Clipboard.addClipboardListener(cb)` — subscription पर `.remove()`; (iOS/Android पर सीमाएँ, docs देखें)।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Coupon / referral / UPI ID / order ID copy
- User-initiated paste (OTP, link)
- "Copy link" share flows

❌ Avoid when:
- Passwords/secrets store करना
- बिना user action के clipboard monitor करना
- Large data transfer (file/shared storage use करें)

---

## 📊 Visual Diagram
```
  [Copy button] ── setStringAsync(text) ──▶ System Clipboard ◀── other apps
                                                │
  [Paste button] ◀── getStringAsync() ──────────┘
        │
   hasStringAsync() first (avoid empty / iOS banner)
        │
   "Copied!" feedback (iOS needs own, Android 13+ shows system preview)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Clipboard | Temporary copy buffer | copy का अस्थायी स्थान |
| setStringAsync | Copy text | text copy करना |
| getStringAsync | Read copied text | copy किया text पढ़ना |
| Universal Clipboard | Apple cross-device clipboard | Apple devices के बीच clipboard |
| Paste banner | iOS privacy notice | iOS की privacy सूचना |
| Sensitive data | Secrets | संवेदनशील डेटा |

---

## ⚡ 3-Line Summary
English: expo-clipboard copies and reads text with setStringAsync and getStringAsync.
Always await, give feedback and read only on a user tap.
Never keep secrets in the clipboard.

Hindi: expo-clipboard में setStringAsync/getStringAsync से text copy और paste होता है।
हमेशा await करें, feedback दें और सिर्फ़ user के tap पर पढ़ें।
Secrets को clipboard में कभी न रखें।

---

## ➡️ Next Topic
**113. Share API** — system share sheet से text/link दूसरे apps में भेजना (copy का अगला कदम)।

---
