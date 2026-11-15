# 22. Text Component
# हिंदी में: Text Component (टेक्स्ट दिखाने वाला Component)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 के हिसाब से examples (check current docs — APIs change between SDKs). `Text` core RN component है, कोई extra install नहीं चाहिए।

---

## 🔵 Simple Definition (English)
`<Text>` is the **only** core component that can display text in React Native. It supports styling, nesting, truncation (`numberOfLines`) and touch handling (`onPress`). Every string must live inside a `<Text>`.

## 🔵 सरल परिभाषा (Hindi)
`<Text>` React Native का **एकमात्र** core component है जो text दिखा सकता है। इसमें styling, nesting, text को काटना (`numberOfLines`) और touch (`onPress`) support है। हर string किसी न किसी `<Text>` के अंदर ही होनी चाहिए।

---

## 🔴 Problem it Solves
```
BEFORE (web thinking):
❌ <div>Hello</div>, <p>, <h1>, <span> सब RN में नहीं चलते
❌ Native side पर text के लिए अलग widget चाहिए
   (Android: TextView, iOS: UILabel)
❌ Long text screen से बाहर जाता है, उसे cut करना पड़ता है
❌ Text के अंदर अलग-अलग style (bold + normal) चाहिए
```
`Text` एक ही API देता है जो दोनों platforms के native text widget में map होता है।

## 🔴 यह क्यों बना? (Hindi)
```
Web में हमारे पास p, h1, span, strong थे।
Native में सिर्फ TextView / UILabel होता है।
RN ने एक unified <Text> बनाया:
✅ Same code → दोनों platforms
✅ numberOfLines / ellipsizeMode से truncate
✅ Nested <Text> से bold/colored हिस्से
✅ onPress से link जैसा behaviour
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → आप <Text style={...}>Hello</Text> लिखते हो
Step 2 → React Native इसे native text view में map करता है
         Android → TextView | iOS → UILabel / NSAttributedString
Step 3 → Yoga layout engine text की size measure करता है
Step 4 → Style (fontSize, color, fontWeight) native view पर लगती है
Step 5 → Nested <Text> एक attributed string बन जाता है
Step 6 → numberOfLines पहुँचने पर ellipsis (...) लगता है
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → <Text> में string और style लिखो
Step 2 → RN इसे Android TextView / iOS UILabel बनाता है
Step 3 → Layout engine text की width-height निकालता है
Step 4 → fontSize, color आदि native view पर apply होते हैं
Step 5 → अंदर का <Text> parent text का हिस्सा बन जाता है
Step 6 → numberOfLines के बाद "..." दिखता है
```

---

## 🟡 Real World Example
**Zomato** restaurant card: restaurant name एक line में truncate होता है (`numberOfLines={1}`), जबकि "₹250 for one" के अंदर price bold होता है (nested Text). **Swiggy** में "Order #1234 • Delivered" जैसी line में order id bold और status green होता है। **Paytm** में terms & conditions का "Read more" link `onPress` वाला Text है।

## 🟡 Real Example Hindi mein
Zomato के card में restaurant का नाम लंबा हो तो एक line में कटकर "..." दिखता है। "₹250 for one" में सिर्फ price bold है — यह nested Text से होता है। Paytm में "Read more" भी एक छोटा `Text` है जिस पर `onPress` लगा है।

---

## 💻 Code Example — Basic
```jsx
// Basic Text example — Android + iOS दोनों पर चलता है
import React from 'react';                       // React import
import { View, Text, StyleSheet } from 'react-native'; // core components

export default function BasicText() {            // component शुरू
  return (
    // बाहर का container
    <View style={styles.container}>
      {/* साधारण text */}
      <Text style={styles.title}>Zomato Gold</Text>
      {/* nested text: अंदर का Text parent की style inherit करता है */}
      <Text style={styles.body}>
        Price:{' '}
        <Text style={styles.bold}>₹250</Text>
        {' '}for one
      </Text>
      {/* सिर्फ 2 lines दिखाओ, बाकी "..." */}
      <Text numberOfLines={2} style={styles.body}>
        Butter Chicken, Naan, Dal Makhani, Paneer Tikka, Biryani, Raita,
        Gulab Jamun aur bahut kuch jo ek line mein nahi aayega.
      </Text>
    </View>
  );
}

// Styles एक जगह
const styles = StyleSheet.create({
  container: { padding: 16 },                    // चारों तरफ gap
  title: { fontSize: 22, fontWeight: '700', color: '#222' }, // heading
  body: { fontSize: 15, color: '#555', marginTop: 8 },       // normal text
  bold: { fontWeight: '700', color: '#000' },    // bold हिस्सा
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: Read more / Read less + selectable + accessibility + font scaling control
import React, { useState } from 'react';          // state के लिए
import { View, Text, Platform, StyleSheet, Linking } from 'react-native';

export default function ExpandableText({ text, limit = 3 }) {
  const [expanded, setExpanded] = useState(false);       // expand state

  // link खोलने का helper — error handle किया
  const openTerms = async () => {
    try {
      await Linking.openURL('https://example.com/terms'); // browser में खोलो
    } catch (e) {
      console.warn('Link नहीं खुला', e);                   // error log
    }
  };

  return (
    <View style={styles.box}>
      <Text
        numberOfLines={expanded ? undefined : limit}     // expanded हो तो सीमा हटाओ
        ellipsizeMode="tail"                             // अंत में ... लगाओ
        selectable                                       // long press से copy
        maxFontSizeMultiplier={1.3}                      // user का बड़ा font layout न तोड़े
        style={styles.text}
      >
        {text}
      </Text>

      {/* Read more toggle — Text पर onPress */}
      <Text
        accessibilityRole="button"                       // screen reader को बताओ
        onPress={() => setExpanded(v => !v)}             // toggle
        style={styles.link}
      >
        {expanded ? 'Read less' : 'Read more'}
      </Text>

      {/* Terms link */}
      <Text onPress={openTerms} style={styles.link}>Terms & Conditions</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  box: { padding: 16 },
  text: {
    fontSize: 15,
    lineHeight: 22,                                      // line gap
    color: '#333',
    // Android extra padding हटाओ (Android only prop)
    ...Platform.select({ android: { includeFontPadding: false }, ios: {} }),
  },
  link: { color: '#f97316', marginTop: 6, fontWeight: '600' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Native widget | `TextView` | `UILabel` / attributed string |
| Default font | Roboto | San Francisco |
| `includeFontPadding` | ✅ support (default true) | ❌ ignore |
| `textAlignVertical` | ✅ support | ❌ ignore |
| `adjustsFontSizeToFit` | ✅ (RN में support) | ✅ |
| `dataDetectorType` | ✅ (phoneNumber, link, email) | ❌ Text पर नहीं |
| `selectable` | long-press menu | long-press menu |
| Font weight '600' | custom font हो तो नज़दीकी weight | सही weight दिखता है |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo में custom font: expo-font या expo-google-fonts
import { useFonts } from 'expo-font';             // Expo package
import { Text } from 'react-native';

export default function App() {
  // font file load करो (assets/fonts/ में रखो)
  const [loaded] = useFonts({ Poppins: require('./assets/fonts/Poppins-Regular.ttf') });
  if (!loaded) return null;                        // load होने तक कुछ नहीं
  return <Text style={{ fontFamily: 'Poppins' }}>Hello</Text>;
}
```
CLI way:
```jsx
// CLI में font files को native folders में link करना पड़ता है
// 1) react-native.config.js में assets: ['./assets/fonts/'] लिखो
// 2) चलाओ: npx react-native-asset
// 3) फिर code में सीधे नाम use करो
import { Text } from 'react-native';
<Text style={{ fontFamily: 'Poppins-Regular' }}>Hello</Text>
// Android में file का नाम ही fontFamily है, iOS में font का PostScript नाम
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Text को `<View>` में सीधे लिखना
```jsx
<View>Hello</View>   // ❌ Error: Text strings must be rendered within a <Text>
```
✅ Correct:
```jsx
<View><Text>Hello</Text></View>   // ✅
```

❌ Mistake 2: Text पर `flexDirection` / `borderRadius` से layout सोचना और ऊपर के View की style Text को inherit होने की उम्मीद करना।
```jsx
<View style={{ color: 'red' }}><Text>Hi</Text></View>  // ❌ color View से Text को नहीं जाता
```
✅ Correct:
```jsx
<Text style={{ color: 'red' }}>Hi</Text>   // ✅ style Text पर लगाओ (सिर्फ nested Text inherit करता है)
```

❌ Mistake 3: `{count && <Text>..</Text>}` में count = 0 रखना (0 string की तरह दिखता है / crash).
✅ Correct: `{count > 0 && <Text>..</Text>}`

---

## 🧠 Tricky Interview Question
```jsx
<Text style={{ color: 'red', fontSize: 20 }}>
  Hello <Text style={{ fontWeight: 'bold' }}>World</Text>
</Text>
```
**Q: "World" का color और size क्या होगा?**

Answer: "World" भी **red और 20 size** का होगा और bold भी। Nested `Text` parent `Text` की style inherit करता है (web के CSS inheritance जैसा) और अपनी style add करता है। लेकिन `<View>` से `<Text>` को कोई style inherit नहीं होती — RN में inheritance सिर्फ Text-के-अंदर-Text में है।

---

## ⚫ Interview Questions + Answers
Q1: RN में `<Text>` क्यों ज़रूरी है?
A1: क्योंकि native side पर text के लिए अलग widget (TextView/UILabel) होता है। `View` text render नहीं कर सकता, इसलिए हर string `<Text>` में होनी चाहिए, वरना error आता है।

Q2: `numberOfLines` और `ellipsizeMode` क्या करते हैं?
A2: `numberOfLines={n}` text को n lines तक सीमित करता है। `ellipsizeMode` तय करता है "..." कहाँ लगे: `head`, `middle`, `tail` (default), `clip`। Zomato के restaurant name के लिए `tail` आम है।

Q3: क्या `Text` के अंदर `View` रख सकते हैं?
A3: हाँ, रख सकते हैं (inline view), लेकिन layout/performance की दिक्कत हो सकती है, ख़ासकर Android पर। सामान्यतः nested `Text` ही use करो।

Q4: Dynamic font size (accessibility) से UI टूटे तो?
A4: `allowFontScaling={false}` या `maxFontSizeMultiplier` set करो। Accessibility के लिए fully बंद करना ठीक नहीं, multiplier बेहतर है।

Q5: `Text` पर press कैसे सुनें?
A5: `onPress` / `onLongPress` prop दो। Link जैसे text के लिए सही है; बड़े touch area के लिए `Pressable` बेहतर है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- कोई भी string/number/label दिखाना हो
- Rich text (bold + colored mix) चाहिए — nested Text
- Long text truncate करना हो

❌ Avoid when:
- Rich HTML content दिखाना हो (WebView / `react-native-render-html` लें)
- बड़ा tappable button चाहिए (`Pressable` में Text रखो)
- बहुत लंबी list के हर item में भारी nested Text (performance)

---

## 📊 Visual Diagram
```
<Text style={{color:'red'}}>
   Hello <Text style={{fontWeight:'bold'}}>World</Text>
</Text>
        │
        ▼ (RN maps)
Android: TextView + SpannableString
iOS    : UILabel   + NSAttributedString

Screen:  Hello **World**   (दोनों red, World bold)

numberOfLines={1}:  "Butter Chicken, Naan, Dal Ma..."
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Text | Only component to show text | text दिखाने वाला component |
| Nested Text | Text inside Text | Text के अंदर Text |
| numberOfLines | Max lines limit | अधिकतम lines |
| ellipsizeMode | Where "..." goes | "..." कहाँ लगे |
| allowFontScaling | Follow system font size | system font size follow करना |
| selectable | Long press copy | copy करने लायक |

---

## ⚡ 3-Line Summary
English:
1. `<Text>` is the only way to show text; strings outside it crash.
2. Nested Text inherits style; View does not pass style to Text.
3. Use `numberOfLines`, `ellipsizeMode`, `onPress` for real app behaviour.

Hindi:
1. Text दिखाने का एकमात्र तरीका `<Text>` है; बाहर string = error।
2. Nested Text style inherit करता है, View नहीं देता।
3. असली app के लिए `numberOfLines`, `ellipsizeMode`, `onPress` use करो।

---

## ➡️ Next Topic
**24. ImageBackground Component** — Image के ऊपर content (text/buttons) रखना, जैसे Swiggy के banners।
