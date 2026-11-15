# 54. Platform Specific Files (.ios.js .android.js)
# हिंदी में: Platform के अनुसार अलग Files
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs)। Metro bundler का built-in feature, `.native.js` भी।

---

## 🔵 Simple Definition (English)
Metro picks files by platform extension. If you create `Button.ios.js` and `Button.android.js`, then `import Button from './Button'` automatically loads the right one. There is also `.native.js` (Android + iOS together, not web).

## 🔵 सरल परिभाषा (Hindi)
Metro file के extension से platform चुनता है। अगर आप `Button.ios.js` और `Button.android.js` बनाते हो, तो `import Button from './Button'` अपने आप सही file load करता है। `.native.js` भी है (Android + iOS दोनों, web नहीं)।

---

## 🔴 Problem it Solves
```
❌ Component में अलग-अलग OS के लिए बहुत सारे if (Platform.OS === ...) भर जाना
❌ iOS-only native library का import Android पर crash करना
❌ दोनों OS का logic एक file में उलझ जाना
```

## 🔴 यह क्यों बना? (Hindi)
```
जब दोनों OS का code काफ़ी अलग हो, तब अलग files साफ़-सुथरी रहती हैं
और import statement वही रहता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → दो files बनाओ:  Picker.ios.js  और  Picker.android.js
Step 2 → कहीं भी लिखो:  import Picker from './Picker';   (extension नहीं)
Step 3 → Metro bundling के समय platform देखता है
Step 4 → iOS बनाते समय Picker.ios.js, Android में Picker.android.js चुनता है
Step 5 → अगर platform वाली file नहीं मिली → Picker.native.js → फिर Picker.js
Step 6 → दूसरी platform की file bundle में शामिल ही नहीं होती
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Picker.ios.js और Picker.android.js बनाओ
Step 2 → import Picker from './Picker';  (extension मत लिखो)
Step 3 → Metro bundling पर platform देखता है
Step 4 → सही platform की file चुनता है
Step 5 → न मिले तो .native.js फिर .js
Step 6 → दूसरी platform की file bundle में नहीं जाती
```

---

## 🟡 Real World Example
**Paytm/PhonePe** जैसी apps में biometric या payment sheet का UI iOS में अलग (Face ID sheet) और Android में अलग (BiometricPrompt) हो सकता है। **WhatsApp**-जैसी apps में date picker का अलग implementation दोनों OS के लिए।

## 🟡 Real Example Hindi mein
Date picker iOS पर inline wheel और Android पर dialog बनकर आता है। इसलिए `DatePicker.ios.js` और `DatePicker.android.js` बनाकर बाकी app में सिर्फ `import DatePicker` लिखते हैं।

---

## 💻 Code Example — Basic
```jsx
// फ़ाइल संरचना:
//   components/Greeting.ios.js
//   components/Greeting.android.js
//   App.js

// ---------- components/Greeting.ios.js ----------
import React from 'react';                                      // React
import { Text } from 'react-native';                            // core
export default function Greeting() {
  return <Text>Hello from iOS </Text>;                          // iOS का संस्करण
}

// ---------- components/Greeting.android.js ----------
// (अलग फ़ाइल में रखो — यहाँ दिखाने के लिए एक साथ लिखा है)
// import React from 'react';
// import { Text } from 'react-native';
// export default function Greeting() { return <Text>Hello from Android</Text>; }

// ---------- App.js ----------
// import Greeting from './components/Greeting';   // extension नहीं
// export default function App() { return <Greeting />; }
```

## 💻 Code Example — Advanced
```jsx
// Advanced: एक ही API (hook) के दो implementations + shared types/logic अलग रखना
// फ़ाइलें:
//   hooks/useBiometric.ts          ← shared type/export (web/default fallback)
//   hooks/useBiometric.ios.ts      ← iOS (Face ID/Touch ID)
//   hooks/useBiometric.android.ts  ← Android (BiometricPrompt)
// Install: npx expo install expo-local-authentication

// ---------- hooks/useBiometric.ios.ts ----------
import * as LocalAuthentication from 'expo-local-authentication'; // native module

export async function authenticate(): Promise<boolean> {
  try {
    const hasHw = await LocalAuthentication.hasHardwareAsync();  // hardware?
    if (!hasHw) return false;                                    // नहीं तो false
    const res = await LocalAuthentication.authenticateAsync({
      promptMessage: 'Face ID से पुष्टि करो',                      // iOS का message
      fallbackLabel: 'Passcode इस्तेमाल करो',                     // iOS-only label
    });
    return res.success;                                          // सफल?
  } catch {
    return false;                                                // error → false
  }
}

// ---------- hooks/useBiometric.android.ts ----------
// import * as LocalAuthentication from 'expo-local-authentication';
// export async function authenticate(): Promise<boolean> {
//   const res = await LocalAuthentication.authenticateAsync({
//     promptMessage: 'Fingerprint से पुष्टि करो',
//     cancelLabel: 'रद्द करो',                                    // Android का label
//   });
//   return res.success;
// }

// ---------- कहीं भी इस्तेमाल ----------
// import { authenticate } from './hooks/useBiometric';   // सही file अपने आप
// const ok = await authenticate();
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Extension | `.android.js` / `.android.tsx` | `.ios.js` / `.ios.tsx` |
| Shared fallback | `.native.js` या `.js` | `.native.js` या `.js` |
| Bundle में | सिर्फ android वाली file | सिर्फ ios वाली file |
| Native-only libs | Android फ़ाइल में import करो | iOS फ़ाइल में import करो |
| Web | `.web.js` अलग (react-native-web) | `.web.js` अलग |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo (Metro) में यह बिना config चलता है
// components/Header.ios.js + components/Header.android.js
import Header from './components/Header';
```
CLI way:
```jsx
// CLI में भी वही Metro rule; TypeScript में type के लिए
// Header.d.ts या Header.ts (shared) रखना पड़ सकता है
import Header from './components/Header';
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Import में extension लिखना
```jsx
import Picker from './Picker.ios';   // ❌ हमेशा iOS वाली file
```
✅ Correct: `import Picker from './Picker';`

❌ Mistake 2: सिर्फ `.ios.js` बनाना, Android के लिए file भूल जाना
✅ Correct: Android के लिए `.android.js` या fallback `.js`/`.native.js` भी रखो, वरना build error "Unable to resolve module"।

❌ Mistake 3: TypeScript में shared type file न बनाना (editor error)
✅ Correct: `Picker.ts` / `Picker.d.ts` में common type/export रखो।

---

## 🧠 Tricky Interview Question
```
Button.js
Button.ios.js
```
**Q: Android पर `import Button from './Button'` कौन-सी file लोड करेगा?**

Answer: `Button.js`। Android में `.android.js` नहीं है और `.native.js` भी नहीं, तो Metro साधारण `Button.js` पर fallback करता है। iOS पर `Button.ios.js` जीतेगा।

---

## ⚫ Interview Questions + Answers
Q1: Resolution order क्या है?
A1: platform (`.ios`/`.android`) → `.native` → default (`.js`)।

Q2: `.native.js` कब?
A2: जब Android + iOS का code एक जैसा हो पर web का अलग।

Q3: Platform.select vs अलग files?
A3: छोटे फ़र्क के लिए select; बड़े logic/UI/imports के फ़र्क के लिए files।

Q4: Bundle size पर असर?
A4: दूसरी platform की file bundle में नहीं जाती, इसलिए बेकार code नहीं रहता।

Q5: Jest tests में कैसे?
A5: jest-expo / react-native preset `defaultPlatform` (आमतौर पर iOS) से चुनता है; ज़रूरत पर `Platform.OS` mock करो।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- OS-specific native library import
- Logic/UI बहुत अलग

❌ Avoid when:
- सिर्फ रंग/padding का फ़र्क (`Platform.select`)
- Code duplication बढ़ने का डर

---

## 📊 Visual Diagram
```
 import X from './X'
        │ Metro (platform)
  ┌─────┼──────────┐
 iOS  → X.ios.js     (नहीं मिली तो ↓)
 Android → X.android.js
         ↓
       X.native.js → X.js
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Platform extension | .ios / .android | platform extension |
| .native.js | Android+iOS साझा | native-साझा file |
| Metro | Bundler | bundler |
| Resolution | File चुनने का क्रम | खोजने का क्रम |
| Fallback | न मिले तो विकल्प | विकल्प file |

---

## ⚡ 3-Line Summary
English:
1. Metro picks `.ios.js` / `.android.js` by platform; no extension in the import.
2. Order: platform, then `.native`, then default.
3. Use for big differences; use `Platform.select` for small ones.

Hindi:
1. Metro platform से `.ios.js` / `.android.js` चुनता है; import में extension नहीं।
2. क्रम: platform, फिर `.native`, फिर default।
3. बड़े फ़र्क पर files; छोटे फ़र्क पर `Platform.select`।

---

## ➡️ Next Topic
**55. Fonts — Custom Fonts Setup** — अपना font app में जोड़ना।
