# 48. Readable Streams
# हिंदी में: Readable Streams — Data Source को Chunks में Read करना

---

## 🔵 Simple Definition (English)
A **Readable stream** is a source of data that you consume in chunks instead of all at once — e.g. `fs.createReadStream()`, `http.IncomingMessage` (the `req` object), `process.stdin`. It operates in two modes: **paused** (you pull data with `.read()`) and **flowing** (data pushed to you automatically via `'data'` events). It's an `EventEmitter` under the hood, extended with stream-specific behavior like backpressure and piping.

## 🔵 सरल परिभाषा (Hindi)
**Readable stream** data का एक source है जिसे आप पूरा नहीं, chunks में consume करते हैं — जैसे `fs.createReadStream()`, `http.IncomingMessage` (`req` object), `process.stdin`। यह दो modes में काम करता है: **paused** (आप `.read()` से data खींचते हो) और **flowing** (data automatically `'data'` events से push होता है)। यह अंदर से `EventEmitter` है, stream-specific behavior (backpressure, piping) के साथ extended।

---

## 🔴 Problem it Solves
Reading an entire large data source into memory before processing (`fs.readFileSync`) doesn't scale — a 10GB file crashes with an out-of-memory error, and even for smaller files, you can't start processing until the ENTIRE read finishes (adding latency). Readable streams let consumers start processing the FIRST chunk the moment it arrives, keep memory bounded to the chunk size, and naturally support backpressure (slowing down the source if the consumer can't keep up).

## 🔴 यह क्यों बना? (Hindi)
पूरा data source memory में load करना (`fs.readFileSync`) scale नहीं करता — 10GB file crash कर देती है, और छोटी files के लिए भी पूरा read खत्म होने तक processing शुरू नहीं हो सकती (latency बढ़ती है)। Readable streams consumer को पहला chunk आते ही process करने देते हैं, memory chunk size तक bounded रहती है, और backpressure naturally support होता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Creation: `fs.createReadStream(path, options)` — options include `highWaterMark` (buffer size, default 64KB) and `encoding` (if set, chunks are strings; otherwise Buffers).
Step 2 → **Flowing mode**: attach a `'data'` listener — stream automatically starts reading and emitting chunks as fast as it can: `stream.on('data', chunk => ...)`.
Step 3 → **Paused mode** (default until a `'data'` listener is added): call `stream.read()` manually to pull a chunk when YOU'RE ready — gives more control over pacing.
Step 4 → `'end'` event fires when there's no more data; `'error'` fires on failure (file not found, permission denied).
Step 5 → `.pipe(destination)` is the most common pattern — automatically manages flowing mode AND backpressure (pausing/resuming the source based on the destination's capacity).
Step 6 → Custom Readable: extend `stream.Readable` and implement `_read(size)`, calling `this.push(chunk)` to supply data, and `this.push(null)` to signal end.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Creation: `fs.createReadStream()` — options में `highWaterMark` (buffer size, default 64KB), `encoding`।
Step 2 → **Flowing mode**: `'data'` listener attach करो — stream automatically chunks emit करने लगता है।
Step 3 → **Paused mode** (default): `stream.read()` manually call करो जब आप ready हो — ज़्यादा control।
Step 4 → `'end'` event — data खत्म; `'error'` — failure पर।
Step 5 → `.pipe(destination)` — flowing mode और backpressure दोनों automatically manage करता है।
Step 6 → Custom Readable: `stream.Readable` extend करो, `_read(size)` implement करो, `this.push(chunk)` से data दो, `this.push(null)` से end signal करो।

---

## 🟡 Real World Example
**Zomato's order export feature:** A restaurant owner clicks "Export last year's orders as CSV." Instead of loading 2 million order rows into memory, the backend creates a database cursor as a Readable stream (`Order.find().cursor()` in Mongoose), reads it in paused mode row-by-row, transforms each to a CSV line, and pipes directly to the HTTP response. Memory stays flat regardless of whether it's 1,000 or 2,000,000 orders — the Readable stream is what makes this possible.

## 🟡 Real Example Hindi mein
**Zomato का order export feature:** Restaurant owner "last year के orders CSV में export करो" click करता है। 2 million rows memory में load करने की जगह, backend database cursor को Readable stream के रूप में use करता है, row-by-row read करके CSV line बनाता है, directly HTTP response में pipe करता है। Memory flat रहती है, चाहे 1,000 orders हों या 2,000,000।

---

## 💻 Code Example — Basic
```javascript
// readable-basics.js
const fs = require('fs');
const { Readable } = require('stream');

// 1. FLOWING MODE -- data pushed to you via 'data' event
const readStream = fs.createReadStream('./sample.txt', { encoding: 'utf8' });

readStream.on('data', (chunk) => {
  console.log('Received chunk of length:', chunk.length);
});
readStream.on('end', () => console.log('No more data - stream ended'));
readStream.on('error', (err) => console.error('Stream error:', err.message));

// 2. PAUSED MODE -- manually pull data with .read()
const readStream2 = fs.createReadStream('./sample.txt');
readStream2.on('readable', () => {
  // 'readable' event fires when data is available to be .read()
  let chunk;
  while ((chunk = readStream2.read()) !== null) {
    console.log('Pulled chunk:', chunk.length, 'bytes');
  }
});
readStream2.on('end', () => console.log('Done reading (paused mode)'));

// 3. CUSTOM READABLE STREAM -- generate data programmatically
class NumberStream extends Readable {
  constructor(max) {
    super();
    this.current = 1;
    this.max = max;
  }
  _read() {
    // Called by Node internals whenever consumer wants more data
    if (this.current > this.max) {
      this.push(null); // signals END of stream
      return;
    }
    this.push(`${this.current}\n`); // push next chunk
    this.current++;
  }
}

const numStream = new NumberStream(5);
numStream.on('data', (chunk) => process.stdout.write(`Number: ${chunk}`));
numStream.on('end', () => console.log('Number stream finished'));
```

## 💻 Code Example — Advanced
```javascript
// readable-advanced.js -- production patterns
const fs = require('fs');
const { Readable } = require('stream');

// ─── 1. READABLE FROM ASYNC DATA SOURCE (e.g. paginated API/DB cursor) ────────
class PaginatedApiStream extends Readable {
  constructor(fetchPage) {
    super({ objectMode: true }); // objectMode: push JS objects, not just Buffers/strings
    this.fetchPage = fetchPage;
    this.page = 1;
    this.done = false;
  }

  async _read() {
    if (this.done) {
      this.push(null);
      return;
    }
    try {
      const results = await this.fetchPage(this.page); // e.g. DB query, API call
      if (results.length === 0) {
        this.done = true;
        this.push(null); // no more data
        return;
      }
      results.forEach((item) => this.push(item)); // push each item individually
      this.page++;
    } catch (err) {
      this.destroy(err); // propagate error, cleans up the stream
    }
  }
}

// Simulated paginated data source (e.g. order records from a database)
async function fetchOrderPage(page) {
  if (page > 3) return []; // simulate 3 pages of data, then done
  return Array.from({ length: 5 }, (_, i) => ({ id: `ORD-${page}-${i}`, amount: 100 * i }));
}

// ─── 2. HANDLING BACKPRESSURE MANUALLY WITH PAUSE/RESUME ─────────────────────
function copyFileManually(src, dest) {
  const readable = fs.createReadStream(src);
  const writable = fs.createWriteStream(dest);

  readable.on('data', (chunk) => {
    const canWriteMore = writable.write(chunk);
    if (!canWriteMore) {
      readable.pause(); // destination buffer full -- stop reading temporarily
    }
  });

  writable.on('drain', () => {
    readable.resume(); // destination ready again -- continue reading
  });

  readable.on('end', () => writable.end());
  readable.on('error', (err) => console.error('Read error:', err.message));
  writable.on('error', (err) => console.error('Write error:', err.message));
}

// ─── 3. ASYNC ITERATION OVER A READABLE STREAM (modern, clean syntax) ────────
async function processFileLineByLine(filePath) {
  const readline = require('readline');
  const fileStream = fs.createReadStream(filePath);
  const rl = readline.createInterface({ input: fileStream });

  let count = 0;
  for await (const line of rl) { // Readable streams are async-iterable!
    count++;
    if (line.trim()) console.log(`Line ${count}: ${line}`);
  }
  console.log(`Total lines processed: ${count}`);
}

// ─── DEMO ──────────────────────────────────────────────────────────────────────
(async () => {
  const apiStream = new PaginatedApiStream(fetchOrderPage);
  for await (const order of apiStream) {
    console.log('Processing order:', order.id);
  }
})();
```

---

## 🟠 Express.js Integration
```javascript
const express = require('express');
const fs = require('fs');
const app = express();

// 1. STREAM A LARGE FILE AS RESPONSE (Readable piped directly to res)
app.get('/export/orders.csv', (req, res) => {
  res.setHeader('Content-Type', 'text/csv');
  const readStream = fs.createReadStream('./data/orders.csv');

  readStream.on('error', (err) => {
    console.error('File read error:', err.message);
    if (!res.headersSent) res.status(500).json({ error: 'Export failed' });
  });

  readStream.pipe(res); // Readable -> Writable (res), handles backpressure automatically
});

// 2. REQUEST BODY IS ALSO A READABLE STREAM (req extends http.IncomingMessage)
app.post('/upload-raw', (req, res) => {
  let totalBytes = 0;
  req.on('data', (chunk) => {
    totalBytes += chunk.length; // process incoming body chunk by chunk
  });
  req.on('end', () => {
    res.json({ message: 'Upload received', bytes: totalBytes });
  });
  req.on('error', (err) => res.status(400).json({ error: err.message }));
});

// 3. STREAMING DATABASE CURSOR RESULTS TO RESPONSE (Readable from DB)
app.get('/export/large-dataset', async (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.write('[');
  let first = true;

  // Simulated cursor -- in real app: Model.find().cursor()
  const cursor = { // mock async iterable cursor
    async *[Symbol.asyncIterator]() {
      for (let i = 0; i < 5; i++) yield { id: i, value: `item-${i}` };
    },
  };

  for await (const doc of cursor) {
    res.write((first ? '' : ',') + JSON.stringify(doc));
    first = false;
  }
  res.write(']');
  res.end();
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Mixing paused and flowing mode APIs on the same stream
```javascript
// Wrong -- attaching 'data' switches to flowing mode, then calling .read() is unreliable
readStream.on('data', (chunk) => console.log(chunk));
const extra = readStream.read(); // undefined behavior -- don't mix modes

// Correct -- pick ONE mode and stick with it
readStream.on('data', (chunk) => console.log(chunk)); // flowing mode only
```

❌ Mistake 2: Not handling the `'error'` event on a Readable stream
```javascript
// Wrong -- if the file doesn't exist, this crashes the process
fs.createReadStream('./missing-file.txt').pipe(res);

// Correct -- always attach an error handler before piping
const stream = fs.createReadStream('./missing-file.txt');
stream.on('error', (err) => res.status(404).json({ error: 'File not found' }));
stream.pipe(res);
```

❌ Mistake 3: Forgetting `this.push(null)` in a custom `_read()` implementation
```javascript
// Wrong -- stream never ends, consumer waits forever
class MyStream extends Readable {
  _read() {
    this.push('data'); // keeps pushing forever, no termination condition
  }
}

// Correct -- explicitly signal the end
class MyStream extends Readable {
  constructor() { super(); this.count = 0; }
  _read() {
    if (this.count++ >= 5) { this.push(null); return; } // signal end
    this.push('data');
  }
}
```

---

## 🧠 Tricky Interview Question
```javascript
const fs = require('fs');
const stream = fs.createReadStream('./sample.txt');

console.log('Before listener');
stream.on('data', (chunk) => console.log('Got chunk'));
console.log('After listener');
```
Answer: Output order is `Before listener`, `After listener`, then (asynchronously, later) `Got chunk` — potentially multiple times. Reading from disk is ASYNCHRONOUS, so even though you attach the `'data'` listener synchronously, actual chunk reading happens on a later tick (after I/O completes via libuv's thread pool). This demonstrates that attaching a listener doesn't instantly trigger it — the stream only starts flowing once it has data ready AND at least one `'data'` listener registered, and that data delivery is always asynchronous, never reads happen synchronously inline in your code.

---

## ⚫ Interview Questions + Answers

Q1: What are the two modes of a Readable stream and how do you switch between them?
A1: **Paused mode** (default): you pull data explicitly via `stream.read()` when the `'readable'` event fires. **Flowing mode**: data is pushed automatically via `'data'` event listeners, `.pipe()`, or calling `.resume()`. Attaching a `'data'` listener or calling `.pipe()`/`.resume()` switches a stream from paused to flowing; calling `.pause()` switches back.

Q2: What's the difference between `highWaterMark` behavior for a Readable in object mode vs byte mode?
A2: In byte/string mode (default), `highWaterMark` is a byte count (default 64KB, 16KB for `net.Socket`) — the internal buffer holds up to that many bytes before `.read()` stops pulling more from the underlying resource. In `objectMode: true`, `highWaterMark` counts the NUMBER of objects (default 16) rather than bytes, since object sizes vary and byte-counting doesn't make sense.

Q3: How do you implement a custom Readable stream, and what's the role of `_read()`?
A3: Extend `stream.Readable` and implement the `_read(size)` method. Node calls `_read()` internally whenever its internal buffer needs more data (consumer is ready for more). Inside `_read()`, you call `this.push(chunk)` to supply the next piece of data, or `this.push(null)` to signal that the stream has ended (no more data will come).

Q4: Can you iterate a Readable stream with `for await...of`? How does that work internally?
A4: Yes — since Node 10, Readable streams implement `Symbol.asyncIterator`, making them async-iterable. `for await (const chunk of readableStream)` pulls chunks one at a time, pausing the loop until each chunk is available, and automatically handles backpressure (it won't pull faster than the loop processes). It's functionally similar to listening for `'data'` events but with cleaner sequential control flow (works naturally with `try/catch`, `break`).

Q5: What happens to a Readable stream if you never attach a `'data'` listener or call `.pipe()`/`.resume()`?
A5: It stays in **paused mode** indefinitely and never emits data automatically — the underlying resource (file descriptor, socket) still gets opened, but no reading occurs until you explicitly call `.read()` or switch to flowing mode. This is intentional — it gives you full control over when/how fast to consume, useful when you need precise backpressure control rather than Node's automatic flow management.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Processing large files, HTTP request/response bodies, or database cursors without loading everything into memory
- Building ETL pipelines where data flows: source → transform → destination
- You need to start processing data before the entire source is available (lower latency)

❌ Avoid when:
- Data is small (a few KB) and fits comfortably in memory — `fs.readFile()` is simpler and sufficient
- You need random access / seeking within data (streams are sequential, forward-only by nature)

---

## 📊 Visual Diagram
```
READABLE STREAM MODES:

  PAUSED (default):                      FLOWING:
  ┌─────────────┐                        ┌─────────────┐
  │ Readable    │ ◄── .read() pulls      │ Readable    │ ── pushes automatically ──►
  │ (buffered)  │     data manually       │ (buffered)  │    'data' event fires
  └─────────────┘                        └─────────────┘

  Switch to flowing: .on('data', fn) | .pipe(dest) | .resume()
  Switch to paused:  .pause()

CUSTOM READABLE LIFECYCLE:
  new MyStream()
       │
       ▼
  Node calls _read(size) when buffer needs filling
       │
       ├─► this.push(chunk)  → data available for consumer
       │
       └─► this.push(null)   → signals 'end' event, no more data
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Readable stream | Source of chunked data | Chunked data का source |
| Paused mode | Pull data manually with .read() | .read() से manually data खींचना |
| Flowing mode | Data pushed automatically | Data automatically push होना |
| highWaterMark | Internal buffer size threshold | Internal buffer की size limit |
| _read() | Internal method to implement custom stream | Custom stream implement करने का method |
| push(null) | Signals end of stream | Stream के end का signal |
| objectMode | Stream carries JS objects, not bytes | Bytes की जगह JS objects carry करना |

---

## ⚡ 3-Line Summary
English: Readable streams deliver data in chunks via paused (`.read()`) or flowing (`'data'` event, `.pipe()`) modes, keeping memory usage constant regardless of source size. Custom Readables implement `_read()`, pushing chunks with `this.push()` and ending with `this.push(null)`. Modern code can use `for await...of` for clean, backpressure-safe iteration.

Hindi: Readable streams data को chunks में deliver करते हैं — paused (`.read()`) या flowing (`'data'` event) mode में — memory usage constant रहती है। Custom Readables `_read()` implement करते हैं, `this.push()` से chunks देते हैं, `this.push(null)` से end करते हैं। Modern code `for await...of` से clean iteration कर सकता है।

---

## ➡️ Next Topic
**49. Writable Streams** — the destination side: `.write()`, `.end()`, backpressure signals, and custom Writable implementation.
