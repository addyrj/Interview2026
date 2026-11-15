# 52. Platform Specific Styling
# हिंदी में: Platform के हिसाब से Styling
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs)। सब कुछ core `Platform` API से।

---

## 🔵 Simple Definition (English)
Platform-specific styling means giving different style values to Android and iOS inside the same code, using `Platform.OS`, `Platform.select` or `StyleSheet.create` with conditional spreads.

## 🔵 सरल परिभाषा (Hindi)
Platform-specific styling का मतलब एक ही code में Android और iOS को अलग style देना। इसके लिए `Platform.OS`, `Platform.select` या `StyleSheet.create` में conditional spread इस्तेमाल करते हैं।

---

## 🔴 Problem it Solves
```
❌ Shadow: iOS पर shadow* props, Android पर elevation — एक जैसा नहीं चलता
❌ Fonts, ripple, header height, padding हर OS पर अलग दिखते हैं
❌ दोनों के लिए अलग component बनाना बेकार दोहराव है
```

## 🔴 यह क्यों बना? (Hindi)
```
दोनों OS के design guidelines अलग हैं (Material vs Human Interface)।
User को अपने OS जैसा लगे, इसलिए थोड़े-बहुत style अलग रखते हैं।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → import { Platform } from 'react-native'
Step 2 → Platform.OS === 'ios' / 'android' से सीधी शर्त
Step 3 → Platform.select({ ios: {...}, android: {...}, default: {...} })
Step 4 → StyleSheet.create के अंदर ...Platform.select(...) spread करो
Step 5 → बड़े फ़र्क के लिए अलग files (.ios.js / .android.js) → Topic 54
Step 6 → दोनों OS पर test करो
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Platform import करो
Step 2 → Platform.OS से शर्त
Step 3 → Platform.select({ ios, android, default })
Step 4 → StyleSheet.create के अंदर spread करो
Step 5 → बड़े फ़र्क पर अलग files (Topic 54)
Step 6 → दोनों OS पर test करो
```

---

## 🟡 Real World Example
**Zomato** card की shadow: iOS पर soft `shadowRadius`, Android पर `elevation`। **Paytm** में Android पर button को ripple और iOS पर opacity feedback। **WhatsApp** का header height/title alignment दोनों OS पर अलग।

## 🟡 Real Example Hindi mein
Zomato के card पर iOS में हल्की shadow आती है पर Android में वही `elevation: 4` से बनती है, इसलिए दोनों के लिए अलग style देते हैं।

---

## 💻 Code Example — Basic
```jsx
// Basic: Platform.select से shadow
import React from 'react';                                      // React
import { View, Text, Platform, StyleSheet } from 'react-native'; // core

export default function Card() {
  return (
    <View style={styles.card}>
      <Text>Same code, अलग style</Text>{/* दोनों OS */}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    margin: 20, padding: 16, borderRadius: 12, backgroundColor: '#fff', // common style
    ...Platform.select({                                        // OS-specific हिस्सा
      ios: {
        shadowColor: '#000',                                    // iOS shadow रंग
        shadowOffset: { width: 0, height: 2 },                  // shadow की जगह
        shadowOpacity: 0.2,                                     // पारदर्शिता
        shadowRadius: 6,                                        // blur
      },
      android: { elevation: 4 },                                // Android shadow
      default: {},                                              // web आदि के लिए
    }),
  },
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: Reusable platform button — ripple (Android) vs opacity (iOS), safe fonts, hitSlop
import React from 'react';                                      // React
import { Pressable, Text, Platform, StyleSheet } from 'react-native'; // core

// Android ripple config, iOS में ripple नहीं होता
const rippleConfig = Platform.OS === 'android'
  ? { color: 'rgba(255,255,255,0.3)', borderless: false }       // Material ripple
  : undefined;                                                   // iOS पर undefined

export default function PrimaryButton({ title, onPress, disabled }) {
  return (
    <Pressable
      onPress={onPress}                                          // tap callback
      disabled={disabled}                                        // बंद
      android_ripple={rippleConfig}                              // सिर्फ Android
      hitSlop={8}                                                // छोटे button का touch क्षेत्र बढ़ाओ
      style={({ pressed }) => [
        styles.btn,
        Platform.OS === 'ios' && pressed && { opacity: 0.6 },    // iOS: दबने पर opacity
        disabled && styles.disabled,                             // disabled look
      ]}
      accessibilityRole="button"                                 // screen reader
    >
      <Text style={styles.text}>{title}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  btn: {
    backgroundColor: '#e23744', paddingVertical: 14, paddingHorizontal: 20, borderRadius: Platform.OS === 'ios' ? 10 : 6, // OS अनुसार corner
    alignItems: 'center',
    overflow: Platform.OS === 'android' ? 'hidden' : 'visible', // ripple clip करने के लिए
  },
  text: {
    color: '#fff', fontSize: 16, fontWeight: '700',
    fontFamily: Platform.select({ ios: 'System', android: 'sans-serif-medium', default: undefined }), // system fonts
  },
  disabled: { opacity: 0.5 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Shadow | `elevation` | `shadowColor`, `shadowOffset`, `shadowOpacity`, `shadowRadius` |
| Touch feedback | `android_ripple` | `opacity` (Pressable `pressed`) |
| System font | Roboto (`sans-serif` आदि) | San Francisco (`System`) |
| Text vertical padding | `includeFontPadding` (Android only) | लागू नहीं |
| `textAlignVertical` | ✅ | ❌ |
| Header/nav height | ~56dp | ~44pt + safe area |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Platform API वही; app.json में OS-specific config भी रख सकते हो
// app.json → { "expo": { "ios": {...}, "android": {...} } }
import { Platform } from 'react-native';
const pad = Platform.OS === 'ios' ? 20 : 12;
```
CLI way:
```jsx
// वही Platform API; native config अलग files में (Info.plist / AndroidManifest.xml)
import { Platform } from 'react-native';
const pad = Platform.OS === 'ios' ? 20 : 12;
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `elevation` iOS पर और `shadow*` Android पर लगाना
✅ Correct: `Platform.select` से अलग-अलग दो।

❌ Mistake 2: `Platform.OS` की जगह ज़्यादा जगह `if` बिखेरना
✅ Correct: Style एक जगह (`StyleSheet`) में `Platform.select`।

❌ Mistake 3: Android `overflow: 'hidden'` से elevation की shadow काटना
✅ Correct: Outer View पर elevation, inner View पर `overflow: 'hidden'`।

---

## 🧠 Tricky Interview Question
```jsx
const s = StyleSheet.create({ box: { ...Platform.select({ ios: { shadowRadius: 5 }, android: { elevation: 5 } }) } });
```
**Q: Web (react-native-web) पर यह क्या देगा?**

Answer: `Platform.select` में `web`/`default` key नहीं है, इसलिए `undefined` मिलता है और spread का कोई असर नहीं होता; shadow नहीं दिखेगी। इसलिए `default: {...}` या `web: {...}` दें।

---

## ⚫ Interview Questions + Answers
Q1: `Platform.OS` की संभावित values?
A1: `'ios'`, `'android'` (और web/windows/macos अन्य targets पर)।

Q2: `Platform.select` और ternary में फ़र्क?
A2: select पूरी object चुनता है और `default` देता है; ternary छोटी शर्तों के लिए।

Q3: `Platform.Version` क्या है?
A3: Android में API level (number), iOS में version string।

Q4: iOS shadow overflow hidden के साथ क्यों नहीं दिखती?
A4: Clip होने से shadow कट जाती है; दो nested Views बनाओ।

Q5: कब अलग files बेहतर?
A5: जब logic/UI बहुत अलग हो (Topic 54)।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Shadow, ripple, font, छोटे spacing फ़र्क
- OS guidelines के अनुसार look

❌ Avoid when:
- हर property अलग हो (अलग files बेहतर)
- Design में दोनों OS पर समान look ज़रूरी हो

---

## 📊 Visual Diagram
```
 Single style code
        │ Platform.select
   ┌────┴─────┐
 iOS: shadow*   Android: elevation
 iOS: opacity   Android: ripple
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Platform.OS | वर्तमान OS | चल रहा OS |
| Platform.select | OS अनुसार value चुनो | चयन |
| elevation | Android shadow | Android छाया |
| android_ripple | Android touch effect | लहर effect |
| default | बाकी platforms का fallback | डिफ़ॉल्ट |

---

## ⚡ 3-Line Summary
English:
1. Use `Platform.OS` / `Platform.select` for OS-specific styles.
2. Shadows differ: iOS `shadow*`, Android `elevation`.
3. Always add `default` and test both OSes.

Hindi:
1. OS-specific style के लिए `Platform.OS` / `Platform.select`।
2. Shadow अलग: iOS `shadow*`, Android `elevation`।
3. हमेशा `default` दो और दोनों OS पर test करो।

---

## ➡️ Next Topic
**53. Platform.OS + Platform.select** — इस API की पूरी गहराई।
