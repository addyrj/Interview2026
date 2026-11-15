# 80. useState in React Native
# हिंदी में: React Native में useState
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK version:** examples target **Expo SDK 52 (React Native 0.76, React 18.3)** — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
`useState` gives a component **memory**. `const [value, setValue] = useState(initial)` returns the current value and a setter. Calling the setter **re-renders** the component with the new value. In RN it drives everything: inputs, toggles, counters, lists, loading flags.

## 🔵 सरल परिभाषा (Hindi)
`useState` component को **memory** देता है। `const [value, setValue] = useState(initial)` current value और एक setter देता है। Setter call करने पर component नई value के साथ **फिर से render** होता है। RN में inputs, toggles, counters, lists, loading flags — सब इसी से चलते हैं।

---

## 🔴 Problem it Solves
```
❌ Normal variable: let count = 0; count++ -> UI update nahi hota
❌ Native views ko manually update karna (setNativeProps) kharab practice
✅ State badlo -> React khud UI update karta hai (declarative)
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ Normal variable: let count = 0; count++ -> UI update नहीं होता
❌ Native views को manually update करना ख़राब practice
✅ State बदलो -> React खुद UI update करता है (declarative)
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → First render: useState(0) -> value = 0
Step 2 → User taps button -> setCount(1)
Step 3 → React schedules a re-render (batched with other updates)
Step 4 → Component function runs again; useState returns 1 now
Step 5 → React diffs the tree -> sends minimal native view updates
Step 6 → Screen shows new value on Android + iOS
Note   → State updates are ASYNC/batched: `count` does NOT change
         immediately inside the same handler.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले render में useState(0) -> value = 0
Step 2 → User button tap करता है -> setCount(1)
Step 3 → React re-render schedule करता है (दूसरे updates के साथ batch)
Step 4 → Component function फिर चलता है; अब useState 1 देता है
Step 5 → React tree diff करके native views में सिर्फ़ ज़रूरी बदलाव भेजता है
Step 6 → Android + iOS दोनों पर नई value दिखती है
Note   → State update async/batched है: उसी handler में `count` तुरंत नहीं बदलता।
```

---

## 🟡 Real World Example
**Zomato cart**: `quantity` per dish (counter), `isVegOnly` toggle (Switch), `coupon` text (TextInput), `isLoading` while placing the order, `selectedAddress`. **Paytm**: amount input + `isPinVisible` toggle + `status` ('idle'|'loading'|'success').

## 🟡 Real Example Hindi mein
**Zomato cart**: हर dish की `quantity` (counter), `isVegOnly` toggle (Switch), `coupon` text (TextInput), order करते समय `isLoading`, `selectedAddress`। **Paytm**: amount input + `isPinVisible` toggle + `status` ('idle'|'loading'|'success')।

---

## 💻 Code Example — Basic
```jsx
// Basic: counter + text input + switch with useState
import React, { useState } from 'react';                           // React + hook
import { View, Text, Button, TextInput, Switch, StyleSheet } from 'react-native'; // UI

export default function BasicState() {
  const [count, setCount] = useState(0);                           // number state
  const [name, setName] = useState('');                            // string state
  const [vegOnly, setVegOnly] = useState(false);                   // boolean state

  return (
    <View style={styles.box}>
      <Text>Count: {count}</Text>{/* show number */}
      <Button title="Add" onPress={() => setCount(count + 1)} />{/* set new value */}
      <Button title="Add 3" onPress={() => {
        setCount((c) => c + 1);                                    // functional update: uses latest
        setCount((c) => c + 1);                                    // runs after previous -> +2
        setCount((c) => c + 1);                                    // total +3 (works when batched)
      }} />

      <TextInput
        value={name}                                               // controlled input
        onChangeText={setName}                                     // RN passes the TEXT (not event)
        placeholder="Your name"
        style={styles.input}
      />
      <Text>Hello {name || 'guest'}</Text>

      <View style={styles.row}>
        <Text>Veg only</Text>
        <Switch value={vegOnly} onValueChange={setVegOnly} />{/* Switch gives boolean */}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  box: { padding: 20, gap: 10 },                                   // layout
  input: { borderWidth: 1, borderColor: '#ccc', padding: 8, borderRadius: 6 }, // input style
  row: { flexDirection: 'row', alignItems: 'center', gap: 10 },    // row
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: cart with object/array state (immutable updates), lazy initial state,
// and status state-machine instead of many booleans (production style)
import React, { useState, useMemo } from 'react';                  // hooks
import { View, Text, Button, FlatList, StyleSheet } from 'react-native'; // UI

const MENU = [                                                     // fake menu data
  { id: 'b1', name: 'Veg Biryani', price: 180 },
  { id: 'p1', name: 'Paneer Tikka', price: 220 },
];

// Lazy initial state: function runs ONLY on first render (good for expensive reads)
function initialCart() {
  return {};                                                       // { [id]: qty }
}

export default function CartScreen() {
  const [cart, setCart] = useState(initialCart);                   // pass function, not call
  const [status, setStatus] = useState('idle');                    // 'idle'|'loading'|'success'|'error'

  // Immutable update of an object: create a NEW object (never cart[id]++)
  const add = (id) =>
    setCart((prev) => ({ ...prev, [id]: (prev[id] ?? 0) + 1 }));

  // Immutable decrement; remove key when 0
  const remove = (id) =>
    setCart((prev) => {
      const qty = (prev[id] ?? 0) - 1;                             // new qty
      if (qty <= 0) {
        const { [id]: _removed, ...rest } = prev;                  // drop the key
        return rest;                                               // new object without id
      }
      return { ...prev, [id]: qty };                               // new object with qty
    });

  // Derived data: DON'T store total in state, compute it
  const total = useMemo(
    () => MENU.reduce((sum, m) => sum + m.price * (cart[m.id] ?? 0), 0),
    [cart]
  );

  const placeOrder = async () => {
    if (status === 'loading') return;                              // block double tap
    setStatus('loading');                                          // show spinner/disable
    try {
      await new Promise((r) => setTimeout(r, 800));                // fake API call
      setStatus('success');                                        // done
      setCart({});                                                 // clear cart
    } catch (e) {
      setStatus('error');                                          // show error UI
    }
  };

  return (
    <View style={styles.c}>
      <FlatList
        data={MENU}
        keyExtractor={(i) => i.id}
        extraData={cart}                                           // re-render rows when cart changes
        renderItem={({ item }) => (
          <View style={styles.row}>
            <Text style={{ flex: 1 }}>{item.name} Rs.{item.price}</Text>
            <Button title="-" onPress={() => remove(item.id)} />
            <Text style={styles.qty}>{cart[item.id] ?? 0}</Text>
            <Button title="+" onPress={() => add(item.id)} />
          </View>
        )}
      />
      <Text style={styles.total}>Total: Rs.{total}</Text>
      <Button title={status === 'loading' ? 'Placing...' : 'Place order'}
              disabled={total === 0 || status === 'loading'} onPress={placeOrder} />
      {status === 'success' && <Text>Order placed!</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  c: { flex: 1, padding: 16 },
  row: { flexDirection: 'row', alignItems: 'center', paddingVertical: 6 },
  qty: { width: 28, textAlign: 'center' },
  total: { fontWeight: '700', marginVertical: 12 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| `useState` behaviour | Same | Same |
| TextInput controlled value | Rarely flickers on fast typing with transforms | Same; avoid transforming text in `onChangeText` heavily |
| `Switch` look | Material toggle (`thumbColor`/`trackColor`) | iOS pill switch |
| State after process death | Lost if OS kills app (Android is aggressive) | Lost too, if app terminated |
| Persistence | Use AsyncStorage/MMKV | Same |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Same useState. Persist state across restarts using expo packages if needed:
import AsyncStorage from '@react-native-async-storage/async-storage'; // npx expo install
```
CLI way:
```jsx
// Same useState. Install + link storage yourself:
// npm i @react-native-async-storage/async-storage && cd ios && pod install
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Mutating state directly
```jsx
cart.push(item); setCart(cart);     // ❌ same reference -> no re-render
```
✅ Correct: `setCart([...cart, item]);`

❌ Mistake 2: Reading state right after setting it
```jsx
setCount(5); console.log(count);    // ❌ still old value
```
✅ Correct: use `useEffect` on `count`, or compute `const next = 5; setCount(next); use(next)`.

❌ Mistake 3: Using the old value for multiple updates
```jsx
setCount(count + 1); setCount(count + 1);   // ❌ only +1
```
✅ Correct: `setCount(c => c + 1)` twice.

❌ Mistake 4: Storing derived data (total, filtered list) in state
✅ Correct: compute during render / `useMemo`.

---

## 🧠 Tricky Interview Question
**Q: What does this print and show?**
```jsx
const [count, setCount] = useState(0);
const onPress = () => {
  setCount(count + 1);
  setCount(count + 1);
  console.log(count);
};
```
**Answer:** It logs `0`, and the screen shows `1` (not 2). `count` is a **snapshot** for that render (`0`); both calls say "set to 0 + 1", and the console reads the old snapshot. Fix with functional updates: `setCount(c => c + 1)` twice -> `2`. In React 18, updates in handlers, timeouts and promises are all batched automatically.

---

## ⚫ Interview Questions + Answers

**Q1: Is `setState` synchronous?**
A1: No. It schedules a re-render; the new value appears in the next render.

**Q2: Why must state be immutable?**
A2: React compares by reference (`Object.is`). Mutating keeps the same reference, so React may skip the re-render.

**Q3: What is lazy initial state?**
A3: `useState(() => expensive())` — the function runs only once, on mount.

**Q4: `onChangeText` vs `onChange` in TextInput?**
A4: `onChangeText` gives the string; `onChange` gives an event object (`e.nativeEvent.text`).

**Q5: When to use `useReducer` instead?**
A5: When state has many related fields or transitions (cart, forms, state machines).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Local UI state (input, toggle, modal visibility, loading)
- Simple values used by one component/subtree

❌ Avoid when:
- State needed across many distant screens (use Context/Redux/Zustand)
- Server data (use React Query / SWR)
- Values that change very often but need no re-render (use `useRef`)

---

## 📊 Visual Diagram
```
render #1: count=0 ──► UI "0"
   tap -> setCount(c=>c+1)
        │
        ▼ schedule re-render (batched)
render #2: count=1 ──► diff ──► native update ──► UI "1"
Each render has its OWN snapshot of count.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| State | Data that changes UI | UI बदलने वाला data |
| Setter | Function to update state | State update का function |
| Batching | Combine updates in one render | कई updates एक render में |
| Immutable | Create new object, don't edit | नया object बनाओ, edit नहीं |
| Lazy init | Initial value via function | Function से initial value |
| Controlled input | Value comes from state | Value state से आती है |

---

## ⚡ 3-Line Summary
**English:**
1. `useState` stores values and re-renders when the setter is called.
2. Updates are batched/async; use functional updates and never mutate.
3. Don't store derived data; use other tools for global/server state.

**Hindi:**
1. `useState` value रखता है और setter call होने पर re-render करता है।
2. Updates batched/async हैं; functional update use करो और mutate कभी मत करो।
3. Derived data state में मत रखो; global/server state के लिए अलग tools।

---

## ➡️ Next Topic
**81. useEffect in React Native** — side effects: API calls, listeners, cleanup।
