# 100. Permissions Handling
# हिंदी में: Permissions Handling (अनुमति सही तरीके से संभालना)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: Expo SDK 52 (React Native 0.76) + `expo-camera`, `expo-location`, `expo-notifications`, `expo-linking` (check current docs — APIs change between SDKs).
> Note: `91-permissions.md` में basics हैं; यहाँ एक reusable **handling pattern** (granted / denied / blocked / settings) पर focus है।

---

## 🔵 Simple Definition (English)
**Permissions handling** means asking the user for access (camera, location, notifications…) at the right time, reading the result (`granted`, `denied`, `canAskAgain`), and guiding the user when access is blocked — usually by opening the app's Settings.

## 🔵 सरल परिभाषा (Hindi)
**Permissions handling** का मतलब है सही समय पर user से access (camera, location, notifications…) माँगना, नतीजा (`granted`, `denied`, `canAskAgain`) पढ़ना, और access blocked हो तो user को app की Settings तक पहुँचाना।

---

## 🔴 Problem it Solves
```
❌ App start par 5 permission ek saath maangna -> user "Deny"
❌ Denied ke baad button kuch nahi karta (dead end)
❌ Permission ke bina API call -> crash / blank screen
✅ Context me maango, status check karo, blocked ho to Settings dikhao
```

## 🔴 यह क्यों बना? (Hindi)
```
OS user की privacy बचाता है, इसलिए हर sensitive feature पर permission लगती है।
गलत समय पर माँगने से user "Deny" दबा देता है।
Deny के बाद OS दोबारा prompt नहीं दिखाता,
इसलिए app को Settings तक ले जाने का रास्ता देना पड़ता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Native declarations: Android manifest / iOS Info.plist (Expo me app.json plugins)
Step 2 → getXPermissionsAsync() se current status
Step 3 → status 'granted' ho to feature chalao
Step 4 → 'undetermined' ho to context dikhake request...Async() call karo
Step 5 → 'denied' + canAskAgain=true => explain karke dobara pucho
Step 6 → 'denied' + canAskAgain=false (blocked) => Linking.openSettings()
Step 7 → AppState 'active' par status dobara check (user Settings se laut aaya)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले manifest / Info.plist में कारण (usage description) घोषित करें।
Step 2 → पहले मौजूदा status देखें, सीधे request न करें।
Step 3 → granted -> feature चलाएँ; undetermined -> prompt दिखाएँ।
Step 4 → blocked (canAskAgain=false) -> Settings खोलने का बटन दें।
Step 5 → user Settings से लौटे तो status फिर जाँचें।
```

---

## 🟡 Real World Example
**Zomato / Swiggy:** Location is asked only when you tap "Use current location", with a one-line reason first. If you denied it forever, a banner says "Location off — Open Settings". **Instagram:** camera permission only when you tap the camera icon, not at launch.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy:** Location तभी माँगते हैं जब आप "Use current location" दबाते हैं, पहले एक लाइन में कारण बताते हैं। हमेशा के लिए deny किया हो तो "Location बंद है — Settings खोलें" बैनर दिखता है। **Instagram:** Camera permission launch पर नहीं, camera icon दबाने पर।

---

## 💻 Code Example — Basic
```jsx
// PermBasic.jsx — camera permission: hook se status + request
import React from 'react';                                             // React
import { View, Text, Button } from 'react-native';                     // RN UI
import { useCameraPermissions } from 'expo-camera';                    // permission hook

export default function PermBasic() {
  const [perm, requestPerm] = useCameraPermissions();                  // perm = null jab tak load ho raha ho

  if (!perm) return <View />;                                          // status load ho raha hai

  if (!perm.granted) {                                                 // access nahi mila
    return (
      <View style={{ padding: 32, gap: 12 }}>
        <Text>Photo scan karne ke liye camera chahiye.</Text>
        <Button title="Allow Camera" onPress={requestPerm} />          // prompt dikhao
      </View>
    );
  }
  return <Text>Camera allowed ✅</Text>;                                // granted: feature chalao
}
```

## 💻 Code Example — Advanced
```jsx
// usePermission.js — reusable hook: granted / denied / blocked + Settings + AppState recheck
import { useCallback, useEffect, useRef, useState } from 'react';
import { AppState, Linking, Alert } from 'react-native';
import * as Location from 'expo-location';

// status: 'loading' | 'granted' | 'undetermined' | 'denied' | 'blocked'
export function useLocationPermission() {
  const [status, setStatus] = useState('loading');                    // current state
  const appState = useRef(AppState.currentState);                     // pichhla app state

  const map = (p) =>                                                  // expo result -> hamara status
    p.granted ? 'granted'
    : p.status === 'undetermined' ? 'undetermined'
    : p.canAskAgain ? 'denied'                                        // dobara pooch sakte hain
    : 'blocked';                                                      // sirf Settings se

  const check = useCallback(async () => {
    try {
      setStatus(map(await Location.getForegroundPermissionsAsync())); // sirf check, prompt nahi
    } catch (e) {
      console.warn('perm check failed', e);                           // error handling
      setStatus('denied');
    }
  }, []);

  const request = useCallback(async () => {
    const res = await Location.requestForegroundPermissionsAsync();   // prompt
    const next = map(res);
    setStatus(next);
    if (next === 'blocked') {                                         // dobara prompt nahi aayega
      Alert.alert('Location band hai', 'Settings me jaake allow karo.', [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Open Settings', onPress: () => Linking.openSettings() }, // app settings page
      ]);
    }
    return next === 'granted';
  }, []);

  useEffect(() => { check(); }, [check]);                             // mount par check

  useEffect(() => {                                                   // Settings se wapas aane par recheck
    const sub = AppState.addEventListener('change', (next) => {
      if (appState.current.match(/inactive|background/) && next === 'active') check();
      appState.current = next;                                        // state yaad rakho
    });
    return () => sub.remove();                                        // cleanup
  }, [check]);

  return { status, request, openSettings: Linking.openSettings };
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Declaration | `AndroidManifest.xml` (Expo: `android.permissions`) | `Info.plist` usage strings (Expo: `infoPlist` / plugin options) |
| Reason text | Optional (rationale in app UI) | **Mandatory** `NS...UsageDescription` else crash / App Store reject |
| "Deny" behaviour | 2nd deny / "Don't ask again" => blocked | **One** prompt only; after deny only Settings |
| One-time grant | "Only this time" (Android 11+) | "Allow Once" (iOS 13+) |
| Notifications | Android 13+ runtime | Always runtime |
| `shouldShowRequestRationale` | Exists (`PermissionsAndroid`) | Not available |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// app.json: { "expo": { "plugins": [["expo-camera", { "cameraPermission": "Scan ke liye camera chahiye" }]] } }
import { useCameraPermissions } from 'expo-camera';               // module-specific hooks
const [perm, request] = useCameraPermissions();                    // sab modules ka same pattern
```
CLI way:
```jsx
// AndroidManifest.xml + Info.plist khud edit karo; library: react-native-permissions
import { check, request, PERMISSIONS, RESULTS } from 'react-native-permissions';
const res = await check(PERMISSIONS.ANDROID.CAMERA);              // iOS: PERMISSIONS.IOS.CAMERA
if (res === RESULTS.DENIED) await request(PERMISSIONS.ANDROID.CAMERA); // RESULTS.BLOCKED => openSettings()
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: App launch पर सारी permissions एक साथ माँगना।
✅ Correct: Feature इस्तेमाल होने के समय, कारण दिखाकर माँगें।

❌ Mistake 2: Denied के बाद फिर से `request` बुलाते रहना (कुछ नहीं होता)।
✅ Correct: `canAskAgain === false` हो तो `Linking.openSettings()`।

❌ Mistake 3: iOS usage description भूल जाना।
✅ Correct: `app.json` plugin options / `infoPlist` में स्पष्ट text दें।

❌ Mistake 4: Settings से लौटने पर status refresh न करना।
✅ Correct: `AppState` 'active' पर दोबारा `get...PermissionsAsync()`।

❌ Mistake 5: Permission के बिना API call करना।
✅ Correct: पहले status जाँचें, fallback UI रखें (manual address entry जैसा)।

---

## 🧠 Tricky Interview Question
On iOS the user denied location once. Your button calls `requestForegroundPermissionsAsync()` again. What happens?

Answer: Nothing visible — iOS shows the system prompt only **once**. The call returns `denied` immediately with `canAskAgain: false`. The only path is `Linking.openSettings()` and re-checking on return. (On Android a second deny also leads to the same "blocked" state.)

हिंदी: iOS prompt सिर्फ़ एक बार दिखाता है; दोबारा request करने पर तुरंत `denied` और `canAskAgain:false` मिलता है। अब सिर्फ़ Settings का रास्ता है।

---

## ⚫ Interview Questions + Answers
Q1: `denied` और `blocked` में क्या फ़र्क है?
A1: Denied = अभी मना किया पर `canAskAgain` true हो सकता है; blocked = `canAskAgain` false, prompt नहीं आएगा, Settings चाहिए।

Q2: Permission कब माँगनी चाहिए?
A2: Just-in-time — feature की ज़रूरत पर, पहले "pre-permission" explanation screen के साथ।

Q3: Settings खोलने का API?
A3: `Linking.openSettings()` (React Native core)।

Q4: Android 13 में कौन सी नई permission आई?
A4: `POST_NOTIFICATIONS` runtime permission; साथ ही photo/video के granular media permissions।

Q5: Expo में usage description कहाँ लिखते हैं?
A5: `app.json` में config plugin options (जैसे `cameraPermission`) या `ios.infoPlist`।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Camera, location, contacts, notifications, microphone जैसी sensitive access
- Reusable hook बनाना हो (हर screen पर वही pattern)

❌ Avoid when:
- Feature बिना permission भी चल सकता है (image picker का system picker — permission नहीं लगती)
- Launch पर अंधाधुंध सारी permissions माँगना

---

## 📊 Visual Diagram
```
 Feature button tap
        │
 get...PermissionsAsync()
        │
  ┌─────┼──────────────┬───────────────────────┐
granted  undetermined  denied(canAskAgain)     blocked(!canAskAgain)
  │          │              │                        │
 run      request()    explain + request()    Alert -> Linking.openSettings()
                                                      │
                            AppState 'active' ──▶ re-check status
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| granted | Access allowed | अनुमति मिली |
| denied | User said no | user ने मना किया |
| blocked | Cannot ask again | दोबारा नहीं पूछ सकते |
| canAskAgain | Can prompt again? | फिर prompt संभव? |
| Usage description | Reason text (iOS) | कारण का text |
| Just-in-time | Ask when needed | ज़रूरत पर माँगना |

---

## ⚡ 3-Line Summary
English: Check status first, request in context, and read granted/denied/canAskAgain.
If blocked, send the user to Settings with Linking.openSettings().
Re-check on AppState active and always provide a fallback.

Hindi: पहले status जाँचें, सही संदर्भ में request करें, और granted/denied/canAskAgain पढ़ें।
Blocked हो तो Linking.openSettings() से Settings दिखाएँ।
AppState active पर फिर जाँचें और fallback UI रखें।

---

## ➡️ Next Topic
**101. Contacts — expo-contacts** — permission के बाद फ़ोन की contact list पढ़ना और जोड़ना।

---
