# 120. Server-Sent Events in React
# हिंदी में: React में Server-Sent Events (SSE) — Server से Client की ओर Live Updates

---

## 🔵 Simple Definition (English)
**Server-Sent Events (SSE)** is a browser feature where the server keeps one HTTP response open and **streams text events to the client**, one way only (server to client). In the browser you use the built-in `EventSource` API, which also reconnects automatically.

## 🔵 सरल परिभाषा (Hindi)
**Server-Sent Events (SSE)** एक browser feature है जिसमें server एक HTTP response खुला रखता है और **client को text events stream करता है**, सिर्फ़ एक तरफ़ (server से client)। Browser में built-in `EventSource` API इस्तेमाल होती है, जो अपने आप reconnect भी करती है।

---

## 🔴 Problem it Solves

Many features only need the server to push updates: notifications, live order status, progress bars, build logs, or AI chat text arriving word by word. Polling wastes requests, and WebSocket is more than needed: you must manage a separate protocol, reconnect logic and a special server. SSE uses plain HTTP, works through most proxies, reconnects on its own, and is simple to build.

```jsx
// PROBLEM: polling for a one-way feed
setInterval(() => fetch('/api/notifications').then(r => r.json()).then(setList), 2000);

// SOLUTION: one open HTTP stream, the server decides when to send
const es = new EventSource('/api/notifications/stream');
es.onmessage = e => setList(prev => [JSON.parse(e.data), ...prev]);
```

## 🔴 यह क्यों बना? (Hindi)
कई features में सिर्फ़ server को updates push करने होते हैं: notifications, live order status, progress bars, build logs, या AI chat का text शब्द-दर-शब्द आना। Polling requests बर्बाद करती है, और WebSocket ज़रूरत से ज़्यादा है: अलग protocol, reconnect logic और खास server संभालना पड़ता है। SSE सादा HTTP इस्तेमाल करता है, ज़्यादातर proxies से चलता है, खुद reconnect करता है और बनाना आसान है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client: new EventSource('/stream')  → sends a normal GET with "Accept: text/event-stream"
Step 2 → Server replies with Content-Type: text/event-stream and does NOT end the response
Step 3 → Server writes events as text:   "event: status\n" + "data: {...}\n" + "id: 42\n" + blank line
Step 4 → Browser parses events → onmessage (default) or addEventListener('status', ...)
Step 5 → If the connection drops, the browser reconnects automatically and sends Last-Event-ID
Step 6 → In React: open in useEffect, setState in handlers, es.close() in cleanup
Step 7 → es.close() stops it for good (a closed EventSource never reconnects)

Format of one message (ends with a blank line):
  id: 42
  event: status
  data: {"orderId":7,"state":"OUT_FOR_DELIVERY"}
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client: new EventSource('/stream') → "Accept: text/event-stream" के साथ सामान्य GET भेजता है
Step 2 → Server Content-Type: text/event-stream के साथ जवाब देता है और response खत्म नहीं करता
Step 3 → Server events text में लिखता है: "event: status\n" + "data: {...}\n" + "id: 42\n" + खाली line
Step 4 → Browser events parse करता है → onmessage (default) या addEventListener('status', ...)
Step 5 → Connection टूटे तो browser अपने आप reconnect करता है और Last-Event-ID भेजता है
Step 6 → React में: useEffect में खोलो, handlers में setState करो, cleanup में es.close()
Step 7 → es.close() इसे हमेशा के लिए रोकता है (बंद EventSource दोबारा reconnect नहीं करता)

एक message का format (खाली line पर खत्म होता है):
  id: 42
  event: status
  data: {"orderId":7,"state":"OUT_FOR_DELIVERY"}
```

---

## 🟡 Real World Example
**Swiggy "Track your order" and Flipkart sale notifications:** After you order, the page shows "Preparing", then "Picked up", then "Out for delivery". Only the server knows when the state changes, and the browser never needs to send anything back. An SSE stream per order pushes a small event for each change. Also, ChatGPT-like UIs stream the answer text token by token over an SSE-style stream (for POST requests, apps use `fetch` with a stream reader, since `EventSource` supports only GET).

## 🟡 Real Example Hindi mein
**Swiggy "Track your order" और Flipkart sale notifications:** Order के बाद page पर "Preparing", फिर "Picked up", फिर "Out for delivery" दिखता है। State कब बदली यह सिर्फ़ server जानता है, और browser को कुछ वापस भेजना नहीं पड़ता। हर order के लिए एक SSE stream हर बदलाव पर छोटा event push करती है। ChatGPT जैसे UIs भी जवाब का text token-by-token SSE जैसी stream से दिखाते हैं (POST requests के लिए apps `fetch` के stream reader का इस्तेमाल करते हैं, क्योंकि `EventSource` सिर्फ़ GET सपोर्ट करता है)।

---

## 💻 Code Example — Basic

```jsx
// Basic: show live notifications with EventSource
import { useEffect, useState } from 'react';                  // React hooks
import { createRoot } from 'react-dom/client';                 // React 18/19 root API

function Notifications() {
  const [items, setItems] = useState([]);                      // list of notifications
  const [online, setOnline] = useState(false);                 // connection indicator

  useEffect(() => {
    const es = new EventSource('/api/notifications/stream');   // open the stream (GET only)

    es.onopen = () => setOnline(true);                         // connected
    es.onerror = () => setOnline(false);                       // dropped: the browser retries by itself
    es.onmessage = (event) => {                                // default event type is "message"
      const data = JSON.parse(event.data);                     // data is always a string
      setItems(prev => [data, ...prev].slice(0, 20));          // newest first, keep 20
    };

    return () => es.close();                                   // CLEANUP: stop the stream on unmount
  }, []);                                                      // open once

  return (
    <div>
      <p>{online ? 'Live' : 'Reconnecting...'}</p>
      <ul>{items.map(n => <li key={n.id}>{n.text}</li>)}</ul>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Notifications />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: a reusable useEventSource hook with named events, typed status, and an order tracker.
// Also includes a matching Node.js (Express) server so you can run it end to end.
import { useEffect, useRef, useState } from 'react';

export function useEventSource(url, handlers = {}) {
  const [status, setStatus] = useState('connecting');           // connecting | open | error | closed
  const handlersRef = useRef(handlers);                         // latest handlers without reconnecting
  useEffect(() => { handlersRef.current = handlers; });         // refresh after each render

  useEffect(() => {
    if (!url) return;                                           // null url = do nothing
    const es = new EventSource(url, { withCredentials: true }); // send cookies for authenticated streams

    es.onopen = () => setStatus('open');                        // browser connected
    es.onerror = () => {
      // readyState CONNECTING (0) = browser is retrying, CLOSED (2) = it gave up (e.g. HTTP 4xx)
      setStatus(es.readyState === EventSource.CLOSED ? 'closed' : 'error');
    };

    // register one listener per named event ("status", "done", ...)
    const names = Object.keys(handlersRef.current);
    const listeners = names.map(name => {
      const fn = (e) => {
        let payload = e.data;                                   // raw text by default
        try { payload = JSON.parse(e.data); } catch { /* keep text */ }
        handlersRef.current[name]?.(payload, e);                // call the latest handler
      };
      es.addEventListener(name, fn);                            // custom event type
      return [name, fn];
    });

    return () => {
      listeners.forEach(([name, fn]) => es.removeEventListener(name, fn)); // tidy up listeners
      es.close();                                               // close the connection
    };
  }, [url]);                                                    // new url = new stream

  return status;
}

// Usage: order tracking that stops by itself when the order is delivered
export function OrderTracker({ orderId }) {
  const [state, setState] = useState('PLACED');                // current order state
  const [finished, setFinished] = useState(false);             // stop streaming after delivery

  const status = useEventSource(finished ? null : `/api/orders/${orderId}/events`, {
    status: (data) => setState(data.state),                    // event: status
    done: () => setFinished(true),                             // event: done → url becomes null → closes
  });

  return <p>Order {orderId}: {state} ({status})</p>;
}

/* ---------- server.js (Node + Express) — run with: node server.js ----------
import express from 'express';
const app = express();

app.get('/api/orders/:id/events', (req, res) => {
  res.set({
    'Content-Type': 'text/event-stream',     // tells the browser this is SSE
    'Cache-Control': 'no-cache, no-transform',
    Connection: 'keep-alive',
  });
  res.flushHeaders();                        // send headers immediately

  const states = ['PREPARING', 'PICKED_UP', 'OUT_FOR_DELIVERY', 'DELIVERED'];
  let i = 0;
  const timer = setInterval(() => {
    res.write(`event: status\ndata: ${JSON.stringify({ state: states[i] })}\n\n`); // one event
    if (states[i] === 'DELIVERED') {
      res.write('event: done\ndata: {}\n\n');
      clearInterval(timer); res.end();
    }
    i++;
  }, 3000);

  req.on('close', () => clearInterval(timer));   // client left: stop work
});
app.listen(3001);
---------------------------------------------------------------------------- */
```

---

## 🟠 Next.js Connection

In the App Router, a Route Handler can return a streaming `Response` with `Content-Type: text/event-stream`, so SSE works without a separate server on Node runtimes. Add `export const dynamic = 'force-dynamic'` so it is never cached. On serverless platforms, long-lived connections are limited by the function's max duration, so the browser will reconnect automatically (SSE handles this well). Client Components (`'use client'`) open `EventSource` inside `useEffect`. Platform limits and proxy buffering are deployment-dependent, so test in production.

```jsx
// app/api/orders/[id]/events/route.js (Route Handler)
export const dynamic = 'force-dynamic';                          // never cache a stream

export async function GET(request, { params }) {
  const { id } = await params;                                   // Next.js 15+: params is a Promise
  const encoder = new TextEncoder();                             // streams need bytes
  const states = ['PREPARING', 'PICKED_UP', 'OUT_FOR_DELIVERY', 'DELIVERED'];

  const stream = new ReadableStream({
    async start(controller) {
      for (const state of states) {
        if (request.signal.aborted) break;                       // client disconnected
        controller.enqueue(encoder.encode(`event: status\ndata: ${JSON.stringify({ id, state })}\n\n`));
        await new Promise(r => setTimeout(r, 3000));             // simulate time between changes
      }
      controller.enqueue(encoder.encode('event: done\ndata: {}\n\n'));
      controller.close();                                        // end the stream
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',                       // SSE content type
      'Cache-Control': 'no-cache, no-transform',                 // do not buffer or transform
      Connection: 'keep-alive',
    },
  });
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Not closing the `EventSource` (the connection stays alive after the component is gone)
✅ **Correct:** Close it in the cleanup function

```jsx
// Wrong: leaks one connection every mount (browsers allow only ~6 per domain on HTTP/1.1)
useEffect(() => { const es = new EventSource(url); es.onmessage = handle; }, [url]);
// Right
useEffect(() => { const es = new EventSource(url); es.onmessage = handle; return () => es.close(); }, [url]);
```

❌ **Mistake 2:** Wanting to send data back or use POST/custom headers with `EventSource`
✅ **Correct:** `EventSource` is GET-only without custom headers. Send data with normal `fetch` calls, or use `fetch` + `ReadableStream` (or `@microsoft/fetch-event-source`) for POST/auth headers

```jsx
// Wrong: there is no way to pass an Authorization header
new EventSource(url, { headers: { Authorization: 'Bearer x' } });   // ❌ option is ignored
// Right: cookies (withCredentials) or fetch streaming
const res = await fetch(url, { headers: { Authorization: 'Bearer x' } }); // ✅
const reader = res.body.getReader();                                       // read chunks manually
```

❌ **Mistake 3:** Forgetting that `event.data` is a string, and ending messages without the blank line
✅ **Correct:** `JSON.parse` the data, and end each server message with `\n\n`

```jsx
// Wrong
es.onmessage = e => setCount(e.data.count);        // ❌ e.data is a string, count is undefined
// Right
es.onmessage = e => setCount(JSON.parse(e.data).count);   // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
useEffect(() => {
  const es = new EventSource('/stream');
  es.onerror = () => es.close();          // "clean up on error"
  es.onmessage = e => console.log(e.data);
  return () => es.close();
}, []);
// The Wi-Fi drops for 2 seconds and returns. Does the app keep receiving events?
```
**Answer:** No. `EventSource` is designed to reconnect automatically after a network drop, but calling `es.close()` inside `onerror` turns that off permanently, because a closed `EventSource` never reconnects. The `error` event fires even for temporary drops. The correct approach is to let the browser retry (just show "Reconnecting..."), and close only when `es.readyState === EventSource.CLOSED` (the browser gave up, for example on HTTP 4xx) or when you decide to stop. The server can also control retry timing with a `retry: 5000` line.

---

## ⚫ Interview Questions + Answers

Q1: SSE vs WebSocket: when to choose which?
A1: SSE is one-way (server to client) over plain HTTP, with automatic reconnect and `Last-Event-ID`, text only. WebSocket is two-way, supports binary, and needs its own protocol and server. Choose SSE for notifications, feeds, progress and log streaming; WebSocket for chat, games and collaboration.

Q2: How does SSE reconnect and not lose events?
A2: The browser reconnects automatically after a delay (default about 3 seconds, adjustable with `retry:`). If the server sets `id:` on events, the browser sends the `Last-Event-ID` header on reconnect, and the server can resume from that point.

Q3: What are the limits of `EventSource`?
A3: GET only, no custom headers, text only (UTF-8), and on HTTP/1.1 browsers limit about 6 connections per domain (HTTP/2 raises this to around 100 streams). For POST bodies or Authorization headers use `fetch` streaming or a library.

Q4: How do you handle SSE cleanup in React?
A4: Open it in `useEffect`, and return a cleanup that calls `es.close()` (and removes custom listeners). This avoids leaks and duplicates in Strict Mode, where effects run twice in development.

Q5: How would you stream an AI/LLM response in React?
A5: The server streams chunks (SSE-formatted or raw text). On the client, for POST requests, use `fetch`, read `response.body.getReader()` with a `TextDecoder`, and append each chunk to state (`setText(t => t + chunk)`). Throttle updates if chunks are very frequent.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Updates flow only from server to client (notifications, order status, progress, live logs)
- You want automatic reconnect with minimal code
- You want to stay on plain HTTP behind existing proxies and auth cookies

❌ **Avoid when:**
- The client must send frequent messages (chat, games) so WebSocket is better
- You need binary data or very high message rates
- Your platform or proxy buffers responses or caps function duration strictly (test first)

---

## 📊 Visual Diagram

```
 React (useEffect)                                    Server (Route Handler)
 ─────────────────                                    ──────────────────────
 new EventSource('/stream')  ── GET (Accept: text/event-stream) ──►
                             ◄── 200 Content-Type: text/event-stream (stays open)
                             ◄── event: status\ndata: {"state":"PICKED_UP"}\n\n
   onmessage / addEventListener('status') → setState → re-render
                             ◄── event: status ... "OUT_FOR_DELIVERY"
        (network drops) ──► browser waits ~3s ──► reconnects with Last-Event-ID
 cleanup: es.close()  ───────────────────────────────────── stream ends

 Direction: SERVER ──► CLIENT only.   Re-render: once per event (batched by React 18).
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SSE | Server pushes events over one HTTP stream | Server का एक HTTP stream पर events भेजना |
| EventSource | Browser API to receive SSE | SSE पाने की Browser API |
| text/event-stream | Content type for SSE responses | SSE responses का content type |
| Last-Event-ID | Header to resume after reconnect | Reconnect के बाद वहीं से चालू करने का header |
| retry | Server hint for reconnect delay | Reconnect की देरी का server hint |
| Named event | Custom event type with `event:` line | `event:` line वाला custom event |
| Streaming | Sending data in chunks over time | Data को टुकड़ों में समय के साथ भेजना |
| Unidirectional | One direction only | सिर्फ़ एक दिशा में |

---

## ⚡ 3-Line Summary
**English:**
1. SSE streams text events from the server to the browser over one open HTTP connection, using `EventSource`.
2. It reconnects automatically, so open it in `useEffect`, parse `event.data`, and call `es.close()` in cleanup.
3. It is one-way and GET-only; use WebSocket for two-way, and in Next.js stream from a Route Handler.

**Hindi:**
1. SSE एक खुले HTTP connection पर server से browser तक text events stream करता है, `EventSource` के ज़रिए।
2. यह अपने आप reconnect करता है, इसलिए `useEffect` में खोलो, `event.data` को parse करो, और cleanup में `es.close()` करो।
3. यह एकतरफ़ा और सिर्फ़ GET है; दो-तरफ़ा के लिए WebSocket लो, और Next.js में Route Handler से stream करो।

---

## ➡️ Next Topic
**121. React Performance Problems** — अब data fetching पूरा हुआ; अगला कदम है यह समझना कि React app धीमा क्यों होता है (अनावश्यक re-renders, भारी calculations, बड़ी lists) ताकि सही optimization चुन सको।
