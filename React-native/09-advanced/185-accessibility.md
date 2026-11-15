# 185. Accessibility in React Native
# हिंदी में: React Native में Accessibility (सबके लिए उपयोगी app)
# Platform: Both ✅ (Android ✅ TalkBack | iOS ✅ VoiceOver)

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs). `accessibilityRole`, `accessibilityLabel`, `accessibilityState`, `AccessibilityInfo` core RN में हैं — अलग install नहीं।

---

## 🔵 Simple Definition (English)
**Accessibility (a11y)** means making your app usable by people with disabilities — blind users (screen readers), low vision (large text), motor impairments (big touch targets), color blindness. In RN you add labels, roles and states so TalkBack (Android) and VoiceOver (iOS) can describe the UI.

## 🔵 सरल परिभाषा (Hindi)
**Accessibility (a11y)** यानी app ऐसा बनाना कि दिव्यांग लोग भी use कर सकें — नेत्रहीन (screen reader), कम दृष्टि (बड़ा text), हाथ की समस्या (बड़े touch targets), color blindness। RN में label, role और state देते हैं ताकि TalkBack (Android) और VoiceOver (iOS) UI को बोलकर बता सकें।

---

## 🔴 Problem it Solves
```
बिना a11y:
  ❌ Screen reader सिर्फ "button" या "unlabeled" बोलता है
  ❌ Icon-only button का मतलब पता नहीं चलता
  ❌ Small touch targets → दबाना मुश्किल
  ❌ Large font setting में layout टूटता है
  ❌ कानूनी जोखिम (कई देशों में a11y compliance ज़रूरी)
a11y के साथ:
  ✅ करोड़ों users तक पहुँच, बेहतर UX सबके लिए
```

## 🔴 यह क्यों बना? (Hindi)
```
हर user आँख/हाथ से एक जैसा app use नहीं करता।
Screen reader को UI का मतलब चाहिए — label/role देकर बताते हैं।
यह नैतिक भी है और कई बार कानूनी ज़रूरत भी।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → हर interactive element को accessible बनाओ (Pressable/Touchable default accessible)
Step 2 → accessibilityLabel दो (icon buttons में ज़रूरी)
Step 3 → accessibilityRole दो (button, link, header, image, switch...)
Step 4 → accessibilityState दो ({ disabled, selected, checked, busy, expanded })
Step 5 → accessibilityHint दो (क्या होगा दबाने पर) — optional
Step 6 → Touch target कम से कम 44x44 (iOS) / 48x48 dp (Android) रखो
Step 7 → Dynamic font scaling support (allowFontScaling default true)
Step 8 → AccessibilityInfo से screen reader status check/announce करो
Step 9 → TalkBack/VoiceOver चालू करके खुद test करो
```

## 🟢 कैसे काम करता है? (Hindi)
```
Native OS हर view का accessibility tree बनाता है।
RN के props उस tree में label/role/state भरते हैं।
Screen reader उसी tree को पढ़कर बोलता है।
```

---

## 🟡 Real World Example
**Paytm** का "Pay" बटन सिर्फ ₹ icon है — `accessibilityLabel="Pay money"` न हो तो TalkBack सिर्फ "button" बोलेगा। **Swiggy** का cart badge "3" — label "Cart, 3 items" होना चाहिए। **Zomato** में rating stars "4.5 out of 5 stars" के रूप में पढ़े जाने चाहिए, 5 अलग star images के रूप में नहीं।

## 🟡 Real Example Hindi mein
Paytm का icon-only Pay बटन — label के बिना TalkBack सिर्फ "button" बोलेगा। Swiggy cart "3" की जगह "Cart, 3 items"। Zomato rating "4.5 out of 5 stars" एक साथ।

---

## 💻 Code Example — Basic
```jsx
import React from 'react';                                   // React for JSX
import { View, Text, Pressable, Image, StyleSheet } from 'react-native'; // RN components

export default function PayButton({ onPress, disabled }) {   // props: press handler, disabled flag
  return (
    <View>
      {/* Heading: screen reader "heading" बोलता है, navigation आसान */}
      <Text accessibilityRole="header" style={styles.title}>Send Money</Text>

      <Pressable
        onPress={onPress}                                    // action
        disabled={disabled}                                  // disables press
        accessible={true}                                    // element को accessible बनाओ
        accessibilityRole="button"                           // type: button
        accessibilityLabel="Pay money"                       // क्या पढ़ा जाए
        accessibilityHint="Opens payment confirmation"       // क्या होगा
        accessibilityState={{ disabled }}                    // dimmed/disabled बताओ
        hitSlop={8}                                          // touch area बढ़ाओ (छोटे icons के लिए)
        style={styles.btn}
      >
        {/* Decorative image — screen reader skip करे */}
        <Image
          source={{ uri: 'https://example.com/rupee.png' }}  // icon
          style={styles.icon}
          accessible={false}                                 // decorative
          importantForAccessibility="no"                     // Android: ignore
        />
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 20, fontWeight: '700' },                // heading style
  btn: { minWidth: 48, minHeight: 48, justifyContent: 'center', alignItems: 'center' }, // 48dp target
  icon: { width: 24, height: 24 },                           // small icon
});
```

## 💻 Code Example — Advanced
```jsx
import React, { useEffect, useState } from 'react';
import { View, Text, Pressable, AccessibilityInfo, Platform, StyleSheet } from 'react-native';

// Custom hook: screen reader और reduce-motion status track करो
function useA11yPrefs() {
  const [screenReader, setScreenReader] = useState(false);    // screen reader ON?
  const [reduceMotion, setReduceMotion] = useState(false);    // animations कम?

  useEffect(() => {
    let mounted = true;                                       // unmount guard
    AccessibilityInfo.isScreenReaderEnabled().then(v => mounted && setScreenReader(v)); // initial
    AccessibilityInfo.isReduceMotionEnabled().then(v => mounted && setReduceMotion(v));
    const s1 = AccessibilityInfo.addEventListener('screenReaderChanged', setScreenReader); // live updates
    const s2 = AccessibilityInfo.addEventListener('reduceMotionChanged', setReduceMotion);
    return () => { mounted = false; s1.remove(); s2.remove(); };  // cleanup listeners
  }, []);

  return { screenReader, reduceMotion };
}

export default function CartItem({ name, qty, onInc }) {
  const { screenReader } = useA11yPrefs();

  function inc() {
    onInc();                                                  // update quantity
    // Dynamic change की घोषणा: screen reader बोले
    AccessibilityInfo.announceForAccessibility(`${name} quantity ${qty + 1}`);
  }

  return (
    <View
      accessible                                              // पूरी row एक item की तरह पढ़ी जाए
      accessibilityLabel={`${name}, quantity ${qty}`}         // combined label
      accessibilityActions={[{ name: 'increment', label: 'Add one more' }]} // custom action (swipe up/down)
      onAccessibilityAction={e => {                           // action handler
        if (e.nativeEvent.actionName === 'increment') inc();
      }}
      style={styles.row}
    >
      <Text style={styles.name}>{name}</Text>
      <Text>{qty}</Text>
      <Pressable
        onPress={inc}
        accessibilityRole="button"
        accessibilityLabel={`Increase ${name}`}
        style={styles.plus}
      >
        <Text style={styles.plusTxt}>+</Text>
      </Pressable>
      {Platform.OS === 'android' && screenReader ? (          // Android-specific tweak example
        <Text accessibilityLiveRegion="polite">Qty {qty}</Text> // Android live region (auto announce)
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', padding: 12 },
  name: { flex: 1, fontSize: 16 },
  plus: { minWidth: 48, minHeight: 48, alignItems: 'center', justifyContent: 'center' },
  plusTxt: { fontSize: 22 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Screen reader | TalkBack | VoiceOver |
| Ignore element | `importantForAccessibility="no"` | `accessible={false}` / `accessibilityElementsHidden` |
| Live region | `accessibilityLiveRegion` (polite/assertive) | Not available — use `announceForAccessibility` |
| Hide children | `importantForAccessibility="no-hide-descendants"` | `accessibilityElementsHidden` |
| Min touch target | 48x48 dp | 44x44 pt |
| Modal focus | `accessibilityViewIsModal` ignore | `accessibilityViewIsModal` supported |
| Gesture to test | Two-finger swipes / explore by touch | Rotor, swipe right/left |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Core RN a11y props — setup नहीं चाहिए, Expo में वैसे ही चलते हैं
// Testing: Android emulator में TalkBack, iOS simulator में Accessibility Inspector
// expo-router / React Navigation के header भी default accessible
```
CLI way:
```jsx
// Same props। Extra tools:
// Android: Accessibility Scanner app, Android Studio layout inspector
// iOS: Xcode > Open Developer Tool > Accessibility Inspector
// कोई native config नहीं बदलता
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Icon button बिना label
✅ Correct: `accessibilityLabel="Add to cart"`

❌ Mistake 2: `<View onTouchEnd>` से button बनाना
✅ Correct: `Pressable` + `accessibilityRole="button"`

❌ Mistake 3: Fixed height text container → large font में text कट जाता
✅ Correct: `minHeight`, flexible layout, `maxFontSizeMultiplier` limit पर सोचो

❌ Mistake 4: सिर्फ color से state बताना (red = error)
✅ Correct: Text/icon + color, contrast ratio 4.5:1

❌ Mistake 5: सिर्फ simulator देखकर "done"
✅ Correct: असली device पर TalkBack/VoiceOver चलाकर test

---

## 🧠 Tricky Interview Question
```jsx
<View accessible accessibilityLabel="Card">
  <Pressable onPress={buy} accessibilityLabel="Buy now"><Text>Buy</Text></Pressable>
</View>
```
Q: Screen reader user "Buy now" button तक पहुँच पाएगा?

Answer: नहीं (आम तौर पर)। parent `accessible` है, तो वह एक single focusable unit बन जाता है और children को screen reader अलग से focus नहीं देता — खासकर iOS पर nested button unreachable हो जाता है। Fix: parent से `accessible` हटाओ, या parent को सिर्फ grouping के लिए रखो और button अलग accessible element रखो, या `accessibilityActions` से parent पर ही action दो।

---

## ⚫ Interview Questions + Answers
Q1: `accessibilityLabel` और `accessibilityHint` का फर्क?
A1: Label = element क्या है/नाम; Hint = दबाने पर क्या होगा। Label ज़रूरी है, hint optional।

Q2: `accessible={true}` क्या करता है?
A2: View को screen reader के लिए एक focusable element बनाता है और उसके children को group कर देता है।

Q3: Dynamic content (toast) की घोषणा कैसे?
A3: `AccessibilityInfo.announceForAccessibility(msg)` (दोनों platform) या Android पर `accessibilityLiveRegion`.

Q4: Large font support कैसे जाँचें?
A4: Device settings में font size/Display size बढ़ाओ; text clip न हो; `allowFontScaling` default true रखो; ज़रूरत हो तो `maxFontSizeMultiplier`।

Q5: Reduce motion कैसे respect करें?
A5: `AccessibilityInfo.isReduceMotionEnabled()` / event सुनो और animations हटाओ/छोटी करो (Reanimated में भी `useReducedMotion`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- हमेशा — हर public app में (खासकर banking, government, e-commerce)
- Icon-only controls, custom components, dynamic updates

❌ Avoid when:
- Decorative elements को label देना (noise) — उन्हें hide करो
- हर Text पर बेवजह `accessible` लगाना

---

## 📊 Visual Diagram
```
  RN props  ──►  Native accessibility tree  ──►  Screen reader
  (label, role,      (Android AccessibilityNodeInfo     TalkBack /
   state, hint)       iOS UIAccessibility)              VoiceOver
                                                         │
                          user सुनता है: "Pay money, button"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| a11y | Accessibility shorthand | सुगम्यता |
| TalkBack | Android screen reader | Android का screen reader |
| VoiceOver | iOS screen reader | iOS का screen reader |
| accessibilityRole | Element type | Element का प्रकार |
| accessibilityLabel | Spoken name | बोला जाने वाला नाम |
| Touch target | Tappable area | दबाने का क्षेत्र |

---

## ⚡ 3-Line Summary
English: Accessibility lets screen readers and all users use your app.
Add labels, roles, states; keep 44-48 size targets; support large fonts and reduce motion.
Always test with TalkBack and VoiceOver on a real device.

Hindi: Accessibility से सभी users, screen reader वाले भी, app चला पाते हैं।
Label, role, state दो; 44-48 size के targets; बड़ा font और reduce motion सपोर्ट करो।
असली device पर TalkBack/VoiceOver से test करो।

---

## ➡️ Next Topic
**186. Internationalization (i18n) in RN** — Hindi, English, Tamil जैसी कई भाषाओं में app चलाना।

---
