# 50. useWindowDimensions Hook
# हिंदी में: useWindowDimensions Hook (Screen का साइज़, अपने आप update)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs)। Core hook।

---

## 🔵 Simple Definition (English)
`useWindowDimensions()` is a React hook that returns the current `width`, `height`, `scale` and `fontScale` of the window and **re-renders automatically** when they change (rotation, split screen, foldables).

## 🔵 सरल परिभाषा (Hindi)
`useWindowDimensions()` एक hook है जो window की वर्तमान `width`, `height`, `scale` और `fontScale` देता है और ये बदलने पर (rotation, split screen, foldable) **अपने आप re-render** करता है।

---

## 🔴 Problem it Solves
```
❌ Dimensions.get('window') एक बार की value देता है; rotate करने पर पुरानी रह जाती है
❌ Listener जोड़ना/हटाना (addEventListener + cleanup) हाथ से करना पड़ता
❌ Tablet/landscape पर layout बदलने का आसान तरीका चाहिए
```

## 🔴 यह क्यों बना? (Hindi)
```
Responsive UI के लिए screen size हमेशा ताज़ा चाहिए। Hook यह काम
सँभालता है और cleanup भी अपने आप करता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → import { useWindowDimensions } from 'react-native'
Step 2 → component में: const { width, height } = useWindowDimensions();
Step 3 → इन values से layout तय करो (जैसे width > 600 → tablet)
Step 4 → Rotate / window resize होने पर RN नया size भेजता है
Step 5 → Hook component को re-render करता है, नई values मिलती हैं
Step 6 → Unmount पर listener अपने आप हट जाता है
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → hook import करो
Step 2 → const { width, height } = useWindowDimensions();
Step 3 → इन values से layout तय करो
Step 4 → Rotate होने पर नया size आता है
Step 5 → Component फिर से render होता है
Step 6 → Unmount पर cleanup अपने आप
```

---

## 🟡 Real World Example
**Swiggy/Zomato** के grid में फोन पर 2 columns और tablet/landscape पर 4 columns। **YouTube** जैसे apps landscape में video को पूरी चौड़ाई देते हैं। **Paytm** tablet पर side-by-side panels दिखा सकता है।

## 🟡 Real Example Hindi mein
Zomato की restaurant grid: फोन में 2 कॉलम, tablet में 4। `useWindowDimensions` से चौड़ाई पता करके `numColumns` बदलते हैं।

---

## 💻 Code Example — Basic
```jsx
// Basic: width/height दिखाओ और orientation पहचानो
import React from 'react';                                         // React
import { View, Text, useWindowDimensions, StyleSheet } from 'react-native'; // core

export default function Basic() {
  const { width, height } = useWindowDimensions();                 // live values
  const isLandscape = width > height;                              // landscape?

  return (
    <View style={styles.box}>
      <Text>Width: {Math.round(width)}</Text>{/* चौड़ाई */}
      <Text>Height: {Math.round(height)}</Text>{/* ऊँचाई */}
      <Text>{isLandscape ? 'Landscape' : 'Portrait'}</Text>{/* दिशा */}
    </View>
  );
}

const styles = StyleSheet.create({
  box: { flex: 1, justifyContent: 'center', alignItems: 'center' }, // बीच में
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: responsive grid — columns, card width, fontScale का सम्मान
import React, { useMemo } from 'react';                            // useMemo
import { View, Text, FlatList, useWindowDimensions, StyleSheet } from 'react-native'; // core

const GAP = 12;                                                    // card के बीच gap
const DATA = Array.from({ length: 20 }, (_, i) => ({ id: String(i), name: 'Restaurant ' + (i + 1) }));

export default function Grid() {
  const { width } = useWindowDimensions();                         // live width

  // breakpoints: <600 → 2, <900 → 3, उससे ऊपर → 4
  const columns = width < 600 ? 2 : width < 900 ? 3 : 4;

  // हर card की चौड़ाई: (कुल - gaps) / columns
  const cardWidth = useMemo(
    () => (width - GAP * (columns + 1)) / columns,
    [width, columns],
  );

  return (
    <FlatList
      key={columns}                                                // numColumns बदले तो key ज़रूरी
      data={DATA}
      numColumns={columns}                                         // dynamic columns
      keyExtractor={(i) => i.id}
      contentContainerStyle={{ padding: GAP / 2 }}
      renderItem={({ item }) => (
        <View style={[styles.card, { width: cardWidth, margin: GAP / 2 }]}>
          <Text style={{ fontSize: 14 }}>{item.name}</Text>{/* font scale RN खुद लगाता है */}
        </View>
      )}
    />
  );
}

const styles = StyleSheet.create({
  card: { height: 100, backgroundColor: '#fff', borderRadius: 10, padding: 8, justifyContent: 'center' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| `height` में क्या | `window` में system bars का हिस्सा version/edge-to-edge पर निर्भर (जाँच लो) | पूरी window (safe area भी शामिल, insets अलग से लो) |
| `Dimensions.get('screen')` | Navigation bar सहित पूरी screen | `window` जैसा |
| Split-screen / multi-window | ✅ size बदलता है | iPad में ✅ |
| Foldable | ✅ size बदलता है | लागू नहीं |
| `fontScale` | User की font setting | Dynamic Type |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Core hook — Expo Go में सीधा
import { useWindowDimensions } from 'react-native';
const { width } = useWindowDimensions();
```
CLI way:
```jsx
// CLI में भी वही; कोई native setup नहीं
import { useWindowDimensions } from 'react-native';
const { width } = useWindowDimensions();
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `Dimensions.get('window')` को top-level पर रखना, तो rotate पर update नहीं
✅ Correct: Component के अंदर `useWindowDimensions()`।

❌ Mistake 2: `FlatList` में `numColumns` बदलना बिना `key` बदले (error आता है)
✅ Correct: `key={columns}` दो।

❌ Mistake 3: Hook को component के बाहर/condition में बुलाना
✅ Correct: Hooks के नियम मानो, सिर्फ function component के top पर।

---

## 🧠 Tricky Interview Question
```jsx
const { width } = Dimensions.get('window');
export default () => <View style={{ width: width * 0.5 }} />;
```
**Q: Landscape में rotate करने पर चौड़ाई सही क्यों नहीं?**

Answer: `Dimensions.get` module load के समय एक बार चली, इसलिए पुरानी portrait width अटकी है। `useWindowDimensions` component के अंदर इस्तेमाल करो ताकि हर बदलाव पर नई width मिले।

---

## ⚫ Interview Questions + Answers
Q1: `Dimensions` और `useWindowDimensions` में फ़र्क?
A1: `Dimensions` static/manual listener; hook अपने आप update और re-render करता है।

Q2: `window` और `screen` का फ़र्क (Android)?
A2: `window` app का दिखने वाला हिस्सा; `screen` पूरी screen (system bars सहित)।

Q3: क्या यह safe area देता है?
A3: नहीं; `react-native-safe-area-context` का `useSafeAreaInsets` इस्तेमाल करो।

Q4: क्या हर resize पर re-render महँगा है?
A4: Rotation/resize कम होता है, पर भारी tree में `useMemo`/`memo` से बचाव करो।

Q5: `scale` क्या है?
A5: Pixel density (जैसे 2, 3)।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Rotation / tablet / foldable पर layout बदलना
- Width के आधार पर columns/font तय करना

❌ Avoid when:
- सिर्फ percentage width चाहिए (`width: '50%'` काफ़ी)
- Safe area चाहिए (insets hook)

---

## 📊 Visual Diagram
```
 Portrait  360x800 ──rotate──► Landscape 800x360
        │                           │
 useWindowDimensions() ──► {width,height} नया ──► re-render ──► नया layout
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| window | App का दिखने वाला हिस्सा | window |
| screen | पूरी screen | पूरी screen |
| scale | Pixel density | घनत्व |
| fontScale | Font का गुणक | font का पैमाना |
| breakpoint | Layout बदलने की चौड़ाई | सीमा-बिंदु |

---

## ⚡ 3-Line Summary
English:
1. `useWindowDimensions` gives live width/height/scale/fontScale.
2. It re-renders on rotation or resize; no manual listener needed.
3. Prefer it over `Dimensions.get` for responsive layouts.

Hindi:
1. `useWindowDimensions` live width/height/scale/fontScale देता है।
2. Rotation या resize पर अपने आप re-render; listener की ज़रूरत नहीं।
3. Responsive layout के लिए `Dimensions.get` से बेहतर है।

---

## ➡️ Next Topic
**51. Responsive Design in React Native** — हर screen size पर सही दिखने की पूरी रणनीति।
