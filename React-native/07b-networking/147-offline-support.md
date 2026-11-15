# 147. Offline Support
# हिंदी में: Offline Support — Internet के बिना भी app चलाना
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 52 target (check current docs — APIs change between SDKs).** React Native 0.76, `@react-native-async-storage/async-storage` 1.23.x, `@react-native-community/netinfo` 11.x, TanStack Query v5 (optional)। Storage और NetInfo native modules हैं पर Expo Go में शामिल हैं।

---

## 🔵 Simple Definition (English)
**Offline support** means the app still shows useful data and lets users do actions when there is no internet. Data is cached locally, and actions are queued and sent when the connection returns.

## 🔵 सरल परिभाषा (Hindi)
**Offline support** का मतलब है कि internet न होने पर भी app उपयोगी data दिखाए और user को actions करने दे। Data locally cache होता है और actions queue में रखकर connection लौटने पर server को भेजे जाते हैं।

---

## 🔴 Problem it Solves
```
भारत में network असमान है — मेट्रो, गाँव, बेसमेंट।
Offline support के बिना: खाली screen, "No internet" और user चला जाता है।
साथ: बार-बार वही data download = data और battery खर्च।
```

## 🔴 यह क्यों बना? (Hindi)
```
Network हमेशा नहीं मिलता।
पिछला देखा हुआ data cache में रहे तो app फिर भी खुलती है।
Actions queue हों तो connection आते ही अपने आप sync।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Fetch सफल → data AsyncStorage/SQLite में cache (timestamp सहित)
Step 2 → अगली बार app खुले → पहले cache दिखाओ (instant)
Step 3 → Online हो तो background में fresh fetch → cache + UI update (stale-while-revalidate)
Step 4 → Offline हो तो cache + "Offline" banner
Step 5 → Offline में user action (like, order note) → queue में save
Step 6 → NetInfo online बताए → queue को क्रम से भेजो, सफल होने पर हटाओ
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. सफल response को local storage में रखो।
2. App खुलते ही cache दिखाओ, फिर नया data लाओ।
3. Offline हो तो cache + banner।
4. Offline actions को queue में रखो।
5. Online होते ही queue भेजो।
```

---

## 🟡 Real World Example
**WhatsApp:** Offline में message लिखो → घड़ी का icon; internet आते ही send। **Zomato:** पुराने orders और menu cache से दिखते हैं। **Google Maps:** offline maps। **Paytm:** transaction history cache से खुलती है पर नया payment offline नहीं (सुरक्षा कारण) — यानी सब actions queue नहीं होने चाहिए।

## 🟡 Real Example Hindi mein
**WhatsApp** में बिना internet message लिखते हैं (queue में) और network आते ही चला जाता है। **Paytm** में history offline दिखती है पर पैसा भेजना नहीं — हर action offline योग्य नहीं होता।

---

## 💻 Code Example — Basic

```jsx
// OfflineBasic.jsx — cache-first list with AsyncStorage
import React, { useEffect, useState } from 'react';               // hooks
import { View, Text, FlatList } from 'react-native';              // UI
import AsyncStorage from '@react-native-async-storage/async-storage'; // local storage

const KEY = 'cache:posts';                                        // storage key

export default function OfflineBasic() {
  const [posts, setPosts] = useState([]);                         // data
  const [fromCache, setFromCache] = useState(false);              // cache से है?

  useEffect(() => {
    let alive = true;                                             // unmount guard
    (async () => {
      try {
        const cached = await AsyncStorage.getItem(KEY);           // पहले cache
        if (cached && alive) { setPosts(JSON.parse(cached)); setFromCache(true); } // instant UI
      } catch {}                                                  // corrupt cache ignore
      try {
        const res = await fetch('https://jsonplaceholder.typicode.com/posts?_limit=10'); // fresh
        if (!res.ok) throw new Error('HTTP ' + res.status);       // HTTP error
        const fresh = await res.json();                           // parse
        await AsyncStorage.setItem(KEY, JSON.stringify(fresh));   // cache update
        if (alive) { setPosts(fresh); setFromCache(false); }      // UI update
      } catch {
        // offline/fail: cache वाला data ही रहने दो
      }
    })();
    return () => { alive = false; };                              // cleanup
  }, []);

  return (
    <View style={{ flex: 1 }}>
      {fromCache && <Text style={{ backgroundColor: '#fde68a', padding: 6 }}>पुराना data (offline?)</Text>}
      <FlatList data={posts} keyExtractor={(p) => String(p.id)}
        renderItem={({ item }) => <Text style={{ padding: 12 }}>{item.title}</Text>} />
    </View>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// offlineQueue.js — persistent action queue, flushed when online (logic)
import AsyncStorage from '@react-native-async-storage/async-storage'; // storage
import NetInfo from '@react-native-community/netinfo';                // connectivity

const QUEUE_KEY = 'offline:queue';                                    // key

export async function enqueue(action) {                               // action = { id, method, url, body }
  const raw = await AsyncStorage.getItem(QUEUE_KEY);                  // existing
  const queue = raw ? JSON.parse(raw) : [];                           // parse
  queue.push({ ...action, id: action.id ?? String(Date.now()) });     // unique id (idempotency key)
  await AsyncStorage.setItem(QUEUE_KEY, JSON.stringify(queue));       // save
}

let flushing = false;                                                 // दोहरा flush रोकने को

export async function flush(send) {                                   // send(action) → Promise
  if (flushing) return;                                               // पहले से चल रहा
  flushing = true;
  try {
    const raw = await AsyncStorage.getItem(QUEUE_KEY);                // queue पढ़ो
    let queue = raw ? JSON.parse(raw) : [];
    while (queue.length) {
      try {
        await send(queue[0]);                                         // भेजो (server idempotency key से duplicate रोके)
        queue = queue.slice(1);                                       // सफल → हटाओ
        await AsyncStorage.setItem(QUEUE_KEY, JSON.stringify(queue)); // progress save
      } catch (e) {
        break;                                                        // fail → बाद में फिर कोशिश (क्रम बना रहे)
      }
    }
  } finally {
    flushing = false;                                                 // flag reset
  }
}

export function startAutoFlush(send) {                                // app start पर एक बार call
  return NetInfo.addEventListener((s) => {                            // connectivity बदलने पर
    if (s.isConnected && s.isInternetReachable !== false) flush(send); // online → flush
  });                                                                 // returns unsubscribe
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| AsyncStorage backend | SQLite (default 6MB limit, configurable) | Files / dictionary |
| Background sync | WorkManager (library के ज़रिए) | BGTaskScheduler (सीमित, OS तय करता है) |
| NetInfo | ConnectivityManager | NWPathMonitor |
| Storage clear | App data clear से सब गायब | App delete पर गायब |
| Logic | Same | Same |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install @react-native-async-storage/async-storage @react-native-community/netinfo
// बड़े structured data: npx expo install expo-sqlite
```
CLI way:
```jsx
// npm i @react-native-async-storage/async-storage @react-native-community/netinfo
// cd ios && pod install
// बड़े data: react-native-mmkv या WatermelonDB (native setup जरूरी)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: AsyncStorage में बड़ी list/images रखना।
✅ Correct: SQLite/MMKV; images के लिए file cache।

❌ Mistake 2: Cache की expiry न रखना।
✅ Correct: timestamp रखो और TTL के बाद refresh।

❌ Mistake 3: Queue में duplicate actions (retry पर दो बार order)।
✅ Correct: Idempotency key भेजो।

❌ Mistake 4: `isConnected` को पक्का internet मान लेना।
✅ Correct: `isInternetReachable` भी देखो।

---

## 🧠 Tricky Interview Question
User offline में 3 बार "Like" दबाता है (toggle)। Queue में 3 actions हैं। Online होने पर क्या भेजें?

Answer: तीनों भेजना बेकार/गलत हो सकता है (like→unlike→like)। बेहतर: **final state** (liked) को एक ही action में collapse करो, या actions को idempotent "set liked=true" रखो। Queue design में conflict resolution सोचना जरूरी है।

---

## ⚫ Interview Questions + Answers
Q1: Stale-while-revalidate क्या?
A1: पुराना cache तुरंत दिखाओ और पीछे से fresh लाकर update करो।

Q2: AsyncStorage vs SQLite vs MMKV?
A2: AsyncStorage सरल key-value (async, धीमा); MMKV बहुत तेज़ key-value (native); SQLite structured/queryable data।

Q3: Offline-first और cache में फर्क?
A3: Offline-first में local DB source of truth है और server से sync होता है; cache सिर्फ़ speed/backup।

Q4: Conflict कैसे सुलझाएँ?
A4: Last-write-wins, version/timestamp, या server-side merge।

Q5: TanStack Query से offline?
A5: `networkMode`, `persistQueryClient` + AsyncStorage persister, mutations queue — docs देखो (v5)।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Read-heavy apps (news, menu, history)
- Low-network users

❌ Avoid when:
- Payments/sensitive actions जिन्हें real-time confirmation चाहिए

---

## 📊 Visual Diagram
```
 open app ─► [Cache] ─► UI (instant)
                 ▲          │
   fresh data ───┘          ├─ online?  ─► fetch ─► update cache + UI
                            └─ offline? ─► banner + queue actions
 NetInfo: offline→online ─► flush queue ─► server
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache | Saved copy | सहेजी हुई प्रति |
| TTL | Cache lifetime | Cache की उम्र |
| Queue | Pending actions list | लंबित actions की सूची |
| Idempotency key | Prevent duplicates | डुप्लिकेट रोकने की कुंजी |
| Sync | Align local & server | मिलान |

---

## ⚡ 3-Line Summary
English: Cache successful responses and show them first.
Queue offline actions and flush when NetInfo says online.
Use idempotency keys and TTLs.

Hindi: सफल responses cache करो और पहले वही दिखाओ।
Offline actions queue करो और online होने पर भेजो।
Idempotency key और TTL रखो।

---

## ➡️ Next Topic
**148. NetInfo + Offline Detection** — connectivity को सही तरह पहचानना।
