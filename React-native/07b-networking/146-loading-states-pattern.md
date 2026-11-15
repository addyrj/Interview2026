# 146. Loading States Pattern
# हिंदी में: Loading States Pattern — Loading / Error / Empty / Success UI
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 52 target (check current docs — APIs change between SDKs).** React Native 0.76। सिर्फ core components (`ActivityIndicator`, `FlatList`, `RefreshControl`) और hooks।

---

## 🔵 Simple Definition (English)
The **loading states pattern** models a data screen as one of a few clear states: `idle`, `loading`, `success`, `empty`, `error`. The UI renders exactly one state at a time, so users always know what is happening.

## 🔵 सरल परिभाषा (Hindi)
**Loading states pattern** में data वाली screen को कुछ साफ़ states में बाँटा जाता है: `idle`, `loading`, `success`, `empty`, `error`। UI एक समय में सिर्फ एक state दिखाती है, जिससे user को हमेशा पता रहता है कि क्या हो रहा है।

---

## 🔴 Problem it Solves
```
अलग-अलग booleans (isLoading, hasError, hasData) से impossible combos बनते हैं:
  isLoading=true  और error="x"  एक साथ?!
  data=[] पर "खाली" दिखाएँ या "लोड हो रहा"?

परिणाम: flicker, खाली screen, अटका spinner।
```

## 🔴 यह क्यों बना? (Hindi)
```
कई booleans = गलत combinations।
एक `status` field = एक समय में एक ही स्थिति।
UI predictable, test करना आसान।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → status = 'idle' | 'loading' | 'success' | 'error'
Step 2 → Fetch शुरू: status='loading'
Step 3 → सफल: data सेट, status='success' (data खाली हो तो UI 'empty' दिखाए)
Step 4 → fail: error सेट, status='error'
Step 5 → Retry/pull-to-refresh: loading दोबारा (पुराना data दिखाते हुए refreshing)
Step 6 → UI: switch(status) → एक ही branch render
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. एक status variable रखो।
2. Fetch पर loading, सफल पर success, fail पर error।
3. List खाली हो तो empty UI।
4. Refresh में पुराना data दिखाते रहो, ऊपर छोटा spinner।
5. UI में switch से सिर्फ़ एक state render।
```

---

## 🟡 Real World Example
**Zomato:** पहली बार खुलने पर **skeleton cards** (loading); internet नहीं → illustration + Retry (error); search में कुछ नहीं मिला → "No restaurants found" (empty); नीचे खींचने पर pull-to-refresh। **Instagram:** feed पर skeleton, और नीचे scroll पर footer spinner (pagination loading)।

## 🟡 Real Example Hindi mein
**Zomato** में पहली बार data आने तक grey skeleton cards दिखते हैं (spinner से बेहतर, क्योंकि layout जैसा दिखता है)। Search खाली हो तो "कोई restaurant नहीं मिला" और error पर Retry।

---

## 💻 Code Example — Basic

```jsx
// LoadingStates.jsx — idle/loading/success/empty/error with one status
import React, { useCallback, useEffect, useState } from 'react';  // hooks
import { View, Text, Button, FlatList, ActivityIndicator, RefreshControl } from 'react-native'; // UI

export default function LoadingStates() {
  const [status, setStatus] = useState('idle');                   // current state
  const [items, setItems] = useState([]);                         // data
  const [refreshing, setRefreshing] = useState(false);            // pull-to-refresh flag

  const load = useCallback(async (isRefresh = false) => {        // loader
    if (isRefresh) setRefreshing(true); else setStatus('loading'); // refresh में पुराना data रखो
    try {
      const res = await fetch('https://jsonplaceholder.typicode.com/todos?_limit=8'); // GET
      if (!res.ok) throw new Error('HTTP ' + res.status);         // HTTP error
      setItems(await res.json());                                 // data
      setStatus('success');                                       // ok
    } catch {
      setStatus('error');                                         // fail
    } finally {
      setRefreshing(false);                                       // refresh खत्म
    }
  }, []);

  useEffect(() => { load(); }, [load]);                           // mount पर

  if (status === 'idle' || status === 'loading')
    return <ActivityIndicator size="large" style={{ marginTop: 60 }} />; // loading UI
  if (status === 'error')
    return (<View style={{ padding: 24 }}><Text>लोड नहीं हो पाया</Text><Button title="Retry" onPress={() => load()} /></View>); // error UI
  return (
    <FlatList
      data={items}                                                // list
      keyExtractor={(i) => String(i.id)}                          // key
      ListEmptyComponent={<Text style={{ padding: 24 }}>कुछ नहीं मिला</Text>} // empty UI
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => load(true)} />} // pull to refresh
      renderItem={({ item }) => <Text style={{ padding: 12 }}>{item.title}</Text>} // row
    />
  );
}
```

## 💻 Code Example — Advanced

```jsx
// useAsync.js — reusable hook with stale-response guard + typed state
import { useCallback, useEffect, useReducer, useRef } from 'react'; // hooks

const initial = { status: 'idle', data: null, error: null };      // starting state

function reducer(state, action) {                                 // pure reducer
  switch (action.type) {
    case 'START':   return { ...state, status: 'loading', error: null };          // पुराना data रखो
    case 'SUCCESS': return { status: 'success', data: action.data, error: null }; // ok
    case 'ERROR':   return { ...state, status: 'error', error: action.error };    // fail
    default:        return state;                                 // unknown
  }
}

export function useAsync(fn, deps = []) {
  const [state, dispatch] = useReducer(reducer, initial);         // state machine
  const callId = useRef(0);                                       // latest request id

  const run = useCallback(async () => {
    const id = ++callId.current;                                  // इस call का id
    dispatch({ type: 'START' });                                  // loading
    try {
      const data = await fn();                                    // actual work
      if (id === callId.current) dispatch({ type: 'SUCCESS', data }); // सिर्फ latest call मान्य
    } catch (error) {
      if (id === callId.current) dispatch({ type: 'ERROR', error }); // stale error ignore
    }
  }, deps);                                                       // eslint-disable-line

  useEffect(() => { run(); return () => { callId.current++; }; }, [run]); // unmount पर invalidate
  return { ...state, reload: run, isEmpty: state.status === 'success' && Array.isArray(state.data) && state.data.length === 0 };
}
// Usage: const { status, data, error, reload, isEmpty } = useAsync(() => api.get('/orders'));
// Stale guard से तेज़ search typing में पुराना response नया overwrite नहीं करता।
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| `ActivityIndicator` look | Material circular | UIKit spinner |
| `size` prop | small / large या number | small / large only |
| `RefreshControl` colors | `colors`, `progressBackgroundColor` | `tintColor`, `title` |
| Pull-to-refresh feel | Material circle | Bounce spinner |
| Logic | Same | Same |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// सब core components Expo Go में चलते हैं।
// Skeleton: npx expo install expo-linear-gradient (shimmer के लिए) या RN Reanimated
```
CLI way:
```jsx
// Core same। Skeleton shimmer: npm i react-native-linear-gradient; cd ios && pod install
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `isLoading`, `isError`, `data` तीन अलग booleans/values।
✅ Correct: एक `status` या reducer।

❌ Mistake 2: Refresh पर पूरी list हटाकर spinner।
✅ Correct: पुराना data + `RefreshControl`।

❌ Mistake 3: Empty और Loading को एक जैसा दिखाना।
✅ Correct: `ListEmptyComponent` सिर्फ़ success+खाली पर।

❌ Mistake 4: तेज़ typing में race condition।
✅ Correct: Request id guard या AbortController।

---

## 🧠 Tricky Interview Question
User search box में "pi", "piz", "pizza" जल्दी टाइप करता है। "pizza" का response पहले आ गया, "pi" का बाद में। UI में क्या दिखेगा और कैसे ठीक करें?

Answer: बिना guard के देर से आया "pi" का response "pizza" का result overwrite कर देगा (race condition)। हल: हर call का id रखकर सिर्फ latest स्वीकारो, या पुरानी request `AbortController` से cancel करो, और typing पर debounce लगाओ।

---

## ⚫ Interview Questions + Answers
Q1: Spinner बनाम skeleton?
A1: Skeleton layout का आभास देता है, perceived speed बेहतर; spinner छोटे/अनजान duration के लिए।

Q2: Empty और error अलग क्यों?
A2: Empty = सफल पर data नहीं; error = fail। संदेश/action अलग हैं।

Q3: Pull-to-refresh कैसे?
A3: `FlatList` का `refreshControl` / `refreshing` + `onRefresh`।

Q4: Pagination footer loading?
A4: `ListFooterComponent` में spinner, `onEndReached` से अगला page, double-trigger से बचाओ।

Q5: React Query से क्या मिलता है?
A5: `isPending/isError/isFetching/data` ready; caching, retry, refetch built-in।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- कोई भी async data screen

❌ Avoid when:
- Static screen (कोई fetch नहीं)

---

## 📊 Visual Diagram
```
 idle ──fetch──► loading ──ok──► success ──(data=[])──► empty UI
                    │                │
                    └──fail──► error ◄── retry ──┘
 refresh: success ─► (पुराना data + छोटा spinner) ─► success
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Skeleton | Placeholder shapes | Placeholder ढाँचा |
| Empty state | Success but no data | डेटा नहीं मिला स्थिति |
| Race condition | Late old response wins | पुराना जवाब बाद में आना |
| Debounce | Wait before firing | रुककर चलाना |
| Pull-to-refresh | Swipe down to reload | नीचे खींचकर reload |

---

## ⚡ 3-Line Summary
English: Use a single status instead of many booleans.
Render exactly one of loading, error, empty or success.
Guard against stale responses.

Hindi: कई booleans की जगह एक status रखो।
Loading, error, empty या success में से एक ही दिखाओ।
पुराने responses से बचाव करो।

---

## ➡️ Next Topic
**147. Offline Support** — internet न हो तब भी app को उपयोगी रखना।
