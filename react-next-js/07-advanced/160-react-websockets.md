# 160. React + WebSockets
# हिंदी में: React + WebSockets — Real-time Data (Live Tracking, Chat)

---

## 🔵 Simple Definition (English)
A **WebSocket** is a long-lived two-way connection between browser and server. After one handshake, either side can send messages at any time, without repeated HTTP requests. In React you open it inside an effect, store incoming messages in state, and close it on cleanup.

## 🔵 सरल परिभाषा (Hindi)
**WebSocket** browser और server के बीच लंबे समय तक चलने वाला दो-तरफ़ा connection है। एक handshake के बाद कोई भी पक्ष कभी भी message भेज सकता है, बार-बार HTTP request की ज़रूरत नहीं। React में आप इसे effect के अंदर खोलते हैं, आने वाले messages state में रखते हैं, और cleanup में बंद करते हैं।

---

## 🔴 Problem it Solves

With normal HTTP the client must ask ("polling"): "Where is my order now?" every 3 seconds. This wastes bandwidth and battery, adds delay up to the poll interval, and loads the server with empty responses. Live features (delivery tracking, chat, stock prices, notifications, multiplayer cursors) need the **server to push** data the moment it changes.

```jsx
// PROBLEM: polling
useEffect(() => {
  const id = setInterval(() => fetch('/api/order/42').then(r => r.json()).then(setOrder), 3000); // 20 requests/min
  return () => clearInterval(id);                  // most responses say "no change"
}, []);
```

## 🔴 यह क्यों बना? (Hindi)
सामान्य HTTP में client को पूछना पड़ता है ("polling"): हर 3 सेकंड में "मेरा order अब कहाँ है?"। इससे bandwidth और battery बर्बाद होती है, delay poll interval तक हो सकता है, और server पर खाली responses का बोझ पड़ता है। Live features (delivery tracking, chat, stock prices, notifications) में **server को खुद data push** करना होता है जैसे ही वह बदले।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Browser sends an HTTP request with "Upgrade: websocket" (the handshake)
Step 2 → Server replies 101 Switching Protocols; the connection stays open (ws:// or wss://)
Step 3 → In React: create the socket INSIDE useEffect (never during render)
Step 4 → Listen: onopen (connected), onmessage (data), onerror, onclose
Step 5 → On message: setState (append to list) so React re-renders the UI
Step 6 → Send: socket.send(JSON.stringify(payload)) only when readyState === OPEN
Step 7 → Cleanup: return () => socket.close() so Strict Mode / unmount does not leak connections
Step 8 → Reconnect with exponential backoff when the connection drops

Re-render behavior: every message that calls setState re-renders. High-frequency feeds (prices at
50/sec) should be batched (collect in a ref, flush with requestAnimationFrame/interval) and rows memoised.
Performance impact: much less traffic than polling, but each open socket costs server memory; avoid
unbounded message arrays (cap the list), and use wss:// in production.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Browser "Upgrade: websocket" वाली HTTP request भेजता है (handshake)
Step 2 → Server 101 Switching Protocols से जवाब देता है; connection खुला रहता है (ws:// या wss://)
Step 3 → React में: socket useEffect के अंदर बनाओ (render के दौरान कभी नहीं)
Step 4 → सुनो: onopen (जुड़ा), onmessage (data), onerror, onclose
Step 5 → Message आने पर: setState (list में जोड़ना) ताकि React UI फिर से render करे
Step 6 → भेजना: socket.send(JSON.stringify(payload)) सिर्फ़ जब readyState === OPEN हो
Step 7 → Cleanup: return () => socket.close() ताकि Strict Mode / unmount पर connection leak न हो
Step 8 → Connection टूटे तो exponential backoff के साथ दोबारा जुड़ो

Re-render behavior: हर message जो setState करे, re-render करता है। तेज़ feeds (50/sec prices) को batch करो
(ref में जमा करो, requestAnimationFrame/interval से flush) और rows को memo करो।
Performance impact: polling से बहुत कम traffic, पर हर खुला socket server memory लेता है; messages की
list सीमित रखो, और production में wss:// इस्तेमाल करो।
```

---

## 🟡 Real World Example
**Zomato / Swiggy live order tracking:** After you order, the delivery partner's phone sends GPS points to the server. The server pushes `{ orderId, lat, lng, status }` to your open socket every few seconds. React updates the map marker and the status ("Picked up", "Arriving in 4 min") instantly. The same pattern powers WhatsApp Web chat, Zerodha live prices and Google Docs presence cursors.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy live order tracking:** Order देने के बाद delivery partner का फ़ोन GPS points server को भेजता है। Server हर कुछ सेकंड में `{ orderId, lat, lng, status }` आपके खुले socket पर push करता है। React map marker और status ("Picked up", "Arriving in 4 min") तुरंत बदल देता है। यही पैटर्न WhatsApp Web chat, Zerodha live prices और Google Docs के presence cursors में चलता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: connect, receive and send with the browser WebSocket API
import { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';

function Chat({ url }) {
  const [messages, setMessages] = useState([]);              // received messages
  const [text, setText] = useState('');                      // input value
  const [connected, setConnected] = useState(false);         // connection status
  const socketRef = useRef(null);                            // keep the socket between renders

  useEffect(() => {
    const socket = new WebSocket(url);                       // open connection (inside effect, not render)
    socketRef.current = socket;                              // store for the send function

    socket.onopen = () => setConnected(true);                // handshake finished
    socket.onclose = () => setConnected(false);              // connection ended
    socket.onmessage = (event) => {                          // server pushed data
      setMessages((prev) => [...prev, event.data]);          // functional update: no stale state
    };

    return () => socket.close();                             // cleanup on unmount / url change
  }, [url]);

  function send(e) {
    e.preventDefault();                                      // stop page reload
    const socket = socketRef.current;
    if (socket && socket.readyState === WebSocket.OPEN) {    // only send when open
      socket.send(text);                                     // transmit text
      setText('');                                           // clear input
    }
  }

  return (
    <div>
      <p>Status: {connected ? 'Online' : 'Offline'}</p>
      <ul>{messages.map((m, i) => <li key={i}>{m}</li>)}</ul>
      <form onSubmit={send}>
        <input value={text} onChange={(e) => setText(e.target.value)} />
        <button disabled={!connected}>Send</button>
      </form>
    </div>
  );
}

// wss://echo.websocket.org echo service has been unreliable; use your own server in practice
createRoot(document.getElementById('root')).render(<Chat url="wss://example.com/chat" />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: reusable useWebSocket hook with auto-reconnect (backoff), JSON parsing,
// message cap, stable send function and cleanup safe for React Strict Mode.
import { useCallback, useEffect, useRef, useState } from 'react';

export function useWebSocket(url, { onMessage, maxRetries = 5 } = {}) {
  const [status, setStatus] = useState('connecting');        // connecting | open | closed
  const socketRef = useRef(null);                            // current socket
  const retryRef = useRef(0);                                // attempts so far
  const timerRef = useRef(null);                             // pending reconnect timer
  const onMessageRef = useRef(onMessage);                    // always call the latest callback
  onMessageRef.current = onMessage;                          // update ref each render (no effect re-run)

  useEffect(() => {
    let stopped = false;                                     // set true by cleanup

    function connect() {
      setStatus('connecting');
      const socket = new WebSocket(url);
      socketRef.current = socket;

      socket.onopen = () => { retryRef.current = 0; setStatus('open'); }; // reset backoff on success

      socket.onmessage = (event) => {
        try {
          onMessageRef.current?.(JSON.parse(event.data));    // parse once, hand to the caller
        } catch {
          console.warn('Ignoring non-JSON message');         // never crash on bad data
        }
      };

      socket.onclose = () => {
        setStatus('closed');
        if (stopped || retryRef.current >= maxRetries) return; // user left or gave up
        const delay = Math.min(1000 * 2 ** retryRef.current, 15000); // 1s, 2s, 4s ... max 15s
        retryRef.current += 1;
        timerRef.current = setTimeout(connect, delay);       // try again later
      };
    }

    connect();
    return () => {                                           // runs on unmount and in Strict Mode re-mount
      stopped = true;                                        // block reconnect
      clearTimeout(timerRef.current);                        // cancel pending retry
      socketRef.current?.close();                            // close the socket
    };
  }, [url, maxRetries]);

  const send = useCallback((data) => {                       // stable identity: safe in memoised children
    const s = socketRef.current;
    if (s?.readyState === WebSocket.OPEN) { s.send(JSON.stringify(data)); return true; }
    return false;                                            // caller can queue/retry
  }, []);

  return { status, send };
}

// Usage: live order tracker
export function OrderTracker({ orderId }) {
  const [location, setLocation] = useState(null);
  const [events, setEvents] = useState([]);
  const { status } = useWebSocket(`wss://api.example.com/orders/${orderId}/live`, {
    onMessage: (msg) => {
      if (msg.type === 'location') setLocation({ lat: msg.lat, lng: msg.lng }); // replace latest point
      if (msg.type === 'status') setEvents((e) => [...e.slice(-49), msg.text]); // cap list at 50
    },
  });
  return (
    <div>
      <p>Connection: {status}</p>
      {location && <p>Rider at {location.lat.toFixed(4)}, {location.lng.toFixed(4)}</p>}
      <ul>{events.map((t, i) => <li key={i}>{t}</li>)}</ul>
    </div>
  );
}
```

---

## 🟠 Next.js Connection

Next.js route handlers and Server Components are **request/response** and run on serverless platforms (like Vercel) that do not keep long-lived WebSocket servers. So in Next.js the WebSocket **client** lives in a Client Component, while the **server** is a separate service (Node `ws`/Socket.IO server, a custom Next server, or a managed service such as Pusher, Ably or Supabase Realtime). For one-way updates (notifications, progress) **Server-Sent Events** from a route handler are often simpler.

```jsx
// app/orders/[id]/Tracker.jsx : Client Component (browser APIs + state)
'use client';
import { useEffect, useState } from 'react';

export default function Tracker({ orderId }) {
  const [status, setStatus] = useState('Waiting...');
  useEffect(() => {
    const url = `${process.env.NEXT_PUBLIC_WS_URL}/orders/${orderId}`; // public env var for the browser
    const socket = new WebSocket(url);
    socket.onmessage = (e) => setStatus(JSON.parse(e.data).status);
    return () => socket.close();
  }, [orderId]);
  return <p>Order status: {status}</p>;
}
```

```js
// app/api/stream/route.js : Server-Sent Events alternative (one-way push, works with route handlers)
export async function GET() {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      const id = setInterval(() => {
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ t: Date.now() })}\n\n`)); // SSE format
      }, 2000);
      // cleanup on client disconnect is handled by cancel()
      this.id = id;
    },
    cancel() { clearInterval(this.id); },
  });
  return new Response(stream, { headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache' } });
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Not closing the socket in cleanup (duplicate connections, memory leaks, duplicate messages in Strict Mode)
✅ **Correct:** Always `return () => socket.close()`

```jsx
// Wrong
useEffect(() => { const s = new WebSocket(url); s.onmessage = handle; }, []);   // ❌ never closed
// Right
useEffect(() => { const s = new WebSocket(url); s.onmessage = handle; return () => s.close(); }, [url]); // ✅
```

❌ **Mistake 2:** Reading state directly inside `onmessage` (stale closure)
✅ **Correct:** Use functional updates or a ref for the latest value

```jsx
// Wrong: messages is the value from the first render
socket.onmessage = (e) => setMessages([...messages, e.data]);          // ❌ loses messages
// Right
socket.onmessage = (e) => setMessages((prev) => [...prev, e.data]);    // ✅
```

❌ **Mistake 3:** Creating the socket at the top level of the component (new connection every render)
✅ **Correct:** Create it inside `useEffect` and keep it in a ref

```jsx
// Wrong
function Chat() { const socket = new WebSocket(url); /* new socket on EVERY render */ }  // ❌
// Right: see useWebSocket above                                                          ✅
```

---

## 🧠 Tricky Interview Question

```jsx
function Feed() {
  const [count, setCount] = useState(0);
  useEffect(() => {
    const socket = new WebSocket('wss://example.com/feed');
    socket.onmessage = () => setCount(count + 1);
    return () => socket.close();
  }, []);
  return <p>{count}</p>;
}
```
**Answer:** After many messages `count` never goes beyond 1. The effect runs once (empty deps), so the `onmessage` closure captured `count = 0`. Every message calls `setCount(0 + 1)`. The fix is `setCount((c) => c + 1)`. In development with Strict Mode, effects run twice (mount, cleanup, mount), so a missing cleanup would also open two sockets and double-count messages; the cleanup `socket.close()` prevents that.

---

## ⚫ Interview Questions + Answers

Q1: WebSocket vs HTTP polling vs Server-Sent Events?
A1: Polling repeatedly asks the server (simple, wasteful, delayed). SSE is a one-way server-to-client stream over HTTP (auto-reconnect built in, great for notifications). WebSocket is full-duplex and best for chat, games and collaborative apps.

Q2: Where do you create the WebSocket in React and why?
A2: Inside `useEffect` (or a custom hook), because it is a side effect and must not run on every render or on the server. Store it in a `ref`, and close it in the cleanup function.

Q3: How do you handle reconnection?
A3: On `onclose` (when not intentionally closed) schedule a reconnect with exponential backoff and jitter, cap attempts or delay, restore subscriptions after reconnecting, and show connection status in the UI. Heartbeat (ping/pong) detects silently dead connections.

Q4: How do you handle very frequent messages?
A4: Do not call `setState` for every message. Buffer messages in a ref and flush at an interval or on `requestAnimationFrame`, keep only the latest or last N items, memoise rows, and consider virtualisation for large lists.

Q5: How do you secure a WebSocket connection?
A5: Use `wss://`, authenticate during connect (a short-lived token in the first message or a secure cookie; browser WebSocket cannot set custom headers), validate the `Origin` on the server, authorise every message, and rate-limit. Avoid long-lived tokens in the URL since they can appear in logs.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- You need real-time two-way communication (chat, collaboration, live trading, multiplayer)
- Updates are frequent and latency matters
- Many clients should get the same event immediately

❌ **Avoid when:**
- Updates are rare (simple polling or revalidation is enough)
- Only the server pushes (SSE is simpler and works through more proxies)
- You deploy on serverless with no way to host a persistent server (use a managed realtime service)

---

## 📊 Visual Diagram

```
  HTTP polling                          WebSocket
  Client      Server                    Client            Server
    │──GET──────►│                         │──Upgrade────────►│
    │◄──no change│                         │◄──101 Switching──│
    │──GET──────►│                         │◄══ location ═════│  (server pushes)
    │◄──no change│                         │◄══ status ═══════│
    │──GET──────►│                         │══ "typing" ═════►│  (client sends)
    │◄──new data │                         │   ... stays open ...

  React:  useEffect → new WebSocket → onmessage → setState → re-render
                                   └── cleanup → socket.close()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| WebSocket | Persistent two-way connection | स्थायी दो-तरफ़ा connection |
| Handshake | HTTP upgrade to start socket | Socket शुरू करने का HTTP upgrade |
| Polling | Repeated requests for updates | बार-बार पूछकर update लेना |
| SSE | One-way server push over HTTP | HTTP पर एकतरफ़ा server push |
| Backoff | Increasing wait between retries | दोबारा कोशिश में बढ़ता इंतज़ार |
| Heartbeat | Ping/pong to detect dead link | मृत connection पहचानने वाला ping |
| readyState | Current socket status | Socket की वर्तमान स्थिति |
| Stale closure | Callback with old state value | पुरानी state वाला callback |

---

## ⚡ 3-Line Summary
**English:**
1. WebSockets give a persistent two-way channel so the server can push live data to React without polling.
2. Open the socket in `useEffect`, update state with functional updates, and always close it in cleanup.
3. Add reconnect with backoff, cap or batch messages, use `wss://`, and host the socket server outside serverless Next.js.

**Hindi:**
1. WebSockets स्थायी दो-तरफ़ा channel देते हैं ताकि server बिना polling के React को live data push कर सके।
2. Socket `useEffect` में खोलो, functional updates से state बदलो, और cleanup में हमेशा बंद करो।
3. Backoff के साथ reconnect जोड़ो, messages सीमित या batch करो, `wss://` इस्तेमाल करो, और socket server को serverless Next.js के बाहर रखो।

---

## ➡️ Next Topic
**161. React + Canvas** — Live tracking जैसे data को अगर map, chart या game की तरह तेज़ी से draw करना हो, तो DOM की जगह Canvas का इस्तेमाल करना पड़ता है।
