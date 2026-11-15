# 298. Build Custom Hook — useNetInfo
# हिंदी में: Custom Hook बनाओ — useNetInfo
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 52 / React Native 0.76** (check current docs — APIs change between SDKs). Uses `@react-native-community/netinfo` (Expo installs the SDK-matching version). The library also ships its own `useNetInfo()` hook; here we build our own to learn and to add `isOffline`.
> Files: [`useNetInfo.js`](./useNetInfo.js) · [`OfflineBanner.jsx`](./OfflineBanner.jsx) · [`NetInfoScreen.jsx`](./NetInfoScreen.jsx)
> Install: `npx expo install @react-native-community/netinfo`

---

## 🔵 Simple Definition (English)
`useNetInfo` is a custom hook that subscribes to network changes (wifi, cellular, none) and returns simple values like `isOffline`. Any screen can show an "No internet" banner or disable a button without knowing how NetInfo works.

## 🔵 सरल परिभाषा (Hindi)
`useNetInfo` एक custom hook है जो network बदलाव (wifi, cellular, none) को सुनता है और `isOffline` जैसे आसान values देता है। कोई भी screen NetInfo की जानकारी के बिना "No internet" banner दिखा सकती है या button disable कर सकती है।

---

## 🔴 Problem it Solves
```
❌ User offline है, फिर भी "Pay" दबाता है -> request fail -> confusing error
❌ हर screen में अलग NetInfo subscribe + unsubscribe code
❌ Subscribe करके unsubscribe भूल गए -> memory leak
❌ isInternetReachable शुरुआत में null होता है -> गलत "offline" flash
```

## 🔴 यह क्यों बना? (Hindi)
```
भारत में train, metro या lift में network अचानक चला जाता है। Paytm / PhonePe / IRCTC
को तुरंत बताना पड़ता है "No internet" ताकि user का payment अधूरा न रहे।
Hook एक बार सही तरीके से subscribe/cleanup करता है, बाकी screens सिर्फ result पढ़ती हैं।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → useState holds { isConnected, isInternetReachable, type } (start as online)
Step 2 → useEffect subscribes: NetInfo.addEventListener(callback)
Step 3 → NetInfo calls back immediately with the current state, then on every change
Step 4 → We normalise null values: isInternetReachable ?? isConnected ?? false
Step 5 → isOffline = isConnected === false || isInternetReachable === false
Step 6 → Cleanup: addEventListener returns unsubscribe -> return it from useEffect
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → useState में { isConnected, isInternetReachable, type } रखो (शुरू में online मानो)
Step 2 → useEffect में NetInfo.addEventListener(callback) से subscribe करो
Step 3 → NetInfo तुरंत current state भेजता है, फिर हर बदलाव पर
Step 4 → null values को ठीक करो: isInternetReachable ?? isConnected ?? false
Step 5 → isOffline = isConnected === false || isInternetReachable === false
Step 6 → Cleanup: addEventListener unsubscribe function लौटाता है, उसे return कर दो
```

---

## 🟡 Real World Example
**Paytm / PhonePe** show a red "No internet connection" bar and disable "Pay". **WhatsApp** shows "Connecting..." in the header. **Swiggy** shows "You're offline" on the menu and keeps the cart locally.

## 🟡 Real Example Hindi mein
**Paytm / PhonePe** लाल "No internet connection" bar दिखाते हैं और "Pay" button disable कर देते हैं। **WhatsApp** header में "Connecting..." दिखाता है। **Swiggy** offline होने पर "You're offline" दिखाता है और cart local रखता है।

---

## 💻 Code Example — Basic
Using the library's own hook (no custom code):

```jsx
// Basic: library hook, no custom hook needed
import React from 'react'; // React
import { Text, View } from 'react-native'; // UI
import { useNetInfo } from '@react-native-community/netinfo'; // built-in hook

export default function BasicNet() {
  const net = useNetInfo(); // { type, isConnected, isInternetReachable, ... }
  return (
    <View style={{ padding: 40 }}>
      {/* type: wifi | cellular | none | unknown */}
      <Text>Type: {net.type}</Text>
      {/* isConnected can be null until first check */}
      <Text>Connected: {String(net.isConnected)}</Text>
    </View>
  );
}
```

## 💻 Code Example — Advanced
Full code: [`useNetInfo.js`](./useNetInfo.js), [`OfflineBanner.jsx`](./OfflineBanner.jsx), [`NetInfoScreen.jsx`](./NetInfoScreen.jsx). Key part:

```js
// useNetInfo.js (key part)
const [state, setState] = useState({ isConnected: true, isInternetReachable: true, type: 'unknown' }); // assume online
useEffect(() => {
  const unsubscribe = NetInfo.addEventListener((s) => {      // fires now + on every change
    setState({
      isConnected: s.isConnected ?? false,                   // joined a network?
      isInternetReachable: s.isInternetReachable ?? s.isConnected ?? false, // null -> fall back
      type: s.type,                                          // 'wifi' | 'cellular' | 'none'
    });
  });
  return unsubscribe;                                        // cleanup on unmount
}, []);
const isOffline = state.isConnected === false || state.isInternetReachable === false;
```
```jsx
// NetInfoScreen.jsx (key part) - fresh check before the critical action
const pay = async () => {
  const s = await NetInfo.fetch();                           // one-time, up-to-date status
  if (!s.isConnected) { Alert.alert('Offline', 'Connect to the internet to pay'); return; }
  Alert.alert('Paying...', 'Request sent');                  // real code: call payment API
};
```

> Verified: rendered under jsdom (react-native-web, NetInfo mocked with a manual event emitter): online shows no banner; emitting offline shows "No internet connection (none)" and disables Pay; emitting online with `isInternetReachable: null` hides the banner; unmount removes the listener. Real airplane-mode/wifi switching on a device: not run.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Permission needed | `ACCESS_NETWORK_STATE` (added by the library) | None |
| Wifi SSID (`details.ssid`) | Needs location permission (Android 8.1+) | Needs location permission + Access WiFi Information entitlement |
| `isInternetReachable` check | Pings a reachability URL (default Google 204) | Same, via library |
| Cellular generation (`details.cellularGeneration`) | Available | Available on supported devices |
| Simulator/emulator | Toggle network in emulator controls | Network Link Conditioner / disable Mac wifi |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx expo install @react-native-community/netinfo   # SDK-matched version, no native setup
```
CLI way:
```bash
npm install @react-native-community/netinfo         # same package
cd ios && pod install && cd ..                      # link iOS pod (Android autolinks)
```
```js
// Same JS API in both. Optional: custom reachability URL if Google is blocked in your market
NetInfo.configure({ reachabilityUrl: 'https://clients3.google.com/generate_204', reachabilityTest: async (r) => r.status === 204 });
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Forgetting to unsubscribe (`return unsubscribe`).
✅ **Correct:** Return the function from `useEffect` so it runs on unmount.

❌ **Mistake 2:** Treating `isInternetReachable === null` as offline.
✅ **Correct:** `null` means unknown; only `false` means offline.

❌ **Mistake 3:** Trusting `isConnected` alone: wifi without internet still says connected.
✅ **Correct:** Also check `isInternetReachable`.

❌ **Mistake 4:** Using cached hook state for a payment decision.
✅ **Correct:** Call `NetInfo.fetch()` right before the critical action.

❌ **Mistake 5:** Putting the subscribe code in every screen.
✅ **Correct:** One hook (or one context provider if many screens need it, to avoid many listeners).

---

## 🧠 Tricky Interview Question
**Q:** Phone is on wifi, but the router has no internet. What do `isConnected` and `isInternetReachable` say, and does our `isOffline` show the banner?

**Answer:** `isConnected` is `true` (joined wifi) and `isInternetReachable` becomes `false` after NetInfo's reachability ping fails (it may be `null` for a moment first). `isOffline = isConnected === false || isInternetReachable === false` is therefore `true`, so the banner shows once reachability is known. During the brief `null` period we assume online - a trade-off to avoid false alarms.

---

## ⚫ Interview Questions + Answers

**Q1: `NetInfo.fetch()` vs `addEventListener` vs `useNetInfo`?**
A1: `fetch()` = one-time Promise. `addEventListener` = subscription for changes (returns unsubscribe). `useNetInfo()` = hook wrapper that re-renders on change.

**Q2: Why start with `isConnected: true`?**
A2: To avoid a flash of the offline banner at launch before the first event arrives. The first callback corrects the state immediately.

**Q3: How do you queue actions while offline?**
A3: Save them in AsyncStorage/SQLite and replay when `isOffline` flips to false (see topic 291, offline-first app).

**Q4: Many components use the hook. Is that many listeners?**
A4: Yes, one per component. For many consumers, subscribe once in a context provider and share the value.

**Q5: Can you detect slow network?**
A5: Partly: `type: 'cellular'` with `details.cellularGeneration` ('2g'/'3g'/'4g'). For real speed, measure request time yourself.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need an offline banner or disabled actions (payments, checkout)
- You want automatic refetch when connection returns

❌ Avoid when:
- You only need to handle failed requests (just catch fetch errors)
- You rely on it as the only check for a critical action (always verify with `fetch()` or the request itself)

---

## 📊 Visual Diagram
```
 OS network change (wifi off / airplane mode)
          │
          ▼
 NetInfo.addEventListener(cb) ──▶ useNetInfo state
          │                          │  isOffline = !connected || !reachable
          ▼                          ▼
   unsubscribe on unmount     <OfflineBanner/>  and  <Button disabled={isOffline}/>
 Before paying: NetInfo.fetch() → fresh check → proceed / Alert
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| NetInfo | Library that reports network state | Network स्थिति बताने वाली library |
| `isConnected` | Joined a network | किसी network से जुड़ा है |
| `isInternetReachable` | Internet really reachable | इंटरनेट सच में चल रहा है |
| Subscription | Listener for changes | बदलाव सुनने वाला listener |
| Cleanup | Removing the listener | Listener हटाना |
| Reachability | Ping test for real internet | असली internet की जाँच |

---

## ⚡ 3-Line Summary
**English:**
1. `useNetInfo` subscribes once, normalises null values and returns a simple `isOffline`.
2. Always unsubscribe in cleanup and treat `null` reachability as unknown, not offline.
3. For critical actions like payment, re-check with `NetInfo.fetch()` right before sending.

**Hindi:**
1. `useNetInfo` एक बार subscribe करता है, null values ठीक करता है और आसान `isOffline` देता है।
2. Cleanup में हमेशा unsubscribe करो और `null` reachability को unknown मानो, offline नहीं।
3. Payment जैसे ज़रूरी काम से ठीक पहले `NetInfo.fetch()` से दोबारा जाँचो।

---

## ➡️ Next Topic
**299. Build Custom Hook - useNotification** - अब push notification की permission, token और listeners को hook में लपेटना।
