# 51. Responsive Design in React Native
# हिंदी में: React Native में Responsive Design
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs)। Safe area के लिए `react-native-safe-area-context` (Expo में शामिल)।

---

## 🔵 Simple Definition (English)
Responsive design means your UI looks good on every screen size, density and orientation: small phones, big phones, tablets, landscape and foldables. In RN you do it with Flexbox, percentages, `useWindowDimensions`, `Platform`, safe-area insets and sensible font scaling.

## 🔵 सरल परिभाषा (Hindi)
Responsive design का मतलब है कि आपका UI हर screen size, density और orientation पर सही दिखे: छोटे फोन, बड़े फोन, tablet, landscape और foldable। RN में इसे Flexbox, percentage, `useWindowDimensions`, `Platform`, safe-area insets और सही font scaling से करते हैं।

---

## 🔴 Problem it Solves
```
❌ Fixed width 360 रखने पर बड़े फोन में खाली जगह, छोटे फोन में कट जाना
❌ Notch/Dynamic Island/navigation bar के नीचे content छिप जाना
❌ Tablet पर फोन जैसा खिंचा हुआ UI
```

## 🔴 यह क्यों बना? (Hindi)
```
भारत में 5-इंच के सस्ते फोन से लेकर 7-इंच tablet तक सब चलते हैं।
एक ही code सब पर ठीक दिखे, इसलिए responsive तकनीकें चाहिए।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Fixed px की जगह flex / % / aspectRatio इस्तेमाल करो
Step 2 → useWindowDimensions से width लो → breakpoints (फोन <600, tablet ≥600)
Step 3 → SafeAreaProvider + useSafeAreaInsets से notch/bars का padding
Step 4 → Images: width: '100%' + aspectRatio (जैसे 16/9), resizeMode सही रखो
Step 5 → Font: allowFontScaling रखो, पर layout टूटे तो maxFontSizeMultiplier दो
Step 6 → Real small (SE/5-इंच) और बड़े (Pro Max/tablet) devices पर test करो
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Fixed px की जगह flex / % / aspectRatio
Step 2 → useWindowDimensions से width → breakpoints
Step 3 → useSafeAreaInsets से notch/bars की जगह छोड़ो
Step 4 → Image में width '100%' + aspectRatio
Step 5 → Font scaling को सीमित रखो (maxFontSizeMultiplier)
Step 6 → छोटे और बड़े दोनों devices पर test करो
```

---

## 🟡 Real World Example
**Zomato** का restaurant card हर फोन पर पूरी चौड़ाई लेता है (image `aspectRatio` से)। **Swiggy** का bottom cart bar notch/gesture bar के ऊपर रहता है (safe area)। **Paytm** tablet पर 2 pane दिखा सकता है।

## 🟡 Real Example Hindi mein
Swiggy की "View Cart" पट्टी iPhone के नीचे की gesture line के ऊपर रहती है, क्योंकि वे bottom safe-area inset जोड़ते हैं।

---

## 💻 Code Example — Basic
```jsx
// Basic: percentage + flex + aspectRatio से responsive card
import React from 'react';                                      // React
import { View, Text, Image, StyleSheet } from 'react-native';   // core

export default function Card() {
  return (
    <View style={styles.card}>
      <Image
        source={{ uri: 'https://picsum.photos/800/450' }}       // demo image
        style={styles.img}                                      // aspectRatio वाला style
      />
      <View style={styles.row}>
        <Text style={styles.title}>Biryani House</Text>{/* बाएँ */}
        <Text>30 min</Text>{/* दाएँ */}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: { width: '92%', alignSelf: 'center', backgroundColor: '#fff', borderRadius: 12, overflow: 'hidden', marginTop: 16 }, // 92% चौड़ाई
  img: { width: '100%', aspectRatio: 16 / 9 },                  // ऊँचाई अपने आप
  row: { flexDirection: 'row', justifyContent: 'space-between', padding: 12 }, // बगल-बगल
  title: { flex: 1, fontWeight: '700' },                        // बाकी जगह भरो
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: breakpoints + safe area + max-width content + font scale limit
// Install: npx expo install react-native-safe-area-context
import React from 'react';                                      // React
import { View, Text, ScrollView, useWindowDimensions, StyleSheet } from 'react-native'; // core
import { SafeAreaProvider, useSafeAreaInsets } from 'react-native-safe-area-context';   // insets

const BREAKPOINT_TABLET = 600;                                  // tablet की सीमा

function Screen() {
  const { width } = useWindowDimensions();                      // live width
  const insets = useSafeAreaInsets();                           // top/bottom/left/right
  const isTablet = width >= BREAKPOINT_TABLET;                  // tablet?

  return (
    <View style={[styles.root, { paddingTop: insets.top, paddingBottom: insets.bottom }]}>
      <ScrollView
        contentContainerStyle={[
          styles.content,
          isTablet && styles.tabletContent,                     // tablet पर max-width
        ]}
      >
        <Text style={styles.h1} maxFontSizeMultiplier={1.3}>{/* font scale सीमित */}
          Your Orders
        </Text>
        <View style={[styles.grid, isTablet && { flexDirection: 'row', flexWrap: 'wrap' }]}>
          {[1, 2, 3, 4].map((n) => (
            <View key={n} style={[styles.item, isTablet && { width: '48%' }]}>
              <Text>Order #{n}</Text>
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>{/* insets के लिए ज़रूरी */}
      <Screen />
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#f5f5f5' },
  content: { padding: 16 },
  tabletContent: { maxWidth: 900, alignSelf: 'center', width: '100%' }, // बहुत चौड़ा न फैले
  h1: { fontSize: 22, fontWeight: '700', marginBottom: 12 },
  grid: { gap: 12 },
  item: { backgroundColor: '#fff', padding: 16, borderRadius: 10 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Screen sizes | बहुत अलग-अलग (बहुत ज़्यादा variety) | सीमित models, पर iPad |
| System bars | Status + Navigation bar (3-button / gesture) | Notch / Dynamic Island + home indicator |
| Safe area | Insets edge-to-edge के साथ ज़्यादा ज़रूरी | हमेशा ज़रूरी |
| Font scaling | System font size बड़ा हो सकता है | Dynamic Type |
| Multi-window | ✅ split screen / foldable | iPad Split View |
| Density (dp) | mdpi...xxxhdpi | @1x/@2x/@3x |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// safe-area-context Expo में पहले से शामिल (expo-router में Provider अपने आप)
import { useSafeAreaInsets } from 'react-native-safe-area-context';
```
CLI way:
```jsx
// CLI में install करना होगा
// npm i react-native-safe-area-context && cd ios && pod install
import { SafeAreaProvider } from 'react-native-safe-area-context';
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Fixed `width: 360` / `height: 800`
✅ Correct: `flex`, `%`, `aspectRatio`, `useWindowDimensions`।

❌ Mistake 2: Notch/gesture bar पर content छिपना
✅ Correct: `useSafeAreaInsets`।

❌ Mistake 3: Tablet पर content पूरी चौड़ाई में खिंचना
✅ Correct: `maxWidth` + `alignSelf: 'center'`।

❌ Mistake 4: Text की ऊँचाई fixed रखना, बड़े font पर कट जाए
✅ Correct: `minHeight` / padding और `maxFontSizeMultiplier`।

---

## 🧠 Tricky Interview Question
```jsx
<View style={{ width: 300, height: 600 }} />
```
**Q: 5-इंच फोन (width 320) और tablet (width 800) पर क्या दिक्कत?**

Answer: छोटे फोन में मार्जिन लगभग खत्म, content कट सकता है; tablet पर 500px खाली जगह। Fixed px नहीं, `%`/flex/`maxWidth` और breakpoints चाहिए। Height भी fixed न रखें (keyboard, font scale, safe area से बदलती है)।

---

## ⚫ Interview Questions + Answers
Q1: RN में media queries क्यों नहीं?
A1: RN CSS नहीं चलाता; `useWindowDimensions` + JS conditions से breakpoints बनाते हैं।

Q2: dp और px?
A2: RN के units density-independent (dp जैसे) हैं; `PixelRatio` से असली pixels निकलते हैं।

Q3: Tablet के लिए अलग layout कैसे?
A3: Width breakpoint से अलग component; या `.tablet.js` जैसी custom file strategy।

Q4: Font size responsive कैसे?
A4: `allowFontScaling` रखो + `maxFontSizeMultiplier` सीमा; अनावश्यक scaling libraries सोच-समझकर।

Q5: Orientation lock?
A5: Expo: `app.json` में `"orientation": "portrait"` या `expo-screen-orientation`।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- App कई devices/tablet/foldable पर जाएगा
- Landscape support चाहिए

❌ Avoid when:
- Over-engineering: सिर्फ फोन, portrait-locked छोटा app, तब flex + safe area काफ़ी

---

## 📊 Visual Diagram
```
 Phone (<600)            Tablet (>=600)
 ┌────────┐            ┌──────────────────────┐
 │ card   │            │ card │ card │ (2 col) │
 │ card   │            │ card │ card │         │
 └────────┘            └──────────────────────┘
 flex/% + safe-area     maxWidth + breakpoints
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Breakpoint | Layout बदलने की चौड़ाई | सीमा बिंदु |
| aspectRatio | चौड़ाई:ऊँचाई अनुपात | अनुपात |
| Safe area | Notch/bars से बचा हिस्सा | सुरक्षित क्षेत्र |
| dp | Density-independent pixel | घनत्व-स्वतंत्र pixel |
| maxFontSizeMultiplier | Font scale की सीमा | font की अधिकतम सीमा |

---

## ⚡ 3-Line Summary
English:
1. Use flex, percentages, aspectRatio and breakpoints instead of fixed pixels.
2. Use safe-area insets and limit font scaling.
3. Test small phones, large phones and tablets.

Hindi:
1. Fixed pixel की जगह flex, percentage, aspectRatio और breakpoints।
2. Safe-area insets इस्तेमाल करो और font scaling सीमित रखो।
3. छोटे/बड़े फोन और tablet पर test करो।

---

## ➡️ Next Topic
**52. Platform Specific Styling** — Android और iOS के लिए अलग style देना।
