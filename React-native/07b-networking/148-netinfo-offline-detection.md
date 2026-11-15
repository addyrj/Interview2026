# 148. NetInfo + Offline Detection
# हिंदी में: NetInfo + Offline Detection — Internet है या नहीं, कैसे पता करें
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 52 target (check current docs — APIs change between SDKs).** `@react-native-community/netinfo` 11.x (`npx expo install @react-native-community/netinfo`)। Native module है; Expo Go में शामिल।

---

## 🔵 Simple Definition (English)
**NetInfo** is a library that tells your app the device's network state: connected or not, the connection type (wifi, cellular), and whether the internet is actually reachable. You can read it once or subscribe to changes.

## 🔵 सरल परिभाषा (Hindi)
**NetInfo** एक library है जो app को बताती है कि device का network कैसा है: connected है या नहीं, connection type (wifi, cellular), और internet असल में पहुँच में है या नहीं। इसे एक बार पढ़ सकते हैं या changes के लिए subscribe कर सकते हैं।

---

## 🔴 Problem it Solves
```
Device wifi से जुड़ा है पर router में internet नहीं — app को कैसे पता?
बिना NetInfo: request भेजकर timeout का इंतज़ार (10-30 sec)।
NetInfo: तुरंत "offline" banner, requests रोकना, auto retry।
```

## 🔴 यह क्यों बना? (Hindi)
```
RN core में network status का भरोसेमंद API नहीं है।
NetInfo दोनों platforms के native APIs को एक जैसा interface देता है।
Offline banner और auto-sync इसी पर बनते हैं।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → NetInfo.addEventListener(cb) — native network callbacks सुनता है
Step 2 → State object: { type, isConnected, isInternetReachable, details }
Step 3 → isConnected = device किसी network से जुड़ा है
Step 4 → isInternetReachable = असल internet तक पहुँच (NetInfo खुद एक reachability URL ping करता है);
          शुरू में null (अज्ञात) हो सकता है
Step 5 → बदलाव पर callback → UI/ queue update
Step 6 → unmount पर unsubscribe
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. addEventListener से network बदलाव सुनो।
2. isConnected = network से जुड़ा; isInternetReachable = internet सच में चल रहा।
3. शुरू में isInternetReachable null हो सकता है।
4. Component हटे तो unsubscribe करो।
```

---

## 🟡 Real World Example
**YouTube/Hotstar:** Wifi → mobile data बदलने पर "Playing on mobile data" warning। **Zomato:** Offline होते ही ऊपर लाल "No Internet" banner, वापस आते ही हरा "Back online"। **Paytm:** Connectivity जाने पर payment button disable।

## 🟡 Real Example Hindi mein
**Hotstar** wifi से mobile data पर जाते समय user को बताता है। **Zomato** में internet जाते ही ऊपर लाल banner आता है और लौटते ही गायब — यह NetInfo के listener से बनता है।

---

## 💻 Code Example — Basic

```jsx
// NetInfoBasic.jsx — live connectivity banner
import React, { useEffect, useState } from 'react';               // hooks
import { View, Text } from 'react-native';                        // UI
import NetInfo from '@react-native-community/netinfo';            // library

export default function NetInfoBasic() {
  const [online, setOnline] = useState(true);                     // मान लो online
  const [type, setType] = useState('unknown');                    // wifi/cellular/...

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener((state) => {     // change listener
      // isInternetReachable null का मतलब "अभी पता नहीं" — उसे offline मत मानो
      const isOnline = state.isConnected === true && state.isInternetReachable !== false;
      setOnline(isOnline);                                        // UI flag
      setType(state.type);                                        // type
    });
    return unsubscribe;                                           // cleanup
  }, []);

  return (
    <View style={{ flex: 1 }}>
      {!online && (
        <Text style={{ backgroundColor: '#dc2626', color: '#fff', padding: 8, textAlign: 'center' }}>
          No Internet
        </Text>
      )}
      <Text style={{ padding: 16 }}>Connection: {type}</Text>
    </View>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// useNetworkStatus.js — hook with debounce + onReconnect callback
import { useEffect, useRef, useState } from 'react';              // hooks
import NetInfo from '@react-native-community/netinfo';            // netinfo

export function useNetworkStatus({ onReconnect, debounceMs = 800 } = {}) {
  const [status, setStatus] = useState({ online: true, type: 'unknown', expensive: false });
  const wasOnline = useRef(true);                                 // पिछली स्थिति
  const timer = useRef(null);                                     // debounce timer
  const reconnectRef = useRef(onReconnect);                       // latest callback
  reconnectRef.current = onReconnect;                             // हर render में update

  useEffect(() => {
    const unsub = NetInfo.addEventListener((s) => {
      clearTimeout(timer.current);                                // flapping रोकने को
      timer.current = setTimeout(() => {                          // settle होने दो
        const online = s.isConnected === true && s.isInternetReachable !== false;
        setStatus({
          online,                                                 // final flag
          type: s.type,                                           // wifi/cellular/none
          expensive: s.details?.isConnectionExpensive === true,   // metered data? (Android में मिलता है)
        });
        if (online && !wasOnline.current) reconnectRef.current?.(); // offline→online पर callback
        wasOnline.current = online;                               // update
      }, debounceMs);
    });
    return () => { clearTimeout(timer.current); unsub(); };       // cleanup
  }, [debounceMs]);

  return status;
}
// एक बार fresh check: const s = await NetInfo.fetch();
// Reachability URL बदलना: NetInfo.configure({ reachabilityUrl: 'https://yourapi.com/health',
//   reachabilityTest: async (r) => r.status === 200, reachabilityLongTimeout: 60000 });
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Needs permission | `ACCESS_NETWORK_STATE` (library manifest में जोड़ती है) | कोई नहीं |
| Wifi SSID/BSSID | Location permission चाहिए | Location + entitlement चाहिए |
| `isConnectionExpensive` | Supported | Supported (Low Data Mode संबंधित) |
| Cellular generation (4g/5g) | Available | Available (सीमित) |
| Reachability check | NetInfo खुद ping करता है | NetInfo खुद ping करता है |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// npx expo install @react-native-community/netinfo
// import NetInfo from '@react-native-community/netinfo';
// (Expo में expo-network भी है: Network.getNetworkStateAsync() — अलग API)
```
CLI way:
```jsx
// npm i @react-native-community/netinfo
// cd ios && pod install
// Android autolink; rebuild जरूरी
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `isConnected` को "internet है" मानना।
✅ Correct: `isInternetReachable` भी देखो।

❌ Mistake 2: `isInternetReachable === null` को offline मानना।
✅ Correct: `!== false` से check।

❌ Mistake 3: Listener unsubscribe न करना।
✅ Correct: `useEffect` से return।

❌ Mistake 4: Offline देखकर request ही न भेजना।
✅ Correct: Banner दिखाओ पर कोशिश भी करने दो (NetInfo कभी-कभी गलत हो सकता है)।

---

## 🧠 Tricky Interview Question
Phone wifi से जुड़ा है पर router में internet नहीं है। `isConnected` और `isInternetReachable` क्या देंगे?

Answer: `isConnected: true` (wifi से जुड़ा है) पर `isInternetReachable: false` (reachability test fail)। इसलिए सिर्फ़ `isConnected` से offline detection गलत होगी। शुरुआत में `isInternetReachable` `null` भी हो सकता है।

---

## ⚫ Interview Questions + Answers
Q1: NetInfo.fetch और addEventListener?
A1: `fetch` एक बार current state; `addEventListener` हर बदलाव पर callback।

Q2: `useNetInfo` hook?
A2: Library `useNetInfo()` hook देती है जो state लौटाता है — सरल UI के लिए।

Q3: Reachability कैसे जाँचता है?
A3: Configured URL (default Google का generate_204) पर request; `configure` से अपना health endpoint दें।

Q4: Expo में `expo-network` से फर्क?
A4: `expo-network` सरल, कम events; NetInfo ज़्यादा features और listener।

Q5: Offline पर क्या करना चाहिए?
A5: Banner, cached data, actions queue, retry on reconnect।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Offline banner, auto-sync, data-saver features

❌ Avoid when:
- सिर्फ error handling चाहिए (request fail से भी पता चल जाता है)
- NetInfo पर ही निर्भर होकर requests रोकना

---

## 📊 Visual Diagram
```
 Native OS network events
         │
         ▼
   NetInfo listener ──► { type, isConnected, isInternetReachable }
         │
   reachability ping ──► isInternetReachable true/false/null
         │
         ▼
   UI banner / queue flush / retry
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| isConnected | Linked to a network | Network से जुड़ा |
| isInternetReachable | Internet actually works | Internet चल रहा |
| type | wifi/cellular/none | कनेक्शन का प्रकार |
| Reachability | Ping test | पहुँच की जाँच |
| Metered | Costly data | सीमित/महँगा data |

---

## ⚡ 3-Line Summary
English: NetInfo reports connection type and reachability and notifies on changes.
Check `isConnected` and `isInternetReachable !== false`.
Always unsubscribe the listener.

Hindi: NetInfo connection type और reachability बताता है और बदलाव पर सूचित करता है।
`isConnected` और `isInternetReachable !== false` दोनों जाँचो।
Listener हमेशा unsubscribe करो।

---

## ➡️ Next Topic
**149. Background Fetch** — app बंद/background में भी periodic data sync।
