# 281. Interview Problem: Build Pull to Refresh
# हिंदी में: Pull to Refresh बनाओ
# Platform: Android ✅ | iOS ✅ | Both ✅
# Difficulty: ⭐⭐ Easy-Medium | Asked at: Swiggy, Zomato, Paytm, Flipkart
# Expo SDK 52 / React Native 0.76 (check current docs — APIs change between SDKs)

> Code files in this folder: `PullToRefreshScreen.jsx`. Copy them into your Expo project and import the main one in `App.js`.
> **Verification note:** syntax-checked with esbuild and rendered under jsdom via react-native-web (initial render + state logic). Real device behaviour (native spinner, gestures) not run.

---

## 🔴 Problem Statement
Build an orders list screen. When the user pulls down from the top, show a spinner, re-fetch the data and replace the list. Handle error state and empty state.

**Constraints:** use `FlatList` + `RefreshControl`; spinner must always stop (even on error); list must be pullable even when empty.

---

## 🔵 Simple Definition (English)
Pull to refresh means the user drags the list down to reload fresh data. React Native gives `RefreshControl` for this.

## 🔵 सरल परिभाषा (Hindi)
Pull to refresh का मतलब है यूज़र लिस्ट को नीचे खींचकर नया डेटा लोड करे। React Native में इसके लिए `RefreshControl` मिलता है।

---

## 🔴 Problem it Solves
Before this, apps needed a manual 'Reload' button. Users expect the same gesture as Instagram or Swiggy; without it the screen shows stale data.

## 🔴 यह क्यों बना? (Hindi)
पहले ऐप में 'Reload' बटन लगाना पड़ता था। यूज़र Swiggy/Instagram जैसा खींचने वाला gesture चाहता है, वरना पुराना डेटा दिखता रहता है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → Keep `refreshing` boolean in state
Step 2 → Pass <RefreshControl refreshing onRefresh /> to FlatList refreshControl prop
Step 3 → User pulls -> onRefresh runs -> set refreshing true
Step 4 → await API, REPLACE list data
Step 5 → set refreshing false in finally
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → state में `refreshing` boolean रखो
Step 2 → FlatList के `refreshControl` prop में RefreshControl दो
Step 3 → यूज़र खींचता है -> onRefresh चलता है -> refreshing = true
Step 4 → API का इंतज़ार, लिस्ट को REPLACE करो (append नहीं)
Step 5 → अंत में refreshing = false
```

---

## 🟡 Real World Example
Swiggy's Orders tab and Zomato's home feed: pull down, spinner appears, restaurants/orders reload.

## 🟡 Real Example Hindi mein
Swiggy के Orders टैब और Zomato के होम फीड में नीचे खींचो तो spinner आता है और नया डेटा लोड होता है।

---

## 💻 Code Example — Basic
```jsx
// Smallest possible pull to refresh
import React, { useState } from 'react'; // state hook
import { FlatList, RefreshControl, Text } from 'react-native'; // core

export default function Mini() {
  const [data, setData] = useState([1, 2, 3]); // list data
  const [refreshing, setRefreshing] = useState(false); // spinner flag
  const onRefresh = async () => { // pull handler
    setRefreshing(true); // show spinner
    await new Promise((r) => setTimeout(r, 1000)); // fake API
    setData([4, 5, 6]); // replace data
    setRefreshing(false); // hide spinner
  };
  return (
    <FlatList
      data={data} // data
      keyExtractor={(i) => String(i)} // key
      renderItem={({ item }) => <Text>{item}</Text>} // row
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />} // pull
    />
  );
}
```

## 💻 Code Example — Advanced (complete solution, every line commented)
**File: `PullToRefreshScreen.jsx`**
```jsx
// Expo SDK 52 (check current docs - APIs change between SDKs)
import React, { useState, useCallback, useEffect } from 'react'; // React + hooks
import { View, Text, FlatList, RefreshControl, StyleSheet, Platform } from 'react-native'; // RN core

// Fake API: returns orders after 800ms (replace with fetch())
const fetchOrders = () =>
  new Promise((resolve) =>
    setTimeout(() => resolve([ // simulate network delay
      { id: String(Date.now()) + 'a', title: 'Biryani - Paradise', time: new Date().toLocaleTimeString() }, // item 1
      { id: String(Date.now()) + 'b', title: 'Masala Dosa - Saravana', time: new Date().toLocaleTimeString() }, // item 2
    ]), 800));

export default function PullToRefreshScreen() {
  const [orders, setOrders] = useState([]); // list data
  const [refreshing, setRefreshing] = useState(false); // spinner state (controlled)
  const [error, setError] = useState(null); // error message

  const load = useCallback(async () => { // shared loader
    try {
      setError(null); // clear old error
      const data = await fetchOrders(); // call API
      setOrders(data); // replace list (refresh = replace, not append)
    } catch (e) {
      setError('Refresh failed. Pull again.'); // show error
    }
  }, []);

  useEffect(() => { load(); }, [load]); // first load on mount

  const onRefresh = useCallback(async () => { // called when user pulls
    setRefreshing(true); // show spinner
    await load(); // wait for data
    setRefreshing(false); // hide spinner (always, even on error)
  }, [load]);

  return (
    <View style={styles.container}>
      {error && <Text style={styles.error}>{error}</Text>}
      <FlatList
        data={orders} // list data
        keyExtractor={(item) => item.id} // stable key
        renderItem={({ item }) => ( // one row
          <View style={styles.row}>
            <Text style={styles.title}>{item.title}</Text>
            <Text style={styles.time}>{item.time}</Text>
          </View>
        )}
        refreshControl={
          <RefreshControl
            refreshing={refreshing} // controlled spinner
            onRefresh={onRefresh} // pull handler
            tintColor="#E23744" // iOS spinner colour
            colors={['#E23744']} // Android spinner colours
            progressViewOffset={Platform.OS === 'android' ? 8 : 0} // Android only offset
          />
        }
        contentContainerStyle={{ flexGrow: 1 }} // so empty list is still pullable
        ListEmptyComponent={<Text style={styles.empty}>No orders yet</Text>} // empty state
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' }, // full screen
  row: { padding: 16, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: '#ddd' }, // row card
  title: { fontSize: 16, fontWeight: '600' }, // title text
  time: { color: '#666', marginTop: 4 }, // sub text
  error: { color: 'red', padding: 8, textAlign: 'center' }, // error banner
  empty: { textAlign: 'center', marginTop: 40, color: '#999' }, // empty text
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Spinner look | Material circular spinner dropping from top (`colors`, `progressBackgroundColor`) | Native UIRefreshControl spinner (`tintColor`, `title`) |
| Colour props | `colors`, `progressBackgroundColor` | `tintColor`, `titleColor` |
| Offset | `progressViewOffset` moves spinner (Android only) | Not available |
| Overscroll | Needs list at scroll offset 0 (nested scroll issues) | Works with bounce; always natural |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx expo install   # RefreshControl is part of react-native core, nothing extra to install
npx expo start
```
CLI way (bare React Native):
```bash
npx react-native init MyApp   # RefreshControl is core too
npx react-native run-android
```
Same code in both: `RefreshControl` is core React Native, so there is no Expo vs CLI difference here.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Never setting `refreshing` back to false (spinner stays forever when API fails).
✅ Correct: Use try/finally so `setRefreshing(false)` always runs.

❌ Mistake 2: Appending data on refresh, so rows duplicate.
✅ Correct: Refresh must REPLACE the list; only pagination appends.

❌ Mistake 3: Putting FlatList inside a ScrollView, so the pull never fires.
✅ Correct: Let FlatList be the scroll container; use ListHeaderComponent for extra UI.

---

## 🧠 Tricky Interview Question
User pulls to refresh but the empty-state list does not respond. Why?

Answer: If `ListEmptyComponent` is small and the list content is shorter than the screen, there is nothing to scroll, so pull does not trigger on some platforms. Fix: `contentContainerStyle={{ flexGrow: 1 }}` so the content fills the screen (done in our file). Hindi: खाली लिस्ट छोटी होती है तो scroll नहीं होता, इसलिए `flexGrow: 1` दो।

---

## ⚫ Interview Questions + Answers
Q1: Is `refreshing` controlled or uncontrolled?
A1: Controlled. You own the boolean; RefreshControl only shows it. If you do not update it the spinner will snap back (iOS) or stay (Android).

Q2: Difference between pull to refresh and infinite scroll?
A2: Refresh replaces data from page 1 at the top. Infinite scroll appends next pages at the bottom.

Q3: Can FlatList have `onRefresh` and `refreshing` props directly?
A3: Yes, FlatList has shortcut props `onRefresh` + `refreshing`. Use `refreshControl` when you need colours/offset.

Q4: How to avoid double refresh calls?
A4: Ignore onRefresh while `refreshing` is true, or keep a ref lock.

Q5: How to refresh on screen focus too?
A5: With React Navigation use `useFocusEffect` and call the same load function.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- List data can go stale (orders, feed, notifications)
- User expects gesture reload

❌ Avoid when:
- Realtime data already pushed by websocket
- Screens without a vertical scroll container

---

## 📊 Visual Diagram
```
User drags down
      |
      v
 RefreshControl --onRefresh--> set refreshing=true
      |                              |
      |                        await fetch()
      |                              |
      +<----- list replaced <--------+
      |
 set refreshing=false (spinner hides)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RefreshControl | Pull-to-refresh component | खींचकर रिफ्रेश वाला कॉम्पोनेंट |
| refreshing | Boolean for spinner visibility | spinner दिख रहा है या नहीं |
| onRefresh | Callback on pull | खींचने पर चलने वाला फंक्शन |
| Controlled | Parent owns the state | state पैरेंट के पास |
| flexGrow | Make content fill container | कंटेंट को पूरी जगह देना |

---

## ⚡ 3-Line Summary
English: RefreshControl + a boolean state gives pull to refresh.
Always reset the boolean in finally.
Refresh replaces data; pagination appends.
Hindi: RefreshControl और एक boolean state से pull to refresh बनता है।
boolean को हमेशा finally में false करो।
Refresh डेटा replace करता है, pagination append करता है।

---

## ➡️ Next Topic
282 — Build Infinite Scroll FlatList: the bottom-side partner of pull to refresh (load next pages).
