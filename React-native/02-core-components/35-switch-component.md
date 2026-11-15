# 35. Switch Component
# हिंदी में: Switch Component (On/Off Toggle)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 के हिसाब से examples (check current docs — APIs change between SDKs). `Switch` core component है।

---

## 🔵 Simple Definition (English)
`Switch` is a boolean toggle (on/off). It is a **controlled component**: you pass `value` and update it in `onValueChange`. Colours of the track and thumb can be customised.

## 🔵 सरल परिभाषा (Hindi)
`Switch` एक on/off toggle है। यह **controlled component** है: आप `value` देते हो और `onValueChange` में उसे update करते हो। Track और thumb के रंग बदल सकते हो।

---

## 🔴 Problem it Solves
```
❌ Settings में true/false चुनाव (Notifications, Dark mode, Autopay)
❌ Checkbox का native-look विकल्प मोबाइल पर नहीं था
❌ Android और iOS का native toggle अलग दिखता है
```

## 🔴 यह क्यों बना? (Hindi)
```
मोबाइल में on/off के लिए toggle switch ही standard है।
Switch एक component से दोनों OS का native toggle देता है
(Android: Material switch, iOS: UISwitch)।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → state बनाओ: const [on, setOn] = useState(false)
Step 2 → <Switch value={on} onValueChange={setOn} />
Step 3 → User tap/slide करता है
Step 4 → Native switch अपना नया value भेजता है → onValueChange(newValue)
Step 5 → आप state बदलते हो → value prop बदलता है → UI sync
Step 6 → अगर state नहीं बदली, switch वापस पुरानी जगह चला जाएगा
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → state बनाओ: const [on, setOn] = useState(false)
Step 2 → <Switch value={on} onValueChange={setOn} />
Step 3 → User tap/slide करता है
Step 4 → onValueChange(newValue) मिलता है
Step 5 → state बदलो → value prop बदलता है
Step 6 → state न बदलो तो switch वापस पुरानी position पर आ जाएगा
```

---

## 🟡 Real World Example
**Zomato** Settings में "Order notifications", **Swiggy** में "Use Swiggy Money", **Paytm** में "Hide balance"/"Biometric lock" और **WhatsApp**-जैसे apps में "Read receipts" — सब on/off toggles हैं।

## 🟡 Real Example Hindi mein
Swiggy में "Swiggy Money use करो" या Paytm में "Biometric lock" का on/off toggle — यही `Switch` है।

---

## 💻 Code Example — Basic
```jsx
// Basic Switch — दोनों platforms
import React, { useState } from 'react';
import { Switch, View, Text, StyleSheet } from 'react-native';

export default function BasicSwitch() {
  const [enabled, setEnabled] = useState(false);           // toggle state

  return (
    <View style={styles.row}>
      <Text style={styles.label}>Order Notifications</Text>
      <Switch
        value={enabled}                                     // वर्तमान state
        onValueChange={setEnabled}                          // बदलने पर state update
        trackColor={{ false: '#ccc', true: '#f9a8a8' }}     // track का रंग (off/on)
        thumbColor={enabled ? '#e23744' : '#f4f3f4'}        // thumb का रंग
      />
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16 },
  label: { fontSize: 16 },
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: settings screen — server sync + optimistic update + rollback + disabled while saving
import React, { useState, useCallback } from 'react';
import { Switch, View, Text, Alert, Platform, StyleSheet } from 'react-native';

// fake API — असली में fetch/axios
const saveSetting = (key, value) =>
  new Promise((res, rej) => setTimeout(() => (Math.random() > 0.2 ? res() : rej(new Error('Network error'))), 400));

function SettingRow({ label, settingKey, initial }) {
  const [value, setValue] = useState(initial);            // वर्तमान value
  const [saving, setSaving] = useState(false);            // सेव हो रहा है

  const onChange = useCallback(async (next) => {
    const prev = value;                                    // पुरानी value याद रखो
    setValue(next);                                        // optimistic update
    setSaving(true);
    try {
      await saveSetting(settingKey, next);                 // server पर save
    } catch (e) {
      setValue(prev);                                      // fail → वापस पुरानी
      Alert.alert('Could not save', e.message);            // user को बताओ
    } finally {
      setSaving(false);
    }
  }, [value, settingKey]);

  return (
    <View style={styles.row}>
      <Text style={styles.label}>{label}</Text>
      <Switch
        value={value}
        onValueChange={onChange}
        disabled={saving}                                  // save के दौरान बंद
        accessibilityLabel={label}
        trackColor={{ false: '#d1d5db', true: '#86efac' }}
        thumbColor={Platform.OS === 'android' ? (value ? '#16a34a' : '#f4f3f4') : undefined} // iOS पर default thumb
        ios_backgroundColor="#d1d5db"                      // iOS: off-state background (सिर्फ iOS)
      />
    </View>
  );
}

export default function Settings() {
  return (
    <View>
      <SettingRow label="Order updates" settingKey="orders" initial />
      <SettingRow label="Offers & promos" settingKey="promos" initial={false} />
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16 },
  label: { fontSize: 16 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Native view | Material `SwitchCompat` | `UISwitch` |
| `thumbColor` | ✅ पूरा control | ✅ (iOS पर सीमित/सिर्फ थोड़ा दिखता है) |
| `trackColor` | ✅ | ✅ |
| `ios_backgroundColor` | ❌ ignore | ✅ off-state का background |
| Size | Material size | Fixed iOS size (resize के लिए `transform: scale`) |
| Look | Flat with thumb | Rounded, green default on |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Core Switch — Expo Go में बिना install
import { Switch } from 'react-native';
<Switch value={true} onValueChange={() => {}} />
```
CLI way:
```jsx
// CLI में भी वही। Custom/animated toggle चाहिए तो library
// (जैसे react-native-switch) — install + pod install (iOS)
import { Switch } from 'react-native';
<Switch value={true} onValueChange={() => {}} />
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `value` देना पर `onValueChange` में state न बदलना
```jsx
<Switch value={on} />  // ❌ switch हिलेगा ही नहीं / वापस आएगा
```
✅ Correct: `onValueChange={setOn}`।

❌ Mistake 2: `onPress` लगाना (Switch में नहीं होता)
✅ Correct: `onValueChange`।

❌ Mistake 3: `value={undefined}` / non-boolean value
✅ Correct: हमेशा boolean (`!!x`)।

---

## 🧠 Tricky Interview Question
```jsx
const [on, setOn] = useState(false);
<Switch value={on} onValueChange={() => {}} />
```
**Q: User tap करे तो क्या होगा?**

Answer: Switch थोड़ा हिलेगा फिर **वापस off** पर आ जाएगा, क्योंकि यह controlled component है और हमने state नहीं बदली। जो `value` prop है वही सच है। यह controlled input की classic गलती है।

---

## ⚫ Interview Questions + Answers
Q1: Switch controlled क्यों?
A1: State एक जगह (React) में रहे इसलिए; UI वही दिखाता है जो `value` बताती है।

Q2: `onValueChange` और `onChange` में अंतर?
A2: `onValueChange(newBool)` सीधे boolean देता है। `onChange` event object देता है।

Q3: iOS पर off-state background?
A3: `ios_backgroundColor` prop।

Q4: Switch का size बदलना?
A4: सीधे नहीं; `style={{ transform: [{ scaleX: 1.2 }, { scaleY: 1.2 }] }}`।

Q5: Server पर save करते समय कैसे?
A5: Optimistic update + fail पर rollback, और save के दौरान `disabled`।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Binary settings (on/off) जो तुरंत लागू हों
- Notifications, dark mode, privacy toggles

❌ Avoid when:
- कई विकल्प (radio/segmented)
- Form में "I agree" जैसा checkbox (checkbox बेहतर)
- Action जिसे confirm चाहिए (button)

---

## 📊 Visual Diagram
```
OFF:  [ ●─────  ]  value=false
ON :  [  ─────● ]  value=true

tap → onValueChange(true) → setOn(true) → value=true → UI ON
tap → onValueChange(true) → (state नहीं बदली) → UI वापस OFF ❌
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Controlled component | UI driven by state | state से चलने वाला |
| value | Current boolean | वर्तमान true/false |
| onValueChange | Callback with new value | नई value के साथ callback |
| trackColor | Track colours | track के रंग |
| thumbColor | Thumb colour | thumb का रंग |

---

## ⚡ 3-Line Summary
English:
1. `Switch` is a controlled on/off toggle.
2. Always update state in `onValueChange` or it snaps back.
3. Customise with `trackColor`, `thumbColor`, `ios_backgroundColor`.

Hindi:
1. `Switch` controlled on/off toggle है।
2. `onValueChange` में state ज़रूर बदलो वरना वापस लौटेगा।
3. `trackColor`, `thumbColor`, `ios_backgroundColor` से रंग बदलो।

---

## ➡️ Next Topic
**36. Slider Component** — range में value चुनना (जैसे price filter)।
