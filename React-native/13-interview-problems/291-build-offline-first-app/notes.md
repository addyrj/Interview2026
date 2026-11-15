# 291. Interview Problem: Build an Offline-First App
# हिंदी में: Offline-First App बनाओ
# Platform: Both ✅ (Android ✅ | iOS ✅)
# Difficulty: ⭐⭐⭐⭐ Hard | Asked at: Swiggy, Zomato, Paytm, Dunzo, Urban Company

Files: `TodoScreen.jsx`, `syncQueue.js` (pure logic, storage injected).
Target: Expo SDK 52 with AsyncStorage + NetInfo (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
An offline-first app reads and writes local storage first, so it works without internet. Changes made offline are saved in a queue and sent to the server when the network comes back.

## 🔵 सरल परिभाषा (Hindi)
Offline-first app पहले local storage से पढ़ता-लिखता है, इसलिए बिना internet भी चलता है। Offline किए गए बदलाव एक queue में सेव होते हैं और network वापस आते ही server को भेज दिए जाते हैं।

---

## 🔴 Problem it Solves
Indian users often have weak or no network (metro, lifts, villages). An app that shows spinners or errors without internet loses users. Offline-first gives instant UI and no data loss.

## 🔴 यह क्यों बना? (Hindi)
भारत में network अक्सर कमज़ोर या गायब होता है (metro, lift, गाँव)। बिना internet spinner या error दिखाने वाले app से users चले जाते हैं। Offline-first से UI तुरंत चलता है और data खोता नहीं।

---

## 🔴 Problem Statement
Build a todo list that: shows cached todos instantly on launch; lets the user add todos offline (optimistic UI); stores unsent actions in a persistent queue; shows an "Offline" banner with pending count; flushes the queue in order when internet returns; keeps failed items for retry.

## 💡 Approach
```
Local cache  : AsyncStorage 'todos_cache'   (what the UI shows)
Queue        : AsyncStorage 'pending_actions' [{ type, payload, id }]  (what the server has not seen)
NetInfo      : addEventListener -> isOnline -> flush()
Optimistic   : update state + cache first, enqueue second
syncQueue.js : createSyncQueue(storage, sendToServer)  -> read / enqueue / flush
```

## 🟢 How it Works — Step by Step
```
Step 1 → Launch: read 'todos_cache' and show it immediately (no spinner)
Step 2 → User adds a todo -> state + cache updated at once (optimistic)
Step 3 → The action is pushed to the queue (survives app kill)
Step 4 → NetInfo says offline -> banner "Offline - changes will sync later (N pending)"
Step 5 → Network returns -> flush(): send actions one by one in order
Step 6 → Failed ones stay in the queue, successful ones are removed, pending count updates
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Launch पर 'todos_cache' पढ़कर तुरंत दिखाओ (spinner नहीं)
Step 2 → User todo जोड़े -> state + cache तुरंत update (optimistic)
Step 3 → Action queue में जाता है (app kill होने पर भी बचा रहता है)
Step 4 → NetInfo offline बताए -> banner "Offline - बदलाव बाद में sync होंगे (N pending)"
Step 5 → Network आते ही flush(): actions को order में एक-एक करके भेजो
Step 6 → Fail हुए queue में रहते हैं, सफल हट जाते हैं, pending count अपडेट
```

---

## 🟡 Real World Example
WhatsApp queues messages (single tick) until you are online; Google Docs / Notion offline editing; Swiggy / Zomato keep your cart and last restaurants cached; Paytm shows the last balance when offline.

## 🟡 Real Example Hindi mein
WhatsApp offline में messages queue करता है (एक tick) और online होने पर भेजता है; Google Docs / Notion का offline editing; Swiggy / Zomato आपका cart और पुराने restaurants cache रखते हैं; Paytm offline में पिछला balance दिखाता है।

---

## 💻 Code Example — Basic
The queue logic (`syncQueue.js`), testable without a device because storage is injected:
```js
const KEY = 'pending_actions';                                   // storage key

export function createSyncQueue(storage, sendToServer) {
  const read = async () => JSON.parse((await storage.getItem(KEY)) || '[]'); // read queue
  const write = (q) => storage.setItem(KEY, JSON.stringify(q));            // write queue
  return {
    read,
    async enqueue(action) {                                      // add while offline
      const q = await read();
      q.push({ ...action, id: action.id || String(Date.now()) + Math.random() });
      await write(q);                                            // persist
    },
    async flush() {                                              // when internet returns
      const q = await read();
      const remaining = [];
      for (const action of q) {                                  // keep ORDER
        try { await sendToServer(action); }                      // server must be idempotent via id
        catch (e) { remaining.push(action); }                    // keep for next time
      }
      await write(remaining);
      return { sent: q.length - remaining.length, failed: remaining.length };
    },
  };
}
```

## 💻 Code Example — Advanced
From `TodoScreen.jsx`:
```jsx
// 1) Show cached data instantly
useEffect(() => {
  AsyncStorage.getItem(CACHE_KEY).then((v) => v && setTodos(JSON.parse(v)));
  queue.read().then((q) => setPending(q.length));
}, [queue]);

// 2) Flush when internet comes back
useEffect(() => {
  const unsub = NetInfo.addEventListener(async (s) => {
    const isOnline = !!s.isConnected && s.isInternetReachable !== false;  // null = unknown -> ok
    setOnline(isOnline);
    if (isOnline) { await queue.flush(); setPending((await queue.read()).length); }
  });
  return unsub;                                                  // cleanup
}, [queue]);

// 3) Optimistic add
const addTodo = useCallback(async () => {
  const item = { id: String(Date.now()), title: text.trim() };
  const next = [item, ...todos];
  setTodos(next); setText('');                                   // UI first
  await AsyncStorage.setItem(CACHE_KEY, JSON.stringify(next));   // local copy
  await queue.enqueue({ type: 'ADD_TODO', payload: item, id: item.id });
  setPending((await queue.read()).length);
}, [text, todos, queue]);
```
Known limits of this sample (say them in the interview): a second concurrent `flush()` can double-send (add a mutex), no conflict resolution (last-write-wins / versions needed), no max retry / backoff, `Date.now()` ids can clash in rare cases (use UUID). For bigger data use SQLite (`expo-sqlite`), WatermelonDB or MMKV; for server state use TanStack Query with `persistQueryClient`.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| NetInfo permission | Needs `ACCESS_NETWORK_STATE` (library adds it) | None |
| Background sync | WorkManager / headless tasks possible | Very limited (Background Fetch, system decides) |
| AsyncStorage limit | ~6 MB default quota on Android (configurable) | No hard small limit |
| Captive Wi-Fi | `isInternetReachable` helps detect it | Same |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install @react-native-async-storage/async-storage @react-native-community/netinfo
// Works in Expo Go; background sync -> expo-background-task / expo-task-manager (dev build)
```
CLI way:
```jsx
// npm i @react-native-async-storage/async-storage @react-native-community/netinfo
// cd ios && pod install ; rebuild
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Trusting `isConnected` alone (connected to Wi-Fi without internet).
✅ Correct: Also check `isInternetReachable !== false`.

❌ Mistake 2: Waiting for the server before updating the UI.
✅ Correct: Optimistic update + queue.

❌ Mistake 3: Keeping the queue only in memory.
✅ Correct: Persist it so it survives app kill.

❌ Mistake 4: Non-idempotent server endpoints with retries -> duplicates.
✅ Correct: Send the action `id`; server ignores repeats.

---

## 🧠 Tricky Interview Question
Two todos are queued, #1 fails permanently on the server (validation error). What does this `flush` do, and is it a problem?

Answer: It keeps #1 in `remaining` and keeps sending #2, so #1 is retried forever and the order is no longer strictly preserved. For permanent errors (4xx) you should drop or mark the action as "dead" and show the user; for transient errors (network / 5xx) retry with backoff. If order matters strictly, stop at the first failure.

---

## ⚫ Interview Questions + Answers
Q1: Offline-first vs offline-support?
A1: Offline-first reads/writes local first and syncs later; offline-support just caches for reading.

Q2: How to resolve conflicts?
A2: Last-write-wins with timestamps, version numbers, or CRDTs for collaborative data.

Q3: Why inject `storage` into `createSyncQueue`?
A3: Easy unit tests with a fake in-memory storage, no device needed.

Q4: How to avoid duplicate sends?
A4: Stable action `id` + idempotent endpoint + a lock around `flush`.

Q5: AsyncStorage vs SQLite vs MMKV?
A5: AsyncStorage = simple key-value, async; MMKV = very fast sync key-value; SQLite = relational queries / large data.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Users are on poor networks; actions are user-generated (notes, orders drafts, forms)

❌ Avoid when:
- Strong server-side consistency is required instantly (payments, seat booking) - show clear online-only state

---

## 📊 Visual Diagram
```
 UI ◄──────── local cache (AsyncStorage)
  │ add todo
  ▼
 optimistic update ─► enqueue(action) ─► [queue on disk]
                                              │  NetInfo: online
                                              ▼
                                  flush(): send 1 ─► send 2 ─► ...
                                     ok ─► removed    fail ─► stays
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Optimistic update | UI changes before server confirms | पहले UI, बाद में server |
| Sync queue | Pending actions list | Sync की कतार |
| Idempotent | Same request twice = same result | बार-बार भेजने पर भी एक जैसा |
| NetInfo | Network status library | Network जानकारी |
| Cache | Local saved copy | स्थानीय प्रति |

---

## ⚡ 3-Line Summary
English: Read and write local storage first; show data instantly.
Queue changes on disk and flush them in order when NetInfo says online.
Use idempotent ids, retries and clear conflict rules.

Hindi: पहले local storage से पढ़ें-लिखें; data तुरंत दिखाएँ।
बदलाव disk पर queue में रखें और NetInfo के online बताने पर order में भेजें।
Idempotent id, retry और conflict के नियम तय रखें।

---

## ✅ What was verified
Under react-native-web + jsdom with in-memory mocks for AsyncStorage and NetInfo: offline banner appears, adding a todo shows it immediately with "1 pending", going online flushes and hides the banner. `syncQueue.js` was run in isolation: a failing action stays in the queue and succeeds on retry. Real storage, real network and background sync were not run.

---

## ➡️ Next Topic
292. Build Push Notification Handler — permissions, tokens and tap handling.
