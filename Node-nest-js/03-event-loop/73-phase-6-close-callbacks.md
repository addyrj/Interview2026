# 73. Phase 6 — Close Callbacks
# हिंदी में: Phase 6 — Close Callbacks Phase

---

## 🔵 Simple Definition (English)
**Close Callbacks** is the final phase of each Event Loop iteration. It runs callbacks for handles/sockets closed **abruptly** — specifically those closed via `socket.destroy()` and similar forced-close operations that emit a `'close'` event. (Graceful closes still fire `'close'`, but this phase is specifically where such close-event callbacks are executed as part of the cycle.)

## 🔵 सरल परिभाषा (Hindi)
**Close Callbacks** हर Event Loop iteration का last phase है। ये उन handles/sockets के callbacks चलाता है जो **abruptly** close हुए हैं — खासकर `socket.destroy()` जैसी forced-close operations से, जो `'close'` event emit करती हैं।

---

## 🔴 Problem it Solves
```
NEED: When a socket/handle is closed (gracefully or forcefully),
      cleanup code (closing file descriptors, freeing resources,
      logging, notifying other parts of the app) needs a dedicated
      place to run — AFTER everything else in the current iteration.

WITHOUT A DEDICATED CLOSE PHASE:
  Cleanup logic could run at unpredictable times relative to other
  pending work, making resource cleanup ordering unreliable.

WITH CLOSE CALLBACKS PHASE:
  All 'close' event handlers run together, at the END of each loop
  iteration, after Timers/Poll/Check — a clean, predictable place
  for cleanup logic (closing DB connections, releasing file handles,
  decrementing connection counters, etc.)
```

## 🔴 यह क्यों बना? (Hindi)
```
Socket/handle close होने पर cleanup code (file descriptors close करना,
resources free करना, logging) को एक dedicated जगह चाहिए run होने के लिए
Close Callbacks phase से सब 'close' event handlers predictable तरीके से
loop iteration के अंत में run होते हैं
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → A socket/handle is closed — either gracefully (socket.end())
          or abruptly (socket.destroy())
Step 2 → libuv emits a 'close' event for that handle
Step 3 → If closed via destroy()/forced close → callback queued for the
          CLOSE CALLBACKS phase specifically
Step 4 → Event loop finishes Check phase (Phase 5)
Step 5 → Event loop enters CLOSE CALLBACKS phase (Phase 6, the LAST phase)
Step 6 → All queued 'close' event callbacks run
Step 7 → Event loop iteration ends → checks if any work remains
          (timers, I/O, refs) → if yes, loops back to Phase 1 (Timers)
          → if no, process exits
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. Socket/handle close होता है — gracefully (end()) या abruptly (destroy())
2. libuv 'close' event emit करता है
3. Forced close callback Close Callbacks phase के लिए queue होता है
4. Check phase खत्म होने पर event loop Close Callbacks (last phase) में आता है
5. सब 'close' callbacks run होते हैं
6. Iteration खत्म → अगर काम बचा है तो फिर Timers से शुरू, नहीं तो process exit
```

---

## 🟡 Real World Example
**Razorpay webhook server:** When a client abruptly disconnects mid-request (e.g., mobile app loses network during a payment confirmation call), the TCP socket emits `'close'`. Razorpay's cleanup logic — decrementing an active-connections gauge, releasing a reserved idempotency lock, logging the abandoned request for monitoring — runs in this Close Callbacks phase. This ensures resource cleanup happens reliably even for ungracefully terminated connections, preventing resource leaks under flaky mobile network conditions.

## 🟡 Real Example Hindi mein
**Razorpay webhook server:** Client अचानक disconnect हो जाए (mobile app network खो दे payment confirmation के दौरान), TCP socket `'close'` emit करता है। Cleanup logic (active-connections counter घटाना, idempotency lock release करना, logging) Close Callbacks phase में run होता है — flaky mobile network में भी resource leak नहीं होता।

---

## 💻 Code Example — Basic

```javascript
// close-callbacks-basic.js
// Run: node close-callbacks-basic.js

const net = require('net');

const server = net.createServer((socket) => {
  console.log('Client connected');

  // 'close' event fires when the socket is fully closed
  socket.on('close', (hadError) => {
    console.log('Socket closed. Had error:', hadError);
    // This runs in the CLOSE CALLBACKS phase
  });

  // Simulate an abrupt close after 1 second
  setTimeout(() => {
    console.log('Forcefully destroying socket...');
    socket.destroy();  // abrupt close, triggers 'close' event
  }, 1000);
});

server.listen(8090, () => {
  console.log('Server listening on 8090');

  // Create a client to connect and trigger the above flow
  const client = net.createConnection({ port: 8090 });
  client.on('close', () => console.log('Client socket also closed'));
});

// OUTPUT:
// Server listening on 8090
// Client connected
// Forcefully destroying socket...
// Socket closed. Had error: false
// Client socket also closed
```

## 💻 Code Example — Advanced

```javascript
// close-callbacks-advanced.js — resource tracking with close cleanup

const net = require('net');

class ConnectionTracker {
  constructor() {
    this.activeConnections = new Set();
  }

  track(socket) {
    this.activeConnections.add(socket);
    console.log(`Connection added. Active: ${this.activeConnections.size}`);

    // Cleanup runs in the Close Callbacks phase — guaranteed to fire
    // whether the socket closed gracefully or was destroyed due to an error
    socket.on('close', (hadError) => {
      this.activeConnections.delete(socket);
      console.log(
        `Connection removed (hadError: ${hadError}). Active: ${this.activeConnections.size}`
      );

      if (hadError) {
        // Log for monitoring/alerting — abrupt closes often indicate
        // network issues, client crashes, or malicious behavior
        console.warn('Connection closed due to a transmission error — investigate if frequent');
      }
    });
  }

  getActiveCount() {
    return this.activeConnections.size;
  }
}

const tracker = new ConnectionTracker();

const server = net.createServer((socket) => {
  tracker.track(socket);

  socket.on('data', (data) => {
    socket.write(`echo: ${data}`);
  });

  socket.on('error', (err) => {
    console.error('Socket error (will trigger close soon):', err.message);
  });
});

server.listen(8091, () => {
  console.log('Tracked server on 8091');

  // Simulate a client connecting, sending data, then being forcefully destroyed
  const client = net.createConnection({ port: 8091 }, () => {
    client.write('hello');
    setTimeout(() => client.destroy(new Error('simulated abrupt disconnect')), 500);
  });
});

// Graceful shutdown: use the tracker to know when it's safe to exit
process.on('SIGTERM', () => {
  console.log(`Shutting down. ${tracker.getActiveCount()} connections still active.`);
  server.close(() => process.exit(0));
});
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const app = express();

app.get('/stream', (req, res) => {
  console.log('Starting long stream response...');

  const interval = setInterval(() => {
    res.write(`data: ${Date.now()}\n\n`);  // Server-Sent Events style
  }, 1000);

  // When client disconnects mid-stream (closes tab, loses connection),
  // the underlying socket's 'close' event fires — this is OUR chance
  // to clean up resources (clear the interval!) to avoid a leak
  req.on('close', () => {
    console.log('Client disconnected — cleaning up interval');
    clearInterval(interval);  // CRITICAL: without this, interval runs forever!
  });
});

app.listen(3000, () => console.log('Streaming server on 3000'));

// WHY THIS MATTERS: if you don't listen for 'close' and clean up,
// every abandoned streaming connection leaves a dangling setInterval
// running forever — a classic Node.js memory/resource leak.
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Not cleaning up resources on socket/request close
```javascript
// WRONG: interval keeps running even after client disconnects
app.get('/leak', (req, res) => {
  setInterval(() => res.write('ping\n'), 1000);  // never cleared!
});

// CORRECT: always listen for 'close' and release resources
app.get('/no-leak', (req, res) => {
  const interval = setInterval(() => res.write('ping\n'), 1000);
  req.on('close', () => clearInterval(interval));
});
```

❌ **Mistake 2:** Assuming `'close'` always means an error occurred
```javascript
// WRONG assumption
socket.on('close', () => {
  console.log('Something went wrong!');  // not necessarily true!
});

// CORRECT: check the hadError argument
socket.on('close', (hadError) => {
  if (hadError) {
    console.log('Closed due to a transmission error');
  } else {
    console.log('Closed normally (e.g., socket.end() or client finished)');
  }
});
```

---

## 🧠 Tricky Interview Question

```javascript
const net = require('net');
const server = net.createServer((socket) => {
  socket.end('bye');  // graceful close — sends data then closes
});
server.listen(8095, () => {
  const client = net.createConnection({ port: 8095 });
  client.on('data', (d) => console.log('data:', d.toString()));
  client.on('end', () => console.log('end event'));
  client.on('close', () => console.log('close event'));
});
```

**Answer:** Output order: `data: bye`, `end event`, `close event`. Explanation: `'data'` fires when bytes arrive. `'end'` fires when the OTHER side signals no more data is coming (FIN packet, via `socket.end()`). `'close'` fires LAST, after the socket is FULLY closed on both sides (TCP connection fully torn down) — and its callback execution is associated with the Close Callbacks phase. The key distinction: `'end'` means "no more incoming data," `'close'` means "the socket resource is completely gone."

---

## ⚫ Interview Questions + Answers

**Q1: What runs in the Close Callbacks phase?**
A1: Callbacks registered via `.on('close', ...)` on sockets, servers, or other handles — particularly those that were closed abruptly (via `.destroy()`). It's the LAST phase in each event loop iteration, after Timers, Pending Callbacks, Poll, and Check.

**Q2: What's the difference between the `'end'` and `'close'` events on a socket?**
A2: `'end'` fires when the readable side of the connection has no more data (the other end sent a FIN packet) — you can still write data after this. `'close'` fires when the socket is FULLY and permanently closed (both directions done) — no further interaction is possible. `'close'` always fires after `'end'` (if `'end'` fired at all).

**Q3: Why is it important to listen for `'close'` events in production code?**
A3: To clean up associated resources — intervals, timeouts, file handles, database connections, in-memory tracking structures — that were tied to that specific connection's lifetime. Forgetting this is one of the most common causes of memory/resource leaks in long-running Node.js servers (e.g., SSE/streaming endpoints where clients disconnect but server-side timers keep running).

**Q4: Does `'close'` always indicate an error?**
A4: No. The `'close'` event callback receives a boolean `hadError` argument. A graceful disconnect (`socket.end()` on both sides) results in `hadError === false`. An abrupt disconnect due to a transmission error (e.g., connection reset) results in `hadError === true`. Always check this argument rather than assuming closure implies failure.

**Q5: How does the event loop decide whether to continue to another iteration after Close Callbacks, or exit the process?**
A5: After Phase 6 completes, Node checks if there's any remaining work: pending timers, active handles/sockets (not `.unref()`'d), or pending I/O. If none exist, the process exits naturally. If work remains, the loop goes back to Phase 1 (Timers) and continues. This is why a Node.js server with an active `server.listen()` never exits — the listening socket is an active handle keeping the loop alive.

---

## 🔷 When to Use + When Not to Use
✅ **Use `'close'` handlers when:**
- Cleaning up resources tied to a connection's lifetime (intervals, locks, counters)
- Implementing graceful shutdown logic that waits for active connections to finish

❌ **Avoid:**
- Relying on `'close'` firing synchronously right after you call `.destroy()` — it's still asynchronous, queued for the Close Callbacks phase

---

## 📊 Visual Diagram

```
CLOSE CALLBACKS PHASE (Phase 6 — LAST):
──────────────────────────────────────────────────────

  CHECK phase finishes (setImmediate callbacks done)
         │
         ▼
  CLOSE CALLBACKS PHASE
  ┌───────────────────────────────────────┐
  │  Run all 'close' event callbacks       │
  │  for sockets/handles destroyed this    │
  │  iteration                             │
  │                                        │
  │  socket.destroy() → 'close' queued here│
  └──────────────────┬──────────────────────┘
                     ▼
         Any work left? (timers, active handles, I/O)
            │Yes                    │No
            ▼                       ▼
     Loop back to Phase 1      Process exits
       (TIMERS)                naturally
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Close Callbacks | Last phase, runs 'close' event handlers | 'close' event handlers चलाने वाला last phase |
| `socket.destroy()` | Abruptly closes a connection | Connection को अचानक close करना |
| `'end'` event | No more incoming data | अब और data नहीं आएगा |
| `'close'` event | Connection fully torn down | Connection पूरी तरह बंद |
| `hadError` | Whether close was due to error | Close error की वजह से था या नहीं |

---

## ⚡ 3-Line Summary
English:
1. Close Callbacks is the final (6th) phase of each event loop iteration, running `'close'` event handlers, especially for abruptly destroyed sockets/handles.
2. `'close'` fires after `'end'`, and the `hadError` boolean tells you whether it was a graceful or error-caused closure.
3. Always clean up resources (intervals, locks, counters) tied to a connection in its `'close'` handler to avoid leaks.

Hindi:
1. Close Callbacks हर event loop iteration का last (6th) phase है, जो `'close'` event handlers चलाता है, खासकर forcefully destroyed sockets के लिए।
2. `'close'` `'end'` के बाद fire होता है, और `hadError` बताता है कि closure graceful था या error की वजह से।
3. Connection से जुड़े resources (intervals, locks, counters) हमेशा `'close'` handler में clean up करो, leak से बचने के लिए।

---

## ➡️ Next Topic
**74. Microtasks — process.nextTick** — The highest-priority queue that runs between every single phase, before Promises।
