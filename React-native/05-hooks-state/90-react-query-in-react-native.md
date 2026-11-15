# 90. React Query in React Native
# हिंदी में: React Native में React Query (TanStack Query)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: Expo SDK 52 (React Native 0.76) + @tanstack/react-query v5 (check current docs — APIs change between SDKs and between React Query majors).

---

## 🔵 Simple Definition (English)
**React Query (TanStack Query)** is a library that fetches, caches, retries and re-fetches *server data* for you. You write `useQuery({ queryKey, queryFn })` and get `data`, `isLoading`, `error` — no manual `useEffect + useState`. In React Native you also wire it to `AppState` (app focus) and `NetInfo` (online status).

## 🔵 सरल परिभाषा (Hindi)
**React Query** एक library है जो *server data* को fetch, cache, retry और दोबारा refresh करती है। आप `useQuery({ queryKey, queryFn })` लिखते हैं और `data`, `isLoading`, `error` मिल जाता है — `useEffect + useState` हाथ से लिखने की जरूरत नहीं। React Native में इसे `AppState` (app focus) और `NetInfo` (online/offline) से जोड़ना पड़ता है।

---

## 🔴 Problem it Solves
```
BEFORE (useEffect + useState):
❌ Har screen me loading/error/data state copy-paste
❌ Same API 3 baar call hoti hai (no caching)
❌ Back aane par purana data / blank screen
❌ Race conditions (old response new response ko overwrite)
❌ Retry, pagination, pull-to-refresh sab manual
❌ Redux me server data rakhna = bahut boilerplate

AFTER (React Query):
✅ Cache + dedupe (same key = ek hi request)
✅ Stale-while-revalidate: purana data turant, naya background me
✅ Auto retry with backoff
✅ Mutations + optimistic updates
✅ Offline support with persist
```

## 🔴 यह क्यों बना? (Hindi)
```
हर screen में loading/error/data state बार-बार लिखना थक देने वाला था।
Same API कई बार call होती थी, cache नहीं था।
Race conditions और stale data की दिक्कत थी।
React Query "server state" को "client state" (Zustand/Redux) से अलग संभालती है।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → App root par <QueryClientProvider client={queryClient}> lagao
Step 2 → Component me useQuery({ queryKey: ['orders'], queryFn })
Step 3 → Cache me 'orders' hai? 
           Haan + fresh (staleTime)  → seedha data do, network nahi
           Haan + stale              → data do + background refetch
           Nahi                      → isLoading = true, fetch karo
Step 4 → Fail hua? Default 3 retries (exponential backoff)
Step 5 → Success → cache update → sab subscribed components re-render
Step 6 → Component unmount → cache gcTime (default 5 min) tak rakhta hai
Step 7 → RN extras:
           focusManager  ← AppState ('active' = focus)
           onlineManager ← NetInfo (offline = pause, online = resume)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → App root पर QueryClientProvider लगाएँ।
Step 2 → useQuery में queryKey (cache का नाम) और queryFn (fetch function) दें।
Step 3 → Cache में data fresh है तो network call नहीं; stale है तो पुराना data दिखाकर background में नया लाता है।
Step 4 → Fail हो तो अपने आप 3 बार retry।
Step 5 → App background से वापस आए तो AppState से refetch trigger होता है।
Step 6 → Internet जाए तो NetInfo से queries pause, आए तो resume।
```

---

## 🟡 Real World Example
**Swiggy order list:** The "Your Orders" screen uses `useQuery(['orders'])`. When you open an order and press back, the list shows instantly from cache while a background refetch updates the status ("Out for delivery"). Pull-to-refresh calls `refetch()`. When you place a new order, a `useMutation` calls the API and then `invalidateQueries(['orders'])` so the list updates by itself. In a lift with no network, the cached list still shows and the query resumes when 4G returns.

## 🟡 Real Example Hindi mein
**Swiggy "Your Orders":** screen खुलते ही cache से list तुरंत दिखती है, पीछे नया data आता है। Pull-to-refresh = `refetch()`। नया order देने पर `useMutation` के बाद `invalidateQueries(['orders'])` से list अपने आप update। Network न हो तो भी पुरानी list दिखती है।

---

## 💻 Code Example — Basic
```jsx
// App.js — basic React Query setup + one query
import React from 'react';                                   // React core
import { View, Text, FlatList, ActivityIndicator } from 'react-native'; // RN UI
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'; // v5

const queryClient = new QueryClient();                        // ek shared cache object

// queryFn: plain async function jo data return kare ya error throw kare
async function fetchOrders() {
  const res = await fetch('https://jsonplaceholder.typicode.com/posts?_limit=5'); // API call
  if (!res.ok) throw new Error('Server error ' + res.status); // fetch khud 404/500 pe throw nahi karta
  return res.json();                                          // parsed JSON
}

function Orders() {
  // v5 me sirf object syntax chalta hai
  const { data, isPending, isError, error, refetch, isRefetching } = useQuery({
    queryKey: ['orders'],        // cache ki key
    queryFn: fetchOrders,        // data laane wala function
  });

  if (isPending) return <ActivityIndicator style={{ marginTop: 50 }} />; // pehli baar loading
  if (isError) return <Text>Error: {error.message}</Text>;    // error UI

  return (
    <FlatList
      data={data}                                             // cached data
      keyExtractor={(item) => String(item.id)}                // unique key
      refreshing={isRefetching}                               // pull-to-refresh spinner
      onRefresh={refetch}                                     // pull karne par refetch
      renderItem={({ item }) => <Text style={{ padding: 12 }}>{item.title}</Text>} // ek row
    />
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>                {/* cache sab children ko do */}
      <View style={{ flex: 1, paddingTop: 60 }}>
        <Orders />
      </View>
    </QueryClientProvider>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// queryClient.js — production setup: focus + online + mutation + optimistic update
import { AppState, Platform } from 'react-native';            // app foreground detect
import NetInfo from '@react-native-community/netinfo';        // internet status (Expo: npx expo install)
import { QueryClient, focusManager, onlineManager, useMutation, useQueryClient } from '@tanstack/react-query';

// 1) Online status: NetInfo -> React Query
onlineManager.setEventListener((setOnline) => {
  return NetInfo.addEventListener((state) => {                // listener return = unsubscribe
    setOnline(!!state.isConnected);                           // true = queries resume
  });
});

// 2) Focus: web me window focus hota hai, RN me AppState
export function onAppStateChange(status) {
  if (Platform.OS !== 'web') {
    focusManager.setFocused(status === 'active');             // 'active' = foreground
  }
}
// App root me: useEffect(() => { const s = AppState.addEventListener('change', onAppStateChange); return () => s.remove(); }, []);

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,                                   // 1 min tak fresh
      gcTime: 10 * 60 * 1000,                                 // v5: cacheTime ka naya naam
      retry: 2,                                               // 2 retries
    },
  },
});

// 3) Mutation + optimistic update
export function useToggleFavorite() {
  const qc = useQueryClient();                                // cache handle
  return useMutation({
    mutationFn: (id) => fetch(`https://api.example.com/fav/${id}`, { method: 'POST' }).then((r) => {
      if (!r.ok) throw new Error('Failed');                   // error ko throw karo
      return r.json();
    }),
    onMutate: async (id) => {
      await qc.cancelQueries({ queryKey: ['restaurants'] });  // in-flight fetch roko
      const previous = qc.getQueryData(['restaurants']);      // rollback ke liye snapshot
      qc.setQueryData(['restaurants'], (old = []) =>          // UI turant update
        old.map((r) => (r.id === id ? { ...r, fav: !r.fav } : r)));
      return { previous };                                    // context
    },
    onError: (_err, _id, ctx) => qc.setQueryData(['restaurants'], ctx.previous), // fail -> rollback
    onSettled: () => qc.invalidateQueries({ queryKey: ['restaurants'] }),        // end me server se sync
  });
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| React Query itself | Pure JS, same | Pure JS, same |
| AppState values | `active`, `background` (also `inactive` rare) | `active`, `inactive` (call/notification shade), `background` |
| Focus refetch | Fires on returning from background | Fires too; `inactive` ko ignore karna sahi hai |
| NetInfo | Needs `ACCESS_NETWORK_STATE` (auto in lib) | Works out of the box |
| Offline persist storage | AsyncStorage / MMKV | AsyncStorage / MMKV |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Install with SDK-compatible versions
// npx expo install @tanstack/react-query @react-native-community/netinfo
// NetInfo Expo Go me bhi chalta hai (included). No native setup.
import NetInfo from '@react-native-community/netinfo';
```
CLI way:
```jsx
// npm i @tanstack/react-query @react-native-community/netinfo
// cd ios && pod install   (iOS ke liye native pods)
// Android: autolinking karta hai, rebuild: npx react-native run-android
import NetInfo from '@react-native-community/netinfo';
```
React Query khud pure JS hai — sirf NetInfo (native module) me fark hai.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `useQuery('orders', fetchOrders)` (v4 syntax) v5 me.
✅ Correct: `useQuery({ queryKey: ['orders'], queryFn: fetchOrders })`.

❌ Mistake 2: `fetch` ke `res.ok` ko check na karna — 404 par bhi query "success" ho jaati hai.
✅ Correct: `if (!res.ok) throw new Error(...)` (axios ye khud karta hai).

❌ Mistake 3: Variable ko queryKey me na daalna: `queryKey: ['order']` jab `id` badalta hai.
✅ Correct: `queryKey: ['order', id]` — key = dependency array.

❌ Mistake 4: `isLoading` se pehli loading dikhana v5 me confuse karta hai (`isLoading = isFetching && isPending`).
✅ Correct: pehli load ke liye `isPending`; disabled query ke case me dhyan rakho.

❌ Mistake 5: AppState/NetInfo setup bhool jana — app background se aane par data refresh nahi hota.
✅ Correct: `focusManager` + `onlineManager` setup karo.

---

## 🧠 Tricky Interview Question
```jsx
const { data } = useQuery({ queryKey: ['user', id], queryFn: () => getUser(id), staleTime: Infinity });
// id 1 se 2 hua, phir wapas 1. Kitni network calls?
```
Answer: **2** (ek id=1 ke liye, ek id=2 ke liye). Key alag = alag cache entry. Wapas 1 par `staleTime: Infinity` ki wajah se cache fresh hai, to **koi nayi call nahi** (jab tak gcTime me entry zinda hai). Agar staleTime 0 hota to cached data dikhata aur background refetch hota.

---

## ⚫ Interview Questions + Answers
Q1: Server state vs client state?
A1: Server state = remote, async, doosron se change ho sakta hai (orders, products) → React Query. Client state = UI-only (theme, modal open) → useState/Zustand.

Q2: `staleTime` vs `gcTime`?
A2: staleTime = data kitni der "fresh" maana jaye (us dauran refetch nahi). gcTime = unused (no observer) data kitni der memory me rahe (default 5 min). v4 me gcTime = `cacheTime`.

Q3: RN me window focus nahi hota, refetch-on-focus kaise?
A3: `AppState` listener me `focusManager.setFocused(status === 'active')`. Screen-focus ke liye `useFocusEffect` + `refetch`, ya `subscribed` option.

Q4: Optimistic update kaise?
A4: `onMutate` me `cancelQueries`, snapshot lo, `setQueryData` se UI badlo; `onError` me rollback; `onSettled` me `invalidateQueries`.

Q5: Offline app kaise banayein?
A5: `PersistQueryClientProvider` + `createAsyncStoragePersister` (`@tanstack/query-async-storage-persister`, `@tanstack/react-query-persist-client`), `onlineManager` with NetInfo, aur `networkMode` set karo.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- API se list/detail data fetch karna, caching/refetch chahiye
- Pagination / infinite scroll (`useInfiniteQuery`)
- Mutations ke baad list auto-refresh

❌ Avoid when:
- Sirf local UI state (theme, form step) — useState/Zustand
- Real-time streaming (WebSocket) — alag handling
- Bahut simple one-time fetch jahan cache ki zarurat nahi

---

## 📊 Visual Diagram
```
 Component A ──┐                      ┌── fresh? ──► return cache
 Component B ──┼─► useQuery(['orders'])┤
 Component C ──┘        │              └── stale? ──► return cache + refetch
                        ▼
                 ┌─────────────┐   fetch   ┌──────────┐
                 │ Query Cache │◄─────────►│  Server  │
                 └─────────────┘           └──────────┘
                        ▲
       AppState(active) │ NetInfo(online)  → refetch / resume
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| queryKey | Cache identity array | Cache की पहचान |
| queryFn | Async fetch function | Data लाने वाला function |
| staleTime | Time data stays fresh | Data कब तक ताज़ा |
| gcTime | Unused cache lifetime | Cache कब तक memory में |
| invalidateQueries | Mark stale and refetch | Cache पुराना घोषित करना |
| mutation | Write operation (POST/PUT) | Server पर बदलाव |
| focusManager | App-focus tracker | App focus ट्रैकर |

---

## ⚡ 3-Line Summary
English: React Query manages server state — caching, retries, refetching — with `useQuery` and `useMutation`.
In React Native, connect `focusManager` to `AppState` and `onlineManager` to NetInfo.
Keep `queryKey` = dependencies; v5 uses object syntax and `gcTime`/`isPending`.

Hindi: React Query server data का cache, retry और refetch संभालती है।
React Native में `focusManager` को AppState से और `onlineManager` को NetInfo से जोड़ें।
`queryKey` में सारे dependencies रखें; v5 में object syntax, `gcTime`, `isPending` चलते हैं।

---

## ➡️ Next Topic
**91. Camera — expo-camera** — अब से device features: server data के बाद phone का hardware (camera) इस्तेमाल करना सीखेंगे।

---
