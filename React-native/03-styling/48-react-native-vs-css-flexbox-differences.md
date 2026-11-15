# 48. React Native vs CSS Flexbox Differences
# हिंदी में: React Native और CSS Flexbox के अंतर
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 (React Native 0.76) — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
React Native uses **Yoga**, a Flexbox implementation similar to CSS but with different defaults: `flexDirection` is **column**, `alignContent` is `flex-start`, `flexShrink` is **0**, and there is no `display: block/inline/grid`, no floats, no cascade.

## 🔵 सरल परिभाषा (Hindi)
React Native **Yoga** engine use करता है, जो CSS Flexbox जैसा है पर defaults अलग हैं: `flexDirection` **column**, `alignContent` `flex-start`, `flexShrink` **0**, और `display: block/inline/grid`, float, cascade नहीं हैं।

---

## 🔴 Problem it Solves
```
Web developer का assumption:
❌ "flex है तो row होगा" → RN में column निकलता है
❌ `display: grid`, `float`, `calc()` की उम्मीद
❌ "flex: 1" का web और RN में थोड़ा अलग मतलब
इन अंतरों को न जानने से layout bugs आते हैं
```

## 🔴 यह क्यों बना? (Hindi)
```
Web developer की गलत धारणा:
❌ "flex है तो row होगा" → RN में column होता है
❌ grid, float, calc() मिलेंगे ऐसा सोचना
❌ flex:1 का मतलब अलग हो सकता है
इन अंतरों को जानना ज़रूरी है ताकि layout bugs न आएँ
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → हर View पहले से display:flex है (display:'none' भी है)
Step 2 → Default: flexDirection column, flexShrink 0, position relative
Step 3 → Sizes unitless numbers या '50%' string
Step 4 → position:'absolute' parent के सापेक्ष (अगला relative parent)
Step 5 → Cascade/inheritance नहीं; styles element-specific
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर View default में flex container है
Step 2 → Defaults: column, flexShrink 0, position relative
Step 3 → Size: unitless numbers या '50%'
Step 4 → absolute position अपने parent के सापेक्ष
Step 5 → Cascade/inheritance नहीं
```

---

## 🟡 Real World Example
Zomato की web team React (CSS) पर और app team RN पर काम करे तो web में `.card { display: flex }` row बनाता है, पर RN में वही `View` बिना `flexDirection: 'row'` के items को ऊपर-नीचे रखेगा। **Paytm** के web और app UI के बीच code share करते समय यही अंतर सबसे ज़्यादा bugs देता है।

## 🟡 Real Example Hindi mein
Zomato की web team CSS पर और app team RN पर काम करे तो web का `display:flex` row बनाता है, पर RN का View `flexDirection:'row'` के बिना items ऊपर-नीचे रखता है। **Paytm** के web और app के बीच code share करते समय यही सबसे ज़्यादा bugs देता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: CSS-jaisa soch vs RN reality
import React from 'react';                               // React
import { View, Text, StyleSheet } from 'react-native';   // RN

export default function Compare() {
  return (
    <View style={styles.screen}>
      {/* Bina flexDirection: items upar-neeche (column default) */}
      <View style={styles.box}><Text>A</Text><Text>B</Text></View>
      {/* Row: web jaisa behaviour chahiye to explicitly likho */}
      <View style={[styles.box, { flexDirection: 'row' }]}><Text>A </Text><Text>B</Text></View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, padding: 20, gap: 12 },             // screen (gap: RN 0.71+)
  box: { padding: 12, backgroundColor: '#eee' },         // grey box
});
```

## 💻 Code Example — Advanced

```jsx
// Advanced: web-style features RN me kaise banate hain
import React from 'react';                                    // React
import { View, Text, ScrollView, StyleSheet, useWindowDimensions } from 'react-native'; // RN

export default function WebToRN() {
  const { width } = useWindowDimensions();                    // calc(100% - 32px) ka replacement
  const cardW = width - 32;                                   // JS me calculation

  return (
    <ScrollView contentContainerStyle={styles.content}>
      {/* 1) calc() nahi hota: JS se width nikaalo */}
      <View style={{ width: cardW, backgroundColor: '#fde68a', padding: 12 }}>
        <Text>width = screen - 32</Text>
      </View>

      {/* 2) float/grid nahi: row + flexWrap + percentage */}
      <View style={styles.grid}>
        {[1, 2, 3, 4].map(n => (
          <View key={n} style={styles.cell}><Text>{n}</Text></View> // 48% => do column
        ))}
      </View>

      {/* 3) box-shadow nahi: platform props */}
      <View style={styles.shadow}><Text>Shadow</Text></View>

      {/* 4) :hover nahi; Pressable ka pressed state use hota hai */}
      {/* 5) Text inheritance: sirf Text-in-Text me */}
      <Text style={{ color: 'red', fontSize: 18 }}>
        Parent <Text style={{ fontWeight: 'bold' }}>nested inherits red + size</Text>
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: { padding: 16, gap: 12 },                          // spacing
  grid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between', rowGap: 8 }, // 2-col grid
  cell: { width: '48%', padding: 16, backgroundColor: '#bfdbfe' }, // 48% width
  shadow: { padding: 16, backgroundColor: '#fff', elevation: 4, shadowColor: '#000', shadowOpacity: 0.2, shadowRadius: 5, shadowOffset: { width: 0, height: 2 } }, // both platforms
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Layout engine result | Yoga | Yoga (same) |
| Box shadow | `elevation` | `shadow*` |
| `borderStyle: 'dotted'` | कुछ cases में solid जैसा (rounded) | ठीक |
| `overflow: 'visible'` | पुराने versions में limited | ठीक |
| Font metrics | Roboto | San Francisco |

---

## 🟠 Expo vs CLI Difference
**Expo way:** (web के लिए भी चलाना हो → react-native-web)
```bash
npx expo install react-dom react-native-web @expo/metro-runtime  # web support
npx expo start --web                                              # browser me
```
**CLI way:**
```bash
# Web support ke liye khud react-native-web + bundler config karna padta hai
npm install react-native-web react-dom
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** `display: 'grid'` या `float` use करना
✅ **Correct:** `flexWrap` + percentage widths या FlatList `numColumns`।

❌ **Mistake 2:** `width: '100vw'`, `calc()`, `rem`, `em`
✅ **Correct:** `useWindowDimensions`, unitless numbers।

❌ **Mistake 3:** Child के `margin: 'auto'` से center की उम्मीद सब जगह
✅ **Correct:** Parent में `alignItems`/`justifyContent`। (नए RN में `auto` margin कुछ cases में support है — docs देखो।)

---

## 🧠 Tricky Interview Question
**Q: Web में `flex: 1` और RN में `flex: 1` बराबर हैं?**

**Answer:** लगभग, पर RN में `flex: 1` का मतलब positive होने पर `flexGrow:1, flexShrink:1, flexBasis:0` जैसा है; web में `flex: 1` = `1 1 0%`। मुख्य अंतर defaults का है: RN `flexShrink` default 0 और `flexDirection` column है, जबकि web में shrink 1 और direction row है। इसलिए खाली `flex` set किए बिना RN children shrink नहीं होते — text overflow हो सकता है।

---

## ⚫ Interview Questions + Answers

**Q1: तीन सबसे बड़े अंतर?**
A1: Default column; no `display:grid/inline/float`; units नहीं और cascade नहीं।

**Q2: `alignContent` default?**
A2: RN में `flex-start`, web में `stretch`/`normal`।

**Q3: CSS selectors / media queries?**
A3: नहीं। `useWindowDimensions`/`Platform` से conditional styles।

**Q4: `position`?**
A4: Default `relative`; `absolute` supported; `fixed`/`sticky` नहीं (sticky header के लिए `stickyHeaderIndices`)।

**Q5: Percentage का base?**
A5: Parent का size।

---

## 🔷 When to Use + When Not to Use
✅ **Use this knowledge when:**
- Web developer RN सीख रहा हो
- Web और mobile code share करना हो

❌ **Avoid:**
- CSS जैसा behaviour assume करना बिना test किए

---

## 📊 Visual Diagram
```
 CSS (web)                 React Native
 ─────────────────         ─────────────────
 flex-direction: row       flexDirection: column
 flex-shrink: 1            flexShrink: 0
 display: block/grid...    only flex (+ none)
 cascade / inheritance     none (except Text in Text)
 units: px, %, vw, rem     unitless dp, %
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Yoga | RN's Flexbox engine | RN का flexbox engine |
| Cascade | CSS style inheritance chain | CSS की inheritance |
| flexShrink | Shrink when no space | जगह कम हो तो सिकुड़ना |
| react-native-web | RN for browsers | Browser में RN |
| Media query | CSS screen-based rule | Screen के हिसाब से rule |

---

## ⚡ 3-Line Summary
**English:**
1. RN Flexbox is like CSS but defaults differ (column, shrink 0).
2. No grid, float, cascade or CSS units.
3. Use JS (dimensions, Platform) in place of calc and media queries.

**Hindi:**
1. RN Flexbox CSS जैसा है पर defaults अलग हैं (column, shrink 0)।
2. Grid, float, cascade, CSS units नहीं हैं।
3. calc और media queries की जगह JS (dimensions, Platform) use करो।

---

## ➡️ Next Topic
**50. useWindowDimensions Hook** — live screen size और rotation के साथ।
