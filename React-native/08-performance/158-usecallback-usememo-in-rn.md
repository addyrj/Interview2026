# 158. useCallback + useMemo in RN
# हिंदी में: RN में useCallback और useMemo
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: **Expo SDK 52 (check current docs — APIs change between SDKs)**, React 18.3 / RN 0.76. React 19 + React Compiler (opt-in, Expo SDK 52+ experimental) कई जगह memoization अपने-आप कर देता है — docs जाँचो।

---

## 🔵 Simple Definition (English)
`useCallback(fn, deps)` remembers a **function** between renders. `useMemo(() => value, deps)` remembers a **computed value**. They only create a new one when something in `deps` changes. Their main use in RN is keeping props stable so `React.memo` rows and `FlatList` don't re-render.

## 🔵 सरल परिभाषा (Hindi)
`useCallback(fn, deps)` एक **function** को renders के बीच याद रखता है। `useMemo(() => value, deps)` एक **calculated value** याद रखता है। `deps` में कुछ बदलने पर ही नया बनता है। RN में इनका मुख्य काम props को stable रखना है ताकि `React.memo` rows और `FlatList` दोबारा render न हों।

---

## 🔴 Problem it Solves
```
function Parent() {
  const onPress = () => {...};   // हर render पर NEW function (नया reference)
  return <Row onPress={onPress} />;
}
Row = React.memo(...)  →  onPress हर बार "बदला हुआ" दिखता है
→ memo बेकार, हर Row re-render!

const sorted = bigArray.sort(...)  // हर render पर दोबारा sort = JS thread busy
```

## 🔴 यह क्यों बना? (Hindi)
```
JavaScript में function/object हर render पर नया बनता है (reference अलग)।
React.memo reference compare करता है → हमेशा "बदला" दिखता है।
useCallback/useMemo reference को स्थिर रखते हैं
→ बेकार re-renders और बार-बार भारी calculation बंद।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → First render: React runs fn / factory, stores result + deps
Step 2 → Next render: React compares new deps with stored deps (Object.is)
Step 3 → Same deps  → returns the OLD function / value (no recompute)
Step 4 → Changed deps → runs again, stores the new result
Step 5 → memo child sees same reference → skips render
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले render में result और deps स्टोर होते हैं
Step 2 → अगले render में नए deps की पुराने से तुलना (Object.is)
Step 3 → deps वही → पुराना function/value लौटता है
Step 4 → deps बदले → दोबारा बनता है
Step 5 → memo child को वही reference दिखा → render skip
```

---

## 🟡 Real World Example
**Zomato cart screen**: items की list में हर row पर "+" button। Cart total बदलने पर `useMemo` से total सिर्फ items बदलने पर compute होता है, और `useCallback` वाला `onIncrement` memoized `CartRow` को stable मिलता है, इसलिए सिर्फ बदला हुआ row re-render होता है, बाकी 30 नहीं।

## 🟡 Real Example Hindi mein
Zomato जैसे cart screen में हर row पर "+" button होता है। `useMemo` से total सिर्फ items बदलने पर निकलता है; `useCallback` वाला `onIncrement` memoized `CartRow` को स्थिर रहता है — इसलिए सिर्फ बदला हुआ row re-render होता है।

---

## 💻 Code Example — Basic
```jsx
// Basic: useCallback + useMemo + memo साथ में
import React, { useState, useCallback, useMemo, memo } from 'react'; // सारे hooks
import { View, Text, Pressable, FlatList } from 'react-native';       // RN components

// memo: props वही रहे तो re-render नहीं
const CartRow = memo(function CartRow({ item, onInc }) {
  console.log('render row', item.id);                                // कितनी बार render हुआ देखो
  return (
    <Pressable onPress={() => onInc(item.id)}>                       {/* tap पर id भेजो */}
      <Text>{item.name} x {item.qty} — ₹{item.price * item.qty}</Text>{/* row text */}
    </Pressable>
  );
});

export default function Cart() {
  const [items, setItems] = useState([                               // cart items state
    { id: 'a', name: 'Paneer Tikka', price: 220, qty: 1 },
    { id: 'b', name: 'Naan', price: 40, qty: 2 },
  ]);
  const [coupon, setCoupon] = useState('');                          // unrelated state

  // useCallback: function reference स्थिर; functional update से deps खाली रह सकते हैं
  const onInc = useCallback((id) => {
    setItems(prev => prev.map(i => i.id === id ? { ...i, qty: i.qty + 1 } : i)); // सिर्फ वही item +1
  }, []);                                                            // कोई outer variable नहीं पढ़ा

  // useMemo: total सिर्फ items बदलने पर दोबारा
  const total = useMemo(
    () => items.reduce((s, i) => s + i.price * i.qty, 0),            // योग
    [items]                                                          // dependency
  );

  return (
    <View>
      <Text>Total: ₹{total}</Text>
      <FlatList data={items} keyExtractor={i => i.id}
        renderItem={({ item }) => <CartRow item={item} onInc={onInc} />} />
      <Text onPress={() => setCoupon(coupon + 'x')}>Coupon: {coupon}</Text>{/* rows re-render नहीं होंगे */}
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: stable renderItem, memoized context value, और stale closure से बचाव
import React, { createContext, useCallback, useMemo, useRef, useState, useContext } from 'react';
import { FlatList, Text, View } from 'react-native';

const ThemeCtx = createContext(null);                                // context बनाओ

export function ThemeProvider({ children }) {
  const [dark, setDark] = useState(false);                           // theme state
  const toggle = useCallback(() => setDark(d => !d), []);            // stable toggle
  // value object memoize नहीं किया तो हर render पर सारे consumers re-render होंगे
  const value = useMemo(() => ({ dark, toggle }), [dark, toggle]);   // stable context value
  return <ThemeCtx.Provider value={value}>{children}</ThemeCtx.Provider>;
}

export function useTheme() { return useContext(ThemeCtx); }          // helper hook

export function SearchList({ data, onSelect }) {
  const [q, setQ] = useState('');                                    // search text
  const latestSelect = useRef(onSelect);                             // ref में हमेशा ताज़ा callback
  latestSelect.current = onSelect;                                   // हर render पर update

  // filtered list महँगा हो सकता है → useMemo
  const filtered = useMemo(
    () => data.filter(x => x.name.toLowerCase().includes(q.toLowerCase())),
    [data, q]
  );

  // renderItem को stable रखो (FlatList extraData/ re-render कम)
  const renderItem = useCallback(({ item }) => (
    <Text onPress={() => latestSelect.current(item)}>{item.name}</Text> // ref से call: stale closure नहीं
  ), []);                                                            // deps खाली क्योंकि ref stable है

  const keyExtractor = useCallback((i) => i.id, []);                 // stable keyExtractor

  return (
    <View>
      <Text onPress={() => setQ('a')}>Search "a"</Text>
      <FlatList data={filtered} renderItem={renderItem} keyExtractor={keyExtractor} />
    </View>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Hook behaviour | Same (JS-level) | Same |
| Benefit visibility | Bigger on low-end phones (slow JS) | Smaller on fast chips |
| Where it matters | Large FlatLists, animations | Same |
| Memory cost of memo | Slightly more JS heap | Slightly more JS heap |

यह React का feature है, platform-specific नहीं; फ़र्क सिर्फ device की speed से दिखता है।

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// कोई setup नहीं। React Compiler (experimental) चालू करना हो तो app.json में
// "experiments": { "reactCompiler": true } — SDK 52+ docs जाँचो
import { useCallback, useMemo } from 'react';
```
CLI way:
```jsx
// कोई setup नहीं। Compiler के लिए babel-plugin-react-compiler manually जोड़ना होगा
import { useCallback, useMemo } from 'react';
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `useCallback` बिना `React.memo` child के।
✅ Correct: Child memo न हो तो useCallback का कोई फ़ायदा नहीं (सिर्फ overhead)।

❌ Mistake 2: Deps array ग़लत/खाली → stale closure (पुरानी state पढ़ना)।
✅ Correct: सारे used variables deps में दो, या functional update `setX(p => ...)` इस्तेमाल करो। ESLint `react-hooks/exhaustive-deps` चालू रखो।

❌ Mistake 3: `useMemo` के अंदर side effects (fetch/setState)।
✅ Correct: `useMemo` सिर्फ pure calculation के लिए; effects `useEffect` में।

❌ Mistake 4: Inline object `style={{...}}` या `data={[...]}` memoized child को देना।
✅ Correct: `StyleSheet.create` या `useMemo` से बनाओ।

---

## 🧠 Tricky Interview Question
```jsx
const [n, setN] = useState(0);
const log = useCallback(() => console.log(n), []);
<Pressable onPress={() => { setN(5); log(); }} />
```
`log()` क्या print करेगा, और बाद में tap पर?

Answer: `0` print होगा — हर बार। deps `[]` हैं, इसलिए `log` पहले render के `n=0` को capture किए हुए है (stale closure)। Fix: deps में `[n]` दो, या `useRef` में latest value रखो। (और `setN(5)` के तुरंत बाद भी `n` उसी render में पुराना ही रहता है।)

---

## ⚫ Interview Questions + Answers
Q1: useCallback और useMemo में अंतर?
A1: useCallback function लौटाता है; useMemo value। `useCallback(fn, d)` = `useMemo(() => fn, d)`।

Q2: कब नहीं लगाना चाहिए?
A2: सस्ते calculation और ऐसे components पर जो memo नहीं हैं; overhead (compare + memory) फ़ायदे से ज़्यादा हो सकता है।

Q3: Stale closure क्या है?
A3: Function पुराने render की variables याद रखे हुए है क्योंकि deps अपडेट नहीं हुए।

Q4: FlatList में renderItem को useCallback क्यों?
A4: Stable reference से FlatList/rows बेकार re-render नहीं होते; पर असली फ़ायदा memoized row के साथ मिलता है।

Q5: React Compiler के बाद ज़रूरत?
A5: Compiler auto-memoize करता है, इसलिए manual hooks कम चाहिए; पर यह opt-in है और हर पैटर्न पर काम नहीं करता — पुराने projects में अभी भी ज़रूरी।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Memoized child (React.memo/FlatList row) को function/object देना हो
- महँगा filter/sort/total calculation हो
- Context value का object बनाना हो

❌ Avoid when:
- Simple छोटे components और सस्ते calculations
- Deps हर render बदलते हों (memo बेकार)

---

## 📊 Visual Diagram
```
 Without:  render1 fn#1 ─► render2 fn#2 ─► memo child sees "new prop" ─► re-render
 With:     render1 fn#1 ─► render2 fn#1 (deps same) ─► memo child SKIPS
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Memoization | Cache result by inputs | इनपुट के आधार पर result याद रखना |
| Dependency array | Values that trigger recompute | वे values जो दोबारा गणना कराएँ |
| Stale closure | Function holding old values | पुरानी values पकड़े function |
| Referential equality | Same object reference | वही reference |
| React.memo | Skips render on same props | Props वही तो render skip |

---

## ⚡ 3-Line Summary
English: useCallback keeps a function stable; useMemo keeps a value stable. They help only with memoized children or expensive work. Wrong deps cause stale closures.
Hindi: useCallback function को स्थिर रखता है; useMemo value को। ये तभी काम के हैं जब memoized child या भारी काम हो। ग़लत deps से stale closure बनता है।

---

## ➡️ Next Topic
**159. FlatList Performance Optimization** — इन tools का सबसे बड़ा use case: बड़ी lists।
