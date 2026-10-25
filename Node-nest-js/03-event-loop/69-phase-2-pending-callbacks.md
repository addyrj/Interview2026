# 69. Phase 2 — Pending Callbacks
# हिंदी में: Phase 2 — Pending Callbacks Phase

---

## 🔵 Simple Definition (English)
The **Pending Callbacks** phase (also called "Pending I/O callbacks") executes I/O callbacks that were **deferred from the previous loop iteration** — typically certain system-level error callbacks like a TCP connection getting `ECONNREFUSED`. It's a smaller, less commonly discussed phase compared to Poll or Timers, but it exists to handle specific OS-level callback deferrals.

## 🔵 सरल परिभाषा (Hindi)
**Pending Callbacks** phase (जिसे "Pending I/O callbacks" भी कहते हैं) उन I/O callbacks को execute करता है जो **पिछले loop iteration से deferred** हुए थे — जैसे कुछ system-level error callbacks (जैसे TCP connection पर `ECONNREFUSED`)। ये Poll या Timers से कम discussed phase है, लेकिन कुछ OS-level callback deferrals handle करने के लिए मौजूद है।

---

## 🔴 Problem it Solves
```
PROBLEM: Some I/O operations complete with an ERROR at the OS level,
but executing that error callback IMMEDIATELY (in the same iteration)
could interfere with ongoing poll-phase processing.

EXAMPLE: A TCP socket tries to connect and gets refused (ECONNREFUSED).
libuv needs to report this error, but defers it to run in a controlled,
predictable phase — the NEXT loop iteration's "Pending Callbacks" phase —
rather than immediately interrupting whatever else is happening.

WITHOUT THIS PHASE:
  Error callbacks could fire at unpredictable/inconsistent times,
  mixed in with normal I/O completions, making ordering guarantees harder.

WITH PENDING CALLBACKS PHASE:
  Deferred OS-level callbacks get a dedicated, predictable execution point
  right after Timers, before the event loop touches new I/O (Poll phase).
```

## 🔴 यह क्यों बना? (Hindi)
```
कुछ I/O operations OS level पर ERROR के साथ complete होते हैं
(जैसे TCP connection ECONNREFUSED)
इन्हें तुरंत handle करना ongoing poll processing को disturb कर सकता है
इसलिए libuv इन्हें अगले iteration के "Pending Callbacks" phase में defer करता है
एक predictable, dedicated execution point मिलता है
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → libuv performs an I/O operation (e.g., TCP connect attempt)
Step 2 → The OS reports an error for that operation (e.g., connection refused)
Step 3 → Instead of running the error callback immediately, libuv QUEUES it
          as a "pending callback" to be run in a later/next loop iteration
Step 4 → Event loop finishes current iteration's work
Step 5 → Next iteration: Timers phase runs first
Step 6 → Then PENDING CALLBACKS phase runs — executes the queued error callbacks
Step 7 → Event loop proceeds to Idle/Prepare → Poll → Check → Close phases
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. libuv कोई I/O operation करता है (जैसे TCP connect)
2. OS उसमें error report करता है (जैसे connection refused)
3. libuv उस error callback को तुरंत नहीं, बल्कि "pending" queue में डालता है
4. अगले iteration में Timers के बाद Pending Callbacks phase में वो callback run होता है
5. फिर आगे Poll → Check → Close phases चलते हैं
```

---

## 🟡 Real World Example
**Amazon microservice resilience:** When Amazon's order-service tries to connect to a downstream inventory-service that's temporarily down (connection refused), the TCP error (`ECONNREFUSED`) that libuv detects is reported through the Pending Callbacks phase. The application's error handler (attached via `socket.on('error', ...)`) then triggers a circuit-breaker pattern — marking the inventory-service as unhealthy and failing fast on subsequent requests instead of waiting for more TCP timeouts.

## 🟡 Real Example Hindi mein
**Amazon:** जब order-service downstream inventory-service से connect नहीं हो पाता (connection refused), वो TCP error Pending Callbacks phase से report होता है। App का error handler (`socket.on('error')`) circuit-breaker pattern trigger करता है — service को unhealthy mark करके आगे requests fail-fast कर देता है।

---

## 💻 Code Example — Basic

```javascript
// pending-callbacks-demo.js
// Run: node pending-callbacks-demo.js
// (We don't have a server listening on port 9999 — triggers ECONNREFUSED)

const net = require('net');

console.log('1: sync start');

const socket = net.createConnection({ port: 9999, host: 'localhost' });

// This error callback execution is related to the Pending Callbacks phase
// internally — libuv defers reporting certain connection errors
socket.on('error', (err) => {
  console.log('3: connection error:', err.code);  // 'ECONNREFUSED'
});

console.log('2: sync end');

// OUTPUT:
// 1: sync start
// 2: sync end
// 3: connection error: ECONNREFUSED
// The error isn't synchronous — it goes through libuv's I/O error reporting
// mechanism, which (depending on platform/libuv version) can be processed
// in the Pending Callbacks phase before the Poll phase begins.
```

## 💻 Code Example — Advanced

```javascript
// pending-callbacks-advanced.js — Circuit breaker pattern using connection errors

const net = require('net');

class CircuitBreaker {
  constructor(host, port) {
    this.host = host;
    this.port = port;
    this.failureCount = 0;
    this.isOpen = false;        // true = circuit open, stop trying
    this.failureThreshold = 3;  // open circuit after 3 consecutive failures
  }

  async checkConnection() {
    if (this.isOpen) {
      console.log('Circuit OPEN — skipping connection attempt (fail fast)');
      return false;
    }

    return new Promise((resolve) => {
      const socket = net.createConnection({ host: this.host, port: this.port });

      socket.once('connect', () => {
        console.log('Connection succeeded — resetting failure count');
        this.failureCount = 0;  // reset on success
        socket.end();
        resolve(true);
      });

      // This error handler receives errors that libuv has processed
      // (deferred reporting ensures consistent ordering with other I/O)
      socket.once('error', (err) => {
        this.failureCount++;
        console.log(`Connection failed (${err.code}), failure count: ${this.failureCount}`);

        if (this.failureCount >= this.failureThreshold) {
          this.isOpen = true;
          console.log('Circuit breaker OPENED — too many failures');
          // Auto-reset after a cooldown period
          setTimeout(() => {
            this.isOpen = false;
            this.failureCount = 0;
            console.log('Circuit breaker reset — will retry');
          }, 10_000);
        }
        resolve(false);
      });
    });
  }
}

(async () => {
  const breaker = new CircuitBreaker('localhost', 9999);  // nothing listening here
  for (let i = 0; i < 4; i++) {
    await breaker.checkConnection();
    await new Promise((r) => setTimeout(r, 500));
  }
})();
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const net = require('net');
const app = express();

// Express relies on pending-callback-style error handling under the hood
// whenever it establishes outbound connections (e.g., proxying to a DB or microservice)
app.get('/check-upstream', (req, res) => {
  const socket = net.createConnection({ port: 5433, host: 'db.internal' });

  socket.once('connect', () => {
    socket.end();
    res.json({ upstream: 'reachable' });
  });

  // Deferred error reporting (pending callbacks phase under the hood)
  // surfaces here as a normal event — Express code doesn't need to know
  // about the internal phase, just handle the error event correctly
  socket.once('error', (err) => {
    res.status(503).json({ upstream: 'unreachable', reason: err.code });
  });
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Not attaching an `'error'` listener on sockets, expecting graceful failure
```javascript
// WRONG: no error handler — process crashes on ECONNREFUSED
const socket = net.createConnection({ port: 9999 });
// Node will throw uncaught exception when the connection fails!

// CORRECT: always listen for errors
const socket = net.createConnection({ port: 9999 });
socket.on('error', (err) => console.error('Failed:', err.code));
```

❌ **Mistake 2:** Assuming Pending Callbacks phase behaves the same as Poll phase
```javascript
// WRONG assumption: "all I/O callbacks run in the same phase"
// Pending Callbacks is specifically for DEFERRED error-style callbacks from
// the previous iteration; normal successful I/O completions run in POLL phase.
// They are conceptually and timing-wise different — don't rely on them
// interleaving in a specific predictable order with Poll-phase callbacks
// in your application logic; instead just correctly handle both 'connect'
// and 'error' events without assuming WHICH phase triggers them.
```

---

## 🧠 Tricky Interview Question

```javascript
const net = require('net');
console.log('A');
const socket = net.createConnection({ port: 54321 }); // nothing listening
socket.on('error', () => console.log('B'));
setTimeout(() => console.log('C'), 0);
console.log('D');
```

**Answer:** Output: `A`, `D`, then `B` and `C` in an order that can vary slightly by platform/timing but is typically `C` (timer, Phase 1) before `B` (pending callback / error, later phase) — because Timers phase (Phase 1) comes before Pending Callbacks (Phase 2) in the event loop cycle, assuming both become ready in roughly the same iteration. In practice, the exact interleaving of connection-refused errors vs timers is not something application code should depend on — the key interview point is recognizing `A`/`D` (sync) always come first, and `B`/`C` are both deferred.

---

## ⚫ Interview Questions + Answers

**Q1: What runs in the Pending Callbacks phase?**
A1: I/O callbacks deferred from the previous loop iteration — most notably certain low-level TCP error callbacks (like `ECONNREFUSED`) that libuv chooses to execute at a predictable point rather than immediately. It's a smaller, often-overlooked phase compared to Timers, Poll, and Check.

**Q2: How is Pending Callbacks different from the Poll phase?**
A2: Poll phase handles NEW I/O events — actively retrieving new completed I/O operations and executing their callbacks (and it's where the event loop can "block" waiting for I/O if nothing else is queued). Pending Callbacks specifically handles a smaller category of DEFERRED callbacks (mostly error-related) carried over from the prior iteration. Poll is the main workhorse phase; Pending Callbacks is a narrower, specialized one.

**Q3: Why doesn't libuv just run the error callback immediately when the error occurs?**
A3: To maintain predictable, consistent ordering guarantees within the event loop's phase-based execution model. Running error callbacks immediately (interrupting whatever phase is currently executing) would break the event loop's deterministic phase-by-phase execution and make reasoning about callback order much harder for both Node internals and application developers.

**Q4: Do application developers usually need to think about this phase directly?**
A4: Rarely. Most developers just attach `.on('error', ...)` handlers and don't need to reason about WHICH phase the callback executes in. Understanding this phase mainly matters for: (1) deep debugging of event loop timing issues, (2) interview questions about the full 6-phase model, (3) understanding libuv/Node internals for contributing to core or writing native addons.

**Q5: What happens if a socket's error event has no listener?**
A5: Node treats it as an uncaught exception and crashes the process (unless a global `process.on('uncaughtException')` handler is present, which is generally discouraged as the primary error-handling strategy). This is why EVERY socket/stream that can error must have an `'error'` listener attached — it's one of Node's strictest conventions.

---

## 🔷 When to Use + When Not to Use
✅ **Relevant when:**
- Deep-diving into libuv/event-loop internals for interviews or debugging
- Writing low-level networking code with `net`/`dgram` where connection errors matter

❌ **Not something you directly control:**
- You can't "choose" to use the Pending Callbacks phase — it's an internal libuv mechanism; you just need to correctly handle `'error'` events in your code

---

## 📊 Visual Diagram

```
PENDING CALLBACKS PHASE (Phase 2):
──────────────────────────────────────────────────────

  Previous Iteration:
  TCP connect attempt → OS reports ECONNREFUSED
         │
         ▼
  libuv DEFERS this error callback (doesn't run immediately)
         │
         ▼
  ── Loop iteration ends ──
         │
         ▼
  NEXT Iteration:
  ┌───────────────────┐
  │ 1. TIMERS          │
  └─────────┬──────────┘
            ▼
  ┌───────────────────┐
  │ 2. PENDING         │  ← deferred error callback runs HERE
  │    CALLBACKS       │
  └─────────┬──────────┘
            ▼
  ┌───────────────────┐
  │ 3. IDLE/PREPARE    │
  └─────────┬──────────┘
            ▼
  ┌───────────────────┐
  │ 4. POLL            │  ← normal successful I/O runs HERE
  └────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pending Callbacks | Phase for deferred I/O error callbacks | Deferred I/O error callbacks का phase |
| ECONNREFUSED | TCP connection refused error | TCP connection refuse होने का error |
| libuv | C library managing async I/O for Node | Node का async I/O library |
| Deferred Callback | Callback delayed to a later iteration | बाद के iteration में चलने वाला callback |

---

## ⚡ 3-Line Summary
English:
1. Pending Callbacks is Phase 2 of the event loop — it runs I/O error callbacks (like `ECONNREFUSED`) deferred from the previous iteration.
2. It's distinct from the Poll phase, which handles new, successful I/O completions.
3. Application code rarely needs to reason about this phase directly — just always attach `.on('error', ...)` handlers on sockets/streams.

Hindi:
1. Pending Callbacks Event Loop का Phase 2 है — पिछले iteration से deferred I/O error callbacks (जैसे `ECONNREFUSED`) यहाँ run होते हैं।
2. ये Poll phase से अलग है, जो नए successful I/O completions handle करता है।
3. Application code को इस phase की चिंता करने की जरूरत नहीं — बस हर socket/stream पर `.on('error')` handler जरूर लगाओ।

---

## ➡️ Next Topic
**70. Phase 3 — Idle + Prepare** — The internal-only phases that run just before Poll।
