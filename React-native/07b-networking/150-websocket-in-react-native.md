# 150. WebSocket in React Native
# हिंदी में: React Native में WebSocket — Real-time दो-तरफ़ा connection
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 52 target (check current docs — APIs change between SDKs).** React Native 0.76। `WebSocket` global में built-in है (browser जैसा API: `onopen`, `onmessage`, `onerror`, `onclose`, `send`, `close`)।

---

## 🔵 Simple Definition (English)
A **WebSocket** keeps one connection open between the app and server so both can send messages any time. It is used for real-time features like chat, live prices, and order tracking, without repeated polling.

## 🔵 सरल परिभाषा (Hindi)
**WebSocket** में app और server के बीच एक connection खुला रहता है, जिससे दोनों कभी भी message भेज सकते हैं। Chat, live prices, order tracking जैसी real-time चीज़ों के लिए, बिना बार-बार poll किए।

---

## 🔴 Problem it Solves
```
HTTP: client पूछे → server जवाब दे। Server खुद नहीं भेज सकता।
Polling (हर 2 sec पूछना): data/battery बर्बाद, देरी।

WebSocket: एक बार connect, फिर server जब चाहे push कर सकता है।
```

## 🔴 यह क्यों बना? (Hindi)
```
HTTP में server पहल नहीं कर सकता।
Polling महँगा और धीमा है।
WebSocket से तुरंत, दो-तरफ़ा, कम overhead वाला संचार।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → new WebSocket('wss://...')  (HTTP Upgrade handshake)
Step 2 → onopen → connection तैयार (readyState 1)
Step 3 → ws.send(JSON.stringify(msg)) — भेजना
Step 4 → onmessage → server का message (e.data string)
Step 5 → onclose / onerror → टूटना; reconnect खुद करना पड़ता है
Step 6 → ws.close() — cleanup (unmount पर)
readyState: 0 CONNECTING, 1 OPEN, 2 CLOSING, 3 CLOSED
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. new WebSocket(wss://...) से connect।
2. onopen पर तैयार।
3. send से भेजो, onmessage से पाओ।
4. टूटने पर खुद reconnect (RN अपने आप नहीं करता)।
5. Screen हटे तो close।
```

---

## 🟡 Real World Example
**WhatsApp/Telegram:** नए messages तुरंत। **Zerodha Kite / Groww:** live stock prices ticks। **Swiggy/Zomato:** delivery partner की live location (अक्सर WebSocket या SSE/MQTT)। **Dream11:** live score updates।

## 🟡 Real Example Hindi mein
**Zerodha Kite** में share के भाव हर सेकंड बदलते हैं — app poll नहीं करता; WebSocket से server हर tick push करता है। **Swiggy** में rider का map पर चलना भी ऐसे ही live updates से।

---

## 💻 Code Example — Basic

```jsx
// WsBasic.jsx — echo chat with a public test server
import React, { useEffect, useRef, useState } from 'react';       // hooks
import { View, Text, TextInput, Button } from 'react-native';     // UI

export default function WsBasic() {
  const wsRef = useRef(null);                                     // socket रखने को
  const [connected, setConnected] = useState(false);              // status
  const [log, setLog] = useState([]);                             // messages
  const [text, setText] = useState('');                           // input

  useEffect(() => {
    const ws = new WebSocket('wss://ws.postman-echo.com/raw');    // echo server (demo)
    wsRef.current = ws;                                           // save
    ws.onopen = () => setConnected(true);                         // connected
    ws.onmessage = (e) => setLog((l) => [...l, 'server: ' + e.data]); // incoming
    ws.onerror = () => setLog((l) => [...l, 'error']);            // error
    ws.onclose = () => setConnected(false);                       // closed
    return () => ws.close();                                      // cleanup
  }, []);

  const send = () => {
    if (wsRef.current?.readyState === 1) {                        // OPEN तभी भेजो
      wsRef.current.send(text);                                   // send
      setLog((l) => [...l, 'me: ' + text]);                       // log
      setText('');                                                // clear
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <Text>{connected ? 'Connected' : 'Disconnected'}</Text>
      <TextInput value={text} onChangeText={setText} placeholder="message" style={{ borderWidth: 1, padding: 8 }} />
      <Button title="Send" onPress={send} />
      {log.map((m, i) => <Text key={i}>{m}</Text>)}
    </View>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// socketClient.js — reconnect with backoff + heartbeat + message queue
export function createSocket(url, { onMessage, onStatus }) {
  let ws = null;                                                  // current socket
  let attempts = 0;                                               // reconnect गिनती
  let closedByUser = false;                                       // जानबूझकर बंद?
  let pingTimer = null;                                           // heartbeat timer
  let retryTimer = null;                                          // reconnect timer
  const pending = [];                                             // offline में भेजने वाले msgs

  const connect = () => {
    onStatus?.('connecting');                                     // UI को बताओ
    ws = new WebSocket(url);                                      // नया socket
    ws.onopen = () => {
      attempts = 0;                                               // reset
      onStatus?.('open');
      while (pending.length) ws.send(pending.shift());            // queued भेजो
      pingTimer = setInterval(() => {                             // heartbeat: connection ज़िंदा रखे
        if (ws.readyState === 1) ws.send(JSON.stringify({ type: 'ping' }));
      }, 25000);
    };
    ws.onmessage = (e) => {
      try { onMessage?.(JSON.parse(e.data)); }                    // JSON मानकर
      catch { onMessage?.(e.data); }                              // नहीं तो raw
    };
    ws.onerror = () => {};                                        // error के बाद onclose आता है
    ws.onclose = () => {
      clearInterval(pingTimer);                                   // heartbeat रोको
      onStatus?.('closed');
      if (closedByUser) return;                                   // user ने बंद किया → reconnect नहीं
      const delay = Math.min(30000, 1000 * 2 ** attempts++) + Math.random() * 300; // backoff+jitter
      retryTimer = setTimeout(connect, delay);                    // दोबारा कोशिश
    };
  };

  connect();                                                      // शुरू

  return {
    send(obj) {
      const s = typeof obj === 'string' ? obj : JSON.stringify(obj); // string बनाओ
      if (ws && ws.readyState === 1) ws.send(s);                  // open तो भेजो
      else pending.push(s);                                       // नहीं तो queue
    },
    close() {                                                     // component unmount पर
      closedByUser = true;                                        // flag
      clearTimeout(retryTimer); clearInterval(pingTimer);         // timers साफ़
      ws?.close();                                                // बंद
    },
  };
}
// App background में जाने पर iOS socket suspend कर देता है — AppState 'active' पर reconnect/refresh करो।
// Auth: token को URL query या पहले message में भेजो (server के अनुसार); wss:// ही use करो।
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Background में socket | कुछ समय बाद Doze में बंद/धीमा | App suspend होते ही कुछ सेकंड में बंद |
| Plain `ws://` | Cleartext blocked (9+) | ATS blocks |
| Custom headers in RN WebSocket | Third argument options में (RN-specific, `headers`) | वही (RN-specific) |
| Keep alive | Foreground service से (native) | केवल special modes (VoIP आदि) |
| API | Same | Same |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// WebSocket built-in। Socket.IO चाहिए तो: npx expo install socket.io-client
// import { io } from 'socket.io-client';
```
CLI way:
```jsx
// built-in WebSocket; npm i socket.io-client
// Android emulator में local server: ws://10.0.2.2:3000 (dev में cleartext allow)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Unmount पर `close()` न करना → memory leak/double messages।
✅ Correct: `useEffect` cleanup।

❌ Mistake 2: `readyState` देखे बिना `send`।
✅ Correct: `=== 1` check या queue।

❌ Mistake 3: तुरंत tight-loop reconnect।
✅ Correct: Exponential backoff + jitter।

❌ Mistake 4: `ws://` production में।
✅ Correct: `wss://`।

❌ Mistake 5: सोचना कि Background में भी चलेगा।
✅ Correct: AppState से reconnect; urgent के लिए push।

---

## 🧠 Tricky Interview Question
Chat screen में `useEffect(() => { const ws = new WebSocket(url); ws.onmessage = ...; })` (बिना dependency array और बिना cleanup) लिखा है। क्या होगा?

Answer: हर render पर नया WebSocket बनेगा और पुराना बंद नहीं होगा — कई connections, duplicate messages, memory leak। हल: `[]` dependency और `return () => ws.close()`।

---

## ⚫ Interview Questions + Answers
Q1: WebSocket vs HTTP polling?
A1: WebSocket persistent और दो-तरफ़ा; polling बार-बार नया request (महँगा)।

Q2: WebSocket vs SSE?
A2: SSE सिर्फ server→client, HTTP पर; WebSocket दो-तरफ़ा binary/text।

Q3: Socket.IO क्यों?
A3: Auto-reconnect, rooms, fallback, acknowledgements — पर server भी Socket.IO चाहिए (plain WebSocket से compatible नहीं)।

Q4: Reconnect कब?
A4: `onclose` पर (जानबूझकर बंद न हो तो), backoff के साथ; AppState active पर भी।

Q5: Heartbeat क्यों?
A5: Proxy/load balancer idle connection काट देते हैं; ping/pong से alive रखते हैं और dead connection पहचानते हैं।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chat, live prices, live tracking, collaborative features

❌ Avoid when:
- कभी-कभी का data (REST काफी)
- App को background में लगातार जगाना हो (push)

---

## 📊 Visual Diagram
```
 App ── HTTP Upgrade ──► Server
 App ◄══ open connection ══► Server
   send ───────────────►
        ◄─────────────── push (anytime)
   onclose ─► backoff ─► reconnect
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Handshake | Upgrade from HTTP | HTTP से upgrade |
| readyState | Socket state number | Socket की स्थिति |
| Heartbeat | Periodic ping | समय-समय का ping |
| Backoff | Growing retry delay | बढ़ती retry देरी |
| wss | Secure WebSocket | सुरक्षित WebSocket |

---

## ⚡ 3-Line Summary
English: WebSocket keeps a persistent two-way connection for real-time data.
Always close on unmount, check readyState, and reconnect with backoff.
It does not run in the background reliably.

Hindi: WebSocket real-time के लिए स्थायी दो-तरफ़ा connection रखता है।
Unmount पर close, readyState जाँचो, backoff से reconnect।
यह background में भरोसेमंद नहीं चलता।

---

## ➡️ Next Topic
**151. GraphQL in React Native** — जरूरत जितना ही data माँगने का तरीका।
