# 71. Phase 4 — Poll
# हिंदी में: Phase 4 — Poll Phase

---

## 🔵 Simple Definition (English)
The **Poll** phase is the most important and busiest phase of the Event Loop. It does two things: (1) calculates how long it should block/wait for I/O, and (2) processes events in the **poll queue** — executing callbacks for completed I/O operations like `fs.readFile`, incoming HTTP requests, TCP data, DNS results, etc. If there's nothing else to do, Poll will actually BLOCK here waiting for new I/O events.

## 🔵 सरल परिभाषा (Hindi)
**Poll** phase Event Loop का सबसे important और busiest phase है। ये दो काम करता है: (1) कितनी देर I/O के लिए wait करना है calculate करता है, (2) **poll queue** के events process करता है — completed I/O operations जैसे `fs.readFile`, incoming HTTP requests, TCP data के callbacks run करता है। कुछ और करने को ना हो तो Poll यहीं BLOCK हो जाता है नए I/O events के लिए wait करते हुए।

---

## 🔴 Problem it Solves
```
NEED: A server must wait for incoming requests/data WITHOUT burning CPU
      in a tight busy-loop (which would waste 100% CPU doing nothing).

WITHOUT POLL PHASE (naive busy-wait):
  while (true) {
    if (hasNewRequest()) handleIt();  // CPU spins at 100% even when idle!
  }

WITH POLL PHASE:
  Poll phase blocks EFFICIENTLY using OS primitives (epoll on Linux,
  kqueue on macOS, IOCP on Windows) — the OS wakes Node up ONLY when
  actual I/O is ready. Zero CPU usage while waiting.
  → This is THE mechanism that makes Node.js efficient at handling
    thousands of concurrent connections with near-zero idle CPU cost.
```

## 🔴 यह क्यों बना? (Hindi)
```
Server को incoming requests/data के लिए wait करना होता है बिना CPU waste किए
Naive busy-wait 100% CPU use करता रहेगा even जब कुछ नहीं हो रहा
Poll phase OS primitives (epoll/kqueue/IOCP) use करके efficiently block होता है
OS तब wake करता है जब actual I/O ready हो — zero CPU idle में
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Event loop enters POLL phase
Step 2 → Calculates poll timeout: how long to wait, based on:
          - Are there setImmediate() callbacks queued? → timeout = 0 (don't block)
          - Is there a pending timer? → timeout = time until that timer
          - Otherwise → timeout = infinite (block until I/O arrives)
Step 3 → Node asks the OS (via epoll/kqueue/IOCP) "wake me when I/O is ready,
          or after [timeout]ms, whichever comes first"
Step 4 → When I/O completes (file read done, HTTP data arrived, etc.),
          OS wakes up the Poll phase
Step 5 → Node processes ALL ready callbacks in the poll queue (up to a limit,
          to avoid starving other phases)
Step 6 → If poll queue becomes empty AND setImmediate callbacks are pending
          → move immediately to CHECK phase
Step 7 → If poll queue is empty AND no setImmediate → loop checks if any
          timers are due; if so, wrap back to TIMERS phase
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. Event loop Poll phase में enter करता है
2. Poll timeout calculate करता है — setImmediate pending? तो wait नहीं; timer due है? तो उतना wait
3. OS से कहता है "I/O ready हो या timeout हो, जो पहले हो मुझे wake करो"
4. I/O complete होने पर OS wake करता है, callback queue process होती है
5. Queue खाली + setImmediate pending → Check phase में जाओ
6. Queue खाली + timer due → Timers phase में वापस जाओ
```

---

## 🟡 Real World Example
**Flipkart product listing API:** When 50,000 concurrent users hit `/api/products`, each request's DB query (`fs`/`net` level I/O under the hood) is handed off to the OS/thread-pool. The Node process's single thread sits in the Poll phase, essentially "sleeping" using `epoll_wait()` on Linux, consuming near-zero CPU, until the OS says "hey, 200 of these DB responses just came back." Then Poll wakes up, runs all 200 callbacks (sending responses), and goes back to waiting. This is why a single Node process can handle massive concurrency with low CPU usage — it's not actively polling in a loop, it's genuinely blocked/sleeping via OS-level event notification.

## 🟡 Real Example Hindi mein
**Flipkart:** 50,000 concurrent users `/api/products` hit करते हैं। हर request की DB query OS/thread-pool को handoff होती है। Node का single thread Poll phase में `epoll_wait()` से sleep करता है, near-zero CPU use करता है, जब तक OS बताए "200 responses आ गए।" फिर Poll wake होता है, सब callbacks run करता है, फिर वापस wait करता है।

---

## 💻 Code Example — Basic

```javascript
// poll-basic.js
// Run: node poll-basic.js

const fs = require('fs');

console.log('1: sync start');

// fs.readFile is async I/O — its callback runs in the POLL phase
fs.readFile(__filename, 'utf8', (err, data) => {
  console.log('3: Poll phase — file read complete, length:', data.length);
});

console.log('2: sync end');

// OUTPUT:
// 1: sync start
// 2: sync end
// 3: Poll phase — file read complete, length: <some number>
// Explanation: fs.readFile offloads the actual disk read to libuv's thread
// pool (since fs operations are blocking at the OS level). Once the read
// completes, the callback is queued, and Poll phase picks it up and runs it.
```

## 💻 Code Example — Advanced

```javascript
// poll-advanced.js — demonstrating Poll phase blocking behavior and timeout calc

const net = require('net');

console.log('Starting server — Poll phase will block here waiting for connections');

const server = net.createServer((socket) => {
  const receivedAt = Date.now();
  console.log('Poll phase woke up — new connection at', receivedAt);

  socket.on('data', (data) => {
    console.log('Poll phase processing data:', data.toString().trim());
    socket.write('ACK\n');
  });

  socket.on('end', () => socket.end());
});

server.listen(8080, () => {
  console.log('Server listening — process is essentially IDLE (near 0% CPU)');
  console.log('until a client connects. This IS the Poll phase blocking efficiently.');
});

// Demonstrate: a timer fires EVEN THOUGH the server has no connections,
// because Poll's calculated timeout respects the pending timer
setTimeout(() => {
  console.log('Timer fired — proves Poll did not block FOREVER, it respected the timer deadline');
}, 2000);

// If you connect with: nc localhost 8080
// and type something, you'll see Poll "wake up" and process it instantly.
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const app = express();

// Every incoming HTTP request Express handles is fundamentally a
// Poll-phase event: the underlying http.Server's TCP socket receives
// data, libuv's poll mechanism wakes Node, and the request handler runs.

app.get('/users/:id', (req, res) => {
  // This handler itself runs as part of Poll-phase callback execution
  // (triggered by the incoming HTTP request's socket data event)
  fetchUserFromDb(req.params.id).then((user) => {
    // The DB query's I/O completion ALSO wakes the Poll phase again
    res.json(user);
  });
});

function fetchUserFromDb(id) {
  return new Promise((resolve) => setTimeout(() => resolve({ id, name: 'Rahul' }), 50));
}

app.listen(3000, () => {
  console.log('Express server — Poll phase handles every incoming connection + DB callback');
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Running CPU-heavy synchronous work inside a Poll-phase callback
```javascript
// WRONG: blocks Poll from processing OTHER pending I/O callbacks
fs.readFile('data.json', (err, data) => {
  const parsed = JSON.parse(data);
  // Heavy synchronous loop — blocks the entire event loop, not just this callback!
  for (let i = 0; i < 1e9; i++) {}
  res.json(parsed);
});

// CORRECT: offload CPU-heavy work to a Worker Thread
const { Worker } = require('worker_threads');
fs.readFile('data.json', (err, data) => {
  const worker = new Worker('./heavy-process.js', { workerData: data });
  worker.on('message', (result) => res.json(result));
});
```

❌ **Mistake 2:** Thinking Poll always blocks indefinitely
```javascript
// WRONG assumption: "Poll waits forever for I/O no matter what"
// In reality, Poll's blocking timeout is dynamically calculated —
// if a setImmediate is queued, Poll doesn't block at all (timeout=0);
// if a timer is due soon, Poll blocks only until that timer's deadline.
```

---

## 🧠 Tricky Interview Question

```javascript
const fs = require('fs');

fs.readFile(__filename, () => {
  console.log('poll callback');
  setTimeout(() => console.log('timeout inside poll'), 0);
  setImmediate(() => console.log('immediate inside poll'));
});
```

**Answer:** Output: `poll callback`, then `immediate inside poll`, then `timeout inside poll`. Explanation: Once inside the Poll-phase callback, scheduling a `setImmediate` means it will run in the very NEXT phase (Check), which comes right after Poll. But `setTimeout(0)` must wait for the loop to cycle all the way back to the TIMERS phase (Phase 1) on the NEXT full iteration. So inside any I/O/poll callback, `setImmediate` always wins over `setTimeout(0)` — this is the one place the ordering IS guaranteed (unlike in the main script).

---

## ⚫ Interview Questions + Answers

**Q1: What happens in the Poll phase?**
A1: Two things: (1) It calculates how long to block waiting for I/O (based on pending timers and setImmediate callbacks), (2) it processes the poll queue — running callbacks for completed I/O operations (file reads, network data, etc.). It's where most "real work" callbacks actually execute in a typical Node.js server.

**Q2: Why can a single-threaded Node.js process handle thousands of concurrent connections efficiently?**
A2: Because the Poll phase uses OS-level efficient I/O notification mechanisms (`epoll` on Linux, `kqueue` on macOS/BSD, `IOCP` on Windows) instead of busy-waiting. The OS itself tracks thousands of file descriptors/sockets and wakes Node up ONLY when something is actually ready, consuming near-zero CPU while idle — this is fundamentally different from thread-per-connection models.

**Q3: Inside an I/O callback, why does `setImmediate` always run before `setTimeout(0)`?**
A3: Because Check (where setImmediate runs) is the very next phase after Poll, while Timers (where setTimeout runs) requires looping all the way back to Phase 1 on the next iteration. So scheduling from inside a Poll callback guarantees setImmediate fires first — this guarantee does NOT hold in the main module script (outside any I/O callback), where the order is less deterministic.

**Q4: What determines how long Poll phase blocks for?**
A4: (1) If `setImmediate()` callbacks are already queued, Poll doesn't block at all (processes immediately, timeout=0). (2) If there are pending timers, Poll blocks only up to the time remaining until the nearest timer. (3) If neither, Poll can block indefinitely, waiting purely for I/O (fully "sleeping" via OS primitives) — until actual I/O arrives.

**Q5: What's a real symptom of "the Poll phase is starved" in production, and how do you detect it?**
A5: If synchronous or microtask work (e.g., runaway `process.nextTick` recursion, or long-running sync CPU code) keeps the event loop busy, Poll never gets a chance to process incoming connections or I/O completions — requests pile up, latency spikes, health checks start timing out. Detect it with event-loop-lag monitoring tools (`perf_hooks` `monitorEventLoopDelay()`, or APM tools like New Relic/Datadog that track event loop lag metrics).

---

## 🔷 When to Use + When Not to Use
✅ **Relevant to you when:**
- Reasoning about why your server feels "slow" under load (Poll starvation from blocking code)
- Deciding whether `setImmediate` vs `setTimeout(0)` ordering matters inside your I/O callbacks

❌ **Not directly controllable:**
- You don't manually trigger Poll — it's driven by actual I/O operations you initiate (fs, net, http, dns)

---

## 📊 Visual Diagram

```
POLL PHASE — THE MAIN WORKHORSE:
──────────────────────────────────────────────────────

  Enter POLL phase
         │
         ▼
  Calculate blocking timeout:
    setImmediate queued? ──Yes──► timeout = 0 (don't block)
         │No
         ▼
    Timer pending? ──Yes──► timeout = time until timer
         │No
         ▼
    timeout = INFINITE (block until I/O, pure sleep)
         │
         ▼
  OS-level wait: epoll_wait() / kqueue / IOCP
  (near-ZERO CPU usage while blocked)
         │
         ▼
  I/O ready! (file read done, socket data arrived, etc.)
         │
         ▼
  Process ALL ready callbacks in poll queue
         │
         ▼
  Queue empty + setImmediate pending? ──► go to CHECK phase immediately
  Queue empty + no setImmediate? ──► loop back toward TIMERS
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Poll Phase | Phase that waits for and processes I/O | I/O wait और process करने वाला phase |
| epoll/kqueue/IOCP | OS-level efficient I/O notification | OS का efficient I/O notification mechanism |
| Poll Queue | Queue of ready I/O callbacks | Ready I/O callbacks की queue |
| Poll Timeout | How long Poll can block | Poll कितनी देर block हो सकता है |

---

## ⚡ 3-Line Summary
English:
1. Poll is the busiest Event Loop phase — it calculates a blocking timeout and processes callbacks for completed I/O (fs, net, http).
2. It uses efficient OS primitives (epoll/kqueue/IOCP) to block with near-zero CPU, waking only when real I/O arrives.
3. Inside any Poll-phase callback, `setImmediate` is guaranteed to run before `setTimeout(0)` because Check is the immediate next phase.

Hindi:
1. Poll सबसे busy Event Loop phase है — blocking timeout calculate करता है और completed I/O (fs, net, http) के callbacks process करता है।
2. Efficient OS primitives (epoll/kqueue/IOCP) से near-zero CPU पर block होता है, सिर्फ real I/O आने पर wake होता है।
3. किसी भी Poll-phase callback के अंदर `setImmediate` हमेशा `setTimeout(0)` से पहले चलता है क्योंकि Check तुरंत अगला phase है।

---

## ➡️ Next Topic
**72. Phase 5 — Check (setImmediate)** — How setImmediate callbacks run right after Poll, and why it's different from setTimeout(0)।
