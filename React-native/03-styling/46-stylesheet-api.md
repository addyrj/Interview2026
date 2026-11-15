# 46. StyleSheet API
# हिंदी में: StyleSheet API
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 (React Native 0.76) — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
**StyleSheet** is the React Native helper for defining styles in one place. `StyleSheet.create()` groups named styles, and it also gives utilities like `flatten`, `compose`, `absoluteFill` and `hairlineWidth`.

## 🔵 सरल परिभाषा (Hindi)
**StyleSheet** styles को एक जगह define करने का helper है। `StyleSheet.create()` named styles का group बनाता है, और `flatten`, `compose`, `absoluteFill`, `hairlineWidth` जैसी utilities भी देता है।

---

## 🔴 Problem it Solves
```
BEFORE:
❌ हर element पर inline objects → messy, repeat code
❌ Typo (जैसे backgroundColour) dev में देर से पकड़ में आता
❌ Styles एक जगह नहीं → maintain करना मुश्किल
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
❌ हर element पर inline objects → गंदा code
❌ Typo की गलती देर से पता चलती
❌ Styles बिखरी हुई → maintain मुश्किल
StyleSheet: एक जगह, named, validated styles
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → const styles = StyleSheet.create({ box: {...} })
Step 2 → create() dev में properties validate करता है (TypeScript में types भी)
Step 3 → <View style={styles.box} /> से use करो
Step 4 → Multiple: style={[styles.a, styles.b]}
Step 5 → StyleSheet.flatten([...]) से एक plain object निकालो
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → StyleSheet.create({ box: {...} }) लिखो
Step 2 → Dev में properties check होती हैं
Step 3 → style={styles.box} से use करो
Step 4 → कई styles: style={[styles.a, styles.b]}
Step 5 → flatten() से एक single object बनाओ
```

---

## 🟡 Real World Example
**Paytm** के payment screen में `styles.amountText`, `styles.successBadge`, `styles.row` जैसे named styles एक ही file के नीचे रखे जाते हैं; `StyleSheet.absoluteFill` से full-screen overlay (loading) और `hairlineWidth` से बारीक divider lines बनती हैं।

## 🟡 Real Example Hindi mein
**Paytm** के payment screen में `styles.amountText`, `styles.row` जैसे named styles एक ही file में रखे जाते हैं; `absoluteFill` से full-screen loading overlay और `hairlineWidth` से पतली divider line बनती है।

---

## 💻 Code Example — Basic

```jsx
// Basic: StyleSheet.create + hairlineWidth + absoluteFill
import React from 'react';                                    // React
import { View, Text, StyleSheet } from 'react-native';        // RN

export default function BasicSheet() {
  return (
    <View style={styles.screen}>                              {/* main container */}
      <Text style={styles.title}>Payment</Text>               {/* title */}
      <View style={styles.divider} />                         {/* thin line */}
      <Text style={styles.amount}>₹499</Text>                 {/* amount */}
      {/* Overlay poori screen pe */}
      <View style={styles.overlay}><Text>Loading...</Text></View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, padding: 20 },                           // full screen
  title: { fontSize: 20, fontWeight: '700' },                 // heading
  divider: { height: StyleSheet.hairlineWidth, backgroundColor: '#999', marginVertical: 12 }, // 1 physical px
  amount: { fontSize: 32 },                                   // amount
  overlay: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(255,255,255,0.8)', alignItems: 'center', justifyContent: 'center' }, // cover all
});
```

## 💻 Code Example — Advanced

```jsx
// Advanced: flatten, compose, style factory with theme + validation helper
import React, { useMemo } from 'react';                       // hooks
import { View, Text, StyleSheet, useWindowDimensions } from 'react-native'; // RN

// Style factory: props ke hisaab se StyleSheet banao
const makeStyles = (primary, compact) =>
  StyleSheet.create({
    btn: { backgroundColor: primary, padding: compact ? 8 : 16, borderRadius: 8 }, // dynamic padding
    label: { color: '#fff', fontWeight: '600' },              // text
  });

export default function Button({ primary = '#5f259f', compact = false, style, children }) {
  const { width } = useWindowDimensions();                    // screen width
  // useMemo: har render pe nayi sheet na bane
  const s = useMemo(() => makeStyles(primary, compact), [primary, compact]);

  // compose: do styles ko ek me jodta hai (array banata hai), flatten: object banata hai
  const merged = StyleSheet.flatten(StyleSheet.compose(s.btn, style)); // user override allowed
  console.log('final style', merged);                         // flatten ka result: plain object

  return (
    <View style={[merged, { width: width * 0.9 }]}>           {/* 90% width */}
      <Text style={s.label}>{children}</Text>
    </View>
  );
}
// Use: <Button style={{ backgroundColor: 'green' }}>Pay</Button>
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| `StyleSheet.create` | same | same |
| `hairlineWidth` | 1 physical pixel (density पर) | 1 physical pixel (0.33–0.5 pt) |
| `elevation` in sheet | काम करता है | ignore |
| `shadow*` in sheet | ignore | काम करता है |

---

## 🟠 Expo vs CLI Difference
**Expo way:**
```jsx
import { StyleSheet } from 'react-native'; // core
// Expo Router/TS template me type hints ready aate hain
```
**CLI way:**
```jsx
import { StyleSheet } from 'react-native'; // identical
// TS use karna ho to project init template me TypeScript option lo
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** `StyleSheet.create` render के अंदर बार-बार चलाना
✅ **Correct:** Component के बाहर (module level) बनाओ; dynamic ज़रूरत हो तो `useMemo`।

❌ **Mistake 2:** यह सोचना कि `StyleSheet.create` हमेशा ID लौटाता है और उससे fast हो जाता है
✅ **Correct:** नए RN में यह मुख्यतः identity function जैसा है; फ़ायदा organization/type-checking है। (Version-dependent behaviour — docs देखो।)

❌ **Mistake 3:** `styles.box.padding` से value पढ़ना
```jsx
// WRONG: styles.box.padding  // nahi bharosemand
// CORRECT: StyleSheet.flatten(styles.box).padding
```
✅ **Correct:** `flatten` use करो।

---

## 🧠 Tricky Interview Question
**Q: `StyleSheet.create` use न करें, plain object दें तो क्या टूटेगा?**

**Answer:** कुछ नहीं टूटेगा — plain objects भी चलते हैं। `create` से dev-time validation, autocomplete (TS), और एक जगह organization मिलता है। पुराने RN versions में यह style को numeric ID में बदलकर bridge पर कम data भेजता था; नए architecture में यह फ़र्क ना के बराबर है।

---

## ⚫ Interview Questions + Answers

**Q1: `absoluteFill` और `absoluteFillObject` में फर्क?**
A1: दोनों `position:'absolute'` और top/left/right/bottom 0 हैं; `absoluteFillObject` plain object है जिसे spread कर सकते हैं।

**Q2: `hairlineWidth` क्या है?**
A2: Platform की सबसे पतली line की width (1 physical pixel)। Dividers के लिए।

**Q3: `flatten` कब?**
A3: जब style array से एक single object चाहिए (value पढ़ने/merge करने)।

**Q4: `compose` क्या?**
A4: दो styles को एक style array में जोड़ता है (`null` safe)।

**Q5: Dynamic styles कैसे?**
A5: Inline override array में, या `makeStyles(theme)` factory + `useMemo`।

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- सभी components (default practice)
- Reusable design tokens

❌ **Avoid when:**
- कुछ properties animated हों → `Animated.Value` inline में दो
- रोज़ बदलते dynamic values → inline override

---

## 📊 Visual Diagram
```
 StyleSheet.create({a,b})
        │
        ├── styles.a ──► <View style={styles.a}/>
        ├── [styles.a, styles.b] ─► merge (b wins)
        └── flatten([a,b]) ─► { ...a, ...b }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| create | Define named styles | Named styles बनाना |
| flatten | Merge to one object | एक object में merge |
| compose | Join two styles | दो styles जोड़ना |
| absoluteFill | Cover parent fully | पूरे parent को ढकना |
| hairlineWidth | Thinnest line | सबसे पतली line |

---

## ⚡ 3-Line Summary
**English:**
1. StyleSheet.create keeps styles organised and validated.
2. flatten/compose merge styles; absoluteFill and hairlineWidth are helpers.
3. Create at module level; use factory + useMemo for dynamic styles.

**Hindi:**
1. StyleSheet.create styles को व्यवस्थित और validated रखता है।
2. flatten/compose merge करते हैं; absoluteFill और hairlineWidth helpers हैं।
3. Module level पर बनाओ; dynamic के लिए factory + useMemo।

---

## ➡️ Next Topic
**47. Flexbox in React Native** — layout की असली ताकत।
