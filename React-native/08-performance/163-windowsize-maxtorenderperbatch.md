# 163. windowSize + maxToRenderPerBatch
# हिंदी में: windowSize और maxToRenderPerBatch (Render window की tuning)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: **Expo SDK 52 (check current docs — APIs change between SDKs)**, RN 0.76. ये `FlatList`/`VirtualizedList` के props हैं: `windowSize` (default 21), `maxToRenderPerBatch` (default 10), `updateCellsBatchingPeriod` (default 50 ms), `initialNumToRender` (default 10)।

---

## 🔵 Simple Definition (English)
- **`windowSize`**: how many screens of content stay rendered. Value 21 = 10 screens above + current + 10 below. Smaller = less memory but more risk of blank areas on fast scroll.
- **`maxToRenderPerBatch`**: how many items are rendered in each batch while scrolling. Smaller = JS stays responsive but content may appear late.

## 🔵 सरल परिभाषा (Hindi)
- **`windowSize`**: कितनी screens जितना content render रहे। 21 = 10 screen ऊपर + 1 current + 10 नीचे। कम मान = कम memory पर तेज़ scroll में blank का risk।
- **`maxToRenderPerBatch`**: scroll के दौरान हर batch में कितने items render हों। कम मान = JS responsive, पर content देर से आ सकता है।

---

## 🔴 Problem it Solves
```
Default (21 screens × भारी rows) → RAM ज़्यादा, सस्ते phone पर crash/lag
बहुत छोटा window → तेज़ scroll पर सफ़ेद खाली (blank) जगह

Trade-off:
  बड़ा windowSize  → ज़्यादा memory, कम blank
  छोटा windowSize  → कम memory, ज़्यादा blank
  बड़ा batch       → जल्दी भरता है, पर JS thread busy (touch lag)
  छोटा batch       → JS खाली, पर content धीरे भरता है
```

## 🔴 यह क्यों बना? (Hindi)
```
Default window बड़ा है → भारी rows पर RAM ज़्यादा।
बहुत छोटा window → तेज़ scroll पर blank।
इन दो knobs से आप memory बनाम smoothness का सही संतुलन चुनते हैं।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → List viewport height = 1 "screen" (visibleLength)
Step 2 → windowSize=5 → render: 2 screens ऊपर + 1 + 2 नीचे
Step 3 → Scroll करने पर window की सीमा के बाहर की rows unmount
Step 4 → नई rows batch में render: हर batch अधिकतम maxToRenderPerBatch items
Step 5 → Batches के बीच updateCellsBatchingPeriod ms का अंतराल
Step 6 → जब तक batch नहीं भरा, खाली जगह में placeholder (blank) दिखती है
Step 7 → Release build + असली device पर values tune करो
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → viewport की height = 1 screen
Step 2 → windowSize=5 → 2 ऊपर + 1 + 2 नीचे
Step 3 → window के बाहर की rows unmount
Step 4 → नई rows batches में, हर batch में अधिकतम maxToRenderPerBatch
Step 5 → batches के बीच updateCellsBatchingPeriod ms
Step 6 → batch भरने तक खाली जगह दिखती है
Step 7 → Release build पर values tune करो
```

---

## 🟡 Real World Example
**Instagram-जैसा feed** (हर item में बड़ी image): `windowSize=5`, `maxToRenderPerBatch=3`, `initialNumToRender=3` रखने से 2GB phone पर RAM स्थिर रहती है। वहीं **Paytm की साधारण text history** में हल्की rows हैं, तो `windowSize=11` और `maxToRenderPerBatch=15` रखकर blank पूरी तरह रोका जा सकता है।

## 🟡 Real Example Hindi mein
Instagram जैसे image feed में `windowSize=5`, `maxToRenderPerBatch=3` से सस्ते phone पर RAM स्थिर रहती है। Paytm की हल्की text history में `windowSize=11` और `maxToRenderPerBatch=15` रखकर blank रोका जा सकता है।

---

## 💻 Code Example — Basic
```jsx
// Basic: भारी rows के लिए छोटा window
import React from 'react';                                           // React
import { FlatList, Text, View } from 'react-native';                 // components

const data = Array.from({ length: 3000 }, (_, i) => ({ id: String(i), title: `Post ${i}` })); // demo data

export default function Feed() {
  return (
    <FlatList
      data={data}                                                    // list data
      keyExtractor={(i) => i.id}                                     // unique key
      initialNumToRender={4}                                         // पहली screen में सिर्फ 4
      windowSize={5}                                                 // 2 screens ऊपर + 1 + 2 नीचे
      maxToRenderPerBatch={4}                                        // हर batch में 4
      updateCellsBatchingPeriod={50}                                 // batches के बीच 50 ms
      renderItem={({ item }) => (
        <View style={{ height: 300, padding: 16 }}>                  {/* भारी row का नमूना */}
          <Text>{item.title}</Text>
        </View>
      )}
    />
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: platform के हिसाब से window profile चुनना
import React, { useMemo } from 'react';
import { FlatList, Platform, Text, View } from 'react-native';

// Profiles: "low" = सस्ते devices, "high" = flagship (किस profile को कब चुनना है यह आपकी टीम तय करे;
// यहाँ सरल heuristic: Android → low, iOS → high. असली ऐप में device info library/remote config देखो)
const PROFILES = {
  low:  { windowSize: 5,  maxToRenderPerBatch: 3,  initialNumToRender: 4,  updateCellsBatchingPeriod: 80 },
  high: { windowSize: 15, maxToRenderPerBatch: 12, initialNumToRender: 10, updateCellsBatchingPeriod: 40 },
};

export default function SmartList({ data, renderRow }) {
  const profile = useMemo(() => (Platform.OS === 'android' ? PROFILES.low : PROFILES.high), []); // चयन

  return (
    <View style={{ flex: 1 }}>
      <Text>Profile: {Platform.OS === 'android' ? 'low' : 'high'}</Text>
      <FlatList
        data={data}
        keyExtractor={(i) => String(i.id)}
        renderItem={renderRow}
        {...profile}                                                 // चुने हुए props फैलाओ
      />
    </View>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Props | Same | Same |
| Typical tuning | छोटा window (RAM/JS कम) | Default या बड़ा ठीक |
| Fast-scroll blank | ज़्यादा दिखता (slow JS) | कम |
| Combine with | `removeClippedSubviews` | सामान्यतः अकेला window tuning |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// core props, कोई setup नहीं
<FlatList windowSize={5} maxToRenderPerBatch={4} initialNumToRender={4} data={d} renderItem={r} />
```
CLI way:
```jsx
// वही। FlashList में ये props नहीं हैं (वह recycling करता है; docs देखो)
<FlatList windowSize={5} maxToRenderPerBatch={4} initialNumToRender={4} data={d} renderItem={r} />
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `windowSize={1}` रखना।
✅ Correct: बहुत छोटा मान blank बनाता है; 3-7 से शुरू करो।

❌ Mistake 2: `maxToRenderPerBatch` बहुत बड़ा → JS thread busy, touch lag।
✅ Correct: छोटे batches + memoized rows।

❌ Mistake 3: Dev mode में tune करना।
✅ Correct: Release build पर असली device से।

❌ Mistake 4: `initialNumToRender` को windowSize जैसा समझना।
✅ Correct: यह सिर्फ पहली render की संख्या है; यह screen भरने जितनी रखो।

---

## 🧠 Tricky Interview Question
"`windowSize` घटाने के बाद memory घटी, पर तेज़ scroll पर सफ़ेद खाली जगह दिखती है। बिना windowSize बढ़ाए इसे कैसे कम करें?"

Answer: Blank इसलिए है कि JS नई rows जल्दी नहीं बना पा रहा। Row को हल्की बनाओ, `React.memo`, `getItemLayout` (measure बचे), images छोटी, `maxToRenderPerBatch` थोड़ा बढ़ाओ और `updateCellsBatchingPeriod` घटाओ। या FlashList जैसा recycling list।

---

## ⚫ Interview Questions + Answers
Q1: windowSize 21 का मतलब?
A1: 10 viewport ऊपर + 1 visible + 10 नीचे = कुल 21 screens render।

Q2: initialNumToRender vs windowSize?
A2: पहली render में कितने items बनें बनाम चलते समय window कितनी बड़ी रहे।

Q3: maxToRenderPerBatch क्या नियंत्रित करता है?
A3: हर incremental render batch में items की अधिकतम संख्या।

Q4: Memory और blank का संबंध?
A4: उल्टा — window छोटी = कम memory, ज़्यादा blank।

Q5: Defaults क्या हैं?
A5: windowSize 21, maxToRenderPerBatch 10, updateCellsBatchingPeriod 50, initialNumToRender 10।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- भारी rows/images वाली लंबी list
- सस्ते Android devices target हों
- Profiling में blank या memory problem दिखे

❌ Avoid when:
- हल्की छोटी lists (defaults ठीक)
- बिना measurement के अंदाज़ से बदलना

---

## 📊 Visual Diagram
```
 windowSize = 5
 ┌─────────────────────────────┐
 │ ░ unmounted ░░░░░░░░░░░░░░░ │
 │ [screen -2] rendered        │
 │ [screen -1] rendered        │
 │ [ VISIBLE ] rendered  ◄──── │ viewport
 │ [screen +1] rendered        │
 │ [screen +2] rendered        │
 │ ░ unmounted ░░░░░░░░░░░░░░░ │
 └─────────────────────────────┘
 नई rows batches में: maxToRenderPerBatch प्रति batch
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| windowSize | Render window in viewport units | Render window का आकार |
| Batch | Group of items rendered together | एक साथ render होने वाला समूह |
| Blank area | Unrendered space while scrolling | Scroll में खाली जगह |
| initialNumToRender | Items in first render | पहली render में items |
| Viewport | Visible list area | दिखने वाला हिस्सा |

---

## ⚡ 3-Line Summary
English: windowSize sets how many screens stay rendered; maxToRenderPerBatch sets how many items render per batch. Smaller values save memory/JS time but risk blank areas. Tune on a release build.
Hindi: windowSize तय करता है कितनी screens render रहें; maxToRenderPerBatch हर batch में कितने items। कम मान memory/JS बचाते हैं पर blank का risk। Release build पर tune करो।

---

## ➡️ Next Topic
**164. Image Optimization** — lists में सबसे भारी चीज़: images।
