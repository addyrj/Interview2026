# 160. getItemLayout
# हिंदी में: getItemLayout (Items की जगह पहले से बताना)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: **Expo SDK 52 (check current docs — APIs change between SDKs)**, RN 0.76. `getItemLayout` core `FlatList`/`SectionList`/`VirtualizedList` का prop है।

---

## 🔵 Simple Definition (English)
`getItemLayout` is a FlatList prop: a function `(data, index) => ({ length, offset, index })` that tells the list the exact height (or width) and position of each row **without measuring it**. It works only when all rows have a known/fixed size.

## 🔵 सरल परिभाषा (Hindi)
`getItemLayout` FlatList का prop है: function `(data, index) => ({ length, offset, index })` जो list को हर row की सटीक height/width और position **बिना measure किए** बता देता है। यह तभी काम करता है जब सभी rows की size पता/fixed हो।

---

## 🔴 Problem it Solves
```
बिना getItemLayout:
  FlatList हर row को render करके measure करता है (async layout)
  scrollToIndex(500) → उस index तक की rows की height पता नहीं
     → error: "scrollToIndex out of range: ... getItemLayout" / wrong jump
  Scrollbar size बार-बार बदलता है, fast scroll में blank

getItemLayout के साथ:
  offset = index * height → तुरंत गणना, कोई measure नहीं
```

## 🔴 यह क्यों बना? (Hindi)
```
बिना इसके FlatList को हर row render करके उसकी height नापनी पड़ती है।
scrollToIndex(500) पर 500 rows की height अज्ञात → error या ग़लत जगह।
getItemLayout से position = index × height, तुरंत → तेज़ और सही।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → तय करो कि हर row की height fixed है (जैसे 72)
Step 2 → function दो: (data, index) => ({ length: 72, offset: 72*index, index })
Step 3 → FlatList को layout पहले से पता → measurement skip
Step 4 → scrollToIndex / initialScrollIndex सीधे सही offset पर जाते हैं
Step 5 → अगर separator है: offset में separator height भी जोड़ो
Step 6 → Header हो तो offset में header height भी जोड़नी पड़ सकती है (ListHeaderComponent अलग गिनी जाती है — test करो)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पक्का करो कि हर row की height fixed है
Step 2 → (data, index) => ({ length, offset, index }) लौटाओ
Step 3 → measurement skip होता है
Step 4 → scrollToIndex / initialScrollIndex सही जगह जाते हैं
Step 5 → Separator हो तो उसकी height offset में जोड़ो
```

---

## 🟡 Real World Example
**WhatsApp chat list / Contacts list**: हर contact row की height fixed (जैसे 72). "A-Z" side index पर tap करने पर `scrollToIndex` से तुरंत उस letter तक कूदना। **Paytm** की transaction history में भी fixed-height rows पर `initialScrollIndex` से "last viewed" जगह खुलती है।

## 🟡 Real Example Hindi mein
**WhatsApp/Contacts** में हर row की height fixed होती है। Side के A-Z index पर tap करते ही `scrollToIndex` से सीधे उस अक्षर पर कूदना `getItemLayout` की वजह से संभव है। **Paytm** की history list में भी `initialScrollIndex` से पिछली जगह पर खुलना।

---

## 💻 Code Example — Basic
```jsx
// Basic: fixed height rows + scrollToIndex
import React, { useRef, useCallback } from 'react';                  // hooks
import { FlatList, Text, View, Pressable, StyleSheet } from 'react-native'; // components

const ITEM_HEIGHT = 60;                                              // हर row की height

const data = Array.from({ length: 1000 }, (_, i) => ({ id: String(i), name: `Contact ${i}` })); // demo data

export default function Contacts() {
  const listRef = useRef(null);                                      // FlatList ref

  const getItemLayout = useCallback((_, index) => ({                 // layout function
    length: ITEM_HEIGHT,                                             // row की height
    offset: ITEM_HEIGHT * index,                                     // top से दूरी
    index,                                                           // row index
  }), []);                                                           // stable reference

  const jump = () => listRef.current?.scrollToIndex({ index: 500, animated: true }); // 500वीं row पर जाओ

  return (
    <View style={{ flex: 1 }}>
      <Pressable onPress={jump}><Text>Jump to 500</Text></Pressable>{/* button */}
      <FlatList
        ref={listRef}                                                // ref जोड़ो
        data={data}
        keyExtractor={(i) => i.id}
        getItemLayout={getItemLayout}                                // measurement skip
        renderItem={({ item }) => (
          <View style={styles.row}><Text>{item.name}</Text></View>   // fixed-height row
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  row: { height: ITEM_HEIGHT, justifyContent: 'center', paddingHorizontal: 16 }, // वही height
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: separator + variable height (पहले से ज्ञात) + safe scrollToIndex fallback
import React, { useRef, useMemo, useCallback } from 'react';
import { FlatList, Text, View } from 'react-native';

const SEP = 1;                                                       // separator की height
const H = 64;                                                        // normal row
const HEADER_ROW_H = 40;                                             // date header row (अलग height)

// हर item में type है: 'header' या 'tx'. Heights पहले से पता हैं → offsets precompute
function buildOffsets(items) {
  const offsets = [];                                                // हर index का offset
  let acc = 0;                                                       // चलता योग
  items.forEach((it, i) => {
    const length = it.type === 'header' ? HEADER_ROW_H : H;          // इस row की height
    offsets.push({ length, offset: acc, index: i });                 // layout रिकॉर्ड
    acc += length + SEP;                                             // अगली row के लिए (separator सहित)
  });
  return offsets;
}

export default function History({ items }) {
  const ref = useRef(null);                                          // list ref
  const layouts = useMemo(() => buildOffsets(items), [items]);       // सिर्फ items बदलने पर

  const getItemLayout = useCallback(
    (_, index) => layouts[index],                                    // O(1) lookup
    [layouts]
  );

  const onScrollToIndexFailed = useCallback((info) => {              // अगर फिर भी fail हो
    ref.current?.scrollToOffset({ offset: info.averageItemLength * info.index, animated: false }); // approx पर जाओ
    setTimeout(() => ref.current?.scrollToIndex({ index: info.index }), 100); // फिर सही जगह
  }, []);

  return (
    <FlatList
      ref={ref}
      data={items}
      keyExtractor={(i) => i.id}
      getItemLayout={getItemLayout}
      onScrollToIndexFailed={onScrollToIndexFailed}                  // safe fallback
      ItemSeparatorComponent={() => <View style={{ height: SEP, backgroundColor: '#ddd' }} />} // 1px line
      renderItem={({ item }) => (
        <View style={{ height: item.type === 'header' ? HEADER_ROW_H : H, justifyContent: 'center' }}>
          <Text>{item.title}</Text>
        </View>
      )}
    />
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| API | Same JS prop | Same JS prop |
| Rounding of heights | Density-based (dp), small drift possible | pt-based, small drift possible |
| Wrong value effect | Rows overlap/jump | Rows overlap/jump |
| Benefit | Smoother fast scroll on low-end | Same, smaller |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// कोई extra setup नहीं (core RN prop)
<FlatList getItemLayout={(_, i) => ({ length: 60, offset: 60 * i, index: i })} />
```
CLI way:
```jsx
// वही; FlashList इस्तेमाल करो तो getItemLayout की जगह estimatedItemSize/overrideItemLayout
<FlatList getItemLayout={(_, i) => ({ length: 60, offset: 60 * i, index: i })} />
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Variable-height rows (text wrap) पर fixed `getItemLayout`।
✅ Correct: Height unknown हो तो इसे मत दो; `onScrollToIndexFailed` संभालो।

❌ Mistake 2: Separator height offset में नहीं जोड़ना → धीरे-धीरे drift।
✅ Correct: `offset = (H + SEP) * index`।

❌ Mistake 3: `numColumns > 1` पर index के हिसाब से offset गिनना।
✅ Correct: Row index = `Math.floor(index / numColumns)` से गिनो।

❌ Mistake 4: Layout value और असली style height अलग (60 बनाम 64)।
✅ Correct: एक constant दोनों जगह इस्तेमाल करो।

---

## 🧠 Tricky Interview Question
"`getItemLayout` दिया, पर `ListHeaderComponent` भी है, और `scrollToIndex({index: 3})` थोड़ा ऊपर-नीचे पहुँचता है। क्यों?"

Answer: `getItemLayout` सिर्फ data items का layout बताता है। Header की height अलग है, इसलिए offset में उसका योगदान हो सकता है; ऐसे में `viewOffset` या offset में header height जोड़कर देखो। ठीक व्यवहार RN version पर निर्भर हो सकता है, इसलिए device पर test करो।

---

## ⚫ Interview Questions + Answers
Q1: getItemLayout कब ज़रूरी है?
A1: `scrollToIndex`, `initialScrollIndex` और बहुत तेज़ scroll वाली fixed-height lists में।

Q2: इसमें `index` क्यों लौटाते हैं?
A2: Return object का shape `{length, offset, index}` है जो VirtualizedList इस्तेमाल करता है।

Q3: Dynamic height पर क्या करें?
A3: Layout पहले से compute करो (known heights) या इसे न दो और `onScrollToIndexFailed` लगाओ; या FlashList।

Q4: Performance कैसे बढ़ता है?
A4: Layout measure (async) बचता है, scroll position गणना O(1) होती है।

Q5: ग़लत value देने पर क्या?
A5: Rows overlap, blank gaps या scroll jumps — कोई error नहीं आता, इसलिए सावधान।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- सभी rows की height fixed हो
- `scrollToIndex`/`initialScrollIndex` चाहिए

❌ Avoid when:
- Text/image से बदलती height
- Expand/collapse rows

---

## 📊 Visual Diagram
```
 index:   0    1    2    3
 height: [60] [60] [60] [60]
 offset:  0    60  120  180   ← offset = 60 × index
 scrollToIndex(3) → सीधे 180px (कोई measure नहीं)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| length | Row size on scroll axis | Row की लंबाई/height |
| offset | Distance from list start | शुरुआत से दूरी |
| scrollToIndex | Jump to row index | किसी index पर कूदना |
| initialScrollIndex | Start at given row | शुरुआती row |
| Virtualization | Render only near viewport | सिर्फ पास की rows render |

---

## ⚡ 3-Line Summary
English: getItemLayout tells FlatList each row's size and offset in advance. It enables instant scrollToIndex and avoids measuring. Use only with known sizes; wrong values cause jumps.
Hindi: getItemLayout FlatList को हर row की size और offset पहले से बताता है। इससे scrollToIndex तुरंत चलता है और measure नहीं करना पड़ता। सिर्फ ज्ञात size पर इस्तेमाल करो; ग़लत value से jumps आते हैं।

---

## ➡️ Next Topic
**161. keyExtractor** — rows की पहचान: सही key क्यों ज़रूरी है।
