# 159. FlatList Performance Optimization
# हिंदी में: FlatList को तेज़ बनाना
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: **Expo SDK 52 (check current docs — APIs change between SDKs)**, RN 0.76. सभी props (`initialNumToRender`, `windowSize`, `maxToRenderPerBatch`, `removeClippedSubviews`, `getItemLayout`, `keyExtractor`) core `FlatList`/`VirtualizedList` के हैं। (विस्तार के लिए 156 देखो।)

---

## 🔵 Simple Definition (English)
**FlatList optimization** is tuning the list so it renders only what is needed: few items at start, stable keys, fixed item heights, memoized rows, and a small render window. This keeps scroll smooth and memory low even with thousands of items.

## 🔵 सरल परिभाषा (Hindi)
**FlatList optimization** का मतलब list को ऐसे tune करना कि सिर्फ ज़रूरी items render हों: शुरू में कम items, stable keys, fixed height, memoized rows और छोटी render window। इससे हज़ारों items होने पर भी scroll smooth रहता है।

---

## 🔴 Problem it Solves
```
FlatList default: windowSize=21 (screen के 10 ऊपर + 10 नीचे), batch=10
Heavy row + fast scroll → blank white area, dropped frames, high RAM

Problems:
  ❌ Blank cells while fast scrolling
  ❌ Whole list re-renders on small state change
  ❌ Slow first paint (renders too many items initially)
  ❌ Scroll jumps when height is unknown
```

## 🔴 यह क्यों बना? (Hindi)
```
FlatList default में screen के ऊपर-नीचे 10-10 screens तक render रखता है।
भारी rows + तेज़ scroll → सफ़ेद खाली जगह, frame drops, ज़्यादा RAM।
Tuning से: कम render, कम memory, तेज़ scroll।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Row को React.memo में लपेटो + renderItem/keyExtractor stable करो
Step 2 → keyExtractor से unique stable id दो (index नहीं)
Step 3 → Fixed height हो तो getItemLayout दो (measure skip)
Step 4 → initialNumToRender घटाओ (पहली screen जितने)
Step 5 → windowSize घटाओ (जैसे 5-7) → कम memory, पर तेज़ scroll पर blank का risk
Step 6 → maxToRenderPerBatch/updateCellsBatchingPeriod tune करो
Step 7 → removeClippedSubviews (Android पर) try करो — test करके
Step 8 → Images छोटी/cached रखो; release build पर measure करो
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Row memo करो, functions stable रखो
Step 2 → keyExtractor में unique id
Step 3 → Fixed height तो getItemLayout
Step 4 → initialNumToRender कम (पहली screen जितना)
Step 5 → windowSize कम = कम memory, पर blank का थोड़ा risk
Step 6 → batch settings tune
Step 7 → removeClippedSubviews आज़माओ (test ज़रूर)
Step 8 → Images छोटी रखो और release build पर मापो
```

---

## 🟡 Real World Example
**Zomato** restaurant list और **Instagram** feed: हज़ारों items, हर item में image + text + button। Optimized FlatList: पहली screen में ~8 cards, `windowSize` छोटी, memoized card, CDN से resized thumbnails, और pagination (`onEndReached`) से अगला पेज।

## 🟡 Real Example Hindi mein
**Zomato** की restaurant list में हज़ारों cards हैं। पहले ~8 cards render होते हैं, `windowSize` छोटी, card memoized, thumbnails छोटे, और `onEndReached` से अगला page आता है — इसलिए सस्ते phone पर भी scroll smooth।

---

## 💻 Code Example — Basic
```jsx
// Basic: सबसे ज़रूरी 5 settings वाली FlatList
import React, { memo, useCallback } from 'react';                     // memo + useCallback
import { FlatList, Text, View, StyleSheet } from 'react-native';      // components

const ROW_H = 72;                                                     // fixed row height (px)

const Row = memo(function Row({ item }) {                             // memoized row
  return (
    <View style={styles.row}>
      <Text>{item.title}</Text>
    </View>
  );
});

const data = Array.from({ length: 2000 }, (_, i) => ({ id: `r${i}`, title: `Restaurant ${i}` })); // demo

export default function BasicList() {
  const renderItem = useCallback(({ item }) => <Row item={item} />, []); // stable renderItem
  const keyExtractor = useCallback((item) => item.id, []);               // stable key
  const getItemLayout = useCallback(                                     // fixed height → fast scroll jump
    (_, index) => ({ length: ROW_H, offset: ROW_H * index, index }), []
  );

  return (
    <FlatList
      data={data}                                                     // list data
      renderItem={renderItem}                                         // row renderer
      keyExtractor={keyExtractor}                                     // unique keys
      getItemLayout={getItemLayout}                                   // pre-known layout
      initialNumToRender={10}                                         // पहली screen भर
      windowSize={7}                                                  // 3 screens ऊपर + 3 नीचे (≈)
      maxToRenderPerBatch={8}                                         // प्रति batch items
      updateCellsBatchingPeriod={50}                                  // batch के बीच ms
      removeClippedSubviews                                           // off-screen native views हटाओ
    />
  );
}

const styles = StyleSheet.create({ row: { height: ROW_H, justifyContent: 'center', paddingHorizontal: 16 } });
```

## 💻 Code Example — Advanced
```jsx
// Advanced: pagination + pull-to-refresh + error/empty states + platform handling
import React, { useState, useCallback, useEffect, memo } from 'react';
import { FlatList, Text, View, ActivityIndicator, Platform, RefreshControl } from 'react-native';

const Card = memo(({ item }) => (<View style={{ padding: 16 }}><Text>{item.name}</Text></View>)); // memo card

export default function Feed() {
  const [items, setItems] = useState([]);                             // loaded items
  const [page, setPage] = useState(1);                                // current page
  const [loading, setLoading] = useState(false);                      // loading flag
  const [refreshing, setRefreshing] = useState(false);                // pull-to-refresh flag
  const [error, setError] = useState(null);                           // error message
  const [done, setDone] = useState(false);                            // सारा data आ गया?

  const load = useCallback(async (p, replace = false) => {
    if (loading || (done && !replace)) return;                        // double-fetch रोको
    setLoading(true); setError(null);                                 // शुरू
    try {
      const res = await fetch(`https://example.com/api/items?page=${p}`); // API call (demo URL)
      if (!res.ok) throw new Error(`HTTP ${res.status}`);             // error check
      const json = await res.json();                                  // parse
      setItems(prev => replace ? json : [...prev, ...json]);          // append या replace
      setDone(json.length === 0);                                     // खाली = खत्म
      setPage(p);                                                     // page update
    } catch (e) {
      setError(e.message);                                            // error दिखाने के लिए
    } finally {
      setLoading(false); setRefreshing(false);                        // flags reset
    }
  }, [loading, done]);

  useEffect(() => { load(1, true); }, []);                            // पहला page

  const onRefresh = useCallback(() => { setRefreshing(true); setDone(false); load(1, true); }, [load]);
  const onEnd = useCallback(() => load(page + 1), [load, page]);      // अगला page

  return (
    <FlatList
      data={items}
      keyExtractor={(i) => String(i.id)}                              // server id
      renderItem={({ item }) => <Card item={item} />}
      onEndReached={onEnd}                                            // नीचे पहुँचने पर
      onEndReachedThreshold={0.5}                                     // आधी screen पहले trigger
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />} // pull to refresh
      ListFooterComponent={loading ? <ActivityIndicator /> : null}    // नीचे spinner
      ListEmptyComponent={!loading && <Text>{error ?? 'Nothing here'}</Text>} // empty/error state
      removeClippedSubviews={Platform.OS === 'android'}               // सिर्फ Android पर
      windowSize={9}
      initialNumToRender={8}
    />
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| `removeClippedSubviews` | Default `true` on Android; helps memory | Default false; can cause glitches/blank on iOS |
| Memory sensitivity | High (low-end devices) | Lower |
| Overscroll | Glow / stretch | Bounce |
| `windowSize` effect | Smaller values help RAM more | Usually fine with default |
| Scroll perf | Needs more tuning | Generally smoother out of the box |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// core FlatList वही। बेहतर perf के लिए: npx expo install @shopify/flash-list
// FlashList Expo Go में चलता है (SDK 52 docs जाँचो)
import { FlashList } from '@shopify/flash-list';
<FlashList data={data} renderItem={renderItem} estimatedItemSize={72} />
```
CLI way:
```jsx
// npm i @shopify/flash-list && cd ios && pod install
import { FlashList } from '@shopify/flash-list';
<FlashList data={data} renderItem={renderItem} estimatedItemSize={72} />
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `keyExtractor` में `index` इस्तेमाल करना (reorder/insert पर bugs)।
✅ Correct: Unique stable `id` इस्तेमाल करो।

❌ Mistake 2: `ScrollView` + `.map()` बड़ी list के लिए।
✅ Correct: `FlatList`/`FlashList`।

❌ Mistake 3: `renderItem` में inline arrow + heavy component बिना memo।
✅ Correct: Row को `memo` करो, `renderItem` को `useCallback`।

❌ Mistake 4: `windowSize` बहुत छोटी (जैसे 1-2) रखना → तेज़ scroll पर blank।
✅ Correct: 5-10 के बीच test करो।

❌ Mistake 5: FlatList को vertical `ScrollView` के अंदर रखना (virtualization टूटती है + warning)।
✅ Correct: `ListHeaderComponent` का इस्तेमाल करो।

---

## 🧠 Tricky Interview Question
"FlatList में `extraData` न देने पर selected item का highlight क्यों नहीं बदलता, जबकि `selectedId` state बदल गई?"

Answer: FlatList `PureComponent` है; सिर्फ `data` और अन्य props की shallow तुलना करता है। `selectedId` renderItem के closure में है, props में नहीं, इसलिए FlatList को बदलाव नहीं दिखता। Fix: `extraData={selectedId}` दो। साथ ही `renderItem` को `useCallback` करो तो deps में `selectedId` रखो।

---

## ⚫ Interview Questions + Answers
Q1: FlatList ScrollView से कैसे बेहतर?
A1: Virtualization — सिर्फ visible (और window के) items render; बाकी unmount → कम memory।

Q2: `initialNumToRender` क्या करता है?
A2: पहले render में कितने items बनें। सिर्फ पहली screen भर रखो; ज़्यादा = धीमा first paint।

Q3: `onEndReachedThreshold` क्या है?
A3: End से कितनी दूरी (visible length का गुणक) पर `onEndReached` चले। 0.5 = आधी screen पहले।

Q4: FlatList vs FlashList?
A4: FlashList (Shopify) cell recycling करता है, इसलिए तेज़ है; `estimatedItemSize` चाहिए (v1)। नए version के docs जाँचो।

Q5: Blank cells क्यों दिखते हैं?
A5: तेज़ scroll पर JS नई rows जल्दी render नहीं कर पाता। Fix: row हल्की करो, memo, `getItemLayout`, `windowSize` बढ़ाओ।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- 50+ items वाली कोई भी list
- Feed, chat, orders, products

❌ Avoid when:
- 5-10 fixed items (साधारण `View` ठीक है)
- Variable-height rows पर `getItemLayout` (ग़लत offsets देगा)

---

## 📊 Visual Diagram
```
 [ windowSize = 5 → 2 screens ऊपर | 1 visible | 2 screens नीचे ]
 ┌─────────── rendered window ───────────┐
 │ unmounted ░░ │ rendered ███ │ ░░ unmounted │
 └───────────────────────────────────────┘
 scroll ↓ → window आगे खिसकती है, पीछे की rows हटती हैं
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Virtualization | Render only what's near viewport | सिर्फ दिखने वाले items render |
| windowSize | Render window in screen heights | Render window का आकार |
| keyExtractor | Unique key per row | हर row की unique key |
| extraData | Extra value to trigger re-render | अतिरिक्त re-render trigger |
| FlashList | Recycling list by Shopify | Shopify की तेज़ list |

---

## ⚡ 3-Line Summary
English: Optimize FlatList with memoized rows, stable keys, getItemLayout, small initial count and tuned window. Never nest it in a ScrollView. Always test on a release build on a low-end phone.
Hindi: FlatList को memoized rows, stable keys, getItemLayout, कम initial count और tuned window से तेज़ करो। इसे ScrollView में मत रखो। हमेशा सस्ते phone के release build पर test करो।

---

## ➡️ Next Topic
**160. getItemLayout** — fixed height बताकर measurement बचाना।
