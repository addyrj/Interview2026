# 44. VirtualizedList
# हिंदी में: VirtualizedList (FlatList का Base Component)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 (React Native 0.76) — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
**VirtualizedList** is the low-level component that powers `FlatList` and `SectionList`. It renders only the items near the screen (windowing) and lets you use any data shape (not only arrays) via `getItem` and `getItemCount`.

## 🔵 सरल परिभाषा (Hindi)
**VirtualizedList** वह low-level component है जिस पर `FlatList` और `SectionList` बने हैं। यह सिर्फ screen के पास वाले items render करता है (windowing) और `getItem` / `getItemCount` से किसी भी data shape (सिर्फ array नहीं) के साथ चलता है।

---

## 🔴 Problem it Solves
```
BEFORE (ScrollView with 10,000 items):
❌ सारे items एक साथ render → memory बहुत ज़्यादा
❌ App slow / crash
❌ Immutable.js List या custom object जैसे data के लिए FlatList सही नहीं
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले (ScrollView में 10,000 items):
❌ सारे items एक साथ render → memory ज़्यादा
❌ App slow या crash
❌ Immutable List/custom data structure के लिए FlatList नहीं चलता
VirtualizedList: सिर्फ दिखने वाले items render + custom data support
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → आप data, getItem(data, index), getItemCount(data) देते हो
Step 2 → List visible window + windowSize के items ही mount करता है
Step 3 → बाकी items की जगह blank spacer रहता है
Step 4 → Scroll करने पर नए items mount, दूर वाले unmount
Step 5 → keyExtractor से हर item की identity track होती है
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप data + getItem + getItemCount देते हो
Step 2 → सिर्फ visible window के आसपास के items mount होते हैं
Step 3 → बाकी की जगह खाली spacer रहता है
Step 4 → Scroll पर नए mount, दूर वाले unmount
Step 5 → keyExtractor से हर item पहचाना जाता है
```

---

## 🟡 Real World Example
**Zomato** की restaurant list में हज़ारों restaurants होते हैं; सब एक साथ render नहीं होते। FlatList (जो VirtualizedList पर बना है) सिर्फ दिखने वाले cards बनाती है। Chat apps (WhatsApp-style) में हज़ारों messages इसी तरह चलते हैं।

## 🟡 Real Example Hindi mein
**Zomato** की list में हज़ारों restaurants होते हैं, सब एक साथ नहीं बनते। FlatList (VirtualizedList पर आधारित) सिर्फ दिखने वाले cards बनाती है। WhatsApp जैसे chat में हज़ारों messages भी ऐसे ही चलते हैं।

---

## 💻 Code Example — Basic

```jsx
// Basic: VirtualizedList with a plain array
import React from 'react';                              // React
import { VirtualizedList, View, Text, StyleSheet } from 'react-native'; // RN

// Item banane ka helper
const getItem = (data, index) => ({ id: String(index), title: `Item ${index + 1}` }); // index se item
const getItemCount = data => data.length;               // total items

export default function BasicVList() {
  const data = new Array(1000).fill(0);                 // 1000 placeholder entries
  return (
    <VirtualizedList
      data={data}                                       // source data
      initialNumToRender={8}                            // pehli baar 8 render
      keyExtractor={item => item.id}                    // unique key
      getItemCount={getItemCount}                       // kitne items
      getItem={getItem}                                 // index -> item
      renderItem={({ item }) => (                       // har row ka UI
        <View style={styles.row}>
          <Text>{item.title}</Text>
        </View>
      )}
    />
  );
}

const styles = StyleSheet.create({
  row: { height: 56, justifyContent: 'center', paddingHorizontal: 16, borderBottomWidth: StyleSheet.hairlineWidth }, // row style
});
```

## 💻 Code Example — Advanced

```jsx
// Advanced: custom Map-based data + getItemLayout + perf tuning
import React, { useCallback, useMemo } from 'react';   // hooks
import { VirtualizedList, View, Text, Platform, StyleSheet } from 'react-native'; // RN

const ROW_H = 64;                                       // fixed row height

// Data ek Map hai (array nahi) — isliye VirtualizedList chahiye
const makeData = () => {
  const m = new Map();                                  // naya Map
  for (let i = 0; i < 5000; i++) m.set(i, { id: `o${i}`, name: `Order #${i}`, amt: 100 + (i % 50) }); // fill
  return m;
};

// Memoized row: re-render kam
const Row = React.memo(({ item }) => (
  <View style={styles.row}>
    <Text style={styles.name}>{item.name}</Text>
    <Text>₹{item.amt}</Text>
  </View>
));

export default function OrdersList() {
  const data = useMemo(makeData, []);                   // ek baar banao
  const getItem = useCallback((d, i) => d.get(i), []);  // Map se item
  const getItemCount = useCallback(d => d.size, []);    // Map ka size
  const keyExtractor = useCallback(item => item.id, []); // stable key
  const getItemLayout = useCallback((_, index) => ({    // fixed height => fast scroll
    length: ROW_H, offset: ROW_H * index, index,
  }), []);

  return (
    <VirtualizedList
      data={data}                                       // Map data
      getItem={getItem}                                 // accessor
      getItemCount={getItemCount}                       // count
      keyExtractor={keyExtractor}                       // key
      getItemLayout={getItemLayout}                     // layout hint
      renderItem={({ item }) => <Row item={item} />}    // row
      windowSize={7}                                    // window = 7 screens
      maxToRenderPerBatch={10}                          // batch size
      updateCellsBatchingPeriod={50}                    // ms between batches
      removeClippedSubviews={Platform.OS === 'android'} // Android pe memory bachao
      initialNumToRender={10}                           // first render
      ListEmptyComponent={<Text>No orders</Text>}       // empty state
    />
  );
}

const styles = StyleSheet.create({
  row: { height: ROW_H, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16 }, // row
  name: { fontWeight: '600' },                          // bold name
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| `removeClippedSubviews` | Default true, memory बचाता है | Default false, bugs आ सकते हैं |
| Overscroll | Glow / stretch | Bounce |
| Scroll physics | Material fling | Momentum |
| Memory limit | Low-end devices पर सख्त | Generally ज़्यादा |

---

## 🟠 Expo vs CLI Difference
**Expo way:**
```jsx
import { VirtualizedList } from 'react-native'; // core, no install
```
**CLI way:**
```jsx
import { VirtualizedList } from 'react-native'; // same, core component
```
दोनों में एक जैसा। (बड़ी lists के लिए third-party `@shopify/flash-list` भी option है — alag install लगता है।)

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** `getItemCount` भूल जाना
```jsx
// WRONG: <VirtualizedList data={arr} getItem={...} renderItem={...} />  // getItemCount required
```
✅ **Correct:** `getItem` और `getItemCount` दोनों दो।

❌ **Mistake 2:** `renderItem` में inline heavy function, और `key` नहीं
✅ **Correct:** `keyExtractor` + `React.memo` + `useCallback`।

❌ **Mistake 3:** VirtualizedList को vertical `ScrollView` के अंदर रखना
✅ **Correct:** बाहर `ScrollView` मत लगाओ; header/footer के लिए `ListHeaderComponent` use करो (warning: "VirtualizedLists should never be nested").

---

## 🧠 Tricky Interview Question
**Q: 1000 items वाली FlatList में scroll तेज़ करने पर blank white area दिखता है। क्यों?**

**Answer:** Windowing की वजह से item render JS thread पर होता है; scroll तेज़ हो तो native scroll JS से आगे निकल जाता है और अभी mount न हुए items की जगह blank दिखती है। Fix: `getItemLayout` (fixed height), `windowSize` बढ़ाना, `initialNumToRender` सही रखना, `React.memo`, हल्के rows। इसका trade-off memory बनाम blank area है।

---

## ⚫ Interview Questions + Answers

**Q1: VirtualizedList और FlatList में क्या फर्क है?**
A1: FlatList, VirtualizedList का wrapper है जो plain array मानता है। VirtualizedList में `getItem` / `getItemCount` से किसी भी data structure का use हो सकता है।

**Q2: Windowing क्या है?**
A2: सिर्फ visible area + उसके आसपास (`windowSize`) के items mount करना, बाकी unmount करके memory बचाना।

**Q3: `getItemLayout` क्यों?**
A3: Item height पहले पता हो तो measure नहीं करना पड़ता; `scrollToIndex` और fast scroll सही चलते हैं।

**Q4: Nested VirtualizedList क्यों warning देता है?**
A4: एक ही direction में nested lists का windowing टूट जाता है; सब items render हो जाते हैं।

**Q5: कब FlashList?**
A5: बहुत बड़ी/complex lists में cell recycling से बेहतर performance चाहिए तो `@shopify/flash-list`।

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Data array नहीं है (Map, Immutable, database cursor)
- Custom list component बना रहे हो

❌ **Avoid when:**
- साधारण array हो → FlatList सीधा use करो
- Grouped data हो → SectionList
- 10–20 items → ScrollView काफी है

---

## 📊 Visual Diagram
```
  data (10,000)
  ┌────────────┐
  │ blank      │ ← unmounted
  │ [mounted]  │
  │ [visible]  │ ← screen
  │ [mounted]  │
  │ blank      │ ← unmounted
  └────────────┘
  ScrollView → VirtualizedList → FlatList / SectionList
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Windowing | Render only nearby items | पास के items ही render |
| getItem | Return item at index | Index से item |
| getItemCount | Total item count | कुल items |
| windowSize | Render window in screen heights | Window का आकार |
| getItemLayout | Fixed size hint | Fixed size की जानकारी |

---

## ⚡ 3-Line Summary
**English:**
1. VirtualizedList is the base of FlatList and SectionList.
2. It renders only visible items and supports custom data via getItem/getItemCount.
3. Use FlatList normally; VirtualizedList for non-array data.

**Hindi:**
1. VirtualizedList, FlatList और SectionList का base है।
2. सिर्फ दिखने वाले items render करता है, custom data भी चलता है।
3. आम तौर पर FlatList; non-array data के लिए VirtualizedList।

---

## ➡️ Next Topic
**45. Styling in React Native** — CSS नहीं, JS objects से styling।
