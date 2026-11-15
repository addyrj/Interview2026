# 32. TouchableNativeFeedback
# हिंदी में: TouchableNativeFeedback (Android का Ripple Effect)
# Platform: Android ✅ | iOS ❌ (सिर्फ Android)

> Expo SDK 52 / React Native 0.76 के हिसाब से examples (check current docs — APIs change between SDKs). iOS पर यह component काम नहीं करता — इसलिए आजकल `Pressable` + `android_ripple` ज़्यादा use होता है।

---

## 🔵 Simple Definition (English)
`TouchableNativeFeedback` is an **Android-only** wrapper that gives the native Material **ripple** effect when a view is pressed. It must have exactly one child `View`, and you choose the ripple with the `background` prop.

## 🔵 सरल परिभाषा (Hindi)
`TouchableNativeFeedback` **सिर्फ Android** के लिए है। दबाने पर Material Design का **ripple** (लहर जैसा) effect देता है। इसमें एक ही child `View` होना चाहिए और ripple का type `background` prop से चुनते हैं।

---

## 🔴 Problem it Solves
```
❌ Android users को ripple की आदत है (Gmail, Play Store, Paytm)
❌ TouchableOpacity में सिर्फ fade होता है → Android पर "non-native" feel
❌ Ripple खुद बनाना (Animated circle) मुश्किल
```

## 🔴 यह क्यों बना? (Hindi)
```
Android के Material Design में हर tap पर ripple होती है।
TouchableOpacity की fade Android पर अजीब लगती है।
इसलिए RN ने Android का native ripple (RippleDrawable) सीधे expose किया।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Child View को TouchableNativeFeedback में लपेटो
Step 2 → background prop में ripple चुनो:
         TouchableNativeFeedback.Ripple(color, borderless, radius)
Step 3 → Android का RippleDrawable child के background/foreground पर लगता है
Step 4 → Touch पर ripple touch-point से फैलती है
Step 5 → उँगली उठाने पर onPress चलता है
Step 6 → iOS पर यह काम नहीं करता → Platform check / Pressable
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → child View को wrap करो
Step 2 → background में Ripple(color, borderless, radius) दो
Step 3 → Android का native RippleDrawable लगता है
Step 4 → जहाँ touch हुआ वहाँ से ripple फैलती है
Step 5 → उँगली उठाने पर onPress
Step 6 → iOS पर नहीं चलता → Platform check या Pressable
```

---

## 🟡 Real World Example
**Paytm** Android app के recharge tiles, **Zomato** के category chips और **Swiggy** के Android bottom sheet options दबाने पर ripple दिखती है। Google Pay जैसे Material apps में हर list item पर यही effect है।

## 🟡 Real Example Hindi mein
Paytm Android के recharge tiles दबाओ तो जहाँ उँगली रखी वहाँ से लहर फैलती है — यही native ripple है।

---

## 💻 Code Example — Basic
```jsx
// Basic: Android ripple — iOS पर fallback TouchableOpacity
import React from 'react';
import { TouchableNativeFeedback, TouchableOpacity, View, Text, Platform, StyleSheet } from 'react-native';

export default function RippleButton({ title, onPress }) {
  // iOS पर TouchableNativeFeedback नहीं चलेगा, इसलिए fallback
  const Touchable = Platform.OS === 'android' ? TouchableNativeFeedback : TouchableOpacity;

  return (
    <Touchable
      onPress={onPress}                                                    // tap
      // background सिर्फ Android के लिए (iOS पर prop ignore)
      background={Platform.OS === 'android'
        ? TouchableNativeFeedback.Ripple('#ffffff55', false)               // हल्की सफ़ेद ripple
        : undefined}
    >
      {/* एक ही child View — ज़रूरी */}
      <View style={styles.btn}>
        <Text style={styles.text}>{title}</Text>
      </View>
    </Touchable>
  );
}

const styles = StyleSheet.create({
  btn: { backgroundColor: '#00baf2', paddingVertical: 12, paddingHorizontal: 24, borderRadius: 8 },
  text: { color: '#fff', fontWeight: '700' },
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: version check, borderless icon ripple, foreground ripple, rounded corners fix
import React from 'react';
import { TouchableNativeFeedback, View, Text, Platform, StyleSheet } from 'react-native';

// Android 5.0 (API 21) से पहले ripple नहीं था; आजकल लगभग सभी devices पर है
const supportsRipple = Platform.OS === 'android' && Platform.Version >= 21;

export function Tile({ label, onPress }) {
  // रंग-भरी ripple, bounded (borderless=false)
  const bg = supportsRipple
    ? TouchableNativeFeedback.Ripple('#00000022', false)   // हल्की काली ripple
    : TouchableNativeFeedback.SelectableBackground();       // पुराने devices के लिए fallback

  return (
    // बाहर overflow hidden → ripple rounded corners के अंदर ही रहे
    <View style={styles.tileWrap}>
      <TouchableNativeFeedback onPress={onPress} background={bg} useForeground={TouchableNativeFeedback.canUseNativeForeground()}>
        <View style={styles.tile}>
          <Text>{label}</Text>
        </View>
      </TouchableNativeFeedback>
    </View>
  );
}

export function IconTap({ onPress, children }) {
  return (
    // borderless ripple: icon के बाहर तक फैलती है (दूसरा arg true)
    <TouchableNativeFeedback
      onPress={onPress}
      background={TouchableNativeFeedback.Ripple('#00000033', true, 24)} // radius 24
    >
      <View style={styles.icon}>{children}</View>
    </TouchableNativeFeedback>
  );
}

const styles = StyleSheet.create({
  tileWrap: { borderRadius: 12, overflow: 'hidden', margin: 8 },  // ripple clip
  tile: { padding: 20, backgroundColor: '#fff' },
  icon: { width: 48, height: 48, alignItems: 'center', justifyContent: 'center' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Support | ✅ पूरा | ❌ नहीं (render error / कोई काम नहीं) |
| Ripple | Native RippleDrawable | N/A |
| Alternative | `Pressable android_ripple` | `Pressable` + pressed style / TouchableOpacity |
| Min Android version | API 21 (ripple) | N/A |
| `useForeground` | ✅ (API 23+ foreground drawable) | N/A |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo Go में Android पर चलता है; iOS पर नहीं। Cross-platform के लिए Pressable:
import { Pressable, Text } from 'react-native';
<Pressable android_ripple={{ color: '#00000022' }} onPress={() => {}}>
  <Text>Tap</Text>
</Pressable>
```
CLI way:
```jsx
// CLI में भी वही core component, कोई extra native setup नहीं
import { TouchableNativeFeedback, View, Text } from 'react-native';
<TouchableNativeFeedback background={TouchableNativeFeedback.Ripple('#0003', false)} onPress={() => {}}>
  <View><Text>Tap</Text></View>
</TouchableNativeFeedback>
// iOS build पर यह screen खोलोगे तो दिक्कत → Platform.OS check ज़रूर
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: iOS पर बिना check के use करना
✅ Correct: `Platform.OS === 'android'` check या `Pressable`।

❌ Mistake 2: एक से ज़्यादा children
✅ Correct: एक `View` में सब रखो।

❌ Mistake 3: Rounded card पर ripple corners से बाहर निकलना
✅ Correct: parent पर `overflow: 'hidden'` और `borderRadius`।

❌ Mistake 4: Child के बजाय बाहरी `style` prop की उम्मीद करना
✅ Correct: style child `View` पर दो (TouchableNativeFeedback खुद style नहीं देता)।

---

## 🧠 Tricky Interview Question
**Q: एक ही code base से Android पर ripple और iOS पर fade कैसे दोगे, बिना दो अलग components लिखे?**

Answer: सबसे साफ तरीका `Pressable` है: `android_ripple` सिर्फ Android पर लगता है, और `style={({pressed}) => ...}` से iOS पर opacity बदल सकते हैं। दूसरा तरीका: `const Touchable = Platform.OS === 'android' ? TouchableNativeFeedback : TouchableOpacity;`। `TouchableNativeFeedback` सीधे iOS पर नहीं चलता, यही असल जाल है।

---

## ⚫ Interview Questions + Answers
Q1: `Ripple()` के arguments?
A1: `Ripple(color, borderless, rippleRadius?)`। borderless true हो तो view की सीमा से बाहर तक फैलती है।

Q2: `SelectableBackground` क्या है?
A2: Android की default selectable item background (theme के हिसाब से ripple)।

Q3: `useForeground` क्यों?
A3: Ripple child के ऊपर (foreground) draw हो, ताकि image जैसे content पर भी दिखे। `canUseNativeForeground()` से (Android 23+) check करो।

Q4: iOS पर क्या होगा?
A4: यह Android-specific है; iOS पर नहीं चलता — fallback ज़रूरी।

Q5: इसकी जगह क्या?
A5: `Pressable` + `android_ripple`।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- सिर्फ Android app/screen हो
- Native Material ripple चाहिए

❌ Avoid when:
- Cross-platform shared code (Pressable लें)
- iOS भी support करना हो
- Pressed state पर custom styling

---

## 📊 Visual Diagram
```
Android tap:                    iOS tap:
   ( ● )  ← touch point          (TouchableNativeFeedback ❌)
  (  ◯   )  ripple फैलती है       → Pressable / TouchableOpacity
 (    ◯    )
┌──────────────┐
│    Tile      │  overflow:hidden से ripple अंदर रहती है
└──────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Ripple | Material touch wave | लहर जैसा effect |
| borderless | Ripple goes outside bounds | सीमा के बाहर तक |
| SelectableBackground | Default theme ripple | theme की default ripple |
| useForeground | Draw ripple above child | child के ऊपर ripple |
| RippleDrawable | Android native class | Android का native class |

---

## ⚡ 3-Line Summary
English:
1. TouchableNativeFeedback gives native Android ripple; iOS is not supported.
2. Use `background={TouchableNativeFeedback.Ripple(color, borderless)}` with one child View.
3. Prefer `Pressable` with `android_ripple` for cross-platform code.

Hindi:
1. TouchableNativeFeedback Android की native ripple देता है; iOS पर नहीं चलता।
2. `background={TouchableNativeFeedback.Ripple(color, borderless)}` और एक child View use करो।
3. Cross-platform के लिए `Pressable` + `android_ripple` बेहतर है।

---

## ➡️ Next Topic
**33. Pressable Component (Modern)** — सभी touchables का आधुनिक और flexible विकल्प।
