# 79. All React Hooks Work in RN
# हिंदी में: सारे React Hooks React Native में चलते हैं
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK version:** examples target **Expo SDK 52 (React Native 0.76, React 18.3)** — check current docs — APIs change between SDKs. (नए RN/React versions में `use`, `useActionState`, `useOptimistic` जैसे React 19 hooks आते हैं — अपने SDK का React version देखें।)

---

## 🔵 Simple Definition (English)
React Native uses the **same React library** as the web, so **all core React hooks** — `useState`, `useEffect`, `useRef`, `useContext`, `useReducer`, `useMemo`, `useCallback`, `useLayoutEffect`, `useId`, `useTransition` — work identically. React Native adds **extra hooks** of its own (`useWindowDimensions`, `useColorScheme`) and libraries add more (`useNavigation`, `useFocusEffect`).

## 🔵 सरल परिभाषा (Hindi)
React Native वही **React library** use करता है जो web करता है, इसलिए **सारे core hooks** — `useState`, `useEffect`, `useRef`, `useContext`, `useReducer`, `useMemo`, `useCallback` आदि — बिल्कुल वैसे ही चलते हैं। React Native अपने **extra hooks** भी देता है (`useWindowDimensions`, `useColorScheme`) और libraries भी (`useNavigation`, `useFocusEffect`)।

---

## 🔴 Problem it Solves
```
❌ Class components: this, lifecycle methods, bahut boilerplate
❌ Logic reuse mushkil (HOC, render props)
❌ Web aur mobile ke liye alag mental model
✅ Hooks: function components + same API = web React ka gyaan mobile par bhi kaam aata hai
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ Class components: this, lifecycle methods, ज़्यादा boilerplate
❌ Logic reuse मुश्किल (HOC, render props)
❌ Web और mobile के लिए अलग सोच
✅ Hooks: function components + वही API = web React का ज्ञान mobile पर भी काम आता है
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → RN renders using the React reconciler (same hooks engine as web)
Step 2 → Hooks store state in the fiber of each component
Step 3 → Rules apply: call at top level, only in components/custom hooks
Step 4 → useEffect runs after native view commit (not browser paint)
Step 5 → RN-specific hooks read native info:
         useWindowDimensions -> screen size, useColorScheme -> light/dark
Step 6 → Differences from web: no DOM refs (refs point to native components),
         no window/document, app can go background (AppState)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → RN, React reconciler से render करता है (web जैसा ही hooks engine)
Step 2 → Hooks का state हर component की fiber में रहता है
Step 3 → Rules वही: top level पर call, सिर्फ़ components/custom hooks में
Step 4 → useEffect native view commit के बाद चलता है (browser paint नहीं)
Step 5 → RN-specific hooks native info पढ़ते हैं:
         useWindowDimensions -> screen size, useColorScheme -> light/dark
Step 6 → Web से फ़र्क: DOM refs नहीं, window/document नहीं, app background में जा सकता है
```

---

## 🟡 Real World Example
**Swiggy cart screen**: `useState` for quantity, `useReducer` for cart, `useMemo` for total price, `useCallback` for stable `renderItem`, `useEffect` to fetch delivery fee, `useRef` for the TextInput of coupon, `useContext` for the logged-in user. All standard React hooks.

## 🟡 Real Example Hindi mein
**Swiggy cart screen**: quantity के लिए `useState`, cart के लिए `useReducer`, total price के लिए `useMemo`, stable `renderItem` के लिए `useCallback`, delivery fee fetch के लिए `useEffect`, coupon TextInput के लिए `useRef`, logged-in user के लिए `useContext` — सब standard React hooks।

---

## 💻 Code Example — Basic
```jsx
// Basic: a tour of the common hooks in one component
import React, {
  useState, useEffect, useRef, useMemo, useCallback, useReducer, useContext, createContext,
} from 'react';                                                    // all from 'react'
import { View, Text, Button, TextInput, StyleSheet, useColorScheme } from 'react-native'; // RN + RN hook

const ThemeCtx = createContext('light');                           // context for useContext

function reducer(state, action) {                                  // reducer for useReducer
  if (action.type === 'inc') return { count: state.count + 1 };    // increase
  if (action.type === 'dec') return { count: state.count - 1 };    // decrease
  return state;                                                    // unknown action
}

export default function HooksTour() {
  const [name, setName] = useState('');                            // useState: local state
  const [state, dispatch] = useReducer(reducer, { count: 0 });     // useReducer: complex state
  const inputRef = useRef(null);                                   // useRef: handle to TextInput
  const theme = useContext(ThemeCtx);                              // useContext: read context
  const scheme = useColorScheme();                                 // RN hook: 'light' | 'dark' | null

  const doubled = useMemo(() => state.count * 2, [state.count]);  // useMemo: cached calc
  const hello = useCallback(() => console.log('Hi', name), [name]); // useCallback: stable fn

  useEffect(() => {                                                // useEffect: side effect
    console.log('count changed ->', state.count);                  // runs after render
  }, [state.count]);                                               // only when count changes

  return (
    <View style={styles.box}>
      <TextInput ref={inputRef} value={name} onChangeText={setName} placeholder="Name" style={styles.input} />
      <Text>Hello {name} | theme {theme} | OS scheme {String(scheme)}</Text>
      <Text>Count {state.count} (x2 = {doubled})</Text>
      <Button title="+" onPress={() => dispatch({ type: 'inc' })} />
      <Button title="-" onPress={() => dispatch({ type: 'dec' })} />
      <Button title="Focus input" onPress={() => inputRef.current?.focus()} />
      <Button title="Log" onPress={hello} />
    </View>
  );
}

const styles = StyleSheet.create({
  box: { padding: 20, gap: 8 },                                    // spacing
  input: { borderWidth: 1, borderColor: '#ccc', padding: 8 },      // simple input
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: RN-specific hooks (+ library hooks) used together:
// useWindowDimensions (responsive), AppState (background/foreground), BackHandler (Android),
// Keyboard events, and cleanup
import React, { useEffect, useState, useRef } from 'react';        // React
import {
  View, Text, StyleSheet, AppState, BackHandler, Keyboard, Platform, useWindowDimensions,
} from 'react-native';                                             // RN APIs
import { useFocusEffect } from '@react-navigation/native';         // library hook
import { useCallback } from 'react';                               // for useFocusEffect

export default function SmartScreen() {
  const { width, height } = useWindowDimensions();                 // re-renders on rotation
  const isTablet = width >= 768;                                   // simple breakpoint
  const [appState, setAppState] = useState(AppState.currentState); // 'active' | 'background' | ...
  const [kbHeight, setKbHeight] = useState(0);                     // keyboard height
  const lastActive = useRef(Date.now());                           // ref survives renders

  // 1. AppState: refresh data when app returns to foreground (e.g. Zomato order status)
  useEffect(() => {
    const sub = AppState.addEventListener('change', (next) => {    // listener
      if (appState.match(/inactive|background/) && next === 'active') {
        console.log('Back to foreground, away for', Date.now() - lastActive.current, 'ms');
      }
      if (next !== 'active') lastActive.current = Date.now();      // remember leave time
      setAppState(next);                                           // store new state
    });
    return () => sub.remove();                                     // CLEANUP
  }, [appState]);

  // 2. Keyboard height (iOS uses *Will*, Android only *Did* events)
  useEffect(() => {
    const showEvt = Platform.OS === 'ios' ? 'keyboardWillShow' : 'keyboardDidShow';
    const hideEvt = Platform.OS === 'ios' ? 'keyboardWillHide' : 'keyboardDidHide';
    const s = Keyboard.addListener(showEvt, (e) => setKbHeight(e.endCoordinates.height));
    const h = Keyboard.addListener(hideEvt, () => setKbHeight(0));
    return () => { s.remove(); h.remove(); };                      // CLEANUP both
  }, []);

  // 3. Android back handling only while this screen is focused
  useFocusEffect(
    useCallback(() => {
      const sub = BackHandler.addEventListener('hardwareBackPress', () => {
        console.log('Custom back');                                // do something
        return false;                                              // false = let default happen
      });
      return () => sub.remove();                                   // CLEANUP on blur
    }, [])
  );

  return (
    <View style={styles.c}>
      <Text>{width}x{height} {isTablet ? '(tablet)' : '(phone)'}</Text>
      <Text>AppState: {appState}</Text>
      <Text>Keyboard: {kbHeight}px</Text>
    </View>
  );
}
const styles = StyleSheet.create({ c: { flex: 1, padding: 20 } });
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Core hooks | Same | Same |
| `BackHandler` | Works (hardware back) | No-op / not applicable |
| Keyboard events | Only `keyboardDid*` reliably | `keyboardWill*` + `keyboardDid*` |
| `AppState` | `active`/`background` | also `inactive` (during transitions, calls) |
| `useEffect` timing in background | JS may be paused when app killed by OS | JS suspended soon after background |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo SDK adds hooks in its packages:
import { useCameraPermissions } from 'expo-camera';   // permission hook
import { useFonts } from 'expo-font';                 // font-loading hook
import { useKeepAwake } from 'expo-keep-awake';       // keeps screen on
```
CLI way:
```jsx
// CLI: core RN hooks same. Library hooks come from community packages:
import NetInfo, { useNetInfo } from '@react-native-community/netinfo'; // connectivity hook
// (needs npm install + pod install + rebuild)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Conditional hooks
```jsx
if (loggedIn) { const [x, setX] = useState(0); }   // ❌ breaks hooks order
```
✅ Correct: always call hooks at the top level; put the condition inside.

❌ Mistake 2: Missing dependencies in `useEffect`/`useCallback` (stale values)
✅ Correct: include all used values (enable `react-hooks/exhaustive-deps` ESLint rule).

❌ Mistake 3: Using web-only things (`window.addEventListener`, `document`) in effects
✅ Correct: use RN APIs: `AppState`, `Keyboard`, `Linking`, `Dimensions`.

❌ Mistake 4: Forgetting cleanup of listeners/timers
✅ Correct: return a cleanup function in `useEffect`.

---

## 🧠 Tricky Interview Question
**Q: Is `useEffect` in React Native the same as web? What happens when the user presses Home and the app goes to background?**

**Answer:** The hook API is identical, but the **environment** differs. Pressing Home does **not** unmount your components — the screen stays mounted, effects do **not** re-run, and cleanup does **not** run. You must listen to `AppState` to react to background/foreground. Also, screens in a Stack stay mounted when you navigate forward, so `useEffect(..., [])` does **not** re-run when you come back — use `useFocusEffect` (React Navigation) for "run every time the screen is focused".

---

## ⚫ Interview Questions + Answers

**Q1: Do all React hooks work in React Native?**
A1: Yes — it's the same React. Only DOM-specific libraries/APIs don't exist.

**Q2: Name RN-specific hooks.**
A2: `useWindowDimensions`, `useColorScheme` (core), `useNavigation`, `useRoute`, `useFocusEffect`, `useIsFocused` (React Navigation), `useNetInfo`, `useSafeAreaInsets`.

**Q3: What are the rules of hooks?**
A3: Call only at top level, only from function components or custom hooks, in the same order each render.

**Q4: `useEffect` vs `useLayoutEffect` in RN?**
A4: `useEffect` runs after the commit asynchronously; `useLayoutEffect` runs synchronously after layout, before the user sees the frame — for measuring (`measure`) or avoiding flicker.

**Q5: Why `useFocusEffect` over `useEffect` for screens?**
A5: Stack screens stay mounted; focus/blur events tell you when screen is visible.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Writing any new RN component (function components are the standard)
- Sharing logic via custom hooks

❌ Avoid when:
- Class-only APIs (e.g. error boundaries still need a class or library)
- Over-memoising everything (`useMemo`/`useCallback` have a cost)

---

## 📊 Visual Diagram
```
React core hooks ───────────────┐
 useState useEffect useRef ...  │  same engine on web + RN
                                ▼
RN built-in hooks     useWindowDimensions, useColorScheme
Navigation hooks      useNavigation, useRoute, useFocusEffect
Expo hooks            useFonts, useCameraPermissions ...
Community hooks       useNetInfo, useSafeAreaInsets ...
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hook | Function to use React features | React features वाला function |
| Custom hook | Your own reusable hook (`useXyz`) | अपना reusable hook |
| Cleanup | Function returned by effect | Effect से लौटाया cleanup function |
| Dependency array | Values that trigger effect | Effect trigger करने वाली values |
| Fiber | React's internal node | React का internal node |
| AppState | App foreground/background state | App का foreground/background state |

---

## ⚡ 3-Line Summary
**English:**
1. RN uses the same React, so all core hooks work unchanged.
2. RN adds environment hooks (`useWindowDimensions`, `useColorScheme`); libraries add more.
3. Mind mobile lifecycle: background does not unmount; use `AppState` and `useFocusEffect`.

**Hindi:**
1. RN वही React use करता है, इसलिए सारे core hooks बिना बदलाव चलते हैं।
2. RN environment hooks देता है (`useWindowDimensions`, `useColorScheme`); libraries और देती हैं।
3. Mobile lifecycle याद रखो: background में unmount नहीं होता; `AppState` और `useFocusEffect` use करो।

---

## ➡️ Next Topic
**80. useState in React Native** — local state, functional updates और RN-specific पैटर्न।
