# 82. useRef in React Native
# हिंदी में: React Native में useRef
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK version:** examples target **Expo SDK 52 (React Native 0.76, React 18.3)** — check current docs — APIs change between SDKs. (React 19 में `ref` सीधा prop की तरह pass हो सकता है, `forwardRef` कम चाहिए — अपने SDK का React version देखें।)

---

## 🔵 Simple Definition (English)
`useRef(initial)` returns a **mutable box** `{ current: initial }` that stays the same across renders. Changing `ref.current` does **not** re-render. In RN it is used for (1) **handles to native components** (`TextInput.focus()`, `FlatList.scrollToIndex`) and (2) **values that must persist without re-render** (timer ids, previous value, flags).

## 🔵 सरल परिभाषा (Hindi)
`useRef(initial)` एक **mutable डिब्बा** `{ current: initial }` देता है जो हर render में वही रहता है। `ref.current` बदलने से **re-render नहीं** होता। RN में दो काम: (1) **native components का handle** (`TextInput.focus()`, `FlatList.scrollToIndex`) और (2) **बिना re-render के values** रखना (timer id, पिछली value, flags)।

---

## 🔴 Problem it Solves
```
❌ TextInput ko code se focus/clear karna ho -> state se nahi hota (imperative action)
❌ Timer id / previous value state me rakho -> har change par faltu re-render
❌ Normal variable component ke andar -> har render me reset
✅ useRef: render ke beech survive, re-render trigger nahi
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ TextInput को code से focus/clear करना है -> state से नहीं होता (imperative काम)
❌ Timer id / पिछली value state में रखो -> हर बदलाव पर फ़ालतू re-render
❌ Component के अंदर normal variable -> हर render में reset
✅ useRef: renders के बीच बचा रहता है, re-render नहीं करता
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → const ref = useRef(null)  -> React creates {current: null} ONCE
Step 2 → Attach: <TextInput ref={ref} />
Step 3 → After mount, React sets ref.current = native component instance
Step 4 → Call methods: ref.current.focus(), .clear(), .blur()
Step 5 → For values: ref.current = Date.now()  (no re-render)
Step 6 → On unmount, ref.current becomes null for attached refs
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → const ref = useRef(null)  -> React एक बार {current: null} बनाता है
Step 2 → जोड़ो: <TextInput ref={ref} />
Step 3 → Mount के बाद React ref.current में native component रख देता है
Step 4 → Methods call करो: ref.current.focus(), .clear(), .blur()
Step 5 → Values के लिए: ref.current = Date.now()  (re-render नहीं)
Step 6 → Unmount पर attached refs का current null हो जाता है
```

---

## 🟡 Real World Example
**Paytm OTP screen**: 6 boxes; typing a digit moves focus to the next box using an array of refs, and backspace moves back. **Swiggy chat/support**: `FlatList` ref -> `scrollToEnd()` on a new message. **Zomato search**: ref stores the debounce timer id.

## 🟡 Real Example Hindi mein
**Paytm OTP screen**: 6 boxes; digit टाइप करने पर refs की array से अगले box पर focus जाता है, backspace पर पिछले पर। **Swiggy chat/support**: नया message आने पर `FlatList` ref से `scrollToEnd()`। **Zomato search**: ref में debounce timer id रखा जाता है।

---

## 💻 Code Example — Basic
```jsx
// Basic: focus next input, clear, and keep a render counter without re-rendering
import React, { useRef, useState } from 'react';                   // hooks
import { View, TextInput, Button, Text, StyleSheet } from 'react-native'; // UI

export default function BasicRef() {
  const emailRef = useRef(null);                                   // handle for email input
  const passRef = useRef(null);                                    // handle for password input
  const renders = useRef(0);                                       // plain value, no re-render
  const [email, setEmail] = useState('');                          // controlled state

  renders.current += 1;                                            // count renders (side-effect-free demo)

  return (
    <View style={styles.c}>
      <TextInput
        ref={emailRef}                                             // attach ref
        value={email}
        onChangeText={setEmail}
        placeholder="Email"
        autoCapitalize="none"
        returnKeyType="next"                                       // keyboard shows "Next"
        onSubmitEditing={() => passRef.current?.focus()}           // move focus on Next/Enter
        style={styles.i}
      />
      <TextInput ref={passRef} placeholder="Password" secureTextEntry style={styles.i} />
      <Button title="Focus email" onPress={() => emailRef.current?.focus()} />
      <Button title="Clear email" onPress={() => { setEmail(''); emailRef.current?.focus(); }} />
      <Text>Rendered {renders.current} times</Text>
    </View>
  );
}
const styles = StyleSheet.create({
  c: { padding: 20, gap: 10 },
  i: { borderWidth: 1, borderColor: '#ccc', padding: 8, borderRadius: 6 },
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: Paytm-style 6-box OTP with array of refs + FlatList scrollToEnd +
// "previous value" hook + interval id in ref
import React, { useRef, useState, useEffect } from 'react';        // hooks
import { View, TextInput, FlatList, Text, Button, Platform, StyleSheet } from 'react-native'; // UI

// Custom hook: remember previous value of something
function usePrevious(value) {
  const ref = useRef();                                            // box that survives renders
  useEffect(() => { ref.current = value; }, [value]);              // update AFTER render
  return ref.current;                                              // returns the OLD value
}

export function OtpInput({ length = 6, onComplete }) {
  const [digits, setDigits] = useState(Array(length).fill(''));    // ['', '', ...]
  const inputs = useRef([]);                                       // array of refs

  const onChange = (text, i) => {
    const d = text.replace(/\D/g, '').slice(-1);                   // keep last digit only
    const next = [...digits]; next[i] = d; setDigits(next);        // immutable update
    if (d && i < length - 1) inputs.current[i + 1]?.focus();       // move forward
    if (next.every(Boolean)) onComplete?.(next.join(''));          // all filled -> callback
  };

  const onKeyPress = (e, i) => {
    // Backspace on empty box -> go to previous box
    if (e.nativeEvent.key === 'Backspace' && !digits[i] && i > 0) {
      inputs.current[i - 1]?.focus();
    }
  };

  return (
    <View style={{ flexDirection: 'row', gap: 8 }}>
      {digits.map((d, i) => (
        <TextInput
          key={i}
          ref={(el) => { inputs.current[i] = el; }}                // callback ref into array
          value={d}
          onChangeText={(t) => onChange(t, i)}
          onKeyPress={(e) => onKeyPress(e, i)}
          keyboardType="number-pad"                                // numeric keyboard
          maxLength={1}                                            // one digit per box
          textContentType="oneTimeCode"                            // iOS SMS autofill
          autoComplete={Platform.OS === 'android' ? 'sms-otp' : 'one-time-code'} // autofill hints
          style={styles.box}
        />
      ))}
    </View>
  );
}

export default function Chat() {
  const [messages, setMessages] = useState([{ id: '1', text: 'Hi' }]); // chat list
  const listRef = useRef(null);                                    // FlatList handle
  const timerRef = useRef(null);                                   // interval id (not state)
  const prevCount = usePrevious(messages.length);                  // previous length

  useEffect(() => {
    timerRef.current = setInterval(() => console.log('poll'), 5000); // start polling
    return () => clearInterval(timerRef.current);                  // stop on unmount
  }, []);

  useEffect(() => {
    if (prevCount !== undefined && messages.length > prevCount) {
      listRef.current?.scrollToEnd({ animated: true });            // new message -> scroll down
    }
  }, [messages.length, prevCount]);

  return (
    <View style={{ flex: 1, padding: 16 }}>
      <OtpInput onComplete={(code) => console.log('OTP', code)} />
      <FlatList ref={listRef} data={messages} keyExtractor={(m) => m.id}
        renderItem={({ item }) => <Text>{item.text}</Text>} />
      <Button title="Send" onPress={() =>
        setMessages((m) => [...m, { id: String(m.length + 1), text: 'Msg ' + (m.length + 1) }])} />
    </View>
  );
}
const styles = StyleSheet.create({
  box: { width: 40, height: 48, borderWidth: 1, borderColor: '#999', borderRadius: 8, textAlign: 'center', fontSize: 20 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| `focus()` on TextInput | Opens keyboard (may need small delay after navigation) | Opens keyboard |
| `autoFocus` | Sometimes needs `setTimeout`/`useFocusEffect` after screen transition | More reliable |
| OTP autofill | `autoComplete="sms-otp"` | `textContentType="oneTimeCode"` |
| Backspace on empty input | `onKeyPress` may fire inconsistently (keyboard dependent) | Fires reliably |
| Ref to View `measure` | Works (async) | Works (async) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: refs also used for expo components (e.g. camera in expo-camera: CameraView)
import { CameraView } from 'expo-camera';
const cam = useRef(null);
// <CameraView ref={cam} />  ->  await cam.current?.takePictureAsync()
```
CLI way:
```jsx
// CLI: same useRef; native libraries expose imperative methods on refs, e.g. react-native-maps
const map = useRef(null);
// <MapView ref={map} />  ->  map.current?.animateToRegion(region)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Expecting UI to update when `ref.current` changes
```jsx
count.current += 1;      // ❌ screen doesn't change
```
✅ Correct: use `useState` for anything shown on screen.

❌ Mistake 2: Reading/writing `ref.current` during render for logic
✅ Correct: touch refs in event handlers and effects (render must stay pure).

❌ Mistake 3: Using ref before mount (`null`)
```jsx
inputRef.current.focus();   // ❌ crash if null
```
✅ Correct: `inputRef.current?.focus()`.

❌ Mistake 4: Using `ref` on custom function components without forwarding
✅ Correct: `forwardRef` (React 18) or accept `ref` as prop (React 19) / use `useImperativeHandle`.

---

## 🧠 Tricky Interview Question
**Q: What is the difference between `useRef` and `useState` for a counter? When does each re-render?**

**Answer:** `useState` setter schedules a re-render and new value is visible in the next render. `useRef` mutation is silent: `ref.current++` changes the box immediately (synchronously readable) but React doesn't know, so no re-render. Use state for what the UI displays; ref for instance-like data (timer id, previous value, "isMounted", scroll offset). A neat trick: `usePrevious` works because the effect updating the ref runs **after** render, so during render you still read the old value.

---

## ⚫ Interview Questions + Answers

**Q1: What is `useRef` used for in RN?**
A1: Imperative handles to native components and mutable values that persist without re-rendering.

**Q2: Callback ref vs object ref?**
A2: Object ref (`useRef`) is read via `.current`; callback ref `(el)=>{}` runs on attach/detach, handy for lists of refs.

**Q3: How to scroll a FlatList programmatically?**
A3: `listRef.current?.scrollToIndex({ index })`, `scrollToEnd`, `scrollToOffset` (provide `getItemLayout` or handle `onScrollToIndexFailed`).

**Q4: Why is `useRef` value stable across renders?**
A4: React stores the same object in the hook slot of the component's fiber.

**Q5: What is `useImperativeHandle`?**
A5: Customises what a parent gets from a child's ref (expose only `focus`, `reset` methods).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Focus/clear/scroll/measure native components
- Timers, previous values, mutable flags, animation values (`Animated.Value` often in a ref)

❌ Avoid when:
- Value should appear on screen (use state)
- You can solve it declaratively (e.g. `autoFocus`, controlled inputs)

---

## 📊 Visual Diagram
```
render 1:  ref = {current: null} ──attach──► {current: <TextInput native>}
render 2:  SAME object (identity stable)
render 3:  SAME object

ref.current = x  ──X──► no re-render
setState(x)      ───────► re-render
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Ref | Persistent mutable box | टिकाऊ mutable डिब्बा |
| `current` | The box's value | डिब्बे की value |
| Imperative | Tell it to do something now | सीधा आदेश देना |
| `forwardRef` | Pass ref through component | Ref को आगे भेजना |
| Callback ref | Function that gets the element | Element पाने वाला function |
| `useImperativeHandle` | Custom ref API | Custom ref API |

---

## ⚡ 3-Line Summary
**English:**
1. `useRef` is a persistent box that does not cause re-renders.
2. Use it for native component handles and values like timer ids/previous values.
3. Anything shown on screen belongs in state, not a ref.

**Hindi:**
1. `useRef` टिकाऊ डिब्बा है जो re-render नहीं करता।
2. Native component handles और timer id/पिछली value जैसी values के लिए use करो।
3. जो screen पर दिखे वह state में रखो, ref में नहीं।

---

## ➡️ Next Topic
**83. useContext in React Native** — बिना prop drilling के theme/user/cart share करना।
