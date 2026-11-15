# 81. useEffect in React Native
# हिंदी में: React Native में useEffect
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK version:** examples target **Expo SDK 52 (React Native 0.76, React 18.3)** — check current docs — APIs change between SDKs. (Dev में React 18 StrictMode effects दो बार चल सकते हैं।)

---

## 🔵 Simple Definition (English)
`useEffect(fn, deps)` runs **side effects** after the component renders: API calls, subscriptions, timers, listeners. The function you **return** is the **cleanup**, which runs before the next effect and when the component unmounts. The **dependency array** controls when it re-runs.

## 🔵 सरल परिभाषा (Hindi)
`useEffect(fn, deps)` component render होने के **बाद** **side effects** चलाता है: API calls, subscriptions, timers, listeners। जो function आप **return** करते हो वह **cleanup** है, जो अगले effect से पहले और unmount पर चलता है। **Dependency array** तय करता है कि effect कब दोबारा चले।

---

## 🔴 Problem it Solves
```
❌ Render ke andar fetch/timer/listener: har render par chalega -> infinite loop, leaks
❌ Listener hata na bhoolo -> memory leak, crash ("state update on unmounted")
✅ useEffect: "render ke BAAD kaam karo, aur jaate waqt safai karo"
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ Render के अंदर fetch/timer/listener: हर render पर चलेगा -> infinite loop, leaks
❌ Listener हटाना भूले -> memory leak, crash
✅ useEffect: "render के बाद काम करो, और जाते समय सफ़ाई करो"
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Component renders and native views are committed
Step 2 → React runs effect (after paint/commit, async)
Step 3 → deps = []        -> run once after mount
         deps = [a, b]    -> run after mount + whenever a or b changes
         no deps          -> run after EVERY render
Step 4 → Before re-running, React calls previous cleanup
Step 5 → On unmount, cleanup runs one last time
Step 6 → RN specific: effects DON'T re-run on background/foreground
         or when you navigate away (stack screens stay mounted)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Component render होता है और native views commit होते हैं
Step 2 → React effect चलाता है (commit के बाद, async)
Step 3 → deps = []        -> mount के बाद एक बार
         deps = [a, b]    -> mount + जब भी a या b बदले
         बिना deps        -> हर render के बाद
Step 4 → दोबारा चलने से पहले पिछला cleanup चलता है
Step 5 → Unmount पर आख़िरी बार cleanup चलता है
Step 6 → RN में: background/foreground या दूसरी screen पर जाने पर effect दोबारा नहीं चलता
         (stack की screens mounted रहती हैं)
```

---

## 🟡 Real World Example
**Swiggy order tracking**: on mount start `setInterval` (poll rider location every 5s); cleanup clears the interval when the screen is gone. **Zomato search**: effect on `[query]` with debounce (300ms) then fetch results, cancelling the previous request in cleanup. **Paytm**: `AppState` listener to lock the app when it returns from background.

## 🟡 Real Example Hindi mein
**Swiggy order tracking**: mount पर `setInterval` (हर 5 सेकंड rider location poll); screen हटने पर cleanup interval साफ़ करता है। **Zomato search**: `[query]` पर effect, 300ms debounce, फिर fetch; cleanup में पिछला request cancel। **Paytm**: background से लौटने पर app lock करने के लिए `AppState` listener।

---

## 💻 Code Example — Basic
```jsx
// Basic: fetch on mount + timer with cleanup
import React, { useState, useEffect } from 'react';                // React hooks
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native'; // UI

export default function BasicEffect() {
  const [users, setUsers] = useState([]);                          // data state
  const [loading, setLoading] = useState(true);                    // loading flag
  const [seconds, setSeconds] = useState(0);                       // timer state

  // Effect 1: runs ONCE after first render (deps = [])
  useEffect(() => {
    let cancelled = false;                                         // flag for unmounted safety
    fetch('https://jsonplaceholder.typicode.com/users?_limit=3')   // sample API
      .then((r) => r.json())                                       // parse JSON
      .then((data) => { if (!cancelled) setUsers(data); })         // set only if still mounted
      .catch((e) => console.log('fetch error', e))                 // handle error
      .finally(() => { if (!cancelled) setLoading(false); });      // stop spinner
    return () => { cancelled = true; };                            // CLEANUP
  }, []);                                                          // empty deps

  // Effect 2: timer that ticks every second
  useEffect(() => {
    const id = setInterval(() => setSeconds((s) => s + 1), 1000);  // functional update (no stale s)
    return () => clearInterval(id);                                // CLEANUP: stop timer
  }, []);

  if (loading) return <ActivityIndicator style={{ marginTop: 50 }} />; // loading UI
  return (
    <View style={styles.c}>
      <Text>Timer: {seconds}s</Text>
      {users.map((u) => <Text key={u.id}>{u.name}</Text>)}
    </View>
  );
}
const styles = StyleSheet.create({ c: { padding: 20 } });
```

## 💻 Code Example — Advanced
```jsx
// Advanced: debounced search with AbortController + AppState refresh +
// useFocusEffect for "every time screen is focused"
import React, { useState, useEffect, useCallback, useRef } from 'react'; // hooks
import { View, TextInput, FlatList, Text, AppState, StyleSheet } from 'react-native'; // UI
import { useFocusEffect } from '@react-navigation/native';         // runs on screen focus

export default function SearchScreen() {
  const [query, setQuery] = useState('');                          // typed text
  const [results, setResults] = useState([]);                      // API results
  const [error, setError] = useState(null);                       // error message
  const appState = useRef(AppState.currentState);                  // keep last AppState

  // 1. Debounced search: wait 300ms after typing stops; cancel old request
  useEffect(() => {
    if (!query.trim()) { setResults([]); return undefined; }       // nothing to search
    const controller = new AbortController();                      // lets us cancel fetch
    const timer = setTimeout(async () => {                         // debounce
      try {
        setError(null);                                            // clear previous error
        const res = await fetch(
          `https://jsonplaceholder.typicode.com/posts?q=${encodeURIComponent(query)}&_limit=5`,
          { signal: controller.signal }                            // attach abort signal
        );
        if (!res.ok) throw new Error(`HTTP ${res.status}`);        // HTTP error
        setResults(await res.json());                              // save results
      } catch (e) {
        if (e.name !== 'AbortError') setError(e.message);          // ignore our own cancel
      }
    }, 300);
    return () => { clearTimeout(timer); controller.abort(); };     // CLEANUP both
  }, [query]);                                                     // re-run on query change

  // 2. Refresh when app comes back to foreground
  useEffect(() => {
    const sub = AppState.addEventListener('change', (next) => {
      if (appState.current.match(/inactive|background/) && next === 'active') {
        console.log('foreground -> refresh search');               // refresh logic here
      }
      appState.current = next;                                     // update ref (no re-render)
    });
    return () => sub.remove();                                     // CLEANUP
  }, []);

  // 3. Every time this screen becomes visible (not only on mount)
  useFocusEffect(
    useCallback(() => {
      console.log('Search screen focused');                        // analytics event
      return () => console.log('Search screen blurred');           // runs on blur
    }, [])
  );

  return (
    <View style={styles.c}>
      <TextInput value={query} onChangeText={setQuery} placeholder="Search dishes" style={styles.i} />
      {error && <Text style={{ color: 'red' }}>{error}</Text>}
      <FlatList data={results} keyExtractor={(i) => String(i.id)}
        renderItem={({ item }) => <Text style={{ paddingVertical: 6 }}>{item.title}</Text>} />
    </View>
  );
}
const styles = StyleSheet.create({
  c: { flex: 1, padding: 16 },
  i: { borderWidth: 1, borderColor: '#ccc', padding: 8, borderRadius: 6 },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Effect timing | After commit | After commit |
| Timers in background | Often throttled/stopped when app backgrounded | Suspended shortly after background |
| `AppState` values | `active`, `background` | also `inactive` |
| Hardware back effect | Needs `BackHandler` in effect | n/a |
| Location/notification listeners | Permission models differ | Same API, different prompts |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: many listeners are in expo packages, cleaned up the same way
import * as Notifications from 'expo-notifications';
useEffect(() => {
  const sub = Notifications.addNotificationReceivedListener((n) => console.log(n));
  return () => sub.remove();            // cleanup
}, []);
```
CLI way:
```jsx
// CLI: same effect pattern with community libs (e.g. NetInfo)
import NetInfo from '@react-native-community/netinfo';
useEffect(() => {
  const unsub = NetInfo.addEventListener((s) => console.log(s.isConnected));
  return unsub;                         // cleanup
}, []);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Infinite loop (set state in effect without proper deps)
```jsx
useEffect(() => { setData(fetchSomething()); });   // ❌ no deps -> runs every render
```
✅ Correct: add `[]` or the right dependencies.

❌ Mistake 2: `async` effect function
```jsx
useEffect(async () => { await load(); }, []);      // ❌ returns a Promise, not cleanup
```
✅ Correct: define `const run = async () => {...}; run();` inside.

❌ Mistake 3: No cleanup for timers/listeners
✅ Correct: `return () => clearInterval(id)` / `sub.remove()`.

❌ Mistake 4: Expecting `[]` effect to re-run when returning to a screen
✅ Correct: use `useFocusEffect` / `useIsFocused`.

❌ Mistake 5: Object/array/function in deps recreated each render (effect loops)
✅ Correct: memoise with `useMemo`/`useCallback` or use primitives.

---

## 🧠 Tricky Interview Question
**Q: In dev, your `useEffect(() => { console.log('mounted') }, [])` prints twice. A bug?**

**Answer:** No. In **development with `<React.StrictMode>`** (React 18+), React deliberately mounts, unmounts and re-mounts each component once to expose missing cleanups. It does not happen in production builds. If doubling breaks your logic (e.g. an analytics event or a subscription), your effect lacks proper cleanup/idempotency. Another classic: interval with `setCount(count+1)` and `[]` deps freezes at 1 due to a **stale closure** — fix with `setCount(c => c+1)`.

---

## ⚫ Interview Questions + Answers

**Q1: What does the dependency array do?**
A1: Tells React when to re-run: `[]` once, `[x]` when x changes, none every render.

**Q2: When does cleanup run?**
A2: Before the effect re-runs, and when the component unmounts.

**Q3: `useEffect` vs `useFocusEffect`?**
A3: `useEffect` follows mount/unmount; `useFocusEffect` follows screen focus/blur (React Navigation) — needed because stack screens stay mounted.

**Q4: How do you cancel a fetch in an effect?**
A4: `AbortController` + `controller.abort()` in cleanup, or an `ignore` flag.

**Q5: Why avoid fetching in effects at all?**
A5: Hand-written effects miss caching, retries, dedup, race conditions — libraries like React Query handle them.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Subscribing to external systems (AppState, Keyboard, NetInfo, sockets)
- Timers, one-time setup/teardown
- Syncing with a non-React API

❌ Avoid when:
- Computing derived values (do in render / `useMemo`)
- Responding to a user event (put it in the event handler)
- Resetting state on prop change (use `key`)

---

## 📊 Visual Diagram
```
mount ─► render ─► commit ─► EFFECT runs
                              │
 deps change ► render ► CLEANUP(prev) ► EFFECT runs again
                              │
 unmount ─────────────────► CLEANUP (final)

RN note: Home button -> app background -> NO cleanup (still mounted!)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Side effect | Work outside rendering | Render के बाहर का काम |
| Cleanup | Undo function returned by effect | Effect का undo function |
| Dependency array | Re-run triggers | दोबारा चलाने वाली values |
| Stale closure | Effect sees old values | Effect को पुरानी values दिखना |
| AbortController | Cancel fetch | Fetch cancel करना |
| StrictMode | Dev-only double-run check | Dev में double-run check |

---

## ⚡ 3-Line Summary
**English:**
1. `useEffect` runs side effects after render; return a cleanup function.
2. Dependencies decide when it re-runs; avoid async effect functions and stale closures.
3. In RN use `AppState` for background and `useFocusEffect` for screen focus.

**Hindi:**
1. `useEffect` render के बाद side effects चलाता है; cleanup function return करो।
2. Dependencies तय करती हैं कब दोबारा चले; async effect function और stale closure से बचो।
3. RN में background के लिए `AppState` और screen focus के लिए `useFocusEffect` use करो।

---

## ➡️ Next Topic
**82. useRef in React Native** — TextInput focus, timers, और बिना re-render के values।
