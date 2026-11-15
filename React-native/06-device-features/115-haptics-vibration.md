# 115. Haptics (Vibration)
# हिंदी में: Haptics — स्पर्श/कंपन Feedback
# Platform: Android ✅ | iOS ✅ | Both ✅

---

**Expo SDK 52 / React Native 0.76 (check current docs — APIs change between SDKs).** Library: `expo-haptics`. Core RN में `Vibration` भी है।

---

## 🔵 Simple Definition (English)
**Haptics** gives small physical feedback (taps, buzzes) when the user does something: a light tap on button press, a success pulse after payment. `expo-haptics` gives refined feedback (impact, notification, selection). Core `Vibration` just buzzes the motor for a set time.

## 🔵 सरल परिभाषा (Hindi)
**Haptics** user के action पर हल्का physical feedback (tap, कंपन) देता है, जैसे button दबाने पर हल्का tap या payment सफल होने पर success pulse। `expo-haptics` बारीक feedback देता है (impact, notification, selection)। Core `Vibration` सिर्फ तय समय के लिए motor चलाता है।

---

## 🔴 Problem it Solves
```
PROBLEM:
  Screen पर tap हुआ या नहीं, user को "महसूस" नहीं होता.
  Payment success/failure सिर्फ़ आँख से दिखता है.
  Vibration.vibrate() भारी और बेढंगा लगता है.

HAPTICS:
  ✅ Light/Medium/Heavy impact
  ✅ Success / Warning / Error notification pattern
  ✅ Selection tick (picker, slider)
  ✅ App premium महसूस होता है
```

## 🔴 यह क्यों बना? (Hindi)
सिर्फ visual feedback काफी नहीं, user को छूकर भी पता चलना चाहिए कि action हुआ। पुराना `Vibration.vibrate()` लंबा और भद्दा buzz देता है। Haptics engine (iOS Taptic Engine, Android vibrator) से छोटा, साफ़ feedback मिलता है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install expo-haptics
Step 2 → import * as Haptics from 'expo-haptics'
Step 3 → Event पर call: Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)
Step 4 → Result के लिए: Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success)
Step 5 → Picker/slider के लिए: Haptics.selectionAsync()
Step 6 → Device support न करे तो call चुपचाप कुछ नहीं करता (crash नहीं)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → expo-haptics install करो
Step 2 → Haptics import करो
Step 3 → Tap पर impactAsync (Light/Medium/Heavy)
Step 4 → Success/Error पर notificationAsync
Step 5 → Picker/slider में selectionAsync
Step 6 → Device सपोर्ट न करे तो कुछ नहीं होता
```

---

## 🟡 Real World Example
**PhonePe/Paytm** में UPI payment सफल होने पर हल्का success haptic मिलता है, गलत PIN पर error haptic। **Swiggy** में cart में item add करते समय light tap। **Zomato** में rating slider चलाते समय selection ticks।

## 🟡 Real Example Hindi mein
PhonePe में payment सफल होने पर success कंपन, गलत PIN पर error कंपन आता है। Swiggy में item add करने पर हल्का tap। Zomato के rating slider पर हर step पर छोटी tick।

---

## 💻 Code Example — Basic
```jsx
// HapticsBasic.jsx — अलग-अलग haptic types
import React from 'react';                                  // React
import { View, Button } from 'react-native';                // UI
import * as Haptics from 'expo-haptics';                    // npx expo install expo-haptics

export default function HapticsBasic() {                    // component
  return (                                                  // UI
    <View style={{ flex: 1, justifyContent: 'center', padding: 24, gap: 10 }}>{/* container */}
      <Button title="Light" onPress={() => Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)} />{/* हल्का tap */}
      <Button title="Heavy" onPress={() => Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy)} />{/* भारी tap */}
      <Button title="Success" onPress={() => Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success)} />{/* success */}
      <Button title="Error" onPress={() => Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error)} />{/* error */}
      <Button title="Selection" onPress={() => Haptics.selectionAsync()} />{/* tick */}
    </View>
  );                                                        // return खत्म
}                                                           // component खत्म
```

## 💻 Code Example — Advanced
```jsx
// useHaptics.js + PayButton.jsx — safe wrapper, user setting, Android fallback to Vibration
import React, { useCallback, useState } from 'react';       // hooks
import { Pressable, Text, Platform, Vibration, Switch, View, StyleSheet } from 'react-native'; // core
import * as Haptics from 'expo-haptics';                    // haptics

// Custom hook: haptics को enable/disable setting के साथ safe बनाता है
export function useHaptics(enabled = true) {                // enabled = user की setting
  const run = useCallback(async (fn, fallbackMs) => {       // fn = haptic call
    if (!enabled) return;                                   // user ने बंद किया हो तो कुछ नहीं
    try {                                                   // error handling
      await fn();                                           // haptic चलाओ
    } catch (e) {                                           // unsupported device
      if (Platform.OS === 'android' && fallbackMs) Vibration.vibrate(fallbackMs); // Android पर simple buzz fallback
    }                                                       // catch खत्म
  }, [enabled]);                                            // enabled बदले तो नया function

  return {                                                  // helpers लौटाओ
    tap: () => run(() => Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light), 15),                          // light tap
    success: () => run(() => Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success), 40),         // success
    error: () => run(() => Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error), 120),            // error
  };                                                        // return खत्म
}                                                           // hook खत्म

export default function PayButton() {                       // component
  const [on, setOn] = useState(true);                       // haptics setting
  const h = useHaptics(on);                                 // hook use

  const pay = async () => {                                 // payment simulate
    h.tap();                                                // press पर tap
    const ok = Math.random() > 0.5;                         // fake result
    ok ? h.success() : h.error();                           // result के हिसाब से haptic
  };                                                        // function खत्म

  return (                                                  // UI
    <View style={s.c}>{/* container */}
      <Pressable style={s.b} onPress={pay}><Text style={s.t}>Pay ₹499</Text></Pressable>{/* pay button */}
      <View style={s.row}><Text>Haptics</Text><Switch value={on} onValueChange={setOn} /></View>{/* setting switch */}
    </View>
  );                                                        // return खत्म
}                                                           // component खत्म

const s = StyleSheet.create({                               // styles
  c: { flex: 1, justifyContent: 'center', padding: 24, gap: 16 },   // layout
  b: { backgroundColor: '#5f259f', padding: 14, borderRadius: 8 },  // button
  t: { color: '#fff', textAlign: 'center', fontWeight: '700' },     // text
  row: { flexDirection: 'row', justifyContent: 'space-between' },   // row
});                                                         // खत्म
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Engine | Vibrator motor (hardware पर निर्भर) | Taptic Engine |
| Quality | Device के हिसाब से अलग, सस्ते phones पर कमज़ोर | बहुत सटीक |
| Permission | `expo-haptics` के लिए manifest में VIBRATE permission जुड़ती है (Expo handles) | कोई नहीं |
| Core `Vibration` | `vibrate(ms)`, pattern, cancel | सिर्फ fixed छोटा buzz, duration ignore |
| Silent/Low power mode | System settings में touch feedback बंद हो सकता है | Low Power Mode / कुछ settings में haptics बंद |
| iOS Simulator | - | Haptics नहीं चलते, असली device चाहिए |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: expo-haptics
import * as Haptics from 'expo-haptics';                 // npx expo install expo-haptics
Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium); // refined haptic
```
CLI way:
```jsx
// CLI: या तो expo-haptics (expo modules setup के साथ) या community library
import ReactNativeHapticFeedback from 'react-native-haptic-feedback'; // npm i react-native-haptic-feedback; cd ios && pod install
ReactNativeHapticFeedback.trigger('impactLight');                    // haptic
import { Vibration } from 'react-native';                            // बिना library: core
Vibration.vibrate(50);                                               // सिर्फ buzz
// Android CLI में <uses-permission android:name="android.permission.VIBRATE" /> manifest में चाहिए
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: हर tap/scroll पर haptic चलाना।
✅ Correct: सिर्फ meaningful actions (add, success, error) पर।

❌ Mistake 2: iOS Simulator पर test करके "काम नहीं करता" कहना।
✅ Correct: असली device पर test करो।

❌ Mistake 3: `Vibration.vibrate(1000)` जैसा लंबा buzz।
✅ Correct: `expo-haptics` का छोटा impact।

❌ Mistake 4: User को haptics बंद करने का option न देना।
✅ Correct: Settings में toggle दो (accessibility)।

---

## 🧠 Tricky Interview Question
```jsx
Vibration.vibrate([0, 500, 200, 500]);
```
यह Android और iOS पर क्या करेगा?

Answer: Android पर pattern `[wait, vibrate, wait, vibrate]` है: तुरंत शुरू, 500ms buzz, 200ms रुकना, 500ms buzz। iOS पर duration/pattern ignore होता है; सिर्फ एक fixed छोटा कंपन मिलता है (और pattern repeat जैसा व्यवहार नहीं)। इसीलिए cross-platform feedback के लिए `expo-haptics` बेहतर है।

---

## ⚫ Interview Questions + Answers
Q1: Haptics और Vibration में फर्क?
A1: Haptics छोटे, प्रकार वाले feedback (impact/notification/selection) देता है; Vibration सिर्फ motor को duration के लिए चलाता है।

Q2: Haptics के प्रकार?
A2: Impact (Light/Medium/Heavy/Rigid/Soft), Notification (Success/Warning/Error), Selection।

Q3: Device सपोर्ट न करे तो?
A3: Call चुपचाप कुछ नहीं करता, फिर भी try/catch रखना अच्छा है।

Q4: Accessibility का ध्यान कैसे?
A4: Toggle दो और haptic को एकमात्र feedback मत बनाओ, visual भी रखो।

Q5: Android permission?
A5: `VIBRATE` permission; Expo इसे खुद जोड़ता है, CLI में manifest में लिखो।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Payment success/failure
- Add to cart, like, toggle
- Picker/slider ticks

❌ Avoid when:
- हर scroll/tap पर
- लंबे alerts के लिए (वह notification sound का काम है)
- Battery बचानी हो / user ने बंद किया हो

---

## 📊 Visual Diagram
```
 User action
     |
     v
 Haptics.impactAsync / notificationAsync / selectionAsync
     |
     +--> iOS: Taptic Engine (precise)
     +--> Android: Vibrator (device dependent)
     |
     v
 User को touch feedback
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Haptic | Touch feedback | स्पर्श feedback |
| Impact | Tap-like feedback | टकराने जैसा tap |
| Notification feedback | Success/Warning/Error | परिणाम वाला feedback |
| Selection | Tiny tick on change | चयन बदलने पर tick |
| Taptic Engine | iOS vibration hardware | iOS का कंपन hardware |

---

## ⚡ 3-Line Summary
English: Haptics gives small touch feedback for key actions.
Use expo-haptics (impact, notification, selection) instead of long Vibration buzzes.
Test on real devices and let users turn it off.

Hindi: Haptics ज़रूरी actions पर छोटा स्पर्श feedback देता है।
लंबे Vibration की जगह expo-haptics (impact, notification, selection) use करो।
असली device पर test करो और user को बंद करने दो।

---

## ➡️ Next Topic
**116. Brightness + Screen**, अब screen की brightness और screen को जगाए रखना सीखेंगे।
