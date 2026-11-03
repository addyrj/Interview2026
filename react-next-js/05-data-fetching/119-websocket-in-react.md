# 119. WebSocket in React
# हिंदी में: React में WebSocket — Real-time Two-way Connection

---

## 🔵 Simple Definition (English)
A **WebSocket** is a long-lived, two-way connection between the browser and a server. Once opened, either side can send messages at any time without a new HTTP request. In React you open it inside `useEffect`, store messages in state, and **close it in the cleanup function**.

## 🔵 सरल परिभाषा (Hindi)
**WebSocket** browser और server के बीच एक लंबे समय तक खुला रहने वाला दो-तरफ़ा connection है। एक बार खुलने के बाद कोई भी पक्ष कभी भी message भेज सकता है, नई HTTP request की ज़रूरत नहीं। React में इसे `useEffect` में खोलते हैं, messages को state में रखते हैं, और **cleanup function में बंद करते हैं**।

---

## 🔴 Problem it Solves

HTTP is request-response: the server cannot talk first. For chat, live scores or stock prices, the old workaround was polling (ask the server every second), which wastes bandwidth, adds delay and loads the server with empty answers. WebSocket keeps one connection open so the server can push data the moment it exists, and the client can send small messages cheaply.

```jsx
// PROBLEM: polling = many wasted requests and delay up to the interval
useEffect(() => {
  const id = setInterval(() => fetch('/api/messages').then(r => r.json()).then(setMsgs), 1000);
  return () => clearInterval(id);       // 3600 requests per hour, most return nothing new
}, []);

// SOLUTION: one connection, the server pushes only when there is something new
const ws = new WebSocket('wss://example.com/chat');
ws.onmessage = e => setMsgs(m => [...m, JSON.parse(e.data)]);
```

## 🔴 यह क्यों बना? (Hindi)
HTTP request-response है: server पहले बात नहीं कर सकता। Chat, live scores या stock prices के लिए पुराना तरीका polling था (हर सेकंड server से पूछना), जिसमें bandwidth बर्बाद होती है, देरी आती है और खाली जवाबों से server पर लोड पड़ता है। WebSocket एक connection खुला रखता है, इसलिए server data बनते ही push कर सकता है और client छोटे messages सस्ते में भेज सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Browser sends an HTTP request with "Upgrade: websocket" header (handshake)
Step 2 → Server replies 101 Switching Protocols → the connection becomes a WebSocket (ws:// or wss://)
Step 3 → Events: onopen (ready), onmessage (data arrived), onerror, onclose
Step 4 → ws.send(string) sends a message; the server can push messages any time
Step 5 → In React: create the socket in useEffect, update state in onmessage
Step 6 → Cleanup: ws.close() when the component unmounts or the URL changes (avoid leaks)
Step 7 → Browser WebSocket does NOT auto-reconnect: add reconnect with backoff yourself (or use a library)

readyState: 0 CONNECTING • 1 OPEN • 2 CLOSING • 3 CLOSED  (send only when it is 1)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Browser "Upgrade: websocket" header वाली HTTP request भेजता है (handshake)
Step 2 → Server 101 Switching Protocols लौटाता है → connection WebSocket बन जाता है (ws:// या wss://)
Step 3 → Events: onopen (तैयार), onmessage (data आया), onerror, onclose
Step 4 → ws.send(string) से message जाता है; server कभी भी messages push कर सकता है
Step 5 → React में: useEffect में socket बनाओ, onmessage में state update करो
Step 6 → Cleanup: component unmount होने या URL बदलने पर ws.close() करो (leak से बचने के लिए)
Step 7 → Browser का WebSocket अपने आप reconnect नहीं करता: backoff के साथ खुद reconnect जोड़ो (या library लो)

readyState: 0 CONNECTING • 1 OPEN • 2 CLOSING • 3 CLOSED  (send सिर्फ़ तब करो जब 1 हो)
```

---

## 🟡 Real World Example
**WhatsApp Web / Zomato delivery chat / Zerodha Kite live prices:** In a chat window, when your friend sends "reached", the server pushes that message through the WebSocket and it appears instantly. Zerodha Kite streams live stock ticks through WebSocket so prices update many times per second. If the network drops, the app shows "Reconnecting..." and reconnects automatically, then asks for missed messages.

## 🟡 Real Example Hindi mein
**WhatsApp Web / Zomato delivery chat / Zerodha Kite live prices:** Chat window में दोस्त "reached" भेजे तो server वह message WebSocket से push करता है और तुरंत दिख जाता है। Zerodha Kite live stock ticks WebSocket से stream करता है इसलिए prices सेकंड में कई बार बदलते हैं। Network टूटे तो app "Reconnecting..." दिखाता है, अपने आप दोबारा जुड़ता है, और छूटे हुए messages माँगता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: a simple chat component using the browser WebSocket API
import { useEffect, useRef, useState } from 'react';          // React hooks
import { createRoot } from 'react-dom/client';                 // React 18/19 root API

function Chat({ url }) {
  const [messages, setMessages] = useState([]);                // all received messages
  const [text, setText] = useState('');                        // input value
  const [connected, setConnected] = useState(false);           // connection status for the UI
  const wsRef = useRef(null);                                  // keep the socket without re-rendering

  useEffect(() => {
    const ws = new WebSocket(url);                             // open the connection
    wsRef.current = ws;                                        // save it for send()

    ws.onopen = () => setConnected(true);                      // ready to send
    ws.onclose = () => setConnected(false);                    // closed (network or server)
    ws.onerror = () => setConnected(false);                    // basic error handling
    ws.onmessage = (event) => {                                // server pushed something
      setMessages(prev => [...prev, event.data]);              // functional update: never lose messages
    };

    return () => ws.close();                                   // CLEANUP: close on unmount / url change
  }, [url]);                                                   // reconnect only if the url changes

  function send(e) {
    e.preventDefault();                                        // stop page reload
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN && text.trim()) { // only send when OPEN
      ws.send(text);                                           // send plain text
      setText('');                                             // clear the input
    }
  }

  return (
    <div>
      <p>{connected ? 'Online' : 'Offline'}</p>
      <ul>{messages.map((m, i) => <li key={i}>{m}</li>)}</ul> {/* index key is OK: append-only list */}
      <form onSubmit={send}>
        <input value={text} onChange={e => setText(e.target.value)} />
        <button disabled={!connected}>Send</button>
      </form>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Chat url="wss://example.com/chat" />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: reusable useWebSocket hook with auto-reconnect (exponential backoff + jitter),
// JSON messages, a send queue while offline, and safe cleanup
import { useCallback, useEffect, useRef, useState } from 'react';

export function useWebSocket(url, { onMessage, maxRetries = 8 } = {}) {
  const [status, setStatus] = useState('connecting');           // connecting | open | reconnecting | closed
  const wsRef = useRef(null);                                    // current socket
  const retryRef = useRef(0);                                    // reconnect attempts so far
  const timerRef = useRef(null);                                 // pending reconnect timeout
  const queueRef = useRef([]);                                   // messages waiting for an open socket
  const onMessageRef = useRef(onMessage);                        // always call the LATEST handler

  useEffect(() => { onMessageRef.current = onMessage; });        // update the ref after every render

  useEffect(() => {
    let cancelled = false;                                       // true after cleanup runs

    function connect() {
      const ws = new WebSocket(url);                             // open a new socket
      wsRef.current = ws;

      ws.onopen = () => {
        retryRef.current = 0;                                    // success: reset the backoff
        setStatus('open');
        queueRef.current.forEach(m => ws.send(m));               // flush messages queued while offline
        queueRef.current = [];
      };

      ws.onmessage = (event) => {
        try { onMessageRef.current?.(JSON.parse(event.data)); }  // parse JSON safely
        catch { onMessageRef.current?.(event.data); }            // fall back to raw text
      };

      ws.onclose = () => {
        if (cancelled) return;                                   // we closed it on purpose: do not reconnect
        if (retryRef.current >= maxRetries) { setStatus('closed'); return; } // give up
        setStatus('reconnecting');
        const base = Math.min(30_000, 1000 * 2 ** retryRef.current); // 1s, 2s, 4s ... max 30s
        const delay = base / 2 + Math.random() * (base / 2);     // jitter: avoids all clients retrying together
        retryRef.current += 1;
        timerRef.current = setTimeout(connect, delay);           // try again later
      };
      // onerror is always followed by onclose, so reconnect logic lives in onclose
    }

    connect();                                                   // first connection

    return () => {
      cancelled = true;                                          // stop reconnecting
      clearTimeout(timerRef.current);                            // cancel pending retry
      wsRef.current?.close();                                    // close the socket
    };
  }, [url, maxRetries]);                                         // new url = fresh connection

  const send = useCallback((data) => {
    const msg = typeof data === 'string' ? data : JSON.stringify(data); // objects become JSON
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) ws.send(msg);    // send now
    else queueRef.current.push(msg);                             // or send after reconnect
  }, []);                                                        // stable identity, safe in deps

  return { status, send };
}

// Usage: live order tracking
export function OrderTracker({ orderId }) {
  const [location, setLocation] = useState(null);                // rider location
  const { status, send } = useWebSocket(`wss://example.com/orders/${orderId}`, {
    onMessage: msg => { if (msg.type === 'LOCATION') setLocation(msg.payload); }, // handle only known types
  });
  return (
    <div>
      <p>Connection: {status}</p>
      <p>Rider: {location ? `${location.lat}, ${location.lng}` : 'waiting...'}</p>
      <button onClick={() => send({ type: 'PING' })}>Ping</button>
    </div>
  );
}
```

---

## 🟠 Next.js Connection

Next.js route handlers and Server Components run on a serverless/edge-style model on platforms like Vercel, which do **not** keep long-lived WebSocket servers. So the usual approach is: the browser (Client Component, `'use client'`) connects to a separate WebSocket service (your own Node server with `ws`/Socket.IO, or a managed service such as Pusher, Ably or Supabase Realtime). If you self-host Next.js with a custom server you can attach a WebSocket server, but that is not supported on Vercel. Never open a WebSocket during server rendering: `WebSocket` code belongs in `useEffect`.

```jsx
// app/orders/[id]/Tracker.jsx
'use client';                                                    // WebSocket exists only in the browser
import { useWebSocket } from '@/hooks/useWebSocket';             // the hook above

export default function Tracker({ orderId }) {
  // NEXT_PUBLIC_ variables are available in the browser
  const url = `${process.env.NEXT_PUBLIC_WS_URL}/orders/${orderId}`;
  const { status } = useWebSocket(url);                          // opens only after hydration (inside useEffect)
  return <p>Live status: {status}</p>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting to close the socket in cleanup (duplicate connections, memory leaks, double messages)
✅ **Correct:** Always `return () => ws.close()`

```jsx
// Wrong: every re-run or Strict Mode remount leaves an old socket open
useEffect(() => { const ws = new WebSocket(url); ws.onmessage = handle; }, [url]);
// Right
useEffect(() => { const ws = new WebSocket(url); ws.onmessage = handle; return () => ws.close(); }, [url]);
```

❌ **Mistake 2:** Using stale state inside `onmessage` (closure bug)
✅ **Correct:** Use the functional update form or a ref

```jsx
// Wrong: `messages` is captured from the first render, so only the last message is kept
ws.onmessage = e => setMessages([...messages, e.data]);          // ❌
// Right
ws.onmessage = e => setMessages(prev => [...prev, e.data]);      // ✅
```

❌ **Mistake 3:** Calling `send()` before the socket is OPEN, and assuming it reconnects itself
✅ **Correct:** Check `readyState` (or queue messages) and implement reconnect

```jsx
// Wrong: throws InvalidStateError if still CONNECTING
ws.send('hello');
// Right
if (ws.readyState === WebSocket.OPEN) ws.send('hello');          // ✅ else queue it
```

---

## 🧠 Tricky Interview Question

```jsx
function Feed({ url }) {
  const [items, setItems] = useState([]);
  useEffect(() => {
    const ws = new WebSocket(url);
    ws.onmessage = e => setItems(prev => [...prev, e.data]);
    // no cleanup
  }, [url]);
  return <p>{items.length}</p>;
}
// In development with <StrictMode>, the server sends ONE message. What does the UI show?
```
**Answer:** It shows `2`. React 18/19 Strict Mode (development only) mounts, unmounts and mounts the component again to reveal missing cleanups. Without a cleanup, the first socket is never closed, so two live connections exist and both receive the server's message (if the server broadcasts to all connections), and both call `setItems`. In production there is one effect run, so you would see `1`, which is why this bug hides until dev or StrictMode. Fix: `return () => ws.close()`. With cleanup, the first socket is closed during the Strict Mode unmount and only the second one delivers messages.

---

## ⚫ Interview Questions + Answers

Q1: WebSocket vs HTTP polling vs Server-Sent Events?
A1: Polling asks repeatedly (simple, wasteful). SSE is a one-way server-to-client stream over HTTP with auto-reconnect. WebSocket is full-duplex (both directions) on one connection. Use WebSocket for chat/games, SSE for one-way feeds, polling for rare updates.

Q2: Where do you create the WebSocket in React and why?
A2: Inside `useEffect`, because it is a side effect that must run in the browser after rendering, and effects have a cleanup for closing the connection. Never during render, and never on the server.

Q3: How do you handle reconnection?
A3: The browser API does not reconnect. In `onclose`, schedule a new connection with exponential backoff and jitter, cap the retries, reset the counter on `onopen`, and avoid reconnecting when the close was intentional (flag set in cleanup). Libraries like `reconnecting-websocket`, `react-use-websocket` or Socket.IO do this for you.

Q4: How do you avoid too many re-renders with high-frequency messages (stock ticks)?
A4: Batch updates (store messages in a ref and flush with `requestAnimationFrame` or every 100 ms), keep only the last N items, update only the changed row, use `memo` for rows, and consider `useSyncExternalStore` for an external store. React 18 batches state updates automatically, but 100 messages per second still need throttling.

Q5: How do you secure a WebSocket?
A5: Use `wss://` (TLS), authenticate during the handshake (cookie or short-lived token in the first message or query string, since browsers cannot set custom headers), validate the `Origin` on the server, validate message formats, and rate-limit. Never trust incoming data blindly: parse with try/catch.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Chat, collaborative editing, multiplayer games
- Live prices, scores or location tracking with frequent updates in both directions
- Low-latency messages are required

❌ **Avoid when:**
- Updates are rare (use polling or React Query `refetchInterval`)
- Only the server sends updates (Server-Sent Events are simpler)
- You deploy on serverless without a separate realtime service

---

## 📊 Visual Diagram

```
 Browser (React)                                   Server
 ───────────────                                   ──────
 GET /chat  Upgrade: websocket  ─────────────────►
                                ◄───────────────── 101 Switching Protocols
 ┌─ onopen ─────────────── persistent TCP connection ────────────────┐
 │  ws.send("hi")  ─────────────────────────────────────────────────►│
 │                 ◄──────────────────────────────── "reached" (push)│
 │  onmessage → setMessages(prev => [...prev, msg]) → re-render      │
 └─ cleanup: ws.close()  ───────────────────────────────────────────►┘

 useEffect( connect, [url] ) ──► cleanup closes the socket on unmount / url change
 Re-render: one render per state update (batched in React 18). Throttle ticks above ~30/s.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| WebSocket | Two-way persistent connection | दो-तरफ़ा स्थायी connection |
| Handshake | HTTP upgrade that starts the socket | HTTP upgrade जिससे socket शुरू होता है |
| wss:// | WebSocket over TLS (secure) | TLS वाला सुरक्षित WebSocket |
| readyState | Connection state number (0 to 3) | Connection की स्थिति (0 से 3) |
| Full-duplex | Both sides send at the same time | दोनों तरफ़ से साथ-साथ भेजना |
| Backoff | Growing wait between reconnect tries | Reconnect के बीच बढ़ता इंतज़ार |
| Jitter | Random delay added to the backoff | Backoff में जुड़ी random देरी |
| Cleanup | Function returned by useEffect | useEffect से लौटने वाला cleanup function |

---

## ⚡ 3-Line Summary
**English:**
1. WebSocket is a persistent two-way connection, opened in `useEffect` and closed in its cleanup.
2. Use functional state updates in `onmessage`, check `readyState` before `send`, and add reconnect with backoff.
3. In Next.js connect from Client Components to a separate realtime server (Vercel has no WebSocket server).

**Hindi:**
1. WebSocket एक स्थायी दो-तरफ़ा connection है जो `useEffect` में खुलता है और उसके cleanup में बंद होता है।
2. `onmessage` में functional state update करो, `send` से पहले `readyState` जाँचो, और backoff के साथ reconnect जोड़ो।
3. Next.js में Client Components से अलग realtime server से जुड़ो (Vercel पर WebSocket server नहीं चलता)।

---

## ➡️ Next Topic
**120. Server-Sent Events in React** — जब सिर्फ़ server से client की ओर updates चाहिए (notifications, live logs, AI streaming), तब WebSocket से सरल विकल्प `EventSource`।
