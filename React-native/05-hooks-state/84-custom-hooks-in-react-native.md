# 84. Custom Hooks in React Native
# हिंदी में: React Native में Custom Hooks
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK version:** examples target **Expo SDK 52 (React Native 0.76, React 18.3)** — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
A **custom hook** is a normal JavaScript function whose name starts with **`use`** and which calls other hooks inside. It lets you **extract and reuse stateful logic** (fetching, debouncing, network status, form handling) across components — each call gets its **own separate state**.

## 🔵 सरल परिभाषा (Hindi)
**Custom hook** एक सामान्य JavaScript function है जिसका नाम **`use`** से शुरू होता है और जो अंदर दूसरे hooks call करता है। इससे आप **stateful logic को निकालकर बार-बार use** कर सकते हो (fetching, debounce, network status, form) — हर call को **अपना अलग state** मिलता है।

---

## 🔴 Problem it Solves
```
❌ Same fetch + loading + error code har screen me copy-paste
❌ Components bade aur ganda (UI + logic mixed)
❌ Logic ko test karna mushkil
✅ Custom hook: logic ek jagah, UI saaf, test aasan
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ वही fetch + loading + error code हर screen में copy-paste
❌ Components बड़े और गंदे (UI + logic मिला हुआ)
❌ Logic test करना मुश्किल
✅ Custom hook: logic एक जगह, UI साफ़, test आसान
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Identify repeated logic (state + effects)
Step 2 → Move it into function useSomething(args)
Step 3 → Inside, use useState/useEffect/useRef etc.
Step 4 → Return what UI needs: values and/or functions
Step 5 → Component calls: const {data, loading} = useSomething(url)
Step 6 → Each component using the hook gets ITS OWN state (not shared!)
         To share state, use Context/store.
Rule  → Name must start with "use" so lint can enforce the rules of hooks.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → दोहराया जाने वाला logic (state + effects) पहचानो
Step 2 → उसे function useSomething(args) में ले जाओ
Step 3 → अंदर useState/useEffect/useRef आदि use करो
Step 4 → UI को जो चाहिए वह return करो: values और/या functions
Step 5 → Component में: const {data, loading} = useSomething(url)
Step 6 → हर component को उसका अपना state मिलता है (shared नहीं!)
         Share करना हो तो Context/store use करो।
Rule  → नाम "use" से शुरू हो ताकि lint hooks के rules जाँच सके।
```

---

## 🟡 Real World Example
**Zomato**: `useDebounce(query)` for search, `useFetch(url)` for restaurant lists, `useNetwork()` to show an "offline" banner. **Swiggy**: `useCountdown()` for "order arriving in 12:00". **Paytm**: `useForm()` for UPI-ID validation, `useKeyboard()` for button above keyboard.

## 🟡 Real Example Hindi mein
**Zomato**: search के लिए `useDebounce(query)`, restaurant lists के लिए `useFetch(url)`, "offline" banner के लिए `useNetwork()`। **Swiggy**: "order 12:00 में पहुँचेगा" के लिए `useCountdown()`। **Paytm**: UPI-ID validation के लिए `useForm()`, keyboard के ऊपर button के लिए `useKeyboard()`।

---

## 💻 Code Example — Basic
```jsx
// Basic: useToggle + useDebounce + usage in a screen
import React, { useState, useEffect, useCallback } from 'react';    // hooks
import { View, Text, TextInput, Button } from 'react-native';       // UI

// Hook 1: boolean toggle
export function useToggle(initial = false) {
  const [on, setOn] = useState(initial);                            // state inside hook
  const toggle = useCallback(() => setOn((v) => !v), []);           // stable toggle function
  return [on, toggle];                                              // return like useState
}

// Hook 2: debounce a fast-changing value
export function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);                // delayed copy
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);        // update after delay
    return () => clearTimeout(id);                                  // cancel if value changes again
  }, [value, delay]);
  return debounced;
}

export default function Demo() {
  const [dark, toggleDark] = useToggle();                           // use hook 1
  const [text, setText] = useState('');                             // raw text
  const q = useDebounce(text, 400);                                 // debounced text

  useEffect(() => { if (q) console.log('search for', q); }, [q]);   // fires only after pause

  return (
    <View style={{ padding: 20, backgroundColor: dark ? '#222' : '#fff' }}>
      <Button title="Toggle theme" onPress={toggleDark} />
      <TextInput value={text} onChangeText={setText} placeholder="Search..." />
      <Text style={{ color: dark ? '#fff' : '#000' }}>Debounced: {q}</Text>
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// Advanced: useFetch (abort, error, refetch), useKeyboard (platform events),
// useCountdown (cleanup) — production-style custom hooks
import { useState, useEffect, useCallback, useRef } from 'react';   // hooks
import { Keyboard, Platform } from 'react-native';                  // RN APIs

// ---------- useFetch ----------
export function useFetch(url, options) {
  const [state, setState] = useState({ data: null, loading: true, error: null }); // all in one
  const [tick, setTick] = useState(0);                              // bump to refetch
  const optsRef = useRef(options);                                  // keep latest options w/o re-running
  optsRef.current = options;

  useEffect(() => {
    if (!url) return undefined;                                     // nothing to fetch
    const controller = new AbortController();                       // cancel support
    setState((s) => ({ ...s, loading: true, error: null }));        // start loading
    (async () => {
      try {
        const res = await fetch(url, { ...optsRef.current, signal: controller.signal });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);         // non-2xx -> error
        const data = await res.json();                              // parse
        setState({ data, loading: false, error: null });            // success
      } catch (e) {
        if (e.name === 'AbortError') return;                        // unmounted/changed url
        setState({ data: null, loading: false, error: e.message }); // failure
      }
    })();
    return () => controller.abort();                                // CLEANUP
  }, [url, tick]);

  const refetch = useCallback(() => setTick((t) => t + 1), []);     // manual refresh
  return { ...state, refetch };                                     // data, loading, error, refetch
}

// ---------- useKeyboard ----------
export function useKeyboard() {
  const [height, setHeight] = useState(0);                          // keyboard height
  useEffect(() => {
    const show = Platform.OS === 'ios' ? 'keyboardWillShow' : 'keyboardDidShow'; // iOS has Will*
    const hide = Platform.OS === 'ios' ? 'keyboardWillHide' : 'keyboardDidHide';
    const a = Keyboard.addListener(show, (e) => setHeight(e.endCoordinates.height));
    const b = Keyboard.addListener(hide, () => setHeight(0));
    return () => { a.remove(); b.remove(); };                       // CLEANUP
  }, []);
  return height;
}

// ---------- useCountdown ----------
export function useCountdown(totalSeconds) {
  const [left, setLeft] = useState(totalSeconds);                   // remaining seconds
  useEffect(() => {
    if (left <= 0) return undefined;                                // stop at zero
    const id = setTimeout(() => setLeft((s) => s - 1), 1000);       // tick every second
    return () => clearTimeout(id);                                  // CLEANUP
  }, [left]);
  const mm = String(Math.floor(left / 60)).padStart(2, '0');        // minutes
  const ss = String(left % 60).padStart(2, '0');                    // seconds
  return { left, label: `${mm}:${ss}`, done: left <= 0 };
}

// Usage in a screen:
// const { data, loading, error, refetch } = useFetch('https://api.example.com/restaurants');
// const kb = useKeyboard();        // lift "Pay" button above keyboard
// const { label } = useCountdown(720);   // "12:00"
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Custom hook logic | Same JS | Same JS |
| Keyboard event names | `keyboardDidShow/Hide` only | `keyboardWillShow/Hide` + `Did*` |
| Network libs (e.g. `useNetInfo`) | Needs `ACCESS_NETWORK_STATE` (autolinked) | No extra permission |
| Timers in background | May pause when backgrounded | Suspended when backgrounded |
| Hardware back hook (`useBackHandler`) | Meaningful | Not applicable |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Wrap an Expo module in your own hook
import { useCameraPermissions } from 'expo-camera';   // already a hook
export function useCameraAccess() {
  const [perm, request] = useCameraPermissions();
  return { granted: perm?.granted ?? false, request };
}
```
CLI way:
```jsx
// Wrap a community native module in a hook (needs install + pod install + rebuild)
import { useEffect, useState } from 'react';
import NetInfo from '@react-native-community/netinfo';
export function useIsOnline() {
  const [online, setOnline] = useState(true);
  useEffect(() => NetInfo.addEventListener((s) => setOnline(!!s.isConnected)), []); // returns unsubscribe
  return online;
}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Hook name without `use`
```jsx
function fetchData() { const [d] = useState(); }   // ❌ lint can't verify hooks rules
```
✅ Correct: `function useFetchData() {...}`.

❌ Mistake 2: Expecting two components to share the same hook state
✅ Correct: each call = separate state. Share through Context / Zustand / React Query cache.

❌ Mistake 3: Returning a new object/array every render and using it in deps
✅ Correct: `useMemo` / `useCallback` for returned objects/functions.

❌ Mistake 4: Forgetting cleanup and cancel in async hooks
✅ Correct: `AbortController`/flags + cleanup return.

---

## 🧠 Tricky Interview Question
**Q: Two components both call `useCounter()`. One increments. Does the other change?**

**Answer:** **No.** A custom hook is just a function; calling it twice runs `useState` twice, creating two independent states, one per component instance. Hooks share **logic**, not **state**. To share state, lift it up (props), use Context, or a store (Redux/Zustand). Follow-up: "Can a custom hook return JSX?" — technically yes, but it then behaves like a component; prefer returning data/functions.

---

## ⚫ Interview Questions + Answers

**Q1: What is a custom hook?**
A1: A function starting with `use` that composes built-in hooks to reuse stateful logic.

**Q2: Custom hook vs HOC vs render props?**
A2: Hooks reuse logic without wrapper components/nesting; simpler and composable.

**Q3: How do you test a custom hook?**
A3: `renderHook` from `@testing-library/react-native` (v12+ includes it) and `act` for updates.

**Q4: Why shouldn't you call hooks conditionally?**
A4: React tracks hooks by call order; changing order corrupts state mapping.

**Q5: Give examples of RN-specific custom hooks.**
A5: `useKeyboard`, `useAppState`, `useNetwork`, `useBackHandler`, `useOrientation`, `useDebounce`, `useFetch`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Same stateful logic in 2+ components
- Component is hard to read due to many effects
- Wrapping a native API with subscription + cleanup

❌ Avoid when:
- Logic is pure (just a util function, no hooks needed)
- Used once and trivial (premature abstraction)
- You need shared state (use Context/store)

---

## 📊 Visual Diagram
```
Screen A ── useFetch(urlA) ─► [state A] ┐
Screen B ── useFetch(urlB) ─► [state B] ├ same code, separate state
Screen C ── useFetch(urlC) ─► [state C] ┘

useFetch():
  useState + useEffect + AbortController
  returns { data, loading, error, refetch }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Custom hook | Own `useX` function | अपना `useX` function |
| Debounce | Wait until user stops | रुकने तक इंतज़ार |
| Reusability | Use in many places | कई जगह इस्तेमाल |
| `renderHook` | Test util for hooks | Hooks test करने का tool |
| Abort | Cancel request | Request cancel |
| Rules of hooks | Top-level, same order | Top-level, वही क्रम |

---

## ⚡ 3-Line Summary
**English:**
1. Custom hooks = `useX` functions that reuse stateful logic.
2. Each call has its own state; share state via Context/stores.
3. Always cleanup (abort, remove listeners) and keep API small.

**Hindi:**
1. Custom hooks = `useX` functions जो stateful logic reuse करते हैं।
2. हर call का अपना state; share करने के लिए Context/store।
3. हमेशा cleanup (abort, listeners हटाना) और API छोटा रखो।

---

## ➡️ Next Topic
**85. Zustand** (पहले से मौजूद) और **86. Redux Toolkit in React Native** — बड़े global state के लिए।
