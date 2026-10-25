# 219. Heap Snapshots
# हिंदी में: Heap Snapshots — Memory में मौजूद सभी Objects का Snapshot

---

## 🔵 Simple Definition (English)
A **heap snapshot** is a complete point-in-time capture of every JavaScript object currently alive in memory — their types, sizes, and most importantly, the **reference chains** showing what's keeping each object alive. Taking multiple snapshots over time and comparing them is the primary technique for pinpointing exactly which objects are leaking and why.

## 🔵 सरल परिभाषा (Hindi)
**Heap snapshot** memory में इस समय alive सभी JavaScript objects का पूरा capture होता है — उनके types, sizes, और सबसे ज़रूरी, वो **reference chains** जो हर object को alive रखते हैं। समय के साथ कई snapshots लेना और उन्हें compare करना ये पहचानने की मुख्य technique है कि exactly कौन से objects leak कर रहे हैं और क्यों।

---

## 🔴 Problem it Solves
Knowing memory usage is growing (via `process.memoryUsage()`) tells you THAT there's a leak, but not WHAT is leaking or WHY it's not being garbage collected. Heap snapshots answer the "what" and "why" — they let you browse the actual object graph, see which objects have grown in count between two points in time, and trace the exact chain of references (Retainers) holding them alive, pinpointing the specific line of code responsible.

## 🔴 यह क्यों बना? (Hindi)
`process.memoryUsage()` से पता चलता है कि memory बढ़ रही है, पर ये नहीं बताता कि क्या leak हो रहा है या क्यों garbage collect नहीं हो रहा। Heap snapshots "what" और "why" दोनों का जवाब देते हैं — actual object graph browse करने देते हैं, देखते हैं कि दो समय points के बीच कौन से objects count में बढ़े, और exact reference chain (Retainers) trace करते हैं जो उन्हें alive रखती है — code की exact line पहचान में आती है।

---

## 🟢 How it Works — Step by Step

Step 1 → Run the app with `node --inspect app.js` (or `--inspect-brk` to pause at start)
Step 2 → Open Chrome and navigate to `chrome://inspect` → click "inspect" under your target to open DevTools connected to your Node process
Step 3 → Go to the **Memory** tab, select "Heap snapshot", click "Take snapshot" — this is **Snapshot 1** (baseline, taken BEFORE the suspected leaky operation)
Step 4 → Exercise the suspected leaky code path (make requests repeatedly, run the workload several times)
Step 5 → Take **Snapshot 2** after the workload. Switch the view dropdown to "Comparison" — this shows objects added between snapshot 1 and 2, sorted by count/size delta
Step 6 → Click into a growing object type → check the **Retainers** panel at the bottom — it shows the chain of references keeping that object alive, usually pointing straight at the leaking variable/listener/cache

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → App को `node --inspect app.js` से चलाओ (या शुरुआत में pause के लिए `--inspect-brk`)
Step 2 → Chrome खोलो, `chrome://inspect` पर जाओ → "inspect" click करो DevTools खोलने के लिए
Step 3 → **Memory** tab में जाओ, "Heap snapshot" select करो, "Take snapshot" click करो — ये **Snapshot 1** है (leaky operation से पहले का baseline)
Step 4 → Suspected leaky code path exercise करो (बार-बार requests भेजो, workload कई बार चलाओ)
Step 5 → Workload के बाद **Snapshot 2** लो। View dropdown को "Comparison" पर switch करो — ये snapshot 1 और 2 के बीच added objects count/size delta के साथ दिखाता है
Step 6 → किसी बढ़ते object type पर click करो → नीचे **Retainers** panel check करो — ये reference chain दिखाता है जो उस object को alive रखती है, आम तौर पर सीधे leaking variable/listener/cache की तरफ इशारा करती है

---

## 🟡 Real World Example
**Amazon India's inventory-sync service** was slowly leaking memory, crashing every 12 hours. Taking two heap snapshots 30 minutes apart in staging under simulated load showed the "Comparison" view: `Closure` objects had grown from 200 to 45,000, and clicking into them showed Retainers pointing to a `setInterval` callback inside a `syncInventoryForWarehouse()` function that was being called repeatedly without clearing the previous interval — each call created a NEW interval (and its closure) while the old ones kept running forever. The snapshot comparison made the exact leaking line immediately obvious, something `process.memoryUsage()` alone could never have shown.

## 🟡 Real Example Hindi mein
**Amazon India की inventory-sync service** धीरे-धीरे memory leak कर रही थी, हर 12 घंटे crash हो रही थी। Staging में simulated load के साथ 30 मिनट के अंतर पर दो heap snapshots लेने पर "Comparison" view में दिखा: `Closure` objects 200 से 45,000 तक बढ़ गए थे, और उन पर click करने पर Retainers एक `setInterval` callback की तरफ इशारा कर रहे थे जो `syncInventoryForWarehouse()` function के अंदर था और बिना पुराना interval clear किए बार-बार call हो रहा था — हर call एक NEW interval बनाती थी जबकि पुराने भी हमेशा के लिए चलते रहते थे।

---

## 💻 Code Example — Basic

```javascript
// heap-snapshot-demo.js — a deliberately leaky endpoint to practice snapshotting
const express = require('express');
const app = express();

const cache = {}; // unbounded cache — our leak for this demo

app.get('/cache-item/:id', (req, res) => {
  const id = req.params.id;
  // BAD: stores a NEW large object per unique id, never evicted
  if (!cache[id]) {
    cache[id] = {
      id,
      data: new Array(100000).fill('x'), // 100k-element array per entry
      createdAt: new Date(),
    };
  }
  res.json({ cached: true, totalCached: Object.keys(cache).length });
});

app.listen(3000);

// To practice snapshotting this leak:
// 1. node --inspect heap-snapshot-demo.js
// 2. chrome://inspect → open DevTools → Memory tab → "Take snapshot" (Snapshot 1)
// 3. for i in {1..5000}; do curl -s "localhost:3000/cache-item/$i" > /dev/null; done
// 4. Take another snapshot (Snapshot 2) → switch to "Comparison" view
// 5. You'll see thousands of new Array/Object entries added — click one,
//    check Retainers → traces back to the module-level `cache` object
```

## 💻 Code Example — Advanced

```javascript
// programmatic-heap-snapshot.js — taking snapshots from code (no manual DevTools steps)
// npm install heapdump (classic) OR use v8.writeHeapSnapshot() (built-in, Node 11.13+)
const v8 = require('v8');
const fs = require('fs');

function takeHeapSnapshot(label) {
  // v8.writeHeapSnapshot() is BUILT INTO Node — no extra dependency needed
  const filename = `./heap-${label}-${Date.now()}.heapsnapshot`;
  v8.writeHeapSnapshot(filename);
  console.log(`Heap snapshot written: ${filename}`);
  return filename;
}

// Trigger snapshots via signals — useful in production without code changes
process.on('SIGUSR2', () => {
  // Run this in another terminal: kill -USR2 <node_process_pid>
  takeHeapSnapshot('manual-trigger');
});

// Or trigger via an admin-only HTTP endpoint for remote debugging
const express = require('express');
const app = express();

app.post('/admin/heap-snapshot', requireAdmin, (req, res) => {
  const filename = takeHeapSnapshot('admin-request');
  res.json({ message: 'Snapshot written', filename });
  // Download the .heapsnapshot file and open it in Chrome DevTools'
  // Memory tab (drag-and-drop the file into the Profiles list) to analyze
});

// ─── AUTOMATED LEAK DETECTION PATTERN ─────────────────────────────────────
// Take snapshots automatically at intervals and track growth of a specific
// constructor's instance count, alerting if it grows unbounded
let previousCount = 0;

function checkForLeaks() {
  const stats = v8.getHeapStatistics();
  const usedMB = stats.used_heap_size / 1024 / 1024;
  console.log(`Current heap used: ${usedMB.toFixed(1)}MB`);

  // In a real setup, you'd parse snapshot files with a library like
  // 'heap-snapshot-parser' to count specific object types programmatically
}

setInterval(checkForLeaks, 60_000);

function requireAdmin(req, res, next) {
  if (req.headers['x-admin-key'] !== process.env.ADMIN_KEY) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  next();
}
```

---

## 🟠 Express.js Integration

```javascript
// routes/admin/diagnostics.js — safely exposing heap diagnostics in production
const express = require('express');
const v8 = require('v8');
const router = express.Router();

// Protect ALL diagnostic routes with strict admin auth — never expose publicly
router.use((req, res, next) => {
  if (req.headers['x-admin-key'] !== process.env.ADMIN_SECRET_KEY) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  next();
});

router.get('/heap-stats', (req, res) => {
  // Quick numeric stats — no full snapshot needed for a high-level check
  const stats = v8.getHeapStatistics();
  res.json({
    totalHeapSizeMB: (stats.total_heap_size / 1024 / 1024).toFixed(1),
    usedHeapSizeMB: (stats.used_heap_size / 1024 / 1024).toFixed(1),
    heapLimitMB: (stats.heap_size_limit / 1024 / 1024).toFixed(1),
    percentUsed: ((stats.used_heap_size / stats.heap_size_limit) * 100).toFixed(1) + '%',
  });
});

router.post('/heap-snapshot', (req, res) => {
  const filename = `/tmp/heap-${Date.now()}.heapsnapshot`;
  v8.writeHeapSnapshot(filename);
  res.download(filename); // let the admin download it directly for local analysis
});

module.exports = router;
// Mount: app.use('/admin/diagnostics', require('./routes/admin/diagnostics'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Taking only ONE snapshot and trying to spot a leak from it alone
```javascript
// WRONG: a single snapshot shows what's alive NOW, but you have nothing
// to compare against — you can't tell what's "normal" vs "growing"

// CORRECT: always take at least 2 snapshots — one baseline, one after
// exercising the suspected code path — and use the "Comparison" view
```

❌ Mistake 2: Taking heap snapshots directly in a live, high-traffic production process without care
```javascript
// WRONG: writeHeapSnapshot() PAUSES the event loop while it serializes the
// entire heap — on a large heap (GBs), this can take seconds, causing
// a visible latency spike / dropped requests on a busy production server

// CORRECT: take snapshots during low-traffic windows, on a canary/staging
// instance under similar load, or accept a brief controlled pause for
// critical debugging, with monitoring aware that a short spike is expected
```

---

## 🧠 Tricky Interview Question

**Q: You take a heap snapshot and see 50,000 `(closure)` objects retained by a single `Timeout` object. What does this tell you, and how do you fix it?**
Answer: This is the classic signature of a **timer leak**: a single `setInterval`/`setTimeout` callback (shown as a `Timeout` object in the snapshot) is holding a closure that itself references 50,000 other objects — meaning each tick of that interval is likely ACCUMULATING data into some structure (array, Map) captured in its closure scope, rather than processing and releasing it. The `Timeout` is the root "Retainer" keeping the entire chain alive, and since the interval was never cleared (`clearInterval`), nothing can ever be garbage collected. Fix: identify what's being accumulated inside that interval's callback, bound or clear it per tick, and ensure `clearInterval()` is called when the work is truly done.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `process.memoryUsage()` and a heap snapshot?
A1: `process.memoryUsage()` gives aggregate NUMBERS (RSS, heapUsed, heapTotal) — useful for noticing a leak trend exists, but gives zero detail on WHAT is leaking. A heap snapshot gives the full OBJECT GRAPH — every live object, its type, size, and reference chain — letting you pinpoint the exact leaking object and what's retaining it.

Q2: What is the "Comparison" view in Chrome DevTools' Memory tab used for?
A2: It shows the DELTA between two heap snapshots — objects newly allocated (and not freed) between snapshot A and snapshot B, sorted by count or size. This isolates genuinely leaking/growing object types from the normal "background noise" of objects that are always present, making it far easier to spot the real leak than browsing a single snapshot's full list.

Q3: What does the "Retainers" panel show, and why is it the key to fixing a leak?
A3: For a selected object, Retainers shows the chain of references FROM GC roots (global scope, active closures, etc.) down to that object — i.e., exactly WHY the garbage collector can't free it. Following this chain typically leads straight to the leaking variable (a module-level array, an un-removed listener, an active timer's closure) — this is the "why" that raw memory numbers can never show.

Q4: Is `v8.writeHeapSnapshot()` safe to call in production?
A4: It works but PAUSES the event loop while serializing the heap to disk — on a large heap this can take noticeable time (hundreds of ms to several seconds), causing a latency spike for in-flight requests. It's best used sparingly, during low-traffic windows, or on a dedicated diagnostic/canary instance rather than continuously on the main production fleet.

Q5: How do "shallow size" and "retained size" differ in a heap snapshot's object listing?
A5: "Shallow size" is the memory the object itself occupies directly (its own properties, not what it references). "Retained size" is the TOTAL memory that would be freed if that object were garbage collected — including everything it exclusively keeps alive (like a Map holding thousands of entries: the Map's shallow size is small, but its retained size includes every entry). Retained size is usually the more important number when hunting for the biggest memory offenders.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You've confirmed memory is growing (via `process.memoryUsage()` trend) and need to find the EXACT cause
- Comparing before/after a suspected fix to confirm the leak is actually resolved
- Investigating which specific object type/module is responsible for high memory usage

❌ Avoid when:
- You haven't yet confirmed there's an actual trend of growing memory (don't snapshot-hunt prematurely)
- On a live, high-traffic production instance without accepting the brief event-loop pause risk (use staging/canary instead)

---

## 📊 Visual Diagram
```
HEAP SNAPSHOT COMPARISON WORKFLOW:
─────────────────────────────────────────────────
  Snapshot 1 (baseline)          Snapshot 2 (after load)
  ┌──────────────────┐           ┌──────────────────┐
  │ Closure: 200      │           │ Closure: 45,000    │ ← grew 225x!
  │ Array: 1,500       │           │ Array: 1,520        │ ← stable, not leak
  │ Object: 3,000       │           │ Object: 3,010         │ ← stable, not leak
  └──────────────────┘           └──────────────────┘
               │                           │
               └──── COMPARISON VIEW ──────┘
                           │
                           ▼
           Click "Closure" → see 45,000 entries
                           │
                           ▼
            RETAINERS panel for one instance:
            Closure → Timeout (setInterval) → module scope
                           │
                           ▼
            Found it: an interval was never cleared!
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Heap snapshot | Full capture of live objects in memory | Memory के live objects का capture |
| Comparison view | Diff between two snapshots | दो snapshots के बीच का diff |
| Retainers | Chain of references keeping an object alive | Object को alive रखने वाली reference chain |
| Shallow size | Memory the object itself occupies | Object की अपनी memory |
| Retained size | Total memory freed if object is collected | Object collect होने पर कुल freed memory |
| v8.writeHeapSnapshot() | Built-in programmatic snapshot API | Built-in snapshot API |

---

## ⚡ 3-Line Summary
English:
1. A heap snapshot captures every live object in memory along with its reference chains, letting you see exactly WHAT is leaking and WHY it can't be garbage collected.
2. Always take at least two snapshots (before/after the suspected leaky workload) and use the "Comparison" view to isolate genuinely growing object types.
3. The "Retainers" panel traces the exact reference chain to the leak's root cause — usually an un-removed listener, uncleared timer, or unbounded cache.

Hindi:
1. Heap snapshot memory में मौजूद हर live object को उसकी reference chains के साथ capture करता है — exactly दिखाता है कि क्या leak हो रहा है और क्यों garbage collect नहीं हो पाता।
2. हमेशा कम से कम दो snapshots लो (suspected leaky workload से पहले/बाद) और genuinely बढ़ते object types को isolate करने के लिए "Comparison" view use करो।
3. "Retainers" panel leak के root cause तक exact reference chain trace करता है — आम तौर पर न हटाया गया listener, clear न हुआ timer, या unbounded cache।

---

## ➡️ Next Topic
**220. Caching Strategies** — repeated expensive operations को बार-बार न चलाकर response time और load कम करना।
