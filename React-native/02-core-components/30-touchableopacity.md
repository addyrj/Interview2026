# 30. TouchableOpacity
# हिंदी में: TouchableOpacity (Tap पर Opacity बदलने वाला Button)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 के हिसाब से examples (check current docs — APIs change between SDKs). ध्यान दें: आज RN docs में `Pressable` को modern recommended बताया जाता है, पर `TouchableOpacity` अभी भी चलता है और interviews में बहुत पूछा जाता है।

---

## 🔵 Simple Definition (English)
`TouchableOpacity` wraps any view and makes it tappable. When pressed, the wrapped view fades (its opacity goes down) to give visual feedback. It accepts `onPress`, `onLongPress`, `activeOpacity` and `disabled`.

## 🔵 सरल परिभाषा (Hindi)
`TouchableOpacity` किसी भी view को tappable बना देता है। दबाने पर view हल्का (opacity कम) हो जाता है ताकि user को feedback मिले। इसमें `onPress`, `onLongPress`, `activeOpacity`, `disabled` props होते हैं।

---

## 🔴 Problem it Solves
```
❌ View / Text पर onPress नहीं होता (View में touch events सीधे नहीं)
❌ Tap पर कोई visual feedback नहीं → user को पता नहीं चला दबा या नहीं
❌ Custom-designed button (icon + text + image) के लिए Button component बहुत सीमित
```

## 🔴 यह क्यों बना? (Hindi)
```
Native Button का look बदलना मुश्किल है।
हमें अपनी design (Zomato का orange "Add" button) चाहिए।
TouchableOpacity: कोई भी children रखो + tap feedback अपने आप।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → आप children को <TouchableOpacity onPress={fn}> में लपेटते हो
Step 2 → उँगली रखने पर touch system "press in" event देता है
Step 3 → component Animated से children की opacity 1 → activeOpacity (default 0.2) करता है
Step 4 → उँगली उठाने पर (जगह के अंदर) onPress चलता है
Step 5 → opacity वापस 1
Step 6 → देर तक दबाओ तो onLongPress (delayLongPress ms बाद)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → children को TouchableOpacity में रखो
Step 2 → उँगली रखते ही press-in event
Step 3 → opacity 1 से activeOpacity (default 0.2) तक घटती है
Step 4 → उँगली उठाने पर onPress चलता है
Step 5 → opacity वापस 1
Step 6 → देर तक दबाने पर onLongPress
```

---

## 🟡 Real World Example
**Zomato** का "ADD" button, **Swiggy** के bottom "View Cart" bar, **Paytm** के "Pay Now" और recharge icons — सब tap पर हल्के होते हैं, यही `TouchableOpacity` जैसा feedback है। Instagram का like heart भी यही pattern use करता है।

## 🟡 Real Example Hindi mein
Zomato का "ADD" button दबाने पर थोड़ा फीका होता है — यही TouchableOpacity है। Swiggy का "View Cart" bar और Paytm का "Pay Now" भी ऐसे ही काम करते हैं।

---

## 💻 Code Example — Basic
```jsx
// Basic TouchableOpacity — दोनों platforms
import React, { useState } from 'react';                        // state के लिए
import { TouchableOpacity, Text, View, StyleSheet } from 'react-native';

export default function AddButton() {
  const [count, setCount] = useState(0);                         // item count

  return (
    <View style={styles.container}>
      <TouchableOpacity
        activeOpacity={0.6}                                      // दबने पर 60% visible
        onPress={() => setCount(c => c + 1)}                     // tap पर count +1
        style={styles.btn}                                       // button style
      >
        <Text style={styles.text}>ADD</Text>
      </TouchableOpacity>
      {/* count दिखाओ */}
      <Text>Items: {count}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20, alignItems: 'flex-start' },          // बाएं align
  btn: { backgroundColor: '#fff', borderColor: '#e23744', borderWidth: 1, paddingHorizontal: 24, paddingVertical: 8, borderRadius: 8 },
  text: { color: '#e23744', fontWeight: '700' },                 // Zomato red
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: debounce double-tap, disabled+loading, long press, accessibility, hitSlop
import React, { useState, useRef, useCallback } from 'react';
import { TouchableOpacity, Text, ActivityIndicator, Alert, StyleSheet, Platform, Vibration } from 'react-native';

export default function PayButton({ onPay, amount }) {
  const [loading, setLoading] = useState(false);                 // API चल रही है?
  const lastTap = useRef(0);                                     // पिछला tap time

  const handlePress = useCallback(async () => {
    const now = Date.now();
    if (now - lastTap.current < 800) return;                     // double tap रोको
    lastTap.current = now;
    setLoading(true);                                            // loader चालू
    try {
      await onPay(amount);                                       // payment API
    } catch (e) {
      Alert.alert('Payment failed', e.message ?? 'Try again');   // error दिखाओ
    } finally {
      setLoading(false);                                         // हमेशा बंद
    }
  }, [onPay, amount]);

  return (
    <TouchableOpacity
      onPress={handlePress}
      onLongPress={() => Platform.OS === 'android' && Vibration.vibrate(30)} // Android पर हल्का vibrate
      delayLongPress={500}                                       // 500ms में long press
      disabled={loading}                                         // loading में बंद
      activeOpacity={0.7}
      hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}         // tap area बड़ा
      accessibilityRole="button"                                 // screen reader
      accessibilityLabel={`Pay ${amount} rupees`}
      accessibilityState={{ disabled: loading, busy: loading }}
      style={[styles.btn, loading && styles.disabled]}           // disabled look
    >
      {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.text}>Pay ₹{amount}</Text>}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  btn: { backgroundColor: '#00baf2', padding: 14, borderRadius: 10, alignItems: 'center' }, // Paytm blue
  disabled: { opacity: 0.5 },
  text: { color: '#fff', fontWeight: '700', fontSize: 16 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Feedback | Opacity fade (ripple नहीं) | Opacity fade |
| Native ripple | ❌ (इसके लिए TouchableNativeFeedback / Pressable `android_ripple`) | N/A |
| `onLongPress` haptic | खुद `Vibration` / Haptics | खुद Haptics |
| `hasTVPreferredFocus` etc. | सिर्फ TV | सिर्फ TV |
| Default `activeOpacity` | 0.2 | 0.2 |
| Hit area | ≥48dp guideline | ≥44pt guideline |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Haptic feedback के लिए expo-haptics (npx expo install expo-haptics)
import * as Haptics from 'expo-haptics';
import { TouchableOpacity, Text } from 'react-native';

<TouchableOpacity onPress={() => Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)}>
  <Text>Tap</Text>
</TouchableOpacity>
```
CLI way:
```jsx
// CLI: TouchableOpacity वही। Haptic के लिए react-native-haptic-feedback (pod install)
import ReactNativeHapticFeedback from 'react-native-haptic-feedback';
import { TouchableOpacity, Text } from 'react-native';

<TouchableOpacity onPress={() => ReactNativeHapticFeedback.trigger('impactLight')}>
  <Text>Tap</Text>
</TouchableOpacity>
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `onPress={handle()}` (call हो जाता है render पर)
✅ Correct: `onPress={handle}` या `onPress={() => handle(id)}`

❌ Mistake 2: एक से ज़्यादा children बिना wrapper (पुराने versions में दिक्कत)
✅ Correct: अंदर एक `View` रखो जिसमें सब children हों।

❌ Mistake 3: Double tap से दो बार API call / दो बार navigate
✅ Correct: loading state + `disabled` या debounce।

❌ Mistake 4: छोटा tap area (icon 20x20)
✅ Correct: `hitSlop` या padding।

---

## 🧠 Tricky Interview Question
```jsx
<TouchableOpacity onPress={() => console.log('A')}>
  <TouchableOpacity onPress={() => console.log('B')}>
    <Text>Tap</Text>
  </TouchableOpacity>
</TouchableOpacity>
```
**Q: Text पर tap करने से क्या print होगा?**

Answer: सिर्फ **B** print होगा। RN का touch responder system सबसे अंदर (deepest) वाले responder को event देता है और वह touch "claim" कर लेता है, parent का `onPress` नहीं चलता (web की तरह bubbling नहीं होती)। Parent को भी चलाना हो तो child के `onPress` में खुद parent function call करो।

---

## ⚫ Interview Questions + Answers
Q1: `activeOpacity` क्या है?
A1: दबे हुए state में children की opacity (0 से 1)। Default 0.2।

Q2: TouchableOpacity बनाम Pressable?
A2: Pressable नया और ज़्यादा flexible है (pressed state पर style function, `android_ripple`, `hitSlop`, `pressRetentionOffset`)। RN docs अब Pressable recommend करते हैं; TouchableOpacity maintained है पर simple fade तक सीमित।

Q3: `disabled` देने पर क्या होता है?
A3: onPress नहीं चलता। Visual बदलाव खुद style से करना पड़ता है।

Q4: Long press कैसे?
A4: `onLongPress` और `delayLongPress` (ms)।

Q5: Android पर ripple चाहिए तो?
A5: `TouchableNativeFeedback` या `Pressable` का `android_ripple` prop।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Simple tap + fade feedback चाहिए
- Custom designed button / card

❌ Avoid when:
- Android ripple या pressed-state का custom style चाहिए (Pressable)
- Text पर inline link (nested `Text onPress`)
- Native look वाला system button (`Button`)

---

## 📊 Visual Diagram
```
Normal:        Pressed (activeOpacity 0.2):     Released:
┌────────┐     ┌────────┐                       ┌────────┐
│  ADD   │ →   │  ADD   │ (फीका)           →    │  ADD   │ + onPress()
└────────┘     └────────┘                       └────────┘
opacity 1      opacity 0.2                      opacity 1
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| onPress | Tap callback | tap पर function |
| activeOpacity | Opacity while pressed | दबे समय की opacity |
| hitSlop | Extra touch area | अतिरिक्त touch जगह |
| delayLongPress | ms for long press | long press का समय |
| Responder system | Decides which view gets touch | touch किसे मिले यह तय करता है |

---

## ⚡ 3-Line Summary
English:
1. TouchableOpacity makes any view tappable with a fade effect.
2. Use `activeOpacity`, `disabled`, `hitSlop` and accessibility props.
3. Pressable is the modern alternative for ripple and custom pressed styles.

Hindi:
1. TouchableOpacity किसी भी view को tappable बनाता है, fade effect के साथ।
2. `activeOpacity`, `disabled`, `hitSlop`, accessibility props use करो।
3. Ripple और custom pressed style के लिए Pressable modern विकल्प है।

---

## ➡️ Next Topic
**31. TouchableHighlight** — दबने पर background रंग बदलने वाला touchable।
