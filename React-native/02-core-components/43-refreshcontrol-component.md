# 43. RefreshControl Component
# हिंदी में: RefreshControl (Pull-to-Refresh)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52 (React Native 0.76) — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
**RefreshControl** adds the "pull down to refresh" gesture to a `ScrollView`, `FlatList` or `SectionList`. You pass it through the `refreshControl` prop, give it a `refreshing` boolean and an `onRefresh` function.

## 🔵 सरल परिभाषा (Hindi)
**RefreshControl** `ScrollView`, `FlatList` या `SectionList` में "नीचे खींचकर refresh" वाला gesture जोड़ता है। आप इसे `refreshControl` prop से देते हो, साथ में `refreshing` (true/false) और `onRefresh` function देते हो।

---

## 🔴 Problem it Solves
```
BEFORE RefreshControl:
❌ Data update करने के लिए अलग "Reload" button बनाना पड़ता था
❌ Gesture + spinner हाथ से बनाना (PanResponder) बहुत मुश्किल
❌ Android और iOS का native spinner अलग-अलग दिखता है
```

## 🔴 यह क्यों बना? (Hindi)
```
RefreshControl से पहले:
❌ Data refresh के लिए अलग "Reload" button बनाना पड़ता था
❌ Pull gesture + spinner खुद बनाना बहुत कठिन था
❌ Android/iOS का native spinner अलग होता है
RefreshControl: native pull-to-refresh एक prop में!
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → List scroll के top पर हो, user नीचे pull करता है
Step 2 → Native spinner दिखता है (Android: circle, iOS: activity indicator)
Step 3 → Threshold पार होते ही onRefresh() call होता है
Step 4 → आप setRefreshing(true) करते हो और API call करते हो
Step 5 → Data आने पर setRefreshing(false) → spinner गायब
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → List सबसे ऊपर हो, user नीचे खींचता है
Step 2 → Native spinner दिखता है
Step 3 → काफ़ी खींचने पर onRefresh() call होता है
Step 4 → आप refreshing=true करके API call करते हो
Step 5 → Data आने पर refreshing=false → spinner बंद
```

---

## 🟡 Real World Example
**Swiggy** के order history में नीचे खींचने पर latest orders reload होते हैं। **Paytm** की transaction history और **Zomato** की "Your orders" list में भी pull-to-refresh मिलता है।

## 🟡 Real Example Hindi mein
**Swiggy** के order history में नीचे खींचो तो नए orders आ जाते हैं। **Paytm** की transaction list और **Zomato** की "Your orders" में भी यही pull-to-refresh है।

---

## 💻 Code Example — Basic

```jsx
// Basic: ScrollView + RefreshControl
import React, { useState, useCallback } from 'react'; // hooks
import { ScrollView, RefreshControl, Text, StyleSheet } from 'react-native'; // components

export default function BasicRefresh() {
  const [refreshing, setRefreshing] = useState(false);   // spinner state
  const [time, setTime] = useState(new Date().toLocaleTimeString()); // demo data

  const onRefresh = useCallback(() => {                  // pull hone par chalega
    setRefreshing(true);                                  // spinner start
    setTimeout(() => {                                    // fake API (1.5s)
      setTime(new Date().toLocaleTimeString());           // data update
      setRefreshing(false);                               // spinner stop
    }, 1500);
  }, []);

  return (
    <ScrollView
      contentContainerStyle={styles.container}            // content styling
      refreshControl={                                    // yahan attach hota hai
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Last updated text */}
      <Text style={styles.text}>Last updated: {time}</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flexGrow: 1, alignItems: 'center', justifyContent: 'center' }, // center; flexGrow zaroori
  text: { fontSize: 18 },                                 // text size
});
```

## 💻 Code Example — Advanced

```jsx
// Advanced: FlatList + RefreshControl + error handling + platform colours
import React, { useState, useCallback, useEffect } from 'react'; // hooks
import { FlatList, RefreshControl, Text, View, Platform, StyleSheet } from 'react-native'; // RN

// Fake API: orders laata hai, kabhi fail bhi hota hai
const fetchOrders = () =>
  new Promise((resolve, reject) =>
    setTimeout(() => (Math.random() > 0.2
      ? resolve([{ id: String(Date.now()), name: 'Paneer Tikka', price: 249 }])
      : reject(new Error('Network error'))), 800));

export default function Orders() {
  const [orders, setOrders] = useState([]);              // list data
  const [refreshing, setRefreshing] = useState(false);   // pull-to-refresh flag
  const [error, setError] = useState(null);              // error message

  const load = useCallback(async () => {                 // common loader
    try {
      setError(null);                                    // purana error hatao
      const data = await fetchOrders();                  // API call
      setOrders(prev => [...data, ...prev]);             // naya data upar
    } catch (e) {
      setError(e.message);                               // error dikhao
    }
  }, []);

  useEffect(() => { load(); }, [load]);                  // first load

  const onRefresh = useCallback(async () => {
    setRefreshing(true);                                 // spinner on
    await load();                                        // data lao
    setRefreshing(false);                                // spinner off (finally ke baad)
  }, [load]);

  return (
    <FlatList
      data={orders}                                      // items
      keyExtractor={item => item.id}                     // unique key
      renderItem={({ item }) => (
        <View style={styles.row}>
          <Text>{item.name}</Text>
          <Text>₹{item.price}</Text>
        </View>
      )}
      ListHeaderComponent={error ? <Text style={styles.err}>{error}</Text> : null} // error banner
      refreshControl={
        <RefreshControl
          refreshing={refreshing}                        // controlled prop
          onRefresh={onRefresh}                          // pull handler
          tintColor="#E23744"                            // iOS spinner colour
          colors={['#E23744', '#fc8019']}                // Android spinner colours
          progressBackgroundColor="#fff"                 // Android circle background
          progressViewOffset={Platform.OS === 'android' ? 20 : 0} // Android offset
        />
      }
    />
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', justifyContent: 'space-between', padding: 16, borderBottomWidth: StyleSheet.hairlineWidth }, // row
  err: { color: 'red', padding: 12 },                    // error text
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Spinner colour prop | `colors` (array), `progressBackgroundColor` | `tintColor`, `title`, `titleColor` |
| Spinner look | Material circle | Activity indicator |
| Offset | `progressViewOffset` | iOS पर नहीं |
| Size | `size` (`RefreshLayoutConsts.SIZE`) | N/A |
| Enabled | `enabled` prop (Android only) | हमेशा on |

---

## 🟠 Expo vs CLI Difference
**Expo way:** (कुछ install नहीं, RN core का हिस्सा)
```jsx
import { RefreshControl } from 'react-native'; // Expo Go me seedha chalta hai
```
**CLI way:**
```jsx
import { RefreshControl } from 'react-native'; // same code, koi pod/gradle change nahi
```
Dono में code same है — यह core component है।

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** `refreshing` कभी false नहीं करना (spinner हमेशा घूमता रहेगा)
✅ **Correct:** `finally` में `setRefreshing(false)` करो ताकि error पर भी रुके।

❌ **Mistake 2:** ScrollView के बाहर RefreshControl लगाना
```jsx
// WRONG: <View><RefreshControl .../></View>  // kaam nahi karega
// CORRECT: <ScrollView refreshControl={<RefreshControl .../>} />
```
✅ **Correct:** `refreshControl` prop से दो।

❌ **Mistake 3:** FlatList में `onRefresh` + `refreshing` को सीधे दे सकते हैं, फिर भी दोनों तरीके एक साथ लगाना
✅ **Correct:** एक ही तरीका चुनो (या तो `refreshControl`, या FlatList के `refreshing`/`onRefresh` props)।

---

## 🧠 Tricky Interview Question
**Q: `refreshing` हमेशा `false` रखा और सिर्फ `onRefresh` में API call की — क्या होगा?**

**Answer:** Component controlled है। Pull करने पर native spinner थोड़ी देर दिख सकता है, पर `refreshing` false होने से React उसे वापस false कर देता है और spinner फौरन गायब हो जाता है, जबकि API चल रही होती है। इसलिए user को feedback नहीं मिलता। Fix: `onRefresh` में पहले `setRefreshing(true)` करो।

---

## ⚫ Interview Questions + Answers

**Q1: Pull-to-refresh कैसे लगाते हैं?**
A1: `RefreshControl` बनाकर `refreshControl` prop में दो (`refreshing` + `onRefresh` ज़रूरी)।

**Q2: FlatList में और आसान तरीका?**
A2: FlatList पर सीधे `refreshing` और `onRefresh` props दे सकते हो; वह internally RefreshControl बनाता है।

**Q3: Android और iOS का spinner रंग कैसे बदलें?**
A3: Android: `colors`, `progressBackgroundColor`; iOS: `tintColor`।

**Q4: Pull-to-refresh vs infinite scroll?**
A4: Refresh = top से fresh data; infinite scroll = `onEndReached` से अगला page। दोनों साथ चलते हैं।

**Q5: Refresh के दौरान duplicate calls कैसे रोकें?**
A5: `if (refreshing) return;` guard या request cancel (AbortController) use करो।

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Orders, feed, transactions जैसी list
- User manually latest data चाहता है

❌ **Avoid when:**
- Real-time data (WebSocket से अपने-आप आता हो)
- Horizontal list / static screen
- Critical action (payment) जिसे गलती से trigger न होने दें

---

## 📊 Visual Diagram
```
  user pull ↓
 ┌──────────────┐
 │     ◌ spin   │  ← RefreshControl (native)
 ├──────────────┤
 │  item 1      │
 │  item 2      │
 └──────────────┘
 onRefresh() → refreshing=true → API → refreshing=false
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| refreshing | Is refresh in progress | Refresh चल रहा है? |
| onRefresh | Callback on pull | Pull पर चलने वाला function |
| tintColor | iOS spinner colour | iOS spinner का रंग |
| colors | Android spinner colours | Android spinner के रंग |
| Controlled | State drives UI | State से चलने वाला |

---

## ⚡ 3-Line Summary
**English:**
1. RefreshControl gives native pull-to-refresh to scrollable lists.
2. Needs `refreshing` and `onRefresh`; always reset refreshing in finally.
3. Colour props differ: `tintColor` iOS, `colors` Android.

**Hindi:**
1. RefreshControl scrollable lists में native pull-to-refresh देता है।
2. `refreshing` और `onRefresh` चाहिए; finally में refreshing false करो।
3. Colour props अलग हैं: iOS `tintColor`, Android `colors`।

---

## ➡️ Next Topic
**44. VirtualizedList** — FlatList के पीछे का base component और custom data sources।
