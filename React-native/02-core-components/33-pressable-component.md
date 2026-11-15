# 33. Pressable Component (Modern)
# हिंदी में: Pressable Component (आधुनिक Touchable)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 के हिसाब से examples (check current docs — APIs change between SDKs). `Pressable` RN 0.63 से core में है।

---

## 🔵 Simple Definition (English)
`Pressable` is React Native's modern, flexible component for detecting presses. It wraps any child, gives you the `pressed` state to style it, supports `android_ripple`, `hitSlop`, long press and more. It is the recommended replacement for the older Touchable components.

## 🔵 सरल परिभाषा (Hindi)
`Pressable` React Native का आधुनिक और flexible component है जो press detect करता है। यह किसी भी child को wrap करता है, `pressed` state देता है जिससे style बदल सकते हो, `android_ripple`, `hitSlop`, long press जैसी सुविधाएँ देता है। पुराने Touchable components की जगह यही recommend होता है।

---

## 🔴 Problem it Solves
```
❌ TouchableOpacity → सिर्फ fade
❌ TouchableHighlight → एक child, underlay
❌ TouchableNativeFeedback → सिर्फ Android
❌ तीन अलग APIs, तीन अलग व्यवहार
```

## 🔴 यह क्यों बना? (Hindi)
```
तीन अलग Touchable components थे, सब सीमित।
Pressable एक ही component:
✅ pressed state से कोई भी style (fade, colour, scale)
✅ Android ripple + iOS style एक ही code में
✅ onPressIn/onPressOut/onLongPress/hitSlop/pressRetentionOffset
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → <Pressable onPress={fn}> में children रखो
Step 2 → style या children को function बना सकते हो: ({ pressed }) => ...
Step 3 → उँगली रखने पर onPressIn, pressed = true
Step 4 → उँगली हटाने पर onPressOut, pressed = false
Step 5 → बाहर खिसकाए बिना हटाई तो onPress
Step 6 → लंबा दबाने पर onLongPress (delayLongPress)
Step 7 → Android पर android_ripple से native ripple
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Pressable में children रखो
Step 2 → style/children function हो सकते हैं: ({ pressed }) => ...
Step 3 → उँगली रखते ही onPressIn और pressed = true
Step 4 → हटते ही onPressOut और pressed = false
Step 5 → सही जगह उठाई तो onPress
Step 6 → देर तक दबाने पर onLongPress
Step 7 → Android पर android_ripple से ripple
```

---

## 🟡 Real World Example
**Zomato** का "ADD" button दबने पर हल्का छोटा (scale) होता है। **Swiggy** के cart का "+ / −" stepper, **Paytm** के UPI tiles (Android पर ripple, iOS पर fade), **Instagram** का like button — सब में pressed state पर अलग style होती है। `Pressable` इन सबके लिए एक ही component देता है।

## 🟡 Real Example Hindi mein
Zomato के ADD button को दबाओ तो थोड़ा छोटा होता है। Paytm के UPI tiles Android पर ripple और iOS पर fade दिखाते हैं। Pressable से यह सब एक ही code में हो जाता है।

---

## 💻 Code Example — Basic
```jsx
// Basic Pressable — pressed state से style बदलना
import React, { useState } from 'react';
import { Pressable, Text, View, StyleSheet } from 'react-native';

export default function BasicPressable() {
  const [count, setCount] = useState(0);                         // counter

  return (
    <View style={styles.container}>
      <Pressable
        onPress={() => setCount(c => c + 1)}                     // tap पर +1
        // style को function बनाओ: pressed true हो तो अलग रंग
        style={({ pressed }) => [styles.btn, pressed && styles.btnPressed]}
        android_ripple={{ color: '#ffffff55' }}                  // सिर्फ Android पर ripple
      >
        {/* children भी function हो सकता है */}
        {({ pressed }) => (
          <Text style={styles.text}>{pressed ? 'Pressing...' : `Taps: ${count}`}</Text>
        )}
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 24 },
  btn: { backgroundColor: '#e23744', padding: 14, borderRadius: 10, alignItems: 'center', overflow: 'hidden' }, // overflow: ripple clip
  btnPressed: { opacity: 0.8, transform: [{ scale: 0.97 }] },    // दबने पर थोड़ा छोटा
  text: { color: '#fff', fontWeight: '700' },
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: reusable AppButton — loading, disabled, hitSlop, long press, a11y, haptic-safe
import React, { useCallback } from 'react';
import { Pressable, Text, ActivityIndicator, StyleSheet, Platform } from 'react-native';

export default function AppButton({
  title, onPress, onLongPress, loading = false, disabled = false, variant = 'primary',
}) {
  const isDisabled = disabled || loading;                        // दोनों में बंद

  // हर press पर safe wrapper — error catch
  const handlePress = useCallback((e) => {
    if (isDisabled) return;                                      // बंद है तो कुछ नहीं
    try {
      onPress?.(e);                                              // user का handler
    } catch (err) {
      console.warn('Button handler error', err);                 // crash रोको
    }
  }, [isDisabled, onPress]);

  return (
    <Pressable
      onPress={handlePress}
      onLongPress={onLongPress}
      delayLongPress={400}                                       // 400ms
      disabled={isDisabled}
      hitSlop={10}                                               // tap area चारों तरफ 10
      pressRetentionOffset={{ top: 20, bottom: 20, left: 20, right: 20 }} // थोड़ा खिसकने पर भी active
      android_ripple={{ color: '#ffffff44', borderless: false }} // Android ripple
      accessibilityRole="button"
      accessibilityLabel={title}
      accessibilityState={{ disabled: isDisabled, busy: loading }}
      style={({ pressed }) => [
        styles.base,
        variant === 'secondary' ? styles.secondary : styles.primary,
        pressed && Platform.OS === 'ios' && { opacity: 0.7 },    // iOS पर fade (Android पर ripple है)
        isDisabled && styles.disabled,
      ]}
    >
      {loading
        ? <ActivityIndicator color="#fff" />
        : <Text style={[styles.text, variant === 'secondary' && { color: '#e23744' }]}>{title}</Text>}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: { paddingVertical: 14, paddingHorizontal: 20, borderRadius: 10, alignItems: 'center', overflow: 'hidden' },
  primary: { backgroundColor: '#e23744' },
  secondary: { backgroundColor: '#fff', borderWidth: 1, borderColor: '#e23744' },
  disabled: { opacity: 0.5 },
  text: { color: '#fff', fontWeight: '700', fontSize: 16 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Ripple | `android_ripple` ✅ | ❌ ignore |
| Default feedback | कोई नहीं (ripple खुद जोड़ो) | कोई नहीं (pressed style खुद दो) |
| Min touch size guideline | 48dp | 44pt |
| `android_disableSound` | ✅ | ❌ |
| `hitSlop` | ✅ | ✅ |
| Press behaviour | वही | वही |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Core component है; Expo Go में सीधे चलता है
import { Pressable, Text } from 'react-native';
<Pressable onPress={() => {}} style={({ pressed }) => ({ opacity: pressed ? 0.6 : 1 })}>
  <Text>Press</Text>
</Pressable>
```
CLI way:
```jsx
// CLI में भी वही; कोई native setup नहीं। Gesture-heavy काम के लिए react-native-gesture-handler (अलग से)
import { Pressable, Text } from 'react-native';
<Pressable onPress={() => {}} style={({ pressed }) => ({ opacity: pressed ? 0.6 : 1 })}>
  <Text>Press</Text>
</Pressable>
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: कोई visual feedback न देना (Pressable में default कुछ नहीं होता)
✅ Correct: `style={({pressed}) => ...}` या `android_ripple`।

❌ Mistake 2: Ripple rounded corners से बाहर
✅ Correct: Pressable style में `overflow: 'hidden'` + `borderRadius`।

❌ Mistake 3: `style={[a, pressed && b]}` बिना function (pressed undefined)
✅ Correct: `style={({ pressed }) => [a, pressed && b]}`

❌ Mistake 4: छोटा tap target
✅ Correct: `hitSlop` या padding ≥ 44–48।

---

## 🧠 Tricky Interview Question
```jsx
<Pressable onPress={() => console.log('press')}
           onPressIn={() => console.log('in')}
           onPressOut={() => console.log('out')}
           onLongPress={() => console.log('long')}>
```
**Q: Normal short tap पर क्रम क्या होगा? और 1 सेकंड दबाने पर?**

Answer: Short tap: `in → out → press` (RN में onPressOut, onPress से पहले fire होता है)। लंबा दबाने (delayLongPress default 500ms): `in → long → out` — और `onPress` **नहीं** चलता (long press fire होने के बाद)। यह क्रम pressed-state animation और double action bugs के लिए अहम है। (क्रम RN version पर थोड़ा निर्भर हो सकता है — अपनी version पर console से जाँचो।)

---

## ⚫ Interview Questions + Answers
Q1: Pressable बनाम TouchableOpacity?
A1: Pressable अधिक flexible है: pressed state, ripple, hitSlop, retention offset। TouchableOpacity सिर्फ fade देता है। Docs में Pressable recommended है।

Q2: `pressRetentionOffset` क्या है?
A2: Press के बाद उँगली view से कितनी दूर खिसक सकती है और फिर भी press active रहे।

Q3: `android_ripple` के options?
A3: `color`, `borderless`, `radius`, `foreground`।

Q4: `hitSlop` क्यों?
A4: छोटे icons का tap area बढ़ाने के लिए (accessibility + UX)।

Q5: Pressable में style function क्यों?
A5: `pressed` बूलियन पाकर dynamic style बनाने के लिए, बिना state manage किए।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- लगभग हर नया button/card/row
- Android ripple + iOS fade साथ चाहिए
- Custom pressed animation

❌ Avoid when:
- Complex gestures (drag, swipe) → Gesture Handler
- System look का simple button (`Button`)
- Text के अंदर inline link (nested `Text onPress`)

---

## 📊 Visual Diagram
```
touch down ──► onPressIn  ──► pressed = true  (style बदली)
   │
   ├─ short ──► touch up ──► onPressOut ──► onPress ──► pressed=false
   │
   └─ long (500ms) ──► onLongPress ──► touch up ──► onPressOut
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| pressed | True while finger down | उँगली दबी होने की state |
| android_ripple | Android ripple config | Android ripple settings |
| hitSlop | Extra touch area | अतिरिक्त touch area |
| pressRetentionOffset | Allowed finger drift | उँगली खिसकने की छूट |
| onPressIn/Out | Down/up events | दबना/छूटना events |

---

## ⚡ 3-Line Summary
English:
1. Pressable is the modern, flexible replacement for Touchable components.
2. Use the `pressed` state in style/children and `android_ripple` for Android.
3. Add accessibility props and a large enough touch target.

Hindi:
1. Pressable पुराने Touchable components का आधुनिक, flexible विकल्प है।
2. style/children में `pressed` state और Android के लिए `android_ripple` use करो।
3. Accessibility props और बड़ा touch target ज़रूर दो।

---

## ➡️ Next Topic
**34. Button Component** — सबसे सरल built-in button और उसकी सीमाएँ।
