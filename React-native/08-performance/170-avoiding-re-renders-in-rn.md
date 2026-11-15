# 170. Avoiding Re-renders in RN
# हिंदी में: RN में बेकार Re-renders से बचना
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 54 (React Native 0.81, React 19) target** — check current docs — APIs change between SDKs. React Compiler support (`experiments.reactCompiler`) is version-dependent; verify in Expo docs for your SDK.

---

## 🔵 Simple Definition (English)
A **re-render** happens when React calls your component function again. Many are wasted: same output, extra work. Avoiding them uses `React.memo`, `useCallback`, `useMemo`, **state colocation**, split Context and stable `keys` so only components whose data truly changed re-render.

## 🔵 सरल परिभाषा (Hindi)
**Re-render** तब होता है जब React आपका component function दोबारा चलाता है। कई बार output वही रहता है — बेकार मेहनत। `React.memo`, `useCallback`, `useMemo`, **state को नीचे रखना (colocation)**, Context को बाँटना और सही `key` से सिर्फ वही components दोबारा render होते हैं जिनका data सच में बदला।

---

## 🔴 Problem it Solves
```
BEFORE:
❌ Parent state changes -> ALL children re-render (even unchanged)
❌ Typing in a TextInput re-renders the whole screen (50 cards)
❌ New function/object props created every render -> memo is useless
❌ One big Context value -> every consumer re-renders on any change
Result: JS thread busy, dropped frames, battery drain
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
❌ Parent का state बदला -> सारे children re-render (भले न बदले हों)
❌ TextInput में type करने पर पूरी screen (50 cards) re-render
❌ हर बार नया function/object बनता है -> memo बेकार
❌ बड़ा Context -> किसी भी बदलाव पर सारे consumers re-render
नतीजा: JS thread busy, frames drop, battery खर्च
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → State/props/context changes in a component
Step 2 → React re-runs that component (and children by default)
Step 3 → React.memo: skip child if props are shallow-equal
Step 4 → Props must be STABLE: useCallback for functions, useMemo for objects
Step 5 → Colocate state: keep fast-changing state (input text) in a small child
Step 6 → Split Context (state vs dispatch) or use selectors (zustand)
Step 7 → Verify with React DevTools Profiler ("Highlight updates")
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → किसी component में state/props/context बदलता है
Step 2 → React वह component (और default में उसके children) दोबारा चलाता है
Step 3 → React.memo: props shallow-equal हों तो child skip
Step 4 → Props stable होने चाहिए: function के लिए useCallback, object के लिए useMemo
Step 5 → State नीचे रखो: तेज़ बदलने वाला state (input text) छोटे child में
Step 6 → Context बाँटो (state और dispatch अलग) या selector वाली library
Step 7 → React DevTools Profiler से check करो
```

---

## 🟡 Real World Example
**Zomato cart screen**: each cart row has +/- buttons. Without optimization, tapping `+` on one dish re-renders all 20 rows. With `React.memo(CartRow)` and a stable `onChange` (`useCallback`), only the changed row re-renders. **Swiggy search bar**: the TextInput state lives inside `SearchBox` so typing never re-renders the restaurant list.

## 🟡 Real Example Hindi mein
**Zomato cart screen**: हर row में +/- button है। Optimization के बिना एक dish का `+` दबाने पर सारी 20 rows re-render होती हैं। `React.memo(CartRow)` और stable `onChange` (`useCallback`) से सिर्फ बदली हुई row re-render होती है। **Swiggy search bar**: TextInput का state `SearchBox` के अंदर है, इसलिए type करने पर restaurant list re-render नहीं होती।

---

## 💻 Code Example — Basic
```jsx
// Basic: React.memo + useCallback so only the changed row re-renders
// Works on both Android + iOS
import React, { memo, useCallback, useState } from 'react'; // React APIs
import { View, Text, Pressable, StyleSheet } from 'react-native'; // RN UI

// memo: skip re-render when props are shallow-equal
const CartRow = memo(function CartRow({ item, onInc }) {
  console.log('render row', item.id);            // watch how often it prints
  return (
    <View style={styles.row}>
      <Text style={styles.name}>{item.name} x {item.qty}</Text>
      {/* call parent handler with this row's id */}
      <Pressable onPress={() => onInc(item.id)} style={styles.btn}>
        <Text style={styles.btnTxt}>+</Text>
      </Pressable>
    </View>
  );
});

export default function Cart() {
  // initial cart state
  const [items, setItems] = useState([
    { id: 1, name: 'Paneer Tikka', qty: 1 },
    { id: 2, name: 'Butter Naan', qty: 2 },
    { id: 3, name: 'Masala Chai', qty: 1 },
  ]);

  // useCallback keeps the SAME function reference between renders
  const onInc = useCallback((id) => {
    // functional update: no need to depend on `items`
    setItems((prev) =>
      prev.map((it) => (it.id === id ? { ...it, qty: it.qty + 1 } : it)) // new object only for changed row
    );
  }, []); // empty deps -> stable forever

  return (
    <View style={styles.container}>
      {items.map((it) => (
        // key = stable id (never array index for dynamic lists)
        <CartRow key={it.id} item={it} onInc={onInc} />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, paddingTop: 60, paddingHorizontal: 16 }, // screen padding
  row: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 10 }, // row layout
  name: { fontSize: 16 }, // dish text
  btn: { backgroundColor: '#f97316', paddingHorizontal: 14, borderRadius: 6 }, // orange button
  btnTxt: { color: '#fff', fontSize: 18 }, // button label
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: state colocation + split Context (state vs actions) + useMemo
// Prevents list re-render while typing, and prevents action-only consumers re-rendering
import React, { createContext, useContext, useMemo, useReducer, useState, memo } from 'react';
import { View, Text, TextInput, FlatList, Platform, StyleSheet } from 'react-native';

// Two contexts: data changes often, dispatch NEVER changes
const StateCtx = createContext(null);    // holds the list
const DispatchCtx = createContext(null); // holds the stable dispatch function

function reducer(state, action) {
  switch (action.type) {
    case 'add': return [...state, action.payload]; // new array for new item
    default: return state;                         // unknown action: unchanged
  }
}

export function CartProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, []); // dispatch identity is stable
  return (
    <DispatchCtx.Provider value={dispatch}>
      <StateCtx.Provider value={state}>{children}</StateCtx.Provider>
    </DispatchCtx.Provider>
  );
}

// Colocated state: typing re-renders ONLY SearchBox, not the whole screen
export const SearchBox = memo(function SearchBox({ onSubmit }) {
  const [text, setText] = useState(''); // fast-changing state stays local
  return (
    <TextInput
      value={text}
      onChangeText={setText}                       // updates only this component
      onSubmitEditing={() => { onSubmit(text); setText(''); }} // push result up once
      placeholder="Add dish"
      style={styles.input}
    />
  );
});

// This component only reads dispatch, so it does NOT re-render when items change
const AddBar = memo(function AddBar() {
  const dispatch = useContext(DispatchCtx);        // stable function
  return <SearchBox onSubmit={(t) => t && dispatch({ type: 'add', payload: { id: Date.now(), name: t } })} />;
});

function List() {
  const items = useContext(StateCtx);              // subscribes to data changes
  // useMemo avoids rebuilding derived data unless items change
  const total = useMemo(() => items.length, [items]);
  return (
    <View>
      <Text style={styles.total}>Total: {total}</Text>
      {/* FlatList + stable keyExtractor; renderItem defined outside = stable */}
      <FlatList data={items} keyExtractor={(i) => String(i.id)} renderItem={renderItem} />
    </View>
  );
}
const renderItem = ({ item }) => <Text style={styles.item}>{item.name}</Text>; // defined once

export default function Screen() {
  return (
    <CartProvider>
      <View style={styles.container}><AddBar /><List /></View>
    </CartProvider>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, paddingTop: Platform.OS === 'ios' ? 60 : 40, paddingHorizontal: 16 }, // status bar gap
  input: { borderWidth: 1, borderColor: '#ccc', padding: 10, borderRadius: 8, marginBottom: 12 }, // input box
  total: { fontWeight: '700', marginBottom: 8 }, // heading
  item: { paddingVertical: 6 }, // row
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Cost of extra re-render | Higher on low-end CPUs (cheap phones jank first) | Usually hidden by fast CPUs |
| TextInput re-render issue | Controlled input lag visible on slow devices | Rarely noticeable |
| Profiling tool | Android Studio + React DevTools | Instruments + React DevTools |
| `memo` logic | Same | Same (JS-level, platform independent) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// app.json — optional React Compiler (auto-memoization); SDK-dependent, check docs
// {
//   "expo": { "experiments": { "reactCompiler": true } }
// }
// Install the compiler plugin as per docs: npx expo install babel-plugin-react-compiler
```
CLI way:
```js
// babel.config.js — add the React Compiler Babel plugin manually (React 19 / RN 0.78+ recommended)
module.exports = {
  presets: ['module:@react-native/babel-preset'], // default RN preset
  plugins: ['babel-plugin-react-compiler'],       // auto-memoize components
};
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Inline object/function props to a memo component
```jsx
<Row style={{ margin: 4 }} onPress={() => go(id)} />  // new reference each render
```
✅ Correct: hoist styles to `StyleSheet.create`, use `useCallback`/pass `id` and let the child call the handler.

❌ Mistake 2: Using array **index** as key in dynamic lists
✅ Correct: use a stable unique id (`key={item.id}`).

❌ Mistake 3: Wrapping everything in `memo`/`useMemo`
✅ Correct: Memoize only measured hot spots; memo itself costs comparison time.

---

## 🧠 Tricky Interview Question
**Q: `Row` is wrapped in `React.memo` but still re-renders every time. Code: `<Row data={{id: 1}} />`. Why?**

**Answer:** `{id: 1}` is a **new object each render**, so shallow comparison (`Object.is`) says props changed. Fix: `useMemo(() => ({id: 1}), [])`, hoist a constant outside the component, or pass primitives (`id={1}`). Same for functions: use `useCallback`.

---

## ⚫ Interview Questions + Answers

**Q1: Does a child re-render when its parent re-renders?**
A1: Yes by default, even if props are equal. `React.memo` stops this when props are shallow-equal.

**Q2: useMemo vs useCallback?**
A2: `useMemo` caches a computed value; `useCallback(fn, deps)` caches the function itself (it is `useMemo(() => fn, deps)`).

**Q3: What is state colocation?**
A3: Keep state as close as possible to where it is used, so updates re-render a small subtree.

**Q4: Why split Context?**
A4: All consumers re-render when the Context `value` changes. Separate contexts (state vs dispatch) or selector libraries limit that.

**Q5: Does React Compiler remove the need for memo?**
A5: It auto-memoizes many cases at build time, but you should still understand why re-renders occur and profile; support depends on your SDK/RN version.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Profiler shows many unnecessary commits
- Long lists with interactive rows (cart, chat)
- Typing or animation state is causing parent re-renders

❌ Avoid when:
- Component is cheap and rarely renders
- Props change every time anyway (memo cannot help)
- You have not measured the problem

---

## 📊 Visual Diagram
```
BEFORE                         AFTER (memo + colocation)
Parent state change            Parent state change
   │                              │
   ├─► Row1 render ✗              ├─► Row1 (props same) SKIP
   ├─► Row2 render ✓ (changed)    ├─► Row2 render ✓ (changed)
   ├─► Row3 render ✗              ├─► Row3 (props same) SKIP
   └─► Row4 render ✗              └─► Row4 (props same) SKIP
 4 renders                      1 render
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Re-render | Component function runs again | Component दोबारा चलना |
| React.memo | Skip render if props same | Props वही हों तो skip |
| useCallback | Stable function reference | Stable function |
| useMemo | Cached computed value | Cache किया हुआ मान |
| Colocation | State near its usage | State को पास रखना |
| Shallow equal | Compare top-level values only | ऊपरी स्तर की तुलना |

---

## ⚡ 3-Line Summary
**English:**
1. Re-renders are normal; wasted ones hurt low-end Android first.
2. Use memo + stable props, colocate state, split Context.
3. Measure with the Profiler before and after.

**Hindi:**
1. Re-render सामान्य हैं; बेकार वाले सस्ते Android को सबसे पहले धीमा करते हैं।
2. memo + stable props, state नीचे रखो, Context बाँटो।
3. Profiler से पहले और बाद में measure करो।

---

## ➡️ Next Topic
**171. New Architecture (Fabric + TurboModules)** — JS और native के बीच communication को ही नया बनाना।
