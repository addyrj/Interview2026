# 282. Interview Problem: Build Infinite Scroll FlatList
# हिंदी में: Infinite Scroll FlatList बनाओ
# Platform: Android ✅ | iOS ✅ | Both ✅
# Difficulty: ⭐⭐⭐ Medium | Asked at: Flipkart, Meesho, Swiggy, Instagram
# Expo SDK 52 / React Native 0.76 (check current docs — APIs change between SDKs)

> Code files in this folder: `InfiniteScrollScreen.jsx`. Copy them into your Expo project and import the main one in `App.js`.
> **Verification note:** syntax-checked with esbuild and rendered under jsdom via react-native-web (initial render + state logic). Real device behaviour (native spinner, gestures) not run. The 10-item first page rendered correctly under jsdom.

---

## 🔴 Problem Statement
Show a product list that loads the next page automatically when the user nears the bottom. Show a footer spinner, stop when there are no more pages, avoid duplicate API calls and duplicate rows.

(Compare with the longer single-file solution in `../277-build-infinite-scroll.md`, which also covers refresh and TypeScript.)

---

## 🔵 Simple Definition (English)
Infinite scroll loads more data as the user scrolls down. FlatList's `onEndReached` tells you when the bottom is near.

## 🔵 सरल परिभाषा (Hindi)
Infinite scroll में यूज़र जैसे-जैसे नीचे जाता है, अगला पेज अपने-आप लोड होता है। FlatList का `onEndReached` बताता है कि नीचे पहुँच गए।

---

## 🔴 Problem it Solves
Loading 10,000 products at once is slow and uses lots of memory. Pagination loads small pages on demand.

## 🔴 यह क्यों बना? (Hindi)
एक साथ 10,000 products लोड करना धीमा है और मेमोरी खाता है। Pagination छोटे-छोटे पेज ज़रूरत पर लोड करता है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → state: items, page, hasMore, loading
Step 2 → load page 1 on mount
Step 3 → onEndReached fires near bottom (threshold)
Step 4 → if loading or !hasMore return (guard)
Step 5 → fetch(page), append only new ids, page+1
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → state: items, page, hasMore, loading
Step 2 → mount पर page 1 लोड करो
Step 3 → नीचे के पास onEndReached चलता है
Step 4 → loading या !hasMore हो तो return (guard)
Step 5 → fetch(page), सिर्फ़ नए id जोड़ो, page+1
```

---

## 🟡 Real World Example
Flipkart search results and Meesho feed keep loading as you scroll; a small spinner shows at the bottom.

## 🟡 Real Example Hindi mein
Flipkart के search results और Meesho फीड स्क्रोल करते रहने पर लोड होते रहते हैं, नीचे छोटा spinner दिखता है।

---

## 💻 Code Example — Basic
```jsx
// Core idea only
<FlatList
  data={items} // accumulated list
  keyExtractor={(i) => i.id} // stable key
  renderItem={renderItem} // row
  onEndReached={loadMore} // call when near bottom
  onEndReachedThreshold={0.5} // 0.5 = half screen before end
  ListFooterComponent={loading ? <ActivityIndicator /> : null} // spinner
/>
```

## 💻 Code Example — Advanced (complete solution, every line commented)
**File: `InfiniteScrollScreen.jsx`**
```jsx
// Expo SDK 52 (check current docs - APIs change between SDKs)
import React, { useState, useEffect, useRef, useCallback, memo } from 'react'; // hooks
import { View, Text, FlatList, ActivityIndicator, StyleSheet } from 'react-native'; // RN core

const PAGE_SIZE = 10; // items per page
const TOTAL = 45; // fake total items on server

// Fake paginated API: page is 1-based
const fetchPage = (page) =>
  new Promise((resolve) =>
    setTimeout(() => {
      const start = (page - 1) * PAGE_SIZE; // first index of this page
      const items = Array.from({ length: PAGE_SIZE }, (_, i) => start + i) // ids
        .filter((n) => n < TOTAL) // stop at TOTAL
        .map((n) => ({ id: 'p' + n, name: 'Product ' + (n + 1) })); // build item
      resolve({ items, hasMore: start + PAGE_SIZE < TOTAL }); // response shape
    }, 500));

const Row = memo(function Row({ item }) { // memo: skip re-render if item same
  return (
    <View style={styles.row}>
      <Text>{item.name}</Text>
    </View>
  );
});

export default function InfiniteScrollScreen() {
  const [items, setItems] = useState([]); // accumulated list
  const [page, setPage] = useState(1); // current page
  const [hasMore, setHasMore] = useState(true); // more pages left?
  const [loading, setLoading] = useState(false); // state for spinner footer
  const loadingRef = useRef(false); // sync guard (state is async, ref is instant)

  const loadMore = useCallback(async () => {
    if (loadingRef.current || !hasMore) return; // block duplicate calls
    loadingRef.current = true; // lock
    setLoading(true); // show footer spinner
    try {
      const res = await fetchPage(page); // fetch current page
      setItems((prev) => { // append without duplicates
        const seen = new Set(prev.map((p) => p.id)); // existing ids
        return [...prev, ...res.items.filter((i) => !seen.has(i.id))]; // only new
      });
      setHasMore(res.hasMore); // update flag
      setPage((p) => p + 1); // next page number
    } finally {
      loadingRef.current = false; // unlock
      setLoading(false); // hide spinner
    }
  }, [page, hasMore]);

  useEffect(() => { loadMore(); }, []); // eslint-disable-line - first page once

  const renderItem = useCallback(({ item }) => <Row item={item} />, []); // stable fn

  return (
    <FlatList
      data={items} // list data
      keyExtractor={(i) => i.id} // id key, not index
      renderItem={renderItem} // row renderer
      onEndReached={loadMore} // reached bottom -> next page
      onEndReachedThreshold={0.5} // fire at half a screen from end
      ListFooterComponent={loading ? <ActivityIndicator style={{ margin: 16 }} /> : null} // bottom spinner
    />
  );
}

const styles = StyleSheet.create({
  row: { padding: 20, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: '#ddd' }, // row style
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| onEndReached firing | Can fire twice quickly on fast fling | Fires once but also on content size change |
| Overscroll | Glow/none | Bounce can re-trigger near end |
| Memory | `removeClippedSubviews` default true | default false (enable manually for long lists) |
| Footer spinner | `ActivityIndicator` Material style | iOS style spinner |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx expo start   # FlatList is core, no extra package
```
CLI way (bare React Native):
```bash
npx react-native run-android   # same FlatList code
```
No difference in code. For very long lists consider `@shopify/flash-list` (works in Expo dev builds too).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using state (`loading`) as the only guard; two calls fire before state updates.
✅ Correct: Use a `useRef` lock for an instant guard (done in our file).

❌ Mistake 2: keyExtractor using array index.
✅ Correct: Use a stable `id` so items do not remount.

❌ Mistake 3: Appending without de-duplication when pages overlap.
✅ Correct: Filter by existing ids using a Set.

---

## 🧠 Tricky Interview Question
`onEndReached` fires immediately on first render with an empty list and loads page 2 before page 1 finishes. Why?

Answer: An empty list is 'already at the end', so onEndReached fires. Guard with the loading lock/ref and `hasMore`; also do not call loadMore from both useEffect and onEndReached without the guard. Hindi: खाली लिस्ट पहले से 'end' पर होती है, इसलिए guard ज़रूरी है।

---

## ⚫ Interview Questions + Answers
Q1: Why React.memo on the row?
A1: Each append re-renders the list; memo skips rows whose props did not change.

Q2: What does onEndReachedThreshold mean?
A2: Distance from the end as a multiple of visible length, e.g. 0.5 means half a screen.

Q3: Offset vs cursor pagination?
A3: Offset (`page=2`) can duplicate/skip if data changes; cursor (`after=id`) is stable. Use cursor for feeds.

Q4: How to refresh too?
A4: Add RefreshControl and reset page to 1, replace list.

Q5: ScrollView vs FlatList here?
A5: FlatList virtualizes rows; ScrollView renders all and will lag.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Long server-side lists (feeds, search)
- Data too large to load at once

❌ Avoid when:
- Short fixed lists (<50 items)
- When users need page numbers/jump to page

---

## 📊 Visual Diagram
```
[ items 1..10 ]  <- page 1
[ items 11..20 ] <- appended when near end
      |
 onEndReached -> guard(loadingRef,hasMore)
      |
 fetchPage(n) -> append -> page = n+1
 footer: <ActivityIndicator/> while loading
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pagination | Loading data in pages | डेटा को पेज में लोड करना |
| onEndReached | Callback near list end | लिस्ट के अंत के पास का callback |
| Threshold | How early to trigger | कितना पहले trigger हो |
| Virtualization | Render only visible rows | सिर्फ़ दिखने वाली rows बनाना |
| Cursor | Pointer to next page | अगले पेज का pointer |

---

## ⚡ 3-Line Summary
English: Use FlatList onEndReached with a guard.
Append new unique items and track hasMore.
Show a footer spinner while loading.
Hindi: FlatList का onEndReached guard के साथ इस्तेमाल करो।
सिर्फ़ नए unique items जोड़ो और hasMore track करो।
लोड होते समय footer में spinner दिखाओ।

---

## ➡️ Next Topic
283 — Build Image Picker + Preview: first native-module problem (permissions + media).
