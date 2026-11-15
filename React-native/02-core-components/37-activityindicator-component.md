# 37. ActivityIndicator Component
# हिंदी में: ActivityIndicator (Loading Spinner)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 / React Native 0.76 के हिसाब से (check current docs — APIs change between SDKs)। Core component, कोई install नहीं।

---

## 🔵 Simple Definition (English)
`ActivityIndicator` shows a native spinning loader. It tells the user that something is loading or processing.

## 🔵 सरल परिभाषा (Hindi)
`ActivityIndicator` एक native घूमने वाला loader (spinner) दिखाता है। यह user को बताता है कि कुछ load या process हो रहा है।

---

## 🔴 Problem it Solves
```
❌ API call के दौरान खाली screen — user को लगता है app hang हो गया
❌ Button दबाने के बाद कोई feedback नहीं, तो user बार-बार दबाता है
❌ हर बार custom spinner बनाना पड़ता
```

## 🔴 यह क्यों बना? (Hindi)
```
Network धीमा हो सकता है। Spinner से user को भरोसा होता है कि काम चल रहा है।
यह native है, इसलिए हर OS पर अपना असली look देता है।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → state बनाओ: const [loading, setLoading] = useState(true)
Step 2 → API call से पहले loading = true
Step 3 → loading true हो तो <ActivityIndicator /> दिखाओ
Step 4 → data आए या error आए → finally में loading = false
Step 5 → spinner हटाकर असली content दिखाओ
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → loading state बनाओ
Step 2 → API से पहले true करो
Step 3 → true होने पर ActivityIndicator दिखाओ
Step 4 → finally में false करो (सफल या fail दोनों में)
Step 5 → spinner हटाकर असली content दिखाओ
```

---

## 🟡 Real World Example
**Swiggy** में restaurant list आने तक spinner/shimmer, **Paytm** में payment process होते समय spinner, **Zomato** में pull-to-refresh का spinner। Button के अंदर छोटा spinner भी आम है ("Placing order...")।

## 🟡 Real Example Hindi mein
Swiggy में "Place Order" दबाते ही button के अंदर spinner घूमता है और button disabled हो जाता है, ताकि दो बार order न जाए।

---

## 💻 Code Example — Basic
```jsx
// Basic: spinner + simple loading
import React, { useEffect, useState } from 'react';            // hooks
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native'; // UI

export default function Basic() {
  const [loading, setLoading] = useState(true);                // शुरू में loading

  useEffect(() => {
    const id = setTimeout(() => setLoading(false), 2000);      // 2 सेकंड बाद खत्म (नकली API)
    return () => clearTimeout(id);                             // cleanup
  }, []);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#e23744" />{/* बड़ा लाल spinner */}
      </View>
    );
  }
  return <View style={styles.center}><Text>Loaded!</Text></View>; // content
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' }, // बीच में
});
```

## 💻 Code Example — Advanced
```jsx
// Advanced: fetch + loading/error/empty states + button में spinner + double-tap रोकना
import React, { useCallback, useEffect, useState } from 'react'; // hooks
import { View, Text, Pressable, FlatList, ActivityIndicator, StyleSheet } from 'react-native'; // UI

export default function Restaurants() {
  const [data, setData] = useState([]);                        // list
  const [loading, setLoading] = useState(true);                // पहला load
  const [error, setError] = useState(null);                    // error
  const [ordering, setOrdering] = useState(false);             // button loading

  const load = useCallback(async () => {
    setLoading(true); setError(null);                          // reset
    try {
      const res = await fetch('https://jsonplaceholder.typicode.com/users'); // demo API
      if (!res.ok) throw new Error('HTTP ' + res.status);      // status जाँच
      setData(await res.json());                               // data रखो
    } catch (e) {
      setError(e.message);                                     // error रखो
    } finally {
      setLoading(false);                                       // हमेशा बंद
    }
  }, []);

  useEffect(() => { load(); }, [load]);                        // mount पर load

  const placeOrder = async () => {
    if (ordering) return;                                      // double-tap guard
    setOrdering(true);
    await new Promise((r) => setTimeout(r, 1500));             // नकली order API
    setOrdering(false);
  };

  if (loading) return <ActivityIndicator style={styles.flex} size="large" />; // पूरी screen spinner
  if (error) return (
    <View style={styles.center}>
      <Text>{error}</Text>
      <Pressable onPress={load}><Text style={styles.link}>Retry</Text></Pressable>
    </View>
  );

  return (
    <View style={styles.flex}>
      <FlatList
        data={data}
        keyExtractor={(i) => String(i.id)}
        renderItem={({ item }) => <Text style={styles.row}>{item.name}</Text>}
        ListEmptyComponent={<Text>कुछ नहीं मिला</Text>}        // empty state
      />
      <Pressable style={[styles.btn, ordering && styles.btnOff]} onPress={placeOrder} disabled={ordering}>
        {ordering ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Place Order</Text>}
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  row: { padding: 12 },
  link: { color: '#e23744', marginTop: 8 },
  btn: { backgroundColor: '#e23744', padding: 14, alignItems: 'center', margin: 16, borderRadius: 8 },
  btnOff: { opacity: 0.6 },
  btnText: { color: '#fff', fontWeight: '700' },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| `size` | `'small' \| 'large'` या **number** (जैसे 48) | सिर्फ `'small'` / `'large'` (number ❌, पुराने versions में) |
| Default रंग | Material teal/हल्का | ग्रे |
| Look | गोल घूमता Material progress | UIKit का पंखुड़ी जैसा spinner |
| `hidesWhenStopped` | ❌ | ✅ (`animating={false}` पर छुपाता है) |
| `animating={false}` | spinner छुप जाता है | `hidesWhenStopped` से तय |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo Go में सीधे — import बस react-native से
import { ActivityIndicator } from 'react-native';
<ActivityIndicator size="large" />
```
CLI way:
```jsx
// CLI में भी वही; कोई pod/gradle बदलाव नहीं
import { ActivityIndicator } from 'react-native';
<ActivityIndicator size="large" />
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `animating={false}` लगाकर सोचना कि component हटा
✅ Correct: Conditional rendering (`{loading && <ActivityIndicator />}`) करो।

❌ Mistake 2: Spinner का `color` न देना, सफ़ेद background पर दिखता नहीं
✅ Correct: साफ़ दिखने वाला `color` दो।

❌ Mistake 3: `finally` में loading false न करना, error पर spinner चलता रहता है
✅ Correct: `try/catch/finally` इस्तेमाल करो।

---

## 🧠 Tricky Interview Question
```jsx
<ActivityIndicator size={60} />
```
**Q: दोनों platform पर क्या होगा?**

Answer: Android पर numeric size काम करता है (60 dp का spinner)। iOS पर numeric size सपोर्ट नहीं है (सिर्फ `small`/`large`), इसलिए cross-platform के लिए `size="large"` और `transform: [{ scale: 1.5 }]` से बड़ा किया जा सकता है।

---

## ⚫ Interview Questions + Answers
Q1: ActivityIndicator कब दिखाएँ?
A1: जब काम अनिश्चित समय का हो (API, upload)। निश्चित progress हो तो progress bar।

Q2: Shimmer/Skeleton vs spinner?
A2: Content का आकार पता हो तो skeleton बेहतर UX; अज्ञात हो तो spinner।

Q3: Button को double-tap से कैसे बचाएँ?
A3: Loading में `disabled` + spinner।

Q4: पूरी screen block कैसे?
A4: `Modal` या absolute overlay `View` में ActivityIndicator।

Q5: रंग कैसे बदलें?
A5: `color` prop।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- छोटी, अनिश्चित loading
- Button के अंदर submit/process feedback

❌ Avoid when:
- लंबे upload (progress % दिखाओ)
- List load जिसका layout पता हो (skeleton)

---

## 📊 Visual Diagram
```
 loading=true  ──►  [  ◌ spinner  ]
        │ API done / error (finally)
        ▼
 loading=false ──►  [ असली content ]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Spinner | घूमता loader | घूमने वाला निशान |
| animating | घूम रहा है या नहीं | चल रहा है? |
| size | small/large (Android में number) | आकार |
| Skeleton | खाका वाला placeholder | खाली ढाँचा |
| finally | हमेशा चलने वाला block | हर हाल में चलने वाला |

---

## ⚡ 3-Line Summary
English:
1. `ActivityIndicator` is a native spinner for loading.
2. Use `size`, `color`, and conditional rendering; reset loading in `finally`.
3. Numeric `size` works on Android only.

Hindi:
1. `ActivityIndicator` loading का native spinner है।
2. `size`, `color` और conditional rendering इस्तेमाल करो; `finally` में loading बंद करो।
3. Numeric `size` सिर्फ Android पर चलता है।

---

## ➡️ Next Topic
**38. Modal Component** — screen के ऊपर popup/overlay दिखाना।
