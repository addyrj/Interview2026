# 162. removeClippedSubviews
# हिंदी में: removeClippedSubviews (स्क्रीन से बाहर की views हटाना)
# Platform: Android ✅ | iOS ✅ (सावधानी के साथ) | Both ✅

> Target: **Expo SDK 52 (check current docs — APIs change between SDKs)**, RN 0.76. यह `View`/`ScrollView`/`FlatList` का prop है। FlatList में Android पर default `true`, iOS पर `false` (docs के अनुसार)।

---

## 🔵 Simple Definition (English)
`removeClippedSubviews` is a prop that detaches child views that are **outside the visible area** from the native view hierarchy. The React components still exist in JS, but the native views are removed, so less memory and less drawing work are used.

## 🔵 सरल परिभाषा (Hindi)
`removeClippedSubviews` एक prop है जो **screen के बाहर** वाली child views को native view hierarchy से अलग कर देता है। JS में React components बने रहते हैं, पर native views हट जाती हैं — इसलिए memory और drawing का काम कम होता है।

---

## 🔴 Problem it Solves
```
लंबी list में दिखने वाली rows 10, पर native views 200 जुड़ी हैं:
  ❌ ज़्यादा native memory
  ❌ हर frame पर ज़्यादा layout/draw काम
  ❌ सस्ते Android phone पर scroll lag

removeClippedSubviews=true:
  ✅ बाहर की views detach → native tree छोटा
```

## 🔴 यह क्यों बना? (Hindi)
```
लंबी list में दिखती 10 rows, पर native tree में 200 views।
नतीजा: ज़्यादा memory, ज़्यादा draw काम, सस्ते Android पर lag।
यह prop बाहर की native views हटाकर tree छोटा रखता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → prop चालू (FlatList में Android पर पहले से)
Step 2 → Scroll होने पर native layer हर child का frame जाँचता है
Step 3 → जो child पूरी तरह clipped (दिखता नहीं) → parent से detach
Step 4 → वापस scroll → child फिर attach
Step 5 → JS component tree वैसी ही रहती है (state सुरक्षित)
Step 6 → Trade-off: कभी-कभी content ग़ायब/blank (खासकर iOS, transforms, absolute-position)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → prop चालू
Step 2 → Scroll पर native layer हर child का frame देखता है
Step 3 → बाहर वाले child parent से detach
Step 4 → वापस आने पर फिर attach
Step 5 → JS tree और state वैसी ही
Step 6 → नुकसान: कभी content ग़ायब दिख सकता है (iOS, transform वाली views)
```

---

## 🟡 Real World Example
**Zomato/Swiggy** की लंबी restaurant list सस्ते Android phones पर चलती है। वहाँ clipped views detach होने से RAM कम रहती है और scroll बेहतर होता है। पर अगर किसी card में `position: 'absolute'` badge या transform animation है और वह ग़ायब होने लगे, तो टीम उस list पर `removeClippedSubviews={false}` कर देती है।

## 🟡 Real Example Hindi mein
**Zomato/Swiggy** की लंबी list सस्ते Android phones पर चलती है; वहाँ बाहर की views detach होने से RAM बचती है। अगर किसी card का absolute badge या animation ग़ायब होने लगे तो उस list पर `removeClippedSubviews={false}` कर दिया जाता है।

---

## 💻 Code Example — Basic
```jsx
// Basic: FlatList में removeClippedSubviews चालू/बंद
import React from 'react';                                           // React
import { FlatList, Text, View, Platform } from 'react-native';       // components

const data = Array.from({ length: 1000 }, (_, i) => ({ id: String(i), name: `Dish ${i}` })); // demo data

export default function Menu() {
  return (
    <FlatList
      data={data}                                                    // list data
      keyExtractor={(i) => i.id}                                     // unique key
      renderItem={({ item }) => (
        <View style={{ height: 56, justifyContent: 'center', paddingHorizontal: 16 }}>
          <Text>{item.name}</Text>
        </View>
      )}
      removeClippedSubviews={Platform.OS === 'android'}              // Android पर चालू, iOS पर बंद
    />
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: बड़े ScrollView में सिर्फ ज़रूरी जगह चालू + glitch toggle + आँकड़े जाँचना
import React, { useState, useCallback } from 'react';
import { ScrollView, View, Text, Switch, Platform } from 'react-native';

const SECTIONS = Array.from({ length: 50 }, (_, i) => ({ id: `s${i}`, title: `Section ${i}` })); // demo

export default function LongPage() {
  const [clip, setClip] = useState(Platform.OS === 'android');       // user/dev toggle (default platform-based)

  const render = useCallback((s) => (
    <View key={s.id} style={{ height: 200, margin: 8, backgroundColor: '#eee' }}>
      <Text>{s.title}</Text>
      {/* absolute badge: clipping में कभी-कभी ग़ायब दिख सकता है — test करो */}
      <View style={{ position: 'absolute', top: 4, right: 4 }}><Text>NEW</Text></View>
    </View>
  ), []);

  return (
    <View style={{ flex: 1 }}>
      <View style={{ flexDirection: 'row', alignItems: 'center', padding: 8 }}>
        <Text>removeClippedSubviews: </Text>
        <Switch value={clip} onValueChange={setClip} />              {/* glitch दिखे तो बंद करो */}
      </View>
      <ScrollView
        removeClippedSubviews={clip}                                 // ScrollView पर भी काम करता है
        scrollEventThrottle={16}                                     // 60fps scroll events
      >
        {SECTIONS.map(render)}
      </ScrollView>
    </View>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| FlatList default | `true` | `false` |
| Benefit | Noticeable (native views बहुत महँगी) | कम; UIKit वैसे भी हल्का |
| Risk | कम (पर absolute/transform glitches संभव) | ज़्यादा: content blank/ग़ायब होने की रिपोर्ट |
| Recommendation | चालू रखो, test करो | बंद रखो जब तक ज़रूरी न हो |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// कोई setup नहीं, core RN prop
<FlatList removeClippedSubviews={Platform.OS === 'android'} data={d} renderItem={r} />
```
CLI way:
```jsx
// वही; कोई native config नहीं
<FlatList removeClippedSubviews={Platform.OS === 'android'} data={d} renderItem={r} />
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: सब जगह `true` कर देना और iOS पर blank rows देखना।
✅ Correct: Platform के हिसाब से लगाओ और दोनों OS पर test करो।

❌ Mistake 2: मानना कि JS components भी unmount होते हैं।
✅ Correct: सिर्फ native views detach होती हैं; JS state/effects चलते रहते हैं (memory बचाना है तो `windowSize` घटाओ)।

❌ Mistake 3: Animated/transform वाली rows पर चालू रखना।
✅ Correct: ऐसी list पर `false` करो।

---

## 🧠 Tricky Interview Question
"`removeClippedSubviews` चालू किया, फिर भी JS heap कम नहीं हुआ। क्यों?"

Answer: यह prop सिर्फ **native** views detach करता है; React elements/fibers JS में रहते हैं। JS memory घटाने के लिए `windowSize`, `maxToRenderPerBatch`, `initialNumToRender` से render window छोटी करो (virtualization), या हल्की rows बनाओ।

---

## ⚫ Interview Questions + Answers
Q1: removeClippedSubviews क्या करता है?
A1: Visible area के बाहर की native child views को parent से detach करता है।

Q2: Default value?
A2: FlatList में Android पर `true`, iOS पर `false`। (core `View` में default `false`; docs जाँचो।)

Q3: Risk क्या है?
A3: Content कभी-कभी ग़ायब/blank दिख सकता है, खासकर iOS या transform/absolute views में।

Q4: windowSize से अंतर?
A4: windowSize तय करता है कि कितने items React-level पर render रहें; removeClippedSubviews native level पर views हटाता है।

Q5: कब बंद करें?
A5: जब glitches दिखें, या rows में animations/overlays हों।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Android पर लंबी, सरल rows वाली list
- Native memory/draw काम घटाना हो

❌ Avoid when:
- iOS (default बंद रखो)
- Animated/absolute/transform वाली rows
- Short lists (फ़ायदा नगण्य)

---

## 📊 Visual Diagram
```
 JS tree      : [r1][r2][r3][r4][r5][r6]...   (सब मौजूद)
 Screen       :        ┌──────┐
 Native tree  :  ✖ ✖  │r3 r4 │  ✖ ✖         (सिर्फ visible attached)
                      └──────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Clipped | Outside visible bounds | दिखने वाले हिस्से के बाहर |
| Detach | Remove from native hierarchy | Native tree से हटाना |
| Native view | Real Android/iOS view | असली Android/iOS view |
| Virtualization | JS-level window of rows | JS-स्तर पर render window |
| Overdraw | Drawing same pixel many times | एक ही pixel पर बार-बार draw |

---

## ⚡ 3-Line Summary
English: removeClippedSubviews detaches off-screen native views to save memory. It helps most on Android; on iOS it can cause blank content. It does not free JS memory.
Hindi: removeClippedSubviews screen के बाहर की native views हटाकर memory बचाता है। Android पर ज़्यादा फ़ायदा; iOS पर content blank हो सकता है। यह JS memory खाली नहीं करता।

---

## ➡️ Next Topic
**163. windowSize + maxToRenderPerBatch** — JS-level render window को tune करना।
