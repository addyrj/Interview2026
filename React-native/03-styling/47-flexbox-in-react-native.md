# 47. Flexbox in React Native
# हिंदी में: React Native में Flexbox
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 (React Native 0.76) — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
**Flexbox** is the layout system of React Native. A container (View) arranges its children along a **main axis** (`flexDirection`) and a **cross axis**, using `justifyContent`, `alignItems`, `flex`, `flexWrap` and `gap`.

## 🔵 सरल परिभाषा (Hindi)
**Flexbox** React Native का layout system है। Container (View) अपने children को **main axis** (`flexDirection`) और **cross axis** पर `justifyContent`, `alignItems`, `flex`, `flexWrap` और `gap` से सजाता है।

---

## 🔴 Problem it Solves
```
BEFORE:
❌ Fixed pixel positions → हर screen size पर टूटता layout
❌ Absolute coordinates से manual गणना
❌ Android/iOS के अलग layout systems
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
❌ Fixed pixels → अलग screen पर layout टूटता
❌ Manual coordinate गणना
❌ Android/iOS के अलग layout systems
Flexbox: जगह के हिसाब से अपने-आप फैलना/सिकुड़ना
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Parent View: flexDirection तय करता है (default column ↓)
Step 2 → justifyContent: main axis पर children की position
Step 3 → alignItems: cross axis पर alignment
Step 4 → Child पर flex: N → बची हुई जगह का हिस्सा
Step 5 → Yoga engine सब कुछ calculate करके native views रखता है
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Parent में flexDirection (default column ↓)
Step 2 → justifyContent: main axis पर position
Step 3 → alignItems: cross axis पर alignment
Step 4 → Child पर flex: N → बची जगह का हिस्सा
Step 5 → Yoga engine calculate करके native views रखता है
```

---

## 🟡 Real World Example
**Zomato** का restaurant row: बाईं तरफ image, बीच में name+rating (`flex: 1`), दाईं तरफ price — यह `flexDirection: 'row'` + `alignItems: 'center'` + `justifyContent: 'space-between'` से बनता है। **Swiggy** का bottom tab bar भी equal-width tabs के लिए `flex: 1` use करता है।

## 🟡 Real Example Hindi mein
**Zomato** के row में बाईं ओर image, बीच में name/rating (`flex: 1`) और दाईं ओर price होता है — `flexDirection: 'row'`, `alignItems: 'center'`, `justifyContent: 'space-between'` से। **Swiggy** के bottom tabs बराबर चौड़ाई के लिए `flex: 1` use करते हैं।

---

## 💻 Code Example — Basic

```jsx
// Basic: row layout with flex ratios
import React from 'react';                                   // React
import { View, Text, StyleSheet } from 'react-native';       // RN

export default function BasicFlex() {
  return (
    <View style={styles.row}>                                {/* horizontal container */}
      <View style={[styles.box, { flex: 1, backgroundColor: '#f87171' }]}><Text>1</Text></View>
      <View style={[styles.box, { flex: 2, backgroundColor: '#60a5fa' }]}><Text>2</Text></View>
      <View style={[styles.box, { flex: 1, backgroundColor: '#34d399' }]}><Text>1</Text></View>
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flex: 1, flexDirection: 'row' },                    // side by side, full height
  box: { alignItems: 'center', justifyContent: 'center' },   // center text in box
});
// Width ratio = 1 : 2 : 1  (flex = remaining space ka hissa)
```

## 💻 Code Example — Advanced

```jsx
// Advanced: Zomato-style card + wrap chips + gap + responsive grid
import React from 'react';                                   // React
import { View, Text, FlatList, StyleSheet, Platform } from 'react-native'; // RN

const tags = ['Pizza', 'Italian', 'Fast Food', 'Desserts', 'Beverages']; // chips

export default function RestaurantRow() {
  return (
    <View style={styles.card}>
      {/* Row: image | info | price */}
      <View style={styles.row}>
        <View style={styles.img} />                          {/* image placeholder */}
        <View style={styles.info}>                           {/* flex:1 => bachi jagah */}
          <Text style={styles.name} numberOfLines={1}>Domino's Pizza - Andheri West</Text>
          <Text style={styles.rating}>⭐ 4.2 • 30 min</Text>
        </View>
        <Text style={styles.price}>₹300</Text>
      </View>

      {/* Chips: flexWrap se agli line me jaate hain */}
      <View style={styles.chips}>
        {tags.map(t => (
          <View key={t} style={styles.chip}><Text>{t}</Text></View>
        ))}
      </View>

      {/* 2-column grid with FlatList numColumns */}
      <FlatList
        data={tags}                                          // items
        numColumns={2}                                       // 2 columns
        keyExtractor={t => t}                                // key
        columnWrapperStyle={{ gap: 8 }}                      // gap between columns
        contentContainerStyle={{ gap: 8 }}                   // gap between rows
        renderItem={({ item }) => <View style={styles.cell}><Text>{item}</Text></View>} // cell
      />
    </View>
  );
}

const styles = StyleSheet.create({
  card: { padding: 12, backgroundColor: '#fff', borderRadius: 12, elevation: Platform.OS === 'android' ? 3 : 0 }, // card
  row: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }, // row layout
  img: { width: 56, height: 56, borderRadius: 8, backgroundColor: '#ddd' }, // thumbnail
  info: { flex: 1, marginHorizontal: 12 },                   // middle takes rest
  name: { fontWeight: '700' },                               // bold name
  rating: { color: '#666', marginTop: 2 },                   // grey
  price: { fontWeight: '600' },                              // price
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginVertical: 10 }, // wrap + gap
  chip: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 16, backgroundColor: '#fde68a' }, // chip
  cell: { flex: 1, padding: 12, backgroundColor: '#eee', borderRadius: 8 }, // grid cell
});
// gap/rowGap/columnGap: RN 0.71+ me available hai (version-dependent)
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Flex engine | Yoga | Yoga (same results) |
| Default `flexDirection` | column | column |
| Text wrapping edge cases | font metrics थोड़े अलग | थोड़े अलग |
| `zIndex` + elevation | elevation order को override कर सकता है | zIndex follow |
| Rounded + `overflow` | कुछ पुराने versions में bugs | ठीक |

---

## 🟠 Expo vs CLI Difference
**Expo way:**
```jsx
// Flexbox core hai — Expo Go me seedha preview, Fast Refresh ke saath
<View style={{ flex: 1, flexDirection: 'row' }} />
```
**CLI way:**
```jsx
// Same code; sirf build alag (npx react-native run-android / run-ios)
<View style={{ flex: 1, flexDirection: 'row' }} />
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Root View पर `flex: 1` भूलना → screen खाली/छोटी
✅ **Correct:** `flex: 1` दो।

❌ **Mistake 2:** `justifyContent` और `alignItems` की axis उलझाना
```jsx
// column: justifyContent = vertical, alignItems = horizontal
// row   : justifyContent = horizontal, alignItems = vertical
```
✅ **Correct:** पहले `flexDirection` देखो।

❌ **Mistake 3:** Fixed `width: 400` हर जगह
✅ **Correct:** `flex`, percentage या `useWindowDimensions`।

---

## 🧠 Tricky Interview Question
**Q: एक `row` में तीन children हैं, एक में `flex: 1`, बाकी में `width: 100`। flex:1 वाला कितना लेगा?**

**Answer:** Fixed width children 100+100 = 200 लेंगे; `flex: 1` वाला **बची हुई पूरी जगह** लेगा (screen width − 200)। `flex` positive number का मतलब "बची जगह का proportion" है, इसलिए अकेला flex child सब कुछ ले लेता है।

---

## ⚫ Interview Questions + Answers

**Q1: Default flexDirection क्या है?**
A1: `column` (वेब में `row` है)।

**Q2: `flex: 1` का मतलब?**
A2: Parent की बची जगह में grow/shrink करो; RN में `flexGrow:1, flexShrink:1, flexBasis:0` जैसा व्यवहार।

**Q3: Center कैसे करें?**
A3: Parent पर `justifyContent:'center'` और `alignItems:'center'`।

**Q4: `flexWrap`?**
A4: जगह कम पड़ने पर items अगली line में जाते हैं (default `nowrap`)।

**Q5: `gap` कब से?**
A5: RN 0.71 से `gap`, `rowGap`, `columnGap` (docs में verify करो)।

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- लगभग हर layout (default तरीका)
- Responsive rows/columns

❌ **Avoid when:**
- Overlay/badge → `position: 'absolute'`
- Float/grid-areas जैसा CSS चाहिए (RN में नहीं)

---

## 📊 Visual Diagram
```
 column (default)          row
 main ↓                    main →
 ┌──────────┐              ┌───┬───┬───┐
 │  A       │  cross →     │ A │ B │ C │ cross ↓
 │  B       │              └───┴───┴───┘
 │  C       │
 └──────────┘
 justifyContent = main axis | alignItems = cross axis
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Main axis | Direction of flexDirection | मुख्य अक्ष |
| Cross axis | Perpendicular axis | आड़ी अक्ष |
| flex | Share of free space | बची जगह का हिस्सा |
| flexWrap | Wrap to next line | अगली line में जाना |
| gap | Space between children | Children के बीच जगह |

---

## ⚡ 3-Line Summary
**English:**
1. Flexbox arranges children by main and cross axis.
2. Default direction is column; flex shares leftover space.
3. justifyContent = main axis, alignItems = cross axis.

**Hindi:**
1. Flexbox children को main और cross axis पर सजाता है।
2. Default column है; flex बची जगह बाँटता है।
3. justifyContent = main axis, alignItems = cross axis।

---

## ➡️ Next Topic
**48. React Native vs CSS Flexbox Differences** — web के आदत वाले mistakes से बचना।
