# 34. Button Component
# हिंदी में: Button Component (बिल्ट-इन सरल Button)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 के हिसाब से examples (check current docs — APIs change between SDKs). `Button` core component है।

---

## 🔵 Simple Definition (English)
`Button` is the simplest built-in button. It takes a `title`, an `onPress` and an optional `color`, and renders a platform-native looking button. It has **very little customisation** (no style prop).

## 🔵 सरल परिभाषा (Hindi)
`Button` सबसे सरल built-in button है। इसमें `title`, `onPress` और optional `color` दिया जाता है और यह platform के हिसाब से native जैसा दिखता है। इसमें **customisation बहुत कम** है (`style` prop नहीं होता)।

---

## 🔴 Problem it Solves
```
❌ सिर्फ एक test button चाहिए, इतना code क्यों: Pressable + Text + styles?
❌ Prototype/debug screens में तुरंत button
❌ Accessibility अपने आप (role = button)
```

## 🔴 यह क्यों बना? (Hindi)
```
Quick prototype, debug menu, simple form submit के लिए
बिना styling के एक native-look button चाहिए था।
Button: 2 props (title, onPress) में काम हो जाता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → <Button title="Pay" onPress={fn} /> लिखो
Step 2 → Android पर यह एक filled Material-जैसा button (color = background)
Step 3 → iOS पर text-only button (color = text का रंग)
Step 4 → disabled={true} दो तो grey होकर press बंद
Step 5 → press पर onPress चलता है
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → title और onPress के साथ <Button /> लिखो
Step 2 → Android पर भरा हुआ button (color = background रंग)
Step 3 → iOS पर सिर्फ text (color = text का रंग)
Step 4 → disabled दो तो grey और press बंद
Step 5 → press पर onPress चलता है
```

---

## 🟡 Real World Example
**Paytm** या **Swiggy** जैसे बड़े apps में अपने custom buttons होते हैं, `Button` नहीं। पर इनकी internal debug/QA screens, या "Retry" जैसे छोटे prototype screens में built-in `Button` काम आ जाता है। Interview में यह पूछा जाता है कि production में custom button क्यों बनाते हैं।

## 🟡 Real Example Hindi mein
बड़े apps (Zomato, Paytm) अपने design वाले custom buttons बनाते हैं। `Button` ज़्यादातर prototype, test screens या सरल demo में use होता है।

---

## 💻 Code Example — Basic
```jsx
// Basic Button — दोनों platforms
import React, { useState } from 'react';
import { Button, View, Text, StyleSheet } from 'react-native';

export default function BasicButton() {
  const [count, setCount] = useState(0);                // click count

  return (
    <View style={styles.container}>
      <Text style={styles.text}>Clicks: {count}</Text>
      <Button
        title="Add to Cart"                             // button text (string ज़रूरी)
        color="#e23744"                                 // Android: background | iOS: text colour
        onPress={() => setCount(c => c + 1)}            // tap
        accessibilityLabel="Add one item to cart"       // screen reader
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 24, gap: 12 },                  // gap RN 0.71+ में
  text: { fontSize: 18 },
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: Button को wrap करके platform-aware, disabled/loading, double-tap safe बनाना
import React, { useState } from 'react';
import { Button, View, Platform, ActivityIndicator, Alert, StyleSheet } from 'react-native';

export default function SubmitOrder({ onSubmit }) {
  const [loading, setLoading] = useState(false);         // request चल रही है?

  const handle = async () => {
    if (loading) return;                                  // double tap रोको
    setLoading(true);
    try {
      await onSubmit();                                   // API call
      Alert.alert('Success', 'Order placed');
    } catch (e) {
      Alert.alert('Error', e?.message ?? 'Something went wrong'); // error handling
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.wrap}>
      {/* View में wrap करके हम spacing/width कंट्रोल करते हैं (Button में style नहीं) */}
      <View style={styles.btnBox}>
        <Button
          title={loading ? 'Placing...' : 'Place Order'}
          onPress={handle}
          disabled={loading}                                // loading में बंद
          // Android में filled button का रंग, iOS में text का रंग
          color={Platform.select({ android: '#2e7d32', ios: '#007aff' })}
        />
      </View>
      {loading && <ActivityIndicator style={styles.spin} />}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flexDirection: 'row', alignItems: 'center', padding: 16 },
  btnBox: { flex: 1, borderRadius: 8, overflow: 'hidden' },  // Android पर rounded look के लिए clip
  spin: { marginLeft: 12 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Look | Filled, Material, uppercase title | Text-only, blue by default |
| `color` | Background colour | Text colour |
| `title` | Auto UPPERCASE | जैसा लिखा वैसा |
| Disabled look | Grey filled | Grey text |
| Ripple | ✅ native | ❌ opacity highlight |
| Extra props | `touchSoundDisabled` | `touchSoundDisabled` Android-side |
| Style prop | ❌ | ❌ |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo में भी core Button वही; custom look के लिए अपना Pressable button
import { Button } from 'react-native';
<Button title="Continue" onPress={() => {}} />
```
CLI way:
```jsx
// CLI में भी बिल्कुल वही — core से आता है, कोई native link नहीं
import { Button } from 'react-native';
<Button title="Continue" onPress={() => {}} />
// Custom design चाहिए तो Pressable + Text (दोनों में same approach)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `<Button style={{...}} />` की उम्मीद
✅ Correct: `Button` में style नहीं है; View में wrap करो या `Pressable` से custom button बनाओ।

❌ Mistake 2: `title` में JSX या number सीधे देना
✅ Correct: `title` string होना चाहिए (`title={String(n)}`)।

❌ Mistake 3: `onPress={fn()}` लिखना
✅ Correct: `onPress={fn}`।

❌ Mistake 4: मान लेना कि दोनों OS पर एक जैसा दिखेगा
✅ Correct: Android filled / iOS text-only — design match चाहिए तो custom button।

---

## 🧠 Tricky Interview Question
**Q: `<Button color="red" title="Delete" />` Android और iOS पर कैसा दिखेगा?**

Answer: Android पर **लाल background** वाला button और सफ़ेद text। iOS पर background नहीं होता, **text लाल** रंग का होगा। यानी `color` का मतलब OS पर निर्भर है। इसी वजह से design-consistent UI के लिए production में `Pressable` से custom button बनाते हैं।

---

## ⚫ Interview Questions + Answers
Q1: Button के required props?
A1: `title` (string) और `onPress`।

Q2: Button को style कैसे करें?
A2: सीधे नहीं। सिर्फ `color` बदलता है। View से लपेटो या Pressable से अपना component बनाओ।

Q3: Button disable कैसे?
A3: `disabled` prop। Press नहीं चलेगा और look grey होगा।

Q4: Button कब बजाय Pressable?
A4: Quick prototype, internal screens, जहाँ native look चलता हो।

Q5: Accessibility?
A5: Button default button role देता है; `accessibilityLabel` और `accessibilityHint` दे सकते हैं।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Prototype, demo, internal/debug screen
- Native-look simple action button

❌ Avoid when:
- Brand design (rounded, icons, gradients)
- Loading spinner button
- दोनों OS पर एक जैसा look चाहिए

---

## 📊 Visual Diagram
```
Android:                       iOS:
┌───────────────┐
│  ADD TO CART  │ (filled)      Add to Cart   (text only, coloured)
└───────────────┘
color = background             color = text colour
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| title | Button text | button का text |
| color | Bg (Android) / text (iOS) | रंग (OS के हिसाब से) |
| disabled | Turns off presses | press बंद |
| accessibilityLabel | Screen reader text | screen reader का text |
| Custom button | Pressable + Text | अपना बनाया button |

---

## ⚡ 3-Line Summary
English:
1. `Button` needs only `title` and `onPress` and looks native on each OS.
2. It cannot be styled; `color` means different things on Android and iOS.
3. For real apps build a custom button with `Pressable`.

Hindi:
1. `Button` में सिर्फ `title` और `onPress` चाहिए; हर OS पर native दिखता है।
2. इसे style नहीं कर सकते; `color` का मतलब Android और iOS में अलग है।
3. असली apps में `Pressable` से custom button बनाओ।

---

## ➡️ Next Topic
**35. Switch Component** — On/Off toggle (जैसे notifications, dark mode)।
