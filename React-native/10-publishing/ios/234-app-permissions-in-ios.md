# 234. App Permissions in iOS
# हिंदी में: iOS में App Permissions
# Platform: Android ❌ (अलग model) | iOS ✅

> Expo SDK 52+ (React Native 0.76+)। Expo SDK 52 (check current docs — APIs change between SDKs). `expo-camera`, `expo-location`, `expo-notifications` की permission API और plugin option names docs से verify करें।

---

## 🔵 Simple Definition (English)
On iOS, an app must ask the user at runtime before using sensitive features like camera, location, photos, microphone or notifications. Each needs a **usage description** in Info.plist; iOS shows a system popup and remembers the answer.

## 🔵 सरल परिभाषा (Hindi)
iOS पर camera, location, photos, microphone, notifications जैसे संवेदनशील features इस्तेमाल करने से पहले app को user से runtime पर पूछना पड़ता है। हर permission के लिए Info.plist में **usage description** चाहिए; iOS system popup दिखाता है और जवाब याद रखता है।

---

## 🔴 Problem it Solves
- Apps चुपचाप user का data/camera access करते थे।
- User को नियंत्रण और पारदर्शिता चाहिए।

## 🔴 यह क्यों बना? (Hindi)
Privacy के लिए Apple permission model बना: कारण बताओ, user चुने (Allow/Don't Allow)। एक बार मना किया तो popup दोबारा नहीं आता — user को Settings में जाना पड़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Info.plist में usage description जोड़ो (app.json ios.infoPlist या plugin option)
Step 2 → App में सही मौके पर request करो (feature इस्तेमाल से ठीक पहले)
Step 3 → iOS popup दिखाता है (सिर्फ पहली बार)
Step 4 → Result: granted / denied / undetermined (limited — photos/location में)
Step 5 → Denied हो तो explain करो + Settings खोलने का बटन (Linking.openSettings())
```

## 🟢 कैसे काम करता है? (Hindi)
- पहली बार request पर popup; user "Allow" या "Don't Allow" चुनता है।
- "Don't Allow" के बाद iOS दोबारा popup नहीं दिखाता — तब `Linking.openSettings()` से Settings खुलवाओ।
- Location में: While Using / Always (Always के लिए अलग कारण string, और Apple review कड़ा)।
- Photos में "Limited Access" भी हो सकता है।
- Notifications के लिए Info.plist string नहीं, पर runtime request और APNs capability ज़रूरी।
**Screen वर्णन:** Popup में app का नाम, आपका लिखा कारण text और बटन "Allow While Using App", "Allow Once", "Don't Allow"।

---

## 🟡 Real World Example
Zomato पहली बार खुलने पर तुरंत location नहीं माँगता, बल्कि "Deliver to" screen पर बटन दबाने पर माँगता है — तब user समझता है क्यों चाहिए, इसलिए Allow की दर ज़्यादा होती है।

## 🟡 Real Example Hindi mein
Paytm QR scan बटन दबाने पर ही camera permission माँगता है, app खोलते ही नहीं। Deny हो जाए तो "Settings में जाकर camera allow करें" वाला बटन दिखता है।

---

## 💻 Code Example — Basic
```jsx
import React from 'react'; // React
import { View, Button, Alert, Linking } from 'react-native'; // UI + settings
import { Camera } from 'expo-camera'; // Expo camera (permissions API)

export default function CameraPermission() { // component
  const ask = async () => { // button पर चलेगा
    const { status } = await Camera.requestCameraPermissionsAsync(); // popup दिखाओ
    if (status === 'granted') { // मंजूर
      Alert.alert('OK', 'Camera चालू'); // संदेश
    } else { // मना किया
      Alert.alert('Permission चाहिए', 'Settings में camera allow करें', [
        { text: 'Cancel', style: 'cancel' }, // रद्द
        { text: 'Open Settings', onPress: () => Linking.openSettings() }, // Settings खोलो
      ]);
    }
  };
  return (
    <View style={{ padding: 24 }}>
      <Button title="Scan QR" onPress={ask} />
    </View>
  );
}
// app.json plugin: ["expo-camera", { "cameraPermission": "QR scan के लिए camera चाहिए" }]
```

## 💻 Code Example — Advanced
```jsx
import { useCallback, useEffect, useState } from 'react'; // hooks
import { AppState, Linking, Platform } from 'react-native'; // RN APIs
import * as Location from 'expo-location'; // location API

export function useLocationPermission() { // reusable hook
  const [status, setStatus] = useState('undetermined'); // permission status

  const refresh = useCallback(async () => { // वर्तमान status पढ़ो (popup नहीं)
    const { status: s } = await Location.getForegroundPermissionsAsync(); // सिर्फ check
    setStatus(s); // state update
  }, []);

  useEffect(() => {
    refresh(); // mount पर check
    const sub = AppState.addEventListener('change', (st) => { // app foreground पर लौटे
      if (st === 'active') refresh(); // Settings से लौटने पर दोबारा check
    });
    return () => sub.remove(); // cleanup
  }, [refresh]);

  const request = useCallback(async () => { // permission माँगो
    try {
      const { status: s, canAskAgain } = await Location.requestForegroundPermissionsAsync(); // popup
      setStatus(s); // update
      if (s !== 'granted' && !canAskAgain && Platform.OS === 'ios') { // iOS पर हमेशा के लिए denied
        Linking.openSettings(); // Settings खोलो
      }
    } catch (e) {
      console.log('permission error', e); // error log
    }
  }, []);

  return { status, request }; // बाहर दो
}
// app.json: ["expo-location", { "locationWhenInUsePermission": "पास के restaurants के लिए" }]
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Declare कहाँ | AndroidManifest `<uses-permission>` | Info.plist usage strings |
| कारण text | optional | अनिवार्य |
| Re-ask | "Don't ask again" के बाद नहीं | Deny के बाद कभी नहीं (Settings) |
| One-time | Android 11+ "Only this time" | "Allow Once" |
| Notifications | Android 13+ runtime permission | हमेशा runtime (iOS 10+) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: plugin options से Info.plist strings
// ["expo-camera", { "cameraPermission": "कारण" }]
// code: Camera.requestCameraPermissionsAsync()
```
CLI way:
```jsx
// Bare: Info.plist में हाथ से NSCameraUsageDescription
// code: react-native-permissions (ios/Podfile में `setup_permissions([...])` ज़रूरी)
// import { request, PERMISSIONS } from 'react-native-permissions';
// await request(PERMISSIONS.IOS.CAMERA);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: App खुलते ही सारी permissions माँगना।
✅ Correct: Feature इस्तेमाल के समय माँगो।

❌ Mistake 2: Usage string भूलना → crash।
✅ Correct: हर permission की string रखो।

❌ Mistake 3: Denied पर कुछ न दिखाना।
✅ Correct: कारण समझाओ + Settings बटन।

---

## 🧠 Tricky Interview Question
Q: User ने "Don't Allow" दबाया। आपने फिर `request...Async()` बुलाया, पर popup नहीं आया। क्यों?

Answer: iOS पहली बार के बाद popup नहीं दिखाता; status `denied` और `canAskAgain=false` आता है। बदलने का एक ही तरीका: user Settings में खुद बदले, इसलिए `Linking.openSettings()`।

---

## ⚫ Interview Questions + Answers
Q1: Usage description क्यों ज़रूरी?
A1: Apple अनिवार्य करता है; बिना इसके crash/rejection।

Q2: Location के कितने levels?
A2: When In Use, Always, (और Precise vs Approximate)।

Q3: Permission status कैसे बिना popup जाँचें?
A3: `get...PermissionsAsync()`।

Q4: Settings कैसे खोलें?
A4: `Linking.openSettings()`।

Q5: Expo Go में permission test?
A5: चलता है, पर Expo Go के नाम से कारण दिखता है; final test development/production build पर।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Feature को संवेदनशील access चाहिए।

❌ Avoid when:
- ज़रूरत न हो (जैसे photo picker iOS में बिना permission चलता है)।

---

## 📊 Visual Diagram
```
 Feature tap ─► status? ─┬─ granted ─► use feature
                         ├─ undetermined ─► request ─► popup ─► granted/denied
                         └─ denied ─► explain ─► Open Settings ─► AppState active ─► recheck
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Usage Description | Reason text | कारण का text |
| undetermined | Not asked yet | अभी पूछा नहीं |
| denied | User refused | मना किया |
| canAskAgain | Can show popup again | दोबारा पूछ सकते हैं? |
| Limited access | Selected photos only | सीमित access |

---

## ⚡ 3-Line Summary
English: Add usage strings, then request at the right moment.
English: iOS never re-prompts after denial; open Settings.
English: Re-check status when app returns to foreground.
Hindi: Usage string जोड़ो, सही समय पर माँगो।
Hindi: Deny के बाद iOS दोबारा नहीं पूछता; Settings खोलो।
Hindi: App वापस आने पर status दोबारा जाँचो।

---

## ➡️ Next Topic
235. App Icons Setup (iOS) — app की पहचान वाला icon।
