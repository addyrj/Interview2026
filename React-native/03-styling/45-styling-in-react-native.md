# 45. Styling in React Native
# हिंदी में: React Native में Styling
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 (React Native 0.76) — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
React Native has **no CSS files**. You style components with plain **JavaScript objects** passed to the `style` prop, using camelCase names (`backgroundColor`). Layout is done with Flexbox, and every View is `display: flex` with `flexDirection: 'column'` by default.

## 🔵 सरल परिभाषा (Hindi)
React Native में **CSS files नहीं** होतीं। आप components को **JavaScript objects** से `style` prop में style करते हो, camelCase नाम के साथ (`backgroundColor`)। Layout Flexbox से होता है और हर View default में `flexDirection: 'column'` होता है।

---

## 🔴 Problem it Solves
```
BEFORE (सोचो अगर CSS/HTML native में होते):
❌ Native UI (UIView / android.view.View) CSS नहीं समझते
❌ Cascade, selectors, inheritance से unpredictable styles
❌ दोनों platforms के लिए अलग XML / Storyboard layout
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
❌ Native UI CSS नहीं समझते
❌ CSS cascade से styles अनिश्चित हो जाते हैं
❌ Android में XML और iOS में Storyboard अलग-अलग लिखने पड़ते थे
React Native: JS objects + Flexbox = एक styling system दोनों के लिए
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → आप style object लिखते हो: { padding: 16, backgroundColor: '#fff' }
Step 2 → style prop में inline / StyleSheet से देते हो
Step 3 → Array से कई styles merge: style={[a, b]} (दाएँ वाला जीतता है)
Step 4 → Yoga (layout engine) Flexbox से position/size निकालता है
Step 5 → Native view पर properties apply होती हैं
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Style object लिखो: { padding: 16 }
Step 2 → style prop में दो
Step 3 → Array से merge: style={[a, b]} — आख़िरी वाला जीतता है
Step 4 → Yoga engine Flexbox से layout निकालता है
Step 5 → Native view पर apply होता है
```

---

## 🟡 Real World Example
**Swiggy** का restaurant card: rounded corners, shadow, orange "Order" button, और offer का badge — सब style objects से। "Selected" tab का रंग state के हिसाब से conditional style (`style={[styles.tab, active && styles.activeTab]}`) से बदलता है।

## 🟡 Real Example Hindi mein
**Swiggy** के restaurant card में rounded corners, shadow, orange button और offer badge सब style objects से बने हैं। Tab "selected" हो तो रंग बदलना conditional style (`active && styles.activeTab`) से होता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: inline style vs StyleSheet vs array merge
import React from 'react';                                // React
import { View, Text, StyleSheet } from 'react-native';    // RN

export default function BasicStyling() {
  return (
    <View style={styles.container}>                       {/* StyleSheet style */}
      {/* Inline style (chhote kaam ke liye) */}
      <Text style={{ fontSize: 22, color: '#333' }}>Hello Inline</Text>
      {/* Array: pehle base, phir override */}
      <Text style={[styles.base, styles.highlight]}>Merged styles</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: '#fff' }, // screen
  base: { fontSize: 18, color: '#666' },                  // base text
  highlight: { color: '#E23744', fontWeight: 'bold' },    // override colour
});
```

## 💻 Code Example — Advanced

```jsx
// Advanced: theme (light/dark) + conditional styles + platform shadow
import React, { useState } from 'react';                  // hooks
import { View, Text, Pressable, Platform, StyleSheet, useColorScheme } from 'react-native'; // RN

// Theme tokens: ek jagah se colours control
const themes = {
  light: { bg: '#ffffff', text: '#111111', card: '#f7f7f7', primary: '#fc8019' },
  dark:  { bg: '#121212', text: '#f1f1f1', card: '#1e1e1e', primary: '#ff9a45' },
};

export default function Card() {
  const scheme = useColorScheme() ?? 'light';             // system theme: 'light' | 'dark'
  const t = themes[scheme];                               // chosen theme
  const [selected, setSelected] = useState(false);        // toggle state

  return (
    <View style={[styles.screen, { backgroundColor: t.bg }]}>
      {/* Card: shadow Platform.select se */}
      <View style={[styles.card, { backgroundColor: t.card }, shadow]}>
        <Text style={[styles.title, { color: t.text }]}>Pizza Hut</Text>
        {/* Conditional style: selected hone par primary border */}
        <Pressable
          onPress={() => setSelected(s => !s)}            // toggle
          style={({ pressed }) => [                       // pressed state style
            styles.btn,
            selected && { borderColor: t.primary, borderWidth: 2 }, // false => ignored
            pressed && { opacity: 0.7 },                  // press feedback
          ]}
        >
          <Text style={{ color: t.primary }}>{selected ? 'Selected' : 'Select'}</Text>
        </Pressable>
      </View>
    </View>
  );
}

// Platform specific shadow
const shadow = Platform.select({
  ios: { shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.15, shadowRadius: 6 },
  android: { elevation: 4 },
});

const styles = StyleSheet.create({
  screen: { flex: 1, justifyContent: 'center', padding: 20 }, // centre card
  card: { borderRadius: 14, padding: 16 },                    // card
  title: { fontSize: 20, fontWeight: '700', marginBottom: 12 }, // title
  btn: { padding: 12, borderRadius: 8, borderWidth: 1, borderColor: '#ccc', alignItems: 'center' }, // button
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Shadow | `elevation` | `shadow*` props |
| Default font | Roboto | San Francisco |
| `overflow` + shadow | elevation clip नहीं होता | overflow:hidden से shadow कटती है |
| Ripple on press | `android_ripple` | `opacity` / highlight |
| Text includeFontPadding | Android-only prop | N/A |

---

## 🟠 Expo vs CLI Difference
**Expo way:** (extra options: `expo-linear-gradient`, `expo-font`)
```jsx
// npx expo install expo-linear-gradient
import { LinearGradient } from 'expo-linear-gradient'; // gradient Expo se
```
**CLI way:**
```jsx
// npm i react-native-linear-gradient && cd ios && pod install
import LinearGradient from 'react-native-linear-gradient'; // third-party
```
Core styling (`StyleSheet`, `style`) दोनों में same है।

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** CSS जैसे `background-color`, `px`, `%` strings (कुछ जगह)
```jsx
// WRONG: { 'background-color': 'red', fontSize: '16px' }
// CORRECT: { backgroundColor: 'red', fontSize: 16 }
```
✅ **Correct:** camelCase और unitless numbers।

❌ **Mistake 2:** यह मान लेना कि style inherit होती है
```jsx
// WRONG: <View style={{color:'red'}}><Text>Hi</Text></View>  // Text red nahi hoga
```
✅ **Correct:** `Text` पर ही `color`/`fontSize` दो (Text के अंदर nested Text inherit करता है)।

❌ **Mistake 3:** हर render पर नया inline object बनाना (heavy lists में)
✅ **Correct:** `StyleSheet.create` या `useMemo`।

---

## 🧠 Tricky Interview Question
**Q: `style={[{color:'red'}, {color:'blue'}]}` में कौन सा रंग?**

**Answer:** **blue**। Array में बाद वाला object पहले को override करता है (right-most wins)। `false`, `null`, `undefined` entries ignore होती हैं, इसीलिए `cond && styles.x` pattern चलता है।

---

## ⚫ Interview Questions + Answers

**Q1: RN में styling CSS से कैसे अलग है?**
A1: JS objects, camelCase, no cascade/inheritance (सिर्फ Text-in-Text), Flexbox default, units नहीं (dp जैसी numbers)।

**Q2: कौन सी units use होती हैं?**
A2: Unitless density-independent numbers (dp/pt)। Percentage string (`'50%'`) भी चलता है।

**Q3: Inline style बनाम StyleSheet?**
A3: दोनों चलते हैं; StyleSheet organization और validation (dev में) देता है; आज perf difference बहुत कम है।

**Q4: Dark mode कैसे?**
A4: `useColorScheme()` + theme object (या context)।

**Q5: Styled-components/NativeWind?**
A5: Third-party options हैं; NativeWind Tailwind classes देता है (अलग install + config)।

---

## 🔷 When to Use + When Not to Use
✅ **Use (StyleSheet) when:**
- Static, reusable styles
- Team में consistent structure चाहिए

❌ **Avoid inline when:**
- Long lists में हर item के लिए नया object
- बड़ी style repetition

---

## 📊 Visual Diagram
```
 style object ─► style prop ─► Yoga layout ─► Native view
 {padding:16}     [a, b]       Flexbox        UIView / View
                  merge → right wins
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| style prop | Object that styles a component | Component की style |
| camelCase | `backgroundColor` naming | CSS की जगह camelCase |
| Yoga | RN layout engine | Layout engine |
| dp | Density-independent pixel | Density-independent unit |
| useColorScheme | Hook for light/dark | Light/dark पता करने का hook |

---

## ⚡ 3-Line Summary
**English:**
1. Styling uses JS objects in `style`, no CSS.
2. Arrays merge styles; the last one wins.
3. Flexbox with column default; shadows differ per platform.

**Hindi:**
1. Styling JS objects से होती है, CSS नहीं।
2. Array से styles merge होती हैं; आख़िरी जीतती है।
3. Flexbox (column default); shadow platform के हिसाब से अलग।

---

## ➡️ Next Topic
**46. StyleSheet API** — `StyleSheet.create`, `compose`, `flatten`, `hairlineWidth`।
