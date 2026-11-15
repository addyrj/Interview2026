# 105. Face ID + Touch ID
# हिंदी में: Face ID + Touch ID (iOS की biometric सुविधाएँ)
# Platform: iOS ✅ (मुख्य) | Android ✅ (fingerprint/face का equivalent) | Both ✅

> Target: Expo SDK 52 (React Native 0.76) + `expo-local-authentication` (check current docs — APIs change between SDKs). **Face ID Expo Go में काम नहीं करता** (Expo Go की Info.plist में Face ID string नहीं) — development build चाहिए।
> Note: `104` में general flow है; यहाँ Face ID / Touch ID की पहचान, permissions और UI-text पर focus है।

---

## 🔵 Simple Definition (English)
**Touch ID** is Apple's fingerprint sensor (older iPhones, some iPads/Macs); **Face ID** is Apple's 3D face recognition (iPhone X and newer). In React Native you use the same API for both and check **which type** the device has to show the right label and icon.

## 🔵 सरल परिभाषा (Hindi)
**Touch ID** Apple का fingerprint sensor है (पुराने iPhone, कुछ iPad/Mac); **Face ID** Apple की 3D चेहरा पहचान है (iPhone X और नए)। React Native में दोनों के लिए एक ही API है; आप देखते हैं कि device में **कौन सा type** है ताकि सही label और icon दिखाएँ।

---

## 🔴 Problem it Solves
```
❌ "Use Fingerprint" button Face ID wale iPhone par confusing
❌ Info.plist me Face ID string na ho to iOS app crash/reject
❌ Android me Face unlock aur iOS Face ID ka behaviour alag
✅ supportedAuthenticationTypesAsync se sahi label (Face ID / Touch ID)
```

## 🔴 यह क्यों बना? (Hindi)
```
हर iPhone में एक जैसा sensor नहीं होता।
Face ID वाले फ़ोन पर "Use Fingerprint" लिखना भ्रामक है।
iOS Face ID के लिए Info.plist में कारण का text अनिवार्य है।
इसलिए type पहचानकर सही text और permission देना ज़रूरी है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → app.json plugin: ["expo-local-authentication", { "faceIDPermission": "Login ke liye Face ID" }]
Step 2 → Development build banao (eas build --profile development --platform ios)
Step 3 → supportedAuthenticationTypesAsync() -> [FINGERPRINT=1, FACIAL_RECOGNITION=2, IRIS=3]
Step 4 → Type ke hisaab se label: "Face ID" / "Touch ID" / "Biometrics"
Step 5 → authenticateAsync() -> iOS system sheet (Face ID animation ya Touch ID dialog)
Step 6 → Face ID fail 2 baar -> iOS passcode fallback; 5 fail -> passcode zaroori
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → plugin में faceIDPermission लिखें (यही Info.plist की NSFaceIDUsageDescription बनता है)।
Step 2 → Dev build पर चलाएँ, Expo Go पर नहीं।
Step 3 → supportedAuthenticationTypesAsync से type पता करें।
Step 4 → उसी के अनुसार button का text/icon दिखाएँ।
Step 5 → authenticateAsync से iOS का system sheet खुलता है।
```

---

## 🟡 Real World Example
**HDFC / ICICI / Kotak mobile apps on iPhone:** the login button says "Login with Face ID" on iPhone 15 and "Login with Touch ID" on iPhone SE. **Paytm / PhonePe:** app lock uses Face ID on iPhone and fingerprint on Android. **Apple Pay:** the same Face ID confirms payments.

## 🟡 Real Example Hindi mein
**HDFC / ICICI / Kotak apps (iPhone पर):** iPhone 15 पर बटन "Face ID से login" और iPhone SE पर "Touch ID से login" दिखता है। **Paytm / PhonePe:** iPhone पर app lock Face ID से, Android पर fingerprint से।

---

## 💻 Code Example — Basic
```jsx
// FaceTouchBasic.jsx — device type pehchano aur sahi button label dikhao
import React, { useEffect, useState } from 'react';                    // React + hooks
import { View, Text, Button } from 'react-native';                     // RN UI
import * as LocalAuthentication from 'expo-local-authentication';      // API

export default function FaceTouchBasic() {
  const [label, setLabel] = useState('Biometrics');                    // button text
  const [result, setResult] = useState('');                            // result text

  useEffect(() => {
    (async () => {
      const types = await LocalAuthentication.supportedAuthenticationTypesAsync(); // [1,2,..]
      const T = LocalAuthentication.AuthenticationType;                // enum
      if (types.includes(T.FACIAL_RECOGNITION)) setLabel('Face ID');   // face wala device
      else if (types.includes(T.FINGERPRINT)) setLabel('Touch ID');    // fingerprint wala
    })();
  }, []);                                                              // mount par ek baar

  const login = async () => {
    const res = await LocalAuthentication.authenticateAsync({
      promptMessage: `Login with ${label}`,                            // sheet ka text
      fallbackLabel: 'Use Passcode',                                   // iOS fallback button
    });
    setResult(res.success ? 'Welcome ✅' : `Failed: ${res.error}`);    // dikhao
  };

  return (
    <View style={{ padding: 40, gap: 12 }}>
      <Button title={`Login with ${label}`} onPress={login} />
      <Text>{result}</Text>
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// biometricLabel.js + LoginButton.jsx — platform-aware label, error mapping, double-tap guard
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Platform, Pressable, Text, Alert, Linking } from 'react-native';
import * as LocalAuthentication from 'expo-local-authentication';

// Pure helper: types array -> user ko dikhne wala naam
export function labelFor(types, os = Platform.OS) {
  const T = LocalAuthentication.AuthenticationType;
  if (types.includes(T.FACIAL_RECOGNITION)) return os === 'ios' ? 'Face ID' : 'Face Unlock';
  if (types.includes(T.FINGERPRINT)) return os === 'ios' ? 'Touch ID' : 'Fingerprint';
  if (types.includes(T.IRIS)) return 'Iris';
  return 'Passcode';                                                   // koi biometric nahi
}

// Error code -> friendly message
export function messageFor(error) {
  switch (error) {
    case 'user_cancel': return null;                                   // chup raho
    case 'user_fallback': return 'Passcode se login karo';
    case 'lockout': return 'Bahut galat koshish. Passcode se unlock karo.';
    case 'not_enrolled': return 'Settings me Face ID / Touch ID set karo.';
    case 'authentication_failed': return 'Pehchaan nahi hui, dobara try karo.';
    default: return 'Verification fail hua.';
  }
}

export default function LoginButton({ onSuccess }) {
  const [label, setLabel] = useState('Passcode');
  const busy = useRef(false);                                          // double tap guard

  useEffect(() => {
    LocalAuthentication.supportedAuthenticationTypesAsync()
      .then((t) => setLabel(labelFor(t)))
      .catch(() => setLabel('Passcode'));                              // error par safe default
  }, []);

  const press = useCallback(async () => {
    if (busy.current) return;                                          // already chal raha hai
    busy.current = true;
    try {
      const res = await LocalAuthentication.authenticateAsync({
        promptMessage: `${label} se verify karo`,
        fallbackLabel: 'Use Passcode',
      });
      if (res.success) return onSuccess?.();
      const msg = messageFor(res.error);
      if (res.error === 'not_enrolled') {
        Alert.alert('Not set up', msg, [{ text: 'Open Settings', onPress: Linking.openSettings }]);
      } else if (msg) Alert.alert('Oops', msg);
    } finally {
      busy.current = false;                                            // hamesha release
    }
  }, [label, onSuccess]);

  return (
    <Pressable onPress={press} style={{ padding: 14, backgroundColor: '#1a73e8', borderRadius: 8 }}>
      <Text style={{ color: '#fff' }}>Login with {label}</Text>
    </Pressable>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Names | Fingerprint / Face Unlock | Touch ID / Face ID |
| Info string | None needed | `NSFaceIDUsageDescription` **required** for Face ID |
| Expo Go | Works for fingerprint | Face ID **not** in Expo Go -> dev build |
| Fallback | System PIN/pattern | Device passcode (`fallbackLabel` controls button) |
| Face security | Many OEM faces are "weak" (2D) | Face ID is strong (3D) |
| Simulator | Emulator: set fingerprint via settings | Simulator: Features -> Face ID -> Enrolled / Matching Face |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// app.json plugins: [["expo-local-authentication", { "faceIDPermission": "Allow $(PRODUCT_NAME) to use Face ID." }]]
// eas build --profile development --platform ios   (Expo Go me Face ID nahi)
import * as LocalAuthentication from 'expo-local-authentication';      // same API
const types = await LocalAuthentication.supportedAuthenticationTypesAsync();
```
CLI way:
```jsx
// ios/YourApp/Info.plist: <key>NSFaceIDUsageDescription</key><string>Login ke liye Face ID</string>
// npm i react-native-biometrics ; pod install
import ReactNativeBiometrics from 'react-native-biometrics';           // alternative
const { biometryType } = await new ReactNativeBiometrics().isSensorAvailable(); // 'FaceID' | 'TouchID' | 'Biometrics'
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Face ID string (Info.plist) न देना।
✅ Correct: plugin `faceIDPermission` या `NSFaceIDUsageDescription`।

❌ Mistake 2: Expo Go में Face ID test करना।
✅ Correct: development build बनाएँ।

❌ Mistake 3: iPhone पर भी "Use Fingerprint" लिखना।
✅ Correct: type देखकर "Face ID"/"Touch ID" दिखाएँ।

❌ Mistake 4: `user_cancel` पर error popup दिखाना।
✅ Correct: cancel पर चुप रहें।

❌ Mistake 5: एक के बाद एक कई `authenticateAsync` (double tap)।
✅ Correct: busy flag से guard करें।

---

## 🧠 Tricky Interview Question
`supportedAuthenticationTypesAsync()` returns `[2]` on an iPhone, but `isEnrolledAsync()` returns `false`. What does it mean and what do you show?

Answer: `[2]` = `FACIAL_RECOGNITION`: the hardware supports Face ID, but the user has **not set up** Face ID in iOS Settings. So you must not call it expecting success; show "Set up Face ID in Settings" (with `Linking.openSettings()`) or use the passcode/password login.

हिंदी: `[2]` यानी hardware Face ID का है, पर user ने enroll नहीं किया। उसे Settings जाने को कहें या password login दें।

---

## ⚫ Interview Questions + Answers
Q1: `AuthenticationType` के values क्या हैं?
A1: `FINGERPRINT = 1`, `FACIAL_RECOGNITION = 2`, `IRIS = 3`।

Q2: Face ID की permission string क्यों चाहिए?
A2: iOS इसे privacy के लिए अनिवार्य करता है; बिना string के Face ID कभी काम नहीं करता या review में reject होता है।

Q3: Face ID और Touch ID में कौन ज़्यादा सुरक्षित?
A3: Apple दोनों को secure मानता है (Secure Enclave); Face ID की false-match दर बहुत कम, पर पसंद/उपयोग-संदर्भ पर निर्भर।

Q4: Fallback कैसे काम करता है?
A4: कुछ fail के बाद iOS device passcode माँगता है; `fallbackLabel` button का text बदलता है।

Q5: Simulator में कैसे test करें?
A5: Xcode Simulator -> Features -> Face ID -> Enrolled, फिर "Matching Face" / "Non-matching Face"।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- iPhone user के लिए app lock / payment confirm
- सही UI label चाहिए (Face ID बनाम Touch ID)
- Secure token पढ़ने से पहले gate

❌ Avoid when:
- Expo Go में परीक्षण (Face ID के लिए)
- Biometric को ही एकमात्र authentication बनाना
- Enrolled न होने पर फिर भी बार-बार prompt

---

## 📊 Visual Diagram
```
 supportedAuthenticationTypesAsync()
        │
   ┌────┴───────────┬────────────────┐
 [2] FACE        [1] FINGERPRINT   []  none
   │                 │                │
 "Face ID"       "Touch ID"      "Passcode"
   └─────────┬───────┘                │
        isEnrolledAsync()             │
             │ true                   │
   authenticateAsync() ─▶ iOS sheet   └─▶ password login
             │
   success / error (user_cancel, lockout, user_fallback)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Face ID | Apple 3D face recognition | Apple की चेहरा पहचान |
| Touch ID | Apple fingerprint | Apple का fingerprint |
| Secure Enclave | Apple's secure chip | Apple का सुरक्षित chip |
| NSFaceIDUsageDescription | iOS reason string | Face ID के कारण का text |
| AuthenticationType | Enum of biometric types | biometric प्रकारों की सूची |
| Passcode | Device PIN | फ़ोन का PIN |

---

## ⚡ 3-Line Summary
English: Face ID and Touch ID use one API; detect the type to show the right label.
Face ID needs the NSFaceIDUsageDescription string and a development build, not Expo Go.
Handle not-enrolled, cancel and lockout with different messages.

Hindi: Face ID और Touch ID का API एक ही है; सही label के लिए type पहचानें।
Face ID के लिए NSFaceIDUsageDescription और development build चाहिए, Expo Go नहीं।
Not-enrolled, cancel और lockout के लिए अलग संदेश दिखाएँ।

---

## ➡️ Next Topic
**109. Background Tasks** — app बंद या background में हो तब भी छोटे काम (sync) चलाना।

---
