# 111. NetInfo — Network State
# हिंदी में: NetInfo — Network की स्थिति (WiFi / Cellular / Offline)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: Expo SDK 52 (React Native 0.76) + `@react-native-community/netinfo` (version `npx expo install` से SDK के अनुसार मिलता है — check current docs; APIs change between versions). Expo Go में bundled है।

---

## 🔵 Simple Definition (English)
**NetInfo** tells your app whether the device is **connected** to a network, what **type** it is (wifi, cellular, none…) and whether the **internet is actually reachable**. You can read it once (`fetch`), subscribe to changes, or use the `useNetInfo` hook.

## 🔵 सरल परिभाषा (Hindi)
**NetInfo** बताता है कि device network से **जुड़ा** है या नहीं, किस **प्रकार** का है (wifi, cellular, none…) और **internet सच में पहुँच** में है या नहीं। इसे एक बार पढ़ सकते हैं (`fetch`), बदलाव सुन सकते हैं, या `useNetInfo` hook इस्तेमाल कर सकते हैं।

---

## 🔴 Problem it Solves
```
❌ Offline hone par app spinner me atak jata hai
❌ Request fail hone ke baad pata chalta hai ki net nahi hai
❌ WiFi ya mobile data me alag behaviour (HD video vs SD) chahiye
✅ "No internet" banner, offline queue, auto-retry jab net aaye
```

## 🔴 यह क्यों बना? (Hindi)
```
Offline में app अनंत spinner में अटक जाता है।
Request fail होने के बाद ही पता चलता है कि net नहीं था।
WiFi और mobile data पर अलग व्यवहार (HD बनाम SD) चाहिए।
NetInfo पहले से बता देता है, ताकि "No internet" banner और offline queue बन सके।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → npx expo install @react-native-community/netinfo
Step 2 → NetInfo.fetch() -> { isConnected, isInternetReachable, type, details }
Step 3 → const unsub = NetInfo.addEventListener(state => ...) -> badlav par callback
Step 4 → Ya hook: const net = useNetInfo()
Step 5 → isConnected = network se juda; isInternetReachable = internet pahunch me (null = abhi pata nahi)
Step 6 → Offline -> banner + queue; online hote hi queue flush
Step 7 → unmount par unsub()
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → fetch() से अभी की स्थिति, addEventListener से लगातार बदलाव।
Step 2 → isConnected सिर्फ़ यह बताता है कि WiFi/Cellular से जुड़े हैं।
Step 3 → isInternetReachable असली internet पहुँच बताता है (null = जाँच जारी)।
Step 4 → Offline पर UI में संदेश और requests queue; online होते ही भेजें।
```

---

## 🟡 Real World Example
**WhatsApp:** shows "Connecting…" / "Waiting for network" and sends queued messages when online. **Swiggy / Zomato:** "No internet connection" screen with Retry. **YouTube / Hotstar:** "Download only on WiFi" setting uses `type === 'wifi'`. **Paytm:** shows "Poor connection" before payment.

## 🟡 Real Example Hindi mein
**WhatsApp:** "Connecting…" दिखाता है और online होते ही queue के messages भेजता है। **Swiggy / Zomato:** "No internet" screen और Retry बटन। **Hotstar:** "सिर्फ़ WiFi पर download" setting `type === 'wifi'` से। **Paytm:** payment से पहले "कमज़ोर connection" चेतावनी।

---

## 💻 Code Example — Basic
```jsx
// NetBasic.jsx — useNetInfo hook se live status
import React from 'react';                                             // React
import { View, Text } from 'react-native';                             // RN UI
import { useNetInfo } from '@react-native-community/netinfo';          // hook

export default function NetBasic() {
  const net = useNetInfo();                                            // live state (auto re-render)

  return (
    <View style={{ padding: 40, gap: 6 }}>
      <Text>Type: {net.type}</Text>
      <Text>Connected: {String(net.isConnected)}</Text>
      <Text>Internet reachable: {String(net.isInternetReachable)}</Text>
      {net.isConnected === false && <Text style={{ color: 'red' }}>Offline ❌</Text>}
    </View>
  );
}
```

## 💻 Code Example — Advanced
```jsx
// useOnline.js + offlineQueue.js — banner, retry queue, cleanup
import { useEffect, useRef, useState } from 'react';
import NetInfo from '@react-native-community/netinfo';

// Pure logic: state -> online hai ya nahi (null ko "abhi pata nahi" maano)
export function computeOnline(state) {
  if (!state) return null;                                             // koi state nahi
  if (state.isConnected === false) return false;                       // juda hi nahi
  if (state.isInternetReachable === false) return false;               // juda hai par net nahi
  if (state.isConnected && state.isInternetReachable === null) return null; // check chal raha hai
  return Boolean(state.isConnected);                                   // true
}

// Simple offline queue: online hote hi flush
export function createOfflineQueue(sender) {
  const items = [];                                                    // pending jobs
  return {
    add: (job) => items.push(job),                                     // queue me daalo
    size: () => items.length,
    async flush() {
      while (items.length) {                                           // ek-ek karke bhejo
        const job = items[0];
        try { await sender(job); items.shift(); }                      // success -> hatao
        catch (e) { break; }                                           // fail -> baad me retry
      }
    },
  };
}

export function useOnline(queue) {
  const [online, setOnline] = useState(null);                          // null = unknown
  const wasOffline = useRef(false);                                    // pichhla offline tha?

  useEffect(() => {
    const unsub = NetInfo.addEventListener((state) => {                // subscribe
      const now = computeOnline(state);
      setOnline(now);
      if (now === false) wasOffline.current = true;                    // offline note
      if (now === true && wasOffline.current) {                        // wapas online
        wasOffline.current = false;
        queue?.flush().catch(console.warn);                            // pending bhejo
      }
    });
    return () => unsub();                                              // cleanup (function return karta hai)
  }, [queue]);

  return online;
}

// One-time check (button handler me): const s = await NetInfo.fetch();
// Poora refresh force: await NetInfo.refresh();
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Permission | `ACCESS_NETWORK_STATE` (auto-added by library) | None |
| WiFi SSID/BSSID | Needs location permission (`ACCESS_FINE_LOCATION`) | Needs location + entitlement / Wi-Fi info capability |
| `isInternetReachable` | Pings a reachability URL (default `clients3.google.com/generate_204`) | Same approach |
| Cellular generation (`details.cellularGeneration`) | ✅ 2g/3g/4g/5g | ✅ |
| VPN type | `vpn` detected | `vpn` detected |
| Captive portal (hotel WiFi) | connected=true, reachable=false | Same |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install @react-native-community/netinfo   (SDK-compatible version)
import NetInfo from '@react-native-community/netinfo';                  // Expo Go me chalta hai
const state = await NetInfo.fetch();                                    // abhi ki state
```
CLI way:
```jsx
// npm i @react-native-community/netinfo && cd ios && pod install       (autolinking)
import NetInfo from '@react-native-community/netinfo';                  // same JS API
const unsub = NetInfo.addEventListener((s) => console.log(s.type));     // subscribe
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `isConnected` को "internet है" मान लेना।
✅ Correct: `isInternetReachable` भी जाँचें (WiFi जुड़ा पर internet नहीं हो सकता)।

❌ Mistake 2: `isInternetReachable === null` को offline समझना।
✅ Correct: `null` = अभी जाँच जारी; `false` ही offline है।

❌ Mistake 3: Listener unsubscribe न करना।
✅ Correct: `const unsub = NetInfo.addEventListener(...); return () => unsub()`।

❌ Mistake 4: सिर्फ़ NetInfo पर भरोसा करके requests न भेजना।
✅ Correct: Request try/catch भी रखें; NetInfo संकेत है, गारंटी नहीं।

❌ Mistake 5: Expo में package `npm i` से अलग version लगाना।
✅ Correct: `npx expo install`।

---

## 🧠 Tricky Interview Question
The phone is on hotel WiFi that needs a login page (captive portal). What are `isConnected` and `isInternetReachable`?

Answer: `isConnected: true` (it is attached to the WiFi) but `isInternetReachable: false` (the reachability ping fails because the portal intercepts traffic). That's why only checking `isConnected` shows "online" while every API fails. (While the first check is running `isInternetReachable` may be `null`.)

हिंदी: Captive portal में `isConnected` true पर `isInternetReachable` false आता है। इसलिए दोनों जाँचें।

---

## ⚫ Interview Questions + Answers
Q1: `isConnected` और `isInternetReachable` में फ़र्क?
A1: पहला network से जुड़ाव, दूसरा असली internet पहुँच (reachability check)।

Q2: `NetInfo.fetch` vs `addEventListener`?
A2: `fetch` एक बार की स्थिति देता है; `addEventListener` हर बदलाव पर callback देता है और unsubscribe function लौटाता है।

Q3: WiFi vs cellular कैसे पहचानें?
A3: `state.type === 'wifi'` / `'cellular'`; cellular पर `details.cellularGeneration` और `details.isConnectionExpensive`।

Q4: Offline-first app कैसे बनाएँ?
A4: Local cache (SQLite/MMKV), write को queue करें, online होते ही flush करें, React Query का `onlineManager` को NetInfo से जोड़ें।

Q5: Reachability URL बदल सकते हैं?
A5: हाँ, `NetInfo.configure({ reachabilityUrl: 'https://yourapi/ping', reachabilityTest: async (r) => r.status === 204 })`।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Offline banner, retry screen
- WiFi-only downloads / data saver
- Offline queue sync

❌ Avoid when:
- NetInfo को ही असली API-success की गारंटी मानना
- बहुत तेज़ polling के लिए (event listener पर्याप्त है)
- Web में बिना testing (browser APIs अलग)

---

## 📊 Visual Diagram
```
 Device network stack
        │
 NetInfo native listener (Android ConnectivityManager | iOS NWPathMonitor)
        │
   state: { type, isConnected, isInternetReachable, details }
        │
  ┌─────┴───────────────┐
  isConnected=false      isConnected=true
  → Offline banner         │
                     isInternetReachable?
                      true → normal | false → "No internet" | null → checking
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| isConnected | Attached to a network | network से जुड़ा |
| isInternetReachable | Internet actually works | internet सच में चल रहा |
| type | wifi / cellular / none... | network का प्रकार |
| Captive portal | Login page before internet | WiFi का login page |
| Offline-first | Works without internet | बिना internet भी चले |
| Reachability | Can we reach a server | server तक पहुँच |

---

## ⚡ 3-Line Summary
English: NetInfo gives connection type and whether the internet is reachable.
Use the hook or subscribe, and treat null reachability as unknown.
Combine it with an offline queue and still handle request errors.

Hindi: NetInfo connection का प्रकार और internet की पहुँच बताता है।
Hook या subscription इस्तेमाल करें, और null reachability को "पता नहीं" मानें।
Offline queue के साथ जोड़ें और request errors भी संभालें।

---

## ➡️ Next Topic
**112. Clipboard API** — text copy/paste (OTP, referral code, share link) करना।

---
