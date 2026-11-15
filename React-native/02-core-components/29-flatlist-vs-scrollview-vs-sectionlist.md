# 29. FlatList vs ScrollView vs SectionList
# हिंदी में: FlatList बनाम ScrollView बनाम SectionList
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 के हिसाब से examples (check current docs — APIs change between SDKs). तीनों core components हैं; इनके बारे में detail अलग notes (26, 27, 28) में है।

---

## 🔵 Simple Definition (English)
All three show scrollable content. **ScrollView** renders all children at once (good for small content). **FlatList** renders only visible items (good for long lists). **SectionList** is like FlatList but with grouped sections and headers.

## 🔵 सरल परिभाषा (Hindi)
तीनों scroll होने वाला content दिखाते हैं। **ScrollView** सारे children एक साथ render करता है (छोटे content के लिए)। **FlatList** सिर्फ दिखने वाले items render करता है (लंबी list के लिए)। **SectionList** FlatList जैसा है पर sections और headers के साथ।

---

## 🔴 Problem it Solves
```
❌ 1000 restaurants ScrollView में डालो → सब एक साथ render
   → memory ज़्यादा, startup slow, app lag/crash
❌ हर बार खुद से "सिर्फ visible items दिखाओ" logic लिखना
❌ Grouped data (A-Z contacts, menu categories) के लिए manual headers
```

## 🔴 यह क्यों बना? (Hindi)
```
मोबाइल की memory कम होती है।
लंबी list में सब कुछ render करना बहुत भारी है।
इसलिए:
✅ ScrollView → छोटा, fixed content
✅ FlatList   → बड़ी list, virtualization (window में ही items)
✅ SectionList → grouped list + sticky headers
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → ScrollView: सारे children mount होते हैं (सब memory में)
Step 2 → FlatList: data array + renderItem मिलता है
Step 3 → FlatList सिर्फ visible window + थोड़ा ऊपर-नीचे (windowSize) render करता है
Step 4 → Scroll करने पर नए items mount, पुराने दूर वाले unmount
Step 5 → SectionList: sections=[{title,data}] लेता है, हर section का header दिखाता है
Step 6 → keyExtractor से हर item की unique key बनती है
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → ScrollView: सारे children एक साथ बनते हैं
Step 2 → FlatList: data array और renderItem लेता है
Step 3 → सिर्फ screen पर दिखने वाले (+ थोड़े आस-पास के) items render होते हैं
Step 4 → scroll करने पर नए items बनते हैं, दूर वाले हटते हैं
Step 5 → SectionList: sections=[{title, data}] से headers सहित list
Step 6 → keyExtractor हर item को unique key देता है
```

---

## 🟡 Real World Example
**Zomato** का restaurant feed (सैकड़ों cards) → `FlatList`। **Swiggy** का menu page (Recommended, Biryani, Desserts categories, sticky headers) → `SectionList`। **Paytm** का "Add Money" छोटा form जिसमें 5-6 fields → `ScrollView`। **WhatsApp**-जैसी contacts list A-Z → `SectionList`।

## 🟡 Real Example Hindi mein
Zomato की लंबी restaurant list `FlatList` से बनती है। Swiggy के menu में categories के headers `SectionList` से आते हैं। Paytm का छोटा form (कुछ fields) `ScrollView` में ठीक रहता है।

---

## 💻 Code Example — Basic
```jsx
// तीनों की side-by-side तुलना — Android + iOS
import React from 'react';
import { ScrollView, FlatList, SectionList, Text, View, StyleSheet } from 'react-native';

const items = Array.from({ length: 20 }, (_, i) => ({ id: String(i), name: `Restaurant ${i + 1}` })); // demo data
const sections = [
  { title: 'Starters', data: ['Paneer Tikka', 'Hara Bhara Kebab'] },   // section 1
  { title: 'Main Course', data: ['Dal Makhani', 'Butter Chicken'] },   // section 2
];

export default function Compare() {
  return (
    <View style={styles.wrap}>
      {/* 1) ScrollView: छोटा content — सब render */}
      <ScrollView style={styles.box}>
        <Text>Terms line 1</Text>
        <Text>Terms line 2</Text>
        <Text>Terms line 3</Text>
      </ScrollView>

      {/* 2) FlatList: लंबी list — सिर्फ visible render */}
      <FlatList
        style={styles.box}
        data={items}                                  // data array
        keyExtractor={item => item.id}                // unique key
        renderItem={({ item }) => <Text>{item.name}</Text>} // हर row
      />

      {/* 3) SectionList: sections + headers */}
      <SectionList
        style={styles.box}
        sections={sections}                           // grouped data
        keyExtractor={(item, index) => item + index}  // unique key
        renderSectionHeader={({ section }) => <Text style={styles.h}>{section.title}</Text>}
        renderItem={({ item }) => <Text>{item}</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, paddingTop: 40 },                  // पूरी screen
  box: { flex: 1, borderBottomWidth: 1, padding: 8 }, // तीनों को बराबर जगह
  h: { fontWeight: '700', backgroundColor: '#eee' },  // header style
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: Swiggy-style FlatList — pull-to-refresh, pagination, empty/error states, optimization
import React, { useState, useCallback } from 'react';
import { FlatList, Text, View, ActivityIndicator, RefreshControl, StyleSheet } from 'react-native';

// अलग component + React.memo → बेवजह re-render नहीं
const Row = React.memo(({ item }) => (
  <View style={styles.row}><Text style={styles.name}>{item.name}</Text></View>
));

export default function Feed() {
  const [data, setData] = useState(() => makePage(0));  // पहला page
  const [refreshing, setRefreshing] = useState(false);  // pull-to-refresh state
  const [loadingMore, setLoadingMore] = useState(false);// pagination state

  const renderItem = useCallback(({ item }) => <Row item={item} />, []); // stable function

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await new Promise(r => setTimeout(r, 500));       // fake API call
      setData(makePage(0));                             // fresh data
    } finally {
      setRefreshing(false);                             // हमेशा बंद करो
    }
  }, []);

  const loadMore = useCallback(async () => {
    if (loadingMore || data.length >= 60) return;       // double call / अंत रोको
    setLoadingMore(true);
    await new Promise(r => setTimeout(r, 500));         // fake API
    setData(prev => [...prev, ...makePage(prev.length)]); // अगला page जोड़ो
    setLoadingMore(false);
  }, [loadingMore, data.length]);

  return (
    <FlatList
      data={data}
      renderItem={renderItem}
      keyExtractor={item => item.id}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />} // दोनों OS
      onEndReached={loadMore}                           // नीचे पहुँचने पर
      onEndReachedThreshold={0.5}                       // आधी स्क्रीन पहले
      ListEmptyComponent={<Text style={styles.empty}>कोई restaurant नहीं मिला</Text>}
      ListFooterComponent={loadingMore ? <ActivityIndicator /> : null}
      initialNumToRender={8}                            // शुरू में कम items
      windowSize={7}                                    // render window
      removeClippedSubviews                             // Android पर off-screen views detach
    />
  );
}

// demo data generator
function makePage(start) {
  return Array.from({ length: 20 }, (_, i) => ({ id: String(start + i), name: `Restaurant ${start + i + 1}` }));
}

const styles = StyleSheet.create({
  row: { padding: 16, borderBottomWidth: StyleSheet.hairlineWidth },
  name: { fontSize: 16 },
  empty: { textAlign: 'center', marginTop: 40 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Pull-to-refresh | Material spinner (colors prop) | UIRefreshControl spinner (tintColor) |
| `removeClippedSubviews` | Default true (Android) | Default false |
| Bounce at end | Overscroll glow/stretch | Rubber-band bounce (`bounces`) |
| `stickySectionHeadersEnabled` | Default false | Default true (SectionList) |
| Scroll indicator | `showsVerticalScrollIndicator` | वही + `indicatorStyle` |
| `nestedScrollEnabled` | ✅ (nested scroll के लिए ज़रूरी) | ❌ ज़रूरत नहीं |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Core lists में कोई फ़र्क नहीं। Faster lists के लिए Shopify FlashList:
// npx expo install @shopify/flash-list
import { FlashList } from '@shopify/flash-list';
<FlashList data={data} renderItem={renderItem} estimatedItemSize={80} />
// (FlashList v1 में estimatedItemSize चाहिए; v2 में optional — version check करो)
```
CLI way:
```jsx
// वही core components। FlashList के लिए:
// npm i @shopify/flash-list && cd ios && pod install
import { FlashList } from '@shopify/flash-list';
<FlashList data={data} renderItem={renderItem} estimatedItemSize={80} />
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: लंबी list के लिए `ScrollView` + `.map()`
```jsx
<ScrollView>{data.map(d => <Row key={d.id} item={d} />)}</ScrollView> // ❌ सब render
```
✅ Correct: `<FlatList data={data} renderItem={...} keyExtractor={...} />`

❌ Mistake 2: FlatList को vertical ScrollView के अंदर रखना (warning: VirtualizedLists should never be nested)
✅ Correct: `ListHeaderComponent` / `ListFooterComponent` use करो या SectionList।

❌ Mistake 3: `keyExtractor` न देना / index को key बनाना (data बदलने पर गलत re-use)
✅ Correct: stable unique id use करो।

❌ Mistake 4: renderItem में inline भारी function बनाना।
✅ Correct: `React.memo` + `useCallback`।

---

## 🧠 Tricky Interview Question
**Q: 10 items की list के लिए FlatList लें या ScrollView? 10,000 के लिए?**

Answer: 10 items जैसे छोटे और fixed content में `ScrollView` सरल और ठीक है (virtualization का overhead नहीं)। 10,000 में `FlatList` (या FlashList) ज़रूरी है, क्योंकि ScrollView सब 10,000 items mount कर देगा। एक catch: FlatList में items fast scroll पर blank दिख सकते हैं (क्योंकि जल्दी render नहीं हुए), जबकि ScrollView में सब पहले से render होने से blank नहीं दिखता। यह trade-off है memory बनाम smoothness।

---

## ⚫ Interview Questions + Answers
Q1: Virtualization क्या है?
A1: सिर्फ screen पर (और आस-पास) दिखने वाले items render करना, बाकी को unmount रखना। इससे memory और startup time बचता है।

Q2: FlatList और SectionList में अंतर?
A2: FlatList flat array लेती है (`data`); SectionList `sections` ([{title, data}]) लेती है और section headers/sticky headers देती है।

Q3: `getItemLayout` कब काम आता है?
A3: जब सारे items की height fixed हो। इससे RN को measure नहीं करना पड़ता, `scrollToIndex` तेज़ और सटीक होता है।

Q4: ScrollView कब बेहतर?
A4: छोटा, सीमित content — forms, onboarding, terms page, कुछ cards।

Q5: FlatList slow हो तो क्या करें?
A5: `React.memo`, `useCallback` renderItem, `keyExtractor`, `getItemLayout`, `initialNumToRender`, `windowSize` कम, छोटी images, या FlashList।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- ScrollView: छोटा/कम items, forms
- FlatList: लंबी या dynamic API list
- SectionList: categories/groups, sticky headers

❌ Avoid when:
- ScrollView में सैकड़ों items
- FlatList को ScrollView में nest करना (same direction)
- बहुत सरल 3-4 items के लिए SectionList

---

## 📊 Visual Diagram
```
ScrollView            FlatList               SectionList
┌─────────┐          ┌─────────┐            ┌──────────┐
│ item 1  │          │ item 5  │ ← render   │ HEADER A │
│ item 2  │          │ item 6  │ ← render   │  a1  a2  │
│ item 3  │ सब       │ item 7  │ ← render   │ HEADER B │
│ ...     │ render   └─────────┘            │  b1  b2  │
│ item 1000│          (बाकी unmounted)       └──────────┘
└─────────┘
Memory: ज़्यादा      Memory: कम             Memory: कम + groups
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Virtualization | Render only visible items | सिर्फ दिखने वाले render |
| keyExtractor | Unique key function | unique key देने वाला function |
| windowSize | How far from viewport to render | viewport के आसपास कितना render |
| getItemLayout | Fixed height hint | fixed height की जानकारी |
| Sticky header | Header stays on top | ऊपर चिपका रहने वाला header |
| onEndReached | Callback near list end | list के अंत पर callback |

---

## ⚡ 3-Line Summary
English:
1. ScrollView renders everything; use it only for small content.
2. FlatList virtualizes items; use it for long dynamic lists.
3. SectionList adds grouped sections and sticky headers.

Hindi:
1. ScrollView सब render करता है; सिर्फ छोटे content के लिए।
2. FlatList virtualization करता है; लंबी list के लिए।
3. SectionList में sections और sticky headers मिलते हैं।

---

## ➡️ Next Topic
**30. TouchableOpacity** — tap पर opacity बदलने वाला classic touchable।
